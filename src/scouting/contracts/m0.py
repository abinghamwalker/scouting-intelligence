"""Strict additive W05 M0 feature, role, artifact, and serving contracts."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Any, Self

from pydantic import AfterValidator, Field, Strict, StringConstraints, model_validator

from .evidence import DataCoverage, Sha256Digest
from .primitives import (
    CanonicalPlayerId,
    ContractModel,
    NonEmptyString,
    NonNegativeInt,
    PositiveInt,
    RetrievalResultId,
    SchemaVersion,
    StrictUuid,
    TenantContext,
    UnitInterval,
    UtcInstant,
)
from .retrieval import (
    RESEMBLANCE_ONLY_CLAIM,
    ApplicabilityState,
    EvidenceDimensionName,
    RetrievalRequest,
    RetrievalResult,
)
from .workflow import RoleConstraint

type FeatureName = Annotated[
    str,
    Strict(),
    StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,127}$"),
]
"""A stable, machine-readable feature name."""

type ResponsibilityCode = Annotated[
    str,
    Strict(),
    StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,127}$"),
]
"""A stable, machine-readable football responsibility identifier."""

type RoleCode = Annotated[
    str,
    Strict(),
    StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,127}$"),
]
"""A stable, machine-readable football role identifier."""


def _json_wire_value(value: Any) -> Any:
    """Encode a strict contract value exactly as its canonical JSON wire projection."""
    if isinstance(value, ContractModel):
        return value.model_dump(mode="json")
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    return str(value)


def _finite_number(value: float) -> float:
    """Reject non-finite numeric inputs before they cross the contract boundary."""
    if not math.isfinite(value):
        raise ValueError("numeric value must be finite")
    if value == 0.0 and math.copysign(1.0, value) < 0.0:
        raise ValueError("negative zero is not a canonical numeric value")
    return value


type FiniteFloat = Annotated[float, Field(strict=True), AfterValidator(_finite_number)]

W04_REAL_GOVERNED_FEATURE_REGISTRY_ID = "w04-wyscout-supported-count-features-v1"
W04_REAL_GOVERNED_FEATURE_REGISTRY_CANONICAL_DIGEST = (
    "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"
)
W04_REAL_GOVERNED_FEATURE_REGISTRY_DECISION_DIGEST = (
    "bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941"
)
W04_REAL_GOVERNED_FEATURE_DESCRIPTOR_DIGEST = (
    "fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e"
)
W04_REAL_GOVERNED_FEATURE_NAMES = (
    "action_count",
    "coordinate_known_action_count",
    "match_count",
    "resolved_possession_action_count",
)
W04_FEATURE_DESCRIPTOR_FIELDS = (
    "aggregation",
    "applicability",
    "denominator",
    "feature_name",
    "input_fields",
    "output_type",
    "reason",
    "state",
)


def w04_feature_descriptor_digest_for_registry(registry: dict[str, Any]) -> Sha256Digest:
    """Derive the frozen descriptor digest from the accepted four-row W04 projection."""
    if registry.get("registry_id") != W04_REAL_GOVERNED_FEATURE_REGISTRY_ID:
        raise ValueError("W04 registry ID does not match the accepted feature registry")
    rows = registry.get("features")
    if not isinstance(rows, list):
        raise ValueError("W04 registry features must be a parsed list")
    supported_rows = [
        row for row in rows if isinstance(row, dict) and row.get("state") == "SUPPORTED"
    ]
    if len(supported_rows) != len(W04_REAL_GOVERNED_FEATURE_NAMES):
        raise ValueError("W04 registry must contain exactly four SUPPORTED feature rows")
    names = tuple(row.get("feature_name") for row in supported_rows)
    if names != W04_REAL_GOVERNED_FEATURE_NAMES:
        raise ValueError("W04 SUPPORTED feature rows must use the accepted canonical order")
    try:
        projection = [
            {field: row[field] for field in W04_FEATURE_DESCRIPTOR_FIELDS} for row in supported_rows
        ]
    except KeyError as error:
        raise ValueError("W04 SUPPORTED feature row is missing a descriptor field") from error
    canonical = json.dumps(
        projection,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class FeatureValueState(StrEnum):
    """Explicit, fail-closed feature states; absence is never silently numeric."""

    VALUE = "value"
    ZERO = "zero"
    MISSING = "missing"
    SUPPRESSED = "suppressed"
    UNAVAILABLE = "unavailable"


class FeatureValue(ContractModel):
    """One typed feature value with explicit absence and suppression semantics."""

    state: FeatureValueState
    numeric_value: FiniteFloat | None = None
    reason_code: NonEmptyString | None = None

    @model_validator(mode="after")
    def state_payload_is_fail_closed(self) -> Self:
        """Require exactly the payload permitted by each feature state."""
        if self.state is FeatureValueState.VALUE:
            if self.numeric_value is None:
                raise ValueError("VALUE feature state requires numeric_value")
            if self.reason_code is not None:
                raise ValueError("VALUE feature state cannot carry reason_code")
        elif self.state is FeatureValueState.ZERO:
            if self.numeric_value != 0:
                raise ValueError("ZERO feature state requires numeric_value equal to zero")
            if self.reason_code is not None:
                raise ValueError("ZERO feature state cannot carry reason_code")
        elif self.numeric_value is not None or self.reason_code is None:
            raise ValueError(
                f"{self.state.value} feature state requires no numeric_value and a reason_code"
            )
        return self


class FootballResponsibility(ContractModel):
    """A versioned taxonomy responsibility expressed in football language."""

    code: ResponsibilityCode
    label: NonEmptyString
    description: NonEmptyString


class FootballRole(ContractModel):
    """A taxonomy role defined only through explicit responsibilities."""

    code: RoleCode
    label: NonEmptyString
    responsibility_codes: Annotated[tuple[ResponsibilityCode, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def responsibility_codes_are_unique(self) -> Self:
        """A role cannot gain implied weight through duplicate responsibilities."""
        if len(self.responsibility_codes) != len(set(self.responsibility_codes)):
            raise ValueError("role responsibility_codes must be unique")
        return self


class DeterministicRoleMapping(ContractModel):
    """An ordered, deterministic mapping from an admitted source label to one role."""

    source_label: NonEmptyString
    role_code: RoleCode


class FootballResponsibilityTaxonomy(ContractModel):
    """One immutable responsibility taxonomy version and its deterministic mappings."""

    schema_version: SchemaVersion = 1
    taxonomy_id: NonEmptyString
    taxonomy_version: NonEmptyString
    canonical_order: NonEmptyString
    expert_validation_status: NonEmptyString
    external_expert_evidence: tuple[NonEmptyString, ...]
    claim: NonEmptyString
    exemplar_notice: NonEmptyString
    taxonomy_digest: Sha256Digest
    responsibilities: Annotated[tuple[FootballResponsibility, ...], Field(min_length=1)]
    roles: Annotated[tuple[FootballRole, ...], Field(min_length=1)]
    deterministic_mappings: tuple[DeterministicRoleMapping, ...] = ()

    @staticmethod
    def digest_for_payload(payload: dict[str, Any]) -> Sha256Digest:
        """Hash canonical taxonomy JSON after sorting all declared semantic keys."""
        stripped = dict(payload)
        stripped.pop("taxonomy_digest", None)
        stripped["responsibilities"] = sorted(
            (
                value if isinstance(value, dict) else value.model_dump(mode="json")
                for value in stripped["responsibilities"]
            ),
            key=lambda value: value["code"],
        )
        stripped["roles"] = sorted(
            (
                {**role, "responsibility_codes": sorted(role["responsibility_codes"])}
                if isinstance(role, dict)
                else {
                    **role.model_dump(mode="json"),
                    "responsibility_codes": sorted(role.responsibility_codes),
                }
                for role in stripped["roles"]
            ),
            key=lambda value: value["code"],
        )
        stripped["deterministic_mappings"] = sorted(
            (
                value if isinstance(value, dict) else value.model_dump(mode="json")
                for value in stripped["deterministic_mappings"]
            ),
            key=lambda value: value["source_label"],
        )
        return hashlib.sha256(
            json.dumps(
                stripped, default=str, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest()

    @model_validator(mode="after")
    def taxonomy_is_closed_and_deterministic(self) -> Self:
        """Reject duplicate or dangling role and source-label mappings."""
        responsibility_codes = [item.code for item in self.responsibilities]
        role_codes = [item.code for item in self.roles]
        source_labels = [item.source_label for item in self.deterministic_mappings]
        if len(responsibility_codes) != len(set(responsibility_codes)):
            raise ValueError("taxonomy responsibility codes must be unique")
        if len(role_codes) != len(set(role_codes)):
            raise ValueError("taxonomy role codes must be unique")
        if len(source_labels) != len(set(source_labels)):
            raise ValueError("taxonomy source-label mappings must be unique")
        if responsibility_codes != sorted(responsibility_codes):
            raise ValueError("taxonomy responsibilities must be ordered by code")
        if role_codes != sorted(role_codes):
            raise ValueError("taxonomy roles must be ordered by code")
        if source_labels != sorted(source_labels):
            raise ValueError("taxonomy deterministic mappings must be ordered by source_label")
        if any(
            list(role.responsibility_codes) != sorted(role.responsibility_codes)
            for role in self.roles
        ):
            raise ValueError("taxonomy role responsibility_codes must be ordered by code")
        defined_responsibilities = set(responsibility_codes)
        if any(
            responsibility not in defined_responsibilities
            for role in self.roles
            for responsibility in role.responsibility_codes
        ):
            raise ValueError("role responsibility_codes must exist in the taxonomy")
        if any(mapping.role_code not in set(role_codes) for mapping in self.deterministic_mappings):
            raise ValueError("deterministic mapping role_code must exist in the taxonomy")
        if self.taxonomy_digest != self.digest_for_payload(self.model_dump(mode="json")):
            raise ValueError("taxonomy_digest must equal canonical taxonomy SHA-256 digest")
        return self


class RoleMembershipProbability(ContractModel):
    """One probability in an explicitly ordered contextual role distribution."""

    role_code: RoleCode
    probability: UnitInterval

    @model_validator(mode="after")
    def probability_is_finite(self) -> Self:
        """Unit interval bounds do not permit NaN or infinite membership."""
        if not math.isfinite(self.probability):
            raise ValueError("role membership probability must be finite")
        return self


class ContextualRoleMembership(ContractModel):
    """A player-window role distribution, never a permanent player label."""

    player_id: CanonicalPlayerId
    context_id: NonEmptyString
    taxonomy_id: NonEmptyString
    taxonomy_version: NonEmptyString
    taxonomy_digest: Sha256Digest
    memberships: Annotated[tuple[RoleMembershipProbability, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def membership_distribution_is_ordered_and_complete(self) -> Self:
        """Ensure unique ordered role probabilities sum exactly to one in decimal form."""
        role_codes = [membership.role_code for membership in self.memberships]
        if len(role_codes) != len(set(role_codes)):
            raise ValueError("role membership role_codes must be unique")
        if role_codes != sorted(role_codes):
            raise ValueError("role memberships must be ordered by role_code")
        total = sum((Decimal(str(item.probability)) for item in self.memberships), Decimal())
        if total != Decimal("1"):
            raise ValueError("role membership probabilities must sum deterministically to one")
        return self

    def require_matching_taxonomy(self, taxonomy: FootballResponsibilityTaxonomy) -> None:
        """Fail closed when this contextual distribution is not bound to its taxonomy."""
        if (self.taxonomy_id, self.taxonomy_version, self.taxonomy_digest) != (
            taxonomy.taxonomy_id,
            taxonomy.taxonomy_version,
            taxonomy.taxonomy_digest,
        ):
            raise ValueError("role membership taxonomy identity does not match")
        taxonomy_roles = {role.code for role in taxonomy.roles}
        if any(membership.role_code not in taxonomy_roles for membership in self.memberships):
            raise ValueError("role membership references a role absent from the taxonomy")


class M0ModelFamily(StrEnum):
    """The complete transparent M0 family surface; no learned ranker is admitted."""

    METADATA_CONTROL = "metadata_control"
    RAW_EUCLIDEAN_CONTROL = "raw_euclidean_control"
    ROBUST_SCALED_COSINE = "robust_scaled_cosine"
    WEIGHTED_COSINE = "weighted_cosine"
    PCA = "pca"
    ROLE_AWARE_RESTRICTION = "role_aware_restriction"


class M0EvidenceClass(StrEnum):
    """The authority class of every W05 artifact; this is not an evaluation partition."""

    W04_REAL_GOVERNED = "w04_real_governed"
    SYNTHETIC_DEVELOPMENT = "synthetic_development"


W04_REAL_GOVERNED_COMPATIBLE_MODEL_FAMILIES = frozenset(
    {
        M0ModelFamily.RAW_EUCLIDEAN_CONTROL,
        M0ModelFamily.ROBUST_SCALED_COSINE,
        M0ModelFamily.WEIGHTED_COSINE,
        M0ModelFamily.PCA,
    }
)


class M0SerializationFormat(StrEnum):
    """Safe, declared serialisation containers for local M0 artifacts."""

    NUMPY_NPZ = "numpy_npz"


class M0ArraySemanticRole(StrEnum):
    """Closed semantic roles for safe, non-executable numeric artifact arrays."""

    FEATURE_MATRIX = "feature_matrix"
    SCALER_CENTER = "scaler_center"
    SCALER_SCALE = "scaler_scale"
    FEATURE_WEIGHTS = "feature_weights"
    PCA_COMPONENTS = "pca_components"
    PCA_EXPLAINED_VARIANCE = "pca_explained_variance"
    INDEX_VECTORS = "index_vectors"
    INDEX_PLAYER_IDS = "index_player_ids"


class M0ArrayDtype(StrEnum):
    """Safe numeric dtypes; object and pickle-capable arrays are excluded."""

    FLOAT64 = "float64"
    INT64 = "int64"
    UINT8 = "uint8"


class M0Endianness(StrEnum):
    """Explicit byte order required for deterministic array interpretation."""

    LITTLE = "little"
    BIG = "big"


class M0MemoryOrder(StrEnum):
    """Explicit array memory order required for safe deterministic reload."""

    C = "c"
    FORTRAN = "fortran"


class M0PcaOrientationPolicy(StrEnum):
    """Canonical sign policy for PCA components."""

    LOWEST_INDEX_MAX_ABS_PIVOT_NON_NEGATIVE = "lowest_index_max_abs_pivot_non_negative"


class M0PcaComponentTieOrderPolicy(StrEnum):
    """Canonical ordering policy when PCA explained variance is tied."""

    EXPLAINED_VARIANCE_DESCENDING_THEN_COMPONENT_BYTES = (
        "explained_variance_descending_then_component_bytes"
    )


class M0TiePolicy(StrEnum):
    """The complete deterministic ordering policy for equal retrieval values."""

    SCORE_DISTANCE_THEN_CANONICAL_PLAYER_UUID_BYTES = (
        "score_distance_then_canonical_player_uuid_bytes"
    )


class M0ResolvedResponsibilityWeight(ContractModel):
    """One ordered resolved responsibility weight from the approved role brief."""

    responsibility_code: ResponsibilityCode
    weight: FiniteFloat

    @model_validator(mode="after")
    def weight_is_non_negative(self) -> Self:
        """A negative emphasis is not an admitted resolved-query weight."""
        if self.weight < 0.0:
            raise ValueError("resolved responsibility weight must be non-negative")
        return self


class M0ResolvedQuery(ContractModel):
    """Complete, replayable role-brief query with a self-verifying identity digest."""

    tenant_context: TenantContext
    trace_id: StrictUuid
    role_brief_id: StrictUuid
    role_brief_version: PositiveInt
    taxonomy_id: NonEmptyString
    taxonomy_version: NonEmptyString
    taxonomy_digest: Sha256Digest
    responsibilities: Annotated[tuple[ResponsibilityCode, ...], Field(min_length=1)]
    responsibility_weights: Annotated[
        tuple[M0ResolvedResponsibilityWeight, ...], Field(min_length=1)
    ]
    hard_constraints: tuple[RoleConstraint, ...] = ()
    exemplar_player_ids: tuple[CanonicalPlayerId, ...] = ()
    query_player_id: CanonicalPlayerId | None = None
    feature_cutoff_ts: UtcInstant
    limit: Annotated[int, Field(strict=True, ge=1, le=100)]
    excluded_player_ids: tuple[CanonicalPlayerId, ...] = ()
    resolved_query_digest: Sha256Digest

    @staticmethod
    def digest_for_payload(payload: dict[str, Any]) -> Sha256Digest:
        """Hash canonical JSON for every resolved-query field except its digest."""
        digest_payload = dict(payload)
        digest_payload.pop("resolved_query_digest", None)
        canonical = json.dumps(
            digest_payload,
            default=_json_wire_value,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @property
    def computed_resolved_query_digest(self) -> Sha256Digest:
        """Return the self-verifying canonical identity of this resolved query."""
        return self.digest_for_payload(
            self.model_dump(mode="json", exclude={"resolved_query_digest"})
        )

    @model_validator(mode="after")
    def query_is_complete_and_self_verifying(self) -> Self:
        """Reject ambiguous query inputs and content substitutions."""
        weights = [item.responsibility_code for item in self.responsibility_weights]
        if len(self.responsibilities) != len(set(self.responsibilities)):
            raise ValueError("resolved query responsibilities must be unique")
        if len(weights) != len(set(weights)):
            raise ValueError("resolved query responsibility weights must be unique")
        if tuple(weights) != self.responsibilities:
            raise ValueError(
                "resolved query responsibility weights must exactly follow "
                "declared responsibilities"
            )
        if len(self.exemplar_player_ids) != len(set(self.exemplar_player_ids)):
            raise ValueError("resolved query exemplar player IDs must be unique")
        if len(self.excluded_player_ids) != len(set(self.excluded_player_ids)):
            raise ValueError("resolved query excluded player IDs must be unique")
        if self.resolved_query_digest != self.computed_resolved_query_digest:
            raise ValueError(
                "resolved_query_digest must equal the canonical resolved-query SHA-256 digest"
            )
        return self


class M0ScoredCandidate(ContractModel):
    """Explicit score inputs retained to validate deterministic candidate ordering."""

    player_id: CanonicalPlayerId
    rank: PositiveInt
    distance: FiniteFloat
    query_feature_values: tuple[FeatureValue, ...]
    candidate_feature_values: tuple[FeatureValue, ...]
    contributions: tuple[FiniteFloat, ...]

    @model_validator(mode="after")
    def distance_is_non_negative(self) -> Self:
        """Distances are canonical non-negative quantities, never signed scores."""
        if self.distance < 0.0:
            raise ValueError("scored candidate distance must be non-negative")
        return self


class M0ArrayDescriptor(ContractModel):
    """Non-executable interpretation and content identity for one artifact array."""

    name: FeatureName
    semantic_role: M0ArraySemanticRole
    dtype: M0ArrayDtype
    shape: Annotated[tuple[PositiveInt, ...], Field(min_length=1)]
    endianness: M0Endianness
    memory_order: M0MemoryOrder
    byte_length: PositiveInt
    digest: Sha256Digest

    @model_validator(mode="after")
    def byte_length_matches_numeric_layout(self) -> Self:
        """Reject a descriptor whose declared shape cannot consume its exact bytes."""
        item_size = {
            M0ArrayDtype.FLOAT64: 8,
            M0ArrayDtype.INT64: 8,
            M0ArrayDtype.UINT8: 1,
        }[self.dtype]
        expected_bytes = math.prod(self.shape) * item_size
        if self.byte_length != expected_bytes:
            raise ValueError("array descriptor byte_length must match dtype and shape")
        return self


class M0ArtifactManifest(ContractModel):
    """Immutable manifest required to load one deterministic local M0 artifact."""

    schema_version: SchemaVersion = 1
    artifact_id: StrictUuid
    model_family: M0ModelFamily
    feature_names: Annotated[tuple[FeatureName, ...], Field(min_length=1)]
    feature_schema_hash: Sha256Digest
    feature_registry_id: NonEmptyString
    feature_registry_canonical_digest: Sha256Digest
    feature_registry_decision_digest: Sha256Digest
    feature_descriptor_digest: Sha256Digest
    evidence_class: M0EvidenceClass
    taxonomy_id: NonEmptyString
    taxonomy_version: NonEmptyString
    taxonomy_digest: Sha256Digest
    configuration_digest: Sha256Digest
    fitting_population_id: NonEmptyString
    fitting_population_count: PositiveInt
    fitting_population_manifest_digest: Sha256Digest
    candidate_universe_id: NonEmptyString
    candidate_universe_count: PositiveInt
    candidate_universe_manifest_digest: Sha256Digest
    array_payload_digest: Sha256Digest
    array_descriptors: Annotated[tuple[M0ArrayDescriptor, ...], Field(min_length=1)]
    array_descriptor_bundle_digest: Sha256Digest
    model_id: NonEmptyString
    model_version: NonEmptyString
    index_id: NonEmptyString
    index_version: NonEmptyString
    lineage_identity: Sha256Digest
    deterministic_seed: NonNegativeInt
    serialization_format: M0SerializationFormat
    pca_orientation_policy: M0PcaOrientationPolicy | None = None
    pca_component_tie_order_policy: M0PcaComponentTieOrderPolicy | None = None
    artifact_manifest_digest: Sha256Digest

    @staticmethod
    def descriptor_bundle_digest_for(
        descriptors: tuple[M0ArrayDescriptor, ...],
    ) -> Sha256Digest:
        """Hash the documented compact sorted-key JSON descriptor bundle projection."""
        canonical = json.dumps(
            [descriptor.model_dump(mode="json") for descriptor in descriptors],
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def digest_for_payload(payload: dict[str, Any]) -> Sha256Digest:
        """Hash compact sorted-key JSON for the full manifest excluding its own digest."""
        digest_payload = dict(payload)
        digest_payload.pop("artifact_manifest_digest", None)
        canonical = json.dumps(
            digest_payload,
            default=lambda value: (
                value.model_dump(mode="json") if isinstance(value, ContractModel) else str(value)
            ),
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @property
    def computed_artifact_manifest_digest(self) -> Sha256Digest:
        """Return this manifest's self-verifying canonical content identity."""
        payload = self.model_dump(mode="json", exclude={"artifact_manifest_digest"})
        return self.digest_for_payload(payload)

    def require_valid_artifact_manifest_digest(self) -> None:
        """Fail closed if construction was bypassed or the manifest was later substituted."""
        if self.artifact_manifest_digest != self.computed_artifact_manifest_digest:
            raise ValueError(
                "artifact_manifest_digest must equal the canonical manifest SHA-256 digest"
            )

    @model_validator(mode="after")
    def feature_order_is_unambiguous(self) -> Self:
        """Validate authority, safe arrays, PCA policy, and content-addressed identity."""
        if len(self.feature_names) != len(set(self.feature_names)):
            raise ValueError("artifact feature_names must be unique and ordered")
        array_names = [descriptor.name for descriptor in self.array_descriptors]
        array_roles = [descriptor.semantic_role for descriptor in self.array_descriptors]
        if len(array_names) != len(set(array_names)):
            raise ValueError("artifact array descriptor names must be unique")
        if len(array_roles) != len(set(array_roles)):
            raise ValueError("artifact array descriptor semantic roles must be unique")
        if self.array_descriptor_bundle_digest != self.descriptor_bundle_digest_for(
            self.array_descriptors
        ):
            raise ValueError("array_descriptor_bundle_digest must match the descriptor bundle")
        roles = {descriptor.semantic_role: descriptor for descriptor in self.array_descriptors}
        canonical_roles = {
            M0ModelFamily.METADATA_CONTROL: (
                M0ArraySemanticRole.FEATURE_MATRIX,
                M0ArraySemanticRole.INDEX_VECTORS,
                M0ArraySemanticRole.INDEX_PLAYER_IDS,
            ),
            M0ModelFamily.RAW_EUCLIDEAN_CONTROL: (
                M0ArraySemanticRole.FEATURE_MATRIX,
                M0ArraySemanticRole.INDEX_VECTORS,
                M0ArraySemanticRole.INDEX_PLAYER_IDS,
            ),
            M0ModelFamily.ROBUST_SCALED_COSINE: (
                M0ArraySemanticRole.FEATURE_MATRIX,
                M0ArraySemanticRole.SCALER_CENTER,
                M0ArraySemanticRole.SCALER_SCALE,
                M0ArraySemanticRole.INDEX_VECTORS,
                M0ArraySemanticRole.INDEX_PLAYER_IDS,
            ),
            M0ModelFamily.WEIGHTED_COSINE: (
                M0ArraySemanticRole.FEATURE_MATRIX,
                M0ArraySemanticRole.SCALER_CENTER,
                M0ArraySemanticRole.SCALER_SCALE,
                M0ArraySemanticRole.FEATURE_WEIGHTS,
                M0ArraySemanticRole.INDEX_VECTORS,
                M0ArraySemanticRole.INDEX_PLAYER_IDS,
            ),
            M0ModelFamily.ROLE_AWARE_RESTRICTION: (
                M0ArraySemanticRole.FEATURE_MATRIX,
                M0ArraySemanticRole.SCALER_CENTER,
                M0ArraySemanticRole.SCALER_SCALE,
                M0ArraySemanticRole.FEATURE_WEIGHTS,
                M0ArraySemanticRole.INDEX_VECTORS,
                M0ArraySemanticRole.INDEX_PLAYER_IDS,
            ),
            M0ModelFamily.PCA: (
                M0ArraySemanticRole.FEATURE_MATRIX,
                M0ArraySemanticRole.SCALER_CENTER,
                M0ArraySemanticRole.SCALER_SCALE,
                M0ArraySemanticRole.PCA_COMPONENTS,
                M0ArraySemanticRole.PCA_EXPLAINED_VARIANCE,
                M0ArraySemanticRole.INDEX_VECTORS,
                M0ArraySemanticRole.INDEX_PLAYER_IDS,
            ),
        }[self.model_family]
        if tuple(array_roles) != canonical_roles:
            raise ValueError("artifact array semantic roles must use the family canonical order")
        player_ids = roles[M0ArraySemanticRole.INDEX_PLAYER_IDS]
        if player_ids.dtype is not M0ArrayDtype.UINT8 or player_ids.shape != (
            self.candidate_universe_count,
            16,
        ):
            raise ValueError("index player IDs must bind candidate count and UUID-byte rows")
        numeric_descriptors = [
            descriptor
            for descriptor in self.array_descriptors
            if descriptor.semantic_role is not M0ArraySemanticRole.INDEX_PLAYER_IDS
        ]
        if any(descriptor.dtype is not M0ArrayDtype.FLOAT64 for descriptor in numeric_descriptors):
            raise ValueError("all numeric model arrays must use float64")
        feature_count = len(self.feature_names)
        feature_matrix = roles[M0ArraySemanticRole.FEATURE_MATRIX]
        if feature_matrix.shape != (self.fitting_population_count, feature_count):
            raise ValueError("feature matrix must bind fitting population and feature counts")
        one_dimensional_feature_roles = (
            M0ArraySemanticRole.SCALER_CENTER,
            M0ArraySemanticRole.SCALER_SCALE,
            M0ArraySemanticRole.FEATURE_WEIGHTS,
        )
        if any(
            role in roles and roles[role].shape != (feature_count,)
            for role in one_dimensional_feature_roles
        ):
            raise ValueError("scaler and feature-weight arrays must match feature_names length")
        index_vectors = roles[M0ArraySemanticRole.INDEX_VECTORS]
        if self.model_family is M0ModelFamily.PCA:
            components = roles[M0ArraySemanticRole.PCA_COMPONENTS]
            variance = roles[M0ArraySemanticRole.PCA_EXPLAINED_VARIANCE]
            component_count = components.shape[0]
            if (
                components.shape[1] != feature_count
                or variance.shape != (component_count,)
                or index_vectors.shape != (self.candidate_universe_count, component_count)
            ):
                raise ValueError(
                    "PCA array shapes must bind components, variance, and index vectors"
                )
            if component_count > min(self.fitting_population_count, feature_count):
                raise ValueError(
                    "PCA component count cannot exceed fitting population or feature count"
                )
        elif index_vectors.shape != (self.candidate_universe_count, feature_count):
            raise ValueError("index vectors must bind candidate and feature counts")
        if self.evidence_class is M0EvidenceClass.W04_REAL_GOVERNED and (
            self.model_family not in W04_REAL_GOVERNED_COMPATIBLE_MODEL_FAMILIES
            or self.feature_registry_id != W04_REAL_GOVERNED_FEATURE_REGISTRY_ID
            or self.feature_registry_canonical_digest
            != W04_REAL_GOVERNED_FEATURE_REGISTRY_CANONICAL_DIGEST
            or self.feature_registry_decision_digest
            != W04_REAL_GOVERNED_FEATURE_REGISTRY_DECISION_DIGEST
            or self.feature_descriptor_digest != W04_REAL_GOVERNED_FEATURE_DESCRIPTOR_DIGEST
            or self.feature_names != W04_REAL_GOVERNED_FEATURE_NAMES
        ):
            raise ValueError(
                "W04_REAL_GOVERNED artifacts must use the exact accepted registry and features"
            )
        pca_policies = (self.pca_orientation_policy, self.pca_component_tie_order_policy)
        if self.model_family is M0ModelFamily.PCA:
            if any(policy is None for policy in pca_policies):
                raise ValueError("PCA artifacts require both canonical PCA policies")
        elif any(policy is not None for policy in pca_policies):
            raise ValueError("non-PCA artifacts cannot declare PCA policies")
        self.require_valid_artifact_manifest_digest()
        return self


class PinnedM0ServingRequest(ContractModel):
    """A retrieval request with every serving-relevant artifact identity pinned."""

    retrieval_request: RetrievalRequest
    expected_artifact_id: StrictUuid
    expected_artifact_manifest_digest: Sha256Digest
    expected_feature_schema_hash: Sha256Digest
    expected_taxonomy_id: NonEmptyString
    expected_taxonomy_version: NonEmptyString
    expected_taxonomy_digest: Sha256Digest
    expected_configuration_digest: Sha256Digest
    expected_fitting_population_id: NonEmptyString
    expected_fitting_population_count: PositiveInt
    expected_fitting_population_manifest_digest: Sha256Digest
    expected_candidate_universe_id: NonEmptyString
    expected_candidate_universe_count: PositiveInt
    expected_candidate_universe_manifest_digest: Sha256Digest
    expected_lineage_identity: Sha256Digest
    expected_model_id: NonEmptyString
    expected_model_version: NonEmptyString
    expected_index_id: NonEmptyString
    expected_index_version: NonEmptyString
    resolved_query: M0ResolvedQuery
    expected_resolved_query_digest: Sha256Digest
    ordered_exclusion_digest: Sha256Digest
    shared_core_version: NonEmptyString
    tie_policy: M0TiePolicy

    @staticmethod
    def ordered_exclusion_digest_for(player_ids: tuple[CanonicalPlayerId, ...]) -> Sha256Digest:
        """Hash the exact ordered exclusion UUID wire projection."""
        canonical = json.dumps(
            [str(player_id) for player_id in player_ids],
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @model_validator(mode="after")
    def request_pins_exact_query_exclusions_and_tie_policy(self) -> Self:
        """Ensure the immutable request and resolved query cannot drift downstream."""
        if self.ordered_exclusion_digest != self.ordered_exclusion_digest_for(
            self.retrieval_request.excluded_player_ids
        ):
            raise ValueError("ordered_exclusion_digest must match retrieval request exclusions")
        query = self.resolved_query
        request = self.retrieval_request
        if self.expected_resolved_query_digest != query.resolved_query_digest:
            raise ValueError(
                "expected_resolved_query_digest must match resolved_query.resolved_query_digest"
            )
        overlapping = (
            ("tenant_context", query.tenant_context, request.tenant_context),
            ("trace_id", query.trace_id, request.trace_id),
            ("role_brief_id", query.role_brief_id, request.role_brief_id),
            ("role_brief_version", query.role_brief_version, request.role_brief_version),
            ("feature_cutoff_ts", query.feature_cutoff_ts, request.feature_cutoff_ts),
            ("limit", query.limit, request.limit),
            ("excluded_player_ids", query.excluded_player_ids, request.excluded_player_ids),
        )
        mismatch = next((name for name, value, actual in overlapping if value != actual), None)
        if mismatch is not None:
            raise ValueError(f"resolved query does not match retrieval request {mismatch}")
        if (
            query.taxonomy_id != self.expected_taxonomy_id
            or query.taxonomy_version != self.expected_taxonomy_version
            or query.taxonomy_digest != self.expected_taxonomy_digest
        ):
            raise ValueError("resolved query taxonomy pins must match serving request pins")
        if request.claim_boundary != RESEMBLANCE_ONLY_CLAIM:
            raise ValueError("resolved query requires the resemblance-only request boundary")
        return self

    def require_matching_artifact(self, artifact: M0ArtifactManifest) -> None:
        """Fail closed unless the supplied manifest exactly equals every request pin."""
        artifact.require_valid_artifact_manifest_digest()
        expected = (
            ("artifact_id", self.expected_artifact_id, artifact.artifact_id),
            (
                "artifact_manifest_digest",
                self.expected_artifact_manifest_digest,
                artifact.artifact_manifest_digest,
            ),
            (
                "feature_schema_hash",
                self.expected_feature_schema_hash,
                artifact.feature_schema_hash,
            ),
            ("taxonomy_id", self.expected_taxonomy_id, artifact.taxonomy_id),
            ("taxonomy_version", self.expected_taxonomy_version, artifact.taxonomy_version),
            ("taxonomy_digest", self.expected_taxonomy_digest, artifact.taxonomy_digest),
            (
                "configuration_digest",
                self.expected_configuration_digest,
                artifact.configuration_digest,
            ),
            (
                "fitting_population_id",
                self.expected_fitting_population_id,
                artifact.fitting_population_id,
            ),
            (
                "fitting_population_count",
                self.expected_fitting_population_count,
                artifact.fitting_population_count,
            ),
            (
                "fitting_population_manifest_digest",
                self.expected_fitting_population_manifest_digest,
                artifact.fitting_population_manifest_digest,
            ),
            (
                "candidate_universe_id",
                self.expected_candidate_universe_id,
                artifact.candidate_universe_id,
            ),
            (
                "candidate_universe_count",
                self.expected_candidate_universe_count,
                artifact.candidate_universe_count,
            ),
            (
                "candidate_universe_manifest_digest",
                self.expected_candidate_universe_manifest_digest,
                artifact.candidate_universe_manifest_digest,
            ),
            ("lineage_identity", self.expected_lineage_identity, artifact.lineage_identity),
            ("model_id", self.expected_model_id, artifact.model_id),
            ("model_version", self.expected_model_version, artifact.model_version),
            ("index_id", self.expected_index_id, artifact.index_id),
            ("index_version", self.expected_index_version, artifact.index_version),
        )
        mismatch = next((name for name, value, actual in expected if value != actual), None)
        if mismatch is not None:
            raise ValueError(f"pinned serving request does not match artifact {mismatch}")
        if self.retrieval_request.role_brief_version < 1:
            raise ValueError("retrieval request must pin a positive role brief version")


class DataConfidenceEvidence(ContractModel):
    """Authoritative non-ranking confidence evidence for one result candidate."""

    player_id: CanonicalPlayerId
    score: UnitInterval
    coverage: DataCoverage
    applicability: ApplicabilityState
    limitations: tuple[NonEmptyString, ...] = ()
    reason_codes: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def reason_codes_are_unique(self) -> Self:
        """Confidence evidence remains concise and deterministic."""
        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise ValueError("data confidence reason_codes must be unique")
        if self.applicability is ApplicabilityState.INSUFFICIENT and not self.limitations:
            raise ValueError("insufficient data confidence requires at least one limitation")
        return self


class M0DimensionEvidenceState(StrEnum):
    """Whether one visible M0 dimension has admitted evidence for this result."""

    MEASURED = "measured"
    ZERO = "zero"
    MISSING = "missing"
    SUPPRESSED = "suppressed"
    UNAVAILABLE = "unavailable"


class M0DimensionEvidence(ContractModel):
    """Explicit state and ranking eligibility for one accepted evidence dimension."""

    name: EvidenceDimensionName
    state: M0DimensionEvidenceState
    reason_codes: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    contributes_to_ranking: bool

    @model_validator(mode="after")
    def absence_dimensions_do_not_rank(self) -> Self:
        """Absence states cannot rank, while a observed canonical zero may rank."""
        absence_states = {
            M0DimensionEvidenceState.MISSING,
            M0DimensionEvidenceState.SUPPRESSED,
            M0DimensionEvidenceState.UNAVAILABLE,
        }
        if self.state in absence_states and self.contributes_to_ranking:
            raise ValueError("absence dimensions cannot contribute to ranking")
        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise ValueError("dimension evidence reason_codes must be unique")
        return self


class M0CandidateDimensionEvidence(ContractModel):
    """Complete candidate-specific six-dimension evidence state projection."""

    player_id: CanonicalPlayerId
    rank: PositiveInt
    dimensions: Annotated[tuple[M0DimensionEvidence, ...], Field(min_length=6, max_length=6)]

    @model_validator(mode="after")
    def dimensions_are_complete_and_ordered(self) -> Self:
        """Every candidate carries each visible dimension exactly once in enum order."""
        if [item.name for item in self.dimensions] != list(EvidenceDimensionName):
            raise ValueError(
                "candidate dimension evidence must use all six dimensions in enum order"
            )
        return self


class M0ExplanationInput(ContractModel):
    """Structured feature inputs retained for deterministic result explanations."""

    feature_name: FeatureName
    query_value: FeatureValue
    candidate_value: FeatureValue
    contribution: FiniteFloat


class M0CandidateExplanation(ContractModel):
    """Deterministic explanation inputs and reason codes for one ranked candidate."""

    player_id: CanonicalPlayerId
    rank: PositiveInt
    inputs: Annotated[tuple[M0ExplanationInput, ...], Field(min_length=1)]
    reason_codes: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def explanation_is_deterministic(self) -> Self:
        """Reject duplicate feature inputs or non-deterministic reason-code repetition."""
        feature_names = [item.feature_name for item in self.inputs]
        if len(feature_names) != len(set(feature_names)):
            raise ValueError("explanation input feature_names must be unique")
        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise ValueError("explanation reason_codes must be unique")
        return self


class M0RetrievalResult(ContractModel):
    """Pinned M0 wrapper retaining resemblance output and a verified SHA-256 digest."""

    schema_version: SchemaVersion = 1
    m0_result_id: RetrievalResultId
    retrieval_result: RetrievalResult
    artifact_manifest: M0ArtifactManifest
    pinned_serving_request: PinnedM0ServingRequest
    scored_candidates: tuple[M0ScoredCandidate, ...]
    data_confidence_evidence: tuple[DataConfidenceEvidence, ...]
    dimension_evidence: tuple[M0CandidateDimensionEvidence, ...]
    explanations: tuple[M0CandidateExplanation, ...]
    result_digest: Sha256Digest

    @staticmethod
    def digest_for_payload(payload: dict[str, Any]) -> Sha256Digest:
        """Return the SHA-256 of canonical JSON excluding the self-referential digest."""
        digest_payload = dict(payload)
        digest_payload.pop("result_digest", None)
        canonical = json.dumps(
            digest_payload,
            default=_json_wire_value,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @property
    def computed_result_digest(self) -> Sha256Digest:
        """Compute this result's digest from the canonical JSON wire projection."""
        payload = self.model_dump(mode="json", exclude={"result_digest"})
        return self.digest_for_payload(payload)

    @model_validator(mode="after")
    def result_is_complete_and_digest_verified(self) -> Self:
        """Bind all evidence, artifact identity, and result bytes exactly."""
        candidates = self.retrieval_result.candidates
        candidate_players = [candidate.player_id for candidate in candidates]
        candidate_ranks = [candidate.rank for candidate in candidates]
        scored_players = [candidate.player_id for candidate in self.scored_candidates]
        scored_ranks = [candidate.rank for candidate in self.scored_candidates]
        confidence_players = [item.player_id for item in self.data_confidence_evidence]
        dimension_players = [item.player_id for item in self.dimension_evidence]
        dimension_ranks = [item.rank for item in self.dimension_evidence]
        explanation_players = [item.player_id for item in self.explanations]
        explanation_ranks = [item.rank for item in self.explanations]
        if candidate_ranks != list(range(1, len(candidates) + 1)):
            raise ValueError("retrieval result candidate ranks must be contiguous from one")
        if confidence_players != candidate_players:
            raise ValueError(
                "data confidence evidence must match retrieval candidates in rank order"
            )
        if explanation_players != candidate_players or explanation_ranks != candidate_ranks:
            raise ValueError("explanations must match retrieval candidates and ranks in order")
        if dimension_players != candidate_players or dimension_ranks != candidate_ranks:
            raise ValueError(
                "candidate dimension evidence must match retrieval candidates and ranks in order"
            )
        if self.retrieval_result.retrieval_request_id != (
            self.pinned_serving_request.retrieval_request.retrieval_request_id
        ):
            raise ValueError("retrieval result request ID must match the pinned serving request")
        request = self.pinned_serving_request.retrieval_request
        result_request_identity = (
            ("tenant_context", self.retrieval_result.tenant_context, request.tenant_context),
            ("trace_id", self.retrieval_result.trace_id, request.trace_id),
            ("role_brief_id", self.retrieval_result.role_brief_id, request.role_brief_id),
            (
                "role_brief_version",
                self.retrieval_result.role_brief_version,
                request.role_brief_version,
            ),
            (
                "feature_cutoff_ts",
                self.retrieval_result.temporal_evidence.feature_cutoff_ts,
                request.feature_cutoff_ts,
            ),
            ("claim_boundary", self.retrieval_result.claim_boundary, request.claim_boundary),
        )
        mismatch = next(
            (name for name, value, actual in result_request_identity if value != actual), None
        )
        if mismatch is not None:
            raise ValueError(f"retrieval result does not match pinned request {mismatch}")
        if any(candidate.claim_boundary != request.claim_boundary for candidate in candidates):
            raise ValueError("retrieval candidates must match the pinned request claim boundary")
        if candidate_ranks != list(range(1, len(candidates) + 1)):
            raise ValueError("retrieval result candidate ranks must be contiguous from one")
        if scored_players != candidate_players or scored_ranks != candidate_ranks:
            raise ValueError(
                "scored candidates must exactly match retrieval candidates and ranks in order"
            )
        feature_count = len(self.artifact_manifest.feature_names)
        if any(
            len(scored.query_feature_values) != feature_count
            or len(scored.candidate_feature_values) != feature_count
            or len(scored.contributions) != feature_count
            for scored in self.scored_candidates
        ):
            raise ValueError(
                "scored candidate vectors must exactly match artifact feature_names length"
            )
        expected_scored_order = sorted(
            self.scored_candidates, key=lambda scored: (scored.distance, scored.player_id.bytes)
        )
        if list(self.scored_candidates) != expected_scored_order:
            raise ValueError(
                "scored candidates must be ordered by distance then canonical player UUID bytes"
            )
        self.pinned_serving_request.require_matching_artifact(self.artifact_manifest)
        requested_limit = request.limit
        if len(candidates) > requested_limit:
            raise ValueError("retrieval result candidates cannot exceed the pinned request limit")
        if candidate_ranks != list(range(1, len(candidates) + 1)):
            raise ValueError("retrieval result candidate ranks must be contiguous from one")
        excluded = set(self.pinned_serving_request.retrieval_request.excluded_player_ids)
        if any(candidate.player_id in excluded for candidate in candidates):
            raise ValueError("retrieval result cannot include a pinned excluded player")
        self.artifact_manifest.require_valid_artifact_manifest_digest()
        if (
            self.retrieval_result.temporal_evidence.feature_schema_hash
            != self.artifact_manifest.feature_schema_hash
        ):
            raise ValueError("retrieval result feature_schema_hash must match artifact manifest")
        if self.retrieval_result.model_version != self.artifact_manifest.model_version:
            raise ValueError("retrieval result model_version must match artifact manifest")
        if self.retrieval_result.index_version != self.artifact_manifest.index_version:
            raise ValueError("retrieval result index_version must match artifact manifest")
        absence_states = {
            M0DimensionEvidenceState.MISSING,
            M0DimensionEvidenceState.SUPPRESSED,
            M0DimensionEvidenceState.UNAVAILABLE,
        }
        required_absence_dimensions = {
            EvidenceDimensionName.IMPACT,
            EvidenceDimensionName.TRAJECTORY,
            EvidenceDimensionName.TRANSFER_RISK,
        }
        for candidate, confidence, candidate_states, explanation, scored in zip(
            candidates,
            self.data_confidence_evidence,
            self.dimension_evidence,
            self.explanations,
            self.scored_candidates,
            strict=True,
        ):
            if (
                candidate.confidence.score != confidence.score
                or candidate.confidence.applicability is not confidence.applicability
                or candidate.confidence.limitations != confidence.limitations
                or candidate.coverage != confidence.coverage
            ):
                raise ValueError(
                    "data confidence evidence must exactly match candidate confidence and coverage"
                )
            legacy = next(
                dimension
                for dimension in candidate.evidence_dimensions
                if dimension.name is EvidenceDimensionName.DATA_CONFIDENCE
            )
            expected_legacy_reasons = (
                *confidence.reason_codes,
                *confidence.limitations,
                f"applicability_{confidence.applicability.value}",
            )
            if (
                legacy.score != confidence.score
                or legacy.confidence != confidence.coverage.overall
                or legacy.reason_codes != expected_legacy_reasons
            ):
                raise ValueError(
                    "legacy data_confidence dimension must be the exact confidence projection"
                )
            state_by_name = {item.name: item for item in candidate_states.dimensions}
            for dimension in candidate.evidence_dimensions:
                state = state_by_name[dimension.name]
                if state.reason_codes != dimension.reason_codes:
                    raise ValueError(
                        "dimension evidence reasons must exactly match the legacy dimension"
                    )
                if (
                    dimension.name is not EvidenceDimensionName.DATA_CONFIDENCE
                    and state.state is M0DimensionEvidenceState.MEASURED
                    and dimension.score <= 0.0
                ):
                    raise ValueError(
                        "MEASURED dimension evidence requires a strictly positive legacy score"
                    )
                if state.state in absence_states and (
                    dimension.score != 0.0 or dimension.confidence != 0.0
                ):
                    raise ValueError(
                        "absence dimensions require zero sentinel scores and matching reasons"
                    )
                if state.state is M0DimensionEvidenceState.ZERO and (
                    dimension.score != 0.0 or math.copysign(1.0, dimension.score) < 0.0
                ):
                    raise ValueError("ZERO dimension evidence requires canonical +0.0 legacy score")
            data_confidence_state = state_by_name[EvidenceDimensionName.DATA_CONFIDENCE]
            if confidence.score == 0.0:
                if math.copysign(1.0, confidence.score) < 0.0:
                    raise ValueError("data confidence score must use canonical +0.0")
                expected_data_confidence_state = M0DimensionEvidenceState.ZERO
            else:
                expected_data_confidence_state = M0DimensionEvidenceState.MEASURED
            if data_confidence_state.state is not expected_data_confidence_state:
                raise ValueError(
                    "data confidence dimension state must be derived from confidence score"
                )
            if (
                data_confidence_state.reason_codes != expected_legacy_reasons
                or data_confidence_state.contributes_to_ranking
            ):
                raise ValueError(
                    "data confidence dimension state must equal the authoritative projection"
                )
            if any(
                state_by_name[name].state not in absence_states
                or state_by_name[name].contributes_to_ranking
                for name in required_absence_dimensions
            ):
                raise ValueError(
                    "impact, trajectory, and transfer risk must remain non-ranking absence states"
                )
            explanation_inputs = explanation.inputs
            if (
                tuple(item.feature_name for item in explanation_inputs)
                != self.artifact_manifest.feature_names
            ):
                raise ValueError("explanations must use artifact feature_names in exact order")
            if any(
                input_item.query_value != query_value
                or input_item.candidate_value != candidate_value
                or input_item.contribution != contribution
                for input_item, query_value, candidate_value, contribution in zip(
                    explanation_inputs,
                    scored.query_feature_values,
                    scored.candidate_feature_values,
                    scored.contributions,
                    strict=True,
                )
            ):
                raise ValueError("explanation inputs must exactly equal scored candidate values")
        if self.artifact_manifest.evidence_class is M0EvidenceClass.W04_REAL_GOVERNED:
            for candidate_states in self.dimension_evidence:
                state_by_name = {item.name: item for item in candidate_states.dimensions}
                role_state = state_by_name[EvidenceDimensionName.ROLE_COMPATIBILITY]
                if role_state.state not in absence_states or role_state.contributes_to_ranking:
                    raise ValueError(
                        "W04_REAL_GOVERNED role compatibility must remain a non-ranking "
                        "absence state"
                    )
        if self.result_digest != self.computed_result_digest:
            raise ValueError("result_digest must equal the canonical SHA-256 result digest")
        return self

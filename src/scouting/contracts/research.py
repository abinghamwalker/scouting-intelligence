"""Strict contracts for the governed historical-player research workbench."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import AfterValidator, Field, model_validator

from .evidence import Sha256Digest
from .numerics import (
    StableNormalizationError,
    stable_finite_sum,
    stable_weighted_unit_components,
)
from .primitives import (
    CanonicalPlayerId,
    ContractModel,
    NonEmptyString,
    NonNegativeInt,
    PositiveInt,
    SchemaVersion,
    StrictUuid,
    UtcInstant,
)


def _reject_negative_zero(value: float) -> float:
    if value == 0.0 and math.copysign(1.0, value) < 0.0:
        raise ValueError("negative zero is not canonical")
    return value


type FiniteFloat = Annotated[
    float,
    Field(strict=True, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]
type NonNegativeFloat = Annotated[
    float,
    Field(strict=True, ge=0.0, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]
type PositiveFloat = Annotated[
    float,
    Field(strict=True, gt=0.0, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]
type ResearchClaimBoundary = Literal["historical_resemblance_research_only"]

RESEARCH_CLAIM_BOUNDARY: ResearchClaimBoundary = "historical_resemblance_research_only"


def canonical_research_digest(value: ContractModel | dict[str, Any]) -> str:
    """Return stable SHA-256 over one canonical JSON-compatible projection."""
    projection = value.model_dump(mode="json") if isinstance(value, ContractModel) else value
    payload = json.dumps(
        projection,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def rows_semantic_digest(rows: Sequence[ContractModel]) -> str:
    """Digest an ordered typed-row population independent of its container format."""

    payload = (
        json.dumps(
            [row.model_dump(mode="json") for row in rows],
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class ResearchCapability(StrEnum):
    """Capabilities declared by a governed dataset, never inferred by clients."""

    EXEMPLAR_QUERY = "exemplar_query"
    WEIGHTED_PROFILE_QUERY = "weighted_profile_query"
    WEIGHTED_EUCLIDEAN = "weighted_euclidean"
    WEIGHTED_COSINE = "weighted_cosine"
    FEATURE_CONTRIBUTIONS = "feature_contributions"
    PLAYER_COMPARISON = "player_comparison"
    SAVED_EXPERIMENT_REPLAY = "saved_experiment_replay"


class MatrixCatalogueEntry(ContractModel):
    """Strict identity roster row supplied by the governed feature build."""

    schema_version: SchemaVersion = 1
    source_player_id: NonEmptyString
    player_id: CanonicalPlayerId
    display_name: NonEmptyString
    position_code: Literal["GK", "DF", "MD", "FW"]
    contains_synthetic_data: Literal[False] = False


class ResearchDatasetDescriptor(ContractModel):
    """User-visible authority and scope for one immutable historical dataset."""

    schema_version: SchemaVersion = 1
    dataset_id: StrictUuid
    dataset_version: NonEmptyString
    dataset_manifest_digest: Sha256Digest
    provider_adapter: NonEmptyString
    provider_neutral_schema_version: NonEmptyString
    rights_classification: Literal["wyscout_figshare_v5_cc_by_4"]
    attribution: NonEmptyString
    source_manifest_id: StrictUuid
    source_manifest_digest: Sha256Digest
    source_completion_digest: Sha256Digest
    identity_bundle_digest: Sha256Digest
    source_available_at: UtcInstant
    identity_available_at: UtcInstant
    feature_cutoff_ts: UtcInstant
    window_start_utc: UtcInstant
    window_end_utc: UtcInstant
    source_match_count: PositiveInt
    source_action_count: PositiveInt
    source_team_count: PositiveInt
    source_player_count: PositiveInt
    capabilities: Annotated[tuple[ResearchCapability, ...], Field(min_length=1)]
    limitations: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    claim_boundary: ResearchClaimBoundary = RESEARCH_CLAIM_BOUNDARY

    @model_validator(mode="after")
    def authority_is_coherent(self) -> Self:
        if self.window_start_utc >= self.window_end_utc:
            raise ValueError("dataset window_start_utc must precede window_end_utc")
        if max(self.source_available_at, self.identity_available_at) >= self.feature_cutoff_ts:
            raise ValueError("dataset authorities must be strictly before feature_cutoff_ts")
        if self.window_end_utc >= self.feature_cutoff_ts:
            raise ValueError("dataset window must close strictly before feature_cutoff_ts")
        if len(self.capabilities) != len(set(self.capabilities)):
            raise ValueError("dataset capabilities must be unique")
        return self


class MinuteEvidenceState(StrEnum):
    """Strength of reconstructed exposure used for eligibility."""

    EXACT = "exact"
    CONSERVATIVE_LOWER_BOUND = "conservative_lower_bound"
    UNUSABLE = "unusable"


class PopulationDecisionReason(StrEnum):
    """One mutually exclusive disposition for every resolved catalogue player."""

    REFERRED_TO_WINDOW_ELIGIBILITY = "referred_to_window_eligibility"
    NO_LINEUP_EVIDENCE = "no_lineup_evidence"


class SourcePopulationDecision(ContractModel):
    """Catalogue-level ledger row, before competition-window eligibility."""

    schema_version: SchemaVersion = 1
    source_player_id: NonEmptyString
    player_id: CanonicalPlayerId
    lineup_evidence_present: bool
    grain_ids: tuple[NonEmptyString, ...]
    reason: PopulationDecisionReason

    @model_validator(mode="after")
    def decision_is_coherent(self) -> Self:
        referred = self.reason is PopulationDecisionReason.REFERRED_TO_WINDOW_ELIGIBILITY
        if referred != self.lineup_evidence_present or referred != bool(self.grain_ids):
            raise ValueError("population decision must agree with lineup evidence and grains")
        if len(self.grain_ids) != len(set(self.grain_ids)):
            raise ValueError("population decision grain ids must be unique")
        return self


def population_referred_grain_digest(
    rows: Sequence[SourcePopulationDecision],
) -> str:
    """Digest the exact referred player/grain ledger in canonical identity order."""

    ledger = [
        {"grain_id": grain_id, "player_id": str(row.player_id)}
        for row in sorted(rows, key=lambda item: item.player_id.bytes)
        for grain_id in row.grain_ids
    ]
    payload = (
        json.dumps(
            ledger,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class EligibilityReason(StrEnum):
    """Mutually exclusive competition-window eligibility outcomes."""

    ELIGIBLE = "eligible"
    INVALID_HISTORICAL_MEMBERSHIP = "invalid_historical_membership"
    UNUSABLE_MINUTES = "unusable_minutes"
    BELOW_MINIMUM_MINUTES = "below_minimum_minutes"
    REQUIRED_FEATURE_MISSING = "required_feature_missing"
    TEMPORAL_CUTOFF_FAILED = "temporal_cutoff_failed"


class EligibilityDecision(ContractModel):
    """One auditable outcome at resolved player/competition-season grain."""

    schema_version: SchemaVersion = 1
    source_player_id: NonEmptyString
    grain_id: NonEmptyString
    player_id: CanonicalPlayerId
    competition_id: StrictUuid
    season_id: NonEmptyString
    eligibility_policy_version: NonEmptyString
    eligibility_policy_digest: Sha256Digest
    minute_state: MinuteEvidenceState
    minutes: NonNegativeFloat | None
    minimum_minutes: PositiveFloat
    eligible: bool
    reason: EligibilityReason
    feature_cutoff_ts: UtcInstant
    temporal_authorities_strictly_before_cutoff: bool
    source_match_count: NonNegativeInt
    source_action_count: NonNegativeInt
    required_missing_features: tuple[NonEmptyString, ...] = ()

    @model_validator(mode="after")
    def outcome_is_coherent(self) -> Self:
        if self.eligible != (self.reason is EligibilityReason.ELIGIBLE):
            raise ValueError("eligible must agree with the eligibility reason")
        if self.minute_state is MinuteEvidenceState.UNUSABLE:
            if self.minutes is not None or self.reason is not EligibilityReason.UNUSABLE_MINUTES:
                raise ValueError("unusable minutes require the unusable-minutes outcome")
        elif self.minutes is None or self.reason is EligibilityReason.UNUSABLE_MINUTES:
            raise ValueError("usable minute evidence requires minutes and a usable outcome")
        if self.reason is EligibilityReason.BELOW_MINIMUM_MINUTES and (
            self.minutes is None or self.minutes >= self.minimum_minutes
        ):
            raise ValueError("below-minimum outcome requires usable minutes below threshold")
        if self.reason in {EligibilityReason.ELIGIBLE, EligibilityReason.REQUIRED_FEATURE_MISSING}:
            if self.minutes is None or self.minutes < self.minimum_minutes:
                raise ValueError("eligible/feature-missing outcomes must meet minimum minutes")
        has_missing = bool(self.required_missing_features)
        if has_missing != (self.reason is EligibilityReason.REQUIRED_FEATURE_MISSING):
            raise ValueError("required missing features must agree with their outcome")
        temporal_failed = self.reason is EligibilityReason.TEMPORAL_CUTOFF_FAILED
        if temporal_failed == self.temporal_authorities_strictly_before_cutoff:
            raise ValueError("temporal outcome must agree with strict-before evidence")
        if len(self.required_missing_features) != len(set(self.required_missing_features)):
            raise ValueError("required missing features must be unique")
        return self


class FeatureValueState(StrEnum):
    """Explicit value semantics; missing evidence is never silently imputed."""

    VALUE = "value"
    ZERO = "zero"
    MISSING = "missing"
    SUPPRESSED = "suppressed"
    UNAVAILABLE = "unavailable"


class ResearchFeatureValue(ContractModel):
    """One explainable feature value and its evidence state."""

    feature_name: NonEmptyString
    state: FeatureValueState
    value: FiniteFloat | None
    numerator: FiniteFloat | None = None
    denominator: PositiveFloat | None = None
    reason: NonEmptyString | None = None

    @model_validator(mode="after")
    def value_matches_state(self) -> Self:
        observed = self.state in {FeatureValueState.VALUE, FeatureValueState.ZERO}
        if observed:
            if self.value is None or self.reason is not None:
                raise ValueError("observed feature states require a value and no reason")
            if self.state is FeatureValueState.ZERO and self.value != 0.0:
                raise ValueError("zero state requires canonical 0.0")
            if self.state is FeatureValueState.VALUE and self.value == 0.0:
                raise ValueError("numeric zero must use the zero state")
            if (self.numerator is None) != (self.denominator is None):
                raise ValueError("numerator and denominator must be supplied together")
        else:
            if any(item is not None for item in (self.value, self.numerator, self.denominator)):
                raise ValueError("absent feature states cannot carry numeric evidence")
            if self.reason is None:
                raise ValueError("absent feature states require a reason")
        return self


class ResearchCoverage(ContractModel):
    """Explicit observed/expected evidence counts for one feature-matrix row."""

    lineup_matches_observed: NonNegativeInt
    lineup_matches_expected: PositiveInt
    action_matches_observed: NonNegativeInt
    action_matches_expected: PositiveInt
    coordinate_actions_observed: NonNegativeInt
    coordinate_actions_expected: NonNegativeInt

    @model_validator(mode="after")
    def observed_does_not_exceed_expected(self) -> Self:
        pairs = (
            (self.lineup_matches_observed, self.lineup_matches_expected),
            (self.action_matches_observed, self.action_matches_expected),
            (self.coordinate_actions_observed, self.coordinate_actions_expected),
        )
        if any(observed > expected for observed, expected in pairs):
            raise ValueError("coverage observed counts cannot exceed expected counts")
        return self


class FeatureMatrixRow(ContractModel):
    """One unique historical player/competition-season research row."""

    schema_version: SchemaVersion = 1
    grain_id: NonEmptyString
    player_id: CanonicalPlayerId
    display_name: NonEmptyString
    competition_id: StrictUuid
    competition_name: NonEmptyString
    season_id: NonEmptyString
    position_code: Literal["GK", "DF", "MD", "FW"]
    team_ids: Annotated[tuple[StrictUuid, ...], Field(min_length=1)]
    team_names: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    minute_state: Literal[MinuteEvidenceState.EXACT, MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND]
    minutes: PositiveFloat
    match_count: PositiveInt
    features: Annotated[tuple[ResearchFeatureValue, ...], Field(min_length=1)]
    missing_feature_names: tuple[NonEmptyString, ...]
    coverage: ResearchCoverage
    window_start_utc: UtcInstant
    window_end_utc: UtcInstant
    feature_cutoff_ts: UtcInstant
    dataset_manifest_digest: Sha256Digest
    identity_bundle_digest: Sha256Digest
    canonical_build_digest: Sha256Digest
    feature_registry_digest: Sha256Digest
    eligibility_policy_digest: Sha256Digest
    eligibility_decision_digest: Sha256Digest
    source_lineage_digest: Sha256Digest
    source_action_count: NonNegativeInt
    contains_synthetic_data: Literal[False] = False

    @model_validator(mode="after")
    def row_is_unique_and_supported(self) -> Self:
        names = [feature.feature_name for feature in self.features]
        if len(names) != len(set(names)):
            raise ValueError("matrix feature names must be unique")
        actual_missing = tuple(
            feature.feature_name
            for feature in self.features
            if feature.state
            in {
                FeatureValueState.MISSING,
                FeatureValueState.SUPPRESSED,
                FeatureValueState.UNAVAILABLE,
            }
        )
        if self.missing_feature_names != actual_missing:
            raise ValueError("matrix missing-feature summary must follow feature order")
        if len(self.team_ids) != len(set(self.team_ids)):
            raise ValueError("matrix team ids must be unique")
        if len(self.team_ids) != len(self.team_names):
            raise ValueError("team ids and names must have equal cardinality")
        if self.window_start_utc >= self.window_end_utc:
            raise ValueError("matrix window start must precede end")
        if self.window_end_utc >= self.feature_cutoff_ts:
            raise ValueError("matrix window must close strictly before its cutoff")
        return self


class ResearchArtifactFile(ContractModel):
    """One immutable physical and semantic artifact bound by a manifest."""

    role: NonEmptyString
    relative_path: NonEmptyString
    row_count: NonNegativeInt
    size_bytes: PositiveInt
    sha256: Sha256Digest
    semantic_digest: Sha256Digest

    @model_validator(mode="after")
    def path_is_safe(self) -> Self:
        if self.relative_path.startswith("/") or ".." in self.relative_path.split("/"):
            raise ValueError("artifact path must be a safe relative path")
        return self


class EligibilityReasonCount(ContractModel):
    reason: EligibilityReason
    count: NonNegativeInt


class FeatureMatrixManifest(ContractModel):
    """Self-verifying population, lineage, temporal, and physical matrix authority."""

    schema_version: SchemaVersion = 1
    manifest_id: StrictUuid
    matrix_version: NonEmptyString
    matrix_digest: Sha256Digest
    generated_at: UtcInstant
    feature_cutoff_ts: UtcInstant
    window_start_utc: UtcInstant
    window_end_utc: UtcInstant
    dataset_version: NonEmptyString
    dataset_manifest_digest: Sha256Digest
    source_manifest_id: StrictUuid
    source_manifest_digest: Sha256Digest
    source_completion_digest: Sha256Digest
    identity_bundle_digest: Sha256Digest
    canonical_build_version: NonEmptyString
    canonical_build_digest: Sha256Digest
    feature_registry_version: NonEmptyString
    feature_registry_digest: Sha256Digest
    eligibility_policy_version: NonEmptyString
    eligibility_policy_digest: Sha256Digest
    code_version: NonEmptyString
    code_digest: Sha256Digest
    feature_names: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    catalogue_player_count: PositiveInt
    population_decision_count: PositiveInt
    population_referred_count: NonNegativeInt
    population_referred_grain_count: NonNegativeInt
    population_referred_grain_ledger_digest: Sha256Digest
    population_no_lineup_count: NonNegativeInt
    unresolved_identity_count: NonNegativeInt
    rejected_identity_count: NonNegativeInt
    rejected_actor_action_count: NonNegativeInt
    eligibility_decision_count: NonNegativeInt
    unique_eligibility_grain_count: NonNegativeInt
    eligibility_ledger_digest: Sha256Digest
    eligibility_reason_counts: Annotated[tuple[EligibilityReasonCount, ...], Field(min_length=1)]
    matrix_row_count: PositiveInt
    unique_matrix_grain_count: PositiveInt
    unique_matrix_player_count: PositiveInt
    files: Annotated[tuple[ResearchArtifactFile, ...], Field(min_length=1)]
    contains_synthetic_rows: Literal[False] = False
    limitations: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    manifest_digest: Sha256Digest
    claim_boundary: ResearchClaimBoundary = RESEARCH_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"manifest_digest", "generated_at"})

    @model_validator(mode="after")
    def manifest_is_coherent(self) -> Self:
        if (
            self.window_start_utc >= self.window_end_utc
            or self.window_end_utc >= self.feature_cutoff_ts
        ):
            raise ValueError("matrix manifest window must close strictly before cutoff")
        if self.population_decision_count != self.catalogue_player_count:
            raise ValueError("one population decision is required per catalogue player")
        if (
            self.population_referred_count + self.population_no_lineup_count
            != self.population_decision_count
        ):
            raise ValueError("population decisions must reconcile to the catalogue")
        if bool(self.population_referred_count) != bool(self.population_referred_grain_count):
            raise ValueError("referred players and referred grains must be empty together")
        if self.population_referred_grain_count < self.population_referred_count:
            raise ValueError("every referred player must declare at least one eligibility grain")
        if self.eligibility_decision_count != self.population_referred_grain_count:
            raise ValueError("one eligibility decision is required per referred grain")
        if self.unique_eligibility_grain_count != self.eligibility_decision_count:
            raise ValueError("eligibility decision grains must be unique and complete")
        reasons = [item.reason for item in self.eligibility_reason_counts]
        if len(reasons) != len(set(reasons)) or set(reasons) != set(EligibilityReason):
            raise ValueError("eligibility reason counts must contain every reason exactly once")
        if (
            sum(item.count for item in self.eligibility_reason_counts)
            != self.eligibility_decision_count
        ):
            raise ValueError("eligibility reasons must reconcile to eligibility decisions")
        eligible_count = next(
            item.count
            for item in self.eligibility_reason_counts
            if item.reason is EligibilityReason.ELIGIBLE
        )
        if eligible_count != self.matrix_row_count:
            raise ValueError("eligible decision count must equal matrix rows")
        if self.unique_matrix_grain_count != self.matrix_row_count:
            raise ValueError("matrix grains must be unique and complete")
        if self.unique_matrix_player_count > self.matrix_row_count:
            raise ValueError("unique matrix players cannot exceed matrix rows")
        if len(self.feature_names) != len(set(self.feature_names)):
            raise ValueError("manifest feature names must be unique")
        roles = [item.role for item in self.files]
        paths = [item.relative_path for item in self.files]
        if len(roles) != len(set(roles)) or len(paths) != len(set(paths)):
            raise ValueError("manifest artifact roles and paths must be unique")
        if self.manifest_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("matrix manifest digest must match its canonical projection")
        return self


class ResearchMethod(StrEnum):
    """Transparent retrieval baselines supported by W09."""

    WEIGHTED_EUCLIDEAN = "weighted_euclidean"
    WEIGHTED_COSINE = "weighted_cosine"


class ResearchIndexManifest(ContractModel):
    """Self-verifying scaler/index authority over one exact eligible matrix."""

    schema_version: SchemaVersion = 1
    index_id: StrictUuid
    index_version: NonEmptyString
    generated_at: UtcInstant
    feature_cutoff_ts: UtcInstant
    matrix_version: NonEmptyString
    matrix_manifest_digest: Sha256Digest
    matrix_digest: Sha256Digest
    identity_bundle_digest: Sha256Digest
    feature_registry_version: NonEmptyString
    feature_registry_digest: Sha256Digest
    eligibility_policy_version: NonEmptyString
    eligibility_policy_digest: Sha256Digest
    model_version: NonEmptyString
    model_configuration_digest: Sha256Digest
    scorer_version: NonEmptyString
    scorer_code_digest: Sha256Digest
    methods: Annotated[tuple[ResearchMethod, ...], Field(min_length=1)]
    feature_names: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    candidate_count: PositiveInt
    catalogue_digest: Sha256Digest
    files: Annotated[tuple[ResearchArtifactFile, ...], Field(min_length=1)]
    contains_synthetic_rows: Literal[False] = False
    limitations: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    manifest_digest: Sha256Digest
    claim_boundary: ResearchClaimBoundary = RESEARCH_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"manifest_digest", "generated_at"})

    @model_validator(mode="after")
    def index_is_coherent(self) -> Self:
        if len(self.methods) != len(set(self.methods)):
            raise ValueError("index methods must be unique")
        if len(self.feature_names) != len(set(self.feature_names)):
            raise ValueError("index feature names must be unique")
        roles = [item.role for item in self.files]
        paths = [item.relative_path for item in self.files]
        if len(roles) != len(set(roles)) or len(paths) != len(set(paths)):
            raise ValueError("index artifact roles and paths must be unique")
        if self.manifest_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("index manifest digest must match its canonical projection")
        return self


class ResearchVersionPins(ContractModel):
    """Exact versions and digests required to load or replay one query."""

    feature_cutoff_ts: UtcInstant
    dataset_version: NonEmptyString
    dataset_manifest_digest: Sha256Digest
    identity_bundle_digest: Sha256Digest
    canonical_build_digest: Sha256Digest
    matrix_version: NonEmptyString
    matrix_manifest_digest: Sha256Digest
    matrix_digest: Sha256Digest
    feature_registry_version: NonEmptyString
    feature_registry_digest: Sha256Digest
    eligibility_policy_version: NonEmptyString
    eligibility_policy_digest: Sha256Digest
    model_version: NonEmptyString
    model_configuration_digest: Sha256Digest
    scorer_version: NonEmptyString
    scorer_code_digest: Sha256Digest
    index_version: NonEmptyString
    index_manifest_digest: Sha256Digest
    catalogue_digest: Sha256Digest

    def assert_compatible(self, loaded: ResearchVersionPins) -> None:
        if self != loaded:
            raise ValueError("submitted research version pins are stale or incompatible")


class ResearchQueryMode(StrEnum):
    """Exactly one user-understandable query mode."""

    EXEMPLAR = "exemplar"
    WEIGHTED_PROFILE = "weighted_profile"


class NamedFeatureValue(ContractModel):
    feature_name: NonEmptyString
    value: FiniteFloat


class FeatureWeight(ContractModel):
    feature_name: NonEmptyString
    weight: NonNegativeFloat


class ResearchFilters(ContractModel):
    """Governed eligibility filters applied before full-population scoring."""

    competition_id: StrictUuid
    # Optional only so retained pre-L-1 saved experiments remain readable. New
    # serving requests fail closed unless the season is explicit.
    season_id: NonEmptyString | None = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )
    position_codes: tuple[Literal["GK", "DF", "MD", "FW"], ...] = ()
    minimum_minutes: NonNegativeFloat | None = None
    excluded_player_ids: tuple[CanonicalPlayerId, ...] = ()

    @model_validator(mode="after")
    def filters_are_unique(self) -> Self:
        if len(self.position_codes) != len(set(self.position_codes)):
            raise ValueError("position filters must be unique")
        if len(self.excluded_player_ids) != len(set(self.excluded_player_ids)):
            raise ValueError("excluded players must be unique")
        return self


class ResearchQueryRequest(ContractModel):
    """Replayable exemplar or weighted-profile request with immutable pins."""

    schema_version: SchemaVersion = 1
    query_id: StrictUuid
    requested_at: UtcInstant
    feature_cutoff_ts: UtcInstant
    pins: ResearchVersionPins
    mode: ResearchQueryMode
    method: ResearchMethod
    exemplar_grain_id: NonEmptyString | None = None
    profile: tuple[NamedFeatureValue, ...] = ()
    weights: Annotated[tuple[FeatureWeight, ...], Field(min_length=1)]
    filters: ResearchFilters
    limit: Annotated[int, Field(strict=True, ge=1, le=100)] = 20
    query_digest: Sha256Digest
    claim_boundary: ResearchClaimBoundary = RESEARCH_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"query_digest", "requested_at"})

    @model_validator(mode="after")
    def query_is_coherent(self) -> Self:
        if self.feature_cutoff_ts != self.pins.feature_cutoff_ts:
            raise ValueError("query cutoff must equal the pinned matrix/index cutoff")
        if self.feature_cutoff_ts > self.requested_at:
            raise ValueError("feature_cutoff_ts cannot be after requested_at")
        if self.mode is ResearchQueryMode.EXEMPLAR:
            if self.exemplar_grain_id is None or self.profile:
                raise ValueError("exemplar mode requires only exemplar_grain_id")
        elif self.exemplar_grain_id is not None or not self.profile:
            raise ValueError("weighted-profile mode requires only profile values")
        weight_names = tuple(item.feature_name for item in self.weights)
        if len(weight_names) != len(set(weight_names)):
            raise ValueError("feature weights must be unique")
        if not any(item.weight > 0.0 for item in self.weights):
            raise ValueError("at least one feature weight must be positive")
        profile_names = tuple(item.feature_name for item in self.profile)
        if len(profile_names) != len(set(profile_names)):
            raise ValueError("profile feature names must be unique")
        if self.profile and profile_names != weight_names:
            raise ValueError("profile features must exactly match weighted feature order")
        if self.query_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("query_digest must match the canonical semantic query")
        return self


class FeatureContribution(ContractModel):
    """One inspectable signed contribution and raw contrast."""

    feature_name: NonEmptyString
    query_value: FiniteFloat
    candidate_value: FiniteFloat
    scaled_query_value: FiniteFloat
    scaled_candidate_value: FiniteFloat
    scaled_contrast: FiniteFloat
    weight: NonNegativeFloat
    normalized_query_component: FiniteFloat | None = None
    normalized_candidate_component: FiniteFloat | None = None
    contribution: FiniteFloat

    @model_validator(mode="after")
    def scaled_values_are_coherent(self) -> Self:
        if not math.isclose(
            self.scaled_contrast,
            self.scaled_candidate_value - self.scaled_query_value,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError("scaled contrast must equal candidate minus query")
        if (self.normalized_query_component is None) != (
            self.normalized_candidate_component is None
        ):
            raise ValueError("normalized cosine components must be supplied together")
        return self


class ResearchCandidate(ContractModel):
    """A ranked real player with enough detail to reproduce its score."""

    rank: PositiveInt
    grain_id: NonEmptyString
    player_id: CanonicalPlayerId
    display_name: NonEmptyString
    competition_id: StrictUuid
    position_code: Literal["GK", "DF", "MD", "FW"]
    minutes: PositiveFloat
    score: NonNegativeFloat
    contributions: Annotated[tuple[FeatureContribution, ...], Field(min_length=1)]
    missing_features: tuple[NonEmptyString, ...] = ()
    limitations: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    claim_boundary: ResearchClaimBoundary = RESEARCH_CLAIM_BOUNDARY

    @model_validator(mode="after")
    def explanation_is_unique(self) -> Self:
        names = [item.feature_name for item in self.contributions]
        if len(names) != len(set(names)):
            raise ValueError("candidate contribution features must be unique")
        if len(self.missing_features) != len(set(self.missing_features)):
            raise ValueError("candidate missing features must be unique")
        if set(names) & set(self.missing_features):
            raise ValueError("contributed and missing features cannot overlap")
        return self


class RetrievalPopulationCounts(ContractModel):
    """Mutually exclusive filter accounting for full-population execution."""

    matrix_rows: PositiveInt
    competition_rows: NonNegativeInt
    position_exclusions: NonNegativeInt
    minimum_minutes_exclusions: NonNegativeInt
    explicit_player_exclusions: NonNegativeInt
    exemplar_self_exclusions: NonNegativeInt
    filter_admitted_rows: NonNegativeInt
    missing_feature_exclusions: NonNegativeInt
    scored_rows: NonNegativeInt
    returned_rows: NonNegativeInt

    @model_validator(mode="after")
    def counts_reconcile(self) -> Self:
        filter_excluded = (
            self.position_exclusions
            + self.minimum_minutes_exclusions
            + self.explicit_player_exclusions
            + self.exemplar_self_exclusions
        )
        if self.competition_rows != filter_excluded + self.filter_admitted_rows:
            raise ValueError("competition rows must reconcile to filters and admitted rows")
        if self.filter_admitted_rows != self.missing_feature_exclusions + self.scored_rows:
            raise ValueError("filter-admitted rows must reconcile to missing plus scored")
        if self.competition_rows > self.matrix_rows:
            raise ValueError("competition rows cannot exceed matrix rows")
        return self


class ResearchQueryResult(ContractModel):
    """Immutable deterministic ranking produced from the exact submitted request."""

    schema_version: SchemaVersion = 1
    result_id: StrictUuid
    request: ResearchQueryRequest
    generated_at: UtcInstant
    population: RetrievalPopulationCounts
    candidates: tuple[ResearchCandidate, ...]
    warnings: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    result_digest: Sha256Digest
    claim_boundary: ResearchClaimBoundary = RESEARCH_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"result_digest", "generated_at"})

    @model_validator(mode="after")
    def result_is_coherent(self) -> Self:
        if self.generated_at < self.request.requested_at:
            raise ValueError("result cannot be generated before its request")
        expected_returned = min(self.request.limit, self.population.scored_rows)
        if self.population.returned_rows != expected_returned:
            raise ValueError("returned rows must equal min(limit, scored rows)")
        if self.population.returned_rows != len(self.candidates):
            raise ValueError("returned row count must match candidates")
        if (
            self.request.mode is ResearchQueryMode.WEIGHTED_PROFILE
            and self.population.exemplar_self_exclusions != 0
        ):
            raise ValueError("profile queries cannot report exemplar-self exclusions")
        if self.population.exemplar_self_exclusions > 1:
            raise ValueError("an exemplar query can exclude at most one exact self row")
        if not self.request.filters.position_codes and self.population.position_exclusions != 0:
            raise ValueError("position exclusions require a submitted position filter")
        if (
            self.request.filters.minimum_minutes is None
            and self.population.minimum_minutes_exclusions != 0
        ):
            raise ValueError("minimum-minute exclusions require a submitted minutes filter")
        if (
            not self.request.filters.excluded_player_ids
            and self.population.explicit_player_exclusions != 0
        ):
            raise ValueError("explicit exclusions require submitted player ids")
        if self.population.explicit_player_exclusions > len(
            self.request.filters.excluded_player_ids
        ):
            raise ValueError("explicit exclusion count exceeds the submitted player set")
        ranks = [candidate.rank for candidate in self.candidates]
        if ranks != list(range(1, len(ranks) + 1)):
            raise ValueError("candidate ranks must be consecutive from one")
        order = [
            (candidate.score, candidate.player_id.bytes, candidate.grain_id)
            for candidate in self.candidates
        ]
        if order != sorted(order):
            raise ValueError("candidates must follow deterministic score/identity/grain order")
        grain_ids = [candidate.grain_id for candidate in self.candidates]
        player_ids = [candidate.player_id for candidate in self.candidates]
        if len(grain_ids) != len(set(grain_ids)) or len(player_ids) != len(set(player_ids)):
            raise ValueError("result candidate grains and players must be unique")
        weight_names = tuple(item.feature_name for item in self.request.weights)
        weights = tuple(item.weight for item in self.request.weights)
        for candidate in self.candidates:
            if candidate.competition_id != self.request.filters.competition_id:
                raise ValueError("candidate competition must equal the request filter")
            if candidate.player_id in self.request.filters.excluded_player_ids:
                raise ValueError("explicitly excluded player cannot be returned")
            if (
                self.request.filters.position_codes
                and candidate.position_code not in self.request.filters.position_codes
            ):
                raise ValueError("candidate position must satisfy the request filter")
            if (
                self.request.filters.minimum_minutes is not None
                and candidate.minutes < self.request.filters.minimum_minutes
            ):
                raise ValueError("candidate minutes must satisfy the request filter")
            if self.request.exemplar_grain_id == candidate.grain_id:
                raise ValueError("the exemplar grain cannot be returned")
            if candidate.missing_features:
                raise ValueError("scored candidates cannot miss an active feature")
            names = tuple(item.feature_name for item in candidate.contributions)
            contribution_weights = tuple(item.weight for item in candidate.contributions)
            if names != weight_names or contribution_weights != weights:
                raise ValueError("candidate contributions must match request feature order/weights")
            try:
                contribution_sum = stable_finite_sum(
                    tuple(item.contribution for item in candidate.contributions)
                )
            except StableNormalizationError as exc:
                raise ValueError("candidate contribution sum is not finite") from exc
            if self.request.method is ResearchMethod.WEIGHTED_EUCLIDEAN:
                invalid_euclidean_term = False
                for item in candidate.contributions:
                    expected_term = item.weight * item.scaled_contrast * item.scaled_contrast
                    if (
                        item.normalized_query_component is not None
                        or item.normalized_candidate_component is not None
                        or not math.isfinite(expected_term)
                        or not math.isclose(
                            item.contribution,
                            expected_term,
                            rel_tol=1e-12,
                            abs_tol=1e-12,
                        )
                    ):
                        invalid_euclidean_term = True
                        break
                if invalid_euclidean_term or not math.isclose(
                    candidate.score * candidate.score,
                    contribution_sum,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    raise ValueError("Euclidean contributions must reconcile to squared distance")
            else:
                try:
                    expected_query_components, query_is_zero = stable_weighted_unit_components(
                        tuple(item.scaled_query_value for item in candidate.contributions),
                        tuple(item.weight for item in candidate.contributions),
                    )
                    expected_candidate_components, candidate_is_zero = (
                        stable_weighted_unit_components(
                            tuple(item.scaled_candidate_value for item in candidate.contributions),
                            tuple(item.weight for item in candidate.contributions),
                        )
                    )
                except StableNormalizationError as exc:
                    raise ValueError("cosine explanation normalization is invalid") from exc
                zero_norm = query_is_zero or candidate_is_zero
                invalid_term = False
                for index, item in enumerate(candidate.contributions):
                    query_component = item.normalized_query_component
                    candidate_component = item.normalized_candidate_component
                    if query_component is None or candidate_component is None:
                        invalid_term = True
                        break
                    expected_query = 0.0 if zero_norm else expected_query_components[index]
                    expected_candidate = 0.0 if zero_norm else expected_candidate_components[index]
                    if not (
                        math.isclose(query_component, expected_query, rel_tol=1e-12, abs_tol=1e-12)
                        and math.isclose(
                            candidate_component,
                            expected_candidate,
                            rel_tol=1e-12,
                            abs_tol=1e-12,
                        )
                        and math.isclose(
                            item.contribution,
                            -(query_component * candidate_component),
                            rel_tol=1e-12,
                            abs_tol=1e-12,
                        )
                    ):
                        invalid_term = True
                        break
                if (
                    invalid_term
                    or candidate.score > 2.0
                    or not math.isclose(
                        candidate.score,
                        1.0 + contribution_sum,
                        rel_tol=1e-12,
                        abs_tol=1e-12,
                    )
                ):
                    raise ValueError("cosine contributions must reconcile to normalized operands")
        if self.result_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("result_digest must match the canonical semantic result")
        return self


class ResearchComparisonRequest(ContractModel):
    schema_version: SchemaVersion = 1
    comparison_id: StrictUuid
    result_id: StrictUuid
    result_digest: Sha256Digest
    query_digest: Sha256Digest
    pins: ResearchVersionPins
    grain_ids: Annotated[tuple[NonEmptyString, ...], Field(min_length=2, max_length=5)]
    comparison_request_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"comparison_request_digest"})

    @model_validator(mode="after")
    def request_is_coherent(self) -> Self:
        if len(self.grain_ids) != len(set(self.grain_ids)):
            raise ValueError("comparison grain ids must be unique")
        if self.comparison_request_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("comparison request digest must match its canonical projection")
        return self


class ResearchComparison(ContractModel):
    schema_version: SchemaVersion = 1
    request: ResearchComparisonRequest
    rows: Annotated[tuple[FeatureMatrixRow, ...], Field(min_length=2, max_length=5)]
    comparison_digest: Sha256Digest

    @model_validator(mode="after")
    def digest_and_rows_are_coherent(self) -> Self:
        ids = tuple(row.grain_id for row in self.rows)
        if ids != self.request.grain_ids:
            raise ValueError("comparison rows must exactly follow requested grain order")
        if any(row.feature_cutoff_ts != self.request.pins.feature_cutoff_ts for row in self.rows):
            raise ValueError("comparison row cutoff must equal the pinned cutoff")
        if any(
            (
                row.dataset_manifest_digest,
                row.identity_bundle_digest,
                row.canonical_build_digest,
                row.feature_registry_digest,
                row.eligibility_policy_digest,
            )
            != (
                self.request.pins.dataset_manifest_digest,
                self.request.pins.identity_bundle_digest,
                self.request.pins.canonical_build_digest,
                self.request.pins.feature_registry_digest,
                self.request.pins.eligibility_policy_digest,
            )
            for row in self.rows
        ):
            raise ValueError("comparison rows must match every submitted data/version pin")
        projection = self.model_dump(mode="json", exclude={"comparison_digest"})
        if self.comparison_digest != canonical_research_digest(projection):
            raise ValueError("comparison_digest must match the canonical comparison")
        return self


class ResearchReportDescriptor(ContractModel):
    """Digest and semantic bindings for locally persisted JSON/HTML report bytes."""

    report_format: Literal["json", "html"]
    report_relative_path: NonEmptyString
    report_digest: Sha256Digest
    generated_at: UtcInstant
    pins: ResearchVersionPins
    query_digest: Sha256Digest
    result_digest: Sha256Digest
    comparison_digest: Sha256Digest | None = None
    claim_boundary: ResearchClaimBoundary = RESEARCH_CLAIM_BOUNDARY

    @model_validator(mode="after")
    def report_path_is_safe(self) -> Self:
        if self.report_relative_path.startswith("/") or ".." in self.report_relative_path.split(
            "/"
        ):
            raise ValueError("report path must be a safe relative path")
        expected_suffix = f".{self.report_format}"
        if not self.report_relative_path.endswith(expected_suffix):
            raise ValueError("report path suffix must match report_format")
        return self


class SavedResearchExperiment(ContractModel):
    """Immutable stored query/result/comparison authority for exact replay."""

    schema_version: SchemaVersion = 1
    experiment_id: StrictUuid
    name: NonEmptyString
    note: NonEmptyString | None = None
    created_at: UtcInstant
    request: ResearchQueryRequest
    result: ResearchQueryResult
    comparison: ResearchComparison | None = None
    report: ResearchReportDescriptor
    experiment_digest: Sha256Digest

    @model_validator(mode="after")
    def experiment_is_coherent(self) -> Self:
        if self.request != self.result.request:
            raise ValueError("experiment request must equal the result request")
        if self.created_at < self.result.generated_at:
            raise ValueError("experiment cannot be created before its result")
        comparison_digest = self.comparison.comparison_digest if self.comparison else None
        if self.comparison is not None:
            request = self.comparison.request
            candidates_by_grain = {item.grain_id: item for item in self.result.candidates}
            if (
                request.result_id != self.result.result_id
                or request.result_digest != self.result.result_digest
                or request.query_digest != self.request.query_digest
                or request.pins != self.request.pins
                or not set(request.grain_ids).issubset(candidates_by_grain)
            ):
                raise ValueError("comparison must be pinned to candidates from this result")
            for row in self.comparison.rows:
                candidate = candidates_by_grain[row.grain_id]
                if (
                    row.player_id != candidate.player_id
                    or row.competition_id != candidate.competition_id
                    or row.position_code != candidate.position_code
                ):
                    raise ValueError("comparison row identity must equal its result candidate")
        if (
            self.report.pins != self.request.pins
            or self.report.query_digest != self.request.query_digest
            or self.report.result_digest != self.result.result_digest
            or self.report.comparison_digest != comparison_digest
        ):
            raise ValueError("report must bind the exact saved experiment components")
        if (
            self.report.generated_at < self.result.generated_at
            or self.created_at < self.report.generated_at
        ):
            raise ValueError("report generation must fall between result and experiment creation")
        projection = self.model_dump(mode="json", exclude={"experiment_digest"})
        if self.experiment_digest != canonical_research_digest(projection):
            raise ValueError("experiment_digest must match the canonical experiment")
        return self


class SavedResearchExperimentSummary(ContractModel):
    """Bounded list projection over indexed immutable experiment metadata."""

    schema_version: SchemaVersion = 1
    experiment_id: StrictUuid
    name: NonEmptyString
    note: NonEmptyString | None = None
    created_at: UtcInstant
    query_id: StrictUuid
    result_id: StrictUuid
    dataset_version: NonEmptyString
    dataset_manifest_digest: Sha256Digest
    matrix_version: NonEmptyString
    matrix_digest: Sha256Digest
    index_version: NonEmptyString
    index_manifest_digest: Sha256Digest
    report_format: Literal["json", "html"]
    report_relative_path: NonEmptyString
    report_digest: Sha256Digest
    experiment_digest: Sha256Digest

    @model_validator(mode="after")
    def report_path_is_safe(self) -> Self:
        if self.report_relative_path.startswith("/") or ".." in self.report_relative_path.split(
            "/"
        ):
            raise ValueError("report path must be a safe relative path")
        if not self.report_relative_path.endswith(f".{self.report_format}"):
            raise ValueError("report path suffix must match report_format")
        return self


class ResearchReplayStatus(StrEnum):
    REPRODUCED = "reproduced"
    INCOMPATIBLE_PINS = "incompatible_pins"
    RESULT_MISMATCH = "result_mismatch"


class ResearchReplayReason(StrEnum):
    EXACT_REPRODUCTION = "exact_reproduction"
    SAVED_ARTIFACTS_UNAVAILABLE_OR_REPLACED = "saved_artifacts_unavailable_or_replaced"
    DETERMINISTIC_RESULT_MISMATCH = "deterministic_result_mismatch"


class ResearchReplayReceipt(ContractModel):
    """Self-verifying evidence that the named saved experiment was replayed."""

    schema_version: SchemaVersion = 1
    replay_receipt_id: StrictUuid
    experiment_id: StrictUuid
    saved_experiment_digest: Sha256Digest
    saved_query_digest: Sha256Digest
    replay_query_digest: Sha256Digest
    replayed_at: UtcInstant
    saved_pins: ResearchVersionPins
    loaded_pins: ResearchVersionPins
    original_result_id: StrictUuid
    replay_result_id: StrictUuid
    original_result_digest: Sha256Digest
    replay_result_digest: Sha256Digest
    status: ResearchReplayStatus
    reason: ResearchReplayReason
    receipt_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"receipt_digest", "replayed_at"})

    @model_validator(mode="after")
    def receipt_is_coherent(self) -> Self:
        exact = (
            self.saved_pins == self.loaded_pins
            and self.saved_query_digest == self.replay_query_digest
            and self.original_result_id == self.replay_result_id
            and self.original_result_digest == self.replay_result_digest
        )
        expected_reason = {
            ResearchReplayStatus.REPRODUCED: ResearchReplayReason.EXACT_REPRODUCTION,
            ResearchReplayStatus.INCOMPATIBLE_PINS: (
                ResearchReplayReason.SAVED_ARTIFACTS_UNAVAILABLE_OR_REPLACED
            ),
            ResearchReplayStatus.RESULT_MISMATCH: (
                ResearchReplayReason.DETERMINISTIC_RESULT_MISMATCH
            ),
        }[self.status]
        if self.reason is not expected_reason:
            raise ValueError("replay reason must agree with its closed status")
        if (self.status is ResearchReplayStatus.REPRODUCED) != exact:
            raise ValueError("reproduced status requires exact pins, query, result ID and digest")
        if (
            self.status is ResearchReplayStatus.INCOMPATIBLE_PINS
            and self.saved_pins == self.loaded_pins
        ):
            raise ValueError("incompatible status requires different saved and loaded pins")
        if self.status is ResearchReplayStatus.RESULT_MISMATCH and (
            self.saved_pins != self.loaded_pins
            or self.saved_query_digest != self.replay_query_digest
        ):
            raise ValueError("result mismatch requires identical saved query and compatible pins")
        if self.receipt_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("receipt_digest must match the canonical replay receipt")
        return self


__all__ = [
    "EligibilityDecision",
    "EligibilityReason",
    "EligibilityReasonCount",
    "FeatureContribution",
    "FeatureMatrixManifest",
    "FeatureMatrixRow",
    "FeatureValueState",
    "FeatureWeight",
    "MatrixCatalogueEntry",
    "MinuteEvidenceState",
    "NamedFeatureValue",
    "PopulationDecisionReason",
    "RESEARCH_CLAIM_BOUNDARY",
    "ResearchArtifactFile",
    "ResearchCandidate",
    "ResearchCapability",
    "ResearchClaimBoundary",
    "ResearchComparison",
    "ResearchComparisonRequest",
    "ResearchCoverage",
    "ResearchDatasetDescriptor",
    "ResearchFeatureValue",
    "ResearchFilters",
    "ResearchIndexManifest",
    "ResearchMethod",
    "ResearchQueryMode",
    "ResearchQueryRequest",
    "ResearchQueryResult",
    "ResearchReplayReason",
    "ResearchReplayReceipt",
    "ResearchReplayStatus",
    "ResearchReportDescriptor",
    "ResearchVersionPins",
    "RetrievalPopulationCounts",
    "SavedResearchExperiment",
    "SavedResearchExperimentSummary",
    "SourcePopulationDecision",
    "canonical_research_digest",
    "population_referred_grain_digest",
    "rows_semantic_digest",
]

"""Deterministic W05 feature-registry loading and synthetic-only materialisation.

This module deliberately has no provider or product imports.  The governed W04
bridge admits an already accepted Gold projection supplied by its caller; synthetic
development data is separately identified and calculated from local fixture inputs.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID

from scouting.contracts.m0 import (
    W04_REAL_GOVERNED_FEATURE_DESCRIPTOR_DIGEST,
    W04_REAL_GOVERNED_FEATURE_NAMES,
    W04_REAL_GOVERNED_FEATURE_REGISTRY_CANONICAL_DIGEST,
    W04_REAL_GOVERNED_FEATURE_REGISTRY_DECISION_DIGEST,
    W04_REAL_GOVERNED_FEATURE_REGISTRY_ID,
    FeatureValue,
    FeatureValueState,
)


class FeatureRegistryError(ValueError):
    """Raised when a feature registry, fixture, or admission is not exact."""


_ROOT_KEYS = frozenset({"registry_id", "registry_version", "families", "registry_digest"})
_FAMILY_KEYS = frozenset(
    {
        "family_id",
        "family_version",
        "evidence_class",
        "provider_source",
        "production_evidence",
        "protected_evaluation",
        "claim",
        "schema",
        "metadata_control_schema",
        "w04_authority",
        "family_digest",
    }
)
_SCHEMA_KEYS = frozenset({"schema_id", "schema_version", "schema_hash", "features"})
_CONTROL_SCHEMA_KEYS = _SCHEMA_KEYS | frozenset({"control_only"})
_FEATURE_KEYS = frozenset(
    {
        "name",
        "order",
        "football_definition",
        "numeric_output_type",
        "unit",
        "numerator_inputs",
        "denominator_inputs",
        "denominator_formula",
        "missing_policy",
        "zero_policy",
        "suppression_policy",
        "unavailable_policy",
        "imputation",
        "as_of_available_at_rule",
        "dependency_lineage_rule",
        "control_only",
    }
)
_W04_AUTHORITY_KEYS = frozenset(
    {
        "candidate_id",
        "candidate_digest",
        "decision_id",
        "decision_digest",
        "descriptor_digest",
        "accepted_gold_row_rule",
        "suppressed_or_unavailable",
    }
)
_FIXTURE_KEYS = frozenset(
    {
        "fixture_id",
        "fixture_version",
        "registry_id",
        "registry_digest",
        "family_id",
        "family_digest",
        "development_peer_group_notice",
        "complete_rows",
        "edge_rows",
        "fixture_digest",
    }
)
_ROW_KEYS = frozenset(
    {
        "player_id",
        "synthetic_position_code",
        "synthetic_age_years",
        "synthetic_elapsed_minutes",
        "feature_cutoff_ts",
        "observed_at",
        "available_at",
        "raw_numerator_inputs",
        "expected_feature_values",
        "constructed_development_peer_group",
        "dependency_identity",
        "state_overrides",
    }
)
_DEPENDENCY_KEYS = frozenset({"lineage_hash", "dependencies"})
_DEPENDENCY_ITEM_KEYS = frozenset({"dependency_id", "digest", "observed_at", "available_at"})

_ACCEPTED_REGISTRY_ID = "w05-m0-feature-registry-v1"
_ACCEPTED_REGISTRY_VERSION = "v1"
_ACCEPTED_REGISTRY_DIGEST = "c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644"
_ACCEPTED_W04_FAMILY = (
    "w05-w04-real-governed-bridge-v1",
    "v1",
    "b3854c5fe1c120233475e3b8224c3f3592d06d656447dedd4f764fe45da36d9b",
)
_ACCEPTED_SYNTHETIC_FAMILY = (
    "w05-synthetic-development-v1",
    "v1",
    "8c0845ab46a71d5cd6542b3e80c568b6a678ab5a9dffbe543e894d6d78eca047",
)
_ACCEPTED_SCHEMA_IDENTITIES = (
    (
        "w05-w04-real-governed-exact-four-v1",
        "v1",
        "cf8847f2b1f70ebf293ce90e48817e80a4e47b78316079bd88e8c2a80bc08127",
    ),
    (
        "w05-synthetic-development-resemblance-v1",
        "v1",
        "1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f",
    ),
    (
        "w05-synthetic-development-metadata-controls-v1",
        "v1",
        "eae69d45d076f4fc07127d3fd08f45d5ae3d4a7c99ae203d7f63e8a56c88abdb",
    ),
)
_ACCEPTED_FIXTURE_ID = "w05-synthetic-development-features-v1"
_ACCEPTED_FIXTURE_VERSION = "v1"
_ACCEPTED_FIXTURE_DIGEST = "7abd569366caa439cc28563a53c51a0c7ecdd1dfb622bee49d69957f444b9545"

_W04_GOLD_PROJECTION = {
    "product_build_id": "b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79",
    "gold_manifest_relative_path": (
        "data/manifests/wyscout/v5/gold/"
        "b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79.manifest.json"
    ),
    "gold_manifest_physical_sha256": (
        "08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068"
    ),
    "gold_product_relative_path": (
        "data/working/wyscout/v5/gold/"
        "build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/"
        "player-window/competition_id=cb5c5317-fa4a-571e-93dc-ef6ce482eab7/"
        "window_definition_id=a0af8d56-e41d-5467-b46e-82887c4861e0/"
        "window_start_utc=20170811T000000000000Z/window_end_utc=20170812T000000000000Z/"
        "feature_cutoff_ts=20260801T000000000000Z/part-00000.parquet"
    ),
    "gold_product_physical_sha256": (
        "6e49b4322c766352fdc427b8d35d73ddaed036d0bd19f1d65435fe3a72edcd17"
    ),
    "gold_product_semantic_sha256": (
        "f1751b4f1ff7911ad339fa1954cd5c88483fc09c733547dba87d7aa301c1bffa"
    ),
    "gold_row_count": 1,
    "feature_schema_hash": "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f",
    "player_id": "be8da881-2b15-513f-978f-6bb3865bc8e2",
    "competition_id": "cb5c5317-fa4a-571e-93dc-ef6ce482eab7",
    "season_id": "4696aa1f-b512-5d18-af79-33cf031455cf",
    "window_definition_id": "a0af8d56-e41d-5467-b46e-82887c4861e0",
    "snapshot_as_of_ts": "2017-08-11T18:45:00Z",
    "available_at_watermark": "2026-07-31T14:15:26Z",
    "feature_cutoff_ts": "2026-08-01T00:00:00Z",
    "applicability": "research_only",
}
_W04_DEPENDENCIES = (
    {
        "kind": "source_manifest",
        "dependency_id": "4e16bdb5-afe7-5601-88ad-adc124cfce3b",
        "digest": "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd",
        "observed_at": "2020-01-28T14:24:27Z",
        "available_at": "2020-01-28T14:24:27Z",
    },
    {
        "kind": "identity_evidence",
        "dependency_id": "31638732-5b25-57db-9eb4-8e943a47a387",
        "digest": "4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80",
        "observed_at": "2026-07-31T12:44:27Z",
        "available_at": "2026-07-31T14:15:26Z",
    },
    {
        "kind": "feature_schema",
        "dependency_id": "32351f4a-4c59-567f-87b5-15364a8d4f47",
        "digest": "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f",
        "observed_at": "2026-07-31T08:37:00Z",
        "available_at": "2026-07-31T10:15:16Z",
    },
    {
        "kind": "feature_schema",
        "dependency_id": "342eb513-ad1c-5d65-aea5-abc2d9c14383",
        "digest": "3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881",
        "observed_at": "2026-07-30T22:14:21Z",
        "available_at": "2026-07-31T08:28:40Z",
    },
    {
        "kind": "feature_schema",
        "dependency_id": "f65e539c-0021-53b6-9b20-27bc2aefad3d",
        "digest": "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959",
        "observed_at": "2026-07-30T20:22:17Z",
        "available_at": "2026-07-30T21:21:23Z",
    },
)
_W04_LINEAGE_HASH = "ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d"


def canonical_json_bytes(value: Any) -> bytes:
    """Return the only admissible compact UTF-8 JSON representation."""
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


def canonical_digest(value: Mapping[str, Any], digest_key: str) -> str:
    """Hash a mapping after excluding exactly its self-referential digest field."""
    if digest_key not in value:
        raise FeatureRegistryError(f"missing {digest_key}")
    payload = dict(value)
    payload.pop(digest_key)
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _require_exact_keys(value: Mapping[str, Any], expected: frozenset[str], context: str) -> None:
    actual = frozenset(value)
    if actual != expected:
        raise FeatureRegistryError(
            f"{context} keys must be exact; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _require_str(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise FeatureRegistryError(f"{context} must be a non-empty string")
    return value


def _require_sha256(value: object, context: str) -> str:
    """Require an exact lower-case SHA-256 identity, never a caller label."""
    text = _require_str(value, context)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise FeatureRegistryError(f"{context} must be a lowercase SHA-256 digest")
    return text


def _parse_instant(value: object, context: str) -> datetime:
    text = _require_str(value, context)
    if not text.endswith("Z"):
        raise FeatureRegistryError(f"{context} must be a UTC Z instant")
    try:
        return datetime.fromisoformat(f"{text[:-1]}+00:00")
    except ValueError as error:
        raise FeatureRegistryError(f"{context} must be an ISO-8601 UTC instant") from error


def _strict_decimal(value: object, context: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise FeatureRegistryError(f"{context} must be a numeric JSON value")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise FeatureRegistryError(f"{context} must be a valid decimal") from error
    if not result.is_finite() or result < 0:
        raise FeatureRegistryError(f"{context} must be finite and non-negative")
    return result


@dataclass(frozen=True)
class FeatureDefinition:
    """One ordered, fully declared feature or metadata-only control."""

    name: str
    order: int
    football_definition: str
    numeric_output_type: str
    unit: str
    numerator_inputs: tuple[str, ...]
    denominator_inputs: tuple[str, ...]
    denominator_formula: str
    missing_policy: str
    zero_policy: str
    suppression_policy: str
    unavailable_policy: str
    imputation: str
    as_of_available_at_rule: str
    dependency_lineage_rule: str
    control_only: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], *, control_only: bool) -> FeatureDefinition:
        _require_exact_keys(value, _FEATURE_KEYS, "feature definition")
        order = value["order"]
        if isinstance(order, bool) or not isinstance(order, int) or order < 1:
            raise FeatureRegistryError("feature order must be a positive integer")
        if value["control_only"] is not control_only:
            raise FeatureRegistryError("feature control_only must match its containing schema")
        strings = {
            key: _require_str(value[key], f"feature {key}")
            for key in _FEATURE_KEYS
            - {"order", "numerator_inputs", "denominator_inputs", "control_only"}
        }
        numerator = value["numerator_inputs"]
        denominator = value["denominator_inputs"]
        if not isinstance(numerator, list) or not isinstance(denominator, list):
            raise FeatureRegistryError("feature input lists must be JSON lists")
        numerator_inputs = tuple(
            _require_str(item, "feature numerator input") for item in numerator
        )
        denominator_inputs = tuple(
            _require_str(item, "feature denominator input") for item in denominator
        )
        if len(numerator_inputs) != len(set(numerator_inputs)) or len(denominator_inputs) != len(
            set(denominator_inputs)
        ):
            raise FeatureRegistryError(
                "feature numerator and denominator inputs must each be unique"
            )
        if strings["imputation"] != "FORBIDDEN":
            raise FeatureRegistryError("feature imputation must be FORBIDDEN")
        return cls(
            name=strings["name"],
            order=order,
            football_definition=strings["football_definition"],
            numeric_output_type=strings["numeric_output_type"],
            unit=strings["unit"],
            numerator_inputs=numerator_inputs,
            denominator_inputs=denominator_inputs,
            denominator_formula=strings["denominator_formula"],
            missing_policy=strings["missing_policy"],
            zero_policy=strings["zero_policy"],
            suppression_policy=strings["suppression_policy"],
            unavailable_policy=strings["unavailable_policy"],
            imputation=strings["imputation"],
            as_of_available_at_rule=strings["as_of_available_at_rule"],
            dependency_lineage_rule=strings["dependency_lineage_rule"],
            control_only=control_only,
        )


@dataclass(frozen=True)
class FeatureSchema:
    """A content-addressed ordered schema."""

    schema_id: str
    schema_version: str
    schema_hash: str
    features: tuple[FeatureDefinition, ...]
    control_only: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], *, control_only: bool) -> FeatureSchema:
        _require_exact_keys(
            value, _CONTROL_SCHEMA_KEYS if control_only else _SCHEMA_KEYS, "feature schema"
        )
        if control_only and value["control_only"] is not True:
            raise FeatureRegistryError("metadata-control schema must declare control_only=true")
        raw_features = value["features"]
        if not isinstance(raw_features, list) or not raw_features:
            raise FeatureRegistryError("feature schema must contain a non-empty feature list")
        if any(not isinstance(item, dict) for item in raw_features):
            raise FeatureRegistryError("feature schema entries must be objects")
        features = tuple(
            FeatureDefinition.from_mapping(item, control_only=control_only) for item in raw_features
        )
        names = tuple(item.name for item in features)
        orders = tuple(item.order for item in features)
        if len(names) != len(set(names)) or orders != tuple(range(1, len(features) + 1)):
            raise FeatureRegistryError(
                "feature names and order positions must be unique and contiguous"
            )
        payload = dict(value)
        payload.pop("schema_hash")
        expected_hash = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
        if value["schema_hash"] != expected_hash:
            raise FeatureRegistryError(
                "feature schema_hash must equal the canonical schema SHA-256"
            )
        return cls(
            schema_id=_require_str(value["schema_id"], "schema_id"),
            schema_version=_require_str(value["schema_version"], "schema_version"),
            schema_hash=_require_str(value["schema_hash"], "schema_hash"),
            features=features,
            control_only=control_only,
        )


@dataclass(frozen=True)
class FeatureFamily:
    """One cryptographically isolated evidence family."""

    family_id: str
    family_version: str
    evidence_class: str
    provider_source: str
    production_evidence: bool
    protected_evaluation: bool
    claim: str
    schema: FeatureSchema
    metadata_control_schema: FeatureSchema | None
    w04_authority: Mapping[str, str] | None
    family_digest: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> FeatureFamily:
        _require_exact_keys(value, _FAMILY_KEYS, "feature family")
        if canonical_digest(value, "family_digest") != value["family_digest"]:
            raise FeatureRegistryError("family_digest must equal the canonical family SHA-256")
        schema_value = value["schema"]
        if not isinstance(schema_value, dict):
            raise FeatureRegistryError("feature family schema must be an object")
        evidence_class = _require_str(value["evidence_class"], "evidence_class")
        is_synthetic = evidence_class == "synthetic_development"
        schema = FeatureSchema.from_mapping(schema_value, control_only=False)
        raw_control = value["metadata_control_schema"]
        metadata_control_schema = None
        if raw_control is not None:
            if not isinstance(raw_control, dict):
                raise FeatureRegistryError("metadata_control_schema must be an object or null")
            metadata_control_schema = FeatureSchema.from_mapping(raw_control, control_only=True)
        raw_authority = value["w04_authority"]
        w04_authority = None
        if raw_authority is not None:
            if not isinstance(raw_authority, dict):
                raise FeatureRegistryError("w04_authority must be an object or null")
            _require_exact_keys(raw_authority, _W04_AUTHORITY_KEYS, "w04_authority")
            w04_authority = {
                key: _require_str(item, f"w04_authority {key}")
                for key, item in raw_authority.items()
            }
        if is_synthetic:
            if (
                value["provider_source"] != "NONE"
                or value["production_evidence"] is not False
                or value["protected_evaluation"] is not False
                or value["claim"] != "constructed_W05_development_only"
                or metadata_control_schema is None
                or w04_authority is not None
            ):
                raise FeatureRegistryError(
                    "synthetic-development family must remain cryptographically separate"
                )
        else:
            if metadata_control_schema is not None or w04_authority is None:
                raise FeatureRegistryError(
                    "W04 governed family must use its bridge and no metadata controls"
                )
        return cls(
            family_id=_require_str(value["family_id"], "family_id"),
            family_version=_require_str(value["family_version"], "family_version"),
            evidence_class=evidence_class,
            provider_source=_require_str(value["provider_source"], "provider_source"),
            production_evidence=value["production_evidence"],
            protected_evaluation=value["protected_evaluation"],
            claim=_require_str(value["claim"], "claim"),
            schema=schema,
            metadata_control_schema=metadata_control_schema,
            w04_authority=w04_authority,
            family_digest=_require_str(value["family_digest"], "family_digest"),
        )


@dataclass(frozen=True)
class FeatureRegistry:
    """The self-verifying W05 feature collection."""

    registry_id: str
    registry_version: str
    families: tuple[FeatureFamily, ...]
    registry_digest: str

    @property
    def w04_family(self) -> FeatureFamily:
        return self._family_for("w04_real_governed")

    @property
    def synthetic_family(self) -> FeatureFamily:
        return self._family_for("synthetic_development")

    def _family_for(self, evidence_class: str) -> FeatureFamily:
        matches = [family for family in self.families if family.evidence_class == evidence_class]
        if len(matches) != 1:
            raise FeatureRegistryError(
                "registry must contain exactly one requested evidence family"
            )
        return matches[0]


def _load_exact_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise FeatureRegistryError(f"{path} is not JSON") from error
    if not isinstance(value, dict):
        raise FeatureRegistryError(f"{path} root must be an object")
    if raw != canonical_json_bytes(value) + b"\n":
        raise FeatureRegistryError(f"{path} must use exact compact canonical JSON bytes")
    return value


def load_feature_registry(path: str | Path) -> FeatureRegistry:
    """Load a compact, self-verifying W05 registry without reading any provider data."""
    value = _load_exact_json(Path(path))
    _require_exact_keys(value, _ROOT_KEYS, "feature registry")
    if canonical_digest(value, "registry_digest") != value["registry_digest"]:
        raise FeatureRegistryError("registry_digest must equal the canonical registry SHA-256")
    raw_families = value["families"]
    if not isinstance(raw_families, list) or len(raw_families) != 2:
        raise FeatureRegistryError("registry must contain exactly two evidence families")
    if any(not isinstance(item, dict) for item in raw_families):
        raise FeatureRegistryError("registry families must be objects")
    families = tuple(FeatureFamily.from_mapping(item) for item in raw_families)
    if (
        len({item.family_id for item in families}) != 2
        or len({item.evidence_class for item in families}) != 2
    ):
        raise FeatureRegistryError("registry family IDs and evidence classes must be unique")
    registry = FeatureRegistry(
        registry_id=_require_str(value["registry_id"], "registry_id"),
        registry_version=_require_str(value["registry_version"], "registry_version"),
        families=families,
        registry_digest=_require_str(value["registry_digest"], "registry_digest"),
    )
    _require_accepted_registry_identity(registry)
    _validate_w04_bridge(registry.w04_family)
    _reject_synthetic_claim_language(registry.synthetic_family)
    synthetic_names = tuple(item.name for item in registry.synthetic_family.schema.features)
    if synthetic_names != (
        "synthetic_progression_actions_per_90",
        "synthetic_final_third_entries_per_90",
        "synthetic_chance_creation_actions_per_90",
        "synthetic_defensive_disruptions_per_90",
        "synthetic_ball_retention_ratio",
        "synthetic_aerial_involvements_per_90",
    ):
        raise FeatureRegistryError(
            "synthetic-development schema must retain its exact ordered names"
        )
    metadata_control_schema = registry.synthetic_family.metadata_control_schema
    if metadata_control_schema is None:
        raise FeatureRegistryError("synthetic metadata-control schema is required")
    if tuple(item.name for item in metadata_control_schema.features) != (
        "synthetic_position_code",
        "synthetic_age_years",
        "synthetic_elapsed_minutes",
    ):
        raise FeatureRegistryError("synthetic metadata-control schema must retain its exact order")
    return registry


def _require_accepted_registry_identity(registry: FeatureRegistry) -> None:
    """Pin W05 v1 identities independently from candidate-carried self-digests."""
    if (registry.registry_id, registry.registry_version, registry.registry_digest) != (
        _ACCEPTED_REGISTRY_ID,
        _ACCEPTED_REGISTRY_VERSION,
        _ACCEPTED_REGISTRY_DIGEST,
    ):
        raise FeatureRegistryError("registry accepted-identity mismatch")
    w04 = registry.w04_family
    synthetic = registry.synthetic_family
    if (w04.family_id, w04.family_version, w04.family_digest) != _ACCEPTED_W04_FAMILY:
        raise FeatureRegistryError("W04 family accepted-identity mismatch")
    if (synthetic.family_id, synthetic.family_version, synthetic.family_digest) != (
        _ACCEPTED_SYNTHETIC_FAMILY
    ):
        raise FeatureRegistryError("synthetic family accepted-identity mismatch")
    metadata_control_schema = synthetic.metadata_control_schema
    if metadata_control_schema is None:
        raise FeatureRegistryError("synthetic metadata-control schema is required")
    observed = (
        (w04.schema.schema_id, w04.schema.schema_version, w04.schema.schema_hash),
        (synthetic.schema.schema_id, synthetic.schema.schema_version, synthetic.schema.schema_hash),
        (
            metadata_control_schema.schema_id,
            metadata_control_schema.schema_version,
            metadata_control_schema.schema_hash,
        ),
    )
    if observed != _ACCEPTED_SCHEMA_IDENTITIES:
        raise FeatureRegistryError("feature schema accepted-identity mismatch")


def _reject_synthetic_claim_language(family: FeatureFamily) -> None:
    """Synthetic descriptors may not be re-signed into provider or evaluation claims."""
    definitions = [
        definition.football_definition
        for schema in (family.schema, family.metadata_control_schema)
        if schema is not None
        for definition in schema.features
    ]
    text = " ".join((family.claim, family.provider_source, *definitions)).lower()
    if any(
        word in text for word in ("wyscout", "production", "expert", "recruitment", "validation")
    ):
        raise FeatureRegistryError("synthetic descriptor contains forbidden claim language")


def _validate_w04_bridge(family: FeatureFamily) -> None:
    if (
        family.evidence_class != "w04_real_governed"
        or family.provider_source != "GOVERNED_W04_GOLD_ONLY"
        or family.production_evidence is not False
        or family.protected_evaluation is not False
        or family.w04_authority is None
    ):
        raise FeatureRegistryError("W04 bridge must be a governed real-data bridge")
    authority = family.w04_authority
    expected = {
        "candidate_id": W04_REAL_GOVERNED_FEATURE_REGISTRY_ID,
        "candidate_digest": W04_REAL_GOVERNED_FEATURE_REGISTRY_CANONICAL_DIGEST,
        "decision_id": "w04-wyscout-supported-feature-registry-decisions-v1",
        "decision_digest": W04_REAL_GOVERNED_FEATURE_REGISTRY_DECISION_DIGEST,
        "descriptor_digest": W04_REAL_GOVERNED_FEATURE_DESCRIPTOR_DIGEST,
    }
    if any(authority[key] != item for key, item in expected.items()):
        raise FeatureRegistryError("W04 bridge must reference the accepted authority identities")
    if tuple(item.name for item in family.schema.features) != W04_REAL_GOVERNED_FEATURE_NAMES:
        raise FeatureRegistryError("W04 bridge must admit exactly the accepted four descriptors")
    if any(
        item.numeric_output_type != "int64"
        or item.denominator_formula != "NONE"
        or item.imputation != "FORBIDDEN"
        for item in family.schema.features
    ):
        raise FeatureRegistryError("W04 bridge cannot reinterpret count outputs or impute them")


def _validate_lineage(value: Mapping[str, Any], cutoff: datetime) -> str:
    _require_exact_keys(value, _DEPENDENCY_KEYS, "dependency identity")
    raw_dependencies = value["dependencies"]
    if not isinstance(raw_dependencies, list) or not raw_dependencies:
        raise FeatureRegistryError("dependency identity must contain dependencies")
    if any(not isinstance(item, dict) for item in raw_dependencies):
        raise FeatureRegistryError("dependency entries must be objects")
    dependencies: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in raw_dependencies:
        _require_exact_keys(item, _DEPENDENCY_ITEM_KEYS, "dependency entry")
        dependency_id = _require_str(item["dependency_id"], "dependency_id")
        try:
            UUID(dependency_id)
        except ValueError as error:
            raise FeatureRegistryError("dependency_id must be a UUID") from error
        if dependency_id in seen:
            raise FeatureRegistryError("dependency identity cannot contain duplicate IDs")
        seen.add(dependency_id)
        _require_sha256(item["digest"], "dependency digest")
        observed_at = _parse_instant(item["observed_at"], "dependency observed_at")
        available_at = _parse_instant(item["available_at"], "dependency available_at")
        if observed_at >= cutoff or available_at >= cutoff:
            raise FeatureRegistryError("every dependency must be strictly before feature_cutoff_ts")
        dependencies.append({key: _require_str(item[key], f"dependency {key}") for key in item})
    expected = hashlib.sha256(canonical_json_bytes(dependencies)).hexdigest()
    if value["lineage_hash"] != expected:
        raise FeatureRegistryError("dependency lineage_hash must bind exact dependency identities")
    return expected


def _feature_value(state: str, value: Decimal | None, reason: str | None) -> FeatureValue:
    if state == "observed":
        if value is None:
            raise FeatureRegistryError("observed feature calculation requires a numeric value")
        converted = float(value)
        if not math.isfinite(converted):
            raise FeatureRegistryError("decimal calculation cannot convert to a finite float")
        if value == 0:
            return FeatureValue(state=FeatureValueState.ZERO, numeric_value=0.0)
        return FeatureValue(state=FeatureValueState.VALUE, numeric_value=converted)
    states = {
        "missing": FeatureValueState.MISSING,
        "suppressed": FeatureValueState.SUPPRESSED,
        "unavailable": FeatureValueState.UNAVAILABLE,
    }
    if state not in states or reason is None:
        raise FeatureRegistryError(
            "feature state override must be observed, missing, suppressed, or unavailable"
        )
    return FeatureValue(state=states[state], reason_code=reason)


def _expected_feature_value(value: object) -> FeatureValue:
    """Parse fixture FeatureValues without permitting a loose model projection."""
    item = _mapping(value, "expected FeatureValue")
    state = item.get("state")
    if state in {"value", "zero"}:
        _require_exact_keys(item, frozenset({"state", "numeric_value"}), "expected FeatureValue")
        numeric = item["numeric_value"]
        if isinstance(numeric, bool) or not isinstance(numeric, (int, float)):
            raise FeatureRegistryError("expected numeric FeatureValue must be a JSON number")
        return FeatureValue(
            state=FeatureValueState.VALUE if state == "value" else FeatureValueState.ZERO,
            numeric_value=float(numeric),
        )
    if state in {"missing", "suppressed", "unavailable"}:
        _require_exact_keys(item, frozenset({"state", "reason_code"}), "expected FeatureValue")
        return FeatureValue(
            state=FeatureValueState(state),
            reason_code=_require_str(item["reason_code"], "reason_code"),
        )
    raise FeatureRegistryError("expected FeatureValue state is invalid")


@dataclass(frozen=True)
class MaterializedFeatureRow:
    """One ordered calculation result with pinned schema and lineage identity."""

    player_id: UUID
    feature_schema_hash: str
    dependency_lineage_hash: str
    values: tuple[FeatureValue, ...]


def materialize_synthetic_row(
    row: Mapping[str, Any], registry: FeatureRegistry
) -> MaterializedFeatureRow:
    """Materialize one synthetic-development row with Decimal arithmetic and fail-closed states."""
    _require_exact_keys(row, _ROW_KEYS, "synthetic feature row")
    family = registry.synthetic_family
    try:
        player_id = UUID(_require_str(row["player_id"], "player_id"))
    except ValueError as error:
        raise FeatureRegistryError("player_id must be a UUID") from error
    cutoff = _parse_instant(row["feature_cutoff_ts"], "feature_cutoff_ts")
    observed_at = _parse_instant(row["observed_at"], "observed_at")
    available_at = _parse_instant(row["available_at"], "available_at")
    if observed_at >= cutoff or available_at >= cutoff:
        raise FeatureRegistryError(
            "synthetic row observed_at and available_at must be strictly before cutoff"
        )
    _validate_lineage(_mapping(row["dependency_identity"], "dependency_identity"), cutoff)
    raw = _mapping(row["raw_numerator_inputs"], "raw_numerator_inputs")
    overrides = _mapping(row["state_overrides"], "state_overrides")
    _require_str(row["synthetic_position_code"], "synthetic_position_code")
    age = row["synthetic_age_years"]
    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        raise FeatureRegistryError("synthetic_age_years must be a non-negative integer control")
    allowed_inputs = {
        input_name for feature in family.schema.features for input_name in feature.numerator_inputs
    } | {"synthetic_attempts"}
    if frozenset(raw) != allowed_inputs:
        raise FeatureRegistryError("synthetic raw numerator inputs must be exact and complete")
    if any(
        not isinstance(key, str) or not isinstance(value, str) for key, value in overrides.items()
    ):
        raise FeatureRegistryError("state_overrides must map feature names to states")
    feature_names = {feature.name for feature in family.schema.features}
    if not frozenset(overrides).issubset(feature_names):
        raise FeatureRegistryError("state_overrides cannot contain unknown features")
    elapsed = _strict_decimal(row["synthetic_elapsed_minutes"], "synthetic_elapsed_minutes")
    numerators = {key: _strict_decimal(value, f"raw numerator {key}") for key, value in raw.items()}
    values: list[FeatureValue] = []
    for feature in family.schema.features:
        override = overrides.get(feature.name, "observed")
        if override != "observed":
            values.append(_feature_value(override, None, f"synthetic_{override}_declared"))
            continue
        if feature.denominator_formula == "synthetic_elapsed_minutes / 90":
            if elapsed == 0:
                raise FeatureRegistryError(
                    "synthetic elapsed minutes cannot become a zero denominator"
                )
            result = numerators[feature.numerator_inputs[0]] / elapsed * Decimal("90")
        elif feature.denominator_formula == "synthetic_attempts":
            attempts = numerators["synthetic_attempts"]
            if attempts == 0:
                raise FeatureRegistryError("synthetic attempts cannot become a zero denominator")
            result = numerators[feature.numerator_inputs[0]] / attempts
        else:
            raise FeatureRegistryError("synthetic feature has an unsupported denominator formula")
        values.append(_feature_value("observed", result, None))
    lineage_hash = _validate_lineage(
        _mapping(row["dependency_identity"], "dependency_identity"), cutoff
    )
    return MaterializedFeatureRow(
        player_id=player_id,
        feature_schema_hash=family.schema.schema_hash,
        dependency_lineage_hash=lineage_hash,
        values=tuple(values),
    )


def materialize_w04_real_row(
    row: Mapping[str, Any], registry: FeatureRegistry
) -> MaterializedFeatureRow:
    """Admit only an exact pre-cutoff accepted-Gold count projection; never read W04 bytes."""
    expected_keys = frozenset(
        {
            "evidence_class",
            "w04_authority",
            "dependency_identity",
            "counts",
            *_W04_GOLD_PROJECTION.keys(),
        }
    )
    _require_exact_keys(row, expected_keys, "W04 real feature row")
    if row["evidence_class"] != "w04_real_governed":
        raise FeatureRegistryError("W04 evidence-class substitution is forbidden")
    gold_row_count = row["gold_row_count"]
    if (
        isinstance(gold_row_count, bool)
        or not isinstance(gold_row_count, int)
        or gold_row_count != 1
    ):
        raise FeatureRegistryError("W04 gold_row_count must be the non-boolean integer 1")
    if any(row[key] != value for key, value in _W04_GOLD_PROJECTION.items()):
        raise FeatureRegistryError("W04 accepted Gold projection identity mismatch")
    cutoff = _parse_instant(_W04_GOLD_PROJECTION["feature_cutoff_ts"], "feature_cutoff_ts")
    _validate_w04_dependency_envelope(
        _mapping(row["dependency_identity"], "dependency_identity"), cutoff
    )
    authority = _mapping(row["w04_authority"], "w04_authority")
    accepted_authority = registry.w04_family.w04_authority
    if accepted_authority is None:
        raise FeatureRegistryError("W04 authority is required")
    if authority != accepted_authority:
        raise FeatureRegistryError("W04 authority substitution is forbidden")
    counts = _mapping(row["counts"], "counts")
    if tuple(counts) != W04_REAL_GOVERNED_FEATURE_NAMES:
        raise FeatureRegistryError(
            "W04 count inputs must use the exact accepted four-feature order"
        )
    values: list[FeatureValue] = []
    for name in W04_REAL_GOVERNED_FEATURE_NAMES:
        value = counts[name]
        expected_value = (2, 2, 1, 2)[len(values)]
        if isinstance(value, bool) or not isinstance(value, int) or value != expected_value:
            raise FeatureRegistryError("W04 counts must equal the accepted one-row feature vector")
        converted = float(value)
        if not math.isfinite(converted) or int(converted) != value:
            raise FeatureRegistryError(
                "W04 count cannot lose int64 identity at the FeatureValue boundary"
            )
        values.append(
            FeatureValue(
                state=FeatureValueState.ZERO if value == 0 else FeatureValueState.VALUE,
                numeric_value=converted,
            )
        )
    return MaterializedFeatureRow(
        player_id=UUID(_require_str(_W04_GOLD_PROJECTION["player_id"], "W04 player_id")),
        feature_schema_hash=registry.w04_family.schema.schema_hash,
        dependency_lineage_hash=_W04_LINEAGE_HASH,
        values=tuple(values),
    )


def _validate_w04_dependency_envelope(value: Mapping[str, Any], cutoff: datetime) -> None:
    """Require the exact five immutable dependencies from the accepted Gold manifest."""
    _require_exact_keys(value, _DEPENDENCY_KEYS, "W04 dependency identity")
    dependencies = value["dependencies"]
    if not isinstance(dependencies, list):
        raise FeatureRegistryError("W04 dependency envelope does not match accepted Gold lineage")
    if any(not isinstance(dependency, dict) for dependency in dependencies):
        raise FeatureRegistryError("W04 dependency entries must be objects")
    if tuple(dependencies) != _W04_DEPENDENCIES:
        raise FeatureRegistryError("W04 dependency envelope does not match accepted Gold lineage")
    for dependency in dependencies:
        _require_exact_keys(
            dependency,
            frozenset({"kind", "dependency_id", "digest", "observed_at", "available_at"}),
            "W04 dependency entry",
        )
        _require_sha256(dependency["digest"], "W04 dependency digest")
        if (
            _parse_instant(dependency["observed_at"], "W04 dependency observed_at") >= cutoff
            or _parse_instant(dependency["available_at"], "W04 dependency available_at") >= cutoff
        ):
            raise FeatureRegistryError("W04 dependencies must be strictly before feature_cutoff_ts")
    if value["lineage_hash"] != _W04_LINEAGE_HASH:
        raise FeatureRegistryError("W04 dependency lineage hash mismatch")
    lineage_payload = json.dumps(
        {
            "dependencies": dependencies,
            "source_completion_index_sha256": (
                "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
            ),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    if hashlib.sha256(lineage_payload).hexdigest() != _W04_LINEAGE_HASH:
        raise FeatureRegistryError(
            "W04 accepted dependency envelope does not reproduce lineage hash"
        )


def _mapping(value: object, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise FeatureRegistryError(f"{context} must be an object")
    return value


def load_synthetic_development_fixture(
    path: str | Path, registry: FeatureRegistry
) -> tuple[Mapping[str, Any], ...]:
    """Load and verify a fixed local synthetic fixture, then reproduce every expected value."""
    value = _load_exact_json(Path(path))
    _require_exact_keys(value, _FIXTURE_KEYS, "synthetic fixture")
    if canonical_digest(value, "fixture_digest") != value["fixture_digest"]:
        raise FeatureRegistryError("fixture_digest must equal the canonical fixture SHA-256")
    if (value["fixture_id"], value["fixture_version"], value["fixture_digest"]) != (
        _ACCEPTED_FIXTURE_ID,
        _ACCEPTED_FIXTURE_VERSION,
        _ACCEPTED_FIXTURE_DIGEST,
    ):
        raise FeatureRegistryError("fixture accepted-identity mismatch")
    family = registry.synthetic_family
    if (
        value["registry_id"] != registry.registry_id
        or value["registry_digest"] != registry.registry_digest
        or value["family_id"] != family.family_id
        or value["family_digest"] != family.family_digest
    ):
        raise FeatureRegistryError(
            "fixture registry or synthetic-family identity substitution is forbidden"
        )
    notice = _require_str(value["development_peer_group_notice"], "development_peer_group_notice")
    required_notice = (
        "development construction labels, not recruitment outcomes, external expert labels "
        "or W06 protected evidence"
    )
    if required_notice not in notice:
        raise FeatureRegistryError("fixture must preserve the development peer-group boundary")
    complete = value["complete_rows"]
    edge = value["edge_rows"]
    if (
        not isinstance(complete, list)
        or not isinstance(edge, list)
        or len(complete) < 18
        or len(edge) < 4
    ):
        raise FeatureRegistryError("fixture requires 18 complete rows and four state edge rows")
    if any(not isinstance(row, dict) for row in [*complete, *edge]):
        raise FeatureRegistryError("fixture rows must be objects")
    groups = {
        _require_str(row.get("constructed_development_peer_group"), "peer group")
        for row in complete
    }
    if len(groups) < 3:
        raise FeatureRegistryError(
            "fixture requires at least three constructed development peer groups"
        )
    materialized = []
    for row in [*complete, *edge]:
        result = materialize_synthetic_row(row, registry)
        expected = row["expected_feature_values"]
        if not isinstance(expected, list) or len(expected) != len(result.values):
            raise FeatureRegistryError("expected FeatureValues must have exact schema length")
        expected_values = tuple(_expected_feature_value(item) for item in expected)
        if result.values != expected_values:
            raise FeatureRegistryError(
                "fixture expected FeatureValues do not reproduce materialization"
            )
        materialized.append(row)
    edge_states = {item["state"] for row in edge for item in row["expected_feature_values"]}
    if not {"missing", "suppressed", "unavailable", "zero"}.issubset(edge_states):
        raise FeatureRegistryError(
            "fixture edge rows must preserve unavailable, suppressed, missing, and zero"
        )
    return tuple(materialized)


__all__ = [
    "FeatureDefinition",
    "FeatureFamily",
    "FeatureRegistry",
    "FeatureRegistryError",
    "FeatureSchema",
    "MaterializedFeatureRow",
    "canonical_digest",
    "canonical_json_bytes",
    "load_feature_registry",
    "load_synthetic_development_fixture",
    "materialize_synthetic_row",
    "materialize_w04_real_row",
]

"""Closed, progression-safe authority for the conservative W04 feature roster."""

from __future__ import annotations

import json
import math
import re
import runpy
import unicodedata
from collections.abc import Mapping
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import TypeGuard
from uuid import RFC_4122, UUID

import pytest
import yaml
from yaml.nodes import MappingNode
from yaml.tokens import AliasToken, AnchorToken, DirectiveToken, TagToken

ROOT = Path(__file__).resolve().parents[2]
AUTHORITIES = ROOT / "reports/reviews/W04/authorities"
DECISION_PATH = AUTHORITIES / "wyscout-supported-feature-registry-decisions-v1.json"
REGISTRY_PATH = ROOT / "configs/features/wyscout-v5-supported-count-features-v1.yaml"
REVIEW_PATH = AUTHORITIES / "wyscout-supported-feature-registry-independent-review-R1.md"
ACCEPTANCE_PATH = AUTHORITIES / "wyscout-supported-feature-registry-acceptance-v1.json"
FIELD_REGISTRY_PATH = ROOT / "configs/schema/wyscout-v5-field-registry-v2.yaml"
FIELD_ACCEPTANCE_PATH = AUTHORITIES / "wyscout-field-semantic-acceptance-v2.json"
POSSESSION_TAXONOMY_PATH = ROOT / "configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml"
POSSESSION_ACCEPTANCE_PATH = AUTHORITIES / "wyscout-possession-semantic-acceptance-v2.json"
POSSESSION_CONTRACT_PATH = ROOT / "tests/contracts/test_w04_possession_semantic_v2_authority.py"
PRODUCT_PREIMAGE_PATH = ROOT / "configs/schema/wyscout-v5-product-contract-preimage-v1.json"
SCHEMA_PREIMAGE_PATH = ROOT / "configs/schema/wyscout-v5-schema-bundle-preimage-v1.json"
CROSS_AUTHORITY_PATH = ROOT / "tests/contracts/test_w04_r21_cross_authority_composability.py"

SOURCE_ID = "wyscout-soccer-match-events-figshare-v5"
DECISION_ID = "w04-wyscout-supported-feature-registry-decisions-v1"
REGISTRY_ID = "w04-wyscout-supported-count-features-v1"
REVIEW_ID = "w04-wyscout-supported-feature-registry-independent-review-R1"
ACCEPTANCE_ID = "w04-wyscout-supported-feature-registry-acceptance-v1"
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
EXPECTED_DECISION_SHA256 = "bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941"
EXPECTED_REGISTRY_PHYSICAL_SHA256 = (
    "8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95"
)
EXPECTED_REGISTRY_CANONICAL_SHA256 = (
    "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"
)
TEST_REVIEWER_ACTOR_ID = "03a65770-02f6-5eb0-9bd2-e2ebb44b62bd"

EXPECTED_INPUTS = {
    "field_acceptance_sha256": ("beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436"),
    "field_registry_canonical_sha256": (
        "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959"
    ),
    "field_registry_id": "w04-wyscout-field-registry-v2",
    "possession_acceptance_sha256": (
        "2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1"
    ),
    "possession_taxonomy_canonical_sha256": (
        "3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881"
    ),
    "possession_taxonomy_id": "w04-wyscout-possession-taxonomy-v2",
    "product_contract_preimage_id": "w04-wyscout-product-contract-preimage-v1",
    "product_contract_preimage_sha256": (
        "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293"
    ),
    "schema_bundle_preimage_id": "w04-wyscout-schema-bundle-preimage-v1",
    "schema_bundle_preimage_sha256": (
        "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f"
    ),
}
EXPECTED_PREDECESSOR_PHYSICAL_SHA256 = {
    FIELD_ACCEPTANCE_PATH: EXPECTED_INPUTS["field_acceptance_sha256"],
    POSSESSION_ACCEPTANCE_PATH: EXPECTED_INPUTS["possession_acceptance_sha256"],
    PRODUCT_PREIMAGE_PATH: EXPECTED_INPUTS["product_contract_preimage_sha256"],
    SCHEMA_PREIMAGE_PATH: EXPECTED_INPUTS["schema_bundle_preimage_sha256"],
}
EXPECTED_POLICIES = {
    "absence_grants_permission": False,
    "continuous_time_features": "UNAVAILABLE",
    "minutes_features": "SUPPRESSED_UNSUPPORTED_DENOMINATOR",
    "outcome_dependent_features": "UNAVAILABLE",
    "per90_features": "SUPPRESSED_UNSUPPORTED_DENOMINATOR",
    "provider_native_possession_features": "UNAVAILABLE",
    "rate_features": "SUPPRESSED_UNSUPPORTED_DENOMINATOR",
    "role_inferred_features": "UNAVAILABLE",
    "unsupported_feature_policy": "UNAVAILABLE",
    "value_model_features": "UNAVAILABLE",
}
EXPECTED_FEATURES = [
    {
        "aggregation": "COUNT",
        "applicability": "ACTION_PRESENT",
        "denominator": "NONE",
        "feature_name": "action_count",
        "input_fields": ["action_source_id"],
        "output_type": "int64",
        "reason": "SUPPORTED_EXACT_SOURCE_ACTION_ID_COUNT",
        "state": "SUPPORTED",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "UNSUPPORTED_MINUTES",
        "feature_name": "action_rate",
        "input_fields": [],
        "output_type": None,
        "reason": "POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR",
        "state": "SUPPRESSED_UNSUPPORTED_DENOMINATOR",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "UNSUPPORTED_MINUTES",
        "feature_name": "actions_per_90",
        "input_fields": [],
        "output_type": None,
        "reason": "POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR",
        "state": "SUPPRESSED_UNSUPPORTED_DENOMINATOR",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "NONE",
        "feature_name": "continuous_time_seconds",
        "input_fields": [],
        "output_type": None,
        "reason": "POC_SOURCE_SUPPORTS_PERIOD_RELATIVE_TIME_ONLY",
        "state": "UNAVAILABLE",
    },
    {
        "aggregation": "COUNT",
        "applicability": "POSITION_PRESENT",
        "denominator": "NONE",
        "feature_name": "coordinate_known_action_count",
        "input_fields": ["action_positions"],
        "output_type": "int64",
        "reason": "SUPPORTED_ACCEPTED_POSITION_EVIDENCE_COUNT",
        "state": "SUPPORTED",
    },
    {
        "aggregation": "DISTINCT_COUNT",
        "applicability": "ALWAYS",
        "denominator": "NONE",
        "feature_name": "match_count",
        "input_fields": ["match_source_id"],
        "output_type": "int64",
        "reason": "SUPPORTED_DISTINCT_ACCEPTED_MATCH_ID_COUNT",
        "state": "SUPPORTED",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "UNSUPPORTED_MINUTES",
        "feature_name": "minutes_lower",
        "input_fields": [],
        "output_type": None,
        "reason": "POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR",
        "state": "SUPPRESSED_UNSUPPORTED_DENOMINATOR",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "UNSUPPORTED_MINUTES",
        "feature_name": "minutes_upper",
        "input_fields": [],
        "output_type": None,
        "reason": "POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR",
        "state": "SUPPRESSED_UNSUPPORTED_DENOMINATOR",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "NONE",
        "feature_name": "outcome_dependent_count",
        "input_fields": [],
        "output_type": None,
        "reason": "OUTCOMES_EXCLUDED_FROM_W04_RESULT_INDEPENDENT_POC",
        "state": "UNAVAILABLE",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "NONE",
        "feature_name": "provider_native_possession_count",
        "input_fields": [],
        "output_type": None,
        "reason": "PROVIDER_NATIVE_POSSESSION_NOT_PRESENT_OR_AUTHORIZED",
        "state": "UNAVAILABLE",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "NONE",
        "feature_name": "resolved_lineup_stint_count",
        "input_fields": [],
        "output_type": None,
        "reason": "LINEUP_STINT_COUNT_NOT_ACCEPTED_IN_CONSERVATIVE_POC_ROSTER",
        "state": "UNAVAILABLE",
    },
    {
        "aggregation": "COUNT",
        "applicability": "POSSESSION_ELIGIBLE",
        "denominator": "NONE",
        "feature_name": "resolved_possession_action_count",
        "input_fields": [
            "action_event_taxonomy_id",
            "action_subevent_taxonomy_id",
            "action_team_source_id",
        ],
        "output_type": "int64",
        "reason": "SUPPORTED_ACCEPTED_POSSESSION_ELIGIBLE_ACTION_COUNT",
        "state": "SUPPORTED",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "NONE",
        "feature_name": "role_inferred_count",
        "input_fields": [],
        "output_type": None,
        "reason": "ROLE_INFERENCE_OUTSIDE_W04_AUTHORITY",
        "state": "UNAVAILABLE",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "NONE",
        "feature_name": "unresolved_action_count",
        "input_fields": [],
        "output_type": None,
        "reason": "UNRESOLVED_ACTION_EVIDENCE_REMAINS_QUARANTINED_NOT_FEATURED",
        "state": "UNAVAILABLE",
    },
    {
        "aggregation": "NONE",
        "applicability": "NEVER",
        "denominator": "NONE",
        "feature_name": "value_model_sum",
        "input_fields": [],
        "output_type": None,
        "reason": "NO_ACCEPTED_ACTION_VALUE_MODEL_IN_W04",
        "state": "UNAVAILABLE",
    },
]
SUPPORTED_FEATURES = {
    "action_count",
    "coordinate_known_action_count",
    "match_count",
    "resolved_possession_action_count",
}
DECISION_KEYS = {
    "authority_class",
    "bound_inputs",
    "decided_at",
    "decided_by",
    "decision_id",
    "decision_schema_version",
    "features",
    "policies",
}
REGISTRY_KEYS = {
    "bound_inputs",
    "decision_id",
    "decision_sha256",
    "features",
    "policies",
    "registry_id",
    "registry_schema_version",
}
ROW_KEYS = {
    "aggregation",
    "applicability",
    "denominator",
    "feature_name",
    "input_fields",
    "output_type",
    "reason",
    "state",
}
REVIEW_KEYS = {
    "candidate_id",
    "candidate_physical_sha256",
    "candidate_sha256",
    "decision_id",
    "decision_physical_sha256",
    "decision_sha256",
    "findings",
    "recommendation",
    "review_id",
    "review_schema_version",
    "reviewed_at",
    "reviewed_by",
}
FINDING_KEYS = {"code", "severity", "summary"}
ACCEPTANCE_KEYS = {
    "acceptance_id",
    "acceptance_schema_version",
    "accepted_at",
    "accepted_by",
    "candidate_id",
    "candidate_physical_sha256",
    "candidate_sha256",
    "decision_id",
    "decision_physical_sha256",
    "decision_sha256",
    "review_id",
    "review_physical_sha256",
    "review_record_sha256",
    "review_recommendation",
    "supersedes_acceptance_id",
}
AGGREGATIONS = {"COUNT", "SUM", "MIN", "MAX", "DISTINCT_COUNT", "NONE"}
APPLICABILITIES = {
    "ALWAYS",
    "ACTION_PRESENT",
    "POSITION_PRESENT",
    "POSSESSION_ELIGIBLE",
    "NEVER",
}
DENOMINATORS = {
    "NONE",
    "ACTION_COUNT",
    "APPLICABLE_ACTION_COUNT",
    "RESOLVED_POSSESSION_COUNT",
    "UNSUPPORTED_MINUTES",
}
OUTPUT_TYPES = {"int64", "decimal128(22,18)", "boolean", None}
STATES = {"SUPPORTED", "SUPPRESSED_UNSUPPORTED_DENOMINATOR", "UNAVAILABLE"}
UTC_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{6})?Z\Z"
)
FEATURE_RE = re.compile(r"[a-z][a-z0-9_]{0,127}\Z")
FIELD_RE = re.compile(r"[a-z][a-z0-9_]{0,127}\Z")
FINDING_CODE_RE = re.compile(r"[A-Z][A-Z0-9_]{1,63}\Z")
PRODUCT_PATHS = (
    ROOT / "data/working/wyscout/v5/.staging",
    ROOT / "data/working/wyscout/v5/identity",
    ROOT / "data/working/wyscout/v5/bronze",
    ROOT / "data/working/wyscout/v5/silver",
    ROOT / "data/working/wyscout/v5/gold",
    ROOT / "data/manifests/wyscout/v5/code",
    ROOT / "data/manifests/wyscout/v5/bronze",
    ROOT / "data/manifests/wyscout/v5/silver",
    ROOT / "data/manifests/wyscout/v5/gold",
    ROOT / "scripts/admit_wyscout_v5_runtime.py",
    ROOT / "scripts/rebuild_wyscout_v5.py",
    ROOT / "scripts/launch_wyscout_v5.py",
    ROOT / "src/scouting/data_products/wyscout",
)


class _UniqueSafeLoader(yaml.SafeLoader):
    """Safe loader that rejects duplicate or non-string mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueSafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key == "<<" or key in result:
            raise ValueError("invalid or duplicate YAML key")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class _NoAliasSafeDumper(yaml.SafeDumper):
    """Deterministic safe dumper that never emits YAML aliases."""

    def ignore_aliases(self, data: object) -> bool:
        return True


def _assert_nfc_tree(value: object) -> None:
    if value is None or type(value) in {bool, int}:  # noqa: E721
        return
    if isinstance(value, float):
        raise ValueError("floats are forbidden")
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non-NFC string")
        value.encode("utf-8")
        return
    if isinstance(value, list):
        for item in value:
            _assert_nfc_tree(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("mapping keys must be strings")
            _assert_nfc_tree(key)
            _assert_nfc_tree(item)
        return
    raise ValueError(f"unsupported scalar type: {type(value).__name__}")


def _canonical_json_bytes(value: object) -> bytes:
    _assert_nfc_tree(value)
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode()


def _duplicate_rejecting_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_canonical_json(raw: bytes) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("JSON BOM is forbidden")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_duplicate_rejecting_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("invalid strict JSON") from exc
    if not isinstance(value, dict) or raw != _canonical_json_bytes(value):
        raise ValueError("noncanonical JSON")
    return value


def _canonical_yaml_bytes(value: object) -> bytes:
    _assert_nfc_tree(value)
    return yaml.dump(
        value,
        Dumper=_NoAliasSafeDumper,
        allow_unicode=True,
        default_flow_style=False,
        explicit_end=False,
        explicit_start=False,
        sort_keys=False,
        width=4096,
    ).encode()


def _walk(value: object) -> list[object]:
    values = [value]
    if isinstance(value, dict):
        for key, item in value.items():
            values.extend(_walk(key))
            values.extend(_walk(item))
    elif isinstance(value, list):
        for item in value:
            values.extend(_walk(item))
    return values


def _load_strict_yaml(raw: bytes, *, require_canonical: bool = True) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("YAML BOM is forbidden")
    try:
        text = raw.decode("utf-8")
        tokens = list(yaml.scan(text))
        documents = list(yaml.load_all(text, Loader=_UniqueSafeLoader))
    except (UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        raise ValueError("invalid strict YAML") from exc
    if any(
        isinstance(token, (AliasToken, AnchorToken, DirectiveToken, TagToken)) for token in tokens
    ):
        raise ValueError("unsafe YAML token")
    if len(documents) != 1 or not isinstance(documents[0], dict):
        raise ValueError("registry must be one mapping")
    value = documents[0]
    _assert_nfc_tree(value)
    if any(isinstance(item, (float, date, datetime)) for item in _walk(value)):
        raise ValueError("unsafe YAML scalar")
    if require_canonical and raw != _canonical_yaml_bytes(value):
        raise ValueError("noncanonical YAML")
    return value


def _require_exact_keys(
    value: object,
    expected: set[str],
    context: str,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{context} keys differ")
    return value


def _parse_canonical_utc(value: object) -> datetime:
    if not isinstance(value, str) or UTC_RE.fullmatch(value) is None:
        raise ValueError("invalid UTC instant")
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise ValueError("invalid UTC instant") from exc
    if parsed.tzinfo != UTC:
        raise ValueError("UTC instant required")
    return parsed


def _validate_actor(value: object, context: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{context} actor must be a string")
    try:
        actor = UUID(value)
    except ValueError as exc:
        raise ValueError(f"{context} actor must be UUID") from exc
    if value != str(actor) or actor.version != 5 or actor.variant != RFC_4122:
        raise ValueError(f"invalid {context} actor")
    return value


def _accepted_field_outputs() -> set[str]:
    registry = _load_strict_yaml(FIELD_REGISTRY_PATH.read_bytes())
    fields = registry.get("fields")
    if not isinstance(fields, list):
        raise ValueError("field registry fields missing")
    return {
        value
        for row in fields
        if isinstance(row, dict)
        and row.get("decision") == "TRANSFORM"
        and isinstance((value := row.get("canonical_field")), str)
    }


def _validate_predecessors() -> None:
    for path, expected in EXPECTED_PREDECESSOR_PHYSICAL_SHA256.items():
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"predecessor digest differs: {path}")
    field_registry = _load_strict_yaml(FIELD_REGISTRY_PATH.read_bytes())
    possession_taxonomy = _load_strict_yaml(POSSESSION_TAXONOMY_PATH.read_bytes())
    if (
        field_registry.get("registry_id") != EXPECTED_INPUTS["field_registry_id"]
        or sha256(_canonical_json_bytes(field_registry)).hexdigest()
        != EXPECTED_INPUTS["field_registry_canonical_sha256"]
        or possession_taxonomy.get("taxonomy_id") != EXPECTED_INPUTS["possession_taxonomy_id"]
        or sha256(_canonical_json_bytes(possession_taxonomy)).hexdigest()
        != EXPECTED_INPUTS["possession_taxonomy_canonical_sha256"]
    ):
        raise ValueError("accepted semantic candidate differs")
    field_acceptance = _load_canonical_json(FIELD_ACCEPTANCE_PATH.read_bytes())
    possession_acceptance = _load_canonical_json(POSSESSION_ACCEPTANCE_PATH.read_bytes())
    if (
        field_acceptance.get("candidate_sha256")
        != EXPECTED_INPUTS["field_registry_canonical_sha256"]
        or possession_acceptance.get("candidate_sha256")
        != EXPECTED_INPUTS["possession_taxonomy_canonical_sha256"]
        or possession_acceptance.get("accepted_at") != "2026-07-31T08:28:40Z"
    ):
        raise ValueError("accepted semantic authority differs")


def _validate_feature_rows(features: object) -> list[dict[str, object]]:
    if not isinstance(features, list) or len(features) != 15:
        raise ValueError("feature roster cardinality differs")
    rows: list[dict[str, object]] = []
    names: list[str] = []
    field_outputs = _accepted_field_outputs()
    for value in features:
        row = _require_exact_keys(value, ROW_KEYS, "feature row")
        name = row["feature_name"]
        inputs = row["input_fields"]
        reason = row["reason"]
        if (
            not isinstance(name, str)
            or FEATURE_RE.fullmatch(name) is None
            or not isinstance(inputs, list)
            or any(not isinstance(item, str) or FIELD_RE.fullmatch(item) is None for item in inputs)
            or inputs != sorted(set(inputs))
            or not isinstance(reason, str)
            or not 1 <= len(reason) <= 2000
            or row["aggregation"] not in AGGREGATIONS
            or row["applicability"] not in APPLICABILITIES
            or row["denominator"] not in DENOMINATORS
            or row["output_type"] not in OUTPUT_TYPES
            or row["state"] not in STATES
        ):
            raise ValueError("feature row value differs")
        state = row["state"]
        if state == "SUPPORTED":
            if (
                not inputs
                or row["aggregation"] == "NONE"
                or row["applicability"] == "NEVER"
                or row["denominator"] == "UNSUPPORTED_MINUTES"
                or row["output_type"] is None
                or any(item not in field_outputs for item in inputs)
            ):
                raise ValueError("supported row union differs")
        elif state == "SUPPRESSED_UNSUPPORTED_DENOMINATOR":
            if (
                inputs
                or row["aggregation"] != "NONE"
                or row["applicability"] != "NEVER"
                or row["denominator"] != "UNSUPPORTED_MINUTES"
                or row["output_type"] is not None
            ):
                raise ValueError("suppressed row union differs")
        elif (
            inputs
            or row["aggregation"] != "NONE"
            or row["applicability"] != "NEVER"
            or row["output_type"] is not None
        ):
            raise ValueError("unavailable row union differs")
        rows.append(row)
        names.append(name)
    if names != sorted(names) or len(names) != len(set(names)):
        raise ValueError("feature names must be sorted and unique")
    if rows != EXPECTED_FEATURES:
        raise ValueError("R21 feature roster differs")
    if {row["feature_name"] for row in rows if row["state"] == "SUPPORTED"} != SUPPORTED_FEATURES:
        raise ValueError("supported feature set differs")
    resolved = next(
        row for row in rows if row["feature_name"] == "resolved_possession_action_count"
    )
    if (
        resolved["input_fields"]
        != [
            "action_event_taxonomy_id",
            "action_subevent_taxonomy_id",
            "action_team_source_id",
        ]
        or resolved["applicability"] != "POSSESSION_ELIGIBLE"
        or "possession_eligibility_state" in resolved["input_fields"]
    ):
        raise ValueError("possession applicability contract differs")
    return rows


def _validate_decision(
    decision: dict[str, object],
    *,
    now: datetime | None = None,
) -> None:
    _require_exact_keys(decision, DECISION_KEYS, "decision")
    if (
        decision["authority_class"] != "SUPPORTED_FEATURE"
        or decision["bound_inputs"] != EXPECTED_INPUTS
        or decision["decision_id"] != DECISION_ID
        or decision["decision_schema_version"] != "w04-supported-feature-decision-v1"
        or decision["policies"] != EXPECTED_POLICIES
        or _validate_actor(decision["decided_by"], "decision") != MASTER_ACTOR_ID
    ):
        raise ValueError("decision authority differs")
    decided_at = _parse_canonical_utc(decision["decided_at"])
    if decided_at <= datetime(2026, 7, 31, 8, 28, 40, tzinfo=UTC):
        raise ValueError("decision does not follow accepted predecessors")
    current_time = datetime.now(UTC) if now is None else now
    if decided_at > current_time + timedelta(minutes=5):
        raise ValueError("future decision clock")
    _validate_feature_rows(decision["features"])


def _validate_registry(
    registry: dict[str, object],
    decision: dict[str, object],
    decision_raw: bytes,
) -> None:
    _require_exact_keys(registry, REGISTRY_KEYS, "registry")
    if (
        registry["bound_inputs"] != EXPECTED_INPUTS
        or registry["decision_id"] != DECISION_ID
        or registry["decision_sha256"] != sha256(decision_raw).hexdigest()
        or registry["decision_sha256"] != EXPECTED_DECISION_SHA256
        or registry["features"] != decision["features"]
        or registry["policies"] != EXPECTED_POLICIES
        or registry["registry_id"] != REGISTRY_ID
        or registry["registry_schema_version"] != "w04-supported-feature-registry-v1"
    ):
        raise ValueError("registry does not restate decision")
    _validate_feature_rows(registry["features"])


def _load_candidates() -> tuple[
    dict[str, object],
    bytes,
    dict[str, object],
    bytes,
]:
    decision_raw = DECISION_PATH.read_bytes()
    registry_raw = REGISTRY_PATH.read_bytes()
    decision = _load_canonical_json(decision_raw)
    registry = _load_strict_yaml(registry_raw)
    return decision, decision_raw, registry, registry_raw


def _candidate_digests(
    decision_raw: bytes,
    registry: dict[str, object],
    registry_raw: bytes,
) -> dict[str, str]:
    decision_digest = sha256(decision_raw).hexdigest()
    return {
        "candidate_physical_sha256": sha256(registry_raw).hexdigest(),
        "candidate_sha256": sha256(_canonical_json_bytes(registry)).hexdigest(),
        "decision_physical_sha256": decision_digest,
        "decision_sha256": decision_digest,
    }


def _load_review_markdown(raw: bytes) -> tuple[dict[str, object], bytes]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("review BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("review must be UTF-8") from exc
    if "\r" in text:
        raise ValueError("review must use LF")
    lines = text.splitlines(keepends=True)
    fences = [
        index
        for index, line in enumerate(lines)
        if re.match(r" {0,3}(?:`{3,}|~{3,})", line) is not None
    ]
    if len(fences) != 2:
        raise ValueError("review requires one fence")
    opening, closing = fences
    if (
        lines[opening] != "```w04-authority-review-v1\n"
        or lines[closing] not in {"```\n", "```"}
        or closing <= opening
    ):
        raise ValueError("invalid review fence")
    record_raw = "".join(lines[opening + 1 : closing]).encode()
    return _load_canonical_json(record_raw), record_raw


def _validate_review(
    raw: bytes,
    decision: dict[str, object],
    decision_raw: bytes,
    registry: dict[str, object],
    registry_raw: bytes,
    *,
    now: datetime,
) -> tuple[dict[str, object], bytes]:
    review, record_raw = _load_review_markdown(raw)
    _require_exact_keys(review, REVIEW_KEYS, "review")
    expected_digests = _candidate_digests(decision_raw, registry, registry_raw)
    if (
        review["candidate_id"] != REGISTRY_ID
        or review["decision_id"] != DECISION_ID
        or review["review_id"] != REVIEW_ID
        or review["review_schema_version"] != "w04-authority-independent-review-v1"
        or any(review[key] != digest for key, digest in expected_digests.items())
    ):
        raise ValueError("review authority differs")
    reviewer = _validate_actor(review["reviewed_by"], "review")
    if reviewer == decision["decided_by"]:
        raise ValueError("self-review is forbidden")
    reviewed_at = _parse_canonical_utc(review["reviewed_at"])
    if (
        not _parse_canonical_utc(decision["decided_at"])
        <= reviewed_at
        <= now + timedelta(minutes=5)
    ):
        raise ValueError("invalid review clock")
    findings = review["findings"]
    if not isinstance(findings, list):
        raise ValueError("findings must be an array")
    for value in findings:
        finding = _require_exact_keys(value, FINDING_KEYS, "finding")
        if (
            not isinstance(finding["code"], str)
            or FINDING_CODE_RE.fullmatch(finding["code"]) is None
            or finding["severity"] not in {"P0", "P1", "P2"}
            or not isinstance(finding["summary"], str)
            or not 1 <= len(finding["summary"]) <= 2000
        ):
            raise ValueError("invalid finding")
    recommendation = review["recommendation"]
    if (
        recommendation not in {"PASS", "REWORK"}
        or (recommendation == "PASS" and findings)
        or (recommendation == "REWORK" and not findings)
    ):
        raise ValueError("review recommendation differs from findings")
    return review, record_raw


def _validate_acceptance(
    raw: bytes,
    review: dict[str, object],
    review_raw: bytes,
    review_record_raw: bytes,
    decision: dict[str, object],
    decision_raw: bytes,
    registry: dict[str, object],
    registry_raw: bytes,
    *,
    now: datetime,
) -> None:
    acceptance = _load_canonical_json(raw)
    _require_exact_keys(acceptance, ACCEPTANCE_KEYS, "acceptance")
    expected_digests = _candidate_digests(decision_raw, registry, registry_raw)
    if (
        acceptance["acceptance_id"] != ACCEPTANCE_ID
        or acceptance["acceptance_schema_version"] != "w04-authority-acceptance-v1"
        or acceptance["candidate_id"] != REGISTRY_ID
        or acceptance["decision_id"] != DECISION_ID
        or acceptance["review_id"] != REVIEW_ID
        or any(acceptance[key] != digest for key, digest in expected_digests.items())
        or acceptance["review_record_sha256"] != sha256(review_record_raw).hexdigest()
        or acceptance["review_physical_sha256"] != sha256(review_raw).hexdigest()
        or acceptance["review_recommendation"] != "PASS"
        or acceptance["supersedes_acceptance_id"] is not None
        or review["recommendation"] != "PASS"
        or review["findings"]
    ):
        raise ValueError("acceptance authority differs")
    if _validate_actor(acceptance["accepted_by"], "acceptance") != MASTER_ACTOR_ID:
        raise ValueError("acceptance actor differs")
    accepted_at = _parse_canonical_utc(acceptance["accepted_at"])
    if not (
        _parse_canonical_utc(decision["decided_at"])
        <= _parse_canonical_utc(review["reviewed_at"])
        <= accepted_at
        <= now + timedelta(minutes=5)
    ):
        raise ValueError("invalid acceptance clock")
    if acceptance["accepted_by"] == review["reviewed_by"]:
        raise ValueError("reviewer cannot accept")


def _validate_authority_state(
    review_raw: bytes | None,
    acceptance_raw: bytes | None,
    *,
    later_authority_present: bool,
    product_path_present: bool,
    now: datetime,
) -> str:
    decision, decision_raw, registry, registry_raw = _load_candidates()
    _validate_decision(decision, now=now)
    _validate_registry(registry, decision, decision_raw)
    if review_raw is None:
        if acceptance_raw is not None or later_authority_present or product_path_present:
            raise ValueError("progression before review")
        return "DECISION_ONLY"
    review, record_raw = _validate_review(
        review_raw,
        decision,
        decision_raw,
        registry,
        registry_raw,
        now=now,
    )
    if acceptance_raw is None:
        if later_authority_present or product_path_present:
            raise ValueError("progression before acceptance")
        return f"REVIEW_{review['recommendation']}"
    _validate_acceptance(
        acceptance_raw,
        review,
        review_raw,
        record_raw,
        decision,
        decision_raw,
        registry,
        registry_raw,
        now=now,
    )
    return "ACCEPTED"


def _feature_schema_hash(state: str, registry: dict[str, object]) -> str:
    if state != "ACCEPTED":
        raise ValueError("feature_schema_hash unavailable before acceptance")
    return sha256(_canonical_json_bytes(registry)).hexdigest()


def _valid_review_record(*, recommendation: str = "PASS") -> dict[str, object]:
    _, decision_raw, registry, registry_raw = _load_candidates()
    findings: list[dict[str, str]] = []
    if recommendation == "REWORK":
        findings = [
            {
                "code": "TEST_REWORK",
                "severity": "P2",
                "summary": "Synthetic bounded progression challenge.",
            }
        ]
    return {
        "candidate_id": REGISTRY_ID,
        **_candidate_digests(decision_raw, registry, registry_raw),
        "decision_id": DECISION_ID,
        "findings": findings,
        "recommendation": recommendation,
        "review_id": REVIEW_ID,
        "review_schema_version": "w04-authority-independent-review-v1",
        "reviewed_at": "2026-07-31T08:38:00Z",
        "reviewed_by": TEST_REVIEWER_ACTOR_ID,
    }


def _review_markdown(record: dict[str, object]) -> bytes:
    return (
        b"# Synthetic review\n\n```w04-authority-review-v1\n"
        + _canonical_json_bytes(record)
        + b"```\n"
    )


def _valid_acceptance_record(
    review_raw: bytes,
    review_record_raw: bytes,
) -> dict[str, object]:
    _, decision_raw, registry, registry_raw = _load_candidates()
    return {
        "acceptance_id": ACCEPTANCE_ID,
        "acceptance_schema_version": "w04-authority-acceptance-v1",
        "accepted_at": "2026-07-31T08:39:00Z",
        "accepted_by": MASTER_ACTOR_ID,
        "candidate_id": REGISTRY_ID,
        **_candidate_digests(decision_raw, registry, registry_raw),
        "decision_id": DECISION_ID,
        "review_id": REVIEW_ID,
        "review_physical_sha256": sha256(review_raw).hexdigest(),
        "review_record_sha256": sha256(review_record_raw).hexdigest(),
        "review_recommendation": "PASS",
        "supersedes_acceptance_id": None,
    }


def _is_strict_integer(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool) and type(value) is int


def _is_strict_positive_integer(value: object) -> bool:
    return _is_strict_integer(value) and value > 0


def _is_finite_position_scalar(value: object) -> TypeGuard[int | float | Decimal]:
    if isinstance(value, bool):
        return False
    if type(value) is int:
        return True
    if type(value) is float:
        return math.isfinite(value)
    if isinstance(value, Decimal):
        return value.is_finite()
    return False


def _has_accepted_positions(value: object) -> bool:
    if not isinstance(value, list) or len(value) not in {1, 2}:
        return False
    for position in value:
        if not isinstance(position, Mapping) or set(position) != {"x", "y"}:
            return False
        for axis in ("x", "y"):
            scalar = position[axis]
            if not _is_finite_position_scalar(scalar) or not 0 <= scalar <= 100:
                return False
    return True


def _predicate_is_potentially_resolution_capable(predicate: dict[str, object]) -> bool:
    decision = predicate.get("decision")
    if decision in {"CONTROL", "RESTART"}:
        return (
            predicate.get("opens_control") is True
            and predicate.get("control_team_source") == "ACTION_TEAM"
        )
    if decision == "DEAD_BALL":
        return predicate.get("dead_ball_attachment") == "PRECEDING_RESOLVED_POSSESSION"
    if decision == "CONTESTED":
        return predicate.get("contested_attachment") in {
            "PRECEDING_RESOLVED_POSSESSION",
            "BUFFER_UNTIL_FOLLOWING_RESOLVED_POSSESSION",
        }
    return False


def _accepted_possession_capability_pair_sets() -> tuple[
    frozenset[tuple[int, int]],
    frozenset[tuple[int, int]],
]:
    _validate_predecessors()
    taxonomy = _load_strict_yaml(POSSESSION_TAXONOMY_PATH.read_bytes())
    predicates = taxonomy.get("predicates")
    if not isinstance(predicates, list) or len(predicates) != 36:
        raise ValueError("accepted possession predicate cardinality differs")
    pair_counts: dict[tuple[int, int], int] = {}
    pair_predicates: dict[tuple[int, int], dict[str, object]] = {}
    for value in predicates:
        if not isinstance(value, dict):
            raise ValueError("accepted possession predicate must be a mapping")
        event_id = value.get("event_id")
        subevent_id = value.get("subevent_id")
        decision = value.get("decision")
        if (
            not _is_strict_integer(event_id)
            or not _is_strict_integer(subevent_id)
            or not isinstance(decision, str)
        ):
            raise ValueError("accepted possession predicate selector differs")
        pair = (event_id, subevent_id)
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        pair_predicates[pair] = value
    unique_pairs = {pair for pair, count in pair_counts.items() if count == 1}
    potentially_capable = frozenset(
        pair
        for pair in unique_pairs
        if _predicate_is_potentially_resolution_capable(pair_predicates[pair])
    )
    structurally_ineligible = frozenset(
        pair for pair in unique_pairs if pair not in potentially_capable
    )
    if (
        len(unique_pairs) != 36
        or len(potentially_capable) != 28
        or len(structurally_ineligible) != 8
        or potentially_capable & structurally_ineligible
    ):
        raise ValueError("accepted possession predicate capability split differs")
    return potentially_capable, structurally_ineligible


def _is_feature_applicable(row: dict[str, object], context: dict[str, object]) -> bool:
    inputs = row["input_fields"]
    if not isinstance(inputs, list) or any(name not in context for name in inputs):
        return False
    applicability = row["applicability"]
    if applicability == "ALWAYS":
        return _is_strict_positive_integer(context.get("match_source_id"))
    if applicability == "ACTION_PRESENT":
        return _is_strict_positive_integer(context.get("action_source_id"))
    if applicability == "POSITION_PRESENT":
        return _has_accepted_positions(context.get("action_positions"))
    if applicability == "POSSESSION_ELIGIBLE":
        event_id = context.get("action_event_taxonomy_id")
        subevent_id = context.get("action_subevent_taxonomy_id")
        if (
            context.get("possession_eligibility_state") != "ELIGIBLE_RESOLVED"
            or not _is_strict_integer(event_id)
            or not _is_strict_integer(subevent_id)
            or not _is_strict_positive_integer(context.get("action_team_source_id"))
        ):
            return False
        potentially_capable, _ = _accepted_possession_capability_pair_sets()
        return (event_id, subevent_id) in potentially_capable
    return False


def test_exact_canonical_decision_registry_and_predecessors() -> None:
    _validate_predecessors()
    decision, decision_raw, registry, registry_raw = _load_candidates()
    _validate_decision(decision)
    _validate_registry(registry, decision, decision_raw)
    assert sha256(decision_raw).hexdigest() == EXPECTED_DECISION_SHA256
    assert sha256(registry_raw).hexdigest() == EXPECTED_REGISTRY_PHYSICAL_SHA256
    assert sha256(_canonical_json_bytes(registry)).hexdigest() == EXPECTED_REGISTRY_CANONICAL_SHA256
    assert registry_raw == _canonical_yaml_bytes(registry)
    assert decision_raw == _canonical_json_bytes(decision)


def test_exact_r21_roster_state_split_and_input_authority() -> None:
    decision = _load_candidates()[0]
    rows = _validate_feature_rows(decision["features"])
    assert [row["feature_name"] for row in rows] == [
        row["feature_name"] for row in EXPECTED_FEATURES
    ]
    assert sum(row["state"] == "SUPPORTED" for row in rows) == 4
    assert sum(row["state"] == "SUPPRESSED_UNSUPPORTED_DENOMINATOR" for row in rows) == 4
    assert sum(row["state"] == "UNAVAILABLE" for row in rows) == 7


@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "duplicate",
        "sixteenth",
        "unknown-row-field",
        "wrong-sort",
        "wrong-state",
        "wrong-output",
        "wrong-aggregation",
        "wrong-denominator",
        "wrong-applicability",
        "unsupported-input",
        "unsupported-output",
        "supported-empty-input",
        "supported-unaccepted-input",
        "name-only-input",
        "possession-internal-input",
        "fifth-supported",
    ),
)
def test_roster_and_closed_row_mutations_reject(mutation: str) -> None:
    features = deepcopy(EXPECTED_FEATURES)
    if mutation == "missing":
        features.pop()
    elif mutation == "duplicate":
        features[-1] = deepcopy(features[0])
    elif mutation == "sixteenth":
        extra = deepcopy(features[-1])
        extra["feature_name"] = "zz_extra"
        features.append(extra)
    elif mutation == "unknown-row-field":
        features[0]["extra"] = True
    elif mutation == "wrong-sort":
        features[0], features[1] = features[1], features[0]
    elif mutation == "wrong-state":
        features[0]["state"] = "UNAVAILABLE"
    elif mutation == "wrong-output":
        features[0]["output_type"] = "boolean"
    elif mutation == "wrong-aggregation":
        features[0]["aggregation"] = "SUM"
    elif mutation == "wrong-denominator":
        features[0]["denominator"] = "ACTION_COUNT"
    elif mutation == "wrong-applicability":
        features[0]["applicability"] = "ALWAYS"
    elif mutation == "unsupported-input":
        features[1]["input_fields"] = ["action_source_id"]
    elif mutation == "unsupported-output":
        features[1]["output_type"] = "int64"
    elif mutation == "supported-empty-input":
        features[0]["input_fields"] = []
    elif mutation == "supported-unaccepted-input":
        features[0]["input_fields"] = ["unknown_canonical_field"]
    elif mutation == "name-only-input":
        features[0]["input_fields"] = ["action_event_name"]
    elif mutation == "possession-internal-input":
        features[11]["input_fields"] = ["possession_eligibility_state"]
    else:
        features[10] = {
            "aggregation": "COUNT",
            "applicability": "ACTION_PRESENT",
            "denominator": "NONE",
            "feature_name": "resolved_lineup_stint_count",
            "input_fields": ["action_source_id"],
            "output_type": "int64",
            "reason": "LINEUP_STINT_COUNT_NOT_ACCEPTED_IN_CONSERVATIVE_POC_ROSTER",
            "state": "SUPPORTED",
        }
    with pytest.raises(ValueError):
        _validate_feature_rows(features)


@pytest.mark.parametrize(
    "mutation",
    (
        "field-v1",
        "possession-v1",
        "field-physical",
        "possession-physical",
        "product-swap",
        "schema-swap",
        "bare-product",
        "unknown-input",
        "policy",
    ),
)
def test_binding_preimage_and_policy_mutations_reject(mutation: str) -> None:
    decision = deepcopy(_load_candidates()[0])
    inputs = decision["bound_inputs"]
    if mutation == "field-v1":
        inputs["field_registry_id"] = "w04-wyscout-field-registry-v1"
    elif mutation == "possession-v1":
        inputs["possession_taxonomy_id"] = "w04-wyscout-possession-taxonomy-v1"
    elif mutation == "field-physical":
        inputs["field_registry_canonical_sha256"] = sha256(
            FIELD_REGISTRY_PATH.read_bytes()
        ).hexdigest()
    elif mutation == "possession-physical":
        inputs["possession_taxonomy_canonical_sha256"] = sha256(
            POSSESSION_TAXONOMY_PATH.read_bytes()
        ).hexdigest()
    elif mutation == "product-swap":
        inputs["product_contract_preimage_sha256"] = EXPECTED_INPUTS[
            "schema_bundle_preimage_sha256"
        ]
    elif mutation == "schema-swap":
        inputs["schema_bundle_preimage_sha256"] = EXPECTED_INPUTS[
            "product_contract_preimage_sha256"
        ]
    elif mutation == "bare-product":
        inputs["product_contract_digest"] = inputs.pop("product_contract_preimage_sha256")
    elif mutation == "unknown-input":
        inputs["extra"] = "0" * 64
    else:
        decision["policies"]["absence_grants_permission"] = True
    with pytest.raises(ValueError):
        _validate_decision(decision)


@pytest.mark.parametrize(
    "raw",
    (
        b"{}\n\n",
        b'{"authority_class": "SUPPORTED_FEATURE"}\n',
        b"\xef\xbb\xbf{}\n",
        b'{"a":1,"a":1}\n',
    ),
)
def test_noncanonical_json_rejects(raw: bytes) -> None:
    with pytest.raises(ValueError):
        _load_canonical_json(raw)


@pytest.mark.parametrize(
    "raw",
    (
        b"---\n{}\n",
        b"a: &x 1\nb: *x\n",
        b"a: !!str 1\n",
        b"a: 1\na: 2\n",
        b"1: value\n",
        b"a: 1.5\n",
        b"a: 2026-07-31\n",
        b"---\na: 1\n---\nb: 2\n",
    ),
)
def test_noncanonical_or_unsafe_yaml_rejects(raw: bytes) -> None:
    with pytest.raises(ValueError):
        _load_strict_yaml(raw)


def test_candidate_digest_link_and_feature_hash_progression() -> None:
    decision, decision_raw, registry, registry_raw = _load_candidates()
    digests = _candidate_digests(decision_raw, registry, registry_raw)
    assert registry["decision_sha256"] == digests["decision_sha256"]
    with pytest.raises(ValueError):
        _feature_schema_hash("DECISION_ONLY", registry)
    assert "feature_schema_hash" not in decision
    assert "feature_schema_hash" not in registry
    schema_preimage = _load_canonical_json(SCHEMA_PREIMAGE_PATH.read_bytes())
    assert schema_preimage["feature_schema_hash_placeholder"] == {
        "concrete_value": None,
        "json_type": "string",
        "pattern": "^[0-9a-f]{64}$",
        "resolution_source": ("accepted:w04-wyscout-supported-count-features-v1:candidate_sha256"),
        "state": "TYPED_UNRESOLVED_UNTIL_SUPPORTED_FEATURE_ACCEPTANCE",
    }


@pytest.mark.parametrize(
    ("row_index", "source_id_field"),
    ((0, "action_source_id"), (5, "match_source_id")),
)
@pytest.mark.parametrize("source_id", (1, 42))
def test_source_id_count_features_accept_only_positive_integer_evidence(
    row_index: int,
    source_id_field: str,
    source_id: int,
) -> None:
    assert _is_feature_applicable(
        EXPECTED_FEATURES[row_index],
        {source_id_field: source_id},
    )


@pytest.mark.parametrize(
    ("row_index", "source_id_field"),
    ((0, "action_source_id"), (5, "match_source_id")),
)
@pytest.mark.parametrize(
    "invalid_source_id",
    (None, True, False, "1", 1.0, Decimal("1"), 0, -1),
)
def test_source_id_count_features_reject_missing_or_mistyped_evidence(
    row_index: int,
    source_id_field: str,
    invalid_source_id: object,
) -> None:
    row = EXPECTED_FEATURES[row_index]
    assert not _is_feature_applicable(row, {})
    assert not _is_feature_applicable(row, {source_id_field: invalid_source_id})


@pytest.mark.parametrize(
    "positions",
    (
        [{"x": 0, "y": 100}],
        [{"x": 12.5, "y": 87.5}],
        [{"x": Decimal("0.1"), "y": Decimal("99.9")}],
        [{"x": 1, "y": 2}, {"x": 99, "y": 98}],
    ),
)
def test_coordinate_feature_accepts_one_or_two_exact_bounded_positions(
    positions: list[dict[str, object]],
) -> None:
    assert _is_feature_applicable(
        EXPECTED_FEATURES[4],
        {"action_positions": positions},
    )


@pytest.mark.parametrize(
    "invalid_positions",
    (
        None,
        [],
        [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}],
        [None],
        [[1, 2]],
        [{"x": 1}],
        [{"y": 2}],
        [{"x": 1, "y": 2, "z": 3}],
        [{"x": None, "y": 2}],
        [{"x": "1", "y": 2}],
        [{"x": True, "y": 2}],
        [{"x": Decimal("NaN"), "y": 2}],
        [{"x": Decimal("Infinity"), "y": 2}],
        [{"x": float("nan"), "y": 2}],
        [{"x": float("inf"), "y": 2}],
        [{"x": -1, "y": 2}],
        [{"x": 101, "y": 2}],
        [{"x": 1, "y": -1}],
        [{"x": 1, "y": 101}],
    ),
)
def test_coordinate_feature_rejects_non_evidence_positions(
    invalid_positions: object,
) -> None:
    row = EXPECTED_FEATURES[4]
    assert not _is_feature_applicable(row, {})
    assert not _is_feature_applicable(row, {"action_positions": invalid_positions})


def test_capability_partition_is_derived_from_exact_accepted_sequence_semantics() -> None:
    potentially_capable, structurally_ineligible = _accepted_possession_capability_pair_sets()
    assert len(potentially_capable) == 28
    assert structurally_ineligible == frozenset(
        {(2, 23), (2, 24), (2, 25), (2, 26), (4, 40), (5, 51), (9, 90), (9, 91)}
    )
    assert not potentially_capable & structurally_ineligible
    assert len(potentially_capable | structurally_ineligible) == 36
    taxonomy = _load_strict_yaml(POSSESSION_TAXONOMY_PATH.read_bytes())
    predicates = taxonomy["predicates"]
    accepted_pairs = [
        (row["event_id"], row["subevent_id"]) for row in predicates if isinstance(row, dict)
    ]
    assert len(accepted_pairs) == len(set(accepted_pairs)) == 36
    assert set(accepted_pairs) == potentially_capable | structurally_ineligible
    assert {
        row["decision"]
        for row in predicates
        if isinstance(row, dict) and (row["event_id"], row["subevent_id"]) in potentially_capable
    } == {"CONTESTED", "CONTROL", "DEAD_BALL", "RESTART"}


def test_representative_capable_pairs_compose_with_accepted_sequence_resolver() -> None:
    resolver = runpy.run_path(str(POSSESSION_CONTRACT_PATH))
    taxonomy = resolver["_load_candidates"]()[2]
    predicates = taxonomy["predicates"]
    sequence_action = resolver["_sequence_action"]
    resolve = resolver["_resolve_same_period_sequences"]
    cases = (
        (
            "CONTROL",
            (7, 70),
            101,
            [sequence_action(101, 7, 70, elapsed=10, ordinal=1, team_id=10)],
        ),
        (
            "RESTART",
            (3, 30),
            201,
            [sequence_action(201, 3, 30, elapsed=10, ordinal=1, team_id=10)],
        ),
        (
            "DEAD_BALL",
            (2, 20),
            302,
            [
                sequence_action(301, 7, 70, elapsed=10, ordinal=1, team_id=10),
                sequence_action(302, 2, 20, elapsed=11, ordinal=2, team_id=10),
            ],
        ),
        (
            "CONTESTED",
            (1, 10),
            401,
            [
                sequence_action(401, 1, 10, elapsed=10, ordinal=1, team_id=10),
                sequence_action(402, 7, 70, elapsed=11, ordinal=2, team_id=10),
            ],
        ),
    )
    potentially_capable, _ = _accepted_possession_capability_pair_sets()
    for decision, pair, target_record_id, actions in cases:
        result = resolve(actions, predicates)[target_record_id]
        assert pair in potentially_capable
        assert result["decision"] == decision
        assert result["possession_eligibility_state"] == "ELIGIBLE_RESOLVED"
        assert result["resolved_possession_id"] is not None
        assert _is_feature_applicable(
            EXPECTED_FEATURES[11],
            {
                "action_event_taxonomy_id": pair[0],
                "action_subevent_taxonomy_id": pair[1],
                "action_team_source_id": 10,
                "possession_eligibility_state": result["possession_eligibility_state"],
            },
        )


def test_additional_ineligible_pairs_compose_as_unresolved_with_valid_control() -> None:
    resolver = runpy.run_path(str(POSSESSION_CONTRACT_PATH))
    taxonomy = resolver["_load_candidates"]()[2]
    predicates = taxonomy["predicates"]
    sequence_action = resolver["_sequence_action"]
    resolve = resolver["_resolve_same_period_sequences"]
    expected_semantics = {
        (2, 23): ("DEAD_BALL", "UNASSIGNED"),
        (2, 24): ("NON_CONTROL_ADMIN", None),
        (2, 26): ("NON_CONTROL_ADMIN", None),
        (5, 51): ("DEAD_BALL", "UNASSIGNED"),
    }
    _, structurally_ineligible = _accepted_possession_capability_pair_sets()
    for case_ordinal, (pair, semantics) in enumerate(expected_semantics.items(), start=1):
        first_record_id = case_ordinal * 1000
        target_record_id = first_record_id + 1
        actions = [
            sequence_action(
                first_record_id,
                7,
                70,
                elapsed=10,
                ordinal=1,
                team_id=10,
            ),
            sequence_action(
                target_record_id,
                pair[0],
                pair[1],
                elapsed=11,
                ordinal=2,
                team_id=10,
            ),
            sequence_action(
                first_record_id + 2,
                7,
                70,
                elapsed=12,
                ordinal=3,
                team_id=10,
            ),
        ]
        result = resolve(actions, predicates)[target_record_id]
        predicate = next(
            row
            for row in predicates
            if row["event_id"] == pair[0] and row["subevent_id"] == pair[1]
        )
        assert pair in structurally_ineligible
        assert (predicate["decision"], predicate["dead_ball_attachment"]) == semantics
        assert result["possession_eligibility_state"] == "INELIGIBLE_UNMAPPED"
        assert result["resolved_possession_id"] is None
        for eligibility_state in (result["possession_eligibility_state"], "ELIGIBLE_RESOLVED"):
            assert not _is_feature_applicable(
                EXPECTED_FEATURES[11],
                {
                    "action_event_taxonomy_id": pair[0],
                    "action_subevent_taxonomy_id": pair[1],
                    "action_team_source_id": 10,
                    "possession_eligibility_state": eligibility_state,
                },
            )


@pytest.mark.parametrize(
    ("event_id", "subevent_id", "decision"),
    (
        (1, 10, "CONTESTED"),
        (7, 70, "CONTROL"),
        (2, 20, "DEAD_BALL"),
        (3, 30, "RESTART"),
    ),
)
def test_resolved_possession_feature_accepts_each_resolution_capable_class(
    event_id: int,
    subevent_id: int,
    decision: str,
) -> None:
    taxonomy = _load_strict_yaml(POSSESSION_TAXONOMY_PATH.read_bytes())
    predicates = taxonomy["predicates"]
    matching = [
        row
        for row in predicates
        if isinstance(row, dict)
        and row.get("event_id") == event_id
        and row.get("subevent_id") == subevent_id
    ]
    assert len(matching) == 1
    assert matching[0]["decision"] == decision
    assert _is_feature_applicable(
        EXPECTED_FEATURES[11],
        {
            "action_event_taxonomy_id": event_id,
            "action_subevent_taxonomy_id": subevent_id,
            "action_team_source_id": 1,
            "possession_eligibility_state": "ELIGIBLE_RESOLVED",
        },
    )


@pytest.mark.parametrize(
    ("event_id", "subevent_id"),
    ((2, 25), (4, 40), (9, 90), (9, 91)),
)
def test_resolved_possession_feature_rejects_every_exact_unmapped_pair(
    event_id: int,
    subevent_id: int,
) -> None:
    _, structurally_ineligible = _accepted_possession_capability_pair_sets()
    assert (event_id, subevent_id) in structurally_ineligible
    assert not _is_feature_applicable(
        EXPECTED_FEATURES[11],
        {
            "action_event_taxonomy_id": event_id,
            "action_subevent_taxonomy_id": subevent_id,
            "action_team_source_id": 1,
            "possession_eligibility_state": "ELIGIBLE_RESOLVED",
        },
    )


@pytest.mark.parametrize(
    ("event_id", "subevent_id"),
    (
        (0, 0),
        (0, 10),
        (1, 0),
        (-1, 10),
        (1, -10),
        (7, 999),
        (999999, 999999),
    ),
)
def test_resolved_possession_feature_rejects_unknown_zero_or_negative_pairs(
    event_id: int,
    subevent_id: int,
) -> None:
    potentially_capable, structurally_ineligible = _accepted_possession_capability_pair_sets()
    assert (event_id, subevent_id) not in potentially_capable | structurally_ineligible
    assert not _is_feature_applicable(
        EXPECTED_FEATURES[11],
        {
            "action_event_taxonomy_id": event_id,
            "action_subevent_taxonomy_id": subevent_id,
            "action_team_source_id": 1,
            "possession_eligibility_state": "ELIGIBLE_RESOLVED",
        },
    )


@pytest.mark.parametrize(
    ("selector", "invalid_value"),
    (
        ("action_event_taxonomy_id", None),
        ("action_event_taxonomy_id", "8"),
        ("action_event_taxonomy_id", 8.0),
        ("action_event_taxonomy_id", Decimal("8")),
        ("action_event_taxonomy_id", True),
        ("action_subevent_taxonomy_id", None),
        ("action_subevent_taxonomy_id", "80"),
        ("action_subevent_taxonomy_id", 80.0),
        ("action_subevent_taxonomy_id", Decimal("80")),
        ("action_subevent_taxonomy_id", False),
        ("action_team_source_id", None),
        ("action_team_source_id", "1"),
        ("action_team_source_id", 1.0),
        ("action_team_source_id", True),
        ("action_team_source_id", Decimal("1")),
        ("action_team_source_id", 0),
        ("action_team_source_id", -1),
    ),
)
def test_resolved_possession_feature_rejects_mistyped_selectors(
    selector: str,
    invalid_value: object,
) -> None:
    context: dict[str, object] = {
        "action_event_taxonomy_id": 8,
        "action_subevent_taxonomy_id": 80,
        "action_team_source_id": 1,
        "possession_eligibility_state": "ELIGIBLE_RESOLVED",
    }
    context[selector] = invalid_value
    assert not _is_feature_applicable(EXPECTED_FEATURES[11], context)


@pytest.mark.parametrize(
    "missing_selector",
    (
        "action_event_taxonomy_id",
        "action_subevent_taxonomy_id",
        "action_team_source_id",
    ),
)
def test_resolved_possession_feature_rejects_missing_selectors(
    missing_selector: str,
) -> None:
    context: dict[str, object] = {
        "action_event_taxonomy_id": 8,
        "action_subevent_taxonomy_id": 80,
        "action_team_source_id": 1,
        "possession_eligibility_state": "ELIGIBLE_RESOLVED",
    }
    context.pop(missing_selector)
    assert not _is_feature_applicable(EXPECTED_FEATURES[11], context)


@pytest.mark.parametrize(
    ("possession_state", "expected"),
    (
        ("ELIGIBLE_RESOLVED", True),
        ("INELIGIBLE_UNMAPPED", False),
        ("PREDICATE_ADMITTED", False),
        (None, False),
        (True, False),
    ),
)
def test_resolved_possession_feature_requires_exact_accepted_eligibility_state(
    possession_state: object,
    expected: bool,
) -> None:
    row = EXPECTED_FEATURES[11]
    context: dict[str, object] = {
        "action_event_taxonomy_id": 8,
        "action_subevent_taxonomy_id": 80,
        "action_team_source_id": 1,
        "possession_eligibility_state": possession_state,
    }
    assert _is_feature_applicable(row, context) is expected
    context.pop("possession_eligibility_state")
    assert not _is_feature_applicable(row, context)
    context["possession_eligibility_state"] = possession_state
    context.pop("action_subevent_taxonomy_id")
    assert not _is_feature_applicable(row, context)


@pytest.mark.parametrize("recommendation", ("PASS", "REWORK"))
def test_valid_review_states_do_not_self_accept(recommendation: str) -> None:
    review_raw = _review_markdown(_valid_review_record(recommendation=recommendation))
    assert (
        _validate_authority_state(
            review_raw,
            None,
            later_authority_present=False,
            product_path_present=False,
            now=datetime(2026, 7, 31, 8, 40, tzinfo=UTC),
        )
        == f"REVIEW_{recommendation}"
    )


@pytest.mark.parametrize(
    "mutation",
    ("self-review", "digest", "clock", "id", "pass-findings", "actor", "extra"),
)
def test_review_mutations_reject(mutation: str) -> None:
    record = _valid_review_record()
    if mutation == "self-review":
        record["reviewed_by"] = MASTER_ACTOR_ID
    elif mutation == "digest":
        record["candidate_sha256"] = "0" * 64
    elif mutation == "clock":
        record["reviewed_at"] = "2026-07-31T08:36:59Z"
    elif mutation == "id":
        record["review_id"] = "wrong"
    elif mutation == "pass-findings":
        record["findings"] = [{"code": "STILL_OPEN", "severity": "P1", "summary": "Not empty."}]
    elif mutation == "actor":
        record["reviewed_by"] = "reviewer.agent"
    else:
        record["extra"] = None
    with pytest.raises(ValueError):
        _validate_authority_state(
            _review_markdown(record),
            None,
            later_authority_present=False,
            product_path_present=False,
            now=datetime(2026, 7, 31, 8, 40, tzinfo=UTC),
        )


def test_valid_acceptance_resolves_feature_hash_only_after_acceptance() -> None:
    review_raw = _review_markdown(_valid_review_record())
    review, review_record_raw = _load_review_markdown(review_raw)
    acceptance = _valid_acceptance_record(review_raw, review_record_raw)
    state = _validate_authority_state(
        review_raw,
        _canonical_json_bytes(acceptance),
        later_authority_present=False,
        product_path_present=False,
        now=datetime(2026, 7, 31, 8, 40, tzinfo=UTC),
    )
    assert review["recommendation"] == "PASS"
    assert state == "ACCEPTED"
    assert _feature_schema_hash(state, _load_candidates()[2]) == (
        EXPECTED_REGISTRY_CANONICAL_SHA256
    )


@pytest.mark.parametrize(
    "mutation",
    ("digest", "clock", "actor", "review-digest", "supersession", "recommendation"),
)
def test_acceptance_mutations_reject(mutation: str) -> None:
    review_raw = _review_markdown(_valid_review_record())
    _, review_record_raw = _load_review_markdown(review_raw)
    acceptance = _valid_acceptance_record(review_raw, review_record_raw)
    if mutation == "digest":
        acceptance["candidate_sha256"] = "0" * 64
    elif mutation == "clock":
        acceptance["accepted_at"] = "2026-07-31T08:37:59Z"
    elif mutation == "actor":
        acceptance["accepted_by"] = TEST_REVIEWER_ACTOR_ID
    elif mutation == "review-digest":
        acceptance["review_physical_sha256"] = "0" * 64
    elif mutation == "supersession":
        acceptance["supersedes_acceptance_id"] = "w04-prior-feature-acceptance"
    else:
        acceptance["review_recommendation"] = "REWORK"
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            _canonical_json_bytes(acceptance),
            later_authority_present=False,
            product_path_present=False,
            now=datetime(2026, 7, 31, 8, 40, tzinfo=UTC),
        )


def test_actual_progression_and_no_product_boundary() -> None:
    review_raw = REVIEW_PATH.read_bytes() if REVIEW_PATH.exists() else None
    acceptance_raw = ACCEPTANCE_PATH.read_bytes() if ACCEPTANCE_PATH.exists() else None
    state = _validate_authority_state(
        review_raw,
        acceptance_raw,
        later_authority_present=CROSS_AUTHORITY_PATH.exists(),
        product_path_present=any(path.exists() for path in PRODUCT_PATHS),
        now=datetime.now(UTC),
    )
    assert state in {"DECISION_ONLY", "REVIEW_PASS", "REVIEW_REWORK", "ACCEPTED"}
    if state != "ACCEPTED":
        assert not CROSS_AUTHORITY_PATH.exists()
        assert not any(path.exists() for path in PRODUCT_PATHS)


def test_decision_only_state_is_valid_and_blocks_progression() -> None:
    now = datetime(2026, 7, 31, 8, 40, tzinfo=UTC)
    assert (
        _validate_authority_state(
            None,
            None,
            later_authority_present=False,
            product_path_present=False,
            now=now,
        )
        == "DECISION_ONLY"
    )
    with pytest.raises(ValueError, match="progression before review"):
        _validate_authority_state(
            None,
            None,
            later_authority_present=True,
            product_path_present=False,
            now=now,
        )

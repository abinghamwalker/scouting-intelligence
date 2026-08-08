"""Contract for the closed, progression-safe W04 possession-semantic v2 authority."""

from __future__ import annotations

import json
import re
import unicodedata
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import RFC_4122, UUID

import pytest
import yaml
from yaml.nodes import MappingNode
from yaml.tokens import AliasToken, AnchorToken, DirectiveToken, TagToken

ROOT = Path(__file__).resolve().parents[2]
AUTHORITIES = ROOT / "reports/reviews/W04/authorities"
DECISION_PATH = AUTHORITIES / "wyscout-possession-semantic-decisions-v2.json"
TAXONOMY_PATH = ROOT / "configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml"
REVIEW_PATH = AUTHORITIES / "wyscout-possession-semantic-independent-review-v2-R1.md"
ACCEPTANCE_PATH = AUTHORITIES / "wyscout-possession-semantic-acceptance-v2.json"
R21_GATE_REPORT_PATH = (
    ROOT / "reports/verification/W04/wyscout-r21-cross-authority-gate-R1-master-verification.md"
)
R21_GATE_RECORD_PATH = ROOT / "reports/phase-gates/W04/wyscout-r21-correction-gate.json"
R21_GATE_REVIEW_PATH = (
    ROOT / "reports/reviews/W04/wyscout-r21-cross-authority-composability-independent-review-R1.md"
)
R21_GATE_RETURN_PATH = ROOT / "reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-GATE-01-R1.md"
R21_GATE_REPORT_PHYSICAL_SHA256 = "656769e7e9fe894421056230344ed9e976d583895cabe42600d1a2294042e14e"
R21_GATE_RETURN_PHYSICAL_SHA256 = "8f45128b4609b2a575a9f7da5e147dd95c5ef83f203812d27ac97e6fbd9eb051"
R21_GATE_REVIEW_PHYSICAL_SHA256 = "e9eca309986140ddfe40c66645a3f640777ff700e6a7187d43f020060d35c070"
R21_GATE_RECORD_PHYSICAL_SHA256 = "980303642f5c58876ed157698a5ea8f25ee79acef3c9faeaf015266cf547f168"
V1_DECISION_PATH = AUTHORITIES / "wyscout-possession-semantic-decisions-v1.json"
V1_TAXONOMY_PATH = ROOT / "configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml"
V1_REVIEW_PATH = AUTHORITIES / "wyscout-possession-semantic-independent-review-R1.md"
V1_ACCEPTANCE_PATH = AUTHORITIES / "wyscout-possession-semantic-acceptance-v1.json"
FIELD_REGISTRY_PATH = ROOT / "configs/schema/wyscout-v5-field-registry-v2.yaml"
FIELD_ACCEPTANCE_PATH = AUTHORITIES / "wyscout-field-semantic-acceptance-v2.json"
EVENT_TAXONOMY_PATH = ROOT / "data/source/wyscout/v5/objects/eventid2name.csv"
TAG_TAXONOMY_PATH = ROOT / "data/source/wyscout/v5/objects/tags2name.csv"

SOURCE_ID = "wyscout-soccer-match-events-figshare-v5"
DECISION_ID = "w04-wyscout-possession-semantic-decisions-v2"
TAXONOMY_ID = "w04-wyscout-possession-taxonomy-v2"
REVIEW_ID = "w04-wyscout-possession-semantic-independent-review-v2-R1"
ACCEPTANCE_ID = "w04-wyscout-possession-semantic-acceptance-v2"
V1_ACCEPTANCE_ID = "w04-wyscout-possession-semantic-acceptance-v1"
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
TEST_REVIEWER_ACTOR_ID = "03a65770-02f6-5eb0-9bd2-e2ebb44b62bd"
HISTORICAL_FAILED_REVIEW_SHA256 = frozenset(
    {
        "609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a",
        "71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a",
    }
)

EXPECTED_INPUTS = {
    "event_taxonomy_source_sha256": (
        "ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842"
    ),
    "field_acceptance_sha256": ("beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436"),
    "field_registry_canonical_sha256": (
        "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959"
    ),
    "field_registry_id": "w04-wyscout-field-registry-v2",
    "tag_taxonomy_source_sha256": (
        "e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922"
    ),
}
EXPECTED_V1_HASHES = {
    V1_ACCEPTANCE_PATH: "f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112",
    V1_DECISION_PATH: "4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71",
    V1_REVIEW_PATH: "1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4",
    V1_TAXONOMY_PATH: "e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d",
}
EXPECTED_PRIOR_AUTHORITY = {
    "acceptance_id": V1_ACCEPTANCE_ID,
    "acceptance_physical_sha256": EXPECTED_V1_HASHES[V1_ACCEPTANCE_PATH],
    "acceptance_schema_version": "w04-authority-acceptance-v1",
    "acceptance_sha256": EXPECTED_V1_HASHES[V1_ACCEPTANCE_PATH],
    "accepted_at": "2026-07-30T16:55:47Z",
    "accepted_by": MASTER_ACTOR_ID,
    "candidate_id": "w04-wyscout-possession-taxonomy-v1",
    "candidate_physical_sha256": EXPECTED_V1_HASHES[V1_TAXONOMY_PATH],
    "candidate_sha256": "6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa",
    "decision_id": "w04-wyscout-possession-semantic-decisions-v1",
    "decision_physical_sha256": EXPECTED_V1_HASHES[V1_DECISION_PATH],
    "decision_sha256": EXPECTED_V1_HASHES[V1_DECISION_PATH],
    "review_id": "w04-wyscout-possession-semantic-independent-review-R1",
    "review_physical_sha256": EXPECTED_V1_HASHES[V1_REVIEW_PATH],
    "review_recommendation": "PASS",
    "review_record_sha256": ("40aa258984714f33d91c502df1d50eefd4e076a7617c0ac6659c9679937d0962"),
    "supersedes_acceptance_id": None,
}
SELECTOR_FIELDS = [
    "action_event_taxonomy_id",
    "action_subevent_taxonomy_id",
    "action_team_source_id",
    "action_tag_ids",
]
EXPECTED_SELECTOR_POLICY = {
    "admitted_state": "PREDICATE_ADMITTED",
    "allowed_input_fields": SELECTOR_FIELDS,
    "coercion_policy": "FORBIDDEN",
    "exact_pair_policy": "REQUIRE_EXACT_PREDICATE",
    "missing_or_mistyped_input_policy": "PREDICATE_UNMAPPED",
    "output_field": "predicate_selection_state",
    "raw_rejected_name_label_matching": "FORBIDDEN",
    "tag_array_contract": "SORTED_UNIQUE_STRICT_INTEGER_REQUIRED",
    "team_requirement": "ACTION_TEAM_REQUIRES_CANONICAL_TEAM",
    "unmapped_state": "PREDICATE_UNMAPPED",
}
SEQUENCE_ORDER_FIELDS = [
    "period_rank",
    "period_elapsed_seconds",
    "source_record_ordinal",
    "source_event_record_id",
]
SEQUENCE_SCOPE_FIELDS = [
    "action_match_source_id",
    "action_period_code",
]
EXPECTED_SEQUENCE_POLICY = {
    "action_order_fields": SEQUENCE_ORDER_FIELDS,
    "assignment_cardinality": "EXACTLY_ONE_DETERMINISTIC_RESOLVED_POSSESSION",
    "contested_attachment_policy": "PREDICATE_PRECEDING_BUFFER_OR_UNASSIGNED_WITHIN_PERIOD",
    "control_open_policy": "OPEN_ACTION_TEAM_CONTROL",
    "cross_period_state_policy": "FORBIDDEN",
    "dead_ball_attachment_policy": "PREDICATE_PRECEDING_OR_UNASSIGNED",
    "equal_clock_cross_team_policy": "UNCERTAIN_BOUNDARY_UNASSIGNED",
    "final_output_field": "possession_eligibility_state",
    "ineligible_state": "INELIGIBLE_UNMAPPED",
    "match_period_scope_fields": SEQUENCE_SCOPE_FIELDS,
    "non_control_administration_policy": "UNASSIGNED",
    "opposing_team_transition_policy": "CLOSE_PRIOR_AND_OPEN_NEW",
    "period_boundary_policy": "CLOSE_AND_UNASSIGN_BUFFER",
    "resolved_state": "ELIGIBLE_RESOLVED",
    "restart_policy": "CLOSE_PRIOR_AND_OPEN_ACTION_TEAM_CONTROL",
    "same_team_transition_policy": "CONTINUE_OPEN_POSSESSION",
    "selector_admitted_state": "PREDICATE_ADMITTED",
    "selector_unmapped_state": "PREDICATE_UNMAPPED",
}
EXPECTED_POLICIES = {
    "cross_authority_selector": EXPECTED_SELECTOR_POLICY,
    "dead_ball_attachment": "PRECEDING_RESOLVED_POSSESSION_OR_UNASSIGNED",
    "period_boundary_policy": "CLOSE",
    "provider_native_possession_claim": False,
    "runtime_label_matching": "FORBIDDEN",
    "simultaneous_cross_team_policy": "UNCERTAIN_BOUNDARY",
    "same_period_sequence_resolution": EXPECTED_SEQUENCE_POLICY,
    "unknown_combination_policy": "UNMAPPED",
    "unknown_name_matching": "FORBIDDEN",
}
DECISION_KEYS = {
    "authority_class",
    "bound_inputs",
    "decided_at",
    "decided_by",
    "decision_id",
    "decision_schema_version",
    "policies",
    "predicates",
    "prior_authority",
    "source_id",
}
TAXONOMY_KEYS = {
    "bound_inputs",
    "decision_id",
    "decision_sha256",
    "policies",
    "predicates",
    "prior_authority",
    "source_id",
    "taxonomy_id",
    "taxonomy_schema_version",
}
PREDICATE_KEYS = {
    "closes_control",
    "contested_attachment",
    "control_team_source",
    "dead_ball_attachment",
    "decided_by",
    "decision",
    "event_id",
    "forbidden_tag_ids",
    "opens_control",
    "rationale",
    "required_tag_ids",
    "subevent_id",
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
R21_GATE_RECORD_KEYS = {
    "decision",
    "gate_path",
    "review_path",
    "review_physical_sha256",
    "review_recommendation",
}
R21_GATE_EVIDENCE_PATHS = (
    R21_GATE_REPORT_PATH,
    R21_GATE_RECORD_PATH,
    R21_GATE_REVIEW_PATH,
    R21_GATE_RETURN_PATH,
)
UTC_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{6})?Z\Z"
)
FINDING_CODE_RE = re.compile(r"[A-Z][A-Z0-9_]{1,63}\Z")
LATER_AUTHORITY_PATHS = (
    AUTHORITIES / "wyscout-supported-feature-registry-decisions-v1.json",
    ROOT / "configs/features/wyscout-v5-supported-count-features-v1.yaml",
    AUTHORITIES / "wyscout-supported-feature-registry-independent-review-R1.md",
    AUTHORITIES / "wyscout-supported-feature-registry-acceptance-v1.json",
    ROOT / "tests/contracts/test_w04_r21_cross_authority_composability.py",
)
PRODUCT_PATHS = (
    ROOT / "data/working/wyscout/v5/.staging",
    ROOT / "data/working/wyscout/v5/identity",
    ROOT / "data/working/wyscout/v5/bronze",
    ROOT / "data/working/wyscout/v5/silver",
    ROOT / "data/working/wyscout/v5/gold",
    ROOT / "data/working/wyscout/v5/possession",
    ROOT / "data/manifests/wyscout/v5/code",
    ROOT / "data/manifests/wyscout/v5/bronze",
    ROOT / "data/manifests/wyscout/v5/silver",
    ROOT / "data/manifests/wyscout/v5/gold",
    ROOT / "scripts/admit_wyscout_v5.py",
    ROOT / "scripts/admit_wyscout_v5_runtime.py",
    ROOT / "scripts/rebuild_wyscout_v5.py",
    ROOT / "scripts/launch_wyscout_v5.py",
    ROOT / "src/scouting/data_products/wyscout/possessions.py",
)


class _UniqueSafeLoader(yaml.SafeLoader):
    """Safe loader that rejects duplicate mappings before construction."""


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
    """Deterministic safe dumper with no aliases."""

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


def _present_r21_gate_evidence() -> dict[str, bytes]:
    return {
        str(path.relative_to(ROOT)): path.read_bytes()
        for path in R21_GATE_EVIDENCE_PATHS
        if path.exists()
    }


def _validate_exact_r21_gate_evidence(evidence: object) -> None:
    expected_paths = {str(path.relative_to(ROOT)) for path in R21_GATE_EVIDENCE_PATHS}
    if (
        not isinstance(evidence, dict)
        or set(evidence) != expected_paths
        or any(not isinstance(raw, bytes) or not raw for raw in evidence.values())
    ):
        raise ValueError("exact four-path R21 gate evidence is required")
    report_relative_path = str(R21_GATE_REPORT_PATH.relative_to(ROOT))
    record_relative_path = str(R21_GATE_RECORD_PATH.relative_to(ROOT))
    review_relative_path = str(R21_GATE_REVIEW_PATH.relative_to(ROOT))
    return_relative_path = str(R21_GATE_RETURN_PATH.relative_to(ROOT))
    if (
        sha256(evidence[report_relative_path]).hexdigest() != R21_GATE_REPORT_PHYSICAL_SHA256
        or sha256(evidence[record_relative_path]).hexdigest() != R21_GATE_RECORD_PHYSICAL_SHA256
        or sha256(evidence[review_relative_path]).hexdigest() != R21_GATE_REVIEW_PHYSICAL_SHA256
        or sha256(evidence[return_relative_path]).hexdigest() != R21_GATE_RETURN_PHYSICAL_SHA256
    ):
        raise ValueError("R21 gate artifact physical digest differs")
    gate = _load_canonical_json(evidence[record_relative_path])
    if set(gate) != R21_GATE_RECORD_KEYS or gate != {
        "decision": "PASS",
        "gate_path": str(R21_GATE_REPORT_PATH.relative_to(ROOT)),
        "review_path": review_relative_path,
        "review_physical_sha256": sha256(evidence[review_relative_path]).hexdigest(),
        "review_recommendation": "PASS",
    }:
        raise ValueError("R21 gate evidence binding differs")


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
        raise ValueError("taxonomy must be one mapping")
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


def _expected_prior_authority() -> dict[str, object]:
    prior = _load_canonical_json(V1_ACCEPTANCE_PATH.read_bytes())
    prior["acceptance_physical_sha256"] = EXPECTED_V1_HASHES[V1_ACCEPTANCE_PATH]
    prior["acceptance_sha256"] = EXPECTED_V1_HASHES[V1_ACCEPTANCE_PATH]
    if prior != EXPECTED_PRIOR_AUTHORITY:
        raise ValueError("accepted v1 authority differs")
    return prior


def _validate_frozen_inputs() -> None:
    assert (
        sha256(EVENT_TAXONOMY_PATH.read_bytes()).hexdigest()
        == EXPECTED_INPUTS["event_taxonomy_source_sha256"]
    )
    assert (
        sha256(TAG_TAXONOMY_PATH.read_bytes()).hexdigest()
        == EXPECTED_INPUTS["tag_taxonomy_source_sha256"]
    )
    field_acceptance_raw = FIELD_ACCEPTANCE_PATH.read_bytes()
    assert sha256(field_acceptance_raw).hexdigest() == EXPECTED_INPUTS["field_acceptance_sha256"]
    assert (
        _load_canonical_json(field_acceptance_raw)["candidate_id"]
        == EXPECTED_INPUTS["field_registry_id"]
    )
    field_registry = _load_strict_yaml(
        FIELD_REGISTRY_PATH.read_bytes(),
        require_canonical=True,
    )
    assert field_registry["registry_id"] == EXPECTED_INPUTS["field_registry_id"]
    assert (
        sha256(_canonical_json_bytes(field_registry)).hexdigest()
        == EXPECTED_INPUTS["field_registry_canonical_sha256"]
    )


def _load_candidates() -> tuple[dict[str, object], bytes, dict[str, object], bytes]:
    decision_raw = DECISION_PATH.read_bytes()
    taxonomy_raw = TAXONOMY_PATH.read_bytes()
    return (
        _load_canonical_json(decision_raw),
        decision_raw,
        _load_strict_yaml(taxonomy_raw),
        taxonomy_raw,
    )


def _validate_decision(
    decision: dict[str, object],
    *,
    now: datetime | None = None,
) -> None:
    _require_exact_keys(decision, DECISION_KEYS, "decision")
    if (
        decision["authority_class"] != "POSSESSION"
        or decision["bound_inputs"] != EXPECTED_INPUTS
        or decision["decision_id"] != DECISION_ID
        or decision["decision_schema_version"] != "w04-possession-semantic-decision-v2"
        or decision["policies"] != EXPECTED_POLICIES
        or decision["prior_authority"] != EXPECTED_PRIOR_AUTHORITY
        or decision["source_id"] != SOURCE_ID
    ):
        raise ValueError("decision authority differs")
    actor = _validate_actor(decision["decided_by"], "decision")
    if actor != MASTER_ACTOR_ID:
        raise ValueError("decision actor differs")
    decided_at = _parse_canonical_utc(decision["decided_at"])
    if decided_at < datetime(2026, 7, 30, 21, 21, 23, tzinfo=UTC):
        raise ValueError("decision predates field-v2 acceptance")
    current_time = datetime.now(UTC) if now is None else now
    if decided_at > current_time + timedelta(minutes=5):
        raise ValueError("future decision clock")
    predicates = decision["predicates"]
    v1_predicates = _load_canonical_json(V1_DECISION_PATH.read_bytes())["predicates"]
    if not isinstance(predicates, list) or len(predicates) != 36:
        raise ValueError("exactly 36 predicates required")
    if predicates != v1_predicates:
        raise ValueError("v1 predicates changed")
    for predicate in predicates:
        _require_exact_keys(predicate, PREDICATE_KEYS, "predicate")


def _validate_taxonomy(
    taxonomy: dict[str, object],
    decision: dict[str, object],
    decision_raw: bytes,
) -> None:
    _require_exact_keys(taxonomy, TAXONOMY_KEYS, "taxonomy")
    if (
        taxonomy["bound_inputs"] != decision["bound_inputs"]
        or taxonomy["decision_id"] != DECISION_ID
        or taxonomy["decision_sha256"] != sha256(decision_raw).hexdigest()
        or taxonomy["policies"] != decision["policies"]
        or taxonomy["predicates"] != decision["predicates"]
        or taxonomy["prior_authority"] != decision["prior_authority"]
        or taxonomy["source_id"] != SOURCE_ID
        or taxonomy["taxonomy_id"] != TAXONOMY_ID
        or taxonomy["taxonomy_schema_version"] != "w04-possession-taxonomy-v2"
    ):
        raise ValueError("taxonomy is not an exact decision restatement")


def _candidate_digests(
    decision_raw: bytes,
    taxonomy: dict[str, object],
    taxonomy_raw: bytes,
) -> dict[str, str]:
    decision_digest = sha256(decision_raw).hexdigest()
    return {
        "candidate_physical_sha256": sha256(taxonomy_raw).hexdigest(),
        "candidate_sha256": sha256(_canonical_json_bytes(taxonomy)).hexdigest(),
        "decision_physical_sha256": decision_digest,
        "decision_sha256": decision_digest,
    }


def _unmapped_selection(
    predicate: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "predicate": predicate,
        "predicate_selection_state": "PREDICATE_UNMAPPED",
    }


def _evaluate_selector(
    action: object,
    predicates: list[dict[str, object]],
) -> dict[str, object]:
    if not isinstance(action, dict):
        return _unmapped_selection()
    event_id = action.get("action_event_taxonomy_id")
    subevent_id = action.get("action_subevent_taxonomy_id")
    tag_ids = action.get("action_tag_ids")
    if type(event_id) is not int or type(subevent_id) is not int:  # noqa: E721
        return _unmapped_selection()
    if (
        not isinstance(tag_ids, list)
        or any(type(item) is not int for item in tag_ids)
        or tag_ids != sorted(set(tag_ids))
    ):
        return _unmapped_selection()
    predicate = next(
        (
            row
            for row in predicates
            if row["event_id"] == event_id and row["subevent_id"] == subevent_id
        ),
        None,
    )
    if predicate is None:
        return _unmapped_selection()
    if not set(predicate["required_tag_ids"]) <= set(tag_ids):
        return _unmapped_selection()
    if set(predicate["forbidden_tag_ids"]) & set(tag_ids):
        return _unmapped_selection()
    if predicate["control_team_source"] == "ACTION_TEAM":
        team_id = action.get("action_team_source_id")
        if type(team_id) is not int or team_id <= 0:  # noqa: E721
            return _unmapped_selection()
    if predicate["decision"] == "UNMAPPED":
        return _unmapped_selection(predicate)
    return {
        "predicate": predicate,
        "predicate_selection_state": "PREDICATE_ADMITTED",
    }


def _sequence_order_key(action: dict[str, object]) -> tuple[int, int, int, int]:
    return tuple(action[field] for field in SEQUENCE_ORDER_FIELDS)  # type: ignore[return-value]


def _sequence_context_is_valid(action: object) -> bool:
    if not isinstance(action, dict):
        return False
    match_id = action.get("action_match_source_id")
    period_code = action.get("action_period_code")
    period_rank = action.get("period_rank")
    elapsed = action.get("period_elapsed_seconds")
    ordinal = action.get("source_record_ordinal")
    record_id = action.get("source_event_record_id")
    return (
        type(match_id) is int  # noqa: E721
        and match_id > 0
        and isinstance(period_code, str)
        and bool(period_code)
        and type(period_rank) is int  # noqa: E721
        and period_rank > 0
        and type(elapsed) is int  # noqa: E721
        and elapsed >= 0
        and type(ordinal) is int  # noqa: E721
        and ordinal >= 0
        and type(record_id) is int  # noqa: E721
        and record_id > 0
    )


def _selector_view(action: dict[str, object]) -> dict[str, object]:
    return {field: action[field] for field in SELECTOR_FIELDS if field in action}


def _resolve_same_period_sequences(
    actions: list[object],
    predicates: list[dict[str, object]],
) -> dict[int, dict[str, object]]:
    """Executable contract evidence; product resolution remains separately owned."""

    results: dict[int, dict[str, object]] = {}
    groups: dict[tuple[int, str], list[dict[str, object]]] = {}
    invalid_ordinal = 0
    for value in actions:
        if not _sequence_context_is_valid(value):
            invalid_ordinal += 1
            results[-invalid_ordinal] = {
                "decision": "UNMAPPED",
                "predicate_selection_state": "PREDICATE_UNMAPPED",
                "possession_eligibility_state": "INELIGIBLE_UNMAPPED",
                "resolved_possession_id": None,
            }
            continue
        action = value
        record_id = action["source_event_record_id"]
        if record_id in results:
            raise ValueError("duplicate source_event_record_id")
        selection = _evaluate_selector(_selector_view(action), predicates)
        predicate = selection["predicate"]
        results[record_id] = {
            "decision": "UNMAPPED" if predicate is None else predicate["decision"],
            "predicate_selection_state": selection["predicate_selection_state"],
            "possession_eligibility_state": "INELIGIBLE_UNMAPPED",
            "resolved_possession_id": None,
        }
        scope = (action["action_match_source_id"], action["action_period_code"])
        groups.setdefault(scope, []).append(action)

    def assign(record_id: int, possession_id: str) -> None:
        result = results[record_id]
        prior = result["resolved_possession_id"]
        if prior is not None and prior != possession_id:
            raise ValueError("action assigned to multiple possessions")
        result["resolved_possession_id"] = possession_id
        result["possession_eligibility_state"] = "ELIGIBLE_RESOLVED"

    for (match_id, period_code), group in groups.items():
        possession_ordinal = 0
        ranks = {action["period_rank"] for action in group}
        if len(ranks) != 1:
            continue
        ordered = sorted(group, key=_sequence_order_key)
        if len({_sequence_order_key(action) for action in ordered}) != len(ordered):
            continue
        active_team: int | None = None
        active_possession: str | None = None
        last_resolved_possession: str | None = None
        buffered: list[int] = []
        cursor = 0
        while cursor < len(ordered):
            clock = (
                ordered[cursor]["period_rank"],
                ordered[cursor]["period_elapsed_seconds"],
            )
            cluster_end = cursor + 1
            while (
                cluster_end < len(ordered)
                and (
                    ordered[cluster_end]["period_rank"],
                    ordered[cluster_end]["period_elapsed_seconds"],
                )
                == clock
            ):
                cluster_end += 1
            cluster = ordered[cursor:cluster_end]
            controlling_teams = {
                action["action_team_source_id"]
                for action in cluster
                if results[action["source_event_record_id"]]["predicate_selection_state"]
                == "PREDICATE_ADMITTED"
                and results[action["source_event_record_id"]]["decision"] in {"CONTROL", "RESTART"}
            }
            if len(controlling_teams) > 1:
                active_team = None
                active_possession = None
                buffered.clear()
                cursor = cluster_end
                continue

            for action in cluster:
                record_id = action["source_event_record_id"]
                result = results[record_id]
                if result["predicate_selection_state"] != "PREDICATE_ADMITTED":
                    continue
                selection = _evaluate_selector(_selector_view(action), predicates)
                predicate = selection["predicate"]
                if predicate is None:
                    raise AssertionError("admitted selection requires predicate")
                decision = predicate["decision"]

                if decision in {"CONTROL", "RESTART"}:
                    team_id = action["action_team_source_id"]
                    if decision == "RESTART" or active_possession is None or active_team != team_id:
                        possession_ordinal += 1
                        active_possession = (
                            f"{match_id}:{period_code}:possession:{possession_ordinal}"
                        )
                        active_team = team_id
                    assign(record_id, active_possession)
                    last_resolved_possession = active_possession
                    for buffered_record_id in buffered:
                        assign(buffered_record_id, active_possession)
                    buffered.clear()
                    continue

                if decision == "DEAD_BALL":
                    if (
                        predicate["dead_ball_attachment"] == "PRECEDING_RESOLVED_POSSESSION"
                        and last_resolved_possession is not None
                    ):
                        assign(record_id, last_resolved_possession)
                    if predicate["closes_control"]:
                        active_team = None
                        active_possession = None
                    continue

                if decision == "CONTESTED":
                    attachment = predicate["contested_attachment"]
                    if (
                        attachment == "PRECEDING_RESOLVED_POSSESSION"
                        and last_resolved_possession is not None
                    ):
                        assign(record_id, last_resolved_possession)
                    elif attachment == "BUFFER_UNTIL_FOLLOWING_RESOLVED_POSSESSION":
                        buffered.append(record_id)

            cursor = cluster_end

    return results


def _sequence_action(
    record_id: int,
    event_id: int,
    subevent_id: int,
    *,
    elapsed: int,
    ordinal: int,
    team_id: object = None,
    match_id: int = 9001,
    period_code: str = "1H",
    period_rank: int = 1,
) -> dict[str, object]:
    action: dict[str, object] = {
        "action_event_taxonomy_id": event_id,
        "action_match_source_id": match_id,
        "action_period_code": period_code,
        "action_subevent_taxonomy_id": subevent_id,
        "action_tag_ids": [],
        "period_elapsed_seconds": elapsed,
        "period_rank": period_rank,
        "source_event_record_id": record_id,
        "source_record_ordinal": ordinal,
    }
    if team_id is not None:
        action["action_team_source_id"] = team_id
    return action


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
    taxonomy: dict[str, object],
    taxonomy_raw: bytes,
    *,
    now: datetime,
) -> tuple[dict[str, object], bytes]:
    review, record_raw = _load_review_markdown(raw)
    _require_exact_keys(review, REVIEW_KEYS, "review")
    expected_digests = _candidate_digests(decision_raw, taxonomy, taxonomy_raw)
    if (
        review["candidate_id"] != TAXONOMY_ID
        or review["decision_id"] != DECISION_ID
        or review["review_id"] != REVIEW_ID
        or review["review_schema_version"] != "w04-authority-independent-review-v1"
        or any(review[key] != digest for key, digest in expected_digests.items())
    ):
        raise ValueError("review candidate authority differs")
    reviewer = _validate_actor(review["reviewed_by"], "review")
    if reviewer == decision["decided_by"]:
        raise ValueError("self-review is forbidden")
    reviewed_at = _parse_canonical_utc(review["reviewed_at"])
    if (
        not _parse_canonical_utc(decision["decided_at"])
        <= reviewed_at
        <= (now + timedelta(minutes=5))
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
    taxonomy: dict[str, object],
    taxonomy_raw: bytes,
    *,
    now: datetime,
) -> None:
    acceptance = _load_canonical_json(raw)
    _require_exact_keys(acceptance, ACCEPTANCE_KEYS, "acceptance")
    expected_digests = _candidate_digests(decision_raw, taxonomy, taxonomy_raw)
    if (
        acceptance["acceptance_id"] != ACCEPTANCE_ID
        or acceptance["acceptance_schema_version"] != "w04-authority-acceptance-v1"
        or acceptance["candidate_id"] != TAXONOMY_ID
        or acceptance["decision_id"] != DECISION_ID
        or acceptance["review_id"] != REVIEW_ID
        or any(acceptance[key] != digest for key, digest in expected_digests.items())
        or acceptance["review_record_sha256"] != sha256(review_record_raw).hexdigest()
        or acceptance["review_physical_sha256"] != sha256(review_raw).hexdigest()
        or acceptance["review_recommendation"] != "PASS"
        or acceptance["supersedes_acceptance_id"] != V1_ACCEPTANCE_ID
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
    now: datetime,
) -> str:
    decision, decision_raw, taxonomy, taxonomy_raw = _load_candidates()
    _validate_decision(decision, now=now)
    _validate_taxonomy(taxonomy, decision, decision_raw)
    review: dict[str, object] | None = None
    record_raw: bytes | None = None
    if review_raw is not None:
        review, record_raw = _validate_review(
            review_raw,
            decision,
            decision_raw,
            taxonomy,
            taxonomy_raw,
            now=now,
        )
    if acceptance_raw is not None:
        if review is None or record_raw is None or review_raw is None:
            raise ValueError("acceptance requires a valid review")
        _validate_acceptance(
            acceptance_raw,
            review,
            review_raw,
            record_raw,
            decision,
            decision_raw,
            taxonomy,
            taxonomy_raw,
            now=now,
        )
        return "ACCEPTED"
    if later_authority_present:
        raise ValueError("later authority requires valid possession-v2 acceptance")
    if review is None:
        return "DECISION_ONLY"
    return f"REVIEW_{review['recommendation']}"


def _valid_review_record(*, recommendation: str = "PASS") -> dict[str, object]:
    decision, decision_raw, taxonomy, taxonomy_raw = _load_candidates()
    findings: list[dict[str, object]] = []
    if recommendation == "REWORK":
        findings = [
            {
                "code": "AUTHORITY_DEFECT",
                "severity": "P1",
                "summary": "A bounded authority defect remains.",
            }
        ]
    return {
        "candidate_id": TAXONOMY_ID,
        **_candidate_digests(decision_raw, taxonomy, taxonomy_raw),
        "decision_id": DECISION_ID,
        "findings": findings,
        "recommendation": recommendation,
        "review_id": REVIEW_ID,
        "review_schema_version": "w04-authority-independent-review-v1",
        "reviewed_at": "2026-07-30T22:15:00Z",
        "reviewed_by": TEST_REVIEWER_ACTOR_ID,
    }


def _review_markdown(record: dict[str, object]) -> bytes:
    return (
        b"Independent review evidence.\n\n```w04-authority-review-v1\n"
        + _canonical_json_bytes(record)
        + b"```\n\nEnd of review.\n"
    )


def _is_historical_failed_review(review_sha256: str) -> bool:
    return review_sha256 in HISTORICAL_FAILED_REVIEW_SHA256


def _current_review_raw_for_progression(review_raw: bytes | None) -> bytes | None:
    if review_raw is None:
        return None
    if _is_historical_failed_review(sha256(review_raw).hexdigest()):
        return None
    return review_raw


def _valid_acceptance_record(
    review: dict[str, object],
    review_raw: bytes,
) -> dict[str, object]:
    decision, decision_raw, taxonomy, taxonomy_raw = _load_candidates()
    return {
        "acceptance_id": ACCEPTANCE_ID,
        "acceptance_schema_version": "w04-authority-acceptance-v1",
        "accepted_at": "2026-07-30T22:15:01Z",
        "accepted_by": MASTER_ACTOR_ID,
        "candidate_id": TAXONOMY_ID,
        **_candidate_digests(decision_raw, taxonomy, taxonomy_raw),
        "decision_id": DECISION_ID,
        "review_id": REVIEW_ID,
        "review_physical_sha256": sha256(review_raw).hexdigest(),
        "review_record_sha256": sha256(_canonical_json_bytes(review)).hexdigest(),
        "review_recommendation": "PASS",
        "supersedes_acceptance_id": V1_ACCEPTANCE_ID,
    }


def test_frozen_inputs_prior_authority_and_v1_bytes_are_exact() -> None:
    _validate_frozen_inputs()
    assert _expected_prior_authority() == EXPECTED_PRIOR_AUTHORITY
    for artifact, expected_hash in EXPECTED_V1_HASHES.items():
        assert sha256(artifact.read_bytes()).hexdigest() == expected_hash


def test_decision_and_taxonomy_are_closed_digest_linked_authorities() -> None:
    decision, decision_raw, taxonomy, taxonomy_raw = _load_candidates()
    assert decision_raw == _canonical_json_bytes(decision)
    assert taxonomy_raw == _canonical_yaml_bytes(taxonomy)
    _validate_decision(decision)
    _validate_taxonomy(taxonomy, decision, decision_raw)


def test_all_36_v1_predicates_are_byte_semantically_unchanged() -> None:
    decision = _load_candidates()[0]
    v1_decision = _load_canonical_json(V1_DECISION_PATH.read_bytes())
    assert len(decision["predicates"]) == 36
    assert _canonical_json_bytes(decision["predicates"]) == _canonical_json_bytes(
        v1_decision["predicates"]
    )
    assert all(
        not row["required_tag_ids"] and not row["forbidden_tag_ids"]
        for row in decision["predicates"]
    )


def test_every_exact_pair_yields_only_its_v1_predicate_selection() -> None:
    predicates = _load_candidates()[0]["predicates"]
    for row in predicates:
        action: dict[str, object] = {
            "action_event_taxonomy_id": row["event_id"],
            "action_subevent_taxonomy_id": row["subevent_id"],
            "action_tag_ids": [],
        }
        if row["control_team_source"] == "ACTION_TEAM":
            action["action_team_source_id"] = 42
        result = _evaluate_selector(action, predicates)
        assert result["predicate"] == row
        assert result["predicate_selection_state"] == (
            "PREDICATE_UNMAPPED" if row["decision"] == "UNMAPPED" else "PREDICATE_ADMITTED"
        )
        assert "possession_eligibility_state" not in result


@pytest.mark.parametrize(
    "mutation",
    (
        "missing-event",
        "missing-subevent",
        "event-string",
        "subevent-string",
        "event-bool",
        "subevent-bool",
        "unknown-pair",
        "missing-tags",
        "tags-string",
        "tag-item-string",
        "tag-item-bool",
        "tags-duplicate",
        "tags-unsorted",
        "missing-team",
        "team-string",
        "team-bool",
        "team-zero",
    ),
)
def test_selector_negative_cases_are_predicate_unmapped(mutation: str) -> None:
    predicates = _load_candidates()[0]["predicates"]
    action: dict[str, object] = {
        "action_event_taxonomy_id": 7,
        "action_subevent_taxonomy_id": 70,
        "action_team_source_id": 42,
        "action_tag_ids": [],
    }
    if mutation == "missing-event":
        del action["action_event_taxonomy_id"]
    elif mutation == "missing-subevent":
        del action["action_subevent_taxonomy_id"]
    elif mutation == "event-string":
        action["action_event_taxonomy_id"] = "7"
    elif mutation == "subevent-string":
        action["action_subevent_taxonomy_id"] = "70"
    elif mutation == "event-bool":
        action["action_event_taxonomy_id"] = True
    elif mutation == "subevent-bool":
        action["action_subevent_taxonomy_id"] = True
    elif mutation == "unknown-pair":
        action["action_subevent_taxonomy_id"] = 999
    elif mutation == "missing-tags":
        del action["action_tag_ids"]
    elif mutation == "tags-string":
        action["action_tag_ids"] = "[]"
    elif mutation == "tag-item-string":
        action["action_tag_ids"] = ["703"]
    elif mutation == "tag-item-bool":
        action["action_tag_ids"] = [True]
    elif mutation == "tags-duplicate":
        action["action_tag_ids"] = [701, 701]
    elif mutation == "tags-unsorted":
        action["action_tag_ids"] = [703, 701]
    elif mutation == "missing-team":
        del action["action_team_source_id"]
    elif mutation == "team-string":
        action["action_team_source_id"] = "42"
    elif mutation == "team-bool":
        action["action_team_source_id"] = True
    else:
        action["action_team_source_id"] = 0
    assert _evaluate_selector(action, predicates) == _unmapped_selection()


def test_selector_never_consumes_raw_rejected_names_labels_or_other_fields() -> None:
    predicates = _load_candidates()[0]["predicates"]
    raw_only = {
        "$.eventId": 7,
        "$.subEventId": 70,
        "$.eventName": "Pass",
        "$.subEventName": "Simple pass",
        "event_label": "Pass",
        "rejected_field_value": 70,
        "action_team_source_id": 42,
        "action_tag_ids": [],
    }
    assert _evaluate_selector(raw_only, predicates) == _unmapped_selection()
    admitted = {
        "action_event_taxonomy_id": 7,
        "action_subevent_taxonomy_id": 70,
        "action_team_source_id": 42,
        "action_tag_ids": [],
    }
    baseline = _evaluate_selector(admitted, predicates)
    for forbidden_field in (
        "$.eventId",
        "$.subEventId",
        "$.eventName",
        "$.subEventName",
        "event_label",
        "subevent_label",
        "rejected_field_value",
    ):
        mutated = {**admitted, forbidden_field: "conflicting evidence"}
        assert _evaluate_selector(mutated, predicates) == baseline


def test_none_team_predicates_do_not_invent_or_require_control() -> None:
    predicates = _load_candidates()[0]["predicates"]
    base = {
        "action_event_taxonomy_id": 1,
        "action_subevent_taxonomy_id": 10,
        "action_tag_ids": [],
    }
    expected = _evaluate_selector(base, predicates)
    assert expected["predicate"]["decision"] == "CONTESTED"
    assert _evaluate_selector({**base, "action_team_source_id": 42}, predicates) == expected


def test_isolated_predicate_lookup_never_emits_final_eligibility() -> None:
    predicates = _load_candidates()[0]["predicates"]
    for event_id, subevent_id, team_id in (
        (7, 70, 42),
        (3, 30, 42),
        (2, 20, None),
        (1, 10, None),
        (2, 24, None),
    ):
        action: dict[str, object] = {
            "action_event_taxonomy_id": event_id,
            "action_subevent_taxonomy_id": subevent_id,
            "action_tag_ids": [],
        }
        if team_id is not None:
            action["action_team_source_id"] = team_id
        selection = _evaluate_selector(action, predicates)
        assert selection["predicate_selection_state"] == "PREDICATE_ADMITTED"
        assert "possession_eligibility_state" not in selection


def test_sequence_control_restart_and_team_transitions_are_deterministic() -> None:
    predicates = _load_candidates()[0]["predicates"]
    actions = [
        _sequence_action(4, 3, 30, elapsed=13, ordinal=4, team_id=20),
        _sequence_action(2, 7, 71, elapsed=11, ordinal=2, team_id=10),
        _sequence_action(1, 7, 70, elapsed=10, ordinal=1, team_id=10),
        _sequence_action(3, 8, 80, elapsed=12, ordinal=3, team_id=20),
    ]
    results = _resolve_same_period_sequences(actions, predicates)
    assert all(
        results[record_id]["possession_eligibility_state"] == "ELIGIBLE_RESOLVED"
        for record_id in (1, 2, 3, 4)
    )
    assert results[1]["resolved_possession_id"] == results[2]["resolved_possession_id"]
    assert results[2]["resolved_possession_id"] != results[3]["resolved_possession_id"]
    assert results[3]["resolved_possession_id"] != results[4]["resolved_possession_id"]


def test_multiscope_possession_ids_are_input_order_invariant() -> None:
    predicates = _load_candidates()[0]["predicates"]
    interleaved = [
        _sequence_action(
            101,
            7,
            70,
            elapsed=10,
            ordinal=1,
            team_id=10,
            match_id=100,
        ),
        _sequence_action(
            201,
            8,
            80,
            elapsed=20,
            ordinal=1,
            team_id=20,
            match_id=200,
            period_code="2H",
            period_rank=2,
        ),
        _sequence_action(
            102,
            3,
            30,
            elapsed=11,
            ordinal=2,
            team_id=10,
            match_id=100,
        ),
        _sequence_action(
            202,
            8,
            81,
            elapsed=21,
            ordinal=2,
            team_id=20,
            match_id=200,
            period_code="2H",
            period_rank=2,
        ),
    ]
    expected = {
        101: {
            "decision": "CONTROL",
            "predicate_selection_state": "PREDICATE_ADMITTED",
            "possession_eligibility_state": "ELIGIBLE_RESOLVED",
            "resolved_possession_id": "100:1H:possession:1",
        },
        102: {
            "decision": "RESTART",
            "predicate_selection_state": "PREDICATE_ADMITTED",
            "possession_eligibility_state": "ELIGIBLE_RESOLVED",
            "resolved_possession_id": "100:1H:possession:2",
        },
        201: {
            "decision": "CONTROL",
            "predicate_selection_state": "PREDICATE_ADMITTED",
            "possession_eligibility_state": "ELIGIBLE_RESOLVED",
            "resolved_possession_id": "200:2H:possession:1",
        },
        202: {
            "decision": "CONTROL",
            "predicate_selection_state": "PREDICATE_ADMITTED",
            "possession_eligibility_state": "ELIGIBLE_RESOLVED",
            "resolved_possession_id": "200:2H:possession:1",
        },
    }
    interleaved_results = _resolve_same_period_sequences(interleaved, predicates)
    reordered_results = _resolve_same_period_sequences(list(reversed(interleaved)), predicates)
    assert interleaved_results == reordered_results == expected


def test_sequence_preceding_dead_ball_and_contested_buffer_attach_once() -> None:
    predicates = _load_candidates()[0]["predicates"]
    actions = [
        _sequence_action(11, 7, 70, elapsed=10, ordinal=1, team_id=10),
        _sequence_action(12, 2, 20, elapsed=11, ordinal=2),
        _sequence_action(13, 1, 10, elapsed=12, ordinal=3),
        _sequence_action(14, 8, 80, elapsed=13, ordinal=4, team_id=20),
    ]
    results = _resolve_same_period_sequences(actions, predicates)
    assert results[11]["possession_eligibility_state"] == "ELIGIBLE_RESOLVED"
    assert results[12]["possession_eligibility_state"] == "ELIGIBLE_RESOLVED"
    assert results[12]["resolved_possession_id"] == results[11]["resolved_possession_id"]
    assert results[13]["possession_eligibility_state"] == "ELIGIBLE_RESOLVED"
    assert results[13]["resolved_possession_id"] == results[14]["resolved_possession_id"]


def test_sequence_unassigned_admin_unmapped_and_boundary_cases_stay_ineligible() -> None:
    predicates = _load_candidates()[0]["predicates"]
    actions = [
        _sequence_action(21, 5, 51, elapsed=10, ordinal=1),
        _sequence_action(22, 2, 20, elapsed=11, ordinal=2),
        _sequence_action(23, 1, 10, elapsed=12, ordinal=3),
        _sequence_action(24, 2, 24, elapsed=13, ordinal=4),
        _sequence_action(25, 9, 90, elapsed=14, ordinal=5),
        _sequence_action(26, 7, 70, elapsed=15, ordinal=6),
        _sequence_action(27, 7, 70, elapsed=16, ordinal=7, team_id=0),
    ]
    results = _resolve_same_period_sequences(actions, predicates)
    for record_id in (21, 22, 23, 24, 25, 26, 27):
        assert results[record_id]["possession_eligibility_state"] == "INELIGIBLE_UNMAPPED"
        assert results[record_id]["resolved_possession_id"] is None
    assert results[26]["predicate_selection_state"] == "PREDICATE_UNMAPPED"
    assert results[27]["predicate_selection_state"] == "PREDICATE_UNMAPPED"


def test_sequence_cross_team_equal_clock_is_an_uncertain_boundary() -> None:
    predicates = _load_candidates()[0]["predicates"]
    actions = [
        _sequence_action(31, 7, 70, elapsed=10, ordinal=1, team_id=10),
        _sequence_action(32, 8, 80, elapsed=10, ordinal=2, team_id=20),
    ]
    results = _resolve_same_period_sequences(actions, predicates)
    for record_id in (31, 32):
        assert results[record_id]["possession_eligibility_state"] == "INELIGIBLE_UNMAPPED"
        assert results[record_id]["resolved_possession_id"] is None


def test_period_boundary_closes_control_unassigns_buffer_and_forbids_cross_period_state() -> None:
    predicates = _load_candidates()[0]["predicates"]
    actions = [
        _sequence_action(41, 7, 70, elapsed=10, ordinal=1, team_id=10),
        _sequence_action(42, 1, 10, elapsed=11, ordinal=2),
        _sequence_action(
            43,
            2,
            20,
            elapsed=1,
            ordinal=3,
            period_code="2H",
            period_rank=2,
        ),
        _sequence_action(
            44,
            8,
            80,
            elapsed=2,
            ordinal=4,
            team_id=20,
            period_code="2H",
            period_rank=2,
        ),
    ]
    results = _resolve_same_period_sequences(actions, predicates)
    assert results[41]["possession_eligibility_state"] == "ELIGIBLE_RESOLVED"
    assert results[42]["possession_eligibility_state"] == "INELIGIBLE_UNMAPPED"
    assert results[43]["possession_eligibility_state"] == "INELIGIBLE_UNMAPPED"
    assert results[44]["possession_eligibility_state"] == "ELIGIBLE_RESOLVED"
    assert results[41]["resolved_possession_id"] != results[44]["resolved_possession_id"]


@pytest.mark.parametrize(
    "mutation",
    ("input", "policy", "prior-missing", "prior-extra", "prior-review", "predicate"),
)
def test_decision_binding_policy_prior_and_predicate_mutations_reject(
    mutation: str,
) -> None:
    decision = deepcopy(_load_candidates()[0])
    if mutation == "input":
        decision["bound_inputs"]["field_registry_id"] = "v1"
    elif mutation == "policy":
        decision["policies"]["cross_authority_selector"]["coercion_policy"] = "ALLOWED"
    elif mutation == "prior-missing":
        del decision["prior_authority"]["acceptance_sha256"]
    elif mutation == "prior-extra":
        decision["prior_authority"]["extra"] = None
    elif mutation == "prior-review":
        decision["prior_authority"]["review_recommendation"] = "REWORK"
    else:
        decision["predicates"][0]["rationale"] = "changed"
    with pytest.raises(ValueError):
        _validate_decision(decision)


@pytest.mark.parametrize(
    "raw",
    (
        b"---\n{}\n",
        b"a: &x 1\nb: *x\n",
        b"a: !!str 1\n",
        b"a: 1\na: 2\n",
        b"1: value\n",
        b"a: 1.5\n",
        b"a: 2026-07-30\n",
        b"---\na: 1\n---\nb: 2\n",
    ),
)
def test_noncanonical_or_unsafe_yaml_rejects(raw: bytes) -> None:
    with pytest.raises(ValueError):
        _load_strict_yaml(raw)


def test_actual_authority_progression_state_is_strict_and_progression_safe() -> None:
    fixed_path_raw = REVIEW_PATH.read_bytes() if REVIEW_PATH.exists() else None
    fixed_path_sha256 = sha256(fixed_path_raw).hexdigest() if fixed_path_raw is not None else None
    review_raw = _current_review_raw_for_progression(fixed_path_raw)
    acceptance_raw = ACCEPTANCE_PATH.read_bytes() if ACCEPTANCE_PATH.exists() else None
    later_authority_present = any(item.exists() for item in LATER_AUTHORITY_PATHS)
    if fixed_path_sha256 in HISTORICAL_FAILED_REVIEW_SHA256:
        assert review_raw is None
        assert acceptance_raw is None
        assert not later_authority_present
    state = _validate_authority_state(
        review_raw,
        acceptance_raw,
        later_authority_present=later_authority_present,
        now=datetime.now(UTC),
    )
    if fixed_path_sha256 in HISTORICAL_FAILED_REVIEW_SHA256:
        assert state == "DECISION_ONLY"
    else:
        assert state in {"DECISION_ONLY", "REVIEW_PASS", "REVIEW_REWORK", "ACCEPTED"}
    if any(item.exists() for item in PRODUCT_PATHS):
        _validate_exact_r21_gate_evidence(_present_r21_gate_evidence())


@pytest.mark.parametrize(
    "mutation",
    (
        "missing-report",
        "missing-record",
        "missing-review",
        "missing-return",
        "additional-path",
        "partial-record",
        "wrong-decision",
        "wrong-gate-path",
        "wrong-review-path",
        "wrong-recommendation",
        "wrong-review-digest",
        "changed-review-bytes",
        "changed-report-bytes",
        "changed-return-bytes",
        "paired-review-recomputed-record",
        "noncanonical-record",
    ),
)
def test_actual_progression_requires_exact_complete_r21_gate_evidence(mutation: str) -> None:
    evidence = _present_r21_gate_evidence()
    path_by_kind = {
        "report": str(R21_GATE_REPORT_PATH.relative_to(ROOT)),
        "record": str(R21_GATE_RECORD_PATH.relative_to(ROOT)),
        "review": str(R21_GATE_REVIEW_PATH.relative_to(ROOT)),
        "return": str(R21_GATE_RETURN_PATH.relative_to(ROOT)),
    }
    if mutation.startswith("missing-"):
        del evidence[path_by_kind[mutation.removeprefix("missing-")]]
    elif mutation == "additional-path":
        evidence["reports/verification/W04/unexpected-gate-evidence.md"] = b"unexpected\n"
    elif mutation == "changed-review-bytes":
        evidence[path_by_kind["review"]] += b"changed\n"
    elif mutation == "changed-report-bytes":
        evidence[path_by_kind["report"]] += b"changed\n"
    elif mutation == "changed-return-bytes":
        evidence[path_by_kind["return"]] += b"changed\n"
    elif mutation == "paired-review-recomputed-record":
        evidence[path_by_kind["review"]] += b"forged replacement review bytes\n"
        gate = _load_canonical_json(evidence[path_by_kind["record"]])
        gate["review_physical_sha256"] = sha256(evidence[path_by_kind["review"]]).hexdigest()
        evidence[path_by_kind["record"]] = _canonical_json_bytes(gate)
    elif mutation == "noncanonical-record":
        evidence[path_by_kind["record"]] = evidence[path_by_kind["record"]].removesuffix(b"\n")
    else:
        gate = _load_canonical_json(evidence[path_by_kind["record"]])
        if mutation == "partial-record":
            del gate["review_recommendation"]
        else:
            field, value = {
                "wrong-decision": ("decision", "REWORK"),
                "wrong-gate-path": ("gate_path", "reports/verification/W04/wrong.md"),
                "wrong-review-path": ("review_path", "reports/reviews/W04/wrong.md"),
                "wrong-recommendation": ("review_recommendation", "REWORK"),
                "wrong-review-digest": ("review_physical_sha256", "0" * 64),
            }[mutation]
            gate[field] = value
        evidence[path_by_kind["record"]] = _canonical_json_bytes(gate)
    with pytest.raises(ValueError):
        _validate_exact_r21_gate_evidence(evidence)


def test_current_review_route_is_exactly_the_r21_fixed_v2_r1_route() -> None:
    assert REVIEW_PATH == (AUTHORITIES / "wyscout-possession-semantic-independent-review-v2-R1.md")
    assert REVIEW_ID == "w04-wyscout-possession-semantic-independent-review-v2-R1"


@pytest.mark.parametrize(
    "review_sha256",
    (
        "71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a",
        "609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a",
    ),
)
def test_exact_historical_failed_reviews_are_transitional_non_authority(
    review_sha256: str,
) -> None:
    assert _is_historical_failed_review(review_sha256)
    assert (
        _validate_authority_state(
            None,
            None,
            later_authority_present=False,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )
        == "DECISION_ONLY"
    )
    with pytest.raises(ValueError, match="acceptance requires a valid review"):
        _validate_authority_state(
            None,
            b"{}",
            later_authority_present=False,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )
    with pytest.raises(ValueError, match="later authority requires valid"):
        _validate_authority_state(
            None,
            None,
            later_authority_present=True,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )


def test_unknown_invalid_current_review_bytes_fail_closed() -> None:
    review_raw = b"unknown invalid current review\n"
    assert not _is_historical_failed_review(sha256(review_raw).hexdigest())
    assert _current_review_raw_for_progression(review_raw) == review_raw
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            None,
            later_authority_present=False,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )


@pytest.mark.parametrize("recommendation", ("PASS", "REWORK"))
def test_valid_fixed_v2_r1_review_states_are_admitted(recommendation: str) -> None:
    review = _valid_review_record(recommendation=recommendation)
    assert review["review_id"] == "w04-wyscout-possession-semantic-independent-review-v2-R1"
    assert (
        _validate_authority_state(
            _review_markdown(review),
            None,
            later_authority_present=False,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )
        == f"REVIEW_{recommendation}"
    )


def test_valid_future_acceptance_lifts_only_the_later_authority_block() -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance_raw = _canonical_json_bytes(_valid_acceptance_record(review, review_raw))
    assert (
        _validate_authority_state(
            review_raw,
            acceptance_raw,
            later_authority_present=True,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )
        == "ACCEPTED"
    )


def test_later_authority_is_blocked_without_valid_acceptance() -> None:
    for review_raw in (
        None,
        _review_markdown(_valid_review_record()),
        _review_markdown(_valid_review_record(recommendation="REWORK")),
    ):
        with pytest.raises(ValueError):
            _validate_authority_state(
                review_raw,
                None,
                later_authority_present=True,
                now=datetime(2026, 7, 30, 23, tzinfo=UTC),
            )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("candidate_id", "wrong"),
        ("candidate_physical_sha256", "0" * 64),
        ("candidate_sha256", "0" * 64),
        ("decision_id", "wrong"),
        ("decision_physical_sha256", "0" * 64),
        ("decision_sha256", "0" * 64),
        ("review_id", "wrong"),
        ("reviewed_by", MASTER_ACTOR_ID),
        ("reviewed_at", "2026-07-30T21:00:00Z"),
    ),
)
def test_future_review_authority_mutations_reject(field: str, value: object) -> None:
    review = _valid_review_record()
    review[field] = value
    with pytest.raises(ValueError):
        _validate_authority_state(
            _review_markdown(review),
            None,
            later_authority_present=False,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("acceptance_id", "wrong"),
        ("accepted_by", TEST_REVIEWER_ACTOR_ID),
        ("candidate_physical_sha256", "0" * 64),
        ("candidate_sha256", "0" * 64),
        ("decision_physical_sha256", "0" * 64),
        ("decision_sha256", "0" * 64),
        ("review_physical_sha256", "0" * 64),
        ("review_record_sha256", "0" * 64),
        ("review_recommendation", "REWORK"),
        ("supersedes_acceptance_id", None),
    ),
)
def test_future_acceptance_authority_mutations_reject(
    field: str,
    value: object,
) -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance = _valid_acceptance_record(review, review_raw)
    acceptance[field] = value
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            _canonical_json_bytes(acceptance),
            later_authority_present=False,
            now=datetime(2026, 7, 30, 23, tzinfo=UTC),
        )

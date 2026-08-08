"""Contract for the closed W04 Wyscout field-semantic v2 authority."""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from uuid import RFC_4122, UUID

import pytest
import yaml
from yaml.nodes import MappingNode
from yaml.tokens import AliasToken, AnchorToken, DirectiveToken, TagToken

ROOT = Path(__file__).resolve().parents[2]
R20_PATH = ROOT / "reports/reviews/W04/wyscout-schema-design-R20.md"
R21_PATH = ROOT / "reports/reviews/W04/wyscout-schema-design-R21.md"
PROFILE_PATH = ROOT / "reports/phase-gates/W04/source-schema-profile.md"
COMPLETION_PATH = ROOT / "data/source/wyscout/v5/completion-manifest.json"
EVENT_TAXONOMY_PATH = ROOT / "data/source/wyscout/v5/objects/eventid2name.csv"
TAG_TAXONOMY_PATH = ROOT / "data/source/wyscout/v5/objects/tags2name.csv"
PRODUCT_PREIMAGE_PATH = ROOT / "configs/schema/wyscout-v5-product-contract-preimage-v1.json"
SCHEMA_PREIMAGE_PATH = ROOT / "configs/schema/wyscout-v5-schema-bundle-preimage-v1.json"
DECISION_PATH = ROOT / "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json"
REGISTRY_PATH = ROOT / "configs/schema/wyscout-v5-field-registry-v2.yaml"
REVIEW_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-v2-R1.md"
)
ACCEPTANCE_PATH = ROOT / "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json"
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
V1_DECISION_PATH = ROOT / "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json"
V1_REGISTRY_PATH = ROOT / "configs/schema/wyscout-v5-field-registry-v1.yaml"
V1_REVIEW_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md"
)
V1_ACCEPTANCE_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json"
)
V1_TEST_PATH = ROOT / "tests/contracts/test_wyscout_field_registry_authority.py"

SOURCE_ID = "wyscout-soccer-match-events-figshare-v5"
DECISION_ID = "w04-wyscout-field-semantic-decisions-v2"
REGISTRY_ID = "w04-wyscout-field-registry-v2"
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
INDEPENDENT_REVIEWER_ACTOR_ID = "03a65770-02f6-5eb0-9bd2-e2ebb44b62bd"
REVIEW_ID = "w04-wyscout-field-semantic-independent-review-v2-R1"
ACCEPTANCE_ID = "w04-wyscout-field-semantic-acceptance-v2"
PRIOR_ACCEPTANCE_ID = "w04-wyscout-field-semantic-acceptance-v1"
EXPECTED_DECISION_SHA256 = "cd4d51c0d7c365b73b0c23997716eb7755797889dca1fc545772263dc9924736"
EXPECTED_REGISTRY_PHYSICAL_SHA256 = (
    "15023556072f90b1e956277f255dc4a1df0bea78a5dcbb14b4863346ff9b5193"
)
EXPECTED_REGISTRY_CANONICAL_SHA256 = (
    "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959"
)
EXPECTED_INPUTS = {
    "completion_manifest_sha256": (
        "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
    ),
    "event_taxonomy_source_sha256": (
        "ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842"
    ),
    "product_contract_preimage_id": "w04-wyscout-product-contract-preimage-v1",
    "product_contract_preimage_sha256": (
        "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293"
    ),
    "r20_design_sha256": "8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047",
    "r21_design_sha256": "faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020",
    "schema_bundle_preimage_id": "w04-wyscout-schema-bundle-preimage-v1",
    "schema_bundle_preimage_sha256": (
        "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f"
    ),
    "source_schema_profile_sha256": (
        "569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649"
    ),
    "tag_taxonomy_source_sha256": (
        "e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922"
    ),
}
EXPECTED_PRIOR_AUTHORITY = {
    "acceptance_id": "w04-wyscout-field-semantic-acceptance-v1",
    "acceptance_physical_sha256": (
        "fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365"
    ),
    "acceptance_schema_version": "w04-authority-acceptance-v1",
    "acceptance_sha256": "fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365",
    "accepted_at": "2026-07-30T15:45:59Z",
    "accepted_by": "4efe5691-8903-5148-8275-30d2e7e8aed0",
    "candidate_id": "w04-wyscout-field-registry-v1",
    "candidate_physical_sha256": "805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2",
    "candidate_sha256": "fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034",
    "decision_id": "w04-wyscout-field-semantic-decisions-v1",
    "decision_physical_sha256": "e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999",
    "decision_sha256": "e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999",
    "review_id": "w04-wyscout-field-semantic-independent-review-R1",
    "review_physical_sha256": "e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861",
    "review_recommendation": "PASS",
    "review_record_sha256": "8beb747f71f43586c4a57125fae405e90db8af2bd8b6b408346b38b64d7e7fa0",
    "supersedes_acceptance_id": None,
}
EXPECTED_SUBEVENT_ROW = {
    "canonical_field": "action_subevent_taxonomy_id",
    "decision": "TRANSFORM",
    "json_path": "$.subEventId",
    "rationale": "action field $.subEventId has measured shape integer:3063574, string:7821. Emit "
    "action_subevent_taxonomy_id only from a strict JSON integer admitted by the exact "
    "frozen (event_id,subevent_id) taxonomy pair. Boolean is not integer. Strings and "
    "every other type are never parsed or coerced. Non-admitted values remain raw "
    "PRESERVE_UNMAPPED rejected-field evidence. Runtime label/name lookup is forbidden.",
    "record_kind": "action",
    "source_shape": [
        {"count": 3063574, "json_type": "integer"},
        {"count": 7821, "json_type": "string"},
    ],
    "source_support": "PROFILE_AND_EVENT_TAXONOMY",
    "transform": {
        "accepted_json_type": "STRICT_INTEGER",
        "admitted_key": ["action_event_taxonomy_id", "raw_subevent_integer"],
        "boolean_is_integer": False,
        "kind": "EVENT_SUBEVENT_TAXONOMY_ID_V2",
        "non_integer_policy": "PRESERVE_UNMAPPED",
        "runtime_label_matching": "FORBIDDEN",
        "string_policy": "PRESERVE_UNMAPPED_NO_COERCION",
        "taxonomy_sha256": "ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842",
        "unknown_integer_policy": "PRESERVE_UNMAPPED",
    },
}
EXPECTED_TAXONOMY_PAIRS = {
    (1, 10),
    (1, 11),
    (1, 12),
    (1, 13),
    (2, 20),
    (2, 21),
    (2, 22),
    (2, 23),
    (2, 24),
    (2, 25),
    (2, 26),
    (2, 27),
    (3, 30),
    (3, 31),
    (3, 32),
    (3, 33),
    (3, 34),
    (3, 35),
    (3, 36),
    (4, 40),
    (5, 50),
    (5, 51),
    (6, 60),
    (7, 70),
    (7, 71),
    (7, 72),
    (8, 80),
    (8, 81),
    (8, 82),
    (8, 83),
    (8, 84),
    (8, 85),
    (8, 86),
    (9, 90),
    (9, 91),
    (10, 100),
}
REASON_CODES = {
    "array": "ACTION_SUBEVENT_ARRAY_UNMAPPED",
    "boolean": "ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER",
    "integer_unknown": "ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY",
    "null": "ACTION_SUBEVENT_NULL_UNMAPPED",
    "number": "ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED",
    "object": "ACTION_SUBEVENT_OBJECT_UNMAPPED",
    "string": "ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED",
}
EXPECTED_V1_PHYSICAL_SHA256 = {
    V1_ACCEPTANCE_PATH: "fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365",
    V1_DECISION_PATH: "e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999",
    V1_REGISTRY_PATH: "805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2",
    V1_REVIEW_PATH: "e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861",
    V1_TEST_PATH: "d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3",
}
EXPECTED_POLICIES = {
    "known_profile_pair_policy": "REQUIRE_EXPLICIT_DECISION",
    "provider_native_semantic_claim": False,
    "runtime_label_matching": "FORBIDDEN",
    "unknown_envelope_kind_policy": "REJECT_RECORD",
    "unknown_field_policy": "UNMAPPED",
}
RECORD_KIND_ORDER = (
    "competition",
    "team",
    "player",
    "match",
    "action",
    "event-taxonomy",
    "tag-taxonomy",
)
EXPECTED_COUNTS = (10, 11, 26, 47, 18, 4, 3)
JSON_TYPE_ORDER = ("array", "boolean", "integer", "number", "null", "object", "string")
DECISION_KEYS = {
    "authority_class",
    "bound_inputs",
    "decided_at",
    "decided_by",
    "decision_id",
    "decision_schema_version",
    "decisions",
    "policies",
    "prior_authority",
    "source_id",
}
REGISTRY_KEYS = {
    "bound_inputs",
    "decision_id",
    "decision_sha256",
    "fields",
    "policies",
    "prior_authority",
    "registry_id",
    "registry_schema_version",
    "source_id",
}
ROW_KEYS = {
    "canonical_field",
    "decision",
    "json_path",
    "rationale",
    "record_kind",
    "source_shape",
    "source_support",
    "transform",
}
SOURCE_SUPPORTS = {
    "PROFILE_ONLY",
    "PROFILE_AND_EVENT_TAXONOMY",
    "PROFILE_AND_TAG_TAXONOMY",
    "PROFILE_AND_COMPLETION",
}
CANONICAL_FIELD_RE = re.compile(r"[a-z][a-z0-9_]{0,127}\Z")
UTC_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{6})?Z\Z"
)
FINDING_CODE_RE = re.compile(r"[A-Z][A-Z0-9_]{1,63}\Z")
MIN_DECISION_TIME = datetime(2026, 7, 30, tzinfo=UTC)
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
DOWNSTREAM_PATHS = (
    ROOT / "data/working/wyscout/v5/.staging",
    ROOT / "data/working/wyscout/v5/identity",
    ROOT / "data/working/wyscout/v5/bronze",
    ROOT / "data/working/wyscout/v5/silver",
    ROOT / "data/working/wyscout/v5/gold",
    ROOT / "data/manifests/wyscout/v5/code",
    ROOT / "data/manifests/wyscout/v5/bronze",
    ROOT / "data/manifests/wyscout/v5/silver",
    ROOT / "data/manifests/wyscout/v5/gold",
    ROOT / "scripts/admit_wyscout_v5.py",
    ROOT / "scripts/admit_wyscout_v5_runtime.py",
    ROOT / "scripts/rebuild_wyscout_v5.py",
    ROOT / "scripts/launch_wyscout_v5.py",
)


def _source_id_transform(entity_kind: str) -> dict[str, object]:
    return {
        "kind": "CANONICAL_SOURCE_ID",
        "entity_kind": entity_kind,
        "zero_policy": "REJECT",
        "allow_null": False,
    }


def _strict_integer_transform() -> dict[str, object]:
    return {
        "kind": "STRICT_INTEGER",
        "allow_null": False,
        "minimum": 0,
        "maximum": None,
    }


# These are the frozen positive projections. Everything outside this exact map is
# separately classified as FORBIDDEN or PRESERVE_UNMAPPED below.
TRANSFORM_ROWS: dict[tuple[str, str], tuple[str, dict[str, object]]] = {
    ("competition", "$.wyId"): (
        "competition_source_id",
        _source_id_transform("COMPETITION"),
    ),
    ("team", "$.wyId"): ("team_source_id", _source_id_transform("TEAM")),
    ("player", "$.wyId"): ("player_source_id", _source_id_transform("PLAYER")),
    ("match", "$.competitionId"): (
        "match_competition_source_id",
        _source_id_transform("COMPETITION"),
    ),
    ("match", "$.dateutc"): (
        "match_start_utc",
        {
            "kind": "PARSE_UTC",
            "allow_null": False,
            "accepted_formats": ["%Y-%m-%d %H:%M:%S"],
        },
    ),
    ("match", "$.gameweek"): ("match_gameweek", _strict_integer_transform()),
    ("match", "$.roundId"): ("match_round_source_id", _strict_integer_transform()),
    ("match", "$.seasonId"): ("match_season_source_id", _strict_integer_transform()),
    ("match", "$.teamsData.*.formation.bench[].playerId"): (
        "match_bench_player_source_id",
        _source_id_transform("PLAYER"),
    ),
    ("match", "$.teamsData.*.formation.lineup[].playerId"): (
        "match_lineup_player_source_id",
        _source_id_transform("PLAYER"),
    ),
    ("match", "$.teamsData.*.formation.substitutions[].minute"): (
        "match_substitution_nominal_minute",
        _strict_integer_transform(),
    ),
    ("match", "$.teamsData.*.formation.substitutions[].playerIn"): (
        "match_substitution_player_in_source_id",
        _source_id_transform("PLAYER"),
    ),
    ("match", "$.teamsData.*.formation.substitutions[].playerOut"): (
        "match_substitution_player_out_source_id",
        _source_id_transform("PLAYER"),
    ),
    ("match", "$.teamsData.*.teamId"): (
        "match_team_source_id",
        _source_id_transform("TEAM"),
    ),
    ("match", "$.wyId"): ("match_source_id", _source_id_transform("MATCH")),
    ("action", "$.eventId"): (
        "action_event_taxonomy_id",
        {
            "kind": "EVENT_TAXONOMY_ID",
            "taxonomy_sha256": EXPECTED_INPUTS["event_taxonomy_source_sha256"],
            "unknown_policy": "PRESERVE_UNMAPPED",
        },
    ),
    ("action", "$.eventSec"): (
        "action_period_relative_seconds",
        {
            "kind": "PERIOD_RELATIVE_SECONDS",
            "precision": 22,
            "scale": 18,
            "allow_negative": False,
        },
    ),
    ("action", "$.id"): ("action_source_id", _source_id_transform("ACTION")),
    ("action", "$.matchId"): (
        "action_match_source_id",
        _source_id_transform("MATCH"),
    ),
    ("action", "$.matchPeriod"): (
        "action_period_code",
        {"kind": "COPY_EXACT"},
    ),
    ("action", "$.playerId"): (
        "action_player_source_id",
        _source_id_transform("PLAYER"),
    ),
    ("action", "$.positions"): (
        "action_positions",
        {
            "kind": "POSITION_ARRAY",
            "axis_order": ["x", "y"],
            "minimum": "0",
            "maximum": "100",
            "anomaly_policy": "PRESERVE_AND_INELIGIBLE",
        },
    ),
    ("action", "$.tags[].id"): (
        "action_tag_ids",
        {
            "kind": "SORTED_TAG_IDS",
            "item_type": "STRICT_INTEGER",
            "duplicate_policy": "PRESERVE_EVIDENCE_AND_DEDUP_CANONICAL",
        },
    ),
    ("action", "$.teamId"): (
        "action_team_source_id",
        _source_id_transform("TEAM"),
    ),
    ("event-taxonomy", "$.event"): (
        "event_taxonomy_event_id",
        {
            "kind": "EVENT_TAXONOMY_ID",
            "taxonomy_sha256": EXPECTED_INPUTS["event_taxonomy_source_sha256"],
            "unknown_policy": "PRESERVE_UNMAPPED",
        },
    ),
    ("event-taxonomy", "$.subevent"): (
        "event_taxonomy_subevent_id",
        {
            "kind": "EVENT_TAXONOMY_ID",
            "taxonomy_sha256": EXPECTED_INPUTS["event_taxonomy_source_sha256"],
            "unknown_policy": "PRESERVE_UNMAPPED",
        },
    ),
    ("tag-taxonomy", "$.Tag"): (
        "tag_taxonomy_tag_id",
        {
            "kind": "TAG_TAXONOMY_ID",
            "taxonomy_sha256": EXPECTED_INPUTS["tag_taxonomy_source_sha256"],
            "unknown_policy": "PRESERVE_UNMAPPED",
        },
    ),
}

FORBIDDEN_REASONS: dict[tuple[str, str], str] = {}

for pair in {
    ("competition", "$.area.name"),
    ("competition", "$.name"),
    ("team", "$.area.name"),
    ("team", "$.city"),
    ("team", "$.name"),
    ("team", "$.officialName"),
    ("player", "$.birthArea.name"),
    ("player", "$.firstName"),
    ("player", "$.lastName"),
    ("player", "$.middleName"),
    ("player", "$.passportArea.name"),
    ("player", "$.shortName"),
    ("match", "$.label"),
    ("match", "$.venue"),
}:
    FORBIDDEN_REASONS[pair] = (
        "it is a name or display field and names cannot establish canonical identity "
        "or a product assertion"
    )

for pair in {
    ("player", "$.currentNationalTeamId"),
    ("player", "$.currentTeamId"),
}:
    FORBIDDEN_REASONS[pair] = (
        "it is a current-team assertion, which is outside the historical W04 proof claim"
    )

for pair in {
    ("player", "$.role"),
    ("player", "$.role.code2"),
    ("player", "$.role.code3"),
    ("player", "$.role.name"),
}:
    FORBIDDEN_REASONS[pair] = (
        "provider-native role data cannot become project role inference or matching authority"
    )

for pair in {
    ("match", "$.teamsData.*.formation.bench[].goals"),
    ("match", "$.teamsData.*.formation.bench[].ownGoals"),
    ("match", "$.teamsData.*.formation.bench[].redCards"),
    ("match", "$.teamsData.*.formation.bench[].yellowCards"),
    ("match", "$.teamsData.*.formation.lineup[].goals"),
    ("match", "$.teamsData.*.formation.lineup[].ownGoals"),
    ("match", "$.teamsData.*.formation.lineup[].redCards"),
    ("match", "$.teamsData.*.formation.lineup[].yellowCards"),
    ("match", "$.teamsData.*.score"),
    ("match", "$.teamsData.*.scoreET"),
    ("match", "$.teamsData.*.scoreHT"),
    ("match", "$.teamsData.*.scoreP"),
    ("match", "$.winner"),
}:
    FORBIDDEN_REASONS[pair] = (
        "it carries score, outcome, goal, or card evidence excluded from result-independent facts"
    )

for pair in {
    ("action", "$.eventName"),
    ("action", "$.subEventName"),
    ("event-taxonomy", "$.event_label"),
    ("event-taxonomy", "$.subevent_label"),
    ("tag-taxonomy", "$.Description"),
    ("tag-taxonomy", "$.Label"),
}:
    FORBIDDEN_REASONS[pair] = (
        "it is a provider display label and runtime label matching is forbidden"
    )

COMPLETION_SUPPORTED_PAIRS = {
    ("competition", "$.wyId"),
    ("team", "$.wyId"),
    ("player", "$.wyId"),
    ("match", "$.competitionId"),
    ("match", "$.teamsData.*.formation.bench[].playerId"),
    ("match", "$.teamsData.*.formation.lineup[].playerId"),
    ("match", "$.teamsData.*.formation.substitutions[].playerIn"),
    ("match", "$.teamsData.*.formation.substitutions[].playerOut"),
    ("match", "$.teamsData.*.teamId"),
    ("match", "$.wyId"),
    ("action", "$.id"),
    ("action", "$.matchId"),
    ("action", "$.playerId"),
    ("action", "$.teamId"),
}
EVENT_TAXONOMY_SUPPORTED_PAIRS = {
    ("action", "$.eventId"),
    ("action", "$.eventName"),
    ("action", "$.subEventId"),
    ("action", "$.subEventName"),
    ("event-taxonomy", "$.event"),
    ("event-taxonomy", "$.event_label"),
    ("event-taxonomy", "$.subevent"),
    ("event-taxonomy", "$.subevent_label"),
}
TAG_TAXONOMY_SUPPORTED_PAIRS = {
    ("action", "$.tags[].id"),
    ("tag-taxonomy", "$.Description"),
    ("tag-taxonomy", "$.Label"),
    ("tag-taxonomy", "$.Tag"),
}


class _UniqueSafeLoader(yaml.SafeLoader):
    """Safe loader that rejects duplicate mappings before construction."""


def _construct_unique_mapping(
    loader: _UniqueSafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[str, object]:
    if not isinstance(node, MappingNode):
        raise ValueError("mapping node required")
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError("YAML mapping keys must be strings")
        if key == "<<":
            raise ValueError("YAML merge keys are forbidden")
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class _NoAliasSafeDumper(yaml.SafeDumper):
    """Deterministic safe dumper that never emits aliases."""

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
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (encoded + "\n").encode()


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
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("JSON is not UTF-8") from exc
    try:
        value = json.loads(text, object_pairs_hook=_duplicate_rejecting_object)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("invalid strict JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("decision must be an object")
    if raw != _canonical_json_bytes(value):
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
    text = yaml.dump(
        value,
        Dumper=_NoAliasSafeDumper,
        allow_unicode=True,
        default_flow_style=False,
        explicit_end=False,
        explicit_start=False,
        sort_keys=False,
        width=4096,
    )
    return text.encode("utf-8")


def _reject_unsafe_yaml_value(value: object) -> None:
    if value is None or type(value) in {bool, int, str}:  # noqa: E721
        _assert_nfc_tree(value)
        return
    if isinstance(value, (float, date, datetime)):
        raise ValueError("floats and implicit timestamps are forbidden")
    if isinstance(value, list):
        for item in value:
            _reject_unsafe_yaml_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("YAML mapping keys must be strings")
            if key == "<<":
                raise ValueError("YAML merge keys are forbidden")
            _reject_unsafe_yaml_value(key)
            _reject_unsafe_yaml_value(item)
        return
    raise ValueError(f"unsafe YAML value: {type(value).__name__}")


def _load_strict_yaml(raw: bytes, *, require_canonical: bool = True) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("YAML BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("YAML is not UTF-8") from exc
    try:
        tokens = list(yaml.scan(text))
    except yaml.YAMLError as exc:
        raise ValueError("invalid YAML token stream") from exc
    denied_tokens = (AliasToken, AnchorToken, DirectiveToken, TagToken)
    if any(isinstance(token, denied_tokens) for token in tokens):
        raise ValueError("YAML aliases, anchors, directives, and explicit tags are forbidden")
    try:
        documents = list(yaml.load_all(text, Loader=_UniqueSafeLoader))
    except (yaml.YAMLError, ValueError) as exc:
        raise ValueError("invalid safe YAML") from exc
    if len(documents) != 1 or not isinstance(documents[0], dict):
        raise ValueError("registry must contain exactly one mapping document")
    value = documents[0]
    _reject_unsafe_yaml_value(value)
    if require_canonical and raw != _canonical_yaml_bytes(value):
        raise ValueError("noncanonical YAML")
    return value


def _authority_roster() -> list[tuple[str, str]]:
    text = R20_PATH.read_text(encoding="utf-8")
    marker = "The following is the normative machine roster:"
    if text.count(marker) != 1:
        raise ValueError("R20 roster marker must occur exactly once")
    tail = text.split(marker, 1)[1]
    block = tail.split("```text", 1)[1].split("```", 1)[0]
    roster: list[tuple[str, str]] = []
    declared_counts: list[int] = []
    for line in block.strip().splitlines():
        if line.startswith("# "):
            match = re.fullmatch(r"# ([a-z-]+): ([0-9]+)", line)
            if match is None:
                raise ValueError("invalid R20 roster count comment")
            declared_counts.append(int(match.group(2)))
            continue
        columns = line.split("\t")
        if len(columns) != 2:
            raise ValueError("R20 roster rows require one ASCII tab")
        roster.append((columns[0], columns[1]))
    if tuple(declared_counts) != EXPECTED_COUNTS:
        raise ValueError("R20 declared counts changed")
    if len(roster) != 119 or len(set(roster)) != 119:
        raise ValueError("R20 roster must contain 119 unique rows")
    return roster


def _parse_shape_text(shape_text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    prior_index = -1
    for component in shape_text.split(", "):
        parts = component.split(":")
        if len(parts) != 2 or parts[0] not in JSON_TYPE_ORDER:
            raise ValueError("unknown measured shape")
        type_index = JSON_TYPE_ORDER.index(parts[0])
        count = int(parts[1])
        if type_index <= prior_index or count <= 0:
            raise ValueError("measured shapes must be positive and in fixed order")
        prior_index = type_index
        rows.append({"json_type": parts[0], "count": count})
    if not rows:
        raise ValueError("empty measured shape")
    return rows


def _profile_shapes() -> dict[tuple[str, str], list[dict[str, object]]]:
    heading_map = {
        "event mapping": "event-taxonomy",
        "tag mapping": "tag-taxonomy",
        "competitions": "competition",
        "teams": "team",
        "players": "player",
        "matches": "match",
        "events": "action",
    }
    active_kind: str | None = None
    result: dict[tuple[str, str], list[dict[str, object]]] = {}
    for line in PROFILE_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            active_kind = heading_map.get(line[4:])
            continue
        if active_kind is None or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] in {"Path", "Column"} or set(cells[0]) == {"-"}:
            continue
        path = (
            cells[0] if active_kind not in {"event-taxonomy", "tag-taxonomy"} else f"$.{cells[0]}"
        )
        pair = (active_kind, path)
        if pair in result:
            raise ValueError("duplicate profile shape")
        shape = _parse_shape_text(cells[3])
        if sum(int(item["count"]) for item in shape) != int(cells[1]):
            raise ValueError("shape count does not equal observations/presence")
        result[pair] = shape
    roster = _authority_roster()
    if len(result) != 119 or set(result) != set(roster):
        raise ValueError("profile and R20 roster disagree")
    return result


def _input_digests() -> dict[str, str]:
    return {
        "completion_manifest_sha256": sha256(COMPLETION_PATH.read_bytes()).hexdigest(),
        "event_taxonomy_source_sha256": sha256(EVENT_TAXONOMY_PATH.read_bytes()).hexdigest(),
        "product_contract_preimage_id": "w04-wyscout-product-contract-preimage-v1",
        "product_contract_preimage_sha256": sha256(PRODUCT_PREIMAGE_PATH.read_bytes()).hexdigest(),
        "r20_design_sha256": sha256(R20_PATH.read_bytes()).hexdigest(),
        "r21_design_sha256": sha256(R21_PATH.read_bytes()).hexdigest(),
        "schema_bundle_preimage_id": "w04-wyscout-schema-bundle-preimage-v1",
        "schema_bundle_preimage_sha256": sha256(SCHEMA_PREIMAGE_PATH.read_bytes()).hexdigest(),
        "source_schema_profile_sha256": sha256(PROFILE_PATH.read_bytes()).hexdigest(),
        "tag_taxonomy_source_sha256": sha256(TAG_TAXONOMY_PATH.read_bytes()).hexdigest(),
    }


def _ordered_prior_authority() -> dict[str, object]:
    prior = _load_canonical_json(V1_ACCEPTANCE_PATH.read_bytes())
    prior["acceptance_physical_sha256"] = EXPECTED_PRIOR_AUTHORITY["acceptance_physical_sha256"]
    prior["acceptance_sha256"] = EXPECTED_PRIOR_AUTHORITY["acceptance_sha256"]
    if prior != EXPECTED_PRIOR_AUTHORITY:
        raise ValueError("field v1 prior authority differs")
    return prior


def _source_support(pair: tuple[str, str]) -> str:
    if pair in COMPLETION_SUPPORTED_PAIRS:
        return "PROFILE_AND_COMPLETION"
    if pair in EVENT_TAXONOMY_SUPPORTED_PAIRS:
        return "PROFILE_AND_EVENT_TAXONOMY"
    if pair in TAG_TAXONOMY_SUPPORTED_PAIRS:
        return "PROFILE_AND_TAG_TAXONOMY"
    return "PROFILE_ONLY"


def _shape_description(source_shape: list[dict[str, object]]) -> str:
    return ", ".join(f"{item['json_type']}:{item['count']}" for item in source_shape)


def _build_rows() -> list[dict[str, object]]:
    v1_decision = _load_canonical_json(V1_DECISION_PATH.read_bytes())
    rows = deepcopy(v1_decision["decisions"])
    matches = [
        index
        for index, row in enumerate(rows)
        if (row["record_kind"], row["json_path"]) == ("action", "$.subEventId")
    ]
    if matches != [106]:
        raise ValueError("v1 action subevent row position differs")
    replacement = deepcopy(EXPECTED_SUBEVENT_ROW)
    replacement["source_shape"] = [
        {"json_type": "integer", "count": 3063574},
        {"json_type": "string", "count": 7821},
    ]
    rows[matches[0]] = replacement
    return rows


def _event_taxonomy_pairs() -> set[tuple[int, int]]:
    with EVENT_TAXONOMY_PATH.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["event", "subevent", "event_label", "subevent_label"]:
            raise ValueError("event taxonomy columns differ")
        pairs = {(int(row["event"]), int(row["subevent"])) for row in reader}
    if len(pairs) != 36:
        raise ValueError("event taxonomy pair cardinality differs")
    return pairs


def _subevent_outcome(event_id: object, raw_value: object) -> dict[str, object]:
    if type(raw_value) is int and type(event_id) is int:  # noqa: E721
        if (event_id, raw_value) in _event_taxonomy_pairs():
            return {"canonical_value": raw_value, "raw_value": None, "reason_code": None}
        reason = REASON_CODES["integer_unknown"]
    elif isinstance(raw_value, str):
        reason = REASON_CODES["string"]
    elif type(raw_value) is bool:  # noqa: E721
        reason = REASON_CODES["boolean"]
    elif raw_value is None:
        reason = REASON_CODES["null"]
    elif isinstance(raw_value, (float, Decimal)):
        reason = REASON_CODES["number"]
    elif isinstance(raw_value, list):
        reason = REASON_CODES["array"]
    elif isinstance(raw_value, dict):
        reason = REASON_CODES["object"]
    elif type(raw_value) is int:  # noqa: E721
        reason = REASON_CODES["integer_unknown"]
    else:
        raise ValueError("value is outside strict JSON types")
    return {"canonical_value": None, "raw_value": raw_value, "reason_code": reason}


def _parse_canonical_utc(value: object) -> datetime:
    if not isinstance(value, str) or UTC_RE.fullmatch(value) is None:
        raise ValueError("noncanonical UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("invalid Gregorian UTC") from exc
    if parsed.tzinfo != UTC:
        raise ValueError("UTC offset must be zero")
    return parsed


def _require_exact_keys(value: object, keys: set[str], context: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{context} keys differ")
    return value


def _is_strict_integer(value: object) -> bool:
    return type(value) is int


def _validate_transform(transform: object) -> None:
    if not isinstance(transform, dict) or not isinstance(transform.get("kind"), str):
        raise ValueError("transform must contain a kind")
    kind = transform["kind"]
    expected_keys: dict[str, set[str]] = {
        "COPY_EXACT": {"kind"},
        "STRICT_INTEGER": {"kind", "allow_null", "minimum", "maximum"},
        "STRICT_DECIMAL": {"kind", "allow_null", "precision", "scale"},
        "PARSE_UTC": {"kind", "allow_null", "accepted_formats"},
        "CANONICAL_SOURCE_ID": {
            "kind",
            "entity_kind",
            "zero_policy",
            "allow_null",
        },
        "PERIOD_RELATIVE_SECONDS": {"kind", "precision", "scale", "allow_negative"},
        "POSITION_ARRAY": {
            "kind",
            "axis_order",
            "minimum",
            "maximum",
            "anomaly_policy",
        },
        "SORTED_TAG_IDS": {"kind", "item_type", "duplicate_policy"},
        "EVENT_TAXONOMY_ID": {"kind", "taxonomy_sha256", "unknown_policy"},
        "TAG_TAXONOMY_ID": {"kind", "taxonomy_sha256", "unknown_policy"},
        "COMPOSE_OBJECT": {"kind", "output_object", "member", "missing_policy"},
        "EVENT_SUBEVENT_TAXONOMY_ID_V2": {
            "accepted_json_type",
            "admitted_key",
            "boolean_is_integer",
            "kind",
            "non_integer_policy",
            "runtime_label_matching",
            "string_policy",
            "taxonomy_sha256",
            "unknown_integer_policy",
        },
    }
    if kind not in expected_keys or set(transform) != expected_keys[kind]:
        raise ValueError("unknown transform or cross-kind transform key")
    if kind == "COPY_EXACT":
        return
    if kind == "STRICT_INTEGER":
        if type(transform["allow_null"]) is not bool:  # noqa: E721
            raise ValueError("STRICT_INTEGER allow_null must be boolean")
        for key in ("minimum", "maximum"):
            if transform[key] is not None and not _is_strict_integer(transform[key]):
                raise ValueError("STRICT_INTEGER bounds must be integer or null")
        minimum = transform["minimum"]
        maximum = transform["maximum"]
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("STRICT_INTEGER bounds are inverted")
        return
    if kind == "STRICT_DECIMAL":
        precision = transform["precision"]
        scale = transform["scale"]
        if (
            type(transform["allow_null"]) is not bool  # noqa: E721
            or not _is_strict_integer(precision)
            or not _is_strict_integer(scale)
            or not 1 <= precision <= 38
            or not 0 <= scale <= precision
        ):
            raise ValueError("invalid STRICT_DECIMAL")
        return
    if kind == "PARSE_UTC":
        formats = transform["accepted_formats"]
        allowed_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]
        if (
            type(transform["allow_null"]) is not bool  # noqa: E721
            or not isinstance(formats, list)
            or not formats
            or len(formats) != len(set(formats))
            or any(item not in allowed_formats for item in formats)
            or formats != [item for item in allowed_formats if item in formats]
        ):
            raise ValueError("invalid PARSE_UTC")
        return
    if kind == "CANONICAL_SOURCE_ID":
        if (
            transform["entity_kind"] not in {"COMPETITION", "TEAM", "PLAYER", "MATCH", "ACTION"}
            or transform["zero_policy"] not in {"ALLOW", "REJECT"}
            or type(transform["allow_null"]) is not bool  # noqa: E721
        ):
            raise ValueError("invalid CANONICAL_SOURCE_ID")
        return
    if kind == "PERIOD_RELATIVE_SECONDS":
        if (
            transform["precision"] != 22
            or transform["scale"] != 18
            or transform["allow_negative"] is not False
        ):
            raise ValueError("invalid PERIOD_RELATIVE_SECONDS")
        return
    if kind == "POSITION_ARRAY":
        if (
            transform["axis_order"] != ["x", "y"]
            or transform["minimum"] != "0"
            or transform["maximum"] != "100"
            or transform["anomaly_policy"] != "PRESERVE_AND_INELIGIBLE"
        ):
            raise ValueError("invalid POSITION_ARRAY")
        return
    if kind == "SORTED_TAG_IDS":
        if (
            transform["item_type"] != "STRICT_INTEGER"
            or transform["duplicate_policy"] != "PRESERVE_EVIDENCE_AND_DEDUP_CANONICAL"
        ):
            raise ValueError("invalid SORTED_TAG_IDS")
        return
    if kind == "EVENT_SUBEVENT_TAXONOMY_ID_V2":
        if transform != EXPECTED_SUBEVENT_ROW["transform"]:
            raise ValueError("invalid EVENT_SUBEVENT_TAXONOMY_ID_V2")
        return
    if kind in {"EVENT_TAXONOMY_ID", "TAG_TAXONOMY_ID"}:
        expected_digest = EXPECTED_INPUTS[
            "event_taxonomy_source_sha256"
            if kind == "EVENT_TAXONOMY_ID"
            else "tag_taxonomy_source_sha256"
        ]
        if (
            transform["taxonomy_sha256"] != expected_digest
            or transform["unknown_policy"] != "PRESERVE_UNMAPPED"
        ):
            raise ValueError("invalid taxonomy transform")
        return
    if (
        CANONICAL_FIELD_RE.fullmatch(str(transform["output_object"])) is None
        or CANONICAL_FIELD_RE.fullmatch(str(transform["member"])) is None
        or transform["missing_policy"] not in {"EXPLICIT_NULL", "REJECT_PARENT"}
    ):
        raise ValueError("invalid COMPOSE_OBJECT")


def _validate_rows(rows: object) -> list[dict[str, object]]:
    if not isinstance(rows, list):
        raise ValueError("rows must be an array")
    typed_rows: list[dict[str, object]] = []
    for row in rows:
        typed_rows.append(_require_exact_keys(row, ROW_KEYS, "row"))
    pairs = [(row["record_kind"], row["json_path"]) for row in typed_rows]
    counts = tuple(
        sum(row["record_kind"] == record_kind for row in typed_rows)
        for record_kind in RECORD_KIND_ORDER
    )
    if counts != EXPECTED_COUNTS:
        raise ValueError("wrong per-kind counts")
    if len(typed_rows) != 119 or len(set(pairs)) != 119:
        raise ValueError("rows must contain 119 unique pairs")
    if pairs != _authority_roster():
        raise ValueError("omitted, extra, duplicate, or reordered roster row")
    shapes = _profile_shapes()
    producers: dict[str, list[dict[str, object]]] = {}
    for row, pair in zip(typed_rows, pairs, strict=True):
        if row["source_shape"] != shapes[pair]:
            raise ValueError("source shape mismatch")
        rationale = row["rationale"]
        if (
            not isinstance(rationale, str)
            or not 1 <= len(rationale) <= 2000
            or unicodedata.normalize("NFC", rationale) != rationale
        ):
            raise ValueError("invalid rationale")
        if row["source_support"] not in SOURCE_SUPPORTS:
            raise ValueError("unknown source support")
        decision = row["decision"]
        if decision == "TRANSFORM":
            canonical_field = row["canonical_field"]
            if (
                not isinstance(canonical_field, str)
                or CANONICAL_FIELD_RE.fullmatch(canonical_field) is None
                or row["transform"] is None
            ):
                raise ValueError("invalid transformed canonical field")
            _validate_transform(row["transform"])
            producers.setdefault(canonical_field, []).append(row)
        elif decision in {"PRESERVE_UNMAPPED", "FORBIDDEN"}:
            if row["canonical_field"] is not None or row["transform"] is not None:
                raise ValueError("non-transform rows require exact nulls")
        else:
            raise ValueError("unknown decision")
    for canonical_field, producer_rows in producers.items():
        if len(producer_rows) == 1:
            continue
        transforms = [row["transform"] for row in producer_rows]
        if any(transform["kind"] != "COMPOSE_OBJECT" for transform in transforms):
            raise ValueError(f"canonical-field collision: {canonical_field}")
        output_objects = {transform["output_object"] for transform in transforms}
        members = [transform["member"] for transform in transforms]
        if len(output_objects) != 1 or len(set(members)) != len(members):
            raise ValueError(f"invalid COMPOSE_OBJECT collision: {canonical_field}")
    return typed_rows


def _validate_decision(value: object) -> dict[str, object]:
    decision = _require_exact_keys(value, DECISION_KEYS, "decision")
    if (
        decision["authority_class"] != "FIELD"
        or decision["decision_id"] != DECISION_ID
        or decision["decision_schema_version"] != "w04-field-semantic-decision-v2"
        or decision["source_id"] != SOURCE_ID
        or decision["bound_inputs"] != EXPECTED_INPUTS
        or decision["policies"] != EXPECTED_POLICIES
        or decision["prior_authority"] != EXPECTED_PRIOR_AUTHORITY
    ):
        raise ValueError("fixed decision authority differs")
    actor = decision["decided_by"]
    if not isinstance(actor, str):
        raise ValueError("actor must be a string")
    try:
        actor_uuid = UUID(actor)
    except ValueError as exc:
        raise ValueError("actor must be UUID") from exc
    if (
        actor != str(actor_uuid)
        or actor_uuid.version != 5
        or actor_uuid.variant != RFC_4122
        or actor != MASTER_ACTOR_ID
    ):
        raise ValueError("invalid or noncanonical master actor")
    decided_at = _parse_canonical_utc(decision["decided_at"])
    if decided_at < MIN_DECISION_TIME:
        raise ValueError("backdated decision clock")
    if decided_at > datetime.now(UTC) + timedelta(minutes=5):
        raise ValueError("future decision clock")
    _validate_rows(decision["decisions"])
    if decision["decisions"] != _build_rows():
        raise ValueError("only the exact R21 action subevent row may differ from v1")
    return decision


def _validate_registry(
    value: object,
    decision: dict[str, object],
    decision_raw: bytes,
) -> dict[str, object]:
    registry = _require_exact_keys(value, REGISTRY_KEYS, "registry")
    if (
        registry["bound_inputs"] != decision["bound_inputs"]
        or registry["decision_id"] != DECISION_ID
        or registry["fields"] != decision["decisions"]
        or registry["policies"] != decision["policies"]
        or registry["prior_authority"] != decision["prior_authority"]
        or registry["registry_id"] != REGISTRY_ID
        or registry["registry_schema_version"] != "w04-field-registry-v2"
        or registry["source_id"] != SOURCE_ID
    ):
        raise ValueError("registry is not the exact parsed decision restatement")
    if registry["decision_sha256"] != sha256(decision_raw).hexdigest():
        raise ValueError("registry decision digest mismatch")
    _validate_rows(registry["fields"])
    return registry


def render_authority_artifacts(decided_at: str) -> tuple[bytes, bytes]:
    """Independently reconstruct the candidates from v1 plus the frozen R21 delta."""
    decision = {
        "authority_class": "FIELD",
        "bound_inputs": deepcopy(EXPECTED_INPUTS),
        "decided_at": decided_at,
        "decided_by": MASTER_ACTOR_ID,
        "decision_id": DECISION_ID,
        "decision_schema_version": "w04-field-semantic-decision-v2",
        "decisions": _build_rows(),
        "policies": deepcopy(EXPECTED_POLICIES),
        "prior_authority": _ordered_prior_authority(),
        "source_id": SOURCE_ID,
    }
    decision_raw = _canonical_json_bytes(decision)
    registry = {
        "bound_inputs": deepcopy(decision["bound_inputs"]),
        "decision_id": DECISION_ID,
        "decision_sha256": sha256(decision_raw).hexdigest(),
        "fields": deepcopy(decision["decisions"]),
        "policies": deepcopy(decision["policies"]),
        "prior_authority": deepcopy(decision["prior_authority"]),
        "registry_id": REGISTRY_ID,
        "registry_schema_version": "w04-field-registry-v2",
        "source_id": SOURCE_ID,
    }
    return decision_raw, _canonical_yaml_bytes(registry)


def _load_candidates() -> tuple[dict[str, object], bytes, dict[str, object], bytes]:
    decision_raw = DECISION_PATH.read_bytes()
    registry_raw = REGISTRY_PATH.read_bytes()
    decision = _load_canonical_json(decision_raw)
    registry = _load_strict_yaml(registry_raw)
    return decision, decision_raw, registry, registry_raw


def _validate_actor(value: object, expected: str | None, context: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{context} actor must be a string")
    try:
        actor = UUID(value)
    except ValueError as exc:
        raise ValueError(f"{context} actor must be UUID") from exc
    if value != str(actor) or actor.version != 5 or actor.variant != RFC_4122:
        raise ValueError(f"invalid or noncanonical {context} actor")
    if expected is not None and value != expected:
        raise ValueError(f"unexpected {context} actor")
    return value


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
        raise ValueError("review Markdown BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("review Markdown is not UTF-8") from exc
    if "\r" in text:
        raise ValueError("review Markdown requires LF line endings")
    lines = text.splitlines(keepends=True)
    fence_indexes = [
        index
        for index, line in enumerate(lines)
        if re.match(r" {0,3}(?:`{3,}|~{3,})", line) is not None
    ]
    if len(fence_indexes) != 2:
        raise ValueError("review Markdown requires exactly one fenced block")
    opening_index, closing_index = fence_indexes
    if (
        lines[opening_index] != "```w04-authority-review-v1\n"
        or lines[closing_index] not in {"```\n", "```"}
        or closing_index <= opening_index
    ):
        raise ValueError("invalid review authority fence")
    body = "".join(lines[opening_index + 1 : closing_index]).encode()
    record = _load_canonical_json(body)
    return record, body


def _validate_review(
    raw: bytes,
    decision: dict[str, object],
    decision_raw: bytes,
    registry: dict[str, object],
    registry_raw: bytes,
    *,
    now: datetime | None = None,
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
        raise ValueError("review candidate authority differs")
    reviewer = _validate_actor(
        review["reviewed_by"],
        None,
        "reviewer",
    )
    if reviewer == decision["decided_by"]:
        raise ValueError("self-review is forbidden")
    reviewed_at = _parse_canonical_utc(review["reviewed_at"])
    decided_at = _parse_canonical_utc(decision["decided_at"])
    if reviewed_at < decided_at:
        raise ValueError("review clock predates decision")
    current_time = datetime.now(UTC) if now is None else now
    if reviewed_at > current_time + timedelta(minutes=5):
        raise ValueError("future review clock")
    findings = review["findings"]
    if not isinstance(findings, list):
        raise ValueError("review findings must be an array")
    for finding_value in findings:
        finding = _require_exact_keys(finding_value, FINDING_KEYS, "finding")
        code = finding["code"]
        severity = finding["severity"]
        summary = finding["summary"]
        if not isinstance(code, str) or FINDING_CODE_RE.fullmatch(code) is None:
            raise ValueError("invalid review finding code")
        if severity not in {"P0", "P1", "P2"}:
            raise ValueError("invalid review finding severity")
        if (
            not isinstance(summary, str)
            or not 1 <= len(summary) <= 2000
            or unicodedata.normalize("NFC", summary) != summary
        ):
            raise ValueError("invalid review finding summary")
    recommendation = review["recommendation"]
    if (
        recommendation not in {"PASS", "REWORK"}
        or (recommendation == "PASS" and findings)
        or (recommendation == "REWORK" and not findings)
    ):
        raise ValueError("review recommendation and findings disagree")
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
    now: datetime | None = None,
) -> dict[str, object]:
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
        or acceptance["supersedes_acceptance_id"] != PRIOR_ACCEPTANCE_ID
    ):
        raise ValueError("acceptance authority differs")
    accepted_by = _validate_actor(
        acceptance["accepted_by"],
        MASTER_ACTOR_ID,
        "acceptance",
    )
    if accepted_by == review["reviewed_by"]:
        raise ValueError("reviewer cannot accept own review")
    if review["recommendation"] != "PASS" or review["findings"]:
        raise ValueError("acceptance requires a valid PASS review")
    decided_at = _parse_canonical_utc(decision["decided_at"])
    reviewed_at = _parse_canonical_utc(review["reviewed_at"])
    accepted_at = _parse_canonical_utc(acceptance["accepted_at"])
    if not decided_at <= reviewed_at <= accepted_at:
        raise ValueError("acceptance clock order is invalid")
    current_time = datetime.now(UTC) if now is None else now
    if accepted_at > current_time + timedelta(minutes=5):
        raise ValueError("future acceptance clock")
    return acceptance


def _validate_authority_state(
    review_raw: bytes | None,
    acceptance_raw: bytes | None,
    *,
    downstream_paths_present: bool,
    now: datetime | None = None,
) -> str:
    if downstream_paths_present:
        raise ValueError("product paths remain blocked until the complete R21 gate")
    decision, decision_raw, registry, registry_raw = _load_candidates()
    _validate_decision(decision)
    _validate_registry(registry, decision, decision_raw)
    review: dict[str, object] | None = None
    review_record_raw: bytes | None = None
    if review_raw is not None:
        review, review_record_raw = _validate_review(
            review_raw,
            decision,
            decision_raw,
            registry,
            registry_raw,
            now=now,
        )
    if acceptance_raw is not None:
        if review is None or review_record_raw is None or review_raw is None:
            raise ValueError("acceptance requires a present valid review")
        _validate_acceptance(
            acceptance_raw,
            review,
            review_raw,
            review_record_raw,
            decision,
            decision_raw,
            registry,
            registry_raw,
            now=now,
        )
        return "ACCEPTED"
    if review is None:
        return "DECISION_ONLY"
    return "REVIEW_PASS" if review["recommendation"] == "PASS" else "REVIEW_REWORK"


def _valid_review_record(*, recommendation: str = "PASS") -> dict[str, object]:
    decision, decision_raw, registry, registry_raw = _load_candidates()
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
        "candidate_id": REGISTRY_ID,
        **_candidate_digests(decision_raw, registry, registry_raw),
        "decision_id": DECISION_ID,
        "findings": findings,
        "recommendation": recommendation,
        "review_id": REVIEW_ID,
        "review_schema_version": "w04-authority-independent-review-v1",
        "reviewed_at": "2026-07-30T20:22:18Z",
        "reviewed_by": INDEPENDENT_REVIEWER_ACTOR_ID,
    }


def _review_markdown(record: dict[str, object]) -> bytes:
    return (
        b"Independent review evidence.\n\n```w04-authority-review-v1\n"
        + _canonical_json_bytes(record)
        + b"```\n\nEnd of review.\n"
    )


def _valid_acceptance_record(
    review: dict[str, object],
    review_raw: bytes,
) -> dict[str, object]:
    decision, decision_raw, registry, registry_raw = _load_candidates()
    return {
        "acceptance_id": ACCEPTANCE_ID,
        "acceptance_schema_version": "w04-authority-acceptance-v1",
        "accepted_at": "2026-07-30T20:22:19Z",
        "accepted_by": MASTER_ACTOR_ID,
        "candidate_id": REGISTRY_ID,
        **_candidate_digests(decision_raw, registry, registry_raw),
        "decision_id": DECISION_ID,
        "review_id": REVIEW_ID,
        "review_physical_sha256": sha256(review_raw).hexdigest(),
        "review_record_sha256": sha256(_canonical_json_bytes(review)).hexdigest(),
        "review_recommendation": "PASS",
        "supersedes_acceptance_id": PRIOR_ACCEPTANCE_ID,
    }


def test_fixed_inputs_and_all_119_source_shapes_reproduce_independently() -> None:
    assert _input_digests() == EXPECTED_INPUTS
    roster = _authority_roster()
    shapes = _profile_shapes()
    assert len(roster) == len(shapes) == 119
    assert (
        tuple(sum(pair[0] == record_kind for pair in roster) for record_kind in RECORD_KIND_ORDER)
        == EXPECTED_COUNTS
    )
    assert all(shapes[pair] for pair in roster)


def test_decision_and_registry_are_closed_digest_linked_authorities() -> None:
    decision, decision_raw, registry, registry_raw = _load_candidates()
    _validate_decision(decision)
    _validate_registry(registry, decision, decision_raw)
    assert sha256(decision_raw).hexdigest() == EXPECTED_DECISION_SHA256
    assert sha256(registry_raw).hexdigest() == EXPECTED_REGISTRY_PHYSICAL_SHA256
    assert sha256(_canonical_json_bytes(registry)).hexdigest() == EXPECTED_REGISTRY_CANONICAL_SHA256
    assert decision_raw == _canonical_json_bytes(decision)
    assert registry_raw == _canonical_yaml_bytes(registry)
    assert render_authority_artifacts(decision["decided_at"]) == (decision_raw, registry_raw)


def test_v1_bytes_prior_authority_and_sole_semantic_delta_are_exact() -> None:
    for path, expected_digest in EXPECTED_V1_PHYSICAL_SHA256.items():
        assert sha256(path.read_bytes()).hexdigest() == expected_digest
    v1_decision = _load_canonical_json(V1_DECISION_PATH.read_bytes())
    v1_registry = _load_strict_yaml(V1_REGISTRY_PATH.read_bytes())
    decision, _, registry, _ = _load_candidates()
    assert (
        sha256(_canonical_json_bytes(v1_registry)).hexdigest()
        == "fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034"
    )
    assert decision["prior_authority"] == EXPECTED_PRIOR_AUTHORITY
    assert registry["prior_authority"] == EXPECTED_PRIOR_AUTHORITY
    differences = [
        index
        for index, (old, new) in enumerate(
            zip(v1_decision["decisions"], decision["decisions"], strict=True)
        )
        if old != new
    ]
    assert differences == [106]
    assert decision["decisions"][106] == EXPECTED_SUBEVENT_ROW
    assert registry["fields"] == decision["decisions"]


def test_exact_frozen_taxonomy_pairs_emit_only_strict_integers() -> None:
    assert _event_taxonomy_pairs() == EXPECTED_TAXONOMY_PAIRS
    for event_id, subevent_id in EXPECTED_TAXONOMY_PAIRS:
        assert _subevent_outcome(event_id, subevent_id) == {
            "canonical_value": subevent_id,
            "raw_value": None,
            "reason_code": None,
        }
    assert _subevent_outcome(True, 10)["canonical_value"] is None
    assert _subevent_outcome(1, True)["reason_code"] == REASON_CODES["boolean"]


@pytest.mark.parametrize(
    ("raw_value", "reason_code"),
    (
        ("10", REASON_CODES["string"]),
        (" 10", REASON_CODES["string"]),
        ("+10", REASON_CODES["string"]),
        ("010", REASON_CODES["string"]),
        (True, REASON_CODES["boolean"]),
        (False, REASON_CODES["boolean"]),
        (None, REASON_CODES["null"]),
        (10.0, REASON_CODES["number"]),
        (Decimal("10.0"), REASON_CODES["number"]),
        ([10], REASON_CODES["array"]),
        ({"value": 10}, REASON_CODES["object"]),
    ),
)
def test_every_non_integer_json_type_preserves_exact_raw_evidence(
    raw_value: object, reason_code: str
) -> None:
    outcome = _subevent_outcome(1, raw_value)
    assert outcome["canonical_value"] is None
    assert outcome["reason_code"] == reason_code
    assert type(outcome["raw_value"]) is type(raw_value)
    assert outcome["raw_value"] == raw_value


def test_unknown_integer_pairs_and_absent_canonical_events_preserve_raw() -> None:
    for event_id, raw_value in ((1, 999), (999, 10), (None, 10), ("1", 10)):
        assert _subevent_outcome(event_id, raw_value) == {
            "canonical_value": None,
            "raw_value": raw_value,
            "reason_code": REASON_CODES["integer_unknown"],
        }
    assert set(REASON_CODES.values()) == {
        "ACTION_SUBEVENT_ARRAY_UNMAPPED",
        "ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER",
        "ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY",
        "ACTION_SUBEVENT_NULL_UNMAPPED",
        "ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED",
        "ACTION_SUBEVENT_OBJECT_UNMAPPED",
        "ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("accepted_json_type", "INTEGER_OR_STRING"),
        ("admitted_key", ["raw_subevent_integer"]),
        ("boolean_is_integer", True),
        ("non_integer_policy", "DROP"),
        ("runtime_label_matching", "ALLOWED"),
        ("string_policy", "PARSE"),
        ("taxonomy_sha256", "0" * 64),
        ("unknown_integer_policy", "GUESS"),
    ),
)
def test_action_subevent_transform_mutations_reject(field: str, value: object) -> None:
    decision, _, _, _ = _load_candidates()
    decision["decisions"][106]["transform"][field] = value
    with pytest.raises(ValueError):
        _validate_decision(decision)


@pytest.mark.parametrize("mutation", ("missing", "extra", "changed", "candidate-drift"))
def test_prior_authority_mutations_reject(mutation: str) -> None:
    decision, decision_raw, registry, _ = _load_candidates()
    if mutation == "missing":
        del decision["prior_authority"]["acceptance_sha256"]
    elif mutation == "extra":
        decision["prior_authority"]["unknown"] = None
    elif mutation == "changed":
        decision["prior_authority"]["review_recommendation"] = "REWORK"
    else:
        registry["prior_authority"]["candidate_sha256"] = "0" * 64
        with pytest.raises(ValueError):
            _validate_registry(registry, decision, decision_raw)
        return
    with pytest.raises(ValueError):
        _validate_decision(decision)


@pytest.mark.parametrize(
    "mutation",
    ("omitted", "extra", "duplicate", "reordered", "wrong-count"),
)
def test_roster_mutations_reject(mutation: str) -> None:
    decision, _, _, _ = _load_candidates()
    rows = decision["decisions"]
    if mutation == "omitted":
        rows.pop()
    elif mutation == "extra":
        extra = deepcopy(rows[-1])
        extra["json_path"] = "$.unexpected"
        rows.append(extra)
    elif mutation == "duplicate":
        rows[-1] = deepcopy(rows[0])
    elif mutation == "reordered":
        rows[0], rows[1] = rows[1], rows[0]
    else:
        rows[0]["record_kind"] = "team"
    with pytest.raises(ValueError):
        _validate_decision(decision)


def test_source_shape_mutation_rejects() -> None:
    decision, _, _, _ = _load_candidates()
    decision["decisions"][0]["source_shape"][0]["count"] += 1
    with pytest.raises(ValueError, match="source shape mismatch"):
        _validate_decision(decision)


@pytest.mark.parametrize("mutation", ("fifth", "changed"))
def test_bound_input_mutations_reject(mutation: str) -> None:
    decision, _, _, _ = _load_candidates()
    if mutation == "fifth":
        decision["bound_inputs"]["review_sha256"] = "0" * 64
    else:
        decision["bound_inputs"]["completion_manifest_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="fixed decision authority"):
        _validate_decision(decision)


def test_unknown_decision_rejects() -> None:
    decision, _, _, _ = _load_candidates()
    decision["decisions"][0]["decision"] = "INFER"
    with pytest.raises(ValueError, match="unknown decision"):
        _validate_decision(decision)


def test_unknown_source_support_rejects() -> None:
    decision, _, _, _ = _load_candidates()
    decision["decisions"][0]["source_support"] = "PROFILE_AND_LABEL"
    with pytest.raises(ValueError, match="unknown source support"):
        _validate_decision(decision)


@pytest.mark.parametrize("mutation", ("unknown-kind", "cross-kind-key", "illegal-null"))
def test_transform_union_mutations_reject(mutation: str) -> None:
    decision, _, _, _ = _load_candidates()
    row = next(row for row in decision["decisions"] if row["decision"] == "TRANSFORM")
    if mutation == "unknown-kind":
        row["transform"] = {"kind": "COERCE"}
    elif mutation == "cross-kind-key":
        row["transform"]["precision"] = 22
    else:
        row["canonical_field"] = None
    with pytest.raises(ValueError):
        _validate_decision(decision)


def test_non_transform_illegal_non_null_rejects() -> None:
    decision, _, _, _ = _load_candidates()
    row = next(row for row in decision["decisions"] if row["decision"] != "TRANSFORM")
    row["transform"] = {"kind": "COPY_EXACT"}
    with pytest.raises(ValueError, match="exact nulls"):
        _validate_decision(decision)


def test_unknown_policy_rejects() -> None:
    decision, _, _, _ = _load_candidates()
    decision["policies"]["unknown_field_policy"] = "COPY"
    with pytest.raises(ValueError, match="fixed decision authority"):
        _validate_decision(decision)


@pytest.mark.parametrize(
    "actor",
    (
        "not-a-uuid",
        "4EFE5691-8903-5148-8275-30D2E7E8AED0",
        "4efe5691-8903-4148-8275-30d2e7e8aed0",
        "00000000-0000-5000-8000-000000000000",
    ),
)
def test_invalid_noncanonical_or_wrong_actor_rejects(actor: str) -> None:
    decision, _, _, _ = _load_candidates()
    decision["decided_by"] = actor
    with pytest.raises(ValueError):
        _validate_decision(decision)


@pytest.mark.parametrize(
    "clock",
    (
        "2026-07-30T12:00:00.1Z",
        "2026-07-30T12:00:00+00:00",
        "2026-02-30T12:00:00Z",
        "2026-07-29T23:59:59Z",
        "9999-12-31T23:59:59Z",
    ),
)
def test_false_noncanonical_backdated_or_future_clock_rejects(clock: str) -> None:
    decision, _, _, _ = _load_candidates()
    decision["decided_at"] = clock
    with pytest.raises(ValueError):
        _validate_decision(decision)


@pytest.mark.parametrize(
    "raw_builder",
    (
        lambda value: json.dumps(value, indent=2, sort_keys=True).encode() + b"\n",
        lambda value: b"\xef\xbb\xbf" + _canonical_json_bytes(value),
        lambda value: _canonical_json_bytes(value) + b"\n",
    ),
    ids=("pretty", "bom", "extra-newline"),
)
def test_noncanonical_json_rejects(raw_builder: object) -> None:
    decision, _, _, _ = _load_candidates()
    with pytest.raises(ValueError):
        _load_canonical_json(raw_builder(decision))


def test_duplicate_json_key_rejects() -> None:
    with pytest.raises(ValueError):
        _load_canonical_json(b'{"a":1,"a":2}\n')


def test_noncanonical_yaml_rejects() -> None:
    raw = REGISTRY_PATH.read_bytes()
    with pytest.raises(ValueError, match="noncanonical YAML"):
        _load_strict_yaml(b"---\n" + raw)


@pytest.mark.parametrize(
    "raw",
    (
        b"a: &anchor value\n",
        b"a: &anchor value\nb: *anchor\n",
        b"a: !!str value\n",
        b"a:\n  '<<': {}\n",
        b"a: 1\na: 2\n",
        b"1: value\n",
        b"a: 2026-07-30\n",
        b"a: 1.5\n",
    ),
    ids=(
        "anchor",
        "alias",
        "tag",
        "merge",
        "duplicate",
        "non-string-key",
        "implicit-timestamp",
        "float",
    ),
)
def test_unsafe_yaml_classes_reject(raw: bytes) -> None:
    with pytest.raises(ValueError):
        _load_strict_yaml(raw, require_canonical=False)


def test_digest_mismatch_and_physical_yaml_substitution_reject() -> None:
    decision, decision_raw, registry, registry_raw = _load_candidates()
    registry["decision_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="decision digest mismatch"):
        _validate_registry(registry, decision, decision_raw)
    registry["decision_sha256"] = sha256(registry_raw).hexdigest()
    with pytest.raises(ValueError, match="decision digest mismatch"):
        _validate_registry(registry, decision, decision_raw)


def test_canonical_field_collision_rejects() -> None:
    decision, _, _, _ = _load_candidates()
    transformed = [row for row in decision["decisions"] if row["decision"] == "TRANSFORM"]
    transformed[1]["canonical_field"] = transformed[0]["canonical_field"]
    with pytest.raises(ValueError, match="canonical-field collision"):
        _validate_decision(decision)


@pytest.mark.parametrize(
    "claim_key",
    ("review_id", "acceptance_id", "dependency_id", "bronze_ready"),
)
def test_premature_review_acceptance_dependency_or_bronze_claim_rejects(
    claim_key: str,
) -> None:
    decision, _, _, _ = _load_candidates()
    decision[claim_key] = "premature"
    with pytest.raises(ValueError, match="decision keys differ"):
        _validate_decision(decision)


def test_actual_authority_progression_state_is_strict_and_progression_safe() -> None:
    review_raw = REVIEW_PATH.read_bytes() if REVIEW_PATH.exists() else None
    acceptance_raw = ACCEPTANCE_PATH.read_bytes() if ACCEPTANCE_PATH.exists() else None
    downstream_paths_present = any(path.exists() for path in DOWNSTREAM_PATHS)
    if downstream_paths_present:
        _validate_exact_r21_gate_evidence(_present_r21_gate_evidence())
    _validate_authority_state(
        review_raw,
        acceptance_raw,
        downstream_paths_present=False,
    )


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


def test_absent_review_and_acceptance_are_valid_before_separate_packets() -> None:
    assert (
        _validate_authority_state(
            None,
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )
        == "DECISION_ONLY"
    )


@pytest.mark.parametrize("recommendation", ("PASS", "REWORK"))
def test_valid_review_states_are_admitted_without_acceptance(recommendation: str) -> None:
    review = _valid_review_record(recommendation=recommendation)
    assert (
        _validate_authority_state(
            _review_markdown(review),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )
        == f"REVIEW_{recommendation}"
    )


def test_valid_acceptance_lifts_only_this_field_authority_block() -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance_raw = _canonical_json_bytes(_valid_acceptance_record(review, review_raw))
    assert (
        _validate_authority_state(
            review_raw,
            acceptance_raw,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )
        == "ACCEPTED"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("candidate_id", "wrong-registry"),
        ("candidate_physical_sha256", "0" * 64),
        ("candidate_sha256", "0" * 64),
        ("decision_id", "wrong-decision"),
        ("decision_physical_sha256", "0" * 64),
        ("decision_sha256", "0" * 64),
        ("review_id", "wrong-review"),
        ("review_schema_version", "wrong-schema"),
        ("reviewed_by", MASTER_ACTOR_ID),
        ("reviewed_by", "not-a-uuid"),
        ("reviewed_by", "03A65770-02F6-5EB0-9BD2-E2EBB44B62BD"),
        ("reviewed_at", "2026-07-30T20:22:15Z"),
        ("reviewed_at", "2026-07-30T14:10:47.1Z"),
        ("reviewed_at", "2026-07-30T14:10:47+00:00"),
        ("reviewed_at", "2026-02-30T14:10:47Z"),
        ("reviewed_at", "9999-12-31T23:59:59Z"),
    ),
)
def test_review_authority_mutations_reject(field: str, value: object) -> None:
    review = _valid_review_record()
    review[field] = value
    with pytest.raises(ValueError):
        _validate_authority_state(
            _review_markdown(review),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "unknown-key",
        "missing-key",
        "physical-canonical-substitution",
        "canonical-physical-substitution",
    ),
)
def test_review_shape_and_digest_substitution_mutations_reject(mutation: str) -> None:
    review = _valid_review_record()
    if mutation == "unknown-key":
        review["unknown"] = None
    elif mutation == "missing-key":
        del review["review_id"]
    elif mutation == "physical-canonical-substitution":
        review["candidate_physical_sha256"] = review["candidate_sha256"]
    else:
        review["candidate_sha256"] = review["candidate_physical_sha256"]
    with pytest.raises(ValueError):
        _validate_authority_state(
            _review_markdown(review),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "pass-with-findings",
        "rework-without-findings",
        "unknown-recommendation",
        "findings-not-array",
        "finding-unknown-key",
        "finding-missing-key",
        "bad-code",
        "bad-severity",
        "empty-summary",
        "long-summary",
        "non-nfc-summary",
    ),
)
def test_review_findings_and_recommendation_mutations_reject(mutation: str) -> None:
    review = _valid_review_record()
    finding = {
        "code": "AUTHORITY_DEFECT",
        "severity": "P1",
        "summary": "A bounded authority defect remains.",
    }
    if mutation == "pass-with-findings":
        review["findings"] = [finding]
    elif mutation == "rework-without-findings":
        review["recommendation"] = "REWORK"
    elif mutation == "unknown-recommendation":
        review["recommendation"] = "APPROVE"
    elif mutation == "findings-not-array":
        review["findings"] = {}
    else:
        review["recommendation"] = "REWORK"
        review["findings"] = [finding]
        if mutation == "finding-unknown-key":
            finding["unknown"] = None
        elif mutation == "finding-missing-key":
            del finding["severity"]
        elif mutation == "bad-code":
            finding["code"] = "lowercase"
        elif mutation == "bad-severity":
            finding["severity"] = "P3"
        elif mutation == "empty-summary":
            finding["summary"] = ""
        elif mutation == "long-summary":
            finding["summary"] = "x" * 2001
        else:
            finding["summary"] = "e\u0301"
    with pytest.raises(ValueError):
        _validate_authority_state(
            _review_markdown(review),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "raw_builder",
    (
        lambda raw: b"\xef\xbb\xbf" + raw,
        lambda raw: raw.replace(
            b"```w04-authority-review-v1\n",
            b"```text\n",
            1,
        ),
        lambda raw: raw.replace(b"```\n\nEnd", b"\n```\n\nEnd", 1),
        lambda raw: raw.replace(b"```\n\nEnd", b"\n{}\n```\n\nEnd", 1),
        lambda raw: raw + b"\n```text\nsecond block\n```\n",
        lambda raw: raw.replace(b"```\n\nEnd of review.\n", b"", 1),
    ),
    ids=(
        "bom",
        "wrong-info-string",
        "extra-body-lf",
        "second-json-record",
        "second-fenced-block",
        "unclosed-fence",
    ),
)
def test_malformed_or_second_review_fence_rejects(raw_builder: object) -> None:
    raw = _review_markdown(_valid_review_record())
    with pytest.raises(ValueError):
        _validate_authority_state(
            raw_builder(raw),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("acceptance_id", "wrong-acceptance"),
        ("acceptance_schema_version", "wrong-schema"),
        ("accepted_by", INDEPENDENT_REVIEWER_ACTOR_ID),
        ("accepted_by", "not-a-uuid"),
        ("accepted_by", "00000000-0000-5000-8000-000000000000"),
        ("accepted_at", "2026-07-30T20:22:16Z"),
        ("accepted_at", "2026-07-30T14:10:48.1Z"),
        ("accepted_at", "2026-07-30T14:10:48+00:00"),
        ("accepted_at", "2026-02-30T14:10:48Z"),
        ("accepted_at", "9999-12-31T23:59:59Z"),
        ("candidate_id", "wrong-registry"),
        ("candidate_physical_sha256", "0" * 64),
        ("candidate_sha256", "0" * 64),
        ("decision_id", "wrong-decision"),
        ("decision_physical_sha256", "0" * 64),
        ("decision_sha256", "0" * 64),
        ("review_id", "wrong-review"),
        ("review_physical_sha256", "0" * 64),
        ("review_record_sha256", "0" * 64),
        ("review_recommendation", "REWORK"),
        ("supersedes_acceptance_id", "prior-acceptance"),
    ),
)
def test_acceptance_authority_mutations_reject(field: str, value: object) -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance = _valid_acceptance_record(review, review_raw)
    acceptance[field] = value
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            _canonical_json_bytes(acceptance),
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "unknown-key",
        "missing-key",
        "candidate-physical-canonical-substitution",
        "candidate-canonical-physical-substitution",
        "review-physical-canonical-substitution",
        "review-canonical-physical-substitution",
    ),
)
def test_acceptance_shape_and_digest_substitution_mutations_reject(mutation: str) -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance = _valid_acceptance_record(review, review_raw)
    if mutation == "unknown-key":
        acceptance["unknown"] = None
    elif mutation == "missing-key":
        del acceptance["acceptance_id"]
    elif mutation == "candidate-physical-canonical-substitution":
        acceptance["candidate_physical_sha256"] = acceptance["candidate_sha256"]
    elif mutation == "candidate-canonical-physical-substitution":
        acceptance["candidate_sha256"] = acceptance["candidate_physical_sha256"]
    elif mutation == "review-physical-canonical-substitution":
        acceptance["review_physical_sha256"] = acceptance["review_record_sha256"]
    else:
        acceptance["review_record_sha256"] = acceptance["review_physical_sha256"]
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            _canonical_json_bytes(acceptance),
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


def test_acceptance_without_review_or_after_rework_rejects() -> None:
    pass_review = _valid_review_record()
    pass_review_raw = _review_markdown(pass_review)
    acceptance_raw = _canonical_json_bytes(_valid_acceptance_record(pass_review, pass_review_raw))
    with pytest.raises(ValueError, match="present valid review"):
        _validate_authority_state(
            None,
            acceptance_raw,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )
    rework_review = _valid_review_record(recommendation="REWORK")
    rework_raw = _review_markdown(rework_review)
    with pytest.raises(ValueError):
        _validate_authority_state(
            rework_raw,
            acceptance_raw,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "raw_builder",
    (
        lambda value: json.dumps(value, indent=2, sort_keys=True).encode() + b"\n",
        lambda value: b"\xef\xbb\xbf" + _canonical_json_bytes(value),
        lambda value: _canonical_json_bytes(value) + b"\n",
    ),
    ids=("pretty", "bom", "extra-newline"),
)
def test_noncanonical_acceptance_rejects(raw_builder: object) -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance = _valid_acceptance_record(review, review_raw)
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            raw_builder(acceptance),
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )


@pytest.mark.parametrize("state", ("absent", "pass-review", "rework-review", "malformed"))
def test_downstream_paths_remain_blocked_without_valid_acceptance(state: str) -> None:
    review_raw: bytes | None = None
    acceptance_raw: bytes | None = None
    if state in {"pass-review", "rework-review"}:
        review_raw = _review_markdown(
            _valid_review_record(recommendation="PASS" if state == "pass-review" else "REWORK")
        )
    elif state == "malformed":
        acceptance_raw = b"{}\n"
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            acceptance_raw,
            downstream_paths_present=True,
            now=datetime(2026, 7, 30, 21, tzinfo=UTC),
        )

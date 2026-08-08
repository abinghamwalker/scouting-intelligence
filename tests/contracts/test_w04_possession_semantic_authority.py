"""Contract for the closed, progression-safe W04 possession-semantic authority."""

from __future__ import annotations

import csv
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
EVENT_TAXONOMY_PATH = ROOT / "data/source/wyscout/v5/objects/eventid2name.csv"
TAG_TAXONOMY_PATH = ROOT / "data/source/wyscout/v5/objects/tags2name.csv"
DECISION_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json"
)
TAXONOMY_PATH = ROOT / "configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml"
REVIEW_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md"
)
ACCEPTANCE_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json"
)

SOURCE_ID = "wyscout-soccer-match-events-figshare-v5"
DECISION_ID = "w04-wyscout-possession-semantic-decisions-v1"
TAXONOMY_ID = "w04-wyscout-possession-taxonomy-v1"
REVIEW_ID = "w04-wyscout-possession-semantic-independent-review-R1"
ACCEPTANCE_ID = "w04-wyscout-possession-semantic-acceptance-v1"
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
TEST_REVIEWER_ACTOR_ID = "03a65770-02f6-5eb0-9bd2-e2ebb44b62bd"
EXPECTED_DECISION_SHA256 = "4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71"
EXPECTED_INPUTS = {
    "event_taxonomy_source_sha256": (
        "ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842"
    ),
    "field_acceptance_sha256": ("fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365"),
    "field_registry_canonical_sha256": (
        "fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034"
    ),
    "field_registry_id": "w04-wyscout-field-registry-v1",
    "tag_taxonomy_source_sha256": (
        "e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922"
    ),
}
EXPECTED_POLICIES = {
    "dead_ball_attachment": "PRECEDING_RESOLVED_POSSESSION_OR_UNASSIGNED",
    "period_boundary_policy": "CLOSE",
    "provider_native_possession_claim": False,
    "runtime_label_matching": "FORBIDDEN",
    "simultaneous_cross_team_policy": "UNCERTAIN_BOUNDARY",
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
    "source_id",
}
TAXONOMY_KEYS = {
    "bound_inputs",
    "decision_id",
    "decision_sha256",
    "policies",
    "predicates",
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
VALID_COMBINATIONS = {
    ("CONTROL", "ACTION_TEAM", True, False, None, None),
    ("RESTART", "ACTION_TEAM", True, True, None, None),
    (
        "DEAD_BALL",
        "NONE",
        False,
        True,
        "PRECEDING_RESOLVED_POSSESSION",
        None,
    ),
    ("DEAD_BALL", "NONE", False, True, "UNASSIGNED", None),
    (
        "CONTESTED",
        "NONE",
        False,
        False,
        None,
        "PRECEDING_RESOLVED_POSSESSION",
    ),
    (
        "CONTESTED",
        "NONE",
        False,
        False,
        None,
        "BUFFER_UNTIL_FOLLOWING_RESOLVED_POSSESSION",
    ),
    ("CONTESTED", "NONE", False, False, None, "UNASSIGNED"),
    ("NON_CONTROL_ADMIN", "NONE", False, False, None, None),
    ("UNMAPPED", "NONE", False, False, None, None),
}
EXPECTED_DISTRIBUTION = {
    "CONTESTED": 4,
    "CONTROL": 11,
    "DEAD_BALL": 8,
    "NON_CONTROL_ADMIN": 2,
    "RESTART": 7,
    "UNMAPPED": 4,
}
EXPECTED_DECISIONS = {
    **{(1, subevent): "CONTESTED" for subevent in range(10, 14)},
    (2, 20): "DEAD_BALL",
    (2, 21): "DEAD_BALL",
    (2, 22): "DEAD_BALL",
    (2, 23): "DEAD_BALL",
    (2, 24): "NON_CONTROL_ADMIN",
    (2, 25): "UNMAPPED",
    (2, 26): "NON_CONTROL_ADMIN",
    (2, 27): "DEAD_BALL",
    **{(3, subevent): "RESTART" for subevent in range(30, 37)},
    (4, 40): "UNMAPPED",
    (5, 50): "DEAD_BALL",
    (5, 51): "DEAD_BALL",
    (6, 60): "DEAD_BALL",
    **{(7, subevent): "CONTROL" for subevent in range(70, 73)},
    **{(8, subevent): "CONTROL" for subevent in range(80, 87)},
    (9, 90): "UNMAPPED",
    (9, 91): "UNMAPPED",
    (10, 100): "CONTROL",
}
UTC_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{6})?Z\Z"
)
FINDING_CODE_RE = re.compile(r"[A-Z][A-Z0-9_]{1,63}\Z")
DOWNSTREAM_PATHS = (
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
    if not isinstance(node, MappingNode):
        raise ValueError("mapping node required")
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
            ensure_ascii=False,
            allow_nan=False,
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


def _read_event_pairs() -> list[tuple[int, int]]:
    raw = EVENT_TAXONOMY_PATH.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED_INPUTS["event_taxonomy_source_sha256"]:
        raise ValueError("event taxonomy digest changed")
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if not rows or tuple(rows[0]) != (
        "event",
        "subevent",
        "event_label",
        "subevent_label",
    ):
        raise ValueError("event taxonomy header changed")
    pairs: list[tuple[int, int]] = []
    for row in rows:
        if not row["event"].isascii() or not row["event"].isdigit():
            raise ValueError("event ID must be decimal")
        if not row["subevent"].isascii() or not row["subevent"].isdigit():
            raise ValueError("subevent ID must be decimal")
        pairs.append((int(row["event"]), int(row["subevent"])))
    if len(pairs) != 36 or len(set(pairs)) != 36:
        raise ValueError("event taxonomy must contain 36 unique pairs")
    return pairs


def _read_tag_ids() -> set[int]:
    raw = TAG_TAXONOMY_PATH.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED_INPUTS["tag_taxonomy_source_sha256"]:
        raise ValueError("tag taxonomy digest changed")
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if not rows or tuple(rows[0]) != ("Tag", "Label", "Description"):
        raise ValueError("tag taxonomy header changed")
    values = [row["Tag"] for row in rows]
    if any(not value.isascii() or not value.isdigit() for value in values):
        raise ValueError("tag IDs must be decimal")
    tag_ids = {int(value) for value in values}
    if len(values) != 59 or len(tag_ids) != 59:
        raise ValueError("tag taxonomy must contain 59 unique IDs")
    return tag_ids


def _selector_key(predicate: dict[str, object]) -> tuple[object, ...]:
    subevent = predicate["subevent_id"]
    return (
        predicate["event_id"],
        1 if subevent is None else 0,
        -1 if subevent is None else subevent,
        tuple(predicate["required_tag_ids"]),
        tuple(predicate["forbidden_tag_ids"]),
    )


def _predicates_overlap(
    left: dict[str, object],
    right: dict[str, object],
) -> bool:
    if left["event_id"] != right["event_id"]:
        return False
    left_sub = left["subevent_id"]
    right_sub = right["subevent_id"]
    if left_sub is not None and right_sub is not None and left_sub != right_sub:
        return False
    left_required = set(left["required_tag_ids"])
    right_required = set(right["required_tag_ids"])
    left_forbidden = set(left["forbidden_tag_ids"])
    right_forbidden = set(right["forbidden_tag_ids"])
    return not (left_required & right_forbidden or right_required & left_forbidden)


def _validate_predicate(
    value: object,
    *,
    actor: str,
    tag_ids: set[int],
) -> dict[str, object]:
    predicate = _require_exact_keys(value, PREDICATE_KEYS, "predicate")
    for key in ("event_id",):
        if type(predicate[key]) is not int or predicate[key] < 0:
            raise ValueError(f"{key} must be a nonnegative integer")
    subevent = predicate["subevent_id"]
    if subevent is not None and (type(subevent) is not int or subevent < 0):
        raise ValueError("subevent_id must be null or nonnegative integer")
    for key in ("opens_control", "closes_control"):
        if type(predicate[key]) is not bool:
            raise ValueError(f"{key} must be boolean")
    for key in ("required_tag_ids", "forbidden_tag_ids"):
        values = predicate[key]
        if (
            not isinstance(values, list)
            or any(type(item) is not int or item < 0 for item in values)
            or values != sorted(set(values))
            or not set(values) <= tag_ids
        ):
            raise ValueError(f"invalid {key}")
    if set(predicate["required_tag_ids"]) & set(predicate["forbidden_tag_ids"]):
        raise ValueError("required and forbidden tags overlap")
    if _validate_actor(predicate["decided_by"], "predicate") != actor:
        raise ValueError("predicate actor differs")
    rationale = predicate["rationale"]
    if (
        not isinstance(rationale, str)
        or not 1 <= len(rationale) <= 2000
        or unicodedata.normalize("NFC", rationale) != rationale
    ):
        raise ValueError("invalid rationale")
    combination = (
        predicate["decision"],
        predicate["control_team_source"],
        predicate["opens_control"],
        predicate["closes_control"],
        predicate["dead_ball_attachment"],
        predicate["contested_attachment"],
    )
    if combination not in VALID_COMBINATIONS:
        raise ValueError("invalid possession combination")
    return predicate


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
        or decision["decision_schema_version"] != "w04-possession-semantic-decision-v1"
        or decision["policies"] != EXPECTED_POLICIES
        or decision["source_id"] != SOURCE_ID
    ):
        raise ValueError("decision authority differs")
    actor = _validate_actor(decision["decided_by"], "decision")
    if actor != MASTER_ACTOR_ID:
        raise ValueError("decision actor differs")
    decided_at = _parse_canonical_utc(decision["decided_at"])
    current_time = datetime.now(UTC) if now is None else now
    if decided_at > current_time + timedelta(minutes=5):
        raise ValueError("future decision clock")
    values = decision["predicates"]
    if not isinstance(values, list):
        raise ValueError("predicates must be an array")
    predicates = [
        _validate_predicate(value, actor=actor, tag_ids=_read_tag_ids()) for value in values
    ]
    if predicates != sorted(predicates, key=_selector_key):
        raise ValueError("predicates are not sorted")
    for index, left in enumerate(predicates):
        for right in predicates[index + 1 :]:
            if _predicates_overlap(left, right):
                raise ValueError("predicates overlap")
    exact_pairs = [(predicate["event_id"], predicate["subevent_id"]) for predicate in predicates]
    if exact_pairs != _read_event_pairs():
        raise ValueError("predicate pair coverage differs from frozen CSV")


def _load_candidates() -> tuple[dict[str, object], bytes, dict[str, object], bytes]:
    decision_raw = DECISION_PATH.read_bytes()
    taxonomy_raw = TAXONOMY_PATH.read_bytes()
    return (
        _load_canonical_json(decision_raw),
        decision_raw,
        _load_strict_yaml(taxonomy_raw),
        taxonomy_raw,
    )


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
        or taxonomy["taxonomy_id"] != TAXONOMY_ID
        or taxonomy["taxonomy_schema_version"] != "w04-possession-taxonomy-v1"
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
    fence_indexes = [
        index
        for index, line in enumerate(lines)
        if re.match(r" {0,3}(?:`{3,}|~{3,})", line) is not None
    ]
    if len(fence_indexes) != 2:
        raise ValueError("review requires one fence")
    opening, closing = fence_indexes
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
            or unicodedata.normalize("NFC", finding["summary"]) != finding["summary"]
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
        or acceptance["supersedes_acceptance_id"] is not None
        or review["recommendation"] != "PASS"
        or review["findings"]
    ):
        raise ValueError("acceptance authority differs")
    if _validate_actor(acceptance["accepted_by"], "acceptance") != decision["decided_by"]:
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
    downstream_paths_present: bool,
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
    if downstream_paths_present:
        raise ValueError("downstream outputs require valid acceptance")
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
        "reviewed_at": "2026-07-30T16:13:00Z",
        "reviewed_by": TEST_REVIEWER_ACTOR_ID,
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
    decision, decision_raw, taxonomy, taxonomy_raw = _load_candidates()
    return {
        "acceptance_id": ACCEPTANCE_ID,
        "acceptance_schema_version": "w04-authority-acceptance-v1",
        "accepted_at": "2026-07-30T16:13:01Z",
        "accepted_by": MASTER_ACTOR_ID,
        "candidate_id": TAXONOMY_ID,
        **_candidate_digests(decision_raw, taxonomy, taxonomy_raw),
        "decision_id": DECISION_ID,
        "review_id": REVIEW_ID,
        "review_physical_sha256": sha256(review_raw).hexdigest(),
        "review_record_sha256": sha256(_canonical_json_bytes(review)).hexdigest(),
        "review_recommendation": "PASS",
        "supersedes_acceptance_id": None,
    }


def _mutated_decision() -> dict[str, object]:
    return deepcopy(_load_candidates()[0])


def test_frozen_taxonomies_reproduce_complete_selector_universes() -> None:
    assert len(_read_event_pairs()) == 36
    assert len(_read_tag_ids()) == 59


def test_decision_and_taxonomy_are_closed_digest_linked_authorities() -> None:
    decision, decision_raw, taxonomy, taxonomy_raw = _load_candidates()
    assert sha256(decision_raw).hexdigest() == EXPECTED_DECISION_SHA256
    assert decision_raw == _canonical_json_bytes(decision)
    assert taxonomy_raw == _canonical_yaml_bytes(taxonomy)
    _validate_decision(decision)
    _validate_taxonomy(taxonomy, decision, decision_raw)


def test_all_36_pairs_have_exact_project_owned_decisions() -> None:
    decision = _load_candidates()[0]
    actual = {
        (row["event_id"], row["subevent_id"]): row["decision"] for row in decision["predicates"]
    }
    distribution = {
        name: list(actual.values()).count(name) for name in sorted(set(actual.values()))
    }
    assert actual == EXPECTED_DECISIONS
    assert distribution == EXPECTED_DISTRIBUTION
    assert all(
        not row["required_tag_ids"] and not row["forbidden_tag_ids"]
        for row in decision["predicates"]
    )
    assert all(
        "not provider-native possession truth" in row["rationale"] for row in decision["predicates"]
    )


def test_dead_ball_and_contested_attachments_are_explicit() -> None:
    decision = _load_candidates()[0]
    rows = {(row["event_id"], row["subevent_id"]): row for row in decision["predicates"]}
    assert all(
        rows[(1, subevent)]["contested_attachment"] == "BUFFER_UNTIL_FOLLOWING_RESOLVED_POSSESSION"
        for subevent in range(10, 14)
    )
    assert rows[(2, 23)]["dead_ball_attachment"] == "UNASSIGNED"
    assert rows[(5, 51)]["dead_ball_attachment"] == "UNASSIGNED"
    preceding_pairs = {(2, 20), (2, 21), (2, 22), (2, 27), (5, 50), (6, 60)}
    assert all(
        rows[pair]["dead_ball_attachment"] == "PRECEDING_RESOLVED_POSSESSION"
        for pair in preceding_pairs
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("authority_class", "FIELD"),
        ("decision_id", "wrong"),
        ("decision_schema_version", "wrong"),
        ("source_id", "wrong"),
        ("decided_by", TEST_REVIEWER_ACTOR_ID),
        ("decided_by", "not-a-uuid"),
        ("decided_at", "2026-07-30T16:12:58+00:00"),
    ),
)
def test_decision_authority_mutations_reject(field: str, value: object) -> None:
    decision = _mutated_decision()
    decision[field] = value
    with pytest.raises(ValueError):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))


@pytest.mark.parametrize("mutation", ("extra", "missing", "input", "policy", "claim"))
def test_closed_decision_shape_and_policy_mutations_reject(mutation: str) -> None:
    decision = _mutated_decision()
    if mutation == "extra":
        decision["label_lookup"] = True
    elif mutation == "missing":
        del decision["authority_class"]
    elif mutation == "input":
        decision["bound_inputs"]["event_taxonomy_source_sha256"] = "0" * 64
    elif mutation == "policy":
        decision["policies"]["unknown_name_matching"] = "ALLOWED"
    else:
        decision["policies"]["provider_native_possession_claim"] = True
    with pytest.raises(ValueError):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("event_id", True),
        ("event_id", -1),
        ("subevent_id", "10"),
        ("opens_control", 1),
        ("closes_control", 0),
        ("required_tag_ids", [703, 703]),
        ("required_tag_ids", [999999]),
        ("forbidden_tag_ids", [703, 701]),
        ("rationale", ""),
        ("rationale", "e\u0301"),
        ("decided_by", TEST_REVIEWER_ACTOR_ID),
        ("decision", "UNKNOWN"),
        ("control_team_source", "OPPONENT"),
    ),
)
def test_predicate_field_and_type_mutations_reject(field: str, value: object) -> None:
    decision = _mutated_decision()
    decision["predicates"][0][field] = value
    with pytest.raises(ValueError):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))


@pytest.mark.parametrize(
    "field",
    (
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
    ),
)
def test_every_missing_predicate_field_rejects(field: str) -> None:
    decision = _mutated_decision()
    del decision["predicates"][0][field]
    with pytest.raises(ValueError):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))


@pytest.mark.parametrize(
    ("decision_name", "field", "value"),
    (
        ("CONTROL", "closes_control", True),
        ("CONTROL", "control_team_source", "NONE"),
        ("RESTART", "opens_control", False),
        ("RESTART", "dead_ball_attachment", "UNASSIGNED"),
        ("DEAD_BALL", "opens_control", True),
        ("DEAD_BALL", "dead_ball_attachment", None),
        ("CONTESTED", "closes_control", True),
        ("CONTESTED", "contested_attachment", None),
        ("NON_CONTROL_ADMIN", "control_team_source", "ACTION_TEAM"),
        ("UNMAPPED", "contested_attachment", "UNASSIGNED"),
    ),
)
def test_invalid_combination_union_mutations_reject(
    decision_name: str,
    field: str,
    value: object,
) -> None:
    decision = _mutated_decision()
    row = next(item for item in decision["predicates"] if item["decision"] == decision_name)
    row[field] = value
    with pytest.raises(ValueError):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))


def test_missing_duplicate_reordered_and_overlapping_predicates_reject() -> None:
    decision = _mutated_decision()
    del decision["predicates"][-1]
    with pytest.raises(ValueError, match="coverage"):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))
    decision = _mutated_decision()
    decision["predicates"].insert(1, deepcopy(decision["predicates"][0]))
    with pytest.raises(ValueError, match="overlap"):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))
    decision = _mutated_decision()
    decision["predicates"][0], decision["predicates"][1] = (
        decision["predicates"][1],
        decision["predicates"][0],
    )
    with pytest.raises(ValueError, match="sorted"):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))
    decision = _mutated_decision()
    duplicate = deepcopy(decision["predicates"][0])
    decision["predicates"][0]["forbidden_tag_ids"] = [701]
    duplicate["required_tag_ids"] = [703]
    decision["predicates"].insert(1, duplicate)
    with pytest.raises(ValueError, match="overlap"):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))


def test_required_and_forbidden_tag_intersection_rejects() -> None:
    decision = _mutated_decision()
    decision["predicates"][0]["required_tag_ids"] = [703]
    decision["predicates"][0]["forbidden_tag_ids"] = [703]
    with pytest.raises(ValueError, match="overlap"):
        _validate_decision(decision, now=datetime(2026, 7, 30, 17, tzinfo=UTC))


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


def test_taxonomy_mutations_and_digest_substitution_reject() -> None:
    decision, decision_raw, taxonomy, _ = _load_candidates()
    mutation = deepcopy(taxonomy)
    mutation["predicates"][0]["rationale"] = "changed"
    with pytest.raises(ValueError):
        _validate_taxonomy(mutation, decision, decision_raw)
    mutation = deepcopy(taxonomy)
    mutation["decision_sha256"] = sha256(_canonical_json_bytes(taxonomy)).hexdigest()
    with pytest.raises(ValueError):
        _validate_taxonomy(mutation, decision, decision_raw)
    mutation = deepcopy(taxonomy)
    mutation["label_lookup"] = "FORBIDDEN"
    with pytest.raises(ValueError):
        _validate_taxonomy(mutation, decision, decision_raw)


def test_noncanonical_and_duplicate_decision_json_rejects() -> None:
    decision = _load_candidates()[0]
    with pytest.raises(ValueError):
        _load_canonical_json(json.dumps(decision, indent=2, sort_keys=True).encode() + b"\n")
    raw = DECISION_PATH.read_bytes().replace(
        b'{"authority_class":"POSSESSION",',
        b'{"authority_class":"POSSESSION","authority_class":"POSSESSION",',
        1,
    )
    with pytest.raises(ValueError):
        _load_canonical_json(raw)


def test_actual_authority_progression_state_is_strict_and_progression_safe() -> None:
    review_raw = REVIEW_PATH.read_bytes() if REVIEW_PATH.exists() else None
    acceptance_raw = ACCEPTANCE_PATH.read_bytes() if ACCEPTANCE_PATH.exists() else None
    _validate_authority_state(
        review_raw,
        acceptance_raw,
        downstream_paths_present=any(path.exists() for path in DOWNSTREAM_PATHS),
        now=datetime.now(UTC),
    )


def test_absent_review_and_acceptance_are_valid_before_separate_packets() -> None:
    assert (
        _validate_authority_state(
            None,
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )
        == "DECISION_ONLY"
    )


@pytest.mark.parametrize("recommendation", ("PASS", "REWORK"))
def test_valid_review_states_are_admitted(recommendation: str) -> None:
    review = _valid_review_record(recommendation=recommendation)
    assert (
        _validate_authority_state(
            _review_markdown(review),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )
        == f"REVIEW_{recommendation}"
    )


def test_valid_acceptance_lifts_only_this_possession_authority_block() -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance_raw = _canonical_json_bytes(_valid_acceptance_record(review, review_raw))
    assert (
        _validate_authority_state(
            review_raw,
            acceptance_raw,
            downstream_paths_present=True,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )
        == "ACCEPTED"
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
        ("review_schema_version", "wrong"),
        ("reviewed_by", MASTER_ACTOR_ID),
        ("reviewed_by", "not-a-uuid"),
        ("reviewed_at", "2026-07-30T16:12:57Z"),
        ("reviewed_at", "2026-07-30T16:13:00+00:00"),
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
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "pass-findings",
        "rework-empty",
        "unknown-recommendation",
        "finding-code",
        "finding-severity",
        "finding-summary",
        "finding-shape",
    ),
)
def test_review_findings_mutations_reject(mutation: str) -> None:
    review = _valid_review_record(recommendation="REWORK")
    finding = review["findings"][0]
    if mutation == "pass-findings":
        review["recommendation"] = "PASS"
    elif mutation == "rework-empty":
        review["findings"] = []
    elif mutation == "unknown-recommendation":
        review["recommendation"] = "APPROVE"
    elif mutation == "finding-code":
        finding["code"] = "bad"
    elif mutation == "finding-severity":
        finding["severity"] = "P3"
    elif mutation == "finding-summary":
        finding["summary"] = ""
    else:
        finding["extra"] = None
    with pytest.raises(ValueError):
        _validate_authority_state(
            _review_markdown(review),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "raw_builder",
    (
        lambda raw: b"\xef\xbb\xbf" + raw,
        lambda raw: raw.replace(b"```w04-authority-review-v1\n", b"```text\n", 1),
        lambda raw: raw + b"\n```text\nsecond\n```\n",
        lambda raw: raw.replace(b"```\n\nEnd", b"\n{}\n```\n\nEnd", 1),
    ),
)
def test_malformed_review_markdown_rejects(raw_builder: object) -> None:
    with pytest.raises(ValueError):
        _validate_authority_state(
            raw_builder(_review_markdown(_valid_review_record())),
            None,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("acceptance_id", "wrong"),
        ("acceptance_schema_version", "wrong"),
        ("accepted_at", "2026-07-30T16:12:59Z"),
        ("accepted_at", "2026-07-30T16:13:01+00:00"),
        ("accepted_by", TEST_REVIEWER_ACTOR_ID),
        ("candidate_id", "wrong"),
        ("candidate_physical_sha256", "0" * 64),
        ("candidate_sha256", "0" * 64),
        ("decision_id", "wrong"),
        ("decision_physical_sha256", "0" * 64),
        ("decision_sha256", "0" * 64),
        ("review_id", "wrong"),
        ("review_physical_sha256", "0" * 64),
        ("review_record_sha256", "0" * 64),
        ("review_recommendation", "REWORK"),
        ("supersedes_acceptance_id", "prior"),
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
            downstream_paths_present=True,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )


def test_acceptance_without_review_or_after_rework_rejects() -> None:
    review = _valid_review_record()
    review_raw = _review_markdown(review)
    acceptance_raw = _canonical_json_bytes(_valid_acceptance_record(review, review_raw))
    with pytest.raises(ValueError, match="valid review"):
        _validate_authority_state(
            None,
            acceptance_raw,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )
    rework = _valid_review_record(recommendation="REWORK")
    with pytest.raises(ValueError):
        _validate_authority_state(
            _review_markdown(rework),
            acceptance_raw,
            downstream_paths_present=False,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )


@pytest.mark.parametrize("state", ("absent", "pass", "rework", "malformed"))
def test_downstream_paths_remain_blocked_without_valid_acceptance(state: str) -> None:
    review_raw: bytes | None = None
    acceptance_raw: bytes | None = None
    if state in {"pass", "rework"}:
        review_raw = _review_markdown(
            _valid_review_record(recommendation="PASS" if state == "pass" else "REWORK")
        )
    elif state == "malformed":
        acceptance_raw = b"{}\n"
    with pytest.raises(ValueError):
        _validate_authority_state(
            review_raw,
            acceptance_raw,
            downstream_paths_present=True,
            now=datetime(2026, 7, 30, 17, tzinfo=UTC),
        )

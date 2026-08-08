"""Closed authority tests for the W04 Wyscout identity v1 route."""

from __future__ import annotations

import json
import re
import unicodedata
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
import yaml  # type: ignore[import-untyped]
from yaml.nodes import MappingNode  # type: ignore[import-untyped]
from yaml.tokens import (  # type: ignore[import-untyped]
    AliasToken,
    AnchorToken,
    DirectiveToken,
    TagToken,
)

ROOT = Path(__file__).resolve().parents[2]
AUTHORITIES = ROOT / "reports/reviews/W04/authorities"
DECISION_PATH = AUTHORITIES / "wyscout-identity-ruleset-decisions-v1.json"
RULESET_PATH = ROOT / "configs/schema/wyscout-v5-identity-ruleset-v1.yaml"
REVIEW_PATH = AUTHORITIES / "wyscout-identity-ruleset-independent-review-R1.md"
ACCEPTANCE_PATH = AUTHORITIES / "wyscout-identity-ruleset-acceptance-v1.json"
SOURCE_MANIFEST_PATH = (
    ROOT
    / "data/manifests/wyscout/v5/source"
    / "4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json"
)
COMPLETION_PATH = ROOT / "data/source/wyscout/v5/completion-manifest.json"
FIELD_REGISTRY_PATH = ROOT / "configs/schema/wyscout-v5-field-registry-v2.yaml"
FIELD_ACCEPTANCE_PATH = AUTHORITIES / "wyscout-field-semantic-acceptance-v2.json"

SOURCE_ID = "wyscout-soccer-match-events-figshare-v5"
DECISION_ID = "w04-wyscout-identity-ruleset-decisions-v1"
RULESET_ID = "w04-wyscout-identity-ruleset-v1"
REVIEW_ID = "w04-wyscout-identity-ruleset-independent-review-R1"
ACCEPTANCE_ID = "w04-wyscout-identity-ruleset-acceptance-v1"
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
TEST_REVIEWER_ACTOR_ID = "169765e6-2e8f-530d-b833-9d3b4463b9f0"
AUTHORITY_CLOCK_FUTURE_TOLERANCE = timedelta(minutes=5)

EXPECTED_DECISION_SHA256 = "6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192"
EXPECTED_RULESET_PHYSICAL_SHA256 = (
    "8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547"
)
EXPECTED_RULESET_CANONICAL_SHA256 = (
    "9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c"
)
EXPECTED_INPUTS = {
    "completion_manifest_sha256": (
        "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
    ),
    "field_acceptance_sha256": ("beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436"),
    "field_registry_canonical_sha256": (
        "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959"
    ),
    "field_registry_id": "w04-wyscout-field-registry-v2",
    "source_manifest_id": "4e16bdb5-afe7-5601-88ad-adc124cfce3b",
    "source_manifest_sha256": ("8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"),
}
EXPECTED_RULES = [
    {
        "canonical_namespace_name": (
            "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5:competition"
        ),
        "entity_kind": "COMPETITION",
        "identity_source_path": "competition_source_id",
        "malformed_policy": "REVIEW_REQUIRED",
        "missing_policy": "REVIEW_REQUIRED",
        "nonzero_absent_master_policy": "REVIEW_REQUIRED",
        "source_id_type": "STRICT_DECIMAL_INTEGER",
        "zero_policy": "REVIEW_REQUIRED",
    },
    {
        "canonical_namespace_name": (
            "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5:team"
        ),
        "entity_kind": "TEAM",
        "identity_source_path": "team_source_id",
        "malformed_policy": "REVIEW_REQUIRED",
        "missing_policy": "REVIEW_REQUIRED",
        "nonzero_absent_master_policy": "REVIEW_REQUIRED",
        "source_id_type": "STRICT_DECIMAL_INTEGER",
        "zero_policy": "REVIEW_REQUIRED",
    },
    {
        "canonical_namespace_name": (
            "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5:player"
        ),
        "entity_kind": "PLAYER",
        "identity_source_path": "player_source_id",
        "malformed_policy": "REVIEW_REQUIRED",
        "missing_policy": "REVIEW_REQUIRED",
        "nonzero_absent_master_policy": "REVIEW_REQUIRED",
        "source_id_type": "STRICT_DECIMAL_INTEGER",
        "zero_policy": "REJECT",
    },
    {
        "canonical_namespace_name": (
            "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5:match"
        ),
        "entity_kind": "MATCH",
        "identity_source_path": "match_source_id",
        "malformed_policy": "REVIEW_REQUIRED",
        "missing_policy": "REVIEW_REQUIRED",
        "nonzero_absent_master_policy": "REVIEW_REQUIRED",
        "source_id_type": "STRICT_DECIMAL_INTEGER",
        "zero_policy": "REVIEW_REQUIRED",
    },
]
EXPECTED_POLICIES = {
    "canonical_id_algorithm": "UUIDV5_SOURCE_KIND_AND_CANONICAL_DECIMAL_ID",
    "cross_kind_collision_policy": "FAIL",
    "duplicate_source_key_policy": "REVIEW_REQUIRED",
    "name_only_matching": "FORBIDDEN",
    "review_queue_policy": "EXACT_UNRESOLVED_NONZERO_REFERENCES",
    "source_key_resolution": "DETERMINISTIC_WHEN_UNIQUE_VALID_MASTER_ROW",
    "version_policy": "CONSECUTIVE_FROM_ONE",
}

DECISION_KEYS = {
    "authority_class",
    "bound_inputs",
    "decided_at",
    "decided_by",
    "decision_id",
    "decision_schema_version",
    "entity_rules",
    "policies",
    "source_id",
}
RULESET_KEYS = {
    "bound_inputs",
    "decision_id",
    "decision_sha256",
    "entity_rules",
    "policies",
    "ruleset_id",
    "ruleset_schema_version",
}
RULE_KEYS = {
    "canonical_namespace_name",
    "entity_kind",
    "identity_source_path",
    "malformed_policy",
    "missing_policy",
    "nonzero_absent_master_policy",
    "source_id_type",
    "zero_policy",
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
UUID_WIRE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
UTC_WIRE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{6})?Z$")


class _UniqueSafeLoader(yaml.SafeLoader):  # type: ignore[misc]
    """Safe YAML loader that rejects duplicate keys."""


def _construct_unique_mapping(
    loader: _UniqueSafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError("YAML mapping keys must be strings")
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _assert_nfc_tree(value: object) -> None:
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non-NFC string")
        return
    if isinstance(value, list):
        for item in value:
            _assert_nfc_tree(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_nfc_tree(key)
            _assert_nfc_tree(item)
        return
    if value is not None and type(value) not in {bool, int}:
        raise ValueError("unsupported authority scalar")


def _canonical_json_bytes(value: object) -> bytes:
    _assert_nfc_tree(value)
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    ).encode()


def _duplicate_rejecting_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_canonical_json(raw: bytes) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("invalid JSON encoding")
    value = json.loads(raw, object_pairs_hook=_duplicate_rejecting_object)
    if type(value) is not dict or raw != _canonical_json_bytes(value):
        raise ValueError("noncanonical JSON")
    return value


def _load_strict_yaml(raw: bytes, *, require_canonical: bool = True) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("invalid YAML encoding")
    tokens = tuple(yaml.scan(raw))
    if any(
        isinstance(token, (AliasToken, AnchorToken, DirectiveToken, TagToken)) for token in tokens
    ):
        raise ValueError("unsafe YAML feature")
    documents = list(yaml.load_all(raw, Loader=_UniqueSafeLoader))
    if len(documents) != 1 or type(documents[0]) is not dict:
        raise ValueError("YAML must be one mapping document")
    value = documents[0]
    _assert_nfc_tree(value)
    if require_canonical:
        rendered = yaml.safe_dump(
            value,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=True,
            width=4096,
        ).encode()
        if raw != rendered:
            raise ValueError("noncanonical YAML")
    return value


def _parse_canonical_utc(value: object) -> datetime:
    if not isinstance(value, str) or UTC_WIRE.fullmatch(value) is None:
        raise ValueError("noncanonical UTC")
    try:
        parsed = datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError as exc:
        raise ValueError("noncanonical UTC") from exc
    timespec = "microseconds" if "." in value else "seconds"
    if parsed.isoformat(timespec=timespec).replace("+00:00", "Z") != value:
        raise ValueError("noncanonical UTC")
    return parsed


def _parse_truthful_authority_clock(value: object, context: str) -> datetime:
    parsed = _parse_canonical_utc(value)
    if parsed > datetime.now(UTC) + AUTHORITY_CLOCK_FUTURE_TOLERANCE:
        raise ValueError(f"future {context} clock")
    return parsed


def _validate_actor(value: object, *, expected: str | None = None) -> str:
    if not isinstance(value, str) or UUID_WIRE.fullmatch(value) is None:
        raise ValueError("invalid actor wire value")
    parsed = UUID(value)
    if str(parsed) != value or parsed.variant != "specified in RFC 4122":
        raise ValueError("invalid actor UUID")
    if expected is not None and value != expected:
        raise ValueError("unexpected actor")
    return value


def _require_keys(value: object, expected: set[str], context: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != expected:
        raise ValueError(f"{context} keys differ")
    return value


def _upstream_inputs() -> dict[str, str]:
    source_raw = SOURCE_MANIFEST_PATH.read_bytes()
    source = json.loads(source_raw)
    if (
        type(source) is not dict
        or not source_raw.endswith(b"\n")
        or sha256(source_raw).hexdigest() != EXPECTED_INPUTS["source_manifest_sha256"]
        or source["manifest_id"] != EXPECTED_INPUTS["source_manifest_id"]
        or sha256(COMPLETION_PATH.read_bytes()).hexdigest()
        != EXPECTED_INPUTS["completion_manifest_sha256"]
    ):
        raise ValueError("source authority differs")

    field = _load_strict_yaml(
        FIELD_REGISTRY_PATH.read_bytes(),
        require_canonical=False,
    )
    if (
        field["registry_id"] != EXPECTED_INPUTS["field_registry_id"]
        or sha256(_canonical_json_bytes(field)).hexdigest()
        != EXPECTED_INPUTS["field_registry_canonical_sha256"]
        or sha256(FIELD_ACCEPTANCE_PATH.read_bytes()).hexdigest()
        != EXPECTED_INPUTS["field_acceptance_sha256"]
    ):
        raise ValueError("field v2 authority differs")
    return deepcopy(EXPECTED_INPUTS)


def _validate_decision(value: object) -> dict[str, object]:
    decision = _require_keys(value, DECISION_KEYS, "decision")
    if (
        decision["authority_class"] != "IDENTITY"
        or decision["bound_inputs"] != EXPECTED_INPUTS
        or decision["decision_id"] != DECISION_ID
        or decision["decision_schema_version"] != "w04-identity-ruleset-decision-v1"
        or decision["entity_rules"] != EXPECTED_RULES
        or decision["policies"] != EXPECTED_POLICIES
        or decision["source_id"] != SOURCE_ID
    ):
        raise ValueError("decision authority differs")
    _validate_actor(decision["decided_by"], expected=MASTER_ACTOR_ID)
    _parse_truthful_authority_clock(decision["decided_at"], "decision")
    for rule in decision["entity_rules"]:
        _require_keys(rule, RULE_KEYS, "entity rule")
    return decision


def _validate_ruleset(
    value: object,
    decision: dict[str, object],
    decision_raw: bytes,
) -> dict[str, object]:
    ruleset = _require_keys(value, RULESET_KEYS, "ruleset")
    if (
        ruleset["bound_inputs"] != decision["bound_inputs"]
        or ruleset["decision_id"] != decision["decision_id"]
        or ruleset["decision_sha256"] != sha256(decision_raw).hexdigest()
        or ruleset["entity_rules"] != decision["entity_rules"]
        or ruleset["policies"] != decision["policies"]
        or ruleset["ruleset_id"] != RULESET_ID
        or ruleset["ruleset_schema_version"] != "w04-identity-ruleset-v1"
    ):
        raise ValueError("ruleset is not the exact decision restatement")
    return ruleset


def _load_candidate() -> tuple[dict[str, object], bytes, dict[str, object], bytes]:
    _upstream_inputs()
    decision_raw = DECISION_PATH.read_bytes()
    decision = _validate_decision(_load_canonical_json(decision_raw))
    ruleset_raw = RULESET_PATH.read_bytes()
    ruleset = _validate_ruleset(_load_strict_yaml(ruleset_raw), decision, decision_raw)
    return decision, decision_raw, ruleset, ruleset_raw


def _candidate_digests(
    decision_raw: bytes,
    ruleset: dict[str, object],
    ruleset_raw: bytes,
) -> dict[str, str]:
    return {
        "candidate_physical_sha256": sha256(ruleset_raw).hexdigest(),
        "candidate_sha256": sha256(_canonical_json_bytes(ruleset)).hexdigest(),
        "decision_physical_sha256": sha256(decision_raw).hexdigest(),
        "decision_sha256": sha256(decision_raw).hexdigest(),
    }


def _load_review_markdown(raw: bytes) -> tuple[dict[str, object], bytes]:
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("invalid review Markdown encoding")
    marker = b"```w04-authority-review-v1\n"
    if raw.count(b"```") != 2 or raw.count(marker) != 1:
        raise ValueError("review requires exactly one authority fence")
    body = raw.split(marker, maxsplit=1)[1].split(b"```\n", maxsplit=1)[0]
    record = _load_canonical_json(body)
    return record, body


def _validate_review(
    raw: bytes,
    decision: dict[str, object],
    expected_digests: dict[str, str],
) -> tuple[dict[str, object], bytes]:
    review, record_raw = _load_review_markdown(raw)
    _require_keys(review, REVIEW_KEYS, "review")
    if (
        review["candidate_id"] != RULESET_ID
        or review["decision_id"] != DECISION_ID
        or review["review_id"] != REVIEW_ID
        or review["review_schema_version"] != "w04-authority-independent-review-v1"
        or any(review[key] != digest for key, digest in expected_digests.items())
    ):
        raise ValueError("review authority differs")
    reviewer = _validate_actor(review["reviewed_by"])
    if reviewer == decision["decided_by"]:
        raise ValueError("self-review is forbidden")
    reviewed_at = _parse_truthful_authority_clock(review["reviewed_at"], "review")
    if reviewed_at < _parse_canonical_utc(decision["decided_at"]):
        raise ValueError("review predates decision")
    findings = review["findings"]
    recommendation = review["recommendation"]
    if type(findings) is not list:
        raise ValueError("findings must be an array")
    for finding in findings:
        row = _require_keys(finding, {"code", "severity", "summary"}, "finding")
        if (
            not isinstance(row["code"], str)
            or re.fullmatch(r"[A-Z][A-Z0-9_]{1,63}", row["code"]) is None
            or row["severity"] not in {"P0", "P1", "P2"}
            or not isinstance(row["summary"], str)
            or not 1 <= len(row["summary"]) <= 2000
        ):
            raise ValueError("invalid finding")
    if (recommendation == "PASS" and findings) or (recommendation == "REWORK" and not findings):
        raise ValueError("review recommendation and findings disagree")
    if recommendation not in {"PASS", "REWORK"}:
        raise ValueError("unknown review recommendation")
    return review, record_raw


def _validate_acceptance(
    raw: bytes,
    decision: dict[str, object],
    review: dict[str, object],
    review_raw: bytes,
    review_record_raw: bytes,
    expected_digests: dict[str, str],
) -> dict[str, object]:
    acceptance = _load_canonical_json(raw)
    _require_keys(acceptance, ACCEPTANCE_KEYS, "acceptance")
    if (
        acceptance["acceptance_id"] != ACCEPTANCE_ID
        or acceptance["acceptance_schema_version"] != "w04-authority-acceptance-v1"
        or acceptance["candidate_id"] != RULESET_ID
        or acceptance["decision_id"] != DECISION_ID
        or acceptance["review_id"] != REVIEW_ID
        or any(acceptance[key] != digest for key, digest in expected_digests.items())
        or acceptance["review_physical_sha256"] != sha256(review_raw).hexdigest()
        or acceptance["review_record_sha256"] != sha256(review_record_raw).hexdigest()
        or acceptance["review_recommendation"] != "PASS"
        or acceptance["supersedes_acceptance_id"] is not None
    ):
        raise ValueError("acceptance authority differs")
    accepted_by = _validate_actor(acceptance["accepted_by"], expected=MASTER_ACTOR_ID)
    if accepted_by == review["reviewed_by"] or review["recommendation"] != "PASS":
        raise ValueError("acceptance requires independent PASS")
    decided_at = _parse_canonical_utc(decision["decided_at"])
    reviewed_at = _parse_canonical_utc(review["reviewed_at"])
    accepted_at = _parse_truthful_authority_clock(acceptance["accepted_at"], "acceptance")
    if not decided_at <= reviewed_at <= accepted_at:
        raise ValueError("acceptance clock order differs")
    return acceptance


def _authority_state(
    review_raw: bytes | None,
    acceptance_raw: bytes | None,
) -> str:
    decision, decision_raw, ruleset, ruleset_raw = _load_candidate()
    digests = _candidate_digests(decision_raw, ruleset, ruleset_raw)
    if review_raw is None:
        if acceptance_raw is not None:
            raise ValueError("acceptance cannot precede review")
        return "CANDIDATE"
    review, record_raw = _validate_review(review_raw, decision, digests)
    if acceptance_raw is None:
        return "REVIEW_PASS" if review["recommendation"] == "PASS" else "REVIEW_REWORK"
    _validate_acceptance(
        acceptance_raw,
        decision,
        review,
        review_raw,
        record_raw,
        digests,
    )
    return "ACCEPTED"


def _canonical_identity(entity_kind: str, source_id: object) -> UUID:
    if type(source_id) is not int or source_id < 0:
        raise ValueError("source identity requires a strict nonnegative integer")
    rule = next(row for row in EXPECTED_RULES if row["entity_kind"] == entity_kind)
    if source_id == 0:
        if rule["zero_policy"] == "REJECT":
            raise ValueError("player zero is rejected")
        raise LookupError("zero identity requires review")
    source_namespace = uuid5(
        NAMESPACE_URL,
        "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5",
    )
    kind_namespace = uuid5(source_namespace, entity_kind.lower())
    return uuid5(kind_namespace, f"figshare-v5:{source_id}")


def _resolve_identity(
    entity_kind: str,
    source_id: object,
    master_source_ids: list[object],
) -> tuple[str, UUID | None]:
    if type(source_id) is not int or source_id < 0:
        return "REVIEW_REQUIRED", None
    if source_id == 0 and entity_kind == "PLAYER":
        return "REJECT", None
    matches = sum(
        type(value) is int and value > 0 and value == source_id for value in master_source_ids
    )
    if source_id == 0 or matches != 1:
        return "REVIEW_REQUIRED", None
    return "RESOLVED", _canonical_identity(entity_kind, source_id)


def _valid_review_record(
    decision_raw: bytes,
    ruleset: dict[str, object],
    ruleset_raw: bytes,
    *,
    recommendation: str = "PASS",
) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    if recommendation == "REWORK":
        findings = [{"code": "IDENTITY_TEST", "severity": "P1", "summary": "test finding"}]
    return {
        "candidate_id": RULESET_ID,
        **_candidate_digests(decision_raw, ruleset, ruleset_raw),
        "decision_id": DECISION_ID,
        "findings": findings,
        "recommendation": recommendation,
        "review_id": REVIEW_ID,
        "review_schema_version": "w04-authority-independent-review-v1",
        "reviewed_at": "2026-07-31T12:50:00Z",
        "reviewed_by": TEST_REVIEWER_ACTOR_ID,
    }


def _review_markdown(record: dict[str, object]) -> bytes:
    return (
        b"Independent identity authority review.\n\n```w04-authority-review-v1\n"
        + _canonical_json_bytes(record)
        + b"```\n\nEnd of review.\n"
    )


def _valid_acceptance(
    review: dict[str, object],
    review_raw: bytes,
    review_record_raw: bytes,
) -> bytes:
    decision, decision_raw, ruleset, ruleset_raw = _load_candidate()
    return _canonical_json_bytes(
        {
            "acceptance_id": ACCEPTANCE_ID,
            "acceptance_schema_version": "w04-authority-acceptance-v1",
            "accepted_at": "2026-07-31T12:51:00Z",
            "accepted_by": MASTER_ACTOR_ID,
            "candidate_id": RULESET_ID,
            **_candidate_digests(decision_raw, ruleset, ruleset_raw),
            "decision_id": DECISION_ID,
            "review_id": REVIEW_ID,
            "review_physical_sha256": sha256(review_raw).hexdigest(),
            "review_record_sha256": sha256(review_record_raw).hexdigest(),
            "review_recommendation": review["recommendation"],
            "supersedes_acceptance_id": None,
        }
    )


def test_candidate_is_exact_canonical_and_binds_upstream_authorities() -> None:
    decision, decision_raw, ruleset, ruleset_raw = _load_candidate()
    assert sha256(decision_raw).hexdigest() == EXPECTED_DECISION_SHA256
    assert sha256(ruleset_raw).hexdigest() == EXPECTED_RULESET_PHYSICAL_SHA256
    assert sha256(_canonical_json_bytes(ruleset)).hexdigest() == EXPECTED_RULESET_CANONICAL_SHA256
    assert decision["bound_inputs"] == _upstream_inputs()


@pytest.mark.parametrize("artifact", ["decision", "ruleset"])
def test_candidate_rejects_unknown_missing_and_mutated_values(artifact: str) -> None:
    decision, decision_raw, ruleset, _ = _load_candidate()
    target = deepcopy(decision if artifact == "decision" else ruleset)
    target["unknown"] = "value"
    with pytest.raises(ValueError, match="keys"):
        if artifact == "decision":
            _validate_decision(target)
        else:
            _validate_ruleset(target, decision, decision_raw)

    target = deepcopy(decision if artifact == "decision" else ruleset)
    target.pop("policies")
    with pytest.raises(ValueError, match="keys"):
        if artifact == "decision":
            _validate_decision(target)
        else:
            _validate_ruleset(target, decision, decision_raw)

    target = deepcopy(decision if artifact == "decision" else ruleset)
    target["bound_inputs"]["source_manifest_sha256"] = "0" * 64  # type: ignore[index]
    with pytest.raises(ValueError, match="differs|restatement"):
        if artifact == "decision":
            _validate_decision(target)
        else:
            _validate_ruleset(target, decision, decision_raw)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda rows: rows.reverse(),
        lambda rows: rows.pop(),
        lambda rows: rows.append(deepcopy(rows[-1])),
        lambda rows: rows[2].__setitem__("zero_policy", "REVIEW_REQUIRED"),
        lambda rows: rows[0].__setitem__("identity_source_path", "name"),
        lambda rows: rows[0].__setitem__("canonical_namespace_name", "urn:changed"),
        lambda rows: rows[0].__setitem__("source_id_type", "STRING"),
    ],
)
def test_entity_rule_mutations_fail_closed(mutation: Any) -> None:
    decision, _, _, _ = _load_candidate()
    mutated = deepcopy(decision)
    rows = mutated["entity_rules"]
    mutation(rows)
    with pytest.raises(ValueError, match="differs"):
        _validate_decision(mutated)


@pytest.mark.parametrize(
    ("entity_kind", "source_id", "master_ids", "state"),
    [
        ("PLAYER", 3319, [3319], "RESOLVED"),
        ("PLAYER", 0, [0], "REJECT"),
        ("PLAYER", "3319", [3319], "REVIEW_REQUIRED"),
        ("PLAYER", True, [1], "REVIEW_REQUIRED"),
        ("PLAYER", -1, [-1], "REVIEW_REQUIRED"),
        ("PLAYER", 3319, [], "REVIEW_REQUIRED"),
        ("PLAYER", 3319, [3319, 3319], "REVIEW_REQUIRED"),
        ("TEAM", 1609, [1609], "RESOLVED"),
        ("TEAM", 0, [0], "REVIEW_REQUIRED"),
    ],
)
def test_resolution_is_numeric_unique_and_fail_closed(
    entity_kind: str,
    source_id: object,
    master_ids: list[object],
    state: str,
) -> None:
    assert _resolve_identity(entity_kind, source_id, master_ids)[0] == state


@pytest.mark.parametrize(
    ("master_ids", "state"),
    [
        ([True], "REVIEW_REQUIRED"),
        ([1.0], "REVIEW_REQUIRED"),
        ([1.5], "REVIEW_REQUIRED"),
        (["player"], "REVIEW_REQUIRED"),
        (["1"], "REVIEW_REQUIRED"),
        ([-1], "REVIEW_REQUIRED"),
        ([0], "REVIEW_REQUIRED"),
        ([1, 1], "REVIEW_REQUIRED"),
        ([True, 1.0, 1.5, "player", "1", -1, 0, 1], "RESOLVED"),
        ([1], "RESOLVED"),
    ],
)
def test_master_identity_keys_are_strict_positive_and_unique(
    master_ids: list[object],
    state: str,
) -> None:
    resolved_state, canonical_id = _resolve_identity("PLAYER", 1, master_ids)
    assert resolved_state == state
    assert canonical_id == (_canonical_identity("PLAYER", 1) if state == "RESOLVED" else None)


def test_uuidv5_identity_derivation_is_exact_and_cross_kind_separated() -> None:
    assert str(_canonical_identity("COMPETITION", 364)) == ("cb5c5317-fa4a-571e-93dc-ef6ce482eab7")
    assert str(_canonical_identity("MATCH", 2499719)) == ("bad97950-6fac-5cf0-a93c-094f91abbb9b")
    assert _canonical_identity("TEAM", 1609) != _canonical_identity("PLAYER", 1609)
    with pytest.raises(ValueError, match="player zero"):
        _canonical_identity("PLAYER", 0)
    with pytest.raises(ValueError, match="strict"):
        _canonical_identity("PLAYER", "3319")


def test_name_only_and_duplicate_resolution_are_forbidden() -> None:
    _, _, ruleset, _ = _load_candidate()
    assert ruleset["policies"] == EXPECTED_POLICIES
    assert EXPECTED_POLICIES["name_only_matching"] == "FORBIDDEN"
    assert EXPECTED_POLICIES["duplicate_source_key_policy"] == "REVIEW_REQUIRED"


@pytest.mark.parametrize(
    "payload",
    [
        b"bound_inputs: &inputs {}\ncopy: *inputs\n",
        b"!!python/object/apply:os.system ['true']\n",
        b"ruleset_id: one\nruleset_id: two\n",
        b"--- {}\n--- {}\n",
    ],
)
def test_unsafe_or_duplicate_yaml_is_rejected(payload: bytes) -> None:
    with pytest.raises((ValueError, yaml.YAMLError)):
        _load_strict_yaml(payload)


def test_json_duplicate_key_and_noncanonical_rendering_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        _load_canonical_json(b'{"a":1,"a":1}\n')
    with pytest.raises(ValueError, match="noncanonical"):
        _load_canonical_json(b'{"a": 1}\n')


@pytest.mark.parametrize(
    "value",
    [
        "2026-07-31T12:50:00Z",
        "2026-07-31T12:50:00.000000Z",
        "2026-07-31T12:50:00.123456Z",
    ],
)
def test_canonical_utc_accepts_seconds_or_exactly_six_fraction_digits(value: str) -> None:
    parsed = _parse_canonical_utc(value)
    timespec = "microseconds" if "." in value else "seconds"
    assert parsed.isoformat(timespec=timespec).replace("+00:00", "Z") == value


@pytest.mark.parametrize(
    "value",
    [
        "2026-07-31T12:50:00.1Z",
        "2026-07-31T12:50:00.12345Z",
        "2026-07-31T12:50:00.1234567Z",
        "2026-07-31T12:50:00+00:00",
        "2026-02-30T12:50:00Z",
    ],
)
def test_canonical_utc_rejects_other_fractions_offsets_and_unreal_values(value: str) -> None:
    with pytest.raises(ValueError, match="noncanonical UTC"):
        _parse_canonical_utc(value)


def test_review_and_acceptance_progression_is_acyclic_and_separated() -> None:
    decision, decision_raw, ruleset, ruleset_raw = _load_candidate()
    digests = _candidate_digests(decision_raw, ruleset, ruleset_raw)
    record = _valid_review_record(decision_raw, ruleset, ruleset_raw)
    review_raw = _review_markdown(record)
    parsed_review, record_raw = _validate_review(review_raw, decision, digests)
    acceptance_raw = _valid_acceptance(parsed_review, review_raw, record_raw)
    assert _authority_state(None, None) == "CANDIDATE"
    assert _authority_state(review_raw, None) == "REVIEW_PASS"
    assert _authority_state(review_raw, acceptance_raw) == "ACCEPTED"

    rework_record = _valid_review_record(
        decision_raw,
        ruleset,
        ruleset_raw,
        recommendation="REWORK",
    )
    rework_raw = _review_markdown(rework_record)
    parsed_rework, rework_record_raw = _validate_review(rework_raw, decision, digests)
    assert _authority_state(rework_raw, None) == "REVIEW_REWORK"
    with pytest.raises(ValueError, match="acceptance authority differs"):
        _authority_state(
            rework_raw,
            _valid_acceptance(parsed_rework, rework_raw, rework_record_raw),
        )
    with pytest.raises(ValueError, match="precede review"):
        _authority_state(None, acceptance_raw)


def test_review_and_acceptance_reject_independent_far_future_clocks() -> None:
    decision, decision_raw, ruleset, ruleset_raw = _load_candidate()
    digests = _candidate_digests(decision_raw, ruleset, ruleset_raw)

    future_review_record = _valid_review_record(decision_raw, ruleset, ruleset_raw)
    future_review_record["reviewed_at"] = "9999-12-30T00:00:00Z"
    with pytest.raises(ValueError, match="future review clock"):
        _validate_review(_review_markdown(future_review_record), decision, digests)

    review_record = _valid_review_record(decision_raw, ruleset, ruleset_raw)
    review_raw = _review_markdown(review_record)
    review, review_record_raw = _validate_review(review_raw, decision, digests)
    acceptance = _load_canonical_json(_valid_acceptance(review, review_raw, review_record_raw))
    acceptance["accepted_at"] = "9999-12-31T00:00:00Z"
    with pytest.raises(ValueError, match="future acceptance clock"):
        _validate_acceptance(
            _canonical_json_bytes(acceptance),
            decision,
            review,
            review_raw,
            review_record_raw,
            digests,
        )


def test_review_rejects_self_review_findings_mismatch_and_candidate_drift() -> None:
    decision, decision_raw, ruleset, ruleset_raw = _load_candidate()
    digests = _candidate_digests(decision_raw, ruleset, ruleset_raw)

    record = _valid_review_record(decision_raw, ruleset, ruleset_raw)
    record["reviewed_by"] = MASTER_ACTOR_ID
    with pytest.raises(ValueError, match="self-review"):
        _validate_review(_review_markdown(record), decision, digests)

    record = _valid_review_record(decision_raw, ruleset, ruleset_raw)
    record["findings"] = [{"code": "BAD", "severity": "P1", "summary": "finding"}]
    with pytest.raises(ValueError, match="disagree"):
        _validate_review(_review_markdown(record), decision, digests)

    record = _valid_review_record(decision_raw, ruleset, ruleset_raw)
    record["candidate_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="differs"):
        _validate_review(_review_markdown(record), decision, digests)


def test_acceptance_rejects_rework_digest_drift_and_clock_inversion() -> None:
    decision, decision_raw, ruleset, ruleset_raw = _load_candidate()
    digests = _candidate_digests(decision_raw, ruleset, ruleset_raw)
    record = _valid_review_record(decision_raw, ruleset, ruleset_raw)
    review_raw = _review_markdown(record)
    review, record_raw = _validate_review(review_raw, decision, digests)
    acceptance = _load_canonical_json(_valid_acceptance(review, review_raw, record_raw))

    acceptance["review_recommendation"] = "REWORK"
    with pytest.raises(ValueError, match="differs"):
        _validate_acceptance(
            _canonical_json_bytes(acceptance),
            decision,
            review,
            review_raw,
            record_raw,
            digests,
        )

    acceptance = _load_canonical_json(_valid_acceptance(review, review_raw, record_raw))
    acceptance["review_physical_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="differs"):
        _validate_acceptance(
            _canonical_json_bytes(acceptance),
            decision,
            review,
            review_raw,
            record_raw,
            digests,
        )

    acceptance = _load_canonical_json(_valid_acceptance(review, review_raw, record_raw))
    acceptance["accepted_at"] = "2026-07-31T12:40:00Z"
    with pytest.raises(ValueError, match="clock"):
        _validate_acceptance(
            _canonical_json_bytes(acceptance),
            decision,
            review,
            review_raw,
            record_raw,
            digests,
        )


def test_live_authority_state_is_valid_without_overclaiming_progression() -> None:
    review_raw = REVIEW_PATH.read_bytes() if REVIEW_PATH.exists() else None
    acceptance_raw = ACCEPTANCE_PATH.read_bytes() if ACCEPTANCE_PATH.exists() else None
    if acceptance_raw is not None:
        expected = "ACCEPTED"
    elif review_raw is None:
        expected = "CANDIDATE"
    else:
        review, _ = _load_review_markdown(review_raw)
        expected = f"REVIEW_{review['recommendation']}"
    assert _authority_state(review_raw, acceptance_raw) == expected

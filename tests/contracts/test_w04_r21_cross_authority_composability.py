"""Executable cross-authority proof for the frozen W04 R21 correction."""

from __future__ import annotations

import json
import runpy
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIELD_CONTRACT = ROOT / "tests/contracts/test_w04_field_semantic_v2_authority.py"
POSSESSION_CONTRACT = ROOT / "tests/contracts/test_w04_possession_semantic_v2_authority.py"
FEATURE_CONTRACT = ROOT / "tests/contracts/test_w04_supported_feature_authority.py"
PREIMAGE_CONTRACT = ROOT / "tests/contracts/test_w04_r21_control_preimages.py"

TEST_PATH = ROOT / "tests/contracts/test_w04_r21_cross_authority_composability.py"
RETURN_PATH = ROOT / "reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R4.md"
REVIEW_PATH = (
    ROOT / "reports/reviews/W04/wyscout-r21-cross-authority-composability-independent-review-R1.md"
)
REVIEW_RETURN_PATH = ROOT / "reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-REVIEW-01-R1.md"
GATE_PATH = (
    ROOT / "reports/verification/W04/wyscout-r21-cross-authority-gate-R1-master-verification.md"
)
GATE_RECORD_PATH = ROOT / "reports/phase-gates/W04/wyscout-r21-correction-gate.json"
GATE_RETURN_PATH = ROOT / "reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-GATE-01-R1.md"

REVIEW_ID = "w04-wyscout-r21-cross-authority-composability-independent-review-R1"
TEST_PRODUCER_ID = "W04-R21-CROSS-AUTHORITY-TEST-01-R1:producer"
REVIEW_FENCE = "```w04-r21-cross-authority-review-v1\n"
REVIEW_RECORD_KEYS = frozenset(
    {
        "recommendation",
        "review_id",
        "review_path",
        "reviewed_by",
        "test_artifact_physical_sha256",
        "test_return_physical_sha256",
    }
)
GATE_RECORD_KEYS = frozenset(
    {
        "decision",
        "gate_path",
        "review_path",
        "review_physical_sha256",
        "review_recommendation",
    }
)
GATE_EVIDENCE_PATHS = frozenset(
    {
        str(GATE_PATH.relative_to(ROOT)),
        str(GATE_RECORD_PATH.relative_to(ROOT)),
        str(GATE_RETURN_PATH.relative_to(ROOT)),
    }
)
DEPENDENCY_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w04:wyscout:evidence-dependency:v1",
)

RESOURCE_PATHS = (
    "configs/schema/wyscout-v5-identity-ruleset-v1.yaml",
    "configs/schema/wyscout-v5-field-registry-v1.yaml",
    "configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml",
    "configs/features/wyscout-v5-supported-count-features-v1.yaml",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json",
    "reports/phase-gates/W04/source-schema-profile.md",
    "reports/reviews/W04/wyscout-schema-design-R21.md",
    "reports/reviews/W04/wyscout-schema-design-independent-review-R15.md",
    "configs/schema/wyscout-v5-product-contract-preimage-v1.json",
    "configs/schema/wyscout-v5-schema-bundle-preimage-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json",
    "configs/schema/wyscout-v5-field-registry-v2.yaml",
    "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-v2-R1.md",
    "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json",
    "configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json",
    "tests/contracts/test_w04_r21_cross_authority_composability.py",
)
V1_RESOURCE_PREFIX = RESOURCE_PATHS[:17]
RESOURCE_PATHS_SHA256 = "0a5a174f05114dc1d260720174f7459526fbbceba3f549200ad6510c243938c6"
FUTURE_IDENTITY_PATHS = frozenset(
    {
        RESOURCE_PATHS[0],
        RESOURCE_PATHS[4],
        RESOURCE_PATHS[5],
        RESOURCE_PATHS[6],
    }
)

V1_PRESENT_PHYSICAL_SHA256 = {
    RESOURCE_PATHS[1]: "805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2",
    RESOURCE_PATHS[2]: "e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d",
    RESOURCE_PATHS[3]: "8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95",
    RESOURCE_PATHS[7]: "e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999",
    RESOURCE_PATHS[8]: "e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861",
    RESOURCE_PATHS[9]: "fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365",
    RESOURCE_PATHS[10]: "4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71",
    RESOURCE_PATHS[11]: "1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4",
    RESOURCE_PATHS[12]: "f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112",
    RESOURCE_PATHS[13]: "bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941",
    RESOURCE_PATHS[14]: "a692cc4aaa002882f92209256f1bdecb96b3eb6bdba8a9bc3f645569daa31c73",
    RESOURCE_PATHS[15]: "d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c",
    RESOURCE_PATHS[16]: "569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649",
}

AUTHORITY_GRAPH_EDGES = frozenset(
    {
        ("R20", "R21"),
        ("R21", "PRODUCT_PREIMAGE"),
        ("R21", "SCHEMA_PREIMAGE"),
        ("PRODUCT_PREIMAGE", "FIELD_V2"),
        ("SCHEMA_PREIMAGE", "FIELD_V2"),
        ("FIELD_V2", "POSSESSION_V2"),
        ("POSSESSION_V2", "FEATURE_DECISION"),
        ("FEATURE_DECISION", "FEATURE_ACCEPTED"),
        ("FEATURE_ACCEPTED", "FIVE_DEPENDENCIES"),
        ("FIVE_DEPENDENCIES", "LATER_PRODUCT"),
    }
)

PACKET_WRITE_SCOPES = (
    frozenset({str(TEST_PATH.relative_to(ROOT)), str(RETURN_PATH.relative_to(ROOT))}),
    frozenset({str(REVIEW_PATH.relative_to(ROOT)), str(REVIEW_RETURN_PATH.relative_to(ROOT))}),
    frozenset(
        {
            str(GATE_PATH.relative_to(ROOT)),
            str(GATE_RECORD_PATH.relative_to(ROOT)),
            str(GATE_RETURN_PATH.relative_to(ROOT)),
        }
    ),
)


@pytest.fixture(scope="module")
def authorities() -> dict[str, dict[str, Any]]:
    return {
        "field": runpy.run_path(str(FIELD_CONTRACT)),
        "possession": runpy.run_path(str(POSSESSION_CONTRACT)),
        "feature": runpy.run_path(str(FEATURE_CONTRACT)),
        "preimage": runpy.run_path(str(PREIMAGE_CONTRACT)),
    }


def _canonical_json_bytes(value: object) -> bytes:
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


def _reject_json_constant(token: str) -> None:
    raise ValueError(token)


def _load_closed_canonical_json(raw: bytes, label: str) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{label} BOM is forbidden")
    try:
        text = raw.decode("utf-8")
        value = json.loads(text, parse_constant=_reject_json_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict canonical JSON") from exc
    if not isinstance(value, dict) or raw != _canonical_json_bytes(value):
        raise ValueError(f"{label} must be a closed canonical JSON object")
    return value


def _load_review_markdown(raw: bytes) -> tuple[dict[str, object], bytes]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("cross-authority review BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("cross-authority review is not UTF-8") from exc
    if "\r" in text:
        raise ValueError("cross-authority review requires LF line endings")
    lines = text.splitlines(keepends=True)
    fences = [index for index, line in enumerate(lines) if line.startswith(("```", "~~~"))]
    if len(fences) != 2:
        raise ValueError("cross-authority review requires exactly one machine fence")
    opening, closing = fences
    if (
        lines[opening] != REVIEW_FENCE
        or lines[closing] not in {"```\n", "```"}
        or closing <= opening
    ):
        raise ValueError("cross-authority review machine fence differs")
    record_raw = "".join(lines[opening + 1 : closing]).encode()
    return _load_closed_canonical_json(record_raw, "cross-authority review record"), record_raw


def _review_markdown(record: dict[str, object]) -> bytes:
    return (
        b"# W04 R21 cross-authority independent review\n\n"
        + REVIEW_FENCE.encode()
        + _canonical_json_bytes(record)
        + b"```\n"
    )


def _validate_resource_roster(paths: tuple[str, ...]) -> None:
    if paths != RESOURCE_PATHS or len(paths) != 30 or len(set(paths)) != 30:
        raise ValueError("R21 resource roster differs")
    if any(
        path.endswith("/")
        or "*" in path
        or path.startswith(("data/working/", "data/manifests/", "runs/"))
        or "/returns/" in path
        for path in paths
    ):
        raise ValueError("resource roster contains shorthand or generated/product evidence")


def _validate_authority_graph(edges: frozenset[tuple[str, str]]) -> None:
    if edges != AUTHORITY_GRAPH_EDGES:
        raise ValueError("R21 authority graph edges differ")
    nodes = {node for edge in edges for node in edge}
    incoming = {node: 0 for node in nodes}
    children = {node: set() for node in nodes}
    for parent, child in edges:
        if parent == child:
            raise ValueError("self edge")
        incoming[child] += 1
        children[parent].add(child)
    ready = [node for node, count in incoming.items() if count == 0]
    visited = 0
    while ready:
        node = ready.pop()
        visited += 1
        for child in children[node]:
            incoming[child] -= 1
            if incoming[child] == 0:
                ready.append(child)
    if visited != len(nodes):
        raise ValueError("authority graph contains a cycle")


def _validate_preimage_pair(
    product: dict[str, object],
    schema: dict[str, object],
    expected_product: dict[str, object],
    expected_schema: dict[str, object],
) -> None:
    if product != expected_product or schema != expected_schema:
        raise ValueError("preimage content differs")
    if schema["feature_schema_hash_placeholder"]["concrete_value"] is not None:
        raise ValueError("premature feature hash")
    descriptors = schema["descriptors"]
    if any(
        row["surface_kind"] != "CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA"
        or set(row) != {"depends_on", "descriptor_id", "descriptor_version", "role", "surface_kind"}
        for row in descriptors
    ):
        raise ValueError("descriptor overclaims implementation")


def _dependency_id(artifact_type: str, candidate_id: str, digest: str, acceptance: str) -> str:
    return str(
        uuid5(
            DEPENDENCY_NAMESPACE,
            f"feature_schema:{artifact_type}:{candidate_id}:{digest}:{acceptance}",
        )
    )


def _dependency_authority_plan(
    field_acceptance: dict[str, object],
    possession_acceptance: dict[str, object],
    feature_acceptance: dict[str, object],
) -> list[dict[str, object]]:
    plan: list[dict[str, object]] = [
        {"kind": "source_manifest", "state": "R20_UNCHANGED"},
        {"kind": "identity_evidence", "state": "FUTURE_ACCEPTED_BUNDLE_REQUIRED"},
    ]
    for artifact_type, acceptance in (
        ("field_registry", field_acceptance),
        ("possession_taxonomy", possession_acceptance),
        ("supported_feature_registry", feature_acceptance),
    ):
        candidate_id = acceptance["candidate_id"]
        digest = acceptance["candidate_sha256"]
        acceptance_digest = sha256(_canonical_json_bytes(acceptance)).hexdigest()
        plan.append(
            {
                "acceptance_sha256": acceptance_digest,
                "candidate_id": candidate_id,
                "dependency_id": _dependency_id(
                    artifact_type,
                    candidate_id,
                    digest,
                    acceptance_digest,
                ),
                "digest": digest,
                "kind": "feature_schema",
            }
        )
    return plan


def _validate_dependency_authority_plan(
    plan: list[dict[str, object]],
    expected: list[dict[str, object]],
) -> None:
    if plan != expected or len(plan) != 5:
        raise ValueError("five-dependency authority binding differs")
    feature_rows = plan[2:]
    if len({row["dependency_id"] for row in feature_rows}) != 3:
        raise ValueError("feature dependency IDs must be distinct")
    if any(UUID(str(row["dependency_id"])).version != 5 for row in feature_rows):
        raise ValueError("feature dependency ID must be UUIDv5")


def _validate_future_review_assertion(
    record: dict[str, object] | None,
    *,
    test_raw: bytes,
    return_raw: bytes,
    forbidden_reviewers: set[str],
) -> None:
    if record is None:
        raise ValueError("independent review is absent")
    if set(record) != REVIEW_RECORD_KEYS:
        raise ValueError("independent review machine record is not closed")
    expected = {
        "recommendation": "PASS",
        "review_id": REVIEW_ID,
        "review_path": str(REVIEW_PATH.relative_to(ROOT)),
        "test_artifact_physical_sha256": sha256(test_raw).hexdigest(),
        "test_return_physical_sha256": sha256(return_raw).hexdigest(),
    }
    if any(record.get(key) != value for key, value in expected.items()):
        raise ValueError("independent review binding differs")
    reviewer = record["reviewed_by"]
    if not isinstance(reviewer, str) or reviewer in forbidden_reviewers:
        raise ValueError("independent reviewer is missing or not distinct")
    try:
        canonical_reviewer = str(UUID(reviewer))
    except ValueError as exc:
        raise ValueError("independent reviewer is not a canonical UUID") from exc
    if reviewer != canonical_reviewer:
        raise ValueError("independent reviewer is not a canonical UUID")


def _validate_future_gate_assertion(
    gate: dict[str, object] | None,
    *,
    review_raw: bytes | None,
    review_recommendation: str | None,
) -> None:
    if gate is None or review_raw is None or review_recommendation != "PASS":
        raise ValueError("master gate requires a present passing independent review")
    if set(gate) != GATE_RECORD_KEYS or gate != {
        "decision": "PASS",
        "gate_path": str(GATE_PATH.relative_to(ROOT)),
        "review_path": str(REVIEW_PATH.relative_to(ROOT)),
        "review_physical_sha256": sha256(review_raw).hexdigest(),
        "review_recommendation": "PASS",
    }:
        raise ValueError("master gate binding differs")


def _validate_r21_lifecycle(
    *,
    review_raw: bytes | None,
    gate_record_raw: bytes | None,
    gate_evidence_paths: frozenset[str],
    product_paths: frozenset[str],
    test_raw: bytes,
    return_raw: bytes,
    forbidden_reviewers: set[str],
) -> str:
    if review_raw is None:
        if gate_record_raw is not None or gate_evidence_paths:
            raise ValueError("master gate cannot precede the independent review")
        if product_paths:
            raise ValueError("product paths require the complete R21 master gate")
        return "AWAITING_REVIEW"

    review, _ = _load_review_markdown(review_raw)
    _validate_future_review_assertion(
        review,
        test_raw=test_raw,
        return_raw=return_raw,
        forbidden_reviewers=forbidden_reviewers,
    )
    if gate_record_raw is None:
        if gate_evidence_paths:
            raise ValueError("master gate evidence is incomplete")
        if product_paths:
            raise ValueError("product paths require the complete R21 master gate")
        return "REVIEW_PASS"

    if gate_evidence_paths != GATE_EVIDENCE_PATHS:
        raise ValueError("master gate evidence is incomplete")
    gate = _load_closed_canonical_json(gate_record_raw, "R21 master gate record")
    _validate_future_gate_assertion(
        gate,
        review_raw=review_raw,
        review_recommendation=str(review["recommendation"]),
    )
    return "GATE_PASS_PRODUCT_PRESENT" if product_paths else "GATE_PASS"


def _forbidden_cross_authority_reviewers(
    authorities: dict[str, dict[str, Any]],
) -> set[str]:
    forbidden = {TEST_PRODUCER_ID}
    for authority in (authorities["field"], authorities["possession"], authorities["feature"]):
        decision = authority["_load_candidates"]()[0]
        review = authority["_load_review_markdown"](authority["REVIEW_PATH"].read_bytes())[0]
        acceptance = authority["_load_canonical_json"](authority["ACCEPTANCE_PATH"].read_bytes())
        forbidden.update(
            {
                str(decision["decided_by"]),
                str(review["reviewed_by"]),
                str(acceptance["accepted_by"]),
            }
        )
    return forbidden


def _synthetic_review_and_gate(
    authorities: dict[str, dict[str, Any]],
) -> tuple[bytes, bytes, bytes, bytes, set[str]]:
    test_raw = TEST_PATH.read_bytes()
    return_raw = RETURN_PATH.read_bytes()
    forbidden_reviewers = _forbidden_cross_authority_reviewers(authorities)
    reviewer = str(uuid5(NAMESPACE_URL, "w04-r21-independent-cross-authority-reviewer"))
    assert reviewer not in forbidden_reviewers
    review_record = {
        "recommendation": "PASS",
        "review_id": REVIEW_ID,
        "review_path": str(REVIEW_PATH.relative_to(ROOT)),
        "reviewed_by": reviewer,
        "test_artifact_physical_sha256": sha256(test_raw).hexdigest(),
        "test_return_physical_sha256": sha256(return_raw).hexdigest(),
    }
    review_raw = _review_markdown(review_record)
    gate_record = {
        "decision": "PASS",
        "gate_path": str(GATE_PATH.relative_to(ROOT)),
        "review_path": str(REVIEW_PATH.relative_to(ROOT)),
        "review_physical_sha256": sha256(review_raw).hexdigest(),
        "review_recommendation": "PASS",
    }
    return (
        review_raw,
        _canonical_json_bytes(gate_record),
        test_raw,
        return_raw,
        forbidden_reviewers,
    )


def _validate_serial_write_scopes(scopes: tuple[frozenset[str], ...]) -> None:
    if scopes != PACKET_WRITE_SCOPES:
        raise ValueError("test, review, and gate write scopes differ")
    if any(left & right for index, left in enumerate(scopes) for right in scopes[index + 1 :]):
        raise ValueError("test, review, and gate write scopes overlap")


def _validate_v1_physical_bytes(relative_path: str, raw: bytes) -> None:
    if sha256(raw).hexdigest() != V1_PRESENT_PHYSICAL_SHA256[relative_path]:
        raise ValueError("v1 physical bytes differ")


def _validate_feature_prerequisites(
    feature: dict[str, Any],
    *,
    field_acceptance_raw: bytes | None,
    possession_acceptance_raw: bytes | None,
    feature_review_raw: bytes | None,
    feature_acceptance_raw: bytes | None,
) -> None:
    if None in {
        field_acceptance_raw,
        possession_acceptance_raw,
        feature_review_raw,
        feature_acceptance_raw,
    }:
        raise ValueError("feature use requires both v2 acceptances and feature acceptance")
    expected = feature["EXPECTED_INPUTS"]
    if sha256(field_acceptance_raw).hexdigest() != expected["field_acceptance_sha256"]:
        raise ValueError("field-v2 acceptance binding differs")
    if sha256(possession_acceptance_raw).hexdigest() != expected["possession_acceptance_sha256"]:
        raise ValueError("possession-v2 acceptance binding differs")
    if (
        feature["_validate_authority_state"](
            feature_review_raw,
            feature_acceptance_raw,
            later_authority_present=False,
            product_path_present=False,
            now=datetime.now(UTC),
        )
        != "ACCEPTED"
    ):
        raise ValueError("feature route is not accepted")


def test_accepted_authority_routes_are_independently_valid(
    authorities: dict[str, dict[str, Any]],
) -> None:
    now = datetime.now(UTC)
    field = authorities["field"]
    possession = authorities["possession"]
    feature = authorities["feature"]
    assert (
        field["_validate_authority_state"](
            field["REVIEW_PATH"].read_bytes(),
            field["ACCEPTANCE_PATH"].read_bytes(),
            downstream_paths_present=False,
            now=now,
        )
        == "ACCEPTED"
    )
    assert (
        possession["_validate_authority_state"](
            possession["REVIEW_PATH"].read_bytes(),
            possession["ACCEPTANCE_PATH"].read_bytes(),
            later_authority_present=False,
            now=now,
        )
        == "ACCEPTED"
    )
    assert (
        feature["_validate_authority_state"](
            feature["REVIEW_PATH"].read_bytes(),
            feature["ACCEPTANCE_PATH"].read_bytes(),
            later_authority_present=False,
            product_path_present=False,
            now=now,
        )
        == "ACCEPTED"
    )


def test_all_strict_pairs_emit_canonical_subevents_and_preserve_v1_predicates(
    authorities: dict[str, dict[str, Any]],
) -> None:
    field = authorities["field"]
    possession = authorities["possession"]
    assert field["_event_taxonomy_pairs"]() == field["EXPECTED_TAXONOMY_PAIRS"]
    for event_id, subevent_id in field["EXPECTED_TAXONOMY_PAIRS"]:
        assert field["_subevent_outcome"](event_id, subevent_id) == {
            "canonical_value": subevent_id,
            "raw_value": None,
            "reason_code": None,
        }
    decision = possession["_load_candidates"]()[0]
    v1_decision = possession["_load_canonical_json"](possession["V1_DECISION_PATH"].read_bytes())
    assert len(decision["predicates"]) == 36
    assert possession["_canonical_json_bytes"](decision["predicates"]) == possession[
        "_canonical_json_bytes"
    ](v1_decision["predicates"])


def test_canonical_field_action_composes_through_possession_and_feature(
    authorities: dict[str, dict[str, Any]],
) -> None:
    field = authorities["field"]
    possession = authorities["possession"]
    feature = authorities["feature"]
    outcome = field["_subevent_outcome"](7, 70)
    assert outcome["canonical_value"] == 70
    action = possession["_sequence_action"](
        101,
        7,
        outcome["canonical_value"],
        elapsed=10,
        ordinal=1,
        team_id=42,
    )
    predicates = possession["_load_candidates"]()[2]["predicates"]
    resolved = possession["_resolve_same_period_sequences"]([action], predicates)[101]
    assert resolved == {
        "decision": "CONTROL",
        "predicate_selection_state": "PREDICATE_ADMITTED",
        "possession_eligibility_state": "ELIGIBLE_RESOLVED",
        "resolved_possession_id": "9001:1H:possession:1",
    }
    context = {
        "action_event_taxonomy_id": 7,
        "action_subevent_taxonomy_id": 70,
        "action_team_source_id": 42,
        "possession_eligibility_state": resolved["possession_eligibility_state"],
    }
    rows = feature["_load_candidates"]()[2]["features"]
    applicable = [
        row["feature_name"] for row in rows if feature["_is_feature_applicable"](row, context)
    ]
    assert applicable == ["resolved_possession_action_count"]


def test_missing_canonical_subevent_fails_closed_in_possession(
    authorities: dict[str, dict[str, Any]],
) -> None:
    possession = authorities["possession"]
    action = possession["_sequence_action"](
        102,
        7,
        70,
        elapsed=10,
        ordinal=1,
        team_id=42,
    )
    del action["action_subevent_taxonomy_id"]
    result = possession["_resolve_same_period_sequences"](
        [action], possession["_load_candidates"]()[2]["predicates"]
    )[102]
    assert result["predicate_selection_state"] == "PREDICATE_UNMAPPED"
    assert result["possession_eligibility_state"] == "INELIGIBLE_UNMAPPED"
    assert result["resolved_possession_id"] is None


def test_feature_candidate_has_exact_ordered_closed_roster(
    authorities: dict[str, dict[str, Any]],
) -> None:
    feature = authorities["feature"]
    rows = feature["_load_candidates"]()[2]["features"]
    assert feature["_validate_feature_rows"](rows) == feature["EXPECTED_FEATURES"]
    assert len(rows) == 15
    assert [row["feature_name"] for row in rows] == sorted(row["feature_name"] for row in rows)
    assert {row["feature_name"] for row in rows if row["state"] == "SUPPORTED"} == {
        "action_count",
        "coordinate_known_action_count",
        "match_count",
        "resolved_possession_action_count",
    }


def test_preimages_are_reproducible_siblings_in_exact_acyclic_graph(
    authorities: dict[str, dict[str, Any]],
) -> None:
    preimage = authorities["preimage"]
    product_raw, product = preimage["_load"](preimage["PRODUCT_PATH"])
    schema_raw, schema = preimage["_load"](preimage["SCHEMA_PATH"])
    assert product_raw == preimage["_canonical_bytes"](product)
    assert schema_raw == preimage["_canonical_bytes"](schema)
    assert product_raw.endswith(b"\n") and not product_raw.endswith(b"\n\n")
    assert schema_raw.endswith(b"\n") and not schema_raw.endswith(b"\n\n")
    _validate_preimage_pair(product, schema, product, schema)
    _validate_authority_graph(AUTHORITY_GRAPH_EDGES)
    assert ("PRODUCT_PREIMAGE", "SCHEMA_PREIMAGE") not in AUTHORITY_GRAPH_EDGES
    assert ("SCHEMA_PREIMAGE", "PRODUCT_PREIMAGE") not in AUTHORITY_GRAPH_EDGES
    for sibling_order in (
        ("R21", "PRODUCT_PREIMAGE", "SCHEMA_PREIMAGE", "FIELD_V2"),
        ("R21", "SCHEMA_PREIMAGE", "PRODUCT_PREIMAGE", "FIELD_V2"),
    ):
        positions = {node: index for index, node in enumerate(sibling_order)}
        assert positions["R21"] < positions["PRODUCT_PREIMAGE"] < positions["FIELD_V2"]
        assert positions["R21"] < positions["SCHEMA_PREIMAGE"] < positions["FIELD_V2"]


def test_exact_resource_roster_preserves_v1_prefix_without_identity_overclaim() -> None:
    _validate_resource_roster(RESOURCE_PATHS)
    assert len(RESOURCE_PATHS) == len(set(RESOURCE_PATHS)) == 30
    assert RESOURCE_PATHS[:17] == V1_RESOURCE_PREFIX
    identity_candidate = {RESOURCE_PATHS[0], RESOURCE_PATHS[4]}
    identity_reviewed = identity_candidate | {RESOURCE_PATHS[5]}
    identity_accepted = identity_reviewed | {RESOURCE_PATHS[6]}
    present_identity_paths = {path for path in FUTURE_IDENTITY_PATHS if (ROOT / path).exists()}
    assert present_identity_paths in (
        set(),
        identity_candidate,
        identity_reviewed,
        identity_accepted,
    )
    assert not any("/returns/" in path for path in RESOURCE_PATHS)
    assert RESOURCE_PATHS[-1] == str(TEST_PATH.relative_to(ROOT))
    assert sha256(_canonical_json_bytes(list(RESOURCE_PATHS))).hexdigest() == RESOURCE_PATHS_SHA256


def test_v2_supersession_and_digest_flow_into_feature_and_dependency_plan(
    authorities: dict[str, dict[str, Any]],
) -> None:
    field = authorities["field"]
    possession = authorities["possession"]
    feature = authorities["feature"]
    field_acceptance = field["_load_canonical_json"](field["ACCEPTANCE_PATH"].read_bytes())
    possession_acceptance = possession["_load_canonical_json"](
        possession["ACCEPTANCE_PATH"].read_bytes()
    )
    feature_acceptance = feature["_load_canonical_json"](feature["ACCEPTANCE_PATH"].read_bytes())
    assert field_acceptance["supersedes_acceptance_id"] == (
        "w04-wyscout-field-semantic-acceptance-v1"
    )
    assert possession_acceptance["supersedes_acceptance_id"] == (
        "w04-wyscout-possession-semantic-acceptance-v1"
    )
    feature_inputs = feature["_load_candidates"]()[0]["bound_inputs"]
    assert feature_inputs["field_registry_canonical_sha256"] == field_acceptance["candidate_sha256"]
    assert (
        feature_inputs["field_acceptance_sha256"]
        == sha256(field["ACCEPTANCE_PATH"].read_bytes()).hexdigest()
    )
    assert (
        feature_inputs["possession_taxonomy_canonical_sha256"]
        == possession_acceptance["candidate_sha256"]
    )
    assert (
        feature_inputs["possession_acceptance_sha256"]
        == sha256(possession["ACCEPTANCE_PATH"].read_bytes()).hexdigest()
    )
    plan = _dependency_authority_plan(
        field_acceptance,
        possession_acceptance,
        feature_acceptance,
    )
    _validate_dependency_authority_plan(plan, deepcopy(plan))
    assert [row["kind"] for row in plan] == [
        "source_manifest",
        "identity_evidence",
        "feature_schema",
        "feature_schema",
        "feature_schema",
    ]
    assert plan[2]["digest"] == feature_inputs["field_registry_canonical_sha256"]
    assert plan[2]["acceptance_sha256"] == feature_inputs["field_acceptance_sha256"]
    assert plan[3]["digest"] == feature_inputs["possession_taxonomy_canonical_sha256"]
    assert plan[3]["acceptance_sha256"] == feature_inputs["possession_acceptance_sha256"]


def test_four_serial_lifecycle_states_bind_exact_review_gate_and_product_boundary(
    authorities: dict[str, dict[str, Any]],
) -> None:
    review_raw, gate_raw, test_raw, return_raw, forbidden_reviewers = _synthetic_review_and_gate(
        authorities
    )
    assert (
        _validate_r21_lifecycle(
            review_raw=None,
            gate_record_raw=None,
            gate_evidence_paths=frozenset(),
            product_paths=frozenset(),
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
        == "AWAITING_REVIEW"
    )
    with pytest.raises(ValueError, match="absent"):
        _validate_future_review_assertion(
            None,
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
    with pytest.raises(ValueError, match="cannot precede"):
        _validate_r21_lifecycle(
            review_raw=None,
            gate_record_raw=gate_raw,
            gate_evidence_paths=GATE_EVIDENCE_PATHS,
            product_paths=frozenset(),
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
    assert (
        _validate_r21_lifecycle(
            review_raw=review_raw,
            gate_record_raw=None,
            gate_evidence_paths=frozenset(),
            product_paths=frozenset(),
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
        == "REVIEW_PASS"
    )
    with pytest.raises(ValueError, match="requires"):
        _validate_future_gate_assertion(None, review_raw=None, review_recommendation=None)
    assert (
        _validate_r21_lifecycle(
            review_raw=review_raw,
            gate_record_raw=gate_raw,
            gate_evidence_paths=GATE_EVIDENCE_PATHS,
            product_paths=frozenset(),
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
        == "GATE_PASS"
    )
    simulated_product_paths = frozenset(
        {
            "data/working/wyscout/v5/bronze",
            "data/working/wyscout/v5/silver",
            "data/working/wyscout/v5/gold",
            "data/manifests/wyscout/v5/bronze",
            "data/manifests/wyscout/v5/silver",
            "data/manifests/wyscout/v5/gold",
            "runs/w04/wyscout-rebuild",
            "src/scouting/data_products/wyscout",
            "scripts/rebuild_wyscout_v5.py",
        }
    )
    assert (
        _validate_r21_lifecycle(
            review_raw=review_raw,
            gate_record_raw=gate_raw,
            gate_evidence_paths=GATE_EVIDENCE_PATHS,
            product_paths=simulated_product_paths,
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
        == "GATE_PASS_PRODUCT_PRESENT"
    )


def test_actual_serial_lifecycle_accepts_current_review_gate_and_product_state(
    authorities: dict[str, dict[str, Any]],
) -> None:
    review_raw = REVIEW_PATH.read_bytes() if REVIEW_PATH.exists() else None
    gate_record_raw = GATE_RECORD_PATH.read_bytes() if GATE_RECORD_PATH.exists() else None
    gate_evidence_paths = frozenset(
        str(path.relative_to(ROOT))
        for path in (GATE_PATH, GATE_RECORD_PATH, GATE_RETURN_PATH)
        if path.exists()
    )
    governed_product_paths = set(authorities["feature"]["PRODUCT_PATHS"])
    governed_product_paths.update(authorities["preimage"]["PRODUCT_DESTINATIONS"])
    governed_product_relative_paths = frozenset(
        str(path.relative_to(ROOT)) for path in governed_product_paths
    )
    assert GATE_EVIDENCE_PATHS.isdisjoint(governed_product_relative_paths)
    actual_product_paths = frozenset(
        str(path.relative_to(ROOT)) for path in governed_product_paths if path.exists()
    )
    state = _validate_r21_lifecycle(
        review_raw=review_raw,
        gate_record_raw=gate_record_raw,
        gate_evidence_paths=gate_evidence_paths,
        product_paths=actual_product_paths,
        test_raw=TEST_PATH.read_bytes(),
        return_raw=RETURN_PATH.read_bytes(),
        forbidden_reviewers=_forbidden_cross_authority_reviewers(authorities),
    )
    assert state in {
        "AWAITING_REVIEW",
        "REVIEW_PASS",
        "GATE_PASS",
        "GATE_PASS_PRODUCT_PRESENT",
    }
    assert actual_product_paths <= governed_product_relative_paths


@pytest.mark.parametrize(
    "raw_value",
    ("10", " 10", "+10", "010", True, False, None, 10.0, [10], {"value": 10}),
)
def test_non_strict_subevent_values_preserve_raw_evidence_without_coercion(
    authorities: dict[str, dict[str, Any]],
    raw_value: object,
) -> None:
    field = authorities["field"]
    outcome = field["_subevent_outcome"](1, raw_value)
    assert outcome["canonical_value"] is None
    assert type(outcome["raw_value"]) is type(raw_value)
    assert outcome["raw_value"] == raw_value
    assert (
        outcome["reason_code"]
        == (
            field["REASON_CODES"][
                "string"
                if isinstance(raw_value, str)
                else "boolean"
                if type(raw_value) is bool
                else "null"
                if raw_value is None
                else "number"
                if type(raw_value) is float
                else "array"
                if isinstance(raw_value, list)
                else "object"
            ]
        )
    )


def test_language_bool_as_int_is_explicitly_excluded(
    authorities: dict[str, dict[str, Any]],
) -> None:
    field = authorities["field"]
    assert isinstance(True, int) and isinstance(False, int)
    assert field["_subevent_outcome"](1, True)["reason_code"] == field["REASON_CODES"]["boolean"]
    assert field["_subevent_outcome"](True, 10)["canonical_value"] is None
    assert field["EXPECTED_SUBEVENT_ROW"]["transform"]["boolean_is_integer"] is False


def test_measured_string_evidence_count_and_reason_are_exactly_preserved(
    authorities: dict[str, dict[str, Any]],
) -> None:
    field = authorities["field"]
    row = field["EXPECTED_SUBEVENT_ROW"]
    assert row["source_shape"] == [
        {"count": 3063574, "json_type": "integer"},
        {"count": 7821, "json_type": "string"},
    ]
    assert field["_profile_shapes"]()[("action", "$.subEventId")] == row["source_shape"]
    assert "string:7821" in row["rationale"]
    assert row["transform"]["string_policy"] == "PRESERVE_UNMAPPED_NO_COERCION"
    assert field["REASON_CODES"]["string"] == "ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED"
    assert field["_subevent_outcome"](1, "10") == {
        "canonical_value": None,
        "raw_value": "10",
        "reason_code": "ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED",
    }


@pytest.mark.parametrize("pair", ((1, 999), (999, 10), (0, 0), (-1, 10)))
def test_unknown_integers_never_emit_canonical_subevent(
    authorities: dict[str, dict[str, Any]],
    pair: tuple[int, int],
) -> None:
    outcome = authorities["field"]["_subevent_outcome"](*pair)
    assert outcome["canonical_value"] is None
    assert outcome["reason_code"] == "ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY"


def test_selectors_ignore_raw_names_labels_and_runtime_taxonomy_labels(
    authorities: dict[str, dict[str, Any]],
) -> None:
    possession = authorities["possession"]
    predicates = possession["_load_candidates"]()[2]["predicates"]
    raw_only = {
        "$.eventId": 7,
        "$.subEventId": 70,
        "$.eventName": "Pass",
        "$.subEventName": "Simple pass",
        "event_label": "Pass",
        "subevent_label": "Simple pass",
        "action_team_source_id": 42,
        "action_tag_ids": [],
    }
    assert (
        possession["_evaluate_selector"](raw_only, predicates)
        == possession["_unmapped_selection"]()
    )
    admitted = {
        "action_event_taxonomy_id": 7,
        "action_subevent_taxonomy_id": 70,
        "action_team_source_id": 42,
        "action_tag_ids": [],
    }
    baseline = possession["_evaluate_selector"](admitted, predicates)
    for field_name in (
        "$.eventId",
        "$.subEventId",
        "$.eventName",
        "$.subEventName",
        "event_label",
        "subevent_label",
    ):
        assert (
            possession["_evaluate_selector"](
                {**admitted, field_name: "conflicting runtime label"}, predicates
            )
            == baseline
        )
    assert possession["_load_candidates"]()[2]["policies"]["runtime_label_matching"] == (
        "FORBIDDEN"
    )


def test_v1_v2_hybrid_dependency_bindings_fail_closed(
    authorities: dict[str, dict[str, Any]],
) -> None:
    field = authorities["field"]
    possession = authorities["possession"]
    feature = authorities["feature"]
    acceptances = [
        module["_load_canonical_json"](module["ACCEPTANCE_PATH"].read_bytes())
        for module in (field, possession, feature)
    ]
    expected = _dependency_authority_plan(*acceptances)
    field_v1_mixed = deepcopy(expected)
    field_v1_mixed[2]["candidate_id"] = "w04-wyscout-field-registry-v1"
    field_v1_mixed[2]["digest"] = "fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034"
    with pytest.raises(ValueError, match="binding"):
        _validate_dependency_authority_plan(field_v1_mixed, expected)
    possession_v1_mixed = deepcopy(expected)
    possession_v1_mixed[3]["candidate_id"] = "w04-wyscout-possession-taxonomy-v1"
    possession_v1_mixed[3]["digest"] = (
        "6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa"
    )
    with pytest.raises(ValueError, match="binding"):
        _validate_dependency_authority_plan(possession_v1_mixed, expected)
    feature_decision = deepcopy(feature["_load_candidates"]()[0])
    feature_decision["bound_inputs"]["possession_taxonomy_id"] = (
        "w04-wyscout-possession-taxonomy-v1"
    )
    with pytest.raises(ValueError):
        feature["_validate_decision"](feature_decision)


@pytest.mark.parametrize(
    ("mutation", "field_name", "value"),
    (
        ("wrong-key", "unexpected", None),
        ("wrong-value", "review_recommendation", "REWORK"),
        ("wrong-digest", "candidate_sha256", "0" * 64),
        ("wrong-cardinality", "acceptance_sha256", None),
    ),
)
def test_prior_authority_key_value_digest_and_cardinality_mutations_reject(
    authorities: dict[str, dict[str, Any]],
    mutation: str,
    field_name: str,
    value: object,
) -> None:
    for authority_name in ("field", "possession"):
        authority = authorities[authority_name]
        decision = deepcopy(authority["_load_candidates"]()[0])
        prior = decision["prior_authority"]
        if mutation == "wrong-cardinality":
            del prior[field_name]
        else:
            prior[field_name] = value
        with pytest.raises(ValueError):
            authority["_validate_decision"](decision)


def test_noncanonical_prior_key_order_rejects(
    authorities: dict[str, dict[str, Any]],
) -> None:
    field = authorities["field"]
    decision = field["_load_candidates"]()[0]
    prior = decision["prior_authority"]
    reordered: dict[str, object] = {}
    for key, value in prior.items():
        if key == "review_recommendation":
            reordered["review_record_sha256"] = prior["review_record_sha256"]
            reordered[key] = value
        elif key != "review_record_sha256":
            reordered[key] = value
    decision["prior_authority"] = reordered
    raw = (json.dumps(decision, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    with pytest.raises(ValueError):
        field["_load_canonical_json"](raw)


def test_wrong_supersession_ids_reject(
    authorities: dict[str, dict[str, Any]],
) -> None:
    for authority_name in ("field", "possession"):
        authority = authorities[authority_name]
        acceptance = authority["_load_canonical_json"](authority["ACCEPTANCE_PATH"].read_bytes())
        acceptance["supersedes_acceptance_id"] = "wrong-prior-acceptance"
        with pytest.raises(ValueError):
            if authority_name == "field":
                authority["_validate_authority_state"](
                    authority["REVIEW_PATH"].read_bytes(),
                    authority["_canonical_json_bytes"](acceptance),
                    downstream_paths_present=False,
                    now=datetime.now(UTC),
                )
            else:
                authority["_validate_authority_state"](
                    authority["REVIEW_PATH"].read_bytes(),
                    authority["_canonical_json_bytes"](acceptance),
                    later_authority_present=False,
                    now=datetime.now(UTC),
                )


@pytest.mark.parametrize("relative_path", tuple(V1_PRESENT_PHYSICAL_SHA256))
def test_every_present_v1_resource_is_physically_immutable(
    relative_path: str,
) -> None:
    raw = (ROOT / relative_path).read_bytes()
    _validate_v1_physical_bytes(relative_path, raw)
    with pytest.raises(ValueError, match="v1 physical"):
        _validate_v1_physical_bytes(relative_path, raw + b"mutation")


def test_decision_candidate_review_and_acceptance_drift_rejects(
    authorities: dict[str, dict[str, Any]],
) -> None:
    for authority_name in ("field", "possession", "feature"):
        authority = authorities[authority_name]
        decision, decision_raw, candidate, candidate_raw = authority["_load_candidates"]()
        mutated_decision = deepcopy(decision)
        mutated_decision["decision_id"] = "wrong"
        with pytest.raises(ValueError):
            authority["_validate_decision"](mutated_decision)
        mutated_candidate = deepcopy(candidate)
        mutated_candidate["decision_sha256"] = "0" * 64
        with pytest.raises(ValueError):
            if authority_name == "field":
                authority["_validate_registry"](mutated_candidate, decision, decision_raw)
            elif authority_name == "possession":
                authority["_validate_taxonomy"](mutated_candidate, decision, decision_raw)
            else:
                authority["_validate_registry"](mutated_candidate, decision, decision_raw)
        assert (
            sha256(candidate_raw).hexdigest()
            != sha256(authority["_canonical_json_bytes"](candidate)).hexdigest()
        )
        mutated_review_raw = authority["REVIEW_PATH"].read_bytes() + b"drift\n"
        with pytest.raises(ValueError):
            if authority_name == "field":
                authority["_validate_authority_state"](
                    mutated_review_raw,
                    authority["ACCEPTANCE_PATH"].read_bytes(),
                    downstream_paths_present=False,
                    now=datetime.now(UTC),
                )
            elif authority_name == "possession":
                authority["_validate_authority_state"](
                    mutated_review_raw,
                    authority["ACCEPTANCE_PATH"].read_bytes(),
                    later_authority_present=False,
                    now=datetime.now(UTC),
                )
            else:
                authority["_validate_authority_state"](
                    mutated_review_raw,
                    authority["ACCEPTANCE_PATH"].read_bytes(),
                    later_authority_present=False,
                    product_path_present=False,
                    now=datetime.now(UTC),
                )
        with pytest.raises(ValueError):
            authority["_load_canonical_json"](
                authority["ACCEPTANCE_PATH"].read_bytes() + b"drift\n"
            )


@pytest.mark.parametrize(
    ("target", "key", "value"),
    (
        (
            "product",
            "own_digest",
            "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293",
        ),
        (
            "product",
            "sibling_digest",
            "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f",
        ),
        (
            "schema",
            "feature_digest",
            "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f",
        ),
        ("product", "build_id", "build-1"),
        ("product", "run_id", "run-1"),
        ("schema", "clock", "2026-07-31T10:00:00Z"),
        ("schema", "root", "/tmp/root"),
        ("schema", "host", "localhost"),
        ("product", "product_bytes", "00"),
        ("product", "output_path_observation", "data/working/wyscout/v5/bronze/x"),
        ("schema", "mutable_runtime_observation", "observed-now"),
    ),
)
def test_preimages_reject_descendant_runtime_and_self_referential_values(
    authorities: dict[str, dict[str, Any]],
    target: str,
    key: str,
    value: str,
) -> None:
    preimage = authorities["preimage"]
    _, expected_product = preimage["_load"](preimage["PRODUCT_PATH"])
    _, expected_schema = preimage["_load"](preimage["SCHEMA_PATH"])
    product = deepcopy(expected_product)
    schema = deepcopy(expected_schema)
    (product if target == "product" else schema)[key] = value
    with pytest.raises(ValueError, match="preimage"):
        _validate_preimage_pair(product, schema, expected_product, expected_schema)


@pytest.mark.parametrize(
    "bad_edge",
    (
        ("PRODUCT_PREIMAGE", "PRODUCT_PREIMAGE"),
        ("FIELD_V2", "PRODUCT_PREIMAGE"),
        ("FEATURE_ACCEPTED", "SCHEMA_PREIMAGE"),
        ("SCHEMA_PREIMAGE", "R21"),
    ),
)
def test_preimage_self_reverse_feature_reverse_and_cycle_edges_reject(
    bad_edge: tuple[str, str],
) -> None:
    edges = frozenset({*AUTHORITY_GRAPH_EDGES, bad_edge})
    with pytest.raises(ValueError, match="graph"):
        _validate_authority_graph(edges)


def test_schema_preimage_rejects_concrete_feature_hash_and_descriptor_overclaim(
    authorities: dict[str, dict[str, Any]],
) -> None:
    preimage = authorities["preimage"]
    _, expected_product = preimage["_load"](preimage["PRODUCT_PATH"])
    _, expected_schema = preimage["_load"](preimage["SCHEMA_PATH"])
    concrete = deepcopy(expected_schema)
    concrete["feature_schema_hash_placeholder"]["concrete_value"] = "f" * 64
    with pytest.raises(ValueError):
        _validate_preimage_pair(expected_product, concrete, expected_product, expected_schema)
    wrong_surface = deepcopy(expected_schema)
    wrong_surface["descriptors"][0]["surface_kind"] = "IMPLEMENTED_SCHEMA"
    with pytest.raises(ValueError):
        _validate_preimage_pair(expected_product, wrong_surface, expected_product, expected_schema)
    serializer_claim = deepcopy(expected_schema)
    serializer_claim["descriptors"][0]["row_schema"] = {"fields": []}
    with pytest.raises(ValueError):
        _validate_preimage_pair(
            expected_product,
            serializer_claim,
            expected_product,
            expected_schema,
        )
    assert all(
        set(row) == {"depends_on", "descriptor_id", "descriptor_version", "role", "surface_kind"}
        for row in expected_schema["descriptors"]
    )


@pytest.mark.parametrize(
    "mutation",
    ("sixteenth", "missing", "duplicate", "wrong-sort", "unknown-field", "omitted-field"),
)
def test_feature_roster_shape_mutations_fail_closed(
    authorities: dict[str, dict[str, Any]],
    mutation: str,
) -> None:
    feature = authorities["feature"]
    rows = deepcopy(feature["_load_candidates"]()[2]["features"])
    if mutation == "sixteenth":
        extra = deepcopy(rows[-1])
        extra["feature_name"] = "zz_sixteenth"
        rows.append(extra)
    elif mutation == "missing":
        rows.pop()
    elif mutation == "duplicate":
        rows[-1] = deepcopy(rows[0])
    elif mutation == "wrong-sort":
        rows[0], rows[1] = rows[1], rows[0]
    elif mutation == "unknown-field":
        rows[0]["unknown"] = None
    else:
        del rows[0]["reason"]
    with pytest.raises(ValueError):
        feature["_validate_feature_rows"](rows)


@pytest.mark.parametrize(
    "input_fields",
    (
        ["$.subEventId"],
        ["action_subevent_name"],
        ["guessed_possession"],
        ["resolved_possession_id"],
        ["unlisted_input"],
    ),
)
def test_supported_features_reject_unaccepted_name_guessed_internal_or_unlisted_inputs(
    authorities: dict[str, dict[str, Any]],
    input_fields: list[str],
) -> None:
    feature = authorities["feature"]
    rows = deepcopy(feature["_load_candidates"]()[2]["features"])
    rows[0]["input_fields"] = input_fields
    with pytest.raises(ValueError):
        feature["_validate_feature_rows"](rows)


def test_only_four_supported_rows_and_closed_unsupported_rows_are_permitted(
    authorities: dict[str, dict[str, Any]],
) -> None:
    feature = authorities["feature"]
    rows = deepcopy(feature["_load_candidates"]()[2]["features"])
    rows[1].update(
        {
            "aggregation": "COUNT",
            "applicability": "ACTION_PRESENT",
            "denominator": "NONE",
            "input_fields": ["action_source_id"],
            "output_type": "int64",
            "state": "SUPPORTED",
        }
    )
    with pytest.raises(ValueError):
        feature["_validate_feature_rows"](rows)
    for row_index in (1, 3):
        mutated = deepcopy(feature["_load_candidates"]()[2]["features"])
        mutated[row_index]["input_fields"] = ["action_source_id"]
        mutated[row_index]["output_type"] = "int64"
        with pytest.raises(ValueError):
            feature["_validate_feature_rows"](mutated)


@pytest.mark.parametrize(
    "missing",
    (
        "field_acceptance_raw",
        "possession_acceptance_raw",
        "feature_review_raw",
        "feature_acceptance_raw",
    ),
)
def test_feature_candidate_review_and_use_require_all_predecessor_acceptances(
    authorities: dict[str, dict[str, Any]],
    missing: str,
) -> None:
    feature = authorities["feature"]
    arguments = {
        "field_acceptance_raw": feature["FIELD_ACCEPTANCE_PATH"].read_bytes(),
        "possession_acceptance_raw": feature["POSSESSION_ACCEPTANCE_PATH"].read_bytes(),
        "feature_review_raw": feature["REVIEW_PATH"].read_bytes(),
        "feature_acceptance_raw": feature["ACCEPTANCE_PATH"].read_bytes(),
    }
    arguments[missing] = None
    with pytest.raises(ValueError, match="requires"):
        _validate_feature_prerequisites(feature, **arguments)


def test_feature_hash_is_unavailable_before_feature_acceptance(
    authorities: dict[str, dict[str, Any]],
) -> None:
    feature = authorities["feature"]
    registry = feature["_load_candidates"]()[2]
    for state in ("DECISION_ONLY", "REVIEW_PASS", "REVIEW_REWORK"):
        with pytest.raises(ValueError, match="unavailable"):
            feature["_feature_schema_hash"](state, registry)
    assert (
        feature["_feature_schema_hash"]("ACCEPTED", registry)
        == feature["EXPECTED_REGISTRY_CANONICAL_SHA256"]
    )


def test_preimage_digest_substitution_and_physical_candidate_substitution_reject(
    authorities: dict[str, dict[str, Any]],
) -> None:
    feature = authorities["feature"]
    decision = deepcopy(feature["_load_candidates"]()[0])
    product_digest = decision["bound_inputs"]["product_contract_preimage_sha256"]
    schema_digest = decision["bound_inputs"]["schema_bundle_preimage_sha256"]
    decision["bound_inputs"]["product_contract_preimage_sha256"] = schema_digest
    decision["bound_inputs"]["schema_bundle_preimage_sha256"] = product_digest
    with pytest.raises(ValueError):
        feature["_validate_decision"](decision)
    field = authorities["field"]
    possession = authorities["possession"]
    acceptances = [
        module["_load_canonical_json"](module["ACCEPTANCE_PATH"].read_bytes())
        for module in (field, possession, feature)
    ]
    expected = _dependency_authority_plan(*acceptances)
    physical_substitution = deepcopy(expected)
    physical_substitution[2]["digest"] = acceptances[0]["candidate_physical_sha256"]
    with pytest.raises(ValueError, match="binding"):
        _validate_dependency_authority_plan(physical_substitution, expected)


@pytest.mark.parametrize(
    "mutation",
    (
        "cardinality",
        "v1-prefix",
        "duplicate",
        "directory",
        "product",
        "return",
        "generated-evidence",
    ),
)
def test_resource_roster_mutations_fail_closed(mutation: str) -> None:
    paths = list(RESOURCE_PATHS)
    if mutation == "cardinality":
        paths.pop()
    elif mutation == "v1-prefix":
        paths[0] = "configs/schema/changed-identity.yaml"
    elif mutation == "duplicate":
        paths[-1] = paths[-2]
    elif mutation == "directory":
        paths[-1] = "tests/contracts/"
    elif mutation == "product":
        paths[-1] = "data/working/wyscout/v5/bronze/build_id=x/part-00000.parquet"
    elif mutation == "return":
        paths[-1] = "reports/reviews/W04/returns/unapproved.md"
    else:
        paths[-1] = "reports/verification/W04/generated-evidence.json"
    with pytest.raises(ValueError, match="roster"):
        _validate_resource_roster(tuple(paths))


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("review_path", "reports/reviews/W04/wrong.md"),
        ("review_id", "wrong-review-id"),
        ("recommendation", "REWORK"),
        ("test_artifact_physical_sha256", "0" * 64),
        ("test_return_physical_sha256", "0" * 64),
        ("reviewed_by", TEST_PRODUCER_ID),
        ("unexpected", "open-record"),
    ),
)
def test_future_review_missing_mutated_wrong_path_id_nonpass_or_self_authored_rejects(
    field_name: str,
    value: str,
) -> None:
    test_raw = TEST_PATH.read_bytes()
    return_raw = b"synthetic return bytes\n"
    reviewer = str(uuid5(NAMESPACE_URL, "w04-r21-independent-reviewer-negative-fixture"))
    record = {
        "recommendation": "PASS",
        "review_id": REVIEW_ID,
        "review_path": str(REVIEW_PATH.relative_to(ROOT)),
        "reviewed_by": reviewer,
        "test_artifact_physical_sha256": sha256(test_raw).hexdigest(),
        "test_return_physical_sha256": sha256(return_raw).hexdigest(),
    }
    record[field_name] = value
    with pytest.raises(ValueError):
        _validate_future_review_assertion(
            record,
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers={TEST_PRODUCER_ID},
        )


def test_review_and_gate_machine_records_are_closed_canonical_and_physically_bound(
    authorities: dict[str, dict[str, Any]],
) -> None:
    review_raw, gate_raw, test_raw, return_raw, forbidden_reviewers = _synthetic_review_and_gate(
        authorities
    )
    review, review_record_raw = _load_review_markdown(review_raw)
    assert review_record_raw == _canonical_json_bytes(review)
    _validate_future_review_assertion(
        review,
        test_raw=test_raw,
        return_raw=return_raw,
        forbidden_reviewers=forbidden_reviewers,
    )
    gate = _load_closed_canonical_json(gate_raw, "R21 master gate record")
    _validate_future_gate_assertion(
        gate,
        review_raw=review_raw,
        review_recommendation="PASS",
    )

    open_review = deepcopy(review)
    open_review["unexpected"] = None
    with pytest.raises(ValueError, match="not closed"):
        _validate_future_review_assertion(
            open_review,
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
    with pytest.raises(ValueError, match="canonical JSON"):
        _load_closed_canonical_json(gate_raw.removesuffix(b"\n"), "R21 master gate record")
    wrong_gate = deepcopy(gate)
    wrong_gate["review_physical_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="binding"):
        _validate_future_gate_assertion(
            wrong_gate,
            review_raw=review_raw,
            review_recommendation="PASS",
        )
    with pytest.raises(ValueError, match="incomplete"):
        _validate_r21_lifecycle(
            review_raw=review_raw,
            gate_record_raw=gate_raw,
            gate_evidence_paths=GATE_EVIDENCE_PATHS - {str(GATE_RETURN_PATH.relative_to(ROOT))},
            product_paths=frozenset(),
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )


def test_combined_write_scope_and_gate_before_pass_review_reject() -> None:
    _validate_serial_write_scopes(PACKET_WRITE_SCOPES)
    combined = (
        PACKET_WRITE_SCOPES[0] | PACKET_WRITE_SCOPES[1],
        PACKET_WRITE_SCOPES[2],
    )
    with pytest.raises(ValueError, match="scope"):
        _validate_serial_write_scopes(combined)
    review_raw = b"independent review bytes\n"
    gate = {
        "decision": "PASS",
        "gate_path": str(GATE_PATH.relative_to(ROOT)),
        "review_path": str(REVIEW_PATH.relative_to(ROOT)),
        "review_physical_sha256": sha256(review_raw).hexdigest(),
        "review_recommendation": "PASS",
    }
    for recommendation in (None, "REWORK"):
        with pytest.raises(ValueError, match="requires"):
            _validate_future_gate_assertion(
                gate,
                review_raw=review_raw,
                review_recommendation=recommendation,
            )


@pytest.mark.parametrize(
    "forbidden_path",
    (
        "data/working/wyscout/v5/bronze",
        "data/working/wyscout/v5/silver",
        "data/working/wyscout/v5/gold",
        "data/manifests/wyscout/v5/bronze",
        "data/manifests/wyscout/v5/silver",
        "data/manifests/wyscout/v5/gold",
        "runs/w04/wyscout-rebuild",
        "src/scouting/data_products/wyscout",
        "scripts/rebuild_wyscout_v5.py",
    ),
)
def test_product_path_is_blocked_before_gate_and_permitted_after_complete_gate(
    authorities: dict[str, dict[str, Any]],
    forbidden_path: str,
) -> None:
    review_raw, gate_raw, test_raw, return_raw, forbidden_reviewers = _synthetic_review_and_gate(
        authorities
    )
    simulated_product = frozenset({forbidden_path})
    with pytest.raises(ValueError, match="complete R21 master gate"):
        _validate_r21_lifecycle(
            review_raw=review_raw,
            gate_record_raw=None,
            gate_evidence_paths=frozenset(),
            product_paths=simulated_product,
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
    assert (
        _validate_r21_lifecycle(
            review_raw=review_raw,
            gate_record_raw=gate_raw,
            gate_evidence_paths=GATE_EVIDENCE_PATHS,
            product_paths=simulated_product,
            test_raw=test_raw,
            return_raw=return_raw,
            forbidden_reviewers=forbidden_reviewers,
        )
        == "GATE_PASS_PRODUCT_PRESENT"
    )

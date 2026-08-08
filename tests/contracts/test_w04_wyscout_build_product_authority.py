"""Closed tests for the decision-only W04 build/product authority."""

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

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-build-product-authority-decisions-v1.json"
)
REVIEW_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-build-product-independent-review-R1.md"
)
ACCEPTANCE_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-build-product-authority-acceptance-v1.json"
)
PRODUCT_DESTINATIONS = (
    ROOT / "data/working/wyscout/v5/bronze",
    ROOT / "data/working/wyscout/v5/silver",
    ROOT / "data/working/wyscout/v5/gold",
    ROOT / "data/manifests/wyscout/v5/bronze",
    ROOT / "data/manifests/wyscout/v5/silver",
    ROOT / "data/manifests/wyscout/v5/gold",
    ROOT / "runs/w04/wyscout-rebuild",
)

DECISION_ID = "w04-wyscout-build-product-authority-decisions-v1"
DECISION_SCHEMA_VERSION = "w04-wyscout-build-product-authority-decision-v1"
EXPECTED_DECISION_PHYSICAL_SHA256 = (
    "3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d"
)
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
REVIEW_ID = "w04-wyscout-build-product-independent-review-R1"
REVIEW_SCHEMA_VERSION = "w04-build-product-authority-independent-review-v1"
ACCEPTANCE_ID = "w04-wyscout-build-product-authority-acceptance-v1"
ACCEPTANCE_SCHEMA_VERSION = "w04-build-product-authority-acceptance-v1"
TEST_REVIEWER_ID = "a66fa478-73f1-534c-8d96-8569786631e5"
FUTURE_TOLERANCE = timedelta(minutes=5)

EXPECTED_BOUND_INPUTS = [
    (
        "reports/verification/W04/wyscout-build-product-authority-authorization-R1.md",
        "b41a0606282d447675989181329bf53f987624be10b079ea5b74778d440fafe9",
    ),
    (
        "reports/verification/W04/wyscout-pre-build-authority-complete-repository-gate-R1.md",
        "08ef2ed6c47c6b478ec4a243c59ab2cd8d4a882061ede900ad468dd473662a5f",
    ),
    (
        "reports/reviews/W04/wyscout-schema-design-R20.md",
        "8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047",
    ),
    (
        "reports/reviews/W04/wyscout-schema-design-R21.md",
        "faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020",
    ),
    (
        "reports/reviews/W04/wyscout-build-receipt-closure-audit-R2.md",
        "77cf8dcb79d202b960553dfd6da631af039e5ec0a382a0e7c30be770045d0491",
    ),
    (
        "reports/reviews/W04/wyscout-build-receipt-closure-audit-R3.md",
        "0cf86df75af1276b3703083d3137de9ef345e2125a08a4e819617bbfd6100435",
    ),
    (
        "reports/reviews/W04/wyscout-build-receipt-closure-audit-R4.md",
        "a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222",
    ),
    (
        "reports/reviews/W04/wyscout-build-receipt-closure-audit-independent-review-R4.md",
        "288c58c29bbd572b8fe9bf5df9875d5a6b9c24cfca44923b8780e2dcb7bd7827",
    ),
    (
        "reports/reviews/W04/returns/W04-BUILD-RECEIPT-CLOSURE-AUDIT-REVIEW-01-R4.md",
        "90c711805516e68b065298320b2628eca5d2d9fd4404d76cdd663bed51ecefe0",
    ),
    (
        "configs/schema/wyscout-v5-product-contract-preimage-v1.json",
        "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293",
    ),
    (
        "configs/schema/wyscout-v5-schema-bundle-preimage-v1.json",
        "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f",
    ),
    (
        "data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json",
        "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd",
    ),
    (
        "data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json",
        "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df",
    ),
    (
        "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json",
        "beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436",
    ),
    (
        "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json",
        "2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1",
    ),
    (
        "reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json",
        "d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c",
    ),
    (
        "reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json",
        "37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86",
    ),
]

TOP_LEVEL_KEYS = {
    "aggregate_materialization",
    "authority_class",
    "bound_inputs",
    "build_identity",
    "completion_index_binding",
    "decided_at",
    "decided_by",
    "decision_id",
    "decision_schema_version",
    "feature_scope",
    "layer_manifest_authority",
    "lifecycle",
    "prohibitions",
    "receipt_contracts",
    "window_authority",
}
ROOT_ROLES = [
    "BRONZE_KNOWN_RECORD",
    "BRONZE_REJECTED_RECORD",
    "BRONZE_REJECTED_FIELD",
    "SILVER_COMPETITION",
    "SILVER_TEAM",
    "SILVER_PLAYER",
    "SILVER_MATCH",
    "SILVER_ACTION",
    "SILVER_LINEUP_STINT",
    "SILVER_POSSESSION",
    "SILVER_PLAYER_MATCH_FACT",
    "GOLD_PLAYER_WINDOW",
    "LAYER_MANIFEST",
    "TEMPORAL_BOUNDARY_RECEIPT",
    "REBUILD_INVOCATION_RECEIPT",
    "ENTRYPOINT_SOURCE_RESULT",
    "COMPONENT_PROOF_RESULT",
    "PRE_BUILD_ADMISSION_RESULT",
    "REBUILD_RECEIPT_SUMMARY",
    "LAYER_MANIFEST_SUMMARY",
    "FINAL_RECHECK_RESULT",
    "POST_BUILD_ID_REBUILD_RESULT",
    "CHILD_RESULT_ENVELOPE",
]
PROJECTION_KEYS = [
    "authority_rows",
    "code_manifest_id",
    "code_manifest_sha256",
    "dependency_rows",
    "dependency_watermark",
    "environment_digest",
    "feature_cutoff_ts",
    "feature_schema_hash",
    "identity_bundle_id",
    "identity_bundle_sha256",
    "local_resource_digest",
    "product_contract_digest",
    "role_context_id",
    "role_context_state",
    "role_context_version",
    "schema_bundle_digest",
    "schema_version",
    "selected_lock_closure_digest",
    "source_manifest_id",
    "source_manifest_sha256",
    "tenant_club_id",
    "tenant_id",
    "window_definition_id",
    "window_end_utc",
    "window_start_utc",
]
INVOCATION_RECEIPT_KEYS = [
    "boundary_receipts",
    "build_id",
    "completed_at",
    "layer_manifests",
    "rebuild_invocation",
    "result_state",
    "run_id",
    "schema_version",
    "started_at",
]
BOUNDARY_RECEIPT_KEYS = [
    "build_id",
    "checked_at",
    "dependency_lineage_hash",
    "feature_cutoff_ts",
    "gold_manifest_relative_path",
    "gold_manifest_sha256",
    "gold_product_physical_sha256",
    "gold_product_relative_path",
    "gold_product_semantic_sha256",
    "gold_relative_path_sha256",
    "row_count",
    "run_id",
    "schema_version",
    "temporal_proof_sha256",
    "verification_state",
]
SUPPORTED_FEATURES = [
    "action_count",
    "coordinate_known_action_count",
    "match_count",
    "resolved_possession_action_count",
]
REVIEW_KEYS = {
    "decision_id",
    "decision_physical_sha256",
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
    "decision_id",
    "decision_physical_sha256",
    "review_id",
    "review_physical_sha256",
    "review_record_sha256",
    "review_recommendation",
}
UUID_WIRE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
UTC_WIRE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{6})?Z$")


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
            if not isinstance(key, str):
                raise ValueError("non-string key")
            _assert_nfc_tree(key)
            _assert_nfc_tree(item)
        return
    if value is not None and type(value) not in {bool, int}:
        raise ValueError("unsupported scalar")


def _canonical_json_bytes(value: object, *, terminal_lf: bool = True) -> bytes:
    _assert_nfc_tree(value)
    suffix = "\n" if terminal_lf else ""
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + suffix
    ).encode()


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _load_canonical_json(raw: bytes) -> dict[str, Any]:
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("invalid JSON encoding")
    value = json.loads(raw, object_pairs_hook=_reject_duplicate_pairs)
    if type(value) is not dict or raw != _canonical_json_bytes(value):
        raise ValueError("noncanonical JSON")
    return value


def _parse_clock(value: object, *, truthful: bool = False) -> datetime:
    if not isinstance(value, str) or UTC_WIRE.fullmatch(value) is None:
        raise ValueError("noncanonical UTC")
    parsed = datetime.fromisoformat(f"{value[:-1]}+00:00")
    timespec = "microseconds" if "." in value else "seconds"
    if parsed.isoformat(timespec=timespec).replace("+00:00", "Z") != value:
        raise ValueError("noncanonical UTC")
    if truthful and parsed > datetime.now(UTC) + FUTURE_TOLERANCE:
        raise ValueError("future authority clock")
    return parsed


def _validate_actor(value: object, *, expected: str | None = None) -> str:
    if not isinstance(value, str) or UUID_WIRE.fullmatch(value) is None:
        raise ValueError("invalid actor")
    actor = UUID(value)
    if str(actor) != value or actor.variant != "specified in RFC 4122":
        raise ValueError("invalid actor")
    if expected is not None and value != expected:
        raise ValueError("unexpected actor")
    return value


def _validate_decision(value: dict[str, Any]) -> None:
    if sha256(_canonical_json_bytes(value)).hexdigest() != EXPECTED_DECISION_PHYSICAL_SHA256:
        raise ValueError("decision digest differs")
    if set(value) != TOP_LEVEL_KEYS:
        raise ValueError("decision keys differ")
    if (
        value["authority_class"] != "BUILD_PRODUCT"
        or value["decision_id"] != DECISION_ID
        or value["decision_schema_version"] != DECISION_SCHEMA_VERSION
        or value["lifecycle"]["state"] != "AUTHORITY_ONLY_NO_PRODUCT_BYTES"
        or value["lifecycle"]["product_bytes_permitted"] is not False
    ):
        raise ValueError("decision scalar differs")
    _validate_actor(value["decided_by"], expected=MASTER_ACTOR_ID)
    _parse_clock(value["decided_at"], truthful=True)
    observed = [(row["path"], row["sha256"]) for row in value["bound_inputs"]]
    if observed != EXPECTED_BOUND_INPUTS:
        raise ValueError("bound inputs differ")
    if (
        value["aggregate_materialization"]["implemented_schema_bundle_v2"]["required_root_roles"]
        != ROOT_ROLES
    ):
        raise ValueError("root roster differs")
    if value["build_identity"]["pre_build_projection_keys"] != PROJECTION_KEYS:
        raise ValueError("projection differs")
    receipts = value["receipt_contracts"]
    if (
        receipts["rebuild_invocation_receipt"]["keys"] != INVOCATION_RECEIPT_KEYS
        or receipts["temporal_boundary_receipt"]["keys"] != BOUNDARY_RECEIPT_KEYS
    ):
        raise ValueError("receipt roster differs")
    semantic = value["layer_manifest_authority"]["manifest_semantic_derivation"]
    if semantic["preimage_keys"] != ["layer_manifest", "semantic_schema_version"]:
        raise ValueError("semantic derivation differs")
    if value["feature_scope"]["supported_feature_names"] != SUPPORTED_FEATURES:
        raise ValueError("feature scope differs")


def _load_decision() -> tuple[dict[str, Any], bytes]:
    raw = AUTHORITY_PATH.read_bytes()
    value = _load_canonical_json(raw)
    _validate_decision(value)
    return value, raw


def _snapshot_destination_state(
    destinations: tuple[Path, ...],
) -> tuple[tuple[str, str, int, int, int], ...]:
    rows: list[tuple[str, str, int, int, int]] = []
    for root in destinations:
        if not root.exists() and not root.is_symlink():
            rows.append((str(root), "absent", 0, 0, 0))
            continue
        candidates = (root, *sorted(root.rglob("*"))) if root.is_dir() else (root,)
        for path in candidates:
            stat = path.lstat()
            if path.is_symlink():
                kind = f"symlink:{path.readlink()}"
            elif path.is_dir():
                kind = "directory"
            else:
                kind = "file"
            rows.append((str(path), kind, stat.st_mode, stat.st_size, stat.st_mtime_ns))
    return tuple(rows)


def _deny_writer_calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    writer_calls: list[str] = []
    original_open = Path.open

    def audited_open(
        path: Path,
        mode: str = "r",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if any(token in mode for token in ("w", "a", "x", "+")):
            writer_calls.append(f"open:{path}:{mode}")
            raise AssertionError("authority evaluation attempted a writer call")
        return original_open(path, mode, *args, **kwargs)

    def unexpected_writer(path: Path, *args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        writer_calls.append(f"{path}")
        raise AssertionError("authority evaluation attempted a writer call")

    monkeypatch.setattr(Path, "open", audited_open)
    for method_name in (
        "hardlink_to",
        "mkdir",
        "rename",
        "replace",
        "rmdir",
        "symlink_to",
        "touch",
        "unlink",
        "write_bytes",
        "write_text",
    ):
        monkeypatch.setattr(Path, method_name, unexpected_writer)
    return writer_calls


def _validate_review(raw: bytes, decision_raw: bytes) -> tuple[dict[str, Any], bytes]:
    marker = b"```w04-build-product-authority-review-v1\n"
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("invalid review encoding")
    if raw.count(b"```") != 2 or raw.count(marker) != 1:
        raise ValueError("review must have one machine fence")
    body = raw.split(marker, maxsplit=1)[1].split(b"```\n", maxsplit=1)[0]
    review = _load_canonical_json(body)
    if set(review) != REVIEW_KEYS:
        raise ValueError("review keys differ")
    if (
        review["decision_id"] != DECISION_ID
        or review["decision_physical_sha256"] != sha256(decision_raw).hexdigest()
        or review["review_id"] != REVIEW_ID
        or review["review_schema_version"] != REVIEW_SCHEMA_VERSION
        or review["recommendation"] not in {"PASS", "REWORK"}
        or type(review["findings"]) is not list
    ):
        raise ValueError("review differs")
    reviewer = _validate_actor(review["reviewed_by"])
    if reviewer == MASTER_ACTOR_ID:
        raise ValueError("self-review")
    if _parse_clock(review["reviewed_at"], truthful=True) < _parse_clock(
        _load_canonical_json(decision_raw)["decided_at"]
    ):
        raise ValueError("review predates decision")
    for finding in review["findings"]:
        if (
            type(finding) is not dict
            or set(finding) != {"code", "severity", "summary"}
            or finding["severity"] not in {"P0", "P1", "P2"}
        ):
            raise ValueError("finding differs")
    if (review["recommendation"] == "PASS") != (review["findings"] == []):
        raise ValueError("review recommendation differs")
    return review, body


def _validate_acceptance(
    raw: bytes,
    decision_raw: bytes,
    review: dict[str, Any],
    review_raw: bytes,
    review_record_raw: bytes,
) -> None:
    acceptance = _load_canonical_json(raw)
    if set(acceptance) != ACCEPTANCE_KEYS:
        raise ValueError("acceptance keys differ")
    if (
        acceptance["acceptance_id"] != ACCEPTANCE_ID
        or acceptance["acceptance_schema_version"] != ACCEPTANCE_SCHEMA_VERSION
        or acceptance["decision_id"] != DECISION_ID
        or acceptance["decision_physical_sha256"] != sha256(decision_raw).hexdigest()
        or acceptance["review_id"] != REVIEW_ID
        or acceptance["review_physical_sha256"] != sha256(review_raw).hexdigest()
        or acceptance["review_record_sha256"] != sha256(review_record_raw).hexdigest()
        or acceptance["review_recommendation"] != "PASS"
        or review["recommendation"] != "PASS"
    ):
        raise ValueError("acceptance differs")
    _validate_actor(acceptance["accepted_by"], expected=MASTER_ACTOR_ID)
    accepted_at = _parse_clock(acceptance["accepted_at"], truthful=True)
    if accepted_at < _parse_clock(review["reviewed_at"]):
        raise ValueError("acceptance predates review")


def _lifecycle_state(review_raw: bytes | None, acceptance_raw: bytes | None) -> str:
    _, decision_raw = _load_decision()
    if review_raw is None:
        if acceptance_raw is not None:
            raise ValueError("acceptance cannot precede review")
        return "AUTHORITY_ONLY_NO_PRODUCT_BYTES"
    review, record_raw = _validate_review(review_raw, decision_raw)
    if acceptance_raw is None:
        return f"REVIEW_{review['recommendation']}"
    _validate_acceptance(acceptance_raw, decision_raw, review, review_raw, record_raw)
    return "ACCEPTED_AUTHORITY_ONLY_NO_PRODUCT_BYTES"


def _valid_review(decision_raw: bytes) -> tuple[dict[str, Any], bytes, bytes]:
    record: dict[str, Any] = {
        "decision_id": DECISION_ID,
        "decision_physical_sha256": sha256(decision_raw).hexdigest(),
        "findings": [],
        "recommendation": "PASS",
        "review_id": REVIEW_ID,
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        "reviewed_at": "2026-08-01T11:45:00Z",
        "reviewed_by": TEST_REVIEWER_ID,
    }
    body = _canonical_json_bytes(record)
    raw = b"Independent review.\n\n```w04-build-product-authority-review-v1\n" + body
    raw += b"```\n"
    return record, body, raw


def _valid_acceptance(decision_raw: bytes, review_raw: bytes, review_record_raw: bytes) -> bytes:
    return _canonical_json_bytes(
        {
            "acceptance_id": ACCEPTANCE_ID,
            "acceptance_schema_version": ACCEPTANCE_SCHEMA_VERSION,
            "accepted_at": "2026-08-01T11:46:00Z",
            "accepted_by": MASTER_ACTOR_ID,
            "decision_id": DECISION_ID,
            "decision_physical_sha256": sha256(decision_raw).hexdigest(),
            "review_id": REVIEW_ID,
            "review_physical_sha256": sha256(review_raw).hexdigest(),
            "review_record_sha256": sha256(review_record_raw).hexdigest(),
            "review_recommendation": "PASS",
        }
    )


def test_decision_is_canonical_closed_and_binds_every_fixed_input() -> None:
    decision, raw = _load_decision()
    assert sha256(raw).hexdigest() == EXPECTED_DECISION_PHYSICAL_SHA256
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert set(decision) == TOP_LEVEL_KEYS
    assert len(decision["bound_inputs"]) == len(EXPECTED_BOUND_INPUTS) == 17
    for path_text, expected_sha256 in EXPECTED_BOUND_INPUTS:
        assert sha256((ROOT / path_text).read_bytes()).hexdigest() == expected_sha256


def test_window_bytes_digest_and_uuid_are_reconstructed_exactly() -> None:
    decision, _ = _load_decision()
    window = decision["window_authority"]
    preimage = _canonical_json_bytes(window["window_identity_object"], terminal_lf=False)
    assert len(preimage) == window["window_identity_byte_length"] == 250
    assert sha256(preimage).hexdigest() == window["window_identity_bytes_sha256"]
    namespace = uuid5(NAMESPACE_URL, window["window_definition_namespace_name"])
    assert (
        str(uuid5(namespace, f"single-match-poc:{sha256(preimage).hexdigest()}"))
        == (window["window_definition_id"])
    )
    assert window["window_start_utc"] < window["window_end_utc"]
    assert window["snapshot_as_of_ts"] == window["selected_match_start_ts"]


def test_completion_index_binding_matches_stored_population_exactly() -> None:
    decision, _ = _load_decision()
    binding = decision["completion_index_binding"]
    index_raw = (ROOT / binding["source_completion_index_path"]).read_bytes()
    index = json.loads(index_raw)
    assert sha256(index_raw).hexdigest() == binding["source_completion_index_sha256"]
    assert index["source_manifest_id"] == binding["source_manifest_id"]
    assert index["source_manifest_sha256"] == binding["source_manifest_sha256"]
    member = next(row for row in index["members"] if row["path"] == binding["source_member_path"])
    assert member["sha256"] == binding["source_member_sha256"]
    assert member["row_count"] == binding["source_member_row_count"]
    periods = [
        {
            "action_count": row["action_count"],
            "ordered_membership_sha256": row["membership_sha256"],
            "period_code": row["action_period_code"],
            "period_rank": row["period_rank"],
        }
        for row in member["periods"]
        if row["match_source_id"] == binding["provider_match_id"]
    ]
    assert periods == binding["periods"]
    assert sum(row["action_count"] for row in periods) == 1768


def test_exact_aggregate_build_receipt_and_semantic_rosters_are_frozen() -> None:
    decision, _ = _load_decision()
    aggregates = decision["aggregate_materialization"]
    schema = aggregates["implemented_schema_bundle_v2"]
    product = aggregates["product_contract_v2"]
    assert schema["required_root_roles"] == ROOT_ROLES and len(ROOT_ROLES) == 23
    assert len(schema["top_level_keys"]) == 8
    assert len(schema["implemented_schema_row_keys"]) == 6
    assert len(product["top_level_keys"]) == 10
    assert product["publication_order"] == [
        "PRODUCT_PARQUET",
        "LAYER_MANIFEST",
        "TEMPORAL_BOUNDARY_RECEIPT",
        "REBUILD_INVOCATION_RECEIPT",
        "CHILD_RESULT_SUMMARY",
    ]
    build = decision["build_identity"]
    assert build["pre_build_projection_keys"] == PROJECTION_KEYS
    assert build["pre_build_projection_key_count"] == 25
    assert build["post_hash_invocation_key_count"] == 25
    assert build["second_build_hash"] == "FORBIDDEN"
    assert decision["receipt_contracts"]["rebuild_invocation_receipt"]["keys"] == (
        INVOCATION_RECEIPT_KEYS
    )
    assert decision["receipt_contracts"]["temporal_boundary_receipt"]["keys"] == (
        BOUNDARY_RECEIPT_KEYS
    )
    semantic = decision["layer_manifest_authority"]["manifest_semantic_derivation"]
    assert semantic["preimage_key_count"] == 2
    assert semantic["preimage_keys"] == ["layer_manifest", "semantic_schema_version"]
    assert semantic["terminal_lf"] is False


def test_aggregate_graph_is_acyclic_and_absent_digests_are_not_serialized() -> None:
    decision, _ = _load_decision()
    aggregate = decision["aggregate_materialization"]
    order = aggregate["dependency_order"]
    assert len(order) == len(set(order)) == 8
    assert order.index("COMPLETE_IMPLEMENTED_SCHEMA_BUNDLE_V2") < order.index(
        "PRODUCT_AUTHORIZED_CONTRACT_V2"
    )
    assert order.index("PRODUCT_AUTHORIZED_CONTRACT_V2") < order.index(
        "UNCHANGED_25_KEY_PRE_BUILD_PROJECTION"
    )

    def mapping_keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value) | set().union(*(mapping_keys(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(mapping_keys(item) for item in value))
        return set()

    keys = mapping_keys(aggregate)
    assert "schema_bundle_preimage_v2_sha256" not in keys
    assert "product_contract_digest" not in keys
    assert "schema_bundle_digest" not in keys
    assert not any(value is None for value in aggregate.values())


def test_layer_population_parent_and_substitution_closure_is_exact() -> None:
    decision, _ = _load_decision()
    layer = decision["layer_manifest_authority"]
    assert layer["layer_summary_order"] == ["BRONZE", "SILVER", "GOLD"]
    assert layer["layer_summary_keys"] == [
        "layer",
        "manifest_relative_path",
        "manifest_sha256",
        "manifest_size_bytes",
        "semantic_sha256",
    ]
    assert layer["parent_chain"] == {"BRONZE": [], "GOLD": ["SILVER"], "SILVER": ["BRONZE"]}
    assert layer["gold_population"]["gold_entry_count"] == 1
    assert layer["gold_population"]["product_count"] == 1
    assert layer["gold_population"]["boundary_receipt_count"] == 1
    assert len(layer["substitution_failures"]) == 8
    assert (
        "REHASH_ALL_DOWNSTREAM_SUMMARY_RECEIPT_AND_CHILD_WRAPPERS" in layer["substitution_failures"]
    )


def test_feature_scope_is_exactly_four_and_preserves_strings_without_coercion() -> None:
    decision, _ = _load_decision()
    scope = decision["feature_scope"]
    assert scope["supported_feature_count"] == 4
    assert scope["supported_feature_names"] == SUPPORTED_FEATURES
    assert scope["action_subevent_mapping"] == (
        "STRICT_JSON_INTEGER_EXCLUDING_BOOLEAN_AND_EXACT_FROZEN_EVENT_SUBEVENT_PAIR_ONLY"
    )
    assert scope["string_subevent_policy"] == ("PRESERVE_UNMAPPED_OR_QUARANTINED_WITHOUT_COERCION")


def test_lifecycle_allows_absent_review_but_fails_closed_when_malformed() -> None:
    _, decision_raw = _load_decision()
    assert _lifecycle_state(None, None) == "AUTHORITY_ONLY_NO_PRODUCT_BYTES"
    review, record_raw, review_raw = _valid_review(decision_raw)
    assert _lifecycle_state(review_raw, None) == "REVIEW_PASS"
    acceptance_raw = _valid_acceptance(decision_raw, review_raw, record_raw)
    assert _lifecycle_state(review_raw, acceptance_raw) == (
        "ACCEPTED_AUTHORITY_ONLY_NO_PRODUCT_BYTES"
    )
    malformed = deepcopy(review)
    malformed["decision_physical_sha256"] = "0" * 64
    malformed_raw = (
        b"```w04-build-product-authority-review-v1\n" + _canonical_json_bytes(malformed) + b"```\n"
    )
    with pytest.raises(ValueError, match="review differs"):
        _lifecycle_state(malformed_raw, None)
    with pytest.raises(ValueError, match="precede review"):
        _lifecycle_state(None, acceptance_raw)


def test_live_lifecycle_artifacts_are_absent_or_strictly_valid() -> None:
    review_raw = REVIEW_PATH.read_bytes() if REVIEW_PATH.exists() else None
    acceptance_raw = ACCEPTANCE_PATH.read_bytes() if ACCEPTANCE_PATH.exists() else None
    state = _lifecycle_state(review_raw, acceptance_raw)
    assert state in {
        "AUTHORITY_ONLY_NO_PRODUCT_BYTES",
        "REVIEW_PASS",
        "REVIEW_REWORK",
        "ACCEPTED_AUTHORITY_ONLY_NO_PRODUCT_BYTES",
    }


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("unknown", "forbidden"),
        lambda value: value.pop("prohibitions"),
        lambda value: value["bound_inputs"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["aggregate_materialization"]["implemented_schema_bundle_v2"][
            "required_root_roles"
        ].append("EXTRA_ROOT"),
        lambda value: value["build_identity"]["pre_build_projection_keys"].append(
            "twenty_sixth_key"
        ),
        lambda value: value["receipt_contracts"]["rebuild_invocation_receipt"]["keys"].pop(),
        lambda value: value["receipt_contracts"]["temporal_boundary_receipt"]["keys"].reverse(),
        lambda value: value["layer_manifest_authority"]["manifest_semantic_derivation"][
            "preimage_keys"
        ].append("second_derivation"),
        lambda value: value["feature_scope"]["supported_feature_names"].append(
            "unapproved_feature"
        ),
        lambda value: value["lifecycle"].__setitem__("product_bytes_permitted", True),
    ],
)
def test_direct_authority_mutations_fail_closed(mutation: Any) -> None:
    decision, _ = _load_decision()
    mutated = deepcopy(decision)
    mutation(mutated)
    with pytest.raises(ValueError, match="differ"):
        _validate_decision(mutated)


def test_duplicate_key_and_noncanonical_authority_bytes_fail_closed() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        _load_canonical_json(b'{"a":1,"a":1}\n')
    with pytest.raises(ValueError, match="noncanonical"):
        _load_canonical_json(b'{"a": 1}\n')


def test_authority_load_is_side_effect_free_for_repository_destinations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _snapshot_destination_state(PRODUCT_DESTINATIONS)
    writer_calls = _deny_writer_calls(monkeypatch)
    decision, _ = _load_decision()
    after = _snapshot_destination_state(PRODUCT_DESTINATIONS)

    assert before == after
    assert writer_calls == []
    assert decision["lifecycle"]["product_bytes_permitted"] is False
    assert "PRODUCT_CONTROL_DATA_BUILD_MANIFEST_OR_RECEIPT_WRITE" in decision["prohibitions"]
    assert "PRODUCT_PUBLICATION" in decision["prohibitions"]


@pytest.mark.parametrize("preexisting", [False, True])
def test_authority_load_preserves_simulated_absent_and_existing_products(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    preexisting: bool,
) -> None:
    destinations = tuple(
        tmp_path / relative
        for relative in (
            "working/bronze",
            "working/silver",
            "working/gold",
            "manifests/bronze",
            "manifests/silver",
            "manifests/gold",
            "runs/rebuild",
        )
    )
    sentinel = destinations[1] / "existing-product.bin"
    if preexisting:
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b"simulated-pre-existing-product\n")

    before = _snapshot_destination_state(destinations)
    writer_calls = _deny_writer_calls(monkeypatch)
    decision, _ = _load_decision()
    after = _snapshot_destination_state(destinations)

    assert before == after
    assert writer_calls == []
    assert decision["lifecycle"]["state"] == "AUTHORITY_ONLY_NO_PRODUCT_BYTES"
    assert decision["lifecycle"]["product_bytes_permitted"] is False
    if preexisting:
        assert sentinel.read_bytes() == b"simulated-pre-existing-product\n"

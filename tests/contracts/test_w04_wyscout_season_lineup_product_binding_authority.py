"""Closed tests for the additive W04 season/lineup product-binding authority."""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Callable
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-decisions-v1.json"
)
REVIEW_PATH = (
    ROOT / "reports/reviews/W04/authorities/"
    "wyscout-season-lineup-product-binding-independent-review-R1.md"
)
ACCEPTANCE_PATH = (
    ROOT / "reports/reviews/W04/authorities/"
    "wyscout-season-lineup-product-binding-acceptance-v1.json"
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

DECISION_ID = "w04-wyscout-season-lineup-product-binding-decisions-v1"
DECISION_SCHEMA_VERSION = "w04-wyscout-season-lineup-product-binding-decision-v1"
EXPECTED_DECISION_PHYSICAL_SHA256 = (
    "3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e"
)
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
REVIEW_ID = "w04-wyscout-season-lineup-product-binding-independent-review-R1"
REVIEW_SCHEMA_VERSION = "w04-season-lineup-product-binding-independent-review-v1"
ACCEPTANCE_ID = "w04-wyscout-season-lineup-product-binding-acceptance-v1"
ACCEPTANCE_SCHEMA_VERSION = "w04-season-lineup-product-binding-acceptance-v1"
TEST_REVIEWER_ID = "a66fa478-73f1-534c-8d96-8569786631e5"
FUTURE_TOLERANCE = timedelta(minutes=5)

EXPECTED_BOUND_INPUTS = [
    (
        "reports/verification/W04/wyscout-season-lineup-correction-authorization-R1.md",
        "9802e4ae037593c62db2b52d38acd4133e5a3d50e59e5ad346c982ad8cca47bb",
    ),
    (
        "reports/reviews/W04/authorities/wyscout-build-product-authority-decisions-v1.json",
        "3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d",
    ),
    (
        "reports/reviews/W04/authorities/wyscout-build-product-independent-review-R1.md",
        "f780a1e4e6043562e9aa342559350eabbaeef3915c64280b096a08d160e522e9",
    ),
    (
        "reports/reviews/W04/authorities/wyscout-build-product-authority-acceptance-v1.json",
        "9bcd9ef6f61b06f443a4d8f0d590db74559ee739976f285c41127da5ff1f5921",
    ),
    (
        "reports/verification/W04/wyscout-build-product-authority-R1-master-acceptance.md",
        "a58f9b97e085a283ae1d26b7168d4f62c3e2366847ba8f2b482355443602d36a",
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
        "data/manifests/wyscout/v5/source/"
        "4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json",
        "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd",
    ),
    (
        "data/manifests/wyscout/v5/source-completion/"
        "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df."
        "source-completion-index.json",
        "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df",
    ),
    (
        "src/scouting/contracts/wyscout_data.py",
        "154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932",
    ),
]

TOP_LEVEL_KEYS = {
    "authority_class",
    "bound_inputs",
    "build_projection_binding",
    "decided_at",
    "decided_by",
    "decision_id",
    "decision_schema_version",
    "lifecycle",
    "lineup_population",
    "prohibitions",
    "season_binding",
    "source_binding",
}
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
EXPECTED_LINEUP_ROW: dict[str, Any] = {
    "elapsed_minutes": None,
    "end_interval": None,
    "lineup_stint_id": "591cdf5b-2281-53c4-8225-150313ca2c01",
    "lineup_stint_uuid_name": "stint:1631:285508:0:w04-wyscout-lineup-stint-v1",
    "lineup_stint_uuid_namespace": {
        "algorithm": "UUIDV5",
        "kind_name": "match",
        "match_namespace": "20b5206f-dfa5-55b4-84ab-8a336a75073e",
        "source_namespace": "89161938-1e8c-53ab-ab52-eba969681833",
        "source_namespace_name": (
            "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5"
        ),
    },
    "lower_bound_minutes": None,
    "match_id": "bad97950-6fac-5cf0-a93c-094f91abbb9b",
    "match_source_id": 2499719,
    "per90_eligible": False,
    "player_id": "be8da881-2b15-513f-978f-6bb3865bc8e2",
    "player_source_id": 285508,
    "right_censored": True,
    "ruleset_version": "w04-wyscout-lineup-stint-v1",
    "start_interval": {"lower": 82, "upper": 83},
    "stint_ordinal": 0,
    "suppression_reason": "suppressed_unsupported_denominator",
    "team_id": "5b353635-819b-5bd1-8ca2-5a7364042a96",
    "team_source_id": 1631,
    "upper_bound_minutes": None,
}
COMPLETE_POPULATION_POLICY = [
    "REJECT_OMISSION",
    "REJECT_ADDITION",
    "REJECT_DUPLICATION",
    "REJECT_REORDERING",
    "REJECT_ALTERNATE_STINT_ORDINAL",
    "REJECT_INFERRED_TERMINAL_INTERVAL",
    "REJECT_INFERRED_MINUTES",
    "REJECT_PER90_ELIGIBILITY",
    "REJECT_ANOTHER_SEASON_MATCH_TEAM_PLAYER_OR_STINT",
]
PROHIBITIONS = [
    "NO_SECOND_SEASON_SEMANTIC_DERIVATION",
    "NO_SEASON_IDENTITY_BUNDLE_KIND_OR_ROW",
    "NO_NEW_SCHEMA_ROOT",
    "NO_NEW_SUPPORTED_FEATURE",
    "NO_NEW_GOLD_ROW",
    "NO_WIDER_PRODUCT_POPULATION",
    "NO_TWENTY_SIXTH_BUILD_PROJECTION_KEY",
    "NO_ALTERED_BUILD_HASH",
    "NO_RUNTIME_SCHEMA_AGGREGATE_PRODUCT_MANIFEST_RECEIPT_OR_BUILD_BYTES",
    "NO_PROVIDER_NETWORK_REMOTE_CLOUD_CONTAINER_CI_DEPLOYMENT_OR_PUBLICATION",
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


def _validate_population(population: object) -> None:
    if type(population) is not dict or set(population) != {
        "complete_population_policy",
        "ordered_population",
        "population_cardinality",
        "population_scope",
    }:
        raise ValueError("lineup population differs")
    if (
        population["complete_population_policy"] != COMPLETE_POPULATION_POLICY
        or population["population_cardinality"] != 1
        or type(population["population_cardinality"]) is not int
        or population["population_scope"]
        != "ONLY_EXACT_AUTHORIZED_W04_SELECTED_MATCH_PLAYER_LINEUP_STINT"
        or population["ordered_population"] != [EXPECTED_LINEUP_ROW]
    ):
        raise ValueError("lineup population differs")
    row = population["ordered_population"][0]
    for key in (
        "match_source_id",
        "player_source_id",
        "team_source_id",
        "stint_ordinal",
    ):
        if type(row[key]) is not int:
            raise ValueError("lineup scalar type differs")
    for key in ("right_censored", "per90_eligible"):
        if type(row[key]) is not bool:
            raise ValueError("lineup scalar type differs")
    if any(
        row[key] is not None
        for key in (
            "end_interval",
            "lower_bound_minutes",
            "upper_bound_minutes",
            "elapsed_minutes",
        )
    ):
        raise ValueError("right-censored lineup fields differ")


def _validate_decision(value: dict[str, Any], *, enforce_digest: bool = True) -> None:
    if enforce_digest and (
        sha256(_canonical_json_bytes(value)).hexdigest() != EXPECTED_DECISION_PHYSICAL_SHA256
    ):
        raise ValueError("decision digest differs")
    if set(value) != TOP_LEVEL_KEYS:
        raise ValueError("decision keys differ")
    if (
        value["authority_class"] != "SEASON_LINEUP_PRODUCT_BINDING"
        or value["decision_id"] != DECISION_ID
        or value["decision_schema_version"] != DECISION_SCHEMA_VERSION
    ):
        raise ValueError("decision scalar differs")
    _validate_actor(value["decided_by"], expected=MASTER_ACTOR_ID)
    _parse_clock(value["decided_at"], truthful=True)
    if any(
        type(row) is not dict or set(row) != {"path", "sha256"} for row in value["bound_inputs"]
    ):
        raise ValueError("bound input row differs")
    observed = [(row["path"], row["sha256"]) for row in value["bound_inputs"]]
    if observed != EXPECTED_BOUND_INPUTS:
        raise ValueError("bound inputs differ")

    build = value["build_projection_binding"]
    if set(build) != {
        "allowed_consumption_member",
        "build_hash_rule",
        "integration_policy",
        "post_hash_invocation_key_count",
        "pre_build_projection_key_count",
        "pre_build_projection_keys",
        "projection_schema_version",
        "second_build_hash",
    }:
        raise ValueError("build projection keys differ")
    if (
        build["allowed_consumption_member"] != "authority_rows"
        or build["integration_policy"]
        != "APPEND_ACCEPTED_AUTHORITY_REFERENCE_ONLY_WITHIN_EXISTING_AUTHORITY_ROWS_MEMBER"
        or build["build_hash_rule"] != "UNCHANGED_SHA256_OF_R20_CANONICAL_JSON_WITHOUT_TERMINAL_LF"
        or build["pre_build_projection_keys"] != PROJECTION_KEYS
        or type(build["pre_build_projection_key_count"]) is not int
        or build["pre_build_projection_key_count"] != len(PROJECTION_KEYS) != 26
        or type(build["post_hash_invocation_key_count"]) is not int
        or build["post_hash_invocation_key_count"] != 25
        or build["projection_schema_version"] != "w04-wyscout-pre-build-projection-v1"
        or build["second_build_hash"] != "FORBIDDEN"
    ):
        raise ValueError("build projection differs")

    season = value["season_binding"]
    if set(season) != {
        "canonical_name",
        "canonical_season_id",
        "derivation",
        "identity_bundle_kind_added",
        "season_source_id",
        "season_source_json_type",
        "second_derivation",
    }:
        raise ValueError("season keys differ")
    if (
        season["canonical_name"] != "figshare-v5:181150"
        or season["canonical_season_id"] != "4696aa1f-b512-5d18-af79-33cf031455cf"
        or type(season["season_source_id"]) is not int
        or season["season_source_id"] != 181150
        or season["season_source_json_type"] != "integer"
        or season["identity_bundle_kind_added"] is not False
        or season["second_derivation"] != "FORBIDDEN"
        or season["derivation"]
        != {
            "algorithm": "UUIDV5",
            "season_namespace": "afb775b9-a955-5bfc-80cd-3e941ca2f098",
            "season_namespace_name": "season",
            "source_namespace": "89161938-1e8c-53ab-ab52-eba969681833",
            "source_namespace_name": (
                "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5"
            ),
        }
    ):
        raise ValueError("season binding differs")

    _validate_population(value["lineup_population"])
    if value["prohibitions"] != PROHIBITIONS:
        raise ValueError("prohibitions differ")

    source = value["source_binding"]
    if source != {
        "completion_index_path": (
            "data/manifests/wyscout/v5/source-completion/"
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df."
            "source-completion-index.json"
        ),
        "completion_index_sha256": (
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
        ),
        "match_member_path": "archive-members/matches_England.json",
        "match_member_row_count": 380,
        "match_member_sha256": ("620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29"),
        "match_member_size_bytes": 1694720,
        "match_raw_record_sha256": (
            "1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86"
        ),
        "match_source_id": 2499719,
        "source_manifest_id": "4e16bdb5-afe7-5601-88ad-adc124cfce3b",
        "source_manifest_path": (
            "data/manifests/wyscout/v5/source/"
            "4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json"
        ),
        "source_manifest_sha256": (
            "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
        ),
        "source_record_ordinal": 379,
    }:
        raise ValueError("source binding differs")
    for key in (
        "match_member_row_count",
        "match_member_size_bytes",
        "match_source_id",
        "source_record_ordinal",
    ):
        if type(source[key]) is not int:
            raise ValueError("source scalar type differs")

    lifecycle = value["lifecycle"]
    if (
        set(lifecycle)
        != {"independent_review", "master_acceptance", "product_bytes_permitted", "state"}
        or lifecycle["state"] != "AUTHORITY_ONLY_NO_PRODUCT_BYTES"
        or lifecycle["product_bytes_permitted"] is not False
        or lifecycle["independent_review"]
        != {
            "allowed_absent_in_states": ["AUTHORITY_ONLY_NO_PRODUCT_BYTES"],
            "path": (
                "reports/reviews/W04/authorities/"
                "wyscout-season-lineup-product-binding-independent-review-R1.md"
            ),
            "required_before_acceptance": True,
            "review_id": REVIEW_ID,
            "review_schema_version": REVIEW_SCHEMA_VERSION,
        }
        or lifecycle["master_acceptance"]
        != {
            "acceptance_id": ACCEPTANCE_ID,
            "acceptance_schema_version": ACCEPTANCE_SCHEMA_VERSION,
            "allowed_absent_in_states": ["AUTHORITY_ONLY_NO_PRODUCT_BYTES"],
            "path": (
                "reports/reviews/W04/authorities/"
                "wyscout-season-lineup-product-binding-acceptance-v1.json"
            ),
            "required_before_product_implementation": True,
        }
    ):
        raise ValueError("lifecycle differs")


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
    marker = b"```w04-season-lineup-product-binding-review-v1\n"
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
        "reviewed_at": "2026-08-01T12:16:00Z",
        "reviewed_by": TEST_REVIEWER_ID,
    }
    body = _canonical_json_bytes(record)
    raw = b"Independent review.\n\n```w04-season-lineup-product-binding-review-v1\n"
    raw += body + b"```\n"
    return record, body, raw


def _valid_acceptance(decision_raw: bytes, review_raw: bytes, review_record_raw: bytes) -> bytes:
    return _canonical_json_bytes(
        {
            "acceptance_id": ACCEPTANCE_ID,
            "acceptance_schema_version": ACCEPTANCE_SCHEMA_VERSION,
            "accepted_at": "2026-08-01T12:17:00Z",
            "accepted_by": MASTER_ACTOR_ID,
            "decision_id": DECISION_ID,
            "decision_physical_sha256": sha256(decision_raw).hexdigest(),
            "review_id": REVIEW_ID,
            "review_physical_sha256": sha256(review_raw).hexdigest(),
            "review_record_sha256": sha256(review_record_raw).hexdigest(),
            "review_recommendation": "PASS",
        }
    )


def test_decision_is_canonical_closed_and_binds_every_frozen_input() -> None:
    decision, raw = _load_decision()
    assert sha256(raw).hexdigest() == EXPECTED_DECISION_PHYSICAL_SHA256
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert set(decision) == TOP_LEVEL_KEYS
    assert len(decision["bound_inputs"]) == len(EXPECTED_BOUND_INPUTS) == 10
    for path_text, expected_sha256 in EXPECTED_BOUND_INPUTS:
        assert sha256((ROOT / path_text).read_bytes()).hexdigest() == expected_sha256


def test_season_and_lineup_uuidv5_chains_reproduce_independently() -> None:
    decision, _ = _load_decision()
    source_name = decision["season_binding"]["derivation"]["source_namespace_name"]
    source_namespace = uuid5(NAMESPACE_URL, source_name)
    assert str(source_namespace) == "89161938-1e8c-53ab-ab52-eba969681833"

    season_namespace = uuid5(source_namespace, "season")
    assert str(season_namespace) == "afb775b9-a955-5bfc-80cd-3e941ca2f098"
    assert str(uuid5(season_namespace, "figshare-v5:181150")) == (
        "4696aa1f-b512-5d18-af79-33cf031455cf"
    )

    match_namespace = uuid5(source_namespace, "match")
    assert str(match_namespace) == "20b5206f-dfa5-55b4-84ab-8a336a75073e"
    assert str(uuid5(match_namespace, "figshare-v5:2499719")) == (
        "bad97950-6fac-5cf0-a93c-094f91abbb9b"
    )
    assert str(uuid5(uuid5(source_namespace, "team"), "figshare-v5:1631")) == (
        "5b353635-819b-5bd1-8ca2-5a7364042a96"
    )
    assert str(uuid5(uuid5(source_namespace, "player"), "figshare-v5:285508")) == (
        "be8da881-2b15-513f-978f-6bb3865bc8e2"
    )
    lineup = decision["lineup_population"]["ordered_population"][0]
    assert str(uuid5(match_namespace, lineup["lineup_stint_uuid_name"])) == (
        "591cdf5b-2281-53c4-8225-150313ca2c01"
    )


def test_source_manifest_match_member_raw_row_and_lineup_evidence_are_exact() -> None:
    decision, _ = _load_decision()
    binding = decision["source_binding"]
    manifest_raw = (ROOT / binding["source_manifest_path"]).read_bytes()
    manifest = json.loads(manifest_raw)
    assert sha256(manifest_raw).hexdigest() == binding["source_manifest_sha256"]
    assert manifest["manifest_id"] == binding["source_manifest_id"]
    member = next(
        row for row in manifest["files"] if row["object_path"] == binding["match_member_path"]
    )
    assert member == {
        "object_path": binding["match_member_path"],
        "row_count": binding["match_member_row_count"],
        "sha256": binding["match_member_sha256"],
        "size_bytes": binding["match_member_size_bytes"],
    }

    member_path = ROOT / "data/source/wyscout/v5" / binding["match_member_path"]
    member_raw = member_path.read_bytes()
    rows = json.loads(member_raw)
    assert sha256(member_raw).hexdigest() == binding["match_member_sha256"]
    assert len(rows) == binding["match_member_row_count"]
    raw_match = rows[binding["source_record_ordinal"]]
    raw_match_digest = sha256(
        json.dumps(raw_match, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()
    assert raw_match_digest == binding["match_raw_record_sha256"]
    assert type(raw_match["wyId"]) is int and raw_match["wyId"] == 2499719
    assert type(raw_match["seasonId"]) is int and raw_match["seasonId"] == 181150

    team = raw_match["teamsData"]["1631"]
    assert sum(row["playerId"] == 285508 for row in team["formation"]["bench"]) == 1
    substitutions = [row for row in team["formation"]["substitutions"] if row["playerIn"] == 285508]
    assert substitutions == [{"minute": 82, "playerIn": 285508, "playerOut": 192748}]


def test_completion_index_and_source_binding_are_content_addressed() -> None:
    decision, _ = _load_decision()
    binding = decision["source_binding"]
    index_raw = (ROOT / binding["completion_index_path"]).read_bytes()
    index = json.loads(index_raw)
    assert sha256(index_raw).hexdigest() == binding["completion_index_sha256"]
    assert index["source_manifest_id"] == binding["source_manifest_id"]
    assert index["source_manifest_sha256"] == binding["source_manifest_sha256"]


def test_complete_lineup_population_is_exactly_one_right_censored_row() -> None:
    decision, _ = _load_decision()
    population = decision["lineup_population"]
    _validate_population(population)
    assert population["population_cardinality"] == len(population["ordered_population"]) == 1
    row = population["ordered_population"][0]
    assert row == EXPECTED_LINEUP_ROW
    assert row["start_interval"] == {"lower": 82, "upper": 83}
    assert row["end_interval"] is None and row["right_censored"] is True
    assert row["per90_eligible"] is False
    assert row["suppression_reason"] == "suppressed_unsupported_denominator"


def test_only_existing_authority_rows_member_may_consume_the_binding() -> None:
    decision, _ = _load_decision()
    build = decision["build_projection_binding"]
    assert build["allowed_consumption_member"] == "authority_rows"
    assert build["pre_build_projection_keys"] == PROJECTION_KEYS
    assert len(build["pre_build_projection_keys"]) == 25
    assert build["pre_build_projection_key_count"] == 25
    assert build["post_hash_invocation_key_count"] == 25
    assert build["second_build_hash"] == "FORBIDDEN"
    assert decision["season_binding"]["identity_bundle_kind_added"] is False
    assert decision["season_binding"]["second_derivation"] == "FORBIDDEN"
    assert decision["prohibitions"] == PROHIBITIONS


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["ordered_population"].clear(),
        lambda value: value["ordered_population"].append(deepcopy(EXPECTED_LINEUP_ROW)),
        lambda value: value["ordered_population"][0].__setitem__("stint_ordinal", 1),
        lambda value: value["ordered_population"][0].__setitem__(
            "end_interval", {"lower": 90, "upper": 91}
        ),
        lambda value: value["ordered_population"][0].__setitem__("lower_bound_minutes", 0),
        lambda value: value["ordered_population"][0].__setitem__("elapsed_minutes", 8),
        lambda value: value["ordered_population"][0].__setitem__("per90_eligible", True),
        lambda value: value["ordered_population"][0].__setitem__("player_source_id", 285509),
        lambda value: value["ordered_population"][0].__setitem__("match_source_id", 2499720),
        lambda value: value.__setitem__("population_cardinality", True),
    ],
)
def test_lineup_population_mutations_fail_closed(
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    decision, _ = _load_decision()
    population = deepcopy(decision["lineup_population"])
    mutation(population)
    with pytest.raises(ValueError, match="differ"):
        _validate_population(population)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("unknown", "forbidden"),
        lambda value: value.pop("prohibitions"),
        lambda value: value["bound_inputs"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["season_binding"].__setitem__("season_source_id", "181150"),
        lambda value: value["season_binding"].__setitem__("season_source_id", True),
        lambda value: value["season_binding"].__setitem__("second_derivation", "ALLOWED"),
        lambda value: value["build_projection_binding"]["pre_build_projection_keys"].append(
            "twenty_sixth_key"
        ),
        lambda value: value["build_projection_binding"].__setitem__(
            "allowed_consumption_member", "season_authority"
        ),
        lambda value: value["lifecycle"].__setitem__("product_bytes_permitted", True),
    ],
)
def test_direct_authority_mutations_fail_closed(
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    decision, _ = _load_decision()
    mutated = deepcopy(decision)
    mutation(mutated)
    with pytest.raises(ValueError, match="differ"):
        _validate_decision(mutated, enforce_digest=False)


def test_lifecycle_allows_absence_and_fails_closed_when_malformed() -> None:
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
    malformed_raw = b"```w04-season-lineup-product-binding-review-v1\n"
    malformed_raw += _canonical_json_bytes(malformed) + b"```\n"
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
    assert (
        "NO_RUNTIME_SCHEMA_AGGREGATE_PRODUCT_MANIFEST_RECEIPT_OR_BUILD_BYTES"
        in (decision["prohibitions"])
    )


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

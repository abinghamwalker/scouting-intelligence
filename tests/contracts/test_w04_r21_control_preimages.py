"""Exact contract for the descriptor-only W04 R21 control preimages."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
PRODUCT_PATH = ROOT / "configs/schema/wyscout-v5-product-contract-preimage-v1.json"
SCHEMA_PATH = ROOT / "configs/schema/wyscout-v5-schema-bundle-preimage-v1.json"

R20_ID = "w04-wyscout-schema-design-R20"
R20_SHA256 = "8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047"
R21_ID = "w04-wyscout-schema-design-R21"
R21_SHA256 = "faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020"
PRODUCT_ID = "w04-wyscout-product-contract-preimage-v1"
SCHEMA_ID = "w04-wyscout-schema-bundle-preimage-v1"
PRODUCT_SHA256 = "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293"
SCHEMA_SHA256 = "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f"
SURFACE_KIND = "CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA"

AUTHORITY_LINKS = {
    "r20_authority_id": R20_ID,
    "r20_authority_sha256": R20_SHA256,
    "r21_authority_id": R21_ID,
    "r21_authority_sha256": R21_SHA256,
}

PATH_TEMPLATES = (
    (
        "BRONZE_KNOWN_RECORD",
        "data/working/wyscout/v5/bronze/build_id=<build_id>/records/"
        "record_kind=<known-kind>/source_sha256=<source_sha>/part-00000.parquet",
    ),
    (
        "BRONZE_REJECTED_RECORD",
        "data/working/wyscout/v5/bronze/build_id=<build_id>/quarantine/"
        "rejected-record/record_kind=unknown/raw_kind_state=<closed-state-token>/"
        "raw_kind_sha256=<64-lowercase-hex>/source_sha256=<source_sha>/"
        "part-00000.parquet",
    ),
    (
        "BRONZE_REJECTED_FIELD",
        "data/working/wyscout/v5/bronze/build_id=<build_id>/quarantine/"
        "rejected-field/record_kind=<known-kind>/source_sha256=<source_sha>/"
        "part-00000.parquet",
    ),
    (
        "SILVER_COMPETITION",
        "data/working/wyscout/v5/silver/build_id=<build_id>/competition/"
        "source_partition=global/part-00000.parquet",
    ),
    (
        "SILVER_TEAM",
        "data/working/wyscout/v5/silver/build_id=<build_id>/team/"
        "source_partition=global/part-00000.parquet",
    ),
    (
        "SILVER_PLAYER",
        "data/working/wyscout/v5/silver/build_id=<build_id>/player/"
        "source_partition=global/part-00000.parquet",
    ),
    (
        "SILVER_MATCH",
        "data/working/wyscout/v5/silver/build_id=<build_id>/match/"
        "source_partition=<country>/part-00000.parquet",
    ),
    (
        "SILVER_ACTION",
        "data/working/wyscout/v5/silver/build_id=<build_id>/action/"
        "source_partition=<country>/part-00000.parquet",
    ),
    (
        "SILVER_LINEUP_STINT",
        "data/working/wyscout/v5/silver/build_id=<build_id>/lineup-stint/"
        "source_partition=<country>/part-00000.parquet",
    ),
    (
        "SILVER_POSSESSION",
        "data/working/wyscout/v5/silver/build_id=<build_id>/possession/"
        "source_partition=<country>/part-00000.parquet",
    ),
    (
        "SILVER_PLAYER_MATCH_FACT",
        "data/working/wyscout/v5/silver/build_id=<build_id>/player-match-fact/"
        "source_partition=<country>/part-00000.parquet",
    ),
    (
        "GOLD_PLAYER_WINDOW",
        "data/working/wyscout/v5/gold/build_id=<build_id>/player-window/"
        "competition_id=<uuid>/window_definition_id=<uuid>/window_start_utc=<utc>/"
        "window_end_utc=<utc>/feature_cutoff_ts=<utc>/part-00000.parquet",
    ),
    (
        "BRONZE_MANIFEST",
        "data/manifests/wyscout/v5/bronze/<build_id>.manifest.json",
    ),
    (
        "SILVER_MANIFEST",
        "data/manifests/wyscout/v5/silver/<build_id>.manifest.json",
    ),
    ("GOLD_MANIFEST", "data/manifests/wyscout/v5/gold/<build_id>.manifest.json"),
    (
        "REBUILD_INVOCATION_RECEIPT",
        "runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json",
    ),
    (
        "TEMPORAL_BOUNDARY_RECEIPT",
        "runs/w04/wyscout-rebuild/<build_id>/<run_id>/boundary/"
        "<sha256-of-exact-gold-relative-path>.temporal-boundary-receipt.json",
    ),
)

SERIALIZER_OWNERSHIP = (
    ("actions.py", ("SILVER_ACTION",)),
    (
        "bronze.py",
        (
            "BRONZE_KNOWN_RECORD",
            "BRONZE_REJECTED_RECORD",
            "BRONZE_REJECTED_FIELD",
            "BRONZE_MANIFEST",
        ),
    ),
    (
        "entities.py",
        ("SILVER_COMPETITION", "SILVER_TEAM", "SILVER_PLAYER", "SILVER_MATCH"),
    ),
    ("gold.py", ("GOLD_PLAYER_WINDOW", "GOLD_MANIFEST")),
    ("lineups.py", ("SILVER_LINEUP_STINT",)),
    ("player_match.py", ("SILVER_PLAYER_MATCH_FACT",)),
    ("possessions.py", ("SILVER_POSSESSION",)),
    ("rebuild.py", ("REBUILD_INVOCATION_RECEIPT",)),
    ("silver_manifest.py", ("SILVER_MANIFEST",)),
    ("temporal_boundary.py", ("TEMPORAL_BOUNDARY_RECEIPT",)),
)

PRIMARY_KEYS = (
    (
        "SILVER_PLAYER_MATCH_FACT",
        (
            "tenant_id",
            "source_manifest_id",
            "match_id",
            "player_id",
            "player_match_fact_schema_version",
        ),
    ),
    (
        "GOLD_PLAYER_WINDOW",
        (
            "tenant_id",
            "player_id",
            "competition_id",
            "season_id",
            "role_context_id",
            "role_context_version",
            "window_definition_id",
            "window_start_utc",
            "window_end_utc",
            "feature_cutoff_ts",
            "dependency_lineage_hash",
        ),
    ),
)

MANIFEST_RECEIPTS = (
    (
        "BRONZE_MANIFEST",
        "bronze.py",
        "data/manifests/wyscout/v5/bronze/<build_id>.manifest.json",
    ),
    (
        "SILVER_MANIFEST",
        "silver_manifest.py",
        "data/manifests/wyscout/v5/silver/<build_id>.manifest.json",
    ),
    (
        "GOLD_MANIFEST",
        "gold.py",
        "data/manifests/wyscout/v5/gold/<build_id>.manifest.json",
    ),
    (
        "REBUILD_INVOCATION_RECEIPT",
        "rebuild.py",
        "runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json",
    ),
    (
        "TEMPORAL_BOUNDARY_RECEIPT",
        "temporal_boundary.py",
        "runs/w04/wyscout-rebuild/<build_id>/<run_id>/boundary/"
        "<sha256-of-exact-gold-relative-path>.temporal-boundary-receipt.json",
    ),
)

DESCRIPTORS = (
    (
        "w04-source-record-envelope",
        "w04-source-record-envelope-v1",
        "SOURCE_RECORD_ENVELOPE",
        (),
    ),
    (
        "w04-wyscout-bronze-known-record",
        "w04-wyscout-bronze-known-record-descriptor-v1",
        "BRONZE_KNOWN_RECORD",
        ("w04-source-record-envelope",),
    ),
    (
        "w04-wyscout-bronze-rejected-record",
        "w04-raw-kind-v1",
        "BRONZE_REJECTED_RECORD",
        ("w04-source-record-envelope",),
    ),
    (
        "w04-wyscout-bronze-rejected-field",
        "w04-wyscout-bronze-rejected-field-descriptor-v1",
        "BRONZE_REJECTED_FIELD",
        ("w04-wyscout-bronze-known-record",),
    ),
    (
        "w04-wyscout-silver-competition",
        "w04-wyscout-silver-competition-descriptor-v1",
        "SILVER_COMPETITION",
        ("w04-wyscout-bronze-known-record",),
    ),
    (
        "w04-wyscout-silver-team",
        "w04-wyscout-silver-team-descriptor-v1",
        "SILVER_TEAM",
        ("w04-wyscout-bronze-known-record",),
    ),
    (
        "w04-wyscout-silver-player",
        "w04-wyscout-silver-player-descriptor-v1",
        "SILVER_PLAYER",
        ("w04-wyscout-bronze-known-record",),
    ),
    (
        "w04-wyscout-silver-match",
        "w04-wyscout-silver-match-descriptor-v1",
        "SILVER_MATCH",
        (
            "w04-wyscout-bronze-known-record",
            "w04-wyscout-silver-competition",
            "w04-wyscout-silver-team",
        ),
    ),
    (
        "w04-wyscout-silver-action",
        "w04-wyscout-silver-action-descriptor-v1",
        "SILVER_ACTION",
        (
            "w04-wyscout-bronze-known-record",
            "w04-wyscout-silver-match",
            "w04-wyscout-silver-player",
            "w04-wyscout-silver-team",
        ),
    ),
    (
        "w04-wyscout-silver-lineup-stint",
        "w04-wyscout-silver-lineup-stint-descriptor-v1",
        "SILVER_LINEUP_STINT",
        (
            "w04-wyscout-silver-match",
            "w04-wyscout-silver-player",
            "w04-wyscout-silver-team",
        ),
    ),
    (
        "w04-wyscout-silver-possession",
        "w04-wyscout-silver-possession-descriptor-v1",
        "SILVER_POSSESSION",
        ("w04-wyscout-silver-action",),
    ),
    (
        "w04-wyscout-silver-player-match-fact",
        "w04-wyscout-silver-player-match-fact-descriptor-v1",
        "SILVER_PLAYER_MATCH_FACT",
        (
            "w04-wyscout-silver-action",
            "w04-wyscout-silver-lineup-stint",
            "w04-wyscout-silver-match",
            "w04-wyscout-silver-player",
            "w04-wyscout-silver-possession",
        ),
    ),
    (
        "w04-wyscout-gold-player-window",
        "w04-wyscout-gold-player-window-descriptor-v1",
        "GOLD_PLAYER_WINDOW",
        ("w04-wyscout-silver-player-match-fact",),
    ),
    (
        "w04-wyscout-layer-manifest",
        "w04-wyscout-layer-manifest-descriptor-v1",
        "LAYER_MANIFEST",
        (
            "w04-wyscout-bronze-known-record",
            "w04-wyscout-bronze-rejected-record",
            "w04-wyscout-bronze-rejected-field",
            "w04-wyscout-silver-competition",
            "w04-wyscout-silver-team",
            "w04-wyscout-silver-player",
            "w04-wyscout-silver-match",
            "w04-wyscout-silver-action",
            "w04-wyscout-silver-lineup-stint",
            "w04-wyscout-silver-possession",
            "w04-wyscout-silver-player-match-fact",
            "w04-wyscout-gold-player-window",
        ),
    ),
    (
        "w04-wyscout-rebuild-invocation-receipt",
        "w04-rebuild-invocation-v1",
        "REBUILD_INVOCATION_RECEIPT",
        ("w04-wyscout-layer-manifest",),
    ),
    (
        "w04-wyscout-temporal-boundary-receipt",
        "w04-wyscout-temporal-boundary-receipt-descriptor-v1",
        "TEMPORAL_BOUNDARY_RECEIPT",
        ("w04-wyscout-gold-player-window", "w04-wyscout-layer-manifest"),
    ),
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


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


def _load(path: Path) -> tuple[bytes, dict[str, Any]]:
    physical = path.read_bytes()
    assert physical.endswith(b"\n")
    assert not physical.endswith(b"\n\n")
    assert b"\r" not in physical
    assert physical.count(b"\n") == 1
    parsed = json.loads(physical)
    assert isinstance(parsed, dict)
    return physical, parsed


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
            raise AssertionError("preimage evaluation attempted a writer call")
        return original_open(path, mode, *args, **kwargs)

    def unexpected_writer(path: Path, *args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        writer_calls.append(f"{path}")
        raise AssertionError("preimage evaluation attempted a writer call")

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


def _walk(value: object) -> list[object]:
    values = [value]
    if isinstance(value, dict):
        for key, child in value.items():
            values.extend((key, *_walk(child)))
    elif isinstance(value, list):
        for child in value:
            values.extend(_walk(child))
    return values


@pytest.mark.parametrize(
    ("path", "expected_sha256"),
    ((PRODUCT_PATH, PRODUCT_SHA256), (SCHEMA_PATH, SCHEMA_SHA256)),
)
def test_physical_bytes_are_exact_canonical_utf8(path: Path, expected_sha256: str) -> None:
    physical, parsed = _load(path)
    physical.decode("utf-8", errors="strict")
    assert physical == _canonical_bytes(parsed)
    assert sha256(physical).hexdigest() == expected_sha256
    assert sha256(_canonical_bytes(parsed)).hexdigest() == expected_sha256
    for value in _walk(parsed):
        if isinstance(value, str):
            assert unicodedata.normalize("NFC", value) == value


def test_product_contract_has_exact_closed_content_and_cardinalities() -> None:
    _, product = _load(PRODUCT_PATH)
    assert list(product) == [
        "authority_links",
        "layer_order",
        "manifest_receipt_templates",
        "path_templates",
        "policy",
        "preimage_id",
        "preimage_schema_version",
        "primary_key_contracts",
        "serializer_ownership",
    ]
    assert product["authority_links"] == AUTHORITY_LINKS
    assert product["layer_order"] == ["BRONZE", "SILVER", "GOLD"]
    assert product["preimage_id"] == PRODUCT_ID
    assert product["preimage_schema_version"] == "w04-product-contract-preimage-v1"
    assert product["policy"] == {
        "control_plane_only": True,
        "no_product_before_gate": "R21_COMPLETE_GATE_PASS",
        "product_bytes_forbidden": True,
    }

    path_rows = product["path_templates"]
    assert len(path_rows) == 17
    assert all(list(row) == ["path_role", "relative_template"] for row in path_rows)
    assert (
        tuple((row["path_role"], row["relative_template"]) for row in path_rows) == PATH_TEMPLATES
    )

    owner_rows = product["serializer_ownership"]
    assert len(owner_rows) == 10
    assert all(list(row) == ["owner", "path_roles"] for row in owner_rows)
    assert (
        tuple((row["owner"], tuple(row["path_roles"])) for row in owner_rows)
        == SERIALIZER_OWNERSHIP
    )
    owned_roles = [role for row in owner_rows for role in row["path_roles"]]
    assert Counter(owned_roles) == Counter(role for role, _ in PATH_TEMPLATES)
    assert all(count == 1 for count in Counter(owned_roles).values())

    key_rows = product["primary_key_contracts"]
    assert len(key_rows) == 2
    assert all(list(row) == ["key_fields", "schema_role"] for row in key_rows)
    assert tuple((row["schema_role"], tuple(row["key_fields"])) for row in key_rows) == PRIMARY_KEYS

    receipt_rows = product["manifest_receipt_templates"]
    assert len(receipt_rows) == 5
    assert all(list(row) == ["artifact_role", "owner", "relative_template"] for row in receipt_rows)
    assert (
        tuple(
            (row["artifact_role"], row["owner"], row["relative_template"]) for row in receipt_rows
        )
        == MANIFEST_RECEIPTS
    )
    assert tuple(row["artifact_role"] for row in receipt_rows) == tuple(
        role for role, _ in PATH_TEMPLATES[12:]
    )


def test_schema_bundle_has_exact_closed_descriptors_and_placeholder() -> None:
    _, schema = _load(SCHEMA_PATH)
    assert list(schema) == [
        "authority_links",
        "dependency_order",
        "descriptors",
        "feature_schema_hash_placeholder",
        "preimage_id",
        "preimage_schema_version",
    ]
    assert schema["authority_links"] == AUTHORITY_LINKS
    assert schema["preimage_id"] == SCHEMA_ID
    assert schema["preimage_schema_version"] == "w04-schema-bundle-preimage-v1"
    assert schema["feature_schema_hash_placeholder"] == {
        "concrete_value": None,
        "json_type": "string",
        "pattern": "^[0-9a-f]{64}$",
        "resolution_source": ("accepted:w04-wyscout-supported-count-features-v1:candidate_sha256"),
        "state": "TYPED_UNRESOLVED_UNTIL_SUPPORTED_FEATURE_ACCEPTANCE",
    }

    rows = schema["descriptors"]
    assert len(rows) == 16
    assert all(
        list(row) == ["depends_on", "descriptor_id", "descriptor_version", "role", "surface_kind"]
        for row in rows
    )
    assert (
        tuple(
            (
                row["descriptor_id"],
                row["descriptor_version"],
                row["role"],
                tuple(row["depends_on"]),
            )
            for row in rows
        )
        == DESCRIPTORS
    )
    assert schema["dependency_order"] == [row[0] for row in DESCRIPTORS]
    assert all(row["surface_kind"] == SURFACE_KIND for row in rows)

    position = {
        descriptor_id: index for index, descriptor_id in enumerate(schema["dependency_order"])
    }
    assert len(position) == 16
    for row in rows:
        assert len(row["depends_on"]) == len(set(row["depends_on"]))
        assert all(
            dependency in position and position[dependency] < position[row["descriptor_id"]]
            for dependency in row["depends_on"]
        )


def test_preimages_are_byte_equal_siblings_without_descendant_overclaim() -> None:
    _, product = _load(PRODUCT_PATH)
    _, schema = _load(SCHEMA_PATH)
    assert product["authority_links"] == schema["authority_links"] == AUTHORITY_LINKS

    product_values = _walk(product)
    schema_values = _walk(schema)
    assert SCHEMA_ID not in product_values
    assert SCHEMA_SHA256 not in product_values
    assert PRODUCT_ID not in schema_values
    assert PRODUCT_SHA256 not in schema_values

    # R21 is the sole parent of both sibling preimages. Both valid presentations
    # prove that their listed order does not create a dependency edge.
    edges = {(R21_ID, PRODUCT_ID), (R21_ID, SCHEMA_ID)}
    for order in (
        (R21_ID, PRODUCT_ID, SCHEMA_ID),
        (R21_ID, SCHEMA_ID, PRODUCT_ID),
    ):
        position = {node: index for index, node in enumerate(order)}
        assert all(position[parent] < position[child] for parent, child in edges)
    assert (PRODUCT_ID, SCHEMA_ID) not in edges
    assert (SCHEMA_ID, PRODUCT_ID) not in edges

    forbidden_keys = {
        "build_id",
        "clock",
        "feature_schema_hash",
        "host",
        "output",
        "physical_sha256",
        "product_contract_preimage_sha256",
        "root",
        "run_id",
        "schema_bundle_preimage_sha256",
    }
    allowed_hashes = {R20_SHA256, R21_SHA256}
    uuid_re = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-"
        r"[0-9a-f]{12}\Z"
    )
    utc_re = re.compile(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
        r"(?:\.[0-9]{1,6})?Z\Z"
    )
    digest_re = re.compile(r"[0-9a-f]{64}\Z")
    for preimage in (product, schema):
        values = _walk(preimage)
        keys = {value for value in values if isinstance(value, str)}
        assert forbidden_keys.isdisjoint(keys)
        assert all(not value.startswith("/") for value in keys)
        assert all(not uuid_re.fullmatch(value) for value in keys)
        assert all(not utc_re.fullmatch(value) for value in keys)
        assert {value for value in keys if digest_re.fullmatch(value)} == allowed_hashes
        assert "accepted-R21-physical-sha256" not in keys
        assert "<accepted-R21-physical-sha256>" not in keys


def test_preimage_load_is_side_effect_free_for_repository_destinations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _snapshot_destination_state(PRODUCT_DESTINATIONS)
    writer_calls = _deny_writer_calls(monkeypatch)
    _, product = _load(PRODUCT_PATH)
    _, schema = _load(SCHEMA_PATH)
    after = _snapshot_destination_state(PRODUCT_DESTINATIONS)

    assert before == after
    assert writer_calls == []
    assert product["policy"] == {
        "control_plane_only": True,
        "no_product_before_gate": "R21_COMPLETE_GATE_PASS",
        "product_bytes_forbidden": True,
    }
    assert all(row["surface_kind"] == SURFACE_KIND for row in schema["descriptors"])


@pytest.mark.parametrize("preexisting", [False, True])
def test_preimage_load_preserves_simulated_absent_and_existing_products(
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
    sentinel = destinations[4] / "existing-manifest.json"
    if preexisting:
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b'{"simulated":"pre-existing"}\n')

    before = _snapshot_destination_state(destinations)
    writer_calls = _deny_writer_calls(monkeypatch)
    _, product = _load(PRODUCT_PATH)
    _, schema = _load(SCHEMA_PATH)
    after = _snapshot_destination_state(destinations)

    assert before == after
    assert writer_calls == []
    assert product["policy"]["control_plane_only"] is True
    assert product["policy"]["product_bytes_forbidden"] is True
    assert all(row["surface_kind"] == SURFACE_KIND for row in schema["descriptors"])
    if preexisting:
        assert sentinel.read_bytes() == b'{"simulated":"pre-existing"}\n'

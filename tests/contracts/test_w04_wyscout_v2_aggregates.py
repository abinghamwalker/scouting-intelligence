from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import cast

import pytest

from scouting.contracts import wyscout_build, wyscout_schema
from scouting.contracts.wyscout_aggregates import (
    PRODUCT_CONTRACT_V2_KEY_ORDER,
    SCHEMA_BUNDLE_V2_KEY_ORDER,
    W04AggregateError,
    aggregate_physical_bytes,
    build_product_contract_v2,
    build_schema_bundle_v2,
    canonical_product_contract_v2_bytes,
    canonical_schema_bundle_v2_bytes,
    product_contract_v2_sha256,
    schema_bundle_v2_sha256,
    validate_materialized_aggregates,
    validate_required_root_roles,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "configs/schema/wyscout-v5-schema-bundle-preimage-v2.json"
PRODUCT_PATH = ROOT / "configs/schema/wyscout-v5-product-contract-preimage-v2.json"


def test_exact_two_node_aggregate_graph_and_physical_bytes() -> None:
    schema = build_schema_bundle_v2()
    schema_digest = schema_bundle_v2_sha256(schema)
    product = build_product_contract_v2(schema_digest)
    product_digest = product_contract_v2_sha256(product)
    assert tuple(schema) == SCHEMA_BUNDLE_V2_KEY_ORDER
    assert tuple(product) == PRODUCT_CONTRACT_V2_KEY_ORDER
    assert len(cast(list[object], schema["implemented_schema_rows"])) == 23
    assert schema["required_root_roles"] == list(wyscout_schema.W04_SCHEMA_ROOT_ROLES)
    assert product["schema_bundle_preimage_v2_sha256"] == schema_digest
    assert validate_materialized_aggregates(schema, product) == (
        schema_digest,
        product_digest,
    )
    assert aggregate_physical_bytes(schema) == SCHEMA_PATH.read_bytes()
    assert aggregate_physical_bytes(product) == PRODUCT_PATH.read_bytes()
    assert SCHEMA_PATH.read_bytes().endswith(b"\n")
    assert not SCHEMA_PATH.read_bytes().endswith(b"\n\n")
    assert PRODUCT_PATH.read_bytes().endswith(b"\n")
    assert not PRODUCT_PATH.read_bytes().endswith(b"\n\n")
    assert hashlib.sha256(SCHEMA_PATH.read_bytes()[:-1]).hexdigest() == schema_digest
    assert hashlib.sha256(PRODUCT_PATH.read_bytes()[:-1]).hexdigest() == product_digest


def test_all_root_content_digests_and_edges_reproduce() -> None:
    schema = build_schema_bundle_v2()
    rows = cast(list[dict[str, object]], schema["implemented_schema_rows"])
    contents = wyscout_schema.export_w04_implemented_schema_contents()
    assert len(rows) == len(contents) == 23
    positions = {row["canonical_schema_id"]: index for index, row in enumerate(rows)}
    for index, (row, content) in enumerate(zip(rows, contents, strict=True)):
        content_bytes = wyscout_schema.canonical_w04_schema_content_bytes(content)
        assert row["canonical_schema_content_sha256"] == hashlib.sha256(content_bytes).hexdigest()
        dependencies = cast(list[str], row["closure_dependencies"])
        assert len(dependencies) == len(set(dependencies))
        assert all(positions[dependency] < index for dependency in dependencies)


def test_product_contract_binds_exact_authority_and_receipt_composition() -> None:
    product = build_product_contract_v2(schema_bundle_v2_sha256())
    assert product["feature_cutoff_ts"] == wyscout_build.FEATURE_CUTOFF_TS
    completion = cast(dict[str, object], product["completion_index_binding"])
    assert (
        completion["source_completion_index_sha256"] == wyscout_build.SOURCE_COMPLETION_INDEX_SHA256
    )
    assert completion["provider_match_id"] == 2_499_719
    assert [(row["period_code"], row["action_count"]) for row in completion["periods"]] == [
        ("1H", 901),
        ("2H", 867),
    ]
    receipts = cast(dict[str, object], product["receipt_contracts"])
    assert set(receipts) == {
        "layer_manifest_receipt_composition",
        "rebuild_invocation_receipt",
        "temporal_boundary_receipt",
    }
    composition = cast(dict[str, object], receipts["layer_manifest_receipt_composition"])
    semantic = cast(dict[str, object], composition["complete_layer_manifest_semantic"])
    assert semantic["wrapper_exact_key_order"] == [
        "layer_manifest",
        "semantic_schema_version",
    ]
    assert composition["layer_order"] == ["BRONZE", "SILVER", "GOLD"]
    assert composition["parent_edges"] == [
        {"child": "BRONZE", "parents": []},
        {"child": "SILVER", "parents": ["BRONZE"]},
        {"child": "GOLD", "parents": ["SILVER"]},
    ]
    assert composition["gold_population"] == {
        "complete_entry_count": 1,
        "row_count": 1,
        "source_match_id": 2_499_719,
        "source_season_id": 181_150,
    }


@pytest.mark.parametrize(
    ("target", "mutation"),
    [
        ("schema", "missing_root"),
        ("schema", "reorder_root"),
        ("schema", "placeholder_digest"),
        ("schema", "v1_digest"),
        ("schema", "forward_edge"),
        ("schema", "self_reference"),
        ("product", "wrong_schema_digest"),
        ("product", "v1_schema_digest"),
        ("product", "swap_v1_digest"),
        ("product", "publication_reorder"),
        ("product", "receipt_substitution"),
        ("product", "extra_key"),
    ],
)
def test_aggregate_mutations_fail_closed(target: str, mutation: str) -> None:
    schema = build_schema_bundle_v2()
    product = build_product_contract_v2(schema_bundle_v2_sha256(schema))
    if target == "schema":
        candidate = deepcopy(schema)
        rows = cast(list[dict[str, object]], candidate["implemented_schema_rows"])
        if mutation == "missing_root":
            rows.pop()
        elif mutation == "reorder_root":
            rows[0], rows[1] = rows[1], rows[0]
        elif mutation == "placeholder_digest":
            rows[0]["canonical_schema_content_sha256"] = "0" * 64
        elif mutation == "v1_digest":
            candidate["schema_bundle_preimage_v1_sha256"] = "0" * 64
        elif mutation == "forward_edge":
            rows[0]["closure_dependencies"] = [rows[1]["canonical_schema_id"]]
        else:
            candidate["schema_bundle_digest"] = "0" * 64
        with pytest.raises(W04AggregateError):
            canonical_schema_bundle_v2_bytes(candidate)
    else:
        candidate = deepcopy(product)
        if mutation == "wrong_schema_digest":
            candidate["schema_bundle_preimage_v2_sha256"] = "0" * 64
        elif mutation == "v1_schema_digest":
            candidate["schema_bundle_preimage_v2_sha256"] = (
                "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f"
            )
        elif mutation == "swap_v1_digest":
            candidate["product_contract_preimage_v1_sha256"] = schema_bundle_v2_sha256()
        elif mutation == "publication_reorder":
            cast(list[object], candidate["publication_order"]).reverse()
        elif mutation == "receipt_substitution":
            candidate["receipt_contracts"] = {"schema_version": "placeholder"}
        else:
            candidate["product_contract_digest"] = "0" * 64
        with pytest.raises(W04AggregateError):
            canonical_product_contract_v2_bytes(candidate)


def test_root_roster_requires_exact_tuple_and_order() -> None:
    validate_required_root_roles(wyscout_schema.W04_SCHEMA_ROOT_ROLES)
    with pytest.raises(W04AggregateError):
        validate_required_root_roles(list(wyscout_schema.W04_SCHEMA_ROOT_ROLES))
    with pytest.raises(W04AggregateError):
        validate_required_root_roles(tuple(reversed(wyscout_schema.W04_SCHEMA_ROOT_ROLES)))


def test_config_json_is_canonical_closed_and_has_no_aggregate_self_digest() -> None:
    schema_body = SCHEMA_PATH.read_bytes()[:-1]
    product_body = PRODUCT_PATH.read_bytes()[:-1]
    assert schema_body == canonical_schema_bundle_v2_bytes(json.loads(schema_body))
    assert product_body == canonical_product_contract_v2_bytes(json.loads(product_body))
    forbidden = {
        "product_contract_digest",
        "schema_bundle_digest",
        "build_id",
        "run_id",
    }

    def keys(value: object) -> set[str]:
        if type(value) is dict:
            mapping = cast(dict[str, object], value)
            return set(mapping) | set().union(*(keys(item) for item in mapping.values()))
        if type(value) is list:
            return set().union(*(keys(item) for item in cast(list[object], value)))
        return set()

    assert not (keys(json.loads(schema_body)) & forbidden)
    assert "product_contract_digest" not in keys(json.loads(product_body))
    assert "schema_bundle_digest" not in keys(json.loads(product_body))

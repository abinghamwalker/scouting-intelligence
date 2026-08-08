"""Acyclic W04 implemented-schema and product-contract v2 aggregates."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Final, cast

from . import wyscout_build, wyscout_schema

SCHEMA_BUNDLE_V2_ID: Final = "w04-wyscout-schema-bundle-preimage-v2"
PRODUCT_CONTRACT_V2_ID: Final = "w04-wyscout-product-contract-preimage-v2"
SCHEMA_BUNDLE_V1_SHA256: Final = "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f"
PRODUCT_CONTRACT_V1_SHA256: Final = (
    "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293"
)
R20_DESIGN_SHA256: Final = "8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047"
R21_DESIGN_SHA256: Final = "faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020"

SCHEMA_BUNDLE_V2_KEY_ORDER: Final = (
    "implemented_schema_rows",
    "preimage_schema_version",
    "r20_design_sha256",
    "r21_design_sha256",
    "required_root_roles",
    "schema_bundle_preimage_id",
    "schema_bundle_preimage_v1_sha256",
    "surface_closure_policy",
)
PRODUCT_CONTRACT_V2_KEY_ORDER: Final = (
    "completion_index_binding",
    "feature_cutoff_ts",
    "preimage_schema_version",
    "product_authorization_state",
    "product_contract_preimage_id",
    "product_contract_preimage_v1_sha256",
    "publication_order",
    "receipt_contracts",
    "schema_bundle_preimage_v2_sha256",
    "window_authority",
)
PUBLICATION_ORDER: Final = (
    "PRODUCT_PARQUET",
    "LAYER_MANIFEST",
    "TEMPORAL_BOUNDARY_RECEIPT",
    "REBUILD_INVOCATION_RECEIPT",
    "CHILD_RESULT_SUMMARY",
)


class W04AggregateError(ValueError):
    """An aggregate differs from the accepted acyclic W04 authority."""


def _copy_json(value: object) -> object:
    return json.loads(wyscout_build.canonical_json_bytes(value))


def _canonical_object(value: Mapping[str, object], keys: tuple[str, ...]) -> bytes:
    if type(value) is not dict or tuple(value) != keys:
        raise W04AggregateError("aggregate object key order or shape differs")
    try:
        encoded = wyscout_build.canonical_json_bytes(value)
    except (TypeError, ValueError) as error:
        raise W04AggregateError("aggregate is not R20-canonical JSON") from error
    if encoded.endswith(b"\n") or json.loads(encoded) != value:
        raise W04AggregateError("aggregate canonical bytes do not reproduce")
    return encoded


def _accepted_schema_exports() -> tuple[
    tuple[dict[str, object], ...], tuple[dict[str, object], ...]
]:
    contents = wyscout_schema.export_w04_implemented_schema_contents()
    rows = wyscout_schema.export_w04_implemented_schema_rows()
    wyscout_schema.validate_w04_implemented_schema_exports(contents, rows)
    if tuple(row["root_role"] for row in rows) != wyscout_schema.W04_SCHEMA_ROOT_ROLES:
        raise W04AggregateError("implemented schema rows differ from required root order")
    for content, row in zip(contents, rows, strict=True):
        digest = hashlib.sha256(
            wyscout_schema.canonical_w04_schema_content_bytes(content)
        ).hexdigest()
        if row["canonical_schema_content_sha256"] != digest:
            raise W04AggregateError("implemented root content digest does not reproduce")
    return contents, rows


def build_schema_bundle_v2() -> dict[str, object]:
    """Build the exact accepted eight-key implemented-schema bundle preimage."""

    _contents, rows = _accepted_schema_exports()
    return {
        "implemented_schema_rows": _copy_json(rows),
        "preimage_schema_version": SCHEMA_BUNDLE_V2_ID,
        "r20_design_sha256": R20_DESIGN_SHA256,
        "r21_design_sha256": R21_DESIGN_SHA256,
        "required_root_roles": list(wyscout_schema.W04_SCHEMA_ROOT_ROLES),
        "schema_bundle_preimage_id": SCHEMA_BUNDLE_V2_ID,
        "schema_bundle_preimage_v1_sha256": SCHEMA_BUNDLE_V1_SHA256,
        "surface_closure_policy": "EXACT_TRANSITIVE_CANONICAL_IMPLEMENTED_SCHEMA_CLOSURE",
    }


def canonical_schema_bundle_v2_bytes(value: Mapping[str, object]) -> bytes:
    """Validate and encode the sole accepted schema-bundle v2 preimage."""

    encoded = _canonical_object(value, SCHEMA_BUNDLE_V2_KEY_ORDER)
    expected = wyscout_build.canonical_json_bytes(build_schema_bundle_v2())
    if encoded != expected:
        raise W04AggregateError("schema-bundle v2 differs from accepted schema exports")
    return encoded


def schema_bundle_v2_sha256(value: Mapping[str, object] | None = None) -> str:
    """Return the one SHA-256 identity of the exact schema-bundle preimage."""

    candidate = build_schema_bundle_v2() if value is None else value
    return hashlib.sha256(canonical_schema_bundle_v2_bytes(candidate)).hexdigest()


def _accepted_constant_corpus() -> dict[str, object]:
    contents, _rows = _accepted_schema_exports()
    definitions = cast(dict[str, object], contents[0]["definitions"])
    corpus = definitions["constant_corpus"]
    if type(corpus) is not dict:
        raise W04AggregateError("accepted schema constant corpus is malformed")
    return cast(dict[str, object], corpus)


def _receipt_composition(corpus: dict[str, object]) -> dict[str, object]:
    receipts = corpus.get("receipt_contracts")
    composition = corpus.get("layer_manifest_receipt_composition")
    if type(receipts) is not dict or type(composition) is not dict:
        raise W04AggregateError("accepted receipt composition is unavailable")
    receipt_rows = cast(dict[str, object], receipts)
    if set(receipt_rows) != {"rebuild_invocation_receipt", "temporal_boundary_receipt"}:
        raise W04AggregateError("receipt contract roster differs")
    return {
        "layer_manifest_receipt_composition": _copy_json(composition),
        "rebuild_invocation_receipt": _copy_json(receipt_rows["rebuild_invocation_receipt"]),
        "temporal_boundary_receipt": _copy_json(receipt_rows["temporal_boundary_receipt"]),
    }


def build_product_contract_v2(schema_bundle_sha256: str) -> dict[str, object]:
    """Build the exact product contract after the schema bundle is content-addressed."""

    expected_schema_digest = schema_bundle_v2_sha256()
    if type(schema_bundle_sha256) is not str or schema_bundle_sha256 != expected_schema_digest:
        raise W04AggregateError("product contract requires the actual schema-bundle v2 digest")
    corpus = _accepted_constant_corpus()
    completion = corpus.get("completion_index_binding")
    window = corpus.get("window_authority")
    if type(completion) is not dict or type(window) is not dict:
        raise W04AggregateError("accepted completion/window authority is unavailable")
    return {
        "completion_index_binding": _copy_json(completion),
        "feature_cutoff_ts": wyscout_build.FEATURE_CUTOFF_TS,
        "preimage_schema_version": PRODUCT_CONTRACT_V2_ID,
        "product_authorization_state": ("W04_SINGLE_MATCH_FOUR_FEATURE_POC_PUBLICATION_AUTHORIZED"),
        "product_contract_preimage_id": PRODUCT_CONTRACT_V2_ID,
        "product_contract_preimage_v1_sha256": PRODUCT_CONTRACT_V1_SHA256,
        "publication_order": list(PUBLICATION_ORDER),
        "receipt_contracts": _receipt_composition(corpus),
        "schema_bundle_preimage_v2_sha256": schema_bundle_sha256,
        "window_authority": _copy_json(window),
    }


def canonical_product_contract_v2_bytes(value: Mapping[str, object]) -> bytes:
    """Validate and encode the sole accepted product-contract v2 preimage."""

    encoded = _canonical_object(value, PRODUCT_CONTRACT_V2_KEY_ORDER)
    schema_digest = value.get("schema_bundle_preimage_v2_sha256")
    if type(schema_digest) is not str:
        raise W04AggregateError("schema-bundle digest is not an exact string")
    expected = wyscout_build.canonical_json_bytes(build_product_contract_v2(schema_digest))
    if encoded != expected:
        raise W04AggregateError("product-contract v2 differs from accepted authority")
    return encoded


def product_contract_v2_sha256(value: Mapping[str, object] | None = None) -> str:
    """Return the one SHA-256 identity of the exact product-contract preimage."""

    candidate = build_product_contract_v2(schema_bundle_v2_sha256()) if value is None else value
    return hashlib.sha256(canonical_product_contract_v2_bytes(candidate)).hexdigest()


def aggregate_physical_bytes(value: Mapping[str, object]) -> bytes:
    """Return canonical config bytes with exactly one physical terminal LF."""

    if tuple(value) == SCHEMA_BUNDLE_V2_KEY_ORDER:
        body = canonical_schema_bundle_v2_bytes(value)
    elif tuple(value) == PRODUCT_CONTRACT_V2_KEY_ORDER:
        body = canonical_product_contract_v2_bytes(value)
    else:
        raise W04AggregateError("aggregate physical object is not an accepted preimage")
    return body + b"\n"


def validate_materialized_aggregates(
    schema_bundle: Mapping[str, object],
    product_contract: Mapping[str, object],
) -> tuple[str, str]:
    """Validate the serial two-node aggregate graph and return both digests."""

    schema_digest = schema_bundle_v2_sha256(schema_bundle)
    if product_contract.get("schema_bundle_preimage_v2_sha256") != schema_digest:
        raise W04AggregateError("product contract does not bind the schema aggregate")
    product_digest = product_contract_v2_sha256(product_contract)
    return schema_digest, product_digest


def validate_required_root_roles(roles: Sequence[object]) -> None:
    """Fail closed unless a caller supplies the exact immutable root order."""

    if type(roles) is not tuple or roles != wyscout_schema.W04_SCHEMA_ROOT_ROLES:
        raise W04AggregateError("required root role roster or order differs")


__all__ = [
    "PRODUCT_CONTRACT_V2_ID",
    "PRODUCT_CONTRACT_V2_KEY_ORDER",
    "SCHEMA_BUNDLE_V2_ID",
    "SCHEMA_BUNDLE_V2_KEY_ORDER",
    "W04AggregateError",
    "aggregate_physical_bytes",
    "build_product_contract_v2",
    "build_schema_bundle_v2",
    "canonical_product_contract_v2_bytes",
    "canonical_schema_bundle_v2_bytes",
    "product_contract_v2_sha256",
    "schema_bundle_v2_sha256",
    "validate_materialized_aggregates",
    "validate_required_root_roles",
]

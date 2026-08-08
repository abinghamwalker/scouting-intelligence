from __future__ import annotations

import hashlib
import inspect
import struct
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from typing import cast

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
import pytest

import scouting.storage.formats as formats_module
from scouting.contracts.wyscout_data import (
    CanonicalJsonArray,
    CanonicalJsonBoolean,
    CanonicalJsonInteger,
    CanonicalJsonKind,
    CanonicalJsonMember,
    CanonicalJsonNull,
    CanonicalJsonNumber,
    CanonicalJsonObject,
    CanonicalJsonString,
    CanonicalJsonValue,
)
from scouting.storage.formats import (
    WYSCOUT_PARQUET_SEMANTIC_VERSION,
    WYSCOUT_PARQUET_SERIALIZER_VERSION,
    FormatError,
    WyscoutArrowListKind,
    WyscoutArrowListNode,
    WyscoutArrowProjectionField,
    WyscoutArrowScalarNode,
    WyscoutArrowScalarType,
    WyscoutArrowStructNode,
    WyscoutLogicalArrowProjectionKind,
    WyscoutParquetEncoding,
    WyscoutParquetProjectionDescriptor,
    arrow_schema_from_w04_projection,
    canonical_decimal_to_w04_arrow_utf8,
    canonical_json_bytes,
    canonical_json_value_to_w04_arrow_utf8,
    encode_w04_wyscout_product_parquet,
    exact_decimal128_with_exponent_to_w04_arrow,
    w04_wyscout_parquet_semantic_sha256,
)


def _scalar(
    name: str,
    scalar_type: WyscoutArrowScalarType,
    *,
    nullable: bool = False,
    projection_kind: WyscoutLogicalArrowProjectionKind = (
        WyscoutLogicalArrowProjectionKind.IDENTITY
    ),
    precision: int | None = None,
    scale: int | None = None,
    logical_position: int | None = None,
) -> WyscoutArrowProjectionField:
    return WyscoutArrowProjectionField(
        name=name,
        nullable=nullable,
        node=WyscoutArrowScalarNode(
            scalar_type=scalar_type,
            projection_kind=projection_kind,
            decimal_precision=precision,
            decimal_scale=scale,
        ),
        logical_position=logical_position,
    )


def _descriptor(
    role: str,
    *fields: WyscoutArrowProjectionField,
) -> WyscoutParquetProjectionDescriptor:
    return WyscoutParquetProjectionDescriptor(
        schema_role=role,
        serializer_version=WYSCOUT_PARQUET_SERIALIZER_VERSION,
        fields=fields,
    )


IDENTITY_DESCRIPTOR = _descriptor(
    "silver-action-v1",
    _scalar("record_id", WyscoutArrowScalarType.INT64),
    _scalar("label", WyscoutArrowScalarType.UTF8),
    _scalar("occurred_at", WyscoutArrowScalarType.TIMESTAMP_US_UTC, nullable=True),
)
SCHEMA = arrow_schema_from_w04_projection(IDENTITY_DESCRIPTOR)
ROWS = (
    {
        "record_id": 1,
        "label": "alpha",
        "occurred_at": datetime(2018, 5, 1, 12, 30, 15, 123456, tzinfo=UTC),
    },
    {"record_id": 2, "label": "bravo", "occurred_at": None},
)
CONTRACT_ROWS = (
    canonical_json_bytes(
        {
            "label": "alpha",
            "occurred_at": "2018-05-01T12:30:15.123456Z",
            "record_id": 1,
        }
    ),
    canonical_json_bytes({"label": "bravo", "occurred_at": None, "record_id": 2}),
)
PRIMARY_KEYS = ((1,), (2,))
PARENTS = ("data/working/wyscout/v5/bronze/build_id=" + "1" * 64 + "/part-00000.parquet",)


def _table(rows: tuple[dict[str, object], ...] = ROWS) -> pa.Table:
    return pa.Table.from_pylist(list(rows), schema=SCHEMA)


def _encode(
    *,
    table: pa.Table | None = None,
    descriptor: WyscoutParquetProjectionDescriptor = IDENTITY_DESCRIPTOR,
    primary_key_fields: tuple[str, ...] = ("record_id",),
    primary_keys: tuple[tuple[str | int, ...], ...] = PRIMARY_KEYS,
    contract_rows: tuple[bytes, ...] = CONTRACT_ROWS,
    parents: tuple[str, ...] = PARENTS,
) -> WyscoutParquetEncoding:
    return encode_w04_wyscout_product_parquet(
        _table() if table is None else table,
        projection_descriptor=descriptor,
        primary_key_fields=primary_key_fields,
        primary_keys=primary_keys,
        contract_row_bytes=contract_rows,
        parent_paths=parents,
    )


def _single_row_encode(
    descriptor: WyscoutParquetProjectionDescriptor,
    physical_row: dict[str, object],
    logical_row: dict[str, object],
) -> WyscoutParquetEncoding:
    schema = arrow_schema_from_w04_projection(descriptor)
    key = physical_row["record_id"]
    assert type(key) in {str, int}
    return encode_w04_wyscout_product_parquet(
        pa.Table.from_pylist([physical_row], schema=schema),
        projection_descriptor=descriptor,
        primary_key_fields=("record_id",),
        primary_keys=((cast(str | int, key),),),
        contract_row_bytes=(canonical_json_bytes(logical_row),),
        parent_paths=(),
    )


def test_fixed_physical_and_semantic_vectors_are_repeatable() -> None:
    first = _encode()
    second = _encode()

    assert first == second
    assert first.payload == second.payload
    assert first.physical_sha256 == hashlib.sha256(first.payload).hexdigest()
    assert first.size_bytes == len(first.payload)
    assert first.row_count == 2
    assert first.schema_descriptor.serializer_version == WYSCOUT_PARQUET_SERIALIZER_VERSION
    assert first.schema_descriptor_bytes == canonical_json_bytes(
        {
            "fields": [
                {"arrow_type": "int64", "name": "record_id", "nullable": False},
                {"arrow_type": "string", "name": "label", "nullable": False},
                {
                    "arrow_type": "timestamp[us, tz=UTC]",
                    "name": "occurred_at",
                    "nullable": True,
                },
            ],
            "schema_role": "silver-action-v1",
            "serializer_version": "w04-wyscout-parquet-v1",
        }
    )
    assert first.physical_sha256 == (
        "889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b"
    )
    assert first.semantic_sha256 == (
        "6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7"
    )


def test_exact_r20_parquet_controls_and_round_trip() -> None:
    encoded = _encode()
    parquet_file = pq.ParquetFile(pa.BufferReader(encoded.payload))
    metadata = parquet_file.metadata

    assert metadata.format_version == "2.6"
    assert metadata.num_rows == 2
    assert metadata.num_row_groups == 1
    assert parquet_file.schema_arrow.equals(SCHEMA, check_metadata=True)
    assert metadata.metadata is not None and b"ARROW:schema" in metadata.metadata
    for column_index in range(metadata.num_columns):
        column = metadata.row_group(0).column(column_index)
        assert column.compression == "ZSTD"
        assert column.statistics is not None
        assert "RLE_DICTIONARY" not in column.encodings
        assert "BYTE_STREAM_SPLIT" not in column.encodings
        assert column.has_column_index is False
        assert column.has_offset_index is False
    assert pq.read_table(pa.BufferReader(encoded.payload)).to_pylist() == list(ROWS)


@pytest.mark.parametrize(
    ("row_count", "expected_sizes"),
    [(65535, (65535,)), (65536, (65536,)), (65537, (65536, 1))],
)
def test_exact_row_group_boundary(row_count: int, expected_sizes: tuple[int, ...]) -> None:
    descriptor = _descriptor(
        "silver-action-row-group-proof",
        _scalar("record_id", WyscoutArrowScalarType.INT64),
    )
    schema = arrow_schema_from_w04_projection(descriptor)
    table = pa.table({"record_id": pa.array(range(row_count), type=pa.int64())}, schema=schema)
    encoded = encode_w04_wyscout_product_parquet(
        table,
        projection_descriptor=descriptor,
        primary_key_fields=("record_id",),
        primary_keys=tuple((index,) for index in range(row_count)),
        contract_row_bytes=tuple(
            canonical_json_bytes({"record_id": index}) for index in range(row_count)
        ),
        parent_paths=(),
    )
    metadata = pq.ParquetFile(pa.BufferReader(encoded.payload)).metadata
    assert (
        tuple(metadata.row_group(index).num_rows for index in range(metadata.num_row_groups))
        == expected_sizes
    )


def test_semantic_preimage_matches_independent_length_framing() -> None:
    encoded = _encode()

    def frame(value: bytes) -> bytes:
        return len(value).to_bytes(8, "big") + value

    preimage = (
        WYSCOUT_PARQUET_SEMANTIC_VERSION.encode()
        + b"\x00S"
        + frame(encoded.schema_descriptor_bytes)
        + b"R"
        + len(CONTRACT_ROWS).to_bytes(8, "big")
        + b"".join(frame(row) for row in CONTRACT_ROWS)
        + b"P"
        + len(PARENTS).to_bytes(8, "big")
        + b"".join(frame(parent.encode()) for parent in PARENTS)
    )
    assert encoded.semantic_sha256 == hashlib.sha256(preimage).hexdigest()
    assert (
        w04_wyscout_parquet_semantic_sha256(
            projection_descriptor=IDENTITY_DESCRIPTOR,
            contract_row_bytes=CONTRACT_ROWS,
            parent_paths=PARENTS,
        )
        == encoded.semantic_sha256
    )


def test_role_parent_value_and_schema_mutations_change_only_existing_digest_inputs() -> None:
    baseline = _encode()
    changed_rows = (ROWS[0], {"record_id": 2, "label": "charlie", "occurred_at": None})
    changed_contract = (
        CONTRACT_ROWS[0],
        canonical_json_bytes({"label": "charlie", "occurred_at": None, "record_id": 2}),
    )
    value = _encode(table=_table(changed_rows), contract_rows=changed_contract)
    role = _encode(descriptor=replace(IDENTITY_DESCRIPTOR, schema_role="gold-action-v1"))
    parent = _encode(parents=("data/parent-2.parquet",))
    nullable_descriptor = replace(
        IDENTITY_DESCRIPTOR,
        fields=(
            IDENTITY_DESCRIPTOR.fields[0],
            replace(IDENTITY_DESCRIPTOR.fields[1], nullable=True),
            IDENTITY_DESCRIPTOR.fields[2],
        ),
    )
    nullable_schema = arrow_schema_from_w04_projection(nullable_descriptor)
    schema = _encode(
        descriptor=nullable_descriptor,
        table=pa.Table.from_pylist(list(ROWS), schema=nullable_schema),
    )

    assert value.physical_sha256 != baseline.physical_sha256
    assert value.semantic_sha256 != baseline.semantic_sha256
    assert role.payload == baseline.payload and role.semantic_sha256 != baseline.semantic_sha256
    assert parent.payload == baseline.payload and parent.semantic_sha256 != baseline.semantic_sha256
    assert schema.physical_sha256 != baseline.physical_sha256
    assert schema.semantic_sha256 != baseline.semantic_sha256


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"primary_keys": ((2,), (1,))}, "canonical primary-key order"),
        ({"primary_keys": ((1,), (1,))}, "unique"),
        ({"primary_keys": ((1,),)}, "count"),
        ({"primary_keys": ((1, 2), (2, 3))}, "arity"),
        ({"primary_keys": ((1,), (3,))}, "does not exactly equal"),
        ({"primary_key_fields": ()}, "non-empty unique"),
        ({"primary_key_fields": ("missing",)}, "not present"),
        ({"primary_keys": ((True,), (2,))}, "unsupported type"),
        ({"primary_keys": ((1,), ("2",))}, "types differ"),
    ],
)
def test_primary_key_failures_are_closed(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(FormatError, match=message):
        _encode(**kwargs)  # type: ignore[arg-type]


def _nested_key_descriptor(
    *,
    tenant_nullable: bool = False,
    tenant_id_nullable: bool = False,
    tenant_id_type: WyscoutArrowScalarType = WyscoutArrowScalarType.UTF8,
) -> WyscoutParquetProjectionDescriptor:
    return _descriptor(
        "silver-nested-key-proof",
        WyscoutArrowProjectionField(
            "tenant_context",
            tenant_nullable,
            WyscoutArrowStructNode(
                WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT,
                (
                    _scalar(
                        "tenant_id",
                        tenant_id_type,
                        nullable=tenant_id_nullable,
                    ),
                    _scalar("club_id", WyscoutArrowScalarType.UTF8, nullable=True),
                ),
            ),
        ),
        _scalar("record_id", WyscoutArrowScalarType.INT64),
    )


def _encode_nested_keys(
    rows: tuple[dict[str, object], ...],
    *,
    descriptor: WyscoutParquetProjectionDescriptor | None = None,
    primary_key_fields: tuple[str, ...] = ("tenant_context.tenant_id", "record_id"),
    primary_keys: tuple[tuple[str | int, ...], ...] = (("tenant-a", 1),),
) -> WyscoutParquetEncoding:
    exact_descriptor = _nested_key_descriptor() if descriptor is None else descriptor
    return encode_w04_wyscout_product_parquet(
        pa.Table.from_pylist(
            list(rows),
            schema=arrow_schema_from_w04_projection(exact_descriptor),
        ),
        projection_descriptor=exact_descriptor,
        primary_key_fields=primary_key_fields,
        primary_keys=primary_keys,
        contract_row_bytes=tuple(canonical_json_bytes(row) for row in rows),
        parent_paths=(),
    )


def test_nested_object_struct_primary_keys_encode_and_read_back_exactly() -> None:
    rows = (
        {"tenant_context": {"tenant_id": "tenant-a", "club_id": None}, "record_id": 1},
        {"tenant_context": {"tenant_id": "tenant-b", "club_id": None}, "record_id": 2},
    )
    encoded = _encode_nested_keys(
        rows,
        primary_keys=(("tenant-a", 1), ("tenant-b", 2)),
    )
    assert pq.read_table(pa.BufferReader(encoded.payload)).to_pylist() == list(rows)


@pytest.mark.parametrize(
    "primary_key_fields",
    [
        ("",),
        (".tenant_context",),
        ("tenant_context.",),
        ("tenant_context..tenant_id",),
        ("tenant-context.tenant_id",),
        ("tenant_context[0].tenant_id",),
        ("tenant_context.*",),
        ("tenant_context.tenant_id", "tenant_context.tenant_id"),
        cast(tuple[str, ...], (1,)),
    ],
)
def test_nested_primary_key_path_grammar_and_duplicates_fail_closed(
    primary_key_fields: tuple[str, ...],
) -> None:
    row = {"tenant_context": {"tenant_id": "tenant-a", "club_id": None}, "record_id": 1}
    with pytest.raises(FormatError):
        _encode_nested_keys(
            (row,),
            primary_key_fields=primary_key_fields,
            primary_keys=tuple(("tenant-a",) for _field in primary_key_fields),
        )


@pytest.mark.parametrize(
    ("descriptor", "primary_key_fields", "primary_keys"),
    [
        (_nested_key_descriptor(), ("tenant_context.missing",), (("tenant-a",),)),
        (_nested_key_descriptor(), ("tenant_context.club_id",), (("tenant-a",),)),
        (
            _nested_key_descriptor(tenant_nullable=True),
            ("tenant_context.tenant_id",),
            (("tenant-a",),),
        ),
        (
            _nested_key_descriptor(tenant_id_nullable=True),
            ("tenant_context.tenant_id",),
            (("tenant-a",),),
        ),
        (_nested_key_descriptor(), ("tenant_context",), (("tenant-a",),)),
        (
            _nested_key_descriptor(tenant_id_type=WyscoutArrowScalarType.BOOL),
            ("tenant_context.tenant_id",),
            ((1,),),
        ),
    ],
)
def test_nested_primary_key_missing_nullable_nonscalar_and_boolean_paths_fail_closed(
    descriptor: WyscoutParquetProjectionDescriptor,
    primary_key_fields: tuple[str, ...],
    primary_keys: tuple[tuple[str | int, ...], ...],
) -> None:
    tenant_context_node = descriptor.fields[0].node
    assert type(tenant_context_node) is WyscoutArrowStructNode
    tenant_id_node = tenant_context_node.children[0].node
    assert type(tenant_id_node) is WyscoutArrowScalarNode
    tenant_value: object = (
        True if tenant_id_node.scalar_type is WyscoutArrowScalarType.BOOL else "tenant-a"
    )
    row = {"tenant_context": {"tenant_id": tenant_value, "club_id": None}, "record_id": 1}
    with pytest.raises(FormatError):
        _encode_nested_keys(
            (row,),
            descriptor=descriptor,
            primary_key_fields=primary_key_fields,
            primary_keys=primary_keys,
        )


def test_nested_primary_keys_reject_type_drift_and_row_reordering() -> None:
    rows = (
        {"tenant_context": {"tenant_id": "tenant-b", "club_id": None}, "record_id": 2},
        {"tenant_context": {"tenant_id": "tenant-a", "club_id": None}, "record_id": 1},
    )
    with pytest.raises(FormatError, match="canonical primary-key order"):
        _encode_nested_keys(
            rows,
            primary_keys=(("tenant-b", 2), ("tenant-a", 1)),
        )
    with pytest.raises(FormatError, match="does not exactly equal"):
        _encode_nested_keys(
            (rows[1],),
            primary_keys=(("tenant-a", "1"),),
        )


def test_timestamp_primary_key_projects_to_exact_canonical_utc_string() -> None:
    descriptor = _descriptor(
        "gold-timestamp-key-proof",
        _scalar("window_start_utc", WyscoutArrowScalarType.TIMESTAMP_US_UTC),
    )
    timestamp = datetime(2017, 8, 11, 0, 0, 0, 123456, tzinfo=UTC)
    canonical = "2017-08-11T00:00:00.123456Z"
    encoded = encode_w04_wyscout_product_parquet(
        pa.Table.from_pylist(
            [{"window_start_utc": timestamp}],
            schema=arrow_schema_from_w04_projection(descriptor),
        ),
        projection_descriptor=descriptor,
        primary_key_fields=("window_start_utc",),
        primary_keys=((canonical,),),
        contract_row_bytes=(canonical_json_bytes({"window_start_utc": canonical}),),
        parent_paths=(),
    )
    assert encoded.row_count == 1


def test_timestamp_primary_key_rejects_raw_timestamp_and_string_drift() -> None:
    descriptor = _descriptor(
        "gold-timestamp-key-drift-proof",
        _scalar("window_start_utc", WyscoutArrowScalarType.TIMESTAMP_US_UTC),
    )
    timestamp = datetime(2017, 8, 11, tzinfo=UTC)
    table = pa.Table.from_pylist(
        [{"window_start_utc": timestamp}],
        schema=arrow_schema_from_w04_projection(descriptor),
    )
    contract_rows = (canonical_json_bytes({"window_start_utc": "2017-08-11T00:00:00Z"}),)
    with pytest.raises(FormatError, match="unsupported type"):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("window_start_utc",),
            primary_keys=cast(tuple[tuple[str | int, ...], ...], ((timestamp,),)),
            contract_row_bytes=contract_rows,
            parent_paths=(),
        )
    with pytest.raises(FormatError, match="does not exactly equal"):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("window_start_utc",),
            primary_keys=(("2017-08-11T00:00:00.000000Z",),),
            contract_row_bytes=contract_rows,
            parent_paths=(),
        )


def test_nested_primary_key_path_never_falls_back_to_top_level_alias() -> None:
    descriptor = _descriptor(
        "silver-nested-key-fallback-proof",
        _scalar("tenant_id", WyscoutArrowScalarType.UTF8),
        _scalar("record_id", WyscoutArrowScalarType.INT64),
    )
    row = {"tenant_id": "tenant-a", "record_id": 1}
    with pytest.raises(FormatError, match="not present"):
        _encode_nested_keys(
            (row,),
            descriptor=descriptor,
            primary_key_fields=("tenant_context.tenant_id",),
            primary_keys=(("tenant-a",),),
        )


def test_primary_key_path_cannot_descend_through_a_list_or_positional_struct() -> None:
    list_descriptor = _descriptor(
        "silver-list-key-path-proof",
        WyscoutArrowProjectionField(
            "values",
            False,
            WyscoutArrowListNode(
                WyscoutLogicalArrowProjectionKind.HOMOGENEOUS_LIST,
                WyscoutArrowListKind.LIST,
                _scalar("item", WyscoutArrowScalarType.INT64),
            ),
        ),
    )
    tuple_descriptor = _descriptor(
        "silver-positional-key-path-proof",
        WyscoutArrowProjectionField(
            "pair",
            False,
            WyscoutArrowStructNode(
                WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT,
                (
                    _scalar(
                        "slot_0",
                        WyscoutArrowScalarType.UTF8,
                        logical_position=0,
                    ),
                ),
            ),
        ),
    )
    for descriptor, row, path in (
        (list_descriptor, {"values": [1]}, "values.item"),
        (tuple_descriptor, {"pair": ["value"]}, "pair.slot_0"),
    ):
        physical_row = row if descriptor is list_descriptor else {"pair": {"slot_0": "value"}}
        with pytest.raises(FormatError, match="fixed object structs"):
            encode_w04_wyscout_product_parquet(
                pa.Table.from_pylist(
                    [physical_row],
                    schema=arrow_schema_from_w04_projection(descriptor),
                ),
                projection_descriptor=descriptor,
                primary_key_fields=(path,),
                primary_keys=((1,) if descriptor is list_descriptor else ("value",),),
                contract_row_bytes=(canonical_json_bytes(row),),
                parent_paths=(),
            )


def test_repeated_rejected_fields_require_complete_source_row_and_json_path_key() -> None:
    descriptor = _descriptor(
        "bronze-rejected-field-key-proof",
        WyscoutArrowProjectionField(
            "source_row",
            False,
            WyscoutArrowStructNode(
                WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT,
                (
                    _scalar("source_manifest_id", WyscoutArrowScalarType.UTF8),
                    _scalar("completion_relative_path", WyscoutArrowScalarType.UTF8),
                    _scalar("source_record_ordinal", WyscoutArrowScalarType.UINT64),
                ),
            ),
        ),
        _scalar("json_path", WyscoutArrowScalarType.UTF8),
        _scalar("evidence", WyscoutArrowScalarType.INT64),
    )
    source_manifest_id = "manifest-a"
    completion_relative_path = "archive-members/events_England.json"
    source_record_ordinal = 7
    source_row = {
        "source_manifest_id": source_manifest_id,
        "completion_relative_path": completion_relative_path,
        "source_record_ordinal": source_record_ordinal,
    }
    rows = (
        {"source_row": source_row, "json_path": "$.eventName", "evidence": 1},
        {"source_row": source_row, "json_path": "$.subEventName", "evidence": 2},
    )
    fields = (
        "source_row.source_manifest_id",
        "source_row.completion_relative_path",
        "source_row.source_record_ordinal",
        "json_path",
    )
    keys: tuple[tuple[str | int, ...], ...] = tuple(
        (
            source_manifest_id,
            completion_relative_path,
            source_record_ordinal,
            cast(str, row["json_path"]),
        )
        for row in rows
    )
    assert (
        _encode_nested_keys(
            rows,
            descriptor=descriptor,
            primary_key_fields=fields,
            primary_keys=keys,
        ).row_count
        == 2
    )
    with pytest.raises(FormatError, match="unique"):
        _encode_nested_keys(
            rows,
            descriptor=descriptor,
            primary_key_fields=fields[:-1],
            primary_keys=(keys[0][:-1], keys[1][:-1]),
        )


@pytest.mark.parametrize(
    "parents",
    [
        ("/absolute.parquet",),
        ("data/../escape.parquet",),
        ("data\\escape.parquet",),
        ("z.parquet", "a.parquet"),
        ("a.parquet", "a.parquet"),
    ],
)
def test_parent_path_failures_are_closed(parents: tuple[str, ...]) -> None:
    with pytest.raises(FormatError):
        _encode(parents=parents)


@pytest.mark.parametrize(
    "contract_rows",
    [
        (b'{"record_id":1}', CONTRACT_ROWS[1]),
        (b'{"record_id":1,"record_id":1}\n', CONTRACT_ROWS[1]),
        (b"[]\n", CONTRACT_ROWS[1]),
        (b"\xff", CONTRACT_ROWS[1]),
        (b'{"label":"e\\u0301","occurred_at":null,"record_id":1}\n', CONTRACT_ROWS[1]),
        (CONTRACT_ROWS[0], CONTRACT_ROWS[0]),
    ],
)
def test_contract_row_failures_are_closed(contract_rows: tuple[bytes, ...]) -> None:
    with pytest.raises(FormatError):
        _encode(contract_rows=contract_rows)


def test_schema_is_generated_only_from_descriptor_and_table_is_exact_readback() -> None:
    assert set(inspect.signature(encode_w04_wyscout_product_parquet).parameters) == {
        "table",
        "projection_descriptor",
        "primary_key_fields",
        "primary_keys",
        "contract_row_bytes",
        "parent_paths",
    }
    assert set(inspect.signature(w04_wyscout_parquet_semantic_sha256).parameters) == {
        "projection_descriptor",
        "contract_row_bytes",
        "parent_paths",
    }
    with pytest.raises(TypeError):
        encode_w04_wyscout_product_parquet(  # type: ignore[call-arg]
            _table(),
            schema=SCHEMA,
            schema_role="silver-action-v1",
            primary_key_fields=("record_id",),
            primary_keys=PRIMARY_KEYS,
            contract_row_bytes=CONTRACT_ROWS,
            parent_paths=PARENTS,
        )
    with pytest.raises(TypeError):
        w04_wyscout_parquet_semantic_sha256(  # type: ignore[call-arg]
            schema=SCHEMA,
            contract_row_bytes=CONTRACT_ROWS,
            parent_paths=PARENTS,
        )
    for table in (
        pa.table({"record_id": [1, 2], "label": ["a", "b"]}),
        pa.table(
            {
                "record_id": [1, 2],
                "label": ["a", "b"],
                "occurred_at": [None, None],
                "extra": [1, 2],
            }
        ),
    ):
        with pytest.raises(FormatError, match="does not exactly equal"):
            _encode(table=table)


def test_all_identity_scalar_and_recursive_types_project_exactly() -> None:
    metadata = WyscoutArrowProjectionField(
        name="metadata",
        nullable=False,
        node=WyscoutArrowStructNode(
            projection_kind=WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT,
            children=(
                _scalar("name", WyscoutArrowScalarType.UTF8),
                _scalar("rank", WyscoutArrowScalarType.UINT16, nullable=True),
            ),
        ),
    )
    descriptor = _descriptor(
        "silver-recursive-types-proof",
        _scalar("record_id", WyscoutArrowScalarType.UINT64),
        _scalar(
            "amount",
            WyscoutArrowScalarType.DECIMAL128,
            precision=8,
            scale=2,
        ),
        WyscoutArrowProjectionField(
            "tags",
            True,
            WyscoutArrowListNode(
                WyscoutLogicalArrowProjectionKind.HOMOGENEOUS_LIST,
                WyscoutArrowListKind.LIST,
                _scalar("item", WyscoutArrowScalarType.UTF8),
            ),
        ),
        WyscoutArrowProjectionField(
            "history",
            True,
            WyscoutArrowListNode(
                WyscoutLogicalArrowProjectionKind.HOMOGENEOUS_LIST,
                WyscoutArrowListKind.LARGE_LIST,
                _scalar("item", WyscoutArrowScalarType.INT16),
            ),
        ),
        WyscoutArrowProjectionField(
            "coordinates",
            True,
            WyscoutArrowListNode(
                WyscoutLogicalArrowProjectionKind.HOMOGENEOUS_LIST,
                WyscoutArrowListKind.FIXED_SIZE_LIST,
                _scalar("item", WyscoutArrowScalarType.FLOAT64),
                2,
            ),
        ),
        metadata,
    )
    row = {
        "record_id": 7,
        "amount": Decimal("12.30"),
        "tags": ["a", "b"],
        "history": [1, 2],
        "coordinates": [1.5, 2.5],
        "metadata": {"name": "sample", "rank": None},
    }
    logical = {**row, "amount": "12.30"}
    encoded = _single_row_encode(descriptor, row, logical)
    assert encoded.row_count == 1


def _tagged_descriptor(*, nullable: bool = False) -> WyscoutParquetProjectionDescriptor:
    return _descriptor(
        "bronze-canonical-json-proof",
        _scalar("record_id", WyscoutArrowScalarType.INT64),
        _scalar(
            "raw_value",
            WyscoutArrowScalarType.UTF8,
            nullable=nullable,
            projection_kind=WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8,
        ),
    )


def _canonical_decimal_descriptor(*, nullable: bool = False) -> WyscoutParquetProjectionDescriptor:
    return _descriptor(
        "gold-canonical-decimal-proof",
        _scalar("record_id", WyscoutArrowScalarType.INT64),
        _scalar(
            "coverage",
            WyscoutArrowScalarType.UTF8,
            nullable=nullable,
            projection_kind=WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8,
        ),
    )


def _exact_decimal_descriptor(*, nullable: bool = False) -> WyscoutParquetProjectionDescriptor:
    return _descriptor(
        "silver-exact-decimal-proof",
        _scalar("record_id", WyscoutArrowScalarType.INT64),
        WyscoutArrowProjectionField(
            "amount",
            nullable,
            WyscoutArrowStructNode(
                WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT,
                (
                    _scalar(
                        "value",
                        WyscoutArrowScalarType.DECIMAL128,
                        precision=22,
                        scale=18,
                    ),
                    _scalar("exponent", WyscoutArrowScalarType.INT8),
                    _scalar("negative_zero", WyscoutArrowScalarType.BOOL),
                ),
            ),
        ),
    )


@pytest.mark.parametrize(
    "value",
    [
        Decimal("10"),
        Decimal("1.000000000000000000"),
        Decimal("1E+3"),
        Decimal("12.3400"),
        Decimal("0"),
        Decimal("-0"),
        Decimal("0.000000000000000000"),
        Decimal("-0.000000000000000000"),
        Decimal("9999.999999999999999999"),
        Decimal("0.000000000000000001"),
    ],
)
def test_exact_decimal128_with_exponent_round_trips_exact_json_token(
    value: Decimal,
) -> None:
    physical = exact_decimal128_with_exponent_to_w04_arrow(
        value,
        declared_scale=max(0, -cast(int, value.as_tuple().exponent)),
    )
    assert physical["exponent"] == value.as_tuple().exponent
    assert physical["negative_zero"] is (value.is_zero() and value.is_signed())
    assert cast(Decimal, physical["value"]).as_tuple().exponent == -18
    encoded = _single_row_encode(
        _exact_decimal_descriptor(),
        {"record_id": 1, "amount": physical},
        {"record_id": 1, "amount": str(value)},
    )
    assert encoded.row_count == 1


@pytest.mark.parametrize(
    ("numeric_value", "negative_zero", "expected"),
    [
        (Decimal("0E-18"), False, "0"),
        (Decimal("0E-18"), True, "-0"),
        (Decimal("-0E-18"), False, "0"),
        (Decimal("-0E-18"), True, "-0"),
    ],
)
def test_exact_decimal_inverse_zero_sign_is_set_only_by_boolean(
    numeric_value: Decimal,
    negative_zero: bool,
    expected: str,
) -> None:
    class FakeChildScalar:
        is_valid = True

        def __init__(self, value: object) -> None:
            self._value = value

        def as_py(self) -> object:
            return self._value

    class FakeStructScalar:
        is_valid = True
        type = pa.struct(
            [
                pa.field("value", pa.decimal128(22, 18), nullable=False),
                pa.field("exponent", pa.int8(), nullable=False),
                pa.field("negative_zero", pa.bool_(), nullable=False),
            ]
        )

        def __init__(self) -> None:
            self._children = (
                FakeChildScalar(numeric_value),
                FakeChildScalar(0),
                FakeChildScalar(negative_zero),
            )

        def __getitem__(self, index: int) -> FakeChildScalar:
            return self._children[index]

    assert (
        formats_module._decode_exact_decimal128_with_exponent(
            cast(pa.Scalar, FakeStructScalar()),
            location="amount",
        )
        == expected
    )


def test_exact_decimal_projection_keeps_coverage_on_canonical_utf8() -> None:
    coverage = _canonical_decimal_descriptor().fields[1]
    assert type(coverage.node) is WyscoutArrowScalarNode
    assert coverage.node.scalar_type is WyscoutArrowScalarType.UTF8
    assert coverage.node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8


@pytest.mark.parametrize(
    ("value", "declared_scale"),
    [
        (None, None),
        (True, None),
        (1, None),
        ("1", None),
        (Decimal("NaN"), None),
        (Decimal("Infinity"), None),
        (Decimal("1"), True),
        (Decimal("1"), 1),
        (Decimal("1.0"), 0),
        (Decimal("10000"), 0),
        (Decimal("1.0000000000000000000"), 19),
        (Decimal("0.0000000000000000001"), 19),
    ],
)
def test_exact_decimal_forward_rejects_wrong_type_scale_and_capacity(
    value: object,
    declared_scale: int | None,
) -> None:
    with pytest.raises(FormatError):
        exact_decimal128_with_exponent_to_w04_arrow(
            value,
            declared_scale=declared_scale,
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "omit",
        "add",
        "order",
        "name",
        "value-type",
        "value-precision",
        "value-scale",
        "exponent-type",
        "sign-type",
        "child-nullable",
        "logical-position",
    ],
)
def test_exact_decimal_descriptor_drift_fails_closed(
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _exact_decimal_descriptor()
    amount = descriptor.fields[1]
    assert type(amount.node) is WyscoutArrowStructNode
    children = list(amount.node.children)
    if mutation == "omit":
        children.pop()
    elif mutation == "add":
        children.append(_scalar("extra", WyscoutArrowScalarType.INT8))
    elif mutation == "order":
        children[0], children[1] = children[1], children[0]
    elif mutation == "name":
        children[0] = replace(children[0], name="numeric_value")
    elif mutation == "value-type":
        children[0] = _scalar("value", WyscoutArrowScalarType.FLOAT64)
    elif mutation == "value-precision":
        children[0] = _scalar("value", WyscoutArrowScalarType.DECIMAL128, precision=21, scale=18)
    elif mutation == "value-scale":
        children[0] = _scalar("value", WyscoutArrowScalarType.DECIMAL128, precision=22, scale=17)
    elif mutation == "exponent-type":
        children[1] = _scalar("exponent", WyscoutArrowScalarType.INT16)
    elif mutation == "sign-type":
        children[2] = _scalar("negative_zero", WyscoutArrowScalarType.INT8)
    elif mutation == "child-nullable":
        children[1] = replace(children[1], nullable=True)
    else:
        children[2] = replace(children[2], logical_position=2)
    node = replace(amount.node, children=tuple(children))
    hash_calls = 0
    writes = 0

    def unexpected_hash(*args: object, **kwargs: object) -> str:
        nonlocal hash_calls
        hash_calls += 1
        raise AssertionError("invalid exact Decimal descriptor reached semantic hashing")

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1
        raise AssertionError("invalid exact Decimal descriptor reached Parquet writing")

    monkeypatch.setattr(
        formats_module,
        "w04_wyscout_parquet_semantic_sha256",
        unexpected_hash,
    )
    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError):
        arrow_schema_from_w04_projection(
            replace(descriptor, fields=(descriptor.fields[0], replace(amount, node=node)))
        )
    assert hash_calls == 0
    assert writes == 0


@pytest.mark.parametrize(
    ("physical", "logical"),
    [
        (
            {"value": Decimal("1.230000000000000000"), "exponent": -1, "negative_zero": False},
            "1.2",
        ),
        (
            {"value": Decimal("1.000000000000000000"), "exponent": 0, "negative_zero": True},
            "1",
        ),
        (
            {"value": Decimal("0E-18"), "exponent": -19, "negative_zero": False},
            "0E-19",
        ),
        (
            {"value": Decimal("0E-18"), "exponent": 4, "negative_zero": False},
            "0E+4",
        ),
        (
            {"value": None, "exponent": 0, "negative_zero": False},
            "0",
        ),
        (
            {"value": Decimal("0E-18"), "exponent": None, "negative_zero": False},
            "0",
        ),
        (
            {"value": Decimal("0E-18"), "exponent": 0, "negative_zero": None},
            "0",
        ),
        (
            {"value": Decimal("1.000000000000000000"), "exponent": 0, "negative_zero": False},
            1,
        ),
    ],
)
def test_invalid_exact_decimal_inverse_reaches_neither_hash_nor_write(
    physical: dict[str, object],
    logical: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _exact_decimal_descriptor()
    table = pa.Table.from_pylist(
        [{"record_id": 1, "amount": physical}],
        schema=arrow_schema_from_w04_projection(descriptor),
    )
    hash_calls = 0
    writes = 0

    def unexpected_hash(*args: object, **kwargs: object) -> str:
        nonlocal hash_calls
        hash_calls += 1
        raise AssertionError("invalid exact Decimal reached semantic hashing")

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1
        raise AssertionError("invalid exact Decimal reached Parquet writing")

    monkeypatch.setattr(
        formats_module,
        "w04_wyscout_parquet_semantic_sha256",
        unexpected_hash,
    )
    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "amount": logical}),),
            parent_paths=(),
        )
    assert hash_calls == 0
    assert writes == 0


def test_exact_decimal_outer_null_is_the_only_nullable_state() -> None:
    descriptor = _exact_decimal_descriptor(nullable=True)
    assert (
        _single_row_encode(
            descriptor,
            {"record_id": 1, "amount": None},
            {"record_id": 1, "amount": None},
        ).row_count
        == 1
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "outer-type",
        "child-order",
        "child-name",
        "value-type",
        "exponent-type",
        "sign-type",
        "child-nullable",
        "schema-metadata",
        "top-metadata",
        "child-metadata",
    ],
)
def test_exact_decimal_physical_schema_drift_reaches_neither_hash_nor_write(
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _exact_decimal_descriptor()
    schema = arrow_schema_from_w04_projection(descriptor)
    amount = schema.field("amount")
    children = list(cast_struct_fields(amount.type))
    metadata: dict[bytes, bytes] | None = None
    record_id = schema.field("record_id")
    if mutation == "outer-type":
        amount = pa.field("amount", pa.string(), nullable=False)
        physical: object = "1"
    else:
        physical = {"value": Decimal("1.000000000000000000"), "exponent": 0, "negative_zero": False}
        if mutation == "child-order":
            children[0], children[1] = children[1], children[0]
        elif mutation == "child-name":
            children[0] = pa.field("numeric", children[0].type, nullable=False)
            physical = {
                "numeric": Decimal("1.000000000000000000"),
                "exponent": 0,
                "negative_zero": False,
            }
        elif mutation == "value-type":
            children[0] = pa.field("value", pa.float64(), nullable=False)
            physical = {"value": 1.0, "exponent": 0, "negative_zero": False}
        elif mutation == "exponent-type":
            children[1] = pa.field("exponent", pa.int16(), nullable=False)
        elif mutation == "sign-type":
            children[2] = pa.field("negative_zero", pa.int8(), nullable=False)
            physical = {"value": Decimal("1.000000000000000000"), "exponent": 0, "negative_zero": 0}
        elif mutation == "child-nullable":
            children[1] = pa.field("exponent", pa.int8(), nullable=True)
        elif mutation == "schema-metadata":
            metadata = {}
        elif mutation == "top-metadata":
            amount = pa.field("amount", amount.type, nullable=False, metadata={})
        elif mutation == "child-metadata":
            children[0] = pa.field("value", pa.decimal128(22, 18), nullable=False, metadata={})
        if mutation not in {"top-metadata", "schema-metadata"}:
            amount = pa.field("amount", pa.struct(children), nullable=False)
    drift = pa.schema([record_id, amount], metadata=metadata)
    table = pa.Table.from_pylist(
        [{"record_id": 1, "amount": physical}],
        schema=drift,
    )
    hash_calls = 0
    writes = 0

    def unexpected_hash(*args: object, **kwargs: object) -> str:
        nonlocal hash_calls
        hash_calls += 1
        raise AssertionError("invalid exact Decimal schema reached semantic hashing")

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1
        raise AssertionError("invalid exact Decimal schema reached Parquet writing")

    monkeypatch.setattr(
        formats_module,
        "w04_wyscout_parquet_semantic_sha256",
        unexpected_hash,
    )
    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "amount": "1"}),),
            parent_paths=(),
        )
    assert hash_calls == 0
    assert writes == 0


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("0"), "0"),
        (Decimal("-0"), "0"),
        (Decimal("1"), "1"),
        (Decimal("1.2300"), "1.23"),
        (Decimal("1E+3"), "1000"),
        (
            Decimal("0.33333333333333333333333333333333333333"),
            "0.33333333333333333333333333333333333333",
        ),
        (Decimal("1E-40"), "0.0000000000000000000000000000000000000001"),
        (Decimal("1E+40"), "10000000000000000000000000000000000000000"),
    ],
)
def test_canonical_decimal_forward_projection_is_exact(
    value: Decimal,
    expected: str,
) -> None:
    rendered = canonical_decimal_to_w04_arrow_utf8(value)
    assert rendered == expected
    assert rendered.encode("utf-8") == expected.encode("utf-8")
    assert not rendered.endswith("\n")
    encoded = _single_row_encode(
        _canonical_decimal_descriptor(),
        {"record_id": 1, "coverage": rendered},
        {"record_id": 1, "coverage": expected},
    )
    assert encoded.row_count == 1


@pytest.mark.parametrize(
    "value",
    [None, True, 1, 1.0, "1", Decimal("NaN"), Decimal("Infinity")],
)
def test_canonical_decimal_forward_rejects_non_exact_or_nonfinite_values(
    value: object,
) -> None:
    with pytest.raises(FormatError):
        canonical_decimal_to_w04_arrow_utf8(value)


@pytest.mark.parametrize(
    "alias",
    [
        "",
        " 1",
        "\t1",
        "1 ",
        "1\n",
        "\ufeff1",
        "+1",
        "01",
        "00",
        "1.0",
        "1.2300",
        "-0",
        "-0.0",
        "0.0",
        "0.10",
        ".1",
        "1.",
        "-01",
        "1e3",
        "1E+3",
        "NaN",
        "sNaN",
        "Infinity",
        "-Infinity",
    ],
)
def test_canonical_decimal_inverse_rejects_every_noncanonical_alias(
    alias: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _canonical_decimal_descriptor()
    schema = arrow_schema_from_w04_projection(descriptor)
    table = pa.Table.from_pylist([{"record_id": 1, "coverage": alias}], schema=schema)
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "coverage": alias}),),
            parent_paths=(),
        )
    assert writes == 0


def test_canonical_decimal_arrow_null_is_only_outer_optionality(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nonnullable = _canonical_decimal_descriptor()
    null_table = pa.Table.from_pylist(
        [{"record_id": 1, "coverage": None}],
        schema=arrow_schema_from_w04_projection(nonnullable),
    )
    writes = 0
    original_write = pq.write_table

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError, match="null"):
        encode_w04_wyscout_product_parquet(
            null_table,
            projection_descriptor=nonnullable,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "coverage": None}),),
            parent_paths=(),
        )
    assert writes == 0
    monkeypatch.setattr(pq, "write_table", original_write)

    nullable = _canonical_decimal_descriptor(nullable=True)
    assert (
        _single_row_encode(
            nullable,
            {"record_id": 1, "coverage": None},
            {"record_id": 1, "coverage": None},
        ).row_count
        == 1
    )


def test_invalid_utf8_canonical_decimal_scalar_fails_before_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _canonical_decimal_descriptor()
    offsets = pa.py_buffer(struct.pack("<ii", 0, 1))
    invalid = pa.Array.from_buffers(pa.string(), 1, [None, offsets, pa.py_buffer(b"\xff")])
    table = pa.Table.from_arrays(
        [pa.array([1], type=pa.int64()), invalid],
        schema=arrow_schema_from_w04_projection(descriptor),
    )
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError, match="strict UTF-8"):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "coverage": "1"}),),
            parent_paths=(),
        )
    assert writes == 0


@pytest.mark.parametrize(
    ("value", "arrow_type"),
    [
        (1, pa.int64()),
        (1.0, pa.float64()),
        (b"1", pa.binary()),
        (Decimal("1.00"), pa.decimal128(22, 18)),
    ],
)
def test_non_string_canonical_decimal_physical_scalars_fail_before_write(
    value: object,
    arrow_type: pa.DataType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _canonical_decimal_descriptor()
    drift_schema = pa.schema(
        [
            pa.field("record_id", pa.int64(), nullable=False),
            pa.field("coverage", arrow_type, nullable=False),
        ]
    )
    table = pa.Table.from_arrays(
        [pa.array([1], type=pa.int64()), pa.array([value], type=arrow_type)],
        schema=drift_schema,
    )
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "coverage": "1"}),),
            parent_paths=(),
        )
    assert writes == 0


def _tagged_dump(value: CanonicalJsonValue) -> dict[str, object]:
    return value.model_dump(mode="json")


TAGGED_VALUES: tuple[CanonicalJsonValue, ...] = (
    CanonicalJsonNull(),
    CanonicalJsonBoolean(value=True),
    CanonicalJsonInteger(value=7),
    CanonicalJsonNumber(value=Decimal("1.25")),
    CanonicalJsonString(value="évidence"),
    CanonicalJsonArray(value=(CanonicalJsonInteger(value=1), CanonicalJsonString(value="two"))),
    CanonicalJsonObject(
        value=(
            CanonicalJsonMember(
                key="array",
                value=CanonicalJsonArray(
                    value=(CanonicalJsonNull(), CanonicalJsonBoolean(value=False))
                ),
            ),
            CanonicalJsonMember(
                key="object",
                value=CanonicalJsonObject(
                    value=(
                        CanonicalJsonMember(
                            key="number",
                            value=CanonicalJsonNumber(value=Decimal("2.5")),
                        ),
                    )
                ),
            ),
        )
    ),
)


def _bypassed_canonical_json_values() -> tuple[tuple[str, object], ...]:
    null = CanonicalJsonNull()
    integer = CanonicalJsonInteger(value=1)
    boolean = CanonicalJsonBoolean(value=True)
    number = CanonicalJsonNumber(value=Decimal("1.25"))
    string = CanonicalJsonString(value="text")
    array = CanonicalJsonArray(value=(integer,))
    member_a = CanonicalJsonMember(key="a", value=null)
    member_b = CanonicalJsonMember(key="b", value=null)
    object_value = CanonicalJsonObject(value=(member_a,))
    direct: tuple[tuple[str, object], ...] = (
        ("copy-boolean-as-integer", integer.model_copy(update={"value": True})),
        ("construct-boolean-as-integer", CanonicalJsonInteger.model_construct(value=True)),
        ("copy-float-as-integer", integer.model_copy(update={"value": 1.0})),
        ("construct-float-as-integer", CanonicalJsonInteger.model_construct(value=1.0)),
        ("copy-string-as-integer", integer.model_copy(update={"value": "1"})),
        ("construct-string-as-integer", CanonicalJsonInteger.model_construct(value="1")),
        ("copy-integer-as-boolean", boolean.model_copy(update={"value": 1})),
        ("construct-integer-as-boolean", CanonicalJsonBoolean.model_construct(value=1)),
        ("copy-list-as-array-tuple", array.model_copy(update={"value": [integer]})),
        ("construct-list-as-array-tuple", CanonicalJsonArray.model_construct(value=[integer])),
        (
            "copy-bare-dict-as-array-child",
            array.model_copy(update={"value": ({"kind": CanonicalJsonKind.INTEGER, "value": 1},)}),
        ),
        (
            "construct-bare-dict-as-array-child",
            CanonicalJsonArray.model_construct(
                value=({"kind": CanonicalJsonKind.INTEGER, "value": 1},)
            ),
        ),
        (
            "copy-wrong-discriminator",
            integer.model_copy(update={"kind": CanonicalJsonKind.BOOLEAN}),
        ),
        (
            "construct-wrong-discriminator",
            CanonicalJsonInteger.model_construct(
                kind=CanonicalJsonKind.BOOLEAN,
                value=1,
            ),
        ),
        ("copy-extra-value-state", integer.model_copy(update={"extra": 1})),
        (
            "copy-extra-member-state",
            object_value.model_copy(update={"value": (member_a.model_copy(update={"extra": 1}),)}),
        ),
        (
            "construct-extra-member-field-set-state",
            CanonicalJsonObject.model_construct(
                value=(
                    CanonicalJsonMember.model_construct(
                        _fields_set={"extra", "key", "value"},
                        key="a",
                        value=null,
                    ),
                )
            ),
        ),
        (
            "copy-duplicate-object-members",
            object_value.model_copy(update={"value": (member_a, member_a)}),
        ),
        (
            "construct-duplicate-object-members",
            CanonicalJsonObject.model_construct(value=(member_a, member_a)),
        ),
        (
            "copy-unsorted-object-members",
            object_value.model_copy(update={"value": (member_b, member_a)}),
        ),
        (
            "construct-unsorted-object-members",
            CanonicalJsonObject.model_construct(value=(member_b, member_a)),
        ),
        (
            "copy-non-finite-decimal",
            number.model_copy(update={"value": Decimal("NaN")}),
        ),
        (
            "construct-non-finite-decimal",
            CanonicalJsonNumber.model_construct(value=Decimal("Infinity")),
        ),
        ("copy-non-nfc-text", string.model_copy(update={"value": "e\u0301"})),
        ("construct-non-nfc-text", CanonicalJsonString.model_construct(value="e\u0301")),
        ("copy-surrogate-text", string.model_copy(update={"value": "\ud800"})),
        ("construct-surrogate-text", CanonicalJsonString.model_construct(value="\ud800")),
    )
    nested_copy = tuple(
        (
            f"nested-copy-array-{name}",
            CanonicalJsonArray(value=(null,)).model_copy(update={"value": (value,)}),
        )
        for name, value in direct
    )
    nested_construct = tuple(
        (
            f"nested-construct-object-{name}",
            CanonicalJsonObject.model_construct(
                value=(CanonicalJsonMember.model_construct(key="child", value=value),)
            ),
        )
        for name, value in direct
    )
    return direct + nested_copy + nested_construct


BYPASSED_CANONICAL_JSON_VALUES = _bypassed_canonical_json_values()


@pytest.mark.parametrize("value", TAGGED_VALUES)
def test_all_seven_tagged_variants_round_trip_exactly(value: CanonicalJsonValue) -> None:
    text = canonical_json_value_to_w04_arrow_utf8(value)
    assert not text.endswith("\n")
    encoded = _single_row_encode(
        _tagged_descriptor(),
        {"record_id": 1, "raw_value": text},
        {"record_id": 1, "raw_value": _tagged_dump(value)},
    )
    assert encoded.row_count == 1


@pytest.mark.parametrize(
    ("case_name", "value"),
    BYPASSED_CANONICAL_JSON_VALUES,
    ids=[name for name, _value in BYPASSED_CANONICAL_JSON_VALUES],
)
def test_copied_constructed_direct_and_nested_tagged_state_fails_closed(
    case_name: str,
    value: object,
) -> None:
    assert case_name
    with pytest.raises(FormatError):
        canonical_json_value_to_w04_arrow_utf8(value)


@pytest.mark.parametrize(
    "value",
    [
        CanonicalJsonInteger(value=1).model_copy(update={"value": True}),
        CanonicalJsonInteger.model_construct(value=True),
    ],
    ids=["copied-boolean-as-integer", "constructed-boolean-as-integer"],
)
def test_bypassed_tagged_state_cannot_reach_semantic_hash_or_parquet_write(
    value: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    semantic_calls = 0
    writes = 0

    def unexpected_semantic_hash(*args: object, **kwargs: object) -> str:
        nonlocal semantic_calls
        semantic_calls += 1
        raise AssertionError("invalid tagged state reached semantic hashing")

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1
        raise AssertionError("invalid tagged state reached Parquet writing")

    monkeypatch.setattr(
        formats_module,
        "w04_wyscout_parquet_semantic_sha256",
        unexpected_semantic_hash,
    )
    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError):
        text = canonical_json_value_to_w04_arrow_utf8(value)
        _single_row_encode(
            _tagged_descriptor(),
            {"record_id": 1, "raw_value": text},
            {
                "record_id": 1,
                "raw_value": {"kind": "integer", "value": 1},
            },
        )
    assert semantic_calls == 0
    assert writes == 0


def test_bypassed_tagged_state_is_rejected_before_pydantic_json_dump(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = CanonicalJsonInteger(value=1).model_copy(update={"value": True})
    dumps = 0

    def unexpected_dump(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal dumps
        dumps += 1
        raise AssertionError("invalid tagged state reached Pydantic JSON serialization")

    monkeypatch.setattr(CanonicalJsonInteger, "model_dump", unexpected_dump)
    with pytest.raises(FormatError):
        canonical_json_value_to_w04_arrow_utf8(value)
    assert dumps == 0


@pytest.mark.parametrize(
    "value",
    [CanonicalJsonString(value="e\u0301"), CanonicalJsonString(value="\ud800")],
)
def test_tagged_writer_rejects_non_nfc_and_surrogate_text(value: CanonicalJsonValue) -> None:
    with pytest.raises(FormatError):
        canonical_json_value_to_w04_arrow_utf8(value)


def test_present_tagged_null_is_non_null_and_distinct_from_outer_absence() -> None:
    descriptor = _tagged_descriptor(nullable=True)
    null_text = canonical_json_value_to_w04_arrow_utf8(CanonicalJsonNull())
    assert null_text == '{"kind":"null","value":null}'
    table = pa.Table.from_pylist(
        [
            {"record_id": 1, "raw_value": null_text},
            {"record_id": 2, "raw_value": None},
        ],
        schema=arrow_schema_from_w04_projection(descriptor),
    )
    encoded = encode_w04_wyscout_product_parquet(
        table,
        projection_descriptor=descriptor,
        primary_key_fields=("record_id",),
        primary_keys=((1,), (2,)),
        contract_row_bytes=(
            canonical_json_bytes({"record_id": 1, "raw_value": _tagged_dump(CanonicalJsonNull())}),
            canonical_json_bytes({"record_id": 2, "raw_value": None}),
        ),
        parent_paths=(),
    )
    assert encoded.row_count == 2

    nonnullable = _tagged_descriptor()
    invalid = pa.Table.from_arrays(
        [pa.array([1], type=pa.int64()), pa.array([None], type=pa.string())],
        schema=arrow_schema_from_w04_projection(nonnullable),
    )
    with pytest.raises(FormatError, match="null"):
        encode_w04_wyscout_product_parquet(
            invalid,
            projection_descriptor=nonnullable,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "raw_value": None}),),
            parent_paths=(),
        )


MALFORMED_TAGGED_TEXT = (
    '{"kind":"object","value":[{"key":"a","value":{"kind":"integer","value":1,"value":2}}]}',
    '{"kind":"number","value":NaN}',
    '{"kind":"integer","value":1.0}',
    '{ "kind":"null","value":null}',
    '{"value":null,"kind":"null"}',
    '{"kind":"string","value":"\\u00e9"}',
    '{"kind":"string","value":"e\u0301"}',
    '{"kind":"unknown","value":null}',
    '{"kind":"integer"}',
    '{"extra":0,"kind":"integer","value":1}',
    '{"kind":"integer","value":"1"}',
    "null",
)


@pytest.mark.parametrize("text", MALFORMED_TAGGED_TEXT)
def test_malformed_tagged_encodings_fail_before_write(
    text: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _tagged_descriptor()
    table = pa.Table.from_pylist(
        [{"record_id": 1, "raw_value": text}],
        schema=arrow_schema_from_w04_projection(descriptor),
    )
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "raw_value": {}}),),
            parent_paths=(),
        )
    assert writes == 0


def test_invalid_utf8_tagged_scalar_fails_before_write(monkeypatch: pytest.MonkeyPatch) -> None:
    descriptor = _tagged_descriptor()
    offsets = pa.py_buffer(struct.pack("<ii", 0, 1))
    invalid = pa.Array.from_buffers(pa.string(), 1, [None, offsets, pa.py_buffer(b"\xff")])
    table = pa.Table.from_arrays(
        [pa.array([1], type=pa.int64()), invalid],
        schema=arrow_schema_from_w04_projection(descriptor),
    )
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError, match="strict UTF-8"):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "raw_value": {}}),),
            parent_paths=(),
        )
    assert writes == 0


def _tuple_descriptor() -> WyscoutParquetProjectionDescriptor:
    return _descriptor(
        "silver-positional-tuple-proof",
        _scalar("record_id", WyscoutArrowScalarType.INT64),
        WyscoutArrowProjectionField(
            "pair",
            False,
            WyscoutArrowStructNode(
                WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT,
                (
                    _scalar("slot_0", WyscoutArrowScalarType.UTF8, logical_position=0),
                    _scalar(
                        "slot_1",
                        WyscoutArrowScalarType.INT64,
                        nullable=True,
                        logical_position=1,
                    ),
                ),
            ),
        ),
    )


def test_positional_tuple_restores_array_order_and_child_nullability() -> None:
    descriptor = _tuple_descriptor()
    for value, logical in (
        ({"slot_0": "first", "slot_1": 2}, ["first", 2]),
        ({"slot_0": "first", "slot_1": None}, ["first", None]),
    ):
        assert (
            _single_row_encode(
                descriptor,
                {"record_id": 1, "pair": value},
                {"record_id": 1, "pair": logical},
            ).row_count
            == 1
        )


@pytest.mark.parametrize("mutation", ["duplicate", "gap", "reorder", "object-position"])
def test_tuple_position_and_shape_descriptor_drift_fails_closed(mutation: str) -> None:
    descriptor = _tuple_descriptor()
    pair = descriptor.fields[1]
    assert type(pair.node) is WyscoutArrowStructNode
    children = list(pair.node.children)
    if mutation == "duplicate":
        children[1] = replace(children[1], logical_position=0)
    elif mutation == "gap":
        children[1] = replace(children[1], logical_position=2)
    elif mutation == "reorder":
        children.reverse()
    else:
        descriptor = replace(
            descriptor,
            fields=(
                descriptor.fields[0],
                replace(
                    pair,
                    node=replace(
                        pair.node,
                        projection_kind=WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT,
                    ),
                ),
            ),
        )
    if mutation != "object-position":
        descriptor = replace(
            descriptor,
            fields=(
                descriptor.fields[0],
                replace(pair, node=replace(pair.node, children=tuple(children))),
            ),
        )
    with pytest.raises(FormatError):
        arrow_schema_from_w04_projection(descriptor)


@pytest.mark.parametrize("mutation", ["omit", "add", "rename", "reorder", "type", "nullable"])
def test_tuple_physical_schema_drift_fails_before_write(
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _tuple_descriptor()
    schema = arrow_schema_from_w04_projection(descriptor)
    fields = list(cast_struct_fields(schema.field("pair").type))
    if mutation == "omit":
        fields.pop()
    elif mutation == "add":
        fields.append(pa.field("slot_2", pa.int64(), nullable=False))
    elif mutation == "rename":
        fields[0] = pa.field("renamed", fields[0].type, nullable=fields[0].nullable)
    elif mutation == "reorder":
        fields.reverse()
    elif mutation == "type":
        fields[1] = pa.field("slot_1", pa.int32(), nullable=True)
    else:
        fields[1] = pa.field("slot_1", pa.int64(), nullable=False)
    drift = pa.schema(
        [schema.field("record_id"), pa.field("pair", pa.struct(fields), nullable=False)]
    )
    physical = {field.name: "text" if pa.types.is_string(field.type) else 1 for field in fields}
    table = pa.Table.from_pylist([{"record_id": 1, "pair": physical}], schema=drift)
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError, match="does not exactly equal"):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "pair": []}),),
            parent_paths=(),
        )
    assert writes == 0


def cast_struct_fields(data_type: pa.DataType) -> tuple[pa.Field, ...]:
    assert pa.types.is_struct(data_type)
    return tuple(data_type)


def _list_descriptor(
    *,
    list_kind: WyscoutArrowListKind = WyscoutArrowListKind.LIST,
    item_name: str = "item",
    item_nullable: bool = False,
    fixed_size: int | None = None,
) -> WyscoutParquetProjectionDescriptor:
    return _descriptor(
        "silver-list-proof",
        _scalar("record_id", WyscoutArrowScalarType.INT64),
        WyscoutArrowProjectionField(
            "values",
            False,
            WyscoutArrowListNode(
                WyscoutLogicalArrowProjectionKind.HOMOGENEOUS_LIST,
                list_kind,
                _scalar(item_name, WyscoutArrowScalarType.INT64, nullable=item_nullable),
                fixed_size,
            ),
        ),
    )


def test_empty_and_nonempty_lists_have_one_descriptor_schema_and_exact_round_trip() -> None:
    descriptor = _list_descriptor()
    schema = arrow_schema_from_w04_projection(descriptor)
    observed_descriptors = []
    for values in ([], [1, 2]):
        encoded = _single_row_encode(
            descriptor,
            {"record_id": 1, "values": values},
            {"record_id": 1, "values": values},
        )
        observed_descriptors.append(encoded.schema_descriptor)
        assert arrow_schema_from_w04_projection(descriptor).equals(schema, check_metadata=True)
    assert observed_descriptors[0] == observed_descriptors[1]


def test_list_item_nullability_and_fixed_cardinality_are_descriptor_owned() -> None:
    nullable = _list_descriptor(item_nullable=True)
    assert (
        _single_row_encode(
            nullable,
            {"record_id": 1, "values": [None]},
            {"record_id": 1, "values": [None]},
        ).row_count
        == 1
    )
    forbidden = _list_descriptor()
    with pytest.raises(FormatError, match="forbidden null"):
        _single_row_encode(
            forbidden,
            {"record_id": 1, "values": [None]},
            {"record_id": 1, "values": [None]},
        )
    fixed = _list_descriptor(
        list_kind=WyscoutArrowListKind.FIXED_SIZE_LIST,
        fixed_size=2,
    )
    assert (
        _single_row_encode(
            fixed,
            {"record_id": 1, "values": [1, 2]},
            {"record_id": 1, "values": [1, 2]},
        ).row_count
        == 1
    )


@pytest.mark.parametrize("mutation", ["name", "type", "nullable", "kind", "fixed-size"])
def test_list_physical_schema_drift_fails_before_write(
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _list_descriptor()
    schema = arrow_schema_from_w04_projection(descriptor)
    item = schema.field("values").type.value_field
    values = [1]
    if mutation == "name":
        drift_type = pa.list_(pa.field("element", pa.int64(), nullable=False))
    elif mutation == "type":
        drift_type = pa.list_(pa.field("item", pa.int32(), nullable=False))
    elif mutation == "nullable":
        drift_type = pa.list_(pa.field("item", pa.int64(), nullable=True))
    elif mutation == "kind":
        drift_type = pa.large_list(item)
    else:
        drift_type = pa.list_(item, 2)
        values = [1, 2]
    drift = pa.schema([schema.field("record_id"), pa.field("values", drift_type, nullable=False)])
    table = pa.Table.from_pylist([{"record_id": 1, "values": values}], schema=drift)
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError, match="does not exactly equal"):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(canonical_json_bytes({"record_id": 1, "values": values}),),
            parent_paths=(),
        )
    assert writes == 0


@pytest.mark.parametrize(
    "descriptor",
    [
        _list_descriptor(item_name="not-canonical"),
        _list_descriptor(list_kind=WyscoutArrowListKind.LIST, fixed_size=1),
        _list_descriptor(list_kind=WyscoutArrowListKind.FIXED_SIZE_LIST, fixed_size=None),
        _list_descriptor(list_kind=WyscoutArrowListKind.FIXED_SIZE_LIST, fixed_size=0),
    ],
)
def test_list_descriptor_drift_fails_closed(
    descriptor: WyscoutParquetProjectionDescriptor,
) -> None:
    with pytest.raises(FormatError):
        arrow_schema_from_w04_projection(descriptor)


@pytest.mark.parametrize("metadata", [{}, {b"hidden": b"value"}])
@pytest.mark.parametrize("boundary", ["schema", "top", "struct", "list"])
def test_recursive_metadata_presence_fails_before_write(
    metadata: dict[bytes, bytes],
    boundary: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = _descriptor(
        "silver-metadata-proof",
        _scalar("record_id", WyscoutArrowScalarType.INT64),
        WyscoutArrowProjectionField(
            "object_value",
            False,
            WyscoutArrowStructNode(
                WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT,
                (_scalar("child", WyscoutArrowScalarType.INT64),),
            ),
        ),
        WyscoutArrowProjectionField(
            "list_value",
            False,
            WyscoutArrowListNode(
                WyscoutLogicalArrowProjectionKind.HOMOGENEOUS_LIST,
                WyscoutArrowListKind.LIST,
                _scalar("item", WyscoutArrowScalarType.INT64),
            ),
        ),
    )
    schema = arrow_schema_from_w04_projection(descriptor)
    fields = list(schema)
    schema_metadata = None
    if boundary == "schema":
        schema_metadata = metadata
    elif boundary == "top":
        fields[0] = pa.field("record_id", pa.int64(), nullable=False, metadata=metadata)
    elif boundary == "struct":
        fields[1] = pa.field(
            "object_value",
            pa.struct([pa.field("child", pa.int64(), nullable=False, metadata=metadata)]),
            nullable=False,
        )
    else:
        fields[2] = pa.field(
            "list_value",
            pa.list_(pa.field("item", pa.int64(), nullable=False, metadata=metadata)),
            nullable=False,
        )
    drift = pa.schema(fields, metadata=schema_metadata)
    table = pa.Table.from_pylist(
        [{"record_id": 1, "object_value": {"child": 2}, "list_value": [3]}],
        schema=drift,
    )
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    with pytest.raises(FormatError, match="metadata|does not exactly equal"):
        encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=("record_id",),
            primary_keys=((1,),),
            contract_row_bytes=(
                canonical_json_bytes(
                    {"record_id": 1, "object_value": {"child": 2}, "list_value": [3]}
                ),
            ),
            parent_paths=(),
        )
    assert writes == 0


@pytest.mark.parametrize(
    "descriptor",
    [
        replace(IDENTITY_DESCRIPTOR, serializer_version="wrong"),
        replace(IDENTITY_DESCRIPTOR, schema_role="Wrong Role"),
        replace(IDENTITY_DESCRIPTOR, fields=()),
        replace(
            IDENTITY_DESCRIPTOR,
            fields=(
                replace(
                    IDENTITY_DESCRIPTOR.fields[0],
                    nullable=1,  # type: ignore[arg-type]
                ),
            ),
        ),
        _descriptor(
            "bad-json-projection",
            _scalar(
                "value",
                WyscoutArrowScalarType.INT64,
                projection_kind=WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8,
            ),
        ),
        _descriptor(
            "bad-canonical-decimal-projection",
            _scalar(
                "value",
                WyscoutArrowScalarType.DECIMAL128,
                projection_kind=WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8,
                precision=22,
                scale=18,
            ),
        ),
        _descriptor(
            "bad-decimal-projection",
            _scalar("value", WyscoutArrowScalarType.DECIMAL128, precision=39, scale=0),
        ),
        _descriptor(
            "bad-scalar-projection",
            _scalar("value", WyscoutArrowScalarType.INT64, precision=1, scale=0),
        ),
    ],
)
def test_descriptor_runtime_and_scalar_invariants_fail_closed(
    descriptor: WyscoutParquetProjectionDescriptor,
) -> None:
    with pytest.raises(FormatError):
        arrow_schema_from_w04_projection(descriptor)


def test_descriptor_rejects_subclasses_lists_callbacks_and_alternate_objects() -> None:
    class DescriptorSubclass(WyscoutParquetProjectionDescriptor):
        pass

    subclassed = DescriptorSubclass(
        IDENTITY_DESCRIPTOR.schema_role,
        IDENTITY_DESCRIPTOR.serializer_version,
        IDENTITY_DESCRIPTOR.fields,
    )
    with pytest.raises(FormatError, match="exact projection descriptor"):
        arrow_schema_from_w04_projection(subclassed)
    with pytest.raises(FormatError):
        arrow_schema_from_w04_projection(
            replace(
                IDENTITY_DESCRIPTOR,
                fields=cast(
                    tuple[WyscoutArrowProjectionField, ...],
                    list(IDENTITY_DESCRIPTOR.fields),
                ),
            )
        )
    for alternate in (True, hashlib.sha256(b"descriptor").hexdigest(), SCHEMA, lambda: SCHEMA):
        with pytest.raises(FormatError):
            arrow_schema_from_w04_projection(alternate)  # type: ignore[arg-type]


def test_every_malformed_family_causes_zero_parquet_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    writes = 0

    def unexpected_write(*args: object, **kwargs: object) -> None:
        nonlocal writes
        writes += 1

    monkeypatch.setattr(pq, "write_table", unexpected_write)
    malformed_calls: tuple[Callable[[], WyscoutParquetEncoding], ...] = (
        lambda: _encode(descriptor=replace(IDENTITY_DESCRIPTOR, serializer_version="wrong")),
        lambda: _encode(table=_table().replace_schema_metadata({b"x": b"y"})),
        lambda: _encode(contract_rows=(b"{}\n", CONTRACT_ROWS[1])),
        lambda: _encode(primary_keys=((2,), (1,))),
        lambda: _encode(parents=("../escape",)),
    )
    for call in malformed_calls:
        with pytest.raises(FormatError):
            call()
    assert writes == 0

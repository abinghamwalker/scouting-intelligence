"""Deterministic serialization formats for immutable local artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, DecimalException, Inexact, InvalidOperation, localcontext
from enum import StrEnum
from typing import cast

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
from pydantic import TypeAdapter, ValidationError

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

type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | dict[str, JsonValue]
type WyscoutPrimaryKeyValue = str | int

_UINT64_MAX = (1 << 64) - 1
_WYSCOUT_SCHEMA_ROLE = re.compile(r"[a-z][a-z0-9._-]{0,127}")
_WYSCOUT_FIELD_NAME = re.compile(r"[a-z][a-z0-9_]{0,127}")
_WYSCOUT_PARENT_PATH = re.compile(r"[A-Za-z0-9._=/-]+")

WYSCOUT_PARQUET_SERIALIZER_VERSION = "w04-wyscout-parquet-v1"
WYSCOUT_PARQUET_SEMANTIC_VERSION = "w04-wyscout-parquet-semantic-v1"


class FormatError(ValueError):
    """Raised when a value cannot be represented by a deterministic format."""


class WyscoutArrowScalarType(StrEnum):
    """The complete scalar roster admitted by the W04 Arrow projection."""

    NULL = "NULL"
    BOOL = "BOOL"
    INT8 = "INT8"
    INT16 = "INT16"
    INT32 = "INT32"
    INT64 = "INT64"
    UINT8 = "UINT8"
    UINT16 = "UINT16"
    UINT32 = "UINT32"
    UINT64 = "UINT64"
    FLOAT16 = "FLOAT16"
    FLOAT32 = "FLOAT32"
    FLOAT64 = "FLOAT64"
    UTF8 = "UTF8"
    DECIMAL128 = "DECIMAL128"
    TIMESTAMP_US_UTC = "TIMESTAMP_US_UTC"


class WyscoutLogicalArrowProjectionKind(StrEnum):
    """The complete recursive logical-to-Arrow projection roster."""

    IDENTITY = "IDENTITY"
    CANONICAL_JSON_VALUE_UTF8 = "CANONICAL_JSON_VALUE_UTF8"
    CANONICAL_DECIMAL_UTF8 = "CANONICAL_DECIMAL_UTF8"
    EXACT_DECIMAL128_WITH_EXPONENT = "EXACT_DECIMAL128_WITH_EXPONENT"
    OBJECT_STRUCT = "OBJECT_STRUCT"
    POSITIONAL_TUPLE_STRUCT = "POSITIONAL_TUPLE_STRUCT"
    HOMOGENEOUS_LIST = "HOMOGENEOUS_LIST"


class WyscoutArrowListKind(StrEnum):
    """The exact homogeneous Arrow list representation."""

    LIST = "LIST"
    LARGE_LIST = "LARGE_LIST"
    FIXED_SIZE_LIST = "FIXED_SIZE_LIST"


@dataclass(frozen=True, slots=True)
class WyscoutArrowScalarNode:
    """One descriptor-owned Arrow scalar and its logical projection."""

    scalar_type: WyscoutArrowScalarType
    projection_kind: WyscoutLogicalArrowProjectionKind
    decimal_precision: int | None = None
    decimal_scale: int | None = None


@dataclass(frozen=True, slots=True)
class WyscoutArrowStructNode:
    """One descriptor-owned object or positional-tuple struct."""

    projection_kind: WyscoutLogicalArrowProjectionKind
    children: tuple[WyscoutArrowProjectionField, ...]


@dataclass(frozen=True, slots=True)
class WyscoutArrowListNode:
    """One descriptor-owned homogeneous sequence."""

    projection_kind: WyscoutLogicalArrowProjectionKind
    list_kind: WyscoutArrowListKind
    item: WyscoutArrowProjectionField
    fixed_size: int | None = None


type WyscoutArrowProjectionNode = (
    WyscoutArrowScalarNode | WyscoutArrowStructNode | WyscoutArrowListNode
)


@dataclass(frozen=True, slots=True)
class WyscoutArrowProjectionField:
    """One exact named field in a recursive W04 projection descriptor."""

    name: str
    nullable: bool
    node: WyscoutArrowProjectionNode
    logical_position: int | None = None


@dataclass(frozen=True, slots=True)
class WyscoutParquetProjectionDescriptor:
    """The sole descriptor content from which a W04 Arrow schema is generated."""

    schema_role: str
    serializer_version: str
    fields: tuple[WyscoutArrowProjectionField, ...]


@dataclass(frozen=True, slots=True)
class WyscoutParquetSchemaField:
    """One immutable field in a W04 product schema descriptor."""

    name: str
    arrow_type: str
    nullable: bool


@dataclass(frozen=True, slots=True)
class WyscoutParquetSchemaDescriptor:
    """Closed semantic description of an explicit W04 product schema."""

    schema_role: str
    serializer_version: str
    fields: tuple[WyscoutParquetSchemaField, ...]


@dataclass(frozen=True, slots=True)
class WyscoutParquetEncoding:
    """Immutable W04 product bytes and the metadata needed by product owners."""

    payload: bytes
    physical_sha256: str
    size_bytes: int
    semantic_sha256: str
    row_count: int
    schema_descriptor: WyscoutParquetSchemaDescriptor
    schema_descriptor_bytes: bytes
    parent_paths: tuple[str, ...]


def _normalise_json(value: object, *, location: str = "$") -> JsonValue:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise FormatError(f"{location} contains a Unicode surrogate")
        if unicodedata.normalize("NFC", value) != value:
            raise FormatError(f"{location} contains a non-NFC string")
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise FormatError(f"{location} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        normalised: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise FormatError(f"{location} contains a non-string object key")
            if any(0xD800 <= ord(character) <= 0xDFFF for character in key):
                raise FormatError(f"{location} contains a Unicode surrogate object key")
            if unicodedata.normalize("NFC", key) != key:
                raise FormatError(f"{location} contains a non-NFC object key")
            normalised[key] = _normalise_json(item, location=f"{location}.{key}")
        return normalised
    if isinstance(value, (list, tuple)):
        return [
            _normalise_json(item, location=f"{location}[{index}]")
            for index, item in enumerate(value)
        ]
    raise FormatError(f"{location} contains unsupported value type {type(value).__name__}")


def canonical_json_bytes(value: object) -> bytes:
    """Return UTF-8 canonical JSON with one terminal newline."""

    normalised = _normalise_json(value)
    return (
        json.dumps(
            normalised,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[object]) -> bytes:
    """Return canonical, newline-delimited JSON records."""

    encoded_rows = [canonical_json_bytes(row) for row in rows]
    return b"".join(encoded_rows)


def parquet_bytes(rows: Iterable[Mapping[str, object]]) -> bytes:
    """Encode homogeneous records as deterministic Parquet bytes.

    Column order is lexical, row order is retained, and optional encoding features
    that may vary with value distribution are disabled.
    """

    materialised = tuple(dict(row) for row in rows)
    if not materialised:
        raise FormatError("Parquet output requires at least one row")

    columns = tuple(sorted(materialised[0]))
    if not columns:
        raise FormatError("Parquet output requires at least one column")
    expected = set(columns)
    for index, row in enumerate(materialised):
        if set(row) != expected:
            raise FormatError(f"Parquet row {index} does not have the same columns")

    table = pa.table({column: [row[column] for row in materialised] for column in columns})
    sink = pa.BufferOutputStream()
    pq.write_table(
        table,
        sink,
        compression="zstd",
        data_page_version="2.0",
        use_dictionary=False,
        version="2.6",
        write_statistics=False,
    )
    return cast(bytes, sink.getvalue().to_pybytes())


def _require_uint64(value: int, *, label: str) -> bytes:
    if value < 0 or value > _UINT64_MAX:
        raise FormatError(f"{label} exceeds the unsigned 64-bit range")
    return struct.pack(">Q", value)


def _frame_uint64(payload: bytes, *, label: str) -> bytes:
    return _require_uint64(len(payload), label=f"{label} length") + payload


def _reject_duplicate_json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise FormatError(f"contract row contains duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> object:
    raise FormatError(f"contract row contains invalid JSON constant {value}")


def _reject_json_float(value: str) -> object:
    raise FormatError(f"canonical tagged JSON contains forbidden float token {value}")


def _require_nfc_json(value: object, *, location: str = "$") -> None:
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise FormatError(f"{location} contains a Unicode surrogate")
        if unicodedata.normalize("NFC", value) != value:
            raise FormatError(f"{location} contains a non-NFC string")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if any(0xD800 <= ord(character) <= 0xDFFF for character in key):
                raise FormatError(f"{location} contains a Unicode surrogate object key")
            if unicodedata.normalize("NFC", key) != key:
                raise FormatError(f"{location} contains a non-NFC object key")
            _require_nfc_json(item, location=f"{location}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _require_nfc_json(item, location=f"{location}[{index}]")


def _canonical_contract_row(payload: object, *, index: int) -> bytes:
    if not isinstance(payload, bytes):
        raise FormatError(f"contract row {index} is not exact bytes")
    if not payload:
        raise FormatError(f"contract row {index} is empty")
    try:
        text = payload.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_pairs,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FormatError(f"contract row {index} is not strict UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise FormatError(f"contract row {index} is not a JSON object")
    _require_nfc_json(value)
    if canonical_json_bytes(value) != payload:
        raise FormatError(f"contract row {index} is not canonical JSON bytes")
    return payload


def _contract_row_value(payload: bytes, *, index: int) -> dict[str, object]:
    _canonical_contract_row(payload, index=index)
    value = json.loads(payload)
    return cast(dict[str, object], value)


def _validate_parent_paths(parent_paths: Iterable[str]) -> tuple[str, ...]:
    materialised = tuple(parent_paths)
    for index, path in enumerate(materialised):
        if not isinstance(path, str):
            raise FormatError(f"parent path {index} is not a string")
        if unicodedata.normalize("NFC", path) != path:
            raise FormatError(f"parent path {index} is not NFC")
        if not _WYSCOUT_PARENT_PATH.fullmatch(path):
            raise FormatError(f"parent path {index} is not a safe repository-relative path")
        segments = path.split("/")
        if path.startswith("/") or any(segment in {"", ".", ".."} for segment in segments):
            raise FormatError(f"parent path {index} is not a safe repository-relative path")
    if materialised != tuple(sorted(set(materialised))):
        raise FormatError("parent paths must be sorted and unique")
    _require_uint64(len(materialised), label="parent count")
    return materialised


def _validate_primary_keys(
    primary_keys: Iterable[tuple[WyscoutPrimaryKeyValue, ...]], *, row_count: int
) -> tuple[tuple[WyscoutPrimaryKeyValue, ...], ...]:
    keys = tuple(primary_keys)
    if len(keys) != row_count:
        raise FormatError("primary-key count does not equal the table row count")
    expected_types: tuple[type[object], ...] | None = None
    for row_index, key in enumerate(keys):
        if not isinstance(key, tuple) or not key:
            raise FormatError(f"primary key {row_index} must be a non-empty tuple")
        key_types: list[type[object]] = []
        for value_index, value in enumerate(key):
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                raise FormatError(
                    f"primary key {row_index} value {value_index} has an unsupported type"
                )
            if isinstance(value, str) and unicodedata.normalize("NFC", value) != value:
                raise FormatError(f"primary key {row_index} value {value_index} is not NFC")
            key_types.append(type(value))
        current_types = tuple(key_types)
        if expected_types is None:
            expected_types = current_types
        elif current_types != expected_types:
            raise FormatError("primary-key value types differ between rows")
    if len(set(keys)) != len(keys):
        raise FormatError("primary keys must be unique")
    if keys != tuple(sorted(keys)):
        raise FormatError("rows must be in canonical primary-key order")
    return keys


def _parse_primary_key_field_path(value: object, *, index: int) -> tuple[str, ...]:
    if type(value) is not str:
        raise FormatError(f"primary-key field {index} is not an exact string")
    path = value.split(".")
    if not path or any(not segment for segment in path):
        raise FormatError(f"primary-key field {index} contains an empty path segment")
    if any(not _WYSCOUT_FIELD_NAME.fullmatch(segment) for segment in path):
        raise FormatError(f"primary-key field {index} contains a non-canonical name")
    return tuple(path)


def _descriptor_field_for_primary_key_path(
    fields: tuple[WyscoutArrowProjectionField, ...],
    path: tuple[str, ...],
) -> WyscoutArrowProjectionField:
    for path_index, segment in enumerate(path):
        matches = tuple(field for field in fields if field.name == segment)
        if len(matches) != 1:
            raise FormatError("primary-key field is not present in the projection descriptor")
        field = matches[0]
        if field.nullable:
            raise FormatError("primary-key field path contains a nullable field")
        if path_index < len(path) - 1:
            node = field.node
            if (
                type(node) is not WyscoutArrowStructNode
                or node.projection_kind is not WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT
            ):
                raise FormatError(
                    "primary-key field path may descend only through fixed object structs"
                )
            fields = node.children
            continue
        node = field.node
        if (
            type(node) is not WyscoutArrowScalarNode
            or node.projection_kind is not WyscoutLogicalArrowProjectionKind.IDENTITY
            or node.scalar_type
            not in {
                WyscoutArrowScalarType.INT8,
                WyscoutArrowScalarType.INT16,
                WyscoutArrowScalarType.INT32,
                WyscoutArrowScalarType.INT64,
                WyscoutArrowScalarType.UINT8,
                WyscoutArrowScalarType.UINT16,
                WyscoutArrowScalarType.UINT32,
                WyscoutArrowScalarType.UINT64,
                WyscoutArrowScalarType.UTF8,
                WyscoutArrowScalarType.TIMESTAMP_US_UTC,
            }
        ):
            raise FormatError("primary-key field must be a non-null exact str/int scalar")
        return field
    raise AssertionError("validated primary-key path unexpectedly had no segments")


def _arrow_field_for_primary_key_path(
    schema: pa.Schema,
    path: tuple[str, ...],
) -> pa.Field:
    fields: tuple[pa.Field, ...] = tuple(schema)
    for path_index, segment in enumerate(path):
        matches = tuple(field for field in fields if field.name == segment)
        if len(matches) != 1:
            raise FormatError("primary-key field is not present in the Arrow schema")
        field = matches[0]
        if field.nullable:
            raise FormatError("primary-key Arrow path contains a nullable field")
        if path_index < len(path) - 1:
            if not pa.types.is_struct(field.type):
                raise FormatError("primary-key Arrow path descends through a non-struct field")
            fields = tuple(field.type)
            continue
        if not (
            pa.types.is_integer(field.type)
            or pa.types.is_string(field.type)
            or pa.types.is_timestamp(field.type)
        ):
            raise FormatError("primary-key Arrow field is not an exact str/int scalar")
        return field
    raise AssertionError("validated primary-key path unexpectedly had no segments")


def _validate_primary_key_field_paths(
    primary_key_fields: object,
    *,
    projection_descriptor: WyscoutParquetProjectionDescriptor,
    schema: pa.Schema,
) -> tuple[tuple[str, ...], ...]:
    if type(primary_key_fields) is not tuple or not primary_key_fields:
        raise FormatError("primary-key fields must be a non-empty unique tuple")
    paths = tuple(
        _parse_primary_key_field_path(value, index=index)
        for index, value in enumerate(primary_key_fields)
    )
    if len(set(paths)) != len(paths):
        raise FormatError("primary-key fields must be a non-empty unique tuple")
    for path in paths:
        _descriptor_field_for_primary_key_path(projection_descriptor.fields, path)
        _arrow_field_for_primary_key_path(schema, path)
    return paths


def _projected_primary_key_value(
    projected_row: dict[str, JsonValue],
    path: tuple[str, ...],
) -> WyscoutPrimaryKeyValue:
    current: object = projected_row
    for segment in path:
        if type(current) is not dict or segment not in current:
            raise FormatError("projected row does not contain the exact primary-key path")
        current = current[segment]
    if type(current) not in {str, int}:
        raise FormatError("projected primary-key value is not an exact str/int scalar")
    return cast(WyscoutPrimaryKeyValue, current)


def _validate_projection_field(
    field: WyscoutArrowProjectionField,
    *,
    location: str,
    tuple_child_position: int | None,
) -> None:
    if type(field) is not WyscoutArrowProjectionField:
        raise FormatError(f"projection field {location!r} has an invalid runtime type")
    if type(field.name) is not str or not _WYSCOUT_FIELD_NAME.fullmatch(field.name):
        raise FormatError(f"projection field {location!r} has a non-canonical name")
    if type(field.nullable) is not bool:
        raise FormatError(f"projection field {location!r} has invalid nullability")
    if tuple_child_position is None:
        if field.logical_position is not None:
            raise FormatError(f"projection field {location!r} has a forbidden logical position")
    elif type(field.logical_position) is not int or field.logical_position != tuple_child_position:
        raise FormatError(
            f"tuple field {location!r} logical position is not exact zero-based order"
        )
    _validate_projection_node(field.node, location=location)


def _validate_projection_node(node: WyscoutArrowProjectionNode, *, location: str) -> None:
    if type(node) is WyscoutArrowScalarNode:
        if type(node.scalar_type) is not WyscoutArrowScalarType:
            raise FormatError(f"projection scalar {location!r} has an invalid scalar type")
        if type(node.projection_kind) is not WyscoutLogicalArrowProjectionKind or (
            node.projection_kind
            not in {
                WyscoutLogicalArrowProjectionKind.IDENTITY,
                WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8,
                WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8,
            }
        ):
            raise FormatError(f"projection scalar {location!r} has an invalid projection kind")
        if (
            node.projection_kind
            in {
                WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8,
                WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8,
            }
            and node.scalar_type is not WyscoutArrowScalarType.UTF8
        ):
            raise FormatError("canonical logical text projection requires exact Arrow UTF-8")
        if node.scalar_type is WyscoutArrowScalarType.DECIMAL128:
            if (
                type(node.decimal_precision) is not int
                or type(node.decimal_scale) is not int
                or not 1 <= node.decimal_precision <= 38
                or not -node.decimal_precision <= node.decimal_scale <= node.decimal_precision
            ):
                raise FormatError(f"projection decimal {location!r} has invalid precision/scale")
        elif node.decimal_precision is not None or node.decimal_scale is not None:
            raise FormatError(f"non-decimal projection scalar {location!r} has decimal state")
        return
    if type(node) is WyscoutArrowStructNode:
        if type(node.projection_kind) is not WyscoutLogicalArrowProjectionKind or (
            node.projection_kind
            not in {
                WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT,
                WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT,
                WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT,
            }
        ):
            raise FormatError(f"projection struct {location!r} has an invalid projection kind")
        if type(node.children) is not tuple or not node.children:
            raise FormatError(f"projection struct {location!r} requires a non-empty child tuple")
        if any(type(child) is not WyscoutArrowProjectionField for child in node.children):
            raise FormatError(f"projection struct {location!r} has an invalid child field")
        names = tuple(child.name for child in node.children)
        if len(set(names)) != len(names):
            raise FormatError(f"projection struct {location!r} has duplicate child names")
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT:
            _validate_exact_decimal128_with_exponent_node(node, location=location)
            return
        positional = (
            node.projection_kind is WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT
        )
        for index, child in enumerate(node.children):
            _validate_projection_field(
                child,
                location=f"{location}.{child.name}",
                tuple_child_position=index if positional else None,
            )
        return
    if type(node) is WyscoutArrowListNode:
        if (
            type(node.projection_kind) is not WyscoutLogicalArrowProjectionKind
            or node.projection_kind is not WyscoutLogicalArrowProjectionKind.HOMOGENEOUS_LIST
        ):
            raise FormatError(f"projection list {location!r} has an invalid projection kind")
        if type(node.list_kind) is not WyscoutArrowListKind:
            raise FormatError(f"projection list {location!r} has an invalid list kind")
        if type(node.item) is not WyscoutArrowProjectionField:
            raise FormatError(f"projection list {location!r} has an invalid item field")
        if node.list_kind is WyscoutArrowListKind.FIXED_SIZE_LIST:
            if type(node.fixed_size) is not int or node.fixed_size <= 0:
                raise FormatError(f"fixed-size projection list {location!r} has invalid size")
        elif node.fixed_size is not None:
            raise FormatError(f"variable projection list {location!r} has fixed-size state")
        _validate_projection_field(
            node.item,
            location=f"{location}[]",
            tuple_child_position=None,
        )
        return
    raise FormatError(f"projection node {location!r} has an invalid runtime type")


def _validate_exact_decimal128_with_exponent_node(
    node: WyscoutArrowStructNode,
    *,
    location: str,
) -> None:
    expected = (
        WyscoutArrowProjectionField(
            name="value",
            nullable=False,
            node=WyscoutArrowScalarNode(
                scalar_type=WyscoutArrowScalarType.DECIMAL128,
                projection_kind=WyscoutLogicalArrowProjectionKind.IDENTITY,
                decimal_precision=22,
                decimal_scale=18,
            ),
        ),
        WyscoutArrowProjectionField(
            name="exponent",
            nullable=False,
            node=WyscoutArrowScalarNode(
                scalar_type=WyscoutArrowScalarType.INT8,
                projection_kind=WyscoutLogicalArrowProjectionKind.IDENTITY,
            ),
        ),
        WyscoutArrowProjectionField(
            name="negative_zero",
            nullable=False,
            node=WyscoutArrowScalarNode(
                scalar_type=WyscoutArrowScalarType.BOOL,
                projection_kind=WyscoutLogicalArrowProjectionKind.IDENTITY,
            ),
        ),
    )
    if node.children != expected:
        raise FormatError(
            f"exact Decimal projection {location!r} requires its exact ordered children"
        )
    for child in node.children:
        _validate_projection_field(
            child,
            location=f"{location}.{child.name}",
            tuple_child_position=None,
        )


def _validate_projection_descriptor(
    descriptor: WyscoutParquetProjectionDescriptor,
) -> None:
    if type(descriptor) is not WyscoutParquetProjectionDescriptor:
        raise FormatError("W04 projection requires one exact projection descriptor")
    if type(descriptor.schema_role) is not str or not _WYSCOUT_SCHEMA_ROLE.fullmatch(
        descriptor.schema_role
    ):
        raise FormatError("projection schema role is not a canonical W04 identifier")
    if (
        type(descriptor.serializer_version) is not str
        or descriptor.serializer_version != WYSCOUT_PARQUET_SERIALIZER_VERSION
    ):
        raise FormatError("projection serializer version differs from the accepted version")
    if type(descriptor.fields) is not tuple or not descriptor.fields:
        raise FormatError("W04 projection descriptor requires a non-empty field tuple")
    if any(type(field) is not WyscoutArrowProjectionField for field in descriptor.fields):
        raise FormatError("W04 projection descriptor has an invalid field runtime type")
    names = tuple(field.name for field in descriptor.fields)
    if len(set(names)) != len(names):
        raise FormatError("W04 projection descriptor field names must be unique")
    for field in descriptor.fields:
        _validate_projection_field(
            field,
            location=field.name,
            tuple_child_position=None,
        )


_SCALAR_ARROW_TYPES: dict[WyscoutArrowScalarType, pa.DataType] = {
    WyscoutArrowScalarType.NULL: pa.null(),
    WyscoutArrowScalarType.BOOL: pa.bool_(),
    WyscoutArrowScalarType.INT8: pa.int8(),
    WyscoutArrowScalarType.INT16: pa.int16(),
    WyscoutArrowScalarType.INT32: pa.int32(),
    WyscoutArrowScalarType.INT64: pa.int64(),
    WyscoutArrowScalarType.UINT8: pa.uint8(),
    WyscoutArrowScalarType.UINT16: pa.uint16(),
    WyscoutArrowScalarType.UINT32: pa.uint32(),
    WyscoutArrowScalarType.UINT64: pa.uint64(),
    WyscoutArrowScalarType.FLOAT16: pa.float16(),
    WyscoutArrowScalarType.FLOAT32: pa.float32(),
    WyscoutArrowScalarType.FLOAT64: pa.float64(),
    WyscoutArrowScalarType.UTF8: pa.string(),
    WyscoutArrowScalarType.TIMESTAMP_US_UTC: pa.timestamp("us", tz="UTC"),
}


def _arrow_type_from_projection_node(node: WyscoutArrowProjectionNode) -> pa.DataType:
    if type(node) is WyscoutArrowScalarNode:
        if node.scalar_type is WyscoutArrowScalarType.DECIMAL128:
            if node.decimal_precision is None or node.decimal_scale is None:
                raise AssertionError("validated Decimal projection lost precision or scale")
            return pa.decimal128(node.decimal_precision, node.decimal_scale)
        return _SCALAR_ARROW_TYPES[node.scalar_type]
    if type(node) is WyscoutArrowStructNode:
        return pa.struct([_arrow_field_from_projection(child) for child in node.children])
    if type(node) is WyscoutArrowListNode:
        item = _arrow_field_from_projection(node.item)
        if node.list_kind is WyscoutArrowListKind.LIST:
            return pa.list_(item)
        if node.list_kind is WyscoutArrowListKind.LARGE_LIST:
            return pa.large_list(item)
        if node.fixed_size is None:
            raise AssertionError("validated fixed-size list projection lost its size")
        return pa.list_(item, node.fixed_size)
    raise AssertionError("validated projection node has an impossible runtime type")


def _arrow_field_from_projection(field: WyscoutArrowProjectionField) -> pa.Field:
    return pa.field(
        field.name,
        _arrow_type_from_projection_node(field.node),
        nullable=field.nullable,
    )


def arrow_schema_from_w04_projection(
    descriptor: WyscoutParquetProjectionDescriptor,
) -> pa.Schema:
    """Generate the exact Arrow schema solely from accepted descriptor content."""

    _validate_projection_descriptor(descriptor)
    schema = pa.schema([_arrow_field_from_projection(field) for field in descriptor.fields])
    _validate_wyscout_schema(schema, schema_role=descriptor.schema_role)
    return schema


def _validate_wyscout_schema(
    schema: pa.Schema, *, schema_role: str
) -> WyscoutParquetSchemaDescriptor:
    if not isinstance(schema, pa.Schema):
        raise FormatError("W04 Parquet output requires one explicit Arrow schema")
    if not _WYSCOUT_SCHEMA_ROLE.fullmatch(schema_role):
        raise FormatError("schema role is not a canonical W04 identifier")
    if len(schema) == 0:
        raise FormatError("W04 Parquet output requires at least one schema field")
    if len(set(schema.names)) != len(schema.names):
        raise FormatError("W04 Parquet schema field names must be unique")
    if schema.metadata is not None:
        raise FormatError("W04 Parquet schema metadata is not permitted")

    fields: list[WyscoutParquetSchemaField] = []
    for field in schema:
        if not _WYSCOUT_FIELD_NAME.fullmatch(field.name):
            raise FormatError(f"schema field {field.name!r} is not a canonical identifier")
        if field.metadata is not None:
            raise FormatError(f"schema field {field.name!r} metadata is not permitted")
        arrow_type = str(field.type)
        if unicodedata.normalize("NFC", arrow_type) != arrow_type:
            raise FormatError(f"schema field {field.name!r} has a non-NFC Arrow type")
        _validate_supported_arrow_type(field.type, location=field.name)
        fields.append(
            WyscoutParquetSchemaField(
                name=field.name,
                arrow_type=arrow_type,
                nullable=field.nullable,
            )
        )
    return WyscoutParquetSchemaDescriptor(
        schema_role=schema_role,
        serializer_version=WYSCOUT_PARQUET_SERIALIZER_VERSION,
        fields=tuple(fields),
    )


def _validate_supported_arrow_type(data_type: pa.DataType, *, location: str) -> None:
    if (
        pa.types.is_null(data_type)
        or pa.types.is_boolean(data_type)
        or pa.types.is_integer(data_type)
        or pa.types.is_floating(data_type)
        or pa.types.is_string(data_type)
        or pa.types.is_decimal(data_type)
    ):
        return
    if pa.types.is_timestamp(data_type):
        if data_type.unit != "us" or data_type.tz != "UTC":
            raise FormatError("W04 timestamp fields must be timestamp[us, tz=UTC]")
        return
    if pa.types.is_struct(data_type):
        names = tuple(field.name for field in data_type)
        if len(set(names)) != len(names):
            raise FormatError(f"Arrow struct {location!r} has duplicate field names")
        for field in data_type:
            if not _WYSCOUT_FIELD_NAME.fullmatch(field.name):
                raise FormatError(f"Arrow struct field {location}.{field.name} is not canonical")
            if field.metadata is not None:
                raise FormatError(f"Arrow struct field {location}.{field.name} has metadata")
            _validate_supported_arrow_type(
                field.type,
                location=f"{location}.{field.name}",
            )
        return
    if (
        pa.types.is_list(data_type)
        or pa.types.is_large_list(data_type)
        or pa.types.is_fixed_size_list(data_type)
    ):
        value_field = data_type.value_field
        if not _WYSCOUT_FIELD_NAME.fullmatch(value_field.name):
            raise FormatError(f"Arrow list value field {location}[] is not canonical")
        if value_field.metadata is not None:
            raise FormatError(f"Arrow list value field {location}[] has metadata")
        if type(value_field.nullable) is not bool:
            raise FormatError(f"Arrow list value field {location}[] has invalid nullability")
        _validate_supported_arrow_type(value_field.type, location=f"{location}[]")
        return
    raise FormatError(f"Arrow field {location!r} has unsupported type {data_type}")


_CANONICAL_JSON_VALUE_ADAPTER: TypeAdapter[CanonicalJsonValue] = TypeAdapter(CanonicalJsonValue)


def _raw_pydantic_model_state(
    value: object,
    *,
    expected_fields: frozenset[str],
    location: str,
) -> dict[str, object]:
    try:
        state = object.__getattribute__(value, "__dict__")
        extra = object.__getattribute__(value, "__pydantic_extra__")
        fields_set = object.__getattribute__(value, "__pydantic_fields_set__")
    except AttributeError as error:
        raise FormatError(f"{location} is not an exact canonical JSON model") from error
    if type(state) is not dict or frozenset(state) != expected_fields:
        raise FormatError(f"{location} has non-exact canonical JSON model fields")
    if extra is not None:
        raise FormatError(f"{location} has forbidden extra canonical JSON model state")
    if type(fields_set) is not set or not fields_set <= expected_fields:
        raise FormatError(f"{location} has forbidden canonical JSON field-set state")
    return cast(dict[str, object], state)


def _require_raw_canonical_text(value: object, *, location: str) -> str:
    if type(value) is not str:
        raise FormatError(f"{location} is not exact canonical JSON text")
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise FormatError(f"{location} contains a Unicode surrogate")
    if unicodedata.normalize("NFC", value) != value:
        raise FormatError(f"{location} contains non-NFC text")
    return value


def _raw_canonical_json_member_state(
    value: object,
    *,
    location: str,
) -> dict[str, object]:
    if type(value) is not CanonicalJsonMember:
        raise FormatError(f"{location} is not an exact CanonicalJsonMember")
    state = _raw_pydantic_model_state(
        value,
        expected_fields=frozenset({"key", "value"}),
        location=location,
    )
    key = _require_raw_canonical_text(state["key"], location=f"{location}.key")
    return {
        "key": key,
        "value": _raw_canonical_json_value_state(
            state["value"],
            location=f"{location}.value",
        ),
    }


def _raw_canonical_json_value_state(
    value: object,
    *,
    location: str,
) -> dict[str, object]:
    model_type = type(value)
    if model_type not in {
        CanonicalJsonNull,
        CanonicalJsonBoolean,
        CanonicalJsonInteger,
        CanonicalJsonNumber,
        CanonicalJsonString,
        CanonicalJsonArray,
        CanonicalJsonObject,
    }:
        raise FormatError(f"{location} is not an exact CanonicalJsonValue model")
    state = _raw_pydantic_model_state(
        value,
        expected_fields=frozenset({"kind", "value"}),
        location=location,
    )
    kind = state["kind"]
    raw_value = state["value"]
    expected_kind: CanonicalJsonKind
    recovered_value: object
    if model_type is CanonicalJsonNull:
        expected_kind = CanonicalJsonKind.NULL
        if raw_value is not None:
            raise FormatError(f"{location}.value is not exact canonical JSON null")
        recovered_value = None
    elif model_type is CanonicalJsonBoolean:
        expected_kind = CanonicalJsonKind.BOOLEAN
        if type(raw_value) is not bool:
            raise FormatError(f"{location}.value is not an exact Boolean")
        recovered_value = raw_value
    elif model_type is CanonicalJsonInteger:
        expected_kind = CanonicalJsonKind.INTEGER
        if type(raw_value) is not int:
            raise FormatError(f"{location}.value is not an exact integer")
        recovered_value = raw_value
    elif model_type is CanonicalJsonNumber:
        expected_kind = CanonicalJsonKind.NUMBER
        if type(raw_value) is not Decimal or not raw_value.is_finite():
            raise FormatError(f"{location}.value is not an exact finite Decimal")
        recovered_value = raw_value
    elif model_type is CanonicalJsonString:
        expected_kind = CanonicalJsonKind.STRING
        recovered_value = _require_raw_canonical_text(
            raw_value,
            location=f"{location}.value",
        )
    elif model_type is CanonicalJsonArray:
        expected_kind = CanonicalJsonKind.ARRAY
        if type(raw_value) is not tuple:
            raise FormatError(f"{location}.value is not an exact tuple")
        recovered_value = tuple(
            _raw_canonical_json_value_state(item, location=f"{location}.value[{index}]")
            for index, item in enumerate(raw_value)
        )
    else:
        expected_kind = CanonicalJsonKind.OBJECT
        if type(raw_value) is not tuple:
            raise FormatError(f"{location}.value is not an exact member tuple")
        recovered_value = tuple(
            _raw_canonical_json_member_state(member, location=f"{location}.value[{index}]")
            for index, member in enumerate(raw_value)
        )
    if type(kind) is not CanonicalJsonKind or kind is not expected_kind:
        raise FormatError(f"{location}.kind is not the exact model discriminator")
    return {"kind": kind, "value": recovered_value}


def canonical_json_value_to_w04_arrow_utf8(value: object) -> str:
    """Return one exact canonical tagged logical JSON UTF-8 scalar without an LF."""

    raw_state = _raw_canonical_json_value_state(value, location="$")
    try:
        typed = _CANONICAL_JSON_VALUE_ADAPTER.validate_python(raw_state, strict=True)
    except ValidationError as error:
        raise FormatError("value is not an exact CanonicalJsonValue") from error
    if type(typed) is not type(value):
        raise FormatError("fresh CanonicalJsonValue validation changed the exact model arm")
    payload = canonical_json_bytes(typed.model_dump(mode="json"))
    if not payload.endswith(b"\n") or payload[:-1].endswith(b"\n"):
        raise AssertionError("canonical tagged JSON framing drifted")
    try:
        return payload[:-1].decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise FormatError("canonical tagged JSON is not strict UTF-8") from error


def canonical_decimal_to_w04_arrow_utf8(value: object) -> str:
    """Return exact canonical finite Decimal text without rounding or an LF."""

    if type(value) is not Decimal or not value.is_finite():
        raise FormatError("value is not an exact finite Decimal")
    if value.is_zero():
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    if not rendered or "e" in rendered.lower() or rendered.endswith("\n"):
        raise AssertionError("canonical Decimal rendering drifted")
    return rendered


def _require_decimal128_22_18_capacity(
    value: object,
    *,
    declared_scale: int | None,
    location: str,
) -> tuple[Decimal, int]:
    if type(value) is not Decimal or not value.is_finite():
        raise FormatError(f"{location} is not an exact finite Decimal")
    exponent = cast(int, value.as_tuple().exponent)
    source_scale = max(0, -exponent)
    coefficient_digits = len(value.as_tuple().digits)
    integer_digits = max(0, coefficient_digits + exponent)
    if source_scale > 18 or integer_digits > 4 or integer_digits + source_scale > 22:
        raise FormatError(f"{location} exceeds exact decimal128(22,18) lexical scale or capacity")
    if declared_scale is not None and (
        type(declared_scale) is not int or declared_scale != source_scale
    ):
        raise FormatError(f"{location} declared scale does not equal its exact source scale")
    return value, exponent


def exact_decimal128_with_exponent_to_w04_arrow(
    value: object,
    *,
    declared_scale: int | None = None,
) -> dict[str, Decimal | int | bool]:
    """Project one exact Decimal into the reversible decimal128(22,18) struct."""

    decimal_value, exponent = _require_decimal128_22_18_capacity(
        value,
        declared_scale=declared_scale,
        location="value",
    )
    try:
        with localcontext() as context:
            context.prec = 22
            context.traps[Inexact] = True
            physical_value = decimal_value.quantize(Decimal("1E-18"), context=context)
    except DecimalException as error:
        raise FormatError("value cannot be represented at scale 18 without rounding") from error
    if physical_value != decimal_value:
        raise FormatError("value cannot be represented at scale 18 without rounding")
    return {
        "value": physical_value,
        "exponent": exponent,
        "negative_zero": decimal_value.is_zero() and decimal_value.is_signed(),
    }


def _decode_exact_decimal128_with_exponent(
    scalar: pa.Scalar,
    *,
    location: str,
) -> str:
    expected_type = pa.struct(
        [
            pa.field("value", pa.decimal128(22, 18), nullable=False),
            pa.field("exponent", pa.int8(), nullable=False),
            pa.field("negative_zero", pa.bool_(), nullable=False),
        ]
    )
    if not pa.types.is_struct(scalar.type) or not scalar.type.equals(expected_type):
        raise FormatError(f"Arrow exact Decimal field {location!r} has an invalid struct type")
    children = tuple(scalar[index] for index in range(3))
    if any(not child.is_valid for child in children):
        raise FormatError(f"Arrow exact Decimal field {location!r} contains a null child")
    physical_value = children[0].as_py()
    exponent = children[1].as_py()
    negative_zero = children[2].as_py()
    if type(physical_value) is not Decimal or not physical_value.is_finite():
        raise FormatError(f"Arrow exact Decimal field {location!r} has an invalid value child")
    if type(exponent) is not int:
        raise FormatError(f"Arrow exact Decimal field {location!r} has an invalid exponent child")
    if type(negative_zero) is not bool:
        raise FormatError(f"Arrow exact Decimal field {location!r} has an invalid sign child")
    if negative_zero and not physical_value.is_zero():
        raise FormatError(
            f"Arrow exact Decimal field {location!r} marks a nonzero as negative zero"
        )
    quantum = Decimal((0, (1,), exponent))
    try:
        with localcontext() as context:
            context.prec = 22
            context.traps[Inexact] = True
            restored = physical_value.quantize(quantum, context=context)
    except DecimalException as error:
        raise FormatError(
            f"Arrow exact Decimal field {location!r} requires rounding at its exponent"
        ) from error
    if restored != physical_value:
        raise FormatError(
            f"Arrow exact Decimal field {location!r} requires rounding at its exponent"
        )
    if restored.is_zero():
        restored = restored.copy_abs()
        if negative_zero:
            restored = restored.copy_negate()
    _require_decimal128_22_18_capacity(
        restored,
        declared_scale=max(0, -exponent),
        location=f"Arrow exact Decimal field {location!r}",
    )
    return str(restored)


def _decode_canonical_decimal_utf8(value: object, *, location: str) -> str:
    if type(value) is not str:
        raise FormatError(f"Arrow canonical Decimal field {location!r} is not exact UTF-8 text")
    try:
        raw = value.encode("utf-8", errors="strict")
        decoded = raw.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise FormatError(
            f"Arrow canonical Decimal field {location!r} is not strict UTF-8"
        ) from error
    if decoded != value:
        raise FormatError(
            f"Arrow canonical Decimal field {location!r} has a UTF-8 round-trip drift"
        )
    try:
        parsed = Decimal(decoded)
    except InvalidOperation as error:
        raise FormatError(
            f"Arrow canonical Decimal field {location!r} is not a Decimal token"
        ) from error
    if not parsed.is_finite():
        raise FormatError(f"Arrow canonical Decimal field {location!r} is not finite")
    canonical = canonical_decimal_to_w04_arrow_utf8(parsed)
    if canonical.encode("utf-8") != raw:
        raise FormatError(f"Arrow canonical Decimal field {location!r} is not canonical bytes")
    return canonical


def _decode_canonical_json_value_utf8(value: object, *, location: str) -> JsonValue:
    if type(value) is not str:
        raise FormatError(f"Arrow tagged JSON field {location!r} is not exact UTF-8 text")
    try:
        raw = value.encode("utf-8", errors="strict")
        decoded = raw.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise FormatError(f"Arrow tagged JSON field {location!r} is not strict UTF-8") from error
    if decoded != value:
        raise FormatError(f"Arrow tagged JSON field {location!r} has a UTF-8 round-trip drift")
    try:
        parsed = json.loads(
            decoded,
            object_pairs_hook=_reject_duplicate_json_pairs,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, FormatError) as error:
        raise FormatError(f"Arrow tagged JSON field {location!r} is not strict JSON") from error
    _require_nfc_json(parsed)
    try:
        typed = _CANONICAL_JSON_VALUE_ADAPTER.validate_json(raw, strict=True)
    except ValidationError as error:
        raise FormatError(
            f"Arrow tagged JSON field {location!r} is not an exact CanonicalJsonValue"
        ) from error
    reencoded = canonical_json_value_to_w04_arrow_utf8(typed).encode("utf-8", errors="strict")
    if reencoded != raw:
        raise FormatError(f"Arrow tagged JSON field {location!r} is not canonical bytes")
    return cast(JsonValue, typed.model_dump(mode="json"))


def _project_identity_arrow_scalar(
    scalar: pa.Scalar,
    data_type: pa.DataType,
    *,
    location: str,
) -> JsonValue:
    value = scalar.as_py()
    if pa.types.is_null(data_type):
        raise FormatError(f"Arrow null field {location!r} contains a non-null value")
    if pa.types.is_boolean(data_type):
        if type(value) is not bool:
            raise FormatError(f"Arrow Boolean field {location!r} has an invalid value")
        return value
    if pa.types.is_integer(data_type):
        if type(value) is not int:
            raise FormatError(f"Arrow integer field {location!r} has an invalid value")
        return value
    if pa.types.is_floating(data_type):
        if type(value) is not float or not math.isfinite(value):
            raise FormatError(f"Arrow float field {location!r} must be finite")
        return value
    if pa.types.is_string(data_type):
        if type(value) is not str:
            raise FormatError(f"Arrow string field {location!r} has an invalid value")
        if unicodedata.normalize("NFC", value) != value:
            raise FormatError(f"Arrow string field {location!r} is not NFC")
        return value
    if pa.types.is_decimal(data_type):
        if type(value) is not Decimal or not value.is_finite():
            raise FormatError(f"Arrow decimal field {location!r} has an invalid value")
        return format(value, "f")
    if pa.types.is_timestamp(data_type):
        if type(value) is not datetime or value.tzinfo is None:
            raise FormatError(f"Arrow timestamp field {location!r} is naive")
        if value.utcoffset() != timedelta(0):
            raise FormatError(f"Arrow timestamp field {location!r} is not UTC")
        rendered = value.strftime("%Y-%m-%dT%H:%M:%S")
        if value.microsecond:
            rendered += f".{value.microsecond:06d}"
        return rendered + "Z"
    raise FormatError(f"Arrow field {location!r} has unsupported type {data_type}")


def _project_arrow_value(
    scalar: pa.Scalar,
    field: WyscoutArrowProjectionField,
    *,
    location: str,
) -> JsonValue:
    if not scalar.is_valid:
        if not field.nullable:
            raise FormatError(f"Arrow field {location!r} contains a forbidden null")
        return None
    node = field.node
    data_type = scalar.type
    if type(node) is WyscoutArrowScalarNode:
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8:
            if not pa.types.is_string(data_type):
                raise FormatError(f"Arrow tagged JSON field {location!r} is not UTF-8")
            try:
                value = scalar.as_py()
            except UnicodeDecodeError as error:
                raise FormatError(
                    f"Arrow tagged JSON field {location!r} is not strict UTF-8"
                ) from error
            return _decode_canonical_json_value_utf8(value, location=location)
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8:
            if not pa.types.is_string(data_type):
                raise FormatError(f"Arrow canonical Decimal field {location!r} is not UTF-8")
            try:
                value = scalar.as_py()
            except UnicodeDecodeError as error:
                raise FormatError(
                    f"Arrow canonical Decimal field {location!r} is not strict UTF-8"
                ) from error
            return _decode_canonical_decimal_utf8(value, location=location)
        return _project_identity_arrow_scalar(scalar, data_type, location=location)
    if type(node) is WyscoutArrowStructNode:
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT:
            return _decode_exact_decimal128_with_exponent(scalar, location=location)
        if not pa.types.is_struct(data_type):
            raise FormatError(f"Arrow struct field {location!r} has an invalid physical type")
        values = [
            _project_arrow_value(
                scalar[index],
                child,
                location=f"{location}.{child.name}",
            )
            for index, child in enumerate(node.children)
        ]
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT:
            return values
        return {child.name: value for child, value in zip(node.children, values, strict=True)}
    if type(node) is WyscoutArrowListNode:
        if not (
            pa.types.is_list(data_type)
            or pa.types.is_large_list(data_type)
            or pa.types.is_fixed_size_list(data_type)
        ):
            raise FormatError(f"Arrow list field {location!r} has an invalid physical type")
        values = scalar.values
        if node.fixed_size is not None and len(values) != node.fixed_size:
            raise FormatError(f"Arrow fixed-size list field {location!r} has wrong cardinality")
        return [
            _project_arrow_value(
                values[index],
                node.item,
                location=f"{location}[{index}]",
            )
            for index in range(len(values))
        ]
    raise AssertionError("validated projection node has an impossible runtime type")


def _project_arrow_row(
    table: pa.Table,
    descriptor: WyscoutParquetProjectionDescriptor,
    *,
    row_index: int,
) -> dict[str, JsonValue]:
    return {
        field.name: _project_arrow_value(
            table.column(column_index)[row_index],
            field,
            location=field.name,
        )
        for column_index, field in enumerate(descriptor.fields)
    }


def _schema_descriptor_bytes(descriptor: WyscoutParquetSchemaDescriptor) -> bytes:
    return canonical_json_bytes(
        {
            "schema_role": descriptor.schema_role,
            "serializer_version": descriptor.serializer_version,
            "fields": [
                {
                    "name": field.name,
                    "arrow_type": field.arrow_type,
                    "nullable": field.nullable,
                }
                for field in descriptor.fields
            ],
        }
    )


def w04_wyscout_parquet_semantic_sha256(
    *,
    projection_descriptor: WyscoutParquetProjectionDescriptor,
    contract_row_bytes: Iterable[bytes],
    parent_paths: Iterable[str],
) -> str:
    """Hash exact ordered W04 contract rows and parents under the R20 domain."""

    schema = arrow_schema_from_w04_projection(projection_descriptor)
    schema_descriptor = _validate_wyscout_schema(
        schema,
        schema_role=projection_descriptor.schema_role,
    )
    schema_bytes = _schema_descriptor_bytes(schema_descriptor)
    rows = tuple(
        _canonical_contract_row(payload, index=index)
        for index, payload in enumerate(contract_row_bytes)
    )
    if not rows:
        raise FormatError("semantic hashing requires at least one contract row")
    if len(set(rows)) != len(rows):
        raise FormatError("contract row bytes must be unique")
    parents = _validate_parent_paths(parent_paths)
    row_count = _require_uint64(len(rows), label="row count")
    parent_count = _require_uint64(len(parents), label="parent count")

    digest = hashlib.sha256()
    digest.update(WYSCOUT_PARQUET_SEMANTIC_VERSION.encode("utf-8"))
    digest.update(b"\x00S")
    digest.update(_frame_uint64(schema_bytes, label="schema descriptor"))
    digest.update(b"R")
    digest.update(row_count)
    for index, row in enumerate(rows):
        digest.update(_frame_uint64(row, label=f"contract row {index}"))
    digest.update(b"P")
    digest.update(parent_count)
    for index, path in enumerate(parents):
        digest.update(_frame_uint64(path.encode("utf-8"), label=f"parent path {index}"))
    return digest.hexdigest()


def encode_w04_wyscout_product_parquet(
    table: pa.Table,
    *,
    projection_descriptor: WyscoutParquetProjectionDescriptor,
    primary_key_fields: tuple[str, ...],
    primary_keys: Iterable[tuple[WyscoutPrimaryKeyValue, ...]],
    contract_row_bytes: Iterable[bytes],
    parent_paths: Iterable[str],
) -> WyscoutParquetEncoding:
    """Encode one non-empty explicit-schema W04 product table without coercion."""

    schema = arrow_schema_from_w04_projection(projection_descriptor)
    if not isinstance(table, pa.Table):
        raise FormatError("W04 Parquet encoding requires an explicit Arrow table")
    descriptor = _validate_wyscout_schema(
        schema,
        schema_role=projection_descriptor.schema_role,
    )
    _validate_wyscout_schema(
        table.schema,
        schema_role=projection_descriptor.schema_role,
    )
    if not table.schema.equals(schema, check_metadata=True):
        raise FormatError("Arrow table schema does not exactly equal the explicit schema")
    if table.num_rows == 0:
        raise FormatError("W04 Parquet output requires at least one row")
    _require_uint64(table.num_rows, label="row count")
    for field, column in zip(schema, table.columns, strict=True):
        if not field.nullable and column.null_count:
            raise FormatError(f"non-nullable schema field {field.name!r} contains nulls")

    rows = tuple(contract_row_bytes)
    if len(rows) != table.num_rows:
        raise FormatError("contract-row count does not equal the table row count")
    canonical_rows = tuple(
        _contract_row_value(payload, index=index) for index, payload in enumerate(rows)
    )
    if len(set(rows)) != len(rows):
        raise FormatError("contract row bytes must be unique")
    parents = _validate_parent_paths(parent_paths)
    primary_key_paths = _validate_primary_key_field_paths(
        primary_key_fields,
        projection_descriptor=projection_descriptor,
        schema=schema,
    )
    keys = _validate_primary_keys(primary_keys, row_count=table.num_rows)
    if any(len(key) != len(primary_key_paths) for key in keys):
        raise FormatError("primary-key tuple arity does not equal primary-key fields")

    canonical_table = table.combine_chunks()
    expected_field_names = set(schema.names)
    for index, (payload, contract_row, key) in enumerate(
        zip(rows, canonical_rows, keys, strict=True)
    ):
        if set(contract_row) != expected_field_names:
            raise FormatError(f"contract row {index} fields do not exactly equal the Arrow schema")
        projected_row = _project_arrow_row(
            canonical_table,
            projection_descriptor,
            row_index=index,
        )
        if canonical_json_bytes(projected_row) != payload:
            raise FormatError(f"Arrow row {index} does not exactly equal its contract row")
        projected_key = tuple(
            _projected_primary_key_value(projected_row, path) for path in primary_key_paths
        )
        for key_index, (projected_value, supplied_value) in enumerate(
            zip(projected_key, key, strict=True)
        ):
            if (
                type(projected_value) is not type(supplied_value)
                or projected_value != supplied_value
            ):
                raise FormatError(
                    f"Arrow row {index} primary-key value {key_index} does not exactly equal "
                    "the supplied key"
                )

    descriptor_bytes = _schema_descriptor_bytes(descriptor)
    semantic_sha256 = w04_wyscout_parquet_semantic_sha256(
        projection_descriptor=projection_descriptor,
        contract_row_bytes=rows,
        parent_paths=parents,
    )

    sink = pa.BufferOutputStream()
    pq.write_table(
        canonical_table,
        sink,
        version="2.6",
        row_group_size=65536,
        compression="zstd",
        compression_level=9,
        data_page_version="2.0",
        use_dictionary=False,
        use_byte_stream_split=False,
        write_statistics=True,
        write_page_index=False,
        coerce_timestamps="us",
        allow_truncated_timestamps=False,
        store_schema=True,
    )
    payload = cast(bytes, sink.getvalue().to_pybytes())
    return WyscoutParquetEncoding(
        payload=payload,
        physical_sha256=hashlib.sha256(payload).hexdigest(),
        size_bytes=len(payload),
        semantic_sha256=semantic_sha256,
        row_count=table.num_rows,
        schema_descriptor=descriptor,
        schema_descriptor_bytes=descriptor_bytes,
        parent_paths=parents,
    )


def read_parquet_bytes(payload: bytes) -> list[dict[str, object]]:
    """Read Parquet bytes for deterministic local verification."""

    table = pq.read_table(pa.BufferReader(payload))
    return [dict(row) for row in table.to_pylist()]

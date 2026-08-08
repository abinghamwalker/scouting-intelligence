"""Exact local W04 Wyscout product composition primitives."""

from __future__ import annotations

import hashlib
import os
import stat
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import cast
from uuid import UUID

import pyarrow as pa  # type: ignore[import-untyped]
from pydantic import BaseModel

from scouting.contracts.evidence import DependencyLineage, EvidenceDependency
from scouting.contracts.primitives import TenantContext
from scouting.contracts.wyscout_build import (
    accepted_dependency_lineage_hash,
    accepted_dependency_rows,
)
from scouting.contracts.wyscout_data import (
    SOURCE_COMPLETION_INDEX_SHA256,
    SOURCE_MANIFEST_ID,
    SOURCE_MANIFEST_SHA256,
    TENANT_ID,
    WyscoutRowLineage,
    accepted_authority_clocks,
    accepted_authority_references,
    accepted_source_authority,
)
from scouting.contracts.wyscout_schema import (
    w04_parquet_projection_content,
    w04_physical_primary_key_paths,
)
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.formats import (
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
)
from scouting.storage.wyscout_publication import (
    WyscoutPublicationRoot,
    WyscoutStagedPublisher,
)


@dataclass(frozen=True, slots=True)
class WyscoutProductRoots:
    """Exact final/staging roots for one isolated or repository-local rebuild."""

    working_final_root: Path
    working_staging_root: Path
    manifest_final_root: Path
    manifest_staging_root: Path
    runs_final_root: Path
    runs_staging_root: Path


@dataclass(frozen=True, slots=True)
class PublishedProduct:
    """One immutably published product and its exact accepted encoding metadata."""

    relative_path: str
    encoding: WyscoutParquetEncoding


def staged_publisher(roots: WyscoutProductRoots) -> WyscoutStagedPublisher:
    """Bind only the three accepted exact output roots."""

    return WyscoutStagedPublisher(
        {
            "wyscout-working": WyscoutPublicationRoot(
                roots.working_final_root,
                roots.working_staging_root,
            ),
            "wyscout-manifests": WyscoutPublicationRoot(
                roots.manifest_final_root,
                roots.manifest_staging_root,
            ),
            "w04-rebuild-runs": WyscoutPublicationRoot(
                roots.runs_final_root,
                roots.runs_staging_root,
            ),
        }
    )


def guarded_read(path: Path) -> bytes:
    """Read one immutable publisher output without following a terminal link."""

    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_nlink != 1
        ):
            raise ValueError("published readback must be one regular 0600 file")
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(descriptor)
        if (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_nlink,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_nlink,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("published readback changed during guarded read")
        payload = b"".join(chunks)
        if len(payload) != before.st_size:
            raise ValueError("published readback size drifted")
        return payload
    finally:
        os.close(descriptor)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def tenant_context() -> TenantContext:
    """Return the sole accepted no-club tenant."""

    return TenantContext(tenant_id=TENANT_ID)


def dependency_lineage() -> DependencyLineage:
    """Project the accepted build dependency rows into the data contract."""

    rows = tuple(
        EvidenceDependency.model_validate_json(row.model_dump_json(), strict=True)
        for row in accepted_dependency_rows()
    )
    return DependencyLineage(
        lineage_hash=accepted_dependency_lineage_hash(),
        dependencies=rows,
    )


def complete_match_lineage(context: VerifiedMatchContext) -> WyscoutRowLineage:
    """Build the exact complete selected-match lineage shared by checked products."""

    action_rows = tuple(action.evidence for action in context.event_population.actions)
    projected_rows = tuple(
        sequence_action.source_row
        for sequence in context.event_population.completion.sequences
        for sequence_action in sequence.actions
    )
    if len(action_rows) != 1_768 or len(projected_rows) != 1_768:
        raise ValueError("complete selected-match lineage must contain 1,768 actions")
    rows = tuple(
        sorted(
            (*projected_rows, context.match_source_row),
            key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
        )
    )
    return WyscoutRowLineage(
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        source_rows=rows,
        authority_references=accepted_authority_references(),
        authority_clocks=accepted_authority_clocks(),
        source_authority=accepted_source_authority(),
        dependency_lineage=dependency_lineage(),
    )


def _projection_node(value: Mapping[str, object]) -> object:
    kind = value["node_kind"]
    projection_kind = WyscoutLogicalArrowProjectionKind(cast(str, value["projection_kind"]))
    if kind == "SCALAR":
        return WyscoutArrowScalarNode(
            scalar_type=WyscoutArrowScalarType(cast(str, value["scalar_type"])),
            projection_kind=projection_kind,
            decimal_precision=cast(int | None, value["decimal_precision"]),
            decimal_scale=cast(int | None, value["decimal_scale"]),
        )
    if kind == "STRUCT":
        return WyscoutArrowStructNode(
            projection_kind=projection_kind,
            children=tuple(
                _projection_field(cast(Mapping[str, object], item))
                for item in cast(list[object], value["children"])
            ),
        )
    if kind == "LIST":
        return WyscoutArrowListNode(
            projection_kind=projection_kind,
            list_kind=WyscoutArrowListKind(cast(str, value["list_kind"])),
            item=_projection_field(cast(Mapping[str, object], value["item"])),
            fixed_size=cast(int | None, value["fixed_size"]),
        )
    raise ValueError("accepted projection node kind drifted")


def _projection_field(value: Mapping[str, object]) -> WyscoutArrowProjectionField:
    return WyscoutArrowProjectionField(
        name=cast(str, value["name"]),
        nullable=cast(bool, value["nullable"]),
        node=cast(
            WyscoutArrowScalarNode | WyscoutArrowStructNode | WyscoutArrowListNode,
            _projection_node(cast(Mapping[str, object], value["node"])),
        ),
        logical_position=cast(int | None, value["logical_position"]),
    )


def projection_descriptor(root_role: str) -> WyscoutParquetProjectionDescriptor:
    """Mechanically instantiate one accepted root-owned projection descriptor."""

    content = w04_parquet_projection_content(root_role)
    raw = cast(Mapping[str, object], content["descriptor"])
    return WyscoutParquetProjectionDescriptor(
        schema_role=cast(str, raw["schema_role"]),
        serializer_version=cast(str, raw["serializer_version"]),
        fields=tuple(
            _projection_field(cast(Mapping[str, object], item))
            for item in cast(list[object], raw["fields"])
        ),
    )


def _model_member(value: object, name: str) -> object:
    if isinstance(value, BaseModel):
        return getattr(value, name)
    if isinstance(value, Mapping):
        return value[name]
    raise TypeError(f"projection object has no member {name!r}")


def _physical_value(value: object, field: WyscoutArrowProjectionField) -> object:
    if value is None:
        return None
    node = field.node
    if isinstance(node, WyscoutArrowScalarNode):
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8:
            return canonical_json_value_to_w04_arrow_utf8(value)
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8:
            return canonical_decimal_to_w04_arrow_utf8(value)
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="strict")
        return value
    if isinstance(node, WyscoutArrowStructNode):
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT:
            return exact_decimal128_with_exponent_to_w04_arrow(value)
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT:
            sequence = cast(Sequence[object], value)
            return {
                child.name: _physical_value(sequence[index], child)
                for index, child in enumerate(node.children)
            }
        return {
            child.name: _physical_value(_model_member(value, child.name), child)
            for child in node.children
        }
    sequence = cast(Sequence[object], value)
    return [_physical_value(item, node.item) for item in sequence]


def encode_contract_rows(
    *,
    root_role: str,
    rows: Sequence[BaseModel],
    parent_paths: tuple[str, ...],
) -> WyscoutParquetEncoding:
    """Encode/readback exact typed rows through the accepted descriptor."""

    descriptor = projection_descriptor(root_role)
    schema = arrow_schema_from_w04_projection(descriptor)
    physical = [
        {
            field.name: _physical_value(getattr(row, field.name), field)
            for field in descriptor.fields
        }
        for row in rows
    ]
    table = pa.Table.from_pylist(physical, schema=schema)
    logical_rows = tuple(row.model_dump(mode="json") for row in rows)
    contract_rows = tuple(canonical_json_bytes(row) for row in logical_rows)
    key_paths = w04_physical_primary_key_paths(root_role)
    primary_keys: list[tuple[str | int, ...]] = []
    for row in logical_rows:
        key: list[str | int] = []
        for path in key_paths:
            current: object = row
            for segment in path:
                if type(current) is not dict or segment not in current:
                    raise ValueError("logical row is missing its descriptor-owned primary key")
                current = cast(dict[str, object], current)[segment]
            if type(current) not in {str, int}:
                raise ValueError("logical primary-key value is not an exact string or integer")
            key.append(cast(str | int, current))
        primary_keys.append(tuple(key))
    encoding = encode_w04_wyscout_product_parquet(
        table,
        projection_descriptor=descriptor,
        primary_key_fields=tuple(".".join(path) for path in key_paths),
        primary_keys=primary_keys,
        contract_row_bytes=contract_rows,
        parent_paths=parent_paths,
    )
    if encoding.row_count != len(rows):
        raise AssertionError("encoded row count drifted")
    return encoding


def publish_product(
    *,
    publisher: WyscoutStagedPublisher,
    final_root: Path,
    relative_path: str,
    encoding: WyscoutParquetEncoding,
    final_recheck: Callable[[], object],
) -> bytes:
    """Publish and immutably reopen one accepted working product."""

    prefix = "data/working/wyscout/v5/"
    if not relative_path.startswith(prefix):
        raise ValueError("working product path is outside the accepted root")

    def validator(candidate: bytes) -> None:
        if candidate != encoding.payload:
            raise ValueError("staged Parquet bytes differ from accepted encoding")

    result = publisher.publish_bytes(
        "wyscout-working",
        relative_path.removeprefix(prefix),
        encoding.payload,
        validator=validator,
        final_recheck=final_recheck,
    )
    readback = guarded_read(final_root / relative_path.removeprefix(prefix))
    if (
        readback != encoding.payload
        or result.physical_sha256 != encoding.physical_sha256
        or result.size_bytes != encoding.size_bytes
    ):
        raise ValueError("published Parquet immutable readback drifted")
    return readback


def utc_token(value: datetime) -> str:
    """Render the exact six-fraction UTC partition token."""

    return value.strftime("%Y%m%dT%H%M%S%fZ")


__all__ = [
    "WyscoutProductRoots",
    "PublishedProduct",
    "complete_match_lineage",
    "dependency_lineage",
    "encode_contract_rows",
    "guarded_read",
    "publish_product",
    "projection_descriptor",
    "sha256",
    "staged_publisher",
    "tenant_context",
    "utc_token",
]

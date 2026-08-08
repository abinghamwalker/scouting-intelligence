# ruff: noqa: E501  # Frozen compact R5 JSONL oracle rows are byte-exact.

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import textwrap
import types
from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated, TypeAliasType, Union, cast, get_args, get_origin

import pyarrow as pa  # type: ignore[import-untyped]
import pytest
import test_wyscout_data_contracts as data_fixtures
from pydantic import BaseModel

from scouting.contracts import evidence, primitives, wyscout_build, wyscout_data
from scouting.contracts.wyscout_schema import (
    W04_CANONICAL_CONTENT_KEY_ORDER,
    W04_CANONICAL_SCHEMA_VERSION,
    W04_IMPLEMENTED_ROW_KEY_ORDER,
    W04_IMPLEMENTED_SCHEMA_SURFACE,
    W04_JSON_ONLY_PROJECTION_STATE,
    W04_PARQUET_SERIALIZER_VERSION,
    W04_SCHEMA_LANGUAGE_VERSION,
    W04_SCHEMA_ROOT_ROLES,
    W04SchemaClosureError,
    canonical_w04_schema_content_bytes,
    export_w04_implemented_schema_contents,
    export_w04_implemented_schema_rows,
    validate_w04_implemented_schema_exports,
    w04_canonical_schema_id,
    w04_parquet_projection_content,
    w04_physical_primary_key_paths,
)
from scouting.storage.formats import (
    WyscoutArrowListKind,
    WyscoutArrowListNode,
    WyscoutArrowProjectionField,
    WyscoutArrowScalarNode,
    WyscoutArrowScalarType,
    WyscoutArrowStructNode,
    WyscoutLogicalArrowProjectionKind,
    WyscoutParquetProjectionDescriptor,
    arrow_schema_from_w04_projection,
    canonical_decimal_to_w04_arrow_utf8,
    canonical_json_bytes,
    canonical_json_value_to_w04_arrow_utf8,
    encode_w04_wyscout_product_parquet,
    exact_decimal128_with_exponent_to_w04_arrow,
)

ROOT_MODELS: tuple[type[BaseModel], ...] = (
    wyscout_data.BronzeKnownRecord,
    wyscout_data.BronzeRejectedRecord,
    wyscout_data.BronzeRejectedField,
    wyscout_data.SilverCompetition,
    wyscout_data.SilverTeam,
    wyscout_data.SilverPlayer,
    wyscout_data.SilverMatch,
    wyscout_data.SilverAction,
    wyscout_data.SilverLineupStint,
    wyscout_data.SilverPossession,
    wyscout_data.SilverPlayerMatchFact,
    wyscout_data.GoldPlayerWindow,
    wyscout_data.LayerManifest,
    wyscout_build.TemporalBoundaryReceipt,
    wyscout_build.RebuildInvocationReceipt,
    wyscout_build.EntrypointSourceResult,
    wyscout_build.ComponentProofResult,
    wyscout_build.PreBuildAdmissionResult,
    wyscout_build.RebuildReceiptSummary,
    wyscout_build.LayerManifestSummary,
    wyscout_build.FinalRecheckResult,
    wyscout_build.PostBuildIdRebuildResult,
    wyscout_build.ChildResultEnvelope,
)

EXPECTED_DEPENDENCY_ROLES = (
    (),
    (),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD", "SILVER_COMPETITION", "SILVER_TEAM"),
    ("BRONZE_KNOWN_RECORD", "SILVER_MATCH", "SILVER_PLAYER", "SILVER_TEAM"),
    ("SILVER_MATCH", "SILVER_PLAYER", "SILVER_TEAM"),
    ("SILVER_ACTION",),
    (
        "SILVER_ACTION",
        "SILVER_LINEUP_STINT",
        "SILVER_MATCH",
        "SILVER_PLAYER",
        "SILVER_POSSESSION",
    ),
    ("SILVER_PLAYER_MATCH_FACT",),
    W04_SCHEMA_ROOT_ROLES[:12],
    ("GOLD_PLAYER_WINDOW", "LAYER_MANIFEST"),
    ("LAYER_MANIFEST", "TEMPORAL_BOUNDARY_RECEIPT"),
    (),
    (),
    ("COMPONENT_PROOF_RESULT",),
    (),
    ("LAYER_MANIFEST",),
    ("REBUILD_RECEIPT_SUMMARY", "LAYER_MANIFEST_SUMMARY"),
    (
        "REBUILD_RECEIPT_SUMMARY",
        "LAYER_MANIFEST_SUMMARY",
        "FINAL_RECHECK_RESULT",
    ),
    (
        "ENTRYPOINT_SOURCE_RESULT",
        "PRE_BUILD_ADMISSION_RESULT",
        "POST_BUILD_ID_REBUILD_RESULT",
    ),
)

EXPECTED_PHYSICAL_PRIMARY_KEY_PATHS = {
    "BRONZE_KNOWN_RECORD": (
        ("source_row", "source_manifest_id"),
        ("source_row", "completion_relative_path"),
        ("source_row", "source_record_ordinal"),
    ),
    "BRONZE_REJECTED_RECORD": (
        ("source_row", "source_manifest_id"),
        ("source_row", "completion_relative_path"),
        ("source_row", "source_record_ordinal"),
    ),
    "BRONZE_REJECTED_FIELD": (
        ("source_row", "source_manifest_id"),
        ("source_row", "completion_relative_path"),
        ("source_row", "source_record_ordinal"),
        ("json_path",),
    ),
    "SILVER_COMPETITION": (("competition_id",),),
    "SILVER_TEAM": (("team_id",),),
    "SILVER_PLAYER": (("player_id",),),
    "SILVER_MATCH": (("match_id",),),
    "SILVER_ACTION": (("action_id",),),
    "SILVER_LINEUP_STINT": (("lineup_stint_id",),),
    "SILVER_POSSESSION": (("possession_id",),),
    "SILVER_PLAYER_MATCH_FACT": (
        ("tenant_context", "tenant_id"),
        ("source_manifest_id",),
        ("match_id",),
        ("player_id",),
        ("player_match_fact_schema_version",),
    ),
    "GOLD_PLAYER_WINDOW": (
        ("tenant_context", "tenant_id"),
        ("player_id",),
        ("competition_id",),
        ("season_id",),
        ("role_context_id",),
        ("role_context_version",),
        ("window_definition_id",),
        ("window_start_utc",),
        ("window_end_utc",),
        ("feature_cutoff_ts",),
        ("dependency_lineage_hash",),
    ),
}


def _exact_dict(value: object, keys: set[str]) -> dict[str, object]:
    assert type(value) is dict
    assert set(value) == keys
    return cast(dict[str, object], value)


def _instantiate_field(value: object) -> WyscoutArrowProjectionField:
    raw = _exact_dict(value, {"name", "nullable", "node", "logical_position"})
    assert type(raw["name"]) is str
    assert type(raw["nullable"]) is bool
    assert raw["logical_position"] is None or type(raw["logical_position"]) is int
    return WyscoutArrowProjectionField(
        name=raw["name"],
        nullable=raw["nullable"],
        node=_instantiate_node(raw["node"]),
        logical_position=raw["logical_position"],
    )


def _instantiate_node(
    value: object,
) -> WyscoutArrowScalarNode | WyscoutArrowStructNode | WyscoutArrowListNode:
    assert type(value) is dict
    raw = cast(dict[str, object], value)
    kind = raw.get("node_kind")
    if kind == "SCALAR":
        assert set(raw) == {
            "node_kind",
            "scalar_type",
            "projection_kind",
            "decimal_precision",
            "decimal_scale",
        }
        scalar_type = raw["scalar_type"]
        projection_kind = raw["projection_kind"]
        assert type(scalar_type) is str and type(projection_kind) is str
        return WyscoutArrowScalarNode(
            scalar_type=WyscoutArrowScalarType(scalar_type),
            projection_kind=WyscoutLogicalArrowProjectionKind(projection_kind),
            decimal_precision=cast(int | None, raw["decimal_precision"]),
            decimal_scale=cast(int | None, raw["decimal_scale"]),
        )
    if kind == "STRUCT":
        assert set(raw) == {"node_kind", "projection_kind", "children"}
        assert type(raw["children"]) is list
        projection_kind = raw["projection_kind"]
        assert type(projection_kind) is str
        return WyscoutArrowStructNode(
            projection_kind=WyscoutLogicalArrowProjectionKind(projection_kind),
            children=tuple(_instantiate_field(item) for item in raw["children"]),
        )
    assert kind == "LIST"
    assert set(raw) == {
        "node_kind",
        "projection_kind",
        "list_kind",
        "item",
        "fixed_size",
    }
    projection_kind = raw["projection_kind"]
    list_kind = raw["list_kind"]
    assert type(projection_kind) is str and type(list_kind) is str
    return WyscoutArrowListNode(
        projection_kind=WyscoutLogicalArrowProjectionKind(projection_kind),
        list_kind=WyscoutArrowListKind(list_kind),
        item=_instantiate_field(raw["item"]),
        fixed_size=cast(int | None, raw["fixed_size"]),
    )


def _instantiate_descriptor(root_role: str) -> WyscoutParquetProjectionDescriptor:
    projection = w04_parquet_projection_content(root_role)
    assert set(projection) == {
        "descriptor",
        "forward_projection",
        "inverse_decoding",
        "metadata_policy",
        "schema_source",
    }
    assert projection["metadata_policy"] == "ABSENT_AT_SCHEMA_FIELD_STRUCT_AND_LIST_LEVELS"
    assert projection["schema_source"] == "ONLY_THIS_CANONICAL_ROOT_CONTENT"
    raw = _exact_dict(projection["descriptor"], {"schema_role", "serializer_version", "fields"})
    assert type(raw["schema_role"]) is str
    assert raw["serializer_version"] == W04_PARQUET_SERIALIZER_VERSION
    assert type(raw["fields"]) is list
    return WyscoutParquetProjectionDescriptor(
        schema_role=raw["schema_role"],
        serializer_version=raw["serializer_version"],
        fields=tuple(_instantiate_field(item) for item in raw["fields"]),
    )


def _assert_metadata_absent(data_type: pa.DataType) -> None:
    if pa.types.is_struct(data_type):
        for child in data_type:
            assert child.metadata is None
            _assert_metadata_absent(child.type)
    elif (
        pa.types.is_list(data_type)
        or pa.types.is_large_list(data_type)
        or pa.types.is_fixed_size_list(data_type)
    ):
        assert data_type.value_field.metadata is None
        _assert_metadata_absent(data_type.value_field.type)


def _tagged_scalar_paths(
    fields: tuple[WyscoutArrowProjectionField, ...],
    *,
    prefix: str,
) -> list[str]:
    result: list[str] = []
    for field in fields:
        path = f"{prefix}.{field.name}"
        node = field.node
        if (
            type(node) is WyscoutArrowScalarNode
            and node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8
        ):
            result.append(path)
        elif type(node) is WyscoutArrowStructNode:
            result.extend(_tagged_scalar_paths(node.children, prefix=path))
        elif type(node) is WyscoutArrowListNode:
            result.extend(_tagged_scalar_paths((node.item,), prefix=f"{path}[]"))
    return result


def _scalar_projection_paths(
    fields: tuple[WyscoutArrowProjectionField, ...],
    *,
    prefix: str,
    projection_kind: WyscoutLogicalArrowProjectionKind,
) -> list[str]:
    result: list[str] = []
    for field in fields:
        path = f"{prefix}.{field.name}"
        node = field.node
        if type(node) is WyscoutArrowScalarNode and node.projection_kind is projection_kind:
            result.append(path)
        elif type(node) is WyscoutArrowStructNode:
            result.extend(
                _scalar_projection_paths(
                    node.children,
                    prefix=path,
                    projection_kind=projection_kind,
                )
            )
        elif type(node) is WyscoutArrowListNode:
            result.extend(
                _scalar_projection_paths(
                    (node.item,),
                    prefix=f"{path}[]",
                    projection_kind=projection_kind,
                )
            )
    return result


def _decimal128_paths(
    fields: tuple[WyscoutArrowProjectionField, ...],
    *,
    prefix: str,
) -> list[str]:
    result: list[str] = []
    for field in fields:
        path = f"{prefix}.{field.name}"
        node = field.node
        if type(node) is WyscoutArrowScalarNode:
            if node.scalar_type is WyscoutArrowScalarType.DECIMAL128:
                assert (node.decimal_precision, node.decimal_scale) == (22, 18)
                result.append(path)
        elif type(node) is WyscoutArrowStructNode:
            result.extend(_decimal128_paths(node.children, prefix=path))
        elif type(node) is WyscoutArrowListNode:
            result.extend(_decimal128_paths((node.item,), prefix=f"{path}[]"))
    return result


def _exact_decimal_paths(
    fields: tuple[WyscoutArrowProjectionField, ...],
    *,
    prefix: str,
) -> list[str]:
    result: list[str] = []
    for field in fields:
        path = f"{prefix}.{field.name}"
        node = field.node
        if (
            type(node) is WyscoutArrowStructNode
            and node.projection_kind
            is WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT
        ):
            assert tuple(child.name for child in node.children) == (
                "value",
                "exponent",
                "negative_zero",
            )
            assert all(not child.nullable for child in node.children)
            result.append(path)
        elif type(node) is WyscoutArrowStructNode:
            result.extend(_exact_decimal_paths(node.children, prefix=path))
        elif type(node) is WyscoutArrowListNode:
            result.extend(_exact_decimal_paths((node.item,), prefix=f"{path}[]"))
    return result


def _physical_and_logical(
    field: WyscoutArrowProjectionField,
    *,
    variant: int,
) -> tuple[object, object]:
    if field.nullable and variant == 0:
        return None, None
    node = field.node
    if type(node) is WyscoutArrowScalarNode:
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8:
            value = wyscout_data.CanonicalJsonObject(
                value=(
                    wyscout_data.CanonicalJsonMember(
                        key="variant",
                        value=wyscout_data.CanonicalJsonInteger(value=variant + 1),
                    ),
                )
            )
            return canonical_json_value_to_w04_arrow_utf8(value), value.model_dump(mode="json")
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8:
            decimal_value = (
                Decimal("0.33333333333333333333333333333333333333")
                if variant == 0
                else Decimal("1.2300")
            )
            rendered = canonical_decimal_to_w04_arrow_utf8(decimal_value)
            return rendered, rendered
        scalar = node.scalar_type
        if scalar is WyscoutArrowScalarType.NULL:
            return None, None
        if scalar is WyscoutArrowScalarType.BOOL:
            return bool(variant), bool(variant)
        if scalar in {
            WyscoutArrowScalarType.INT8,
            WyscoutArrowScalarType.INT16,
            WyscoutArrowScalarType.INT32,
            WyscoutArrowScalarType.INT64,
            WyscoutArrowScalarType.UINT8,
            WyscoutArrowScalarType.UINT16,
            WyscoutArrowScalarType.UINT32,
            WyscoutArrowScalarType.UINT64,
        }:
            return variant + 1, variant + 1
        if scalar in {
            WyscoutArrowScalarType.FLOAT16,
            WyscoutArrowScalarType.FLOAT32,
            WyscoutArrowScalarType.FLOAT64,
        }:
            return float(variant + 1), float(variant + 1)
        if scalar is WyscoutArrowScalarType.UTF8:
            return f"variant-{variant}", f"variant-{variant}"
        if scalar is WyscoutArrowScalarType.DECIMAL128:
            decimal_value = Decimal(variant + 1).quantize(Decimal("0.000000000000000001"))
            return decimal_value, format(decimal_value, "f")
        if scalar is WyscoutArrowScalarType.TIMESTAMP_US_UTC:
            timestamp_value = datetime(2026, 8, variant + 1, tzinfo=UTC)
            return timestamp_value, timestamp_value.strftime("%Y-%m-%dT%H:%M:%SZ")
        raise AssertionError("unhandled accepted scalar")
    if type(node) is WyscoutArrowStructNode:
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT:
            decimal_value = Decimal("10") if variant == 0 else Decimal("-0.000000000000000000")
            return (
                exact_decimal128_with_exponent_to_w04_arrow(decimal_value),
                str(decimal_value),
            )
        pairs = [_physical_and_logical(child, variant=variant) for child in node.children]
        physical = {child.name: pair[0] for child, pair in zip(node.children, pairs, strict=True)}
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT:
            return physical, [pair[1] for pair in pairs]
        return physical, {
            child.name: pair[1] for child, pair in zip(node.children, pairs, strict=True)
        }
    assert type(node) is WyscoutArrowListNode
    item_count = node.fixed_size if node.fixed_size is not None else 1
    pairs = [_physical_and_logical(node.item, variant=variant) for _index in range(item_count)]
    return [pair[0] for pair in pairs], [pair[1] for pair in pairs]


def _row_pair(
    descriptor: WyscoutParquetProjectionDescriptor,
    variant: int,
) -> tuple[dict[str, object], dict[str, object]]:
    pairs = [_physical_and_logical(field, variant=variant) for field in descriptor.fields]
    return (
        {field.name: pair[0] for field, pair in zip(descriptor.fields, pairs, strict=True)},
        {field.name: pair[1] for field, pair in zip(descriptor.fields, pairs, strict=True)},
    )


def _lineage_for_action_sequence(
    sequence: wyscout_data.PossessionPeriodSequence,
) -> wyscout_data.WyscoutRowLineage:
    base = data_fixtures.make_lineage()
    non_action_rows = tuple(
        row
        for row in base.source_rows
        if row.record_kind is not wyscout_data.SourceRecordKind.ACTION
    )
    payload = base.model_dump()
    payload["source_rows"] = tuple(
        sorted(
            (*non_action_rows, *(entry.source_row for entry in sequence.actions)),
            key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
        )
    )
    return wyscout_data.WyscoutRowLineage.model_validate(payload, strict=True)


def _scale18_action(action: wyscout_data.SilverAction) -> wyscout_data.SilverAction:
    quantum = Decimal("0.000000000000000001")
    payload = action.model_dump()
    payload["period_elapsed_seconds"] = action.period_elapsed_seconds.quantize(quantum)
    payload["event_sec_source_scale"] = 18
    payload["action_positions"] = tuple(
        {
            **position.model_dump(),
            "x": position.x.quantize(quantum),
            "y": position.y.quantize(quantum),
        }
        for position in action.action_positions
    )
    sequence = dict(payload["possession_period_sequence"])
    sequence["actions"] = tuple(
        {
            **entry,
            "period_elapsed_seconds": cast(Decimal, entry["period_elapsed_seconds"]).quantize(
                quantum
            ),
        }
        for entry in sequence["actions"]
    )
    payload["possession_period_sequence"] = sequence
    return wyscout_data.SilverAction.model_validate(payload, strict=True)


def _three_action_precision_fact() -> tuple[
    tuple[wyscout_data.SilverAction, ...],
    wyscout_data.SilverPossession,
    wyscout_data.SilverPlayerMatchFact,
    wyscout_data.GoldPlayerWindow,
]:
    team_id = wyscout_data.canonical_source_uuid(wyscout_data.SourceRecordKind.TEAM, 2)
    sequence = data_fixtures._equal_clock_sequence(
        (
            (5, team_id, 7, 70, Decimal("9.000000000000000000")),
            (6, team_id, 7, 70, Decimal("10.000000000000000000")),
            (7, team_id, 7, 70, Decimal("11.000000000000000000")),
        )
    )
    lineage = _lineage_for_action_sequence(sequence)
    base_action = _scale18_action(data_fixtures.make_silver_rows()[4])
    positions = (
        (
            wyscout_data.ActionPosition(
                x=Decimal("50.000000000000000000"),
                y=Decimal("60.000000000000000000"),
                within_accepted_bounds=True,
            ),
        ),
        (
            wyscout_data.ActionPosition(
                x=Decimal("-1.000000000000000000"),
                y=Decimal("60.000000000000000000"),
                within_accepted_bounds=False,
            ),
        ),
        (
            wyscout_data.ActionPosition(
                x=Decimal("101.000000000000000000"),
                y=Decimal("60.000000000000000000"),
                within_accepted_bounds=False,
            ),
        ),
    )
    actions: list[wyscout_data.SilverAction] = []
    for entry, action_positions in zip(sequence.actions, positions, strict=True):
        payload = base_action.model_dump()
        payload.update(
            lineage=lineage,
            source_rows=(entry.source_row,),
            action_source_id=entry.source_event_record_id,
            action_id=entry.action_id,
            source_event_record_id=entry.source_event_record_id,
            period_elapsed_seconds=entry.period_elapsed_seconds,
            source_record_ordinal=entry.source_record_ordinal,
            action_positions=action_positions,
            possession_period_sequence=sequence,
        )
        actions.append(wyscout_data.SilverAction.model_validate(payload, strict=True))
    frozen_actions = tuple(actions)
    possession_payload = data_fixtures.make_silver_rows()[6].model_dump()
    possession_payload.update(
        lineage=lineage,
        source_rows=tuple(entry.source_row for entry in sequence.actions),
        contributing_actions=frozen_actions,
        action_ids=tuple(action.action_id for action in frozen_actions),
        first_action_order=frozen_actions[0].action_order_key,
        last_action_order=frozen_actions[-1].action_order_key,
    )
    possession = wyscout_data.SilverPossession.model_validate(possession_payload, strict=True)
    one_third = Decimal("0.33333333333333333333333333333333333333")
    counts = {
        wyscout_data.GoldCoverageDimensionName.IDENTITY: 3,
        wyscout_data.GoldCoverageDimensionName.LINEUP: 1,
        wyscout_data.GoldCoverageDimensionName.ACTION: 3,
        wyscout_data.GoldCoverageDimensionName.POSSESSION: 3,
        wyscout_data.GoldCoverageDimensionName.TEMPORAL: 9,
    }
    dimensions = tuple(
        wyscout_data.GoldCoverageDimension(
            name=name,
            numerator=1
            if name is wyscout_data.GoldCoverageDimensionName.COORDINATE
            else counts[name],
            denominator=(
                3 if name is wyscout_data.GoldCoverageDimensionName.COORDINATE else counts[name]
            ),
            coverage=(
                one_third
                if name is wyscout_data.GoldCoverageDimensionName.COORDINATE
                else Decimal(1)
            ),
            state=(
                wyscout_data.GoldCoverageState.PARTIAL
                if name is wyscout_data.GoldCoverageDimensionName.COORDINATE
                else wyscout_data.GoldCoverageState.COMPLETE
            ),
            reason_codes=(
                ("COORDINATE_EVIDENCE_INCOMPLETE",)
                if name is wyscout_data.GoldCoverageDimensionName.COORDINATE
                else ()
            ),
        )
        for name in wyscout_data.GoldCoverageDimensionName
    )
    coverage = wyscout_data.GoldCoverage(
        dimensions=dimensions,
        coverage_overall=one_third,
        missing_dimensions=(wyscout_data.GoldCoverageDimensionName.COORDINATE,),
    )
    applicability = wyscout_data.W04ApplicabilityAssessment(
        state=wyscout_data.W04Applicability.RESEARCH_ONLY,
        reason_codes=("COORDINATE_EVIDENCE_INCOMPLETE",),
    )
    fact_payload = data_fixtures.make_silver_rows()[-1].model_dump()
    fact_payload.update(
        lineage=lineage,
        source_rows=tuple(entry.source_row for entry in sequence.actions),
        contributing_actions=frozen_actions,
        contributing_possessions=(possession,),
        action_count=3,
        coordinate_known_action_count=1,
        resolved_possession_action_count=3,
        coverage=coverage,
        applicability=applicability,
    )
    fact = wyscout_data.SilverPlayerMatchFact.model_validate(fact_payload, strict=True)
    gold_payload = data_fixtures.make_gold().model_dump()
    gold_payload.update(
        lineage=lineage,
        source_rows=fact.source_rows,
        coverage=coverage,
        applicability=applicability,
        contributing_player_match_facts=(fact,),
        contributing_player_match_keys=(fact.primary_key,),
    )
    gold_payload["features"].update(
        action_count=3,
        coordinate_known_action_count=1,
        resolved_possession_action_count=3,
    )
    gold = wyscout_data.GoldPlayerWindow.model_validate(gold_payload, strict=True)
    return frozen_actions, possession, fact, gold


def _open_lineup_fact_and_gold() -> tuple[
    wyscout_data.SilverLineupStint,
    wyscout_data.SilverPlayerMatchFact,
    wyscout_data.GoldPlayerWindow,
]:
    open_payload = data_fixtures.make_silver_rows()[5].model_dump()
    open_payload.update(
        end_interval=None,
        lower_bound_minutes=None,
        upper_bound_minutes=None,
        right_censored=True,
    )
    lineup = wyscout_data.SilverLineupStint.model_validate(open_payload, strict=True)
    authorities = {row.authority_kind: row for row in wyscout_data.accepted_authority_references()}
    dimension_rows = {
        wyscout_data.GoldCoverageDimensionName.IDENTITY: (1, 1, Decimal(1), None, ()),
        wyscout_data.GoldCoverageDimensionName.LINEUP: (1, 1, Decimal(1), None, ()),
        wyscout_data.GoldCoverageDimensionName.ACTION: (
            0,
            0,
            Decimal(0),
            None,
            ("ACTION_EVIDENCE_INCOMPLETE",),
        ),
        wyscout_data.GoldCoverageDimensionName.COORDINATE: (
            0,
            0,
            Decimal(1),
            wyscout_data.AuthorityKind.FIELD,
            ("NO_APPLICABLE_COORDINATE_EVIDENCE",),
        ),
        wyscout_data.GoldCoverageDimensionName.POSSESSION: (
            0,
            0,
            Decimal(1),
            wyscout_data.AuthorityKind.POSSESSION,
            ("NO_POSSESSION_ELIGIBLE_ACTIONS",),
        ),
        wyscout_data.GoldCoverageDimensionName.TEMPORAL: (6, 6, Decimal(1), None, ()),
    }
    dimensions: list[wyscout_data.GoldCoverageDimension] = []
    for name in wyscout_data.GoldCoverageDimensionName:
        numerator, denominator, coverage_value, authority_kind, reasons = dimension_rows[name]
        if name is wyscout_data.GoldCoverageDimensionName.ACTION:
            state = wyscout_data.GoldCoverageState.MISSING_ZERO_DENOMINATOR
        elif authority_kind is not None:
            state = wyscout_data.GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR
        else:
            state = wyscout_data.GoldCoverageState.COMPLETE
        dimensions.append(
            wyscout_data.GoldCoverageDimension(
                name=name,
                numerator=numerator,
                denominator=denominator,
                coverage=coverage_value,
                state=state,
                reason_codes=reasons,
                zero_denominator_authority=(
                    authorities[authority_kind] if authority_kind is not None else None
                ),
            )
        )
    coverage = wyscout_data.GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal(0),
        missing_dimensions=(wyscout_data.GoldCoverageDimensionName.ACTION,),
    )
    applicability = wyscout_data.W04ApplicabilityAssessment(
        state=wyscout_data.W04Applicability.SUPPRESSED,
        reason_codes=("ACTION_EVIDENCE_INCOMPLETE", "RIGHT_CENSORED_OR_UNCERTAIN"),
    )
    fact_payload = data_fixtures.make_silver_rows()[-1].model_dump()
    fact_payload.update(
        source_rows=lineup.source_rows,
        lineup_evidence_present=True,
        contributing_lineup_stints=(lineup,),
        contributing_actions=(),
        contributing_possessions=(),
        action_count=0,
        coordinate_known_action_count=0,
        resolved_possession_action_count=0,
        right_censored_or_uncertain=True,
        coverage=coverage,
        applicability=applicability,
    )
    fact = wyscout_data.SilverPlayerMatchFact.model_validate(fact_payload, strict=True)
    gold_payload = data_fixtures.make_gold().model_dump()
    gold_payload.update(
        source_rows=fact.source_rows,
        coverage=coverage,
        applicability=applicability,
        contributing_player_match_facts=(fact,),
        contributing_player_match_keys=(fact.primary_key,),
    )
    gold_payload["features"].update(
        action_count=0,
        coordinate_known_action_count=0,
        resolved_possession_action_count=0,
    )
    gold = wyscout_data.GoldPlayerWindow.model_validate(gold_payload, strict=True)
    return lineup, fact, gold


def _equal_clock_survivor_possession() -> wyscout_data.SilverPossession:
    team_a = wyscout_data.canonical_source_uuid(wyscout_data.SourceRecordKind.TEAM, 2)
    team_b = wyscout_data.canonical_source_uuid(wyscout_data.SourceRecordKind.TEAM, 22)
    sequence = data_fixtures._equal_clock_sequence(
        (
            (5, team_a, 7, 70, Decimal("9.000000000000000000")),
            (6, team_a, 7, 70, Decimal("10.000000000000000000")),
            (7, team_b, 7, 70, Decimal("10.000000000000000000")),
        )
    )
    lineage = _lineage_for_action_sequence(sequence)
    entry = sequence.actions[0]
    action_payload = _scale18_action(data_fixtures.make_silver_rows()[4]).model_dump()
    action_payload.update(
        lineage=lineage,
        source_rows=(entry.source_row,),
        period_elapsed_seconds=entry.period_elapsed_seconds,
        possession_period_sequence=sequence,
    )
    action = wyscout_data.SilverAction.model_validate(action_payload, strict=True)
    possession_payload = data_fixtures.make_silver_rows()[6].model_dump()
    possession_payload.update(
        lineage=lineage,
        source_rows=tuple(item.source_row for item in sequence.actions),
        contributing_actions=(action,),
        action_ids=(action.action_id,),
        first_action_order=action.action_order_key,
        last_action_order=action.action_order_key,
    )
    return wyscout_data.SilverPossession.model_validate(possession_payload, strict=True)


def _lineage_with_source_row(
    base: wyscout_data.WyscoutRowLineage,
    source_row: wyscout_data.WyscoutSourceRowReference,
) -> wyscout_data.WyscoutRowLineage:
    physical_key = (source_row.completion_relative_path, source_row.source_record_ordinal)
    payload = base.model_dump()
    payload["source_rows"] = tuple(
        sorted(
            (
                *(
                    row
                    for row in base.source_rows
                    if (row.completion_relative_path, row.source_record_ordinal) != physical_key
                ),
                source_row,
            ),
            key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
        )
    )
    return wyscout_data.WyscoutRowLineage.model_validate(payload, strict=True)


def _source_row_for_raw_record(
    template: wyscout_data.WyscoutSourceRowReference,
    raw_record: wyscout_data.CanonicalJsonObject,
    *,
    source_record_ordinal: int | None = None,
) -> wyscout_data.WyscoutSourceRowReference:
    payload = template.model_dump()
    if source_record_ordinal is not None:
        payload["source_record_ordinal"] = source_record_ordinal
    payload["raw_record_sha256"] = hashlib.sha256(
        wyscout_data.canonical_raw_json_bytes(raw_record)
    ).hexdigest()
    return wyscout_data.WyscoutSourceRowReference.model_validate(payload, strict=True)


def _r5_silver_action_variant(
    base: wyscout_data.SilverAction,
    *,
    action_source_id: int,
    source_record_ordinal: int,
    competition_id: object,
    period_elapsed_seconds: Decimal,
    event_sec_source_scale: int,
    action_positions: tuple[wyscout_data.ActionPosition, ...],
    player_id: object,
    team_id: object,
    action_event_taxonomy_id: int | None,
    action_subevent_taxonomy_id: int | None,
    action_tag_ids: tuple[int, ...],
    possession_predicate_state: wyscout_data.PossessionPredicateState,
    possession_eligibility_state: wyscout_data.PossessionEligibilityState,
) -> wyscout_data.SilverAction:
    source_row_payload = base.source_rows[0].model_dump(mode="python")
    source_row_payload.update(
        source_record_ordinal=source_record_ordinal,
        raw_record_sha256=f"{action_source_id % 10}" * 64,
    )
    source_row = wyscout_data.WyscoutSourceRowReference.model_validate(
        source_row_payload, strict=True
    )
    action_id = wyscout_data.canonical_source_uuid(
        wyscout_data.SourceRecordKind.ACTION, action_source_id
    )
    sequence_entry = wyscout_data.PossessionSequenceAction.model_validate(
        {
            "action_id": action_id,
            "source_event_record_id": action_source_id,
            "source_row": source_row,
            "match_id": base.match_id,
            "player_id": player_id,
            "team_id": team_id,
            "action_event_taxonomy_id": action_event_taxonomy_id,
            "action_subevent_taxonomy_id": action_subevent_taxonomy_id,
            "action_period_code": base.action_period_code,
            "period_rank": base.period_rank,
            "period_elapsed_seconds": period_elapsed_seconds,
            "source_record_ordinal": source_record_ordinal,
            "action_tag_ids": action_tag_ids,
        },
        strict=True,
    )
    sequence = wyscout_data.PossessionPeriodSequence.model_validate(
        {
            "construction_authority_state": "semantic_only_unchecked",
            "match_id": base.match_id,
            "source_completion_index_sha256": base.source_completion_index_sha256,
            "source_completion_membership_sha256": (
                base.possession_period_sequence.source_completion_membership_sha256
            ),
            "action_period_code": base.action_period_code,
            "period_action_count": 1,
            "actions": (sequence_entry,),
            "complete_period_evidence": True,
        },
        strict=True,
    )
    payload = base.model_dump(mode="python")
    payload.update(
        lineage=_lineage_for_action_sequence(sequence),
        source_rows=(source_row,),
        action_source_id=action_source_id,
        action_id=action_id,
        source_event_record_id=action_source_id,
        competition_id=competition_id,
        player_id=player_id,
        team_id=team_id,
        action_event_taxonomy_id=action_event_taxonomy_id,
        action_subevent_taxonomy_id=action_subevent_taxonomy_id,
        period_elapsed_seconds=period_elapsed_seconds,
        event_sec_source_scale=event_sec_source_scale,
        source_record_ordinal=source_record_ordinal,
        action_tag_ids=action_tag_ids,
        action_positions=action_positions,
        possession_predicate_state=possession_predicate_state,
        possession_period_sequence=sequence,
        possession_eligibility_state=possession_eligibility_state,
    )
    return wyscout_data.SilverAction.model_validate(payload, strict=True)


def _canonical_json_kind_roster(
    value: wyscout_data.CanonicalJsonValue,
) -> set[wyscout_data.CanonicalJsonKind]:
    result = {value.kind}
    if isinstance(value, wyscout_data.CanonicalJsonArray):
        for item in value.value:
            result.update(_canonical_json_kind_roster(item))
    elif isinstance(value, wyscout_data.CanonicalJsonObject):
        for member in value.value:
            result.update(_canonical_json_kind_roster(member.value))
    return result


def _valid_model_matrix() -> tuple[tuple[str, BaseModel], ...]:
    envelopes = data_fixtures.make_envelopes()
    lineage = data_fixtures.make_lineage()
    known_raw_records = (
        cast(
            wyscout_data.CanonicalJsonObject,
            wyscout_data.canonicalize_json_value(
                {
                    "array": [None, True, 7, Decimal("1.25"), "text", [], {}],
                    "boolean": False,
                    "integer": 42,
                    "nullValue": None,
                    "number": Decimal("9.500"),
                    "object": {"nested": [{"leaf": None}]},
                    "string": "recursive-all-seven-arms",
                }
            ),
        ),
        cast(
            wyscout_data.CanonicalJsonObject,
            wyscout_data.canonicalize_json_value(
                {"alternate": {"empty_array": [], "empty_object": {}}}
            ),
        ),
    )
    known_source_rows = tuple(
        _source_row_for_raw_record(envelope.source_row_reference, raw_record)
        for envelope, raw_record in zip(envelopes[:2], known_raw_records, strict=True)
    )
    bronze_known = tuple(
        wyscout_data.BronzeKnownRecord(
            build_id=data_fixtures.BUILD_ID,
            tenant_context=data_fixtures.tenant(),
            source_row=source_row,
            raw_record=raw_record,
            raw_record_sha256=source_row.raw_record_sha256,
            measured_raw_fields=data_fixtures.measurements(raw_record),
            classification=data_fixtures.restricted_rights(),
            lineage=_lineage_with_source_row(lineage, source_row),
        )
        for source_row, raw_record in zip(known_source_rows, known_raw_records, strict=True)
    )
    rejected_raw_values: tuple[object, ...] = (
        {"payload": {"case": "missing"}},
        {"payload": [], "record_kind": None},
        {"payload": {"count": 1}, "record_kind": 7},
        {"payload": [True], "record_kind": "unknown_kind"},
        {"payload": {"nested": [None]}, "record_kind": "../action"},
    )
    rejected_raw_records = tuple(
        cast(wyscout_data.CanonicalJsonObject, wyscout_data.canonicalize_json_value(value))
        for value in rejected_raw_values
    )
    raw_kinds = (
        wyscout_data.classify_raw_record_kind(value_present=False),
        wyscout_data.classify_raw_record_kind(value_present=True, value=None),
        wyscout_data.classify_raw_record_kind(value_present=True, value=7),
        wyscout_data.classify_raw_record_kind(value_present=True, value="unknown_kind"),
        wyscout_data.classify_raw_record_kind(value_present=True, value="../action"),
    )
    rejected_source_rows = tuple(
        _source_row_for_raw_record(
            envelopes[0].source_row_reference,
            raw_record,
            source_record_ordinal=index,
        )
        for index, raw_record in enumerate(rejected_raw_records)
    )
    bronze_rejected = tuple(
        wyscout_data.BronzeRejectedRecord(
            build_id=data_fixtures.BUILD_ID,
            tenant_context=data_fixtures.tenant(),
            source_row=wyscout_data.WyscoutRawSourceRowReference.model_validate(
                {
                    key: value
                    for key, value in source_row.model_dump().items()
                    if key != "record_kind" and key != "raw_record_sha256"
                },
                strict=True,
            ),
            raw_record=raw_record,
            raw_record_sha256=source_row.raw_record_sha256,
            raw_kind=raw_kind,
            classification=data_fixtures.restricted_rights(),
            lineage=_lineage_with_source_row(lineage, source_row),
        )
        for raw_kind, raw_record, source_row in zip(
            raw_kinds, rejected_raw_records, rejected_source_rows, strict=True
        )
    )
    rejected_values: tuple[object, ...] = (
        None,
        True,
        999,
        Decimal("1.25"),
        "70",
        [70],
        {"subevent": 70},
    )
    rejected_fields = tuple(data_fixtures.make_rejected_field(value) for value in rejected_values)
    competition, team, player, match, raw_base_action, raw_closed_lineup, raw_possession, _ = (
        data_fixtures.make_silver_rows()
    )
    base_possession_action_payload = data_fixtures.action_payload_with_sequence_updates(
        raw_base_action, period_elapsed_seconds=Decimal("10")
    )
    base_possession_action_payload["event_sec_source_scale"] = 0
    base_possession_action = wyscout_data.SilverAction.model_validate(
        base_possession_action_payload, strict=True
    )
    closed_lineup_payload = raw_closed_lineup.model_dump()
    closed_lineup = wyscout_data.SilverLineupStint.model_validate(
        closed_lineup_payload, strict=True
    )
    base_possession_payload = raw_possession.model_dump()
    base_possession_payload.update(
        contributing_actions=(base_possession_action,),
        first_action_order=base_possession_action.action_order_key,
        last_action_order=base_possession_action.action_order_key,
    )
    base_possession = wyscout_data.SilverPossession.model_validate(
        base_possession_payload, strict=True
    )
    null_unmapped_action = _r5_silver_action_variant(
        raw_base_action,
        action_source_id=5,
        source_record_ordinal=0,
        competition_id=None,
        period_elapsed_seconds=Decimal("0"),
        event_sec_source_scale=0,
        action_positions=(),
        player_id=None,
        team_id=None,
        action_event_taxonomy_id=None,
        action_subevent_taxonomy_id=None,
        action_tag_ids=(101, 102),
        possession_predicate_state=wyscout_data.PossessionPredicateState.PREDICATE_UNMAPPED,
        possession_eligibility_state=wyscout_data.PossessionEligibilityState.INELIGIBLE_UNMAPPED,
    )
    one_position_action = _r5_silver_action_variant(
        raw_base_action,
        action_source_id=6,
        source_record_ordinal=1,
        competition_id=raw_base_action.competition_id,
        period_elapsed_seconds=Decimal("10.123456789012345678"),
        event_sec_source_scale=18,
        action_positions=(
            wyscout_data.ActionPosition.model_validate(
                {
                    "x": Decimal("1.000000000000000000"),
                    "y": Decimal("99.00"),
                    "within_accepted_bounds": True,
                },
                strict=True,
            ),
        ),
        player_id=raw_base_action.player_id,
        team_id=raw_base_action.team_id,
        action_event_taxonomy_id=8,
        action_subevent_taxonomy_id=80,
        action_tag_ids=(201, 202),
        possession_predicate_state=wyscout_data.PossessionPredicateState.PREDICATE_ADMITTED,
        possession_eligibility_state=wyscout_data.PossessionEligibilityState.ELIGIBLE_RESOLVED,
    )
    two_position_action = _r5_silver_action_variant(
        raw_base_action,
        action_source_id=7,
        source_record_ordinal=2,
        competition_id=raw_base_action.competition_id,
        period_elapsed_seconds=Decimal("9999.999999999999999999"),
        event_sec_source_scale=18,
        action_positions=(
            wyscout_data.ActionPosition.model_validate(
                {
                    "x": Decimal("0"),
                    "y": Decimal("100.000"),
                    "within_accepted_bounds": True,
                },
                strict=True,
            ),
            wyscout_data.ActionPosition.model_validate(
                {
                    "x": Decimal("99.000000000000000000"),
                    "y": Decimal("1.0"),
                    "within_accepted_bounds": True,
                },
                strict=True,
            ),
        ),
        player_id=raw_base_action.player_id,
        team_id=raw_base_action.team_id,
        action_event_taxonomy_id=3,
        action_subevent_taxonomy_id=30,
        action_tag_ids=(301, 302),
        possession_predicate_state=wyscout_data.PossessionPredicateState.PREDICATE_ADMITTED,
        possession_eligibility_state=wyscout_data.PossessionEligibilityState.ELIGIBLE_RESOLVED,
    )
    open_lineup, lineup_only_fact, lineup_only_gold = _open_lineup_fact_and_gold()
    _, precision_possession, precision_fact, precision_gold = _three_action_precision_fact()
    matrix: tuple[tuple[str, BaseModel], ...] = (
        *(("BRONZE_KNOWN_RECORD", row) for row in bronze_known),
        *(("BRONZE_REJECTED_RECORD", row) for row in bronze_rejected),
        *(("BRONZE_REJECTED_FIELD", row) for row in rejected_fields),
        ("SILVER_COMPETITION", competition),
        ("SILVER_TEAM", team),
        ("SILVER_PLAYER", player),
        ("SILVER_MATCH", match),
        ("SILVER_ACTION", null_unmapped_action),
        ("SILVER_ACTION", one_position_action),
        ("SILVER_ACTION", two_position_action),
        ("SILVER_LINEUP_STINT", closed_lineup),
        ("SILVER_LINEUP_STINT", open_lineup),
        ("SILVER_POSSESSION", base_possession),
        ("SILVER_POSSESSION", _equal_clock_survivor_possession()),
        ("SILVER_PLAYER_MATCH_FACT", precision_fact),
        ("SILVER_PLAYER_MATCH_FACT", lineup_only_fact),
        ("GOLD_PLAYER_WINDOW", precision_gold),
        ("GOLD_PLAYER_WINDOW", lineup_only_gold),
    )
    assert len(matrix) == 29
    assert (
        precision_possession.contributing_actions
        == precision_fact.contributing_possessions[0].contributing_actions
    )
    return matrix


def _project_model_value(
    field: WyscoutArrowProjectionField,
    python_value: object,
    json_value: object,
) -> object:
    if python_value is None:
        assert field.nullable
        assert json_value is None
        return None
    node = field.node
    if type(node) is WyscoutArrowScalarNode:
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8:
            return canonical_json_value_to_w04_arrow_utf8(
                cast(wyscout_data.CanonicalJsonValue, python_value)
            )
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8:
            return canonical_decimal_to_w04_arrow_utf8(python_value)
        if node.scalar_type in {
            WyscoutArrowScalarType.UTF8,
            WyscoutArrowScalarType.NULL,
        }:
            return json_value
        return python_value
    if type(node) is WyscoutArrowStructNode:
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.EXACT_DECIMAL128_WITH_EXPONENT:
            return exact_decimal128_with_exponent_to_w04_arrow(python_value)
        if isinstance(python_value, BaseModel):
            python_children = {
                child.name: getattr(python_value, child.name) for child in node.children
            }
        elif type(python_value) is dict:
            python_children = python_value
        else:
            assert type(python_value) in {tuple, list}
            python_sequence = cast(tuple[object, ...] | list[object], python_value)
            python_children = {
                child.name: python_sequence[cast(int, child.logical_position)]
                for child in node.children
            }
        if node.projection_kind is WyscoutLogicalArrowProjectionKind.POSITIONAL_TUPLE_STRUCT:
            assert type(json_value) is list
            json_children = {
                child.name: json_value[cast(int, child.logical_position)] for child in node.children
            }
        else:
            assert type(json_value) is dict
            json_children = json_value
        return {
            child.name: _project_model_value(
                child,
                cast(dict[str, object], python_children)[child.name],
                cast(dict[str, object], json_children)[child.name],
            )
            for child in node.children
        }
    assert type(node) is WyscoutArrowListNode
    assert type(python_value) in {tuple, list}
    assert type(json_value) is list
    python_sequence = cast(tuple[object, ...] | list[object], python_value)
    json_sequence = cast(list[object], json_value)
    return [
        _project_model_value(node.item, python_item, json_item)
        for python_item, json_item in zip(python_sequence, json_sequence, strict=True)
    ]


def _project_model(
    descriptor: WyscoutParquetProjectionDescriptor,
    model: BaseModel,
) -> tuple[dict[str, object], dict[str, object]]:
    python_row = {field_name: getattr(model, field_name) for field_name in type(model).model_fields}
    logical_row = model.model_dump(mode="json")
    return (
        {
            field.name: _project_model_value(
                field,
                python_row[field.name],
                logical_row[field.name],
            )
            for field in descriptor.fields
        },
        logical_row,
    )


def _model_registry() -> dict[str, type[BaseModel]]:
    result: dict[str, type[BaseModel]] = {}
    for module in (primitives, evidence, wyscout_data, wyscout_build):
        for value in vars(module).values():
            if inspect.isclass(value) and issubclass(value, BaseModel):
                result.setdefault(value.__name__, value)
    result.update((model.__name__, model) for model in ROOT_MODELS)
    return result


def _unwrap_operand_annotation(annotation: object) -> object:
    while isinstance(annotation, TypeAliasType):
        annotation = annotation.__value__
    while get_origin(annotation) is Annotated:
        annotation = get_args(annotation)[0]
    origin = get_origin(annotation)
    if origin in {Union, types.UnionType}:
        non_null = tuple(item for item in get_args(annotation) if item is not type(None))
        if len(non_null) == 1:
            return _unwrap_operand_annotation(non_null[0])
    return annotation


def _resolve_runtime_operand(model: type[BaseModel], operand: str) -> object:
    current: object = model
    for segment in operand.split("."):
        sequence = segment.endswith("[]")
        field_name = segment.removesuffix("[]")
        current = _unwrap_operand_annotation(current)
        assert inspect.isclass(current) and issubclass(current, BaseModel)
        assert field_name in current.model_fields
        current = _unwrap_operand_annotation(current.model_fields[field_name].annotation)
        if sequence:
            origin = get_origin(current)
            assert origin in {tuple, list}
            arguments = get_args(current)
            assert arguments
            current = _unwrap_operand_annotation(arguments[0])
    return current


def test_exact_23_root_content_row_rosters_and_acyclic_dependencies() -> None:
    contents = export_w04_implemented_schema_contents()
    rows = export_w04_implemented_schema_rows()
    assert len(contents) == len(rows) == 23
    assert tuple(content["root_role"] for content in contents) == W04_SCHEMA_ROOT_ROLES
    assert tuple(row["root_role"] for row in rows) == W04_SCHEMA_ROOT_ROLES
    for index, (content, row, role, dependency_roles, model) in enumerate(
        zip(
            contents,
            rows,
            W04_SCHEMA_ROOT_ROLES,
            EXPECTED_DEPENDENCY_ROLES,
            ROOT_MODELS,
            strict=True,
        )
    ):
        assert tuple(content) == W04_CANONICAL_CONTENT_KEY_ORDER
        assert tuple(row) == W04_IMPLEMENTED_ROW_KEY_ORDER
        schema_id = w04_canonical_schema_id(role)
        assert content["canonical_schema_id"] == row["canonical_schema_id"] == schema_id
        assert content["canonical_schema_version"] == W04_CANONICAL_SCHEMA_VERSION
        assert row["canonical_schema_version"] == W04_CANONICAL_SCHEMA_VERSION
        assert content["schema_language_version"] == W04_SCHEMA_LANGUAGE_VERSION
        assert content["root_definition_id"] == model.__name__
        assert row["surface_kind"] == W04_IMPLEMENTED_SCHEMA_SURFACE
        assert row["closure_dependencies"] == [
            w04_canonical_schema_id(dependency) for dependency in dependency_roles
        ]
        assert all(
            W04_SCHEMA_ROOT_ROLES.index(dependency) < index for dependency in dependency_roles
        )
        content_bytes = canonical_w04_schema_content_bytes(content)
        assert not content_bytes.endswith(b"\n")
        assert row["canonical_schema_content_sha256"] == hashlib.sha256(content_bytes).hexdigest()
    validate_w04_implemented_schema_exports(contents, rows)


def test_every_definition_reference_field_and_runtime_validator_is_closed() -> None:
    registry = _model_registry()
    for content, root_model in zip(
        export_w04_implemented_schema_contents(), ROOT_MODELS, strict=True
    ):
        definitions = cast(dict[str, object], content["definitions"])
        assert set(definitions) == {
            "constant_corpus",
            "definition_order",
            "external_authority_predicates",
            "predicate_constant_resolver",
            "schemas",
            "serialization_contract",
        }
        schemas = cast(dict[str, dict[str, object]], definitions["schemas"])
        definition_order = cast(list[str], definitions["definition_order"])
        assert len(definition_order) == len(set(definition_order)) == len(schemas)
        assert set(definition_order) == set(schemas)
        assert definition_order[0] == root_model.__name__
        for definition_id, schema in schemas.items():
            if "properties" in schema:
                properties = cast(dict[str, object], schema["properties"])
                assert set(cast(list[str], schema["serialized_field_order"])) == set(properties)
                assert schema["required"] == schema["serialized_field_order"]
                assert schema["additionalProperties"] is False
            if definition_id in registry:
                model = registry[definition_id]
                if "properties" in schema:
                    assert schema["serialized_field_order"] == list(model.model_fields)
                predicates = cast(list[dict[str, object]], schema["predicates"])
                assert len(predicates) == len(model.__pydantic_decorators__.model_validators)
                assert not model.__pydantic_decorators__.field_validators
                for predicate in predicates:
                    assert set(predicate) == {
                        "owner_model",
                        "declared_owner_model",
                        "validator_name",
                        "predicate_id",
                        "predicate_classification",
                        "authority_sources",
                        "operation",
                        "operands",
                        "constants",
                    }
                    assert predicate["predicate_classification"] == "RUNTIME_MODEL_VALIDATOR"
                    assert predicate["owner_model"] == model.__name__
                    assert type(predicate["declared_owner_model"]) is str
                    assert predicate["validator_name"] in (
                        model.__pydantic_decorators__.model_validators
                    )
                    assert predicate["authority_sources"] == []
                    assert type(predicate["operation"]) is str and predicate["operation"]
                    assert type(predicate["operands"]) is list and predicate["operands"]
                    assert type(predicate["constants"]) is list and predicate["constants"]
                    for operand in cast(list[str], predicate["operands"]):
                        _resolve_runtime_operand(model, operand)
        external = cast(list[dict[str, object]], definitions["external_authority_predicates"])
        assert [predicate["predicate_id"] for predicate in external] == [
            "E1-source-completion",
            "E2-season-and-lineup",
            "E3-checked-product-issuance",
            "E4-build-projection-composition",
            "E5-layer-semantic-closure",
            "E6-parent-and-population-closure",
            "E7-receipt-clocks-and-results",
            "E8-schema-acceptance",
        ]
        for predicate in external:
            assert set(predicate) == {
                "predicate_id",
                "predicate_classification",
                "authority_sources",
                "operation",
                "operands",
                "constants",
            }
            assert predicate["predicate_classification"] == "EXTERNAL_COMPOSED_AUTHORITY"
            assert type(predicate["authority_sources"]) is list and predicate["authority_sources"]
            assert type(predicate["operands"]) is list and predicate["operands"]
            assert type(predicate["constants"]) is dict
        refs: list[str] = []

        def collect(value: object) -> None:
            if type(value) is dict:
                for key, child in value.items():
                    if key == "$ref":
                        refs.append(cast(str, child))
                    else:
                        collect(child)
            elif type(value) is list:
                for child in value:
                    collect(child)

        collect(schemas)
        assert all(
            reference.startswith("#/$defs/") and reference.removeprefix("#/$defs/") in schemas
            for reference in refs
        )


_R5_RUNTIME_PREDICATE_ORACLE_JSONL = r"""
{"constants":["C1","C3"],"declared_owner":"BronzeKnownRecord","operation":"P01","operands":["raw_record","raw_record_sha256","source_row","lineage","measured_raw_fields","tenant_context","classification"],"owner":"BronzeKnownRecord","validator":"raw_record_is_preserved_once"}
{"constants":["L:U+D800..U+DFFF"],"declared_owner":"CanonicalJsonMember","operation":"P02","operands":["key"],"owner":"CanonicalJsonMember","validator":"key_is_unicode_scalar_text"}
{"constants":["L:finite Decimal"],"declared_owner":"CanonicalJsonNumber","operation":"P03","operands":["value"],"owner":"CanonicalJsonNumber","validator":"number_is_finite"}
{"constants":["L:Unicode lexical sort"],"declared_owner":"CanonicalJsonObject","operation":"P04","operands":["value"],"owner":"CanonicalJsonObject","validator":"members_are_unique_and_sorted"}
{"constants":["C8"],"declared_owner":"DependencyLineage","operation":"P05","operands":["dependencies"],"owner":"DependencyLineage","validator":"dependencies_are_unique"}
{"constants":["C3"],"declared_owner":"SourceUseClassification","operation":"P06","operands":["use_class","derived_data_allowed","internal_review_allowed","export_allowed","attribution_required","attribution_text"],"owner":"SourceUseClassification","validator":"prohibit_unlicensed_use"}
{"constants":["C3"],"declared_owner":"WyscoutAuthorityClock","operation":"P07","operands":["decided_at","reviewed_at","accepted_at","authority_kind"],"owner":"WyscoutAuthorityClock","validator":"clocks_are_the_accepted_authority_clocks"}
{"constants":["C3"],"declared_owner":"WyscoutAuthorityReference","operation":"P08","operands":["acceptance_id","acceptance_sha256","authority_kind","candidate_id","candidate_sha256","review_id","review_sha256"],"owner":"WyscoutAuthorityReference","validator":"reference_is_the_accepted_authority"}
{"constants":["C1","C3","C8"],"declared_owner":"WyscoutRowLineage","operation":"P09","operands":["source_manifest_id","source_manifest_sha256","source_completion_index_sha256","authority_references","authority_clocks","source_authority","source_rows","dependency_lineage"],"owner":"WyscoutRowLineage","validator":"lineage_is_closed"}
{"constants":["C1","C3"],"declared_owner":"WyscoutSourceAuthority","operation":"P10","operands":["source_manifest_id","source_manifest_sha256","tenant_context","available_at","acquired_at","classification"],"owner":"WyscoutSourceAuthority","validator":"source_authority_is_exact"}
{"constants":["C1","C2"],"declared_owner":"WyscoutRawSourceRowReference","operation":"P11","operands":["source_manifest_id","completion_relative_path","source_sha256","source_record_ordinal"],"owner":"WyscoutSourceRowReference","validator":"source_row_is_manifested"}
{"constants":["C2"],"declared_owner":"WyscoutSourceRowReference","operation":"P12","operands":["completion_relative_path","record_kind"],"owner":"WyscoutSourceRowReference","validator":"record_kind_matches_completion_path"}
{"constants":["C1","C3"],"declared_owner":"BronzeRejectedRecord","operation":"P13","operands":["raw_record_sha256","raw_record","tenant_context","classification","lineage","source_row"],"owner":"BronzeRejectedRecord","validator":"rejected_record_is_closed"}
{"constants":["L:w04-raw-kind-v1\\x00","L:uint64-be","L:^[A-Za-z][A-Za-z0-9_-]{0,63}$"],"declared_owner":"RawKindEvidence","operation":"P14","operands":["value_present","value","raw_kind_state","envelope_bytes","raw_kind_sha256"],"owner":"RawKindEvidence","validator":"evidence_matches_state_and_framed_digest"}
{"constants":["C1","C2"],"declared_owner":"WyscoutRawSourceRowReference","operation":"P15","operands":["source_manifest_id","completion_relative_path","source_sha256","source_record_ordinal"],"owner":"WyscoutRawSourceRowReference","validator":"source_row_is_manifested"}
{"constants":["C1","C3","C4","C5","C6"],"declared_owner":"BronzeRejectedField","operation":"P16","operands":["source_row","record_kind","original_value","measured_json_type","original_value_sha256","field_authority","json_path","decision","reason_code","action_event_taxonomy_id","classification","tenant_context","lineage"],"owner":"BronzeRejectedField","validator":"rejected_value_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P17","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverCompetition","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(competition)"],"declared_owner":"SilverCompetition","operation":"P18","operands":["source_rows","competition_id","competition_source_id"],"owner":"SilverCompetition","validator":"competition_identity_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P19","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverTeam","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(team)"],"declared_owner":"SilverTeam","operation":"P20","operands":["source_rows","team_id","team_source_id"],"owner":"SilverTeam","validator":"team_identity_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P21","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPlayer","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(player)"],"declared_owner":"SilverPlayer","operation":"P22","operands":["source_rows","player_id","player_source_id"],"owner":"SilverPlayer","validator":"player_identity_is_exact_and_nonzero"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P23","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverMatch","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C2","L:canonical_source_uuid(match)","L:UUID.bytes sort"],"declared_owner":"SilverMatch","operation":"P24","operands":["source_rows","source_partition","match_id","match_source_id","team_ids"],"owner":"SilverMatch","validator":"match_identity_and_teams_are_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P25","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverAction","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C5","C6","L:decimal128(22,18)"],"declared_owner":"SilverAction","operation":"P26","operands":["source_rows","action_id","action_source_id","source_event_record_id","source_record_ordinal","period_elapsed_seconds","event_sec_source_scale","action_tag_ids","action_subevent_taxonomy_id","action_event_taxonomy_id","team_id","possession_predicate_state","possession_period_sequence","match_id","action_period_code","lineage","player_id","period_rank","possession_eligibility_state"],"owner":"SilverAction","validator":"action_is_strict_and_orderable"}
{"constants":["L:decimal128(22,18)","L:[0,100]"],"declared_owner":"ActionPosition","operation":"P27","operands":["x","y","within_accepted_bounds"],"owner":"ActionPosition","validator":"bound_flag_preserves_anomalies_without_clamping"}
{"constants":["C1"],"declared_owner":"PossessionPeriodSequence","operation":"P28","operands":["source_completion_index_sha256","period_action_count","actions","match_id","action_period_code"],"owner":"PossessionPeriodSequence","validator":"period_sequence_is_complete_unique_and_ordered"}
{"constants":["L:canonical_source_uuid(action)","L:canonical action order"],"declared_owner":"PossessionSequenceAction","operation":"P29","operands":["source_row","source_record_ordinal","action_id","source_event_record_id","period_elapsed_seconds","action_tag_ids"],"owner":"PossessionSequenceAction","validator":"sequence_action_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P30","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverLineupStint","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:half-open nominal minute"],"declared_owner":"SilverLineupStint","operation":"P31","operands":["source_rows","start_interval","end_interval","right_censored","lower_bound_minutes","upper_bound_minutes"],"owner":"SilverLineupStint","validator":"stint_bounds_are_interval_derived"}
{"constants":["L:upper=lower+1"],"declared_owner":"NominalMinuteInterval","operation":"P32","operands":["upper","lower"],"owner":"NominalMinuteInterval","validator":"interval_is_one_nominal_minute"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P33","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPossession","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C5","C6","L:equal-clock group-first"],"declared_owner":"SilverPossession","operation":"P34","operands":["contributing_actions","team_id","build_id","tenant_context","lineage","match_id","action_period_code","source_rows","action_ids","first_action_order","last_action_order"],"owner":"SilverPossession","validator":"possession_is_one_ordered_same_period_sequence"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P35","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPlayerMatchFact","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C8","L:fact derivations"],"declared_owner":"SilverPlayerMatchFact","operation":"P36","operands":["source_manifest_id","contributing_lineup_stints","build_id","tenant_context","lineage","match_id","player_id","match_team_id","lineup_evidence_present","contributing_actions","competition_id","contributing_possessions","source_rows","action_count","coordinate_known_action_count","resolved_possession_action_count","temporal_proof","match_start_utc","coverage","right_censored_or_uncertain","applicability"],"owner":"SilverPlayerMatchFact","validator":"player_match_key_and_state_are_exact"}
{"constants":["L:six CoverageDimensionName values"],"declared_owner":"GoldCoverage","operation":"P37","operands":["dimensions","missing_dimensions","coverage_overall"],"owner":"GoldCoverage","validator":"six_dimensions_are_exact"}
{"constants":["C3","L:precision-38 exact division"],"declared_owner":"GoldCoverageDimension","operation":"P38","operands":["numerator","denominator","reason_codes","state","coverage","zero_denominator_authority","name"],"owner":"GoldCoverageDimension","validator":"coverage_is_exact"}
{"constants":["L:W04_DATA_READY"],"declared_owner":"W04ApplicabilityAssessment","operation":"P39","operands":["reason_codes","state"],"owner":"W04ApplicabilityAssessment","validator":"reasons_are_sorted_unique"}
{"constants":["C1","C3","C8","C10"],"declared_owner":"W04SemanticTemporalProof","operation":"P40","operands":["dependency_lineage","source_completion_index_sha256","source_authority","authority_clocks","feature_cutoff_ts","available_at_watermark","valid_from_ts","snapshot_as_of_ts","dependency_lineage_hash","source_manifest_ids","feature_schema_hash"],"owner":"W04SemanticTemporalProof","validator":"proof_has_exact_five_strict_dependencies"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P41","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"GoldPlayerWindow","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C8","C10","L:four-feature sums"],"declared_owner":"GoldPlayerWindow","operation":"P42","operands":["role_context_id","role_context_version","role_context_state","window_start_utc","window_end_utc","feature_cutoff_ts","temporal_proof","dependency_lineage_hash","lineage","feature_schema_hash","contributing_player_match_facts","contributing_player_match_keys","build_id","tenant_context","player_id","competition_id","season_id","source_rows","features","coverage","applicability"],"owner":"GoldPlayerWindow","validator":"gold_key_and_feature_state_are_exact"}
{"constants":["L:component<=action"],"declared_owner":"GoldFeatureValues","operation":"P43","operands":["coordinate_known_action_count","action_count","resolved_possession_action_count"],"owner":"GoldFeatureValues","validator":"component_counts_cannot_exceed_actions"}
{"constants":["C1","C3","C8","C10"],"declared_owner":"LayerManifest","operation":"P44","operands":["manifest_path","layer","source_manifest_id","source_manifest_sha256","source_completion_index_sha256","build_id","tenant_context","classification","source_available_at","source_acquired_at","authority_clocks","feature_schema_hash","dependency_lineage","dependency_lineage_hash","entries","parent_layer_manifests"],"owner":"LayerManifest","validator":"layer_order_and_entries_are_exact"}
{"constants":["C3","C10"],"declared_owner":"LayerManifestEntry","operation":"P45","operands":["serializer","path","schema_role","partition_values","classification","ordered_parent_paths"],"owner":"LayerManifestEntry","validator":"entry_binds_owner_rights_and_partition_order"}
{"constants":["C10"],"declared_owner":"ParentLayerManifest","operation":"P46","operands":["layer","build_id","relative_path"],"owner":"ParentLayerManifest","validator":"parent_path_is_exact_and_safe"}
{"constants":["C10","L:NFC","L:canonical UUID/UTC"],"declared_owner":"WyscoutProductPath","operation":"P47","operands":["relative_path","path_role"],"owner":"WyscoutProductPath","validator":"path_is_the_exact_role_template"}
{"constants":["C10","L:SHA256(path UTF-8)"],"declared_owner":"TemporalBoundaryReceipt","operation":"P48","operands":["gold_manifest_relative_path","gold_product_relative_path","build_id","gold_relative_path_sha256"],"owner":"TemporalBoundaryReceipt","validator":"exact_paths"}
{"constants":["C10","C11"],"declared_owner":"RebuildInvocationReceipt","operation":"P49","operands":["build_id","rebuild_invocation","started_at","completed_at","layer_manifests","boundary_receipts","run_id"],"owner":"RebuildInvocationReceipt","validator":"exact_receipt"}
{"constants":["C3"],"declared_owner":"AuthorityRow","operation":"P50","operands":["acceptance_id","acceptance_sha256","authority_kind","candidate_id","candidate_sha256","review_id","review_sha256"],"owner":"AuthorityRow","validator":"equals_accepted_row"}
{"constants":["C8"],"declared_owner":"DependencyRow","operation":"P51","operands":["observed_at","available_at"],"owner":"DependencyRow","validator":"clocks_are_ordered"}
{"constants":["C3","C8","C10","L:single build hash"],"declared_owner":"RebuildInvocation","operation":"P52","operands":["authority_rows","dependency_rows","code_manifest_id","code_manifest_sha256","product_contract_digest","schema_bundle_digest","build_id"],"owner":"RebuildInvocation","validator":"exact_invocation"}
{"constants":["C10"],"declared_owner":"EntrypointSourceResult","operation":"P53","operands":["role","relative_path"],"owner":"EntrypointSourceResult","validator":"exact_role_path"}
{"constants":["C10","L:SHA256 canonical JSON","L:base64url"],"declared_owner":"PreBuildAdmissionResult","operation":"P54","operands":["admission_run_id","admission_prefix_relative_path","component_proofs","component_proofs_sha256","canonical_manifest_bytes_b64u","canonical_manifest_sha256","manifest_schema_version","repository_code_sha256","environment_digest"],"owner":"PreBuildAdmissionResult","validator":"exact_admission_result"}
{"constants":["C10","C11","L:SHA256 canonical JSON"],"declared_owner":"PostBuildIdRebuildResult","operation":"P55","operands":["build_id","run_id","rebuild_prefix_relative_path","rebuild_receipt","layer_manifests","final_recheck"],"owner":"PostBuildIdRebuildResult","validator":"exact_rebuild_result"}
{"constants":["C10","L:SHA256 ordered argv"],"declared_owner":"ChildResultEnvelope","operation":"P56","operands":["entrypoint_source","child_role","payload_kind","result","expected_repository_code_sha256","child_environment_sha256","ordered_argv_sha256"],"owner":"ChildResultEnvelope","validator":"exact_role_payload_binding"}
{"constants":["L:NFC without controls","L:safe root-independent non-PYC site path","L:strict sys.modules key or DYLD_IMAGE"],"declared_owner":"RuntimeSubsetObservation","operation":"P57","operands":["owner_version","site_relative_path","observation_kind","subject_name"],"owner":"RuntimeSubsetObservation","validator":"exact_runtime_observation"}
{"constants":["L:w04-normalized-runtime-subset-observations-v1","L:canonical-byte sorted unique cardinality 1..100000","L:SHA256 canonical JSON and nonempty owner projection"],"declared_owner":"FinalRecheckResult","operation":"P58","operands":["runtime_subset_rows","runtime_subset_digest"],"owner":"FinalRecheckResult","validator":"exact_runtime_subset"}
""".removeprefix("\n")
_R5_RUNTIME_PREDICATE_ORACLE_SHA256 = (
    "5a787de72cdad220a6e609c9ca713df33830e4afa7845b4b2e5de3df87d57d2b"
)


def _load_r5_runtime_predicate_oracle() -> tuple[dict[str, object], ...]:
    encoded = _R5_RUNTIME_PREDICATE_ORACLE_JSONL.encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == _R5_RUNTIME_PREDICATE_ORACLE_SHA256
    rows = tuple(json.loads(line) for line in _R5_RUNTIME_PREDICATE_ORACLE_JSONL.splitlines())
    assert len(rows) == 58
    assert [row["operation"] for row in rows] == [f"P{index:02d}" for index in range(1, 59)]
    assert all(
        tuple(row)
        == (
            "constants",
            "declared_owner",
            "operation",
            "operands",
            "owner",
            "validator",
        )
        for row in rows
    )
    assert len({(row["owner"], row["validator"]) for row in rows}) == 58
    return cast(tuple[dict[str, object], ...], rows)


_R5_RUNTIME_PREDICATE_ORACLE = _load_r5_runtime_predicate_oracle()


def _direct_validator_field_reads(model: type[BaseModel], validator_name: str) -> set[str]:
    function = model.__pydantic_decorators__.model_validators[validator_name].func
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    fields = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
        and node.attr in model.model_fields
    }
    if any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
        and node.func.attr == "model_dump"
        for node in ast.walk(tree)
    ):
        fields.update(model.model_fields)
    return fields


def test_independent_runtime_and_external_expected_ledgers_are_exact() -> None:
    contents = export_w04_implemented_schema_contents()
    runtime_by_owner_validator: dict[tuple[str, str], dict[str, object]] = {}
    for content in contents:
        definitions = cast(dict[str, object], content["definitions"])
        schemas = cast(dict[str, dict[str, object]], definitions["schemas"])
        for schema in schemas.values():
            for predicate in cast(list[dict[str, object]], schema.get("predicates", [])):
                key = (cast(str, predicate["owner_model"]), cast(str, predicate["validator_name"]))
                if key in runtime_by_owner_validator:
                    assert runtime_by_owner_validator[key] == predicate
                runtime_by_owner_validator[key] = predicate

    expected_keys = [
        (cast(str, row["owner"]), cast(str, row["validator"]))
        for row in _R5_RUNTIME_PREDICATE_ORACLE
    ]
    assert len(runtime_by_owner_validator) == len(expected_keys) == 58
    assert set(runtime_by_owner_validator) == set(expected_keys)
    registry = _model_registry()
    normalized_rows: list[dict[str, object]] = []
    for oracle_row, key in zip(_R5_RUNTIME_PREDICATE_ORACLE, expected_keys, strict=True):
        predicate = runtime_by_owner_validator[key]
        normalized = {
            "constants": predicate["constants"],
            "declared_owner": predicate["declared_owner_model"],
            "operation": predicate["operation"],
            "operands": predicate["operands"],
            "owner": predicate["owner_model"],
            "validator": predicate["validator_name"],
        }
        assert normalized == oracle_row
        normalized_rows.append(normalized)
        assert predicate["predicate_classification"] == "RUNTIME_MODEL_VALIDATOR"
        assert predicate["authority_sources"] == []

        owner, validator_name = key
        declared_owner = next(
            candidate.__name__
            for candidate in registry[owner].__mro__
            if validator_name in candidate.__dict__
        )
        assert predicate["declared_owner_model"] == declared_owner
        operands = cast(list[str], predicate["operands"])
        direct_fields = _direct_validator_field_reads(registry[owner], validator_name)
        operand_roots = {operand.split(".")[0].removesuffix("[]") for operand in operands}
        assert direct_fields <= operand_roots, (
            owner,
            validator_name,
            sorted(direct_fields - operand_roots),
        )

    normalized_jsonl = b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in normalized_rows
    )
    assert normalized_jsonl == _R5_RUNTIME_PREDICATE_ORACLE_JSONL.encode("utf-8")
    assert hashlib.sha256(normalized_jsonl).hexdigest() == _R5_RUNTIME_PREDICATE_ORACLE_SHA256

    root_definitions = cast(dict[str, object], contents[0]["definitions"])
    external = cast(list[dict[str, object]], root_definitions["external_authority_predicates"])
    assert (
        hashlib.sha256(
            json.dumps(external, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        == "516b15112f8412048fcc1df0b8ef78fb0604944452f5c0327ca0bfbfe9cbd438"
    )

    resolvers = [
        cast(
            dict[str, object],
            cast(dict[str, object], content["definitions"])["predicate_constant_resolver"],
        )
        for content in contents
    ]
    assert all(resolver == resolvers[0] for resolver in resolvers)
    resolver = resolvers[0]
    expected_constant_refs = {f"C{index}" for index in range(1, 12)}
    assert set(resolver) == expected_constant_refs
    referenced: set[str] = set()
    for row in _R5_RUNTIME_PREDICATE_ORACLE:
        constants = cast(list[str], row["constants"])
        assert len(constants) == len(set(constants))
        constant_refs = [constant for constant in constants if constant.startswith("C")]
        literals = [constant for constant in constants if constant.startswith("L:")]
        assert constants == constant_refs + literals
        assert constant_refs == sorted(constant_refs, key=lambda value: int(value[1:]))
        assert len(constant_refs) + len(literals) == len(constants)
        assert set(constant_refs) <= expected_constant_refs
        assert all(len(literal) > 2 for literal in literals)
        referenced.update(constant_refs)
    for reference, material in resolver.items():
        if any(material == predicate["constants"] for predicate in external):
            referenced.add(reference)
    assert referenced == expected_constant_refs
    assert all(type(material) in {dict, list} and material for material in resolver.values())

    corpus = cast(dict[str, object], root_definitions["constant_corpus"])
    c1 = cast(dict[str, object], resolver["C1"])
    assert c1 == {
        "feature_schema_hash": wyscout_data.FEATURE_SCHEMA_HASH,
        "identity_bundle_id": wyscout_build.IDENTITY_BUNDLE_ID,
        "identity_bundle_sha256": wyscout_build.IDENTITY_BUNDLE_SHA256,
        "source_completion_index_sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
        "source_manifest_id": str(wyscout_data.SOURCE_MANIFEST_ID),
        "source_manifest_sha256": wyscout_data.SOURCE_MANIFEST_SHA256,
        "tenant_context": {
            "club_id": None,
            "tenant_id": str(wyscout_data.TENANT_ID),
        },
    }
    assert resolver["C2"] == corpus["source_members"]
    c3 = cast(dict[str, object], resolver["C3"])
    assert c3["data_authority_rows"] == [
        row.model_dump(mode="json") for row in wyscout_data.accepted_authority_references()
    ]
    assert c3["data_authority_clocks"] == [
        row.model_dump(mode="json") for row in wyscout_data.accepted_authority_clocks()
    ]
    assert c3["build_authority_rows"] == [
        row.model_dump(mode="json") for row in wyscout_build.accepted_authority_rows()
    ]
    assert c3["source_classification"] == (
        wyscout_data.accepted_source_classification().model_dump(mode="json")
    )
    assert resolver["C4"] == corpus["field_registry"]
    assert resolver["C5"] == {
        "admitted_event_subevent_pairs": [
            list(pair) for pair in sorted(wyscout_data._ADMITTED_EVENT_SUBEVENT_PAIRS)
        ]
    }
    c6 = cast(dict[str, object], resolver["C6"])
    assert c6 == {
        "possession_semantics": corpus["possession_semantics"],
        "subevent_quarantine_reasons": {
            member.name: member.value for member in wyscout_data.ActionSubeventReason
        },
    }
    assert resolver["C7"] == corpus["completion_index_binding"]
    assert resolver["C8"] == {
        "dependency_lineage_hash": wyscout_build.accepted_dependency_lineage_hash(),
        "dependency_rows": [
            row.model_dump(mode="json") for row in wyscout_build.accepted_dependency_rows()
        ],
    }
    assert resolver["C9"] == corpus["season_and_lineup"]
    c10 = cast(dict[str, object], resolver["C10"])
    assert c10 == {
        "admission_argv": list(wyscout_build.ADMISSION_ARGV),
        "build_identity": corpus["build_identity"],
        "component_keys": list(wyscout_build.COMPONENT_KEYS),
        "layer_manifest_authority": corpus["layer_manifest_authority"],
        "post_hash_invocation_keys": list(wyscout_build.POST_HASH_INVOCATION_KEYS),
        "pre_build_projection_keys": list(wyscout_build.PRE_BUILD_PROJECTION_KEYS),
        "rebuild_argv": list(wyscout_build.REBUILD_ARGV),
        "stable_manifest_keys": list(wyscout_build._STABLE_MANIFEST_KEYS),
        "window_authority": corpus["window_authority"],
    }
    assert resolver["C11"] == {
        "layer_manifest_receipt_composition": corpus["layer_manifest_receipt_composition"],
        "receipt_contracts": corpus["receipt_contracts"],
    }


@pytest.mark.parametrize(
    "mutation",
    ["missing_material", "unused_material", "reordered_constants", "duplicate_constant"],
)
def test_predicate_constant_resolver_and_ledger_mutations_fail_closed(mutation: str) -> None:
    contents = list(deepcopy(export_w04_implemented_schema_contents()))
    rows = export_w04_implemented_schema_rows()
    definitions = cast(dict[str, object], contents[0]["definitions"])
    if mutation in {"missing_material", "unused_material"}:
        resolver = cast(dict[str, object], definitions["predicate_constant_resolver"])
        if mutation == "missing_material":
            resolver.pop("C11")
        else:
            resolver["C12"] = {"unexpected": True}
    else:
        schemas = cast(dict[str, dict[str, object]], definitions["schemas"])
        schema = next(schema for schema in schemas.values() if schema.get("predicates"))
        predicate = cast(list[dict[str, object]], schema["predicates"])[0]
        constants = cast(list[str], predicate["constants"])
        if mutation == "reordered_constants":
            constants.reverse()
        else:
            constants.append(constants[0])
    with pytest.raises(W04SchemaClosureError):
        validate_w04_implemented_schema_exports(tuple(contents), rows)


def test_frozen_constant_corpus_reproduces_contracts_authorities_and_composed_inputs() -> None:
    contents = export_w04_implemented_schema_contents()
    corpora = [
        cast(dict[str, object], content["definitions"])["constant_corpus"] for content in contents
    ]
    assert all(corpus == corpora[0] for corpus in corpora)
    corpus = cast(dict[str, object], corpora[0])
    assert set(corpus) == {
        "authority_composition",
        "build_identity",
        "completion_index",
        "completion_index_binding",
        "dependency_rows",
        "field_registry",
        "layer_manifest_authority",
        "layer_manifest_receipt_composition",
        "possession_semantics",
        "receipt_contracts",
        "season_and_lineup",
        "source_authority",
        "source_members",
        "subevent_semantics",
        "window_authority",
    }

    source_members = [
        {
            "completion_relative_path": path,
            "country_partition": country.value if country is not None else None,
            "record_kind": record_kind.value,
            "row_count": row_count,
            "source_sha256": source_sha256,
        }
        for path, (record_kind, source_sha256, country, row_count) in sorted(
            wyscout_data._SOURCE_PATH_ROWS.items()
        )
    ]
    assert corpus["source_members"] == source_members
    assert corpus["source_authority"] == wyscout_data.accepted_source_authority().model_dump(
        mode="json"
    )

    authority = cast(dict[str, object], corpus["authority_composition"])
    assert authority["data_authority_rows"] == [
        row.model_dump(mode="json") for row in wyscout_data.accepted_authority_references()
    ]
    assert authority["data_authority_clocks"] == [
        row.model_dump(mode="json") for row in wyscout_data.accepted_authority_clocks()
    ]
    assert authority["build_authority_rows"] == [
        row.model_dump(mode="json") for row in wyscout_build.accepted_authority_rows()
    ]
    assert (
        authority["data_authority_row_count"],
        authority["data_authority_clock_count"],
        authority["build_authority_row_count"],
    ) == (4, 4, 5)
    assert corpus["dependency_rows"] == [
        row.model_dump(mode="json") for row in wyscout_build.accepted_dependency_rows()
    ]

    expected_registry = []
    for text in wyscout_data._FIELD_REGISTRY_ROWS_TEXT.splitlines():
        record_kind, json_path, decision, kinds = text.split("|")
        expected_registry.append(
            {
                "admitted_json_kinds": kinds.split(","),
                "decision": decision,
                "json_path": json_path,
                "record_kind": record_kind,
            }
        )
    field_registry = cast(dict[str, object], corpus["field_registry"])
    assert field_registry == {
        "acceptance_sha256": wyscout_data.FIELD_ACCEPTANCE_SHA256,
        "candidate_sha256": wyscout_data.FIELD_CANDIDATE_SHA256,
        "review_sha256": "76c4744d302b4c6d86f4d537498695e365f0d3c733211bfafcb1e5c2805c0886",
        "row_count": 119,
        "rows": expected_registry,
    }

    subevent = cast(dict[str, object], corpus["subevent_semantics"])
    assert subevent["admitted_integer_pairs"] == [
        list(pair) for pair in sorted(wyscout_data._ADMITTED_EVENT_SUBEVENT_PAIRS)
    ]
    assert subevent["quarantine_reasons_by_union_arm"] == {
        member.name: member.value for member in wyscout_data.ActionSubeventReason
    }
    assert subevent["emitting_runtime_type"] == "exact_int_excluding_bool"
    assert subevent["coercion_permitted"] is False
    assert subevent["strings_remain_unmapped"] is True

    possession = cast(dict[str, object], corpus["possession_semantics"])
    for key, values in (
        ("contested_pairs", wyscout_data._CONTESTED_PAIRS),
        ("dead_ball_preceding_pairs", wyscout_data._DEAD_BALL_PRECEDING_PAIRS),
        ("dead_ball_unassigned_pairs", wyscout_data._DEAD_BALL_UNASSIGNED_PAIRS),
        ("non_control_admin_pairs", wyscout_data._NON_CONTROL_ADMIN_PAIRS),
        ("explicit_unmapped_pairs", wyscout_data._EXPLICIT_UNMAPPED_PAIRS),
        ("restart_pairs", wyscout_data._RESTART_PAIRS),
        ("control_pairs", wyscout_data._CONTROL_PAIRS),
    ):
        assert possession[key] == [list(pair) for pair in sorted(values)]
    assert cast(dict[str, object], possession["equal_clock"])["resolution_order"] == ("group-first")

    completion = cast(dict[str, object], corpus["completion_index"])
    assert completion["content_sha256"] == wyscout_data.SOURCE_COMPLETION_INDEX_SHA256
    assert completion["source_manifest_id"] == str(wyscout_data.SOURCE_MANIFEST_ID)
    assert completion["source_manifest_sha256"] == wyscout_data.SOURCE_MANIFEST_SHA256
    assert completion["aggregate_action_count"] == 3_071_395
    periods = cast(dict[str, object], completion["one_match_scope"])["periods"]
    assert periods == [
        {
            "action_count": 901,
            "action_period_code": "1H",
            "membership_sha256": (
                "473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b"
            ),
            "period_rank": 1,
        },
        {
            "action_count": 867,
            "action_period_code": "2H",
            "membership_sha256": (
                "b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16"
            ),
            "period_rank": 2,
        },
    ]

    root = Path(__file__).resolve().parents[2]
    build_authority = json.loads(
        (
            root
            / "reports/reviews/W04/authorities/wyscout-build-product-authority-decisions-v1.json"
        ).read_text(encoding="utf-8")
    )
    assert type(build_authority) is dict
    for key in (
        "completion_index_binding",
        "build_identity",
        "window_authority",
        "layer_manifest_authority",
        "receipt_contracts",
    ):
        assert corpus[key] == build_authority[key]

    season_authority = json.loads(
        (
            root / "reports/reviews/W04/authorities/"
            "wyscout-season-lineup-product-binding-decisions-v1.json"
        ).read_text(encoding="utf-8")
    )
    assert type(season_authority) is dict
    season_lineup = cast(dict[str, object], corpus["season_and_lineup"])
    for key in (
        "source_binding",
        "season_binding",
        "lineup_population",
        "build_projection_binding",
    ):
        assert season_lineup[key] == season_authority[key]
    assert "1cc084583a48055142846f4ee09ce4b5490db93ba26b30dc459c6f81373d4d86" not in json.dumps(
        corpus, sort_keys=True
    )
    assert (
        cast(dict[str, object], season_lineup["source_binding"])["match_raw_record_sha256"]
        == "1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86"
    )

    receipt = cast(dict[str, object], corpus["layer_manifest_receipt_composition"])
    semantic = cast(dict[str, object], receipt["complete_layer_manifest_semantic"])
    assert semantic["wrapper_exact_key_order"] == [
        "layer_manifest",
        "semantic_schema_version",
    ]
    assert semantic["wrapper_fixed_member"] == {
        "semantic_schema_version": "w04-wyscout-layer-manifest-semantic-v1"
    }
    assert receipt["layer_order"] == ["BRONZE", "SILVER", "GOLD"]
    assert receipt["operational_clock_relation"] == "started_at<=checked_at<=completed_at"

    root_definitions = cast(dict[str, object], contents[0]["definitions"])
    external = cast(list[dict[str, object]], root_definitions["external_authority_predicates"])
    for predicate in external:
        for source in cast(list[dict[str, str]], predicate["authority_sources"]):
            assert (
                hashlib.sha256((root / source["path"]).read_bytes()).hexdigest() == source["sha256"]
            )


@pytest.mark.parametrize(
    ("corpus_key", "replacement"),
    [
        ("source_members", "FROZEN_SOURCE_MEMBER_MAP"),
        ("field_registry", {"row_count": 119}),
        ("subevent_semantics", "STRICT_INTEGER_MAPPING"),
        ("completion_index", {"content_sha256": "0" * 64}),
        ("season_and_lineup", "EXACT_POC_POPULATION"),
        ("layer_manifest_receipt_composition", "R4_RECEIPT_CLOSURE"),
    ],
)
def test_frozen_constant_placeholder_or_partial_substitution_fails_closed(
    corpus_key: str,
    replacement: object,
) -> None:
    contents = list(deepcopy(export_w04_implemented_schema_contents()))
    rows = export_w04_implemented_schema_rows()
    definitions = cast(dict[str, object], contents[0]["definitions"])
    corpus = cast(dict[str, object], definitions["constant_corpus"])
    corpus[corpus_key] = replacement
    with pytest.raises(W04SchemaClosureError):
        validate_w04_implemented_schema_exports(tuple(contents), rows)


def test_all_twelve_descriptors_mechanically_generate_exact_metadata_free_schemas() -> None:
    tagged_paths: list[str] = []
    canonical_decimal_paths: list[str] = []
    decimal128_paths: list[str] = []
    exact_decimal_paths: list[str] = []
    for role, model in zip(W04_SCHEMA_ROOT_ROLES[:12], ROOT_MODELS[:12], strict=True):
        descriptor = _instantiate_descriptor(role)
        tagged_paths.extend(_tagged_scalar_paths(descriptor.fields, prefix=role))
        canonical_decimal_paths.extend(
            _scalar_projection_paths(
                descriptor.fields,
                prefix=role,
                projection_kind=WyscoutLogicalArrowProjectionKind.CANONICAL_DECIMAL_UTF8,
            )
        )
        decimal128_paths.extend(_decimal128_paths(descriptor.fields, prefix=role))
        exact_decimal_paths.extend(_exact_decimal_paths(descriptor.fields, prefix=role))
        assert descriptor.schema_role == w04_canonical_schema_id(role)
        assert tuple(field.name for field in descriptor.fields) == tuple(model.model_fields)
        schema = arrow_schema_from_w04_projection(descriptor)
        assert schema.metadata is None
        assert tuple(schema.names) == tuple(model.model_fields)
        for field in schema:
            assert field.metadata is None
            _assert_metadata_absent(field.type)

    assert tagged_paths == [
        "BRONZE_KNOWN_RECORD.raw_record",
        "BRONZE_REJECTED_RECORD.raw_record",
        "BRONZE_REJECTED_RECORD.raw_kind.value",
        "BRONZE_REJECTED_FIELD.original_value",
    ]
    assert canonical_decimal_paths == [
        "SILVER_PLAYER_MATCH_FACT.coverage.dimensions[].item.coverage",
        "SILVER_PLAYER_MATCH_FACT.coverage.coverage_overall",
        "GOLD_PLAYER_WINDOW.coverage.dimensions[].item.coverage",
        "GOLD_PLAYER_WINDOW.coverage.coverage_overall",
        (
            "GOLD_PLAYER_WINDOW.contributing_player_match_facts[].item.coverage."
            "dimensions[].item.coverage"
        ),
        ("GOLD_PLAYER_WINDOW.contributing_player_match_facts[].item.coverage.coverage_overall"),
    ]
    assert decimal128_paths
    assert len(decimal128_paths) == len(exact_decimal_paths) == 30
    assert all(path.endswith(".value") for path in decimal128_paths)
    assert all(".coverage" not in path for path in exact_decimal_paths)
    assert any(path.endswith("period_elapsed_seconds") for path in exact_decimal_paths)
    assert any(path.endswith("action_positions[].item.x") for path in exact_decimal_paths)
    assert any(path.endswith("first_action_order.position_1") for path in exact_decimal_paths)

    bronze = _instantiate_descriptor("BRONZE_KNOWN_RECORD")
    raw_record = next(field for field in bronze.fields if field.name == "raw_record")
    assert type(raw_record.node) is WyscoutArrowScalarNode
    assert (
        raw_record.node.projection_kind
        is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8
    )
    rejected = _instantiate_descriptor("BRONZE_REJECTED_RECORD")
    raw_kind = next(field for field in rejected.fields if field.name == "raw_kind")
    assert type(raw_kind.node) is WyscoutArrowStructNode
    raw_kind_value = next(field for field in raw_kind.node.children if field.name == "value")
    assert type(raw_kind_value.node) is WyscoutArrowScalarNode
    assert (
        raw_kind_value.node.projection_kind
        is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8
    )
    rejected_field = _instantiate_descriptor("BRONZE_REJECTED_FIELD")
    original = next(field for field in rejected_field.fields if field.name == "original_value")
    assert type(original.node) is WyscoutArrowScalarNode
    assert (
        original.node.projection_kind is WyscoutLogicalArrowProjectionKind.CANONICAL_JSON_VALUE_UTF8
    )

    match_schema = arrow_schema_from_w04_projection(_instantiate_descriptor("SILVER_MATCH"))
    assert match_schema.field("match_start_utc").type == pa.timestamp("us", tz="UTC")
    assert match_schema.field("team_ids").type == pa.list_(
        pa.field("item", pa.string(), nullable=False), 2
    )
    action_schema = arrow_schema_from_w04_projection(_instantiate_descriptor("SILVER_ACTION"))
    assert action_schema.field("period_elapsed_seconds").type == pa.struct(
        [
            pa.field("value", pa.decimal128(22, 18), nullable=False),
            pa.field("exponent", pa.int8(), nullable=False),
            pa.field("negative_zero", pa.bool_(), nullable=False),
        ]
    )


def test_all_twelve_physical_primary_key_path_rosters_are_exact_descriptor_owned() -> None:
    assert tuple(EXPECTED_PHYSICAL_PRIMARY_KEY_PATHS) == W04_SCHEMA_ROOT_ROLES[:12]
    projected_scalar_types = {
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
    for role in W04_SCHEMA_ROOT_ROLES[:12]:
        paths = w04_physical_primary_key_paths(role)
        assert paths == EXPECTED_PHYSICAL_PRIMARY_KEY_PATHS[role]
        assert paths and len(paths) == len(set(paths))
        descriptor = _instantiate_descriptor(role)
        schema = arrow_schema_from_w04_projection(descriptor)
        for path in paths:
            descriptor_fields = descriptor.fields
            arrow_fields = tuple(schema)
            for path_index, segment in enumerate(path):
                descriptor_field = next(
                    field for field in descriptor_fields if field.name == segment
                )
                arrow_field = next(field for field in arrow_fields if field.name == segment)
                assert descriptor_field.nullable is False
                assert arrow_field.nullable is False
                if path_index < len(path) - 1:
                    assert type(descriptor_field.node) is WyscoutArrowStructNode
                    assert (
                        descriptor_field.node.projection_kind
                        is WyscoutLogicalArrowProjectionKind.OBJECT_STRUCT
                    )
                    assert pa.types.is_struct(arrow_field.type)
                    descriptor_fields = descriptor_field.node.children
                    arrow_fields = tuple(arrow_field.type)
                else:
                    assert type(descriptor_field.node) is WyscoutArrowScalarNode
                    assert (
                        descriptor_field.node.projection_kind
                        is WyscoutLogicalArrowProjectionKind.IDENTITY
                    )
                    assert descriptor_field.node.scalar_type in projected_scalar_types
                    assert (
                        pa.types.is_integer(arrow_field.type)
                        or pa.types.is_string(arrow_field.type)
                        or pa.types.is_timestamp(arrow_field.type)
                    )

    with pytest.raises(W04SchemaClosureError):
        w04_physical_primary_key_paths("LAYER_MANIFEST")
    with pytest.raises(W04SchemaClosureError):
        w04_physical_primary_key_paths("SILVER-ACTION")


def _value_at_path(row: dict[str, object], path: tuple[str, ...]) -> str | int:
    current: object = row
    for segment in path:
        assert type(current) is dict and segment in current
        current = current[segment]
    assert type(current) in {str, int}
    return cast(str | int, current)


@pytest.mark.parametrize("role", ["SILVER_PLAYER_MATCH_FACT", "GOLD_PLAYER_WINDOW"])
def test_fact_and_gold_nested_tenant_primary_keys_encode_exact_readback(role: str) -> None:
    model = next(
        candidate for matrix_role, candidate in _valid_model_matrix() if matrix_role == role
    )
    descriptor = _instantiate_descriptor(role)
    physical, logical = _project_model(descriptor, model)
    paths = w04_physical_primary_key_paths(role)
    keys = tuple(_value_at_path(logical, path) for path in paths)
    assert paths[0] == ("tenant_context", "tenant_id")
    assert keys[0] == str(wyscout_data.TENANT_ID)
    encoded = encode_w04_wyscout_product_parquet(
        pa.Table.from_pylist(
            [physical],
            schema=arrow_schema_from_w04_projection(descriptor),
        ),
        projection_descriptor=descriptor,
        primary_key_fields=tuple(".".join(path) for path in paths),
        primary_keys=(keys,),
        contract_row_bytes=(canonical_json_bytes(logical),),
        parent_paths=(),
    )
    assert encoded.row_count == 1


def test_two_materially_different_rows_never_infer_or_change_any_root_schema() -> None:
    assert set(inspect.signature(w04_parquet_projection_content).parameters) == {"root_role"}
    for role in W04_SCHEMA_ROOT_ROLES[:12]:
        descriptor = _instantiate_descriptor(role)
        schema = arrow_schema_from_w04_projection(descriptor)
        first, _first_logical = _row_pair(descriptor, 0)
        second, _second_logical = _row_pair(descriptor, 1)
        assert first != second
        first_table = pa.Table.from_pylist([first], schema=schema)
        second_table = pa.Table.from_pylist([second], schema=schema)
        assert first_table.schema.equals(schema, check_metadata=True)
        assert second_table.schema.equals(schema, check_metadata=True)
        assert arrow_schema_from_w04_projection(_instantiate_descriptor(role)).equals(
            schema, check_metadata=True
        )


@pytest.mark.parametrize(
    "value",
    [
        Decimal("10"),
        Decimal("10.000000000000000000"),
        Decimal("1E+3"),
        Decimal("12.3400"),
        Decimal("0"),
        Decimal("-0"),
        Decimal("0.000000000000000000"),
        Decimal("-0.000000000000000000"),
    ],
)
def test_adopted_descriptor_exact_decimal_vectors_reproduce_logical_json_bytes(
    value: Decimal,
) -> None:
    descriptor = _instantiate_descriptor("SILVER_ACTION")
    schema = arrow_schema_from_w04_projection(descriptor)
    physical, logical = _row_pair(descriptor, 1)
    physical["period_elapsed_seconds"] = exact_decimal128_with_exponent_to_w04_arrow(
        value,
        declared_scale=max(0, -cast(int, value.as_tuple().exponent)),
    )
    logical["period_elapsed_seconds"] = str(value)
    primary_field = descriptor.fields[0].name
    primary_value = physical[primary_field]
    assert type(primary_value) in {str, int}
    encoding = encode_w04_wyscout_product_parquet(
        pa.Table.from_pylist([physical], schema=schema),
        projection_descriptor=descriptor,
        primary_key_fields=(primary_field,),
        primary_keys=((cast(str | int, primary_value),),),
        contract_row_bytes=(canonical_json_bytes(logical),),
        parent_paths=(),
    )
    assert encoding.row_count == 1


def test_minimum_29_valid_model_rows_round_trip_only_through_accepted_descriptors() -> None:
    matrix = _valid_model_matrix()
    assert {role for role, _model in matrix} == set(W04_SCHEMA_ROOT_ROLES[:12])
    known_rows = tuple(
        cast(wyscout_data.BronzeKnownRecord, model)
        for role, model in matrix
        if role == "BRONZE_KNOWN_RECORD"
    )
    assert _canonical_json_kind_roster(known_rows[0].raw_record) == set(
        wyscout_data.CanonicalJsonKind
    )
    assert b'"nullValue":null' in wyscout_data.canonical_raw_json_bytes(known_rows[0].raw_record)
    assert wyscout_data.canonical_raw_json_bytes(known_rows[1].raw_record) == (
        b'{"alternate":{"empty_array":[],"empty_object":{}}}'
    )
    assert len({row.raw_record_sha256 for row in known_rows}) == 2
    assert all(row.source_row in row.lineage.source_rows for row in known_rows)

    rejected_rows = tuple(
        cast(wyscout_data.BronzeRejectedRecord, model)
        for role, model in matrix
        if role == "BRONZE_REJECTED_RECORD"
    )
    assert tuple(row.raw_kind.raw_kind_state for row in rejected_rows) == tuple(
        wyscout_data.RawKindState
    )
    assert len({row.raw_record_sha256 for row in rejected_rows}) == 5
    assert (
        len({wyscout_data.canonical_raw_json_bytes(row.raw_record) for row in rejected_rows}) == 5
    )
    assert (
        len({wyscout_data.canonical_contract_json_bytes(row.lineage) for row in rejected_rows}) == 5
    )
    assert (
        len(
            {
                (row.source_row.completion_relative_path, row.source_row.source_record_ordinal)
                for row in rejected_rows
            }
        )
        == 5
    )

    action_rows = tuple(
        cast(wyscout_data.SilverAction, model) for role, model in matrix if role == "SILVER_ACTION"
    )
    null_action, one_position_action, two_position_action = action_rows
    assert tuple(len(row.action_positions) for row in action_rows) == (0, 1, 2)
    assert tuple(row.event_sec_source_scale for row in action_rows) == (0, 18, 18)
    assert tuple(row.period_elapsed_seconds for row in action_rows) == (
        Decimal("0"),
        Decimal("10.123456789012345678"),
        Decimal("9999.999999999999999999"),
    )
    assert tuple(str(row.period_elapsed_seconds) for row in action_rows) == (
        "0",
        "10.123456789012345678",
        "9999.999999999999999999",
    )
    assert tuple(row.period_elapsed_seconds.as_tuple().exponent for row in action_rows) == (
        0,
        -18,
        -18,
    )
    assert len(two_position_action.period_elapsed_seconds.as_tuple().digits) == 22
    assert len({row.action_id for row in action_rows}) == 3
    assert tuple(row.action_source_id for row in action_rows) == (5, 6, 7)
    assert len({row.action_source_id for row in action_rows}) == 3
    assert tuple(row.source_event_record_id for row in action_rows) == (5, 6, 7)
    physical_source_identities = tuple(
        (
            row.source_rows[0].completion_relative_path,
            row.source_rows[0].source_record_ordinal,
            row.source_rows[0].raw_record_sha256,
        )
        for row in action_rows
    )
    assert len(set(physical_source_identities)) == 3
    assert tuple(row.source_record_ordinal for row in action_rows) == (0, 1, 2)
    assert all(
        row.action_id
        == wyscout_data.canonical_source_uuid(
            wyscout_data.SourceRecordKind.ACTION, row.action_source_id
        )
        for row in action_rows
    )
    assert all(row.action_tag_ids == tuple(sorted(set(row.action_tag_ids))) for row in action_rows)
    assert all(
        row.possession_period_sequence.period_action_count == 1
        and row.possession_period_sequence.actions[0].action_id == row.action_id
        and row.possession_period_sequence.actions[0].source_row == row.source_rows[0]
        and row.source_rows[0] in row.lineage.source_rows
        and tuple(
            source_row
            for source_row in row.lineage.source_rows
            if source_row.record_kind is wyscout_data.SourceRecordKind.ACTION
        )
        == row.source_rows
        for row in action_rows
    )
    assert (
        null_action.competition_id,
        null_action.player_id,
        null_action.team_id,
        null_action.action_event_taxonomy_id,
        null_action.action_subevent_taxonomy_id,
    ) == (None, None, None, None, None)
    assert null_action.action_positions == ()
    assert null_action.period_elapsed_seconds == Decimal("0")
    assert null_action.event_sec_source_scale == 0
    assert (
        null_action.possession_predicate_state
        is wyscout_data.PossessionPredicateState.PREDICATE_UNMAPPED
    )
    assert (
        null_action.possession_eligibility_state
        is wyscout_data.PossessionEligibilityState.INELIGIBLE_UNMAPPED
    )
    assert all(
        row.competition_id is not None
        and row.team_id is not None
        and row.possession_predicate_state
        is wyscout_data.PossessionPredicateState.PREDICATE_ADMITTED
        and row.possession_eligibility_state
        is wyscout_data.PossessionEligibilityState.ELIGIBLE_RESOLVED
        for row in (one_position_action, two_position_action)
    )
    assert (
        one_position_action.action_event_taxonomy_id,
        one_position_action.action_subevent_taxonomy_id,
    ) == (8, 80)
    assert (
        two_position_action.action_event_taxonomy_id,
        two_position_action.action_subevent_taxonomy_id,
    ) == (3, 30)
    assert (
        wyscout_data._possession_predicate_decision(
            one_position_action.action_event_taxonomy_id,
            one_position_action.action_subevent_taxonomy_id,
            one_position_action.team_id,
            one_position_action.action_tag_ids,
        ),
        wyscout_data._possession_predicate_decision(
            two_position_action.action_event_taxonomy_id,
            two_position_action.action_subevent_taxonomy_id,
            two_position_action.team_id,
            two_position_action.action_tag_ids,
        ),
    ) == (
        wyscout_data.PossessionPredicateDecision.CONTROL,
        wyscout_data.PossessionPredicateDecision.RESTART,
    )
    assert tuple(
        (
            position.x,
            position.x.as_tuple().exponent,
            position.y,
            position.y.as_tuple().exponent,
            position.within_accepted_bounds,
        )
        for row in (one_position_action, two_position_action)
        for position in row.action_positions
    ) == (
        (Decimal("1.000000000000000000"), -18, Decimal("99.00"), -2, True),
        (Decimal("0"), 0, Decimal("100.000"), -3, True),
        (Decimal("99.000000000000000000"), -18, Decimal("1.0"), -1, True),
    )
    assert null_action.action_id not in {
        action_id
        for _team_id, action_ids in wyscout_data._resolved_possession_groups(
            null_action.possession_period_sequence
        )
        for action_id in action_ids
    }
    assert all(
        row.action_id
        in {
            action_id
            for _team_id, action_ids in wyscout_data._resolved_possession_groups(
                row.possession_period_sequence
            )
            for action_id in action_ids
        }
        for row in (one_position_action, two_position_action)
    )
    action_descriptor = _instantiate_descriptor("SILVER_ACTION")
    action_schema = arrow_schema_from_w04_projection(action_descriptor)
    action_logical_bytes: list[bytes] = []
    for action in action_rows:
        physical, logical = _project_model(action_descriptor, action)
        logical_bytes = canonical_json_bytes(logical)
        action_logical_bytes.append(logical_bytes)
        assert logical_bytes == canonical_json_bytes(action.model_dump(mode="json"))
        primary_field = action_descriptor.fields[0].name
        primary_value = physical[primary_field]
        assert type(primary_value) in {str, int}
        encoding = encode_w04_wyscout_product_parquet(
            pa.Table.from_pylist([physical], schema=action_schema),
            projection_descriptor=action_descriptor,
            primary_key_fields=(primary_field,),
            primary_keys=((cast(str | int, primary_value),),),
            contract_row_bytes=(logical_bytes,),
            parent_paths=(),
        )
        assert encoding.row_count == 1
        assert encoding.schema_descriptor.schema_role == action_descriptor.schema_role
        assert encoding.schema_descriptor.serializer_version == action_descriptor.serializer_version
    assert len(set(action_logical_bytes)) == 3
    for role, candidate in matrix:
        owner = ROOT_MODELS[W04_SCHEMA_ROOT_ROLES.index(role)]
        assert type(candidate) is owner
        fresh = owner.model_validate(candidate.model_dump(mode="python"), strict=True)
        assert fresh == candidate
        descriptor = _instantiate_descriptor(role)
        schema = arrow_schema_from_w04_projection(descriptor)
        physical, logical = _project_model(descriptor, fresh)
        table = pa.Table.from_pylist([physical], schema=schema)
        primary_field = descriptor.fields[0].name
        primary_value = physical[primary_field]
        assert type(primary_value) in {str, int}
        contract_bytes = canonical_json_bytes(logical)
        encoding = encode_w04_wyscout_product_parquet(
            table,
            projection_descriptor=descriptor,
            primary_key_fields=(primary_field,),
            primary_keys=((cast(str | int, primary_value),),),
            contract_row_bytes=(contract_bytes,),
            parent_paths=(),
        )
        assert encoding.row_count == 1
        assert encoding.schema_descriptor.schema_role == descriptor.schema_role
        assert fresh.model_dump(mode="json") == logical

    role_counts = {
        role: sum(matrix_role == role for matrix_role, _model in matrix)
        for role in W04_SCHEMA_ROOT_ROLES[:12]
    }
    assert role_counts == {
        "BRONZE_KNOWN_RECORD": 2,
        "BRONZE_REJECTED_RECORD": 5,
        "BRONZE_REJECTED_FIELD": 7,
        "SILVER_COMPETITION": 1,
        "SILVER_TEAM": 1,
        "SILVER_PLAYER": 1,
        "SILVER_MATCH": 1,
        "SILVER_ACTION": 3,
        "SILVER_LINEUP_STINT": 2,
        "SILVER_POSSESSION": 2,
        "SILVER_PLAYER_MATCH_FACT": 2,
        "GOLD_PLAYER_WINDOW": 2,
    }


@pytest.mark.parametrize(
    ("target", "mutation"),
    [
        ("content", "omit"),
        ("content", "add"),
        ("content", "reorder"),
        ("content", "24th"),
        ("row", "dependency-forward"),
        ("row", "dependency-duplicate"),
        ("projection", "width"),
        ("projection", "nullable"),
        ("projection", "metadata"),
        ("projection", "projection-kind"),
    ],
)
def test_roster_dependency_and_projection_authority_mutations_fail_closed(
    target: str,
    mutation: str,
) -> None:
    contents = list(deepcopy(export_w04_implemented_schema_contents()))
    rows = list(deepcopy(export_w04_implemented_schema_rows()))
    if target == "content" and mutation == "omit":
        contents.pop()
        rows.pop()
    elif target == "content" and mutation == "add":
        contents[0]["unknown"] = None
    elif target == "content" and mutation == "reorder":
        contents[0] = dict(reversed(tuple(contents[0].items())))
    elif target == "content":
        contents.append(deepcopy(contents[0]))
        rows.append(deepcopy(rows[0]))
    elif target == "row" and mutation == "dependency-forward":
        rows[0]["closure_dependencies"] = [w04_canonical_schema_id("SILVER_ACTION")]
    elif target == "row":
        dependency = w04_canonical_schema_id("BRONZE_KNOWN_RECORD")
        rows[2]["closure_dependencies"] = [dependency, dependency]
    else:
        projection = cast(dict[str, object], contents[0]["parquet_projection"])
        descriptor = cast(dict[str, object], projection["descriptor"])
        fields = cast(list[dict[str, object]], descriptor["fields"])
        if mutation == "nullable":
            fields[0]["nullable"] = not fields[0]["nullable"]
        elif mutation == "metadata":
            fields[0]["metadata"] = {}
        else:
            node = cast(dict[str, object], fields[0]["node"])
            if mutation == "width":
                node["scalar_type"] = "INT32"
            else:
                node["projection_kind"] = "CANONICAL_JSON_VALUE_UTF8"
    with pytest.raises(W04SchemaClosureError):
        validate_w04_implemented_schema_exports(tuple(contents), tuple(rows))


@pytest.mark.parametrize("replacement", [None, "PLACEHOLDER", {}, {"descriptor": {}}])
def test_json_only_roots_reject_null_omission_placeholder_or_descriptor_substitution(
    replacement: object,
) -> None:
    contents = list(deepcopy(export_w04_implemented_schema_contents()))
    rows = export_w04_implemented_schema_rows()
    if replacement == {}:
        del contents[12]["parquet_projection"]
    else:
        contents[12]["parquet_projection"] = replacement
    with pytest.raises(W04SchemaClosureError):
        validate_w04_implemented_schema_exports(tuple(contents), rows)
    assert export_w04_implemented_schema_contents()[12]["parquet_projection"] == (
        W04_JSON_ONLY_PROJECTION_STATE
    )
    with pytest.raises(W04SchemaClosureError):
        w04_parquet_projection_content("LAYER_MANIFEST")


def test_exports_are_fresh_and_gold_has_no_alternative_schema_authority() -> None:
    first_contents = export_w04_implemented_schema_contents()
    first_rows = export_w04_implemented_schema_rows()
    first_contents[0]["root_role"] = "MUTATED"
    first_rows[0]["root_role"] = "MUTATED"
    second_contents = export_w04_implemented_schema_contents()
    second_rows = export_w04_implemented_schema_rows()
    assert second_contents[0]["root_role"] == "BRONZE_KNOWN_RECORD"
    assert second_rows[0]["root_role"] == "BRONZE_KNOWN_RECORD"
    with pytest.raises(TypeError):
        w04_parquet_projection_content(  # type: ignore[call-arg]
            "GOLD_PLAYER_WINDOW", schema=pa.schema([])
        )
    with pytest.raises(TypeError):
        w04_parquet_projection_content(  # type: ignore[call-arg]
            "GOLD_PLAYER_WINDOW", callback=lambda: pa.schema([])
        )
    with pytest.raises(W04SchemaClosureError):
        w04_parquet_projection_content(hashlib.sha256(b"gold").hexdigest())

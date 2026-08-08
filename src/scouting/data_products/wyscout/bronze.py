"""Complete exact Bronze Action and rejected-field population."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import cast

from scouting.contracts.wyscout_build import (
    LayerManifestSummary,
    canonical_json_bytes,
    layer_manifest_semantic_sha256,
    load_canonical_json,
)
from scouting.contracts.wyscout_data import (
    _FIELD_REGISTRY_ROWS,
    BronzeKnownRecord,
    BronzeRejectedField,
    CanonicalJsonObject,
    CanonicalJsonValue,
    Layer,
    LayerManifest,
    RawFieldMeasurement,
    RejectedFieldDecision,
    SourceRecordKind,
    WyscoutRowLineage,
    WyscoutSourceRowReference,
    accepted_authority_clocks,
    accepted_authority_references,
    accepted_source_authority,
    accepted_source_classification,
    canonical_raw_json_bytes,
    canonicalize_json_value,
    classify_action_subevent,
)
from scouting.sources import wyscout_completion_index as completion
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import (
    PublishedProduct,
    dependency_lineage,
    encode_contract_rows,
    guarded_read,
    publish_product,
    tenant_context,
)
from .silver_manifest import PublishedManifest

EVENT_MEMBER_SHA256 = "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad"


@dataclass(frozen=True, slots=True)
class BronzePopulation:
    known_actions: tuple[BronzeKnownRecord, ...]
    rejected_fields: tuple[BronzeRejectedField, ...]


def _decode_raw(payload: bytes) -> dict[str, object]:
    value = json.loads(payload, parse_float=Decimal)
    if type(value) is not dict:
        raise ValueError("verified action raw record must be one object")
    return cast(dict[str, object], value)


def _raw_object(value: object) -> CanonicalJsonObject:
    canonical = canonicalize_json_value(value)
    if not isinstance(canonical, CanonicalJsonObject):
        raise ValueError("Bronze Action raw record must be one canonical object")
    return canonical


def _lineage(
    context: VerifiedMatchContext, source_row: WyscoutSourceRowReference
) -> WyscoutRowLineage:
    return WyscoutRowLineage(
        source_manifest_id=context.source_manifest_id,
        source_manifest_sha256=context.source_manifest_sha256,
        source_completion_index_sha256=context.event_population.index.sha256,
        source_rows=(source_row,),
        authority_references=accepted_authority_references(),
        authority_clocks=accepted_authority_clocks(),
        source_authority=accepted_source_authority(),
        dependency_lineage=dependency_lineage(),
    )


def _measurements(raw: CanonicalJsonObject) -> tuple[RawFieldMeasurement, ...]:
    return tuple(
        RawFieldMeasurement(
            json_path=f"$.{member.key}",
            measured_json_type=member.value.kind,
        )
        for member in raw.value
    )


def _path_values(raw: dict[str, object], path: str) -> tuple[object, ...]:
    if path == "$":
        return (raw,)
    if path == "$.tags":
        return (raw["tags"],)
    if path in {"$.positions[]", "$.tags[]"}:
        value = raw[path.removeprefix("$.").removesuffix("[]")]
        if type(value) is not list:
            raise ValueError(f"{path} source value must be an exact array")
        return tuple(cast(list[object], value))
    if path in {"$.positions[].x", "$.positions[].y"}:
        positions = raw["positions"]
        if type(positions) is not list:
            raise ValueError("action positions must be an exact array")
        key = path.rsplit(".", 1)[1]
        values: list[object] = []
        for item in cast(list[object], positions):
            if type(item) is not dict or key not in cast(dict[str, object], item):
                raise ValueError(f"{path} source value is malformed")
            values.append(cast(dict[str, object], item)[key])
        return tuple(values)
    key = path.removeprefix("$.")
    return (raw[key],) if key in raw else ()


def _generic_rejected_values(raw: dict[str, object]) -> tuple[tuple[str, object, str], ...]:
    rows: list[tuple[str, object, str]] = []
    for (kind, path), (decision, _types) in _FIELD_REGISTRY_ROWS.items():
        # PRESERVE_UNMAPPED fields already remain losslessly present in the one
        # canonical Bronze raw row.  Quarantine contains forbidden values and
        # failed transforms only; it must not duplicate successfully retained
        # raw evidence or invent an array occurrence ordinal absent from schema.
        if kind is not SourceRecordKind.ACTION or decision != "FORBIDDEN":
            continue
        for value in _path_values(raw, path):
            rows.append((path, value, decision))
    return tuple(rows)


def _rejected_field(
    *,
    build_id: str,
    source_row: WyscoutSourceRowReference,
    lineage: WyscoutRowLineage,
    path: str,
    raw_value: object,
    decision: RejectedFieldDecision,
    reason_code: str,
    action_event_taxonomy_id: int | None = None,
) -> BronzeRejectedField:
    original: CanonicalJsonValue = canonicalize_json_value(raw_value)
    return BronzeRejectedField(
        build_id=build_id,
        tenant_context=tenant_context(),
        source_row=source_row,
        record_kind=SourceRecordKind.ACTION,
        json_path=path,
        original_value=original,
        original_value_sha256=hashlib.sha256(canonical_raw_json_bytes(original)).hexdigest(),
        measured_json_type=original.kind,
        action_event_taxonomy_id=action_event_taxonomy_id,
        decision=decision,
        reason_code=reason_code,
        field_authority=accepted_authority_references()[0],
        classification=accepted_source_classification(),
        lineage=lineage,
    )


def build_bronze_population(*, context: VerifiedMatchContext, build_id: str) -> BronzePopulation:
    """Traverse every selected raw Action exactly once under the accepted registry."""

    known: list[BronzeKnownRecord] = []
    rejected: list[BronzeRejectedField] = []
    source_by_ordinal = {
        entry.source_record_ordinal: entry.source_row
        for sequence in context.event_population.completion.sequences
        for entry in sequence.actions
    }
    if len(source_by_ordinal) != 1_768:
        raise ValueError("checked Action source-row population must be exactly 1,768")
    for verified in context.event_population.actions:
        raw_python = _decode_raw(verified.canonical_raw_record)
        raw = _raw_object(raw_python)
        source_row = source_by_ordinal[verified.evidence.source_record_ordinal]
        lineage = _lineage(context, source_row)
        known.append(
            BronzeKnownRecord(
                build_id=build_id,
                tenant_context=tenant_context(),
                source_row=source_row,
                raw_record=raw,
                raw_record_sha256=verified.evidence.raw_record_sha256,
                measured_raw_fields=_measurements(raw),
                classification=accepted_source_classification(),
                lineage=lineage,
            )
        )
        for path, value, decision_token in _generic_rejected_values(raw_python):
            rejected.append(
                _rejected_field(
                    build_id=build_id,
                    source_row=source_row,
                    lineage=lineage,
                    path=path,
                    raw_value=value,
                    decision=RejectedFieldDecision(decision_token),
                    reason_code=f"FIELD_V2_{decision_token}",
                )
            )
        raw_subevent = canonicalize_json_value(raw_python.get("subEventId"))
        outcome = classify_action_subevent(
            verified.evidence.action_event_taxonomy_id,
            raw_subevent,
        )
        if outcome.rejected_raw_value is not None:
            if outcome.reason_code is None:
                raise AssertionError("rejected subevent lacks its accepted reason")
            rejected.append(
                _rejected_field(
                    build_id=build_id,
                    source_row=source_row,
                    lineage=lineage,
                    path="$.subEventId",
                    raw_value=raw_python.get("subEventId"),
                    decision=RejectedFieldDecision.PRESERVE_UNMAPPED,
                    reason_code=outcome.reason_code.value,
                    action_event_taxonomy_id=verified.evidence.action_event_taxonomy_id,
                )
            )
    known_rows = tuple(sorted(known, key=lambda row: row.source_row.source_record_ordinal))
    rejected_rows = tuple(
        sorted(
            rejected,
            key=lambda row: (
                row.source_row.source_record_ordinal,
                row.json_path,
                row.original_value_sha256,
                row.reason_code,
            ),
        )
    )
    if len(known_rows) != 1_768:
        raise ValueError("Bronze known Action population must contain exactly 1,768 rows")
    if not rejected_rows:
        raise ValueError("accepted action registry traversal must yield nonzero rejected fields")
    if len(set(known_rows)) != len(known_rows) or len(set(rejected_rows)) != len(rejected_rows):
        raise ValueError("Bronze traversal cannot duplicate or collapse retained evidence")
    return BronzePopulation(known_actions=known_rows, rejected_fields=rejected_rows)


def publish_bronze_products(
    *,
    publisher: WyscoutStagedPublisher,
    final_root: Path,
    build_id: str,
    population: BronzePopulation,
    final_recheck: Callable[[], object],
) -> tuple[PublishedProduct, PublishedProduct]:
    """Publish the complete known Action and nonzero rejected-field products."""

    specifications = (
        (
            "BRONZE_KNOWN_RECORD",
            population.known_actions,
            f"data/working/wyscout/v5/bronze/build_id={build_id}/records/"
            f"record_kind=action/source_sha256={EVENT_MEMBER_SHA256}/part-00000.parquet",
        ),
        (
            "BRONZE_REJECTED_FIELD",
            population.rejected_fields,
            f"data/working/wyscout/v5/bronze/build_id={build_id}/quarantine/"
            "rejected-field/record_kind=action/"
            f"source_sha256={EVENT_MEMBER_SHA256}/part-00000.parquet",
        ),
    )
    products: list[PublishedProduct] = []
    for role, rows, relative_path in specifications:
        encoding = encode_contract_rows(
            root_role=role,
            rows=rows,
            parent_paths=(),
        )
        publish_product(
            publisher=publisher,
            final_root=final_root,
            relative_path=relative_path,
            encoding=encoding,
            final_recheck=final_recheck,
        )
        products.append(PublishedProduct(relative_path=relative_path, encoding=encoding))
    return products[0], products[1]


def publish_bronze_manifest(
    *,
    publisher: WyscoutStagedPublisher,
    handle: completion.CheckedProduct[LayerManifest],
    final_root: Path,
    final_recheck: Callable[[], object],
) -> PublishedManifest:
    """Publish the checked Bronze manifest after both Bronze products exist."""

    value = completion.require_checked_product(handle, expected_type=LayerManifest)
    if value.layer is not Layer.BRONZE:
        raise ValueError("bronze.py may publish only the Bronze manifest")
    payload = canonical_json_bytes(value, terminal_lf=True)
    tail = f"bronze/{value.build_id}.manifest.json"

    def validator(candidate: bytes) -> None:
        parsed = load_canonical_json(candidate, terminal_lf=True)
        typed = LayerManifest.model_validate_json(candidate[:-1], strict=True)
        if typed != value or typed.model_dump(mode="json") != parsed:
            raise ValueError("Bronze manifest staged readback drifted")

    result = publisher.publish_bytes(
        "wyscout-manifests",
        tail,
        payload,
        validator=validator,
        final_recheck=final_recheck,
    )
    readback = guarded_read(final_root / tail)
    if readback != payload or result.physical_sha256 != hashlib.sha256(payload).hexdigest():
        raise ValueError("Bronze manifest immutable readback drifted")
    parsed = load_canonical_json(readback, terminal_lf=True)
    summary = LayerManifestSummary(
        layer="BRONZE",
        manifest_relative_path=value.manifest_path.relative_path,
        manifest_sha256=result.physical_sha256,
        manifest_size_bytes=result.size_bytes,
        semantic_sha256=layer_manifest_semantic_sha256(parsed),
    )
    completion.require_checked_product(handle, expected_type=LayerManifest)
    return PublishedManifest(
        handle=handle,
        value=value,
        relative_path=value.manifest_path.relative_path,
        payload=readback,
        summary=summary,
    )


__all__ = [
    "BronzePopulation",
    "build_bronze_population",
    "publish_bronze_manifest",
    "publish_bronze_products",
]

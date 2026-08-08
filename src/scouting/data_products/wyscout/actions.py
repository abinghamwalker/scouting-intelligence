"""Checked Silver Action construction for the exact selected match."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import cast
from uuid import UUID

from scouting.contracts.wyscout_data import (
    ActionPosition,
    PossessionEligibilityState,
    SilverAction,
    SourceRecordKind,
    WyscoutRowLineage,
    _possession_predicate_state,
    _resolved_possession_groups,
    canonical_source_uuid,
)
from scouting.sources import wyscout_completion_index as completion
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import PublishedProduct, encode_contract_rows, publish_product, tenant_context

TARGET_ACTION_SOURCE_IDS = (177_960_876, 177_961_018)


@dataclass(frozen=True, slots=True)
class CheckedActionPopulation:
    handles_by_id: dict[UUID, completion.CheckedProduct[SilverAction]]
    ordered_handles: tuple[completion.CheckedProduct[SilverAction], ...]
    ordered_values: tuple[SilverAction, ...]
    target_handles: tuple[completion.CheckedProduct[SilverAction], ...]
    target_values: tuple[SilverAction, ...]
    resolved_groups: tuple[
        tuple[object, UUID, tuple[UUID, ...]],
        ...,
    ]


def _positions(raw: object) -> tuple[ActionPosition, ...]:
    if type(raw) is not tuple:
        raise ValueError("verified action positions must be one immutable tuple")
    values: list[ActionPosition] = []
    for item in cast(tuple[object, ...], raw):
        if not isinstance(item, Mapping):
            raise ValueError("verified action position must be an immutable mapping")
        x_raw = item["x"]
        y_raw = item["y"]
        if type(x_raw) not in {int, Decimal} or type(y_raw) not in {int, Decimal}:
            raise ValueError("verified action axes must be exact JSON numbers")
        x = x_raw if type(x_raw) is Decimal else Decimal(x_raw)
        y = y_raw if type(y_raw) is Decimal else Decimal(y_raw)
        values.append(
            ActionPosition(
                x=x,
                y=y,
                within_accepted_bounds=Decimal(0) <= x <= 100 and Decimal(0) <= y <= 100,
            )
        )
    return tuple(values)


def build_checked_actions(
    *,
    context: VerifiedMatchContext,
    lineage: WyscoutRowLineage,
    build_id: str,
) -> CheckedActionPopulation:
    """Build exactly the two complete resolved groups containing target actions."""

    checked_match = context.event_population.completion
    sequences = checked_match.sequences
    groups = tuple(
        (sequence, team_id, action_ids)
        for sequence in sequences
        for team_id, action_ids in _resolved_possession_groups(sequence)
    )
    target_ids = {
        canonical_source_uuid(SourceRecordKind.ACTION, source_id)
        for source_id in TARGET_ACTION_SOURCE_IDS
    }
    selected_groups = tuple(group for group in groups if target_ids.intersection(group[2]))
    if tuple(len(group[2]) for group in selected_groups) != (7, 6):
        raise ValueError("target actions must intersect exact resolved groups of seven and six")
    selected_ids = {action_id for _sequence, _team, ids in selected_groups for action_id in ids}
    if len(selected_ids) != 13 or not target_ids <= selected_ids:
        raise ValueError("selected resolved action population must be exactly thirteen")
    all_entries = {entry.action_id: entry for sequence in sequences for entry in sequence.actions}
    raw_by_id = {
        canonical_source_uuid(
            SourceRecordKind.ACTION, action.evidence.source_event_record_id
        ): action
        for action in context.event_population.actions
    }
    resolved_ids = {action_id for _sequence, _team, ids in groups for action_id in ids}
    handles: dict[UUID, completion.CheckedProduct[SilverAction]] = {}
    for action_id in selected_ids:
        entry = all_entries[action_id]
        verified = raw_by_id[action_id]
        raw_positions = verified.raw_record.get("positions")
        scale = max(0, -cast(int, entry.period_elapsed_seconds.as_tuple().exponent))
        handle = completion.build_checked_silver_action(
            completion=checked_match,
            payload={
                "build_id": build_id,
                "tenant_context": tenant_context(),
                "source_completion_index_sha256": context.event_population.index.sha256,
                "source_rows": (entry.source_row,),
                "lineage": lineage,
                "action_source_id": entry.source_event_record_id,
                "action_id": entry.action_id,
                "source_event_record_id": entry.source_event_record_id,
                "match_id": entry.match_id,
                "competition_id": context.competition.canonical_id,
                "player_id": entry.player_id,
                "team_id": entry.team_id,
                "action_event_taxonomy_id": entry.action_event_taxonomy_id,
                "action_subevent_taxonomy_id": entry.action_subevent_taxonomy_id,
                "action_period_code": entry.action_period_code,
                "period_rank": entry.period_rank,
                "period_elapsed_seconds": entry.period_elapsed_seconds,
                "event_sec_source_scale": scale,
                "source_record_ordinal": entry.source_record_ordinal,
                "action_tag_ids": entry.action_tag_ids,
                "action_positions": _positions(raw_positions),
                "possession_predicate_state": _possession_predicate_state(
                    entry.action_event_taxonomy_id,
                    entry.action_subevent_taxonomy_id,
                    entry.team_id,
                    entry.action_tag_ids,
                ),
                "possession_eligibility_state": (
                    PossessionEligibilityState.ELIGIBLE_RESOLVED
                    if entry.action_id in resolved_ids
                    else PossessionEligibilityState.INELIGIBLE_UNMAPPED
                ),
            },
        )
        value = completion.require_checked_product(handle, expected_type=SilverAction)
        if value.action_id != action_id:
            raise AssertionError("checked action readback identity drifted")
        handles[action_id] = handle
    ordered_values = tuple(
        sorted(
            (
                completion.require_checked_product(handle, expected_type=SilverAction)
                for handle in handles.values()
            ),
            key=lambda row: (row.action_order_key, row.action_id.bytes),
        )
    )
    ordered_handles = tuple(handles[row.action_id] for row in ordered_values)
    target_values = tuple(row for row in ordered_values if row.action_id in target_ids)
    if tuple(row.action_source_id for row in target_values) != TARGET_ACTION_SOURCE_IDS:
        raise ValueError("target checked actions are not in exact canonical order")
    return CheckedActionPopulation(
        handles_by_id=handles,
        ordered_handles=ordered_handles,
        ordered_values=ordered_values,
        target_handles=tuple(handles[row.action_id] for row in target_values),
        target_values=target_values,
        resolved_groups=selected_groups,
    )


def publish_actions(
    *,
    publisher: WyscoutStagedPublisher,
    final_root: Path,
    build_id: str,
    population: CheckedActionPopulation,
    parent_paths: tuple[str, ...],
    final_recheck: Callable[[], object],
) -> PublishedProduct:
    """Encode, publish, and reopen exactly thirteen checked Action rows."""

    rows = tuple(sorted(population.ordered_values, key=lambda row: str(row.action_id)))
    if len(rows) != 13:
        raise ValueError("Silver Action publication requires exactly thirteen rows")
    encoding = encode_contract_rows(root_role="SILVER_ACTION", rows=rows, parent_paths=parent_paths)
    relative_path = (
        f"data/working/wyscout/v5/silver/build_id={build_id}/action/"
        "source_partition=england/part-00000.parquet"
    )
    publish_product(
        publisher=publisher,
        final_root=final_root,
        relative_path=relative_path,
        encoding=encoding,
        final_recheck=final_recheck,
    )
    return PublishedProduct(relative_path=relative_path, encoding=encoding)


__all__ = [
    "CheckedActionPopulation",
    "TARGET_ACTION_SOURCE_IDS",
    "build_checked_actions",
    "publish_actions",
]

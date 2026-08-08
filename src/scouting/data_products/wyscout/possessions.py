"""Checked project-defined possession materialization."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid5

from scouting.contracts.wyscout_data import SilverPossession, WyscoutRowLineage
from scouting.sources import wyscout_completion_index as completion
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import PublishedProduct, encode_contract_rows, publish_product, tenant_context
from .actions import CheckedActionPopulation


@dataclass(frozen=True, slots=True)
class CheckedPossessionPopulation:
    handles: tuple[completion.CheckedProduct[SilverPossession], ...]
    values: tuple[SilverPossession, ...]


def build_checked_possessions(
    *,
    context: VerifiedMatchContext,
    lineage: WyscoutRowLineage,
    build_id: str,
    actions: CheckedActionPopulation,
) -> CheckedPossessionPopulation:
    """Build the exact two resolved source-complete groups containing targets."""

    values: list[tuple[UUID, completion.CheckedProduct[SilverPossession]]] = []
    for sequence_value, team_id, action_ids in actions.resolved_groups:
        sequence = sequence_value
        possession_id = uuid5(
            context.match.canonical_id,
            f"checked:{sequence.action_period_code}:{action_ids[0]}",  # type: ignore[attr-defined]
        )
        handle = completion.build_checked_silver_possession(
            completion=context.event_population.completion,
            payload={
                "build_id": build_id,
                "tenant_context": tenant_context(),
                "source_completion_index_sha256": context.event_population.index.sha256,
                "lineage": lineage,
                "possession_id": possession_id,
                "match_id": context.match.canonical_id,
                "action_period_code": sequence.action_period_code,  # type: ignore[attr-defined]
                "team_id": team_id,
            },
            contributing_actions=tuple(
                actions.handles_by_id[action_id] for action_id in action_ids
            ),
        )
        value = completion.require_checked_product(handle, expected_type=SilverPossession)
        if value.action_ids != action_ids:
            raise AssertionError("checked possession does not retain its complete resolved group")
        values.append((possession_id, handle))
    values.sort(key=lambda item: item[0].bytes)
    handles = tuple(handle for _identity, handle in values)
    products = tuple(
        completion.require_checked_product(handle, expected_type=SilverPossession)
        for handle in handles
    )
    if len(products) != 2 or tuple(len(row.action_ids) for row in products) not in {(7, 6), (6, 7)}:
        raise ValueError("checked possession population must contain groups of seven and six")
    return CheckedPossessionPopulation(handles=handles, values=products)


def publish_possessions(
    *,
    publisher: WyscoutStagedPublisher,
    final_root: Path,
    build_id: str,
    population: CheckedPossessionPopulation,
    parent_paths: tuple[str, ...],
    final_recheck: Callable[[], object],
) -> PublishedProduct:
    rows = tuple(sorted(population.values, key=lambda row: str(row.possession_id)))
    if len(rows) != 2:
        raise ValueError("Silver Possession publication requires exactly two rows")
    encoding = encode_contract_rows(
        root_role="SILVER_POSSESSION", rows=rows, parent_paths=parent_paths
    )
    relative_path = (
        f"data/working/wyscout/v5/silver/build_id={build_id}/possession/"
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
    "CheckedPossessionPopulation",
    "build_checked_possessions",
    "publish_possessions",
]

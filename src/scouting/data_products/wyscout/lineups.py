"""Exact accepted one-row right-censored lineup population."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import UUID

from scouting.contracts.wyscout_data import (
    NominalMinuteInterval,
    SilverLineupStint,
    WyscoutRowLineage,
)
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import PublishedProduct, encode_contract_rows, publish_product, tenant_context

LINEUP_STINT_ID = UUID("591cdf5b-2281-53c4-8225-150313ca2c01")


def build_lineup_stint(
    *, context: VerifiedMatchContext, lineage: WyscoutRowLineage, build_id: str
) -> SilverLineupStint:
    """Reconstruct the accepted bench-to-minute-82 open stint without inference."""

    if context.target_substitution_minute != 82:
        raise ValueError("accepted target substitution minute drifted")
    return SilverLineupStint(
        build_id=build_id,
        tenant_context=tenant_context(),
        source_completion_index_sha256=context.event_population.index.sha256,
        source_rows=(context.match_source_row,),
        lineage=lineage,
        lineup_stint_id=LINEUP_STINT_ID,
        match_id=context.match.canonical_id,
        player_id=context.target_player.canonical_id,
        team_id=context.target_team.canonical_id,
        start_interval=NominalMinuteInterval(lower=82, upper=83),
        end_interval=None,
        lower_bound_minutes=None,
        upper_bound_minutes=None,
        right_censored=True,
    )


def publish_lineup_stint(
    *,
    publisher: WyscoutStagedPublisher,
    final_root: Path,
    build_id: str,
    value: SilverLineupStint,
    parent_paths: tuple[str, ...],
    final_recheck: Callable[[], object],
) -> PublishedProduct:
    encoding = encode_contract_rows(
        root_role="SILVER_LINEUP_STINT", rows=(value,), parent_paths=parent_paths
    )
    relative_path = (
        f"data/working/wyscout/v5/silver/build_id={build_id}/lineup-stint/"
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


__all__ = ["LINEUP_STINT_ID", "build_lineup_stint", "publish_lineup_stint"]

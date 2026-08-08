"""Exact checked one-row Silver player-match fact."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from scouting.contracts.wyscout_data import (
    FEATURE_SCHEMA_HASH,
    GoldCoverage,
    GoldCoverageDimension,
    GoldCoverageDimensionName,
    GoldCoverageState,
    SilverPlayerMatchFact,
    W04Applicability,
    W04ApplicabilityAssessment,
    W04SemanticTemporalProof,
    WyscoutRowLineage,
    accepted_authority_clocks,
    accepted_source_authority,
)
from scouting.sources import wyscout_completion_index as completion
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import (
    PublishedProduct,
    dependency_lineage,
    encode_contract_rows,
    publish_product,
    tenant_context,
)
from .actions import CheckedActionPopulation
from .possessions import CheckedPossessionPopulation

FEATURE_CUTOFF = datetime(2026, 8, 1, tzinfo=UTC)
DEPENDENCY_WATERMARK = datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC)


def temporal_proof(context: VerifiedMatchContext) -> W04SemanticTemporalProof:
    lineage = dependency_lineage()
    snapshot = datetime(2017, 8, 11, 18, 45, tzinfo=UTC)
    if context.match_start_utc != "2017-08-11T18:45:00Z":
        raise ValueError("selected match snapshot drifted")
    return W04SemanticTemporalProof(
        snapshot_as_of_ts=snapshot,
        available_at_watermark=DEPENDENCY_WATERMARK,
        valid_from_ts=DEPENDENCY_WATERMARK,
        feature_cutoff_ts=FEATURE_CUTOFF,
        source_manifest_ids=(context.source_manifest_id,),
        source_completion_index_sha256=context.event_population.index.sha256,
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        dependency_lineage_hash=lineage.lineage_hash,
        dependency_lineage=lineage,
        source_authority=accepted_source_authority(),
        authority_clocks=accepted_authority_clocks(),
    )


def _complete_coverage() -> GoldCoverage:
    dimensions = tuple(
        GoldCoverageDimension(
            name=name,
            numerator={
                GoldCoverageDimensionName.IDENTITY: 3,
                GoldCoverageDimensionName.LINEUP: 1,
                GoldCoverageDimensionName.ACTION: 2,
                GoldCoverageDimensionName.COORDINATE: 2,
                GoldCoverageDimensionName.POSSESSION: 2,
                GoldCoverageDimensionName.TEMPORAL: 8,
            }[name],
            denominator={
                GoldCoverageDimensionName.IDENTITY: 3,
                GoldCoverageDimensionName.LINEUP: 1,
                GoldCoverageDimensionName.ACTION: 2,
                GoldCoverageDimensionName.COORDINATE: 2,
                GoldCoverageDimensionName.POSSESSION: 2,
                GoldCoverageDimensionName.TEMPORAL: 8,
            }[name],
            coverage=Decimal(1),
            state=GoldCoverageState.COMPLETE,
        )
        for name in GoldCoverageDimensionName
    )
    return GoldCoverage(dimensions=dimensions, coverage_overall=Decimal(1), missing_dimensions=())


def build_checked_player_match_fact(
    *,
    context: VerifiedMatchContext,
    lineage: WyscoutRowLineage,
    build_id: str,
    lineup: object,
    actions: CheckedActionPopulation,
    possessions: CheckedPossessionPopulation,
) -> completion.CheckedProduct[SilverPlayerMatchFact]:
    """Build and immediately reverify the exact target-player match fact."""

    proof = temporal_proof(context)
    assessment = W04ApplicabilityAssessment(
        state=W04Applicability.RESEARCH_ONLY,
        reason_codes=("RIGHT_CENSORED_OR_UNCERTAIN",),
    )
    handle = completion.build_checked_silver_player_match_fact(
        completion=context.event_population.completion,
        payload={
            "build_id": build_id,
            "tenant_context": tenant_context(),
            "source_completion_index_sha256": context.event_population.index.sha256,
            "lineage": lineage,
            "source_manifest_id": context.source_manifest_id,
            "match_id": context.match.canonical_id,
            "player_id": context.target_player.canonical_id,
            "competition_id": context.competition.canonical_id,
            "season_id": context.season_id,
            "match_start_utc": datetime(2017, 8, 11, 18, 45, tzinfo=UTC),
            "match_team_id": context.target_team.canonical_id,
            "action_count": 2,
            "coordinate_known_action_count": 2,
            "resolved_possession_action_count": 2,
            "right_censored_or_uncertain": True,
            "coverage": _complete_coverage(),
            "applicability": assessment,
            "temporal_proof": proof,
        },
        contributing_lineup_stints=(lineup,),
        contributing_actions=actions.target_handles,
        contributing_possessions=possessions.handles,
    )
    value = completion.require_checked_product(handle, expected_type=SilverPlayerMatchFact)
    if (
        value.action_count,
        value.coordinate_known_action_count,
        value.resolved_possession_action_count,
    ) != (
        2,
        2,
        2,
    ):
        raise AssertionError("checked fact exact feature counts drifted")
    return handle


def publish_player_match_fact(
    *,
    publisher: WyscoutStagedPublisher,
    final_root: Path,
    build_id: str,
    handle: completion.CheckedProduct[SilverPlayerMatchFact],
    parent_paths: tuple[str, ...],
    final_recheck: Callable[[], object],
) -> PublishedProduct:
    value = completion.require_checked_product(handle, expected_type=SilverPlayerMatchFact)
    encoding = encode_contract_rows(
        root_role="SILVER_PLAYER_MATCH_FACT",
        rows=(value,),
        parent_paths=parent_paths,
    )
    relative_path = (
        f"data/working/wyscout/v5/silver/build_id={build_id}/player-match-fact/"
        "source_partition=england/part-00000.parquet"
    )
    publish_product(
        publisher=publisher,
        final_root=final_root,
        relative_path=relative_path,
        encoding=encoding,
        final_recheck=final_recheck,
    )
    completion.require_checked_product(handle, expected_type=SilverPlayerMatchFact)
    return PublishedProduct(relative_path=relative_path, encoding=encoding)


__all__ = [
    "DEPENDENCY_WATERMARK",
    "FEATURE_CUTOFF",
    "build_checked_player_match_fact",
    "publish_player_match_fact",
    "temporal_proof",
]

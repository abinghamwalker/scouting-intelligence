"""Exact checked four-feature Gold player window."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from scouting.contracts.wyscout_build import (
    WINDOW_DEFINITION_ID,
    LayerManifestSummary,
    accepted_window_identity,
    canonical_json_bytes,
    layer_manifest_semantic_sha256,
    load_canonical_json,
)
from scouting.contracts.wyscout_data import (
    FEATURE_SCHEMA_HASH,
    ROLE_CONTEXT_ID,
    ROLE_CONTEXT_STATE,
    ROLE_CONTEXT_VERSION,
    GoldFeatureValues,
    GoldPlayerWindow,
    Layer,
    LayerManifest,
    SilverPlayerMatchFact,
    WyscoutRowLineage,
)
from scouting.sources import wyscout_completion_index as completion
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import (
    PublishedProduct,
    encode_contract_rows,
    guarded_read,
    publish_product,
    tenant_context,
    utc_token,
)
from .silver_manifest import PublishedManifest


@dataclass(frozen=True, slots=True)
class CheckedGold:
    handle: completion.CheckedProduct[GoldPlayerWindow]
    value: GoldPlayerWindow


def build_checked_gold(
    *,
    context: VerifiedMatchContext,
    lineage: WyscoutRowLineage,
    build_id: str,
    fact: completion.CheckedProduct[SilverPlayerMatchFact],
) -> CheckedGold:
    """Build exactly one Gold row and immediately rederive its checked graph."""

    fact_value = completion.require_checked_product(fact, expected_type=SilverPlayerMatchFact)
    window = accepted_window_identity()
    handle = completion.build_checked_gold_player_window(
        payload={
            "build_id": build_id,
            "tenant_context": tenant_context(),
            "source_completion_index_sha256": context.event_population.index.sha256,
            "lineage": lineage,
            "player_id": context.target_player.canonical_id,
            "competition_id": context.competition.canonical_id,
            "season_id": context.season_id,
            "role_context_id": ROLE_CONTEXT_ID,
            "role_context_version": ROLE_CONTEXT_VERSION,
            "role_context_state": ROLE_CONTEXT_STATE,
            "window_definition_id": window_identity_id(window),
            "window_start_utc": datetime(2017, 8, 11, tzinfo=UTC),
            "window_end_utc": datetime(2017, 8, 12, tzinfo=UTC),
            "feature_cutoff_ts": datetime(2026, 8, 1, tzinfo=UTC),
            "dependency_lineage_hash": fact_value.temporal_proof.dependency_lineage_hash,
            "feature_schema_hash": FEATURE_SCHEMA_HASH,
            "temporal_proof": fact_value.temporal_proof,
            "coverage": fact_value.coverage,
            "applicability": fact_value.applicability,
            "features": GoldFeatureValues(
                action_count=2,
                coordinate_known_action_count=2,
                match_count=1,
                resolved_possession_action_count=2,
            ),
        },
        contributing_player_match_facts=(fact,),
    )
    value = completion.require_checked_product(handle, expected_type=GoldPlayerWindow)
    if value.features != GoldFeatureValues(
        action_count=2,
        coordinate_known_action_count=2,
        match_count=1,
        resolved_possession_action_count=2,
    ):
        raise AssertionError("checked Gold vector drifted")
    return CheckedGold(handle=handle, value=value)


def window_identity_id(window: object) -> UUID:
    """Return the accepted UUID without creating a second derivation."""

    del window
    return UUID(WINDOW_DEFINITION_ID)


def publish_gold_product(
    *,
    publisher: WyscoutStagedPublisher,
    final_root: Path,
    build_id: str,
    checked: CheckedGold,
    parent_paths: tuple[str, ...],
    final_recheck: Callable[[], object],
) -> PublishedProduct:
    value = completion.require_checked_product(checked.handle, expected_type=GoldPlayerWindow)
    encoding = encode_contract_rows(
        root_role="GOLD_PLAYER_WINDOW", rows=(value,), parent_paths=parent_paths
    )
    relative_path = (
        f"data/working/wyscout/v5/gold/build_id={build_id}/player-window/"
        f"competition_id={value.competition_id}/"
        f"window_definition_id={value.window_definition_id}/"
        f"window_start_utc={utc_token(value.window_start_utc)}/"
        f"window_end_utc={utc_token(value.window_end_utc)}/"
        f"feature_cutoff_ts={utc_token(value.feature_cutoff_ts)}/part-00000.parquet"
    )
    publish_product(
        publisher=publisher,
        final_root=final_root,
        relative_path=relative_path,
        encoding=encoding,
        final_recheck=final_recheck,
    )
    completion.require_checked_product(checked.handle, expected_type=GoldPlayerWindow)
    return PublishedProduct(relative_path=relative_path, encoding=encoding)


def publish_gold_manifest(
    *,
    publisher: WyscoutStagedPublisher,
    handle: completion.CheckedProduct[LayerManifest],
    final_root: Path,
    final_recheck: Callable[[], object],
) -> PublishedManifest:
    """Publish the checked Gold manifest after the one Gold product exists."""

    value = completion.require_checked_product(handle, expected_type=LayerManifest)
    if value.layer is not Layer.GOLD:
        raise ValueError("gold.py may publish only the Gold manifest")
    payload = canonical_json_bytes(value, terminal_lf=True)
    tail = f"gold/{value.build_id}.manifest.json"

    def validator(candidate: bytes) -> None:
        parsed = load_canonical_json(candidate, terminal_lf=True)
        typed = LayerManifest.model_validate_json(candidate[:-1], strict=True)
        if typed != value or typed.model_dump(mode="json") != parsed:
            raise ValueError("Gold manifest staged readback drifted")

    result = publisher.publish_bytes(
        "wyscout-manifests",
        tail,
        payload,
        validator=validator,
        final_recheck=final_recheck,
    )
    readback = guarded_read(final_root / tail)
    if readback != payload or result.physical_sha256 != hashlib.sha256(payload).hexdigest():
        raise ValueError("Gold manifest immutable readback drifted")
    parsed = load_canonical_json(readback, terminal_lf=True)
    summary = LayerManifestSummary(
        layer="GOLD",
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
    "CheckedGold",
    "build_checked_gold",
    "publish_gold_manifest",
    "publish_gold_product",
]

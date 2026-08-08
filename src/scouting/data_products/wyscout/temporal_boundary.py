"""Strict Gold temporal-boundary readback and sole boundary-receipt writer."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID

from scouting.contracts.wyscout_build import (
    BoundaryReceiptSummary,
    TemporalBoundaryReceipt,
    boundary_receipt_path,
    canonical_json_bytes,
)
from scouting.contracts.wyscout_data import GoldPlayerWindow
from scouting.sources import wyscout_completion_index as completion
from scouting.storage.formats import (
    canonical_json_bytes as format_canonical_json_bytes,
)
from scouting.storage.formats import (
    read_parquet_bytes,
    w04_wyscout_parquet_semantic_sha256,
)
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import PublishedProduct, guarded_read, projection_descriptor
from .gold import CheckedGold
from .silver_manifest import PublishedManifest


@dataclass(frozen=True, slots=True)
class PublishedBoundaryReceipt:
    value: TemporalBoundaryReceipt
    relative_path: str
    payload: bytes
    summary: BoundaryReceiptSummary


def publish_temporal_boundary_receipt(
    *,
    publisher: WyscoutStagedPublisher,
    working_final_root: Path,
    runs_final_root: Path,
    build_id: str,
    run_id: UUID,
    checked_at: datetime,
    checked_gold: CheckedGold,
    gold_product: PublishedProduct,
    gold_manifest: PublishedManifest,
    final_recheck: Callable[[], object],
) -> PublishedBoundaryReceipt:
    """Reopen exact Gold bytes and publish one strict-before-cutoff receipt."""

    gold = completion.require_checked_product(checked_gold.handle, expected_type=GoldPlayerWindow)
    if gold.build_id != build_id:
        raise ValueError("Gold checked build differs from receipt build")
    working_prefix = "data/working/wyscout/v5/"
    if not gold_product.relative_path.startswith(working_prefix):
        raise ValueError("Gold product path is outside the accepted working root")
    physical = guarded_read(
        working_final_root / gold_product.relative_path.removeprefix(working_prefix)
    )
    if physical != gold_product.encoding.payload or read_parquet_bytes(
        physical
    ) != read_parquet_bytes(gold_product.encoding.payload):
        raise ValueError("Gold physical readback differs from accepted encoding")
    logical = format_canonical_json_bytes(gold.model_dump(mode="json"))
    semantic = w04_wyscout_parquet_semantic_sha256(
        projection_descriptor=projection_descriptor("GOLD_PLAYER_WINDOW"),
        contract_row_bytes=(logical,),
        parent_paths=gold_product.encoding.parent_paths,
    )
    if (
        hashlib.sha256(physical).hexdigest() != gold_product.encoding.physical_sha256
        or semantic != gold_product.encoding.semantic_sha256
    ):
        raise ValueError("Gold physical or semantic digest readback drifted")
    if len(gold_manifest.value.entries) != 1:
        raise ValueError("Gold manifest must contain exactly one product")
    entry = gold_manifest.value.entries[0]
    if (
        entry.path.relative_path != gold_product.relative_path
        or entry.physical_sha256 != gold_product.encoding.physical_sha256
        or entry.semantic_sha256 != gold_product.encoding.semantic_sha256
        or entry.row_count != 1
    ):
        raise ValueError("Gold manifest entry differs from reopened Gold product")
    proof_bytes = canonical_json_bytes(gold.temporal_proof.model_dump(mode="json"))
    if not (
        gold.temporal_proof.snapshot_as_of_ts < gold.feature_cutoff_ts
        and gold.temporal_proof.available_at_watermark < gold.feature_cutoff_ts
        and gold.temporal_proof.valid_from_ts < gold.feature_cutoff_ts
    ):
        raise ValueError("Gold temporal proof is not strictly before cutoff")
    relative_path = boundary_receipt_path(build_id, str(run_id), gold_product.relative_path)
    value = TemporalBoundaryReceipt(
        build_id=build_id,
        checked_at=checked_at.isoformat().replace("+00:00", "Z"),
        dependency_lineage_hash=gold.dependency_lineage_hash,
        gold_manifest_relative_path=gold_manifest.relative_path,
        gold_manifest_sha256=gold_manifest.summary.manifest_sha256,
        gold_product_physical_sha256=gold_product.encoding.physical_sha256,
        gold_product_relative_path=gold_product.relative_path,
        gold_product_semantic_sha256=gold_product.encoding.semantic_sha256,
        gold_relative_path_sha256=hashlib.sha256(
            gold_product.relative_path.encode("utf-8")
        ).hexdigest(),
        run_id=str(run_id),
        temporal_proof_sha256=hashlib.sha256(proof_bytes).hexdigest(),
    )
    payload = canonical_json_bytes(value, terminal_lf=True)
    prefix = "runs/w04/wyscout-rebuild/"
    tail = relative_path.removeprefix(prefix)

    def validator(candidate: bytes) -> None:
        typed = TemporalBoundaryReceipt.model_validate_json(candidate[:-1], strict=True)
        if candidate != payload or typed != value:
            raise ValueError("temporal boundary staged readback drifted")

    result = publisher.publish_bytes(
        "w04-rebuild-runs",
        tail,
        payload,
        validator=validator,
        final_recheck=final_recheck,
    )
    readback = guarded_read(runs_final_root / tail)
    if readback != payload:
        raise ValueError("temporal boundary immutable readback drifted")
    completion.require_checked_product(checked_gold.handle, expected_type=GoldPlayerWindow)
    return PublishedBoundaryReceipt(
        value=value,
        relative_path=relative_path,
        payload=readback,
        summary=BoundaryReceiptSummary(
            gold_relative_path=gold_product.relative_path,
            relative_path=relative_path,
            sha256=result.physical_sha256,
            size_bytes=result.size_bytes,
        ),
    )


__all__ = ["PublishedBoundaryReceipt", "publish_temporal_boundary_receipt"]

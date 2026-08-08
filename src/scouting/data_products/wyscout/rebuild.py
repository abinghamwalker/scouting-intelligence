"""Exact isolated W04 raw-to-Gold rebuild and sole invocation-receipt writer."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import cast
from uuid import UUID

from scouting.contracts.wyscout_build import (
    GoldProductReadback,
    GoldSchemaAuthorityUnavailableError,
    RebuildInvocation,
    RebuildInvocationReceipt,
    RebuildReceiptSummary,
    canonical_json_bytes,
    load_canonical_json,
    projection_from_invocation,
    rebuild_receipt_path,
    validate_receipt_closure,
)
from scouting.contracts.wyscout_data import (
    Layer,
    ProductPathRole,
)
from scouting.sources import wyscout_completion_index as completion
from scouting.sources import wyscout_vertical_slice as context_adapter
from scouting.storage.formats import read_parquet_bytes

from . import (
    PublishedProduct,
    WyscoutProductRoots,
    complete_match_lineage,
    guarded_read,
    staged_publisher,
)
from .actions import CheckedActionPopulation, build_checked_actions, publish_actions
from .bronze import (
    BronzePopulation,
    build_bronze_population,
    publish_bronze_manifest,
    publish_bronze_products,
)
from .gold import (
    CheckedGold,
    build_checked_gold,
    publish_gold_manifest,
    publish_gold_product,
)
from .lineups import build_lineup_stint, publish_lineup_stint
from .player_match import build_checked_player_match_fact, publish_player_match_fact
from .possessions import (
    CheckedPossessionPopulation,
    build_checked_possessions,
    publish_possessions,
)
from .silver_manifest import (
    PublishedManifest,
    build_checked_manifest,
    manifest_entry,
    publish_silver_manifest,
)
from .temporal_boundary import (
    PublishedBoundaryReceipt,
    publish_temporal_boundary_receipt,
)


@dataclass(frozen=True, slots=True)
class PublishedRebuildReceipt:
    value: RebuildInvocationReceipt
    relative_path: str
    payload: bytes
    summary: RebuildReceiptSummary


@dataclass(frozen=True, slots=True)
class WyscoutRebuildResult:
    bronze_population: BronzePopulation
    actions: CheckedActionPopulation
    possessions: CheckedPossessionPopulation
    gold: CheckedGold
    products: tuple[PublishedProduct, ...]
    manifests: tuple[PublishedManifest, PublishedManifest, PublishedManifest]
    boundary_receipt: PublishedBoundaryReceipt
    rebuild_receipt: PublishedRebuildReceipt


def _read_product(roots: WyscoutProductRoots, product: PublishedProduct) -> bytes:
    prefix = "data/working/wyscout/v5/"
    if not product.relative_path.startswith(prefix):
        raise ValueError("product is outside the accepted working root")
    return guarded_read(roots.working_final_root / product.relative_path.removeprefix(prefix))


def _validate_complete_receipt_closure(
    *,
    receipt: RebuildInvocationReceipt,
    products: tuple[PublishedProduct, ...],
    manifests: tuple[PublishedManifest, PublishedManifest, PublishedManifest],
    boundary: PublishedBoundaryReceipt,
    gold: CheckedGold,
    roots: WyscoutProductRoots,
) -> None:
    """Complete the accepted receipt checks now that Gold schema authority exists.

    The upstream validator is retained as an independent prefix check.  Its final
    legacy exception marks only the once-unavailable Gold projection step; the
    descriptor-owned product validation below closes that exact bounded gap.
    """

    gold_product = products[-1]
    gold_row = completion.require_checked_product(gold.handle, expected_type=type(gold.value))
    try:
        validate_receipt_closure(
            receipt,
            ((boundary.value, boundary.payload),),
            tuple(manifest.payload for manifest in manifests),
            GoldProductReadback(
                contract_row_bytes=(
                    canonical_json_bytes(gold_row.model_dump(mode="json"), terminal_lf=True),
                ),
                physical_bytes=_read_product(roots, gold_product),
                temporal_proof_bytes=canonical_json_bytes(
                    gold_row.temporal_proof.model_dump(mode="json")
                ),
            ),
        )
    except GoldSchemaAuthorityUnavailableError:
        pass
    else:
        raise AssertionError("legacy receipt validator unexpectedly bypassed its explicit stop")

    summaries = tuple(manifest.summary for manifest in manifests)
    if receipt.layer_manifests != summaries:
        raise ValueError("receipt layer summaries differ from published manifests")
    if not (receipt.started_at <= boundary.value.checked_at <= receipt.completed_at):
        raise ValueError("boundary check lies outside the invocation interval")
    product_by_path = {product.relative_path: product for product in products}
    if len(product_by_path) != len(products):
        raise ValueError("published product paths are not unique")
    expected_parent_manifest_layers = ((), (Layer.BRONZE,), (Layer.SILVER,))
    for manifest, expected_layers in zip(manifests, expected_parent_manifest_layers, strict=True):
        if (
            tuple(parent.layer for parent in manifest.value.parent_layer_manifests)
            != expected_layers
        ):
            raise ValueError("manifest parent layer chain drifted")
        reparsed = load_canonical_json(manifest.payload, terminal_lf=True)
        if reparsed != manifest.value.model_dump(mode="json"):
            raise ValueError("manifest canonical readback differs from checked value")
        for entry in manifest.value.entries:
            product = product_by_path.get(entry.path.relative_path)
            if product is None:
                raise ValueError("manifest entry has no published product readback")
            physical = _read_product(roots, product)
            if (
                physical != product.encoding.payload
                or hashlib.sha256(physical).hexdigest() != entry.physical_sha256
                or product.encoding.semantic_sha256 != entry.semantic_sha256
                or product.encoding.row_count != entry.row_count
                or product.encoding.size_bytes != entry.size_bytes
                or product.encoding.parent_paths != entry.ordered_parent_paths
            ):
                raise ValueError("manifest product readback binding drifted")
            if not read_parquet_bytes(physical):
                raise ValueError("manifest product Parquet readback is empty")
    if set(product_by_path) != {
        entry.path.relative_path for manifest in manifests for entry in manifest.value.entries
    }:
        raise ValueError("published product roster differs from complete manifests")
    if receipt.boundary_receipts != (boundary.summary,):
        raise ValueError("receipt boundary summary differs from published boundary")


def _publish_rebuild_receipt(
    *,
    publisher: object,
    roots: WyscoutProductRoots,
    value: RebuildInvocationReceipt,
    final_recheck: Callable[[], object],
) -> PublishedRebuildReceipt:
    from scouting.storage.wyscout_publication import WyscoutStagedPublisher

    if not isinstance(publisher, WyscoutStagedPublisher):
        raise TypeError("rebuild receipt requires the accepted staged publisher")
    payload = canonical_json_bytes(value, terminal_lf=True)
    relative_path = rebuild_receipt_path(value.build_id, str(value.run_id))
    prefix = "runs/w04/wyscout-rebuild/"
    tail = relative_path.removeprefix(prefix)

    def validator(candidate: bytes) -> None:
        typed = RebuildInvocationReceipt.model_validate_json(candidate[:-1], strict=True)
        if candidate != payload or typed != value:
            raise ValueError("rebuild receipt staged readback drifted")

    result = publisher.publish_bytes(
        "w04-rebuild-runs",
        tail,
        payload,
        validator=validator,
        final_recheck=final_recheck,
    )
    readback = guarded_read(roots.runs_final_root / tail)
    if readback != payload:
        raise ValueError("rebuild receipt immutable readback drifted")
    return PublishedRebuildReceipt(
        value=value,
        relative_path=relative_path,
        payload=readback,
        summary=RebuildReceiptSummary(
            relative_path=relative_path,
            sha256=result.physical_sha256,
            size_bytes=result.size_bytes,
        ),
    )


def rebuild_wyscout_v5(
    *,
    invocation: RebuildInvocation,
    run_id: UUID,
    roots: WyscoutProductRoots,
    source_root: Path,
    source_manifest_root: Path,
    identity_root: Path,
    started_at: datetime,
    checked_at: datetime,
    completed_at: datetime,
    final_recheck: Callable[[], object],
) -> WyscoutRebuildResult:
    """Execute the complete accepted one-match slice below exact supplied roots."""

    projection_from_invocation(invocation)
    if not started_at <= checked_at <= completed_at:
        raise ValueError("rebuild receipt clocks are not one ordered interval")
    context = context_adapter.load_verified_match_context(
        source_root=source_root,
        manifest_root=source_manifest_root,
        identity_root=identity_root,
        source_manifest_sha256=context_adapter.SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=context_adapter.SOURCE_COMPLETION_INDEX_SHA256,
        identity_bundle_sha256=context_adapter.IDENTITY_BUNDLE_SHA256,
    )
    publisher = staged_publisher(roots)
    build_id = invocation.build_id
    lineage = complete_match_lineage(context)

    bronze_population = build_bronze_population(context=context, build_id=build_id)
    bronze_products = publish_bronze_products(
        publisher=publisher,
        final_root=roots.working_final_root,
        build_id=build_id,
        population=bronze_population,
        final_recheck=final_recheck,
    )
    bronze_entries = tuple(
        manifest_entry(
            product=product,
            path_role=role,
            serializer="bronze.py",
            parent_paths=(),
        )
        for product, role in zip(
            bronze_products,
            (ProductPathRole.BRONZE_KNOWN_RECORD, ProductPathRole.BRONZE_REJECTED_FIELD),
            strict=True,
        )
    )
    bronze_handle = build_checked_manifest(
        context=context,
        build_id=build_id,
        layer=Layer.BRONZE,
        entries=bronze_entries,
        parent=None,
        products=(),
    )
    bronze_manifest = publish_bronze_manifest(
        publisher=publisher,
        handle=bronze_handle,
        final_root=roots.manifest_final_root,
        final_recheck=final_recheck,
    )

    parent_paths = tuple(sorted(product.relative_path for product in bronze_products))
    actions = build_checked_actions(context=context, lineage=lineage, build_id=build_id)
    lineup = build_lineup_stint(context=context, lineage=lineage, build_id=build_id)
    possessions = build_checked_possessions(
        context=context, lineage=lineage, build_id=build_id, actions=actions
    )
    fact = build_checked_player_match_fact(
        context=context,
        lineage=lineage,
        build_id=build_id,
        lineup=lineup,
        actions=actions,
        possessions=possessions,
    )
    silver_products = (
        publish_actions(
            publisher=publisher,
            final_root=roots.working_final_root,
            build_id=build_id,
            population=actions,
            parent_paths=parent_paths,
            final_recheck=final_recheck,
        ),
        publish_lineup_stint(
            publisher=publisher,
            final_root=roots.working_final_root,
            build_id=build_id,
            value=lineup,
            parent_paths=parent_paths,
            final_recheck=final_recheck,
        ),
        publish_possessions(
            publisher=publisher,
            final_root=roots.working_final_root,
            build_id=build_id,
            population=possessions,
            parent_paths=parent_paths,
            final_recheck=final_recheck,
        ),
        publish_player_match_fact(
            publisher=publisher,
            final_root=roots.working_final_root,
            build_id=build_id,
            handle=fact,
            parent_paths=parent_paths,
            final_recheck=final_recheck,
        ),
    )
    silver_entries = tuple(
        manifest_entry(
            product=product,
            path_role=role,
            serializer=serializer,
            parent_paths=parent_paths,
        )
        for product, role, serializer in zip(
            silver_products,
            (
                ProductPathRole.SILVER_ACTION,
                ProductPathRole.SILVER_LINEUP_STINT,
                ProductPathRole.SILVER_POSSESSION,
                ProductPathRole.SILVER_PLAYER_MATCH_FACT,
            ),
            ("actions.py", "lineups.py", "possessions.py", "player_match.py"),
            strict=True,
        )
    )
    contributing_silver = cast(
        tuple[completion.CheckedProduct[object], ...],
        (*actions.ordered_handles, *possessions.handles, fact),
    )
    silver_handle = build_checked_manifest(
        context=context,
        build_id=build_id,
        layer=Layer.SILVER,
        entries=silver_entries,
        parent=bronze_manifest,
        products=contributing_silver,
    )
    silver_manifest = publish_silver_manifest(
        publisher=publisher,
        handle=silver_handle,
        final_root=roots.manifest_final_root,
        final_recheck=final_recheck,
    )

    checked_gold = build_checked_gold(
        context=context, lineage=lineage, build_id=build_id, fact=fact
    )
    gold_parent_paths = tuple(sorted(product.relative_path for product in silver_products))
    gold_product = publish_gold_product(
        publisher=publisher,
        final_root=roots.working_final_root,
        build_id=build_id,
        checked=checked_gold,
        parent_paths=gold_parent_paths,
        final_recheck=final_recheck,
    )
    gold_entry = manifest_entry(
        product=gold_product,
        path_role=ProductPathRole.GOLD_PLAYER_WINDOW,
        serializer="gold.py",
        parent_paths=gold_parent_paths,
    )
    gold_handle = build_checked_manifest(
        context=context,
        build_id=build_id,
        layer=Layer.GOLD,
        entries=(gold_entry,),
        parent=silver_manifest,
        products=cast(tuple[completion.CheckedProduct[object], ...], (checked_gold.handle,)),
    )
    gold_manifest = publish_gold_manifest(
        publisher=publisher,
        handle=gold_handle,
        final_root=roots.manifest_final_root,
        final_recheck=final_recheck,
    )
    boundary = publish_temporal_boundary_receipt(
        publisher=publisher,
        working_final_root=roots.working_final_root,
        runs_final_root=roots.runs_final_root,
        build_id=build_id,
        run_id=run_id,
        checked_at=checked_at,
        checked_gold=checked_gold,
        gold_product=gold_product,
        gold_manifest=gold_manifest,
        final_recheck=final_recheck,
    )
    manifests = (bronze_manifest, silver_manifest, gold_manifest)
    products = (*bronze_products, *silver_products, gold_product)
    receipt_value = RebuildInvocationReceipt(
        boundary_receipts=(boundary.summary,),
        build_id=build_id,
        completed_at=completed_at.isoformat().replace("+00:00", "Z"),
        layer_manifests=tuple(manifest.summary for manifest in manifests),
        rebuild_invocation=invocation,
        run_id=str(run_id),
        started_at=started_at.isoformat().replace("+00:00", "Z"),
    )
    _validate_complete_receipt_closure(
        receipt=receipt_value,
        products=products,
        manifests=manifests,
        boundary=boundary,
        gold=checked_gold,
        roots=roots,
    )
    rebuild_receipt = _publish_rebuild_receipt(
        publisher=publisher,
        roots=roots,
        value=receipt_value,
        final_recheck=final_recheck,
    )
    _validate_complete_receipt_closure(
        receipt=receipt_value,
        products=products,
        manifests=manifests,
        boundary=boundary,
        gold=checked_gold,
        roots=roots,
    )
    return WyscoutRebuildResult(
        bronze_population=bronze_population,
        actions=actions,
        possessions=possessions,
        gold=checked_gold,
        products=products,
        manifests=manifests,
        boundary_receipt=boundary,
        rebuild_receipt=rebuild_receipt,
    )


__all__ = [
    "PublishedRebuildReceipt",
    "WyscoutRebuildResult",
    "rebuild_wyscout_v5",
]

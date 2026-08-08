"""Checked manifest composition and sole Silver-manifest writer."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from scouting.contracts.wyscout_build import (
    LayerManifestSummary,
    canonical_json_bytes,
    layer_manifest_semantic_sha256,
    load_canonical_json,
)
from scouting.contracts.wyscout_data import (
    FEATURE_SCHEMA_HASH,
    SOURCE_ACQUIRED_AT,
    SOURCE_COMPLETION_INDEX_SHA256,
    SOURCE_MANIFEST_ID,
    SOURCE_MANIFEST_SHA256,
    SOURCE_RELEASE,
    Layer,
    LayerManifest,
    LayerManifestEntry,
    ManifestPartitionValue,
    ParentLayerManifest,
    ProductPathRole,
    WyscoutProductPath,
    accepted_authority_clocks,
    accepted_source_classification,
)
from scouting.sources import wyscout_completion_index as completion
from scouting.sources.wyscout_vertical_slice import VerifiedMatchContext
from scouting.storage.wyscout_publication import WyscoutStagedPublisher

from . import PublishedProduct, dependency_lineage, guarded_read, tenant_context


@dataclass(frozen=True, slots=True)
class PublishedManifest:
    handle: completion.CheckedProduct[LayerManifest]
    value: LayerManifest
    relative_path: str
    payload: bytes
    summary: LayerManifestSummary


def manifest_entry(
    *,
    product: PublishedProduct,
    path_role: ProductPathRole,
    serializer: str,
    parent_paths: tuple[str, ...],
) -> LayerManifestEntry:
    """Bind one already-encoded product into its exact complete manifest entry."""

    return LayerManifestEntry(
        path=WyscoutProductPath(path_role=path_role, relative_path=product.relative_path),
        serializer=serializer,
        serializer_version=product.encoding.schema_descriptor.serializer_version,
        schema_role=path_role.value,
        row_count=product.encoding.row_count,
        semantic_sha256=product.encoding.semantic_sha256,
        physical_sha256=product.encoding.physical_sha256,
        size_bytes=product.encoding.size_bytes,
        ordered_parent_paths=parent_paths,
        partition_values=tuple(
            # The contract validator independently derives and checks these.
            sorted(
                (
                    ManifestPartitionValue(
                        key=segment.split("=", 1)[0],
                        value=segment.split("=", 1)[1],
                    )
                    for segment in product.relative_path.split("/")
                    if "=" in segment
                ),
                key=lambda item: item.key,
            )
        ),
        classification=accepted_source_classification(),
    )


def build_checked_manifest(
    *,
    context: VerifiedMatchContext,
    build_id: str,
    layer: Layer,
    entries: Sequence[LayerManifestEntry],
    parent: PublishedManifest | None,
    products: Sequence[completion.CheckedProduct[object]],
) -> completion.CheckedProduct[LayerManifest]:
    """Construct one checked complete manifest from its authentic product graph."""

    parent_rows = (
        ()
        if parent is None
        else (
            ParentLayerManifest(
                layer=parent.value.layer,
                build_id=build_id,
                relative_path=parent.relative_path,
                sha256=parent.summary.manifest_sha256,
            ),
        )
    )
    relative_path = f"data/manifests/wyscout/v5/{layer.value.lower()}/{build_id}.manifest.json"
    lineage = dependency_lineage()
    handle = completion.build_checked_layer_manifest(
        payload={
            "layer": layer,
            "build_id": build_id,
            "manifest_path": WyscoutProductPath(
                path_role=ProductPathRole[f"{layer.value}_MANIFEST"],
                relative_path=relative_path,
            ),
            "source_manifest_id": SOURCE_MANIFEST_ID,
            "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
            "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
            "tenant_context": tenant_context(),
            "classification": accepted_source_classification(),
            "source_available_at": SOURCE_RELEASE,
            "source_acquired_at": SOURCE_ACQUIRED_AT,
            "authority_clocks": accepted_authority_clocks(),
            "feature_schema_hash": FEATURE_SCHEMA_HASH,
            "dependency_lineage_hash": lineage.lineage_hash,
            "dependency_lineage": lineage,
            "entries": tuple(sorted(entries, key=lambda entry: entry.path.relative_path)),
            "parent_layer_manifests": parent_rows,
        },
        completions=(context.event_population.completion,),
        contributing_products=tuple(products),
    )
    return handle


def _manifest_payload(value: LayerManifest) -> bytes:
    return canonical_json_bytes(value, terminal_lf=True)


def publish_silver_manifest(
    *,
    publisher: WyscoutStagedPublisher,
    handle: completion.CheckedProduct[LayerManifest],
    final_root: Path,
    final_recheck: Callable[[], object],
) -> PublishedManifest:
    """Publish and reopen the checked Silver manifest after all products exist."""

    value = completion.require_checked_product(handle, expected_type=LayerManifest)
    if value.layer is not Layer.SILVER:
        raise ValueError("silver_manifest.py may publish only the Silver manifest")
    payload = _manifest_payload(value)
    tail = f"silver/{value.build_id}.manifest.json"

    def validator(candidate: bytes) -> None:
        parsed = load_canonical_json(candidate, terminal_lf=True)
        typed = LayerManifest.model_validate_json(candidate[:-1], strict=True)
        if typed != value or typed.model_dump(mode="json") != parsed:
            raise ValueError("Silver manifest staged readback drifted")

    result = publisher.publish_bytes(
        "wyscout-manifests",
        tail,
        payload,
        validator=validator,
        final_recheck=final_recheck,
    )
    path = final_root / tail
    readback = guarded_read(path)
    if readback != payload or result.physical_sha256 != hashlib.sha256(payload).hexdigest():
        raise ValueError("Silver manifest immutable readback drifted")
    parsed = load_canonical_json(readback, terminal_lf=True)
    summary = LayerManifestSummary(
        layer="SILVER",
        manifest_relative_path=value.manifest_path.relative_path,
        manifest_sha256=result.physical_sha256,
        manifest_size_bytes=result.size_bytes,
        semantic_sha256=layer_manifest_semantic_sha256(parsed),
    )
    return PublishedManifest(
        handle=handle,
        value=value,
        relative_path=value.manifest_path.relative_path,
        payload=readback,
        summary=summary,
    )


__all__ = [
    "PublishedManifest",
    "PublishedProduct",
    "build_checked_manifest",
    "manifest_entry",
    "publish_silver_manifest",
]

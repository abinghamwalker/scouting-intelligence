from __future__ import annotations

import base64
import hashlib
from copy import deepcopy
from dataclasses import fields as dataclass_fields
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
from pydantic import ValidationError

from scouting.contracts.evidence import DependencyLineage, EvidenceDependency
from scouting.contracts.primitives import TenantContext
from scouting.contracts.wyscout_build import (
    ADMISSION_ARGV,
    COMPETITION_ID,
    COMPONENT_KEYS,
    DEPENDENCY_WATERMARK,
    FEATURE_CUTOFF_TS,
    POST_HASH_INVOCATION_KEYS,
    PRE_BUILD_PROJECTION_KEYS,
    REBUILD_ARGV,
    SCHEMA_BUNDLE_V1_SHA256,
    SELECTED_MATCH_START_TS,
    SNAPSHOT_AS_OF_TS,
    WINDOW_BYTES_SHA256,
    WINDOW_DEFINITION_ID,
    WINDOW_END_UTC,
    WINDOW_NAMESPACE_NAME,
    WINDOW_START_UTC,
    AuthorityRow,
    BoundaryReceiptSummary,
    ChildResultEnvelope,
    ComponentProofResult,
    EntrypointSourceResult,
    FinalRecheckResult,
    GoldProductReadback,
    GoldSchemaAuthorityUnavailableError,
    LayerManifestSummary,
    PostBuildIdRebuildResult,
    PreBuildAdmissionResult,
    PreBuildProjection,
    RebuildInvocation,
    RebuildInvocationReceipt,
    RebuildReceiptSummary,
    RuntimeSubsetObservation,
    TemporalBoundaryReceipt,
    accepted_authority_rows,
    accepted_dependency_lineage_hash,
    accepted_dependency_rows,
    accepted_window_identity,
    boundary_receipt_path,
    bounded_season_uuid,
    build_id_for_projection,
    canonical_json_bytes,
    code_manifest_id_for_digest,
    gold_manifest_path,
    invocation_from_projection,
    layer_manifest_path,
    layer_manifest_semantic_sha256,
    load_canonical_json,
    projection_from_invocation,
    rebuild_receipt_path,
    sha256_json,
    validate_admission_component_authority,
    validate_layer_manifest_semantic_binding,
    validate_receipt_closure,
    validate_window_clocks,
)
from scouting.contracts.wyscout_data import (
    GoldCoverage,
    GoldCoverageDimension,
    GoldCoverageDimensionName,
    GoldCoverageState,
    GoldFeatureValues,
    GoldPlayerWindow,
    Layer,
    LayerManifest,
    LayerManifestEntry,
    ManifestPartitionValue,
    NominalMinuteInterval,
    ParentLayerManifest,
    ProductPathRole,
    SilverLineupStint,
    SilverPlayerMatchFact,
    SourceRecordKind,
    W04Applicability,
    W04ApplicabilityAssessment,
    W04SemanticTemporalProof,
    WyscoutProductPath,
    WyscoutRowLineage,
    WyscoutSourceRowReference,
    accepted_authority_references,
    accepted_source_authority,
    accepted_source_classification,
)
from scouting.contracts.wyscout_data import (
    accepted_authority_clocks as accepted_data_authority_clocks,
)

H1 = "1" * 64
H2 = "2" * 64
H3 = "3" * 64
H4 = "4" * 64
H5 = "5" * 64
H6 = "6" * 64
H7 = "7" * 64
H8 = "8" * 64
H9 = "9" * 64
HA = "a" * 64
HB = "b" * 64
HC = "c" * 64
HD = "d" * 64
HE = "e" * 64
HF = "f" * 64
REJECTED_CALLER_GOLD_SEMANTIC_CLAIM = H1
RUN_ID = "12345678-1234-4123-8123-123456789abc"
ADMISSION_RUN_ID = "87654321-4321-4321-8321-cba987654321"
FORMER_R1_COMPETITION_ID = "11111111-1111-5111-8111-111111111111"


def _projection() -> PreBuildProjection:
    code_digest = H1
    return PreBuildProjection(
        authority_rows=accepted_authority_rows(),
        code_manifest_id=code_manifest_id_for_digest(code_digest),
        code_manifest_sha256=code_digest,
        dependency_rows=accepted_dependency_rows(),
        environment_digest=H2,
        local_resource_digest=H3,
        product_contract_digest=H4,
        schema_bundle_digest=H5,
        selected_lock_closure_digest=H6,
    )


def _gold_path(build_id: str) -> str:
    return (
        f"data/working/wyscout/v5/gold/build_id={build_id}/player-window/"
        f"competition_id={COMPETITION_ID}/window_definition_id={WINDOW_DEFINITION_ID}/"
        "window_start_utc=20170811T000000000000Z/"
        "window_end_utc=20170812T000000000000Z/"
        "feature_cutoff_ts=20260801T000000000000Z/part-00000.parquet"
    )


def _layer_summaries(build_id: str) -> tuple[LayerManifestSummary, ...]:
    return tuple(
        LayerManifestSummary.model_validate(
            {
                "layer": layer,
                "manifest_relative_path": (
                    f"data/manifests/wyscout/v5/{layer.lower()}/{build_id}.manifest.json"
                ),
                "manifest_sha256": digest,
                "manifest_size_bytes": index,
                "semantic_sha256": semantic,
            }
        )
        for index, (layer, digest, semantic) in enumerate(
            (("BRONZE", H7, HA), ("SILVER", H8, HB), ("GOLD", H9, HC)), start=101
        )
    )


def _data_lineage() -> DependencyLineage:
    dependencies = tuple(
        EvidenceDependency.model_validate_json(canonical_json_bytes(row), strict=True)
        for row in accepted_dependency_rows()
    )
    return DependencyLineage(
        lineage_hash=accepted_dependency_lineage_hash(), dependencies=dependencies
    )


def _match_source_row() -> WyscoutSourceRowReference:
    return WyscoutSourceRowReference(
        source_manifest_id=UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b"),
        completion_relative_path="archive-members/matches_England.json",
        source_sha256="620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29",
        source_record_ordinal=379,
        record_kind=SourceRecordKind.MATCH,
        raw_record_sha256="1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86",
    )


def _row_lineage() -> WyscoutRowLineage:
    return WyscoutRowLineage(
        source_manifest_id=UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b"),
        source_manifest_sha256=("8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"),
        source_completion_index_sha256=(
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
        ),
        source_rows=(_match_source_row(),),
        authority_references=accepted_authority_references(),
        authority_clocks=accepted_data_authority_clocks(),
        source_authority=accepted_source_authority(),
        dependency_lineage=_data_lineage(),
    )


def _temporal_proof() -> W04SemanticTemporalProof:
    lineage = _data_lineage()
    return W04SemanticTemporalProof(
        snapshot_as_of_ts=datetime(2017, 8, 11, 18, 45, tzinfo=UTC),
        available_at_watermark=datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC),
        valid_from_ts=datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC),
        feature_cutoff_ts=datetime(2026, 8, 1, tzinfo=UTC),
        source_manifest_ids=(UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b"),),
        source_completion_index_sha256=(
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
        ),
        feature_schema_hash=("49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"),
        dependency_lineage_hash=lineage.lineage_hash,
        dependency_lineage=lineage,
        source_authority=accepted_source_authority(),
        authority_clocks=accepted_data_authority_clocks(),
    )


def _zero_action_coverage() -> GoldCoverage:
    authority = {row.authority_kind.value: row for row in accepted_authority_references()}
    return GoldCoverage(
        dimensions=(
            GoldCoverageDimension(
                name=GoldCoverageDimensionName.IDENTITY,
                numerator=1,
                denominator=1,
                coverage=Decimal(1),
                state=GoldCoverageState.COMPLETE,
            ),
            GoldCoverageDimension(
                name=GoldCoverageDimensionName.LINEUP,
                numerator=1,
                denominator=1,
                coverage=Decimal(1),
                state=GoldCoverageState.COMPLETE,
            ),
            GoldCoverageDimension(
                name=GoldCoverageDimensionName.ACTION,
                numerator=0,
                denominator=0,
                coverage=Decimal(0),
                state=GoldCoverageState.MISSING_ZERO_DENOMINATOR,
                reason_codes=("ACTION_EVIDENCE_INCOMPLETE",),
            ),
            GoldCoverageDimension(
                name=GoldCoverageDimensionName.COORDINATE,
                numerator=0,
                denominator=0,
                coverage=Decimal(1),
                state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
                reason_codes=("NO_APPLICABLE_COORDINATE_EVIDENCE",),
                zero_denominator_authority=authority["FIELD"],
            ),
            GoldCoverageDimension(
                name=GoldCoverageDimensionName.POSSESSION,
                numerator=0,
                denominator=0,
                coverage=Decimal(1),
                state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
                reason_codes=("NO_POSSESSION_ELIGIBLE_ACTIONS",),
                zero_denominator_authority=authority["POSSESSION"],
            ),
            GoldCoverageDimension(
                name=GoldCoverageDimensionName.TEMPORAL,
                numerator=6,
                denominator=6,
                coverage=Decimal(1),
                state=GoldCoverageState.COMPLETE,
            ),
        ),
        coverage_overall=Decimal(0),
        missing_dimensions=(GoldCoverageDimensionName.ACTION,),
    )


def _gold_row(build_id: str) -> GoldPlayerWindow:
    tenant = TenantContext(tenant_id=UUID("65a43912-d412-5ff9-a364-7f84d1ad6c5d"))
    lineage = _row_lineage()
    proof = _temporal_proof()
    source_row = _match_source_row()
    player_id = UUID("be8da881-2b15-513f-978f-6bb3865bc8e2")
    team_id = UUID("5b353635-819b-5bd1-8ca2-5a7364042a96")
    match_id = UUID("bad97950-6fac-5cf0-a93c-094f91abbb9b")
    lineup = SilverLineupStint(
        build_id=build_id,
        tenant_context=tenant,
        source_completion_index_sha256=(
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
        ),
        source_rows=(source_row,),
        lineage=lineage,
        lineup_stint_id=UUID("591cdf5b-2281-53c4-8225-150313ca2c01"),
        match_id=match_id,
        player_id=player_id,
        team_id=team_id,
        start_interval=NominalMinuteInterval(lower=82, upper=83),
        end_interval=None,
        lower_bound_minutes=None,
        upper_bound_minutes=None,
        right_censored=True,
    )
    coverage = _zero_action_coverage()
    applicability = W04ApplicabilityAssessment(
        state=W04Applicability.SUPPRESSED,
        reason_codes=("ACTION_EVIDENCE_INCOMPLETE", "RIGHT_CENSORED_OR_UNCERTAIN"),
    )
    fact = SilverPlayerMatchFact(
        build_id=build_id,
        tenant_context=tenant,
        source_completion_index_sha256=lineup.source_completion_index_sha256,
        source_rows=(source_row,),
        lineage=lineage,
        source_manifest_id=UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b"),
        match_id=match_id,
        player_id=player_id,
        competition_id=UUID(COMPETITION_ID),
        season_id=bounded_season_uuid(181150),
        match_start_utc=datetime(2017, 8, 11, 18, 45, tzinfo=UTC),
        match_team_id=team_id,
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
        temporal_proof=proof,
    )
    return GoldPlayerWindow(
        build_id=build_id,
        tenant_context=tenant,
        source_completion_index_sha256=fact.source_completion_index_sha256,
        source_rows=(source_row,),
        lineage=lineage,
        player_id=player_id,
        competition_id=UUID(COMPETITION_ID),
        season_id=bounded_season_uuid(181150),
        role_context_id=UUID("3a17850f-5ac4-5ad8-ac9a-b753f10bdf77"),
        role_context_version="w04-neutral-role-context-v1",
        role_context_state="neutral_unscoped",
        window_definition_id=UUID(WINDOW_DEFINITION_ID),
        window_start_utc=datetime(2017, 8, 11, tzinfo=UTC),
        window_end_utc=datetime(2017, 8, 12, tzinfo=UTC),
        feature_cutoff_ts=datetime(2026, 8, 1, tzinfo=UTC),
        dependency_lineage_hash=proof.dependency_lineage_hash,
        feature_schema_hash=proof.feature_schema_hash,
        temporal_proof=proof,
        coverage=coverage,
        applicability=applicability,
        features=GoldFeatureValues(
            action_count=0,
            coordinate_known_action_count=0,
            match_count=1,
            resolved_possession_action_count=0,
        ),
        contributing_player_match_facts=(fact,),
        contributing_player_match_keys=(fact.primary_key,),
    )


def _gold_product(
    build_id: str, parent_path: str
) -> tuple[GoldProductReadback, str, str, int, str]:
    gold = _gold_row(build_id)
    row = gold.model_dump(mode="json")
    proof_bytes = canonical_json_bytes(gold.temporal_proof)
    return _gold_product_from_row(row, parent_path=parent_path, proof_bytes=proof_bytes)


def _gold_product_from_row(
    row: dict[str, object],
    *,
    parent_path: str,
    proof_bytes: bytes,
) -> tuple[GoldProductReadback, str, str, int, str]:
    row_bytes = canonical_json_bytes(row) + b"\n"
    unavailable_physical = b"GOLD_PLAYER_WINDOW_SCHEMA_AUTHORITY_UNAVAILABLE"
    return (
        GoldProductReadback(
            contract_row_bytes=(row_bytes,),
            physical_bytes=unavailable_physical,
            temporal_proof_bytes=proof_bytes,
        ),
        hashlib.sha256(unavailable_physical).hexdigest(),
        REJECTED_CALLER_GOLD_SEMANTIC_CLAIM,
        len(unavailable_physical),
        hashlib.sha256(proof_bytes).hexdigest(),
    )


def _path(role: ProductPathRole, relative_path: str) -> WyscoutProductPath:
    return WyscoutProductPath(path_role=role, relative_path=relative_path)


def _entry(
    path: WyscoutProductPath,
    *,
    serializer: str,
    physical_sha256: str,
    semantic_sha256: str,
    size_bytes: int,
    parents: tuple[str, ...] = (),
) -> LayerManifestEntry:
    partitions = tuple(
        sorted(
            (
                ManifestPartitionValue(key=key, value=value)
                for segment in path.relative_path.split("/")
                if "=" in segment
                for key, value in (segment.split("=", 1),)
            ),
            key=lambda item: item.key,
        )
    )
    return LayerManifestEntry(
        path=path,
        serializer=serializer,
        serializer_version="w04-contract-fixture-v1",
        schema_role=path.path_role.value,
        row_count=1,
        semantic_sha256=semantic_sha256,
        physical_sha256=physical_sha256,
        size_bytes=size_bytes,
        ordered_parent_paths=parents,
        partition_values=partitions,
        classification=accepted_source_classification(),
    )


def _manifest_summary(
    manifest: LayerManifest | dict[str, object],
) -> tuple[LayerManifestSummary, bytes]:
    parsed = manifest.model_dump(mode="json") if isinstance(manifest, LayerManifest) else manifest
    layer = str(parsed["layer"])
    build_id = str(parsed["build_id"])
    physical = canonical_json_bytes(parsed, terminal_lf=True)
    summary = LayerManifestSummary.model_validate(
        {
            "layer": layer,
            "manifest_relative_path": (
                f"data/manifests/wyscout/v5/{layer.lower()}/{build_id}.manifest.json"
            ),
            "manifest_sha256": hashlib.sha256(physical).hexdigest(),
            "manifest_size_bytes": len(physical),
            "semantic_sha256": layer_manifest_semantic_sha256(parsed),
        }
    )
    return summary, physical


def _manifest_population(
    build_id: str,
) -> tuple[
    tuple[LayerManifestSummary, ...],
    tuple[bytes, ...],
    GoldProductReadback,
    tuple[str, str, int, str],
]:
    bronze_path = _path(
        ProductPathRole.BRONZE_KNOWN_RECORD,
        f"data/working/wyscout/v5/bronze/build_id={build_id}/records/record_kind=action/"
        "source_sha256=301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad/"
        "part-00000.parquet",
    )
    silver_path = _path(
        ProductPathRole.SILVER_PLAYER_MATCH_FACT,
        f"data/working/wyscout/v5/silver/build_id={build_id}/player-match-fact/"
        "source_partition=england/part-00000.parquet",
    )
    gold_readback, physical, semantic, size, proof_digest = _gold_product(
        build_id, silver_path.relative_path
    )
    lineage = _data_lineage()
    common: dict[str, object] = {
        "build_id": build_id,
        "source_manifest_id": UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b"),
        "source_manifest_sha256": (
            "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
        ),
        "source_completion_index_sha256": (
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
        ),
        "tenant_context": TenantContext(tenant_id=UUID("65a43912-d412-5ff9-a364-7f84d1ad6c5d")),
        "classification": accepted_source_classification(),
        "source_available_at": datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC),
        "source_acquired_at": accepted_source_authority().acquired_at,
        "authority_clocks": accepted_data_authority_clocks(),
        "feature_schema_hash": ("49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"),
        "dependency_lineage_hash": lineage.lineage_hash,
        "dependency_lineage": lineage,
    }
    bronze = LayerManifest.model_validate(
        {
            **common,
            "layer": Layer.BRONZE,
            "manifest_path": _path(
                ProductPathRole.BRONZE_MANIFEST, layer_manifest_path("BRONZE", build_id)
            ),
            "entries": (
                _entry(
                    bronze_path,
                    serializer="bronze.py",
                    physical_sha256=H1,
                    semantic_sha256=H2,
                    size_bytes=1,
                ),
            ),
            "parent_layer_manifests": (),
        }
    )
    bronze_summary, bronze_bytes = _manifest_summary(bronze)
    silver = LayerManifest.model_validate(
        {
            **common,
            "layer": Layer.SILVER,
            "manifest_path": _path(
                ProductPathRole.SILVER_MANIFEST, layer_manifest_path("SILVER", build_id)
            ),
            "entries": (
                _entry(
                    silver_path,
                    serializer="player_match.py",
                    physical_sha256=H3,
                    semantic_sha256=H4,
                    size_bytes=1,
                    parents=(bronze_path.relative_path,),
                ),
            ),
            "parent_layer_manifests": (
                ParentLayerManifest(
                    layer=Layer.BRONZE,
                    build_id=build_id,
                    relative_path=bronze_summary.manifest_relative_path,
                    sha256=bronze_summary.manifest_sha256,
                ),
            ),
        }
    )
    silver_summary, silver_bytes = _manifest_summary(silver)
    gold = LayerManifest.model_validate(
        {
            **common,
            "layer": Layer.GOLD,
            "manifest_path": _path(
                ProductPathRole.GOLD_MANIFEST, layer_manifest_path("GOLD", build_id)
            ),
            "entries": (
                _entry(
                    _path(ProductPathRole.GOLD_PLAYER_WINDOW, _gold_path(build_id)),
                    serializer="gold.py",
                    physical_sha256=physical,
                    semantic_sha256=semantic,
                    size_bytes=size,
                    parents=(silver_path.relative_path,),
                ),
            ),
            "parent_layer_manifests": (
                ParentLayerManifest(
                    layer=Layer.SILVER,
                    build_id=build_id,
                    relative_path=silver_summary.manifest_relative_path,
                    sha256=silver_summary.manifest_sha256,
                ),
            ),
        }
    )
    gold_summary, gold_bytes = _manifest_summary(gold)
    return (
        (bronze_summary, silver_summary, gold_summary),
        (bronze_bytes, silver_bytes, gold_bytes),
        gold_readback,
        (physical, semantic, size, proof_digest),
    )


def _boundary(
    build_id: str,
    *,
    gold_manifest_sha256: str = H9,
    gold_product_physical_sha256: str = HE,
    gold_product_semantic_sha256: str = HF,
    temporal_proof_sha256: str = H1,
    checked_at: str = "2026-08-01T00:00:02Z",
) -> TemporalBoundaryReceipt:
    gold_path = _gold_path(build_id)
    return TemporalBoundaryReceipt(
        build_id=build_id,
        checked_at=checked_at,
        dependency_lineage_hash=accepted_dependency_lineage_hash(),
        gold_manifest_relative_path=gold_manifest_path(build_id),
        gold_manifest_sha256=gold_manifest_sha256,
        gold_product_physical_sha256=gold_product_physical_sha256,
        gold_product_relative_path=gold_path,
        gold_product_semantic_sha256=gold_product_semantic_sha256,
        gold_relative_path_sha256=hashlib.sha256(gold_path.encode()).hexdigest(),
        run_id=RUN_ID,
        temporal_proof_sha256=temporal_proof_sha256,
    )


def _receipt(
    boundary: TemporalBoundaryReceipt,
    *,
    layer_summaries: tuple[LayerManifestSummary, ...] | None = None,
    started_at: str = "2026-08-01T00:00:01Z",
    completed_at: str = "2026-08-01T00:00:03Z",
) -> tuple[RebuildInvocationReceipt, bytes]:
    invocation = invocation_from_projection(_projection())
    physical = canonical_json_bytes(boundary, terminal_lf=True)
    boundary_summary = BoundaryReceiptSummary(
        gold_relative_path=boundary.gold_product_relative_path,
        relative_path=boundary_receipt_path(
            invocation.build_id, RUN_ID, boundary.gold_product_relative_path
        ),
        sha256=hashlib.sha256(physical).hexdigest(),
        size_bytes=len(physical),
    )
    return (
        RebuildInvocationReceipt(
            boundary_receipts=(boundary_summary,),
            build_id=invocation.build_id,
            completed_at=completed_at,
            layer_manifests=(
                _layer_summaries(invocation.build_id)
                if layer_summaries is None
                else layer_summaries
            ),
            rebuild_invocation=invocation,
            run_id=RUN_ID,
            started_at=started_at,
        ),
        physical,
    )


def _validate_receipt(
    receipt: RebuildInvocationReceipt,
    population: tuple[tuple[TemporalBoundaryReceipt, bytes], ...],
    manifests: tuple[bytes, ...],
    gold_readback: GoldProductReadback,
) -> None:
    validate_receipt_closure(receipt, population, manifests, gold_readback)


def _composed_receipt(
    *, checked_at: str = "2026-08-01T00:00:02Z"
) -> tuple[
    RebuildInvocationReceipt,
    TemporalBoundaryReceipt,
    bytes,
    tuple[bytes, ...],
    GoldProductReadback,
]:
    invocation = invocation_from_projection(_projection())
    summaries, manifests, gold_readback, digests = _manifest_population(invocation.build_id)
    physical, semantic, _size, proof_digest = digests
    boundary = _boundary(
        invocation.build_id,
        gold_manifest_sha256=summaries[2].manifest_sha256,
        gold_product_physical_sha256=physical,
        gold_product_semantic_sha256=semantic,
        temporal_proof_sha256=proof_digest,
        checked_at=checked_at,
    )
    receipt, boundary_bytes = _receipt(boundary, layer_summaries=summaries)
    return receipt, boundary, boundary_bytes, manifests, gold_readback


def _recompose_manifest_objects(
    manifests: tuple[dict[str, object], ...],
    gold_readback: GoldProductReadback,
) -> tuple[
    RebuildInvocationReceipt,
    TemporalBoundaryReceipt,
    bytes,
    tuple[bytes, ...],
    GoldProductReadback,
]:
    invocation = invocation_from_projection(_projection())
    summary_physical = tuple(_manifest_summary(manifest) for manifest in manifests)
    summaries = tuple(row[0] for row in summary_physical)
    population = tuple(row[1] for row in summary_physical)
    gold = manifests[2]["entries"]
    gold_entry = (
        gold[0] if isinstance(gold, list) and len(gold) == 1 and isinstance(gold[0], dict) else {}
    )
    physical = str(gold_entry.get("physical_sha256", H1))
    semantic = str(gold_entry.get("semantic_sha256", H1))
    boundary = _boundary(
        invocation.build_id,
        gold_manifest_sha256=summaries[2].manifest_sha256,
        gold_product_physical_sha256=physical,
        gold_product_semantic_sha256=semantic,
        temporal_proof_sha256=hashlib.sha256(gold_readback.temporal_proof_bytes).hexdigest(),
    )
    receipt, boundary_bytes = _receipt(boundary, layer_summaries=summaries)
    return receipt, boundary, boundary_bytes, population, gold_readback


def _components() -> dict[str, object]:
    values: dict[str, object] = {}
    for key in COMPONENT_KEYS:
        if key == "selector":
            values[key] = {
                "algorithm": "w04-packaging-tag-bootstrap-v1",
                "ordered_tags": ["cp312-cp312-macosx_11_0_arm64"],
            }
        elif key == "uv_version":
            values[key] = "uv 0.9.21 (Homebrew 2025-12-30)"
        else:
            values[key] = H1
    return values


def _component_proofs(
    components: dict[str, object], counts: tuple[int, ...] = tuple(range(1, 21))
) -> tuple[ComponentProofResult, ...]:
    return tuple(
        ComponentProofResult.model_validate(
            {
                "component_key": key,
                "evidence_row_count": count,
                "value_json_sha256": sha256_json(components[key]),
            }
        )
        for key, count in zip(COMPONENT_KEYS, counts, strict=True)
    )


def _admission_result(
    components: dict[str, object] | None = None,
    counts: tuple[int, ...] = tuple(range(1, 21)),
) -> PreBuildAdmissionResult:
    components = _components() if components is None else components
    proofs = _component_proofs(components, counts)
    environment_digest = sha256_json(components)
    manifest = {
        **components,
        "environment_digest": environment_digest,
        "repository_code_sha256": H3,
        "schema_version": "w04-code-environment-admission-v16",
    }
    manifest_bytes = canonical_json_bytes(manifest)
    return PreBuildAdmissionResult(
        admission_prefix_relative_path=(
            "data/working/wyscout/v5/.staging/admission/"
            f"admission_run_id={ADMISSION_RUN_ID}/runtime-pycache"
        ),
        admission_run_id=ADMISSION_RUN_ID,
        canonical_manifest_bytes_b64u=base64.urlsafe_b64encode(manifest_bytes).decode().rstrip("="),
        canonical_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        component_proofs=proofs,
        component_proofs_sha256=sha256_json([row.model_dump(mode="json") for row in proofs]),
        environment_digest=environment_digest,
        repository_code_sha256=H3,
    )


def _validate_admission(result: PreBuildAdmissionResult) -> None:
    validate_admission_component_authority(
        result,
        _components(),
        tuple(zip(COMPONENT_KEYS, range(1, 21), strict=True)),
    )


def _entrypoint(role: str) -> EntrypointSourceResult:
    path = ADMISSION_ARGV[-1] if role == "PRE_BUILD_ADMISSION" else REBUILD_ARGV[-1]
    return EntrypointSourceResult.model_validate(
        {
            "descriptor_cloexec": False,
            "descriptor_inheritable": True,
            "descriptor_number": 3,
            "device": 0,
            "inode": 1,
            "link_count": 1,
            "mode": 420,
            "offset_after": 0,
            "offset_before": 0,
            "relative_path": path,
            "role": role,
            "sha256": H1,
            "size_bytes": 1,
            "source_eof": True,
        }
    )


def _runtime_subset() -> tuple[tuple[RuntimeSubsetObservation, ...], str]:
    rows = (
        RuntimeSubsetObservation(
            observation_kind="MODULE_SOURCE",
            owner_name="pydantic",
            owner_version="2.12.5",
            site_relative_path="pydantic/__init__.py",
            subject_name="pydantic",
        ),
    )
    digest = sha256_json(
        {
            "algorithm": "w04-normalized-runtime-subset-observations-v1",
            "rows": [row.model_dump(mode="json") for row in rows],
        }
    )
    return rows, digest


def _rebuild_result(child_environment_sha256: str = H2) -> PostBuildIdRebuildResult:
    invocation = invocation_from_projection(_projection())
    layers = _layer_summaries(invocation.build_id)
    receipt = RebuildReceiptSummary(
        relative_path=rebuild_receipt_path(invocation.build_id, RUN_ID),
        sha256=H1,
        size_bytes=1,
    )
    runtime_rows, runtime_digest = _runtime_subset()
    recheck = FinalRecheckResult(
        build_id=invocation.build_id,
        child_environment_sha256=child_environment_sha256,
        entrypoint_sha256=H1,
        environment_digest=H2,
        layer_manifest_set_sha256=sha256_json([row.model_dump(mode="json") for row in layers]),
        rebuild_receipt_sha256=receipt.sha256,
        repository_code_sha256=H3,
        repository_pyc_inventory_sha256=H4,
        resource_digest=H5,
        run_id=RUN_ID,
        runtime_subset_digest=runtime_digest,
        runtime_subset_rows=runtime_rows,
        site_pyc_inventory_sha256=H7,
    )
    return PostBuildIdRebuildResult(
        build_id=invocation.build_id,
        final_recheck=recheck,
        layer_manifests=layers,
        rebuild_prefix_relative_path=(
            f"data/working/wyscout/v5/.staging/{invocation.build_id}/{RUN_ID}/runtime-pycache"
        ),
        rebuild_receipt=receipt,
        run_id=RUN_ID,
    )


def test_exact_window_bytes_uuid_and_half_open_clock_contract() -> None:
    window = accepted_window_identity()
    assert tuple(type(window).model_fields) == (
        "match_id",
        "source_manifest_id",
        "window_end_utc",
        "window_schema_version",
        "window_start_utc",
    )
    raw = canonical_json_bytes(window)
    assert len(raw) == 250
    assert hashlib.sha256(raw).hexdigest() == WINDOW_BYTES_SHA256
    namespace = uuid5(NAMESPACE_URL, WINDOW_NAMESPACE_NAME)
    assert str(uuid5(namespace, f"single-match-poc:{WINDOW_BYTES_SHA256}")) == WINDOW_DEFINITION_ID

    validate_window_clocks(
        match_start_ts=SELECTED_MATCH_START_TS,
        snapshot_as_of_ts=SNAPSHOT_AS_OF_TS,
        dependency_clocks=("2020-01-28T14:24:27Z", DEPENDENCY_WATERMARK),
        dependency_watermark=DEPENDENCY_WATERMARK,
        valid_from=DEPENDENCY_WATERMARK,
    )
    for changed in (WINDOW_START_UTC, WINDOW_END_UTC, FEATURE_CUTOFF_TS):
        with pytest.raises(ValueError):
            validate_window_clocks(
                match_start_ts=changed,
                snapshot_as_of_ts=SNAPSHOT_AS_OF_TS,
                dependency_clocks=(DEPENDENCY_WATERMARK,),
                dependency_watermark=DEPENDENCY_WATERMARK,
                valid_from=DEPENDENCY_WATERMARK,
            )
    with pytest.raises(ValueError):
        validate_window_clocks(
            match_start_ts=SELECTED_MATCH_START_TS,
            snapshot_as_of_ts=SNAPSHOT_AS_OF_TS,
            dependency_clocks=(FEATURE_CUTOFF_TS,),
            dependency_watermark=FEATURE_CUTOFF_TS,
            valid_from=FEATURE_CUTOFF_TS,
        )


@pytest.mark.parametrize("rejected", [True, False, 181150.0, "181150", None, 181149, 181151])
def test_bounded_season_uuid_rejects_every_non_exact_integer(rejected: object) -> None:
    with pytest.raises(ValueError):
        bounded_season_uuid(rejected)


def test_bounded_season_uuid_reproduces_sole_uuidv5_chain() -> None:
    season_id = bounded_season_uuid(181150)
    assert type(season_id) is UUID
    assert str(season_id) == "4696aa1f-b512-5d18-af79-33cf031455cf"


def test_canonical_json_rejects_duplicates_whitespace_floats_lf_and_noncanonical_nfc() -> None:
    assert canonical_json_bytes({"b": 2, "a": "é"}) == '{"a":"é","b":2}'.encode()
    with pytest.raises(ValueError):
        canonical_json_bytes({"a": "e\u0301"})
    assert load_canonical_json(b'{"a":1}') == {"a": 1}
    for raw in (b'{"a":1,"a":1}', b'{"a": 1}', b'{"a":1}\n'):
        with pytest.raises(ValueError):
            load_canonical_json(raw)
    with pytest.raises(TypeError):
        canonical_json_bytes({"a": 1.0})
    assert load_canonical_json(b'{"a":1}\n', terminal_lf=True) == {"a": 1}
    with pytest.raises(ValueError):
        load_canonical_json(b'{"a":1}\n\n', terminal_lf=True)


def test_exact_five_authority_rows_only_inside_unchanged_projection_member() -> None:
    rows = accepted_authority_rows()
    assert len(rows) == 5
    assert tuple(row.authority_kind for row in rows) == (
        "FIELD",
        "POSSESSION",
        "SUPPORTED_FEATURE",
        "IDENTITY",
        "SEASON_LINEUP_PRODUCT_BINDING",
    )
    assert tuple(AuthorityRow.model_fields) == (
        "acceptance_id",
        "acceptance_sha256",
        "authority_kind",
        "candidate_id",
        "candidate_sha256",
        "review_id",
        "review_sha256",
    )
    assert "season" not in PRE_BUILD_PROJECTION_KEYS
    assert "season" not in POST_HASH_INVOCATION_KEYS
    changed = rows[0].model_dump()
    changed["review_sha256"] = H1
    with pytest.raises(ValidationError):
        AuthorityRow.model_validate(changed)


def test_projection_has_exact_25_keys_and_one_hash_strict_inverse() -> None:
    projection = _projection()
    assert tuple(type(projection).model_fields) == PRE_BUILD_PROJECTION_KEYS
    assert len(projection.model_dump()) == 25
    build_id = build_id_for_projection(projection)
    assert build_id == hashlib.sha256(canonical_json_bytes(projection)).hexdigest()
    invocation = invocation_from_projection(projection)
    assert tuple(type(invocation).model_fields) == POST_HASH_INVOCATION_KEYS
    assert len(invocation.model_dump()) == 25
    assert invocation.build_id == build_id
    assert projection_from_invocation(invocation) == projection
    before = projection.model_dump(mode="json")
    after = invocation.model_dump(mode="json")
    assert set(before) - set(after) == {"schema_version"}
    assert set(after) - set(before) == {"build_id"}
    assert all(before[key] == after[key] for key in set(before) & set(after))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_bundle_digest", SCHEMA_BUNDLE_V1_SHA256),
        ("tenant_id", "11111111-1111-5111-8111-111111111111"),
        ("tenant_club_id", "11111111-1111-5111-8111-111111111111"),
        ("feature_cutoff_ts", "2026-08-01T00:00:01Z"),
        ("window_start_utc", WINDOW_END_UTC),
    ],
)
def test_projection_rejects_substituted_or_placeholder_inputs(field: str, value: object) -> None:
    malformed = _projection().model_dump(mode="json")
    malformed[field] = value
    with pytest.raises(ValidationError):
        PreBuildProjection.model_validate(malformed)


def test_projection_rejects_sixth_authority_26th_key_reordering_and_boolean_integer() -> None:
    malformed = _projection().model_dump(mode="json")
    malformed["unknown_26th_key"] = H1
    with pytest.raises(ValidationError):
        PreBuildProjection.model_validate(malformed)
    malformed = _projection().model_dump(mode="json")
    malformed["authority_rows"].append(deepcopy(malformed["authority_rows"][0]))
    with pytest.raises(ValidationError):
        PreBuildProjection.model_validate(malformed)
    malformed = _projection().model_dump(mode="json")
    malformed["authority_rows"][0], malformed["authority_rows"][1] = (
        malformed["authority_rows"][1],
        malformed["authority_rows"][0],
    )
    with pytest.raises(ValidationError):
        PreBuildProjection.model_validate(malformed)
    with pytest.raises(ValidationError):
        LayerManifestSummary(
            layer="BRONZE",
            manifest_relative_path=layer_manifest_path("BRONZE", H1),
            manifest_sha256=H1,
            manifest_size_bytes=True,
            semantic_sha256=H2,
        )


def test_invocation_rejects_build_substitution_second_hash_and_projection_alias() -> None:
    invocation = invocation_from_projection(_projection())
    malformed = invocation.model_dump(mode="json")
    malformed["build_id"] = H9
    with pytest.raises(ValidationError):
        RebuildInvocation.model_validate(malformed)
    malformed = invocation.model_dump(mode="json")
    malformed["schema_version"] = "w04-rebuild-invocation-v1"
    with pytest.raises(ValidationError):
        RebuildInvocation.model_validate(malformed)


def test_receipt_models_have_exact_closed_key_rosters_and_clock_closure() -> None:
    receipt, boundary, physical, manifests, gold = _composed_receipt()
    assert tuple(TemporalBoundaryReceipt.model_fields) == (
        "build_id",
        "checked_at",
        "dependency_lineage_hash",
        "feature_cutoff_ts",
        "gold_manifest_relative_path",
        "gold_manifest_sha256",
        "gold_product_physical_sha256",
        "gold_product_relative_path",
        "gold_product_semantic_sha256",
        "gold_relative_path_sha256",
        "row_count",
        "run_id",
        "schema_version",
        "temporal_proof_sha256",
        "verification_state",
    )
    assert tuple(RebuildInvocationReceipt.model_fields) == (
        "boundary_receipts",
        "build_id",
        "completed_at",
        "layer_manifests",
        "rebuild_invocation",
        "result_state",
        "run_id",
        "schema_version",
        "started_at",
    )
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        _validate_receipt(receipt, ((boundary, physical),), manifests, gold)


def test_receipt_closure_rejects_omission_mutation_and_clock_substitution() -> None:
    receipt, boundary, physical, manifests, gold = _composed_receipt()
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        _validate_receipt(receipt, (), manifests, gold)
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        _validate_receipt(receipt, ((boundary, physical + b" "),), manifests, gold)
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        changed_gold = GoldProductReadback(
            contract_row_bytes=gold.contract_row_bytes,
            physical_bytes=b"coherent-caller-digest-substitution",
            temporal_proof_bytes=gold.temporal_proof_bytes,
        )
        validate_receipt_closure(
            receipt,
            ((boundary, physical),),
            manifests,
            changed_gold,
        )
    late_receipt, late, late_physical, late_manifests, late_gold = _composed_receipt(
        checked_at="2026-08-01T00:00:04Z"
    )
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        _validate_receipt(late_receipt, ((late, late_physical),), late_manifests, late_gold)


def test_caller_schema_table_fixture_or_equivalent_authority_is_unrepresentable() -> None:
    assert tuple(field.name for field in dataclass_fields(GoldProductReadback)) == (
        "contract_row_bytes",
        "physical_bytes",
        "temporal_proof_bytes",
    )
    with pytest.raises(TypeError):
        GoldProductReadback(  # type: ignore[call-arg]
            table=object(),
            schema=object(),
            projection_descriptor=object(),
            contract_row_bytes=(b"{}\n",),
            physical_bytes=b"caller-claim",
            temporal_proof_bytes=b"{}",
        )

    receipt, boundary, boundary_bytes, manifests, gold = _composed_receipt()
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        _validate_receipt(receipt, ((boundary, boundary_bytes),), manifests, gold)


def test_fixed_caller_semantic_claim_cannot_authorize_receipt_closure() -> None:
    receipt, boundary, boundary_bytes, manifests, gold = _composed_receipt()
    gold_manifest = cast(dict[str, object], load_canonical_json(manifests[2], terminal_lf=True))
    gold_entries = cast(list[dict[str, object]], gold_manifest["entries"])
    assert gold_entries[0]["semantic_sha256"] == REJECTED_CALLER_GOLD_SEMANTIC_CLAIM
    assert boundary.gold_product_semantic_sha256 == REJECTED_CALLER_GOLD_SEMANTIC_CLAIM
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        _validate_receipt(receipt, ((boundary, boundary_bytes),), manifests, gold)


def test_receipts_reject_paths_layers_build_run_and_unknown_fields() -> None:
    invocation = invocation_from_projection(_projection())
    boundary = _boundary(invocation.build_id)
    malformed = boundary.model_dump(mode="json")
    malformed["gold_relative_path_sha256"] = H1
    with pytest.raises(ValidationError):
        TemporalBoundaryReceipt.model_validate(malformed)
    receipt, _ = _receipt(boundary)
    malformed_receipt = receipt.model_dump(mode="json")
    malformed_receipt["layer_manifests"].reverse()
    with pytest.raises(ValidationError):
        RebuildInvocationReceipt.model_validate(malformed_receipt)
    malformed_receipt = receipt.model_dump(mode="json")
    malformed_receipt["unknown"] = None
    with pytest.raises(ValidationError):
        RebuildInvocationReceipt.model_validate(malformed_receipt)


def test_gold_path_rejects_former_generic_uuidv5_competition() -> None:
    invocation = invocation_from_projection(_projection())
    accepted = _gold_path(invocation.build_id)
    former = accepted.replace(COMPETITION_ID, FORMER_R1_COMPETITION_ID)
    malformed = _boundary(invocation.build_id).model_dump(mode="json")
    malformed["gold_product_relative_path"] = former
    malformed["gold_relative_path_sha256"] = hashlib.sha256(former.encode()).hexdigest()
    with pytest.raises(ValidationError):
        TemporalBoundaryReceipt.model_validate(malformed)


def test_composed_manifest_closure_rejects_each_summary_physical_and_semantic_substitution() -> (
    None
):
    receipt, boundary, boundary_bytes, manifests, gold = _composed_receipt()
    for index in range(3):
        for field, value in (
            ("manifest_sha256", H1),
            ("manifest_size_bytes", 1),
            ("semantic_sha256", H2),
        ):
            summaries = list(receipt.layer_manifests)
            summaries[index] = summaries[index].model_copy(update={field: value})
            changed = receipt.model_copy(update={"layer_manifests": tuple(summaries)})
            with pytest.raises(ValueError):
                _validate_receipt(changed, ((boundary, boundary_bytes),), manifests, gold)


def test_manifest_semantic_substitution_survives_downstream_rehash_but_not_receipt_closure() -> (
    None
):
    receipt, boundary, boundary_bytes, manifests, gold = _composed_receipt()
    summaries = list(receipt.layer_manifests)
    summaries[0] = summaries[0].model_copy(update={"semantic_sha256": H1})
    changed_receipt = receipt.model_copy(update={"layer_manifests": tuple(summaries)})
    receipt_physical = canonical_json_bytes(changed_receipt, terminal_lf=True)
    receipt_summary = RebuildReceiptSummary(
        relative_path=rebuild_receipt_path(receipt.build_id, RUN_ID),
        sha256=hashlib.sha256(receipt_physical).hexdigest(),
        size_bytes=len(receipt_physical),
    )
    runtime_rows, runtime_digest = _runtime_subset()
    recheck = FinalRecheckResult(
        build_id=receipt.build_id,
        child_environment_sha256=H2,
        entrypoint_sha256=H1,
        environment_digest=H2,
        layer_manifest_set_sha256=sha256_json([row.model_dump(mode="json") for row in summaries]),
        rebuild_receipt_sha256=receipt_summary.sha256,
        repository_code_sha256=H3,
        repository_pyc_inventory_sha256=H4,
        resource_digest=H5,
        run_id=RUN_ID,
        runtime_subset_digest=runtime_digest,
        runtime_subset_rows=runtime_rows,
        site_pyc_inventory_sha256=H7,
    )
    rebuild = PostBuildIdRebuildResult(
        build_id=receipt.build_id,
        final_recheck=recheck,
        layer_manifests=tuple(summaries),
        rebuild_prefix_relative_path=(
            f"data/working/wyscout/v5/.staging/{receipt.build_id}/{RUN_ID}/runtime-pycache"
        ),
        rebuild_receipt=receipt_summary,
        run_id=RUN_ID,
    )
    ChildResultEnvelope(
        child_environment_sha256=H2,
        child_role="POST_BUILD_ID_REBUILD",
        entrypoint_source=_entrypoint("POST_BUILD_ID_REBUILD"),
        expected_repository_code_sha256=H3,
        launcher_sha256=H4,
        nonce=H5,
        ordered_argv_sha256=sha256_json(list(REBUILD_ARGV)),
        payload_kind="REBUILD_COMPLETION",
        result=rebuild,
    )
    with pytest.raises(ValueError):
        _validate_receipt(changed_receipt, ((boundary, boundary_bytes),), manifests, gold)


def test_composed_manifest_closure_rejects_physical_and_parsed_readback_substitution() -> None:
    receipt, boundary, boundary_bytes, manifests, gold = _composed_receipt()
    for index in range(3):
        changed = list(manifests)
        changed[index] += b" "
        with pytest.raises(ValueError):
            _validate_receipt(receipt, ((boundary, boundary_bytes),), tuple(changed), gold)
        changed = list(manifests)
        parsed = cast(dict[str, object], load_canonical_json(changed[index], terminal_lf=True))
        parsed["complete"] = False
        changed[index] = canonical_json_bytes(parsed, terminal_lf=True)
        with pytest.raises(ValueError):
            _validate_receipt(receipt, ((boundary, boundary_bytes),), tuple(changed), gold)


def test_r3_manifest_bytes_reject_r2_dict_and_model_construct_schema_bypasses() -> None:
    receipt, boundary, boundary_bytes, manifests, gold = _composed_receipt()
    parsed = tuple(
        cast(dict[str, object], load_canonical_json(row, terminal_lf=True)) for row in manifests
    )
    with pytest.raises(TypeError):
        validate_receipt_closure(
            receipt,
            ((boundary, boundary_bytes),),
            cast(Any, parsed),
            gold,
        )
    constructed = tuple(LayerManifest.model_construct(**cast(Any, row)) for row in parsed)
    with pytest.raises(TypeError):
        validate_receipt_closure(
            receipt,
            ((boundary, boundary_bytes),),
            cast(Any, constructed),
            gold,
        )
    for index in range(3):
        invalid = [deepcopy(row) for row in parsed]
        entries = cast(list[dict[str, object]], invalid[index]["entries"])
        invalid[index]["entries"] = [{"complete": True, "path": deepcopy(entries[0]["path"])}]
        invalid_bytes = tuple(canonical_json_bytes(row, terminal_lf=True) for row in invalid)
        with pytest.raises((ValueError, ValidationError, GoldSchemaAuthorityUnavailableError)):
            validate_receipt_closure(
                receipt,
                ((boundary, boundary_bytes),),
                invalid_bytes,
                gold,
            )


def test_gold_readback_rejects_malformed_logical_content_and_caller_physical_claim() -> None:
    receipt, boundary, boundary_bytes, manifests, gold = _composed_receipt()
    invalid_inputs = (
        GoldProductReadback(
            contract_row_bytes=(),
            physical_bytes=gold.physical_bytes,
            temporal_proof_bytes=gold.temporal_proof_bytes,
        ),
        GoldProductReadback(
            contract_row_bytes=gold.contract_row_bytes * 2,
            physical_bytes=gold.physical_bytes,
            temporal_proof_bytes=gold.temporal_proof_bytes,
        ),
        GoldProductReadback(
            contract_row_bytes=(b"{}\n",),
            physical_bytes=gold.physical_bytes,
            temporal_proof_bytes=gold.temporal_proof_bytes,
        ),
    )
    for invalid in invalid_inputs:
        with pytest.raises((ValueError, ValidationError)):
            _validate_receipt(receipt, ((boundary, boundary_bytes),), manifests, invalid)

    caller_claim = GoldProductReadback(
        contract_row_bytes=gold.contract_row_bytes,
        physical_bytes=b"coherent-caller-product-claim",
        temporal_proof_bytes=gold.temporal_proof_bytes,
    )
    with pytest.raises(GoldSchemaAuthorityUnavailableError):
        _validate_receipt(receipt, ((boundary, boundary_bytes),), manifests, caller_claim)


@pytest.mark.parametrize("mutation", ["window", "temporal"])
def test_r3_coherent_gold_and_temporal_rehash_cannot_authorize_changed_content(
    mutation: str,
) -> None:
    _, _, _, manifest_bytes, gold = _composed_receipt()
    manifests = [
        deepcopy(cast(dict[str, object], load_canonical_json(row, terminal_lf=True)))
        for row in manifest_bytes
    ]
    row = cast(
        dict[str, object],
        load_canonical_json(gold.contract_row_bytes[0][:-1]),
    )
    proof = cast(dict[str, object], deepcopy(row["temporal_proof"]))
    if mutation == "window":
        row["window_start_utc"] = "2017-08-10T00:00:00Z"
    else:
        proof["snapshot_as_of_ts"] = "2017-08-11T18:44:59Z"
        row["temporal_proof"] = proof
        facts = cast(list[dict[str, object]], row["contributing_player_match_facts"])
        facts[0]["temporal_proof"] = deepcopy(proof)
    gold_entry = cast(list[dict[str, object]], manifests[2]["entries"])[0]
    parent_path = cast(list[str], gold_entry["ordered_parent_paths"])[0]
    changed_gold, physical, semantic, size, _proof_digest = _gold_product_from_row(
        row,
        parent_path=parent_path,
        proof_bytes=canonical_json_bytes(proof),
    )
    gold_entry["physical_sha256"] = physical
    gold_entry["semantic_sha256"] = semantic
    gold_entry["size_bytes"] = size
    receipt, boundary, boundary_bytes, recomposed, changed_gold = _recompose_manifest_objects(
        tuple(manifests), changed_gold
    )
    with pytest.raises(ValueError):
        _validate_receipt(
            receipt,
            ((boundary, boundary_bytes),),
            recomposed,
            changed_gold,
        )


@pytest.mark.parametrize("manifest_index", [1, 2])
def test_composed_manifest_closure_rejects_parent_field_cardinality_and_order_after_rehash(
    manifest_index: int,
) -> None:
    _, _, _, population, gold = _composed_receipt()
    base_manifests = tuple(
        deepcopy(cast(dict[str, object], load_canonical_json(row, terminal_lf=True)))
        for row in population
    )
    for mutation in ("missing", "additional", "build_id", "layer", "relative_path", "sha256"):
        manifests = deepcopy(base_manifests)
        parents = manifests[manifest_index]["parent_layer_manifests"]
        assert isinstance(parents, list)
        if mutation == "missing":
            parents.clear()
        elif mutation == "additional":
            parents.append(deepcopy(parents[0]))
        else:
            parents[0][mutation] = H1
        receipt, boundary, boundary_bytes, recomposed, changed_gold = _recompose_manifest_objects(
            manifests, gold
        )
        with pytest.raises(ValueError):
            _validate_receipt(receipt, ((boundary, boundary_bytes),), recomposed, changed_gold)


def test_composed_manifest_closure_rejects_each_frozen_authority_after_downstream_rehash() -> None:
    _, _, _, population, gold = _composed_receipt()
    base_manifests = tuple(
        deepcopy(cast(dict[str, object], load_canonical_json(row, terminal_lf=True)))
        for row in population
    )
    fields = (
        "manifest_schema_version",
        "construction_authority_state",
        "layer",
        "build_id",
        "manifest_path",
        "complete",
        "source_manifest_id",
        "source_manifest_sha256",
        "source_completion_index_sha256",
        "tenant_context",
        "classification",
        "source_available_at",
        "source_acquired_at",
        "authority_clocks",
        "feature_schema_hash",
        "dependency_lineage_hash",
        "dependency_lineage",
    )
    for manifest_index in range(3):
        for field in fields:
            manifests = deepcopy(base_manifests)
            manifests[manifest_index][field] = H1
            with pytest.raises((ValueError, ValidationError)):
                receipt, boundary, boundary_bytes, recomposed, changed_gold = (
                    _recompose_manifest_objects(manifests, gold)
                )
                _validate_receipt(receipt, ((boundary, boundary_bytes),), recomposed, changed_gold)


def test_composed_manifest_closure_rejects_gold_role_path_cardinality_after_rehash() -> None:
    _, _, _, population, gold = _composed_receipt()
    base_manifests = tuple(
        deepcopy(cast(dict[str, object], load_canonical_json(row, terminal_lf=True)))
        for row in population
    )
    mutations = (
        "missing",
        "additional",
        "role",
        "competition",
        "physical_sha256",
        "semantic_sha256",
        "row_count",
    )
    for mutation in mutations:
        manifests = deepcopy(base_manifests)
        entries = manifests[2]["entries"]
        assert isinstance(entries, list)
        if mutation == "missing":
            entries.clear()
        elif mutation == "additional":
            entries.append(deepcopy(entries[0]))
        elif mutation == "role":
            entries[0]["path"]["path_role"] = "SILVER_ACTION"
        elif mutation == "competition":
            entries[0]["path"]["relative_path"] = entries[0]["path"]["relative_path"].replace(
                COMPETITION_ID, FORMER_R1_COMPETITION_ID
            )
        else:
            entries[0][mutation] = H1
        with pytest.raises((ValueError, ValidationError, GoldSchemaAuthorityUnavailableError)):
            receipt, boundary, boundary_bytes, recomposed, changed_gold = (
                _recompose_manifest_objects(manifests, gold)
            )
            _validate_receipt(receipt, ((boundary, boundary_bytes),), recomposed, changed_gold)


def test_result_role_models_have_exact_nine_rosters() -> None:
    expected: dict[type[Any], tuple[str, ...]] = {
        EntrypointSourceResult: (
            "descriptor_cloexec",
            "descriptor_inheritable",
            "descriptor_number",
            "device",
            "inode",
            "link_count",
            "mode",
            "offset_after",
            "offset_before",
            "relative_path",
            "role",
            "sha256",
            "size_bytes",
            "source_eof",
        ),
        ComponentProofResult: ("component_key", "evidence_row_count", "value_json_sha256"),
        RuntimeSubsetObservation: (
            "observation_kind",
            "owner_name",
            "owner_version",
            "site_relative_path",
            "subject_name",
        ),
        PreBuildAdmissionResult: (
            "admission_prefix_relative_path",
            "admission_run_id",
            "canonical_manifest_bytes_b64u",
            "canonical_manifest_sha256",
            "component_proofs",
            "component_proofs_sha256",
            "environment_digest",
            "manifest_schema_version",
            "repository_code_sha256",
        ),
        RebuildReceiptSummary: ("relative_path", "sha256", "size_bytes"),
        LayerManifestSummary: (
            "layer",
            "manifest_relative_path",
            "manifest_sha256",
            "manifest_size_bytes",
            "semantic_sha256",
        ),
        FinalRecheckResult: (
            "build_id",
            "child_environment_sha256",
            "entrypoint_descriptor_match",
            "entrypoint_sha256",
            "environment_digest",
            "in_place_pyc_unchanged",
            "layer_manifest_set_sha256",
            "rebuild_prefix_empty",
            "rebuild_receipt_sha256",
            "repository_code_sha256",
            "repository_pyc_inventory_sha256",
            "resource_digest",
            "run_id",
            "runtime_subset_digest",
            "runtime_subset_rows",
            "schema_version",
            "selected_prefix_role",
            "site_pyc_inventory_sha256",
        ),
        PostBuildIdRebuildResult: (
            "build_id",
            "final_recheck",
            "layer_manifests",
            "rebuild_prefix_relative_path",
            "rebuild_receipt",
            "run_id",
        ),
        ChildResultEnvelope: (
            "child_environment_sha256",
            "child_role",
            "entrypoint_source",
            "expected_repository_code_sha256",
            "launcher_sha256",
            "nonce",
            "ordered_argv_sha256",
            "payload_kind",
            "result",
            "schema_version",
        ),
    }
    assert len(expected) == 9
    for model, keys in expected.items():
        assert tuple(model.model_fields) == keys


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("observation_kind", "UNKNOWN"),
        ("observation_kind", None),
        ("observation_kind", 1),
        ("site_relative_path", "/absolute/demo.py"),
        ("site_relative_path", "demo/../demo.py"),
        ("site_relative_path", "demo\\demo.py"),
        ("site_relative_path", "demo/cache.PYC"),
        ("site_relative_path", "de\u0301mo.py"),
        ("subject_name", "not-a-module-key"),
    ),
)
def test_runtime_subset_observation_rejects_kind_path_nfc_and_pyc_attacks(
    field: str, value: object
) -> None:
    values: dict[str, object] = {
        "observation_kind": "MODULE_SOURCE",
        "owner_name": "demo",
        "owner_version": "1.0",
        "site_relative_path": "demo.py",
        "subject_name": "demo",
    }
    values[field] = value
    with pytest.raises(ValidationError):
        RuntimeSubsetObservation.model_validate(values)


def test_runtime_subset_field_validators_fail_with_validation_errors_not_key_errors() -> None:
    with pytest.raises(ValidationError):
        RuntimeSubsetObservation.model_validate(
            {
                "observation_kind": None,
                "owner_name": "demo",
                "owner_version": "1.0",
                "site_relative_path": "demo.py",
                "subject_name": "demo",
            }
        )
    values = _rebuild_result().final_recheck.model_dump(mode="json")
    values["runtime_subset_rows"] = None
    with pytest.raises(ValidationError):
        FinalRecheckResult.model_validate(values)


def test_final_recheck_rejects_runtime_row_omission_reorder_duplicate_and_digest_drift() -> None:
    base = _rebuild_result().final_recheck.model_dump(mode="json")
    second = RuntimeSubsetObservation(
        observation_kind="MODULE_SOURCE",
        owner_name="typing-extensions",
        owner_version="4.15.0",
        site_relative_path="typing_extensions.py",
        subject_name="typing_extensions",
    ).model_dump(mode="json")
    first = cast(list[dict[str, object]], base["runtime_subset_rows"])[0]
    ordered = sorted((first, second), key=canonical_json_bytes)
    attacks = []
    omitted = {**base, "runtime_subset_rows": []}
    omitted["runtime_subset_digest"] = sha256_json(
        {"algorithm": "w04-normalized-runtime-subset-observations-v1", "rows": []}
    )
    attacks.append(omitted)
    for rows in (list(reversed(ordered)), [ordered[0], ordered[0]]):
        changed = {**base, "runtime_subset_rows": rows}
        changed["runtime_subset_digest"] = sha256_json(
            {"algorithm": "w04-normalized-runtime-subset-observations-v1", "rows": rows}
        )
        attacks.append(changed)
    attacks.append({**base, "runtime_subset_digest": H1})
    for attacked in attacks:
        with pytest.raises(ValidationError):
            FinalRecheckResult.model_validate(attacked)


def test_runtime_result_contract_rejects_stale_r12_physical_versions() -> None:
    final_values = _rebuild_result().final_recheck.model_dump(mode="json")
    final_values["schema_version"] = "w04-rebuild-final-recheck-v1"
    with pytest.raises(ValidationError):
        FinalRecheckResult.model_validate(final_values)

    rebuild = _rebuild_result()
    child_values = ChildResultEnvelope(
        child_environment_sha256=H2,
        child_role="POST_BUILD_ID_REBUILD",
        entrypoint_source=_entrypoint("POST_BUILD_ID_REBUILD"),
        expected_repository_code_sha256=H3,
        launcher_sha256=H4,
        nonce=H5,
        ordered_argv_sha256=sha256_json(list(REBUILD_ARGV)),
        payload_kind="REBUILD_COMPLETION",
        result=rebuild,
    ).model_dump(mode="json")
    child_values["schema_version"] = "w04-child-result-v2"
    with pytest.raises(ValidationError):
        ChildResultEnvelope.model_validate(child_values)


def test_admission_result_validates_manifest_proofs_prefix_and_base64() -> None:
    result = _admission_result()
    assert len(result.component_proofs) == 20
    _validate_admission(result)
    malformed = result.model_dump(mode="json")
    malformed["component_proofs"].reverse()
    with pytest.raises(ValidationError):
        PreBuildAdmissionResult.model_validate(malformed)
    malformed = result.model_dump(mode="json")
    malformed["canonical_manifest_sha256"] = H1
    with pytest.raises(ValidationError):
        PreBuildAdmissionResult.model_validate(malformed)
    malformed = result.model_dump(mode="json")
    malformed["admission_run_id"] = True
    with pytest.raises(ValidationError):
        PreBuildAdmissionResult.model_validate(malformed)


def test_admission_rejects_missing_additional_operational_and_stale_manifest_fields() -> None:
    result = _admission_result()
    raw = base64.urlsafe_b64decode(
        result.canonical_manifest_bytes_b64u
        + "=" * (-len(result.canonical_manifest_bytes_b64u) % 4)
    )
    manifest = load_canonical_json(raw)
    assert isinstance(manifest, dict)
    for mutation in ("missing", "additional", "operational", "stale"):
        changed = deepcopy(manifest)
        if mutation == "missing":
            del changed[COMPONENT_KEYS[0]]
        elif mutation == "additional":
            changed["unknown_component"] = H1
        elif mutation == "operational":
            changed["run_id"] = RUN_ID
        else:
            changed["schema_version"] = "w04-code-environment-admission-v15"
        changed_bytes = canonical_json_bytes(changed)
        values = result.model_dump()
        values["canonical_manifest_bytes_b64u"] = (
            base64.urlsafe_b64encode(changed_bytes).decode().rstrip("=")
        )
        values["canonical_manifest_sha256"] = hashlib.sha256(changed_bytes).hexdigest()
        with pytest.raises(ValidationError):
            PreBuildAdmissionResult.model_validate(values)


def test_admission_each_component_value_is_internally_proven_and_independently_authorized() -> None:
    expected = _components()
    for key in COMPONENT_KEYS:
        changed = deepcopy(expected)
        if key == "selector":
            changed[key] = {"algorithm": "substituted", "ordered_tags": ["other"]}
        elif key == "uv_version":
            changed[key] = "uv 0.9.20 (substituted)"
        else:
            changed[key] = H2
        if key == "uv_version":
            with pytest.raises(ValidationError):
                _admission_result(changed)
            continue
        coherent_substitution = _admission_result(changed)
        with pytest.raises(ValueError):
            validate_admission_component_authority(
                coherent_substitution,
                expected,
                tuple(zip(COMPONENT_KEYS, range(1, 21), strict=True)),
            )


def test_admission_rejects_each_proof_digest_order_and_independent_count_substitution() -> None:
    result = _admission_result()
    for index in range(20):
        values = result.model_dump()
        proofs = list(values["component_proofs"])
        proofs[index] = {**proofs[index], "value_json_sha256": H2}
        values["component_proofs"] = tuple(proofs)
        values["component_proofs_sha256"] = sha256_json(proofs)
        with pytest.raises(ValidationError):
            PreBuildAdmissionResult.model_validate(values)

        changed_counts = list(range(1, 21))
        changed_counts[index] += 100
        coherent_count_substitution = _admission_result(counts=tuple(changed_counts))
        with pytest.raises(ValueError):
            _validate_admission(coherent_count_substitution)

    values = result.model_dump()
    proofs = list(values["component_proofs"])
    proofs[0], proofs[1] = proofs[1], proofs[0]
    values["component_proofs"] = tuple(proofs)
    values["component_proofs_sha256"] = sha256_json(proofs)
    with pytest.raises(ValidationError):
        PreBuildAdmissionResult.model_validate(values)
    with pytest.raises(ValueError):
        validate_admission_component_authority(
            result,
            _components(),
            tuple((key, True) for key in COMPONENT_KEYS),
        )


def test_admission_and_rebuild_child_envelopes_enforce_role_payload_and_argv() -> None:
    admission = _admission_result()
    envelope = ChildResultEnvelope(
        child_environment_sha256=H2,
        child_role="PRE_BUILD_ADMISSION",
        entrypoint_source=_entrypoint("PRE_BUILD_ADMISSION"),
        expected_repository_code_sha256=H3,
        launcher_sha256=H4,
        nonce=H5,
        ordered_argv_sha256=sha256_json(list(ADMISSION_ARGV)),
        payload_kind="CODE_ENVIRONMENT_MANIFEST",
        result=admission,
    )
    assert envelope.result == admission
    malformed = envelope.model_dump(mode="json")
    malformed["payload_kind"] = "REBUILD_COMPLETION"
    with pytest.raises(ValidationError):
        ChildResultEnvelope.model_validate(malformed)

    rebuild = _rebuild_result()
    rebuild_envelope = ChildResultEnvelope(
        child_environment_sha256=H2,
        child_role="POST_BUILD_ID_REBUILD",
        entrypoint_source=_entrypoint("POST_BUILD_ID_REBUILD"),
        expected_repository_code_sha256=H3,
        launcher_sha256=H4,
        nonce=H5,
        ordered_argv_sha256=sha256_json(list(REBUILD_ARGV)),
        payload_kind="REBUILD_COMPLETION",
        result=rebuild,
    )
    assert rebuild_envelope.result == rebuild
    malformed = rebuild_envelope.model_dump(mode="json")
    malformed["ordered_argv_sha256"] = H1
    with pytest.raises(ValidationError):
        ChildResultEnvelope.model_validate(malformed)


def test_entrypoint_and_rebuild_results_reject_substitutions_and_boolean_integers() -> None:
    entrypoint = _entrypoint("PRE_BUILD_ADMISSION")
    malformed = entrypoint.model_dump(mode="json")
    malformed["descriptor_number"] = True
    with pytest.raises(ValidationError):
        EntrypointSourceResult.model_validate(malformed)
    malformed = entrypoint.model_dump(mode="json")
    malformed["relative_path"] = REBUILD_ARGV[-1]
    with pytest.raises(ValidationError):
        EntrypointSourceResult.model_validate(malformed)
    rebuild = _rebuild_result()
    malformed = rebuild.model_dump(mode="json")
    malformed["final_recheck"]["layer_manifest_set_sha256"] = H1
    with pytest.raises(ValidationError):
        PostBuildIdRebuildResult.model_validate(malformed)


def test_r4_sole_two_key_complete_manifest_semantic_derivation_and_substitutions() -> None:
    complete_manifest = {
        "build_id": H1,
        "complete": True,
        "entries": [{"relative_path": "x", "semantic_sha256": H2}],
        "layer": "BRONZE",
        "manifest_schema_version": "w04-test-complete-layer-manifest-v2",
    }
    exact_preimage = {
        "layer_manifest": complete_manifest,
        "semantic_schema_version": "w04-wyscout-layer-manifest-semantic-v1",
    }
    derived = layer_manifest_semantic_sha256(complete_manifest)
    assert derived == hashlib.sha256(canonical_json_bytes(exact_preimage)).hexdigest()
    assert (
        derived
        != hashlib.sha256(canonical_json_bytes(exact_preimage, terminal_lf=True)).hexdigest()
    )
    assert derived != H2
    assert (
        derived
        != hashlib.sha256(canonical_json_bytes(complete_manifest, terminal_lf=True)).hexdigest()
    )

    summary = LayerManifestSummary(
        layer="BRONZE",
        manifest_relative_path=layer_manifest_path("BRONZE", H1),
        manifest_sha256=H3,
        manifest_size_bytes=1,
        semantic_sha256=derived,
    )
    validate_layer_manifest_semantic_binding(summary, complete_manifest)
    for substitution in (H2, H3, H4):
        malformed = summary.model_copy(update={"semantic_sha256": substitution})
        with pytest.raises(ValueError):
            validate_layer_manifest_semantic_binding(malformed, complete_manifest)
    expanded = deepcopy(complete_manifest)
    expanded["authority_clocks"] = {"new": "field"}
    assert layer_manifest_semantic_sha256(expanded) != derived

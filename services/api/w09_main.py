"""Loopback production composition root for the governed W09 workbench."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from fastapi import FastAPI
from pydantic import ValidationError

from scouting.api.research import ResearchApiError, ResearchApiRuntime
from scouting.contracts.research import (
    FeatureMatrixManifest,
    ResearchCapability,
    ResearchDatasetDescriptor,
    ResearchIndexManifest,
    ResearchVersionPins,
)
from scouting.modeling.research import (
    DEFAULT_INDEX_ROOT,
    DEFAULT_MATRIX_ARTIFACT_ROOT,
    LoadedFeatureMatrix,
    LoadedResearchIndex,
    ResearchIndexBuildError,
    discover_feature_matrix_manifest,
    load_feature_matrix,
    load_research_index,
)
from scouting.serving.research import ResearchServingError, ResearchServingService
from scouting.storage.embedded import (
    EmbeddedDatabaseConfigurationError,
    EmbeddedDatabaseMigrationError,
    create_embedded_engine,
)
from scouting.storage.guarded import GuardedStorage, StorageError
from scouting.storage.research import (
    RESEARCH_REPORT_ROOT_NAME,
    ResearchExperimentStore,
    ResearchStorageError,
)
from scouting.web.w09 import create_w09_app

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_ROOT = PROJECT_ROOT / "data/working/w09/research-reports"

_SOURCE_AVAILABLE_AT = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
_IDENTITY_AVAILABLE_AT = datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC)
_SOURCE_PLAYER_COUNT = 3_603
_SOURCE_TEAM_COUNT = 142
_SOURCE_MATCH_COUNT = 1_826
_SOURCE_ACTION_COUNT = 3_071_395
_ATTRIBUTION = (
    "Data source: Pappalardo et al., Soccer match event dataset, supplied by Wyscout, "
    "figshare collection v5, licensed CC BY 4.0."
)
_RIGHTS_LIMITATIONS = (
    "Retained historical 2017/18 evidence only; no current provider coverage.",
    (
        "Restricted to this local workbench; network transfer, deployment and publication "
        "are not authorised."
    ),
)
_HISTORICAL_BOUNDARY = (
    "Ranks show resemblance inside this governed historical population only. They do not "
    "predict performance or establish recruitment usefulness, value, availability or squad fit."
)


class W09ProductionBootstrapError(RuntimeError):
    """Exact governed production authorities cannot be composed safely."""


def _pins(
    matrix: FeatureMatrixManifest,
    index: ResearchIndexManifest,
) -> ResearchVersionPins:
    return ResearchVersionPins(
        feature_cutoff_ts=matrix.feature_cutoff_ts,
        dataset_version=matrix.dataset_version,
        dataset_manifest_digest=matrix.dataset_manifest_digest,
        identity_bundle_digest=matrix.identity_bundle_digest,
        canonical_build_digest=matrix.canonical_build_digest,
        matrix_version=matrix.matrix_version,
        matrix_manifest_digest=matrix.manifest_digest,
        matrix_digest=matrix.matrix_digest,
        feature_registry_version=matrix.feature_registry_version,
        feature_registry_digest=matrix.feature_registry_digest,
        eligibility_policy_version=matrix.eligibility_policy_version,
        eligibility_policy_digest=matrix.eligibility_policy_digest,
        model_version=index.model_version,
        model_configuration_digest=index.model_configuration_digest,
        scorer_version=index.scorer_version,
        scorer_code_digest=index.scorer_code_digest,
        index_version=index.index_version,
        index_manifest_digest=index.manifest_digest,
        catalogue_digest=index.catalogue_digest,
    )


def _dataset_descriptor(
    matrix: FeatureMatrixManifest,
    index: ResearchIndexManifest,
) -> ResearchDatasetDescriptor:
    if matrix.catalogue_player_count != _SOURCE_PLAYER_COUNT:
        raise W09ProductionBootstrapError(
            "feature manifest does not reconcile the retained 3,603-player source catalogue"
        )
    capabilities = (
        ResearchCapability.EXEMPLAR_QUERY,
        ResearchCapability.WEIGHTED_PROFILE_QUERY,
        ResearchCapability.WEIGHTED_EUCLIDEAN,
        ResearchCapability.WEIGHTED_COSINE,
        ResearchCapability.FEATURE_CONTRIBUTIONS,
        ResearchCapability.PLAYER_COMPARISON,
        ResearchCapability.SAVED_EXPERIMENT_REPLAY,
    )
    limitations = tuple(
        dict.fromkeys(
            (
                _HISTORICAL_BOUNDARY,
                *_RIGHTS_LIMITATIONS,
                *matrix.limitations,
                *index.limitations,
            )
        )
    )
    dataset_id = uuid5(
        NAMESPACE_URL,
        "\0".join(
            (
                "urn:scouting-intelligence:w09:retained-dataset:v1",
                matrix.dataset_version,
                matrix.dataset_manifest_digest,
                matrix.identity_bundle_digest,
            )
        ),
    )
    return ResearchDatasetDescriptor(
        dataset_id=dataset_id,
        dataset_version=matrix.dataset_version,
        dataset_manifest_digest=matrix.dataset_manifest_digest,
        provider_adapter="provider-neutral-w09-canonical-v1",
        provider_neutral_schema_version="w09-historical-canonical-v1",
        rights_classification="wyscout_figshare_v5_cc_by_4",
        attribution=_ATTRIBUTION,
        source_manifest_id=matrix.source_manifest_id,
        source_manifest_digest=matrix.source_manifest_digest,
        source_completion_digest=matrix.source_completion_digest,
        identity_bundle_digest=matrix.identity_bundle_digest,
        source_available_at=_SOURCE_AVAILABLE_AT,
        identity_available_at=_IDENTITY_AVAILABLE_AT,
        feature_cutoff_ts=matrix.feature_cutoff_ts,
        window_start_utc=matrix.window_start_utc,
        window_end_utc=matrix.window_end_utc,
        source_match_count=_SOURCE_MATCH_COUNT,
        source_action_count=_SOURCE_ACTION_COUNT,
        source_team_count=_SOURCE_TEAM_COUNT,
        source_player_count=_SOURCE_PLAYER_COUNT,
        capabilities=capabilities,
        limitations=limitations,
    )


def load_production_w09_runtime(
    *,
    utc_clock: Callable[[], datetime] | None = None,
) -> tuple[ResearchApiRuntime, ResearchServingService]:
    """Load one accepted matrix and its one fixed compatible local index."""

    try:
        manifest_path = discover_feature_matrix_manifest()
        matrix: LoadedFeatureMatrix = load_feature_matrix(
            manifest_path,
            artifact_root=DEFAULT_MATRIX_ARTIFACT_ROOT,
        )
        index: LoadedResearchIndex = load_research_index(
            DEFAULT_INDEX_ROOT,
            matrix_manifest=matrix.manifest,
        )
        serving = ResearchServingService(
            matrix=matrix,
            index=index,
            pins=_pins(matrix.manifest, index.manifest),
        )
        dataset = _dataset_descriptor(matrix.manifest, index.manifest)
        engine = create_embedded_engine()
        store = ResearchExperimentStore(
            engine,
            GuardedStorage({RESEARCH_REPORT_ROOT_NAME: DEFAULT_REPORT_ROOT}),
        )
        runtime = ResearchApiRuntime(
            dataset=dataset,
            serving=serving,
            store=store,
            retained_attribution=_ATTRIBUTION,
            rights_limitations=_RIGHTS_LIMITATIONS,
            utc_clock=utc_clock or (lambda: datetime.now(UTC)),
        )
    except (
        EmbeddedDatabaseConfigurationError,
        EmbeddedDatabaseMigrationError,
        OSError,
        ResearchApiError,
        ResearchIndexBuildError,
        ResearchServingError,
        ResearchStorageError,
        StorageError,
        TypeError,
        ValidationError,
        ValueError,
    ) as exc:
        raise W09ProductionBootstrapError(str(exc)) from exc
    return runtime, serving


def create_production_w09_app() -> FastAPI:
    """Start live only for one accepted authority; otherwise remain honestly closed."""

    try:
        runtime, serving = load_production_w09_runtime()
    except W09ProductionBootstrapError as exc:
        return create_w09_app(
            runtime=None,
            serving=None,
            unavailable_reason=f"Governed historical research artifacts are unavailable: {exc}",
        )
    return create_w09_app(runtime=runtime, serving=serving)


app = create_production_w09_app()

__all__ = [
    "DEFAULT_REPORT_ROOT",
    "W09ProductionBootstrapError",
    "app",
    "create_production_w09_app",
    "load_production_w09_runtime",
]

"""End-to-end HTTP evidence for the local governed W09 research API."""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_w09_research_index_build import (
    _COMPETITION,
    _CUTOFF,
    _feature_fixture,
)

from scouting.api.research import ResearchApiRuntime, create_research_router
from scouting.contracts.research import (
    FeatureWeight,
    NamedFeatureValue,
    ResearchCapability,
    ResearchComparisonRequest,
    ResearchDatasetDescriptor,
    ResearchFilters,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchQueryResult,
    ResearchReplayStatus,
    ResearchVersionPins,
    canonical_research_digest,
)
from scouting.modeling.research import (
    LoadedFeatureMatrix,
    LoadedResearchIndex,
    ResearchIndexBuildMode,
    build_research_index,
    load_feature_matrix,
    load_research_index,
)
from scouting.serving.research import ResearchServingService
from scouting.storage.embedded import create_embedded_engine
from scouting.storage.guarded import GuardedStorage
from scouting.storage.research import RESEARCH_REPORT_ROOT_NAME, ResearchExperimentStore

_REQUESTED = datetime(2026, 8, 5, 15, 0, tzinfo=UTC)
_NOW = datetime(2026, 8, 5, 16, 0, tzinfo=UTC)
_ATTRIBUTION = "Wyscout public dataset on figshare, licensed CC BY 4.0."
_RIGHTS_LIMITATIONS = (
    "Retained historical 2017/18 evidence only; no current provider coverage.",
    "Attribution must accompany every saved report and external export is not authorised.",
)


def _pins(matrix: LoadedFeatureMatrix, index: LoadedResearchIndex) -> ResearchVersionPins:
    matrix_manifest = matrix.manifest
    index_manifest = index.manifest
    return ResearchVersionPins(
        feature_cutoff_ts=matrix_manifest.feature_cutoff_ts,
        dataset_version=matrix_manifest.dataset_version,
        dataset_manifest_digest=matrix_manifest.dataset_manifest_digest,
        identity_bundle_digest=matrix_manifest.identity_bundle_digest,
        canonical_build_digest=matrix_manifest.canonical_build_digest,
        matrix_version=matrix_manifest.matrix_version,
        matrix_manifest_digest=matrix_manifest.manifest_digest,
        matrix_digest=matrix_manifest.matrix_digest,
        feature_registry_version=matrix_manifest.feature_registry_version,
        feature_registry_digest=matrix_manifest.feature_registry_digest,
        eligibility_policy_version=matrix_manifest.eligibility_policy_version,
        eligibility_policy_digest=matrix_manifest.eligibility_policy_digest,
        model_version=index_manifest.model_version,
        model_configuration_digest=index_manifest.model_configuration_digest,
        scorer_version=index_manifest.scorer_version,
        scorer_code_digest=index_manifest.scorer_code_digest,
        index_version=index_manifest.index_version,
        index_manifest_digest=index_manifest.manifest_digest,
        catalogue_digest=index_manifest.catalogue_digest,
    )


def _authority(root: Path) -> tuple[ResearchServingService, LoadedFeatureMatrix]:
    matrix_root = root / "matrix"
    manifest_path, manifest = _feature_fixture(matrix_root, cross_competition=True)
    index_root = root / "index"
    build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=matrix_root,
        output_root=index_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    matrix = load_feature_matrix(
        manifest_path,
        artifact_root=matrix_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    index = load_research_index(
        index_root,
        matrix_manifest=manifest,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    return ResearchServingService(matrix=matrix, index=index, pins=_pins(matrix, index)), matrix


def _dataset(service: ResearchServingService) -> ResearchDatasetDescriptor:
    manifest = service.matrix_manifest
    return ResearchDatasetDescriptor(
        dataset_id=UUID("10000000-0000-4000-8000-000000000001"),
        dataset_version=manifest.dataset_version,
        dataset_manifest_digest=manifest.dataset_manifest_digest,
        provider_adapter="wyscout_historical_v1",
        provider_neutral_schema_version="w09-canonical-v1",
        rights_classification="wyscout_figshare_v5_cc_by_4",
        attribution=_ATTRIBUTION,
        source_manifest_id=manifest.source_manifest_id,
        source_manifest_digest=manifest.source_manifest_digest,
        source_completion_digest=manifest.source_completion_digest,
        identity_bundle_digest=manifest.identity_bundle_digest,
        source_available_at=datetime(2018, 7, 2, tzinfo=UTC),
        identity_available_at=datetime(2018, 7, 3, tzinfo=UTC),
        feature_cutoff_ts=manifest.feature_cutoff_ts,
        window_start_utc=manifest.window_start_utc,
        window_end_utc=manifest.window_end_utc,
        source_match_count=1_826,
        source_action_count=3_071_395,
        source_team_count=142,
        source_player_count=3_603,
        capabilities=tuple(ResearchCapability),
        limitations=(
            "Fixture matrix represents retained historical evidence only.",
            "G-RW4 expert relevance validation is absent.",
        ),
    )


def _query(service: ResearchServingService) -> ResearchQueryRequest:
    weights = (
        FeatureWeight(feature_name="passes_per_90", weight=1.0),
        FeatureWeight(feature_name="shots_per_90", weight=1.0),
    )
    profile = (
        NamedFeatureValue(feature_name="passes_per_90", value=1.0),
        NamedFeatureValue(feature_name="shots_per_90", value=5.0),
    )
    draft = ResearchQueryRequest.model_construct(
        query_id=UUID("70000000-0000-4000-8000-000000000001"),
        requested_at=_REQUESTED,
        feature_cutoff_ts=_CUTOFF,
        pins=service.pins,
        mode=ResearchQueryMode.WEIGHTED_PROFILE,
        method=ResearchMethod.WEIGHTED_EUCLIDEAN,
        exemplar_grain_id=None,
        profile=profile,
        weights=weights,
        filters=ResearchFilters(competition_id=_COMPETITION, season_id="2017-18"),
        limit=20,
        query_digest="0" * 64,
    )
    return ResearchQueryRequest(
        query_id=draft.query_id,
        requested_at=draft.requested_at,
        feature_cutoff_ts=draft.feature_cutoff_ts,
        pins=draft.pins,
        mode=draft.mode,
        method=draft.method,
        exemplar_grain_id=draft.exemplar_grain_id,
        profile=draft.profile,
        weights=draft.weights,
        filters=draft.filters,
        limit=draft.limit,
        query_digest=canonical_research_digest(draft.digest_projection()),
    )


def _comparison(result: ResearchQueryResult) -> ResearchComparisonRequest:
    grain_ids = tuple(item.grain_id for item in result.candidates[:2])
    draft = ResearchComparisonRequest.model_construct(
        comparison_id=UUID("80000000-0000-4000-8000-000000000001"),
        result_id=result.result_id,
        result_digest=result.result_digest,
        query_digest=result.request.query_digest,
        pins=result.request.pins,
        grain_ids=grain_ids,
        comparison_request_digest="0" * 64,
    )
    return ResearchComparisonRequest(
        comparison_id=draft.comparison_id,
        result_id=draft.result_id,
        result_digest=draft.result_digest,
        query_digest=draft.query_digest,
        pins=draft.pins,
        grain_ids=draft.grain_ids,
        comparison_request_digest=canonical_research_digest(draft.digest_projection()),
    )


@pytest.fixture
def api(
    tmp_path: Path,
) -> Iterator[
    tuple[
        TestClient,
        ResearchApiRuntime,
        ResearchServingService,
        ResearchExperimentStore,
        ResearchQueryRequest,
    ]
]:
    service, _ = _authority(tmp_path)
    engine = create_embedded_engine(tmp_path / "research.sqlite3", allowed_root=tmp_path)
    store = ResearchExperimentStore(
        engine,
        GuardedStorage({RESEARCH_REPORT_ROOT_NAME: tmp_path / "reports"}),
    )
    runtime = ResearchApiRuntime(
        dataset=_dataset(service),
        serving=service,
        store=store,
        retained_attribution=_ATTRIBUTION,
        rights_limitations=_RIGHTS_LIMITATIONS,
        utc_clock=lambda: _NOW,
    )
    app = FastAPI()
    app.include_router(create_research_router(runtime))
    with TestClient(app) as client:
        yield client, runtime, service, store, _query(service)
    engine.dispose()


def _save_payload(
    result: ResearchQueryResult,
    comparison: dict[str, object] | None = None,
    *,
    report_format: str = "json",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "experiment_id": "90000000-0000-4000-8000-000000000001",
        "name": "Historical player research",
        "note": "Fixture-only API evidence",
        "result_id": str(result.result_id),
        "result_digest": result.result_digest,
        "report_format": report_format,
    }
    if comparison is not None:
        request = cast(dict[str, object], comparison["request"])
        payload["comparison_id"] = request["comparison_id"]
        payload["comparison_digest"] = comparison["comparison_digest"]
    return payload


def _served_result(client: TestClient, request: ResearchQueryRequest) -> ResearchQueryResult:
    response = client.post("/api/w09/queries", json=request.model_dump(mode="json"))
    assert response.status_code == 200
    return ResearchQueryResult.model_validate_json(response.content)


def test_complete_browser_api_journey_and_exact_report_bytes(
    api: tuple[
        TestClient,
        ResearchApiRuntime,
        ResearchServingService,
        ResearchExperimentStore,
        ResearchQueryRequest,
    ],
) -> None:
    client, _, _, store, request = api

    datasets = client.get("/api/w09/datasets")
    assert datasets.status_code == 200
    assert datasets.json()[0]["source_action_count"] == 3_071_395
    players = client.get("/api/w09/players", params={"limit": 2})
    assert players.status_code == 200
    assert len(players.json()["players"]) == 2
    assert players.json()["total_matches"] == 4
    assert players.json()["contains_synthetic_rows"] is False
    assert all(item["contains_synthetic_data"] is False for item in players.json()["players"])

    result = _served_result(client, request)
    loaded = client.get(f"/api/w09/results/{result.result_id}")
    assert loaded.status_code == 200
    assert loaded.json() == result.model_dump(mode="json")

    comparison_request = _comparison(result)
    comparison_response = client.post(
        "/api/w09/comparisons",
        json=comparison_request.model_dump(mode="json"),
    )
    assert comparison_response.status_code == 200
    comparison = cast(dict[str, object], comparison_response.json())
    save_payload = _save_payload(result, comparison)
    saved = client.post("/api/w09/experiments", json=save_payload)
    assert saved.status_code == 200
    experiment_id = saved.json()["experiment_id"]
    assert client.post("/api/w09/experiments", json=save_payload).json() == saved.json()
    assert client.get(f"/api/w09/experiments/{experiment_id}").json() == saved.json()
    listed = client.get("/api/w09/experiments")
    assert listed.status_code == 200
    assert listed.json() == [
        {
            "schema_version": 1,
            "experiment_id": experiment_id,
            "name": saved.json()["name"],
            "note": saved.json()["note"],
            "created_at": saved.json()["created_at"],
            "query_id": saved.json()["request"]["query_id"],
            "result_id": saved.json()["result"]["result_id"],
            "dataset_version": saved.json()["request"]["pins"]["dataset_version"],
            "dataset_manifest_digest": saved.json()["request"]["pins"]["dataset_manifest_digest"],
            "matrix_version": saved.json()["request"]["pins"]["matrix_version"],
            "matrix_digest": saved.json()["request"]["pins"]["matrix_digest"],
            "index_version": saved.json()["request"]["pins"]["index_version"],
            "index_manifest_digest": saved.json()["request"]["pins"]["index_manifest_digest"],
            "report_format": saved.json()["report"]["report_format"],
            "report_relative_path": saved.json()["report"]["report_relative_path"],
            "report_digest": saved.json()["report"]["report_digest"],
            "experiment_digest": saved.json()["experiment_digest"],
        }
    ]

    report = client.get(f"/api/w09/experiments/{experiment_id}/report")
    assert report.status_code == 200
    assert report.headers["content-type"] == "application/json"
    assert report.content == store.load_report_bytes(UUID(experiment_id))
    replay = client.post(f"/api/w09/experiments/{experiment_id}/replay")
    assert replay.status_code == 200
    assert replay.json()["status"] == ResearchReplayStatus.REPRODUCED
    assert client.post(f"/api/w09/experiments/{experiment_id}/replay").json() == replay.json()


def test_bounded_search_strict_validation_stale_pins_and_unknown_ids(
    api: tuple[
        TestClient,
        ResearchApiRuntime,
        ResearchServingService,
        ResearchExperimentStore,
        ResearchQueryRequest,
    ],
) -> None:
    client, _, _, _, request = api
    filtered = client.get(
        "/api/w09/players",
        params={
            "name": "fixture player 2",
            "position": "DF",
            "competition_id": str(_COMPETITION),
            "limit": 1,
        },
    )
    assert filtered.status_code == 200
    assert [item["display_name"] for item in filtered.json()["players"]] == [
        "Historical Fixture Player 2"
    ]
    assert client.get("/api/w09/players", params={"limit": 101}).status_code == 422
    assert client.get("/api/w09/players", params={"name": "   "}).status_code == 422

    malformed = request.model_dump(mode="json")
    malformed["fictional_role"] = "recruiter"
    assert client.post("/api/w09/queries", json=malformed).status_code == 422
    stale_pins = request.pins.model_copy(update={"index_version": "stale-index-v0"})
    stale_draft = request.model_copy(update={"pins": stale_pins, "query_digest": "0" * 64})
    stale = ResearchQueryRequest.model_validate(
        stale_draft.model_dump(mode="python")
        | {"query_digest": canonical_research_digest(stale_draft.digest_projection())}
    )
    assert client.post("/api/w09/queries", json=stale.model_dump(mode="json")).status_code == 409
    unknown = "aaaaaaaa-0000-4000-8000-000000000001"
    assert client.get(f"/api/w09/results/{unknown}").status_code == 404
    assert client.get(f"/api/w09/experiments/{unknown}").status_code == 404
    assert client.get(f"/api/w09/experiments/{unknown}/report").status_code == 404
    assert client.post(f"/api/w09/experiments/{unknown}/replay").status_code == 404


def test_html_media_type_and_concurrent_result_cache_are_exact(
    api: tuple[
        TestClient,
        ResearchApiRuntime,
        ResearchServingService,
        ResearchExperimentStore,
        ResearchQueryRequest,
    ],
) -> None:
    client, runtime, _, store, request = api
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = tuple(executor.map(lambda _: runtime.execute_query(request), range(24)))
    assert len(set(results)) == 1
    result = results[0]
    payload = _save_payload(result, report_format="html")
    saved = client.post("/api/w09/experiments", json=payload)
    assert saved.status_code == 200
    experiment_id = UUID(saved.json()["experiment_id"])
    report = client.get(f"/api/w09/experiments/{experiment_id}/report")
    assert report.status_code == 200
    assert report.headers["content-type"] == "text/html; charset=utf-8"
    assert report.content == store.load_report_bytes(experiment_id)


def test_result_authority_cache_is_bounded_lru(
    api: tuple[
        TestClient,
        ResearchApiRuntime,
        ResearchServingService,
        ResearchExperimentStore,
        ResearchQueryRequest,
    ],
) -> None:
    client, runtime, _, _, request = api
    result_ids: list[UUID] = []
    for index in range(129):
        draft = request.model_copy(
            update={
                "query_id": UUID(int=index + 1),
                "query_digest": "0" * 64,
            }
        )
        varied = ResearchQueryRequest.model_validate(
            draft.model_dump(mode="python")
            | {"query_digest": canonical_research_digest(draft.digest_projection())}
        )
        result_ids.append(runtime.execute_query(varied).result_id)

    assert len(runtime._results) == 128
    assert client.get(f"/api/w09/results/{result_ids[0]}").status_code == 404
    assert client.get(f"/api/w09/results/{result_ids[-1]}").status_code == 200


def test_replay_records_incompatible_pins_without_rewriting_saved_query(
    api: tuple[
        TestClient,
        ResearchApiRuntime,
        ResearchServingService,
        ResearchExperimentStore,
        ResearchQueryRequest,
    ],
) -> None:
    client, _, service, _, request = api
    result = _served_result(client, request)
    saved = client.post("/api/w09/experiments", json=_save_payload(result))
    assert saved.status_code == 200
    experiment_id = saved.json()["experiment_id"]
    stale = service.pins.model_copy(update={"index_version": "replacement-index-v2"})
    object.__setattr__(service, "_pins", stale)

    replay = client.post(f"/api/w09/experiments/{experiment_id}/replay")
    assert replay.status_code == 200
    assert replay.json()["status"] == ResearchReplayStatus.INCOMPATIBLE_PINS
    assert replay.json()["saved_pins"] == saved.json()["request"]["pins"]
    assert replay.json()["loaded_pins"]["index_version"] == "replacement-index-v2"


def test_replay_records_deterministic_result_mismatch(
    api: tuple[
        TestClient,
        ResearchApiRuntime,
        ResearchServingService,
        ResearchExperimentStore,
        ResearchQueryRequest,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, _, _, request = api
    result = _served_result(client, request)
    saved = client.post("/api/w09/experiments", json=_save_payload(result))
    assert saved.status_code == 200
    experiment_id = saved.json()["experiment_id"]
    original = ResearchServingService.execute_query

    def mismatched(
        self: ResearchServingService,
        request_value: ResearchQueryRequest,
        *,
        generated_at: datetime,
    ) -> ResearchQueryResult:
        reproduced = original(self, request_value, generated_at=generated_at)
        warnings = (*reproduced.warnings, "Deterministic mismatch test evidence.")
        draft = reproduced.model_copy(update={"warnings": warnings, "result_digest": "0" * 64})
        return ResearchQueryResult(
            result_id=draft.result_id,
            request=draft.request,
            generated_at=draft.generated_at,
            population=draft.population,
            candidates=draft.candidates,
            warnings=draft.warnings,
            result_digest=canonical_research_digest(draft.digest_projection()),
        )

    monkeypatch.setattr(ResearchServingService, "execute_query", mismatched)
    replay = client.post(f"/api/w09/experiments/{experiment_id}/replay")
    assert replay.status_code == 200
    assert replay.json()["status"] == ResearchReplayStatus.RESULT_MISMATCH
    assert replay.json()["original_result_digest"] != replay.json()["replay_result_digest"]

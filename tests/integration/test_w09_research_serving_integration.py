"""End-to-end research serving tests over built and loaded artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import pytest
from test_w09_research_index_build import (
    _COMPETITION,
    _CUTOFF,
    _PLAYERS,
    _SECOND_COMPETITION,
    _feature_fixture,
    _self_digest_manifest,
    _write_private,
)

import scouting.serving.research as research_serving
from scouting.contracts.research import (
    EligibilityDecision,
    FeatureMatrixManifest,
    FeatureMatrixRow,
    FeatureValueState,
    FeatureWeight,
    MinuteEvidenceState,
    NamedFeatureValue,
    ResearchComparisonRequest,
    ResearchFeatureValue,
    ResearchFilters,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchVersionPins,
    canonical_research_digest,
)
from scouting.modeling.research import (
    ELIGIBILITY_DECISIONS_ROLE,
    FEATURE_MATRIX_ROWS_ROLE,
    LoadedFeatureMatrix,
    LoadedResearchIndex,
    ResearchIndexBuildMode,
    build_research_index,
    load_feature_matrix,
    load_research_index,
    rows_semantic_digest,
)
from scouting.serving.research import ResearchServingError, ResearchServingService
from scouting.storage.formats import canonical_jsonl_bytes

_REQUESTED = datetime(2026, 8, 5, 15, 0, tzinfo=UTC)
_GENERATED = _REQUESTED + timedelta(seconds=1)


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


def _authority(
    root: Path,
    *,
    cross_competition: bool = True,
    cross_season: bool = False,
) -> tuple[ResearchServingService, LoadedFeatureMatrix, LoadedResearchIndex]:
    matrix_root = root / "matrix"
    manifest_path, manifest = _feature_fixture(
        matrix_root,
        cross_competition=cross_competition,
        cross_season=cross_season,
    )
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
    return (
        ResearchServingService(matrix=matrix, index=index, pins=_pins(matrix, index)),
        matrix,
        index,
    )


def _make_first_row_lower_bound(
    matrix_root: Path,
    manifest_path: Path,
) -> FeatureMatrixManifest:
    payload = cast(dict[str, Any], json.loads(manifest_path.read_bytes()))
    descriptors = {item["role"]: item for item in payload["files"]}

    eligibility_path = matrix_root / descriptors[ELIGIBILITY_DECISIONS_ROLE]["relative_path"]
    eligibility_payloads = [json.loads(line) for line in eligibility_path.read_bytes().splitlines()]
    eligibility_payloads[0]["minute_state"] = MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND
    eligibility = tuple(
        EligibilityDecision.model_validate_json(json.dumps(item)) for item in eligibility_payloads
    )
    encoded_eligibility = canonical_jsonl_bytes(
        [item.model_dump(mode="json") for item in eligibility]
    )
    _write_private(eligibility_path, encoded_eligibility)
    eligibility_descriptor = descriptors[ELIGIBILITY_DECISIONS_ROLE]
    eligibility_descriptor.update(
        {
            "size_bytes": len(encoded_eligibility),
            "sha256": hashlib.sha256(encoded_eligibility).hexdigest(),
            "semantic_digest": rows_semantic_digest(eligibility),
        }
    )
    payload["eligibility_ledger_digest"] = eligibility_descriptor["semantic_digest"]

    rows_path = matrix_root / descriptors[FEATURE_MATRIX_ROWS_ROLE]["relative_path"]
    row_payloads = [json.loads(line) for line in rows_path.read_bytes().splitlines()]
    row_payloads[0]["minute_state"] = MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND
    row_payloads[0]["eligibility_decision_digest"] = canonical_research_digest(eligibility[0])
    rows = tuple(FeatureMatrixRow.model_validate_json(json.dumps(item)) for item in row_payloads)
    encoded_rows = canonical_jsonl_bytes([item.model_dump(mode="json") for item in rows])
    _write_private(rows_path, encoded_rows)
    rows_descriptor = descriptors[FEATURE_MATRIX_ROWS_ROLE]
    rows_descriptor.update(
        {
            "size_bytes": len(encoded_rows),
            "sha256": hashlib.sha256(encoded_rows).hexdigest(),
            "semantic_digest": rows_semantic_digest(rows),
        }
    )
    payload["matrix_digest"] = rows_descriptor["semantic_digest"]
    encoded_manifest = _self_digest_manifest(payload)
    _write_private(manifest_path, encoded_manifest)
    return FeatureMatrixManifest.model_validate_json(encoded_manifest)


def _query(
    service: ResearchServingService,
    *,
    mode: ResearchQueryMode = ResearchQueryMode.WEIGHTED_PROFILE,
    method: ResearchMethod = ResearchMethod.WEIGHTED_EUCLIDEAN,
    competition_id: UUID = _COMPETITION,
    feature_names: tuple[str, ...] = ("passes_per_90", "shots_per_90"),
    profile_values: tuple[float, ...] = (1.0, 5.0),
    exemplar_grain_id: str | None = None,
    position_codes: tuple[str, ...] = (),
    minimum_minutes: float | None = None,
    excluded_player_ids: tuple[UUID, ...] = (),
    season_id: str | None = "2017-18",
    limit: int = 20,
) -> ResearchQueryRequest:
    weights = tuple(FeatureWeight(feature_name=name, weight=1.0) for name in feature_names)
    profile = (
        tuple(
            NamedFeatureValue(feature_name=name, value=value)
            for name, value in zip(feature_names, profile_values, strict=True)
        )
        if mode is ResearchQueryMode.WEIGHTED_PROFILE
        else ()
    )
    draft = ResearchQueryRequest.model_construct(
        query_id=UUID("70000000-0000-4000-8000-000000000001"),
        requested_at=_REQUESTED,
        feature_cutoff_ts=_CUTOFF,
        pins=service.pins,
        mode=mode,
        method=method,
        exemplar_grain_id=exemplar_grain_id,
        profile=profile,
        weights=weights,
        filters=ResearchFilters(
            competition_id=competition_id,
            season_id=season_id,
            position_codes=cast(tuple[object, ...], position_codes),
            minimum_minutes=minimum_minutes,
            excluded_player_ids=excluded_player_ids,
        ),
        limit=limit,
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


def _comparison_request(
    service: ResearchServingService,
    result: object,
    grain_ids: tuple[str, ...],
) -> ResearchComparisonRequest:
    from scouting.contracts.research import ResearchQueryResult

    served = cast(ResearchQueryResult, result)
    draft = ResearchComparisonRequest.model_construct(
        comparison_id=UUID("80000000-0000-4000-8000-000000000001"),
        result_id=served.result_id,
        result_digest=served.result_digest,
        query_digest=served.request.query_digest,
        pins=service.pins,
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


@pytest.mark.parametrize(
    "method",
    (ResearchMethod.WEIGHTED_EUCLIDEAN, ResearchMethod.WEIGHTED_COSINE),
)
def test_full_population_query_is_deterministic_explained_and_version_pinned(
    tmp_path: Path,
    method: ResearchMethod,
) -> None:
    service, _, _ = _authority(tmp_path)
    request = _query(service, method=method)

    first = service.execute_query(request, generated_at=_GENERATED)
    later = service.execute_query(request, generated_at=_GENERATED + timedelta(minutes=1))

    assert first.result_id == later.result_id
    assert first.result_digest == later.result_digest
    assert first.candidates == later.candidates
    assert first.population.matrix_rows == 4
    assert first.population.competition_rows == 3
    assert first.population.scored_rows == 3
    assert first.population.returned_rows == 3
    assert [candidate.rank for candidate in first.candidates] == [1, 2, 3]
    assert all(candidate.competition_id == _COMPETITION for candidate in first.candidates)
    assert all(
        tuple(item.feature_name for item in candidate.contributions)
        == ("passes_per_90", "shots_per_90")
        for candidate in first.candidates
    )
    assert any("G-RW4" in warning for warning in first.warnings)
    assert not any("absent active value" in warning for warning in first.warnings)
    assert all(candidate.missing_features == () for candidate in first.candidates)
    assert not any(
        "absent active value" in limitation
        for candidate in first.candidates
        for limitation in candidate.limitations
    )


def test_exemplar_active_subset_filters_and_full_score_before_limit(tmp_path: Path) -> None:
    service, _, _ = _authority(tmp_path)
    exemplar = _query(
        service,
        mode=ResearchQueryMode.EXEMPLAR,
        feature_names=("shots_per_90",),
        profile_values=(),
        exemplar_grain_id="competition-season-player-1",
        limit=1,
    )

    result = service.execute_query(exemplar, generated_at=_GENERATED)

    assert result.population.exemplar_self_exclusions == 1
    assert result.population.scored_rows == 2
    assert result.population.returned_rows == 1
    assert result.candidates[0].player_id == _PLAYERS[1]
    assert result.candidates[0].score == 0.0
    assert tuple(item.feature_name for item in result.candidates[0].contributions) == (
        "shots_per_90",
    )

    filtered = _query(
        service,
        position_codes=("GK", "DF"),
        minimum_minutes=902.0,
        excluded_player_ids=(_PLAYERS[1],),
    )
    filtered_result = service.execute_query(filtered, generated_at=_GENERATED)
    assert filtered_result.population.position_exclusions == 1
    assert filtered_result.population.minimum_minutes_exclusions == 1
    assert filtered_result.population.explicit_player_exclusions == 1
    assert filtered_result.population.scored_rows == 0


def test_same_player_cross_competition_is_valid_but_mandatory_filter_is_first(
    tmp_path: Path,
) -> None:
    service, _, _ = _authority(tmp_path)

    result = service.execute_query(
        _query(
            service,
            competition_id=_SECOND_COMPETITION,
            profile_values=(4.0, 5.0),
        ),
        generated_at=_GENERATED,
    )

    assert result.population.matrix_rows == 4
    assert result.population.competition_rows == 1
    assert result.population.scored_rows == 1
    assert [(item.player_id, item.competition_id) for item in result.candidates] == [
        (_PLAYERS[0], _SECOND_COMPETITION)
    ]


def test_explicit_season_filter_separates_same_player_competition_grains(
    tmp_path: Path,
) -> None:
    service, _, _ = _authority(
        tmp_path,
        cross_competition=False,
        cross_season=True,
    )

    retained = service.execute_query(
        _query(service, season_id="2017-18"),
        generated_at=_GENERATED,
    )
    next_season = service.execute_query(
        _query(service, season_id="2018-19", profile_values=(4.0, 5.0)),
        generated_at=_GENERATED,
    )

    assert retained.population.matrix_rows == 4
    assert retained.population.competition_rows == retained.population.scored_rows == 3
    assert next_season.population.competition_rows == next_season.population.scored_rows == 1
    assert next_season.candidates[0].player_id == _PLAYERS[0]
    with pytest.raises(ResearchServingError, match="explicit season_id"):
        service.execute_query(
            _query(service, season_id=None),
            generated_at=_GENERATED,
        )


def test_service_privately_copies_arrays_and_exposes_only_frozen_validated_rows(
    tmp_path: Path,
) -> None:
    service, matrix, index = _authority(tmp_path)
    request = _query(service)
    before = service.execute_query(request, generated_at=_GENERATED)
    pins = service.pins

    assert service.matrix_rows == matrix.rows
    assert service.matrix_rows is not matrix.rows
    assert all(served is not loaded for served, loaded in zip(service.matrix_rows, matrix.rows))
    with pytest.raises(TypeError):
        service.matrix_rows[0] = service.matrix_rows[1]  # type: ignore[index]
    with pytest.raises(ValueError, match="frozen"):
        service.matrix_rows[0].display_name = "Tampered"  # type: ignore[misc]

    for array in (index.center, index.scale, index.vectors):
        array.setflags(write=True)
        array.flat[0] += 1000.0
    for private in (service._index.center, service._index.scale, service._index.vectors):
        with pytest.raises(ValueError, match="WRITEABLE"):
            private.setflags(write=True)

    after = service.execute_query(request, generated_at=_GENERATED)
    assert after == before
    assert service.pins == pins


def test_cosine_zero_norm_query_fails_closed_instead_of_ranking_by_uuid(tmp_path: Path) -> None:
    service, _, index = _authority(tmp_path)
    center = tuple(float(value) for value in index.center)
    request = _query(
        service,
        method=ResearchMethod.WEIGHTED_COSINE,
        profile_values=center,
    )

    with pytest.raises(ResearchServingError, match="shared scorer rejected") as rejected:
        service.execute_query(request, generated_at=_GENERATED)

    assert rejected.value.__cause__ is not None
    assert "zero weighted norm" in str(rejected.value.__cause__)


def test_cosine_query_explanation_is_normalized_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, _, _ = _authority(tmp_path)
    request = _query(service, method=ResearchMethod.WEIGHTED_COSINE)
    original = research_serving.stable_weighted_unit_components
    calls = 0

    def counted(
        values: tuple[float, ...],
        weights: tuple[float, ...],
    ) -> tuple[tuple[float, ...], bool]:
        nonlocal calls
        calls += 1
        return original(values, weights)

    monkeypatch.setattr(research_serving, "stable_weighted_unit_components", counted)
    result = service.execute_query(request, generated_at=_GENERATED)

    assert calls == len(result.candidates) + 1


def test_lower_bound_minutes_are_visible_in_result_and_candidate_warnings(
    tmp_path: Path,
) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, _ = _feature_fixture(matrix_root)
    manifest = _make_first_row_lower_bound(matrix_root, manifest_path)
    index_root = tmp_path / "index"
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
    service = ResearchServingService(matrix=matrix, index=index, pins=_pins(matrix, index))

    result = service.execute_query(_query(service), generated_at=_GENERATED)

    candidate = next(item for item in result.candidates if item.player_id == _PLAYERS[0])
    assert any("lower-bound minutes" in warning for warning in result.warnings)
    assert any("conservative lower bound" in limitation for limitation in candidate.limitations)


def test_comparison_returns_exact_candidate_rows_in_requested_order(tmp_path: Path) -> None:
    service, matrix, _ = _authority(tmp_path)
    result = service.execute_query(_query(service, limit=3), generated_at=_GENERATED)
    grain_ids = (result.candidates[1].grain_id, result.candidates[0].grain_id)
    request = _comparison_request(service, result, grain_ids)

    comparison = service.compare(request, result)

    expected = {row.grain_id: row for row in matrix.rows}
    assert comparison.rows == tuple(expected[grain_id] for grain_id in grain_ids)
    assert comparison.comparison_digest == canonical_research_digest(
        comparison.model_dump(mode="json", exclude={"comparison_digest"})
    )


def test_comparison_uses_the_exact_cached_result_without_rescoring(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, _, _ = _authority(tmp_path)
    result = service.execute_query(_query(service, limit=3), generated_at=_GENERATED)
    grain_ids = tuple(item.grain_id for item in result.candidates[:2])
    request = _comparison_request(service, result, grain_ids)

    def reject_rescore(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise AssertionError("comparison attempted to rescore the population")

    monkeypatch.setattr(ResearchServingService, "execute_query", reject_rescore)
    comparison = service.compare(request, result)

    assert comparison.request.result_digest == result.result_digest
    assert tuple(row.grain_id for row in comparison.rows) == grain_ids


def test_serving_fails_closed_on_stale_requests_unknown_features_and_tampering(
    tmp_path: Path,
) -> None:
    service, matrix, index = _authority(tmp_path)

    stale_pins = service.pins.model_copy(update={"matrix_digest": "f" * 64})
    stale_draft = _query(service).model_copy(update={"pins": stale_pins})
    stale = stale_draft.model_copy(
        update={"query_digest": canonical_research_digest(stale_draft.digest_projection())}
    )
    with pytest.raises(ResearchServingError, match="stale or incompatible"):
        service.execute_query(stale, generated_at=_GENERATED)

    unknown = _query(service, feature_names=("unknown_feature",), profile_values=(1.0,))
    with pytest.raises(ResearchServingError, match="unknown active feature"):
        service.execute_query(unknown, generated_at=_GENERATED)

    unordered = _query(
        service,
        feature_names=("shots_per_90", "passes_per_90"),
        profile_values=(5.0, 1.0),
    )
    with pytest.raises(ResearchServingError, match="ordered subset"):
        service.execute_query(unordered, generated_at=_GENERATED)

    vectors = index.vectors.copy()
    vectors[0, 0] += 1.0
    vectors.setflags(write=False)
    with pytest.raises(ResearchServingError, match="array drifts"):
        ResearchServingService(
            matrix=matrix,
            index=replace(index, vectors=vectors),
            pins=service.pins,
        )

    missing = ResearchFeatureValue(
        feature_name="passes_per_90",
        state=FeatureValueState.MISSING,
        value=None,
        reason="fixture absence",
    )
    first = matrix.rows[0].model_copy(
        update={
            "features": (missing, matrix.rows[0].features[1]),
            "missing_feature_names": ("passes_per_90",),
        }
    )
    with pytest.raises(ResearchServingError, match="in-memory evidence drifts"):
        ResearchServingService(
            matrix=replace(matrix, rows=(first, *matrix.rows[1:])),
            index=index,
            pins=service.pins,
        )

    duplicate_rows = (matrix.rows[0], matrix.rows[0], *matrix.rows[2:])
    with pytest.raises(ResearchServingError, match="in-memory evidence drifts"):
        ResearchServingService(
            matrix=replace(matrix, rows=duplicate_rows),
            index=index,
            pins=service.pins,
        )

    mismatched_catalogue = (
        index.catalogue[0].model_copy(update={"display_name": "Mismatched identity"}),
        *index.catalogue[1:],
    )
    with pytest.raises(ResearchServingError, match="catalogue count, order or digest drifts"):
        ResearchServingService(
            matrix=matrix,
            index=replace(index, catalogue=mismatched_catalogue),
            pins=service.pins,
        )


def test_comparison_rejects_non_candidate_and_mutated_result(tmp_path: Path) -> None:
    service, _, _ = _authority(tmp_path)
    result = service.execute_query(
        _query(service, excluded_player_ids=(_PLAYERS[2],), limit=2),
        generated_at=_GENERATED,
    )
    invalid_grains = (result.candidates[0].grain_id, "competition-season-player-3")
    with pytest.raises(ResearchServingError, match="non-candidate"):
        service.compare(_comparison_request(service, result, invalid_grains), result)

    mutated = result.model_copy(update={"warnings": (*result.warnings, "tampered")})
    valid_grains = tuple(item.grain_id for item in result.candidates)
    with pytest.raises(ResearchServingError, match="result contract rejected"):
        service.compare(_comparison_request(service, result, valid_grains), mutated)

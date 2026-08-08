from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, cast

import pytest
from test_w09_research_serving_integration import _GENERATED, _authority, _query

from scouting.contracts.research import (
    FeatureWeight,
    ResearchMethod,
    ResearchQueryRequest,
    canonical_research_digest,
)
from scouting.evaluation.research import (
    DEFAULT_EVALUATION_CONFIG_PATH,
    FrozenQueryCase,
    FrozenResearchEvaluationSuite,
    ResearchEvaluationError,
    _scaler,
    _verify_explanations,
    load_frozen_evaluation_suite,
    render_evaluation_payload,
    research_version_pins,
    run_research_evaluation,
)
from scouting.modeling.research import (
    DEFAULT_FEATURE_MANIFEST_ROOT,
    DEFAULT_INDEX_ROOT,
    DEFAULT_MATRIX_ARTIFACT_ROOT,
    LoadedFeatureMatrix,
    LoadedResearchIndex,
    ResearchIndexBuildMode,
    discover_feature_matrix_manifest,
    load_feature_matrix,
    load_research_index,
)
from scouting.serving.research import ResearchServingService
from scouting.storage.formats import canonical_json_bytes

_SCRIPT_PATH = Path(__file__).parents[2] / "scripts/evaluate_w09_retrieval.py"
_SPEC = importlib.util.spec_from_file_location("evaluate_w09_retrieval_integration", _SCRIPT_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("could not load evaluate_w09_retrieval.py")
_SCRIPT = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _SCRIPT
_SPEC.loader.exec_module(_SCRIPT)
evaluation_main = _SCRIPT.main

_EXPECTED_SUITE_DIGEST = "6a2630c3766d4762c12fc5ebf74e1fbfd43b4c2aa11b55847615c3c34e896a84"
_EXPECTED_RESULT_DIGEST = "5dd3cf9bd0cf20ae689c121fdf05471b930836c09b2a4bea4b8bb43729ae7e90"


@pytest.fixture(scope="module")
def retained_authority() -> tuple[
    ResearchServingService,
    LoadedFeatureMatrix,
    LoadedResearchIndex,
    FrozenResearchEvaluationSuite,
]:
    manifest_path = discover_feature_matrix_manifest(DEFAULT_FEATURE_MANIFEST_ROOT)
    matrix = load_feature_matrix(
        manifest_path,
        artifact_root=DEFAULT_MATRIX_ARTIFACT_ROOT,
        mode=ResearchIndexBuildMode.PRODUCTION,
    )
    index = load_research_index(
        DEFAULT_INDEX_ROOT,
        matrix_manifest=matrix.manifest,
        mode=ResearchIndexBuildMode.PRODUCTION,
    )
    service = ResearchServingService(
        matrix=matrix,
        index=index,
        pins=research_version_pins(matrix.manifest, index.manifest),
    )
    suite = load_frozen_evaluation_suite(DEFAULT_EVALUATION_CONFIG_PATH, service=service)
    return service, matrix, index, suite


def _write_rehashed_suite(
    source: Path,
    destination: Path,
    mutate: Any,
) -> None:
    payload = cast(dict[str, Any], json.loads(source.read_bytes()))
    mutate(payload)
    payload["suite_digest"] = canonical_research_digest(
        {key: value for key, value in payload.items() if key != "suite_digest"}
    )
    destination.write_bytes(canonical_json_bytes(payload))


def _case_for_query(query: ResearchQueryRequest, source_grain_id: str) -> FrozenQueryCase:
    draft = FrozenQueryCase.model_construct(
        case_id="synthetic-explanation-fixture",
        query_id=query.query_id,
        mode=query.mode,
        method=query.method,
        source_grain_id=source_grain_id,
        weights=query.weights,
        filters=query.filters,
        limit=query.limit,
        witnesses=(),
        case_digest="0" * 64,
    )
    return FrozenQueryCase(
        case_id=draft.case_id,
        query_id=draft.query_id,
        mode=draft.mode,
        method=draft.method,
        source_grain_id=draft.source_grain_id,
        weights=draft.weights,
        filters=draft.filters,
        limit=draft.limit,
        witnesses=draft.witnesses,
        case_digest=canonical_research_digest(draft.digest_projection()),
    )


def test_frozen_suite_uses_exact_real_authority_and_required_mode_coverage(
    retained_authority: tuple[
        ResearchServingService,
        LoadedFeatureMatrix,
        LoadedResearchIndex,
        FrozenResearchEvaluationSuite,
    ],
) -> None:
    service, matrix, index, suite = retained_authority
    rows = {row.grain_id: row for row in matrix.rows}
    source_rows = tuple(rows[case.source_grain_id] for case in suite.cases)

    assert suite.pins == service.pins
    assert suite.suite_digest == _EXPECTED_SUITE_DIGEST
    assert suite.feature_names == matrix.manifest.feature_names == index.manifest.feature_names
    assert suite.matrix_row_count == len(matrix.rows) == index.manifest.candidate_count == 1975
    assert suite.unique_matrix_player_count == 1965
    assert suite.source_player_count == 3603
    assert {row.position_code for row in source_rows} == {"GK", "DF", "MD", "FW"}
    assert len({row.competition_id for row in source_rows}) == 5
    assert {case.mode for case in suite.cases} == set(type(suite.cases[0].mode))
    assert {case.method for case in suite.cases} == set(ResearchMethod)
    assert not suite.contains_synthetic_rows
    assert not any(row.contains_synthetic_data for row in source_rows)
    assert all(row.minute_state.value == "conservative_lower_bound" for row in matrix.rows)


def test_retained_evaluation_is_exactly_reproducible_and_claim_bounded(
    retained_authority: tuple[
        ResearchServingService,
        LoadedFeatureMatrix,
        LoadedResearchIndex,
        FrozenResearchEvaluationSuite,
    ],
) -> None:
    service, _, _, suite = retained_authority

    first = run_research_evaluation(suite, service=service)
    second = run_research_evaluation(suite, service=service)

    assert first == second
    assert first.result_digest == _EXPECTED_RESULT_DIGEST
    assert render_evaluation_payload(first) == render_evaluation_payload(second)
    assert len(first.query_witnesses) == len(suite.cases) == 9
    assert len(first.explanation_witnesses) == 9
    assert len(first.filter_witnesses) == sum(len(case.witnesses) for case in suite.cases)
    assert len(first.stability_witnesses) == len(suite.perturbations) == 2
    assert first.coverage.matrix_row_count == 1975
    assert first.coverage.unique_matrix_player_count == 1965
    assert first.coverage.source_player_count == 3603
    assert len(first.coverage.competition_coverage) == 5
    assert all(item.sensitivity_only for item in first.stability_witnesses)
    assert not any(item.validates_ranking_quality for item in first.stability_witnesses)
    assert all(item.missing_feature_count == 0 for item in first.explanation_witnesses)
    assert all(item.passed for item in first.filter_witnesses)
    assert any(
        "not football relevance or recruitment usefulness" in item for item in first.limitations
    )
    assert any("G-RW4" in item for item in first.weaknesses)
    assert any("do not validate rankings" in item for item in first.weaknesses)


def test_suite_loader_rejects_stale_pins_and_absent_real_grains(
    tmp_path: Path,
    retained_authority: tuple[
        ResearchServingService,
        LoadedFeatureMatrix,
        LoadedResearchIndex,
        FrozenResearchEvaluationSuite,
    ],
) -> None:
    service, _, _, _ = retained_authority
    stale_path = tmp_path / "stale.json"

    def stale(payload: dict[str, Any]) -> None:
        cast(dict[str, Any], payload["pins"])["matrix_digest"] = "f" * 64

    _write_rehashed_suite(DEFAULT_EVALUATION_CONFIG_PATH, stale_path, stale)
    with pytest.raises(ResearchEvaluationError, match="pins are stale or incompatible"):
        load_frozen_evaluation_suite(stale_path, service=service)

    absent_path = tmp_path / "absent.json"

    def absent(payload: dict[str, Any]) -> None:
        case = cast(dict[str, Any], cast(list[Any], payload["cases"])[0])
        case["source_grain_id"] = "absent-retained-grain"
        case["case_digest"] = canonical_research_digest(
            {key: value for key, value in case.items() if key != "case_digest"}
        )

    _write_rehashed_suite(DEFAULT_EVALUATION_CONFIG_PATH, absent_path, absent)
    with pytest.raises(ResearchEvaluationError, match="absent or synthetic grain"):
        load_frozen_evaluation_suite(absent_path, service=service)


def test_explanation_verifier_covers_zero_weight_ties_missingness_and_matrix_boundary(
    tmp_path: Path,
) -> None:
    service, matrix, _ = _authority(tmp_path)
    base = _query(service, limit=3)
    weights = (
        FeatureWeight(feature_name="passes_per_90", weight=0.0),
        FeatureWeight(feature_name="shots_per_90", weight=1.0),
    )
    draft = base.model_copy(update={"weights": weights, "query_digest": "0" * 64})
    query = ResearchQueryRequest.model_validate(
        draft.model_copy(
            update={"query_digest": canonical_research_digest(draft.digest_projection())}
        )
    )
    result = service.execute_query(query, generated_at=_GENERATED)
    registry = service.index_manifest.feature_names
    center, scale = _scaler(service.matrix_rows, registry)
    case = _case_for_query(query, matrix.rows[0].grain_id)

    witness = _verify_explanations(
        case=case,
        query=query,
        result=result,
        rows=service.matrix_rows,
        registry=registry,
        center=center,
        scale=scale,
    )

    assert witness.candidate_rows_checked == 3
    assert witness.zero_weight_terms_checked == 3
    assert witness.deterministic_tie_pairs_checked == 2
    assert all(candidate.score == 0.0 for candidate in result.candidates)

    missing_candidate = result.candidates[0].model_copy(
        update={"missing_features": ("passes_per_90",)}
    )
    missing_result = result.model_copy(
        update={"candidates": (missing_candidate, *result.candidates[1:])}
    )
    with pytest.raises(ResearchEvaluationError, match="missing active features"):
        _verify_explanations(
            case=case,
            query=query,
            result=missing_result,
            rows=service.matrix_rows,
            registry=registry,
            center=center,
            scale=scale,
        )

    foreign_candidate = result.candidates[0].model_copy(update={"grain_id": "foreign-grain"})
    foreign_result = result.model_copy(
        update={"candidates": (foreign_candidate, *result.candidates[1:])}
    )
    with pytest.raises(ResearchEvaluationError, match="outside the governed matrix"):
        _verify_explanations(
            case=case,
            query=query,
            result=foreign_result,
            rows=service.matrix_rows,
            registry=registry,
            center=center,
            scale=scale,
        )

    contribution = result.candidates[0].contributions[0]
    inconsistent = contribution.model_copy(update={"query_value": contribution.query_value + 1.0})
    inconsistent_candidate = result.candidates[0].model_copy(
        update={"contributions": (inconsistent, *result.candidates[0].contributions[1:])}
    )
    inconsistent_result = result.model_copy(
        update={"candidates": (inconsistent_candidate, *result.candidates[1:])}
    )
    with pytest.raises(ResearchEvaluationError, match="operand is inconsistent"):
        _verify_explanations(
            case=case,
            query=query,
            result=inconsistent_result,
            rows=service.matrix_rows,
            registry=registry,
            center=center,
            scale=scale,
        )


def test_cli_writes_only_to_explicit_temporary_output_root(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "evaluation-output"

    assert evaluation_main(["--output-root", str(output_root)]) == 0
    stdout = cast(dict[str, Any], json.loads(capsys.readouterr().out))
    output = Path(cast(str, stdout["output"]))
    payload = output.read_bytes()

    assert output.parent == output_root
    assert output.name == f"{stdout['evaluation_result_digest']}.evaluation.json"
    assert canonical_json_bytes(json.loads(payload)) == payload
    assert stdout["state"] == "confirmed"

"""Deterministic W10 v2 descriptor derivation tests."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import duckdb
import pytest
from pydantic import ValidationError

from scouting.contracts.expert_relevance import (
    AssessmentBasisV2,
    CandidateEvidenceJudgementV2,
    EvidenceAvailabilityV2,
    EvidenceSufficiencyV2,
    JudgementState,
    MdEvidenceSubrubricV2,
    ParticipantEvidenceComparisonV2,
    ParticipantExpertEvidenceBundleV2,
    validate_response_comparison_v2,
)
from scouting.contracts.research import (
    FeatureMatrixManifest,
    FeatureMatrixRow,
    FeatureValueState,
    ResearchCoverage,
    ResearchFeatureValue,
    canonical_research_digest,
)
from scouting.data_products.wyscout import expert_evidence
from scouting.data_products.wyscout.expert_evidence import (
    ExpertEvidenceBuildError,
    _Aggregate,
    _bin_index,
    _midrank_percentile,
    _raw_families,
    _SpatialComponent,
    build_expert_evidence_bundles_v2,
    build_participant_evidence_comparison_v2,
    load_expert_evidence_policy_v2,
    participant_safe_comparison_bytes_v2,
    participant_safe_evidence_bytes_v2,
)
from scouting.modeling.research import LoadedFeatureMatrix
from scouting.storage.formats import canonical_json_bytes

_ROOT = Path(__file__).resolve().parents[2]
_H64 = "1" * 64


def _row(position: str = "GK", ordinal: int = 1) -> FeatureMatrixRow:
    policy = load_expert_evidence_policy_v2()
    minutes = 900.0
    features = tuple(
        ResearchFeatureValue(
            feature_name=name,
            state=FeatureValueState.VALUE,
            value=index * 90.0 / minutes,
            numerator=float(index),
            denominator=minutes,
        )
        for index, name in enumerate(policy.feature_names, start=1)
    )
    return FeatureMatrixRow.model_construct(
        grain_id=f"player=00000000-0000-0000-0000-{ordinal:012d}|competition=00000000-0000-0000-0000-000000000002|season=181150-{position}",
        player_id=UUID(f"00000000-0000-0000-0000-{ordinal:012d}"),
        display_name=f"Fixture Player {ordinal}",
        competition_id=UUID("00000000-0000-0000-0000-000000000002"),
        competition_name="Fixture competition",
        season_id=f"181150-{position}",
        position_code=position,
        team_ids=(UUID("00000000-0000-0000-0000-000000000003"),),
        team_names=("Fixture team",),
        minute_state="conservative_lower_bound",
        minutes=minutes,
        match_count=10,
        features=features,
        missing_feature_names=(),
        coverage=ResearchCoverage(
            lineup_matches_observed=10,
            lineup_matches_expected=10,
            action_matches_observed=10,
            action_matches_expected=10,
            coordinate_actions_observed=200,
            coordinate_actions_expected=200,
        ),
        window_start_utc=datetime(2017, 7, 1, tzinfo=UTC),
        window_end_utc=datetime(2018, 7, 1, tzinfo=UTC),
        feature_cutoff_ts=datetime(2026, 8, 5, tzinfo=UTC),
        dataset_manifest_digest=_H64,
        identity_bundle_digest=_H64,
        canonical_build_digest=("0105267ae0f107a63fad33b24adecdb3c4bb2e900bdf79a505e9ad4af6264b43"),
        feature_registry_digest=_H64,
        eligibility_policy_digest=_H64,
        eligibility_decision_digest=_H64,
        source_lineage_digest=_H64,
        source_action_count=200,
        contains_synthetic_data=False,
    )


def _aggregate() -> _Aggregate:
    return _Aggregate(
        total_actions=200,
        starts=_SpatialComponent(total=200, valid=200, bins=[25] * 8 + [0]),
        passes=50,
        pass_subtypes={81: 5, 83: 10, 84: 15, 85: 20},
        duels=20,
        duel_subtypes={10: 5, 11: 5, 12: 5, 13: 5},
        defending_duels=_SpatialComponent(total=5, valid=5, bins=[5] + [0] * 8),
        interceptions=_SpatialComponent(total=5, valid=5, bins=[0, 5] + [0] * 7),
        clearances=_SpatialComponent(total=3, valid=3, bins=[0, 0, 3] + [0] * 6),
        shots=_SpatialComponent(total=10, valid=10, bins=[1] * 8 + [2]),
        gk_goal_kicks=20,
        gk_leaving_line=3,
        gk_save_attempts=10,
        gk_reflexes=4,
        gk_generic_saves=6,
    )


def _matrix(*rows: FeatureMatrixRow) -> LoadedFeatureMatrix:
    policy = load_expert_evidence_policy_v2()
    manifest = FeatureMatrixManifest.model_construct(
        matrix_version=policy.matrix_version,
        matrix_digest=policy.matrix_digest,
        canonical_build_digest=rows[0].canonical_build_digest,
        feature_names=policy.feature_names,
    )
    return LoadedFeatureMatrix(
        manifest=manifest,
        rows=rows,
        catalogue=(),
        population_decisions=(),
        eligibility_decisions=(),
    )


def _fixture_bundles(
    monkeypatch: pytest.MonkeyPatch,
    *,
    position: str = "GK",
    branches: tuple[MdEvidenceSubrubricV2, MdEvidenceSubrubricV2] | None = None,
) -> tuple[ParticipantExpertEvidenceBundleV2, ParticipantExpertEvidenceBundleV2]:
    rows = (_row(position, 1), _row(position, 2))
    monkeypatch.setattr(
        expert_evidence,
        "aggregate_actions_v2",
        lambda _rows, _paths: {row.grain_id: _aggregate() for row in rows},
    )
    md_subrubrics = (
        {}
        if branches is None
        else {row.grain_id: branch for row, branch in zip(rows, branches, strict=True)}
    )
    bundles = build_expert_evidence_bundles_v2(
        _matrix(*rows),
        action_paths=(),
        selected_grain_ids=tuple(row.grain_id for row in rows),
        md_subrubrics=md_subrubrics,
    )
    return bundles[0], bundles[1]


def test_production_loader_rejects_same_id_substituted_canonical_manifest_before_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "substituted-root"
    action_path = root / "data/changed-actions.parquet"
    action_path.parent.mkdir(parents=True)
    action_bytes = b"internally self-consistent substituted artifact"
    action_path.write_bytes(action_bytes)
    manifest_path = root / "same-build-id.canonical-manifest.json"
    manifest_path.write_bytes(
        canonical_json_bytes(
            {
                "canonical_build_id": (
                    "2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e"
                ),
                "artifacts": [
                    {
                        "role": "canonical_actions",
                        "path": "data/changed-actions.parquet",
                        "sha256": hashlib.sha256(action_bytes).hexdigest(),
                        "size_bytes": len(action_bytes),
                    }
                ],
            }
        )
    )
    matrix = _matrix(_row())
    monkeypatch.setattr(expert_evidence, "PROJECT_ROOT", root)
    monkeypatch.setattr(expert_evidence, "CANONICAL_MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(expert_evidence, "load_feature_matrix", lambda *_args, **_kwargs: matrix)

    with pytest.raises(ExpertEvidenceBuildError, match="accepted pin"):
        expert_evidence.load_production_evidence_inputs_v2()


def _response(comparison_digest: str, **updates: Any) -> CandidateEvidenceJudgementV2:
    values: dict[str, Any] = {
        "response_version": "w10-expert-evidence-response-v2",
        "judgement_id": uuid4(),
        "session_id": uuid4(),
        "participant_id": uuid4(),
        "presentation_id": uuid4(),
        "query_id": uuid4(),
        "candidate_id": uuid4(),
        "comparison_digest": comparison_digest,
        "position_code": "GK",
        "md_subrubric": None,
        "state": JudgementState.RATED,
        "evidence_sufficiency": EvidenceSufficiencyV2.SUFFICIENT,
        "assessment_basis": AssessmentBasisV2.SUPPLIED_EVIDENCE,
        "relevance_rating": 3,
        "confidence": 4,
        "evidence_gap": None,
        "cited_independent_family_ids": ("ID-GK-01",),
        "explanation": None,
        "recorded_at": datetime(2026, 8, 6, tzinfo=UTC),
    }
    values.update(updates)
    draft = CandidateEvidenceJudgementV2.model_construct(**values, judgement_digest="0" * 64)
    values["judgement_digest"] = canonical_research_digest(draft.digest_projection())
    return CandidateEvidenceJudgementV2(**values)


@pytest.mark.parametrize(
    "x,y,index",
    ((0, 0, 0), (33, 66, 1), (34, 67, 5), (66, 66, 4), (67, 0, 6), (100, 100, 8)),
)
def test_neutral_recorded_coordinate_bins_are_exact(x: int, y: int, index: int) -> None:
    assert _bin_index(x, y) == index


def test_percentile_is_deterministic_midrank_over_observed_values() -> None:
    assert _midrank_percentile(2.0, [1.0, 2.0, 2.0, 4.0]) == 50.0


def test_independent_percentile_references_are_normalized_once_per_row_and_family(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = (_row("GK", 1), _row("GK", 2))
    monkeypatch.setattr(
        expert_evidence,
        "aggregate_actions_v2",
        lambda _rows, _paths: {row.grain_id: _aggregate() for row in rows},
    )
    original = expert_evidence._position_family
    calls: list[tuple[str, str]] = []

    def counted(position_code: str, family_id: str, raw: Any) -> Any:
        calls.append((position_code, family_id))
        return original(position_code, family_id, raw)

    monkeypatch.setattr(expert_evidence, "_position_family", counted)
    bundles = build_expert_evidence_bundles_v2(
        _matrix(*rows),
        action_paths=(),
        selected_grain_ids=tuple(row.grain_id for row in rows),
    )

    assert len(calls) == len(rows) * 6
    assert set(calls) == {
        ("GK", family_id)
        for family_id in (
            "ID-LOC-01",
            "ID-PASS-01",
            "ID-DUEL-01",
            "ID-DEFLOC-01",
            "ID-SHOTLOC-01",
            "ID-GK-01",
        )
    }
    assert all(
        metric.within_position_percentile == 50.0
        for bundle in bundles
        for family in bundle.independent_descriptors
        if family.availability
        in {EvidenceAvailabilityV2.OBSERVED_VALUE, EvidenceAvailabilityV2.OBSERVED_ZERO}
        for metric in family.metrics
    )


def test_zero_opportunity_is_insufficient_not_invalid_or_observed_zero() -> None:
    aggregate = _aggregate()
    aggregate.shots = _SpatialComponent()
    family = _raw_families(_row("FW"), aggregate, load_expert_evidence_policy_v2())["ID-SHOTLOC-01"]

    assert family.availability is EvidenceAvailabilityV2.INSUFFICIENT_OPPORTUNITIES
    assert family.denominator == 0
    assert all(metric.value is None for metric in family.metrics)


def test_defloc_exposes_separate_exact_component_floors_and_denominators() -> None:
    family = _raw_families(_row("DF"), _aggregate(), load_expert_evidence_policy_v2())[
        "ID-DEFLOC-01"
    ]

    assert [
        (item.component_id, item.denominator, item.floor) for item in family.opportunity_components
    ] == [
        ("defending_duel_valid_starts", 5, 5),
        ("interception_valid_starts", 5, 5),
        ("clearance_valid_starts", 3, 3),
    ]


def test_builder_reconstructs_exact_bytes_purposes_coverage_and_narrow_gk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = _row("GK")
    aggregate = _aggregate()
    monkeypatch.setattr(
        expert_evidence,
        "aggregate_actions_v2",
        lambda _rows, _paths: {row.grain_id: aggregate},
    )

    first = build_expert_evidence_bundles_v2(
        _matrix(row), action_paths=(), selected_grain_ids=(row.grain_id,)
    )[0]
    second = build_expert_evidence_bundles_v2(
        _matrix(row), action_paths=(), selected_grain_ids=(row.grain_id,)
    )[0]
    payload = participant_safe_evidence_bytes_v2(first)

    assert payload == participant_safe_evidence_bytes_v2(second)
    assert len(first.w09_inputs.metrics) == 16
    assert all(metric.used_by_w09_ranking for metric in first.w09_inputs.metrics)
    assert all(
        not metric.used_by_w09_ranking
        for family in first.independent_descriptors
        for metric in family.metrics
    )
    assert first.context.quantity.lineup_match_coverage.proportion == 1.0
    assert first.context.quantity.action_match_coverage.proportion == 1.0
    assert b'"gk.shots_faced"' in payload and b'"gk.save_percentage"' in payload
    assert b'"candidate_id"' not in payload and b'"retrieval_rank"' not in payload


def test_component_metrics_carry_their_own_exact_coverage_and_gk_minutes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    defender, _second_defender = _fixture_bundles(monkeypatch, position="DF")
    defloc = next(
        family for family in defender.independent_descriptors if family.family_id == "ID-DEFLOC-01"
    )
    goalkeeper_panel, _second_goalkeeper = _fixture_bundles(monkeypatch)
    goalkeeper = next(
        family
        for family in goalkeeper_panel.independent_descriptors
        if family.family_id == "ID-GK-01"
    )

    clearance = next(
        metric for metric in defloc.metrics if metric.metric_id.startswith("defloc.clearance.")
    )
    defending_duel = next(
        metric for metric in defloc.metrics if metric.metric_id.startswith("defloc.defending_duel.")
    )
    goal_kick = next(
        metric for metric in goalkeeper.metrics if metric.metric_id == "gk.goal_kicks_per90"
    )
    leaving = next(
        metric for metric in goalkeeper.metrics if metric.metric_id == "gk.leaving_line_per90"
    )
    reflex = next(metric for metric in goalkeeper.metrics if metric.metric_id == "gk.reflex_share")

    assert (clearance.coverage.observed, clearance.coverage.expected) == (3, 3)
    assert (defending_duel.coverage.observed, defending_duel.coverage.expected) == (5, 5)
    assert goal_kick.coverage.observed == 20
    assert leaving.coverage.observed == 3
    assert reflex.coverage.observed == 10
    assert (
        goal_kick.raw_opportunity_denominator == goalkeeper_panel.context.quantity.governed_minutes
    )
    assert leaving.raw_opportunity_denominator == goalkeeper_panel.context.quantity.governed_minutes
    assert defloc.raw_opportunity_denominator is None and defloc.opportunity_floor is None
    assert goalkeeper.raw_opportunity_denominator is None
    assert goalkeeper.opportunity_floor is None


def test_exact_comparison_binds_response_pair_position_branch_and_observed_citations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exemplar, candidate = _fixture_bundles(monkeypatch)
    comparison = build_participant_evidence_comparison_v2(exemplar, candidate)
    response = _response(comparison.comparison_digest)

    validate_response_comparison_v2(response, comparison)
    payload = participant_safe_comparison_bytes_v2(comparison)
    assert b'"comparison_digest"' in payload
    assert b'"player_id"' not in payload and b'"origin"' not in payload

    stale = _response("2" * 64)
    with pytest.raises(ValueError, match="exact evidence comparison"):
        validate_response_comparison_v2(stale, comparison)


def test_comparison_rejects_mixed_md_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    defensive, shooting = _fixture_bundles(
        monkeypatch,
        position="MD",
        branches=(MdEvidenceSubrubricV2.DEFENSIVE, MdEvidenceSubrubricV2.SHOOTING),
    )
    with pytest.raises(ExpertEvidenceBuildError, match="share position, policy and MD branch"):
        build_participant_evidence_comparison_v2(defensive, shooting)


def test_comparison_rejects_cross_panel_semantic_asymmetry_with_recomputed_digests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exemplar, candidate = _fixture_bundles(monkeypatch)
    candidate_payload = candidate.model_dump(mode="json")
    candidate_payload["independent_descriptors"][0]["label"] = "Asymmetric participant label"
    candidate_projection = {
        key: value for key, value in candidate_payload.items() if key != "bundle_digest"
    }
    candidate_payload["bundle_digest"] = canonical_research_digest(candidate_projection)
    asymmetric_candidate = ParticipantExpertEvidenceBundleV2.model_validate_json(
        json.dumps(candidate_payload)
    )
    comparison = build_participant_evidence_comparison_v2(exemplar, candidate)
    comparison_payload = comparison.model_dump(mode="json")
    comparison_payload["candidate"] = asymmetric_candidate.model_dump(mode="json")
    comparison_projection = {
        key: value for key, value in comparison_payload.items() if key != "comparison_digest"
    }
    comparison_payload["comparison_digest"] = canonical_research_digest(comparison_projection)

    with pytest.raises(ValidationError, match="symmetric evidence semantics"):
        ParticipantEvidenceComparisonV2.model_validate_json(json.dumps(comparison_payload))


def test_metric_formula_and_family_shape_mutations_fail_with_recomputed_bundle_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle, _candidate = _fixture_bundles(monkeypatch)
    payload = bundle.model_dump(mode="json")
    pass_metric = payload["independent_descriptors"][1]["metrics"][0]
    pass_metric["raw_value"] = 0.99
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="share values must reconstruct"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    metrics = payload["independent_descriptors"][1]["metrics"]
    metrics[0], metrics[1] = metrics[1], metrics[0]
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="metric roster or order"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    families = payload["independent_descriptors"]
    families[0], families[1] = families[1], families[0]
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="exact ordered roster"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    components = payload["independent_descriptors"][5]["opportunity_components"]
    components[1]["component_id"] = components[0]["component_id"]
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="components must be unique"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    w09_metrics = payload["w09_inputs"]["metrics"]
    w09_metrics[0], w09_metrics[1] = w09_metrics[1], w09_metrics[0]
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="metric roster or order"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    goal_kick = payload["independent_descriptors"][5]["metrics"][0]
    goal_kick["raw_opportunity_denominator"] = 200.0
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="per-90 raw denominator"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    pass_family = payload["independent_descriptors"][1]
    pass_component = pass_family["opportunity_components"][0]
    pass_component["raw_opportunity_denominator"] = 24
    pass_component["coverage"]["observed"] = 24
    pass_component["coverage"]["expected"] = 24
    pass_component["coverage"]["proportion"] = 1.0
    pass_family["raw_opportunity_denominator"] = 24
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="observed family requires every component"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    duel_family = payload["independent_descriptors"][2]
    duel_family["availability"] = "insufficient_opportunities"
    for metric in duel_family["metrics"]:
        metric["availability"] = "insufficient_opportunities"
        metric["raw_value"] = None
        metric["within_position_percentile"] = None
    projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
    payload["bundle_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="insufficient family requires a component below"):
        ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))

    for glossary_mutation in (
        {"label": "Tampered metric label"},
        {"definition": "Tampered metric definition"},
        {"coverage_definition": "Tampered coverage definition"},
        {
            "purpose": "INDEPENDENT_DESCRIPTOR",
            "used_by_w09_ranking": False,
        },
    ):
        payload = bundle.model_dump(mode="json")
        payload["glossary"][0].update(glossary_mutation)
        projection = {key: value for key, value in payload.items() if key != "bundle_digest"}
        payload["bundle_digest"] = canonical_research_digest(projection)
        with pytest.raises(ValidationError, match="glossary content must exactly reconstruct"):
            ParticipantExpertEvidenceBundleV2.model_validate_json(json.dumps(payload))


def test_unsupported_inferences_are_not_captured_and_structurally_non_numeric(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle, _candidate = _fixture_bundles(monkeypatch)
    unsupported = {item.inference_id: item for item in bundle.unsupported_inferences}

    assert "gk.shots_faced" in unsupported
    assert "gk.save_percentage" in unsupported
    assert all(
        item.availability is EvidenceAvailabilityV2.NOT_CAPTURED for item in unsupported.values()
    )
    numeric_keys = {"raw_value", "value", "numerator", "denominator", "percentile"}
    assert all(numeric_keys.isdisjoint(item.model_dump()) for item in unsupported.values())


def test_mandatory_family_failure_makes_selected_row_query_ineligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = _row("GK")
    aggregate = _aggregate()
    aggregate.gk_leaving_line = 2
    monkeypatch.setattr(
        expert_evidence,
        "aggregate_actions_v2",
        lambda _rows, _paths: {row.grain_id: aggregate},
    )

    with pytest.raises(ExpertEvidenceBuildError, match="query-ineligible"):
        build_expert_evidence_bundles_v2(
            _matrix(row), action_paths=(), selected_grain_ids=(row.grain_id,)
        )


def test_md_requires_one_explicit_selected_branch_and_rejects_extra_keys() -> None:
    row = _row("MD")
    with pytest.raises(ExpertEvidenceBuildError, match="every selected MD"):
        build_expert_evidence_bundles_v2(
            _matrix(row), action_paths=(), selected_grain_ids=(row.grain_id,)
        )
    with pytest.raises(ExpertEvidenceBuildError, match="unselected"):
        build_expert_evidence_bundles_v2(
            _matrix(_row("GK")),
            action_paths=(),
            selected_grain_ids=(_row("GK").grain_id,),
            md_subrubrics={row.grain_id: MdEvidenceSubrubricV2.DEFENSIVE},
        )


def test_retained_population_and_legacy_pack_coverage_is_deterministic() -> None:
    matrix_path = _ROOT / (
        "data/working/wyscout/v5/research_features/"
        "matrix_version=w09-historical-player-window-v1-a9f7cc2d5fc12ea0/"
        "feature-matrix-rows.parquet"
    )
    action_glob = str(
        _ROOT
        / (
            "data/working/wyscout/v5/research/"
            "build_id=2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e/"
            "canonical/actions/*/*.parquet"
        )
    )
    query = """
        WITH action AS (
          SELECT player_id, competition_id, season_id,
            count(*) total,
            count(*) FILTER (WHERE coordinate_evidence_state='valid') valid_starts,
            count(*) FILTER (WHERE event_id=8) passes,
            count(*) FILTER (WHERE event_id=1) duels,
            count(*) FILTER (WHERE event_id=1 AND sub_event_id=12
                             AND coordinate_evidence_state='valid') defending_duels,
            count(*) FILTER (WHERE list_contains(tag_ids,1401)
                             AND coordinate_evidence_state='valid') interceptions,
            count(*) FILTER (WHERE sub_event_id=71
                             AND coordinate_evidence_state='valid') clearances,
            count(*) FILTER (WHERE event_id=10
                             AND coordinate_evidence_state='valid') shots,
            count(*) FILTER (WHERE event_id=9 AND sub_event_id IN (90,91)) saves,
            count(*) FILTER (WHERE event_id=4 AND sub_event_id=40) leaves,
            count(*) FILTER (WHERE event_id=3 AND sub_event_id=34) kicks
          FROM read_parquet(?) WHERE player_id IS NOT NULL GROUP BY ALL
        )
        SELECT matrix.grain_id, matrix.position_code,
          valid_starts>=100 AND valid_starts::DOUBLE/total>=.95 loc_ok,
          passes>=25 pass_ok, duels>=20 duel_ok,
          defending_duels>=5 AND interceptions>=5 AND clearances>=3 def_ok,
          shots>=10 shot_ok, saves>=10 AND leaves>=3 AND kicks>=20 gk_ok
        FROM read_parquet(?) matrix JOIN action USING(player_id,competition_id,season_id)
    """
    cursor = duckdb.connect().execute(query, [action_glob, str(matrix_path)])
    names = [item[0] for item in cursor.description]
    rows = [dict(zip(names, values, strict=True)) for values in cursor.fetchall()]

    def eligible(row: dict[str, object]) -> bool:
        common = bool(row["loc_ok"] and row["pass_ok"])
        if row["position_code"] == "GK":
            return common and bool(row["gk_ok"])
        if row["position_code"] == "DF":
            return common and bool(row["duel_ok"] and row["def_ok"])
        if row["position_code"] == "FW":
            return common and bool(row["duel_ok"] and row["shot_ok"])
        return common and bool(row["duel_ok"] and (row["def_ok"] or row["shot_ok"]))

    assert {
        position: (
            sum(row["position_code"] == position for row in rows),
            sum(row["position_code"] == position and eligible(row) for row in rows),
        )
        for position in ("GK", "DF", "MD", "FW")
    } == {"GK": (136, 136), "DF": (713, 713), "MD": (711, 692), "FW": (415, 385)}

    by_grain = {row["grain_id"]: row for row in rows}
    pack = json.loads((_ROOT / "configs/evaluation/w10-frozen-query-pack-v1.json").read_bytes())
    coverage: dict[str, tuple[bool, bool] | int] = {}
    for item in pack["queries"]:
        grains = [item["exemplar_grain_id"], *[value["grain_id"] for value in item["candidates"]]]
        if item["exemplar_position_code"] == "MD":
            coverage[item["query_code"]] = (
                all(
                    by_grain[grain]["loc_ok"]
                    and by_grain[grain]["pass_ok"]
                    and by_grain[grain]["duel_ok"]
                    and by_grain[grain]["def_ok"]
                    for grain in grains
                ),
                all(
                    by_grain[grain]["loc_ok"]
                    and by_grain[grain]["pass_ok"]
                    and by_grain[grain]["duel_ok"]
                    and by_grain[grain]["shot_ok"]
                    for grain in grains
                ),
            )
        else:
            coverage[item["query_code"]] = sum(eligible(by_grain[grain]) for grain in grains)
    assert coverage["W10-Q03-GERMANY-MD-LOWER"] == (False, False)
    assert coverage["W10-Q07-ITALY-MD-HIGHER"] == (False, False)
    assert coverage["W10-Q04-SPAIN-FW-HIGHER"] == 10
    assert coverage["W10-Q08-FRANCE-FW-LOWER"] == 11

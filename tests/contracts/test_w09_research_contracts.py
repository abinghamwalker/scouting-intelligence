"""Adversarial contract tests for the W09 historical research boundary."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError

import scouting.contracts as public_contracts
from scouting.contracts.m0 import FeatureValue as M0FeatureValue
from scouting.contracts.m0 import FeatureValueState as M0FeatureValueState
from scouting.contracts.numerics import stable_weighted_unit_components
from scouting.contracts.research import (
    EligibilityDecision,
    EligibilityReason,
    EligibilityReasonCount,
    FeatureContribution,
    FeatureMatrixManifest,
    FeatureMatrixRow,
    FeatureValueState,
    FeatureWeight,
    MinuteEvidenceState,
    NamedFeatureValue,
    PopulationDecisionReason,
    ResearchArtifactFile,
    ResearchCandidate,
    ResearchCapability,
    ResearchComparison,
    ResearchComparisonRequest,
    ResearchCoverage,
    ResearchDatasetDescriptor,
    ResearchFeatureValue,
    ResearchFilters,
    ResearchIndexManifest,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchQueryResult,
    ResearchReplayReason,
    ResearchReplayReceipt,
    ResearchReplayStatus,
    ResearchReportDescriptor,
    ResearchVersionPins,
    RetrievalPopulationCounts,
    SavedResearchExperiment,
    SourcePopulationDecision,
    canonical_research_digest,
)

_ZERO = "0" * 64
_ONE = "1" * 64
_PLAYER = UUID("10000000-0000-4000-8000-000000000001")
_PLAYER_2 = UUID("10000000-0000-4000-8000-000000000002")
_COMPETITION = UUID("20000000-0000-4000-8000-000000000001")
_TEAM = UUID("21000000-0000-4000-8000-000000000001")
_CUTOFF = datetime(2026, 8, 5, tzinfo=UTC)
_REQUESTED = _CUTOFF + timedelta(hours=1)


def _pins(**overrides: object) -> ResearchVersionPins:
    values: dict[str, object] = {
        "feature_cutoff_ts": _CUTOFF,
        "dataset_version": "wyscout-v5-2017-18",
        "dataset_manifest_digest": _ZERO,
        "identity_bundle_digest": _ONE,
        "canonical_build_digest": "2" * 64,
        "matrix_version": "w09-matrix-v1",
        "matrix_manifest_digest": "3" * 64,
        "matrix_digest": "4" * 64,
        "feature_registry_version": "w09-features-v1",
        "feature_registry_digest": "5" * 64,
        "eligibility_policy_version": "w09-eligibility-v1",
        "eligibility_policy_digest": "6" * 64,
        "model_version": "w09-robust-v1",
        "model_configuration_digest": "7" * 64,
        "scorer_version": "shared-vector-scorer-v1",
        "scorer_code_digest": "8" * 64,
        "index_version": "w09-index-v1",
        "index_manifest_digest": "9" * 64,
        "catalogue_digest": "a" * 64,
    }
    values.update(overrides)
    return ResearchVersionPins.model_validate(values)


def _query(**overrides: object) -> ResearchQueryRequest:
    values: dict[str, object] = {
        "query_id": UUID("30000000-0000-4000-8000-000000000001"),
        "requested_at": _REQUESTED,
        "feature_cutoff_ts": _CUTOFF,
        "pins": _pins(),
        "mode": ResearchQueryMode.EXEMPLAR,
        "method": ResearchMethod.WEIGHTED_EUCLIDEAN,
        "exemplar_grain_id": "england:2017:player-0",
        "weights": (FeatureWeight(feature_name="passes_per_90", weight=1.0),),
        "filters": ResearchFilters(competition_id=_COMPETITION, season_id="2017"),
        "limit": 20,
    }
    values.update(overrides)
    draft = ResearchQueryRequest.model_construct(**values, query_digest=_ZERO)
    return ResearchQueryRequest.model_validate(
        {**values, "query_digest": canonical_research_digest(draft.digest_projection())}
    )


def _candidate(player: UUID, grain: str, rank: int, score: float) -> ResearchCandidate:
    return ResearchCandidate(
        rank=rank,
        grain_id=grain,
        player_id=player,
        display_name=f"Player {rank}",
        competition_id=_COMPETITION,
        position_code="MD",
        minutes=900.0,
        score=score,
        contributions=(
            FeatureContribution(
                feature_name="passes_per_90",
                query_value=10.0,
                candidate_value=10.0 + score,
                scaled_query_value=0.0,
                scaled_candidate_value=score,
                scaled_contrast=score,
                weight=1.0,
                contribution=score * score,
            ),
        ),
        limitations=("Historical resemblance is not a recruitment recommendation.",),
    )


def _result(**overrides: object) -> ResearchQueryResult:
    values: dict[str, object] = {
        "result_id": UUID("31000000-0000-4000-8000-000000000001"),
        "request": _query(),
        "generated_at": _REQUESTED + timedelta(seconds=1),
        "population": RetrievalPopulationCounts(
            matrix_rows=3,
            competition_rows=3,
            position_exclusions=0,
            minimum_minutes_exclusions=0,
            explicit_player_exclusions=0,
            exemplar_self_exclusions=1,
            filter_admitted_rows=2,
            missing_feature_exclusions=0,
            scored_rows=2,
            returned_rows=2,
        ),
        "candidates": (
            _candidate(_PLAYER, "england:2017:player-1", 1, 1.0),
            _candidate(_PLAYER_2, "england:2017:player-2", 2, 2.0),
        ),
        "warnings": ("Engineering evaluation only; G-RW4 is absent.",),
    }
    values.update(overrides)
    draft = ResearchQueryResult.model_construct(**values, result_digest=_ZERO)
    return ResearchQueryResult.model_validate(
        {**values, "result_digest": canonical_research_digest(draft.digest_projection())}
    )


def _matrix_row(player: UUID, grain: str, value: float) -> FeatureMatrixRow:
    state = FeatureValueState.ZERO if value == 0.0 else FeatureValueState.VALUE
    return FeatureMatrixRow(
        grain_id=grain,
        player_id=player,
        display_name="Historical player",
        competition_id=_COMPETITION,
        competition_name="England",
        season_id="2017",
        position_code="MD",
        team_ids=(_TEAM,),
        team_names=("Historical team",),
        minute_state=MinuteEvidenceState.EXACT,
        minutes=900.0,
        match_count=10,
        features=(
            ResearchFeatureValue(
                feature_name="passes_per_90",
                state=state,
                value=value,
            ),
        ),
        missing_feature_names=(),
        coverage=ResearchCoverage(
            lineup_matches_observed=10,
            lineup_matches_expected=10,
            action_matches_observed=10,
            action_matches_expected=10,
            coordinate_actions_observed=100,
            coordinate_actions_expected=100,
        ),
        window_start_utc=datetime(2017, 7, 1, tzinfo=UTC),
        window_end_utc=datetime(2018, 7, 1, tzinfo=UTC),
        feature_cutoff_ts=_CUTOFF,
        dataset_manifest_digest=_ZERO,
        identity_bundle_digest=_ONE,
        canonical_build_digest="2" * 64,
        feature_registry_digest="5" * 64,
        eligibility_policy_digest="6" * 64,
        eligibility_decision_digest="b" * 64,
        source_lineage_digest="c" * 64,
        source_action_count=100,
    )


def _comparison(result: ResearchQueryResult) -> ResearchComparison:
    request_values = {
        "comparison_id": UUID("32000000-0000-4000-8000-000000000001"),
        "result_id": result.result_id,
        "result_digest": result.result_digest,
        "query_digest": result.request.query_digest,
        "pins": result.request.pins,
        "grain_ids": tuple(item.grain_id for item in result.candidates),
    }
    request_draft = ResearchComparisonRequest.model_construct(
        **request_values, comparison_request_digest=_ZERO
    )
    request = ResearchComparisonRequest.model_validate(
        {
            **request_values,
            "comparison_request_digest": canonical_research_digest(
                request_draft.digest_projection()
            ),
        }
    )
    rows = (
        _matrix_row(_PLAYER, result.candidates[0].grain_id, 1.0),
        _matrix_row(_PLAYER_2, result.candidates[1].grain_id, 2.0),
    )
    draft = ResearchComparison.model_construct(
        request=request,
        rows=rows,
        comparison_digest=_ZERO,
    )
    return ResearchComparison.model_validate(
        {
            "request": request,
            "rows": rows,
            "comparison_digest": canonical_research_digest(
                draft.model_dump(mode="json", exclude={"comparison_digest"})
            ),
        }
    )


def _experiment() -> SavedResearchExperiment:
    result = _result()
    comparison = _comparison(result)
    report = ResearchReportDescriptor(
        report_format="json",
        report_relative_path="experiments/example/report.json",
        report_digest="d" * 64,
        generated_at=result.generated_at,
        pins=result.request.pins,
        query_digest=result.request.query_digest,
        result_digest=result.result_digest,
        comparison_digest=comparison.comparison_digest,
    )
    values = {
        "experiment_id": UUID("33000000-0000-4000-8000-000000000001"),
        "name": "Midfield resemblance",
        "created_at": result.generated_at,
        "request": result.request,
        "result": result,
        "comparison": comparison,
        "report": report,
    }
    draft = SavedResearchExperiment.model_construct(**values, experiment_digest=_ZERO)
    projection = draft.model_dump(mode="json", exclude={"experiment_digest"})
    return SavedResearchExperiment.model_validate(
        {**values, "experiment_digest": canonical_research_digest(projection)}
    )


def test_dataset_requires_strict_before_authorities() -> None:
    with pytest.raises(ValidationError, match="strictly before"):
        ResearchDatasetDescriptor(
            dataset_id=UUID("40000000-0000-4000-8000-000000000001"),
            dataset_version="wyscout-v5-2017-18",
            dataset_manifest_digest=_ZERO,
            provider_adapter="canonical-wyscout-historical-v1",
            provider_neutral_schema_version="historical-player-events-v1",
            rights_classification="wyscout_figshare_v5_cc_by_4",
            attribution="Pappalardo et al., supplied by Wyscout, CC BY 4.0",
            source_manifest_id=UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b"),
            source_manifest_digest=_ONE,
            source_completion_digest="2" * 64,
            identity_bundle_digest="3" * 64,
            source_available_at=datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC),
            identity_available_at=_CUTOFF,
            feature_cutoff_ts=_CUTOFF,
            window_start_utc=datetime(2017, 7, 1, tzinfo=UTC),
            window_end_utc=datetime(2018, 7, 1, tzinfo=UTC),
            source_match_count=1826,
            source_action_count=3071395,
            source_team_count=142,
            source_player_count=3603,
            capabilities=(ResearchCapability.EXEMPLAR_QUERY,),
            limitations=("Historical research data only.",),
        )


def test_population_and_window_ledgers_reject_contradictions() -> None:
    with pytest.raises(ValidationError, match="population decision"):
        SourcePopulationDecision(
            source_player_id="player:1",
            player_id=_PLAYER,
            lineup_evidence_present=False,
            grain_ids=("england:2017:player-1",),
            reason=PopulationDecisionReason.NO_LINEUP_EVIDENCE,
        )
    with pytest.raises(ValidationError, match="below-minimum"):
        EligibilityDecision(
            source_player_id="player:1",
            grain_id="england:2017:player-1",
            player_id=_PLAYER,
            competition_id=_COMPETITION,
            season_id="2017",
            eligibility_policy_version="v1",
            eligibility_policy_digest="6" * 64,
            minute_state=MinuteEvidenceState.EXACT,
            minutes=900.0,
            minimum_minutes=450.0,
            eligible=False,
            reason=EligibilityReason.BELOW_MINIMUM_MINUTES,
            feature_cutoff_ts=_CUTOFF,
            temporal_authorities_strictly_before_cutoff=True,
            source_match_count=10,
            source_action_count=100,
        )
    with pytest.raises(ValidationError, match="usable minute evidence"):
        EligibilityDecision(
            source_player_id="player:1",
            grain_id="england:2017:player-1",
            player_id=_PLAYER,
            competition_id=_COMPETITION,
            season_id="2017",
            eligibility_policy_version="v1",
            eligibility_policy_digest="6" * 64,
            minute_state=MinuteEvidenceState.EXACT,
            minutes=900.0,
            minimum_minutes=450.0,
            eligible=False,
            reason=EligibilityReason.UNUSABLE_MINUTES,
            feature_cutoff_ts=_CUTOFF,
            temporal_authorities_strictly_before_cutoff=True,
            source_match_count=10,
            source_action_count=100,
        )
    with pytest.raises(ValidationError, match="unusable minutes"):
        EligibilityDecision(
            source_player_id="player:1",
            grain_id="england:2017:player-1",
            player_id=_PLAYER,
            competition_id=_COMPETITION,
            season_id="2017",
            eligibility_policy_version="v1",
            eligibility_policy_digest="6" * 64,
            minute_state=MinuteEvidenceState.UNUSABLE,
            minutes=1.0,
            minimum_minutes=450.0,
            eligible=False,
            reason=EligibilityReason.UNUSABLE_MINUTES,
            feature_cutoff_ts=_CUTOFF,
            temporal_authorities_strictly_before_cutoff=True,
            source_match_count=10,
            source_action_count=100,
        )


def test_feature_value_semantics_are_canonical() -> None:
    with pytest.raises(ValidationError, match="zero state"):
        ResearchFeatureValue(feature_name="x", state=FeatureValueState.ZERO, value=1.0)
    with pytest.raises(ValidationError, match="negative zero"):
        ResearchFeatureValue(feature_name="x", state=FeatureValueState.ZERO, value=-0.0)
    with pytest.raises(ValidationError, match="zero must use"):
        ResearchFeatureValue(feature_name="x", state=FeatureValueState.VALUE, value=0.0)
    with pytest.raises(ValidationError, match="cannot carry numeric"):
        ResearchFeatureValue(
            feature_name="x",
            state=FeatureValueState.MISSING,
            value=None,
            numerator=1.0,
            denominator=2.0,
            reason="not observed",
        )


def test_query_binds_cutoff_mode_order_and_digest() -> None:
    with pytest.raises(ValidationError, match="cutoff must equal"):
        _query(feature_cutoff_ts=_CUTOFF - timedelta(seconds=1))
    with pytest.raises(ValidationError, match="exemplar mode"):
        _query(profile=(NamedFeatureValue(feature_name="passes_per_90", value=1.0),))
    with pytest.raises(ValidationError, match="feature order"):
        _query(
            mode=ResearchQueryMode.WEIGHTED_PROFILE,
            exemplar_grain_id=None,
            weights=(
                FeatureWeight(feature_name="passes_per_90", weight=1.0),
                FeatureWeight(feature_name="shots_per_90", weight=1.0),
            ),
            profile=(
                NamedFeatureValue(feature_name="shots_per_90", value=1.0),
                NamedFeatureValue(feature_name="passes_per_90", value=1.0),
            ),
        )
    valid = _query()
    with pytest.raises(ValidationError, match="query_digest"):
        ResearchQueryRequest.model_validate({**valid.model_dump(mode="python"), "limit": 1})


def test_version_pins_fail_closed_on_any_stale_digest() -> None:
    submitted = _pins()
    submitted.assert_compatible(_pins())
    with pytest.raises(ValueError, match="stale or incompatible"):
        submitted.assert_compatible(_pins(matrix_digest="f" * 64))


def test_population_counts_and_results_enforce_full_scoring_and_explanations() -> None:
    _result()
    with pytest.raises(ValidationError, match="competition rows"):
        RetrievalPopulationCounts(
            matrix_rows=3,
            competition_rows=2,
            position_exclusions=0,
            minimum_minutes_exclusions=0,
            explicit_player_exclusions=0,
            exemplar_self_exclusions=0,
            filter_admitted_rows=3,
            missing_feature_exclusions=0,
            scored_rows=3,
            returned_rows=2,
        )
    bad_candidate = _candidate(_PLAYER, "england:2017:player-1", 1, 1.0).model_copy(
        update={"score": 2.0}
    )
    with pytest.raises(ValidationError, match="Euclidean contributions"):
        _result(candidates=(bad_candidate, _candidate(_PLAYER_2, "x", 2, 3.0)))
    bad_term = FeatureContribution(
        feature_name="passes_per_90",
        query_value=10.0,
        candidate_value=10.0,
        scaled_query_value=1.0,
        scaled_candidate_value=1.0,
        scaled_contrast=0.0,
        weight=1.0,
        contribution=1.0,
    )
    bad_explanation = _candidate(_PLAYER, "england:2017:player-1", 1, 1.0).model_copy(
        update={"contributions": (bad_term,)}
    )
    with pytest.raises(ValidationError, match="Euclidean contributions"):
        _result(candidates=(bad_explanation, _candidate(_PLAYER_2, "x", 2, 2.0)))


def test_result_counts_require_corresponding_submitted_filters() -> None:
    population = RetrievalPopulationCounts(
        matrix_rows=3,
        competition_rows=3,
        position_exclusions=1,
        minimum_minutes_exclusions=0,
        explicit_player_exclusions=0,
        exemplar_self_exclusions=1,
        filter_admitted_rows=1,
        missing_feature_exclusions=0,
        scored_rows=1,
        returned_rows=1,
    )
    with pytest.raises(ValidationError, match="position exclusions require"):
        _result(
            population=population,
            candidates=(_candidate(_PLAYER, "england:2017:player-1", 1, 1.0),),
        )


def test_cosine_terms_bind_normalized_operands() -> None:
    request = _query(method=ResearchMethod.WEIGHTED_COSINE)
    contribution = FeatureContribution(
        feature_name="passes_per_90",
        query_value=10.0,
        candidate_value=10.0,
        scaled_query_value=1.0,
        scaled_candidate_value=1.0,
        scaled_contrast=0.0,
        weight=1.0,
        normalized_query_component=1.0,
        normalized_candidate_component=1.0,
        contribution=-1.0,
    )
    candidate = _candidate(_PLAYER, "england:2017:player-1", 1, 0.0).model_copy(
        update={"contributions": (contribution,)}
    )
    population = RetrievalPopulationCounts(
        matrix_rows=2,
        competition_rows=2,
        position_exclusions=0,
        minimum_minutes_exclusions=0,
        explicit_player_exclusions=0,
        exemplar_self_exclusions=1,
        filter_admitted_rows=1,
        missing_feature_exclusions=0,
        scored_rows=1,
        returned_rows=1,
    )
    _result(request=request, population=population, candidates=(candidate,))
    bad = candidate.model_copy(
        update={
            "contributions": (
                contribution.model_copy(update={"normalized_candidate_component": 0.5}),
            )
        }
    )
    with pytest.raises(ValidationError, match="normalized operands"):
        _result(request=request, population=population, candidates=(bad,))


def test_large_finite_cosine_explanation_validates_without_arithmetic_overflow() -> None:
    request = _query(
        method=ResearchMethod.WEIGHTED_COSINE,
        weights=(
            FeatureWeight(feature_name="passes_per_90", weight=1.0),
            FeatureWeight(feature_name="shots_per_90", weight=1.0),
        ),
    )
    query_components, _ = stable_weighted_unit_components((1e308, 1e308), (1.0, 1.0))
    candidate_components, _ = stable_weighted_unit_components((1.0, 1.0), (1.0, 1.0))
    contributions = tuple(
        FeatureContribution(
            feature_name=name,
            query_value=1e308,
            candidate_value=1.0,
            scaled_query_value=1e308,
            scaled_candidate_value=1.0,
            scaled_contrast=1.0 - 1e308,
            weight=1.0,
            normalized_query_component=query_components[index],
            normalized_candidate_component=candidate_components[index],
            contribution=-(query_components[index] * candidate_components[index]),
        )
        for index, name in enumerate(("passes_per_90", "shots_per_90"))
    )
    score = max(0.0, 1.0 + sum(item.contribution for item in contributions))
    candidate = ResearchCandidate(
        rank=1,
        grain_id="england:2017:player-1",
        player_id=_PLAYER,
        display_name="Player 1",
        competition_id=_COMPETITION,
        position_code="MD",
        minutes=900.0,
        score=score,
        contributions=contributions,
        limitations=("Historical resemblance is not a recruitment recommendation.",),
    )
    population = RetrievalPopulationCounts(
        matrix_rows=2,
        competition_rows=2,
        position_exclusions=0,
        minimum_minutes_exclusions=0,
        explicit_player_exclusions=0,
        exemplar_self_exclusions=1,
        filter_admitted_rows=1,
        missing_feature_exclusions=0,
        scored_rows=1,
        returned_rows=1,
    )
    _result(request=request, population=population, candidates=(candidate,))


def test_large_finite_euclidean_term_fails_as_controlled_validation_error() -> None:
    contribution = FeatureContribution(
        feature_name="passes_per_90",
        query_value=0.0,
        candidate_value=1e200,
        scaled_query_value=0.0,
        scaled_candidate_value=1e200,
        scaled_contrast=1e200,
        weight=1.0,
        contribution=1.0,
    )
    candidate = _candidate(_PLAYER, "england:2017:player-1", 1, 1.0).model_copy(
        update={"contributions": (contribution,)}
    )
    with pytest.raises(ValidationError, match="Euclidean contributions"):
        _result(
            population=RetrievalPopulationCounts(
                matrix_rows=2,
                competition_rows=2,
                position_exclusions=0,
                minimum_minutes_exclusions=0,
                explicit_player_exclusions=0,
                exemplar_self_exclusions=1,
                filter_admitted_rows=1,
                missing_feature_exclusions=0,
                scored_rows=1,
                returned_rows=1,
            ),
            candidates=(candidate,),
        )


def test_matrix_and_index_manifests_self_verify_population_and_files() -> None:
    reason_counts = tuple(
        EligibilityReasonCount(
            reason=reason,
            count=(
                1
                if reason is EligibilityReason.ELIGIBLE
                else 2995
                if reason is EligibilityReason.REQUIRED_FEATURE_MISSING
                else 0
            ),
        )
        for reason in EligibilityReason
    )
    file = ResearchArtifactFile(
        role="feature_matrix",
        relative_path="feature-matrix/part-00000.parquet",
        row_count=1,
        size_bytes=100,
        sha256="b" * 64,
        semantic_digest="c" * 64,
    )
    values = {
        "manifest_id": UUID("41000000-0000-4000-8000-000000000001"),
        "matrix_version": "v1",
        "matrix_digest": "4" * 64,
        "generated_at": _REQUESTED,
        "feature_cutoff_ts": _CUTOFF,
        "window_start_utc": datetime(2017, 7, 1, tzinfo=UTC),
        "window_end_utc": datetime(2018, 7, 1, tzinfo=UTC),
        "dataset_version": "v1",
        "dataset_manifest_digest": _ZERO,
        "source_manifest_id": UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b"),
        "source_manifest_digest": _ONE,
        "source_completion_digest": "2" * 64,
        "identity_bundle_digest": "3" * 64,
        "canonical_build_version": "v1",
        "canonical_build_digest": "4" * 64,
        "feature_registry_version": "v1",
        "feature_registry_digest": "5" * 64,
        "eligibility_policy_version": "v1",
        "eligibility_policy_digest": "6" * 64,
        "code_version": "v1",
        "code_digest": "7" * 64,
        "feature_names": ("passes_per_90",),
        "catalogue_player_count": 3603,
        "population_decision_count": 3603,
        "population_referred_count": 2996,
        "population_referred_grain_count": 2996,
        "population_referred_grain_ledger_digest": "8" * 64,
        "population_no_lineup_count": 607,
        "unresolved_identity_count": 15,
        "rejected_identity_count": 1,
        "rejected_actor_action_count": 226038,
        "eligibility_decision_count": 2996,
        "unique_eligibility_grain_count": 2996,
        "eligibility_ledger_digest": "9" * 64,
        "eligibility_reason_counts": reason_counts,
        "matrix_row_count": 1,
        "unique_matrix_grain_count": 1,
        "unique_matrix_player_count": 1,
        "files": (file,),
        "limitations": ("Historical resemblance engineering only.",),
    }
    draft = FeatureMatrixManifest.model_construct(**values, manifest_digest=_ZERO)
    manifest = FeatureMatrixManifest.model_validate(
        {**values, "manifest_digest": canonical_research_digest(draft.digest_projection())}
    )
    with pytest.raises(ValidationError, match="population decisions"):
        FeatureMatrixManifest.model_validate(
            {**manifest.model_dump(mode="python"), "population_no_lineup_count": 606}
        )
    with pytest.raises(ValidationError, match="one eligibility decision"):
        FeatureMatrixManifest.model_validate(
            {**manifest.model_dump(mode="python"), "eligibility_decision_count": 2995}
        )
    with pytest.raises(ValidationError, match="matrix grains must be unique"):
        FeatureMatrixManifest.model_validate(
            {**manifest.model_dump(mode="python"), "unique_matrix_grain_count": 2}
        )
    zero_referred = {
        **manifest.model_dump(mode="python"),
        "population_referred_count": 0,
        "population_no_lineup_count": 3603,
    }
    with pytest.raises(ValidationError, match="empty together"):
        FeatureMatrixManifest.model_validate(zero_referred)
    zero_grains = {
        **manifest.model_dump(mode="python"),
        "population_referred_grain_count": 0,
    }
    with pytest.raises(ValidationError, match="empty together"):
        FeatureMatrixManifest.model_validate(zero_grains)

    index_values = {
        "index_id": UUID("42000000-0000-4000-8000-000000000001"),
        "index_version": "v1",
        "generated_at": _REQUESTED,
        "feature_cutoff_ts": _CUTOFF,
        "matrix_version": manifest.matrix_version,
        "matrix_manifest_digest": manifest.manifest_digest,
        "matrix_digest": manifest.matrix_digest,
        "identity_bundle_digest": manifest.identity_bundle_digest,
        "feature_registry_version": manifest.feature_registry_version,
        "feature_registry_digest": manifest.feature_registry_digest,
        "eligibility_policy_version": manifest.eligibility_policy_version,
        "eligibility_policy_digest": manifest.eligibility_policy_digest,
        "model_version": "v1",
        "model_configuration_digest": "8" * 64,
        "scorer_version": "v1",
        "scorer_code_digest": "9" * 64,
        "methods": (ResearchMethod.WEIGHTED_EUCLIDEAN, ResearchMethod.WEIGHTED_COSINE),
        "feature_names": manifest.feature_names,
        "candidate_count": manifest.matrix_row_count,
        "catalogue_digest": "a" * 64,
        "files": (file,),
        "limitations": ("No expert relevance evidence.",),
    }
    index_draft = ResearchIndexManifest.model_construct(**index_values, manifest_digest=_ZERO)
    index = ResearchIndexManifest.model_validate(
        {
            **index_values,
            "manifest_digest": canonical_research_digest(index_draft.digest_projection()),
        }
    )
    with pytest.raises(ValidationError, match="manifest digest"):
        ResearchIndexManifest.model_validate(
            {**index.model_dump(mode="python"), "candidate_count": 2}
        )


def test_comparison_experiment_and_report_are_cross_bound() -> None:
    experiment = _experiment()
    assert experiment.comparison is not None
    changed_report = experiment.report.model_copy(update={"result_digest": "e" * 64})
    with pytest.raises(ValidationError, match="report must bind"):
        SavedResearchExperiment.model_validate(
            {**experiment.model_dump(mode="python"), "report": changed_report}
        )
    wrong_row = experiment.comparison.rows[0].model_copy(update={"player_id": _PLAYER_2})
    comparison_values = {
        "request": experiment.comparison.request,
        "rows": (wrong_row, experiment.comparison.rows[1]),
    }
    draft = ResearchComparison.model_construct(**comparison_values, comparison_digest=_ZERO)
    changed_comparison = ResearchComparison.model_validate(
        {
            **comparison_values,
            "comparison_digest": canonical_research_digest(
                draft.model_dump(mode="json", exclude={"comparison_digest"})
            ),
        }
    )
    with pytest.raises(ValidationError, match="comparison row identity"):
        SavedResearchExperiment.model_validate(
            {**experiment.model_dump(mode="python"), "comparison": changed_comparison}
        )


def test_replay_receipt_binds_the_saved_experiment_and_self_digest() -> None:
    experiment = _experiment()
    values = {
        "replay_receipt_id": UUID("34000000-0000-4000-8000-000000000001"),
        "experiment_id": experiment.experiment_id,
        "saved_experiment_digest": experiment.experiment_digest,
        "saved_query_digest": experiment.request.query_digest,
        "replay_query_digest": experiment.request.query_digest,
        "replayed_at": experiment.created_at + timedelta(seconds=1),
        "saved_pins": experiment.request.pins,
        "loaded_pins": experiment.request.pins,
        "original_result_id": experiment.result.result_id,
        "replay_result_id": experiment.result.result_id,
        "original_result_digest": experiment.result.result_digest,
        "replay_result_digest": experiment.result.result_digest,
        "status": ResearchReplayStatus.REPRODUCED,
        "reason": ResearchReplayReason.EXACT_REPRODUCTION,
    }
    draft = ResearchReplayReceipt.model_construct(**values, receipt_digest=_ZERO)
    receipt = ResearchReplayReceipt.model_validate(
        {**values, "receipt_digest": canonical_research_digest(draft.digest_projection())}
    )
    with pytest.raises(ValidationError, match="reproduced status"):
        ResearchReplayReceipt.model_validate(
            {
                **receipt.model_dump(mode="python"),
                "replay_result_digest": "f" * 64,
                "receipt_digest": _ZERO,
            }
        )
    mismatch_values = {
        **values,
        "replay_query_digest": "e" * 64,
        "replay_result_id": UUID("34000000-0000-4000-8000-000000000002"),
        "replay_result_digest": "f" * 64,
        "status": ResearchReplayStatus.RESULT_MISMATCH,
        "reason": ResearchReplayReason.DETERMINISTIC_RESULT_MISMATCH,
    }
    mismatch_draft = ResearchReplayReceipt.model_construct(**mismatch_values, receipt_digest=_ZERO)
    with pytest.raises(ValidationError, match="identical saved query"):
        ResearchReplayReceipt.model_validate(
            {
                **mismatch_values,
                "receipt_digest": canonical_research_digest(mismatch_draft.digest_projection()),
            }
        )


def test_package_exports_keep_m0_and_research_state_pairs_unambiguous() -> None:
    assert public_contracts.FeatureValue is M0FeatureValue
    assert public_contracts.FeatureValueState is M0FeatureValueState
    assert public_contracts.M0FeatureValue is M0FeatureValue
    assert public_contracts.M0FeatureValueState is M0FeatureValueState
    assert public_contracts.ResearchFeatureValue is ResearchFeatureValue
    assert public_contracts.ResearchFeatureValueState is FeatureValueState
    public_contracts.FeatureValue(
        state=public_contracts.FeatureValueState.ZERO,
        numeric_value=0.0,
    )
    public_contracts.ResearchFeatureValue(
        feature_name="x",
        state=public_contracts.ResearchFeatureValueState.ZERO,
        value=0.0,
    )


def test_contracts_reject_coercion_extra_fields_and_noncanonical_numbers() -> None:
    valid = _query()
    legacy_filters = ResearchFilters.model_validate({"competition_id": _COMPETITION})
    assert legacy_filters.season_id is None
    assert "season_id" not in legacy_filters.model_dump(mode="json")
    with pytest.raises(ValidationError):
        ResearchQueryRequest.model_validate({**valid.model_dump(mode="python"), "limit": "20"})
    with pytest.raises(ValidationError):
        ResearchFilters.model_validate(
            {"competition_id": str(_COMPETITION), "fictional_role": "scout"}
        )
    with pytest.raises(ValidationError, match="negative zero"):
        FeatureWeight(feature_name="x", weight=-0.0)
    with pytest.raises(ValidationError):
        FeatureWeight(feature_name="x", weight=float("nan"))

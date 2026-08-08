"""Unit evidence for deterministic W09 research reports."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

import pytest

from scouting.contracts.research import (
    FeatureContribution,
    FeatureMatrixRow,
    FeatureValueState,
    FeatureWeight,
    MinuteEvidenceState,
    ResearchCandidate,
    ResearchComparison,
    ResearchComparisonRequest,
    ResearchCoverage,
    ResearchFeatureValue,
    ResearchFilters,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchQueryResult,
    ResearchVersionPins,
    RetrievalPopulationCounts,
    canonical_research_digest,
)
from scouting.reporting.research import (
    ResearchReportInputError,
    render_research_report,
)
from scouting.storage.formats import canonical_json_bytes
from scouting.storage.research import research_report_relative_path

_CUTOFF = datetime(2019, 1, 1, tzinfo=UTC)
_REQUESTED = datetime(2026, 8, 5, 10, 0, tzinfo=UTC)
_RESULT_AT = datetime(2026, 8, 5, 10, 1, tzinfo=UTC)
_REPORT_AT = datetime(2026, 8, 5, 10, 2, tzinfo=UTC)
_COMPETITION_ID = UUID("10000000-0000-0000-0000-000000000001")
_RIGHTS = "wyscout_figshare_v5_cc_by_4"
_ATTRIBUTION = "Wyscout public dataset on figshare, CC BY 4.0."
_RIGHTS_LIMITATIONS = ("Retained historical 2017/18 source scope only.",)


def _digest(value: int) -> str:
    return f"{value:064x}"


def _pins() -> ResearchVersionPins:
    return ResearchVersionPins(
        feature_cutoff_ts=_CUTOFF,
        dataset_version="wyscout-2017-18-v1",
        dataset_manifest_digest=_digest(1),
        identity_bundle_digest=_digest(2),
        canonical_build_digest=_digest(3),
        matrix_version="player-season-v1",
        matrix_manifest_digest=_digest(4),
        matrix_digest=_digest(5),
        feature_registry_version="features-v1",
        feature_registry_digest=_digest(6),
        eligibility_policy_version="minutes-v1",
        eligibility_policy_digest=_digest(7),
        model_version="robust-scaling-v1",
        model_configuration_digest=_digest(8),
        scorer_version="weighted-distance-v1",
        scorer_code_digest=_digest(9),
        index_version="historical-index-v1",
        index_manifest_digest=_digest(10),
        catalogue_digest=_digest(11),
    )


def _request() -> ResearchQueryRequest:
    fields = {
        "query_id": UUID("30000000-0000-0000-0000-000000000001"),
        "requested_at": _REQUESTED,
        "feature_cutoff_ts": _CUTOFF,
        "pins": _pins(),
        "mode": ResearchQueryMode.EXEMPLAR,
        "method": ResearchMethod.WEIGHTED_EUCLIDEAN,
        "exemplar_grain_id": "player-season:exemplar",
        "weights": (
            FeatureWeight(feature_name="actions_per_90", weight=0.75),
            FeatureWeight(feature_name="pass_accuracy", weight=0.25),
        ),
        "filters": ResearchFilters(
            competition_id=_COMPETITION_ID,
            season_id="2017-18",
            position_codes=("MD",),
            minimum_minutes=900.0,
            excluded_player_ids=(UUID("20000000-0000-0000-0000-000000000099"),),
        ),
        "limit": 2,
    }
    draft = ResearchQueryRequest.model_construct(**fields, query_digest=_digest(0))
    return ResearchQueryRequest(
        **fields,
        query_digest=canonical_research_digest(draft.digest_projection()),
    )


def _result(*, display_name: str = "Historical Player 1") -> ResearchQueryResult:
    request = _request()
    candidates = tuple(
        ResearchCandidate(
            rank=rank,
            grain_id=f"player-season:{rank}",
            player_id=UUID(f"20000000-0000-0000-0000-{rank:012d}"),
            display_name=display_name if rank == 1 else f"Historical Player {rank}",
            competition_id=_COMPETITION_ID,
            position_code="MD",
            minutes=1_500.0 + rank,
            score=float(rank),
            contributions=(
                FeatureContribution(
                    feature_name="actions_per_90",
                    query_value=1.0,
                    candidate_value=float(rank + 1),
                    scaled_query_value=0.25,
                    scaled_candidate_value=float(rank) + 0.25,
                    scaled_contrast=float(rank),
                    weight=0.75,
                    contribution=0.75 * rank * rank,
                ),
                FeatureContribution(
                    feature_name="pass_accuracy",
                    query_value=0.8,
                    candidate_value=0.8 + (rank * 0.1),
                    scaled_query_value=0.0,
                    scaled_candidate_value=float(rank),
                    scaled_contrast=float(rank),
                    weight=0.25,
                    contribution=0.25 * rank * rank,
                ),
            ),
            limitations=("Historical evidence is limited to one retained season.",),
        )
        for rank in (1, 2)
    )
    fields = {
        "result_id": UUID("40000000-0000-0000-0000-000000000001"),
        "request": request,
        "generated_at": _RESULT_AT,
        "population": RetrievalPopulationCounts(
            matrix_rows=3_000,
            competition_rows=2_500,
            position_exclusions=1_000,
            minimum_minutes_exclusions=400,
            explicit_player_exclusions=1,
            exemplar_self_exclusions=1,
            filter_admitted_rows=1_098,
            missing_feature_exclusions=10,
            scored_rows=1_088,
            returned_rows=2,
        ),
        "candidates": candidates,
        "warnings": ("No expert football-relevance validation has been completed.",),
    }
    draft = ResearchQueryResult.model_construct(**fields, result_digest=_digest(0))
    return ResearchQueryResult(
        **fields,
        result_digest=canonical_research_digest(draft.digest_projection()),
    )


def _comparison_row(
    candidate: ResearchCandidate,
    pins: ResearchVersionPins,
    ordinal: int,
) -> FeatureMatrixRow:
    return FeatureMatrixRow(
        grain_id=candidate.grain_id,
        player_id=candidate.player_id,
        display_name=candidate.display_name,
        competition_id=candidate.competition_id,
        competition_name="Historical Competition",
        season_id="2017-18",
        position_code=candidate.position_code,
        team_ids=(UUID(f"70000000-0000-0000-0000-{ordinal:012d}"),),
        team_names=(f"Historical Team {ordinal}",),
        minute_state=MinuteEvidenceState.EXACT,
        minutes=candidate.minutes,
        match_count=20,
        features=(
            ResearchFeatureValue(
                feature_name="actions_per_90",
                state=FeatureValueState.VALUE,
                value=float(ordinal + 1),
            ),
            ResearchFeatureValue(
                feature_name="pass_accuracy",
                state=FeatureValueState.VALUE,
                value=0.8 + (ordinal * 0.1),
            ),
        ),
        missing_feature_names=(),
        coverage=ResearchCoverage(
            lineup_matches_observed=20,
            lineup_matches_expected=20,
            action_matches_observed=20,
            action_matches_expected=20,
            coordinate_actions_observed=100,
            coordinate_actions_expected=100,
        ),
        window_start_utc=datetime(2017, 7, 1, tzinfo=UTC),
        window_end_utc=datetime(2018, 7, 1, tzinfo=UTC),
        feature_cutoff_ts=pins.feature_cutoff_ts,
        dataset_manifest_digest=pins.dataset_manifest_digest,
        identity_bundle_digest=pins.identity_bundle_digest,
        canonical_build_digest=pins.canonical_build_digest,
        feature_registry_digest=pins.feature_registry_digest,
        eligibility_policy_digest=pins.eligibility_policy_digest,
        eligibility_decision_digest=_digest(20 + ordinal),
        source_lineage_digest=_digest(30 + ordinal),
        source_action_count=100,
    )


def _comparison(
    result: ResearchQueryResult,
    *,
    result_id: UUID | None = None,
) -> ResearchComparison:
    grain_ids = tuple(candidate.grain_id for candidate in result.candidates)
    request_fields = {
        "comparison_id": UUID("60000000-0000-0000-0000-000000000001"),
        "result_id": result_id or result.result_id,
        "result_digest": result.result_digest,
        "query_digest": result.request.query_digest,
        "pins": result.request.pins,
        "grain_ids": grain_ids,
    }
    request_draft = ResearchComparisonRequest.model_construct(
        **request_fields,
        comparison_request_digest=_digest(0),
    )
    request = ResearchComparisonRequest(
        **request_fields,
        comparison_request_digest=canonical_research_digest(request_draft.digest_projection()),
    )
    rows = tuple(
        _comparison_row(candidate, result.request.pins, ordinal)
        for ordinal, candidate in enumerate(result.candidates, start=1)
    )
    draft = ResearchComparison.model_construct(
        request=request,
        rows=rows,
        comparison_digest=_digest(0),
    )
    return ResearchComparison(
        request=request,
        rows=rows,
        comparison_digest=canonical_research_digest(
            draft.model_dump(mode="json", exclude={"comparison_digest"})
        ),
    )


def _render(
    result: ResearchQueryResult,
    *,
    comparison: ResearchComparison | None = None,
    report_format: str = "json",
    attribution: str = _ATTRIBUTION,
):
    return render_research_report(
        result,
        comparison=comparison,
        report_format=report_format,
        generated_at=_REPORT_AT,
        rights_classification=_RIGHTS,
        attribution=attribution,
        rights_limitations=_RIGHTS_LIMITATIONS,
    )


def test_json_report_is_canonical_stable_complete_and_content_addressed() -> None:
    result = _result()
    comparison = _comparison(result)

    first = _render(result, comparison=comparison)
    second = _render(result, comparison=comparison)
    decoded = json.loads(first.payload.decode("utf-8"))

    assert first == second
    assert canonical_json_bytes(decoded) == first.payload
    assert hashlib.sha256(first.payload).hexdigest() == first.descriptor.report_digest
    assert first.descriptor.report_relative_path == research_report_relative_path(
        first.descriptor.report_digest,
        "json",
    )
    assert first.descriptor.pins == result.request.pins
    assert first.descriptor.query_digest == result.request.query_digest
    assert first.descriptor.result_digest == result.result_digest
    assert first.descriptor.comparison_digest == comparison.comparison_digest
    assert decoded["query"] == result.request.model_dump(mode="json")
    assert decoded["population"] == result.population.model_dump(mode="json")
    assert decoded["ranked_historical_players"] == [
        candidate.model_dump(mode="json") for candidate in result.candidates
    ]
    assert decoded["comparison"] == comparison.model_dump(mode="json")
    assert decoded["version_pins"] == result.request.pins.model_dump(mode="json")
    assert decoded["rights"]["attribution"] == _ATTRIBUTION
    assert decoded["claim"]["boundary"] == "historical_resemblance_research_only"


def test_html_report_is_stable_self_contained_and_escapes_every_data_surface() -> None:
    result = _result(display_name='<script>alert("player")</script>')
    comparison = _comparison(result)
    attribution = '<img src="remote" onerror="alert(1)">'

    first = _render(
        result,
        comparison=comparison,
        report_format="html",
        attribution=attribution,
    )
    second = _render(
        result,
        comparison=comparison,
        report_format="html",
        attribution=attribution,
    )
    text = first.payload.decode("utf-8")
    lowered = text.lower()

    assert first == second
    assert first.payload.startswith(b"<!doctype html>\n")
    assert hashlib.sha256(first.payload).hexdigest() == first.descriptor.report_digest
    assert first.descriptor.report_relative_path.endswith(".html")
    assert "<script" not in lowered
    assert "<img" not in lowered
    assert "javascript:" not in lowered
    assert 'src="http' not in lowered
    assert "&lt;script&gt;alert(&quot;player&quot;)&lt;/script&gt;" in text
    assert "&lt;img src=&quot;remote&quot; onerror=&quot;alert(1)&quot;&gt;" in text
    assert "raw, scaled, and score contributions" in lowered
    assert "full-population accounting" in lowered
    assert "missing features" not in lowered
    assert "recruitment usefulness" not in lowered
    assert "synthetic player" not in lowered


def test_comparison_must_bind_the_exact_result() -> None:
    result = _result()
    wrong_result = _comparison(
        result,
        result_id=UUID("40000000-0000-0000-0000-000000000099"),
    )

    with pytest.raises(ResearchReportInputError, match="exact research result"):
        _render(result, comparison=wrong_result)


def test_renderer_rejects_invalid_format_clock_rights_and_mutated_contract() -> None:
    result = _result()
    with pytest.raises(ResearchReportInputError, match="report_format"):
        _render(result, report_format="pdf")
    with pytest.raises(ResearchReportInputError, match="timezone-aware UTC"):
        render_research_report(
            result,
            report_format="json",
            generated_at=datetime(2026, 8, 5, 10, 2),
            rights_classification=_RIGHTS,
            attribution=_ATTRIBUTION,
            rights_limitations=_RIGHTS_LIMITATIONS,
        )
    with pytest.raises(ResearchReportInputError, match="unsupported"):
        render_research_report(
            result,
            report_format="json",
            generated_at=_REPORT_AT,
            rights_classification="unknown",
            attribution=_ATTRIBUTION,
            rights_limitations=_RIGHTS_LIMITATIONS,
        )
    mutated = result.model_copy(update={"result_digest": _digest(63)})
    with pytest.raises(ResearchReportInputError, match="result contract rejected"):
        _render(mutated)

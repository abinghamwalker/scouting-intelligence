"""Contracts for the plain-language historical-player comparison pilot."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from scouting.contracts.expert_relevance import (
    AssessmentBasisV2,
    EvidenceGapV2,
    EvidenceSufficiencyV2,
    HistoricalComparisonJudgementV1,
    HistoricalComparisonPilotDebriefV1,
    JudgementState,
    participant_keyed_candidate_order,
)
from scouting.contracts.research import canonical_research_digest


def _judgement(**updates: Any) -> HistoricalComparisonJudgementV1:
    values: dict[str, Any] = {
        "response_version": "historical-player-comparison-response-v1",
        "judgement_id": uuid4(),
        "session_id": uuid4(),
        "participant_id": uuid4(),
        "presentation_id": uuid4(),
        "query_id": uuid4(),
        "candidate_id": uuid4(),
        "comparison_digest": "1" * 64,
        "position_code": "GK",
        "md_subrubric": None,
        "state": JudgementState.RATED,
        "evidence_sufficiency": EvidenceSufficiencyV2.SUFFICIENT,
        "assessment_basis": AssessmentBasisV2.SUPPLIED_EVIDENCE,
        "relevance_rating": 3,
        "confidence": 4,
        "evidence_gap": None,
        "cited_independent_family_ids": ("ID-GK-01",),
        "statistics_used_to_find_similar_players_helped": True,
        "explanation": "The additional goalkeeper evidence made the comparison assessable.",
        "recorded_at": datetime(2026, 8, 7, 10, 0, tzinfo=UTC),
    }
    values.update(updates)
    draft = HistoricalComparisonJudgementV1.model_construct(**values, judgement_digest="0" * 64)
    values["judgement_digest"] = canonical_research_digest(draft.digest_projection())
    return HistoricalComparisonJudgementV1(**values)


def _debrief(**updates: Any) -> HistoricalComparisonPilotDebriefV1:
    values: dict[str, Any] = {
        "debrief_version": "historical-player-comparison-debrief-v1",
        "debrief_id": uuid4(),
        "session_id": uuid4(),
        "participant_id": uuid4(),
        "names_or_minutes_only_for_any_comparison": False,
        "names_or_minutes_only_details": None,
        "any_position_lacked_enough_evidence": False,
        "position_evidence_details": None,
        "any_label_chart_warning_or_navigation_unclear": False,
        "interface_clarity_details": None,
        "form_appeared_to_reveal_system_preference": False,
        "preference_revelation_details": None,
        "recorded_at": datetime(2026, 8, 7, 10, 5, tzinfo=UTC),
    }
    values.update(updates)
    draft = HistoricalComparisonPilotDebriefV1.model_construct(**values, debrief_digest="0" * 64)
    values["debrief_digest"] = canonical_research_digest(draft.digest_projection())
    return HistoricalComparisonPilotDebriefV1(**values)


def test_reworked_response_has_a_distinct_version_without_changing_rating_semantics() -> None:
    response = _judgement()

    assert response.schema_version == 3
    assert response.response_version == "historical-player-comparison-response-v1"
    assert response.state is JudgementState.RATED
    assert response.evidence_sufficiency is EvidenceSufficiencyV2.SUFFICIENT
    assert response.assessment_basis is AssessmentBasisV2.SUPPLIED_EVIDENCE
    assert response.relevance_rating == 3
    assert response.confidence == 4
    assert response.cited_independent_family_ids == ("ID-GK-01",)
    assert response.statistics_used_to_find_similar_players_helped is True

    mutation = response.model_dump(mode="python")
    mutation["confidence"] = 2
    with pytest.raises(ValidationError, match="digest"):
        HistoricalComparisonJudgementV1.model_validate(mutation)


def test_unable_response_preserves_explicit_missingness_without_form_citations() -> None:
    response = _judgement(
        state=JudgementState.UNABLE_TO_ASSESS,
        evidence_sufficiency=EvidenceSufficiencyV2.INSUFFICIENT,
        assessment_basis=AssessmentBasisV2.UNABLE_TO_ASSESS,
        relevance_rating=None,
        confidence=None,
        evidence_gap=EvidenceGapV2.MISSING_DESCRIPTOR,
        cited_independent_family_ids=(),
        statistics_used_to_find_similar_players_helped=False,
        explanation="A necessary type of playing evidence was missing.",
    )

    assert response.state is JudgementState.UNABLE_TO_ASSESS
    assert response.relevance_rating is None
    assert response.confidence is None
    assert response.cited_independent_family_ids == ()

    with pytest.raises(ValidationError, match="cannot cite information from the form"):
        _judgement(
            state=JudgementState.UNABLE_TO_ASSESS,
            evidence_sufficiency=EvidenceSufficiencyV2.INSUFFICIENT,
            assessment_basis=AssessmentBasisV2.UNABLE_TO_ASSESS,
            relevance_rating=None,
            confidence=None,
            evidence_gap=EvidenceGapV2.MISSING_DESCRIPTOR,
            cited_independent_family_ids=(),
            statistics_used_to_find_similar_players_helped=True,
            explanation="A necessary type of playing evidence was missing.",
        )


def test_pilot_feedback_is_a_separate_four_question_contract() -> None:
    debrief = _debrief()
    rating_fields = {
        "state",
        "evidence_sufficiency",
        "assessment_basis",
        "relevance_rating",
        "confidence",
        "evidence_gap",
        "cited_independent_family_ids",
        "explanation",
    }
    feedback_answers = {
        "names_or_minutes_only_for_any_comparison",
        "any_position_lacked_enough_evidence",
        "any_label_chart_warning_or_navigation_unclear",
        "form_appeared_to_reveal_system_preference",
    }

    assert feedback_answers <= set(type(debrief).model_fields)
    assert rating_fields.isdisjoint(type(debrief).model_fields)
    assert "pilot_feedback" not in type(_judgement()).model_fields


@pytest.mark.parametrize(
    ("answer_field", "details_field"),
    (
        (
            "names_or_minutes_only_for_any_comparison",
            "names_or_minutes_only_details",
        ),
        ("any_position_lacked_enough_evidence", "position_evidence_details"),
        (
            "any_label_chart_warning_or_navigation_unclear",
            "interface_clarity_details",
        ),
        (
            "form_appeared_to_reveal_system_preference",
            "preference_revelation_details",
        ),
    ),
)
def test_each_yes_pilot_feedback_answer_requires_its_own_explanation(
    answer_field: str,
    details_field: str,
) -> None:
    with pytest.raises(ValidationError, match="each yes pilot-feedback answer"):
        _debrief(**{answer_field: True})

    retained = _debrief(
        **{
            answer_field: True,
            details_field: "A concrete participant explanation retained for this question.",
        }
    )
    assert getattr(retained, answer_field) is True
    assert getattr(retained, details_field) is not None

    with pytest.raises(ValidationError, match="each yes pilot-feedback answer"):
        _debrief(
            **{
                answer_field: False,
                details_field: "Details cannot be detached from a yes answer.",
            }
        )


def test_pilot_feedback_rejects_semantic_mutation_after_digesting() -> None:
    payload = _debrief().model_dump(mode="python")
    payload["form_appeared_to_reveal_system_preference"] = True
    payload["preference_revelation_details"] = (
        "The presentation appeared to reveal a preferred comparison."
    )

    with pytest.raises(ValidationError, match="pilot debrief digest"):
        HistoricalComparisonPilotDebriefV1.model_validate(payload)


def test_participant_keyed_order_is_repeatable_and_uses_no_response_outcome() -> None:
    comparison_ids = tuple(
        UUID(f"00000000-0000-0000-0000-{ordinal:012d}") for ordinal in range(1, 6)
    )
    first_key = "1" * 64
    second_key = "2" * 64

    first = participant_keyed_candidate_order(first_key, comparison_ids)
    replay = participant_keyed_candidate_order(first_key, comparison_ids)
    second = participant_keyed_candidate_order(second_key, comparison_ids)

    assert first == replay
    assert set(first) == set(comparison_ids)
    assert second != first

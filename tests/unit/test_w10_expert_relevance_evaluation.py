from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from fractions import Fraction
from pathlib import Path
from typing import Any, Literal, cast
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
from pydantic import ValidationError

from scouting.contracts.expert_relevance import (
    CandidateJudgement,
    CandidateOrigin,
    CandidatePresentation,
    ConsentRecord,
    ExpertExperienceKind,
    ExpertGateDecisionKind,
    FormalStudySubmission,
    FrozenCandidate,
    JudgementState,
    ParticipantEligibility,
    PresentationKind,
    ProtocolApproval,
    StudyMode,
    StudySession,
    build_formal_candidate_presentations,
    participant_code_digest,
)
from scouting.contracts.primitives import ContractModel
from scouting.contracts.research import canonical_research_digest
from scouting.evaluation.expert_relevance import (
    DEFAULT_PRESENTATION_PATH,
    ExpertRelevanceEvaluationError,
    _load_protected_submissions,
    evaluate_expert_relevance,
    load_frozen_presentation,
    load_frozen_protocol,
    load_frozen_query_pack,
    paired_query_bootstrap,
    render_safe_report,
)
from scouting.storage.formats import canonical_json_bytes

_NAMESPACE = uuid5(NAMESPACE_URL, "w10-expert-relevance-implementation-fixtures")
_EVALUATED_AT = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
type RatingRule = Callable[[FrozenCandidate], int]
type ScheduleMutation = Literal[
    "terminal",
    "reordered",
    "adjacent",
    "under_delayed",
    "wrong_reference",
    "wrong_id",
    "participant_substituted",
]


def _finish_digest[T: ContractModel](
    model: type[T], payload: dict[str, Any], digest_field: str
) -> T:
    draft = model.model_construct(**payload, **{digest_field: "0" * 64})
    payload[digest_field] = canonical_research_digest(draft.digest_projection())
    return model(**payload)


def _approval() -> ProtocolApproval:
    protocol = load_frozen_protocol()
    query_pack = load_frozen_query_pack()
    payload: dict[str, Any] = {
        "approval_id": uuid5(_NAMESPACE, "approval"),
        "protocol_version": protocol.protocol_version,
        "protocol_digest": protocol.protocol_digest,
        "query_pack_version": query_pack.query_pack_version,
        "query_pack_digest": query_pack.query_pack_digest,
        "approved_at": query_pack.built_at + timedelta(minutes=1),
        "approved_by_pseudonym": "FIXTURE-OWNER",
        "confirmation": (
            "I approve this exact protocol and frozen query pack for formal G-RW4 participation."
        ),
    }
    return _finish_digest(ProtocolApproval, payload, "approval_digest")


def _submission(
    participant_number: int,
    rating_rule: RatingRule,
    *,
    changed_repeats: bool = False,
    abstained_repeat_indexes: frozenset[int] = frozenset(),
    abstained_primary_candidates: frozenset[UUID] = frozenset(),
    schedule_mutation: ScheduleMutation | None = None,
) -> FormalStudySubmission:
    protocol = load_frozen_protocol()
    query_pack = load_frozen_query_pack()
    approval = _approval()
    participant_id = uuid5(_NAMESPACE, f"participant:{participant_number}")
    session_id = uuid5(_NAMESPACE, f"session:{participant_number}")
    base = approval.approved_at + timedelta(hours=participant_number)
    eligibility = _finish_digest(
        ParticipantEligibility,
        {
            "participant_id": participant_id,
            "participant_code_digest": participant_code_digest(f"FIXTURE-{participant_number:02d}"),
            "assessed_at": base,
            "years_experience": protocol.eligibility.minimum_years_experience,
            "experience_kinds": (ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
            "assessed_players_within_window": True,
            "conflict_declared": False,
            "eligible": True,
        },
        "eligibility_digest",
    )
    consent = _finish_digest(
        ConsentRecord,
        {
            "consent_id": uuid5(_NAMESPACE, f"consent:{participant_number}"),
            "participant_id": participant_id,
            "protocol_digest": protocol.protocol_digest,
            "query_pack_digest": query_pack.query_pack_digest,
            "consented_at": base + timedelta(minutes=1),
            "voluntary_participation": True,
            "local_pseudonymous_storage": True,
            "withdrawal_before_submission_understood": True,
            "immutable_after_submission_understood": True,
            "research_limitations_understood": True,
        },
        "consent_digest",
    )
    presentation_bundle = load_frozen_presentation()
    candidate_by_id: dict[UUID, FrozenCandidate] = {}
    for query in query_pack.queries:
        for candidate in query.candidates:
            candidate_by_id[candidate.candidate_id] = candidate
    schedule_digest = eligibility.participant_code_digest
    if schedule_mutation == "participant_substituted":
        schedule_digest = participant_code_digest(f"FIXTURE-{participant_number + 20:02d}")
    presentations = list(
        build_formal_candidate_presentations(
            presentation_bundle,
            session_id=session_id,
            participant_digest=schedule_digest,
        )
    )
    if schedule_mutation is not None and schedule_mutation != "participant_substituted":
        presentations = _mutated_schedule(presentations, schedule_mutation, participant_number)
    submitted_at = base + timedelta(minutes=20)
    session = StudySession(
        session_id=session_id,
        mode=StudyMode.FORMAL_G_RW4,
        participant_id=participant_id,
        protocol_digest=protocol.protocol_digest,
        query_pack_digest=query_pack.query_pack_digest,
        approval_digest=approval.approval_digest,
        eligibility_digest=eligibility.eligibility_digest,
        consent_digest=consent.consent_digest,
        started_at=base + timedelta(minutes=2),
        last_activity_at=base + timedelta(minutes=19),
        presentations=tuple(presentations),
        submitted_at=submitted_at,
    )
    judgements: list[CandidateJudgement] = []
    repeat_index = 0
    for presentation in presentations:
        primary_rating = rating_rule(candidate_by_id[presentation.candidate_id])
        rating = (
            4 - primary_rating
            if changed_repeats and presentation.kind is PresentationKind.REPEAT
            else primary_rating
        )
        abstained_repeat = (
            presentation.kind is PresentationKind.REPEAT
            and repeat_index in abstained_repeat_indexes
        )
        abstained_primary = (
            presentation.kind is PresentationKind.PRIMARY
            and presentation.candidate_id in abstained_primary_candidates
        )
        if presentation.kind is PresentationKind.REPEAT:
            repeat_index += 1
        state = (
            JudgementState.ABSTAIN
            if abstained_repeat or abstained_primary
            else JudgementState.RATED
        )
        judgement = _finish_digest(
            CandidateJudgement,
            {
                "judgement_id": uuid5(
                    _NAMESPACE,
                    f"judgement:{participant_number}:{presentation.presentation_ordinal}",
                ),
                "session_id": session_id,
                "participant_id": participant_id,
                "presentation_id": presentation.presentation_id,
                "query_id": presentation.query_id,
                "candidate_id": presentation.candidate_id,
                "state": state,
                "relevance_rating": rating if state is JudgementState.RATED else None,
                "confidence": 5 if state is JudgementState.RATED else None,
                "explanation": "synthetic implementation fixture only",
                "recorded_at": base + timedelta(minutes=3),
            },
            "judgement_digest",
        )
        judgements.append(judgement)
    return _finish_digest(
        FormalStudySubmission,
        {
            "submission_id": uuid5(_NAMESPACE, f"submission:{participant_number}"),
            "mode": StudyMode.FORMAL_G_RW4,
            "session_id": session_id,
            "participant_id": participant_id,
            "protocol_digest": protocol.protocol_digest,
            "query_pack_digest": query_pack.query_pack_digest,
            "approval_digest": approval.approval_digest,
            "w09_pins": protocol.w09_pins,
            "session": session,
            "eligibility": eligibility,
            "consent": consent,
            "submitted_at": submitted_at,
            "judgements": tuple(judgements),
        },
        "submission_digest",
    )


def _mutated_schedule(
    presentations: list[CandidatePresentation],
    mutation: ScheduleMutation,
    participant_number: int,
) -> list[CandidatePresentation]:
    primaries = [item for item in presentations if item.kind is PresentationKind.PRIMARY]
    repeats = [item for item in presentations if item.kind is PresentationKind.REPEAT]
    if mutation == "terminal":
        changed = [*primaries, *repeats]
    elif mutation == "reordered":
        changed = presentations.copy()
        changed[0], changed[1] = changed[1], changed[0]
    elif mutation == "adjacent":
        changed = [*primaries[:20], *repeats, *primaries[20:]]
    elif mutation == "under_delayed":
        target = repeats[0]
        changed = [item for item in presentations if item.presentation_id != target.presentation_id]
        anchor_index = next(
            index
            for index, item in enumerate(changed)
            if item.presentation_id == target.repeat_of_presentation_id
        )
        changed.insert(anchor_index + 1, target)
    elif mutation == "wrong_reference":
        changed = presentations.copy()
        index = changed.index(repeats[0])
        wrong_primary = next(
            item
            for item in primaries
            if item.presentation_id != repeats[0].repeat_of_presentation_id
        )
        changed[index] = repeats[0].model_copy(
            update={"repeat_of_presentation_id": wrong_primary.presentation_id}
        )
    elif mutation == "wrong_id":
        changed = presentations.copy()
        index = changed.index(repeats[0])
        changed[index] = repeats[0].model_copy(
            update={"presentation_id": uuid5(_NAMESPACE, f"wrong-id:{participant_number}")}
        )
    else:
        raise AssertionError(f"unsupported fixture schedule mutation: {mutation}")
    return [
        item.model_copy(update={"presentation_ordinal": ordinal})
        for ordinal, item in enumerate(changed, start=1)
    ]


def _evaluate(
    rating_rule: RatingRule,
    *,
    participant_count: int = 5,
    changed_repeats: bool = False,
):
    return evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        tuple(
            _submission(number, rating_rule, changed_repeats=changed_repeats)
            for number in range(participant_count)
        ),
        evaluated_at=_EVALUATED_AT,
    )


def _metrics(result) -> dict[str, float | None]:
    return {metric.metric_name: metric.value for metric in result.metrics}


def test_real_frozen_authorities_are_canonical_and_unicode_safe() -> None:
    raw = DEFAULT_PRESENTATION_PATH.read_bytes()
    decoded = cast(dict[str, Any], json.loads(raw))

    assert any(byte >= 0x80 for byte in raw)
    assert canonical_json_bytes(decoded) == raw
    assert load_frozen_protocol().protocol_digest.startswith("7420c3")
    assert load_frozen_query_pack().query_pack_digest.startswith("cf6796")
    presentation = load_frozen_presentation()
    assert presentation.presentation_digest.startswith("4ca84a")
    assert (
        presentation.repeat_anchor_candidate_ids
        == load_frozen_query_pack().repeat_anchor_candidate_ids
    )


def test_synthetic_protected_row_uses_json_contract_revalidation(tmp_path: Path) -> None:
    submission = _submission(1, lambda candidate: 4)
    envelope = canonical_json_bytes(
        {
            "schema_version": 1,
            "evidence_class": "FORMAL_G_RW4",
            "submissions": [submission.model_dump(mode="json")],
        }
    )
    protected = tmp_path / "synthetic-implementation-envelope.json"
    protected.write_bytes(envelope)

    loaded, digest = _load_protected_submissions(protected)

    assert loaded == (submission,)
    assert digest == hashlib.sha256(envelope).hexdigest()


def test_complete_synthetic_fixture_passes_with_exact_arithmetic() -> None:
    result = _evaluate(lambda candidate: 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0)
    metrics = _metrics(result)

    assert result.decision is ExpertGateDecisionKind.PASS
    assert result.rated_judgement_count == 400
    assert result.confidence_distribution == (0, 0, 0, 0, 400)
    assert metrics["retrieved_precision_at_5"] == 1.0
    assert metrics["mean_retrieved_ndcg_at_5"] == 1.0
    assert metrics["mean_control_ndcg_at_5"] == 0.0
    assert metrics["retrieved_control_relevant_rate_lift"] == 1.0
    assert metrics["paired_ndcg_delta"] == 1.0
    assert metrics["paired_ndcg_bootstrap_lower"] == 1.0
    assert metrics["mean_pairwise_ordinal_agreement"] == 1.0
    assert metrics["repeat_mean_absolute_difference"] == 0.0
    assert metrics["repeat_within_one_rate"] == 1.0


@pytest.mark.parametrize(
    "schedule_mutation",
    (
        "terminal",
        "reordered",
        "adjacent",
        "under_delayed",
        "wrong_id",
        "participant_substituted",
    ),
)
def test_substituted_formal_schedule_fails_integrity(
    schedule_mutation: ScheduleMutation,
) -> None:
    submissions = tuple(
        _submission(
            number,
            lambda candidate: 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0,
            schedule_mutation=schedule_mutation if number == 0 else None,
        )
        for number in range(5)
    )

    result = evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        submissions,
        evaluated_at=_EVALUATED_AT,
    )

    assert result.decision is ExpertGateDecisionKind.FAIL
    assert result.decision_reasons == (
        "INTEGRITY_FAILURE:formal participant-keyed presentation schedule mismatch",
    )


def test_wrong_repeat_reference_is_rejected_by_submission_contract() -> None:
    with pytest.raises(
        ValidationError,
        match="repeat presentation must preserve query and candidate identity",
    ):
        _submission(
            0,
            lambda candidate: 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0,
            schedule_mutation="wrong_reference",
        )


def test_complete_threshold_miss_is_fail_and_retained() -> None:
    result = _evaluate(lambda candidate: 4)
    metrics = _metrics(result)

    assert result.decision is ExpertGateDecisionKind.FAIL
    assert result.negative_result_retained is True
    assert metrics["mean_retrieved_ndcg_at_5"] == 1.0
    assert metrics["mean_control_ndcg_at_5"] == 1.0
    assert metrics["retrieved_control_relevant_rate_lift"] == 0.0
    assert all(metric.supported for metric in result.metrics)


def test_fully_rated_all_zero_pool_is_complete_negative_evidence() -> None:
    result = _evaluate(lambda candidate: 0)
    metrics = _metrics(result)

    assert result.decision is ExpertGateDecisionKind.FAIL
    assert metrics["mean_retrieved_ndcg_at_5"] == 0.0
    assert metrics["mean_control_ndcg_at_5"] == 0.0
    assert all(metric.supported for metric in result.metrics)


def test_incomplete_participant_and_candidate_denominators_are_insufficient() -> None:
    result = _evaluate(lambda candidate: 4, participant_count=1)

    assert result.decision is ExpertGateDecisionKind.INSUFFICIENT_EVIDENCE
    assert _metrics(result)["paired_ndcg_delta"] is None
    assert "INSUFFICIENT_ELIGIBLE_COMPLETED_PARTICIPANTS" in result.decision_reasons
    assert "INSUFFICIENT_CANDIDATE_RATING_COVERAGE" in result.decision_reasons


def test_repeats_change_only_consistency_metrics() -> None:
    def rule(candidate: FrozenCandidate) -> int:
        return 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0

    stable = _evaluate(rule)
    changed = _evaluate(rule, changed_repeats=True)
    stable_metrics = _metrics(stable)
    changed_metrics = _metrics(changed)

    for name in (
        "retrieved_precision_at_5",
        "mean_retrieved_ndcg_at_5",
        "mean_control_ndcg_at_5",
        "retrieved_control_relevant_rate_lift",
        "paired_ndcg_delta",
    ):
        assert changed_metrics[name] == stable_metrics[name]
    assert changed.rated_judgement_count == 400
    assert changed_metrics["repeat_mean_absolute_difference"] == 4.0
    assert changed_metrics["repeat_within_one_rate"] == 0.0
    assert changed.decision is ExpertGateDecisionKind.FAIL


def test_nine_of_ten_rated_repeat_pairs_remain_preregistered_evidence() -> None:
    def rule(candidate: FrozenCandidate) -> int:
        return 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0

    submissions = tuple(
        _submission(
            number,
            rule,
            abstained_repeat_indexes=frozenset({0}) if number == 0 else frozenset(),
        )
        for number in range(5)
    )

    result = evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        submissions,
        evaluated_at=_EVALUATED_AT,
    )

    assert result.decision is ExpertGateDecisionKind.PASS
    assert "INSUFFICIENT_RATED_REPEAT_PAIRS" not in result.decision_reasons
    assert _metrics(result)["repeat_within_one_rate"] == 1.0


def test_repeat_pair_rate_below_frozen_minimum_is_insufficient() -> None:
    def rule(candidate: FrozenCandidate) -> int:
        return 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0

    submissions = tuple(
        _submission(
            number,
            rule,
            abstained_repeat_indexes=(
                frozenset({0, 1}) if number == 0 else frozenset({0}) if number == 1 else frozenset()
            ),
        )
        for number in range(5)
    )

    result = evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        submissions,
        evaluated_at=_EVALUATED_AT,
    )

    assert result.decision is ExpertGateDecisionKind.INSUFFICIENT_EVIDENCE
    assert "INSUFFICIENT_RATED_REPEAT_PAIRS" in result.decision_reasons


def test_macro_precision_exposes_its_exact_fraction_under_variable_abstention() -> None:
    selected_candidate = next(
        candidate.candidate_id
        for query in load_frozen_query_pack().queries
        for candidate in query.candidates
        if candidate.origin is CandidateOrigin.RETRIEVED
    )
    submissions = tuple(
        _submission(
            number,
            lambda candidate, participant=number: (
                4 if candidate.origin is CandidateOrigin.RETRIEVED and participant < 3 else 0
            ),
            abstained_primary_candidates=(
                frozenset({selected_candidate}) if number == 4 else frozenset()
            ),
        )
        for number in range(5)
    )

    result = evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        submissions,
        evaluated_at=_EVALUATED_AT,
    )
    metric = next(item for item in result.metrics if item.metric_name == "retrieved_precision_at_5")

    assert metric.value == 0.60375
    assert (metric.numerator, metric.denominator) == (483, 800)
    assert metric.value == metric.numerator / metric.denominator


@pytest.mark.parametrize(
    ("retrieved_rating", "control_rating", "expected"),
    ((4, 0, Fraction(1, 1)), (4, 4, Fraction(0, 1)), (0, 4, Fraction(-1, 1))),
)
def test_rate_lift_exposes_exact_positive_zero_and_negative_two_arm_evidence(
    retrieved_rating: int,
    control_rating: int,
    expected: Fraction,
) -> None:
    result = _evaluate(
        lambda candidate: (
            retrieved_rating if candidate.origin is CandidateOrigin.RETRIEVED else control_rating
        )
    )
    metric = next(
        item
        for item in result.metrics
        if item.metric_name == "retrieved_control_relevant_rate_lift"
    )

    assert metric.value == float(expected)
    assert (metric.numerator, metric.denominator) == (expected.numerator, expected.denominator)
    assert metric.rate_contrast is not None
    evidence = metric.rate_contrast
    reconstructed = Fraction(
        evidence.retrieved_relevant_count,
        evidence.retrieved_rated_count,
    ) - Fraction(evidence.control_relevant_count, evidence.control_rated_count)
    assert reconstructed == expected
    assert evidence.retrieved_rate == (
        evidence.retrieved_relevant_count / evidence.retrieved_rated_count
    )
    assert evidence.control_rate == evidence.control_relevant_count / evidence.control_rated_count


def test_rate_lift_evidence_reconstructs_unequal_arm_denominators() -> None:
    retrieved_candidate = next(
        candidate.candidate_id
        for query in load_frozen_query_pack().queries
        for candidate in query.candidates
        if candidate.origin is CandidateOrigin.RETRIEVED
    )
    submissions = tuple(
        _submission(
            number,
            lambda candidate: 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0,
            abstained_primary_candidates=(
                frozenset({retrieved_candidate}) if number == 0 else frozenset()
            ),
        )
        for number in range(5)
    )

    result = evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        submissions,
        evaluated_at=_EVALUATED_AT,
    )
    metric = next(
        item
        for item in result.metrics
        if item.metric_name == "retrieved_control_relevant_rate_lift"
    )
    assert metric.rate_contrast is not None
    evidence = metric.rate_contrast
    assert evidence.retrieved_rated_count != evidence.control_rated_count
    exact = Fraction(
        evidence.retrieved_relevant_count,
        evidence.retrieved_rated_count,
    ) - Fraction(evidence.control_relevant_count, evidence.control_rated_count)
    assert metric.value == float(exact)
    assert (metric.numerator, metric.denominator) == (exact.numerator, exact.denominator)


def test_evaluation_cannot_precede_any_included_submission() -> None:
    def rule(candidate: FrozenCandidate) -> int:
        return 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0

    submissions = tuple(_submission(number, rule) for number in range(5))

    result = evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        submissions,
        evaluated_at=submissions[-1].submitted_at - timedelta(minutes=1),
    )

    assert result.decision is ExpertGateDecisionKind.FAIL
    assert result.decision_reasons == ("INTEGRITY_FAILURE:EVALUATION_PRECEDES_FORMAL_SUBMISSION",)


def test_duplicate_formal_submission_is_excluded_and_counted() -> None:
    submission = _submission(1, lambda candidate: 4)
    result = evaluate_expert_relevance(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        (submission, submission),
        evaluated_at=_EVALUATED_AT,
    )

    assert result.decision is ExpertGateDecisionKind.INSUFFICIENT_EVIDENCE
    assert result.excluded_submission_count == 1
    assert result.included_submission_digests == (submission.submission_digest,)


def test_stale_authority_is_rejected_before_metric_access() -> None:
    stale = load_frozen_query_pack().model_copy(update={"query_pack_digest": "0" * 64})

    with pytest.raises(ExpertRelevanceEvaluationError, match="query pack contract rejected"):
        evaluate_expert_relevance(
            load_frozen_protocol(),
            stale,
            load_frozen_presentation(),
            _approval(),
            (),
            evaluated_at=_EVALUATED_AT,
        )


def test_paired_bootstrap_is_seed_deterministic() -> None:
    first = paired_query_bootstrap((0.1, 0.2, 0.3, 0.4), seed=17, resamples=500, confidence=0.95)
    second = paired_query_bootstrap((0.1, 0.2, 0.3, 0.4), seed=17, resamples=500, confidence=0.95)

    assert first == second
    assert first[0] == pytest.approx(0.25)


def test_safe_report_is_deterministic_and_excludes_row_labels_and_free_text() -> None:
    result = _evaluate(lambda candidate: 4 if candidate.origin is CandidateOrigin.RETRIEVED else 0)
    first = render_safe_report(
        result, presentation_digest=load_frozen_presentation().presentation_digest
    )
    second = render_safe_report(
        result, presentation_digest=load_frozen_presentation().presentation_digest
    )

    assert first == second
    assert first.endswith(b"\n")
    assert b"synthetic implementation fixture only" not in first
    assert b'"explanation"' not in first
    assert b'"relevance_rating"' not in first

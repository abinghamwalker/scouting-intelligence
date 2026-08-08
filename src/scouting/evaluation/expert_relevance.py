"""Deterministic one-use W10 football-expert relevance evaluation.

The formal runner deliberately accepts a protected-input *path*, not already-opened
labels.  It claims the invocation before reading that path and emits only aggregate,
content-addressed evidence.  Participant explanations and row-level ratings never enter
the run, result, report, receipt, logs, or exceptions.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import stat
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any, cast
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import ValidationError

from scouting.contracts.expert_relevance import (
    CandidateJudgement,
    CandidateOrigin,
    ExpertGateDecisionKind,
    ExpertRelevanceProtocol,
    ExpertRelevanceStudyResult,
    ExpertStudyPresentationBundle,
    FormalStudySubmission,
    FrozenCandidate,
    FrozenExpertQuery,
    FrozenExpertQueryPack,
    JudgementState,
    MetricValue,
    PresentationKind,
    ProtocolApproval,
    QualitativeFailureCategory,
    RateContrastEvidence,
    StudyMode,
    SubgroupResult,
    build_formal_candidate_presentations,
)
from scouting.contracts.primitives import ContractModel
from scouting.contracts.research import canonical_research_digest
from scouting.storage.formats import canonical_json_bytes

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROTOCOL_PATH = PROJECT_ROOT / "configs/evaluation/w10-expert-relevance-protocol-v1.json"
DEFAULT_QUERY_PACK_PATH = PROJECT_ROOT / "configs/evaluation/w10-frozen-query-pack-v1.json"
DEFAULT_PRESENTATION_PATH = (
    PROJECT_ROOT / "configs/evaluation/w10-expert-study-presentation-v1.json"
)
FORMAL_EVALUATION_AUTHORITY_ROOT = PROJECT_ROOT / "data/working/w10/formal-evaluation-authority"

FROZEN_PROTOCOL_DIGEST = "7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f"
FROZEN_QUERY_PACK_DIGEST = "cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5"
FROZEN_PRESENTATION_DIGEST = "4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96"

CLAIM_FILENAME = "formal-evaluation-claim.json"
RUN_FILENAME = "formal-evaluation-run.json"
RESULT_FILENAME = "formal-evaluation-result.json"
REPORT_FILENAME = "formal-evaluation-report.json"
RECEIPT_FILENAME = "formal-evaluation-receipt.json"

_METRIC_NAMES = (
    "participant_completion_rate",
    "candidate_rating_coverage_rate",
    "query_coverage_rate",
    "retrieved_precision_at_5",
    "mean_retrieved_ndcg_at_5",
    "mean_control_ndcg_at_5",
    "retrieved_relevant_rate",
    "control_relevant_rate",
    "retrieved_control_relevant_rate_lift",
    "paired_ndcg_delta",
    "paired_ndcg_bootstrap_lower",
    "paired_ndcg_bootstrap_upper",
    "mean_pairwise_ordinal_agreement",
    "repeat_mean_absolute_difference",
    "repeat_within_one_rate",
)


class ExpertRelevanceEvaluationError(ValueError):
    """A frozen authority, protected input, or evaluation invariant failed closed."""


@dataclass(frozen=True, slots=True)
class FormalEvaluationArtifacts:
    """Paths and identities from one successfully retained formal invocation."""

    result: ExpertRelevanceStudyResult
    claim_path: Path
    run_path: Path
    result_path: Path
    report_path: Path
    receipt_path: Path
    authority_claim_path: Path
    authority_receipt_path: Path
    receipt_digest: str


@dataclass(frozen=True, slots=True)
class _CandidateAggregate:
    query: FrozenExpertQuery
    candidate: FrozenCandidate
    ratings: tuple[int, ...]
    relevant_count: int

    @property
    def mean_gain(self) -> float | None:
        if not self.ratings:
            return None
        return _clean_float(math.fsum(self.ratings) / len(self.ratings))

    @property
    def relevance_rate(self) -> float | None:
        if not self.ratings:
            return None
        return _clean_float(self.relevant_count / len(self.ratings))


@dataclass(frozen=True, slots=True)
class _QueryMeasures:
    query: FrozenExpertQuery
    retrieved_ndcg: float
    control_ndcg: float
    retrieved_precision: float

    @property
    def delta(self) -> float:
        return _clean_float(self.retrieved_ndcg - self.control_ndcg)


def _clean_float(value: float) -> float:
    if not math.isfinite(value):
        raise ExpertRelevanceEvaluationError("non-finite aggregate evaluation value")
    return 0.0 if value == 0.0 else value


def _canonical_bytes(value: object) -> bytes:
    return canonical_json_bytes(value)


def _fresh[T: ContractModel](value: T, model: type[T], *, label: str) -> T:
    if type(value) is not model:
        raise ExpertRelevanceEvaluationError(f"{label} must use the exact contract type")
    try:
        return model.model_validate(value.model_dump(mode="python"))
    except ValidationError as exc:
        raise ExpertRelevanceEvaluationError(f"{label} contract rejected") from exc


def _safe_canonical_json(path: Path) -> tuple[dict[str, Any], bytes]:
    absolute = path.absolute()
    for ancestor in (absolute, *absolute.parents):
        if not ancestor.exists():
            continue
        if ancestor.is_symlink() or ancestor.resolve(strict=True) != ancestor:
            raise ExpertRelevanceEvaluationError("evaluation input has an unsafe ancestor")
    if absolute.is_symlink() or not absolute.is_file():
        raise ExpertRelevanceEvaluationError("evaluation input is absent or unsafe")
    try:
        metadata = absolute.lstat()
        raw = absolute.read_bytes()
    except OSError as exc:
        raise ExpertRelevanceEvaluationError("evaluation input cannot be inspected") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise ExpertRelevanceEvaluationError("evaluation input must be a regular file")
    try:
        decoded = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExpertRelevanceEvaluationError("evaluation input is not strict JSON") from exc
    if type(decoded) is not dict or _canonical_bytes(decoded) != raw:
        raise ExpertRelevanceEvaluationError("evaluation input must be one canonical JSON object")
    return cast(dict[str, Any], decoded), raw


def _load_contract[T: ContractModel](path: Path, model: type[T], *, label: str) -> T:
    _, raw = _safe_canonical_json(path)
    try:
        return model.model_validate_json(raw)
    except ValidationError as exc:
        raise ExpertRelevanceEvaluationError(f"{label} contract rejected") from exc


def load_frozen_protocol(path: Path = DEFAULT_PROTOCOL_PATH) -> ExpertRelevanceProtocol:
    protocol = _load_contract(path, ExpertRelevanceProtocol, label="frozen protocol")
    if protocol.protocol_digest != FROZEN_PROTOCOL_DIGEST:
        raise ExpertRelevanceEvaluationError("frozen protocol digest is stale or substituted")
    return protocol


def load_frozen_query_pack(path: Path = DEFAULT_QUERY_PACK_PATH) -> FrozenExpertQueryPack:
    query_pack = _load_contract(path, FrozenExpertQueryPack, label="frozen query pack")
    if query_pack.query_pack_digest != FROZEN_QUERY_PACK_DIGEST:
        raise ExpertRelevanceEvaluationError("frozen query-pack digest is stale or substituted")
    return query_pack


def load_frozen_presentation(
    path: Path = DEFAULT_PRESENTATION_PATH,
) -> ExpertStudyPresentationBundle:
    presentation = _load_contract(path, ExpertStudyPresentationBundle, label="frozen presentation")
    if presentation.presentation_digest != FROZEN_PRESENTATION_DIGEST:
        raise ExpertRelevanceEvaluationError("frozen presentation digest is stale or substituted")
    return presentation


def load_protocol_approval(path: Path) -> ProtocolApproval:
    return _load_contract(path, ProtocolApproval, label="protocol approval")


def _assert_authority(
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
    presentation: ExpertStudyPresentationBundle,
    approval: ProtocolApproval | None,
) -> tuple[
    ExpertRelevanceProtocol,
    FrozenExpertQueryPack,
    ExpertStudyPresentationBundle,
    ProtocolApproval | None,
]:
    active_protocol = _fresh(protocol, ExpertRelevanceProtocol, label="protocol")
    active_pack = _fresh(query_pack, FrozenExpertQueryPack, label="query pack")
    active_presentation = _fresh(presentation, ExpertStudyPresentationBundle, label="presentation")
    if active_protocol.protocol_digest != FROZEN_PROTOCOL_DIGEST:
        raise ExpertRelevanceEvaluationError("protocol does not equal frozen W10 authority")
    if active_pack.query_pack_digest != FROZEN_QUERY_PACK_DIGEST:
        raise ExpertRelevanceEvaluationError("query pack does not equal frozen W10 authority")
    if active_presentation.presentation_digest != FROZEN_PRESENTATION_DIGEST:
        raise ExpertRelevanceEvaluationError("presentation does not equal frozen W10 authority")
    if active_protocol.w09_pins != active_pack.w09_pins:
        raise ExpertRelevanceEvaluationError("protocol and query-pack W09 pins disagree")
    if (
        active_presentation.protocol_digest != active_protocol.protocol_digest
        or active_presentation.query_pack_digest != active_pack.query_pack_digest
    ):
        raise ExpertRelevanceEvaluationError("presentation authority does not bind protocol/pack")
    _assert_presentation_projection(active_pack, active_presentation)
    for query in active_pack.queries:
        if query.w09_generated_at < active_pack.built_at:
            raise ExpertRelevanceEvaluationError("query W09 result predates frozen pack authority")
    active_approval: ProtocolApproval | None = None
    if approval is not None:
        active_approval = _fresh(approval, ProtocolApproval, label="approval")
        if (
            active_approval.protocol_digest != active_protocol.protocol_digest
            or active_approval.query_pack_digest != active_pack.query_pack_digest
            or active_approval.protocol_version != active_protocol.protocol_version
            or active_approval.query_pack_version != active_pack.query_pack_version
            or active_approval.approved_at < active_pack.built_at
        ):
            raise ExpertRelevanceEvaluationError("approval does not bind final frozen authority")
    return active_protocol, active_pack, active_presentation, active_approval


def _assert_presentation_projection(
    query_pack: FrozenExpertQueryPack,
    presentation: ExpertStudyPresentationBundle,
) -> None:
    if presentation.repeat_anchor_candidate_ids != query_pack.repeat_anchor_candidate_ids:
        raise ExpertRelevanceEvaluationError("presentation repeat-anchor roster substitution")
    frozen_queries = {query.query_id: query for query in query_pack.queries}
    presented_queries = {query.query_id: query for query in presentation.queries}
    if set(frozen_queries) != set(presented_queries):
        raise ExpertRelevanceEvaluationError("presentation query roster substitution")
    for query_id, shown in presented_queries.items():
        frozen = frozen_queries[query_id]
        if (
            shown.query_code != frozen.query_code
            or shown.exemplar_display_name != frozen.exemplar_display_name
            or shown.exemplar_competition_name != frozen.exemplar_competition_name
            or shown.exemplar_position_code != frozen.exemplar_position_code
            or shown.exemplar_team_names != frozen.exemplar_team_names
            or shown.exemplar_minutes != frozen.exemplar_minutes
            or shown.football_prompt != frozen.football_prompt
        ):
            raise ExpertRelevanceEvaluationError("presentation exemplar projection substitution")
        frozen_candidates = {candidate.candidate_id: candidate for candidate in frozen.candidates}
        shown_candidates = {candidate.candidate_id: candidate for candidate in shown.candidates}
        if set(frozen_candidates) != set(shown_candidates):
            raise ExpertRelevanceEvaluationError("presentation candidate roster substitution")
        for candidate_id, candidate in shown_candidates.items():
            source = frozen_candidates[candidate_id]
            if (
                candidate.display_name != source.display_name
                or candidate.competition_name != source.competition_name
                or candidate.position_code != source.position_code
                or candidate.team_names != source.team_names
                or candidate.minutes != source.minutes
            ):
                raise ExpertRelevanceEvaluationError(
                    "presentation candidate projection substitution"
                )


def absent_formal_evidence_status(
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
    presentation: ExpertStudyPresentationBundle,
    approval: ProtocolApproval | None = None,
) -> dict[str, object]:
    """Return evidence-honest status without accepting a protected-input argument.

    This route is pure: it writes no claim, run, result, report, or receipt artifact.
    """

    active_protocol, active_pack, active_presentation, active_approval = _assert_authority(
        protocol, query_pack, presentation, approval
    )
    reason = "FORMAL_APPROVAL_ABSENT" if active_approval is None else "FORMAL_EVIDENCE_ABSENT"
    return {
        "schema_version": 1,
        "decision": ExpertGateDecisionKind.INSUFFICIENT_EVIDENCE.value,
        "decision_reasons": [reason],
        "protocol_digest": active_protocol.protocol_digest,
        "query_pack_digest": active_pack.query_pack_digest,
        "presentation_digest": active_presentation.presentation_digest,
        "approval_digest": (
            active_approval.approval_digest if active_approval is not None else None
        ),
        "protected_input_accepted": False,
        "run_artifact_created": False,
        "result_artifact_created": False,
    }


def _assert_submission(
    submission: FormalStudySubmission,
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
    presentation: ExpertStudyPresentationBundle,
    approval: ProtocolApproval,
) -> FormalStudySubmission:
    value = _fresh(submission, FormalStudySubmission, label="formal submission")
    if (
        value.mode is not StudyMode.FORMAL_G_RW4
        or value.protocol_digest != protocol.protocol_digest
        or value.query_pack_digest != query_pack.query_pack_digest
        or value.approval_digest != approval.approval_digest
        or value.w09_pins != protocol.w09_pins
    ):
        raise ExpertRelevanceEvaluationError("formal submission authority substitution")
    eligibility = value.eligibility
    accepted_experience = bool(
        set(eligibility.experience_kinds) & set(protocol.eligibility.accepted_experience)
    )
    expected_eligible = (
        eligibility.years_experience >= protocol.eligibility.minimum_years_experience
        and accepted_experience
        and (
            eligibility.assessed_players_within_window
            if protocol.eligibility.requires_recent_player_assessment
            else True
        )
        and not eligibility.conflict_declared
    )
    if not expected_eligible or not eligibility.eligible:
        raise ExpertRelevanceEvaluationError("formal eligibility does not satisfy protocol")
    if (
        approval.approved_at > value.consent.consented_at
        or eligibility.assessed_at > value.session.started_at
        or value.consent.consented_at > value.session.started_at
    ):
        raise ExpertRelevanceEvaluationError("approval/eligibility/consent chronology invalid")
    if any(
        judgement.recorded_at < value.session.started_at
        or judgement.recorded_at > value.submitted_at
        for judgement in value.judgements
    ):
        raise ExpertRelevanceEvaluationError("judgement chronology invalid")
    _assert_submission_presentations(value, query_pack, presentation)
    return value


def _assert_submission_presentations(
    submission: FormalStudySubmission,
    query_pack: FrozenExpertQueryPack,
    presentation: ExpertStudyPresentationBundle,
) -> None:
    expected_primary = {
        (query.query_id, candidate.candidate_id)
        for query in query_pack.queries
        for candidate in query.candidates
    }
    primaries = tuple(
        presentation
        for presentation in submission.session.presentations
        if presentation.kind is PresentationKind.PRIMARY
    )
    actual_primary = {(item.query_id, item.candidate_id) for item in primaries}
    if len(actual_primary) != len(primaries) or actual_primary != expected_primary:
        raise ExpertRelevanceEvaluationError("formal primary presentation roster substitution")
    repeats = tuple(
        presentation
        for presentation in submission.session.presentations
        if presentation.kind is PresentationKind.REPEAT
    )
    if {item.candidate_id for item in repeats} != set(query_pack.repeat_anchor_candidate_ids):
        raise ExpertRelevanceEvaluationError("formal repeat anchor substitution")
    try:
        expected_schedule = build_formal_candidate_presentations(
            presentation,
            session_id=submission.session_id,
            participant_digest=submission.eligibility.participant_code_digest,
        )
    except ValueError as exc:
        raise ExpertRelevanceEvaluationError(
            "frozen formal presentation schedule cannot be constructed"
        ) from exc
    if submission.session.presentations != expected_schedule:
        raise ExpertRelevanceEvaluationError(
            "formal participant-keyed presentation schedule mismatch"
        )


def _metric(
    name: str,
    value: float | None,
    *,
    numerator: int,
    denominator: int,
    limitation: str | None = None,
    rate_contrast: RateContrastEvidence | None = None,
) -> MetricValue:
    return MetricValue(
        metric_name=name,
        value=_clean_float(value) if value is not None else None,
        numerator=numerator,
        denominator=denominator,
        supported=value is not None,
        limitation=limitation if value is None else None,
        rate_contrast=rate_contrast,
    )


def _unsupported_metrics(reason: str) -> tuple[MetricValue, ...]:
    return tuple(
        _metric(name, None, numerator=0, denominator=0, limitation=reason) for name in _METRIC_NAMES
    )


def _dcg(gains: Sequence[float]) -> float:
    return _clean_float(math.fsum(gain / math.log2(index + 2) for index, gain in enumerate(gains)))


def _query_measures(
    query: FrozenExpertQuery,
    aggregates: Mapping[UUID, _CandidateAggregate],
) -> _QueryMeasures:
    candidates = tuple(aggregates[candidate.candidate_id] for candidate in query.candidates)
    if any(item.mean_gain is None or item.relevance_rate is None for item in candidates):
        raise ExpertRelevanceEvaluationError("query metric denominator is incomplete")
    retrieved = tuple(
        sorted(
            (item for item in candidates if item.candidate.origin is CandidateOrigin.RETRIEVED),
            key=lambda item: cast(int, item.candidate.retrieval_rank),
        )
    )
    controls = tuple(
        sorted(
            (item for item in candidates if item.candidate.origin is CandidateOrigin.CONTROL),
            key=lambda item: cast(int, item.candidate.control_rank),
        )
    )
    retrieved_gains = tuple(cast(float, item.mean_gain) for item in retrieved)
    control_gains = tuple(cast(float, item.mean_gain) for item in controls)
    ideal = _dcg(tuple(sorted((*retrieved_gains, *control_gains), reverse=True)[:5]))
    # The frozen W10 clarification makes a fully rated all-zero pool complete negative
    # evidence: both arms receive NDCG 0.0, never an invented unsupported denominator.
    retrieved_ndcg = 0.0 if ideal == 0.0 else _clean_float(_dcg(retrieved_gains) / ideal)
    control_ndcg = 0.0 if ideal == 0.0 else _clean_float(_dcg(control_gains) / ideal)
    precision = _clean_float(
        math.fsum(cast(float, item.relevance_rate) for item in retrieved) / len(retrieved)
    )
    return _QueryMeasures(query, retrieved_ndcg, control_ndcg, precision)


def paired_query_bootstrap(
    deltas: Sequence[float],
    *,
    seed: int,
    resamples: int,
    confidence: float,
) -> tuple[float, float, float]:
    """Return point, lower, and upper paired percentile query-bootstrap values."""

    values = tuple(_clean_float(value) for value in deltas)
    if not values:
        raise ExpertRelevanceEvaluationError("paired bootstrap requires query deltas")
    point = _clean_float(math.fsum(values) / len(values))
    # Deliberately reproducible statistical resampling; no security token is generated.
    rng = random.Random(seed)  # nosec B311
    samples = sorted(
        _clean_float(math.fsum(values[rng.randrange(len(values))] for _ in values) / len(values))
        for _ in range(resamples)
    )
    alpha = (1.0 - confidence) / 2.0
    lower = samples[int(math.floor(alpha * (len(samples) - 1)))]
    upper = samples[int(math.ceil((1.0 - alpha) * (len(samples) - 1)))]
    return point, _clean_float(lower), _clean_float(upper)


def _participant_primary_judgements(
    submission: FormalStudySubmission,
) -> tuple[CandidateJudgement, ...]:
    presentations = {item.presentation_id: item for item in submission.session.presentations}
    return tuple(
        judgement
        for judgement in submission.judgements
        if presentations[judgement.presentation_id].kind is PresentationKind.PRIMARY
    )


def _repeat_differences(submissions: Sequence[FormalStudySubmission]) -> tuple[int, ...]:
    differences: list[int] = []
    for submission in submissions:
        judgements = {item.presentation_id: item for item in submission.judgements}
        for presentation in submission.session.presentations:
            if presentation.kind is not PresentationKind.REPEAT:
                continue
            reference = presentation.repeat_of_presentation_id
            if reference is None:
                raise ExpertRelevanceEvaluationError("repeat presentation lost primary identity")
            primary = judgements[reference]
            repeated = judgements[presentation.presentation_id]
            if (
                primary.state is JudgementState.RATED
                and repeated.state is JudgementState.RATED
                and primary.relevance_rating is not None
                and repeated.relevance_rating is not None
            ):
                differences.append(abs(primary.relevance_rating - repeated.relevance_rating))
    return tuple(differences)


def _candidate_aggregates(
    query_pack: FrozenExpertQueryPack,
    submissions: Sequence[FormalStudySubmission],
    relevant_floor: int,
) -> dict[UUID, _CandidateAggregate]:
    query_by_candidate = {
        candidate.candidate_id: query
        for query in query_pack.queries
        for candidate in query.candidates
    }
    candidate_by_id = {
        candidate.candidate_id: candidate
        for query in query_pack.queries
        for candidate in query.candidates
    }
    ratings: dict[UUID, list[int]] = defaultdict(list)
    relevant: dict[UUID, int] = defaultdict(int)
    for submission in submissions:
        for judgement in _participant_primary_judgements(submission):
            if judgement.state is not JudgementState.RATED:
                continue
            rating = judgement.relevance_rating
            if rating is None:
                raise ExpertRelevanceEvaluationError("rated judgement lost its rating")
            ratings[judgement.candidate_id].append(rating)
            relevant[judgement.candidate_id] += rating >= relevant_floor
    return {
        candidate_id: _CandidateAggregate(
            query_by_candidate[candidate_id],
            candidate,
            tuple(ratings[candidate_id]),
            relevant[candidate_id],
        )
        for candidate_id, candidate in candidate_by_id.items()
    }


def _ordinal_agreement(aggregates: Mapping[UUID, _CandidateAggregate]) -> tuple[float, int]:
    values = tuple(
        1.0 - abs(left - right) / 4.0
        for aggregate in aggregates.values()
        for left, right in combinations(aggregate.ratings, 2)
    )
    if not values:
        raise ExpertRelevanceEvaluationError("ordinal agreement has no rating pairs")
    return _clean_float(math.fsum(values) / len(values)), len(values)


def _subgroups(
    queries: Sequence[FrozenExpertQuery],
    submissions: Sequence[FormalStudySubmission],
    aggregates: Mapping[UUID, _CandidateAggregate],
    measures: Mapping[UUID, _QueryMeasures],
    *,
    dimension: str,
    value_of: Callable[[FrozenExpertQuery], str],
) -> tuple[SubgroupResult, ...]:
    grouped: dict[str, list[FrozenExpertQuery]] = defaultdict(list)
    for query in queries:
        grouped[value_of(query)].append(query)
    output: list[SubgroupResult] = []
    for value in sorted(grouped):
        selected = tuple(grouped[value])
        candidate_ids = {
            candidate.candidate_id for query in selected for candidate in query.candidates
        }
        selected_aggregates = tuple(aggregates[candidate_id] for candidate_id in candidate_ids)
        rated = sum(len(item.ratings) for item in selected_aggregates)
        relevant = sum(item.relevant_count for item in selected_aggregates)
        precision = _clean_float(
            math.fsum(measures[query.query_id].retrieved_precision for query in selected)
            / len(selected)
        )
        mean_ndcg = _clean_float(
            math.fsum(measures[query.query_id].retrieved_ndcg for query in selected) / len(selected)
        )
        participant_count = sum(
            bool(
                candidate_ids
                & {
                    judgement.candidate_id
                    for judgement in _participant_primary_judgements(submission)
                    if judgement.state is JudgementState.RATED
                }
            )
            for submission in submissions
        )
        output.append(
            SubgroupResult(
                dimension=dimension,
                value=value,
                participant_count=participant_count,
                query_count=len(selected),
                rated_judgement_count=rated,
                relevant_judgement_count=relevant,
                retrieved_precision_at_k=precision,
                mean_ndcg_at_k=mean_ndcg,
            )
        )
    return tuple(output)


def _make_result(
    *,
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
    approval_digest: str | None,
    evaluated_at: datetime,
    included_submission_digests: tuple[str, ...],
    excluded_submission_count: int,
    eligible_participant_count: int,
    completed_participant_count: int,
    rated_judgement_count: int,
    abstention_count: int,
    unable_to_assess_count: int,
    missing_judgement_count: int,
    metrics: tuple[MetricValue, ...],
    position_subgroups: tuple[SubgroupResult, ...],
    competition_subgroups: tuple[SubgroupResult, ...],
    confidence_distribution: tuple[int, int, int, int, int],
    qualitative_failure_categories: dict[QualitativeFailureCategory, int],
    decision: ExpertGateDecisionKind,
    reasons: tuple[str, ...],
) -> ExpertRelevanceStudyResult:
    identity = {
        "protocol_digest": protocol.protocol_digest,
        "query_pack_digest": query_pack.query_pack_digest,
        "approval_digest": approval_digest,
        "evaluated_at": evaluated_at.isoformat(),
        "submissions": included_submission_digests,
        "decision": decision.value,
        "reasons": reasons,
    }
    result_id = uuid5(NAMESPACE_URL, f"w10-expert-relevance:{canonical_research_digest(identity)}")
    payload: dict[str, Any] = {
        "result_id": result_id,
        "protocol_digest": protocol.protocol_digest,
        "query_pack_digest": query_pack.query_pack_digest,
        "approval_digest": approval_digest,
        "evaluated_at": evaluated_at,
        "included_submission_digests": included_submission_digests,
        "excluded_submission_count": excluded_submission_count,
        "eligible_participant_count": eligible_participant_count,
        "completed_participant_count": completed_participant_count,
        "query_count": len(query_pack.queries),
        "candidate_count": sum(len(query.candidates) for query in query_pack.queries),
        "rated_judgement_count": rated_judgement_count,
        "abstention_count": abstention_count,
        "unable_to_assess_count": unable_to_assess_count,
        "missing_judgement_count": missing_judgement_count,
        "metrics": metrics,
        "position_subgroups": position_subgroups,
        "competition_subgroups": competition_subgroups,
        "confidence_distribution": confidence_distribution,
        "qualitative_failure_categories": qualitative_failure_categories,
        "decision": decision,
        "decision_reasons": reasons,
        "negative_result_retained": True,
    }
    draft = ExpertRelevanceStudyResult.model_construct(**payload, result_digest="0" * 64)
    payload["result_digest"] = canonical_research_digest(draft.digest_projection())
    return ExpertRelevanceStudyResult(**payload)


def _integrity_failure_result(
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
    approval_digest: str | None,
    evaluated_at: datetime,
    *,
    reason: str,
    excluded_submission_count: int,
) -> ExpertRelevanceStudyResult:
    return _make_result(
        protocol=protocol,
        query_pack=query_pack,
        approval_digest=approval_digest,
        evaluated_at=evaluated_at,
        included_submission_digests=(),
        excluded_submission_count=excluded_submission_count,
        eligible_participant_count=0,
        completed_participant_count=0,
        rated_judgement_count=0,
        abstention_count=0,
        unable_to_assess_count=0,
        missing_judgement_count=0,
        metrics=_unsupported_metrics("integrity failure prevented metric access"),
        position_subgroups=(),
        competition_subgroups=(),
        confidence_distribution=(0, 0, 0, 0, 0),
        qualitative_failure_categories={category: 0 for category in QualitativeFailureCategory},
        decision=ExpertGateDecisionKind.FAIL,
        reasons=(f"INTEGRITY_FAILURE:{reason}",),
    )


def evaluate_expert_relevance(
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
    presentation: ExpertStudyPresentationBundle,
    approval: ProtocolApproval,
    submissions: Sequence[FormalStudySubmission],
    *,
    evaluated_at: datetime,
) -> ExpertRelevanceStudyResult:
    """Evaluate exact formal submissions without persisting or exposing row labels."""

    active_protocol, active_pack, active_presentation, active_approval = _assert_authority(
        protocol, query_pack, presentation, approval
    )
    if active_approval is None:
        raise ExpertRelevanceEvaluationError("formal evaluation requires approval")
    if type(evaluated_at) is not datetime or evaluated_at.utcoffset() != timedelta(0):
        raise ExpertRelevanceEvaluationError("evaluation datetime must be an exact UTC datetime")
    if evaluated_at < active_approval.approved_at:
        return _integrity_failure_result(
            active_protocol,
            active_pack,
            active_approval.approval_digest,
            evaluated_at,
            reason="EVALUATION_PRECEDES_PROTOCOL_APPROVAL",
            excluded_submission_count=len(submissions),
        )
    ordered_inputs = tuple(submissions)
    try:
        validated = tuple(
            sorted(
                (
                    _assert_submission(
                        item,
                        active_protocol,
                        active_pack,
                        active_presentation,
                        active_approval,
                    )
                    for item in ordered_inputs
                ),
                key=lambda item: (item.participant_id.bytes, item.submission_digest),
            )
        )
    except ExpertRelevanceEvaluationError as exc:
        return _integrity_failure_result(
            active_protocol,
            active_pack,
            active_approval.approval_digest,
            evaluated_at,
            reason=str(exc),
            excluded_submission_count=len(ordered_inputs),
        )
    if any(item.submitted_at > evaluated_at for item in validated):
        return _integrity_failure_result(
            active_protocol,
            active_pack,
            active_approval.approval_digest,
            evaluated_at,
            reason="EVALUATION_PRECEDES_FORMAL_SUBMISSION",
            excluded_submission_count=len(ordered_inputs),
        )
    included_list: list[FormalStudySubmission] = []
    seen_participants: set[UUID] = set()
    seen_submissions: set[str] = set()
    excluded_submission_count = 0
    for submission in validated:
        if (
            submission.participant_id in seen_participants
            or submission.submission_digest in seen_submissions
        ):
            excluded_submission_count += 1
            continue
        seen_participants.add(submission.participant_id)
        seen_submissions.add(submission.submission_digest)
        included_list.append(submission)
    included = tuple(included_list)
    submission_digests = tuple(item.submission_digest for item in included)

    primary = tuple(
        judgement
        for submission in included
        for judgement in _participant_primary_judgements(submission)
    )
    rated = tuple(item for item in primary if item.state is JudgementState.RATED)
    abstentions = sum(item.state is JudgementState.ABSTAIN for item in primary)
    unable = sum(item.state is JudgementState.UNABLE_TO_ASSESS for item in primary)
    expected_primary = len(included) * 80
    missing = max(0, expected_primary - len(primary))
    confidence = tuple(sum(item.confidence == value for item in rated) for value in range(1, 6))
    confidence_distribution = cast(tuple[int, int, int, int, int], confidence)
    failure_counts = {
        category: sum(item.failure_category is category for item in primary)
        for category in QualitativeFailureCategory
    }
    participant_count = len(included)
    completion_rate = 1.0 if participant_count else None
    aggregates = _candidate_aggregates(
        active_pack,
        included,
        active_protocol.thresholds.relevant_rating_floor,
    )
    minimum_raters = active_protocol.completion.minimum_non_abstaining_raters_per_candidate
    covered_candidates = sum(len(item.ratings) >= minimum_raters for item in aggregates.values())
    total_candidates = len(aggregates)
    query_coverage = {
        query.query_id: all(
            len(aggregates[candidate.candidate_id].ratings) >= minimum_raters
            for candidate in query.candidates
        )
        for query in active_pack.queries
    }
    covered_queries = sum(query_coverage.values())
    coverage_metrics = (
        _metric(
            "participant_completion_rate",
            completion_rate,
            numerator=participant_count,
            denominator=participant_count,
            limitation="no eligible completed participant denominator",
        ),
        _metric(
            "candidate_rating_coverage_rate",
            covered_candidates / total_candidates,
            numerator=covered_candidates,
            denominator=total_candidates,
        ),
        _metric(
            "query_coverage_rate",
            covered_queries / len(active_pack.queries),
            numerator=covered_queries,
            denominator=len(active_pack.queries),
        ),
    )
    insufficient_reasons: list[str] = []
    if participant_count < active_protocol.completion.minimum_eligible_participants:
        insufficient_reasons.append("INSUFFICIENT_ELIGIBLE_COMPLETED_PARTICIPANTS")
    if (
        completion_rate is None
        or completion_rate < active_protocol.completion.minimum_participant_completion_rate
    ):
        insufficient_reasons.append("INSUFFICIENT_PARTICIPANT_COMPLETION")
    if covered_candidates != total_candidates:
        insufficient_reasons.append("INSUFFICIENT_CANDIDATE_RATING_COVERAGE")
    if (
        covered_queries / len(active_pack.queries)
        < active_protocol.completion.minimum_query_coverage_rate
    ):
        insufficient_reasons.append("INSUFFICIENT_QUERY_COVERAGE")
    repeat_differences = _repeat_differences(included)
    expected_repeat_pairs = (
        participant_count * active_protocol.completion.repeated_judgements_per_participant
    )
    rated_repeat_pair_rate = (
        len(repeat_differences) / expected_repeat_pairs if expected_repeat_pairs else 0.0
    )
    if rated_repeat_pair_rate < active_protocol.completion.minimum_rated_repeat_pair_rate:
        insufficient_reasons.append("INSUFFICIENT_RATED_REPEAT_PAIRS")

    if insufficient_reasons:
        remaining = tuple(
            _metric(
                name,
                None,
                numerator=0,
                denominator=0,
                limitation="required formal denominator is incomplete",
            )
            for name in _METRIC_NAMES[len(coverage_metrics) :]
        )
        return _make_result(
            protocol=active_protocol,
            query_pack=active_pack,
            approval_digest=active_approval.approval_digest,
            evaluated_at=evaluated_at,
            included_submission_digests=submission_digests,
            excluded_submission_count=excluded_submission_count,
            eligible_participant_count=participant_count,
            completed_participant_count=participant_count,
            rated_judgement_count=len(rated),
            abstention_count=abstentions,
            unable_to_assess_count=unable,
            missing_judgement_count=missing,
            metrics=coverage_metrics + remaining,
            position_subgroups=(),
            competition_subgroups=(),
            confidence_distribution=confidence_distribution,
            qualitative_failure_categories=failure_counts,
            decision=ExpertGateDecisionKind.INSUFFICIENT_EVIDENCE,
            reasons=tuple(sorted(set(insufficient_reasons))),
        )

    query_measures = tuple(_query_measures(query, aggregates) for query in active_pack.queries)
    measures_by_query = {item.query.query_id: item for item in query_measures}
    retrieved_aggregates = tuple(
        item for item in aggregates.values() if item.candidate.origin is CandidateOrigin.RETRIEVED
    )
    control_aggregates = tuple(
        item for item in aggregates.values() if item.candidate.origin is CandidateOrigin.CONTROL
    )
    retrieved_precision_fraction = sum(
        (Fraction(item.relevant_count, len(item.ratings)) for item in retrieved_aggregates),
        start=Fraction(0, 1),
    ) / len(retrieved_aggregates)
    retrieved_precision = _clean_float(float(retrieved_precision_fraction))
    retrieved_ndcg = _clean_float(
        math.fsum(item.retrieved_ndcg for item in query_measures) / len(query_measures)
    )
    control_ndcg = _clean_float(
        math.fsum(item.control_ndcg for item in query_measures) / len(query_measures)
    )
    retrieved_relevant = sum(item.relevant_count for item in retrieved_aggregates)
    retrieved_rated = sum(len(item.ratings) for item in retrieved_aggregates)
    control_relevant = sum(item.relevant_count for item in control_aggregates)
    control_rated = sum(len(item.ratings) for item in control_aggregates)
    retrieved_rate_fraction = Fraction(retrieved_relevant, retrieved_rated)
    control_rate_fraction = Fraction(control_relevant, control_rated)
    lift_fraction = retrieved_rate_fraction - control_rate_fraction
    retrieved_rate = _clean_float(float(retrieved_rate_fraction))
    control_rate = _clean_float(float(control_rate_fraction))
    lift = _clean_float(float(lift_fraction))
    point_delta, lower, upper = paired_query_bootstrap(
        tuple(item.delta for item in query_measures),
        seed=active_protocol.thresholds.paired_ndcg_bootstrap_seed,
        resamples=active_protocol.thresholds.paired_ndcg_bootstrap_resamples,
        confidence=active_protocol.thresholds.paired_ndcg_confidence,
    )
    agreement, agreement_pairs = _ordinal_agreement(aggregates)
    repeat_mad = _clean_float(math.fsum(repeat_differences) / len(repeat_differences))
    repeat_within_one_count = sum(value <= 1 for value in repeat_differences)
    repeat_within_one = _clean_float(repeat_within_one_count / len(repeat_differences))
    metrics = coverage_metrics + (
        _metric(
            "retrieved_precision_at_5",
            retrieved_precision,
            numerator=retrieved_precision_fraction.numerator,
            denominator=retrieved_precision_fraction.denominator,
        ),
        _metric(
            "mean_retrieved_ndcg_at_5",
            retrieved_ndcg,
            numerator=len(query_measures),
            denominator=len(query_measures),
        ),
        _metric(
            "mean_control_ndcg_at_5",
            control_ndcg,
            numerator=len(query_measures),
            denominator=len(query_measures),
        ),
        _metric(
            "retrieved_relevant_rate",
            retrieved_rate,
            numerator=retrieved_relevant,
            denominator=retrieved_rated,
        ),
        _metric(
            "control_relevant_rate",
            control_rate,
            numerator=control_relevant,
            denominator=control_rated,
        ),
        _metric(
            "retrieved_control_relevant_rate_lift",
            lift,
            numerator=lift_fraction.numerator,
            denominator=lift_fraction.denominator,
            rate_contrast=RateContrastEvidence(
                retrieved_relevant_count=retrieved_relevant,
                retrieved_rated_count=retrieved_rated,
                retrieved_rate=retrieved_rate,
                control_relevant_count=control_relevant,
                control_rated_count=control_rated,
                control_rate=control_rate,
            ),
        ),
        _metric(
            "paired_ndcg_delta",
            point_delta,
            numerator=len(query_measures),
            denominator=len(query_measures),
        ),
        _metric(
            "paired_ndcg_bootstrap_lower",
            lower,
            numerator=len(query_measures),
            denominator=len(query_measures),
        ),
        _metric(
            "paired_ndcg_bootstrap_upper",
            upper,
            numerator=len(query_measures),
            denominator=len(query_measures),
        ),
        _metric(
            "mean_pairwise_ordinal_agreement",
            agreement,
            numerator=agreement_pairs,
            denominator=agreement_pairs,
        ),
        _metric(
            "repeat_mean_absolute_difference",
            repeat_mad,
            numerator=sum(repeat_differences),
            denominator=len(repeat_differences),
        ),
        _metric(
            "repeat_within_one_rate",
            repeat_within_one,
            numerator=repeat_within_one_count,
            denominator=len(repeat_differences),
        ),
    )
    values = {item.metric_name: cast(float, item.value) for item in metrics if item.supported}
    thresholds = active_protocol.thresholds
    threshold_misses: list[str] = []
    threshold_rules = (
        (
            "retrieved_precision_at_5",
            values["retrieved_precision_at_5"] >= thresholds.minimum_retrieved_precision_at_k,
        ),
        (
            "mean_retrieved_ndcg_at_5",
            values["mean_retrieved_ndcg_at_5"] >= thresholds.minimum_mean_ndcg_at_k,
        ),
        (
            "retrieved_control_relevant_rate_lift",
            values["retrieved_control_relevant_rate_lift"]
            >= thresholds.minimum_retrieved_control_relevant_rate_lift,
        ),
        ("paired_ndcg_delta", values["paired_ndcg_delta"] >= thresholds.minimum_paired_ndcg_delta),
        (
            "paired_ndcg_bootstrap_lower",
            values["paired_ndcg_bootstrap_lower"] > thresholds.paired_ndcg_lower_bound_must_exceed,
        ),
        (
            "mean_pairwise_ordinal_agreement",
            values["mean_pairwise_ordinal_agreement"] >= thresholds.minimum_ordinal_agreement,
        ),
        (
            "repeat_mean_absolute_difference",
            values["repeat_mean_absolute_difference"]
            <= thresholds.maximum_repeat_mean_absolute_difference,
        ),
        (
            "repeat_within_one_rate",
            values["repeat_within_one_rate"] >= thresholds.minimum_repeat_within_one_rate,
        ),
    )
    threshold_misses.extend(
        f"THRESHOLD_MISS:{name}" for name, passed in threshold_rules if not passed
    )
    decision = ExpertGateDecisionKind.FAIL if threshold_misses else ExpertGateDecisionKind.PASS
    reasons = (
        tuple(threshold_misses) if threshold_misses else ("ALL_MANDATORY_REQUIREMENTS_PASSED",)
    )
    positions = _subgroups(
        active_pack.queries,
        included,
        aggregates,
        measures_by_query,
        dimension="position",
        value_of=lambda query: query.exemplar_position_code,
    )
    competitions = _subgroups(
        active_pack.queries,
        included,
        aggregates,
        measures_by_query,
        dimension="competition",
        value_of=lambda query: query.exemplar_competition_name,
    )
    return _make_result(
        protocol=active_protocol,
        query_pack=active_pack,
        approval_digest=active_approval.approval_digest,
        evaluated_at=evaluated_at,
        included_submission_digests=submission_digests,
        excluded_submission_count=excluded_submission_count,
        eligible_participant_count=participant_count,
        completed_participant_count=participant_count,
        rated_judgement_count=len(rated),
        abstention_count=abstentions,
        unable_to_assess_count=unable,
        missing_judgement_count=missing,
        metrics=metrics,
        position_subgroups=positions,
        competition_subgroups=competitions,
        confidence_distribution=confidence_distribution,
        qualitative_failure_categories=failure_counts,
        decision=decision,
        reasons=reasons,
    )


def render_result(result: ExpertRelevanceStudyResult) -> bytes:
    validated = _fresh(result, ExpertRelevanceStudyResult, label="study result")
    return _canonical_bytes(validated.model_dump(mode="json"))


def render_safe_report(
    result: ExpertRelevanceStudyResult,
    *,
    presentation_digest: str,
) -> bytes:
    """Render aggregate-only report bytes with no labels or free text."""

    validated = _fresh(result, ExpertRelevanceStudyResult, label="study result")
    result_json = validated.model_dump(mode="json")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "evidence_class": "FORMAL_G_RW4",
        "claim_boundary": result_json["claim_boundary"],
        "protocol_digest": result_json["protocol_digest"],
        "query_pack_digest": result_json["query_pack_digest"],
        "presentation_digest": presentation_digest,
        "approval_digest": result_json["approval_digest"],
        "evaluated_at": result_json["evaluated_at"],
        "result_id": result_json["result_id"],
        "result_digest": result_json["result_digest"],
        "included_submission_digests": result_json["included_submission_digests"],
        "excluded_submission_count": result_json["excluded_submission_count"],
        "eligible_participant_count": result_json["eligible_participant_count"],
        "completed_participant_count": result_json["completed_participant_count"],
        "query_count": result_json["query_count"],
        "candidate_count": result_json["candidate_count"],
        "rated_judgement_count": result_json["rated_judgement_count"],
        "abstention_count": result_json["abstention_count"],
        "unable_to_assess_count": result_json["unable_to_assess_count"],
        "missing_judgement_count": result_json["missing_judgement_count"],
        "metrics": result_json["metrics"],
        "position_subgroups": result_json["position_subgroups"],
        "competition_subgroups": result_json["competition_subgroups"],
        "confidence_distribution": result_json["confidence_distribution"],
        "qualitative_failure_categories": result_json["qualitative_failure_categories"],
        "decision": result_json["decision"],
        "decision_reasons": result_json["decision_reasons"],
        "negative_result_retained": True,
    }
    payload["report_digest"] = canonical_research_digest(payload)
    return _canonical_bytes(payload)


def _write_exclusive(directory_fd: int, filename: str, content: bytes) -> str:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    file_descriptor = os.open(filename, flags, 0o600, dir_fd=directory_fd)
    with os.fdopen(file_descriptor, "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(content).hexdigest()


def _prepare_output_directory(path: Path) -> tuple[Path, int]:
    absolute = Path(os.path.abspath(path))
    for ancestor in (absolute, *absolute.parents):
        if not ancestor.exists():
            continue
        if ancestor.is_symlink() or ancestor.resolve(strict=True) != ancestor:
            raise ExpertRelevanceEvaluationError("evaluation output has an unsafe ancestor")
    absolute.mkdir(mode=0o700, parents=True, exist_ok=True)
    for ancestor in (absolute, *absolute.parents):
        if ancestor.is_symlink() or ancestor.resolve(strict=True) != ancestor:
            raise ExpertRelevanceEvaluationError("evaluation output has an unsafe ancestor")
    if not absolute.is_dir():
        raise ExpertRelevanceEvaluationError("evaluation output must be a directory")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(absolute, flags)
    if not stat.S_ISDIR(os.fstat(directory_fd).st_mode):
        os.close(directory_fd)
        raise ExpertRelevanceEvaluationError("evaluation output must be a directory")
    return absolute, directory_fd


def _artifact_exists(directory_fd: int, filename: str) -> bool:
    try:
        os.stat(filename, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def _artifact_paths(output_directory: Path) -> tuple[Path, Path, Path, Path, Path]:
    return (
        output_directory / CLAIM_FILENAME,
        output_directory / RUN_FILENAME,
        output_directory / RESULT_FILENAME,
        output_directory / REPORT_FILENAME,
        output_directory / RECEIPT_FILENAME,
    )


def _load_protected_submissions(path: Path) -> tuple[tuple[FormalStudySubmission, ...], str]:
    payload, raw = _safe_canonical_json(path)
    if set(payload) != {"schema_version", "evidence_class", "submissions"}:
        raise ExpertRelevanceEvaluationError("protected input envelope shape is incompatible")
    if payload["schema_version"] != 1 or payload["evidence_class"] != "FORMAL_G_RW4":
        raise ExpertRelevanceEvaluationError("protected input evidence class is incompatible")
    rows = payload["submissions"]
    if type(rows) is not list:
        raise ExpertRelevanceEvaluationError("protected input submissions must be a list")
    try:
        submissions = tuple(
            FormalStudySubmission.model_validate_json(canonical_json_bytes(item)) for item in rows
        )
    except ValidationError as exc:
        raise ExpertRelevanceEvaluationError(
            "protected formal submission contract rejected"
        ) from exc
    return submissions, hashlib.sha256(raw).hexdigest()


def run_one_use_formal_evaluation(
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
    presentation: ExpertStudyPresentationBundle,
    approval: ProtocolApproval,
    *,
    protected_input_path: Path,
    output_directory: Path,
    invocation_id: UUID,
    evaluated_at: datetime,
) -> FormalEvaluationArtifacts:
    """Claim once, then open protected input and retain aggregate immutable evidence."""

    active_protocol, active_pack, active_presentation, active_approval = _assert_authority(
        protocol, query_pack, presentation, approval
    )
    if active_approval is None:
        raise ExpertRelevanceEvaluationError("formal evaluation requires approval")
    output_directory, directory_fd = _prepare_output_directory(output_directory)
    claim_path, run_path, result_path, report_path, receipt_path = _artifact_paths(output_directory)
    try:
        authority_directory, authority_fd = _prepare_output_directory(
            FORMAL_EVALUATION_AUTHORITY_ROOT
        )
    except Exception:
        os.close(directory_fd)
        raise
    authority_identity = {
        "protocol_digest": active_protocol.protocol_digest,
        "query_pack_digest": active_pack.query_pack_digest,
        "presentation_digest": active_presentation.presentation_digest,
        "approval_digest": active_approval.approval_digest,
    }
    authority_key = canonical_research_digest(authority_identity)
    authority_claim_path = authority_directory / f"{authority_key}.claim.json"
    authority_receipt_path = authority_directory / f"{authority_key}.receipt.json"
    try:
        if any(
            _artifact_exists(directory_fd, path.name)
            for path in (claim_path, run_path, result_path, report_path, receipt_path)
        ):
            raise FileExistsError("one-use formal evaluation refuses replay or partial output")
        claim_payload: dict[str, Any] = {
            "schema_version": 1,
            "authority_key": authority_key,
            "invocation_id": str(invocation_id),
            "protocol_digest": active_protocol.protocol_digest,
            "query_pack_digest": active_pack.query_pack_digest,
            "presentation_digest": active_presentation.presentation_digest,
            "approval_digest": active_approval.approval_digest,
            "evaluated_at": evaluated_at.isoformat(),
            "output_directory": str(output_directory),
            "protected_input_claimed_before_open": True,
            "one_use": True,
        }
        claim_payload["claim_digest"] = canonical_research_digest(claim_payload)
        claim_content = _canonical_bytes(claim_payload)
        try:
            authority_claim_file_digest = _write_exclusive(
                authority_fd, authority_claim_path.name, claim_content
            )
        except FileExistsError as exc:
            raise FileExistsError("one-use formal authority was already consumed") from exc
        claim_file_digest = _write_exclusive(directory_fd, claim_path.name, claim_content)

        protected_input_digest: str | None = None
        try:
            submissions, protected_input_digest = _load_protected_submissions(protected_input_path)
            result = evaluate_expert_relevance(
                active_protocol,
                active_pack,
                active_presentation,
                active_approval,
                submissions,
                evaluated_at=evaluated_at,
            )
        except ExpertRelevanceEvaluationError:
            result = _integrity_failure_result(
                active_protocol,
                active_pack,
                active_approval.approval_digest,
                evaluated_at,
                reason="PROTECTED_INPUT_REJECTED",
                excluded_submission_count=0,
            )

        result_content = render_result(result)
        report_content = render_safe_report(
            result, presentation_digest=active_presentation.presentation_digest
        )
        run_payload: dict[str, Any] = {
            "schema_version": 1,
            "invocation_id": str(invocation_id),
            "protocol_digest": active_protocol.protocol_digest,
            "query_pack_digest": active_pack.query_pack_digest,
            "presentation_digest": active_presentation.presentation_digest,
            "approval_digest": active_approval.approval_digest,
            "protected_input_file_digest": protected_input_digest,
            "evaluated_at": evaluated_at.isoformat(),
            "included_submission_digests": result.included_submission_digests,
            "result_digest": result.result_digest,
            "decision": result.decision.value,
        }
        run_payload["run_digest"] = canonical_research_digest(run_payload)
        run_content = _canonical_bytes(run_payload)
        run_file_digest = _write_exclusive(directory_fd, run_path.name, run_content)
        result_file_digest = _write_exclusive(directory_fd, result_path.name, result_content)
        report_file_digest = _write_exclusive(directory_fd, report_path.name, report_content)
        report_digest = cast(str, json.loads(report_content)["report_digest"])
        receipt_payload: dict[str, Any] = {
            "schema_version": 1,
            "invocation_id": str(invocation_id),
            "claim_digest": claim_payload["claim_digest"],
            "run_digest": run_payload["run_digest"],
            "result_digest": result.result_digest,
            "report_digest": report_digest,
            "claim_file_digest": claim_file_digest,
            "authority_claim_file_digest": authority_claim_file_digest,
            "run_file_digest": run_file_digest,
            "result_file_digest": result_file_digest,
            "report_file_digest": report_file_digest,
            "one_use_consumed": True,
        }
        receipt_payload["receipt_digest"] = canonical_research_digest(receipt_payload)
        receipt_content = _canonical_bytes(receipt_payload)
        receipt_file_digest = _write_exclusive(directory_fd, receipt_path.name, receipt_content)
        authority_receipt_payload: dict[str, Any] = {
            "schema_version": 1,
            "authority_key": authority_key,
            "claim_digest": claim_payload["claim_digest"],
            "invocation_id": str(invocation_id),
            "output_receipt_digest": receipt_payload["receipt_digest"],
            "output_receipt_file_digest": receipt_file_digest,
            "one_use_consumed": True,
        }
        authority_receipt_payload["authority_receipt_digest"] = canonical_research_digest(
            authority_receipt_payload
        )
        _write_exclusive(
            authority_fd,
            authority_receipt_path.name,
            _canonical_bytes(authority_receipt_payload),
        )
        os.fsync(directory_fd)
        os.fsync(authority_fd)
        return FormalEvaluationArtifacts(
            result=result,
            claim_path=claim_path,
            run_path=run_path,
            result_path=result_path,
            report_path=report_path,
            receipt_path=receipt_path,
            authority_claim_path=authority_claim_path,
            authority_receipt_path=authority_receipt_path,
            receipt_digest=cast(str, receipt_payload["receipt_digest"]),
        )
    finally:
        os.close(directory_fd)
        os.close(authority_fd)


__all__ = [
    "CLAIM_FILENAME",
    "DEFAULT_PRESENTATION_PATH",
    "DEFAULT_PROTOCOL_PATH",
    "DEFAULT_QUERY_PACK_PATH",
    "FROZEN_PRESENTATION_DIGEST",
    "FROZEN_PROTOCOL_DIGEST",
    "FROZEN_QUERY_PACK_DIGEST",
    "FormalEvaluationArtifacts",
    "REPORT_FILENAME",
    "RECEIPT_FILENAME",
    "RESULT_FILENAME",
    "RUN_FILENAME",
    "ExpertRelevanceEvaluationError",
    "absent_formal_evidence_status",
    "evaluate_expert_relevance",
    "load_frozen_presentation",
    "load_frozen_protocol",
    "load_frozen_query_pack",
    "load_protocol_approval",
    "paired_query_bootstrap",
    "render_result",
    "render_safe_report",
    "run_one_use_formal_evaluation",
]

"""Protocol-bound deterministic ranking metrics using persisted contracts."""
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from scouting.contracts.evaluation import (
    AgreementMethod,
    BootstrapInterval,
    BootstrapMethod,
    EvaluationEvidence,
    EvaluationProtocol,
    MetricName,
    MetricResult,
    MetricStatus,
    PairPredictionState,
    PairPreferenceEvidence,
    RankComparisonResult,
    RelevanceLabel,
    ReviewerAuthority,
    ReviewerIdentity,
    TiePolicy,
    _sequence_digest,
    derive_rank_comparison,
)
from scouting.contracts.evaluation import _digest as _contract_digest
from scouting.contracts.evaluation_calculations import (
    Calculation,
)
from scouting.contracts.evaluation_calculations import (
    derive_ranking_metric_children as _calculate_ranking_metric_children,
)
from scouting.contracts.primitives import ContractModel


class LabelState(StrEnum):
    RELEVANT = "RELEVANT"
    PARTIAL = "PARTIAL"
    IRRELEVANT = "IRRELEVANT"
    UNJUDGED = "UNJUDGED"
    ABSTAIN = "ABSTAIN"


def _input_digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def _contract[ContractT: ContractModel](
    cls: type[ContractT], payload: dict[str, object], digest_name: str
) -> ContractT:
    draft = cls.model_construct(**payload)  # type: ignore[arg-type]
    payload[digest_name] = _contract_digest(draft.model_dump(mode="json"), digest_name)
    return cls(**payload)


@dataclass(frozen=True, slots=True)
class RankedItem:
    candidate_id: str
    score: float
    label: LabelState

    def __post_init__(self) -> None:
        if (
            not self.candidate_id
            or not math.isfinite(self.score)
            or (self.score == 0.0 and math.copysign(1.0, self.score) < 0)
        ):
            raise ValueError(
                "ranked item requires a non-empty candidate and finite canonical score"
            )


@dataclass(frozen=True, slots=True)
class RankingRow:
    query_id: str
    candidate_universe: tuple[str, ...]
    items: tuple[RankedItem, ...]


@dataclass(frozen=True, slots=True)
class PairPrediction:
    preference: PairPreferenceEvidence
    reviewer: ReviewerIdentity
    state: PairPredictionState
    predicted_candidate_id: str | None = None

    def __post_init__(self) -> None:
        allowed = (self.preference.left_candidate_id, self.preference.right_candidate_id)
        if (
            self.state is PairPredictionState.PREDICTED
            and self.predicted_candidate_id not in allowed
        ):
            raise ValueError("predicted pair member must be in the canonical pair")
        if (
            self.state is not PairPredictionState.PREDICTED
            and self.predicted_candidate_id is not None
        ):
            raise ValueError("abstained and missing predictions cannot name a candidate")


@dataclass(frozen=True, slots=True)
class AgreementRow:
    left: EvaluationEvidence
    right: EvaluationEvidence
    left_reviewer: ReviewerIdentity
    right_reviewer: ReviewerIdentity


def _metric_result(
    metric: MetricName,
    k: int | None,
    protocol: EvaluationProtocol,
    query_ids: tuple[str, ...],
    value: float | None,
    numerator: float | None,
    denominator: float | None,
    reason: str | None,
    input_payload: object,
) -> MetricResult:
    return _contract(
        MetricResult,
        {
            "metric": metric,
            "k": k,
            "protocol_digest": protocol.protocol_digest,
            "evaluated_query_digest": _sequence_digest(query_ids),
            "input_digest": _input_digest(input_payload),
            "value": value,
            "numerator": numerator,
            "denominator": denominator,
            "status": MetricStatus.COMPUTED
            if value is not None
            else MetricStatus.INSUFFICIENT_DENOMINATOR,
            "reason": reason,
        },
        "result_digest",
    )


def _ordered_items(protocol: EvaluationProtocol, row: RankingRow) -> tuple[RankedItem, ...]:
    if protocol.tie_policy is not TiePolicy.SCORE_DESC_CANDIDATE_ID:
        raise ValueError("protocol tie policy is unsupported")
    universe = row.candidate_universe
    if (
        tuple(sorted(universe)) != universe
        or len(universe) != len(set(universe))
        or len(row.items) != len(universe)
    ):
        raise ValueError(
            "candidate universe and ranked items must be complete and canonically unique"
        )
    if {item.candidate_id for item in row.items} != set(universe):
        raise ValueError("ranked items must exactly equal frozen candidate universe")
    ordered = tuple(sorted(row.items, key=lambda item: (-item.score, item.candidate_id)))
    if row.items != ordered:
        raise ValueError("ranked items must follow protocol score-desc candidate-ID tie policy")
    return ordered


def _ranking_calculation(
    protocol: EvaluationProtocol,
    rows: tuple[tuple[str, tuple[str, ...], tuple[float, ...], tuple[str, ...]], ...],
    metric: MetricName,
    k: int,
) -> Calculation:
    return _calculate_ranking_metric_children(
        protocol_digest=protocol.protocol_digest,
        declared_k=protocol.declared_k,
        partial_gain=protocol.partial_gain,
        partial_counts_for_precision_recall=protocol.partial_counts_for_precision_recall,
        bootstrap_seed=protocol.bootstrap_seed,
        bootstrap_resamples=protocol.bootstrap_resamples,
        bootstrap_confidence=protocol.bootstrap_confidence,
        bootstrap_method=protocol.bootstrap_method.value,
        rows=rows,
        metric=metric.value,
        k=k,
    )


def _calculated_metric(payload: dict[str, object]) -> MetricResult:
    value: dict[str, Any] = dict(payload)
    value["metric"] = MetricName(str(value["metric"]))
    value["status"] = MetricStatus(str(value["status"]))
    return MetricResult(**value)


def _calculated_interval(payload: dict[str, object]) -> BootstrapInterval:
    value: dict[str, Any] = dict(payload)
    value["method"] = BootstrapMethod(str(value["method"]))
    value["status"] = MetricStatus(str(value["status"]))
    return BootstrapInterval(**value)


def evaluate_ranking(
    protocol: EvaluationProtocol, row: RankingRow, k: int
) -> dict[MetricName, MetricResult]:
    """Adapt one ranking row to the shared primitive calculation authority."""
    ordered = _ordered_items(protocol, row)
    values: dict[MetricName, MetricResult] = {}
    for metric in (MetricName.PRECISION, MetricName.RECALL, MetricName.NDCG, MetricName.COVERAGE):
        calculation = _ranking_calculation(
            protocol,
            (
                (
                    row.query_id,
                    tuple(item.candidate_id for item in ordered),
                    tuple(item.score for item in ordered),
                    tuple(item.label.value for item in ordered),
                ),
            ),
            metric,
            k,
        )
        values[metric] = _calculated_metric(calculation.per_query[0])
    return values


def bootstrap_interval(
    protocol: EvaluationProtocol, rows: Sequence[RankingRow], k: int, metric: MetricName
) -> tuple[MetricResult, BootstrapInterval]:
    """Return the shared canonical aggregate and deterministic bootstrap interval."""
    if (
        protocol.resampling_unit != "query"
        or metric
        not in {
            MetricName.PRECISION,
            MetricName.RECALL,
            MetricName.NDCG,
            MetricName.COVERAGE,
        }
        or metric not in set(protocol.primary_metrics + protocol.secondary_metrics)
    ):
        raise ValueError("protocol does not support query bootstrap for metric")
    canonical_rows = tuple(
        (
            row.query_id,
            tuple(item.candidate_id for item in _ordered_items(protocol, row)),
            tuple(item.score for item in _ordered_items(protocol, row)),
            tuple(item.label.value for item in _ordered_items(protocol, row)),
        )
        for row in rows
    )
    calculation = _ranking_calculation(protocol, canonical_rows, metric, k)
    return _calculated_metric(calculation.aggregate), _calculated_interval(calculation.interval)


def rank_comparison(
    protocol: EvaluationProtocol, query_id: str, left: Sequence[str], right: Sequence[str], k: int
) -> RankComparisonResult:
    """Canonical comparison that keeps valid set metrics when rho is unavailable."""
    return derive_rank_comparison(protocol, query_id, tuple(left), tuple(right), k)


def pair_preference_accuracy(
    protocol: EvaluationProtocol, predictions: Sequence[PairPrediction]
) -> MetricResult:
    """Governed pair accuracy with explicit predicted, abstained and missing states."""
    ordered = tuple(
        sorted(
            predictions,
            key=lambda row: (
                row.preference.query_id,
                row.preference.left_candidate_id,
                row.preference.right_candidate_id,
                row.preference.reviewer_key,
                row.preference.preference_id,
            ),
        )
    )
    if tuple(predictions) != ordered:
        raise ValueError("pair predictions must be canonically ordered")
    keys = {
        (
            row.preference.query_id,
            row.preference.left_candidate_id,
            row.preference.right_candidate_id,
            row.preference.reviewer_key,
        )
        for row in predictions
    }
    ids = {row.preference.preference_id for row in predictions}
    if len(keys) != len(predictions) or len(ids) != len(predictions):
        raise ValueError("pair predictions require unique canonical pair identities")
    query_ids = tuple(sorted({row.preference.query_id for row in predictions}))
    input_payload = [
        (
            row.preference.preference_digest,
            row.reviewer.reviewer_digest,
            row.state.value,
            row.predicted_candidate_id,
        )
        for row in predictions
    ]
    eligible: list[PairPrediction] = []
    for row in predictions:
        preference, reviewer = row.preference, row.reviewer
        if (
            preference.rubric_id != protocol.rubric.rubric_id
            or preference.rubric_digest != protocol.rubric_digest
        ):
            raise ValueError("pair preference evidence must bind the protocol rubric")
        if (preference.reviewer_key, preference.reviewer_digest) != (
            reviewer.reviewer_key,
            reviewer.reviewer_digest,
        ) or reviewer.authority is not ReviewerAuthority.GOVERNED_HUMAN_EXPERT:
            raise ValueError("pair preference must bind a governed reviewer")
        if row.state is PairPredictionState.MISSING:
            return _metric_result(
                MetricName.PAIR_PREFERENCE,
                None,
                protocol,
                query_ids,
                None,
                None,
                None,
                "missing_pair_prediction",
                input_payload,
            )
        if not preference.abstained and row.state is PairPredictionState.PREDICTED:
            eligible.append(row)
    if not eligible:
        return _metric_result(
            MetricName.PAIR_PREFERENCE,
            None,
            protocol,
            query_ids,
            None,
            None,
            None,
            "no_eligible_predicted_pairs",
            input_payload,
        )
    correct = sum(
        row.predicted_candidate_id == row.preference.preferred_candidate_id for row in eligible
    )
    return _metric_result(
        MetricName.PAIR_PREFERENCE,
        None,
        protocol,
        query_ids,
        correct / len(eligible),
        float(correct),
        float(len(eligible)),
        None,
        input_payload,
    )


def inter_rater_agreement(
    protocol: EvaluationProtocol, rows: Sequence[AgreementRow]
) -> MetricResult:
    """Canonical exact agreement with protocol-bound rubric and orientation."""
    if protocol.agreement_method is not AgreementMethod.EXACT_PERCENT_AGREEMENT:
        raise ValueError("protocol agreement method is unsupported")
    canonical: list[
        tuple[EvaluationEvidence, EvaluationEvidence, ReviewerIdentity, ReviewerIdentity]
    ] = []
    for row in rows:
        left, right, left_reviewer, right_reviewer = (
            row.left,
            row.right,
            row.left_reviewer,
            row.right_reviewer,
        )
        if (left.reviewer_key, left.evidence_digest) > (right.reviewer_key, right.evidence_digest):
            left, right, left_reviewer, right_reviewer = right, left, right_reviewer, left_reviewer
        canonical.append((left, right, left_reviewer, right_reviewer))
    ordered = tuple(
        sorted(
            canonical,
            key=lambda row: (
                row[0].query_id,
                row[0].candidate_id,
                row[0].reviewer_key,
                row[1].reviewer_key,
            ),
        )
    )
    if tuple(canonical) != ordered:
        raise ValueError("agreement rows must be canonically ordered")
    keys = {
        (left.query_id, left.candidate_id, left.reviewer_key, right.reviewer_key)
        for left, right, _, _ in ordered
    }
    if len(keys) != len(ordered):
        raise ValueError("agreement rows require unique query candidate reviewer identities")
    query_ids = tuple(sorted({left.query_id for left, _, _, _ in ordered}))
    input_payload: list[tuple[str, str]] = []
    eligible: list[tuple[EvaluationEvidence, EvaluationEvidence]] = []
    for left, right, left_reviewer, right_reviewer in ordered:
        if (left.query_id, left.candidate_id, left.rubric_id, left.rubric_digest) != (
            right.query_id,
            right.candidate_id,
            right.rubric_id,
            right.rubric_digest,
        ) or left.reviewer_key == right.reviewer_key:
            raise ValueError(
                "agreement rows must compare distinct reviewers on one query candidate rubric"
            )
        if (
            left.rubric_id != protocol.rubric.rubric_id
            or left.rubric_digest != protocol.rubric_digest
        ):
            raise ValueError("agreement evidence must bind the protocol rubric")
        if (left.reviewer_key, left.reviewer_digest) != (
            left_reviewer.reviewer_key,
            left_reviewer.reviewer_digest,
        ) or (right.reviewer_key, right.reviewer_digest) != (
            right_reviewer.reviewer_key,
            right_reviewer.reviewer_digest,
        ):
            raise ValueError("agreement rows must bind reviewer identities")
        if (
            left_reviewer.authority is not ReviewerAuthority.GOVERNED_HUMAN_EXPERT
            or right_reviewer.authority is not ReviewerAuthority.GOVERNED_HUMAN_EXPERT
        ):
            raise ValueError("agreement requires governed reviewers")
        input_payload.append((left.evidence_digest, right.evidence_digest))
        if left.label is not RelevanceLabel.ABSTAIN and right.label is not RelevanceLabel.ABSTAIN:
            eligible.append((left, right))
    if not eligible:
        return _metric_result(
            MetricName.AGREEMENT,
            None,
            protocol,
            query_ids,
            None,
            None,
            None,
            "no_eligible_rater_labels",
            input_payload,
        )
    matches = sum(left.label is right.label for left, right in eligible)
    return _metric_result(
        MetricName.AGREEMENT,
        None,
        protocol,
        query_ids,
        matches / len(eligible),
        float(matches),
        float(len(eligible)),
        None,
        input_payload,
    )

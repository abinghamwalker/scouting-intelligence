"""Strict, canonical, relational contracts for governed ranking evaluation."""
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import math
import random
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import AfterValidator, Field, Strict, StringConstraints, model_validator

from .evaluation_calculations import (
    derive_ranking_metric_children as _calculate_ranking_metric_children,
)
from .evidence import LicenceUseClass, Sha256Digest
from .primitives import (
    ContractModel,
    NonEmptyString,
    NonNegativeInt,
    PositiveInt,
    SchemaVersion,
    UtcInstant,
)


def _finite(value: float) -> float:
    if not math.isfinite(value) or (value == 0.0 and math.copysign(1.0, value) < 0):
        raise ValueError("numeric value must be finite and canonical")
    return value


type FiniteFloat = Annotated[float, Field(strict=True), AfterValidator(_finite)]
type EvaluationId = Annotated[str, Strict(), StringConstraints(pattern=r"^[a-z][a-z0-9_-]{0,127}$")]


def _digest(payload: dict[str, Any], omitted: str) -> Sha256Digest:
    value = dict(payload)
    value.pop(omitted, None)

    def json_default(item: object) -> Any:
        if isinstance(item, datetime):
            return item.isoformat().replace("+00:00", "Z")
        if isinstance(item, ContractModel):
            return item.model_dump(mode="json")
        return str(item)

    return hashlib.sha256(
        json.dumps(
            value, default=json_default, ensure_ascii=True, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    ).hexdigest()


def _sequence_digest(values: tuple[str, ...]) -> Sha256Digest:
    return hashlib.sha256(
        json.dumps(values, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _canonical(items: tuple[Any, ...], key: Any, message: str) -> None:
    if tuple(sorted(items, key=key)) != items:
        raise ValueError(message)


class EvaluationPartition(StrEnum):
    FIT = "FIT"
    TUNE = "TUNE"
    CALIBRATION = "CALIBRATION"
    PROTECTED_TEST = "PROTECTED_TEST"
    PROSPECTIVE = "PROSPECTIVE"


class EvidenceAuthority(StrEnum):
    GOVERNED_HUMAN_EXPERT = "GOVERNED_HUMAN_EXPERT"
    IMPLEMENTATION_FIXTURE = "IMPLEMENTATION_FIXTURE"


class ReviewerAuthority(StrEnum):
    GOVERNED_HUMAN_EXPERT = "GOVERNED_HUMAN_EXPERT"
    IMPLEMENTATION_FIXTURE = "IMPLEMENTATION_FIXTURE"


class RelevanceLabel(StrEnum):
    RELEVANT = "RELEVANT"
    IRRELEVANT = "IRRELEVANT"
    PARTIAL = "PARTIAL"
    ABSTAIN = "ABSTAIN"


class GateDecisionKind(StrEnum):
    ACCEPT_CLAIM = "ACCEPT_CLAIM"
    NARROW_APPLICABILITY = "NARROW_APPLICABILITY"
    NO_GO = "NO_GO"


class MetricStatus(StrEnum):
    COMPUTED = "COMPUTED"
    INSUFFICIENT_DENOMINATOR = "INSUFFICIENT_DENOMINATOR"
    UNSUPPORTED = "UNSUPPORTED"


class MetricName(StrEnum):
    PRECISION = "precision"
    RECALL = "recall"
    NDCG = "ndcg"
    COVERAGE = "coverage"
    PAIR_PREFERENCE = "pair_preference"
    AGREEMENT = "agreement"


class PairPredictionState(StrEnum):
    PREDICTED = "PREDICTED"
    ABSTAINED = "ABSTAINED"
    MISSING = "MISSING"


class NoGoReason(StrEnum):
    MISSING_EXPERT_RELEVANCE_EVIDENCE = "MISSING_EXPERT_RELEVANCE_EVIDENCE"
    MISSING_PROTECTED_POPULATION = "MISSING_PROTECTED_POPULATION"


class ProtectedAccessOutcomeKind(StrEnum):
    """The only possible outcome before a protected population is opened."""

    NOT_ACCESSED_MISSING_POPULATION = "NOT_ACCESSED_MISSING_POPULATION"


class MissingnessPolicy(StrEnum):
    REQUIRE_COMPLETE = "REQUIRE_COMPLETE"


class TiePolicy(StrEnum):
    SCORE_DESC_CANDIDATE_ID = "SCORE_DESC_CANDIDATE_ID"


class AgreementMethod(StrEnum):
    EXACT_PERCENT_AGREEMENT = "EXACT_PERCENT_AGREEMENT"


class BootstrapMethod(StrEnum):
    PERCENTILE = "PERCENTILE"


class RobustnessStatus(StrEnum):
    COMPUTED = "COMPUTED"
    UNSUPPORTED_INSUFFICIENT_EVIDENCE = "UNSUPPORTED_INSUFFICIENT_EVIDENCE"


class StressTestKind(StrEnum):
    SPLIT_HALF_RELIABILITY = "split_half_reliability"
    ROLLING_WINDOW_STABILITY = "rolling_window_stability"
    MINUTES_SAMPLE_SENSITIVITY = "minutes_sample_sensitivity"
    TIME_WALK_FORWARD = "time_walk_forward"
    LEAVE_COMPETITION_OUT = "leave_competition_out"
    LEAVE_TEAM_OUT = "leave_team_out"
    LEAVE_PROVIDER_OUT = "leave_provider_out"
    INTERSECTION_ONLY_SOURCE_COMPARISON = "intersection_only_source_comparison"


class ControlKind(StrEnum):
    COVERAGE_ONLY = "coverage_only"
    METADATA = "metadata"
    RAW_EUCLIDEAN = "raw_euclidean"
    SHUFFLED_LABEL = "shuffled_label"
    SHUFFLED_PAIR = "shuffled_pair"


class FailureCategory(StrEnum):
    DATA_COVERAGE = "data_coverage"
    ROLE_AMBIGUITY = "role_ambiguity"
    CONTEXT_MISMATCH = "context_mismatch"
    SAMPLE_INSUFFICIENCY = "sample_insufficiency"
    IDENTITY_UNCERTAINTY = "identity_uncertainty"
    OBJECTIVE_MISMATCH = "objective_mismatch"
    TEMPORAL_INSUFFICIENCY = "temporal_insufficiency"
    SOURCE_TRANSFER_INSUFFICIENCY = "source_transfer_insufficiency"


class ApplicabilityState(StrEnum):
    UNSUPPORTED = "UNSUPPORTED"


_RANK_METRICS = frozenset(
    {MetricName.PRECISION, MetricName.RECALL, MetricName.NDCG, MetricName.COVERAGE}
)
_BOOTSTRAP_METRICS = _RANK_METRICS


class RubricAuthority(ContractModel):
    rubric_id: EvaluationId
    authority_record_digest: Sha256Digest
    rubric_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.rubric_digest != _digest(self.model_dump(mode="json"), "rubric_digest"):
            raise ValueError("rubric_digest must match canonical payload")
        return self


class ReviewerIdentity(ContractModel):
    reviewer_key: EvaluationId
    authority: ReviewerAuthority
    authority_record_digest: Sha256Digest
    credential_digest: Sha256Digest
    permitted_use: LicenceUseClass
    reviewer_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.permitted_use is LicenceUseClass.PROHIBITED:
            raise ValueError("reviewer use cannot be prohibited")
        if self.reviewer_digest != _digest(self.model_dump(mode="json"), "reviewer_digest"):
            raise ValueError("reviewer_digest must match canonical payload")
        return self


class EvaluationQuery(ContractModel):
    query_id: EvaluationId
    role_brief_id: EvaluationId
    role_brief_digest: Sha256Digest
    exemplar_ids: tuple[EvaluationId, ...] = ()
    exemplar_digest: Sha256Digest
    candidate_universe_digest: Sha256Digest
    candidate_ids: Annotated[tuple[EvaluationId, ...], Field(min_length=1)]
    feature_cutoff_ts: UtcInstant
    query_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            len(self.exemplar_ids) != len(set(self.exemplar_ids))
            or tuple(sorted(self.exemplar_ids)) != self.exemplar_ids
        ):
            raise ValueError("exemplar_ids must be unique and canonically ordered")
        if (
            len(self.candidate_ids) != len(set(self.candidate_ids))
            or tuple(sorted(self.candidate_ids)) != self.candidate_ids
        ):
            raise ValueError("candidate_ids must be unique and canonically ordered")
        if set(self.exemplar_ids) & set(self.candidate_ids):
            raise ValueError("exemplars cannot enter the candidate universe")
        if self.candidate_universe_digest != _sequence_digest(self.candidate_ids):
            raise ValueError("candidate_universe_digest must bind canonical candidate_ids")
        if self.query_digest != _digest(self.model_dump(mode="json"), "query_digest"):
            raise ValueError("query_digest must match canonical payload")
        return self


class EvaluationEvidence(ContractModel):
    evidence_id: EvaluationId
    query_id: EvaluationId
    candidate_id: EvaluationId
    reviewer_key: EvaluationId
    reviewer_digest: Sha256Digest
    rubric_id: EvaluationId
    rubric_digest: Sha256Digest
    label: RelevanceLabel
    authority: EvidenceAuthority
    provenance_digest: Sha256Digest
    rights_use: LicenceUseClass
    available_at: UtcInstant
    evidence_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.rights_use is LicenceUseClass.PROHIBITED:
            raise ValueError("evidence rights cannot be prohibited")
        if (
            self.authority is EvidenceAuthority.IMPLEMENTATION_FIXTURE
            and self.label is RelevanceLabel.ABSTAIN
        ):
            raise ValueError("fixture evidence must exercise a concrete implementation label")
        if self.evidence_digest != _digest(self.model_dump(mode="json"), "evidence_digest"):
            raise ValueError("evidence_digest must match canonical payload")
        return self


class PairPreferenceEvidence(ContractModel):
    preference_id: EvaluationId
    query_id: EvaluationId
    left_candidate_id: EvaluationId
    right_candidate_id: EvaluationId
    preferred_candidate_id: EvaluationId | None
    abstained: bool
    reviewer_key: EvaluationId
    reviewer_digest: Sha256Digest
    rubric_id: EvaluationId
    rubric_digest: Sha256Digest
    provenance_digest: Sha256Digest
    rights_use: LicenceUseClass
    available_at: UtcInstant
    preference_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.left_candidate_id >= self.right_candidate_id:
            raise ValueError("pair candidates must be canonically unordered")
        if self.abstained != (self.preferred_candidate_id is None):
            raise ValueError("abstention and preferred candidate must agree")
        if self.preferred_candidate_id not in (
            None,
            self.left_candidate_id,
            self.right_candidate_id,
        ):
            raise ValueError("preferred candidate must be in pair")
        if self.rights_use is LicenceUseClass.PROHIBITED:
            raise ValueError("preference rights cannot be prohibited")
        if self.preference_digest != _digest(self.model_dump(mode="json"), "preference_digest"):
            raise ValueError("preference_digest must match canonical payload")
        return self


class HardNegativeEvidence(ContractModel):
    hard_negative_id: EvaluationId
    query_id: EvaluationId
    candidate_id: EvaluationId
    reviewer_key: EvaluationId
    reviewer_digest: Sha256Digest
    rubric_id: EvaluationId
    rubric_digest: Sha256Digest
    authority: EvidenceAuthority
    rationale_digest: Sha256Digest
    provenance_digest: Sha256Digest
    rights_use: LicenceUseClass
    available_at: UtcInstant
    hard_negative_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.rights_use is LicenceUseClass.PROHIBITED:
            raise ValueError("hard-negative rights cannot be prohibited")
        if self.hard_negative_digest != _digest(
            self.model_dump(mode="json"), "hard_negative_digest"
        ):
            raise ValueError("hard_negative_digest must match canonical payload")
        return self


class PartitionMembership(ContractModel):
    query_id: EvaluationId
    partition: EvaluationPartition
    membership_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.membership_digest != _digest(self.model_dump(mode="json"), "membership_digest"):
            raise ValueError("membership_digest must match canonical payload")
        return self


class EvaluationProtocol(ContractModel):
    schema_version: SchemaVersion = 1
    protocol_id: EvaluationId
    protocol_version: PositiveInt
    claim_boundary: Literal["resemblance_only"]
    declared_k: Annotated[tuple[PositiveInt, ...], Field(min_length=1)]
    decision_cutoff_ts: UtcInstant
    rubric: RubricAuthority
    rubric_digest: Sha256Digest
    query_digest: Sha256Digest
    reviewer_roster_digest: Sha256Digest
    partition_digest: Sha256Digest
    partial_gain: FiniteFloat
    partial_counts_for_precision_recall: bool
    missingness_policy: MissingnessPolicy
    tie_policy: TiePolicy
    agreement_method: AgreementMethod
    resampling_unit: Literal["query"]
    bootstrap_seed: NonNegativeInt
    bootstrap_resamples: PositiveInt
    bootstrap_confidence: FiniteFloat
    bootstrap_method: BootstrapMethod
    primary_metrics: Annotated[tuple[MetricName, ...], Field(min_length=1)]
    secondary_metrics: tuple[MetricName, ...] = ()
    protocol_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if tuple(sorted(self.declared_k)) != self.declared_k or len(self.declared_k) != len(
            set(self.declared_k)
        ):
            raise ValueError("declared_k must be unique and canonically ordered")
        if self.rubric_digest != self.rubric.rubric_digest:
            raise ValueError("protocol rubric_digest must bind rubric authority")
        if not 0.0 <= self.partial_gain <= 1.0 or not 0.0 < self.bootstrap_confidence < 1.0:
            raise ValueError("partial gain and bootstrap confidence must be unit values")
        all_metrics = self.primary_metrics + self.secondary_metrics
        if len(all_metrics) != len(set(all_metrics)):
            raise ValueError("metric roster must be unique")
        if any(metric not in _BOOTSTRAP_METRICS for metric in self.primary_metrics):
            raise ValueError("primary metrics must support the protected bootstrap contract")
        if self.protocol_digest != _digest(self.model_dump(mode="json"), "protocol_digest"):
            raise ValueError("protocol_digest must match canonical payload")
        return self


class Adjudication(ContractModel):
    adjudication_id: EvaluationId
    query_id: EvaluationId
    candidate_id: EvaluationId
    rubric_id: EvaluationId
    rubric_digest: Sha256Digest
    evidence_ids: Annotated[tuple[EvaluationId, ...], Field(min_length=2)]
    adjudicator_key: EvaluationId
    resolved_label: RelevanceLabel
    rationale_digest: Sha256Digest
    adjudication_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            len(self.evidence_ids) != len(set(self.evidence_ids))
            or tuple(sorted(self.evidence_ids)) != self.evidence_ids
        ):
            raise ValueError("adjudication evidence must be unique and canonically ordered")
        if self.resolved_label is RelevanceLabel.ABSTAIN:
            raise ValueError("adjudication must resolve a concrete label")
        if self.adjudication_digest != _digest(self.model_dump(mode="json"), "adjudication_digest"):
            raise ValueError("adjudication_digest must match canonical payload")
        return self


class EvaluationBundle(ContractModel):
    schema_version: SchemaVersion = 1
    protocol: EvaluationProtocol
    queries: Annotated[tuple[EvaluationQuery, ...], Field(min_length=1)]
    reviewers: Annotated[tuple[ReviewerIdentity, ...], Field(min_length=1)]
    relevance: tuple[EvaluationEvidence, ...] = ()
    preferences: tuple[PairPreferenceEvidence, ...] = ()
    hard_negatives: tuple[HardNegativeEvidence, ...] = ()
    adjudications: tuple[Adjudication, ...] = ()
    memberships: Annotated[tuple[PartitionMembership, ...], Field(min_length=1)]
    candidate_manifest_digest: Sha256Digest
    bundle_digest: Sha256Digest

    @model_validator(mode="after")
    def coherent(self) -> Self:
        _canonical(self.queries, lambda item: item.query_id, "queries must be canonically ordered")
        queries = {item.query_id: item for item in self.queries}
        if len(queries) != len(self.queries):
            raise ValueError("query IDs must be unique")
        _canonical(
            self.memberships, lambda item: item.query_id, "memberships must be canonically ordered"
        )
        memberships = {item.query_id: item for item in self.memberships}
        if len(memberships) != len(self.memberships) or set(memberships) != set(queries):
            raise ValueError("each query must have exactly one partition membership")
        _canonical(
            self.reviewers,
            lambda item: item.reviewer_key,
            "reviewer roster must be canonically ordered",
        )
        reviewers = {item.reviewer_key: item for item in self.reviewers}
        if len(reviewers) != len(self.reviewers):
            raise ValueError("reviewer roster must be unique")
        if self.protocol.query_digest != _sequence_digest(
            tuple(item.query_digest for item in self.queries)
        ):
            raise ValueError("protocol query digest does not bind queries")
        if self.protocol.reviewer_roster_digest != _sequence_digest(
            tuple(item.reviewer_digest for item in self.reviewers)
        ):
            raise ValueError("protocol reviewer roster does not bind reviewers")
        if self.protocol.partition_digest != _sequence_digest(
            tuple(item.membership_digest for item in self.memberships)
        ):
            raise ValueError("protocol partition digest does not bind memberships")
        manifest = _sequence_digest(
            tuple(f"{item.query_id}:{item.candidate_universe_digest}" for item in self.queries)
        )
        if self.candidate_manifest_digest != manifest:
            raise ValueError("candidate_manifest_digest must bind every query candidate roster")
        for query in self.queries:
            if query.feature_cutoff_ts > self.protocol.decision_cutoff_ts:
                raise ValueError(
                    "query feature cutoff cannot be later than protocol decision cutoff"
                )

        _canonical(
            self.relevance,
            lambda item: (
                item.query_id,
                item.candidate_id,
                item.reviewer_key,
                item.rubric_id,
                item.evidence_id,
            ),
            "relevance must be canonically ordered",
        )
        relevance_ids = {item.evidence_id for item in self.relevance}
        relevance_keys = {
            (item.query_id, item.candidate_id, item.reviewer_key, item.rubric_id)
            for item in self.relevance
        }
        if len(relevance_ids) != len(self.relevance) or len(relevance_keys) != len(self.relevance):
            raise ValueError("relevance requires unique IDs and semantic keys")
        for relevance_item in self.relevance:
            self._validate_reviewed_item(
                relevance_item.query_id,
                relevance_item.candidate_id,
                relevance_item.reviewer_key,
                relevance_item.reviewer_digest,
                relevance_item.rubric_id,
                relevance_item.rubric_digest,
                relevance_item.authority,
                relevance_item.available_at,
                queries,
                memberships,
                reviewers,
            )

        _canonical(
            self.preferences,
            lambda item: (
                item.query_id,
                item.left_candidate_id,
                item.right_candidate_id,
                item.reviewer_key,
                item.rubric_id,
                item.preference_id,
            ),
            "preferences must be canonically ordered",
        )
        preference_ids = {item.preference_id for item in self.preferences}
        preference_keys = {
            (
                item.query_id,
                item.left_candidate_id,
                item.right_candidate_id,
                item.reviewer_key,
                item.rubric_id,
            )
            for item in self.preferences
        }
        if len(preference_ids) != len(self.preferences) or len(preference_keys) != len(
            self.preferences
        ):
            raise ValueError("preferences require unique IDs and semantic keys")
        for preference_item in self.preferences:
            self._validate_reviewed_item(
                preference_item.query_id,
                preference_item.left_candidate_id,
                preference_item.reviewer_key,
                preference_item.reviewer_digest,
                preference_item.rubric_id,
                preference_item.rubric_digest,
                None,
                preference_item.available_at,
                queries,
                memberships,
                reviewers,
            )
            if (
                preference_item.right_candidate_id
                not in queries[preference_item.query_id].candidate_ids
            ):
                raise ValueError("pair candidate absent from frozen universe")

        _canonical(
            self.hard_negatives,
            lambda item: (
                item.query_id,
                item.candidate_id,
                item.rationale_digest,
                item.hard_negative_id,
            ),
            "hard negatives must be canonically ordered",
        )
        hard_ids = {item.hard_negative_id for item in self.hard_negatives}
        hard_keys = {
            (item.query_id, item.candidate_id, item.rationale_digest)
            for item in self.hard_negatives
        }
        if len(hard_ids) != len(self.hard_negatives) or len(hard_keys) != len(self.hard_negatives):
            raise ValueError("hard negatives require unique IDs and semantic keys")
        for hard_negative_item in self.hard_negatives:
            if (
                hard_negative_item.query_id not in queries
                or hard_negative_item.available_at >= self.protocol.decision_cutoff_ts
                or hard_negative_item.candidate_id
                not in queries[hard_negative_item.query_id].candidate_ids
            ):
                raise ValueError("hard-negative must be in the frozen pre-cutoff universe")
            self._validate_reviewed_item(
                hard_negative_item.query_id,
                hard_negative_item.candidate_id,
                hard_negative_item.reviewer_key,
                hard_negative_item.reviewer_digest,
                hard_negative_item.rubric_id,
                hard_negative_item.rubric_digest,
                hard_negative_item.authority,
                hard_negative_item.available_at,
                queries,
                memberships,
                reviewers,
            )

        _canonical(
            self.adjudications,
            lambda item: (
                item.query_id,
                item.candidate_id,
                item.rubric_id,
                item.evidence_ids,
                item.adjudication_id,
            ),
            "adjudications must be canonically ordered",
        )
        adjudication_ids = {item.adjudication_id for item in self.adjudications}
        adjudication_keys = {
            (item.query_id, item.candidate_id, item.rubric_id, item.evidence_ids)
            for item in self.adjudications
        }
        if len(adjudication_ids) != len(self.adjudications) or len(adjudication_keys) != len(
            self.adjudications
        ):
            raise ValueError("adjudications require unique IDs and semantic keys")
        evidence_by_id = {item.evidence_id: item for item in self.relevance}
        for adjudication_item in self.adjudications:
            referenced = tuple(
                evidence_by_id.get(evidence_id) for evidence_id in adjudication_item.evidence_ids
            )
            if None in referenced or adjudication_item.rubric_digest != self.protocol.rubric_digest:
                raise ValueError("adjudication references missing evidence or substituted rubric")
            if any(
                record is None
                or (record.query_id, record.candidate_id, record.rubric_id, record.rubric_digest)
                != (
                    adjudication_item.query_id,
                    adjudication_item.candidate_id,
                    adjudication_item.rubric_id,
                    adjudication_item.rubric_digest,
                )
                for record in referenced
            ):
                raise ValueError("adjudication must concern one query candidate and rubric")
            if len({record.label for record in referenced if record is not None}) < 2:
                raise ValueError("adjudication requires an actual label disagreement")
            adjudicator = reviewers.get(adjudication_item.adjudicator_key)
            if (
                adjudicator is None
                or adjudicator.authority is not ReviewerAuthority.GOVERNED_HUMAN_EXPERT
            ):
                raise ValueError("adjudicator must be a rostered governed human")
        if self.bundle_digest != _digest(self.model_dump(mode="json"), "bundle_digest"):
            raise ValueError("bundle_digest must bind the canonical aggregate")
        return self

    def _validate_reviewed_item(
        self,
        query_id: str,
        candidate_id: str,
        reviewer_key: str,
        reviewer_digest: str,
        rubric_id: str,
        rubric_digest: str,
        authority: EvidenceAuthority | None,
        available_at: datetime,
        queries: dict[str, EvaluationQuery],
        memberships: dict[str, PartitionMembership],
        reviewers: dict[str, ReviewerIdentity],
    ) -> None:
        if (
            query_id not in queries
            or available_at >= self.protocol.decision_cutoff_ts
            or candidate_id not in queries[query_id].candidate_ids
        ):
            raise ValueError("evidence must be in the frozen pre-cutoff universe")
        reviewer = reviewers.get(reviewer_key)
        if reviewer is None or reviewer.reviewer_digest != reviewer_digest:
            raise ValueError("evidence reviewer substitution")
        if (
            rubric_id != self.protocol.rubric.rubric_id
            or rubric_digest != self.protocol.rubric_digest
        ):
            raise ValueError("evidence rubric substitution")
        if authority is not None and authority.value != reviewer.authority.value:
            raise ValueError("evidence authority must bind reviewer authority")
        if (
            memberships[query_id].partition
            in {
                EvaluationPartition.CALIBRATION,
                EvaluationPartition.PROTECTED_TEST,
                EvaluationPartition.PROSPECTIVE,
            }
            and reviewer.authority is not ReviewerAuthority.GOVERNED_HUMAN_EXPERT
        ):
            raise ValueError("governed partition evidence must be governed human")


class EvaluatedQueryRoster(ContractModel):
    query_ids: Annotated[tuple[EvaluationId, ...], Field(min_length=1)]
    evaluated_query_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            len(self.query_ids) != len(set(self.query_ids))
            or tuple(sorted(self.query_ids)) != self.query_ids
        ):
            raise ValueError("evaluated query IDs must be unique and canonically ordered")
        if self.evaluated_query_digest != _sequence_digest(self.query_ids):
            raise ValueError("evaluated query digest must bind canonical evaluated query IDs")
        return self


class MetricResult(ContractModel):
    metric: MetricName
    k: PositiveInt | None = None
    protocol_digest: Sha256Digest
    evaluated_query_digest: Sha256Digest
    input_digest: Sha256Digest
    value: FiniteFloat | None = None
    numerator: FiniteFloat | None = None
    denominator: FiniteFloat | None = None
    status: MetricStatus
    reason: NonEmptyString | None = None
    result_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        computed = self.status is MetricStatus.COMPUTED
        if computed != (
            self.value is not None and self.numerator is not None and self.denominator is not None
        ):
            raise ValueError("computed metrics require value and sufficient statistics")
        if computed:
            if not (
                self.value is not None
                and self.numerator is not None
                and self.denominator is not None
            ):
                raise ValueError("computed metrics require value and sufficient statistics")
            if self.reason is not None:
                raise ValueError("computed metrics cannot retain an unavailable reason")
            if self.numerator < 0.0 or self.denominator <= 0.0:
                raise ValueError(
                    "computed metric sufficient statistics must be non-negative with positive denominator"
                )
            if self.value != self.numerator / self.denominator:
                raise ValueError(
                    "computed metric value must equal numerator divided by denominator"
                )
            if not 0.0 <= self.value <= 1.0:
                raise ValueError("unit metric value must be within [0, 1]")
        if not computed and (
            self.value is not None
            or self.numerator is not None
            or self.denominator is not None
            or self.reason is None
        ):
            raise ValueError("unavailable metrics retain a reason and no invented value")
        if self.result_digest != _digest(self.model_dump(mode="json"), "result_digest"):
            raise ValueError("result_digest must match canonical payload")
        return self


class EvaluationAccessRecord(ContractModel):
    access_id: EvaluationId
    protocol_digest: Sha256Digest
    bundle_digest: Sha256Digest
    candidate_manifest_digest: Sha256Digest
    evaluated_queries: EvaluatedQueryRoster
    evaluated_query_digest: Sha256Digest
    partition: EvaluationPartition
    accessor_key: EvaluationId
    purpose: NonEmptyString
    accessed_at: UtcInstant
    one_use: Literal[True]
    consumed_by_run_id: EvaluationId
    access_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.evaluated_query_digest != self.evaluated_queries.evaluated_query_digest:
            raise ValueError("access evaluated query digest must bind evaluated query roster")
        if self.access_digest != _digest(self.model_dump(mode="json"), "access_digest"):
            raise ValueError("access_digest must match canonical payload")
        return self


class BootstrapInterval(ContractModel):
    metric_result_digest: Sha256Digest
    protocol_digest: Sha256Digest
    evaluated_query_digest: Sha256Digest
    input_digest: Sha256Digest
    point_value: FiniteFloat | None = None
    resample_digest: Sha256Digest | None = None
    seed: NonNegativeInt
    resamples: PositiveInt
    confidence: FiniteFloat
    method: BootstrapMethod
    lower: FiniteFloat | None = None
    upper: FiniteFloat | None = None
    status: MetricStatus
    reason: NonEmptyString | None = None
    interval_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        computed = self.status is MetricStatus.COMPUTED
        if computed != (
            self.point_value is not None
            and self.resample_digest is not None
            and self.lower is not None
            and self.upper is not None
        ):
            raise ValueError("computed interval requires point, resample identity and bounds")
        if computed:
            if not (
                self.lower is not None and self.point_value is not None and self.upper is not None
            ):
                raise ValueError("computed interval requires point, resample identity and bounds")
            if self.reason is not None:
                raise ValueError("computed intervals cannot retain an unavailable reason")
            if not self.lower <= self.point_value <= self.upper:
                raise ValueError("interval bounds must contain the point value")
            if not 0.0 <= self.lower <= self.upper <= 1.0:
                raise ValueError("unit metric interval bounds must be within [0, 1]")
        if not computed and (
            self.point_value is not None
            or self.resample_digest is not None
            or self.lower is not None
            or self.upper is not None
            or self.reason is None
        ):
            raise ValueError("unavailable interval retains a reason and no bounds")
        if not 0.0 < self.confidence < 1.0:
            raise ValueError("confidence must be strictly between zero and one")
        if self.interval_digest != _digest(self.model_dump(mode="json"), "interval_digest"):
            raise ValueError("interval_digest must match canonical payload")
        return self


class RankComparisonResult(ContractModel):
    protocol_digest: Sha256Digest
    evaluated_query_digest: Sha256Digest
    k: PositiveInt
    left_input_digest: Sha256Digest
    right_input_digest: Sha256Digest
    spearman: FiniteFloat | None = None
    overlap_count: NonNegativeInt | None = None
    overlap_rate: FiniteFloat | None = None
    jaccard: FiniteFloat | None = None
    candidate_churn: FiniteFloat | None = None
    disagreements: tuple[EvaluationId, ...] = ()
    reason: NonEmptyString | None = None
    result_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.spearman is not None and not -1.0 <= self.spearman <= 1.0:
            raise ValueError("Spearman correlation must be within [-1, 1]")
        if self.spearman is None and self.reason is None:
            raise ValueError("unavailable rank comparison requires a reason")
        if self.spearman is not None and self.reason is not None:
            raise ValueError("computed rank comparison cannot retain an unavailable reason")
        set_metrics = (self.overlap_count, self.overlap_rate, self.jaccard, self.candidate_churn)
        if any(value is None for value in set_metrics) != all(
            value is None for value in set_metrics
        ):
            raise ValueError("rank comparison set metrics must be present or absent together")
        if self.spearman is not None and self.overlap_count is None:
            raise ValueError("computed Spearman requires top-k set metrics")
        if self.overlap_count is not None:
            if not (
                self.overlap_rate is not None
                and self.jaccard is not None
                and self.candidate_churn is not None
            ):
                raise ValueError("rank comparison set metrics must be present or absent together")
            if self.overlap_count > self.k:
                raise ValueError("rank comparison overlap cannot exceed k")
            expected_rate = self.overlap_count / self.k
            if self.overlap_rate != expected_rate or self.candidate_churn != 1.0 - expected_rate:
                raise ValueError(
                    "rank comparison overlap rate and churn must match overlap arithmetic"
                )
            if self.jaccard != self.overlap_count / (2 * self.k - self.overlap_count):
                raise ValueError("rank comparison Jaccard must match top-k overlap arithmetic")
            if len(self.disagreements) != 2 * (self.k - self.overlap_count):
                raise ValueError(
                    "rank comparison disagreements must match top-k overlap arithmetic"
                )
        elif self.disagreements:
            raise ValueError("rank comparison without set metrics cannot retain disagreements")
        if (
            len(self.disagreements) != len(set(self.disagreements))
            or tuple(sorted(self.disagreements)) != self.disagreements
        ):
            raise ValueError("rank comparison disagreements must be canonically unique")
        if self.result_digest != _digest(self.model_dump(mode="json"), "result_digest"):
            raise ValueError("rank comparison result_digest must match canonical payload")
        return self


class SliceResult(ContractModel):
    slice_id: EvaluationId
    definition_digest: Sha256Digest
    metric_results: tuple[MetricResult, ...]
    status: MetricStatus
    reason: NonEmptyString | None = None
    slice_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.status is MetricStatus.COMPUTED and not self.metric_results:
            raise ValueError("computed slice requires metric results")
        _canonical(
            self.metric_results,
            lambda item: (item.metric.value, item.k or 0),
            "slice metric results must be canonically ordered",
        )
        if len({(item.metric, item.k) for item in self.metric_results}) != len(self.metric_results):
            raise ValueError("slice metric results must be semantically unique")
        if self.status is not MetricStatus.COMPUTED and self.reason is None:
            raise ValueError("unavailable slice requires a reason")
        if self.slice_digest != _digest(self.model_dump(mode="json"), "slice_digest"):
            raise ValueError("slice_digest must match canonical payload")
        return self


class FailureResult(ContractModel):
    failure_id: EvaluationId
    query_id: EvaluationId
    category: NonEmptyString
    evidence_digest: Sha256Digest
    failure_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.failure_digest != _digest(self.model_dump(mode="json"), "failure_digest"):
            raise ValueError("failure_digest must match canonical payload")
        return self


class EvaluationRun(ContractModel):
    run_id: EvaluationId
    protocol: EvaluationProtocol
    access: EvaluationAccessRecord
    bundle_digest: Sha256Digest
    candidate_manifest_digest: Sha256Digest
    evaluated_queries: EvaluatedQueryRoster
    evaluated_query_digest: Sha256Digest
    partition: EvaluationPartition
    metric_results: Annotated[tuple[MetricResult, ...], Field(min_length=1)]
    intervals: tuple[BootstrapInterval, ...] = ()
    slices: tuple[SliceResult, ...] = ()
    failures: tuple[FailureResult, ...] = ()
    run_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        access = self.access
        if (
            access.protocol_digest,
            access.bundle_digest,
            access.candidate_manifest_digest,
            access.partition,
            access.consumed_by_run_id,
            access.evaluated_query_digest,
        ) != (
            self.protocol.protocol_digest,
            self.bundle_digest,
            self.candidate_manifest_digest,
            self.partition,
            self.run_id,
            self.evaluated_query_digest,
        ):
            raise ValueError(
                "access must be consumed by this exact protocol bundle candidate roster and run"
            )
        if (
            self.evaluated_query_digest != self.evaluated_queries.evaluated_query_digest
            or self.evaluated_queries != access.evaluated_queries
        ):
            raise ValueError("run evaluated query roster must exactly equal consumed access roster")
        _canonical(
            self.metric_results,
            lambda item: (item.metric.value, item.k or 0),
            "metric results must be canonically ordered",
        )
        result_keys = {(item.metric, item.k) for item in self.metric_results}
        if len(result_keys) != len(self.metric_results):
            raise ValueError("metric results must be semantically unique")
        roster = set(self.protocol.primary_metrics + self.protocol.secondary_metrics)
        for metric_result in self.metric_results:
            if metric_result.metric not in roster:
                raise ValueError("result metric is absent from protocol roster")
            if (metric_result.metric in _RANK_METRICS) != (metric_result.k is not None):
                raise ValueError("rank metrics require k and non-rank metrics forbid k")
            if metric_result.k is not None and metric_result.k not in self.protocol.declared_k:
                raise ValueError("result k is absent from protocol")
            if metric_result.evaluated_query_digest != self.evaluated_query_digest:
                raise ValueError("result must bind the run evaluated query population")
            if metric_result.protocol_digest != self.protocol.protocol_digest:
                raise ValueError("result must bind the run protocol")
        _canonical(
            self.intervals,
            lambda item: item.metric_result_digest,
            "intervals must be canonically ordered",
        )
        result_by_digest = {item.result_digest: item for item in self.metric_results}
        if len({item.metric_result_digest for item in self.intervals}) != len(self.intervals):
            raise ValueError("intervals must be unique per result")
        for interval in self.intervals:
            linked_result = result_by_digest.get(interval.metric_result_digest)
            if linked_result is None:
                raise ValueError("interval must reference a present result")
            if interval.evaluated_query_digest != self.evaluated_query_digest:
                raise ValueError("interval must bind the run evaluated query population")
            if interval.protocol_digest != self.protocol.protocol_digest:
                raise ValueError("interval must bind the run protocol")
            if interval.input_digest != linked_result.input_digest:
                raise ValueError("interval must bind the result input lineage")
            if (interval.seed, interval.resamples, interval.confidence, interval.method) != (
                self.protocol.bootstrap_seed,
                self.protocol.bootstrap_resamples,
                self.protocol.bootstrap_confidence,
                self.protocol.bootstrap_method,
            ):
                raise ValueError("interval settings must match protocol")
            if linked_result.metric not in _BOOTSTRAP_METRICS:
                raise ValueError("protocol does not support bootstrap for this metric")
            if interval.status is MetricStatus.COMPUTED and (
                linked_result.status is not MetricStatus.COMPUTED
                or interval.point_value != linked_result.value
            ):
                raise ValueError("computed interval must bind computed result point value")
        _canonical(self.slices, lambda item: item.slice_id, "slices must be canonically ordered")
        if (
            len({item.slice_id for item in self.slices}) != len(self.slices)
            or len({item.slice_digest for item in self.slices}) != len(self.slices)
            or len({(item.slice_id, item.definition_digest) for item in self.slices})
            != len(self.slices)
        ):
            raise ValueError("slices require unique IDs, digests and semantic keys")
        for slice_result in self.slices:
            if any(
                metric_result.evaluated_query_digest != self.evaluated_query_digest
                for metric_result in slice_result.metric_results
            ):
                raise ValueError(
                    "slice metric results must bind the run evaluated query population"
                )
            if any(
                metric_result.protocol_digest != self.protocol.protocol_digest
                for metric_result in slice_result.metric_results
            ):
                raise ValueError("slice metric results must bind the run protocol")
        _canonical(
            self.failures, lambda item: item.failure_id, "failures must be canonically ordered"
        )
        if (
            len({item.failure_id for item in self.failures}) != len(self.failures)
            or len({item.failure_digest for item in self.failures}) != len(self.failures)
            or len({(item.query_id, item.category, item.evidence_digest) for item in self.failures})
            != len(self.failures)
        ):
            raise ValueError("failures require unique IDs, digests and semantic keys")
        if any(
            failure.query_id not in self.evaluated_queries.query_ids for failure in self.failures
        ):
            raise ValueError("failure query must belong to the run evaluated query population")
        if self.run_digest != _digest(self.model_dump(mode="json"), "run_digest"):
            raise ValueError("run_digest must match canonical payload")
        return self


class FrozenW05Candidate(ContractModel):
    """The content-addressed W05 candidate that W06 is permitted to assess."""

    selected_family: Literal["role_aware_restriction"]
    artifact_id: NonEmptyString
    manifest_digest: Sha256Digest
    configuration_digest: Sha256Digest
    taxonomy_digest: Sha256Digest
    feature_registry_digest: Sha256Digest
    feature_schema_hash: Sha256Digest
    accepted_result_digest: Sha256Digest
    lineage_hash: Sha256Digest
    candidate_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.candidate_digest != _digest(self.model_dump(mode="json"), "candidate_digest"):
            raise ValueError("candidate_digest must match canonical payload")
        return self


class FrozenProtectedProtocol(ContractModel):
    """The conservative W06 protocol, frozen before a broker can be invoked."""

    claim_boundary: Literal["resemblance_only"]
    evidence_boundary: Literal["GOVERNED_HUMAN_EXPERT_REQUIRED"]
    protected_partition: Literal["PROTECTED_TEST"]
    primary_metric: Literal["ndcg@10"]
    secondary_metrics: tuple[NonEmptyString, ...]
    explicitly_unsupported_k: tuple[NonEmptyString, ...]
    baselines: tuple[NonEmptyString, ...]
    nulls: tuple[NonEmptyString, ...]
    bootstrap_seed: Literal[20260804]
    bootstrap_resamples: Literal[2000]
    bootstrap_confidence: FiniteFloat
    bootstrap_method: Literal["percentile"]
    minimum_useful_effect: Literal["ndcg@10_delta_vs_best_control>=0.05;lower>0.0"]
    fail_closed_order: tuple[NonEmptyString, ...]
    stop_rule: NonEmptyString
    protocol_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            self.secondary_metrics
            != (
                "precision@5",
                "precision@10",
                "recall@5",
                "recall@10",
                "ndcg@5",
                "coverage@5",
                "coverage@10",
                "pair_preference",
                "agreement_when_multiple_real_reviewers_exist",
            )
            or self.explicitly_unsupported_k != ("k=25:W05_CANDIDATE_UNIVERSE_HAS_18_MEMBERS",)
            or self.baselines != ("metadata", "raw_euclidean")
            or self.nulls != ("shuffled_label", "shuffled_pair_when_governed_pair_evidence_exists")
            or self.bootstrap_confidence != 0.95
            or self.fail_closed_order
            != (
                "AUTHENTIC_GOVERNED_EXPERT_EVIDENCE",
                "NONEMPTY_PROTECTED_POPULATION",
                "VALID_PARTITION_ACCESS",
                "TEMPORAL_AND_SOURCE_LINEAGE",
                "PRIMARY_EFFECT_AND_INTERVAL",
                "NULL_CONTROLS",
                "MANDATORY_SLICES_AND_APPLICABILITY",
                "UNCHANGED_EXPLANATION_AND_SERVING_PARITY",
            )
            or self.stop_rule
            != (
                "The first failed prerequisite yields NO_GO; no protected outputs are opened "
                "when governed expert evidence or a protected population is absent, and no "
                "retuning or rerun is permitted after the one-use broker invocation."
            )
        ):
            raise ValueError("frozen protocol roster substitution")
        if self.protocol_digest != _digest(self.model_dump(mode="json"), "protocol_digest"):
            raise ValueError("protocol_digest must match canonical payload")
        return self


class GovernedEvidenceInventory(ContractModel):
    """Retained negative evidence; this is deliberately not an EvaluationBundle."""

    authentic_governed_human_relevance_reviewers: Literal[0]
    governed_relevance_judgements: Literal[0]
    governed_pair_preferences: Literal[0]
    protected_queries: Literal[0]
    missing_evidence: tuple[
        Literal["MISSING_EXPERT_RELEVANCE_EVIDENCE", "MISSING_PROTECTED_POPULATION"], ...
    ]
    inventory_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.missing_evidence != (
            "MISSING_EXPERT_RELEVANCE_EVIDENCE",
            "MISSING_PROTECTED_POPULATION",
        ):
            raise ValueError("missing evidence must retain the exact frozen negative inventory")
        if self.inventory_digest != _digest(self.model_dump(mode="json"), "inventory_digest"):
            raise ValueError("inventory_digest must match canonical payload")
        return self


class FrozenProtectedPreregistration(ContractModel):
    schema_version: SchemaVersion = 1
    preregistration_id: Literal["w06-protected-preregistration-v1"]
    candidate: FrozenW05Candidate
    protocol: FrozenProtectedProtocol
    evidence_inventory: GovernedEvidenceInventory
    preregistration_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            self.candidate.selected_family,
            self.candidate.artifact_id,
            self.candidate.manifest_digest,
            self.candidate.configuration_digest,
            self.candidate.taxonomy_digest,
            self.candidate.feature_registry_digest,
            self.candidate.feature_schema_hash,
            self.candidate.accepted_result_digest,
            self.candidate.lineage_hash,
        ) != (
            "role_aware_restriction",
            "9a0d43c6-d177-51be-8280-3bf02bedbc99",
            "2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9",
            "5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a",
            "59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097",
            "c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644",
            "1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f",
            "9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e",
            "c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491",
        ):
            raise ValueError("exact W05 candidate identity required")
        if self.preregistration_digest != _digest(
            self.model_dump(mode="json"), "preregistration_digest"
        ):
            raise ValueError("preregistration_digest must match canonical payload")
        return self


class ProtectedAccessOutcome(ContractModel):
    preregistration_digest: Sha256Digest
    candidate_digest: Sha256Digest
    inventory_digest: Sha256Digest
    outcome: Literal[ProtectedAccessOutcomeKind.NOT_ACCESSED_MISSING_POPULATION]
    protected_outputs_opened: Literal[False]
    outcome_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.outcome_digest != _digest(self.model_dump(mode="json"), "outcome_digest"):
            raise ValueError("outcome_digest must match canonical payload")
        return self


class ProtectedGateExecutionReceipt(ContractModel):
    invocation_id: EvaluationId
    preregistration_digest: Sha256Digest
    candidate_digest: Sha256Digest
    access_outcome_digest: Sha256Digest
    gate_digest: Sha256Digest
    access_outcome_file_digest: Sha256Digest
    gate_decision_file_digest: Sha256Digest
    receipt_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.receipt_digest != _digest(self.model_dump(mode="json"), "receipt_digest"):
            raise ValueError("receipt_digest must match canonical payload")
        return self


class GateDecision(ContractModel):
    gate_id: EvaluationId
    decision: GateDecisionKind
    protocol: EvaluationProtocol | FrozenProtectedProtocol
    bundle: EvaluationBundle | None = None
    run: EvaluationRun | None = None
    claim_boundary: Literal["resemblance_only"]
    reason_codes: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    gate_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        requires_evaluation = self.decision in {
            GateDecisionKind.ACCEPT_CLAIM,
            GateDecisionKind.NARROW_APPLICABILITY,
        }
        has_complete_evaluation = self.bundle is not None and self.run is not None
        if requires_evaluation and not has_complete_evaluation:
            raise ValueError("claim and narrowing decisions require an actual bundle and run")
        if not requires_evaluation and (self.bundle is None) != (self.run is None):
            raise ValueError("NO_GO must retain neither object or both linked bundle and run")
        if self.decision is GateDecisionKind.NO_GO and not has_complete_evaluation:
            if len(self.reason_codes) != 1 or self.reason_codes[0] not in {
                reason.value for reason in NoGoReason
            }:
                raise ValueError(
                    "missing-population NO_GO requires one explicit missing-evidence reason"
                )
        if self.run is not None and self.bundle is not None:
            if not isinstance(self.protocol, EvaluationProtocol):
                raise ValueError("frozen missing-population protocol cannot retain a bundle or run")
            if (
                self.bundle.protocol.protocol_digest,
                self.run.protocol.protocol_digest,
                self.run.bundle_digest,
                self.run.candidate_manifest_digest,
                self.run.partition,
            ) != (
                self.protocol.protocol_digest,
                self.protocol.protocol_digest,
                self.bundle.bundle_digest,
                self.bundle.candidate_manifest_digest,
                EvaluationPartition.PROTECTED_TEST,
            ):
                raise ValueError("gate run must bind this protected protocol and bundle")
            self._validate_evaluated_population(self.bundle, self.run)
            if self.decision in {
                GateDecisionKind.ACCEPT_CLAIM,
                GateDecisionKind.NARROW_APPLICABILITY,
            }:
                if not self._has_governed_human_evidence(self.bundle, self.run.evaluated_queries):
                    raise ValueError(
                        "claim or narrowing requires governed evidence for every evaluated protected query"
                    )
                required = {
                    (metric, k)
                    for metric in self.protocol.primary_metrics
                    for k in (self.protocol.declared_k if metric in _RANK_METRICS else (None,))
                }
                results = {(result.metric, result.k): result for result in self.run.metric_results}
                if set(results) < required or any(
                    results[key].status is not MetricStatus.COMPUTED for key in required
                ):
                    raise ValueError("claim or narrowing requires every primary result computed")
                intervals = {
                    interval.metric_result_digest: interval for interval in self.run.intervals
                }
                if any(
                    (interval := intervals.get(results[key].result_digest)) is None
                    or interval.status is not MetricStatus.COMPUTED
                    for key in required
                ):
                    raise ValueError("claim or narrowing requires every primary interval computed")
        if self.gate_digest != _digest(self.model_dump(mode="json"), "gate_digest"):
            raise ValueError("gate_digest must match canonical payload")
        return self

    @staticmethod
    def _validate_evaluated_population(bundle: EvaluationBundle, run: EvaluationRun) -> None:
        membership_by_query = {
            membership.query_id: membership.partition for membership in bundle.memberships
        }
        selected = set(run.evaluated_queries.query_ids)
        protected = {
            query_id
            for query_id, partition in membership_by_query.items()
            if partition is EvaluationPartition.PROTECTED_TEST
        }
        if selected != protected or any(
            membership_by_query.get(query_id) is not run.partition for query_id in selected
        ):
            raise ValueError(
                "evaluated query roster must exactly cover the protected bundle population"
            )

    @staticmethod
    def _has_governed_human_evidence(
        bundle: EvaluationBundle, roster: EvaluatedQueryRoster
    ) -> bool:
        evidence_by_query: dict[str, list[EvaluationEvidence]] = {
            query_id: [] for query_id in roster.query_ids
        }
        for evidence in bundle.relevance:
            if evidence.query_id in evidence_by_query:
                evidence_by_query[evidence.query_id].append(evidence)
        return all(
            rows
            and all(
                row.authority is EvidenceAuthority.GOVERNED_HUMAN_EXPERT
                and row.label is not RelevanceLabel.ABSTAIN
                for row in rows
            )
            for rows in evidence_by_query.values()
        )


class RankedObservation(ContractModel):
    """A complete score-ordered, labelled ranking embedded in robustness evidence."""

    row_id: EvaluationId
    query_id: EvaluationId
    candidate_ids: Annotated[tuple[EvaluationId, ...], Field(min_length=1)]
    scores: Annotated[tuple[FiniteFloat, ...], Field(min_length=1)]
    labels: Annotated[tuple[RelevanceLabel, ...], Field(min_length=1)]
    ranking_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            len(self.candidate_ids) != len(self.scores)
            or len(self.candidate_ids) != len(self.labels)
            or len(self.candidate_ids) != len(set(self.candidate_ids))
        ):
            raise ValueError("ranked observation requires complete unique candidate evidence")
        ordered = tuple(
            sorted(
                zip(self.candidate_ids, self.scores, self.labels, strict=True),
                key=lambda item: (-item[1], item[0]),
            )
        )
        if ordered != tuple(zip(self.candidate_ids, self.scores, self.labels, strict=True)):
            raise ValueError("ranked observation must retain score-desc candidate-ID order")
        if any(label is RelevanceLabel.ABSTAIN for label in self.labels):
            raise ValueError("fixture ranking labels must be concrete")
        if self.ranking_digest != _digest(self.model_dump(mode="json"), "ranking_digest"):
            raise ValueError("ranking_digest must bind exact ranked observation")
        return self


class DeficitKind(StrEnum):
    PER_UNIT_OBSERVATIONS = "PER_UNIT_OBSERVATIONS"
    DISTINCT_WINDOWS = "DISTINCT_WINDOWS"
    THRESHOLD_OBSERVATIONS = "THRESHOLD_OBSERVATIONS"
    DISTINCT_GROUPS = "DISTINCT_GROUPS"
    PROVIDER_INTERSECTION = "PROVIDER_INTERSECTION"
    WALK_FORWARD_PARTITION = "WALK_FORWARD_PARTITION"
    GOVERNED_PAIR_EVIDENCE = "GOVERNED_PAIR_EVIDENCE"
    INCOHERENT_LABEL_EVIDENCE = "INCOHERENT_LABEL_EVIDENCE"
    INSUFFICIENT_COMMON_CANDIDATES = "INSUFFICIENT_COMMON_CANDIDATES"


class PopulationDeficit(ContractModel):
    kind: DeficitKind
    scope: NonEmptyString
    observed: NonNegativeInt
    required: PositiveInt
    deficit_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.observed >= self.required:
            raise ValueError("typed deficit requires an unmet observed population")
        if self.deficit_digest != _digest(self.model_dump(mode="json"), "deficit_digest"):
            raise ValueError("deficit digest must bind typed evidence")
        return self


class GovernedPopulationMember(ContractModel):
    """One immutable ranking observation in a governed robustness population.

    ``query_id`` names the evaluated unit.  It deliberately need not be unique: a
    stress experiment can only prove a split/window transformation when it retains
    multiple independently identified observations for that unit.
    """

    observation_id: EvaluationId
    query_id: EvaluationId
    competition_id: EvaluationId
    team_id: EvaluationId
    provider_id: EvaluationId
    window_id: EvaluationId
    chronological_index: NonNegativeInt
    minutes: NonNegativeInt
    authority: EvidenceAuthority
    ranking: RankedObservation
    member_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.ranking.query_id != self.query_id:
            raise ValueError("population ranking must bind its evaluated query")
        if self.member_digest != _digest(self.model_dump(mode="json"), "member_digest"):
            raise ValueError("population member_digest must match canonical payload")
        return self

    @property
    def candidate_ids(self) -> tuple[EvaluationId, ...]:
        return tuple(sorted(self.ranking.candidate_ids))


class GovernedPopulationInventory(ContractModel):
    protocol_digest: Sha256Digest
    members: Annotated[tuple[GovernedPopulationMember, ...], Field(min_length=1)]
    inventory_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        _canonical(
            self.members,
            lambda item: (item.query_id, item.observation_id),
            "population members must be canonically ordered",
        )
        if len({item.observation_id for item in self.members}) != len(self.members):
            raise ValueError("population observations require unique IDs")
        window_indexes: dict[str, int] = {}
        for member in self.members:
            previous = window_indexes.setdefault(member.window_id, member.chronological_index)
            if previous != member.chronological_index:
                raise ValueError("each canonical window must have exactly one chronology index")
        if len(window_indexes) != len(set(window_indexes.values())):
            raise ValueError("distinct canonical windows require distinct chronology indexes")
        if self.inventory_digest != _digest(self.model_dump(mode="json"), "inventory_digest"):
            raise ValueError("population inventory_digest must match canonical payload")
        return self


class StressTestSpecification(ContractModel):
    test_id: EvaluationId
    kind: StressTestKind
    protocol: EvaluationProtocol
    inventory: GovernedPopulationInventory
    metric: MetricName
    k: PositiveInt
    thresholds: tuple[PositiveInt, ...] = ()
    walk_forward_cutoff_index: NonNegativeInt | None = None
    specification_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.inventory.protocol_digest != self.protocol.protocol_digest:
            raise ValueError("stress inventory must bind the embedded exact protocol")
        if self.metric not in _RANK_METRICS:
            raise ValueError("stress tests require a supported ranking metric")
        if self.metric not in set(self.protocol.primary_metrics + self.protocol.secondary_metrics):
            raise ValueError("stress metric must be in the embedded protocol roster")
        if self.k not in self.protocol.declared_k:
            raise ValueError("stress k must be declared by the embedded protocol")
        if self.kind is StressTestKind.MINUTES_SAMPLE_SENSITIVITY:
            if (
                len(self.thresholds) < 2
                or tuple(sorted(self.thresholds)) != self.thresholds
                or len(set(self.thresholds)) != len(self.thresholds)
            ):
                raise ValueError("minutes sensitivity requires two ordered unique thresholds")
        elif self.thresholds:
            raise ValueError("only minutes sensitivity may declare thresholds")
        indexes = {member.chronological_index for member in self.inventory.members}
        if self.kind is StressTestKind.TIME_WALK_FORWARD:
            if (
                self.walk_forward_cutoff_index is None
                or self.walk_forward_cutoff_index not in indexes
            ):
                raise ValueError("walk-forward requires an embedded declared cutoff index")
            if not any(index > self.walk_forward_cutoff_index for index in indexes):
                raise ValueError("walk-forward cutoff requires a later test population")
        elif self.walk_forward_cutoff_index is not None:
            raise ValueError("only walk-forward may declare a cutoff index")
        if self.specification_digest != _digest(
            self.model_dump(mode="json"), "specification_digest"
        ):
            raise ValueError("stress specification_digest must match canonical payload")
        return self

    @property
    def protocol_digest(self) -> Sha256Digest:
        return self.protocol.protocol_digest

    @property
    def inventory_digest(self) -> Sha256Digest:
        return self.inventory.inventory_digest


def _payload_digest(payload: object) -> Sha256Digest:
    """Digest the accepted-core JSON payload without wrapping it in a contract."""
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    ).hexdigest()


def ranked_observation_metric_input_digest(row: RankedObservation, k: int) -> Sha256Digest:
    """The exact accepted-core per-query ranking metric input identity."""
    return _payload_digest(
        {
            "row": {
                "query_id": row.query_id,
                "candidate_universe": tuple(sorted(row.candidate_ids)),
                "items": tuple(zip(row.candidate_ids, row.scores, row.labels, strict=True)),
            },
            "k": k,
        }
    )


def aggregate_metric_input_digest(
    rows: tuple[RankedObservation, ...],
    per_query_results: tuple[MetricResult, ...],
    metric: MetricName,
    k: int,
) -> Sha256Digest:
    """The exact accepted-core aggregate/bootstrap input identity."""
    return _payload_digest(
        {
            "query_metric_digests": tuple(result.result_digest for result in per_query_results),
            "rows": tuple(
                {
                    "query_id": row.query_id,
                    "candidate_universe": tuple(sorted(row.candidate_ids)),
                    "items": tuple(zip(row.candidate_ids, row.scores, row.labels, strict=True)),
                }
                for row in rows
            ),
            "metric": metric.value,
            "k": k,
        }
    )


def ranking_input_digest(query_id: str, ranking: tuple[str, ...]) -> Sha256Digest:
    return _payload_digest({"query_id": query_id, "ranking": ranking})


def derived_ranking(row: RankedObservation, candidates: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(candidate for candidate in row.candidate_ids if candidate in set(candidates))


def derive_cohort_ranked_rows(
    specification: StressTestSpecification,
    cohort_id: str,
    observation_ids: tuple[str, ...],
) -> tuple[RankedObservation, ...]:
    """Aggregate exactly the inventory observations named by a cohort."""
    members_by_id = {member.observation_id: member for member in specification.inventory.members}
    members = tuple(members_by_id[observation_id] for observation_id in observation_ids)
    grouped: dict[str, list[GovernedPopulationMember]] = {}
    for member in members:
        grouped.setdefault(member.query_id, []).append(member)
    rows: list[RankedObservation] = []
    for query_id in sorted(grouped):
        rankings = [member.ranking for member in grouped[query_id]]
        common = set(rankings[0].candidate_ids)
        for ranking in rankings[1:]:
            common &= set(ranking.candidate_ids)
        if len(common) < specification.k:
            raise ValueError(
                f"query={query_id}:common_candidate_count={len(common)}<{specification.k}"
            )
        values: list[tuple[str, float, RelevanceLabel]] = []
        for candidate in sorted(common):
            found = [
                next(
                    zip_item
                    for zip_item in zip(
                        ranking.candidate_ids, ranking.scores, ranking.labels, strict=True
                    )
                    if zip_item[0] == candidate
                )
                for ranking in rankings
            ]
            if len({item[2] for item in found}) != 1:
                raise ValueError(f"query={query_id}:incoherent_label")
            values.append((candidate, sum(item[1] for item in found) / len(found), found[0][2]))
        ordered = tuple(sorted(values, key=lambda item: (-item[1], item[0])))
        payload: dict[str, Any] = {
            "row_id": f"{cohort_id}-{query_id}",
            "query_id": query_id,
            "candidate_ids": tuple(item[0] for item in ordered),
            "scores": tuple(item[1] for item in ordered),
            "labels": tuple(item[2] for item in ordered),
        }
        payload["ranking_digest"] = _digest(payload, "ranking_digest")
        rows.append(RankedObservation(**payload))
    return tuple(rows)


def derive_label_null_rows(
    rows: tuple[RankedObservation, ...], seed: int
) -> tuple[RankedObservation, ...]:
    """Deterministically shuffle labels only; scores/candidate order remain frozen."""

    output: list[RankedObservation] = []
    for row in rows:
        labels = list(row.labels)
        # Deterministic statistical shuffled-null PRNG; never security or credential randomness.
        random.Random(f"{seed}:{row.query_id}").shuffle(labels)  # nosec B311
        payload: dict[str, Any] = {
            "row_id": f"{row.row_id}-label-null",
            "query_id": row.query_id,
            "candidate_ids": row.candidate_ids,
            "scores": row.scores,
            "labels": tuple(labels),
        }
        payload["ranking_digest"] = _digest(payload, "ranking_digest")
        output.append(RankedObservation(**payload))
    return tuple(output)


def derive_label_permutation(rows: tuple[RankedObservation, ...], seed: int) -> tuple[str, ...]:

    values: list[str] = []
    for row in rows:
        source = list(row.candidate_ids)
        # Deterministic statistical shuffled-null PRNG; never security or credential randomness.
        random.Random(f"{seed}:{row.query_id}").shuffle(source)  # nosec B311
        values.extend(
            f"{row.query_id}|{candidate}|{source[index]}"
            for index, candidate in enumerate(row.candidate_ids)
        )
    return tuple(values)


def _derived_contract[ContractT: ContractModel](
    cls: type[ContractT], payload: dict[str, Any], digest_name: str
) -> ContractT:
    draft = cls.model_construct(**payload)
    payload[digest_name] = _digest(draft.model_dump(mode="json"), digest_name)
    return cls(**payload)


def derive_rank_comparison(
    protocol: EvaluationProtocol,
    query_id: str,
    left: tuple[str, ...],
    right: tuple[str, ...],
    k: int,
) -> RankComparisonResult:
    """Derive the entire persisted comparison value from ordered rankings."""
    if k < 1 or len(left) != len(set(left)) or len(right) != len(set(right)):
        raise ValueError("rankings must be unique and k positive")
    payload: dict[str, Any] = {
        "protocol_digest": protocol.protocol_digest,
        "evaluated_query_digest": _sequence_digest((query_id,)),
        "k": k,
        "left_input_digest": ranking_input_digest(query_id, left),
        "right_input_digest": ranking_input_digest(query_id, right),
    }
    if len(left) < k or len(right) < k:
        payload.update({"reason": "candidate_universe_smaller_than_k"})
        return _derived_contract(RankComparisonResult, payload, "result_digest")
    left_top, right_top = set(left[:k]), set(right[:k])
    overlap = left_top & right_top
    overlap_count = len(overlap)
    payload.update(
        {
            "overlap_count": overlap_count,
            "overlap_rate": overlap_count / k,
            "jaccard": overlap_count / len(left_top | right_top),
            "candidate_churn": 1.0 - overlap_count / k,
            "disagreements": tuple(sorted(left_top ^ right_top)),
        }
    )
    common = sorted(set(left) & set(right))
    if len(common) < 2:
        payload.update({"reason": "insufficient_correlation_intersection"})
        return _derived_contract(RankComparisonResult, payload, "result_digest")
    left_rank = {item: index for index, item in enumerate(item for item in left if item in common)}
    right_rank = {
        item: index for index, item in enumerate(item for item in right if item in common)
    }
    count = len(common)
    payload["spearman"] = 1 - 6 * sum(
        (left_rank[item] - right_rank[item]) ** 2 for item in common
    ) / (count * (count * count - 1))
    return _derived_contract(RankComparisonResult, payload, "result_digest")


def derive_ranking_metric_children(
    protocol: EvaluationProtocol,
    rows: tuple[RankedObservation, ...],
    metric: MetricName,
    k: int,
) -> tuple[tuple[MetricResult, ...], MetricResult, BootstrapInterval]:
    """Adapt persisted rows to the shared dependency-free calculation authority."""
    calculation = _calculate_ranking_metric_children(
        protocol_digest=protocol.protocol_digest,
        declared_k=protocol.declared_k,
        partial_gain=protocol.partial_gain,
        partial_counts_for_precision_recall=protocol.partial_counts_for_precision_recall,
        bootstrap_seed=protocol.bootstrap_seed,
        bootstrap_resamples=protocol.bootstrap_resamples,
        bootstrap_confidence=protocol.bootstrap_confidence,
        bootstrap_method=protocol.bootstrap_method.value,
        rows=tuple(
            (
                row.query_id,
                row.candidate_ids,
                row.scores,
                tuple(label.value for label in row.labels),
            )
            for row in rows
        ),
        metric=metric.value,
        k=k,
    )

    def metric_result(payload: dict[str, object]) -> MetricResult:
        value: dict[str, Any] = dict(payload)
        value["metric"] = MetricName(str(value["metric"]))
        value["status"] = MetricStatus(str(value["status"]))
        return MetricResult(**value)

    interval_payload: dict[str, Any] = dict(calculation.interval)
    interval_payload["method"] = BootstrapMethod(str(interval_payload["method"]))
    interval_payload["status"] = MetricStatus(str(interval_payload["status"]))
    return (
        tuple(metric_result(payload) for payload in calculation.per_query),
        metric_result(calculation.aggregate),
        BootstrapInterval(**interval_payload),
    )


class StressCohort(ContractModel):
    """A content-addressed transformed population and its accepted-core evidence."""

    cohort_id: EvaluationId
    observation_ids: Annotated[tuple[EvaluationId, ...], Field(min_length=1)]
    evaluated_query_ids: Annotated[tuple[EvaluationId, ...], Field(min_length=1)]
    observation_digest: Sha256Digest
    candidate_roster_digest: Sha256Digest
    ranked_rows: Annotated[tuple[RankedObservation, ...], Field(min_length=1)]
    per_query_results: Annotated[tuple[MetricResult, ...], Field(min_length=1)]
    metric_result: MetricResult
    interval: BootstrapInterval
    cohort_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if (
            len(self.observation_ids) != len(set(self.observation_ids))
            or tuple(sorted(self.observation_ids)) != self.observation_ids
        ):
            raise ValueError("cohort observations must be unique and canonically ordered")
        if (
            len(self.evaluated_query_ids) != len(set(self.evaluated_query_ids))
            or tuple(sorted(self.evaluated_query_ids)) != self.evaluated_query_ids
        ):
            raise ValueError("cohort evaluated queries must be unique and canonically ordered")
        if self.observation_digest != _sequence_digest(self.observation_ids):
            raise ValueError("cohort observation digest must bind exact observations")
        _canonical(
            self.ranked_rows, lambda item: item.query_id, "cohort ranked rows must be canonical"
        )
        if tuple(row.query_id for row in self.ranked_rows) != self.evaluated_query_ids:
            raise ValueError("cohort ranked rows must exactly bind evaluated query population")
        if self.candidate_roster_digest != _digest(
            {"rows": tuple(row.ranking_digest for row in self.ranked_rows)}, "omitted"
        ):
            raise ValueError("cohort candidate roster must derive from embedded ranked rows")
        _canonical(
            self.per_query_results,
            lambda item: item.evaluated_query_digest,
            "cohort per-query results must be canonical",
        )
        if tuple(result.evaluated_query_digest for result in self.per_query_results) != tuple(
            _sequence_digest((query_id,)) for query_id in self.evaluated_query_ids
        ):
            raise ValueError("cohort per-query metric identities must bind embedded rows")
        if any(
            result.protocol_digest != self.metric_result.protocol_digest
            or result.metric is not self.metric_result.metric
            or result.k != self.metric_result.k
            or result.input_digest
            != ranked_observation_metric_input_digest(
                self.ranked_rows[index], int(self.metric_result.k or 0)
            )
            for index, result in enumerate(self.per_query_results)
        ):
            raise ValueError("cohort per-query metrics must bind aggregate core authority")
        if (
            self.metric_result.status is not MetricStatus.COMPUTED
            or self.interval.status is not MetricStatus.COMPUTED
        ):
            raise ValueError("computed cohort requires accepted computed core evidence")
        if self.metric_result.evaluated_query_digest != _sequence_digest(self.evaluated_query_ids):
            raise ValueError("cohort metric must bind its exact evaluated query population")
        if self.metric_result.input_digest != aggregate_metric_input_digest(
            self.ranked_rows,
            self.per_query_results,
            self.metric_result.metric,
            int(self.metric_result.k or 0),
        ):
            raise ValueError("cohort aggregate metric must derive from embedded per-query rows")
        if (
            self.interval.metric_result_digest != self.metric_result.result_digest
            or self.interval.protocol_digest != self.metric_result.protocol_digest
            or self.interval.evaluated_query_digest != self.metric_result.evaluated_query_digest
            or self.interval.input_digest != self.metric_result.input_digest
        ):
            raise ValueError("cohort interval must bind its exact metric, protocol and input")
        if self.cohort_digest != _digest(self.model_dump(mode="json"), "cohort_digest"):
            raise ValueError("cohort_digest must match canonical payload")
        return self


class StressComparison(ContractModel):
    left_cohort_digest: Sha256Digest
    right_cohort_digest: Sha256Digest
    query_id: EvaluationId
    common_candidate_digest: Sha256Digest
    left_ranking: RankedObservation
    right_ranking: RankedObservation
    comparison: RankComparisonResult
    comparison_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.left_cohort_digest >= self.right_cohort_digest:
            raise ValueError("stress comparisons must orient cohort identities canonically")
        if self.comparison.evaluated_query_digest != _sequence_digest((self.query_id,)):
            raise ValueError("stress comparison must bind its exact query")
        if (
            self.left_ranking.query_id != self.query_id
            or self.right_ranking.query_id != self.query_id
        ):
            raise ValueError("stress comparison must embed exact left/right ranked rows")
        common = tuple(
            sorted(set(self.left_ranking.candidate_ids) & set(self.right_ranking.candidate_ids))
        )
        if self.common_candidate_digest != _sequence_digest(common):
            raise ValueError("stress comparison common candidates must derive from embedded rows")
        if self.comparison.left_input_digest != ranking_input_digest(
            self.query_id, derived_ranking(self.left_ranking, common)
        ) or self.comparison.right_input_digest != ranking_input_digest(
            self.query_id, derived_ranking(self.right_ranking, common)
        ):
            raise ValueError("stress comparison inputs must derive from canonical ranked rows")
        if self.comparison_digest != _digest(self.model_dump(mode="json"), "comparison_digest"):
            raise ValueError("stress comparison_digest must match canonical payload")
        return self


class StressTestResult(ContractModel):
    specification: StressTestSpecification
    status: RobustnessStatus
    deficits: tuple[PopulationDeficit, ...] = ()
    cohorts: tuple[StressCohort, ...] = ()
    comparisons: tuple[StressComparison, ...] = ()
    result_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        computed = self.status is RobustnessStatus.COMPUTED
        if computed and (self.deficits or not self.cohorts):
            raise ValueError("computed stress test requires transformed cohorts and no deficits")
        if not computed and (self.cohorts or self.comparisons or not self.deficits):
            raise ValueError("unsupported stress test retains exact deficits and no values")
        _canonical(
            self.comparisons,
            lambda item: (item.left_cohort_digest, item.right_cohort_digest, item.query_id),
            "stress comparisons must be canonically ordered",
        )
        _canonical(
            self.cohorts, lambda item: item.cohort_id, "stress cohorts must be canonically ordered"
        )
        if len({item.cohort_id for item in self.cohorts}) != len(self.cohorts):
            raise ValueError("stress cohorts require unique IDs")
        if computed:
            cohorts = {item.cohort_digest: item for item in self.cohorts}
            if len(cohorts) != len(self.cohorts):
                raise ValueError("stress cohorts require unique identities")
            expected_cohorts = self._expected_cohorts()
            if {
                cohort.cohort_id: cohort.observation_ids for cohort in self.cohorts
            } != expected_cohorts:
                raise ValueError(
                    "computed stress cohorts must prove the exact declared transformation"
                )
            if any(
                cohort.metric_result.protocol_digest != self.specification.protocol_digest
                or cohort.metric_result.metric is not self.specification.metric
                or cohort.metric_result.k != self.specification.k
                for cohort in self.cohorts
            ):
                raise ValueError("stress cohort core results must bind the specification")
            pairs = self._required_pairs(self.cohorts)
            expected = {
                (left, right, query_id)
                for left, right in pairs
                for query_id in set(cohorts[left].evaluated_query_ids)
                & set(cohorts[right].evaluated_query_ids)
            }
            actual = {
                (item.left_cohort_digest, item.right_cohort_digest, item.query_id)
                for item in self.comparisons
            }
            if actual != expected:
                raise ValueError(
                    "computed stress result requires exact declared cohort comparisons"
                )
            if any(
                item.left_cohort_digest not in cohorts
                or item.right_cohort_digest not in cohorts
                or item.comparison.protocol_digest != self.specification.protocol_digest
                or item.comparison.k != self.specification.k
                for item in self.comparisons
            ):
                raise ValueError("stress comparison child substitution")
            for item in self.comparisons:
                left = cohorts[item.left_cohort_digest]
                right = cohorts[item.right_cohort_digest]
                left_row = next(row for row in left.ranked_rows if row.query_id == item.query_id)
                right_row = next(row for row in right.ranked_rows if row.query_id == item.query_id)
                if (item.left_ranking, item.right_ranking) != (left_row, right_row):
                    raise ValueError("stress comparison rankings must equal named cohort rows")
                common = tuple(sorted(set(left_row.candidate_ids) & set(right_row.candidate_ids)))
                expected_comparison = derive_rank_comparison(
                    self.specification.protocol,
                    item.query_id,
                    derived_ranking(left_row, common),
                    derived_ranking(right_row, common),
                    self.specification.k,
                )
                if item.comparison != expected_comparison:
                    raise ValueError("stress comparison values must equal canonical derivation")
            for cohort in self.cohorts:
                expected_rows = derive_cohort_ranked_rows(
                    self.specification, cohort.cohort_id, cohort.observation_ids
                )
                if cohort.ranked_rows != expected_rows:
                    raise ValueError(
                        "stress cohort ranked rows must derive from named observations"
                    )
                expected_per_query, expected_metric, expected_interval = (
                    derive_ranking_metric_children(
                        self.specification.protocol,
                        cohort.ranked_rows,
                        self.specification.metric,
                        self.specification.k,
                    )
                )
                if (cohort.per_query_results, cohort.metric_result, cohort.interval) != (
                    expected_per_query,
                    expected_metric,
                    expected_interval,
                ):
                    raise ValueError(
                        "stress metric and interval values must equal canonical derivation"
                    )
            if self.specification.kind is StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON:
                common = tuple(
                    sorted(
                        set.intersection(
                            *(
                                set(member.candidate_ids)
                                for member in self.specification.inventory.members
                            )
                        )
                    )
                )
                if not common or any(
                    comparison.common_candidate_digest != _sequence_digest(common)
                    for comparison in self.comparisons
                ):
                    raise ValueError(
                        "source comparisons require the exact non-empty governed intersection"
                    )
        _canonical(
            self.deficits,
            lambda item: (item.kind.value, item.scope),
            "stress deficits must be canonical",
        )
        if not computed and self.deficits != self._expected_deficits():
            raise ValueError("stress deficits must derive from the embedded specification")
        if self.result_digest != _digest(self.model_dump(mode="json"), "result_digest"):
            raise ValueError("stress result_digest must match canonical payload")
        return self

    def _expected_deficits(self) -> tuple[PopulationDeficit, ...]:
        members = self.specification.inventory.members
        kind = self.specification.kind
        drafts: list[tuple[DeficitKind, str, int, int]] = []
        if kind is StressTestKind.SPLIT_HALF_RELIABILITY:
            counts: dict[str, int] = {}
            for member in members:
                counts[member.query_id] = counts.get(member.query_id, 0) + 1
            drafts.extend(
                (DeficitKind.PER_UNIT_OBSERVATIONS, query, count, 4)
                for query, count in counts.items()
                if count < 4
            )
        elif kind is StressTestKind.ROLLING_WINDOW_STABILITY:
            count = len({member.window_id for member in members})
            if count < 3:
                drafts.append((DeficitKind.DISTINCT_WINDOWS, "rolling", count, 3))
        elif kind is StressTestKind.MINUTES_SAMPLE_SENSITIVITY:
            for threshold in self.specification.thresholds:
                count = sum(member.minutes >= threshold for member in members)
                if count < 1:
                    drafts.append((DeficitKind.THRESHOLD_OBSERVATIONS, str(threshold), count, 1))
        elif kind is StressTestKind.TIME_WALK_FORWARD:
            cutoff = self.specification.walk_forward_cutoff_index
            if cutoff is None:
                raise ValueError("walk-forward requires an embedded declared cutoff index")
            train = sum(member.chronological_index <= cutoff for member in members)
            test = sum(member.chronological_index > cutoff for member in members)
            if train < 1:
                drafts.append((DeficitKind.WALK_FORWARD_PARTITION, "train", train, 1))
            if test < 1:
                drafts.append((DeficitKind.WALK_FORWARD_PARTITION, "test", test, 1))
        else:
            field = (
                "provider_id"
                if kind is StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON
                else {
                    StressTestKind.LEAVE_COMPETITION_OUT: "competition_id",
                    StressTestKind.LEAVE_TEAM_OUT: "team_id",
                    StressTestKind.LEAVE_PROVIDER_OUT: "provider_id",
                }[kind]
            )
            groups = {str(getattr(member, field)) for member in members}
            if len(groups) < 2:
                drafts.append((DeficitKind.DISTINCT_GROUPS, field, len(groups), 2))
            if kind is StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON:
                common = set.intersection(*(set(member.candidate_ids) for member in members))
                if not common:
                    drafts.append((DeficitKind.PROVIDER_INTERSECTION, "providers", 0, 1))
        # These are semantic aggregation prerequisites, not executor exceptions.  They
        # are derived for every declared cohort and every required comparison so an
        # otherwise sufficient population has a representable unsupported result.
        member_by_id = {member.observation_id: member for member in members}
        cohort_candidates: dict[tuple[str, str], tuple[str, ...]] = {}
        for cohort_id, observation_ids in self._expected_cohorts().items():
            by_query: dict[str, list[RankedObservation]] = {}
            for observation_id in observation_ids:
                member = member_by_id[observation_id]
                by_query.setdefault(member.query_id, []).append(member.ranking)
            for query_id, rankings in by_query.items():
                common_candidates = set(rankings[0].candidate_ids)
                for ranking in rankings[1:]:
                    common_candidates &= set(ranking.candidate_ids)
                cohort_common = tuple(sorted(common_candidates))
                cohort_candidates[(cohort_id, query_id)] = cohort_common
                if len(cohort_common) < self.specification.k:
                    drafts.append(
                        (
                            DeficitKind.INSUFFICIENT_COMMON_CANDIDATES,
                            f"cohort:{cohort_id}:{query_id}",
                            len(cohort_common),
                            self.specification.k,
                        )
                    )
                for candidate in cohort_common:
                    labels = {
                        ranking.labels[ranking.candidate_ids.index(candidate)]
                        for ranking in rankings
                    }
                    if len(labels) != 1:
                        drafts.append(
                            (
                                DeficitKind.INCOHERENT_LABEL_EVIDENCE,
                                f"cohort:{cohort_id}:{query_id}:{candidate}",
                                0,
                                1,
                            )
                        )
        cohort_ids = tuple(self._expected_cohorts())
        pairs_by_id: tuple[tuple[str, str], ...]
        if kind in {StressTestKind.SPLIT_HALF_RELIABILITY, StressTestKind.TIME_WALK_FORWARD}:
            pairs_by_id = ((cohort_ids[0], cohort_ids[1]),) if len(cohort_ids) == 2 else ()
        elif kind in {
            StressTestKind.ROLLING_WINDOW_STABILITY,
            StressTestKind.MINUTES_SAMPLE_SENSITIVITY,
        }:
            pairs_by_id = tuple(zip(cohort_ids, cohort_ids[1:], strict=False))
        else:
            pairs_by_id = tuple(
                (cohort_ids[left], cohort_ids[right])
                for left in range(len(cohort_ids))
                for right in range(left + 1, len(cohort_ids))
            )
        for left, right in pairs_by_id:
            for query_id in sorted(
                {query for cohort, query in cohort_candidates if cohort == left}
                & {query for cohort, query in cohort_candidates if cohort == right}
            ):
                common = set(cohort_candidates[(left, query_id)]) & set(
                    cohort_candidates[(right, query_id)]
                )
                if len(common) < self.specification.k:
                    drafts.append(
                        (
                            DeficitKind.INSUFFICIENT_COMMON_CANDIDATES,
                            f"comparison:{left}:{right}:{query_id}",
                            len(common),
                            self.specification.k,
                        )
                    )
        values: list[PopulationDeficit] = []
        for deficit_kind, scope, observed, required in sorted(
            drafts, key=lambda item: (item[0].value, item[1])
        ):
            values.append(
                PopulationDeficit(
                    kind=deficit_kind,
                    scope=scope,
                    observed=observed,
                    required=required,
                    deficit_digest=_digest(
                        {
                            "kind": deficit_kind,
                            "scope": scope,
                            "observed": observed,
                            "required": required,
                        },
                        "deficit_digest",
                    ),
                )
            )
        return tuple(values)

    def _required_pairs(self, cohorts: tuple[StressCohort, ...]) -> tuple[tuple[str, str], ...]:
        def canonical_pair(left: str, right: str) -> tuple[str, str]:
            return (left, right) if left < right else (right, left)

        ordered = tuple(item.cohort_digest for item in cohorts)
        kind = self.specification.kind
        if kind in {StressTestKind.SPLIT_HALF_RELIABILITY, StressTestKind.TIME_WALK_FORWARD}:
            if len(ordered) != 2:
                raise ValueError("split and walk-forward require exactly two cohorts")
            return (canonical_pair(ordered[0], ordered[1]),)
        if kind in {
            StressTestKind.ROLLING_WINDOW_STABILITY,
            StressTestKind.MINUTES_SAMPLE_SENSITIVITY,
        }:
            if len(ordered) < 2:
                raise ValueError("rolling and minutes tests require every declared cohort")
            return tuple(
                canonical_pair(ordered[index], ordered[index + 1])
                for index in range(len(ordered) - 1)
            )
        if kind in {
            StressTestKind.LEAVE_COMPETITION_OUT,
            StressTestKind.LEAVE_TEAM_OUT,
            StressTestKind.LEAVE_PROVIDER_OUT,
            StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON,
        }:
            if len(ordered) < 2:
                raise ValueError("leave-group and source tests require every declared cohort")
            return tuple(
                canonical_pair(ordered[left], ordered[right])
                for left in range(len(ordered))
                for right in range(left + 1, len(ordered))
            )
        raise ValueError("unknown stress kind")

    def _expected_cohorts(self) -> dict[str, tuple[str, ...]]:
        members = self.specification.inventory.members
        kind = self.specification.kind
        if kind is StressTestKind.SPLIT_HALF_RELIABILITY:
            by_query: dict[str, list[GovernedPopulationMember]] = {}
            for member in members:
                by_query.setdefault(member.query_id, []).append(member)
            return {
                "half-a": tuple(
                    sorted(
                        member.observation_id
                        for observations in by_query.values()
                        for index, member in enumerate(observations)
                        if index % 2 == 0
                    )
                ),
                "half-b": tuple(
                    sorted(
                        member.observation_id
                        for observations in by_query.values()
                        for index, member in enumerate(observations)
                        if index % 2 == 1
                    )
                ),
            }
        windows = sorted({(member.chronological_index, member.window_id) for member in members})
        if kind is StressTestKind.ROLLING_WINDOW_STABILITY:
            return {
                f"window-{index:04d}": tuple(
                    member.observation_id for member in members if member.window_id == window
                )
                for index, (_, window) in enumerate(windows)
            }
        if kind is StressTestKind.MINUTES_SAMPLE_SENSITIVITY:
            return {
                f"minutes-{threshold}": tuple(
                    member.observation_id for member in members if member.minutes >= threshold
                )
                for threshold in self.specification.thresholds
            }
        if kind is StressTestKind.TIME_WALK_FORWARD:
            if len(windows) < 2:
                return {}
            cutoff = self.specification.walk_forward_cutoff_index
            if cutoff is None:
                raise ValueError("walk-forward requires an embedded declared cutoff index")
            return {
                "train-earlier": tuple(
                    member.observation_id
                    for member in members
                    if member.chronological_index <= cutoff
                ),
                "test-later": tuple(
                    member.observation_id
                    for member in members
                    if member.chronological_index > cutoff
                ),
            }
        field = {
            StressTestKind.LEAVE_COMPETITION_OUT: "competition_id",
            StressTestKind.LEAVE_TEAM_OUT: "team_id",
            StressTestKind.LEAVE_PROVIDER_OUT: "provider_id",
            StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON: "provider_id",
        }[kind]
        values = tuple(sorted({str(getattr(member, field)) for member in members}))
        if kind is StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON:
            return {
                f"provider-{value}": tuple(
                    member.observation_id for member in members if member.provider_id == value
                )
                for value in values
            }
        return {
            f"leave-{value}": tuple(
                member.observation_id for member in members if str(getattr(member, field)) != value
            )
            for value in values
        }

    @property
    def specification_digest(self) -> Sha256Digest:
        return self.specification.specification_digest


class ControlAuthorityKind(StrEnum):
    COVERAGE_BASELINE = "COVERAGE_BASELINE"
    METADATA_BASELINE = "METADATA_BASELINE"
    RAW_EUCLIDEAN_BASELINE = "RAW_EUCLIDEAN_BASELINE"
    LABEL_EVIDENCE = "LABEL_EVIDENCE"
    ABSENT_GOVERNED_PAIR_EVIDENCE = "ABSENT_GOVERNED_PAIR_EVIDENCE"


class ControlBaselineAuthority(ContractModel):
    """Content-addressed, kind-specific public control authority."""

    kind: ControlAuthorityKind
    evidence_class: EvidenceAuthority
    authority_id: EvaluationId
    source_artifact_digest: Sha256Digest
    method_definition_digest: Sha256Digest
    baseline_ranking_digests: tuple[Sha256Digest, ...] = ()
    challenger_ranking_digests: tuple[Sha256Digest, ...] = ()
    authority_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        pair = self.kind is ControlAuthorityKind.ABSENT_GOVERNED_PAIR_EVIDENCE
        if pair != (not self.baseline_ranking_digests and not self.challenger_ranking_digests):
            raise ValueError("pair authority alone may omit exact ranking authority")
        if not pair and (
            len(self.baseline_ranking_digests) != len(self.challenger_ranking_digests)
            or not self.baseline_ranking_digests
        ):
            raise ValueError("control authority must bind paired baseline and challenger rankings")
        if self.authority_digest != _digest(self.model_dump(mode="json"), "authority_digest"):
            raise ValueError("control authority digest must bind its typed source and method")
        return self


class ControlInput(ContractModel):
    control: ControlKind
    authority: ControlBaselineAuthority
    k: PositiveInt
    baseline_rows: tuple[RankedObservation, ...] = ()
    challenger_rows: tuple[RankedObservation, ...] = ()
    input_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        pair = self.control is ControlKind.SHUFFLED_PAIR
        if pair:
            if (
                self.authority.kind is not ControlAuthorityKind.ABSENT_GOVERNED_PAIR_EVIDENCE
                or self.baseline_rows
                or self.challenger_rows
            ):
                raise ValueError(
                    "pair control must retain only typed absent governed pair evidence"
                )
        else:
            required = {
                ControlKind.COVERAGE_ONLY: ControlAuthorityKind.COVERAGE_BASELINE,
                ControlKind.METADATA: ControlAuthorityKind.METADATA_BASELINE,
                ControlKind.RAW_EUCLIDEAN: ControlAuthorityKind.RAW_EUCLIDEAN_BASELINE,
                ControlKind.SHUFFLED_LABEL: ControlAuthorityKind.LABEL_EVIDENCE,
            }[self.control]
            if (
                self.authority.kind is not required
                or not self.baseline_rows
                or not self.challenger_rows
            ):
                raise ValueError(
                    "control must embed its typed baseline authority and exact ranking rows"
                )
            _canonical(
                self.baseline_rows,
                lambda item: item.query_id,
                "control baseline rows must be canonical",
            )
            _canonical(
                self.challenger_rows,
                lambda item: item.query_id,
                "control challenger rows must be canonical",
            )
            if tuple(row.query_id for row in self.baseline_rows) != tuple(
                row.query_id for row in self.challenger_rows
            ):
                raise ValueError("control baseline/challenger query populations must match")
            if self.authority.baseline_ranking_digests != tuple(
                row.ranking_digest for row in self.baseline_rows
            ) or self.authority.challenger_ranking_digests != tuple(
                row.ranking_digest for row in self.challenger_rows
            ):
                raise ValueError("control authority must bind the exact embedded ranking rows")
        if self.input_digest != _digest(self.model_dump(mode="json"), "input_digest"):
            raise ValueError("control input digest must derive from embedded authority and rows")
        return self


class DeterministicControlResult(ContractModel):
    control: ControlKind
    protocol: EvaluationProtocol
    input: ControlInput
    seed: NonNegativeInt
    permutation: tuple[NonEmptyString, ...] = ()
    permutation_digest: Sha256Digest | None = None
    status: RobustnessStatus
    deficits: tuple[PopulationDeficit, ...] = ()
    baseline_rows: tuple[RankedObservation, ...] = ()
    null_rows: tuple[RankedObservation, ...] = ()
    baseline_per_query_results: tuple[MetricResult, ...] = ()
    null_per_query_results: tuple[MetricResult, ...] = ()
    baseline_result: MetricResult | None = None
    null_result: MetricResult | None = None
    comparisons: tuple[RankComparisonResult, ...] = ()
    control_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.control != self.input.control:
            raise ValueError("control result must bind embedded typed input")
        unsupported = self.status is RobustnessStatus.UNSUPPORTED_INSUFFICIENT_EVIDENCE
        if self.control is ControlKind.SHUFFLED_PAIR:
            expected = PopulationDeficit.model_construct(
                kind=DeficitKind.GOVERNED_PAIR_EVIDENCE,
                scope="MISSING_GOVERNED_PAIR_EVIDENCE",
                observed=0,
                required=1,
                deficit_digest=_digest(
                    {
                        "kind": DeficitKind.GOVERNED_PAIR_EVIDENCE,
                        "scope": "MISSING_GOVERNED_PAIR_EVIDENCE",
                        "observed": 0,
                        "required": 1,
                    },
                    "deficit_digest",
                ),
            )
            if (
                not unsupported
                or self.baseline_result is not None
                or self.null_result is not None
                or self.baseline_rows
                or self.null_rows
                or self.baseline_per_query_results
                or self.null_per_query_results
                or self.permutation
                or self.deficits != (expected,)
            ):
                raise ValueError(
                    "absent governed pair evidence must remain unsupported without values"
                )
        elif (
            unsupported or self.baseline_result is None or self.null_result is None or self.deficits
        ):
            raise ValueError("ranking controls require computed embedded-input results")
        if not unsupported:
            expected_null = (
                derive_label_null_rows(self.input.challenger_rows, self.seed)
                if self.control is ControlKind.SHUFFLED_LABEL
                else self.input.challenger_rows
            )
            if self.baseline_rows != self.input.baseline_rows or self.null_rows != expected_null:
                raise ValueError("control result rows must derive from its exact embedded input")
            for rows, results, aggregate in (
                (self.baseline_rows, self.baseline_per_query_results, self.baseline_result),
                (self.null_rows, self.null_per_query_results, self.null_result),
            ):
                if (
                    tuple(result.evaluated_query_digest for result in results)
                    != tuple(_sequence_digest((row.query_id,)) for row in rows)
                    or any(
                        result.protocol_digest != self.protocol.protocol_digest
                        or result.metric is not MetricName.PRECISION
                        or result.k != self.input.k
                        or result.input_digest
                        != ranked_observation_metric_input_digest(row, self.input.k)
                        for row, result in zip(rows, results, strict=True)
                    )
                    or aggregate is None
                    or aggregate.input_digest
                    != aggregate_metric_input_digest(
                        rows, results, MetricName.PRECISION, self.input.k
                    )
                ):
                    raise ValueError("control metric children must derive from persisted rows")
                expected_results, expected_aggregate, _ = derive_ranking_metric_children(
                    self.protocol, rows, MetricName.PRECISION, self.input.k
                )
                if results != expected_results or aggregate != expected_aggregate:
                    raise ValueError("control metric values must equal canonical derivation")
            expected_comparisons = {
                row.query_id: (
                    ranking_input_digest(row.query_id, tuple(row.candidate_ids)),
                    ranking_input_digest(null.query_id, tuple(null.candidate_ids)),
                )
                for row, null in zip(self.baseline_rows, self.null_rows, strict=True)
            }
            if {
                comparison.evaluated_query_digest: (
                    comparison.left_input_digest,
                    comparison.right_input_digest,
                )
                for comparison in self.comparisons
            } != {
                _sequence_digest((query_id,)): inputs
                for query_id, inputs in expected_comparisons.items()
            }:
                raise ValueError(
                    "control comparisons must derive from persisted baseline/null rows"
                )
            expected_comparison_values = tuple(
                sorted(
                    (
                        derive_rank_comparison(
                            self.protocol,
                            row.query_id,
                            tuple(row.candidate_ids),
                            tuple(null.candidate_ids),
                            self.input.k,
                        )
                        for row, null in zip(self.baseline_rows, self.null_rows, strict=True)
                    ),
                    key=lambda item: item.result_digest,
                )
            )
            if self.comparisons != expected_comparison_values:
                raise ValueError("control comparison values must equal canonical derivation")
        if self.control is ControlKind.SHUFFLED_LABEL:
            if not self.permutation or len(self.permutation) != len(set(self.permutation)):
                raise ValueError("shuffled control requires a unique ordered permutation identity")
            if self.permutation_digest != _sequence_digest(self.permutation):
                raise ValueError("shuffled control permutation digest must bind ordered mapping")
            if self.permutation != derive_label_permutation(self.input.challenger_rows, self.seed):
                raise ValueError(
                    "shuffled control permutation must derive from input and protocol seed"
                )
        elif self.permutation:
            raise ValueError("non-shuffled controls cannot retain a permutation")
        elif self.permutation_digest is not None:
            raise ValueError("non-shuffled controls cannot retain a permutation digest")
        if self.seed != self.protocol.bootstrap_seed:
            raise ValueError("control seed must bind the protocol seed")
        if not unsupported and any(
            result.protocol_digest != self.protocol.protocol_digest
            or result.metric is not MetricName.PRECISION
            for result in (self.baseline_result, self.null_result)
            if result is not None
        ):
            raise ValueError(
                "control baseline and null results must bind protocol and control evidence"
            )
        _canonical(
            self.comparisons,
            lambda item: item.result_digest,
            "control comparisons must be canonically ordered",
        )
        if len({item.result_digest for item in self.comparisons}) != len(self.comparisons) or any(
            item.protocol_digest != self.protocol.protocol_digest for item in self.comparisons
        ):
            raise ValueError("control comparisons must be unique and protocol-bound")
        if self.control_digest != _digest(self.model_dump(mode="json"), "control_digest"):
            raise ValueError("control_digest must match canonical payload")
        return self

    @property
    def protocol_digest(self) -> Sha256Digest:
        return self.protocol.protocol_digest

    @property
    def input_digest(self) -> Sha256Digest:
        return self.input.input_digest


class FailureCase(ContractModel):
    case_id: EvaluationId
    query_id: EvaluationId
    category: FailureCategory
    severity: NonNegativeInt
    evidence_digest: Sha256Digest
    case_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.case_digest != _digest(self.model_dump(mode="json"), "case_digest"):
            raise ValueError("failure case_digest must match canonical payload")
        return self


class FailureCaseRegister(ContractModel):
    source_cases: tuple[FailureCase, ...]
    source_digest: Sha256Digest
    retained_cases: tuple[FailureCase, ...]
    total_case_count: NonNegativeInt
    shortfall: NonNegativeInt
    register_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        _canonical(
            self.source_cases,
            lambda item: (-item.severity, item.case_id),
            "failure source cases must be worst-first canonically ordered",
        )
        if len({item.case_id for item in self.source_cases}) != len(self.source_cases):
            raise ValueError("failure source cases require unique IDs")
        if self.source_digest != _sequence_digest(
            tuple(item.case_digest for item in self.source_cases)
        ):
            raise ValueError("failure source digest must bind every canonical source case")
        _canonical(
            self.retained_cases,
            lambda item: (-item.severity, item.case_id),
            "failure cases must be worst-first canonically ordered",
        )
        if len({item.case_id for item in self.retained_cases}) != len(self.retained_cases):
            raise ValueError("failure cases require unique IDs")
        expected = max(0, 10 - len(self.source_cases))
        if (
            self.total_case_count != len(self.source_cases)
            or self.shortfall != expected
            or len(self.retained_cases) != min(10, len(self.source_cases))
        ):
            raise ValueError("failure register must retain ten or every case with exact shortfall")
        if self.retained_cases != self.source_cases[:10]:
            raise ValueError(
                "failure register retained cases must derive from complete source population"
            )
        if self.register_digest != _digest(self.model_dump(mode="json"), "register_digest"):
            raise ValueError("failure register_digest must match canonical payload")
        return self


class ApplicabilityAssessment(ContractModel):
    inventory: GovernedPopulationInventory
    state: ApplicabilityState
    stress_results: tuple[StressTestResult, ...]
    control_results: tuple[DeterministicControlResult, ...]
    missing_evidence: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    supported_population: tuple[NonEmptyString, ...]
    exclusions: tuple[NonEmptyString, ...]
    non_claims: tuple[NonEmptyString, ...]
    assessment_digest: Sha256Digest

    @model_validator(mode="after")
    def valid(self) -> Self:
        _canonical(
            self.stress_results,
            lambda item: item.specification.kind.value,
            "applicability stress results must be canonically ordered",
        )
        _canonical(
            self.control_results,
            lambda item: item.control.value,
            "applicability control results must be canonically ordered",
        )
        if {item.specification.kind for item in self.stress_results} != set(StressTestKind):
            raise ValueError("applicability requires the complete mandatory stress roster")
        if {item.control for item in self.control_results} != set(ControlKind):
            raise ValueError("applicability requires the complete mandatory control roster")
        if any(
            item.specification.inventory_digest != self.inventory.inventory_digest
            for item in self.stress_results
        ):
            raise ValueError("applicability stress results must bind this exact inventory")
        if any(
            item.specification.protocol_digest != self.inventory.protocol_digest
            for item in self.stress_results
        ) or any(
            item.protocol_digest != self.inventory.protocol_digest for item in self.control_results
        ):
            raise ValueError("applicability results must bind the inventory protocol")
        derived = {"MISSING_EXPERT_RELEVANCE_EVIDENCE"}
        for stress_result in self.stress_results:
            if stress_result.status is RobustnessStatus.UNSUPPORTED_INSUFFICIENT_EVIDENCE:
                derived.update(
                    f"MISSING_{stress_result.specification.kind.value}:{deficit.kind.value}:{deficit.scope}"
                    for deficit in stress_result.deficits
                )
        for control_result in self.control_results:
            if control_result.null_result is None:
                derived.update(deficit.scope for deficit in control_result.deficits)
            elif control_result.null_result.status is not MetricStatus.COMPUTED:
                derived.add("MISSING_MANDATORY_CONTROL_EVIDENCE")
        if tuple(sorted(derived)) != self.missing_evidence:
            raise ValueError(
                "applicability missing evidence must derive from mandatory result roster"
            )
        if (
            len(self.missing_evidence) != len(set(self.missing_evidence))
            or tuple(sorted(self.missing_evidence)) != self.missing_evidence
        ):
            raise ValueError("applicability missing evidence must be canonically unique")
        if (
            self.supported_population != ("IMPLEMENTATION_FIXTURE_ONLY",)
            or self.exclusions != ("NO_EMPIRICAL_TRANSFER_OR_EXPERT_EVIDENCE",)
            or self.non_claims
            != (
                "NOT_HUMAN_EXPERT_EVIDENCE",
                "NOT_PROTECTED_OR_PROSPECTIVE_EVIDENCE",
                "NOT_PROVIDER_OR_RECRUITMENT_OUTCOME_EVIDENCE",
            )
        ):
            raise ValueError("applicability fixture claims must be static derived non-claims")
        if self.assessment_digest != _digest(self.model_dump(mode="json"), "assessment_digest"):
            raise ValueError("applicability assessment_digest must match canonical payload")
        return self

    @property
    def inventory_digest(self) -> Sha256Digest:
        return self.inventory.inventory_digest

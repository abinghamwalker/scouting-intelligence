"""Resemblance-only retrieval request, candidate, and result contracts."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .evidence import DataCoverage, DependencyLineage, TemporalEvidence
from .primitives import (
    CanonicalPlayerId,
    ContractModel,
    NonEmptyString,
    PositiveInt,
    PositiveVersion,
    RetrievalRequestId,
    RetrievalResultId,
    RetrievalRunId,
    RoleBriefId,
    SchemaVersion,
    TenantContext,
    TraceId,
    UnitInterval,
    UtcInstant,
)

type RetrievalClaimBoundary = Literal["resemblance_only"]
RESEMBLANCE_ONLY_CLAIM: RetrievalClaimBoundary = "resemblance_only"


class EvidenceDimensionName(StrEnum):
    """The six separately visible dimensions of a candidate evidence card."""

    STYLE_RESEMBLANCE = "style_resemblance"
    ROLE_COMPATIBILITY = "role_compatibility"
    IMPACT = "impact"
    TRAJECTORY = "trajectory"
    TRANSFER_RISK = "transfer_risk"
    DATA_CONFIDENCE = "data_confidence"


class EvidenceDimension(ContractModel):
    """One visible evidence dimension; it is never a hidden composite."""

    name: EvidenceDimensionName
    score: UnitInterval
    confidence: UnitInterval
    reason_codes: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def reason_codes_are_unique(self) -> Self:
        """Repeated reason codes add no evidence and are rejected."""
        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise ValueError("evidence-dimension reason_codes must be unique")
        return self


class ApplicabilityState(StrEnum):
    """Whether the evidence supports displaying a recommendation."""

    APPLICABLE = "applicable"
    LIMITED = "limited"
    INSUFFICIENT = "insufficient"


class ConfidenceAssessment(ContractModel):
    """Calibrated confidence and explicit applicability limitations."""

    score: UnitInterval
    applicability: ApplicabilityState
    limitations: tuple[NonEmptyString, ...] = ()

    @model_validator(mode="after")
    def insufficient_evidence_names_a_limitation(self) -> Self:
        """Insufficient applicability cannot be presented without an explanation."""
        if self.applicability is ApplicabilityState.INSUFFICIENT and not self.limitations:
            raise ValueError("insufficient applicability requires at least one limitation")
        return self


class RetrievalCandidate(ContractModel):
    """One ranked resemblance candidate with complete evidence and lineage."""

    player_id: CanonicalPlayerId
    rank: PositiveInt
    evidence_dimensions: Annotated[tuple[EvidenceDimension, ...], Field(min_length=6)]
    confidence: ConfidenceAssessment
    coverage: DataCoverage
    lineage: DependencyLineage
    reason_codes: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    claim_boundary: RetrievalClaimBoundary = RESEMBLANCE_ONLY_CLAIM

    @model_validator(mode="after")
    def evidence_card_is_complete(self) -> Self:
        """Every candidate exposes the full evidence card without duplicate dimensions."""
        names = [dimension.name for dimension in self.evidence_dimensions]
        required = set(EvidenceDimensionName)
        if len(names) != len(set(names)):
            raise ValueError("candidate evidence dimensions must be unique")
        if set(names) != required:
            raise ValueError("candidate must expose all six evidence dimensions")
        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise ValueError("candidate reason_codes must be unique")
        return self


class RetrievalRequest(ContractModel):
    """A replayable retrieval request pinned to a role-brief version and cutoff."""

    schema_version: SchemaVersion = 1
    retrieval_request_id: RetrievalRequestId
    tenant_context: TenantContext
    version: PositiveVersion
    trace_id: TraceId
    role_brief_id: RoleBriefId
    role_brief_version: PositiveVersion
    requested_at: UtcInstant
    feature_cutoff_ts: UtcInstant
    limit: Annotated[int, Field(strict=True, ge=1, le=100)]
    excluded_player_ids: tuple[CanonicalPlayerId, ...] = ()
    claim_boundary: RetrievalClaimBoundary = RESEMBLANCE_ONLY_CLAIM

    @model_validator(mode="after")
    def request_is_coherent(self) -> Self:
        """A request cannot use evidence from after it was made."""
        if self.feature_cutoff_ts > self.requested_at:
            raise ValueError("feature_cutoff_ts cannot be after requested_at")
        if len(self.excluded_player_ids) != len(set(self.excluded_player_ids)):
            raise ValueError("excluded_player_ids must be unique")
        return self


class RetrievalResult(ContractModel):
    """Immutable output of one resolved resemblance-only retrieval run."""

    schema_version: SchemaVersion = 1
    retrieval_result_id: RetrievalResultId
    retrieval_request_id: RetrievalRequestId
    retrieval_run_id: RetrievalRunId
    tenant_context: TenantContext
    version: PositiveVersion
    trace_id: TraceId
    role_brief_id: RoleBriefId
    role_brief_version: PositiveVersion
    model_version: NonEmptyString
    index_version: NonEmptyString
    generated_at: UtcInstant
    temporal_evidence: TemporalEvidence
    candidates: tuple[RetrievalCandidate, ...]
    claim_boundary: RetrievalClaimBoundary = RESEMBLANCE_ONLY_CLAIM

    @model_validator(mode="after")
    def result_is_coherent(self) -> Self:
        """Ranks are unique and generation agrees with temporal evidence."""
        ranks = [candidate.rank for candidate in self.candidates]
        if len(ranks) != len(set(ranks)):
            raise ValueError("candidate ranks must be unique")
        if ranks != sorted(ranks):
            raise ValueError("candidates must be ordered by ascending rank")
        if self.generated_at != self.temporal_evidence.generated_at_ts:
            raise ValueError("generated_at must match temporal_evidence.generated_at_ts")
        if any(
            candidate.lineage != self.temporal_evidence.dependency_lineage
            for candidate in self.candidates
        ):
            raise ValueError(
                "candidate lineage must exactly match temporal_evidence dependency lineage"
            )
        return self

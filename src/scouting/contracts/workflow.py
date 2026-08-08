"""Versioned role-brief and shortlist workflow contracts."""

from __future__ import annotations

from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .evidence import Sha256Digest
from .primitives import (
    ActorId,
    CanonicalPlayerId,
    CanonicalTeamId,
    CommentId,
    ContractModel,
    EvidencePackId,
    NonEmptyString,
    ObservationId,
    PositiveInt,
    PositiveVersion,
    RetrievalLinkId,
    RetrievalRequestId,
    RetrievalResultId,
    RetrievalRunId,
    RoleBriefId,
    SchemaVersion,
    ShortlistEntryId,
    ShortlistId,
    TenantContext,
    TraceId,
    UnitInterval,
    UtcInstant,
)


class RoleBriefStatus(StrEnum):
    """Lifecycle states retained with every role-brief version."""

    DRAFT = "draft"
    APPROVED = "approved"
    ARCHIVED = "archived"


class ConstraintOperator(StrEnum):
    """Supported replayable hard-constraint comparisons."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    AT_LEAST = "at_least"
    AT_MOST = "at_most"
    IN = "in"


class RoleConstraint(ContractModel):
    """One hard requirement kept separate from model evidence."""

    field: NonEmptyString
    operator: ConstraintOperator
    value: NonEmptyString


class RolePreference(ContractModel):
    """One transparent, replayable brief weight."""

    dimension: NonEmptyString
    weight: UnitInterval


class RoleBrief(ContractModel):
    """An immutable version of a human-authored recruitment brief."""

    schema_version: SchemaVersion = 1
    role_brief_id: RoleBriefId
    tenant_context: TenantContext
    version: PositiveVersion
    trace_id: TraceId
    owner_id: ActorId
    title: NonEmptyString
    taxonomy_version: NonEmptyString
    status: RoleBriefStatus
    created_at: UtcInstant
    approved_at: UtcInstant | None = None
    team_id: CanonicalTeamId | None = None
    responsibilities: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    hard_constraints: tuple[RoleConstraint, ...] = ()
    preferences: tuple[RolePreference, ...] = ()
    exemplar_player_ids: tuple[CanonicalPlayerId, ...] = ()

    @model_validator(mode="after")
    def brief_entries_are_unique(self) -> Self:
        """Validate lifecycle time and reject ambiguous replay inputs."""
        if self.status is RoleBriefStatus.APPROVED:
            if self.approved_at is None:
                raise ValueError("approved role briefs require approved_at")
            if self.approved_at < self.created_at:
                raise ValueError("approved_at cannot be earlier than created_at")
        elif self.approved_at is not None:
            raise ValueError("non-approved role briefs cannot set approved_at")

        if len(self.responsibilities) != len(set(self.responsibilities)):
            raise ValueError("responsibilities must be unique")
        preference_dimensions = [preference.dimension for preference in self.preferences]
        if len(preference_dimensions) != len(set(preference_dimensions)):
            raise ValueError("preference dimensions must be unique")
        constraint_fields = [constraint.field for constraint in self.hard_constraints]
        if len(constraint_fields) != len(set(constraint_fields)):
            raise ValueError("hard-constraint fields must be unique")
        if len(self.exemplar_player_ids) != len(set(self.exemplar_player_ids)):
            raise ValueError("exemplar player IDs must be unique")
        return self


class ShortlistEntryState(StrEnum):
    """Auditable decision states; none is a model prediction."""

    LONGLIST = "longlist"
    MONITOR = "monitor"
    SCOUT = "scout"
    SHORTLIST = "shortlist"
    HOLD = "hold"
    REJECTED = "rejected"


class ShortlistEntry(ContractModel):
    """Collaborative shortlist state with optimistic concurrency and provenance."""

    schema_version: SchemaVersion = 1
    shortlist_entry_id: ShortlistEntryId
    shortlist_id: ShortlistId
    tenant_context: TenantContext
    version: PositiveVersion
    trace_id: TraceId
    player_id: CanonicalPlayerId
    state: ShortlistEntryState
    owner_id: ActorId
    rationale: NonEmptyString
    created_at: UtcInstant
    updated_at: UtcInstant
    retrieval_run_id: RetrievalRunId | None = None
    rank_at_addition: PositiveInt | None = None
    model_version_at_addition: NonEmptyString | None = None

    @model_validator(mode="after")
    def shortlist_provenance_is_coherent(self) -> Self:
        """Model-assisted additions retain complete provenance or none of it."""
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot be earlier than created_at")
        provenance = (
            self.retrieval_run_id,
            self.rank_at_addition,
            self.model_version_at_addition,
        )
        if any(item is not None for item in provenance) and any(
            item is None for item in provenance
        ):
            raise ValueError(
                "retrieval_run_id, rank_at_addition, and model_version_at_addition "
                "must be supplied together"
            )
        return self


class WorkflowVisibility(StrEnum):
    """Closed visibility vocabulary for collaborative workflow objects."""

    OWNER_ONLY = "OWNER_ONLY"
    TEAM = "TEAM"


class WorkflowEvidenceOrigin(StrEnum):
    """Provenance label that prevents automated fixtures becoming human evidence."""

    SYNTHETIC_AUTOMATED_TEST = "synthetic_automated_test"
    HUMAN_ENTERED_LOCAL = "human_entered_local"


class R1RoleBriefStatus(StrEnum):
    """Complete R1 role-brief lifecycle; every state is retained as a revision."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETIRED = "retired"


class RoleBriefRejectionReason(StrEnum):
    REQUIREMENTS_UNCLEAR = "requirements_unclear"
    CONSTRAINTS_UNAPPROVED = "constraints_unapproved"
    RIGHTS_OR_POLICY_CONFLICT = "rights_or_policy_conflict"
    EVIDENCE_DEFINITION_INCOMPLETE = "evidence_definition_incomplete"
    OTHER = "other"


class R1RoleBriefVersion(ContractModel):
    """One immutable interpretation of a local R1 role brief."""

    schema_version: SchemaVersion = 1
    role_brief_id: RoleBriefId
    tenant_context: TenantContext
    version: PositiveVersion
    trace_id: TraceId
    owner_id: ActorId
    created_by: ActorId
    visibility: WorkflowVisibility
    title: NonEmptyString
    template_id: NonEmptyString
    taxonomy_version: NonEmptyString
    status: R1RoleBriefStatus
    responsibilities: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    hard_constraints: tuple[RoleConstraint, ...] = ()
    preferences: tuple[RolePreference, ...] = ()
    exemplar_player_ids: tuple[CanonicalPlayerId, ...] = ()
    previous_version: PositiveVersion | None = None
    transition_reason: NonEmptyString
    rejection_reason: RoleBriefRejectionReason | None = None
    decision_note: NonEmptyString | None = None
    submitted_at: UtcInstant | None = None
    decided_at: UtcInstant | None = None
    decided_by: ActorId | None = None
    created_at: UtcInstant

    @model_validator(mode="after")
    def lifecycle_and_replay_inputs_are_coherent(self) -> Self:
        if self.version == 1 and self.previous_version is not None:
            raise ValueError("first role-brief version cannot name a previous version")
        if self.version > 1 and self.previous_version != self.version - 1:
            raise ValueError("role-brief previous_version must identify the prior version")
        if len(self.responsibilities) != len(set(self.responsibilities)):
            raise ValueError("responsibilities must be unique")
        preference_dimensions = [item.dimension for item in self.preferences]
        if len(preference_dimensions) != len(set(preference_dimensions)):
            raise ValueError("preference dimensions must be unique")
        constraint_fields = [item.field for item in self.hard_constraints]
        if len(constraint_fields) != len(set(constraint_fields)):
            raise ValueError("hard-constraint fields must be unique")
        if len(self.exemplar_player_ids) != len(set(self.exemplar_player_ids)):
            raise ValueError("exemplar player IDs must be unique")
        if self.status is R1RoleBriefStatus.DRAFT:
            if any((self.submitted_at, self.decided_at, self.decided_by, self.rejection_reason)):
                raise ValueError("draft role briefs cannot carry submission or decision fields")
        elif self.status is R1RoleBriefStatus.SUBMITTED:
            if self.submitted_at is None or any(
                (self.decided_at, self.decided_by, self.rejection_reason)
            ):
                raise ValueError("submitted role briefs require only submitted_at")
        elif self.status in {R1RoleBriefStatus.APPROVED, R1RoleBriefStatus.REJECTED}:
            if self.submitted_at is None or self.decided_at is None or self.decided_by is None:
                raise ValueError("decided role briefs require submission and decision authority")
            if self.decided_at < self.submitted_at:
                raise ValueError("role-brief decision cannot precede submission")
            if self.status is R1RoleBriefStatus.REJECTED:
                if self.rejection_reason is None:
                    raise ValueError("rejected role briefs require a controlled reason")
                if (
                    self.rejection_reason is RoleBriefRejectionReason.OTHER
                    and not self.decision_note
                ):
                    raise ValueError("other role-brief rejection requires a note")
            elif self.rejection_reason is not None:
                raise ValueError("approved role briefs cannot carry a rejection reason")
        elif self.rejection_reason is not None:
            raise ValueError("retired role briefs cannot carry a rejection reason")
        return self


class ReplayableRetrievalLink(ContractModel):
    """Immutable link from an approved brief version to one accepted serving result."""

    schema_version: SchemaVersion = 1
    retrieval_link_id: RetrievalLinkId
    tenant_context: TenantContext
    role_brief_id: RoleBriefId
    role_brief_version: PositiveVersion
    retrieval_request_id: RetrievalRequestId
    retrieval_result_id: RetrievalResultId
    retrieval_run_id: RetrievalRunId
    query_player_id: CanonicalPlayerId | None = None
    exemplar_player_ids: tuple[CanonicalPlayerId, ...] = ()
    model_version: NonEmptyString
    index_version: NonEmptyString
    data_version: NonEmptyString
    taxonomy_version: NonEmptyString
    result_digest: Sha256Digest
    lineage_digest: Sha256Digest
    claim_boundary: Literal["resemblance_only"] = "resemblance_only"
    evidence_class: Literal["synthetic_development_only"] = "synthetic_development_only"
    applicability: Literal["LIMITED"] = "LIMITED"
    limitations: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    created_by: ActorId
    created_at: UtcInstant

    @model_validator(mode="after")
    def query_mode_is_exactly_one(self) -> Self:
        """Retain the exact serving input without inventing a query player."""
        if (self.query_player_id is None) == (not self.exemplar_player_ids):
            raise ValueError("retrieval links require exactly one query mode")
        if len(self.exemplar_player_ids) != len(set(self.exemplar_player_ids)):
            raise ValueError("retrieval link exemplar player IDs must be unique")
        return self


class ShortlistRejectionReason(StrEnum):
    OUTSIDE_BRIEF = "outside_brief"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    IDENTITY_UNRESOLVED = "identity_unresolved"
    RIGHTS_OR_ELIGIBILITY = "rights_or_eligibility"
    SCOUT_NOT_RECOMMENDED = "scout_not_recommended"
    DUPLICATE_CANDIDATE = "duplicate_candidate"
    OTHER = "other"


class ShortlistHoldReason(StrEnum):
    AWAITING_EVIDENCE = "awaiting_evidence"
    IDENTITY_REVIEW = "identity_review"
    RIGHTS_REVIEW = "rights_review"
    AVAILABILITY_REVIEW = "availability_review"
    OTHER = "other"


class R1ShortlistEntryRevision(ContractModel):
    """Immutable, attributable revision of one candidate workflow entry."""

    schema_version: SchemaVersion = 1
    shortlist_entry_id: ShortlistEntryId
    shortlist_id: ShortlistId
    tenant_context: TenantContext
    revision: PositiveVersion
    previous_revision: PositiveVersion | None = None
    role_brief_id: RoleBriefId
    role_brief_version: PositiveVersion
    player_id: CanonicalPlayerId
    state: ShortlistEntryState
    owner_id: ActorId
    assigned_scout_id: ActorId | None = None
    retrieval_link_id: RetrievalLinkId
    rationale: NonEmptyString
    transition_reason: NonEmptyString
    rejection_reason: ShortlistRejectionReason | None = None
    hold_reason: ShortlistHoldReason | None = None
    reason_note: NonEmptyString | None = None
    next_action: NonEmptyString | None = None
    next_action_owner_id: ActorId | None = None
    changed_by: ActorId
    created_at: UtcInstant

    @model_validator(mode="after")
    def transition_context_is_coherent(self) -> Self:
        if self.revision == 1 and self.previous_revision is not None:
            raise ValueError("first shortlist revision cannot name a previous revision")
        if self.revision > 1 and self.previous_revision != self.revision - 1:
            raise ValueError("shortlist previous_revision must identify the prior revision")
        if self.state is ShortlistEntryState.REJECTED:
            if self.rejection_reason is None:
                raise ValueError("rejected shortlist entries require a controlled reason")
        elif self.rejection_reason is not None:
            raise ValueError("non-rejected shortlist entries cannot carry a rejection reason")
        if self.state is ShortlistEntryState.HOLD:
            if self.hold_reason is None:
                raise ValueError("held shortlist entries require a controlled reason")
        elif self.hold_reason is not None:
            raise ValueError("non-held shortlist entries cannot carry a hold reason")
        if (
            self.rejection_reason is ShortlistRejectionReason.OTHER
            or self.hold_reason is ShortlistHoldReason.OTHER
        ) and self.reason_note is None:
            raise ValueError("other shortlist reasons require a bounded note")
        if (self.next_action is None) != (self.next_action_owner_id is None):
            raise ValueError("next action and its owner must be supplied together")
        if self.state is ShortlistEntryState.SCOUT and self.assigned_scout_id is None:
            raise ValueError("scout state requires an assigned scout")
        return self


class ShortlistComment(ContractModel):
    """Append-only attributable workflow comment."""

    schema_version: SchemaVersion = 1
    comment_id: CommentId
    tenant_context: TenantContext
    shortlist_entry_id: ShortlistEntryId
    author_id: ActorId
    visibility: WorkflowVisibility
    body: NonEmptyString
    evidence_origin: WorkflowEvidenceOrigin
    created_at: UtcInstant


class ScoutRubricDimensionName(StrEnum):
    ROLE_EXECUTION = "role_execution"
    DECISION_MAKING = "decision_making"
    TECHNICAL_EXECUTION = "technical_execution"
    OFF_BALL_CONTRIBUTION = "off_ball_contribution"
    CONTEXT_AND_RISK = "context_and_risk"


class ScoutRubricDimension(ContractModel):
    dimension: ScoutRubricDimensionName
    rating: Annotated[int, Field(strict=True, ge=1, le=5)]
    confidence: UnitInterval
    note: NonEmptyString


class LocalEvidenceReferenceKind(StrEnum):
    LOCAL_CLIP = "local_clip"
    LOCAL_NOTE = "local_note"


class LocalEvidenceReference(ContractModel):
    kind: LocalEvidenceReferenceKind
    reference: NonEmptyString

    @model_validator(mode="after")
    def reference_stays_local(self) -> Self:
        value = str(self.reference)
        parsed = PurePosixPath(value)
        if "://" in value or parsed.is_absolute() or ".." in parsed.parts:
            raise ValueError("observation evidence references must stay local")
        return self


class ScoutObservationVersion(ContractModel):
    """Versioned scout evidence with explicit confidence and disagreement."""

    schema_version: SchemaVersion = 1
    observation_id: ObservationId
    tenant_context: TenantContext
    version: PositiveVersion
    previous_version: PositiveVersion | None = None
    shortlist_entry_id: ShortlistEntryId
    author_id: ActorId
    visibility: WorkflowVisibility
    dimensions: Annotated[tuple[ScoutRubricDimension, ...], Field(min_length=1)]
    overall_confidence: UnitInterval
    evidence_references: tuple[LocalEvidenceReference, ...] = ()
    summary: NonEmptyString
    disagreement: bool
    disagreement_reason: NonEmptyString | None = None
    recommended_next_action: NonEmptyString
    evidence_origin: WorkflowEvidenceOrigin
    created_at: UtcInstant

    @model_validator(mode="after")
    def version_and_disagreement_are_coherent(self) -> Self:
        if self.version == 1 and self.previous_version is not None:
            raise ValueError("first observation version cannot name a previous version")
        if self.version > 1 and self.previous_version != self.version - 1:
            raise ValueError("observation previous_version must identify the prior version")
        names = [item.dimension for item in self.dimensions]
        if len(names) != len(set(names)):
            raise ValueError("scout rubric dimensions must be unique")
        if self.disagreement != (self.disagreement_reason is not None):
            raise ValueError("disagreement and disagreement reason must be supplied together")
        return self


class LocalEvidencePackReceipt(ContractModel):
    """Content-addressed local-only export receipt; revocation is separately appended."""

    schema_version: SchemaVersion = 1
    evidence_pack_id: EvidencePackId
    tenant_context: TenantContext
    generated_by: ActorId
    classification: Literal["w08_local_confidential_synthetic_workflow"]
    relative_path: NonEmptyString
    sha256: Sha256Digest
    generated_at: UtcInstant
    limitations: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]

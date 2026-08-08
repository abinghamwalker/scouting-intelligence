"""Strict W08 workflow contracts preserve history and evidence boundaries."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from scouting.contracts import (
    LocalEvidenceReference,
    LocalEvidenceReferenceKind,
    R1RoleBriefStatus,
    R1RoleBriefVersion,
    R1ShortlistEntryRevision,
    ReplayableRetrievalLink,
    RoleBriefRejectionReason,
    ScoutObservationVersion,
    ScoutRubricDimension,
    ScoutRubricDimensionName,
    ShortlistEntryState,
    ShortlistHoldReason,
    ShortlistRejectionReason,
    TenantContext,
    WorkflowEvidenceOrigin,
    WorkflowVisibility,
)

NOW = datetime(2026, 8, 4, 20, 0, tzinfo=UTC)
TENANT = UUID("50000000-0000-4000-8000-000000000001")
ANALYST = UUID("81000000-0000-4000-8000-000000000001")
SCOUT = UUID("81000000-0000-4000-8000-000000000002")
APPROVER = UUID("81000000-0000-4000-8000-000000000003")
BRIEF = UUID("82000000-0000-4000-8000-000000000001")
SHORTLIST = UUID("83000000-0000-4000-8000-000000000001")
ENTRY = UUID("84000000-0000-4000-8000-000000000001")
LINK = UUID("85000000-0000-4000-8000-000000000001")
PLAYER = UUID("20000000-0000-4000-8000-000000000001")


def _brief(**changes: object) -> R1RoleBriefVersion:
    payload: dict[str, object] = {
        "role_brief_id": BRIEF,
        "tenant_context": TenantContext(tenant_id=TENANT),
        "version": 1,
        "trace_id": uuid4(),
        "owner_id": ANALYST,
        "created_by": ANALYST,
        "visibility": WorkflowVisibility.OWNER_ONLY,
        "title": "Synthetic automated role brief",
        "template_id": "w08-role-template-v1",
        "taxonomy_version": "w05-football-responsibility-taxonomy-v1",
        "status": R1RoleBriefStatus.DRAFT,
        "responsibilities": ("advance_play_final_third",),
        "transition_reason": "synthetic automated contract witness",
        "created_at": NOW,
    }
    payload.update(changes)
    return R1RoleBriefVersion.model_validate(payload)


def _link() -> ReplayableRetrievalLink:
    return ReplayableRetrievalLink(
        retrieval_link_id=LINK,
        tenant_context=TenantContext(tenant_id=TENANT),
        role_brief_id=BRIEF,
        role_brief_version=3,
        retrieval_request_id=uuid4(),
        retrieval_result_id=uuid4(),
        retrieval_run_id=uuid4(),
        query_player_id=PLAYER,
        model_version="w05-m0-baseline-v1",
        index_version="w05-m0-index-v1",
        data_version="w05-synthetic-development-v1",
        taxonomy_version="w05-football-responsibility-taxonomy-v1",
        result_digest="a" * 64,
        lineage_digest="b" * 64,
        limitations=(
            "MISSING_EXPERT_RELEVANCE_EVIDENCE",
            "no_recommendation_evidence",
        ),
        created_by=ANALYST,
        created_at=NOW,
    )


def test_retrieval_link_query_mode_is_exactly_one_and_exemplars_are_unique() -> None:
    player_mode = _link()
    assert player_mode.query_player_id == PLAYER
    exemplar_mode = ReplayableRetrievalLink.model_validate(
        _link().model_dump(mode="python")
        | {"query_player_id": None, "exemplar_player_ids": (PLAYER, uuid4())}
    )
    assert exemplar_mode.query_player_id is None
    assert exemplar_mode.exemplar_player_ids[0] == PLAYER
    with pytest.raises(ValidationError, match="exactly one query mode"):
        ReplayableRetrievalLink.model_validate(
            _link().model_dump(mode="python") | {"query_player_id": None}
        )
    with pytest.raises(ValidationError, match="exactly one query mode"):
        ReplayableRetrievalLink.model_validate(
            _link().model_dump(mode="python") | {"exemplar_player_ids": (uuid4(),)}
        )
    with pytest.raises(ValidationError, match="must be unique"):
        ReplayableRetrievalLink.model_validate(
            _link().model_dump(mode="python")
            | {"query_player_id": None, "exemplar_player_ids": (PLAYER, PLAYER)}
        )


def test_role_brief_versions_retain_submission_and_approval_authority() -> None:
    draft = _brief()
    submitted = _brief(
        version=2,
        previous_version=1,
        status=R1RoleBriefStatus.SUBMITTED,
        visibility=WorkflowVisibility.TEAM,
        submitted_at=NOW + timedelta(minutes=1),
        created_at=NOW + timedelta(minutes=1),
    )
    approved = _brief(
        version=3,
        previous_version=2,
        status=R1RoleBriefStatus.APPROVED,
        visibility=WorkflowVisibility.TEAM,
        submitted_at=submitted.submitted_at,
        decided_at=NOW + timedelta(minutes=2),
        decided_by=APPROVER,
        created_by=APPROVER,
        created_at=NOW + timedelta(minutes=2),
    )
    assert (draft.version, submitted.version, approved.version) == (1, 2, 3)
    assert approved.decided_by == APPROVER


def test_role_brief_rejection_and_version_links_fail_closed() -> None:
    with pytest.raises(ValidationError, match="controlled reason"):
        _brief(
            version=2,
            previous_version=1,
            status=R1RoleBriefStatus.REJECTED,
            submitted_at=NOW,
            decided_at=NOW,
            decided_by=APPROVER,
        )
    with pytest.raises(ValidationError, match="requires a note"):
        _brief(
            version=2,
            previous_version=1,
            status=R1RoleBriefStatus.REJECTED,
            submitted_at=NOW,
            decided_at=NOW,
            decided_by=APPROVER,
            rejection_reason=RoleBriefRejectionReason.OTHER,
        )
    with pytest.raises(ValidationError, match="prior version"):
        _brief(version=3, previous_version=1)


def test_retrieval_link_fixes_claim_and_synthetic_evidence_class() -> None:
    link = _link()
    assert link.claim_boundary == "resemblance_only"
    assert link.evidence_class == "synthetic_development_only"
    assert link.applicability == "LIMITED"
    with pytest.raises(ValidationError):
        ReplayableRetrievalLink.model_validate(
            {**link.model_dump(), "claim_boundary": "validated_recommendation"}
        )


def test_shortlist_revisions_require_assignment_reasons_and_next_action_owner() -> None:
    common = {
        "shortlist_entry_id": ENTRY,
        "shortlist_id": SHORTLIST,
        "tenant_context": TenantContext(tenant_id=TENANT),
        "revision": 2,
        "previous_revision": 1,
        "role_brief_id": BRIEF,
        "role_brief_version": 3,
        "player_id": PLAYER,
        "owner_id": ANALYST,
        "retrieval_link_id": LINK,
        "rationale": "synthetic automated workflow mechanics",
        "transition_reason": "request bounded scout review",
        "changed_by": ANALYST,
        "created_at": NOW,
    }
    scout_revision = R1ShortlistEntryRevision(
        **common,
        state=ShortlistEntryState.SCOUT,
        assigned_scout_id=SCOUT,
        next_action="Review local synthetic evidence",
        next_action_owner_id=SCOUT,
    )
    assert scout_revision.assigned_scout_id == SCOUT
    with pytest.raises(ValidationError, match="assigned scout"):
        R1ShortlistEntryRevision(**common, state=ShortlistEntryState.SCOUT)
    with pytest.raises(ValidationError, match="controlled reason"):
        R1ShortlistEntryRevision(**common, state=ShortlistEntryState.REJECTED)
    held = R1ShortlistEntryRevision(
        **common,
        state=ShortlistEntryState.HOLD,
        hold_reason=ShortlistHoldReason.AWAITING_EVIDENCE,
    )
    assert held.hold_reason is ShortlistHoldReason.AWAITING_EVIDENCE
    rejected = R1ShortlistEntryRevision(
        **common,
        state=ShortlistEntryState.REJECTED,
        rejection_reason=ShortlistRejectionReason.INSUFFICIENT_EVIDENCE,
    )
    assert rejected.rejection_reason is ShortlistRejectionReason.INSUFFICIENT_EVIDENCE


def test_observation_history_is_structured_local_and_explicitly_synthetic() -> None:
    observation = ScoutObservationVersion(
        observation_id=uuid4(),
        tenant_context=TenantContext(tenant_id=TENANT),
        version=1,
        shortlist_entry_id=ENTRY,
        author_id=SCOUT,
        visibility=WorkflowVisibility.TEAM,
        dimensions=(
            ScoutRubricDimension(
                dimension=ScoutRubricDimensionName.ROLE_EXECUTION,
                rating=3,
                confidence=0.55,
                note="Synthetic automated mechanics only",
            ),
        ),
        overall_confidence=0.55,
        evidence_references=(
            LocalEvidenceReference(
                kind=LocalEvidenceReferenceKind.LOCAL_CLIP,
                reference="clips/synthetic-automated/segment-01",
            ),
        ),
        summary="Synthetic automated scout-form submission",
        disagreement=True,
        disagreement_reason="Synthetic disagreement path witness",
        recommended_next_action="Request a second synthetic automated observation",
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        created_at=NOW,
    )
    assert observation.evidence_origin is WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST
    with pytest.raises(ValidationError, match="stay local"):
        LocalEvidenceReference(
            kind=LocalEvidenceReferenceKind.LOCAL_CLIP,
            reference="https://external.invalid/clip",
        )
    with pytest.raises(ValidationError, match="supplied together"):
        ScoutObservationVersion.model_validate(
            {**observation.model_dump(), "disagreement_reason": None}
        )

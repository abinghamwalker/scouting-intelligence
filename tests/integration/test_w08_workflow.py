"""Synthetic automated integration witnesses for the local R1 workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from scouting.audit import AuditIntegrityError
from scouting.contracts import (
    R1RoleBriefStatus,
    R1RoleBriefVersion,
    R1ShortlistEntryRevision,
    ReplayableRetrievalLink,
    ScoutObservationVersion,
    ScoutRubricDimension,
    ScoutRubricDimensionName,
    ShortlistComment,
    ShortlistEntryState,
    ShortlistRejectionReason,
    TenantContext,
    WorkflowEvidenceOrigin,
    WorkflowVisibility,
)
from scouting.observations import ScoutObservationService
from scouting.policy import LocalRole, R1AuthorizationDenied, R1Principal
from scouting.storage.embedded import create_embedded_engine
from scouting.workflow import R1WorkflowService, WorkflowConflict

NOW = datetime(2026, 8, 4, tzinfo=UTC)
DIGEST = "a" * 64


@pytest.fixture
def runtime(tmp_path: Path) -> tuple[Engine, UUID, UUID, UUID, UUID]:
    engine = create_embedded_engine(tmp_path / "w08.sqlite3", allowed_root=tmp_path)
    tenant, analyst, scout, approver = uuid4(), uuid4(), uuid4(), uuid4()
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO tenants VALUES (:id,:slug,'Synthetic R1',:at)"),
            {"id": tenant, "slug": f"t-{tenant.hex}", "at": NOW},
        )
        for actor, name in ((analyst, "Analyst"), (scout, "Scout"), (approver, "Approver")):
            connection.execute(
                text("INSERT INTO local_accounts VALUES (:actor,:tenant,:name,1,:at,NULL)"),
                {"actor": actor, "tenant": tenant, "name": name, "at": NOW},
            )
        for actor, role in ((analyst, "analyst"), (scout, "scout"), (approver, "approver")):
            connection.execute(
                text("INSERT INTO local_account_roles VALUES (:actor,:role,:at,:by)"),
                {"actor": actor, "role": role, "at": NOW, "by": analyst},
            )
    yield engine, tenant, analyst, scout, approver
    engine.dispose()


def principal(actor: UUID, tenant: UUID, role: LocalRole) -> R1Principal:
    return R1Principal(actor, tenant, frozenset({role}), uuid4())


def brief(
    brief_id: UUID,
    tenant: UUID,
    analyst: UUID,
    version: int,
    status: R1RoleBriefStatus,
    *,
    approver: UUID | None = None,
    created_by: UUID | None = None,
) -> R1RoleBriefVersion:
    return R1RoleBriefVersion(
        role_brief_id=brief_id,
        tenant_context=TenantContext(tenant_id=tenant),
        version=version,
        previous_version=None if version == 1 else version - 1,
        trace_id=uuid4(),
        owner_id=analyst,
        created_by=created_by or analyst,
        visibility=WorkflowVisibility.TEAM,
        title="Synthetic automated test role",
        template_id="synthetic-template",
        taxonomy_version="v1",
        status=status,
        responsibilities=("progress ball",),
        transition_reason="synthetic automated transition",
        submitted_at=NOW if status is not R1RoleBriefStatus.DRAFT else None,
        decided_at=NOW
        if status in {R1RoleBriefStatus.APPROVED, R1RoleBriefStatus.REJECTED}
        else None,
        decided_by=approver
        if status in {R1RoleBriefStatus.APPROVED, R1RoleBriefStatus.REJECTED}
        else None,
        created_at=NOW,
    )


def entry(
    entry_id: UUID,
    shortlist_id: UUID,
    brief_id: UUID,
    link_id: UUID,
    tenant: UUID,
    analyst: UUID,
    *,
    revision: int,
    state: ShortlistEntryState,
    scout: UUID | None = None,
    approver: UUID | None = None,
    player: UUID | None = None,
    rejection_reason: ShortlistRejectionReason | None = None,
    transition_reason: str = "synthetic transition",
) -> R1ShortlistEntryRevision:
    return R1ShortlistEntryRevision(
        shortlist_entry_id=entry_id,
        shortlist_id=shortlist_id,
        tenant_context=TenantContext(tenant_id=tenant),
        revision=revision,
        previous_revision=None if revision == 1 else revision - 1,
        role_brief_id=brief_id,
        role_brief_version=3,
        player_id=player or uuid4(),
        state=state,
        owner_id=analyst,
        assigned_scout_id=scout,
        retrieval_link_id=link_id,
        rationale="synthetic automated evidence review",
        transition_reason=transition_reason,
        next_action="review evidence" if state is not ShortlistEntryState.REJECTED else None,
        next_action_owner_id=analyst if state is not ShortlistEntryState.REJECTED else None,
        changed_by=approver or analyst,
        rejection_reason=rejection_reason,
        created_at=NOW,
    )


def test_synthetic_automated_role_brief_to_observation_journey(
    runtime: tuple[Engine, UUID, UUID, UUID, UUID],
) -> None:
    engine, tenant, analyst, scout, approver = runtime
    workflow, observations = R1WorkflowService(), ScoutObservationService()
    analyst_p, scout_p, approver_p = (
        principal(analyst, tenant, LocalRole.ANALYST),
        principal(scout, tenant, LocalRole.SCOUT),
        principal(approver, tenant, LocalRole.APPROVER),
    )
    analyst_approver_non_owner_p = R1Principal(
        approver,
        tenant,
        frozenset({LocalRole.ANALYST, LocalRole.APPROVER}),
        uuid4(),
    )
    brief_id, link_id, shortlist_id, entry_id, player_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    with engine.begin() as connection:
        workflow.create_role_brief(
            connection,
            principal=analyst_p,
            brief=brief(brief_id, tenant, analyst, 1, R1RoleBriefStatus.DRAFT),
            request_id=uuid4(),
        )
        workflow.transition_role_brief(
            connection,
            principal=analyst_p,
            next_version=brief(brief_id, tenant, analyst, 2, R1RoleBriefStatus.SUBMITTED),
            expected_lock_version=1,
            request_id=uuid4(),
        )
        with pytest.raises(R1AuthorizationDenied):
            workflow.transition_role_brief(
                connection,
                principal=approver_p,
                next_version=brief(
                    brief_id,
                    tenant,
                    analyst,
                    3,
                    R1RoleBriefStatus.APPROVED,
                    approver=uuid4(),
                    created_by=approver,
                ),
                expected_lock_version=2,
                request_id=uuid4(),
            )
        workflow.transition_role_brief(
            connection,
            principal=approver_p,
            next_version=brief(
                brief_id,
                tenant,
                analyst,
                3,
                R1RoleBriefStatus.APPROVED,
                approver=approver,
                created_by=approver,
            ),
            expected_lock_version=2,
            request_id=uuid4(),
        )
        link = ReplayableRetrievalLink(
            retrieval_link_id=link_id,
            tenant_context=TenantContext(tenant_id=tenant),
            role_brief_id=brief_id,
            role_brief_version=3,
            retrieval_request_id=uuid4(),
            retrieval_result_id=uuid4(),
            retrieval_run_id=uuid4(),
            query_player_id=uuid4(),
            model_version="w05-public",
            index_version="w05-index",
            data_version="w04",
            taxonomy_version="v1",
            result_digest=DIGEST,
            lineage_digest=DIGEST,
            limitations=("W06 NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE",),
            created_by=analyst,
            created_at=NOW,
        )
        workflow.create_retrieval_link(
            connection, principal=analyst_p, link=link, request_id=uuid4()
        )
        workflow.create_shortlist(
            connection,
            shortlist_id=shortlist_id,
            tenant_id=tenant,
            role_brief_id=brief_id,
            role_brief_version=3,
            owner_id=analyst,
            visibility=WorkflowVisibility.TEAM,
            title="Synthetic automated shortlist",
            principal=analyst_p,
            request_id=uuid4(),
        )
        first = entry(
            entry_id,
            shortlist_id,
            brief_id,
            link_id,
            tenant,
            analyst,
            revision=1,
            state=ShortlistEntryState.LONGLIST,
            player=player_id,
        )
        workflow.add_entry(connection, principal=analyst_p, revision=first, request_id=uuid4())
        scout_revision = entry(
            entry_id,
            shortlist_id,
            brief_id,
            link_id,
            tenant,
            analyst,
            revision=2,
            state=ShortlistEntryState.SCOUT,
            scout=scout,
            player=player_id,
            approver=approver,
        )
        workflow.transition_entry(
            connection,
            principal=analyst_approver_non_owner_p,
            next_revision=scout_revision,
            expected_lock_version=1,
            request_id=uuid4(),
        )
        observation = ScoutObservationVersion(
            observation_id=uuid4(),
            tenant_context=TenantContext(tenant_id=tenant),
            version=1,
            shortlist_entry_id=entry_id,
            author_id=scout,
            visibility=WorkflowVisibility.TEAM,
            dimensions=(
                ScoutRubricDimension(
                    dimension=ScoutRubricDimensionName.ROLE_EXECUTION,
                    rating=3,
                    confidence=0.4,
                    note="synthetic automated fixture",
                ),
            ),
            overall_confidence=0.4,
            summary="Synthetic automated test observation; not real scout evidence.",
            disagreement=True,
            disagreement_reason="synthetic disagreement",
            recommended_next_action="human review",
            evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
            created_at=NOW,
        )
        observations.create(
            connection, principal=scout_p, observation=observation, request_id=uuid4()
        )
        workflow.add_comment(
            connection,
            principal=scout_p,
            comment=ShortlistComment(
                comment_id=uuid4(),
                tenant_context=TenantContext(tenant_id=tenant),
                shortlist_entry_id=entry_id,
                author_id=scout,
                visibility=WorkflowVisibility.TEAM,
                body="Synthetic automated test comment, not a scout judgement.",
                evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
                created_at=NOW,
            ),
            request_id=uuid4(),
        )
        visible = observations.visible_versions(
            connection, principal=analyst_p, shortlist_entry_id=entry_id
        )
        assert len(visible) == 1 and visible[0]["evidence_origin"] == "synthetic_automated_test"
        rejected = entry(
            entry_id,
            shortlist_id,
            brief_id,
            link_id,
            tenant,
            analyst,
            revision=3,
            state=ShortlistEntryState.REJECTED,
            player=player_id,
            rejection_reason=ShortlistRejectionReason.INSUFFICIENT_EVIDENCE,
        )
        workflow.transition_entry(
            connection,
            principal=analyst_p,
            next_revision=rejected,
            expected_lock_version=2,
            request_id=uuid4(),
        )
        reconsidered = entry(
            entry_id,
            shortlist_id,
            brief_id,
            link_id,
            tenant,
            analyst,
            revision=4,
            state=ShortlistEntryState.LONGLIST,
            player=player_id,
            transition_reason="synthetic reconsideration after new local evidence",
        )
        connection.execute(
            text(
                """CREATE TRIGGER synthetic_reconsideration_audit_failure
                BEFORE INSERT ON audit_receipts
                BEGIN SELECT RAISE(ABORT, 'synthetic audit failure'); END"""
            )
        )
        with pytest.raises(AuditIntegrityError):
            workflow.transition_entry(
                connection,
                principal=analyst_p,
                next_revision=reconsidered,
                expected_lock_version=3,
                request_id=uuid4(),
            )
        assert (
            connection.execute(
                text(
                    "SELECT latest_revision FROM shortlist_entry_workflows "
                    "WHERE shortlist_entry_id=:id"
                ),
                {"id": entry_id},
            ).scalar_one()
            == 3
        )
        connection.execute(text("DROP TRIGGER synthetic_reconsideration_audit_failure"))
        workflow.transition_entry(
            connection,
            principal=analyst_p,
            next_revision=reconsidered,
            expected_lock_version=3,
            request_id=uuid4(),
        )
        with pytest.raises(WorkflowConflict):
            workflow.transition_entry(
                connection,
                principal=analyst_p,
                next_revision=entry(
                    entry_id,
                    shortlist_id,
                    brief_id,
                    link_id,
                    tenant,
                    analyst,
                    revision=5,
                    state=ShortlistEntryState.MONITOR,
                    player=player_id,
                ),
                expected_lock_version=3,
                request_id=uuid4(),
            )
        revisions = (
            connection.execute(
                text(
                    "SELECT revision, state, rejection_reason, player_id "
                    "FROM shortlist_entry_revisions "
                    "WHERE shortlist_entry_id=:id ORDER BY revision"
                ),
                {"id": entry_id},
            )
            .mappings()
            .all()
        )
        assert [row["state"] for row in revisions] == ["longlist", "scout", "rejected", "longlist"]
        assert revisions[2]["rejection_reason"] == "insufficient_evidence"
        assert revisions[2]["player_id"] == revisions[3]["player_id"] == str(player_id)
        with pytest.raises(WorkflowConflict):
            workflow.add_entry(
                connection,
                principal=analyst_p,
                revision=entry(
                    uuid4(),
                    shortlist_id,
                    brief_id,
                    link_id,
                    tenant,
                    analyst,
                    revision=1,
                    state=ShortlistEntryState.LONGLIST,
                    player=player_id,
                ),
                request_id=uuid4(),
            )
        assert (
            connection.execute(
                text("SELECT count(*) FROM shortlist_entry_workflows WHERE shortlist_id=:id"),
                {"id": shortlist_id},
            ).scalar_one()
            == 1
        )
        with pytest.raises(R1AuthorizationDenied):
            workflow.transition_entry(
                connection,
                principal=analyst_p,
                next_revision=entry(
                    entry_id,
                    shortlist_id,
                    brief_id,
                    link_id,
                    tenant,
                    analyst,
                    revision=5,
                    state=ShortlistEntryState.MONITOR,
                    player=player_id,
                    approver=approver,
                ),
                expected_lock_version=4,
                request_id=uuid4(),
            )
        disabled_scout, admin_only = uuid4(), uuid4()
        for actor, name, enabled, disabled_at in (
            (disabled_scout, "Disabled scout", 0, NOW),
            (admin_only, "Admin only", 1, None),
        ):
            connection.execute(
                text(
                    """INSERT INTO local_accounts
                    (actor_id, tenant_id, display_name, enabled, created_at, disabled_at)
                    VALUES (:actor,:tenant,:name,:enabled,:created,:disabled)"""
                ),
                {
                    "actor": actor,
                    "tenant": tenant,
                    "name": name,
                    "enabled": enabled,
                    "created": NOW,
                    "disabled": disabled_at,
                },
            )
        for actor, role in ((disabled_scout, "scout"), (admin_only, "admin")):
            connection.execute(
                text(
                    """INSERT INTO local_account_roles
                    (actor_id, role, assigned_at, assigned_by)
                    VALUES (:actor,:role,:at,:by)"""
                ),
                {"actor": actor, "role": role, "at": NOW, "by": analyst},
            )
        assert not workflow._is_enabled_same_tenant_scout(
            connection, tenant_id=uuid4(), actor_id=scout
        )
        for invalid_scout in (disabled_scout, analyst, approver, admin_only, uuid4()):
            with pytest.raises(R1AuthorizationDenied):
                workflow.transition_entry(
                    connection,
                    principal=analyst_p,
                    next_revision=entry(
                        entry_id,
                        shortlist_id,
                        brief_id,
                        link_id,
                        tenant,
                        analyst,
                        revision=5,
                        state=ShortlistEntryState.MONITOR,
                        player=player_id,
                        scout=invalid_scout,
                    ),
                    expected_lock_version=4,
                    request_id=uuid4(),
                )
        with pytest.raises(WorkflowConflict):
            workflow.add_entry(
                connection,
                principal=analyst_p,
                revision=entry(
                    uuid4(),
                    shortlist_id,
                    brief_id,
                    link_id,
                    tenant,
                    analyst,
                    revision=1,
                    state=ShortlistEntryState.LONGLIST,
                    scout=scout,
                ),
                request_id=uuid4(),
            )
        with pytest.raises(WorkflowConflict):
            workflow.add_entry(
                connection,
                principal=analyst_p,
                revision=entry(
                    uuid4(),
                    shortlist_id,
                    uuid4(),
                    link_id,
                    tenant,
                    analyst,
                    revision=1,
                    state=ShortlistEntryState.LONGLIST,
                ),
                request_id=uuid4(),
            )
        with pytest.raises(WorkflowConflict):
            observations.amend(
                connection,
                principal=scout_p,
                observation=observation.model_copy(
                    update={
                        "version": 2,
                        "previous_version": 1,
                        "shortlist_entry_id": uuid4(),
                        "evidence_origin": WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL,
                    }
                ),
                expected_version=1,
                request_id=uuid4(),
            )
        with pytest.raises(WorkflowConflict):
            workflow.transition_role_brief(
                connection,
                principal=analyst_p,
                next_version=brief(
                    brief_id,
                    tenant,
                    analyst,
                    4,
                    R1RoleBriefStatus.RETIRED,
                    created_by=analyst,
                ).model_copy(update={"title": "rewritten role"}),
                expected_lock_version=3,
                request_id=uuid4(),
            )
        with pytest.raises(WorkflowConflict):
            workflow.create_role_brief(
                connection,
                principal=analyst_p,
                brief=brief(
                    uuid4(),
                    tenant,
                    analyst,
                    1,
                    R1RoleBriefStatus.DRAFT,
                    created_by=approver,
                ),
                request_id=uuid4(),
            )
        assert (
            connection.execute(
                text("SELECT count(*) FROM shortlist_entry_revisions WHERE shortlist_entry_id=:id"),
                {"id": entry_id},
            ).scalar_one()
            == 4
        )
        assert (
            connection.execute(
                text("SELECT count(*) FROM scout_observations WHERE observation_id=:id"),
                {"id": observation.observation_id},
            ).scalar_one()
            == 1
        )
        assert connection.execute(text("SELECT count(*) FROM audit_receipts")).scalar_one() == 11


def test_stale_write_has_no_partial_mutation(
    runtime: tuple[Engine, UUID, UUID, UUID, UUID],
) -> None:
    engine, tenant, analyst, _, _ = runtime
    service, analyst_p, brief_id = (
        R1WorkflowService(),
        principal(analyst, tenant, LocalRole.ANALYST),
        uuid4(),
    )
    with engine.begin() as connection:
        service.create_role_brief(
            connection,
            principal=analyst_p,
            brief=brief(brief_id, tenant, analyst, 1, R1RoleBriefStatus.DRAFT),
            request_id=uuid4(),
        )
        submitted = brief(brief_id, tenant, analyst, 2, R1RoleBriefStatus.SUBMITTED)
        service.transition_role_brief(
            connection,
            principal=analyst_p,
            next_version=submitted,
            expected_lock_version=1,
            request_id=uuid4(),
        )
        with pytest.raises(WorkflowConflict):
            service.transition_role_brief(
                connection,
                principal=analyst_p,
                next_version=brief(brief_id, tenant, analyst, 3, R1RoleBriefStatus.DRAFT),
                expected_lock_version=1,
                request_id=uuid4(),
            )
        assert (
            connection.execute(
                text("SELECT count(*) FROM role_brief_revisions WHERE role_brief_id=:id"),
                {"id": brief_id},
            ).scalar_one()
            == 2
        )


def test_audit_failure_rolls_back_material_write_and_retry_recovers(
    runtime: tuple[Engine, UUID, UUID, UUID, UUID],
) -> None:
    engine, tenant, analyst, _, _ = runtime
    service = R1WorkflowService()
    analyst_p = principal(analyst, tenant, LocalRole.ANALYST)
    brief_id = uuid4()
    draft = brief(brief_id, tenant, analyst, 1, R1RoleBriefStatus.DRAFT)
    with engine.begin() as connection:
        connection.execute(
            text(
                """CREATE TRIGGER synthetic_receipt_failure BEFORE INSERT ON audit_receipts
                BEGIN SELECT RAISE(ABORT, 'synthetic audit failure'); END"""
            )
        )
        with pytest.raises(AuditIntegrityError):
            service.create_role_brief(
                connection, principal=analyst_p, brief=draft, request_id=uuid4()
            )
        assert (
            connection.execute(
                text("SELECT count(*) FROM role_brief_workflows WHERE role_brief_id=:id"),
                {"id": brief_id},
            ).scalar_one()
            == 0
        )
        connection.execute(text("DROP TRIGGER synthetic_receipt_failure"))
        service.create_role_brief(connection, principal=analyst_p, brief=draft, request_id=uuid4())
        assert (
            connection.execute(
                text("SELECT count(*) FROM role_brief_workflows WHERE role_brief_id=:id"),
                {"id": brief_id},
            ).scalar_one()
            == 1
        )

# ruff: noqa: E501
"""Transactional local R1 brief, retrieval, shortlist, and comment workflow.

This module deliberately accepts only already-authenticated local principals.  It
never calls a model or a remote service: retrieval links are immutable references to
the accepted local serving result and retain W06's ``NO_GO`` evidence boundary.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from scouting.audit.ledger import AuditLedger
from scouting.contracts import (
    AuditAction,
    AuditEvent,
    R1RoleBriefStatus,
    R1RoleBriefVersion,
    R1ShortlistEntryRevision,
    ReplayableRetrievalLink,
    ShortlistComment,
    TenantContext,
    WorkflowVisibility,
)
from scouting.policy.r1 import (
    R1AuthorizationDenied,
    R1AuthorizationPolicy,
    R1Principal,
    R1Resource,
)


class WorkflowConflict(RuntimeError):
    """A stale optimistic-lock write or illegal state transition."""


_BRIEF_TRANSITIONS = {
    (R1RoleBriefStatus.DRAFT, R1RoleBriefStatus.SUBMITTED),
    (R1RoleBriefStatus.SUBMITTED, R1RoleBriefStatus.APPROVED),
    (R1RoleBriefStatus.SUBMITTED, R1RoleBriefStatus.REJECTED),
    (R1RoleBriefStatus.SUBMITTED, R1RoleBriefStatus.DRAFT),
    (R1RoleBriefStatus.DRAFT, R1RoleBriefStatus.RETIRED),
    (R1RoleBriefStatus.APPROVED, R1RoleBriefStatus.RETIRED),
    (R1RoleBriefStatus.REJECTED, R1RoleBriefStatus.DRAFT),
}
_ENTRY_TRANSITIONS = {
    ("longlist", "monitor"),
    ("longlist", "scout"),
    ("monitor", "longlist"),
    ("monitor", "scout"),
    ("scout", "monitor"),
    ("scout", "shortlist"),
    ("longlist", "hold"),
    ("monitor", "hold"),
    ("scout", "hold"),
    ("shortlist", "hold"),
    ("hold", "longlist"),
    ("hold", "monitor"),
    ("hold", "scout"),
    ("hold", "shortlist"),
    ("longlist", "rejected"),
    ("monitor", "rejected"),
    ("scout", "rejected"),
    ("shortlist", "rejected"),
    ("hold", "rejected"),
    ("rejected", "longlist"),
}


def entry_transition_actions(next_state: str) -> tuple[str, ...]:
    """Return the explicit grants applicable to one entry transition target.

    Special targets intentionally have one sole grant.  Ordinary targets compose
    the owner-scoped analyst and approver grants, each evaluated against the same
    exact resource by the caller.
    """
    if next_state == "shortlist":
        return ("shortlist_entry.approve",)
    if next_state == "hold":
        return ("shortlist_entry.hold",)
    if next_state == "rejected":
        return ("shortlist_entry.reject_with_reason",)
    return ("shortlist_entry.transition_owned", "shortlist_entry.transition")


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _at() -> datetime:
    return datetime.now(UTC)


class R1WorkflowService:
    """Persistence operations which always write an audit receipt in the same savepoint."""

    def __init__(
        self, *, policy: R1AuthorizationPolicy | None = None, ledger: AuditLedger | None = None
    ) -> None:
        self._policy = policy or R1AuthorizationPolicy()
        self._ledger = ledger or AuditLedger()

    def create_role_brief(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        brief: R1RoleBriefVersion,
        request_id: UUID,
    ) -> None:
        if (
            brief.status is not R1RoleBriefStatus.DRAFT
            or brief.version != 1
            or brief.owner_id != principal.actor_id
            or brief.created_by != principal.actor_id
        ):
            raise WorkflowConflict("role brief creation requires an owner draft at version 1")
        self._require(
            principal,
            "role_brief.create",
            brief.tenant_context.tenant_id,
            brief.owner_id,
            brief.visibility,
        )
        with connection.begin_nested():
            now = _at().isoformat()
            connection.execute(
                text("""INSERT INTO role_brief_workflows
                (role_brief_id, tenant_id, owner_id, visibility, lock_version, latest_version, created_at, updated_at)
                VALUES (:id,:tenant,:owner,:visibility,1,1,:now,:now)"""),
                {
                    "id": brief.role_brief_id,
                    "tenant": brief.tenant_context.tenant_id,
                    "owner": brief.owner_id,
                    "visibility": brief.visibility.value,
                    "now": now,
                },
            )
            self._insert_brief_revision(connection, brief)
            self._audit(
                connection,
                principal,
                request_id,
                brief.trace_id,
                AuditAction.CREATE,
                "role_brief",
                brief.role_brief_id,
                None,
                _digest(brief.model_dump(mode="json")),
                str(brief.transition_reason),
            )

    def transition_role_brief(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        next_version: R1RoleBriefVersion,
        expected_lock_version: int,
        request_id: UUID,
    ) -> None:
        row = (
            connection.execute(
                text(
                    "SELECT owner_id, visibility, lock_version, latest_version FROM role_brief_workflows WHERE role_brief_id=:id AND tenant_id=:tenant"
                ),
                {"id": next_version.role_brief_id, "tenant": next_version.tenant_context.tenant_id},
            )
            .mappings()
            .one_or_none()
        )
        if (
            row is None
            or int(row["lock_version"]) != expected_lock_version
            or int(row["latest_version"]) + 1 != next_version.version
        ):
            raise WorkflowConflict("stale or absent role brief")
        prior = self._brief_row(connection, next_version.role_brief_id, int(row["latest_version"]))
        prior_status = R1RoleBriefStatus(str(prior["status"]))
        if (prior_status, next_version.status) not in _BRIEF_TRANSITIONS:
            raise WorkflowConflict("illegal role brief transition")
        action = self._brief_action(prior_status, next_version.status)
        self._require(
            principal,
            action,
            next_version.tenant_context.tenant_id,
            UUID(str(row["owner_id"])),
            str(row["visibility"]),
        )
        if next_version.owner_id != UUID(str(row["owner_id"])):
            raise R1AuthorizationDenied()
        if next_version.created_by != principal.actor_id:
            raise R1AuthorizationDenied()
        if (
            next_version.status
            in {
                R1RoleBriefStatus.APPROVED,
                R1RoleBriefStatus.REJECTED,
            }
            and next_version.decided_by != principal.actor_id
        ):
            raise R1AuthorizationDenied()
        if next_version.status in {
            R1RoleBriefStatus.SUBMITTED,
            R1RoleBriefStatus.APPROVED,
            R1RoleBriefStatus.REJECTED,
            R1RoleBriefStatus.RETIRED,
        } and not self._brief_content_matches(prior, next_version):
            raise WorkflowConflict("status transition cannot rewrite role brief content")
        with connection.begin_nested():
            result = connection.execute(
                text("""UPDATE role_brief_workflows SET lock_version=lock_version+1, latest_version=:version, visibility=:visibility, updated_at=:now
                WHERE role_brief_id=:id AND tenant_id=:tenant AND lock_version=:expected"""),
                {
                    "version": next_version.version,
                    "visibility": next_version.visibility.value,
                    "now": _at().isoformat(),
                    "id": next_version.role_brief_id,
                    "tenant": next_version.tenant_context.tenant_id,
                    "expected": expected_lock_version,
                },
            )
            if result.rowcount != 1:
                raise WorkflowConflict("stale role brief")
            self._insert_brief_revision(connection, next_version)
            self._audit(
                connection,
                principal,
                request_id,
                next_version.trace_id,
                AuditAction.UPDATE,
                "role_brief",
                next_version.role_brief_id,
                _digest(dict(prior)),
                _digest(next_version.model_dump(mode="json")),
                str(next_version.transition_reason),
            )

    def create_retrieval_link(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        link: ReplayableRetrievalLink,
        request_id: UUID,
    ) -> None:
        brief = self._brief_row(connection, link.role_brief_id, link.role_brief_version)
        if (
            brief is None
            or str(brief["tenant_id"]) != str(link.tenant_context.tenant_id)
            or brief["status"] != R1RoleBriefStatus.APPROVED.value
            or link.created_by != principal.actor_id
        ):
            raise WorkflowConflict(
                "retrieval links require an approved role brief owned by the actor"
            )
        self._require(
            principal,
            "retrieval_link.create_owned",
            link.tenant_context.tenant_id,
            UUID(str(brief["owner_id"])),
            str(brief["visibility"]),
        )
        if (
            link.claim_boundary != "resemblance_only"
            or link.evidence_class != "synthetic_development_only"
            or link.applicability != "LIMITED"
        ):
            raise WorkflowConflict("W06 NO_GO claim boundary cannot be widened")
        with connection.begin_nested():
            connection.execute(
                text("""INSERT INTO replayable_retrieval_links
                (retrieval_link_id,tenant_id,role_brief_id,role_brief_version,retrieval_request_id,retrieval_result_id,retrieval_run_id,query_player_id,exemplar_player_ids,model_version,index_version,data_version,taxonomy_version,result_digest,lineage_digest,claim_boundary,evidence_class,applicability,limitations,created_by,created_at)
                VALUES (:id,:tenant,:brief,:version,:request,:result,:run,:player,:exemplars,:model,:index,:data,:taxonomy,:result_digest,:lineage,:claim,:evidence,:applicability,:limitations,:actor,:created)"""),
                {
                    "id": link.retrieval_link_id,
                    "tenant": link.tenant_context.tenant_id,
                    "brief": link.role_brief_id,
                    "version": link.role_brief_version,
                    "request": link.retrieval_request_id,
                    "result": link.retrieval_result_id,
                    "run": link.retrieval_run_id,
                    "player": link.query_player_id,
                    "exemplars": _json(link.exemplar_player_ids),
                    "model": link.model_version,
                    "index": link.index_version,
                    "data": link.data_version,
                    "taxonomy": link.taxonomy_version,
                    "result_digest": link.result_digest,
                    "lineage": link.lineage_digest,
                    "claim": link.claim_boundary,
                    "evidence": link.evidence_class,
                    "applicability": link.applicability,
                    "limitations": _json(link.limitations),
                    "actor": link.created_by,
                    "created": link.created_at,
                },
            )
            self._audit(
                connection,
                principal,
                request_id,
                link.retrieval_request_id,
                AuditAction.CREATE,
                "replayable_retrieval_link",
                link.retrieval_link_id,
                None,
                _digest(link.model_dump(mode="json")),
                "pinned local W05 public-serving result; W06 NO_GO retained",
            )

    def create_shortlist(
        self,
        connection: Connection,
        *,
        shortlist_id: UUID,
        tenant_id: UUID,
        role_brief_id: UUID,
        role_brief_version: int,
        owner_id: UUID,
        visibility: WorkflowVisibility,
        title: str,
        principal: R1Principal,
        request_id: UUID,
    ) -> None:
        if owner_id != principal.actor_id:
            raise R1AuthorizationDenied()
        brief = self._brief_row(connection, role_brief_id, role_brief_version)
        if (
            brief is None
            or str(brief["tenant_id"]) != str(tenant_id)
            or brief["status"] != "approved"
        ):
            raise WorkflowConflict("shortlists require an approved role brief version")
        self._require(principal, "shortlist.create_owned", tenant_id, owner_id, visibility.value)
        with connection.begin_nested():
            now = _at().isoformat()
            connection.execute(
                text("""INSERT INTO workflow_shortlists (shortlist_id,tenant_id,role_brief_id,role_brief_version,owner_id,visibility,title,lock_version,created_at,updated_at)
            VALUES (:id,:tenant,:brief,:version,:owner,:visibility,:title,1,:now,:now)"""),
                {
                    "id": shortlist_id,
                    "tenant": tenant_id,
                    "brief": role_brief_id,
                    "version": role_brief_version,
                    "owner": owner_id,
                    "visibility": visibility.value,
                    "title": title,
                    "now": now,
                },
            )
            self._audit(
                connection,
                principal,
                request_id,
                uuid4(),
                AuditAction.CREATE,
                "workflow_shortlist",
                shortlist_id,
                None,
                _digest({"title": title, "role_brief_version": role_brief_version}),
                "create local shortlist",
            )

    def add_entry(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        revision: R1ShortlistEntryRevision,
        request_id: UUID,
    ) -> None:
        if (
            revision.revision != 1
            or revision.state.value != "longlist"
            or revision.owner_id != principal.actor_id
            or revision.changed_by != principal.actor_id
            or revision.assigned_scout_id is not None
        ):
            raise WorkflowConflict("entry creation requires an owner longlist revision")
        shortlist = self._shortlist_row(
            connection, revision.shortlist_id, revision.tenant_context.tenant_id
        )
        self._require(
            principal,
            "shortlist_entry.add_owned",
            revision.tenant_context.tenant_id,
            UUID(str(shortlist["owner_id"])),
            str(shortlist["visibility"]),
        )
        if not self._initial_entry_chain_is_persisted(connection, revision, shortlist):
            raise WorkflowConflict(
                "shortlist entry requires one approved persisted retrieval chain"
            )
        duplicate = connection.execute(
            text(
                """SELECT 1 FROM shortlist_entry_workflows
                WHERE tenant_id=:tenant AND shortlist_id=:shortlist AND player_id=:player"""
            ),
            {
                "tenant": revision.tenant_context.tenant_id,
                "shortlist": revision.shortlist_id,
                "player": revision.player_id,
            },
        ).scalar_one_or_none()
        if duplicate is not None:
            raise WorkflowConflict("duplicate shortlist candidate is denied")
        with connection.begin_nested():
            now = _at().isoformat()
            connection.execute(
                text("""INSERT INTO shortlist_entry_workflows (shortlist_entry_id,tenant_id,shortlist_id,player_id,lock_version,latest_revision,created_at,updated_at)
            VALUES (:id,:tenant,:shortlist,:player,1,1,:now,:now)"""),
                {
                    "id": revision.shortlist_entry_id,
                    "tenant": revision.tenant_context.tenant_id,
                    "shortlist": revision.shortlist_id,
                    "player": revision.player_id,
                    "now": now,
                },
            )
            self._insert_entry_revision(connection, revision)
            self._audit(
                connection,
                principal,
                request_id,
                uuid4(),
                AuditAction.CREATE,
                "shortlist_entry",
                revision.shortlist_entry_id,
                None,
                _digest(revision.model_dump(mode="json")),
                str(revision.transition_reason),
            )

    def transition_entry(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        next_revision: R1ShortlistEntryRevision,
        expected_lock_version: int,
        request_id: UUID,
    ) -> None:
        entry = (
            connection.execute(
                text(
                    "SELECT lock_version,latest_revision FROM shortlist_entry_workflows WHERE shortlist_entry_id=:id AND tenant_id=:tenant"
                ),
                {
                    "id": next_revision.shortlist_entry_id,
                    "tenant": next_revision.tenant_context.tenant_id,
                },
            )
            .mappings()
            .one_or_none()
        )
        if (
            entry is None
            or int(entry["lock_version"]) != expected_lock_version
            or int(entry["latest_revision"]) + 1 != next_revision.revision
        ):
            raise WorkflowConflict("stale or absent shortlist entry")
        if next_revision.changed_by != principal.actor_id:
            raise R1AuthorizationDenied()
        if next_revision.assigned_scout_id is not None and not self._is_enabled_same_tenant_scout(
            connection,
            tenant_id=next_revision.tenant_context.tenant_id,
            actor_id=next_revision.assigned_scout_id,
        ):
            raise R1AuthorizationDenied()
        prior = self._entry_row(
            connection, next_revision.shortlist_entry_id, int(entry["latest_revision"])
        )
        immutable_identity = {
            "shortlist_id": str(next_revision.shortlist_id),
            "role_brief_id": str(next_revision.role_brief_id),
            "role_brief_version": next_revision.role_brief_version,
            "player_id": str(next_revision.player_id),
            "retrieval_link_id": str(next_revision.retrieval_link_id),
            "owner_id": str(next_revision.owner_id),
        }
        if any(str(prior[name]) != str(value) for name, value in immutable_identity.items()):
            raise WorkflowConflict(
                "shortlist entry revision cannot rewrite pinned identity or evidence"
            )
        if (
            str(prior["state"]) == "rejected"
            and next_revision.state.value == "longlist"
            and not str(next_revision.transition_reason).strip()
        ):
            raise WorkflowConflict("reconsideration requires an attributable reason")
        if (str(prior["state"]), next_revision.state.value) not in _ENTRY_TRANSITIONS:
            raise WorkflowConflict("illegal shortlist entry transition")
        shortlist = self._shortlist_row(
            connection, next_revision.shortlist_id, next_revision.tenant_context.tenant_id
        )
        actions = entry_transition_actions(next_revision.state.value)
        self._require_any(
            principal,
            actions,
            next_revision.tenant_context.tenant_id,
            UUID(str(shortlist["owner_id"])),
            str(shortlist["visibility"]),
            frozenset({UUID(str(prior["assigned_scout_id"]))})
            if prior["assigned_scout_id"]
            else frozenset(),
        )
        with connection.begin_nested():
            result = connection.execute(
                text("""UPDATE shortlist_entry_workflows SET lock_version=lock_version+1,latest_revision=:revision,updated_at=:now
                WHERE shortlist_entry_id=:id AND tenant_id=:tenant AND lock_version=:expected"""),
                {
                    "revision": next_revision.revision,
                    "now": _at().isoformat(),
                    "id": next_revision.shortlist_entry_id,
                    "tenant": next_revision.tenant_context.tenant_id,
                    "expected": expected_lock_version,
                },
            )
            if result.rowcount != 1:
                raise WorkflowConflict("stale shortlist entry")
            self._insert_entry_revision(connection, next_revision)
            self._audit(
                connection,
                principal,
                request_id,
                uuid4(),
                AuditAction.UPDATE,
                "shortlist_entry",
                next_revision.shortlist_entry_id,
                _digest(dict(prior)),
                _digest(next_revision.model_dump(mode="json")),
                str(next_revision.transition_reason),
            )

    def add_comment(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        comment: ShortlistComment,
        request_id: UUID,
    ) -> None:
        entry = (
            connection.execute(
                text("""SELECT e.shortlist_entry_id,s.owner_id,s.visibility,r.assigned_scout_id
            FROM shortlist_entry_workflows e
            JOIN workflow_shortlists s ON s.shortlist_id=e.shortlist_id AND s.tenant_id=e.tenant_id
            JOIN shortlist_entry_revisions r ON r.shortlist_entry_id=e.shortlist_entry_id AND r.revision=e.latest_revision
            WHERE e.shortlist_entry_id=:id AND e.tenant_id=:tenant"""),
                {"id": comment.shortlist_entry_id, "tenant": comment.tenant_context.tenant_id},
            )
            .mappings()
            .one_or_none()
        )
        if entry is None or comment.author_id != principal.actor_id:
            raise R1AuthorizationDenied()
        self._require(
            principal,
            "shortlist_comment.create",
            comment.tenant_context.tenant_id,
            UUID(str(entry["owner_id"])),
            str(entry["visibility"]),
            frozenset()
            if entry["assigned_scout_id"] is None
            else frozenset({UUID(str(entry["assigned_scout_id"]))}),
        )
        with connection.begin_nested():
            connection.execute(
                text("""INSERT INTO shortlist_comments (comment_id,tenant_id,shortlist_entry_id,author_id,visibility,body,evidence_origin,created_at)
                VALUES (:id,:tenant,:entry,:author,:visibility,:body,:origin,:created)"""),
                {
                    "id": comment.comment_id,
                    "tenant": comment.tenant_context.tenant_id,
                    "entry": comment.shortlist_entry_id,
                    "author": comment.author_id,
                    "visibility": comment.visibility.value,
                    "body": comment.body,
                    "origin": comment.evidence_origin.value,
                    "created": comment.created_at,
                },
            )
            self._audit(
                connection,
                principal,
                request_id,
                uuid4(),
                AuditAction.CREATE,
                "shortlist_comment",
                comment.comment_id,
                None,
                _digest(comment.model_dump(mode="json")),
                "append-only workflow comment",
            )

    def _insert_brief_revision(self, connection: Connection, brief: R1RoleBriefVersion) -> None:
        connection.execute(
            text("""INSERT INTO role_brief_revisions (role_brief_id,tenant_id,version,previous_version,trace_id,owner_id,created_by,visibility,title,template_id,taxonomy_version,status,responsibilities,hard_constraints,preferences,exemplar_player_ids,transition_reason,rejection_reason,decision_note,submitted_at,decided_at,decided_by,created_at)
        VALUES (:id,:tenant,:version,:previous,:trace,:owner,:created_by,:visibility,:title,:template,:taxonomy,:status,:responsibilities,:constraints,:preferences,:exemplars,:reason,:reject,:note,:submitted,:decided,:decided_by,:created)"""),
            {
                "id": brief.role_brief_id,
                "tenant": brief.tenant_context.tenant_id,
                "version": brief.version,
                "previous": brief.previous_version,
                "trace": brief.trace_id,
                "owner": brief.owner_id,
                "created_by": brief.created_by,
                "visibility": brief.visibility.value,
                "title": brief.title,
                "template": brief.template_id,
                "taxonomy": brief.taxonomy_version,
                "status": brief.status.value,
                "responsibilities": _json(brief.responsibilities),
                "constraints": _json([x.model_dump(mode="json") for x in brief.hard_constraints]),
                "preferences": _json([x.model_dump(mode="json") for x in brief.preferences]),
                "exemplars": _json(brief.exemplar_player_ids),
                "reason": brief.transition_reason,
                "reject": None if brief.rejection_reason is None else brief.rejection_reason.value,
                "note": brief.decision_note,
                "submitted": brief.submitted_at,
                "decided": brief.decided_at,
                "decided_by": brief.decided_by,
                "created": brief.created_at,
            },
        )

    @staticmethod
    def _brief_content_matches(prior: Any, next_version: R1RoleBriefVersion) -> bool:
        """Approval/status revisions preserve the exact replayable brief interpretation."""
        expected = {
            "owner_id": str(next_version.owner_id),
            "visibility": next_version.visibility.value,
            "title": str(next_version.title),
            "template_id": str(next_version.template_id),
            "taxonomy_version": str(next_version.taxonomy_version),
            "responsibilities": _json(next_version.responsibilities),
            "hard_constraints": _json(
                [item.model_dump(mode="json") for item in next_version.hard_constraints]
            ),
            "preferences": _json(
                [item.model_dump(mode="json") for item in next_version.preferences]
            ),
            "exemplar_player_ids": _json(next_version.exemplar_player_ids),
        }
        return all(str(prior[column]) == value for column, value in expected.items())

    def _initial_entry_chain_is_persisted(
        self, connection: Connection, revision: R1ShortlistEntryRevision, shortlist: Any
    ) -> bool:
        """Require the initial candidate to pin one tenant-local approved evidence chain."""
        if (
            str(shortlist["role_brief_id"]) != str(revision.role_brief_id)
            or int(shortlist["role_brief_version"]) != revision.role_brief_version
            or str(shortlist["owner_id"]) != str(revision.owner_id)
        ):
            return False
        link = (
            connection.execute(
                text(
                    """SELECT tenant_id, role_brief_id, role_brief_version
                FROM replayable_retrieval_links
                WHERE retrieval_link_id=:link AND tenant_id=:tenant"""
                ),
                {
                    "link": revision.retrieval_link_id,
                    "tenant": revision.tenant_context.tenant_id,
                },
            )
            .mappings()
            .one_or_none()
        )
        if link is None or (
            str(link["role_brief_id"]) != str(revision.role_brief_id)
            or int(link["role_brief_version"]) != revision.role_brief_version
        ):
            return False
        brief = self._brief_row(connection, revision.role_brief_id, revision.role_brief_version)
        return bool(
            brief is not None
            and str(brief["tenant_id"]) == str(revision.tenant_context.tenant_id)
            and str(brief["status"]) == R1RoleBriefStatus.APPROVED.value
        )

    @staticmethod
    def _is_enabled_same_tenant_scout(
        connection: Connection, *, tenant_id: UUID, actor_id: UUID
    ) -> bool:
        """Resolve an assignment without revealing whether account, role, or state failed."""
        return (
            connection.execute(
                text(
                    """SELECT 1 FROM local_accounts account
                    JOIN local_account_roles role ON role.actor_id=account.actor_id
                    WHERE account.actor_id=:actor AND account.tenant_id=:tenant
                      AND account.enabled=1 AND role.role='scout'"""
                ),
                {"actor": actor_id, "tenant": tenant_id},
            ).scalar_one_or_none()
            == 1
        )

    def _insert_entry_revision(
        self, connection: Connection, value: R1ShortlistEntryRevision
    ) -> None:
        connection.execute(
            text("""INSERT INTO shortlist_entry_revisions (shortlist_entry_id,tenant_id,shortlist_id,revision,previous_revision,role_brief_id,role_brief_version,player_id,state,owner_id,assigned_scout_id,retrieval_link_id,rationale,transition_reason,rejection_reason,hold_reason,reason_note,next_action,next_action_owner_id,changed_by,created_at)
        VALUES (:id,:tenant,:shortlist,:revision,:previous,:brief,:brief_version,:player,:state,:owner,:scout,:link,:rationale,:reason,:reject,:hold,:note,:next_action,:next_owner,:changed,:created)"""),
            {
                "id": value.shortlist_entry_id,
                "tenant": value.tenant_context.tenant_id,
                "shortlist": value.shortlist_id,
                "revision": value.revision,
                "previous": value.previous_revision,
                "brief": value.role_brief_id,
                "brief_version": value.role_brief_version,
                "player": value.player_id,
                "state": value.state.value,
                "owner": value.owner_id,
                "scout": value.assigned_scout_id,
                "link": value.retrieval_link_id,
                "rationale": value.rationale,
                "reason": value.transition_reason,
                "reject": None if value.rejection_reason is None else value.rejection_reason.value,
                "hold": None if value.hold_reason is None else value.hold_reason.value,
                "note": value.reason_note,
                "next_action": value.next_action,
                "next_owner": value.next_action_owner_id,
                "changed": value.changed_by,
                "created": value.created_at,
            },
        )

    def _brief_row(self, connection: Connection, role_brief_id: UUID, version: int) -> Any:
        return (
            connection.execute(
                text(
                    "SELECT * FROM role_brief_revisions WHERE role_brief_id=:id AND version=:version"
                ),
                {"id": role_brief_id, "version": version},
            )
            .mappings()
            .one_or_none()
        )

    def _entry_row(self, connection: Connection, entry_id: UUID, revision: int) -> Any:
        return (
            connection.execute(
                text(
                    "SELECT * FROM shortlist_entry_revisions WHERE shortlist_entry_id=:id AND revision=:revision"
                ),
                {"id": entry_id, "revision": revision},
            )
            .mappings()
            .one()
        )

    def _shortlist_row(self, connection: Connection, shortlist_id: UUID, tenant_id: UUID) -> Any:
        row = (
            connection.execute(
                text(
                    "SELECT * FROM workflow_shortlists WHERE shortlist_id=:id AND tenant_id=:tenant"
                ),
                {"id": shortlist_id, "tenant": tenant_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise R1AuthorizationDenied()
        return row

    def _require(
        self,
        principal: R1Principal,
        action: str,
        tenant_id: UUID,
        owner_id: UUID,
        visibility: str,
        assigned: frozenset[UUID] = frozenset(),
    ) -> None:
        self._policy.require(
            principal,
            action=action,
            resource=R1Resource(
                tenant_id=tenant_id,
                owner_actor_id=owner_id,
                visibility=visibility,
                assigned_actor_ids=assigned,
            ),
        )

    def _require_any(
        self,
        principal: R1Principal,
        actions: tuple[str, ...],
        tenant_id: UUID,
        owner_id: UUID,
        visibility: str,
        assigned: frozenset[UUID] = frozenset(),
    ) -> None:
        """Require one explicit action grant for this exact transition resource."""
        resource = R1Resource(
            tenant_id=tenant_id,
            owner_actor_id=owner_id,
            visibility=visibility,
            assigned_actor_ids=assigned,
        )
        if not any(
            self._policy.authorize(principal, action=action, resource=resource)
            for action in actions
        ):
            raise R1AuthorizationDenied()

    @staticmethod
    def _brief_action(prior: R1RoleBriefStatus, next_status: R1RoleBriefStatus) -> str:
        if next_status is R1RoleBriefStatus.APPROVED:
            return "role_brief.approve"
        if next_status is R1RoleBriefStatus.REJECTED:
            return "role_brief.reject"
        return (
            "role_brief.submit_owned"
            if next_status is R1RoleBriefStatus.SUBMITTED
            else "role_brief.version_owned"
        )

    def _audit(
        self,
        connection: Connection,
        principal: R1Principal,
        request_id: UUID,
        trace_id: UUID,
        action: AuditAction,
        target_type: str,
        target_id: UUID,
        before: str | None,
        after: str | None,
        reason: str,
    ) -> None:
        self._ledger.append(
            connection,
            AuditEvent(
                audit_event_id=uuid4(),
                tenant_context=TenantContext(tenant_id=principal.tenant_id),
                trace_id=trace_id,
                request_id=request_id,
                actor_id=principal.actor_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                occurred_at=_at(),
                before_digest=before,
                after_digest=after,
                reason=reason,
            ),
        )

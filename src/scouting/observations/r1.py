# ruff: noqa: E501
"""Versioned local scout observations with restrictive visibility and audit receipts."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from scouting.audit.ledger import AuditLedger
from scouting.contracts import AuditAction, AuditEvent, ScoutObservationVersion, TenantContext
from scouting.policy.r1 import R1AuthorizationDenied, R1AuthorizationPolicy, R1Principal, R1Resource
from scouting.workflow.r1 import WorkflowConflict


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


class ScoutObservationService:
    """Persists immutable observation versions; amendments never alter earlier evidence."""

    def __init__(
        self, *, policy: R1AuthorizationPolicy | None = None, ledger: AuditLedger | None = None
    ) -> None:
        self._policy = policy or R1AuthorizationPolicy()
        self._ledger = ledger or AuditLedger()

    def create(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        observation: ScoutObservationVersion,
        request_id: UUID,
    ) -> None:
        if observation.version != 1 or observation.author_id != principal.actor_id:
            raise R1AuthorizationDenied()
        resource = self._entry_resource(
            connection, observation.shortlist_entry_id, observation.tenant_context.tenant_id
        )
        self._policy.require(principal, action="observation.create_assigned", resource=resource)
        with connection.begin_nested():
            self._insert(connection, observation)
            self._audit(connection, principal, request_id, observation, AuditAction.CREATE, None)

    def amend(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        observation: ScoutObservationVersion,
        expected_version: int,
        request_id: UUID,
    ) -> None:
        if (
            observation.version != expected_version + 1
            or observation.previous_version != expected_version
            or observation.author_id != principal.actor_id
        ):
            raise WorkflowConflict("stale or malformed observation amendment")
        current = (
            connection.execute(
                text(
                    """SELECT author_id, version, shortlist_entry_id, evidence_origin
                    FROM scout_observations
                    WHERE observation_id=:id AND tenant_id=:tenant
                    ORDER BY version DESC LIMIT 1"""
                ),
                {"id": observation.observation_id, "tenant": observation.tenant_context.tenant_id},
            )
            .mappings()
            .one_or_none()
        )
        if (
            current is None
            or int(current["version"]) != expected_version
            or UUID(str(current["author_id"])) != principal.actor_id
            or UUID(str(current["shortlist_entry_id"])) != observation.shortlist_entry_id
            or str(current["evidence_origin"]) != observation.evidence_origin.value
        ):
            raise WorkflowConflict("stale or unauthorised observation amendment")
        resource = self._entry_resource(
            connection, observation.shortlist_entry_id, observation.tenant_context.tenant_id
        )
        self._policy.require(principal, action="observation.amend_own", resource=resource)
        with connection.begin_nested():
            self._insert(connection, observation)
            self._audit(
                connection,
                principal,
                request_id,
                observation,
                AuditAction.UPDATE,
                _digest(dict(current)),
            )

    def visible_versions(
        self, connection: Connection, *, principal: R1Principal, shortlist_entry_id: UUID
    ) -> list[dict[str, object]]:
        resource = self._entry_resource(connection, shortlist_entry_id, principal.tenant_id)
        rows = (
            connection.execute(
                text(
                    "SELECT * FROM scout_observations WHERE tenant_id=:tenant AND shortlist_entry_id=:entry ORDER BY observation_id, version"
                ),
                {"tenant": principal.tenant_id, "entry": shortlist_entry_id},
            )
            .mappings()
            .all()
        )
        visible: list[dict[str, object]] = []
        for row in rows:
            own = UUID(str(row["author_id"])) == principal.actor_id
            action = "observation.read_own" if own else "observation.read_team_visible"
            observation_resource = R1Resource(
                tenant_id=resource.tenant_id,
                owner_actor_id=resource.owner_actor_id,
                visibility=str(row["visibility"]),
                assigned_actor_ids=resource.assigned_actor_ids
                | frozenset({UUID(str(row["author_id"]))}),
            )
            if self._policy.authorize(principal, action=action, resource=observation_resource):
                visible.append(dict(row))
        return visible

    def _entry_resource(
        self, connection: Connection, entry_id: UUID, tenant_id: UUID
    ) -> R1Resource:
        row = (
            connection.execute(
                text("""SELECT s.tenant_id,s.owner_id,s.visibility,r.assigned_scout_id FROM shortlist_entry_workflows e
        JOIN workflow_shortlists s ON s.shortlist_id=e.shortlist_id AND s.tenant_id=e.tenant_id
        JOIN shortlist_entry_revisions r ON r.shortlist_entry_id=e.shortlist_entry_id AND r.revision=e.latest_revision
        WHERE e.shortlist_entry_id=:entry AND e.tenant_id=:tenant"""),
                {"entry": entry_id, "tenant": tenant_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise R1AuthorizationDenied()
        assigned = (
            frozenset()
            if row["assigned_scout_id"] is None
            else frozenset({UUID(str(row["assigned_scout_id"]))})
        )
        return R1Resource(
            tenant_id=UUID(str(row["tenant_id"])),
            owner_actor_id=UUID(str(row["owner_id"])),
            visibility=str(row["visibility"]),
            assigned_actor_ids=assigned,
        )

    def _insert(self, connection: Connection, value: ScoutObservationVersion) -> None:
        connection.execute(
            text("""INSERT INTO scout_observations (observation_id,tenant_id,version,previous_version,shortlist_entry_id,author_id,visibility,dimensions,overall_confidence,evidence_references,summary,disagreement,disagreement_reason,recommended_next_action,evidence_origin,created_at)
        VALUES (:id,:tenant,:version,:previous,:entry,:author,:visibility,:dimensions,:confidence,:refs,:summary,:disagreement,:why,:next,:origin,:created)"""),
            {
                "id": value.observation_id,
                "tenant": value.tenant_context.tenant_id,
                "version": value.version,
                "previous": value.previous_version,
                "entry": value.shortlist_entry_id,
                "author": value.author_id,
                "visibility": value.visibility.value,
                "dimensions": json.dumps([d.model_dump(mode="json") for d in value.dimensions]),
                "confidence": value.overall_confidence,
                "refs": json.dumps([r.model_dump(mode="json") for r in value.evidence_references]),
                "summary": value.summary,
                "disagreement": int(value.disagreement),
                "why": value.disagreement_reason,
                "next": value.recommended_next_action,
                "origin": value.evidence_origin.value,
                "created": value.created_at,
            },
        )

    def _audit(
        self,
        connection: Connection,
        principal: R1Principal,
        request_id: UUID,
        value: ScoutObservationVersion,
        action: AuditAction,
        before: str | None,
    ) -> None:
        self._ledger.append(
            connection,
            AuditEvent(
                audit_event_id=uuid4(),
                tenant_context=TenantContext(tenant_id=value.tenant_context.tenant_id),
                trace_id=uuid4(),
                request_id=request_id,
                actor_id=principal.actor_id,
                action=action,
                target_type="scout_observation",
                target_id=value.observation_id,
                occurred_at=datetime.now(UTC),
                before_digest=before,
                after_digest=_digest(value.model_dump(mode="json")),
                reason="versioned scout observation",
            ),
        )

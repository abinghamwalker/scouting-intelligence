"""One app-role transaction for the synthetic role-brief-to-audit journey."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

from scouting.audit import AuditWriter
from scouting.contracts import (
    AuditAction,
    AuditEvent,
    RetrievalCandidate,
    RetrievalRequest,
    RetrievalResult,
    RoleBrief,
    ShortlistEntry,
    ShortlistEntryState,
    TenantContext,
)
from scouting.policy import (
    AuthorizationPolicy,
    AuthorizationRequest,
    ResourceContext,
    SyntheticPrincipal,
)
from scouting.serving import ServingExplanation, SyntheticServingService
from scouting.storage.embedded import EMBEDDED_DATABASE_USER

_AUDIT_ACTIONS = (
    "role_brief.approved",
    "retrieval.executed",
    "evidence.viewed",
    "shortlist.entry_created",
)


@dataclass(frozen=True, slots=True)
class ApplicationIdentity:
    """Verified embedded-store identity established before domain access."""

    current_user: str
    tenant_id: UUID


class ApplicationDatabase:
    """The single-tenant workflow boundary around the embedded database."""

    def __init__(self, engine: Engine, *, tenant_id: UUID) -> None:
        self._engine = engine
        self._tenant_id = tenant_id

    @contextmanager
    def transaction(self, tenant_id: UUID) -> Iterator[tuple[Connection, ApplicationIdentity]]:
        """Enter one application transaction for the configured local tenant."""
        if tenant_id != self._tenant_id:
            raise PermissionError("action denied")
        with self._engine.begin() as connection:
            stored_tenants = (
                connection.execute(text("SELECT tenant_id FROM tenants")).scalars().all()
            )
            if stored_tenants != [str(self._tenant_id)]:
                raise RuntimeError("embedded tenant boundary was not established")
            identity = ApplicationIdentity(
                current_user=EMBEDDED_DATABASE_USER,
                tenant_id=self._tenant_id,
            )
            yield connection, identity


@dataclass(frozen=True, slots=True)
class JourneyCommand:
    """Contract-bound human action inputs for one deterministic journey."""

    role_brief: RoleBrief
    retrieval_request: RetrievalRequest
    shortlist_id: UUID
    shortlist_entry_id: UUID
    rationale: str

    def __post_init__(self) -> None:
        if not self.rationale.strip() or len(self.rationale) > 512:
            raise ValueError("shortlist rationale must be between 1 and 512 characters")


@dataclass(frozen=True, slots=True)
class JourneyResult:
    """Successful journey evidence returned to the composition layer."""

    retrieval_result: RetrievalResult
    explanations: tuple[ServingExplanation, ...]
    shortlist_entry: ShortlistEntry
    audit_actions: tuple[str, ...]
    database_identity: ApplicationIdentity
    admitted_fact_ids: tuple[UUID, ...]
    rejected_evidence: tuple[tuple[UUID, str], ...]


class WorkflowService:
    """Compose authorization, serving, writes, and audit atomically."""

    def __init__(
        self,
        *,
        database: ApplicationDatabase,
        authorization: AuthorizationPolicy,
        serving: SyntheticServingService,
        audit_writer: AuditWriter,
    ) -> None:
        self._database = database
        self._authorization = authorization
        self._serving = serving
        self._audit_writer = audit_writer

    def execute_journey(
        self,
        *,
        principal: SyntheticPrincipal,
        request_id: UUID,
        command: JourneyCommand,
    ) -> JourneyResult:
        """Execute the full material path on one fail-closed transaction."""
        tenant_id = command.role_brief.tenant_context.tenant_id
        if principal.tenant_id != tenant_id:
            self._require(
                principal=principal,
                request_id=request_id,
                action="role_brief.create",
                resource_type="role_brief",
                resource_id=command.role_brief.role_brief_id,
                resource_tenant_id=tenant_id,
                owner_actor_id=command.role_brief.owner_id,
            )
        if command.role_brief.owner_id != principal.actor_id:
            raise PermissionError("action denied")

        with self._database.transaction(tenant_id) as (connection, database_identity):
            self._require_journey_actions(principal, request_id, command)
            outcome = self._serving.retrieve(
                command.role_brief,
                command.retrieval_request,
            )
            if outcome.status != "available" or outcome.result is None:
                missing = ",".join(outcome.missing_evidence) or "required serving evidence"
                raise RuntimeError(f"retrieval unavailable: {missing}")
            if not outcome.result.candidates:
                raise RuntimeError("retrieval unavailable: no eligible candidate")

            retrieval_result = outcome.result
            candidate = retrieval_result.candidates[0]
            shortlist_entry = self._shortlist_entry(
                command=command,
                result=retrieval_result,
                candidate=candidate,
            )
            self._insert_role_brief(connection, command.role_brief)
            self._append_audit(
                connection,
                event=self._event(
                    request_id=request_id,
                    principal=principal,
                    trace_id=command.role_brief.trace_id,
                    action=AuditAction.CREATE,
                    target_type=_AUDIT_ACTIONS[0],
                    target_id=command.role_brief.role_brief_id,
                    occurred_at=command.role_brief.approved_at or command.role_brief.created_at,
                    after=command.role_brief.model_dump(mode="json"),
                    reason="synthetic approved brief entered local review",
                ),
            )

            self._insert_retrieval(connection, retrieval_result, candidate)
            self._append_audit(
                connection,
                event=self._event(
                    request_id=request_id,
                    principal=principal,
                    trace_id=retrieval_result.trace_id,
                    action=AuditAction.CREATE,
                    target_type=_AUDIT_ACTIONS[1],
                    target_id=retrieval_result.retrieval_result_id,
                    occurred_at=retrieval_result.generated_at,
                    after=retrieval_result.model_dump(mode="json"),
                    reason="deterministic synthetic retrieval executed",
                ),
            )
            self._append_audit(
                connection,
                event=self._event(
                    request_id=request_id,
                    principal=principal,
                    trace_id=retrieval_result.trace_id,
                    action=AuditAction.READ,
                    target_type=_AUDIT_ACTIONS[2],
                    target_id=candidate.player_id,
                    occurred_at=retrieval_result.generated_at + timedelta(microseconds=1),
                    after=candidate.model_dump(mode="json"),
                    reason="synthetic evidence inspected",
                ),
            )

            self._insert_shortlist(connection, command, shortlist_entry)
            self._append_audit(
                connection,
                event=self._event(
                    request_id=request_id,
                    principal=principal,
                    trace_id=shortlist_entry.trace_id,
                    action=AuditAction.CREATE,
                    target_type=_AUDIT_ACTIONS[3],
                    target_id=shortlist_entry.shortlist_entry_id,
                    occurred_at=shortlist_entry.created_at,
                    after=shortlist_entry.model_dump(mode="json"),
                    reason=shortlist_entry.rationale,
                ),
            )
            return JourneyResult(
                retrieval_result=retrieval_result,
                explanations=outcome.explanations,
                shortlist_entry=shortlist_entry,
                audit_actions=_AUDIT_ACTIONS,
                database_identity=database_identity,
                admitted_fact_ids=outcome.admitted_fact_ids,
                rejected_evidence=tuple(
                    (evidence.fact_id, evidence.reason_code)
                    for evidence in outcome.rejected_evidence
                ),
            )

    def readiness(self, tenant_id: UUID) -> ApplicationIdentity:
        """Prove the same app-role boundary without touching domain tables."""
        with self._database.transaction(tenant_id) as (_, identity):
            return identity

    def audit_denied_confidential_action(
        self,
        *,
        principal: SyntheticPrincipal,
        request_id: UUID,
        target_id: UUID,
        action: Literal["read", "export"],
    ) -> ApplicationIdentity:
        """Retain a content-free denial attempt without reading the target."""
        policy_action = f"confidential_evidence.{action}_unauthorised"
        decision = self._authorization.authorize(
            AuthorizationRequest(
                principal=principal,
                action=policy_action,
                resource=ResourceContext(
                    resource_type="confidential_evidence",
                    resource_id=target_id,
                    tenant_id=principal.tenant_id,
                    owner_actor_id=principal.actor_id,
                    visibility="OWNER_ONLY",
                ),
                request_id=request_id,
            )
        )
        reason = "authorization_denied" if not decision.allowed else "policy_conflict_denied"
        audit_action = AuditAction.READ if action == "read" else AuditAction.EXPORT
        export_scope = () if action == "read" else ("denied_attempt",)
        event = AuditEvent(
            audit_event_id=uuid5(
                NAMESPACE_URL,
                f"w03-denial-audit:{request_id}:{action}:{target_id}",
            ),
            tenant_context=TenantContext(tenant_id=principal.tenant_id),
            trace_id=request_id,
            request_id=request_id,
            actor_id=principal.actor_id,
            action=audit_action,
            target_type="confidential_evidence.denied_attempt",
            target_id=target_id,
            occurred_at=datetime.now(UTC),
            reason=reason,
            export_scope=export_scope,
        )
        with self._database.transaction(principal.tenant_id) as (connection, identity):
            self._append_audit(connection, event=event)
            return identity

    def _require_journey_actions(
        self,
        principal: SyntheticPrincipal,
        request_id: UUID,
        command: JourneyCommand,
    ) -> None:
        brief = command.role_brief
        resources = (
            (
                "role_brief.create",
                "role_brief",
                brief.role_brief_id,
                brief.tenant_context.tenant_id,
                brief.owner_id,
            ),
            (
                "retrieval.create",
                "retrieval",
                command.retrieval_request.retrieval_request_id,
                command.retrieval_request.tenant_context.tenant_id,
                brief.owner_id,
            ),
            (
                "player.evidence.read",
                "player_evidence",
                brief.role_brief_id,
                brief.tenant_context.tenant_id,
                brief.owner_id,
            ),
            (
                "shortlist_entry.add",
                "shortlist_entry",
                command.shortlist_entry_id,
                brief.tenant_context.tenant_id,
                brief.owner_id,
            ),
        )
        for action, resource_type, resource_id, tenant_id, owner_id in resources:
            self._require(
                principal=principal,
                request_id=request_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_tenant_id=tenant_id,
                owner_actor_id=owner_id,
            )

    def _require(
        self,
        *,
        principal: SyntheticPrincipal,
        request_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        resource_tenant_id: UUID,
        owner_actor_id: UUID,
    ) -> None:
        self._authorization.require(
            AuthorizationRequest(
                principal=principal,
                action=action,
                resource=ResourceContext(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    tenant_id=resource_tenant_id,
                    owner_actor_id=owner_actor_id,
                    visibility="OWNER_ONLY",
                ),
                request_id=request_id,
            )
        )

    @staticmethod
    def _shortlist_entry(
        *,
        command: JourneyCommand,
        result: RetrievalResult,
        candidate: RetrievalCandidate,
    ) -> ShortlistEntry:
        created_at = result.generated_at + timedelta(minutes=1, seconds=59)
        return ShortlistEntry(
            shortlist_entry_id=command.shortlist_entry_id,
            shortlist_id=command.shortlist_id,
            tenant_context=result.tenant_context,
            version=1,
            trace_id=result.trace_id,
            player_id=candidate.player_id,
            state=ShortlistEntryState.SHORTLIST,
            owner_id=command.role_brief.owner_id,
            rationale=command.rationale,
            created_at=created_at,
            updated_at=created_at,
            retrieval_run_id=result.retrieval_run_id,
            rank_at_addition=candidate.rank,
            model_version_at_addition=result.model_version,
        )

    @staticmethod
    def _insert_role_brief(connection: Connection, brief: RoleBrief) -> None:
        parameters = {
            "role_brief_id": brief.role_brief_id,
            "tenant_id": brief.tenant_context.tenant_id,
            "version": brief.version,
            "trace_id": brief.trace_id,
            "owner_id": brief.owner_id,
            "team_id": brief.team_id,
            "title": brief.title,
            "taxonomy_version": brief.taxonomy_version,
            "status": brief.status.value,
            "responsibilities": json.dumps(brief.responsibilities),
            "hard_constraints": json.dumps(
                [constraint.model_dump(mode="json") for constraint in brief.hard_constraints]
            ),
            "preferences": json.dumps(
                [preference.model_dump(mode="json") for preference in brief.preferences]
            ),
            "exemplar_player_ids": json.dumps(
                [str(player_id) for player_id in brief.exemplar_player_ids]
            ),
            "created_at": brief.created_at,
            "approved_at": brief.approved_at,
        }
        inserted = connection.execute(
            text(
                """
                INSERT INTO role_briefs (
                    role_brief_id, tenant_id, version, trace_id, owner_id, team_id,
                    title, taxonomy_version, status, responsibilities, hard_constraints,
                    preferences, exemplar_player_ids, created_at, approved_at
                )
                VALUES (
                    :role_brief_id, :tenant_id, :version, :trace_id, :owner_id, :team_id,
                    :title, :taxonomy_version, :status, :responsibilities,
                    :hard_constraints, :preferences, :exemplar_player_ids,
                    :created_at, :approved_at
                )
                ON CONFLICT (role_brief_id, version) DO NOTHING
                RETURNING role_brief_id
                """
            ),
            parameters,
        ).scalar_one_or_none()
        if inserted is not None:
            return
        _require_exact_persisted_row(
            connection,
            """
            SELECT 1
            FROM role_briefs
            WHERE role_brief_id = :role_brief_id
              AND version = :version
              AND tenant_id IS NOT DISTINCT FROM :tenant_id
              AND trace_id IS NOT DISTINCT FROM :trace_id
              AND owner_id IS NOT DISTINCT FROM :owner_id
              AND team_id IS NOT DISTINCT FROM :team_id
              AND title IS NOT DISTINCT FROM :title
              AND taxonomy_version IS NOT DISTINCT FROM :taxonomy_version
              AND status IS NOT DISTINCT FROM :status
              AND responsibilities IS NOT DISTINCT FROM :responsibilities
              AND hard_constraints IS NOT DISTINCT FROM :hard_constraints
              AND preferences IS NOT DISTINCT FROM :preferences
              AND exemplar_player_ids IS NOT DISTINCT FROM :exemplar_player_ids
              AND created_at IS NOT DISTINCT FROM :created_at
              AND approved_at IS NOT DISTINCT FROM :approved_at
            """,
            parameters,
        )

    @staticmethod
    def _insert_retrieval(
        connection: Connection,
        result: RetrievalResult,
        candidate: RetrievalCandidate,
    ) -> None:
        retrieval_parameters = {
            "retrieval_run_id": result.retrieval_run_id,
            "tenant_id": result.tenant_context.tenant_id,
            "retrieval_request_id": result.retrieval_request_id,
            "retrieval_result_id": result.retrieval_result_id,
            "role_brief_id": result.role_brief_id,
            "role_brief_version": result.role_brief_version,
            "trace_id": result.trace_id,
            "feature_cutoff_ts": result.temporal_evidence.feature_cutoff_ts,
            "generated_at": result.generated_at,
            "model_version": result.model_version,
            "index_version": result.index_version,
            "lineage_hash": result.temporal_evidence.dependency_lineage_hash,
            "status": "complete",
            "created_at": result.generated_at,
        }
        inserted_retrieval = connection.execute(
            text(
                """
                INSERT INTO retrieval_runs (
                    retrieval_run_id, tenant_id, retrieval_request_id,
                    retrieval_result_id, role_brief_id, role_brief_version, trace_id,
                    feature_cutoff_ts, generated_at, model_version, index_version,
                    dependency_lineage_hash, status, created_at
                )
                VALUES (
                    :retrieval_run_id, :tenant_id, :retrieval_request_id,
                    :retrieval_result_id, :role_brief_id, :role_brief_version, :trace_id,
                    :feature_cutoff_ts, :generated_at, :model_version, :index_version,
                    :lineage_hash, :status, :created_at
                )
                ON CONFLICT DO NOTHING
                RETURNING retrieval_run_id
                """
            ),
            retrieval_parameters,
        ).scalar_one_or_none()
        if inserted_retrieval is None:
            _require_exact_persisted_row(
                connection,
                """
                SELECT 1
                FROM retrieval_runs
                WHERE retrieval_run_id = :retrieval_run_id
                  AND tenant_id IS NOT DISTINCT FROM :tenant_id
                  AND retrieval_request_id IS NOT DISTINCT FROM :retrieval_request_id
                  AND retrieval_result_id IS NOT DISTINCT FROM :retrieval_result_id
                  AND role_brief_id IS NOT DISTINCT FROM :role_brief_id
                  AND role_brief_version IS NOT DISTINCT FROM :role_brief_version
                  AND trace_id IS NOT DISTINCT FROM :trace_id
                  AND feature_cutoff_ts IS NOT DISTINCT FROM :feature_cutoff_ts
                  AND generated_at IS NOT DISTINCT FROM :generated_at
                  AND model_version IS NOT DISTINCT FROM :model_version
                  AND index_version IS NOT DISTINCT FROM :index_version
                  AND dependency_lineage_hash IS NOT DISTINCT FROM :lineage_hash
                  AND status IS NOT DISTINCT FROM :status
                  AND created_at IS NOT DISTINCT FROM :created_at
                """,
                retrieval_parameters,
            )
        dimensions = {
            "dimensions": [
                dimension.model_dump(mode="json") for dimension in candidate.evidence_dimensions
            ],
            "coverage": candidate.coverage.model_dump(mode="json"),
        }
        style_score = next(
            dimension.score
            for dimension in candidate.evidence_dimensions
            if dimension.name.value == "style_resemblance"
        )
        candidate_parameters = {
            "candidate_result_id": uuid5(
                NAMESPACE_URL,
                f"w03-candidate:{result.retrieval_run_id}:{candidate.player_id}",
            ),
            "tenant_id": result.tenant_context.tenant_id,
            "retrieval_run_id": result.retrieval_run_id,
            "player_id": candidate.player_id,
            "rank": candidate.rank,
            "score": style_score,
            "confidence": candidate.confidence.score,
            "evidence_dimensions": json.dumps(dimensions),
            "reason_codes": json.dumps(candidate.reason_codes),
            "claim_boundary": candidate.claim_boundary,
            "created_at": result.generated_at,
        }
        inserted_candidate = connection.execute(
            text(
                """
                INSERT INTO candidate_results (
                    candidate_result_id, tenant_id, retrieval_run_id, player_id,
                    rank, score, confidence, evidence_dimensions, reason_codes,
                    claim_boundary, created_at
                )
                VALUES (
                    :candidate_result_id, :tenant_id, :retrieval_run_id, :player_id,
                    :rank, :score, :confidence, :evidence_dimensions,
                    :reason_codes, :claim_boundary, :created_at
                )
                ON CONFLICT DO NOTHING
                RETURNING candidate_result_id
                """
            ),
            candidate_parameters,
        ).scalar_one_or_none()
        if inserted_candidate is None:
            _require_exact_persisted_row(
                connection,
                """
                SELECT 1
                FROM candidate_results
                WHERE candidate_result_id = :candidate_result_id
                  AND tenant_id IS NOT DISTINCT FROM :tenant_id
                  AND retrieval_run_id IS NOT DISTINCT FROM :retrieval_run_id
                  AND player_id IS NOT DISTINCT FROM :player_id
                  AND rank IS NOT DISTINCT FROM :rank
                  AND score IS NOT DISTINCT FROM :score
                  AND confidence IS NOT DISTINCT FROM :confidence
                  AND evidence_dimensions IS NOT DISTINCT FROM :evidence_dimensions
                  AND reason_codes IS NOT DISTINCT FROM :reason_codes
                  AND claim_boundary IS NOT DISTINCT FROM :claim_boundary
                  AND created_at IS NOT DISTINCT FROM :created_at
                """,
                candidate_parameters,
            )

    @staticmethod
    def _insert_shortlist(
        connection: Connection,
        command: JourneyCommand,
        entry: ShortlistEntry,
    ) -> None:
        brief = command.role_brief
        shortlist_parameters = {
            "shortlist_id": entry.shortlist_id,
            "tenant_id": entry.tenant_context.tenant_id,
            "role_brief_id": brief.role_brief_id,
            "role_brief_version": brief.version,
            "owner_id": entry.owner_id,
            "title": f"{brief.title} synthetic shortlist",
            "version": 1,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }
        inserted_shortlist = connection.execute(
            text(
                """
                INSERT INTO shortlists (
                    shortlist_id, tenant_id, role_brief_id, role_brief_version,
                    owner_id, title, version, created_at, updated_at
                )
                VALUES (
                    :shortlist_id, :tenant_id, :role_brief_id, :role_brief_version,
                    :owner_id, :title, :version, :created_at, :updated_at
                )
                ON CONFLICT (shortlist_id) DO NOTHING
                RETURNING shortlist_id
                """
            ),
            shortlist_parameters,
        ).scalar_one_or_none()
        if inserted_shortlist is None:
            _require_exact_persisted_row(
                connection,
                """
                SELECT 1
                FROM shortlists
                WHERE shortlist_id = :shortlist_id
                  AND tenant_id IS NOT DISTINCT FROM :tenant_id
                  AND role_brief_id IS NOT DISTINCT FROM :role_brief_id
                  AND role_brief_version IS NOT DISTINCT FROM :role_brief_version
                  AND owner_id IS NOT DISTINCT FROM :owner_id
                  AND title IS NOT DISTINCT FROM :title
                  AND version IS NOT DISTINCT FROM :version
                  AND created_at IS NOT DISTINCT FROM :created_at
                  AND updated_at IS NOT DISTINCT FROM :updated_at
                """,
                shortlist_parameters,
            )
        entry_parameters = {
            "shortlist_entry_id": entry.shortlist_entry_id,
            "tenant_id": entry.tenant_context.tenant_id,
            "shortlist_id": entry.shortlist_id,
            "player_id": entry.player_id,
            "retrieval_run_id": entry.retrieval_run_id,
            "rank_at_addition": entry.rank_at_addition,
            "model_version_at_addition": entry.model_version_at_addition,
            "state": entry.state.value,
            "owner_id": entry.owner_id,
            "rationale": entry.rationale,
            "version": entry.version,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }
        inserted_entry = connection.execute(
            text(
                """
                INSERT INTO shortlist_entries (
                    shortlist_entry_id, tenant_id, shortlist_id, player_id,
                    retrieval_run_id, rank_at_addition, model_version_at_addition,
                    state, owner_id, rationale, version, created_at, updated_at
                )
                VALUES (
                    :shortlist_entry_id, :tenant_id, :shortlist_id, :player_id,
                    :retrieval_run_id, :rank_at_addition, :model_version_at_addition,
                    :state, :owner_id, :rationale, :version, :created_at, :updated_at
                )
                ON CONFLICT DO NOTHING
                RETURNING shortlist_entry_id
                """
            ),
            entry_parameters,
        ).scalar_one_or_none()
        if inserted_entry is None:
            _require_exact_persisted_row(
                connection,
                """
                SELECT 1
                FROM shortlist_entries
                WHERE shortlist_entry_id = :shortlist_entry_id
                  AND tenant_id IS NOT DISTINCT FROM :tenant_id
                  AND shortlist_id IS NOT DISTINCT FROM :shortlist_id
                  AND player_id IS NOT DISTINCT FROM :player_id
                  AND retrieval_run_id IS NOT DISTINCT FROM :retrieval_run_id
                  AND rank_at_addition IS NOT DISTINCT FROM :rank_at_addition
                  AND model_version_at_addition
                      IS NOT DISTINCT FROM :model_version_at_addition
                  AND state IS NOT DISTINCT FROM :state
                  AND owner_id IS NOT DISTINCT FROM :owner_id
                  AND rationale IS NOT DISTINCT FROM :rationale
                  AND version IS NOT DISTINCT FROM :version
                  AND created_at IS NOT DISTINCT FROM :created_at
                  AND updated_at IS NOT DISTINCT FROM :updated_at
                """,
                entry_parameters,
            )

    def _append_audit(self, connection: Connection, *, event: AuditEvent) -> None:
        self._audit_writer.append(connection, event)

    @staticmethod
    def _event(
        *,
        request_id: UUID,
        principal: SyntheticPrincipal,
        trace_id: UUID,
        action: AuditAction,
        target_type: str,
        target_id: UUID,
        occurred_at: Any,
        after: Mapping[str, Any],
        reason: str,
    ) -> AuditEvent:
        return AuditEvent(
            audit_event_id=uuid5(
                NAMESPACE_URL,
                f"w03-audit:{request_id}:{target_type}:{target_id}",
            ),
            tenant_context=TenantContext(tenant_id=principal.tenant_id),
            trace_id=trace_id,
            request_id=request_id,
            actor_id=principal.actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            occurred_at=occurred_at,
            after_digest=_digest(after),
            reason=reason,
        )


def _require_exact_persisted_row(
    connection: Connection,
    statement: str,
    parameters: Mapping[str, Any],
) -> None:
    """Deny a silent conflict unless the tenant-visible immutable row is exact."""
    exact_match = connection.execute(text(statement), parameters).scalar_one_or_none()
    if exact_match != 1:
        raise PermissionError("action denied")


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

"""Transactional append-only persistence for strict audit contracts."""

from __future__ import annotations

import json

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from scouting.contracts import AuditEvent


class AuditWriteError(RuntimeError):
    """Audit persistence failed; callers must roll back the material action."""


class AuditWriter:
    """Append an audit event on the caller's existing application transaction."""

    def append(self, connection: Connection, event: AuditEvent) -> None:
        """Insert one immutable event without opening or committing a transaction."""
        try:
            connection.execute(
                text(
                    """
                    INSERT INTO audit_events (
                        audit_event_id, tenant_id, trace_id, request_id, actor_id,
                        action, target_type, target_id, occurred_at, before_digest,
                        after_digest, reason, export_scope
                    )
                    VALUES (
                        :audit_event_id, :tenant_id, :trace_id, :request_id, :actor_id,
                        :action, :target_type, :target_id, :occurred_at, :before_digest,
                        :after_digest, :reason, :export_scope
                    )
                    """
                ),
                {
                    "audit_event_id": event.audit_event_id,
                    "tenant_id": event.tenant_context.tenant_id,
                    "trace_id": event.trace_id,
                    "request_id": event.request_id,
                    "actor_id": event.actor_id,
                    "action": event.action.value,
                    "target_type": event.target_type,
                    "target_id": event.target_id,
                    "occurred_at": event.occurred_at,
                    "before_digest": event.before_digest,
                    "after_digest": event.after_digest,
                    "reason": event.reason,
                    "export_scope": json.dumps(event.export_scope),
                },
            )
        except SQLAlchemyError as exc:
            raise AuditWriteError("audit persistence failed") from exc

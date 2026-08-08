# ruff: noqa: E501
"""Transactional, hash-chained audit receipts for the local R1 runtime."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.exc import SQLAlchemyError

from scouting.contracts import AuditEvent, AuditReceipt


class AuditIntegrityError(RuntimeError):
    """The receipt chain is malformed, incomplete, or has been tampered with."""


def _canonical_event(event: AuditEvent) -> bytes:
    return json.dumps(
        _event_payload(
            audit_event_id=event.audit_event_id,
            tenant_id=event.tenant_context.tenant_id,
            trace_id=event.trace_id,
            request_id=event.request_id,
            actor_id=event.actor_id,
            action=event.action.value,
            target_type=str(event.target_type),
            target_id=event.target_id,
            occurred_at=event.occurred_at,
            before_digest=event.before_digest,
            after_digest=event.after_digest,
            reason=event.reason,
            export_scope=event.export_scope,
        ),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _event_payload(
    *,
    audit_event_id: UUID,
    tenant_id: UUID,
    trace_id: UUID,
    request_id: UUID,
    actor_id: UUID,
    action: str,
    target_type: str,
    target_id: UUID,
    occurred_at: datetime,
    before_digest: str | None,
    after_digest: str | None,
    reason: str | None,
    export_scope: tuple[str, ...],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "audit_event_id": str(audit_event_id),
        "tenant_context": {"tenant_id": str(tenant_id), "club_id": None},
        "trace_id": str(trace_id),
        "request_id": str(request_id),
        "actor_id": str(actor_id),
        "action": action,
        "target_type": target_type,
        "target_id": str(target_id),
        "occurred_at": occurred_at.isoformat(),
        "before_digest": before_digest,
        "after_digest": after_digest,
        "reason": reason,
        "export_scope": export_scope,
    }


def _receipt_digest(
    *,
    tenant_id: UUID,
    receipt_id: UUID,
    previous: str | None,
    event_digest: str,
    sequence: int,
    event_id: UUID,
    recorded_at: datetime,
) -> str:
    """Return the unambiguous digest for every immutable receipt assertion."""
    payload = {
        "tenant_id": str(tenant_id),
        "audit_receipt_id": str(receipt_id),
        "previous_receipt_digest": previous,
        "event_digest": event_digest,
        "sequence": sequence,
        "audit_event_id": str(event_id),
        "recorded_at": recorded_at.isoformat(),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _stored_export_scope(value: object) -> tuple[str, ...]:
    parsed = json.loads(str(value))
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise ValueError("audit export scope is malformed")
    return tuple(parsed)


def _stored_timestamp(value: object) -> datetime:
    encoded = str(value)
    parsed = datetime.fromisoformat(encoded)
    if parsed.tzinfo is None or parsed.isoformat() != encoded:
        raise ValueError("audit timestamp must include an offset")
    return parsed


def _stored_uuid(value: object) -> UUID:
    encoded = str(value)
    parsed = UUID(encoded)
    if str(parsed) != encoded:
        raise ValueError("audit UUID is not canonical")
    return parsed


def _stored_digest(value: object, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    encoded = str(value)
    if len(encoded) != 64 or any(character not in "0123456789abcdef" for character in encoded):
        raise ValueError("audit digest is malformed")
    return encoded


def _stored_sequence(value: object) -> int:
    if type(value) is not int or value < 1:
        raise ValueError("audit sequence is malformed")
    return value


def _stored_optional_text(value: object) -> str | None:
    if value is not None and type(value) is not str:
        raise ValueError("audit optional text is malformed")
    return value


class AuditLedger:
    """Appends a receipt in the caller's transaction; callers commit atomically."""

    def append(self, connection: Connection, event: AuditEvent) -> AuditReceipt:
        try:
            tenant = event.tenant_context.tenant_id
            prior = self._verify_tail(connection, tenant_id=tenant)
            sequence = 1 if prior is None else _stored_sequence(prior["sequence"]) + 1
            previous = None if prior is None else str(prior["receipt_digest"])
            event_digest = hashlib.sha256(_canonical_event(event)).hexdigest()
            receipt_id = uuid4()
            recorded = datetime.now(UTC)
            digest = _receipt_digest(
                tenant_id=tenant,
                receipt_id=receipt_id,
                previous=previous,
                event_digest=event_digest,
                sequence=sequence,
                event_id=event.audit_event_id,
                recorded_at=recorded,
            )
            connection.execute(
                text("""INSERT INTO audit_events (audit_event_id, tenant_id, trace_id, request_id, actor_id, action, target_type, target_id, occurred_at, before_digest, after_digest, reason, export_scope)
                VALUES (:audit_event_id, :tenant_id, :trace_id, :request_id, :actor_id, :action, :target_type, :target_id, :occurred_at, :before_digest, :after_digest, :reason, :export_scope)"""),
                {
                    "audit_event_id": str(event.audit_event_id),
                    "tenant_id": str(tenant),
                    "trace_id": str(event.trace_id),
                    "request_id": str(event.request_id),
                    "actor_id": str(event.actor_id),
                    "action": event.action.value,
                    "target_type": str(event.target_type),
                    "target_id": str(event.target_id),
                    "occurred_at": event.occurred_at.isoformat(),
                    "before_digest": event.before_digest,
                    "after_digest": event.after_digest,
                    "reason": event.reason,
                    "export_scope": json.dumps(event.export_scope),
                },
            )
            connection.execute(
                text("""INSERT INTO audit_receipts (audit_receipt_id, tenant_id, sequence, audit_event_id, previous_receipt_digest, event_digest, receipt_digest, recorded_at)
                VALUES (:receipt_id, :tenant_id, :sequence, :event_id, :previous, :event_digest, :receipt_digest, :recorded_at)"""),
                {
                    "receipt_id": str(receipt_id),
                    "tenant_id": str(tenant),
                    "sequence": sequence,
                    "event_id": str(event.audit_event_id),
                    "previous": previous,
                    "event_digest": event_digest,
                    "receipt_digest": digest,
                    "recorded_at": recorded.isoformat(),
                },
            )
            return AuditReceipt(
                audit_receipt_id=receipt_id,
                tenant_context=event.tenant_context,
                sequence=sequence,
                audit_event_id=event.audit_event_id,
                previous_receipt_digest=previous,
                event_digest=event_digest,
                receipt_digest=digest,
                recorded_at=recorded,
            )
        except (SQLAlchemyError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            raise AuditIntegrityError("audit receipt persistence failed") from exc

    def _verify_tail(self, connection: Connection, *, tenant_id: UUID) -> dict[str, object] | None:
        """Verify the append point without re-hashing the tenant's full history."""

        try:
            orphan_event = connection.execute(
                text(
                    """SELECT 1 FROM audit_events e LEFT JOIN audit_receipts r
                    ON r.audit_event_id = e.audit_event_id AND r.tenant_id = e.tenant_id
                    WHERE e.tenant_id = :tenant_id AND r.audit_event_id IS NULL LIMIT 1"""
                ),
                {"tenant_id": str(tenant_id)},
            ).scalar_one_or_none()
            if orphan_event is not None:
                raise AuditIntegrityError("audit receipt chain rejected")
            newest_rows = (
                connection.execute(
                    text("""SELECT r.audit_receipt_id, r.tenant_id AS receipt_tenant_id, r.sequence,
            r.audit_event_id, r.previous_receipt_digest, r.event_digest, r.receipt_digest, r.recorded_at,
            e.audit_event_id AS event_id, e.tenant_id AS event_tenant_id, e.trace_id, e.request_id, e.actor_id, e.action, e.target_type, e.target_id,
            e.occurred_at, e.before_digest, e.after_digest, e.reason, e.export_scope
            FROM audit_receipts r LEFT JOIN audit_events e
            ON e.audit_event_id = r.audit_event_id AND e.tenant_id = r.tenant_id
            WHERE r.tenant_id = :tenant_id ORDER BY r.sequence DESC LIMIT 2"""),
                    {"tenant_id": str(tenant_id)},
                )
                .mappings()
                .all()
            )
            if not newest_rows:
                return None
            rows = list(reversed(newest_rows))
            first = rows[0]
            first_sequence = _stored_sequence(first["sequence"])
            if len(rows) == 1:
                if first_sequence != 1:
                    raise AuditIntegrityError("audit receipt chain rejected")
                first_previous: str | None = None
            else:
                first_previous = _stored_digest(first["previous_receipt_digest"], nullable=True)
            first_digest = self._verify_row(
                first,
                tenant_id=tenant_id,
                expected_sequence=first_sequence,
                expected_previous=first_previous,
            )
            if len(rows) == 2:
                newest = rows[1]
                self._verify_row(
                    newest,
                    tenant_id=tenant_id,
                    expected_sequence=first_sequence + 1,
                    expected_previous=first_digest,
                )
                return dict(newest)
            return dict(first)
        except AuditIntegrityError:
            raise
        except (SQLAlchemyError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            raise AuditIntegrityError("audit receipt chain rejected") from exc

    @staticmethod
    def _verify_row(
        row: RowMapping | dict[str, Any],
        *,
        tenant_id: UUID,
        expected_sequence: int,
        expected_previous: str | None,
    ) -> str:
        values = dict(row)
        if (
            _stored_sequence(values["sequence"]) != expected_sequence
            or values["event_id"] is None
            or values["receipt_tenant_id"] != str(tenant_id)
            or values["event_tenant_id"] != str(tenant_id)
        ):
            raise AuditIntegrityError("audit receipt chain rejected")
        event_payload = _event_payload(
            audit_event_id=_stored_uuid(values["event_id"]),
            tenant_id=tenant_id,
            trace_id=_stored_uuid(values["trace_id"]),
            request_id=_stored_uuid(values["request_id"]),
            actor_id=_stored_uuid(values["actor_id"]),
            action=str(values["action"]),
            target_type=str(values["target_type"]),
            target_id=_stored_uuid(values["target_id"]),
            occurred_at=_stored_timestamp(values["occurred_at"]),
            before_digest=_stored_digest(values["before_digest"], nullable=True),
            after_digest=_stored_digest(values["after_digest"], nullable=True),
            reason=_stored_optional_text(values["reason"]),
            export_scope=_stored_export_scope(values["export_scope"]),
        )
        event_digest = hashlib.sha256(
            json.dumps(
                event_payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        receipt = _receipt_digest(
            tenant_id=tenant_id,
            receipt_id=_stored_uuid(values["audit_receipt_id"]),
            previous=expected_previous,
            event_digest=event_digest,
            sequence=expected_sequence,
            event_id=_stored_uuid(values["audit_event_id"]),
            recorded_at=_stored_timestamp(values["recorded_at"]),
        )
        if (
            _stored_digest(values["previous_receipt_digest"], nullable=True) != expected_previous
            or _stored_digest(values["event_digest"]) != event_digest
            or _stored_digest(values["receipt_digest"]) != receipt
        ):
            raise AuditIntegrityError("audit receipt chain rejected")
        return receipt

    def verify(self, connection: Connection, *, tenant_id: UUID) -> None:
        try:
            orphan_event = connection.execute(
                text(
                    """SELECT 1 FROM audit_events e LEFT JOIN audit_receipts r
                    ON r.audit_event_id = e.audit_event_id AND r.tenant_id = e.tenant_id
                    WHERE e.tenant_id = :tenant_id AND r.audit_event_id IS NULL LIMIT 1"""
                ),
                {"tenant_id": str(tenant_id)},
            ).scalar_one_or_none()
            if orphan_event is not None:
                raise AuditIntegrityError("audit receipt chain rejected")
            rows = (
                connection.execute(
                    text("""SELECT r.audit_receipt_id, r.tenant_id AS receipt_tenant_id, r.sequence,
            r.audit_event_id, r.previous_receipt_digest, r.event_digest, r.receipt_digest, r.recorded_at,
            e.audit_event_id AS event_id, e.tenant_id AS event_tenant_id, e.trace_id, e.request_id, e.actor_id, e.action, e.target_type, e.target_id,
            e.occurred_at, e.before_digest, e.after_digest, e.reason, e.export_scope
            FROM audit_receipts r LEFT JOIN audit_events e
            ON e.audit_event_id = r.audit_event_id AND e.tenant_id = r.tenant_id
            WHERE r.tenant_id = :tenant_id ORDER BY r.sequence"""),
                    {"tenant_id": str(tenant_id)},
                )
                .mappings()
                .all()
            )
            previous: str | None = None
            for expected_sequence, row in enumerate(rows, start=1):
                if (
                    int(row["sequence"]) != expected_sequence
                    or row["event_id"] is None
                    or row["receipt_tenant_id"] != str(tenant_id)
                    or row["event_tenant_id"] != str(tenant_id)
                ):
                    raise AuditIntegrityError("audit receipt chain rejected")
                previous = self._verify_row(
                    row,
                    tenant_id=tenant_id,
                    expected_sequence=expected_sequence,
                    expected_previous=previous,
                )
        except AuditIntegrityError:
            raise
        except (SQLAlchemyError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            raise AuditIntegrityError("audit receipt chain rejected") from exc

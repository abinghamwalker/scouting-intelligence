"""Append-only material-action audit contract."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import model_validator

from .evidence import Sha256Digest
from .primitives import (
    ActorId,
    AuditEventId,
    AuditReceiptId,
    ContractModel,
    NonEmptyString,
    RequestId,
    SchemaVersion,
    StrictUuid,
    TenantContext,
    TraceId,
    UtcInstant,
)


class AuditAction(StrEnum):
    """Material actions that require durable evidence."""

    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    OVERRIDE = "override"


class AuditEvent(ContractModel):
    """Immutable audit evidence for one material read, write, export, or override."""

    schema_version: SchemaVersion = 1
    audit_event_id: AuditEventId
    tenant_context: TenantContext
    trace_id: TraceId
    request_id: RequestId
    actor_id: ActorId
    action: AuditAction
    target_type: NonEmptyString
    target_id: StrictUuid
    occurred_at: UtcInstant
    before_digest: Sha256Digest | None = None
    after_digest: Sha256Digest | None = None
    reason: NonEmptyString | None = None
    export_scope: tuple[NonEmptyString, ...] = ()

    @model_validator(mode="after")
    def material_action_has_required_context(self) -> Self:
        """Privileged actions remain attributable and export scope is explicit."""
        if self.action is AuditAction.CREATE:
            if self.before_digest is not None or self.after_digest is None:
                raise ValueError("CREATE requires after_digest and forbids before_digest")
        elif self.action in {AuditAction.UPDATE, AuditAction.OVERRIDE}:
            if self.before_digest is None or self.after_digest is None:
                raise ValueError(
                    f"{self.action.value.upper()} requires before_digest and after_digest"
                )
        elif self.action is AuditAction.DELETE:
            if self.before_digest is None or self.after_digest is not None:
                raise ValueError("DELETE requires before_digest and forbids after_digest")

        if self.action is AuditAction.EXPORT and not self.export_scope:
            raise ValueError("export audit events require export_scope")
        if self.action is AuditAction.OVERRIDE and self.reason is None:
            raise ValueError("override audit events require reason")
        if len(self.export_scope) != len(set(self.export_scope)):
            raise ValueError("export_scope entries must be unique")
        return self


class AuditReceipt(ContractModel):
    """Hash-chained receipt for an append-only audit event."""

    schema_version: SchemaVersion = 1
    audit_receipt_id: AuditReceiptId
    tenant_context: TenantContext
    sequence: int
    audit_event_id: AuditEventId
    previous_receipt_digest: Sha256Digest | None = None
    event_digest: Sha256Digest
    receipt_digest: Sha256Digest
    recorded_at: UtcInstant

    @model_validator(mode="after")
    def sequence_and_predecessor_are_coherent(self) -> Self:
        if self.sequence < 1:
            raise ValueError("audit receipt sequence must be positive")
        if (self.sequence == 1) != (self.previous_receipt_digest is None):
            raise ValueError("only the first audit receipt may omit its predecessor")
        return self

"""Strict primitives shared by every cross-boundary scouting contract."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, Strict, StringConstraints


def _require_utc(value: datetime) -> datetime:
    """Reject naive and non-UTC datetimes without normalising the input."""
    offset = value.utcoffset()
    if offset is None or offset != timedelta(0):
        raise ValueError("datetime must be timezone-aware and expressed in UTC")
    return value


type StrictUuid = Annotated[UUID, Strict()]
"""A UUID object in Python mode (JSON UUID strings remain valid wire values)."""

type UtcInstant = Annotated[datetime, Strict(), AfterValidator(_require_utc)]
"""A timezone-aware datetime whose UTC offset is exactly zero."""

type NonEmptyString = Annotated[
    str,
    Strict(),
    StringConstraints(strip_whitespace=True, min_length=1, max_length=512),
]
type PositiveVersion = Annotated[int, Field(strict=True, ge=1)]
type NonNegativeInt = Annotated[int, Field(strict=True, ge=0)]
type PositiveInt = Annotated[int, Field(strict=True, ge=1)]
type UnitInterval = Annotated[float, Field(strict=True, ge=0.0, le=1.0)]
type SchemaVersion = Literal[1]

type TenantId = StrictUuid
type ActorId = StrictUuid
type CanonicalPlayerId = StrictUuid
type CanonicalTeamId = StrictUuid
type RoleBriefId = StrictUuid
type RetrievalRequestId = StrictUuid
type RetrievalResultId = StrictUuid
type RetrievalRunId = StrictUuid
type ShortlistId = StrictUuid
type ShortlistEntryId = StrictUuid
type RetrievalLinkId = StrictUuid
type ShortlistRevisionId = StrictUuid
type CommentId = StrictUuid
type ObservationId = StrictUuid
type SessionId = StrictUuid
type EvidencePackId = StrictUuid
type AuditReceiptId = StrictUuid
type AuditEventId = StrictUuid
type SourceSnapshotId = StrictUuid
type SourceManifestId = StrictUuid
type TraceId = StrictUuid
type RequestId = StrictUuid


class ContractModel(BaseModel):
    """Immutable, strict base for all contracts crossing a module boundary."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )


class TenantContext(ContractModel):
    """Tenant ownership carried explicitly even by the single-tenant runtime."""

    tenant_id: TenantId
    club_id: CanonicalTeamId | None = None


class TraceContext(ContractModel):
    """Identifiers that correlate one boundary operation end to end."""

    trace_id: TraceId
    request_id: RequestId

"""Closed W04 Wyscout identity queue and initial-bundle contracts."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from unicodedata import normalize
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import Field, model_validator

from .evidence import IdentityMatchMethod, Sha256Digest, SourceIdentity
from .primitives import ActorId, ContractModel, StrictUuid, TenantContext, UtcInstant
from .wyscout_data import (
    IDENTITY_ACCEPTANCE_SHA256,
    IDENTITY_CANDIDATE_SHA256,
    SOURCE_MANIFEST_ID,
    SOURCE_MANIFEST_SHA256,
    SOURCE_RELEASE,
    TENANT_ID,
    SourceRecordKind,
    WyscoutSourceRowReference,
    canonical_source_uuid,
    identity_dependency_id,
)

IDENTITY_DECISION_ID: Literal["w04-wyscout-identity-ruleset-decisions-v1"] = (
    "w04-wyscout-identity-ruleset-decisions-v1"
)
IDENTITY_DECISION_SHA256 = "6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192"
IDENTITY_RULESET_ID: Literal["w04-wyscout-identity-ruleset-v1"] = "w04-wyscout-identity-ruleset-v1"
IDENTITY_REVIEW_ID: Literal["w04-wyscout-identity-ruleset-independent-review-R1"] = (
    "w04-wyscout-identity-ruleset-independent-review-R1"
)
IDENTITY_REVIEW_PATH: Literal[
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md"
] = "reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md"
IDENTITY_REVIEW_SHA256 = "62295d6a1da681fbec23285ca6c74124e3ef44fe3962c1472f0523ef46fb2a19"
IDENTITY_ACCEPTANCE_ID: Literal["w04-wyscout-identity-ruleset-acceptance-v1"] = (
    "w04-wyscout-identity-ruleset-acceptance-v1"
)
IDENTITY_DECIDED_AT = datetime(2026, 7, 31, 12, 44, 27, tzinfo=UTC)
IDENTITY_REVIEWED_AT = datetime(2026, 7, 31, 14, 11, 16, tzinfo=UTC)
IDENTITY_ACCEPTED_AT = datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC)
IDENTITY_REVIEW_QUEUE_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w04:wyscout:identity-review-queue:v1",
)
IDENTITY_CROSSWALK_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w04:wyscout:identity-crosswalk:v2",
)

type StrictPositiveInt = Annotated[int, Field(strict=True, ge=1)]
type StrictNonNegativeInt = Annotated[int, Field(strict=True, ge=0)]
type StrictConfidence = Annotated[float, Field(strict=True, ge=0.0, le=1.0)]


def _canonical_json_no_newline(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sorted_unique_source_rows(
    rows: tuple[WyscoutSourceRowReference, ...],
) -> bool:
    keys = tuple(
        (
            row.completion_relative_path,
            row.source_record_ordinal,
            row.raw_record_sha256,
        )
        for row in rows
    )
    return keys == tuple(sorted(set(keys)))


class WyscoutIdentityEntityKind(StrEnum):
    COMPETITION = "COMPETITION"
    TEAM = "TEAM"
    PLAYER = "PLAYER"
    MATCH = "MATCH"


class WyscoutIdentityState(StrEnum):
    RESOLVED = "RESOLVED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"


class WyscoutIdentityClassificationMethod(StrEnum):
    SOURCE_KEY_DETERMINISTIC_RESOLUTION = "SOURCE_KEY_DETERMINISTIC_RESOLUTION"
    SOURCE_KEY_REVIEW_REQUIRED = "SOURCE_KEY_REVIEW_REQUIRED"
    PROVIDER_ZERO_ACTOR_REJECTION = "PROVIDER_ZERO_ACTOR_REJECTION"
    REVIEWED_QUEUE_RESOLUTION = "REVIEWED_QUEUE_RESOLUTION"
    REVIEWED_QUEUE_REJECTION = "REVIEWED_QUEUE_REJECTION"
    REVIEWED_DIRECT_SUPERSESSION_RESOLUTION = "REVIEWED_DIRECT_SUPERSESSION_RESOLUTION"
    REVIEWED_DIRECT_SUPERSESSION_REJECTION = "REVIEWED_DIRECT_SUPERSESSION_REJECTION"


class WyscoutIdentityQueueStatus(StrEnum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED_BY_CORRECTION = "RESOLVED_BY_CORRECTION"
    REJECTED_BY_CORRECTION = "REJECTED_BY_CORRECTION"


def crosswalk_semantic_payload(row: W04IdentityCrosswalkRow) -> dict[str, object]:
    """Return exactly the semantic preimage fields of one crosswalk row."""

    payload = row.model_dump(mode="json")
    for key in ("evidence_digest", "crosswalk_row_id", "trace_id"):
        payload.pop(key)
    return payload


def crosswalk_evidence_digest(row: W04IdentityCrosswalkRow) -> str:
    return hashlib.sha256(_canonical_json_no_newline(crosswalk_semantic_payload(row))).hexdigest()


def crosswalk_row_identity(row: W04IdentityCrosswalkRow) -> UUID:
    return uuid5(IDENTITY_CROSSWALK_NAMESPACE, crosswalk_row_preimage_text(row))


def crosswalk_row_preimage_text(row: W04IdentityCrosswalkRow) -> str:
    """Return the addendum-frozen crosswalk UUIDv5 UTF-8 text preimage."""

    source_payload = row.source_identity.model_dump(mode="json")
    if any(
        type(value) is not str or normalize("NFC", value) != value
        for value in source_payload.values()
    ):
        raise ValueError("source identity UUID preimage must contain strict NFC strings")
    source_json = _canonical_json_no_newline(source_payload).decode("utf-8")
    return (
        f"{str(row.tenant_context.tenant_id).lower()}:{row.entity_kind.value}:{source_json}:"
        f"{row.version}:{row.evidence_digest.lower()}"
    )


class W04IdentityCrosswalkRow(ContractModel):
    """One immutable, versioned W04 source-to-canonical identity assertion."""

    schema_version: Literal[1] = 1
    crosswalk_schema_version: Literal["w04-wyscout-crosswalk-v2"] = "w04-wyscout-crosswalk-v2"
    tenant_context: TenantContext
    entity_kind: WyscoutIdentityEntityKind
    source_identity: SourceIdentity
    source_manifest_id: StrictUuid
    source_manifest_sha256: Sha256Digest
    source_row_refs: Annotated[tuple[WyscoutSourceRowReference, ...], Field(min_length=1)]
    canonical_id: StrictUuid | None
    version: StrictPositiveInt
    classification_method: WyscoutIdentityClassificationMethod
    identity_match_method: IdentityMatchMethod | None
    confidence: StrictConfidence
    state: WyscoutIdentityState
    valid_from: UtcInstant
    valid_to: UtcInstant | None
    available_at: UtcInstant
    reviewed_by: ActorId | None
    supersedes_evidence_digest: Sha256Digest | None
    identity_ruleset_id: Literal["w04-wyscout-identity-ruleset-v1"]
    identity_ruleset_sha256: Sha256Digest
    identity_decision_id: Literal["w04-wyscout-identity-ruleset-decisions-v1"]
    identity_decision_sha256: Sha256Digest
    identity_review_id: Literal["w04-wyscout-identity-ruleset-independent-review-R1"]
    identity_review_sha256: Sha256Digest
    identity_acceptance_id: Literal["w04-wyscout-identity-ruleset-acceptance-v1"]
    identity_acceptance_sha256: Sha256Digest
    reason_codes: Annotated[tuple[str, ...], Field(min_length=1)]
    evidence_digest: Sha256Digest
    crosswalk_row_id: StrictUuid
    trace_id: StrictUuid

    @model_validator(mode="after")
    def row_is_exact(self) -> Self:
        if (
            self.tenant_context != TenantContext(tenant_id=TENANT_ID)
            or self.source_manifest_id != SOURCE_MANIFEST_ID
            or self.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
            or self.identity_ruleset_sha256 != IDENTITY_CANDIDATE_SHA256
            or self.identity_decision_sha256 != IDENTITY_DECISION_SHA256
            or self.identity_review_sha256 != IDENTITY_REVIEW_SHA256
            or self.identity_acceptance_sha256 != IDENTITY_ACCEPTANCE_SHA256
            or self.valid_from != SOURCE_RELEASE
            or self.valid_to is not None
            or self.available_at != IDENTITY_ACCEPTED_AT
            or self.version != 1
            or self.supersedes_evidence_digest is not None
        ):
            raise ValueError("crosswalk row authority differs from the accepted route")
        if self.source_identity.provider != "Wyscout" or self.source_identity.source_version != (
            "figshare-v5"
        ):
            raise ValueError("source identity provider/version differs")
        expected_prefix = self.entity_kind.value.lower() + ":"
        if not self.source_identity.source_id.startswith(expected_prefix):
            raise ValueError("source identity kind prefix differs")
        source_id_text = self.source_identity.source_id.removeprefix(expected_prefix)
        if (
            not source_id_text.isascii()
            or not source_id_text.isdecimal()
            or (len(source_id_text) > 1 and source_id_text.startswith("0"))
        ):
            raise ValueError("source identity must use one canonical decimal integer")
        source_id = int(source_id_text)
        if not _sorted_unique_source_rows(self.source_row_refs):
            raise ValueError("source row references must be sorted and unique")
        if self.reason_codes != tuple(sorted(set(self.reason_codes))):
            raise ValueError("reason codes must be sorted and unique")
        deterministic = (
            self.state is WyscoutIdentityState.RESOLVED
            and self.classification_method
            is WyscoutIdentityClassificationMethod.SOURCE_KEY_DETERMINISTIC_RESOLUTION
            and self.identity_match_method is IdentityMatchMethod.DETERMINISTIC
            and self.canonical_id is not None
            and self.confidence == 1.0
            and self.reviewed_by is None
        )
        review_required = (
            self.state is WyscoutIdentityState.REVIEW_REQUIRED
            and self.classification_method
            is WyscoutIdentityClassificationMethod.SOURCE_KEY_REVIEW_REQUIRED
            and self.identity_match_method is None
            and self.canonical_id is None
            and self.confidence == 0.0
            and self.reviewed_by is None
        )
        zero_rejected = (
            self.state is WyscoutIdentityState.REJECTED
            and self.classification_method
            is WyscoutIdentityClassificationMethod.PROVIDER_ZERO_ACTOR_REJECTION
            and self.entity_kind is WyscoutIdentityEntityKind.PLAYER
            and self.source_identity.source_id == "player:0"
            and self.identity_match_method is None
            and self.canonical_id is None
            and self.confidence == 0.0
            and self.reviewed_by is None
        )
        if not (deterministic or review_required or zero_rejected):
            raise ValueError("initial crosswalk row state/method combination is invalid")
        expected_reason_codes = {
            WyscoutIdentityState.RESOLVED: ("SOURCE_KEY_DETERMINISTIC_RESOLUTION",),
            WyscoutIdentityState.REVIEW_REQUIRED: ("NONZERO_ABSENT_PLAYER_MASTER",),
            WyscoutIdentityState.REJECTED: ("PROVIDER_ZERO_ACTOR_REJECTION",),
        }
        if self.reason_codes != expected_reason_codes[self.state]:
            raise ValueError("initial crosswalk reason code differs")
        if self.state is WyscoutIdentityState.RESOLVED:
            expected_kind = SourceRecordKind(self.entity_kind.value.lower())
            if (
                source_id == 0
                or len(self.source_row_refs) != 1
                or self.source_row_refs[0].record_kind is not expected_kind
                or self.canonical_id != canonical_source_uuid(expected_kind, source_id)
            ):
                raise ValueError("resolved crosswalk source/canonical identity differs")
        elif self.state is WyscoutIdentityState.REVIEW_REQUIRED:
            if source_id == 0 or any(
                reference.record_kind is not SourceRecordKind.MATCH
                for reference in self.source_row_refs
            ):
                raise ValueError("review-required crosswalk source references differ")
        elif source_id != 0 or any(
            reference.record_kind not in {SourceRecordKind.ACTION, SourceRecordKind.MATCH}
            for reference in self.source_row_refs
        ):
            raise ValueError("zero-rejected crosswalk source references differ")
        if self.evidence_digest != crosswalk_evidence_digest(self):
            raise ValueError("crosswalk evidence digest differs from semantic preimage")
        expected_row_id = crosswalk_row_identity(self)
        if self.crosswalk_row_id != expected_row_id:
            raise ValueError("crosswalk row ID differs from UUIDv5 preimage")
        if self.trace_id != uuid5(expected_row_id, "w04-identity-crosswalk-trace-v2"):
            raise ValueError("crosswalk trace ID differs")
        return self


def queue_item_preimage(item: WyscoutIdentityQueueItem) -> dict[str, object]:
    """Return the master-frozen five-field, no-newline queue UUID preimage."""

    return {
        "entity_kind": item.entity_kind.value,
        "reason_family": item.reason_family,
        "source_identity": item.source_identity.model_dump(mode="json"),
        "source_manifest_id": str(item.source_manifest_id),
        "tenant_id": str(item.tenant_context.tenant_id),
    }


def queue_item_preimage_bytes(item: WyscoutIdentityQueueItem) -> bytes:
    return _canonical_json_no_newline(queue_item_preimage(item))


def queue_item_identity(item: WyscoutIdentityQueueItem) -> UUID:
    return uuid5(IDENTITY_REVIEW_QUEUE_NAMESPACE, queue_item_preimage_bytes(item).decode("utf-8"))


class WyscoutIdentityQueueItem(ContractModel):
    queue_item_id: StrictUuid
    tenant_context: TenantContext
    entity_kind: WyscoutIdentityEntityKind
    source_identity: SourceIdentity
    source_manifest_id: StrictUuid
    reason_family: Literal["NONZERO_ABSENT_MASTER"]
    reason_codes: tuple[Literal["NONZERO_ABSENT_PLAYER_MASTER"], ...]
    source_row_refs: Annotated[tuple[WyscoutSourceRowReference, ...], Field(min_length=1)]
    first_seen_source_valid_at: UtcInstant
    available_at: UtcInstant
    status: WyscoutIdentityQueueStatus
    disposition_id: StrictUuid | None

    @model_validator(mode="after")
    def item_is_exact(self) -> Self:
        if (
            self.tenant_context != TenantContext(tenant_id=TENANT_ID)
            or self.entity_kind is not WyscoutIdentityEntityKind.PLAYER
            or self.source_manifest_id != SOURCE_MANIFEST_ID
            or self.source_identity.provider != "Wyscout"
            or self.source_identity.source_version != "figshare-v5"
            or not self.source_identity.source_id.startswith("player:")
            or self.source_identity.source_id == "player:0"
            or self.reason_codes != ("NONZERO_ABSENT_PLAYER_MASTER",)
            or self.first_seen_source_valid_at != SOURCE_RELEASE
            or self.available_at != IDENTITY_ACCEPTED_AT
        ):
            raise ValueError("initial queue item identity/reason differs")
        source_id_text = self.source_identity.source_id.removeprefix("player:")
        if (
            not source_id_text.isascii()
            or not source_id_text.isdecimal()
            or source_id_text == "0"
            or (len(source_id_text) > 1 and source_id_text.startswith("0"))
            or self.status is not WyscoutIdentityQueueStatus.OPEN
            or self.disposition_id is not None
            or any(
                reference.record_kind is not SourceRecordKind.MATCH
                for reference in self.source_row_refs
            )
        ):
            raise ValueError("initial queue item value differs")
        if not _sorted_unique_source_rows(self.source_row_refs):
            raise ValueError("queue source rows must be sorted and unique")
        if self.queue_item_id != queue_item_identity(self):
            raise ValueError("queue item ID differs from the frozen no-newline preimage")
        return self


class WyscoutIdentityReviewQueue(ContractModel):
    schema_version: Literal[1] = 1
    queue_schema_version: Literal["w04-wyscout-identity-review-queue-v1"] = (
        "w04-wyscout-identity-review-queue-v1"
    )
    tenant_context: TenantContext
    source_manifest_id: StrictUuid
    source_manifest_sha256: Sha256Digest
    identity_ruleset_id: Literal["w04-wyscout-identity-ruleset-v1"]
    identity_ruleset_sha256: Sha256Digest
    identity_decision_id: Literal["w04-wyscout-identity-ruleset-decisions-v1"]
    identity_decision_sha256: Sha256Digest
    identity_review_id: Literal["w04-wyscout-identity-ruleset-independent-review-R1"]
    identity_review_sha256: Sha256Digest
    identity_acceptance_id: Literal["w04-wyscout-identity-ruleset-acceptance-v1"]
    identity_acceptance_sha256: Sha256Digest
    prior_queue_sha256: Sha256Digest | None
    items: tuple[WyscoutIdentityQueueItem, ...]
    counts_by_kind_and_status: dict[str, StrictNonNegativeInt]

    @model_validator(mode="after")
    def queue_is_exact(self) -> Self:
        if (
            self.tenant_context != TenantContext(tenant_id=TENANT_ID)
            or self.source_manifest_id != SOURCE_MANIFEST_ID
            or self.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
            or self.identity_ruleset_sha256 != IDENTITY_CANDIDATE_SHA256
            or self.identity_decision_sha256 != IDENTITY_DECISION_SHA256
            or self.identity_review_sha256 != IDENTITY_REVIEW_SHA256
            or self.identity_acceptance_sha256 != IDENTITY_ACCEPTANCE_SHA256
            or self.prior_queue_sha256 is not None
        ):
            raise ValueError("initial queue authority differs")
        keys = tuple(
            (
                tuple(WyscoutIdentityEntityKind).index(item.entity_kind),
                item.source_identity.provider,
                item.source_identity.source_id,
                item.source_identity.source_version,
                item.reason_family,
                item.queue_item_id.bytes,
            )
            for item in self.items
        )
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("queue items must be uniquely and canonically ordered")
        expected = {"PLAYER:OPEN": len(self.items)} if self.items else {}
        if self.counts_by_kind_and_status != expected:
            raise ValueError("queue counts must reconcile exactly to items")
        return self


class WyscoutIdentityEffectiveState(ContractModel):
    evidence_digest: Sha256Digest
    classification_method: WyscoutIdentityClassificationMethod
    effective_state: WyscoutIdentityState


class WyscoutAcceptedIdentityCorrection(ContractModel):
    correction_id: str = Field(strict=True)
    correction_path: str = Field(strict=True)
    correction_sha256: Sha256Digest
    acceptance_sha256: Sha256Digest
    accepted_at: UtcInstant


class WyscoutIdentityBundle(ContractModel):
    """The content-addressed initial identity bundle preimage (ID/digest excluded)."""

    schema_version: Literal[1] = 1
    bundle_schema_version: Literal["w04-wyscout-identity-bundle-v1"] = (
        "w04-wyscout-identity-bundle-v1"
    )
    tenant_context: TenantContext
    source_manifest_id: StrictUuid
    source_manifest_sha256: Sha256Digest
    identity_ruleset_id: Literal["w04-wyscout-identity-ruleset-v1"]
    identity_ruleset_sha256: Sha256Digest
    identity_decision_id: Literal["w04-wyscout-identity-ruleset-decisions-v1"]
    identity_decision_sha256: Sha256Digest
    identity_decided_at: UtcInstant
    identity_review_id: Literal["w04-wyscout-identity-ruleset-independent-review-R1"]
    identity_review_path: Literal[
        "reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md"
    ]
    identity_review_sha256: Sha256Digest
    identity_reviewed_at: UtcInstant
    identity_acceptance_id: Literal["w04-wyscout-identity-ruleset-acceptance-v1"]
    identity_acceptance_sha256: Sha256Digest
    identity_accepted_at: UtcInstant
    current_rows: tuple[W04IdentityCrosswalkRow, ...]
    historical_row_digests: tuple[Sha256Digest, ...]
    effective_state_index: tuple[WyscoutIdentityEffectiveState, ...]
    supersession_edges: tuple[tuple[Sha256Digest, Sha256Digest], ...]
    counts_by_entity_kind_and_effective_state: dict[str, StrictNonNegativeInt]
    review_queue_path: str = Field(strict=True)
    review_queue_sha256: Sha256Digest
    accepted_corrections: tuple[WyscoutAcceptedIdentityCorrection, ...]
    prior_identity_bundle_id: StrictUuid | None
    prior_identity_bundle_sha256: Sha256Digest | None
    observed_at: UtcInstant
    available_at: UtcInstant

    @model_validator(mode="after")
    def bundle_is_exact(self) -> Self:
        if (
            self.tenant_context != TenantContext(tenant_id=TENANT_ID)
            or self.source_manifest_id != SOURCE_MANIFEST_ID
            or self.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
            or self.identity_ruleset_sha256 != IDENTITY_CANDIDATE_SHA256
            or self.identity_decision_sha256 != IDENTITY_DECISION_SHA256
            or self.identity_review_sha256 != IDENTITY_REVIEW_SHA256
            or self.identity_acceptance_sha256 != IDENTITY_ACCEPTANCE_SHA256
            or self.identity_decided_at != IDENTITY_DECIDED_AT
            or self.identity_reviewed_at != IDENTITY_REVIEWED_AT
            or self.identity_accepted_at != IDENTITY_ACCEPTED_AT
            or self.observed_at != IDENTITY_DECIDED_AT
            or self.available_at != IDENTITY_ACCEPTED_AT
            or self.historical_row_digests
            or self.supersession_edges
            or self.accepted_corrections
            or self.prior_identity_bundle_id is not None
            or self.prior_identity_bundle_sha256 is not None
        ):
            raise ValueError("initial bundle authority/history differs")
        row_keys = tuple(
            (
                tuple(WyscoutIdentityEntityKind).index(row.entity_kind),
                row.source_identity.provider,
                row.source_identity.source_id,
                row.source_identity.source_version,
                row.version,
                row.evidence_digest,
            )
            for row in self.current_rows
        )
        if row_keys != tuple(sorted(row_keys)) or len(row_keys) != len(set(row_keys)):
            raise ValueError("bundle current rows must be uniquely and canonically ordered")
        expected_index = tuple(
            sorted(
                (
                    WyscoutIdentityEffectiveState(
                        evidence_digest=row.evidence_digest,
                        classification_method=row.classification_method,
                        effective_state=row.state,
                    )
                    for row in self.current_rows
                ),
                key=lambda item: item.evidence_digest,
            )
        )
        if self.effective_state_index != expected_index:
            raise ValueError("bundle effective-state index must be recomputed from rows")
        counts: dict[str, int] = {}
        for row in self.current_rows:
            key = f"{row.entity_kind.value}:{row.state.value}"
            counts[key] = counts.get(key, 0) + 1
        if self.counts_by_entity_kind_and_effective_state != counts:
            raise ValueError("bundle counts must be recomputed from current rows")
        expected_queue = f"review-queues/{self.review_queue_sha256}.identity-review-queue.json"
        if self.review_queue_path != expected_queue:
            raise ValueError("bundle queue path must be the exact content address")
        return self


def identity_bundle_id(identity_bundle_sha256: str) -> UUID:
    """Expose the one R20 dependency/build UUID derived from accepted bundle bytes."""

    return identity_dependency_id(identity_bundle_sha256)


__all__ = [
    "IDENTITY_ACCEPTANCE_ID",
    "IDENTITY_ACCEPTED_AT",
    "IDENTITY_CROSSWALK_NAMESPACE",
    "IDENTITY_DECISION_ID",
    "IDENTITY_DECISION_SHA256",
    "IDENTITY_DECIDED_AT",
    "IDENTITY_REVIEW_ID",
    "IDENTITY_REVIEW_PATH",
    "IDENTITY_REVIEW_QUEUE_NAMESPACE",
    "IDENTITY_REVIEW_SHA256",
    "IDENTITY_REVIEWED_AT",
    "IDENTITY_RULESET_ID",
    "W04IdentityCrosswalkRow",
    "WyscoutAcceptedIdentityCorrection",
    "WyscoutIdentityBundle",
    "WyscoutIdentityClassificationMethod",
    "WyscoutIdentityEffectiveState",
    "WyscoutIdentityEntityKind",
    "WyscoutIdentityQueueItem",
    "WyscoutIdentityQueueStatus",
    "WyscoutIdentityReviewQueue",
    "WyscoutIdentityState",
    "crosswalk_evidence_digest",
    "crosswalk_row_identity",
    "crosswalk_row_preimage_text",
    "identity_bundle_id",
    "queue_item_identity",
    "queue_item_preimage",
    "queue_item_preimage_bytes",
]

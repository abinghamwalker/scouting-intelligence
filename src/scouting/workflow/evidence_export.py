"""Fail-closed local R1 evidence-pack export.

This module deliberately has no destination abstraction: an evidence pack can only be
written through :class:`~scouting.storage.guarded.GuardedStorage` beneath the
declared local evidence-pack root.  Its JSON is canonical, immutable and explicitly
labelled as synthetic workflow mechanics rather than scout or model evidence.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import yaml  # type: ignore[import-untyped]
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from scouting.audit import AuditIntegrityError, AuditLedger
from scouting.contracts import AuditAction, AuditEvent, AuditReceipt, TenantContext
from scouting.policy import (
    LocalRole,
    R1AuthorizationDenied,
    R1AuthorizationPolicy,
    R1Principal,
    R1Resource,
)
from scouting.storage import GuardedStorage, StorageError, canonical_json_bytes, sha256_hex

_EXPORT_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs/policies/w08-export.yaml"
_CLASSIFICATION = "w08_local_confidential_synthetic_workflow"
_ROOT_NAME = "evidence_packs"
_LIMITATIONS = (
    "NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE.",
    "claim_boundary: resemblance_only.",
    "model_evidence: synthetic_development_only.",
    "applicability: LIMITED.",
    "Workflow action-origin values are persisted labels, not representative-user evidence.",
)


class EvidenceExportDenied(PermissionError):
    """Raised for indistinguishable export, readback, and policy denials."""

    def __init__(self) -> None:
        super().__init__("evidence export denied")


class EvidenceExportIntegrityError(RuntimeError):
    """Raised when a supposedly immutable local evidence pack cannot be verified."""


@dataclass(frozen=True, slots=True)
class EvidenceExportResult:
    """Minimal, non-sensitive receipt returned after a local export succeeds."""

    evidence_pack_id: UUID
    relative_path: str
    sha256: str
    audit_receipt_digest: str


def _expected_export_policy(policy_path: Path) -> None:
    """Reject any policy drift rather than guessing at a changed export policy."""

    raw = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    expected = {
        "schema_version": 1,
        "policy_id": "w08-local-export-v1",
        "status": "planned_r1_local_control",
        "default": "deny",
        "allowed_classification": _CLASSIFICATION,
        "allowed_destination": "guarded_project_local_evidence_pack_root",
        "allowed_roles": ["analyst", "approver"],
        "required_contents": [
            "classification",
            "underlying_values",
            "role_brief_version",
            "retrieval_link",
            "model_version",
            "data_version",
            "limitations",
            "checksums",
            "audit_receipt",
        ],
        "forbidden_contents": [
            "private_observation_not_visible_to_exporter",
            "plaintext_session_token",
            "password_material",
            "raw_provider_payload",
        ],
        "network_transfer_allowed": False,
        "external_sharing_allowed": False,
        "removable_media_transfer_allowed": False,
        "revocation_is_append_only": True,
    }
    if raw != expected:
        raise EvidenceExportDenied()


def _decode_json(value: object, *, field: str) -> object:
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError) as exc:
        raise EvidenceExportIntegrityError(f"invalid persisted {field}") from exc


def _row_dict(row: object, *, json_fields: tuple[str, ...] = ()) -> dict[str, object]:
    mapping = dict(cast(Mapping[str, object], row))
    for field in json_fields:
        mapping[field] = _decode_json(mapping[field], field=field)
    return {key: str(value) if isinstance(value, UUID) else value for key, value in mapping.items()}


@dataclass(frozen=True, slots=True)
class _EvidenceBundle:
    resource: R1Resource
    payload: dict[str, Any]


class LocalEvidenceExporter:
    """Creates and reads only policy-bound, guarded local evidence packs."""

    def __init__(
        self,
        storage: GuardedStorage,
        *,
        audit_ledger: AuditLedger | None = None,
        authorization_policy: R1AuthorizationPolicy | None = None,
        export_policy_path: Path = _EXPORT_POLICY_PATH,
    ) -> None:
        # Instantiating the retained authz policy validates its whole allowlist as well.
        self._policy = authorization_policy or R1AuthorizationPolicy()
        _expected_export_policy(export_policy_path)
        self._export_policy_path = export_policy_path
        self._storage = storage
        self._ledger = audit_ledger or AuditLedger()

    def export(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        evidence_pack_id: UUID,
        role_brief_id: UUID,
        role_brief_version: int,
        retrieval_link_id: UUID,
        shortlist_id: UUID,
        trace_id: UUID,
        request_id: UUID,
    ) -> EvidenceExportResult:
        """Write one canonical pack in the caller's database transaction.

        The caller owns the transaction boundary.  Therefore a storage or audit
        exception rolls back `evidence_exports` and the audit rows when used under
        ``connection.begin()``.  A safely orphaned immutable byte-identical artifact
        is harmless and makes a retry idempotent if an audit write was interrupted.
        """

        _expected_export_policy(self._export_policy_path)
        self._require_valid_ledger(connection, principal.tenant_id)
        if not principal.roles.intersection({LocalRole.ANALYST, LocalRole.APPROVER}):
            raise EvidenceExportDenied()
        bundle = self._bundle(
            connection,
            principal=principal,
            role_brief_id=role_brief_id,
            role_brief_version=role_brief_version,
            retrieval_link_id=retrieval_link_id,
            shortlist_id=shortlist_id,
        )
        self._require_export(principal, bundle.resource)
        relative_path = f"exports/{principal.tenant_id}/{evidence_pack_id}.json"
        payload = canonical_json_bytes(bundle.payload)
        digest = sha256_hex(payload)

        existing = (
            connection.execute(
                text(
                    "SELECT relative_path, sha256 FROM evidence_exports "
                    "WHERE tenant_id = :tenant_id AND evidence_pack_id = :evidence_pack_id"
                ),
                {"tenant_id": principal.tenant_id, "evidence_pack_id": evidence_pack_id},
            )
            .mappings()
            .one_or_none()
        )
        if existing is not None:
            existing_receipt = self._existing_receipt(
                connection, principal.tenant_id, evidence_pack_id
            )
            receipt_row = (
                connection.execute(
                    text(
                        """SELECT audit_event_id, sequence FROM audit_receipts
                    WHERE tenant_id = :tenant AND receipt_digest = :receipt"""
                    ),
                    {"tenant": principal.tenant_id, "receipt": existing_receipt},
                )
                .mappings()
                .one_or_none()
            )
            if receipt_row is None:
                raise EvidenceExportIntegrityError("export receipt is missing")
            persisted_payload = canonical_json_bytes(
                {
                    **bundle.payload,
                    "audit_receipt": {
                        "audit_event_id": str(receipt_row["audit_event_id"]),
                        "receipt_digest": existing_receipt,
                        "sequence": int(receipt_row["sequence"]),
                    },
                }
            )
            digest = sha256_hex(persisted_payload)
            if str(existing["sha256"]) != digest or str(existing["relative_path"]) != relative_path:
                raise EvidenceExportIntegrityError("evidence-pack identity conflicts")
            self._assert_not_revoked(connection, principal.tenant_id, evidence_pack_id)
            self._verify_bytes(relative_path, digest)
            return EvidenceExportResult(evidence_pack_id, relative_path, digest, existing_receipt)

        underlying_digest = str(bundle.payload["checksums"]["underlying_values_sha256"])
        event = AuditEvent(
            audit_event_id=uuid4(),
            tenant_context=TenantContext(tenant_id=principal.tenant_id),
            trace_id=trace_id,
            request_id=request_id,
            actor_id=principal.actor_id,
            action=AuditAction.EXPORT,
            target_type="local.evidence_pack",
            target_id=evidence_pack_id,
            occurred_at=datetime.now(UTC),
            after_digest=underlying_digest,
            reason="local synthetic workflow evidence-pack export",
            export_scope=(str(role_brief_id), str(retrieval_link_id), str(shortlist_id)),
        )
        try:
            # The savepoint is intentional: a web handler may catch this domain
            # exception and continue its outer request transaction.  No audit or
            # export row may survive that caught failure.
            with connection.begin_nested():
                audit_receipt: AuditReceipt = self._ledger.append(connection, event)
                payload = canonical_json_bytes(
                    {
                        **bundle.payload,
                        "audit_receipt": {
                            "audit_event_id": str(audit_receipt.audit_event_id),
                            "receipt_digest": str(audit_receipt.receipt_digest),
                            "sequence": audit_receipt.sequence,
                        },
                    }
                )
                digest = sha256_hex(payload)
                # Persist database intent before immutable bytes.  A database
                # failure therefore cannot create an orphaned content address.
                connection.execute(
                    text(
                        """INSERT INTO evidence_exports
                        (evidence_pack_id, tenant_id, generated_by, classification, relative_path,
                         sha256, limitations, generated_at)
                        VALUES (:id, :tenant, :actor, :classification, :path, :sha256,
                        :limitations, :at)"""
                    ),
                    {
                        "id": evidence_pack_id,
                        "tenant": principal.tenant_id,
                        "actor": principal.actor_id,
                        "classification": _CLASSIFICATION,
                        "path": relative_path,
                        "sha256": digest,
                        "limitations": json.dumps(_LIMITATIONS),
                        "at": datetime.now(UTC).isoformat(),
                    },
                )
                self._storage.write_bytes(
                    _ROOT_NAME,
                    relative_path,
                    payload,
                    media_type="application/json",
                    lineage={
                        "classification": _CLASSIFICATION,
                        "evidence_pack_id": str(evidence_pack_id),
                        "tenant_id": str(principal.tenant_id),
                    },
                    retention={"policy": "retain_local_project_lifetime", "hard_delete": False},
                )
                self._verify_bytes(relative_path, digest)
        except (AuditIntegrityError, SQLAlchemyError, StorageError, OSError) as exc:
            raise EvidenceExportIntegrityError("evidence export failed closed") from exc
        return EvidenceExportResult(
            evidence_pack_id, relative_path, digest, str(audit_receipt.receipt_digest)
        )

    def read(
        self, connection: Connection, *, principal: R1Principal, evidence_pack_id: UUID
    ) -> dict[str, object]:
        """Return verified bytes only to the matching exporter or same-tenant approver."""

        _expected_export_policy(self._export_policy_path)
        self._require_valid_ledger(connection, principal.tenant_id)
        row = (
            connection.execute(
                text(
                    "SELECT generated_by, relative_path, sha256 FROM evidence_exports "
                    "WHERE tenant_id = :tenant_id AND evidence_pack_id = :evidence_pack_id"
                ),
                {"tenant_id": principal.tenant_id, "evidence_pack_id": evidence_pack_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise EvidenceExportDenied()
        self._assert_not_revoked(connection, principal.tenant_id, evidence_pack_id)
        resource = R1Resource(
            principal.tenant_id,
            UUID(str(row["generated_by"])),
            "TEAM" if LocalRole.APPROVER in principal.roles else "OWNER_ONLY",
        )
        if (
            principal.actor_id != resource.owner_actor_id
            and LocalRole.APPROVER not in principal.roles
        ):
            raise EvidenceExportDenied()
        self._require_export(principal, resource)
        payload = self._verified_payload(str(row["relative_path"]), str(row["sha256"]))
        return payload

    def revoke(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        evidence_pack_id: UUID,
        reason: str,
        trace_id: UUID,
        request_id: UUID,
    ) -> None:
        """Append a durable revocation; it never deletes pack bytes or prior receipts."""

        _expected_export_policy(self._export_policy_path)
        self._require_valid_ledger(connection, principal.tenant_id)
        if not reason.strip():
            raise EvidenceExportDenied()
        row = (
            connection.execute(
                text(
                    "SELECT generated_by, relative_path, sha256 FROM evidence_exports "
                    "WHERE tenant_id = :tenant_id AND evidence_pack_id = :evidence_pack_id"
                ),
                {"tenant_id": principal.tenant_id, "evidence_pack_id": evidence_pack_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise EvidenceExportDenied()
        self._require_export(
            principal,
            R1Resource(
                principal.tenant_id,
                UUID(str(row["generated_by"])),
                "TEAM" if LocalRole.APPROVER in principal.roles else "OWNER_ONLY",
            ),
        )
        self.verify_persisted_pack(str(row["relative_path"]), str(row["sha256"]))
        try:
            with connection.begin_nested():
                connection.execute(
                    text(
                        """INSERT INTO evidence_export_revocations
                        (revocation_id, tenant_id, evidence_pack_id, revoked_by, reason, revoked_at)
                        VALUES (:id, :tenant, :pack, :actor, :reason, :at)"""
                    ),
                    {
                        "id": uuid4(),
                        "tenant": principal.tenant_id,
                        "pack": evidence_pack_id,
                        "actor": principal.actor_id,
                        "reason": reason.strip(),
                        "at": datetime.now(UTC).isoformat(),
                    },
                )
                self._ledger.append(
                    connection,
                    AuditEvent(
                        audit_event_id=uuid4(),
                        tenant_context=TenantContext(tenant_id=principal.tenant_id),
                        trace_id=trace_id,
                        request_id=request_id,
                        actor_id=principal.actor_id,
                        action=AuditAction.UPDATE,
                        target_type="local.evidence_pack_revocation",
                        target_id=evidence_pack_id,
                        occurred_at=datetime.now(UTC),
                        before_digest=str(row["sha256"]),
                        after_digest=sha256_hex(reason.strip().encode("utf-8")),
                        reason=reason.strip(),
                    ),
                )
        except (AuditIntegrityError, SQLAlchemyError) as exc:
            raise EvidenceExportIntegrityError("evidence-pack revocation failed closed") from exc

    def _bundle(
        self,
        connection: Connection,
        *,
        principal: R1Principal,
        role_brief_id: UUID,
        role_brief_version: int,
        retrieval_link_id: UUID,
        shortlist_id: UUID,
    ) -> _EvidenceBundle:
        role_brief = (
            connection.execute(
                text(
                    """SELECT r.* FROM role_brief_revisions r JOIN role_brief_workflows w
                ON w.role_brief_id = r.role_brief_id
                WHERE r.tenant_id = :tenant AND r.role_brief_id = :brief AND r.version = :version"""
                ),
                {
                    "tenant": principal.tenant_id,
                    "brief": role_brief_id,
                    "version": role_brief_version,
                },
            )
            .mappings()
            .one_or_none()
        )
        retrieval = (
            connection.execute(
                text(
                    "SELECT * FROM replayable_retrieval_links WHERE tenant_id = :tenant "
                    "AND retrieval_link_id = :id"
                ),
                {"tenant": principal.tenant_id, "id": retrieval_link_id},
            )
            .mappings()
            .one_or_none()
        )
        shortlist = (
            connection.execute(
                text(
                    "SELECT * FROM workflow_shortlists WHERE tenant_id = :tenant "
                    "AND shortlist_id = :id"
                ),
                {"tenant": principal.tenant_id, "id": shortlist_id},
            )
            .mappings()
            .one_or_none()
        )
        if role_brief is None or retrieval is None or shortlist is None:
            raise EvidenceExportDenied()
        if (
            str(retrieval["role_brief_id"]) != str(role_brief_id)
            or int(retrieval["role_brief_version"]) != role_brief_version
            or str(shortlist["role_brief_id"]) != str(role_brief_id)
            or int(shortlist["role_brief_version"]) != role_brief_version
        ):
            raise EvidenceExportDenied()
        entries = (
            connection.execute(
                text(
                    """SELECT r.* FROM shortlist_entry_revisions r JOIN shortlist_entry_workflows w
                ON w.shortlist_entry_id = r.shortlist_entry_id AND w.tenant_id = r.tenant_id
                WHERE r.tenant_id = :tenant AND r.shortlist_id = :shortlist
                ORDER BY r.shortlist_entry_id, r.revision"""
                ),
                {"tenant": principal.tenant_id, "shortlist": shortlist_id},
            )
            .mappings()
            .all()
        )
        latest_assignments = (
            connection.execute(
                text(
                    """SELECT r.shortlist_entry_id, r.assigned_scout_id
                    FROM shortlist_entry_revisions r JOIN shortlist_entry_workflows w
                    ON w.shortlist_entry_id = r.shortlist_entry_id AND w.tenant_id = r.tenant_id
                    JOIN local_accounts a ON a.actor_id = r.assigned_scout_id
                    AND a.tenant_id = r.tenant_id AND a.enabled = 1
                    JOIN local_account_roles roles ON roles.actor_id = a.actor_id
                    AND roles.role = 'scout'
                    WHERE r.tenant_id = :tenant AND r.shortlist_id = :shortlist
                    AND r.revision = w.latest_revision"""
                ),
                {"tenant": principal.tenant_id, "shortlist": shortlist_id},
            )
            .mappings()
            .all()
        )
        current_assigned_entry_ids = {
            str(row["shortlist_entry_id"])
            for row in latest_assignments
            if str(row["assigned_scout_id"] or "") == str(principal.actor_id)
        }
        resource = R1Resource(
            principal.tenant_id,
            UUID(str(shortlist["owner_id"])),
            str(shortlist["visibility"]),
            frozenset(
                UUID(str(row["assigned_scout_id"]))
                for row in latest_assignments
                if row["assigned_scout_id"] is not None
            ),
        )
        observations = (
            connection.execute(
                text(
                    """SELECT o.* FROM scout_observations o
                WHERE o.tenant_id = :tenant AND o.shortlist_entry_id IN (
                    SELECT shortlist_entry_id FROM shortlist_entry_workflows
                    WHERE tenant_id = :tenant AND shortlist_id = :shortlist
                ) ORDER BY o.observation_id, o.version"""
                ),
                {"tenant": principal.tenant_id, "shortlist": shortlist_id},
            )
            .mappings()
            .all()
        )
        visible_observations = [
            _row_dict(row, json_fields=("dimensions", "evidence_references"))
            for row in observations
            if str(row["visibility"]) == "TEAM"
            or str(row["author_id"]) == str(principal.actor_id)
            or str(row["shortlist_entry_id"]) in current_assigned_entry_ids
        ]
        comments = (
            connection.execute(
                text(
                    """SELECT c.* FROM shortlist_comments c
                    WHERE c.tenant_id = :tenant AND c.shortlist_entry_id IN (
                        SELECT shortlist_entry_id FROM shortlist_entry_workflows
                        WHERE tenant_id = :tenant AND shortlist_id = :shortlist
                    ) ORDER BY c.created_at, c.comment_id"""
                ),
                {"tenant": principal.tenant_id, "shortlist": shortlist_id},
            )
            .mappings()
            .all()
        )
        visible_comments = [
            _row_dict(row)
            for row in comments
            if str(row["visibility"]) == "TEAM"
            or str(row["author_id"]) == str(principal.actor_id)
            or str(row["shortlist_entry_id"]) in current_assigned_entry_ids
        ]
        workflow_action_origins = sorted(
            {
                str(row["evidence_origin"])
                for row in [*comments, *observations]
                if (
                    str(row["visibility"]) == "TEAM"
                    or str(row.get("author_id")) == str(principal.actor_id)
                    or str(row["shortlist_entry_id"]) in current_assigned_entry_ids
                )
            }
        )
        underlying = {
            "role_brief_version": _row_dict(
                role_brief,
                json_fields=(
                    "responsibilities",
                    "hard_constraints",
                    "preferences",
                    "exemplar_player_ids",
                ),
            ),
            "retrieval_link": _row_dict(
                retrieval, json_fields=("limitations", "exemplar_player_ids")
            ),
            "shortlist": _row_dict(shortlist),
            "shortlist_entry_revisions": [_row_dict(row) for row in entries],
            "shortlist_comments_visible_to_exporter": visible_comments,
            "scout_observations_visible_to_exporter": visible_observations,
        }
        underlying_bytes = canonical_json_bytes(underlying)
        payload: dict[str, Any] = {
            "schema_version": 1,
            "classification": _CLASSIFICATION,
            "workflow_action_origins": workflow_action_origins,
            "claim_boundary": "resemblance_only",
            "model_evidence": "synthetic_development_only",
            "applicability": "LIMITED",
            "role_brief_version": {
                "role_brief_id": str(role_brief_id),
                "version": role_brief_version,
                "taxonomy_version": str(role_brief["taxonomy_version"]),
            },
            "retrieval_link": {
                "retrieval_link_id": str(retrieval_link_id),
                "model_version": str(retrieval["model_version"]),
                "data_version": str(retrieval["data_version"]),
                "taxonomy_version": str(retrieval["taxonomy_version"]),
            },
            "model_version": str(retrieval["model_version"]),
            "data_version": str(retrieval["data_version"]),
            "limitations": list(_LIMITATIONS),
            "underlying_values": underlying,
            "checksums": {
                "algorithm": "sha256",
                "underlying_values_sha256": hashlib.sha256(underlying_bytes).hexdigest(),
            },
        }
        return _EvidenceBundle(resource=resource, payload=payload)

    def _require_export(self, principal: R1Principal, resource: R1Resource) -> None:
        try:
            self._policy.require(principal, action="evidence_export.create", resource=resource)
        except R1AuthorizationDenied as exc:
            raise EvidenceExportDenied() from exc

    def _require_valid_ledger(self, connection: Connection, tenant_id: UUID) -> None:
        try:
            self._ledger.verify(connection, tenant_id=tenant_id)
        except AuditIntegrityError as exc:
            raise EvidenceExportIntegrityError("audit ledger rejected") from exc

    def _assert_not_revoked(
        self, connection: Connection, tenant_id: UUID, evidence_pack_id: UUID
    ) -> None:
        revoked = connection.execute(
            text(
                "SELECT 1 FROM evidence_export_revocations "
                "WHERE tenant_id = :tenant_id AND evidence_pack_id = :evidence_pack_id"
            ),
            {"tenant_id": tenant_id, "evidence_pack_id": evidence_pack_id},
        ).scalar_one_or_none()
        if revoked is not None:
            raise EvidenceExportDenied()

    def _existing_receipt(
        self, connection: Connection, tenant_id: UUID, evidence_pack_id: UUID
    ) -> str:
        receipt = connection.execute(
            text(
                """SELECT r.receipt_digest FROM audit_receipts r JOIN audit_events e
                ON e.audit_event_id = r.audit_event_id WHERE r.tenant_id = :tenant
                AND e.target_type = 'local.evidence_pack' AND e.target_id = :pack
                ORDER BY r.sequence DESC LIMIT 1"""
            ),
            {"tenant": tenant_id, "pack": evidence_pack_id},
        ).scalar_one_or_none()
        if receipt is None:
            raise EvidenceExportIntegrityError("export receipt is missing")
        return str(receipt)

    def verify_persisted_pack(self, relative_path: str, digest: str) -> dict[str, object]:
        """Verify persisted metadata and bytes before any policy-visible use.

        This is deliberately the single public boundary used by readback, export
        idempotency, inventory, and revocation.  Database metadata is not proof
        that the immutable guarded bytes remain readable, canonical, or within the
        W08 claim boundary.
        """
        try:
            payload = self._storage.read_bytes(_ROOT_NAME, relative_path)
            decoded = json.loads(payload.decode("utf-8", "strict"))
        except (StorageError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceExportIntegrityError("evidence pack is unreadable") from exc
        if sha256_hex(payload) != digest:
            raise EvidenceExportIntegrityError("evidence-pack digest rejected")
        if canonical_json_bytes(decoded) != payload:
            raise EvidenceExportIntegrityError("evidence-pack canonical form rejected")
        if not isinstance(decoded, dict) or decoded.get("classification") != _CLASSIFICATION:
            raise EvidenceExportIntegrityError("evidence-pack classification rejected")
        if (
            decoded.get("claim_boundary") != "resemblance_only"
            or decoded.get("applicability") != "LIMITED"
        ):
            raise EvidenceExportIntegrityError("evidence-pack claim boundary rejected")
        if decoded.get("model_evidence") != "synthetic_development_only":
            raise EvidenceExportIntegrityError("evidence-pack evidence class rejected")
        return decoded

    def _verify_bytes(self, relative_path: str, digest: str) -> None:
        self.verify_persisted_pack(relative_path, digest)

    def _verified_payload(self, relative_path: str, digest: str) -> dict[str, object]:
        return self.verify_persisted_pack(relative_path, digest)

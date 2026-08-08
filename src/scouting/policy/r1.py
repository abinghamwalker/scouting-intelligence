# ruff: noqa: E501
"""Local R1 authentication and object authorisation primitives.

The module intentionally keeps authentication local: credentials and session tokens
are accepted only at the boundary and are never persisted in plaintext.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from uuid import UUID, uuid4

import yaml  # type: ignore[import-untyped]
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError


class LocalRole(StrEnum):
    ANALYST = "analyst"
    SCOUT = "scout"
    APPROVER = "approver"
    ADMIN = "admin"


class R1AuthenticationDenied(PermissionError):
    """A deliberately generic local authentication failure."""

    def __init__(self) -> None:
        super().__init__("session authentication failed")


class R1AuthorizationDenied(PermissionError):
    """A deliberately generic object-authorisation failure."""

    def __init__(self) -> None:
        super().__init__("action denied")


_ROLE_ACTIONS: dict[LocalRole, frozenset[str]] = {
    LocalRole.ANALYST: frozenset(
        {
            "work_queue.read",
            "role_brief.create",
            "role_brief.read",
            "role_brief.update_owned",
            "role_brief.submit_owned",
            "role_brief.version_owned",
            "retrieval_link.create_owned",
            "retrieval_link.read_owned",
            "shortlist.create_owned",
            "shortlist.read",
            "shortlist_entry.add_owned",
            "shortlist_entry.transition_owned",
            "shortlist_entry.reject_with_reason",
            "shortlist_comment.create",
            "observation.read_team_visible",
            "evidence_export.create",
        }
    ),
    LocalRole.SCOUT: frozenset(
        {
            "work_queue.read",
            "role_brief.read_approved",
            "retrieval_link.read_assigned",
            "shortlist.read_assigned",
            "shortlist_comment.create",
            "observation.create_assigned",
            "observation.read_own",
            "observation.read_team_visible",
            "observation.amend_own",
            "observation.flag_disagreement",
            "shortlist_entry.recommend_next_action",
        }
    ),
    LocalRole.APPROVER: frozenset(
        {
            "work_queue.read",
            "role_brief.read",
            "role_brief.approve",
            "role_brief.reject",
            "retrieval_link.read",
            "shortlist.read",
            "shortlist_comment.create",
            "shortlist_entry.transition",
            "shortlist_entry.approve",
            "shortlist_entry.hold",
            "shortlist_entry.reject_with_reason",
            "observation.read_team_visible",
            "evidence_export.create",
        }
    ),
    LocalRole.ADMIN: frozenset(
        {
            "local_account.create",
            "local_account.disable",
            "local_account.assign_role",
            "local_session.revoke",
            "policy.read",
            "audit.read",
            "audit.export_local",
        }
    ),
}
_GLOBAL_DENIES = frozenset(
    {
        "recruitment.autonomous_select",
        "recruitment.autonomous_approve",
        "protected_trait.infer",
        "protected_trait.rank",
        "evidence.external_share",
        "evidence.external_model_send",
        "audit.update",
        "audit.delete",
        "tenant.cross_access",
    }
)
_ADMIN_NOT_GRANTED = frozenset(
    {"role_brief.approve", "shortlist_entry.approve", "evidence_export.create"}
)
_OWNED_ACTIONS = frozenset(
    {
        "role_brief.update_owned",
        "role_brief.submit_owned",
        "role_brief.version_owned",
        "retrieval_link.create_owned",
        "retrieval_link.read_owned",
        "shortlist.create_owned",
        "shortlist_entry.add_owned",
        "shortlist_entry.transition_owned",
    }
)
_VISIBILITY = {
    "allowed": ["OWNER_ONLY", "TEAM"],
    "owner_only_requires_owner_or_assignment": True,
    "team_requires_action_grant": True,
}
_DUMMY_SALT = b"scouting-r1-dummy-salt-for-login"
_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs/policies/w08-authorization.yaml"


@dataclass(frozen=True, slots=True)
class R1Principal:
    actor_id: UUID
    tenant_id: UUID
    roles: frozenset[LocalRole]
    session_id: UUID


@dataclass(frozen=True, slots=True)
class R1Resource:
    tenant_id: UUID
    owner_actor_id: UUID
    visibility: str
    assigned_actor_ids: frozenset[UUID] = frozenset()


class LocalSessionService:
    """Password verification plus expiring, revocable, rotating local sessions."""

    def __init__(self, *, token_key: bytes, now: Callable[[], datetime] | None = None) -> None:
        if len(token_key) < 32:
            raise ValueError("token_key must have at least 32 bytes")
        self._token_key = token_key
        self._now = now or (lambda: datetime.now(UTC))

    def create_account(
        self,
        connection: Connection,
        *,
        actor_id: UUID,
        tenant_id: UUID,
        display_name: str,
        password: str,
        roles: Iterable[LocalRole],
        assigned_by: UUID,
    ) -> None:
        role_values = tuple(dict.fromkeys(LocalRole(role) for role in roles))
        if not password or not display_name.strip() or not role_values:
            raise ValueError("accounts require a display name, password, and at least one role")
        salt = secrets.token_bytes(16)
        digest = self._password_digest(password, salt)
        now = self._timestamp()
        try:
            with connection.begin_nested():
                connection.execute(
                    text("""INSERT INTO local_accounts
                (actor_id, tenant_id, display_name, enabled, created_at, disabled_at)
                VALUES (:actor_id, :tenant_id, :display_name, 1, :created_at, NULL)"""),
                    {
                        "actor_id": actor_id,
                        "tenant_id": tenant_id,
                        "display_name": display_name.strip(),
                        "created_at": now,
                    },
                )
                connection.execute(
                    text("""INSERT INTO local_password_credentials
                (actor_id, salt_hex, password_digest, scrypt_n, scrypt_r, scrypt_p, created_at)
                VALUES (:actor_id, :salt_hex, :password_digest, 16384, 8, 1, :created_at)"""),
                    {
                        "actor_id": actor_id,
                        "salt_hex": salt.hex(),
                        "password_digest": digest.hex(),
                        "created_at": now,
                    },
                )
                for role in role_values:
                    connection.execute(
                        text("""INSERT INTO local_account_roles
                    (actor_id, role, assigned_at, assigned_by)
                    VALUES (:actor_id, :role, :assigned_at, :assigned_by)"""),
                        {
                            "actor_id": actor_id,
                            "role": role.value,
                            "assigned_at": now,
                            "assigned_by": assigned_by,
                        },
                    )
        except SQLAlchemyError as exc:
            raise R1AuthenticationDenied() from exc

    def login(
        self, connection: Connection, *, actor_id: UUID, password: str, ttl: timedelta
    ) -> tuple[str, str]:
        row = (
            connection.execute(
                text("""SELECT a.tenant_id, a.enabled, c.salt_hex, c.password_digest
            FROM local_accounts a JOIN local_password_credentials c ON c.actor_id = a.actor_id
            WHERE a.actor_id = :actor_id"""),
                {"actor_id": actor_id},
            )
            .mappings()
            .one_or_none()
        )
        salt = _DUMMY_SALT if row is None else bytes.fromhex(str(row["salt_hex"]))
        expected = "0" * 64 if row is None else str(row["password_digest"])
        verified = hmac.compare_digest(self._password_digest(password, salt).hex(), expected)
        if row is None or row["enabled"] != 1 or not verified:
            raise R1AuthenticationDenied()
        return self._issue(
            connection, actor_id=actor_id, tenant_id=UUID(str(row["tenant_id"])), ttl=ttl
        )

    def authenticate(
        self,
        connection: Connection,
        *,
        token: str,
        csrf_token: str | None = None,
        require_csrf: bool = False,
    ) -> R1Principal:
        row = (
            connection.execute(
                text("""SELECT s.session_id, s.tenant_id, s.actor_id, s.token_digest,
            s.csrf_digest, s.expires_at, s.revoked_at, a.enabled FROM local_sessions s
            JOIN local_accounts a ON a.actor_id = s.actor_id AND a.tenant_id = s.tenant_id
            WHERE s.token_digest = :token_digest"""),
                {"token_digest": self._digest(token)},
            )
            .mappings()
            .one_or_none()
        )
        if (
            row is None
            or row["enabled"] != 1
            or row["revoked_at"] is not None
            or self._expired(str(row["expires_at"]))
        ):
            raise R1AuthenticationDenied()
        if require_csrf and (
            csrf_token is None
            or not hmac.compare_digest(self._digest(csrf_token), str(row["csrf_digest"]))
        ):
            raise R1AuthenticationDenied()
        roles = (
            connection.execute(
                text("SELECT role FROM local_account_roles WHERE actor_id = :actor_id"),
                {"actor_id": row["actor_id"]},
            )
            .scalars()
            .all()
        )
        try:
            role_set = frozenset(LocalRole(role) for role in roles)
        except ValueError as exc:
            raise R1AuthenticationDenied() from exc
        if not role_set:
            raise R1AuthenticationDenied()
        connection.execute(
            text("UPDATE local_sessions SET last_seen_at = :now WHERE session_id = :session_id"),
            {"now": self._timestamp(), "session_id": row["session_id"]},
        )
        return R1Principal(
            UUID(str(row["actor_id"])),
            UUID(str(row["tenant_id"])),
            role_set,
            UUID(str(row["session_id"])),
        )

    def rotate(self, connection: Connection, *, token: str, ttl: timedelta) -> tuple[str, str]:
        principal = self.authenticate(connection, token=token)
        new_token, csrf_token = self._issue(
            connection, actor_id=principal.actor_id, tenant_id=principal.tenant_id, ttl=ttl
        )
        connection.execute(
            text("""UPDATE local_sessions SET revoked_at = :now, replaced_by_session_id = :replacement
            WHERE session_id = :session_id AND revoked_at IS NULL"""),
            {
                "now": self._timestamp(),
                "replacement": self._session_id_for_token(connection, new_token),
                "session_id": principal.session_id,
            },
        )
        return new_token, csrf_token

    def revoke(self, connection: Connection, *, session_id: UUID) -> None:
        connection.execute(
            text(
                "UPDATE local_sessions SET revoked_at = :now WHERE session_id = :session_id AND revoked_at IS NULL"
            ),
            {"now": self._timestamp(), "session_id": session_id},
        )

    def _issue(
        self, connection: Connection, *, actor_id: UUID, tenant_id: UUID, ttl: timedelta
    ) -> tuple[str, str]:
        if ttl <= timedelta(0):
            raise ValueError("session ttl must be positive")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        session_id, now = uuid4(), self._now()
        connection.execute(
            text("""INSERT INTO local_sessions
            (session_id, tenant_id, actor_id, token_digest, csrf_digest, issued_at, expires_at, last_seen_at, revoked_at, replaced_by_session_id)
            VALUES (:session_id, :tenant_id, :actor_id, :token_digest, :csrf_digest, :issued_at, :expires_at, :last_seen_at, NULL, NULL)"""),
            {
                "session_id": session_id,
                "tenant_id": tenant_id,
                "actor_id": actor_id,
                "token_digest": self._digest(token),
                "csrf_digest": self._digest(csrf),
                "issued_at": now.isoformat(),
                "expires_at": (now + ttl).isoformat(),
                "last_seen_at": now.isoformat(),
            },
        )
        return token, csrf

    def _session_id_for_token(self, connection: Connection, token: str) -> str:
        return str(
            connection.execute(
                text("SELECT session_id FROM local_sessions WHERE token_digest = :digest"),
                {"digest": self._digest(token)},
            ).scalar_one()
        )

    def _digest(self, value: str) -> str:
        return hmac.new(self._token_key, value.encode("utf-8"), hashlib.sha256).hexdigest()

    @staticmethod
    def _password_digest(password: str, salt: bytes) -> bytes:
        return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32)

    def _timestamp(self) -> str:
        return self._now().isoformat()

    def _expired(self, timestamp: str) -> bool:
        return datetime.fromisoformat(timestamp) <= self._now()


class R1AuthorizationPolicy:
    """Deny-by-default role, tenant, owner, assignment, and visibility decisions."""

    def __init__(self, policy_path: Path = _POLICY_PATH) -> None:
        """Reject startup if the retained authorisation policy no longer matches R1."""
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or raw.get("policy_id") != "w08-authorization-v1":
            raise ValueError("unexpected R1 authorization policy")
        if raw.get("schema_version") != 1 or raw.get("status") != "planned_r1_local_control":
            raise ValueError("R1 authorization policy identity must remain retained")
        if (
            raw.get("default") != "deny"
            or frozenset(raw.get("global_denies", ())) != _GLOBAL_DENIES
        ):
            raise ValueError("R1 authorization policy must remain deny by default")
        roles = raw.get("roles")
        if not isinstance(roles, dict) or set(roles) != {role.value for role in LocalRole}:
            raise ValueError("R1 authorization policy roles do not match the retained policy")
        for role, actions in _ROLE_ACTIONS.items():
            body = roles.get(role.value)
            if not isinstance(body, dict) or frozenset(body.get("allow", ())) != actions:
                raise ValueError("R1 authorization policy grants do not match the retained policy")
        if frozenset(raw.get("admin_not_granted", ())) != _ADMIN_NOT_GRANTED:
            raise ValueError("R1 admin denial boundary does not match the retained policy")
        if raw.get("visibility") != _VISIBILITY:
            raise ValueError("R1 visibility boundary does not match the retained policy")

    def authorize(self, principal: R1Principal, *, action: str, resource: R1Resource) -> bool:
        if not action or action in _GLOBAL_DENIES or principal.tenant_id != resource.tenant_id:
            return False
        if resource.visibility not in {"OWNER_ONLY", "TEAM"} or not principal.roles:
            return False
        grants = frozenset().union(
            *(_ROLE_ACTIONS.get(role, frozenset()) for role in principal.roles)
        )
        if action not in grants:
            return False
        owner_or_assigned = (
            principal.actor_id == resource.owner_actor_id
            or principal.actor_id in resource.assigned_actor_ids
        )
        # These are deliberately enumerated rather than inferred from a suffix:
        # every owner-only grant is an explicit retained policy decision.
        if action in _OWNED_ACTIONS and principal.actor_id != resource.owner_actor_id:
            return False
        if resource.visibility == "OWNER_ONLY" and not owner_or_assigned:
            return False
        if "assigned" in action and not owner_or_assigned:
            return False
        return True

    def require(self, principal: R1Principal, *, action: str, resource: R1Resource) -> None:
        if not self.authorize(principal, action=action, resource=resource):
            raise R1AuthorizationDenied()

"""Injected local synthetic sessions with constant-time token verification."""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final
from uuid import UUID

_TOKEN_DOMAIN: Final = b"scouting-w03-local-session-v1"


class AuthenticationDenied(PermissionError):
    """An intentionally non-disclosing session authentication failure."""


@dataclass(frozen=True, slots=True)
class SyntheticAccount:
    """An injected development account; it never contains a credential."""

    actor_id: UUID
    tenant_id: UUID
    roles: tuple[str, ...]
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.roles or any(not role.strip() for role in self.roles):
            raise ValueError("synthetic accounts require non-empty roles")
        if len(self.roles) != len(set(self.roles)):
            raise ValueError("synthetic account roles must be unique")


@dataclass(frozen=True, slots=True)
class SyntheticPrincipal:
    """Authenticated actor context carried to authorization."""

    actor_id: UUID
    tenant_id: UUID
    roles: tuple[str, ...]


def _digest_token(token: str) -> bytes:
    return hmac.new(_TOKEN_DOMAIN, token.encode("utf-8"), hashlib.sha256).digest()


class SessionAuthenticator:
    """Validate injected tokens without retaining plaintext credentials."""

    def __init__(self, token_accounts: Mapping[str, SyntheticAccount]) -> None:
        if not token_accounts:
            raise ValueError("at least one injected synthetic session is required")
        records: list[tuple[bytes, SyntheticAccount]] = []
        for token, account in token_accounts.items():
            if len(token) < 16 or not token.strip():
                raise ValueError("injected synthetic session tokens must be at least 16 characters")
            records.append((_digest_token(token), account))
        self._records = tuple(records)
        self._accounts = MappingProxyType(
            {account.actor_id: account for _, account in self._records}
        )

    @property
    def known_actor_ids(self) -> frozenset[UUID]:
        """Return non-secret actor identifiers for policy validation."""
        return frozenset(self._accounts)

    def authenticate(self, token: str | None) -> SyntheticPrincipal:
        """Return a principal or a generic denial after comparing every digest."""
        candidate = _digest_token(token or "")
        matched: SyntheticAccount | None = None
        for expected, account in self._records:
            if hmac.compare_digest(candidate, expected):
                matched = account
        if matched is None or not matched.enabled:
            raise AuthenticationDenied("session authentication failed")
        return SyntheticPrincipal(
            actor_id=matched.actor_id,
            tenant_id=matched.tenant_id,
            roles=matched.roles,
        )

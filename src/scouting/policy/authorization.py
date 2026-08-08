"""Executable deny-by-default authorization loaded from the frozen W03 policy."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast
from uuid import UUID

import yaml  # type: ignore[import-untyped]

from .authentication import SyntheticPrincipal


class AuthorizationDenied(PermissionError):
    """A non-disclosing authorization failure."""

    def __init__(self, *, reason_code: str) -> None:
        super().__init__("action denied")
        self.reason_code = reason_code


@dataclass(frozen=True, slots=True)
class ResourceContext:
    """Object attributes required by the frozen global policy."""

    resource_type: str
    resource_id: UUID
    tenant_id: UUID
    owner_actor_id: UUID
    visibility: str


@dataclass(frozen=True, slots=True)
class AuthorizationRequest:
    """Complete actor, action, tenant, request, and object context."""

    principal: SyntheticPrincipal
    action: str
    resource: ResourceContext
    request_id: UUID


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """A policy outcome with a machine-safe reason code."""

    allowed: bool
    reason_code: str
    policy_id: str


@dataclass(frozen=True, slots=True)
class _ActionRule:
    requires_owner: bool
    owner_only_visibility_exempt: bool


def _mapping(value: object, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping")
    return cast(Mapping[str, Any], value)


def _strings(value: object, *, context: str) -> frozenset[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{context} must be a string list")
    return frozenset(cast(list[str], value))


def _strict_bool(value: object, *, context: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{context} must be an exact boolean")
    return value


class AuthorizationPolicy:
    """Frozen role/action policy with explicit global and object denials."""

    def __init__(
        self,
        *,
        policy_id: str,
        role_actions: Mapping[str, frozenset[str]],
        action_rules: Mapping[str, _ActionRule],
        global_denies: frozenset[str],
        known_actor_ids: frozenset[UUID],
    ) -> None:
        self.policy_id = policy_id
        self._role_actions = MappingProxyType(dict(role_actions))
        self._action_rules = MappingProxyType(dict(action_rules))
        self._global_denies = global_denies
        self._known_actor_ids = known_actor_ids

    @classmethod
    def from_path(
        cls,
        path: Path,
        *,
        known_actor_ids: Iterable[UUID] = (),
    ) -> AuthorizationPolicy:
        """Load and minimally validate the accepted frozen policy."""
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        root = _mapping(raw, context="authorization policy")
        decision = _mapping(root.get("decision"), context="authorization decision")
        if root.get("policy_id") != "w03-authorization-v1":
            raise ValueError("unexpected authorization policy id")
        deny_fields = (
            "default",
            "unknown_actor",
            "unknown_role",
            "unknown_action",
            "missing_context",
            "cross_tenant",
        )
        if any(decision.get(field) != "deny" for field in deny_fields):
            raise ValueError("authorization policy must remain deny by default")

        raw_roles = _mapping(root.get("roles"), context="authorization roles")
        role_actions: dict[str, frozenset[str]] = {}
        for role, body in raw_roles.items():
            role_body = _mapping(body, context=f"role {role}")
            role_actions[role] = _strings(role_body.get("allow"), context=f"role {role}.allow")
        allowed_actions = frozenset(
            action for actions in role_actions.values() for action in actions
        )
        raw_action_rules = _mapping(
            root.get("action_rules"),
            context="authorization action_rules",
        )
        if frozenset(raw_action_rules) != allowed_actions:
            raise ValueError("authorization action_rules must cover every allowed action exactly")
        action_rules: dict[str, _ActionRule] = {}
        for action, body in raw_action_rules.items():
            action_body = _mapping(body, context=f"action_rules.{action}")
            if frozenset(action_body) != {
                "requires_owner",
                "owner_only_visibility_exempt",
            }:
                raise ValueError(f"action_rules.{action} has unsupported or missing fields")
            action_rules[action] = _ActionRule(
                requires_owner=_strict_bool(
                    action_body["requires_owner"],
                    context=f"action_rules.{action}.requires_owner",
                ),
                owner_only_visibility_exempt=_strict_bool(
                    action_body["owner_only_visibility_exempt"],
                    context=f"action_rules.{action}.owner_only_visibility_exempt",
                ),
            )
        return cls(
            policy_id=cast(str, root["policy_id"]),
            role_actions=role_actions,
            action_rules=action_rules,
            global_denies=_strings(
                root.get("global_denies"),
                context="authorization global_denies",
            ),
            known_actor_ids=frozenset(known_actor_ids),
        )

    @property
    def known_roles(self) -> frozenset[str]:
        """Expose policy role names without making the mapping mutable."""
        return frozenset(self._role_actions)

    def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision:
        """Evaluate every applicable denial before role grants."""
        principal = request.principal
        resource = request.resource
        if (
            not request.action.strip()
            or not resource.resource_type.strip()
            or not resource.visibility.strip()
            or not isinstance(request.request_id, UUID)
            or not isinstance(principal.actor_id, UUID)
            or not isinstance(principal.tenant_id, UUID)
            or not isinstance(resource.resource_id, UUID)
            or not isinstance(resource.tenant_id, UUID)
            or not isinstance(resource.owner_actor_id, UUID)
        ):
            return self._deny("missing_context")
        if principal.actor_id not in self._known_actor_ids:
            return self._deny("unknown_actor")
        if principal.tenant_id != resource.tenant_id:
            return self._deny("cross_tenant")
        if request.action in self._global_denies:
            return self._deny("global_deny")
        if not principal.roles or any(role not in self._role_actions for role in principal.roles):
            return self._deny("unknown_role")

        allowed_actions: set[str] = set()
        for role in principal.roles:
            allowed_actions.update(self._role_actions[role])
        if request.action not in allowed_actions:
            return self._deny("unknown_or_ungranted_action")

        action_rule = self._action_rules[request.action]
        if action_rule.requires_owner and resource.owner_actor_id != principal.actor_id:
            return self._deny("owner_mismatch")
        if resource.visibility not in {"OWNER_ONLY", "TEAM"}:
            return self._deny("unknown_visibility")
        if (
            resource.visibility == "OWNER_ONLY"
            and resource.owner_actor_id != principal.actor_id
            and not action_rule.owner_only_visibility_exempt
        ):
            return self._deny("object_not_visible")
        return AuthorizationDecision(True, "role_grant", self.policy_id)

    def require(self, request: AuthorizationRequest) -> None:
        """Raise a generic denial when the complete policy does not allow."""
        decision = self.authorize(request)
        if not decision.allowed:
            raise AuthorizationDenied(reason_code=decision.reason_code)

    def _deny(self, reason_code: str) -> AuthorizationDecision:
        return AuthorizationDecision(False, reason_code, self.policy_id)

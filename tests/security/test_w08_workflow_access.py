"""Synthetic automated security witnesses for R1 workflow object access."""

from __future__ import annotations

from uuid import uuid4

import pytest

from scouting.policy import (
    LocalRole,
    R1AuthorizationDenied,
    R1AuthorizationPolicy,
    R1Principal,
    R1Resource,
)
from scouting.workflow import R1WorkflowService
from scouting.workflow.r1 import entry_transition_actions


def test_cross_object_and_role_escalation_are_denied() -> None:
    tenant, owner, other, scout, approver = uuid4(), uuid4(), uuid4(), uuid4(), uuid4()
    policy = R1AuthorizationPolicy()
    private = R1Resource(
        tenant_id=tenant,
        owner_actor_id=owner,
        visibility="OWNER_ONLY",
        assigned_actor_ids=frozenset({scout}),
    )
    with pytest.raises(R1AuthorizationDenied):
        policy.require(
            R1Principal(other, tenant, frozenset({LocalRole.ANALYST}), uuid4()),
            action="role_brief.update_owned",
            resource=private,
        )
    with pytest.raises(R1AuthorizationDenied):
        policy.require(
            R1Principal(scout, tenant, frozenset({LocalRole.SCOUT}), uuid4()),
            action="shortlist_entry.approve",
            resource=private,
        )
    with pytest.raises(R1AuthorizationDenied):
        policy.require(
            R1Principal(approver, uuid4(), frozenset({LocalRole.APPROVER}), uuid4()),
            action="role_brief.approve",
            resource=private,
        )


def test_private_visibility_does_not_widen_for_team_role() -> None:
    tenant, owner, unassigned = uuid4(), uuid4(), uuid4()
    resource = R1Resource(tenant_id=tenant, owner_actor_id=owner, visibility="OWNER_ONLY")
    policy = R1AuthorizationPolicy()
    assert not policy.authorize(
        R1Principal(unassigned, tenant, frozenset({LocalRole.APPROVER}), uuid4()),
        action="observation.read_team_visible",
        resource=resource,
    )


def test_ordinary_transition_uses_any_applicable_explicit_grant() -> None:
    tenant, owner, actor = uuid4(), uuid4(), uuid4()
    service = R1WorkflowService()
    actions = entry_transition_actions("monitor")
    assert actions == ("shortlist_entry.transition_owned", "shortlist_entry.transition")

    # The analyst grant is inapplicable to a non-owner, but the independently
    # granted approver transition remains sufficient for the same exact resource.
    service._require_any(
        R1Principal(
            actor,
            tenant,
            frozenset({LocalRole.ANALYST, LocalRole.APPROVER}),
            uuid4(),
        ),
        actions,
        tenant,
        owner,
        "TEAM",
    )
    with pytest.raises(R1AuthorizationDenied):
        service._require_any(
            R1Principal(actor, tenant, frozenset({LocalRole.ANALYST}), uuid4()),
            actions,
            tenant,
            owner,
            "TEAM",
        )


def test_special_transition_targets_keep_their_sole_grant() -> None:
    assert entry_transition_actions("shortlist") == ("shortlist_entry.approve",)
    assert entry_transition_actions("hold") == ("shortlist_entry.hold",)
    assert entry_transition_actions("rejected") == ("shortlist_entry.reject_with_reason",)

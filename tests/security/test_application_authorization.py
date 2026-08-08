"""Application authentication and frozen policy fail closed without disclosure."""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import secrets
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import yaml  # type: ignore[import-untyped]

from scouting.policy import (
    AuthenticationDenied,
    AuthorizationDenied,
    AuthorizationPolicy,
    AuthorizationRequest,
    ResourceContext,
    SessionAuthenticator,
    SyntheticAccount,
    SyntheticPrincipal,
    SyntheticRightsPolicy,
)
from scouting.serving import ServingDenied, SyntheticDomainSnapshot

ROOT = Path(__file__).resolve().parents[2]
TENANT_A = UUID("70000000-0000-4000-8000-000000000101")
TENANT_B = UUID("70000000-0000-4000-8000-000000000102")
ANALYST_ID = UUID("60000000-0000-4000-8000-000000000101")
OTHER_ID = UUID("60000000-0000-4000-8000-000000000102")
RESOURCE_ID = UUID("80000000-0000-4000-8000-000000000101")


@pytest.fixture
def policy() -> AuthorizationPolicy:
    return AuthorizationPolicy.from_path(
        ROOT / "configs/policies/authorization.yaml",
        known_actor_ids=(ANALYST_ID, OTHER_ID),
    )


def test_known_analyst_action_is_allowed(policy: AuthorizationPolicy) -> None:
    decision = policy.authorize(
        _request(
            principal=SyntheticPrincipal(ANALYST_ID, TENANT_A, ("analyst",)),
            action="retrieval.create",
        )
    )
    assert decision.allowed
    assert decision.policy_id == "w03-authorization-v1"


def test_object_action_rules_are_explicit_and_fail_closed(tmp_path: Path) -> None:
    source = ROOT / "configs/policies/authorization.yaml"
    configured = yaml.safe_load(source.read_text(encoding="utf-8"))
    del configured["action_rules"]["retrieval.create"]
    missing = tmp_path / "missing-action-rule.yaml"
    missing.write_text(yaml.safe_dump(configured), encoding="utf-8")
    with pytest.raises(ValueError, match="cover every allowed action exactly"):
        AuthorizationPolicy.from_path(missing, known_actor_ids=(ANALYST_ID,))

    configured = yaml.safe_load(source.read_text(encoding="utf-8"))
    configured["action_rules"]["retrieval.create"]["requires_owner"] = "false"
    non_boolean = tmp_path / "non-boolean-action-rule.yaml"
    non_boolean.write_text(yaml.safe_dump(configured), encoding="utf-8")
    with pytest.raises(ValueError, match="must be an exact boolean"):
        AuthorizationPolicy.from_path(non_boolean, known_actor_ids=(ANALYST_ID,))


@pytest.mark.parametrize(
    ("principal", "action", "resource", "reason"),
    [
        (
            SyntheticPrincipal(
                UUID("60000000-0000-4000-8000-000000000199"),
                TENANT_A,
                ("analyst",),
            ),
            "retrieval.create",
            ResourceContext(
                "retrieval",
                RESOURCE_ID,
                TENANT_A,
                UUID("60000000-0000-4000-8000-000000000199"),
                "OWNER_ONLY",
            ),
            "unknown_actor",
        ),
        (
            SyntheticPrincipal(OTHER_ID, TENANT_A, ("unknown",)),
            "retrieval.create",
            ResourceContext("retrieval", RESOURCE_ID, TENANT_A, OTHER_ID, "OWNER_ONLY"),
            "unknown_role",
        ),
        (
            SyntheticPrincipal(ANALYST_ID, TENANT_A, ("analyst",)),
            "not.registered",
            ResourceContext("retrieval", RESOURCE_ID, TENANT_A, ANALYST_ID, "OWNER_ONLY"),
            "unknown_or_ungranted_action",
        ),
        (
            SyntheticPrincipal(ANALYST_ID, TENANT_A, ("analyst",)),
            "retrieval.create",
            ResourceContext("retrieval", RESOURCE_ID, TENANT_B, ANALYST_ID, "OWNER_ONLY"),
            "cross_tenant",
        ),
        (
            SyntheticPrincipal(ANALYST_ID, TENANT_A, ("analyst",)),
            "confidential_evidence.read_unauthorised",
            ResourceContext(
                "confidential_evidence",
                RESOURCE_ID,
                TENANT_A,
                OTHER_ID,
                "OWNER_ONLY",
            ),
            "unknown_or_ungranted_action",
        ),
        (
            SyntheticPrincipal(ANALYST_ID, TENANT_A, ("analyst",)),
            "retrieval.create",
            ResourceContext("retrieval", RESOURCE_ID, TENANT_A, ANALYST_ID, ""),
            "missing_context",
        ),
    ],
)
def test_unknown_cross_tenant_confidential_and_missing_context_deny_without_content(
    policy: AuthorizationPolicy,
    principal: SyntheticPrincipal,
    action: str,
    resource: ResourceContext,
    reason: str,
) -> None:
    request = AuthorizationRequest(principal, action, resource, uuid4())
    decision = policy.authorize(request)
    assert not decision.allowed
    assert decision.reason_code == reason
    with pytest.raises(AuthorizationDenied) as caught:
        policy.require(request)
    assert str(caught.value) == "action denied"
    assert "confidential" not in str(caught.value)
    assert str(RESOURCE_ID) not in str(caught.value)


def test_export_needs_role_policy_and_frozen_data_rights(
    policy: AuthorizationPolicy,
) -> None:
    request = _request(
        principal=SyntheticPrincipal(ANALYST_ID, TENANT_A, ("analyst",)),
        action="evidence_export.create",
    )
    assert policy.authorize(request).allowed
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    with pytest.raises(PermissionError, match="action denied"):
        rights.require_export_allowed()


def test_session_validation_compares_every_digest_and_returns_generic_denial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_token = secrets.token_urlsafe(32)
    second_token = secrets.token_urlsafe(32)
    authenticator = SessionAuthenticator(
        {
            first_token: SyntheticAccount(ANALYST_ID, TENANT_A, ("analyst",)),
            second_token: SyntheticAccount(OTHER_ID, TENANT_A, ("scout",)),
        }
    )
    comparisons = 0
    original_compare = hmac.compare_digest

    def counting_compare(left: bytes, right: bytes) -> bool:
        nonlocal comparisons
        comparisons += 1
        return original_compare(left, right)

    monkeypatch.setattr(hmac, "compare_digest", counting_compare)
    principal = authenticator.authenticate(first_token)
    assert principal.actor_id == ANALYST_ID
    assert comparisons == 2

    comparisons = 0
    with pytest.raises(AuthenticationDenied) as caught:
        authenticator.authenticate(secrets.token_urlsafe(32))
    assert comparisons == 2
    assert str(caught.value) == "session authentication failed"
    assert first_token not in repr(authenticator)


def test_domain_resolution_rejects_absolute_traversal_and_escaped_symlink_before_read(
    tmp_path: Path,
) -> None:
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    allowed_root = tmp_path / "allowed"
    outside_root = tmp_path / "outside"
    allowed_root.mkdir()
    outside_root.mkdir()
    outside_domain = outside_root / "domain.json"
    outside_domain.write_text("not-json", encoding="utf-8")

    with pytest.raises(ServingDenied, match="relative domain name"):
        SyntheticDomainSnapshot.from_path(
            outside_domain,
            allowed_fixture_root=allowed_root,
            rights_policy=rights,
        )
    with pytest.raises(ServingDenied, match="relative domain name"):
        SyntheticDomainSnapshot.from_path(
            "../outside/domain.json",
            allowed_fixture_root=allowed_root,
            rights_policy=rights,
        )

    (allowed_root / "domain.json").symlink_to(outside_domain)
    with pytest.raises(ServingDenied, match="escapes the allowed fixture root"):
        SyntheticDomainSnapshot.from_path(
            "domain.json",
            allowed_fixture_root=allowed_root,
            rights_policy=rights,
        )


def test_temporary_protected_envelope_requires_explicit_partition_selection(
    tmp_path: Path,
) -> None:
    source_document = json.loads(
        (ROOT / "tests/fixtures/synthetic/domain.json").read_text(encoding="utf-8")
    )
    assert isinstance(source_document, dict)
    document = copy.deepcopy(source_document)
    manifest = document["manifest"]
    payload = document["payload"]
    assert isinstance(manifest, dict)
    assert isinstance(payload, dict)
    manifest["fixture_id"] = "w03-temporary-protected-envelope"
    manifest["partition"] = "protected_test"
    manifest["content_digest"] = hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    fixture_root = tmp_path / "temporary-fixture"
    fixture_root.mkdir()
    (fixture_root / "domain.json").write_text(json.dumps(document), encoding="utf-8")
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")

    with pytest.raises(ServingDenied, match="explicit selection"):
        SyntheticDomainSnapshot.from_path(
            "domain.json",
            allowed_fixture_root=fixture_root,
            rights_policy=rights,
        )
    snapshot = SyntheticDomainSnapshot.from_path(
        "domain.json",
        allowed_fixture_root=fixture_root,
        expected_partition="protected_test",
        rights_policy=rights,
    )
    assert snapshot.partition == "protected_test"
    assert snapshot.fixture_id == "w03-temporary-protected-envelope"


def _request(
    *,
    principal: SyntheticPrincipal,
    action: str,
) -> AuthorizationRequest:
    return AuthorizationRequest(
        principal=principal,
        action=action,
        resource=ResourceContext(
            resource_type="retrieval",
            resource_id=RESOURCE_ID,
            tenant_id=principal.tenant_id,
            owner_actor_id=principal.actor_id,
            visibility="OWNER_ONLY",
        ),
        request_id=uuid4(),
    )

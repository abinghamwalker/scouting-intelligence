# ruff: noqa: E501
"""Synthetic automated tests for local R1 identity, permissions, and audit mechanics."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import yaml  # type: ignore[import-untyped]
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError

from scouting.audit import AuditIntegrityError, AuditLedger
from scouting.contracts import AuditAction, AuditEvent, TenantContext
from scouting.policy import (
    LocalRole,
    LocalSessionService,
    R1AuthenticationDenied,
    R1AuthorizationDenied,
    R1AuthorizationPolicy,
    R1Principal,
    R1Resource,
)
from scouting.storage.embedded import create_embedded_engine


@pytest.fixture
def runtime(tmp_path: Path) -> tuple[Engine, UUID, UUID, UUID, LocalSessionService]:
    engine = create_embedded_engine(tmp_path / "r1.sqlite3", allowed_root=tmp_path)
    tenant_id, analyst_id, scout_id = uuid4(), uuid4(), uuid4()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tenants (tenant_id, slug, display_name, created_at) VALUES (:id, :slug, 'R1', :now)"
            ),
            {"id": tenant_id, "slug": f"r1-{tenant_id.hex}", "now": "2026-08-04T00:00:00+00:00"},
        )
        service = LocalSessionService(token_key=b"r1-test-key-material-must-be-at-least-32-bytes")
        service.create_account(
            connection,
            actor_id=analyst_id,
            tenant_id=tenant_id,
            display_name="Synthetic Analyst",
            password="synthetic-test-password",
            roles=(LocalRole.ANALYST,),
            assigned_by=analyst_id,
        )
        service.create_account(
            connection,
            actor_id=scout_id,
            tenant_id=tenant_id,
            display_name="Synthetic Scout",
            password="synthetic-test-password",
            roles=(LocalRole.SCOUT,),
            assigned_by=analyst_id,
        )
    try:
        yield engine, tenant_id, analyst_id, scout_id, service
    finally:
        engine.dispose()


def test_password_sessions_expire_revoke_rotate_and_require_csrf(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService],
) -> None:
    engine, _, analyst_id, _, service = runtime
    with engine.begin() as connection:
        token, csrf = service.login(
            connection,
            actor_id=analyst_id,
            password="synthetic-test-password",
            ttl=timedelta(minutes=5),
        )
        principal = service.authenticate(
            connection, token=token, csrf_token=csrf, require_csrf=True
        )
        replacement, replacement_csrf = service.rotate(
            connection, token=token, ttl=timedelta(minutes=5)
        )
        with pytest.raises(R1AuthenticationDenied):
            service.authenticate(connection, token=token)
        replacement_principal = service.authenticate(
            connection, token=replacement, csrf_token=replacement_csrf, require_csrf=True
        )
        assert replacement_principal.actor_id == principal.actor_id
        assert replacement_principal.session_id != principal.session_id
        with pytest.raises(R1AuthenticationDenied):
            service.authenticate(
                connection, token=replacement, csrf_token="wrong", require_csrf=True
            )
        service.revoke(
            connection,
            session_id=UUID(
                str(
                    connection.execute(
                        text("SELECT session_id FROM local_sessions WHERE token_digest = :digest"),
                        {"digest": service._digest(replacement)},
                    ).scalar_one()
                )
            ),
        )
        with pytest.raises(R1AuthenticationDenied):
            service.authenticate(connection, token=replacement)


def test_expired_session_and_plaintext_credential_absence(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService],
) -> None:
    engine, _, analyst_id, _, service = runtime
    with engine.begin() as connection:
        token, _ = service.login(
            connection,
            actor_id=analyst_id,
            password="synthetic-test-password",
            ttl=timedelta(seconds=1),
        )
        expired_service = LocalSessionService(
            token_key=b"r1-test-key-material-must-be-at-least-32-bytes",
            now=lambda: datetime(2030, 1, 1, tzinfo=UTC),
        )
        with pytest.raises(R1AuthenticationDenied):
            expired_service.authenticate(connection, token=token)
        values = (
            connection.execute(
                text("SELECT salt_hex, password_digest FROM local_password_credentials")
            )
            .mappings()
            .all()
        )
    assert all("synthetic-test-password" not in repr(row) for row in values)


def test_unknown_account_uses_the_scrypt_work_factor(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, _, _, _, service = runtime
    calls = 0
    original = service._password_digest

    def counted(password: str, salt: bytes) -> bytes:
        nonlocal calls
        calls += 1
        return original(password, salt)

    monkeypatch.setattr(service, "_password_digest", counted)
    with engine.begin() as connection, pytest.raises(R1AuthenticationDenied):
        service.login(
            connection,
            actor_id=uuid4(),
            password="synthetic-test-password",
            ttl=timedelta(minutes=5),
        )
    assert calls == 1


def test_deny_by_default_owner_assignment_visibility_and_admin_boundary(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService],
) -> None:
    engine, tenant_id, analyst_id, scout_id, service = runtime
    policy = R1AuthorizationPolicy()
    with engine.begin() as connection:
        analyst_token, _ = service.login(
            connection,
            actor_id=analyst_id,
            password="synthetic-test-password",
            ttl=timedelta(minutes=5),
        )
        scout_token, _ = service.login(
            connection,
            actor_id=scout_id,
            password="synthetic-test-password",
            ttl=timedelta(minutes=5),
        )
        analyst, scout = (
            service.authenticate(connection, token=analyst_token),
            service.authenticate(connection, token=scout_token),
        )
    owner_only = R1Resource(tenant_id, analyst_id, "OWNER_ONLY")
    owner_only_not_owned = R1Resource(tenant_id, scout_id, "OWNER_ONLY")
    assigned = R1Resource(tenant_id, analyst_id, "OWNER_ONLY", frozenset({scout_id}))
    team = R1Resource(tenant_id, analyst_id, "TEAM", frozenset({scout_id}))
    team_not_owned = R1Resource(tenant_id, scout_id, "TEAM")
    unassigned_team = R1Resource(tenant_id, analyst_id, "TEAM")
    for action in (
        "role_brief.update_owned",
        "role_brief.submit_owned",
        "role_brief.version_owned",
        "retrieval_link.create_owned",
        "retrieval_link.read_owned",
        "shortlist.create_owned",
        "shortlist_entry.add_owned",
        "shortlist_entry.transition_owned",
    ):
        assert policy.authorize(analyst, action=action, resource=owner_only)
        assert policy.authorize(analyst, action=action, resource=team)
        assert not policy.authorize(analyst, action=action, resource=owner_only_not_owned)
        assert not policy.authorize(analyst, action=action, resource=team_not_owned)
    assert not policy.authorize(scout, action="observation.create_assigned", resource=owner_only)
    assert policy.authorize(scout, action="observation.create_assigned", resource=assigned)
    assert policy.authorize(scout, action="shortlist.read_assigned", resource=team)
    assert policy.authorize(analyst, action="shortlist.read", resource=unassigned_team)
    assert policy.authorize(scout, action="observation.read_team_visible", resource=unassigned_team)
    approver = R1Principal(uuid4(), tenant_id, frozenset({LocalRole.APPROVER}), uuid4())
    assert policy.authorize(approver, action="role_brief.read", resource=unassigned_team)
    mixed = R1Principal(
        analyst_id,
        tenant_id,
        frozenset({LocalRole.ANALYST, LocalRole.SCOUT}),
        uuid4(),
    )
    assert policy.authorize(mixed, action="role_brief.read", resource=owner_only)
    assert policy.authorize(mixed, action="retrieval_link.read_owned", resource=owner_only)
    assert not policy.authorize(analyst, action="recruitment.autonomous_approve", resource=team)
    assert not policy.authorize(analyst, action="role_brief.approve", resource=team)
    admin = R1Principal(uuid4(), tenant_id, frozenset({LocalRole.ADMIN}), uuid4())
    assert not policy.authorize(admin, action="role_brief.approve", resource=team)
    assert not policy.authorize(admin, action="evidence_export.create", resource=unassigned_team)
    assert not policy.authorize(analyst, action="unknown.action", resource=team)
    assert not policy.authorize(
        analyst, action="shortlist.read", resource=R1Resource(uuid4(), analyst_id, "TEAM")
    )
    with pytest.raises(R1AuthorizationDenied, match="action denied"):
        policy.require(scout, action="observation.create_assigned", resource=owner_only)


@pytest.mark.parametrize(
    "field", ["schema_version", "status", "default", "admin_not_granted", "visibility"]
)
def test_retained_policy_semantic_drift_fails_closed(tmp_path: Path, field: str) -> None:
    source = Path(__file__).resolve().parents[2] / "configs/policies/w08-authorization.yaml"
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    raw[field] = "drift"
    drifted = tmp_path / "drifted-policy.yaml"
    drifted.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="R1|unexpected"):
        R1AuthorizationPolicy(drifted)


def test_retained_role_grant_and_global_deny_drift_fail_closed(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[2] / "configs/policies/w08-authorization.yaml"
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    roles = raw["roles"]
    assert isinstance(roles, dict)
    analyst = roles["analyst"]
    assert isinstance(analyst, dict)
    analyst["allow"] = []
    drifted_role = tmp_path / "drifted-role-policy.yaml"
    drifted_role.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="grants"):
        R1AuthorizationPolicy(drifted_role)
    raw["global_denies"] = []
    drifted_deny = tmp_path / "drifted-deny-policy.yaml"
    drifted_deny.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="deny"):
        R1AuthorizationPolicy(drifted_deny)


def test_account_creation_savepoint_reverses_caught_role_failure(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService],
) -> None:
    engine, tenant_id, _, _, service = runtime
    rejected_actor = uuid4()
    with engine.begin() as connection:
        with pytest.raises(R1AuthenticationDenied):
            service.create_account(
                connection,
                actor_id=rejected_actor,
                tenant_id=tenant_id,
                display_name="Synthetic Rejected Account",
                password="synthetic-test-password",
                roles=(LocalRole.ANALYST,),
                assigned_by=uuid4(),
            )
        assert (
            connection.execute(
                text("SELECT count(*) FROM local_accounts WHERE actor_id = :actor_id"),
                {"actor_id": rejected_actor},
            ).scalar_one()
            == 0
        )
        assert (
            connection.execute(
                text("SELECT count(*) FROM local_password_credentials WHERE actor_id = :actor_id"),
                {"actor_id": rejected_actor},
            ).scalar_one()
            == 0
        )


def _event(tenant_id: UUID, actor_id: UUID) -> AuditEvent:
    return AuditEvent(
        audit_event_id=uuid4(),
        tenant_context=TenantContext(tenant_id=tenant_id),
        trace_id=uuid4(),
        request_id=uuid4(),
        actor_id=actor_id,
        action=AuditAction.CREATE,
        target_type="synthetic.workflow",
        target_id=uuid4(),
        occurred_at=datetime(2026, 8, 4, tzinfo=UTC),
        after_digest="a" * 64,
    )


def test_transactional_audit_receipts_verify_chain_and_reject_tampering(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService],
) -> None:
    engine, tenant_id, analyst_id, _, _ = runtime
    ledger = AuditLedger()
    with engine.begin() as connection:
        ledger.append(connection, _event(tenant_id, analyst_id))
        ledger.append(connection, _event(tenant_id, analyst_id))
        ledger.verify(connection, tenant_id=tenant_id)
    with pytest.raises(DBAPIError, match="append-only"):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE audit_receipts SET event_digest = :digest WHERE tenant_id = :tenant_id"
                ),
                {"digest": "b" * 64, "tenant_id": tenant_id},
            )
    with engine.begin() as connection:
        fake_event = _event(tenant_id, analyst_id)
        connection.execute(
            text("""INSERT INTO audit_events (
            audit_event_id, tenant_id, trace_id, request_id, actor_id, action,
            target_type, target_id, occurred_at, after_digest, export_scope
        ) VALUES (:id, :tenant, :trace, :request, :actor, 'create', 'synthetic.workflow',
            :target, :occurred, :digest, '[]')"""),
            {
                "id": fake_event.audit_event_id,
                "tenant": tenant_id,
                "trace": fake_event.trace_id,
                "request": fake_event.request_id,
                "actor": analyst_id,
                "target": fake_event.target_id,
                "occurred": fake_event.occurred_at,
                "digest": "a" * 64,
            },
        )
        connection.execute(
            text(
                "INSERT INTO audit_receipts (audit_receipt_id, tenant_id, sequence, audit_event_id, previous_receipt_digest, event_digest, receipt_digest, recorded_at) VALUES (:id, :tenant, 3, :event, :prev, :event_digest, :receipt, :now)"
            ),
            {
                "id": uuid4(),
                "tenant": tenant_id,
                "event": fake_event.audit_event_id,
                "prev": "0" * 64,
                "event_digest": "0" * 64,
                "receipt": "1" * 64,
                "now": "2026-08-04T00:00:00+00:00",
            },
        )
        with pytest.raises(AuditIntegrityError, match="chain rejected"):
            ledger.verify(connection, tenant_id=tenant_id)


@pytest.mark.parametrize("field", ["audit_receipt_id", "recorded_at", "tenant_id"])
def test_receipt_identity_context_and_time_tampering_fail_before_next_action(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService], field: str
) -> None:
    """Each claimed immutable receipt field is bound to the chain digest.

    This deliberately removes the test database's append-only trigger, which models
    the isolated compromise precondition.  Values remain valid-format and the row
    counts stay fixed: rejection is due to digest/context verification, not a schema
    error or a second fault.
    """
    engine, tenant_id, analyst_id, _, _ = runtime
    ledger = AuditLedger()
    other_tenant = uuid4()
    with engine.connect() as connection:
        # The one-tenant runtime deliberately has no valid alternate tenant.  This
        # isolated adversarial fixture disables FK enforcement only for the forged
        # tenant text, after which receipt verification must still fail closed.
        if field == "tenant_id":
            connection.exec_driver_sql("PRAGMA foreign_keys = OFF")
            connection.commit()
        with connection.begin():
            ledger.append(connection, _event(tenant_id, analyst_id))
            ledger.append(connection, _event(tenant_id, analyst_id))
            baseline = {
                table: connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
                for table in ("audit_events", "audit_receipts")
            }
            connection.execute(text("DROP TRIGGER audit_receipts_reject_update"))
            target = (
                connection.execute(
                    text(
                        "SELECT audit_receipt_id, recorded_at FROM audit_receipts "
                        "WHERE tenant_id = :tenant ORDER BY sequence LIMIT 1"
                    ),
                    {"tenant": tenant_id},
                )
                .mappings()
                .one()
            )
            if field == "audit_receipt_id":
                connection.execute(
                    text(
                        "UPDATE audit_receipts SET audit_receipt_id = :value WHERE audit_receipt_id = :id"
                    ),
                    {"value": uuid4(), "id": target["audit_receipt_id"]},
                )
            elif field == "recorded_at":
                replacement = datetime.fromisoformat(str(target["recorded_at"])) + timedelta(
                    seconds=1
                )
                connection.execute(
                    text(
                        "UPDATE audit_receipts SET recorded_at = :value WHERE audit_receipt_id = :id"
                    ),
                    {"value": replacement.isoformat(), "id": target["audit_receipt_id"]},
                )
            else:
                connection.execute(
                    text(
                        "UPDATE audit_receipts SET tenant_id = :value WHERE audit_receipt_id = :id"
                    ),
                    {"value": other_tenant, "id": target["audit_receipt_id"]},
                )

            with pytest.raises(AuditIntegrityError, match="chain rejected"):
                ledger.verify(connection, tenant_id=tenant_id)
            with pytest.raises(AuditIntegrityError, match="chain rejected"):
                ledger.append(connection, _event(tenant_id, analyst_id))
            assert {
                table: connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
                for table in baseline
            } == baseline


def test_append_refuses_existing_orphan_and_preserves_caller_savepoint(
    runtime: tuple[Engine, UUID, UUID, UUID, LocalSessionService],
) -> None:
    engine, tenant_id, analyst_id, _, _ = runtime
    ledger = AuditLedger()
    with engine.begin() as connection:
        ledger.append(connection, _event(tenant_id, analyst_id))
        orphan = _event(tenant_id, analyst_id)
        connection.execute(
            text("""INSERT INTO audit_events (
            audit_event_id, tenant_id, trace_id, request_id, actor_id, action, target_type,
            target_id, occurred_at, after_digest, export_scope
            ) VALUES (:id, :tenant, :trace, :request, :actor, 'create', 'synthetic.orphan',
            :target, :occurred, :digest, '[]')"""),
            {
                "id": orphan.audit_event_id,
                "tenant": tenant_id,
                "trace": orphan.trace_id,
                "request": orphan.request_id,
                "actor": analyst_id,
                "target": orphan.target_id,
                "occurred": orphan.occurred_at,
                "digest": "a" * 64,
            },
        )
        with pytest.raises(AuditIntegrityError, match="chain rejected"):
            ledger.append(connection, _event(tenant_id, analyst_id))
        assert connection.execute(text("SELECT count(*) FROM audit_receipts")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 2

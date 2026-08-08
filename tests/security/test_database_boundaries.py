"""Security checks for the guarded, single-tenant embedded database."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError

from scouting.storage.embedded import (
    EMBEDDED_DATABASE_USER,
    EmbeddedDatabaseConfigurationError,
    create_embedded_engine,
)
from scouting.workflow import ApplicationDatabase


@pytest.fixture
def embedded_runtime(tmp_path: Path) -> tuple[Engine, UUID]:
    engine = create_embedded_engine(
        tmp_path / "security.sqlite3",
        allowed_root=tmp_path,
    )
    tenant_id = uuid4()
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO tenants (tenant_id, slug, display_name, created_at)
                VALUES (:tenant_id, :slug, 'Security Tenant', :created_at)
                """
            ),
            {
                "tenant_id": tenant_id,
                "slug": f"security-{tenant_id.hex}",
                "created_at": "2026-07-29T00:00:00+00:00",
            },
        )
    try:
        yield engine, tenant_id
    finally:
        engine.dispose()


def test_application_boundary_accepts_only_configured_tenant(
    embedded_runtime: tuple[Engine, UUID],
) -> None:
    engine, tenant_id = embedded_runtime
    database = ApplicationDatabase(engine, tenant_id=tenant_id)

    with database.transaction(tenant_id) as (_, identity):
        assert identity.current_user == EMBEDDED_DATABASE_USER
        assert identity.tenant_id == tenant_id

    with pytest.raises(PermissionError, match="action denied"):
        with database.transaction(uuid4()):
            pass


def test_database_file_cannot_escape_its_guarded_root(tmp_path: Path) -> None:
    with pytest.raises(EmbeddedDatabaseConfigurationError, match="guarded root"):
        create_embedded_engine(
            tmp_path.parent / "outside.sqlite3",
            allowed_root=tmp_path,
        )


def test_audit_events_are_append_only_at_database_level(
    embedded_runtime: tuple[Engine, UUID],
) -> None:
    engine, tenant_id = embedded_runtime
    audit_event_id = uuid4()
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO audit_events (
                    audit_event_id, tenant_id, trace_id, request_id, actor_id,
                    action, target_type, target_id, occurred_at, after_digest
                )
                VALUES (
                    :audit_event_id, :tenant_id, :trace_id, :request_id, :actor_id,
                    'create', 'security.boundary', :target_id, :occurred_at, :after_digest
                )
                """
            ),
            {
                "audit_event_id": audit_event_id,
                "tenant_id": tenant_id,
                "trace_id": uuid4(),
                "request_id": uuid4(),
                "actor_id": uuid4(),
                "target_id": uuid4(),
                "occurred_at": "2026-07-29T00:00:00+00:00",
                "after_digest": "a" * 64,
            },
        )

    for statement in (
        "UPDATE audit_events SET reason = 'tamper' WHERE audit_event_id = :event_id",
        "DELETE FROM audit_events WHERE audit_event_id = :event_id",
    ):
        with pytest.raises(DBAPIError, match="append-only"):
            with engine.begin() as connection:
                connection.execute(text(statement), {"event_id": audit_event_id})

    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT count(*) FROM audit_events WHERE audit_event_id = :event_id"),
            {"event_id": audit_event_id},
        ).scalar_one()
    assert count == 1

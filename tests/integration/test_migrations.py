"""Executable checks for the container-free embedded foundation migration."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from scouting.storage.embedded import (
    EmbeddedDatabaseConfigurationError,
    create_embedded_engine,
    resolve_database_path,
    upgrade_database,
)

_EXPECTED_TABLES = {
    "audit_events",
    "audit_receipts",
    "candidate_results",
    "canonical_players",
    "canonical_teams",
    "competitions",
    "evidence_export_revocations",
    "evidence_exports",
    "local_account_roles",
    "local_accounts",
    "local_password_credentials",
    "local_sessions",
    "matches",
    "replayable_retrieval_links",
    "research_experiments",
    "research_replay_receipts",
    "role_brief_revisions",
    "role_brief_workflows",
    "retrieval_runs",
    "role_briefs",
    "schema_migrations",
    "scout_observations",
    "seasons",
    "shortlist_comments",
    "shortlist_entry_revisions",
    "shortlist_entry_workflows",
    "shortlist_entries",
    "shortlists",
    "tenants",
    "workflow_shortlists",
}
ROOT = Path(__file__).resolve().parents[2]


def test_database_path_defaults_inside_project_and_rejects_escape(tmp_path: Path) -> None:
    default_path = resolve_database_path(environ={})
    assert default_path.name == "scouting.sqlite3"
    assert default_path.parent.name == "working"

    with pytest.raises(EmbeddedDatabaseConfigurationError, match="guarded root"):
        resolve_database_path(
            tmp_path.parent / "escaped.sqlite3",
            allowed_root=tmp_path,
        )

    with pytest.raises(EmbeddedDatabaseConfigurationError, match="must use one of"):
        resolve_database_path(tmp_path / "not-a-database.txt", allowed_root=tmp_path)


def test_upgrade_is_idempotent_and_installs_expected_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "migration.sqlite3"
    upgrade_database(database_path, allowed_root=tmp_path)
    upgrade_database(database_path, allowed_root=tmp_path)
    engine = create_embedded_engine(database_path, allowed_root=tmp_path)
    try:
        assert set(inspect(engine).get_table_names()) == _EXPECTED_TABLES
        with engine.connect() as connection:
            assert connection.execute(text("PRAGMA user_version")).scalar_one() == 3
            assert connection.execute(
                text("SELECT version, name FROM schema_migrations")
            ).all() == [
                (1, "0001_foundation"),
                (2, "0002_w08_workflow"),
                (3, "0003_w09_research"),
            ]
            assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    finally:
        engine.dispose()


def test_existing_foundation_database_upgrades_once_without_rewriting_v1(tmp_path: Path) -> None:
    database_path = tmp_path / "existing-v1.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            (ROOT / "migrations/versions/0001_foundation.sql").read_text(encoding="utf-8")
        )
        assert connection.execute("PRAGMA user_version").fetchone() == (1,)
    finally:
        connection.close()

    upgrade_database(database_path, allowed_root=tmp_path)
    upgraded = sqlite3.connect(database_path)
    try:
        assert upgraded.execute("PRAGMA user_version").fetchone() == (3,)
        assert upgraded.execute(
            "SELECT version, name FROM schema_migrations ORDER BY version"
        ).fetchall() == [
            (1, "0001_foundation"),
            (2, "0002_w08_workflow"),
            (3, "0003_w09_research"),
        ]
    finally:
        upgraded.close()


def test_single_tenant_and_optimistic_version_constraints_are_enforced(
    tmp_path: Path,
) -> None:
    engine = create_embedded_engine(
        tmp_path / "constraints.sqlite3",
        allowed_root=tmp_path,
    )
    tenant_id = uuid4()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO tenants (tenant_id, slug, display_name, created_at)
                    VALUES (:tenant_id, :slug, 'Tenant A', :created_at)
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "slug": f"tenant-a-{tenant_id.hex}",
                    "created_at": "2026-07-29T00:00:00+00:00",
                },
            )

        with pytest.raises(IntegrityError, match="single-tenant"):
            with engine.begin() as connection:
                second_tenant = uuid4()
                connection.execute(
                    text(
                        """
                        INSERT INTO tenants (tenant_id, slug, display_name, created_at)
                        VALUES (:tenant_id, :slug, 'Tenant B', :created_at)
                        """
                    ),
                    {
                        "tenant_id": second_tenant,
                        "slug": f"tenant-b-{second_tenant.hex}",
                        "created_at": "2026-07-29T00:00:00+00:00",
                    },
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        """
                        INSERT INTO canonical_players (
                            player_id, tenant_id, display_name, provenance,
                            valid_from, version, created_at
                        )
                        VALUES (
                            :player_id, :tenant_id, 'Invalid Version',
                            '{}', :created_at, 0, :created_at
                        )
                        """
                    ),
                    {
                        "player_id": uuid4(),
                        "tenant_id": tenant_id,
                        "created_at": "2026-07-29T00:00:00+00:00",
                    },
                )
    finally:
        engine.dispose()

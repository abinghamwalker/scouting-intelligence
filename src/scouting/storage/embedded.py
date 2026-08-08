"""Guarded, container-free SQLite persistence for the local application."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import Engine, create_engine, event, text

DATABASE_PATH_ENV = "SCOUTING_DATABASE_PATH"
EMBEDDED_DATABASE_USER = "embedded_app"
SCHEMA_VERSION = 3

_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_DATABASE_PATH = Path("data/working/scouting.sqlite3")
_MIGRATION_PATHS = {
    1: _ROOT / "migrations/versions/0001_foundation.sql",
    2: _ROOT / "migrations/versions/0002_w08_workflow.sql",
    3: _ROOT / "migrations/versions/0003_w09_research.sql",
}
_ALLOWED_SUFFIXES = frozenset({".db", ".sqlite", ".sqlite3"})


class EmbeddedDatabaseConfigurationError(ValueError):
    """The requested embedded database path violates the guarded local boundary."""


class EmbeddedDatabaseMigrationError(RuntimeError):
    """The embedded database cannot be advanced to the supported schema."""


def resolve_database_path(
    value: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    allowed_root: Path | None = None,
) -> Path:
    """Resolve one database file inside the project or an explicit test root."""
    environment = os.environ if environ is None else environ
    configured = value if value is not None else environment.get(DATABASE_PATH_ENV)
    candidate = Path(configured) if configured is not None else _DEFAULT_DATABASE_PATH
    if not candidate.is_absolute():
        candidate = _ROOT / candidate

    guard = (allowed_root or _ROOT).resolve()
    resolved = candidate.resolve()
    if not resolved.is_relative_to(guard):
        raise EmbeddedDatabaseConfigurationError(
            f"{DATABASE_PATH_ENV} must stay inside the guarded root: {guard}"
        )
    if resolved.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise EmbeddedDatabaseConfigurationError(
            f"{DATABASE_PATH_ENV} must use one of {sorted(_ALLOWED_SUFFIXES)}"
        )
    if resolved.exists() and not resolved.is_file():
        raise EmbeddedDatabaseConfigurationError(
            f"{DATABASE_PATH_ENV} must identify a regular database file"
        )
    return resolved


def upgrade_database(
    database_path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    allowed_root: Path | None = None,
) -> Path:
    """Apply the append-only embedded schema migration idempotently."""
    path = resolve_database_path(
        database_path,
        environ=environ,
        allowed_root=allowed_root,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        current_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if current_version > SCHEMA_VERSION:
            raise EmbeddedDatabaseMigrationError(
                f"database schema {current_version} is newer than supported {SCHEMA_VERSION}"
            )
        for version in range(current_version + 1, SCHEMA_VERSION + 1):
            migration = _MIGRATION_PATHS[version].read_text(encoding="utf-8")
            if not migration.strip():
                raise EmbeddedDatabaseMigrationError(f"embedded migration {version} is empty")
            connection.executescript(migration)
        recorded = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        if recorded != [(version,) for version in range(1, SCHEMA_VERSION + 1)]:
            raise EmbeddedDatabaseMigrationError(
                f"expected schema migrations through {SCHEMA_VERSION}; found {recorded!r}"
            )
    except sqlite3.DatabaseError as exc:
        raise EmbeddedDatabaseMigrationError("embedded schema migration failed") from exc
    finally:
        connection.close()
    return path


def create_embedded_engine(
    database_path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    allowed_root: Path | None = None,
    echo: bool = False,
    initialize: bool = True,
) -> Engine:
    """Create a configured SQLite engine with no service or credential dependency."""
    path = resolve_database_path(
        database_path,
        environ=environ,
        allowed_root=allowed_root,
    )
    if initialize:
        upgrade_database(path, allowed_root=allowed_root)

    sqlite3.register_adapter(UUID, str)
    sqlite3.register_adapter(datetime, lambda value: value.isoformat())
    engine = create_engine(
        f"sqlite+pysqlite:///{path}",
        connect_args={"check_same_thread": False},
        echo=echo,
    )

    @event.listens_for(engine, "connect")
    def _configure_connection(
        dbapi_connection: sqlite3.Connection,
        connection_record: object,
    ) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA busy_timeout = 5000")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = FULL")
        finally:
            cursor.close()

    with engine.connect() as connection:
        foreign_keys = connection.execute(text("PRAGMA foreign_keys")).scalar_one()
        if foreign_keys != 1:
            engine.dispose()
            raise EmbeddedDatabaseConfigurationError("SQLite foreign keys must be enabled")
    return engine

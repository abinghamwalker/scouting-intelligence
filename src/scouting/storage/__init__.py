"""Guarded local artifact storage."""

from .embedded import (
    DATABASE_PATH_ENV,
    EMBEDDED_DATABASE_USER,
    EmbeddedDatabaseConfigurationError,
    EmbeddedDatabaseMigrationError,
    create_embedded_engine,
    resolve_database_path,
    upgrade_database,
)
from .formats import (
    FormatError,
    JsonPrimitive,
    JsonValue,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    parquet_bytes,
    read_parquet_bytes,
)
from .guarded import (
    ArtifactConflictError,
    ArtifactReceipt,
    GuardedStorage,
    InvalidArtifactPathError,
    PathEscapeError,
    StorageConfigurationError,
    StorageError,
    UndeclaredRootError,
    sha256_hex,
)

__all__ = [
    "ArtifactConflictError",
    "ArtifactReceipt",
    "DATABASE_PATH_ENV",
    "EMBEDDED_DATABASE_USER",
    "EmbeddedDatabaseConfigurationError",
    "EmbeddedDatabaseMigrationError",
    "FormatError",
    "GuardedStorage",
    "InvalidArtifactPathError",
    "JsonPrimitive",
    "JsonValue",
    "PathEscapeError",
    "StorageConfigurationError",
    "StorageError",
    "UndeclaredRootError",
    "canonical_json_bytes",
    "canonical_jsonl_bytes",
    "create_embedded_engine",
    "parquet_bytes",
    "read_parquet_bytes",
    "resolve_database_path",
    "sha256_hex",
    "upgrade_database",
]

"""Guarded, immutable persistence beneath explicitly declared local roots."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import stat
import sys
import uuid
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from .formats import (
    JsonValue,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    parquet_bytes,
)

_ROOT_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_MAX_PATH_BYTES = 1024
_MAX_PATH_DEPTH = 16
_MAX_SEGMENT_BYTES = 255
_DIRECTORY_MODE = 0o700
_FILE_MODE = 0o600
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_DIRECTORY = getattr(os, "O_DIRECTORY", 0)


class StorageError(RuntimeError):
    """Base class for guarded storage failures."""


class StorageConfigurationError(StorageError):
    """Raised when declared roots are invalid or ambiguous."""


class UndeclaredRootError(StorageError):
    """Raised when a caller requests a root that was not configured."""


class InvalidArtifactPathError(StorageError):
    """Raised for absolute, traversing, malformed, or unbounded artifact paths."""


class PathEscapeError(StorageError):
    """Raised when a symlink or non-directory component could escape a root."""


class ArtifactConflictError(StorageError):
    """Raised when immutable content already exists with different bytes."""


@dataclass(frozen=True, slots=True)
class ArtifactReceipt:
    """Stable result of an immutable artifact and completion-manifest write."""

    root_name: str
    relative_path: str
    manifest_relative_path: str
    sha256: str
    size_bytes: int
    payload_created: bool
    manifest_created: bool


def sha256_hex(payload: bytes) -> str:
    """Return the lower-case SHA-256 digest of bytes."""

    return hashlib.sha256(payload).hexdigest()


def _relative_parts(relative_path: str | os.PathLike[str]) -> tuple[str, ...]:
    raw = os.fspath(relative_path)
    if not isinstance(raw, str):
        raise InvalidArtifactPathError("artifact paths must be text")
    if not raw or "\x00" in raw or "\\" in raw:
        raise InvalidArtifactPathError("artifact path is empty or malformed")
    if len(raw.encode("utf-8")) > _MAX_PATH_BYTES:
        raise InvalidArtifactPathError("artifact path exceeds the bounded length")

    parsed = PurePosixPath(raw)
    raw_parts = raw.split("/")
    if parsed.is_absolute() or any(part in {"", ".", ".."} for part in raw_parts):
        raise InvalidArtifactPathError("artifact path must be a normal relative path")
    if len(raw_parts) > _MAX_PATH_DEPTH:
        raise InvalidArtifactPathError("artifact path exceeds the bounded depth")
    if any(len(part.encode("utf-8")) > _MAX_SEGMENT_BYTES for part in raw_parts):
        raise InvalidArtifactPathError("artifact path contains an overlong segment")
    return tuple(raw_parts)


def _metadata(value: Mapping[str, object], *, name: str) -> dict[str, JsonValue]:
    if not value:
        raise StorageConfigurationError(f"{name} metadata must not be empty")
    normalised_payload = canonical_json_bytes(dict(value))
    # Parsing the canonical representation gives the recursive JSON type expected here.
    parsed = json.loads(normalised_payload)
    if not isinstance(parsed, dict):
        raise StorageConfigurationError(f"{name} metadata must be an object")
    return parsed


class GuardedStorage:
    """Immutable artifact persistence under a closed set of named roots."""

    def __init__(self, roots: Mapping[str, Path]) -> None:
        if not roots:
            raise StorageConfigurationError("at least one storage root is required")

        declared: dict[str, Path] = {}
        canonical_paths: set[Path] = set()
        for root_name, configured_path in roots.items():
            if not _ROOT_NAME.fullmatch(root_name):
                raise StorageConfigurationError(f"invalid root name: {root_name!r}")
            if not configured_path.is_absolute():
                raise StorageConfigurationError(f"root {root_name!r} must be absolute")

            configured_path.mkdir(mode=_DIRECTORY_MODE, parents=True, exist_ok=True)
            if configured_path.is_symlink():
                raise StorageConfigurationError(f"root {root_name!r} cannot be a symlink")
            canonical = configured_path.resolve(strict=True)
            if not canonical.is_dir():
                raise StorageConfigurationError(f"root {root_name!r} is not a directory")
            if canonical in canonical_paths:
                raise StorageConfigurationError("declared roots must be distinct")
            canonical_paths.add(canonical)
            declared[root_name] = canonical
        self._roots = declared

    def write_bytes(
        self,
        root_name: str,
        relative_path: str | os.PathLike[str],
        payload: bytes,
        *,
        media_type: str,
        lineage: Mapping[str, object],
        retention: Mapping[str, object],
    ) -> ArtifactReceipt:
        """Persist payload, then its deterministic completion manifest."""

        if not isinstance(payload, bytes):
            raise TypeError("payload must be bytes")
        if not media_type or media_type.strip() != media_type:
            raise StorageConfigurationError("media_type must be a non-empty trimmed string")

        root = self._root(root_name)
        parts = _relative_parts(relative_path)
        relative = "/".join(parts)
        manifest_relative = f"{relative}.manifest.json"
        lineage_json = _metadata(lineage, name="lineage")
        retention_json = _metadata(retention, name="retention")
        digest = sha256_hex(payload)
        manifest = canonical_json_bytes(
            {
                "lineage": lineage_json,
                "media_type": media_type,
                "payload": {
                    "path": relative,
                    "sha256": digest,
                    "size_bytes": len(payload),
                },
                "retention": retention_json,
                "schema_version": 1,
                "state": "complete",
            }
        )

        # Preflight both immutable destinations. In particular, a conflicting manifest
        # must not cause a previously absent payload to be created.
        self._assert_compatible_or_absent(root, parts, payload)
        manifest_parts = _relative_parts(manifest_relative)
        self._assert_compatible_or_absent(root, manifest_parts, manifest)

        payload_created = self._persist_immutable(root, parts, payload)
        manifest_created = self._persist_immutable(root, manifest_parts, manifest)
        return ArtifactReceipt(
            root_name=root_name,
            relative_path=relative,
            manifest_relative_path=manifest_relative,
            sha256=digest,
            size_bytes=len(payload),
            payload_created=payload_created,
            manifest_created=manifest_created,
        )

    def write_json(
        self,
        root_name: str,
        relative_path: str | os.PathLike[str],
        value: object,
        *,
        lineage: Mapping[str, object],
        retention: Mapping[str, object],
    ) -> ArtifactReceipt:
        return self.write_bytes(
            root_name,
            relative_path,
            canonical_json_bytes(value),
            media_type="application/json",
            lineage=lineage,
            retention=retention,
        )

    def write_jsonl(
        self,
        root_name: str,
        relative_path: str | os.PathLike[str],
        rows: list[object],
        *,
        lineage: Mapping[str, object],
        retention: Mapping[str, object],
    ) -> ArtifactReceipt:
        return self.write_bytes(
            root_name,
            relative_path,
            canonical_jsonl_bytes(rows),
            media_type="application/x-ndjson",
            lineage=lineage,
            retention=retention,
        )

    def write_parquet(
        self,
        root_name: str,
        relative_path: str | os.PathLike[str],
        rows: list[Mapping[str, object]],
        *,
        lineage: Mapping[str, object],
        retention: Mapping[str, object],
    ) -> ArtifactReceipt:
        return self.write_bytes(
            root_name,
            relative_path,
            parquet_bytes(rows),
            media_type="application/vnd.apache.parquet",
            lineage=lineage,
            retention=retention,
        )

    def read_bytes(self, root_name: str, relative_path: str | os.PathLike[str]) -> bytes:
        """Read a regular immutable artifact without following symlinks."""

        root = self._root(root_name)
        parts = _relative_parts(relative_path)
        with self._parent_descriptor(root, parts[:-1], create=False) as parent_fd:
            existing = self._read_regular(parent_fd, parts[-1])
        if existing is None:
            raise FileNotFoundError("/".join(parts))
        return existing

    @contextmanager
    def open_binary(
        self, root_name: str, relative_path: str | os.PathLike[str]
    ) -> Iterator[BinaryIO]:
        """Open a guarded regular artifact for bounded-memory sequential reads."""

        root = self._root(root_name)
        parts = _relative_parts(relative_path)
        with self._parent_descriptor(root, parts[:-1], create=False) as parent_fd:
            try:
                file_descriptor = os.open(parts[-1], os.O_RDONLY | _NOFOLLOW, dir_fd=parent_fd)
            except OSError as error:
                if error.errno in {errno.ELOOP, errno.ENOTDIR}:
                    raise PathEscapeError(
                        f"artifact target is not a regular file: {parts[-1]}"
                    ) from error
                raise
            try:
                metadata = os.fstat(file_descriptor)
                if not stat.S_ISREG(metadata.st_mode):
                    raise PathEscapeError(f"artifact target is not a regular file: {parts[-1]}")
                if stat.S_IMODE(metadata.st_mode) & 0o077:
                    raise PathEscapeError(
                        "artifact target has unsafe permissions: "
                        f"{parts[-1]}; run chmod 600 on the file"
                    )
                with os.fdopen(file_descriptor, "rb", closefd=True) as stream:
                    file_descriptor = -1
                    yield stream
            finally:
                if file_descriptor >= 0:
                    os.close(file_descriptor)

    def _root(self, root_name: str) -> Path:
        try:
            return self._roots[root_name]
        except KeyError as error:
            raise UndeclaredRootError(f"undeclared storage root: {root_name!r}") from error

    def _assert_compatible_or_absent(
        self, root: Path, parts: tuple[str, ...], payload: bytes
    ) -> None:
        with self._parent_descriptor(root, parts[:-1], create=True) as parent_fd:
            existing = self._read_regular(parent_fd, parts[-1])
        if existing is not None and existing != payload:
            raise ArtifactConflictError(f"immutable artifact conflicts at {'/'.join(parts)}")

    def _persist_immutable(self, root: Path, parts: tuple[str, ...], payload: bytes) -> bool:
        with self._parent_descriptor(root, parts[:-1], create=True) as parent_fd:
            existing = self._read_regular(parent_fd, parts[-1])
            if existing is not None:
                if existing == payload:
                    return False
                raise ArtifactConflictError(f"immutable artifact conflicts at {'/'.join(parts)}")

            target_name = parts[-1]
            temporary_name = f".{target_name}.{uuid.uuid4().hex}.tmp"
            temporary_fd: int | None = None
            temporary_exists = False
            try:
                temporary_fd = os.open(
                    temporary_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW,
                    _FILE_MODE,
                    dir_fd=parent_fd,
                )
                temporary_exists = True
                self._write_all(temporary_fd, payload)
                os.fsync(temporary_fd)
                os.close(temporary_fd)
                temporary_fd = None
                try:
                    os.link(
                        temporary_name,
                        target_name,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                        follow_symlinks=False,
                    )
                except FileExistsError:
                    raced = self._read_regular(parent_fd, target_name)
                    if raced != payload:
                        raise ArtifactConflictError(
                            f"immutable artifact conflicts at {'/'.join(parts)}"
                        ) from None
                    return False
                return True
            finally:
                failure_in_flight = sys.exc_info()[0] is not None
                if temporary_fd is not None:
                    os.close(temporary_fd)
                if temporary_exists:
                    try:
                        os.unlink(temporary_name, dir_fd=parent_fd)
                    except FileNotFoundError:
                        pass
                try:
                    os.fsync(parent_fd)
                except OSError:
                    if not failure_in_flight:
                        raise

    @staticmethod
    def _write_all(file_descriptor: int, payload: bytes) -> None:
        view = memoryview(payload)
        while view:
            written = os.write(file_descriptor, view)
            if written <= 0:
                raise OSError("atomic artifact write made no progress")
            view = view[written:]

    @staticmethod
    def _read_regular(parent_fd: int, name: str) -> bytes | None:
        try:
            file_descriptor = os.open(name, os.O_RDONLY | _NOFOLLOW, dir_fd=parent_fd)
        except FileNotFoundError:
            return None
        except OSError as error:
            if error.errno in {errno.ELOOP, errno.ENOTDIR}:
                raise PathEscapeError(f"artifact target is not a regular file: {name}") from error
            raise
        try:
            metadata = os.fstat(file_descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise PathEscapeError(f"artifact target is not a regular file: {name}")
            if stat.S_IMODE(metadata.st_mode) & 0o077:
                raise PathEscapeError(
                    f"artifact target has unsafe permissions: {name}; run chmod 600 on the file"
                )
            chunks: list[bytes] = []
            while chunk := os.read(file_descriptor, 1024 * 1024):
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(file_descriptor)

    @staticmethod
    @contextmanager
    def _parent_descriptor(
        root: Path, directories: tuple[str, ...], *, create: bool
    ) -> Iterator[int]:
        descriptors: list[int] = []
        try:
            current = os.open(root, os.O_RDONLY | _DIRECTORY | _NOFOLLOW)
            descriptors.append(current)
            for directory in directories:
                try:
                    metadata = os.stat(directory, dir_fd=current, follow_symlinks=False)
                except FileNotFoundError:
                    if not create:
                        raise
                    os.mkdir(directory, _DIRECTORY_MODE, dir_fd=current)
                    os.fsync(current)
                    metadata = os.stat(directory, dir_fd=current, follow_symlinks=False)
                if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
                    raise PathEscapeError(f"path component is not a real directory: {directory}")
                try:
                    child = os.open(
                        directory,
                        os.O_RDONLY | _DIRECTORY | _NOFOLLOW,
                        dir_fd=current,
                    )
                except OSError as error:
                    if error.errno in {errno.ELOOP, errno.ENOTDIR}:
                        raise PathEscapeError(
                            f"path component is not a real directory: {directory}"
                        ) from error
                    raise
                descriptors.append(child)
                current = child
            yield current
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)

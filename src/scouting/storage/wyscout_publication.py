"""Sidecar-free staged publication for immutable W04 Wyscout products."""

from __future__ import annotations

import errno
import hashlib
import os
import re
import stat
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_ROOT_NAMES = frozenset({"wyscout-working", "wyscout-manifests", "w04-rebuild-runs"})
_TAIL_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._=-]{0,254}$")
_MAX_PATH_BYTES = 1024
_MAX_PATH_DEPTH = 16
_MAX_SEGMENT_BYTES = 255
_DIRECTORY_MODE = 0o700
_FILE_MODE = 0o600
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_NONBLOCK = getattr(os, "O_NONBLOCK", 0)


class WyscoutPublicationError(RuntimeError):
    """Base class for fail-closed W04 publication errors."""


class PublicationConfigurationError(WyscoutPublicationError):
    """Raised when the closed named-root configuration is unsafe or ambiguous."""


class UndeclaredPublicationRootError(WyscoutPublicationError):
    """Raised when a caller selects a root outside the closed configuration."""


class InvalidPublicationPathError(WyscoutPublicationError):
    """Raised when a publication tail is not a bounded normalized POSIX path."""


class PublicationPathSecurityError(WyscoutPublicationError):
    """Raised for symlink, nonregular, hardlink, mode, or containment failures."""


class PublicationConflictError(WyscoutPublicationError):
    """Raised when immutable final or staged evidence conflicts with a request."""


class PublicationRaceError(WyscoutPublicationError):
    """Raised when a path identity changes during a publication transaction."""


class PublicationCrossDeviceError(WyscoutPublicationError):
    """Raised when staging and final publication are not on one filesystem."""


class PublicationValidationError(WyscoutPublicationError):
    """Raised when serializer-owned bytes fail their caller validator."""


class PublicationRecheckError(WyscoutPublicationError):
    """Raised when the final code/environment/resource recheck fails."""


@dataclass(frozen=True, slots=True)
class WyscoutPublicationRoot:
    """One exact final root and its serializer-owned staging root."""

    final_root: Path
    staging_root: Path


@dataclass(frozen=True, slots=True)
class WyscoutPublicationResult:
    """Guard-read immutable result of a completed or idempotent publication."""

    root_name: str
    relative_path: str
    physical_sha256: str
    size_bytes: int
    created: bool


@dataclass(frozen=True, slots=True)
class _DirectoryIdentity:
    device: int
    inode: int


@dataclass(frozen=True, slots=True)
class _DeclaredRoot:
    final_root: Path
    staging_root: Path
    final_identity: _DirectoryIdentity
    staging_identity: _DirectoryIdentity


@dataclass(frozen=True, slots=True)
class _RegularRead:
    payload: bytes
    metadata: os.stat_result


def _directory_identity(metadata: os.stat_result) -> _DirectoryIdentity:
    return _DirectoryIdentity(device=metadata.st_dev, inode=metadata.st_ino)


def _absolute_directory_parts(path: Path, *, label: str) -> tuple[str, ...]:
    raw = os.fspath(path)
    if not isinstance(raw, str):
        raise PublicationConfigurationError(f"{label} must be a text path")
    if not raw or "\x00" in raw or "\\" in raw:
        raise PublicationConfigurationError(f"{label} is empty or malformed")
    parsed = PurePosixPath(raw)
    raw_parts = raw.split("/")
    if not parsed.is_absolute() or raw_parts[0] != "":
        raise PublicationConfigurationError(f"{label} must be absolute")
    parts = tuple(raw_parts[1:])
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise PublicationConfigurationError(f"{label} must be a normalized absolute path")
    return parts


def _open_absolute_directory(path: Path, *, label: str) -> int:
    parts = _absolute_directory_parts(path, label=label)
    current = os.open("/", os.O_RDONLY | _DIRECTORY | _NOFOLLOW)
    try:
        for part in parts:
            try:
                before = os.stat(part, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError as error:
                raise PublicationConfigurationError(f"{label} does not exist") from error
            if not stat.S_ISDIR(before.st_mode) or stat.S_ISLNK(before.st_mode):
                raise PublicationConfigurationError(f"{label} crosses a non-directory or link")
            try:
                child = os.open(
                    part,
                    os.O_RDONLY | _DIRECTORY | _NOFOLLOW,
                    dir_fd=current,
                )
            except OSError as error:
                if error.errno in {errno.ELOOP, errno.ENOTDIR}:
                    raise PublicationConfigurationError(
                        f"{label} crosses a non-directory or link"
                    ) from error
                raise
            after = os.fstat(child)
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                os.close(child)
                raise PublicationRaceError(f"{label} changed while it was opened")
            os.close(current)
            current = child
        metadata = os.fstat(current)
        if stat.S_IMODE(metadata.st_mode) != _DIRECTORY_MODE:
            raise PublicationConfigurationError(f"{label} must have mode 0700")
        return current
    except BaseException:
        os.close(current)
        raise


def _relative_parts(relative_path: str | os.PathLike[str]) -> tuple[str, ...]:
    raw = os.fspath(relative_path)
    if not isinstance(raw, str):
        raise InvalidPublicationPathError("publication paths must be text")
    if not raw or "\x00" in raw or "\\" in raw:
        raise InvalidPublicationPathError("publication path is empty or malformed")
    if len(raw.encode("utf-8")) > _MAX_PATH_BYTES:
        raise InvalidPublicationPathError("publication path exceeds the bounded length")
    parsed = PurePosixPath(raw)
    parts = tuple(raw.split("/"))
    if parsed.is_absolute() or any(part in {"", ".", ".."} for part in parts):
        raise InvalidPublicationPathError("publication path must be a normal relative path")
    if len(parts) > _MAX_PATH_DEPTH:
        raise InvalidPublicationPathError("publication path exceeds the bounded depth")
    if any(len(part.encode("utf-8")) > _MAX_SEGMENT_BYTES for part in parts):
        raise InvalidPublicationPathError("publication path contains an overlong segment")
    if any(_TAIL_SEGMENT.fullmatch(part) is None for part in parts):
        raise InvalidPublicationPathError("publication path contains a non-canonical segment")
    if parts[-1].endswith(".partial"):
        raise InvalidPublicationPathError("final publication path cannot use the staged suffix")
    staged_name = f"{parts[-1]}.partial"
    if len(staged_name.encode("utf-8")) > _MAX_SEGMENT_BYTES:
        raise InvalidPublicationPathError("staged publication name exceeds the segment bound")
    return parts


def _same_file_identity(first: os.stat_result, second: os.stat_result) -> bool:
    return (first.st_dev, first.st_ino) == (second.st_dev, second.st_ino)


def _stable_file_state(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


class WyscoutStagedPublisher:
    """Publish immutable bytes through exact no-follow staging and hard linking."""

    def __init__(self, roots: Mapping[str, WyscoutPublicationRoot]) -> None:
        if not roots:
            raise PublicationConfigurationError("at least one publication root is required")

        declared: dict[str, _DeclaredRoot] = {}
        all_identities: set[_DirectoryIdentity] = set()
        for root_name, root in roots.items():
            if root_name not in _ROOT_NAMES:
                raise PublicationConfigurationError(f"invalid root name: {root_name!r}")
            if not isinstance(root, WyscoutPublicationRoot):
                raise PublicationConfigurationError(
                    f"root {root_name!r} must be a WyscoutPublicationRoot"
                )
            final_fd = _open_absolute_directory(
                root.final_root,
                label=f"root {root_name!r} final_root",
            )
            staging_fd: int | None = None
            try:
                staging_fd = _open_absolute_directory(
                    root.staging_root,
                    label=f"root {root_name!r} staging_root",
                )
                final_metadata = os.fstat(final_fd)
                staging_metadata = os.fstat(staging_fd)
                final_identity = _directory_identity(final_metadata)
                staging_identity = _directory_identity(staging_metadata)
                if final_metadata.st_dev != staging_metadata.st_dev:
                    raise PublicationCrossDeviceError(
                        f"root {root_name!r} final and staging roots are cross-device"
                    )
                for identity in (final_identity, staging_identity):
                    if identity in all_identities:
                        raise PublicationConfigurationError(
                            "declared final and staging roots must all be distinct"
                        )
                    all_identities.add(identity)
                declared[root_name] = _DeclaredRoot(
                    final_root=root.final_root,
                    staging_root=root.staging_root,
                    final_identity=final_identity,
                    staging_identity=staging_identity,
                )
            finally:
                os.close(final_fd)
                if staging_fd is not None:
                    os.close(staging_fd)
        self._roots = declared

    def publish_bytes(
        self,
        root_name: str,
        relative_path: str | os.PathLike[str],
        payload: bytes,
        *,
        validator: Callable[[bytes], object],
        final_recheck: Callable[[], object],
    ) -> WyscoutPublicationResult:
        """Validate and publish bytes without a sidecar or replacement operation."""

        if not isinstance(payload, bytes):
            raise TypeError("payload must be exact bytes")
        if not callable(validator):
            raise TypeError("validator must be callable")
        if not callable(final_recheck):
            raise TypeError("final_recheck must be callable")
        root = self._root(root_name)
        parts = _relative_parts(relative_path)
        relative = "/".join(parts)
        staged_parts = (*parts[:-1], f"{parts[-1]}.partial")
        digest = hashlib.sha256(payload).hexdigest()

        with self._parent_descriptor(
            root.staging_root,
            root.staging_identity,
            staged_parts[:-1],
            create=True,
        ) as staging_parent_fd:
            with self._parent_descriptor(
                root.final_root,
                root.final_identity,
                parts[:-1],
                create=True,
            ) as final_parent_fd:
                if os.fstat(staging_parent_fd).st_dev != os.fstat(final_parent_fd).st_dev:
                    raise PublicationCrossDeviceError(
                        "staged and final publication parents are cross-device"
                    )
                staging_parent_metadata = os.fstat(staging_parent_fd)
                final_parent_metadata = os.fstat(final_parent_fd)

                staged_name = staged_parts[-1]
                final_name = parts[-1]
                if self._read_regular(staging_parent_fd, staged_name) is not None:
                    raise PublicationConflictError(
                        f"staged evidence already exists at {relative}.partial"
                    )

                existing_final = self._read_regular(final_parent_fd, final_name)
                if existing_final is not None:
                    if existing_final.payload != payload:
                        raise PublicationConflictError(f"immutable final conflicts at {relative}")
                    self._run_validator(validator, existing_final.payload)
                    self._run_final_recheck(final_recheck)
                    confirmed = self._require_named_final(
                        root.final_root,
                        root.final_identity,
                        parts[:-1],
                        final_name,
                        payload=payload,
                        expected_parent=final_parent_metadata,
                        expected_identity=existing_final.metadata,
                    )
                    if (
                        self._read_named_regular(
                            root.staging_root,
                            root.staging_identity,
                            staged_parts[:-1],
                            staged_name,
                            expected_parent=staging_parent_metadata,
                        )
                        is not None
                    ):
                        raise PublicationRaceError(
                            f"staged evidence appeared during replay at {relative}.partial"
                        )
                    return WyscoutPublicationResult(
                        root_name=root_name,
                        relative_path=relative,
                        physical_sha256=hashlib.sha256(confirmed.payload).hexdigest(),
                        size_bytes=len(confirmed.payload),
                        created=False,
                    )

                staged_metadata = self._create_staged(
                    staging_parent_fd,
                    staged_name,
                    payload,
                )
                reopened = self._require_staged(
                    staging_parent_fd,
                    staged_name,
                    payload=payload,
                    expected_identity=staged_metadata,
                    expected_links=1,
                )
                self._run_validator(validator, reopened.payload)
                self._run_final_recheck(final_recheck)
                self._require_staged(
                    staging_parent_fd,
                    staged_name,
                    payload=payload,
                    expected_identity=staged_metadata,
                    expected_links=1,
                )
                self._require_named_staged(
                    root.staging_root,
                    root.staging_identity,
                    staged_parts[:-1],
                    staged_name,
                    payload=payload,
                    expected_parent=staging_parent_metadata,
                    expected_identity=staged_metadata,
                    expected_links=1,
                )
                if (
                    self._read_named_regular(
                        root.final_root,
                        root.final_identity,
                        parts[:-1],
                        final_name,
                        expected_parent=final_parent_metadata,
                    )
                    is not None
                ):
                    raise PublicationRaceError(f"final appeared before promotion at {relative}")

                try:
                    os.link(
                        staged_name,
                        final_name,
                        src_dir_fd=staging_parent_fd,
                        dst_dir_fd=final_parent_fd,
                        follow_symlinks=False,
                    )
                except FileExistsError as error:
                    raise PublicationRaceError(
                        f"final appeared during no-replace promotion at {relative}"
                    ) from error
                except OSError as error:
                    if error.errno == errno.EXDEV:
                        raise PublicationCrossDeviceError(
                            "staged and final publication are cross-device"
                        ) from error
                    raise

                linked_final = self._require_final(
                    final_parent_fd,
                    final_name,
                    payload=payload,
                    expected_identity=staged_metadata,
                    expected_links=2,
                )
                self._require_staged(
                    staging_parent_fd,
                    staged_name,
                    payload=payload,
                    expected_identity=staged_metadata,
                    expected_links=2,
                )
                os.fsync(final_parent_fd)
                os.unlink(staged_name, dir_fd=staging_parent_fd)
                os.fsync(staging_parent_fd)

                if (
                    self._read_named_regular(
                        root.staging_root,
                        root.staging_identity,
                        staged_parts[:-1],
                        staged_name,
                        expected_parent=staging_parent_metadata,
                    )
                    is not None
                ):
                    raise PublicationRaceError("staged name remained after promotion")
                final = self._require_named_final(
                    root.final_root,
                    root.final_identity,
                    parts[:-1],
                    final_name,
                    payload=payload,
                    expected_parent=final_parent_metadata,
                    expected_identity=linked_final.metadata,
                    expected_links=1,
                )
                os.fsync(final_parent_fd)
                if hashlib.sha256(final.payload).hexdigest() != digest:
                    raise PublicationRaceError("final physical digest changed after promotion")
                return WyscoutPublicationResult(
                    root_name=root_name,
                    relative_path=relative,
                    physical_sha256=digest,
                    size_bytes=len(final.payload),
                    created=True,
                )

    def _root(self, root_name: str) -> _DeclaredRoot:
        if not isinstance(root_name, str) or root_name not in _ROOT_NAMES:
            raise UndeclaredPublicationRootError(f"undeclared publication root: {root_name!r}")
        try:
            return self._roots[root_name]
        except KeyError as error:
            raise UndeclaredPublicationRootError(
                f"undeclared publication root: {root_name!r}"
            ) from error

    @staticmethod
    def _run_validator(validator: Callable[[bytes], object], payload: bytes) -> None:
        try:
            result = validator(payload)
        except Exception as error:
            raise PublicationValidationError("staged bytes failed caller validation") from error
        if result is not None:
            raise PublicationValidationError("validator must return None after validation")

    @staticmethod
    def _run_final_recheck(final_recheck: Callable[[], object]) -> None:
        try:
            result = final_recheck()
        except Exception as error:
            raise PublicationRecheckError(
                "final code/environment/resource recheck failed"
            ) from error
        if result is not None:
            raise PublicationRecheckError("final recheck must return None")

    @staticmethod
    def _create_staged(parent_fd: int, name: str, payload: bytes) -> os.stat_result:
        file_descriptor: int | None = None
        try:
            file_descriptor = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW,
                _FILE_MODE,
                dir_fd=parent_fd,
            )
            metadata = os.fstat(file_descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise PublicationPathSecurityError("created staged path is not regular")
            if stat.S_IMODE(metadata.st_mode) != _FILE_MODE:
                raise PublicationPathSecurityError("created staged path must have mode 0600")
            if metadata.st_nlink != 1:
                raise PublicationPathSecurityError("created staged path must have link count one")
            view = memoryview(payload)
            while view:
                written = os.write(file_descriptor, view)
                if written <= 0:
                    raise OSError("staged publication write made no progress")
                view = view[written:]
            os.fsync(file_descriptor)
            completed = os.fstat(file_descriptor)
            if not _same_file_identity(metadata, completed):
                raise PublicationRaceError("staged file identity changed while writing")
            if stat.S_IMODE(completed.st_mode) != _FILE_MODE or completed.st_nlink != 1:
                raise PublicationPathSecurityError("staged file mode or link count changed")
            if completed.st_size != len(payload):
                raise PublicationRaceError("staged file size differs from the complete payload")
            os.fsync(parent_fd)
            return completed
        finally:
            if file_descriptor is not None:
                os.close(file_descriptor)

    @classmethod
    def _require_staged(
        cls,
        parent_fd: int,
        name: str,
        *,
        payload: bytes,
        expected_identity: os.stat_result,
        expected_links: int,
    ) -> _RegularRead:
        staged = cls._read_regular(parent_fd, name, expected_links=expected_links)
        if staged is None:
            raise PublicationRaceError("staged evidence disappeared")
        if not _same_file_identity(staged.metadata, expected_identity):
            raise PublicationRaceError("staged file identity changed")
        if staged.payload != payload:
            raise PublicationRaceError("staged bytes changed")
        return staged

    @classmethod
    def _require_final(
        cls,
        parent_fd: int,
        name: str,
        *,
        payload: bytes,
        expected_identity: os.stat_result,
        expected_links: int = 1,
    ) -> _RegularRead:
        final = cls._read_regular(parent_fd, name, expected_links=expected_links)
        if final is None:
            raise PublicationRaceError("final publication disappeared")
        if not _same_file_identity(final.metadata, expected_identity):
            raise PublicationRaceError("final publication identity changed")
        if final.payload != payload:
            raise PublicationRaceError("final publication bytes changed")
        return final

    @classmethod
    def _read_named_regular(
        cls,
        root: Path,
        root_identity: _DirectoryIdentity,
        directories: tuple[str, ...],
        name: str,
        *,
        expected_parent: os.stat_result,
        expected_links: int = 1,
    ) -> _RegularRead | None:
        try:
            with cls._parent_descriptor(
                root,
                root_identity,
                directories,
                create=False,
            ) as parent_fd:
                if not _same_file_identity(os.fstat(parent_fd), expected_parent):
                    raise PublicationRaceError("named publication parent identity changed")
                return cls._read_regular(parent_fd, name, expected_links=expected_links)
        except FileNotFoundError as error:
            raise PublicationRaceError("named publication parent disappeared") from error

    @classmethod
    def _require_named_staged(
        cls,
        root: Path,
        root_identity: _DirectoryIdentity,
        directories: tuple[str, ...],
        name: str,
        *,
        payload: bytes,
        expected_parent: os.stat_result,
        expected_identity: os.stat_result,
        expected_links: int,
    ) -> _RegularRead:
        staged = cls._read_named_regular(
            root,
            root_identity,
            directories,
            name,
            expected_parent=expected_parent,
            expected_links=expected_links,
        )
        if staged is None:
            raise PublicationRaceError("named staged evidence disappeared")
        if not _same_file_identity(staged.metadata, expected_identity):
            raise PublicationRaceError("named staged file identity changed")
        if staged.payload != payload:
            raise PublicationRaceError("named staged bytes changed")
        return staged

    @classmethod
    def _require_named_final(
        cls,
        root: Path,
        root_identity: _DirectoryIdentity,
        directories: tuple[str, ...],
        name: str,
        *,
        payload: bytes,
        expected_parent: os.stat_result,
        expected_identity: os.stat_result,
        expected_links: int = 1,
    ) -> _RegularRead:
        final = cls._read_named_regular(
            root,
            root_identity,
            directories,
            name,
            expected_parent=expected_parent,
            expected_links=expected_links,
        )
        if final is None:
            raise PublicationRaceError("named final publication disappeared")
        if not _same_file_identity(final.metadata, expected_identity):
            raise PublicationRaceError("named final publication identity changed")
        if final.payload != payload:
            raise PublicationRaceError("named final publication bytes changed")
        return final

    @staticmethod
    def _read_regular(
        parent_fd: int,
        name: str,
        *,
        expected_links: int = 1,
    ) -> _RegularRead | None:
        try:
            before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode):
            raise PublicationPathSecurityError(f"publication path is not regular: {name}")
        if stat.S_IMODE(before.st_mode) != _FILE_MODE:
            raise PublicationPathSecurityError(f"publication path must have mode 0600: {name}")
        if before.st_nlink != expected_links:
            raise PublicationPathSecurityError(
                f"publication path has unexpected link count: {name}"
            )
        try:
            file_descriptor = os.open(
                name,
                os.O_RDONLY | _NOFOLLOW | _NONBLOCK,
                dir_fd=parent_fd,
            )
        except OSError as error:
            if error.errno in {errno.ELOOP, errno.ENOTDIR, errno.ENXIO}:
                raise PublicationPathSecurityError(
                    f"publication path is not a no-follow regular file: {name}"
                ) from error
            raise
        try:
            opened = os.fstat(file_descriptor)
            if not _same_file_identity(before, opened):
                raise PublicationRaceError(f"publication path changed while opening: {name}")
            if not stat.S_ISREG(opened.st_mode):
                raise PublicationPathSecurityError(f"publication path is not regular: {name}")
            if stat.S_IMODE(opened.st_mode) != _FILE_MODE:
                raise PublicationPathSecurityError(f"publication path must have mode 0600: {name}")
            if opened.st_nlink != expected_links:
                raise PublicationPathSecurityError(
                    f"publication path has unexpected link count: {name}"
                )
            chunks: list[bytes] = []
            while chunk := os.read(file_descriptor, 1024 * 1024):
                chunks.append(chunk)
            after = os.fstat(file_descriptor)
            if _stable_file_state(opened) != _stable_file_state(after):
                raise PublicationRaceError(f"publication path changed while reading: {name}")
            payload = b"".join(chunks)
            if len(payload) != after.st_size:
                raise PublicationRaceError(f"publication path size changed while reading: {name}")
            return _RegularRead(payload=payload, metadata=after)
        finally:
            os.close(file_descriptor)

    @staticmethod
    @contextmanager
    def _parent_descriptor(
        root: Path,
        root_identity: _DirectoryIdentity,
        directories: tuple[str, ...],
        *,
        create: bool,
    ) -> Iterator[int]:
        root_fd = _open_absolute_directory(root, label="declared publication root")
        descriptors = [root_fd]
        try:
            if _directory_identity(os.fstat(root_fd)) != root_identity:
                raise PublicationRaceError("declared publication root identity changed")
            current = root_fd
            for directory in directories:
                created = False
                try:
                    before = os.stat(directory, dir_fd=current, follow_symlinks=False)
                except FileNotFoundError:
                    if not create:
                        raise
                    try:
                        os.mkdir(directory, _DIRECTORY_MODE, dir_fd=current)
                    except FileExistsError as error:
                        raise PublicationRaceError(
                            f"directory appeared during creation: {directory}"
                        ) from error
                    os.fsync(current)
                    before = os.stat(directory, dir_fd=current, follow_symlinks=False)
                    created = True
                if not stat.S_ISDIR(before.st_mode) or stat.S_ISLNK(before.st_mode):
                    raise PublicationPathSecurityError(
                        f"publication component is not a real directory: {directory}"
                    )
                if stat.S_IMODE(before.st_mode) != _DIRECTORY_MODE:
                    raise PublicationPathSecurityError(
                        f"publication directory must have mode 0700: {directory}"
                    )
                try:
                    child = os.open(
                        directory,
                        os.O_RDONLY | _DIRECTORY | _NOFOLLOW,
                        dir_fd=current,
                    )
                except OSError as error:
                    if error.errno in {errno.ELOOP, errno.ENOTDIR}:
                        raise PublicationPathSecurityError(
                            f"publication component is not a real directory: {directory}"
                        ) from error
                    raise
                opened = os.fstat(child)
                if not _same_file_identity(before, opened):
                    os.close(child)
                    raise PublicationRaceError(
                        f"publication directory changed while opening: {directory}"
                    )
                if stat.S_IMODE(opened.st_mode) != _DIRECTORY_MODE:
                    os.close(child)
                    raise PublicationPathSecurityError(
                        f"publication directory must have mode 0700: {directory}"
                    )
                descriptors.append(child)
                current = child
                if created:
                    os.fsync(child)
            yield current
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)

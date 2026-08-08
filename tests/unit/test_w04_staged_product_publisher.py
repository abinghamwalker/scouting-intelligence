from __future__ import annotations

import errno
import hashlib
import os
import stat
from collections.abc import Callable
from pathlib import Path

import pytest

from scouting.storage.wyscout_publication import (
    InvalidPublicationPathError,
    PublicationConfigurationError,
    PublicationConflictError,
    PublicationCrossDeviceError,
    PublicationPathSecurityError,
    PublicationRaceError,
    PublicationRecheckError,
    PublicationValidationError,
    UndeclaredPublicationRootError,
    WyscoutPublicationResult,
    WyscoutPublicationRoot,
    WyscoutStagedPublisher,
)

PAYLOAD = b"deterministic-w04-product-bytes\n"
RELATIVE = "build_id=" + "a" * 64 + "/action/part-00000.parquet"
ROOT_NAME = "wyscout-working"


def _make_directory(path: Path) -> None:
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)
        directory.chmod(0o700)
    path.chmod(0o700)


def _publisher(tmp_path: Path) -> tuple[WyscoutStagedPublisher, Path, Path]:
    final_root = tmp_path / "final-root"
    staging_root = tmp_path / "staging-root"
    _make_directory(final_root)
    _make_directory(staging_root)
    publisher = WyscoutStagedPublisher(
        {
            ROOT_NAME: WyscoutPublicationRoot(
                final_root=final_root,
                staging_root=staging_root,
            )
        }
    )
    return publisher, final_root, staging_root


def _accept(payload: bytes) -> None:
    assert payload == PAYLOAD


def _unchanged() -> None:
    return None


def _stage_path(staging_root: Path, relative: str = RELATIVE) -> Path:
    return staging_root / f"{relative}.partial"


def _final_path(final_root: Path, relative: str = RELATIVE) -> Path:
    return final_root / relative


def _write_attack_file(path: Path, payload: bytes = b"attacker") -> None:
    _make_directory(path.parent)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def test_publish_is_sidecar_free_guard_read_and_exactly_repeatable(tmp_path: Path) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    validations: list[bytes] = []
    rechecks = 0

    def validate(payload: bytes) -> None:
        validations.append(payload)
        assert payload == PAYLOAD

    def recheck() -> None:
        nonlocal rechecks
        rechecks += 1

    created = publisher.publish_bytes(
        ROOT_NAME,
        RELATIVE,
        PAYLOAD,
        validator=validate,
        final_recheck=recheck,
    )
    replayed = publisher.publish_bytes(
        ROOT_NAME,
        RELATIVE,
        PAYLOAD,
        validator=validate,
        final_recheck=recheck,
    )

    final = _final_path(final_root)
    assert created.root_name == ROOT_NAME
    assert created.relative_path == RELATIVE
    assert created.physical_sha256 == hashlib.sha256(PAYLOAD).hexdigest()
    assert created.size_bytes == len(PAYLOAD)
    assert created.created is True
    assert replayed == WyscoutPublicationResult(
        root_name=ROOT_NAME,
        relative_path=RELATIVE,
        physical_sha256=hashlib.sha256(PAYLOAD).hexdigest(),
        size_bytes=len(PAYLOAD),
        created=False,
    )
    assert validations == [PAYLOAD, PAYLOAD]
    assert rechecks == 2
    assert final.read_bytes() == PAYLOAD
    assert stat.S_IMODE(final.stat().st_mode) == 0o600
    assert final.stat().st_nlink == 1
    assert not _stage_path(staging_root).exists()
    assert tuple(final.parent.glob("*.sha256")) == ()
    assert tuple(final.parent.glob("*.manifest.json")) == ()
    assert tuple(staging_root.rglob("*partial")) == ()
    for directory in (
        final_root / ("build_id=" + "a" * 64),
        final.parent,
        staging_root / ("build_id=" + "a" * 64),
        _stage_path(staging_root).parent,
    ):
        assert stat.S_IMODE(directory.stat().st_mode) == 0o700


def test_equal_final_replay_rejects_regular_staged_appearance_at_final_checkpoint(
    tmp_path: Path,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    publisher.publish_bytes(
        ROOT_NAME,
        RELATIVE,
        PAYLOAD,
        validator=_accept,
        final_recheck=_unchanged,
    )
    final = _final_path(final_root)
    staged = _stage_path(staging_root)
    final_before = (
        final.read_bytes(),
        final.stat().st_dev,
        final.stat().st_ino,
        final.stat().st_mode,
        final.stat().st_nlink,
    )

    def create_staged_evidence() -> None:
        _write_attack_file(staged, b"raced-staged-evidence")

    with pytest.raises(PublicationRaceError, match="staged evidence appeared during replay"):
        publisher.publish_bytes(
            ROOT_NAME,
            RELATIVE,
            PAYLOAD,
            validator=_accept,
            final_recheck=create_staged_evidence,
        )

    assert (
        final.read_bytes(),
        final.stat().st_dev,
        final.stat().st_ino,
        final.stat().st_mode,
        final.stat().st_nlink,
    ) == final_before
    assert staged.read_bytes() == b"raced-staged-evidence"
    assert stat.S_IMODE(staged.stat().st_mode) == 0o600
    assert staged.stat().st_nlink == 1


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo", "directory", "unsafe-mode"])
def test_equal_final_replay_rejects_every_nonregular_or_unsafe_staged_appearance(
    tmp_path: Path,
    kind: str,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    publisher.publish_bytes(
        ROOT_NAME,
        RELATIVE,
        PAYLOAD,
        validator=_accept,
        final_recheck=_unchanged,
    )
    final = _final_path(final_root)
    staged = _stage_path(staging_root)
    final_before = (final.read_bytes(), final.stat().st_dev, final.stat().st_ino)
    attacker = tmp_path / f"replay-{kind}-evidence"

    def create_unsafe_staged_evidence() -> None:
        if kind == "symlink":
            _write_attack_file(attacker, b"symlink-evidence")
            staged.symlink_to(attacker)
        elif kind == "hardlink":
            _write_attack_file(attacker, b"hardlink-evidence")
            os.link(attacker, staged)
        elif kind == "fifo":
            os.mkfifo(staged, 0o600)
        elif kind == "directory":
            _make_directory(staged)
        else:
            _write_attack_file(staged, b"unsafe-mode-evidence")
            staged.chmod(0o640)

    with pytest.raises(PublicationPathSecurityError):
        publisher.publish_bytes(
            ROOT_NAME,
            RELATIVE,
            PAYLOAD,
            validator=_accept,
            final_recheck=create_unsafe_staged_evidence,
        )

    assert (final.read_bytes(), final.stat().st_dev, final.stat().st_ino) == final_before
    if kind == "symlink":
        assert staged.is_symlink()
        assert attacker.read_bytes() == b"symlink-evidence"
    elif kind == "hardlink":
        assert staged.read_bytes() == b"hardlink-evidence"
        assert staged.stat().st_ino == attacker.stat().st_ino
        assert staged.stat().st_nlink == attacker.stat().st_nlink == 2
    elif kind == "fifo":
        assert stat.S_ISFIFO(staged.lstat().st_mode)
    elif kind == "directory":
        assert staged.is_dir()
    else:
        assert staged.read_bytes() == b"unsafe-mode-evidence"
        assert stat.S_IMODE(staged.stat().st_mode) == 0o640


@pytest.mark.parametrize("replacement", [False, True])
def test_equal_final_replay_rejects_disappeared_or_replaced_staging_parent(
    tmp_path: Path,
    replacement: bool,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    publisher.publish_bytes(
        ROOT_NAME,
        RELATIVE,
        PAYLOAD,
        validator=_accept,
        final_recheck=_unchanged,
    )
    final = _final_path(final_root)
    staged = _stage_path(staging_root)
    staged_parent = staged.parent
    moved_parent = staged_parent.with_name("action-moved-during-replay")
    final_before = (final.read_bytes(), final.stat().st_dev, final.stat().st_ino)

    def replace_staging_parent() -> None:
        _write_attack_file(staged, b"moved-staged-evidence")
        staged_parent.rename(moved_parent)
        if replacement:
            _make_directory(staged_parent)

    with pytest.raises(PublicationRaceError, match="named publication parent"):
        publisher.publish_bytes(
            ROOT_NAME,
            RELATIVE,
            PAYLOAD,
            validator=_accept,
            final_recheck=replace_staging_parent,
        )

    assert (final.read_bytes(), final.stat().st_dev, final.stat().st_ino) == final_before
    assert (moved_parent / staged.name).read_bytes() == b"moved-staged-evidence"
    if replacement:
        assert staged_parent.is_dir()
        assert tuple(staged_parent.iterdir()) == ()
    else:
        assert not staged_parent.exists()


def test_unequal_final_fails_without_staging_or_replacement(tmp_path: Path) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    final = _final_path(final_root)
    _write_attack_file(final, b"existing-evidence")

    with pytest.raises(PublicationConflictError, match="immutable final conflicts"):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert final.read_bytes() == b"existing-evidence"
    assert not _stage_path(staging_root).exists()


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo", "directory"])
def test_preexisting_staged_links_and_nonregular_evidence_fail_closed(
    tmp_path: Path,
    kind: str,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    staged = _stage_path(staging_root)
    _make_directory(staged.parent)
    if kind == "symlink":
        attacker = tmp_path / "attacker-staged"
        _write_attack_file(attacker)
        staged.symlink_to(attacker)
    elif kind == "hardlink":
        attacker = tmp_path / "attacker-staged"
        _write_attack_file(attacker)
        os.link(attacker, staged)
    elif kind == "fifo":
        os.mkfifo(staged, 0o600)
    else:
        _make_directory(staged)

    with pytest.raises(PublicationPathSecurityError):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert os.path.lexists(staged)
    assert not _final_path(final_root).exists()


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo", "directory"])
def test_preexisting_final_links_and_nonregular_evidence_fail_closed(
    tmp_path: Path,
    kind: str,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    final = _final_path(final_root)
    _make_directory(final.parent)
    if kind == "symlink":
        attacker = tmp_path / "attacker-final"
        _write_attack_file(attacker)
        final.symlink_to(attacker)
    elif kind == "hardlink":
        attacker = tmp_path / "attacker-final"
        _write_attack_file(attacker)
        os.link(attacker, final)
    elif kind == "fifo":
        os.mkfifo(final, 0o600)
    else:
        _make_directory(final)

    with pytest.raises(PublicationPathSecurityError):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert os.path.lexists(final)
    assert not _stage_path(staging_root).exists()


@pytest.mark.parametrize(
    "relative",
    [
        "",
        ".",
        "..",
        "/absolute.parquet",
        "a//b.parquet",
        "a/./b.parquet",
        "a/../b.parquet",
        "a\\b.parquet",
        "a/\x00b.parquet",
        "a/file.partial",
        "a/not canonical.parquet",
        "a/%2e%2e.parquet",
        "é/file.parquet",
    ],
)
def test_malformed_or_noncanonical_publication_paths_are_rejected_before_write(
    tmp_path: Path,
    relative: str,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)

    with pytest.raises(InvalidPublicationPathError):
        publisher.publish_bytes(
            ROOT_NAME, relative, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert tuple(final_root.iterdir()) == ()
    assert tuple(staging_root.iterdir()) == ()


def test_path_depth_length_and_staged_suffix_bounds_are_rejected(tmp_path: Path) -> None:
    publisher, _, _ = _publisher(tmp_path)
    paths = (
        "/".join(["a"] * 17),
        "a/" + "b" * 256,
        "a/" + "b" * 248,
        "a/" + "/".join(["b" * 64] * 16),
    )
    for relative in paths:
        with pytest.raises(InvalidPublicationPathError):
            publisher.publish_bytes(
                ROOT_NAME, relative, PAYLOAD, validator=_accept, final_recheck=_unchanged
            )


@pytest.mark.parametrize(
    "alias",
    [
        "silver",
        "bronze",
        "gold",
        "manifests",
        "runs",
        "valid-token",
        "wyscout-working-copy",
        "w04_rebuild_runs",
        "",
        7,
        True,
        None,
        ("wyscout-working",),
    ],
)
def test_every_root_alias_and_non_string_fails_before_write(
    tmp_path: Path,
    alias: object,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    with pytest.raises(UndeclaredPublicationRootError):
        publisher.publish_bytes(
            alias,  # type: ignore[arg-type]
            RELATIVE,
            PAYLOAD,
            validator=_accept,
            final_recheck=_unchanged,
        )
    assert tuple(final_root.iterdir()) == ()
    assert tuple(staging_root.iterdir()) == ()


def test_unsafe_root_configurations_fail_closed(tmp_path: Path) -> None:
    _, final_root, staging_root = _publisher(tmp_path)
    with pytest.raises(PublicationConfigurationError, match="invalid root name"):
        WyscoutStagedPublisher({"Silver": WyscoutPublicationRoot(final_root, staging_root)})
    with pytest.raises(PublicationConfigurationError, match="must be absolute"):
        WyscoutStagedPublisher(
            {
                ROOT_NAME: WyscoutPublicationRoot(
                    Path("relative-final"),
                    staging_root,
                )
            }
        )
    with pytest.raises(PublicationConfigurationError, match="distinct"):
        WyscoutStagedPublisher({ROOT_NAME: WyscoutPublicationRoot(final_root, final_root)})


def test_all_three_exact_authorized_root_names_can_be_declared(tmp_path: Path) -> None:
    roots: dict[str, WyscoutPublicationRoot] = {}
    paths: dict[str, tuple[Path, Path]] = {}
    for root_name in ("wyscout-working", "wyscout-manifests", "w04-rebuild-runs"):
        final_root = tmp_path / root_name / "final"
        staging_root = tmp_path / root_name / "staging"
        _make_directory(final_root)
        _make_directory(staging_root)
        roots[root_name] = WyscoutPublicationRoot(final_root, staging_root)
        paths[root_name] = (final_root, staging_root)

    publisher = WyscoutStagedPublisher(roots)
    for index, root_name in enumerate(roots):
        result = publisher.publish_bytes(
            root_name,
            f"artifact-{index}.json",
            PAYLOAD,
            validator=_accept,
            final_recheck=_unchanged,
        )
        final_root, staging_root = paths[root_name]
        assert result.root_name == root_name
        assert (final_root / f"artifact-{index}.json").read_bytes() == PAYLOAD
        assert not (staging_root / f"artifact-{index}.json.partial").exists()


def test_root_symlink_and_mode_drift_are_rejected_without_chmod(tmp_path: Path) -> None:
    real_final = tmp_path / "real-final"
    staging_root = tmp_path / "staging"
    _make_directory(real_final)
    _make_directory(staging_root)
    linked_final = tmp_path / "linked-final"
    linked_final.symlink_to(real_final, target_is_directory=True)
    with pytest.raises(PublicationConfigurationError, match="link"):
        WyscoutStagedPublisher({ROOT_NAME: WyscoutPublicationRoot(linked_final, staging_root)})

    real_final.chmod(0o755)
    with pytest.raises(PublicationConfigurationError, match="mode 0700"):
        WyscoutStagedPublisher({ROOT_NAME: WyscoutPublicationRoot(real_final, staging_root)})
    assert stat.S_IMODE(real_final.stat().st_mode) == 0o755


@pytest.mark.parametrize("target", ["staged", "final"])
def test_existing_file_mode_drift_fails_without_chmod(tmp_path: Path, target: str) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    path = _stage_path(staging_root) if target == "staged" else _final_path(final_root)
    _write_attack_file(path, PAYLOAD)
    path.chmod(0o640)

    with pytest.raises(PublicationPathSecurityError, match="mode 0600"):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert stat.S_IMODE(path.stat().st_mode) == 0o640


def test_partial_write_failure_preserves_exact_staged_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    real_write = os.write
    writes = 0

    def partial_then_fail(file_descriptor: int, payload: bytes | memoryview) -> int:
        nonlocal writes
        writes += 1
        if writes == 1:
            return real_write(file_descriptor, bytes(payload[:3]))
        raise OSError(errno.EIO, "simulated partial-write failure")

    monkeypatch.setattr("scouting.storage.wyscout_publication.os.write", partial_then_fail)
    with pytest.raises(OSError, match="simulated partial-write failure"):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    staged = _stage_path(staging_root)
    assert staged.read_bytes() == PAYLOAD[:3]
    assert stat.S_IMODE(staged.stat().st_mode) == 0o600
    assert not _final_path(final_root).exists()


@pytest.mark.parametrize("non_none", [False, True])
def test_validator_failure_preserves_complete_staged_evidence(
    tmp_path: Path,
    non_none: bool,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)

    def fail_validation(payload: bytes) -> object:
        assert payload == PAYLOAD
        if non_none:
            return False
        raise ValueError("invalid serializer bytes")

    with pytest.raises(PublicationValidationError):
        publisher.publish_bytes(
            ROOT_NAME,
            RELATIVE,
            PAYLOAD,
            validator=fail_validation,
            final_recheck=_unchanged,
        )

    assert _stage_path(staging_root).read_bytes() == PAYLOAD
    assert not _final_path(final_root).exists()


@pytest.mark.parametrize("non_none", [False, True])
def test_final_recheck_failure_preserves_complete_staged_evidence(
    tmp_path: Path,
    non_none: bool,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)

    def fail_recheck() -> object:
        if non_none:
            return "changed"
        raise ValueError("resource digest changed")

    with pytest.raises(PublicationRecheckError):
        publisher.publish_bytes(
            ROOT_NAME,
            RELATIVE,
            PAYLOAD,
            validator=_accept,
            final_recheck=fail_recheck,
        )

    assert _stage_path(staging_root).read_bytes() == PAYLOAD
    assert not _final_path(final_root).exists()


@pytest.mark.parametrize("failure_target", ["file", "directory"])
def test_fsync_failure_preserves_staged_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_target: str,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    real_fsync = os.fsync
    failed = False

    def fail_selected_fsync(file_descriptor: int) -> None:
        nonlocal failed
        metadata = os.fstat(file_descriptor)
        selected = (
            stat.S_ISREG(metadata.st_mode)
            if failure_target == "file"
            else stat.S_ISDIR(metadata.st_mode)
        )
        if selected and not failed:
            failed = True
            raise OSError(errno.EIO, f"simulated {failure_target} fsync failure")
        real_fsync(file_descriptor)

    monkeypatch.setattr("scouting.storage.wyscout_publication.os.fsync", fail_selected_fsync)
    with pytest.raises(OSError, match="simulated"):
        publisher.publish_bytes(
            ROOT_NAME, "artifact.parquet", PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    staged = _stage_path(staging_root, "artifact.parquet")
    assert staged.read_bytes() == PAYLOAD
    assert not _final_path(final_root, "artifact.parquet").exists()


def test_no_follow_reopen_failure_preserves_staged_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    real_open = os.open

    def fail_staged_reopen(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if os.fspath(path) == "artifact.parquet.partial" and not flags & os.O_CREAT:
            raise OSError(errno.EIO, "simulated staged reopen failure")
        return int(real_open(path, flags, mode, dir_fd=dir_fd))

    monkeypatch.setattr("scouting.storage.wyscout_publication.os.open", fail_staged_reopen)
    with pytest.raises(OSError, match="simulated staged reopen failure"):
        publisher.publish_bytes(
            ROOT_NAME, "artifact.parquet", PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert _stage_path(staging_root, "artifact.parquet").read_bytes() == PAYLOAD
    assert not _final_path(final_root, "artifact.parquet").exists()


def test_mode_and_hardlink_mutation_during_validation_fail_closed(tmp_path: Path) -> None:
    for mutation in ("mode", "hardlink"):
        case_root = tmp_path / mutation
        _make_directory(case_root)
        publisher, final_root, staging_root = _publisher(case_root)
        staged = _stage_path(staging_root)

        def mutate(_: bytes) -> None:
            if mutation == "mode":
                staged.chmod(0o640)
            else:
                os.link(staged, case_root / "attacker-alias")

        with pytest.raises(PublicationPathSecurityError):
            publisher.publish_bytes(
                ROOT_NAME, RELATIVE, PAYLOAD, validator=mutate, final_recheck=_unchanged
            )

        assert staged.exists()
        assert not _final_path(final_root).exists()
        if mutation == "mode":
            assert stat.S_IMODE(staged.stat().st_mode) == 0o640
        else:
            assert staged.stat().st_nlink == 2


def test_final_appearance_during_recheck_is_a_race_and_never_replaced(tmp_path: Path) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    final = _final_path(final_root)

    def create_racing_final() -> None:
        _write_attack_file(final, b"racing-final")

    with pytest.raises(PublicationRaceError, match="appeared before promotion"):
        publisher.publish_bytes(
            ROOT_NAME,
            RELATIVE,
            PAYLOAD,
            validator=_accept,
            final_recheck=create_racing_final,
        )

    assert final.read_bytes() == b"racing-final"
    assert _stage_path(staging_root).read_bytes() == PAYLOAD


def test_link_target_race_preserves_both_final_and_staged_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)

    def race_link(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        del source, src_dir_fd, follow_symlinks
        descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=dst_dir_fd,
        )
        try:
            os.write(descriptor, b"raced")
        finally:
            os.close(descriptor)
        raise FileExistsError(errno.EEXIST, "simulated link target race")

    monkeypatch.setattr("scouting.storage.wyscout_publication.os.link", race_link)
    with pytest.raises(PublicationRaceError, match="during no-replace promotion"):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert _final_path(final_root).read_bytes() == b"raced"
    assert _stage_path(staging_root).read_bytes() == PAYLOAD


def test_cross_device_link_failure_preserves_staged_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)

    def cross_device_link(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise OSError(errno.EXDEV, "simulated cross-device promotion")

    monkeypatch.setattr("scouting.storage.wyscout_publication.os.link", cross_device_link)
    with pytest.raises(PublicationCrossDeviceError, match="cross-device"):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    assert _stage_path(staging_root).read_bytes() == PAYLOAD
    assert not _final_path(final_root).exists()


def test_nested_symlink_component_cannot_escape_either_root(tmp_path: Path) -> None:
    for selected in ("staging", "final"):
        case_root = tmp_path / selected
        _make_directory(case_root)
        publisher, final_root, staging_root = _publisher(case_root)
        outside = case_root / "outside"
        _make_directory(outside)
        selected_root = staging_root if selected == "staging" else final_root
        (selected_root / "escape").symlink_to(outside, target_is_directory=True)

        with pytest.raises(PublicationPathSecurityError, match="real directory"):
            publisher.publish_bytes(
                ROOT_NAME,
                "escape/artifact.parquet",
                PAYLOAD,
                validator=_accept,
                final_recheck=_unchanged,
            )

        assert tuple(outside.iterdir()) == ()


@pytest.mark.parametrize("selected", ["staging", "final"])
def test_parent_directory_rename_during_callbacks_fails_path_binding(
    tmp_path: Path,
    selected: str,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    final_parent = _final_path(final_root).parent
    staged_parent = _stage_path(staging_root).parent

    def rename_parent() -> None:
        parent = staged_parent if selected == "staging" else final_parent
        parent.rename(parent.with_name(f"{parent.name}-moved"))
        _make_directory(parent)

    def validator(_: bytes) -> None:
        if selected == "staging":
            rename_parent()

    def recheck() -> None:
        if selected == "final":
            rename_parent()

    with pytest.raises(PublicationRaceError, match="parent identity changed"):
        publisher.publish_bytes(
            ROOT_NAME,
            RELATIVE,
            PAYLOAD,
            validator=validator,
            final_recheck=recheck,
        )

    assert not _final_path(final_root).exists()


def test_root_identity_and_nested_directory_mode_drift_fail_closed(tmp_path: Path) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    moved = tmp_path / "moved-staging"
    staging_root.rename(moved)
    _make_directory(staging_root)
    with pytest.raises(PublicationRaceError, match="root identity changed"):
        publisher.publish_bytes(
            ROOT_NAME, "artifact.parquet", PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    publisher, final_root, staging_root = _publisher(tmp_path / "mode-case")
    nested = staging_root / "nested"
    _make_directory(nested)
    nested.chmod(0o755)
    with pytest.raises(PublicationPathSecurityError, match="mode 0700"):
        publisher.publish_bytes(
            ROOT_NAME,
            "nested/artifact.parquet",
            PAYLOAD,
            validator=_accept,
            final_recheck=_unchanged,
        )
    assert stat.S_IMODE(nested.stat().st_mode) == 0o755
    assert not _final_path(final_root, "nested/artifact.parquet").exists()


def test_unlink_failure_retains_two_link_evidence_and_returns_no_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    real_unlink = os.unlink

    def fail_stage_unlink(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        dir_fd: int | None = None,
    ) -> None:
        if os.fsdecode(path).endswith(".partial"):
            raise OSError(errno.EIO, "simulated staged unlink failure")
        real_unlink(path, dir_fd=dir_fd)

    monkeypatch.setattr("scouting.storage.wyscout_publication.os.unlink", fail_stage_unlink)
    with pytest.raises(OSError, match="simulated staged unlink failure"):
        publisher.publish_bytes(
            ROOT_NAME, RELATIVE, PAYLOAD, validator=_accept, final_recheck=_unchanged
        )

    staged = _stage_path(staging_root)
    final = _final_path(final_root)
    assert staged.read_bytes() == PAYLOAD
    assert final.read_bytes() == PAYLOAD
    assert staged.stat().st_ino == final.stat().st_ino
    assert staged.stat().st_nlink == final.stat().st_nlink == 2


@pytest.mark.parametrize("boundary", ["final-parent-after-link", "staging-parent-after-unlink"])
def test_post_link_directory_fsync_failures_have_exact_evidence_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    boundary: str,
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    relative = "artifact.parquet"
    final = _final_path(final_root, relative)
    staged = _stage_path(staging_root, relative)
    sentinel = final_root / "preexisting-evidence.json"
    _write_attack_file(sentinel, b"preexisting-final-evidence")
    sentinel_identity = (sentinel.stat().st_dev, sentinel.stat().st_ino)
    real_fsync = os.fsync
    injected = False

    def fail_at_exact_boundary(file_descriptor: int) -> None:
        nonlocal injected
        metadata = os.fstat(file_descriptor)
        if not stat.S_ISDIR(metadata.st_mode):
            real_fsync(file_descriptor)
            return
        final_link_count = final.stat().st_nlink if final.exists() else None
        stage_present = os.path.lexists(staged)
        final_parent_selected = (
            boundary == "final-parent-after-link"
            and metadata.st_dev == final_root.stat().st_dev
            and metadata.st_ino == final_root.stat().st_ino
            and final_link_count == 2
            and stage_present
        )
        staging_parent_selected = (
            boundary == "staging-parent-after-unlink"
            and metadata.st_dev == staging_root.stat().st_dev
            and metadata.st_ino == staging_root.stat().st_ino
            and final_link_count == 1
            and not stage_present
        )
        if not injected and (final_parent_selected or staging_parent_selected):
            injected = True
            raise OSError(errno.EIO, f"simulated {boundary} fsync failure")
        real_fsync(file_descriptor)

    monkeypatch.setattr(
        "scouting.storage.wyscout_publication.os.fsync",
        fail_at_exact_boundary,
    )
    with pytest.raises(OSError, match=f"simulated {boundary} fsync failure"):
        publisher.publish_bytes(
            ROOT_NAME,
            relative,
            PAYLOAD,
            validator=_accept,
            final_recheck=_unchanged,
        )

    assert injected is True
    assert final.read_bytes() == PAYLOAD
    assert stat.S_IMODE(final.stat().st_mode) == 0o600
    assert sentinel.read_bytes() == b"preexisting-final-evidence"
    assert (sentinel.stat().st_dev, sentinel.stat().st_ino) == sentinel_identity
    assert sentinel.stat().st_nlink == 1
    if boundary == "final-parent-after-link":
        assert staged.read_bytes() == PAYLOAD
        assert staged.stat().st_ino == final.stat().st_ino
        assert staged.stat().st_nlink == final.stat().st_nlink == 2
    else:
        assert not os.path.lexists(staged)
        assert final.stat().st_nlink == 1
    assert tuple(final_root.glob("*.sha256")) == ()
    assert tuple(staging_root.glob("*.sha256")) == ()


def test_payload_and_callback_types_fail_before_write(tmp_path: Path) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    cases: tuple[tuple[object, object, object], ...] = (
        (bytearray(PAYLOAD), _accept, _unchanged),
        (PAYLOAD, None, _unchanged),
        (PAYLOAD, _accept, None),
    )
    for payload, validator, final_recheck in cases:
        with pytest.raises(TypeError):
            publisher.publish_bytes(
                ROOT_NAME,
                RELATIVE,
                payload,  # type: ignore[arg-type]
                validator=validator,  # type: ignore[arg-type]
                final_recheck=final_recheck,  # type: ignore[arg-type]
            )
    assert tuple(final_root.iterdir()) == ()
    assert tuple(staging_root.iterdir()) == ()


def test_callbacks_run_in_validate_then_recheck_order(tmp_path: Path) -> None:
    publisher, _, _ = _publisher(tmp_path)
    order: list[str] = []

    def validate(_: bytes) -> None:
        order.append("validate")

    def recheck() -> None:
        order.append("recheck")

    publisher.publish_bytes(
        ROOT_NAME,
        "artifact.parquet",
        PAYLOAD,
        validator=validate,
        final_recheck=recheck,
    )
    assert order == ["validate", "recheck"]


def test_test_helpers_use_only_the_passed_temporary_root(tmp_path: Path) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    publisher.publish_bytes(
        ROOT_NAME,
        "artifact.parquet",
        PAYLOAD,
        validator=lambda _: None,
        final_recheck=lambda: None,
    )
    assert final_root.is_relative_to(tmp_path)
    assert staging_root.is_relative_to(tmp_path)


Validator = Callable[[bytes], object]
Recheck = Callable[[], object]


@pytest.mark.parametrize(
    ("validator", "recheck", "error"),
    [
        (lambda _: 0, _unchanged, PublicationValidationError),
        (_accept, lambda: False, PublicationRecheckError),
    ],
)
def test_falsey_non_none_callback_results_are_not_treated_as_success(
    tmp_path: Path,
    validator: Validator,
    recheck: Recheck,
    error: type[Exception],
) -> None:
    publisher, final_root, staging_root = _publisher(tmp_path)
    with pytest.raises(error):
        publisher.publish_bytes(
            ROOT_NAME,
            "artifact.parquet",
            PAYLOAD,
            validator=validator,
            final_recheck=recheck,
        )
    assert _stage_path(staging_root, "artifact.parquet").read_bytes() == PAYLOAD
    assert not _final_path(final_root, "artifact.parquet").exists()

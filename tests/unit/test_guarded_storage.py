from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from scouting.storage import (
    ArtifactConflictError,
    FormatError,
    GuardedStorage,
    InvalidArtifactPathError,
    PathEscapeError,
    StorageConfigurationError,
    UndeclaredRootError,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    parquet_bytes,
    read_parquet_bytes,
    sha256_hex,
)

LINEAGE = {"producing_run_id": "run-001", "source_manifest_ids": ["manifest-001"]}
RETENTION = {"delete_after_utc": "2030-01-01T00:00:00Z", "policy": "synthetic-review"}


@pytest.fixture
def artifacts(tmp_path: Path) -> Path:
    return tmp_path / "artifacts"


@pytest.fixture
def storage(artifacts: Path) -> GuardedStorage:
    return GuardedStorage({"reviewed": artifacts})


def test_declared_roots_are_explicit_absolute_and_distinct(tmp_path: Path) -> None:
    with pytest.raises(StorageConfigurationError, match="absolute"):
        GuardedStorage({"reviewed": Path("relative")})
    with pytest.raises(StorageConfigurationError, match="invalid root"):
        GuardedStorage({"NOT VALID": tmp_path / "invalid"})

    root = tmp_path / "same"
    with pytest.raises(StorageConfigurationError, match="distinct"):
        GuardedStorage({"first": root, "second": root})


@pytest.mark.parametrize(
    "relative_path",
    [
        "/tmp/escape.json",
        "../escape.json",
        "nested/../../escape.json",
        "./artifact.json",
        "nested//artifact.json",
        "nested\\artifact.json",
        "",
    ],
)
def test_rejects_absolute_parent_and_malformed_paths(
    storage: GuardedStorage, relative_path: str
) -> None:
    with pytest.raises(InvalidArtifactPathError):
        storage.write_json(
            "reviewed",
            relative_path,
            {"safe": True},
            lineage=LINEAGE,
            retention=RETENTION,
        )


def test_rejects_undeclared_root(storage: GuardedStorage) -> None:
    with pytest.raises(UndeclaredRootError):
        storage.write_json(
            "unknown",
            "artifact.json",
            {"safe": True},
            lineage=LINEAGE,
            retention=RETENTION,
        )


def test_rejects_parent_and_target_symlink_escapes(
    storage: GuardedStorage, artifacts: Path, tmp_path: Path
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (artifacts / "parent-link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(PathEscapeError):
        storage.write_bytes(
            "reviewed",
            "parent-link/escape.bin",
            b"blocked",
            media_type="application/octet-stream",
            lineage=LINEAGE,
            retention=RETENTION,
        )
    assert list(outside.iterdir()) == []

    outside_file = outside / "outside.bin"
    outside_file.write_bytes(b"unchanged")
    (artifacts / "target-link.bin").symlink_to(outside_file)
    with pytest.raises(PathEscapeError):
        storage.write_bytes(
            "reviewed",
            "target-link.bin",
            b"blocked",
            media_type="application/octet-stream",
            lineage=LINEAGE,
            retention=RETENTION,
        )
    assert outside_file.read_bytes() == b"unchanged"


def test_payload_precedes_complete_manifest_and_has_restrictive_modes(
    storage: GuardedStorage, artifacts: Path
) -> None:
    receipt = storage.write_bytes(
        "reviewed",
        "runs/001/payload.bin",
        b"payload",
        media_type="application/octet-stream",
        lineage=LINEAGE,
        retention=RETENTION,
    )

    assert receipt.sha256 == sha256_hex(b"payload")
    assert receipt.size_bytes == 7
    assert receipt.payload_created is True
    assert receipt.manifest_created is True
    payload_path = artifacts / receipt.relative_path
    manifest_path = artifacts / receipt.manifest_relative_path
    assert payload_path.read_bytes() == b"payload"
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest == {
        "lineage": LINEAGE,
        "media_type": "application/octet-stream",
        "payload": {
            "path": "runs/001/payload.bin",
            "sha256": sha256_hex(b"payload"),
            "size_bytes": 7,
        },
        "retention": RETENTION,
        "schema_version": 1,
        "state": "complete",
    }
    assert stat.S_IMODE(payload_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(manifest_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(payload_path.parent.stat().st_mode) == 0o700


def test_partial_write_is_cleaned_and_never_creates_completion_manifest(
    storage: GuardedStorage, artifacts: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_after_partial_write(file_descriptor: int, payload: bytes) -> None:
        os.write(file_descriptor, payload[:2])
        raise OSError("simulated disk failure")

    monkeypatch.setattr(storage, "_write_all", fail_after_partial_write)
    with pytest.raises(OSError, match="simulated"):
        storage.write_bytes(
            "reviewed",
            "runs/failed.bin",
            b"payload",
            media_type="application/octet-stream",
            lineage=LINEAGE,
            retention=RETENTION,
        )

    assert not (artifacts / "runs/failed.bin").exists()
    assert not (artifacts / "runs/failed.bin.manifest.json").exists()
    assert list((artifacts / "runs").iterdir()) == []


def test_cleanup_directory_fsync_does_not_mask_write_failure(
    storage: GuardedStorage,
    artifacts: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_write(file_descriptor: int, payload: bytes) -> None:
        del file_descriptor, payload
        raise OSError("primary write failure")

    def fail_fsync(file_descriptor: int) -> None:
        del file_descriptor
        raise OSError("secondary directory fsync failure")

    monkeypatch.setattr(storage, "_write_all", fail_write)
    monkeypatch.setattr("scouting.storage.guarded.os.fsync", fail_fsync)

    with pytest.raises(OSError, match="primary write failure"):
        storage.write_bytes(
            "reviewed",
            "failed.bin",
            b"payload",
            media_type="application/octet-stream",
            lineage=LINEAGE,
            retention=RETENTION,
        )

    assert list(artifacts.iterdir()) == []


def test_unsafe_permission_error_names_the_repair(
    storage: GuardedStorage,
    artifacts: Path,
) -> None:
    target = artifacts / "unsafe.bin"
    target.write_bytes(b"unsafe")
    target.chmod(0o644)

    with pytest.raises(PathEscapeError, match="chmod 600"):
        storage.read_bytes("reviewed", "unsafe.bin")


def test_open_binary_streams_a_guarded_regular_artifact(storage: GuardedStorage) -> None:
    storage.write_bytes(
        "reviewed",
        "streamed.bin",
        b"one-two-three",
        media_type="application/octet-stream",
        lineage=LINEAGE,
        retention=RETENTION,
    )

    with storage.open_binary("reviewed", "streamed.bin") as stream:
        assert stream.read(4) == b"one-"
        assert stream.read() == b"two-three"


def test_identical_retry_is_idempotent_and_conflict_fails_closed(storage: GuardedStorage) -> None:
    first = storage.write_json(
        "reviewed",
        "result.json",
        {"b": 2, "a": 1},
        lineage=LINEAGE,
        retention=RETENTION,
    )
    retry = storage.write_json(
        "reviewed",
        "result.json",
        {"a": 1, "b": 2},
        lineage=LINEAGE,
        retention=RETENTION,
    )
    assert first.payload_created is True
    assert first.manifest_created is True
    assert retry.payload_created is False
    assert retry.manifest_created is False

    with pytest.raises(ArtifactConflictError):
        storage.write_json(
            "reviewed",
            "result.json",
            {"a": 999},
            lineage=LINEAGE,
            retention=RETENTION,
        )
    assert storage.read_bytes("reviewed", "result.json") == b'{"a":1,"b":2}\n'


def test_conflicting_manifest_metadata_does_not_change_payload(storage: GuardedStorage) -> None:
    storage.write_bytes(
        "reviewed",
        "stable.bin",
        b"stable",
        media_type="application/octet-stream",
        lineage=LINEAGE,
        retention=RETENTION,
    )

    with pytest.raises(ArtifactConflictError):
        storage.write_bytes(
            "reviewed",
            "stable.bin",
            b"stable",
            media_type="application/octet-stream",
            lineage={"producing_run_id": "different"},
            retention=RETENTION,
        )
    assert storage.read_bytes("reviewed", "stable.bin") == b"stable"


def test_json_and_jsonl_are_canonical() -> None:
    assert canonical_json_bytes({"z": "é", "a": [2, 1]}) == ('{"a":[2,1],"z":"é"}\n'.encode())
    assert canonical_jsonl_bytes([{"b": 2, "a": 1}, {"x": True}]) == (
        b'{"a":1,"b":2}\n{"x":true}\n'
    )
    with pytest.raises(FormatError, match="non-finite"):
        canonical_json_bytes({"invalid": float("nan")})
    with pytest.raises(FormatError, match="non-string"):
        canonical_json_bytes({1: "invalid"})


def test_json_and_jsonl_writers_use_expected_media_types(storage: GuardedStorage) -> None:
    json_receipt = storage.write_json(
        "reviewed",
        "record.json",
        {"b": 2, "a": 1},
        lineage=LINEAGE,
        retention=RETENTION,
    )
    jsonl_receipt = storage.write_jsonl(
        "reviewed",
        "records.jsonl",
        [{"b": 2, "a": 1}, {"c": 3}],
        lineage=LINEAGE,
        retention=RETENTION,
    )
    assert storage.read_bytes("reviewed", json_receipt.relative_path) == b'{"a":1,"b":2}\n'
    assert storage.read_bytes("reviewed", jsonl_receipt.relative_path) == (
        b'{"a":1,"b":2}\n{"c":3}\n'
    )


def test_parquet_is_deterministic_and_reads_back(storage: GuardedStorage) -> None:
    rows = [
        {"player_id": "p-2", "score": 0.75},
        {"score": 0.5, "player_id": "p-1"},
    ]
    first = parquet_bytes(rows)
    second = parquet_bytes(rows)
    assert first == second
    assert read_parquet_bytes(first) == [
        {"player_id": "p-2", "score": 0.75},
        {"player_id": "p-1", "score": 0.5},
    ]

    receipt = storage.write_parquet(
        "reviewed",
        "candidates.parquet",
        rows,
        lineage=LINEAGE,
        retention=RETENTION,
    )
    assert read_parquet_bytes(storage.read_bytes("reviewed", receipt.relative_path)) == (
        read_parquet_bytes(first)
    )


def test_parquet_rejects_empty_or_inconsistent_rows() -> None:
    with pytest.raises(FormatError, match="at least one row"):
        parquet_bytes([])
    with pytest.raises(FormatError, match="same columns"):
        parquet_bytes([{"a": 1}, {"b": 2}])


def test_metadata_must_be_nonempty_and_json_compatible(storage: GuardedStorage) -> None:
    with pytest.raises(StorageConfigurationError, match="lineage"):
        storage.write_bytes(
            "reviewed",
            "invalid.bin",
            b"x",
            media_type="application/octet-stream",
            lineage={},
            retention=RETENTION,
        )
    with pytest.raises(FormatError, match="unsupported"):
        storage.write_bytes(
            "reviewed",
            "invalid.bin",
            b"x",
            media_type="application/octet-stream",
            lineage={"not_json": object()},
            retention=RETENTION,
        )

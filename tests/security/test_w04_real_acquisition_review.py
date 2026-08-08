"""Independent read-only verification of the ignored W04 Wyscout snapshot."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import stat
import zipfile
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, cast

import pytest

from scouting.sources import (
    WyscoutSourceConfig,
    acquire_wyscout_v5,
    load_wyscout_source_config,
)
from scouting.storage import GuardedStorage, canonical_json_bytes

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs/sources/w04-provider.yaml"
SNAPSHOT_ROOT = ROOT / "data/source/wyscout/v5"
WORKING_ROOT = ROOT / "data/working/wyscout/v5"
EXPECTED_MANIFEST_SHA256 = "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
SIGNED_DELIVERY_TOKENS = (
    b"X-Amz-",
    b"AWS4-HMAC-SHA256",
    b"X-Amz-Signature",
)
CHUNK_SIZE = 1024 * 1024
MAX_ARCHIVE_MEMBER_BYTES = 1024 * 1024 * 1024
MAX_ARCHIVE_BYTES = 4 * 1024 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200


@pytest.fixture(autouse=True)
def deny_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Turn any accidental socket use into an immediate test failure."""

    def denied_connection(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("real acquisition review must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", denied_connection)


def _required_snapshot_root() -> Path:
    if not SNAPSHOT_ROOT.exists():
        pytest.skip("ignored W04 real-acquisition snapshot is genuinely absent")
    assert SNAPSHOT_ROOT.is_dir()
    assert not SNAPSHOT_ROOT.is_symlink()
    return SNAPSHOT_ROOT


def _inventory(root: Path) -> dict[str, tuple[int, int, int, int]]:
    inventory: dict[str, tuple[int, int, int, int]] = {}
    for path in (root, *sorted(root.rglob("*"))):
        assert not path.is_symlink()
        status = path.stat()
        relative = "." if path == root else path.relative_to(root).as_posix()
        inventory[relative] = (
            stat.S_IFMT(status.st_mode),
            stat.S_IMODE(status.st_mode),
            status.st_size,
            status.st_mtime_ns,
        )
    return inventory


def _stream_evidence(stream: Any) -> tuple[int, str, str]:
    md5 = hashlib.md5(usedforsecurity=False)
    sha256 = hashlib.sha256()
    size = 0
    maximum_token_size = max(map(len, SIGNED_DELIVERY_TOKENS))
    tail = b""
    while chunk := stream.read(CHUNK_SIZE):
        assert isinstance(chunk, bytes)
        window = tail + chunk
        for token in SIGNED_DELIVERY_TOKENS:
            assert token not in window
        size += len(chunk)
        md5.update(chunk)
        sha256.update(chunk)
        tail = window[-(maximum_token_size - 1) :]
    return size, md5.hexdigest(), sha256.hexdigest()


def _path_evidence(path: Path) -> tuple[int, str, str]:
    assert path.is_file()
    assert not path.is_symlink()
    with path.open("rb") as stream:
        return _stream_evidence(stream)


def _load_canonical_document(path: Path) -> tuple[bytes, dict[str, Any]]:
    payload = path.read_bytes()
    for token in SIGNED_DELIVERY_TOKENS:
        assert token not in payload
    document = cast(dict[str, Any], json.loads(payload))
    assert canonical_json_bytes(document) == payload
    return payload, document


def _assert_sidecar(
    snapshot_root: Path,
    relative_path: str,
    *,
    payload_size: int,
    payload_sha256: str,
    media_type: str,
    lineage: dict[str, object],
    retention: dict[str, object],
) -> None:
    sidecar_path = snapshot_root / f"{relative_path}.manifest.json"
    _, sidecar = _load_canonical_document(sidecar_path)
    assert sidecar == {
        "lineage": lineage,
        "media_type": media_type,
        "payload": {
            "path": relative_path,
            "sha256": payload_sha256,
            "size_bytes": payload_size,
        },
        "retention": retention,
        "schema_version": 1,
        "state": "complete",
    }


def _expected_licence(config: WyscoutSourceConfig) -> dict[str, object]:
    return {
        "attribution_text": config.attribution_text,
        "change_notice": config.change_notice,
        "licence_id": config.licence_id,
        "licence_name": config.licence_name,
        "licence_url": config.licence_url,
    }


def _assert_archive_directory_member_is_safe(info: zipfile.ZipInfo) -> None:
    name = info.filename
    parsed = PurePosixPath(name)
    assert name
    assert "\\" not in name
    assert not parsed.is_absolute()
    assert all(part not in {"", ".", ".."} for part in name.split("/"))
    assert len(parsed.parts) == 1
    assert not info.is_dir()
    assert not info.flag_bits & 0x1
    file_type = stat.S_IFMT(info.external_attr >> 16)
    assert file_type in {0, stat.S_IFREG}
    assert 0 <= info.file_size <= MAX_ARCHIVE_MEMBER_BYTES
    if info.file_size:
        assert info.compress_size > 0
        assert info.file_size <= info.compress_size * MAX_COMPRESSION_RATIO


def test_real_snapshot_reconciles_every_durable_byte_and_replays_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshot_root = _required_snapshot_root()
    before_snapshot = _inventory(snapshot_root)
    before_working = _inventory(WORKING_ROOT) if WORKING_ROOT.exists() else None
    config = load_wyscout_source_config(CONFIG_PATH)
    completion_path = snapshot_root / "completion-manifest.json"
    manifest_bytes, completion = _load_canonical_document(completion_path)

    assert hashlib.sha256(manifest_bytes).hexdigest() == EXPECTED_MANIFEST_SHA256
    assert set(completion) == {
        "acquisition",
        "admitted_archive_members",
        "classification",
        "collection",
        "licence",
        "objects",
        "provider",
        "schema_version",
        "scope_excluded_archive_members",
        "source_id",
        "state",
    }
    assert completion["schema_version"] == 1
    assert completion["state"] == "complete"
    assert completion["source_id"] == config.source_id
    assert completion["provider"] == config.provider
    assert completion["classification"] == "wyscout_figshare_v5_cc_by_4"
    assert completion["collection"] == {
        "collection_doi": config.collection_doi,
        "collection_id": config.collection_id,
        "collection_published_at": "2020-01-28T14:24:27Z",
        "collection_version": config.collection_version,
    }
    assert completion["licence"] == _expected_licence(config)
    acquisition = cast(dict[str, object], completion["acquisition"])
    assert acquisition["source_available_at"] == "2020-01-28T14:24:27Z"
    assert (
        acquisition["source_available_at_basis"]
        == config.source_available_at_basis
        == "frozen_collection_release_time"
    )
    acquired_at = datetime.fromisoformat(
        cast(str, acquisition["acquired_at"]).replace("Z", "+00:00")
    )
    assert acquired_at > config.source_available_at

    object_records = cast(list[dict[str, Any]], completion["objects"])
    assert len(object_records) == len(config.objects) == 7
    expected_files = {
        "completion-manifest.json",
        "completion-manifest.json.manifest.json",
    }
    object_sha256: dict[str, str] = {}
    for source_object, record in zip(config.objects, object_records, strict=True):
        relative_path = f"objects/{source_object.name}"
        size, md5, sha256 = _path_evidence(snapshot_root / relative_path)
        assert record == {
            "article_doi": source_object.article_doi,
            "article_id": source_object.article_id,
            "computed_md5": md5,
            "expected_md5": source_object.expected_md5,
            "file_id": source_object.file_id,
            "name": source_object.name,
            "object_path": relative_path,
            "sha256": sha256,
            "size_bytes": size,
            "url": source_object.url,
        }
        assert size == source_object.size_bytes
        assert md5 == source_object.expected_md5
        assert "?" not in source_object.url
        object_sha256[source_object.name] = sha256
        _assert_sidecar(
            snapshot_root,
            relative_path,
            payload_size=size,
            payload_sha256=sha256,
            media_type=(
                "application/zip"
                if source_object.name.endswith(".zip")
                else "application/octet-stream"
            ),
            lineage={
                "collection_doi": config.collection_doi,
                "source_id": config.source_id,
                "source_url": source_object.url,
            },
            retention={
                "local_retention": "allowed",
                "raw_export": "forbidden",
            },
        )
        expected_files.update({relative_path, f"{relative_path}.manifest.json"})

    admitted_records = cast(
        list[dict[str, Any]],
        completion["admitted_archive_members"],
    )
    expected_admitted_pairs = [
        (archive_name, name)
        for archive_name in ("matches.zip", "events.zip")
        for name in config.archive_members_for(archive_name)
    ]
    assert [
        (record["archive_name"], record["name"]) for record in admitted_records
    ] == expected_admitted_pairs
    admitted_by_pair = {
        (cast(str, record["archive_name"]), cast(str, record["name"])): record
        for record in admitted_records
    }

    excluded_records = cast(
        list[dict[str, Any]],
        completion["scope_excluded_archive_members"],
    )
    expected_excluded_pairs = [
        (archive_name, name)
        for archive_name in ("matches.zip", "events.zip")
        for name in config.excluded_archive_members_for(archive_name)
    ]
    assert [
        (record["archive_name"], record["name"]) for record in excluded_records
    ] == expected_excluded_pairs
    excluded_by_pair = {
        (cast(str, record["archive_name"]), cast(str, record["name"])): record
        for record in excluded_records
    }

    for archive_name in ("matches.zip", "events.zip"):
        admitted_names = config.archive_members_for(archive_name)
        excluded_names = config.excluded_archive_members_for(archive_name)
        complete_names = admitted_names + excluded_names
        with zipfile.ZipFile(snapshot_root / f"objects/{archive_name}") as archive:
            infos = archive.infolist()
            assert len(infos) == len(complete_names) == 7
            assert len({info.filename for info in infos}) == len(infos)
            assert {info.filename for info in infos} == set(complete_names)
            assert sum(info.file_size for info in infos) <= MAX_ARCHIVE_BYTES
            by_name = {info.filename: info for info in infos}
            for info in infos:
                _assert_archive_directory_member_is_safe(info)

            for name in admitted_names:
                info = by_name[name]
                with archive.open(info, "r") as member_stream:
                    archive_size, _, archive_sha256 = _stream_evidence(member_stream)
                relative_path = f"archive-members/{name}"
                durable_size, _, durable_sha256 = _path_evidence(snapshot_root / relative_path)
                record = admitted_by_pair[(archive_name, name)]
                assert record == {
                    "archive_name": archive_name,
                    "member_path": relative_path,
                    "name": name,
                    "sha256": durable_sha256,
                    "size_bytes": durable_size,
                }
                assert (archive_size, archive_sha256) == (
                    durable_size,
                    durable_sha256,
                )
                _assert_sidecar(
                    snapshot_root,
                    relative_path,
                    payload_size=durable_size,
                    payload_sha256=durable_sha256,
                    media_type="application/json",
                    lineage={
                        "archive_name": archive_name,
                        "archive_sha256": object_sha256[archive_name],
                        "collection_doi": config.collection_doi,
                        "source_id": config.source_id,
                    },
                    retention={
                        "local_retention": "allowed",
                        "raw_export": "forbidden",
                    },
                )
                expected_files.update({relative_path, f"{relative_path}.manifest.json"})

            for name in excluded_names:
                info = by_name[name]
                assert excluded_by_pair[(archive_name, name)] == {
                    "archive_name": archive_name,
                    "compressed_size_bytes": info.compress_size,
                    "declared_size_bytes": info.file_size,
                    "directory_crc32": f"{info.CRC:08x}",
                    "disposition": ("directory_verified_payload_not_opened_or_admitted"),
                    "name": name,
                }
                assert not (snapshot_root / f"archive-members/{name}").exists()
                assert not (snapshot_root / f"archive-members/{name}.manifest.json").exists()

    _assert_sidecar(
        snapshot_root,
        "completion-manifest.json",
        payload_size=len(manifest_bytes),
        payload_sha256=EXPECTED_MANIFEST_SHA256,
        media_type="application/json",
        lineage={
            "collection_doi": config.collection_doi,
            "source_id": config.source_id,
        },
        retention={"immutable": True, "raw_export": "forbidden"},
    )
    actual_files = {
        path.relative_to(snapshot_root).as_posix()
        for path in snapshot_root.rglob("*")
        if path.is_file()
    }
    assert actual_files == expected_files
    assert all(
        details[1] == (0o700 if details[0] == stat.S_IFDIR else 0o600)
        for details in before_snapshot.values()
    )

    reads: list[str] = []
    streamed_objects: list[str] = []
    opened_archive_members: list[str] = []
    network_calls: list[tuple[str, float]] = []
    original_read = GuardedStorage.read_bytes
    original_open_binary = GuardedStorage.open_binary
    original_archive_open = zipfile.ZipFile.open

    def recording_read(
        storage: GuardedStorage,
        root_name: str,
        relative_path: str | os.PathLike[str],
    ) -> bytes:
        reads.append(os.fspath(relative_path))
        return original_read(storage, root_name, relative_path)

    def denied_write(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("exact replay attempted to write durable data")

    def recording_open_binary(
        storage: GuardedStorage,
        root_name: str,
        relative_path: str | os.PathLike[str],
    ) -> AbstractContextManager[BinaryIO]:
        streamed_objects.append(os.fspath(relative_path))
        return original_open_binary(storage, root_name, relative_path)

    def recording_archive_open(
        archive: zipfile.ZipFile,
        name: str | zipfile.ZipInfo,
        mode: str = "r",
        pwd: bytes | None = None,
        *,
        force_zip64: bool = False,
    ) -> Any:
        opened_archive_members.append(name.filename if isinstance(name, zipfile.ZipInfo) else name)
        return original_archive_open(
            archive,
            name,
            mode,
            pwd,
            force_zip64=force_zip64,
        )

    def denied_opener(url: str, timeout_seconds: float) -> Any:
        network_calls.append((url, timeout_seconds))
        raise AssertionError("exact replay attempted a provider call")

    monkeypatch.setattr(GuardedStorage, "read_bytes", recording_read)
    monkeypatch.setattr(GuardedStorage, "open_binary", recording_open_binary)
    monkeypatch.setattr(GuardedStorage, "write_bytes", denied_write)
    monkeypatch.setattr(zipfile.ZipFile, "open", recording_archive_open)
    replay = acquire_wyscout_v5(
        config,
        destination_root=snapshot_root,
        working_root=WORKING_ROOT,
        acquired_at=acquired_at,
        opener=denied_opener,
    )

    expected_reads = [
        "completion-manifest.json",
        *(
            f"archive-members/{name}"
            for archive_name in ("matches.zip", "events.zip")
            for name in config.archive_members_for(archive_name)
        ),
    ]
    assert reads == expected_reads
    assert streamed_objects == [f"objects/{source_object.name}" for source_object in config.objects]
    assert opened_archive_members == [
        name
        for archive_name in ("matches.zip", "events.zip")
        for name in config.archive_members_for(archive_name)
    ]
    assert set(opened_archive_members).isdisjoint(
        name
        for archive_name in ("matches.zip", "events.zip")
        for name in config.excluded_archive_members_for(archive_name)
    )
    assert network_calls == []
    assert replay.manifest_relative_path == "completion-manifest.json"
    assert replay.manifest_bytes == manifest_bytes
    assert replay.manifest_sha256 == EXPECTED_MANIFEST_SHA256
    assert not replay.manifest_created
    assert _inventory(snapshot_root) == before_snapshot
    assert (_inventory(WORKING_ROOT) if WORKING_ROOT.exists() else None) == before_working

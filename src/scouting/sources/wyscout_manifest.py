"""Strict bridge from frozen Wyscout completion evidence to one source manifest."""

from __future__ import annotations

import argparse
import csv
import errno
import hashlib
import io
import json
import os
import stat
import sys
import uuid
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import ValidationError

from scouting.contracts.evidence import (
    CoverageDimension,
    DataCoverage,
    LicenceUseClass,
    SourceFileDigest,
    SourceSnapshotManifest,
    SourceUseClassification,
)
from scouting.contracts.primitives import TenantContext
from scouting.storage.formats import canonical_json_bytes

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SOURCE_ROOT_RELATIVE = Path("data/source/wyscout/v5")
_MANIFEST_ROOT_RELATIVE = Path("data/manifests")
_SOURCE_ROOT = _PROJECT_ROOT / _SOURCE_ROOT_RELATIVE
_MANIFEST_ROOT = _PROJECT_ROOT / _MANIFEST_ROOT_RELATIVE

_SOURCE_ID = "wyscout-soccer-match-events-figshare-v5"
_PROVIDER = "Wyscout"
_PROVIDER_SCHEMA_VERSION = "figshare-v5+completion-v1+bridge-v1"
_BRIDGE_VERSION = "w04-wyscout-manifest-bridge-v1"
_COMPLETION_SHA256 = "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
_TENANT_ID = UUID("65a43912-d412-5ff9-a364-7f84d1ad6c5d")
_MANIFEST_ID = UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b")
_TRACE_ID = UUID("2c441714-d968-5495-8339-c85ecaf5f596")
_ACQUIRED_AT = datetime(2026, 7, 29, 15, 51, 8, 598589, tzinfo=UTC)
_AVAILABLE_AT = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
_ATTRIBUTION_TEXT = (
    "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
    "Wyscout, figshare collection v5, licensed CC BY 4.0."
)
_MANIFEST_RELATIVE_PATH = PurePosixPath(
    "wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json"
)
_CHUNK_SIZE = 1024 * 1024
_DIRECTORY_MODE = 0o700
_FILE_MODE = 0o600
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_DIRECTORY = getattr(os, "O_DIRECTORY", 0)


class WyscoutSourceManifestError(RuntimeError):
    """Base failure for frozen evidence, contract, or immutable materialization."""


class WyscoutSourceManifestPathError(WyscoutSourceManifestError):
    """Raised when a requested or admitted path is not the exact safe local path."""


class WyscoutSourceManifestConflictError(WyscoutSourceManifestError):
    """Raised when immutable manifest bytes already exist with different content."""


@dataclass(frozen=True, slots=True)
class SourceEvidenceSpec:
    """One exact R20 physical source-evidence row."""

    object_path: str
    size_bytes: int
    row_count: int | None
    sha256: str
    row_format: str | None = None
    csv_header: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class SourceEvidenceMeasurement:
    """One bounded physical measurement of an exact source-evidence row."""

    object_path: str
    size_bytes: int
    row_count: int | None
    sha256: str
    payload: bytes | None = None


@dataclass(frozen=True, slots=True)
class SourceManifestMaterialization:
    """Result of writing or confirming the sole immutable source manifest."""

    manifest: SourceSnapshotManifest
    relative_path: str
    sha256: str
    size_bytes: int
    created: bool


_SOURCE_EVIDENCE = (
    SourceEvidenceSpec(
        "completion-manifest.json",
        6_803,
        None,
        _COMPLETION_SHA256,
    ),
    SourceEvidenceSpec(
        "objects/competitions.json",
        1_209,
        7,
        "39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1",
        "json-array",
    ),
    SourceEvidenceSpec(
        "objects/teams.json",
        27_404,
        142,
        "9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d",
        "json-array",
    ),
    SourceEvidenceSpec(
        "objects/players.json",
        1_737_347,
        3_603,
        "877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e",
        "json-array",
    ),
    SourceEvidenceSpec(
        "objects/matches.zip",
        645_097,
        None,
        "c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9",
    ),
    SourceEvidenceSpec(
        "objects/events.zip",
        77_323_413,
        None,
        "877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45",
    ),
    SourceEvidenceSpec(
        "objects/eventid2name.csv",
        1_001,
        36,
        "ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842",
        "csv",
        ("event", "subevent", "event_label", "subevent_label"),
    ),
    SourceEvidenceSpec(
        "objects/tags2name.csv",
        1_754,
        59,
        "e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922",
        "csv",
        ("Tag", "Label", "Description"),
    ),
    SourceEvidenceSpec(
        "archive-members/matches_England.json",
        1_694_720,
        380,
        "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/matches_France.json",
        1_707_222,
        380,
        "851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/matches_Germany.json",
        1_377_328,
        306,
        "6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/matches_Italy.json",
        2_019_196,
        380,
        "afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/matches_Spain.json",
        1_705_380,
        380,
        "9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/events_England.json",
        188_888_614,
        643_150,
        "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/events_France.json",
        186_374_196,
        632_807,
        "18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/events_Germany.json",
        152_916_631,
        519_407,
        "2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/events_Italy.json",
        190_544_685,
        647_372,
        "b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84",
        "json-array",
    ),
    SourceEvidenceSpec(
        "archive-members/events_Spain.json",
        184_164_406,
        628_659,
        "b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154",
        "json-array",
    ),
)

_EXPECTED_OBJECT_COMPLETION_ROWS = (
    (
        "competitions.json",
        7_765_316,
        "10.6084/m9.figshare.7765316.v4",
        15_073_685,
        "3dc210a4805dda5337b0ff9f7eaa407a",
    ),
    (
        "teams.json",
        7_765_310,
        "10.6084/m9.figshare.7765310.v3",
        15_073_697,
        "1381ff9449f21105090729cf0e086b5b",
    ),
    (
        "players.json",
        7_765_196,
        "10.6084/m9.figshare.7765196.v3",
        15_073_721,
        "f28ddf6326281efeda6488b2169f5609",
    ),
    (
        "matches.zip",
        7_770_422,
        "10.6084/m9.figshare.7770422.v1",
        14_464_622,
        "51d80beb17480919f69a53a0152c2d71",
    ),
    (
        "events.zip",
        7_770_599,
        "10.6084/m9.figshare.7770599.v1",
        14_464_685,
        "7c20e8647e7eda58d7838a0c7b1ec6ab",
    ),
    (
        "eventid2name.csv",
        11_743_836,
        "10.6084/m9.figshare.11743836.v1",
        21_385_245,
        "46daf16100ece0c743eedc9adcfea162",
    ),
    (
        "tags2name.csv",
        11_743_818,
        "10.6084/m9.figshare.11743818.v1",
        21_385_239,
        "e7acb14918d00e40c80a898b1da8fc39",
    ),
)

_EXPECTED_EXCLUDED_ROWS = (
    {
        "archive_name": "matches.zip",
        "compressed_size_bytes": 19_805,
        "declared_size_bytes": 312_151,
        "directory_crc32": "9e64a3d4",
        "disposition": "directory_verified_payload_not_opened_or_admitted",
        "name": "matches_European_Championship.json",
    },
    {
        "archive_name": "matches.zip",
        "compressed_size_bytes": 25_498,
        "declared_size_bytes": 395_677,
        "directory_crc32": "649719a9",
        "disposition": "directory_verified_payload_not_opened_or_admitted",
        "name": "matches_World_Cup.json",
    },
    {
        "archive_name": "events.zip",
        "compressed_size_bytes": 1_869_471,
        "declared_size_bytes": 22_954_338,
        "directory_crc32": "13c071be",
        "disposition": "directory_verified_payload_not_opened_or_admitted",
        "name": "events_European_Championship.json",
    },
    {
        "archive_name": "events.zip",
        "compressed_size_bytes": 2_440_430,
        "declared_size_bytes": 29_981_214,
        "directory_crc32": "053e0ae8",
        "disposition": "directory_verified_payload_not_opened_or_admitted",
        "name": "events_World_Cup.json",
    },
)


class _JsonArrayObjectCounter:
    """Count top-level object rows in one pinned JSON array without loading it."""

    def __init__(self) -> None:
        self._stack: list[int] = []
        self._in_string = False
        self._escaped = False
        self._started = False
        self._finished = False
        self._top_state = "first-or-end"
        self._row_count = 0

    def feed(self, chunk: bytes) -> None:
        for byte in chunk:
            if self._finished:
                if byte not in b" \t\r\n":
                    raise WyscoutSourceManifestError("JSON array has trailing content")
                continue
            if self._in_string:
                if self._escaped:
                    self._escaped = False
                elif byte == ord("\\"):
                    self._escaped = True
                elif byte == ord('"'):
                    self._in_string = False
                elif byte < 0x20:
                    raise WyscoutSourceManifestError("JSON string contains a control byte")
                continue
            if not self._started:
                if byte in b" \t\r\n":
                    continue
                if byte != ord("["):
                    raise WyscoutSourceManifestError("source JSON must be one top-level array")
                self._started = True
                self._stack.append(byte)
                continue
            if len(self._stack) == 1:
                if byte in b" \t\r\n":
                    continue
                if self._top_state in {"first-or-end", "item-required"}:
                    if byte == ord("]") and self._top_state == "first-or-end":
                        self._stack.pop()
                        self._finished = True
                    elif byte == ord("{"):
                        self._stack.append(byte)
                        self._row_count += 1
                    else:
                        raise WyscoutSourceManifestError(
                            "source JSON array rows must be top-level objects"
                        )
                    continue
                if self._top_state == "comma-or-end":
                    if byte == ord(","):
                        self._top_state = "item-required"
                    elif byte == ord("]"):
                        self._stack.pop()
                        self._finished = True
                    else:
                        raise WyscoutSourceManifestError("source JSON row separator is invalid")
                    continue
            if byte == ord('"'):
                self._in_string = True
            elif byte in {ord("["), ord("{")}:
                self._stack.append(byte)
            elif byte in {ord("]"), ord("}")}:
                expected = ord("[") if byte == ord("]") else ord("{")
                if not self._stack or self._stack[-1] != expected:
                    raise WyscoutSourceManifestError("source JSON nesting is invalid")
                self._stack.pop()
                if len(self._stack) == 1:
                    self._top_state = "comma-or-end"

    def finish(self) -> int:
        if (
            not self._started
            or not self._finished
            or self._stack
            or self._in_string
            or self._escaped
        ):
            raise WyscoutSourceManifestError("source JSON array is incomplete")
        return self._row_count


def _exact_root_argument(path: Path, *, relative: Path, context: str) -> Path:
    expected = _PROJECT_ROOT / relative
    if path.is_absolute():
        accepted = path == expected
    else:
        accepted = path == relative and Path.cwd() == _PROJECT_ROOT
    if not accepted:
        raise WyscoutSourceManifestPathError(f"{context} must be exactly {relative.as_posix()}")
    return expected


def _normal_relative_parts(relative_path: str) -> tuple[str, ...]:
    parsed = PurePosixPath(relative_path)
    parts = tuple(relative_path.split("/"))
    if (
        parsed.is_absolute()
        or not parts
        or any(part in {"", ".", ".."} for part in parts)
        or "\\" in relative_path
        or "\x00" in relative_path
    ):
        raise WyscoutSourceManifestPathError("source evidence path is not a normal POSIX path")
    return parts


@contextmanager
def _open_regular_beneath(root: Path, relative_path: str) -> Iterator[int]:
    parts = _normal_relative_parts(relative_path)
    descriptors: list[int] = []
    try:
        current = os.open(root, os.O_RDONLY | _DIRECTORY | _NOFOLLOW)
        descriptors.append(current)
        for directory in parts[:-1]:
            child = os.open(
                directory,
                os.O_RDONLY | _DIRECTORY | _NOFOLLOW,
                dir_fd=current,
            )
            metadata = os.fstat(child)
            if not stat.S_ISDIR(metadata.st_mode):
                raise WyscoutSourceManifestPathError(
                    f"source path component is not a directory: {directory}"
                )
            descriptors.append(child)
            current = child
        file_descriptor = os.open(parts[-1], os.O_RDONLY | _NOFOLLOW, dir_fd=current)
        descriptors.append(file_descriptor)
        metadata = os.fstat(file_descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise WyscoutSourceManifestPathError(
                f"source evidence is not a regular file: {relative_path}"
            )
        yield file_descriptor
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise WyscoutSourceManifestPathError(
                f"source evidence path contains a link or non-directory: {relative_path}"
            ) from exc
        raise
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _count_csv_rows(payload: bytes, spec: SourceEvidenceSpec) -> int:
    try:
        decoded = payload.decode("utf-8", errors="strict")
        rows = list(csv.reader(io.StringIO(decoded, newline=""), strict=True))
    except (UnicodeError, csv.Error) as exc:
        raise WyscoutSourceManifestError(f"CSV source is invalid: {spec.object_path}") from exc
    if not rows or tuple(rows[0]) != spec.csv_header:
        raise WyscoutSourceManifestError(f"CSV header conflicts: {spec.object_path}")
    if any(len(row) != len(rows[0]) for row in rows[1:]):
        raise WyscoutSourceManifestError(f"CSV row width conflicts: {spec.object_path}")
    return len(rows) - 1


def _measure_source_file(root: Path, spec: SourceEvidenceSpec) -> SourceEvidenceMeasurement:
    collect_payload = spec.object_path == "completion-manifest.json" or spec.row_format == "csv"
    chunks: list[bytes] | None = [] if collect_payload else None
    counter = _JsonArrayObjectCounter() if spec.row_format == "json-array" else None
    digest = hashlib.sha256()
    size_bytes = 0
    with _open_regular_beneath(root, spec.object_path) as descriptor:
        before = os.fstat(descriptor)
        while chunk := os.read(descriptor, _CHUNK_SIZE):
            size_bytes += len(chunk)
            if size_bytes > spec.size_bytes:
                raise WyscoutSourceManifestError(
                    f"source size exceeds authority: {spec.object_path}"
                )
            digest.update(chunk)
            if chunks is not None:
                chunks.append(chunk)
            if counter is not None:
                counter.feed(chunk)
        after = os.fstat(descriptor)
    stable_fields = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
        raise WyscoutSourceManifestError(f"source changed during read: {spec.object_path}")
    payload = b"".join(chunks) if chunks is not None else None
    if counter is not None:
        row_count = counter.finish()
    elif spec.row_format == "csv":
        if payload is None:
            raise AssertionError("CSV payload collection is unavailable")
        row_count = _count_csv_rows(payload, spec)
    else:
        row_count = None
    return SourceEvidenceMeasurement(
        object_path=spec.object_path,
        size_bytes=size_bytes,
        row_count=row_count,
        sha256=digest.hexdigest(),
        payload=payload,
    )


def _validate_measurements(
    measurements: Sequence[SourceEvidenceMeasurement],
) -> tuple[SourceEvidenceMeasurement, ...]:
    materialised = tuple(measurements)
    if len(materialised) != len(_SOURCE_EVIDENCE):
        raise WyscoutSourceManifestError("source evidence cardinality must be exactly 18")
    for index, (spec, measured) in enumerate(zip(_SOURCE_EVIDENCE, materialised, strict=True)):
        expected = (spec.object_path, spec.size_bytes, spec.row_count, spec.sha256)
        actual = (
            measured.object_path,
            measured.size_bytes,
            measured.row_count,
            measured.sha256,
        )
        if actual != expected:
            raise WyscoutSourceManifestError(
                f"source evidence row {index + 1} conflicts: {spec.object_path}"
            )
    return materialised


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise WyscoutSourceManifestError(f"completion manifest repeats key {key!r}")
        result[key] = value
    return result


def _decode_completion_manifest(payload: bytes) -> dict[str, object]:
    try:
        decoded = json.loads(payload, object_pairs_hook=_reject_duplicate_json_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutSourceManifestError("completion manifest is invalid JSON") from exc
    if type(decoded) is not dict:
        raise WyscoutSourceManifestError("completion manifest must be one JSON object")
    document = cast(dict[str, object], decoded)
    if canonical_json_bytes(document) != payload:
        raise WyscoutSourceManifestError("completion manifest bytes are not canonical")
    return document


def _validate_completion_document(document: dict[str, object]) -> None:
    expected_top = {
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
    if set(document) != expected_top:
        raise WyscoutSourceManifestError("completion manifest top-level keys conflict")
    if (
        document["schema_version"] != 1
        or document["state"] != "complete"
        or document["source_id"] != _SOURCE_ID
        or document["provider"] != _PROVIDER
        or document["classification"] != "wyscout_figshare_v5_cc_by_4"
    ):
        raise WyscoutSourceManifestError("completion manifest identity conflicts")
    if document["acquisition"] != {
        "acquired_at": "2026-07-29T15:51:08.598589Z",
        "source_available_at": "2020-01-28T14:24:27Z",
        "source_available_at_basis": "frozen_collection_release_time",
    }:
        raise WyscoutSourceManifestError("completion manifest clocks conflict")
    if document["collection"] != {
        "collection_doi": "10.6084/m9.figshare.c.4415000.v5",
        "collection_id": 4_415_000,
        "collection_published_at": "2020-01-28T14:24:27Z",
        "collection_version": 5,
    }:
        raise WyscoutSourceManifestError("completion collection authority conflicts")
    if document["licence"] != {
        "attribution_text": _ATTRIBUTION_TEXT,
        "change_notice": (
            "This project normalises source JSON, reconstructs lineup stints and "
            "possessions, and derives player-window aggregates."
        ),
        "licence_id": "CC-BY-4.0",
        "licence_name": "Creative Commons Attribution 4.0 International",
        "licence_url": "https://creativecommons.org/licenses/by/4.0/",
    }:
        raise WyscoutSourceManifestError("completion rights authority conflicts")

    raw_objects = document["objects"]
    if type(raw_objects) is not list or len(raw_objects) != 7:
        raise WyscoutSourceManifestError("completion object rows must be exactly seven")
    evidence_by_path = {spec.object_path: spec for spec in _SOURCE_EVIDENCE}
    expected_object_rows: list[dict[str, object]] = []
    for name, article_id, article_doi, file_id, md5 in _EXPECTED_OBJECT_COMPLETION_ROWS:
        spec = evidence_by_path[f"objects/{name}"]
        expected_object_rows.append(
            {
                "article_doi": article_doi,
                "article_id": article_id,
                "computed_md5": md5,
                "expected_md5": md5,
                "file_id": file_id,
                "name": name,
                "object_path": spec.object_path,
                "sha256": spec.sha256,
                "size_bytes": spec.size_bytes,
                "url": f"https://ndownloader.figshare.com/files/{file_id}",
            }
        )
    if raw_objects != expected_object_rows:
        raise WyscoutSourceManifestError("completion object evidence conflicts")

    raw_members = document["admitted_archive_members"]
    member_specs = _SOURCE_EVIDENCE[8:]
    expected_members = [
        {
            "archive_name": "matches.zip" if "/matches_" in spec.object_path else "events.zip",
            "member_path": spec.object_path,
            "name": PurePosixPath(spec.object_path).name,
            "sha256": spec.sha256,
            "size_bytes": spec.size_bytes,
        }
        for spec in member_specs
    ]
    if raw_members != expected_members:
        raise WyscoutSourceManifestError("completion admitted-member evidence conflicts")
    if document["scope_excluded_archive_members"] != list(_EXPECTED_EXCLUDED_ROWS):
        raise WyscoutSourceManifestError("completion scope-exclusion evidence conflicts")


def _manifest_identity(tenant_id: UUID, club_id: UUID | None) -> tuple[UUID, UUID]:
    identity_input = canonical_json_bytes(
        {
            "bridge_version": _BRIDGE_VERSION,
            "club_id": str(club_id) if club_id is not None else None,
            "completion_sha256": _COMPLETION_SHA256,
            "source_id": _SOURCE_ID,
            "tenant_id": str(tenant_id),
        }
    )
    namespace = uuid5(
        NAMESPACE_URL,
        "urn:scouting-intelligence:source-snapshot-manifest:wyscout:v1",
    )
    manifest_id = uuid5(namespace, hashlib.sha256(identity_input).hexdigest())
    return manifest_id, uuid5(manifest_id, "semantic-manifest-trace:w04-wyscout:v1")


def _source_coverage() -> DataCoverage:
    counts = (
        ("source_object_integrity", 7),
        ("admitted_member_integrity", 10),
        ("match_partition_presence", 5),
        ("event_partition_presence", 5),
        ("partition_match_id_alignment", 5),
        ("scope_exclusion_directory_only", 4),
    )
    return DataCoverage(
        overall=1.0,
        dimensions=tuple(
            CoverageDimension(
                name=name,
                coverage=1.0,
                observed_count=count,
                expected_count=count,
            )
            for name, count in counts
        ),
        missing_dimensions=(),
    )


def build_source_snapshot_manifest(
    *,
    source_root: Path,
    tenant_id: UUID,
    club_id: UUID | None = None,
) -> SourceSnapshotManifest:
    """Validate the exact frozen source and construct its strict contract manifest."""

    root = _exact_root_argument(
        source_root,
        relative=_SOURCE_ROOT_RELATIVE,
        context="source root",
    )
    if tenant_id != _TENANT_ID or club_id is not None:
        raise WyscoutSourceManifestError("tenant context is not the fixed local POC context")
    manifest_id, trace_id = _manifest_identity(tenant_id, club_id)
    if manifest_id != _MANIFEST_ID or trace_id != _TRACE_ID:
        raise WyscoutSourceManifestError("source manifest UUIDv5 derivation conflicts")

    measurements = _validate_measurements(
        tuple(_measure_source_file(root, spec) for spec in _SOURCE_EVIDENCE)
    )
    completion = measurements[0]
    if completion.payload is None or completion.sha256 != _COMPLETION_SHA256:
        raise WyscoutSourceManifestError("completion manifest bytes are unavailable")
    document = _decode_completion_manifest(completion.payload)
    _validate_completion_document(document)

    manifest = SourceSnapshotManifest(
        manifest_id=manifest_id,
        tenant_context=TenantContext(tenant_id=tenant_id, club_id=club_id),
        trace_id=trace_id,
        provider=_PROVIDER,
        provider_schema_version=_PROVIDER_SCHEMA_VERSION,
        classification=SourceUseClassification(
            use_class=LicenceUseClass.RESTRICTED,
            derived_data_allowed=True,
            internal_review_allowed=True,
            export_allowed=False,
            attribution_required=True,
            attribution_text=_ATTRIBUTION_TEXT,
        ),
        acquired_at=_ACQUIRED_AT,
        available_at=_AVAILABLE_AT,
        files=tuple(
            SourceFileDigest(
                object_path=measurement.object_path,
                sha256=measurement.sha256,
                size_bytes=measurement.size_bytes,
                row_count=measurement.row_count,
            )
            for measurement in measurements
        ),
        coverage=_source_coverage(),
    )
    payload = canonical_json_bytes(manifest.model_dump(mode="json"))
    try:
        restored = SourceSnapshotManifest.model_validate_json(payload)
    except ValidationError as exc:
        raise WyscoutSourceManifestError("source manifest contract round-trip failed") from exc
    if restored != manifest or canonical_json_bytes(restored.model_dump(mode="json")) != payload:
        raise WyscoutSourceManifestError("source manifest canonical round-trip drifted")
    return manifest


@contextmanager
def _created_parent_descriptor(root: Path, directories: tuple[str, ...]) -> Iterator[int]:
    descriptors: list[int] = []
    try:
        current = os.open(root, os.O_RDONLY | _DIRECTORY | _NOFOLLOW)
        descriptors.append(current)
        for directory in directories:
            try:
                os.mkdir(directory, _DIRECTORY_MODE, dir_fd=current)
                os.fsync(current)
            except FileExistsError:
                pass
            child = os.open(
                directory,
                os.O_RDONLY | _DIRECTORY | _NOFOLLOW,
                dir_fd=current,
            )
            metadata = os.fstat(child)
            if not stat.S_ISDIR(metadata.st_mode):
                raise WyscoutSourceManifestPathError(
                    f"manifest path component is not a directory: {directory}"
                )
            descriptors.append(child)
            current = child
        yield current
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise WyscoutSourceManifestPathError(
                "manifest path contains a link or non-directory"
            ) from exc
        raise
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _read_immutable(parent_descriptor: int, filename: str) -> tuple[bytes, os.stat_result] | None:
    try:
        descriptor = os.open(filename, os.O_RDONLY | _NOFOLLOW, dir_fd=parent_descriptor)
    except FileNotFoundError:
        return None
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise WyscoutSourceManifestPathError("manifest target is not a regular file") from exc
        raise
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != _FILE_MODE:
            raise WyscoutSourceManifestPathError("manifest target mode or type is unsafe")
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, _CHUNK_SIZE):
            chunks.append(chunk)
        return b"".join(chunks), metadata
    finally:
        os.close(descriptor)


def _write_all(descriptor: int, payload: bytes) -> None:
    remaining = memoryview(payload)
    while remaining:
        written = os.write(descriptor, remaining)
        if written <= 0:
            raise OSError("immutable manifest write made no progress")
        remaining = remaining[written:]


def _persist_immutable_file(parent_descriptor: int, filename: str, payload: bytes) -> bool:
    existing = _read_immutable(parent_descriptor, filename)
    if existing is not None:
        if existing[0] != payload:
            raise WyscoutSourceManifestConflictError("immutable source manifest bytes conflict")
        return False

    temporary_name = f".{filename}.{uuid.uuid4().hex}.partial"
    temporary_descriptor: int | None = None
    temporary_exists = False
    try:
        temporary_descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW,
            _FILE_MODE,
            dir_fd=parent_descriptor,
        )
        temporary_exists = True
        _write_all(temporary_descriptor, payload)
        os.fsync(temporary_descriptor)
        os.close(temporary_descriptor)
        temporary_descriptor = None
        try:
            os.link(
                temporary_name,
                filename,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except FileExistsError:
            raced = _read_immutable(parent_descriptor, filename)
            if raced is None or raced[0] != payload:
                raise WyscoutSourceManifestConflictError(
                    "immutable source manifest bytes conflict"
                ) from None
            return False
        return True
    finally:
        if temporary_descriptor is not None:
            os.close(temporary_descriptor)
        if temporary_exists:
            try:
                os.unlink(temporary_name, dir_fd=parent_descriptor)
            except FileNotFoundError:
                pass
        os.fsync(parent_descriptor)


def materialize_source_snapshot_manifest(
    *,
    manifest_root: Path,
    manifest: SourceSnapshotManifest,
) -> SourceManifestMaterialization:
    """Write or confirm canonical bytes at the sole content-addressed path."""

    root = _exact_root_argument(
        manifest_root,
        relative=_MANIFEST_ROOT_RELATIVE,
        context="manifest root",
    )
    if manifest.manifest_id != _MANIFEST_ID or manifest.trace_id != _TRACE_ID:
        raise WyscoutSourceManifestError("manifest identity is not the frozen bridge identity")
    payload = canonical_json_bytes(manifest.model_dump(mode="json"))
    try:
        restored = SourceSnapshotManifest.model_validate_json(payload)
    except ValidationError as exc:
        raise WyscoutSourceManifestError("manifest payload violates the source contract") from exc
    if restored != manifest:
        raise WyscoutSourceManifestError("manifest payload does not round-trip")

    root.parent.mkdir(mode=_DIRECTORY_MODE, parents=True, exist_ok=True)
    if root.parent.is_symlink():
        raise WyscoutSourceManifestPathError("data root cannot be a link")
    relative_parts = tuple(_MANIFEST_RELATIVE_PATH.parts)
    with _created_parent_descriptor(root.parent, (root.name, *relative_parts[:-1])) as parent:
        created = _persist_immutable_file(parent, relative_parts[-1], payload)
        readback = _read_immutable(parent, relative_parts[-1])
    if readback is None or readback[0] != payload:
        raise WyscoutSourceManifestError("immutable source manifest readback failed")
    digest = hashlib.sha256(payload).hexdigest()
    return SourceManifestMaterialization(
        manifest=manifest,
        relative_path=(
            _MANIFEST_ROOT_RELATIVE / Path(_MANIFEST_RELATIVE_PATH.as_posix())
        ).as_posix(),
        sha256=digest,
        size_bytes=len(payload),
        created=created,
    )


def _canonical_uuid(value: str, *, context: str) -> UUID:
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise WyscoutSourceManifestError(f"{context} must be a canonical UUID") from exc
    if str(parsed) != value:
        raise WyscoutSourceManifestError(f"{context} must be a canonical UUID")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--manifest-root", required=True, type=Path)
    parser.add_argument("--tenant-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate and materialize the fixed local manifest without provider access."""

    arguments = _parser().parse_args(argv)
    try:
        tenant_id = _canonical_uuid(arguments.tenant_id, context="tenant-id")
        manifest = build_source_snapshot_manifest(
            source_root=arguments.source_root,
            tenant_id=tenant_id,
        )
        result = materialize_source_snapshot_manifest(
            manifest_root=arguments.manifest_root,
            manifest=manifest,
        )
    except (OSError, WyscoutSourceManifestError) as exc:
        print(f"W04 Wyscout source manifest failed: {exc}", file=sys.stderr)
        return 1
    state = "created" if result.created else "confirmed"
    print(
        f"W04 Wyscout source manifest {state}: {result.relative_path} "
        f"sha256={result.sha256} size_bytes={result.size_bytes}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SourceManifestMaterialization",
    "WyscoutSourceManifestConflictError",
    "WyscoutSourceManifestError",
    "WyscoutSourceManifestPathError",
    "build_source_snapshot_manifest",
    "main",
    "materialize_source_snapshot_manifest",
]

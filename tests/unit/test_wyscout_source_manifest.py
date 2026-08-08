"""Focused acceptance tests for the strict W04 Wyscout source-manifest bridge."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest

from scouting.contracts.evidence import LicenceUseClass, SourceSnapshotManifest
from scouting.sources import wyscout_manifest as bridge
from scouting.storage.formats import canonical_json_bytes

TENANT_ID = UUID("65a43912-d412-5ff9-a364-7f84d1ad6c5d")
MANIFEST_ID = UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b")
TRACE_ID = UUID("2c441714-d968-5495-8339-c85ecaf5f596")


@pytest.fixture(scope="module")
def frozen_manifest() -> SourceSnapshotManifest:
    return bridge.build_source_snapshot_manifest(
        source_root=Path("data/source/wyscout/v5"),
        tenant_id=TENANT_ID,
    )


def test_exact_frozen_source_builds_fixed_manifest_identity(
    frozen_manifest: SourceSnapshotManifest,
) -> None:
    assert frozen_manifest.manifest_id == MANIFEST_ID
    assert frozen_manifest.trace_id == TRACE_ID
    assert frozen_manifest.tenant_context.tenant_id == TENANT_ID
    assert frozen_manifest.tenant_context.club_id is None
    assert frozen_manifest.provider == "Wyscout"
    assert frozen_manifest.provider_schema_version == "figshare-v5+completion-v1+bridge-v1"
    assert frozen_manifest.acquired_at.isoformat() == "2026-07-29T15:51:08.598589+00:00"
    assert frozen_manifest.available_at.isoformat() == "2020-01-28T14:24:27+00:00"


def test_manifest_has_exact_restricted_rights(
    frozen_manifest: SourceSnapshotManifest,
) -> None:
    rights = frozen_manifest.classification
    assert rights.use_class is LicenceUseClass.RESTRICTED
    assert rights.derived_data_allowed is True
    assert rights.internal_review_allowed is True
    assert rights.export_allowed is False
    assert rights.attribution_required is True
    assert rights.attribution_text == (
        "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
        "Wyscout, figshare collection v5, licensed CC BY 4.0."
    )


def test_manifest_files_are_the_exact_ordered_r20_roster(
    frozen_manifest: SourceSnapshotManifest,
) -> None:
    actual = tuple(
        (row.object_path, row.size_bytes, row.row_count, row.sha256)
        for row in frozen_manifest.files
    )
    expected = tuple(
        (row.object_path, row.size_bytes, row.row_count, row.sha256)
        for row in bridge._SOURCE_EVIDENCE
    )
    assert actual == expected
    assert len(actual) == 18


def test_manifest_has_exact_six_dimension_complete_source_coverage(
    frozen_manifest: SourceSnapshotManifest,
) -> None:
    assert frozen_manifest.coverage.overall == 1.0
    assert frozen_manifest.coverage.missing_dimensions == ()
    assert tuple(
        (
            dimension.name,
            dimension.coverage,
            dimension.observed_count,
            dimension.expected_count,
        )
        for dimension in frozen_manifest.coverage.dimensions
    ) == (
        ("source_object_integrity", 1.0, 7, 7),
        ("admitted_member_integrity", 1.0, 10, 10),
        ("match_partition_presence", 1.0, 5, 5),
        ("event_partition_presence", 1.0, 5, 5),
        ("partition_match_id_alignment", 1.0, 5, 5),
        ("scope_exclusion_directory_only", 1.0, 4, 4),
    )


def test_manifest_canonical_bytes_round_trip_identically(
    frozen_manifest: SourceSnapshotManifest,
) -> None:
    payload = canonical_json_bytes(frozen_manifest.model_dump(mode="json"))
    restored = SourceSnapshotManifest.model_validate_json(payload)

    assert restored == frozen_manifest
    assert canonical_json_bytes(restored.model_dump(mode="json")) == payload
    assert payload.endswith(b"\n")
    assert not payload.endswith(b"\n\n")


def test_uuidv5_derivation_is_exact_and_tenant_sensitive() -> None:
    assert bridge._manifest_identity(TENANT_ID, None) == (MANIFEST_ID, TRACE_ID)
    other_manifest, other_trace = bridge._manifest_identity(
        UUID("75a43912-d412-5ff9-a364-7f84d1ad6c5d"),
        None,
    )
    assert other_manifest != MANIFEST_ID
    assert other_trace != TRACE_ID


@pytest.mark.parametrize(
    ("tenant_id", "club_id"),
    [
        (UUID("75a43912-d412-5ff9-a364-7f84d1ad6c5d"), None),
        (TENANT_ID, UUID("85a43912-d412-5ff9-a364-7f84d1ad6c5d")),
    ],
)
def test_nonfixed_tenant_context_fails_before_source_use(
    tenant_id: UUID,
    club_id: UUID | None,
) -> None:
    with pytest.raises(bridge.WyscoutSourceManifestError, match="tenant context"):
        bridge.build_source_snapshot_manifest(
            source_root=Path("data/source/wyscout/v5"),
            tenant_id=tenant_id,
            club_id=club_id,
        )


@pytest.mark.parametrize(
    "source_root",
    [
        Path("data/source/wyscout"),
        Path("data/source/wyscout/v5/.."),
        Path("/tmp/wyscout-v5"),
    ],
)
def test_source_root_alias_or_override_is_rejected(source_root: Path) -> None:
    with pytest.raises(bridge.WyscoutSourceManifestPathError, match="source root"):
        bridge.build_source_snapshot_manifest(
            source_root=source_root,
            tenant_id=TENANT_ID,
        )


def test_completion_manifest_rejects_clock_mutation() -> None:
    payload = Path("data/source/wyscout/v5/completion-manifest.json").read_bytes()
    document = bridge._decode_completion_manifest(payload)
    mutated = json.loads(json.dumps(document))
    mutated["acquisition"]["acquired_at"] = "2026-07-29T15:51:09.598589Z"

    with pytest.raises(bridge.WyscoutSourceManifestError, match="clocks"):
        bridge._validate_completion_document(mutated)


def test_completion_manifest_rejects_rights_mutation() -> None:
    payload = Path("data/source/wyscout/v5/completion-manifest.json").read_bytes()
    document = bridge._decode_completion_manifest(payload)
    mutated = json.loads(json.dumps(document))
    mutated["licence"]["licence_id"] = "UNKNOWN"

    with pytest.raises(bridge.WyscoutSourceManifestError, match="rights"):
        bridge._validate_completion_document(mutated)


def test_completion_manifest_rejects_noncanonical_and_duplicate_keys() -> None:
    with pytest.raises(bridge.WyscoutSourceManifestError, match="not canonical"):
        bridge._decode_completion_manifest(b'{"state": "complete"}\n')
    with pytest.raises(bridge.WyscoutSourceManifestError, match="repeats key"):
        bridge._decode_completion_manifest(b'{"state":"complete","state":"complete"}\n')


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (b"[]", 0),
        (b"[{}]", 1),
        (b'[{"nested":[{"text":"},]"}]},{"value":2}]\n', 2),
    ],
)
def test_streaming_json_counter_counts_top_level_object_rows(
    payload: bytes,
    expected: int,
) -> None:
    counter = bridge._JsonArrayObjectCounter()
    for offset in range(0, len(payload), 3):
        counter.feed(payload[offset : offset + 3])
    assert counter.finish() == expected


@pytest.mark.parametrize(
    "payload",
    [b"{}", b"[1]", b"[{},]", b"[{}]x", b'[{"x":"unterminated}]'],
)
def test_streaming_json_counter_rejects_invalid_top_level_shape(payload: bytes) -> None:
    counter = bridge._JsonArrayObjectCounter()
    with pytest.raises(bridge.WyscoutSourceManifestError):
        counter.feed(payload)
        counter.finish()


@pytest.mark.parametrize("field", ["object_path", "size_bytes", "row_count", "sha256"])
def test_measurement_validation_rejects_each_evidence_drift(field: str) -> None:
    measurements = [
        bridge.SourceEvidenceMeasurement(
            object_path=spec.object_path,
            size_bytes=spec.size_bytes,
            row_count=spec.row_count,
            sha256=spec.sha256,
        )
        for spec in bridge._SOURCE_EVIDENCE
    ]
    replacement: object
    if field == "object_path":
        replacement = "objects/other.json"
    elif field == "size_bytes":
        replacement = measurements[1].size_bytes + 1
    elif field == "row_count":
        replacement = measurements[1].row_count + 1  # type: ignore[operator]
    else:
        replacement = "0" * 64
    measurements[1] = replace(measurements[1], **{field: replacement})

    with pytest.raises(bridge.WyscoutSourceManifestError, match="row 2 conflicts"):
        bridge._validate_measurements(measurements)


def test_measurement_validation_rejects_missing_extra_and_reordered_rows() -> None:
    measurements = tuple(
        bridge.SourceEvidenceMeasurement(
            object_path=spec.object_path,
            size_bytes=spec.size_bytes,
            row_count=spec.row_count,
            sha256=spec.sha256,
        )
        for spec in bridge._SOURCE_EVIDENCE
    )
    with pytest.raises(bridge.WyscoutSourceManifestError, match="exactly 18"):
        bridge._validate_measurements(measurements[:-1])
    with pytest.raises(bridge.WyscoutSourceManifestError, match="exactly 18"):
        bridge._validate_measurements((*measurements, measurements[-1]))
    with pytest.raises(bridge.WyscoutSourceManifestError, match="row 1 conflicts"):
        bridge._validate_measurements((measurements[1], measurements[0], *measurements[2:]))


def test_descriptor_reader_rejects_a_symlink_source(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_bytes(b"[]")
    (tmp_path / "source.json").symlink_to(target)
    spec = bridge.SourceEvidenceSpec(
        object_path="source.json",
        size_bytes=2,
        row_count=0,
        sha256=hashlib.sha256(b"[]").hexdigest(),
        row_format="json-array",
    )

    with pytest.raises(bridge.WyscoutSourceManifestPathError, match="link"):
        bridge._measure_source_file(tmp_path, spec)


def test_immutable_writer_is_idempotent_and_conflict_closed(tmp_path: Path) -> None:
    parent = os.open(tmp_path, os.O_RDONLY | bridge._DIRECTORY | bridge._NOFOLLOW)
    try:
        assert bridge._persist_immutable_file(parent, "manifest.json", b"one\n") is True
        assert bridge._persist_immutable_file(parent, "manifest.json", b"one\n") is False
        with pytest.raises(bridge.WyscoutSourceManifestConflictError, match="conflict"):
            bridge._persist_immutable_file(parent, "manifest.json", b"two\n")
    finally:
        os.close(parent)
    assert (tmp_path / "manifest.json").read_bytes() == b"one\n"
    assert (tmp_path / "manifest.json").stat().st_mode & 0o777 == 0o600
    assert list(tmp_path.iterdir()) == [tmp_path / "manifest.json"]


def test_manifest_root_override_is_rejected(frozen_manifest: SourceSnapshotManifest) -> None:
    with pytest.raises(bridge.WyscoutSourceManifestPathError, match="manifest root"):
        bridge.materialize_source_snapshot_manifest(
            manifest_root=Path("data/working"),
            manifest=frozen_manifest,
        )


def test_canonical_uuid_parser_rejects_noncanonical_spelling() -> None:
    with pytest.raises(bridge.WyscoutSourceManifestError, match="canonical UUID"):
        bridge._canonical_uuid(str(TENANT_ID).upper(), context="tenant-id")


def test_no_product_or_provider_runtime_authority_is_present() -> None:
    source = Path(bridge.__file__).read_text(encoding="utf-8")
    forbidden = (
        "urllib",
        "requests",
        "httpx",
        "data/working/wyscout/v5/bronze",
        "data/working/wyscout/v5/silver",
        "data/working/wyscout/v5/gold",
    )
    assert all(token not in source for token in forbidden)

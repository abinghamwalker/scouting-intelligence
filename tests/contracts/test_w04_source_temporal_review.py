"""Independent adversarial review of the W04 source temporal contract."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from scouting.contracts import (
    CoverageDimension,
    DataCoverage,
    DependencyKind,
    DependencyLineage,
    EvidenceDependency,
    LicenceUseClass,
    SourceFileDigest,
    SourceSnapshotManifest,
    SourceUseClassification,
    TemporalEvidence,
    TenantContext,
)

RELEASE = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
T09 = datetime(2026, 7, 29, 9, tzinfo=UTC)
T10 = datetime(2026, 7, 29, 10, tzinfo=UTC)
T11 = datetime(2026, 7, 29, 11, tzinfo=UTC)
T12 = datetime(2026, 7, 29, 12, tzinfo=UTC)
T13 = datetime(2026, 7, 29, 13, tzinfo=UTC)
T14 = datetime(2026, 7, 29, 14, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def _classification() -> SourceUseClassification:
    return SourceUseClassification(
        use_class=LicenceUseClass.INTERNAL,
        derived_data_allowed=True,
        internal_review_allowed=True,
        export_allowed=False,
        attribution_required=False,
    )


def _coverage() -> DataCoverage:
    return DataCoverage(
        overall=1.0,
        dimensions=(
            CoverageDimension(
                name="source_objects",
                coverage=1.0,
                observed_count=1,
                expected_count=1,
            ),
        ),
    )


def _source_file(
    *,
    object_path: str = "source/provider/snapshot.json",
    digest: str = HASH_A,
) -> SourceFileDigest:
    return SourceFileDigest(
        object_path=object_path,
        sha256=digest,
        size_bytes=128,
        row_count=1,
    )


def _manifest(
    *,
    acquired_at: datetime = T14,
    available_at: datetime = RELEASE,
    files: tuple[SourceFileDigest, ...] | None = None,
) -> SourceSnapshotManifest:
    return SourceSnapshotManifest(
        manifest_id=uuid4(),
        tenant_context=TenantContext(tenant_id=uuid4()),
        trace_id=uuid4(),
        provider="review-provider",
        provider_schema_version="review-v1",
        classification=_classification(),
        acquired_at=acquired_at,
        available_at=available_at,
        files=files or (_source_file(),),
        coverage=_coverage(),
    )


def _lineage(
    *,
    manifest_id: UUID,
    observed_at: datetime,
    available_at: datetime,
) -> DependencyLineage:
    return DependencyLineage(
        lineage_hash=HASH_B,
        dependencies=(
            EvidenceDependency(
                kind=DependencyKind.SOURCE_MANIFEST,
                dependency_id=manifest_id,
                digest=HASH_A,
                observed_at=observed_at,
                available_at=available_at,
            ),
        ),
    )


def _temporal_evidence(
    *,
    lineage: DependencyLineage,
    cutoff: datetime = T12,
) -> TemporalEvidence:
    watermark = lineage.available_at_watermark
    snapshot_as_of = RELEASE
    return TemporalEvidence(
        snapshot_as_of_ts=snapshot_as_of,
        available_at_watermark=watermark,
        valid_from_ts=max(snapshot_as_of, watermark),
        generated_at_ts=max(T14, watermark + timedelta(seconds=1)),
        feature_cutoff_ts=cutoff,
        source_manifest_ids=(lineage.dependencies[0].dependency_id,),
        feature_schema_hash=HASH_C,
        dependency_lineage_hash=lineage.lineage_hash,
        dependency_lineage=lineage,
    )


@pytest.mark.parametrize(
    ("acquired_at", "available_at", "expected_relation"),
    (
        (T14, RELEASE, "release-before-acquisition"),
        (T10, T10, "equal"),
        (T10, T11, "embargo-after-receipt"),
    ),
)
def test_independent_clocks_preserve_all_legitimate_orderings(
    acquired_at: datetime,
    available_at: datetime,
    expected_relation: str,
) -> None:
    """Receipt and upstream availability retain their supplied factual ordering."""
    manifest = _manifest(acquired_at=acquired_at, available_at=available_at)

    assert manifest.acquired_at == acquired_at
    assert manifest.available_at == available_at
    if expected_relation == "release-before-acquisition":
        assert manifest.available_at < manifest.acquired_at
    elif expected_relation == "equal":
        assert manifest.available_at == manifest.acquired_at
    else:
        assert manifest.available_at > manifest.acquired_at


def test_both_clocks_survive_canonical_json_round_trip() -> None:
    """Canonical JSON retains both required UTC instants without conflation."""
    manifest = _manifest(acquired_at=T14, available_at=RELEASE)

    encoded = manifest.model_dump_json()
    restored = SourceSnapshotManifest.model_validate_json(encoded)

    assert restored == manifest
    assert restored.acquired_at == T14
    assert restored.available_at == RELEASE
    assert '"acquired_at":"2026-07-29T14:00:00Z"' in encoded
    assert '"available_at":"2020-01-28T14:24:27Z"' in encoded


@pytest.mark.parametrize("field", ("acquired_at", "available_at"))
def test_both_temporal_fields_are_required(field: str) -> None:
    payload = _manifest().model_dump()
    payload.pop(field)

    with pytest.raises(ValidationError, match="Field required"):
        SourceSnapshotManifest.model_validate(payload)


@pytest.mark.parametrize("field", ("acquired_at", "available_at"))
@pytest.mark.parametrize(
    "invalid_instant",
    (
        datetime(2026, 7, 29, 10),
        datetime(2026, 7, 29, 10, tzinfo=timezone(timedelta(hours=1))),
    ),
    ids=("naive", "non-utc"),
)
def test_both_clocks_reject_ambiguous_python_instants(
    field: str,
    invalid_instant: datetime,
) -> None:
    payload = _manifest().model_dump()
    payload[field] = invalid_instant

    with pytest.raises(ValidationError, match="UTC"):
        SourceSnapshotManifest.model_validate(payload)


@pytest.mark.parametrize("field", ("acquired_at", "available_at"))
@pytest.mark.parametrize(
    "invalid_wire_instant",
    ("2026-07-29T10:00:00", "2026-07-29T11:00:00+01:00"),
    ids=("naive-json", "non-utc-json"),
)
def test_both_clocks_reject_ambiguous_json_instants(
    field: str,
    invalid_wire_instant: str,
) -> None:
    encoded = _manifest().model_dump_json()
    field_fragment = (
        '"acquired_at":"2026-07-29T14:00:00Z"'
        if field == "acquired_at"
        else '"available_at":"2020-01-28T14:24:27Z"'
    )
    invalid_fragment = f'"{field}":"{invalid_wire_instant}"'

    with pytest.raises(ValidationError, match="UTC"):
        SourceSnapshotManifest.model_validate_json(
            encoded.replace(field_fragment, invalid_fragment)
        )


def test_duplicate_source_object_identity_still_rejects() -> None:
    files = (
        _source_file(digest=HASH_A),
        _source_file(digest=HASH_B),
    )

    with pytest.raises(ValidationError, match="source object paths must be unique"):
        _manifest(files=files)


def test_unknown_manifest_fields_still_reject() -> None:
    payload = _manifest().model_dump()
    payload["fabricated_clock"] = T10

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        SourceSnapshotManifest.model_validate(payload)


@pytest.mark.parametrize("bad_digest", ("a" * 63, "A" * 64, "g" * 64))
def test_bad_source_digests_still_reject(bad_digest: str) -> None:
    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        _source_file(digest=bad_digest)


def test_prohibited_classification_cannot_grant_rights() -> None:
    with pytest.raises(ValidationError, match="prohibited sources cannot grant"):
        SourceUseClassification(
            use_class=LicenceUseClass.PROHIBITED,
            derived_data_allowed=True,
            internal_review_allowed=True,
            export_allowed=True,
            attribution_required=False,
        )


@pytest.mark.parametrize(
    ("observed_at", "available_at", "error"),
    (
        (T12, T11, "observed_at must be before"),
        (T13, T11, "observed_at must be before"),
        (T09, T12, "available_at must be before"),
        (T09, T13, "available_at must be before"),
    ),
    ids=(
        "observed-equals-cutoff",
        "observed-after-cutoff",
        "available-equals-cutoff",
        "available-after-cutoff",
    ),
)
def test_temporal_evidence_rejects_cutoff_equality_and_later_facts(
    observed_at: datetime,
    available_at: datetime,
    error: str,
) -> None:
    manifest = _manifest()
    lineage = _lineage(
        manifest_id=manifest.manifest_id,
        observed_at=observed_at,
        available_at=available_at,
    )

    with pytest.raises(ValidationError, match=error):
        _temporal_evidence(lineage=lineage)


def test_early_receipt_cannot_bypass_embargo_at_cutoff() -> None:
    """The independent receipt clock does not weaken downstream availability gating."""
    embargoed = _manifest(acquired_at=T09, available_at=T12)
    lineage = _lineage(
        manifest_id=embargoed.manifest_id,
        observed_at=T09,
        available_at=embargoed.available_at,
    )

    with pytest.raises(ValidationError, match="available_at must be before"):
        _temporal_evidence(lineage=lineage, cutoff=T12)


def test_pre_cutoff_availability_remains_eligible_after_later_local_acquisition() -> None:
    """A truthful later receipt does not rewrite the upstream availability fact."""
    released = _manifest(acquired_at=T14, available_at=RELEASE)
    lineage = _lineage(
        manifest_id=released.manifest_id,
        observed_at=RELEASE,
        available_at=released.available_at,
    )

    evidence = _temporal_evidence(lineage=lineage, cutoff=T12)

    assert evidence.available_at_watermark == RELEASE
    assert evidence.source_manifest_ids == (released.manifest_id,)

"""Immutable source, identity, coverage, and temporal-evidence contracts."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Self

from pydantic import Field, Strict, StringConstraints, model_validator

from .primitives import (
    ActorId,
    ContractModel,
    NonEmptyString,
    NonNegativeInt,
    PositiveVersion,
    SchemaVersion,
    SourceManifestId,
    StrictUuid,
    TenantContext,
    TraceId,
    UnitInterval,
    UtcInstant,
)

type Sha256Digest = Annotated[
    str,
    Strict(),
    StringConstraints(pattern=r"^[0-9a-f]{64}$"),
]


class LicenceUseClass(StrEnum):
    """The strictest permitted use inherited by every derived product."""

    OPEN = "open"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"


class SourceUseClassification(ContractModel):
    """Executable licence/use decisions for one source snapshot."""

    use_class: LicenceUseClass
    derived_data_allowed: bool
    internal_review_allowed: bool
    export_allowed: bool
    attribution_required: bool
    attribution_text: NonEmptyString | None = None

    @model_validator(mode="after")
    def prohibit_unlicensed_use(self) -> Self:
        """A prohibited source cannot accidentally grant a downstream use."""
        if self.use_class is LicenceUseClass.PROHIBITED and (
            self.derived_data_allowed or self.internal_review_allowed or self.export_allowed
        ):
            raise ValueError("prohibited sources cannot grant derived, review, or export use")
        if self.attribution_required and self.attribution_text is None:
            raise ValueError("required attribution must include attribution_text")
        return self


class SourceFileDigest(ContractModel):
    """Content identity and bounded size/count evidence for one source object."""

    object_path: NonEmptyString
    sha256: Sha256Digest
    size_bytes: NonNegativeInt
    row_count: NonNegativeInt | None = None


class CoverageDimension(ContractModel):
    """Coverage for one declared evidence family or population slice."""

    name: NonEmptyString
    coverage: UnitInterval
    observed_count: NonNegativeInt
    expected_count: NonNegativeInt | None = None

    @model_validator(mode="after")
    def counts_are_consistent(self) -> Self:
        """Observed evidence cannot exceed a declared expected population."""
        if self.expected_count is not None and self.observed_count > self.expected_count:
            raise ValueError("observed_count cannot exceed expected_count")
        return self


class DataCoverage(ContractModel):
    """Explicit evidence completeness; missing dimensions are never implicit."""

    overall: UnitInterval
    dimensions: Annotated[tuple[CoverageDimension, ...], Field(min_length=1)]
    missing_dimensions: tuple[NonEmptyString, ...] = ()

    @model_validator(mode="after")
    def dimensions_are_unique(self) -> Self:
        """Each evidence family has exactly one coverage statement."""
        names = [dimension.name for dimension in self.dimensions]
        if len(names) != len(set(names)):
            raise ValueError("coverage dimension names must be unique")
        if len(self.missing_dimensions) != len(set(self.missing_dimensions)):
            raise ValueError("missing_dimensions must be unique")
        return self


class SourceSnapshotManifest(ContractModel):
    """Immutable manifest for one admitted provider delivery.

    ``acquired_at`` records actual local receipt, while ``available_at`` records when
    the upstream source or fact became available. They are independent truthful
    instants: neither is derived from the other, and no ordering is implied.
    """

    schema_version: SchemaVersion = 1
    manifest_id: SourceManifestId
    tenant_context: TenantContext
    trace_id: TraceId
    provider: NonEmptyString
    provider_schema_version: NonEmptyString
    classification: SourceUseClassification
    acquired_at: Annotated[
        UtcInstant,
        Field(description="Actual UTC instant when this project received the delivery."),
    ]
    available_at: Annotated[
        UtcInstant,
        Field(
            description=(
                "Upstream UTC source/fact availability instant; independent of local receipt."
            )
        ),
    ]
    files: Annotated[tuple[SourceFileDigest, ...], Field(min_length=1)]
    coverage: DataCoverage

    @model_validator(mode="after")
    def manifest_is_coherent(self) -> Self:
        """Reject duplicate object identities without conflating the two clocks."""
        paths = [source_file.object_path for source_file in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError("source object paths must be unique")
        return self


class SourceIdentity(ContractModel):
    """A provider-owned identity at a pinned source version."""

    provider: NonEmptyString
    source_id: NonEmptyString
    source_version: NonEmptyString


class IdentityMatchMethod(StrEnum):
    """How a provider identity was linked to a canonical entity."""

    EXACT = "exact"
    DETERMINISTIC = "deterministic"
    REVIEWED = "reviewed"


class IdentityEvidence(ContractModel):
    """Versioned evidence supporting one canonical identity assignment."""

    schema_version: SchemaVersion = 1
    tenant_context: TenantContext
    version: PositiveVersion
    trace_id: TraceId
    source_identity: SourceIdentity
    canonical_id: StrictUuid
    method: IdentityMatchMethod
    confidence: UnitInterval
    evidence_digest: Sha256Digest
    available_at: UtcInstant
    valid_from: UtcInstant
    valid_to: UtcInstant | None = None
    reviewed_by: ActorId | None = None
    supersedes_evidence_digest: Sha256Digest | None = None

    @model_validator(mode="after")
    def identity_evidence_is_coherent(self) -> Self:
        """Retain accountable review and an ordered canonical-identity interval."""
        if self.method is IdentityMatchMethod.REVIEWED and self.reviewed_by is None:
            raise ValueError("reviewed identity evidence requires reviewed_by")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be earlier than valid_from")
        return self


class DependencyKind(StrEnum):
    """Kinds of immutable evidence admitted to a derived result."""

    SOURCE_MANIFEST = "source_manifest"
    IDENTITY_EVIDENCE = "identity_evidence"
    FEATURE_SCHEMA = "feature_schema"
    MODEL_ARTIFACT = "model_artifact"
    RETRIEVAL_INDEX = "retrieval_index"


class EvidenceDependency(ContractModel):
    """One immutable upstream object with observed and knowable times."""

    kind: DependencyKind
    dependency_id: StrictUuid
    digest: Sha256Digest
    observed_at: UtcInstant
    available_at: UtcInstant


class DependencyLineage(ContractModel):
    """Canonical digest plus the exact upstream evidence set."""

    lineage_hash: Sha256Digest
    dependencies: Annotated[tuple[EvidenceDependency, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def dependencies_are_unique(self) -> Self:
        """A dependency identity may appear only once in canonical lineage."""
        identities = [
            (dependency.kind, dependency.dependency_id) for dependency in self.dependencies
        ]
        if len(identities) != len(set(identities)):
            raise ValueError("lineage dependencies must be unique")
        return self

    @property
    def available_at_watermark(self) -> UtcInstant:
        """Latest availability time across all admitted dependencies."""
        return max(dependency.available_at for dependency in self.dependencies)


class TemporalEvidence(ContractModel):
    """Fail-closed as-of proof for one derived boundary payload."""

    schema_version: SchemaVersion = 1
    snapshot_as_of_ts: UtcInstant
    available_at_watermark: UtcInstant
    valid_from_ts: UtcInstant
    generated_at_ts: UtcInstant
    feature_cutoff_ts: UtcInstant
    source_manifest_ids: Annotated[tuple[SourceManifestId, ...], Field(min_length=1)]
    feature_schema_hash: Sha256Digest
    dependency_lineage_hash: Sha256Digest
    dependency_lineage: DependencyLineage

    @model_validator(mode="after")
    def evidence_is_temporally_eligible(self) -> Self:
        """Reject future dependencies and inconsistent declared watermarks."""
        if self.snapshot_as_of_ts > self.feature_cutoff_ts:
            raise ValueError("snapshot_as_of_ts cannot be after feature_cutoff_ts")

        cutoff_or_later_observations = [
            dependency
            for dependency in self.dependency_lineage.dependencies
            if dependency.observed_at >= self.feature_cutoff_ts
        ]
        if cutoff_or_later_observations:
            raise ValueError("dependency observed_at must be before feature_cutoff_ts")

        cutoff_or_later_availability = [
            dependency
            for dependency in self.dependency_lineage.dependencies
            if dependency.available_at >= self.feature_cutoff_ts
        ]
        if cutoff_or_later_availability:
            raise ValueError("dependency available_at must be before feature_cutoff_ts")

        if self.available_at_watermark != self.dependency_lineage.available_at_watermark:
            raise ValueError("available_at_watermark must equal the latest dependency availability")
        if self.available_at_watermark >= self.feature_cutoff_ts:
            raise ValueError("available_at_watermark must be before feature_cutoff_ts")

        expected_valid_from = max(self.snapshot_as_of_ts, self.available_at_watermark)
        if self.valid_from_ts != expected_valid_from:
            raise ValueError(
                "valid_from_ts must equal max(snapshot_as_of_ts, available_at_watermark)"
            )
        if self.generated_at_ts < self.valid_from_ts:
            raise ValueError("generated_at_ts cannot be earlier than valid_from_ts")
        if self.dependency_lineage_hash != self.dependency_lineage.lineage_hash:
            raise ValueError("dependency_lineage_hash must match dependency_lineage.lineage_hash")

        manifest_ids = tuple(
            dependency.dependency_id
            for dependency in self.dependency_lineage.dependencies
            if dependency.kind is DependencyKind.SOURCE_MANIFEST
        )
        if self.source_manifest_ids != manifest_ids:
            raise ValueError("source_manifest_ids must exactly match source-manifest lineage order")
        return self

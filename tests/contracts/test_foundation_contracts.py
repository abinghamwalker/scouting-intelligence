"""Executable acceptance tests for the W03 cross-boundary contract foundation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from scouting.contracts import (
    RESEMBLANCE_ONLY_CLAIM,
    ApplicabilityState,
    AuditAction,
    AuditEvent,
    ConfidenceAssessment,
    ConstraintOperator,
    CoverageDimension,
    DataCoverage,
    DependencyKind,
    DependencyLineage,
    EvidenceDependency,
    EvidenceDimension,
    EvidenceDimensionName,
    IdentityEvidence,
    IdentityMatchMethod,
    LicenceUseClass,
    RetrievalCandidate,
    RetrievalRequest,
    RetrievalResult,
    RoleBrief,
    RoleBriefStatus,
    RoleConstraint,
    RolePreference,
    ShortlistEntry,
    ShortlistEntryState,
    SourceFileDigest,
    SourceIdentity,
    SourceSnapshotManifest,
    SourceUseClassification,
    TemporalEvidence,
    TenantContext,
)

T09 = datetime(2026, 7, 29, 9, tzinfo=UTC)
T10 = datetime(2026, 7, 29, 10, tzinfo=UTC)
T11 = datetime(2026, 7, 29, 11, tzinfo=UTC)
T12 = datetime(2026, 7, 29, 12, tzinfo=UTC)
T13 = datetime(2026, 7, 29, 13, tzinfo=UTC)
T14 = datetime(2026, 7, 29, 14, tzinfo=UTC)
WYSCOUT_RELEASE = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def make_tenant() -> TenantContext:
    """Return one explicit tenant context for contract fixtures."""
    return TenantContext(tenant_id=uuid4(), club_id=uuid4())


def make_coverage() -> DataCoverage:
    """Return coverage that names every observed evidence family."""
    return DataCoverage(
        overall=0.8,
        dimensions=(
            CoverageDimension(
                name="events",
                coverage=0.8,
                observed_count=80,
                expected_count=100,
            ),
        ),
        missing_dimensions=("tracking",),
    )


def make_source_manifest(
    *,
    acquired_at: datetime = T10,
    available_at: datetime = T11,
    files: tuple[SourceFileDigest, ...] | None = None,
) -> SourceSnapshotManifest:
    """Return a strict source manifest with independently supplied temporal facts."""
    return SourceSnapshotManifest(
        manifest_id=uuid4(),
        tenant_context=make_tenant(),
        trace_id=uuid4(),
        provider="synthetic-provider",
        provider_schema_version="1",
        classification=SourceUseClassification(
            use_class=LicenceUseClass.INTERNAL,
            derived_data_allowed=True,
            internal_review_allowed=True,
            export_allowed=False,
            attribution_required=False,
        ),
        acquired_at=acquired_at,
        available_at=available_at,
        files=files
        or (
            SourceFileDigest(
                object_path="source/snapshot.json",
                sha256=HASH_A,
                size_bytes=128,
                row_count=2,
            ),
        ),
        coverage=make_coverage(),
    )


def make_lineage(
    *,
    manifest_id: UUID | None = None,
    observed_at: datetime = T09,
    available_at: datetime = T10,
) -> DependencyLineage:
    """Return minimal source-manifest lineage with a declared availability time."""
    return DependencyLineage(
        lineage_hash=HASH_B,
        dependencies=(
            EvidenceDependency(
                kind=DependencyKind.SOURCE_MANIFEST,
                dependency_id=manifest_id or uuid4(),
                digest=HASH_A,
                observed_at=observed_at,
                available_at=available_at,
            ),
        ),
    )


def make_temporal_evidence(
    *,
    lineage: DependencyLineage | None = None,
    cutoff: datetime = T12,
    generated_at: datetime = T13,
) -> TemporalEvidence:
    """Build a coherent temporal proof from its immutable dependencies."""
    resolved_lineage = lineage or make_lineage()
    manifest_ids = tuple(
        dependency.dependency_id
        for dependency in resolved_lineage.dependencies
        if dependency.kind is DependencyKind.SOURCE_MANIFEST
    )
    watermark = resolved_lineage.available_at_watermark
    return TemporalEvidence(
        snapshot_as_of_ts=T09,
        available_at_watermark=watermark,
        valid_from_ts=max(T09, watermark),
        generated_at_ts=generated_at,
        feature_cutoff_ts=cutoff,
        source_manifest_ids=manifest_ids,
        feature_schema_hash=HASH_C,
        dependency_lineage_hash=resolved_lineage.lineage_hash,
        dependency_lineage=resolved_lineage,
    )


def make_role_brief(*, tenant: TenantContext | None = None) -> RoleBrief:
    """Return a versioned role brief with immutable constraints and weights."""
    return RoleBrief(
        role_brief_id=uuid4(),
        tenant_context=tenant or make_tenant(),
        version=1,
        trace_id=uuid4(),
        owner_id=uuid4(),
        title="Progressive full-back",
        taxonomy_version="roles-v1",
        status=RoleBriefStatus.APPROVED,
        created_at=T10,
        approved_at=T11,
        responsibilities=("progression", "wide_defending"),
        hard_constraints=(
            RoleConstraint(
                field="minimum_minutes",
                operator=ConstraintOperator.AT_LEAST,
                value="900",
            ),
        ),
        preferences=(RolePreference(dimension="style_resemblance", weight=0.7),),
        exemplar_player_ids=(uuid4(),),
    )


def make_dimensions() -> tuple[EvidenceDimension, ...]:
    """Return the full six-part evidence card required by the product contract."""
    return tuple(
        EvidenceDimension(
            name=name,
            score=0.6,
            confidence=0.7,
            reason_codes=(f"{name.value}_available",),
        )
        for name in EvidenceDimensionName
    )


def make_candidate(*, lineage: DependencyLineage | None = None) -> RetrievalCandidate:
    """Return one resemblance-only candidate with confidence, coverage, and lineage."""
    return RetrievalCandidate(
        player_id=uuid4(),
        rank=1,
        evidence_dimensions=make_dimensions(),
        confidence=ConfidenceAssessment(
            score=0.7,
            applicability=ApplicabilityState.APPLICABLE,
        ),
        coverage=make_coverage(),
        lineage=lineage or make_lineage(),
        reason_codes=("style_neighbour", "role_compatible"),
    )


def test_python_uuid_inputs_are_strict_but_wire_json_round_trips() -> None:
    """Python strings are not silently coerced, while canonical JSON remains usable."""
    tenant_id = uuid4()
    tenant = TenantContext(tenant_id=tenant_id)

    with pytest.raises(ValidationError, match="UUID"):
        TenantContext(tenant_id=str(tenant_id))

    restored = TenantContext.model_validate_json(tenant.model_dump_json())
    assert restored == tenant


@pytest.mark.parametrize(
    "invalid_instant",
    [
        datetime(2026, 7, 29, 10),
        datetime(2026, 7, 29, 10, tzinfo=timezone(timedelta(hours=1))),
    ],
)
def test_naive_and_non_utc_instants_are_rejected(invalid_instant: datetime) -> None:
    """Source availability never normalises an ambiguous or non-UTC instant."""
    with pytest.raises(ValidationError, match="UTC"):
        EvidenceDependency(
            kind=DependencyKind.SOURCE_MANIFEST,
            dependency_id=uuid4(),
            digest=HASH_A,
            observed_at=T09,
            available_at=invalid_instant,
        )


def test_contracts_forbid_unknown_fields_and_are_frozen() -> None:
    """The shared base rejects schema drift and mutation at every boundary."""
    tenant = make_tenant()

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TenantContext(tenant_id=uuid4(), unexpected="drift")

    with pytest.raises(ValidationError, match="frozen"):
        tenant.tenant_id = uuid4()


def test_source_manifest_carries_rights_digests_coverage_and_availability() -> None:
    """A provider delivery is reconstructable and explicitly classified."""
    manifest = make_source_manifest()

    assert manifest.files[0].sha256 == HASH_A
    assert manifest.classification.export_allowed is False
    with pytest.raises(ValidationError, match="frozen"):
        manifest.provider = "other-provider"


@pytest.mark.parametrize(
    ("acquired_at", "available_at"),
    (
        (T14, WYSCOUT_RELEASE),
        (T10, T10),
        (T10, T11),
    ),
    ids=("wyscout-release-before-local-acquisition", "equal-instants", "embargo-after-receipt"),
)
def test_source_manifest_accepts_independent_acquisition_and_availability_orderings(
    acquired_at: datetime,
    available_at: datetime,
) -> None:
    """Local receipt and upstream availability remain distinct truthful instants."""
    manifest = make_source_manifest(
        acquired_at=acquired_at,
        available_at=available_at,
    )

    assert manifest.acquired_at == acquired_at
    assert manifest.available_at == available_at


@pytest.mark.parametrize("required_field", ("acquired_at", "available_at"))
def test_source_manifest_requires_both_temporal_instants(required_field: str) -> None:
    """Neither local receipt nor upstream availability may be fabricated by omission."""
    payload = make_source_manifest().model_dump()
    payload.pop(required_field)

    with pytest.raises(ValidationError, match="Field required"):
        SourceSnapshotManifest.model_validate(payload)


@pytest.mark.parametrize("temporal_field", ("acquired_at", "available_at"))
@pytest.mark.parametrize(
    "invalid_instant",
    (
        datetime(2026, 7, 29, 10),
        datetime(2026, 7, 29, 10, tzinfo=timezone(timedelta(hours=1))),
    ),
    ids=("naive", "non-utc"),
)
def test_source_manifest_rejects_non_utc_temporal_instants(
    temporal_field: str,
    invalid_instant: datetime,
) -> None:
    """Both source-manifest clocks retain the strict UTC contract."""
    payload = make_source_manifest().model_dump()
    payload[temporal_field] = invalid_instant

    with pytest.raises(ValidationError, match="UTC"):
        SourceSnapshotManifest.model_validate(payload)


def test_source_manifest_rejects_duplicate_object_paths_and_unknown_fields() -> None:
    """Relaxing timestamp ordering does not weaken object or strict-model identity."""
    source_file = make_source_manifest().files[0]
    duplicate_path = source_file.model_copy(update={"sha256": HASH_B})

    with pytest.raises(ValidationError, match="source object paths must be unique"):
        make_source_manifest(files=(source_file, duplicate_path))

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        SourceSnapshotManifest(
            **make_source_manifest().model_dump(),
            fabricated_availability="not permitted",
        )


def test_prohibited_use_fails_closed() -> None:
    """A prohibited classification cannot accidentally grant downstream rights."""
    with pytest.raises(ValidationError, match="prohibited"):
        SourceUseClassification(
            use_class=LicenceUseClass.PROHIBITED,
            derived_data_allowed=True,
            internal_review_allowed=False,
            export_allowed=False,
            attribution_required=False,
        )


def test_reviewed_identity_evidence_requires_accountable_reviewer() -> None:
    """Manual identity decisions cannot omit who reviewed the evidence."""
    with pytest.raises(ValidationError, match="reviewed_by"):
        IdentityEvidence(
            tenant_context=make_tenant(),
            version=1,
            trace_id=uuid4(),
            source_identity=SourceIdentity(
                provider="synthetic-provider",
                source_id="player-1",
                source_version="snapshot-1",
            ),
            canonical_id=uuid4(),
            method=IdentityMatchMethod.REVIEWED,
            confidence=0.9,
            evidence_digest=HASH_A,
            available_at=T10,
            valid_from=T09,
        )


def test_identity_evidence_retains_an_ordered_valid_interval() -> None:
    """Canonical crosswalk evidence rejects an inverted validity interval."""
    base = {
        "tenant_context": make_tenant(),
        "version": 1,
        "trace_id": uuid4(),
        "source_identity": SourceIdentity(
            provider="synthetic-provider",
            source_id="player-1",
            source_version="snapshot-1",
        ),
        "canonical_id": uuid4(),
        "method": IdentityMatchMethod.EXACT,
        "confidence": 1.0,
        "evidence_digest": HASH_A,
        "available_at": T10,
        "valid_from": T09,
    }
    open_ended = IdentityEvidence(**base)
    bounded = IdentityEvidence(**base, valid_to=T11)

    assert open_ended.valid_to is None
    assert bounded.valid_from < bounded.valid_to

    with pytest.raises(ValidationError, match="valid_to cannot be earlier"):
        IdentityEvidence(**base, valid_to=datetime(2026, 7, 29, 8, tzinfo=UTC))


def test_temporal_evidence_rejects_future_dependencies() -> None:
    """An event observed earlier remains ineligible when its source arrived later."""
    future_lineage = make_lineage(available_at=T13)

    with pytest.raises(ValidationError, match="available_at must be before"):
        make_temporal_evidence(
            lineage=future_lineage,
            cutoff=T12,
            generated_at=T14,
        )


@pytest.mark.parametrize(
    ("lineage", "error"),
    [
        (make_lineage(observed_at=T12, available_at=T11), "observed_at must be before"),
        (make_lineage(observed_at=T09, available_at=T12), "available_at must be before"),
    ],
)
def test_temporal_evidence_rejects_exact_cutoff_boundary(
    lineage: DependencyLineage,
    error: str,
) -> None:
    """Observed and available evidence must both be strictly before the cutoff."""
    with pytest.raises(ValidationError, match=error):
        make_temporal_evidence(lineage=lineage, cutoff=T12, generated_at=T13)


def test_temporal_evidence_rejects_forged_watermarks_and_validity() -> None:
    """Declared temporal fields must be derived exactly from the admitted lineage."""
    lineage = make_lineage(available_at=T10)
    payload = make_temporal_evidence(lineage=lineage).model_dump()
    payload["available_at_watermark"] = T11

    with pytest.raises(ValidationError, match="latest dependency availability"):
        TemporalEvidence.model_validate(payload)

    payload = make_temporal_evidence(lineage=lineage).model_dump()
    payload["valid_from_ts"] = T11
    with pytest.raises(ValidationError, match="valid_from_ts"):
        TemporalEvidence.model_validate(payload)


def test_role_brief_requires_tenant_trace_and_optimistic_version() -> None:
    """Replayable workflow state cannot be constructed without ownership/version data."""
    brief = make_role_brief()
    for required_field in ("tenant_context", "trace_id", "version"):
        payload = brief.model_dump()
        payload.pop(required_field)
        with pytest.raises(ValidationError, match="Field required"):
            RoleBrief.model_validate(payload)


def test_role_brief_approval_timestamps_follow_status_semantics() -> None:
    """Approval is timed, ordered, and cannot be claimed by another status."""
    approved = make_role_brief()
    assert approved.created_at == T10
    assert approved.approved_at == T11

    missing_approval = approved.model_dump(exclude={"approved_at"})
    with pytest.raises(ValidationError, match="require approved_at"):
        RoleBrief.model_validate(missing_approval)

    before_creation = {
        **approved.model_dump(exclude={"approved_at"}),
        "approved_at": T09,
    }
    with pytest.raises(ValidationError, match="earlier than created_at"):
        RoleBrief.model_validate(before_creation)

    draft_claiming_approval = {
        **approved.model_dump(exclude={"status"}),
        "status": RoleBriefStatus.DRAFT,
    }
    with pytest.raises(ValidationError, match="non-approved"):
        RoleBrief.model_validate(draft_claiming_approval)


def test_shortlist_entry_requires_version_and_complete_model_provenance() -> None:
    """Optimistic workflow state cannot retain a partial retrieval provenance tuple."""
    tenant = make_tenant()
    base = {
        "shortlist_entry_id": uuid4(),
        "shortlist_id": uuid4(),
        "tenant_context": tenant,
        "version": 1,
        "trace_id": uuid4(),
        "player_id": uuid4(),
        "state": ShortlistEntryState.LONGLIST,
        "owner_id": uuid4(),
        "rationale": "Evidence warrants review",
        "created_at": T12,
        "updated_at": T13,
    }
    entry = ShortlistEntry(**base)
    assert entry.version == 1

    without_version = dict(base)
    without_version.pop("version")
    with pytest.raises(ValidationError, match="Field required"):
        ShortlistEntry(**without_version)

    with pytest.raises(ValidationError, match="must be supplied together"):
        ShortlistEntry(**base, retrieval_run_id=uuid4())


def test_retrieval_request_is_versioned_tenant_scoped_and_cutoff_safe() -> None:
    """The request pins both brief version and the latest eligible evidence time."""
    brief = make_role_brief()
    request = RetrievalRequest(
        retrieval_request_id=uuid4(),
        tenant_context=brief.tenant_context,
        version=1,
        trace_id=brief.trace_id,
        role_brief_id=brief.role_brief_id,
        role_brief_version=brief.version,
        requested_at=T13,
        feature_cutoff_ts=T12,
        limit=10,
    )
    assert request.claim_boundary == RESEMBLANCE_ONLY_CLAIM

    with pytest.raises(ValidationError, match="cannot be after requested_at"):
        RetrievalRequest(
            **{
                **request.model_dump(exclude={"feature_cutoff_ts"}),
                "feature_cutoff_ts": T14,
            }
        )


def test_retrieval_candidate_exposes_six_dimensions_and_resemblance_only_claim() -> None:
    """Retrieval cannot omit evidence views or add a transfer-success assertion."""
    candidate = make_candidate()
    assert {dimension.name for dimension in candidate.evidence_dimensions} == set(
        EvidenceDimensionName
    )
    assert candidate.confidence.score == 0.7
    assert candidate.coverage.overall == 0.8
    assert candidate.lineage.lineage_hash == HASH_B
    assert candidate.claim_boundary == RESEMBLANCE_ONLY_CLAIM

    with pytest.raises(ValidationError, match="at least 6|all six"):
        RetrievalCandidate(
            **{
                **candidate.model_dump(exclude={"evidence_dimensions"}),
                "evidence_dimensions": candidate.evidence_dimensions[:5],
            }
        )

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        RetrievalCandidate(
            **candidate.model_dump(),
            transfer_success_probability=0.9,
        )


def test_retrieval_result_retains_versions_trace_temporal_proof_and_reason_codes() -> None:
    """A ranked output is exactly replayable and remains inside its claim boundary."""
    tenant = make_tenant()
    brief = make_role_brief(tenant=tenant)
    request_id = uuid4()
    trace_id = uuid4()
    temporal_evidence = make_temporal_evidence()
    candidate = make_candidate(lineage=temporal_evidence.dependency_lineage)
    result = RetrievalResult(
        retrieval_result_id=uuid4(),
        retrieval_request_id=request_id,
        retrieval_run_id=uuid4(),
        tenant_context=tenant,
        version=1,
        trace_id=trace_id,
        role_brief_id=brief.role_brief_id,
        role_brief_version=brief.version,
        model_version="m0-v1",
        index_version="index-v1",
        generated_at=T13,
        temporal_evidence=temporal_evidence,
        candidates=(candidate,),
    )

    assert result.candidates[0].reason_codes == (
        "style_neighbour",
        "role_compatible",
    )
    assert RetrievalResult.model_validate_json(result.model_dump_json()) == result


def test_retrieval_result_rejects_candidate_lineage_outside_temporal_proof() -> None:
    """A candidate cannot smuggle mismatched or future evidence into a valid result."""
    tenant = make_tenant()
    brief = make_role_brief(tenant=tenant)
    temporal_evidence = make_temporal_evidence()
    mismatched_candidate = make_candidate(lineage=make_lineage())
    future_candidate = make_candidate(lineage=make_lineage(available_at=T14))
    base = {
        "retrieval_result_id": uuid4(),
        "retrieval_request_id": uuid4(),
        "retrieval_run_id": uuid4(),
        "tenant_context": tenant,
        "version": 1,
        "trace_id": uuid4(),
        "role_brief_id": brief.role_brief_id,
        "role_brief_version": brief.version,
        "model_version": "m0-v1",
        "index_version": "index-v1",
        "generated_at": T13,
        "temporal_evidence": temporal_evidence,
    }

    for candidate in (mismatched_candidate, future_candidate):
        with pytest.raises(ValidationError, match="lineage must exactly match"):
            RetrievalResult(**base, candidates=(candidate,))


@pytest.mark.parametrize(
    ("action", "before_digest", "after_digest"),
    [
        (AuditAction.CREATE, None, HASH_C),
        (AuditAction.UPDATE, HASH_A, HASH_C),
        (AuditAction.DELETE, HASH_A, None),
        (AuditAction.OVERRIDE, HASH_A, HASH_C),
    ],
)
def test_audit_mutations_require_coherent_digests(
    action: AuditAction,
    before_digest: str | None,
    after_digest: str | None,
) -> None:
    """Each mutation records exactly the state sides meaningful to that action."""
    event = AuditEvent(
        audit_event_id=uuid4(),
        tenant_context=make_tenant(),
        trace_id=uuid4(),
        request_id=uuid4(),
        actor_id=uuid4(),
        action=action,
        target_type="shortlist_entry",
        target_id=uuid4(),
        occurred_at=T13,
        before_digest=before_digest,
        after_digest=after_digest,
        reason="Human override" if action is AuditAction.OVERRIDE else None,
    )
    assert event.action is action


@pytest.mark.parametrize(
    ("action", "before_digest", "after_digest", "error"),
    [
        (AuditAction.CREATE, None, None, "CREATE"),
        (AuditAction.CREATE, HASH_A, HASH_C, "CREATE"),
        (AuditAction.UPDATE, None, HASH_C, "UPDATE"),
        (AuditAction.UPDATE, HASH_A, None, "UPDATE"),
        (AuditAction.DELETE, None, None, "DELETE"),
        (AuditAction.DELETE, HASH_A, HASH_C, "DELETE"),
        (AuditAction.OVERRIDE, None, HASH_C, "OVERRIDE"),
        (AuditAction.OVERRIDE, HASH_A, None, "OVERRIDE"),
    ],
)
def test_audit_mutations_reject_missing_or_incoherent_digest_sides(
    action: AuditAction,
    before_digest: str | None,
    after_digest: str | None,
    error: str,
) -> None:
    """Mutation events fail closed when their before/after evidence is incomplete."""
    with pytest.raises(ValidationError, match=error):
        AuditEvent(
            audit_event_id=uuid4(),
            tenant_context=make_tenant(),
            trace_id=uuid4(),
            request_id=uuid4(),
            actor_id=uuid4(),
            action=action,
            target_type="shortlist_entry",
            target_id=uuid4(),
            occurred_at=T13,
            before_digest=before_digest,
            after_digest=after_digest,
            reason="Human override" if action is AuditAction.OVERRIDE else None,
        )


def test_audit_event_requires_tenant_and_privileged_action_context() -> None:
    """Material actions retain tenant, actor, request, trace, and export scope."""
    base = {
        "audit_event_id": uuid4(),
        "tenant_context": make_tenant(),
        "trace_id": uuid4(),
        "request_id": uuid4(),
        "actor_id": uuid4(),
        "target_type": "retrieval_result",
        "target_id": uuid4(),
        "occurred_at": T13,
    }
    event = AuditEvent(
        **base,
        action=AuditAction.EXPORT,
        export_scope=("candidate_evidence",),
        after_digest=HASH_C,
    )
    assert event.schema_version == 1

    with pytest.raises(ValidationError, match="export_scope"):
        AuditEvent(**base, action=AuditAction.EXPORT)

    without_tenant = dict(base)
    without_tenant.pop("tenant_context")
    with pytest.raises(ValidationError, match="Field required"):
        AuditEvent(**without_tenant, action=AuditAction.READ)

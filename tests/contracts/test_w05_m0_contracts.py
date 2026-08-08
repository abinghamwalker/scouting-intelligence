"""Adversarial checks for the additive W05 M0 contract boundary."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import yaml
from pydantic import ValidationError

from scouting.contracts import (
    RESEMBLANCE_ONLY_CLAIM,
    ApplicabilityState,
    ConfidenceAssessment,
    ContextualRoleMembership,
    CoverageDimension,
    DataConfidenceEvidence,
    DataCoverage,
    DependencyKind,
    DependencyLineage,
    DeterministicRoleMapping,
    EvidenceDependency,
    EvidenceDimension,
    EvidenceDimensionName,
    FeatureValue,
    FeatureValueState,
    FootballResponsibility,
    FootballResponsibilityTaxonomy,
    FootballRole,
    M0ArrayDescriptor,
    M0ArrayDtype,
    M0ArraySemanticRole,
    M0ArtifactManifest,
    M0CandidateDimensionEvidence,
    M0CandidateExplanation,
    M0DimensionEvidence,
    M0DimensionEvidenceState,
    M0Endianness,
    M0EvidenceClass,
    M0ExplanationInput,
    M0MemoryOrder,
    M0ModelFamily,
    M0PcaComponentTieOrderPolicy,
    M0PcaOrientationPolicy,
    M0ResolvedQuery,
    M0ResolvedResponsibilityWeight,
    M0RetrievalResult,
    M0ScoredCandidate,
    M0SerializationFormat,
    M0TiePolicy,
    PinnedM0ServingRequest,
    RetrievalCandidate,
    RetrievalRequest,
    RetrievalResult,
    RoleMembershipProbability,
    TemporalEvidence,
    TenantContext,
    w04_feature_descriptor_digest_for_registry,
)

T09 = datetime(2026, 8, 1, 9, tzinfo=UTC)
T10 = datetime(2026, 8, 1, 10, tzinfo=UTC)
T11 = datetime(2026, 8, 1, 11, tzinfo=UTC)
T12 = datetime(2026, 8, 1, 12, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def make_tenant() -> TenantContext:
    """Return an explicit strict tenant context."""
    return TenantContext(tenant_id=uuid4())


def make_coverage() -> DataCoverage:
    """Return explicit coverage for one admitted evidence family."""
    return DataCoverage(
        overall=1.0,
        dimensions=(
            CoverageDimension(
                name="action_events",
                coverage=1.0,
                observed_count=2,
                expected_count=2,
            ),
        ),
    )


def make_descriptors(
    *,
    model_family: M0ModelFamily = M0ModelFamily.WEIGHTED_COSINE,
    feature_count: int = 2,
    candidate_count: int = 1,
    fitting_count: int | None = None,
    component_count: int = 1,
) -> tuple[M0ArrayDescriptor, ...]:
    """Return the complete canonical array descriptor sequence for one M0 family."""
    fit_count = candidate_count if fitting_count is None else fitting_count
    rows: list[tuple[str, M0ArraySemanticRole, tuple[int, ...], M0ArrayDtype]] = [
        (
            "feature_matrix",
            M0ArraySemanticRole.FEATURE_MATRIX,
            (fit_count, feature_count),
            M0ArrayDtype.FLOAT64,
        )
    ]
    if model_family in {
        M0ModelFamily.ROBUST_SCALED_COSINE,
        M0ModelFamily.WEIGHTED_COSINE,
        M0ModelFamily.ROLE_AWARE_RESTRICTION,
        M0ModelFamily.PCA,
    }:
        rows.extend(
            (
                (
                    "scaler_center",
                    M0ArraySemanticRole.SCALER_CENTER,
                    (feature_count,),
                    M0ArrayDtype.FLOAT64,
                ),
                (
                    "scaler_scale",
                    M0ArraySemanticRole.SCALER_SCALE,
                    (feature_count,),
                    M0ArrayDtype.FLOAT64,
                ),
            )
        )
    if model_family in {M0ModelFamily.WEIGHTED_COSINE, M0ModelFamily.ROLE_AWARE_RESTRICTION}:
        rows.append(
            (
                "feature_weights",
                M0ArraySemanticRole.FEATURE_WEIGHTS,
                (feature_count,),
                M0ArrayDtype.FLOAT64,
            )
        )
    vector_width = feature_count
    if model_family is M0ModelFamily.PCA:
        rows.extend(
            (
                (
                    "pca_components",
                    M0ArraySemanticRole.PCA_COMPONENTS,
                    (component_count, feature_count),
                    M0ArrayDtype.FLOAT64,
                ),
                (
                    "pca_explained_variance",
                    M0ArraySemanticRole.PCA_EXPLAINED_VARIANCE,
                    (component_count,),
                    M0ArrayDtype.FLOAT64,
                ),
            )
        )
        vector_width = component_count
    rows.extend(
        (
            (
                "index_vectors",
                M0ArraySemanticRole.INDEX_VECTORS,
                (candidate_count, vector_width),
                M0ArrayDtype.FLOAT64,
            ),
            (
                "index_player_ids",
                M0ArraySemanticRole.INDEX_PLAYER_IDS,
                (candidate_count, 16),
                M0ArrayDtype.UINT8,
            ),
        )
    )
    item_sizes = {M0ArrayDtype.FLOAT64: 8, M0ArrayDtype.UINT8: 1}
    digests = (HASH_A, HASH_B, HASH_C)
    return tuple(
        M0ArrayDescriptor(
            name=name,
            semantic_role=role,
            dtype=dtype,
            shape=shape,
            endianness=M0Endianness.LITTLE,
            memory_order=M0MemoryOrder.C,
            byte_length=item_sizes[dtype] * _product(shape),
            digest=digests[index % len(digests)],
        )
        for index, (name, role, shape, dtype) in enumerate(rows)
    )


def _product(shape: tuple[int, ...]) -> int:
    """Return a tiny deterministic descriptor-shape product without model code."""
    result = 1
    for dimension in shape:
        result *= dimension
    return result


def make_descriptor() -> M0ArrayDescriptor:
    """Return one safe numeric descriptor for the default feature matrix."""
    return make_descriptors()[0]


def make_artifact(**updates: object) -> M0ArtifactManifest:
    """Build a content-addressed synthetic-development artifact manifest."""
    descriptors = make_descriptors()
    payload: dict[str, object] = {
        "schema_version": 1,
        "artifact_id": uuid4(),
        "model_family": M0ModelFamily.WEIGHTED_COSINE,
        "feature_names": ("action_count", "match_count"),
        "feature_schema_hash": HASH_C,
        "feature_registry_id": "synthetic-feature-registry-v1",
        "feature_registry_canonical_digest": HASH_A,
        "feature_registry_decision_digest": HASH_B,
        "feature_descriptor_digest": HASH_B,
        "evidence_class": M0EvidenceClass.SYNTHETIC_DEVELOPMENT,
        "taxonomy_id": "football-responsibilities",
        "taxonomy_version": "v1",
        "taxonomy_digest": HASH_C,
        "configuration_digest": HASH_B,
        "fitting_population_id": "synthetic-fit-v1",
        "fitting_population_count": 1,
        "fitting_population_manifest_digest": HASH_A,
        "candidate_universe_id": "synthetic-candidates-v1",
        "candidate_universe_count": 1,
        "candidate_universe_manifest_digest": HASH_B,
        "array_payload_digest": HASH_C,
        "array_descriptors": descriptors,
        "array_descriptor_bundle_digest": M0ArtifactManifest.descriptor_bundle_digest_for(
            descriptors
        ),
        "model_id": "m0-weighted-cosine",
        "model_version": "m0-v1",
        "index_id": "m0-index",
        "index_version": "m0-index-v1",
        "lineage_identity": HASH_A,
        "deterministic_seed": 7,
        "serialization_format": M0SerializationFormat.NUMPY_NPZ,
        "pca_orientation_policy": None,
        "pca_component_tie_order_policy": None,
    }
    payload.update(updates)
    payload["artifact_manifest_digest"] = M0ArtifactManifest.digest_for_payload(payload)
    return M0ArtifactManifest(**payload)


def make_family_artifact(
    model_family: M0ModelFamily,
    *,
    feature_names: tuple[str, ...] = ("action_count", "match_count"),
    candidate_count: int = 1,
    fitting_count: int = 1,
    component_count: int = 1,
    **updates: object,
) -> M0ArtifactManifest:
    """Build one valid family-specific artifact with canonical array descriptors."""
    descriptors = make_descriptors(
        model_family=model_family,
        feature_count=len(feature_names),
        candidate_count=candidate_count,
        fitting_count=fitting_count,
        component_count=component_count,
    )
    family_updates: dict[str, object] = {
        "model_family": model_family,
        "feature_names": feature_names,
        "fitting_population_count": fitting_count,
        "candidate_universe_count": candidate_count,
        "array_descriptors": descriptors,
        "array_descriptor_bundle_digest": M0ArtifactManifest.descriptor_bundle_digest_for(
            descriptors
        ),
        "pca_orientation_policy": (
            M0PcaOrientationPolicy.LOWEST_INDEX_MAX_ABS_PIVOT_NON_NEGATIVE
            if model_family is M0ModelFamily.PCA
            else None
        ),
        "pca_component_tie_order_policy": (
            M0PcaComponentTieOrderPolicy.EXPLAINED_VARIANCE_DESCENDING_THEN_COMPONENT_BYTES
            if model_family is M0ModelFamily.PCA
            else None
        ),
    }
    family_updates.update(updates)
    return make_artifact(**family_updates)


def make_w04_artifact(
    model_family: M0ModelFamily = M0ModelFamily.WEIGHTED_COSINE,
) -> M0ArtifactManifest:
    """Build the exact W04 governed artifact projection without changing authority bytes."""
    feature_names = (
        "action_count",
        "coordinate_known_action_count",
        "match_count",
        "resolved_possession_action_count",
    )
    return make_family_artifact(
        model_family,
        feature_names=feature_names,
        feature_registry_id="w04-wyscout-supported-count-features-v1",
        feature_registry_canonical_digest="49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f",
        feature_registry_decision_digest="bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941",
        feature_descriptor_digest="fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e",
        evidence_class=M0EvidenceClass.W04_REAL_GOVERNED,
    )


def make_taxonomy() -> FootballResponsibilityTaxonomy:
    """Build one canonically ordered, self-verifying football taxonomy."""
    payload: dict[str, object] = {
        "schema_version": 1,
        "taxonomy_id": "football-responsibilities",
        "taxonomy_version": "v1",
        "canonical_order": "responsibility_code_role_code_source_label",
        "expert_validation_status": "NOT_PERFORMED",
        "external_expert_evidence": (),
        "claim": "synthetic_development_taxonomy_only",
        "exemplar_notice": "Exemplars remain an additional signal, never a taxonomy replacement.",
        "responsibilities": (
            FootballResponsibility(
                code="pressing",
                label="Pressing",
                description="Closes down opposition possession.",
            ),
            FootballResponsibility(
                code="progression",
                label="Progression",
                description="Advances the ball under control.",
            ),
        ),
        "roles": (
            FootballRole(code="anchor", label="Anchor", responsibility_codes=("pressing",)),
            FootballRole(
                code="carrier",
                label="Carrier",
                responsibility_codes=("pressing", "progression"),
            ),
        ),
        "deterministic_mappings": (
            DeterministicRoleMapping(source_label="Anchor", role_code="anchor"),
            DeterministicRoleMapping(source_label="Carrier", role_code="carrier"),
        ),
    }
    payload["taxonomy_digest"] = FootballResponsibilityTaxonomy.digest_for_payload(payload)
    return FootballResponsibilityTaxonomy(**payload)


def validate_artifact_update(artifact: M0ArtifactManifest, **updates: object) -> M0ArtifactManifest:
    """Re-sign an adversarial manifest update so contract validation reaches the changed field."""
    payload = artifact.model_dump()
    payload.update(updates)
    payload["artifact_manifest_digest"] = M0ArtifactManifest.digest_for_payload(payload)
    return M0ArtifactManifest(**payload)


def make_request(*, excluded_player_ids: tuple = ()) -> RetrievalRequest:
    """Return a strict request shared by the pinned serving fixture."""
    return RetrievalRequest(
        retrieval_request_id=uuid4(),
        tenant_context=make_tenant(),
        version=1,
        trace_id=uuid4(),
        role_brief_id=uuid4(),
        role_brief_version=1,
        requested_at=T12,
        feature_cutoff_ts=T11,
        limit=5,
        excluded_player_ids=excluded_player_ids,
    )


def make_pinned_request(
    artifact: M0ArtifactManifest,
    *,
    retrieval_request: RetrievalRequest | None = None,
) -> PinnedM0ServingRequest:
    """Return a serving request with every artifact and query identity pinned."""
    request = retrieval_request or make_request()
    query_payload: dict[str, object] = {
        "tenant_context": request.tenant_context,
        "trace_id": request.trace_id,
        "role_brief_id": request.role_brief_id,
        "role_brief_version": request.role_brief_version,
        "taxonomy_id": artifact.taxonomy_id,
        "taxonomy_version": artifact.taxonomy_version,
        "taxonomy_digest": artifact.taxonomy_digest,
        "responsibilities": ("pressing",),
        "responsibility_weights": (
            M0ResolvedResponsibilityWeight(responsibility_code="pressing", weight=1.0),
        ),
        "hard_constraints": (),
        "exemplar_player_ids": (),
        "query_player_id": None,
        "feature_cutoff_ts": request.feature_cutoff_ts,
        "limit": request.limit,
        "excluded_player_ids": request.excluded_player_ids,
    }
    query_payload["resolved_query_digest"] = M0ResolvedQuery.digest_for_payload(query_payload)
    resolved_query = M0ResolvedQuery(**query_payload)
    return PinnedM0ServingRequest(
        retrieval_request=request,
        expected_artifact_id=artifact.artifact_id,
        expected_artifact_manifest_digest=artifact.artifact_manifest_digest,
        expected_feature_schema_hash=artifact.feature_schema_hash,
        expected_taxonomy_id=artifact.taxonomy_id,
        expected_taxonomy_version=artifact.taxonomy_version,
        expected_taxonomy_digest=artifact.taxonomy_digest,
        expected_configuration_digest=artifact.configuration_digest,
        expected_fitting_population_id=artifact.fitting_population_id,
        expected_fitting_population_count=artifact.fitting_population_count,
        expected_fitting_population_manifest_digest=artifact.fitting_population_manifest_digest,
        expected_candidate_universe_id=artifact.candidate_universe_id,
        expected_candidate_universe_count=artifact.candidate_universe_count,
        expected_candidate_universe_manifest_digest=artifact.candidate_universe_manifest_digest,
        expected_lineage_identity=artifact.lineage_identity,
        expected_model_id=artifact.model_id,
        expected_model_version=artifact.model_version,
        expected_index_id=artifact.index_id,
        expected_index_version=artifact.index_version,
        resolved_query=resolved_query,
        expected_resolved_query_digest=resolved_query.resolved_query_digest,
        ordered_exclusion_digest=PinnedM0ServingRequest.ordered_exclusion_digest_for(
            request.excluded_player_ids
        ),
        shared_core_version="m0-shared-core-v1",
        tie_policy=M0TiePolicy.SCORE_DISTANCE_THEN_CANONICAL_PLAYER_UUID_BYTES,
    )


def make_retrieval_result(
    request: RetrievalRequest,
    evidence_class: M0EvidenceClass = M0EvidenceClass.SYNTHETIC_DEVELOPMENT,
) -> RetrievalResult:
    """Return an approved six-dimension resemblance-only result."""
    lineage = DependencyLineage(
        lineage_hash=HASH_B,
        dependencies=(
            EvidenceDependency(
                kind=DependencyKind.SOURCE_MANIFEST,
                dependency_id=uuid4(),
                digest=HASH_A,
                observed_at=T09,
                available_at=T10,
            ),
        ),
    )
    temporal_evidence = TemporalEvidence(
        snapshot_as_of_ts=T09,
        available_at_watermark=T10,
        valid_from_ts=T10,
        generated_at_ts=T12,
        feature_cutoff_ts=T11,
        source_manifest_ids=(lineage.dependencies[0].dependency_id,),
        feature_schema_hash=HASH_C,
        dependency_lineage_hash=HASH_B,
        dependency_lineage=lineage,
    )
    coverage = make_coverage()
    confidence = ConfidenceAssessment(score=0.5, applicability=ApplicabilityState.APPLICABLE)
    dimensions = tuple(
        EvidenceDimension(
            name=name,
            score=0.0
            if (
                evidence_class is M0EvidenceClass.W04_REAL_GOVERNED
                and name is EvidenceDimensionName.ROLE_COMPATIBILITY
            )
            else 0.5
            if name
            in {
                EvidenceDimensionName.STYLE_RESEMBLANCE,
                EvidenceDimensionName.ROLE_COMPATIBILITY,
                EvidenceDimensionName.DATA_CONFIDENCE,
            }
            else 0.0,
            confidence=0.0
            if (
                evidence_class is M0EvidenceClass.W04_REAL_GOVERNED
                and name is EvidenceDimensionName.ROLE_COMPATIBILITY
            )
            else 1.0
            if name is EvidenceDimensionName.DATA_CONFIDENCE
            else (
                0.5
                if name
                in {
                    EvidenceDimensionName.STYLE_RESEMBLANCE,
                    EvidenceDimensionName.ROLE_COMPATIBILITY,
                }
                else 0.0
            ),
            reason_codes=(
                ("coverage_complete", "applicability_applicable")
                if name is EvidenceDimensionName.DATA_CONFIDENCE
                else ("unavailable_role_compatibility",)
                if (
                    evidence_class is M0EvidenceClass.W04_REAL_GOVERNED
                    and name is EvidenceDimensionName.ROLE_COMPATIBILITY
                )
                else (f"unavailable_{name.value}",)
                if name
                in {
                    EvidenceDimensionName.IMPACT,
                    EvidenceDimensionName.TRAJECTORY,
                    EvidenceDimensionName.TRANSFER_RISK,
                }
                else (f"{name.value}_measured",)
            ),
        )
        for name in EvidenceDimensionName
    )
    candidate = RetrievalCandidate(
        player_id=uuid4(),
        rank=1,
        evidence_dimensions=dimensions,
        confidence=confidence,
        coverage=coverage,
        lineage=lineage,
        reason_codes=("m0_neighbour",),
    )
    return RetrievalResult(
        retrieval_result_id=uuid4(),
        retrieval_request_id=request.retrieval_request_id,
        retrieval_run_id=uuid4(),
        tenant_context=request.tenant_context,
        version=1,
        trace_id=request.trace_id,
        role_brief_id=request.role_brief_id,
        role_brief_version=request.role_brief_version,
        model_version="m0-v1",
        index_version="m0-index-v1",
        generated_at=T12,
        temporal_evidence=temporal_evidence,
        candidates=(candidate,),
        claim_boundary=RESEMBLANCE_ONLY_CLAIM,
    )


def make_result(artifact: M0ArtifactManifest | None = None) -> M0RetrievalResult:
    """Return a self-verifying result with confidence and dimension-state projections."""
    artifact = artifact or make_artifact()
    request = make_request()
    pinned = make_pinned_request(artifact, retrieval_request=request)
    retrieval_result = make_retrieval_result(request, artifact.evidence_class)
    candidate = retrieval_result.candidates[0]
    confidence = DataConfidenceEvidence(
        player_id=candidate.player_id,
        score=0.5,
        coverage=candidate.coverage,
        applicability=ApplicabilityState.APPLICABLE,
        reason_codes=("coverage_complete",),
    )
    query_feature_values = tuple(
        FeatureValue(
            state=FeatureValueState.VALUE if index == 0 else FeatureValueState.ZERO,
            numeric_value=2.0 if index == 0 else 0.0,
        )
        for index, _ in enumerate(artifact.feature_names)
    )
    candidate_feature_values = tuple(
        FeatureValue(
            state=FeatureValueState.ZERO if index == 0 else FeatureValueState.VALUE,
            numeric_value=0.0 if index == 0 else 1.0,
        )
        for index, _ in enumerate(artifact.feature_names)
    )
    contributions = tuple(
        -0.5 if index == 0 else 0.0 for index, _ in enumerate(artifact.feature_names)
    )
    explanation = M0CandidateExplanation(
        player_id=candidate.player_id,
        rank=1,
        inputs=tuple(
            M0ExplanationInput(
                feature_name=feature_name,
                query_value=query_value,
                candidate_value=candidate_value,
                contribution=contribution,
            )
            for feature_name, query_value, candidate_value, contribution in zip(
                artifact.feature_names,
                query_feature_values,
                candidate_feature_values,
                contributions,
                strict=True,
            )
        ),
        reason_codes=("feature_difference",),
    )
    scored_candidate = M0ScoredCandidate(
        player_id=candidate.player_id,
        rank=candidate.rank,
        distance=0.5,
        query_feature_values=query_feature_values,
        candidate_feature_values=candidate_feature_values,
        contributions=contributions,
    )
    dimension_evidence = M0CandidateDimensionEvidence(
        player_id=candidate.player_id,
        rank=candidate.rank,
        dimensions=tuple(
            M0DimensionEvidence(
                name=name,
                state=M0DimensionEvidenceState.UNAVAILABLE
                if (
                    artifact.evidence_class is M0EvidenceClass.W04_REAL_GOVERNED
                    and name is EvidenceDimensionName.ROLE_COMPATIBILITY
                )
                else M0DimensionEvidenceState.MEASURED
                if name
                in {
                    EvidenceDimensionName.STYLE_RESEMBLANCE,
                    EvidenceDimensionName.ROLE_COMPATIBILITY,
                    EvidenceDimensionName.DATA_CONFIDENCE,
                }
                else M0DimensionEvidenceState.UNAVAILABLE,
                reason_codes=(
                    ("coverage_complete", "applicability_applicable")
                    if name is EvidenceDimensionName.DATA_CONFIDENCE
                    else ("unavailable_role_compatibility",)
                    if (
                        artifact.evidence_class is M0EvidenceClass.W04_REAL_GOVERNED
                        and name is EvidenceDimensionName.ROLE_COMPATIBILITY
                    )
                    else (f"unavailable_{name.value}",)
                    if name
                    in {
                        EvidenceDimensionName.IMPACT,
                        EvidenceDimensionName.TRAJECTORY,
                        EvidenceDimensionName.TRANSFER_RISK,
                    }
                    else (f"{name.value}_measured",)
                ),
                contributes_to_ranking=(
                    name
                    in {
                        EvidenceDimensionName.STYLE_RESEMBLANCE,
                        EvidenceDimensionName.ROLE_COMPATIBILITY,
                    }
                    and not (
                        artifact.evidence_class is M0EvidenceClass.W04_REAL_GOVERNED
                        and name is EvidenceDimensionName.ROLE_COMPATIBILITY
                    )
                ),
            )
            for name in EvidenceDimensionName
        ),
    )
    result_id = uuid4()
    payload = {
        "schema_version": 1,
        "m0_result_id": str(result_id),
        "retrieval_result": retrieval_result.model_dump(mode="json"),
        "artifact_manifest": artifact.model_dump(mode="json"),
        "pinned_serving_request": pinned.model_dump(mode="json"),
        "scored_candidates": [scored_candidate.model_dump(mode="json")],
        "data_confidence_evidence": [confidence.model_dump(mode="json")],
        "dimension_evidence": [dimension_evidence.model_dump(mode="json")],
        "explanations": [explanation.model_dump(mode="json")],
    }
    return M0RetrievalResult(
        m0_result_id=result_id,
        retrieval_result=retrieval_result,
        artifact_manifest=artifact,
        pinned_serving_request=pinned,
        scored_candidates=(scored_candidate,),
        data_confidence_evidence=(confidence,),
        dimension_evidence=(dimension_evidence,),
        explanations=(explanation,),
        result_digest=M0RetrievalResult.digest_for_payload(payload),
    )


def result_payload_with_digest(result: M0RetrievalResult) -> dict[str, object]:
    """Return a mutable complete wire projection with a newly computed result digest."""
    payload = result.model_dump()
    payload["result_digest"] = M0RetrievalResult.digest_for_payload(payload)
    return payload


def test_feature_states_are_explicit_finite_and_fail_closed() -> None:
    """Distinct value states reject missing reasons, invalid zeroes, and non-finite values."""
    assert FeatureValue(state=FeatureValueState.VALUE, numeric_value=1.5).numeric_value == 1.5
    assert FeatureValue(state=FeatureValueState.ZERO, numeric_value=0.0).numeric_value == 0.0
    assert (
        FeatureValue(state=FeatureValueState.MISSING, reason_code="not_observed").numeric_value
        is None
    )
    with pytest.raises(ValidationError, match="ZERO"):
        FeatureValue(state=FeatureValueState.ZERO, numeric_value=0.1)
    with pytest.raises(ValidationError, match="finite"):
        FeatureValue(state=FeatureValueState.VALUE, numeric_value=float("nan"))
    with pytest.raises(ValidationError, match="negative zero"):
        M0ScoredCandidate(
            player_id=uuid4(),
            rank=1,
            distance=-0.0,
            query_feature_values=(),
            candidate_feature_values=(),
            contributions=(),
        )
    with pytest.raises(ValidationError, match="negative zero"):
        M0ScoredCandidate(
            player_id=uuid4(),
            rank=1,
            distance=0.0,
            query_feature_values=(),
            candidate_feature_values=(),
            contributions=(-0.0,),
        )


def test_manifest_is_content_addressed_and_real_authority_is_closed() -> None:
    """Manifest construction and reload reject digest drift and W04 feature expansion."""
    artifact = make_artifact()
    assert M0ArtifactManifest.model_validate_json(artifact.model_dump_json()) == artifact
    with pytest.raises(ValidationError, match="artifact_manifest_digest"):
        M0ArtifactManifest.model_validate(
            {**artifact.model_dump(), "artifact_manifest_digest": HASH_A}
        )
    with pytest.raises(ValidationError, match="W04_REAL_GOVERNED"):
        make_artifact(evidence_class=M0EvidenceClass.W04_REAL_GOVERNED)


def test_safe_array_and_pca_policies_fail_closed() -> None:
    """Unsafe numeric layouts, unknown formats, and incomplete PCA policies are rejected."""
    with pytest.raises(ValidationError, match="byte_length"):
        M0ArrayDescriptor.model_validate({**make_descriptor().model_dump(), "byte_length": 8})
    with pytest.raises(ValidationError, match="Input should be"):
        make_artifact(serialization_format="pickle")
    with pytest.raises(ValidationError, match="family canonical order"):
        make_artifact(model_family=M0ModelFamily.PCA)


def test_w04_descriptor_derivation_and_manifest_authority_fail_closed() -> None:
    """The accepted W04 four-row descriptor and all three identities are exact."""
    registry = yaml.safe_load(
        Path("configs/features/wyscout-v5-supported-count-features-v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert w04_feature_descriptor_digest_for_registry(registry) == (
        "fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e"
    )
    reordered = deepcopy(registry)
    reordered["features"][0], reordered["features"][4] = (
        reordered["features"][4],
        reordered["features"][0],
    )
    with pytest.raises(ValueError, match="canonical order"):
        w04_feature_descriptor_digest_for_registry(reordered)
    expanded = deepcopy(registry)
    expanded["features"].append(deepcopy(registry["features"][0]))
    with pytest.raises(ValueError, match="exactly four"):
        w04_feature_descriptor_digest_for_registry(expanded)
    missing = deepcopy(registry)
    missing["features"] = [
        row for row in missing["features"] if row["feature_name"] != "action_count"
    ]
    with pytest.raises(ValueError, match="exactly four"):
        w04_feature_descriptor_digest_for_registry(missing)
    changed = deepcopy(registry)
    changed["features"][0]["reason"] = "CHANGED"
    assert w04_feature_descriptor_digest_for_registry(changed) != (
        "fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e"
    )

    artifact = make_w04_artifact()
    assert M0ArtifactManifest.model_validate(artifact.model_dump()) == artifact
    for field in (
        "feature_registry_canonical_digest",
        "feature_registry_decision_digest",
        "feature_descriptor_digest",
    ):
        with pytest.raises(ValidationError, match="W04_REAL_GOVERNED"):
            validate_artifact_update(artifact, **{field: HASH_A})
    two_column_matrix = artifact.array_descriptors[0].model_copy(
        update={"shape": (1, 2), "byte_length": 16}
    )
    bad_shape = (two_column_matrix, *artifact.array_descriptors[1:])
    with pytest.raises(ValidationError, match="feature matrix"):
        validate_artifact_update(
            artifact,
            array_descriptors=bad_shape,
            array_descriptor_bundle_digest=M0ArtifactManifest.descriptor_bundle_digest_for(
                bad_shape
            ),
        )


@pytest.mark.parametrize(
    "model_family",
    (
        M0ModelFamily.RAW_EUCLIDEAN_CONTROL,
        M0ModelFamily.ROBUST_SCALED_COSINE,
        M0ModelFamily.WEIGHTED_COSINE,
        M0ModelFamily.PCA,
    ),
)
def test_w04_real_governed_accepts_only_compatible_model_families(
    model_family: M0ModelFamily,
) -> None:
    """Every W04-compatible family retains the exact governed registry identities."""
    assert make_w04_artifact(model_family).model_family is model_family


@pytest.mark.parametrize(
    "model_family",
    (M0ModelFamily.METADATA_CONTROL, M0ModelFamily.ROLE_AWARE_RESTRICTION),
)
def test_w04_real_governed_rejects_incompatible_model_families(
    model_family: M0ModelFamily,
) -> None:
    """W04 evidence cannot be relabelled as a metadata or role-aware family."""
    with pytest.raises(ValidationError, match="W04_REAL_GOVERNED"):
        make_w04_artifact(model_family)


def test_all_family_array_roles_and_shapes_are_executable() -> None:
    """Every M0 family admits only its canonical float64 array topology."""
    for family in M0ModelFamily:
        assert make_family_artifact(family).model_family is family
    weighted = make_family_artifact(M0ModelFamily.WEIGHTED_COSINE)
    reordered = (
        weighted.array_descriptors[0],
        weighted.array_descriptors[2],
        weighted.array_descriptors[1],
        *weighted.array_descriptors[3:],
    )
    with pytest.raises(ValidationError, match="family canonical order"):
        validate_artifact_update(
            weighted,
            array_descriptors=reordered,
            array_descriptor_bundle_digest=M0ArtifactManifest.descriptor_bundle_digest_for(
                reordered
            ),
        )
    pca = make_family_artifact(M0ModelFamily.PCA, component_count=1)
    missing_pca = (
        pca.array_descriptors[0],
        pca.array_descriptors[1],
        pca.array_descriptors[2],
        pca.array_descriptors[-2],
        pca.array_descriptors[-1],
    )
    with pytest.raises(ValidationError, match="family canonical order"):
        validate_artifact_update(
            pca,
            array_descriptors=missing_pca,
            array_descriptor_bundle_digest=M0ArtifactManifest.descriptor_bundle_digest_for(
                missing_pca
            ),
        )
    bad_pca_index = pca.array_descriptors[-2].model_copy(
        update={"shape": (1, 2), "byte_length": 16}
    )
    bad_pca_shape = (*pca.array_descriptors[:-2], bad_pca_index, pca.array_descriptors[-1])
    with pytest.raises(ValidationError, match="PCA array shapes"):
        validate_artifact_update(
            pca,
            array_descriptors=bad_pca_shape,
            array_descriptor_bundle_digest=M0ArtifactManifest.descriptor_bundle_digest_for(
                bad_pca_shape
            ),
        )


def test_array_rows_bind_fitting_population_and_pca_capacity() -> None:
    """Training arrays use fitting rows while index arrays retain candidate rows."""
    weighted = make_family_artifact(
        M0ModelFamily.WEIGHTED_COSINE,
        fitting_count=2,
        candidate_count=3,
    )
    assert weighted.array_descriptors[0].shape == (2, 2)
    assert weighted.array_descriptors[-2].shape == (3, 2)
    assert weighted.array_descriptors[-1].shape == (3, 16)
    candidate_rows_matrix = weighted.array_descriptors[0].model_copy(
        update={"shape": (3, 2), "byte_length": 48}
    )
    mismatched_descriptors = (candidate_rows_matrix, *weighted.array_descriptors[1:])
    with pytest.raises(ValidationError, match="fitting population"):
        validate_artifact_update(
            weighted,
            array_descriptors=mismatched_descriptors,
            array_descriptor_bundle_digest=M0ArtifactManifest.descriptor_bundle_digest_for(
                mismatched_descriptors
            ),
        )
    valid_pca = make_family_artifact(
        M0ModelFamily.PCA,
        fitting_count=2,
        candidate_count=3,
        component_count=2,
    )
    assert valid_pca.array_descriptors[-2].shape == (3, 2)
    with pytest.raises(ValidationError, match="PCA component count"):
        make_family_artifact(
            M0ModelFamily.PCA,
            fitting_count=1,
            candidate_count=2,
            component_count=2,
        )
    with pytest.raises(ValidationError, match="PCA component count"):
        make_family_artifact(
            M0ModelFamily.PCA,
            fitting_count=3,
            candidate_count=2,
            component_count=3,
        )


def test_taxonomy_and_contextual_membership_are_content_addressed() -> None:
    """Canonical taxonomy ordering and contextual membership pins reject substitution."""
    taxonomy = make_taxonomy()
    membership = ContextualRoleMembership(
        player_id=uuid4(),
        context_id="season_2025",
        taxonomy_id=taxonomy.taxonomy_id,
        taxonomy_version=taxonomy.taxonomy_version,
        taxonomy_digest=taxonomy.taxonomy_digest,
        memberships=(
            RoleMembershipProbability(role_code="anchor", probability=0.5),
            RoleMembershipProbability(role_code="carrier", probability=0.5),
        ),
    )
    membership.require_matching_taxonomy(taxonomy)
    reordered = taxonomy.model_dump()
    reordered["responsibilities"] = tuple(reversed(reordered["responsibilities"]))
    reordered["taxonomy_digest"] = FootballResponsibilityTaxonomy.digest_for_payload(reordered)
    with pytest.raises(ValidationError, match="responsibilities must be ordered"):
        FootballResponsibilityTaxonomy.model_validate(reordered)
    substituted = taxonomy.model_dump()
    substituted["responsibilities"] = (
        FootballResponsibility(
            code="pressing",
            label="Different pressing",
            description="Closes down opposition possession.",
        ),
        *taxonomy.responsibilities[1:],
    )
    substituted["taxonomy_digest"] = FootballResponsibilityTaxonomy.digest_for_payload(substituted)
    substitute_taxonomy = FootballResponsibilityTaxonomy.model_validate(substituted)
    with pytest.raises(ValueError, match="taxonomy identity"):
        membership.require_matching_taxonomy(substitute_taxonomy)
    with pytest.raises(ValidationError, match="ordered by role_code"):
        ContextualRoleMembership(
            player_id=membership.player_id,
            context_id=membership.context_id,
            taxonomy_id=taxonomy.taxonomy_id,
            taxonomy_version=taxonomy.taxonomy_version,
            taxonomy_digest=taxonomy.taxonomy_digest,
            memberships=tuple(reversed(membership.memberships)),
        )
    with pytest.raises(ValidationError, match="sum deterministically"):
        ContextualRoleMembership(
            player_id=membership.player_id,
            context_id=membership.context_id,
            taxonomy_id=taxonomy.taxonomy_id,
            taxonomy_version=taxonomy.taxonomy_version,
            taxonomy_digest=taxonomy.taxonomy_digest,
            memberships=(
                RoleMembershipProbability(role_code="anchor", probability=0.4),
                RoleMembershipProbability(role_code="carrier", probability=0.5),
            ),
        )
    unknown_role = membership.model_copy(
        update={"memberships": (RoleMembershipProbability(role_code="unknown", probability=1.0),)}
    )
    with pytest.raises(ValueError, match="absent from the taxonomy"):
        unknown_role.require_matching_taxonomy(taxonomy)


@pytest.mark.parametrize(
    "substitution",
    (
        {"array_payload_digest": HASH_B},
        {"feature_names": ("match_count", "action_count")},
    ),
)
def test_pinned_request_rejects_same_id_manifest_substitution(
    substitution: dict[str, object],
) -> None:
    """Payload, feature-order, and family changes cannot reuse an artifact UUID."""
    artifact = make_artifact()
    pinned = make_pinned_request(artifact)
    substitute = make_artifact(artifact_id=artifact.artifact_id, **substitution)
    with pytest.raises(ValueError, match="artifact_manifest_digest"):
        pinned.require_matching_artifact(substitute)


def test_pinned_request_binds_query_exclusions_and_candidate_universe() -> None:
    """Query, ordered exclusions, core, tie policy, and candidate roster all remain pinned."""
    artifact = make_artifact()
    request = make_request()
    pinned = make_pinned_request(artifact, retrieval_request=request)
    pinned.require_matching_artifact(artifact)
    with pytest.raises(ValidationError, match="ordered_exclusion_digest"):
        PinnedM0ServingRequest.model_validate(
            {**pinned.model_dump(), "ordered_exclusion_digest": HASH_A}
        )
    with pytest.raises(ValidationError, match="Input should be"):
        PinnedM0ServingRequest.model_validate(
            {**pinned.model_dump(), "tie_policy": "unstable_input_order"}
        )
    with pytest.raises(ValueError, match="artifact_manifest_digest"):
        pinned.require_matching_artifact(
            make_artifact(
                artifact_id=artifact.artifact_id,
                candidate_universe_manifest_digest=HASH_C,
            )
        )


def test_resolved_query_is_typed_self_verifying_and_request_bound() -> None:
    """Query contents, ordered weights, and overlapping request identity fail closed."""
    pinned = make_pinned_request(make_artifact())
    assert pinned.resolved_query.resolved_query_digest == (
        pinned.resolved_query.computed_resolved_query_digest
    )
    duplicate_responsibilities = pinned.resolved_query.model_dump()
    duplicate_responsibilities["responsibilities"] = ("pressing", "pressing")
    duplicate_responsibilities["responsibility_weights"] = (
        M0ResolvedResponsibilityWeight(responsibility_code="pressing", weight=1.0),
        M0ResolvedResponsibilityWeight(responsibility_code="pressing", weight=0.5),
    )
    duplicate_responsibilities["resolved_query_digest"] = M0ResolvedQuery.digest_for_payload(
        duplicate_responsibilities
    )
    with pytest.raises(ValidationError, match="responsibilities must be unique"):
        M0ResolvedQuery.model_validate(duplicate_responsibilities)
    drifted_query = pinned.resolved_query.model_dump()
    drifted_query["trace_id"] = uuid4()
    drifted_query["resolved_query_digest"] = M0ResolvedQuery.digest_for_payload(drifted_query)
    with pytest.raises(ValidationError, match="trace_id"):
        PinnedM0ServingRequest.model_validate(
            {
                **pinned.model_dump(),
                "resolved_query": drifted_query,
                "expected_resolved_query_digest": drifted_query["resolved_query_digest"],
            }
        )


def test_result_rejects_same_id_query_substitution_despite_recomputed_digests() -> None:
    """The independent upstream pin rejects semantic query substitution under one brief ID."""
    payload = result_payload_with_digest(make_result())
    pinned_payload = payload["pinned_serving_request"]
    query_payload = pinned_payload["resolved_query"]  # type: ignore[index]
    query_payload["responsibilities"] = ("progression",)  # type: ignore[index]
    query_payload["responsibility_weights"] = (  # type: ignore[index]
        M0ResolvedResponsibilityWeight(responsibility_code="progression", weight=1.0),
    )
    query_payload["resolved_query_digest"] = M0ResolvedQuery.digest_for_payload(  # type: ignore[index]
        query_payload  # type: ignore[arg-type]
    )
    payload["result_digest"] = M0RetrievalResult.digest_for_payload(payload)
    with pytest.raises(
        ValidationError,
        match="expected_resolved_query_digest must match resolved_query.resolved_query_digest",
    ):
        M0RetrievalResult.model_validate(payload)


def test_candidate_specific_dimension_states_enforce_zero_and_evidence_boundaries() -> None:
    """Each candidate owns its six states, with ZERO distinct from ranking absence."""
    result = make_result()
    assert result.dimension_evidence[0].player_id == result.retrieval_result.candidates[0].player_id
    style_zero = (
        result.dimension_evidence[0]
        .dimensions[0]
        .model_copy(update={"state": M0DimensionEvidenceState.ZERO, "contributes_to_ranking": True})
    )
    zero_states = result.dimension_evidence[0].model_copy(
        update={"dimensions": (style_zero, *result.dimension_evidence[0].dimensions[1:])}
    )
    zero_legacy = (
        result.retrieval_result.candidates[0]
        .evidence_dimensions[0]
        .model_copy(update={"score": 0.0})
    )
    zero_candidate = result.retrieval_result.candidates[0].model_copy(
        update={
            "evidence_dimensions": (
                zero_legacy,
                *result.retrieval_result.candidates[0].evidence_dimensions[1:],
            )
        }
    )
    zero_payload = result.model_dump()
    zero_payload["retrieval_result"]["candidates"] = (zero_candidate.model_dump(),)  # type: ignore[index]
    zero_payload["dimension_evidence"] = (zero_states.model_dump(),)
    zero_payload["result_digest"] = M0RetrievalResult.digest_for_payload(zero_payload)
    assert M0RetrievalResult.model_validate(zero_payload).dimension_evidence[0].dimensions[
        0
    ].state is (M0DimensionEvidenceState.ZERO)
    negative_zero_legacy = zero_legacy.model_copy(update={"score": -0.0})
    negative_zero_candidate = zero_candidate.model_copy(
        update={
            "evidence_dimensions": (
                negative_zero_legacy,
                *zero_candidate.evidence_dimensions[1:],
            )
        }
    )
    zero_payload["retrieval_result"]["candidates"] = (  # type: ignore[index]
        negative_zero_candidate.model_dump(),
    )
    zero_payload["result_digest"] = M0RetrievalResult.digest_for_payload(zero_payload)
    with pytest.raises(ValidationError, match=r"canonical \+0\.0"):
        M0RetrievalResult.model_validate(zero_payload)
    misaligned_states = result.dimension_evidence[0].model_copy(update={"player_id": uuid4()})
    misaligned_payload = result.model_dump()
    misaligned_payload["dimension_evidence"] = (misaligned_states.model_dump(),)
    misaligned_payload["result_digest"] = M0RetrievalResult.digest_for_payload(misaligned_payload)
    with pytest.raises(ValidationError, match="candidate dimension evidence must match"):
        M0RetrievalResult.model_validate(misaligned_payload)
    measured_impact = (
        result.dimension_evidence[0]
        .dimensions[2]
        .model_copy(
            update={"state": M0DimensionEvidenceState.MEASURED, "contributes_to_ranking": False}
        )
    )
    impact_states = result.dimension_evidence[0].model_copy(
        update={
            "dimensions": (
                *result.dimension_evidence[0].dimensions[:2],
                measured_impact,
                *result.dimension_evidence[0].dimensions[3:],
            )
        }
    )
    impact_payload = result.model_dump()
    impact_payload["dimension_evidence"] = (impact_states.model_dump(),)
    impact_payload["result_digest"] = M0RetrievalResult.digest_for_payload(impact_payload)
    with pytest.raises(ValidationError, match="strictly positive legacy score"):
        M0RetrievalResult.model_validate(impact_payload)
    w04_result = make_result(make_w04_artifact())
    measured_role = (
        w04_result.dimension_evidence[0]
        .dimensions[1]
        .model_copy(
            update={"state": M0DimensionEvidenceState.MEASURED, "contributes_to_ranking": True}
        )
    )
    w04_states = w04_result.dimension_evidence[0].model_copy(
        update={
            "dimensions": (
                w04_result.dimension_evidence[0].dimensions[0],
                measured_role,
                *w04_result.dimension_evidence[0].dimensions[2:],
            )
        }
    )
    w04_payload = w04_result.model_dump()
    w04_payload["dimension_evidence"] = (w04_states.model_dump(),)
    w04_payload["result_digest"] = M0RetrievalResult.digest_for_payload(w04_payload)
    with pytest.raises(ValidationError, match="strictly positive legacy score"):
        M0RetrievalResult.model_validate(w04_payload)


def test_dimension_states_preserve_legacy_truth_after_digest_recomputation() -> None:
    """Re-digested state records cannot relabel scores or authoritative reasons."""
    result = make_result()
    candidate = result.retrieval_result.candidates[0]
    style_legacy_zero = candidate.evidence_dimensions[0].model_copy(update={"score": 0.0})
    zero_style_candidate = candidate.model_copy(
        update={
            "evidence_dimensions": (
                style_legacy_zero,
                *candidate.evidence_dimensions[1:],
            )
        }
    )
    measured_zero_payload = result_payload_with_digest(result)
    measured_zero_payload["retrieval_result"]["candidates"] = (  # type: ignore[index]
        zero_style_candidate.model_dump(),
    )
    measured_zero_payload["result_digest"] = M0RetrievalResult.digest_for_payload(
        measured_zero_payload
    )
    with pytest.raises(ValidationError, match="strictly positive legacy score"):
        M0RetrievalResult.model_validate(measured_zero_payload)

    contradictory_style = (
        result.dimension_evidence[0]
        .dimensions[0]
        .model_copy(update={"reason_codes": ("contradictory_state_reason",)})
    )
    contradictory_states = result.dimension_evidence[0].model_copy(
        update={
            "dimensions": (
                contradictory_style,
                *result.dimension_evidence[0].dimensions[1:],
            )
        }
    )
    reason_drift_payload = result_payload_with_digest(result)
    reason_drift_payload["dimension_evidence"] = (contradictory_states.model_dump(),)
    reason_drift_payload["result_digest"] = M0RetrievalResult.digest_for_payload(
        reason_drift_payload
    )
    with pytest.raises(ValidationError, match="reasons must exactly match"):
        M0RetrievalResult.model_validate(reason_drift_payload)

    zero_confidence = result.data_confidence_evidence[0].model_copy(update={"score": 0.0})
    data_confidence_legacy = next(
        dimension
        for dimension in candidate.evidence_dimensions
        if dimension.name is EvidenceDimensionName.DATA_CONFIDENCE
    ).model_copy(update={"score": 0.0})
    zero_confidence_candidate = candidate.model_copy(
        update={
            "confidence": candidate.confidence.model_copy(update={"score": 0.0}),
            "evidence_dimensions": tuple(
                data_confidence_legacy
                if dimension.name is EvidenceDimensionName.DATA_CONFIDENCE
                else dimension
                for dimension in candidate.evidence_dimensions
            ),
        }
    )
    zero_data_state = (
        result.dimension_evidence[0]
        .dimensions[-1]
        .model_copy(
            update={"state": M0DimensionEvidenceState.ZERO, "contributes_to_ranking": False}
        )
    )
    zero_data_states = result.dimension_evidence[0].model_copy(
        update={"dimensions": (*result.dimension_evidence[0].dimensions[:-1], zero_data_state)}
    )
    zero_confidence_payload = result_payload_with_digest(result)
    zero_confidence_payload["retrieval_result"]["candidates"] = (  # type: ignore[index]
        zero_confidence_candidate.model_dump(),
    )
    zero_confidence_payload["data_confidence_evidence"] = (zero_confidence.model_dump(),)
    zero_confidence_payload["dimension_evidence"] = (zero_data_states.model_dump(),)
    zero_confidence_payload["result_digest"] = M0RetrievalResult.digest_for_payload(
        zero_confidence_payload
    )
    assert (
        M0RetrievalResult.model_validate(zero_confidence_payload)
        .dimension_evidence[0]
        .dimensions[-1]
        .state
        is M0DimensionEvidenceState.ZERO
    )
    incorrect_data_state = zero_data_state.model_copy(
        update={"state": M0DimensionEvidenceState.MEASURED}
    )
    incorrect_data_states = zero_data_states.model_copy(
        update={
            "dimensions": (
                *zero_data_states.dimensions[:-1],
                incorrect_data_state,
            )
        }
    )
    zero_confidence_payload["dimension_evidence"] = (incorrect_data_states.model_dump(),)
    zero_confidence_payload["result_digest"] = M0RetrievalResult.digest_for_payload(
        zero_confidence_payload
    )
    with pytest.raises(ValidationError, match="derived from confidence score"):
        M0RetrievalResult.model_validate(zero_confidence_payload)
    bad_data_reasons = zero_data_state.model_copy(
        update={"reason_codes": ("contradictory_data_state_reason",)}
    )
    bad_data_states = zero_data_states.model_copy(
        update={"dimensions": (*zero_data_states.dimensions[:-1], bad_data_reasons)}
    )
    zero_confidence_payload["dimension_evidence"] = (bad_data_states.model_dump(),)
    zero_confidence_payload["result_digest"] = M0RetrievalResult.digest_for_payload(
        zero_confidence_payload
    )
    with pytest.raises(ValidationError, match="reasons must exactly match"):
        M0RetrievalResult.model_validate(zero_confidence_payload)


def test_explanations_equal_scored_inputs_after_result_digest_recomputation() -> None:
    """A re-signed explanation cannot omit or fabricate scored feature inputs."""
    result = make_result()
    payload = result.model_dump()
    altered_input = result.explanations[0].inputs[0].model_copy(update={"contribution": 99.0})
    altered_explanation = result.explanations[0].model_copy(
        update={"inputs": (altered_input, *result.explanations[0].inputs[1:])}
    )
    payload["explanations"] = (altered_explanation.model_dump(),)
    payload["result_digest"] = M0RetrievalResult.digest_for_payload(payload)
    with pytest.raises(ValidationError, match="explanation inputs must exactly equal"):
        M0RetrievalResult.model_validate(payload)
    incomplete = result.explanations[0].model_copy(
        update={"inputs": result.explanations[0].inputs[:1]}
    )
    payload["explanations"] = (incomplete.model_dump(),)
    payload["result_digest"] = M0RetrievalResult.digest_for_payload(payload)
    with pytest.raises(ValidationError, match="artifact feature_names"):
        M0RetrievalResult.model_validate(payload)


def test_result_binds_manifest_ranks_confidence_dimension_states_and_digest() -> None:
    """The wrapper enforces result/artifact parity and authoritative confidence projections."""
    result = make_result()
    assert M0RetrievalResult.model_validate_json(result.model_dump_json()) == result
    with pytest.raises(ValidationError, match="result_digest"):
        M0RetrievalResult.model_validate({**result.model_dump(), "result_digest": HASH_A})
    for field, value, message in (
        ("model_version", "other-model", "model_version"),
        ("index_version", "other-index", "index_version"),
    ):
        bad_retrieval = result.retrieval_result.model_copy(update={field: value})
        with pytest.raises(ValidationError, match=message):
            M0RetrievalResult(
                m0_result_id=result.m0_result_id,
                retrieval_result=bad_retrieval,
                artifact_manifest=result.artifact_manifest,
                pinned_serving_request=result.pinned_serving_request,
                scored_candidates=result.scored_candidates,
                data_confidence_evidence=result.data_confidence_evidence,
                dimension_evidence=result.dimension_evidence,
                explanations=result.explanations,
                result_digest=HASH_A,
            )
    bad_temporal_evidence = result.retrieval_result.temporal_evidence.model_copy(
        update={"feature_schema_hash": HASH_A}
    )
    with pytest.raises(ValidationError, match="feature_schema_hash"):
        M0RetrievalResult(
            m0_result_id=result.m0_result_id,
            retrieval_result=result.retrieval_result.model_copy(
                update={"temporal_evidence": bad_temporal_evidence}
            ),
            artifact_manifest=result.artifact_manifest,
            pinned_serving_request=result.pinned_serving_request,
            scored_candidates=result.scored_candidates,
            data_confidence_evidence=result.data_confidence_evidence,
            dimension_evidence=result.dimension_evidence,
            explanations=result.explanations,
            result_digest=HASH_A,
        )


@pytest.mark.parametrize(
    ("path", "replacement", "message"),
    (
        (("retrieval_result", "tenant_context", "tenant_id"), uuid4(), "tenant_context"),
        (("retrieval_result", "trace_id"), uuid4(), "trace_id"),
        (("retrieval_result", "role_brief_id"), uuid4(), "role_brief_id"),
        (("retrieval_result", "role_brief_version"), 2, "role_brief_version"),
        (
            ("retrieval_result", "temporal_evidence", "feature_cutoff_ts"),
            T10,
            "feature_cutoff_ts",
        ),
        (("retrieval_result", "claim_boundary"), "other_claim", "claim_boundary"),
    ),
)
def test_result_rejects_recomputed_digest_request_identity_drift(
    path: tuple[str, ...], replacement: object, message: str
) -> None:
    """A recomputed digest cannot bless request/result identity or claim drift."""
    payload = result_payload_with_digest(make_result())
    target: dict[str, object] = payload
    for key in path[:-1]:
        target = target[key]  # type: ignore[assignment,index]
    target[path[-1]] = replacement
    payload["result_digest"] = M0RetrievalResult.digest_for_payload(payload)
    with pytest.raises(ValidationError, match=message):
        M0RetrievalResult.model_validate(payload)


def test_result_rejects_recomputed_digest_inverse_uuid_equal_distance_tie() -> None:
    """Equal distances must use ascending canonical UUID bytes as their final key."""
    result = make_result()
    high_id = UUID(int=2)
    low_id = UUID(int=1)
    high_candidate = result.retrieval_result.candidates[0].model_copy(
        update={"player_id": high_id, "rank": 1}
    )
    low_candidate = result.retrieval_result.candidates[0].model_copy(
        update={"player_id": low_id, "rank": 2}
    )
    high_scored = result.scored_candidates[0].model_copy(
        update={"player_id": high_id, "rank": 1, "distance": 1.0}
    )
    low_scored = result.scored_candidates[0].model_copy(
        update={"player_id": low_id, "rank": 2, "distance": 1.0}
    )
    high_confidence = result.data_confidence_evidence[0].model_copy(update={"player_id": high_id})
    low_confidence = result.data_confidence_evidence[0].model_copy(update={"player_id": low_id})
    high_explanation = result.explanations[0].model_copy(update={"player_id": high_id, "rank": 1})
    low_explanation = result.explanations[0].model_copy(update={"player_id": low_id, "rank": 2})
    high_dimension_evidence = result.dimension_evidence[0].model_copy(
        update={"player_id": high_id, "rank": 1}
    )
    low_dimension_evidence = result.dimension_evidence[0].model_copy(
        update={"player_id": low_id, "rank": 2}
    )
    payload = result.model_dump()
    payload["retrieval_result"]["candidates"] = (
        high_candidate.model_dump(),
        low_candidate.model_dump(),
    )  # type: ignore[index]
    payload["scored_candidates"] = (
        high_scored.model_dump(),
        low_scored.model_dump(),
    )
    payload["data_confidence_evidence"] = (
        high_confidence.model_dump(),
        low_confidence.model_dump(),
    )
    payload["explanations"] = (high_explanation.model_dump(), low_explanation.model_dump())
    payload["dimension_evidence"] = (
        high_dimension_evidence.model_dump(),
        low_dimension_evidence.model_dump(),
    )
    payload["result_digest"] = M0RetrievalResult.digest_for_payload(payload)
    with pytest.raises(ValidationError, match="distance then canonical player UUID bytes"):
        M0RetrievalResult.model_validate(payload)
    bad_confidence = result.data_confidence_evidence[0].model_copy(update={"score": 0.2})
    with pytest.raises(ValidationError, match="data confidence evidence"):
        M0RetrievalResult(
            m0_result_id=result.m0_result_id,
            retrieval_result=result.retrieval_result,
            artifact_manifest=result.artifact_manifest,
            pinned_serving_request=result.pinned_serving_request,
            scored_candidates=result.scored_candidates,
            data_confidence_evidence=(bad_confidence,),
            dimension_evidence=result.dimension_evidence,
            explanations=result.explanations,
            result_digest=HASH_A,
        )
    rank_two_candidate = result.retrieval_result.candidates[0].model_copy(update={"rank": 2})
    with pytest.raises(ValidationError, match="contiguous"):
        M0RetrievalResult(
            m0_result_id=result.m0_result_id,
            retrieval_result=result.retrieval_result.model_copy(
                update={"candidates": (rank_two_candidate,)}
            ),
            artifact_manifest=result.artifact_manifest,
            pinned_serving_request=result.pinned_serving_request,
            scored_candidates=result.scored_candidates,
            data_confidence_evidence=result.data_confidence_evidence,
            dimension_evidence=result.dimension_evidence,
            explanations=(result.explanations[0].model_copy(update={"rank": 2}),),
            result_digest=HASH_A,
        )
    excluded_request = result.pinned_serving_request.retrieval_request.model_copy(
        update={"excluded_player_ids": (result.retrieval_result.candidates[0].player_id,)}
    )
    excluded_pinned_request = result.pinned_serving_request.model_copy(
        update={
            "retrieval_request": excluded_request,
            "ordered_exclusion_digest": PinnedM0ServingRequest.ordered_exclusion_digest_for(
                excluded_request.excluded_player_ids
            ),
        }
    )
    with pytest.raises(ValidationError, match="excluded_player_ids"):
        M0RetrievalResult(
            m0_result_id=result.m0_result_id,
            retrieval_result=result.retrieval_result,
            artifact_manifest=result.artifact_manifest,
            pinned_serving_request=excluded_pinned_request,
            scored_candidates=result.scored_candidates,
            data_confidence_evidence=result.data_confidence_evidence,
            dimension_evidence=result.dimension_evidence,
            explanations=result.explanations,
            result_digest=HASH_A,
        )
    unavailable_style = M0DimensionEvidence(
        name=EvidenceDimensionName.STYLE_RESEMBLANCE,
        state=M0DimensionEvidenceState.UNAVAILABLE,
        reason_codes=("style_resemblance_measured",),
        contributes_to_ranking=False,
    )
    unavailable_candidate_states = result.dimension_evidence[0].model_copy(
        update={
            "dimensions": (
                unavailable_style,
                *result.dimension_evidence[0].dimensions[1:],
            )
        }
    )
    with pytest.raises(ValidationError, match="absence dimensions"):
        M0RetrievalResult(
            m0_result_id=result.m0_result_id,
            retrieval_result=result.retrieval_result,
            artifact_manifest=result.artifact_manifest,
            pinned_serving_request=result.pinned_serving_request,
            scored_candidates=result.scored_candidates,
            data_confidence_evidence=result.data_confidence_evidence,
            dimension_evidence=(unavailable_candidate_states,),
            explanations=result.explanations,
            result_digest=HASH_A,
        )

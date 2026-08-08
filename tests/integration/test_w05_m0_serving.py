"""Focused parity tests for the one read-only W05 M0 serving core."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

import pytest

from scouting.contracts import (
    ConstraintOperator,
    M0ArtifactManifest,
    M0ResolvedQuery,
    M0ResolvedResponsibilityWeight,
    M0TiePolicy,
    PinnedM0ServingRequest,
    RetrievalRequest,
    RoleConstraint,
    TenantContext,
)
from scouting.features.registry import load_feature_registry
from scouting.m0 import (
    LoadedM0Artifact,
    load_m0_artifact,
    load_m0_configuration,
    load_m0_development_candidates,
    load_m0_development_queries,
)
from scouting.roles.taxonomy import load_role_taxonomy
from scouting.serving.m0 import (
    M0_SERVING_CORE_VERSION,
    M0ServingCore,
    M0ServingError,
    serve_m0_batch,
    serve_m0_request,
)

ROOT = Path(__file__).parents[2]
ARTIFACT_ROOT = ROOT / "runs/w05/m0-baseline-v1"
QUERY_PLAYER = UUID("20000000-0000-4000-8000-000000000001")
EXEMPLAR = UUID("20000000-0000-4000-8000-000000000002")


@pytest.fixture()
def core() -> M0ServingCore:
    """Build the core using only the accepted local authority loaders."""
    registry = load_feature_registry(ROOT / "configs/features/w05-m0-feature-registry-v1.json")
    taxonomy = load_role_taxonomy(
        ROOT / "configs/roles/w05-football-responsibility-taxonomy-v1.json"
    )
    configuration = load_m0_configuration(ROOT / "configs/models/w05-m0-baselines-v1.json")
    candidates = load_m0_development_candidates(
        ROOT / "tests/fixtures/w05/m0-development-candidates-v1.json",
        registry=registry,
        taxonomy=taxonomy,
    )
    queries = load_m0_development_queries(
        ROOT / "tests/fixtures/w05/m0-development-queries-v1.json",
        candidates=candidates,
        configuration=configuration,
    )
    return M0ServingCore(
        registry=registry,
        taxonomy=taxonomy,
        configuration=configuration,
        candidates=candidates,
        queries=queries,
    )


def _request(
    *,
    query_player_id: UUID | None = QUERY_PLAYER,
    exemplar_player_ids: tuple[UUID, ...] = (),
    constraints: tuple[RoleConstraint, ...] = (),
) -> PinnedM0ServingRequest:
    manifest = M0ArtifactManifest.model_validate_json(
        (ARTIFACT_ROOT / "manifest.json").read_bytes()
    )
    request = RetrievalRequest(
        retrieval_request_id=UUID("40000000-0000-4000-8000-000000000001"),
        tenant_context=TenantContext(tenant_id=UUID("50000000-0000-4000-8000-000000000001")),
        version=1,
        trace_id=UUID("60000000-0000-4000-8000-000000000001"),
        role_brief_id=UUID("70000000-0000-4000-8000-000000000001"),
        role_brief_version=1,
        requested_at=datetime(2026, 8, 2, tzinfo=UTC),
        feature_cutoff_ts=datetime(2026, 8, 1, tzinfo=UTC),
        limit=3,
    )
    query_payload: dict[str, object] = {
        "tenant_context": request.tenant_context,
        "trace_id": request.trace_id,
        "role_brief_id": request.role_brief_id,
        "role_brief_version": request.role_brief_version,
        "taxonomy_id": manifest.taxonomy_id,
        "taxonomy_version": manifest.taxonomy_version,
        "taxonomy_digest": manifest.taxonomy_digest,
        "responsibilities": ("advance_play_final_third", "progress_through_pressure"),
        "responsibility_weights": (
            M0ResolvedResponsibilityWeight(
                responsibility_code="advance_play_final_third", weight=1.0
            ),
            M0ResolvedResponsibilityWeight(
                responsibility_code="progress_through_pressure", weight=1.0
            ),
        ),
        "hard_constraints": constraints,
        "exemplar_player_ids": exemplar_player_ids,
        "query_player_id": query_player_id,
        "feature_cutoff_ts": request.feature_cutoff_ts,
        "limit": request.limit,
        "excluded_player_ids": request.excluded_player_ids,
    }
    query_payload["resolved_query_digest"] = M0ResolvedQuery.digest_for_payload(query_payload)
    query = M0ResolvedQuery(**query_payload)
    return PinnedM0ServingRequest(
        retrieval_request=request,
        expected_artifact_id=manifest.artifact_id,
        expected_artifact_manifest_digest=manifest.artifact_manifest_digest,
        expected_feature_schema_hash=manifest.feature_schema_hash,
        expected_taxonomy_id=manifest.taxonomy_id,
        expected_taxonomy_version=manifest.taxonomy_version,
        expected_taxonomy_digest=manifest.taxonomy_digest,
        expected_configuration_digest=manifest.configuration_digest,
        expected_fitting_population_id=manifest.fitting_population_id,
        expected_fitting_population_count=manifest.fitting_population_count,
        expected_fitting_population_manifest_digest=manifest.fitting_population_manifest_digest,
        expected_candidate_universe_id=manifest.candidate_universe_id,
        expected_candidate_universe_count=manifest.candidate_universe_count,
        expected_candidate_universe_manifest_digest=manifest.candidate_universe_manifest_digest,
        expected_lineage_identity=manifest.lineage_identity,
        expected_model_id=manifest.model_id,
        expected_model_version=manifest.model_version,
        expected_index_id=manifest.index_id,
        expected_index_version=manifest.index_version,
        resolved_query=query,
        expected_resolved_query_digest=query.resolved_query_digest,
        ordered_exclusion_digest=PinnedM0ServingRequest.ordered_exclusion_digest_for(()),
        shared_core_version=M0_SERVING_CORE_VERSION,
        tie_policy=M0TiePolicy.SCORE_DISTANCE_THEN_CANONICAL_PLAYER_UUID_BYTES,
    )


def test_request_and_batch_are_byte_identical_and_replayable(core: M0ServingCore) -> None:
    """Both entry points return one canonical result byte sequence and digest."""
    request = _request()
    direct = serve_m0_request(core, request)
    batch = serve_m0_batch(core, (request,))[0]
    reload = serve_m0_request(core, request)

    assert direct.model_dump_json() == batch.model_dump_json() == reload.model_dump_json()
    assert direct.result_digest == batch.result_digest == reload.result_digest
    assert direct.retrieval_result.claim_boundary == "resemblance_only"
    payload = direct.model_dump(mode="json")
    wire = direct.model_dump_json().lower()
    assert "match_percentage" not in wire
    assert "overall_score" not in wire
    assert '"recommendation":' not in wire
    assert "overall" not in payload["retrieval_result"]


def test_serving_uses_the_shared_loader_and_preserves_artifact_bytes(
    core: M0ServingCore,
) -> None:
    """The two thin entry points load the accepted bundle; neither can mutate it."""
    before = {
        path.name: sha256(path.read_bytes()).hexdigest() for path in sorted(ARTIFACT_ROOT.iterdir())
    }
    with (
        patch("scouting.serving.m0.load_m0_artifact", wraps=load_m0_artifact) as loader,
        patch.object(
            LoadedM0Artifact,
            "score",
            autospec=True,
            side_effect=LoadedM0Artifact.score,
        ) as scorer,
    ):
        serve_m0_request(core, _request())
        serve_m0_batch(core, (_request(),))
    assert loader.call_count == 2
    assert scorer.call_count == 2
    after = {
        path.name: sha256(path.read_bytes()).hexdigest() for path in sorted(ARTIFACT_ROOT.iterdir())
    }
    assert after == before
    assert not any(hasattr(M0ServingCore, name) for name in ("fit", "write", "update"))


def test_filters_and_exemplar_mode_are_fail_closed_and_deterministic(core: M0ServingCore) -> None:
    """Supported filters work; invalid filters and missing query signal cannot degrade."""
    constrained = _request(
        constraints=(
            RoleConstraint(
                field="synthetic_position_code",
                operator=ConstraintOperator.EQUALS,
                value="CENTRAL",
            ),
        )
    )
    constrained_result = serve_m0_request(core, constrained)
    assert all(
        int(str(candidate.player_id).rsplit("-", maxsplit=1)[1]) % 3 == 1
        for candidate in constrained_result.retrieval_result.candidates
    )

    exemplar_result = serve_m0_request(
        core, _request(query_player_id=None, exemplar_player_ids=(EXEMPLAR, QUERY_PLAYER))
    )
    assert exemplar_result.explanations[0].reason_codes[0] == "exemplar_query_resolved"

    invalid = _request(
        constraints=(
            RoleConstraint(field="unknown", operator=ConstraintOperator.EQUALS, value="x"),
        )
    )
    with pytest.raises(M0ServingError, match="unsupported"):
        serve_m0_request(core, invalid)


def test_stale_constructed_request_is_rejected_before_loader(core: M0ServingCore) -> None:
    """A carried digest cannot authenticate model-copy or construct query mutations."""
    original = _request()
    forged_query = original.resolved_query.model_copy(
        update={
            "hard_constraints": (
                RoleConstraint(
                    field="synthetic_position_code",
                    operator=ConstraintOperator.EQUALS,
                    value="CENTRAL",
                ),
            )
        }
    )
    forged = original.model_copy(update={"resolved_query": forged_query})
    with patch("scouting.serving.m0.load_m0_artifact", wraps=load_m0_artifact) as loader:
        with pytest.raises(M0ServingError, match="normal validation"):
            serve_m0_request(core, forged)
        with pytest.raises(M0ServingError, match="normal validation"):
            serve_m0_request(core, original.model_copy(update={"expected_model_version": "forged"}))
    assert loader.call_count == 0


def test_ids_filter_plan_confidence_and_temporal_evidence_are_truthful(core: M0ServingCore) -> None:
    """Corrected public results have unique IDs, canonical filters, limits, and row clocks."""
    baseline = serve_m0_request(core, _request())
    changed_time = _request().model_copy(
        update={
            "retrieval_request": _request().retrieval_request.model_copy(
                update={"requested_at": datetime(2026, 8, 2, tzinfo=UTC) + timedelta(days=1)}
            )
        }
    )
    replay = serve_m0_request(core, changed_time)
    assert baseline.m0_result_id != replay.m0_result_id
    assert (
        baseline.retrieval_result.retrieval_result_id != replay.retrieval_result.retrieval_result_id
    )
    assert baseline.retrieval_result.retrieval_run_id != replay.retrieval_result.retrieval_run_id
    assert "hard_constraints_applied" not in baseline.retrieval_result.candidates[0].reason_codes
    assert baseline.retrieval_result.candidates[0].confidence.applicability.value == "limited"
    assert baseline.retrieval_result.candidates[0].confidence.limitations == (
        "synthetic_development_only",
        "no_recommendation_evidence",
    )
    confidence_evidence = baseline.data_confidence_evidence[0]
    data_dimension = baseline.retrieval_result.candidates[0].evidence_dimensions[-1]
    assert (
        confidence_evidence.limitations
        == baseline.retrieval_result.candidates[0].confidence.limitations
    )
    assert data_dimension.reason_codes == (
        *confidence_evidence.reason_codes,
        *confidence_evidence.limitations,
        "applicability_limited",
    )
    assert baseline.retrieval_result.temporal_evidence.snapshot_as_of_ts == datetime(
        2025, 1, 3, tzinfo=UTC
    )
    assert baseline.retrieval_result.temporal_evidence.available_at_watermark == datetime(
        2025, 1, 4, tzinfo=UTC
    )

    false_first = (
        RoleConstraint(
            field="synthetic_position_code", operator=ConstraintOperator.EQUALS, value="NONE"
        ),
        RoleConstraint(
            field="synthetic_age_years", operator=ConstraintOperator.AT_LEAST, value="bad"
        ),
    )
    for constraints in (false_first, tuple(reversed(false_first))):
        with pytest.raises(M0ServingError, match="numeric constraint value"):
            serve_m0_request(core, _request(constraints=constraints))

    first = (
        RoleConstraint(
            field="synthetic_age_years", operator=ConstraintOperator.AT_LEAST, value="18"
        ),
        RoleConstraint(
            field="synthetic_position_code", operator=ConstraintOperator.IN, value="WIDE,CENTRAL"
        ),
    )
    second = tuple(reversed(first))
    one = serve_m0_request(core, _request(constraints=first))
    two = serve_m0_request(core, _request(constraints=second))
    assert one.scored_candidates == two.scored_candidates
    assert one.dimension_evidence == two.dimension_evidence
    assert one.explanations == two.explanations

"""Read-only local evidence UI that delegates all retrieval geometry to W05."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from scouting.contracts import (
    M0ArtifactManifest,
    M0ResolvedQuery,
    M0ResolvedResponsibilityWeight,
    M0TiePolicy,
    PinnedM0ServingRequest,
    RetrievalRequest,
    TenantContext,
)
from scouting.features.registry import load_feature_registry
from scouting.m0 import (
    load_m0_configuration,
    load_m0_development_candidates,
    load_m0_development_queries,
)
from scouting.roles.taxonomy import load_role_taxonomy
from scouting.serving.m0 import (
    M0_SERVING_CORE_VERSION,
    M0ServingCore,
    serve_m0_batch,
    serve_m0_request,
)

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "apps/web/templates/w07"
STATIC = ROOT / "apps/web/static/w07"
_NO_GO = "NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE"
_REGISTRY_DIGEST = "c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644"
_ACCEPTED_RESULT_DIGEST = "9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e"
_ACCEPTED_LINEAGE_HASH = "c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491"


class W07State(StrEnum):
    LOADING = "loading"
    EMPTY = "empty"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    NO_GO = "no-go"


def _core() -> tuple[M0ServingCore, Any]:
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
    return (
        M0ServingCore(
            registry=registry,
            taxonomy=taxonomy,
            configuration=configuration,
            candidates=candidates,
            queries=queries,
        ),
        candidates,
    )


def default_request(
    query_player_id: UUID = UUID("20000000-0000-4000-8000-000000000001"),
) -> PinnedM0ServingRequest:
    manifest = M0ArtifactManifest.model_validate_json(
        (ROOT / "runs/w05/m0-baseline-v1/manifest.json").read_bytes()
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
    payload: dict[str, Any] = {
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
        "hard_constraints": (),
        "exemplar_player_ids": (),
        "query_player_id": query_player_id,
        "feature_cutoff_ts": request.feature_cutoff_ts,
        "limit": request.limit,
        "excluded_player_ids": (),
    }
    payload["resolved_query_digest"] = M0ResolvedQuery.digest_for_payload(payload)
    query = M0ResolvedQuery.model_validate(payload)
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


def create_w07_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static/w07", StaticFiles(directory=STATIC), name="w07-static")
    templates = Environment(
        loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(("html",))
    )
    core, candidates = _core()
    catalogue = {
        UUID(str(row["feature_row"]["player_id"])): {
            "label": f"Synthetic candidate {index:02d}",
            "player_id": UUID(str(row["feature_row"]["player_id"])),
            "row": row,
        }
        for index, row in enumerate(candidates.rows, 1)
    }
    manifest = M0ArtifactManifest.model_validate_json(
        (ROOT / "runs/w05/m0-baseline-v1/manifest.json").read_bytes()
    )
    authority = {
        "source": "local synthetic-development W05",
        "evidence_class": "synthetic_development",
        "model_id": manifest.model_id,
        "model_version": manifest.model_version,
        "index_id": manifest.index_id,
        "index_version": manifest.index_version,
        "artifact_id": str(manifest.artifact_id),
        "manifest_digest": manifest.artifact_manifest_digest,
        "feature_registry_id": "w05-m0-feature-registry-v1",
        "feature_registry_digest": _REGISTRY_DIGEST,
        "feature_schema_hash": manifest.feature_schema_hash,
        "taxonomy_id": manifest.taxonomy_id,
        "taxonomy_version": manifest.taxonomy_version,
        "taxonomy_digest": manifest.taxonomy_digest,
        "configuration_digest": manifest.configuration_digest,
        "fitting_population": (
            f"{manifest.fitting_population_id} ({manifest.fitting_population_count} rows)"
        ),
        "candidate_population": (
            f"{manifest.candidate_universe_id} ({manifest.candidate_universe_count} rows)"
        ),
        "data_model_window": (
            "synthetic observations 2025-01-03; local availability watermark 2025-01-04"
        ),
        "feature_cutoff_ts": "2026-08-01T00:00:00+00:00",
        "confidence": "1.0 data completeness; no expert relevance confidence",
        "applicability": "LIMITED",
        "limitations": ("resemblance_only; synthetic_development_only; no_recommendation_evidence"),
        "lineage_identity": manifest.lineage_identity,
        "accepted_result_digest": _ACCEPTED_RESULT_DIGEST,
        "accepted_lineage_hash": _ACCEPTED_LINEAGE_HASH,
    }
    w04 = {
        "action_count": 2,
        "coordinate_known_action_count": 2,
        "match_count": 1,
        "resolved_possession_action_count": 2,
        "suppressed": "minutes/rates/per-90",
    }
    w06 = {
        "decision": "NO_GO",
        "reason": "MISSING_EXPERT_RELEVANCE_EVIDENCE",
        "protected_outputs_opened": False,
    }

    @app.middleware("http")
    async def local_policy(_: Request, call_next: Any) -> Any:
        response = await call_next(_)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; "
            "base-uri 'none'; form-action 'self'"
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    def page(request: Request, name: str, **context: Any) -> HTMLResponse:
        render_context = {
            "request": request,
            "no_go": _NO_GO,
            "authority": authority,
            "w04": w04,
            "w06": w06,
        }
        render_context.update(context)
        return HTMLResponse(templates.get_template(name).render(**render_context))

    @app.get("/", response_class=HTMLResponse)
    @app.get("/w07", response_class=HTMLResponse)
    def landing(request: Request) -> HTMLResponse:
        return page(
            request,
            "landing.html",
            current_page="landing",
            page_title="Local evidence overview",
        )

    @app.get("/w07/search", response_class=HTMLResponse)
    def search(request: Request, q: str = "", position: str = "") -> HTMLResponse:
        query = q.strip().lower()[:64]
        requested_position = position.strip().upper()[:32]
        selected: list[dict[str, Any]] = []
        for player_id, player_record in catalogue.items():
            row = player_record["row"]
            feature = row["feature_row"]
            label = str(player_record["label"])
            if query and query not in label.lower() and query not in str(player_id):
                continue
            if requested_position not in {"", "CENTRAL", "DEFENSIVE", "WIDE"}:
                selected = []
                break
            if requested_position and feature.get("synthetic_position_code") != requested_position:
                continue
            selected.append(player_record)
        return page(
            request,
            "search.html",
            players=tuple(selected),
            empty=not selected,
            q=q,
            position=requested_position,
            positions=("CENTRAL", "DEFENSIVE", "WIDE"),
            current_page="search",
            page_title="Search synthetic-development evidence",
        )

    @app.get("/w07/player/{player_id}", response_class=HTMLResponse)
    def player(request: Request, player_id: str) -> HTMLResponse:
        try:
            identity = UUID(player_id)
        except ValueError:
            return _state_page(request, W07State.UNAVAILABLE)
        player_record = catalogue.get(identity)
        if player_record is None:
            return _state_page(request, W07State.UNAVAILABLE)
        return page(
            request,
            "player.html",
            player=player_record,
            current_page="player",
            page_title=f"{player_record['label']} evidence",
        )

    def result_context(result: Any) -> dict[str, Any]:
        rows = tuple(
            {
                "player_id": scored.player_id,
                "label": catalogue[scored.player_id]["label"],
                "rank": scored.rank,
                "distance": scored.distance,
                "candidate": candidate,
                "confidence": confidence,
                "dimensions": dimensions,
                "explanation": explanation,
                "reason_codes": candidate.reason_codes,
                "applicability": candidate.confidence.applicability.value,
                "limitations": candidate.confidence.limitations,
            }
            for scored, candidate, confidence, dimensions, explanation in zip(
                result.scored_candidates,
                result.retrieval_result.candidates,
                result.data_confidence_evidence,
                result.dimension_evidence,
                result.explanations,
                strict=True,
            )
        )
        result_authority = {
            **authority,
            "result_id": str(result.m0_result_id),
            "result_digest": result.result_digest,
            "feature_cutoff_ts": (
                result.retrieval_result.temporal_evidence.feature_cutoff_ts.isoformat()
            ),
            "lineage": (result.retrieval_result.temporal_evidence.dependency_lineage_hash),
        }
        return {
            "result": result,
            "result_rows": rows,
            "query_id": result.pinned_serving_request.resolved_query.query_player_id,
            "authority": result_authority,
        }

    @app.get("/w07/retrieval", response_class=HTMLResponse)
    def retrieval(request: Request) -> HTMLResponse:
        result = serve_m0_request(core, default_request())
        return page(
            request,
            "result.html",
            comparison=False,
            current_page="retrieval",
            page_title="Role-aware retrieval evidence",
            **result_context(result),
        )

    @app.get("/w07/retrieval/{query_id}", response_class=HTMLResponse)
    def retrieval_for_player(request: Request, query_id: str) -> HTMLResponse:
        try:
            query = UUID(query_id)
        except ValueError:
            return _state_page(request, W07State.UNAVAILABLE)
        if query not in catalogue:
            return _state_page(request, W07State.UNAVAILABLE)
        result = serve_m0_request(core, default_request(query))
        return page(
            request,
            "result.html",
            comparison=False,
            current_page="retrieval",
            page_title="Role-aware retrieval evidence",
            **result_context(result),
        )

    @app.get("/w07/compare/{query_id}/{candidate_id}", response_class=HTMLResponse)
    def compare(request: Request, query_id: str, candidate_id: str) -> HTMLResponse:
        try:
            query, candidate = UUID(query_id), UUID(candidate_id)
        except ValueError:
            return _state_page(request, W07State.UNAVAILABLE)
        if query not in catalogue or candidate not in catalogue:
            return _state_page(request, W07State.UNAVAILABLE)
        result = serve_m0_batch(core, (default_request(query),))[0]
        context = result_context(result)
        selected_row = next(
            (row for row in context["result_rows"] if row["player_id"] == candidate),
            None,
        )
        if selected_row is None:
            return _state_page(request, W07State.UNAVAILABLE)
        return page(
            request,
            "result.html",
            comparison=True,
            selected_row=selected_row,
            current_page="retrieval",
            page_title="Query and candidate evidence contrast",
            **context,
        )

    @app.get("/w07/evidence", response_class=HTMLResponse)
    def evidence(request: Request) -> HTMLResponse:
        return page(
            request,
            "evidence.html",
            current_page="evidence",
            page_title="Evidence and validation centre",
        )

    def _state_page(request: Request, state: W07State) -> HTMLResponse:
        return page(
            request,
            "state.html",
            state=state.value,
            current_page="state",
            page_title=f"{state.value.title()} evidence state",
        )

    @app.get("/w07/state/{state}", response_class=HTMLResponse)
    def state(request: Request, state: str) -> HTMLResponse:
        try:
            selected = W07State(state)
        except ValueError:
            raise HTTPException(status_code=404, detail="unknown evidence state") from None
        return _state_page(request, selected)

    return app

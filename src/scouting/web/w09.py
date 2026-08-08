"""Local-only browser composition for the governed W09 research workbench."""

from __future__ import annotations

import ipaddress
import json
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from scouting.api.research import ResearchApiRuntime, create_research_router
from scouting.contracts.research import ResearchDatasetDescriptor, ResearchVersionPins
from scouting.serving.research import ResearchServingService

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "apps/web/templates/w09"
STATIC = ROOT / "apps/web/static/w09"
_HISTORICAL_BOUNDARY = (
    "Ranks show resemblance inside this governed historical population only. They do not "
    "predict performance or establish recruitment usefulness, value, availability or squad fit."
)


class W09BootstrapError(RuntimeError):
    """Injected runtime and serving authority cannot be rendered coherently."""


def _bootstrap_payload(
    runtime: ResearchApiRuntime,
    serving: ResearchServingService,
) -> dict[str, object]:
    dataset = ResearchDatasetDescriptor.model_validate(runtime.dataset.model_dump(mode="python"))
    pins = ResearchVersionPins.model_validate(serving.pins.model_dump(mode="python"))
    if (
        dataset.dataset_version != pins.dataset_version
        or dataset.dataset_manifest_digest != pins.dataset_manifest_digest
        or dataset.feature_cutoff_ts != pins.feature_cutoff_ts
    ):
        raise W09BootstrapError("rendered dataset and serving pins are incompatible")
    matrix = serving.matrix_manifest
    competition_seasons: dict[tuple[UUID, str], set[str]] = {}
    for row in serving.matrix_rows:
        competition_seasons.setdefault((row.competition_id, row.competition_name), set()).add(
            row.season_id
        )
    competitions = tuple(
        {
            "competition_id": str(competition_id),
            "competition_name": competition_name,
            "season_ids": sorted(season_ids),
        }
        for (competition_id, competition_name), season_ids in sorted(
            competition_seasons.items(),
            key=lambda item: (item[0][1].casefold(), item[0][0].bytes),
        )
    )
    return {
        "schema_version": 1,
        "dataset": dataset.model_dump(mode="json"),
        "pins": pins.model_dump(mode="json"),
        "feature_names": list(matrix.feature_names),
        "matrix_row_count": matrix.matrix_row_count,
        "unique_matrix_player_count": matrix.unique_matrix_player_count,
        "competitions": competitions,
        "claim_boundary": _HISTORICAL_BOUNDARY,
    }


def _host_name(host_header: str) -> str:
    if not host_header:
        return ""
    if host_header.startswith("["):
        closing = host_header.find("]")
        return host_header[1:closing] if closing > 0 else ""
    return host_header.rsplit(":", 1)[0] if host_header.count(":") == 1 else host_header


def _loopback_host(host_header: str, *, allow_test_host: bool) -> bool:
    host = _host_name(host_header).casefold()
    if host == "localhost" or (allow_test_host and host == "testserver"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _security_headers(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
        "img-src 'self'; font-src 'self'; base-uri 'none'; form-action 'self'; "
        "frame-ancestors 'none'"
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"


def create_w09_app(
    *,
    runtime: ResearchApiRuntime | None,
    serving: ResearchServingService | None,
    unavailable_reason: str | None = None,
    allow_test_host: bool = False,
) -> FastAPI:
    """Compose one W09 page and its exact same-process accepted API router."""

    if (runtime is None) != (serving is None):
        raise TypeError("runtime and serving must be supplied together")
    if runtime is not None and type(runtime) is not ResearchApiRuntime:
        raise TypeError("runtime must be an exact ResearchApiRuntime")
    if serving is not None and type(serving) is not ResearchServingService:
        raise TypeError("serving must be an exact ResearchServingService")
    if runtime is None and (
        not unavailable_reason or unavailable_reason != unavailable_reason.strip()
    ):
        raise TypeError("an unavailable app requires one trimmed reason")
    if runtime is not None and unavailable_reason is not None:
        raise TypeError("an available app cannot carry an unavailable reason")

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static/w09", StaticFiles(directory=STATIC), name="w09-static")
    templates = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(("html",)),
    )
    available = runtime is not None and serving is not None
    bootstrap = (
        _bootstrap_payload(runtime, serving)
        if runtime is not None and serving is not None
        else None
    )
    if runtime is not None:
        app.include_router(create_research_router(runtime))
    app.state.w09_available = available
    app.state.w09_unavailable_reason = unavailable_reason

    @app.middleware("http")
    async def local_only_policy(request: Request, call_next: Any) -> Response:
        if not _loopback_host(
            request.headers.get("host", ""),
            allow_test_host=allow_test_host,
        ):
            response: Response = PlainTextResponse(
                "W09 is available only on a loopback host.",
                status_code=400,
            )
        else:
            response = await call_next(request)
        _security_headers(response)
        return response

    def favicon() -> Response:
        return Response(status_code=204)

    def page(request: Request) -> HTMLResponse:
        rendered = templates.get_template("workbench.html").render(
            request=request,
            available=available,
            unavailable_reason=unavailable_reason,
            bootstrap_json=(
                json.dumps(
                    bootstrap,
                    ensure_ascii=False,
                    allow_nan=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                if bootstrap is not None
                else ""
            ),
            historical_boundary=_HISTORICAL_BOUNDARY,
        )
        return HTMLResponse(rendered, status_code=200 if available else 503)

    app.add_api_route("/", page, methods=["GET"], response_class=HTMLResponse)
    app.add_api_route("/w09", page, methods=["GET"], response_class=HTMLResponse)
    app.add_api_route("/favicon.ico", favicon, methods=["GET"], include_in_schema=False)
    return app


__all__ = [
    "W09BootstrapError",
    "create_w09_app",
]

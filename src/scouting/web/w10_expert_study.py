"""Local-only browser console for the blinded W10 expert relevance study."""

from __future__ import annotations

import hashlib
import ipaddress
import secrets
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from scouting.contracts.expert_relevance import (
    AssessmentBasisV2,
    EvidenceAvailabilityV2,
    EvidenceGapV2,
    EvidenceMetricUnitV2,
    EvidenceSufficiencyV2,
    ExpertExperienceKind,
    ExpertRelevanceProtocol,
    ExpertStudyPresentationBundle,
    HistoricalComparisonJudgementV1,
    HistoricalComparisonPilotDebriefV1,
    JudgementState,
    MdEvidenceSubrubricV2,
    QualitativeFailureCategory,
    StudyMode,
)
from scouting.storage.expert_study import (
    PROTOCOL_APPROVAL_CONFIRMATION,
    ExpertStudyConfigurationError,
    ExpertStudyConflictError,
    ExpertStudyIntegrityError,
    ExpertStudyNotFoundError,
    ExpertStudyPreparationError,
    ExpertStudyStorageError,
    ExpertStudyStore,
    HistoricalComparisonPilotStore,
    HistoricalComparisonStudySnapshot,
    StudySessionSnapshot,
    V2MechanicsPilotStore,
    V2StudySnapshot,
)

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "apps/web/templates/w10_expert_study"
STATIC = ROOT / "apps/web/static/w10-expert-study"
_MAX_FORM_BYTES = 32 * 1024
_CAPABILITY_COOKIE = "w10_study_capability"
_LANE_COOKIE = "w10_study_lane"
_CSRF_COOKIE = "w10_study_csrf"
_LANES: dict[str, StudyMode] = {
    "pilot": StudyMode.MECHANICS_PILOT,
    "formal": StudyMode.FORMAL_G_RW4,
}
_APPROVAL_FIELDS = frozenset({"csrf", "approved_by_pseudonym", "confirmation"})
_SESSION_FIELDS = frozenset(
    {
        "csrf",
        "lane",
        "participant_code",
        "years_experience",
        "assessed_players_within_window",
        "conflict_declared",
        "conflict_note",
        "voluntary_participation",
        "local_pseudonymous_storage",
        "withdrawal_before_submission_understood",
        "immutable_after_submission_understood",
        "research_limitations_understood",
        *(f"experience_{kind.value}" for kind in ExpertExperienceKind),
    }
)
_JUDGEMENT_FIELDS = frozenset(
    {
        "csrf",
        "command_id",
        "expected_revision",
        "presentation_id",
        "state",
        "relevance_rating",
        "confidence",
        "failure_category",
        "explanation",
    }
)
_CORRECTION_FIELDS = _JUDGEMENT_FIELDS
_SUBMIT_FIELDS = frozenset({"csrf", "command_id", "expected_revision"})
_DETACH_FIELDS = frozenset({"csrf"})


class W10StudyWebError(ValueError):
    """A bounded local browser action is invalid."""

    def __init__(self, message: str, *, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


def _host_name(host_header: str) -> str:
    if not host_header:
        return ""
    if host_header.startswith("["):
        closing = host_header.find("]")
        return host_header[1:closing] if closing > 0 else ""
    return host_header.rsplit(":", 1)[0] if host_header.count(":") == 1 else host_header


def _loopback_host(host_header: str, *, allow_test_host: bool) -> bool:
    host = _host_name(host_header).casefold()
    if host == "localhost" or (allow_test_host and host in {"testclient", "testserver"}):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _security_headers(response: Response) -> None:
    response.headers.update(
        {
            "Cache-Control": "no-store",
            "Content-Security-Policy": (
                "default-src 'none'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self'; font-src 'self'; "
                "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
            ),
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }
    )


def _bounded_text(
    value: str,
    *,
    field: str,
    limit: int,
    required: bool = False,
) -> str:
    normalized = value.strip()
    if required and not normalized:
        raise W10StudyWebError(f"{field} is required")
    if len(normalized) > limit:
        raise W10StudyWebError(f"{field} is too long")
    return normalized


def _boolean(values: Mapping[str, str], key: str) -> bool:
    return values.get(key) == "true"


async def _form_values(
    request: Request,
    csrf_token: str,
    *,
    allowed_fields: frozenset[str],
    csrf_cookie_name: str = _CSRF_COOKIE,
) -> tuple[dict[str, str], str]:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].casefold()
    if content_type != "application/x-www-form-urlencoded":
        raise W10StudyWebError("unsupported form", status_code=415)
    declared = request.headers.get("content-length")
    if declared is not None and (not declared.isdecimal() or int(declared) > _MAX_FORM_BYTES):
        raise W10StudyWebError("oversized form", status_code=413)
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        if len(chunk) > _MAX_FORM_BYTES - size:
            raise W10StudyWebError("oversized form", status_code=413)
        size += len(chunk)
        chunks.append(chunk)
    raw = b"".join(chunks)
    try:
        decoded = raw.decode("utf-8", errors="strict")
        parsed = parse_qs(decoded, keep_blank_values=True, strict_parsing=False)
    except UnicodeError as exc:
        raise W10StudyWebError("form must be strict UTF-8") from exc
    if any(key not in allowed_fields for key in parsed):
        raise W10StudyWebError("form contains an unexpected field")
    if any(len(items) != 1 for items in parsed.values()):
        raise W10StudyWebError("form fields must occur exactly once")
    values = {key: items[0] for key, items in parsed.items() if items}
    if values.get("csrf") != csrf_token or request.cookies.get(csrf_cookie_name) != csrf_token:
        raise W10StudyWebError("local form expired; reload and try again", status_code=403)
    return values, hashlib.sha256(raw).hexdigest()


def create_w10_expert_study_app(
    *,
    protocol: ExpertRelevanceProtocol | None,
    presentation: ExpertStudyPresentationBundle | None,
    pilot_store: ExpertStudyStore | None,
    formal_store: ExpertStudyStore | None,
    unavailable_reason: str | None = None,
    allow_test_host: bool = False,
) -> FastAPI:
    """Compose one local W10 page from participant-safe authority only."""

    supplied = (protocol, presentation, pilot_store, formal_store)
    available = all(value is not None for value in supplied)
    if any(value is not None for value in supplied) and not available:
        raise TypeError("protocol, presentation and both stores must be supplied together")
    if not available and (
        not unavailable_reason or unavailable_reason != unavailable_reason.strip()
    ):
        raise TypeError("unavailable W10 app requires one trimmed reason")
    if available and unavailable_reason is not None:
        raise TypeError("available W10 app cannot carry an unavailable reason")
    if protocol is not None and type(protocol) is not ExpertRelevanceProtocol:
        raise TypeError("protocol must be an exact ExpertRelevanceProtocol")
    if presentation is not None and type(presentation) is not ExpertStudyPresentationBundle:
        raise TypeError("presentation must be an exact ExpertStudyPresentationBundle")
    if pilot_store is not None and (
        type(pilot_store) is not ExpertStudyStore
        or pilot_store.mode is not StudyMode.MECHANICS_PILOT
    ):
        raise TypeError("pilot_store must be an exact mechanics-pilot store")
    if formal_store is not None and (
        type(formal_store) is not ExpertStudyStore
        or formal_store.mode is not StudyMode.FORMAL_G_RW4
    ):
        raise TypeError("formal_store must be an exact formal store")
    if available:
        if protocol is None or presentation is None or pilot_store is None or formal_store is None:
            raise TypeError("available W10 app lost its complete authority")
        if any(
            store.protocol.protocol_digest != protocol.protocol_digest
            or store.presentation.presentation_digest != presentation.presentation_digest
            for store in (pilot_store, formal_store)
        ):
            raise TypeError("store authority differs from rendered authority")

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.mount(
        "/static/w10-expert-study",
        StaticFiles(directory=STATIC),
        name="w10-expert-study-static",
    )
    templates = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(("html",)),
    )
    csrf_token = secrets.token_urlsafe(32)
    app.state.w10_available = available
    app.state.protocol = protocol
    app.state.presentation = presentation

    @app.middleware("http")
    async def local_only_policy(request: Request, call_next: Any) -> Response:
        client_host = request.client.host if request.client is not None else ""
        host_allowed = _loopback_host(
            request.headers.get("host", ""), allow_test_host=allow_test_host
        )
        client_allowed = _loopback_host(client_host, allow_test_host=allow_test_host)
        if not host_allowed or not client_allowed:
            response: Response = PlainTextResponse(
                "W10 is available only on a loopback host.",
                status_code=400,
            )
        else:
            response = await call_next(request)
        _security_headers(response)
        response.set_cookie(
            _CSRF_COOKIE,
            csrf_token,
            httponly=True,
            samesite="strict",
            secure=False,
        )
        return response

    def render(template: str, *, status_code: int = 200, **context: object) -> HTMLResponse:
        return HTMLResponse(
            templates.get_template(template).render(
                csrf=csrf_token,
                protocol=protocol,
                presentation=presentation,
                approval_confirmation=PROTOCOL_APPROVAL_CONFIRMATION,
                experience_kinds=tuple(ExpertExperienceKind),
                rating_anchors=protocol.rating_anchors if protocol is not None else (),
                failure_categories=tuple(QualitativeFailureCategory),
                **context,
            ),
            status_code=status_code,
        )

    def request_session(
        request: Request,
    ) -> tuple[ExpertStudyStore, str, StudySessionSnapshot] | None:
        capability = request.cookies.get(_CAPABILITY_COOKIE)
        lane = request.cookies.get(_LANE_COOKIE)
        if not capability or lane not in _LANES:
            return None
        store = pilot_store if lane == "pilot" else formal_store
        if store is None:
            return None
        try:
            return store, capability, store.load_session(capability)
        except ExpertStudyNotFoundError:
            return None

    def page(request: Request, *, error_message: str | None = None) -> HTMLResponse:
        if not available:
            return render(
                "unavailable.html",
                status_code=503,
                unavailable_reason=unavailable_reason,
            )
        if formal_store is None:
            raise RuntimeError("available W10 app lost its formal store")
        active = request_session(request)
        if active is None:
            approval = formal_store.load_protocol_approval()
            return render(
                "dashboard.html",
                approval=approval,
                error_message=error_message,
            )
        store, _, snapshot = active
        if snapshot.complete:
            return render(
                "complete.html",
                snapshot=snapshot,
                completion=snapshot.completion,
                pilot=store.mode is StudyMode.MECHANICS_PILOT,
                test_only=store.test_only,
            )
        task = store.current_task(snapshot)
        judgement_by_presentation = {item.presentation_id: item for item in snapshot.judgements}
        review_rows = tuple(
            {
                "ordinal": item.presentation_ordinal,
                "judgement": judgement_by_presentation[item.presentation_id],
                "command_id": uuid4(),
            }
            for item in snapshot.session.presentations
            if item.presentation_id in judgement_by_presentation
        )
        return render(
            "participant.html",
            snapshot=snapshot,
            task=task,
            pilot=store.mode is StudyMode.MECHANICS_PILOT,
            command_id=uuid4(),
            completion_command_id=uuid4(),
            review_rows=review_rows,
            error_message=error_message,
        )

    @app.get("/", response_model=None)
    def root() -> RedirectResponse:
        return RedirectResponse("/w10", status_code=307)

    @app.get("/w10", response_class=HTMLResponse)
    def w10(request: Request) -> HTMLResponse:
        return page(request)

    if available:
        if pilot_store is None or formal_store is None:
            raise TypeError("available W10 app lost its study stores")

        @app.post("/w10/approval", response_model=None)
        async def approve_protocol(
            request: Request,
        ) -> RedirectResponse | HTMLResponse:
            try:
                values, _ = await _form_values(
                    request,
                    csrf_token,
                    allowed_fields=_APPROVAL_FIELDS,
                )
                formal_store.record_protocol_approval(
                    approved_by_pseudonym=_bounded_text(
                        values.get("approved_by_pseudonym", ""),
                        field="product-owner pseudonym",
                        limit=32,
                        required=True,
                    ),
                    confirmation=values.get("confirmation", ""),
                )
                return RedirectResponse("/w10", status_code=303)
            except (W10StudyWebError, ExpertStudyStorageError) as exc:
                status_code = (
                    exc.status_code
                    if isinstance(exc, W10StudyWebError)
                    else 409
                    if isinstance(exc, ExpertStudyConflictError)
                    else 422
                )
                error_response = page(request, error_message=str(exc))
                error_response.status_code = status_code
                return error_response

        @app.post("/w10/sessions", response_model=None)
        async def prepare_session(
            request: Request,
        ) -> RedirectResponse | HTMLResponse:
            try:
                values, _ = await _form_values(
                    request,
                    csrf_token,
                    allowed_fields=_SESSION_FIELDS,
                )
                lane = values.get("lane", "")
                if lane not in _LANES:
                    raise W10StudyWebError("study lane is invalid")
                store = pilot_store if lane == "pilot" else formal_store
                try:
                    years = int(values.get("years_experience", ""))
                except ValueError as exc:
                    raise W10StudyWebError("years of experience must be a whole number") from exc
                if not 0 <= years <= 80:
                    raise W10StudyWebError("years of experience are outside the supported range")
                kinds: list[ExpertExperienceKind] = []
                for kind in ExpertExperienceKind:
                    if _boolean(values, f"experience_{kind.value}"):
                        kinds.append(kind)
                note = _bounded_text(
                    values.get("conflict_note", ""),
                    field="conflict note",
                    limit=500,
                )
                consent = {
                    name: _boolean(values, name)
                    for name in (
                        "voluntary_participation",
                        "local_pseudonymous_storage",
                        "withdrawal_before_submission_understood",
                        "immutable_after_submission_understood",
                        "research_limitations_understood",
                    )
                }
                prepared = store.prepare_session(
                    participant_code=_bounded_text(
                        values.get("participant_code", ""),
                        field="participant pseudonym",
                        limit=32,
                        required=True,
                    ),
                    years_experience=years,
                    experience_kinds=kinds,
                    assessed_players_within_window=_boolean(
                        values, "assessed_players_within_window"
                    ),
                    conflict_declared=_boolean(values, "conflict_declared"),
                    conflict_note=note or None,
                    consent_items=consent,
                )
                response = RedirectResponse("/w10", status_code=303)
                response.set_cookie(
                    _CAPABILITY_COOKIE,
                    prepared.capability,
                    httponly=True,
                    samesite="strict",
                    secure=False,
                )
                response.set_cookie(
                    _LANE_COOKIE,
                    lane,
                    httponly=True,
                    samesite="strict",
                    secure=False,
                )
                return response
            except (W10StudyWebError, ExpertStudyStorageError) as exc:
                status_code = (
                    exc.status_code
                    if isinstance(exc, W10StudyWebError)
                    else 409
                    if isinstance(exc, ExpertStudyConflictError)
                    else 422
                )
                error_response = page(request, error_message=str(exc))
                error_response.status_code = status_code
                return error_response

        @app.post("/w10/judgements", response_model=None)
        async def record_judgement(
            request: Request,
        ) -> RedirectResponse | HTMLResponse:
            try:
                values, request_digest = await _form_values(
                    request,
                    csrf_token,
                    allowed_fields=_JUDGEMENT_FIELDS,
                )
                active = request_session(request)
                if active is None:
                    raise W10StudyWebError("study session is unavailable", status_code=404)
                store, capability, _ = active
                state = JudgementState(values.get("state", ""))
                relevance: int | None = None
                confidence: int | None = None
                if state is JudgementState.RATED:
                    relevance = int(values.get("relevance_rating", ""))
                    confidence = int(values.get("confidence", ""))
                failure_value = values.get("failure_category", "")
                failure = QualitativeFailureCategory(failure_value) if failure_value else None
                explanation = _bounded_text(
                    values.get("explanation", ""),
                    field="optional football explanation",
                    limit=1000,
                )
                store.record_judgement(
                    capability=capability,
                    command_id=UUID(values.get("command_id", "")),
                    expected_revision=int(values.get("expected_revision", "")),
                    request_digest=request_digest,
                    presentation_id=UUID(values.get("presentation_id", "")),
                    state=state,
                    relevance_rating=relevance,
                    confidence=confidence,
                    failure_category=failure,
                    explanation=explanation or None,
                )
                return RedirectResponse("/w10", status_code=303)
            except (
                ValueError,
                ExpertStudyStorageError,
            ) as exc:
                status_code = 409 if isinstance(exc, ExpertStudyConflictError) else 422
                response = page(request, error_message=str(exc))
                response.status_code = status_code
                return response

        @app.post("/w10/submit", response_model=None)
        async def submit_session(
            request: Request,
        ) -> RedirectResponse | HTMLResponse:
            try:
                values, request_digest = await _form_values(
                    request,
                    csrf_token,
                    allowed_fields=_SUBMIT_FIELDS,
                )
                active = request_session(request)
                if active is None:
                    raise W10StudyWebError("study session is unavailable", status_code=404)
                store, capability, _ = active
                store.complete_session(
                    capability=capability,
                    command_id=UUID(values.get("command_id", "")),
                    expected_revision=int(values.get("expected_revision", "")),
                    request_digest=request_digest,
                )
                return RedirectResponse("/w10", status_code=303)
            except (ValueError, ExpertStudyStorageError) as exc:
                status_code = 409 if isinstance(exc, ExpertStudyConflictError) else 422
                response = page(request, error_message=str(exc))
                response.status_code = status_code
                return response

        @app.post("/w10/corrections", response_model=None)
        async def revise_judgement(
            request: Request,
        ) -> RedirectResponse | HTMLResponse:
            try:
                values, request_digest = await _form_values(
                    request,
                    csrf_token,
                    allowed_fields=_CORRECTION_FIELDS,
                )
                active = request_session(request)
                if active is None:
                    raise W10StudyWebError("study session is unavailable", status_code=404)
                store, capability, _ = active
                state = JudgementState(values.get("state", ""))
                relevance: int | None = None
                confidence: int | None = None
                if state is JudgementState.RATED:
                    relevance = int(values.get("relevance_rating", ""))
                    confidence = int(values.get("confidence", ""))
                failure_value = values.get("failure_category", "")
                failure = QualitativeFailureCategory(failure_value) if failure_value else None
                explanation = _bounded_text(
                    values.get("explanation", ""),
                    field="optional football explanation",
                    limit=1000,
                )
                store.revise_judgement(
                    capability=capability,
                    command_id=UUID(values.get("command_id", "")),
                    expected_revision=int(values.get("expected_revision", "")),
                    request_digest=request_digest,
                    presentation_id=UUID(values.get("presentation_id", "")),
                    state=state,
                    relevance_rating=relevance,
                    confidence=confidence,
                    failure_category=failure,
                    explanation=explanation or None,
                )
                return RedirectResponse("/w10", status_code=303)
            except (ValueError, ExpertStudyStorageError) as exc:
                status_code = 409 if isinstance(exc, ExpertStudyConflictError) else 422
                response = page(request, error_message=str(exc))
                response.status_code = status_code
                return response

        @app.post("/w10/detach", response_model=None)
        async def detach_completed_session(
            request: Request,
        ) -> RedirectResponse | HTMLResponse:
            try:
                await _form_values(
                    request,
                    csrf_token,
                    allowed_fields=_DETACH_FIELDS,
                )
                active = request_session(request)
                if active is None:
                    raise W10StudyWebError("study session is unavailable", status_code=404)
                _, _, snapshot = active
                if not snapshot.complete:
                    raise W10StudyWebError(
                        "an in-progress session remains attached for safe resume",
                        status_code=409,
                    )
                response = RedirectResponse("/w10", status_code=303)
                response.delete_cookie(_CAPABILITY_COOKIE)
                response.delete_cookie(_LANE_COOKIE)
                return response
            except (W10StudyWebError, ExpertStudyStorageError) as exc:
                status_code = exc.status_code if isinstance(exc, W10StudyWebError) else 422
                error_response = page(request, error_message=str(exc))
                error_response.status_code = status_code
                return error_response

    return app


def create_w10_v2_mechanics_pilot_app(
    *,
    store: V2MechanicsPilotStore | None,
    unavailable_reason: str | None = None,
    allow_test_host: bool = False,
) -> FastAPI:
    """Expose only the separate v2 mechanics-pilot lane at ``/w10/v2``.

    There is intentionally no approval endpoint, formal mode, or fallback to a
    v1 store.  The browser receives a comparison only after its opaque per-task
    token has been resolved server-side.
    """
    if store is None and not unavailable_reason:
        raise TypeError("unavailable v2 app requires a reason")
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static/w10-expert-study", StaticFiles(directory=STATIC), name="w10-v2-static")
    templates = Environment(
        loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(("html",))
    )
    csrf = secrets.token_urlsafe(32)
    capability_cookie = "w10_v2_pilot_capability"

    @app.middleware("http")
    async def local_only(request: Request, call_next: Any) -> Response:
        client = request.client.host if request.client is not None else ""
        if not _loopback_host(
            request.headers.get("host", ""), allow_test_host=allow_test_host
        ) or not _loopback_host(client, allow_test_host=allow_test_host):
            response: Response = PlainTextResponse(
                "W10 v2 is available only on a loopback host.", status_code=400
            )
        else:
            response = await call_next(request)
        _security_headers(response)
        response.set_cookie(_CSRF_COOKIE, csrf, httponly=True, samesite="strict", secure=False)
        return response

    def render(name: str, *, status_code: int = 200, **context: object) -> HTMLResponse:
        return HTMLResponse(
            templates.get_template(name).render(
                csrf=csrf,
                shell_heading="Football-expert evidence mechanics pilot",
                shell_lede=(
                    "A local, visible-identity assessment of governed 2017/18 football evidence; "
                    "retrieval provenance remains hidden."
                ),
                shell_home="/w10/v2",
                **context,
            ),
            status_code=status_code,
        )

    def current(request: Request) -> tuple[str, V2StudySnapshot] | None:
        if store is None:
            return None
        capability = request.cookies.get(capability_cookie)
        if not capability:
            return None
        try:
            return capability, store.load_session(capability)
        except ExpertStudyNotFoundError:
            return None

    def page(request: Request, error: str | None = None) -> HTMLResponse:
        if store is None:
            return render(
                "v2_legacy_unavailable.html",
                status_code=503,
                unavailable_reason=unavailable_reason,
            )
        active = current(request)
        if active is None:
            return render(
                "v2_legacy_dashboard.html",
                error_message=error,
                experience_choices=tuple(
                    (item.value, item.value.replace("_", " ").title())
                    for item in ExpertExperienceKind
                ),
            )
        capability, snapshot = active
        task = store.task(capability)
        return render(
            "v2_legacy_participant.html",
            error_message=error,
            snapshot=snapshot,
            task=task,
            review_tasks=store.review_tasks(capability),
            command_id=uuid4(),
        )

    def error_page(request: Request, exc: Exception) -> HTMLResponse:
        response = page(request, str(exc))
        if isinstance(exc, W10StudyWebError):
            response.status_code = exc.status_code
        elif isinstance(exc, ExpertStudyConflictError):
            response.status_code = 409
        else:
            response.status_code = 422
        return response

    @app.get("/", response_model=None)
    def root() -> RedirectResponse:
        return RedirectResponse("/w10/v2", status_code=307)

    @app.get("/w10/v2", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return page(request)

    if store is not None:

        @app.post("/w10/v2/sessions", response_model=None)
        async def start(request: Request) -> Response:
            try:
                fields = {
                    "csrf",
                    "participant_code",
                    "years_experience",
                    "assessed_players_within_window",
                    "conflict_declared",
                    "conflict_note",
                    "voluntary_participation",
                    "local_pseudonymous_storage",
                    "withdrawal_before_submission_understood",
                    "immutable_after_submission_understood",
                    "research_limitations_understood",
                }
                fields.update(f"experience_{item.value}" for item in ExpertExperienceKind)
                values, _ = await _form_values(request, csrf, allowed_fields=frozenset(fields))
                years_text = values.get("years_experience", "")
                if not years_text.isdecimal():
                    raise W10StudyWebError("years of experience must be a whole number")
                capability, _snapshot = store.prepare_session(
                    participant_code=_bounded_text(
                        values.get("participant_code", ""),
                        field="participant pseudonym",
                        limit=32,
                        required=True,
                    ),
                    years_experience=int(years_text),
                    experience_kinds=tuple(
                        item
                        for item in ExpertExperienceKind
                        if _boolean(values, f"experience_{item.value}")
                    ),
                    assessed_players_within_window=_boolean(
                        values, "assessed_players_within_window"
                    ),
                    conflict_declared=_boolean(values, "conflict_declared"),
                    conflict_note=_bounded_text(
                        values.get("conflict_note", ""), field="conflict note", limit=500
                    )
                    or None,
                    consent_items={
                        key: _boolean(values, key)
                        for key in (
                            "voluntary_participation",
                            "local_pseudonymous_storage",
                            "withdrawal_before_submission_understood",
                            "immutable_after_submission_understood",
                            "research_limitations_understood",
                        )
                    },
                )
                response = RedirectResponse("/w10/v2", status_code=303)
                response.set_cookie(
                    capability_cookie, capability, httponly=True, samesite="strict", secure=False
                )
                return response
            except (ValueError, W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

        @app.post("/w10/v2/judgements", response_model=None)
        @app.post("/w10/v2/corrections", response_model=None)
        async def judgement(request: Request) -> Response:
            fields = frozenset(
                {
                    "csrf",
                    "command_id",
                    "expected_revision",
                    "presentation_token",
                    "state",
                    "evidence_sufficiency",
                    "assessment_basis",
                    "relevance_rating",
                    "confidence",
                    "evidence_gap",
                    "citations",
                    "explanation",
                }
            )
            try:
                values, digest = await _form_values(request, csrf, allowed_fields=fields)
                active = current(request)
                if active is None:
                    raise W10StudyWebError("v2 session is unavailable", status_code=404)
                capability, _snapshot = active
                citations = tuple(item for item in values.get("citations", "").split(",") if item)
                store.record(
                    capability=capability,
                    command_id=UUID(values["command_id"]),
                    expected_revision=int(values["expected_revision"]),
                    request_digest=digest,
                    presentation_token=values["presentation_token"],
                    state=JudgementState(values["state"]),
                    evidence_sufficiency=EvidenceSufficiencyV2(values["evidence_sufficiency"]),
                    assessment_basis=AssessmentBasisV2(values["assessment_basis"]),
                    relevance_rating=int(values["relevance_rating"])
                    if values.get("relevance_rating")
                    else None,
                    confidence=int(values["confidence"]) if values.get("confidence") else None,
                    evidence_gap=EvidenceGapV2(values["evidence_gap"])
                    if values.get("evidence_gap")
                    else None,
                    citations=citations,
                    explanation=_bounded_text(
                        values.get("explanation", ""), field="qualitative note", limit=1000
                    )
                    or None,
                )
                return RedirectResponse("/w10/v2", status_code=303)
            except (ValueError, W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

        @app.post("/w10/v2/submit", response_model=None)
        async def submit(request: Request) -> Response:
            try:
                values, digest = await _form_values(
                    request,
                    csrf,
                    allowed_fields=frozenset({"csrf", "command_id", "expected_revision"}),
                )
                active = current(request)
                if active is None:
                    raise W10StudyWebError("v2 session is unavailable", status_code=404)
                store.complete(
                    capability=active[0],
                    command_id=UUID(values["command_id"]),
                    expected_revision=int(values["expected_revision"]),
                    request_digest=digest,
                )
                return RedirectResponse("/w10/v2", status_code=303)
            except (ValueError, W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

        @app.post("/w10/v2/detach", response_model=None)
        async def detach(request: Request) -> Response:
            try:
                await _form_values(request, csrf, allowed_fields=frozenset({"csrf"}))
                active = current(request)
                if active is None:
                    raise W10StudyWebError("v2 session is unavailable", status_code=404)
                if not active[1].complete:
                    raise W10StudyWebError(
                        "an in-progress v2 session remains attached for safe resume",
                        status_code=409,
                    )
                response = RedirectResponse("/w10/v2", status_code=303)
                response.delete_cookie(capability_cookie)
                return response
            except (W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

    return app


_HISTORICAL_ROUTE = "/historical-player-comparison"
_HISTORICAL_CSRF_COOKIE = "historical_comparison_csrf"
_HISTORICAL_CAPABILITY_COOKIE = "historical_comparison_capability"
_POSITION_NAMES = {
    "GK": "Goalkeeper",
    "DF": "Defender",
    "MD": "Midfielder",
    "FW": "Forward",
}
_FAMILY_PRESENTATION: dict[str, dict[str, str]] = {
    "ID-LOC-01": {
        "key": "action_locations",
        "label": "Where recorded actions began",
        "summary": "The distribution of recorded action starting points across nine neutral areas.",
        "can_indicate": "Where this player's recorded on-ball actions tended to begin.",
        "cannot_indicate": (
            "Playing direction, pitch side, action quality, success or tactical intent."
        ),
    },
    "ID-PASS-01": {
        "key": "pass_types",
        "label": "Types of passes attempted",
        "summary": "The mix of recorded pass types among all of the player's pass attempts.",
        "can_indicate": "The relative mix of the recorded pass types shown.",
        "cannot_indicate": "Passing quality, accuracy, difficulty, intent or effectiveness.",
    },
    "ID-DUEL-01": {
        "key": "duel_types",
        "label": "Types of duels contested",
        "summary": "The mix of recorded duel types among all of the player's duels.",
        "can_indicate": "Which kinds of recorded duels made up the player's duel activity.",
        "cannot_indicate": "Duel quality, difficulty, tactical responsibility or effectiveness.",
    },
    "ID-DEFLOC-01": {
        "key": "defensive_locations",
        "label": "Where defensive actions occurred",
        "summary": (
            "Separate neutral-area distributions for defending duels, interceptions and clearances."
        ),
        "can_indicate": "Where the shown defensive actions were recorded.",
        "cannot_indicate": "Playing direction, defensive quality, causal tactics or effectiveness.",
    },
    "ID-SHOTLOC-01": {
        "key": "shot_locations",
        "label": "Where shots were taken",
        "summary": "The distribution of recorded shot starting points across nine neutral areas.",
        "can_indicate": "Where the player's recorded shots began.",
        "cannot_indicate": "Playing direction, chance quality, shot quality or expected outcomes.",
    },
    "ID-GK-01": {
        "key": "goalkeeper_mix",
        "label": "Goalkeeper action mix — not save quality",
        "summary": "Recorded goal-kick, leaving-line and save-attempt involvement.",
        "can_indicate": "The mix and rate of the limited goalkeeper actions shown.",
        "cannot_indicate": "Shots faced, save percentage, shot-stopping quality or effectiveness.",
    },
}
_FAMILY_ID_BY_KEY = {value["key"]: family_id for family_id, value in _FAMILY_PRESENTATION.items()}
_STAT_DEFINITIONS = {
    "Passes per 90": "Recorded pass attempts for each 90 minutes in the evidence.",
    "Accurate passes per 90": "Recorded accurate passes for each 90 minutes in the evidence.",
    "Crosses per 90": "Recorded crosses for each 90 minutes in the evidence.",
    "Smart passes per 90": "Recorded smart-pass actions for each 90 minutes in the evidence.",
    "Shots per 90": "Recorded shots for each 90 minutes in the evidence.",
    "Shots on target per 90": "Recorded shots on target for each 90 minutes in the evidence.",
    "Goals per 90": "Recorded goals for each 90 minutes in the evidence.",
    "Key passes per 90": "Recorded key passes for each 90 minutes in the evidence.",
    "Assists per 90": "Recorded assists for each 90 minutes in the evidence.",
    "Duels per 90": "Recorded duels for each 90 minutes in the evidence.",
    "Duels won per 90": "Recorded duels won for each 90 minutes in the evidence.",
    "Interceptions per 90": "Recorded interceptions for each 90 minutes in the evidence.",
    "Clearances per 90": "Recorded clearances for each 90 minutes in the evidence.",
    "Accelerations per 90": "Recorded acceleration actions for each 90 minutes in the evidence.",
    "Fouls per 90": "Recorded fouls for each 90 minutes in the evidence.",
    "Touches per 90": "Recorded touches for each 90 minutes in the evidence.",
}
_CREDIBILITY_LABELS = {
    0: "Not credible",
    1: "Weakly credible",
    2: "Mixed",
    3: "Credible",
    4: "Strongly credible",
}
_BASIS_LABELS = {
    AssessmentBasisV2.SUPPLIED_EVIDENCE: "The information shown in this form",
    AssessmentBasisV2.PRIOR_PROFESSIONAL_KNOWLEDGE: "My prior professional knowledge",
    AssessmentBasisV2.BOTH: "Both the information shown and my prior knowledge",
    AssessmentBasisV2.UNABLE_TO_ASSESS: "I could not make a fair comparison",
}
_GAP_LABELS = {
    EvidenceGapV2.SPARSE_OPPORTUNITIES: "Too few recorded actions",
    EvidenceGapV2.MISSING_DESCRIPTOR: "A type of playing evidence was missing",
    EvidenceGapV2.COVERAGE_LIMITATION: "The evidence coverage was too limited",
    EvidenceGapV2.CONTEXT_AMBIGUITY: "The playing context was unclear",
    EvidenceGapV2.OTHER: "Another important gap",
}


def _participant_error_message(exc: Exception) -> str:
    if isinstance(exc, W10StudyWebError):
        return str(exc)
    if isinstance(exc, ExpertStudyConflictError):
        return "This page changed after it was opened. Reload it before saving again."
    if isinstance(exc, ExpertStudyNotFoundError):
        return "Your saved local session could not be found on this computer."
    if isinstance(exc, ExpertStudyPreparationError):
        return str(exc)
    if isinstance(exc, (ExpertStudyConfigurationError, ExpertStudyIntegrityError)):
        return "This local form could not be verified. Stop here and contact the operator."
    return "We could not save that step safely. Reload the page and check your answers."


def _participant_player(
    panel: Any, md_subrubric: MdEvidenceSubrubricV2 | None
) -> dict[str, object]:
    position = _POSITION_NAMES[panel.context.position_code]
    if panel.context.position_code == "MD":
        position = (
            "Defensive / ball-winning midfielder"
            if md_subrubric is MdEvidenceSubrubricV2.DEFENSIVE
            else "Attacking / shooting midfielder"
        )
    return {
        "name": panel.context.display_name,
        "season": "2017/18 historical season",
        "competition": panel.context.competition_name,
        "teams": tuple(panel.context.team_names),
        "position": position,
        "minutes": f"{panel.context.quantity.governed_minutes:,.0f} recorded minutes",
        "minutes_note": "",
    }


def _percentile_text(value: float) -> str:
    return f"Higher than around {value:.0f}% of players in the same position"


def _statistic_rows(comparison: Any) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for player_a, player_b in zip(
        comparison.exemplar.w09_inputs.metrics,
        comparison.candidate.w09_inputs.metrics,
        strict=True,
    ):
        if (
            player_a.availability
            not in {EvidenceAvailabilityV2.OBSERVED_VALUE, EvidenceAvailabilityV2.OBSERVED_ZERO}
            or player_b.availability
            not in {EvidenceAvailabilityV2.OBSERVED_VALUE, EvidenceAvailabilityV2.OBSERVED_ZERO}
            or player_a.raw_value is None
            or player_b.raw_value is None
            or player_a.within_position_percentile is None
            or player_b.within_position_percentile is None
        ):
            continue
        rows.append(
            {
                "label": player_a.label,
                "definition": _STAT_DEFINITIONS[player_a.label],
                "player_a_recorded": f"{player_a.raw_value:.2f} per 90",
                "player_a_percentile": _percentile_text(player_a.within_position_percentile),
                "player_b_recorded": f"{player_b.raw_value:.2f} per 90",
                "player_b_percentile": _percentile_text(player_b.within_position_percentile),
            }
        )
    return tuple(rows)


def _evidence_row_label(family_id: str, metric: Any, index: int) -> str:
    if family_id in {"ID-LOC-01", "ID-SHOTLOC-01"}:
        area = (index % 9) + 1
        return f"Neutral map area {area} — row {index // 3 + 1}, column {index % 3 + 1}"
    if family_id == "ID-DEFLOC-01":
        component = ("Defending duels", "Interceptions", "Clearances")[index // 9]
        within_component = index % 9
        return (
            f"{component} — neutral map area {within_component + 1}, "
            f"row {within_component // 3 + 1}, column {within_component % 3 + 1}"
        )
    cleaned = str(metric.label).replace(" share", "")
    return {
        "Hand pass": "Hand passes — recorded provider category",
        "High pass": "High passes",
        "Launch": "Launches",
        "Simple pass": "Simple passes — recorded provider category",
        "Air duel": "Aerial duels",
        "Ground attacking duel": "Attacking ground duels",
        "Ground defending duel": "Defending ground duels",
        "Ground loose-ball duel": "Loose-ball ground duels",
        "Goal kicks per 90": "Goal kicks per 90 recorded minutes",
        "Leaving-line actions per 90": "Leaving-line actions per 90 recorded minutes",
        "Reflex save-attempt": "Reflex-labelled save attempts",
        "Generic save-attempt": "Other recorded save attempts",
    }.get(cleaned, cleaned)


def _additional_evidence(comparison: Any) -> tuple[dict[str, object], ...]:
    exemplar_by_id = {
        family.family_id: family for family in comparison.exemplar.independent_descriptors
    }
    candidate_by_id = {
        family.family_id: family for family in comparison.candidate.independent_descriptors
    }
    useful_order = {
        "GK": ("ID-GK-01", "ID-LOC-01", "ID-PASS-01"),
        "DF": ("ID-DEFLOC-01", "ID-DUEL-01", "ID-LOC-01", "ID-PASS-01"),
        "FW": ("ID-SHOTLOC-01", "ID-LOC-01", "ID-PASS-01", "ID-DUEL-01"),
        "MD_DEFENSIVE": (
            "ID-DEFLOC-01",
            "ID-DUEL-01",
            "ID-LOC-01",
            "ID-PASS-01",
        ),
        "MD_SHOOTING": (
            "ID-SHOTLOC-01",
            "ID-LOC-01",
            "ID-PASS-01",
            "ID-DUEL-01",
        ),
    }
    branch = (
        f"MD_{comparison.md_subrubric.value}"
        if comparison.position_code == "MD"
        else comparison.position_code
    )
    sections: list[dict[str, object]] = []
    for family_id in useful_order[branch]:
        player_a = exemplar_by_id[family_id]
        player_b = candidate_by_id[family_id]
        observed = {EvidenceAvailabilityV2.OBSERVED_VALUE, EvidenceAvailabilityV2.OBSERVED_ZERO}
        if (
            not player_a.mandatory_for_selected_rubric
            or not player_b.mandatory_for_selected_rubric
            or player_a.availability not in observed
            or player_b.availability not in observed
        ):
            continue
        rows: list[dict[str, object]] = []
        for index, (metric_a, metric_b) in enumerate(
            zip(player_a.metrics, player_b.metrics, strict=True)
        ):
            if (
                metric_a.raw_numerator is None
                or metric_b.raw_numerator is None
                or metric_a.raw_value is None
                or metric_b.raw_value is None
            ):
                continue
            if metric_a.unit is EvidenceMetricUnitV2.SHARE:
                player_a_context = f"{metric_a.raw_value * 100:.1f}%"
                player_b_context = f"{metric_b.raw_value * 100:.1f}%"
            else:
                player_a_context = f"{metric_a.raw_value:.2f} per 90"
                player_b_context = f"{metric_b.raw_value:.2f} per 90"
            rows.append(
                {
                    "label": _evidence_row_label(family_id, metric_a, index),
                    "player_a_count": f"{metric_a.raw_numerator:,} recorded",
                    "player_a_percentage": player_a_context,
                    "player_b_count": f"{metric_b.raw_numerator:,} recorded",
                    "player_b_percentage": player_b_context,
                }
            )
        presentation = _FAMILY_PRESENTATION[family_id]
        sections.append(
            {
                **presentation,
                "direction_notice": (
                    "Pitch direction is unavailable. The source does not provide a consistent "
                    "playing direction or pitch side. Area numbers are neutral and must not be "
                    "read as attacking direction."
                    if family_id in {"ID-LOC-01", "ID-DEFLOC-01", "ID-SHOTLOC-01"}
                    else ""
                ),
                "rows": tuple(rows),
            }
        )
    return tuple(sections)


def _task_view(task: tuple[str, Any, int, int], *, resumed: bool) -> dict[str, object]:
    token, comparison, ordinal, total = task
    return {
        "token": token,
        "ordinal": ordinal,
        "total": total,
        "resumed": resumed,
        "player_a": _participant_player(comparison.exemplar, comparison.md_subrubric),
        "player_b": _participant_player(comparison.candidate, comparison.md_subrubric),
        "statistics": _statistic_rows(comparison),
        "evidence_sections": _additional_evidence(comparison),
        "shared_minutes_note": (
            "Recorded minutes are conservative lower bounds. True playing time may be higher, "
            "so per-90 rates can be overstated."
        ),
    }


def _local_timestamp(value: str) -> str:
    timestamp = datetime.fromisoformat(value).astimezone()
    return f"{timestamp.day} {timestamp:%B %Y, %H:%M %Z}"


def _debrief_view(
    debrief: HistoricalComparisonPilotDebriefV1 | None,
) -> dict[str, object] | None:
    if debrief is None:
        return None
    return {
        "names_or_minutes_only": debrief.names_or_minutes_only_for_any_comparison,
        "names_or_minutes_details": debrief.names_or_minutes_only_details or "",
        "position_lacked_evidence": debrief.any_position_lacked_enough_evidence,
        "position_evidence_details": debrief.position_evidence_details or "",
        "interface_unclear": debrief.any_label_chart_warning_or_navigation_unclear,
        "interface_clarity_details": debrief.interface_clarity_details or "",
        "system_preference_revealed": debrief.form_appeared_to_reveal_system_preference,
        "preference_revelation_details": debrief.preference_revelation_details or "",
    }


def _review_view(
    rows: tuple[tuple[str, HistoricalComparisonJudgementV1, int, Any], ...],
) -> tuple[dict[str, object], ...]:
    output: list[dict[str, object]] = []
    for token, judgement, ordinal, comparison in rows:
        sections = _additional_evidence(comparison)
        helped_ids = set(judgement.cited_independent_family_ids)
        helped_sections = tuple(
            section for section in sections if _FAMILY_ID_BY_KEY[str(section["key"])] in helped_ids
        )
        helped_keys = (
            ("statistics",) if judgement.statistics_used_to_find_similar_players_helped else ()
        ) + tuple(str(section["key"]) for section in helped_sections)
        helped_labels = (
            ("Statistics used to find similar players",)
            if judgement.statistics_used_to_find_similar_players_helped
            else ()
        ) + tuple(str(section["label"]) for section in helped_sections)
        output.append(
            {
                "token": token,
                "ordinal": ordinal,
                "command_id": uuid4(),
                "fair_comparison": "yes" if judgement.state is JudgementState.RATED else "no",
                "credibility": judgement.relevance_rating,
                "credibility_label": (
                    _CREDIBILITY_LABELS[judgement.relevance_rating]
                    if judgement.relevance_rating is not None
                    else "No fair judgement recorded"
                ),
                "confidence": judgement.confidence,
                "assessment_basis": judgement.assessment_basis.value,
                "assessment_basis_label": _BASIS_LABELS[judgement.assessment_basis],
                "statistics_helped": (judgement.statistics_used_to_find_similar_players_helped),
                "evidence_sections": sections,
                "helped_keys": helped_keys,
                "helped_labels": helped_labels,
                "important_information_missing": (
                    "yes"
                    if judgement.evidence_sufficiency is EvidenceSufficiencyV2.INSUFFICIENT
                    else "no"
                ),
                "evidence_gap": (
                    judgement.evidence_gap.value if judgement.evidence_gap is not None else ""
                ),
                "evidence_gap_label": (
                    _GAP_LABELS[judgement.evidence_gap]
                    if judgement.evidence_gap is not None
                    else "No important information reported missing"
                ),
                "explanation": judgement.explanation or "",
            }
        )
    return tuple(output)


def create_historical_player_comparison_app(
    *,
    store: HistoricalComparisonPilotStore | None,
    unavailable_reason: str | None = None,
    allow_test_host: bool = False,
) -> FastAPI:
    """Expose the self-contained participant journey on one friendly local route."""

    if store is None and not unavailable_reason:
        raise TypeError("unavailable participant form requires a reason")
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.mount(
        "/static/historical-player-comparison",
        StaticFiles(directory=STATIC),
        name="historical-player-comparison-static",
    )
    templates = Environment(
        loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(("html",))
    )
    csrf = secrets.token_urlsafe(32)

    @app.middleware("http")
    async def local_only(request: Request, call_next: Any) -> Response:
        client = request.client.host if request.client is not None else ""
        if not _loopback_host(
            request.headers.get("host", ""), allow_test_host=allow_test_host
        ) or not _loopback_host(client, allow_test_host=allow_test_host):
            response: Response = PlainTextResponse(
                "Historical player comparison is available only on this computer.",
                status_code=400,
            )
        else:
            response = await call_next(request)
        _security_headers(response)
        response.set_cookie(
            _HISTORICAL_CSRF_COOKIE,
            csrf,
            httponly=True,
            samesite="strict",
            secure=False,
        )
        return response

    def render(name: str, *, status_code: int = 200, **context: object) -> HTMLResponse:
        return HTMLResponse(
            templates.get_template(name).render(csrf=csrf, **context),
            status_code=status_code,
        )

    def current(request: Request) -> tuple[str, HistoricalComparisonStudySnapshot] | None:
        if store is None:
            return None
        capability = request.cookies.get(_HISTORICAL_CAPABILITY_COOKIE)
        if not capability:
            return None
        try:
            return capability, store.load_session(capability)
        except ExpertStudyNotFoundError:
            return None

    def page(
        request: Request,
        error: str | None = None,
        *,
        invalid_field: str | None = None,
    ) -> HTMLResponse:
        if store is None:
            return render(
                "v2_unavailable.html",
                status_code=503,
                unavailable_reason=(
                    "The local comparison form has not been prepared. Please contact the operator."
                    if unavailable_reason
                    else "The local comparison form is unavailable."
                ),
            )
        active = current(request)
        if active is None:
            return render(
                "v2_dashboard.html",
                error_message=error,
                invalid_field=invalid_field,
                experience_choices=tuple(
                    (item.value, item.value.replace("_", " ").title())
                    for item in ExpertExperienceKind
                ),
            )
        capability, snapshot = active
        task = store.task(capability)
        receipt_view = (
            {
                "submitted_at": _local_timestamp(snapshot.completed_at),
                "comparison_count": len(snapshot.presentation_tokens),
                "total": len(snapshot.presentation_tokens),
                "participant_code_masked": "Kept private after entry",
                "immutable": True,
                "storage_note": "Saved pseudonymously on this computer.",
            }
            if snapshot.complete and snapshot.completed_at is not None
            else None
        )
        return render(
            "v2_participant.html",
            error_message=error,
            snapshot=snapshot,
            task_view=(
                _task_view(task, resumed=snapshot.revision > 0) if task is not None else None
            ),
            review_rows=_review_view(store.review_tasks(capability)),
            debrief_view=_debrief_view(snapshot.debrief),
            receipt_view=receipt_view,
            command_id=uuid4(),
            debrief_command_id=uuid4(),
            submission_command_id=uuid4(),
        )

    def error_page(request: Request, exc: Exception) -> HTMLResponse:
        invalid_field = (
            "years_experience"
            if isinstance(exc, W10StudyWebError) and "years of experience" in str(exc).casefold()
            else None
        )
        response = page(
            request,
            _participant_error_message(exc),
            invalid_field=invalid_field,
        )
        response.status_code = (
            exc.status_code
            if isinstance(exc, W10StudyWebError)
            else 409
            if isinstance(exc, ExpertStudyConflictError)
            else 404
            if isinstance(exc, ExpertStudyNotFoundError)
            else 422
        )
        return response

    async def form(request: Request, allowed_fields: frozenset[str]) -> tuple[dict[str, str], str]:
        return await _form_values(
            request,
            csrf,
            allowed_fields=allowed_fields,
            csrf_cookie_name=_HISTORICAL_CSRF_COOKIE,
        )

    @app.get("/", response_model=None)
    def root() -> RedirectResponse:
        return RedirectResponse(_HISTORICAL_ROUTE, status_code=307)

    @app.get("/favicon.ico", response_model=None)
    def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/w10/v2", response_model=None)
    def legacy() -> RedirectResponse:
        return RedirectResponse(_HISTORICAL_ROUTE, status_code=307)

    @app.get(_HISTORICAL_ROUTE, response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return page(request)

    if store is not None:

        @app.post(f"{_HISTORICAL_ROUTE}/sessions", response_model=None)
        async def start(request: Request) -> Response:
            fields = {
                "csrf",
                "participant_code",
                "years_experience",
                "assessed_players_within_window",
                "conflict_declared",
                "conflict_note",
                "voluntary_participation",
                "local_pseudonymous_storage",
                "withdrawal_before_submission_understood",
                "immutable_after_submission_understood",
                "research_limitations_understood",
            }
            fields.update(f"experience_{item.value}" for item in ExpertExperienceKind)
            try:
                values, _digest = await form(request, frozenset(fields))
                years_text = values.get("years_experience", "")
                if not years_text.isdecimal():
                    raise W10StudyWebError("Enter years of experience as a whole number.")
                capability, _snapshot = store.prepare_session(
                    participant_code=_bounded_text(
                        values.get("participant_code", ""),
                        field="Pseudonym",
                        limit=32,
                        required=True,
                    ),
                    years_experience=int(years_text),
                    experience_kinds=tuple(
                        item
                        for item in ExpertExperienceKind
                        if _boolean(values, f"experience_{item.value}")
                    ),
                    assessed_players_within_window=_boolean(
                        values, "assessed_players_within_window"
                    ),
                    conflict_declared=_boolean(values, "conflict_declared"),
                    conflict_note=_bounded_text(
                        values.get("conflict_note", ""), field="Conflict note", limit=500
                    )
                    or None,
                    consent_items={
                        key: _boolean(values, key)
                        for key in (
                            "voluntary_participation",
                            "local_pseudonymous_storage",
                            "withdrawal_before_submission_understood",
                            "immutable_after_submission_understood",
                            "research_limitations_understood",
                        )
                    },
                )
                response = RedirectResponse(_HISTORICAL_ROUTE, status_code=303)
                response.set_cookie(
                    _HISTORICAL_CAPABILITY_COOKIE,
                    capability,
                    httponly=True,
                    samesite="strict",
                    secure=False,
                )
                return response
            except (ValueError, W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

        response_fields = frozenset(
            {
                "csrf",
                "command_id",
                "expected_revision",
                "presentation_token",
                "fair_comparison",
                "credibility",
                "confidence",
                "assessment_basis",
                "helped_statistics",
                "important_information_missing",
                "evidence_gap",
                "explanation",
                *(f"helped_{key}" for key in _FAMILY_ID_BY_KEY),
            }
        )

        @app.post(f"{_HISTORICAL_ROUTE}/responses", response_model=None)
        @app.post(f"{_HISTORICAL_ROUTE}/corrections", response_model=None)
        async def response(request: Request) -> Response:
            try:
                values, request_digest = await form(request, response_fields)
                active = current(request)
                if active is None:
                    raise W10StudyWebError(
                        "Your saved local session is unavailable.", status_code=404
                    )
                fair = values.get("fair_comparison")
                missing = values.get("important_information_missing")
                if fair not in {"yes", "no"} or missing not in {"yes", "no"}:
                    raise W10StudyWebError(
                        "Answer whether a fair comparison was possible and whether "
                        "information was missing."
                    )
                if (fair == "yes") != (missing == "no"):
                    raise W10StudyWebError(
                        "A rated comparison needs enough information. If important information "
                        "was missing, choose that you could not make a fair judgement."
                    )
                if fair == "yes":
                    state = JudgementState.RATED
                    sufficiency = EvidenceSufficiencyV2.SUFFICIENT
                    basis = AssessmentBasisV2(values.get("assessment_basis", ""))
                    if basis is AssessmentBasisV2.UNABLE_TO_ASSESS:
                        raise W10StudyWebError("Choose what you based the fair comparison on.")
                    credibility = int(values.get("credibility", ""))
                    confidence = int(values.get("confidence", ""))
                    gap = None
                else:
                    state = JudgementState.UNABLE_TO_ASSESS
                    sufficiency = EvidenceSufficiencyV2.INSUFFICIENT
                    basis = AssessmentBasisV2.UNABLE_TO_ASSESS
                    credibility = None
                    confidence = None
                    gap = EvidenceGapV2(values.get("evidence_gap", ""))
                citation_ids = tuple(
                    family_id
                    for key, family_id in _FAMILY_ID_BY_KEY.items()
                    if _boolean(values, f"helped_{key}")
                )
                store.record(
                    capability=active[0],
                    command_id=UUID(values["command_id"]),
                    expected_revision=int(values["expected_revision"]),
                    request_digest=request_digest,
                    presentation_token=values["presentation_token"],
                    state=state,
                    evidence_sufficiency=sufficiency,
                    assessment_basis=basis,
                    relevance_rating=credibility,
                    confidence=confidence,
                    evidence_gap=gap,
                    citation_family_ids=citation_ids,
                    statistics_helped=_boolean(values, "helped_statistics"),
                    explanation=_bounded_text(
                        values.get("explanation", ""),
                        field="Explanation",
                        limit=1000,
                    )
                    or None,
                )
                return RedirectResponse(_HISTORICAL_ROUTE, status_code=303)
            except (ValueError, W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

        debrief_fields = frozenset(
            {
                "csrf",
                "command_id",
                "expected_revision",
                "names_or_minutes_only",
                "names_or_minutes_details",
                "position_lacked_evidence",
                "position_evidence_details",
                "interface_unclear",
                "interface_clarity_details",
                "system_preference_revealed",
                "preference_revelation_details",
            }
        )

        @app.post(f"{_HISTORICAL_ROUTE}/form-feedback", response_model=None)
        async def pilot_feedback(request: Request) -> Response:
            try:
                values, request_digest = await form(request, debrief_fields)
                active = current(request)
                if active is None:
                    raise W10StudyWebError(
                        "Your saved local session is unavailable.", status_code=404
                    )

                def answer(name: str) -> bool:
                    value = values.get(name)
                    if value not in {"yes", "no"}:
                        raise W10StudyWebError(
                            "Answer every form-feedback question with Yes or No."
                        )
                    return value == "yes"

                def details(name: str, required: bool) -> str | None:
                    value = _bounded_text(
                        values.get(name, ""), field="Pilot feedback explanation", limit=1000
                    )
                    if required and not value:
                        raise W10StudyWebError("Explain each form-feedback answer marked Yes.")
                    if not required and value:
                        raise W10StudyWebError("Leave the explanation blank when the answer is No.")
                    return value or None

                names_only = answer("names_or_minutes_only")
                position_gap = answer("position_lacked_evidence")
                unclear = answer("interface_unclear")
                preference = answer("system_preference_revealed")
                store.record_debrief(
                    capability=active[0],
                    command_id=UUID(values["command_id"]),
                    expected_revision=int(values["expected_revision"]),
                    request_digest=request_digest,
                    names_or_minutes_only=names_only,
                    names_or_minutes_details=details("names_or_minutes_details", names_only),
                    position_lacked_evidence=position_gap,
                    position_evidence_details=details("position_evidence_details", position_gap),
                    interface_unclear=unclear,
                    interface_clarity_details=details("interface_clarity_details", unclear),
                    system_preference_revealed=preference,
                    preference_revelation_details=details(
                        "preference_revelation_details", preference
                    ),
                )
                return RedirectResponse(_HISTORICAL_ROUTE, status_code=303)
            except (ValueError, W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

        @app.post(f"{_HISTORICAL_ROUTE}/submit", response_model=None)
        async def submit(request: Request) -> Response:
            try:
                values, request_digest = await form(
                    request, frozenset({"csrf", "command_id", "expected_revision"})
                )
                active = current(request)
                if active is None:
                    raise W10StudyWebError(
                        "Your saved local session is unavailable.", status_code=404
                    )
                store.complete(
                    capability=active[0],
                    command_id=UUID(values["command_id"]),
                    expected_revision=int(values["expected_revision"]),
                    request_digest=request_digest,
                )
                return RedirectResponse(_HISTORICAL_ROUTE, status_code=303)
            except (ValueError, W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

        @app.post(f"{_HISTORICAL_ROUTE}/detach", response_model=None)
        async def detach(request: Request) -> Response:
            try:
                await form(request, frozenset({"csrf"}))
                active = current(request)
                if active is None:
                    raise W10StudyWebError(
                        "Your saved local session is unavailable.", status_code=404
                    )
                if not active[1].complete:
                    raise W10StudyWebError(
                        "Your unfinished session stays attached so it can be resumed safely.",
                        status_code=409,
                    )
                response = RedirectResponse(_HISTORICAL_ROUTE, status_code=303)
                response.delete_cookie(_HISTORICAL_CAPABILITY_COOKIE)
                return response
            except (W10StudyWebError, ExpertStudyStorageError) as exc:
                return error_page(request, exc)

    return app


__all__ = [
    "W10StudyWebError",
    "create_historical_player_comparison_app",
    "create_w10_expert_study_app",
    "create_w10_v2_mechanics_pilot_app",
]

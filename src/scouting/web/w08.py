# ruff: noqa: E501
"""Loopback-only W08 local workflow composition.

This is deliberately a small server-rendered surface: all state transitions remain
in the R1 services, and every fixture emitted by ``seed_synthetic_accounts`` is
explicitly synthetic automated-test material rather than participant evidence.
"""

from __future__ import annotations

import json
import secrets
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qs, urlsplit
from uuid import UUID, uuid4, uuid5

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from scouting.audit.ledger import AuditIntegrityError, AuditLedger
from scouting.contracts import (
    ConstraintOperator,
    LocalEvidenceReference,
    LocalEvidenceReferenceKind,
    M0ResolvedQuery,
    M0ResolvedResponsibilityWeight,
    PinnedM0ServingRequest,
    R1RoleBriefStatus,
    R1RoleBriefVersion,
    R1ShortlistEntryRevision,
    ReplayableRetrievalLink,
    RoleBriefRejectionReason,
    RoleConstraint,
    RolePreference,
    ScoutObservationVersion,
    ScoutRubricDimension,
    ScoutRubricDimensionName,
    ShortlistComment,
    ShortlistEntryState,
    ShortlistHoldReason,
    ShortlistRejectionReason,
    TenantContext,
    WorkflowEvidenceOrigin,
    WorkflowVisibility,
)
from scouting.observations import ScoutObservationService
from scouting.policy import (
    LocalRole,
    LocalSessionService,
    R1AuthenticationDenied,
    R1AuthorizationDenied,
    R1AuthorizationPolicy,
    R1Principal,
    R1Resource,
)
from scouting.storage import GuardedStorage
from scouting.storage.embedded import create_embedded_engine
from scouting.web.w07 import _core as w07_core
from scouting.web.w07 import default_request as w07_default_request
from scouting.workflow import (
    EvidenceExportDenied,
    EvidenceExportIntegrityError,
    LocalEvidenceExporter,
    R1WorkflowService,
    WorkflowConflict,
)
from scouting.workflow.r1 import entry_transition_actions

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "apps/web/templates/w08"
STATIC = ROOT / "apps/web/static/w08"
_BOUNDARY = "NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE — resemblance_only; synthetic_development_only; LIMITED; no_recommendation_evidence."
_W08_REPLAY_NAMESPACE = UUID("d943ada6-4642-59b6-bb6f-bacdcf247d72")
_GUIDED_ROLES = (
    ("analyst", "Analyst", "Create briefs, retrieval links and shortlists"),
    ("approver", "Approver", "Approve briefs and record meeting decisions"),
    ("scout", "Scout", "Complete structured review and disagreement"),
    ("admin", "Admin", "Inspect audit evidence and denied export paths"),
)


def _now() -> datetime:
    return datetime.now(UTC)


def _redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def _validated_study_console_url(value: str | None) -> str | None:
    """Accept only an explicit loopback console link for the guided pilot surface."""
    if value is None:
        return None
    parsed = urlsplit(value)
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("invalid guided study console URL") from error
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or port is None
        or not 1024 <= port <= 65535
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith("/participants/W08-P")
    ):
        raise ValueError("invalid guided study console URL")
    return value.rstrip("/")


def _guided_return_path(value: str | None) -> str:
    """Keep pilot role-switch redirects inside the local W08 application."""
    candidate = value or "/w08/guide"
    if (
        not candidate.startswith("/w08")
        or candidate.startswith("//")
        or "\r" in candidate
        or "\n" in candidate
        or urlsplit(candidate).scheme
        or urlsplit(candidate).netloc
    ):
        return "/w08/guide"
    return candidate


def _role_briefs_for_links(
    connection: Connection,
    links: Sequence[RowMapping],
    *,
    tenant_id: UUID,
) -> dict[tuple[str, int], RowMapping]:
    """Load every exact link-bound brief revision in one deterministic query."""

    keys = tuple(
        sorted(
            {
                (
                    str(link["role_brief_id"]),
                    int(cast(Any, link["role_brief_version"])),
                )
                for link in links
            }
        )
    )
    if not keys:
        return {}
    values = ",".join(f"(:brief_{index}, :version_{index})" for index in range(len(keys)))
    parameters: dict[str, object] = {"tenant": str(tenant_id)}
    for index, (brief_id, version) in enumerate(keys):
        parameters[f"brief_{index}"] = brief_id
        parameters[f"version_{index}"] = version
    rows = (
        connection.execute(
            text(
                # Interpolation contains generated bind labels only; values stay parameterized.
                "WITH requested(role_brief_id, version) AS (VALUES "  # nosec B608
                f"{values}) SELECT r.* FROM role_brief_revisions r "
                "JOIN requested q ON q.role_brief_id=r.role_brief_id "
                "AND q.version=r.version WHERE r.tenant_id=:tenant"
            ),
            parameters,
        )
        .mappings()
        .all()
    )
    return {(str(row["role_brief_id"]), int(cast(Any, row["version"]))): row for row in rows}


def seed_synthetic_accounts(
    engine: Engine, sessions: LocalSessionService
) -> dict[str, dict[str, str]]:
    """Create a fresh local-only synthetic persona set; return credentials only in memory."""
    tenant = uuid4()
    personas: dict[str, dict[str, str]] = {}
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tenants (tenant_id,slug,display_name,created_at) VALUES (:id,:slug,:name,:at)"
            ),
            {
                "id": tenant,
                "slug": f"w08-{tenant.hex}",
                "name": "Synthetic automated-study tenant",
                "at": _now(),
            },
        )
        for role in LocalRole:
            actor = uuid4()
            password = secrets.token_urlsafe(24)
            sessions.create_account(
                connection,
                actor_id=actor,
                tenant_id=tenant,
                display_name=f"Synthetic automated test {role.value}",
                password=password,
                roles=(role,),
                assigned_by=actor,
            )
            personas[role.value] = {
                "actor_id": str(actor),
                "password": password,
                "tenant_id": str(tenant),
            }
    return personas


def create_w08_app(
    *,
    evidence_origin: WorkflowEvidenceOrigin,
    database_path: Path | None = None,
    allowed_root: Path | None = None,
    seed: bool = True,
    guided_study: bool = False,
    study_console_url: str | None = None,
) -> FastAPI:
    """Create an app with a caller-declared, server-controlled evidence origin."""
    if guided_study and not seed:
        raise ValueError("guided study mode requires fresh synthetic personas")
    guided_console = _validated_study_console_url(study_console_url)
    if guided_study and guided_console is None:
        raise ValueError("guided study mode requires a loopback Study Console URL")
    root = allowed_root or ROOT
    path = database_path or (root / "data/working/w08-local.sqlite3")
    engine = create_embedded_engine(path, allowed_root=root)
    sessions = LocalSessionService(token_key=secrets.token_bytes(32))
    policy = R1AuthorizationPolicy()
    workflow = R1WorkflowService(policy=policy)
    observations = ScoutObservationService(policy=policy)
    storage = GuardedStorage({"evidence_packs": root / "data/working/w08-evidence-packs"})
    exporter = LocalEvidenceExporter(storage)
    audit_ledger = AuditLedger()
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.engine, app.state.sessions = engine, sessions
    app.state.workflow_evidence_origin = evidence_origin
    app.state.synthetic_personas = seed_synthetic_accounts(engine, sessions) if seed else {}
    app.state.guided_study = guided_study
    app.state.study_console_url = guided_console
    guided_switch_token = secrets.token_urlsafe(32)
    app.mount("/static/w08", StaticFiles(directory=STATIC), name="w08-static")
    templates = Environment(
        loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(("html",))
    )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_: Request, __: RequestValidationError) -> HTMLResponse:
        return HTMLResponse("Action unavailable", status_code=404)

    @app.exception_handler(ValueError)
    async def invalid_form(request: Request, _: ValueError) -> HTMLResponse:
        return denied(request)

    @app.middleware("http")
    async def headers(request: Request, call_next: Any) -> Any:
        if request.url.hostname not in {"testserver", "127.0.0.1", "localhost", None}:
            return HTMLResponse("not found", status_code=404)
        response = await call_next(request)
        response.headers.update(
            {
                "Content-Security-Policy": "default-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
                "Cache-Control": "no-store",
                "Referrer-Policy": "no-referrer",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            }
        )
        if guided_study:
            response.set_cookie(
                "w08_guide_csrf",
                guided_switch_token,
                httponly=True,
                samesite="strict",
                secure=False,
                path="/w08",
            )
        return response

    def principal(
        request: Request, *, csrf_token: str | None = None, csrf_required: bool = False
    ) -> R1Principal:
        token = request.cookies.get("w08_session", "")
        csrf_value = request.headers.get("x-csrf-token") or request.cookies.get("w08_csrf")
        with engine.begin() as connection:
            return sessions.authenticate(
                connection,
                token=token,
                csrf_token=csrf_token if csrf_required else csrf_value,
                require_csrf=csrf_required,
            )

    def page(request: Request, name: str, **context: Any) -> HTMLResponse:
        guided_role_actor_ids = {
            role: str(persona["actor_id"])
            for role, persona in app.state.synthetic_personas.items()
            if isinstance(persona, dict) and "actor_id" in persona
        }
        return HTMLResponse(
            templates.get_template(name).render(
                request=request,
                boundary=_BOUNDARY,
                csrf=request.cookies.get("w08_csrf", ""),
                guided_study=guided_study,
                guided_roles=_GUIDED_ROLES,
                guided_switch_token=guided_switch_token,
                guided_role_actor_ids=guided_role_actor_ids,
                study_console_url=guided_console,
                **context,
            )
        )

    def denied(request: Request, status: int = 403) -> HTMLResponse:
        response = page(
            request,
            "error.html",
            title="Action unavailable",
            message="The requested action is unavailable for this local session.",
        )
        response.status_code = status
        return response

    async def form_values(request: Request) -> dict[str, str]:
        """Parse bounded urlencoded local forms without adding multipart support."""
        content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
        if content_type != "application/x-www-form-urlencoded":
            raise ValueError("unsupported local form media type")
        limit = 64 * 1024
        declared = request.headers.get("content-length")
        if declared is not None and (not declared.isdecimal() or int(declared) > limit):
            raise ValueError("oversized local form")
        chunks: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            # Reject the next chunk before retaining it.  This keeps the in-memory
            # accumulation bounded even when a peer lies about Content-Length or
            # sends a chunked body.
            if len(chunk) > limit - size:
                raise ValueError("oversized local form")
            size += len(chunk)
            chunks.append(chunk)
        raw = b"".join(chunks).decode("utf-8", "strict")
        if size > limit:
            raise ValueError("oversized local form")
        parsed = parse_qs(raw, keep_blank_values=True, strict_parsing=False)
        return {key: values[-1] for key, values in parsed.items() if values}

    def retained_brief_options() -> dict[str, object]:
        """Expose only the public W07 request inputs retained by local W08 forms."""
        request = w07_default_request()
        query = request.resolved_query
        return {
            "template_id": "w08-local-template",
            "taxonomy_id": str(query.taxonomy_id),
            "taxonomy_version": str(query.taxonomy_version),
            "responsibilities": tuple(str(code) for code in query.responsibilities),
            "preference_weights": ("0.5", "1.0"),
            "constraint_field": "synthetic_age_years",
            "constraint_operator": ConstraintOperator.AT_MOST.value,
            "constraint_values": ("40",),
            "exemplar_player_ids": (str(query.query_player_id),),
        }

    def can_read_brief(current: R1Principal, row: Any) -> bool:
        """Apply all explicit brief grants without treating scout as an override.

        `role_brief.read` is the normal analyst/approver grant.  The narrowly
        scoped scout grant is a separate fallback and only applies to an approved
        latest revision.  This is deliberately shared by the queue and direct
        detail route so the two projections cannot drift apart.
        """
        resource = R1Resource(
            current.tenant_id,
            UUID(str(row["owner_id"])),
            str(row["visibility"]),
        )
        if policy.authorize(current, action="role_brief.read", resource=resource):
            return True
        return str(row["status"]) == "approved" and policy.authorize(
            current, action="role_brief.read_approved", resource=resource
        )

    def can_read_retrieval_link(
        current: R1Principal, connection: Connection, link: Any, brief: Any
    ) -> bool:
        """Require one applicable explicit grant for this exact replay link.

        Scout access is intentionally stricter than the generic R1 resource
        helper: it needs a *current latest* shortlist-entry assignment reached
        through this link, rather than ownership or tenant membership alone.
        """
        resource = R1Resource(
            current.tenant_id,
            UUID(str(link["created_by"])),
            str(brief["visibility"]),
        )
        if policy.authorize(current, action="retrieval_link.read_owned", resource=resource):
            return True
        if policy.authorize(current, action="retrieval_link.read", resource=resource):
            return True
        assignments = (
            connection.execute(
                text(
                    """SELECT s.owner_id,s.visibility,r.assigned_scout_id
                    FROM shortlist_entry_workflows e
                    JOIN workflow_shortlists s
                      ON s.shortlist_id=e.shortlist_id AND s.tenant_id=e.tenant_id
                    JOIN shortlist_entry_revisions r
                      ON r.shortlist_entry_id=e.shortlist_entry_id
                     AND r.revision=e.latest_revision
                    WHERE e.tenant_id=:tenant AND r.retrieval_link_id=:link
                      AND r.assigned_scout_id=:actor"""
                ),
                {
                    "tenant": current.tenant_id,
                    "link": link["retrieval_link_id"],
                    "actor": current.actor_id,
                },
            )
            .mappings()
            .all()
        )
        return any(
            policy.authorize(
                current,
                action="retrieval_link.read_assigned",
                resource=R1Resource(
                    current.tenant_id,
                    UUID(str(assignment["owner_id"])),
                    str(assignment["visibility"]),
                    frozenset({current.actor_id}),
                ),
            )
            for assignment in assignments
        )

    def parse_brief_form(
        form: dict[str, str],
    ) -> tuple[tuple[str, ...], tuple[Any, ...], tuple[Any, ...], tuple[UUID, ...]]:
        options = retained_brief_options()
        responsibility_options = cast(tuple[str, ...], options["responsibilities"])
        constraint_values = cast(tuple[str, ...], options["constraint_values"])
        preference_weights = cast(tuple[str, ...], options["preference_weights"])
        exemplar_options = cast(tuple[str, ...], options["exemplar_player_ids"])
        responsibilities = tuple(
            part.strip()
            for part in form.get("responsibilities", form.get("responsibility", "")).split(",")
            if part.strip()
        )
        if not responsibilities or any(
            responsibility not in responsibility_options for responsibility in responsibilities
        ):
            raise ValueError("at least one responsibility is required")
        constraints: tuple[Any, ...] = ()
        if any(form.get(f"constraint_{key}", "").strip() for key in ("field", "operator", "value")):
            if (
                form.get("constraint_field", "").strip() != options["constraint_field"]
                or form.get("constraint_operator", "").strip() != options["constraint_operator"]
                or form.get("constraint_value", "").strip() not in constraint_values
            ):
                raise ValueError("unsupported local constraint")
            constraints = (
                RoleConstraint(
                    field=form["constraint_field"].strip(),
                    operator=ConstraintOperator(form["constraint_operator"].strip()),
                    value=form["constraint_value"].strip(),
                ),
            )
        preferences: tuple[Any, ...] = ()
        if (
            form.get("preference_dimension", "").strip()
            or form.get("preference_weight", "").strip()
        ):
            if (
                form.get("preference_dimension", "").strip() not in responsibility_options
                or form.get("preference_weight", "").strip() not in preference_weights
            ):
                raise ValueError("unsupported retained preference")
            preferences = (
                RolePreference(
                    dimension=form["preference_dimension"].strip(),
                    weight=float(form["preference_weight"]),
                ),
            )
        exemplars = tuple(
            UUID(part.strip())
            for part in form.get("exemplar_player_ids", "").split(",")
            if part.strip()
        )
        if any(str(exemplar) not in exemplar_options for exemplar in exemplars):
            raise ValueError("unsupported retained exemplar")
        return responsibilities, constraints, preferences, exemplars

    @app.get("/", response_class=HTMLResponse)
    @app.get("/w08", response_class=HTMLResponse)
    def landing(request: Request) -> HTMLResponse:
        return page(
            request,
            "landing.html",
            title="Local R1 scouting workflow",
            personas=app.state.synthetic_personas,
        )

    def session_response(*, actor_id: str, password: str, return_to: str) -> RedirectResponse:
        with engine.begin() as connection:
            token, csrf = sessions.login(
                connection,
                actor_id=UUID(actor_id),
                password=password,
                ttl=timedelta(hours=8),
            )
        response = _redirect(return_to)
        response.set_cookie(
            "w08_session", token, httponly=True, samesite="strict", secure=False, path="/w08"
        )
        response.set_cookie(
            "w08_csrf", csrf, httponly=False, samesite="strict", secure=False, path="/w08"
        )
        return response

    @app.post("/w08/login", response_model=None)
    async def login(request: Request) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            actor = UUID(form.get("actor_id", ""))
            response = session_response(
                actor_id=str(actor),
                password=str(form.get("password", "")),
                return_to="/w08/queue",
            )
        except (ValueError, R1AuthenticationDenied):
            return denied(request, 401)
        return response

    @app.post("/w08/guide/switch-role", response_model=None)
    async def guided_switch_role(request: Request) -> RedirectResponse | HTMLResponse:
        if not guided_study:
            return denied(request, 404)
        form = await form_values(request)
        submitted_token = form.get("guide_csrf", "")
        cookie_token = request.cookies.get("w08_guide_csrf", "")
        if not (
            submitted_token
            and cookie_token
            and secrets.compare_digest(submitted_token, guided_switch_token)
            and secrets.compare_digest(cookie_token, guided_switch_token)
        ):
            return denied(request)
        persona = app.state.synthetic_personas.get(form.get("role", ""))
        if not isinstance(persona, dict):
            return denied(request)
        try:
            previous = principal(request)
        except R1AuthenticationDenied:
            previous = None
        if previous is not None:
            with engine.begin() as connection:
                sessions.revoke(connection, session_id=previous.session_id)
        try:
            return session_response(
                actor_id=str(persona["actor_id"]),
                password=str(persona["password"]),
                return_to=_guided_return_path(form.get("return_to")),
            )
        except (KeyError, ValueError, R1AuthenticationDenied):
            return denied(request)

    @app.get("/w08/guide", response_class=HTMLResponse, response_model=None)
    def guided_journey(request: Request) -> HTMLResponse | RedirectResponse:
        if not guided_study:
            return denied(request, 404)
        try:
            current = principal(request)
        except R1AuthenticationDenied:
            return _redirect("/w08")
        return page(
            request,
            "guide.html",
            title="Guided pilot journey",
            principal=current,
        )

    @app.post("/w08/logout")
    async def logout(request: Request) -> RedirectResponse:
        try:
            form = await form_values(request)
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            with engine.begin() as connection:
                sessions.revoke(connection, session_id=current.session_id)
        except R1AuthenticationDenied:
            pass
        response = _redirect("/w08")
        response.delete_cookie("w08_session", path="/w08")
        response.delete_cookie("w08_csrf", path="/w08")
        return response

    @app.get("/w08/queue", response_class=HTMLResponse)
    def queue(request: Request) -> HTMLResponse:
        try:
            current = principal(request)
        except R1AuthenticationDenied:
            return denied(request, 401)
        with engine.connect() as connection:
            briefs = (
                connection.execute(
                    text(
                        "SELECT w.role_brief_id,w.lock_version,w.owner_id,w.visibility,r.version,r.status,r.title FROM role_brief_workflows w JOIN role_brief_revisions r ON r.role_brief_id=w.role_brief_id AND r.version=w.latest_version WHERE w.tenant_id=:tenant ORDER BY w.updated_at DESC"
                    ),
                    {"tenant": current.tenant_id},
                )
                .mappings()
                .all()
            )
            entries = (
                connection.execute(
                    text(
                        """SELECT e.shortlist_entry_id,e.lock_version,r.revision,r.state,r.assigned_scout_id,
                        s.owner_id,s.visibility FROM shortlist_entry_workflows e
                        JOIN workflow_shortlists s ON s.shortlist_id=e.shortlist_id AND s.tenant_id=e.tenant_id
                        JOIN shortlist_entry_revisions r ON r.shortlist_entry_id=e.shortlist_entry_id AND r.revision=e.latest_revision
                        WHERE e.tenant_id=:tenant ORDER BY e.updated_at DESC"""
                    ),
                    {"tenant": current.tenant_id},
                )
                .mappings()
                .all()
            )
        briefs = [row for row in briefs if can_read_brief(current, row)]
        entries = [row for row in entries if can_read_entry(current, row)]
        return page(
            request,
            "queue.html",
            title="Work queue",
            principal=current,
            briefs=briefs,
            entries=entries,
            brief_options=retained_brief_options(),
        )

    @app.post("/w08/briefs", response_model=None)
    async def create_brief(request: Request) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
        except R1AuthenticationDenied:
            return denied(request, 401)
        brief_id = uuid4()
        now = _now()
        try:
            responsibilities, constraints, preferences, exemplars = parse_brief_form(form)
            brief = R1RoleBriefVersion(
                role_brief_id=brief_id,
                tenant_context=TenantContext(tenant_id=current.tenant_id),
                version=1,
                trace_id=uuid4(),
                owner_id=current.actor_id,
                created_by=current.actor_id,
                visibility=WorkflowVisibility.TEAM,
                title=str(form.get("title", "Synthetic role brief")),
                template_id=str(retained_brief_options()["template_id"]),
                taxonomy_version=str(retained_brief_options()["taxonomy_version"]),
                status=R1RoleBriefStatus.DRAFT,
                responsibilities=responsibilities,
                hard_constraints=constraints,
                preferences=preferences,
                exemplar_player_ids=exemplars,
                transition_reason="local user-created draft; workflow mechanics only",
                created_at=now,
            )
            with engine.begin() as connection:
                workflow.create_role_brief(
                    connection, principal=current, brief=brief, request_id=uuid4()
                )
        except (ValueError, WorkflowConflict, R1AuthorizationDenied):
            return denied(request)
        return _redirect(f"/w08/briefs/{brief_id}")

    def _brief_version(
        connection: Any,
        brief_id: UUID,
        tenant: UUID,
        *,
        status: R1RoleBriefStatus,
        actor: UUID,
        rejection_reason: RoleBriefRejectionReason | None = None,
        decision_note: str | None = None,
    ) -> tuple[R1RoleBriefVersion, int]:
        row = (
            connection.execute(
                text(
                    "SELECT w.lock_version,r.* FROM role_brief_workflows w JOIN role_brief_revisions r ON r.role_brief_id=w.role_brief_id AND r.version=w.latest_version WHERE w.role_brief_id=:id AND w.tenant_id=:tenant"
                ),
                {"id": brief_id, "tenant": tenant},
            )
            .mappings()
            .one()
        )
        version = int(row["version"]) + 1
        now = _now()
        prior_submitted = (
            None
            if row["submitted_at"] is None
            else datetime.fromisoformat(str(row["submitted_at"]))
        )
        return R1RoleBriefVersion(
            role_brief_id=brief_id,
            tenant_context=TenantContext(tenant_id=tenant),
            version=version,
            previous_version=version - 1,
            trace_id=UUID(str(row["trace_id"])),
            owner_id=UUID(str(row["owner_id"])),
            created_by=actor,
            visibility=WorkflowVisibility(str(row["visibility"])),
            title=str(row["title"]),
            template_id=str(row["template_id"]),
            taxonomy_version=str(row["taxonomy_version"]),
            status=status,
            responsibilities=tuple(json.loads(str(row["responsibilities"]))),
            hard_constraints=tuple(
                RoleConstraint(
                    field=str(item["field"]),
                    operator=ConstraintOperator(str(item["operator"])),
                    value=str(item["value"]),
                )
                for item in json.loads(str(row["hard_constraints"]))
            ),
            preferences=tuple(
                RolePreference(dimension=str(item["dimension"]), weight=float(item["weight"]))
                for item in json.loads(str(row["preferences"]))
            ),
            exemplar_player_ids=tuple(
                UUID(str(player_id)) for player_id in json.loads(str(row["exemplar_player_ids"]))
            ),
            transition_reason="local user-attributable status transition",
            rejection_reason=rejection_reason,
            decision_note=decision_note,
            submitted_at=now if status is R1RoleBriefStatus.SUBMITTED else prior_submitted,
            decided_at=_now()
            if status in {R1RoleBriefStatus.APPROVED, R1RoleBriefStatus.REJECTED}
            else None,
            decided_by=actor
            if status in {R1RoleBriefStatus.APPROVED, R1RoleBriefStatus.REJECTED}
            else None,
            created_at=now,
        ), int(row["lock_version"])

    def _corrected_draft_version(
        connection: Any, brief_id: UUID, tenant: UUID, *, actor: UUID, form: dict[str, str]
    ) -> tuple[R1RoleBriefVersion, int]:
        row = (
            connection.execute(
                text(
                    "SELECT w.lock_version,r.* FROM role_brief_workflows w JOIN role_brief_revisions r ON r.role_brief_id=w.role_brief_id AND r.version=w.latest_version WHERE w.role_brief_id=:id AND w.tenant_id=:tenant"
                ),
                {"id": brief_id, "tenant": tenant},
            )
            .mappings()
            .one()
        )
        if str(row["status"]) != R1RoleBriefStatus.REJECTED.value:
            raise WorkflowConflict("only rejected briefs may be corrected")
        responsibilities, constraints, preferences, exemplars = parse_brief_form(form)
        version = int(row["version"]) + 1
        return R1RoleBriefVersion(
            role_brief_id=brief_id,
            tenant_context=TenantContext(tenant_id=tenant),
            version=version,
            previous_version=version - 1,
            trace_id=UUID(str(row["trace_id"])),
            owner_id=UUID(str(row["owner_id"])),
            created_by=actor,
            visibility=WorkflowVisibility(str(row["visibility"])),
            title=form["title"].strip(),
            template_id=str(row["template_id"]),
            taxonomy_version=str(row["taxonomy_version"]),
            status=R1RoleBriefStatus.DRAFT,
            responsibilities=responsibilities,
            hard_constraints=constraints,
            preferences=preferences,
            exemplar_player_ids=exemplars,
            transition_reason="local attributable correction after controlled rejection",
            created_at=_now(),
        ), int(row["lock_version"])

    def replay_approved_brief(row: Any, tenant_id: UUID) -> tuple[Any, Any]:
        """Replay W07's registered public M0 core under the local brief identity only."""
        base = w07_default_request()
        brief_id = UUID(str(row["role_brief_id"]))
        version = int(row["version"])
        trace_id = UUID(str(row["trace_id"]))
        retrieval_id = uuid5(_W08_REPLAY_NAMESPACE, f"request:{brief_id}:{version}")
        approved_at = datetime.fromisoformat(str(row["created_at"]))
        request = base.retrieval_request.model_copy(
            update={
                "retrieval_request_id": retrieval_id,
                "tenant_context": TenantContext(tenant_id=tenant_id),
                "trace_id": trace_id,
                "role_brief_id": brief_id,
                "role_brief_version": version,
                "requested_at": approved_at,
            }
        )
        responsibilities = tuple(json.loads(str(row["responsibilities"])))
        preferences = {
            str(item["dimension"]): float(item["weight"])
            for item in json.loads(str(row["preferences"]))
        }
        payload = base.resolved_query.model_dump(mode="python")
        payload.update(
            {
                "tenant_context": request.tenant_context,
                "trace_id": trace_id,
                "role_brief_id": brief_id,
                "role_brief_version": version,
                "responsibilities": responsibilities,
                "responsibility_weights": tuple(
                    M0ResolvedResponsibilityWeight(
                        responsibility_code=code, weight=preferences.get(str(code), 1.0)
                    )
                    for code in responsibilities
                ),
                "hard_constraints": tuple(
                    RoleConstraint(
                        field=str(item["field"]),
                        operator=ConstraintOperator(str(item["operator"])),
                        value=str(item["value"]),
                    )
                    for item in json.loads(str(row["hard_constraints"]))
                ),
                "exemplar_player_ids": tuple(
                    UUID(str(player_id))
                    for player_id in json.loads(str(row["exemplar_player_ids"]))
                ),
            }
        )
        if payload["exemplar_player_ids"]:
            payload["query_player_id"] = None
        payload["resolved_query_digest"] = M0ResolvedQuery.digest_for_payload(payload)
        query = M0ResolvedQuery.model_validate(payload)
        pinned_payload = base.model_dump(mode="python")
        pinned_payload.update(
            {
                "retrieval_request": request,
                "resolved_query": query,
                "expected_resolved_query_digest": query.resolved_query_digest,
            }
        )
        pinned = PinnedM0ServingRequest.model_validate(pinned_payload)
        core, _ = w07_core()
        return pinned, core.serve(pinned)

    def replay_projection(row: Any, tenant_id: UUID) -> dict[str, object]:
        """Return the complete fresh local replay projection used by every guarded route."""
        pinned, replay = replay_approved_brief(row, tenant_id)
        query = pinned.resolved_query
        result = replay.retrieval_result
        return {
            "tenant_id": str(tenant_id),
            "role_brief_id": str(query.role_brief_id),
            "role_brief_version": query.role_brief_version,
            "owner_id": str(row["owner_id"]),
            "brief_created_at": str(row["created_at"]),
            "trace_id": str(query.trace_id),
            "retrieval_request_id": str(pinned.retrieval_request.retrieval_request_id),
            "requested_at": pinned.retrieval_request.requested_at.isoformat(),
            "resolved_query_digest": str(query.resolved_query_digest),
            "query_player_id": None
            if query.query_player_id is None
            else str(query.query_player_id),
            "exemplar_player_ids": tuple(str(item) for item in query.exemplar_player_ids),
            "retrieval_result_id": str(result.retrieval_result_id),
            "retrieval_run_id": str(result.retrieval_run_id),
            "wrapper_result_digest": str(replay.result_digest),
            "lineage_digest": str(result.temporal_evidence.dependency_lineage_hash),
            "model_version": str(result.model_version),
            "index_version": str(result.index_version),
            "taxonomy_version": str(replay.artifact_manifest.taxonomy_version),
            "data_version": str(replay.artifact_manifest.candidate_universe_id),
            "ordered_candidate_ids": tuple(str(item.player_id) for item in result.candidates),
            "applicability": "LIMITED",
            "limitations": (
                "NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE",
                "resemblance_only",
                "synthetic_development_only",
                "no_recommendation_evidence",
            ),
            "retrieval_link_id": str(
                uuid5(
                    _W08_REPLAY_NAMESPACE,
                    f"link:{query.role_brief_id}:{query.role_brief_version}",
                )
            ),
        }

    def exact_double_replay_projection(row: Any, tenant_id: UUID) -> dict[str, object]:
        first = replay_projection(row, tenant_id)
        second = replay_projection(row, tenant_id)
        if first != second:
            raise WorkflowConflict("local replay identity mismatch")
        return first

    def projection_matches_link(link: Any, projection: dict[str, object]) -> bool:
        """Compare every persisted link field to the same fresh replay projection."""
        created_at = datetime.fromisoformat(str(link["created_at"]))
        brief_created_at = datetime.fromisoformat(str(projection["brief_created_at"]))
        return (
            str(link["retrieval_link_id"]) == projection["retrieval_link_id"]
            and str(link["tenant_id"]) == projection["tenant_id"]
            and str(link["role_brief_id"]) == projection["role_brief_id"]
            and int(link["role_brief_version"]) == projection["role_brief_version"]
            and str(link["retrieval_request_id"]) == projection["retrieval_request_id"]
            and str(link["retrieval_result_id"]) == projection["retrieval_result_id"]
            and str(link["retrieval_run_id"]) == projection["retrieval_run_id"]
            and (None if link["query_player_id"] is None else str(link["query_player_id"]))
            == projection["query_player_id"]
            and tuple(json.loads(str(link["exemplar_player_ids"])))
            == projection["exemplar_player_ids"]
            and str(link["model_version"]) == projection["model_version"]
            and str(link["index_version"]) == projection["index_version"]
            and str(link["data_version"]) == projection["data_version"]
            and str(link["taxonomy_version"]) == projection["taxonomy_version"]
            and str(link["result_digest"]) == projection["wrapper_result_digest"]
            and str(link["lineage_digest"]) == projection["lineage_digest"]
            and str(link["claim_boundary"]) == "resemblance_only"
            and str(link["evidence_class"]) == "synthetic_development_only"
            and str(link["applicability"]) == projection["applicability"]
            and tuple(json.loads(str(link["limitations"])))
            == (
                "NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE",
                "no_recommendation_evidence",
            )
            and str(link["created_by"]) == projection["owner_id"]
            and created_at.tzinfo is not None
            and brief_created_at.tzinfo is not None
            and created_at >= brief_created_at
            and created_at <= _now()
        )

    @app.post("/w08/briefs/{brief_id}/status/{action}", response_model=None)
    async def transition_brief(
        brief_id: UUID, action: str, request: Request
    ) -> RedirectResponse | HTMLResponse:
        try:
            form = await form_values(request)
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            target = {
                "submit": R1RoleBriefStatus.SUBMITTED,
                "approve": R1RoleBriefStatus.APPROVED,
                "reject": R1RoleBriefStatus.REJECTED,
            }[action]
            rejection_reason = (
                RoleBriefRejectionReason(form["rejection_reason"])
                if target is R1RoleBriefStatus.REJECTED
                else None
            )
            decision_note = form.get("decision_note") or None
        except (R1AuthenticationDenied, KeyError, ValueError):
            return denied(request)
        try:
            with engine.begin() as connection:
                next_version, lock = _brief_version(
                    connection,
                    brief_id,
                    current.tenant_id,
                    status=target,
                    actor=current.actor_id,
                    rejection_reason=rejection_reason,
                    decision_note=decision_note,
                )
                workflow.transition_role_brief(
                    connection,
                    principal=current,
                    next_version=next_version,
                    expected_lock_version=lock,
                    request_id=uuid4(),
                )
        except (
            NoResultFound,
            SQLAlchemyError,
            ValueError,
            WorkflowConflict,
            R1AuthorizationDenied,
        ):
            return denied(request)
        return _redirect(f"/w08/briefs/{brief_id}")

    @app.post("/w08/briefs/{brief_id}/correct", response_model=None)
    async def correct_brief(brief_id: UUID, request: Request) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            expected = int(form["expected_lock_version"])
            with engine.begin() as connection:
                corrected, lock = _corrected_draft_version(
                    connection, brief_id, current.tenant_id, actor=current.actor_id, form=form
                )
                if lock != expected:
                    raise WorkflowConflict("stale brief correction")
                workflow.transition_role_brief(
                    connection,
                    principal=current,
                    next_version=corrected,
                    expected_lock_version=expected,
                    request_id=uuid4(),
                )
        except (
            KeyError,
            ValueError,
            NoResultFound,
            SQLAlchemyError,
            WorkflowConflict,
            R1AuthenticationDenied,
            R1AuthorizationDenied,
        ):
            return denied(request)
        return _redirect(f"/w08/briefs/{brief_id}")

    @app.get("/w08/briefs/{brief_id}", response_class=HTMLResponse)
    def detail(brief_id: UUID, request: Request) -> HTMLResponse:
        try:
            current = principal(request)
        except R1AuthenticationDenied:
            return denied(request, 401)
        with engine.connect() as connection:
            rows = (
                connection.execute(
                    text(
                        "SELECT r.* FROM role_brief_revisions r WHERE r.role_brief_id=:id AND r.tenant_id=:tenant ORDER BY version"
                    ),
                    {"id": brief_id, "tenant": current.tenant_id},
                )
                .mappings()
                .all()
            )
            links = (
                connection.execute(
                    text(
                        "SELECT * FROM replayable_retrieval_links WHERE role_brief_id=:id AND tenant_id=:tenant"
                    ),
                    {"id": brief_id, "tenant": current.tenant_id},
                )
                .mappings()
                .all()
            )
        if not rows:
            return denied(request, 404)
        latest = rows[-1]
        if not can_read_brief(current, latest):
            return denied(request, 404)
        rendered_links: list[dict[str, object]] = []
        try:
            with engine.connect() as connection:
                briefs_by_key = _role_briefs_for_links(
                    connection,
                    links,
                    tenant_id=current.tenant_id,
                )
                for link in links:
                    brief = briefs_by_key.get(
                        (str(link["role_brief_id"]), int(link["role_brief_version"]))
                    )
                    if brief is None:
                        raise WorkflowConflict("link brief is unavailable")
                    if not can_read_retrieval_link(current, connection, link, brief):
                        continue
                    projection = exact_double_replay_projection(brief, current.tenant_id)
                    if not projection_matches_link(link, projection):
                        raise WorkflowConflict("persisted replay link mismatch")
                    rendered_links.append({**dict(link), "projection": projection})
        except (NoResultFound, ValueError, WorkflowConflict):
            return denied(request)
        return page(
            request,
            "brief.html",
            title="Role brief history",
            principal=current,
            brief_id=brief_id,
            rows=rows,
            links=rendered_links,
            brief_options=retained_brief_options(),
        )

    @app.post("/w08/briefs/{brief_id}/retrieval", response_model=None)
    async def link_retrieval(brief_id: UUID, request: Request) -> RedirectResponse | HTMLResponse:
        try:
            form = await form_values(request)
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
        except R1AuthenticationDenied:
            return denied(request, 401)
        try:
            with engine.begin() as connection:
                row = (
                    connection.execute(
                        text(
                            "SELECT r.* FROM role_brief_workflows w JOIN role_brief_revisions r ON r.role_brief_id=w.role_brief_id AND r.version=w.latest_version WHERE w.role_brief_id=:id AND w.tenant_id=:tenant"
                        ),
                        {"id": brief_id, "tenant": current.tenant_id},
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    return denied(request)
                if str(row["status"]) != R1RoleBriefStatus.APPROVED.value:
                    return denied(request)
                projection = exact_double_replay_projection(row, current.tenant_id)
                existing = (
                    connection.execute(
                        text(
                            "SELECT * FROM replayable_retrieval_links WHERE tenant_id=:tenant "
                            "AND role_brief_id=:brief AND role_brief_version=:version"
                        ),
                        {
                            "tenant": current.tenant_id,
                            "brief": brief_id,
                            "version": int(row["version"]),
                        },
                    )
                    .mappings()
                    .one_or_none()
                )
                if existing is not None:
                    if not projection_matches_link(existing, projection):
                        raise WorkflowConflict("persisted replay link mismatch")
                    return _redirect(f"/w08/briefs/{brief_id}")
                link = ReplayableRetrievalLink(
                    retrieval_link_id=uuid5(
                        _W08_REPLAY_NAMESPACE, f"link:{brief_id}:{row['version']}"
                    ),
                    tenant_context=TenantContext(tenant_id=current.tenant_id),
                    role_brief_id=brief_id,
                    role_brief_version=int(row["version"]),
                    retrieval_request_id=UUID(str(projection["retrieval_request_id"])),
                    retrieval_result_id=UUID(str(projection["retrieval_result_id"])),
                    retrieval_run_id=UUID(str(projection["retrieval_run_id"])),
                    query_player_id=(
                        None
                        if projection["query_player_id"] is None
                        else UUID(str(projection["query_player_id"]))
                    ),
                    exemplar_player_ids=tuple(
                        UUID(str(item))
                        for item in cast(tuple[str, ...], projection["exemplar_player_ids"])
                    ),
                    model_version=str(projection["model_version"]),
                    index_version=str(projection["index_version"]),
                    data_version=str(projection["data_version"]),
                    taxonomy_version=str(projection["taxonomy_version"]),
                    result_digest=str(projection["wrapper_result_digest"]),
                    lineage_digest=str(projection["lineage_digest"]),
                    limitations=(
                        "NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE",
                        "no_recommendation_evidence",
                    ),
                    created_by=current.actor_id,
                    created_at=_now(),
                )
                workflow.create_retrieval_link(
                    connection, principal=current, link=link, request_id=uuid4()
                )
        except (
            NoResultFound,
            SQLAlchemyError,
            ValueError,
            WorkflowConflict,
            R1AuthorizationDenied,
        ):
            return denied(request)
        return _redirect(f"/w08/briefs/{brief_id}")

    @app.get("/w08/audit", response_class=HTMLResponse)
    def audit(request: Request) -> HTMLResponse:
        try:
            current = principal(request)
        except R1AuthenticationDenied:
            return denied(request, 401)
        if LocalRole.ADMIN not in current.roles:
            return denied(request)
        try:
            with engine.connect() as connection:
                audit_ledger.verify(connection, tenant_id=current.tenant_id)
                rows = (
                    connection.execute(
                        text(
                            "SELECT r.sequence,r.receipt_digest,e.action,e.target_type,e.target_id,e.reason FROM audit_receipts r JOIN audit_events e ON e.audit_event_id=r.audit_event_id WHERE r.tenant_id=:tenant ORDER BY r.sequence"
                        ),
                        {"tenant": current.tenant_id},
                    )
                    .mappings()
                    .all()
                )
        except AuditIntegrityError:
            return denied(request)
        return page(
            request, "audit.html", title="Append-only audit receipts", principal=current, rows=rows
        )

    @app.get("/w08/export/{pack_id}", response_class=HTMLResponse)
    def read_export(pack_id: UUID, request: Request) -> HTMLResponse:
        try:
            current = principal(request)
        except R1AuthenticationDenied:
            return denied(request, 401)
        try:
            with engine.begin() as connection:
                payload = exporter.read(connection, principal=current, evidence_pack_id=pack_id)
        except (EvidenceExportDenied, EvidenceExportIntegrityError):
            return denied(request)
        return page(
            request,
            "export.html",
            title="Local evidence pack",
            principal=current,
            payload=payload,
            pack_id=pack_id,
        )

    @app.get("/w08/exports", response_class=HTMLResponse)
    def exports(request: Request) -> HTMLResponse:
        try:
            current = principal(request)
            if not current.roles.intersection({LocalRole.ANALYST, LocalRole.APPROVER}):
                return denied(request)
            with engine.connect() as connection:
                audit_ledger.verify(connection, tenant_id=current.tenant_id)
                rows = (
                    connection.execute(
                        text(
                            "SELECT e.*,v.reason,v.revoked_at FROM evidence_exports e "
                            "LEFT JOIN evidence_export_revocations v ON v.evidence_pack_id=e.evidence_pack_id "
                            "AND v.tenant_id=e.tenant_id WHERE e.tenant_id=:tenant "
                            "AND (:approver=1 OR e.generated_by=:actor) ORDER BY e.generated_at DESC"
                        ),
                        {
                            "tenant": current.tenant_id,
                            "actor": current.actor_id,
                            "approver": int(LocalRole.APPROVER in current.roles),
                        },
                    )
                    .mappings()
                    .all()
                )
                for row in rows:
                    exporter.verify_persisted_pack(str(row["relative_path"]), str(row["sha256"]))
        except (R1AuthenticationDenied, AuditIntegrityError, EvidenceExportIntegrityError):
            return denied(request)
        return page(
            request, "exports.html", title="Local evidence packs", principal=current, rows=rows
        )

    @app.post("/w08/exports", response_model=None)
    async def create_export(request: Request) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            identity = ":".join(
                (
                    str(current.tenant_id),
                    str(current.actor_id),
                    form["role_brief_id"],
                    form["role_brief_version"],
                    form["retrieval_link_id"],
                    form["shortlist_id"],
                )
            )
            pack_id = uuid5(_W08_REPLAY_NAMESPACE, f"export:{identity}")
            with engine.begin() as connection:
                exporter.export(
                    connection,
                    principal=current,
                    evidence_pack_id=pack_id,
                    role_brief_id=UUID(form["role_brief_id"]),
                    role_brief_version=int(form["role_brief_version"]),
                    retrieval_link_id=UUID(form["retrieval_link_id"]),
                    shortlist_id=UUID(form["shortlist_id"]),
                    trace_id=uuid5(_W08_REPLAY_NAMESPACE, f"export-trace:{identity}"),
                    request_id=uuid5(_W08_REPLAY_NAMESPACE, f"export-request:{identity}"),
                )
        except (
            KeyError,
            ValueError,
            SQLAlchemyError,
            R1AuthenticationDenied,
            EvidenceExportDenied,
            EvidenceExportIntegrityError,
        ):
            return denied(request)
        return _redirect(f"/w08/export/{pack_id}")

    @app.post("/w08/export/{pack_id}/revoke", response_model=None)
    async def revoke_export(pack_id: UUID, request: Request) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            with engine.begin() as connection:
                exporter.revoke(
                    connection,
                    principal=current,
                    evidence_pack_id=pack_id,
                    reason=form["reason"],
                    trace_id=uuid4(),
                    request_id=uuid4(),
                )
        except (
            KeyError,
            ValueError,
            SQLAlchemyError,
            R1AuthenticationDenied,
            EvidenceExportDenied,
            EvidenceExportIntegrityError,
        ):
            return denied(request)
        return _redirect("/w08/exports")

    def entry_context(connection: Any, entry_id: UUID, tenant_id: UUID) -> Any:
        return (
            connection.execute(
                text(
                    """SELECT e.shortlist_entry_id,e.lock_version,e.latest_revision,
                    s.shortlist_id,s.owner_id,s.visibility,s.role_brief_id,s.role_brief_version,
                    r.* FROM shortlist_entry_workflows e
                    JOIN workflow_shortlists s ON s.shortlist_id=e.shortlist_id AND s.tenant_id=e.tenant_id
                    JOIN shortlist_entry_revisions r ON r.shortlist_entry_id=e.shortlist_entry_id
                        AND r.revision=e.latest_revision
                    WHERE e.shortlist_entry_id=:id AND e.tenant_id=:tenant"""
                ),
                {"id": entry_id, "tenant": tenant_id},
            )
            .mappings()
            .one_or_none()
        )

    def can_read_entry(current: R1Principal, row: Any) -> bool:
        resource = R1Resource(
            current.tenant_id,
            UUID(str(row["owner_id"])),
            str(row["visibility"]),
            frozenset()
            if row["assigned_scout_id"] is None
            else frozenset({UUID(str(row["assigned_scout_id"]))}),
        )
        return policy.authorize(
            current,
            action="shortlist.read",
            resource=resource,
        ) or policy.authorize(current, action="shortlist.read_assigned", resource=resource)

    def can_read_shortlist(current: R1Principal, shortlist: Any, entries: Sequence[Any]) -> bool:
        """Apply shortlist-wide access before the exact assigned-entry fallback."""
        resource = R1Resource(
            current.tenant_id,
            UUID(str(shortlist["owner_id"])),
            str(shortlist["visibility"]),
        )
        return policy.authorize(current, action="shortlist.read", resource=resource) or any(
            can_read_entry(current, entry) for entry in entries
        )

    def permitted_entry_targets(current: R1Principal, row: Any) -> tuple[str, ...]:
        """Expose only transitions the unchanged service/policy can accept."""
        legal_targets = {
            "longlist": ("monitor", "scout", "hold", "rejected"),
            "monitor": ("longlist", "scout", "hold", "rejected"),
            "scout": ("monitor", "shortlist", "hold", "rejected"),
            "shortlist": ("hold", "rejected"),
            "hold": ("longlist", "monitor", "scout", "shortlist", "rejected"),
            "rejected": ("longlist",),
        }[str(row["state"])]
        resource = R1Resource(
            current.tenant_id,
            UUID(str(row["owner_id"])),
            str(row["visibility"]),
            frozenset()
            if row["assigned_scout_id"] is None
            else frozenset({UUID(str(row["assigned_scout_id"]))}),
        )

        return tuple(
            target
            for target in legal_targets
            if any(
                policy.authorize(current, action=action, resource=resource)
                for action in entry_transition_actions(target)
            )
        )

    def rendered_observation(observation: dict[str, object]) -> dict[str, object]:
        """Decode stored structured fields for a complete, safe rendered history."""
        rendered = dict(observation)
        rendered["dimensions"] = json.loads(str(observation["dimensions"]))
        rendered["evidence_references"] = json.loads(str(observation["evidence_references"]))
        return rendered

    def entry_revision(row: Any, *, actor: UUID, form: dict[str, str]) -> R1ShortlistEntryRevision:
        state = ShortlistEntryState(form.get("state", str(row["state"])))
        scout_value = form.get("assigned_scout_id")
        assigned_scout = (
            UUID(str(row["assigned_scout_id"]))
            if scout_value is None and row["assigned_scout_id"] is not None
            else UUID(scout_value)
            if scout_value
            else None
        )
        rejection = form.get("rejection_reason", "").strip()
        hold = form.get("hold_reason", "").strip()
        next_action = form.get("next_action", "").strip() or None
        next_owner = form.get("next_action_owner_id", "").strip()
        return R1ShortlistEntryRevision(
            shortlist_entry_id=UUID(str(row["shortlist_entry_id"])),
            shortlist_id=UUID(str(row["shortlist_id"])),
            tenant_context=TenantContext(tenant_id=UUID(str(row["tenant_id"]))),
            revision=int(row["revision"]) + 1,
            previous_revision=int(row["revision"]),
            role_brief_id=UUID(str(row["role_brief_id"])),
            role_brief_version=int(row["role_brief_version"]),
            player_id=UUID(str(row["player_id"])),
            state=state,
            owner_id=UUID(str(row["owner_id"])),
            assigned_scout_id=assigned_scout,
            retrieval_link_id=UUID(str(row["retrieval_link_id"])),
            rationale=str(row["rationale"]),
            transition_reason=form.get("transition_reason", "local attributable transition"),
            rejection_reason=ShortlistRejectionReason(rejection) if rejection else None,
            hold_reason=ShortlistHoldReason(hold) if hold else None,
            reason_note=form.get("reason_note", "").strip() or None,
            next_action=next_action,
            next_action_owner_id=UUID(next_owner) if next_owner else None,
            changed_by=actor,
            created_at=_now(),
        )

    def conflict(request: Request, reload_path: str) -> HTMLResponse:
        response = page(
            request,
            "error.html",
            title="Winning revision changed",
            message="Another local action won this revision. Reload the current history and retry.",
            reload_path=reload_path,
        )
        response.status_code = 409
        return response

    @app.post("/w08/briefs/{brief_id}/shortlists", response_model=None)
    async def create_shortlist(brief_id: UUID, request: Request) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            link_id = UUID(form.get("retrieval_link_id", ""))
            shortlist_id = uuid4()
            with engine.begin() as connection:
                link = (
                    connection.execute(
                        text(
                            """SELECT role_brief_id, role_brief_version
                            FROM replayable_retrieval_links
                            WHERE retrieval_link_id=:id AND tenant_id=:tenant"""
                        ),
                        {"id": link_id, "tenant": current.tenant_id},
                    )
                    .mappings()
                    .one_or_none()
                )
                if link is None or str(link["role_brief_id"]) != str(brief_id):
                    return denied(request)
                workflow.create_shortlist(
                    connection,
                    shortlist_id=shortlist_id,
                    tenant_id=current.tenant_id,
                    role_brief_id=brief_id,
                    role_brief_version=int(link["role_brief_version"]),
                    owner_id=current.actor_id,
                    visibility=WorkflowVisibility(form.get("visibility", "TEAM")),
                    title=form.get("title", "Local shortlist"),
                    principal=current,
                    request_id=uuid4(),
                )
        except (ValueError, WorkflowConflict, R1AuthorizationDenied):
            return denied(request)
        return _redirect(f"/w08/shortlists/{shortlist_id}")

    @app.get("/w08/shortlists/{shortlist_id}", response_class=HTMLResponse)
    def shortlist_detail(shortlist_id: UUID, request: Request) -> HTMLResponse:
        try:
            current = principal(request)
        except R1AuthenticationDenied:
            return denied(request, 401)
        with engine.connect() as connection:
            shortlist = (
                connection.execute(
                    text(
                        "SELECT * FROM workflow_shortlists WHERE shortlist_id=:id AND tenant_id=:tenant"
                    ),
                    {"id": shortlist_id, "tenant": current.tenant_id},
                )
                .mappings()
                .one_or_none()
            )
            entries = (
                []
                if shortlist is None
                else connection.execute(
                    text("""SELECT e.shortlist_entry_id,e.lock_version,r.revision,r.state,r.player_id,r.assigned_scout_id,
                s.owner_id,s.visibility
                FROM shortlist_entry_workflows e JOIN workflow_shortlists s ON s.shortlist_id=e.shortlist_id AND s.tenant_id=e.tenant_id
                JOIN shortlist_entry_revisions r ON r.shortlist_entry_id=e.shortlist_entry_id AND r.revision=e.latest_revision
                WHERE e.shortlist_id=:id AND e.tenant_id=:tenant ORDER BY e.updated_at DESC"""),
                    {"id": shortlist_id, "tenant": current.tenant_id},
                )
                .mappings()
                .all()
            )
            links = (
                []
                if shortlist is None
                else connection.execute(
                    text(
                        "SELECT * FROM replayable_retrieval_links WHERE role_brief_id=:brief "
                        "AND role_brief_version=:version AND tenant_id=:tenant"
                    ),
                    {
                        "brief": shortlist["role_brief_id"],
                        "version": shortlist["role_brief_version"],
                        "tenant": current.tenant_id,
                    },
                )
                .mappings()
                .all()
            )
        list_allowed = shortlist is not None and can_read_shortlist(current, shortlist, entries)
        entries = [row for row in entries if can_read_entry(current, row)]
        if shortlist is None or not list_allowed:
            return denied(request, 404)
        candidate_options: list[dict[str, object]] = []
        rendered_links: list[Any] = []
        try:
            with engine.connect() as connection:
                briefs_by_key = _role_briefs_for_links(
                    connection,
                    links,
                    tenant_id=current.tenant_id,
                )
                for link in links:
                    brief = briefs_by_key.get(
                        (str(link["role_brief_id"]), int(link["role_brief_version"]))
                    )
                    if brief is None:
                        raise WorkflowConflict("link brief is unavailable")
                    if not can_read_retrieval_link(current, connection, link, brief):
                        continue
                    projection = exact_double_replay_projection(brief, current.tenant_id)
                    if not projection_matches_link(link, projection):
                        raise WorkflowConflict("persisted replay link mismatch")
                    rendered_links.append(link)
                    for rank, player_id in enumerate(
                        cast(tuple[str, ...], projection["ordered_candidate_ids"]), 1
                    ):
                        candidate_options.append(
                            {
                                "link_id": str(link["retrieval_link_id"]),
                                "player_id": str(player_id),
                                "rank": rank,
                            }
                        )
        except (NoResultFound, ValueError, WorkflowConflict):
            return denied(request)
        return page(
            request,
            "shortlist.html",
            title="Local shortlist",
            principal=current,
            shortlist=shortlist,
            entries=entries,
            links=rendered_links,
            candidate_options=candidate_options,
            can_export=policy.authorize(
                current,
                action="evidence_export.create",
                resource=R1Resource(
                    current.tenant_id,
                    UUID(str(shortlist["owner_id"])),
                    str(shortlist["visibility"]),
                ),
            ),
        )

    @app.post("/w08/shortlists/{shortlist_id}/entries", response_model=None)
    async def add_shortlist_entry(
        shortlist_id: UUID, request: Request
    ) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            entry_id = uuid4()
            with engine.begin() as connection:
                shortlist = (
                    connection.execute(
                        text(
                            "SELECT * FROM workflow_shortlists WHERE shortlist_id=:id AND tenant_id=:tenant"
                        ),
                        {"id": shortlist_id, "tenant": current.tenant_id},
                    )
                    .mappings()
                    .one_or_none()
                )
                if shortlist is None:
                    return denied(request, 404)
                selection = form.get("candidate_selection", "")
                selected_link, separator, selected_player = selection.partition(":")
                link_id = selected_link if separator else form.get("retrieval_link_id", "")
                requested_player = selected_player if separator else form.get("player_id", "")
                if not link_id or not requested_player:
                    return denied(request)
                link = (
                    connection.execute(
                        text(
                            "SELECT * FROM replayable_retrieval_links WHERE retrieval_link_id=:id AND tenant_id=:tenant"
                        ),
                        {"id": link_id, "tenant": current.tenant_id},
                    )
                    .mappings()
                    .one_or_none()
                )
                if link is None:
                    return denied(request)
                brief = (
                    connection.execute(
                        text(
                            "SELECT * FROM role_brief_revisions WHERE role_brief_id=:id AND version=:version AND tenant_id=:tenant"
                        ),
                        {
                            "id": link["role_brief_id"],
                            "version": link["role_brief_version"],
                            "tenant": current.tenant_id,
                        },
                    )
                    .mappings()
                    .one_or_none()
                )
                if (
                    brief is None
                    or str(link["role_brief_id"]) != str(shortlist["role_brief_id"])
                    or int(link["role_brief_version"]) != int(shortlist["role_brief_version"])
                ):
                    return denied(request)
                projection = exact_double_replay_projection(brief, current.tenant_id)
                if not projection_matches_link(link, projection):
                    return denied(request)
                player_id = UUID(requested_player)
                if str(player_id) not in cast(tuple[str, ...], projection["ordered_candidate_ids"]):
                    return denied(request)
                revision = R1ShortlistEntryRevision(
                    shortlist_entry_id=entry_id,
                    shortlist_id=shortlist_id,
                    tenant_context=TenantContext(tenant_id=current.tenant_id),
                    revision=1,
                    role_brief_id=UUID(str(shortlist["role_brief_id"])),
                    role_brief_version=int(shortlist["role_brief_version"]),
                    player_id=player_id,
                    state=ShortlistEntryState.LONGLIST,
                    owner_id=current.actor_id,
                    retrieval_link_id=UUID(link_id),
                    rationale=form.get("rationale", "local evidence inspection"),
                    transition_reason="local attributable longlist addition",
                    changed_by=current.actor_id,
                    created_at=_now(),
                )
                workflow.add_entry(
                    connection, principal=current, revision=revision, request_id=uuid4()
                )
        except (ValueError, WorkflowConflict, R1AuthorizationDenied):
            return denied(request)
        return _redirect(f"/w08/entries/{entry_id}")

    @app.get("/w08/entries/{entry_id}", response_class=HTMLResponse)
    def entry_detail(entry_id: UUID, request: Request) -> HTMLResponse:
        try:
            current = principal(request)
        except R1AuthenticationDenied:
            return denied(request, 401)
        with engine.connect() as connection:
            row = entry_context(connection, entry_id, current.tenant_id)
            if row is None or not can_read_entry(current, row):
                return denied(request, 404)
            history = (
                connection.execute(
                    text(
                        "SELECT * FROM shortlist_entry_revisions WHERE shortlist_entry_id=:id AND tenant_id=:tenant ORDER BY revision"
                    ),
                    {"id": entry_id, "tenant": current.tenant_id},
                )
                .mappings()
                .all()
            )
            visible_observations = observations.visible_versions(
                connection, principal=current, shortlist_entry_id=entry_id
            )
            comments = (
                connection.execute(
                    text("""SELECT * FROM shortlist_comments WHERE shortlist_entry_id=:id AND tenant_id=:tenant
                ORDER BY created_at"""),
                    {"id": entry_id, "tenant": current.tenant_id},
                )
                .mappings()
                .all()
            )
        comments = [
            item
            for item in comments
            if policy.authorize(
                current,
                action="shortlist_comment.create",
                resource=R1Resource(
                    current.tenant_id,
                    UUID(str(row["owner_id"])),
                    str(item["visibility"]),
                    frozenset()
                    if row["assigned_scout_id"] is None
                    else frozenset({UUID(str(row["assigned_scout_id"]))}),
                ),
            )
        ]
        rendered_observations = [rendered_observation(item) for item in visible_observations]
        latest_visible_observations: dict[str, dict[str, Any]] = {}
        for observation in rendered_observations:
            observation_id = str(observation["observation_id"])
            current_latest = latest_visible_observations.get(observation_id)
            if current_latest is None or int(str(observation["version"])) > int(
                str(current_latest["version"])
            ):
                latest_visible_observations[observation_id] = observation
        amendable_observations = [
            observation
            for observation in latest_visible_observations.values()
            if UUID(str(observation["author_id"])) == current.actor_id
        ]
        return page(
            request,
            "entry.html",
            title="Candidate workflow history",
            principal=current,
            row=row,
            history=history,
            observations=rendered_observations,
            amendable_observations=amendable_observations,
            comments=comments,
            transition_targets=permitted_entry_targets(current, row),
        )

    @app.post("/w08/entries/{entry_id}/transition", response_model=None)
    async def transition_entry(entry_id: UUID, request: Request) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            expected = int(form.get("expected_lock_version", ""))
            with engine.begin() as connection:
                row = entry_context(connection, entry_id, current.tenant_id)
                if row is None or not can_read_entry(current, row):
                    return denied(request, 404)
                workflow.transition_entry(
                    connection,
                    principal=current,
                    next_revision=entry_revision(row, actor=current.actor_id, form=form),
                    expected_lock_version=expected,
                    request_id=uuid4(),
                )
        except WorkflowConflict:
            return conflict(request, f"/w08/entries/{entry_id}")
        except (ValueError, R1AuthenticationDenied, R1AuthorizationDenied):
            return denied(request)
        return _redirect(f"/w08/entries/{entry_id}")

    @app.post("/w08/entries/{entry_id}/comments", response_model=None)
    async def add_entry_comment(
        entry_id: UUID, request: Request
    ) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            comment = ShortlistComment(
                comment_id=uuid4(),
                tenant_context=TenantContext(tenant_id=current.tenant_id),
                shortlist_entry_id=entry_id,
                author_id=current.actor_id,
                visibility=WorkflowVisibility(form.get("visibility", "TEAM")),
                body=form.get("body", ""),
                evidence_origin=evidence_origin,
                created_at=_now(),
            )
            with engine.begin() as connection:
                workflow.add_comment(
                    connection, principal=current, comment=comment, request_id=uuid4()
                )
        except (ValueError, R1AuthenticationDenied, R1AuthorizationDenied):
            return denied(request)
        return _redirect(f"/w08/entries/{entry_id}")

    @app.post("/w08/entries/{entry_id}/observations", response_model=None)
    async def create_observation(
        entry_id: UUID, request: Request
    ) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            dimensions = tuple(
                ScoutRubricDimension(
                    dimension=name,
                    rating=int(form[f"{name.value}_rating"]),
                    confidence=float(form[f"{name.value}_confidence"]),
                    note=form[f"{name.value}_note"],
                )
                for name in ScoutRubricDimensionName
            )
            observation = ScoutObservationVersion(
                observation_id=uuid4(),
                tenant_context=TenantContext(tenant_id=current.tenant_id),
                version=1,
                shortlist_entry_id=entry_id,
                author_id=current.actor_id,
                visibility=WorkflowVisibility(form.get("visibility", "TEAM")),
                dimensions=dimensions,
                overall_confidence=float(form["overall_confidence"]),
                summary=form["summary"],
                disagreement=form.get("disagreement") == "yes",
                disagreement_reason=form.get("disagreement_reason") or None,
                recommended_next_action=form["recommended_next_action"],
                evidence_references=(
                    LocalEvidenceReference(
                        kind=LocalEvidenceReferenceKind(form["evidence_kind"]),
                        reference=form["evidence_reference"],
                    ),
                ),
                evidence_origin=evidence_origin,
                created_at=_now(),
            )
            with engine.begin() as connection:
                observations.create(
                    connection, principal=current, observation=observation, request_id=uuid4()
                )
        except (
            KeyError,
            ValueError,
            WorkflowConflict,
            R1AuthenticationDenied,
            R1AuthorizationDenied,
        ):
            return denied(request)
        return _redirect(f"/w08/entries/{entry_id}")

    @app.post("/w08/observations/{observation_id}/amend", response_model=None)
    async def amend_observation(
        observation_id: UUID, request: Request
    ) -> RedirectResponse | HTMLResponse:
        form = await form_values(request)
        try:
            current = principal(request, csrf_token=form.get("csrf"), csrf_required=True)
            expected = int(form["expected_version"])
            with engine.begin() as connection:
                row = (
                    connection.execute(
                        text(
                            "SELECT * FROM scout_observations WHERE observation_id=:id AND tenant_id=:tenant ORDER BY version DESC LIMIT 1"
                        ),
                        {"id": observation_id, "tenant": current.tenant_id},
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    return denied(request, 404)
                dimensions = tuple(
                    ScoutRubricDimension(
                        dimension=name,
                        rating=int(form[f"{name.value}_rating"]),
                        confidence=float(form[f"{name.value}_confidence"]),
                        note=form[f"{name.value}_note"],
                    )
                    for name in ScoutRubricDimensionName
                )
                revised = ScoutObservationVersion(
                    observation_id=observation_id,
                    tenant_context=TenantContext(tenant_id=current.tenant_id),
                    version=expected + 1,
                    previous_version=expected,
                    shortlist_entry_id=UUID(str(row["shortlist_entry_id"])),
                    author_id=current.actor_id,
                    visibility=WorkflowVisibility(form.get("visibility", str(row["visibility"]))),
                    dimensions=dimensions,
                    overall_confidence=float(form["overall_confidence"]),
                    summary=form["summary"],
                    disagreement=form.get("disagreement") == "yes",
                    disagreement_reason=form.get("disagreement_reason") or None,
                    recommended_next_action=form["recommended_next_action"],
                    evidence_references=(
                        LocalEvidenceReference(
                            kind=LocalEvidenceReferenceKind(form["evidence_kind"]),
                            reference=form["evidence_reference"],
                        ),
                    ),
                    evidence_origin=WorkflowEvidenceOrigin(str(row["evidence_origin"])),
                    created_at=_now(),
                )
                observations.amend(
                    connection,
                    principal=current,
                    observation=revised,
                    expected_version=expected,
                    request_id=uuid4(),
                )
        except WorkflowConflict:
            return conflict(
                request,
                f"/w08/entries/{row['shortlist_entry_id'] if 'row' in locals() and row else ''}",
            )
        except (KeyError, ValueError, R1AuthenticationDenied, R1AuthorizationDenied):
            return denied(request)
        return _redirect(f"/w08/entries/{row['shortlist_entry_id']}")

    return app

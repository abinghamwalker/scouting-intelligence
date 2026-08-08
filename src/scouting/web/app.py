"""Authenticated local HTML and JSON surfaces for the W03 journey."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NoReturn
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, ConfigDict, Field, field_validator

from scouting.audit import AuditWriteError
from scouting.contracts import RetrievalRequest, RoleBrief
from scouting.operations import LocalTelemetry
from scouting.policy import (
    AuthenticationDenied,
    AuthorizationDenied,
    SessionAuthenticator,
    SyntheticPrincipal,
)
from scouting.serving import ServingDenied
from scouting.workflow import JourneyCommand, WorkflowService


class JourneyPayload(BaseModel):
    """Strict human action inputs accepted by the JSON journey."""

    model_config = ConfigDict(extra="forbid")

    role_brief: RoleBrief
    retrieval_request: RetrievalRequest
    shortlist_id: UUID
    shortlist_entry_id: UUID
    rationale: str = Field(min_length=1, max_length=512)

    @field_validator("role_brief", mode="before")
    @classmethod
    def validate_role_brief_wire_payload(cls, value: object) -> RoleBrief:
        """Preserve strict contracts while accepting their documented JSON wire form."""
        if isinstance(value, RoleBrief):
            return value
        return RoleBrief.model_validate_json(json.dumps(value))

    @field_validator("retrieval_request", mode="before")
    @classmethod
    def validate_retrieval_request_wire_payload(
        cls,
        value: object,
    ) -> RetrievalRequest:
        """Preserve strict contracts while accepting their documented JSON wire form."""
        if isinstance(value, RetrievalRequest):
            return value
        return RetrievalRequest.model_validate_json(json.dumps(value))


class ConfidentialAttemptPayload(BaseModel):
    """Target identity for an always-denied confidential action attempt."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: UUID


@dataclass(frozen=True, slots=True)
class W03WebSettings:
    """Non-secret local composition metadata."""

    tenant_id: UUID
    authorization_policy_id: str
    data_rights_policy_id: str
    source_manifest_id: UUID
    source_manifest_digest: str
    template_path: Path


def create_app(
    *,
    authenticator: SessionAuthenticator,
    workflow: WorkflowService,
    telemetry: LocalTelemetry,
    settings: W03WebSettings,
) -> FastAPI:
    """Create an app without opening a listener or configuring an exporter."""
    app = FastAPI(
        title="W03 synthetic scouting review",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    templates = Environment(
        loader=FileSystemLoader(settings.template_path.parent),
        autoescape=select_autoescape(("html",)),
    )

    @app.middleware("http")
    async def instrument_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = _request_id(request.headers.get("x-request-id"))
        request.state.request_id = request_id
        telemetry.increment("http_requests_total")
        with telemetry.trace(
            "http.request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        ):
            response = await call_next(request)
        response.headers["x-request-id"] = str(request_id)
        telemetry.log(
            "http_request_complete",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "healthy",
            "environment": "w03-local-review",
            "exposure": "loopback_only",
        }

    @app.get("/ready")
    def readiness() -> dict[str, str]:
        identity = workflow.readiness(settings.tenant_id)
        return {
            "status": "ready",
            "database_user": identity.current_user,
            "tenant_id": str(identity.tenant_id),
            "telemetry_export": "disabled",
        }

    @app.get("/w03", response_class=HTMLResponse)
    def journey_page(request: Request) -> HTMLResponse:
        principal = _authenticate(request, authenticator, telemetry)
        template = templates.get_template(settings.template_path.name)
        return HTMLResponse(
            template.render(
                actor_id=str(principal.actor_id),
                tenant_id=str(principal.tenant_id),
                claim_boundary="resemblance only; no recruitment outcome prediction",
            )
        )

    @app.post("/api/w03/journey")
    def journey(request: Request, payload: JourneyPayload) -> JSONResponse:
        principal = _authenticate(request, authenticator, telemetry)
        request_id = _state_request_id(request)
        try:
            result = workflow.execute_journey(
                principal=principal,
                request_id=request_id,
                command=JourneyCommand(
                    role_brief=payload.role_brief,
                    retrieval_request=payload.retrieval_request,
                    shortlist_id=payload.shortlist_id,
                    shortlist_entry_id=payload.shortlist_entry_id,
                    rationale=payload.rationale,
                ),
            )
        except (AuthorizationDenied, PermissionError, ServingDenied):
            telemetry.increment("authorization_denials_total")
            telemetry.log(
                "journey_denied",
                request_id=request_id,
                actor_id=principal.actor_id,
                tenant_id=principal.tenant_id,
                action="w03.journey",
                policy_id=settings.authorization_policy_id,
            )
            raise HTTPException(status_code=403, detail="action denied") from None
        except AuditWriteError:
            telemetry.increment("audit_failures_total")
            telemetry.log(
                "journey_audit_failed",
                request_id=request_id,
                actor_id=principal.actor_id,
                tenant_id=principal.tenant_id,
            )
            raise HTTPException(status_code=503, detail="material action unavailable") from None
        except RuntimeError:
            telemetry.increment("journey_unavailable_total")
            raise HTTPException(status_code=503, detail="journey unavailable") from None

        retrieval = result.retrieval_result
        telemetry.increment("journey_success_total")
        telemetry.log(
            "journey_complete",
            request_id=request_id,
            actor_id=principal.actor_id,
            tenant_id=principal.tenant_id,
            action="w03.journey",
            policy_id=settings.authorization_policy_id,
        )
        return JSONResponse(
            {
                "request_id": str(request_id),
                "actor_id": str(principal.actor_id),
                "tenant_id": str(principal.tenant_id),
                "role_brief_id": str(retrieval.role_brief_id),
                "role_brief_version": retrieval.role_brief_version,
                "data_manifest_id": str(settings.source_manifest_id),
                "data_manifest_digest": settings.source_manifest_digest,
                "policy_ids": [
                    settings.authorization_policy_id,
                    settings.data_rights_policy_id,
                ],
                "lineage_hash": retrieval.temporal_evidence.dependency_lineage_hash,
                "cutoff_ts": retrieval.temporal_evidence.feature_cutoff_ts.isoformat().replace(
                    "+00:00", "Z"
                ),
                "retrieval_run_id": str(retrieval.retrieval_run_id),
                "model_version": retrieval.model_version,
                "index_version": retrieval.index_version,
                "claim_boundary": retrieval.claim_boundary,
                "model_quality_claim": False,
                "result": retrieval.model_dump(mode="json"),
                "explanations": [
                    {
                        "player_id": str(explanation.player_id),
                        "claim_boundary": explanation.claim_boundary,
                        "reason_codes": list(explanation.reason_codes),
                        "summary": explanation.summary,
                    }
                    for explanation in result.explanations
                ],
                "shortlist_entry": result.shortlist_entry.model_dump(mode="json"),
                "audit_actions": list(result.audit_actions),
                "admitted_fact_ids": [str(fact_id) for fact_id in result.admitted_fact_ids],
                "rejected_evidence": [
                    {"fact_id": str(fact_id), "reason_code": reason}
                    for fact_id, reason in result.rejected_evidence
                ],
                "database_context": {
                    "current_user": result.database_identity.current_user,
                    "tenant_id": str(result.database_identity.tenant_id),
                    "transaction_local": True,
                },
            }
        )

    @app.post("/api/w03/confidential-evidence/read")
    def denied_confidential_read(
        request: Request,
        payload: ConfidentialAttemptPayload,
    ) -> None:
        _deny_confidential_action(
            request=request,
            payload=payload,
            action="read",
            authenticator=authenticator,
            workflow=workflow,
            telemetry=telemetry,
        )

    @app.post("/api/w03/confidential-evidence/export")
    def denied_confidential_export(
        request: Request,
        payload: ConfidentialAttemptPayload,
    ) -> None:
        _deny_confidential_action(
            request=request,
            payload=payload,
            action="export",
            authenticator=authenticator,
            workflow=workflow,
            telemetry=telemetry,
        )

    app.state.telemetry = telemetry
    app.state.workflow = workflow
    return app


def _authenticate(
    request: Request,
    authenticator: SessionAuthenticator,
    telemetry: LocalTelemetry,
) -> SyntheticPrincipal:
    authorization = request.headers.get("authorization", "")
    scheme, separator, token = authorization.partition(" ")
    try:
        if separator != " " or scheme.lower() != "bearer":
            raise AuthenticationDenied("session authentication failed")
        return authenticator.authenticate(token)
    except AuthenticationDenied:
        telemetry.increment("authentication_denials_total")
        telemetry.log(
            "authentication_denied",
            request_id=_state_request_id(request),
            method=request.method,
            path=request.url.path,
        )
        raise HTTPException(status_code=401, detail="session authentication failed") from None


def _deny_confidential_action(
    *,
    request: Request,
    payload: ConfidentialAttemptPayload,
    action: Literal["read", "export"],
    authenticator: SessionAuthenticator,
    workflow: WorkflowService,
    telemetry: LocalTelemetry,
) -> NoReturn:
    principal = _authenticate(request, authenticator, telemetry)
    request_id = _state_request_id(request)
    try:
        workflow.audit_denied_confidential_action(
            principal=principal,
            request_id=request_id,
            target_id=payload.evidence_id,
            action=action,
        )
    except AuditWriteError:
        telemetry.increment("audit_failures_total")
        telemetry.log(
            "confidential_denial_audit_failed",
            request_id=request_id,
            actor_id=principal.actor_id,
            tenant_id=principal.tenant_id,
        )
        raise HTTPException(status_code=503, detail="material action unavailable") from None
    telemetry.increment("authorization_denials_total")
    telemetry.log(
        "confidential_action_denied",
        request_id=request_id,
        actor_id=principal.actor_id,
        tenant_id=principal.tenant_id,
        action=f"confidential_evidence.{action}",
    )
    raise HTTPException(status_code=403, detail="action denied")


def _request_id(value: str | None) -> UUID:
    if value is not None:
        try:
            return UUID(value)
        except ValueError:
            pass
    return uuid4()


def _state_request_id(request: Request) -> UUID:
    value = getattr(request.state, "request_id", None)
    return value if isinstance(value, UUID) else uuid4()

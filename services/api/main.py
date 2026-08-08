"""Environment-composed entrypoint for the loopback-only W03 API."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, cast
from uuid import UUID

from fastapi import FastAPI

from scouting.audit import AuditWriter
from scouting.operations import LocalTelemetry
from scouting.policy import (
    AuthorizationPolicy,
    SessionAuthenticator,
    SyntheticAccount,
    SyntheticRightsPolicy,
)
from scouting.serving import (
    SyntheticArtifactCatalog,
    SyntheticDomainSnapshot,
    SyntheticServingService,
)
from scouting.storage.embedded import create_embedded_engine
from scouting.web import W03WebSettings, create_app
from scouting.workflow import ApplicationDatabase, WorkflowService

_ROOT = Path(__file__).resolve().parents[2]


def create_api_app(environ: Mapping[str, str] | None = None) -> FastAPI:
    """Build the local app from ignored environment credentials and frozen config."""
    environment = os.environ if environ is None else environ
    token = _required(environment, "SCOUTING_SYNTHETIC_SESSION_TOKEN")
    actor_id = UUID(_required(environment, "SCOUTING_SYNTHETIC_ACTOR_ID"))
    tenant_id = UUID(_required(environment, "SCOUTING_SYNTHETIC_TENANT_ID"))
    fixture_root = Path(_required(environment, "SCOUTING_SYNTHETIC_FIXTURE_ROOT"))
    domain_name = environment.get("SCOUTING_SYNTHETIC_DOMAIN_NAME", "domain.json")
    partition = _partition(environment.get("SCOUTING_SYNTHETIC_PARTITION", "development"))

    authorization = AuthorizationPolicy.from_path(
        _ROOT / "configs/policies/authorization.yaml",
        known_actor_ids=(actor_id,),
    )
    rights = SyntheticRightsPolicy.from_path(_ROOT / "configs/policies/data-rights.yaml")
    snapshot = SyntheticDomainSnapshot.from_path(
        domain_name,
        allowed_fixture_root=fixture_root,
        expected_partition=partition,
        rights_policy=rights,
    )
    artifacts = SyntheticArtifactCatalog.development()
    serving = SyntheticServingService(snapshot, artifacts=artifacts)
    database = ApplicationDatabase(
        create_embedded_engine(
            environment.get("SCOUTING_DATABASE_PATH"),
            environ=environment,
        ),
        tenant_id=tenant_id,
    )
    workflow = WorkflowService(
        database=database,
        authorization=authorization,
        serving=serving,
        audit_writer=AuditWriter(),
    )
    authenticator = SessionAuthenticator(
        {
            token: SyntheticAccount(
                actor_id=actor_id,
                tenant_id=tenant_id,
                roles=("analyst",),
            )
        }
    )
    return create_app(
        authenticator=authenticator,
        workflow=workflow,
        telemetry=LocalTelemetry(),
        settings=W03WebSettings(
            tenant_id=tenant_id,
            authorization_policy_id=authorization.policy_id,
            data_rights_policy_id=rights.policy_id,
            source_manifest_id=artifacts.source_manifest_id,
            source_manifest_digest=snapshot.manifest_digest,
            template_path=_ROOT / "apps/web/templates/w03_journey.html",
        ),
    )


def _required(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} is required")
    return value


def _partition(value: str) -> Literal["development", "protected_test"]:
    if value not in {"development", "protected_test"}:
        raise RuntimeError("SCOUTING_SYNTHETIC_PARTITION is invalid")
    return cast(Literal["development", "protected_test"], value)

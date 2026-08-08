"""Bounded local worker health check with no network listener."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from scouting.operations import LocalTelemetry
from scouting.workflow import WorkflowService


@dataclass(frozen=True, slots=True)
class WorkerCheck:
    """Evidence that a worker entered the guarded application boundary."""

    status: str
    database_user: str
    tenant_id: UUID
    listener_started: bool


def run_once(
    *,
    workflow: WorkflowService,
    tenant_id: UUID,
    telemetry: LocalTelemetry,
) -> WorkerCheck:
    """Perform one local readiness unit without queue authority or a listener."""
    with telemetry.trace("worker.readiness", tenant_id=tenant_id):
        identity = workflow.readiness(tenant_id)
    telemetry.increment("worker_checks_total")
    telemetry.log("worker_ready", tenant_id=tenant_id)
    return WorkerCheck(
        status="ready",
        database_user=identity.current_user,
        tenant_id=identity.tenant_id,
        listener_started=False,
    )

"""Local telemetry remains useful, bounded, redacted, and exporter-free."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import cast
from uuid import UUID

from fastapi.testclient import TestClient

from scouting.operations import LocalTelemetry
from scouting.policy import SessionAuthenticator, SyntheticAccount
from scouting.web import W03WebSettings, create_app
from scouting.workflow import WorkflowService

ROOT = Path(__file__).resolve().parents[2]
ACTOR_ID = UUID("60000000-0000-4000-8000-000000000101")
TENANT_ID = UUID("70000000-0000-4000-8000-000000000101")


def test_structured_logs_traces_and_metrics_do_not_capture_credentials_or_payloads() -> None:
    telemetry = LocalTelemetry(maximum_records=20)
    valid_token = secrets.token_urlsafe(32)
    invalid_token = secrets.token_urlsafe(32)
    confidential_payload = secrets.token_urlsafe(24)
    app = create_app(
        authenticator=SessionAuthenticator(
            {valid_token: SyntheticAccount(ACTOR_ID, TENANT_ID, ("analyst",))}
        ),
        workflow=cast(WorkflowService, object()),
        telemetry=telemetry,
        settings=W03WebSettings(
            tenant_id=TENANT_ID,
            authorization_policy_id="w03-authorization-v1",
            data_rights_policy_id="w03-synthetic-data-rights-v1",
            source_manifest_id=UUID("90000000-0000-4000-8000-000000000101"),
            source_manifest_digest="0" * 64,
            template_path=ROOT / "apps/web/templates/w03_journey.html",
        ),
    )

    with TestClient(app) as client:
        response = client.get(
            "/w03",
            headers={
                "Authorization": f"Bearer {invalid_token}",
                "X-Confidential-Evidence": confidential_payload,
            },
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "session authentication failed"}
        assert client.get("/health").status_code == 200

    snapshot = telemetry.snapshot()
    assert snapshot.metrics["http_requests_total"] == 2
    assert snapshot.metrics["authentication_denials_total"] == 1
    assert len(snapshot.logs) >= 3
    assert len(snapshot.traces) == 2
    serialized = telemetry.serialized_snapshot()
    assert valid_token not in serialized
    assert invalid_token not in serialized
    assert confidential_payload not in serialized
    assert "authorization" not in serialized.lower()
    assert "exporter" not in serialized.lower()


def test_telemetry_bounds_records_and_drops_unapproved_attributes() -> None:
    telemetry = LocalTelemetry(maximum_records=2)
    telemetry.log("one", request_id=UUID(int=1), secret="not-retained")
    telemetry.log("two", tenant_id=TENANT_ID)
    telemetry.log("three", actor_id=ACTOR_ID)
    with telemetry.trace("bounded", token="not-retained"):
        telemetry.increment("bounded_total")

    snapshot = telemetry.snapshot()
    assert [record["event"] for record in snapshot.logs] == ["two", "three"]
    assert snapshot.metrics == {"bounded_total": 1}
    assert "secret" not in telemetry.serialized_snapshot()
    assert "token" not in telemetry.serialized_snapshot()


def test_telemetry_drops_boolean_and_unbounded_allowed_values() -> None:
    telemetry = LocalTelemetry()
    telemetry.log(
        "bounded-values",
        status_code=True,
        path="/" + ("x" * 512),
        method="GET",
    )

    record = telemetry.snapshot().logs[0]
    assert "status_code" not in record
    assert "path" not in record
    assert record["method"] == "GET"

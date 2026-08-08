"""Browser-console witnesses for the genuine-user W08 study mechanics."""

from __future__ import annotations

import importlib.util
import socket
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from fastapi.testclient import TestClient

from scouting.web.w08_study_console import create_w08_study_console

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts/run_w08_study.py"
_SPEC = importlib.util.spec_from_file_location("run_w08_study_console", _SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
run_w08_study = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run_w08_study)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _console(tmp_path: Path) -> tuple[Any, Path, Path]:
    study_parent = tmp_path / "studies"
    capture_root = tmp_path / "captures"
    study_parent.mkdir()
    app = create_w08_study_console(
        study_parent=study_parent,
        capture_root=capture_root,
        expire_session=run_w08_study.expire_session,
        create_receipt=run_w08_study.receipt,
        repository_commit="a" * 40,
    )
    return app, study_parent, capture_root


def _csrf(client: TestClient) -> str:
    response = client.get("/")
    assert response.status_code == 200
    token = client.cookies.get("w08_console_csrf")
    assert token is not None
    return token


def _consent(client: TestClient, csrf: str, code: str = "W08-U01") -> None:
    response = client.post(
        f"/participants/{code}/consent",
        data={
            "csrf": csrf,
            "responsibility_analyst": "true",
            "responsibility_approver_or_meeting_decision": "true",
            "moderator_code": "MOD-01",
            "qualification_confirmed": "true",
            "consent_obtained": "true",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_console_records_deidentified_capture_without_claiming_gate_acceptance(
    tmp_path: Path,
) -> None:
    app, _, capture_root = _console(tmp_path)
    with TestClient(app) as client:
        csrf = _csrf(client)
        dashboard = client.get("/")
        assert "Pilot the flow, then run the five sessions" in dashboard.text
        assert "Pilot mode" in dashboard.text
        assert "0" in dashboard.text
        _consent(client, csrf)

        capture_path = capture_root / "W08-U01.yaml"
        capture = yaml.safe_load(capture_path.read_text(encoding="utf-8"))
        assert capture["status"] == "IN_PROGRESS"
        assert capture["participant"]["participant_code"] == "W08-U01"
        assert capture["participant"]["consent_obtained"] is True
        assert capture["session"]["study_runtime_commit"] == "a" * 40
        assert len(capture["session"]["protocol_sha256"]) == 64
        participant_page = client.get("/participants/W08-U01")
        assert participant_page.status_code == 200
        assert "Prepare W08-U01" in participant_page.text
        assert "Moderate T1–T7" in participant_page.text

        task = client.post(
            "/participants/W08-U01/tasks/T1",
            data={
                "csrf": csrf,
                "outcome": "PASS",
                "elapsed_seconds": "142",
                "assistance_count": "0",
                "retained_identifiers": "brief-1\naudit-2",
                "deidentified_observation": "Located preserved history unaided.",
            },
            follow_redirects=False,
        )
        assert task.status_code == 303
        capture = yaml.safe_load(capture_path.read_text(encoding="utf-8"))
        assert capture["tasks"]["T1_role_brief"] == {
            "outcome": "PASS",
            "elapsed_seconds": 142,
            "assistance_count": 0,
            "retained_identifiers": ["brief-1", "audit-2"],
            "deidentified_observation": "Located preserved history unaided.",
        }
        assert capture["attestation"]["record_sha256"] is None

        review = client.post(
            "/participants/W08-U01/review",
            data={
                "csrf": csrf,
                "evidence_boundary_interpretation": "CORRECT",
                "unaided_confidence_1_to_5": "4",
                "access_denial_disclosed_object_existence": "false",
                "material_history_identifiable_and_reversible": "true",
                "keyboard_blocker": "false",
                "missing_label_landmark_or_visible_focus": "false",
                "horizontal_overflow": "false",
                "unrecoverable_state": "false",
                "non_loopback_requests_observed": "false",
                "findings": "P3: Minor wording preference.",
            },
            follow_redirects=False,
        )
        assert review.status_code == 303

        completed = client.post(
            "/participants/W08-U01/complete",
            data={
                "csrf": csrf,
                "participant_reviewed": "true",
                "no_sensitive_data": "true",
                "no_substitution": "true",
                "no_protected_w06": "true",
            },
            follow_redirects=False,
        )
        assert completed.status_code == 303
        capture = yaml.safe_load(capture_path.read_text(encoding="utf-8"))
        assert capture["status"] == "CAPTURE_COMPLETE_PENDING_MASTER_REPRODUCTION"
        assert capture["attestation"]["record_sha256"] is None
        assert capture["findings"] == ["P3: Minor wording preference."]


def test_pilot_mode_is_distinct_progression_evidence_and_never_increments_user_count(
    tmp_path: Path,
) -> None:
    app, study_parent, capture_root = _console(tmp_path)
    with TestClient(app) as client:
        csrf = _csrf(client)
        prepared = client.post(
            "/participants/W08-P01/consent",
            data={
                "csrf": csrf,
                "moderator_code": "PILOT-OP",
                "pilot_progression_acknowledged": "true",
            },
            follow_redirects=False,
        )
        assert prepared.status_code == 303

        pilot_path = study_parent / "w08-pilot-captures/W08-P01.yaml"
        assert pilot_path.is_file()
        assert not (capture_root / "W08-P01.yaml").exists()
        pilot = yaml.safe_load(pilot_path.read_text(encoding="utf-8"))
        assert pilot["record_type"] == "w08_pilot_progression_capture"
        assert pilot["status"] == "PILOT_IN_PROGRESS_DEVELOPMENT_EVIDENCE"
        assert pilot["pilot"] == {
            "gate_id": "G-W08A",
            "progression_gate_evidence": True,
            "representative_acceptance_evidence": False,
            "development_progression_boundary_acknowledged": True,
            "purpose": "end_to_end_smoke_test_and_development_progression_review",
        }
        assert pilot["participant"]["consent_obtained"] is False
        assert pilot["participant"]["qualification_confirmed_by_authorised_study_owner"] is False

        pilot_page = client.get("/participants/W08-P01")
        assert pilot_page.status_code == 200
        assert "Development pilot workspace" in pilot_page.text
        assert "can never count toward the five-user G-W08B/G4 gate" in pilot_page.text

        started = client.post(
            "/participants/W08-P01/start",
            data={"csrf": csrf, "port": str(_free_port())},
            follow_redirects=False,
        )
        assert started.status_code == 303
        assert app.state.manager.sessions["W08-P01"].running
        pilot_session = app.state.manager.sessions["W08-P01"]
        assert pilot_session.guided_study is True
        assert pilot_session.app.state.guided_study is True
        with TestClient(pilot_session.app) as pilot_client:
            guided_landing = pilot_client.get("/w08")
            assert "Start guided journey" in guided_landing.text
            assert pilot_session.app.state.study_console_url == (
                "http://127.0.0.1:8767/participants/W08-P01"
            )
        stopped = client.post(
            "/participants/W08-P01/stop",
            data={"csrf": csrf},
            follow_redirects=False,
        )
        assert stopped.status_code == 303
        pilot = yaml.safe_load(pilot_path.read_text(encoding="utf-8"))
        assert len(pilot["session"]["local_database_receipt_sha256"]) == 64

        for task_id in ("T1", "T2", "T3", "T4", "T5", "T6", "T7"):
            updated = client.post(
                f"/participants/W08-P01/tasks/{task_id}",
                data={
                    "csrf": csrf,
                    "outcome": "PASS",
                    "elapsed_seconds": "1",
                    "assistance_count": "0",
                },
                follow_redirects=False,
            )
            assert updated.status_code == 303

        completed = client.post(
            "/participants/W08-P01/complete",
            data={
                "csrf": csrf,
                "participant_reviewed": "true",
                "no_sensitive_data": "true",
                "no_protected_w06": "true",
            },
            follow_redirects=False,
        )
        assert completed.status_code == 303
        pilot = yaml.safe_load(pilot_path.read_text(encoding="utf-8"))
        assert pilot["status"] == "PILOT_CAPTURE_COMPLETE_PENDING_G_W08A_REVIEW"
        assert (
            pilot["attestation"]["no_automated_persona_or_moderator_substituted_for_participant"]
            is False
        )

        dashboard = client.get("/")
        assert '<div class="gate-number"><strong>0</strong><span>/ 5</span></div>' in dashboard.text
        assert "G-W08A · PENDING · 1 submitted (1 required)" in dashboard.text


def test_console_requires_consent_csrf_and_bounded_codes(tmp_path: Path) -> None:
    app, _, _ = _console(tmp_path)
    with TestClient(app) as client:
        csrf = _csrf(client)
        no_consent = client.post(
            "/participants/W08-U01/start",
            data={"csrf": csrf, "port": str(_free_port())},
        )
        assert no_consent.status_code == 400
        assert "record qualification and consent" in no_consent.text

        missing_csrf = client.post(
            "/participants/W08-U01/consent",
            data={
                "responsibility_analyst": "true",
                "moderator_code": "MOD-01",
                "qualification_confirmed": "true",
                "consent_obtained": "true",
            },
        )
        assert missing_csrf.status_code == 400
        assert "form expired" in missing_csrf.text
        assert client.get("/participants/W08-U99").status_code == 400
        assert client.get("/", headers={"host": "example.test"}).status_code == 404


def test_console_starts_expires_and_stops_one_fresh_loopback_runtime(tmp_path: Path) -> None:
    app, study_parent, capture_root = _console(tmp_path)
    with TestClient(app) as console_client:
        csrf = _csrf(console_client)
        _consent(console_client, csrf)
        participant_port = _free_port()
        started = console_client.post(
            "/participants/W08-U01/start",
            data={"csrf": csrf, "port": str(participant_port)},
            follow_redirects=False,
        )
        assert started.status_code == 303
        session = app.state.manager.sessions["W08-U01"]
        assert session.running
        assert session.root == study_parent / "w08-study-W08-U01"
        assert session.port == participant_port
        assert session.guided_study is False
        assert session.app.state.guided_study is False
        assert session.app.state.workflow_evidence_origin.value == "human_entered_local"

        analyst = session.personas["analyst"]
        with TestClient(session.app) as participant_client:
            login = participant_client.post("/w08/login", data=analyst, follow_redirects=False)
            assert login.status_code == 303
            expired = console_client.post(
                "/participants/W08-U01/expire",
                data={"csrf": csrf, "role": "analyst"},
                follow_redirects=False,
            )
            assert expired.status_code == 303
            assert participant_client.get("/w08/queue").status_code == 401

        stopped = console_client.post(
            "/participants/W08-U01/stop",
            data={"csrf": csrf},
            follow_redirects=False,
        )
        assert stopped.status_code == 303
        assert not session.running
        assert session.personas == {}
        assert session.receipt is not None
        capture = yaml.safe_load((capture_root / "W08-U01.yaml").read_text(encoding="utf-8"))
        assert len(capture["session"]["local_database_receipt_sha256"]) == 64
        assert len(capture["session"]["local_export_root_receipt_sha256"]) == 64

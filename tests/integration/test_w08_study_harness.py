"""Synthetic automated tests for the W08 moderated-study harness mechanics."""

from __future__ import annotations

import importlib.util
import json
import re
from datetime import timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from scouting.contracts import WorkflowEvidenceOrigin
from scouting.policy import R1AuthenticationDenied
from scouting.web.w08 import create_w08_app

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts/run_w08_study.py"
_SPEC = importlib.util.spec_from_file_location("run_w08_study", _SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
run_w08_study = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run_w08_study)


def _login(client: TestClient, persona: dict[str, str]) -> str:
    assert client.post("/w08/login", data=persona, follow_redirects=False).status_code == 303
    csrf = client.cookies.get("w08_csrf")
    assert csrf is not None
    return csrf


def test_serve_requires_a_fresh_root_and_exact_loopback_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    captured: dict[str, object] = {}

    def no_listener(app: object, **kwargs: object) -> None:
        captured["app"] = app
        captured.update(kwargs)

    monkeypatch.setattr(run_w08_study.uvicorn, "run", no_listener)
    root = tmp_path / "fresh-study"
    run_w08_study.serve(root, 8768)
    output = capsys.readouterr().out

    assert root.is_dir()
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8768
    assert captured["access_log"] is False
    assert captured["log_level"] == "warning"
    assert (
        captured["app"].state.workflow_evidence_origin is WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL
    )
    assert "Synthetic setup accounts only" in output
    assert "representative-user evidence" in output
    with pytest.raises(run_w08_study.StudyHarnessError, match="new and unused"):
        run_w08_study.serve(root, 8768)
    with pytest.raises(run_w08_study.StudyHarnessError, match="unprivileged"):
        run_w08_study.serve(tmp_path / "bad-port", 1023)
    with pytest.raises(run_w08_study.StudyHarnessError, match="invalid local study root"):
        run_w08_study.serve(Path("/"), 8768)
    symlink = tmp_path / "linked-study"
    symlink.symlink_to(root, target_is_directory=True)
    with pytest.raises(run_w08_study.StudyHarnessError, match="invalid local study root"):
        run_w08_study.serve(symlink, 8768)


def test_expire_session_scopes_to_one_current_actor_and_authentication_then_denies(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    root.mkdir()
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=root / run_w08_study.DATABASE_NAME,
        allowed_root=root,
        seed=True,
    )
    analyst = app.state.synthetic_personas["analyst"]
    with app.state.engine.begin() as connection:
        token, _ = app.state.sessions.login(
            connection,
            actor_id=UUID(analyst["actor_id"]),
            password=analyst["password"],
            ttl=timedelta(minutes=10),
        )

    assert run_w08_study.expire_session(root, analyst["actor_id"]) == 1
    with app.state.engine.begin() as connection, pytest.raises(R1AuthenticationDenied):
        app.state.sessions.authenticate(connection, token=token)
    with pytest.raises(run_w08_study.StudyHarnessError, match="session unavailable"):
        run_w08_study.expire_session(root, str(uuid4()))
    with pytest.raises(run_w08_study.StudyHarnessError, match="runtime unavailable"):
        run_w08_study.expire_session(tmp_path / "missing", analyst["actor_id"])
    app.state.engine.dispose()


def test_human_mode_route_origin_is_server_selected_mechanics_only(tmp_path: Path) -> None:
    """Exercise a study-mode provenance label without creating participant evidence."""
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL,
        database_path=tmp_path / "human-mode.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = TestClient(app)
    analyst_csrf = _login(analyst, app.state.synthetic_personas["analyst"])
    created = analyst.post(
        "/w08/briefs",
        data={
            "csrf": analyst_csrf,
            "title": "Mechanical human-mode provenance witness",
            "responsibility": "progress_through_pressure",
        },
        follow_redirects=False,
    )
    assert created.status_code == 303
    brief_id = created.headers["location"].rsplit("/", 1)[-1]
    assert (
        analyst.post(
            f"/w08/briefs/{brief_id}/status/submit",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    approver = TestClient(app)
    approver_csrf = _login(approver, app.state.synthetic_personas["approver"])
    assert (
        approver.post(
            f"/w08/briefs/{brief_id}/status/approve",
            data={"csrf": approver_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        analyst.post(
            f"/w08/briefs/{brief_id}/retrieval",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    with app.state.engine.connect() as connection:
        link_id = str(
            connection.execute(
                text("SELECT retrieval_link_id FROM replayable_retrieval_links LIMIT 1")
            ).scalar_one()
        )
    shortlist = analyst.post(
        f"/w08/briefs/{brief_id}/shortlists",
        data={"csrf": analyst_csrf, "retrieval_link_id": link_id, "title": "Mechanical shortlist"},
        follow_redirects=False,
    )
    assert shortlist.status_code == 303
    shortlist_path = shortlist.headers["location"]
    candidate = re.search(
        r'name="candidate_selection"[^>]*>.*?value="([^"]+)"',
        analyst.get(shortlist_path).text,
        flags=re.DOTALL,
    )
    assert candidate is not None
    entry = analyst.post(
        f"{shortlist_path}/entries",
        data={
            "csrf": analyst_csrf,
            "candidate_selection": candidate.group(1),
            "rationale": "Mechanical provenance-only setup",
        },
        follow_redirects=False,
    )
    assert entry.status_code == 303
    entry_path = entry.headers["location"]
    scout_persona = app.state.synthetic_personas["scout"]
    assert (
        analyst.post(
            f"{entry_path}/transition",
            data={
                "csrf": analyst_csrf,
                "expected_lock_version": "1",
                "state": "scout",
                "assigned_scout_id": scout_persona["actor_id"],
                "transition_reason": "Mechanical route setup",
            },
            follow_redirects=False,
        ).status_code
        == 303
    )
    scout = TestClient(app)
    scout_csrf = _login(scout, scout_persona)
    observation = {
        "csrf": scout_csrf,
        "visibility": "TEAM",
        "overall_confidence": "0.5",
        "summary": "Mechanical origin witness, not a participant result",
        "disagreement": "no",
        "recommended_next_action": "No study conclusion",
        "evidence_kind": "local_note",
        "evidence_reference": "mechanical/origin-witness",
        "evidence_origin": "synthetic_automated_test",
    }
    for dimension in (
        "role_execution",
        "decision_making",
        "technical_execution",
        "off_ball_contribution",
        "context_and_risk",
    ):
        observation.update(
            {
                f"{dimension}_rating": "3",
                f"{dimension}_confidence": "0.5",
                f"{dimension}_note": "Mechanical provenance-only fixture",
            }
        )
    assert (
        scout.post(
            f"{entry_path}/observations", data=observation, follow_redirects=False
        ).status_code
        == 303
    )
    rendered = scout.get(entry_path)
    assert "human_entered_local" in rendered.text
    assert "Mechanical origin witness, not a participant result" in rendered.text
    with app.state.engine.connect() as connection:
        assert connection.execute(
            text("SELECT evidence_origin FROM scout_observations")
        ).scalar_one() == ("human_entered_local")
        assert (
            len(
                str(
                    connection.execute(
                        text(
                            "SELECT after_digest FROM audit_events "
                            "WHERE target_type='scout_observation'"
                        )
                    ).scalar_one()
                )
            )
            == 64
        )
    exported = analyst.post(
        "/w08/exports",
        data={
            "csrf": analyst_csrf,
            "role_brief_id": brief_id,
            "role_brief_version": "3",
            "retrieval_link_id": link_id,
            "shortlist_id": shortlist_path.rsplit("/", 1)[-1],
            "evidence_origin": "synthetic_automated_test",
        },
        follow_redirects=False,
    )
    assert exported.status_code == 303
    pack_id = exported.headers["location"].rsplit("/", 1)[-1]
    pack = next(tmp_path.rglob(f"{pack_id}.json"))
    assert json.loads(pack.read_text(encoding="utf-8"))["workflow_action_origins"] == [
        "human_entered_local"
    ]
    app.state.engine.dispose()


def test_expire_session_refuses_an_ambiguous_actor_session_set(tmp_path: Path) -> None:
    root = tmp_path / "study"
    root.mkdir()
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=root / run_w08_study.DATABASE_NAME,
        allowed_root=root,
        seed=True,
    )
    analyst = app.state.synthetic_personas["analyst"]
    with app.state.engine.begin() as connection:
        for _ in range(2):
            app.state.sessions.login(
                connection,
                actor_id=UUID(analyst["actor_id"]),
                password=analyst["password"],
                ttl=timedelta(minutes=10),
            )
    with pytest.raises(run_w08_study.StudyHarnessError, match="session unavailable"):
        run_w08_study.expire_session(root, analyst["actor_id"])
    app.state.engine.dispose()


def test_receipt_is_stable_and_contains_no_credentials_or_participant_outcomes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    root.mkdir()
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=root / run_w08_study.DATABASE_NAME,
        allowed_root=root,
        seed=True,
    )
    app.state.engine.dispose()
    evidence = root / run_w08_study.EVIDENCE_PACK_DIRECTORY / "packs"
    evidence.mkdir(parents=True)
    (evidence / "local-pack.json").write_text('{"classification":"local"}', encoding="utf-8")

    first = run_w08_study.receipt(root)
    second = run_w08_study.receipt(root)

    assert first == second
    assert first["status"] == "mechanical_receipt_only"
    assert first["export_file_count"] == 1
    encoded = json.dumps(first, sort_keys=True)
    assert "password" not in encoded.lower()
    assert "participant" not in encoded.lower()
    assert len(str(first["database_sha256"])) == 64
    assert len(str(first["export_manifest_sha256"])) == 64


def test_receipt_fails_closed_when_runtime_wal_or_evidence_symlink_is_present(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    root.mkdir()
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=root / run_w08_study.DATABASE_NAME,
        allowed_root=root,
        seed=True,
    )
    app.state.engine.dispose()
    wal = root / f"{run_w08_study.DATABASE_NAME}-wal"
    wal.write_bytes(b"not a live receipt")
    with pytest.raises(run_w08_study.StudyHarnessError, match="must be stopped"):
        run_w08_study.receipt(root)
    wal.unlink()
    evidence = root / run_w08_study.EVIDENCE_PACK_DIRECTORY
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "escape").symlink_to(tmp_path)
    with pytest.raises(run_w08_study.StudyHarnessError, match="receipt unavailable"):
        run_w08_study.receipt(root)

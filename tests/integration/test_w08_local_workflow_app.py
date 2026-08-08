"""Synthetic automated TestClient witnesses for the local W08 presentation seam."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from scouting.contracts import WorkflowEvidenceOrigin
from scouting.policy import LocalRole
from scouting.web import w08
from scouting.web.w08 import create_w08_app


def _login(client: TestClient, persona: dict[str, str]) -> str:
    assert client.post("/w08/login", data=persona, follow_redirects=False).status_code == 303
    csrf = client.cookies.get("w08_csrf")
    assert csrf is not None
    return csrf


def _retained_brief_form(csrf: str, *, title: str, responsibility: str) -> dict[str, str]:
    return {
        "csrf": csrf,
        "title": title,
        "responsibility": responsibility,
        "constraint_field": "synthetic_age_years",
        "constraint_operator": "at_most",
        "constraint_value": "40",
        "preference_dimension": responsibility,
        "preference_weight": "0.5",
        "exemplar_player_ids": "20000000-0000-4000-8000-000000000001",
    }


def test_guided_pilot_has_one_click_roles_and_contextual_next_actions(tmp_path: Path) -> None:
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL,
        database_path=tmp_path / "w08-guided.sqlite3",
        allowed_root=tmp_path,
        guided_study=True,
        study_console_url="http://127.0.0.1:8767/participants/W08-P02",
    )
    client = TestClient(app)
    landing = client.get("/w08")
    assert landing.status_code == 200
    assert "Start guided journey" in landing.text
    assert "The guide handles synthetic role changes for you" in landing.text
    token_match = re.search(r'name="guide_csrf" value="([^"]+)"', landing.text)
    assert token_match is not None
    guide_csrf = token_match.group(1)

    missing_csrf = client.post(
        "/w08/guide/switch-role",
        data={"role": "analyst", "return_to": "/w08/guide"},
    )
    assert missing_csrf.status_code == 403
    switched = client.post(
        "/w08/guide/switch-role",
        data={
            "guide_csrf": guide_csrf,
            "role": "analyst",
            "return_to": "/w08/guide",
        },
        follow_redirects=False,
    )
    assert switched.status_code == 303
    assert switched.headers["location"] == "/w08/guide"
    guide = client.get("/w08/guide")
    assert "Working as Analyst" in guide.text
    assert "Follow one journey from brief to evidence" in guide.text
    assert "http://127.0.0.1:8767/participants/W08-P02#tasks" in guide.text

    csrf = str(client.cookies.get("w08_csrf"))
    created = client.post(
        "/w08/briefs",
        data=_retained_brief_form(
            csrf,
            title="Guided pilot brief",
            responsibility="progress_through_pressure",
        ),
        follow_redirects=False,
    )
    assert created.status_code == 303
    brief_path = created.headers["location"]
    assert (
        client.post(
            f"{brief_path}/status/submit",
            data={"csrf": csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    submitted = client.get(brief_path)
    assert "T2 · Continue as Approver" in submitted.text

    as_approver = client.post(
        "/w08/guide/switch-role",
        data={
            "guide_csrf": guide_csrf,
            "role": "approver",
            "return_to": brief_path,
        },
        follow_redirects=True,
    )
    assert as_approver.status_code == 200
    assert "Working as Approver" in as_approver.text
    assert "T2 · Approve this submitted brief" in as_approver.text
    assert "Approve brief" in as_approver.text

    bounded_redirect = client.post(
        "/w08/guide/switch-role",
        data={
            "guide_csrf": guide_csrf,
            "role": "analyst",
            "return_to": "https://example.test/escape",
        },
        follow_redirects=False,
    )
    assert bounded_redirect.status_code == 303
    assert bounded_redirect.headers["location"] == "/w08/guide"


def test_guided_role_switch_is_absent_from_standard_runtime(tmp_path: Path) -> None:
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08-standard.sqlite3",
        allowed_root=tmp_path,
    )
    client = TestClient(app)
    assert client.get("/w08/guide").status_code == 404
    assert client.post("/w08/guide/switch-role", data={}).status_code == 404
    assert "Start guided journey" not in client.get("/w08").text


def test_synthetic_automated_login_brief_and_denial(tmp_path: Path) -> None:
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = app.state.synthetic_personas["analyst"]
    client = TestClient(app)
    assert client.get("/w08/queue").status_code == 401
    response = client.post("/w08/login", data=analyst, follow_redirects=True)
    assert response.status_code == 200
    assert "Synthetic automated tests are not representative-user evidence" in response.text
    brief = client.post(
        "/w08/briefs",
        data=_retained_brief_form(
            str(client.cookies.get("w08_csrf")),
            title="Synthetic test",
            responsibility="progress_through_pressure",
        ),
    )
    assert brief.status_code == 200
    assert "Role brief history" in brief.text
    assert client.get("/w08/audit").status_code == 403
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["cache-control"] == "no-store"


def test_synthetic_automated_scout_brief_and_replay_authorization_matrix(tmp_path: Path) -> None:
    """Adversarial route witness for the W08 scout brief/replay disclosure boundary.

    This is synthetic automated access-control evidence, not scout or representative-user
    evidence.  It proves that brief visibility and replay-link visibility are separate
    decisions and that analyst+scout grants compose by union.
    """
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = TestClient(app)
    analyst_csrf = _login(analyst, app.state.synthetic_personas["analyst"])
    approver = TestClient(app)
    approver_csrf = _login(approver, app.state.synthetic_personas["approver"])
    scout = TestClient(app)
    _login(scout, app.state.synthetic_personas["scout"])

    def create_brief(title: str) -> str:
        response = analyst.post(
            "/w08/briefs",
            data=_retained_brief_form(
                analyst_csrf, title=title, responsibility="progress_through_pressure"
            ),
            follow_redirects=False,
        )
        assert response.status_code == 303
        return response.headers["location"].rsplit("/", 1)[-1]

    # A scout-only account cannot enumerate any pre-approval lifecycle state.
    draft_id = create_brief("SCOUT-DRAFT-MARKER")
    submitted_id = create_brief("SCOUT-SUBMITTED-MARKER")
    assert (
        analyst.post(
            f"/w08/briefs/{submitted_id}/status/submit",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    rejected_id = create_brief("SCOUT-REJECTED-MARKER")
    assert (
        analyst.post(
            f"/w08/briefs/{rejected_id}/status/submit",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        approver.post(
            f"/w08/briefs/{rejected_id}/status/reject",
            data={
                "csrf": approver_csrf,
                "rejection_reason": "requirements_unclear",
                "decision_note": "Synthetic rejection",
            },
            follow_redirects=False,
        ).status_code
        == 303
    )
    scout_queue = scout.get("/w08/queue")
    assert scout_queue.status_code == 200
    for marker, brief_id in (
        ("SCOUT-DRAFT-MARKER", draft_id),
        ("SCOUT-SUBMITTED-MARKER", submitted_id),
        ("SCOUT-REJECTED-MARKER", rejected_id),
    ):
        assert marker not in scout_queue.text
        assert scout.get(f"/w08/briefs/{brief_id}").status_code == 404

    approved_id = create_brief("SCOUT-APPROVED-MARKER")
    assert (
        analyst.post(
            f"/w08/briefs/{approved_id}/status/submit",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        approver.post(
            f"/w08/briefs/{approved_id}/status/approve",
            data={"csrf": approver_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        analyst.post(
            f"/w08/briefs/{approved_id}/retrieval",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    with app.state.engine.connect() as connection:
        link_id = str(
            connection.execute(
                text(
                    "SELECT retrieval_link_id FROM replayable_retrieval_links "
                    "WHERE role_brief_id=:brief"
                ),
                {"brief": approved_id},
            ).scalar_one()
        )

    # Approved brief metadata is visible to a scout, but the exact replay link and
    # candidate controls remain absent until a current assignment exists.
    unassigned_detail = scout.get(f"/w08/briefs/{approved_id}")
    assert unassigned_detail.status_code == 200
    assert "SCOUT-APPROVED-MARKER" in unassigned_detail.text
    assert "Exact local replay projection" not in unassigned_detail.text
    assert link_id not in unassigned_detail.text
    assert 'name="candidate_selection"' not in unassigned_detail.text
    assert "Query digest and mode" not in unassigned_detail.text
    assert "Synthetic resemblance candidate" not in unassigned_detail.text

    shortlist = analyst.post(
        f"/w08/briefs/{approved_id}/shortlists",
        data={"csrf": analyst_csrf, "retrieval_link_id": link_id, "title": "Scoped shortlist"},
        follow_redirects=False,
    )
    shortlist_id = shortlist.headers["location"].rsplit("/", 1)[-1]
    # No linked entry assignment means the scout cannot obtain a separate shortlist
    # projection as an alternative path to the exact replay link or candidate list.
    assert scout.get(shortlist.headers["location"]).status_code == 404
    approver_scout_id, approver_scout_password = uuid4(), "synthetic-approver-scout"
    with app.state.engine.begin() as connection:
        app.state.sessions.create_account(
            connection,
            actor_id=approver_scout_id,
            tenant_id=UUID(app.state.synthetic_personas["scout"]["tenant_id"]),
            display_name="Synthetic mixed approver scout",
            password=approver_scout_password,
            roles=(LocalRole.APPROVER, LocalRole.SCOUT),
            assigned_by=UUID(app.state.synthetic_personas["admin"]["actor_id"]),
        )
    approver_scout = TestClient(app)
    _login(
        approver_scout,
        {"actor_id": str(approver_scout_id), "password": approver_scout_password},
    )
    # The explicit approver shortlist.read grant remains effective even though
    # scout-only access would require a current assignment.
    assert approver_scout.get(shortlist.headers["location"]).status_code == 200
    shortlist_page = analyst.get(shortlist.headers["location"])
    selection = re.search(
        r'name="candidate_selection"[^>]*>.*?value="([^"]+)"',
        shortlist_page.text,
        re.DOTALL,
    )
    assert selection is not None
    entry = analyst.post(
        f"/w08/shortlists/{shortlist_id}/entries",
        data={
            "csrf": analyst_csrf,
            "candidate_selection": selection.group(1),
            "rationale": "synthetic",
        },
        follow_redirects=False,
    )
    entry_id = entry.headers["location"].rsplit("/", 1)[-1]
    scout_id = app.state.synthetic_personas["scout"]["actor_id"]
    assert (
        analyst.post(
            f"/w08/entries/{entry_id}/transition",
            data={
                "csrf": analyst_csrf,
                "expected_lock_version": "1",
                "state": "scout",
                "assigned_scout_id": scout_id,
                "transition_reason": "synthetic assignment",
                "next_action": "scout review",
                "next_action_owner_id": scout_id,
            },
            follow_redirects=False,
        ).status_code
        == 303
    )
    assigned_detail = scout.get(f"/w08/briefs/{approved_id}")
    assert assigned_detail.status_code == 200
    assert "Exact local replay projection" in assigned_detail.text
    assert link_id in assigned_detail.text
    assert scout.get(shortlist.headers["location"]).status_code == 200
    assert scout.get(f"/w08/entries/{entry_id}").status_code == 200

    # Reassignment removes the former scout's replay projection and grants it only
    # to the new current assignee; it does not rely on same-tenant membership.
    second_scout_id, second_password = uuid4(), "synthetic-reassigned-scout"
    with app.state.engine.begin() as connection:
        app.state.sessions.create_account(
            connection,
            actor_id=second_scout_id,
            tenant_id=UUID(app.state.synthetic_personas["scout"]["tenant_id"]),
            display_name="Synthetic reassigned scout",
            password=second_password,
            roles=(LocalRole.SCOUT,),
            assigned_by=UUID(app.state.synthetic_personas["admin"]["actor_id"]),
        )
    second_scout = TestClient(app)
    _login(second_scout, {"actor_id": str(second_scout_id), "password": second_password})
    with app.state.engine.connect() as connection:
        clear_assignment_lock = str(
            connection.execute(
                text(
                    "SELECT lock_version FROM shortlist_entry_workflows "
                    "WHERE shortlist_entry_id=:entry"
                ),
                {"entry": entry_id},
            ).scalar_one()
        )
    assert (
        analyst.post(
            f"/w08/entries/{entry_id}/transition",
            data={
                "csrf": analyst_csrf,
                "expected_lock_version": clear_assignment_lock,
                "state": "monitor",
                "assigned_scout_id": "",
                "transition_reason": "synthetic assignment clearance",
                "next_action": "assign replacement scout",
                "next_action_owner_id": app.state.synthetic_personas["analyst"]["actor_id"],
            },
            follow_redirects=False,
        ).status_code
        == 303
    )
    former_detail = scout.get(f"/w08/briefs/{approved_id}")
    assert "Exact local replay projection" not in former_detail.text
    assert link_id not in former_detail.text
    assert 'name="candidate_selection"' not in former_detail.text
    assert "Query digest and mode" not in former_detail.text
    assert "Synthetic resemblance candidate" not in former_detail.text
    assert scout.get(shortlist.headers["location"]).status_code == 404
    assert scout.get(f"/w08/entries/{entry_id}").status_code == 404
    with app.state.engine.connect() as connection:
        reassign_lock = str(
            connection.execute(
                text(
                    "SELECT lock_version FROM shortlist_entry_workflows "
                    "WHERE shortlist_entry_id=:entry"
                ),
                {"entry": entry_id},
            ).scalar_one()
        )
    assert (
        analyst.post(
            f"/w08/entries/{entry_id}/transition",
            data={
                "csrf": analyst_csrf,
                "expected_lock_version": reassign_lock,
                "state": "scout",
                "assigned_scout_id": str(second_scout_id),
                "transition_reason": "synthetic reassignment",
                "next_action": "replacement scout review",
                "next_action_owner_id": str(second_scout_id),
            },
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert "Exact local replay projection" in second_scout.get(f"/w08/briefs/{approved_id}").text

    # A mixed analyst+scout principal reads an own draft through the analyst grant;
    # scout presence cannot override that explicit grant.
    mixed_id, mixed_password = uuid4(), "synthetic-mixed-role"
    with app.state.engine.begin() as connection:
        app.state.sessions.create_account(
            connection,
            actor_id=mixed_id,
            tenant_id=UUID(app.state.synthetic_personas["analyst"]["tenant_id"]),
            display_name="Synthetic mixed analyst scout",
            password=mixed_password,
            roles=(LocalRole.ANALYST, LocalRole.SCOUT),
            assigned_by=UUID(app.state.synthetic_personas["admin"]["actor_id"]),
        )
    mixed = TestClient(app)
    mixed_csrf = _login(mixed, {"actor_id": str(mixed_id), "password": mixed_password})
    mixed_created = mixed.post(
        "/w08/briefs",
        data=_retained_brief_form(
            mixed_csrf, title="MIXED-OWN-DRAFT-MARKER", responsibility="progress_through_pressure"
        ),
        follow_redirects=False,
    )
    assert mixed_created.status_code == 303
    assert mixed.get(mixed_created.headers["location"]).status_code == 200

    # The same analyst+scout account keeps its independent shortlist.read grant:
    # scout presence cannot turn an empty owner shortlist into a 404.  OWNER_ONLY
    # remains owner-scoped, rather than becoming scout-readable generally.
    mixed_brief_id = mixed_created.headers["location"].rsplit("/", 1)[-1]
    assert (
        mixed.post(
            f"/w08/briefs/{mixed_brief_id}/status/submit",
            data={"csrf": mixed_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        approver.post(
            f"/w08/briefs/{mixed_brief_id}/status/approve",
            data={"csrf": approver_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        mixed.post(
            f"/w08/briefs/{mixed_brief_id}/retrieval",
            data={"csrf": mixed_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    with app.state.engine.connect() as connection:
        mixed_link_id = str(
            connection.execute(
                text(
                    "SELECT retrieval_link_id FROM replayable_retrieval_links "
                    "WHERE role_brief_id=:brief"
                ),
                {"brief": mixed_brief_id},
            ).scalar_one()
        )
    for visibility in ("TEAM", "OWNER_ONLY"):
        response = mixed.post(
            f"/w08/briefs/{mixed_brief_id}/shortlists",
            data={
                "csrf": mixed_csrf,
                "retrieval_link_id": mixed_link_id,
                "title": f"MIXED-{visibility}-SHORTLIST",
                "visibility": visibility,
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert mixed.get(response.headers["location"]).status_code == 200
        if visibility == "OWNER_ONLY":
            assert scout.get(response.headers["location"]).status_code == 404

    # The private counterpart is an approved brief with an exact replay link, but
    # remains generically absent to a non-owner scout even after approval.  The
    # direct database fixture models the retained OWNER_ONLY workflow state; the
    # route assertions remain the actual user-visible confidentiality witness.
    owner_only_id = create_brief("SCOUT-OWNER-ONLY-MARKER")
    assert (
        analyst.post(
            f"/w08/briefs/{owner_only_id}/status/submit",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        approver.post(
            f"/w08/briefs/{owner_only_id}/status/approve",
            data={"csrf": approver_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        analyst.post(
            f"/w08/briefs/{owner_only_id}/retrieval",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    with app.state.engine.begin() as connection:
        connection.execute(text("DROP TRIGGER role_brief_revisions_reject_update"))
        connection.execute(
            text(
                "UPDATE role_brief_revisions SET visibility='OWNER_ONLY' WHERE role_brief_id=:brief"
            ),
            {"brief": owner_only_id},
        )
        connection.execute(
            text(
                "UPDATE role_brief_workflows SET visibility='OWNER_ONLY' WHERE role_brief_id=:brief"
            ),
            {"brief": owner_only_id},
        )
    owner_only_queue = scout.get("/w08/queue")
    assert "SCOUT-OWNER-ONLY-MARKER" not in owner_only_queue.text
    owner_only_detail = scout.get(f"/w08/briefs/{owner_only_id}")
    assert owner_only_detail.status_code == 404
    assert "Exact local replay projection" not in owner_only_detail.text

    # An identical UUID in another local tenant is a generic 404, preserving the
    # cross-object/cross-tenant non-disclosure boundary.
    foreign_root = tmp_path / "foreign"
    foreign_app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=foreign_root / "w08.sqlite3",
        allowed_root=foreign_root,
    )
    foreign_scout = TestClient(foreign_app)
    _login(foreign_scout, foreign_app.state.synthetic_personas["scout"])
    assert foreign_scout.get(f"/w08/briefs/{approved_id}").status_code == 404
    assert foreign_scout.get(shortlist.headers["location"]).status_code == 404
    assert foreign_scout.get(f"/w08/entries/{entry_id}").status_code == 404


def test_synthetic_automated_csrf_and_unknown_object_denial(tmp_path: Path) -> None:
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = app.state.synthetic_personas["analyst"]
    client = TestClient(app)
    client.post("/w08/login", data=analyst)
    assert client.post("/w08/briefs", data={"title": "x", "responsibility": "x"}).status_code == 401
    client.cookies.clear()
    assert client.post("/w08/briefs", data={"title": "x", "responsibility": "x"}).status_code == 401
    assert client.get("/w08/briefs/00000000-0000-4000-8000-000000000001").status_code == 401


def test_synthetic_automated_mutations_need_submitted_csrf_not_cookie(tmp_path: Path) -> None:
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = app.state.synthetic_personas["analyst"]
    client = TestClient(app)
    client.post("/w08/login", data=analyst)
    response = client.post(
        "/w08/briefs",
        data={"title": "Synthetic test", "responsibility": "progress", "csrf": "wrong"},
    )
    assert response.status_code == 401
    assert "Action unavailable" in response.text


def test_synthetic_automated_six_version_brief_witness_and_atomic_denials(
    tmp_path: Path,
) -> None:
    """Synthetic TestClient witness; it is not representative-user evidence."""
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = TestClient(app)
    analyst_csrf = _login(analyst, app.state.synthetic_personas["analyst"])
    queue = analyst.get("/w08/queue")
    for retained_value in (
        "w08-local-template",
        "w05-football-responsibility-taxonomy-v1",
        "advance_play_final_third",
        "progress_through_pressure",
        "synthetic_age_years",
        "Public W07 query player 20000000-0000-4000-8000-000000000001",
    ):
        assert retained_value in queue.text

    original = _retained_brief_form(
        analyst_csrf,
        title="Original retained interpretation",
        responsibility="advance_play_final_third",
    )
    created = analyst.post("/w08/briefs", data=original, follow_redirects=False)
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
    rejected = approver.post(
        f"/w08/briefs/{brief_id}/status/reject",
        data={
            "csrf": approver_csrf,
            "rejection_reason": "requirements_unclear",
            "decision_note": "Synthetic controlled rejection note",
        },
        follow_redirects=False,
    )
    assert rejected.status_code == 303

    corrected = _retained_brief_form(
        analyst_csrf,
        title="Corrected retained interpretation",
        responsibility="progress_through_pressure",
    )
    corrected["expected_lock_version"] = "3"
    assert (
        analyst.post(
            f"/w08/briefs/{brief_id}/correct", data=corrected, follow_redirects=False
        ).status_code
        == 303
    )
    assert (
        analyst.post(
            f"/w08/briefs/{brief_id}/status/submit",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        approver.post(
            f"/w08/briefs/{brief_id}/status/approve",
            data={"csrf": approver_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )

    with app.state.engine.connect() as connection:
        rows = (
            connection.execute(
                text("SELECT * FROM role_brief_revisions WHERE role_brief_id=:id ORDER BY version"),
                {"id": brief_id},
            )
            .mappings()
            .all()
        )
        lock = (
            connection.execute(
                text(
                    "SELECT lock_version,latest_version FROM role_brief_workflows "
                    "WHERE role_brief_id=:id"
                ),
                {"id": brief_id},
            )
            .mappings()
            .one()
        )
        receipts = connection.execute(
            text(
                "SELECT count(*) FROM audit_receipts r JOIN audit_events e "
                "ON e.audit_event_id=r.audit_event_id "
                "WHERE e.target_type='role_brief' AND e.target_id=:id"
            ),
            {"id": brief_id},
        ).scalar_one()
    assert [row["version"] for row in rows] == [1, 2, 3, 4, 5, 6]
    assert [row["status"] for row in rows] == [
        "draft",
        "submitted",
        "rejected",
        "draft",
        "submitted",
        "approved",
    ]
    original_fields = (
        "title",
        "responsibilities",
        "hard_constraints",
        "preferences",
        "exemplar_player_ids",
    )
    corrected_fields = original_fields
    assert all(
        rows[0][field] == rows[index][field] for index in (1, 2) for field in original_fields
    )
    assert all(
        rows[3][field] == rows[index][field] for index in (4, 5) for field in corrected_fields
    )
    assert rows[2]["rejection_reason"] == "requirements_unclear"
    assert rows[2]["decision_note"] == "Synthetic controlled rejection note"
    assert rows[3]["submitted_at"] is None and rows[3]["decided_at"] is None
    assert rows[3]["decided_by"] is None and rows[3]["rejection_reason"] is None
    immutable = ("template_id", "taxonomy_version", "trace_id", "owner_id")
    assert all(rows[0][field] == row[field] for row in rows for field in immutable)
    analyst_id = app.state.synthetic_personas["analyst"]["actor_id"]
    approver_id = app.state.synthetic_personas["approver"]["actor_id"]
    assert [str(row["created_by"]) for row in rows] == [
        analyst_id,
        analyst_id,
        approver_id,
        analyst_id,
        analyst_id,
        approver_id,
    ]
    assert all(row["created_at"] is not None for row in rows)
    assert rows[1]["submitted_at"] is not None and rows[2]["submitted_at"] is not None
    assert rows[4]["submitted_at"] is not None and rows[5]["submitted_at"] is not None
    assert rows[2]["decided_at"] is not None and rows[5]["decided_at"] is not None
    assert lock == {"lock_version": 6, "latest_version": 6}
    assert receipts == 6

    history = analyst.get(f"/w08/briefs/{brief_id}")
    assert history.status_code == 200
    assert "retained replay context" in history.text
    assert "not quality evidence" in history.text
    assert '<th scope="col">Version/status</th>' in history.text

    def counts() -> tuple[int, int, int]:
        with app.state.engine.connect() as connection:
            return (
                connection.execute(
                    text("SELECT count(*) FROM role_brief_revisions WHERE role_brief_id=:id"),
                    {"id": brief_id},
                ).scalar_one(),
                connection.execute(
                    text("SELECT lock_version FROM role_brief_workflows WHERE role_brief_id=:id"),
                    {"id": brief_id},
                ).scalar_one(),
                connection.execute(
                    text(
                        "SELECT count(*) FROM audit_events WHERE target_type='role_brief' "
                        "AND target_id=:id"
                    ),
                    {"id": brief_id},
                ).scalar_one(),
            )

    before = counts()
    scout = TestClient(app)
    scout_csrf = _login(scout, app.state.synthetic_personas["scout"])
    admin = TestClient(app)
    admin_csrf = _login(admin, app.state.synthetic_personas["admin"])
    invalid_forms = (
        {**original, "responsibility": "invented_responsibility"},
        {**original, "constraint_operator": "equals"},
        {**original, "preference_weight": "0.7"},
        {**original, "exemplar_player_ids": str(uuid4())},
    )
    for form in invalid_forms:
        assert analyst.post("/w08/briefs", data=form, follow_redirects=False).status_code == 403
        assert counts() == before
    assert (
        scout.post(
            "/w08/briefs", data={**original, "csrf": scout_csrf}, follow_redirects=False
        ).status_code
        == 403
    )
    assert (
        admin.post(
            "/w08/briefs", data={**original, "csrf": admin_csrf}, follow_redirects=False
        ).status_code
        == 403
    )
    assert (
        approver.post(
            f"/w08/briefs/{brief_id}/status/reject",
            data={"csrf": approver_csrf, "rejection_reason": "invented", "decision_note": "x"},
            follow_redirects=False,
        ).status_code
        == 403
    )
    assert (
        analyst.post(
            f"/w08/briefs/{brief_id}/correct",
            data={**corrected, "expected_lock_version": "3"},
            follow_redirects=False,
        ).status_code
        == 403
    )
    assert (
        analyst.post(
            f"/w08/briefs/{brief_id}/status/submit",
            data={"csrf": "bad"},
            follow_redirects=False,
        ).status_code
        == 403
    )
    assert counts() == before

    foreign_app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "foreign.sqlite3",
        allowed_root=tmp_path,
    )
    foreign = TestClient(foreign_app)
    foreign_csrf = _login(foreign, foreign_app.state.synthetic_personas["analyst"])
    assert (
        foreign.post(
            f"/w08/briefs/{brief_id}/status/submit",
            data={"csrf": foreign_csrf},
            follow_redirects=False,
        ).status_code
        == 403
    )
    assert counts() == before


def test_synthetic_automated_complete_authorised_export_journey_witness(tmp_path: Path) -> None:
    """Exercise the complete local export journey; this is not human-study evidence."""
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = TestClient(app)
    analyst_csrf = _login(analyst, app.state.synthetic_personas["analyst"])
    approver = TestClient(app)
    approver_csrf = _login(approver, app.state.synthetic_personas["approver"])

    created = analyst.post(
        "/w08/briefs",
        data=_retained_brief_form(
            analyst_csrf,
            title="Synthetic complete authorised export journey",
            responsibility="progress_through_pressure",
        ),
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
        retrieval_link_id = str(
            connection.execute(
                text(
                    "SELECT retrieval_link_id FROM replayable_retrieval_links "
                    "WHERE role_brief_id=:brief"
                ),
                {"brief": brief_id},
            ).scalar_one()
        )
    shortlist_response = analyst.post(
        f"/w08/briefs/{brief_id}/shortlists",
        data={
            "csrf": analyst_csrf,
            "retrieval_link_id": retrieval_link_id,
            "title": "Synthetic TEAM export shortlist",
            "visibility": "TEAM",
        },
        follow_redirects=False,
    )
    assert shortlist_response.status_code == 303
    shortlist_path = shortlist_response.headers["location"]
    shortlist = analyst.get(shortlist_path)
    assert shortlist.status_code == 200

    def hidden(name: str) -> str:
        match = re.search(rf'name="{name}" value="([^"]+)"', shortlist.text)
        assert match is not None
        return match.group(1)

    export_form = {
        "csrf": analyst_csrf,
        "role_brief_id": hidden("role_brief_id"),
        "role_brief_version": hidden("role_brief_version"),
        "shortlist_id": hidden("shortlist_id"),
        "retrieval_link_id": hidden("retrieval_link_id"),
    }
    assert export_form == {
        "csrf": analyst_csrf,
        "role_brief_id": brief_id,
        "role_brief_version": "3",
        "shortlist_id": shortlist_path.rsplit("/", 1)[-1],
        "retrieval_link_id": retrieval_link_id,
    }
    first_export = analyst.post("/w08/exports", data=export_form, follow_redirects=False)
    assert first_export.status_code == 303
    export_path = first_export.headers["location"]
    pack_id = export_path.rsplit("/", 1)[-1]
    verified = analyst.get(export_path)
    assert verified.status_code == 200
    for safe_value in (
        "Classification",
        "w08_local_confidential_synthetic_workflow",
        "resemblance_only",
        "synthetic_development_only",
        "LIMITED",
        brief_id,
        retrieval_link_id,
        "Underlying SHA-256",
        "Audit receipt",
        "MISSING_EXPERT_RELEVANCE_EVIDENCE",
        "no_recommendation_evidence",
    ):
        assert safe_value in verified.text
    revoke_match = re.search(rf'action="/w08/export/{re.escape(pack_id)}/revoke"', verified.text)
    assert revoke_match is not None
    assert "underlying_values" not in verified.text
    assert "private marker" not in verified.text
    assert "recommended" not in verified.text.lower()

    second_export = analyst.post("/w08/exports", data=export_form, follow_redirects=False)
    assert second_export.status_code == 303
    assert second_export.headers["location"] == export_path
    with app.state.engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM evidence_exports")).scalar_one() == 1
        assert (
            connection.execute(
                text("SELECT count(*) FROM audit_events WHERE target_type='local.evidence_pack'")
            ).scalar_one()
            == 1
        )
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM audit_receipts r JOIN audit_events e "
                    "ON e.audit_event_id=r.audit_event_id WHERE e.target_type='local.evidence_pack'"
                )
            ).scalar_one()
            == 1
        )

    assert approver.get(export_path).status_code == 200
    approver_inventory = approver.get("/w08/exports")
    assert approver_inventory.status_code == 200
    assert pack_id in approver_inventory.text

    second_analyst_id, second_analyst_password = uuid4(), "synthetic-second-analyst-password"
    with app.state.engine.begin() as connection:
        app.state.sessions.create_account(
            connection,
            actor_id=second_analyst_id,
            tenant_id=UUID(app.state.synthetic_personas["analyst"]["tenant_id"]),
            display_name="Synthetic other analyst",
            password=second_analyst_password,
            roles=(LocalRole.ANALYST,),
            assigned_by=UUID(app.state.synthetic_personas["admin"]["actor_id"]),
        )
    second_analyst = TestClient(app)
    second_analyst_csrf = _login(
        second_analyst,
        {"actor_id": str(second_analyst_id), "password": second_analyst_password},
    )
    second_inventory = second_analyst.get("/w08/exports")
    assert second_inventory.status_code == 200
    assert "No local packs visible." in second_inventory.text
    assert second_analyst.get(export_path).status_code == 403
    assert (
        second_analyst.post(
            f"/w08/export/{pack_id}/revoke",
            data={"csrf": second_analyst_csrf, "reason": "Synthetic denied revoke"},
            follow_redirects=False,
        ).status_code
        == 403
    )

    scout = TestClient(app)
    scout_csrf = _login(scout, app.state.synthetic_personas["scout"])
    admin = TestClient(app)
    admin_csrf = _login(admin, app.state.synthetic_personas["admin"])
    for client, csrf in ((scout, scout_csrf), (admin, admin_csrf)):
        queue = client.get("/w08/queue")
        assert "Local evidence packs" not in queue.text
        assert 'action="/w08/exports"' not in queue.text
        assert client.get("/w08/exports").status_code == 403
        assert client.get(export_path).status_code == 403
        assert (
            client.post(
                "/w08/exports", data=export_form | {"csrf": csrf}, follow_redirects=False
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/w08/export/{pack_id}/revoke",
                data={"csrf": csrf, "reason": "Synthetic denied revoke"},
                follow_redirects=False,
            ).status_code
            == 403
        )

    revocation_reason = "Synthetic local compromise response"
    revoked = analyst.post(
        f"/w08/export/{pack_id}/revoke",
        data={"csrf": analyst_csrf, "reason": revocation_reason},
        follow_redirects=False,
    )
    assert revoked.status_code == 303
    assert revoked.headers["location"] == "/w08/exports"
    inventory = analyst.get("/w08/exports")
    assert inventory.status_code == 200
    assert pack_id in inventory.text
    assert revocation_reason in inventory.text
    assert "revoked " in inventory.text
    assert f'href="{export_path}"' not in inventory.text
    assert analyst.get(export_path).status_code == 403
    with app.state.engine.connect() as connection:
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM evidence_export_revocations WHERE evidence_pack_id=:pack"
                ),
                {"pack": pack_id},
            ).scalar_one()
            == 1
        )
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM audit_events "
                    "WHERE target_type='local.evidence_pack_revocation' AND target_id=:pack"
                ),
                {"pack": pack_id},
            ).scalar_one()
            == 1
        )
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM audit_receipts r JOIN audit_events e "
                    "ON e.audit_event_id=r.audit_event_id "
                    "WHERE e.target_type='local.evidence_pack_revocation' AND e.target_id=:pack"
                ),
                {"pack": pack_id},
            ).scalar_one()
            == 1
        )


def test_synthetic_automated_replay_guard_projection_and_candidate_allowlist(
    tmp_path: Path, monkeypatch: object
) -> None:
    """Synthetic exact-replay witness; never representative-user or model evidence."""
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = TestClient(app)
    analyst_csrf = _login(analyst, app.state.synthetic_personas["analyst"])
    approver = TestClient(app)
    approver_csrf = _login(approver, app.state.synthetic_personas["approver"])

    def approved_link(title: str) -> tuple[str, str]:
        created = analyst.post(
            "/w08/briefs",
            data=_retained_brief_form(
                analyst_csrf, title=title, responsibility="progress_through_pressure"
            ),
            follow_redirects=False,
        )
        brief_id = created.headers["location"].rsplit("/", 1)[-1]
        assert (
            analyst.post(
                f"/w08/briefs/{brief_id}/status/submit",
                data={"csrf": analyst_csrf},
                follow_redirects=False,
            ).status_code
            == 303
        )
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
                    text(
                        "SELECT retrieval_link_id FROM replayable_retrieval_links "
                        "WHERE role_brief_id=:brief"
                    ),
                    {"brief": brief_id},
                ).scalar_one()
            )
        return brief_id, link_id

    first_brief, first_link = approved_link("First exact replay")
    with app.state.engine.connect() as connection:
        first_link_audit = connection.execute(
            text("SELECT count(*) FROM audit_events WHERE target_type='replayable_retrieval_link'")
        ).scalar_one()
    assert (
        analyst.post(
            f"/w08/briefs/{first_brief}/retrieval",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 303
    )
    with app.state.engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM replayable_retrieval_links")).scalar_one()
            == 1
        )
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM audit_events "
                    "WHERE target_type='replayable_retrieval_link'"
                )
            ).scalar_one()
            == first_link_audit
        )

    detail = analyst.get(f"/w08/briefs/{first_brief}")
    for projection_field in (
        "requested at",
        "Query digest and mode",
        "Result / run / wrapper digest",
        "candidate universe",
        "resemblance_only",
        "synthetic_development_only",
        "LIMITED",
        "no_recommendation_evidence",
    ):
        assert projection_field in detail.text
    first_shortlist = analyst.post(
        f"/w08/briefs/{first_brief}/shortlists",
        data={"csrf": analyst_csrf, "retrieval_link_id": first_link, "title": "First shortlist"},
        follow_redirects=False,
    ).headers["location"]
    first_view = analyst.get(first_shortlist)
    first_selection = re.search(
        r'name="candidate_selection"[^>]*>.*?value="([^"]+)"',
        first_view.text,
        flags=re.DOTALL,
    )
    assert first_selection is not None
    assert 'name="player_id"' not in first_view.text
    assert "Synthetic resemblance candidate" in first_view.text

    second_brief, second_link = approved_link("Second exact replay")
    second_shortlist = analyst.post(
        f"/w08/briefs/{second_brief}/shortlists",
        data={"csrf": analyst_csrf, "retrieval_link_id": second_link, "title": "Second shortlist"},
        follow_redirects=False,
    ).headers["location"]
    second_match = re.search(
        r'name="candidate_selection"[^>]*>.*?value="([^"]+)"',
        analyst.get(second_shortlist).text,
        flags=re.DOTALL,
    )
    assert second_match is not None

    def entry_audit_counts() -> tuple[int, int]:
        with app.state.engine.connect() as connection:
            return (
                connection.execute(
                    text("SELECT count(*) FROM shortlist_entry_workflows")
                ).scalar_one(),
                connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one(),
            )

    before = entry_audit_counts()
    assert (
        analyst.post(
            f"{first_shortlist}/entries",
            data={
                "csrf": analyst_csrf,
                "candidate_selection": f"{first_link}:{uuid4()}",
                "rationale": "x",
            },
            follow_redirects=False,
        ).status_code
        == 403
    )
    assert (
        analyst.post(
            f"{first_shortlist}/entries",
            data={
                "csrf": analyst_csrf,
                "candidate_selection": second_match.group(1),
                "rationale": "x",
            },
            follow_redirects=False,
        ).status_code
        == 403
    )
    assert entry_audit_counts() == before
    assert (
        analyst.post(
            f"{first_shortlist}/entries",
            data={
                "csrf": analyst_csrf,
                "candidate_selection": first_selection.group(1),
                "rationale": "x",
            },
            follow_redirects=False,
        ).status_code
        == 303
    )

    before_tamper = entry_audit_counts()
    try:
        with app.state.engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE replayable_retrieval_links SET result_digest=:digest "
                    "WHERE retrieval_link_id=:id"
                ),
                {"digest": "0" * 64, "id": first_link},
            )
    except IntegrityError:
        pass
    else:
        raise AssertionError("append-only replay link tamper unexpectedly succeeded")
    assert entry_audit_counts() == before_tamper
    with app.state.engine.begin() as connection:
        connection.execute(text("DROP TRIGGER replayable_retrieval_links_reject_update"))
        connection.execute(
            text(
                "UPDATE replayable_retrieval_links SET result_digest=:digest "
                "WHERE retrieval_link_id=:id"
            ),
            {"digest": "0" * 64, "id": first_link},
        )
    assert analyst.get(f"/w08/briefs/{first_brief}").status_code == 403
    assert (
        analyst.post(
            f"/w08/briefs/{first_brief}/retrieval",
            data={"csrf": analyst_csrf},
            follow_redirects=False,
        ).status_code
        == 403
    )
    assert entry_audit_counts() == before_tamper

    mismatch = approved_link("Mismatch replay")[0]
    original_core = w08.w07_core
    calls = 0

    def mismatched_core() -> tuple[object, object]:
        nonlocal calls
        core, candidates = original_core()

        class AlternatingCore:
            def serve(self, pinned: object) -> object:
                nonlocal calls
                result = core.serve(pinned)
                calls += 1
                return (
                    result if calls == 1 else result.model_copy(update={"result_digest": "1" * 64})
                )

        return AlternatingCore(), candidates

    monkeypatch.setattr(w08, "w07_core", mismatched_core)
    with app.state.engine.connect() as connection:
        links_before = connection.execute(
            text("SELECT count(*) FROM replayable_retrieval_links")
        ).scalar_one()
        audit_before = connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()
    assert (
        analyst.post(
            f"/w08/briefs/{mismatch}/retrieval", data={"csrf": analyst_csrf}, follow_redirects=False
        ).status_code
        == 403
    )
    with app.state.engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM replayable_retrieval_links")).scalar_one()
            == links_before
        )
        assert (
            connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()
            == audit_before
        )


def test_synthetic_automated_shortlist_assignment_observation_and_conflict(
    tmp_path: Path,
) -> None:
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = TestClient(app)
    analyst_csrf = _login(analyst, app.state.synthetic_personas["analyst"])
    created = analyst.post(
        "/w08/briefs",
        data={
            "title": "Synthetic workflow",
            "responsibility": "progress_through_pressure",
            "csrf": analyst_csrf,
        },
        follow_redirects=False,
    )
    brief_path = created.headers["location"]
    brief_id = brief_path.rsplit("/", 1)[-1]
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
            f"/w08/briefs/{brief_id}/retrieval", data={"csrf": analyst_csrf}, follow_redirects=False
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
        data={"csrf": analyst_csrf, "retrieval_link_id": link_id, "title": "Synthetic shortlist"},
        follow_redirects=False,
    )
    assert shortlist.status_code == 303
    shortlist_path = shortlist.headers["location"]
    shortlist_view = analyst.get(shortlist_path)
    candidate_match = re.search(
        r'name="candidate_selection"[^>]*>.*?value="([^"]+)"',
        shortlist_view.text,
        flags=re.DOTALL,
    )
    assert candidate_match is not None
    entry = analyst.post(
        f"{shortlist_path}/entries",
        data={
            "csrf": analyst_csrf,
            "candidate_selection": candidate_match.group(1),
            "rationale": "Synthetic automated test evidence",
        },
        follow_redirects=False,
    )
    assert entry.status_code == 303
    entry_path = entry.headers["location"]
    scout_id = app.state.synthetic_personas["scout"]["actor_id"]
    assigned = analyst.post(
        f"{entry_path}/transition",
        data={
            "csrf": analyst_csrf,
            "expected_lock_version": "1",
            "state": "scout",
            "assigned_scout_id": scout_id,
            "transition_reason": "synthetic assignment",
            "next_action": "scout review",
            "next_action_owner_id": scout_id,
        },
        follow_redirects=False,
    )
    assert assigned.status_code == 303
    stale = analyst.post(
        f"{entry_path}/transition",
        data={"csrf": analyst_csrf, "expected_lock_version": "1", "state": "monitor"},
        follow_redirects=False,
    )
    assert stale.status_code == 409
    assert "Reload winning revision and retry" in stale.text

    scout = TestClient(app)
    scout_csrf = _login(scout, app.state.synthetic_personas["scout"])
    observation = {
        "csrf": scout_csrf,
        "visibility": "TEAM",
        "overall_confidence": "0.5",
        "summary": "Synthetic automated observation",
        "disagreement": "yes",
        "disagreement_reason": "Synthetic disagreement",
        "recommended_next_action": "meeting review",
        "evidence_kind": "local_note",
        "evidence_reference": "synthetic/clip-note",
        "evidence_origin": "human_entered_local",
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
                f"{dimension}_note": "Synthetic automated fixture",
            }
        )
    assert (
        scout.post(
            f"{entry_path}/observations", data=observation, follow_redirects=False
        ).status_code
        == 303
    )
    detail = scout.get(entry_path)
    assert detail.status_code == 200
    assert "synthetic_automated_test" in detail.text
    with app.state.engine.connect() as connection:
        observation_id = str(
            connection.execute(
                text("SELECT observation_id FROM scout_observations LIMIT 1")
            ).scalar_one()
        )
    amended = dict(observation)
    amended.update(
        {
            "expected_version": "1",
            "summary": "Synthetic automated amended observation",
            "evidence_reference": "synthetic/amended-note",
        }
    )
    assert (
        scout.post(
            f"/w08/observations/{observation_id}/amend",
            data=amended,
            follow_redirects=False,
        ).status_code
        == 303
    )
    with app.state.engine.connect() as connection:
        observation_rows = (
            connection.execute(
                text("SELECT * FROM scout_observations WHERE observation_id=:id ORDER BY version"),
                {"id": observation_id},
            )
            .mappings()
            .all()
        )
        assert len(observation_rows) == 2
        assert {str(row["evidence_origin"]) for row in observation_rows} == {
            "synthetic_automated_test"
        }
        audit_rows = (
            connection.execute(
                text(
                    "SELECT e.after_digest FROM audit_events e JOIN audit_receipts r "
                    "ON r.audit_event_id=e.audit_event_id AND r.tenant_id=e.tenant_id "
                    "WHERE e.target_type='scout_observation' AND e.target_id=:id "
                    "ORDER BY r.sequence"
                ),
                {"id": observation_id},
            )
            .mappings()
            .all()
        )
        assert len(audit_rows) == 2
        for row, audit in zip(observation_rows, audit_rows, strict=True):
            value = dict(row)
            dimensions = tuple(
                w08.ScoutRubricDimension(
                    dimension=w08.ScoutRubricDimensionName(item["dimension"]),
                    rating=int(item["rating"]),
                    confidence=float(item["confidence"]),
                    note=str(item["note"]),
                )
                for item in json.loads(str(value["dimensions"]))
            )
            references = tuple(
                w08.LocalEvidenceReference(
                    kind=w08.LocalEvidenceReferenceKind(item["kind"]),
                    reference=str(item["reference"]),
                )
                for item in json.loads(str(value["evidence_references"]))
            )
            observation_contract = w08.ScoutObservationVersion(
                observation_id=UUID(str(value["observation_id"])),
                tenant_context=w08.TenantContext(tenant_id=UUID(str(value["tenant_id"]))),
                version=int(value["version"]),
                previous_version=value["previous_version"],
                shortlist_entry_id=UUID(str(value["shortlist_entry_id"])),
                author_id=UUID(str(value["author_id"])),
                visibility=w08.WorkflowVisibility(str(value["visibility"])),
                dimensions=dimensions,
                overall_confidence=float(value["overall_confidence"]),
                evidence_references=references,
                summary=str(value["summary"]),
                disagreement=bool(value["disagreement"]),
                disagreement_reason=value["disagreement_reason"],
                recommended_next_action=str(value["recommended_next_action"]),
                evidence_origin=WorkflowEvidenceOrigin(str(value["evidence_origin"])),
                created_at=datetime.fromisoformat(str(value["created_at"])),
            )
            expected = hashlib.sha256(
                json.dumps(
                    observation_contract.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                    default=str,
                ).encode()
            ).hexdigest()
            assert str(audit["after_digest"]) == expected
    assert 'expected_version" value="2' in scout.get(entry_path).text
    approver_detail = approver.get(entry_path)
    assert approver_detail.status_code == 200
    assert "Synthetic automated amended observation" in approver_detail.text
    assert "Amend visible observation" not in approver_detail.text

    assert (
        scout.post(
            f"{entry_path}/comments",
            data={
                "csrf": scout_csrf,
                "visibility": "TEAM",
                "body": "Synthetic team comment",
                "evidence_origin": "human_entered_local",
            },
            follow_redirects=False,
        ).status_code
        == 303
    )
    assert (
        scout.post(
            f"{entry_path}/comments",
            data={
                "csrf": scout_csrf,
                "visibility": "OWNER_ONLY",
                "body": "Synthetic owner-only comment",
            },
            follow_redirects=False,
        ).status_code
        == 303
    )
    private_observation = dict(observation)
    private_observation.update(
        {
            "visibility": "OWNER_ONLY",
            "summary": "Synthetic owner-only observation",
            "evidence_reference": "synthetic/private-note",
        }
    )
    assert (
        scout.post(
            f"{entry_path}/observations", data=private_observation, follow_redirects=False
        ).status_code
        == 303
    )
    approver_view = approver.get(entry_path)
    assert "Synthetic automated amended observation" in approver_view.text
    assert "Synthetic team comment" in approver_view.text
    assert "Synthetic owner-only observation" not in approver_view.text
    assert "Synthetic owner-only comment" not in approver_view.text

    with app.state.engine.connect() as connection:
        assert set(
            connection.execute(text("SELECT evidence_origin FROM shortlist_comments")).scalars()
        ) == {"synthetic_automated_test"}
        shortlist_id = str(
            connection.execute(
                text(
                    "SELECT shortlist_id FROM shortlist_entry_workflows "
                    "WHERE shortlist_entry_id=:entry"
                ),
                {"entry": entry_path.rsplit("/", 1)[-1]},
            ).scalar_one()
        )
        role_brief_id = str(
            connection.execute(
                text("SELECT role_brief_id FROM workflow_shortlists WHERE shortlist_id=:id"),
                {"id": shortlist_id},
            ).scalar_one()
        )
    exported = analyst.post(
        "/w08/exports",
        data={
            "csrf": analyst_csrf,
            "role_brief_id": role_brief_id,
            "role_brief_version": "3",
            "retrieval_link_id": link_id,
            "shortlist_id": shortlist_id,
            "evidence_origin": "human_entered_local",
        },
        follow_redirects=False,
    )
    assert exported.status_code == 303
    pack_id = exported.headers["location"].rsplit("/", 1)[-1]
    pack = next(tmp_path.rglob(f"{pack_id}.json"))
    assert json.loads(pack.read_text(encoding="utf-8"))["workflow_action_origins"] == [
        "synthetic_automated_test"
    ]

    held = approver.post(
        f"{entry_path}/transition",
        data={
            "csrf": approver_csrf,
            "expected_lock_version": "2",
            "state": "hold",
            "hold_reason": "awaiting_evidence",
            "transition_reason": "Synthetic meeting hold",
            "next_action": "obtain local evidence",
            "next_action_owner_id": scout_id,
        },
        follow_redirects=False,
    )
    assert held.status_code == 303
    rejected = approver.post(
        f"{entry_path}/transition",
        data={
            "csrf": approver_csrf,
            "expected_lock_version": "3",
            "state": "rejected",
            "rejection_reason": "insufficient_evidence",
            "transition_reason": "Synthetic meeting rejection",
        },
        follow_redirects=False,
    )
    assert rejected.status_code == 303
    reconsidered = analyst.post(
        f"{entry_path}/transition",
        data={
            "csrf": analyst_csrf,
            "expected_lock_version": "4",
            "state": "longlist",
            "transition_reason": "Synthetic attributable reconsideration",
        },
        follow_redirects=False,
    )
    assert reconsidered.status_code == 303
    history = analyst.get(entry_path)
    assert history.status_code == 200
    for retained_value in (
        "Synthetic meeting hold",
        "awaiting_evidence",
        "obtain local evidence",
        "Synthetic meeting rejection",
        "insufficient_evidence",
        "Synthetic attributable reconsideration",
        scout_id,
    ):
        assert retained_value in history.text
    control = history.text.split('<select name="state">', 1)[1].split("</select>", 1)[0]
    assert 'value="hold"' not in control
    assert 'value="shortlist"' not in control

    second_scout_id, second_scout_password = uuid4(), "synthetic-second-scout-password"
    with app.state.engine.begin() as connection:
        app.state.sessions.create_account(
            connection,
            actor_id=second_scout_id,
            tenant_id=UUID(app.state.synthetic_personas["scout"]["tenant_id"]),
            display_name="Synthetic unassigned second scout",
            password=second_scout_password,
            roles=(LocalRole.SCOUT,),
            assigned_by=UUID(app.state.synthetic_personas["analyst"]["actor_id"]),
        )
    second_scout = TestClient(app)
    _login(
        second_scout,
        {"actor_id": str(second_scout_id), "password": second_scout_password},
    )
    unassigned = second_scout.get(entry_path)
    assert unassigned.status_code == 404
    assert "Synthetic owner-only observation" not in unassigned.text
    foreign = approver.get(f"/w08/entries/{uuid4()}")
    assert foreign.status_code == 404
    assert "Synthetic meeting hold" not in foreign.text

    with app.state.engine.connect() as connection:
        before_observations = connection.execute(
            text("SELECT count(*) FROM scout_observations")
        ).scalar_one()
        before_audit = connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()
    for invalid_reference in (
        "",
        "/private/clip",
        "../synthetic/clip",
        "https://example.invalid/clip",
    ):
        invalid = dict(observation)
        invalid.update(
            {
                "summary": "Rejected local-reference fixture",
                "evidence_reference": invalid_reference,
            }
        )
        assert (
            scout.post(
                f"{entry_path}/observations", data=invalid, follow_redirects=False
            ).status_code
            == 403
        )
    with app.state.engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM scout_observations")).scalar_one()
            == before_observations
        )
        assert (
            connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()
            == before_audit
        )

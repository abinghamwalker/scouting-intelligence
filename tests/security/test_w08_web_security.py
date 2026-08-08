"""Synthetic automated web security witnesses; not user-study evidence."""

from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from scouting.audit import AuditIntegrityError, AuditLedger
from scouting.contracts import WorkflowEvidenceOrigin
from scouting.policy import LocalRole
from scouting.storage import GuardedStorage
from scouting.web.w08 import create_w08_app


def _login(client: TestClient, persona: dict[str, str]) -> str:
    assert client.post("/w08/login", data=persona, follow_redirects=False).status_code == 303
    csrf = client.cookies.get("w08_csrf")
    assert csrf is not None
    return csrf


def _brief_form(csrf: str) -> dict[str, str]:
    return {
        "csrf": csrf,
        "title": "Synthetic adversarial export witness",
        "responsibility": "progress_through_pressure",
        "constraint_field": "synthetic_age_years",
        "constraint_operator": "at_most",
        "constraint_value": "40",
        "preference_dimension": "progress_through_pressure",
        "preference_weight": "0.5",
        "exemplar_player_ids": "20000000-0000-4000-8000-000000000001",
    }


def _export_baseline(app: object, root: Path) -> tuple[int, int, int, int, tuple[str, ...]]:
    """Return exact non-content counts used to prove denied routes are inert."""
    with app.state.engine.connect() as connection:  # type: ignore[attr-defined]
        database = tuple(
            int(connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one())
            for table in (
                "evidence_exports",
                "evidence_export_revocations",
                "audit_events",
                "audit_receipts",
            )
        )
    pack_root = root / "data/working/w08-evidence-packs"
    files = tuple(
        sorted(str(path.relative_to(pack_root)) for path in pack_root.rglob("*") if path.is_file())
    )
    return (*database, files)


def _approved_export_context(
    tmp_path: Path,
) -> tuple[object, TestClient, str, TestClient, str, dict[str, str], str]:
    """Build an authorised synthetic route context; never participant evidence."""
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    analyst = TestClient(app)
    analyst_csrf = _login(analyst, app.state.synthetic_personas["analyst"])
    approver = TestClient(app)
    approver_csrf = _login(approver, app.state.synthetic_personas["approver"])
    created = analyst.post("/w08/briefs", data=_brief_form(analyst_csrf), follow_redirects=False)
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
            f"/w08/briefs/{brief_id}/retrieval", data={"csrf": analyst_csrf}, follow_redirects=False
        ).status_code
        == 303
    )
    with app.state.engine.connect() as connection:
        link = str(
            connection.execute(
                text(
                    "SELECT retrieval_link_id FROM replayable_retrieval_links "
                    "WHERE role_brief_id=:id"
                ),
                {"id": brief_id},
            ).scalar_one()
        )
    created_shortlist = analyst.post(
        f"/w08/briefs/{brief_id}/shortlists",
        data={
            "csrf": analyst_csrf,
            "retrieval_link_id": link,
            "title": "Synthetic export shortlist",
        },
        follow_redirects=False,
    )
    assert created_shortlist.status_code == 303
    shortlist_id = created_shortlist.headers["location"].rsplit("/", 1)[-1]
    form = {
        "csrf": analyst_csrf,
        "role_brief_id": brief_id,
        "role_brief_version": "3",
        "retrieval_link_id": link,
        "shortlist_id": shortlist_id,
    }
    return app, analyst, analyst_csrf, approver, approver_csrf, form, shortlist_id


def test_synthetic_automated_security_headers_and_admin_export_denial(tmp_path: Path) -> None:
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    admin = app.state.synthetic_personas["admin"]
    client = TestClient(app)
    response = client.post("/w08/login", data=admin, follow_redirects=True)
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert client.get("/w08/export/00000000-0000-4000-8000-000000000001").status_code == 403


def test_synthetic_automated_export_adversarial_atomicity_and_input_boundaries(
    tmp_path: Path, monkeypatch: object
) -> None:
    """Route failures are generic and inert; this is synthetic automated evidence only."""
    app, analyst, analyst_csrf, approver, approver_csrf, form, shortlist_id = (
        _approved_export_context(tmp_path)
    )
    root = tmp_path

    def assert_denied(
        response: object, baseline: tuple[int, int, int, int, tuple[str, ...]]
    ) -> None:
        assert response.status_code == 403  # type: ignore[attr-defined]
        assert "SECRET-DO-NOT-ECHO" not in response.text  # type: ignore[attr-defined]
        assert _export_baseline(app, root) == baseline

    baseline = _export_baseline(app, root)
    # Role, CSRF, malformed object tuple, and wrong tenant/object routes must not
    # create a pack, receipt, revocation, or file.
    scout = TestClient(app)
    scout_csrf = _login(scout, app.state.synthetic_personas["scout"])
    admin = TestClient(app)
    admin_csrf = _login(admin, app.state.synthetic_personas["admin"])
    for client, csrf in ((scout, scout_csrf), (admin, admin_csrf)):
        assert_denied(client.post("/w08/exports", data={**form, "csrf": csrf}), baseline)
    assert_denied(analyst.post("/w08/exports", data={**form, "csrf": "bad"}), baseline)
    assert_denied(
        analyst.post("/w08/exports", data={**form, "shortlist_id": str(uuid4())}), baseline
    )
    foreign_root = tmp_path / "foreign-root"
    foreign_app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=foreign_root / "foreign.sqlite3",
        allowed_root=foreign_root,
    )
    foreign = TestClient(foreign_app)
    foreign_csrf = _login(foreign, foreign_app.state.synthetic_personas["analyst"])
    assert foreign.post("/w08/exports", data={**form, "csrf": foreign_csrf}).status_code == 403
    assert _export_baseline(app, root) == baseline

    # Input boundary witnesses use raw requests so malformed content never reaches
    # form parsing or echoes the supplied secret marker.
    raw_cases = (
        ({}, b"csrf=SECRET-DO-NOT-ECHO"),
        ({"content-type": "text/plain"}, b"csrf=SECRET-DO-NOT-ECHO"),
        (
            {"content-type": "application/x-www-form-urlencoded", "content-length": "bogus"},
            b"csrf=SECRET-DO-NOT-ECHO",
        ),
        (
            {"content-type": "application/x-www-form-urlencoded", "content-length": "65537"},
            b"csrf=SECRET-DO-NOT-ECHO",
        ),
        ({"content-type": "application/x-www-form-urlencoded"}, b"csrf=SECRET-DO-NOT-ECHO\xff"),
        (
            {
                "content-type": "application/x-www-form-urlencoded",
                "content-length": "1",
            },
            b"x=" + b"a" * (64 * 1024),
        ),
    )
    for headers, body in raw_cases:
        response = analyst.post("/w08/exports", content=body, headers=headers)
        assert_denied(response, baseline)

    shortlist_page = analyst.get(f"/w08/shortlists/{shortlist_id}")
    selection = re.search(
        r'name="candidate_selection"[^>]*>.*?value="([^"]+)"', shortlist_page.text, re.DOTALL
    )
    assert selection is not None
    created_entry = analyst.post(
        f"/w08/shortlists/{shortlist_id}/entries",
        data={
            "csrf": analyst_csrf,
            "candidate_selection": selection.group(1),
            "rationale": "synthetic",
        },
        follow_redirects=False,
    )
    assert created_entry.status_code == 303
    entry_id = created_entry.headers["location"].rsplit("/", 1)[-1]
    with app.state.engine.begin() as connection:
        connection.execute(
            text(
                """INSERT INTO scout_observations
                (observation_id, tenant_id, version, previous_version, shortlist_entry_id,
                 author_id, visibility, dimensions, overall_confidence, evidence_references,
                 summary, disagreement, disagreement_reason, recommended_next_action,
                 evidence_origin, created_at)
                VALUES (:id, :tenant, 1, NULL, :entry, :author, 'OWNER_ONLY', :dimensions,
                0.5, '[]', :summary, 0, NULL, 'synthetic next action',
                'synthetic_automated_test', :now)"""
            ),
            {
                "id": uuid4(),
                "tenant": app.state.synthetic_personas["analyst"]["tenant_id"],
                "entry": entry_id,
                "author": app.state.synthetic_personas["scout"]["actor_id"],
                "dimensions": '[{"dimension":"role_execution","rating":3}]',
                "summary": "PRIVATE-OBSERVATION-DO-NOT-DISCLOSE",
                "now": "2026-08-04T00:00:00+00:00",
            },
        )
    created = analyst.post("/w08/exports", data=form, follow_redirects=False)
    assert created.status_code == 303
    path = created.headers["location"]
    pack_id = path.rsplit("/", 1)[-1]
    pack_file = next(root.rglob(f"{pack_id}.json"))
    assert "PRIVATE-OBSERVATION-DO-NOT-DISCLOSE" not in pack_file.read_text(encoding="utf-8")
    first = _export_baseline(app, root)
    # A repeated deterministic creation is a read-only idempotent operation.
    assert (
        analyst.post("/w08/exports", data=form, follow_redirects=False).headers["location"] == path
    )
    assert _export_baseline(app, root) == first
    assert approver.get(path).status_code == 200

    # IDOR and revocation replay are denied without leaking the pack body or adding
    # a second receipt/revocation.  A second same-tenant analyst has no export scope.
    other_id, password = uuid4(), "synthetic-other-analyst-password"
    with app.state.engine.begin() as connection:
        app.state.sessions.create_account(
            connection,
            actor_id=other_id,
            tenant_id=UUID(app.state.synthetic_personas["analyst"]["tenant_id"]),
            display_name="Synthetic other analyst",
            password=password,
            roles=(LocalRole.ANALYST,),
            assigned_by=UUID(app.state.synthetic_personas["admin"]["actor_id"]),
        )
    other = TestClient(app)
    other_csrf = _login(other, {"actor_id": str(other_id), "password": password})
    before_idor = _export_baseline(app, root)
    assert_denied(other.get(path), before_idor)
    assert_denied(
        other.post(
            f"/w08/export/{pack_id}/revoke",
            data={"csrf": other_csrf, "reason": "SECRET-DO-NOT-ECHO"},
        ),
        before_idor,
    )
    assert_denied(scout.get(path), before_idor)
    assert_denied(
        admin.post(
            f"/w08/export/{pack_id}/revoke",
            data={"csrf": admin_csrf, "reason": "SECRET-DO-NOT-ECHO"},
        ),
        before_idor,
    )

    revoked = analyst.post(
        f"/w08/export/{pack_id}/revoke",
        data={"csrf": analyst_csrf, "reason": "synthetic compromise"},
        follow_redirects=False,
    )
    assert revoked.status_code == 303
    revoked_baseline = _export_baseline(app, root)
    assert_denied(analyst.get(path), revoked_baseline)
    assert_denied(
        analyst.post(
            f"/w08/export/{pack_id}/revoke",
            data={"csrf": analyst_csrf, "reason": "SECRET-DO-NOT-ECHO"},
        ),
        revoked_baseline,
    )

    # New app instances isolate byte/audit tamper and injected recovery probes.
    tamper_app, tamper_analyst, _, _, _, tamper_form, _ = _approved_export_context(
        tmp_path / "tamper"
    )
    tamper_created = tamper_analyst.post("/w08/exports", data=tamper_form, follow_redirects=False)
    tamper_path = tamper_created.headers["location"]
    pack_file = next((tmp_path / "tamper").rglob(f"{tamper_path.rsplit('/', 1)[-1]}.json"))
    pack_file.write_bytes(b"SECRET-DO-NOT-ECHO")
    tamper_baseline = _export_baseline(tamper_app, tmp_path / "tamper")
    # Byte tampering is an independent fault: each policy-visible export route
    # must reject it before any later audit-ledger corruption is introduced.
    for response in (
        tamper_analyst.get("/w08/exports"),
        tamper_analyst.get(tamper_path),
        tamper_analyst.post("/w08/exports", data=tamper_form),
        tamper_analyst.post(
            f"{tamper_path}/revoke",
            data={"csrf": tamper_analyst.cookies.get("w08_csrf"), "reason": "synthetic"},
        ),
    ):
        assert response.status_code == 403
        assert "SECRET-DO-NOT-ECHO" not in response.text
        assert _export_baseline(tamper_app, tmp_path / "tamper") == tamper_baseline

    ledger_app, ledger_analyst, _, _, _, ledger_form, _ = _approved_export_context(
        tmp_path / "ledger-tamper"
    )
    ledger_created = ledger_analyst.post("/w08/exports", data=ledger_form, follow_redirects=False)
    ledger_path = ledger_created.headers["location"]
    with ledger_app.state.engine.begin() as connection:
        connection.execute(text("DROP TRIGGER audit_receipts_reject_update"))
        connection.execute(
            text("UPDATE audit_receipts SET receipt_digest=:digest WHERE sequence=1"),
            {"digest": "0" * 64},
        )
    corrupted_baseline = _export_baseline(ledger_app, tmp_path / "ledger-tamper")
    for response in (
        ledger_analyst.get("/w08/exports"),
        ledger_analyst.get(ledger_path),
        ledger_analyst.post("/w08/exports", data=ledger_form),
        ledger_analyst.post(
            f"{ledger_path}/revoke",
            data={"csrf": ledger_analyst.cookies.get("w08_csrf"), "reason": "synthetic"},
        ),
    ):
        assert response.status_code == 403
        assert "SECRET-DO-NOT-ECHO" not in response.text
        assert _export_baseline(ledger_app, tmp_path / "ledger-tamper") == corrupted_baseline

    def injected_case(name: str, patcher: object) -> None:
        failure_app, failure_analyst, _, _, _, failure_form, _ = _approved_export_context(
            tmp_path / name
        )
        before = _export_baseline(failure_app, tmp_path / name)
        with monkeypatch.context() as scoped:  # type: ignore[attr-defined]
            patcher(scoped)
            response = failure_analyst.post("/w08/exports", data=failure_form)
            assert response.status_code == 403
            assert _export_baseline(failure_app, tmp_path / name) == before
        assert (
            failure_analyst.post(
                "/w08/exports", data=failure_form, follow_redirects=False
            ).status_code
            == 303
        )

    def fail_audit(scoped: object) -> None:
        scoped.setattr(
            AuditLedger,
            "append",
            lambda *args, **kwargs: (_ for _ in ()).throw(AuditIntegrityError("injected")),
        )

    def fail_storage(scoped: object) -> None:
        scoped.setattr(
            GuardedStorage,
            "write_bytes",
            lambda *args, **kwargs: (_ for _ in ()).throw(OSError("injected")),
        )

    def fail_database(scoped: object) -> None:
        original_execute = Connection.execute

        def reject_export_insert(
            connection: object, statement: object, *args: object, **kwargs: object
        ) -> object:
            if "INSERT INTO evidence_exports" in str(statement):
                raise SQLAlchemyError("injected database insert failure")
            return original_execute(connection, statement, *args, **kwargs)  # type: ignore[arg-type]

        scoped.setattr(Connection, "execute", reject_export_insert)

    injected_case("audit-failure", fail_audit)
    injected_case("storage-failure", fail_storage)
    injected_case("database-failure", fail_database)

    # Storage-read failure is a non-mutating generic denial; remove injection then
    # prove the same verified pack is readable again.
    read_app, read_analyst, _, _, _, read_form, _ = _approved_export_context(
        tmp_path / "read-failure"
    )
    read_path = read_analyst.post("/w08/exports", data=read_form, follow_redirects=False).headers[
        "location"
    ]
    before_read_failure = _export_baseline(read_app, tmp_path / "read-failure")
    with monkeypatch.context() as scoped:  # type: ignore[attr-defined]
        scoped.setattr(
            GuardedStorage,
            "read_bytes",
            lambda *args, **kwargs: (_ for _ in ()).throw(OSError("injected")),
        )
        assert read_analyst.get(read_path).status_code == 403
        assert _export_baseline(read_app, tmp_path / "read-failure") == before_read_failure
    assert read_analyst.get(read_path).status_code == 200

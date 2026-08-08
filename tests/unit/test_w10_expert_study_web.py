"""Fail-closed composition tests for the local W10 expert-study page."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from urllib.parse import urlencode

from fastapi.testclient import TestClient

from scouting.contracts.expert_relevance import (
    ExpertRelevanceProtocol,
    ExpertStudyPresentationBundle,
    StudyMode,
)
from scouting.storage.expert_study import (
    FROZEN_PRESENTATION_DIGEST,
    FROZEN_PROTOCOL_DIGEST,
    FROZEN_QUERY_PACK_DIGEST,
    PROTOCOL_APPROVAL_CONFIRMATION,
    ExpertStudyStore,
)
from scouting.web.w10_expert_study import create_w10_expert_study_app

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = ROOT / "configs/evaluation/w10-expert-relevance-protocol-v1.json"
PRESENTATION_PATH = ROOT / "configs/evaluation/w10-expert-study-presentation-v1.json"

_SERVICE_SPEC = importlib.util.spec_from_file_location(
    "w10_study_main_test",
    ROOT / "services/api/w10_study_main.py",
)
assert _SERVICE_SPEC is not None and _SERVICE_SPEC.loader is not None
w10_study_main = importlib.util.module_from_spec(_SERVICE_SPEC)
_SERVICE_SPEC.loader.exec_module(w10_study_main)


def _authority() -> tuple[ExpertRelevanceProtocol, ExpertStudyPresentationBundle]:
    return (
        ExpertRelevanceProtocol.model_validate_json(PROTOCOL_PATH.read_bytes()),
        ExpertStudyPresentationBundle.model_validate_json(PRESENTATION_PATH.read_bytes()),
    )


def _client(tmp_path: Path) -> tuple[TestClient, ExpertStudyStore, ExpertStudyStore]:
    protocol, presentation = _authority()
    pilot = ExpertStudyStore(
        database_path=tmp_path / "pilot.sqlite3",
        capture_root=tmp_path / "pilot-captures",
        allowed_root=tmp_path,
        mode=StudyMode.MECHANICS_PILOT,
        protocol=protocol,
        presentation=presentation,
        test_only=True,
    )
    formal = ExpertStudyStore(
        database_path=tmp_path / "formal.sqlite3",
        capture_root=tmp_path / "formal-captures",
        allowed_root=tmp_path,
        mode=StudyMode.FORMAL_G_RW4,
        protocol=protocol,
        presentation=presentation,
        test_only=True,
    )
    app = create_w10_expert_study_app(
        protocol=protocol,
        presentation=presentation,
        pilot_store=pilot,
        formal_store=formal,
        allow_test_host=True,
    )
    return TestClient(app, base_url="http://127.0.0.1"), pilot, formal


def test_unavailable_page_is_loopback_only_and_has_no_mutation_routes() -> None:
    app = create_w10_expert_study_app(
        protocol=None,
        presentation=None,
        pilot_store=None,
        formal_store=None,
        unavailable_reason="exact frozen participant-safe authority is unavailable",
        allow_test_host=True,
    )
    client = TestClient(app, base_url="http://127.0.0.1")

    page = client.get("/w10")
    assert page.status_code == 503
    assert "exact frozen participant-safe authority is unavailable" in page.text
    assert client.post("/w10/sessions").status_code == 404
    assert client.post("/w10/approval").status_code == 404
    assert client.post("/w10/detach").status_code == 404
    assert client.get("/api/w09/datasets").status_code == 404

    rejected = client.get("/w10", headers={"host": "study.example"})
    assert rejected.status_code == 400
    remote_client = TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("203.0.113.19", 54321),
    )
    spoofed = remote_client.get("/w10", headers={"host": "localhost"})
    assert spoofed.status_code == 400
    assert "only on a loopback host" in spoofed.text
    assert page.headers["cache-control"] == "no-store"
    assert page.headers["referrer-policy"] == "no-referrer"
    assert page.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'none'" in page.headers["content-security-policy"]
    assert "connect-src 'self'" in page.headers["content-security-policy"]


def test_decision_page_states_exact_burden_rules_authority_and_pilot_boundary(
    tmp_path: Path,
) -> None:
    client, _, _ = _client(tmp_path)

    page = client.get("/w10")

    assert page.status_code == 200
    for expected in (
        "approximately 30–35 minutes",
        "8 query sets",
        "80 blinded primary candidates",
        "2 delayed, blinded repeat assessments",
        "82 responses",
        "at least 2 years",
        "last 5 years",
        "at least 5 eligible experts",
        "football relevance from 0–4",
        "confidence from 1–5",
        "explicitly abstain",
        "one-way participant-code digest",
        "PASS",
        "FAIL",
        "INSUFFICIENT_EVIDENCE",
        "3 non-abstaining raters per candidate",
        "never formal expert evidence",
    ):
        assert expected in page.text
    assert FROZEN_PROTOCOL_DIGEST in page.text
    assert FROZEN_QUERY_PACK_DIGEST in page.text
    assert FROZEN_PRESENTATION_DIGEST in page.text
    assert "Start formal frozen study" in page.text
    assert 'disabled aria-disabled="true"' in page.text


def test_approval_requires_csrf_human_pseudonym_and_exact_confirmation(
    tmp_path: Path,
) -> None:
    client, _, formal = _client(tmp_path)
    page = client.get("/w10")
    csrf = page.cookies["w10_study_csrf"]

    missing_csrf = client.post(
        "/w10/approval",
        data={"approved_by_pseudonym": "OWNER-01", "confirmation": "yes"},
    )
    assert missing_csrf.status_code == 403
    assert formal.load_protocol_approval() is None

    wrong_confirmation = client.post(
        "/w10/approval",
        data={
            "csrf": csrf,
            "approved_by_pseudonym": "OWNER-01",
            "confirmation": "I approve.",
        },
    )
    assert wrong_confirmation.status_code == 422
    assert formal.load_protocol_approval() is None

    approved = client.post(
        "/w10/approval",
        data={
            "csrf": csrf,
            "approved_by_pseudonym": "OWNER-01",
            "confirmation": PROTOCOL_APPROVAL_CONFIRMATION,
        },
        follow_redirects=True,
    )
    assert approved.status_code == 200, approved.text
    assert "Formal participant preparation is now authorized" in approved.text
    assert "Approval alone creates no relevance result" in approved.text
    assert "pending master review" not in approved.text


def test_forms_reject_duplicate_singletons_and_unknown_route_fields(tmp_path: Path) -> None:
    client, _, _ = _client(tmp_path)
    csrf = client.get("/w10").cookies["w10_study_csrf"]
    headers = {"content-type": "application/x-www-form-urlencoded"}

    duplicate = client.post(
        "/w10/approval",
        content=urlencode(
            (
                ("csrf", csrf),
                ("csrf", csrf),
                ("approved_by_pseudonym", "OWNER-01"),
                ("confirmation", PROTOCOL_APPROVAL_CONFIRMATION),
            )
        ).encode(),
        headers=headers,
    )
    assert duplicate.status_code == 422
    assert "form fields must occur exactly once" in duplicate.text

    unknown = client.post(
        "/w10/judgements",
        content=urlencode((("csrf", csrf), ("unexpected_rank", "1"))).encode(),
        headers=headers,
    )
    assert unknown.status_code == 422
    assert "form contains an unexpected field" in unknown.text


def test_invalid_pseudonyms_render_bounded_form_errors_instead_of_500(tmp_path: Path) -> None:
    client, _, formal = _client(tmp_path)
    csrf = client.get("/w10").cookies["w10_study_csrf"]

    invalid_owner = client.post(
        "/w10/approval",
        data={
            "csrf": csrf,
            "approved_by_pseudonym": "Adrian",
            "confirmation": PROTOCOL_APPROVAL_CONFIRMATION,
        },
    )
    assert invalid_owner.status_code == 422
    assert "6-32 uppercase alphanumeric/hyphen characters" in invalid_owner.text
    assert formal.load_protocol_approval() is None

    invalid_participant = client.post(
        "/w10/sessions",
        data={
            "csrf": csrf,
            "lane": "pilot",
            "participant_code": "Adrian",
            "years_experience": "3",
            "experience_professional_scouting": "true",
            "assessed_players_within_window": "true",
            "conflict_note": "",
            "voluntary_participation": "true",
            "local_pseudonymous_storage": "true",
            "withdrawal_before_submission_understood": "true",
            "immutable_after_submission_understood": "true",
            "research_limitations_understood": "true",
        },
    )
    assert invalid_participant.status_code == 422
    assert "6-32 uppercase alphanumeric/hyphen characters" in invalid_participant.text


def test_production_v2_paths_are_physically_separate_from_retained_v1_paths() -> None:
    assert "/study/v2/pilot/" in str(w10_study_main.V2_PILOT_AUTHORITY_PATH)
    assert w10_study_main.V2_PILOT_DATABASE_PATH.name == "mechanics-pilot-v2.sqlite3"
    assert (
        w10_study_main.HISTORICAL_COMPARISON_AUTHORITY_PATH.name
        == "historical-player-comparison-pilot-authority-v1.json"
    )
    assert (
        w10_study_main.HISTORICAL_COMPARISON_DATABASE_PATH.name
        == "historical-player-comparison-pilot-v1.sqlite3"
    )
    assert w10_study_main.HISTORICAL_COMPARISON_AUTHORITY_PATH != (
        w10_study_main.V2_PILOT_AUTHORITY_PATH
    )
    assert w10_study_main.HISTORICAL_COMPARISON_DATABASE_PATH != (
        w10_study_main.V2_PILOT_DATABASE_PATH
    )


def test_web_composition_has_no_evaluator_or_browser_injection_seam() -> None:
    paths = (
        ROOT / "src/scouting/web/w10_expert_study.py",
        ROOT / "services/api/w10_study_main.py",
        ROOT / "apps/web/static/w10-expert-study/study.js",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for forbidden in (
        "w10-frozen-query-pack-v1.json",
        "FrozenExpertQueryPack",
        "CandidateOrigin",
        "retrieval_score",
        "retrieval_rank",
        "scouting.evaluation",
        "scouting.web.w09",
        "ResearchApiRuntime",
        "innerHTML",
        "insertAdjacentHTML",
        "document.write",
        "localStorage",
        "sessionStorage",
    ):
        assert forbidden not in combined

    tree = ast.parse(paths[0].read_text(encoding="utf-8"))
    imported = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not any(
        module.startswith(("scouting.evaluation", "scouting.web.w09")) for module in imported
    )

"""Independent participant-boundary checks for the historical comparison form."""

from __future__ import annotations

import html
import importlib.util
import json
import re
import sqlite3
from html.parser import HTMLParser
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from scouting.contracts.expert_relevance import (
    AssessmentBasisV2,
    EvidenceSufficiencyV2,
    ExpertExperienceKind,
    JudgementState,
    MdEvidenceSubrubricV2,
    ParticipantEvidenceComparisonV2,
)
from scouting.contracts.research import canonical_research_digest
from scouting.data_products.wyscout.expert_evidence import (
    build_participant_evidence_comparison_v2,
)
from scouting.storage.expert_study import (
    HISTORICAL_COMPARISON_AUTHORITY_VERSION,
    HISTORICAL_COMPARISON_DEBRIEF_VERSION,
    HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
    HISTORICAL_COMPARISON_RESPONSE_VERSION,
    ExpertStudyConflictError,
    ExpertStudyIntegrityError,
    HistoricalComparisonPilotStore,
)
from scouting.storage.formats import canonical_json_bytes
from scouting.web.w10_expert_study import create_historical_player_comparison_app

ROOT = Path(__file__).resolve().parents[2]
FRIENDLY_PATH = "/historical-player-comparison"
LEGACY_PATH = "/w10/v2"
CONSENT = {
    "voluntary_participation": "true",
    "local_pseudonymous_storage": "true",
    "withdrawal_before_submission_understood": "true",
    "immutable_after_submission_understood": "true",
    "research_limitations_understood": "true",
}

_BYTE_FORBIDDEN = (
    re.compile(r"\bw(?:0?[3-9]|10)\b", re.IGNORECASE),
    re.compile(r"\bg-rw4\b", re.IGNORECASE),
    re.compile(r"\b(?:a5|08d|08e|08f)\b", re.IGNORECASE),
    re.compile(r"\bv[12]\b", re.IGNORECASE),
    re.compile(r"\b(?:phase|gate|checkpoint|rework)\b", re.IGNORECASE),
    re.compile(r"\b(?:authority|protocol)\b", re.IGNORECASE),
    re.compile(r"\bmatrix\b", re.IGNORECASE),
    re.compile(r"\bscorer\b", re.IGNORECASE),
    re.compile(r"feature registry", re.IGNORECASE),
    re.compile(r"canonical authority", re.IGNORECASE),
    re.compile(r"\bpredicate\b", re.IGNORECASE),
    re.compile(r"\bdigest\b", re.IGNORECASE),
    re.compile(r"\blineage\b", re.IGNORECASE),
    re.compile(r"schema version", re.IGNORECASE),
    re.compile(r"policy digest", re.IGNORECASE),
    re.compile(r"authority version", re.IGNORECASE),
    re.compile(r"query[- ]pack", re.IGNORECASE),
    re.compile(r"independent descriptors?", re.IGNORECASE),
    re.compile(r"independent famil(?:y|ies)", re.IGNORECASE),
    re.compile(r"\bid-(?:loc|pass|duel|defloc|shotloc|gk)-01\b", re.IGNORECASE),
    re.compile(r"recorded_x_\d+_\d+__recorded_y_\d+_\d+", re.IGNORECASE),
    re.compile(r"\bobserved value\b", re.IGNORECASE),
    re.compile(r"\braw value\b", re.IGNORECASE),
    re.compile(r"\bgoverned minutes\b", re.IGNORECASE),
    re.compile(r"\bopportunity (?:denominator|floor)\b", re.IGNORECASE),
    re.compile(r"\bretained actions?\b", re.IGNORECASE),
    re.compile(r"\bpilot\b", re.IGNORECASE),
    re.compile(r"\bparticipant-safe\b", re.IGNORECASE),
    re.compile(r"\b(?:claim|evidence) boundary\b", re.IGNORECASE),
    re.compile(r"\b(?:retrieval|ranking) provenance\b", re.IGNORECASE),
    re.compile(r"\brelevance verdict\b", re.IGNORECASE),
    re.compile(r"\bformal (?:route|evidence|study|collection)\b", re.IGNORECASE),
    re.compile(r"\b(?:candidate|exemplar)\b", re.IGNORECASE),
    re.compile(r"\bappend-only\b", re.IGNORECASE),
    re.compile(r"\bresponse state\b", re.IGNORECASE),
    re.compile(r"\bqualitative note\b", re.IGNORECASE),
    re.compile(r"\brevision\b", re.IGNORECASE),
    re.compile(r"candidate origin", re.IGNORECASE),
    re.compile(r"\bretrieved\b", re.IGNORECASE),
    re.compile(r"\b(?:retrieval[ _-]?)?rank\b", re.IGNORECASE),
    re.compile(r"\b(?:(?:retrieval|similarity)[ _-]?)?score\b", re.IGNORECASE),
    re.compile(r"\bdistance\b", re.IGNORECASE),
    re.compile(r"(?:data-|[\"'])origin\b", re.IGNORECASE),
    re.compile(r"\brepeat(?: identity)?\b", re.IGNORECASE),
    re.compile(r"expected[_-](?:answer|outcome|result)", re.IGNORECASE),
    re.compile(r"\baggregate similarity\b", re.IGNORECASE),
    re.compile(
        r"\b(?:query_id|candidate_id|comparison_digest|bundle_digest|grain_id|player_id)\b",
        re.IGNORECASE,
    ),
)


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._suppressed = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style"}:
            self._suppressed += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._suppressed:
            self._suppressed -= 1

    def handle_data(self, data: str) -> None:
        if not self._suppressed:
            self.parts.append(data)


def _visible_text(document: str) -> str:
    parser = _VisibleText()
    parser.feed(document)
    return " ".join(" ".join(parser.parts).split())


def _assert_participant_safe(document: str) -> None:
    decoded = html.unescape(document)
    for pattern in _BYTE_FORBIDDEN:
        assert pattern.search(decoded) is None, (
            f"participant bytes expose forbidden internal language: {pattern.pattern}"
        )


def _assert_neutral_asset_payload(document: str) -> None:
    decoded = html.unescape(document)
    for pattern in (
        re.compile(r"\bw(?:0?[3-9]|10)\b", re.IGNORECASE),
        re.compile(r"/w10(?:/|\b)", re.IGNORECASE),
        re.compile(r"\bid-(?:loc|pass|duel|defloc|shotloc|gk)-01\b", re.IGNORECASE),
        re.compile(r"recorded_x_\d+_\d+__recorded_y_\d+_\d+", re.IGNORECASE),
        re.compile(r"\bmechanics[- ]pilot\b", re.IGNORECASE),
        re.compile(
            r"\b(?:query_id|candidate_id|comparison_digest|bundle_digest|grain_id|player_id)\b",
            re.IGNORECASE,
        ),
    ):
        assert pattern.search(decoded) is None, pattern.pattern


def _csrf(document: str) -> str:
    matched = re.search(r'<input type="hidden" name="csrf" value="([^"]+)"', document)
    assert matched is not None
    return matched.group(1)


def _fixture_comparisons(monkeypatch: pytest.MonkeyPatch) -> tuple[object, ...]:
    spec = importlib.util.spec_from_file_location(
        "w10_participant_boundary_fixture",
        ROOT / "tests/unit/test_w10_expert_evidence_v2.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    requests = (
        ("GK", None),
        ("DF", None),
        (
            "MD",
            (MdEvidenceSubrubricV2.DEFENSIVE, MdEvidenceSubrubricV2.DEFENSIVE),
        ),
        (
            "MD",
            (MdEvidenceSubrubricV2.SHOOTING, MdEvidenceSubrubricV2.SHOOTING),
        ),
        ("FW", None),
    )
    comparisons = []
    for position, branches in requests:
        exemplar, candidate = module._fixture_bundles(
            monkeypatch,
            position=position,
            branches=branches,
        )
        comparisons.append(build_participant_evidence_comparison_v2(exemplar, candidate))
    assert len({item.comparison_digest for item in comparisons}) == 5
    return tuple(comparisons)


def _fixture_store(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    comparisons: tuple[object, ...] | None = None,
) -> HistoricalComparisonPilotStore:
    root.mkdir(parents=True, exist_ok=True)
    selected = comparisons or _fixture_comparisons(monkeypatch)
    authority_path = root / "historical-player-comparison-authority.json"
    authority_path.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": 3,
                "authority_version": HISTORICAL_COMPARISON_AUTHORITY_VERSION,
                "participant_contract_version": HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
                "response_contract_version": HISTORICAL_COMPARISON_RESPONSE_VERSION,
                "debrief_contract_version": HISTORICAL_COMPARISON_DEBRIEF_VERSION,
                "lane": "MECHANICS_PILOT",
                "comparisons": [item.model_dump(mode="json") for item in selected],
            }
        )
    )
    return HistoricalComparisonPilotStore(
        database_path=root / "historical-player-comparison-pilot-v1.sqlite3",
        authority_path=authority_path,
        allowed_root=root,
    )


@pytest.fixture()
def participant_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[FastAPI, Path]:
    fixture_root = tmp_path / "isolated-participant-pilot"
    store = _fixture_store(fixture_root, monkeypatch)
    return create_historical_player_comparison_app(store=store, allow_test_host=True), fixture_root


def _eligible_form(csrf: str, code: str) -> dict[str, str]:
    return {
        "csrf": csrf,
        "participant_code": code,
        "years_experience": "3",
        "experience_professional_playing": "true",
        "assessed_players_within_window": "true",
        "conflict_declared": "false",
        "conflict_note": "",
        **CONSENT,
    }


def _record_response(
    store: HistoricalComparisonPilotStore,
    capability: str,
    token: str,
    comparison: ParticipantEvidenceComparisonV2,
    *,
    rating: int = 3,
) -> object:
    snapshot = store.load_session(capability)
    helpful_families = tuple(
        sorted(
            {
                family.family_id
                for panel in (comparison.exemplar, comparison.candidate)
                for family in panel.independent_descriptors
                if family.mandatory_for_selected_rubric
            }
        )
    )
    assert helpful_families
    request_digest = canonical_research_digest(
        {
            "action": "record-comparison",
            "revision": snapshot.revision,
            "comparison_digest": comparison.comparison_digest,
            "rating": rating,
        }
    )
    return store.record(
        capability=capability,
        command_id=uuid4(),
        expected_revision=snapshot.revision,
        request_digest=request_digest,
        presentation_token=token,
        state=JudgementState.RATED,
        evidence_sufficiency=EvidenceSufficiencyV2.SUFFICIENT,
        assessment_basis=AssessmentBasisV2.SUPPLIED_EVIDENCE,
        relevance_rating=rating,
        confidence=4,
        evidence_gap=None,
        citation_family_ids=helpful_families,
        statistics_helped=True,
        explanation="The additional playing evidence made this comparison assessable.",
    )


def _record_all_comparisons(
    store: HistoricalComparisonPilotStore,
    capability: str,
) -> None:
    while task := store.task(capability):
        token, comparison, _ordinal, _total = task
        _record_response(store, capability, token, comparison)


def _record_debrief(
    store: HistoricalComparisonPilotStore,
    capability: str,
    *,
    unclear: bool,
) -> object:
    snapshot = store.load_session(capability)
    request_digest = canonical_research_digest(
        {
            "action": "record-feedback",
            "revision": snapshot.revision,
            "unclear": unclear,
        }
    )
    return store.record_debrief(
        capability=capability,
        command_id=uuid4(),
        expected_revision=snapshot.revision,
        request_digest=request_digest,
        names_or_minutes_only=False,
        names_or_minutes_details=None,
        position_lacked_evidence=False,
        position_evidence_details=None,
        interface_unclear=unclear,
        interface_clarity_details=(
            "One chart label needed a clearer football example." if unclear else None
        ),
        system_preference_revealed=False,
        preference_revelation_details=None,
    )


def test_friendly_route_owns_the_address_and_legacy_route_only_redirects(
    participant_app: tuple[FastAPI, Path],
) -> None:
    app, _fixture_root = participant_app
    client = TestClient(app, base_url="http://127.0.0.1")

    legacy = client.get(LEGACY_PATH, follow_redirects=False)
    assert legacy.status_code in {303, 307, 308}
    assert legacy.headers["location"] == FRIENDLY_PATH

    page = client.get(FRIENDLY_PATH)
    assert page.status_code == 200
    assert page.url.path == FRIENDLY_PATH
    assert FRIENDLY_PATH in page.text
    assert LEGACY_PATH not in page.text
    for action in re.findall(r'action="([^"]+)"', page.text):
        assert action.startswith(FRIENDLY_PATH)
    assets = re.findall(r'(?:href|src)="(/static/[^"]+)"', page.text)
    assert assets
    assert all(asset.startswith("/static/historical-player-comparison/") for asset in assets)
    for asset in assets:
        payload = client.get(asset)
        assert payload.status_code == 200
        _assert_neutral_asset_payload(payload.text)
    _assert_participant_safe(page.text)


def test_introduction_is_self_contained_and_uses_plain_eligibility_and_consent_language(
    participant_app: tuple[FastAPI, Path],
) -> None:
    app, _fixture_root = participant_app
    page = TestClient(app, base_url="http://127.0.0.1").get(FRIENDLY_PATH)
    visible = _visible_text(page.text).casefold()

    for expected in (
        "trial",
        "historical player-comparison",
        "five pairs",
        "participant code",
        "stored locally",
        "not sent",
        "withdraw before final submission",
        "locked and cannot be edited",
        "not recruitment advice",
        "conflict",
    ):
        assert expected in visible
    assert "professional playing" in visible
    assert "last five years" in visible
    assert "aria-describedby=" in page.text
    _assert_participant_safe(page.text)


def test_rendered_comparison_has_plain_sections_readable_positions_and_no_leakage(
    participant_app: tuple[FastAPI, Path],
) -> None:
    app, fixture_root = participant_app
    client = TestClient(app, base_url="http://127.0.0.1")
    entry = client.get(FRIENDLY_PATH)
    started = client.post(
        f"{FRIENDLY_PATH}/sessions",
        data=_eligible_form(_csrf(entry.text), "BOUNDARY-PLAYER-01"),
        follow_redirects=True,
    )

    assert started.status_code == 200
    assert started.url.path == FRIENDLY_PATH
    visible = _visible_text(started.text)
    visible_folded = visible.casefold()
    for expected in (
        "comparison 1 of 5",
        "how credible is player b as a historical playing-style comparison to player a",
        "statistics used to find similar players",
        "additional playing evidence",
        "this information provides extra context that was not used to select the comparison",
        "where recorded actions began",
        "types of passes attempted",
        "what this information cannot tell you",
        "can you make a fair comparison from the information provided",
        "how credible is player b",
        "how confident are you",
        "what information helped you most",
        "what did you base your answer on",
        "was important information missing",
        "please explain anything that was unclear or insufficient",
    ):
        assert expected in visible_folded
    assert any(
        position in visible for position in ("Goalkeeper", "Defender", "Midfielder", "Forward")
    )
    assert re.search(r"(?:^|[ ·(])(?:GK|DF|MD|FW)(?:$|[ ·)])", visible) is None
    assert "not applicable" not in visible_folded
    assert "independent descriptors" not in visible_folded
    if "goalkeeper action mix" in visible_folded:
        assert "not save quality" in visible_folded
    assert "pitch direction" in visible_folded
    assert "effectiveness" in visible_folded or "quality" in visible_folded
    _assert_participant_safe(started.text)

    databases = tuple(fixture_root.rglob("*.sqlite3"))
    assert len(databases) == 1
    assert databases[0].is_relative_to(fixture_root)


def test_server_validation_errors_are_plain_bounded_and_participant_safe(
    participant_app: tuple[FastAPI, Path],
) -> None:
    app, _fixture_root = participant_app
    client = TestClient(app, base_url="http://127.0.0.1")
    entry = client.get(FRIENDLY_PATH)
    form = _eligible_form(_csrf(entry.text), "BOUNDARY-PLAYER-02")
    form["years_experience"] = "three"

    response = client.post(f"{FRIENDLY_PATH}/sessions", data=form)

    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert "years of experience" in _visible_text(response.text).casefold()
    assert "whole number" in _visible_text(response.text).casefold()
    assert 'aria-invalid="true"' in response.text
    _assert_participant_safe(response.text)


def test_participant_app_is_loopback_only_and_has_no_json_or_openapi_payload(
    participant_app: tuple[FastAPI, Path],
) -> None:
    app, _fixture_root = participant_app
    local = TestClient(app, base_url="http://127.0.0.1")
    assert local.get("/openapi.json").status_code == 404
    assert local.get(f"{FRIENDLY_PATH}.json").status_code == 404

    remote = TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("203.0.113.50", 43000),
    )
    rejected = remote.get(FRIENDLY_PATH, headers={"host": "localhost"})
    assert rejected.status_code == 400
    assert "loopback" in rejected.text.casefold() or "this computer" in rejected.text.casefold()
    _assert_participant_safe(rejected.text)


def test_schedule_is_participant_keyed_deterministic_and_database_confined_to_tmp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    comparisons = _fixture_comparisons(monkeypatch)
    first = _fixture_store(tmp_path / "first", monkeypatch, comparisons=comparisons)
    second = _fixture_store(tmp_path / "second", monkeypatch, comparisons=comparisons)
    third = _fixture_store(tmp_path / "third", monkeypatch, comparisons=comparisons)

    first.prepare_session(
        participant_code="DETERMINISTIC-01",
        years_experience=4,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_PLAYING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items={key: True for key in CONSENT},
    )
    second.prepare_session(
        participant_code="DETERMINISTIC-01",
        years_experience=4,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_PLAYING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items={key: True for key in CONSENT},
    )
    third.prepare_session(
        participant_code="DETERMINISTIC-02",
        years_experience=4,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_PLAYING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items={key: True for key in CONSENT},
    )

    def order(database: Path) -> tuple[str, ...]:
        with sqlite3.connect(database) as connection:
            rows = connection.execute(
                "SELECT comparison_json FROM hpc_presentations ORDER BY ordinal"
            ).fetchall()
        return tuple(json.loads(row[0])["comparison_digest"] for row in rows)

    first_order = order(first.database_path)
    second_order = order(second.database_path)
    third_order = order(third.database_path)
    assert first_order == second_order
    assert third_order != first_order
    assert set(first_order) == {item.comparison_digest for item in comparisons}
    assert first.database_path.is_relative_to(tmp_path)
    assert second.database_path.is_relative_to(tmp_path)
    assert third.database_path.is_relative_to(tmp_path)


def test_new_store_exactly_reconstructs_revisions_debrief_and_immutable_completion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _fixture_store(tmp_path / "exact-reconstruction", monkeypatch)
    capability, prepared = store.prepare_session(
        participant_code="RECONSTRUCT-01",
        years_experience=5,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_PLAYING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items={key: True for key in CONSENT},
    )
    assert prepared.revision == 0
    assert prepared.complete is False

    _record_all_comparisons(store, capability)
    review = store.review_tasks(capability)
    assert len(review) == 5
    first_token, _first_response, _ordinal, first_comparison = review[0]
    revised = _record_response(
        store,
        capability,
        first_token,
        first_comparison,
        rating=2,
    )
    assert revised.judgements[0].relevance_rating == 2

    initial_feedback = _record_debrief(store, capability, unclear=False)
    assert initial_feedback.debrief is not None
    assert initial_feedback.debrief.any_label_chart_warning_or_navigation_unclear is False
    revised_feedback = _record_debrief(store, capability, unclear=True)
    assert revised_feedback.debrief is not None
    assert revised_feedback.debrief.any_label_chart_warning_or_navigation_unclear is True
    assert revised_feedback.debrief.interface_clarity_details is not None

    before_completion = store.load_session(capability)
    completed = store.complete(
        capability=capability,
        command_id=uuid4(),
        expected_revision=before_completion.revision,
        request_digest=canonical_research_digest(
            {"action": "complete", "revision": before_completion.revision}
        ),
    )
    reconstructed = store.load_session(capability)
    assert reconstructed == completed
    assert reconstructed.complete is True
    assert reconstructed.revision == 9
    assert reconstructed.completed_at is not None
    assert reconstructed.receipt_digest is not None
    assert len(reconstructed.judgements) == 5
    assert reconstructed.judgements[0].relevance_rating == 2
    assert reconstructed.debrief == revised_feedback.debrief

    with pytest.raises(ExpertStudyConflictError, match="cannot be changed"):
        _record_response(store, capability, first_token, first_comparison, rating=4)
    with pytest.raises(ExpertStudyConflictError, match="cannot be changed"):
        _record_debrief(store, capability, unclear=False)
    with pytest.raises(ExpertStudyConflictError, match="out of date"):
        store.complete(
            capability=capability,
            command_id=uuid4(),
            expected_revision=reconstructed.revision,
            request_digest=canonical_research_digest(
                {"action": "complete-again", "revision": reconstructed.revision}
            ),
        )
    assert store.load_session(capability) == reconstructed


def test_new_store_detects_semantic_tampering_during_exact_reconstruction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _fixture_store(tmp_path / "tamper-detection", monkeypatch)
    capability, _prepared = store.prepare_session(
        participant_code="TAMPER-CHECK-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_PLAYING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items={key: True for key in CONSENT},
    )
    task = store.task(capability)
    assert task is not None
    token, comparison, _ordinal, _total = task
    saved = _record_response(store, capability, token, comparison)
    assert store.load_session(capability) == saved

    with sqlite3.connect(store.database_path) as connection:
        row = connection.execute(
            "SELECT session_id,presentation_id,judgement_json FROM hpc_judgements"
        ).fetchone()
        assert row is not None
        altered = json.loads(row[2])
        altered["confidence"] = 1
        connection.execute(
            "UPDATE hpc_judgements SET judgement_json=? WHERE session_id=? AND presentation_id=?",
            (canonical_json_bytes(altered).decode(), row[0], row[1]),
        )

    with pytest.raises(ExpertStudyIntegrityError):
        store.load_session(capability)

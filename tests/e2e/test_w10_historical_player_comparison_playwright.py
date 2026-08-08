"""Real-browser boundary and journey checks for the historical comparison form."""

from __future__ import annotations

import html
import importlib.util
import re
import socket
import sqlite3
import threading
from collections.abc import Iterator
from pathlib import Path
from time import monotonic, sleep

import pytest
import uvicorn
from fastapi import FastAPI
from playwright.sync_api import Browser, Page, expect, sync_playwright

from scouting.contracts.expert_relevance import MdEvidenceSubrubricV2
from scouting.data_products.wyscout.expert_evidence import (
    build_participant_evidence_comparison_v2,
)
from scouting.storage.expert_study import (
    HISTORICAL_COMPARISON_AUTHORITY_VERSION,
    HISTORICAL_COMPARISON_DEBRIEF_VERSION,
    HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
    HISTORICAL_COMPARISON_RESPONSE_VERSION,
    HistoricalComparisonPilotStore,
)
from scouting.storage.formats import canonical_json_bytes
from scouting.web.w10_expert_study import create_historical_player_comparison_app

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = Path(__file__).resolve().parents[2]
FRIENDLY_PATH = "/historical-player-comparison"
CONSENT_NAMES = (
    "voluntary_participation",
    "local_pseudonymous_storage",
    "withdrawal_before_submission_understood",
    "immutable_after_submission_understood",
    "research_limitations_understood",
)
FORBIDDEN_PARTICIPANT_PATTERNS = (
    r"\bw(?:0?[3-9]|10)\b",
    r"\bg-rw4\b",
    r"\b(?:a5|08d|08e|08f)\b",
    r"\bv[12]\b",
    r"\b(?:phase|gate|checkpoint|rework)\b",
    r"\b(?:authority|protocol)\b",
    r"\bmatrix\b",
    r"\bscorer\b",
    r"feature registry",
    r"canonical authority",
    r"\bpredicate\b",
    r"\bdigest\b",
    r"\blineage\b",
    r"schema version",
    r"policy digest",
    r"authority version",
    r"query[- ]pack",
    r"independent descriptors?",
    r"independent famil(?:y|ies)",
    r"\bid-(?:loc|pass|duel|defloc|shotloc|gk)-01\b",
    r"recorded_x_\d+_\d+__recorded_y_\d+_\d+",
    r"\bobserved value\b",
    r"\braw value\b",
    r"\bgoverned minutes\b",
    r"\bopportunity (?:denominator|floor)\b",
    r"\bretained actions?\b",
    r"\bpilot\b",
    r"\bparticipant-safe\b",
    r"\b(?:claim|evidence) boundary\b",
    r"\b(?:retrieval|ranking) provenance\b",
    r"\brelevance verdict\b",
    r"\bformal (?:route|evidence|study|collection)\b",
    r"\b(?:candidate|exemplar)\b",
    r"\bappend-only\b",
    r"\bresponse state\b",
    r"\bqualitative note\b",
    r"\brevision\b",
    r"candidate origin",
    r"\bretrieved\b",
    r"\b(?:retrieval[ _-]?)?rank\b",
    r"\b(?:(?:retrieval|similarity)[ _-]?)?score\b",
    r"\bdistance\b",
    r"(?:data-|[\"'])origin\b",
    r"\brepeat(?: identity)?\b",
    r"expected[_-](?:answer|outcome|result)",
    r"aggregate similarity",
    r"\b(?:query_id|candidate_id|comparison_digest|bundle_digest|grain_id|player_id)\b",
)


def _assert_safe_participant_bytes(document: str) -> None:
    decoded = html.unescape(document)
    for pattern in FORBIDDEN_PARTICIPANT_PATTERNS:
        assert re.search(pattern, decoded, re.IGNORECASE) is None, pattern


@pytest.fixture()
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(executable_path=CHROME, headless=True)
        try:
            yield instance
        finally:
            instance.close()


@pytest.fixture()
def participant_fixture_app(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[FastAPI, Path]:
    spec = importlib.util.spec_from_file_location(
        "w10_historical_comparison_e2e_fixture",
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

    fixture_root = tmp_path / "historical-player-comparison-browser-witness"
    fixture_root.mkdir()
    authority_path = fixture_root / "historical-player-comparison-authority.json"
    authority_path.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": 3,
                "authority_version": HISTORICAL_COMPARISON_AUTHORITY_VERSION,
                "participant_contract_version": HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
                "response_contract_version": HISTORICAL_COMPARISON_RESPONSE_VERSION,
                "debrief_contract_version": HISTORICAL_COMPARISON_DEBRIEF_VERSION,
                "lane": "MECHANICS_PILOT",
                "comparisons": [item.model_dump(mode="json") for item in comparisons],
            }
        )
    )
    store = HistoricalComparisonPilotStore(
        database_path=fixture_root / "historical-player-comparison-pilot-v1.sqlite3",
        authority_path=authority_path,
        allowed_root=fixture_root,
    )
    app = create_historical_player_comparison_app(store=store, allow_test_host=True)
    return app, fixture_root


@pytest.fixture()
def loopback_url(participant_fixture_app: tuple[FastAPI, Path]) -> Iterator[str]:
    app, _fixture_root = participant_fixture_app
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = monotonic() + 10
    while not server.started and monotonic() < deadline:
        sleep(0.01)
    assert server.started, "loopback historical-comparison server did not start"
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def _complete_entry(page: Page, code: str) -> None:
    page.locator('input[name="participant_code"]').fill(code)
    page.locator('input[name="years_experience"]').fill("4")
    page.locator('input[name="experience_professional_playing"]').check()
    page.locator('input[name="assessed_players_within_window"][value="true"]').check()
    page.locator('input[name="conflict_declared"][value="false"]').check()
    for name in CONSENT_NAMES:
        page.locator(f'input[name="{name}"]').check()


def _choose_assessable_response(page: Page, *, rating: str = "3", confidence: str = "4") -> None:
    page.locator('input[name="fair_comparison"][value="yes"]').check()
    page.locator('input[name="assessment_basis"][value="supplied_evidence"]').check()
    page.locator(f'input[name="credibility"][value="{rating}"]').check()
    page.locator(f'input[name="confidence"][value="{confidence}"]').check()
    page.locator('input[name="helped_statistics"][value="true"]').check()
    additional_choices = page.locator(
        'input[name^="helped_"][type="checkbox"]:not([name="helped_statistics"])'
    )
    assert additional_choices.count() >= 1
    additional_choices.first.check()
    page.locator('input[name="important_information_missing"][value="no"]').check()


def _install_browser_witness(
    page: Page, loopback_url: str
) -> tuple[list[str], list[tuple[str, int]], list[str], list[str]]:
    requests: list[str] = []
    http_errors: list[tuple[str, int]] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    page.on("request", lambda request: requests.append(request.url))
    page.on(
        "response",
        lambda response: (
            http_errors.append((response.url, response.status)) if response.status >= 400 else None
        ),
    )
    page.on(
        "console",
        lambda message: console_errors.append(message.text) if message.type == "error" else None,
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.set_default_timeout(8_000)
    page.goto(f"{loopback_url}{FRIENDLY_PATH}", wait_until="networkidle")
    return requests, http_errors, console_errors, page_errors


def test_accessible_desktop_mobile_keyboard_and_participant_payload_boundary(
    loopback_url: str,
    browser: Browser,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    requests, http_errors, console_errors, page_errors = _install_browser_witness(
        page, loopback_url
    )
    try:
        assert page.url == f"{loopback_url}{FRIENDLY_PATH}"
        assert page.locator("header").count() == 1
        assert page.locator("main").count() == 1
        assert page.locator("h1").count() == 1
        page.keyboard.press("Tab")
        expect(page.locator(":focus")).to_have_class(re.compile("skip-link"))
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main-content"

        participant_code = page.locator('input[name="participant_code"]')
        participant_code.focus()
        page.locator('input[name="years_experience"]').fill("1")
        page.get_by_role("button", name=re.compile("begin|start", re.IGNORECASE)).click()
        assert page.locator(":invalid").count() >= 1
        assert page.evaluate("document.activeElement.name") in {
            "participant_code",
            "years_experience",
        }

        _complete_entry(page, "BROWSER-BOUNDARY-01")
        page.get_by_role("button", name=re.compile("begin|start", re.IGNORECASE)).focus()
        page.keyboard.press("Enter")
        page.wait_for_url(f"{loopback_url}{FRIENDLY_PATH}")
        expect(page.get_by_role("heading", name="Comparison 1 of 5")).to_be_visible()
        rendered = page.locator("body").inner_text()
        participant_html = page.content()
        _assert_safe_participant_bytes(rendered)
        _assert_safe_participant_bytes(participant_html)
        for expected in (
            "Statistics used to find similar players",
            "Additional playing evidence",
            "Where recorded actions began",
            "Types of passes attempted",
            "Can you make a fair comparison from the information provided?",
            "How credible is",
            "How confident are you?",
            "What did you base your answer on?",
            "What information helped you most?",
            "Was important information missing?",
        ):
            expect(page.get_by_text(expected, exact=False).first).to_be_visible()

        panels = page.locator(".player-card")
        assert panels.count() == 2
        first_labels = panels.nth(0).locator("dt").all_inner_texts()
        second_labels = panels.nth(1).locator("dt").all_inner_texts()
        assert first_labels == second_labels
        assert first_labels
        assert page.locator(".profile-label").count() >= 16
        comparison_rows = page.locator(".comparison-table tbody tr")
        assert comparison_rows.count() >= 16
        for index in range(comparison_rows.count()):
            assert comparison_rows.nth(index).locator("th, td").count() == 3
        assert page.locator("details").count() < 7
        assert re.search(r"\b\d+(?:\.\d+)?%", rendered)
        assert "not applicable" not in rendered.casefold()
        assert re.search(r"(?:^|[ ·(])(?:GK|DF|MD|FW)(?:$|[ ·)])", rendered) is None

        page.set_viewport_size({"width": 320, "height": 760})
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
        expect(page.get_by_role("heading", name="Comparison 1 of 5")).to_be_visible()
        page.locator('input[name="fair_comparison"][value="yes"]').focus()
        page.keyboard.press("Space")
        assert page.locator('input[name="fair_comparison"][value="yes"]').is_checked()

        assert requests and all(url.startswith(loopback_url) for url in requests)
        assert http_errors == []
        assert not console_errors, "\n".join(console_errors)
        assert not page_errors, "\n".join(page_errors)
    finally:
        page.close()


def test_complete_resume_review_correct_debrief_submit_and_local_receipt_without_coaching(
    loopback_url: str,
    browser: Browser,
    participant_fixture_app: tuple[FastAPI, Path],
) -> None:
    _app, fixture_root = participant_fixture_app
    page = browser.new_page(viewport={"width": 1180, "height": 850})
    requests, http_errors, console_errors, page_errors = _install_browser_witness(
        page, loopback_url
    )
    try:
        _complete_entry(page, "BROWSER-JOURNEY-01")
        page.get_by_role("button", name=re.compile("begin|start", re.IGNORECASE)).click()
        page.wait_for_url(f"{loopback_url}{FRIENDLY_PATH}")

        for ordinal in range(1, 6):
            expect(page.get_by_role("heading", name=f"Comparison {ordinal} of 5")).to_be_visible()
            _choose_assessable_response(page)
            save = page.get_by_role("button", name=re.compile("save", re.IGNORECASE)).first
            if ordinal == 1:
                save.focus()
                page.keyboard.press("Enter")
                expect(page.get_by_role("heading", name="Comparison 2 of 5")).to_be_visible()
                page.reload(wait_until="networkidle")
                expect(page.get_by_role("heading", name="Comparison 2 of 5")).to_be_visible()
                expect(
                    page.get_by_text(
                        "Welcome back. Your saved answers are still here.", exact=False
                    )
                ).to_be_visible()
                continue
            save.click()

        expect(page.get_by_text("Tell us about the form", exact=False)).to_be_visible()
        _assert_safe_participant_bytes(page.content())
        feedback_fields = (
            "names_or_minutes_only",
            "position_lacked_evidence",
            "interface_unclear",
            "system_preference_revealed",
        )
        for field in feedback_fields:
            control = page.locator(f'input[name="{field}"][value="no"]')
            assert control.count() == 1
            control.check()
        feedback_text = page.locator("body").inner_text().casefold()
        for expected in (
            "names or recorded minutes",
            "lack enough playing evidence",
            "label, chart, warning, or navigation",
            "reveal which comparison the system preferred",
        ):
            assert expected in feedback_text
        page.get_by_role("button", name=re.compile("save feedback", re.IGNORECASE)).click()

        expect(page.get_by_text(re.compile("review", re.IGNORECASE)).first).to_be_visible()
        _assert_safe_participant_bytes(page.content())
        review_cards = page.locator(".review-list > .review-card")
        assert review_cards.count() == 5
        review_cards.first.locator("summary").click()
        review_cards.first.locator('input[name="confidence"][value="3"]').check()
        review_cards.first.get_by_role("button", name="Save changes").click()
        expect(page.get_by_text(re.compile("review", re.IGNORECASE)).first).to_be_visible()
        review_cards = page.locator(".review-list > .review-card")
        review_cards.first.locator("summary").click()
        assert review_cards.first.locator('input[name="confidence"][value="3"]').is_checked()

        immutable_notice = page.get_by_text(re.compile("cannot be edited", re.IGNORECASE))
        expect(immutable_notice.first).to_be_visible()
        page.locator(".immutable-confirmation input").check()
        submit = page.get_by_role("button", name=re.compile("submit", re.IGNORECASE)).last
        submit.click()
        expect(
            page.get_by_text(re.compile("complete|submitted", re.IGNORECASE)).first
        ).to_be_visible()
        completion_text = page.locator("body").inner_text()
        for expected in (
            "thank you",
            "stored locally and are now locked",
            "historical player-comparison form trial",
            "participant code",
            "comparisons completed",
            "submitted on this computer",
            "submitted and locked",
        ):
            assert expected in completion_text.casefold()
        _assert_safe_participant_bytes(page.content())

        databases = tuple(fixture_root.rglob("*.sqlite3"))
        assert len(databases) == 1
        database = databases[0]
        assert database.is_relative_to(fixture_root)
        with sqlite3.connect(database) as connection:
            assert connection.execute("SELECT count(*) FROM hpc_sessions").fetchone()[0] == 1
            assert connection.execute("SELECT count(*) FROM hpc_judgements").fetchone()[0] == 5
            assert connection.execute("SELECT count(*) FROM hpc_completions").fetchone()[0] == 1
            assert connection.execute("SELECT count(*) FROM hpc_debriefs").fetchone()[0] == 1

        assert requests and all(url.startswith(loopback_url) for url in requests)
        assert http_errors == []
        assert not console_errors, "\n".join(console_errors)
        assert not page_errors, "\n".join(page_errors)
    finally:
        page.close()

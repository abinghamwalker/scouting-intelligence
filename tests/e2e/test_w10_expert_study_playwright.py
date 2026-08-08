"""Real-browser acceptance for the local W10 expert-study console."""

from __future__ import annotations

import importlib.util
import socket
import threading
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic, sleep

import pytest
import uvicorn
from fastapi import FastAPI
from playwright.sync_api import Browser, Page, expect, sync_playwright

from scouting.contracts.expert_relevance import (
    ExpertRelevanceProtocol,
    ExpertStudyPresentationBundle,
    StudyMode,
)
from scouting.storage.expert_study import ExpertStudyStore, V2MechanicsPilotStore
from scouting.storage.formats import canonical_json_bytes
from scouting.web.w10_expert_study import (
    create_w10_expert_study_app,
    create_w10_v2_mechanics_pilot_app,
)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = Path(__file__).resolve().parents[2]
CONSENT_NAMES = (
    "voluntary_participation",
    "local_pseudonymous_storage",
    "withdrawal_before_submission_understood",
    "immutable_after_submission_understood",
    "research_limitations_understood",
)


@pytest.fixture()
def fixture_app(tmp_path: Path) -> FastAPI:
    protocol = ExpertRelevanceProtocol.model_validate_json(
        (ROOT / "configs/evaluation/w10-expert-relevance-protocol-v1.json").read_bytes()
    )
    presentation = ExpertStudyPresentationBundle.model_validate_json(
        (ROOT / "configs/evaluation/w10-expert-study-presentation-v1.json").read_bytes()
    )

    def clock() -> datetime:
        return datetime(2026, 8, 5, 18, 0, tzinfo=UTC)

    pilot = ExpertStudyStore(
        database_path=tmp_path / "pilot.sqlite3",
        capture_root=tmp_path / "pilot-captures",
        allowed_root=tmp_path,
        mode=StudyMode.MECHANICS_PILOT,
        protocol=protocol,
        presentation=presentation,
        test_only=True,
        clock=clock,
    )
    formal = ExpertStudyStore(
        database_path=tmp_path / "formal.sqlite3",
        capture_root=tmp_path / "formal-captures",
        allowed_root=tmp_path,
        mode=StudyMode.FORMAL_G_RW4,
        protocol=protocol,
        presentation=presentation,
        test_only=True,
        clock=clock,
    )
    return create_w10_expert_study_app(
        protocol=protocol,
        presentation=presentation,
        pilot_store=pilot,
        formal_store=formal,
    )


@pytest.fixture()
def v2_fixture_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    from scouting.data_products.wyscout.expert_evidence import (
        build_participant_evidence_comparison_v2,
    )

    spec = importlib.util.spec_from_file_location(
        "w10_v2_e2e_fixture", ROOT / "tests/unit/test_w10_expert_evidence_v2.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    exemplar, candidate = module._fixture_bundles(monkeypatch)
    comparison = build_participant_evidence_comparison_v2(exemplar, candidate)
    authority = {
        "schema_version": 2,
        "authority_version": "w10-v2-mechanics-pilot-authority-v1",
        "lane": "MECHANICS_PILOT",
        "comparisons": [comparison.model_dump(mode="json")],
    }
    authority_path = tmp_path / "mechanics-pilot-authority-v1.json"
    authority_path.write_bytes(canonical_json_bytes(authority))
    return create_w10_v2_mechanics_pilot_app(
        store=V2MechanicsPilotStore(
            database_path=tmp_path / "mechanics-pilot-v2.sqlite3",
            authority_path=authority_path,
            allowed_root=tmp_path,
        ),
        allow_test_host=True,
    )


@pytest.fixture()
def loopback_url(fixture_app: FastAPI) -> Iterator[str]:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(fixture_app, host="127.0.0.1", port=port, log_level="error")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = monotonic() + 10
    while not server.started and monotonic() < deadline:
        sleep(0.01)
    assert server.started, "loopback W10 uvicorn did not start"
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture()
def v2_loopback_url(v2_fixture_app: FastAPI) -> Iterator[str]:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(v2_fixture_app, host="127.0.0.1", port=port, log_level="error")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = monotonic() + 10
    while not server.started and monotonic() < deadline:
        sleep(0.01)
    assert server.started
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture()
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(executable_path=CHROME, headless=True)
        try:
            yield instance
        finally:
            instance.close()


def _complete_entry_form(page: Page, code: str) -> None:
    locator = page.locator
    locator('input[name="participant_code"]').fill(code)
    locator('input[name="years_experience"]').fill("3")
    locator('input[name="experience_professional_scouting"]').check()
    locator('input[name="assessed_players_within_window"]').check()
    for name in CONSENT_NAMES:
        locator(f'input[name="{name}"]').check()


def test_narrow_screen_full_pilot_resume_submit_detach_and_next_participant(
    loopback_url: str,
    browser: Browser,
) -> None:
    page = browser.new_page(viewport={"width": 320, "height": 760})
    page.set_default_timeout(8_000)
    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url))
    try:
        page.goto(f"{loopback_url}/w10", wait_until="networkidle")
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
        page.keyboard.press("Tab")
        assert page.locator(":focus").get_attribute("class") == "skip-link"
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main-content"
        page.locator("details summary").click()
        body = page.locator("body").inner_text()
        for expected in (
            "30–35 minutes",
            "8 query sets",
            "80 blinded primary candidates",
            "2 delayed, blinded repeat assessments",
            "at least 5 eligible experts",
            "football relevance from 0–4",
            "confidence from 1–5",
            "PASS",
            "FAIL",
            "INSUFFICIENT_EVIDENCE",
            "Pilot versus formal",
        ):
            assert expected in body
        assert page.locator("header").count() == 1
        assert page.locator("nav").count() == 1
        assert page.locator("main").count() == 1
        assert page.locator("footer").count() == 1
        assert page.locator("h1").count() == 1

        _complete_entry_form(page, "PILOT-41")
        page.get_by_role("button", name="Start mechanics pilot").click()
        expect(page.get_by_text("0 / 22", exact=True)).to_be_visible()
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
        assert page.locator('select[name="relevance_rating"]').evaluate(
            "element => element.validity.valueMissing"
        )
        assert page.locator('select[name="confidence"]').evaluate(
            "element => element.validity.valueMissing"
        )
        first_candidate = page.locator(".player-card").nth(1).inner_text()

        page.get_by_role("radio", name="Abstain", exact=True).check()
        expect(page.locator("#study-status")).to_contain_text(
            "Explicit abstain or unable-to-assess selected"
        )
        assert page.locator('select[name="relevance_rating"]').is_disabled()
        assert page.locator('select[name="confidence"]').is_disabled()
        page.get_by_role("button", name="Save and continue").click()
        expect(page.get_by_text("1 / 22", exact=True)).to_be_visible()
        page.reload(wait_until="networkidle")
        expect(page.get_by_text("1 / 22", exact=True)).to_be_visible()
        assert first_candidate not in page.locator(".player-card").nth(1).inner_text()

        for completed in range(2, 23):
            page.locator('select[name="relevance_rating"]').select_option("3")
            page.locator('select[name="confidence"]').select_option("4")
            page.get_by_role("button", name="Save and continue").click()
            if completed < 22:
                expect(page.get_by_text(f"{completed} / 22", exact=True)).to_be_visible()

        expect(page.get_by_text("Review and correct responses before sealing")).to_be_visible()
        page.locator(".review-list details summary").first.click()
        expect(page.get_by_text("Save append-only correction").first).to_be_visible()
        assert "All 22 blinded presentations" in page.locator("#study-content").inner_text()
        page.get_by_role("button", name="Submit once and make responses immutable").click()
        expect(page.get_by_text("Pilot complete — not formal relevance evidence")).to_be_visible()
        assert "cannot enter formal tables" in page.locator("#study-content").inner_text()
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")

        page.get_by_role("button", name="Finish and prepare next participant").click()
        expect(page.get_by_text("Start a pseudonymous local session")).to_be_visible()
        _complete_entry_form(page, "PILOT-42")
        page.get_by_role("button", name="Start mechanics pilot").click()
        expect(page.get_by_text("0 / 22", exact=True)).to_be_visible()
        page.reload(wait_until="networkidle")
        expect(page.get_by_text("0 / 22", exact=True)).to_be_visible()
        assert all(url.startswith(loopback_url) for url in requests)
    finally:
        page.close()


def test_exact_approval_unlocks_blinded_82_task_formal_entry(
    loopback_url: str,
    browser: Browser,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.set_default_timeout(8_000)
    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url))
    try:
        page.goto(f"{loopback_url}/w10", wait_until="networkidle")
        formal_button = page.get_by_role("button", name="Start formal frozen study")
        assert formal_button.is_disabled()
        page.locator('input[name="approved_by_pseudonym"]').fill("OWNER-41")
        page.locator('input[name="confirmation"]').check()
        page.get_by_role("button", name="Record exact human approval").click()
        expect(page.get_by_text("Exact protocol approved.")).to_be_visible()
        assert "Approval alone creates no relevance result" in page.locator("body").inner_text()
        assert not formal_button.is_disabled()

        _complete_entry_form(page, "EXPERT-41")
        formal_button.click()
        expect(page.get_by_text("0 / 82", exact=True)).to_be_visible()
        expect(page.get_by_text("Formal frozen study", exact=True)).to_be_visible()
        rendered = page.locator("body").inner_text().casefold()
        for forbidden in (
            "candidate origin",
            "retrieval score",
            "retrieval rank",
            "presentation kind",
            "repeat assessment",
            "83d47be3-aae3-5127-b936-e23d2df5e815",
            "f59fb3f6-e85b-5fba-8e5a-f8d996ad5f25",
        ):
            assert forbidden not in rendered
        page.reload(wait_until="networkidle")
        expect(page.get_by_text("0 / 82", exact=True)).to_be_visible()
        assert all(url.startswith(loopback_url) for url in requests)
    finally:
        page.close()


def test_v2_evidence_desktop_mobile_keyboard_and_safe_payload(
    v2_loopback_url: str, browser: Browser
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.set_default_timeout(8_000)
    requests: list[str] = []
    responses: list[tuple[str, int]] = []
    page.on("request", lambda request: requests.append(request.url))
    page.on("response", lambda response: responses.append((response.url, response.status)))
    try:
        page.goto(f"{v2_loopback_url}/w10/v2", wait_until="networkidle")
        page.keyboard.press("Tab")
        assert page.locator(":focus").get_attribute("class") == "skip-link"
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main-content"
        framing = page.locator("body").inner_text()
        assert "visible-identity assessment" in framing
        assert "retrieval provenance remains hidden" in framing
        assert "A blinded, local assessment" not in framing
        navigation = {
            "Study home": "/w10/v2",
            "Evidence boundary": "#boundary",
            "Current step": "#study-content",
        }
        for label, target in navigation.items():
            link = page.get_by_role("link", name=label, exact=True)
            assert link.get_attribute("href") == target
            link.focus()
            page.keyboard.press("Enter")
            if target.startswith("#"):
                expect(page.locator(target)).to_have_count(1)
                assert page.url.endswith(target)
            else:
                page.wait_for_url(f"{v2_loopback_url}{target}")
                assert page.url == f"{v2_loopback_url}{target}"
        for experience in (
            "professional_scouting",
            "recruitment_analysis",
            "performance_analysis",
            "professional_coaching",
            "professional_playing",
        ):
            assert page.locator(f'input[name="experience_{experience}"]').count() == 1
        _complete_entry_form(page, "V2-E2E-01")
        page.get_by_role("button", name="Start v2 mechanics pilot").click()
        expect(page.get_by_text("Historical role/style comparison 1 of 1")).to_be_visible()
        text = page.locator("body").inner_text().casefold()
        for expected in (
            "frozen w09 model inputs",
            "independent descriptors",
            "evidence glossary",
            "governed minutes",
            "compact w09-input profile",
        ):
            assert expected in text
        for forbidden in (
            "candidate origin",
            "retrieval rank",
            "aggregate similarity",
            "control identity",
            "evidence band",
            "expected",
            "previous",
            "aggregate",
            "query_id",
            "candidate_id",
            "comparison_digest",
            "bundle_digest",
        ):
            assert forbidden not in text
        participant_html = page.content().casefold()
        for protected_field in (
            "candidate origin",
            "retrieval rank",
            "aggregate similarity",
            "control identity",
            "evidence band",
            "query_id",
            "candidate_id",
            "comparison_digest",
            "bundle_digest",
        ):
            assert protected_field not in participant_html
        profiles = page.locator(".profile-visual")
        assert profiles.count() == 2
        exemplar_rows = profiles.nth(0).locator(".profile-row")
        candidate_rows = profiles.nth(1).locator(".profile-row")
        exemplar_ids = exemplar_rows.evaluate_all("rows => rows.map(row => row.dataset.metricId)")
        candidate_ids = candidate_rows.evaluate_all("rows => rows.map(row => row.dataset.metricId)")
        assert exemplar_ids == candidate_ids
        assert len(exemplar_ids) == 16
        for rows in (exemplar_rows, candidate_rows):
            for index in range(rows.count()):
                row = rows.nth(index)
                percentile = row.get_attribute("data-percentile")
                if percentile:
                    assert row.locator(".profile-fill").get_attribute("style") == (
                        f"width: {percentile}%"
                    )
                    assert row.get_attribute("data-raw-value") not in (None, "")
        open_family_counts = [
            page.locator(".evidence-panel").nth(index).locator("details[open]").count()
            for index in range(2)
        ]
        assert open_family_counts[0] == open_family_counts[1] and open_family_counts[0] > 0
        assert page.locator(".evidence-panel details:not([open])").count() >= 2
        page.get_by_label("Show within-position percentiles instead of raw values").check()
        expect(page.get_by_text("Within-position percentile").first).to_be_visible()
        expect(profiles.nth(0).locator(".profile-value.percentile-value").first).to_be_visible()
        page.set_viewport_size({"width": 320, "height": 760})
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
        # Complete the actual v2 journey: save, resume, append a zero-rated
        # correction, seal, detach only the HttpOnly capability, then start anew.
        page.locator('input[name="evidence_sufficiency"][value="sufficient"]').check()
        page.locator('input[name="assessment_basis"][value="supplied_evidence"]').check()
        page.locator('input[name="state"][value="rated"]').check()
        assert page.locator('select[name="citations"]').evaluate("element => element.required")
        assert page.locator('select[name="evidence_gap"]').is_disabled()
        page.locator('select[name="relevance_rating"]').select_option("3")
        page.locator('select[name="confidence"]').select_option("4")
        citation = page.locator('select[name="citations"] option').nth(1)
        page.locator('select[name="citations"]').select_option(citation.get_attribute("value"))
        page.get_by_role("button", name="Save response").click()
        expect(page.get_by_text("Review and correct before immutable submission")).to_be_visible()
        page.reload(wait_until="networkidle")
        page.locator(".review-card summary").click()
        page.locator('.review-card input[name="relevance_rating"]').fill("0")
        page.locator('.review-card select[name="citations"]').select_option(
            page.locator('.review-card select[name="citations"] option')
            .nth(1)
            .get_attribute("value")
        )
        page.get_by_role("button", name="Save append-only correction").click()
        expect(page.get_by_text("Review and correct before immutable submission")).to_be_visible()
        page.locator(".review-card summary").click()
        expect(page.locator('.review-card input[name="relevance_rating"]')).to_have_value("0")
        expect(page.locator('.review-card select[name="citations"]')).not_to_have_value("")
        page.get_by_role("button", name="Submit mechanics-pilot responses").click()
        expect(page.get_by_text("V2 pilot submitted")).to_be_visible()
        page.get_by_role("button", name="Finish and prepare next participant").click()
        expect(page.get_by_text("Start a pseudonymous v2 pilot session")).to_be_visible()
        _complete_entry_form(page, "V2-E2E-02")
        page.get_by_role("button", name="Start v2 mechanics pilot").click()
        expect(page.get_by_text("Historical role/style comparison 1 of 1")).to_be_visible()
        assert all(url.startswith(v2_loopback_url) for url in requests)
        assert all(status < 400 for _url, status in responses)
    finally:
        page.close()

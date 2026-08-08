"""Real-browser W08 workflow witnesses; synthetic automation, never a user study."""

from __future__ import annotations

import socket
import threading
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import monotonic, sleep

import pytest
import uvicorn
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from sqlalchemy import text

from scouting.contracts import WorkflowEvidenceOrigin
from scouting.web.w08 import create_w08_app

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


@pytest.fixture()
def workflow_runtime(tmp_path: Path) -> Iterator[tuple[str, object]]:
    """Serve one fresh, synthetic-only application exclusively on loopback."""
    app = create_w08_app(
        evidence_origin=WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST,
        database_path=tmp_path / "w08.sqlite3",
        allowed_root=tmp_path,
    )
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = monotonic() + 10
    while not server.started and monotonic() < deadline:
        sleep(0.01)
    assert server.started, "loopback W08 uvicorn did not start"
    try:
        yield f"http://127.0.0.1:{port}", app
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


def _login(page: Page, base: str, persona: dict[str, str]) -> None:
    page.goto(f"{base}/w08", wait_until="networkidle")
    page.get_by_label("Actor ID").fill(persona["actor_id"])
    page.get_by_label("Password").fill(persona["password"])
    page.get_by_role("button", name="Sign in").click()
    assert page.get_by_role("heading", name="Work queue").is_visible()


def _context(browser: Browser, base: str, persona: dict[str, str]) -> BrowserContext:
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.set_default_timeout(5_000)
    _login(page, base, persona)
    return context


def _brief(page: Page) -> str:
    page.get_by_label("Brief title").fill("Synthetic Playwright workflow brief")
    page.get_by_role("button", name="Create immutable draft").click()
    assert page.get_by_role("heading", name="Role brief history").is_visible()
    brief_id = page.url.rsplit("/", 1)[-1]
    page.get_by_role("button", name="Submit for approval").click()
    assert "submitted" in page.locator("table").inner_text().lower()
    return brief_id


def _observation_form(page: Page, summary: str) -> None:
    for name in (
        "role_execution",
        "decision_making",
        "technical_execution",
        "off_ball_contribution",
        "context_and_risk",
    ):
        page.locator(f'input[name="{name}_rating"]').last.fill("4")
        page.locator(f'input[name="{name}_confidence"]').last.fill("0.8")
        page.locator(f'input[name="{name}_note"]').last.fill(f"Synthetic {name} note")
    page.locator('input[name="overall_confidence"]').last.fill("0.8")
    page.locator('input[name="summary"]').last.fill(summary)
    page.locator('input[name="evidence_reference"]').last.fill("synthetic/local-note-01")
    page.locator('select[name="disagreement"]').last.select_option("yes")
    page.locator('input[name="disagreement_reason"]').last.fill("Synthetic automated disagreement")
    page.locator('input[name="recommended_next_action"]').last.fill("Synthetic local follow-up")


def test_real_browser_synthetic_complete_role_workflow_and_loopback_requests(
    workflow_runtime: tuple[str, object], browser: Browser
) -> None:
    """Exercise the multi-role workflow in Chromium without claiming user participation."""
    base, app = workflow_runtime
    personas = app.state.synthetic_personas  # type: ignore[attr-defined]
    requests: list[str] = []
    analyst = _context(browser, base, personas["analyst"])
    try:
        page = analyst.pages[0]
        page.on("request", lambda request: requests.append(request.url))
        brief_id = _brief(page)
        approver = _context(browser, base, personas["approver"])
        try:
            approve_page = approver.pages[0]
            approve_page.goto(f"{base}/w08/briefs/{brief_id}", wait_until="networkidle")
            approve_page.get_by_role("button", name="Approve brief").click()
            assert "approved" in approve_page.locator("table").inner_text().lower()
        finally:
            approver.close()
        page.goto(f"{base}/w08/briefs/{brief_id}", wait_until="networkidle")
        page.get_by_role("button", name="Create replayable retrieval link").click()
        assert page.get_by_role("heading", name="Exact local replay projection").is_visible()
        page.get_by_label("Shortlist title").fill("Synthetic browser shortlist")
        page.get_by_role("button", name="Create local shortlist").click()
        shortlist_id = page.url.rsplit("/", 1)[-1]
        page.get_by_label("Rationale").fill("Synthetic automated local rationale")
        page.get_by_role("button", name="Add longlist entry").click()
        entry_id = page.url.rsplit("/", 1)[-1]
        stale = analyst.new_page()
        stale.set_default_timeout(5_000)
        stale.goto(f"{base}/w08/entries/{entry_id}", wait_until="networkidle")
        page.locator('select[name="state"]').select_option("scout")
        page.get_by_label("Scout ID (for scout state)").fill(personas["scout"]["actor_id"])
        page.get_by_label("Transition reason").fill("Synthetic browser scout assignment")
        page.get_by_role("button", name="Append immutable revision").click()
        assert "scout" in page.locator("table").first.inner_text().lower()
        stale.locator('select[name="state"]').select_option("scout")
        stale.get_by_label("Scout ID (for scout state)").fill(personas["scout"]["actor_id"])
        stale.get_by_label("Transition reason").fill("Synthetic stale browser assignment")
        stale.get_by_role("button", name="Append immutable revision").click()
        assert stale.get_by_role("heading", name="Winning revision changed").is_visible()
        stale.get_by_role("link", name="Reload winning revision and retry").click()
        assert "scout" in stale.locator("table").first.inner_text().lower()
        stale.close()
        scout = _context(browser, base, personas["scout"])
        try:
            scout_page = scout.pages[0]
            scout_page.goto(f"{base}/w08/entries/{entry_id}", wait_until="networkidle")
            _observation_form(scout_page, "Synthetic browser observation")
            scout_page.get_by_role("button", name="Append observation").click()
            assert "Synthetic browser observation" in scout_page.locator("table").last.inner_text()
            _observation_form(scout_page, "Synthetic browser amended observation")
            scout_page.get_by_role("button", name="Append amendment").click()
            assert (
                "Synthetic browser amended observation"
                in scout_page.locator("table").last.inner_text()
            )
        finally:
            scout.close()
        meeting = _context(browser, base, personas["approver"])
        try:
            meeting_page = meeting.pages[0]
            meeting_page.goto(f"{base}/w08/entries/{entry_id}", wait_until="networkidle")
            meeting_page.locator('select[name="state"]').select_option("hold")
            meeting_page.locator('select[name="hold_reason"]').select_option("awaiting_evidence")
            meeting_page.get_by_label("Transition reason").fill("Synthetic meeting hold")
            meeting_page.get_by_label("Next action").fill("Obtain synthetic local evidence")
            meeting_page.get_by_label("Next-action owner ID").fill(personas["analyst"]["actor_id"])
            meeting_page.get_by_role("button", name="Append immutable revision").click()
            meeting_page.locator('select[name="state"]').select_option("rejected")
            meeting_page.locator('select[name="rejection_reason"]').select_option(
                "insufficient_evidence"
            )
            meeting_page.get_by_label("Transition reason").fill("Synthetic meeting rejection")
            meeting_page.get_by_role("button", name="Append immutable revision").click()
            meeting_text = meeting_page.locator("table").first.inner_text().lower()
            assert "awaiting_evidence" in meeting_text and "insufficient_evidence" in meeting_text
            meeting_page.locator('select[name="state"]').select_option("longlist")
            meeting_page.get_by_label("Transition reason").fill(
                "Synthetic attributable reconsideration"
            )
            meeting_page.get_by_role("button", name="Append immutable revision").click()
            assert (
                "Synthetic attributable reconsideration"
                in meeting_page.locator("table").first.inner_text()
            )
        finally:
            meeting.close()
        page.goto(f"{base}/w08/shortlists/{shortlist_id}", wait_until="networkidle")
        page.locator('input[name="shortlist_id"]').evaluate(
            "node => { node.value = '00000000-0000-4000-8000-000000000000'; }"
        )
        page.get_by_role("button", name="Create verified local pack").click()
        assert page.get_by_role("heading", name="Action unavailable").is_visible()
        assert "requested action is unavailable" in page.locator("main").inner_text().lower()
        page.goto(f"{base}/w08/shortlists/{shortlist_id}", wait_until="networkidle")
        page.get_by_role("button", name="Create verified local pack").click()
        assert page.get_by_role("heading", name="Local evidence pack").is_visible()
        assert "MISSING_EXPERT_RELEVANCE_EVIDENCE" in page.locator("main").inner_text()
        page.get_by_label("Revocation reason").fill("Synthetic browser revocation")
        page.get_by_role("button", name="Revoke local evidence pack").click()
        assert page.get_by_role("heading", name="Local evidence packs").is_visible()
        admin = _context(browser, base, personas["admin"])
        try:
            audit_page = admin.pages[0]
            audit_page.goto(f"{base}/w08/audit", wait_until="networkidle")
            assert audit_page.get_by_role("heading", name="Append-only audit receipts").is_visible()
            assert (
                audit_page.locator("table caption").inner_text()
                == "Material actions retained locally"
            )
        finally:
            admin.close()
        with app.state.engine.begin() as connection:  # type: ignore[attr-defined]
            connection.execute(
                text(
                    "UPDATE local_sessions SET expires_at=:expired "
                    "WHERE actor_id=:actor AND revoked_at IS NULL"
                ),
                {
                    "expired": (datetime.now(UTC) + timedelta(seconds=1)).isoformat(),
                    "actor": personas["analyst"]["actor_id"],
                },
            )
        sleep(1.1)
        assert page.goto(f"{base}/w08/queue").status == 401
        page.goto(f"{base}/w08", wait_until="networkidle")
        _login(page, base, personas["analyst"])
        page.goto(f"{base}/w08/queue", wait_until="networkidle")
        page.get_by_role("button", name="Sign out and revoke session").click()
        assert page.get_by_role("heading", name="Local R1 scouting workflow").is_visible()
        assert page.goto(f"{base}/w08/queue").status == 401
        assert all(url.split("/")[2].split(":")[0] == "127.0.0.1" for url in requests)
    finally:
        analyst.close()


def test_real_browser_role_brief_history_wraps_at_320_without_hiding_history(
    workflow_runtime: tuple[str, object], browser: Browser
) -> None:
    """Keep the fixed limitation and immutable history reachable on a narrow viewport."""
    base, app = workflow_runtime
    page = browser.new_page(viewport={"width": 320, "height": 700})
    page.set_default_timeout(5_000)
    try:
        _login(page, base, app.state.synthetic_personas["analyst"])  # type: ignore[attr-defined]
        _brief(page)
        boundary = page.get_by_text("NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE", exact=False).last
        assert boundary.is_visible()
        assert "resemblance_only" in boundary.inner_text()
        table = page.locator("table")
        assert table.get_by_text("Immutable interpretations and decisions").is_visible()
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
        assert table.evaluate("node => getComputedStyle(node).overflowX") == "auto"
        assert table.evaluate(
            "node => { node.scrollLeft = node.scrollWidth; return node.scrollLeft > 0; }"
        )
    finally:
        page.close()


@pytest.mark.parametrize("viewport", [(1440, 900), (390, 844), (320, 700)])
def test_real_browser_semantics_keyboard_and_responsive_layout(
    workflow_runtime: tuple[str, object], browser: Browser, viewport: tuple[int, int]
) -> None:
    base, app = workflow_runtime
    page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
    page.set_default_timeout(5_000)
    try:
        page.goto(f"{base}/w08", wait_until="networkidle")
        page.keyboard.press("Tab")
        assert page.locator(":focus").get_attribute("class") == "skip"
        assert page.locator(":focus").is_visible()
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main"
        page.keyboard.press("Tab")
        assert (
            page.locator(":focus").evaluate("node => getComputedStyle(node).outlineWidth") != "0px"
        )
        assert page.locator("header").count() == page.locator("nav").count() == 1
        assert page.locator("main").count() == page.locator("footer").count() == 1
        assert page.locator("h1").count() == 1
        assert page.locator("label").count() == 2
        assert page.locator("table caption").count() == 1
        assert page.locator("th[scope]").count() >= 2
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
        _login(page, base, app.state.synthetic_personas["analyst"])  # type: ignore[attr-defined]
        assert page.locator("h1").count() == 1
        assert page.locator("table caption").count() == 2
        assert page.locator("th[scope]").count() >= 6
        page.locator('select[name="responsibility"]').focus()
        assert (
            page.locator(":focus").evaluate("node => getComputedStyle(node).outlineWidth") != "0px"
        )
        page.get_by_role("button", name="Create immutable draft").focus()
        assert (
            page.locator(":focus").evaluate("node => getComputedStyle(node).outlineWidth") != "0px"
        )
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
    finally:
        page.close()

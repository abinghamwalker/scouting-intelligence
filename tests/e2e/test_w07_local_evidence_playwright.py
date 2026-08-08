"""Real-browser acceptance witnesses for the W07 local evidence journey."""

from __future__ import annotations

import socket
import threading
from collections.abc import Iterator
from time import monotonic, sleep

import pytest
import uvicorn
from playwright.sync_api import Browser, Page, sync_playwright

from scouting.web.w07 import create_w07_app

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


@pytest.fixture()
def loopback_url() -> Iterator[str]:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(create_w07_app(), host="127.0.0.1", port=port, log_level="error")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = monotonic() + 10
    while not server.started and monotonic() < deadline:
        sleep(0.01)
    assert server.started, "loopback uvicorn did not start"
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


@pytest.mark.parametrize(
    "viewport",
    [{"width": 1440, "height": 900}, {"width": 390, "height": 844}, {"width": 320, "height": 700}],
)
def test_real_browser_has_no_body_horizontal_overflow(
    loopback_url: str, browser: Browser, viewport: dict[str, int]
) -> None:
    page = browser.new_page(viewport=viewport)
    page.set_default_timeout(3_000)
    try:
        page.goto(f"{loopback_url}/w07", wait_until="networkidle")
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
    finally:
        page.close()


def test_real_browser_exact_activation_journeys_and_local_requests(
    loopback_url: str, browser: Browser
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.set_default_timeout(3_000)
    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url))
    try:
        page.goto(f"{loopback_url}/w07", wait_until="networkidle")
        page.get_by_role("link", name="Search synthetic-development evidence").click()
        page.get_by_role("link", name="Synthetic candidate 02").click()
        page.get_by_role("link", name="Inspect role-aware retrieval").click()
        assert page.get_by_role("heading", name="Role-aware retrieval evidence").is_visible()
        page.get_by_role("link", name="Compare records").first.click()
        assert page.get_by_role(
            "heading", name="Query and candidate evidence contrast"
        ).is_visible()
        page.goto(f"{loopback_url}/w07", wait_until="networkidle")
        page.get_by_role("link", name="Evidence centre").click()
        assert page.get_by_role("heading", name="Evidence and validation centre").is_visible()
        assert all(url.split("/")[2].split(":")[0] == "127.0.0.1" for url in requests)
    finally:
        page.close()


def test_real_browser_keyboard_landmarks_controls_and_distinct_states(
    loopback_url: str, browser: Browser
) -> None:
    page: Page = browser.new_page(viewport={"width": 390, "height": 844})
    page.set_default_timeout(3_000)
    try:
        page.goto(f"{loopback_url}/w07", wait_until="networkidle")
        page.keyboard.press("Tab")
        assert page.locator(":focus").get_attribute("class") == "skip-link"
        assert page.locator(":focus").is_visible()
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main-content"
        page.keyboard.press("Tab")
        assert (
            page.locator(":focus").evaluate("node => getComputedStyle(node).outlineWidth") != "0px"
        )
        assert (
            page.locator("main").count()
            == page.locator("header").count()
            == page.locator("nav").count()
            == page.locator("footer").count()
            == 1
        )
        for route in ("/w07", "/w07/search", "/w07/retrieval", "/w07/evidence"):
            page.goto(f"{loopback_url}{route}", wait_until="networkidle")
            assert page.locator("h1").count() == 1
            assert page.locator("label").count() or route != "/w07/search"
            assert page.locator("caption").count() or route not in {"/w07/search", "/w07/retrieval"}
            assert page.locator("th[scope]").count() or route not in {
                "/w07/search",
                "/w07/retrieval",
            }
            assert page.locator("details summary").count() >= 1
        states = {}
        for state in ("loading", "empty", "unavailable", "error", "no-go"):
            page.goto(f"{loopback_url}/w07/state/{state}", wait_until="networkidle")
            states[state] = page.locator(".state-card").inner_text()
        assert len(set(states.values())) == 5
        assert "no positive evaluation conclusion" in states["no-go"].lower()
        assert "no unsupported result" in states["error"].lower()
    finally:
        page.close()

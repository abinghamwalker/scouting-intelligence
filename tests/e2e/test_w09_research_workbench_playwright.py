"""Real-browser acceptance for the fixture-only W09 research workbench."""

from __future__ import annotations

import importlib
import json
import socket
import sys
import threading
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import monotonic, sleep

import pytest
import uvicorn
from playwright.sync_api import Browser, Page, Route, expect, sync_playwright

from scouting.api.research import ResearchApiRuntime
from scouting.storage.embedded import create_embedded_engine
from scouting.storage.guarded import GuardedStorage
from scouting.storage.research import RESEARCH_REPORT_ROOT_NAME, ResearchExperimentStore
from scouting.web.w09 import create_w09_app

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def fixture_app(tmp_path: Path) -> Iterator[object]:
    """Build explicitly synthetic, temporary authorities for browser tests only."""

    integration_tests = ROOT / "tests/integration"
    sys.path.insert(0, str(integration_tests))
    try:
        helpers = importlib.import_module("test_w09_research_api_integration")
        service, _ = helpers._authority(tmp_path / "fixture-authority")
        dataset = helpers._dataset(service)
        engine = create_embedded_engine(tmp_path / "fixture.sqlite3", allowed_root=tmp_path)
        runtime = ResearchApiRuntime(
            dataset=dataset,
            serving=service,
            store=ResearchExperimentStore(
                engine,
                GuardedStorage({RESEARCH_REPORT_ROOT_NAME: tmp_path / "fixture-reports"}),
            ),
            retained_attribution=helpers._ATTRIBUTION,
            rights_limitations=helpers._RIGHTS_LIMITATIONS,
            utc_clock=lambda: datetime.now(UTC) + timedelta(minutes=1),
        )
        yield create_w09_app(runtime=runtime, serving=service)
        engine.dispose()
    finally:
        sys.path.remove(str(integration_tests))


@pytest.fixture()
def loopback_url(fixture_app: object) -> Iterator[str]:
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
    assert server.started, "loopback W09 uvicorn did not start"
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


def test_real_browser_exemplar_profile_methods_compare_save_report_and_replay(
    loopback_url: str,
    browser: Browser,
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    page.set_default_timeout(5_000)
    try:
        page.goto(loopback_url, wait_until="networkidle")
        assert page.locator("#dataset-state").inner_text() == "Verified local authority"
        assert "3,071,395" in page.locator("#dataset-summary").inner_text()
        assert page.locator("#search-page-state").inner_text() == "1–4 of 4"

        methodology = page.locator("#methodology-details")
        assert methodology.get_attribute("open") is None
        methodology.locator("summary").click()
        assert methodology.get_attribute("open") == ""
        methodology_copy = methodology.inner_text()
        assert "retained event numerator counts per 90 governed minutes" in methodology_copy
        assert "conservative lower bounds" in methodology_copy
        assert "(raw − global median) / global IQR" in methodology_copy
        assert "filters do not refit the scaler" in methodology_copy
        assert "one selected target competition and season" in methodology_copy
        assert "The exemplar may come from another competition" in methodology_copy
        assert "excludes recorded event-9 save-attempt actions" in methodology_copy
        assert "not percentages, probabilities or calibrated match scores" in methodology_copy

        page.get_by_label("Competition").nth(0).select_option(index=2)
        page.get_by_role("button", name="Search players").click()
        expect(page.locator(".search-result")).to_have_count(1)
        page.get_by_label("Competition").nth(0).select_option("")
        page.get_by_role("button", name="Search players").click()
        expect(page.locator(".search-result")).to_have_count(4)

        page.get_by_role("button", name="Use exemplar").first.click()
        page.get_by_label("Retrieval method").select_option("weighted_euclidean")
        page.get_by_role("button", name="Run full-population query").click()
        page.locator(".candidate-card").first.wait_for()
        assert page.locator(".candidate-card").count() == 2
        assert "Weighted Euclidean result" in page.locator("#method-interpretation").inner_text()
        assert "square root of their sum" in page.locator("#method-interpretation").inner_text()
        page.get_by_text("Inspect contributions and contrasts").first.click()
        assert page.locator(".candidate-card table").first.is_visible()
        assert "Scaled contrast" in page.locator(".candidate-card table").first.inner_text()
        assert "Missing active features" not in page.locator(".candidate-card").first.inner_text()

        page.locator(".candidate-select input").nth(0).check()
        page.locator(".candidate-select input").nth(1).check()
        page.get_by_role("button", name="Compare 2 selected").click()
        page.locator(".comparison-card").first.wait_for()
        assert page.locator(".comparison-card").count() == 2

        page.get_by_label("Deterministic report").select_option("json")
        page.get_by_role("button", name="Save exact experiment").click()
        report = page.get_by_role("link", name="Open exact JSON report")
        report.wait_for()
        report_response = page.request.get(f"{loopback_url}{report.get_attribute('href')}")
        assert report_response.ok
        assert report_response.headers["content-type"] == "application/json"
        assert report_response.json()["claim"]["boundary"] == "historical_resemblance_research_only"
        saved_report_href = report.get_attribute("href")
        page.get_by_role("button", name="Save exact experiment").click()
        expect(page.get_by_role("link", name="Open exact JSON report")).to_have_attribute(
            "href", saved_report_href
        )
        expect(page.locator("#experiment-list li")).to_have_count(1)
        page.get_by_role("button", name="Replay exact saved pins").click()
        page.locator('#replay-state[data-state="reproduced"]').wait_for()
        assert "exact saved query" in page.locator("#replay-state").inner_text()

        replay_failures = iter(("result_mismatch", "incompatible_pins"))

        def replay_failure(route: Route) -> None:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "status": next(replay_failures),
                        "receipt_digest": "f" * 64,
                    }
                ),
            )

        page.route("**/api/w09/experiments/*/replay", replay_failure)
        page.get_by_role("button", name="Replay exact saved pins").click()
        page.locator('#replay-state[data-state="result_mismatch"]').wait_for()
        assert "does not match" in page.locator("#replay-state").inner_text()
        page.get_by_role("button", name="Replay exact saved pins").click()
        page.locator('#replay-state[data-state="incompatible_pins"]').wait_for()
        assert "differ from the saved experiment" in page.locator("#replay-state").inner_text()
        page.unroute("**/api/w09/experiments/*/replay", replay_failure)

        def unknown_replay_status(route: Route) -> None:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"status": "future_status", "receipt_digest": "e" * 64}),
            )

        page.route("**/api/w09/experiments/*/replay", unknown_replay_status)
        page.get_by_role("button", name="Replay exact saved pins").click()
        page.locator('#replay-state[data-state="error"]').wait_for()
        assert "unsupported" in page.locator("#replay-state").inner_text()
        assert "undefined" not in page.locator("#replay-state").inner_text()
        page.unroute("**/api/w09/experiments/*/replay", unknown_replay_status)

        page.get_by_label("Deterministic report").select_option("html")
        page.get_by_role("button", name="Save exact experiment").click()
        html_report = page.get_by_role("link", name="Open exact HTML report")
        html_report.wait_for()
        html_response = page.request.get(f"{loopback_url}{html_report.get_attribute('href')}")
        assert html_response.ok
        assert html_response.headers["content-type"] == "text/html; charset=utf-8"
        assert "historical_resemblance_research_only" in html_response.text()

        page.get_by_role("radio", name="Weighted profile").check()
        page.get_by_label("Retrieval method").select_option("weighted_cosine")
        page.locator("#profile-fields input").nth(0).fill("1e-5")
        page.locator("#profile-fields input").nth(1).fill("1e16")
        page.locator("#weight-fields input").nth(0).fill("1e-7")
        page.locator("#weight-fields input").nth(1).fill("1e16")
        page.get_by_label("Minimum evidenced minutes").fill("1e-5")
        with page.expect_response(
            lambda response: (
                response.url.endswith("/api/w09/queries") and response.request.method == "POST"
            )
        ) as response_info:
            page.get_by_role("button", name="Run full-population query").click()
        assert response_info.value.status == 200, response_info.value.text()
        expect(page.locator("#result-digest")).to_have_attribute("data-method", "weighted_cosine")
        assert "Weighted cosine result" in page.locator("#method-interpretation").inner_text()
        assert "signed contribution" in page.locator("#method-interpretation").inner_text()
        assert "distance is 1 plus their sum" in page.locator("#method-interpretation").inner_text()
        assert page.locator(".candidate-card").count() == 3
        assert page.locator("#workbench-status").get_attribute("data-state") == "ready"
    finally:
        page.close()


def test_keyboard_landmarks_narrow_screen_and_local_request_containment(
    loopback_url: str,
    browser: Browser,
) -> None:
    page = browser.new_page(viewport={"width": 320, "height": 760})
    page.set_default_timeout(5_000)
    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url))
    try:
        page.goto(f"{loopback_url}/w09", wait_until="networkidle")
        assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
        page.keyboard.press("Tab")
        assert page.locator(":focus").get_attribute("class") == "skip-link"
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main-content"
        assert page.locator("header").count() == 1
        assert page.locator("nav").count() == 1
        assert page.locator("main").count() == 1
        assert page.locator("footer").count() == 1
        assert page.locator("h1").count() == 1
        assert page.locator("label").count() > 10
        assert page.locator("details summary").count() >= 2
        assert all(url.startswith(loopback_url) for url in requests)
    finally:
        page.close()


def test_distinct_empty_validation_conflict_and_unavailable_states(
    loopback_url: str,
    browser: Browser,
) -> None:
    page: Page = browser.new_page(viewport={"width": 960, "height": 800})
    page.set_default_timeout(5_000)
    page.goto(loopback_url, wait_until="networkidle")
    responses = iter(
        (
            (
                200,
                {
                    "dataset_version": "wyscout-2017-18-v1",
                    "matrix_version": "fixture",
                    "matrix_digest": "0" * 64,
                    "name": "nobody",
                    "position_code": None,
                    "competition_id": None,
                    "offset": 0,
                    "limit": 50,
                    "total_matches": 0,
                    "players": [],
                    "contains_synthetic_rows": False,
                },
            ),
            (422, {"detail": "fixture validation failure"}),
            (409, {"detail": "fixture stale pin conflict"}),
            (503, {"detail": "fixture governed artifact unavailable"}),
        )
    )

    def intercept(route: Route) -> None:
        status_code, payload = next(responses)
        route.fulfill(
            status=status_code,
            content_type="application/json",
            body=json.dumps(payload),
        )

    page.route("**/api/w09/players?*", intercept)
    try:
        expected = ("empty", "validation-error", "conflict", "unavailable")
        for state in expected:
            page.get_by_label("Search eligible historical players").fill("nobody")
            page.get_by_role("button", name="Search players").click()
            page.locator(f'#workbench-status[data-state="{state}"]').wait_for()
        assert (
            "required governed evidence is unavailable"
            in page.locator("#status-message").inner_text()
        )
    finally:
        page.close()

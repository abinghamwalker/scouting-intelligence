"""Fail-closed composition tests for the local W09 research workbench."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import scouting.web.w09 as w09
from scouting.api.research import ResearchApiConflictError
from scouting.modeling.research import ResearchIndexBuildError

_SERVICE_PATH = Path("services/api/w09_main.py")
_TEMPLATE_PATH = Path("apps/web/templates/w09/workbench.html")
_SCRIPT_PATH = Path("apps/web/static/w09/workbench.js")
_SERVICE_SPEC = importlib.util.spec_from_file_location("w09_main_test", _SERVICE_PATH)
assert _SERVICE_SPEC is not None and _SERVICE_SPEC.loader is not None
w09_main = importlib.util.module_from_spec(_SERVICE_SPEC)
_SERVICE_SPEC.loader.exec_module(w09_main)


def _unavailable_client(monkeypatch: pytest.MonkeyPatch, message: str) -> TestClient:
    def ambiguous() -> Path:
        raise ResearchIndexBuildError(message)

    monkeypatch.setattr(w09_main, "discover_feature_matrix_manifest", ambiguous)
    return TestClient(w09_main.create_production_w09_app())


def test_missing_or_ambiguous_production_artifacts_fail_closed_without_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _unavailable_client(
        monkeypatch,
        "exactly one accepted W09 feature manifest is required",
    )

    page = client.get("/", headers={"host": "127.0.0.1"})
    assert page.status_code == 503
    assert "exactly one accepted W09 feature manifest" in page.text
    assert "No synthetic, stale, newest-found, or legacy W07/W08 population" in page.text
    assert client.get("/api/w09/datasets", headers={"host": "127.0.0.1"}).status_code == 404
    assert client.get("/w07", headers={"host": "127.0.0.1"}).status_code == 404
    assert client.get("/w08", headers={"host": "127.0.0.1"}).status_code == 404


def test_incompatible_matrix_or_index_is_an_honest_unavailable_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        w09_main,
        "discover_feature_matrix_manifest",
        lambda: Path("data/manifests/wyscout/v5/research_features/accepted.manifest.json"),
    )

    def incompatible(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise ResearchIndexBuildError("research index is stale or incompatible with the matrix")

    monkeypatch.setattr(w09_main, "load_feature_matrix", incompatible)
    client = TestClient(w09_main.create_production_w09_app())

    page = client.get("/w09", headers={"host": "localhost"})
    assert page.status_code == 503
    assert "stale or incompatible" in page.text
    assert "Run full-population query" not in page.text


def test_runtime_or_store_composition_conflict_is_caught_as_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        w09_main,
        "discover_feature_matrix_manifest",
        lambda: Path("data/manifests/wyscout/v5/research_features/accepted.manifest.json"),
    )

    def composition_conflict(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise ResearchApiConflictError("dataset descriptor conflicts with exact serving pins")

    monkeypatch.setattr(w09_main, "load_feature_matrix", composition_conflict)
    client = TestClient(w09_main.create_production_w09_app())

    page = client.get("/w09", headers={"host": "127.0.0.1"})
    assert page.status_code == 503
    assert "dataset descriptor conflicts" in page.text


def test_loopback_and_response_security_policy_apply_to_failure_surfaces(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _unavailable_client(monkeypatch, "governed artifact root is absent")

    rejected = client.get("/", headers={"host": "research.example"})
    assert rejected.status_code == 400
    accepted = client.get("/", headers={"host": "[::1]:8123"})
    assert accepted.status_code == 503
    assert client.get("/favicon.ico", headers={"host": "127.0.0.1"}).status_code == 204
    assert accepted.headers["cache-control"] == "no-store"
    assert accepted.headers["referrer-policy"] == "no-referrer"
    assert accepted.headers["x-content-type-options"] == "nosniff"
    assert "connect-src 'self'" in accepted.headers["content-security-policy"]
    assert "default-src 'none'" in accepted.headers["content-security-policy"]


def test_factory_requires_exact_runtime_and_serving_pair() -> None:
    with pytest.raises(TypeError, match="supplied together"):
        w09.create_w09_app(runtime=None, serving=object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="trimmed reason"):
        w09.create_w09_app(runtime=None, serving=None, unavailable_reason="  ")


def test_w09_composition_has_no_legacy_provider_or_html_injection_seam() -> None:
    paths = (
        Path("src/scouting/web/w09.py"),
        Path("services/api/w09_main.py"),
        Path("apps/web/static/w09/workbench.js"),
    )
    forbidden_text = (
        "tests/fixtures/w05",
        "runs/w05",
        "synthetic_position_code",
        "SyntheticServingService",
        "w07_core",
        "w07_default_request",
        "load_m0_development_candidates",
        "load_m0_development_queries",
        ".innerHTML",
        "insertAdjacentHTML",
        "document.write",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert not any(value in combined for value in forbidden_text)

    tree = ast.parse(paths[0].read_text(encoding="utf-8"))
    imported = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert "scouting.modeling.research" not in imported
    assert not any(
        marker in module
        for module in imported
        for marker in (
            "scouting.sources",
            "scouting.data_products",
            "scouting.web.w07",
            "scouting.web.w08",
            "scouting.auth",
            "scouting.audit",
            "scouting.workflow",
        )
    )


def test_methodology_copy_is_accessible_and_method_specific() -> None:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    script = _SCRIPT_PATH.read_text(encoding="utf-8")

    assert '<details id="methodology-details">' in template
    assert "How raw values, scaling and distances work" in template
    assert "retained event numerator counts per 90 governed minutes" in template
    assert "conservative lower bounds" in template
    assert "(raw − global median) / global IQR" in template
    assert "A zero global IQR uses a unit scale of 1" in template
    assert "filters do not refit the scaler" in template
    assert "one selected target competition and season" in template
    assert "The exemplar may come from another competition" in template
    assert "excludes recorded event-9 save-attempt actions" in template
    assert "not percentages, probabilities or calibrated match scores" in template
    assert 'id="method-interpretation"' in template

    assert "Weighted Euclidean result" in script
    assert "weight × scaled contrast²" in script
    assert "distance is the square root of their sum" in script
    assert "Weighted cosine result" in script
    assert "each signed contribution is the negative product" in script
    assert "distance is 1 plus their sum" in script

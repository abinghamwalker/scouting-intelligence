"""Focused strict-boundary tests for the provider-neutral W09 research API."""

from __future__ import annotations

import ast
from pathlib import Path
from uuid import UUID

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from scouting.api.research import (
    ResearchApiNotFoundError,
    ResearchPlayerSearchResponse,
    SaveResearchExperimentRequest,
    _raise_http_error,
)
from scouting.serving.research import ResearchServingConflictError, ResearchServingError


def test_save_request_is_strict_and_requires_complete_comparison_reference() -> None:
    base = {
        "experiment_id": UUID("90000000-0000-4000-8000-000000000001"),
        "name": "Historical comparison",
        "result_id": UUID("90000000-0000-4000-8000-000000000002"),
        "result_digest": "1" * 64,
    }

    assert SaveResearchExperimentRequest(**base).report_format == "json"
    with pytest.raises(ValidationError, match="comparison id and digest"):
        SaveResearchExperimentRequest(
            **base,
            comparison_id=UUID("90000000-0000-4000-8000-000000000003"),
        )
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        SaveResearchExperimentRequest(**base, invented_role="scout")
    with pytest.raises(ValidationError):
        SaveResearchExperimentRequest(**(base | {"result_digest": "ABC"}))


def test_player_search_response_cannot_claim_synthetic_population() -> None:
    with pytest.raises(ValidationError):
        ResearchPlayerSearchResponse(
            dataset_version="wyscout-2017-18-v1",
            matrix_version="matrix-v1",
            matrix_digest="2" * 64,
            name=None,
            position_code=None,
            competition_id=None,
            offset=0,
            limit=20,
            total_matches=0,
            players=(),
            contains_synthetic_rows=True,
        )


def test_http_mapping_uses_typed_errors_and_stable_non_disclosing_details() -> None:
    with pytest.raises(HTTPException) as conflict:
        _raise_http_error(ResearchServingConflictError("opaque authority conflict"))
    assert conflict.value.status_code == 409
    assert conflict.value.detail == "research_conflict"

    with pytest.raises(HTTPException) as input_error:
        _raise_http_error(ResearchServingError("contains stale but is an input error"))
    assert input_error.value.status_code == 422
    assert input_error.value.detail == "research_request_rejected"

    secret = "/private/local/report.json"
    with pytest.raises(HTTPException) as missing:
        _raise_http_error(ResearchApiNotFoundError(secret))
    assert missing.value.status_code == 404
    assert missing.value.detail == "research_not_found"
    assert secret not in str(missing.value.detail)


def test_api_imports_only_w09_contract_serving_reporting_and_storage_boundaries() -> None:
    path = Path("src/scouting/api/research.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    called = {
        ast.unparse(node.func).casefold() for node in ast.walk(tree) if isinstance(node, ast.Call)
    }

    assert not any(
        marker in module
        for module in imported
        for marker in (
            "scouting.sources",
            "scouting.adapters",
            "scouting.web",
            "scouting.auth",
            "scouting.audit",
            "scouting.workflow",
            "scouting.retrieval.service",
        )
    )
    assert "artifact discovery" not in source.casefold()
    assert "provider runtime" not in source.casefold()
    assert not any(
        marker in call
        for call in called
        for marker in ("w03", "w05", "w07", "w08", "provider", "legacy")
    )

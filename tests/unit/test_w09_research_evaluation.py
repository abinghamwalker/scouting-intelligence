from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from scouting.contracts.research import canonical_research_digest
from scouting.evaluation.research import (
    DEFAULT_EVALUATION_CONFIG_PATH,
    FrozenQueryCase,
    RankDisplacement,
    ResearchEvaluationError,
    _safe_canonical_json,
)
from scouting.storage.formats import canonical_json_bytes

_SCRIPT_PATH = Path(__file__).parents[2] / "scripts/evaluate_w09_retrieval.py"
_SPEC = importlib.util.spec_from_file_location("evaluate_w09_retrieval_unit", _SCRIPT_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("could not load evaluate_w09_retrieval.py")
_SCRIPT = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _SCRIPT
_SPEC.loader.exec_module(_SCRIPT)
_write_immutable = _SCRIPT._write_immutable


def test_frozen_case_self_digest_rejects_semantic_tampering() -> None:
    suite = cast(dict[str, Any], json.loads(DEFAULT_EVALUATION_CONFIG_PATH.read_bytes()))
    case = cast(dict[str, Any], suite["cases"][0])

    assert (
        FrozenQueryCase.model_validate_json(canonical_json_bytes(case)).case_digest
        == case["case_digest"]
    )
    tampered = {**case, "limit": cast(int, case["limit"]) + 1}
    with pytest.raises(ValidationError, match="case digest"):
        FrozenQueryCase.model_validate_json(canonical_json_bytes(tampered))


def test_rank_displacement_contract_rejects_inconsistent_absolute_value() -> None:
    with pytest.raises(ValidationError, match="absolute rank displacement"):
        RankDisplacement(
            grain_id="retained-grain",
            baseline_rank=1,
            perturbed_rank=4,
            absolute_displacement=2,
        )


def test_safe_suite_reader_requires_canonical_json_and_safe_ancestors(tmp_path: Path) -> None:
    canonical_path = tmp_path / "canonical.json"
    canonical_path.write_bytes(canonical_json_bytes({"suite": "fixture"}))
    assert _safe_canonical_json(canonical_path) == canonical_path.read_bytes()

    noncanonical_path = tmp_path / "noncanonical.json"
    noncanonical_path.write_text('{"suite": "fixture"}\n', encoding="utf-8")
    with pytest.raises(ResearchEvaluationError, match="canonical JSON"):
        _safe_canonical_json(noncanonical_path)

    real = tmp_path / "real"
    real.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(real, target_is_directory=True)
    unsafe_path = linked / "suite.json"
    unsafe_path.write_bytes(canonical_json_bytes({"suite": "fixture"}))
    with pytest.raises(ResearchEvaluationError, match="unsafe ancestor"):
        _safe_canonical_json(unsafe_path)


def test_immutable_evaluation_writer_is_idempotent_private_and_conflict_closed(
    tmp_path: Path,
) -> None:
    payload = canonical_json_bytes({"result": "fixture"})
    output = _write_immutable(tmp_path / "evaluation", "result.json", payload)

    assert output.read_bytes() == payload
    assert output.stat().st_mode & 0o777 == 0o600
    assert _write_immutable(tmp_path / "evaluation", "result.json", payload) == output

    output.write_bytes(canonical_json_bytes({"result": "conflict"}))
    os.chmod(output, 0o600)
    with pytest.raises(ResearchEvaluationError, match="immutable evaluation output conflicts"):
        _write_immutable(tmp_path / "evaluation", "result.json", payload)


def test_frozen_config_is_physically_canonical_and_self_digested() -> None:
    payload = cast(dict[str, Any], json.loads(DEFAULT_EVALUATION_CONFIG_PATH.read_bytes()))

    assert canonical_json_bytes(payload) == DEFAULT_EVALUATION_CONFIG_PATH.read_bytes()
    assert payload["suite_digest"] == canonical_research_digest(
        {key: value for key, value in payload.items() if key != "suite_digest"}
    )

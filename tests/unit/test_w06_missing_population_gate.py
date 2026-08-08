"""Public, temporary-directory checks for the W06 missing-population broker."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scouting.contracts.evaluation import FrozenProtectedPreregistration, _digest
from scouting.evaluation.gate import broker_missing_population_no_go

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/w06-protected-preregistration-v1.json"


def _preregistration() -> FrozenProtectedPreregistration:
    return FrozenProtectedPreregistration.model_validate_json(CONFIG.read_text(encoding="utf-8"))


def _validate_json_payload(payload: object) -> FrozenProtectedPreregistration:
    return FrozenProtectedPreregistration.model_validate_json(json.dumps(payload))


def test_public_missing_population_broker_is_one_use_and_never_constructs_a_run(
    tmp_path: Path,
) -> None:
    preregistration = _preregistration()
    outcome, decision, receipt = broker_missing_population_no_go(
        preregistration,
        caller_preregistration_digest=preregistration.preregistration_digest,
        invocation_id="public-invocation",
        output_directory=tmp_path,
    )
    assert outcome.outcome == "NOT_ACCESSED_MISSING_POPULATION"
    assert outcome.protected_outputs_opened is False
    assert decision.decision == "NO_GO"
    assert decision.bundle is None and decision.run is None
    assert decision.reason_codes == ("MISSING_EXPERT_RELEVANCE_EVIDENCE",)
    assert receipt.gate_digest == decision.gate_digest
    with pytest.raises(FileExistsError, match="one-use"):
        broker_missing_population_no_go(
            preregistration,
            caller_preregistration_digest=preregistration.preregistration_digest,
            invocation_id="different-invocation",
            output_directory=tmp_path,
        )


def test_broker_rejects_digest_substitution_and_partial_output(tmp_path: Path) -> None:
    preregistration = _preregistration()
    with pytest.raises(ValueError, match="caller preregistration digest disagreement"):
        broker_missing_population_no_go(
            preregistration,
            caller_preregistration_digest="0" * 64,
            invocation_id="public-invocation",
            output_directory=tmp_path,
        )
    (tmp_path / "protected-gate-decision.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError, match="partial"):
        broker_missing_population_no_go(
            preregistration,
            caller_preregistration_digest=preregistration.preregistration_digest,
            invocation_id="public-invocation",
            output_directory=tmp_path,
        )


def test_preregistration_rejects_unknown_fields_and_fabricated_evidence() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    payload["unknown"] = True
    with pytest.raises(ValidationError, match="Extra inputs"):
        _validate_json_payload(payload)
    payload.pop("unknown")
    payload["evidence_inventory"]["protected_queries"] = 1
    with pytest.raises(ValidationError, match="Input should be 0"):
        _validate_json_payload(payload)


def test_preregistration_rejects_rehashed_candidate_and_protocol_substitution() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    payload["candidate"]["artifact_id"] = "9a0d43c6-d177-51be-8280-3bf02bedbc98"
    payload["candidate"]["candidate_digest"] = _digest(payload["candidate"], "candidate_digest")
    payload["preregistration_digest"] = _digest(payload, "preregistration_digest")
    with pytest.raises(ValidationError, match="exact W05 candidate identity"):
        _validate_json_payload(payload)
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    payload["protocol"]["baselines"] = ["metadata", "substitute"]
    payload["protocol"]["protocol_digest"] = _digest(payload["protocol"], "protocol_digest")
    payload["preregistration_digest"] = _digest(payload, "preregistration_digest")
    with pytest.raises(ValidationError, match="frozen protocol roster substitution"):
        _validate_json_payload(payload)


def test_preregistration_rejects_exact_resigned_fail_order_and_stop_rule() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    fail_closed_order = payload["protocol"]["fail_closed_order"]
    fail_closed_order[0], fail_closed_order[1] = fail_closed_order[1], fail_closed_order[0]
    payload["protocol"]["stop_rule"] = "Proceed despite missing expert evidence."
    payload["protocol"]["protocol_digest"] = _digest(payload["protocol"], "protocol_digest")
    payload["preregistration_digest"] = _digest(payload, "preregistration_digest")

    assert (
        payload["protocol"]["protocol_digest"]
        == "0315215e86788e773050637a2ac6d6cda70464efbdc4297f28c2cac3b27a3f4e"
    )
    assert (
        payload["preregistration_digest"]
        == "5f71bc77d1ea5430e3663ac5e0f0f84697b07c00776a4f3a1ce678a24cb3dffe"
    )
    with pytest.raises(ValidationError, match="frozen protocol roster substitution"):
        _validate_json_payload(payload)

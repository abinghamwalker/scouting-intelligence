from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast
from uuid import NAMESPACE_URL, uuid5

import pytest

import scouting.evaluation.expert_relevance as evaluation_module
from scouting.contracts.expert_relevance import (
    ExpertGateDecisionKind,
    ProtocolApproval,
)
from scouting.contracts.research import canonical_research_digest
from scouting.evaluation.expert_relevance import (
    CLAIM_FILENAME,
    RECEIPT_FILENAME,
    REPORT_FILENAME,
    RESULT_FILENAME,
    RUN_FILENAME,
    ExpertRelevanceEvaluationError,
    absent_formal_evidence_status,
    load_frozen_presentation,
    load_frozen_protocol,
    load_frozen_query_pack,
    run_one_use_formal_evaluation,
)
from scouting.storage.formats import canonical_json_bytes

_NAMESPACE = uuid5(NAMESPACE_URL, "w10-expert-relevance-integration-fixtures")
_EVALUATED_AT = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
_ARTIFACT_NAMES = (
    CLAIM_FILENAME,
    RUN_FILENAME,
    RESULT_FILENAME,
    REPORT_FILENAME,
    RECEIPT_FILENAME,
)


@pytest.fixture(autouse=True)
def _isolated_formal_evaluation_authority(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        evaluation_module,
        "FORMAL_EVALUATION_AUTHORITY_ROOT",
        tmp_path / "formal-evaluation-authority",
    )


def _approval() -> ProtocolApproval:
    protocol = load_frozen_protocol()
    query_pack = load_frozen_query_pack()
    payload: dict[str, Any] = {
        "approval_id": uuid5(_NAMESPACE, "approval"),
        "protocol_version": protocol.protocol_version,
        "protocol_digest": protocol.protocol_digest,
        "query_pack_version": query_pack.query_pack_version,
        "query_pack_digest": query_pack.query_pack_digest,
        "approved_at": query_pack.built_at + timedelta(minutes=1),
        "approved_by_pseudonym": "FIXTURE-OWNER",
        "confirmation": (
            "I approve this exact protocol and frozen query pack for formal G-RW4 participation."
        ),
    }
    draft = ProtocolApproval.model_construct(**payload, approval_digest="0" * 64)
    payload["approval_digest"] = canonical_research_digest(draft.digest_projection())
    return ProtocolApproval(**payload)


def _run_with_missing_input(output: Path, invocation_number: int = 1):
    return run_one_use_formal_evaluation(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        protected_input_path=output.parent / "protected-input-does-not-exist.json",
        output_directory=output,
        invocation_id=uuid5(_NAMESPACE, f"invocation:{invocation_number}"),
        evaluated_at=_EVALUATED_AT,
    )


def test_absent_evidence_status_is_pure_and_accepts_no_protected_input(
    tmp_path: Path,
) -> None:
    before = tuple(tmp_path.iterdir())
    status = absent_formal_evidence_status(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
    )

    assert status["decision"] == ExpertGateDecisionKind.INSUFFICIENT_EVIDENCE.value
    assert status["decision_reasons"] == ["FORMAL_EVIDENCE_ABSENT"]
    assert status["protected_input_accepted"] is False
    no_approval = absent_formal_evidence_status(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
    )
    assert no_approval["decision_reasons"] == ["FORMAL_APPROVAL_ABSENT"]
    assert tuple(tmp_path.iterdir()) == before


def test_one_use_runner_claims_before_rejecting_input_and_retains_safe_failure(
    tmp_path: Path,
) -> None:
    protected = tmp_path / "protected.json"
    protected.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": 1,
                "evidence_class": "FORMAL_G_RW4",
                "submissions": "fixture-invalid-shape",
            }
        )
    )
    output = tmp_path / "evaluation"
    artifacts = run_one_use_formal_evaluation(
        load_frozen_protocol(),
        load_frozen_query_pack(),
        load_frozen_presentation(),
        _approval(),
        protected_input_path=protected,
        output_directory=output,
        invocation_id=uuid5(_NAMESPACE, "malformed-invocation"),
        evaluated_at=_EVALUATED_AT,
    )

    assert artifacts.result.decision is ExpertGateDecisionKind.FAIL
    assert artifacts.result.decision_reasons == ("INTEGRITY_FAILURE:PROTECTED_INPUT_REJECTED",)
    assert set(path.name for path in output.iterdir()) == set(_ARTIFACT_NAMES)
    for name in _ARTIFACT_NAMES:
        raw = (output / name).read_bytes()
        assert canonical_json_bytes(json.loads(raw)) == raw
        assert (output / name).stat().st_mode & 0o777 == 0o600
    claim = json.loads((output / CLAIM_FILENAME).read_bytes())
    run = json.loads((output / RUN_FILENAME).read_bytes())
    report = (output / REPORT_FILENAME).read_bytes()
    assert claim["protected_input_claimed_before_open"] is True
    assert run["protected_input_file_digest"] is None
    assert b"fixture-invalid-shape" not in report
    assert b'"explanation"' not in report
    assert b'"relevance_rating"' not in report
    assert artifacts.authority_claim_path.exists()
    assert artifacts.authority_receipt_path.exists()
    assert artifacts.authority_claim_path.parent == (tmp_path / "formal-evaluation-authority")

    with pytest.raises(FileExistsError, match="replay or partial output"):
        _run_with_missing_input(output, invocation_number=2)


def test_distinct_output_directory_cannot_reset_authority_consumption(
    tmp_path: Path,
) -> None:
    first = _run_with_missing_input(tmp_path / "first-output", invocation_number=1)

    with pytest.raises(FileExistsError, match="authority was already consumed"):
        _run_with_missing_input(tmp_path / "second-output", invocation_number=2)

    authority_files = tuple(sorted(first.authority_claim_path.parent.iterdir()))
    assert authority_files == (
        first.authority_claim_path,
        first.authority_receipt_path,
    )
    assert not (tmp_path / "second-output" / CLAIM_FILENAME).exists()


def test_partial_output_collision_refuses_before_protected_input_access(
    tmp_path: Path,
) -> None:
    output = tmp_path / "partial"
    output.mkdir()
    collision = output / RESULT_FILENAME
    collision.write_bytes(canonical_json_bytes({"fixture": "pre-existing"}))

    with pytest.raises(FileExistsError, match="replay or partial output"):
        _run_with_missing_input(output)

    assert collision.read_bytes() == canonical_json_bytes({"fixture": "pre-existing"})
    assert not (output / CLAIM_FILENAME).exists()


def test_concurrent_invocations_have_exactly_one_exclusive_claim(tmp_path: Path) -> None:
    output = tmp_path / "concurrent"

    def invoke(number: int) -> str:
        try:
            _run_with_missing_input(output, invocation_number=number)
        except FileExistsError:
            return "rejected"
        return "retained"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = tuple(executor.map(invoke, (1, 2)))

    assert sorted(outcomes) == ["rejected", "retained"]
    assert set(path.name for path in output.iterdir()) == set(_ARTIFACT_NAMES)


def test_output_symlink_is_rejected_without_writing_claim(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(real, target_is_directory=True)

    with pytest.raises(ExpertRelevanceEvaluationError, match="unsafe ancestor"):
        _run_with_missing_input(linked)

    assert tuple(real.iterdir()) == ()


def test_receipt_file_digests_bind_exact_canonical_artifacts(tmp_path: Path) -> None:
    output = tmp_path / "digests"
    _run_with_missing_input(output)
    receipt = cast(dict[str, Any], json.loads((output / RECEIPT_FILENAME).read_bytes()))

    for artifact, field in (
        (CLAIM_FILENAME, "claim_file_digest"),
        (RUN_FILENAME, "run_file_digest"),
        (RESULT_FILENAME, "result_file_digest"),
        (REPORT_FILENAME, "report_file_digest"),
    ):
        assert hashlib.sha256((output / artifact).read_bytes()).hexdigest() == receipt[field]
    assert os.path.samefile(output, output.resolve())

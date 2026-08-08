"""One-use, fail-closed broker for a missing W06 protected population."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from scouting.contracts.evaluation import (
    FrozenProtectedPreregistration,
    GateDecision,
    GateDecisionKind,
    ProtectedAccessOutcome,
    ProtectedAccessOutcomeKind,
    ProtectedGateExecutionReceipt,
    _digest,
)
from scouting.contracts.primitives import ContractModel

ACCESS_OUTCOME_FILENAME = "protected-access-outcome.json"
GATE_DECISION_FILENAME = "protected-gate-decision.json"
EXECUTION_RECEIPT_FILENAME = "protected-execution-receipt.json"


def _contract[ContractT: ContractModel](
    cls: type[ContractT], payload: dict[str, Any], digest_name: str
) -> ContractT:
    draft = cls.model_construct(**payload)
    payload[digest_name] = _digest(draft.model_dump(mode="json"), digest_name)
    return cls(**payload)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


def _write_exclusive(path: Path, value: object) -> str:
    content = _canonical_bytes(value)
    with path.open("xb") as handle:
        handle.write(content)
    return hashlib.sha256(content).hexdigest()


def _output_paths(output_directory: Path) -> tuple[Path, Path, Path]:
    return (
        output_directory / ACCESS_OUTCOME_FILENAME,
        output_directory / GATE_DECISION_FILENAME,
        output_directory / EXECUTION_RECEIPT_FILENAME,
    )


def broker_missing_population_no_go(
    preregistration: FrozenProtectedPreregistration,
    *,
    caller_preregistration_digest: str,
    invocation_id: str,
    output_directory: Path,
) -> tuple[ProtectedAccessOutcome, GateDecision, ProtectedGateExecutionReceipt]:
    """Persist the sole permitted missing-population result exactly once.

    The broker purposefully has no protected-input parameter.  It therefore cannot
    open a protected output or construct an evaluation bundle/run on this route.
    """
    if caller_preregistration_digest != preregistration.preregistration_digest:
        raise ValueError("caller preregistration digest disagreement")
    if preregistration.evidence_inventory.protected_queries != 0:
        raise ValueError("missing-population broker accepts only the frozen zero population")
    output_directory.mkdir(parents=True, exist_ok=True)
    access_path, gate_path, receipt_path = _output_paths(output_directory)
    if any(path.exists() for path in (access_path, gate_path, receipt_path)):
        raise FileExistsError("one-use broker refuses existing or partial output presence")

    outcome = _contract(
        ProtectedAccessOutcome,
        {
            "preregistration_digest": preregistration.preregistration_digest,
            "candidate_digest": preregistration.candidate.candidate_digest,
            "inventory_digest": preregistration.evidence_inventory.inventory_digest,
            "outcome": ProtectedAccessOutcomeKind.NOT_ACCESSED_MISSING_POPULATION,
            "protected_outputs_opened": False,
        },
        "outcome_digest",
    )
    gate = _contract(
        GateDecision,
        {
            "gate_id": f"missing-population-{invocation_id}",
            "decision": GateDecisionKind.NO_GO,
            "protocol": preregistration.protocol,
            "claim_boundary": "resemblance_only",
            "reason_codes": ("MISSING_EXPERT_RELEVANCE_EVIDENCE",),
        },
        "gate_digest",
    )
    access_file_digest = _write_exclusive(access_path, outcome.model_dump(mode="json"))
    gate_file_digest = _write_exclusive(gate_path, gate.model_dump(mode="json"))
    receipt = _contract(
        ProtectedGateExecutionReceipt,
        {
            "invocation_id": invocation_id,
            "preregistration_digest": preregistration.preregistration_digest,
            "candidate_digest": preregistration.candidate.candidate_digest,
            "access_outcome_digest": outcome.outcome_digest,
            "gate_digest": gate.gate_digest,
            "access_outcome_file_digest": access_file_digest,
            "gate_decision_file_digest": gate_file_digest,
        },
        "receipt_digest",
    )
    _write_exclusive(receipt_path, receipt.model_dump(mode="json"))
    return outcome, gate, receipt


def load_preregistration(path: Path) -> FrozenProtectedPreregistration:
    """Load a strict content-addressed preregistration, rejecting unknown fields."""
    return FrozenProtectedPreregistration.model_validate_json(path.read_text(encoding="utf-8"))

# Subagent return

## Task

- task_id: W04-PHASE-VERIFIER-READY-01
- objective: Require complete canonical task-packet structure before a master-owned task may omit a delegated return.

## Files changed

- `scripts/verify_phase.py`
- `tests/unit/test_orchestration_controls.py`
- `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R3.md`

## Summary

- Reused `scripts.verify_task_return.REQUIRED_PACKET_FIELDS` as the single mandatory-field authority; no packet-field contract was duplicated.
- Added fail-closed completeness validation immediately after packet parsing and before ownership or task-identity acceptance. Any absent canonical field rejects the empty-return exemption and reports the exact sorted missing-field set.
- Preserved R1 `READY` eligibility and all dependency, task-state, evidence, declared-check, zero-remote, checkpoint, and closed-tree enforcement.
- Preserved R2 task-ID binding and the missing, malformed, delegated, mixed, borrowed, and invalid-ID rejection behavior.
- Confirmed the corrected current source-authority R1/R2 and source-acquire R1 packets contain every canonical mandatory field and both master task exemptions remain eligible.
- Added an exact regression for the independent review’s matching two-field skeletal mapping and parametrized coverage proving omission of each of the 19 canonical packet fields fails closed.
- Preserved the R1 and R2 handbacks by creating this separate R3 handback.

## Tests run

- command: `uv run python -c "from pathlib import Path; from scripts.control_utils import load_yaml_mapping; from scripts.verify_task_return import REQUIRED_PACKET_FIELDS; paths=['orchestration/task_packets/W04-SOURCE-AUTHORITY-01-R1.yaml','orchestration/task_packets/W04-SOURCE-AUTHORITY-01-R2.yaml','orchestration/task_packets/W04-SOURCE-ACQUIRE-01-R1.yaml']; print([(path, sorted(REQUIRED_PACKET_FIELDS-set(load_yaml_mapping(Path(path))))) for path in paths])"`
  - exit status: 0
  - result: All three exemption-supporting master packets reported an empty missing-field list.
- command: `uv run ruff format --check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  - exit status: 0
  - result: `2 files already formatted`
- command: `uv run ruff check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  - exit status: 0
  - result: `All checks passed!`
- command: `uv run mypy scripts/verify_phase.py`
  - exit status: 0
  - result: `Success: no issues found in 1 source file`
- command: `uv run pytest -q tests/unit/test_orchestration_controls.py`
  - exit status: 0
  - result: `34 passed in 0.50s`

## Artifacts/evidence

- `scripts/verify_phase.py`
- `tests/unit/test_orchestration_controls.py`
- `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R3.md`
- Preserved superseded evidence: `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R1.md`
- Preserved superseded evidence: `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R2.md`

## Risks

- Packet completeness uses the repository’s existing mandatory-key contract and intentionally does not introduce deeper per-field type validation beyond the already required master role and string task-ID controls.
- The master must independently inspect and reproduce R3, obtain fresh independent review, and rerun the complete repository gate.
- No R21 authority, product semantic, architecture, dependency, local-only boundary, registry data, or phase lifecycle data was changed.

## Follow-up items

- Master to inspect the three R3-owned files, reproduce all packet checks, obtain fresh independent review, and rerun the complete repository gate.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; only the three R3 packet-owned paths listed above were edited by this subagent.

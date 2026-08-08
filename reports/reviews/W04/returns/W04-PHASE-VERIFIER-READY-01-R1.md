# Subagent return

## Task

- task_id: W04-PHASE-VERIFIER-READY-01
- objective: Correct the generic phase verifier so a fully evidenced in-progress `READY` phase is eligible for verification while only wholly master-assigned tasks may omit delegated returns.

## Files changed

- `scripts/verify_phase.py`
- `tests/unit/test_orchestration_controls.py`
- `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R1.md`

## Summary

- Added `READY` to the existing verifier-eligible states without changing dependency, task-state, evidence, declared-check, zero-remote, checkpoint, or closed-tree enforcement.
- Added a fail-closed packet-derived exemption for an empty task return list. The exemption succeeds only when the task references at least one packet, every path is a string, every packet exists and parses as a mapping, and every packet has the exact `assigned_role: master` value.
- Preserved mandatory non-empty reviews and packet evidence for every task and preserved retained-file checks whenever a return list is non-empty.
- Added unit coverage for the exact eligible-state set, wholly master-assigned empty returns, delegated empty-return rejection, missing-packet rejection, and malformed-packet rejection.

## Tests run

- command: `uv run ruff format --check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  - exit status: 1
  - result: Initial check correctly reported one formatter-only string-layout difference in the new test.
- command: `uv run ruff format --check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  - exit status: 0
  - result: `2 files already formatted` after the bounded formatting correction.
- command: `uv run ruff check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  - exit status: 0
  - result: `All checks passed!`
- command: `uv run mypy scripts/verify_phase.py`
  - exit status: 0
  - result: `Success: no issues found in 1 source file`
- command: `uv run pytest -q tests/unit/test_orchestration_controls.py`
  - exit status: 0
  - result: `11 passed in 0.46s`

## Artifacts/evidence

- `scripts/verify_phase.py`
- `tests/unit/test_orchestration_controls.py`
- `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R1.md`

## Risks

- The master must still update W04 lifecycle records, reviews, evidence, and declared checks truthfully before the complete phase verifier can pass; this correction does not waive any of those gates.
- No R21 authority, product semantic, architecture, dependency, local-only, or phase-registry data was changed.

## Follow-up items

- Master to inspect the three owned files, reproduce the bounded checks, obtain independent review, and rerun the complete repository gate.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; only the three packet-owned paths listed above were edited.

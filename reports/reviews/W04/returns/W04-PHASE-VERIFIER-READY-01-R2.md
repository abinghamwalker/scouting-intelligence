# Subagent return

## Task

- task_id: W04-PHASE-VERIFIER-READY-01
- objective: Bind the master-owned empty-return exemption to the exact registry task ID so an unrelated master packet cannot be borrowed as exemption evidence.

## Files changed

- `scripts/verify_phase.py`
- `tests/unit/test_orchestration_controls.py`
- `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R2.md`

## Summary

- Preserved the R1 `READY` eligibility correction and every existing phase, dependency, task-state, evidence, declared-check, zero-remote, checkpoint, and closed-tree gate.
- Extended the empty-return exemption to require a non-empty string registry task ID and require every referenced packet to contain a string `task_id` exactly equal to that registry task ID, in addition to existing existence, parse, and exact `assigned_role: master` requirements.
- Preserved positive exemption behavior for both current master-owned tasks: `W04-SOURCE-AUTHORITY-01` and `W04-SOURCE-ACQUIRE-01`.
- Added fail-closed coverage for an unrelated borrowed master packet, non-string registry task ID, missing packet task ID, mixed master/delegated packet ownership, missing packet, malformed packet, and delegated packet.
- Preserved the R1 handback byte-for-byte by creating a separate R2 handback.

## Tests run

- command: `uv run ruff format --check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  - exit status: 1
  - result: Initial R2 check reported one formatter-only parenthesised string-layout difference in the new test.
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
  - result: `14 passed in 0.49s`

## Artifacts/evidence

- `scripts/verify_phase.py`
- `tests/unit/test_orchestration_controls.py`
- `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R2.md`
- Preserved superseded evidence: `reports/reviews/W04/returns/W04-PHASE-VERIFIER-READY-01-R1.md`

## Risks

- The master must still independently verify and review this correction and truthfully complete the W04 lifecycle, review, evidence, and declared-check records before the complete phase verifier can pass.
- No R21 authority, product semantic, architecture, dependency, local-only boundary, registry data, or phase lifecycle data was changed.

## Follow-up items

- Master to inspect the three R2-owned files, reproduce the exact checks, obtain independent review, and rerun the complete repository gate.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; only the three R2 packet-owned paths listed above were edited.

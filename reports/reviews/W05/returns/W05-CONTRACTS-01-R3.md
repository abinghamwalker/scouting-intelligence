# Subagent return

## Task

- task_id: W05-CONTRACTS-01
- objective: Convergence-narrowed additive W05 contract correction.

## Files changed

- src/scouting/contracts/m0.py
- src/scouting/contracts/__init__.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-01-R3.md

## Summary

- Implemented canonical negative-zero rejection, taxonomy digest fields and self-verification, taxonomy digest pins, and stricter artifact array-role/shape requirements including index UUID-byte rows and weighted-family arrays.
- Updated focused fixtures and retained passing contract checks.
- This return is intentionally incomplete: the mandatory R3 typed resolved-query projection, scored-candidate total-order projection, per-candidate dimension-state/explanation alignment, and exact W04 descriptor derivation are not implemented. Do not accept this packet as complete.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/m0.py src/scouting/contracts/__init__.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/contracts/m0.py src/scouting/contracts/__init__.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/m0.py src/scouting/contracts/__init__.py`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py`
  - exit status: 0
  - result: 49 passed in 0.14s.
- command: `uv run lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken.

## Artifacts/evidence

- src/scouting/contracts/m0.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-01-R3.md

## Risks

- High: R3 remains incomplete against its packet requirements. Result/request identity, candidate-specific ordering/state, explanation equality, exact W04 descriptor derivation, and several adversarial probes remain insufficient.

## Follow-up items

- Rework R3 before review; implement every omitted mandatory projection and adversarial test listed above.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

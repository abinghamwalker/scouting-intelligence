# Subagent return

## Task

- task_id: W05-CONTRACTS-QUERY-02
- objective: Add the independent resolved-query identity pin and reject same-ID semantic substitutions after attacker-controlled digest recomputation.

## Files changed

- src/scouting/contracts/m0.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-QUERY-02-R2.md

## Summary

- Added `expected_resolved_query_digest` beside the complete typed resolved query in `PinnedM0ServingRequest`.
- Required the supplied independent pin to exactly equal the already self-verified nested query digest; the field is neither derived nor overwritten during validation.
- Updated focused fixtures and retained all R1 request-overlap checks by explicitly updating the independent pin only in the existing intentional trace-drift fixture.
- Added a strict public-model attack that substitutes responsibilities and matching weights under the same identity and pins, recomputes nested and result digests, leaves the expected pin unchanged, and fails on the independent digest mismatch.

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
  - result: 58 passed in 0.15s.
- command: `uv run lint-imports`
  - exit status: 1
  - result: sandbox denied access to `/Users/adrian/.cache/uv/sdists-v9/.git` before import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-query-02-r2-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken (40 files, 79 dependencies).

## Artifacts/evidence

- src/scouting/contracts/m0.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-QUERY-02-R2.md

## Risks

- The exact import-lint command remains blocked only by the pre-existing unreadable shared uv cache. Isolated-cache import validation passed.
- Candidate-specific evidence, W04 descriptor/array semantics, and explanation equality remain intentionally out of scope.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

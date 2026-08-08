# Subagent return

## Task

- task_id: W05-CONTRACTS-QUERY-02
- objective: Implement self-verifying resolved-query and scored-candidate identity and deterministic ordering projections.

## Files changed

- src/scouting/contracts/m0.py
- src/scouting/contracts/__init__.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-QUERY-02-R1.md

## Summary

- Added a typed, self-verifying `M0ResolvedQuery` with ordered responsibility weights, hard constraints, exemplar/query player fields, taxonomy pins, request overlap checks, and canonical SHA-256 wire digest validation.
- Replaced the opaque pinned query digest with the complete resolved-query model and retained independently verified ordered exclusions.
- Added `M0ScoredCandidate`, exact result/candidate identity and feature-vector cardinality validation, non-negative canonical distance validation, and ascending distance then UUID-byte total-order validation.
- Bound request/result tenant, trace, brief, cutoff, and claim-boundary projections; result digests include both the resolved query and scored candidates through the complete wrapper wire projection.
- Added direct re-digested drift and inverse-equal-UUID-tie adversarial tests plus resolved-query duplicate/overlap coverage.

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
  - result: 57 passed in 0.19s.
- command: `uv run lint-imports`
  - exit status: 1
  - result: sandbox denied access to `/Users/adrian/.cache/uv/sdists-v9/.git` before project import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-query-02-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken (40 files, 79 dependencies).

## Artifacts/evidence

- src/scouting/contracts/m0.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-QUERY-02-R1.md

## Risks

- The exact `uv run lint-imports` command remains blocked only by the pre-existing unreadable shared uv cache path. The isolated local cache verification passed; master reproduction may require the same cache isolation.
- Candidate-specific dimension evidence and explanation equality remain intentionally out of scope for W05-CONTRACTS-TRUTH-03.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

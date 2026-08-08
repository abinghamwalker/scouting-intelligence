# Subagent return

## Task

- task_id: W05-CONTRACTS-TRUTH-03
- objective: Close candidate-specific truth, scored-explanation equality, taxonomy identity, W04 authority identity, and family-array contract gaps.

## Files changed

- src/scouting/contracts/m0.py
- src/scouting/contracts/__init__.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-TRUTH-03-R1.md

## Summary

- Replaced global dimension state with `M0CandidateDimensionEvidence`, which binds player/rank and all six enum-ordered states one-to-one to retrieval and scored candidates. Absence, canonical ZERO, DATA_CONFIDENCE, W04 role-fit, and permanently unavailable dimensions now fail closed at the candidate level.
- Bound every explanation exactly to artifact feature order and its scored candidate’s query values, candidate values, and contributions.
- Added contextual taxonomy digest pins and canonical taxonomy ordering checks, including same-ID semantic substitution rejection.
- Corrected W04 candidate and decision registry identities, required the frozen mechanical four-feature descriptor digest, and exposed the pure descriptor derivation helper without modifying W04 authority bytes.
- Made per-family descriptor role ordering, dtypes, feature/candidate axes, PCA component/variance/index dimensions, and UUID byte rows executable.
- Added adversarial tests for re-signed explanation drift, candidate-state drift, negative zero, W04 descriptor derivation/identity/matrix mismatch, family reorder/PCA topology, and taxonomy/membership substitutions.

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
  - result: 63 passed in 0.17s.
- command: `uv run lint-imports`
  - exit status: 1
  - result: sandbox denied access to `/Users/adrian/.cache/uv/sdists-v9/.git` before import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-truth-03-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken (40 files, 79 dependencies).

## Artifacts/evidence

- src/scouting/contracts/m0.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-TRUTH-03-R1.md

## Risks

- The exact import-lint command remains blocked only by the pre-existing unreadable shared uv cache; the isolated-cache equivalent passed.
- No loader, fitting, scoring, serving, W06, config, or authority-byte work was introduced.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

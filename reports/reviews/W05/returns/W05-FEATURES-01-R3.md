# Subagent return

## Task

- task_id: W05-FEATURES-01
- objective: Add the bounded strict JSON scalar check for the accepted W04 Gold row count.

## Files changed

- src/scouting/features/registry.py
- tests/unit/test_w05_features.py
- reports/reviews/W05/returns/W05-FEATURES-01-R3.md

## Summary

- Before the generic accepted W04 projection comparison, `gold_row_count` now requires a non-boolean Python `int` exactly equal to `1`.
- Added direct regressions proving JSON-equivalent `true`, `1.0`, `false`, `0`, and `2` reject with the row-count type/value reason, while integer `1` continues to materialize the exact accepted `(2.0, 2.0, 1.0, 2.0)` vector.
- No registry, fixture, digest, accepted W04 identity, lineage, claim, formula, count-vector, or other source surface changed.

## Tests run

- command: `UV_CACHE_DIR=/tmp/w05-features-01-r3-uv-cache uv run --no-sync ruff format --check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r3-uv-cache uv run --no-sync ruff check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r3-uv-cache uv run --no-sync mypy src/scouting/features`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r3-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: 0
  - result: 193 passed in 9.64s.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r3-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken; 42 files and 81 dependencies analyzed.
- command: `UV_CACHE_DIR=/tmp/w05-features-01-r3-uv-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 checks passed.

## Artifacts/evidence

- direct row-count regression: `tests/unit/test_w05_features.py::test_w04_gold_row_count_requires_non_boolean_integer_one`
- accepted integer regression: `tests/unit/test_w05_features.py::test_w04_gold_row_count_integer_one_retains_accepted_result`

## Risks

- The known shared uv-cache permission issue was avoided with the packet-authorized isolated existing cache; no dependency resolution or lock change occurred.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

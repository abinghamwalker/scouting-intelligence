# Subagent return

## Task

- task_id: W05-FEATURES-SECURITY-02-R1
- objective: Replace the five terminal feature-loader runtime assertions with explicit fail-closed validation that remains active under optimized Python.

## Files changed

- src/scouting/features/registry.py
- tests/unit/test_w05_features.py
- reports/reviews/W05/returns/W05-FEATURES-SECURITY-02-R1.md

## Summary

- Replaced exactly five production `assert` statements with deterministic `FeatureRegistryError` validation for absent synthetic metadata controls, missing observed numeric values, absent W04 authority, and non-mapping W04 dependencies.
- Added focused regression coverage for every replaced terminal gate and an AST assertion that the production module contains no `Assert` node.
- Preserved accepted positive W04 output and frozen registry/fixture bytes. `rg` found no remaining `assert` token in `src/scouting/features/registry.py`.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync ruff format --check src/scouting/features/registry.py tests/unit/test_w05_features.py`
  - exit status: 0
  - result: 2 files already formatted
- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync ruff check src/scouting/features/registry.py tests/unit/test_w05_features.py`
  - exit status: 0
  - result: all checks passed
- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync mypy src/scouting/features/registry.py`
  - exit status: 0
  - result: Success: no issues found in 1 source file
- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync bandit -q -r src/scouting/features/registry.py`
  - exit status: 0
  - result: zero findings (quiet output)
- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/unit/test_w05_m0_models.py tests/integration/test_w05_m0_serving.py`
  - exit status: 0
  - result: 64 passed in 1.23s
- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 kept, 0 broken
- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 checks passed
- command: `UV_CACHE_DIR=/private/tmp/w05-feature-security-cache uv run --no-sync python -O -c "... materialize_w04_real_row(malformed_dependencies, registry)" 2>&1 | rg 'W04 dependency entries must be objects'`
  - exit status: 0
  - result: optimized Python emitted `FeatureRegistryError: W04 dependency entries must be objects`; no repository write occurred.

## Artifacts/evidence

- `reports/reviews/W05/returns/W05-FEATURES-SECURITY-02-R1.md`
- Registry physical SHA-256 unchanged: `8616e5b14540a5666097fd06d3ec4f98ea56ba2a706601a99f462c3c5badfb1a`
- Fixture physical SHA-256 unchanged: `25b42be0f038265fdc5480c15689598c7d83e5b16463f35292634ee6beb41c02`
- Accepted W04 integer-one output remains `(2.0, 2.0, 1.0, 2.0)` under focused tests.

## Risks

- None identified within this mechanical validation-only scope. The new explicit errors cover states that are normally prevented by prior loader validation as well as internal tampering paths.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

# Subagent return

## Task

- task_id: W05-CONTRACTS-TRUTH-03-R2
- objective: Close the remaining M0 state-truth, W04 family-compatibility, and fitting-population physical-dimension contract gaps.

## Files changed

- src/scouting/contracts/m0.py
- src/scouting/contracts/__init__.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-TRUTH-03-R2.md

## Summary

- Bound each candidate-specific state reason tuple exactly to its corresponding legacy `EvidenceDimension`; MEASURED now requires a strictly positive legacy score, while ZERO requires canonical `+0.0` and absence states remain zero-confidence, non-ranking sentinels.
- Made DATA_CONFIDENCE state derivation authoritative: a canonical zero confidence score maps only to ZERO, a nonzero score maps only to MEASURED, reasons must equal the legacy confidence projection, and it never contributes to ranking.
- Restricted W04 governed manifests to raw Euclidean control, robust-scaled cosine, weighted cosine, and PCA; synthetic-development manifests still admit every M0 family.
- Corrected physical descriptor dimensions: FEATURE_MATRIX rows bind fitting population count; index vectors and player IDs bind candidate-universe count; PCA components cannot exceed either fitting rows or feature columns.
- Added re-digested adversarial coverage for score/reason relabelling, zero DATA_CONFIDENCE state derivation, all six W04 family outcomes, distinct fitting/candidate counts, and PCA capacity overflows by fitting rows and feature columns.

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
- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: 0
  - result: 216 passed in 9.54s.
- command: `uv run lint-imports`
  - exit status: 1
  - result: sandbox denied access to the pre-existing shared uv cache path `/Users/adrian/.cache/uv/sdists-v9/.git` before import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-truth-03-r2-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken (40 files, 79 dependencies).
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all local-only boundary checks passed.

## Risks

- The exact import-lint command remains blocked solely by the unreadable shared uv cache; the isolated-cache equivalent completed successfully.
- No fitting implementation, scoring implementation, serving, W04 authority bytes, config, or dependency work was changed.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

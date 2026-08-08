# Subagent return

## Task

- task_id: W06-EVAL-VALUE-IDENTITY-03-R2
- objective: Close only the computed-Spearman completeness defect while preserving every accepted metric, identity, unavailable shape, gate and population behavior.

## Files changed

- src/scouting/contracts/evaluation.py
- tests/contracts/test_w06_evaluation_contracts.py
- reports/reviews/W06/returns/W06-EVAL-VALUE-IDENTITY-03-R2.md

## Summary

- `RankComparisonResult.valid` now rejects `spearman is not None` when the top-k set-metric quartet is absent, with `computed Spearman requires top-k set metrics`.
- The check runs after the existing all-present/all-absent quartet invariant. It therefore preserves both accepted unavailable forms: `spearman=None` with present set metrics and an insufficiency reason, and `spearman=None` with absent set metrics and a candidate-universe reason.
- The exact previously accepted normal-constructor preimage is pinned at `54cb89310bf9d6feaa7d15cc608f6262adc947f762ddb23d49cfbffe21322231` and now rejects.
- No digest field, formula, core implementation, gate/population relation, export, unit test, or fixture was changed.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r2-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: `11 passed in 0.16s`.
- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r2-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-value-identity-r2-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r2-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-value-identity-r2-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in 3 source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r2-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken.

## Artifacts/evidence

- Exact incomplete-computed witness `54cb89310bf9d6feaa7d15cc608f6262adc947f762ddb23d49cfbffe21322231`: rejected.
- Accepted insufficient-correlation comparison identity remains `5febc6782ae9e260f943e22f682ed9e32947bc3f14f1e15956e8606b5d9d786c` with set metrics present.
- Existing stable pair identity `78250572322fbb52efdae3c2bf4a9214d4124f7b766c0a325aff98a9675ca515`, agreement identity `d20633a5ce1bd3377fec6109a2d09111d8d1e36c2d6a11f8ab9af2a262fbf1e4`, directly persisted metric identity `f021adec1d57a5f54eec235273a66ef6a0a6665599c56cc7843169f0b0cb562e`, and interval identity `79322b611e83d790af4052a63225d0cbe82c878d04c1ffda07e7fbef7ac1003a` all remain pinned and green.
- Existing gate-population, arithmetic, lineage, child-uniqueness and public-fixture regressions all remain green.

## Risks

- none within the bounded correction. Public identities remain implementation evidence only and make no protected or prospective claim.

## Follow-up items

- none.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider access: confirmed.
- no fixture changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-04-R6
- objective: Consolidate ranking metric and bootstrap calculation values, statuses, identities and percentile resampling into one dependency-safe pure authority.

## Files changed

- src/scouting/contracts/evaluation_calculations.py
- src/scouting/contracts/evaluation.py
- src/scouting/evaluation/core.py
- tests/unit/test_w06_evaluation_metrics.py
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-04-R6.md

## Summary

- Added `contracts.evaluation_calculations`, a stdlib-only primitive calculation authority. It canonicalizes numeric score representations, owns ranking-metric values/statuses/sufficient statistics and bootstrap input/resample/percentile identities.
- `core.evaluate_ranking`, `core.bootstrap_interval`, and the persisted-row `derive_ranking_metric_children` are adapters over that one calculation. The unused core comparison helpers were removed; `derive_rank_comparison` remains the sole comparison authority.
- Added a direct cross-surface regression covering all four metrics, integer/float score normalization, aggregate/interval identity parity, and undeclared-k rejection.

## One-core call-path matrix

| Surface | Adapter | Only metric/bootstrap formula authority |
| --- | --- | --- |
| General per-row evaluation | `core.evaluate_ranking` | `evaluation_calculations.derive_ranking_metric_children` |
| General aggregate/bootstrap | `core.bootstrap_interval` | `evaluation_calculations.derive_ranking_metric_children` |
| Robustness production | `evaluation.derive_ranking_metric_children` | `evaluation_calculations.derive_ranking_metric_children` |
| Stress/control validation | `evaluation.derive_ranking_metric_children` | `evaluation_calculations.derive_ranking_metric_children` |

## Boundary outcomes

- Direct parity regression: all four supported metrics, partial relevance, integer/float scores, seed/resample identity and interval bounds match the shared calculation; undeclared `k=999` rejects at the shared boundary.
- Three literal parent witnesses retained by the focused normal-construction robustness closures: `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb`, `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815`, and `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404`; re-signed substituted children reject.

## Tests run

- `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: 19 passed.
- `uv run --no-sync ruff check src/scouting/contracts/evaluation_calculations.py src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: all checks passed.
- `uv run --no-sync mypy src/scouting/contracts/evaluation_calculations.py src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: success; no issues in 5 source files.
- `uv run --no-sync lint-imports`
  - exit status: 0
  - result: 54 files / 109 dependencies; 3 contract dependencies kept, 0 broken.
- `shasum -a 256 tests/fixtures/w06/public-evaluation-v1.json tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: evaluation `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`; robustness `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.
- `test -s reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-04-R6.md`
  - exit status: 0
  - result: pass.

## Risks

- remaining P0/P1 risk: none identified in the scoped implementation; independent review remains required.

## Follow-up items

- none

## Scope confirmation

- implementation-only/no-fabricated-expert boundary: confirmed.
- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected outputs, external access, model tuning, orchestration edits, or edits outside `allowed_paths`: confirmed.

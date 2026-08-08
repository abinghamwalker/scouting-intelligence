# Subagent return

## Task

- task_id: W06-EVAL-VALUE-IDENTITY-03-R1
- objective: Complete the final W06 value/identity convergence with exact metric semantics, one persisted result implementation, input-bound comparison/pair/agreement identities, and fail-closed run lineage.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/contracts/__init__.py
- src/scouting/evaluation/__init__.py
- src/scouting/evaluation/core.py
- tests/contracts/test_w06_evaluation_contracts.py
- tests/unit/test_w06_evaluation_metrics.py
- reports/reviews/W06/returns/W06-EVAL-VALUE-IDENTITY-03-R1.md

## Summary

- Complete judged rankings compute `Precision@k = eligible_gain_in_top_k / k`, including `0/k`; `Recall@k = eligible_gain_in_top_k / eligible_gain_in_universe` and alone becomes unavailable when that denominator is zero. Partial labels contribute `partial_gain` to NDCG and contribute to P/R only when the frozen protocol enables it. `UNJUDGED` and `ABSTAIN` make the ranking metrics unavailable.
- Core ranking, pair, agreement, and bootstrap execution now emits the immutable persisted `MetricResult` and `BootstrapInterval` contracts directly. The parallel `EvaluationValue` implementation was removed. `bootstrap_interval` returns its aggregate `MetricResult` and linked `BootstrapInterval`, so no protocol/input lineage is discarded during persistence.
- `MetricResult.result_digest` binds every persisted field other than itself: metric, `k`, protocol digest, evaluated-query digest, ordered-input digest, value, numerator, denominator, status, and reason. `BootstrapInterval.interval_digest` similarly binds linked metric-result digest, protocol, evaluated population, input lineage, point value, resample identity/settings, bounds, status, and reason. `EvaluationRun` checks result and interval protocol/population lineage and requires interval input lineage to equal its linked result.
- `RankComparisonResult` is a persisted contract whose digest binds protocol, population, `k`, separate ordered left/right ranking input digests, Spearman, overlap/Jaccard/churn, canonical disagreements, and reason. Pair metric input lineage binds each governed preference/reviewer digest, prediction state, and predicted candidate; agreement lineage binds canonical reviewer/evidence orientation. Both pair and agreement evidence must match the protocol rubric.
- Computed metrics and intervals forbid unavailable reasons. Computed metric values retain exact non-negative sufficient statistics and `[0,1]` bounds; computed intervals retain `[0,1]` bounds containing the point. Rank comparison enforces Spearman in `[-1,1]`, `overlap_count <= k`, `overlap_rate = overlap_count/k`, `churn = 1-overlap_rate`, `Jaccard = overlap_count/(2k-overlap_count)`, and exactly `2(k-overlap_count)` canonical disagreement candidates whenever set metrics are present. Unsupported protected-bootstrap primary metrics reject. Slice/run child IDs, digests, and semantic keys remain canonical and unique without weakening the accepted gate-population checks.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: `11 passed in 0.16s`.
- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r1-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-value-identity-r1-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: all checks passed, including literal contract-export coverage.
- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r1-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-value-identity-r1-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in 3 source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-value-identity-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 kept contracts, 0 broken.

## Artifacts/evidence

- Zero-positive ranking: `Precision@1 = 0/1 = 0.0`; `Recall@1` is unavailable with `no_eligible_relevance_denominator`.
- Missing pair prediction: unavailable with `missing_pair_prediction`; correct and wrong predictions have distinct result digests.
- Correct pair identity: `78250572322fbb52efdae3c2bf4a9214d4124f7b766c0a325aff98a9675ca515`.
- Orientation-normalized agreement identity: `d20633a5ce1bd3377fec6109a2d09111d8d1e36c2d6a11f8ab9af2a262fbf1e4`.
- Insufficient-Spearman comparison identity: `5febc6782ae9e260f943e22f682ed9e32947bc3f14f1e15956e8606b5d9d786c`; changing an otherwise metric-equivalent left ranking changes the digest because `left_input_digest`/`right_input_digest` are persisted.
- Core-produced directly persisted metric identity: `f021adec1d57a5f54eec235273a66ef6a0a6665599c56cc7843169f0b0cb562e`; linked interval identity: `79322b611e83d790af4052a63225d0cbe82c878d04c1ffda07e7fbef7ac1003a`. `EvaluationRun` retains both exact digests.
- Pair rubric substitution and agreement rubric substitution reject with protocol-rubric errors. Negative statistics, out-of-unit interval bounds, unsupported primary capability, duplicate slice rows, and duplicate failure rows also reject.
- The reproduced impossible constructors now reject: `spearman=2.0` with `Spearman correlation must be within [-1, 1]`; `overlap_count=2` at `k=1` with `rank comparison overlap cannot exceed k`; a computed metric with `reason=unsupported` with `computed metrics cannot retain an unavailable reason`. The equivalent computed-interval reason constructor also rejects.
- `tests/fixtures/w06/public-evaluation-v1.json` was read only; its implementation-only authority notice and pinned SHA-256 assertion remain unchanged.

## Risks

- Protected/prospective execution must still independently construct the governed input roster and recompute metric/resample inputs; no public identity predicts a protected outcome.
- Float arithmetic is deterministic for the frozen ordered inputs and implementation, but cross-runtime claims still require the persisted protocol and input digests to match exactly.
- No protected evidence, result, threshold, positive claim, provider access, or external access was used.

## Follow-up items

- none.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no fixture changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

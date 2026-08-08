# Subagent return

## Task

- task_id: `W06-EVAL-CORE-REVIEW-01` revision `R2`
- objective: Freshly determine whether every R1 protected-binding, aggregate, metric, comparison, and interval defect closed, reporting only remaining effects on values, partitions, leakage, and claims.

## Files changed

- `reports/reviews/W06/evaluation-core-independent-review-R2.md`
- `reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R2.md`

## Summary

- Verdict: **RETURN FOR REWORK**; exact remaining inventory is **1 P0, 4 P1, 1 P2**.
- W06-EC-R1-01 — **OPEN / P0**: retained constructor chain is FIT non-one-use access → empty `PROTECTED_TEST` run → mismatched-protocol `ACCEPT_CLAIM`, all validating normally. Fixture relevance rejection and bundle roots are partial closures only.
- W06-EC-R1-02 — **OPEN / P1**: retained aggregate accepts relevance `(eone,eone,etwo)`, reversed same-ID pairs, duplicate hard negatives, and cross-candidate adjudication; reordering the same relevance multiset produces another valid, different bundle digest.
- W06-EC-R1-03 — **OPEN / P1**: with one relevant, one partial, `k=2`, gain `0.5`, and partial excluded from P/R, `captured=1.5`, denominator `=1.0`, and reported recall `=1.5`; non-finite scores also make accepted results order-dependent.
- W06-EC-R1-04 — **OPEN / P1**: `left=(a,x)`, `right=(a,y)`, `k=1` has actual overlap `1` and churn `0`, but reports overlap `0`, churn `1`, and disagreement `(a)`; pair/agreement identity remains unbound.
- W06-EC-R1-05 — **OPEN / P1**: `MetricResult(value=2.0,numerator=1,denominator=2)` and computed interval `[1.0,0.0]` with method `anything` validate; the improved core bootstrap digest is not carried into linked interval/run/gate validation.
- Tests — **P2**: four tests pass but do not exercise the surviving cases. Public fixture SHA-256 is `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6` (510 bytes); its test does not assert identity or execute it through the new metric path.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 2
  - result: Environment-only failure before collection because the sandbox denied the global uv cache path `/Users/adrian/.cache/uv/sdists-v9/.git`.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: `4 passed in 0.36s`.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-ruff uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: All checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-mypy uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: Success; no issues in 3 source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken.
- command: `test -s reports/reviews/W06/evaluation-core-independent-review-R2.md`
  - exit status: 0
  - result: Review report exists and is non-empty.
- command: `test -s reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R2.md`
  - exit status: 0
  - result: Mandatory return exists and is non-empty.
- command: focused task-local `uv run --no-sync python -c` normal-constructor and metric probes, one retained case per W06-EC-R1-01 through W06-EC-R1-05
  - exit status: 0
  - result: reproduced every retained counterexample summarized above without protected expected-output access.

## Artifacts/evidence

- `reports/reviews/W06/evaluation-core-independent-review-R2.md` — full findings, explicit closure matrix, formulas, identifiers, correction bounds, and acceptance ledger.
- `reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R2.md` — mandatory closeout.
- `W06-EC-R1-01` through `W06-EC-R1-05` — all remain open with partial closures recorded exactly.

## Risks

- Leakage/partition: protected-labelled acceptance remains possible with FIT access and no metrics; future feature cutoffs remain unbound.
- Schema/digest: duplicate/non-canonical evidence and opaque candidate-universe identity can change weighting and aggregate identity.
- Metric/applicability: accepted partial-label and score inputs can yield out-of-range, exceptional, or order-dependent results; pair/agreement identity is not governed.
- Interval/claim: metric arithmetic, interval bounds/settings, run content, access, protocol, and gate identity can contradict one another while validating.
- Test residual: the public fixture authority/identity and retained adversarial cases are not mechanically exercised.

## Follow-up items

- Bind protocol, access, protected partition, non-empty run results, and gate acceptance as one validated aggregate; enforce the feature cutoff.
- Canonicalize and uniquely key every evidence collection, unordered pair, candidate universe, and same-subject adjudication.
- Correct partial gain/zero-denominator handling, reject non-finite scores, and make missingness/tie policies executable.
- Separate overlap calculations from Spearman availability and carry governed pair/item/reviewer identity into pair/agreement metrics.
- Enforce result arithmetic/ranges/protocol roster, interval ordering and resample identity, linked canonical run rosters, plus one rejecting regression per R1 row and executable fixture identity coverage.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no protected expected-output access: confirmed
- no external/provider or credential access: confirmed
- no delegation and no self-approval: confirmed

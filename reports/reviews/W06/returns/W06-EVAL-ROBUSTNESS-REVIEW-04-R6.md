# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-REVIEW-04-R6
- objective: Independently adjudicate the R6 single-core consolidation, exact boundary parity and mandated original three-parent regression completeness.

## Files changed

- reports/reviews/W06/evaluation-robustness-independent-review-R6.md
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R6.md

## Summary

- final verdict: **REWORK — 0 P0, 1 P1**.
- one live primitive calculation owns general, robustness-production and owning-validator ranking metric/bootstrap values, statuses, identities, seeded resampling and percentile bounds.
- all requested public boundaries independently reproduced with parity or the declared fail-closed adapter result.
- exact parents `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb`, `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815` and `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404` all reproduce and reject at runtime.
- no test contains any of those three literals, so exact recurrence coverage is absent despite the green focused suite.

## One-core call path

| Surface | Path |
|---|---|
| General per-query | `core.evaluate_ranking` → `_ranking_calculation` → `evaluation_calculations.derive_ranking_metric_children` |
| General bootstrap | `core.bootstrap_interval` → `_ranking_calculation` → shared calculation |
| Stress/control production | robustness producer → `contracts.evaluation.derive_ranking_metric_children` → shared calculation |
| Stress/control validation | owning validator → contract adapter → shared calculation → exact child equality |
| Rank comparison | all callers/validators → `derive_rank_comparison` |

## Boundary and parent outcomes

- all four metrics; partial off/on; zero recall/NDCG denominators; insufficient candidate population; missing labels where representable; canonical/reversed ties; integer/float scores; seed/resample identity; interval bounds; undeclared `k`; unsupported metric; query ordering/population: **PASS**.
- `fa8bea37...a8fb`: exact metadata comparison parent reproduced, **REJECT** with `control comparison values must equal canonical derivation`; committed literal assertion **ABSENT**.
- `e67c82c8...7815`: exact metadata aggregate parent reproduced, **REJECT** with `control metric values must equal canonical derivation`; committed literal assertion **ABSENT**.
- `2e70e316...1404`: exact relinked split aggregate/interval parent reproduced, **REJECT** with `stress metric and interval values must equal canonical derivation`; committed literal assertion **ABSENT**.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/w06-r6-review-uv-cache uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: `19 passed in 0.27s`.
- command: packet ruff check with the same no-bytecode/task-local-cache prefix
  - exit status: 0
  - result: all checks passed.
- command: packet mypy check with the same prefix
  - exit status: 0
  - result: no issues in 5 source files.
- command: packet `lint-imports` check with the same prefix
  - exit status: 0
  - result: 3 contracts kept, 0 broken.
- command: `shasum -a 256 tests/fixtures/w06/public-evaluation-v1.json tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`; `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.
- command: exact public boundary, three-parent and result-identity probes via `uv run --no-sync python`
  - exit status: 0
  - result: call-path/boundary matrices and all runtime parent outcomes reproduced.
- command: literal three-parent `rg` over `tests/`
  - exit status: 1
  - result: no mandated parent digest exists in committed tests.

## Artifacts/evidence

- reports/reviews/W06/evaluation-robustness-independent-review-R6.md
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R6.md

## Risks

- remaining P0: none identified.
- remaining P1: one — the exact three original substituted parents are not literally reconstructed and identity-pinned in committed tests.
- public implementation-only boundary remains intact; no protected, expert, transfer, prospective, provider, recruitment-outcome or positive empirical evidence was created.

## Follow-up items

- Add the three exact public substitutions and literal parent assertions to the existing normal-construction robustness regression; no production change is required.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output, external/provider/credential access, model tuning or new dependency: confirmed.
- no source, test, orchestration or other out-of-scope edits: confirmed.
- edits outside `allowed_paths`: none.

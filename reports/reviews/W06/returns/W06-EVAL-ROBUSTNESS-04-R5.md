# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-04-R5
- objective: Close the single numeric-child lineage class through one shared canonical derivation.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/evaluation/core.py
- src/scouting/evaluation/robustness.py
- tests/unit/test_w06_robustness.py
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-04-R5.md

## Summary

- Added shared pure derivations for complete rank-comparison values and complete per-query, aggregate, and deterministic bootstrap metric children.
- Robustness producers use those derivations; stress and deterministic-control validators reconstruct them from persisted rows, protocol, metric, and `k` and require exact equality.
- `core.rank_comparison` now uses the same comparison derivation.
- Normal-constructor regressions re-sign and reject comparison numeric, stress interval, and control aggregate numeric substitutions; unmodified public fixture identities pass.

## Tests run

- command: `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: `18 passed in 0.21s`.
- command: `uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: `Success: no issues found in 4 source files`.
- command: `uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken.
- command: `shasum -a 256 tests/fixtures/w06/public-evaluation-v1.json tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: evaluation `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`; robustness `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.
- command: `test -s reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-04-R5.md`
  - exit status: 0
  - result: mandatory return present.

## Artifacts/evidence

- comparison parent witness `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb`: reject under normal construction after re-signed Spearman substitution.
- control metric parent witness `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815`: reject under normal construction after re-signed aggregate substitution.
- stress metric/interval parent witness `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404`: reject under normal construction after re-signed interval resample-identity substitution.

## Risks

- remaining P0/P1 risk: none identified within the numeric-child lineage class.
- Implementation-only boundary retained: no fabricated expert, protected, transfer, prospective, provider, recruitment-outcome, or empirical applicability evidence.

## Follow-up items

- none.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider/credential access, model tuning, or out-of-scope changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

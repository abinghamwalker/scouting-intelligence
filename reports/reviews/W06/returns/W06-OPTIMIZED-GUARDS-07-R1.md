# Subagent return

## Task

- task_id: W06-OPTIMIZED-GUARDS-07-R1
- objective: Replace the seven Bandit-reported W06 runtime assertions with fail-closed optimized-mode guards and scope B311 only to deterministic statistical PRNGs.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/contracts/evaluation_calculations.py
- src/scouting/evaluation/robustness.py
- tests/contracts/test_w06_evaluation_contracts.py
- reports/reviews/W06/returns/W06-OPTIMIZED-GUARDS-07-R1.md

## Summary

- Replaced exactly these seven production assertions with explicit fail-closed guards, without changing their predicates:
  - `MetricResult.valid` computed value/numerator/denominator presence: `ValueError("computed metrics require value and sufficient statistics")`.
  - `BootstrapInterval.valid` computed point/lower/upper presence: `ValueError("computed interval requires point, resample identity and bounds")`.
  - `RankComparisonResult.valid` set-metric child presence: `ValueError("rank comparison set metrics must be present or absent together")`.
  - `StressTestResult._expected_deficits` walk-forward cutoff presence: `ValueError("walk-forward requires an embedded declared cutoff index")`.
  - `StressTestResult._expected_cohorts` walk-forward cutoff presence: `ValueError("walk-forward requires an embedded declared cutoff index")`.
  - `evaluate_stress_test` walk-forward cutoff presence: `ValueError("walk-forward requires an embedded declared cutoff index")`.
  - `assess_applicability` inventory runtime type: `TypeError("inventory must be a GovernedPopulationInventory")`.
- Added only three scoped `# nosec B311` annotations: `evaluation.py:1659` and `evaluation.py:1678` cover the two seeded shuffled-null `Random` constructions; `evaluation_calculations.py:241` covers the seeded bootstrap `Random` construction. Each is documented as deterministic statistical reproducibility PRNG use, never security or credential randomness.
- Added the single focused regression `test_optimized_python_still_rejects_missing_computed_metric_values`, which invokes the current interpreter with `-B -O` and proves a malformed computed `MetricResult` still rejects with the stable message.
- Confirmed `rg -n '\\bassert\\b'` finds no assertion in any of the three production files.

## Tests run

- command: `uv run --no-sync ruff format --check src/scouting/contracts/evaluation.py src/scouting/contracts/evaluation_calculations.py src/scouting/evaluation/robustness.py tests/contracts/test_w06_evaluation_contracts.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: `7 files already formatted`.
- command: `uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/evaluation_calculations.py src/scouting/evaluation/robustness.py tests/contracts/test_w06_evaluation_contracts.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: `All checks passed!`.
- command: `uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/contracts/evaluation_calculations.py src/scouting/evaluation/robustness.py`
  - exit status: 0
  - result: `Success: no issues found in 3 source files`.
- command: `uv run --no-sync bandit -q -r src/scouting/contracts/evaluation.py src/scouting/contracts/evaluation_calculations.py src/scouting/evaluation/robustness.py`
  - exit status: 0
  - result: no Bandit issues in the three production files.
- command: `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py tests/unit/test_w06_missing_population_gate.py`
  - exit status: 0
  - result: `25 passed in 0.99s`, including the optimized-Python witness.
- command: `shasum -a 256 configs/evaluation/w06-protected-preregistration-v1.json tests/fixtures/w06/public-evaluation-v1.json tests/fixtures/w06/public-robustness-v1.json tests/fixtures/w06/public-missing-population-gate-v1.json reports/evaluation/W06/protected-access-outcome.json reports/evaluation/W06/protected-gate-decision.json reports/evaluation/W06/protected-execution-receipt.json`
  - exit status: 0
  - result: unchanged identities listed below.

## Artifacts/evidence

- optimized-mode witness: `tests/contracts/test_w06_evaluation_contracts.py:359`.
- unchanged config/fixture/protected-output SHA-256 identities:
  - `configs/evaluation/w06-protected-preregistration-v1.json`: `dc2fdc1ec4178f1d913cf58268aca5d48eb699f7135b0e627975ef8d89de2410`
  - `tests/fixtures/w06/public-evaluation-v1.json`: `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`
  - `tests/fixtures/w06/public-robustness-v1.json`: `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`
  - `tests/fixtures/w06/public-missing-population-gate-v1.json`: `495f8148f68f36c1e98c3aff0f255a1009949d3ffcef583bdaaeda72dbc692eb`
  - `reports/evaluation/W06/protected-access-outcome.json`: `d614c24d77fb03af3b9bbdcdff730ace22667bba1b7cc2afa0bf9a2136f37084`
  - `reports/evaluation/W06/protected-gate-decision.json`: `f45d0a9530b1816ab221d5ece24db78883a0cefbcb362112bd518b3f1ba82e55`
  - `reports/evaluation/W06/protected-execution-receipt.json`: `1ad4b0e85f5008c97468a7932fde3d6b9ba1a93c507bb8cfdec1eebaf824842a`

## Risks

- remaining P0/P1 risk: none identified within this bounded optimized-mode correction.

## Follow-up items

- none.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed; no protected output, configuration, fixture, protocol, formula, seed, digest, gate, claim, orchestration, or external state was changed.

# W06 optimized guards independent review R1

## Decision

- verdict: **ACCEPT**
- P0 findings: **0**
- P1 findings: **0**
- decision-bearing findings: none

The seven former runtime-assert predicates are explicit fail-closed guards, survive optimized Python, and retain the same rejection predicates. The only three B311 suppressions are deterministic statistical PRNG constructions. Focused identities, frozen inputs, retained protected reports, and the sole-reason `NO_GO` remain unchanged.

## Seven guard mappings

1. `MetricResult.valid` (`src/scouting/contracts/evaluation.py:733-738`): when status is computed, `value`, `numerator`, and `denominator` must all be present; otherwise `ValueError("computed metrics require value and sufficient statistics")`.
2. `BootstrapInterval.valid` (`src/scouting/contracts/evaluation.py:815-818`): when status is computed, `lower`, `point_value`, and `upper` must all be present; otherwise `ValueError("computed interval requires point, resample identity and bounds")`. The surrounding validator continues to require the resample identity as well.
3. `RankComparisonResult.valid` (`src/scouting/contracts/evaluation.py:871-876`): an existing `overlap_count` requires `overlap_rate`, `jaccard`, and `candidate_churn`; otherwise `ValueError("rank comparison set metrics must be present or absent together")`.
4. `StressTestResult._expected_deficits` (`src/scouting/contracts/evaluation.py:2065-2067`): a walk-forward calculation requires a non-null embedded cutoff; otherwise `ValueError("walk-forward requires an embedded declared cutoff index")`.
5. `StressTestResult._expected_cohorts` (`src/scouting/contracts/evaluation.py:2263-2265`): a walk-forward cohort transformation requires a non-null embedded cutoff; otherwise the same stable `ValueError`.
6. `evaluate_stress_test` (`src/scouting/evaluation/robustness.py:244-246`): walk-forward execution requires a non-null embedded cutoff; otherwise the same stable `ValueError`.
7. `assess_applicability` (`src/scouting/evaluation/robustness.py:420-421`): `inventory` must be a `GovernedPopulationInventory`; otherwise `TypeError("inventory must be a GovernedPopulationInventory")`.

`rg -n "\\bassert\\b|random\\.(Random|random|randrange|choice|choices|shuffle)|nosec"` found no production assertion and only the three PRNG constructions classified below. An independent `uv run --no-sync python -B -O -c ...` witness exercised all seven mappings and exited 0 with:

```text
metric,interval,comparison,expected_deficits,expected_cohorts,evaluate_stress_test,inventory_type
```

## B311 classifications

1. `src/scouting/contracts/evaluation.py:1659`: `random.Random(f"{seed}:{row.query_id}").shuffle(labels)  # nosec B311` is a seeded shuffled-label null used for deterministic statistical reproducibility.
2. `src/scouting/contracts/evaluation.py:1678`: `random.Random(f"{seed}:{row.query_id}").shuffle(source)  # nosec B311` is a seeded shuffled-permutation null used for deterministic statistical reproducibility.
3. `src/scouting/contracts/evaluation_calculations.py:241`: `random.Random(bootstrap_seed)  # nosec B311` is the frozen-seed percentile bootstrap sampler used for deterministic statistical reproducibility.

All three operate on evaluation labels, candidate permutation identities, or bootstrap sample indexes. None supplies credentials, tokens, identifiers requiring unpredictability, cryptographic material, access control, or other security randomness. No broader suppression exists.

## Reproduced checks

- `uv run --no-sync ruff format --check ...`: exit 0; `7 files already formatted`.
- `uv run --no-sync ruff check ...`: exit 0; `All checks passed!`.
- `uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/contracts/evaluation_calculations.py src/scouting/evaluation/robustness.py`: exit 0; no issues in 3 source files.
- `uv run --no-sync bandit -q -r src/scouting/contracts/evaluation.py src/scouting/contracts/evaluation_calculations.py src/scouting/evaluation/robustness.py`: exit 0; no issues.
- `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py tests/unit/test_w06_missing_population_gate.py`: exit 0; `25 passed in 0.49s`, including the committed optimized-Python witness.
- Independent seven-path optimized witness under `python -B -O`: exit 0; all seven stable rejection labels observed.

The first sandboxed static-check attempt exited 2 before tool execution because the managed sandbox denied read access to uv's existing cache metadata. The identical bounded commands were rerun with approved cache access, repository bytecode/cache writes disabled or redirected to `/tmp`, and passed as recorded above. This environmental denial is not a product finding.

## Frozen and protected identities

- `configs/evaluation/w06-protected-preregistration-v1.json`: `dc2fdc1ec4178f1d913cf58268aca5d48eb699f7135b0e627975ef8d89de2410`
- `tests/fixtures/w06/public-evaluation-v1.json`: `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`
- `tests/fixtures/w06/public-robustness-v1.json`: `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`
- `tests/fixtures/w06/public-missing-population-gate-v1.json`: `495f8148f68f36c1e98c3aff0f255a1009949d3ffcef583bdaaeda72dbc692eb`
- `reports/evaluation/W06/protected-access-outcome.json`: `d614c24d77fb03af3b9bbdcdff730ace22667bba1b7cc2afa0bf9a2136f37084`
- `reports/evaluation/W06/protected-gate-decision.json`: `f45d0a9530b1816ab221d5ece24db78883a0cefbcb362112bd518b3f1ba82e55`
- `reports/evaluation/W06/protected-execution-receipt.json`: `1ad4b0e85f5008c97468a7932fde3d6b9ba1a93c507bb8cfdec1eebaf824842a`

These match the retained identities in the producer handback and the focused public identity witnesses passed. The retained decision is still `NO_GO`, with no bundle or run, protected outputs not opened, and exactly one reason: `MISSING_EXPERT_RELEVANCE_EVIDENCE`.

## Scope confirmation

- Wrote only this review and the mandatory return named by the review packet.
- No code, tests, fixtures, configuration, evidence, protected report, orchestration, dependency, lockfile, or Git state was changed.
- No broker was invoked; no protected expected output, external/provider resource, credential, network service, or delegated agent was accessed.

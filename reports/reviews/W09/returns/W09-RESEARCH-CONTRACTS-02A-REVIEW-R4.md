# Subagent return

## Task

- task_id: `W09-RESEARCH-CONTRACTS-02A-REVIEW`
- revision: `R4`
- objective: Independently verify the two R3 P1 corrections, rerun all seven former R2 adversarial cases, search adjacent P1/P2 contradictions, and issue the final shared-boundary recommendation.

## Files changed

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R4.md`

## Recommendation

- recommendation: **REWORK**
- highest severity: **P1**
- open finding count: **1 P1, 1 P2**
- Both R3 P1 attacks are resolved, all seven former R2 attacks remain closed, and the full named parity suite passes. Acceptance is nevertheless blocked by two fresh strict-numeric interoperability defects found in adjacent finite-float cases: the scorer returns a mathematically false and internally inconsistent cosine result for accepted subnormal inputs, and the strict result contract raises an uncontrolled `OverflowError` while checking a scorer-valid large-finite cosine explanation.

## R3 correction disposition

| R3 P1 | Disposition | Independent executable evidence |
| --- | --- | --- |
| Zero referred players with non-zero referred grains/eligible matrix row | **RESOLVED** | Rebuilt a self-digested manifest with 3,603 catalogue decisions, zero referred players, 3,603 no-lineup decisions, 2,996 referred grains/eligibility decisions and one eligible matrix row. The canonical digest was recomputed after mutation. Validation rejected it with `referred players and referred grains must be empty together`. The inverse zero-grain/non-zero-player case is also guarded at `research.py:422-425`, with regression attacks at `test_w09_research_contracts.py:599-611`. |
| Aligned large-finite cosine vectors silently returned distance 1 | **RESOLVED** | Reconstructed the exact query `[1e308, 1e308]` and candidate `[1.0, 1.0]` as little-endian float64 under exact `WEIGHTED_COSINE`. The scorer returned distance `2.220446049250313e-16` and contributions `(-0.4999999999999999, -0.4999999999999999)`, numerically the correct zero-distance result. Weighted-component overflow and Euclidean subtraction/square overflow instead raise `VectorScoringError`. The stable `math.hypot` path and finite guards are at `scoring.py:106-149`; the regression is at `test_w09_scoring_kernel.py:117-134`. |

## Former R2 attack disposition

| R2 case | Disposition | Fresh reconstruction |
| --- | --- | --- |
| 1. Exact minutes mislabeled `UNUSABLE_MINUTES` | **RESOLVED** | Rejected with `usable minute evidence requires minutes and a usable outcome`. |
| 2. Referred grain/decision and unique matrix counts could contradict population | **RESOLVED** | A freshly self-digested 2,996-player/one-grain manifest and a one-row/two-unique-grain manifest were both rejected by their semantic invariants, not merely by stale digests. The R3 zero-boundary variant was also rejected as above. |
| 3. Contribution contradicted displayed contrast | **RESOLVED** | A re-digested Euclidean result with zero scaled contrast, contribution 1 and score 1 was rejected with `Euclidean contributions must reconcile to squared distance`. |
| 4. Exclusion counts claimed an absent filter | **RESOLVED** | A balanced result with no submitted position filter and `position_exclusions=1` was rejected with `position exclusions require a submitted position filter`. |
| 5. Comparison used the right grain for the wrong player | **RESOLVED** | Replaced a comparison row's player, then recomputed the comparison, report and experiment bindings. `SavedResearchExperiment` rejected it with `comparison row identity must equal its result candidate`. |
| 6. `RESULT_MISMATCH` used a different query | **RESOLVED** | Recomputed the receipt digest after changing the replay query digest under equal pins. Validation rejected it with `result mismatch requires identical saved query and compatible pins`. |
| 7. Invalid scorer method, negative-zero output/weights and finite post-operation safety | **RESOLVED for the former attacks** | A string method and a `-0.0` weight raise `VectorScoringError`; valid cosine zero terms are canonical positive zero and round-trip through strict `FeatureContribution`; the exact former large-finite overflow returns the correct aligned score. The fresh subnormal attack below is a distinct adjacent finite-domain defect. |

## Severity-ranked findings

### [P1] Accepted subnormal cosine vectors violate scale invariance and explanation reconciliation

`score_vector_rows` accepts every finite little-endian float64 vector. It computes `math.hypot` directly over weighted components and divides the original subnormal components by the rounded subnormal norm (`src/scouting/m0/scoring.py:106-149`). Near float64's minimum positive values, the norm has too little relative precision to produce a unit normalized vector. The final `max(0.0, distance)` then hides negative pre-clamp distances without reconciling the returned contributions (`:149-154`).

The independent attack used an aligned query `[5e-324, 5e-324]` and candidate `[1.0, 1.0]`. Both are finite and non-zero. The scorer accepted them and returned:

- `distance = 0.0`;
- `contributions = (-0.7071067811865475, -0.7071067811865475)`;
- explanation-implied distance `1 + sum(contributions) = -0.4142135623730949`.

At `[1e-323, 1e-323]`, the same aligned direction returned distance `0.057190958417936755` instead of zero. A magnitude sweep through `5e-324`, `1e-323`, `5e-323`, `1e-322`, `1e-320`, `1e-310`, `1e-308` and `1e-307` reproduced scale-dependent scores and, in several cases, a returned distance different from `1 + sum(contributions)`. This is silent deterministic ranking and explanation corruption over inputs the scorer explicitly admits, so G-RW2's inspectable-explanation floor is not met.

Required correction: normalize weighted vectors in a scale-invariant way (for example, scale by the maximum absolute component before the norm), or reject numerically unsupported non-zero magnitudes with `VectorScoringError`. Before returning, enforce a finite cosine range and reconciliation between distance and contribution sum; do not use clamping to conceal a materially negative computed distance. Add exact subnormal/near-subnormal scale-invariance and explanation-reconciliation attacks.

### [P2] The strict result contract cannot safely verify scorer-valid large-finite cosine output

The scorer now correctly handles the former `[1e308, 1e308]` cosine case, but `ResearchQueryResult.result_is_coherent` independently recomputes weighted norms with `scaled_value**2` (`src/scouting/contracts/research.py:819-829`). Constructing a two-feature candidate from the scorer's correct large-finite output reaches this validator and raises raw `OverflowError: (34, 'Result too large')`, rather than validating the correct explanation or producing a controlled Pydantic validation failure. The scorer and strict public result contract therefore disagree on their accepted finite domain.

The same validator underflows subnormal squares to zero and rejects the scorer's non-zero normalized components, confirming that the shared scorer/result boundary is not interoperable at either extreme. Separately, weighted-component multiplication can emit a NumPy overflow warning immediately before the scorer's intended `VectorScoringError` (`scoring.py:107-110`); this does not corrupt a returned row but should be contained by the same numeric guard.

Required correction: share an overflow/underflow-stable normalization/reconciliation primitive between scoring and contract verification, or align both boundaries around an explicitly rejected numeric domain. Ensure all unsafe finite cases fail through controlled contract/scoring errors, never raw arithmetic exceptions. Add an end-to-end test that converts the corrected large-finite scorer output into strict `FeatureContribution`/`ResearchQueryResult` contracts.

## Fresh contradiction search

- Re-read manifest population reconciliation, eligibility reasons, matrix uniqueness, exact version pins, query-mode exclusivity, filter/count provenance, deterministic ranking, comparison/result identity binding, report/experiment binding, replay status/query/pin binding, public exports and fixed claim literals.
- Probed large, tiny and minimum-subnormal aligned/opposed cosine vectors, huge finite weights, Euclidean overflow, invalid methods, negative-zero weights and strict contribution/result construction. No additional P1/P2 contradiction was established beyond the two numeric findings above.
- Both findings are bounded implementation/test corrections. No product decision, provider access, data-rights decision, dependency, deployment or architecture expansion is required.

## W05 and boundary conclusions

- **W05 public-export compatibility: PASS.** Generic `FeatureValue`/`FeatureValueState` remain the existing M0 pair, explicit M0 aliases remain identical, and `ResearchFeatureValueState` remains the W09 enum in `src/scouting/contracts/__init__.py`.
- **W05 scorer/serving fixture parity: PASS.** The complete named suite passes 32 tests, including W05 model and integration-serving checks. The R3 corrections did not alter the pinned W05 fixture outputs.
- **Strict numeric interoperability: REWORK.** The former large-finite overflow is fixed and invalid/non-finite/negative-zero cases are controlled, but accepted subnormals can still corrupt cosine score/explanation semantics, and scorer-valid large finite explanations crash strict result verification with raw overflow.
- **W09 claim boundary: PASS.** Dataset, matrix/index, query, candidate, result and report surfaces retain `historical_resemblance_research_only`; matrix/index rows remain literal non-synthetic; limitations stay mandatory. No football relevance, recruitment usefulness, recommendation, current-market or G-RW4 claim was introduced.

## Checks run

- `uv run ruff check src/scouting/contracts/research.py src/scouting/contracts/__init__.py tests/contracts/test_w09_research_contracts.py src/scouting/m0/scoring.py src/scouting/m0/core.py tests/unit/test_w09_scoring_kernel.py`
  - exit status: `0`
  - result: PASS — `All checks passed!`
- `uv run mypy src/scouting/contracts/research.py src/scouting/m0/scoring.py src/scouting/m0/core.py`
  - exit status: `0`
  - result: PASS — no issues found in three source files.
- `uv run pytest -q tests/contracts/test_w09_research_contracts.py tests/unit/test_w09_scoring_kernel.py tests/unit/test_w05_m0_models.py tests/integration/test_w05_m0_serving.py`
  - exit status: `0`
  - result: PASS — 32 tests passed in 1.54 seconds.
- Independent local-only `uv run python -c` probes reconstructed both R3 P1 attacks and all seven former R2 cases rather than invoking their committed test functions. Further probes exercised large, tiny, subnormal, opposed and weighted-overflow vectors and strict result construction. The processes exited `0` after explicitly recording each disposition.
- `test -s reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R4.md`
  - exit status: `0`
  - result: PASS — the required R4 review artifact is non-empty.

## Artifacts/evidence

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R4.md`
- implementation reviewed: `src/scouting/contracts/research.py`, `src/scouting/contracts/__init__.py`, `src/scouting/m0/scoring.py`, `src/scouting/m0/core.py`
- tests reviewed: `tests/contracts/test_w09_research_contracts.py`, `tests/unit/test_w09_scoring_kernel.py`, plus named W05 model/serving parity tests
- population authority: `reports/verification/W09/data-inventory-and-coverage.md`
- prior review: `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R3.md`

## Risks and follow-up

- Issue bounded rework for stable subnormal normalization, pre-return cosine reconciliation and shared scorer/result numeric verification. Add the exact probes above, preserve the passing W05 suite and claim boundary, then obtain a fresh independent review before accepting the shared W09 contract/scorer floor.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no dependency or lockfile changes: confirmed.
- no implementation, test or orchestration edits: confirmed.
- no edits outside `allowed_paths`: confirmed; only this R4 report was created.

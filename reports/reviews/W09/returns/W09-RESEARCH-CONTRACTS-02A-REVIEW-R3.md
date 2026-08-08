# Subagent return

## Task

- task_id: `W09-RESEARCH-CONTRACTS-02A-REVIEW`
- revision: `R3`
- objective: Independently verify all seven R2 P1 contract/scorer findings, search for adjacent executable contradictions, and preserve W05 compatibility and the historical-resemblance-only boundary.

## Files changed

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R3.md`

## Recommendation

- recommendation: **REWORK**
- highest severity: **P1**
- open finding count: **2 P1, 0 P2**
- Six former findings are fully resolved. The seventh is substantially corrected, but its required post-operation finite guard remains incomplete. A second zero-boundary reconciliation attack was found in the new matrix-manifest fields. Both attacks were independently executed with fresh canonical digests or strict scorer inputs; neither is inferred only from the committed tests.

## R2 finding-by-finding disposition

| R2 P1 | Disposition | Independent executable evidence |
| --- | --- | --- |
| 1. `UNUSABLE_MINUTES` accepted exact exposure | **RESOLVED** | Reconstructed `EligibilityDecision` with `EXACT`, 900 minutes and `UNUSABLE_MINUTES`. It now raises validation error `usable minute evidence requires minutes and a usable outcome` through `research.py:190-194`. Probe output: `R2-1_REJECTED True`. Both directions are also covered at `test_w09_research_contracts.py:333-370`. |
| 2. Manifest did not bind referred grains/eligibility decisions or unique matrix grains | **PARTIAL; P1 remains** | The exact R2 attacks—2,996 referred players with one referred grain/decision, and `unique_matrix_grain_count=2` with one row—were independently rejected. New fields and checks are at `research.py:383-398` and `:415-446`. A zero-referred boundary still accepts one referred grain, one eligible decision and one matrix row; see finding 1. |
| 3. Contribution could contradict its displayed contrast | **RESOLVED** | Rebuilt a Euclidean result with identical scaled values, zero contrast, weight 1, contribution 1 and score 1. It now raises `Euclidean contributions must reconcile to squared distance` through the per-term formula at `research.py:797-815`. Probe output: `R2-3_REJECTED True`. Cosine terms now bind scaled and normalized operands at `:816-873`. |
| 4. Counts could claim filters that were not submitted | **RESOLVED** | Rebuilt a balanced result with no position filter and `position_exclusions=1`. It now raises `position exclusions require a submitted position filter` at `research.py:743-749`. Equivalent explicit-player presence and upper-bound checks are at `:750-758`. Probe output: `R2-4_REJECTED True`. |
| 5. Comparison could bind the right grain to the wrong player | **RESOLVED** | Recomputed valid comparison, report and experiment digests after replacing the first row's player with the second candidate's player. The experiment now rejects it at `research.py:984-1002`. Probe output: `R2-5_REJECTED True`. Player, competition and position identities are all cross-bound. |
| 6. `RESULT_MISMATCH` accepted a different replay query | **RESOLVED** | Recomputed a receipt with equal pins, different query digest and closed result-mismatch values. It now raises `result mismatch requires identical saved query and compatible pins` at `research.py:1082-1086`. Probe output: `R2-6_REJECTED True`. |
| 7. Shared scorer accepted invalid methods and emitted non-canonical/unsafe numerics | **PARTIAL; P1 remains** | Invalid string methods and negative-zero weights are rejected at `scoring.py:60-61` and `:78-86`. A valid cosine zero term is canonical `0.0` and round-trips through two strict `FeatureContribution` models; outputs: `R2-7_INVALID_METHOD_REJECTED`, `R2-7_CANONICAL_ROUNDTRIP True 2`, `R2-7_NEGATIVE_ZERO_WEIGHT_REJECTED`. Finite inputs that overflow the unchecked norm still silently produce the wrong distance; see finding 2. |

## Severity-ranked findings

### [P1] A manifest can produce an eligible matrix row from zero referred players

`FeatureMatrixManifest.manifest_is_coherent` requires only `population_referred_grain_count >= population_referred_count` before equating grains, eligibility decisions and unique eligibility grains (`src/scouting/contracts/research.py:422-427`). It does not require both referred counts to be zero or non-zero together.

The independent probe built a canonical, self-digested manifest with:

- 3,603 catalogue/population decisions;
- zero referred players and 3,603 no-lineup players;
- one referred grain, one unique eligibility decision, one eligible reason;
- one unique matrix grain/player/row.

The model accepted it and printed `ZERO_REFERRED_ACCEPTED_BAD`. This claims a governed eligible player row despite the catalogue ledger referring no player to window eligibility, breaking the source-to-grain reconciliation required by G-RW1.

Required correction: enforce `bool(population_referred_count) == bool(population_referred_grain_count)` in addition to the existing lower bound, or otherwise encode an exact referred-player-to-grain ledger cardinality proof. Add zero-player/non-zero-grain and non-zero-player/zero-grain attacks.

### [P1] Finite cosine inputs can overflow an unchecked norm and silently become distance 1

The scorer validates finite inputs and canonicalizes final contributions/distance, but computes query and candidate norms without applying `_canonical_finite_float` or an overflow-stable norm (`src/scouting/m0/scoring.py:107-110`, `:124-126`). With NumPy warnings locally suppressed only to make the probe output clear, the exact finite inputs were:

- query: `[1e308, 1e308]` little-endian float64;
- candidate: `[[1.0, 1.0]]` little-endian float64;
- method: exact `WEIGHTED_COSINE`; default positive weights.

Squaring the query overflowed the norm to infinity; finite-over-infinite terms became zero. The scorer accepted the row and printed `POST_OPERATION_OVERFLOW_ACCEPTED_BAD 1.0 (0.0, 0.0)`. These aligned non-zero vectors have cosine distance 0, not 1. This is a silent ranking/explanation corruption, and it leaves the R2 requirement to fail on non-finite post-operation values unresolved.

Required correction: use an overflow-stable weighted norm or reject any non-finite norm/intermediate before the zero-norm branch and term calculation. Add large-finite Euclidean/cosine attacks and assert either mathematically correct finite output or `VectorScoringError`; never accept the fallback result.

## Fresh contradiction search

- Query-mode exclusivity, exact cutoff pins, strict clocks, digest projections, candidate order/uniqueness, contribution names/weights, comparison pins, report/result/experiment timestamps, replay status/reason mapping, package exports and literal claims were reread in the complete current files. No additional P1/P2 issue was found beyond the two executable cases above.
- The manifest and overflow cases are bounded implementation defects; no new product, rights, provider, dependency or architectural decision is required.

## W05 and boundary conclusions

- **W05 public-export compatibility: PASS.** Generic `FeatureValue`/`FeatureValueState` remain the M0 pair; explicit M0 aliases are identical; `ResearchFeatureValueState` is the W09 enum (`contracts/__init__.py:81-87`, `:138-177`, `:229-230`).
- **W05 scorer/serving fixture parity: PASS.** The full named suite passes 31 tests, including W05 model and integration serving checks. The invalid-method and zero canonicalization fixes do not alter accepted fixture behaviour.
- **Strict numeric interoperability: REWORK.** Invalid methods, NaN/infinity inputs, negative-zero weights, final negative-zero terms and strict contribution round-trip are controlled. Unchecked finite overflow still produces a semantically false cosine result.
- **W09 claim boundary: PASS.** Dataset, matrix/index, query, candidate, result and report surfaces retain the fixed `historical_resemblance_research_only` literal and mandatory limitations. Rights remain closed to the retained Wyscout classification. No football relevance, current-market, recruitment usefulness, recommendation or G-RW4 claim was introduced.

## Checks run

- `uv run ruff check src/scouting/contracts/research.py src/scouting/contracts/__init__.py tests/contracts/test_w09_research_contracts.py src/scouting/m0/scoring.py src/scouting/m0/core.py tests/unit/test_w09_scoring_kernel.py`
  - exit status: `0`
  - result: PASS — `All checks passed!`
- `uv run mypy src/scouting/contracts/research.py src/scouting/m0/scoring.py src/scouting/m0/core.py`
  - exit status: `0`
  - result: PASS — no issues in three source files.
- `uv run pytest -q tests/contracts/test_w09_research_contracts.py tests/unit/test_w09_scoring_kernel.py tests/unit/test_w05_m0_models.py tests/integration/test_w05_m0_serving.py`
  - exit status: `0`
  - result: PASS — 31 tests passed in 1.27 seconds.
- Seven local-only `uv run python -c` adversarial invocations reconstructed every former R2 payload rather than invoking its test function. The manifest invocation additionally tried the zero-referred boundary; the scorer invocation additionally tried large finite overflow. All processes exited `0` after recording whether strict validation rejected or accepted each attack.
- `test -s reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R3.md`
  - exit status: `0`
  - result: PASS — the required R3 review artifact is non-empty.

## Artifacts/evidence

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R3.md`
- implementation: `src/scouting/contracts/research.py`, `src/scouting/contracts/__init__.py`, `src/scouting/m0/scoring.py`, `src/scouting/m0/core.py`
- tests: `tests/contracts/test_w09_research_contracts.py`, `tests/unit/test_w09_scoring_kernel.py`
- population authority: `reports/verification/W09/data-inventory-and-coverage.md`
- prior review: `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R2.md`

## Risks and follow-up

- Issue bounded rework for the zero-referred manifest invariant and overflow-safe scorer norm, add the exact probes above, preserve the passing W05 suite and claim boundary, and obtain a fresh independent review before accepting the shared contract/scorer floor.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no dependency or lockfile changes: confirmed.
- no implementation, test or orchestration edits: confirmed.
- no edits outside `allowed_paths`: confirmed; only this R3 report was created.

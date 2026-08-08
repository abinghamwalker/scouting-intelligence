# Subagent return

## Task

- task_id: `W09-RESEARCH-CONTRACTS-02A-REVIEW`
- revision: `R2`
- objective: Independently verify that every R1 contract finding is resolved without weakening accepted W05 compatibility or the historical-resemblance-only boundary.

## Files changed

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R2.md`

## Recommendation

- recommendation: **REWORK**
- highest severity: **P1**
- new/open finding count: **7 P1, 0 P2**
- The revision materially improves the boundary: typed matrix/index manifests now exist; rows carry coverage, windows, minute state and lineage pins; authority clocks are strict-before; queries carry a self-digest and exact cutoff pin; result order, aggregate contribution reconciliation and count trees are checked; comparisons, reports, experiments and replay receipts have substantially stronger digests; numeric aliases reject negative zero; and public M0/research feature-state exports are no longer cross-wired.
- It is not yet acceptable because seven executable contradictions remain. Each affects a declared W09 gate or fail-closed shared scorer boundary, rather than formatting or documentation.

## R1 finding-by-finding disposition

| R1 finding | R2 disposition | Exact evidence |
| --- | --- | --- |
| Eligibility could not represent reconciliation and accepted contradictions | **PARTIAL; P1 remains** | `SourcePopulationDecision` now separates catalogue decisions from window eligibility (`research.py:126-150`) and `EligibilityDecision` carries policy/temporal evidence (`:164-210`). However, the implication is one-way: `minute_state=UNUSABLE` requires `reason=UNUSABLE_MINUTES`, while `reason=UNUSABLE_MINUTES` does not require the unusable state (`:190-194`). A read-only construction with `EXACT`, 900 minutes and `UNUSABLE_MINUTES` validated successfully. See R2 finding 1. |
| No typed manifests; matrix row lacked coverage/lineage/window/exposure | **PARTIAL; P1 remains** | The row fields and both manifest types are present (`research.py:253-497`). Manifest reconciliation still accepts fewer eligibility decisions than referred players and does not assert unique grain count. The checked test fixture itself validates 2,996 referred players with one eligibility decision (`test_w09_research_contracts.py:441-458`). See R2 finding 2. |
| Cutoff equality and query/matrix cutoff drift | **RESOLVED** | Dataset authorities and window end must be strictly before cutoff (`research.py:105-115`); row/manifest windows use the same rule (`:328-331`, `:403-409`); query cutoff must exactly equal its pins (`:583-588`); pins carry the cutoff and matrix/index identities (`:500-525`). The equality adversary is tested at `test_w09_research_contracts.py:275-300`. |
| Rankings/explanations were not reproducible | **PARTIAL; P1 remains** | Non-negative scores, rank order, uniqueness, filter membership, exact feature order/weights and aggregate Euclidean/cosine reconciliation are enforced (`research.py:620-645`, `:695-773`). Per-feature contributions remain unrelated to their displayed contrast/value evidence, and the shared scorer can emit contract-invalid negative zero. See R2 findings 3 and 7. |
| Population counts could be impossible | **PARTIAL; P1 remains** | The parent/child tree and exact return count are now enforced (`research.py:648-676`, `:699-714`). Counts can still report position or minimum-minute exclusions when the corresponding filter was not submitted. See R2 finding 4. |
| Saved experiments/comparisons were under-bound | **PARTIAL; P1 remains** | The result embeds the exact request; comparison request pins and grain order are checked; report digests/pins and timestamps are cross-bound (`research.py:776-907`). The saved experiment checks only comparison grain membership, allowing a row with the right grain but the wrong player identity. See R2 finding 5. |
| Replay receipt did not prove replay of the named experiment | **PARTIAL; P1 remains** | Experiment/query/result identities, pins, closed status/reason values and a self-digest were added (`research.py:910-978`). `RESULT_MISMATCH` still accepts a different replay query, so it does not prove deterministic execution of the saved query. See R2 finding 6. |
| Package exports paired the wrong M0/W09 enums | **RESOLVED** | Generic `FeatureValue`/`FeatureValueState` remain the accepted M0 exports (`contracts/__init__.py:81-87`, `:229-230`); W09 uses the explicit `ResearchFeatureValueState` alias (`:138-177`). Package identity and construction are tested at `test_w09_research_contracts.py:543-558`. |
| Feature values admitted contradictory/non-canonical evidence | **RESOLVED at the contract; scorer interoperability remains P1** | Negative zero is rejected by all three float aliases (`research.py:26-45`); observed/absent state, zero/value and numerator/denominator rules are enforced (`:223-250`) and adversarially tested (`test_w09_research_contracts.py:333-348`, `:561-572`). The shared cosine scorer still emits `-0.0`; see R2 finding 7. |

## Severity-ranked findings

### [P1] `UNUSABLE_MINUTES` still accepts exact, usable exposure

`EligibilityDecision.outcome_is_coherent` validates the implication from `MinuteEvidenceState.UNUSABLE` to `EligibilityReason.UNUSABLE_MINUTES`, but not its converse (`src/scouting/contracts/research.py:190-194`). The following semantic combination validated in the independent read-only probe: `minute_state=EXACT`, `minutes=900.0`, `minimum_minutes=450.0`, `eligible=False`, `reason=UNUSABLE_MINUTES`, strict temporal evidence true. This is the exact R1 contradiction and permits an exclusion ledger to misstate usable exposure as unusable.

Required correction: require `reason is UNUSABLE_MINUTES` if and only if `minute_state is UNUSABLE` and `minutes is None`; add both directional adversarial tests.

### [P1] Matrix-manifest counts do not prove one eligibility decision per referred grain or unique matrix grain

`FeatureMatrixManifest.manifest_is_coherent` reconciles the two catalogue decisions and the eligibility reason sum, but never relates `population_referred_count` to `eligibility_decision_count` (`src/scouting/contracts/research.py:410-431`). The committed positive fixture validates `population_referred_count=2996` with `eligibility_decision_count=1` (`tests/contracts/test_w09_research_contracts.py:441-458`). A referred player has one or more `grain_ids` by contract (`research.py:143-149`), so 2,996 referred players cannot truthfully yield one eligibility decision.

The only uniqueness field is `unique_matrix_player_count`, checked merely as `<= matrix_row_count` (`research.py:392-393`, `:432-433`). Multiple competition/window rows per player may be valid, so player uniqueness cannot prove the required exactly-one-row-per-declared-grain invariant.

Required correction: bind a referred-grain total/ledger digest, require eligibility decisions to equal that total, add `unique_matrix_grain_count == matrix_row_count`, and test duplicate/missing ledger branches. This is required before G-RW1 can rely on the manifest.

### [P1] A feature explanation can display zero contrast while assigning it a non-zero contribution

The result validator checks only the sum of contribution values against the score (`src/scouting/contracts/research.py:753-770`). It does not validate a Euclidean term as `weight * scaled_contrast**2`, nor otherwise bind `query_value`, `candidate_value` and `scaled_contrast`. An independently constructed Euclidean result with identical displayed values, `scaled_contrast=0.0`, `weight=1.0`, `contribution=1.0` and `score=1.0` validated successfully because the aggregate sum matched.

Required correction: validate each Euclidean contribution against its declared weight and scaled contrast. For cosine, expose the normalized per-feature operands needed to reproduce each signed term and validate each term, not only the sum. Add one-field redistribution/zero-contrast attacks.

### [P1] Retrieval counts can claim exclusions for filters that were never submitted

The final result checks profile/self and explicit-player count bounds (`src/scouting/contracts/research.py:704-714`) and returned candidates satisfy actual filters (`:730-748`). It does not require `position_exclusions == 0` when `position_codes` is empty or `minimum_minutes_exclusions == 0` when `minimum_minutes is None`. A read-only result with no position filter and `position_exclusions=1` validated successfully while its arithmetic tree remained balanced.

Required correction: make every exclusion count conditional on the corresponding submitted filter, and test absent-filter/non-zero-count combinations. Otherwise population accounting can hide an unrequested exclusion and cannot evidence full-population behaviour for G-RW2.

### [P1] A saved comparison can bind the right grain but the wrong player

`ResearchComparison` checks requested grain order and row data pins (`src/scouting/contracts/research.py:804-832`). `SavedResearchExperiment` then checks only that comparison grain IDs are a subset of result candidate grain IDs (`:881-891`). It never compares each row's `player_id` (or competition) with the candidate having that grain. The independent probe replaced the first comparison row's player with the second candidate's player, recomputed the legitimate comparison/report/experiment digests, and the saved experiment validated.

Required correction: in the experiment validator, map candidates by grain and require row player/competition/position identity to match the result candidate for every requested grain. Add a recomputed-digest identity-substitution test.

### [P1] `RESULT_MISMATCH` replay status accepts a different query

For `RESULT_MISMATCH`, the receipt validator requires only equal saved/loaded pins (`src/scouting/contracts/research.py:971-975`). It does not require `saved_query_digest == replay_query_digest`. A receipt with equal pins, different query digests, different result ID/digest, closed `RESULT_MISMATCH`/`DETERMINISTIC_RESULT_MISMATCH` values and a correct receipt digest validated successfully.

Required correction: require query-digest equality for a deterministic result mismatch, or introduce a distinct closed query-mismatch status. A receipt must not call execution deterministic when it did not replay the saved query.

### [P1] The shared scorer is not fail-closed or serialization-compatible with the W09 numeric contracts

`score_vector_rows` does not validate `method` at runtime. Any non-enum value misses both identity comparisons, takes the zero-query-norm cosine fallback and returns a distance instead of failing (`src/scouting/m0/scoring.py:84-102`, `:107-130`). The read-only probe passed `"not_a_method"` and received distance `1.0`.

For valid cosine scoring, terms are negated directly (`src/scouting/m0/scoring.py:123-129`). Query `[1, 1]` against candidate `[1, 0]` produced contributions `(-0.7071067811865475, -0.0)`. `FeatureContribution.contribution` uses `FiniteFloat`, which rejects negative zero (`research.py:26-36`, `:609-617`). Thus a valid shared-kernel result cannot always cross the strict W09 result boundary.

Required correction: reject any method not exactly `VectorScoringMethod`, canonicalize all zero inputs/outputs (including weights and projected contributions), fail on non-finite post-operation values, and add scorer-to-`FeatureContribution` round-trip tests for Euclidean, cosine, zero components and invalid methods. Preserve the accepted W05 outputs while doing so.

## W05 compatibility and claim-boundary conclusions

- **W05 public exports: PASS.** Existing generic M0 names remain unchanged, explicit M0 aliases are identical, and explicit research aliases point to the W09 types. The focused package-export test passes.
- **W05 serving/scoring regression suite: PASS for current accepted fixtures.** All 28 named contract/scorer/W05 model/serving tests pass. The refactor to the shared scorer has not changed the checked W05 fixture outputs. This does not cure the new shared-kernel fail-open/negative-zero cases above; the bounded correction must retain this parity.
- **W09 claim boundary: PASS.** The fixed literal `historical_resemblance_research_only` is present on dataset, matrix/index, query, candidate, result and report surfaces; rights are a closed Wyscout classification; limitations remain mandatory; and no recruitment outcome, usefulness, current-market or recommendation field was introduced. G-RW4 remains absent and no positive football-relevance claim is authorised.

## Checks run

- `uv run ruff check src/scouting/contracts/research.py src/scouting/contracts/__init__.py tests/contracts/test_w09_research_contracts.py src/scouting/m0/scoring.py src/scouting/m0/core.py tests/unit/test_w09_scoring_kernel.py`
  - exit status: `0`
  - result: PASS — `All checks passed!`
- `uv run mypy src/scouting/contracts/research.py src/scouting/m0/scoring.py src/scouting/m0/core.py`
  - exit status: `0`
  - result: PASS — no issues in three source files.
- `uv run pytest -q tests/contracts/test_w09_research_contracts.py tests/unit/test_w09_scoring_kernel.py tests/unit/test_w05_m0_models.py tests/integration/test_w05_m0_serving.py`
  - exit status: `0`
  - result: PASS — 28 tests passed in 1.23 seconds.
- Three additional local-only `uv run python -c` adversarial constructions exercised the eligibility/scorer, result/contribution, and count/comparison/replay cases described above.
  - exit status: `0` for each probe; each supposedly invalid model/result was accepted as reported.
- `test -s reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R2.md`
  - exit status: `0`
  - result: PASS — the required R2 review artifact is non-empty.

## Artifacts/evidence

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R2.md`
- Reviewed implementation: `src/scouting/contracts/research.py`, `src/scouting/contracts/__init__.py`, `src/scouting/m0/scoring.py`, `src/scouting/m0/core.py`
- Reviewed tests: `tests/contracts/test_w09_research_contracts.py`, `tests/unit/test_w09_scoring_kernel.py`
- Population authority: `reports/verification/W09/data-inventory-and-coverage.md`
- Prior review: `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R1.md`

## Risks and follow-up

- Freezing these shapes now would let later matrix, API, compare and replay producers generate self-digested but semantically contradictory artifacts. Issue bounded rework for all seven P1 findings, add the exact adversarial cases above, preserve the passing W05 suite and claim literal, then obtain a fresh independent contract review.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed.
- no implementation, test or orchestration edits: confirmed.
- no edits outside `allowed_paths`: confirmed; only this R2 report was created.

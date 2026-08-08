# Subagent return

## Task

- task_id: `W09-RESEARCH-CONTRACTS-02A-REVIEW`
- revision: `R5`
- objective: Independently verify the R4 scale-invariant normalization and controlled strict-result fixes, rerun every former attack, search for fresh P1/P2 contradictions, and issue a final shared-boundary recommendation.

## Files changed

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R5.md`

## Recommendation

- recommendation: **ACCEPT**
- highest open severity: **none**
- open finding count: **0 P1, 0 P2**
- Both R4 findings are resolved, every former R2/R3 attack remains closed, all fresh extreme-numeric attacks either produce reconciled correct output or a controlled boundary error, and the complete named parity suite passes 44 tests.

## R4 finding disposition

| R4 finding | Disposition | Independent executable evidence |
| --- | --- | --- |
| P1: subnormal cosine vectors violated scale invariance and explanation reconciliation | **RESOLVED** | Independently scored aligned query magnitudes `5e-324`, `1e-323`, `5e-323`, `1e-322`, `1e-320`, `1e-310`, `1e-308` and `1e-307` against `[1.0, 1.0]`. Every distance was either `0.0` or one rounding unit (`2.220446049250313e-16`), and every value exactly matched `1 + fsum(contributions)`. `stable_weighted_unit_components` uses a rescaled path when direct normalization is not reliable (`src/scouting/contracts/numerics.py:26-91`), and the scorer derives both score and terms from those components. |
| P2: strict result verification overflowed on scorer-valid large-finite cosine output | **RESOLVED** | Rebuilt the two-feature `[1e308, 1e308]` versus `[1.0, 1.0]` scorer output as strict `FeatureContribution`, `ResearchCandidate` and self-digested `ResearchQueryResult` objects. Validation completed without `OverflowError`. Scoring and result verification now share the same stable normalization primitive (`src/scouting/m0/scoring.py:115-170`; `src/scouting/contracts/research.py:835-878`). |

## Former attack disposition

| Former case | Final disposition | Fresh reconstruction against final state |
| --- | --- | --- |
| Exact minutes labeled `UNUSABLE_MINUTES` | **RESOLVED** | Rejected with controlled `ValidationError` containing `usable minute evidence`. |
| 2,996 referred players represented by one grain/decision | **RESOLVED** | Recomputed the canonical manifest digest after mutation; rejected by the per-referred-player grain lower bound. |
| One matrix row claimed two unique grains | **RESOLVED** | Recomputed the canonical manifest digest; rejected by matrix-grain reconciliation. |
| Zero referred players produced non-zero eligibility grains and an eligible row | **RESOLVED** | Recomputed the canonical digest after setting zero referred players and 3,603 no-lineup decisions; rejected because referred players and grains must be empty together. |
| Euclidean contribution contradicted a zero displayed contrast | **RESOLVED** | Rebuilt and re-digested the result; rejected by contribution/contrast reconciliation. |
| Exclusion count claimed a position filter that was absent | **RESOLVED** | Balanced result counts were rejected because position exclusions require a submitted filter. |
| Comparison bound the right grain to the wrong player | **RESOLVED** | Recomputed comparison, report and experiment bindings after player substitution; rejected by result-candidate identity binding. |
| `RESULT_MISMATCH` replay used a different query | **RESOLVED** | Recomputed the receipt digest; rejected because result mismatch requires an identical saved/replay query. |
| Invalid scorer method | **RESOLVED** | Rejected through `VectorScoringError`. |
| Negative-zero weight and emitted negative-zero term | **RESOLVED** | `-0.0` weight is rejected; a legitimate zero cosine term is canonical `0.0` and round-trips through strict `FeatureContribution`. |
| Large finite aligned cosine input silently returned distance 1 | **RESOLVED** | `[1e308, 1e308]` versus `[1.0, 1.0]` returns distance `2.220446049250313e-16`, contributions approximately `(-0.5, -0.5)`, and exact explanation reconciliation. |
| Finite feature contrast overflow | **RESOLVED** | Large-opposed Euclidean and cosine inputs fail through `VectorScoringError: feature contrast overflowed`, preserving the finite `FeatureContribution.scaled_contrast` boundary. |

## Extreme numeric and adjacent contradiction search

- **Subnormal and scale invariance:** all eight R4 magnitudes produce correct aligned cosine scores and reconciled explanations.
- **Zero vector:** `[0.0, 0.0]` versus `[1.0, 1.0]` returns distance `1.0` and zero contributions, with implied distance `1.0`.
- **Opposed vector:** `[1e308, -1e308]` versus `[-1.0, 1.0]` returns distance `1.9999999999999998` and implied distance equal to the returned value.
- **Huge finite weight:** query `[1e308, 1.0]`, candidate `[1.0, 1.0]`, weights `[1e308, 1.0]` returns distance `0.0`, contributions `(-1.0, 0.0)`, and exact reconciliation.
- **Zero-weight extreme dimension:** query `[1e308, 1e-308]`, candidate `[0.0, 1.0]`, weights `[0.0, 1.0]` returns the mathematically correct distance `0.0` and contributions `(0.0, -1.0)`. Fallback scale and division now consider only strictly positive-weight dimensions (`numerics.py:62-75`).
- **Aggregate overflow:** two finite Euclidean contributions near `1e308` fail through `VectorScoringError: Euclidean contribution sum overflowed`; an extreme finite cosine contribution projection fails through `VectorScoringError: cosine contribution sum overflowed`. `stable_finite_sum` translates `math.fsum` overflow into the shared controlled error (`numerics.py:13-23`; `scoring.py:134-167`).
- **Strict Euclidean overflow:** a finite `scaled_contrast=1e200` payload fails with a controlled Pydantic `ValidationError`, not raw `OverflowError`; finite aggregate overflow is likewise translated before result reconciliation (`research.py:804-833`).
- **Fresh contract search:** reread population/eligibility reconciliation, exact pins and digests, mode exclusivity, filter provenance, ranking uniqueness, explanation formulas, comparison/result identity, saved report/experiment bindings, replay state mapping, public exports and fixed claim literals. No remaining executable P1/P2 contradiction was established.

## W05 and boundary conclusions

- **W05 public-export compatibility: PASS.** Generic `FeatureValue`/`FeatureValueState` remain the M0 pair, explicit M0 aliases remain identical, and `ResearchFeatureValueState` remains the W09 enum.
- **W05 scorer/serving fixture parity: PASS.** The named suite passes all 44 tests, including W05 model and integration-serving checks. Stable helpers preserve the ordinary W05 arithmetic path and pinned fixture behaviour.
- **Strict numeric interoperability: PASS.** Large, subnormal, zero, opposed, huge-weight and zero-weight finite cosine cases reconcile; unsupported contrast, per-term and aggregate overflow exits through controlled scorer/contract errors; strict scorer-to-result large-finite construction succeeds.
- **W09 claim boundary: PASS.** Dataset, matrix/index, query, candidate, result and report surfaces retain `historical_resemblance_research_only`; matrix/index rows remain literal non-synthetic and limitations remain mandatory. No football relevance, recruitment usefulness, recommendation, current-market or G-RW4 claim was introduced.

## Checks run

- `uv run ruff check src/scouting/contracts/numerics.py src/scouting/contracts/research.py src/scouting/contracts/__init__.py tests/contracts/test_w09_research_contracts.py src/scouting/m0/scoring.py src/scouting/m0/core.py tests/unit/test_w09_scoring_kernel.py`
  - exit status: `0`
  - result: PASS — `All checks passed!`
- `uv run mypy src/scouting/contracts/numerics.py src/scouting/contracts/research.py src/scouting/m0/scoring.py src/scouting/m0/core.py`
  - exit status: `0`
  - result: PASS — no issues found in four source files.
- `uv run pytest -q tests/contracts/test_w09_research_contracts.py tests/unit/test_w09_scoring_kernel.py tests/unit/test_w05_m0_models.py tests/integration/test_w05_m0_serving.py`
  - exit status: `0`
  - result: PASS — 44 tests passed in 1.55 seconds.
- Independent local-only `uv run python -c` probes reconstructed both R4 findings, both R3 cases and every former R2 payload rather than invoking committed test functions. Additional probes covered zero, opposed, huge-weight, zero-weight, contrast-overflow, Euclidean aggregate-overflow, projected-cosine aggregate-overflow and strict-result construction. Each produced the correct reconciled output or the expected controlled error.
- `test -s reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R5.md`
  - exit status: `0`
  - result: PASS — the required R5 review artifact is non-empty.

## Artifacts/evidence

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R5.md`
- implementation reviewed: `src/scouting/contracts/numerics.py`, `src/scouting/contracts/research.py`, `src/scouting/contracts/__init__.py`, `src/scouting/m0/scoring.py`, `src/scouting/m0/core.py`
- tests reviewed: `tests/contracts/test_w09_research_contracts.py`, `tests/unit/test_w09_scoring_kernel.py`, plus the named W05 parity tests
- prior review: `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R4.md`

## Risks and follow-up

- residual P1/P2 risks: none established within this shared contract/scorer packet.
- follow-up: master may accept the shared W09 boundary and continue dependency-ordered W09 integration; later retrieval, artifact and UI packets still require their own acceptance evidence.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no dependency or lockfile changes: confirmed.
- no implementation, test or orchestration edits by this reviewer: confirmed.
- no edits outside `allowed_paths`: confirmed; only this R5 report was created.

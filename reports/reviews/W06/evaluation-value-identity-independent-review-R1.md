# W06 evaluation value/identity independent review — R1

## Verdict

**REWORK.** The fresh public-only review found **no P0 and one P1**. All named R3 and
packet master counterexamples now close, core metrics and intervals persist without a
lineage-dropping translation, and the accepted gate/population relation reproduced with
six expected accepts and 24 expected rejects. One normal persisted comparison shape is
still incomplete: `RankComparisonResult` accepts a computed Spearman value while the
entire top-k set-metric family is absent.

No protected expected output was opened, executed, or inferred.

## Finding

### P1 — A computed rank comparison may omit every required top-k set metric

A normal final constructor accepted this semantic shape (the preliminary
`model_construct` was used only to derive the canonical digest, as in the public test
convention):

```text
k = 1
left_input_digest  = aa...aa
right_input_digest = bb...bb
spearman = 1.0
overlap_count = overlap_rate = jaccard = candidate_churn = None
disagreements = ()
reason = None
result_digest = 54cb89310bf9d6feaa7d15cc608f6262adc947f762ddb23d49cfbffe21322231
```

The all-present/all-absent quartet check permits the all-absent branch independently of
Spearman availability. This shape is not produced by `rank_comparison`: the core either
returns all top-k set metrics (including when correlation is unavailable) or returns no
comparison values for insufficient `k`. The persisted contract can therefore certify a
computed comparison while silently dropping overlap, Jaccard, churn and the associated
disagreement arithmetic. That directly changes the persisted comparison result and its
content-addressed identity, so it is P1 under this packet's materiality rule.

Smallest bounded correction: when `spearman is not None`, require the set-metric quartet
to be present, then retain the existing valid shape where Spearman is unavailable but the
set metrics remain present. Add the exact normal-constructor regression above.

## Formula, identity and constructor matrix

| Family | Fresh public evidence | Adjudication |
|---|---|---:|
| Zero positives | Complete irrelevant top-1 produced `Precision@1 = 0/1 = 0.0`; Recall was unavailable with `no_eligible_relevance_denominator`; NDCG was unavailable; Coverage was `1/1 = 1.0`. | closed |
| Partial gain | Relevant + partial at `k=2` produced `(P,R,NDCG,Coverage)=(0.5,1,1,1)` when partial was excluded from P/R and `(0.75,1,1,1)` when included. | closed |
| Insufficient `k` | A one-candidate universe at `k=2` made all four ranking metrics unavailable with `candidate_universe_smaller_than_k`. | closed |
| Missingness | `UNJUDGED` and `ABSTAIN` each made all four ranking metrics unavailable with `incomplete_or_abstained_labels`; neither became zero gain. | closed |
| Tie policy | Wrong candidate-ID order at an equal score rejected with the tie-policy validator. | closed |
| Pair states | Correct, wrong, missing and explicit-abstention outputs had four distinct identities. Correct=`8e98c6c9...d575`, wrong=`8fe4d5fe...8497`, missing=`f44e7c86...273b`, abstained=`798b5986...639b`; missing and abstained retained their distinct reasons. | closed |
| Pair constructors | Predicted-without-candidate and abstained-with-candidate rejected. Protocol-rubric substitution rejected. | closed |
| Agreement | Reversing reviewer/evidence orientation retained identity `2de47d7e410f952e268f5fe6a3f4292ff438753f25fb00426e0e97108679c536`; rubric substitution rejected. | closed |
| Comparison identity | Insufficient-correlation comparison retained exact set metrics and digest `5febc678...786c`; changing only the left ranking produced `d6e35f05...3348`; swapping ordered left/right inputs produced `b3be0ecf...7ff3`. | closed |
| Comparison arithmetic | Spearman `2.0`, overlap `2` at `k=1`, wrong overlap rate, Jaccard, churn and disagreement cardinality all rejected. | closed |
| Comparison completeness | Computed Spearman with the full set-metric quartet absent validated as `54cb8931...231`. | **open P1** |
| Metric arithmetic | Negative sufficient statistics, zero denominator, a value outside `[0,1]`, and a computed reason all rejected. | closed |
| Interval arithmetic | Bounds outside `[0,1]`, a point outside its bounds, and a computed reason all rejected. | closed |
| Capability | `AGREEMENT` as a primary protected-bootstrap metric rejected at protocol construction. | closed |
| Core/persisted lineage | A fresh two-query bootstrap returned `MetricResult d4f001bd...7ca9` and `BootstrapInterval cf50ad2a...b674` with identical input lineage. A separate direct-run probe retained core identities `4e2c5a5b...22e0` and `d25e5f0f...542` unchanged in `EvaluationRun`. | closed |
| Child uniqueness | Duplicate slice metric semantic keys, duplicate failure semantic keys and duplicate slice IDs rejected; distinct slice children remained valid. | closed |
| Gate regressions | Fresh normal-constructor matrix matched all accepted R2 expectations: six accepts and 24 rejects, zero mismatches. | closed |
| Public fixture authority | SHA-256 remained `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`; `IMPLEMENTATION_FIXTURE_ONLY` and the non-human-expert claim notice were unchanged. | closed |

## Master-counterexample adjudication

| Packet counterexample | Fresh result | Severity |
|---|---|---:|
| Distinct comparison inputs collided at `4011d5fc...8350` | Closed: otherwise metric-equivalent inputs emitted distinct `5febc678...786c` and `d6e35f05...3348` identities. | none |
| Pair rubric substitution accepted at `cb4261e4...666` | Closed: normal core call rejected with the protocol-rubric error. | none |
| Core/persisted translations emitted `bc74844c` and `3f9f8a51` | Closed: core returns the persisted contracts directly; fresh run retained exact metric/interval digests, and the producer's stable `f021adec...562e` / `79322b61...003a` regression passed. | none |
| Spearman `2.0` validated at `07261866...7826` | Closed: rejected with `Spearman correlation must be within [-1, 1]`. | none |
| `overlap_count=2` at `k=1` validated at `6ca6259f...467` | Closed: rejected with `rank comparison overlap cannot exceed k`. | none |
| Computed reason validated at `f73f54f9...082` | Closed for both `MetricResult` and `BootstrapInterval`: computed reasons rejected. | none |

## Gate-regression matrix

The six expected accepts were coherent `ACCEPT_CLAIM`, coherent
`NARROW_APPLICABILITY`, linked-evidence `NO_GO`, both permitted missing-population
`NO_GO` reasons, and an exact protected subset of a mixed FIT/protected bundle. The 24
expected rejects covered all-/mixed-abstain positive decisions, zero relevance, foreign
slice/failure children, non-protected intrusion, protected omission, absent roster,
run/gate protocol substitution, bundle/candidate-manifest/access-bundle substitution,
access/result/interval population substitution, unsupported or interval-less primary
results, arbitrary/multiple missing reasons, and both orphan `NO_GO` shapes. There were
zero mismatches; no gate-population implementation was reopened.

## Commands and results

All Python/tool caches and bytecode were directed outside the repository.

| Command | Exit | Result |
|---|---:|---|
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | `11 passed in 0.20s`. |
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r1-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-value-identity-review-r1-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | All checks passed. |
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r1-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-value-identity-review-r1-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | No issues in three source files. |
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | Three contracts kept, zero broken. |
| `shasum -a 256 tests/fixtures/w06/public-evaluation-v1.json` | 0 | Pinned public digest reproduced exactly. |
| Public formula/pair/agreement/comparison inline constructor probe via `uv run --no-sync python - <<'PY' ... PY` | 1 | Reviewer probe had an incorrect expected overlap for one comparison after all preceding families passed; no implementation failure was inferred. |
| Corrected public comparison and master-constructor probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | All six impossible-arithmetic constructors rejected; the remaining incomplete-comparison identity `54cb8931...231` validated. |
| Public metric/interval/capability/core-lineage probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | All expected results and rejections matched. |
| Public gate regression probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | Six accepts, 24 rejects, zero mismatches. |
| Public direct-persistence/uniqueness probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | Core identities persisted unchanged; all duplicate attacks rejected. |

## Residual risks and correction

- Metric, interval, population, pair/agreement identity, child uniqueness and accepted
  gate-population risks are closed within this public review matrix.
- One comparison-identity risk remains: a persisted computed correlation can omit all
  required top-k set metrics and still receive a canonical digest.
- Public identities remain implementation evidence only; they make no protected,
  prospective or human-expert claim.

Smallest bounded correction: require the set-metric quartet whenever Spearman is
computed and add the exact `54cb8931...231` normal-constructor regression. No broader
comparison, applicability, null or gate change is indicated.

No Git operation, dependency/lock change, protected expected-output access,
external/provider access, implementation edit, or write outside the two authorized
review report paths occurred.

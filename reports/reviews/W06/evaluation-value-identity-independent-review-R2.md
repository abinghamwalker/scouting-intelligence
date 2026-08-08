# W06 evaluation value/identity independent review — R2

## Verdict

**ACCEPT — 0 P0, 0 P1.** The sole R1 P1 is closed. The exact formerly accepted
computed-Spearman preimage still derives digest
`54cb89310bf9d6feaa7d15cc608f6262adc947f762ddb23d49cfbffe21322231`, but its normal
`RankComparisonResult` constructor now rejects with
`computed Spearman requires top-k set metrics`.

The narrow correction did not change the accepted formulas, persisted identities,
unavailable shapes, lineage, gate population relation, applicability behavior, or public
claim boundary. The bounded R1 regression found no new P0 or P1. No protected expected
output was opened, executed, or inferred.

## Exact R1 P1 closure

The former witness was reconstructed independently with the same canonical fields:

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

The preliminary `model_construct` step was used only to derive the canonical digest;
the normal constructor rejected the payload with the new completeness error. The
validator first retains the existing all-present/all-absent quartet invariant, then
requires a present quartet whenever `spearman` is computed.

Both declared unavailable forms remain valid:

- Insufficient correlation retained `spearman=None`, the complete set-metric quartet
  `(overlap_count, overlap_rate, jaccard, churn)=(1, 1.0, 1.0, 0.0)`, reason
  `insufficient_correlation_intersection`, and digest
  `5febc6782ae9e260f943e22f682ed9e32947bc3f14f1e15956e8606b5d9d786c`.
- Candidate universe smaller than `k` retained `spearman=None`, no set metrics, no
  disagreements, reason `candidate_universe_smaller_than_k`, and digest
  `e1fc307ff1c24512752b66276d52a33211b58c6689531997f8a65d2a2a768b26`.

## Bounded R1 regression matrix

| Family | Fresh public evidence | Severity |
|---|---|---:|
| Former P1 | Exact digest `54cb8931...2231` rejected by the normal constructor with `computed Spearman requires top-k set metrics`. | none; closed |
| Ranking formulas | Zero positives retained Precision `0.0`, unavailable Recall/NDCG reasons, and Coverage `1.0`. Partial excluded/included retained `(0.5,1,1,1)` and `(0.75,1,1,1)`. | none |
| Insufficient and missing ranking inputs | Universe smaller than `k` retained the declared reason for all four metrics; `UNJUDGED` and `ABSTAIN` retained `incomplete_or_abstained_labels`. The focused tie-policy regression remained green. | none |
| Pair states and identity | Correct, wrong, missing and explicit-abstention results remained distinct. The accepted correct identity stayed `78250572322fbb52efdae3c2bf4a9214d4124f7b766c0a325aff98a9675ca515`; missing and abstention retained distinct reasons. Constructor and rubric-substitution tests remained green. | none |
| Agreement identity | Canonical orientation stayed `d20633a5ce1bd3377fec6109a2d09111d8d1e36c2d6a11f8ab9af2a262fbf1e4` in both directions; rubric substitution remained rejected. | none |
| Rank-comparison identity | Insufficient-correlation `5febc678...786c`, distinct-left `d6e35f05...3348`, and ordered-swap `b3be0ecf...7ff3` stayed distinct. A complete computed comparison remained valid at `e24c41c8...6af9`. | none |
| Comparison arithmetic | Spearman outside `[-1,1]`, overlap greater than `k`, and the exact incomplete computed shape rejected in focused tests; the retained complete/unavailable forms matched core output. | none |
| Metric and interval constructors | Negative sufficient statistics, invalid ratios and bounds, computed reasons, unsupported primary capability, and lineage substitutions all remained rejected. | none |
| Direct persistence and lineage | Direct core `MetricResult` stayed `f021adec1d57a5f54eec235273a66ef6a0a6665599c56cc7843169f0b0cb562e`; `BootstrapInterval` stayed `79322b611e83d790af4052a63225d0cbe82c878d04c1ffda07e7fbef7ac1003a`. Both persisted unchanged through `EvaluationRun`, with identical input lineage. | none |
| Child uniqueness | Duplicate slice/failure children and foreign slice/failure population children remained rejected by the focused contract suite. | none |
| Gate population | Six R1 accepted shapes reproduced: both positive decisions, linked-evidence `NO_GO`, both permitted missing-population `NO_GO` reasons, and an exact protected subset of a mixed FIT/protected bundle. A bounded 15-case reject set covered all-/mixed-abstain and empty-evidence positive decisions, population intrusion/omission, protocol substitution, arbitrary/multiple missing reasons, both orphan `NO_GO` shapes, interval-less primary output, and result/interval population substitutions. Zero mismatches. | none |
| Public fixture and claim | SHA-256 remained `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`; `IMPLEMENTATION_FIXTURE_ONLY` and the non-human-expert notice were unchanged. | none |

## Commands and results

All Python/tool caches and bytecode were directed outside the repository.

| Command | Exit | Result |
|---|---:|---|
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r2-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | `11 passed in 0.16s`. |
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r2-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-value-identity-review-r2-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | All checks passed. |
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r2-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-value-identity-review-r2-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | No issues in three source files. |
| `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r2-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | Three contracts kept, zero broken. |
| Public inline R2 digest/formula/identity/lineage/gate probe via `UV_CACHE_DIR=/private/tmp/w06-value-identity-review-r2-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python - <<'PY' ... PY` | 0 | Exact P1 rejection; both unavailable forms valid; pinned identities unchanged; formula matrix matched; six gate accepts and 15 bounded rejects with zero mismatches. |
| `shasum -a 256 tests/fixtures/w06/public-evaluation-v1.json` | 0 | Pinned public digest reproduced exactly. |
| `test -s reports/reviews/W06/evaluation-value-identity-independent-review-R2.md` | 0 | Review report exists and is non-empty. |
| `test -s reports/reviews/W06/returns/W06-EVAL-VALUE-IDENTITY-REVIEW-03-R2.md` | 0 | Mandatory return exists and is non-empty. |

## Residual risks and correction

- No remaining metric-value, interval, pair/agreement/comparison identity, constructor,
  lineage, gate-population, applicability, or claim defect was found in the bounded
  public matrix.
- This remains public implementation evidence only; it makes no protected, prospective,
  or human-expert claim.
- Smallest bounded correction: **none**.

No Git operation, dependency/lock change, protected expected-output access,
external/provider/credential access, implementation edit, or write outside the two
authorized R2 report paths occurred.

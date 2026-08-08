# W06 evaluation robustness independent review — R6

## Verdict

**REWORK — 0 P0, 1 P1.** R6 has one live ranking metric/bootstrap formula path,
and independent public probes reproduced parity across the declared metric, status,
score, ordering, population, resampling and identity boundaries. All three original
numeric-child parents also still reproduce and reject under normal construction.

The remaining P1 is committed regression completeness. None of the three mandated
parent digests occurs anywhere under `tests/`. The current R5-named mutation test uses a
split-stress comparison rather than the original metadata-control comparison, changes
only a split interval resample digest rather than reconstructing the original split
aggregate/interval substitution, and never asserts any of the three exact parents. The
metadata aggregate mutation has the original substitution shape, but its parent identity
is likewise not pinned. Therefore the exact recurrence witnesses can silently drift or
disappear while the focused suite remains green.

No P0 is assigned: all evidence used was public and implementation-only, applicability
remains `UNSUPPORTED`, governed-pair evidence remains absent, and no protected or
positive empirical decision is created.

## P1-1 — The three original parents are rejected at runtime but absent from committed tests

The review packet requires literal reconstruction, identity pinning and normal-constructor
rejection for:

- `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb`;
- `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815`;
- `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404`.

`rg` across `tests/` found none of those literals and exited `1`. The focused suite still
passes `19/19`, proving that it does not enforce the mandated identities. The relevant
test at `tests/unit/test_w06_robustness.py:319` constructs different witnesses and makes
no parent-digest assertion.

This is one P1 test-completeness defect, not three findings: runtime validation closes
the common numeric-child substitution class, but the three original recurrence witnesses
are not durably identity-pinned.

## One-core call-path matrix

| Surface | Exact live path | Outcome |
|---|---|---|
| General per-query metrics | `core.evaluate_ranking` → `core._ranking_calculation` → `evaluation_calculations.derive_ranking_metric_children` | Shared calculation owns all four per-query values, statuses, sufficient statistics and digests. |
| General aggregate/bootstrap | `core.bootstrap_interval` → `core._ranking_calculation` → `evaluation_calculations.derive_ranking_metric_children` | Shared calculation owns aggregate mean, input identity, seeded samples, resample identity, percentile indexes/bounds and interval identity. |
| Stress production | `robustness._cohort` → `contracts.evaluation.derive_ranking_metric_children` → shared calculation | Contract function only converts persisted rows and wraps primitive payloads. |
| Control production | `robustness.evaluate_control` baseline/null → contract adapter → shared calculation | Both control metric branches use the same owner. |
| Stress validation | `StressTestResult.valid` → contract adapter → shared calculation → exact full-child equality | Re-signed numeric substitutions reject. |
| Control validation | `DeterministicControlResult.valid` → contract adapter → shared calculation → exact result equality | Re-signed aggregate substitutions reject. |
| Rank comparison | general, stress/control production and validators → `derive_rank_comparison` | Separate comparison concern retains one live formula owner. |

The only ranking metric/bootstrap formulas, missing/insufficient decisions, aggregate
mean, bootstrap RNG, sample sorting, percentile selection and resample/interval digest
construction are in `src/scouting/contracts/evaluation_calculations.py:89`. General
adapters enter at `src/scouting/evaluation/core.py:169`; persisted adapters enter at
`src/scouting/contracts/evaluation.py:1549`; stress/control validators re-enter that
adapter at lines 1806 and 2292. Source tracing found no second metric/bootstrap formula
body.

## Boundary matrix

| Boundary | Independent public reproduction | Disposition |
|---|---|---|
| Four metrics | Precision, recall, NDCG and coverage matched exact per-query, aggregate and interval identities on general, persisted and primitive surfaces. | PASS |
| Partial relevance off/on | Eight metric/configuration cases matched exactly with `partial_counts_for_precision_recall=False` and `True`. | PASS |
| Zero denominator | Recall returned `no_eligible_relevance_denominator`; NDCG returned `no_eligible_ndcg_denominator`; both propagated `insufficient_query_metric` to aggregate and interval. | PASS |
| Insufficient population | General and persisted rows shorter than `k` returned `candidate_universe_smaller_than_k`, then unavailable aggregate/interval children. | PASS |
| Missing/abstained labels | General and primitive paths returned `incomplete_or_abstained_labels`; persisted implementation-fixture `RankedObservation` rejected `ABSTAIN`, which is its declared representability boundary. | PASS |
| Canonical ties/order | Candidate-ID ordered ties were accepted; reversed candidate-ID ties rejected on both general and persisted adapters. | PASS |
| Integer/float scores | General integer-valued scores and persisted float-normalized scores produced the same per-query, aggregate, input, resample and interval identities. Aggregate input was `7226ec9e27ac604ac545d478c14a7316446e3c2a50feb3be161f6ff82a9ae616`; resample identity was `1214baf63da149ea318ff4e0ff693dedaa5f8e698a5ad68a409d28c695888825`. | PASS |
| Seed/resamples/bounds | Shared protocol settings yielded identical resample and interval identities and exact bounds `1.0, 1.0` in the representation probe. | PASS |
| Undeclared `k`/metric | General and persisted adapters rejected `k=999`; primitive and general bootstrap surfaces rejected unsupported pair-preference bootstrap. | PASS |
| Query population | Shared calculation sorts query IDs and rejects empty or duplicate query populations; owning persisted validators bind the resulting exact query roster. | PASS |

The committed parity regression at `tests/unit/test_w06_evaluation_metrics.py:188`
directly covers all four metrics, integer/float canonicalization and undeclared `k` on
one partial-on row. The broader boundary matrix is also guaranteed by the single shared
calculation and was independently executed here. It does not cure the separate literal
three-parent test gap.

## Exact three-parent evidence

| Original witness | Reconstructed children | Exact parent | Normal-constructor result | Committed literal test |
|---|---|---|---|---|
| Metadata comparison, Spearman `-0.19999999999999996 → 0.0` with inputs retained | comparison `2202faddee618ff386a32da44c294d2cf88adc0c2540d9c2dd4bd463aeb9a0cd` | `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb` | **REJECT** — `control comparison values must equal canonical derivation` | **ABSENT** |
| Metadata baseline aggregate `1.0 → 0.0`, numerator `1.0 → 0.0`, input retained | metric `212ab5780f43435150de689f8ce5b143c40f841006d2069be8edf7bcd48f8a4b`; input `4d78956709bc04c45f22dc2ea720b1fbe202335fcf760ce3f210f3f4eeb437ba` | `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815` | **REJECT** — `control metric values must equal canonical derivation` | **ABSENT** |
| Split aggregate `1.0 → 0.0`, numerator `2.0 → 0.0`, interval point retained/relinked, comparison cohort links re-signed | metric `ca55b6e60f5cb044aa3d06fe2bac0b94a0e47de9887353a8c9c0edb7d97e27e7`; interval `a90cba591c09f8b055c95b858f9e2c718ec2d8223b6eb867f347e70c9860fd7c`; cohort `1f420a7fc6333c9a80525c45628130ab8e5ce028b642e774ed0967474d5975fe` | `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404` | **REJECT** — `stress metric and interval values must equal canonical derivation` | **ABSENT** |

## Fixture and retained result identities

Fixture bytes remain unchanged:

- evaluation: `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`;
- robustness: `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.

The eight computed stress identities remain, in enum order:

1. `2fcdf6fdaa56e2a39214dcb213112aca6446ecd15503edb0c5b646c7508c8725`
2. `f8816750f185201090bf4a9e9dbd091f2a72bb24c0c111b182418e8b30414967`
3. `f9b29f502ca81aa718b4f9c2a6a9ec3e955600e208536ee9e263aa3568ebf5f0`
4. `f608776240d1029e8c4e86eb1334d2e9e664fc6fbfbc645709d20fe308610d0a`
5. `f81ada5992650905a8cdee5133ee638dc195b630bb47f6e881a80b872fb119a2`
6. `adc824c2995bc0583d17bb3236670b3dcacdcbbfd4296b60205b92434894875f`
7. `add8d26951c7db8c4124c8bb2bca4a8a51e4b687d9f722e7d318ce9b9e24fc78`
8. `d497ed6c4c1ec7613f6a04108c7f54174ff056503e7662c2c4e8c263433a18d6`

Sparse unsupported stress remains
`26e98b12c1617910404bfa4b4bab476a96d4d10e639d7bff6c38993ec54e6f2a`,
with deficits `340060f54bc16051582fa974e2c4130e952725a4ab94e9641f2263576be9069c`
and `c06d34b21f9aed971890da807e18c75290abd310b5262dcf16fe3baef3453a2e`.
All five public control input/result identities matched the fixture; the shuffled-label
permutation remained `a67bc397e88b775678aaae6009e950ce60a3365de661128afa6fe3feae019585`.

## Commands and results

All Python commands used `uv run --no-sync`, `PYTHONDONTWRITEBYTECODE=1`, a task-local
`/private/tmp` uv cache and only public fixture data.

| Command | Exit | Result |
|---|---:|---|
| Complete reads of the R6 review packet and every `read_first` path | 0 | All required authorities read fully before adjudication. |
| Focused four-file pytest command | 0 | `19 passed in 0.27s`. |
| Packet ruff command | 0 | All checks passed. |
| Packet mypy command | 0 | No issues in 5 source files. |
| `uv run --no-sync lint-imports` | 0 | 3 contracts kept, 0 broken. |
| Packet two-fixture `shasum -a 256` | 0 | Exact fixture identities above. |
| Call-site/formula `rg` trace | 0 | One live metric/bootstrap formula body and thin caller paths reproduced. |
| Public boundary probe | 0 | All boundary outcomes in the matrix reproduced. |
| Exact three-parent constructor probe | 0 | All exact parents reproduced; all rejected with their owning canonical-derivation error. |
| Literal-parent `rg` over `tests/` | 1 | No mandated digest occurs in committed tests. |
| Public result identity probe | 0 | Eight stress results, sparse deficits, five controls and permutation remained stable. |

## Smallest bounded correction

Add one public regression that reconstructs the original metadata comparison, metadata
aggregate and relinked split aggregate/interval substitutions; assert each exact parent
digest literally before asserting the current normal-constructor rejection message.
No formula, contract, fixture, identity semantics or production code change is needed.

Remaining P0 risk: **none identified**. Remaining P1 risk: **one**, the missing literal
three-parent recurrence coverage above.

No Git operation, delegation, dependency/lock change, source/test/orchestration edit,
protected expected-output access, external/provider/credential access, model tuning or
write outside the two authorized report paths occurred.

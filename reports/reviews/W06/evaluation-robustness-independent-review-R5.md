# W06 evaluation robustness independent review — R5

## Verdict

**REWORK — 0 P0, 1 P1.** All three exact R4 numeric-child parents now reject
under normal construction, but R5 does not satisfy the controlling requirement for one
reusable deterministic metric/bootstrap core. The general evaluation API still executes
the complete formulas in `core.evaluate_ranking` and `core.bootstrap_interval`, while
robustness production and validation execute a second complete implementation in
`contracts.evaluation.derive_ranking_metric_children`.

Comparison derivation is consolidated: general `rank_comparison`, stress production,
control production, and both owning validators all call `derive_rank_comparison`.
Metric and bootstrap derivation is not consolidated. The two paths currently return
exactly equal children on the shared, float-normalized supported domain exercised by a
16-case public parity probe, but they are independently editable and already disagree at
their input boundary. The general path rejects undeclared `k`; the second derivation
accepts `k=999` and emits unavailable metric/interval children. A `RankedItem` with integer
scores is accepted by the general path, while robustness normalization to
`RankedObservation` changes the canonical input identity from
`45844bf1a49500f88d79d3b4ea9526ceb8aff439f6c0e0d7e46f9b5bbfbd34fc` to
`a634aa694138c9333e9956172d6160b574fc2cc77d7c8ededaa7bfcdda2bb530`.
That is direct evidence of two live authorities, not merely a hypothetical refactor
concern.

No P0 is assigned because the evidence remains public implementation-only,
applicability remains `UNSUPPORTED`, governed pair evidence remains absent, and no
protected or positive empirical decision is created.

## P1-1 — General evaluation and robustness retain two live metric/bootstrap formulas

The general public API exports `evaluate_ranking` and `bootstrap_interval`
(`src/scouting/evaluation/__init__.py:9-10`). `evaluate_ranking` independently derives
precision, recall, NDCG, coverage, incomplete-label behavior, sufficient statistics and
metric digests (`src/scouting/evaluation/core.py:162-285`). `bootstrap_interval` calls
that implementation and independently derives aggregate values, deterministic resamples,
percentile bounds, resample identity and interval identity
(`src/scouting/evaluation/core.py:287-405`). These functions are live in the focused
contract and unit suites and remain the development/protected/future evaluation surface.

R5 added another full implementation in the contract module. It independently derives
the same per-query values and statuses, aggregate metric, random resamples, percentile
bounds and all child digests (`src/scouting/contracts/evaluation.py:1542-1613`). Stress
production calls it at `src/scouting/evaluation/robustness.py:104-106`; control production
calls it twice at lines 350-355. Stress validation calls it at
`src/scouting/contracts/evaluation.py:1825-1835`, and control validation calls it at
lines 2302-2306. Thus robustness producers and validators agree with one another, while
the general core remains a distinct live authority.

This fails the R5 convergence rule and the user-authorized single reusable metric
implementation criterion even though current float-normalized results match. A future
formula, denominator, missingness, seed, resample, percentile or identity correction can
land on either path alone and make general/protected evaluation diverge from robustness
evidence.

The comparison surface is different and is now one live path. The sole complete formula
is `derive_rank_comparison` (`src/scouting/contracts/evaluation.py:1497-1540`). General
`rank_comparison` delegates to it (`src/scouting/evaluation/core.py:445-449`), robustness
producers call it (`src/scouting/evaluation/robustness.py:143-149,359-366`), and stress
and control validators call it (`src/scouting/contracts/evaluation.py:1810-1817,
2328-2337`). The unused `_comparison` helper at `core.py:411-442` has no caller and does
not form a second live formula path, although it should be removed with the consolidation.

## Exact three-witness outcomes

| Witness | Exact reconstructed substitution | Re-signed child evidence | Exact parent | R5 normal-constructor outcome |
|---|---|---|---|---|
| Metadata comparison | Spearman `-0.19999999999999996 -> 0.0`, left/right inputs retained | comparison `2202faddee618ff386a32da44c294d2cf88adc0c2540d9c2dd4bd463aeb9a0cd` | `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb` | **REJECT**, `control comparison values must equal canonical derivation` |
| Metadata control aggregate | baseline aggregate `1.0 -> 0.0`, numerator `1.0 -> 0.0`, input `4d78956709bc04c45f22dc2ea720b1fbe202335fcf760ce3f210f3f4eeb437ba` retained | metric `212ab5780f43435150de689f8ce5b143c40f841006d2069be8edf7bcd48f8a4b` | `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815` | **REJECT**, `control metric values must equal canonical derivation` |
| Split stress aggregate/interval | aggregate `1.0 -> 0.0`, numerator `2.0 -> 0.0`, input `2fe3afe03310ecd0a52e3e98c266fed3674bf5f1dbb49190cf3d41b7a00746da` retained; interval point remains `1.0` and is re-linked | metric `ca55b6e60f5cb044aa3d06fe2bac0b94a0e47de9887353a8c9c0edb7d97e27e7`; interval `a90cba591c09f8b055c95b858f9e2c718ec2d8223b6eb867f347e70c9860fd7c`; cohort `1f420a7fc6333c9a80525c45628130ab8e5ce028b642e774ed0967474d5975fe` | `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404` | **REJECT**, `stress metric and interval values must equal canonical derivation` |

The R5 regression named `test_r5_recomputed_numeric_children_reject_at_normal_construction`
does not itself pin all three exact parents. Its comparison case mutates a split-stress
parent rather than exact metadata-control parent `fa8...`; its stress case mutates the
interval resample digest rather than reconstructing exact aggregate/interval parent
`2e70...`; and it asserts no parent identities. The implementation return's statement
that `2e70...` is the interval-resample substitution is therefore inaccurate. The
independent probe above reconstructs and rejects the mandated original three parents.
This is retained under P1-1 because exact regression evidence and the duplicate formula
authority are part of the same incomplete convergence correction.

## Semantics, fixture and retained closure evidence

The public parity probe compared both live metric/bootstrap implementations across all
four rank metrics, both partial-relevance counting settings, zero-relevance denominators,
short candidate populations, aggregate values, bootstrap seed/resamples, resample
digests and percentile bounds. All 16 shared-domain cases were exactly equal when scores
were normalized floats. General missing/unjudged labels returned only
`incomplete_or_abstained_labels`; robustness `RankedObservation` rejected abstained
fixture labels. Both surfaces rejected a noncanonical candidate-ID tie order. These
current results do not cure the two-authority defect.

Fixture byte identities remain:

- evaluation: `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`;
- robustness: `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.

The eight computed stress result identities remain, in enum order:

1. `2fcdf6fdaa56e2a39214dcb213112aca6446ecd15503edb0c5b646c7508c8725`
2. `f8816750f185201090bf4a9e9dbd091f2a72bb24c0c111b182418e8b30414967`
3. `f9b29f502ca81aa718b4f9c2a6a9ec3e955600e208536ee9e263aa3568ebf5f0`
4. `f608776240d1029e8c4e86eb1334d2e9e664fc6fbfbc645709d20fe308610d0a`
5. `f81ada5992650905a8cdee5133ee638dc195b630bb47f6e881a80b872fb119a2`
6. `adc824c2995bc0583d17bb3236670b3dcacdcbbfd4296b60205b92434894875f`
7. `add8d26951c7db8c4124c8bb2bca4a8a51e4b687d9f722e7d318ce9b9e24fc78`
8. `d497ed6c4c1ec7613f6a04108c7f54174ff056503e7662c2c4e8c263433a18d6`

Sparse unsupported stress remains
`26e98b12c1617910404bfa4b4bab476a96d4d10e639d7bff6c38993ec54e6f2a`
with deficits `340060f54bc16051582fa974e2c4130e952725a4ab94e9641f2263576be9069c`
and `c06d34b21f9aed971890da807e18c75290abd310b5262dcf16fe3baef3453a2e`.
All five control input/result identities and permutation identity remain equal to the
public fixture and R4 review. The focused suite retains the R3 row/authority closures,
typed incoherent/common-candidate deficits, governed-pair absence, applicability,
failure retention, partial, missing-label and tie checks.

## Commands and results

All Python probes used `uv run --no-sync`, `PYTHONDONTWRITEBYTECODE=1`, public fixture
data and task-local `/private/tmp` caches. No protected expected output was accessed.

| Command | Exit | Result |
|---|---:|---|
| complete reads of the R5 review packet and every direct `read_first` path | 0 | required authorities read fully before adjudication |
| `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | `18 passed in 0.22s` |
| `uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | all checks passed |
| `uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | no issues in four source files |
| `uv run --no-sync lint-imports` | 0 | three contracts kept, zero broken |
| packet two-fixture `shasum -a 256` | 0 | exact fixture identities above |
| exact three-parent public constructor probe | 0 | all exact parent digests reproduced; all reject with the owning canonical-derivation error |
| call-site `rg` trace | 0 | one live comparison path; two live metric/bootstrap formula paths |
| public metric/bootstrap overlap and boundary probe | 0 | 16 normalized cases equal; undeclared-`k` and integer-score lineage differences reproduced |
| public fixture identity execution probe | 0 | eight computed stress, sparse deficits, five controls and permutation remain stable |
| `test -s reports/reviews/W06/evaluation-robustness-independent-review-R5.md` and `test -s reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R5.md` | 0 | both mandatory reports present and non-empty |

## Smallest bounded correction

Make the general core the sole owner of ranking metric and bootstrap formulas, or move
one canonical implementation into a dependency-safe pure module and make both general
evaluation and contract validators call it. Remove the complete formula body from the
other path, retain only representation conversion and equality checks, remove unused
comparison construction helpers, and add literal assertions for all three mandated
parent digests using their original substitutions.

Remaining P0 risk: **none identified**. Remaining P1 risk: **one**, the live duplicate
metric/bootstrap implementation and incomplete exact regression evidence described
above.

No Git operation, delegation, dependency/lock change, implementation edit, protected
expected-output access, external/provider/credential access, model tuning, or write
outside the two authorized report paths occurred.

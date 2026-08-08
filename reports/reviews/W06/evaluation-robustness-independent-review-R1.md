# W06 evaluation robustness independent review — R1

## Verdict

**REWORK — 0 P0, 7 P1.** The implementation is deterministic in the narrow sense that
identical inputs reproduce identical digests, and all accepted W06 core regressions stay
green. It does not implement the declared robustness experiment. Every computed stress
kind ultimately bootstraps the unchanged full row population, retains no partition or
comparison evidence, and can therefore label a non-experiment `COMPUTED`. The failure
register, applicability assessment, stress specification/result and controls also retain
caller-asserted or unbound state that opens every master counterexample.

No P0 was assigned because the fixture applicability state is still forced to
`UNSUPPORTED`; the defects do not by themselves construct a positive empirical claim.
They are P1 because their results can enter later gate evidence while claiming stress,
null, transfer or population behavior that did not occur.

This review used public fixtures and fresh public inline objects only. No protected
expected output was opened, executed, inferred or relabelled.

## Findings

### P1-1 — Every computed stress kind scores the unchanged full population

`evaluate_stress_test` counts groups or thresholds at lines 126–166, then all eight kinds
converge on the same call at lines 169–171:

```text
bootstrap_interval(protocol, tuple(item.row for item in selected), specification.k, specification.metric)
```

There is no half evaluation, window evaluation, threshold-specific population, train/test
split, leave-group population or comparison. The returned `StressTestResult` at lines
174–182 omits `comparisons`, so the default empty tuple is accepted. On a six-query public
probe, all eight results had metric input digest
`fbe0e51f77387270f27cb7ba3b8f5f65b499b632a4162169f6f865b6222a7afe`,
value `0.5`, denominator `6.0` and `comparisons=0`.

This also leaves the split-half master identity
`c1cbcf5b1968e11aa6473c9ca9a914b487c96a841fd7233d425ade298db3f177`
**OPEN**. A fresh semantic reproduction with four distinct queries and one ranking row per
query returned `COMPUTED`, value `0.5`, denominator `4.0`, zero comparisons and result
digest `66cbe9d4882755ee760839061da8bdc82a2e1c3fa41a6f9459d3821ba75c6902`.
The implementation treats four queries as four observations instead of enforcing four
eligible observations within every declared evaluated unit.

Chronology and minima are also only global counts. The computed probe included
`windowa` indices `0` and `100` and later `windowc` indices `50` and `60`; walk-forward
still computed because the check compares only `min(first_window) < max(last_window)`.
Minutes thresholds `(45, 90)` had only two rows at the higher threshold, yet the returned
metric still had denominator `6.0`. Leave-group results likewise kept all six rows.

### P1-2 — Source comparison never computes the governed candidate intersection

For `intersection_only_source_comparison`, lines 153–161 require only two distinct
provider IDs. Lines 162–166 report `exact_candidate_intersection=0` only when `selected`
is empty, but a valid `GovernedPopulationInventory` requires at least one member and
`_rows` requires the rows to equal it. The declared deficit is therefore unreachable for
a valid call. No provider-to-candidate roster is represented or intersected.

The master identity
`f0f0afb88df883815037246a21e3ae384eb461c0b7286c9e18100c627bd15cca`
is **OPEN**. A fresh two-provider reproduction used candidate universes
`{alpha,beta}` and `{delta,gamma}`; their intersection was empty, yet the function returned
`COMPUTED`, precision `1.0`, `comparisons=0`, and result digest
`0dc3d3a6f2bccdda1f26f7528e084e250fc71624ff15433b9ef4d2b1b6262510`.

### P1-3 — Controls reject real rank order and the nulls shuffle candidates

Lines 195–198 require each ranking sequence itself to equal alphabetical set order. A
valid score order `("beta", "alpha")` is rejected with
`control inputs must be canonically ordered and unique`. Lines 201–206 then implement
both `shuffled_label` and `shuffled_pair` by shuffling the challenger candidate IDs.
There are no labels or pair outcomes in the API to permute, and the three non-null
controls receive no coverage, metadata or raw-vector evidence at all.

With seed `17` and candidates `(alpha,beta,delta,gamma)`, both shuffled kinds produced
the identical candidate permutation `(alpha,delta,beta,gamma)` and identical comparison
digest `32cbafb4333c788a7c9b694c63211604252d3abfcc5a4d980f0e9863784b6551`.
This proves neither declared null. Coverage, metadata and raw Euclidean all produced the
same unchanged-ranking comparison digest
`8bb8bd3842f7598aa1a6e7a00b11237373c26660544d06e8128643459288ebd1`.

### P1-4 — Stress specifications/results are not bound to the frozen protocol or inventory

`StressTestSpecification` validates threshold shape and its own digest only (contract
lines 1214–1239). It accepts metrics outside the accepted ranking capability and any
positive `k`; an agreement-at-999 semantic reproduction was accepted with digest
`e8261a80778f461e3bdf49ee71517a2f59f177f637e0b1c9b468fb3410540ecf`
against protocol `90b2603b...70f07`, whose declared k is `(1,2,3)` and whose roster is
precision/recall/NDCG/coverage. Thus master specification identity
`6599b30a7fb0334dc64c7001de9abc2a8722a1bcce86f91cb7557f74199bf42b`
is **OPEN**.

The executor compares protocol digests but never compares
`specification.inventory_digest` with `inventory.inventory_digest`. A specification with
inventory digest `aa...aa` and actual inventory
`bacf2d6cef4ae014f349350d3145b76cc6f8e7a2da0bca33b1e2d9a5bef80a1c`
was accepted and returned `COMPUTED`; specification digest
`cdf99a992ea92c3179957d9047da678bfac2d025157823cc7aa0cddba54f0e44`,
result digest `a48165bece4f6e8789f79a99ecb66e1946fef822fbb8d47d0300ce302bc10cdf`.

`StressTestResult` (lines 1242–1283) also does not bind its interval to its metric result,
or either child to the specification's protocol, inventory, metric or k. It explicitly
allows an empty comparison tuple for every computed kind.

### P1-5 — Failure registers do not bind the full source population

`FailureCaseRegister` receives only retained cases, a caller count and shortfall. Lines
1338–1340 validate arithmetic against the caller count but have no source-population
digest or complete-case digest. The exact master constructor reproduced:

```text
register_digest  = 31f5ab91dafe4377b5ec94b837a2cb01634e4d0883405ed25d39ee90abb99056
retained_cases   = 10
total_case_count = 100
shortfall        = 0
```

Only `case0` through `case9` were supplied. The claimed omitted ninety cases—and whether
they include worse severities—are unbound. `register_failures` is sound only when its
caller has already supplied the complete population; the persisted contract cannot prove
that premise.

### P1-6 — Applicability trusts a caller assertion instead of stress/control results

`assess_applicability` accepts only an inventory and boolean
`mandatory_transfer_supported` (lines 243–249). It receives no stress/control results and
does not inspect the one-competition/team/provider/window inventory. The exact master
witness reproduced: for inventory
`c8c0f26e1a41b84015eacb0aa3f05cf731f12d195cf216b905cf796818875479`,
passing `True` produced assessment
`ed497952ab334aeac02d2f0f7e513e78fa31137a458583353cdade96b5ca31e2`
with only `MISSING_EXPERT_RELEVANCE_EVIDENCE`; the exact mandatory transfer deficit was
suppressed.

### P1-7 — The public fixture and focused tests do not exercise the declared layer

The public robustness fixture digest is
`3faba3693b28c887b0d411f0ac300fbfb166a1230727c06eeb319095ca26c549`,
but its only data is the strings `deterministic-control` and
`unsupported-provider-transfer`. It contains no ranking, population, partition, control,
failure or applicability input. Neither robustness test file contains a call to
`evaluate_stress_test` or `evaluate_control`; `rg` returned zero matches. The unit test
checks only that the fixture SHA is nonempty rather than equal to the producer's claimed
pinned digest. This explains why all 14 focused tests pass while every computed stress
semantics remains absent.

## Exact stress matrix

The computed column used one six-query public population with three windows, two
competitions, teams and providers, and thresholds `(45,90)`. Every computed row had value
`0.5`, denominator `6.0`, zero comparisons and the identical full-population input digest
`fbe0e51f...22a7afe`. The unsupported column used one query at 50 minutes.

| Stress kind | Computed result digest | Computed behavior | Unsupported result digest | Exact unsupported conditions |
|---|---|---|---|---|
| split half | `7b3105a62b26499705ad6a29da2f842bc309511294728138dd06daa79e9829d7` | unchanged 6 rows | `978c931135c8f3a893a3e2a590cc686063edd2c79b5f45bf2917df5098dc567f` | `deterministic_halves_non_empty=false`; `eligible_observations=1<4` |
| rolling window | `1332a304739b43a581f20312756f5756e2e4ba5bdaaf38a1f2c739b867e16bc2` | unchanged 6 rows | `a6da80ba3689cae689df31c464dcdae76f1b32bec4cbb638b04efb3b6561c7ac` | `distinct_chronological_windows=1<3` |
| minutes/sample | `e905b908c07e5e55337a39f2392aa26beba9053c2d76a77ae91e566bc5769a3b` | unchanged 6 rows, including below-threshold rows | `96484963b7375b58408381ae9756c20edf99436160978315ea58aedf63a5823a` | `minutes_threshold=90:eligible_observations=0` |
| walk-forward | `f798728de444d38cbcc08b0f38131dbd8a5c814acda5f69c79ef58eff0b9dc8d` | unchanged 6 rows; overlapping chronology accepted | `e73c9b53db355ac4b58c6be401888174e4ae50bbde40d85170e3d24ba29f9b4b` | `distinct_chronological_windows=1<2` |
| leave competition out | `d4eedf4f4cf929ccea52cee4c84c7af639e87d8ec6bdef5e30d06c1b95df08df` | no competition left out | `4ac4669acc2db96b92931497768951993c8b5bdc1707a04d37c865567895218d` | `distinct_competitions=1<2` |
| leave team out | `d0ae624f4f097ef17d3f0e8c7b8557d6d10228a240f7da737e80e475d6fad528` | no team left out | `c04070665bae4cb0b8a6b22d3783fb978e1c2c480ec5cb6da6c537a4efac289c` | `distinct_teams=1<2` |
| leave provider out | `1524f9c40cf93c86e9e56a2297469d3f8c6d34abe83de04cd5694717213d220c` | no provider left out | `2478e460709b29e0c277c9cb2795b5b5e0bcb662b81be0eff0672d3bc7dab17e` | `distinct_providers=1<2` |
| intersection-only source | `ccae405b7d897aa48943f48f2ecd6fd8c96bf81cc2a88597d56b8d0531544e03` | no candidate intersection | `92f57f8f8599d089cc821ff4377c24416a0dae781cd874944755b35e2a9bf438` | `distinct_providers=1<2`; zero-intersection deficit unreachable |

## Exact control matrix

| Control | Control digest | Permutation | Comparison evidence |
|---|---|---|---|
| coverage only | `546b99d34580bc7f9114f2596cd302230ba63c08662691d6cde0d79a1364146f` | none | unchanged comparison `8bb8bd38...88ebd1` |
| metadata | `f424b83de531b6a5ffa987895b873bd0a2b75216e797689dbe722a40468cb0b1` | none | unchanged comparison `8bb8bd38...88ebd1` |
| raw Euclidean | `6654401aa661d7441fdb01c391f64b682e1f7e5a016068273cdda76774601f38` | none | unchanged comparison `8bb8bd38...88ebd1` |
| shuffled label | `e15f42bcfd0a4d6d178e015c96619c50dd1e4a35e9864792764f6592ecb99a53` | `(alpha,delta,beta,gamma)` candidate order | `32cbafb4333c788a7c9b694c63211604252d3abfcc5a4d980f0e9863784b6551`; rho `0.8`, overlap `1` |
| shuffled pair | `6d6c6b9c382cca99ffd8a0d2d6c1ff71c4fc903d5d184ad1a040b6f20aeb80c0` | `(alpha,delta,beta,gamma)` candidate order | same `32cbafb4...4b6551`; no pair outcomes represented |

## Constructor and master-counterexample matrix

| Surface | Outcome | Exact evidence | Severity |
|---|---|---|---:|
| Split result | OPEN | master `c1cbcf5b...3f177`; fresh semantic twin `66cbe9d4...c6902`, `COMPUTED`, four query rows, value `0.5`, no comparison | P1 |
| Source result | OPEN | master `f0f0afb8...5cca`; fresh semantic twin `0dc3d3a6...62510`, disjoint provider candidate sets, `COMPUTED`, no comparison | P1 |
| Failure register | OPEN, exact digest reproduced | `31f5ab91...9056`, 10 supplied/retained while total says 100 | P1 |
| Applicability | OPEN, exact digest reproduced | `ed497952...1e2`, caller `True` suppresses transfer deficit | P1 |
| Stress specification | OPEN | master `6599b30a...42b`; fresh normal-constructor agreement/k=999 witness `e8261a80...40ecf`; substituted-inventory computed result `a48165be...0cdf` | P1 |
| Ordered control | OPEN | `(beta,alpha)` rejected solely for nonalphabetical order | P1 |
| Shuffled nulls | OPEN | label/pair controls share candidate permutation and comparison `32cbafb4...4b6551` | P1 |
| Inventory | accepts canonical query roster | does not bind provider candidate sets or coherent window chronology | P1 support |
| Stress result | accepts computed result with zero comparisons | all eight computed probe rows had `comparisons=0` | P1 support |

The master packet gives only digests—not the full canonical split, source or specification
preimages—so byte-for-byte re-materialization of those three opaque hashes is impossible
from the packet alone. Their exact identities are retained above, source readback shows
the accepting paths are unchanged, and fresh independently constructed semantic twins
reproduce each behavior. The failure-register and applicability preimages were fully
specified by the packet/test conventions and their exact master digests reproduced.

## Commands and results

All Python/tool caches and bytecode were directed outside the repository.

| Command | Exit | Result |
|---|---:|---|
| `UV_CACHE_DIR=/private/tmp/w06-robust-review-pytest-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | `14 passed in 0.21s`. |
| `UV_CACHE_DIR=/private/tmp/w06-robust-review-ruff-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-robust-review-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | All checks passed. |
| `UV_CACHE_DIR=/private/tmp/w06-robust-review-mypy-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-robust-review-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | No issues in four source files. |
| `UV_CACHE_DIR=/private/tmp/w06-robust-review-lint-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | Three contracts kept, zero broken. |
| `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json` | 0 | `3faba3693b28c887b0d411f0ac300fbfb166a1230727c06eeb319095ca26c549`. |
| Public inline eight-kind computed/unsupported, chronology, source-intersection, inventory-substitution and five-control probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | Exact matrices above; all eight computed kinds shared the unchanged input digest and zero comparisons. |
| Public inline failure/specification/applicability constructor probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | Exact `31f5ab91...9056` and `ed497952...1e2` reproduced; agreement/k=999 accepted. |
| `rg -n 'evaluate_stress_test|evaluate_control|StressTestResult|DeterministicControlResult' tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 1 (normalized to shell 0 for evidence collection) | Zero matches. |
| `test -s reports/reviews/W06/evaluation-robustness-independent-review-R1.md` | 0 | Independent review exists and is nonempty. |
| `test -s reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R1.md` | 0 | Mandatory return exists and is nonempty. |

## Required correction

The smallest sound correction is one bounded producer rework that:

1. represents and executes each declared partition/transformation, persists every
   transformed population identity and required comparison, and enforces minima per
   evaluated unit with unambiguous window chronology;
2. represents provider candidate rosters and rejects an empty exact intersection;
3. binds specification metric/k/inventory to the protocol, and binds result children and
   comparisons back to that specification;
4. replaces alphabetical ranking rejection with canonical record identity while
   preserving score order, supplies actual coverage/metadata/raw inputs, and permutes
   labels or pair outcomes—not candidates—for the null controls;
5. binds failure registers to a canonical full-source population digest and derives
   applicability from exact mandatory stress/control results and inventory deficits; and
6. replaces the label-only fixture with executable computed and unsupported cases and
   tests every stress/control/constructor branch with pinned identities.

After correction, obtain a fresh independent review. Remaining result, population, null,
register, applicability and gate-input risk is **high** until then. Public implementation
evidence continues to make no human-expert, protected, transfer, calibration,
prospective, provider, recruitment-outcome or positive product claim.

No Git operation, dependency/lock change, implementation edit, protected expected-output
access, external/provider/credential access or write outside the two authorized report
paths occurred.

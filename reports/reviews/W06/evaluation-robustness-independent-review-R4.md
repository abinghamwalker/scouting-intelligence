# W06 evaluation robustness independent review — R4

## Verdict

**REWORK — 0 P0, 1 P1.** The R4 implementation closes the exact R3 row,
authority, fixture and typed-deficit substitutions: exact stress witness
`013da049ef32c63d7bf5d40e825b7d377000cca70fe8b6c86fb2becb05797598`, exact
control witness
`75b2bc182bbd1e72816de51ce7516e1cf1ee2475328aa49cbabca80485699e1b`, and
arbitrary-authority control
`fd55e1eeaf2c977f0aa38156af350fb98f1b56a8b77d50aca10681cec86a74ba` all
reject under the current normal constructors. The fixture drives a computed and
unsupported stress population, all five typed controls including pair absence, exact
failure/applicability identities, and exact typed incoherent/common-candidate deficits.

One material value-lineage class remains open. The validators derive metric/comparison
input identities from persisted rows but do not derive the stored numeric outputs from
those rows. The mandated metadata control comparison witness changes only Spearman from
`-0.19999999999999996` to `0.0`, retains exact left/right input digests, re-signs the
child and parent, and accepts as exact parent
`fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb`.
Fresh extensions demonstrate the same root defect for aggregate control and stress
metric values. This is one P1 class, not three independent findings: all three accept
because persisted numeric children are self-consistent and signed but are not
recomputed from their already-bound inputs.

No P0 is assigned because this assessment remains public implementation-only evidence,
the applicability state is `UNSUPPORTED`, governed pair evidence remains absent, and no
positive empirical or protected decision is created. The defect is P1 because it can
substitute retained stress/control/null values and therefore corrupt the evidence later
consumed by a protected gate.

This review used only the public W06 fixtures and fresh public inline objects. It did
not open, execute, infer, or relabel protected expected output.

## Finding

### P1-1 — Persisted metric and rank-comparison values are not derived from their bound rows

`MetricResult` enforces internal sufficient-statistic arithmetic and its payload digest,
but it cannot prove that the numerator/denominator came from `input_digest`
(`src/scouting/contracts/evaluation.py:702-749`). `RankComparisonResult` similarly
enforces range and set-metric arithmetic but does not derive Spearman, overlap,
disagreements, or churn from the left/right rankings
(`src/scouting/contracts/evaluation.py:828-886`).

R4 correctly binds cohort rows, per-query/aggregate input identities, and interval
links (`src/scouting/contracts/evaluation.py:1502-1566`). It also binds stress comparison
endpoints and input digests (`src/scouting/contracts/evaluation.py:1580-1605,
1633-1686`). Those checks stop foreign-row substitution, but none compares the complete
persisted `MetricResult` or `RankComparisonResult` with the result of the accepted core
algorithm.

The control validator has the same boundary. It derives exact baseline/null rows,
per-query input identities, aggregate input identities, comparison endpoint digests,
and label permutation (`src/scouting/contracts/evaluation.py:2125-2176`), but it checks
only the comparison input digests at lines 2152-2169 and only aggregate metric input
digests at lines 2133-2151. Re-signing a numerically different child therefore passes
the parent at lines 2192-2203.

The exact mandated witness reproduces as follows:

- original metadata control:
  `cf1925a1913ca7c72bbed64c9056c11c3473f668472b1d64b0b6972e4272799c`;
- unchanged left input:
  `4113634a8c816a9eac58b6b307266fcda38e326dfc0eb7f659db7dff648b5441`;
- unchanged right input:
  `3acadf49e014d851cd16d8fe5064b2b2fce2ab23fda98531f661f5b2c2dadd32`;
- original comparison:
  `dea2ae967331e4074c98dc96dc3ba2353abe1d22866de0569bf0d2eac8caeb87`,
  Spearman `-0.19999999999999996`;
- re-signed comparison:
  `2202faddee618ff386a32da44c294d2cf88adc0c2540d9c2dd4bd463aeb9a0cd`,
  Spearman `0.0`;
- re-signed parent:
  `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb`;
- normal-constructor outcome: **ACCEPT**.

Two bounded extensions classify the full retained-value effect without adding a second
finding:

- metadata aggregate baseline value `1.0 -> 0.0`, with exact aggregate input digest
  `4d78956709bc04c45f22dc2ea720b1fbe202335fcf760ce3f210f3f4eeb437ba`
  retained, accepts child
  `212ab5780f43435150de689f8ce5b143c40f841006d2069be8edf7bcd48f8a4b`
  and parent
  `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815`;
- split cohort aggregate value `1.0 -> 0.0`, with exact aggregate input digest
  `2fe3afe03310ecd0a52e3e98c266fed3674bf5f1dbb49190cf3d41b7a00746da`
  retained and the interval point still `1.0`, accepts metric
  `ca55b6e60f5cb044aa3d06fe2bac0b94a0e47de9887353a8c9c0edb7d97e27e7`,
  cohort
  `1f420a7fc6333c9a80525c45628130ab8e5ce028b642e774ed0967474d5975fe`,
  and stress parent
  `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404`.

## Exact R3/R4 witness and closure matrix

| Surface | Exact public evidence | Outcome | Disposition |
|---|---|---|---|
| R3 split rows/children under exact split IDs | result `013da049...97598`; cohorts `821b2779...d3e`, `e2fbf1ca...1bd4`; comparisons `9c6e7109...de65`, `5f1ee04b...c4e1` | Normal parent rejects: named comparison rankings do not equal named cohort rows | **Closed** |
| R3 metadata foreign rows/authority/stale children | input `94d2c2b8...e96883`; parent `75b2bc18...e1b`; children `e20a2424...8a27`, `d97634df...172a`, `dea2ae96...b87` | Current normal constructor rejects at `input.authority` | **Closed** |
| R3 arbitrary bare metadata authority | input `88972776...b9cd`; parent `fd55e1ee...a74ba` | Current normal constructor rejects at `input.authority` | **Closed** |
| R4 metadata comparison value | parent `fa8bea37...a8fb`; child `2202fadd...a0cd`; exact inputs retained | Normal constructor accepts Spearman substitution | **Open P1** |
| R4 aggregate control/stress metric values | parents `e67c82c8...7815`, `2e70e316...1404` | Normal constructors accept values inconsistent with persisted rows/per-query evidence | **Open P1**, same root class |
| Typed sparse split | `26e98b12...e6f2a`; deficits `340060f5...69c`, `c06d34b2...a2e` | Exact typed unsupported, no cohorts/comparisons | Closed |
| Typed incoherent labels | spec `81217d49...bfd2`; result `38310e0b...80e1`; deficit `a693ae1b...d706` | Exact `INCOHERENT_LABEL_EVIDENCE`, `0/1`, no raise | Closed |
| Typed common candidates | spec `faa4a8fa...3eee`; result `e75bdbe4...35fc`; deficits `1e975614...5eb0`, `21e40253...2162` | Exact cohort and comparison `INSUFFICIENT_COMMON_CANDIDATES`, both `0/1`, no raise | Closed |
| Typed control authority mutation | metadata authority `68a353ce...e490` | Stale digest rejects; re-sign changes identity to `d8890cae...3cca` | Closed |
| Governed pair absence | `c8a0c416...727a` | Typed unsupported; no values/permutation | Closed |
| Applicability/static claims | `3fdff230...5445` | `UNSUPPORTED`; only expert and governed-pair deficits; static implementation-only non-claims | Closed |
| Failure retention | fixture `5dac72fe...17e3`: 2 total/2 retained/shortfall 8; independent `14b3c8ce...e361`: 12 total/10 retained/shortfall 0 | Complete source and exact worst-first retention enforced | Closed |

## Fixture and retained-behaviour evidence

Fixture SHA:
`b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.
The fixture-derived computed stress identities in enum order are:

1. `2fcdf6fdaa56e2a39214dcb213112aca6446ecd15503edb0c5b646c7508c8725`
2. `f8816750f185201090bf4a9e9dbd091f2a72bb24c0c111b182418e8b30414967`
3. `f9b29f502ca81aa718b4f9c2a6a9ec3e955600e208536ee9e263aa3568ebf5f0`
4. `f608776240d1029e8c4e86eb1334d2e9e664fc6fbfbc645709d20fe308610d0a`
5. `f81ada5992650905a8cdee5133ee638dc195b630bb47f6e881a80b872fb119a2`
6. `adc824c2995bc0583d17bb3236670b3dcacdcbbfd4296b60205b92434894875f`
7. `add8d26951c7db8c4124c8bb2bca4a8a51e4b687d9f722e7d318ce9b9e24fc78`
8. `d497ed6c4c1ec7613f6a04108c7f54174ff056503e7662c2c4e8c263433a18d6`

All eight are computed. Walk-forward retains 8 train and 4 test observations, with all
12 inventory observations used exactly once. The five fixture-derived control input
identities are `aff6b0cc...5b25`, `cbd83cab...34b5`, `c9bef117...a4af`,
`9d24ce87...77cd`, and `d6f26145...4a2c`; result identities are
`8d1b4d0e...6a12`, `cf1925a1...799c`, `fbdceaf8...f45d`,
`a335cfb1...e38`, and `c8a0c416...727a`. Shuffled-label evidence preserves exact
candidate IDs and scores and derives permutation digest
`a67bc397e88b775678aaae6009e950ce60a3365de661128afa6fe3feae019585`.
Undeclared stress `k=999` rejects. A material observation mutation changes inventory
identity; a material authority mutation with a stale digest rejects and, when re-signed,
changes authority identity.

The expected-identities block is executed rather than merely loaded: it pins computed
split stress, sparse unsupported stress and deficits, all five control inputs/results,
pair absence, applicability, and failure register. The dedicated incoherent and
common-candidate populations execute to the exact typed results recorded above.

## Review-question disposition

| Question | Answer |
|---|---|
| Do stress rows, metric input identities and comparison endpoints derive from exact observations/cohorts? | Yes for rows and input/endpoints; exact R3 stress witness rejects. Numeric metric/comparison outputs still do not derive from those inputs. |
| Do control authority, exact rows, null rows and metric children derive from one persisted input? | Authority, rows, null rows and child input identities do. Child numeric values do not. |
| Are rank-comparison values exactly reproducible from persisted rows? | No. Exact `fa8bea37...a8fb` accepts after changing only Spearman. |
| Does the fixture drive computed, unsupported, pair-absence and literal identity paths? | Yes, with the exact identities above. |
| Do incoherent/common-candidate deficits return exact unsupported evidence? | Yes; exact typed results and deficit identities are recorded above. |
| Are applicability and failure retention evidence-honest? | Yes. Applicability is static `UNSUPPORTED`; no human evidence is fabricated; failure retention derives from the complete source. |

## Commands and results

All Python probes used `uv run --no-sync`, `PYTHONDONTWRITEBYTECODE=1`, public fixtures,
and task-local `/private/tmp` UV caches. No protected path was accessed.

| Command | Exit | Result |
|---|---:|---|
| complete `sed` reads of the exact packet and every direct `read_first` path | 0 | all required authorities read fully before review |
| `UV_CACHE_DIR=/private/tmp/w06-r4-review-pytest-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | `17 passed in 0.24s` |
| `UV_CACHE_DIR=/private/tmp/w06-r4-review-ruff-uv RUFF_CACHE_DIR=/private/tmp/w06-r4-review-ruff PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | all checks passed |
| `UV_CACHE_DIR=/private/tmp/w06-r4-review-mypy-uv MYPY_CACHE_DIR=/private/tmp/w06-r4-review-mypy PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | no issues in four source files |
| `UV_CACHE_DIR=/private/tmp/w06-r4-review-lint-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | three contracts kept, zero broken |
| `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json` | 0 | exact `b5354763...8cb6` |
| public exact R3 stress constructor probe via `uv run --no-sync python` | 0 | rebuilt exact cohorts/comparisons/result; `013da049...97598` rejects |
| public exact R3 control/authority probes via `uv run --no-sync python` | 0 | rebuilt exact inputs/results; `75b2bc18...e1b` and `fd55e1ee...a74ba` reject |
| public R4 comparison/value probe via `uv run --no-sync python` | 0 | exact `fa8bea37...a8fb`, `e67c82c8...7815`, and `2e70e316...1404` accept |
| public fixture/typed-deficit/identity/retained-closure probe via `uv run --no-sync python` | 0 | exact matrix above; no raise on typed incoherent/common deficits |

## Smallest bounded correction

Use one shared pure canonical derivation for the complete value-bearing children, not
only their input digests. Given the persisted protocol, rows, metric and `k`, reconstruct
and require exact equality of every per-query and aggregate `MetricResult`; require the
interval point/bounds to equal the reconstructed aggregate/bootstrap result. Given the
persisted ordered rankings and `k`, reconstruct and require exact equality of every
`RankComparisonResult`, including Spearman, top-k overlap, Jaccard, churn,
disagreements, reason and result digest. Call the same functions from executor and
validators, then add the exact `fa8bea37...a8fb` regression plus aggregate stress/control
value and interval-point substitutions.

Remaining P0 risk: **none identified**. Remaining P1 risk: **one**, the exact persisted
numeric-child derivation class above.

No Git operation, dependency/lock change, implementation edit, protected expected-output
access, external/provider/credential access, model tuning, or write outside the two
authorized report paths occurred.

# W06 evaluation robustness independent review — R3

## Verdict

**REWORK — 0 P0, 4 P1.** The focused public suite passes and the R3 implementation
retains several real R2 closures: all eight named stresses execute on the complete public
population, walk-forward assigns all twelve observations across its frozen cutoff,
population deficits and source-intersection absence are typed, the pair control is
unsupported without a fabricated value, applicability claim fields are static, and the
failure register derives from its complete source.

The bounded convergence defects are nevertheless still material. Both exact master
normal-constructor witnesses remain valid. A stress result can bind the exact split
observation IDs while persisting rolling-window rows and metric children, and a metadata
control can bind foreign rows and an arbitrary authority digest while retaining old
baseline/null/comparison children. The authority itself remains only a caller-selected
kind plus an opaque digest over generic ranking rows. The public JSON supplies only the
fully computed population, does not drive pair absence, contains no sparse/unsupported
population, and pins no literal stress/control/applicability identities. Finally,
otherwise sufficient incoherent-label or insufficient-common-candidate inputs raise from
an empty-deficit unsupported object instead of returning exact typed unsupported evidence.

No P0 is assigned because the public assessment remains `UNSUPPORTED` and no positive
empirical or protected claim is created. These are P1 because they can substitute a
persisted stress/control value or authority, conceal the population that produced it,
and prevent exact unsupported/applicability evidence from being persisted.

This review used only the public W06 fixtures and fresh public inline objects. It did not
open, execute, infer, or relabel protected expected output.

## Findings

### P1-1 — Stress observation IDs still do not bind embedded rows and child lineage

`StressCohort` validates the observation-ID digest and independently validates the
embedded-row roster, but it never derives those rows from the named observations in the
embedded specification inventory. It also checks per-query population/protocol/metric
shape without recomputing each `MetricResult.input_digest` or the aggregate metric from
the embedded rows (`src/scouting/contracts/evaluation.py:1364-1418`).
`StressComparison` derives its common-candidate digest from its own embedded rankings but
does not bind those rankings to the named cohorts or recompute the comparison's left/right
input digests (`src/scouting/contracts/evaluation.py:1422-1450`). `StressTestResult`
checks the exact cohort ID-to-observation-ID mapping and comparison cohort identities,
not those missing row relations (`src/scouting/contracts/evaluation.py:1478-1518`).

The exact mandated normal constructor accepts:

- result: `013da049ef32c63d7bf5d40e825b7d377000cca70fe8b6c86fb2becb05797598`;
- specification: the exact split specification;
- cohort observation IDs: the exact split half-A and half-B observation rosters;
- embedded cohort rows, per-query results, aggregate result and interval: copied from
  rolling windows 0000 and 0001;
- forged cohort identities:
  `821b2779f3f35ffee3ee28e2b34503eb465b80d9d63bfad86b1b47cb286f0d3e` and
  `e2fbf1ca8aa4d362068a081d605da8f968e2777acb5256e0e1d777c7d99f1bd4`;
- comparison rankings/results: retained from the original split result while only the
  cohort digest endpoints were updated;
- forged comparison identities:
  `9c6e71094654ef56698478343b7fccfb718d93e2e03cae1be16064b2dc2ede65`
  and `5f1ee04b0af15d9ce85d99de8ec57849c00a7d4ca6e263ba642192a42821c4e1`.

The persisted result therefore cannot prove that its exact observation roster produced
its ranked rows, per-query metrics, aggregate metric, interval, or comparisons.

### P1-2 — Control rows, results and named authority remain independently substitutable

`ControlInput` hashes a caller-provided `authority_kind`, bare `authority_digest`, and
generic `RankedObservation` rows (`src/scouting/contracts/evaluation.py:1745-1797`).
`DeterministicControlResult` binds the outer control kind to that input and checks child
protocol/metric shape, but it does not recompute baseline/null metric input digests or
comparison inputs from the embedded rows (`src/scouting/contracts/evaluation.py:1800-1880`).

The exact mandated metadata constructor accepts:

- control: `75b2bc182bbd1e72816de51ce7516e1cf1ee2475328aa49cbabca80485699e1b`;
- embedded input: authority digest `bb...bb`, baseline `queryone-obs2`, challenger
  `queryone-obs3`, input digest
  `94d2c2b8c2127dd6089c385edaa7cd5e72d5fab4f70e068777aa29bb78e96883`;
- stale baseline result:
  `e20a2424a0e8120aa200dd0e0129cf06a53872a4dd62dffcb97912052b3c8a27`;
- stale null result:
  `d97634df2c27d20c60f642c041b800c2f2699c923e3738a5d84c636b69de172a`;
- stale comparison:
  `dea2ae967331e4074c98dc96dc3ba2353abe1d22866de0569bf0d2eac8caeb87`.

The authority question is also unresolved, not merely the child link. A fresh normal
metadata execution accepted arbitrary authority digest `bb...bb` with the original
obs0/obs1 rows as input
`88972776f48eebf52ca538ba9e191a828b7f23a1879ee8a307b46771a0ddb9cd`
and control
`fd55e1eeaf2c977f0aa38156af350fb98f1b56a8b77d50aca10681cec86a74ba`;
its three children were identical to the fixture metadata children above. The same
generic row pair is used for coverage, metadata, and raw-Euclidean controls. No embedded
coverage fields, metadata values, raw vectors/distance definition, artifact object, or
content from which `authority_digest` can be verified exists. The kind and digest still
permit caller relabelling rather than proving kind-specific control authority.

### P1-3 — The public fixture does not drive unsupported/pair evidence or literal identities

The exact fixture SHA is
`eee02e82271041c0da10f1474770f983d920b7cff32e08f670e03ac614104b00`.
Its twelve observations form only the fully sufficient computed population
(`tests/fixtures/w06/public-robustness-v1.json:9-22`). It contains no sparse/unsupported
observation roster or expected deficit/result identities. The tests assert every stress
is computed (`tests/unit/test_w06_robustness.py:154-159`) and execute no fixture-derived
unsupported stress case.

The fixture declares `"governed_pair_evidence": false` at line 8, but the pair input is
constructed from a hard-coded `HASH` and hard-coded absent-authority kind rather than
that field (`tests/unit/test_w06_robustness.py:197-207`). The file SHA is pinned, but no
literal stress result, control result/input, pair result, deficit, failure-register, or
applicability identity is asserted anywhere in the R3 robustness tests. The current
public identity set is therefore observed only by this review:

- computed stress identities in enum order:
  `2fcdf6fdaa56e2a39214dcb213112aca6446ecd15503edb0c5b646c7508c8725`,
  `0a65e5566a06fc7395aa57d5279681112c6dbb5848bf3cc523b417a87cac7a9b`,
  `f9b29f502ca81aa718b4f9c2a6a9ec3e955600e208536ee9e263aa3568ebf5f0`,
  `a2ff16bca3c90949d0a14f0df177f9bbee2b8f2f98a9e09fe03dd7fd15175919`,
  `f81ada5992650905a8cdee5133ee638dc195b630bb47f6e881a80b872fb119a2`,
  `adc824c2995bc0583d17bb3236670b3dcacdcbbfd4296b60205b92434894875f`,
  `add8d26951c7db8c4124c8bb2bca4a8a51e4b687d9f722e7d318ce9b9e24fc78`,
  `d497ed6c4c1ec7613f6a04108c7f54174ff056503e7662c2c4e8c263433a18d6`;
- computed control identities for coverage/metadata/raw/shuffled-label:
  `5e3a449238385eb69dd762ace03605d40941afd9d1b2112a546e6ff726b74e57`,
  `a9e34274bc416c1883007a443dc32d136b99663b6fdf195307cbb5376ad1b3af`,
  `f0162e225d2de081e73b6b48fdbcf637bc7bbe749c4c9d392d04e5ae5fc38445`,
  `7e4b4c06fd2b6ecfd53708d034385aee5e4dba072aac942160a28a4df1ad2dd1`;
- typed pair-absence control:
  `4f4f1a15adac8aabf724d0cb0e02575a2442721c2f2a573391bdc7c42f69c98a`;
- applicability assessment:
  `211213b14635915ae8f4e829cfa57914e3748909539c0505d5a5a38cddbe58f5`.

The public JSON is consequently not the sole executable authority for the required
computed-plus-unsupported population, pair absence, and expected identities.

### P1-4 — Aggregation incoherence does not return exact typed unsupported evidence

`evaluate_stress_test` prechecks only population-count deficits, catches any later
aggregation/comparison `ValueError`, then calls `_unsupported`
(`src/scouting/evaluation/robustness.py:217-229,310-324`). `_unsupported` derives only the
predeclared count/group/intersection deficits. When the population is otherwise sufficient,
that tuple is empty, but `StressTestResult` forbids an unsupported result with no deficit
(`src/scouting/contracts/evaluation.py:1463-1467`).

Two normal public inputs reproduce the gap:

- rolling specification
  `f314dffdfaf28ce33909820d7d05ab80de953efc76827926f1546756e0acaca2`
  changes one embedded label so a cohort has incoherent candidate labels; execution raises
  `unsupported stress test retains exact deficits and no values`;
- rolling specification
  `131b4a150333d92b842b16f45d596294082d4d5424d7fa8ad22024fcdf30f00c`
  gives one observation a disjoint candidate roster; execution raises the same error.

For contrast, a fresh two-observation-per-query split population correctly returns typed
unsupported result
`26e4845c435365032b7b87870d18e61ee082ecd5962ab69d5afca0de5884af25`
with exact `PER_UNIT_OBSERVATIONS` deficits `queryone:2/4` and `querytwo:2/4`. The broken
path is specifically the required incoherent-label/common-candidate path, which cannot
be represented in applicability because no `StressTestResult` is returned.

## Narrow constructor and fixture matrix

| Surface | Exact public evidence | Outcome | Disposition |
|---|---|---|---|
| Split normal constructor with rolling children | `013da049...97598` | Accepted | **Open P1** |
| Metadata normal constructor with foreign rows/authority and stale children | `75b2bc18...e1b` | Accepted | **Open P1** |
| Bare metadata authority with normally recomputed result | `fd55e1ee...a74ba` | Accepted; child identities unchanged | **Open P1**, same control-authority class |
| Full fixture stress roster | eight identities above | All computed | Functional, but no literal identity assertions |
| Sparse split public inline population | `26e4845c...af25` | Typed unsupported, two exact deficits | Closed behavior; absent from fixture |
| Incoherent-label sufficient population | spec `f314dffd...aca2` | Raises invalid empty-deficit result | **Open P1** |
| Common-candidate deficient sufficient population | spec `131b4a15...f00c` | Raises invalid empty-deficit result | **Open P1** |
| Governed pair absence | `4f4f1a15...c98a` | Typed unsupported, no value/permutation | Runtime closed; fixture field does not drive it |
| Applicability | `211213b1...58f5` | Unsupported with expert and pair deficits | Runtime closed; identity unpinned |

## Retained R2 closure check

| Retained class | R3 evidence | Outcome |
|---|---|---|
| Named stress execution | all eight exact identities above | Retained |
| Complete walk-forward cutoff | `a2ff16bc...5919`; all 12 observations used exactly once across train/test | Retained |
| Per-unit split minima and caller deficit rejection | sparse `26e4845c...af25`; changed observed count rejects | Retained |
| Empty source intersection | `d23254464977cc3dac34ed1e047d285ae2c4a7f6019a91eb1afc437ae1cb49fd`, exact `PROVIDER_INTERSECTION:providers:0/1` | Retained |
| Specification protocol/k binding | normal `k=999` constructor rejects | Retained |
| Score order and label-only permutation | focused suite passes; shuffled-label `7e4b4c06...2dd1` retains candidates and deterministic mapping | Retained |
| Pair absence | `4f4f1a15...c98a`, no baseline/null/permutation | Retained |
| Failure source completeness | register `a1906599...69dd`, 12 total, 10 retained, shortfall 0, source digest `e68e3368...5518` | Retained |
| Applicability static claims | caller-supported population constructor rejects | Retained |

## Review-question disposition

| Question | Answer |
|---|---|
| Are cohort rows exactly derived from specification observation IDs? | No; exact `013da049...97598` accepts rolling rows under split IDs. |
| Are cohort metric and comparison input digests derived from those rows? | No; the same witness retains foreign/stale metric and comparison children. |
| Can control rows/authority change without recomputing children? | Yes; exact `75b2bc18...e1b`. |
| Are bare authority digests sufficient? | No; `fd55e1ee...a74ba` accepts arbitrary `bb...bb` and generic rows as metadata authority. |
| Does the fixture drive computed and unsupported paths, pair absence and literal identities? | No; computed only, pair absence hard-coded outside the field, no literal result identities. |
| Does incoherent label/common-candidate input return typed unsupported evidence? | No; both fresh normal inputs raise from an empty-deficit object. |
| Do pair absence, applicability, failure source and walk-forward remain closed? | Yes, proportionately verified as recorded above. |

## Commands and results

All Python probes used `uv run --no-sync`, `PYTHONDONTWRITEBYTECODE=1`, public fixtures,
and task-local `/private/tmp` caches. No protected path was accessed.

| Command | Exit | Result |
|---|---:|---|
| complete `sed` reads of `AGENTS.md`, the R3 review packet and every direct `read_first` path | 0 | all required authorities read fully before review |
| four packet `uv run --no-sync` checks without a task-local cache | 2 each | blocked before execution by sandbox denial on `/Users/adrian/.cache/uv/sdists-v9/.git` |
| `UV_CACHE_DIR=/private/tmp/w06-r3-review-pytest-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | `15 passed in 0.23s` |
| focused packet `ruff check` with task-local UV/Ruff caches | 0 | all checks passed |
| focused packet `mypy` with task-local UV/mypy caches | 0 | no issues in four source files |
| packet `lint-imports` with task-local UV cache | 0 | three contracts kept, zero broken |
| `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json` | 0 | exact `eee02e82...4b00` |
| public exact stress/control master-witness probe via `uv run --no-sync python` | 0 | normal constructors accepted exact `013da049...97598` and `75b2bc18...e1b` |
| public unsupported/incoherence probe via `uv run --no-sync python` | 0 | sparse typed `26e4845c...af25`; incoherent/common specifications raised empty-deficit validation error |
| public identity/authority probe via `uv run --no-sync python` | 0 | exact stress/control/pair/applicability identities above; arbitrary authority `fd55e1ee...a74ba` accepted |
| public retained-R2 closure probe via `uv run --no-sync python` | 0 | walk-forward, source intersection, specification, shuffled label, failure, claims and deficit checks above |
| `rg` for literal R3 robustness identities and fixture-field use | 1/0 | no literal result identities; `governed_pair_evidence` appears only in JSON, not executable test use |

## Smallest bounded correction

1. At normal construction, derive each cohort's aggregate ranked rows from the exact
   inventory members selected by `observation_ids`; recompute per-query and aggregate
   metric inputs from those rows; bind comparison rankings and left/right input digests
   to the named cohorts.
2. At normal control construction, recompute baseline/null/comparison children from the
   embedded rows and replace bare kind-plus-digest authority with a content-addressed,
   kind-specific authority object that contains the coverage/metadata/raw inputs needed
   to verify its digest.
3. Put both computed and sparse/unsupported populations, pair absence, typed control
   inputs, and literal expected stress/control/deficit/failure/applicability identities in
   the public fixture; make each field drive the constructed objects and add material
   mutation checks.
4. Represent incoherent labels and insufficient common candidates as exact typed deficits
   (or reject them at the specification boundary) so execution never routes a sufficient
   population into an invalid empty-deficit unsupported result.

Remaining bounded value/population/control-authority/unsupported/applicability risk is
**high** until corrected and freshly reviewed. The fixture remains implementation-only
and makes no human-expert, protected, transfer, calibration, prospective, provider,
recruitment-outcome, or positive empirical claim.

No Git operation, dependency/lock change, implementation edit, protected expected-output
access, external/provider/credential access, or write outside the two authorized report
paths occurred.

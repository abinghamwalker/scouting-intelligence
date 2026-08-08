# W06 evaluation robustness independent review — R2

## Verdict

**REWORK — 0 P0, 7 P1.** The R2 implementation materially improves execution: the
focused suite passes, specifications bind the protocol/inventory, split minima and the
source intersection fail closed, failure registers bind their complete source, and the
executor now builds named cohorts and comparisons. It still does not persist or validate
the evidence needed to prove those results. Exact normal-constructor witnesses substitute
stress children and control input identity, a one-pair identity permutation is accepted as
a governed null, the three non-null baselines are caller-enum aliases over the same generic
rows, applicability retains caller-controlled claim fields and trusted deficit strings,
and the JSON fixture does not drive the executable objects. In addition, walk-forward
silently discards every intermediate window.

No P0 is assigned because the applicability state remains `UNSUPPORTED` and these public
objects do not by themselves create a positive empirical claim. They are P1 because they
can change a persisted stress/control value, evaluated population, null interpretation,
applicability reason or later gate input while retaining normal-constructor validity.

This review used only the public W06 fixtures and fresh public inline objects. It did not
open, execute, infer or relabel a protected expected output.

## Findings

### P1-1 — Stress cohort and comparison children are not bound to their ranked rows

`StressCohort` persists observation IDs and an opaque `candidate_roster_digest`, but no
ranked rows. Its validator links the interval to the supplied metric and checks only the
metric's evaluated-query digest; it cannot derive the metric input from the observations
or derive the roster digest. `StressComparison` likewise does not derive its common
candidate digest or its `RankComparisonResult` inputs. `StressTestResult` checks cohort
observation membership plus child protocol/metric/k, not those missing row relations
(`src/scouting/contracts/evaluation.py:1280-1427`).

The exact master constructor succeeds as a normal `StressTestResult`:

- result: `5edc056a4aa5d317642b1efd22e490eac2ff4a849b3f51d770babaa75f91d3f8`;
- split cohorts retain the exact expected half observation IDs, but their metric/interval
  children come from rolling windows 0000 and 0001;
- forged cohort identities: `ff8e89a965733bdfbbd8068c6dda0b80e0a565907669796818b7efc905553478`
  and `92e4faa060d510c8d055e7a8204d9e5e555081b401d7995197ffee62c9ec1bd7`;
- both `candidate_roster_digest` values are `bb...bb`;
- comparison identities are
  `94ef2ac608d8d10f8b1d0480b911d3960c4fcfaba52b28564e5b51a0a75a0e6e`
  and `a9b5047089d3d4362d67b649d4e1b23f00047afdb731caacb1d2dfbf52846e37`;
- both `common_candidate_digest` values are `cc...cc`, while the unchanged split
  `RankComparisonResult` children are accepted.

Thus a persisted cohort does not embed or cryptographically derive the exact rows needed
to reproduce its metric, interval, roster or comparison.

### P1-2 — Persisted controls do not bind their input evidence or children to `input_digest`

`DeterministicControlResult` stores an opaque `input_digest` and child results, but embeds
neither ranking rows nor pair evidence. Validation checks seed, metric kind and protocol;
it never derives `input_digest` or links the child input digests to it
(`src/scouting/contracts/evaluation.py:1551-1600`).

The exact master metadata witness succeeds after changing only `input_digest` to
`bb...bb` and recomputing the outer digest:

- forged control: `a2fc46a61a5b5408bc1d2bc1e4cf53aec4adbf8cab202b7fb30b17ccdddb97fa`;
- unchanged baseline: `e20a2424a0e8120aa200dd0e0129cf06a53872a4dd62dffcb97912052b3c8a27`;
- unchanged null: `d97634df2c27d20c60f642c041b800c2f2699c923e3738a5d84c636b69de172a`;
- unchanged comparison: `dea2ae967331e4074c98dc96dc3ba2353abe1d22866de0569bf0d2eac8caeb87`.

The control therefore cannot be recomputed from its persisted representation and its
children remain substitutable relative to the claimed input identity.

### P1-3 — Shuffled-pair accepts fabricated authority and an identity permutation

The pair path accepts any locally constructed `ReviewerIdentity` whose enum says
`GOVERNED_HUMAN_EXPERT`; it is not bound to a protocol reviewer roster, evaluation bundle
or governed evidence population. `_shuffle_pairs` does not require a non-identity or
sufficient permutation (`src/scouting/evaluation/robustness.py:462-514`).

The exact master witness reproduces:

- fabricated reviewer digest:
  `561ffc2e2c3d1875e9154f563146735e09cadc1bb5bb0510875ed09b2571e4bb`;
- fabricated preference digest:
  `8fb6a0415be46a37246bac4d20ae74b9ddfbcf52f2b4dac031ffb8ffd0a2cdb3`;
- control digest:
  `96da14ddc305f67058a90a095b399ac428900a2b95d95fee129b420c6b861776`;
- input digest:
  `500685e737989869775e4258c2479becb6119e196922b9d44b6f31c8931c6568`;
- permutation `("queryone|pair|pair",)` and permutation digest
  `f22116c547df9eb7407805ed2fd0bd70ba12535a9b615772c5d174f6b69ed5ba`;
- identical baseline/null digest
  `8fcb199b3aa00d74d0236fb44b987d2c120486aa758294ae94b125b3e5542a32`
  and baseline = null = `1.0`.

This is not a null experiment. Because its null status is `COMPUTED`, applicability also
does not expose missing governed pair evidence.

### P1-4 — Coverage, metadata and raw-Euclidean controls have no kind-specific authority

`ControlRankingInput` contains only a query plus two generic `RankingRow` values. The
non-null path changes behavior only through the caller's `ControlKind` enum and places
that enum in the opaque outer input digest (`src/scouting/evaluation/robustness.py:68-74,
517-602`). The same generic row pair produced:

| Caller kind | Control digest | Input digest | Baseline | Null | Comparison |
|---|---|---|---|---|---|
| coverage | `945d7f18...1878` | `a08227d7...a05` | `e20a2424...8a27` | `d97634df...172a` | `dea2ae96...eb87` |
| metadata | `cf72d73d...86c3` | `64bb24f1...e475` | `e20a2424...8a27` | `d97634df...172a` | `dea2ae96...eb87` |
| raw Euclidean | `4bb1a98e...d868` | `0731cbc0...aa96` | `e20a2424...8a27` | `d97634df...172a` | `dea2ae96...eb87` |

The different outer digests prove only that the caller chose different enum values; no
coverage field, metadata field, raw vector, distance definition, baseline artifact or
governed kind identity exists to support the names.

### P1-5 — Applicability claim fields and unsupported reasons remain caller-controlled

The constructor derives only `missing_evidence`. It does not validate
`supported_population`, `exclusions` or `non_claims` at all
(`src/scouting/contracts/evaluation.py:1666-1728`). A normal constructor accepted:

- assessment `6497964c48f108a1c8046b96400b30573b85bd267b0f6a68f532a050558e78a0`;
- `supported_population=("CALLER_SUPPORTED",)`;
- `exclusions=("CALLER_EXCLUSION",)`;
- `non_claims=("CALLER_CLAIM",)`.

Unsupported reasons are also trusted from `StressTestResult`, whose unsupported branch
checks only that a canonical non-empty string exists. On the fully computed public
inventory, a caller-created split result
`56d61f82d4d253eb4f971cef8bbc5ebb0417717c9636eaef6b75a334a8b5e1c4`
with reason `caller_asserted_deficit` produced applicability assessment
`cc0b50afc3667a52f5aec0df9810cf31f7f56e4b09e6faf5ffd8c4c189f71263`
and `MISSING_split_half_reliability:caller_asserted_deficit`.

The helper returns conservative static strings, but persisted applicability is not exactly
derived and its mandatory-control check looks only at null computation status. This lets
the fabricated pair witness suppress missing governed pair evidence.

### P1-6 — The public JSON is descriptive metadata, not executable fixture input

Fixture SHA-256 is
`0f369d628b9d9ad714d62b35c0b7bebd4f345c9e2fae76f333c0d80fd77565e8`.
It contains population counts/labels and rosters, but no observation records, scores,
labels, pair outcomes, kind-specific baseline inputs or expected identities. The test
reads only `evidence_class` and `claim_notice` before calling the independent hard-coded
`protocol()` and `fixture_population()` constructors
(`tests/unit/test_w06_robustness.py:179-199`). Its final hash check compares a fresh hash
of the file with `fixture_digest()`, which hashes the same file again; it pins no expected
digest (`tests/unit/test_w06_robustness.py:387-398`).

| Fixture field | Drives executable objects or pinned identities? |
|---|---|
| protocol declaration | No |
| computed population | No |
| unsupported population/deficits | No |
| mandatory stress roster | No |
| mandatory control roster | No |
| non-claims | No; only separate `claim_notice` substring is asserted |

Changing those fixture bytes can leave every stress/control identity assertion green.

### P1-7 — Walk-forward samples only the first and last window

The executor takes `windows[0]` as train and `windows[-1]` as test, then drops all other
windows (`src/scouting/evaluation/robustness.py:317-337`). Public result
`766f1df254e1714c72a8723229c56d909902b72a94c40af9bd4d7c8f3df7f826`
used window-one observations `obs0/obs1` and window-three observations `obs4/obs5` for
both queries, omitting every window-two `obs2/obs3`. Replacing all middle-window ranking
scores/order while retaining governed identities produced the same result digest.

The protocol does not declare a fold/cutoff that authorises this sample. A three-window
population is therefore reported as walk-forward evidence while one third of its declared
observations cannot affect the value or identity.

## R1 closure matrix

| R1 class / witness | R2 outcome | Evidence |
|---|---|---|
| unchanged-population transforms; split master `c1cbcf5b...3f177` | Execution closed; persisted proof retained P1 | sparse per-unit split is unsupported as `94519ef4...a1f4`, and named cohorts execute; exact R2 child substitution `5edc056a...d3f8` remains valid |
| empty provider intersection; master `f0f0afb8...5cca` | Closed | fresh disjoint-provider population returns only `exact_candidate_intersection=0`, result `4d0e5c97...e2fd` |
| controls rejected score order / shuffled candidates | Ranking and label branch closed; pair branch retained P1 | score-desc `(beta,alpha)` accepted; shuffled-label preserves candidates; exact identity pair null `96da14dd...1776` computes |
| unbound specification/result | Specification/executor closed; result retained P1 | k=999 rejects; foreign inventory rejects; exact foreign result children still construct as `5edc056a...d3f8` |
| failure register `31f5ab91...9056` | Closed | obsolete exact shape rejects for missing `source_cases` and `source_digest`; current total/shortfall derive from complete source |
| applicability `ed497952...1e2` | Caller boolean closed; claim fields/reasons retained P1 | obsolete keyword rejects; normal `6497964c...78a0` caller claim fields and `cc0b50af...1263` asserted reason succeed |
| label-only fixture | Open | JSON still has no executable rows or kind-specific inputs; tests use hard-coded objects |

## R2 execution and constructor matrix

| Surface | Fresh public result | Cohorts / comparisons | Outcome |
|---|---|---:|---|
| split half | `ba4512d1...92bc` | 2 / 2 | executor computes; exact substituted constructor also accepts as `5edc056a...d3f8` |
| rolling window | `a4b15e55...e918` | 3 / 4 | executor computes adjacent windows |
| minutes sensitivity | `36abac84...4efe` | 2 / 2 | executor computes both declared threshold cohorts |
| walk-forward | `766f1df2...f826` | 2 / 2 | computes but omits the middle window |
| leave competition | `c0d8ef5b...aa06` | 2 / 2 | executor computes |
| leave team | `481116c9...c16e` | 2 / 2 | executor computes |
| leave provider | `480ad514...f631` | 2 / 2 | executor computes |
| source intersection | `4914acf9...4481` | 2 / 2 | computes exact non-empty intersection; disjoint case is unsupported |
| metadata master constructor | `a2fc46a6...97fa` | unchanged children | exact arbitrary input digest accepts |
| shuffled-pair master constructor | `96da14dd...1776` | identity permutation | exact fabricated one-pair null computes baseline = null = 1.0 |

## Review-question disposition

| Question | Answer |
|---|---|
| Can stress children be substituted? | Yes; exact `5edc056a...d3f8`. |
| Do cohorts embed/derive exact ranked rows? | No. |
| Do controls embed exact ranking/label/pair inputs and baseline authority? | No; exact `a2fc46a6...97fa`. |
| Are metadata/raw/coverage governed by baseline identity rather than enum? | No. |
| Does shuffled-pair avoid fabricated evidence and identity nulls? | No; exact `96da14dd...1776`. |
| Are applicability population/claims/reasons exactly derived? | No; `6497964c...78a0` and `cc0b50af...1263`. |
| Do fixture bytes drive every pinned identity? | No. |
| Is walk-forward a declared complete earlier/later population? | No; intermediate windows are omitted. |

## Commands and results

All Python bytecode and tool caches were directed to `/private/tmp`; `uv` used
`--no-sync`. The inline probes imported only public test helpers and public source.

| Command | Exit | Result |
|---|---:|---|
| `UV_CACHE_DIR=/private/tmp/w06-r2-review-pytest-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | `15 passed in 0.19s` |
| `UV_CACHE_DIR=/private/tmp/w06-r2-review-ruff-uv RUFF_CACHE_DIR=/private/tmp/w06-r2-review-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | all checks passed |
| `UV_CACHE_DIR=/private/tmp/w06-r2-review-mypy-uv MYPY_CACHE_DIR=/private/tmp/w06-r2-review-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | no issues in four source files |
| `UV_CACHE_DIR=/private/tmp/w06-r2-review-lint-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | three contracts kept, zero broken |
| `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json` | 0 | `0f369d62...565e8` |
| public exact R2 split foreign-child constructor probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | exact `5edc056a...d3f8` accepted |
| public exact R2 metadata input-digest constructor probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | exact `a2fc46a6...97fa` accepted |
| public exact R2 fabricated pair-null probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | exact `96da14dd...1776`, identity permutation, baseline=null=1.0 |
| public R1 closure and walk-forward mutation probe via `uv run --no-sync python - <<'PY' ... PY` | 0 | boundaries/matrices above; changing omitted middle-window rows left `766f1df2...f826` unchanged |
| public applicability constructor probes via `uv run --no-sync python - <<'PY' ... PY` | 0 | exact fresh `6497964c...78a0` and `cc0b50af...1263` accepted |
| `rg -n "fixture\\[|fixture_digest\\(|public-robustness-v1|computed_population|unsupported_population|mandatory_stress_kinds|mandatory_controls" ...` | 0 | only `evidence_class`/`claim_notice` are consumed; final digest comparison is self-referential |
| `test -s reports/reviews/W06/evaluation-robustness-independent-review-R2.md` | 0 | detailed review exists and is non-empty |
| `test -s reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R2.md` | 0 | mandatory return exists and is non-empty |

## Required correction

The smallest bounded correction is one robustness rework that:

1. embeds canonical ranked rows (or a complete canonical row manifest) in every stress
   cohort and derives candidate rosters, metric/interval inputs and comparison inputs from
   those exact rows at normal construction;
2. embeds each control's exact ranking/label/pair evidence, k and governed baseline
   authority, derives all child inputs from it, and gives coverage/metadata/raw controls
   distinct typed evidence contracts;
3. requires shuffled-pair evidence to bind an accepted governed roster/bundle and fails
   closed on an insufficient or identity permutation;
4. derives applicability population, exclusions, non-claims and every deficit from the
   bound inventory/results, including explicit missing governed pair evidence;
5. makes the public JSON contain the actual executable observations, rankings, labels,
   pair evidence and kind-specific inputs, with its exact bytes feeding all pinned
   identities; and
6. freezes a walk-forward fold/cutoff that assigns every eligible declared window to the
   earlier-train or later-test population rather than silently sampling endpoints.

Remaining result/population/null/fixture/applicability/claim risk is **high** until fresh
rework and independent review. The public evidence remains implementation-only and makes
no human-expert, protected, transfer, calibration, prospective, provider,
recruitment-outcome or positive empirical claim.

No Git operation, dependency/lock change, implementation edit, protected expected-output
access, external/provider/credential access or write outside the two authorized report
paths occurred.

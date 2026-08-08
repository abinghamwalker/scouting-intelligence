# W06 evaluation core independent review — R2

## Verdict

**RETURN FOR REWORK.** R2 closes meaningful parts of every R1 family, but it does not close any family completely. The exact remaining review inventory is **1 P0, 4 P1, and 1 P2**. In particular, a normal `ACCEPT_CLAIM` can still bind a protected-test run with no metrics to a FIT access record and a different protocol digest. Passing the four-test suite therefore does not support a governed protected-evaluation claim.

This was a fresh, report-only review. No protected expected output was opened or inferred.

## Findings

### P0 — W06-EC-R1-01 remains open: protected access, run, protocol, and gate identity are not relationally bound

R2 now rejects `IMPLEMENTATION_FIXTURE` relevance evidence in governed partitions and binds protocol query/reviewer/partition roots inside `EvaluationBundle`. Those are real closures, but the protected claim chain remains open:

- `EvaluationAccessRecord` validates `one_use` only when the access record itself says `PROTECTED_TEST`; it is not linked to a run.
- `EvaluationRun` accepts a `PROTECTED_TEST` partition, a FIT access digest, and an empty `metric_results` roster.
- `GateDecision` accepts any non-null run digest for `ACCEPT_CLAIM`; it does not bind the gate protocol to the run protocol or require protected, non-empty, eligible results.
- `EvaluationQuery.feature_cutoff_ts` is still not compared with `EvaluationProtocol.decision_cutoff_ts`.

Retained normal-constructor counterexample:

```text
access.partition = FIT, access.one_use = false
run.partition = PROTECTED_TEST, run.access_digest = access.access_digest
run.metric_results = ()
run.protocol_digest = 00…00
gate.decision = ACCEPT_CLAIM
gate.protocol_digest = 11…11
gate.run_digest = run.run_digest
result: all four contracts validate; gate.protocol_digest != run.protocol_digest
```

Impact: a protected claim can be accepted without proving protected one-use access, protocol identity, or even one computed metric. This remains P0 because the surviving path can authorize a claim rather than merely distort a diagnostic.

Smallest bounded correction: validate the access/run/gate aggregate, not isolated digest shapes. Require one protocol digest across protocol, access, run, and gate; identical protected partition across access and run; one-use protected access; a canonical non-empty required metric roster; linked intervals/slices; and query feature cutoffs no later than the protocol decision cutoff. `ACCEPT_CLAIM` must require that complete valid aggregate.

### P1 — W06-EC-R1-02 remains open: aggregate row identity and canonical content are incomplete

R2 binds protocol roots to ordered query, reviewer, and membership digests, and the bundle digest covers its serialized payload. It still does not define one canonical evidence aggregate:

- relevance evidence IDs and semantic rows are not required to be unique or canonically ordered;
- pair uniqueness is directional, so `(alpha,beta)` and `(beta,alpha)` are accepted as different rows, even with the same preference ID;
- hard-negative IDs/rows are not required to be unique or canonical;
- adjudication only checks that referenced evidence IDs exist and that the adjudicator is rostered; it does not require one query/candidate/rubric or an actual disagreement;
- `candidate_universe_digest` is accepted as an opaque hash rather than recomputed from `candidate_ids`.

Retained normal-constructor counterexample:

```text
bundle A relevance = (eone, eone, etwo)
bundle B relevance = (etwo, eone, eone)
preferences = ((alpha,beta,id=preference), (beta,alpha,id=preference))
hard_negatives = (hard, hard)
adjudication.evidence_ids = (eone@alpha, etwo@beta)
candidate_universe_digest = 11…11 (not derived from candidate_ids)
result: both bundles validate and have different bundle digests
```

Impact: identical evidence multisets can acquire different aggregate identities; duplicate weight and cross-candidate adjudication can change evaluated values.

Smallest bounded correction: recompute the candidate-universe digest from the canonical candidate roster; define canonical keys for every evidence family; reject duplicate IDs and duplicate semantic rows; canonicalize unordered pairs before uniqueness checks; require deterministic collection ordering; and bind adjudications to a genuine same-query, same-candidate, same-rubric disagreement.

### P1 — W06-EC-R1-03 remains open: partial-label arithmetic and ranking order are not safe

R2 correctly introduces an explicit complete universe, declared `k`, and unavailable results for unjudged/abstained labels. However, `captured` always includes partial gain while the recall denominator excludes it when `partial_counts_for_precision_recall=false`.

Retained counterexample and formula:

```text
k = 2
labels = (RELEVANT, PARTIAL)
partial_gain = 0.5
partial_counts_for_precision_recall = false
captured = 1.0 + 0.5 = 1.5
denominator = 1.0
reported recall = 1.5 / 1.0 = 1.5
```

The same implementation raises `ZeroDivisionError` when partial labels are eligible, `partial_gain=0`, and there are no relevant labels. `RankedItem.score` also accepts `NaN`; reversing input order changed precision@1 from `1.0` to `0.0`, so the nominal score/candidate tie ordering is not deterministic for all accepted inputs. The protocol `missingness_policy` field is not used to select behavior.

Impact: accepted inputs can produce out-of-range values, exceptions, or order-dependent values.

Smallest bounded correction: use one policy-specific gain function for both numerator and denominator, return explicit unavailable on a zero eligible denominator, reject non-finite/canonical-invalid scores at construction, and make the declared missingness/tie policy executable.

### P1 — W06-EC-R1-04 remains open: low-intersection comparison and relational pair/agreement identity are incomplete

R2 reranks the shared intersection before Spearman and bounds ordinary overlap/churn calculations. The `len(common) < 2` early return nevertheless overwrites independently defined top-k overlap metrics.

Retained counterexample:

```text
left = (a, x)
right = (a, y)
k = 1
actual top-k overlap = 1; overlap_rate = 1.0; churn = 0.0
reported overlap = 0; overlap_rate = 0.0; churn = 1.0; disagreements = (a,)
```

`pair_preference_accuracy` accepts aligned strings without pair ID, unordered candidate-pair identity, membership, uniqueness, or reviewer authority. `inter_rater_agreement` accepts aligned label vectors without item/reviewer identity, and the protocol declares only a generic `agreement` metric rather than the statistic and eligibility policy.

Impact: comparison values can be wrong even when both top-k sets are identical, and pair/agreement values cannot be traced to the governed evidence being claimed.

Smallest bounded correction: compute overlap/Jaccard/churn independently of Spearman availability; return only Spearman as unavailable for fewer than two shared items; pass canonical governed pair/item identities into pair and agreement calculations; reject duplicates/misalignment; and declare the agreement statistic and exclusions in the protocol.

### P1 — W06-EC-R1-05 remains open: result, interval, run, and bootstrap contracts do not enforce arithmetic or protocol links

R2 improves the core bootstrap resample digest: query identity, values, metric, k, seed, resample count, confidence, method, and samples are included, and input row reordering is canonical. The persistence and orchestration contracts remain opaque.

Retained normal-constructor counterexample:

```text
MetricResult(metric=precision, value=2.0, numerator=1, denominator=2) validates
BootstrapInterval(method=anything, lower=1.0, upper=0.0, status=COMPUTED) validates
```

Consequences include:

- `MetricResult` does not require `value = numerator / denominator`, a unit range, a declared metric/k, or protocol identity;
- fractional partial gains emitted by `evaluate_ranking` cannot be represented by its integer numerator/denominator fields without changing or rounding the value;
- `BootstrapInterval` does not require `lower <= point <= upper`, the protocol method/settings, or the core `resample_digest`;
- unavailable intervals may retain bounds;
- `EvaluationRun` does not link intervals to present results or require canonical/non-empty protocol metrics;
- `resampling_unit="candidate"` validates even though the implementation samples queries;
- a protocol can roster `agreement` for bootstrap, which then raises `KeyError` because ranking evaluation has no such output key.

Impact: persisted values and intervals can contradict their own sufficient statistics and protocol, while accepted configurations can fail at runtime.

Smallest bounded correction: use `MetricName`, enforce protocol metric/k membership and exact arithmetic/ranges with a representation that supports weighted counts; require interval ordering, point containment, method/settings/resample identity, and no bounds when unavailable; validate query-unit resampling and metric capability; and enforce canonical linked result/interval rosters in the run.

### P2 — R2 tests and public-fixture mechanics remain too thin for the claimed closure

The scoped suite has four tests. It covers exemplar/candidate overlap, declared k, complete-universe/missingness behavior, bootstrap row reordering, one ordinary Spearman/churn case, one pair example, and one agreement example. It does not test the retained P0/P1 cases above.

The public fixture test reads `tests/fixtures/w06/public-evaluation-v1.json`, checks `evidence_class`, and searches the notice text. It neither asserts the file digest nor transforms the fixture through the new ranking/evaluation path. Freshly observed identity: SHA-256 `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`, 510 bytes.

Smallest bounded correction: add one rejecting regression for each retained R1 row and assert the fixture bytes/digest plus an executable fixture-to-contract-to-metric path.

## R1 closure matrix

| R1 identifier | R2 status | Remaining severity | Independently reproduced closure | Retained surviving counterexample |
|---|---|---:|---|---|
| W06-EC-R1-01 | **OPEN (partial closure)** | **P0** | Governed partitions reject fixture relevance; bundle roots bind query/reviewer/membership; relevance checks cutoff, reviewer, rubric, and candidate roster. | FIT non-one-use access + empty protected run + mismatched-protocol `ACCEPT_CLAIM` all validate. |
| W06-EC-R1-02 | **OPEN (partial closure)** | **P1** | Bundle digest covers payload; query/reviewer/membership rosters and their roots are ordered/bound. | Duplicate/reordered relevance, reversed same-ID pairs, duplicate hard negatives, and cross-candidate adjudication validate; reorder changes bundle digest. |
| W06-EC-R1-03 | **OPEN (partial closure)** | **P1** | Declared k, explicit label states, complete unique universe, and unavailable missing labels are enforced. | With partial excluded from P/R, implementation reports recall `1.5`; accepted NaN score makes precision input-order dependent. |
| W06-EC-R1-04 | **OPEN (partial closure)** | **P1** | Shared intersection is reranked for ordinary Spearman; ordinary churn is bounded; pair/agreement functions exist. | Identical top-1 item with only one common candidate is reported as overlap `0` and churn `1`; relational identity remains absent. |
| W06-EC-R1-05 | **OPEN (partial closure)** | **P1** | Core bootstrap digest now binds query IDs, values, metric/k, settings, and samples; row reorder is canonical. | Value `2.0` with `1/2` and interval `[1.0,0.0]` with arbitrary method validate; run/gate links remain opaque. |

## Acceptance and reproduction ledger

The literal first pytest attempt could not open the sandboxed global uv cache and exited 2 before collection (`/Users/adrian/.cache/uv/sdists-v9/.git: Operation not permitted`). This was an environment-only failure. The same packet-scoped commands were then run against the existing environment with a task-local uv cache, `--no-sync`, and cache outputs outside the repository:

| Command | Exit | Result |
|---|---:|---|
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | `4 passed in 0.36s` |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-ruff uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | All checks passed. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-mypy uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | Success: no issues found in 3 source files. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r2-uv-cache uv run --no-sync lint-imports` | 0 | 3 contracts kept, 0 broken. |
| `test -s reports/reviews/W06/evaluation-core-independent-review-R2.md` | 0 | Review report exists and is non-empty. |
| `test -s reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R2.md` | 0 | Mandatory return exists and is non-empty. |

Focused normal-constructor probes for R1-01, R1-02, and R1-05 and deterministic metric probes for R1-03/R1-04 exited 0 and produced the exact counterexamples retained above. No protected fixture or protected verification artifact was accessed.

## Residual risk and scope

- Leakage/partition: a claim gate can still accept a protected-labelled run backed by FIT access; future query cutoff is unbound.
- Schema/digest: canonical roots do not compensate for non-canonical, duplicate evidence rows or opaque candidate-universe identity.
- Metric/applicability: partial arithmetic can exceed the unit range or fail; missingness/tie behavior is not fully protocol-executable; pair/agreement values lack governed identity.
- Interval/claim: stored point values, intervals, runs, and gates can mutually contradict one another while validating.
- Scope: no Git operations, dependency or lockfile changes, implementation/test edits, external/provider access, protected expected-output access, or writes outside the two R2 report paths occurred.

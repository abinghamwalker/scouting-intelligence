# W06 evaluation core independent review — R1

## Scope and verdict

- Review task: `W06-EVAL-CORE-REVIEW-01-R1`
- Reviewed implementation: `W06-EVAL-CORE-01-R1`
- Decision: **REWORK**
- Highest severity: **P0**
- Findings: **1 P0, 4 P1, 1 P2**

The implementation is not admissible for a protected comparison or a claim decision. The focused quality checks pass, but the contracts permit an `ACCEPT_CLAIM` object to be assembled from implementation-fixture evidence, a mismatched non-one-use `FIT` access record, an empty `PROTECTED_TEST` run, and a different protocol digest. Independently, the ranking core changes metric values or denominators for undeclared `k`, unjudged items, out-of-universe labels and ties; the Spearman and churn formulae produce invalid values; required pair-preference and inter-rater metrics are absent; and interval/result digests are not protocol-bound.

No protected expected output or W03 protected-attempt report was accessed.

## Finding summary

| ID | Severity | Finding | Material effect |
| --- | --- | --- | --- |
| W06-EC-R1-01 | P0 | Protected evidence, access, run and gate objects are not relationally bound, and implementation fixtures can reach `ACCEPT_CLAIM`. | Changes protected membership/access semantics and permits an unsupported protected claim decision. |
| W06-EC-R1-02 | P1 | Protocol/bundle roots do not bind nested queries, reviewers, rubrics, labels, preferences or adjudications; re-signed substitutions and duplicates are admitted. | Changes admitted evidence, label/reviewer/rubric identity and downstream denominators while preserving validation success. |
| W06-EC-R1-03 | P1 | Ranking evaluation does not enforce protocol-declared `k` or represent per-item irrelevant/unjudged/abstained state, candidate-universe membership or ties. | Changes Precision, Recall and NDCG values/denominators and makes tied results caller-order-dependent. |
| W06-EC-R1-04 | P1 | Rank comparison uses an invalid partial-universe Spearman calculation, unbounded churn, and omits required pair-preference/inter-rater metrics and explicit top-k overlap. | Produces wrong or out-of-range stability metrics and leaves required gate evidence unavailable. |
| W06-EC-R1-05 | P1 | Bootstrap settings/results, `MetricResult`, intervals and aggregate run ordering are insufficiently declared and bound. | Allows arbitrary metric values, undeclared `k`, inverted/unmatched intervals, unstable run digests and resample-digest collisions across materially different inputs. |
| W06-EC-R1-06 | P2 | Four focused tests do not exercise the claimed adversarial invariants, and the public JSON fixture is never loaded by the tests. | The suite passes while every P0/P1 counterexample above remains live; the fixture notice is documentary rather than enforced. |

## Findings and reproductions

### W06-EC-R1-01 — P0 — protected gate can accept fixture-only, unbound evidence

Evidence:

- `EvaluationBundle` has neither `schema_version` nor `bundle_digest` and contains no adjudications or access record (`src/scouting/contracts/evaluation.py:229-267`).
- A query's `feature_cutoff_ts` is self-digested but never checked against `protocol.decision_cutoff_ts` (`src/scouting/contracts/evaluation.py:99-115`, `229-267`).
- `IMPLEMENTATION_FIXTURE` is a valid evidence authority and is not prohibited in `PROTECTED_TEST`, `CALIBRATION` or `PROSPECTIVE` (`src/scouting/contracts/evaluation.py:62-65`, `118-141`, `229-267`).
- `EvaluationAccessRecord` only requires the boolean `one_use=True` when its own partition is protected. There is no consumption identity, candidate implementation digest or relation to a run (`src/scouting/contracts/evaluation.py:313-329`).
- `EvaluationRun` stores only opaque `protocol_digest` and `access_digest` strings, allows zero metric results, and does not validate access/protocol partition agreement (`src/scouting/contracts/evaluation.py:390-407`).
- `GateDecision` requires only a non-null run digest for `ACCEPT_CLAIM`; it does not validate a run, bundle, protected partition, access record, evidence authority, result roster or protocol equality (`src/scouting/contracts/evaluation.py:410-427`).

The executed constructor probe used these exact semantic inputs and every final constructor returned successfully:

| Object | Attack input | Accepted result |
| --- | --- | --- |
| Protocol | `declared_k=(1,)`, decision cutoff `2026-01-02T00:00:00Z` | valid |
| Query | feature cutoff `2026-01-03T00:00:00Z` | valid inside bundle despite being after decision cutoff |
| Evidence | authority `IMPLEMENTATION_FIXTURE` | valid in a query whose membership is `PROTECTED_TEST` |
| Access | partition `FIT`, `one_use=False`, protocol digest `9` repeated 64 times | valid |
| Run 1 | partition `PROTECTED_TEST`, points at the preceding FIT access digest | valid |
| Run 2 | same access digest reused, zero metric results | valid |
| Gate | `ACCEPT_CLAIM`, points at Run 2, protocol digest `7` repeated 64 times and therefore different from Run 2 | valid; equality output was `false` |

The probe also returned `same_access_reused_for_second_run=true` and `empty_metric_protected_run_accepted=0`. This is a direct protected-decision and claim-boundary bypass, not only a schema incompleteness.

Smallest bounded correction:

1. Introduce one canonical aggregate whose digest recomputes from the actual protocol, rubric, exact reviewer roster, queries, memberships, evidence, preferences, hard negatives and adjudications in a declared canonical order.
2. Reject query feature cutoffs after the protocol cutoff and prohibit implementation-fixture authority from calibration, protected, prospective and claim-eligible aggregates.
3. Bind a protected access object to the same protocol, partition, frozen bundle, preregistered implementation/candidate and one consumption/run identity; enforce uniqueness outside a caller-supplied boolean.
4. Make a claim gate validate the actual nested run and aggregate: same protocol/bundle/access, protected partition, required non-empty metric/slice/interval roster, governed eligible evidence only, and no unmatched/unavailable primary result. `GateDecision` must not be constructible from unrelated digest strings.

### W06-EC-R1-02 — P1 — nested digests and governed evidence can be substituted

Evidence:

- The four protocol root fields are accepted as arbitrary SHA-256-shaped strings and are not recomputed from the bundle. In the probe, `protocol.query_digest` was `aa…aa`, the actual nested query digest was `c12da27045777b53999d1e584cabee5f5c0d25e5f573eacf8320423159d39d8e`, and the unequal pair was accepted (`src/scouting/contracts/evaluation.py:205-267`).
- Reviewer checking is conditional on a non-empty roster and applies only to relevance rows. Preferences have no roster check; rubric identity is never compared with the protocol (`src/scouting/contracts/evaluation.py:247-266`).
- Relevance rows have no uniqueness rule. The same row was admitted twice, returning `duplicate_relevance_count_accepted=2`.
- Pair identity is directional and ignores `preference_id`; two reversed pairs with the same ID and a non-roster reviewer were admitted. Their digests were `51878c543a732f94772f9750ce5ebdf15020f8e3e765cdd1751d08ece46444c3` and `f00a058523d91f4aa5d9165864e7586c8a49a6ab8e6a48e3f4d50f02d0046bdf`.
- A re-signed relevance row changed label `RELEVANT→IRRELEVANT`, reviewer key/digest and rubric digest, recomputed its leaf digest, and was admitted when the optional roster was empty. Accepted digest: `13a8bbf54516643c7c4c7f6016b90fc39e7c2a27fc920c0bc1f7a01a1bac9b77`.
- `Adjudication` is not a field of `EvaluationBundle`; a standalone adjudication referencing `("missing1", "missing2")` and adjudicator `nobody` validated (`src/scouting/contracts/evaluation.py:294-310`).

Smallest bounded correction:

- Recompute all protocol roots from canonical nested digest sequences and add a self-verifying aggregate digest.
- Require the exact governed reviewer roster for governed evidence; bind every evidence and preference rubric/reviewer to it and to the protocol rubric.
- Define canonical semantic identities and uniqueness for evidence IDs, `(query,candidate,reviewer,rubric)` labels, unordered candidate pairs, hard negatives and adjudications. Reject reversed duplicate pairs.
- Include adjudications in the aggregate; require referenced evidence to exist, concern one query/candidate/rubric, represent an actual disagreement, and use an eligible rostered adjudicator.
- Validate every evidence candidate against the query's frozen candidate universe and reject query/exemplar overlap consistently for relevance, pairs and hard negatives.

### W06-EC-R1-03 — P1 — ranking denominators, declared k and ties are not fail-closed

The implemented formulae are:

```text
captured = Σ[candidate_i ∈ relevant], i=1..k
Precision@k = captured / k
Recall@k = captured / |relevant|
gain_i = 1 if relevant, else 0.5 if partial, else 0
DCG@k = Σ gain_i / log2(i+1), i=1..k
IDCG@k = DCG of |relevant| unit gains plus |partial| half gains
NDCG@k = DCG@k / IDCG@k
```

These are visible at `src/scouting/evaluation/core.py:28-53`. `evaluate_ranking` accepts only `(row, k)` and cannot inspect `EvaluationProtocol.declared_k` despite its docstring claiming to refuse undeclared values.

Executed counterexamples:

- Protocol `declared_k=(1,)`; `evaluate_ranking(RankingRow("q", ("a","b"), {"a"}), 2)` computed Precision `1/2=0.5`, Recall `1/1=1.0`, NDCG `1.0` and coverage `2/2=1.0` instead of rejecting undeclared `k=2`.
- Candidate `b` had no label at all, yet the same call silently put it in the precision denominator and treated it as zero gain: Precision `0.5`.
- With the same ranking, changing the relevant set from `{"a"}` to `{"a","ghost"}` changed Recall from `1.0` (`1/1`) to `0.5` (`1/2`), although `ghost` was outside the ranked/candidate universe.
- `partial={"b"}`, `relevant={"a"}`, ranking `("b","a")`, `k=1` produced Precision `0.0`, Recall `0.0`, NDCG `0.5`; no protocol declares whether partial relevance counts for precision/recall or with what gain.
- `RankingRow` fields are only `query_id`, `ranking`, `relevant`, `partial`, `abstained` (`src/scouting/evaluation/core.py:15-21`). There is no explicit irrelevant/unjudged set, no per-item abstention, no score/tie group and no candidate-universe identity. Query-level `abstained=True` makes every metric unavailable, which cannot preserve mixed judged/unjudged/abstained items.
- The ideal list is derived from unconstrained sets, so out-of-ranking labels and overlaps between `relevant` and `partial` can change the denominator or double-count ideal gains.

Smallest bounded correction:

- Make evaluation consume a validated protocol plus a validated query/candidate label table, not unconstrained sets.
- Give every candidate an explicit mutually exclusive state (`RELEVANT`, `PARTIAL`, `IRRELEVANT`, `UNJUDGED`, reviewer abstention/adjudication state) and a declared policy for which states are eligible for each denominator. Missing/unjudged must make a row unavailable or be excluded according to the frozen protocol, never default to irrelevant.
- Require all labels to belong to the frozen candidate universe, keep relevant/partial/irrelevant sets disjoint, and enforce `k in protocol.declared_k`.
- Carry score/tie groups and a frozen deterministic tie policy (including candidate-ID fallback), or fail closed when a cutoff intersects an unresolved tie.
- Declare partial gain and its Precision/Recall treatment in the protocol; use that same declaration to build DCG and IDCG.

### W06-EC-R1-04 — P1 — comparison math is wrong/incomplete

The code applies

```text
rho = 1 - 6 Σ(left_absolute_position(item) - right_absolute_position(item))²
          / (n (n² - 1))
```

to only the common items (`src/scouting/evaluation/core.py:82-88`). That shortcut is valid for two complete, tie-free permutations of the same `n` items, not absolute positions of a partial intersection.

Executed counterexamples:

- Left `("x","a","b")`, right `("a","b","y")`: common items `a,b` have the same relative order, so their rank correlation is `+1`; implementation returned `-1.0`.
- Left `("a","b")`, right `("x","y","a","b")`: implementation returned `-7.0`, outside Spearman's `[-1,1]` range.
- Disjoint top-2 rankings returned `candidate_churn=2.0`. The implementation is `|left_top Δ right_top|/k`, whose range is `[0,2]` (`src/scouting/evaluation/core.py:89-93`). Replacement churn must be bounded: `1-|intersection|/k = |Δ|/(2k)` for equal-size top-k lists.
- The only exported functions are `evaluate_ranking`, `bootstrap_interval` and `rank_comparison` (`src/scouting/evaluation/__init__.py:3-5`). There is no pair-preference score, eligible non-abstaining denominator, inter-rater agreement, or explicit top-k overlap value. No protocol declares the intended correlation/agreement method or tie behavior.

Smallest bounded correction:

- Either require the exact same complete candidate universe and compute Spearman on valid ranks, or rerank the declared intersection before correlation; declare and test the chosen population/tie policy.
- Return both overlap count/rate and Jaccard, and use bounded replacement churn.
- Implement pair-preference accuracy with an explicit eligible real-reviewer/non-abstaining denominator and canonical unordered pair identity.
- Implement and protocol-declare an inter-rater statistic suitable for the label scale, including eligibility, missingness, abstention, ties and insufficient-denominator behavior.

### W06-EC-R1-05 — P1 — result, interval and digest bindings are insufficient

Bootstrap formula (`src/scouting/evaluation/core.py:56-73`): canonically sort queries by ID, draw `n` query values with replacement for each resample, sort the resample means, and select indices `floor(alpha*(B-1))` and `ceil((1-alpha)*(B-1))`. This is deterministic for the tested input order, but none of seed, resample count, confidence, method, metric roster or resampling unit is declared by `EvaluationProtocol` (`src/scouting/contracts/evaluation.py:205-226`).

Material reproductions:

- Renaming both query IDs while retaining their values produced the same resample digest `51b70694b610e2c65de96af6f7487a89cfb9301728ad9e9ae4c14fb393e52c41`.
- Changing confidence from `0.9` to `0.8` also produced the same digest. The implementation hashes only sorted sample means, not query identities, `k`, metric, seed, resample count, confidence or method (`src/scouting/evaluation/core.py:72`). `resample_digest` is not a field of `BootstrapInterval`.
- A `MetricResult(metric="precision", k=2, value=2.0, numerator=1, denominator=2)` validated although the protocol declared only `k=1`, the value was outside `[0,1]`, and `2.0 != 1/2`. Accepted result digest: `0e3b07a3504dab6d01abf6ac10680a1977133596d74d2a851e0a4c3065da0e5c` (`src/scouting/contracts/evaluation.py:270-291`).
- A computed interval with method `anything`, lower `1.0`, upper `0.0`, and a nonexistent metric-result digest validated. Accepted interval digest: `6189314f40b51bdc6e4aa65393e3a670a8f011548640653ff68a472be46e57f6` (`src/scouting/contracts/evaluation.py:332-354`).
- Reversing two otherwise identical metric results in a run changed the accepted run digest from `8538f6e977e977a12001bf3c1b2b15eb223ee97a9743cace412a8ccd7c742bc3` to `34c80d94c3fbe20fc95542648c7e454e2271bf43984b4720dfbee20f7456f884`. No canonical semantic order is enforced (`src/scouting/contracts/evaluation.py:390-407`).

Smallest bounded correction:

- Freeze resampling unit, seed, count, confidence, method/quantile convention, metric roster, canonical query order and insufficient-row policy in the protocol.
- Bind a resample/input digest to query IDs, per-query metric values/statuses, metric, `k` and every bootstrap setting, in addition to sample outputs.
- Use metric enums/declarations with value ranges and formula-specific numerator/denominator checks; require `k` to be declared.
- Require interval method equality, `lower <= point <= upper`, no bounds for unavailable intervals, and an exact link to a metric result in the same run.
- Enforce semantic uniqueness and canonical order for metrics, intervals, slices and failures before hashing; require the gate's declared primary result roster to be present.

### W06-EC-R1-06 — P2 — focused tests do not prove the stated invariants

The two test files contain four tests total and pass in `0.16s`. Coverage gaps are material:

- The supposed reviewer-substitution test creates no `ReviewerIdentity` and attempts no substitution; the success path depends on the empty-roster bypass (`tests/contracts/test_w06_evaluation_contracts.py:32-49`).
- The digest test checks only an unknown field with an intentionally wrong leaf digest; it does not perform a re-signed substitution (`tests/contracts/test_w06_evaluation_contracts.py:52-54`).
- No test covers protocol root recomputation, bundle/run/gate aggregate binding, duplicate relevance, reversed pair identity, preference reviewer/rubric checks, candidate-universe membership, feature cutoff leakage, adjudication, access reuse/mismatch, empty protected runs, fixture authority or a gate decision.
- No metric test covers declared-k enforcement, per-item unjudged/abstention, partial Precision/Recall policy, ties, label-set disjointness, out-of-universe labels, pair preference, inter-rater agreement, complete/intersection Spearman semantics, disjoint churn, overlap rate, bootstrap protocol settings/digest binding, interval arithmetic or result/run canonical ordering (`tests/unit/test_w06_evaluation_metrics.py:7-28`).
- `rg` found `public-evaluation-v1` only inside the fixture itself; the tests inline separate rows and never load `tests/fixtures/w06/public-evaluation-v1.json`. The fixture parses as two rows, SHA-256 `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`, and carries a clear `IMPLEMENTATION_FIXTURE_ONLY` notice, but that notice is not enforced by the contracts or tests.

Smallest bounded correction: add one public-fixture-driven mathematical test matrix plus adversarial contract tests for every invariant and counterexample in W06-EC-R1-01 through W06-EC-R1-05. Assert rejected construction, exact status/reason/denominator, exact formula values and stable canonical digests.

## Direct answers to the packet review questions

1. **Do aggregate protocol/bundle/run/gate digests bind every nested object and canonical identity? — No.** Leaf and run self-digests recompute their own serialized payload, but the protocol roots are opaque, the bundle has no digest, adjudications/access are not nested, the gate holds unrelated digest strings, and run collections are not canonically ordered.
2. **Can substitution, duplication, overlap or access attacks change admitted evidence without rejection? — Yes.** Re-signed label/reviewer/rubric substitution with an empty roster, non-roster pair reviewers, reversed same-ID pairs, duplicate relevance, nonexistent adjudication references, FIT-access substitution/reuse and protocol-mismatched gates were all accepted. Only the narrow tested query-ID equality overlap and same-query cross-membership cases fail.
3. **Does the core enforce declared k and preserve per-item unjudged/missing/abstention? — No.** The core has no protocol argument and no per-item judged/abstention state; absent labels become zero gain/precision misses.
4. **Are partial relevance, ties, insufficient denominators and universe limits defined and deterministic? — No.** Partial gain is hard-coded only for NDCG, Precision/Recall treatment is undeclared, ties cannot be represented, out-of-universe labels alter denominators, and only short ranking length has an explicit insufficiency reason.
5. **Are pair preference, eligible agreement, Spearman, overlap/Jaccard, bounded churn and disagreement lists correct? — No.** Pair and inter-rater metrics are absent; Spearman is wrong for partial intersections and can leave `[-1,1]`; churn reaches `2`; Jaccard and canonical ID-only disagreement lists work for the simple tie-free set case; explicit overlap is absent.
6. **Are bootstrap unit/settings/order/arithmetic/digests stable and contract-bound? — Partly deterministic, but no.** Query sorting and seeded draws are stable for the narrow test, but settings are not in the protocol, the sample digest omits identities/settings, interval links/arithmetic are unchecked, and aggregate ordering is unstable.
7. **Do public fixtures prove implementation math only and avoid expert/protected/claim evidence? — Documentary yes, enforceable no.** The JSON is clearly labelled implementation-only and contains no real/expert/prospective content, but tests never load it and the contract accepts implementation-fixture evidence in a protected claim path.
8. **Do focused tests exercise the required fail-closed and mathematical invariants? — No.** They exercise four happy/narrow cases and miss every reproduced P0/P1 attack.

## Verification command ledger

All commands ran from `/Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence`. No command accessed a protected path.

| Exact command | Exit | Concise result |
| --- | ---: | --- |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 2 | Global uv cache denied at `/Users/adrian/.cache/uv/sdists-v9/.git`; no tests ran. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | `4 passed in 0.16s`. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | All checks passed. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | No issues in 3 source files. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | 3 contracts kept, 0 broken. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python -c 'import hashlib,json,pathlib; p=pathlib.Path("tests/fixtures/w06/public-evaluation-v1.json"); d=json.loads(p.read_text()); print(d["fixture_id"],d["evidence_class"],hashlib.sha256(p.read_bytes()).hexdigest(),len(d["rows"]))'` | 0 | Fixture ID/class, digest and 2-row count reproduced. |
| `test -s reports/reviews/W06/evaluation-core-independent-review-R1.md` | 0 | Independent report exists and is non-empty. |
| `test -s reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R1.md` | 0 | Mandatory return exists and is non-empty. |

The metric and contract counterexamples were executed as inline `python -c` probes under the same task-specific-cache prefix. Their exact semantic inputs, formulae, returned values and accepted identifiers are retained in W06-EC-R1-01 through W06-EC-R1-05; they were exploratory reproductions rather than packet acceptance commands.

Two earlier iterations of the contract attack probe exited `1` before exercising a contract because the review-only helper initially omitted Pydantic default fields, then attempted to hash nested Pydantic objects as raw Python values. The final helper canonicalized nested objects with `model_dump(mode="json")`; the successful results above come only from normal validated constructors, not `model_construct` outputs.

## Residual risks and handoff

- **Leakage/protected access:** a post-decision query feature cutoff is admitted; one-use is a caller assertion rather than consumed state; fixture authority is not partition/claim restricted.
- **Schema/digest:** no rubric aggregate, bundle digest, adjudication binding, candidate roster or protected decision envelope exists; semantic collection order is not canonical.
- **Interval/statistics:** settings are caller-controlled, primary results are not linked, and wrong/out-of-range values validate.
- **Applicability:** slice definitions are opaque digests and are not connected to the protocol population, evidence coverage or gate narrowing decision.
- **Claim:** `ACCEPT_CLAIM` proves only that a run-shaped digest string is present, not that governed protected evidence supports the resemblance claim.

Required handoff: issue bounded rework covering all P0/P1 corrections and tests, then obtain a fresh independent material review. Do not execute or interpret a protected result through this contract version.

## Scope confirmation

- Files written by this review are only:
  - `reports/reviews/W06/evaluation-core-independent-review-R1.md`
  - `reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R1.md`
- No Git operation was run.
- No dependency or lockfile was changed.
- No implementation, test, fixture, orchestration, config, data, run, documentation or protected file was edited.
- No protected expected output or W03 protected-attempt report was read.
- No delegation or self-approval occurred.

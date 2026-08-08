# W06 evaluation core independent review — R3

## Verdict

**RETURN FOR REWORK.** R3 materially improves every R2 family and fully closes the
canonical evidence-aggregate family, but the protected decision boundary is still open.
The exact remaining inventory is **1 P0, 4 P1, and 1 P2**. In particular, an
`ACCEPT_CLAIM` can bind a mixed FIT/PROTECTED_TEST bundle without any run-level evaluated
query roster, and it can bind a bundle whose embedded protocol differs from the gate/run
protocol. A protected `NARROW_APPLICABILITY` can also validate with no relevance rows and
only an `UNSUPPORTED` metric.

This was a fresh, report-only, public-structure review. No protected expected output was
opened, executed, or inferred.

## Review-question adjudication

| Review question | Answer | Material evidence |
|---|---|---|
| Does R3 close every R2 P0/P1 constructor, aggregate, metric, comparison and interval counterexample? | **No.** | R2 aggregate attacks now reject, but protected gate lineage, zero-positive precision, pair/comparison identity, negative sufficient statistics, interval range, and unsupported-primary configuration defects survive. |
| Can a `NO_GO` immutably retain and bind an available negative bundle/access/run while still allowing explicit missing population? | **No.** | No-evidence `NO_GO` validates, but a complete bundle/run is rejected, while a run-only orphan validates. |
| Can `ACCEPT_CLAIM` or `NARROW_APPLICABILITY` bind mixed/non-protected memberships or pass without governed evidence required by the claimed population? | **Yes.** | Mixed-membership `ACCEPT_CLAIM`, protocol-substituted `ACCEPT_CLAIM`, and zero-relevance `NARROW_APPLICABILITY` all validated. |
| Do `MetricResult` and `BootstrapInterval` reject negative sufficient statistics and out-of-unit-range unit-metric bounds? | **No.** | `(-1)/(-2)=0.5` validates; a precision interval `[-1,2]` around `0.5` and its linked run validate. |
| Are metric, interval, slice, failure and comparison identities canonical, unique and persistable without substitution? | **No.** | Individual contract digests reject an arbitrary digest, but pair outputs collide across different predictions, agreement orientation changes identity, rank comparison has no identity, and duplicate slice/failure rows validate. |
| Do focused tests reproduce all decision-affecting cases, and do declared static checks pass? | **No.** | Six tests pass, but none covers the surviving gate/value/identity attacks; the declared Ruff command fails on `contracts/__init__.py`. |

## Findings

### P0 — Protected decision lineage is not bound to one protocol and one evaluated protected query population

`GateDecision` compares the gate protocol only with `run.protocol`; it does not compare
`bundle.protocol.protocol_digest` with either one. `EvaluationRun` carries a bundle-wide
digest but no canonical evaluated-query roster, evaluated-membership digest, or per-result
query-population identity. The gate therefore cannot establish that its metric and
interval values came from the protected queries whose evidence it inspects.

Three normal-constructor probes validated:

- `ACCEPT_CLAIM` over memberships `['FIT', 'PROTECTED_TEST']`, with a computed
  precision/interval but no evaluated-query roster: independent gate digest
  `6a8fb2d6680f040a3e7148cc8b03464c2840526427f7447332e0434f6986a884`.
  The converged master constructor has gate digest
  `013f2376e78166f376f50b6955f8a81073469028a016666cef8a0ea28094cb8a`.
- `ACCEPT_CLAIM` where the gate/run protocol digest is
  `42fd1161c03a6ff36273d93780acff7c19fb89fba75d0ac2013b8e7053b2280c`
  but the nested bundle protocol digest is
  `a9020476b7a53bd15e0dc9cecf45327adb84c4869585af69407e3adca46016ee`:
  gate digest `22920e4fb7b1dd319082abd854dbbd82806207d114daa9a70d1a5b79f75a6925`.
- Protected `NARROW_APPLICABILITY` with zero relevance rows and sole result
  `UNSUPPORTED / MISSING_EXPERT_RELEVANCE_EVIDENCE`: independent gate digest
  `d8c6564b1a1f9fab2c32b87375f9b206b6b2871ec34121bb13897c9b43cad3e1`;
  the converged master constructor has gate digest
  `a28a06a242db776e750a921dcf5ebadb810edd14ddccd119843cd1db2df8edd4`.

Impact: a positive protected claim can be authorized without proving which protected
query population produced its values, and with a protocol substituted across the bundle
boundary. Narrowing can be asserted without governed relevance for the population being
narrowed. This is a retained P0 claim-integrity path.

Smallest correction: add a canonical non-empty `evaluated_query_ids`/digest relation to
the access and run, require each evaluated query to exist in the bound bundle and have the
run partition, bind every aggregate result and resample identity to that roster, and
require the gate protocol to equal `bundle.protocol` as well as `run.protocol`. Require
`ACCEPT_CLAIM` and `NARROW_APPLICABILITY` evidence/results to cover the same governed
evaluated population; a missing-expert population must yield an explicit negative
decision, not an ungrounded narrowing.

### P1 — `NO_GO` evidence retention is contradictory and permits orphan evidence

The equivalence at `GateDecision.valid` treats any evidence as forbidden for `NO_GO`
when both `bundle` and `run` are present, but permits exactly one orphan object:

```python
requires_evaluation = False
has_complete_evaluation = bundle is not None and run is not None
# False != True rejects a complete retained negative evaluation.
# False != False accepts bundle-only or run-only evidence.
```

Independent results:

- missing-population `NO_GO` with neither object validates, digest
  `1142b95b5cd05703e79e1b788735fca0f92414ac1e5ee4104a694ee9b0da3606`;
- `NO_GO` with the valid linked public bundle/run is rejected with
  `claim and narrowing decisions require an actual bundle and run`;
- `NO_GO` with the run but no bundle validates, gate digest
  `66c5c94e21114b772ca7e2d0bc82e5be658c4b317795b1df37d8ed6ac409be73`.

Impact: available negative evidence cannot be immutably retained at the gate, while an
unbound run can be recorded as if it were a coherent gate input.

Smallest correction: define exactly two valid `NO_GO` shapes: neither bundle nor run for
an explicit missing-population reason, or both bundle and run with the same full lineage
validation as other evaluated decisions. Reject exactly-one-object shapes.

### P1 — Precision availability and pair missingness do not implement their own denominators

R3 correctly uses the partial policy in both P/R numerators and recall denominator. It
then uses total eligible relevance to suppress *both* metrics. For a complete all-
irrelevant `k=1` row the exact formulas are:

```text
precision@1 = 0 / 1 = 0.0       (defined)
recall@1    = 0 / 0             (unavailable)
```

The implementation returned both as
`{value: None, numerator: None, denominator: None,
reason: no_eligible_relevance_denominator}`. The focused test codifies the same incorrect
precision behavior for an all-PARTIAL row when partial labels do not count for P/R.

Separately, a non-abstaining governed preference with
`PairPrediction.predicted_candidate_id=None` is silently counted as an incorrect result:
`value=0.0, numerator=0.0, denominator=1.0`. It is neither an explicit prediction
abstention nor unavailable/excluded.

Impact: a fully judged zero-positive ranking loses a valid precision value, and missing
pair predictions are indistinguishable from explicit incorrect predictions.

Smallest correction: always compute precision with denominator `k` after completeness
checks, independently make recall unavailable on zero eligible relevance, and give pair
predictions an explicit computed/abstained/missing state with protocol-declared inclusion
and exclusion behavior.

### P1 — Comparison, pair, agreement, slice, and failure identities are not canonical or unique

Fresh identity probes found:

- correct, wrong, and missing predictions for the same pair all emitted result identity
  `b44ef7b7e5e47692b010fbe0efd9e7e32f72f01bfaf74592781b732eee7060f6`
  even though their values were `1.0`, `0.0`, and `0.0`;
- swapping left/right orientation of the same semantic agreement row kept value `1.0`
  but changed identity from
  `ee60068e5a30f3c120c560dcc1dffbd1d2f89d12e561d4b843f02bc2cf3c37be`
  to `f1b4d39349f0d1e84e94e0738211ed1a7e6bca1625b65dbd6dcb89ca52c97ee1`;
- the agreement function accepted evidence rubric digest `aa…aa` against a different
  protocol rubric digest, because it binds the two rows to each other but not to the
  protocol/bundle;
- `rank_comparison` returns no result identity or persistable result contract;
- a slice containing the same `MetricResult` twice validated, and a run containing the
  same slice and failure twice validated. Identities were slice
  `6c501b99c770e3b697a12d9bc5c2e79e283933ab200ed162f2a3b10109934cd9`,
  failure `a77daf1a2a5772a4d1dd706547358436b6586ea952b8e39d032c96e5caab03f7`,
  and run `bb807e8a572233fd8d28e668901f4c7ba479f543518508e8ecbf4d12a18f411b`.

Impact: materially different comparison outputs can share an identity, the same
agreement can acquire multiple identities, and duplicate persisted rows can change
weight/content without a uniqueness failure.

Smallest correction: introduce typed comparison/pair/agreement result contracts whose
canonical preimages bind protocol, evaluated queries, governed input rows, prediction or
method, exclusions, sufficient statistics and result values. Canonicalize agreement
reviewer orientation. Require canonical unique child metric keys in slices and unique
slice/failure IDs, digests and semantic keys in runs.

### P1 — Metric/interval arithmetic and accepted protocol capability remain incomplete

The exact packet master counterexample validates unchanged:

```python
p = {
    "metric": MetricName.PRECISION,
    "k": 1,
    "value": 0.5,
    "numerator": -1.0,
    "denominator": -2.0,
    "status": MetricStatus.COMPUTED,
}
p["result_digest"] = _digest(
    MetricResult.model_construct(**p).model_dump(mode="json"), "result_digest"
)
MetricResult(**p)
```

It produces result digest
`af706ff4f29d3a37b0b7689415e4d1735756059fb6b0f534a1e8857822f002dd`.
The arithmetic and unit-valued result checks pass because negative numerator and
denominator are never rejected individually.

A computed precision result `0.5=1/2` linked to a computed interval with
`lower=-1.0, point=0.5, upper=2.0` also validates through `EvaluationRun`; interval digest
`784ec217b0cdd509e97a27d79e02e77bba1ec1a1bcd92d945381ae2dbe14ec04`,
run digest `b0d90cf25d63341e2ff8b67466211a1a5fadf2ad3a7f397fc433607fba09254e`.

Finally, a protocol with primary metric `AGREEMENT` validates, digest
`d2f6d2fa35eff1e1693a2ecb3f71244a82493fd51d700478a6c605632d5015b3`,
although `bootstrap_interval` immediately rejects that metric and the gate requires an
interval for every primary metric. The configuration is internally unachievable.

Impact: persisted sufficient statistics and uncertainty for unit metrics can be
semantically impossible, and a validated protocol can fail deterministically before any
claim can be assembled.

Smallest correction: require non-negative numerator and strictly positive denominator
for computed unit metrics; validate unit interval bounds through the linked metric type;
and reject at protocol construction any primary-metric/interval capability combination
that the run/gate contract cannot fulfill.

### P2 — Focused regression and static-check claims are incomplete

The six focused tests pass but do not cover any surviving counterexample above. In
particular, the all-PARTIAL test asserts unavailable precision instead of the declared
`P@k` formula. The declared Ruff command, which includes
`src/scouting/contracts/__init__.py`, fails with `I001` due to import ordering. The
producer's narrower Ruff command omitted that file.

Smallest correction: add one explicit regression per P0/P1 counterexample, correct the
zero-positive precision expectation, add gate population/protocol/NO_GO shape tests,
identity collision/duplicate tests, negative-stat and unit-bound tests, then sort the
export imports and run the literal reviewer check.

## R2 closure matrix

| R2 identifier | R3 status | Remaining severity | Independently reproduced closure | Surviving counterexample |
|---|---|---:|---|---|
| W06-EC-R1-01 | **OPEN (material partial closure)** | **P0** | False one-use rejects; FIT-access/PROTECTED-run mismatch rejects; non-empty run, access consumption, cutoff, primary result and interval checks exist. | Mixed-membership and protocol-substituted `ACCEPT_CLAIM` validate; zero-evidence `NARROW_APPLICABILITY` validates; complete negative `NO_GO` rejects while orphan run-only `NO_GO` validates. |
| W06-EC-R1-02 | **CLOSED** | none | Wrong candidate-universe digest, duplicate/reordered relevance, reversed pair, duplicate preference, duplicate hard negative, and cross-candidate adjudication all rejected with the intended validators. | none found within the bounded aggregate review. |
| W06-EC-R1-03 | **OPEN (substantial partial closure)** | **P1** | Partial-excluded row now gives P=`0.5`, R=`1.0`, NDCG=`1.0`; zero recall denominator no longer divides; NaN, negative zero and wrong tie order reject. | Fully judged all-irrelevant row incorrectly makes precision unavailable; non-abstaining pair prediction `None` is silently an incorrect observation. |
| W06-EC-R1-04 | **OPEN (partial closure)** | **P1** | Low-common top-1 now reports overlap `1`, rate/Jaccard `1.0`, churn `0.0`, empty disagreements; pair/agreement rows bind reviewer objects. | Pair identity ignores prediction; agreement orientation is non-canonical and rubric is not protocol-bound; rank comparison has no identity/persistence contract. |
| W06-EC-R1-05 | **OPEN (substantial partial closure)** | **P1** | `2.0 != 1/2` and inverted intervals reject; interval settings/result links and query-unit resample identity work; bootstrap row reorder retained digest `9d10c6843048b6ba92c31219baa7bbfb5cbdd3e7dcb46e0ce0ba959f30b86aca`. | Negative sufficient statistics, out-of-unit interval bounds, duplicate slice/failure rows, and unsupported primary metric configuration validate. |

## Master-counterexample adjudication

| Counterexample | Independent result | Adjudication |
|---|---|---|
| Negative precision sufficient statistics | Validated with exact digest `af706ff4…2dd`. | **SURVIVES, P1.** |
| `NO_GO` with valid linked bundle/run | Rejected; missing-population shape validates; orphan run-only shape also validates. | **SURVIVES, P1.** |
| Declared Ruff check includes `contracts/__init__.py` | Exit `1`, `I001 Import block is un-sorted or un-formatted`. | **SURVIVES, P2.** |
| Zero-relevance protected narrowing | Independent equivalent validated (`d8c6564b…d3e1`); master constructor identity `a28a06a2…dd4` retained. | **SURVIVES inside P0.** |
| Mixed-membership accepted claim without evaluated-query roster | Independent equivalent validated (`6a8fb2d6…a884`); master constructor identity `013f2376…b8a` retained. | **SURVIVES, P0.** |

## Acceptance and reproduction ledger

All Python checks used the existing locked environment with a task-local cache,
`--no-sync`, bytecode disabled, and pytest cache disabled so the report-only task did not
write outside its two allowed report paths.

| Command | Exit | Concise result |
|---|---:|---|
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | `6 passed in 0.16s`. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 1 | One `I001` in `src/scouting/contracts/__init__.py`. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation` | 0 | Success, no issues in three source files. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | Three contracts kept, zero broken. |
| Public-only inline constructor/metric probes via `uv run --no-sync python -c ...` | 0 each | Reproduced all identities and formulas stated above; no protected path opened. |
| `test -s reports/reviews/W06/evaluation-core-independent-review-R3.md` | 0 | Review exists and is non-empty. |
| `test -s reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R3.md` | 0 | Return exists and is non-empty. |

## Smallest bounded correction split

The two corrections overlap shared evaluation contracts and must remain serial:

1. **R4-A — critical gate population/lineage correction:** bind bundle protocol,
   canonical evaluated protected query roster, access/run/result/resample population, and
   governed evidence; implement the two valid `NO_GO` shapes and reject or reclassify
   ungrounded narrowing.
2. **R4-B — value/identity/static correction:** separate P@k and R@k availability,
   type pair prediction missingness, require non-negative statistics and unit interval
   bounds, reject unsupported primary configurations, add canonical comparison results
   and slice/failure uniqueness, add all adversarial tests, and sort exports.

R4-B should start only after R4-A fixes the result population preimage that comparison
and interval identities must bind.

## Residual risk and scope

- Leakage/partition: a positive claim does not prove that values came exclusively from
  its protected query membership, and the bundle protocol can be substituted.
- Schema/identity: negative sufficient statistics, broad unit intervals, identity
  collisions, non-canonical agreement orientation, and duplicate slice/failure rows
  remain persistable.
- Metric/applicability: defined zero precision is discarded; missing pair predictions
  become false observations; a narrowing can lack governed relevance.
- Interval/configuration: a primary metric can be accepted despite having no supported
  bootstrap path.
- Scope: no Git operation, dependency/lock change, protected expected-output access,
  external/provider access, implementation edit, or write outside the two authorized R3
  report paths occurred.

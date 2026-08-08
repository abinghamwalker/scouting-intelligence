# W06 evaluation gate/population binding independent review — R1

## Verdict

**RETURN FOR REWORK.** The split correction closes the exact R3 mixed-membership,
protocol-substitution, zero-relevance narrowing, top-level result/interval population,
and `NO_GO` orphan counterexamples. It does not yet make the whole protected relation
fail closed. The fresh inventory is **1 P0 and 1 P1**:

- a protected `ACCEPT_CLAIM` or `NARROW_APPLICABILITY` validates when every retained
  relevance row is a governed-human `ABSTAIN`, even though the public metric path treats
  an abstained population as unavailable;
- a protected run and retained-evidence `NO_GO` validate with a slice metric bound to a
  foreign evaluated-query digest and with a failure row naming an absent query.

This was a fresh report-only review using public synthetic constructors. No protected
expected output was opened, executed, or inferred. The reserved R3 metric-value,
comparison/identity, range, capability, duplicate-child, and static defects were not
re-reviewed except for the two child-population escapes above.

## Review-question adjudication

| Review question | Verdict | Fresh evidence |
|---|---|---|
| Do gate, bundle, and run bind exactly one validated protocol? | **PASS.** | Gate-protocol and run-protocol substitutions both rejected with `gate run must bind this protected protocol and bundle`; a substituted bundle also rejected. Every protocol object had its digest recomputed by its normal constructor. |
| Does one canonical roster bind access, run, every metric and interval, and exactly all protected memberships? | **FAIL, P1.** | Roster, access, top-level result, and interval digest substitutions rejected, and the gate selected exactly the protected membership set. But a `SliceResult.metric_results` child carrying the digest for `('foreign',)` validated inside a run whose roster was `('query',)`. |
| Can a non-protected/absent query enter, or can a protected query be omitted? | **PASS for the gate roster.** | FIT, TUNE, CALIBRATION, PROSPECTIVE, absent-query, protected-query-omission, and mixed-roster intrusions all rejected. A mixed bundle whose run selected exactly its protected subset validated, as intended. |
| Do positive decisions require governed relevance and computed primary results/intervals? | **FAIL, P0.** | Zero relevance, an unsupported primary result, and a missing primary interval rejected. Both positive decisions nevertheless accepted a protected query whose only governed relevance row was `ABSTAIN`. |
| Are the two `NO_GO` shapes exact and is retained negative evidence fully linked? | **FAIL, P1.** | Neither-object `NO_GO` accepted each single explicit missing reason and rejected arbitrary/multiple reasons. Both-object linked `NO_GO` accepted; bundle-only and run-only rejected. But the both-object shape retained a foreign-population slice metric and an absent-query failure. |
| Do caller substitutions fail under normal constructors? | **FAIL only for run children.** | Roster digest, access population digest, protocol, bundle, candidate manifest, access bundle, top-level result population, and interval population substitutions rejected. The nested slice-result and failure-query substitutions validated. |
| Do the exact R3 constructors reject without breaking coherent shapes? | **PASS, with new counterexamples.** | Mixed FIT/protected roster intrusion, protocol substitution, and zero-evidence narrowing rejected. Coherent `ACCEPT_CLAIM`, `NARROW_APPLICABILITY`, linked negative `NO_GO`, and both explicit missing-population `NO_GO` variants validated. |

## Findings

### P0 — Abstention-only protected evidence authorizes positive decisions

A public one-query protected bundle was built with one governed reviewer and one
`EvaluationEvidence` row whose label was `ABSTAIN`. Access, run, top-level precision
(`1/1`), and its computed interval were all bound to the canonical roster `('query',)`.
The normal `GateDecision` constructor accepted both positive shapes:

| Constructor | Actual result | Identity |
|---|---|---|
| `ACCEPT_CLAIM` + all-`ABSTAIN` protected relevance | accepted | `506ba104393a275f2a1a4a1f3916429ea0ac170fd76e3af488e5a028c27dd1f3` |
| `NARROW_APPLICABILITY` + all-`ABSTAIN` protected relevance | accepted | `80ba94ad92d69df980046bb1e5a8ce425294fc72893661faae8b60f35ab82e9a` |

`GateDecision._has_governed_human_evidence` checks only that each query has rows and that
their authority is governed; it never requires an eligible non-abstaining relevance
judgment. The public evaluation implementation explicitly makes any ranking containing
an abstained label unavailable with `incomplete_or_abstained_labels`. Therefore a caller
can attach invented computed primary values to a population with no usable relevance and
obtain a positive protected decision. This is the same claim/applicability integrity
class as the R3 zero-evidence constructor, not a reserved metric-value re-review.

Smallest bounded correction: for every evaluated protected query, require governed,
eligible concrete relevance after adjudication; an all-abstain query must fail positive
gate validation and resolve to the explicit missing-expert-evidence `NO_GO` path. Add
exact `ACCEPT_CLAIM` and `NARROW_APPLICABILITY` all-abstain regressions.

### P1 — Nested slice metrics and failure rows escape the run population

`EvaluationRun.valid` checks `evaluated_query_digest` only on top-level
`metric_results` and `intervals`. It does not traverse `SliceResult.metric_results`, and
it does not require `FailureResult.query_id` to belong to `evaluated_queries`. Two normal
public constructors therefore survived:

| Constructor | Actual result | Identity |
|---|---|---|
| protected run roster `('query',)` + slice metric digest for `('foreign',)` | accepted | run `4d24ccae6b5d800fb55fe20a99258ebb626294ca0c71a662fef216ae3b2d4581` |
| retained linked `NO_GO` over that run | accepted | gate `0b359ea3623bebcdfc8305fc0d575511aa245c20e38d8e89e78b8f658854636b` |
| protected run roster `('query',)` + failure `query_id='absent'` | accepted | run `6fe2869c9fbaa2dde5d9c14c58069758bd9ac76d636d9b99d47a989ace9eb78b` |
| retained linked `NO_GO` over that run | accepted | gate `318ea9d3b3638431cfa40d7d28af73b625b62f24578ef5e6b4188eb4b4eef559` |

This does not reopen the top-level primary-result or interval binding. It does mean that
the purported complete negative run can retain metrics and failures from outside the
protected population, so retained negative evidence is not yet one fail-closed relation.

Smallest bounded correction: validate every nested slice metric against the run's
evaluated-query digest (or give a slice an explicit canonical sub-roster constrained to
the run roster), and require every failure query ID to be in the run roster. Add both
constructors to the focused contract tests.

## Reproduction matrix

All payloads were synthetic and finalized through normal Pydantic constructors;
`model_construct` was used only to calculate the canonical digest preimage before normal
validation, matching the public test convention.

| Family | Constructor/result | Severity |
|---|---|---:|
| Coherent positive | Bound protected `ACCEPT_CLAIM` accepted (`ec19366f...e6ade`); bound protected `NARROW_APPLICABILITY` accepted (`1d31bdf9...54fbb`). | closure |
| Exact R3 mixed membership | FIT + PROTECTED roster rejected; exact protected subset of a mixed bundle accepted (`2a76e632...61e2d`). | closure |
| Partition completeness | FIT, TUNE, CALIBRATION, PROSPECTIVE, absent query, and omitted protected query all rejected with `evaluated query roster must exactly cover...`. | closure |
| Protocol/bundle/candidate/access | Gate protocol, run protocol, bundle, candidate manifest, and access-bundle substitutions all rejected with the relational gate error. | closure |
| Roster/result/interval | Wrong roster digest, access population digest, top-level metric population, and interval population all rejected at their owning relation. | closure |
| Positive evidence/results | Zero relevance rejected; unsupported primary rejected; missing interval rejected; all-abstain evidence accepted for both positive decisions. | **P0** |
| Missing-population negative | Each single `NoGoReason` accepted; arbitrary and multiple reasons rejected. | closure |
| Retained negative shape | Complete linked bundle/run accepted (`b4eb8984...ba7f1`); bundle-only and run-only rejected. | closure |
| Retained negative children | Foreign-population slice metric and absent-query failure each validated through linked `NO_GO`. | **P1** |

## Commands and results

All caches and bytecode were directed away from the repository.

| Command | Exit | Result |
|---|---:|---|
| Initial public-constructor inline harness: `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-review-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python - <<'PY' ... PY` | 1 | Harness-only digest helper omitted model default fields; first `MetricResult` correctly rejected its miscomputed digest. No review conclusion used this run. |
| Corrected 33-case public-constructor matrix via the same `uv run --no-sync python` heredoc | 0 | 28 expected closures reproduced; five unexpected accepts reduced to the two findings above. |
| Focused eight-witness public-constructor matrix via the same `uv run --no-sync python` heredoc | 0 | Both all-abstain positive gates accepted; missing/unsupported primary requirements rejected; foreign slice metric and absent-query failure each validated at run and retained `NO_GO`. |
| `PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | `8 passed in 0.29s`. |
| `uv run --no-sync ruff check src/scouting/contracts/evaluation.py tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | All checks passed. |
| `uv run --no-sync mypy src/scouting/contracts/evaluation.py` | 0 | Success; no issues in one source file. |
| `uv run --no-sync lint-imports` | 0 | Three contracts kept, zero broken. |
| `test -s reports/reviews/W06/evaluation-gate-binding-independent-review-R1.md` | 0 | Review exists and is non-empty. |
| `test -s reports/reviews/W06/returns/W06-EVAL-GATE-BINDING-REVIEW-02-R1.md` | 0 | Mandatory return exists and is non-empty. |

## Residual risk and bounded follow-up

- **Population/leakage:** the canonical top-level roster relation is closed, but nested
  slice metrics and failure rows can describe a foreign or absent query population.
- **Claim/applicability:** a positive protected decision can be issued with no eligible
  relevance judgment because governed abstention is treated as governed relevance.
- **Negative retention:** object shape and top-level linkage are correct; child evidence
  remains population-substitutable.
- **Intervals:** top-level interval population and primary-interval presence checks
  closed in the reproduced matrix; no new interval defect was found in this split.
- **Reserved work:** the R3 metric arithmetic/missing-prediction, comparison identity,
  range/capability, duplicate-child, and static findings remain reserved for the next
  serial packet and were not adjudicated here.

No Git operation, dependency/lock change, protected expected-output access,
external/provider access, implementation edit, or write outside the two authorized
review paths occurred.

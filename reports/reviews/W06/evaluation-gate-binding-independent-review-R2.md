# W06 evaluation gate/population binding independent review — R2

## Verdict

**ACCEPT.** A fresh 30-case public-constructor matrix reproduced all six R2
residual/master constructors and the bounded R1 relation regressions. Both positive
decisions now reject all-`ABSTAIN` and mixed concrete-plus-`ABSTAIN` governed relevance
under `REQUIRE_COMPLETE`; a foreign-population metric nested in a slice and a failure
naming an absent query both reject at `EvaluationRun` construction. Coherent concrete
positive decisions, an exact protected subset, retained in-population negative evidence,
and both explicit missing-population `NO_GO` reasons remain constructible.

No P0 or P1 remains in the gate/population split. No protected expected output was
opened, executed, or inferred. Reserved metric arithmetic/value, comparison identity,
range/capability, duplicate-child, and static work was not reopened.

## Review-question adjudication

| Review question | Verdict | Fresh evidence |
|---|---|---|
| Do all-`ABSTAIN` and mixed concrete-plus-`ABSTAIN` relevance reject for both positive decisions? | **PASS.** | `ACCEPT_CLAIM` and `NARROW_APPLICABILITY` each rejected both evidence shapes with `claim or narrowing requires governed evidence for every evaluated protected query`. |
| Does a coherent complete governed positive shape still validate? | **PASS.** | Concrete governed `ACCEPT_CLAIM` (`4ac0f31f...2c594`) and `NARROW_APPLICABILITY` (`d4b3ccc7...97c00`) validated. |
| Do foreign nested slice metrics and absent/non-rostered failures reject at run construction? | **PASS.** | The foreign digest rejected with `slice metric results must bind the run evaluated query population`; the absent failure rejected with `failure query must belong to the run evaluated query population`. |
| Do exact protocol, protected roster, access, top-level result/interval and both `NO_GO` closures remain intact? | **PASS.** | Protocol, bundle, candidate-manifest, access, roster, result and interval substitutions rejected. Linked retained-evidence and both explicit neither-object `NO_GO` forms accepted; arbitrary/multiple missing reasons and either orphan shape rejected. |
| Can a normal-constructor substitution alter evaluated membership, retained negative population, or positive eligibility in this split? | **PASS (no surviving substitution).** | Non-protected intrusion, protected omission, absent-roster selection, foreign retained children, zero relevance, abstention, unsupported primary result, and missing primary interval all rejected at their owning relation. |

## Fresh constructor matrix

All final payloads used normal Pydantic constructors. `model_construct` was used only to
calculate each canonical digest preimage, following the public test convention.

| Family | Public constructor and result | Severity |
|---|---|---:|
| Coherent positives | Bound concrete governed `ACCEPT_CLAIM` and `NARROW_APPLICABILITY` accepted (`4ac0f31f...2c594`, `d4b3ccc7...97c00`). | closure |
| R2 all-abstain | All-`ABSTAIN` `ACCEPT_CLAIM` rejected; all-`ABSTAIN` `NARROW_APPLICABILITY` rejected. | former P0 closed |
| R2 mixed abstain | Concrete-plus-`ABSTAIN` `ACCEPT_CLAIM` rejected; concrete-plus-`ABSTAIN` `NARROW_APPLICABILITY` rejected. | former P0 closed |
| R2 slice population | Run with nested slice metric digest for `('foreign',)` rejected at run construction. | former P1 closed |
| R2 failure population | Run with `FailureResult(query_id='absent')` rejected at run construction. | former P1 closed |
| Retained negative children | Linked `NO_GO` retaining a slice metric for `('query',)` and a failure for `query` accepted (`e5b4a77f...92ef5`). | closure |
| Protected membership | Exact protected subset of a FIT/protected bundle accepted (`5287053e...80952`); non-protected intrusion, protected omission, and absent-roster substitution rejected. | closure |
| Protocol and aggregate binding | Run-protocol, gate-protocol, bundle, candidate-manifest and access-bundle substitutions rejected. | closure |
| Access and top-level population | Access-population, top-level metric-population and top-level interval-population substitutions rejected. | closure |
| Positive prerequisites | Zero relevance, unsupported primary result and missing primary interval rejected. | closure |
| Neither-object `NO_GO` | Each single `MISSING_EXPERT_RELEVANCE_EVIDENCE` and `MISSING_PROTECTED_POPULATION` reason accepted (`225ec75f...941a`, `3c983659...f7095`); arbitrary and multiple reasons rejected. | closure |
| Linked-object `NO_GO` | Fully linked retained-evidence shape accepted; bundle-only and run-only shapes rejected. | closure |

The matrix contained 30 cases: six expected accepts and 24 expected rejects. Every case
matched its expected outcome. The digest-preimage helper emitted one non-fatal Pydantic
serializer warning when the alternate protocol's already-validated nested rubric was
temporarily represented as its Python-mode dictionary; the final public
`EvaluationProtocol` constructor validated, and neither the identity nor rejection
conclusion depended on bypassed validation.

## Commands and results

All caches and bytecode were directed outside the repository.

| Command | Exit | Result |
|---|---:|---|
| `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r2-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python - <<'PY' ... PY` | 0 | Fresh 30-case matrix: 6 expected accepts, 24 expected rejects, zero mismatches. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r2-review-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | `9 passed in 0.17s`. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r2-review-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r2-review-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py` | 0 | All checks passed. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r2-review-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r2-review-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py` | 0 | Success; no issues in one source file. |
| `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r2-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports` | 0 | Three contracts kept, zero broken. |
| `test -s reports/reviews/W06/evaluation-gate-binding-independent-review-R2.md` | 0 | Review exists and is non-empty. |
| `test -s reports/reviews/W06/returns/W06-EVAL-GATE-BINDING-REVIEW-02-R2.md` | 0 | Mandatory return exists and is non-empty. |

## Residual risk and bounded correction

- **Population:** closed within this split. Run, access, top-level metrics/intervals,
  nested slice metrics and failure queries remain bound to the canonical evaluated
  roster; no slice sub-population protocol was introduced.
- **Negative retention:** the coherent linked `NO_GO` can retain in-population slice and
  failure children, while both foreign-child forms fail before a gate can retain them.
- **Applicability and claim:** coherent concrete governed shapes remain eligible; zero,
  all-abstain and partially abstained relevance cannot authorize either positive shape.
- **Reserved work:** metric arithmetic/value, missing prediction, comparison identity,
  range/capability, duplicate-child and static findings remain owned by the later serial
  split and are not adjudicated here.

Remaining counterexamples in the reviewed gate/population relation: **none**. Smallest
bounded correction: **none**.

No Git operation, dependency/lock change, protected expected-output access,
external/provider access, implementation edit, or write outside the two authorized R2
review paths occurred.

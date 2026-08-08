# W05 M0 query and ranking contracts independent review R2

- Task: `W05-CONTRACTS-QUERY-REVIEW-02`
- Reviewed surface: current `src/scouting/contracts/m0.py` and `tests/contracts/test_w05_m0_contracts.py`
- Date: 2026-08-03
- Verdict: **PASS**
- Severity: **P0: 0; P1: 0; P2: 0**

The R1 same-ID semantic-query blocker is closed. `PinnedM0ServingRequest` now retains an
independently supplied `expected_resolved_query_digest`, requires exact equality with
the nested query's self-verified digest, and remains included in the outer result digest.
The fixed-pin substitution fails for the exact independent-pin mismatch after both
attacker-controlled digests are recomputed. No regression was found in the accepted
query/ranking checks.

## Six W05 blocker tests

| Blocker test | Outcome | R2 evidence |
| --- | --- | --- |
| 1 — admitted byte change | PASS | Same-ID semantic query bytes cannot change while the independent expected pin stays fixed. |
| 2 — leakage or lineage substitution | PASS | A reused brief ID/version cannot carry substituted responsibilities past the fixed upstream query pin. |
| 3 — parity | PASS | The independently pinned resolved query remains exact at the serving/result boundary. |
| 4 — false claim | PASS | Substituted query semantics and all request/result claim drift probes reject. |
| 5 — local-only or authority violation | PASS | No external/provider access or unauthorised write was used or found. |
| 6 — reproducible P0/P1 defect | PASS | No P0/P1 correctness or security defect reproduced in the bounded surface. |

## R1 closure

The new field is explicit on `PinnedM0ServingRequest` (`m0.py:654-658`). Validation
compares the independently supplied pin with `resolved_query.resolved_query_digest`
before the existing request overlap and taxonomy checks (`m0.py:670-703`). It is not a
default, computed field, or validator overwrite. The fixture supplies it explicitly
(`test_w05_m0_contracts.py:238-265`).

The direct R1 attack preserved tenant, trace, brief ID/version, taxonomy, cutoff, limit,
exclusions, artifact pins, and the expected query pin; changed `pressing` to
`progression` and the matching weight code; then recomputed `resolved_query_digest` and
`result_digest`. Strict public validation produced:

```text
SAME_ID_QUERY_FIXED_PIN_REJECTED expected_resolved_query_digest must match resolved_query.resolved_query_digest
```

This is the intended closure reason. The committed focused test performs the same attack
and asserts the exact mismatch (`test_w05_m0_contracts.py:567-584`).

The expected pin is also bound by the outer canonical result projection because the
complete pinned request is a field of `M0RetrievalResult` and `digest_for_payload` hashes
the complete payload except `result_digest` (`m0.py:850-879`). A second probe changed to
a valid new query and updated the independent expected pin, but retained the original
outer result digest:

```text
OUTER_RESULT_BINDS_EXPECTED_PIN_REJECTED result_digest must equal
```

## Regression probes

All probes used `uv run --no-sync python -B`, existing producer fixtures, and strict
public model validation. No construction bypass, external system, source edit, or test
edit was used.

```text
NEGATIVE_ZERO_DISTANCE_REJECTED negative zero
NEGATIVE_ZERO_CONTRIBUTIONS_REJECTED negative zero
IDENTITY_DRIFT_TENANT_REJECTED
IDENTITY_DRIFT_TRACE_REJECTED
IDENTITY_DRIFT_BRIEF_ID_REJECTED
IDENTITY_DRIFT_BRIEF_VERSION_REJECTED
IDENTITY_DRIFT_CUTOFF_REJECTED
IDENTITY_DRIFT_CLAIM_REJECTED
EXCLUSION_DRIFT_REJECTED cannot include a pinned excluded player
FEATURE_AXIS_MISMATCH_REJECTED must exactly match artifact feature_names length
INVERSE_UUID_EQUAL_TIE_REJECTED distance then canonical player UUID bytes
```

The exclusion probe recomputed the retrieval request exclusions, resolved-query
exclusions and digest, expected query pin, ordered-exclusion digest, and result digest;
the candidate remained rejected. The feature-axis and equal-tie probes likewise
recomputed the outer digest. Existing result identity, claim, feature-axis, order,
limit, and exclusion validators remain unchanged in effect (`m0.py:898-957`).

## Review-question answers

1. **Independent pin and outer binding:** the required field exactly matches the nested
   verified digest, is explicitly supplied, and is part of the outer result digest.
   **Pass.**
2. **Fixed-pin same-brief substitution:** semantic responsibility/weight substitution
   fails for the exact expected-query-digest mismatch after recomputing both
   attacker-controlled digests. **Pass.**
3. **Regression surface:** negative zero, tenant/trace/brief/cutoff/claim drift,
   exclusions, feature-axis mismatch, and inverse-UUID equal ties all reject. **Pass.**

## Acceptance checks

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py` | 0 | 58 passed in 0.18s |
| `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py` | 0 | All checks passed |
| `uv run mypy src/scouting/contracts/m0.py` | 0 | Success; no issues in 1 source file |
| `uv run lint-imports` | 2 | Sandbox denied the shared uv cache path before analysis |
| `UV_CACHE_DIR=/tmp/w05-contracts-query-review-02-r2-uv-cache uv run --no-sync lint-imports` | 0 | 3 contracts kept, 0 broken; 40 files/79 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | status PASS; failures `[]` |
| Direct R2 adversarial/regression probes | 0 | Fixed-pin attack and every named regression probe rejected |

## Scope and residual risk

No residual P0, P1, or P2 finding remains in this bounded query/ranking packet. No
smallest remaining correction is required. Candidate-specific evidence, W04
descriptor/array semantics, and explanation equality remain intentionally reserved to
the serial follow-on packet and were not reviewed as R2 defects.

Only this report and the required R2 return were written. No source, test, config,
orchestration, dependency/lock, accepted W04 byte, data/run, phase-gate, or verification
path was changed. No Git command, delegation, self-approval, provider/network/external
service, dependency change, or destructive action occurred.

# W05 M0 query and ranking contracts independent review R1

- Task: `W05-CONTRACTS-QUERY-REVIEW-02`
- Reviewed surface: current `src/scouting/contracts/m0.py`, its retrieval/workflow dependencies,
  and the two packet-named contract test files
- Date: 2026-08-03
- Verdict: **REWORK**
- Severity: **P0: 0; P1: 1; P2: 0**

The query/ranking split closes result identity drift, canonical numeric handling,
feature-axis cardinality, and executable distance/UUID ordering. One narrow blocker
remains: `M0ResolvedQuery` verifies a digest supplied inside the same substitutable
object, while `PinnedM0ServingRequest` retains no independent expected query-content
identity. Consequently a different query can reuse the same brief ID/version and be
accepted after recomputing both self-digests.

## Controlling blocker tests

Findings use the six W05 tests: (1) admitted feature, artifact, ranking or result-byte
change; (2) temporal leakage or lineage substitution; (3) training-serving or
batch-request parity break; (4) false explanation, confidence or claim; (5)
unauthorised code/data or local-only violation; (6) reproducible P0/P1
correctness/security defect.

| Blocker test | Outcome | Evidence |
| --- | --- | --- |
| 1 | FAIL | Same-ID resolved-query semantic bytes can change and still validate after digest recomputation. |
| 2 | FAIL | The accepted brief identity can be associated with substituted resolved responsibilities. |
| 3 | FAIL | A serving request can validate a query different from the upstream resolution for the same brief ID/version. |
| 4 | FAIL | The wrapper can claim the substituted resolved query as the replayable query. |
| 5 | PASS | No external/provider access or local-only violation was found or used. |
| 6 | FAIL | The acceptance is directly reproducible through strict public model validation. |

## Finding

### P1-1 — same-ID resolved-query substitution is accepted after recomputing digests

**Blocker tests: 1, 2, 3, 4, 6.** `M0ResolvedQuery` contains the complete requested
projection (`m0.py:372-392`) and hashes every field except `resolved_query_digest`
(`m0.py:394-406`). Its validator only compares that supplied digest with a digest
recomputed from the same object (`m0.py:408-435`). `PinnedM0ServingRequest` embeds the
query but has no independent expected resolved-query digest (`m0.py:650-657`); it
cross-checks request overlaps and taxonomy pins only (`m0.py:669-698`).

A direct strict-model probe changed responsibility `pressing` to `progression` and
changed its matching weight code while preserving tenant, trace, brief ID/version,
taxonomy, cutoff, limit, exclusions, and every artifact pin. It recomputed the nested
query digest and outer result digest and produced:

```text
SAME_ID_QUERY_SUBSTITUTION_ACCEPTED ('progression',)
```

This is not cured by the outer result digest: that digest authenticates the substituted
wire projection (`m0.py:856-874`) rather than preserving the originally resolved query.
The focused producer test changes `trace_id` and is correctly rejected by request
overlap (`test_w05_m0_contracts.py:553-559`), but it does not mutate semantic query
content while keeping all overlaps and the brief identity unchanged.

**Smallest bounded correction:** retain an independently supplied expected
resolved-query digest in `PinnedM0ServingRequest` alongside, not instead of, the full
typed query, and require it to equal the query's already verified digest. Add a direct
test that substitutes responsibilities/weights under the same brief ID/version,
recomputes `resolved_query_digest` and `result_digest`, leaves the independent expected
pin unchanged, and requires rejection. This mirrors the accepted independent artifact
manifest pin without adding free text, learned-query state, a dependency, or follow-on
truth work.

## Review-question answers

1. **Resolved-query completeness:** tenant, trace, brief ID/version, taxonomy
   ID/version/digest, ordered responsibilities/weights/constraints/exemplars/query
   player, cutoff, limit, exclusions, uniqueness checks, and a canonical digest are
   present. The digest is self-consistent but not independently pinned against same-ID
   semantic substitution. **No, blocking.**
2. **Pinned request overlaps and claim:** tenant, trace, brief ID/version, cutoff,
   limit, exclusions, taxonomy pins, and the resemblance-only boundary are checked.
   Overlap substitutions reject, but non-overlapping semantic query substitution is
   accepted after recomputation. **Partial, blocking.**
3. **Scored candidates:** distance and contributions are finite and reject negative
   zero; distance is non-negative; player/rank and all three vector lengths bind to the
   artifact feature axis (`m0.py:439-454,923-936`). **Pass.**
4. **Total order:** ordering is executable as ascending distance then canonical UUID
   bytes, and inverse UUID equal ties reject (`m0.py:937-943`). **Pass.**
5. **Result/request drift:** request ID, tenant, trace, brief ID/version, cutoff,
   request/result/candidate claim boundary, limit, and exclusions fail closed even with
   a recomputed result digest (`m0.py:893-952`). **Pass.**
6. **Scope separation:** the producer did not implement candidate-specific dimension
   state, W04 descriptor/array truth, or explanation equality reserved to the serial
   follow-on packet. **Pass.**

## Direct adversarial probes

All probes used `uv run --no-sync python -B` with the existing strict public models and
producer fixtures. No `model_construct`, mutation bypass, source edit, provider, or
external system was used.

```text
SAME_ID_QUERY_SUBSTITUTION_ACCEPTED ('progression',)
NEGATIVE_ZERO_REJECTED distance
NEGATIVE_ZERO_REJECTED contributions
IDENTITY_DRIFT_REJECTED tenant
IDENTITY_DRIFT_REJECTED trace
IDENTITY_DRIFT_REJECTED brief_id
IDENTITY_DRIFT_REJECTED brief_version
IDENTITY_DRIFT_REJECTED cutoff
EXCLUSION_DRIFT_REJECTED
INVERSE_UUID_EQUAL_TIE_REJECTED
```

The packet's parameterised test additionally covers recomputed-digest result claim drift
(`test_w05_m0_contracts.py:604-630`). Request and candidate claims are closed literals,
and result validation requires every candidate claim to equal the pinned request claim
(`m0.py:912-920`). Limit enforcement is executable at `m0.py:945-947`.

## Acceptance checks

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py` | 0 | 57 passed in 0.18s |
| `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py` | 0 | All checks passed |
| `uv run mypy src/scouting/contracts/m0.py` | 0 | Success; no issues in 1 source file |
| `uv run lint-imports` | 2 | Sandbox denied the shared uv cache path before analysis |
| `UV_CACHE_DIR=/tmp/w05-contracts-query-review-02-uv-cache uv run --no-sync lint-imports` | 0 | 3 contracts kept, 0 broken; 40 files/79 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | status PASS; failures `[]` |
| Direct adversarial probe | 0 | One same-ID query blocker reproduced; all named safety probes above rejected |

## Scope and residual risk

Residual W05 risk is limited to query-content authority under a reused brief identity.
No P0 or P2 finding was identified. Candidate-specific state, W04 descriptor/array
truth, and explanation equality remain intentionally reserved to
`W05-CONTRACTS-TRUTH-03` and were not reclassified as defects here.

Only this report and the required return were written. No source, test, config,
orchestration, dependency/lock, accepted W04 byte, data/run, phase-gate, or verification
path was changed. No Git command, delegation, self-approval, provider/network/external
service, dependency change, or destructive action occurred.

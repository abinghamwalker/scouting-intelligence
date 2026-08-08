# W05 M0 contracts independent review R1

- Task: `W05-CONTRACTS-REVIEW-01`
- Reviewed bytes: current post-R2 `src/scouting/contracts/m0.py` and `tests/contracts/test_w05_m0_contracts.py`
- Date: 2026-08-03
- Verdict: **REWORK**
- Severity: **P0: 0; P1: 6; P2: 0**

The R2 manifest digest closes the two narrow R1 same-ID substitution findings, but the
current contract does not close every accepted architecture-preflight P1. In particular,
the declared tie policy is not executable from result content, the request/result pair is
not one self-contained resolved query, evidence state is not candidate-specific,
explanations are not derived from the artifact feature projection, signed zero is not
canonical, taxonomy content is not addressed, and W04 feature authority remains partly
opaque/misnamed. A recomputed result digest authenticates substituted bytes; it does not
make those bytes true.

## Controlling blocker tests

Findings use the exact six tests from the architecture preflight: (1) admitted feature,
artifact, ranking or result-byte change; (2) temporal leakage or lineage substitution;
(3) training-serving or batch-request parity break; (4) false explanation, confidence or
claim; (5) unauthorised code/data or local-only violation; (6) reproducible P0/P1
correctness/security defect.

## Findings

### P1-1 — ranking and request/result identity are not contract-verifiable

**Blocker tests: 1, 2, 3, 4, 6.** `M0TiePolicy` is only an enum
(`m0.py:298-303`); candidates carry no canonical primary distance/score or secondary key.
The wrapper checks only contiguous ranks, limit and exclusions (`m0.py:680-687`). Two
candidates with identical visible evidence were accepted in descending UUID order even
though the declared final key is canonical UUID bytes:

```text
EQUAL_VISIBLE_SCORES_UUID_TIE_VIOLATION_ACCEPTED
['00000000-0000-0000-0000-000000000002',
 '00000000-0000-0000-0000-000000000001']
```

The wrapper cross-checks only `retrieval_request_id` (`m0.py:675-678`). With that ID held,
changed result `role_brief_id`, `role_brief_version` and `trace_id` were accepted after
recomputing the digest:

```text
REQUEST_RESULT_BRIEF_TRACE_DRIFT_ACCEPTED 99 True True
```

The request has only an opaque `resolved_role_brief_query_digest` (`m0.py:463`), not the
resolved responsibilities, weights, exemplars or hard constraints. Thus it is neither a
self-contained typed query nor able to validate its own digest. Smallest correction:
add a canonical scored-candidate projection (finite canonical distance/score plus UUID),
validate total ordering and ranks, embed a typed resolved query projection and derive its
digest, and cross-check tenant, trace, brief identity/version, cutoff and claim boundary
between request and result.

### P1-2 — canonical numeric and PCA handling is incomplete

**Blocker tests: 1, 3, 4, 6.** `_finite_number` checks only finiteness
(`m0.py:55-62`) and ZERO uses equality with zero (`m0.py:101-103`). Both ZERO and VALUE
accept `-0.0` and serialize it distinctly:

```text
NEG_ZERO_ACCEPTED {"state":"zero","numeric_value":-0.0,"reason_code":null}
                  {"state":"value","numeric_value":-0.0,"reason_code":null}
```

Descriptor metadata binds declared dtype/shape/order, but the family does not require the
arrays needed by its semantics. A PCA artifact containing only `FEATURE_MATRIX` was
accepted:

```text
PCA_WITHOUT_PCA_ARRAYS_ACCEPTED ['feature_matrix']
```

Therefore the contract cannot validate PCA component signs/order, centre, scale,
explained values or transformed bytes; it merely declares two policy enum values.
Smallest correction: reject or normalize signed zero before all canonical projections;
define one numeric encoding; require family-specific ordered descriptor roles and
shape relations (including feature axis, PCA components/variance/centre/scale and index
rows); validate the canonical orientation/order against admitted numeric content at the
artifact loading boundary.

### P1-3 — dimension evidence is global, ZERO is collapsed operationally, and W04 can claim unsupported role-fit

**Blocker tests: 1, 4, 6.** `dimension_evidence` is one six-item result tuple with no
`player_id` (`m0.py:637,688-701`), then reused for every candidate (`m0.py:702-739`). It
cannot represent candidate A measured and candidate B missing/suppressed. ZERO is a
distinct enum but the validator classifies every non-MEASURED state identically and
forbids it from ranking (`m0.py:574-589,732-739`):

```text
DIMENSION_ZERO_ACCEPTED_ONLY_NONRANKING
{"name":"style_resemblance","state":"zero",...,"contributes_to_ranking":false}
```

For W04 real evidence, only impact, trajectory and transfer risk are prohibited from
MEASURED (`m0.py:740-750`), despite the accepted W04 card also saying role-fit scores are
unavailable. A W04 artifact/result with measured, ranking `ROLE_COMPATIBILITY` was
accepted. The authoritative confidence/coverage/legacy data-confidence equality itself
is sound, but it does not cure these other dimensions. Smallest correction: attach the
six state records to each candidate; distinguish observed numeric ZERO from absence and
permit it wherever measured zero legitimately ranks; derive admissible measured
dimensions from evidence class/registry, explicitly suppress W04 role compatibility,
and validate each legacy dimension against that candidate's state.

### P1-4 — explanations can be fabricated and re-signed

**Blocker tests: 1, 4, 6.** Explanation validation checks only duplicate feature names
and reason codes (`m0.py:605-620`). The baseline artifact names two features while its
accepted explanation includes only one. Replacing that input with another feature,
arbitrary values, contribution `12345.0`, and `fabricated_reason`, then recomputing the
result digest, was accepted:

```text
EXPLANATION_INCOMPLETE_BASELINE 2 1
EXPLANATION_SUBSTITUTION_ACCEPTED {"inputs":[{"feature_name":"match_count",
 "query_value":{"numeric_value":99.0},"candidate_value":{"numeric_value":-7.0},
 "contribution":12345.0}],"reason_codes":["fabricated_reason"]}
```

Smallest correction: require exact artifact feature order and cardinality (including
explicit missing/suppressed states), bind exact query/candidate transform values and
weights/contrasts, derive contributions and ordered reasons under the declared family,
and reject rather than merely re-digest any mismatch.

### P1-5 — taxonomy content can change under the same identity

**Blocker tests: 1, 3, 4, 6.** The taxonomy carries only ID/version and uniqueness/dangling
checks (`m0.py:143-174`), with no canonical digest or canonical responsibility/role/mapping
order. Two taxonomies with the same ID/version but reversed responsibilities, reordered
role responsibilities and changed role label were both accepted and had different JSON
bytes. The artifact pins only taxonomy ID/version (`m0.py:344-345`). The rewritten test
file contains no taxonomy or contextual-membership test at all (its six tests begin at
line 355 and cover feature state, manifest, arrays, request and result).

Smallest correction: add a self-verifying taxonomy digest over canonical ordered
responsibilities, roles and mappings; pin it in artifact/request/result; define and
validate canonical orders; add strict contextual probability, unknown-role, context,
mapping and same-ID substitution tests.

### P1-6 — W04 authority is exact in roster but not exact/unambiguous in descriptor authority

**Blocker tests: 1, 2, 4, 6.** The feature ID and exact four-name order are correctly
closed (`m0.py:64-73,424-430`), so a broader roster cannot use `W04_REAL_GOVERNED`.
However, `W04_REAL_GOVERNED_REGISTRY_DIGEST` is populated from the config's
`decision_sha256` (`config:12-13`), while the field is named
`feature_registry_canonical_digest`; and `feature_descriptor_digest` is unconstrained for
W04. A real manifest with descriptor digest `f*64` and a 2-column feature matrix for the
four-feature roster was accepted:

```text
W04_ROLE_COMPATIBILITY_MEASURED_ACCEPTED measured True
descriptor_digest ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
matrix_shape (1, 2)
```

Smallest correction: name and bind the accepted decision digest as a decision digest,
derive/pin the canonical registry and exact-four descriptor digest separately, and enforce
descriptor feature-axis agreement. Preserve the current exact-four roster rejection.

## Review-question answers

1. **Same-ID content substitution:** artifact manifest fields are content-addressed and
   request-pinned, but taxonomy content is not; explanation/query content can be changed
   and re-signed; family-specific PCA arrays are not required. **No.**
2. **Canonical numeric handling:** finite checks and descriptor metadata exist, but
   signed zero, family/shape relations and actual PCA orientation/order validation do not.
   **No.**
3. **Tie policy:** it is declared but cannot be validated from explicit result values;
   UUID-inverted equal visible scores validate. **No.**
4. **Self-contained query:** target IDs, cutoff, exclusions and opaque digest are present,
   but the resolved brief/exemplars/constraints are not. **No.**
5. **Dimension/confidence:** confidence projection equality passes; candidate-specific
   state, meaningful ZERO and W04 role-fit suppression do not. **No.**
6. **Explanation:** candidate/rank alignment passes; exact artifact order, complete state,
   input truth, reasons and contributions do not. **No.**
7. **Taxonomy:** membership code enforces finite, sorted, exact decimal sum and taxonomy
   role existence, but taxonomy content identity/order and R2 tests are incomplete.
   **No.**
8. **W04 authority:** exact ID/four-name order blocks broader families, but digest naming,
   descriptor authority/shape and W04 role-fit claim boundary are not exact. **Partial,
   still blocking.**

## Acceptance checks

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py` | 0 | 50 passed in 0.14s |
| `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py` | 0 | All checks passed |
| `uv run mypy src/scouting/contracts/m0.py` | 0 | no issues in 1 source file |
| `uv run lint-imports` | 2 | sandbox denied read of `/Users/adrian/.cache/uv/sdists-v9/.git` |
| `UV_CACHE_DIR=/tmp/w05-contracts-review-uv-cache uv run --no-sync lint-imports` | 0 | 3 kept, 0 broken; 40 files/78 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | status PASS; failures `[]` |

Direct probes were executed through `uv run python -B - <<'PY'` and constructed the
strict public models from the producer fixtures, changed one bounded surface, recomputed
the documented digest, and printed the acceptance results quoted above. No bypassed
object was the final validation target.

## Risks, W10 separation, and scope

Residual W05 risk is false ranking/explanation/taxonomy/role-fit evidence and batch/request
drift, not external access. The initial import-lint failure is a sandbox/cache visibility
condition; the isolated `/tmp` cache rerun passed and it is not promoted to W05. Cache,
inode/link, timestamp, temporary-path spelling and equivalent host metadata remain
**W10-only** absent a reproduced path through blocker tests 1-6; none was found here.

Only this report and the required return were written. No source, test, config,
orchestration, dependency/lock, data/run, Git, phase-gate or verification byte was
changed. No Git command, delegation, self-approval, provider/network/external service or
destructive action occurred.

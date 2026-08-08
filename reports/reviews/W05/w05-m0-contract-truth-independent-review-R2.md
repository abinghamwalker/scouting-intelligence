# W05 M0 contract truth independent review R2

- Task: `W05-CONTRACTS-TRUTH-REVIEW-03`
- Reviewed bytes: current R2 `src/scouting/contracts/m0.py` and `tests/contracts/test_w05_m0_contracts.py`
- Date: 2026-08-03
- Verdict: **PASS**
- Severity: **P0: 0; P1: 0; P2: 0**

All three R1 P1 classes are closed. Independent strict-model replay shows every prior
accepted mutation now fails at normal Pydantic validation for the intended state,
authority, fitting-axis or PCA-capacity reason. The authorized positive surfaces remain
open: exactly four W04 real-governed families validate, all six synthetic families
validate, observed ZERO remains evidence-bearing, and fitting and candidate row counts
may legitimately differ.

No residual issue reproduces through any of the six W05 blocker tests: (1) admitted
feature/artifact/ranking/result-byte change; (2) temporal leakage or lineage substitution;
(3) training-serving or batch-request parity break; (4) false explanation, confidence or
claim; (5) unauthorized code/data or local-only violation; or (6) reproducible P0/P1
correctness/security defect.

## R1 attack replay

All result attacks recomputed the documented `result_digest`; all manifest attacks used
normal strict construction with the complete descriptor bundle and computed manifest
digest.

| R1 attack | R2 outcome | Intended rejection |
| --- | --- | --- |
| MEASURED style with legacy score `0.0` | rejected | `MEASURED dimension evidence requires a strictly positive legacy score` |
| MEASURED state reason drift | rejected | `dimension evidence reasons must exactly match the legacy dimension` |
| ZERO state reason drift | rejected | `dimension evidence reasons must exactly match the legacy dimension` |
| DATA_CONFIDENCE score zero labelled MEASURED | rejected | state must be derived from confidence score |
| DATA_CONFIDENCE ZERO with contradictory state reasons | rejected | state reasons must exactly match legacy projection |
| W04 `METADATA_CONTROL` | rejected | incompatible `W04_REAL_GOVERNED` family |
| W04 `ROLE_AWARE_RESTRICTION` | rejected | incompatible `W04_REAL_GOVERNED` family |
| fitting count `2` with feature matrix `(1, 2)` | rejected | feature matrix must bind fitting population and feature counts |
| PCA 2 components with 1 fitting sample | rejected | PCA component count exceeds fitting population |
| PCA 3 components with 2 features | rejected | PCA component count exceeds feature count |

The independent command printed:

```text
R1_MEASURED_ZERO REJECTED strictly positive legacy score
R1_MEASURED_REASON_DRIFT REJECTED reasons must exactly match
R1_ZERO_REASON_DRIFT REJECTED reasons must exactly match
R1_DATA_CONFIDENCE_MEASURED_ZERO REJECTED derived from confidence score
R1_DATA_CONFIDENCE_ZERO_REASON_DRIFT REJECTED reasons must exactly match
R1_W04_METADATA_CONTROL REJECTED W04_REAL_GOVERNED
R1_W04_ROLE_AWARE_RESTRICTION REJECTED W04_REAL_GOVERNED
R1_FIT_FEATURE_AXIS_DRIFT REJECTED fitting population
R1_PCA_FITTING_OVERFLOW REJECTED PCA component count
R1_PCA_FEATURE_OVERFLOW REJECTED PCA component count
```

## Positive-boundary and regression evidence

Exactly these four W04 families validate with the frozen W04 identities:

```text
raw_euclidean_control
robust_scaled_cosine
weighted_cosine
pca
```

All six `M0ModelFamily` values validate under `SYNTHETIC_DEVELOPMENT`, including metadata
control and role-aware restriction. A distinct-axis weighted artifact validated with
`FEATURE_MATRIX=(2, 2)`, `INDEX_VECTORS=(3, 2)` and `INDEX_PLAYER_IDS=(3, 16)`, proving
fitting rows are independent of candidate index rows.

The following retained attacks also rejected through strict contracts or the focused
direct test functions:

- explanation contribution substitution after result re-digest;
- incomplete/fabricated explanation input projection;
- same-ID changed taxonomy content and contextual-membership drift;
- W04 descriptor identity drift;
- negative-zero feature/distance/contribution values;
- request/result `trace_id` drift after result re-digest;
- inverse UUID ordering at equal distance;
- missing/reordered PCA and family semantic roles, W04 two-column feature matrix, and
  PCA index-shape drift through the focused suite.

## Review-question answers

1. **MEASURED/ZERO and DATA_CONFIDENCE truth:** MEASURED-zero, MEASURED and ZERO reason
   drift, DATA_CONFIDENCE state drift, and DATA_CONFIDENCE reason drift all reject after
   result re-digest. Canonical ZERO remains valid and may rank where admitted. **Yes.**
2. **W04 and synthetic family compatibility:** only raw Euclidean, robust cosine,
   weighted cosine and PCA validate for W04; metadata and role-aware reject; synthetic
   retains all six. **Yes.**
3. **FEATURE_MATRIX and index rows:** feature-matrix rows bind
   `fitting_population_count`; index vectors and UUID rows independently bind
   `candidate_universe_count`. **Yes.**
4. **PCA capacity and retained topology:** components are bounded by both fitting samples
   and feature count while component/variance/index shapes and both PCA policies remain
   required. **Yes.**
5. **Retained truth surfaces:** exact explanations, taxonomy content identity, all three
   W04 digests, negative zero, query/result identity, and distance/UUID ties remain
   closed. **Yes.**

## Acceptance checks

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_supported_feature_authority.py` | 0 | 216 passed in 9.51s |
| `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py` | 0 | all checks passed |
| `uv run mypy src/scouting/contracts/m0.py` | 0 | no issues in 1 source file |
| `uv run lint-imports` | 2 | sandbox denied read of `/Users/adrian/.cache/uv/sdists-v9/.git` before analysis |
| `UV_CACHE_DIR=/tmp/w05-contracts-truth-review-03-r2-uv-cache uv run --no-sync lint-imports` | 0 | 3 kept, 0 broken; 40 files/79 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | PASS; failures `[]` |
| strict direct R1/regression probes through `uv run python -B -` | 0 | every expected rejection and positive admission matched |

The exact import-lint invocation remains affected only by the pre-existing unreadable
shared uv cache; the isolated no-sync execution analyzed the installed project and passed.
This is not a W05 blocker.

## Scope and residual risk

No W05 P0/P1/P2 finding remains. Loader implementation, numeric-content PCA orientation
checking at load time, cache metadata, inode/link behavior and equivalent physical-host
concerns remain later-wave work and were not promoted without a reproduction through the
six W05 blocker tests.

Only this report and the mandatory R2 return were written. No source, test, config,
orchestration, accepted predecessor, dependency/lock, data/run, phase-gate or verification
byte was changed. No Git operation, delegation, self-approval, provider/network access or
destructive action occurred.

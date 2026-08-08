# W05 M0 contract truth independent review R1

- Task: `W05-CONTRACTS-TRUTH-REVIEW-03`
- Reviewed bytes: current `src/scouting/contracts/m0.py`, `tests/contracts/test_w05_m0_contracts.py`, unchanged accepted W04 YAML and acceptance JSON
- Date: 2026-08-03
- Verdict: **REWORK**
- Severity: **P0: 0; P1: 3; P2: 0**

The split implementation closes the earlier candidate-alignment, exact-explanation,
taxonomy-content, W04 identity, negative-zero and basic family-topology findings. It does
not yet make the final truth surface non-contradictory. Strict public-model attacks,
including recomputed documented digests where applicable, admit contradictory dimension
states, W04-governed artifacts in semantically unauthorised families, a feature matrix
whose fitting axis disagrees with the fitting population, and impossible PCA component
counts.

These are contract-boundary P1s, not loader-later or W10-only observations. The packet
expressly requires candidate state truth and executable family array relationships in the
manifest/result contracts. Each accepted attack can therefore change admitted ranking,
claim, fitting, or artifact interpretation bytes before any future loader exists.

## Controlling blocker tests

Findings use the six W05 tests from the architecture preflight: (1) admitted feature,
artifact, ranking or result-byte change; (2) temporal leakage or lineage substitution;
(3) training-serving or batch-request parity break; (4) false explanation, confidence or
claim; (5) unauthorised code/data or local-only violation; (6) reproducible P0/P1
correctness/security defect.

## Findings

### P1-1 — evidence state, legacy score and reasons can contradict

**Blocker tests: 1, 4, 6.** Candidate ownership, rank alignment and enum order are now
enforced, but the state projection is only joined to legacy values for absence states and
the ZERO score (`m0.py:1162-1179`). MEASURED has no non-zero rule and neither MEASURED nor
ZERO requires state reasons to equal legacy reasons. DATA_CONFIDENCE is forced non-ranking,
but its state and state reasons are not projected from the authoritative confidence object.

Direct strict-model attacks accepted after recomputing `result_digest`:

```text
MEASURED_ZERO_ACCEPTED measured 0.0
MEASURED_REASON_DRIFT_ACCEPTED
  state=('contradictory_state_reason',)
  legacy=('style_resemblance_measured',)
DATA_CONFIDENCE_ZERO_REASON_DRIFT_ACCEPTED
  state=zero
  state_reasons=('contradictory_data_state_reason',)
  legacy_reasons=('coverage_complete', 'applicability_applicable')
```

This collapses the required operational distinction between observed ZERO and MEASURED
and permits a visible confidence-state narrative that contradicts the exact confidence
projection. Smallest bounded correction: require MEASURED legacy score to be non-zero;
require ZERO to be canonical `+0.0`; require MEASURED/ZERO state reasons to equal legacy
reasons; and derive DATA_CONFIDENCE state as ZERO exactly when its authoritative score is
zero, otherwise MEASURED, with exact projected reasons.

### P1-2 — W04 real authority is not bound to a compatible model family

**Blocker tests: 1, 2, 3, 4, 6.** The exact W04 registry ID, candidate digest, decision
digest, descriptor digest and four-feature order are enforced (`m0.py:729-740`), and W04
ROLE_COMPATIBILITY result evidence is correctly suppressed. However, the manifest applies
no evidence-class/family compatibility rule. Both of these strict, fully content-addressed
manifests validate:

```text
W04_FAMILY_ACCEPTED role_aware_restriction w04_real_governed
W04_FAMILY_ACCEPTED metadata_control w04_real_governed
```

`ROLE_AWARE_RESTRICTION` claims a role-aware family over W04 authority whose accepted
registry explicitly marks `role_inferred_count` unavailable and whose W05 result boundary
forbids W04 role compatibility. `METADATA_CONTROL` simultaneously labels the exact four
governed count features as a metadata-control family. Result-level role suppression does
not cure the artifact-family claim. Smallest bounded correction: add an explicit
evidence-class/model-family compatibility allow-list and reject at least these two
combinations for `W04_REAL_GOVERNED`; add direct construction tests for every admitted and
rejected combination.

### P1-3 — fitting and PCA dimensional bounds are not executable

**Blocker tests: 1, 2, 3, 6.** `FEATURE_MATRIX` is bound to
`candidate_universe_count` (`m0.py:700-703`) while the independently pinned
`fitting_population_count` is never related to an array. PCA relates components,
variance and index width (`m0.py:715-726`) but does not enforce the mathematical bound
`component_count <= min(fitting_population_count, feature_count)`.

Strict, re-digested manifests accepted:

```text
FIT_FEATURE_AXIS_DRIFT_ACCEPTED fitting_population_count=2 feature_matrix_shape=(1, 2)
PCA_COMPONENT_OVERFLOW_ACCEPTED fitting_population_count=1 feature_count=2 components=(3, 2)
```

The first manifest cannot describe its declared fitting population; the second cannot be
the output of a legitimate PCA fit for either its sample or feature bound. These are
training-serving/artifact parity defects at the W05 manifest boundary, not facts that a
future loader may safely reinterpret. Smallest bounded correction: bind the
`FEATURE_MATRIX` first axis to `fitting_population_count`, continue binding index arrays
and UUID rows to `candidate_universe_count`, and require PCA component count not to exceed
either fitting samples or feature count.

## Review-question answers

1. **Candidate-specific six-dimension state:** player/rank/order and absence non-ranking
   are exact; observed ZERO remains distinguishable structurally, but MEASURED-zero and
   reason drift are accepted. **No, P1-1.**
2. **Confidence and W04/synthetic boundaries:** authoritative confidence/coverage equals
   the legacy DATA_CONFIDENCE projection and W04 role result evidence is suppressed, but
   the separate visible state/reasons can contradict it and W04 family claims exceed the
   authority. **No, P1-1 and P1-2.**
3. **Exact explanations:** artifact order/cardinality and exact scored query values,
   candidate values and contributions are enforced; re-signed changes fail. **Yes.**
4. **Taxonomy and contextual membership:** ID/version/digest, canonical ordering, exact
   sum and known-role membership are enforced; same-ID changed content fails. **Yes.**
5. **W04 identities:** candidate, decision and mechanical exact-four descriptor digests
   are separate and exact; unchanged W04 bytes were not modified. **Yes.**
6. **Family arrays:** canonical roles, dtypes, UUID rows, feature widths and basic PCA
   cross-array shapes are executable, but fitting-sample and legitimate PCA component
   bounds are not, and family/evidence-class compatibility is absent. **No, P1-2 and
   P1-3.**
7. **Named negative attacks:** negative zero, PCA-only topology, W04 two-column matrix,
   descriptor reorder and result re-digest substitutions fail for their intended reason.
   The additional attacks above remain accepted. **Partial; still blocking.**

## W04 descriptor digest reproduction

The helper was run directly against the unchanged parsed file
`configs/features/wyscout-v5-supported-count-features-v1.yaml`:

```text
fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e
```

This exactly equals the frozen W05 descriptor digest. The unchanged acceptance JSON also
retains candidate digest
`49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`
and decision digest
`bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`.

## Acceptance checks

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_supported_feature_authority.py` | 0 | 208 passed in 9.63s |
| `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py` | 0 | all checks passed |
| `uv run mypy src/scouting/contracts/m0.py` | 0 | no issues in 1 source file |
| `uv run lint-imports` | 2 | sandbox denied read of the shared uv cache `.git` path |
| `UV_CACHE_DIR=/tmp/w05-contracts-truth-review-03-uv-cache uv run --no-sync lint-imports` | 0 | 3 kept, 0 broken; 40 files/79 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | status PASS; failures `[]` |

Direct attacks used the strict public models and producer test fixtures. Final targets
were constructed through normal Pydantic validation; no bypassed object was accepted as
evidence.

## Scope and residual risk

The three findings are bounded W05 correctness/authority blockers under tests 1-4 and 6;
none invokes blocker test 5. No external/provider access, dependency change, destructive
action, Git operation, delegation or self-approval occurred. Cache metadata, inode/link,
temporary-path spelling and future loader implementation remain W10-only unless they
reproduce through the six tests; no such separate path was found.

Only this report and the mandatory return were written. No source, test, config,
orchestration, accepted W04, dependency/lock, data/run, phase-gate or verification byte
was changed.

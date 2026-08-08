# W05 M0 serving independent review R1

## Verdict

**REWORK.** No P0 was reproduced, but five serving P1 blocker classes are directly
reproducible. The implementation does use one loader/core/scorer path and preserves the
selected artifact bytes, but it does not yet satisfy the six W05 blocker tests because a
public boundary accepts stale carried digests, distinct canonical request bytes collide
on all result/run UUIDs, filter validation depends on order, emitted reasons/applicability
overstate the evidence, and temporal output understates admitted feature-row evidence
while inventing model/index availability.

This verdict does not reopen W05 model selection and does not classify W06/W10 quality,
calibration, expert evaluation, provider evidence, production readiness, or recruitment
outcomes.

## P1 findings and smallest bounded corrections

### P1-1 — Public serving accepts a behavior-bearing resolved-query mutation with stale pins

`M0ServingCore.serve` only checks the outer instance type and selected core/tie/claim
values before use (`src/scouting/serving/m0.py:192`). It does not reconstruct and normally
revalidate the complete `PinnedM0ServingRequest` and nested `M0ResolvedQuery`. A direct
`model_copy`/`model_construct` boundary object can therefore retain the accepted carried
`resolved_query_digest` while changing `hard_constraints`.

Fresh reproduction changed the nested query from no constraint to
`synthetic_position_code == CENTRAL` while retaining carried digest
`f31c183ec77fd530264e4a218e11581027a2afb648c60cb1f2d010d67eabe363`.
The recomputed digest was
`b9822f251dd6a4a5e8817bf72ef17a826d80a8ad2994751257e12da34274b654`,
yet the public boundary served one constrained candidate.

Smallest correction: at every public request and batch item boundary, reconstruct via
normal validation from the full Python/JSON projection, explicitly recompute and compare
the nested resolved-query digest and exclusion digest, and use only that reconstructed
object. Add direct `model_construct`, nested `model_copy`, and carried-pin attacks.

### P1-2 — Different canonical request bytes collide on result, run, and M0 UUIDs

`_identifier` hashes request ID, artifact ID, manifest digest, and resolved-query digest
only (`src/scouting/serving/m0.py:105`). A normally validated request retaining the same
request/artifact/query IDs but changing retrieval request `version` from 1 to 2 and
`requested_at` by one day produced different result bytes and a different
`result_digest`, while `retrieval_result_id`, `retrieval_run_id`, and `m0_result_id` all
remained identical.

Smallest correction: derive all three UUIDs from the complete canonical validated pinned
request bytes plus exact artifact identity and core version, with a domain separator.
Add collision tests for every request field not currently named by `_identifier`.

### P1-3 — Invalid filters can be hidden by an earlier false predicate

Constraint fields are prechecked, but supported-field operator/value validation occurs
inside the per-row evaluation loop (`src/scouting/serving/m0.py:403` and
`src/scouting/serving/m0.py:421`). With an always-false supported position constraint
before `synthetic_age_years at_least "bad"`, serving returned an empty successful result.
Reversing the same two constraints raised `M0ServingError: numeric constraint value is
invalid`. Thus filter order changes admission rather than remaining deterministic and
fail closed.

Two valid constraint orders selected the same candidate IDs but emitted different result
digests because the noncanonical input order remains in the pinned result payload. This
belongs to the same filter blocker rather than a separate W10 concern.

Smallest correction: parse, type-check, operator-check, and canonicalize every constraint
once before evaluating any row; reject the entire request on any invalid member; execute
only the validated canonical plan; and ensure semantically equivalent constraint
permutations have one canonical request/result projection.

### P1-4 — No-constraint and synthetic applicability reasons are false claims

Every candidate unconditionally receives `hard_constraints_applied`
(`src/scouting/serving/m0.py:628`) even when `hard_constraints == ()`. The accepted
synthetic-development artifact also emits confidence score 1.0 with applicability
`applicable` and no limitations (`src/scouting/serving/m0.py:550`). The contract defines
that applicability state in recommendation-display terms, so constructed synthetic
development evidence cannot truthfully emit it without an explicit limitation.

Fresh output reproduced both facts: `no_constraints_reason=true`, applicability
`applicable`, limitations `[]`.

Smallest correction: emit constraint reasons only when a nonempty validated constraint
plan actually ran; derive every reason from occurred actions/evidence; classify
constructed synthetic-development applicability as limited (or insufficient if that is
the accepted product meaning) and attach an explicit development-only/no-recommendation
limitation in both candidate confidence and `DataConfidenceEvidence`.

### P1-5 — Temporal watermarks understate feature evidence and fabricate derived availability

The selected feature rows state `observed_at=2025-01-03T00:00:00Z` and
`available_at=2025-01-04T00:00:00Z`. The emitted result instead reported snapshot
`2025-01-01T00:00:00Z`, availability watermark `2025-01-02T00:00:00Z`, and valid-from
`2025-01-02T00:00:00Z`, because `_temporal_evidence` uses only dependency times
(`src/scouting/serving/m0.py:469`). It then assigns those source dependency times to the
feature-schema, model-artifact, and retrieval-index dependencies
(`src/scouting/serving/m0.py:493`) without artifact/model/index availability evidence.

The cutoff checks themselves are strict (`>= cutoff` rejects) for both feature rows and
dependencies, but the visible temporal proof is not truthful after admission.

Smallest correction: compute snapshot, availability watermark, and valid-from over every
admitted evidence clock including feature-row observed/available times; retain exact
feature-row lineage; and obtain explicit immutable availability evidence for schema,
taxonomy, model, and index rather than copying source times. If no such authority exists,
fail closed rather than fabricate it. Add exact-cutoff and post-cutoff probes for both
row and dependency clocks.

## Six blocker-test adjudication

1. **One core/loader/scorer and byte parity — partial PASS.** Request and one-item batch
   each called `M0ServingCore.serve`, the accepted loader, and
   `LoadedM0Artifact.score` once. Their full JSON bytes matched at digest
   `6e05031833c34d6b1dbab1f23e1e7eff8e7edcfe022092b267bfd4a4b1221996`.
   Two independently constructed fresh cores emitted the same bytes. P1-2 still blocks
   identity uniqueness for different canonical request bytes.
2. **Read-only/import/artifact boundary — PASS for this R1.** The serving source has no
   direct modeling, fitting, writing, provider, source, Gold, network, clock, or
   randomness import/call and exposes no fit/write/update method. It delegates artifact
   geometry to the accepted loader/scorer. Missing/extra/symlink/root and re-signed
   artifact authority attacks remain fail closed through the exact registered root and
   accepted loader. No fallback authority was found.
3. **Exact pins, signals, exclusions, role restrictions, and filters — REWORK.** Loader
   pins and ordinary query/exemplar/exclusion/role paths hold, but P1-1 and P1-3 break
   public request integrity and order-independent fail-closed filtering.
4. **Six states, confidence, explanations, and claim boundary — REWORK.** Six dimensions
   are in enum order; absent impact/trajectory/transfer-risk dimensions use zero
   sentinels and nonranking unavailable states; data confidence is separate/nonranking;
   explanations exactly project scorer contributions in artifact feature order; and
   `resemblance_only` is retained. P1-4 makes applicability and reasons untruthful.
5. **Temporal and exact lineage — REWORK.** Every candidate binds the same emitted result
   lineage and dependency cutoff checks are strict, but P1-5 understates admitted
   feature-row clocks, omits an explicit taxonomy dependency, and fabricates derived
   availability times.
6. **Determinism, collisions, mutation, and forbidden claims — REWORK.** Same-request
   replay and fresh-core bytes are stable and artifact hashes remain unchanged, but
   P1-1/P1-2 permit stale behavior pins and UUID collisions. No blended percentage,
   outcome probability, value, transfer-success, W06, provider, expert, or production
   claim was found; the synthetic recommendation applicability in P1-4 is the reproduced
   claim blocker.

## Artifact immutability and identities

The same four physical hashes were observed before and after every review probe:

- arrays: `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`;
- manifest: `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`;
- configuration: `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`;
- candidate universe: `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

Shared core is `m0-shared-core-v1`; selected artifact is
`9a0d43c6-d177-51be-8280-3bf02bedbc99`; manifest digest is
`2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`;
model/index identities are `w05-m0-role_aware_restriction-v1@v1` and
`w05-m0-role_aware_restriction-index-v1@v1`; configuration digest is
`5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`;
candidate-universe digest is
`2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`;
lineage pin is
`e77de98a171447b8a3361161e5efbc8173909f933435f27ac99e0534c6d591c7`.

## Checks

- Focused integration/e2e/unit/contract suite: exit 0, `42 passed in 1.00s`.
- Ruff check on bounded serving/tests: exit 0.
- Mypy on `src/scouting/serving/m0.py`: exit 0.
- Import-linter: exit 0, three contracts kept.
- Local-only verifier: exit 0, PASS with no failures.
- Fresh adversarial runtime probe: exit 0 and reproduced all five P1 classes above.
- Fresh in-memory re-signed manifest/request-pin matrix: exit 0; independently rejected
  all 17 behavior-bearing manifest identity substitutions and all 18 corresponding
  request-pin substitutions (including manifest digest), without touching artifact files.

## P2 and W10 boundary

No independent P2 is required to explain this verdict. Existing list-collection and
redundant query/exclusion-overlap representations remain the accepted model-review P2
boundary. Retrieval quality, calibration, robustness, expert/provider validation,
production applicability, and recruitment outcomes remain W06/W10 work and were not
used to fail this serving review.

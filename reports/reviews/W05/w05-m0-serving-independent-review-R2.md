# W05 M0 serving independent review R2

## Verdict

**PASS.** No W05 serving P0 or P1 reproduced. R2 closes all five R1 P1 classes while
retaining the exact accepted artifact, selected role-aware model, scorer geometry,
request/batch parity, six-state evidence card, explanation projection, and
`resemblance_only` claim boundary.

The only fresh residual is P2 preflight ordering: some normally typed but semantically
invalid filter/query requests read the exact already-authorized registered local artifact
before rejection. They never call the scorer, admit no data or authority, emit no result,
ranking, evidence, explanation, confidence, or claim, and alter no bytes. It does not
satisfy any of the six blocker tests and is not W06/W10 work.

## R1 P1 closure

### 1. Complete public-boundary revalidation — closed

Fresh `model_copy` and `model_construct` attacks retained carried digests while changing
query player, exemplars, responsibilities, responsibility weights, constraints, limit,
cutoff, exclusions, taxonomy, every artifact/configuration/fitting/candidate/lineage/
model/index pin, expected query digest, exclusion digest, shared-core version, tie policy,
and claim boundary. All 34 cases rejected through both public single and batch APIs.
Loader and scorer spies both remained at zero for these stale behavior/pin attacks.

Ordinary typed input was accepted; mapping input was explicitly rejected. The accepted
typed baseline emitted digest
`9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`.

### 2. Domain-separated complete-request UUIDs — closed

Twelve normally validated requests held the selected request/artifact authority constant
while independently changing version, requested time, trace, tenant, role-brief ID and
version, query player, exemplar mode, responsibilities, constraints, limit, and
exclusions. Their canonical pinned-request bytes were all distinct, and each of the three
UUID domains was independently collision-free.

The baseline identities are:

- `m0_result_id`: `e77948a1-2987-514d-a585-cd54015e2152`;
- `retrieval_result_id`: `8a0c3594-0b40-572a-8a9a-aecaa0b6052e`;
- `retrieval_run_id`: `332c42c4-6b0d-5fd5-b8aa-f09ae9ae501c`.

Repeated single, one-item batch, and independently constructed fresh-core calls returned
byte-identical complete JSON and the same result digest.

### 3. Complete constraint-plan validation and semantic parity — closed

Every admitted operator was exercised: position `equals`, `not_equals`, and `in`; age and
elapsed-minutes `equals`, `not_equals`, `at_least`, and `at_most`. Unknown field,
unsupported position/numeric operator, malformed numeric, non-finite numeric, and malformed
position-IN value were each placed before and after an always-false valid predicate. All
12 permutations rejected; none reached the scorer.

Equivalent valid filter permutations returned identical candidate identities/order,
distances, contributions, dimension states, and explanations. Their request-bound UUIDs
and result digests remained distinct because the accepted resolved-query digest is
truthfully order-sensitive. This is the required distinction between semantic execution
parity and request identity; no contract digest change was made or required.

### 4. Truthful reasons and synthetic limitations — closed

No-constraint output contains no `hard_constraints_applied` reason. Every candidate and
the separate confidence projection report applicability `limited` with exact ordered
limitations `synthetic_development_only` and `no_recommendation_evidence`. The legacy
DATA_CONFIDENCE and state projections exactly combine coverage reasons, these limitations,
and `applicability_limited`.

Every emitted reason belongs to the closed serving enum and canonical ordering. The full
wire contains no blended/match percentage, overall score, success/outcome probability,
transfer value, positive recommendation, provider, expert, W06, or production claim.
The required negative `no_recommendation_evidence` limitation is not a recommendation.

### 5. Truthful explicit temporal lineage — closed

Feature-row and raw-source `observed_at` and `available_at` were independently moved to
the cutoff and one second after it. All eight public-API attacks rejected before scoring.

The accepted lineage contains exactly 18 `SOURCE_MANIFEST` plus 18 per-row
`FEATURE_SCHEMA` dependencies and no fabricated `MODEL_ARTIFACT`, `RETRIEVAL_INDEX`, or
identity availability. Every feature dependency uses the manifest feature-schema digest,
exact row clocks, and deterministic UUID over player ID plus row-lineage digest. The
recomputed lineage hash equals the result and candidate lineage hash:
`c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491`.

Visible times equal the maxima over all explicit admitted clocks:

- snapshot: `2025-01-03T00:00:00Z`;
- availability watermark: `2025-01-04T00:00:00Z`;
- valid-from: `2025-01-04T00:00:00Z`;
- generated-at: request time `2026-08-02T00:00:00Z`.

## Six blocker-test adjudication

1. **One core, loader, scorer, and parity — PASS.** Accepted single and batch items use
   the same `M0ServingCore`, accepted `load_m0_artifact`, and
   `LoadedM0Artifact.score`. Same-request/fresh-core bytes are exact. No copied scaling,
   PCA, cosine, Euclidean, or contribution implementation exists in serving.
2. **Read-only artifact/import boundary — PASS.** Serving directly imports only contracts
   and the accepted M0 runtime. Its only public core method is `serve`; fit, train, write,
   update, and save are absent. Missing, extra, wrong-file, and symlink roots reject. No
   provider, Gold, network, randomness, or wall-clock path was found.
3. **Pins, signals, exclusions, roles, and filters — PASS.** All 17 independently
   re-signed behavior-bearing manifest substitutions and all expected request-pin
   substitutions reject. Query-player, sorted-exemplar mean, exclusion, absent/both,
   unknown/excluded signal, responsibility, role threshold, and complete filter paths
   are deterministic and fail closed.
4. **Six dimensions, confidence, explanations, and claims — PASS.** Dimensions are in
   canonical enum order. Impact, trajectory, and transfer risk use zero sentinels with
   unavailable nonranking states. Confidence is separate/nonranking. Explanations equal
   scorer values and contributions in exact artifact feature order.
5. **Temporal and exact lineage — PASS.** Strict cutoff rejection, exact source/row
   clocks, lineage hash, candidate binding, and no fabricated derived timestamps all
   reproduce.
6. **Determinism, collision resistance, mutation resistance, and frozen geometry — PASS.**
   Distinct admitted canonical request bytes have distinct UUIDs; stale constructed
   requests fail before artifact access; same requests replay exactly; selected ranking
   geometry and artifact bytes remain frozen.

## Frozen model and artifact evidence

Serving output exactly matched direct `LoadedM0Artifact.score` for the baseline:

| rank | player | distance |
|---:|---|---:|
| 1 | `20000000-0000-4000-8000-000000000002` | `0.00013857118024163118` |
| 2 | `20000000-0000-4000-8000-000000000003` | `0.000554708060777731` |
| 3 | `20000000-0000-4000-8000-000000000004` | `0.0012485263821517822` |

Shared core remains `m0-shared-core-v1`; selected artifact ID is
`9a0d43c6-d177-51be-8280-3bf02bedbc99`; manifest digest is
`2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`;
model/index are `w05-m0-role_aware_restriction-v1@v1` and
`w05-m0-role_aware_restriction-index-v1@v1`; configuration digest is
`5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`;
taxonomy digest is
`59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`.

The same physical hashes were observed before and after every probe:

- arrays: `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`;
- manifest: `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`;
- configuration: `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`;
- candidate universe: `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Checks

- Focused integration/e2e/unit/contract suite: exit 0, `44 passed in 1.09s`.
- Ruff check on the bounded serving/tests: exit 0.
- Mypy on `src/scouting/serving/m0.py`: exit 0.
- Import-linter: exit 0, three contracts kept.
- Local-only verifier: exit 0, PASS with no failures.
- All independent inline public-API attack matrices: exit 0 after the corrected temporal
  probe; every asserted closure above reproduced.

## P2 and W06/W10 boundary

The read-only authorized-artifact load before rejection of some semantically invalid typed
filter/query requests is P2 preflight efficiency/error-order hardening only. The scorer is
never called and no user-visible result exists. It needs no correction for this PASS.
Retrieval quality, robustness, calibration, protected/expert/provider evaluation,
production applicability, and recruitment outcomes remain W06/W10 work and were not used
to pass or fail this serving review.

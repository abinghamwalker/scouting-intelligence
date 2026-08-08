# W05 architecture preflight R1

- Task: `W05-ARCH-REVIEW-00`
- Date: `2026-08-03`
- Reviewer role: independent verifier, report only
- Verdict: **REWORK BEFORE W05 IMPLEMENTATION FAN-OUT**
- Severity summary: **P0: 0; P1: 4; P2: 0**

The proposed additive-contract direction is sound, but the dispatched contract packet does
not yet make four high-impact substitution classes fail closed. The smallest correction is
to tighten the unaccepted W05 contract and its adversarial tests before feature, taxonomy,
artifact, serving, or parity packets consume it. No accepted W03/W04 contract or evidence
byte needs to change.

## Controlling evidence and review boundary

1. `orchestration/task_packets/W05-CONTRACTS-01-R1.yaml:65-89` requires additive
   contracts, five-valued feature state, artifact and request identities, a separate
   confidence object, stable result identity, and adversarial tests. It does not define
   the canonical byte and authority rules identified below.
2. `src/scouting/contracts/evidence.py:189-289` already supplies typed dependency kinds,
   closed dependency lineage, and strict-before-cutoff `TemporalEvidence`.
   `src/scouting/contracts/retrieval.py:82-169` supplies the accepted six-dimension,
   resemblance-only request/result boundary and checks lineage equality. These accepted
   models must remain byte/behaviour compatible.
3. `src/scouting/contracts/workflow.py:63-101` binds a role brief to a taxonomy version,
   responsibilities, preferences, exemplars, version, tenant, and lifecycle state.
4. `docs/dataset-cards/w04-wyscout-transformed-v1.md:91-102` authorises exactly four
   real Gold counts: `action_count`, `coordinate_known_action_count`, `match_count`, and
   `resolved_possession_action_count`; rates, minutes, per-90, fifth/inferred features,
   role-fit, value, and similar expansions are unavailable or suppressed.
5. `../scouting-ml-agent-implementation-workflow.html:990-998` orders W05 as registry,
   taxonomy, M0 artifact, shared serving core, then parity audit, and limits the gate to
   synthetic/frozen development improvement with **no validation claim**.
   Lines 1008-1014 reserve expert sets, protected comparison, transfer/null evidence, and
   the claim gate for W06.
6. `../scouting-ml-production-blueprint.html:1947-2051` requires a multi-view result plus
   separate confidence, M0 controls, and artifact feature/split/runtime/fallback evidence;
   lines 2447-2456 require deterministic retrieval, explanations, confidence, reason codes,
   precomputed index, baseline comparison, and disclosed failure cases.
7. `reports/phase-gates/W04/acceptance-report.md:25-28` and
   `reports/verification/W04/w10-deferred-runtime-host-state-hardening-backlog-R1.md:40-43`
   explicitly defer host-specific cache, inode/link, timestamp, temporary-path, and
   equivalent metadata concerns unless a reproducible controlling P0/P1 path exists.

## The six controlling W05 blocker tests

Each finding below is classified against the user-defined tests:

1. changes admitted features, fitted artifacts, rankings, or result bytes;
2. causes temporal leakage or lineage substitution;
3. breaks training-serving or batch-request parity;
4. produces a false explanation, confidence statement, or claim boundary;
5. admits unauthorised code/data or violates local-only controls; or
6. demonstrates a reproducible P0/P1 correctness or security defect.

## Findings

### P1-1 — Real W04 feature authority and broader synthetic-development inputs are not cryptographically distinct

**Blocker tests:** 1, 2, 4, 5, and 6.

**Evidence.** The W05 contract packet asks an artifact to bind feature names/order/hash
and fitting-population identity/count, but it does not require the accepted feature
registry ID and canonical decision digest, the evidence class (`w04_real_governed` versus
`synthetic_development`), or the exact four-feature real roster. W04 expressly authorises
only four counts and suppresses minutes/rates/per-90. A generic schema hash can faithfully
identify a broader schema without proving that the broader schema is authorised for real
W04 data. A fitting-population identifier likewise does not state whether its rows are
real, synthetic, or mixed.

**Reproducible adversarial substitution.** Build two internally consistent manifests:
one using the four accepted counts and one adding `actions_per_90`; give each its own
valid schema hash and array digest. Both satisfy the packet as written. A serving request
pinning the second manifest will fail no current stated invariant even though the second
feature is suppressed for the real W04 boundary. The same ambiguity permits a mixed
real/synthetic fit to be labelled only by an opaque population ID.

**Smallest required correction.** Before downstream work, require:

- `feature_registry_id` and its canonical SHA-256 decision digest;
- an enum evidence class that distinguishes `W04_REAL_GOVERNED` from
  `SYNTHETIC_DEVELOPMENT` (not a W06 partition enum);
- a canonical feature descriptor digest covering name, order, type, semantic state,
  denominator, imputation rule, reason code, and source authority;
- for `W04_REAL_GOVERNED`, an invariant requiring exactly the four accepted names in
  registry order and rejecting every minutes/rate/per-90/fifth feature;
- a fitting-population manifest digest that binds evidence class, ordered row/player
  identities, count, cutoff, source manifests, feature registry digest, and dependency
  lineage; mixed evidence classes fail closed.

Broader M0 inputs may be used only in explicitly labelled synthetic-development
artifacts and reports. They must never be presented as W04-derived evidence or as W06
evaluation evidence.

### P1-2 — The artifact identity does not fully determine safe array interpretation or PCA orientation

**Blocker tests:** 1, 3, 5, and 6.

**Evidence.** The packet requires one array-payload digest, a serialization-format field,
a seed, and a configuration digest, but it does not require an allowlisted non-executable
format, per-array descriptors, or a canonical PCA sign/order convention. A byte digest
proves which bytes were loaded; it does not prove that the loader interprets the bytes as
the same named arrays, dtype, shape, byte order, or row/column orientation. A free-form
format can also name an executable pickle/joblib-like payload. PCA component signs are
mathematically ambiguous, and equal/near-equal components need an explicit deterministic
ordering rule; a seed alone does not make those bytes canonical.

**Reproducible adversarial substitutions.** Keep payload bytes fixed while swapping two
array names or shapes in loader-side metadata; or fit an equivalent PCA basis with one
component sign flipped. Distances may remain mathematically equivalent while artifact,
explanation, and digest bytes differ. Alternatively, label an executable pickle payload
with a syntactically valid format string. None is explicitly rejected by the packet.

**Smallest required correction.** Define a closed serialization enum and permit only a
non-executable numeric representation loaded with object/pickle loading disabled. Bind a
canonical ordered tuple of per-array descriptors (`name`, semantic role, dtype, shape,
endianness, memory order, byte length, SHA-256) plus a canonical bundle digest. Reject
object dtype, unknown arrays, duplicate names, extra archive members, non-finite values,
shape mismatches, trailing bytes, and path-bearing members.

For PCA, pin solver/version-neutral algorithm configuration and canonicalise every
component: choose the lowest feature index among maximum-absolute loadings as pivot and
force its loading non-negative; order components by decreasing explained variance with a
declared canonical component-byte tie break. Persist and test oriented components, centre,
scale, explained values, feature order, and transformed-array digest. Serialize/reload
must reproduce exact bytes and explanations.

### P1-3 — Candidate-universe, query, tie, and canonical result-byte identities are incomplete

**Blocker tests:** 1, 2, 3, 4, and 6.

**Evidence.** The packet pins artifact/schema/taxonomy/configuration/fitting-population/
lineage and asks for model/index identities, but it does not explicitly bind the ordered
candidate universe and row-to-player mapping, resolved role-brief/query bytes, exclusion
set, score/tie policy, or the result-digest preimage. Existing `RetrievalResult` checks
unique ascending ranks, but not contiguous ranks, deterministic tie resolution, request
limit conformance, or the canonical digest formula. `RetrievalRequest` pins brief ID and
version, not a W05-resolved brief/query digest. These omissions allow the same valid model
bytes to yield different rankings or result bytes across batch and request paths.

**Reproducible adversarial substitutions.** Keep index vectors and their payload digest
fixed but swap the external row-to-player mapping; add or remove a candidate without
changing fitting population; permute tied input rows; change canonical JSON field/default
handling when calculating the result digest; or resolve the same brief version through a
different taxonomy/query projection. Each can change player/rank/result bytes without an
explicit stated mismatch.

**Smallest required correction.** Add and pin:

- an ordered candidate-universe/row-mapping manifest digest, count, and eligibility
  cutoff/lineage, separate from fitting population;
- the exact resolved role-brief digest (including version, taxonomy, responsibilities,
  weights, exemplars, hard constraints), ordered exclusion digest, request limit, tenant,
  and cutoff;
- batch ID and request ID as separate execution identities over the same canonical query
  digest, plus a shared core/version identity;
- score semantics and canonical numeric encoding; reject NaN/infinity and normalise
  negative zero;
- a total order: primary distance/score, declared secondary keys, then canonical player
  UUID bytes; ranks must be contiguous `1..n`, unique, limit-bounded, and exclude all
  requested players;
- a versioned result-digest algorithm over canonical JSON bytes with the digest field
  excluded and defaults included; bind ordered candidates, exact score/explanation inputs,
  all resolved identities, temporal evidence, confidence evidence, and reason codes.

Parity evidence must compare fit-time transform, reload transform, batch retrieval, and
single-request retrieval at array, score, ordered-candidate, explanation, and final result
byte levels. A matching top-k set alone is insufficient.

### P1-4 — The accepted six-dimension payload and new separate confidence object can disagree or overstate unsupported M0 evidence

**Blocker tests:** 1, 4, and 6.

**Evidence.** `RetrievalCandidate` requires six scored dimensions, including
`data_confidence`, while the blueprint and W05 packet additionally require a separate
data-confidence object. The packet does not say which is authoritative or require exact
projection equality. The accepted dimensions also require numeric scores for impact,
trajectory, and transfer risk even though W04 has only four counts and explicitly lacks
role-fit/value/current-form evidence. The M0 result wrapper therefore needs additive
invariants to prevent arbitrary placeholder numbers or contradictory confidence from
being represented as evidence.

**Reproducible adversarial substitution.** Set the accepted `data_confidence` dimension
to `0.95` and the separate confidence object to `0.20`, each with plausible unique reason
codes; or populate impact/trajectory/transfer-risk scores from constants despite missing
evidence. Both satisfy the existing models and the packet states no cross-object truth
rule.

**Smallest required correction.** Make the new typed confidence object authoritative and
require the legacy data-confidence dimension to be a deterministic, exact projection of
it (score, applicability, coverage and ordered reason/limitation codes). Define a closed
M0 evidence-state/reason-code mapping for every other dimension. Unsupported dimensions
must be explicitly `UNAVAILABLE`/`SUPPRESSED`, must name the accepted reason, and must not
contribute to ordering. If compatibility forces a numeric legacy field, require a fixed
documented sentinel projection that is never described as measured evidence and is
covered by claim-boundary tests. Explanations must be deterministic functions of the
exact admitted feature values, weights, contrasts, states, and confidence evidence bound
into the result digest; no free-text or arbitrary reason-code substitution is accepted.

## Answers to the review questions

### 1. Does the additive approach preserve W03/W04 bytes and pin every serving identity?

It can preserve all accepted bytes because a new `m0.py` wrapper and new exports need not
modify `TemporalEvidence`, `RetrievalRequest`, `RetrievalResult`, `RoleBrief`, or any W04
authority file. As dispatched, however, it does **not** pin every necessary identity.
The four P1 corrections are required: source/registry evidence class; numeric payload
layout/PCA identity; candidate/query/tie/result-byte identity; and one authoritative
confidence/explanation truth.

Byte preservation must be demonstrated by frozen JSON byte fixtures for accepted W03/W04
models before and after the additive export, not merely by object equality. New wrapper
parsing must reject an old payload unless it is explicitly wrapped; accepted old model
serialization must remain unchanged.

### 2. Exact serial dependency order

The required acceptance order is:

1. **Additive W05 contracts** — corrected, adversarially tested, independently reviewed,
   and accepted without changing prior bytes.
2. **Feature registry/state** — freeze the W04-real exact-four authority and a separate
   synthetic-development authority; publish canonical descriptors and digests.
3. **Role taxonomy** — freeze responsibilities, deterministic mappings, ordered
   contextual probabilities, canonical digest, and no permanent labels; it consumes the
   accepted feature/evidence-state vocabulary.
4. **M0 model/index artifact** — fit only against accepted registry/taxonomy identities;
   produce safe canonical arrays, PCA orientation, fitting and candidate rosters, index,
   lineage, and development-check evidence.
5. **Serving core** — read-only load of the accepted artifact; no provider adapters,
   fitting, registry mutation, or alternate math; enforce pinned query, cutoff, roster,
   ties, explanations, confidence, and result digest.
6. **Parity evidence** — independently compare fit/reload/batch/request bytes and all
   failure substitutions, then run the complete W05 gate.

No downstream step may begin against a merely dispatched predecessor because each step
consumes immutable digests emitted by the prior step. Feature registry and taxonomy may
be designed in parallel only before final acceptance; their authoritative digests and
consumer packets remain serial in the order above.

### 3. Adversarial substitutions requiring explicit rejection

- feature-registry/evidence-class swap; real/synthetic mix; supported/suppressed state or
  denominator/reason change; feature order/type/imputation drift;
- fitting-population row/order/cutoff/source/lineage substitution;
- array name/shape/dtype/endianness/orientation swap; extra member; object/pickle payload;
- PCA sign flip or equal-component reorder; scaler centre/scale or weight reorder;
- taxonomy responsibility/order/mapping/probability/context substitution;
- candidate-universe or row-to-player mapping substitution; index/model alias drift;
- brief/query/exemplar/exclusion/tenant/cutoff substitution;
- equal-score input permutation, negative zero/non-finite score, rank gaps, excess limit;
- explanation input/reason/contrast drift; confidence projection disagreement;
- canonical JSON/default/order/digest-algorithm drift; batch/request core-version drift;
- provider read, fitting, mutation, external access, or fallback to a different artifact
  from the serving path.

### 4. W04 real-data boundary versus broader M0 inputs

The real boundary remains exactly the four result-independent counts named in P1-1.
Minutes, rates, per-90, inferred roles, action value, outcomes, and fifth features remain
suppressed or unavailable. Broader M0 features are permitted only in deterministic
synthetic-development fixtures with an explicit evidence-class and manifest digest.
They cannot support a real-data, expert-relevance, protected-test, transfer, reliability,
or validation claim.

### 5. Minimum W05 development improvement check

Use a frozen, manifest-digested **synthetic-development** fixture designed before model
comparison. It must contain at least two queries, deterministic intended-neighbour pairs,
deliberate metadata confounders, raw-scale domination cases, exact ties, missing/
suppressed states, and a fixed candidate roster. Preregister:

- metadata control and raw Euclidean control configurations/digests;
- candidate M0 configuration/digest;
- exact pairwise ordering expectations and `NDCG@k`/top-k overlap computation over only
  synthetic intended relations;
- a minimum deterministic margin (for example, candidate satisfies every declared
  intended-pair ordering and has strictly greater aggregate synthetic NDCG than both
  controls), exact repeat-run digests, and failure-case disclosure.

Call the result **development-fixture discrimination**, not relevance, reliability,
validation, expert judgement, or promotion. Do not use W06 partition names, labels,
protected data, bootstrap claims, or minimum useful product effects. A failure is a W05
`NO-GO/REWORK`, not evidence about real scouting quality.

### 6. Testability of serialization, PCA, ties, parity, and serving isolation

All are testable after P1-2/P1-3 are corrected. Tests must construct and reject unsafe
format/object arrays, malformed descriptors, PCA sign/order substitutions, row-map and
tie permutations, query/lineage mismatches, and provider/fitting import or call attempts.
Run the same frozen input through fit-time transformation, fresh-process safe reload,
batch, and request paths and assert exact array/score/explanation/result bytes. Enforce
module boundaries (`serving` cannot import `modeling` training or `sources`) and inject
spies that fail if provider reads, fitting, writes, or external access are attempted.

### 7. W10-only host-state concerns

Foreign-interpreter `.pyc` tags, incidental cache rows, inode/link counts,
empty-directory metadata, timestamps, temporary-path spelling, and equivalent
non-authoritative host variation remain **W10-only**. None is a W05 finding by itself.
It becomes W05-blocking only with a reproducible path satisfying one of the six tests—for
example, a cache file admitted as executable code (test 5/6), host metadata entering
artifact/result bytes (test 1/3), or a temporary path entering lineage (test 2). This
review found no such host-state path and raises no W10 concern as a W05 blocker.

## Concrete W05 acceptance matrix

| Surface | Minimum accepted evidence | Required negative/adversarial proof | Blocking tests |
| --- | --- | --- | --- |
| Additive compatibility | Frozen old contract JSON bytes and public behaviour unchanged; strict new wrapper round-trip | unknown field, invalid digest/enum/state, direct legacy mutation | 1, 6 |
| Real/synthetic feature authority | registry ID/digest, exact descriptors, evidence class, fitting manifest | fifth feature, per-90/rate/minutes, mixed real/synthetic, state/reason/type/order swap | 1, 2, 4, 5, 6 |
| Feature state | distinct VALUE/ZERO/MISSING/SUPPRESSED/UNAVAILABLE; finite VALUE, numeric zero only for ZERO | NaN/inf, `-0`, value on unavailable state, absent reason, unrecognised imputation | 1, 4, 6 |
| Taxonomy | version/canonical digest; unique ordered responsibilities; contextual probabilities finite in `[0,1]` with deterministic sum 1 | permanent label, duplicate/reordered responsibility, context swap, tolerance-dependent sum | 1, 4, 6 |
| Safe artifact | closed safe format; per-array descriptors/digests; canonical bundle; seed/config; fit and candidate rosters; model/index IDs | pickle/object, extra member, shape/dtype/name/order change, truncation/trailing bytes | 1, 3, 5, 6 |
| PCA/scaler/weights | canonical component orientation/order and exact transform bytes after reload | sign flip, tied-component reorder, centre/scale/weight order substitution | 1, 3, 4, 6 |
| Temporal lineage | request, feature, fit, candidate and result cutoffs/manifests/lineage agree with strict `TemporalEvidence` | post-cutoff fact, lineage or source-manifest swap, mixed cutoff, generated-time substitution | 2, 4, 6 |
| Query/index/ranking | resolved brief/query digest, row map, candidate roster, total tie order, contiguous/limited ranks | row-map swap, roster add/drop, tied input permutation, excluded candidate, alias fallback | 1, 2, 3, 6 |
| Explanation/confidence | authoritative confidence object; exact legacy projection; deterministic cited contrasts/states/reasons; resemblance-only | confidence disagreement, arbitrary unavailable scores, reason/input substitution, blended/outcome claim | 1, 4, 6 |
| Batch/request parity | same loader/core/query; exact arrays, scores, order, explanations and canonical result bytes | alternate transform/math, stale index, differing defaults, batch-only/request-only filter | 1, 3, 4, 6 |
| Serving isolation | read-only accepted artifact load; no provider, fitting, mutation, network/external service | import/call spies and local-only verifier reject source/training/provider/external paths | 3, 5, 6 |
| Development improvement | frozen synthetic fixture beats metadata and raw distance under preregistered deterministic rule; exact repeat digest; failures disclosed | controls changed after result, protected/expert labels, W06 claim language | 1, 4, 6 |
| W10 separation | no host metadata in authority, lineage, artifact or result preimages | only escalate a reproduced executable/product/lineage/parity/claim/security path | 1-6 only when reproduced |

## Risks and follow-ups

- Residual risk after correction: W05 development evidence remains synthetic and cannot
  establish expert relevance, time/league/source transfer, calibration, or product utility.
- Follow-up 1: revise `W05-CONTRACTS-01` within its existing additive paths and obtain a
  fresh independent review before dispatching registry/taxonomy work.
- Follow-up 2: issue serial packets in the dependency order above with the acceptance
  matrix rows copied into their checks.
- Follow-up 3: reserve all W06 expert/protected/null/interval/transfer evidence and claim
  decisions for W06; record W05 negative development results rather than tuning the gate.
- Follow-up 4: keep the W10 host-state backlog unchanged; no W05 expansion is warranted.

## Scope confirmation

- Report-only review; no implementation, source, tests, configuration, orchestration,
  dependency, data/run, phase-gate, verification, or Git state changed.
- No provider/network/external service was accessed.
- No Git command was run; no self-approval or delegation occurred.
- The only paths written are the two exact paths allowed by the task packet.

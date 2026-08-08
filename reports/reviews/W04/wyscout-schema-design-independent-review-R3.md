# W04 Wyscout schema design independent review R3

## Decision

**REWORK**

R4 is substantially more exact than R3, but it is not yet safe to decompose into the
claimed ownership-complete implementation graph. Four P1 defects remain:

1. the identity bundle is temporally backdated to source release even though its
   digest includes later project decision, review, and acceptance evidence;
2. the controlling W04.3 canonical-identity lifecycle is no longer fully specified
   or owned;
3. required source-manifest output, data-health, transformed dataset-card, and W04
   phase-gate evidence have no exact packet owner; and
4. the code manifest is non-circular for repository Python, but it does not
   content-address all behavior-affecting third-party and local resource bytes that
   the actual rebuild can execute or consume.

No P0 defect was found. No separate P2 defect is reported: each remaining issue can
make temporal admission, identity correction, phase completion, or build identity
materially false, so each is ranked P1 rather than minimized as a documentation-only
issue.

This review does not reject the source seam, exact event clock representation, local
project possession decision route, strict 18-row manifest, strict source coverage,
neutral Gold grain, minute suppression, Gold coverage equations, or the
result-independent player-match schema. It rejects the claims that all six R3
corrections are closed and that every required implementation/phase artifact has an
owner.

## Scope and authorities read

The complete R3 review packet and every `read_first` document were read before this
report was written. The review also read the controlling W04/P2 passages of the
approved implementation workflow and production blueprint because `AGENTS.md` makes
them authoritative and the master explicitly challenged W04.3, data health, the
dataset card, and phase-gate ownership.

The relevant controlling requirements are:

- W04.3 / P2.3 requires canonical players, teams, competitions, and matches with
  confidence, a human/manual review queue, versioned corrections, and crosswalk
  tests;
- W04.6 / P2.8 requires data-health evidence including coverage, freshness, identity
  backlog, reconciliation, rejected fields, and temporal violations;
- W04.7 / P2.9 requires an independent raw-to-Gold rebuild and review/publication of
  the dataset card; and
- G-W04 requires deterministic manifested raw-to-Gold output, identity/reconciliation
  thresholds, zero post-cutoff admission, and guarded local roots.

No provider, network, container, remote, or external service was used. No source,
code, test, configuration, data, dependency, migration, orchestration, or Git path
was changed.

## Ranked findings

### P1-01 — the reviewed identity bundle is backdated to source availability

R4 Section 6.2 assigns both `observed_at` and `available_at` of the “reviewed identity
bundle” to `2020-01-28T14:24:27Z`, the upstream source release. Section 6.2 then says
the bundle digest covers:

- the identity ruleset;
- a decision actor and decision time;
- independent review; and
- an acceptance record.

Those project artifacts necessarily exist later than the source release. Their
content cannot be knowable in 2020 merely because the underlying provider IDs were
available then. The claim that “no later human identity assertion is being backdated”
does not cure the contradiction: the dependency is the digest of the reviewed,
accepted project bundle, not merely the provider IDs.

The distinction is important:

- the source fact “provider entity ID X exists in this frozen delivery” can truthfully
  be available at source release;
- a deterministic UUID formula may have a source-valid interval beginning at source
  release; but
- the accepted project assertion that formula/version maps X to canonical UUID Y,
  together with its decision, review, and acceptance digests, is not available before
  that authority route completes.

The current clock makes a historical `feature_cutoff_ts` before the actual identity
decision appear eligible for an identity ruleset that did not yet exist. That violates
the evaluation contract’s distinction between occurrence/valid time and knowable
time, and it invalidates the maximum dependency watermark in both
`W04SemanticTemporalProof` and the adapted `TemporalEvidence`.

Required correction:

1. Give the identity ruleset an exact decision, independent-review, and master
   acceptance route with truthful clocks.
2. Either set the identity-bundle `observed_at` to its decision time and
   `available_at` to its acceptance time, or split source identity facts from a
   separate `feature_schema` identity-ruleset dependency whose availability is the
   acceptance time.
3. For each `IdentityEvidence`, distinguish `valid_from` from `available_at`: a
   mapping may describe a source-valid interval beginning in 2020 while remaining a
   late-known project assertion available only at acceptance.
4. Require identity corrections and reviews to use their own later availability and
   make the lineage watermark advance.
5. Test that a cutoff equal to or before identity acceptance rejects the bundle even
   though all provider records were released in 2020.

Until corrected, `W04-DESIGN-SEMANTIC-TEMPORAL-BOUNDARY-01` is not closed.

### P1-02 — W04.3 canonical identity is not a standalone implementable lifecycle

R4 retains a deterministic UUIDv5 formula, confidence `1.0` for deterministic
assignments, zero-player separation, and fail-closed unresolved references. Those are
sound primitives, but the standalone design has regressed from the controlling W04.3
requirements and from the more explicit R2 crosswalk.

The identity bundle is required by the temporal proof and `build_id`, but R4 does not
define:

- the bundle’s complete canonical schema;
- the relationship between `identity_bundle_id` in `build_id` and the separately
  named `identity_bundle_dependency_id`;
- the bundle’s generated artifact path;
- the exact `IdentityEvidence.evidence_digest` formula;
- the initial evidence `version` and trace/tenant population rules;
- the crosswalk state enum and confidence threshold;
- a durable unresolved/manual-review queue schema and artifact path;
- queue deduplication, disposition, and downstream blocking rules;
- a reviewed correction schema with reviewer, reason, valid interval, new version,
  and `supersedes_evidence_digest`;
- correction/bundle regeneration ownership and independent review; or
- one exact owner for the decision, review, acceptance, queue, correction, and
  immutable bundle artifacts.

The text says that the bundle digest includes decision actor/time, independent
review, and acceptance, but the implementation graph contains no identity decision,
identity review, or identity acceptance packet. Row 10 owns only
`src/scouting/identity/wyscout.py`, one test file, and a return. It is called the sole
identity-bundle writer without being authorized to write any bundle data path.

Likewise, “a future reviewed or corrected identity must carry its own later truthful
availability” is a stop rule, not an implementable versioned correction design.
Missing and conflicting references are known to exist in the measured evidence
(including absent master references from bench and substitution evidence), yet no
review-queue product is owned.

Confidence also needs an exact decision boundary. If W04 deliberately supports only
structurally unique deterministic mapping, state that the resolution threshold is
exactly `confidence == 1.0`, every non-qualifying reference enters `review_required`,
and no intermediate confidence is permitted. If reviewed mappings are allowed, give
their evidence and threshold an accountable versioned contract. A blanket `1.0`
without the crosswalk state/threshold contract does not satisfy “identities with
confidence.”

Required correction:

1. Restore a complete strict crosswalk contract for competition, team, player, and
   match identity with ID, tenant, kind, source identity/version, canonical ID,
   version, method, confidence, state, evidence digest, valid/availability interval,
   reviewer, supersession, and sorted reason codes.
2. Define exact initial-version and deterministic-confidence rules and the
   resolve/review/reject/supersede state machine.
3. Define a content-addressed identity bundle schema, ID derivation, path, digest,
   ordering, clocks, and relationship to the dependency ID and `build_id`.
4. Define a durable review-queue artifact with exact owner, path, immutable item IDs,
   evidence links, state transitions, and fail-closed Gold behavior.
5. Define reviewed correction artifacts that append a new version and supersession
   link without mutating version 1.
6. Add separate master decision/acceptance and independent-review packets for the
   identity ruleset and correction acceptance, then make all identity consumers
   depend on them.

W04.3 is therefore not implementable from R4 without inventing contracts and paths.

### P1-03 — the ownership graph omits required runtime and phase evidence

R4 fixes several R3 ownership gaps: it names shared-export integration, sole Bronze,
Silver, and Gold layer-manifest writers, a post-integration code-admission step, an
independent code-manifest review, one rebuild entry point, and a final independent
rebuild review. The only proposed parallel group, 11A–11C, is path-disjoint.

The graph is nevertheless not ownership-complete.

First, the strict source artifact is defined as:

```text
data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json
```

Row 8 owns only bridge implementation/test/return paths. Row 22 is the runtime-output
packet, but its broad manifest scopes include only `bronze/**`, `silver/**`, and
`gold/**`; it omits `source/**`. No packet is authorized to materialize the strict
source manifest used by Bronze and `build_id`.

Second, the identity bundle and review queue have no generated paths or runtime owner,
as described in P1-02.

Third, the controlling W04 evidence is missing:

- no packet owns a data-health surface covering the required coverage matrix,
  freshness, identity backlog, reconciliation, rejected fields, temporal violations,
  and exact suppression states;
- no packet owns the final transformed W04 dataset card;
- no packet owns the G-W04 phase-gate report and master verification evidence; and
- no final master-only row owns the corresponding phase-registry/checkpoint evidence
  after independent acceptance.

The existing `docs/dataset-cards/w04-source.md` is a source-authority card, not a
completed raw-to-Gold dataset card. It still says that exact admitted counts “must
measure and report” later and warns that possession/minutes reconstruction can be
wrong. A final W04 card must incorporate the measured admitted populations, actual
transformations, identity backlog, supported/unsupported outputs, Gold coverage,
known biases, rights inheritance, and update/correction policy. W04.7 explicitly
requires the master to review it.

The quality library in row 16 is code, not the required retained data-health report.
The rebuild evidence in row 22 and independent report in row 23 do not implicitly own
the dataset card or master phase-gate decision. `AGENTS.md` reserves phase evidence
and registry/checkpoint actions to the master, so those paths must be explicit
master-owned serial rows rather than omitted.

Required correction:

1. Add `data/manifests/wyscout/v5/source/**` to the sole runtime-output packet while
   retaining `manifest_bridge.py` as the only serializer.
2. Add exact generated identity bundle/queue/correction paths and owners.
3. Add a serial data-health evidence packet after the completed rebuild with an exact
   report path and all P2.8/W04.6 dimensions.
4. Add a master-owned transformed dataset-card packet with an exact path, after data
   health and rebuild evidence, followed by independent review.
5. Add exact master verification and G-W04 phase-gate report paths after the final
   independent rebuild review.
6. Explicitly retain orchestration registry and local checkpoint actions as
   master-only after gate acceptance; do not give those paths to implementation
   agents.

`W04-DESIGN-PACKET-GRAPH-01` remains open.

### P1-04 — the code manifest does not bind every byte that can affect execution

The R4 code-manifest construction is non-circular:

- the code-admission implementation is itself under the full Wyscout Python seed;
- the final rebuild entry point, Wyscout package files, identity module, and W04
  contract are seeded;
- repository-local Python imports and package initializers are recursively closed;
- actual local file bytes, sizes, modes, paths, and local import edges are hashed;
- non-literal dynamic imports, repository native extensions, path-loaded executable
  code, and `sys.path` mutation are forbidden;
- the manifest does not contain its own digest or ID; and
- integration precedes admission/review, runtime verification precedes `build_id`,
  and build output is not an input to the code manifest.

Thus there is no self-hash cycle and the post-integration ordering is correct.

The remaining defect is that “actual rebuild code” includes more than repository
Python filenames.

For installed distributions, the manifest records only normalized distribution name,
selected lock version, and installed metadata version. The exact `uv.lock` bytes are
hashed, but a lock can list multiple platform artifacts for one version, and installed
package files can differ or be modified while their metadata version remains equal.
R4 does not record the selected wheel/sdist hash, platform/ABI selection, or verify
installed distribution file hashes. Therefore two environments can pass the same
name/version checks under one `lock_digest` while executing different third-party
bytes. This is especially material to exact Parquet output.

For repository-local non-Python resources, the AST closure discovers only Python
modules. R4 forbids executable code loaded from paths, but it neither hashes nor
categorically forbids behavior-affecting SQL, JSON, YAML, templates, package data, or
other files read by the admitted code, except for the individually listed semantic
authorities already present in `build_id`. A new unbound local lookup/resource could
alter behavior without changing the code-manifest digest.

The two-empty-root check does not solve this: both roots can share the same modified
environment/resource, and a later run can change behavior under the same `build_id`.

Required correction:

1. Record the exact selected locked artifact identity/hash for every imported
   distribution, plus the interpreter/platform/ABI selector needed to choose it.
2. Verify actual installed distribution contents, for example against signed/hashed
   distribution `RECORD` entries and the selected lock artifact, or recreate the
   locked environment from verified local artifacts immediately before both admission
   and rebuild and prove byte equality.
3. Extend admission to every repository-local non-Python resource transitively read
   by the rebuild, or fail closed on all such reads except an exact allowlist whose
   paths and digests are explicit `build_id` inputs.
4. Include these selected artifact/resource digests in `lock_digest`,
   `closure_digest`, or separate canonical build-identity inputs.
5. Add negative tests for same-version modified installed code and an added/changed
   local non-Python lookup.

`W04-DESIGN-CODE-CHECKPOINT-01` is therefore partially, not fully, closed.

## Six returned-defect closure table

| R3 defect | R4 result | Independent basis |
| --- | --- | --- |
| `W04-DESIGN-CODE-CHECKPOINT-01` (P1) | **PARTIAL / REWORK** | The arbitrary label is removed; local Python closure is content-addressed, non-circular, post-integration, independently reproduced, and checked before `build_id`. Installed third-party executable bytes and arbitrary local non-Python resources are not fully bound. |
| `W04-DESIGN-SEMANTIC-TEMPORAL-BOUNDARY-01` (P1) | **PARTIAL / REWORK** | The clock-free proof and truthful generation-clock adapter are exact and compatible with current strict contracts. The accepted/reviewed identity bundle is still falsely made available at source release. |
| `W04-DESIGN-SEMANTIC-AUTHORITY-SOURCE-01` (P1) | **CLOSED** | Field and possession semantics are explicitly project-defined, bind exact local inputs, require accountable decisions, separate independent review and master acceptance, use truthful acceptance clocks, preserve unknowns as `UNMAPPED`, and make no provider-native possession claim. |
| `W04-DESIGN-PACKET-GRAPH-01` (P1) | **OPEN / REWORK** | Shared code and layer-manifest writers are improved, but source-manifest runtime output, identity lifecycle artifacts, data health, final dataset card, and phase-gate evidence have no exact owner/path. |
| `W04-DESIGN-MANIFEST-FILE-COUNT-01` (P2) | **CLOSED** | Every construction, gate, and negative test now requires ordered `completion + 7 objects + 10 members == 18`. |
| `W04-DESIGN-SOURCE-COVERAGE-CONTRACT-01` (P2) | **CLOSED** | R4 names literal strict fields, types, counts, float `1.0`, exact dimension order, `overall`, empty missing tuple, and tuple-to-array serialization, separately from Gold coverage. |

Three of the six returned defects close. Two are partial and one remains open. The
packet definition of done requires all defects to close or a REWORK return.

## Retained five-closure table

| Previously accepted finding | R4 result | Independent basis |
| --- | --- | --- |
| `W04-DESIGN-SOURCE-SEAM-01` | **RETAINED CLOSED** | Only exact completion-declared direct/member paths may be read; downstream never opens the ZIP objects or directory-only exclusions; escape and symlink cases fail. |
| `W04-DESIGN-GOLD-GRAIN-01` | **RETAINED CLOSED** | The deterministic neutral role-context ID/version remains in the Gold key and snapshot UUID input; W05 cannot overwrite or collide silently. |
| `W04-DESIGN-MINUTES-01` | **RETAINED CLOSED** | Nominal substitution intervals and right-censoring are explicit; no terminal, elapsed minute, `minutes_played`, or per-90 denominator is fabricated. |
| `W04-DESIGN-COVERAGE-01` | **RETAINED CLOSED** | The six Gold dimensions, integer counts, zero-denominator rules, minimum overall, missing reasons, and ordered applicability are unchanged and distinct from strict source coverage. |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **RETAINED CLOSED AS A ROW SCHEMA** | Player × match × source/schema grain, match-bound team, result independence, evidence flags/counts, suppressed minutes, proof, lineage, and reconciliation remain exact. Dispatch still depends on closing the identity lifecycle that supplies its canonical player IDs. |

All five previously accepted closures survive as design components. They do not
override the new identity, temporal, code-truth, and phase-evidence blockers.

## Original nine-finding disposition after R4

| Original finding | Disposition |
| --- | --- |
| `W04-DESIGN-EVENT-CLOCK-01` | **PARTIAL / REWORK**: period-relative Decimal/order/null UTC and boundary adapter are correct, but the identity dependency clock still makes the full temporal proof untruthful. |
| `W04-DESIGN-SOURCE-SEAM-01` | **CLOSED** |
| `W04-DESIGN-MANIFEST-BRIDGE-01` | **CLOSED**: UUID construction is non-circular; tenant/classification are explicit; exact 18 rows and field-exact coverage now agree. |
| `W04-DESIGN-REBUILD-CLOCK-01` | **PARTIAL / REWORK**: semantic/receipt separation and local code-manifest sequence are sound, but actual executable/resource closure remains incomplete. |
| `W04-DESIGN-POSSESSION-AUTHORITY-01` | **CLOSED**: project semantics have an exact accountable local decision/review/acceptance route. |
| `W04-DESIGN-GOLD-GRAIN-01` | **CLOSED** |
| `W04-DESIGN-MINUTES-01` | **CLOSED** |
| `W04-DESIGN-COVERAGE-01` | **CLOSED** |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **CLOSED AS SCHEMA; IMPLEMENTATION BLOCKED BY W04.3** |

## Boundary challenges that pass

### Strict temporal contract compatibility

`W04SemanticTemporalProof` is clearly defined as a clock-free W04 product contract,
not a mutation or alternate wire form of `TemporalEvidence`. Its validators reproduce
the current strict cutoff, source IDs, watermark, valid-from, feature hash, lineage
hash, and source-dependency ordering requirements.

The adapter samples one truthful UTC generation clock at the boundary, requires it
not precede `valid_from_ts`, copies every semantic temporal field exactly, and supplies
the same instant to `RetrievalResult.generated_at`. It does not put that clock into
Gold bytes or build identity. This closes the structural
`generated_at_ts` incompatibility. P1-01 is a dependency input-clock defect, not an
adapter defect.

### Dependency kinds and row lineage

R4 correctly uses existing `source_manifest`, `identity_evidence`, and
`feature_schema` kinds. It no longer invents match/action dependency kinds. Source
row refs retain match/action evidence with null action UTC and deterministic ordering.
Field/taxonomy dependency UUIDs, kinds, decision/acceptance clocks, ordering, and
lineage hashing are implementable. Only the identity bundle clock/lifecycle is
returned.

### Semantic authority provenance

The field and possession routes no longer pretend source structure proves semantic
meaning. Each is a local project-defined decision with exact bound source/map/profile
digests, accountable actor/time, rationale, independent review, master acceptance,
and later truthful authority availability. Runtime label inference and undocumented
fallbacks are forbidden. Unknown combinations remain `UNMAPPED`. This is a valid
local normative algorithm boundary and does not require provider access.

### Exact source manifest, UUIDs, coverage, and rights

The strict manifest has exactly 18 ordered `SourceFileDigest` rows and literal current
`DataCoverage` population. UUIDv5 identity inputs do not contain their output UUID or
serialized manifest digest. Explicit tenant and deterministic trace values satisfy
strict UUID fields.

Restricted use, internal derivation/review, export denial, and required attribution
remain conservative and compatible with the current classification contract. No
container, external service, migration, dependency change, provider access, or
architecture expansion is introduced.

### Football product boundaries

Period-relative event evidence remains exact without an inferred 2H UTC. Match-start
window selection does not claim an action-instant cutoff. Coordinates retain anomalies
without clamping. Possession is labelled project-derived, unknown/uncertain actions
remain unassigned, and periods never merge. Player-match facts exclude score, winner,
points, result, current-team repair, elapsed minutes, and per-90 output.

## Required R5 acceptance gates

An R5 design can be accepted only when the standalone document:

1. assigns the reviewed identity bundle/ruleset truthful decision and acceptance
   clocks rather than source release;
2. provides complete crosswalk, identity bundle, review queue, correction, review,
   acceptance, version, confidence, and supersession contracts and owners for W04.3;
3. gives one exact packet owner to the strict source-manifest runtime output, identity
   runtime artifacts, data-health report, final transformed dataset card, master
   verification, and G-W04 gate evidence;
4. retains phase registry and checkpoint integration as explicit master-only work
   after independent gate acceptance;
5. binds the exact selected and installed third-party executable bytes plus every
   behavior-affecting local non-Python resource, or fails closed on their use;
6. retains the now-correct clock-free adapter, semantic authority routes, 18-row
   manifest, strict source coverage, five prior closures, rights, and local-only
   boundary; and
7. obtains a fresh independent review before any implementation packet is dispatched.

## Recommendation

Return R4 for a bounded R5 correction. Do not dispatch the implementation graph yet.
No self-approval is granted.

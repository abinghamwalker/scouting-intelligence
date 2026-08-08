# W04 Wyscout schema design independent review R2

## Decision

**REWORK**

No P0 defect was found. Four P1 defects and two P2 defects remain. They are within
the packet's design, temporal, lineage, authority, determinism, and decomposition
stop conditions, so the R3 design is not yet safe to decompose into implementation
packets.

The review is intentionally fail-closed. It does not reject the measured source
profile, the restricted local-only boundary, the period-relative event
representation, or the result-independent player-match grain. It rejects only the
claims that all nine prior findings are closed and that the current packet graph is
fully implementable without guessing.

## Scope and evidence reviewed

This review independently read the packet and all required evidence, including the
R3 design, the prior independent review, the accepted R2 source profile, the exact
completion manifest, the Wyscout source adapter, the evaluation contract, and the
current strict evidence and retrieval contracts.

No provider or network access was used. No excluded archive stream was opened. No
container or external service is introduced or required by this recommendation. No
source, code, configuration, data, dependency, migration, test, or orchestration
artifact was changed.

The measured profile remains the authority for what the source proves:

- event time is period-relative `eventSec`, with no proved period-start UTC or
  terminal;
- labels and numeric-key membership were measured, but possession boundaries,
  ownership rules, and event-to-possession semantics were not proved;
- exact elapsed player minutes are not supported;
- the admitted source seam is the completion-declared set of direct objects and ZIP
  members only.

## Ranked findings

### P1-01 — `code_checkpoint` is not an exact or verifiable code identity

R3 includes `code_checkpoint` in the canonical build identity, but defines it only as
an “immutable local checkpoint identifier supplied by the master.” It does not
define:

- the identifier syntax or namespace;
- the bytes or repository state from which it is derived;
- whether it identifies a commit, tree, source bundle, or reviewed manifest;
- the required relationship between that checkpoint and the exact implementation
  executed by the rebuild;
- a validation that the runtime code equals the admitted checkpoint; or
- a serial point in the packet graph at which all implementation is integrated
  before the checkpoint is frozen.

Consequently, a planned label, a stale checkpoint, or an arbitrary immutable string
can satisfy the prose while the rebuild executes different code. Including such a
label in `build_id` does not bind the product to its implementation. The statement is
non-circular at the hash level, but it is not a truthful code checkpoint.

The ordering also conflicts with the responsibility split. Implementation packets
cannot discover or change the checkpoint, yet the packet table has no master-owned
post-integration checkpoint-admission step. The quality/rebuild packet is listed
immediately after Gold, before any explicit integration/checkpoint freeze. That makes
the claimed closure of `W04-DESIGN-REBUILD-CLOCK-01` incomplete.

Required correction:

1. Define the exact checkpoint form and canonical text, preferably a repository
   commit/tree identity or a content-addressed immutable source manifest.
2. State which paths are covered and how submodules, generated code, dirty tracked
   state, and untracked runtime code are handled.
3. Add a master-owned serial integration and checkpoint-admission packet after all
   implementation writes and before any rebuild.
4. Require the rebuild entry point to verify that its executed implementation equals
   the admitted checkpoint before computing `build_id`.
5. Use the non-circular sequence: integrate implementation; freeze and independently
   admit the code checkpoint; then rebuild from exactly that checkpoint; then compute
   and verify the build ID and outputs. Semantic data outputs need not be committed
   to define the implementation checkpoint.

This review does not prescribe or perform a Git operation. It requires the design to
specify a truthful immutable implementation identity.

### P1-02 — clock-free semantic rows do not have a defined strict temporal boundary

R3 states that all Bronze, Silver, and Gold semantic rows contain no run-clock field,
while the Gold row requires “strict temporal evidence.” The existing strict
`TemporalEvidence` contract requires `generated_at_ts`. Its validator also requires
`generated_at_ts >= valid_from_ts`. The existing `RetrievalResult` contract separately
requires its operational `generated_at` to equal
`temporal_evidence.generated_at_ts`.

The proposed W04 data-contract packet does not define an alternative clock-free
temporal evidence type, its complete fields and validators, or an adapter into the
existing retrieval boundary. An implementer therefore has incompatible choices:

- serialize a truthful run generation time into Gold and lose the claimed
  clock-free semantic bytes and byte-for-byte rebuild identity;
- fabricate or freeze a generation time and misstate operational generation; or
- omit/replace `TemporalEvidence` without a specified compliant boundary.

The source-manifest dependency clock rule itself is conservative and acceptable:
using snapshot upstream availability for both `observed_at` and `available_at`
truthfully says when the complete frozen snapshot was knowable. It must not be
relabeled as action occurrence time, and R3 correctly keeps action UTC null. The
defect is the undefined derived temporal-evidence contract and its downstream
boundary, not the conservative source dependency clock.

The lineage mapping is also incomplete against the actual strict contract.
`DependencyKind` currently permits only `source_manifest`,
`identity_evidence`, `feature_schema`, `model_artifact`, and `retrieval_index`;
each dependency ID must be a UUID. R3 requires source, identity, registry, taxonomy,
selected-match, and selected-action dependency groups but never states:

- which allowed kind represents field-registry and taxonomy authorities;
- deterministic UUID rules for their string artifact IDs;
- whether match/action groups are evidence dependencies or row-level lineage only;
- exact `observed_at` and `available_at` rules for every admitted authority; or
- canonical dependency ordering before the lineage hash.

Required correction:

1. Define a complete W04 clock-free semantic temporal-proof contract with exact field
   types, dependency kinds, ID derivations, clocks, ordering, canonicalization, and
   validators; explicitly state that it is not the current `TemporalEvidence` if it
   omits `generated_at_ts`.
2. Define the later boundary adapter that adds a truthful execution
   `generated_at_ts` outside semantic product bytes when a current
   `TemporalEvidence` or `RetrievalResult` is created.
3. Keep that operational timestamp in a receipt/boundary payload and exclude it from
   semantic identity, while retaining the same source/authority lineage digest.
4. Alternatively, revise the existing architecture contract through a separately
   authorized architecture packet. R3 may not silently do that.
5. Map every registry, taxonomy, identity, match, and action lineage item to an exact
   existing kind or define an explicitly reviewed new strict kind and ID rule.

Until that boundary is explicit, `W04-DESIGN-EVENT-CLOCK-01` and
`W04-DESIGN-REBUILD-CLOCK-01` are only partially closed.

### P1-03 — the semantic-authority packets have schemas but no authority source

The field-registry and possession-taxonomy artifact schemas are useful controls:
they freeze paths, digests, unknown behavior, and synthetic challenges before
transformation. Serial ownership also prevents concurrent mutation. Those controls
do not, by themselves, establish the truth of the semantic decisions placed in the
artifacts.

The accepted source profile explicitly says that the measured field/mapping evidence
does not prove possession boundaries, ownership rules, or event-to-possession
semantics. R3 nevertheless requires exhaustive decisions such as `CONTROL`,
`CONTESTED`, `DEAD_BALL`, `RESTART`, `control_team_source`, opening/closing control,
and attachment behavior. It correctly forbids label substring matching and implicit
football convention, but names no local reviewed semantic source, accountable domain
reviewer, decision record, or other authority from which those values can be
populated.

“Master-owned” defines write responsibility; it does not turn an unsupported
interpretation into reviewed semantic evidence. As dispatched, the authority packet
can only:

- guess mappings, violating the design and measured-evidence boundary;
- classify every unsupported combination as `UNMAPPED`, which does not support the
  claimed resolved possession product; or
- stop for new authority.

The same problem applies, more narrowly, to field-to-canonical transforms marked
`reviewed_semantic` and the six literal `"null"` container decisions. Structural
facts can be copied from the profile; semantic transforms require named review
authority.

Required correction:

1. Supply an exact local, reviewed semantic input and accountable acceptance route
   for every `reviewed_semantic` field decision and possession predicate.
2. Bind its immutable digest and availability time into the authority artifact and
   dependency lineage.
3. If no such authority exists, narrow W04: preserve fields as unmapped, emit
   possession as unavailable/unresolved, set coverage and applicability accordingly,
   and remove claims of resolved possession closure.
4. Do not fetch a provider, infer from label substrings, or use undocumented football
   convention to fill the gap.

Therefore `W04-DESIGN-POSSESSION-AUTHORITY-01` remains open.

### P1-04 — the implementation packet graph is not ownership-complete

The explicit paths in rows 1–12 are disjoint, and parallel packets 7A–7C are locally
safe for the paths shown. The overall decomposition is not complete, because required
shared work is described but not assigned to an exact serial packet.

Specifically:

- shared exports or `__init__.py` edits are deferred to a separate integration
  packet “if needed,” but that packet has no ID, exact path set, dependency order, or
  acceptance check;
- the master-owned code-checkpoint freeze/admission step required for truthful build
  identity is absent;
- Bronze, Silver, and Gold layer manifests are required, but the table does not name
  an exact sole writer for each manifest or the code path that writes them;
- Silver consists of outputs from 7A, 7B, 7C, 8, and 9, yet no serial owner is named
  to reconcile those products and write the Silver layer manifest last;
- the rebuild needs one entry point that orchestrates all producers from an empty
  root and verifies its code checkpoint, but no exact ownership path is assigned;
- the authority text says an independent review records each authority digest, while
  the proposed table gives the same authority packet both the artifact and its
  review report and provides no independent authority-review packet.

An “if needed” shared edit cannot be left to implementation-time judgment in a graph
whose safety claim depends on exact paths. Nor may several packets opportunistically
write a common layer manifest.

Required correction:

1. Add explicit master-owned serial packet rows for shared integration, authority
   acceptance where independence is claimed, code-checkpoint admission, and final
   rebuild orchestration.
2. Give every row an exact write scope and dependency order.
3. Name one sole writer for each layer manifest, especially Silver, and require it to
   run after all contributing products.
4. Keep 7A–7C parallel only for their current disjoint module/test/return paths.
5. Ensure the rebuild packet consumes the admitted code checkpoint and does not
   mutate shared source or authority artifacts.

The current table is therefore not yet safe to dispatch even though its listed
implementation paths are pairwise disjoint.

### P2-01 — the strict-manifest file-count gate contradicts the construction

Section 3.3 constructs:

- one completion document;
- seven completion object records; and
- ten admitted ZIP members.

That is exactly 18 `SourceFileDigest` rows. The nine-finding closure section also says
18. Section 13 instead makes exact 17 file rows an acceptance gate.

Both cannot be satisfied. Omitting the completion document would contradict Section
3.3 and remove the explicitly listed evidence row; omitting an admitted object/member
would contradict the source seam. The correct count under the stated construction is
18.

Required correction: change every quality, test, and reconciliation statement to
exactly 18 rows and explicitly test the ordered sequence
`completion + 7 objects + 10 admitted members`.

### P2-02 — strict source-manifest coverage population is not field-exact

R3 says it provides exact `SourceSnapshotManifest` population, but its coverage table
uses the conceptual names `Numerator`, `Denominator`, and an accepted fraction. The
actual strict `CoverageDimension` fields are `coverage` as a strict float,
`observed_count`, and nullable `expected_count`; `DataCoverage` contains `overall`,
`dimensions`, and `missing_dimensions`.

For the accepted source manifest, the intended mapping appears to be
`observed_count=N`, `expected_count=D`, `coverage=float(N / D)`, overall `1.0`, and an
empty missing tuple. That inference should not be left to the bridge implementer,
especially because later Gold coverage uses a different, richer integer/decimal
structure with states and reason codes.

Required correction: state the exact strict-contract field mapping, value types,
dimension ordering, and tuple/list serialization for the source manifest. Explicitly
separate this strict source `DataCoverage` representation from the W04 Gold coverage
contract.

## Nine-finding closure table

| Prior finding | R2 result | Independent basis |
| --- | --- | --- |
| `W04-DESIGN-EVENT-CLOCK-01` | **PARTIAL / REWORK** | Period-relative decimal, period order, null action UTC, and snapshot-before-cutoff proof are sound. The required clock-free semantic temporal proof is not reconciled with strict `TemporalEvidence.generated_at_ts`, and authority dependency clocks/kinds are incomplete. |
| `W04-DESIGN-SOURCE-SEAM-01` | **CLOSED** | Reads are constrained to exact completion `object_path`/`member_path` values. Excluded directory-only entries are not opened. |
| `W04-DESIGN-MANIFEST-BRIDGE-01` | **PARTIAL / REWORK** | UUIDv5 identity is non-circular, tenant and classification are explicit, and the strict artifact is singular. The 17/18 file-count contradiction and field-inexact coverage population prevent full closure. |
| `W04-DESIGN-REBUILD-CLOCK-01` | **OPEN / REWORK** | Semantic/run receipt separation is sound in principle, but `code_checkpoint` does not bind actual implemented code and the strict temporal boundary still requires a generation clock. |
| `W04-DESIGN-POSSESSION-AUTHORITY-01` | **OPEN / REWORK** | Serial artifact schemas are defined, but no evidence/reviewer authority capable of making the required semantic mappings is supplied. |
| `W04-DESIGN-GOLD-GRAIN-01` | **CLOSED** | Neutral role context ID and version are in the logical key and snapshot UUID input; W05 cannot silently overwrite the W04 row. |
| `W04-DESIGN-MINUTES-01` | **CLOSED** | Period terminals and exact elapsed minutes remain unsupported; minutes and per-90 are explicitly suppressed rather than estimated or zero-filled. |
| `W04-DESIGN-COVERAGE-01` | **CLOSED WITH P2 REPRESENTATION CORRECTION** | The six Gold equations, zero-denominator states, minimum overall, missing rules, and applicability ordering are exact. P2-02 concerns strict source-manifest field population, not the Gold equations. |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **CLOSED** | The Silver fact has an exact match/player/team grain, result-independent fields, explicit lineage/coverage, minute state, and reconciliation rules. |

Five findings are substantively closed, two are partial, and two remain open. The
definition of done requires every finding to be demonstrably closed or a REWORK
return; therefore REWORK is mandatory.

## Independent boundary challenges

### Source paths, manifest identity, UUIDs, and rights

The source seam uses completion-declared logical paths and does not authorize probing
excluded entries. The manifest UUIDv5 input does not contain the resulting manifest
UUID or serialized manifest digest, so it is non-circular. UUIDv5 values are compatible
with the current strict UUID fields. Explicit immutable `TenantContext` is required
and no default tenant is allowed.

The proposed classification is conservative and valid against
`SourceUseClassification`: restricted use, derived data and internal review allowed,
export denied, and required attribution text present. Downstream manifests inherit
that restriction. Nothing in R3 authorizes an export, provider call, container, or
external service.

The manifest bridge does not pass only because its file-count gate and exact coverage
field population conflict with its otherwise sound construction.

### Temporal precision and dependency truthfulness

The exact `decimal128(22,18)` period-relative representation preserves measured
lexical scale without inventing a 2H UTC. Ordering by period rank, elapsed decimal,
source ordinal, and unique record ID is deterministic but does not falsely claim a
continuous match clock.

The match-start window is also properly distinguished from an action-instant cutoff.
The full snapshot availability is a truthful conservative observation/availability
time for the source-manifest dependency. Identity, registry, and taxonomy authorities
still need their own exact availability evidence; they cannot inherit a convenient
source clock unless that is factually their availability.

The current strict `TemporalEvidence` incompatibility in P1-02 must be corrected
without putting a run clock into semantic product identity.

### Semantic and physical determinism

Canonical row order, fixed schemas, canonical nulls, stable authority digests, one
file per partition, locked Parquet writer options, semantic digests, physical
digests, and two-empty-root comparison form a credible deterministic strategy.

That strategy is conditional on:

- a truthful checkpoint that identifies the exact executed implementation;
- exact writer/runtime admission and failure on mismatch;
- a sole writer for shared layer manifests;
- a complete clock-free semantic temporal contract; and
- stable, genuinely reviewed semantic authority artifacts.

Until those are fixed, equal build IDs do not necessarily mean equal code or equal
admitted boundary semantics.

### Identity, possession, minutes, coverage, and Gold

Entity UUIDv5 derivation is deterministic within source and entity kind, keeps zero
player separate, and does not repair missing identities from names/current-team
attributes. Possession segmentation rules are deterministic once an accepted
taxonomy exists, but R3 has not supplied the evidence needed to accept that taxonomy.

Minutes remain correctly suppressed. Coverage equations preserve counts, do not
waive missing evidence, and make optional zero-denominator states conditional on
accepted authority. The neutral Gold role context is stable and collision-resistant
with later role-specific versions. Result-derived score/winner/outcome features are
excluded from the player-match fact.

## Required R4 acceptance gates

An R4 design can be accepted only if all of the following are explicit in the
standalone design:

1. A verifiable post-integration `code_checkpoint` format, derivation, admission
   sequence, and runtime equality check.
2. A complete W04 clock-free temporal-proof contract plus a truthful adapter to the
   existing generation-clock-bearing boundary.
3. Exact dependency kinds, deterministic UUIDs, observed/available clocks, ordering,
   and hashing for every source and authority dependency.
4. A named local semantic authority and accountable review decision for every
   reviewed field and possession mapping, or a narrowed unresolved-possession scope.
5. One consistent strict-manifest count of 18 and exact
   `CoverageDimension`/`DataCoverage` field population.
6. An ownership-complete packet table containing exact serial authority review,
   integration, checkpoint admission, sole layer-manifest writers, and rebuild
   orchestration paths.
7. Continued restricted local-only operation with no provider, container, external
   service, migration, dependency, rights, or architecture expansion.

## Recommendation

Return the R3 design to the master for a bounded R4 correction. Do not dispatch the
proposed implementation packets yet. No self-approval is granted.

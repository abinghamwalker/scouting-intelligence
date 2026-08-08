# W04 Wyscout v5 canonical schema and deterministic rebuild design — R6

Status: **implementation design for master and independent review; not self-approved**

This document replaces R5 in full. It is the standalone design for the local-only W04
Wyscout Figshare v5 Bronze-to-Gold proof. R6 closes the seven P1 findings returned
against R5 without changing the approved architecture, source, rights, dependency,
migration, provider, network, or local-only boundary.

The binding measured evidence remains:

- `data/source/wyscout/v5/completion-manifest.json`, 6,803 bytes, SHA-256
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- `reports/phase-gates/W04/source-schema-profile.md`, SHA-256
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- upstream availability `2020-01-28T14:24:27Z` and actual local acquisition
  `2026-07-29T15:51:08.598589Z`;
- completion classification `wyscout_figshare_v5_cc_by_4`, licence `CC-BY-4.0`,
  restricted project control, attribution required;
- 7 direct objects, 10 durable admitted archive members, 4 directory-only
  exclusions, 7 competitions, 142 teams, 3,603 players, 1,826 matches, and
  3,071,395 event records; and
- the accepted source adapter in `src/scouting/sources/wyscout.py`, which writes only
  `objects/<name>`, `archive-members/<name>`, and `completion-manifest.json`.

No provider access, excluded-payload read, network, download, wheelhouse acquisition,
runtime label guessing, container, hosted artifact, dependency change, migration, new
local root, ignore-rule change, or export is authorised.

## 1. Claim boundary and global invariants

The permitted claim is a frozen historical engineering and player-evidence proof. It
does not establish current players, live coverage, provider continuity, women or
youth coverage, exact minutes, commercial-product equivalence, recruitment
relevance, or prospective benefit.

The following are normative.

1. Only completion-declared `object_path` and `member_path` values are readable.
2. `matches.zip` and `events.zip` are hash evidence only and are never opened
   downstream. The four excluded directories have no admitted payload path.
3. Provider record `id` identifies an event record; `eventId` identifies taxonomy.
   Names are display evidence only and never identity or semantic matching keys.
4. JSON numbers are parsed as `Decimal`. Event occurrence is period-relative. No
   second-half UTC, half-time duration, terminal, or continuous clock is invented.
5. Field, possession, identity, and supported-feature semantics are usable only after
   a master decision, independent review, and master acceptance with truthful clocks.
6. Source validity and project knowability are different clocks. Human decisions,
   reviews, acceptances, and corrections are never backdated to source release.
7. Existing `DependencyKind`, `IdentityEvidence`, `TemporalEvidence`, and
   `RetrievalResult` contracts are unchanged. W04 adds strict local contracts and
   projects only compatible resolved identity rows into `IdentityEvidence`.
8. Bronze, Silver, Gold, their semantic manifests, and semantic proofs contain no run
   ID, host path, elapsed duration, operational trace, or generation clock.
9. A real sampled generation clock is introduced only by the serving adapter.
10. Build identity closes over repository code, lock-declared artifact metadata,
    actual uv extracted-tree bytes, actual installed bytes, interpreter/libpython,
    standard library, and exact local resources before outputs are formed.
11. The original wheel ZIP hash is explicitly **not verified** when that archive is
    absent. Extracted trees and installed files are verified as the bytes they are.
12. Rights, identity, cutoff, authority, cache association, executable, resource,
    lineage, partition, reconciliation, and sole-writer failures are fail-closed.
13. Generated identity, product, staging, and runtime-bytecode state stays beneath the
    already-approved `data/working` root. No new storage or ignore boundary exists.
14. The full gate precedes the acceptance integration commit and annotated accepted
    tag. Registry/checkpoint evidence then lands in a distinct local ledger commit.

## 2. Exact completion-declared source seam

The source root is exactly `data/source/wyscout/v5`. The completion document is read
first and its digest checked. NFC POSIX-relative paths must remain below the resolved
root, be regular non-symlink files, and match declared bytes.

Readable direct objects are `objects/competitions.json`, `objects/teams.json`,
`objects/players.json`, `objects/eventid2name.csv`, and
`objects/tags2name.csv`. The ten readable archive members are the five
`archive-members/matches_<country>.json` and five
`archive-members/events_<country>.json` entries in Section 4. ZIP objects are hashed
only. For each country, distinct event `matchId` equals match `wyId`: England 380,
France 380, Germany 306, Italy 380, and Spain 380.

Any path not in the strict source manifest is denied. Directory scans, fallback
archive extraction, inferred layouts, symlinks, path aliases, and case-normalised
substitutes are forbidden.

## 3. Normative local semantic authorities

The profile establishes shapes, counts, key membership, and mapping-file bytes. It
does not establish field, possession, identity, or supported-feature meaning.

### 3.1 Field authority

The exact serial route is:

```text
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json
configs/schema/wyscout-v5-field-registry-v1.yaml
reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json
```

The decision and registry bind the completion/profile digests, event-map digest
`ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`,
tag-map digest
`e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922`,
and every measured `(record_kind,json_path)`. Each field decision is exactly
`TRANSFORM`, `PRESERVE_UNMAPPED`, or `FORBIDDEN`. Unknown fields are `UNMAPPED`;
unknown record kinds are quarantined as rejected records; runtime label matching and
provider-native semantic claims are false.

The independent reviewer records the decision and registry digests without editing
either. The master accepts only a `PASS`; acceptance records the decision, registry,
review path/digest, truthful actors and clocks, `status=accepted`, and nullable
`supersedes`. `decided_at <= reviewed_at <= accepted_at`; an observed clock is never
invented from file metadata. The registry has no self-digest.

### 3.2 Possession authority

After field acceptance, the analogous exact route is:

```text
reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json
configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml
reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json
```

Predicates use only numeric `event_id`, nullable numeric `subevent_id`, sorted
required tag IDs, and sorted forbidden tag IDs. A decision is exactly `CONTROL`,
`CONTESTED`, `DEAD_BALL`, `RESTART`, `NON_CONTROL_ADMIN`, or `UNMAPPED`. Global
policies remain:

```text
unknown_combination_policy: UNMAPPED
unknown_name_matching: forbidden
runtime_label_matching: forbidden
provider_native_possession_claim: false
period_boundary_policy: close
simultaneous_cross_team_policy: uncertain_boundary
```

The taxonomy binds accepted field authority. Decision/review/acceptance clocks are
truthful and ordered as above.

### 3.3 Supported-feature decision, review, and acceptance

The supported-feature registry is behavior-affecting semantic authority and is
therefore accepted **before Gold**, through this exact serial route:

```text
reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json
configs/features/wyscout-v5-supported-count-features-v1.yaml
reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json
```

The master decision contains fixed decision/registry IDs, `authority_class`,
`decided_by`, truthful `decided_at`, the strict source-manifest digest, accepted
identity/field/possession authority IDs and digests, all W04 product schema versions,
neutral-role-context version, and an exhaustive ordered definition for every
supported, suppressed, and unavailable field. Each entry binds input fields,
aggregation, applicability, denominator policy, output type, state, reason, and
schema version. Minutes, elapsed/rate/per-90, continuous-time, action-value, provider
possession, outcome-dependent, role-inferred, and otherwise unsupported features are
explicitly `not_available` or `suppressed_unsupported_denominator`; absence never
grants permission.

The independent review reproduces canonical registry bytes and the exhaustive
supported/suppressed decision set, records `reviewed_by`, truthful `reviewed_at`, and
`recommendation=PASS|FAIL`, and cannot edit the candidate. The master acceptance
binds the decision, registry, and review digests and records `accepted_by`,
`accepted_at`, `status=accepted`, and nullable `supersedes`. Required order is
`decided_at <= reviewed_at <= accepted_at`; actual operation times are used.

Canonical parsed YAML is JSON with sorted object keys and schema-declared array order.
The registry digest excludes acceptance bytes. The acceptance digest binds the
registry digest, avoiding a cycle. Gold, `feature_schema_hash`, build identity, and
the local-resource set are unavailable until this acceptance exists.

## 4. Source-manifest bridge and exact 18-row source evidence

`TenantContext` is explicit: `tenant_id` has no default and nullable `club_id` is
fixed.

```text
manifest_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source-snapshot-manifest:wyscout:v1")
manifest_identity_input = canonical_json({
  "bridge_version": "w04-wyscout-manifest-bridge-v1",
  "completion_sha256": <exact digest>,
  "source_id": "wyscout-soccer-match-events-figshare-v5",
  "tenant_id": <canonical UUID>,
  "club_id": <canonical UUID or null>
})
manifest_id = UUIDv5(manifest_namespace, SHA256(manifest_identity_input))
trace_id = UUIDv5(manifest_id, "semantic-manifest-trace:w04-wyscout:v1")
```

The manifest uses existing `SourceSnapshotManifest`, exact clocks, restricted
classification, derived/internal-review allowed, export false, and attribution
required. Its `files` tuple is exactly the following order:

| # | `object_path` | bytes | rows | SHA-256 |
| ---: | --- | ---: | ---: | --- |
| 1 | `completion-manifest.json` | 6,803 | null | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| 2 | `objects/competitions.json` | 1,209 | 7 | `39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1` |
| 3 | `objects/teams.json` | 27,404 | 142 | `9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d` |
| 4 | `objects/players.json` | 1,737,347 | 3,603 | `877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e` |
| 5 | `objects/matches.zip` | 645,097 | null | `c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9` |
| 6 | `objects/events.zip` | 77,323,413 | null | `877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45` |
| 7 | `objects/eventid2name.csv` | 1,001 | 36 | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` |
| 8 | `objects/tags2name.csv` | 1,754 | 59 | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` |
| 9 | `archive-members/matches_England.json` | 1,694,720 | 380 | `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29` |
| 10 | `archive-members/matches_France.json` | 1,707,222 | 380 | `851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea` |
| 11 | `archive-members/matches_Germany.json` | 1,377,328 | 306 | `6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9` |
| 12 | `archive-members/matches_Italy.json` | 2,019,196 | 380 | `afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725` |
| 13 | `archive-members/matches_Spain.json` | 1,705,380 | 380 | `9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce` |
| 14 | `archive-members/events_England.json` | 188,888,614 | 643,150 | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` |
| 15 | `archive-members/events_France.json` | 186,374,196 | 632,807 | `18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317` |
| 16 | `archive-members/events_Germany.json` | 152,916,631 | 519,407 | `2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3` |
| 17 | `archive-members/events_Italy.json` | 190,544,685 | 647,372 | `b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84` |
| 18 | `archive-members/events_Spain.json` | 184,164,406 | 628,659 | `b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154` |

The exact existing source `DataCoverage` is:

```text
source_object_integrity              7 / 7 = 1.0
admitted_member_integrity           10 / 10 = 1.0
match_partition_presence             5 / 5 = 1.0
event_partition_presence             5 / 5 = 1.0
partition_match_id_alignment         5 / 5 = 1.0
scope_exclusion_directory_only       4 / 4 = 1.0
overall = min(all dimensions) = 1.0
missing_dimensions = ()
```

Coverage values are strict Python `float` `1.0`; counts are strict non-negative
`int`. Zero expected counts, 17/19 rows, reordered rows, duplicate paths, or conceptual
Gold coverage fields fail.

The sole artifact is:

```text
data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json
```

Canonical entity identity uses numeric keys only:

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
kind_namespace = UUIDv5(source_namespace, "<competition|team|player|match|action>")
canonical_id =
  UUIDv5(kind_namespace, "figshare-v5:<canonical-decimal-source-id>")
```

Zero is not a player identity. Names, current teams, and external knowledge cannot
repair missing, malformed, duplicate, conflicting, or absent master-table keys.

## 5. Complete identity authority and lifecycle

### 5.1 Ruleset route and exact generated roots

The exact authority route is:

```text
reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json
configs/schema/wyscout-v5-identity-ruleset-v1.yaml
reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json
```

The accepted ruleset binds tenant, manifest, all four master-table groups, UUID rules,
the classification-method table below, queue policy, both correction routes, and all
digests. The reviewer reproduces mappings/counts/ambiguities; the master accepts only
`PASS`. Clocks are truthful and ordered.

All generated identity state is under the already-declared and ignored generated
root, with no alias:

```text
data/working/wyscout/v5/identity/review-queues/
  <queue_sha256>.identity-review-queue.json
data/working/wyscout/v5/identity/bundles/
  <identity_bundle_sha256>.identity-bundle.json
data/working/wyscout/v5/identity/corrections/
  <correction_id>.identity-correction.json
```

The guarded-path category is `W04_IDENTITY_RUNTIME`. Only the identity runtime
serializer may write it. Readers begin from an exact accepted bundle path, validate
its digest, and may then open only the exact queue/correction relative paths named by
that bundle. Directory scans, newest-file selection, alternate roots, and unreferenced
identity files are denied.

### 5.2 Crosswalk classification method and existing projection

`W04IdentityCrosswalkRow` has the following relevant strict fields:

```text
schema_version: 1
crosswalk_schema_version: "w04-wyscout-crosswalk-v2"
tenant_context
entity_kind: COMPETITION | TEAM | PLAYER | MATCH
source_identity
source_manifest_id, source_manifest_sha256
source_row_refs: non-empty sorted tuple
canonical_id: UUID | null
version: positive int
classification_method: W04IdentityClassificationMethod
identity_match_method: existing IdentityMatchMethod | null
confidence: exactly 0.0 or 1.0
state: RESOLVED | REVIEW_REQUIRED | REJECTED
valid_from, valid_to
available_at
reviewed_by
supersedes_evidence_digest
identity ruleset decision/review/acceptance IDs and digests
reason_codes: sorted unique non-empty tuple
evidence_digest, crosswalk_row_id, trace_id
```

The W04-only classification enum and all valid combinations are exact:

| Situation | Row/effective state | `classification_method` | `identity_match_method` | canonical/confidence/reviewer |
| --- | --- | --- | --- | --- |
| unique valid same-kind source key | `RESOLVED` | `SOURCE_KEY_DETERMINISTIC_RESOLUTION` | `DETERMINISTIC` | UUID / 1.0 / null |
| malformed, absent, duplicate, collision, or conflict | `REVIEW_REQUIRED` | `SOURCE_KEY_REVIEW_REQUIRED` | null | null / 0.0 / null |
| source player key zero | `REJECTED` | `PROVIDER_ZERO_ACTOR_REJECTION` | null | null / 0.0 / null |
| queued item reviewed to a canonical entity | `RESOLVED` | `REVIEWED_QUEUE_RESOLUTION` | `REVIEWED` | UUID / 1.0 / non-null |
| queued item reviewed as rejected | `REJECTED` | `REVIEWED_QUEUE_REJECTION` | null | null / 0.0 / non-null |
| current resolved row directly superseded to another entity | `RESOLVED` | `REVIEWED_DIRECT_SUPERSESSION_RESOLUTION` | `REVIEWED` | UUID / 1.0 / non-null |
| current resolved row directly superseded to rejection | `REJECTED` | `REVIEWED_DIRECT_SUPERSESSION_REJECTION` | null | null / 0.0 / non-null |
| immutable prior row behind accepted edge | effective `SUPERSEDED` | `ACCEPTED_SUPERSESSION_EDGE` on the bundle index | original value unchanged | original bytes unchanged |

`IdentityMatchMethod.EXACT` is not used by W04. `SUPERSEDED` is an exact effective
bundle-index state, not a mutation of an old row. An implementation cannot assign a
different classification or match method.

Only a current effective `RESOLVED` row projects to existing `IdentityEvidence`.
Projection renames `identity_match_method` to `method` and copies the existing
contract fields exactly. Null match methods, null canonical IDs, non-resolved states,
and superseded rows never project. The existing contract and enum are unchanged.

The evidence digest is SHA-256 of canonical JSON of all semantic fields through
`reason_codes`, excluding the digest, row ID, and trace. IDs remain:

```text
crosswalk_row_id = UUIDv5(
  identity_crosswalk_namespace,
  tenant_id + ":" + entity_kind + ":" + source_identity.canonical_json +
  ":" + version + ":" + evidence_digest)
trace_id = UUIDv5(crosswalk_row_id, "w04-identity-crosswalk-trace-v2")
```

Initial `version=1`; later versions are exactly prior + 1 and name the prior evidence
digest. Gaps, forks, tenant changes, invalid combinations, or classification-method
changes fail. Initial `valid_from` may equal source release, while initial
`available_at` is the truthful ruleset acceptance time.

### 5.3 Queue and bundle

Queue canonical bytes exclude their own digest and contain tenant/manifest/ruleset
bindings, `prior_queue_sha256`, sorted items, and exact counts. An item contains its
UUIDv5 ID, kind, source identity, reason family/codes, sorted refs,
`first_seen_source_valid_at`, `available_at`, status, and nullable disposition ID.
Status is `OPEN`, `IN_REVIEW`, `RESOLVED_BY_CORRECTION`, or
`REJECTED_BY_CORRECTION`. Only `REVIEW_REQUIRED` rows enter the queue. Player zero is
rejected without an invented item. The measured 23 absent bench and 8 absent
substitution-in references remain queued and excluded unless separately reviewed.

The bundle path is content-addressed as shown in 5.1. Canonical top-level fields are:

```text
schema/bundle versions; tenant; source manifest ID/digest
ruleset decision/review/acceptance IDs, paths, digests, and truthful clocks
current_rows
historical_row_digests
effective_state_index entries including classification method
supersession_edges: sorted (prior_digest,new_digest)
counts_by_kind_and_effective_state
review_queue_path, review_queue_sha256
accepted_corrections: sorted correction ID/path/digest/acceptance/accepted_at
prior_identity_bundle_id, prior_identity_bundle_sha256
observed_at, available_at
```

Rows sort by kind/provider/source ID/source version/version/evidence digest. Every
master row and every referenced unresolved key appears exactly once in the effective
index. Queue, counts, history, edges, correction chain, and referenced paths are
recomputed before hashing.

```text
identity_bundle_id =
  UUIDv5(w04_dependency_namespace,
    "identity_bundle:" + identity_bundle_sha256)
```

That exact ID is the bundle external ID, the identity dependency ID, and the build
identity field. The dependency uses existing kind `identity_evidence`,
`observed_at=ruleset decision.decided_at`, and
`available_at=max(ruleset acceptance, included correction acceptances)`.

### 5.4 Two explicit reviewed correction routes

Every correction uses:

```text
reports/reviews/W04/identity-corrections/<correction_id>.decision.json
reports/reviews/W04/identity-corrections/<correction_id>.independent-review.md
reports/reviews/W04/identity-corrections/<correction_id>.acceptance.json
data/working/wyscout/v5/identity/corrections/
  <correction_id>.identity-correction.json
```

The decision binds `correction_route`, tenant/source identity, exact current prior
bundle and row, old state/canonical ID, proposed resolution or rejection, non-empty
reason, source refs, `new_version=prior+1`, proposed validity, actor, and truthful
clock. Review is independent and immutable. Acceptance binds decision/review digests,
is `accepted`, and has
`accepted_at >= max(decided_at,reviewed_at,prior_bundle.available_at)`. For this
frozen source, a correction supersedes the prior assertion over the same source-valid
interval: new `valid_from=prior.valid_from` and `valid_to=prior.valid_to`. Its later
`available_at=accepted_at` expresses knowability without backdating.

The normalized correction schema has common fields plus an exact discriminated union:

```text
common:
  schema/correction versions, correction_id, correction_route
  tenant, entity_kind, source_identity
  prior_bundle_id, prior_bundle_sha256
  prior_evidence_digest, prior_version
  new_crosswalk_row, reason
  decision/review/acceptance paths, digests, actors, clocks, statuses

QUEUE_DISPOSITION:
  queue_disposition = {
    prior_queue_sha256: non-null,
    queue_item_id: non-null,
    prior_status: OPEN | IN_REVIEW,
    next_status: RESOLVED_BY_CORRECTION | REJECTED_BY_CORRECTION
  }
  direct_supersession = null

DIRECT_CURRENT_RESOLVED_SUPERSESSION:
  queue_disposition = null
  direct_supersession = {
    asserted_current_bundle_id,
    asserted_current_evidence_digest,
    asserted_prior_state: RESOLVED
  }
```

For `QUEUE_DISPOSITION`, the item must exist in the prior bundle's queue and reconcile
to the prior row. The identity serializer emits a new queue snapshot linked to the
prior queue, transitions that one item, and sets transition availability to accepted
time. It emits a reviewed resolved or reviewed rejected row with the route-specific
classification method, then a new bundle.

For `DIRECT_CURRENT_RESOLVED_SUPERSESSION`, the prior row must be the current
non-superseded resolved row in the asserted bundle and must have no queue item. The
serializer emits **no queue item, transition, or queue snapshot**. The new bundle
retains the exact prior queue path/digest unchanged. It emits a reviewed direct
resolved or direct rejected row, adds the supersession edge, and regenerates the
bundle. Thus no queue history is invented.

Both routes set `supersedes_evidence_digest`, retain all prior bytes, advance the
bundle availability and digest/ID, and consequently change dependency lineage,
watermark, and build ID. Cross-route fields, stale bundle/queue, non-current prior,
missing independent `PASS`, actor/clock mismatch, non-consecutive version, name-only
evidence, or queue creation on the direct route fails.

## 6. Exact temporal dependency set

W04 uses exactly five dependencies:

| Order basis | Evidence | Existing kind | observed | available |
| --- | --- | --- | --- | --- |
| enum rank then ID | strict source manifest | `source_manifest` | source release | source release |
| enum rank then ID | accepted identity bundle | `identity_evidence` | identity decision | max identity/correction acceptance |
| enum rank then ID | accepted field registry | `feature_schema` | field decision | field acceptance |
| enum rank then ID | accepted possession taxonomy | `feature_schema` | possession decision | possession acceptance |
| enum rank then ID | accepted supported-feature registry | `feature_schema` | feature decision | feature acceptance |

Each feature dependency ID is UUIDv5 over its artifact type, fixed artifact ID,
artifact digest, and acceptance digest. Dependencies sort by
`(DependencyKind enum rank, dependency_id.bytes, digest, observed_at, available_at)`.
Duplicates by kind/ID fail. `lineage_hash` is the SHA-256 of all five complete ordered
records. The cardinality is exactly 5: 1 source, 1 identity, 3 feature-schema.

Every observed and available clock is strictly before `feature_cutoff_ts`; equality
fails. The watermark is the maximum of all five availability clocks. Cutoffs before
or equal to the supported-feature decision, review (because acceptance is later), or
acceptance fail. A registry revision requires a new decision/review/acceptance,
dependency ID/digest, feature schema hash, lineage hash, watermark, and build ID.

`W04SemanticTemporalProof` is clock-free and contains snapshot/watermark/valid-from/
cutoff, manifest IDs, feature schema hash, dependency lineage, period-relative
precision, and `partial_match_claim_supported=false`. It accepts exactly the five
dependencies above. `feature_schema_hash` binds field, possession, accepted supported
feature registry **and its acceptance digest**, action, lineup, possession,
player-match, Gold schemas, and neutral role context.

At serving time one real injected UTC clock is sampled:

```text
adapt_w04_temporal_proof(proof, generated_at_ts) -> TemporalEvidence
```

The adapter revalidates the proof, requires generation at or after valid-from, copies
all existing fields one-to-one, and adds only generation. `RetrievalResult.generated_at`
uses the same sample. Boundary receipts are operational and not build inputs.

## 7. Football products retained

`silver_action` retains period code/rank, exact `decimal128(22,18)` elapsed seconds,
source scale 0..18, `occurrence_precision=period_relative`, null period/action UTC,
and ordering:

```text
(period_rank, period_elapsed_seconds, source_record_ordinal,
 source_event_record_id)
```

Gold selects complete matches by
`window_start_utc <= match_start_utc < window_end_utc`; match start and all five
dependencies are strict-before cutoff. Partial-match/action-instant claims remain
`unsupported_period_relative_occurrence`.

Substitution minute `m` means nominal `[m,m+1)`. For start `[s0,s1)` and end `[e0,e1)`:

```text
lower = max(0, e0 - s1)
upper = max(0, e1 - s0)
```

Open stints are right-censored. Event maxima, `Regular`, 90, and substitution maxima
cannot invent a terminal. Exact/elapsed minutes and all per-90 outputs remain absent
or null, `per90_eligible=false`, with
`suppressed_unsupported_denominator`.

Silver retains exact match, action, lineup-stint, project-defined possession, and
player-match schemas from R5. Actions preserve 7,821 string subevent IDs as unmapped,
source coordinate order, x=-1, and two y=101 anomalies. Possessions never cross
periods and never claim provider-native possession.

The player-match key remains:

```text
(tenant_id, source_manifest_id, match_id, player_id,
 player_match_fact_schema_version)
```

Team is match-bound. Facts are result-independent and contain evidence flags/counts,
nominal stint states, null elapsed fields, six coverage structures, applicability,
clock-free proof, refs, and all source/identity/authority/schema digests. They contain
no score, winner, points, outcome, current team, minutes, or per-90.

Candidate pairs are the union of resolved non-zero lineup, bench, substitution, and
event references. Zero actors are separate. The measured 50,522 event player-match
pairs are evidence counts, not minutes evidence.

Gold grain remains neutral and collision-free:

```text
(tenant_id, player_id, competition_id, season_id,
 role_context_id, role_context_version,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, dependency_lineage_hash)
```

Neutral context remains UUIDv5 namespace
`urn:scouting-intelligence:role-context`, version
`w04-neutral-role-context-v1`, state `neutral_unscoped`.

Gold coverage remains six exact integer numerator/denominator dimensions: identity,
lineup, action, coordinate, possession, and temporal. For denominator > 0 the ratio
is exact and numerator cannot exceed denominator. Only coordinate/possession may
equal 1 at denominator zero when authority proves
`not_applicable_zero_denominator`; otherwise it is 0 with
`missing_zero_denominator`. Overall is the minimum. Rights/manifest/authority/
identity/partition/lineage/cutoff failures suppress; uncertainty makes the result
`research_only`; only complete registry-supported rows can be `w04_data_ready`.

## 8. Exact generated path grammar and sole writers

All path tokens are deterministic:

```text
sha = exactly 64 lowercase hex
uuid = lowercase canonical 36-character UUID
country = england | france | germany | italy | spain
utc = UTC rendered YYYYMMDDTHHMMSSffffffZ, always six fractional digits
build_id = exactly 64 lowercase hex
run_id = canonical UUID sampled once per invocation
```

Paths are NFC POSIX relative paths with no empty, dot, dot-dot, percent-encoded, or
case-folded segments. The only generated roots are the approved `data/working` and
`runs`; reviewed manifests remain in approved `data/manifests`.

### 8.1 Bronze raw preservation and quarantine

For each non-empty admitted source-record partition:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  records/record_kind=<kind>/source_sha256=<source_sha>/part-00000.parquet
```

`kind` is exactly `competition`, `team`, `player`, `event-taxonomy`,
`tag-taxonomy`, `match`, or `action`. The source SHA disambiguates the five country
members. Bronze stores the complete parsed raw object as canonical JSON without
semantic deletion, its canonical digest, exact source path/digest/ordinal, raw field
paths/types, accepted registry, admission state, source availability, rights, tenant,
manifest, and row lineage. The immutable source bytes remain the byte authority.

Quarantine paths are:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  quarantine/rejected-record/record_kind=<kind>/
  source_sha256=<source_sha>/part-00000.parquet

data/working/wyscout/v5/bronze/build_id=<build_id>/
  quarantine/rejected-field/record_kind=<kind>/
  source_sha256=<source_sha>/part-00000.parquet
```

A rejected-record row contains source ref, complete canonical raw record and digest,
sorted rejected paths, rejection code, registry/acceptance digests, source
availability, tenant, and inherited rights. A rejected-field row contains source ref,
exact JSON path, canonical raw value and digest, measured JSON type, decision
(`PRESERVE_UNMAPPED|FORBIDDEN`), reason, registry/acceptance, and rights. Unknown
record kinds produce rejected-record rows. Unknown or forbidden fields produce
rejected-field rows and cannot disappear silently. Empty quarantine partitions have
a manifest `empty` count and no zero-row Parquet file.

`bronze.py` is the sole serializer for raw and both quarantine families and the sole
writer of:

```text
data/manifests/wyscout/v5/bronze/<build_id>.manifest.json
```

### 8.2 Every Silver product

The exact final formulas are:

```text
data/working/wyscout/v5/silver/build_id=<build_id>/
  competition/source_partition=global/part-00000.parquet
data/working/wyscout/v5/silver/build_id=<build_id>/
  team/source_partition=global/part-00000.parquet
data/working/wyscout/v5/silver/build_id=<build_id>/
  player/source_partition=global/part-00000.parquet
data/working/wyscout/v5/silver/build_id=<build_id>/
  match/source_partition=<country>/part-00000.parquet
data/working/wyscout/v5/silver/build_id=<build_id>/
  action/source_partition=<country>/part-00000.parquet
data/working/wyscout/v5/silver/build_id=<build_id>/
  lineup-stint/source_partition=<country>/part-00000.parquet
data/working/wyscout/v5/silver/build_id=<build_id>/
  possession/source_partition=<country>/part-00000.parquet
data/working/wyscout/v5/silver/build_id=<build_id>/
  player-match-fact/source_partition=<country>/part-00000.parquet
```

The fixed country token is derived only from the admitted member filename; no content
label chooses a path. `entities.py` solely serializes competition/team/player/match;
`actions.py` action; `lineups.py` lineup-stint; `possessions.py` possession; and
`player_match.py` player-match-fact. `silver_manifest.py` alone writes:

```text
data/manifests/wyscout/v5/silver/<build_id>.manifest.json
```

### 8.3 Gold and temporal receipts

For each non-empty contributing competition/window partition:

```text
data/working/wyscout/v5/gold/build_id=<build_id>/player-window/
  competition_id=<uuid>/window_definition_id=<uuid>/
  window_start_utc=<utc>/window_end_utc=<utc>/
  feature_cutoff_ts=<utc>/part-00000.parquet
```

Rows inside sort by the full Gold key, including season and neutral role context.
`gold.py` is the sole Gold serializer and sole writer of:

```text
data/manifests/wyscout/v5/gold/<build_id>.manifest.json
```

One rebuild invocation receipt is:

```text
runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json
```

One temporal adapter receipt per Gold partition is:

```text
runs/w04/wyscout-rebuild/<build_id>/<run_id>/boundary/
  <sha256-of-exact-gold-relative-path>.temporal-boundary-receipt.json
```

`temporal_boundary.py` alone serializes boundary receipts; `rebuild.py` writes only
the invocation receipt and invokes named serializers. Receipts bind the exact Gold
path/digest/proof, real generation clock, adapter result, run/trace IDs, and code/build
identity. They are never Gold/manifest/build-ID inputs. Two-root review compares
semantic relative paths exactly and compares boundary suffixes after removing the
permitted `<run_id>` prefix; receipt clocks/run IDs may differ.

### 8.4 Staging, atomic completion, manifests, and readers

Each serializer stages only beneath its own matching family:

```text
data/working/wyscout/v5/.staging/<build_id>/<run_id>/
  bronze/<same suffix as final Bronze path>.partial
  silver/<product>/<same partition suffix>.partial
  gold/<same suffix as final Gold path>.partial
```

An empty runtime bytecode prefix is:

```text
data/working/wyscout/v5/.staging/<build_id>/<run_id>/runtime-pycache/
```

It is not a product and must remain empty. Serializers write, flush, close, hash, and
validate staged files; code/environment closure is rechecked; each file is atomically
renamed to its immutable final path; an existing unequal destination fails. The
layer manifest is written last through an exact sibling
`.<build_id>.<run_id>.manifest.json.partial` and atomically renamed. Final readers
require the manifest completion marker and open only the exact payload paths it
lists. A final payload not referenced once, a referenced missing payload, a partial,
or a cross-layer path fails.

Manifest file entries contain repo-relative path, serializer ID/version, schema,
row count, semantic digest, physical SHA-256/size, ordered parent digests, partition
values, rights, and completion state. Bronze manifest references all raw/quarantine
files; Silver references every Silver file and the Bronze manifest digest; Gold
references every Gold file, Silver manifest, all five dependencies, feature schema,
and proofs. Manifests do not copy payloads.

Required path tests create two distinct empty project roots, run the same admitted
build, remove only each absolute root, and require equality of all `data/working`
final relative paths, schemas, rows, semantic/physical digests, and all three manifest
bytes. A grammar test enumerates every family above and proves pairwise prefix
disjointness among identity, Bronze, Silver, Gold, staging, receipts, and committed
manifests. It also proves exactly one serializer claim per final/staging family,
two-root containment, unknown-field quarantine, no zero-row quarantine file, no
unmanifested final file, and no rebuild-orchestrator serialization.

## 9. Offline code, uv extracted-cache, installed runtime, and resources

Admission runs serially after W04 code and shared exports are frozen. It is wholly
offline and does not materialize or request a wheel archive.

### 9.1 Repository and selector

Seeds remain `scripts/rebuild_wyscout_v5.py`, Wyscout data-product modules,
`src/scouting/identity/wyscout.py`, and the W04 contract. AST traversal includes all
reachable repository-local modules and package `__init__.py`; dynamic/nonliteral
imports, path-loaded code, `sys.path` mutation, symlinks, aliases, generated code,
repository native extensions, and writable code fail.

The selector records platform, implementation/full version/cache tag, SOABI,
MULTIARCH, EXT_SUFFIX, byte order, libc, and ordered compatible tags. Python is
`==3.12.*`. For every external distribution owning a closure import, exactly one
marker branch and compatible wheel record are selected from `uv.lock`.

Each selected artifact has two truth domains:

```text
lock declaration:
  normalized name, version, filename, URL basename,
  declared SHA-256, declared size, parsed tags, selector digest

local byte verification:
  archive_state = ORIGINAL_WHEEL_ARCHIVE_ABSENT
  original_wheel_zip_sha256_verified = false
  original_wheel_zip_size_verified = false
  association_basis = UV_WHEELS_V5_EXACT_NAME_VERSION_TAG_LINK
  extracted_tree_sha256, extracted_record_sha256,
  extracted metadata/WHEEL digests and exact file records
```

The lock hash/size are retained as lock-declared metadata. They are never relabelled
as a locally reproduced archive hash/size. An `.http`/`.msgpack` sidecar is not the
wheel and cannot satisfy those fields.

### 9.2 Exact uv cache association

From the selected wheel filename, admission derives:

```text
wheels-v5/pypi/<pep503-normalized-distribution>/
  <wheel-filename-with-distribution-prefix-and-.whl-removed>
```

That exact entry must be one symlink. Its immediate target must be one directory
exactly below `archive-v0/<opaque-key>` in the same resolved uv cache root. The target
tree may contain only directories and regular non-symlink files. `METADATA` Name and
Version and `WHEEL` Tag must match the selected lock record. Its `RECORD` is strict
UTF-8 CSV; every hashed row must match target bytes/size, only `RECORD` itself may be
unhashed, and every target file must occur exactly once.

The operational admission receipt records the resolved cache root, cache-relative
selector link, raw link text, exact `archive-v0/<opaque-key>` target, link lstat,
`.http` and `.msgpack` sidecar path/digest/size, and extracted tree enumeration. Host
absolute paths and opaque cache keys do not enter semantic products or build ID.
The canonical code manifest records the stable selector key, association basis,
tree/file/metadata/RECORD digests, and false archive-verification flags.

The observed state motivating this algorithm includes:

```text
wheels-v5/pypi/pydantic/2.13.4-py3-none-any
  -> archive-v0/hZn3d0nQeuHZMbMvwu2wZ
wheels-v5/pypi/pyarrow/23.0.1-cp312-cp312-macosx_12_0_arm64
  -> archive-v0/qmE4fOTLPNxRYsAoWNC1x
wheels-v5/pypi/polars/1.43.0-py3-none-any
  -> archive-v0/UZ5njLwpNYlTnR_FiTjvi
wheels-v5/pypi/packaging/26.2-py3-none-any
  -> archive-v0/ta1RuwiHup8YM4bS5IZ7r
wheels-v5/pypi/pyyaml/6.0.3-cp312-cp312-macosx_11_0_arm64
  -> archive-v0/JYtSSNi0Fy-dfIf8atf6x
```

These are extracted directories, not ZIP archives. A missing/ambiguous link, changed
target tree, metadata/tag mismatch, or claim of wheel ZIP verification fails. A future
archive-based algorithm requires a separately reviewed design; it is not selected
automatically.

### 9.3 Installed `RECORD`, files, and exact generated rules

For each extracted tree, PEP 427 member mapping is deterministic: root and
`.data/purelib`/`.data/platlib` members map into site-packages;
`.data/scripts` maps into the environment scripts path; `.data/headers` into the
environment include scheme; `.data/data` into the environment prefix. Any escape or
collision fails.

Exactly one installed `.dist-info` matches Name/Version. Every extracted `RECORD`
payload row maps to one installed file whose actual bytes match its recorded digest
and size. The installed `RECORD` is separately hashed and compared as a row set. The
only allowed installed additions/rewrites are:

| Rule | Exact path/content/record rule |
| --- | --- |
| `UV_INSTALLER` | `<dist-info>/INSTALLER`, required; bytes exactly `b"uv"` (2 bytes, no newline); installed `RECORD` has URL-safe unpadded SHA-256 and size 2 |
| `UV_REQUESTED` | `<dist-info>/REQUESTED`, required for this root locked/all-groups environment; bytes exactly empty; installed `RECORD` has the empty SHA-256 and size 0 |
| `UV_REWRITTEN_RECORD` | `<dist-info>/RECORD`; its own row is empty hash/size; row set equals mapped extracted rows plus exactly the two generated rows above |
| `CPYTHON_BYTECODE_CACHE_DENIED` | optional actual `**/__pycache__/<source>.<sys.implementation.cache_tag>[.opt-N].pyc`; must map to one RECORD-owned `.py`, have current magic, and is hashed/sized/mode-recorded, but is not executable or readable by rebuild |

No other generated metadata or installed extra is allowed. In particular,
`direct_url.json`, generated `.pth`, generated entry points, signatures, alternate
installer/requested content, extra dist-info files, and unowned native/data files
fail. A file such as `entry_points.txt` is allowed only when it already exists as a
verified extracted-tree `RECORD` member.

The installed environment currently contains the exact `INSTALLER`/`REQUESTED`
pattern above and generated in-place bytecode (for example, observed pydantic has 66
`.pyc` files). Admission therefore records those actual bytes instead of pretending
the installed tree equals the wheel tree byte-for-byte.

Rebuild is launched with an exact empty alternate `PYTHONPYCACHEPREFIX` from Section
8.4, `PYTHONDONTWRITEBYTECODE=1`, and `python -B`. The guarded reader denies every
in-place `.pyc`; audit tests prove none is opened and the alternate prefix remains
empty. Thus bytecode caches are truthfully enumerated but cannot affect execution.

Every installed record includes environment-relative path, SHA-256, size, mode,
source extracted member or exact generated rule, owner, and executable/read policy.
Duplicate ownership, path escape, symlink, unexpected hardlink alias, or an import
from an unadmitted distribution fails. Per-distribution digests bind lock declaration,
cache association/tree, installed metadata/RECORD, installed files, and generated
rules. Their ordered digest is `installed_runtime_digest`.

### 9.4 Interpreter, stdlib, and resources

The resolved `sys.executable`, loaded `libpython` when present, selector, and all
regular files under resolved stdlib/platstdlib are hashed with size/mode. Only
site/dist-packages, `__pycache__`, and `.pyc` are excluded from stdlib enumeration.
Pure Python, lib-dynload, extensions, encodings, and resource data are included.
Symlinks, aliases, escape, missing files, or drift fail. This retains the R5
interpreter/libpython/stdlib closure that passed review.

The exact local resource list is 17 paths: the four authority YAML files; the
decision/review/acceptance artifacts for identity, field, possession, and supported
features (12 files); and the source profile. Each has repo-relative path, digest,
size, mode, purpose, parser/schema version, and authority link. Source, identity,
outputs, uv cache, installed runtime, and stdlib use their own guarded categories and
are not generic resources.

Guarded reads classify exactly: repository code; lock inputs; operational uv selector
link/sidecars/extracted tree during admission; admitted installed/stdlib bytes; exact
resource; exact strict source; exact accepted identity bundle references; exact
manifest-referenced parent product; exact staging/final destination; or exact receipt
destination. All other reads are denied.

The code manifest uses algorithm
`w04-code-environment-admission-v3` and contains source closure, lock declarations,
selector, extracted cache materializations, installed distributions, interpreter,
stdlib, resources, component digests, and:

```text
environment_digest = SHA256(canonical_json({
  selector,
  lock_inputs_digest,
  selected_lock_declarations_digest,
  extracted_runtime_digest,
  installed_runtime_digest,
  interpreter_digest,
  stdlib_digest,
  local_resource_digest
}))
```

It has no own ID/path, clock, actor, Git state, run ID, or output digest.

```text
code_manifest_sha256 = SHA256(canonical_manifest_bytes)
code_manifest_id = UUIDv5(
  w04_dependency_namespace,
  "post_integration_code_environment_manifest:" + code_manifest_sha256)
path = data/manifests/wyscout/v5/code/
       <code_manifest_sha256>.code-manifest.json
```

Independent review reproduces the entire algorithm. Negative tests cover lock
selection/tag drift, cache link/target/tree/RECORD drift, false wheel-ZIP claims,
installed payload/RECORD/generated-metadata drift, readable pyc, extra import,
interpreter/libpython/stdlib/resource drift, and early build-ID formation.

## 10. Build identity and deterministic serialization

Canonical build input is version `w04-wyscout-build-id-v4` and contains tenant;
manifest; identity bundle/queue/ruleset/accepted corrections; field, possession, and
supported-feature registry decision/review/acceptance IDs/digests; all product schema
versions; neutral context; window/cutoff; code manifest; source/lock-declaration/
extracted/installed/interpreter/stdlib/resource/environment digests.

`build_id=SHA256(canonical_json(all fields))`. Missing acceptance, placeholder,
unverified extracted/installed state, or pre-closure call makes the function
unavailable. Branch/tag/commit, original absent archive bytes, output root, run ID,
and clocks do not participate.

Parquet remains version 2.6, one `part-00000.parquet` per logical partition, row group
65,536, zstd level 9, data page 2.0, no dictionary or byte-stream split, statistics
on, page index off, timestamps in microseconds without truncation, and stored schema.
Rows use canonical UUID/UTC/Decimal/null/list forms and primary-key order. Semantic
digests cover schema, length-prefixed rows, and ordered parents; physical digests
cover exact bytes.

## 11. Quality, health, card, and `G-W04`

Quality retains the exact source counts; five partition equalities; unique matches
and event IDs; exactly two teams per match; zero match/team conflicts; 226,038 zero
actors; lineup/bench/substitution counts; 23/8 unresolved references; 1H/2H and scale
constraints; coordinate anomalies; accepted authorities; exact five-dependency
clocks/order; result-independent facts; neutral Gold; zero minute/per-90 emission;
six coverage equations; verified runtime/resources; sole writers; quarantine; and
two-root equality.

P2.8 outputs remain:

```text
reports/phase-gates/W04/data-health.json
reports/phase-gates/W04/data-health.md
```

JSON is controlling machine evidence. It includes coverage, clocks, identity
backlog/corrections/supersession, rejected records/fields, unmapped fields,
reconciliation, temporal violations, cache/archive-verification truth, installed
generated rules, path ownership, environment/resource checks, and two-root equality.

P2.9 remains separate:

```text
docs/dataset-cards/w04-wyscout-transformed-v1.md
reports/reviews/W04/wyscout-transformed-dataset-card-independent-review-R1.md
```

The card binds build/layer/health digests and states intended/excluded use,
populations, coverage, backlog/correction policy, transformations, supported and
suppressed features, time/minute limitations, coordinate/semantic biases, inherited
rights/attribution, and reproduction policy. Independent review cannot edit it.

`G-W04` passes only when one manifested input deterministically rebuilds Gold from raw
evidence; all identity, reconciliation, temporal, rights, guarded-root, executable,
resource, quarantine, manifest, card, independent review, and exact-path gates pass.
Identity readiness means all unique valid master rows resolve, resolvable references
resolve once, and every unresolvable reference is exactly queued/excluded—not guessed.

Master/gate outputs remain:

```text
reports/verification/W04/wyscout-raw-to-gold-R1-master-verification.md
reports/verification/W04/verification-report.md
reports/verification/W04/clean-tree-report.md
reports/verification/W04/phase-verifier-candidate.json
reports/reviews/W04/master-review.md
reports/phase-gates/W04/acceptance-report.md
reports/phase-gates/W04/gate-report.json
```

`gate-report.json` is controlling machine evidence. No report is emitted as accepted
until every required independent recommendation is `PASS`.

## 12. Ownership-complete serial graph

Only Silver producers with disjoint path families may overlap. All authorities,
shared contracts, admission, manifests, rebuild, reviews, gate, and ledger are serial.

| # | Exact owner/packet | Sole output responsibility | Coverage/dependency |
| ---: | --- | --- | --- |
| 1 | accepted source/master | existing source card/profile | W04.1/P2.1 |
| 2–4 | field decision/review/accept packets | four exact Section 3.1 artifacts/tests/returns | before Bronze |
| 5–7 | possession decision/review/accept packets | four exact Section 3.2 artifacts/tests/returns | before possession |
| 8–10 | identity decision/review/accept packets | four exact Section 5.1 artifacts/tests/returns | W04.3/P2.3 |
| 11 | `W04-DATA-CONTRACTS-01-R1` / master | W04 contract/tests/return; existing evidence unchanged | W04.2–W04.6 |
| 12 | manifest bridge/source owner | bridge/test/exact source manifest/return | sole source-manifest writer |
| 13 | Bronze owner | `bronze.py`, test, exact Bronze raw/quarantine/staging families and Bronze manifest | W04.2/W04.4/P2.2 |
| 14 | identity runtime owner | identity module/test and exact Section 5 generated families | W04.3/P2.3 |
| 14C | correction master/reviewer/master | exact decision/review/accept artifacts/returns | conditional authority only |
| 14D | identity runtime owner | one normalized correction; route-specific queue behavior; new bundle | only after accepted 14C |
| 15A | entity owner | competition/team/player/match Silver families | W04.4/P2.4 |
| 15B | action owner | action Silver family | W04.4/P2.4 |
| 15C | lineup owner | lineup-stint Silver family | W04.4/P2.4 |
| 16 | possession owner | possession Silver family | after action |
| 17 | player-match owner | player-match-fact Silver family | after all Silver inputs |
| 18 | Silver manifest owner | exact Silver manifest only | after all Silver serializers |
| 19 | `W04-FEATURE-REGISTRY-DECISION-01-R1` / master | feature decision, registry, contract test, return | P2.6 |
| 19R | `W04-FEATURE-REGISTRY-REVIEW-01-R1` / independent | exact feature independent review/return | candidate read-only |
| 19A | `W04-FEATURE-REGISTRY-ACCEPT-01-R1` / master | exact feature acceptance/return | Gold blocked until accepted |
| 20 | Gold/temporal owner | Gold module/temporal module/tests, exact Gold/staging/manifest/boundary families | W04.5/P2.5/P2.7 |
| 21 | quality owner | quality module/tests | W04.6/P2.8 |
| 22 | admission implementer/master | admission module/script/tests | offline algorithm only |
| 23 | rebuild entrypoint/master | rebuild module/script/integration test; invocation receipt only | calls sole writers |
| 24 | shared integration/master | named shared exports only | serial |
| 25 | code-manifest admit/master | exact code manifest and admission report/return | after code freeze |
| 26 | code-manifest independent reviewer | exact independent review/return | reproduce bytes/digests |
| 27 | two-root invocation/master | two run families and rebuild evidence report/return | no broad data write grant |
| 28 | health owner | exact JSON/Markdown health/return | P2.8 |
| 29 | card author/master | exact transformed card/return | P2.9 |
| 30 | card independent reviewer | exact card review/return | W04.7 |
| 31 | rebuild independent reviewer | leakage test, exact rebuild review/return | W04.7 |
| 32 | master verifier | raw-to-Gold verification, verification report, pre-ledger candidate evidence | W04.7 |
| 33 | master gate | master review, acceptance report, gate-report | full `G-W04` |
| 34 | master local Git authority | acceptance integration commit and annotated accepted tag | only after full gate |
| 35 | master ledger authority | registry checkpoint mutation plus clean-tree proof in separate local commit | after accepted tag |

Exact implementation packet IDs expand as in R5 for field, possession, identity,
Silver, quality, admission, rebuild, card, and review tasks. `return` always means
`reports/reviews/W04/returns/<packet-id>.md`. No directory shorthand grants a writer
another product family. Row 27 invokes serializers and owns run receipts/evidence
only; it does not own `data/working/wyscout/v5/**`.

This graph covers W04.1–W04.7 and P2.1–P2.9: rights/source, Bronze, four-kind identity,
all Silver products, temporal state, supported features, neutral Gold, health, card,
independent rebuild, and `G-W04`.

## 13. Controlling two-local-commit acceptance ledger

The order is exact and follows the implementation workflow:

1. Master completes every implementation/readback/independent review and writes the
   candidate verification, machine gate report, and acceptance rendering. The full
   shared/risk-specific `G-W04` gate runs first. Registry remains pre-checkpoint.
2. With the gate passing, master creates local acceptance integration commit
   `C_accept` with exact message
   `phase(w04): accept governed data spine`.
3. Master creates annotated local tag `checkpoint/w04-accepted` on exactly
   `C_accept`. The tag is never moved to the later ledger commit.
4. Master resolves `C_accept` from the tag and writes the registry mutation:
   W04 state/checkpoint fields, exact `C_accept` SHA, exact tag, exact approved
   message, gate-report path/digest, acceptance-report path/digest, and evidence
   paths. The registry contains no ledger commit SHA.
5. Master writes `reports/verification/W04/clean-tree-report.md` as a predicate
   certificate. It contains `C_accept` SHA/tag/message, the exact two ledger paths
   (`orchestration/phase_registry.yaml` and this clean-tree report), the commands and
   required results proving no unstaged/untracked paths, empty remote list, active
   guard, index/worktree equality, and the rule that the ledger commit is created
   only if those predicates pass. It contains no own digest, tree hash, or future
   ledger commit SHA.
6. After staging exactly those two paths, master verifies the predicates and creates
   one separate local commit with exact message
   `orchestration(w04): record accepted checkpoint ledger`.
7. Master runs final read-only clean-tree, remote, guard, registry, and local-only
   verification. Empty output is required. These checks do not rewrite an artifact.
   The committed predicate certificate plus Git's staged-tree-to-commit transition
   avoids a self-referential hash while the final command reproduces cleanliness.

Thus the accepted tag names the accepted product/evidence integration, while `HEAD`
after closure is the later ledger commit. No registry-before-checkpoint cycle,
self-hash, tag movement, third cleanup commit, or history rewrite is allowed. A
failed post-ledger check stops closure and is not waived.

## 14. Required positive and negative tests

In addition to retained source, football, coverage, minute, rights, temporal,
environment, card, and gate tests, R6 requires:

- identity paths resolve only under
  `data/working/wyscout/v5/identity/{review-queues,bundles,corrections}`;
- all classification-method/state/match-method combinations in Section 5.2, with
  exact rejection of every other combination and valid resolved-only projection;
- queue resolved/rejected corrections and direct resolved-to-resolved/rejected
  supersessions; direct route creates no item/snapshot/history;
- correction clocks and later bundle availability change dependency/build identity;
- feature decision/review/acceptance digests/clocks, exact five-dependency cardinality
  and order, and cutoff before/equal decision/review/acceptance;
- exact Bronze raw/rejected-record/rejected-field paths; every Silver family; Gold,
  staging, receipt, and manifest formulas; two-root and pairwise no-overlap;
- unknown record/field quarantine and manifest reconciliation;
- rebuild entrypoint cannot serialize a product or layer manifest;
- uv selector symlink-to-extracted-tree association, strict extracted RECORD, lock
  metadata versus unverified original archive truth, and sidecars rejected as wheel;
- installed mapped payload, exact `INSTALLER=b"uv"`, empty `REQUESTED`, rewritten
  RECORD, denied/enumerated pyc, forbidden other extras, and alternate empty pycache;
- integration commit/tag then registry/clean certificate ledger sequence, exact
  messages/tag, no self-referential fields, and final clean read-only verification.

## 15. Closure and stop rules

R6 retains closed findings for the completion-only source seam, exact 18 rows and
strict source coverage, restricted rights/attribution, field and possession
authorities, identity valid/availability clocks, period-relative temporal ordering,
neutral Gold grain, minutes/per-90 suppression, six coverage equations, player-match
fact, clock-free proof/truthful adapter, interpreter/libpython/stdlib, health/card,
independent reviews, two-root rebuild, and machine `G-W04`.

The seven R5 P1s are closed by Sections 5.1 (approved identity root), 9 (actual
extracted/installed bytes), 3.3/6 (feature authority and temporal dependency), 5.2
(exact classification methods), 5.4 (two correction routes), 8/12 (exact paths and
sole writers), and 13 (controlling two-commit ledger).

Stop rather than improvise if any path/digest/count changes; an authority or truthful
clock is missing; a queue/direct route cannot satisfy its discriminator; an unknown
would be guessed; a source/excluded path would be read; action UTC/minutes would be
fabricated; an original archive hash would be claimed without archive bytes; cache,
installed, interpreter, stdlib, code, or resource closure fails; a writer overlaps;
or any dependency, migration, provider, network, rights, architecture, local-only,
ignore, remote, or deployment change is needed.

Implementation begins only after master and another independent reviewer accept R6.
This document does not approve itself.

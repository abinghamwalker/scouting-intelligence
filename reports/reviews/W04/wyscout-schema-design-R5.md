# W04 Wyscout v5 canonical schema and deterministic rebuild design — R5

Status: **implementation design for master and independent review; not self-approved**

This document replaces R4 in full. It is the standalone design for the local-only W04
Wyscout Figshare v5 Bronze-to-Gold proof. It retains the accepted source seam,
period-relative temporal model, project-defined semantic authority, exact 18-row
source manifest, strict source coverage, neutral Gold grain, minute suppression, Gold
coverage equations, and required player-match fact. It additionally makes the
identity, runtime-environment, resource, phase-artifact, and acceptance lifecycles
complete and executable.

The binding measured evidence is:

- `data/source/wyscout/v5/completion-manifest.json`, 6,803 bytes, SHA-256
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- `reports/phase-gates/W04/source-schema-profile.md`, SHA-256
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- upstream availability `2020-01-28T14:24:27Z` and actual local acquisition
  `2026-07-29T15:51:08.598589Z`;
- completion classification `wyscout_figshare_v5_cc_by_4`, licence `CC-BY-4.0`,
  restricted project control, attribution required;
- 7 direct objects, 10 separately durable admitted members, 4 directory-only
  exclusions, 7 competitions, 142 teams, 3,603 players, 1,826 matches, and
  3,071,395 event records; and
- the accepted adapter in `src/scouting/sources/wyscout.py`, which writes only
  `objects/<name>`, `archive-members/<name>`, and `completion-manifest.json`.

No provider access, excluded-payload read, network, runtime label guessing,
container, hosted artifact, dependency change, migration, or export is authorised.

## 1. Claim boundary and global invariants

The permitted claim is a frozen historical engineering and player-evidence proof. It
does not establish current players, live coverage, provider continuity, women or
youth coverage, exact minutes, commercial-product equivalence, recruitment
relevance, or prospective benefit.

The following are normative:

1. Only exact completion-declared `object_path` and `member_path` values are readable.
2. `matches.zip` and `events.zip` are hashed evidence but never opened downstream.
   The four excluded directories have no admitted payload path and are never read.
3. Provider record `id` identifies an event record; `eventId` identifies taxonomy.
   Names are display evidence only, never identity or semantic matching keys.
4. Source JSON numbers are parsed as `Decimal`. Event time is period-relative. No
   second-half UTC, half-time duration, terminal, or continuous clock is invented.
5. Field and possession semantics are project-defined only after decision,
   independent review, and master acceptance. Unknowns remain `UNMAPPED`.
6. Identity source validity and project knowability are different clocks. No human
   decision, review, acceptance, or correction is backdated to source release.
7. Existing `DependencyKind` values are unchanged. Row lineage is not an invented
   dependency kind.
8. Bronze, Silver, and Gold semantic bytes contain no run ID, host path, run clock,
   elapsed duration, operational trace, or generation clock.
9. Existing `TemporalEvidence` and `RetrievalResult` contracts are unchanged. A real
   sampled generation clock is introduced only at the serving boundary.
10. The implementation identity closes over repository code, the exact selected lock
    artifacts, installed runtime bytes, interpreter and standard library bytes, and
    an exact local-resource allowlist before `build_id` is formed.
11. Rights, identity, cutoff, authority, environment, resource, lineage, partition,
    reconciliation, and sole-writer failures are fail-closed.
12. Phase acceptance, registry mutation, and checkpoint creation are master-only and
    occur only after independent review and a passing `G-W04`.

## 2. Exact completion-declared source seam

The source root is exactly `data/source/wyscout/v5`. The completion document is read
first and its digest checked. Normalised NFC POSIX-relative paths must remain below
the resolved root, be regular non-symlink files, and match declared bytes.

Readable direct objects are `objects/competitions.json`, `objects/teams.json`,
`objects/players.json`, `objects/eventid2name.csv`, and
`objects/tags2name.csv`. The ten readable archive members are the five
`archive-members/matches_<country>.json` and five
`archive-members/events_<country>.json` entries in Section 5. ZIP objects are hashed
only. For each country, distinct event `matchId` equals match `wyId`: England 380,
France 380, Germany 306, Italy 380, Spain 380.

Any path not present in the exact strict source manifest is denied. Directory scans,
fallback archive extraction, obsolete inferred layouts, symlinks, path aliases, and
case-normalised substitutes are forbidden.

## 3. Normative local semantic authorities

The profile establishes shape, counts, key membership, and local mapping-file bytes.
It does not establish field meaning or possession meaning. Both semantic routes bind
the completion digest, profile digest, event-map digest
`ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`,
and tag-map digest
`e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922`.

### 3.1 Field decision, review, and acceptance

The exact artifacts are:

```text
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json
configs/schema/wyscout-v5-field-registry-v1.yaml
reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json
```

The master decision contains `schema_version`, fixed decision/source IDs,
`authority_class=project_defined_reviewed_semantics`, `decided_by`, truthful
`decided_at`, all bound input digests, and an exhaustive ordered decision for every
measured `(record_kind,json_path)`. Each decision is `TRANSFORM`,
`PRESERVE_UNMAPPED`, or `FORBIDDEN`, with measured type set, nullable canonical
field, source-support class, and rationale. Policies are
`unknown_field_policy=UNMAPPED`, `unknown_record_kind_policy=REJECT_PARTITION`,
`runtime_label_matching=forbidden`, and
`provider_native_semantic_claim=false`.

The six literal string `"null"` substitution containers receive explicit decisions.
Mixed IDs, string `subEventId`, coordinates, and decimal event time retain measured
source types unless the accepted registry authorises an exact transform.

The independent reviewer records the exact decision and registry digests without
editing either. After a `PASS`, the master acceptance records decision/artifact IDs
and digests, independent-review path/digest, `accepted_by`, truthful `accepted_at`,
`status=accepted`, and nullable `supersedes`. Acceptance cannot predate decision or
review. The registry digest excludes acceptance bytes, avoiding a cycle.

### 3.2 Possession decision, review, and acceptance

After field acceptance, the analogous artifacts are:

```text
reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json
configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml
reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json
```

Each mapping predicate uses only exact numeric `event_id`, nullable numeric
`subevent_id`, sorted required tag IDs, and sorted forbidden tag IDs. A decision is
`CONTROL`, `CONTESTED`, `DEAD_BALL`, `RESTART`, `NON_CONTROL_ADMIN`, or `UNMAPPED`.
A mapped row declares control-team source, open/close behavior, dead-ball and
contested attachment, rationale, and accountable actor. Global policies are:

```text
unknown_combination_policy: UNMAPPED
unknown_name_matching: forbidden
runtime_label_matching: forbidden
provider_native_possession_claim: false
period_boundary_policy: close
simultaneous_cross_team_policy: uncertain_boundary
```

Decision, review, and acceptance clocks are truthful and ordered. The taxonomy binds
the accepted field authority. Parsed YAML is canonicalised as JSON with sorted object
keys and schema-declared array order; no self-digest appears.

## 4. Source-manifest bridge and identity-independent IDs

A serial bridge converts acquisition evidence into existing
`SourceSnapshotManifest`. `TenantContext` is explicit; `tenant_id` has no default and
nullable `club_id` is fixed.

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

The manifest has `schema_version=1`, provider `Wyscout`,
`provider_schema_version="figshare-v5+completion-v1+bridge-v1"`, exact acquisition
and source-availability clocks, explicit tenant and trace, restricted classification,
derived/internal-review allowed, export false, attribution required.

Canonical entity identity uses numeric source keys only:

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
kind_namespace = UUIDv5(source_namespace, "<competition|team|player|match|action>")
canonical_id =
  UUIDv5(kind_namespace, "figshare-v5:<canonical-decimal-source-id>")
```

Zero is not a player identity. Names, current teams, and external knowledge cannot
repair a missing, malformed, duplicate, conflicting, or absent master-table key.

## 5. Exactly 18 strict `SourceFileDigest` rows and `DataCoverage`

The `files` tuple is exactly this order; no row can be added, removed, or reordered.

| # | `object_path` | `size_bytes` | `row_count` | `sha256` |
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

The exact existing source coverage contract is:

```text
dimensions = (
  CoverageDimension(name="source_object_integrity",
    coverage=1.0, observed_count=7, expected_count=7),
  CoverageDimension(name="admitted_member_integrity",
    coverage=1.0, observed_count=10, expected_count=10),
  CoverageDimension(name="match_partition_presence",
    coverage=1.0, observed_count=5, expected_count=5),
  CoverageDimension(name="event_partition_presence",
    coverage=1.0, observed_count=5, expected_count=5),
  CoverageDimension(name="partition_match_id_alignment",
    coverage=1.0, observed_count=5, expected_count=5),
  CoverageDimension(name="scope_exclusion_directory_only",
    coverage=1.0, observed_count=4, expected_count=4),
)
DataCoverage(overall=1.0, dimensions=dimensions, missing_dimensions=())
```

All coverage values are strict Python `float` `1.0`; counts are strict non-negative
`int`. JSON serialises the tuples as arrays and `missing_dimensions` as `[]`.
Admission recomputes each ratio, rejects zero expected counts, and requires
`overall == min(dimensions.coverage) == 1.0`. Gold numerator/denominator fields do
not belong to this contract.

The sole strict artifact is canonical JSON at:

```text
data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json
```

The artifact SHA-256 is derived after serialisation and is absent from its identity
input.

## 6. Complete identity authority and W04.3 lifecycle

Identity is a reviewed project assertion even when its mapping rule is deterministic.
The source key can be historically valid at source release while the project mapping
is not knowable until acceptance. R5 therefore does not copy source availability into
accepted identity availability.

### 6.1 Ruleset decision, independent review, acceptance

The exact authority route is:

```text
reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json
configs/schema/wyscout-v5-identity-ruleset-v1.yaml
reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json
```

The master decision binds tenant, strict source manifest ID/digest, completion/profile
digests, all four admitted master-table row groups, the UUID namespaces/rules, exact
crosswalk schema, confidence/state rules, queue policy, and correction policy. It has
truthful `decided_by` and `decided_at`. The independent reviewer reproduces mappings,
counts, row digests, and ambiguity cases, recording truthful `reviewed_at` without
editing the candidate. The master accepts only a `PASS`, with `accepted_by` and
`accepted_at >= max(decided_at, reviewed_at)`.

The ruleset is project-defined; no name matching, fuzzy matching, current-team
matching, provider call, or external identity is allowed. Missing authority or
clock-order failure blocks all identity products.

### 6.2 Strict four-kind crosswalk row

Every competition, team, player, and match master row, and every referenced key,
passes through one strict `W04IdentityCrosswalkRow`:

```text
schema_version: Literal[1]
crosswalk_schema_version: Literal["w04-wyscout-crosswalk-v1"]
tenant_context: existing strict TenantContext
entity_kind: COMPETITION | TEAM | PLAYER | MATCH
source_identity: existing strict SourceIdentity
source_manifest_id: strict UUID
source_manifest_sha256: lowercase SHA-256
source_row_refs: non-empty sorted tuple[W04SourceRowRef, ...]
canonical_id: strict UUID | null
version: strict positive int
method: existing IdentityMatchMethod
confidence: strict finite float, exactly 0.0 or 1.0
state: RESOLVED | REVIEW_REQUIRED | REJECTED | SUPERSEDED
valid_from: timezone-aware UTC
valid_to: timezone-aware UTC | null
available_at: timezone-aware UTC
reviewed_by: ActorId | null
supersedes_evidence_digest: lowercase SHA-256 | null
identity_ruleset_id: fixed string
identity_ruleset_sha256: lowercase SHA-256
identity_decision_sha256: lowercase SHA-256
identity_review_sha256: lowercase SHA-256
identity_acceptance_sha256: lowercase SHA-256
reason_codes: sorted unique non-empty tuple[str, ...]
evidence_digest: lowercase SHA-256
crosswalk_row_id: strict UUID
trace_id: strict UUID
```

`source_identity` is the existing strict three-field object: `provider="Wyscout"`
and `source_version="figshare-v5"`. For a syntactically valid source key,
`source_id="<competition|team|player|match>:<canonical-decimal-source-id>"`. For a
malformed value it is
`"<kind>:invalid:<raw-field-canonical-json-sha256>"`; such a value can only be
`REVIEW_REQUIRED` and never feeds the UUID formula. Prefixing the kind prevents the
existing projection from losing kind identity; the same kind appears in the separate
strict `entity_kind` field and the two must agree.
The evidence digest is SHA-256 of canonical JSON of all semantic fields through
`reason_codes`, excluding `evidence_digest`, `crosswalk_row_id`, and `trace_id`.
Then:

```text
crosswalk_row_id = UUIDv5(
  identity_crosswalk_namespace,
  tenant_id + ":" + entity_kind + ":" + source_identity.canonical_json +
  ":" + version + ":" + evidence_digest)
trace_id = UUIDv5(crosswalk_row_id, "w04-identity-crosswalk-trace-v1")
```

Only a current `RESOLVED` row projects into existing strict `IdentityEvidence`,
because that contract requires a non-null canonical UUID. The projection copies
exactly `schema_version`, tenant, version, trace, source identity, canonical ID,
method, confidence, evidence digest, availability, valid interval, reviewer, and
superseded digest. `REVIEW_REQUIRED`, `REJECTED`, and logically `SUPERSEDED` rows
remain crosswalk/queue evidence and must never be coerced into `IdentityEvidence`.
A resolved projection that fails the existing validator is rejected.

Every initial crosswalk row has `version=1`, copies the exact immutable
`TenantContext` from the strict source manifest, and uses the deterministic trace
rule above. A later row for the same `(tenant,entity_kind,source_identity)` has
version exactly one greater than the prior current row and names its evidence digest;
gaps, forks, or tenant/trace substitution fail.

Initial v1 classification is exhaustive:

- a strict positive integer that occurs exactly once in its admitted same-kind master
  table and satisfies referential constraints is `RESOLVED`, method
  `deterministic`, confidence `1.0`;
- a non-zero key absent from the master, malformed key, duplicate master key,
  cross-kind collision, team/match conflict, or conflicting mapping is
  `REVIEW_REQUIRED`, confidence `0.0`, canonical ID null, and queued;
- player key zero is `REJECTED`, confidence `0.0`, canonical ID null, with
  `provider_zero_actor`; it is counted separately and does not create a queue item;
- `SUPERSEDED` is an effective bundle-index state derived only from a later accepted
  row whose `supersedes_evidence_digest` names the prior digest; the immutable prior
  crosswalk/evidence row retains its original bytes and state.

Consumers accept only the current, non-superseded `RESOLVED` row at confidence
exactly `1.0`, with a valid interval covering the fact and accepted bundle
availability strictly before cutoff. There is no intermediate confidence band.

For v1, `valid_from` may truthfully be source release
`2020-01-28T14:24:27Z`: it describes the interval for which the numeric mapping is
asserted. Its `available_at` is the later identity-ruleset master `accepted_at`: it
describes when this project could use that reviewed assertion. The two clocks are
never substituted.

### 6.3 Durable review queue

Unresolved cases are preserved in content-addressed immutable queue snapshots:

```text
data/identity/wyscout/v5/review-queues/
  <queue_sha256>.identity-review-queue.json
```

The canonical bytes exclude their own digest and contain:

```text
schema_version, queue_schema_version, tenant_context,
source_manifest_id, source_manifest_sha256,
identity_ruleset_id, identity_ruleset_sha256, identity_acceptance_sha256,
prior_queue_sha256 | null,
items: sorted tuple[
  queue_item_id, entity_kind, source_identity, reason_family,
  reason_codes, source_row_refs, first_seen_source_valid_at,
  available_at, status, disposition_id | null
],
counts_by_kind_and_status
```

`queue_item_id` is UUIDv5 over tenant, kind, canonical source identity, source
manifest ID, and reason family. Repeated references aggregate into sorted unique row
refs rather than duplicate items. Status is `OPEN`, `IN_REVIEW`,
`RESOLVED_BY_CORRECTION`, or `REJECTED_BY_CORRECTION`. Every transition creates a
new snapshot linked by `prior_queue_sha256`; no queue is edited in place. Counts must
exactly reconcile to items. Unknown status, missing item, duplicate dedupe key, or a
resolved disposition without an accepted correction fails closed.

An initial item's `first_seen_source_valid_at` may be source release, but its
`available_at` is the identity-ruleset acceptance when the reviewed project first
classified it unresolved. A status/disposition transition takes the later accepted
correction time. Queue snapshot availability is the maximum item/transition
availability and is included in the bundle watermark.

The measured 23 absent bench references and 8 absent substitution-in references
remain queued and excluded from accepted identity consumers unless new admissible
review evidence is separately supplied. A gate may require the backlog to reconcile
exactly; it must not claim the backlog is zero.

### 6.4 Bundle identity and evidence dependency

The immutable, canonical bundle is:

```text
data/identity/wyscout/v5/bundles/
  <identity_bundle_sha256>.identity-bundle.json
```

It excludes its own digest and derived ID. Its exact top-level fields are:

```text
schema_version: Literal[1]
bundle_schema_version: Literal["w04-wyscout-identity-bundle-v1"]
tenant_context: TenantContext
source_manifest_id: UUID
source_manifest_sha256: SHA-256
identity_ruleset_id: fixed string
identity_ruleset_sha256: SHA-256
identity_decision_id: fixed string
identity_decision_sha256: SHA-256
identity_decided_at: UTC
identity_review_path: fixed POSIX path
identity_review_sha256: SHA-256
identity_reviewed_at: UTC
identity_acceptance_id: fixed string
identity_acceptance_sha256: SHA-256
identity_accepted_at: UTC
current_rows: sorted tuple[W04IdentityCrosswalkRow, ...]
historical_row_digests: sorted tuple[SHA-256, ...]
supersession_edges: sorted tuple[prior SHA-256, new SHA-256]
counts_by_entity_kind_and_effective_state: canonical object
review_queue_sha256: SHA-256
accepted_corrections: sorted tuple[
  correction_id, correction_sha256, acceptance_sha256, accepted_at
]
prior_identity_bundle_id: UUID | null
prior_identity_bundle_sha256: SHA-256 | null
observed_at: UTC
available_at: UTC
```

Rows sort by `(entity_kind, source_identity.provider, source_identity.source_id,
source_identity.source_version, version, evidence_digest)`. The bundle contains
`current_rows`, immutable `historical_row_digests`, and sorted
`supersession_edges=(prior_evidence_digest,new_evidence_digest)`. It must include all
four kinds and all master rows, plus every referenced unresolved key, exactly once
in `current_rows`; every history/edge target must resolve exactly once. Its counts,
effective state index, queue, correction chain, and crosswalk bytes are recomputed
before hashing.

```text
identity_bundle_id =
  UUIDv5(w04_dependency_namespace,
    "identity_bundle:" + identity_bundle_sha256)
```

That exact `identity_bundle_id` is used in all three places: the bundle's external
identity, the `EvidenceDependency.dependency_id`, and the build-identity field. No
second derived dependency ID exists.

The identity dependency uses existing kind `identity_evidence`, bundle digest,
`observed_at=identity decision.decided_at`, and
`available_at=max(identity acceptance.accepted_at,
all included correction acceptance accepted_at)`. Thus the source facts can be valid
in 2020 while the reviewed bundle becomes knowable later. A cutoff equal to or before
either the decision or the bundle availability fails the existing strict-before
contract. A later accepted correction necessarily advances bundle availability and
changes bundle digest/ID, dependency lineage, watermark, and build ID.

### 6.5 Correction and supersession

Manual correction is allowed only through:

```text
reports/reviews/W04/identity-corrections/<correction_id>.decision.json
reports/reviews/W04/identity-corrections/<correction_id>.independent-review.md
reports/reviews/W04/identity-corrections/<correction_id>.acceptance.json
data/identity/wyscout/v5/corrections/
  <correction_id>.identity-correction.json
```

The master decision binds the prior row/bundle/queue digests, exact source refs, old
state/canonical ID, proposed new canonical ID or reviewed reject, non-empty reason,
`decided_by`, `decided_at`, proposed validity interval, and `new_version =
prior.version + 1`. The independent reviewer verifies evidence and records
`reviewed_by`, `reviewed_at`, and recommendation without editing the decision. The
master acceptance binds both digests with `accepted_by`, `accepted_at`, and status.

Only then is the normalized correction emitted. A resolved correction uses existing
method `reviewed`, confidence `1.0`, non-null reviewer, and
`supersedes_evidence_digest=prior.evidence_digest`; a reviewed reject has confidence
`0.0` and nullable canonical ID. The new crosswalk row has the accepted correction
availability. Valid intervals cannot overlap another current version and cannot
erase history. Earlier bytes remain immutable. The next queue snapshot records the
disposition and the next bundle makes the new row current, retains the prior digest
in history, and adds the supersession edge; the effective index reports the prior row
as `SUPERSEDED` without changing it. Name evidence alone is insufficient.

The normalized correction has exact fields:

```text
schema_version=1
correction_schema_version="w04-wyscout-identity-correction-v1"
correction_id
tenant_context
entity_kind
source_identity
prior_bundle_id, prior_bundle_sha256
prior_queue_sha256, queue_item_id
prior_evidence_digest, prior_version
new_crosswalk_row
reason
decision_path, decision_sha256, decided_by, decided_at
review_path, review_sha256, reviewed_by, reviewed_at, recommendation="PASS"
acceptance_path, acceptance_sha256, accepted_by, accepted_at, status="accepted"
```

Its canonical digest excludes no semantic field and is recorded in the bundle's
accepted-correction entry. Unknown fields, mismatched actors/clocks, non-consecutive
version, wrong prior digest, or non-`PASS` review fail.

Owners are unambiguous: master owns ruleset and correction decisions/acceptances;
independent reviewer owns only review reports; identity runtime owner owns crosswalk
projection, queue snapshot, correction normalization, and bundle regeneration; master
code admission later freezes the implementation bytes. No implementation packet can
accept its own identity assertion.

## 7. Dependency clocks, lineage, and cutoff

Existing kinds remain exactly:

```text
source_manifest, identity_evidence, feature_schema,
model_artifact, retrieval_index
```

W04 products use only the first three:

| Evidence | Kind | ID/digest | `observed_at` | `available_at` |
| --- | --- | --- | --- | --- |
| strict source manifest | `source_manifest` | exact manifest ID/artifact digest | source release | source release |
| accepted identity bundle | `identity_evidence` | exact bundle ID/digest | identity decision time | max identity/correction acceptance |
| field registry | `feature_schema` | deterministic registry dependency ID/registry digest | field decision time | field acceptance time |
| possession taxonomy | `feature_schema` | deterministic taxonomy dependency ID/taxonomy digest | possession decision time | possession acceptance time |
| match/action rows | not dependencies | row-lineage digests | match UTC / null action UTC | inherited through admitted source |

Field and taxonomy dependency IDs are UUIDv5 over type, artifact ID/digest, and
acceptance digest. Dependencies sort by `(kind_rank, dependency_id.bytes, digest,
observed_at, available_at)`, where ranks follow the enum order above. Duplicates by
kind/ID fail. `lineage_hash` is SHA-256 of canonical JSON containing the complete
ordered dependency fields. Every observed and available clock must be strictly
before `feature_cutoff_ts`; equality fails.

`W04SourceRowRef` contains source manifest ID, declared file path/digest, record kind,
ordinal, nullable source record ID, and canonical raw-record digest. Refs sort by
path, kind, ordinal, source ID, digest. Match/action rows are portions of the source
manifest, never new dependency kinds.

## 8. Event clock, ordering, and minute suppression

`silver_action` carries `period_code` (`1H`/`2H`), ordering-only rank 1/2,
`period_elapsed_seconds` as exact `decimal128(22,18)`,
`period_elapsed_source_scale` 0..18, `occurrence_precision=period_relative`, nullable
`period_start_utc=null`, nullable `event_observed_at=null`, and cutoff proof. Order is:

```text
(period_rank, period_elapsed_seconds, source_record_ordinal,
 source_event_record_id)
```

Gold selects complete matches by
`window_start_utc <= match_start_utc < window_end_utc`, with match start strictly
before cutoff and all dependencies strict-before cutoff. Partial-match or
action-instant cutoff is `unsupported_period_relative_occurrence`.

Substitution minute `m` represents nominal `[m,m+1)`. A starter begins at nominal
zero. For start interval `[s0,s1)` and end `[e0,e1)`:

```text
nominal_duration_lower = max(0, e0 - s1)
nominal_duration_upper = max(0, e1 - s0)
```

Open stints are right-censored. Event maxima, `Regular`, 90, and substitution maxima
cannot supply a terminal. Every elapsed-minute field is null, exact `minutes_played`
is absent, `per90_eligible=false`, and minute/per-90 outputs are
`suppressed_unsupported_denominator`.

## 9. Clock-free proof and truthful boundary adapter

`W04SemanticTemporalProof` is a strict W04 product contract with:

```text
schema_version=1
proof_version="w04-semantic-temporal-proof-v1"
snapshot_as_of_ts
available_at_watermark
valid_from_ts
feature_cutoff_ts
source_manifest_ids
feature_schema_hash
dependency_lineage_hash
dependency_lineage
occurrence_precision="match_start_and_period_relative_action"
partial_match_claim_supported=false
```

It contains no `generated_at_ts`. It accepts exactly one source dependency, exactly
one current accepted identity bundle, exactly the accepted field and possession
schema dependencies, valid canonical order/hash, and only allowed kinds. Every
dependency clock is strict-before cutoff. `available_at_watermark` equals maximum
dependency availability. `snapshot_as_of_ts` is maximum selected match start (or the
single match start at player-match grain). `valid_from_ts` equals the maximum of
snapshot and watermark. Feature schema hash binds field, possession,
action/lineup/possession/player-match/Gold schemas, neutral role context, and
supported-feature registry. Semantic JSON forbids run/generation/host/elapsed keys.

At serving time:

```text
adapt_w04_temporal_proof(
  proof: W04SemanticTemporalProof,
  generated_at_ts: UtcInstant
) -> TemporalEvidence
```

Production samples one real injected UTC clock and disallows caller-supplied fixture
time. The adapter revalidates the proof, requires generation at or after valid-from,
copies all unchanged fields one-to-one into existing `TemporalEvidence`, and adds
only generation. `RetrievalResult.generated_at` is the same sample and every
candidate lineage is exact. Boundary receipts are operational, not Gold or build-ID
inputs.

## 10. Bronze, Silver, player-match, and possession

Bronze grain is `(source_file_sha256, record_ordinal)`. It records declared
path/digest, record kind/ID, canonical raw digest, raw field paths, parser/registry,
admission state, source availability, rights, tenant, strict manifest, and row
lineage. Excluded members produce no row.

`silver_match` is one admitted deterministic match ID with competition/season, two
distinct match-bound teams, exact `dateutc`, preserved status/duration label, source
lineage, and reconciliation state.

`silver_action` is one unique provider event-record `id`, containing match/team,
nullable player, numeric event and nullable numeric subevent IDs, raw subevent type,
period fields, ordered positions, coordinate state, sorted tag IDs, nullable accepted
semantic class, `UNMAPPED` state, ordinal, lineage, and possession eligibility. The
7,821 string subevent IDs remain unmapped. Coordinates retain source order; x=-1 and
two y=101 anomalies are never clamped.

`silver_lineup_stint` is player × match × continuous provider-nominal interval,
carrying match-bound team/player, nominal bounds, boundary source, simultaneous
substitution group, terminal/derivation states, and exact refs. It has no elapsed
minute.

`silver_possession` is one contiguous project-taxonomy-resolved sequence in a match
period. It has UUIDv5 identity over match, accepted taxonomy, ruleset, period and
ordinal, plus team, first/last action, count, boundary and assignment state,
authority digests, proof/lineage, and
`provider_native_possession_claim=false`. Possessions never cross periods; unknown,
missing-team, contested, and equal-clock cross-team cases remain unresolved.

The required `silver_player_match_fact` key is:

```text
(tenant_id, source_manifest_id, match_id, player_id,
 player_match_fact_schema_version)
```

Team is a required match-bound attribute. The fact contains deterministic IDs,
competition/season, provider side, starting/bench/substitution/event flags,
result-independent counts, nullable possession counts, nominal stint states, null
elapsed fields, `per90_eligible=false`, six Gold coverage structures, applicability,
match start, source/authority availability, temporal proof, source-row lineage, and
all source/identity/semantic/code schema digests. It contains no score, winner,
points, outcome, or current-team field.

Candidate pairs are the union of resolved non-zero lineup, bench, substitution, and
event player references. Zero actors are separate. Facts reconcile one-to-one to
resolved evidence, correct match/team, and exact admitted counts; unresolved,
excluded, and conflicting identities yield no fact. The measured 50,522 distinct
non-zero event player-match pairs is an input count, not minutes evidence.

Possession construction after authority is deterministic: mapped control/restart
opens; same-team control continues; opposing control closes and opens; dead-ball and
contested behavior follows the exact accepted row; equal-clock cross-team is
uncertain; unknown/missing/unmapped is unassigned; period end closes. Its name is
`w04_project_defined_possession_v1`, never provider-native.

## 11. P2.6 supported feature registry, Gold coverage, and grain

The exact local registry
`configs/features/wyscout-v5-supported-count-features-v1.yaml` lists only count,
evidence, reconciliation, and coverage features derivable under this design. Every
entry binds input fact fields, aggregation, applicability, schema version, and
authority digests. Minutes, rates, per-90, continuous-time, action-value, provider
possession, outcome-dependent, role-inferred, and unsupported fields are explicitly
listed with `state=not_available` or `suppressed_unsupported_denominator`; absence
never means permission. W05 can add a new accepted registry version but cannot
mutate this one.

Gold coverage is separate from source `DataCoverage`. Each dimension has integer
numerator/denominator, exact decimal ratio, state, and sorted reasons:

| Dimension | Denominator | Numerator |
| --- | --- | --- |
| identity | all non-zero player-reference occurrences in contributing lineup, bench, substitution, event evidence | occurrences resolved once to row player and match team |
| lineup | selected player-match candidate facts | reconciled formation/stint state, including explicit event-only/no-lineup |
| action | admitted non-zero-player actions for row player | actions assigned once to correct player-match/team |
| coordinate | actions the accepted registry marks position-applicable | allowed cardinality/axes and numeric 0..100 |
| possession | actions accepted taxonomy marks possession-eligible | assigned to exactly one resolved possession |
| temporal | required dependencies plus selected match/action groups | dependencies strict-before cutoff, matches before cutoff, actions with snapshot proof |

For denominator > 0, coverage is exact numerator/denominator and numerator cannot
exceed denominator. With denominator zero, only coordinate/possession can be 1 with
authority-proven `not_applicable_zero_denominator`; otherwise value is 0 with
`missing_zero_denominator`. Overall is the minimum. Missing dimensions are sorted
partial/missing/authority-missing/failed dimensions.

Applicability is ordered: rights/manifest/authority/identity/partition/lineage/cutoff
failures suppress; mandatory zero denominator, missing dependency, N>D, or a
minute/per-90 request suppresses; hard gates with uncertainty are `research_only`;
all complete or authority-proven optional non-applicable dimensions with overall 1
is `w04_data_ready` only for registry-supported features.

Neutral role context is:

```text
role_context_namespace =
  UUIDv5(NAMESPACE_URL, "urn:scouting-intelligence:role-context")
role_context_version = "w04-neutral-role-context-v1"
role_context_id =
  UUIDv5(role_context_namespace, "w04:neutral-unscoped:version:1")
role_context_state = "neutral_unscoped"
```

The exact Gold key is:

```text
(tenant_id, player_id, competition_id, season_id,
 role_context_id, role_context_version,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, dependency_lineage_hash)
```

Gold contains supported counts, unresolved counts, six coverage values,
applicability, clock-free proof, source/identity/authority/schema lineage, and minute
suppression. W05 role-specific rows are separately versioned and cannot collide.

## 12. Closed post-integration code, executable, and resource manifest

Code/environment admission occurs serially after every W04 implementation, test,
rebuild entry point, authority, identity, and shared export is integrated and no
implementation packet may edit admitted paths. It runs wholly offline.

### 12.1 Repository code closure

Seeds are:

```text
scripts/rebuild_wyscout_v5.py
src/scouting/data_products/wyscout/**/*.py
src/scouting/identity/wyscout.py
src/scouting/contracts/wyscout_data.py
```

All regular `.py` files under the package glob are included. AST traversal recursively
includes every reachable repository-local module and package `__init__.py` under
`src/scouting`. Relative and `from` imports resolve exactly. Literal dynamic imports
resolve; non-literal dynamic imports, `__import__`, path-loaded executable code, and
runtime `sys.path` changes are forbidden. Each file records NFC repo-relative path,
exact byte digest/size, executable-bit boolean, local imports, and external roots.
Symlinks, hardlink aliases, generated Python, repository native extensions, device
files, `.pyc`, caches, or group/world-writable code fail.

Lock inputs are exact `.python-version`, `pyproject.toml`, and `uv.lock` bytes.
Design-time observed digests are respectively
`7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d`,
`963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b`,
and `1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca`.
Admission records current exact bytes; a change requires a new reviewed manifest.

### 12.2 Exact environment selector and selected lock artifacts

The environment selector records:

```text
sys_platform
platform_system
platform_release
platform_machine
python_implementation
python_full_version
python_cache_tag
SOABI
MULTIARCH
EXT_SUFFIX
byteorder
libc_name_and_version | null
ordered_packaging_compatible_tags
compatible_tags_sha256
```

The interpreter must satisfy `==3.12.*` and the project constraint. `uv lock --check`
and offline locked sync state must pass. For every external distribution owning an
import in the code closure, admission resolves exactly one marker branch and exactly
one compatible wheel entry from the selected package's `uv.lock` record. Selection
uses the ordered compatible-tag list and the lock's exact wheel filename/tags. An
sdist-only or ambiguous selection is rejected for the W04 imported runtime.

Each `selected_artifact` records normalized distribution name, locked version,
filename, locked URL basename, locked SHA-256, locked size, parsed wheel tags,
and selector digest. The local `uv cache dir` is searched read-only for that exact
content identity; exactly one distinct byte content must match filename/hash/size.
Its host path is operational and recorded only in the admission receipt, not in the
canonical manifest. The wheel bytes must exist before the build and be compatible;
no download or index lookup is allowed. The ordered artifact records form
`selected_artifacts_digest`.

Name/version equality alone is insufficient. Same-version wheels with different
bytes, platform, ABI, URL filename, size, or lock hash are different and fail
admission.

### 12.3 Installed distribution bytes and `RECORD`

For each selected wheel, admission identifies exactly one installed `.dist-info`
directory and requires metadata name/version to match. It parses the wheel's
`RECORD`, verifies the wheel archive member hashes/sizes, and compares its importable
payload and package data to installed files.

The installed manifest records every actual regular file owned by the distribution,
including `.py`, native libraries, typed metadata, templates/data, and the
`.dist-info` tree. Every hashed `RECORD` row must match installed hash/size. Unhashed
rows such as `RECORD` itself and permitted installer-generated metadata are hashed
from actual bytes and explicitly typed. Missing or extra owned files fail unless the
exact generated filename and rule is enumerated in the manifest schema. Paths outside
the environment, symlinks, hardlink aliases, ambiguous ownership, duplicate path
ownership, and distribution files outside the selected wheel payload fail.

Each file record contains environment-relative path, exact SHA-256/size, mode,
wheel-member path or explicit generated rule, and owner. Per-distribution digests
combine selected artifact, installed metadata, sorted installed file records, and
verified `RECORD`. Their ordered combination is `installed_runtime_digest`.
Runtime import monitoring rejects any third-party owner not in this admitted set.

### 12.4 Interpreter and standard library closure

Admission hashes the resolved `sys.executable` bytes, size, and mode; the loaded
`libpython` shared library when present; and the selector in Section 12.2. It records
their paths relative to the environment/system prefix, never host-absolute paths in
semantic products. These records form `interpreter_digest`.

It then enumerates all regular files under resolved `sysconfig` `stdlib` and
`platstdlib` roots, excluding only `site-packages`, `dist-packages`, `__pycache__`,
and `.pyc`. It includes pure Python, `lib-dynload`, extension modules, encodings,
zone/resource data, and other loadable standard-library resources. Each file records
normalised root-relative path, bytes, size, and mode. Overlapping roots deduplicate
only by identical resolved file and root-relative identity. Symlinks, hardlink
aliases, outside-root resolution, missing files, or changed enumeration fail. The
sorted records form `stdlib_digest`.

At rebuild start and immediately before output commit, interpreter, library, stdlib,
selected artifacts, installed distributions, imports, and closure are reverified.

### 12.5 Closed local non-Python resource allowlist

All behavior-affecting local non-Python reads are explicit records, never globs:

```text
configs/schema/wyscout-v5-identity-ruleset-v1.yaml
configs/schema/wyscout-v5-field-registry-v1.yaml
configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml
configs/features/wyscout-v5-supported-count-features-v1.yaml
reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json
reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json
reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json
reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json
reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json
reports/phase-gates/W04/source-schema-profile.md
```

Each resource record contains exact repo-relative path, SHA-256, size, mode, purpose,
parser/schema version, and authority link. The three independent-review files and
profile are exact resources because admission verifies the bytes referenced by each
acceptance/decision, not merely a stored digest string. Source payloads are admitted
by the strict source manifest; identity bundle, queue, and corrections are admitted
by the current bundle; selected wheels and stdlib data are admitted above. They are
not duplicated as generic resources.

The guarded reader classifies every open during admission/rebuild as exactly one of:
admitted repository code; an exact lock-named wheel candidate during admission;
admitted installed/stdlib file; exact allowlist resource; exact strict-source file;
current bundle/queue/correction file; or current output/receipt destination. A wheel
candidate is readable only after its expected lock hash/size/filename was selected
and is not executable. Any other read, directory fallback, wildcard expansion,
environment-derived configuration, locale file, user configuration, plugin,
credential, or newly added resource is denied. The sorted resource records form
`local_resource_digest`.

### 12.6 Non-circular manifest and environment digest

The content-addressed code manifest has these exact top-level fields:

```text
schema_version=1
manifest_kind="w04_post_integration_code_environment_manifest"
admission_algorithm="w04-code-environment-admission-v2"
entry_point="scripts/rebuild_wyscout_v5.py"
seed_spec
source_files
lock_inputs
environment_selector
selected_artifacts
installed_distributions
interpreter_files
stdlib_files
local_resources
source_closure_digest
lock_inputs_digest
selected_artifacts_digest
installed_runtime_digest
interpreter_digest
stdlib_digest
local_resource_digest
environment_digest
```

All collections use the orders defined above. Derived component digests are:

```text
source_closure_digest
lock_inputs_digest
selected_artifacts_digest
installed_runtime_digest
interpreter_digest
stdlib_digest
local_resource_digest
environment_digest = SHA256(canonical_json({
  selector,
  lock_inputs_digest,
  selected_artifacts_digest,
  installed_runtime_digest,
  interpreter_digest,
  stdlib_digest,
  local_resource_digest
}))
```

The document contains no own digest/ID/path, run ID, clock, actor, Git state, or
output digest.

```text
code_manifest_sha256 = SHA256(canonical_manifest_bytes)
code_manifest_id =
  UUIDv5(w04_dependency_namespace,
    "post_integration_code_environment_manifest:" + code_manifest_sha256)
path =
  data/manifests/wyscout/v5/code/
  <code_manifest_sha256>.code-manifest.json
```

Independent review reproduces all enumerations/digests from frozen bytes. Runtime
recomputes them before `build_id`. Tests must fail on same-version installed byte
tamper, `RECORD` tamper, wheel hash/size/tag drift, selector/ABI drift,
interpreter/libpython byte drift, stdlib drift, resource byte/mode drift, added or
unallowlisted local resource, extra imported distribution, and any attempt to form
`build_id` before all checks pass.

## 13. Build identity and deterministic outputs

Only after source, identity, authority, code, executable, environment, and resource
verification succeeds is canonical build input formed:

```text
build_identity_version="w04-wyscout-build-id-v3"
tenant_context
strict_manifest_id, strict_manifest_sha256
identity_bundle_id, identity_bundle_sha256
identity_queue_sha256
identity_ruleset_id, identity_ruleset_sha256, identity_acceptance_sha256
accepted_correction_ids_and_sha256
field_registry_id, field_registry_sha256, field_acceptance_sha256
possession_taxonomy_id, possession_taxonomy_sha256, possession_acceptance_sha256
supported_feature_registry_id, supported_feature_registry_sha256
action, lineup, possession, player_match_fact, gold schema/ruleset versions
neutral_role_context_id, neutral_role_context_version
window_definition, feature_cutoff_ts
code_manifest_id, code_manifest_sha256
source_closure_digest, lock_inputs_digest
selected_artifacts_digest, installed_runtime_digest
interpreter_digest, stdlib_digest, local_resource_digest, environment_digest
```

`build_id = SHA256(canonical_json(all fields above))`. No label, branch, tag, commit,
run/host clock, output root, random ID, or receipt participates. Missing component,
placeholder digest, or unverified state makes the function unavailable rather than
producing an ID.

Semantic files use canonical UUID/UTC/Decimal/null/list values, primary-key row order,
fixed partitions, and one `part-00000.parquet` per logical partition with Parquet
2.6, row group 65,536, zstd level 9, data page 2.0, no dictionary or byte-stream
split, statistics on, page index off, timestamp microseconds without truncation, and
stored schema. Semantic digest covers schema, length-prefixed canonical rows, and
ordered parent/authority/environment digests; physical digest covers bytes.

Two distinct empty-root builds with the one admitted manifest must have equal
relative paths, rows, schemas, lineage, semantic digests, and physical digests.
Operational receipts at
`runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json` contain truthful
run/trace clocks and may differ. Clock-free layer manifests are written last:

```text
data/manifests/wyscout/v5/bronze/<build_id>.manifest.json
data/manifests/wyscout/v5/silver/<build_id>.manifest.json
data/manifests/wyscout/v5/gold/<build_id>.manifest.json
```

## 14. Quality, data health, and `G-W04`

Quality requires exact 18-row source order and strict source coverage; 7 competitions,
142 teams, 3,603 players; 1,826 unique matches; 3,071,395 unique event IDs and zero
event-ID duplicates; five exact partition ID equalities; exactly two teams per match;
zero event match/team conflicts; zero non-zero event-player master misses and 226,038
zero actors accounted separately; 40,172 lineup, 28,715 bench, 10,423 substitution
rows; 23 bench and 8 substitution-in absent-master refs retained in the queue; only
1H/2H with scale <=18; 709 one-position and 3,070,686 two-position actions with all
three coordinate anomalies retained;
accepted identity/field/possession authorities; exact dependency clocks/order;
clock-free proof and truthful adapter; result-independent player-match facts; neutral
Gold context; zero elapsed-minute/per-90 emissions; exact coverage; verified closed
environment/resources; sole writers; and two-root equality.

P2.8 data-health outputs are both:

```text
reports/phase-gates/W04/data-health.json
reports/phase-gates/W04/data-health.md
```

The JSON is canonical machine evidence; Markdown is its human rendering. They report
the exact coverage matrix, freshness/source and acceptance clocks, identity backlog
by kind/reason/status, correction/supersession chain, reconciliation counts, rejected
and unmapped fields, temporal violations, environment/resource verification,
two-root equality, and all hard-gate results. Markdown cannot override JSON.

The transformed P2.9 card is separate from the pre-transform source card:

```text
docs/dataset-cards/w04-wyscout-transformed-v1.md
reports/reviews/W04/wyscout-transformed-dataset-card-independent-review-R1.md
```

It binds the accepted build, layer, and data-health digests and documents intended
and excluded uses, admitted populations, historical coverage, identity backlog and
correction policy, transformations, supported and suppressed features, period-time
and minute limitations, coordinate and semantic biases, inherited rights and
attribution, and update/version/reproduction policy. The independent review verifies
every claim against machine evidence and cannot edit the card.

`G-W04` passes only when one manifested input deterministically rebuilds Gold from
raw evidence; identity and reconciliation thresholds pass; there are zero
post-cutoff facts; rights and guarded roots pass; and all named runtime and review
artifacts exist with matching digests. Identity threshold means 100% of unique valid
master rows for competition/team/player/match are resolved, all resolvable
references resolve once, no duplicate/conflicting accepted mapping exists, and every
unresolvable reference is exactly represented in the queue and excluded. It does not
mean every malformed/absent reference was guessed.

Negative tests cover path escape/symlink, 17/19/reordered source rows, strict float
violations, conceptual source-coverage fields, unknown semantic keys, label guessing,
bad identity validity/availability clocks, cutoff equal to identity acceptance,
correction without independent acceptance, stale bundle/queue, fabricated action UTC,
dependency invention/order/hash errors, run clock in Gold, generation before
valid-from, repository code/mode drift, all executable/resource tamper cases in
Section 12.6, build ID before closure, and shared-manifest double writers.

Exact test ownership is:

| Test path | Required assertions |
| --- | --- |
| `tests/contracts/test_wyscout_identity_authority.py` | authority schema/digests; decision-review-acceptance order; four kinds; exact 1.0/0.0 state boundary |
| `tests/unit/test_wyscout_identity.py` | crosswalk/evidence digest/UUID; non-null-only `IdentityEvidence` projection; queue dedupe/transitions; bundle order/ID/dependency-ID equality; correction version/supersession |
| `tests/unit/test_wyscout_temporal_boundary.py` | source-valid identity with later availability; cutoff before/equal acceptance rejection; later correction advances watermark; truthful generation |
| `tests/unit/test_wyscout_code_admission.py` | selector/tag and wheel selection; wheel/installed `RECORD` equality; interpreter/stdlib/resource enumeration; every Section 12.6 tamper; no early build ID |
| `tests/integration/test_wyscout_rebuild.py` | guarded-read denial; exact source/identity paths; two empty roots; equal semantic/physical products |
| `tests/security/test_w04_temporal_leakage.py` | zero post-cutoff facts; no fabricated action UTC or operational product clock; identity acceptance equality rejection |

Master verification and gate outputs are exactly:

```text
reports/verification/W04/wyscout-raw-to-gold-R1-master-verification.md
reports/verification/W04/verification-report.md
reports/verification/W04/clean-tree-report.md
reports/verification/W04/phase-verifier-candidate.json
reports/reviews/W04/master-review.md
reports/phase-gates/W04/acceptance-report.md
reports/phase-gates/W04/gate-report.json
```

Master verification binds the independent rebuild and card reviews, code/runtime
review, data-health JSON, layer manifests, and two-root receipts. `gate-report.json`
is controlling machine evidence for `G-W04`; the Markdown acceptance report renders
it. Neither is emitted until every required independent recommendation is `PASS`.

## 15. Ownership-complete graph: W04.1–W04.7, P2.1–P2.9

Each path has one owner. Authorities, identity lifecycle, code admission, manifests,
rebuild, card review, gate, registry, and checkpoint are serial. Only the three
path-disjoint Silver producers run in parallel.

| Order | Packet / accountable owner | Exact output scope | Workflow coverage and dependency |
| ---: | --- | --- | --- |
| 1 | accepted W04.1 source evidence / master | existing `docs/dataset-cards/w04-source.md`; existing `reports/phase-gates/W04/source-schema-profile.md` | W04.1, P2.1; accepted provider/rights/coverage inputs are read-only |
| 2 | `W04-FIELD-SEMANTIC-DECISION-01-R1` / master | `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json`; `configs/schema/wyscout-v5-field-registry-v1.yaml`; `tests/contracts/test_wyscout_field_registry_authority.py`; return | W04.1; decision only |
| 3 | `W04-FIELD-SEMANTIC-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`; return | after 2; candidate read-only |
| 4 | `W04-FIELD-SEMANTIC-ACCEPT-01-R1` / master | `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json`; return | after PASS 3; sole acceptance |
| 5 | `W04-POSSESSION-SEMANTIC-DECISION-01-R1` / master | `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json`; `configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml`; `tests/contracts/test_wyscout_possession_taxonomy_authority.py`; return | after 4; project semantics |
| 6 | `W04-POSSESSION-SEMANTIC-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md`; return | after 5 |
| 7 | `W04-POSSESSION-SEMANTIC-ACCEPT-01-R1` / master | `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json`; return | after PASS 6 |
| 8 | `W04-IDENTITY-RULESET-DECISION-01-R1` / master | `reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json`; `configs/schema/wyscout-v5-identity-ruleset-v1.yaml`; `tests/contracts/test_wyscout_identity_authority.py`; return | W04.3, P2.3; four kinds/queue/correction policy |
| 9 | `W04-IDENTITY-RULESET-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md`; return | after 8; candidate read-only |
| 10 | `W04-IDENTITY-RULESET-ACCEPT-01-R1` / master | `reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json`; return | after PASS 9; truthful acceptance clock |
| 11 | `W04-DATA-CONTRACTS-01-R1` / master shared-contract owner | `src/scouting/contracts/wyscout_data.py`; `tests/contracts/test_wyscout_data_contracts.py`; return | W04.2–W04.6; existing evidence contracts unchanged |
| 12 | `W04-MANIFEST-BRIDGE-01-R1` / source runtime owner | `src/scouting/data_products/wyscout/manifest_bridge.py`; `tests/unit/test_wyscout_manifest_bridge.py`; `data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json`; return | W04.2, P2.1; sole strict source-manifest serializer |
| 13 | `W04-BRONZE-01-R1` / Bronze owner | `src/scouting/data_products/wyscout/bronze.py`; `tests/unit/test_wyscout_bronze.py`; Bronze product and `data/manifests/wyscout/v5/bronze/<build_id>.manifest.json`; return | W04.2/W04.4, P2.2; sole Bronze writer |
| 14 | `W04-IDENTITY-01-R1` / identity runtime owner | `src/scouting/identity/wyscout.py`; `tests/unit/test_wyscout_identity.py`; `data/identity/wyscout/v5/bundles/<digest>.identity-bundle.json`; `data/identity/wyscout/v5/review-queues/<digest>.identity-review-queue.json`; accepted `data/identity/wyscout/v5/corrections/<correction_id>.identity-correction.json`; return | W04.3, P2.3; sole crosswalk/queue/bundle runtime writer |
| 14C | `W04-IDENTITY-CORRECTION-<id>-DECISION/REVIEW/ACCEPT` / master, independent reviewer, master | exact `reports/reviews/W04/identity-corrections/<id>.decision.json`; `<id>.independent-review.md`; `<id>.acceptance.json`; three returns | conditional serial authority lifecycle; no runtime identity bytes |
| 14D | `W04-IDENTITY-REGENERATE-<id>-R1` / identity runtime owner | exact `data/identity/wyscout/v5/corrections/<id>.identity-correction.json`; new content-addressed queue and bundle; tests; return | only after PASS/accept 14C; sole correction normalization and regeneration |
| 15A | `W04-SILVER-MATCH-01-R1` / match owner | `src/scouting/data_products/wyscout/entities.py`; `tests/unit/test_wyscout_entities.py`; return | W04.4, P2.4; parallel only 15A–C, no manifest |
| 15B | `W04-SILVER-ACTION-01-R1` / action owner | `src/scouting/data_products/wyscout/actions.py`; `tests/unit/test_wyscout_actions.py`; return | W04.4, P2.4; after possession authority and identity |
| 15C | `W04-SILVER-LINEUP-01-R1` / lineup owner | `src/scouting/data_products/wyscout/lineups.py`; `tests/unit/test_wyscout_lineups.py`; return | W04.4, P2.4 |
| 16 | `W04-POSSESSION-01-R1` / possession owner | `src/scouting/data_products/wyscout/possessions.py`; `tests/unit/test_wyscout_possessions.py`; return | W04.4, P2.4; after 15B |
| 17 | `W04-PLAYER-MATCH-FACT-01-R1` / fact owner | `src/scouting/data_products/wyscout/player_match.py`; `tests/unit/test_wyscout_player_match.py`; return | W04.4, P2.4; after all Silver producers |
| 18 | `W04-SILVER-MANIFEST-01-R1` / Silver manifest owner | `src/scouting/data_products/wyscout/silver_manifest.py`; `tests/unit/test_wyscout_silver_manifest.py`; `data/manifests/wyscout/v5/silver/<build_id>.manifest.json`; return | W04.4, P2.4; sole Silver manifest writer |
| 19 | `W04-FEATURE-REGISTRY-01-R1` / master semantic owner | `configs/features/wyscout-v5-supported-count-features-v1.yaml`; `tests/contracts/test_wyscout_supported_feature_registry.py`; return | P2.6; only supported count/evidence features |
| 20 | `W04-GOLD-TEMPORAL-01-R1` / Gold owner | `src/scouting/data_products/wyscout/gold.py`; `src/scouting/data_products/wyscout/temporal_boundary.py`; `tests/unit/test_wyscout_gold.py`; `tests/unit/test_wyscout_temporal_boundary.py`; `data/manifests/wyscout/v5/gold/<build_id>.manifest.json`; boundary receipts; return | W04.5, P2.5/P2.7; sole Gold manifest writer |
| 21 | `W04-QUALITY-01-R1` / quality owner | `src/scouting/data_products/wyscout/quality.py`; `tests/unit/test_wyscout_quality.py`; return | W04.6, P2.8; no layer manifest |
| 22 | `W04-CODE-ADMISSION-IMPLEMENT-01-R1` / master | `src/scouting/data_products/wyscout/code_admission.py`; `scripts/admit_wyscout_v5_code.py`; `tests/unit/test_wyscout_code_admission.py`; return | executable/resource closure implementation |
| 23 | `W04-REBUILD-ENTRYPOINT-01-R1` / master | `src/scouting/data_products/wyscout/rebuild.py`; `scripts/rebuild_wyscout_v5.py`; `tests/integration/test_wyscout_rebuild.py`; return | W04.6; sole orchestrator, calls named writers |
| 24 | `W04-SHARED-INTEGRATION-01-R1` / master | `src/scouting/contracts/__init__.py`; `src/scouting/data_products/__init__.py`; `src/scouting/data_products/wyscout/__init__.py`; `src/scouting/identity/__init__.py`; return | serial sole shared-export owner |
| 25 | `W04-CODE-MANIFEST-ADMIT-01-R1` / master | `data/manifests/wyscout/v5/code/<code_manifest_sha256>.code-manifest.json`; `reports/reviews/W04/wyscout-code-manifest-admission-R1.md`; return | after integration freeze; sole admission invocation |
| 26 | `W04-CODE-MANIFEST-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/wyscout-code-manifest-independent-review-R1.md`; return | reproduces exact artifacts/runtime/resources |
| 27 | `W04-TWO-ROOT-REBUILD-01-R1` / master runtime owner | `runs/w04/wyscout-rebuild/<build_id>/**`; `data/working/wyscout/v5/**`; exact source/identity/layer runtime artifacts through sole serializers; `reports/reviews/W04/wyscout-rebuild-evidence-R1.md`; return | W04.6; after PASS 26; module sole writers remain |
| 28 | `W04-DATA-HEALTH-01-R1` / quality-report owner | `reports/phase-gates/W04/data-health.json`; `reports/phase-gates/W04/data-health.md`; return | P2.8; after 27, machine JSON controls |
| 29 | `W04-TRANSFORMED-DATASET-CARD-01-R1` / master card author | `docs/dataset-cards/w04-wyscout-transformed-v1.md`; return | P2.9; distinct from source card; after health |
| 30 | `W04-DATASET-CARD-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/wyscout-transformed-dataset-card-independent-review-R1.md`; return | W04.7/P2.9; verifies intended use, populations, coverage, bias, rights, transformations, update policy |
| 31 | `W04-INDEPENDENT-REBUILD-REVIEW-01-R1` / independent reviewer | `tests/security/test_w04_temporal_leakage.py`; `reports/reviews/W04/wyscout-rebuild-independent-review-R1.md`; return | W04.7; independent raw-to-Gold proof after 27–30 |
| 32 | `W04-MASTER-VERIFY-01-R1` / master verifier | `reports/verification/W04/wyscout-raw-to-gold-R1-master-verification.md`; `reports/verification/W04/verification-report.md`; `reports/verification/W04/clean-tree-report.md`; `reports/verification/W04/phase-verifier-candidate.json`; return | W04.7, G-W04; verifies all runtime/review artifacts |
| 33 | `W04-MASTER-GATE-01-R1` / master | `reports/reviews/W04/master-review.md`; `reports/phase-gates/W04/acceptance-report.md`; `reports/phase-gates/W04/gate-report.json`; return | G-W04; after all independent PASS reports |
| 34 | W04 registry acceptance / master only | `orchestration/phase_registry.yaml` | only after passing gate-report digest is final |
| 35 | W04 checkpoint / master only | local commit `phase(w04): accept governed data spine`; local tag `checkpoint/w04-accepted` | commit only after accepted registry update; master reruns clean-tree verification, then applies the tag to that exact commit |

The runtime scopes in rows 12, 14, 27 are generated outputs, not direct multi-writer
permission. `manifest_bridge.py`, `bronze.py`, `silver_manifest.py`, and `gold.py`
alone serialise their manifests. `rebuild.py` orchestrates; it does not serialise a
layer manifest. The identity runtime alone emits crosswalk/queue/bundle bytes, but
cannot author or accept human decisions.

In this table, `return` always means the one exact path
`reports/reviews/W04/returns/<packet-id>.md`; it is never a directory grant.
Authority/output shorthand in rows 2–10 expands only to the exact paths already
enumerated in Sections 3 and 6, and test shorthand expands only to the named test
paths in Section 14. No owner may choose a different path during implementation.

This graph covers W04.1 rights/coverage, W04.2 source ingestion and admission, W04.3
four-kind identity lifecycle, W04.4 Bronze/Silver, W04.5 temporal/Gold, W04.6
quality/rebuild, W04.7 independent review and gate; and P2.1 acquisition, P2.2
Bronze, P2.3 identity, P2.4 Silver, P2.5 temporal, P2.6 feature families, P2.7 Gold,
P2.8 health, P2.9 card.

## 16. Finding closure

| Finding | R5 closure |
| --- | --- |
| R4 P1 identity clocks | Sections 6–7 distinguish historical `valid_from` from truthful decision/review/master-acceptance `available_at`; bundle dependency uses decision observation and acceptance watermark; corrections advance availability; equality to cutoff fails. |
| R4 P1 W04.3 lifecycle | Section 6 specifies four-kind crosswalk rows, exact state/confidence, content-addressed bundle and ID relationship, strict `IdentityEvidence` projection, durable deduplicated queue, correction/review/acceptance, immutable supersession, and owners. |
| R4 P1 runtime/phase ownership | Section 15 names source and identity outputs, data health, separate transformed card and independent review, final independent and master verification, gate artifacts, and master-only registry/checkpoint. |
| R4 P1 executable/resource closure | Section 12 binds exact selector-selected lock wheels, installed `RECORD` and file bytes, interpreter/libpython/stdlib, closed local resources, runtime guarded reads, all pre-build digests, and negative tamper tests. |
| Accepted temporal closure | Sections 7–9 retain period-relative ordering, clock-free semantic proof, truthful unchanged-contract adapter, and strict dependency clocks. |
| Accepted semantic authority | Section 3 retains local digests, accountable decisions, independent reviews, master acceptance, `UNMAPPED`, and no provider-native possession claim. |
| Accepted source/coverage closure | Sections 2 and 5 retain the completion-only seam, exact 18 ordered rows, and exact strict `DataCoverage`. |
| Accepted Gold/minutes/fact closure | Sections 8–11 retain minute/per-90 suppression, neutral role grain, Gold equations/applicability, and result-independent player-match fact. |

## 17. Stop rules and handoff

Stop rather than improvise when a path/digest/count changes; a tenant, identity or
semantic decision/review/acceptance is missing; an identity clock would be backdated;
an excluded stream would be read; an unknown would be guessed; action UTC or minutes
would be fabricated; a wheel, installed file, interpreter, stdlib, code, or local
resource is outside the admitted closure; a shared writer is ambiguous; a required
health/card/review/gate artifact is absent; or a dependency, migration, network,
provider, rights, architecture, or local-only change is needed.

Implementation begins only after master and independent acceptance of this R5.
Implementers do not update the phase registry, create the checkpoint, or self-approve.

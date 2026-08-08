# W04 Wyscout v5 canonical schema and deterministic rebuild design — R8

Status: **implementation design for master and independent review; not self-approved**

This document replaces R7 in full. It is the standalone design for the local-only
W04 Wyscout Figshare v5 Bronze-to-Gold proof. R8 retains R7's total unknown-kind
quarantine and conservative all-groups distribution closure, restores every R6/R5
source, temporal, identity, football-product, coverage, path, environment, resource,
gate, and ledger contract, and closes the eight P1 and two P2 regressions returned
against R7. It changes no architecture, provider, rights, dependency, lock,
migration, network, storage-root, ignore, remote, or deployment boundary.

The binding measured evidence is:

- `data/source/wyscout/v5/completion-manifest.json`, 6,803 bytes, SHA-256
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- `reports/phase-gates/W04/source-schema-profile.md`, SHA-256
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- upstream availability `2020-01-28T14:24:27Z` and actual local acquisition
  `2026-07-29T15:51:08.598589Z`;
- completion class `wyscout_figshare_v5_cc_by_4`, licence `CC-BY-4.0`,
  restricted project control, attribution required;
- 7 direct objects, 10 durable admitted archive members, 4 directory-only
  exclusions, 7 competitions, 142 teams, 3,603 players, 1,826 matches, and
  3,071,395 events; and
- the accepted adapter `src/scouting/sources/wyscout.py`, whose durable source
  namespace is limited to `objects/<name>`, `archive-members/<name>`, and
  `completion-manifest.json`.

No provider access, excluded-payload read, network, download, wheelhouse acquisition,
runtime label guessing, dependency change, environment cleanup, container, hosted
artifact, migration, new root, ignore-rule change, export, or Git action is
authorised by this design.

## 1. Claim boundary and non-negotiable invariants

The permitted claim is a frozen historical engineering and player-evidence proof.
It does not establish current players, live coverage, provider continuity, women or
youth coverage, exact minutes, provider-product equivalence, recruitment relevance,
transfer success, or prospective benefit.

The following are normative:

1. Only exact completion-declared `object_path` and `member_path` values are
   readable. `matches.zip` and `events.zip` are hash evidence only; downstream never
   opens them. The four excluded directories have no admitted payload path.
2. Provider event `id` identifies an action record; `eventId` identifies taxonomy.
   Names are display evidence only and never identity or semantic matching keys.
3. JSON numbers are parsed as `Decimal`. Action occurrence is period-relative. No
   second-half UTC, half-time duration, terminal, continuous clock, elapsed minutes,
   or per-90 denominator is invented.
4. Field, possession, identity, and supported-feature semantics require a master
   decision, independent review, and master acceptance with truthful clocks.
5. Source validity and project knowability are distinct. Decisions, reviews,
   acceptances, and corrections are never backdated to source release.
6. Existing `DependencyKind`, `IdentityEvidence`, `TemporalEvidence`, and
   `RetrievalResult` remain unchanged. W04 projects only compatible resolved rows.
7. Bronze, Silver, Gold, semantic manifests, stable environment identity, and
   semantic proofs contain no run ID, host path, elapsed duration, operational
   trace, generation clock, root-bearing script bytes, or pyc bytes.
8. One real sampled generation clock is introduced only by the serving adapter and
   is shared with `RetrievalResult.generated_at`.
9. Stable build identity closes before output over repository code, exact selected
   all-groups lock closure, verified extracted and installed bytes, reviewed
   normalization of uv-generated scripts, interpreter/libpython, standard library,
   exact local resources, schemas, and source/identity/authority evidence.
10. The original wheel ZIP hash is explicitly not verified when the archive is
    absent. Extracted trees and installed files are attested as the bytes they are.
11. Rights, authority, identity, cutoff, cache association, script, bytecode,
    interpreter, resource, ownership, lineage, partition, reconciliation, and
    sole-writer failures are fail-closed.
12. Generated identity, product, staging, and alternate bytecode state stays under
    the already-approved `data/working` root.
13. The full gate precedes the acceptance integration commit and annotated tag.
    Registry/checkpoint evidence then lands in a distinct local ledger commit.

## 2. Completion-declared source seam and strict source-record envelope

The exact source root is `data/source/wyscout/v5`. The completion document is opened
first and its digest checked. Every admitted path is NFC POSIX-relative, remains
beneath the resolved root, is a regular non-symlink file, and matches its declared
size and SHA-256. Directory scanning, aliases, fallback extraction, inferred
layouts, symlinks, case-normalized substitutes, and reads of undeclared paths fail.

Readable direct objects are:

```text
objects/competitions.json
objects/teams.json
objects/players.json
objects/eventid2name.csv
objects/tags2name.csv
```

Readable archive members are the five exact `matches_<country>.json` and five exact
`events_<country>.json` paths in Section 3. For each country, distinct event
`matchId` equals match `wyId`: England 380, France 380, Germany 306, Italy 380, and
Spain 380.

### 2.1 Envelope owns record family; payload never does

The completion reader emits one strict project source-record envelope per parsed
top-level source record. The envelope is not provider payload and has exact fields:

```text
envelope_version = "w04-source-record-envelope-v1"
source_manifest_id
completion_relative_path
source_sha256
source_record_ordinal
record_kind
raw_record
```

`record_kind` is assigned only by this closed completion-path map:

| Exact completion path | Envelope `record_kind` |
| --- | --- |
| `objects/competitions.json` | `competition` |
| `objects/teams.json` | `team` |
| `objects/players.json` | `player` |
| `objects/eventid2name.csv` | `event-taxonomy` |
| `objects/tags2name.csv` | `tag-taxonomy` |
| `archive-members/matches_<country>.json` | `match` |
| `archive-members/events_<country>.json` | `action` |

Here `<country>` is exactly one of `England`, `France`, `Germany`, `Italy`, or
`Spain`, with the exact filename/case already declared by completion. No wildcard,
substring, prefix-only, or case-folded match is permitted. Any other completion path
is denied before parsing.

The Bronze dispatcher reads only the envelope member named exactly `record_kind`.
It never reads a payload `kind`, name, label, `eventId`, table shape, or filename to
select a family. A payload field named `kind` remains ordinary preserved/provider
data governed by the accepted field registry and has no dispatch authority.

The seven known tokens are exactly:

```text
competition | team | player | event-taxonomy | tag-taxonomy | match | action
```

A production envelope constructed from the accepted map necessarily has one of
those values. Contract fixtures also exercise absent, null, non-string, safe unknown,
and unsafe unknown envelope discriminators. Those states route only to the fixed
unknown rejected-record family in Section 7.3 and never to known Bronze, rejected
field, Silver, or Gold. There is no trimming, Unicode normalization, case folding,
plural conversion, label lookup, payload inference, or fallback.

## 3. Exact 18-row source evidence and source `DataCoverage`

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

The existing `SourceSnapshotManifest` uses exact clocks, restricted classification,
derived/internal-review allowed, export false, and attribution required. Its `files`
tuple is exactly:

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

The exact source `DataCoverage` is separate from Gold coverage:

```text
source_object_integrity              7 / 7 = 1.0
admitted_member_integrity           10 / 10 = 1.0
match_partition_presence             5 / 5 = 1.0
event_partition_presence             5 / 5 = 1.0
partition_match_id_alignment         5 / 5 = 1.0
scope_exclusion_directory_only       4 / 4 = 1.0
overall = min(all six dimensions) = 1.0
missing_dimensions = ()
```

Coverage values are strict Python `float` `1.0`; counts are non-negative strict
`int`. Zero expected counts, 17/19 rows, reordered/duplicate paths, or replacing
these dimensions with Gold eligibility fields fails.

The sole source-manifest artifact is:

```text
data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json
```

Canonical source identity uses numeric keys only:

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

## 4. Accepted semantic and identity authorities

The profile establishes shape/count/key evidence, not meaning. Each candidate has
truthfully ordered `decided_at <= reviewed_at <= accepted_at`; a reviewer cannot
edit the candidate, the master accepts only `PASS`, and no clock comes from file
metadata.

### 4.1 Field, possession, and supported-feature routes

Field authority is exactly:

```text
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json
configs/schema/wyscout-v5-field-registry-v1.yaml
reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json
```

It binds completion/profile, the event-map digest
`ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`,
tag-map digest
`e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922`,
and every `(record_kind,json_path)`. Each field is exactly `TRANSFORM`,
`PRESERVE_UNMAPPED`, or `FORBIDDEN`; unknown fields are `UNMAPPED`; unknown
envelope kinds are rejected records; runtime label matching and provider-native
semantic claims are false.

Possession authority, after field acceptance, is exactly:

```text
reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json
configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml
reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json
```

Predicates use numeric `event_id`, nullable numeric `subevent_id`, sorted required
tag IDs, and sorted forbidden tag IDs. Decisions are `CONTROL`, `CONTESTED`,
`DEAD_BALL`, `RESTART`, `NON_CONTROL_ADMIN`, or `UNMAPPED`. Policies are:

```text
unknown_combination_policy: UNMAPPED
unknown_name_matching: forbidden
runtime_label_matching: forbidden
provider_native_possession_claim: false
period_boundary_policy: close
simultaneous_cross_team_policy: uncertain_boundary
```

Supported-feature authority, accepted before Gold, is exactly:

```text
reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json
configs/features/wyscout-v5-supported-count-features-v1.yaml
reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json
```

It exhaustively binds each supported/suppressed/unavailable field to inputs,
aggregation, applicability, denominator, output type, state, reason, and schema.
Minutes, rates, per-90, continuous time, action value, provider possession,
outcome-dependent, role-inferred, and otherwise unsupported features are explicitly
unavailable or `suppressed_unsupported_denominator`; absence never grants permission.
Canonical parsed YAML is sorted-key JSON with schema-declared array order. Registry
digest excludes acceptance bytes; acceptance binds registry digest. Gold and
`feature_schema_hash` are unavailable until acceptance.

### 4.2 Identity authority, rows, queue, bundle, and corrections

Identity authority is exactly:

```text
reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json
configs/schema/wyscout-v5-identity-ruleset-v1.yaml
reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json
```

Generated identity paths are only:

```text
data/working/wyscout/v5/identity/review-queues/
  <queue_sha256>.identity-review-queue.json
data/working/wyscout/v5/identity/bundles/
  <identity_bundle_sha256>.identity-bundle.json
data/working/wyscout/v5/identity/corrections/
  <correction_id>.identity-correction.json
```

The guarded category is `W04_IDENTITY_RUNTIME`. Readers start from one exact accepted
bundle and may open only queue/correction paths named by it. Scans, newest selection,
aliases, alternate roots, and unreferenced files fail.

`W04IdentityCrosswalkRow` strictly contains:

```text
schema_version = 1
crosswalk_schema_version = "w04-wyscout-crosswalk-v2"
tenant_context
entity_kind = COMPETITION | TEAM | PLAYER | MATCH
source_identity
source_manifest_id, source_manifest_sha256
source_row_refs: non-empty sorted tuple
canonical_id: UUID | null
version: positive int
classification_method
identity_match_method: existing IdentityMatchMethod | null
confidence: exactly 0.0 or 1.0
state: RESOLVED | REVIEW_REQUIRED | REJECTED
valid_from, valid_to, available_at, reviewed_by
supersedes_evidence_digest
ruleset decision/review/acceptance IDs and digests
reason_codes: sorted unique non-empty tuple
evidence_digest, crosswalk_row_id, trace_id
```

Valid combinations are exact:

| Situation | Effective state | Classification | Existing match method | Canonical/confidence/reviewer |
| --- | --- | --- | --- | --- |
| unique valid same-kind source key | `RESOLVED` | `SOURCE_KEY_DETERMINISTIC_RESOLUTION` | `DETERMINISTIC` | UUID / 1.0 / null |
| malformed, absent, duplicate, collision, conflict | `REVIEW_REQUIRED` | `SOURCE_KEY_REVIEW_REQUIRED` | null | null / 0.0 / null |
| player key zero | `REJECTED` | `PROVIDER_ZERO_ACTOR_REJECTION` | null | null / 0.0 / null |
| reviewed queue resolution | `RESOLVED` | `REVIEWED_QUEUE_RESOLUTION` | `REVIEWED` | UUID / 1.0 / non-null |
| reviewed queue rejection | `REJECTED` | `REVIEWED_QUEUE_REJECTION` | null | null / 0.0 / non-null |
| direct resolved supersession to entity | `RESOLVED` | `REVIEWED_DIRECT_SUPERSESSION_RESOLUTION` | `REVIEWED` | UUID / 1.0 / non-null |
| direct resolved supersession to rejection | `REJECTED` | `REVIEWED_DIRECT_SUPERSESSION_REJECTION` | null | null / 0.0 / non-null |
| immutable prior behind accepted edge | effective `SUPERSEDED` | `ACCEPTED_SUPERSESSION_EDGE` in bundle index | original unchanged | original unchanged |

`IdentityMatchMethod.EXACT` is unused. Only current effective `RESOLVED` rows project
to `IdentityEvidence`; projection renames `identity_match_method` to `method` and
copies existing fields. Null method/ID, non-resolved, and superseded rows never
project.

Evidence digest is SHA-256 of canonical semantic fields through `reason_codes`,
excluding digest/IDs/trace. IDs are:

```text
crosswalk_row_id = UUIDv5(
  identity_crosswalk_namespace,
  tenant_id + ":" + entity_kind + ":" + source_identity.canonical_json +
  ":" + version + ":" + evidence_digest)
trace_id = UUIDv5(crosswalk_row_id, "w04-identity-crosswalk-trace-v2")
```

Versions are consecutive; gaps, forks, tenant changes, invalid combinations, or
classification changes fail. Initial validity may equal source release, but initial
availability is truthful ruleset acceptance.

Queue bytes exclude their digest and bind tenant/manifest/ruleset, prior queue,
sorted items, and exact counts. Only `REVIEW_REQUIRED` enters. Player zero is
rejected without a queue item. The measured 23 absent bench and 8 absent
substitution-in references remain queued/excluded unless separately reviewed.

Bundle bytes contain tenant/source/ruleset, current rows, historical digests,
effective index/classification, supersession edges, counts, queue path/digest,
accepted corrections, prior bundle, observed/available clocks. Rows sort by
kind/provider/source ID/source version/version/evidence digest; the entire index,
queue, history, edges, correction chain, counts, and references are recomputed.

```text
identity_bundle_id =
  UUIDv5(w04_dependency_namespace,
    "identity_bundle:" + identity_bundle_sha256)
```

That ID is the bundle external/dependency/build field. Its dependency kind is
`identity_evidence`; observed time is the ruleset decision; available time is the
maximum ruleset/correction acceptance.

Every correction uses:

```text
reports/reviews/W04/identity-corrections/<correction_id>.decision.json
reports/reviews/W04/identity-corrections/<correction_id>.independent-review.md
reports/reviews/W04/identity-corrections/<correction_id>.acceptance.json
data/working/wyscout/v5/identity/corrections/
  <correction_id>.identity-correction.json
```

The normalized correction is an exact union:

```text
QUEUE_DISPOSITION:
  prior_queue_sha256, queue_item_id
  prior_status = OPEN | IN_REVIEW
  next_status = RESOLVED_BY_CORRECTION | REJECTED_BY_CORRECTION
  direct_supersession = null

DIRECT_CURRENT_RESOLVED_SUPERSESSION:
  queue_disposition = null
  asserted_current_bundle_id
  asserted_current_evidence_digest
  asserted_prior_state = RESOLVED
```

Queue disposition emits a linked queue snapshot and exactly one transition. Direct
supersession requires a current non-superseded resolved row without queue item,
emits no item/transition/snapshot, and retains the exact prior queue path/digest.
Both retain prior bytes, set `supersedes_evidence_digest`, use `new_version=prior+1`,
preserve the same frozen source-valid interval, set later availability to accepted
time, advance the bundle, dependency lineage, watermark, and build ID. Stale state,
cross-route fields, invented queue history, name-only evidence, actor/clock mismatch,
or non-consecutive version fails.

### 4.3 Exact 17-path local-resource allowlist

The local-resource category contains exactly these 17 repo-relative paths:

1. `configs/schema/wyscout-v5-identity-ruleset-v1.yaml`
2. `configs/schema/wyscout-v5-field-registry-v1.yaml`
3. `configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml`
4. `configs/features/wyscout-v5-supported-count-features-v1.yaml`
5. `reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json`
6. `reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md`
7. `reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json`
8. `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json`
9. `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`
10. `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json`
11. `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json`
12. `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md`
13. `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json`
14. `reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json`
15. `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
16. `reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json`
17. `reports/phase-gates/W04/source-schema-profile.md`

Each entry binds exact path, physical SHA-256, size, mode, purpose, parser/schema
version, and authority link. There is no directory shorthand and no eighteenth
resource.

Guard categories stay disjoint:

- strict source: completion plus exactly declared objects/members;
- identity runtime: one accepted bundle and only named queue/corrections;
- runtime admission: repository/lock/uv-cache/extracted/installed/interpreter/stdlib;
- exact local resources: only the 17 paths above;
- parent products: only completion-manifest-named parent files;
- outputs: exact staging/final/manifest/receipt destinations.

Source, identity, runtime bytes, outputs, window values, cutoff values, and neutral
context are not relabelled generic resources. Window definition/cutoff and neutral
context remain schema-bound canonical invocation values. They become resources only
if a later, separately approved packet names an exact already-approved file; broad
config discovery is forbidden.

## 5. Exact temporal dependency and cutoff contract

W04 has exactly five dependencies:

| Evidence | Existing `DependencyKind` | `observed_at` | `available_at` |
| --- | --- | --- | --- |
| strict source manifest | `source_manifest` | source release | source release |
| accepted identity bundle | `identity_evidence` | identity decision | max identity/correction acceptance |
| accepted field registry | `feature_schema` | field decision | field acceptance |
| accepted possession taxonomy | `feature_schema` | possession decision | possession acceptance |
| accepted supported-feature registry | `feature_schema` | feature decision | feature acceptance |

Feature dependency IDs are UUIDv5 over artifact type, fixed artifact ID, artifact
digest, and acceptance digest. Dependencies sort exactly by:

```text
(DependencyKind enum rank, dependency_id.bytes, digest,
 observed_at, available_at)
```

Duplicate kind/ID fails. Cardinality is exactly five: one source manifest, one
identity evidence, and three distinct feature-schema dependencies.

The eligibility predicate is strictly:

```text
for every dependency d:
    d.observed_at < feature_cutoff_ts
    d.available_at < feature_cutoff_ts

dependency_watermark = max(d.available_at for all five dependencies)
dependency_watermark < feature_cutoff_ts
```

Equality fails in every comparison. `<=` is forbidden. In addition, every authority
decision, independent-review, acceptance, and included identity-correction clock
bound by a dependency must be strictly before the cutoff; a clock equal to cutoff
fails even if another projected field would otherwise compare earlier. Cutoff
before or equal to supported-feature decision, review, or acceptance fails. The same
strict rule applies to source, identity, field, possession, and feature authorities
without exception.

`lineage_hash` is SHA-256 of the five complete ordered dependency records. A registry
revision requires a new decision/review/acceptance, dependency ID/digest,
`feature_schema_hash`, lineage hash, watermark, and build ID.

`W04SemanticTemporalProof` is clock-free with snapshot, valid-from, strict watermark,
cutoff, manifest IDs, feature schema hash, five-dependency lineage, period-relative
precision, and `partial_match_claim_supported=false`. Its validator applies all
strict inequalities above.

At serving, exactly one injected UTC value is sampled:

```text
adapt_w04_temporal_proof(proof, generated_at_ts) -> TemporalEvidence
```

The adapter revalidates proof/cutoff, requires generation at or after valid-from,
copies every existing field one-to-one, and adds only generation.
`RetrievalResult.generated_at` uses the same sample. Boundary receipts contain real
run clocks but are operational, never semantic/build inputs.

## 6. Football products, keys, feature coverage, and applicability

### 6.1 Action, lineup, possession, and player-match facts

`silver_action` retains provider record ID and numeric taxonomy IDs, canonical actor/
team/match/competition where resolved, period code/rank, exact
`decimal128(22,18)` `eventSec`, source scale 0..18, sorted tags, original coordinate
order, source refs, authority IDs/digests, and lineage. Its occurrence precision is
`period_relative`; period/action UTC is null. Order is:

```text
(period_rank, period_elapsed_seconds, source_record_ordinal,
 source_event_record_id)
```

The 7,821 string subevent IDs remain preserved/unmapped. Source `x=-1` and the two
`y=101` anomalies remain evidence and never silently clamp.

Lineup stints use only lineup, bench, substitution, and period-relative evidence.
Substitution nominal minute `m` means `[m,m+1)`. If start is `[s0,s1)` and end is
`[e0,e1)`:

```text
lower = max(0, e0 - s1)
upper = max(0, e1 - s0)
```

Open stints are right-censored. Event maxima, `Regular`, 90, and substitution maxima
cannot invent a terminal. Exact/elapsed minutes and per-90 remain null/absent,
`per90_eligible=false`, reason `suppressed_unsupported_denominator`.

Possessions order actions by the action key. Within each match/period, reviewed
`CONTROL`/`RESTART` opens team control; same-team continues; opposing resolved
control closes/opens; `DEAD_BALL` closes/attaches only as taxonomy states;
`CONTESTED` buffers/attaches only under its rule; cross-team equal clocks are
uncertain; unknown/missing team stays unassigned; period end closes; nothing crosses
periods. Only deterministic sequences are resolved/Gold-eligible. This is a
project-defined taxonomy result, never provider-native possession.

Candidate player-match pairs are the union of resolved non-zero lineup, bench,
substitution, and event references. Zero actors are separate. The measured 50,522
event player-match pairs are evidence counts, not minutes.

The exact player-match primary key is restored unchanged:

```text
(tenant_id, source_manifest_id, match_id, player_id,
 player_match_fact_schema_version)
```

Competition, season, and match-bound team are reconciled row/context fields, not key
substitutes. Team is match-bound. Facts are result-independent and contain evidence
flags/counts, nominal stint states, null elapsed fields, the six Gold coverage
structures below, applicability, clock-free proof, refs, and source/identity/
authority/schema digests. They contain no score, winner, points, outcome, current
team, minutes, or per-90.

Gold selects complete matches satisfying:

```text
window_start_utc <= match_start_utc < window_end_utc
match_start_utc < feature_cutoff_ts
all five dependencies satisfy Section 5 strict-before
```

Partial-match/action-instant claims remain
`unsupported_period_relative_occurrence`.

### 6.2 Exact Gold key and neutral role context

Gold has exact collision-free key:

```text
(tenant_id, player_id, competition_id, season_id,
 role_context_id, role_context_version,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, dependency_lineage_hash)
```

`feature_schema_hash` is required on every row and proof but is not a primary-key
member and never replaces `role_context_version` or `dependency_lineage_hash`.
Competition/season/role/window/context/lineage fields reconcile to the manifest.

Neutral context is:

```text
role_context_namespace =
  UUIDv5(NAMESPACE_URL, "urn:scouting-intelligence:role-context")
role_context_version = "w04-neutral-role-context-v1"
role_context_state = "neutral_unscoped"
role_context_id =
  UUIDv5(role_context_namespace,
         role_context_version + ":" + role_context_state)
```

No inferred role label or current-team context enters W04 Gold.

### 6.3 Separate exact six-dimensional Gold coverage

Gold coverage is computed per Gold player-window over selected
`silver_player_match_fact` rows. It is not source `DataCoverage`. Every dimension
stores strict integer `numerator`, strict integer `denominator`, exact decimal
coverage, state, and sorted unique reason codes. Integers, not rounded floats, are
authority.

| Dimension | Denominator `D` | Numerator `N` |
| --- | --- | --- |
| `identity` | all non-zero player-reference occurrences in contributing lineup, bench, substitution, and event evidence | occurrences resolved exactly once to the row player and correct match team |
| `lineup` | selected player-match candidate facts | facts with structurally reconciled formation membership/stint state, including explicit event-only/no-lineup state |
| `action` | admitted non-zero-player actions for the row player in selected matches | actions assigned exactly once to the correct player-match fact and team |
| `coordinate` | row actions for which the accepted field registry marks positions applicable | applicable actions with allowed cardinality, all required axes present, numeric, and within inclusive `0..100` |
| `possession` | row actions the accepted taxonomy marks possession eligible | eligible actions assigned to exactly one resolved possession |
| `temporal` | the strict source/identity/field/possession/feature dependencies plus selected match/action dependency groups | dependencies with observed and available clocks strictly before cutoff, matches starting before cutoff, and actions carrying snapshot-before-cutoff proof |

For each dimension:

```text
if D > 0:
    require 0 <= N <= D
    coverage = exact_decimal(N / D)
    state = complete if N == D else partial
elif D == 0 and dimension in {coordinate, possession}
     and the accepted field-registry/taxonomy proves no applicable evidence:
    N = 0
    coverage = 1
    state = not_applicable_zero_denominator
else:
    N = 0
    coverage = 0
    state = missing_zero_denominator
```

`N>D`, `N<0`, or `D<0` is a hard reconciliation failure. Only coordinate and
possession may use `not_applicable_zero_denominator`, and only with exact accepted
authority. `missing_dimensions` is the lexically sorted set of dimensions in
`partial`, `missing_zero_denominator`, `authority_missing`, or `failed`;
authority-proven optional non-applicability is not missing.

```text
coverage_overall =
  min(identity, lineup, action, coordinate, possession, temporal)
```

There is no weighting, waiver, or substitution with source coverage.

Applicability is evaluated in this exact order:

1. prohibited/unknown rights; invalid strict manifest; missing/unaccepted
   registry/taxonomy; identity/partition/lineage mismatch; duplicate action identity;
   match/team conflict; or any dependency/authority at or after cutoff =>
   `suppressed` with exact hard-failure reason;
2. mandatory identity/action/temporal zero denominator; `N>D`; required dependency
   absent; or request for minutes/rate/per-90 =>
   `suppressed` with `mandatory_coverage_or_denominator_failure` or
   `unsupported_minutes_denominator`;
3. hard gates pass but any dimension is partial/missing, any player-match fact is
   right-censored/uncertain, or coordinate/possession evidence is incomplete =>
   `research_only` with sorted incomplete dimensions/states;
4. all dimensions are complete or authority-proven optional non-applicable,
   `coverage_overall=1`, and every requested feature is in the accepted supported
   registry => `w04_data_ready`.

No other applicability state or promotion path exists.

## 7. Exact paths, serializers, staging, and unknown quarantine

Path tokens are:

```text
sha = exactly 64 lowercase hex
uuid = lowercase canonical 36-character UUID
country = england | france | germany | italy | spain
utc = UTC YYYYMMDDTHHMMSSffffffZ with six fractional digits
build_id = exactly 64 lowercase hex
run_id = canonical UUID sampled once per invocation
```

### 7.1 Known Bronze, rejected fields, and Silver

The exact known Bronze raw path is:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  records/record_kind=<known-kind>/source_sha256=<source_sha>/
  part-00000.parquet
```

The literal segment is `records`, never `raw`. Each row preserves complete canonical
raw record/digest, source path/digest/ordinal, envelope kind, measured paths/types,
accepted registry, admission, source availability, tenant/manifest/lineage, and
rights.

Known-record rejected fields are:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  quarantine/rejected-field/record_kind=<known-kind>/
  source_sha256=<source_sha>/part-00000.parquet
```

Each rejected field stores source ref, exact JSON path, canonical original
value/digest, measured JSON type, `PRESERVE_UNMAPPED|FORBIDDEN`, reason, accepted
registry, and rights. Unknown records emit no rejected-field rows.

Every Silver final formula is:

```text
data/working/wyscout/v5/silver/build_id=<build_id>/
  competition/source_partition=global/part-00000.parquet
  team/source_partition=global/part-00000.parquet
  player/source_partition=global/part-00000.parquet
  match/source_partition=<country>/part-00000.parquet
  action/source_partition=<country>/part-00000.parquet
  lineup-stint/source_partition=<country>/part-00000.parquet
  possession/source_partition=<country>/part-00000.parquet
  player-match-fact/source_partition=<country>/part-00000.parquet
```

Country comes only from the exact admitted member filename. `entities.py` alone
serializes competition/team/player/match; `actions.py` action; `lineups.py`
lineup-stint; `possessions.py` possession; `player_match.py` player-match-fact.
`silver_manifest.py` alone writes
`data/manifests/wyscout/v5/silver/<build_id>.manifest.json`.

### 7.2 Gold, receipts, staging, and publication

For every non-empty competition/window partition:

```text
data/working/wyscout/v5/gold/build_id=<build_id>/player-window/
  competition_id=<uuid>/window_definition_id=<uuid>/
  window_start_utc=<utc>/window_end_utc=<utc>/
  feature_cutoff_ts=<utc>/part-00000.parquet
```

`gold.py` is sole serializer and sole writer of
`data/manifests/wyscout/v5/gold/<build_id>.manifest.json`.

Receipts are:

```text
runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json
runs/w04/wyscout-rebuild/<build_id>/<run_id>/boundary/
  <sha256-of-exact-gold-relative-path>.temporal-boundary-receipt.json
```

`temporal_boundary.py` alone writes boundary receipts. `rebuild.py` invokes named
serializers and writes only the invocation receipt; it cannot serialize products or
layer manifests. Receipt clocks/paths are operational and excluded from semantic
payloads, manifests, and build ID.

Each serializer stages only under:

```text
data/working/wyscout/v5/.staging/<build_id>/<run_id>/
  bronze/<same final suffix>.partial
  silver/<product>/<same final suffix>.partial
  gold/<same final suffix>.partial
  runtime-pycache/
```

A serializer writes, flushes, closes, hashes, validates, rechecks frozen code/
environment/resources, and atomically renames. Existing unequal destination fails.
Each layer manifest is written last via exact sibling partial and atomic rename.
Readers open only paths named exactly once by the completion manifest; missing,
extra, partial, cross-layer, or unowned paths fail.

Manifest entries bind repo-relative path, serializer/version, schema, row count,
semantic digest, physical SHA-256/size, ordered parents, partition values, rights,
and completion. Empty quarantine partitions record count zero without a zero-row
Parquet. Bronze references every records/rejected-record/rejected-field file; Silver
references Bronze; Gold references Silver, five dependencies, accepted feature
schema, and strict temporal proofs.

### 7.3 Fixed unknown partition and canonical discriminator identity

Every envelope with a missing/null/non-string/unknown `record_kind` uses:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  quarantine/rejected-record/record_kind=unknown/
  raw_kind_state=<closed-state-token>/
  raw_kind_sha256=<64-lowercase-hex>/
  source_sha256=<source_sha>/part-00000.parquet
```

`record_kind` is literal `unknown`; original discriminator text never enters a path.
`raw_kind_*` names are retained schema names and refer only to the strict envelope
discriminator, never a payload field. States are:

| Token | Exact envelope discriminator condition |
| --- | --- |
| `missing` | `record_kind` absent |
| `null` | present JSON null |
| `non-string` | present boolean, number, array, or object |
| `string-unknown-safe` | unknown string matching ASCII `[A-Za-z][A-Za-z0-9_-]{0,63}` |
| `string-unsafe` | every other unknown string, including empty, `.`, `..`, slash/backslash, control, percent, non-ASCII, or longer |

Known tokens never enter string-unknown states. Safe affects only the state; original
text never becomes a path token.

The exact canonical JSON envelope is:

```json
{
  "envelope_version": "w04-raw-kind-v1",
  "state": "<UPPERCASE_STATE>",
  "value_present": true,
  "value": "<exact typed canonical JSON value>"
}
```

States are `MISSING`, `NULL`, `NON_STRING`, `STRING_UNKNOWN_SAFE`,
`STRING_UNSAFE`. Missing uses `value_present=false,value=null`; null uses
`value_present=true,value=null`. Other values retain exact typed semantic JSON:
sorted object keys, ordered arrays, untrimmed/un-normalized Unicode string scalars,
canonical Decimal numbers, and booleans. Canonical JSON has sorted keys, no
insignificant whitespace, UTF-8, and fixed escaping.

```text
envelope_bytes = canonical_json(envelope)
raw_kind_sha256 = lowercase_hex(SHA256(
  UTF8("w04-raw-kind-v1") || 0x00 ||
  UINT64_BE(len(envelope_bytes)) || envelope_bytes
))
```

The rejected row preserves source ref, complete raw record/digest, state, presence
bit, exact typed original value, envelope bytes/digest, rejection code
`UNKNOWN_RECORD_KIND`, accepted field authority, clocks, tenant/manifest/lineage,
and rights.

Before staging, Bronze maps `(raw_kind_state,raw_kind_sha256)` to exact
`envelope_bytes`. Equal envelope shares a partition; equal state/digest with unequal
bytes is a collision and aborts before rename/manifest. It never overwrites,
first/last-wins, suffixes, or changes algorithm. Required tests distinguish missing
from null and `17`, `false`, `[]`, `{}`; classify `"Competition"` as safe unknown;
classify `"../action"` and `"a/b"` as distinct unsafe root-independent digests; and
prove every unknown occurs once in rejected reconciliation and zero times in known
records, rejected-field, Silver, and Gold.

`bronze.py` is sole serializer for known records and both quarantine families and
sole writer of `data/manifests/wyscout/v5/bronze/<build_id>.manifest.json`.

## 8. Conservative all-groups distribution and runtime closure

Admission requires the master already ran exactly
`uv sync --locked --all-groups` for this repository/interpreter. Admission is
read-only, offline, and pre-execution: it does not sync, resolve, install, download,
query an index, import third-party code, or execute a generated script. Its only pyc
opens are the bounded pre-rebuild magic/hash/size reads in Section 8.6; rebuild
itself reads zero pyc.

Distribution identity is PEP 503:

```text
normalize(name) =
  lowercase(collapse_each_maximal_run_of("-", "_", ".") to "-")
```

The stable target record binds implementation/full Python version, ABI and ordered
`packaging.tags.sys_tags()`, marker environment, platform fields, root-project
identity/source, sorted selected group names, `pyproject.toml` and `uv.lock` SHA-256,
and uv version plus physical executable SHA-256. The uv executable's resolved
absolute path is recorded only in the operational admission receipt; it is excluded
from stable environment, two-root, semantic, and build identity.

### 8.1 Exact lock closure `L`

The selected root is the unique lock package matching project normalized name/
version and exact editable `"."`; verify then exclude it from third parties.
All `[dependency-groups]` are selected: `data`, `e2e`, `lint-type`, `model`,
`orchestration`, `runtime`, `security`, and `test`. Sorted declared groups must equal
root locked dev-dependency keys and direct edges/specifiers. Production edges are
also selected if present. An extra is active only on an exact selected edge.

Recursively evaluate each marker against the frozen marker environment. True/
unmarked edges are followed; false omitted; exact selected extras activate their
optional edges. Unknown marker, error, ambiguous extra, or optional edge without
extra fails. Multiple same-normalized-name candidates must resolve by exact
source/version/marker to one; zero/multiple fails. Only supported registry sources
are allowed for third parties. Traverse to fixed point and sort by normalized name,
canonical version, source identity.

`L` contains normalized name/version/source, parent edges, extras, marker evidence,
selected wheel filename/tags, lock SHA-256/size. No AST/direct-import pruning occurs.

### 8.2 Compatible wheel selection

Parse all lock wheel filenames; name/version must match the selected member. A wheel
is compatible when a tag occurs in frozen ordered `sys_tags()`. Select the wheel
whose best tag has lowest sequence index; exactly one may occupy that rank. No
compatible wheel or tie fails; no sdist/local build fallback.

Bind filename, full declared tags, lock SHA-256/size, URL basename, and rank. URL is
metadata and never fetched. Reviewed mandatory examples are:

```text
pydantic-core 2.46.4
pydantic_core-2.46.4-cp312-cp312-macosx_11_0_arm64.whl

polars-runtime-32 1.43.0
polars_runtime_32-1.43.0-cp310-abi3-macosx_11_0_arm64.whl
```

ABI3 is accepted only by the same ordered tag test.

### 8.3 Installed equality `L == I`

Enumerate immediate `.dist-info` directories only under exact interpreter
`purelib`/`platlib`, both contained in `.venv`, non-symlink, and the only third-party
site roots in `sys.path`. Disable user site. A `.pth` is allowed only as verified
RECORD-owned non-executable path-only content; executable/external `.pth`, `.egg`,
and `.egg-info` fail.

Each RECORD-owned `METADATA` has exactly one valid Name/Version. Normalize Name and
canonicalize Version. Duplicate/malformed/nested/aliased identity fails. Verify the
editable project separately as `scouting-intelligence==0.1.0`, source `"."`, then
exclude it from third-party installed set `I`. No tooling/unused exception exists.

```text
{(name,version) in L} == {(name,version) in I}
```

Report sorted `lock_only`/`installed_only`; either non-empty fails. Require one-to-one
member/dist-info association.

### 8.4 Cache, extracted tree, install mapping, and base generated rows

For every `L` member derive exact:

```text
wheels-v5/pypi/<pep503-name>/
  <wheel-filename-with-distribution-prefix-and-.whl-removed>
```

It is one symlink. Record raw link text. Resolve once to one regular non-symlink
`archive-v0/<opaque>` directory in the same admitted cache root. Absolute raw link
text is permitted only if resolved containment is exact. Chains/dangling/escape/
ambiguous shared target fail.

Lock filename/hash/size and selector sidecars are operational association evidence.
Sidecars are not opened as wheel archives. If archive absent, record:

```text
original_wheel_archive_present = false
original_wheel_archive_hash_verified = false
```

Extracted RECORD paths are strict POSIX-relative, no absolute/`..`/duplicate/
symlink/directory/escape. Every non-self row has supported SHA-256 and size; self row
is empty. Physical extracted tree equals RECORD set. Hash every file and bind a
length-framed sorted extracted-tree digest.

Installed RECORD uses the same normal path rules except the one controlled generated
script scheme in Section 8.5. PEP 427 mapping handles root and
`.data/{purelib,platlib,scripts,headers,data}` to the exact environment schemes;
unsupported scheme, collision, overwrite, or escape fails. Every extracted payload
maps once and installed bytes equal extracted bytes.

Base installer-generated rows are exactly:

```text
<dist-info>/INSTALLER = b"uv"          # two bytes, no newline
<dist-info>/REQUESTED = b""            # empty
<dist-info>/RECORD                     # self row empty hash/size
```

Their installed RECORD hashes/sizes are exact. Other generated metadata is forbidden
except verified scripts and enumerated denied pyc below.

### 8.5 Exact uv-generated console/gui script rule

For each selected distribution, `entry_points.txt` is usable only when it is a
regular verified extracted RECORD member, maps byte-identically into installed
dist-info, and is parsed without importing the distribution. Decode strict UTF-8;
use INI syntax with no interpolation, duplicate section/key, continuation, comment
ambiguity, or unnamed value. Only `[console_scripts]` and `[gui_scripts]` generate
scripts. Other entry-point groups remain metadata and generate no executable.

Each selected entry is exactly:

```text
<safe-name> = <module-path>:<attribute>
```

`module-path` is dot-separated Python identifiers; `attribute` is one Python
identifier; extras, calls, whitespace-bearing names, duplicate names, and malformed
targets fail. `<safe-name>` is ASCII and matches
`[A-Za-z0-9][A-Za-z0-9._-]{0,127}`, is not `.` or `..`, contains no slash,
backslash, percent, control, or Unicode, and is unique under both exact bytes and
ASCII case-fold across all selected console/gui entries. Allowed script names are
derived only from this verified set.

On this POSIX environment each allowed entry generates exactly one regular,
non-symlink, single-owner file at:

```text
<exact-venv-scripts-directory>/<safe-name>
```

Its owning installed RECORD row is textually exactly
`../../../bin/<safe-name>`. This is the sole permitted RECORD path containing
`..`. It is parsed as a controlled environment-scheme path, never by generic path
normalization: append it to the owning dist-info directory, lexically normalize once,
resolve the parent directories, and require the result equal the exact scripts
directory plus the exact basename. Any other `../`, different depth/directory,
absolute path, alias, symlink, hardlink alias, collision, or unlisted script fails.

Actual mode is exactly `0o755`. Actual size and URL-safe unpadded SHA-256 must equal
the installed RECORD row. Actual bytes must be strict UTF-8/LF and equal this
reviewed uv POSIX template byte-for-byte:

```text
#!<absolute-admitted-sys.executable>\n
# -*- coding: utf-8 -*-\n
import sys\n
from <module-path> import <attribute>\n
if __name__ == "__main__":\n
    if sys.argv[0].endswith("-script.pyw"):\n
        sys.argv[0] = sys.argv[0][:-11]\n
    elif sys.argv[0].endswith(".exe"):\n
        sys.argv[0] = sys.argv[0][:-4]\n
    sys.exit(<attribute>())\n
```

The first line is exactly ASCII `#!`, the absolute `sys.executable` launch path of
the admitted `.venv` interpreter, and LF. No `/usr/bin/env`, alternate interpreter,
argument, CRLF, encoding variance, wrapper body, or target mismatch is accepted.
The remaining bytes are a deterministic function of the verified entry point and
are compared exactly. GUI entries use the same reviewed POSIX template in this
environment; platform change requires a newly reviewed template/selector.

Operational evidence records absolute script path, exact root-bearing bytes SHA-256,
size, mode, shebang bytes, RECORD row, owner, group/name/target, and verification.
Stable identity does not hide verification: after actual bytes pass, it replaces
only the exact verified first line with:

```text
#!<W04_VENV_PYTHON>\n
```

and retains every remaining byte unchanged. The stable script row binds distribution
identity, entry-point group/name/target, normalized bytes SHA-256/size, mode, and the
normalization algorithm version `w04-uv-script-normalization-v1`. Stable
environment/build/two-root identity uses those rows; operational receipts use actual
rows. Two roots must have equal stable rows and equal remaining bytes after the one
shebang substitution. Script reads and execution are denied from rebuild launch
through final recheck. Admission may read scripts only before that denial to verify
them. No other generated `bin` payload is allowed.

### 8.6 Pre-existing pyc enumeration, operational proof, and read denial

Pre-existing `__pycache__` and pyc are not a fatal admission condition and are not
deleted. Enumerate them beneath admitted site roots before rebuild. Each pyc must:

- be a regular non-symlink file at a safe contained
  `**/__pycache__/<source>.<current-cache-tag>[.opt-0|.opt-1|.opt-2].pyc` path;
- be accepted by `importlib.util.source_from_cache` and map to exactly one existing
  verified RECORD-owned `.py` in the same selected distribution;
- have exactly current `sys.implementation.cache_tag`;
- start with current `importlib.util.MAGIC_NUMBER`; and
- have exactly one owner and no hardlink/path alias.

Admission may open each pyc once only to verify magic/hash/size. Operational
inventory binds absolute and site-relative path, owner, source path/digest,
cache tag, optimization, actual physical SHA-256, size, mode, magic, and verification
result. Those possibly root-bearing pyc bytes, hashes, absolute paths, counts, and
inventory digest are operational evidence only and are excluded from semantic
products, stable environment identity, build ID, and two-root equality.

Stable identity instead binds algorithm
`w04-preexisting-pyc-enumerate-deny-v1`, current cache tag/magic, the no-cleanup
policy, and a sorted source map for every verified RECORD-owned `.py`:

```text
(distribution identity, RECORD source-relative path, source SHA-256/size,
 deterministic allowed cache-name grammar)
```

Thus the policy and source authority are stable without treating pyc bytes as code.

Before any rebuild interpreter/import starts, the external admitted launcher:

1. snapshots all existing in-place pyc/`__pycache__` paths and metadata;
2. creates/selects the exact staging `runtime-pycache/`, proves it empty, and sets
   absolute `PYTHONPYCACHEPREFIX` to it before interpreter start;
3. sets `PYTHONDONTWRITEBYTECODE=1` and launches the exact interpreter with `-B`;
4. activates an audit/guard rule denying open/read/mmap/execute/import of every
   in-place pyc and denying every generated script read/execute; and
5. after rebuild proves zero pyc/script read events, no new/changed/deleted in-place
   pyc or pycache path, and an empty alternate prefix.

Any unsafe/unowned/wrong-tag/wrong-magic pyc, pyc read, generated-script read or
execution, new/changed bytecode, or non-empty alternate prefix fails. This restores
R6's truthful enumerate-and-deny behavior without destructive cleanup.

### 8.7 RECORD ownership and runtime subset

Installed RECORD is ownership authority; `top_level.txt`,
`packages_distributions()`, names, and AST imports are advisory. Every concrete
normalized installed file has one owner. A normal import root has one owner.
Namespace sharing is allowed only with no contributor-owned `__init__.py`, contained
search locations, singular concrete child ownership, and no overlapping child.
Extension modules are parsed against complete frozen `EXTENSION_SUFFIXES`; native
origin is exact RECORD-owned. Site-root shared libraries require singular owner;
system/interpreter libraries use the separate interpreter closure.

Only after `L`, `I`, extracted/installed/script policy, pyc policy/source map,
interpreter/resources, and ownership freeze may W04 execute. An observer records
third-party module origins, namespace search locations, extensions, site-root shared
images, and owners. Every origin is pre-admitted and unchanged.

Let `R` be actual loaded owners:

```text
R subset-of L
```

`R` is post-execution receipt/health evidence, not selection or build input. It
cannot add, rescan, retry, or expand. Equal two-root runs require equal normalized
origin/owner observations. Positive proofs include
`pydantic -> pydantic-core` and `polars -> polars-runtime-32`; both dependencies are
in `L` before execution and native owners appear in `R` if loaded. Duplicate
concrete owner, ambiguous normal/namespace/native ownership, installed-only/
lock-only distribution, external origin, or dynamic import outside `L` fails.

### 8.8 Repository, interpreter, stdlib, environment, and recheck

Repository selection is an exact repo-relative allowlisted manifest after code
freeze. AST traversal proves local import coverage but does not choose
distributions. Symlink/escape/duplicate/dynamic path code/sys.path mutation/
writable code/repository native extension fails.

The interpreter closure binds exact `.venv` launch identity, implementation/full
version, ABI, physical executable SHA-256/size/mode, loaded libpython and loader
images. Stable identity contains the interpreter-relative identity/digests, not a
project-root prefix. Standard-library roots derive from that interpreter, exclude
site-packages and operational pyc, and hash exact regular file bytes. Imports
outside repo, `L` ownership, stdlib, built-in/frozen, or admitted loader/system
paths fail.

Environment variables use a fixed allowlist and canonical values; unknown
behavior-affecting variables fail. Locale, timezone, hash seed, bytecode, and thread
controls are fixed. Network/provider interfaces are disabled. Before every output
rename and manifest write, code, `L==I`, extracted/installed actual bytes, scripts,
pyc no-read/no-change state, interpreter, stdlib, environment, and 17 resources are
rechecked.

### 8.9 Exact stable code/environment manifest

The admitted environment has two truth domains:

```text
stable code/environment manifest:
  repo-relative code bytes and import-coverage proof
  pyproject/lock digests and selected L
  wheel declarations and stable selector keys
  verified extracted-tree and installed RECORD-owned bytes
  exact INSTALLER/REQUESTED rows
  normalized uv-script rows
  stable pyc policy/source map
  uv version and physical executable digest
  interpreter/libpython/loader and stdlib stable digests
  exact 17-resource digest
  canonical environment values

operational admission evidence:
  actual resolved uv executable path
  actual cache root, symlink text and archive-v0 opaque target
  actual root-bearing generated-script paths/bytes/hashes
  actual pyc paths/bytes/hashes/counts/modes
  admission observations and no-read/no-change audit
```

The stable manifest algorithm is `w04-code-environment-admission-v5`. Component
digests are length-framed, sorted by declared stable key, and combined exactly as:

```text
environment_digest = SHA256(canonical_json({
  "selector": <frozen Python/platform/ordered-tag selector>,
  "lock_inputs_digest": <pyproject-plus-uv-lock digest>,
  "selected_lock_closure_digest": <complete L digest>,
  "wheel_declaration_digest": <selected declarations digest>,
  "extracted_runtime_digest": <all verified extracted trees>,
  "installed_record_runtime_digest": <mapped RECORD-owned/base generated bytes>,
  "normalized_script_digest": <reviewed stable script rows>,
  "pyc_policy_source_map_digest": <stable policy/source map>,
  "uv_version": <exact version>,
  "uv_physical_sha256": <exact executable bytes digest>,
  "interpreter_digest": <stable interpreter/libpython/loader closure>,
  "stdlib_digest": <exact standard-library bytes>,
  "local_resource_digest": <exact 17-path resource set>,
  "environment_values_digest": <fixed canonical allowlist>
}))
```

It contains no own ID/path, clock, actor, Git state, run ID, output digest, uv
absolute path, cache absolute path, actual script path/hash, or actual pyc path/hash.
Its identity and sole path are:

```text
code_manifest_sha256 = SHA256(canonical_manifest_bytes)
code_manifest_id = UUIDv5(
  w04_dependency_namespace,
  "post_integration_code_environment_manifest:" + code_manifest_sha256)
data/manifests/wyscout/v5/code/
  <code_manifest_sha256>.code-manifest.json
```

Independent review reproduces the complete manifest from admitted bytes. Negative
tests cover lock/tag selection drift, cache link/target/tree/RECORD drift, false
wheel-ZIP claims, installed payload/RECORD/base-row drift, script target/body/
shebang/mode/normalization drift, unsafe/read pyc, interpreter/libpython/stdlib/
resource drift, behavior-environment drift, and early build-ID formation.

## 9. Build identity, deterministic bytes, and two-root proof

Canonical build-input version is `w04-wyscout-build-id-v6`. It contains:

- tenant and exact source manifest;
- identity bundle/queue/ruleset/accepted corrections;
- field, possession, feature, and identity decision/review/acceptance IDs/digests;
- all product schemas, exact keys, Gold coverage equations, and neutral context;
- exact window/cutoff values and the five strict dependencies;
- repository code manifest and `pyproject.toml`/`uv.lock` digests;
- selected all-groups `L`, wheel declarations, stable selector associations,
  extracted trees, installed RECORD-owned bytes/base rows;
- stable normalized uv-script rows and pyc policy/source map, never operational
  root-bearing script or pyc bytes;
- uv version and physical executable digest, never uv absolute path;
- interpreter/libpython/loader and standard-library stable digests;
- exact 17 local resources and fixed environment.

```text
build_id = SHA256(canonical_json(all stable semantic build-input fields))
```

Runtime `R`, root-bearing script paths/bytes, actual pyc inventory/bytes, uv absolute
path, cache absolute root/opaque key, run ID, output root, host clocks, Git
branch/tag/commit, absent wheel archive bytes, and output digests are excluded.
Missing acceptance, placeholder, unverified member, mismatch, or pre-closure call
makes build identity unavailable.

Parquet is version 2.6; one `part-00000.parquet` per logical partition; row group
65,536; zstd 9; data page 2.0; dictionary and byte-stream split off; statistics on;
page index off; timestamp microseconds without truncation; stored schema. Rows use
canonical UUID/UTC/Decimal/null/list forms and full primary-key order. Semantic
digests cover schema, length-framed ordered rows, and parents; physical digests
cover exact bytes.

Two-root review uses two distinct empty absolute project roots, same manifested
source and admitted environment. It removes only explicitly operational root
prefixes and requires equal:

- relative product/manifest paths, schemas, rows, semantic/physical digests;
- source/identity/authority/strict temporal evidence and build ID;
- `L==I`, wheel selection, extracted/installed stable ownership;
- normalized uv-script rows with byte-identical bodies after exact shebang token;
- stable pyc policy/source map (not actual pyc bytes/inventory);
- resources/interpreter/stdlib/environment stable evidence;
- unknown-kind paths, states, envelope bytes, and digests; and
- normalized runtime origin/owner observations.

Operational run IDs/clocks, uv absolute path, actual root-bearing script path/hash,
and actual pyc inventory may differ only in their documented operational fields.
They never leak into stable identity.

## 10. Quality, health, card, gate, and serial ownership

Quality requires exact source counts/country equalities, unique match/action IDs,
two teams per match, zero match/team conflicts, 226,038 zero actors, measured
lineup/bench/substitution counts, 23/8 unresolved references, period/coordinate
constraints, accepted authorities, exactly five strict dependencies, neutral
result-independent facts, zero minute/per-90 output, separate source and Gold
coverage equations, complete all-groups environment, script/pyc denial, exact
resources, sole writers, quarantine reconciliation, and two-root equality.

Health outputs are:

```text
reports/phase-gates/W04/data-health.json
reports/phase-gates/W04/data-health.md
```

Controlling JSON includes source and Gold coverage separately; source/identity/
temporal/rights metrics; backlog/corrections; rejected field/record counts; unknown
states/digests/collision status; `L`, `I`, `L==I`; wheel/cache/extracted/installed
evidence; actual and normalized generated-script evidence; operational pyc inventory
and zero-read/no-change proof; loaded subset `R`; uv/interpreter/stdlib/resources;
path ownership; and two-root equality.

Card/review are:

```text
docs/dataset-cards/w04-wyscout-transformed-v1.md
reports/reviews/W04/wyscout-transformed-dataset-card-independent-review-R1.md
```

The card binds build/layer/health digests and covers intended/excluded use,
population/coverage, correction policy, transformations, supported/suppressed
features, time/minute limitation, coordinate/semantic bias, rights/attribution, and
offline reproduction. Independent review cannot edit it.

`G-W04` passes only when one manifested input deterministically rebuilds Gold and all
identity, reconciliation, strict temporal, rights, guarded-root, environment,
script/bytecode, quarantine, manifest, card, independent-review, resource, and
exact-path checks pass. No report is accepted until each independent recommendation
is `PASS`.

Sole ownership is serial. Authority candidates/reviews/acceptances have distinct
owners. Bronze owns known records and both quarantines. Identity owns only its three
generated roots. Entity/action/lineup/possession/player-match Silver owners write
only named families; Silver manifest is separate. Gold/temporal owns Gold, Gold
manifest, boundary receipts. Rebuild only invokes and writes invocation receipt.
Admission owns admission code/report and immutable code/environment manifest.
Quality, health, card/reviews, master verification, gate, acceptance Git, and ledger
are later serial owners. Only disjoint Silver families may overlap.

This graph covers W04.1–W04.7 and P2.1–P2.9: source/rights, Bronze, four-kind
identity, every Silver product, temporal state, feature registry, neutral Gold,
health, card, independent rebuild, and `G-W04`.

The ownership-complete sequence is exact; `return` always means
`reports/reviews/W04/returns/<packet-id>.md`:

| # | Exact owner/packet class | Sole output responsibility | Coverage/dependency |
| ---: | --- | --- | --- |
| 1 | accepted source/master | existing source card/profile | W04.1/P2.1 |
| 2–4 | field decision/review/accept packets | four exact Section 4.1 field artifacts, tests, returns | before Bronze |
| 5–7 | possession decision/review/accept packets | four exact Section 4.1 possession artifacts, tests, returns | before possession |
| 8–10 | identity decision/review/accept packets | four exact Section 4.2 authority artifacts, tests, returns | W04.3/P2.3 |
| 11 | `W04-DATA-CONTRACTS-01-R1` / master | W04 contract/tests/return; existing evidence unchanged | W04.2–W04.6 |
| 12 | manifest bridge/source owner | bridge, test, exact source manifest, return | sole source-manifest writer |
| 13 | Bronze owner | `bronze.py`, test, exact records/quarantine/staging families, Bronze manifest | W04.2/W04.4/P2.2 |
| 14 | identity runtime owner | identity module/test and exact three generated identity families | W04.3/P2.3 |
| 14C | correction master/reviewer/master | exact decision/review/acceptance artifacts/returns | conditional authority |
| 14D | identity runtime owner | one normalized correction, route-specific queue behavior, new bundle | after accepted 14C |
| 15A | entity owner | competition/team/player/match Silver families | W04.4/P2.4 |
| 15B | action owner | action Silver family | W04.4/P2.4 |
| 15C | lineup owner | lineup-stint Silver family | W04.4/P2.4 |
| 16 | possession owner | possession Silver family | after action |
| 17 | player-match owner | player-match-fact Silver family | after all Silver inputs |
| 18 | Silver manifest owner | exact Silver manifest only | after all Silver serializers |
| 19 | `W04-FEATURE-REGISTRY-DECISION-01-R1` / master | feature decision, registry, contract test, return | P2.6 |
| 19R | `W04-FEATURE-REGISTRY-REVIEW-01-R1` / independent | exact feature independent review/return | candidate read-only |
| 19A | `W04-FEATURE-REGISTRY-ACCEPT-01-R1` / master | exact feature acceptance/return | Gold blocked until accepted |
| 20 | Gold/temporal owner | Gold/temporal modules/tests, exact Gold/staging/manifest/boundary families | W04.5/P2.5/P2.7 |
| 21 | quality owner | quality module/tests | W04.6/P2.8 |
| 22 | admission implementer/master | admission module/script/tests including L==I, scripts, pyc | offline algorithm only |
| 23 | rebuild entrypoint/master | rebuild module/script/integration test, invocation receipt only | calls sole writers |
| 24 | shared integration/master | named shared exports only | serial |
| 25 | code-manifest admit/master | exact code manifest and admission report/return | after code freeze |
| 26 | code-manifest independent reviewer | exact independent review/return | reproduces bytes/digests |
| 27 | two-root invocation/master | two run families and rebuild evidence report/return | no broad product write grant |
| 28 | health owner | exact JSON/Markdown health/return | P2.8 |
| 29 | card author/master | exact transformed card/return | P2.9 |
| 30 | card independent reviewer | exact card review/return | W04.7 |
| 31 | rebuild independent reviewer | leakage test, exact rebuild review/return | W04.7 |
| 32 | master verifier | raw-to-Gold verification, verification report, pre-ledger candidate evidence | W04.7 |
| 33 | master gate | master review, acceptance report, gate report | full `G-W04` |
| 34 | master local Git authority | acceptance integration commit and annotated tag | only after full gate |
| 35 | master ledger authority | registry checkpoint mutation plus clean-tree proof, separate commit | after accepted tag |

Master/gate output paths are exact:

```text
reports/verification/W04/wyscout-raw-to-gold-R1-master-verification.md
reports/verification/W04/verification-report.md
reports/verification/W04/clean-tree-report.md
reports/verification/W04/phase-verifier-candidate.json
reports/reviews/W04/master-review.md
reports/phase-gates/W04/acceptance-report.md
reports/phase-gates/W04/gate-report.json
```

`gate-report.json` is controlling machine evidence. Row 27 invokes serializers and
owns run receipts/evidence only; it does not own
`data/working/wyscout/v5/**`. No directory shorthand grants another family.

## 11. Controlling two-local-commit acceptance ledger

The exact order is:

1. Master completes implementation/readback, independent reviews, candidate
   verification, machine gate, and acceptance rendering. Full `G-W04` passes while
   registry remains pre-checkpoint.
2. Master creates local integration commit `C_accept` with exact message
   `phase(w04): accept governed data spine`.
3. Master creates immutable annotated tag `checkpoint/w04-accepted` exactly on
   `C_accept`.
4. Master resolves `C_accept` from tag and writes registry W04 state/checkpoint,
   exact SHA/tag/message, gate/acceptance paths/digests, and evidence paths. Registry
   contains no ledger commit SHA.
5. Master writes `reports/verification/W04/clean-tree-report.md` as a predicate
   certificate naming only the registry and itself as ledger paths. It records
   commands/results proving no unstaged/untracked path, empty remote, active guard,
   and index/worktree equality. It has no self digest/tree hash/future commit SHA.
6. After staging exactly those two paths and repeating predicates, master creates
   one local commit with exact message
   `orchestration(w04): record accepted checkpoint ledger`.
7. Master runs final read-only clean-tree, remote, guard, registry, and local-only
   verification. Empty output is required and nothing is rewritten.

Tag names accepted integration; later `HEAD` is ledger commit. Registry-before-tag
cycles, self hashes, tag movement, third cleanup commit, waiver, stash/reset/history
rewrite are forbidden.

## 12. Required positive/negative tests and closure

Required tests retain all R5/R6 source, rights, field/possession/feature authority,
identity lifecycle/correction, five-dependency, period-relative football, exact key,
Gold coverage, minute suppression, path/serializer, atomic publication,
interpreter/stdlib/resource, card/gate, two-root, and two-commit ledger checks, plus:

1. Map each exact completion path to the exact envelope kind. Prove payload `kind`
   and payload shape never select family. Exercise envelope discriminator
   missing/null/boolean/number/array/object/safe unknown/unsafe unknown.
2. Prove unknown state/value preservation, distinct missing/null/typed values,
   root-safe full digests, collision abort before rename, and zero unknown leakage.
3. Assert known Bronze literal `records/record_kind=...`, exact player-match key,
   exact Gold key, and required non-key `feature_schema_hash`.
4. Assert source `DataCoverage` six dimensions are unchanged and Gold coverage is a
   separate six-dimensional integer contract with exact zero/minimum/applicability.
5. Reject every dependency/authority observed, reviewed, accepted, corrected,
   available, or watermark clock equal to cutoff, as well as after cutoff.
6. Select all groups, explicit extras, marker-active recursive edges; reject group
   mismatch, ambiguous candidates, unsupported source, sdist fallback, wheel tie.
7. Require normalized exact `L==I`; reject either difference, duplicate/malformed
   metadata, egg, external site root, executable `.pth`.
8. For every `L` member verify selector containment, extracted RECORD/tree,
   installation mapping, `INSTALLER=b"uv"`, empty `REQUESTED`, and rewritten RECORD.
9. From verified `entry_points.txt`, derive all/only safe console/gui scripts;
   accept only controlled `../../../bin/<safe-name>` resolving to exact scripts
   root; verify target/body/shebang/hash/size/mode/owner; reject all other bin rows.
10. Prove actual script paths/bytes are operational, reviewed normalization is stable
    across two roots, remaining bytes are exact, and rebuild reads/executes none.
11. Enumerate pre-existing pyc without cleanup; reject unsafe/unowned/wrong-tag/
    wrong-magic; bind operational hashes and stable policy/source map; prove `-B`,
    `PYTHONDONTWRITEBYTECODE=1`, early alternate prefix, zero reads/changes/new files,
    and empty alternate prefix.
12. Prove uv version/physical digest stable while its absolute path is operational
    only; assert the exact 17 resources and disjoint guard categories.
13. Prove `pydantic -> pydantic-core` and `polars -> polars-runtime-32`, native
    ownership, `R subset-of L`, and no runtime expansion/retry.
14. Reject duplicate file/package/namespace/native ownership, mutation after freeze,
    extra read/write, broad resource discovery, writer overlap, or serializer bypass.

Stop rather than improvise if a path/digest/count/lock/installed set changes; a
truthful clock/authority is missing; unknown kind would be guessed; payload would
select family; excluded/source path would be read; action UTC/minutes would be
fabricated; absent wheel would be claimed verified; scripts/pyc cannot satisfy the
exact rules; ownership is ambiguous; runtime wants an unselected distribution; a
collision would mutate a path; writers overlap; or dependency, lock, cleanup,
migration, provider, network, rights, architecture, local-only, ignore, remote,
storage-root, or deployment change is needed.

R8 closes the returned P1/P2 findings without self-approval. Implementation begins
only after master and a separate independent reviewer accept this standalone design.

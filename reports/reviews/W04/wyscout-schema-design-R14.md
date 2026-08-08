# W04 Wyscout v5 canonical schema and deterministic rebuild design — R14

Status: **implementation design for master and independent review; not self-approved**

This document replaces R13 in full. It is the standalone design for the local-only
W04 Wyscout Figshare v5 Bronze-to-Gold proof. R14 retains every accepted R13, R12,
and earlier closure without compression or substitution: all source, rights, temporal,
identity, football-product, coverage, quarantine, path, serializer, environment,
resource, exact executable/alias/bytecode census, gate, ownership, two-root, and
two-commit ledger contracts remain binding. It closes only the returned R13 master
findings: an acyclic bootstrap-environment digest graph; exhaustive, closed
admission/rebuild child input contracts; one exact canonical rebuild transport;
manifest/build-ID-before-rebuild-prefix chronology; and a truthful bounded R14
scope attestation. The R13 encoding-source, descriptor/race, result-v2, exact argv,
58/19-plus-four-predicate pyc, 35-executable, three-alias, three-`.pth`, and
17-resource closures remain unchanged. It changes no architecture,
provider, rights, dependency, lock, migration, network, storage-root, ignore,
remote, deployment, product writer, or child argv.

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
   all-groups lock closure, verified extracted and installed bytes, the reviewed
   total executable census and its root normalization, no-site/bootstrap evidence,
   interpreter/libpython, standard library, exact local resources, schemas, and
   source/identity/authority evidence.
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

After build identity exists, each serializer stages only under the rebuild-process
prefix:

```text
data/working/wyscout/v5/.staging/<build_id>/<run_id>/
  bronze/<same final suffix>.partial
  silver/<product>/<same final suffix>.partial
  gold/<same final suffix>.partial
  runtime-pycache/
```

`<build_id>` is already frozen before this tree is created. This tree is never the
stage-0 admission tree. Pre-build admission uses only the separate exact prefix in
Section 8.0, which contains no build ID and no serializer partials. Substituting the
rebuild tree during stage 0 is an ordering failure.

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
`uv sync --locked --all-groups` for this repository/interpreter. Admission remains
read-only and offline: it does not sync, resolve, install, download, query an index,
execute generated code, execute a `.pth`, call a site helper, or clean the
environment. The constructive runtime has exactly three Python roles, in order:

1. outer `W04_LOCAL_CONTROL`;
2. child `PRE_BUILD_ADMISSION`; and
3. child `POST_BUILD_ID_REBUILD`.

The two child argv remain byte-for-byte unchanged. The outer argv also remains
byte-for-byte unchanged. Each role has its own fresh empty alternate bytecode
prefix. “Three Python roles” does not count the non-Python master invocation owner
or any `uv` transport/wait process. No third product-writing Python process exists:
only the rebuild child may invoke the already named product writers.

The exact startup claim is intentionally narrower than “nothing file-backed runs
before the guard.” CPython 3.12.12 opens the launcher source and preloads three
file-backed encoding modules before user code. The launcher audit hook cannot and
does not claim to observe those earlier operations. With the selected empty control
prefix, the three modules are loaded from the exact source rows below instead of
their installed pycs; `-B` prevents an alternate-cache write. After the first
user-code verifier and hook installation, every further file-backed import/open is
subject to the admitted guard.

### 8.0 Constructive three-role no-site startup and compatible-tag bootstrap

The three exact prefix forms and owners are:

| order | role | sole sampler/creator | exact relative prefix |
|---:|---|---|---|
| 1 | `W04_LOCAL_CONTROL` | master invocation trust-root owner | `data/working/wyscout/v5/.staging/control/control_run_id=<uuid>/runtime-pycache/` |
| 2 | `PRE_BUILD_ADMISSION` | admitted launcher | `data/working/wyscout/v5/.staging/admission/admission_run_id=<uuid>/runtime-pycache/` |
| 3 | `POST_BUILD_ID_REBUILD` | admitted launcher | `data/working/wyscout/v5/.staging/<build_id>/<run_id>/runtime-pycache/` |

Every `<uuid>` is the canonical lowercase representation of 16 fresh OS-CSPRNG
bytes with UUID version 4 and RFC 4122 variant bits. Control, admission, and rebuild
UUIDs are distinct. Each creator resolves the already approved staging parent with
contained directory descriptors; rejects a link, alias, `.`/`..`, hard-linked
non-directory component, unexpected mode/owner, pre-existing selected leaf, escape,
or any entry; creates only the required components; and proves the leaf empty by a
descriptor-relative enumeration before the associated `uv` process exists. The
creator records the parent/leaf identities and an empty inventory digest. After
that role exits it repeats `lstat`/`fstat`, containment, identity, and empty
enumeration and requires the same directory and empty digest. No prefix, pyc, or
directory is deleted, truncated, moved, or “repaired.”

All three UUIDs, absolute paths, device/inode values, clocks, and empty-inventory
observations are operational. The policy `w04-three-role-runtime-pycache-v1`, the
three roles, order, distinctness, path templates, empty-before/unchanged-after
rules, `PYTHONDONTWRITEBYTECODE="1"`, and `-B` are stable environment/build
authority.

#### 8.0.1 Outer control prefix, exact encoding-source bootstrap, and unchanged argv

The master invocation trust-root owner alone performs the following ordered
prelaunch transaction:

1. verifies the accepted repository root, exact `uv` and Python 3.12.12 physical
   rows, exact outer argv, fixed environment, accepted launcher tuple, and launcher
   descriptor contract in Section 8.0.2;
2. samples `control_run_id`, safely creates the exact control prefix above, proves
   it empty, and converts only that reviewed contained leaf to an absolute spelling;
3. sets `PYTHONPYCACHEPREFIX` to that absolute spelling and
   `PYTHONDONTWRITEBYTECODE` to exactly `"1"` before any `uv` or outer Python
   process exists; and
4. launches from the accepted repository root exactly:

   ```text
   uv run --locked --no-sync python -S -B scripts/launch_wyscout_v5.py
   ```

Missing, extra, reordered, duplicated, or substituted tokens; plain `uv run`;
another working directory; site startup; sync; generated/wrapper/module execution;
another prefix; or a second launcher fails. The outer prefix is never absent and is
not an admission or rebuild prefix.

The interpreter-bootstrap authority contains these three exact standard-library
source rows, relative to the independently admitted Python 3.12.12 standard-library
root:

| module | exact source row | bytes | SHA-256 |
|---|---|---:|---|
| `encodings` | `encodings/__init__.py` | 5,884 | `78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8` |
| `encodings.aliases` | `encodings/aliases.py` | 15,677 | `6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2` |
| `encodings.utf_8` | `encodings/utf_8.py` | 1,005 | `ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d` |

The rows require contained regular non-link sources, the exact admitted stdlib
mode/owner, size, complete bytes, and digest. Their installed `__pycache__` files
remain classified operational bytecode and are neither removed nor read.

For this exact CPython 3.12.12 launch, the empty control prefix changes the cache
candidate away from each installed stdlib pyc. The interpreter finds no alternate
cache file and loads the exact source row. `-B` and
`PYTHONDONTWRITEBYTECODE="1"` prohibit writing the candidate. The master positive
test must trace/reproduce all three source opens, zero installed-pyc opens for
them, and zero control-prefix writes, then prove the prefix still empty. If a
future interpreter, `uv`, platform, or launcher cannot reproduce that observation,
W04 stops; it never deletes installed pycs, disables the source comparison, or
weakens bytecode denial.

The first executed user-code statement enters an inline, review-frozen bootstrap
verifier. Before any import that could resolve to another file-backed module, it
may obtain only already resident built-in/frozen `sys`, `posix`, and `_io`
capabilities. An embedded, separately tested SHA-256 implementation in the accepted
launcher bytes performs hashing without importing `hashlib` or any other
file-backed module. The verifier:

- requires exactly the three names above in `sys.modules`;
- requires each `__spec__.origin` and `__file__` to be the corresponding contained
  source row, never an installed or alternate pyc;
- requires any `__cached__` spelling to point under the selected control prefix and
  requires that candidate absent;
- no-follow reads each exact source through its admitted stdlib parent, requires
  exact EOF, size, and digest; and
- performs the inherited launcher-source descriptor comparison below.

Using only the same inline built-in/frozen facilities, it also decodes the exact
canonical bootstrap tuple with its embedded base64url decoder and compares role,
working directory, `sys.orig_argv`/ordered argv, fixed transport environment,
control-prefix spelling, and interpreter identity fields that require no new file
open. Only after all comparisons pass does the launcher install its
audit/open/import guard. Under that installed guard it performs the remaining
file-backed uv/interpreter/stdlib/repository checks and imports further
standard-library or project code under the existing closure. The guard evidence
begins at installation. Reports call the earlier encoding-source, launcher-
descriptor, and tuple-transport reads **pre-guard verified bootstrap reads**, never
audit observations.

At outer exit, after launcher status and all postchecks, the master proves the same
control leaf is still contained, identical, and empty with the same inventory
digest, without cleanup. A nonempty, replaced, missing, written, reused, or changed
control prefix fails all manifest/build authority.

#### 8.0.2 Master-opened launcher-source descriptor and bootstrap trust

The exact future launcher remains:

```text
scripts/launch_wyscout_v5.py
```

Its role is exactly `W04_LOCAL_CONTROL`; this design names but does not create it.
The accepted `w04-local-control-bootstrap-v2` tuple is exactly:

```text
process_role = W04_LOCAL_CONTROL
working_directory = <W04_PROJECT_ROOT>
ordered_argv =
  ["uv","run","--locked","--no-sync","python","-S","-B",
   "scripts/launch_wyscout_v5.py"]
uv_version = "uv 0.9.21 (Homebrew 2025-12-30)"
uv_physical_mode = 0o555
uv_physical_size = 41617552
uv_physical_sha256 =
  4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
python_version = 3.12.12
python_physical_mode = 0o755
python_physical_size = 49968
python_physical_sha256 =
  cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79
launcher_relative_path = scripts/launch_wyscout_v5.py
launcher_mode = 0o644
launcher_size = exact future accepted byte length
launcher_sha256 = SHA256(exact future accepted launcher bytes)
fixed_environment_algorithm = "w04-outer-environment-bootstrap-v1"
fixed_environment_digest =
  SHA256(canonical normalized base-environment object before tuple insertion)
pyproject_sha256
uv_lock_sha256
control_prefix_policy = "w04-three-role-runtime-pycache-v1"
control_prefix_relative_template =
  "data/working/wyscout/v5/.staging/control/control_run_id=<uuid>/runtime-pycache/"
encoding_source_rows = the exact ordered three-row table in Section 8.0.1
launcher_source_descriptor_policy = "w04-inherited-source-fd-v1"
```

No placeholder size/digest is executable authority. Bytes, digest, relative path,
mode, link count, and role are stable. Descriptor number, device, inode,
root-bearing spelling, and open/close clocks are operational.

Before prefix creation, the master resolves the exact launcher beneath a still-open
repository-root directory descriptor, performs contained `lstat`, then opens once
with `O_RDONLY|O_NOFOLLOW` (and `O_CLOEXEC` while it verifies). It requires one
regular non-symlink, non-hardlink-aliased mode-`0o644` file with `st_nlink==1`,
exact accepted size and bytes/digest, and `lstat`/`fstat` device/inode/mode/link/
size equality. It hashes with descriptor-relative positional reads, requires exact
EOF, and leaves the shared open-file-description position at `0`.

The master chooses a nonstandard descriptor integer greater than `2`, sets it
inheritable and therefore clears `FD_CLOEXEC`, verifies both facts, and encodes its
canonical strict decimal spelling in exactly:

```text
W04_LAUNCHER_SOURCE_FD=<digits>
```

The grammar is `(?:[3-9]|[1-9][0-9]+)` with no sign, space, leading zero, suffix,
duplicate assignment, or value above `2147483647`. It sets
`close_fds=true`/the platform-equivalent and passes exactly that descriptor through
the `uv` launch. Standard descriptors `0`, `1`, and `2` plus this one launcher
descriptor are the only descriptors admitted at the first outer Python
instruction. The required implementation test positively demonstrates preservation
through the exact `uv run --locked --no-sync python -S -B ...` path, including
equal `fstat`, offset `0`, inheritable true, and `FD_CLOEXEC` clear in outer Python.
A direct-python test is insufficient. There is no reopen-by-path or copied-bytes
fallback.

After successful process creation the master closes only its parent duplicate and
transfers logical ownership of the inherited Python-side descriptor to the
launcher. An implementation-internal `uv` transport duplicate is not authority and
must not alter offset or bytes; it disappears with that transport. The launcher is
the sole logical close owner of its inherited descriptor and keeps it open through
both children, both result/diagnostic EOFs, both reaps, all launcher/path/pyc/prefix
postchecks, and final master-facing status construction.

As part of the first user-code verifier, the launcher parses the environment value
without a helper import; requires the descriptor open, nonstandard, inheritable,
and `FD_CLOEXEC` clear; compares `fstat` to the accepted row; requires offset `0`;
positionally reads exactly the accepted size plus EOF; computes the embedded
digest; and again requires offset `0`. It enumerates inherited descriptors and
fails any extra nonstandard descriptor. Missing, closed, substituted, duplicated,
extra-inherited, non-preserved, nonregular, linked, wrong-position, unequal, or
path-reopened authority fails before a UUID, child, manifest, or build ID. It
then sets this retained launcher descriptor noninheritable and therefore restores
`FD_CLOEXEC`, verifies both states, and leaves it open in the launcher. Each child
spawn uses `close_fds=true`/the platform equivalent and an exact pass set containing
only that child's entrypoint source and result writer; the launcher descriptor is
not inherited into either child. The launcher repeats its descriptor
`fstat`/positional bytes/digest after each child and immediately before closing it
exactly once at final launcher exit.

The accepted tuple remains independently frozen by master plus independent review.
Stage 0 includes the exact stable launcher row and the two new stable bootstrap
policies in the canonical code/environment manifest. Operational descriptor
observations never enter stable identity.

The outer launch environment and its digest construction are closed by
`w04-outer-environment-bootstrap-v1`. The master constructs an exact string-to-
string map `E_outer_base` which does **not** contain
`W04_BOOTSTRAP_TUPLE_B64`. Its stable literal entries are exactly:

```text
ARROW_NUM_THREADS = "1"
LANG = "C"
LC_ALL = "C"
MKL_NUM_THREADS = "1"
NUMEXPR_NUM_THREADS = "1"
OMP_NUM_THREADS = "1"
OPENBLAS_NUM_THREADS = "1"
POLARS_MAX_THREADS = "1"
PYTHONDONTWRITEBYTECODE = "1"
PYTHONHASHSEED = "0"
PYTHONIOENCODING = "utf-8:strict"
PYTHONNOUSERSITE = "1"
PYTHONUTF8 = "1"
RAYON_NUM_THREADS = "1"
TZ = "UTC"
UV_LOCKED = "1"
UV_NO_SYNC = "1"
UV_OFFLINE = "1"
UV_RUN_RECURSION_DEPTH = "1"
VECLIB_MAXIMUM_THREADS = "1"
```

Its operationally substituted entries are exactly:

```text
HOME = <actual accepted account home>; stable token <W04_HOME>
PATH = <actual accepted executable path>; stable token
  <W04_VENV_BIN>:<W04_UV_BIN_DIR>:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONPYCACHEPREFIX = <absolute reviewed control prefix>; stable token
  <CONTROL_PREFIX>
TMPDIR = <actual accepted local temporary root>; stable token <W04_TMPDIR>
UV_CACHE_DIR = <actual admitted uv cache root>; stable token <W04_UV_CACHE_ROOT>
UV = <actual resolved admitted uv physical path>; stable token
  <W04_UV_PHYSICAL_PATH>
VIRTUAL_ENV = <absolute project-root>/.venv; stable token
  <W04_PROJECT_ROOT>/.venv
W04_LAUNCHER_SOURCE_FD = <strict decimal inherited descriptor>; stable token
  <LAUNCHER_SOURCE_FD>
__CF_USER_TEXT_ENCODING = <actual accepted macOS encoding marker>; stable token
  <W04_CF_USER_TEXT_ENCODING>
```

These are the actual values at the outer Python first instruction, not an
unexamined assumption that `uv` preserves its input environment. The master's
exact `uv`-input map uses `UV_RUN_RECURSION_DEPTH="0"` and a `PATH` whose first
component is `<W04_UV_BIN_DIR>` (not the venv bin); it explicitly sets the accepted
`UV` and `__CF_USER_TEXT_ENCODING` actual values. The admitted uv 0.9.21
transformation must overwrite `UV` with its resolved physical spelling, increment
the depth to `"1"`, and prepend exactly `<W04_PROJECT_ROOT>/.venv/bin:` to `PATH`,
leaving every other value byte-identical. The master computes the expected
outer-Python map from that exact transformation. Any extra uv mutation, duplicate
venv prefix, different depth, absent/changed macOS marker, or changed `UV` path
fails before trusting the tuple. This transformation algorithm and its positive
exact-uv test are stable authority; the two root-bearing actual values remain
operational.

Before tuple insertion, the following names are explicitly absent:

```text
ALL_PROXY
COVERAGE_PROCESS_CONFIG
COVERAGE_PROCESS_START
DYLD_FALLBACK_FRAMEWORK_PATH
DYLD_FALLBACK_LIBRARY_PATH
DYLD_FRAMEWORK_PATH
DYLD_INSERT_LIBRARIES
DYLD_LIBRARY_PATH
HTTP_PROXY
HTTPS_PROXY
LD_LIBRARY_PATH
LD_PRELOAD
NO_PROXY
PYTHONBREAKPOINT
PYTHONHOME
PYTHONINSPECT
PYTHONOPTIMIZE
PYTHONPATH
PYTHONSTARTUP
PYTHONUSERBASE
PYTHONWARNINGS
UV_DEFAULT_INDEX
UV_EXTRA_INDEX_URL
UV_FIND_LINKS
UV_INDEX
UV_PROJECT_ENVIRONMENT
UV_PYTHON
UV_PYTHON_PREFERENCE
W04_BOOTSTRAP_TUPLE_B64
W04_CHILD_INPUT_B64
W04_CHILD_ROLE
W04_ENTRYPOINT_SOURCE_FD
W04_RESULT_FD
W04_RESULT_NONCE
all_proxy
http_proxy
https_proxy
no_proxy
```

This is a closed map: every name not in the exact present set is absent. In
particular, an unknown behavior-affecting variable is not ignored or normalized;
it fails. The launcher-control contract distinguishes the exact literal values,
the nine named operational substitutions, the exact deterministic uv
input-to-Python transformation, and the exact required-absent array.

The acyclic construction is exact:

1. Build the expected actual outer-Python `E_outer_base` from the closed uv-input
   map and exact uv transformation, without `W04_BOOTSTRAP_TUPLE_B64`, and verify
   the closed present/absent contract.
2. Construct canonical object
   `{"algorithm":"w04-outer-environment-bootstrap-v1",
   "excluded_until_insertion":["W04_BOOTSTRAP_TUPLE_B64"],
   "present":<the exact name-sorted map with only the nine actual values replaced
   by the tokens above>,"required_absent":<the exact code-point-sorted array>}`.
3. Set `fixed_environment_digest` to SHA-256 of those canonical UTF-8 JSON bytes.
4. Insert that digest into `w04-local-control-bootstrap-v2`, canonical-encode the
   now-complete tuple once, and base64url-encode it without padding.
5. Set `W04_BOOTSTRAP_TUPLE_B64` to that encoding, producing
   `E_outer_transport`. There is no second tuple encoding.
6. Separately set operational
   `outer_transport_environment_sha256 =
   SHA256(canonical_json(E_outer_transport))`, using every complete actual
   environment name and actual value after insertion.

The complete transport hash never appears inside the tuple or transport
environment. The master computes it from the map it supplies; the launcher's first
verifier recomputes it from its received complete map and returns it in the
existing final master-facing control status for equality. The verifier removes
only `W04_BOOTSTRAP_TUPLE_B64`, reapplies the nine named substitutions, reconstructs
the exact base object, verifies `fixed_environment_digest`, decodes and
canonical-re-encodes the tuple byte-identically, and verifies every tuple field.
No recursion, fixed-point search, self-digest, placeholder digest, omitted variable,
or unbounded exception is permitted. The algorithm identifier, exact inclusion,
absence, substitution, insertion, canonicalization, and comparison rules are
stable authority inside `local_launcher_control_digest`.

#### 8.0.3 Sole control ownership, child prefixes, and manifest/build handoff

The launcher alone:

1. verifies its first-instruction bootstrap and retains the launcher source
   descriptor;
2. snapshots the whole repository/site bytecode inventory;
3. may sample the admission UUID, the future rebuild UUID, and the two distinct
   result nonces, but these sampled rebuild values grant no path authority;
4. safely creates and proves empty **only** the admission prefix;
5. preopens the admission entrypoint descriptor, constructs the exact admission
   input envelope and child environment, then launches only admission;
6. validates the admission result frame, diagnostics, EOF, exit, descriptor, path,
   pyc, prefix, manifest bytes, and component proofs;
7. atomically writes or confirms the immutable canonical code manifest returned
   by admission, reopens/readbacks it, and requires byte/digest/identity equality;
8. only after that readback calculates the complete Section 9 build ID from no
   placeholder field;
9. only after the build ID exists derives, creates, and proves empty the one
   build-scoped rebuild prefix;
10. only then preopens the rebuild entrypoint descriptor, constructs the exact
    rebuild input envelope and child environment, and launches rebuild; and
11. validates the rebuild result, receipt/layer identities, diagnostics, EOF,
    exit, descriptors, paths, pyc, prefixes, and final recheck before final status.

The exact child argv remain:

```text
uv run --locked --no-sync python -S -B scripts/admit_wyscout_v5_runtime.py
uv run --locked --no-sync python -S -B scripts/rebuild_wyscout_v5.py
```

Admission uses the admission prefix before a build ID exists. Merely sampling a
rebuild UUID early does not create a directory, path, envelope, environment, child,
or output authority. Rebuild uses only the build-scoped prefix after immutable
manifest publication/readback and build-ID calculation.
Both receive `PYTHONDONTWRITEBYTECODE="1"` and the absolute selected child prefix
before their own `uv`/Python creation. Each new child has independent interpreter,
guard, descriptors, environment, prefix, nonce, and result channel. It inherits no
live audit state from another Python process.

`scripts/admit_wyscout_v5_runtime.py` alone constructs canonical code/environment
manifest bytes and component proofs; it cannot write the manifest or calculate a
build ID. The launcher is the sole code-manifest writer and build-ID calculator.
`scripts/rebuild_wyscout_v5.py` and existing named serializers retain all R12
product/layer/receipt ownership. The launcher may verify the named rebuild receipt
but cannot write it or any Bronze, Silver, Gold, layer manifest, boundary receipt,
invocation receipt, health/card, or product byte.

Publication order is globally unique and is repeated verbatim by every process,
test, sequence diagram, and ownership record: sample values if desired; create
admission prefix only; admission launch; admission frame digest/EOF;
descriptor-final binding; diagnostic EOF; exit `0`; admission
path/pyc/prefix/launcher postchecks; exact manifest-byte and proof validation;
immutable atomic manifest write/confirm; manifest readback equality; complete
build-ID calculation; rebuild-prefix derivation and creation; rebuild envelope and
environment construction; rebuild launch; rebuild result/receipt/layer validation.
Early rebuild-prefix creation, a placeholder/partial build ID, a rebuild envelope
or environment built before the ID, a second ordering, or an implied exception
fails. Any failure leaves no build authority and is not repaired or cleaned.

#### 8.0.4 Exact child entry-point source descriptors and bounded channels

Before each child, the launcher resolves that role's exact repo-relative script
beneath the still-open repository root, performs contained `lstat`, and opens one
dedicated descriptor using `O_RDONLY|O_NOFOLLOW` with `O_CLOEXEC` during
verification. It requires a regular non-link mode-`0o644`, `st_nlink==1`, exact
frozen size, bytes, digest, role, path, argv, expected repository-code digest,
environment, and nonce; `lstat`/`fstat` identity fields must agree. Positional
reads require exact EOF and leave offset `0`.

The launcher then marks only that source descriptor and the fresh result-pipe write
descriptor inheritable/`FD_CLOEXEC` clear. It passes their strict decimal numbers as
`W04_ENTRYPOINT_SOURCE_FD` and `W04_RESULT_FD`. Each uses grammar
`(?:[3-9]|[1-9][0-9]+)`, is at most `2147483647`, and the two numbers differ.
Together they are exactly the two nonstandard inherited descriptors in the child;
the former R12 claim that the result descriptor is the only one is withdrawn.
Stdin is closed. Stdout and stderr are the standard-numbered bounded diagnostic
pipes. Every unrelated descriptor/pipe end is noninheritable or closed in the
appropriate process. In particular, the still-open launcher-source descriptor has
`FD_CLOEXEC` set in the launcher and is excluded from the child's exact pass set;
“lifetime through both children” means the launcher retains it while they run, not
that either child receives a third source descriptor.

The launcher retains its original entrypoint descriptor through frame EOF,
diagnostic EOF, child reap, and all postchecks. The child uses positional reads so
the shared open-file-description offset remains `0`. Its first user-code verifier,
before another file-backed import, requires the environment descriptor open,
inheritable, `FD_CLOEXEC` clear, regular, mode/link/size-equal, offset `0`, and
positionally byte/digest/EOF-equal to the frozen row. It also verifies role, path,
argv, complete environment, nonce, launcher digest, and expected repository-code
digest. Immediately before framing the result, it repeats `fstat`, positional
bytes/digest/EOF, and offset comparison and binds the observation in the payload.
It writes the one result frame, closes its source copy exactly once, closes the
result writer exactly once, and exits. The launcher closes its retained parent
source descriptor exactly once only after reap and postchecks. Close error,
premature close, offset drift, missing EOF, or unequal final observation fails.

For each child the launcher creates a fresh anonymous unidirectional result pipe.
The frame remains exactly:

```text
8 bytes   magic = ASCII "W04CRSLT"
2 bytes   UINT16_BE version = 1
4 bytes   UINT32_BE payload_length, 1..16777216
N bytes   strict UTF-8 canonical JSON payload
32 bytes  raw SHA256(payload bytes)
EOF
```

There is no newline, compression, second frame, trailing byte, recovery scan, or
diagnostic substitution. Wrong magic/version/length, empty/truncated/oversized/
concatenated input, payload digest inequality, or anything after the digest fails.

Stdout and stderr remain separate pipes, each capped at exactly 1,048,576 bytes and
drained while the child runs. They are operational bytes only and never parsed as
authority. Overflow, confusion, or read error fails. The exact monotonic deadline
remains 21,600 seconds per child from successful creation through result EOF,
diagnostic EOF, and reap and is never reset. Frame and result EOF precede
interpretation; exact exit status `0` follows. A zero exit without one valid frame,
a valid frame with nonzero/signal exit, timeout, or channel failure terminates and
reaps the child, retains only failure evidence, performs postchecks, and never
cleans state into success.

#### 8.0.5 Closed child environments and canonical input envelopes

Both children receive one and only one value-bearing invocation transport:

```text
W04_CHILD_INPUT_B64 =
  unpadded base64url(canonical UTF-8 JSON w04-child-input-v1 envelope)
```

There is no argv value token: both exact eight-token no-argument child argv remain
unchanged. There is no stdin, sidecar config, newest-file selection, directory
scan, generic config blob, inherited Python object, provider access, network
resource, or alternate environment-value channel. The four bootstrap/control
environment variables below identify the role and descriptors; all semantic
invocation values live in the one canonical envelope and any duplicated bootstrap
value must compare equal.

For either role, the launcher first constructs expected actual-Python
`E_child_base`. It consists of the twenty stable literal outer entries in Section
8.0.2, plus exactly these
eight outer operational entries with the same accepted actual values:
`HOME`, `PATH`, `PYTHONPYCACHEPREFIX`, `TMPDIR`, `UV_CACHE_DIR`, and
`VIRTUAL_ENV`, plus `UV` and `__CF_USER_TEXT_ENCODING`. Their stable tokens remain
`<W04_HOME>`, the exact
`<W04_VENV_BIN>:<W04_UV_BIN_DIR>:/usr/bin:/bin:/usr/sbin:/sbin`,
`<W04_TMPDIR>`, `<W04_UV_CACHE_ROOT>`, and
`<W04_PROJECT_ROOT>/.venv`, `<W04_UV_PHYSICAL_PATH>`, and
`<W04_CF_USER_TEXT_ENCODING>`; the selected `PYTHONPYCACHEPREFIX` token is
role-specific `<ADMISSION_PREFIX>` or `<REBUILD_PREFIX>`.
`PYTHONPYCACHEPREFIX` is the already-created absolute admission prefix for
admission or the already-created absolute build-scoped rebuild prefix for rebuild.
It then contains exactly:

```text
W04_CHILD_ROLE = "PRE_BUILD_ADMISSION" or "POST_BUILD_ID_REBUILD"
W04_ENTRYPOINT_SOURCE_FD = <strict decimal source descriptor>
W04_RESULT_FD = <different strict decimal result descriptor>
W04_RESULT_NONCE = <64 lowercase hex>
```

`W04_LAUNCHER_SOURCE_FD`, `W04_BOOTSTRAP_TUPLE_B64`, and
`W04_CHILD_INPUT_B64` are absent at this point. The exact proxy, coverage,
dynamic-loader, Python-path/startup, uv-index/selector, and lowercase-proxy names
listed as absent for the outer environment remain absent. Every environment name
not in this exact present set is absent; an unknown name fails.

For each child launch the launcher constructs the corresponding exact uv-input
map with depth `"0"` and the venv component omitted from the front of `PATH`;
the same admitted uv transformation must yield depth `"1"`, one venv prefix, the
resolved `UV` path, and no other mutation at the child first instruction. Thus the
closed environment describes what child Python actually receives, while the
stable process-launch contract also binds the exact map transported into uv and
the exact deterministic transformation between them.

The child base-environment digest uses
`w04-child-environment-input-v1`. The launcher substitutes only the eight named
operational values above with their Section 8.0.2 tokens, substitutes actual source
and result decimals with `<ENTRYPOINT_SOURCE_FD>` and `<RESULT_FD>`, substitutes
the nonce with `<RESULT_NONCE>`, and leaves the exact role literal. It canonical-
hashes:

```text
{
  "algorithm": "w04-child-environment-input-v1",
  "excluded_until_insertion": ["W04_CHILD_INPUT_B64"],
  "present": <exact name-sorted normalized E_child_base>,
  "required_absent": <exact code-point-sorted absent-name array>
}
```

That digest is placed in the input envelope. Only after the complete envelope is
canonical-encoded and base64url-encoded does the launcher insert
`W04_CHILD_INPUT_B64`, yielding `E_child_transport`. It then calculates operational
`child_transport_environment_sha256 =
SHA256(canonical_json(E_child_transport))`. The complete transport hash is not in
the envelope or environment; the child independently recomputes it and returns it
as the already accepted result field `child_environment_sha256`. Thus neither
child digest graph is recursive.

The decoded envelope must be 1..262,144 bytes, must satisfy the canonical JSON
rules in Section 8.0.6, and has exactly these sixteen keys:

Input scalar grammars are closed. SHA-256 and nonce use `[0-9a-f]{64}`. A
canonical UUID uses lowercase hex and hyphens with RFC 4122 variant and the
field-declared version nibble. An authority/artifact ID that is not declared a UUID
is 1..512 NFC ASCII characters matching
`[A-Za-z0-9][A-Za-z0-9._:/=-]{0,511}` and must equal the accepted upstream ID.
A canonical UTC instant matches
`[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{6})?Z`
and must also be a real proleptic-Gregorian UTC value; fractions, when present,
have exactly six digits. Strict-decimal FD and integer grammars are as already
defined. Relative and absolute paths use Section 8.0.6 segment safety; an absolute
input path must additionally equal the descriptor-contained project-root join of
its paired relative path. Base64url uses the canonical unpadded grammar. Exact
literal fields accept no alternate case, alias, whitespace, or normalization.

| key | JSON type | nullability, grammar, cardinality/order, role, and authority |
|---|---|---|
| `base_environment_digest` | string | non-null SHA-256 of the exact normalized child base object; stable |
| `child_role` | string | non-null exact role literal; stable and equal `W04_CHILD_ROLE` |
| `entrypoint_relative_path` | string | non-null exact role script path from the unchanged argv; stable |
| `entrypoint_sha256` | string | non-null exact accepted script SHA-256; stable |
| `entrypoint_size_bytes` | integer | non-null exact accepted positive size, at most 16,777,216; stable |
| `expected_repository_code_sha256` | string | non-null exact pre-admitted repo code digest; rebuild equals admitted manifest field; stable |
| `inputs` | object | non-null exact one role schema below; the other role's keys are absent |
| `launcher_sha256` | string | non-null exact accepted launcher-byte digest; stable |
| `nonce` | string | non-null 64 lowercase hex, equal `W04_RESULT_NONCE`; operational/replay-bound |
| `ordered_argv` | array | non-null exactly eight strings, in the unchanged role argv order; stable |
| `ordered_argv_sha256` | string | non-null SHA-256 of canonical JSON of that exact array; stable |
| `pycache_prefix_absolute` | string | non-null absolute actual selected prefix, no trailing slash; byte-for-byte the contained project-root join of the relative field, already created/proved empty; operational |
| `pycache_prefix_relative` | string | non-null exact role template below, no trailing slash; operational run/build values under stable template |
| `result_descriptor_number` | integer | non-null `3..2147483647`, equal strict-decimal `W04_RESULT_FD`; operational |
| `schema_version` | string | non-null exact `w04-child-input-v1`; stable |
| `source_descriptor_number` | integer | non-null `3..2147483647`, different from result and equal `W04_ENTRYPOINT_SOURCE_FD`; operational |

The two `ordered_argv` values are exactly:

```text
["uv","run","--locked","--no-sync","python","-S","-B",
 "scripts/admit_wyscout_v5_runtime.py"]
["uv","run","--locked","--no-sync","python","-S","-B",
 "scripts/rebuild_wyscout_v5.py"]
```

For `PRE_BUILD_ADMISSION`, `inputs` has exactly these eight non-null keys and no
rebuild key:

| key | JSON type | exact rule |
|---|---|---|
| `admission_prefix_relative_path` | string | `data/working/wyscout/v5/.staging/admission/admission_run_id=<admission_run_id>/runtime-pycache`; equals common prefix |
| `admission_run_id` | string | canonical lowercase v4 UUID; operational |
| `bootstrap_tuple_sha256` | string | SHA-256 of decoded canonical `w04-local-control-bootstrap-v2` bytes; stable |
| `code_manifest_schema_version` | string | exact `w04-code-environment-admission-v11`; stable |
| `pyproject_sha256` | string | exact accepted `pyproject.toml` SHA-256; stable |
| `repository_code_sha256` | string | exact common expected repository code digest; stable |
| `selected_dependency_groups` | array | exactly `["data","e2e","lint-type","model","orchestration","runtime","security","test"]` in this order; stable |
| `uv_lock_sha256` | string | exact accepted `uv.lock` SHA-256; stable |

For `POST_BUILD_ID_REBUILD`, `inputs` has exactly these ten non-null keys and no
admission key:

| key | JSON type | exact rule |
|---|---|---|
| `build_id` | string | exact Section 9 64-lowercase-hex build ID, already calculated; stable |
| `code_manifest_id` | string | canonical lowercase UUIDv5 of the immutable admitted manifest; stable |
| `code_manifest_relative_path` | string | exact `data/manifests/wyscout/v5/code/<code_manifest_sha256>.code-manifest.json`; stable |
| `code_manifest_sha256` | string | exact immutable readback digest; stable |
| `environment_digest` | string | exact admitted environment digest; stable |
| `layer_manifest_relative_paths` | array | exactly Bronze, Silver, Gold manifest paths below in that order; stable |
| `rebuild_invocation` | object | exact twenty-five-key schema below; stable and schema-bound |
| `rebuild_prefix_relative_path` | string | exact `data/working/wyscout/v5/.staging/<build_id>/<run_id>/runtime-pycache`; equals common prefix; run component operational |
| `rebuild_receipt_relative_path` | string | exact `runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json`; operational run component under stable template |
| `run_id` | string | canonical lowercase v4 UUID; operational and equal every run/path/result field |

The three `layer_manifest_relative_paths` strings are exactly:

```text
data/manifests/wyscout/v5/bronze/<build_id>.manifest.json
data/manifests/wyscout/v5/silver/<build_id>.manifest.json
data/manifests/wyscout/v5/gold/<build_id>.manifest.json
```

`rebuild_invocation` is not an opaque or generic configuration payload. It is the
closed, already-authorized `w04-rebuild-invocation-v1` object with exactly these
twenty-five keys:

| key | JSON type | exact rule |
|---|---|---|
| `authority_rows` | array | exactly four rows, FIELD, POSSESSION, SUPPORTED_FEATURE, IDENTITY in that order, schema below |
| `build_id` | string | equal enclosing `build_id` and recomputed Section 9 digest |
| `code_manifest_id` | string | equal enclosing immutable manifest UUIDv5 |
| `code_manifest_sha256` | string | equal enclosing/readback digest |
| `dependency_rows` | array | exactly five complete Section 5 dependencies in its declared canonical sort |
| `dependency_watermark` | string | canonical UTC instant, strict maximum of the five `available_at` values and before cutoff |
| `environment_digest` | string | equal enclosing/admission digest |
| `feature_cutoff_ts` | string | canonical UTC instant with `Z`; every bound clock is strictly earlier |
| `feature_schema_hash` | string | exact accepted feature-schema SHA-256 |
| `identity_bundle_id` | string | exact accepted identity-bundle ID |
| `identity_bundle_sha256` | string | exact accepted identity-bundle SHA-256 |
| `local_resource_digest` | string | exact Section 4.3 seventeen-resource digest |
| `product_contract_digest` | string | digest of exact Section 7 paths, serializers, schemas, keys, receipts, and layer order |
| `role_context_id` | string | exact neutral role-context UUID |
| `role_context_state` | string | exact `neutral_unscoped` |
| `role_context_version` | string | exact `w04-neutral-role-context-v1` |
| `schema_bundle_digest` | string | digest of every already-authorized Bronze/Silver/Gold/result/receipt schema |
| `selected_lock_closure_digest` | string | exact admitted complete `L` digest |
| `source_manifest_id` | string | exact immutable source manifest ID |
| `source_manifest_sha256` | string | exact immutable source manifest digest |
| `tenant_club_id` | string or null | canonical lowercase UUID when scoped to a club; JSON null is permitted only here and means the accepted single-tenant no-club context |
| `tenant_id` | string | canonical lowercase tenant UUID |
| `window_definition_id` | string | canonical lowercase UUID for the exact accepted window |
| `window_end_utc` | string | canonical UTC instant from the accepted window contract |
| `window_start_utc` | string | canonical UTC instant from the accepted window contract |

Each `authority_rows` object has exactly seven non-null string keys:
`acceptance_id`, `acceptance_sha256`, `authority_kind`, `candidate_id`,
`candidate_sha256`, `review_id`, and `review_sha256`. `authority_kind` is the
ordered literal. Every ID is the exact accepted artifact ID; every digest is
lowercase SHA-256. Each `dependency_rows` object has exactly five non-null string
keys: `available_at`, `dependency_kind`, `manifest_id`, `manifest_sha256`, and
`observed_at`. The array has exactly the one `source_manifest`, one
`identity_evidence`, and three distinct `feature_schema` records required by
Section 5, in its exact tuple sort; IDs/digests and strict clocks equal the
accepted evidence. Arrays preserve the stated order; object keys remain canonical.

The rebuild child derives all read and write authority from this exact envelope:
manifest identities select exact immutable files; the invocation selects only
already-authorized schema-bound values; `build_id` binds every layer path;
`run_id` binds the rebuild prefix and receipt; the exact layer array binds all
completion rows. It must not scan for a code manifest, select newest, read a
generic config, accept a provider/resource argument, invent an argv token, acquire
a resource, or infer a value from ambient state.

The first child instruction decodes, canonical-parses, canonical-re-encodes, and
validates the entire envelope before using a value. Unknown or duplicate
environment names; unknown, duplicate, cross-role, missing, null (except the one
declared nullable field), mistyped, malformed, over-cardinality, reordered, or
noncanonical envelope data fails. It then requires exact equality among role,
source FD, result FD, nonce, prefix, launcher digest, repository digest, script
row, argv, and environment digest wherever environment/envelope/accepted
authority duplicate them. Any environment/envelope disagreement fails before
import, manifest construction, serializer call, receipt, or product write.
Admission result fields and decoded manifest must equal or deterministically bind
its eight inputs. The unchanged rebuild result binds the complete encoded envelope
through `child_environment_sha256`, binds all twenty-five invocation values by
recomputing `build_id`, and requires its run/prefix/receipt/three layer rows to
equal the ten enclosing inputs. The final recheck binds the same
build/code/environment/resource identities.

#### 8.0.6 Canonical JSON and exhaustive closed child-result schemas

Input-envelope and result-payload JSON use the same canonical UTF-8 encoding with
no BOM. Objects serialize keys in increasing
Unicode code-point order; duplicate keys are rejected during tokenization. There is
no insignificant whitespace. Strings contain only Unicode scalar values in NFC,
escape quotation mark and reverse solidus, use the short escapes for backspace,
tab, LF, form feed, and CR, use lowercase `\u00xx` for other U+0000..U+001F
controls, and otherwise emit UTF-8 directly. Surrogates and non-NFC spellings fail.
The only numbers permitted by these schemas are JSON integers in
`0..9007199254740991`, written as the shortest decimal token with no sign unless a
field explicitly allowed negative values (none does), no leading zero except `0`,
and no fraction or exponent. Floats are forbidden. Booleans are lowercase JSON
`true`/`false`. Result payloads forbid null everywhere; input envelopes forbid null
everywhere except `rebuild_invocation.tenant_club_id`, whose sole nullable meaning
is declared in Section 8.0.5. Base64url is RFC 4648 URL alphabet
without `=` padding, grammar `[A-Za-z0-9_-]+`, and must decode/re-encode
identically. SHA-256 strings are exactly `[0-9a-f]{64}`. Nonce strings use that same
grammar. Result run UUIDs are canonical lowercase v4,
`[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}`.
Input fields declared UUIDv5 require version nibble `5`; other input UUID fields
require canonical lowercase RFC 4122 spelling with the version required by their
accepted upstream contract.

A relative path is an NFC POSIX path with `/`, no leading slash, trailing slash,
empty segment, `.`, `..`, backslash, NUL, control, percent-encoding, or alternate
separator. Generic path characters are `[A-Za-z0-9._=/-]`; fields below further
restrict the path to an exact constant or exact template. Every object has exactly
the keys named below. Every array has exactly the stated cardinality and order.
Missing, unknown, duplicate, mistyped, null, unordered, inconsistent, or
over-cardinality data fails before any authority is used.

The top-level payload has exactly these ten keys:

| key | JSON type | exact rule |
|---|---|---|
| `child_environment_sha256` | string | SHA-256 of canonical JSON of the complete actual child transport environment after `W04_CHILD_INPUT_B64` insertion, including actual FD decimals, nonce, selected prefix, and exact encoded envelope |
| `child_role` | string | exact `PRE_BUILD_ADMISSION` or `POST_BUILD_ID_REBUILD` |
| `entrypoint_source` | object | exact fourteen-key observation below |
| `expected_repository_code_sha256` | string | exact pre-admitted repository-code SHA-256; rebuild equals admission manifest value |
| `launcher_sha256` | string | exact accepted launcher bytes digest |
| `nonce` | string | exact distinct launcher-supplied 64-lowercase-hex nonce |
| `ordered_argv_sha256` | string | SHA-256 of canonical JSON array of the exact eight child argv tokens |
| `payload_kind` | string | `CODE_ENVIRONMENT_MANIFEST` iff admission; `REBUILD_COMPLETION` iff rebuild |
| `result` | object | the one role-specific exact object below |
| `schema_version` | string | exact `w04-child-result-v2` |

The exact `entrypoint_source` object has:

| key | JSON type | exact rule |
|---|---|---|
| `descriptor_cloexec` | boolean | exactly `false` |
| `descriptor_inheritable` | boolean | exactly `true` |
| `descriptor_number` | integer | actual `3..2147483647`, equal `W04_ENTRYPOINT_SOURCE_FD`, operational only |
| `device` | integer | actual nonnegative `fstat.st_dev`, operational only |
| `inode` | integer | actual positive `fstat.st_ino`, operational only |
| `link_count` | integer | exactly `1` |
| `mode` | integer | exactly `420` (`0o644`) |
| `offset_after` | integer | exactly `0` after final positional read |
| `offset_before` | integer | exactly `0` before first positional read |
| `relative_path` | string | exact role path named in the unchanged argv |
| `role` | string | equal top-level `child_role` |
| `sha256` | string | exact frozen entrypoint SHA-256 |
| `size_bytes` | integer | exact frozen positive source size, at most `16777216` |
| `source_eof` | boolean | exactly `true` after reading exactly `size_bytes` plus one-byte EOF probe |

The descriptor number/device/inode are operational and excluded from stable/build
identity; path/role/mode/link/size/bytes/digest and descriptor policy are stable.
All observation fields must equal the child's first and final checks and the
launcher's retained descriptor row.

For admission, `result` has exactly these nine keys:

| key | JSON type | exact rule |
|---|---|---|
| `admission_prefix_relative_path` | string | exact `data/working/wyscout/v5/.staging/admission/admission_run_id=<admission_run_id>/runtime-pycache` without trailing slash |
| `admission_run_id` | string | canonical v4 UUID equal launch environment/prefix |
| `canonical_manifest_bytes_b64u` | string | unpadded canonical base64url of 1..12,000,000 decoded bytes; decoded bytes are strict canonical UTF-8 JSON for Section 8.9 |
| `canonical_manifest_sha256` | string | SHA-256 of decoded bytes and future immutable filename |
| `component_proofs` | array | exactly twenty rows in the fixed order below |
| `component_proofs_sha256` | string | SHA-256 of canonical JSON bytes of that exact array |
| `environment_digest` | string | SHA-256 of canonical JSON of the exact Section 8.9 environment-component object |
| `manifest_schema_version` | string | exact `w04-code-environment-admission-v11` |
| `repository_code_sha256` | string | equal top-level `expected_repository_code_sha256` and decoded-manifest field |

Decoding `canonical_manifest_bytes_b64u`, canonical parsing, and canonical
re-serialization must return byte-identical bytes. The decoded manifest has the
exact Section 8.9 closed stable fields and its `schema_version`,
`repository_code_sha256`, and `environment_digest` must equal the three result
values. The file digest must equal `canonical_manifest_sha256`. No operational FD,
nonce, run ID, absolute prefix, device/inode, or diagnostic may occur in the decoded
stable manifest.

Each `component_proofs` row is an object with exactly:

| key | JSON type | exact rule |
|---|---|---|
| `component_key` | string | one exact key in the ordered set below |
| `evidence_row_count` | integer | `1..10000000`, equal the independently recounted stable evidence rows for that component |
| `value_json_sha256` | string | SHA-256 of canonical JSON of the decoded manifest's exact value for `component_key` |

The array cardinality is exactly twenty, with no duplicate, and is ordered exactly:

```text
child_result_contract_digest
editable_root_digest
environment_values_digest
executable_census_digest
extracted_runtime_digest
installed_record_runtime_digest
interpreter_digest
local_launcher_control_digest
local_resource_digest
lock_inputs_digest
process_launch_contract_digest
pyc_policy_source_map_digest
selected_lock_closure_digest
selector
selector_bootstrap_digest
stdlib_digest
uv_physical_sha256
uv_version
venv_bootstrap_digest
wheel_declaration_digest
```

Those are exactly the twenty keys of the decoded manifest environment-component
object. `selector` is the frozen closed selector object; `uv_version` is the exact
version string; every key ending `_digest` and `uv_physical_sha256` is a lowercase
SHA-256 string. Unknown or omitted components, zero/excess rows, wrong ordering,
wrong value digest, proof digest disagreement, or manifest/result disagreement
fails.

For rebuild, `result` has exactly these six keys:

| key | JSON type | exact rule |
|---|---|---|
| `build_id` | string | SHA-256 grammar, equal the launcher-calculated Section 9 build ID and all nested/path values |
| `final_recheck` | object | exact closed object below |
| `layer_manifests` | array | exactly three exact rows ordered `BRONZE`, `SILVER`, `GOLD` |
| `rebuild_prefix_relative_path` | string | exact `data/working/wyscout/v5/.staging/<build_id>/<run_id>/runtime-pycache` |
| `rebuild_receipt` | object | exact receipt row below |
| `run_id` | string | canonical v4 UUID equal launch environment, prefix, receipt, and nested values |

`rebuild_receipt` has exactly:

| key | JSON type | exact rule |
|---|---|---|
| `relative_path` | string | exact `runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json` |
| `sha256` | string | complete physical receipt bytes SHA-256 |
| `size_bytes` | integer | exact positive physical size, at most `16777216` |

Each `layer_manifests` row has exactly:

| key | JSON type | exact rule |
|---|---|---|
| `layer` | string | row 0 `BRONZE`, row 1 `SILVER`, row 2 `GOLD` |
| `manifest_relative_path` | string | exact lower-case layer path `data/manifests/wyscout/v5/<bronze|silver|gold>/<build_id>.manifest.json` matching `layer` |
| `manifest_sha256` | string | complete physical manifest bytes SHA-256 |
| `manifest_size_bytes` | integer | exact positive size, at most `16777216` |
| `semantic_sha256` | string | exact layer semantic digest in that manifest |

`final_recheck` has exactly these seventeen keys:

| key | JSON type | exact rule |
|---|---|---|
| `build_id` | string | equal rebuild result `build_id` |
| `child_environment_sha256` | string | equal top-level value |
| `entrypoint_descriptor_match` | boolean | exactly `true` after final descriptor read |
| `entrypoint_sha256` | string | equal top-level `entrypoint_source.sha256` |
| `environment_digest` | string | equal admitted immutable manifest environment digest |
| `in_place_pyc_unchanged` | boolean | exactly `true` versus launch snapshot |
| `layer_manifest_set_sha256` | string | SHA-256 of canonical JSON of exact `layer_manifests` array |
| `rebuild_prefix_empty` | boolean | exactly `true` at child's final check |
| `rebuild_receipt_sha256` | string | equal `rebuild_receipt.sha256` |
| `repository_code_sha256` | string | equal top-level expected value/admitted manifest |
| `repository_pyc_inventory_sha256` | string | operational final repository inventory digest |
| `resource_digest` | string | exact stable 17-resource digest |
| `run_id` | string | equal rebuild result `run_id` |
| `runtime_subset_digest` | string | exact final admitted `R subset-of L` digest |
| `schema_version` | string | exact `w04-rebuild-final-recheck-v1` |
| `selected_prefix_role` | string | exact `POST_BUILD_ID_REBUILD` |
| `site_pyc_inventory_sha256` | string | operational final site inventory digest |

The launcher recomputes every path, digest, array digest, cross-field equality,
prefix state, descriptor binding, code/environment identity, and final inventory
against its independent retained evidence before accepting the frame. A payload
never grants new source, owner, distribution, manifest, build, serializer, or
product authority.

#### 8.0.7 Checkpoint detection and honest same-trust-domain residual

For the launcher, the master pre-`lstat`/open/`fstat` and outer first-instruction
descriptor check detect a replacement or mutation persistent across those
checkpoints; launcher after-admission, after-rebuild, and final descriptor/path
checks plus master post-exit contained path comparison detect a replacement,
mutation, link/mode/size change, or deletion persistent at any later checkpoint.

For each child, launcher pre-`lstat`/open/`fstat`, child first descriptor check,
child final descriptor binding, and launcher post-reap descriptor/path check detect
persistent substitution, deletion, link/mode/size/byte drift, wrong transported
descriptor, and mutation of the open inode. The descriptor proves the bytes
transported and observed, not that CPython executed by descriptor.

This is not a cryptographic prevention claim. A same-trust-domain actor able to
race the filesystem could transiently replace the path for CPython's path-based
script open and restore the accepted path before the first/self/post observations,
while leaving the transported original descriptor unchanged. Such an unobservable
replace-and-restore may evade this bounded checkpoint design. Eliminating it would
require a different execution primitive/trust boundary not authorised here.
Threat-model T03 therefore remains only partially mitigated and T06/local
administrator remains in the same trust domain. The future implementation must
retain this residual, test persistent replacements and bounded races honestly, and
must not report path/descriptor equality as proof that every transient race was
impossible.

Compatible tags have one narrow bootstrap, avoiding R8's circular claim that no
third-party code runs while `packaging.tags.sys_tags()` is used:

1. With standard-library and repository code only, parse `uv.lock` via `tomllib`.
   Require exactly registry package `packaging==26.2` and exactly the universal
   wheel `packaging-26.2-py3-none-any.whl`, lock SHA-256
   `5fc45236b9446107ff2415ce77c807cee2862cb6fac22b8a73826d0693b0980e`,
   size `100195`. The exact universal filename is selected without a platform-tag
   query; ambiguity, another source, another wheel, or non-universal bootstrap
   fails.
2. Resolve only Packaging's reviewed cache association, extracted RECORD/tree,
   PEP 427 mapping, installed dist-info, RECORD ownership, hashes, sizes, and modes
   using Sections 8.3–8.4 without importing it. All Packaging 26.2 extracted and
   installed bytes must pass before the site root becomes importable.
3. Manually append the one verified contained site root. Keep imports deny-by-
   default, then permit only RECORD-owned `packaging` modules needed by
   `packaging.tags`, its Packaging-owned helpers, marker/version parsing, and no
   other third-party owner. Existing pyc remains denied, so source bytes load.
   Every loaded origin must equal the pre-admitted Packaging RECORD path and bytes.
4. Call `packaging.tags.sys_tags()` once, freeze its complete ordered result and
   the marker environment, then remove the bootstrap exception. Record exact
   imported Packaging modules/origins and an audit proof that no other
   third-party, `.pth`, generated executable, or pyc was opened or imported.
5. Recompute the Packaging association during full `L == I` admission and require
   byte-for-byte equality with the bootstrap observation. Selector disagreement,
   a second tag computation, an extra import, or any mutation fails.

Thus tag computation follows byte admission rather than selecting what may be
admitted. The stable manifest binds the Packaging wheel declaration, extracted and
installed tree digests, exact `packaging==26.2`, ordered tag sequence, marker
environment, and algorithm `w04-packaging-tag-bootstrap-v1`; absolute cache/site
paths and the audit event clock remain operational only.

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
site roots manually added to `sys.path` after the Section 8.0 no-site guard. Disable
user site. The only admitted `.pth` files are the exact three classified in Section
8.3A; none is executed or used to mutate `sys.path`. Every other `.pth`, and every
`.egg` or `.egg-info`, fails. Executable `.pth` content outside those exact
read-and-deny classes, a call through `site`, or any `.pth`-caused import fails.

Each RECORD-owned `METADATA` has exactly one valid Name/Version. Normalize Name and
canonicalize Version. Duplicate/malformed/nested/aliased identity fails. Verify the
editable project separately as `scouting-intelligence==0.1.0`, source `"."`, then
exclude it from third-party installed set `I`. No tooling/unused exception exists.

```text
{(name,version) in L} == {(name,version) in I}
```

Report sorted `lock_only`/`installed_only`; either non-empty fails. Require one-to-one
member/dist-info association.

### 8.3A Exact uv-bootstrap, coverage-hook, and editable-root closure

The verified site root has exactly three regular, non-symlink mode-`0o644` `.pth`
files. Their basenames are unique under exact bytes and ASCII case-fold; there is no
fourth file, alias, hardlink, escape, or startup execution:

| Class | Exact file and owner | Exact actual bytes evidence | Admission |
| --- | --- | --- | --- |
| `UV_VENV_BOOTSTRAP` | unowned `_virtualenv.pth` plus unowned sibling `_virtualenv.py` | `.pth`: `b"import _virtualenv"` (18 bytes), SHA-256 `69ac3d8f27e679c81b94ab30b3b56e9cd138219b1ba94a1fa3606d5a76a1433d`; `.py`: 4,342 bytes, SHA-256 `6cf30c56faf2a55228914dbbd17f8088ed371ebb08f5e7fa6fd931f913fcaf1d` | Separate exact venv-bootstrap class, never distribution ownership; both files are hashed but neither is imported/executed. |
| `DISTRIBUTION_PTH_DENIED` | Coverage 7.15.2 RECORD-owned `a1_coverage.pth` | 205 bytes, SHA-256 `ef2ed06d19867ec669c09a804060666a9cd5e383af0a9d11aa2de79b77d448e8`; RECORD URL-safe digest `7y7QbRmGfsZpwJqAQGBmapzV44OvCp0Rqi3nm3fUSOg` | Installed distribution content is byte-verified, but its executable coverage hook is never evaluated. |
| `EDITABLE_ROOT_PATH_DENIED` | editable root RECORD-owned `scouting_intelligence.pth` | exactly the absolute `<project-root>/src` bytes, no newline; current size 81 and SHA-256 `3dc417212f5f46b7399aa8e13c8bd999c4e0cef30f012f8a9412bf8a54f59fba` | Verify containment and root relation, then manually append the same resolved `src` root; never execute/read it through `site`. |

For `_virtualenv.pth`, the exact no-newline content is executable syntax, but this is
authority to retain and deny it, not authority to run it. `_virtualenv.py` must be
the exact sibling above, regular/non-symlink/mode `0o644`, absent from every
distribution RECORD, and root-independent. Any other unowned site file fails.
Stage-0 asserts `_virtualenv` is absent throughout admission and rebuild. The stable
bootstrap row binds both relative names, exact bytes/hashes/sizes/modes, and
`w04-uv-venv-bootstrap-deny-v1`; its current pyc is handled only by Section 8.6.

The Coverage hook must be the exact RECORD row and bytes above. Its one LF-terminated
line is retained as opaque bytes; admission never `exec`s or imports it.
`COVERAGE_PROCESS_START` and `COVERAGE_PROCESS_CONFIG` are absent from the fixed
environment. A changed hook, missing owner, attempted read through `site`, or
`coverage.process_startup` observation fails.

The editable project is verified separately and remains excluded from third-party
`I`. Exactly one `scouting-intelligence==0.1.0` dist-info exists. Its RECORD has the
reviewed nine rows and singularly owns the `.pth`; `INSTALLER=b"uv"`,
`REQUESTED=b""`, `uv_build.json=b"{}"`, and the exact root-independent
`METADATA`/`WHEEL`/other stable metadata bytes are retained and hashed. The `.pth`
must decode strict UTF-8 to exactly one absolute line, with no newline, equal
`<project-root>/src`, whose resolved directory is contained in the project and is
the exact repo source root. Stable normalization replaces that complete verified
line only with `<W04_PROJECT_ROOT>/src`; it never trims, expands, or normalizes any
other content.

`direct_url.json` is exactly 123 bytes in the current root and strict JSON
`{"url":"file://<project-root>","dir_info":{"editable":true}}` with no newline.
Actual bytes/path/hash
`2361d905ac1e0a9300426cb6a2ab39e0ddec56d3c20e9eb967966ff19a053243`
are operational evidence; after exact URL decoding and equality to the project
root, stable normalization substitutes only `<W04_PROJECT_ROOT>` and reserializes
with the reviewed byte grammar. `uv_cache.json` is exactly 194 current bytes,
SHA-256 `a4bf7fb0887dc0b05c0f8286f841340f7dfac4a70ff2b5fec9da26275f9fdd8a`,
and has exactly keys `timestamp`, `commit`, `tags`, `env`, `directories`, with
`commit=null`, `tags=null`, `env={}`, and only directory `src`; its timestamp and
directory timestamp are operational editable-install observations, excluded from
stable identity. Unknown keys or a non-null commit/tag fails.

The stable editable-root digest binds exact root-independent metadata bytes,
normalized `.pth` and `direct_url` bytes, the reviewed `uv_cache` structural
predicate/version (not its clocks), normalized RECORD rows with those operational
hashes replaced by their stable normalized row digests, `pyproject.toml`,
`uv.lock`, and the repo code manifest. Operational evidence retains every actual
root-bearing byte/hash/size/path and `uv_cache` timestamp. Two roots require equal
stable editable-root digests and may differ only in those named operational fields.

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
except the exact Section 8.3A venv-bootstrap/editable-root classes, the total Section
8.5 executable census, and the enumerated denied pyc below.

### 8.5 Total installed executable census and canonical wrapper interpreter

Let `B` be every installed RECORD row across `I` whose text begins exactly
`../../../bin/`. Enumerate `B` before opening any target. The row is not passed to a
generic normalizer: require exactly three parent components, literal `bin`, and one
safe basename; append it to the owning dist-info directory, lexically normalize
once, resolve the parent directory without following the final file, and require
the result equal the exact venv scripts directory plus that basename. The target is
one regular, non-symlink, non-hardlink-aliased mode-`0o755` file with one RECORD
owner. Absolute paths, another depth/directory, slash/backslash/percent/control/
Unicode in the basename, exact or ASCII-case-fold collisions, and escape fail.

Every `B` row belongs to exactly one of three authority classes:

```text
E = direct verified console/gui entry-point wrappers
P = the one reviewed pip interpreter-version alias
W = verified wheel .data/scripts payloads

B = E disjoint-union P disjoint-union W
|B| = 35; |E| = 33; |P| = 1; |W| = 1; owners(B) = 21
```

Missing, extra, multiply classified, unsafe, colliding, unowned, wrong-mode,
changed, read during rebuild, or executed rows fail. A fresh locked sync that
changes any census member/owner/class/count stops the work rather than updating this
design implicitly.

#### 8.5.1 Canonical venv interpreter alias closure

Wrapper authority is not incidental equality with the spelling returned by
`sys.executable`. The exact venv scripts directory contains exactly these three
distinct required alias symlinks:

```text
<project-root>/.venv/bin/python
  raw link -> /Users/adrian/.local/share/uv/python/
              cpython-3.12.12-macos-aarch64-none/bin/python3.12
<project-root>/.venv/bin/python3
  raw link -> python
<project-root>/.venv/bin/python3.12
  raw link -> python
```

All three alias paths are contained in the exact venv scripts directory, have
distinct lstat rows, have lstat mode `0o755`, are symlinks, have no cycle or extra
hop, and resolve to the same frozen regular physical Python 3.12.12 executable.
Both `python3 -> python` and `python3.12 -> python` are exact one-hop relative
links that remain inside the scripts directory. The only permitted absolute leaf
is `python`'s exact admitted physical interpreter above. Its mode is `0o755`, size
`49,968`, and SHA-256
`cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79`.
Implementation/full version, ABI, platform, loaded libpython/loader and interpreter
closure must equal Section 8.8. A missing alias, a fourth alias, changed raw target,
inode alias, target-byte mismatch, escape, cycle, non-link intermediate, extra hop,
or version/mode mismatch fails.

`python` is the canonical uv POSIX wrapper-shebang alias.
Both exact launches—`uv run --locked --no-sync python -S -B
scripts/admit_wyscout_v5_runtime.py` and `uv run --locked --no-sync python -S -B
scripts/rebuild_wyscout_v5.py`—operationally report the admitted `python3` alias.
Admission
records all three absolute alias paths, raw link texts, distinct lstat identities,
complete resolution chains, the operational locked/no-sync
`python -> python3` launch observation,
resolved physical path, and exact wrapper shebang. Only `python` is permitted in a
generated-wrapper shebang. Stable identity binds the three alias basenames, both
root-independent safe relative chains (`python3 -> python` and
`python3.12 -> python`), the canonical `python -> physical interpreter` role,
physical interpreter identity/digest, and algorithm
`w04-venv-wrapper-interpreter-alias-v2`; it excludes all root-bearing absolute alias
and external physical-path spellings.

#### 8.5.2 Class E — direct console/gui entry-point wrappers

For each selected distribution, `entry_points.txt` is usable only when it is a
regular verified extracted RECORD member, maps byte-identically into installed
dist-info, and is parsed without importing the distribution. Decode strict UTF-8;
use INI syntax with no interpolation, duplicate section/key, continuation, comment
ambiguity, or unnamed value. Only `[console_scripts]` and `[gui_scripts]` generate
direct wrappers. Other groups remain metadata and generate no executable.

Each entry is exactly `<safe-name> = <module-path>:<attribute>`.
`module-path` is dot-separated Python identifiers; `attribute` is one Python
identifier; extras, calls, whitespace-bearing names, duplicate names, and malformed
targets fail. `<safe-name>` is ASCII and matches
`[A-Za-z0-9][A-Za-z0-9._-]{0,127}`, is not `.` or `..`, and passes the common
collision rules above.

Each direct entry maps to exactly one `B` row with the same name and owner. Actual
size and URL-safe unpadded SHA-256 equal its installed RECORD row. Actual bytes are
strict UTF-8/LF and equal this reviewed uv POSIX template byte-for-byte:

```text
#!<project-root>/.venv/bin/python\n
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

The first line must use the exact admitted canonical `python` alias—not `python3`,
the launch-time `sys.executable` spelling, `/usr/bin/env`, an argument, another
root, or another alias. The remaining bytes are the exact deterministic function of
the verified target. GUI entries use the same reviewed POSIX template only on this
frozen platform.

The positive direct-wrapper census is exact:

| Owner | Exact direct entry-point names |
| --- | --- |
| `bandit==1.9.4` | `bandit`, `bandit-baseline`, `bandit-config-generator` |
| `cachecontrol==0.14.4` | `doesitcache` |
| `charset-normalizer==3.4.9` | `normalizer` |
| `coverage==7.15.2` | `coverage`, `coverage-3.12`, `coverage3` |
| `detect-secrets==1.5.0` | `detect-secrets`, `detect-secrets-hook` |
| `fastapi==0.140.0` | `fastapi` |
| `httpx==0.28.1` | `httpx` |
| `hypothesis==6.161.6` | `hypothesis` |
| `idna==3.18` | `idna` |
| `import-linter==2.13` | `import-linter`, `lint-imports` |
| `markdown-it-py==4.2.0` | `markdown-it` |
| `mypy==1.20.2` | `dmypy`, `mypy`, `mypyc`, `stubgen`, `stubtest` |
| `numpy==2.5.1` | `f2py`, `numpy-config` |
| `pip==26.1.2` | `pip`, `pip3` |
| `pip-audit==2.10.1` | `pip-audit` |
| `pip-licenses==5.5.5` | `pip-licenses` |
| `playwright==1.61.0` | `playwright` |
| `pygments==2.20.0` | `pygmentize` |
| `pytest==9.1.1` | `py.test`, `pytest` |
| `uvicorn==0.51.0` | `uvicorn` |

This table contains 33 names and 20 owners. Each manifest row additionally binds
entry-point group, exact module/attribute target, owning dist-info/RECORD row, exact
actual bytes/hash/size/mode, and verified path.

#### 8.5.3 Class P — exact pip interpreter-version alias

Pip 26.1.2's verified 84-byte `entry_points.txt` contains exactly:

```text
[console_scripts]
pip=pip._internal.cli.main:main
pip3=pip._internal.cli.main:main
```

Only when both base entries have the same exact target and both Class-E wrappers
pass may uv's interpreter-version alias be derived as
`pip<python-major>.<python-minor>`. For the frozen Python 3.12.12 interpreter the
sole derived name is `pip3.12`; it is not treated as a declared entry point. Its
owner is exactly `pip==26.1.2`, target is exactly
`pip._internal.cli.main:main`, path row is exactly `../../../bin/pip3.12`, and it
must be absent from wheel `.data/scripts`.

The installed `pip`, `pip3`, and `pip3.12` files are all exact mode `0o755`, size
382, SHA-256
`d371b253cc444af2efa4c2f1f41ff3030f5cc10a912807de94a35629dc0bc3ff`,
installed RECORD URL-safe digest
`03GyU8xESvLvpMLx9B_zAw9cwQqRKAfelKNWKdwLw_8`, and byte-identical. Their exact
canonical-`python` shebang and remaining template bytes must pass before the alias
is admitted. No `pip3`, `pip3.12`, or basename rule may generate a second class:
`pip3` is E; only `pip3.12` is P. Another pip alias, interpreter-version spelling,
target, owner, byte, hash, size, mode, RECORD row, or base-wrapper mismatch fails.

#### 8.5.4 Class W — wheel `.data/scripts` payload

Class W derives only from a verified extracted RECORD path of exact form
`<wheel-data-dir>.data/scripts/<safe-name>` and PEP 427's scripts-scheme mapping,
never from an entry point. The extracted row must be a regular non-symlink file,
have a supported SHA-256 and size, and map singularly to the exact `B` path owned by
the same distribution. Safe-name/path, containment, case-fold uniqueness, one owner,
no hardlink, exact installed RECORD row, and mode `0o755` all apply.

This design has no wheel-script shebang-rewrite class. Extracted and installed bytes
must be byte-identical; any `#!python`/`#!pythonw` trigger, installer rewrite,
non-identical byte, changed mode, or other transformation fails. The only positive
member is:

```text
owner: ruff==0.16.0
extracted: ruff-0.16.0.data/scripts/ruff
installed RECORD: ../../../bin/ruff
entry-point authority: none (no console_scripts or gui_scripts)
file kind: Mach-O 64-bit arm64 executable
mode: 0o755
size: 23669488
SHA-256: 1ac190f23d9a690d75b3e74eb88a07e02f6414227a41ba1920609af989ecec52
RECORD digest: GsGQ8j2aaQ11s-dOuIoH4C9kFCJ6QboZIGCa-Yns7FI
extracted == installed: byte-for-byte
```

No execution is used to admit Ruff. A second `.data/scripts` member, a Ruff entry
point, name collision, non-byte-identical mapping, or another W owner changes the
census and fails.

#### 8.5.5 Stable/operational evidence and denial

Operational rows record absolute script path, class, exact root-bearing bytes/hash/
size/mode, RECORD row, owner, authority, target where applicable, interpreter alias
chain, and verification. For E and P only, after actual bytes pass, stable
normalization replaces exactly the verified first line
`#!<project-root>/.venv/bin/python\n` with
`#!<W04_VENV_WRAPPER_PYTHON>\n` and retains every remaining byte unchanged. It does
not normalize any other shebang/substring. W has no root-bearing shebang; its exact
byte digest/size/mode and extracted/installed equality are stable unchanged.

Each stable row binds the class and constructive authority so equal bytes cannot
collapse P into E or W. The combined version is
`w04-installed-executable-census-v2`. Stable environment/build/two-root identity
uses the 35 sorted classed rows; operational receipts use actual rows. Distinct
roots require identical membership/classes/owners/targets/normalized bytes/modes
and W bytes. Admission may read all 35 only before denial. From each process's
guard installation through its final recheck, open/read/mmap/execute of every
executable target is denied and audited. Zero reads and zero executions are
required across both processes.

### 8.6 Source-complete bytecode authority, operational census, and read denial

Pre-existing `__pycache__` directories and pyc are operational state, not code
authority. They are never deleted, imported, or used to select a source. Before
each Section 8.0 child Python process exists, the exact local-control launcher
enumerates the exact
site root and whole repository with safe contained lstat traversal and no symlink
following. It snapshots directory entries, file identity, hardlink count, mode,
size, SHA-256, first 16 header bytes, magic, and cache-name tag. Any path escape,
symlink, hardlink alias, non-regular pyc, duplicate path, unreadable file, or
mutation during the bounded read fails.

#### 8.6.1 Stable authority is built from every admitted source

The stable map is constructed before considering whether any pyc exists. It is the
complete lexically sorted union of:

1. every selected third-party `.py` having exactly one verified installed RECORD
   owner from `L`, keyed by normalized distribution name/version and its exact
   root-independent RECORD path;
2. every `.py` owned by the frozen repository code manifest, keyed by exact
   repository-relative source path; and
3. the exact Section 8.3A uv-bootstrap
   `site-packages/_virtualenv.py`, keyed by its bootstrap authority rather than a
   distribution.

Every row binds authority class, owner identity, root-independent source path,
source SHA-256, source size, and exact source bytes through the enclosing admitted
tree digest. Third-party and repository rows bind both deterministic allowed cache
name grammars:

```text
NORMAL(source) =
  <source-stem>.cpython-312[.opt-0|.opt-1|.opt-2].pyc
PYTEST(source) =
  <source-stem>.cpython-312-pytest-9.1.1.pyc
```

The pytest grammar is permitted only with the exact admitted `pytest==9.1.1`; it
never transfers source ownership. The uv-bootstrap source permits only its normal
grammar. A filename cannot satisfy both grammars. The map contains a row even when
no corresponding pyc exists and may describe both allowed grammars when neither or
only one is currently present. It is never derived by reversing the current pyc
list, never frozen to 58 repository rows, and never expanded by an orphan.

Stable identity binds algorithm `w04-preexisting-pyc-enumerate-deny-v4`, current
interpreter cache tag/magic, exact normal/pytest grammars and pytest version, the
complete source-authority map above, traversal-root roles, the exact optional site
orphan predicate and all three exact optional repository orphan predicates below,
and the no-cleanup/zero-read/zero-change policy. Source
rows change only through their already-authoritative RECORD, repository-code, or
uv-bootstrap inputs. An accepted code addition therefore changes the admitted
source/code manifest as designed; the incidental pyc created, omitted, renamed, or
rewritten for that source has no additional stable-identity effect.

#### 8.6.2 Operational classification of every actual site pyc

Every actual site pyc must satisfy exactly one class:

1. `SITE_DISTRIBUTION_NORMAL` — its normal grammar maps to one existing row for a
   third-party RECORD-owned source in the same selected distribution.
2. `SITE_PYTEST_REWRITE` — its exact pytest grammar maps to one existing
   third-party RECORD-owned source row. Removing only the complete suffix and
   appending `.py` must select that source.
3. `UV_BOOTSTRAP_NORMAL` — exactly
   `site-packages/__pycache__/_virtualenv.cpython-312.pyc`, mapped only to the
   exact uv-bootstrap source. This first-root file has mode `0o644`, size `4,159`,
   and SHA-256
   `08765615dd291d8a643581c2e7a0d3f891284aed32dd38a3940675488579f5f6`.
4. `SITE_SIX_OPTIONAL_INERT_ORPHAN` — optionally exactly
   `site-packages/__pycache__/six.cpython-312.pyc`, with absent sibling source and
   no RECORD/bootstrap owner. If present it must be a safe regular current-magic,
   `cpython-312` file with mode `0o644`, size `41,388`, and SHA-256
   `4e59431b1d92fe443cbdb1f76e065ece05b1c4f6cb4925168be8e9321f390e28`.
   Absence in another fresh root is valid. Changed present bytes, source
   appearance, ownership, another path, or a second site orphan fails.

The current first-root site observation is 1,075 pyc: 962 normal lexical names,
112 pytest-rewrite names, and the optional six orphan present. The 962 normal names
are 961 distribution-source mappings plus the one uv-bootstrap mapping. These
counts are an operational observation, not an admission requirement for another
root and not a stable-map cardinality.

#### 8.6.3 Operational classification of every actual repository pyc

Every actual repository pyc must likewise satisfy exactly one class:

1. `REPOSITORY_NORMAL` — its normal grammar maps to one existing
   repository-code-manifest-owned `.py` source row.
2. `REPOSITORY_PYTEST_REWRITE` — its exact pytest grammar maps to one existing
   repository-code-manifest-owned `.py` source row.
3. `REPOSITORY_MIGRATIONS_ENV_OPTIONAL_INERT_ORPHAN` — optionally exactly
   `migrations/__pycache__/env.cpython-312.pyc`, while `migrations/env.py` is
   absent and no admitted source or owner claims it. If present it must be a safe
   regular file with cache tag `cpython-312`, current magic `cb0d0d0a`, mode
   `0o644`, size `2,795`, and SHA-256
   `6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2`.
   It grants no authority of any kind.
4. `REPOSITORY_MIGRATIONS_FOUNDATION_OPTIONAL_INERT_ORPHAN` — optionally exactly
   `migrations/versions/__pycache__/0001_foundation.cpython-312.pyc`, while
   `migrations/versions/0001_foundation.py` is absent and no admitted source or
   owner claims it. The existing
   `migrations/versions/0001_foundation.sql` is not a Python source sibling and
   grants no Python source, import, or ownership authority. If present the pyc
   must be a safe regular file with cache tag `cpython-312`, current magic
   `cb0d0d0a`, mode `0o644`, size `25,415`, and SHA-256
   `b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d`.
   It grants no authority of any kind.
5. `REPOSITORY_POSTGRES_OPTIONAL_INERT_ORPHAN` — optionally exactly
   `src/scouting/storage/__pycache__/postgres.cpython-312.pyc`, while
   `src/scouting/storage/postgres.py` is absent and no admitted source or owner
   claims it. If present it must be a safe regular file with cache tag
   `cpython-312`, current magic `cb0d0d0a`, mode `0o644`, size `4,230`, and
   SHA-256
   `ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac`.
   It grants no source, repository-code, import, owner, environment, build, or
   semantic authority.

Each of these three source-absent repository predicates independently permits
absence in another fresh root. Each binds the exact path, absent exact `.py`
sibling, absence of admitted ownership, regular-file/no-link containment,
`cpython-312` tag, current `cb0d0d0a` magic, mode, size, and SHA-256 above.
Changed present bytes/header/mode, appearance of the exact Python sibling or an
admitted owner, or any other source-absent repository pyc fails. These predicates
are the entire repository orphan allowance; they do not authorize an arbitrary
orphan class, another path, a renamed file, or a fourth repository orphan.

The current first-root repository observation is 58 pyc in 19 `__pycache__`
directories: exactly 35 normal files mapped to present admitted sources, exactly
20 `cpython-312-pytest-9.1.1` files mapped to present admitted sources, and exactly
the three optional source-absent inert orphans above. A lexical filename census
therefore contains 38 normal-grammar names, but three of those names are the
source-absent inert orphans and are not mapped normal bytecode. No repository pyc
outside the admitted source map or one of the three exact repository predicates is
accepted; whole-repository traversal ensures such a file is denied and fails
admission rather than broadening authority.

#### 8.6.4 Operational evidence, three-role guards, and two-root rule

Every present mapped pyc still requires current `importlib.util.MAGIC_NUMBER`,
current cache tag, safe containment, an unambiguous source row, exact operational
path/hash/size/mode, and zero Python-role pyc read. Normal/pytest/bootstrap rows
bind their verified source row in the operational receipt. The exact optional-six
site predicate and three exact repository predicates remain four stable optional
predicates total; orphan presence is operational and grants no source authority.

Before outer launch, the master:

1. snapshots/classifies every current site and repository pyc/`__pycache__` path;
2. proves the control-role prefix empty, installs its absolute spelling in
   `PYTHONPYCACHEPREFIX`, and sets `PYTHONDONTWRITEBYTECODE=1`;
3. records the exact three installed encoding pycs as denied classified inventory,
   without opening their bytes during outer Python startup; and
4. after outer exit proves the whole in-place snapshot byte-identical and the
   control prefix identical and empty, without cleanup.

The outer CPython pre-guard allowance is exactly the launcher source open plus the
three verified encoding **source** rows in Section 8.0.1. It allows no installed
stdlib-pyc read and makes no audit-hook claim. The launcher's first user-code
verifier proves those rows and its inherited source descriptor, then installs the
guard. From that point the outer role denies every in-place pyc, `.pth`, Section
8.5 executable, and nonselected alternate-cache path.

Before admission, the launcher re-enumerates/classifies and requires equality with
the outer live snapshot, proves only the admission prefix empty, and starts the
admission child with its own guard and descriptor. After exit it requires zero
denied reads/executes/imports, byte-identical in-place state, and the same empty
admission prefix. After code-manifest freeze/build-ID formation it repeats the full
operation for only the rebuild prefix and child. Rebuild postconditions likewise
require zero denied reads, unchanged in-place state, and empty rebuild prefix.
Control, admission, and rebuild prefixes are distinct and never selected by
another role.

Actual pyc paths, bytes, hashes, sizes, modes, current 1,075-site count, current
58-repository/19-directory count, optional-orphan presence, three UUIDs, descriptor
numbers, device/inode values, and all three absolute prefix paths are operational.
The source-derived authority map, exact four optional predicates, three-role prefix
policy, exact bootstrap source rows, and denial policy are stable. A second empty
root may have different mapped pyc paths/counts/bytes and omit any optional orphan;
every present file must still classify and stay unread. Root equality never
requires operational inventory equality.

Negative tests cover an installed encoding-pyc read, absent/aliased/nonempty/reused
control prefix, control-prefix write, another pre-guard file-backed import,
claiming a pre-install audit observation, any role using another role's prefix,
in-place mutation, cleanup, unsafe/ambiguous pyc, wrong cache tag/magic/pytest
version, optional-predicate drift, and any new unclassified pyc.

### 8.7 RECORD ownership and runtime subset

Installed RECORD is ownership authority; `top_level.txt`,
`packages_distributions()`, names, and AST imports are advisory. Every concrete
normalized installed file has one owner. A normal import root has one owner.
Namespace sharing is allowed only with no contributor-owned `__init__.py`, contained
search locations, singular concrete child ownership, and no overlapping child.
Extension modules are parsed against complete frozen `EXTENSION_SUFFIXES`; native
origin is exact RECORD-owned. Site-root shared libraries require singular owner;
system/interpreter libraries use the separate interpreter closure.

Only after stage-0/Packaging bootstrap, exact `.pth`/editable-root closure, `L`,
`I`, extracted/installed/35-row executable policy, complete source-derived
site/repository pyc authority plus optional-orphan predicates,
interpreter/resources, and ownership freeze may W04 execute.
An observer records third-party module origins, namespace search locations,
extensions, site-root shared images, and owners. Every origin is pre-admitted and
unchanged; no `.pth`, executable, orphan pyc, bootstrap module, or unselected module
may become an origin.

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

The interpreter closure binds all three exact safe venv aliases and raw link chains
from Section 8.5.1, canonical wrapper alias, launch-time alias observation,
implementation/full version, ABI, physical executable SHA-256/size/mode, loaded
libpython and loader images. All three aliases resolve to the same frozen physical
Python 3.12.12. Stable identity contains verified root-independent alias topology and
interpreter-relative identity/digests, not a project-root or physical-path prefix.
Standard-library roots derive from that interpreter, exclude site-packages and all
operational pyc, and hash exact regular source/extension bytes, including the three
exact interpreter-bootstrap source rows in Section 8.0.1. The master invokes
the local control plane exactly as
`uv run --locked --no-sync python -S -B scripts/launch_wyscout_v5.py`; that
launcher invokes stage 0 exactly as
`uv run --locked --no-sync python -S -B scripts/admit_wyscout_v5_runtime.py`.
Except for the three preloaded encoding source rows verified before guard
installation, the exact site and repo source roots are manually added only after
the guard.
Imports outside repo, `L` ownership, the singular admitted Packaging bootstrap,
stdlib, built-in/frozen, or admitted loader/system paths fail.

Environment variables use only the exact closed outer and child maps in Sections
8.0.2 and 8.0.5. Their literal values, operational substitutions, required
absences, acyclic base digests, one-time envelope insertion, and complete actual
transport hashes are exhaustive; every unknown name fails. Locale, timezone, hash
seed, bytecode, thread, uv locked/no-sync/offline, proxy, coverage, dynamic-loader,
and Python-startup controls have the exact stated values or absences.
Network/provider interfaces are disabled. Before every output rename and manifest write, code,
stage-0/Packaging proof, three `.pth` classes/editable-root evidence, `L==I`,
extracted/installed actual bytes, all 35 executables, all three aliases, complete
source-derived site/repo pyc classification/no-read/no-change state, the applicable
control/admission/rebuild role's empty alternate prefix, inherited source
descriptor, interpreter, stdlib, environment, and 17 resources are rechecked.

### 8.9 Exact stable code/environment manifest

The admitted environment has two truth domains:

```text
stable code/environment manifest:
  repo-relative code bytes and import-coverage proof
  pyproject/lock digests and selected L
  Packaging-bootstrap bytes/proof and stable ordered selector keys
  exact uv-bootstrap-deny and normalized editable-root evidence
  wheel declarations and cache associations
  verified extracted-tree and installed RECORD-owned bytes
  exact INSTALLER/REQUESTED rows
  total 35-row classed executable census and stable normalization
  source-complete site/repository pyc authority map and optional-orphan predicates
  uv version and physical executable digest
  exact local launcher row, role, ordered argv, acyclic bootstrap construction,
    accepted completed bootstrap tuple, encoding-source verifier, outer prefix
    policy, and inherited source descriptor
  exact locked/no-sync outer/admission/rebuild argv, roles, three prefix policies,
    entry-point paths/bytes, inherited source descriptors, closed child
    environments, and exact canonical input envelopes
  exact bounded child-result frame plus exhaustive v2 payload schemas and
    input/result equalities and sole-control ownership
  exact three-alias topology plus interpreter/libpython/loader/stdlib digests
  exact 17-resource digest
  canonical environment values

operational admission evidence:
  actual resolved uv executable path
  actual root-bearing launch spelling and process-role/argv observation
  actual cache root, symlink text and archive-v0 opaque target
  actual python/python3/python3.12 aliases, link text/chains and wrapper shebang
  actual root-bearing executable paths/bytes/hashes
  actual .pth/bootstrap/direct_url/uv_cache paths/bytes/hashes/clocks
  actual site/repository pyc paths/bytes/hashes/counts/modes
  control/admission/rebuild run IDs and all three absolute alternate-prefix paths
  launcher/entrypoint/result descriptor numbers, nonces, and bounded diagnostic bytes
  complete actual outer and child transport-environment SHA-256 values
  launcher/entry-point device, inode, link count and root-bearing path observations
  no-site/Packaging observations and per-role no-read/no-change/empty-prefix proof
```

The stable manifest algorithm is `w04-code-environment-admission-v11`. Component
digests are length-framed, sorted by declared stable key, and combined exactly as:

```text
environment_digest = SHA256(canonical_json({
  "selector": <frozen Python/platform/ordered-tag selector>,
  "selector_bootstrap_digest": <byte-admitted Packaging 26.2 proof>,
  "lock_inputs_digest": <pyproject-plus-uv-lock digest>,
  "editable_root_digest": <stable normalized editable root and metadata>,
  "venv_bootstrap_digest": <exact _virtualenv files plus deny policy>,
  "selected_lock_closure_digest": <complete L digest>,
  "wheel_declaration_digest": <selected declarations digest>,
  "extracted_runtime_digest": <all verified extracted trees>,
  "installed_record_runtime_digest": <mapped RECORD-owned/base generated bytes>,
  "executable_census_digest": <35 reviewed classed stable rows>,
  "pyc_policy_source_map_digest": <source-complete stable authority map and orphan predicates>,
  "uv_version": <exact version>,
  "uv_physical_sha256": <exact executable bytes digest>,
  "local_launcher_control_digest": <launcher row, role, exact argv, acyclic w04-outer-environment-bootstrap-v1 construction, completed bootstrap tuple, encoding-source verifier, control-prefix policy, and inherited launcher-source descriptor policy>,
  "process_launch_contract_digest": <the exact outer and two exact child ordered locked/no-sync argv, uv-input maps and admitted uv input-to-Python environment transformation, three roles, unique chronology, three prefix policies, source-descriptor code rows, closed child environments, and w04-child-input-v1 transport>,
  "child_result_contract_digest": <frame, exhaustive v2 role payload schemas, exhaustive role input schemas, input/result/receipt/layer equality, inherited entrypoint descriptors, diagnostics, timeout/EOF checks, and sole-control ownership>,
  "interpreter_digest": <alias topology and interpreter/libpython/loader closure>,
  "stdlib_digest": <exact standard-library bytes>,
  "local_resource_digest": <exact 17-path resource set>,
  "environment_values_digest": <exact closed outer/child present maps, required-absent names, operational substitutions, insertion rules, and complete-transport comparison algorithms>
}))
```

It contains no own ID/path, clock, actor, Git state, control/admission/rebuild run ID,
launcher/entrypoint/result descriptor number, nonce, diagnostic bytes, device/inode
observation, absolute alternate-prefix path, output digest, uv
absolute/root-bearing launch path, cache absolute path, actual alias/shebang/executable path/hash,
root-bearing `.pth`/`direct_url` bytes, `uv_cache` clocks, or actual pyc path/hash/
count. Operational evidence cannot be substituted into a stable component.
Its identity and sole path are:

```text
code_manifest_sha256 = SHA256(canonical_manifest_bytes)
code_manifest_id = UUIDv5(
  w04_dependency_namespace,
  "post_integration_code_environment_manifest:" + code_manifest_sha256)
data/manifests/wyscout/v5/code/
  <code_manifest_sha256>.code-manifest.json
```

The admission process returns these canonical manifest bytes before build identity
exists; the exact local-control launcher writes or confirms the immutable path above and only
then invokes Section 9. Independent review reproduces the complete manifest from
admitted bytes. Negative
tests cover launcher/bootstrap tuple/acyclic base digest/one-time insertion/
complete transport hash/role/argv/environment/encoding-source/
control-prefix/source-descriptor/path/mode/size/digest/link/checkpoint drift;
child-entrypoint descriptor and persistent replacement drift; the documented
transient same-trust-domain residual; child result magic/version/length/UTF-8/
canonical-JSON/closed input/result schema/environment-envelope disagreement/nonce/
role/code identity/digest/EOF/timeout/exit/order
drift; diagnostics overflow or
authority substitution; lock/tag selection drift, cache link/target/tree/RECORD drift, false
wheel-ZIP claims, installed payload/RECORD/base-row drift, Packaging bootstrap or
extra-import drift, `.pth` execution/bootstrap/editable metadata drift, executable
class/owner/target/body/shebang/mode/normalization/census drift, unsafe/class-
ambiguous/read pyc, optional-orphan drift, incomplete source authority, any of the
three aliases or either relative alias chain drifting, interpreter/libpython/
stdlib/resource drift, behavior-environment drift, an unknown-build stage-0 prefix,
prefix reuse/non-emptiness, a missing/reordered `--locked`/`--no-sync`, plain
`uv run`, a sync/reconciliation attempt, alternate argv/interpreter/entry point,
generated-script execution, entry-point byte/role/TOCTOU drift, manifest-writer or
build-calculator overlap, early rebuild-prefix/envelope formation, generic config
or scan selection, and early/placeholder build-ID formation.

## 9. Build identity, deterministic bytes, and two-root proof

Canonical build-input version is `w04-wyscout-build-id-v12`. It contains:

- tenant and exact source manifest;
- identity bundle/queue/ruleset/accepted corrections;
- field, possession, feature, and identity decision/review/acceptance IDs/digests;
- all product schemas, exact keys, Gold coverage equations, and neutral context;
- exact window/cutoff values and the five strict dependencies;
- repository code manifest and `pyproject.toml`/`uv.lock` digests;
- selected all-groups `L`, Packaging bootstrap/selector proof, wheel declarations,
  stable cache associations, extracted trees, installed RECORD-owned bytes/base
  rows;
- stable uv-bootstrap-deny and normalized editable-root evidence;
- all 35 classed executable rows, with canonical wrapper normalization for E/P and
  exact root-independent W bytes;
- the source-complete site/repository pyc authority map plus exact optional-six,
  migrations-env, migrations-foundation, and PostgreSQL inert-orphan predicates,
  never operational root-bearing executable or pyc bytes/inventories;
- uv version and physical executable digest, never uv absolute path;
- exact local-control launcher row, role, ordered argv, acyclic outer-environment
  algorithm, accepted completed bootstrap tuple, encoding-source first-instruction
  verifier, inherited source-descriptor policy, closed child environments/input
  envelopes, bounded child-result contract, and sole-control ownership;
- exact root-independent process-launch contract: the outer and both child ordered
  `uv run --locked --no-sync python -S -B` argv, all three roles/prefix policies,
  unique manifest/build-ID/rebuild-prefix chronology, launcher/child inherited
  source-descriptor contracts, exhaustive role input schemas and all three
  repository-owned entry-point path/byte rows;
- exact safe three-alias topology, interpreter/libpython/loader, and
  standard-library stable digests;
- exact 17 local resources and fixed environment.
- exact `w04-rebuild-invocation-v1` fields, four authority rows, five dependency
  rows, immutable code-manifest identity, and schema-bound receipt/layer paths.

```text
build_id = SHA256(canonical_json(all stable semantic build-input fields))
```

Runtime `R`, actual alias/raw-link/physical path spellings, root-bearing executable
paths/bytes, actual `.pth`/editable metadata paths and `uv_cache` clocks, actual pyc
inventory/bytes/counts, uv absolute path, cache absolute root/opaque key,
control/admission/rebuild run IDs, launcher/entrypoint/result descriptor numbers,
nonces/diagnostic bytes, complete actual transport-environment hashes,
device/inode observations,
all three operational alternate-prefix absolute paths, output root, host clocks, Git
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
- byte-admitted Packaging selector bootstrap and frozen ordered tags;
- `L==I`, wheel selection, extracted/installed stable ownership;
- exact uv-bootstrap deny and normalized editable-root evidence;
- the total 35-row executable census/classes/owners, with byte-identical E/P bodies
  after the one exact canonical shebang token and exact W bytes;
- the complete source-derived site/repository pyc authority map and all four exact
  optional orphan predicates (not actual pyc bytes/inventories or current counts);
- exact normalized launcher bytes/row/bootstrap/encoding-source verifier,
  acyclic environment algorithms, three-prefix/source-descriptor, exhaustive
  child-input/result, rebuild-invocation, and ownership contracts;
- resources, alias/interpreter/stdlib/environment stable evidence;
- unknown-kind paths, states, envelope bytes, and digests; and
- normalized runtime origin/owner observations.

Operational control/admission/rebuild run IDs and alternate-prefix absolute paths/clocks,
uv/cache paths, actual alias/link/shebang/executable
paths/hashes, actual root-bearing editable-install bytes/clocks, and actual site/repo
pyc inventories may differ only in their documented operational fields. Any
optional orphan may be absent, and mapped pyc counts/paths/hashes may differ, while
every present file must still classify and remain denied. None leaks into stable
identity.

## 10. Quality, health, card, gate, and serial ownership

Quality requires exact source counts/country equalities, unique match/action IDs,
two teams per match, zero match/team conflicts, 226,038 zero actors, measured
lineup/bench/substitution counts, 23/8 unresolved references, period/coordinate
constraints, accepted authorities, exactly five strict dependencies, neutral
result-independent facts, zero minute/per-90 output, separate source and Gold
coverage equations, complete all-groups environment, constructive no-site/Packaging
startup, exact three-`.pth` and editable-root closure, total 35-row executable
census, exact three-alias interpreter closure, source-complete site/repository
bytecode authority, constructive classification/denial of every actual pyc,
three-role ordering with all three exact empty alternate prefixes, exact
locked/no-sync local launcher and its encoding-source/control-prefix/inherited-
descriptor/exhaustive-child-result contract, both exact child argv and repository
entry points, exact resources, sole writers, quarantine
reconciliation, and two-root equality.

Health outputs are:

```text
reports/phase-gates/W04/data-health.json
reports/phase-gates/W04/data-health.md
```

Controlling JSON includes source and Gold coverage separately; source/identity/
temporal/rights metrics; backlog/corrections; rejected field/record counts; unknown
states/digests/collision status; `L`, `I`, `L==I`; wheel/cache/extracted/installed
evidence; Packaging bootstrap/ordered tags; uv-bootstrap/coverage-hook/editable-root
evidence; exact actual and normalized 35-row executable census with classes/owners/
aliases; the exact three-alias topology; source-complete pyc authority-map digest;
all four exact optional orphan predicates and each presence; first-root operational
site/repository class inventories including repository `58 pyc / 19 cache
directories = 35 mapped normal + 20 mapped pytest + migrations-env +
migrations-foundation + PostgreSQL source-absent inert orphans`;
control/admission/rebuild process IDs and prefix roles; all three exact relative
prefixes plus operational absolute paths and empty-before/unchanged-empty-after
proof; per-role zero in-place-pyc read/no-change proof; the exact three
encoding-source origin/size/digest observations and explicit pre-guard status; zero
installed-encoding-pyc reads/control-prefix writes; the exact local launcher
bootstrap/path/byte/role/argv/inherited-source-descriptor row; the exhaustive
child-result schemas, frame, diagnostics, timeout, EOF, and cross-field
observations; both exact child argv and entry-point
path/byte/role/inherited-descriptor/checkpoint rows; the explicit transient
replace-and-restore residual; uv locked/no-sync enforcement and observed physical
digest/alias; loaded
subset `R`; uv/alias/interpreter/stdlib/resources; path ownership; and two-root
equality.

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
no-site/bootstrap/editable-root, executable/bytecode, quarantine, manifest, card,
independent-review, resource, and exact-path checks pass. No report is accepted
until each independent recommendation is `PASS`.

Sole ownership is serial. Authority candidates/reviews/acceptances have distinct
owners. Bronze owns known records and both quarantines. Identity owns only its three
generated roots. Entity/action/lineup/possession/player-match Silver owners write
only named families; Silver manifest is separate. Gold/temporal owns Gold, Gold
manifest, boundary receipts. Rebuild only invokes and writes invocation receipt.
The local-control implementer owns launcher code/tests. At runtime the accepted
launcher alone writes or confirms the immutable code/environment manifest and
calculates the build ID. Admission owns admission code/report and constructs/
returns canonical manifest bytes only; it cannot write the manifest or calculate
the build ID. Rebuild retains invocation-receipt ownership and every named
serializer retains its product/layer/boundary-receipt ownership; the launcher only
verifies their returned identities. Quality, health, card/reviews, master
verification, gate, acceptance Git, and ledger are later serial owners. Only
disjoint Silver families may overlap.

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
| 21L | local-control implementer/master | future exact `scripts/launch_wyscout_v5.py` plus acyclic bootstrap digest, first-instruction guard, whole-repo pyc census, source-descriptor/closed child-input/result/diagnostics, three-prefix chronology, TOCTOU, manifest-write and build-ID-order tests | transient control only; R14 names but does not create script |
| 22 | admission implementer/master | future exact `scripts/admit_wyscout_v5_runtime.py` plus tests: locked/no-sync no-site/Packaging bootstrap, pre-build admission prefix/process, closed input envelope, `.pth`/editable root, `L==I`, 35 executables, three aliases, source-complete pyc authority/classes, canonical manifest construction/result frame | offline constructor only; cannot write manifest/calculate build ID; R14 does not create script |
| 23 | rebuild entrypoint/master | future exact `scripts/rebuild_wyscout_v5.py`, locked/no-sync integration test, exact rebuild-input envelope, bounded result frame, invocation receipt only | only after manifest readback, build ID, then rebuild-prefix creation; calls sole writers; R14 does not create script |
| 24 | shared integration/master | named shared exports only | serial |
| 25 | code-manifest invocation/master via accepted launcher | exact immutable code manifest, launcher-computed build ID handoff, and admission report/return | sole runtime manifest writer/build calculator; after code freeze, before rebuild |
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
   metadata, egg, external site root, or any `.pth` outside the exact three denied
   classes.
8. For every `L` member verify selector containment, extracted RECORD/tree,
   installation mapping, `INSTALLER=b"uv"`, empty `REQUESTED`, and rewritten RECORD.
9. From the repository root invoke only exact
   `uv run --locked --no-sync python -S -B scripts/launch_wyscout_v5.py` under
   role `W04_LOCAL_CONTROL`. Have the master alone sample `control_run_id`,
   safely create/prove empty
   `data/working/wyscout/v5/.staging/control/control_run_id=<uuid>/runtime-pycache/`,
   set its absolute path plus `PYTHONDONTWRITEBYTECODE=1` before `uv`, and preserve
   the exact master-opened `O_RDONLY|O_NOFOLLOW` launcher source descriptor through
   `uv` via strict-decimal `W04_LAUNCHER_SOURCE_FD`. Positively prove `fstat`,
   offset, inheritable/`FD_CLOEXEC`, complete bytes/digest, only-admitted-FD, and
   no-reopen behavior in outer Python. Trace the exact three preloaded modules
   `encodings`, `encodings.aliases`, and `encodings.utf_8`; require their exact
   source origins/sizes/digests, zero installed-pyc reads, zero prefix writes under
   `-B`, and an empty unchanged control prefix after exit. Reject the former
   built-in/frozen-only claim and never attribute pre-install events to the hook.
   Stop if this exact outer launch cannot reproduce the source-only result.
   Require the first user-code verifier before another file-backed import, then the
   audit guard. Re-arm `FD_CLOEXEC` on the retained launcher descriptor before
   either child, prove neither child inherits it, keep it open in the launcher
   through both children, and close it under the exact ownership contract.

   Construct `E_outer_base` with every exact present and absent name and without
   `W04_BOOTSTRAP_TUPLE_B64`; apply exactly the admitted uv input-to-Python
   transformation and nine declared operational substitutions; hash the canonical
   base object; place that digest into the
   tuple; canonical-encode once; insert the encoded tuple; and independently
   compare the complete actual transport hash. Prove the graph is acyclic and
   reject inclusion of the tuple in its own base digest, an omitted/extra name,
   an undeclared substitution, tuple re-encoding, recursion/fixed-point search,
   placeholder digest, complete-hash injection, or master/launcher comparison
   inequality.
   
   Have the launcher alone sample distinct admission/rebuild UUIDs if desired, but
   create only the retained admission prefix before admission. For each unchanged
   exact child argv, preopen the
   exact role entrypoint with `O_RDONLY|O_NOFOLLOW`, pass exactly its strict-decimal
   `W04_ENTRYPOINT_SOURCE_FD` plus the distinct result writer, and prove the child
   first/final descriptor observations and launcher retained-descriptor/path
   postcheck. Exactly two nonstandard descriptors, not result-only, are inherited.
   Exercise missing/closed/substituted/extra/non-preserved descriptors, premature
   close, offset/EOF drift, role/path/bytes/digest/argv/environment/nonce mismatch,
   persistent replacements at every checkpoint, and the documented unobservable
   transient replace-and-restore residual.

   Exhaustively decode `W04_CHILD_INPUT_B64` as the sole canonical value
   transport. Require all sixteen common keys, exactly eight admission keys or
   exactly ten rebuild keys, all stated types/nullability/grammars/cardinalities
   and orders, the four ordered authority rows, five canonically sorted dependency
   rows, twenty-five rebuild-invocation keys, exact FDs/nonce/launcher/repository
   digests/argv/prefix values, and closed child environments. Recompute the
   acyclic child base digest before inserting the envelope, then independently
   compare the complete actual environment hash to the result. Reject an unknown
   environment name; unknown/duplicate/cross-role/missing/null/mistyped envelope
   field; environment/envelope disagreement; argv value; stdin/config sidecar;
   opaque/generic config; newest/scan selection; new resource/provider access; or
   any alternate transport.
   
   Exercise the exact frame, SHA-256, nonce, EOF, diagnostics, timeout, and exit
   ordering with exhaustive `w04-child-result-v2` decoding. For admission, require
   all nine exact result keys, byte-identical canonical manifest base64url,
   manifest/environment/repository-code equalities, exactly twenty component proofs
   in declared order, exact row schemas, and proof digests. For rebuild require all
   six exact result keys, build/run/prefix equality, exact receipt row, exactly
   three ordered layer rows, and all seventeen exact final-recheck keys and
   equalities. Reject every missing, unknown, duplicate, mistyped, null,
   noncanonical, unordered, inconsistent, over-cardinality, replayed, truncated,
   oversized, extra-byte, nonzero-exit, or diagnostic-substituted result. Require
   the launcher alone to publish/read back the manifest and only then calculate
   the complete build ID, derive/create/prove the build-scoped rebuild prefix,
   construct the rebuild envelope/environment, and start rebuild. Bind the exact
   immutable code-manifest identity, build ID, run ID, prefix, twenty-five
   schema-bound invocation fields, receipt path, and three layer paths through the
   rebuild result. Reject an early rebuild directory/prefix/envelope/environment,
   unknown-build admission path, placeholder/partial build ID, second ordering,
   flag/argv/prefix reuse, sync, site startup, generated scripts, another
   writer/calculator, any prefix/in-place-pyc change, and launcher
   product/layer/receipt writes.
10. Require exactly `_virtualenv.pth/_virtualenv.py`, `a1_coverage.pth`, and
    `scouting_intelligence.pth`; verify their exact class/bytes/hash/size/mode/owner
    predicates and zero execution. Prove root-normalized editable `.pth` and
    `direct_url`, operational-only `uv_cache` clocks, exact stable metadata, and
    equal stable editable-root digests across two roots.
11. Prove exactly three distinct mode-`0o755` symlinks: `python ->` the exact
    physical Python 3.12.12 bytes/ABI/mode, `python3 -> python`, and
    `python3.12 -> python`. Require both relative chains contained, all three
    resolving identically, only canonical `python` in every wrapper shebang, and
    the locked/no-sync uv `python -> python3` launch observation operational only.
    Reject a missing or
    fourth alias, raw-target drift, cycle, extra hop, escape, inode alias, physical
    mismatch, or incidental `sys.executable` equality.
12. Census exactly 35 `../../../bin` rows across 21 owners and exactly one class
    each: 33 direct E wrappers, only pip 26.1.2 `pip3.12` in P, and only the
    byte-identical Ruff 0.16.0 `.data/scripts` payload in W. Verify every path,
    owner, target/authority, bytes/hash/size/mode, collision rule, stable row, and
    zero admission execution/rebuild read or execution.
13. Reject a missing/extra/multiply classified bin row; an undeclared pip alias;
    changed base pip wrapper; Ruff entry point; second wheel script; any wheel
    script rewrite/`#!python` trigger; unsafe name; link/hardlink; and any alternate
    wrapper interpreter/shebang/root normalization.
14. Build the stable authority map from every admitted RECORD-owned third-party
    `.py`, repo-code-manifest-owned `.py`, and exact uv-bootstrap source regardless
    of pyc presence. Classify every actual pyc against it or the exact optional
    six, migrations-env, migrations-foundation, and PostgreSQL orphan predicates.
    Record the first-root observations: site
    1,075 = 961 mapped distribution normal + one mapped bootstrap normal + 112
    mapped pytest + optional six orphan; repository 58 in 19 cache directories =
    35 mapped normal + 20 mapped pytest + exactly three present source-absent inert
    orphans:
    `migrations/__pycache__/env.cpython-312.pyc`,
    `migrations/versions/__pycache__/0001_foundation.cpython-312.pyc`, and
    `src/scouting/storage/__pycache__/postgres.cpython-312.pyc`. Verify every exact
    path, absent `.py` sibling, magic, tag, mode, size, and digest; prove the
    Foundation SQL file confers no Python authority. Reject unsafe/ambiguous/
    wrong-tag/magic/pytest/source ownership, changed present bytes, source
    appearance, another path or orphan, pyc read/change/new file, cleanup, or
    non-empty alternate prefix. Prove another root may independently omit any of
    the four optional orphans and vary mapped pyc counts/paths/hashes without
    changing stable authority.
15. Prove uv version/physical digest stable while its absolute path is operational
    only; assert the exact 17 resources and disjoint guard categories.
16. Prove `pydantic -> pydantic-core` and `polars -> polars-runtime-32`, native
    ownership, `R subset-of L`, and no runtime expansion/retry.
17. Reject duplicate file/package/namespace/native ownership, mutation after freeze,
    extra read/write, broad resource discovery, writer overlap, or serializer bypass.

Stop rather than improvise if a path/digest/count/lock/installed set changes; a
truthful clock/authority is missing; unknown kind would be guessed; payload would
select family; excluded/source path would be read; action UTC/minutes would be
fabricated; absent wheel would be claimed verified; no-site/Packaging bootstrap,
`.pth`/editable-root, executable census/alias, or pyc classes cannot satisfy the
exact rules; ownership is ambiguous; runtime wants an unselected distribution; a
collision would mutate a path; writers overlap; or dependency, lock, cleanup,
migration, provider, network, rights, architecture, local-only, ignore, remote,
storage-root, or deployment change is needed.

R14 closes the returned R13 master findings and retains the accepted R13 and returned
independent R8 closures without self-approval. R14 created or modified only this
design and its assigned return under the project root; it created no parent-workspace
report path, directory, or cleanup obligation. Implementation
begins only after master and a separate independent reviewer accept this standalone
design.

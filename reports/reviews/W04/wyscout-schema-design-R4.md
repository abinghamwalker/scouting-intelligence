# W04 Wyscout v5 canonical schema and deterministic rebuild design — R4

Status: **implementation design for master and independent review; not self-approved**

This document replaces R3 in full. It is the standalone design for the local-only W04
Wyscout Figshare v5 Bronze-to-Gold proof. It retains the accepted source seam, Gold
grain, minute suppression, Gold coverage equations, and Silver player-match fact, and
closes the six defects returned against R3. It does not alter acquisition, source
rights, architecture, dependencies, migrations, or the local-only boundary.

The binding measured evidence is:

- completion manifest
  `data/source/wyscout/v5/completion-manifest.json`, 6,803 bytes, SHA-256
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- accepted profile
  `reports/phase-gates/W04/source-schema-profile.md`, SHA-256
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- source availability `2020-01-28T14:24:27Z` and actual local acquisition
  `2026-07-29T15:51:08.598589Z`;
- completion classification `wyscout_figshare_v5_cc_by_4`, licence `CC-BY-4.0`,
  restricted project control, and required attribution;
- 7 direct source objects, 10 separately durable admitted members, 4 directory-only
  exclusions, 7 competitions, 142 teams, 3,603 players, 1,826 matches, and
  3,071,395 event records; and
- the accepted adapter in `src/scouting/sources/wyscout.py`, which writes
  `objects/<name>`, `archive-members/<name>`, and `completion-manifest.json`.

No provider access, excluded payload read, runtime label guessing, container, external
service, hosted artifact, dependency change, migration, or export is authorised.

## 1. Claim boundary and global invariants

The permitted claim is a frozen historical engineering and player-evidence proof. It
does not establish current players, live coverage, provider continuity, women or youth
coverage, exact minutes, commercial-product equivalence, recruitment relevance, or
prospective benefit.

The implementation invariants are:

1. A source path is read only when the accepted completion document declares that
   exact `object_path` or `member_path`.
2. `matches.zip` and `events.zip` are hashed source evidence but are never opened
   downstream. The four scope exclusions have no admitted payload path and are never
   read or transformed.
3. Provider record `id` is event-record identity. `eventId` is taxonomy identity.
   Names are display evidence, never identity or semantic matching keys.
4. Source JSON numbers are parsed as `Decimal`; event time is period-relative
   evidence. No second-half UTC, half-time duration, terminal, or continuous match
   clock is fabricated.
5. Project field and possession semantics exist only after the exact accountable
   authority route in Section 3. Unknown decisions remain `UNMAPPED`.
6. Every evidence dependency uses an existing `DependencyKind`. Match and action rows
   are row lineage, not invented evidence-dependency kinds.
7. Bronze, Silver, and Gold semantic bytes contain no run ID, host path, run clock,
   elapsed runtime, operational trace, or generated-at clock.
8. The existing `TemporalEvidence` and `RetrievalResult` contracts are unchanged.
   Their truthful generation clock is supplied only at the serving/retrieval boundary.
9. The implementation identity is the digest of a verified post-integration code
   manifest, not a branch, tag, commit label, or arbitrary checkpoint string.
10. Rights, identity, cutoff, authority, lineage, partition, and reconciliation
    failures are fail-closed and cannot be averaged away by coverage.

## 2. Exact completion-declared source seam

The source root is exactly `data/source/wyscout/v5`. The completion document is read
first, its exact digest is checked, and it becomes the only source-path authority.
Normalised POSIX-relative paths must remain beneath the resolved root, must not be
symlinks, and must match the completion values byte for byte.

### 2.1 Direct objects

| Completion `object_path` | Bytes | SHA-256 | Downstream access |
| --- | ---: | --- | --- |
| `objects/competitions.json` | 1,209 | `39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1` | read |
| `objects/teams.json` | 27,404 | `9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d` | read |
| `objects/players.json` | 1,737,347 | `877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e` | read |
| `objects/matches.zip` | 645,097 | `c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9` | never opened |
| `objects/events.zip` | 77,323,413 | `877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45` | never opened |
| `objects/eventid2name.csv` | 1,001 | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` | read |
| `objects/tags2name.csv` | 1,754 | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` | read |

### 2.2 Separately durable admitted members

| Completion `member_path` | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `archive-members/matches_England.json` | 380 | 1,694,720 | `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29` |
| `archive-members/matches_France.json` | 380 | 1,707,222 | `851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea` |
| `archive-members/matches_Germany.json` | 306 | 1,377,328 | `6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9` |
| `archive-members/matches_Italy.json` | 380 | 2,019,196 | `afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725` |
| `archive-members/matches_Spain.json` | 380 | 1,705,380 | `9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce` |
| `archive-members/events_England.json` | 643,150 | 188,888,614 | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` |
| `archive-members/events_France.json` | 632,807 | 186,374,196 | `18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317` |
| `archive-members/events_Germany.json` | 519,407 | 152,916,631 | `2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3` |
| `archive-members/events_Italy.json` | 647,372 | 190,544,685 | `b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84` |
| `archive-members/events_Spain.json` | 628,659 | 184,164,406 | `b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154` |

All sizes and digests are streamed and verified before parsing. For each country, the
distinct event `matchId` set must equal the match `wyId` set: England 380, France 380,
Germany 306, Italy 380, and Spain 380. Any obsolete inferred layout is forbidden.

## 3. Normative local semantic authorities

The profile proves shapes, counts, key membership, and literal local map bytes. It
does not prove field meaning, possession boundaries, ownership, or event-to-possession
semantics. Those are explicit **project-defined decisions**, not provider-native
claims. Ownership of a file does not establish semantic truth; the accountable route
below does.

### 3.1 Exact local evidence inputs

Both authority routes must bind these immutable local inputs:

| Input | Exact path | SHA-256 | Clock treatment |
| --- | --- | --- | --- |
| completion | `data/source/wyscout/v5/completion-manifest.json` | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` | `2020-01-28T14:24:27Z` upstream; locally received later |
| measured profile | `reports/phase-gates/W04/source-schema-profile.md` | `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649` | not a separate temporal dependency; its use becomes knowable only with the authority acceptance clock |
| event numeric-key map | `data/source/wyscout/v5/objects/eventid2name.csv` | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` | `2020-01-28T14:24:27Z` |
| tag numeric-key map | `data/source/wyscout/v5/objects/tags2name.csv` | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` | `2020-01-28T14:24:27Z` |

The map digests prove the locally frozen numeric-key/label association only. A label
does not itself prove a control or possession meaning.

### 3.2 Field decision, independent review, and acceptance

The field route has four immutable artifacts:

```text
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json
configs/schema/wyscout-v5-field-registry-v1.yaml
reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json
```

The first is a master-authored decision record, not a provider assertion. Its strict
canonical JSON schema is:

```text
schema_version: 1
decision_id: w04-wyscout-field-semantic-decisions-v1
source_id: wyscout-soccer-match-events-figshare-v5
authority_class: project_defined_reviewed_semantics
decided_by: UUID ActorId
decided_at: canonical UTC
bound_inputs:
  completion_sha256: exact digest
  profile_sha256: exact digest
  event_map_sha256: exact digest
  tag_map_sha256: exact digest
decisions:
  - record_kind: exact kind
    json_path: exact path
    source_shape: exact measured type set
    decision: TRANSFORM | PRESERVE_UNMAPPED | FORBIDDEN
    canonical_field: string | null
    rationale: non-empty local decision text
    source_support: STRUCTURAL | PROJECT_SEMANTIC
unknown_field_policy: UNMAPPED
unknown_record_kind_policy: REJECT_PARTITION
runtime_label_matching: forbidden
provider_native_semantic_claim: false
```

The registry binds the complete decision-record digest and all four input digests.
Every measured path is exhaustively either transformed, preserved `UNMAPPED`, or
forbidden. The six literal string `"null"` substitution containers receive explicit
decisions; absence of a reviewed decision means `PRESERVE_UNMAPPED`, never empty-array
coercion. Mixed IDs, string `subEventId`, coordinates, and event decimal time retain
their measured source types unless an exact decision authorises a transform.

An independent reviewer writes only the independent report and records the candidate
registry digest and decision digest. The master then writes the acceptance JSON only
after a `PASS` recommendation. Its strict fields are:

```text
schema_version, acceptance_id, artifact_id, artifact_sha256,
decision_id, decision_sha256, independent_review_path,
independent_review_sha256, accepted_by (ActorId), accepted_at (UTC),
status="accepted", supersedes=null
```

`accepted_at` is the truthful availability instant of the normative field authority.
It cannot predate `decided_at` or the independent review completion. Acceptance bytes
do not become an input to the registry digest, so no digest is circular.

### 3.3 Possession decision, independent review, and acceptance

The possession route begins only after accepted field semantics and has the analogous
four artifacts:

```text
reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json
configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml
reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json
```

The decision record additionally binds the accepted registry and field-acceptance
digests. Each mapping key is an exact predicate over numeric `event_id`, nullable
numeric `subevent_id`, sorted required tag IDs, and sorted forbidden tag IDs. Its
decision is one of:

```text
CONTROL, CONTESTED, DEAD_BALL, RESTART, NON_CONTROL_ADMIN, UNMAPPED
```

A non-`UNMAPPED` row must explicitly state `control_team_source`,
`opens_control`, `closes_control`, `dead_ball_attachment`, and
`contested_attachment`, plus project rationale and accountable `decided_by`. The
taxonomy is normative only for W04 project derivation. It must set:

```text
unknown_combination_policy: UNMAPPED
unknown_name_matching: forbidden
runtime_label_matching: forbidden
provider_native_possession_claim: false
period_boundary_policy: close
simultaneous_cross_team_policy: uncertain_boundary
```

No substring, fuzzy label, current name, undocumented football convention, or runtime
guess can populate a mapping. An unknown remains `UNMAPPED`, is not possession
eligible, and reduces or suppresses the relevant applicability when the taxonomy says
the action class should have been resolved. The possession acceptance record has the
same strict acceptance fields and clock ordering as the field record. Its
`accepted_at` is the truthful possession-authority availability instant.

The registry and taxonomy digest are SHA-256 over canonical JSON of the fully parsed
YAML, with sorted keys, arrays in schema-declared order, canonical booleans/integers/
nulls, UTF-8, and no self-digest. Existing bytes are idempotent only when identical.

## 4. Non-circular strict source-manifest bridge

A single serial bridge converts acquisition evidence into the existing strict
`SourceSnapshotManifest`. It requires an explicit immutable `TenantContext`;
`tenant_id` has no default and `club_id` is nullable but fixed.

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

The UUID input does not include the UUID or serialized manifest digest. The strict
manifest has `schema_version=1`, provider `Wyscout`,
`provider_schema_version="figshare-v5+completion-v1+bridge-v1"`, exact acquisition and
availability clocks, and the explicit tenant and deterministic trace. Its
classification is `restricted`, derived data and internal review allowed, export
false, attribution required, with the exact completion attribution.

### 4.1 Exactly 18 `SourceFileDigest` rows

`files` is a tuple in the following exact order. No row may be omitted or added.

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

Tests assert both `len(files) == 18` and the ordered shape
`completion + 7 objects + 10 admitted members`. Exclusions are coverage evidence,
not file rows, because they have no admitted payload path or payload digest.

### 4.2 Field-exact strict `DataCoverage`

This is the exact existing contract, not the richer Gold structure. The six
`CoverageDimension` objects are a tuple in this exact order:

```text
CoverageDimension(
  name="source_object_integrity",
  coverage=1.0, observed_count=7, expected_count=7)
CoverageDimension(
  name="admitted_member_integrity",
  coverage=1.0, observed_count=10, expected_count=10)
CoverageDimension(
  name="match_partition_presence",
  coverage=1.0, observed_count=5, expected_count=5)
CoverageDimension(
  name="event_partition_presence",
  coverage=1.0, observed_count=5, expected_count=5)
CoverageDimension(
  name="partition_match_id_alignment",
  coverage=1.0, observed_count=5, expected_count=5)
CoverageDimension(
  name="scope_exclusion_directory_only",
  coverage=1.0, observed_count=4, expected_count=4)
```

Each `coverage` and `overall` is a strict Python `float`, specifically `1.0`; each
count is a strict non-negative `int`; no `expected_count` is null here.

```text
DataCoverage(
  overall=1.0,
  dimensions=(<the six objects above in order>),
  missing_dimensions=(),
)
```

In canonical JSON, both tuples serialize as JSON arrays, so `dimensions` is a
six-element array and `missing_dimensions` is `[]`. Admission recomputes
`coverage=float(observed_count / expected_count)`, rejects zero expected counts,
requires `overall == min(coverage) == 1.0`, and requires the empty missing tuple. It
does not serialize conceptual `numerator`, `denominator`, `state`, or `reason_codes`.
Those names belong only to Gold coverage in Section 10.

The one strict artifact is:

```text
data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json
```

It is canonical `SourceSnapshotManifest` JSON. Existing bytes must match. Its SHA-256
is returned after serialization and is not embedded in the manifest identity input.

## 5. Event clock, ordering, cutoff, and minutes

The profile proves only period-relative `eventSec`, periods `1H` and `2H`, scale at
most 18, and no exact terminal. The adapter configuration phrase
`match_start_plus_match_period_and_event_sec` is descriptive configuration; the
adapter emits no event UTC, so it is not timestamp evidence for W04.

`silver_action` uses:

| Field | Exact type/rule |
| --- | --- |
| `period_code` | enum `1H` or `2H`; unknown fails the partition |
| `period_rank` | strict int8; `1H=1`, `2H=2`, ordering only |
| `period_elapsed_seconds` | `decimal128(22,18)`, non-negative, exact pad without rounding |
| `period_elapsed_source_scale` | int8 `0..18`, exact lexical source scale |
| `occurrence_precision` | constant `period_relative` |
| `period_start_utc` | nullable UTC, always null in W04 |
| `event_observed_at` | nullable UTC, always null in W04 |
| `event_cutoff_proof` | `snapshot_available_before_cutoff` or `ineligible` |

The deterministic action order is:

```text
(period_rank, period_elapsed_seconds, source_record_ordinal,
 source_event_record_id)
```

There is no `match_elapsed_us`, second-half UTC, 2,700-second offset, half-time
duration, or inferred terminal. Gold selection is a match-start window:
`window_start_utc <= match_start_utc < window_end_utc`. An action is eligible only
when its match is admitted and selected, the manifest and every semantic/identity
authority is strictly available before `feature_cutoff_ts`, and
`match_start_utc < feature_cutoff_ts`. A partial-match or action-instant cutoff is
`unsupported_period_relative_occurrence`.

Substitution minute `m` is the nominal half-open interval `[m,m+1)`. A starter begins
at nominal zero. For start `[s0,s1)` and end `[e0,e1)`:

```text
nominal_duration_lower = max(0, e0 - s1)
nominal_duration_upper = max(0, e1 - s0)
```

Open stints are right-censored. Event maxima, `Regular`, 90, and substitution maxima
cannot supply a terminal. Every W04 elapsed-minute field is null, exact
`minutes_played` is absent, `per90_eligible=false`, and minutes/per-90 outputs are
`suppressed_unsupported_denominator`.

## 6. Existing dependency kinds and row lineage

R4 does not change `src/scouting/contracts/evidence.py`. The exact current
`DependencyKind` values remain:

```text
source_manifest, identity_evidence, feature_schema,
model_artifact, retrieval_index
```

W04 semantic products use only the first three.

### 6.1 Deterministic dependency IDs

Canonical entity identities use the frozen source-and-kind UUIDv5 rule:

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
kind_namespace = UUIDv5(source_namespace, "<competition|team|player|match|action>")
canonical_id =
  UUIDv5(kind_namespace, "figshare-v5:<canonical-decimal-source-id>")
```

Provider integer zero is not a player identity. A missing, malformed, duplicate, or
non-zero ID absent from its admitted master table remains unresolved; names and
current-team attributes cannot repair it. Each deterministic `IdentityEvidence`
record binds its exact source-row digest, uses method `deterministic`, confidence
`1.0`, source availability for both `available_at` and `valid_from`, and no reviewer.
The bundle is the ordered digest manifest described below.

```text
w04_dependency_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:w04:wyscout:evidence-dependency:v1")

identity_bundle_dependency_id =
  UUIDv5(w04_dependency_namespace,
    "identity_evidence:" + source_manifest_id + ":" +
    identity_ruleset_version + ":" + identity_bundle_sha256)

field_registry_dependency_id =
  UUIDv5(w04_dependency_namespace,
    "feature_schema:field_registry:" + registry_id + ":" +
    registry_sha256 + ":" + field_acceptance_sha256)

possession_taxonomy_dependency_id =
  UUIDv5(w04_dependency_namespace,
    "feature_schema:possession_taxonomy:" + taxonomy_id + ":" +
    taxonomy_sha256 + ":" + possession_acceptance_sha256)
```

The source dependency ID is the existing strict `manifest_id`, not a derived
replacement. All UUID inputs use lowercase canonical UUID and digest text.

### 6.2 Exact kind and clock map

| Evidence | Existing kind | `dependency_id` | `digest` | `observed_at` | `available_at` |
| --- | --- | --- | --- | --- | --- |
| strict source manifest | `source_manifest` | exact `manifest_id` | strict manifest SHA-256 | `2020-01-28T14:24:27Z` | `2020-01-28T14:24:27Z` |
| reviewed identity bundle | `identity_evidence` | UUIDv5 above | identity bundle SHA-256 | `2020-01-28T14:24:27Z` | `2020-01-28T14:24:27Z` |
| field registry authority | `feature_schema` | UUIDv5 above | registry SHA-256 | field decision `decided_at` | field acceptance `accepted_at` |
| possession taxonomy authority | `feature_schema` | UUIDv5 above | taxonomy SHA-256 | possession decision `decided_at` | possession acceptance `accepted_at` |
| match source row | **not a dependency** | none | row lineage digest | exact `dateutc` is the match semantic instant | knowability inherited from source-manifest dependency |
| action source row | **not a dependency** | none | row lineage digest | null action UTC; period-relative fields retained | knowability inherited from source-manifest dependency |

The source dependency clocks conservatively state when the frozen delivery was
upstream-knowable; they do not relabel action occurrence. The identity assignments
use method `deterministic`, derive only from the admitted numeric ID plus the frozen
UUIDv5 rules below, and have the same knowability clock as their source facts; no
later human identity assertion is being backdated. A future reviewed or corrected
identity must instead carry its own later truthful availability. Field/taxonomy
authority clocks are real recorded human-review clocks and cannot be copied from
source availability. Every clock must be canonical UTC and
`observed_at <= available_at < feature_cutoff_ts`.

The identity bundle is an immutable manifest of the exact contributing
`IdentityEvidence` records, sorted by source entity kind, canonical source ID,
canonical ID, and evidence digest. Its digest covers the sorted assignment digests,
source manifest ID/digest, identity ruleset, decision actor/time, independent review,
and acceptance record. Names/current-team attributes cannot repair identities.

### 6.3 Canonical dependency order and hash

Dependencies are a tuple sorted by:

```text
(kind_rank, dependency_id.bytes, digest,
 canonical_utc(observed_at), canonical_utc(available_at))

kind_rank:
  source_manifest=0
  identity_evidence=1
  feature_schema=2
  model_artifact=3
  retrieval_index=4
```

W04 rejects model or retrieval dependencies in this proof. `lineage_hash` is:

```text
SHA256(canonical_json({
  "lineage_version": "w04-dependency-lineage-v1",
  "dependencies": [
    {
      "kind": <enum value>,
      "dependency_id": <canonical UUID>,
      "digest": <lowercase SHA-256>,
      "observed_at": <canonical UTC>,
      "available_at": <canonical UTC>
    }, ...
  ]
}))
```

The strict `DependencyLineage` object must carry exactly that tuple and hash.
Duplicates by `(kind, dependency_id)` fail.

### 6.4 Match and action row lineage

Source-row lineage is separate because current `DependencyKind` has no match/action
kind and those rows are portions of the already admitted source manifest. A
`W04SourceRowRef` has exact fields:

```text
source_manifest_id: UUID
source_file_path: completion-declared string
source_file_sha256: SHA-256
record_kind: MATCH | ACTION | LINEUP | BENCH | SUBSTITUTION
record_ordinal: non-negative int
source_record_id: canonical decimal string | null
raw_record_sha256: SHA-256 of canonical source record
```

Refs sort by `(source_file_path, record_kind, record_ordinal, source_record_id or "",
raw_record_sha256)`. A row lineage digest is SHA-256 of canonical JSON containing its
version and ordered refs. A player-match fact carries the one match ref plus ordered
lineup/bench/substitution/action refs. Gold carries sorted player-match IDs and each
fact lineage digest. An action has no invented UTC in either lineage representation.

## 7. Clock-free W04 semantic temporal proof

`W04SemanticTemporalProof` is a new W04 product contract, not an alias for, mutation
of, or substitute wire form of current `TemporalEvidence`.

Its complete strict fields are:

```text
schema_version: Literal[1] = 1
proof_version: Literal["w04-semantic-temporal-proof-v1"]
snapshot_as_of_ts: strict timezone-aware UTC
available_at_watermark: strict timezone-aware UTC
valid_from_ts: strict timezone-aware UTC
feature_cutoff_ts: strict timezone-aware UTC
source_manifest_ids: non-empty tuple[StrictUuid, ...]
feature_schema_hash: lowercase 64-character SHA-256
dependency_lineage_hash: lowercase 64-character SHA-256
dependency_lineage: existing strict DependencyLineage
occurrence_precision: Literal["match_start_and_period_relative_action"]
partial_match_claim_supported: Literal[False] = false
```

It intentionally has no `generated_at_ts`. Validators require:

1. no unknown field and strict types;
2. dependency order and `lineage_hash` exactly as Section 6.3;
3. kinds limited to `source_manifest`, `identity_evidence`, and `feature_schema`;
4. exactly one source dependency for this single-source W04 product;
5. `source_manifest_ids` equal the source dependency IDs in dependency tuple order;
6. exactly one deterministic identity-bundle dependency and exactly the accepted
   field-registry and possession-taxonomy feature-schema dependencies, in the
   UUID-derived order required by Section 6.3;
7. every dependency `observed_at < feature_cutoff_ts` and
   `available_at < feature_cutoff_ts`;
8. `available_at_watermark` equals the maximum dependency availability;
9. `snapshot_as_of_ts` equals the maximum selected match-start UTC represented by the
   row, or the one match-start UTC at player-match grain, and is not after cutoff;
10. `valid_from_ts == max(snapshot_as_of_ts, available_at_watermark)`;
11. `feature_schema_hash` equals SHA-256 of canonical JSON containing, in exact order,
    the field registry ID/digest/acceptance digest, taxonomy ID/digest/acceptance
    digest, action/lineup/possession/player-match/Gold schema versions, neutral role
    context ID/version, and supported-feature schema digest;
12. `dependency_lineage_hash == dependency_lineage.lineage_hash`; and
13. semantic JSON contains no key matching `generated_at`, `run_id`, `started_at`,
    `completed_at`, `host`, or `elapsed`.

Empty windows produce no Gold player row; they are represented in the layer manifest,
not by fabricating `snapshot_as_of_ts`.

### 7.1 Truthful adapter to existing boundary contracts

Serving/retrieval code uses a pure boundary function:

```text
adapt_w04_temporal_proof(
  proof: W04SemanticTemporalProof,
  generated_at_ts: UtcInstant,
) -> TemporalEvidence
```

The boundary service samples `generated_at_ts` once from its real injected UTC clock
when constructing the response. Production callers cannot supply a frozen fixture
clock. Tests may inject a labelled deterministic test clock. The adapter first
revalidates the semantic proof, requires `generated_at_ts >= proof.valid_from_ts`,
then constructs current `TemporalEvidence` with an exact one-to-one copy of:

```text
snapshot_as_of_ts
available_at_watermark
valid_from_ts
feature_cutoff_ts
source_manifest_ids
feature_schema_hash
dependency_lineage_hash
dependency_lineage
```

and adds only `generated_at_ts`. The current contract's own validator must pass.
When constructing a current `RetrievalResult`, its `generated_at` is the same sampled
instant and every candidate lineage is exactly the copied dependency lineage, as the
existing validator requires.

The adapter writes a boundary receipt containing the semantic proof digest, lineage
hash, generated clock, result ID, and result digest. That receipt and the response
payload are operational boundary outputs. They are not Bronze/Silver/Gold product
bytes, are not a build-ID input, and do not change semantic identity. A request whose
cutoff or source IDs differ from the proof fails; the adapter never edits the proof,
recomputes availability from generation time, or freezes/fabricates generation.

## 8. Bronze and Silver products

### 8.1 Bronze record index

Bronze reads the five readable direct objects and ten admitted member payloads listed
by the strict manifest. Grain is `(source_file_sha256, record_ordinal)`. It carries
source path/digest, record kind/ID, canonical raw-record digest, exact raw field paths,
parser and registry versions, admission state/reasons, source availability, rights,
tenant, strict manifest ID/digest, and row lineage. Excluded members produce no row.
Unknown field semantics remain preserved `UNMAPPED` or fail according to the accepted
registry; they are never guessed.

### 8.2 `silver_match`

Grain is one admitted match keyed by deterministic match UUID. It contains source
match ID, competition/season, two distinct match-bound teams, exact parsed `dateutc`,
preserved provider status/duration category, file/row lineage, and reconciliation
state. `Regular` is not converted to minutes or a terminal.

### 8.3 `silver_action`

Grain is one unique provider event record `id`. It contains canonical match/team,
nullable canonical player, event and nullable numeric subevent taxonomy IDs, raw
subevent type, Section 5 period fields, preserved ordered positions, coordinate state,
sorted tag IDs, nullable project semantic class, `UNMAPPED` state, ordinal, row
lineage, and possession eligibility.

Coordinates retain source order. Values outside inclusive 0..100 remain
`out_of_range`; the measured x=-1 and two y=101 values are never clamped. The 7,821
string subevent IDs stay `UNMAPPED`, not parsed as integers.

### 8.4 `silver_lineup_stint`

Grain is player × match × continuous provider-nominal interval. It carries match-bound
team/player, nominal interval, boundary source, simultaneous substitution group,
derivation/terminal states, and exact row lineage. No elapsed-minute field is
populated.

### 8.5 `silver_possession`

Grain is one contiguous project-taxonomy-resolved control sequence within one match
and period. ID is UUIDv5 of match ID, accepted taxonomy digest, possession ruleset,
period, and ordinal. It carries team, first/last action, count, assignment states,
boundary reason, taxonomy/acceptance digests, proof/row lineage, and an explicit
`provider_native_possession_claim=false`.

Possessions never cross periods. `UNMAPPED`, missing-team, unresolved contested, and
cross-team equal-clock cases remain uncertain/unassigned. Possession cannot run until
the master and independent route in Section 3.3 is accepted.

### 8.6 Required `silver_player_match_fact`

The logical uniqueness key is:

```text
(tenant_id, source_manifest_id, match_id, player_id,
 player_match_fact_schema_version)
```

Team is a required match-bound attribute; a player linked to both teams is a conflict.
The fact includes deterministic IDs, competition/season, provider side, starting/
bench/substitution/event-presence flags, result-independent action and evidence
counts, nullable possession counts, nominal stint states, all elapsed-minute fields
null, `per90_eligible=false`, the six coverage structures, applicability, match start,
source/authority availability, the clock-free temporal proof, source-row lineage, and
all source/identity/semantic/code schema digests.

It contains no score, winner, points, outcome, or current-team field. Candidate pairs
are the union of resolved non-zero lineup, bench, substitution, and event player
references. Player ID zero remains actor-missing evidence. The measured 23 absent
bench and 8 absent substitution-in references stay reconciliation failures.

Exact reconciliation requires:

1. one fact for each resolved candidate pair;
2. every non-zero player event maps once to the correct match/team fact;
3. fact action counts sum to admitted non-zero attributed actions;
4. every resolved lineup/stint reference maps once;
5. no fact for an excluded member, unresolved identity, or team conflict;
6. zero actors and rejects reconcile separately; and
7. primary-key-sorted reruns have equal row lineage and semantic digests.

The 50,522 distinct non-zero event player-match pairs are an input reconciliation
count, not proof of minutes or lineup status.

## 9. Project possession algorithm after authority

Using Section 5 order and only accepted taxonomy predicates:

1. reviewed `CONTROL` or `RESTART` opens mapped control;
2. same-team control continues;
3. opposing resolved control closes and opens;
4. `DEAD_BALL` closes/attaches exactly as its decision states;
5. `CONTESTED` buffers/attaches only under its exact rule;
6. cross-team equal clocks produce an uncertain boundary;
7. unknown predicates, missing teams, and `UNMAPPED` remain unassigned;
8. period end closes and nothing crosses periods; and
9. only deterministic sequences are Gold eligible.

The product is explicitly `w04_project_defined_possession_v1`, never
`wyscout_native_possession`.

## 10. Gold coverage and applicability

Gold coverage is distinct from strict source `DataCoverage`. Each of six dimensions
stores integer `numerator`, integer `denominator`, decimal coverage, state, and sorted
reason codes:

| Dimension | Denominator | Numerator |
| --- | --- | --- |
| `identity` | all non-zero player-reference occurrences in contributing lineup, bench, substitution, and event evidence | occurrences resolved exactly once to the row player and match team |
| `lineup` | selected player-match candidate facts | facts with reconciled formation/stint state, including explicit event-only/no-lineup |
| `action` | admitted non-zero-player actions for the row player | actions assigned once to correct player-match/team |
| `coordinate` | row actions the accepted registry marks position-applicable | applicable actions with allowed cardinality, required axes, numeric values in 0..100 |
| `possession` | row actions accepted taxonomy marks possession-eligible | eligible actions assigned to exactly one resolved possession |
| `temporal` | strict source/identity/registry/taxonomy dependencies plus selected match/action row groups | dependencies strict-before cutoff, matches before cutoff, actions with snapshot proof |

For `D>0`, coverage is exact `N/D`; `N>D` fails. For `D=0`, only coordinate or
possession may be `1` with `not_applicable_zero_denominator`, and only when accepted
authority proves no evidence is applicable. Otherwise it is `0` with
`missing_zero_denominator`. Complete means `N=D`; otherwise partial.
`coverage_overall` is the minimum of all six values. Missing dimensions are the
lexically sorted partial, missing, authority-missing, or failed dimensions.

Applicability is evaluated in order:

1. prohibited/unknown rights, invalid manifest, unaccepted authority, partition or
   identity conflict, duplicate event, lineage mismatch, or source/authority
   availability at-or-after cutoff => `suppressed`;
2. mandatory identity/action/temporal denominator zero, `N>D`, absent dependency, or
   a minutes/per-90 request => `suppressed`;
3. hard gates pass but incomplete/uncertain/right-censored evidence exists =>
   `research_only`;
4. all dimensions complete or authority-proven optional non-applicable, overall 1,
   and missing empty => `w04_data_ready` for supported count/evidence features only.

No W04 state enables per-90.

## 11. Gold grain and neutral role context

```text
role_context_namespace =
  UUIDv5(NAMESPACE_URL, "urn:scouting-intelligence:role-context")
role_context_version = "w04-neutral-role-context-v1"
role_context_id =
  UUIDv5(role_context_namespace, "w04:neutral-unscoped:version:1")
role_context_state = "neutral_unscoped"
```

The exact `gold_player_window` key is:

```text
(tenant_id, player_id, competition_id, season_id,
 role_context_id, role_context_version,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, dependency_lineage_hash)
```

The snapshot UUID covers the same tuple. Gold contains neutral context, supported
counts, unresolved counts, six Gold coverage structs, applicability, the clock-free
temporal proof, source/identity/authority/schema lineage, and suppressed minute state.
W05 may create a separately versioned role-specific row but cannot mutate or collide
with this neutral row.

## 12. Post-integration content-addressed code manifest

`code_checkpoint` is removed. The implementation identity is a post-integration,
content-addressed code manifest admitted serially by the master.

### 12.1 Freeze point and covered bytes

Code admission occurs only after:

1. all W04 implementation, tests, the final rebuild entry point, and shared package
   exports are integrated;
2. authority artifacts and their independent acceptance records are final;
3. `uv sync --locked --all-groups` and the complete pre-admission test suite pass;
4. no implementation packet remains allowed to edit a covered path; and
5. the master invokes the sole code-admission writer.

The manifest seeds are:

```text
scripts/rebuild_wyscout_v5.py
src/scouting/data_products/wyscout/**/*.py
src/scouting/identity/wyscout.py
src/scouting/contracts/wyscout_data.py
```

All regular `.py` files under the Wyscout package seed are included, imported or not.
The admission scanner parses each seed with Python AST and recursively includes every
repository-local imported module and package `__init__.py` reachable under
`src/scouting`, including existing contracts, source, and storage modules. Relative
imports resolve from the importing module. `from x import y` includes `x`, its package
initializers, and `x/y.py` when that module exists. Imports under Python standard
library or installed distributions are recorded as external; unresolved local-looking
imports fail. Literal `importlib.import_module` names are resolved; non-literal dynamic
imports, `__import__`, executable code loaded from paths, and runtime `sys.path`
mutation are forbidden in the rebuild closure.

The lock inputs are exact regular files:

```text
.python-version
pyproject.toml
uv.lock
```

At design time their observed digests are respectively
`7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d`,
`963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b`,
and `1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca`.
Admission records the then-current bytes; if any digest differs, it is a new code
manifest and requires review, not an implicit failure against these design-time
observations.

### 12.2 Exact non-circular manifest schema

The canonical JSON document is:

```text
schema_version: 1
manifest_kind: w04_post_integration_code_manifest
admission_algorithm: w04-code-admission-v1
entry_point: scripts/rebuild_wyscout_v5.py
seed_spec:
  - exact four seed patterns above, in listed order
source_files:
  - path: NFC repo-relative POSIX path
    sha256: lowercase digest of exact bytes
    size_bytes: non-negative integer
    executable: strict boolean
    local_imports: sorted tuple of included repo-relative module paths
    external_import_roots: sorted tuple of top-level names
lock_inputs:
  - path: .python-version | pyproject.toml | uv.lock, in that order
    sha256: exact byte digest
    size_bytes: non-negative integer
python_constraint: ">=3.12,<3.13"
locked_distributions:
  - normalized_name: string
    version: exact selected lock version for current environment
    installed_version: exact local installed version
closure_digest: SHA256(canonical JSON of source_files only)
lock_digest: SHA256(canonical JSON of lock_inputs and locked_distributions)
```

`source_files` sorts by UTF-8 path bytes. Local imports sort by path and external
roots lexically. Distribution names use PEP 503 normalisation and sort by name/version.
The document contains no manifest digest, ID, path, admission clock, actor, run ID,
Git state, or output digest.

```text
code_manifest_sha256 = SHA256(canonical_manifest_bytes)
code_manifest_id =
  UUIDv5(w04_dependency_namespace,
    "post_integration_code_manifest:" + code_manifest_sha256)
path =
  data/manifests/wyscout/v5/code/
  <code_manifest_sha256>.code-manifest.json
```

This is non-circular: digest and ID are derived after serialization and are absent
from the bytes.

### 12.3 Dirty, untracked, generated, symlink, and mode rules

No Git command or Git metadata is used. “Tracked”, “dirty”, and “untracked” are not
admission categories:

- actual bytes found at every seed and closure path are hashed;
- an uncommitted modification therefore changes the manifest digest;
- an untracked `.py` under the Wyscout package seed is included;
- an imported untracked local module elsewhere is included by closure;
- a local code file outside both the full seed and resolved closure cannot be loaded
  by the rebuild; doing so fails the import guard;
- missing or extra Wyscout-package `.py` files fail equality against an admitted
  manifest at rebuild time.

Every included path must be a regular non-symlink file beneath the repository root.
Hard-linked paths with the same inode are rejected to avoid alias ambiguity.
`__pycache__`, `.pyc`, generated Python, native extensions loaded from repository
paths, sockets/devices, and group/world-writable source files are forbidden.
`executable` is exactly whether any execute bit is set. Only scripts may be
executable; package modules must not be. Rebuild verification compares the boolean,
bytes, size, paths, and closure, so an executable-bit change fails even with equal
bytes.

### 12.4 Lock and import verification

Admission and rebuild both:

1. verify exact `.python-version`, `pyproject.toml`, and `uv.lock` bytes/digests;
2. require Python major/minor 3.12 and the project constraint;
3. run `uv lock --check` before entering the rebuild process;
4. resolve the current environment marker branch of `uv.lock`;
5. require every external distribution used by the AST closure to have exactly one
   selected locked version and the installed metadata version to equal it;
6. reject an imported distribution absent from the selected lock or an ambiguity in
   package-to-distribution ownership; and
7. recompute the full local import closure and require exact equality to the manifest.

The independent code-admission review reruns those checks from the frozen tree and
compares canonical manifest bytes. The runtime does the same before build identity is
computed. A stale manifest, changed byte, changed mode, extra/missing closure file,
different lock, unresolved import, or environment mismatch stops without creating a
build directory.

## 13. Build identity, deterministic outputs, and receipts

Only after code verification succeeds is this canonical input formed:

```text
{
  "build_identity_version": "w04-wyscout-build-id-v2",
  "tenant_context": <exact>,
  "completion_sha256": <exact>,
  "strict_manifest_id": <UUID>,
  "strict_manifest_sha256": <digest>,
  "identity_bundle_id": <UUID>,
  "identity_bundle_sha256": <digest>,
  "field_registry_id": <string>,
  "field_registry_sha256": <digest>,
  "field_acceptance_sha256": <digest>,
  "possession_taxonomy_id": <string>,
  "possession_taxonomy_sha256": <digest>,
  "possession_acceptance_sha256": <digest>,
  "identity_ruleset_version": <string>,
  "action_ruleset_version": <string>,
  "lineup_ruleset_version": <string>,
  "possession_ruleset_version": <string>,
  "player_match_fact_schema_version": <string>,
  "gold_schema_version": <string>,
  "neutral_role_context_id": <UUID>,
  "neutral_role_context_version": <string>,
  "window_definition": <exact canonical object>,
  "feature_cutoff_ts": <canonical UTC>,
  "code_manifest_id": <UUID>,
  "code_manifest_sha256": <digest>,
  "closure_digest": <digest>,
  "lock_digest": <digest>
}
build_id = SHA256(canonical_json(input))
```

No label, branch, tag, commit, run clock, host, output root, random ID, or receipt is
an input.

Semantic outputs use fixed schemas, canonical UUID/UTC/Decimal/null/list values,
primary-key row order, fixed partitions, and one `part-00000.parquet` per logical
partition with:

```text
format_version="2.6"; row_group_size=65536; compression="zstd";
compression_level=9; data_page_version="2.0"; use_dictionary=false;
write_statistics=true; write_page_index=false; use_byte_stream_split=false;
coerce_timestamps="us"; allow_truncated_timestamps=false; store_schema=true
```

The semantic digest covers canonical schema, length-prefixed canonical rows, and
ordered parent/authority/code digests. The physical digest covers exact file bytes.
Two builds from distinct empty roots with one admitted code manifest must have equal
relative paths, rows, schemas, lineage, semantic digests, and physical digests.

Each run separately writes:

```text
runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json
```

with truthful run/trace IDs, start/completion clocks, elapsed duration, requested
empty root, code manifest ID/digest and verification result, lock/runtime versions,
boundary state, build ID, and ordered semantic/physical digests. Receipts are excluded
from semantic and physical products and may truthfully differ.

Layer manifests are written last and contain no clock:

```text
data/manifests/wyscout/v5/bronze/<build_id>.manifest.json
data/manifests/wyscout/v5/silver/<build_id>.manifest.json
data/manifests/wyscout/v5/gold/<build_id>.manifest.json
```

## 14. Quality and reconciliation gates

An accepted rebuild requires:

- exact ordered `completion + 7 objects + 10 admitted members == 18` strict file rows;
- exact field/type/order/tuple population of strict source `DataCoverage`;
- source records 7/142/3,603 and exact member row counts;
- 1,826 unique matches, 3,071,395 unique event IDs, and zero duplicates;
- five exact event/match partition-ID equalities;
- exactly two teams per match, team-key equality, and zero event match/team conflicts;
- zero non-zero event-player misses, with 226,038 zero actors separate;
- 40,172 lineup, 28,715 bench, and 10,423 substitution rows reconciled, retaining 23
  bench and 8 substitution-in missing-master references;
- only 1H/2H, scale at most 18, no inferred action UTC, and strict-before cutoff;
- 709 one-position and 3,070,686 two-position actions, all three anomalies retained;
- accepted decision, artifact, independent review, and acceptance digests for both
  semantic authorities; every unknown stays `UNMAPPED`;
- correct existing dependency kinds, deterministic UUIDs/clocks/order/hash, and exact
  row lineage;
- complete validation of clock-free proof and truthful boundary-adapter challenges;
- result-independent player-match facts and neutral Gold role context;
- zero elapsed-minute/per-90 emissions;
- exact Gold coverage and applicability equations;
- code-manifest byte/mode/import/lock equality before build ID;
- sole-writer layer manifests written last;
- two independent empty-root semantic and physical rebuild equalities; and
- restricted attribution and local-only control inherited everywhere.

Negative tests cover source path escape/symlink, 17 or 19 file rows, reordered files,
integer `1` where strict float `1.0` is required, conceptual coverage field names,
unknown semantic keys, label guessing, stale acceptance, bad authority clocks,
fabricated action UTC, dependency kind invention, UUID/hash/order mismatch, run clock
inside Gold, boundary generation before valid-from, changed/untracked/imported code,
extra Wyscout module, mode/lock drift, build-ID-before-code-verification, and shared
manifest double writers.

## 15. Ownership-complete serial implementation graph

Every listed path has one owner. Reports and returns shown in a row belong only to
that packet. Shared exports, authorities, code admission, layer manifests, and rebuild
orchestration are serial. The only parallel group is the three path-disjoint Silver
producers. No migration or dependency edit is proposed.

| Order | Packet / owner | Exact write scope | Dependency and sole-writer rule |
| ---: | --- | --- | --- |
| 1 | `W04-FIELD-SEMANTIC-DECISION-01-R1` / master | `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json`; `configs/schema/wyscout-v5-field-registry-v1.yaml`; `tests/contracts/test_wyscout_field_registry_authority.py`; `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-DECISION-01-R1.md` | Serial master decision; no acceptance claim |
| 2 | `W04-FIELD-SEMANTIC-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`; `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-REVIEW-01-R1.md` | Independent after 1; cannot edit candidate |
| 3 | `W04-FIELD-SEMANTIC-ACCEPT-01-R1` / master | `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json`; `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-ACCEPT-01-R1.md` | Serial after PASS from 2; sole acceptance writer |
| 4 | `W04-POSSESSION-SEMANTIC-DECISION-01-R1` / master | `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json`; `configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml`; `tests/contracts/test_wyscout_possession_taxonomy_authority.py`; `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-DECISION-01-R1.md` | Serial after 3; project semantics only |
| 5 | `W04-POSSESSION-SEMANTIC-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md`; `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-REVIEW-01-R1.md` | Independent after 4 |
| 6 | `W04-POSSESSION-SEMANTIC-ACCEPT-01-R1` / master | `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json`; `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-ACCEPT-01-R1.md` | Serial after PASS from 5; sole acceptance writer |
| 7 | `W04-DATA-CONTRACTS-01-R1` / master shared-contract owner | `src/scouting/contracts/wyscout_data.py`; `tests/contracts/test_wyscout_data_contracts.py`; `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R1.md` | Serial; defines proof/row contracts, does not edit existing evidence contract |
| 8 | `W04-MANIFEST-BRIDGE-01-R1` | `src/scouting/data_products/wyscout/manifest_bridge.py`; `tests/unit/test_wyscout_manifest_bridge.py`; `reports/reviews/W04/returns/W04-MANIFEST-BRIDGE-01-R1.md` | After 7; sole strict source-manifest writer |
| 9 | `W04-BRONZE-01-R1` | `src/scouting/data_products/wyscout/bronze.py`; `tests/unit/test_wyscout_bronze.py`; `reports/reviews/W04/returns/W04-BRONZE-01-R1.md` | After 3, 7, 8; sole Bronze product and Bronze layer-manifest writer |
| 10 | `W04-IDENTITY-01-R1` | `src/scouting/identity/wyscout.py`; `tests/unit/test_wyscout_identity.py`; `reports/reviews/W04/returns/W04-IDENTITY-01-R1.md` | Serial after 9; sole identity-bundle writer |
| 11A | `W04-SILVER-MATCH-01-R1` | `src/scouting/data_products/wyscout/entities.py`; `tests/unit/test_wyscout_entities.py`; `reports/reviews/W04/returns/W04-SILVER-MATCH-01-R1.md` | Parallel only with 11B/11C after 10; no layer-manifest writes |
| 11B | `W04-SILVER-ACTION-01-R1` | `src/scouting/data_products/wyscout/actions.py`; `tests/unit/test_wyscout_actions.py`; `reports/reviews/W04/returns/W04-SILVER-ACTION-01-R1.md` | Parallel only with 11A/11C after 6 and 10; no layer-manifest writes |
| 11C | `W04-SILVER-LINEUP-01-R1` | `src/scouting/data_products/wyscout/lineups.py`; `tests/unit/test_wyscout_lineups.py`; `reports/reviews/W04/returns/W04-SILVER-LINEUP-01-R1.md` | Parallel only with 11A/11B after 10; no layer-manifest writes |
| 12 | `W04-POSSESSION-01-R1` | `src/scouting/data_products/wyscout/possessions.py`; `tests/unit/test_wyscout_possessions.py`; `reports/reviews/W04/returns/W04-POSSESSION-01-R1.md` | Serial after 11B and accepted taxonomy; no layer-manifest writes |
| 13 | `W04-PLAYER-MATCH-FACT-01-R1` | `src/scouting/data_products/wyscout/player_match.py`; `tests/unit/test_wyscout_player_match.py`; `reports/reviews/W04/returns/W04-PLAYER-MATCH-FACT-01-R1.md` | Serial after 11A/11B/11C/12; no layer-manifest writes |
| 14 | `W04-SILVER-MANIFEST-01-R1` | `src/scouting/data_products/wyscout/silver_manifest.py`; `tests/unit/test_wyscout_silver_manifest.py`; `reports/reviews/W04/returns/W04-SILVER-MANIFEST-01-R1.md` | Serial after all Silver producers; sole Silver layer-manifest writer |
| 15 | `W04-GOLD-TEMPORAL-01-R1` | `src/scouting/data_products/wyscout/gold.py`; `src/scouting/data_products/wyscout/temporal_boundary.py`; `tests/unit/test_wyscout_gold.py`; `tests/unit/test_wyscout_temporal_boundary.py`; `reports/reviews/W04/returns/W04-GOLD-TEMPORAL-01-R1.md` | Serial after 14; `gold.py` sole Gold product/layer-manifest writer; boundary receipt separate |
| 16 | `W04-QUALITY-01-R1` | `src/scouting/data_products/wyscout/quality.py`; `tests/unit/test_wyscout_quality.py`; `reports/reviews/W04/returns/W04-QUALITY-01-R1.md` | Serial quality library; writes no layer manifest |
| 17 | `W04-CODE-ADMISSION-IMPLEMENT-01-R1` / master | `src/scouting/data_products/wyscout/code_admission.py`; `scripts/admit_wyscout_v5_code.py`; `tests/unit/test_wyscout_code_admission.py`; `reports/reviews/W04/returns/W04-CODE-ADMISSION-IMPLEMENT-01-R1.md` | Serial implementation of sole code-manifest writer |
| 18 | `W04-REBUILD-ENTRYPOINT-01-R1` / master | `src/scouting/data_products/wyscout/rebuild.py`; `scripts/rebuild_wyscout_v5.py`; `tests/integration/test_wyscout_rebuild.py`; `reports/reviews/W04/returns/W04-REBUILD-ENTRYPOINT-01-R1.md` | Serial after 16/17; sole empty-root orchestration entry point; only calls named manifest writers |
| 19 | `W04-SHARED-INTEGRATION-01-R1` / master | `src/scouting/contracts/__init__.py`; `src/scouting/data_products/__init__.py`; `src/scouting/data_products/wyscout/__init__.py`; `src/scouting/identity/__init__.py`; `reports/reviews/W04/returns/W04-SHARED-INTEGRATION-01-R1.md` | Serial after all source implementation; sole shared-export owner; no “if needed” edits |
| 20 | `W04-CODE-MANIFEST-ADMIT-01-R1` / master | `data/manifests/wyscout/v5/code/<computed-code-manifest-sha256>.code-manifest.json`; `reports/reviews/W04/wyscout-code-manifest-admission-R1.md`; `reports/reviews/W04/returns/W04-CODE-MANIFEST-ADMIT-01-R1.md` | Post-integration freeze after 19; dynamic filename is exactly the computed digest rule; sole code-manifest invocation |
| 21 | `W04-CODE-MANIFEST-REVIEW-01-R1` / independent reviewer | `reports/reviews/W04/wyscout-code-manifest-independent-review-R1.md`; `reports/reviews/W04/returns/W04-CODE-MANIFEST-REVIEW-01-R1.md` | Independent byte/import/mode/lock reproduction; cannot edit code manifest |
| 22 | `W04-TWO-ROOT-REBUILD-01-R1` / master | `runs/w04/wyscout-rebuild/**`; `data/working/wyscout/v5/**`; `data/manifests/wyscout/v5/bronze/**`; `data/manifests/wyscout/v5/silver/**`; `data/manifests/wyscout/v5/gold/**`; `reports/reviews/W04/wyscout-rebuild-evidence-R1.md`; `reports/reviews/W04/returns/W04-TWO-ROOT-REBUILD-01-R1.md` | After PASS 21; one entry point, two empty roots; runtime code verifies before build ID; module-level sole-writer rules remain enforced |
| 23 | `W04-INDEPENDENT-REBUILD-REVIEW-01-R1` / independent reviewer | `tests/security/test_w04_temporal_leakage.py`; `reports/reviews/W04/wyscout-rebuild-independent-review-R1.md`; `reports/reviews/W04/returns/W04-INDEPENDENT-REBUILD-REVIEW-01-R1.md` | Final independent temporal, lineage, rights, determinism, and ownership review after 22 |

The broad generated scopes in row 22 are runtime outputs, not permission for direct
multi-writer access. `manifest_bridge.py`, `bronze.py`, `silver_manifest.py`, and
`gold.py` remain the only code paths allowed to serialize their respective manifests.
`rebuild.py` orchestrates them and cannot serialize a layer manifest itself.

If any migration, dependency, lock, architecture, or source-rights change becomes
necessary, this graph stops. Such work requires a separately authorised master-owned
serial packet and a new review; it is not implied here.

## 16. Finding closure

| Finding | R4 closure |
| --- | --- |
| `W04-DESIGN-EVENT-CLOCK-01` | Exact period-relative decimal/order and null action UTC are retained; Sections 6–7 now provide complete dependency clocks, clock-free proof, validators, and truthful existing-contract adapter. |
| `W04-DESIGN-SOURCE-SEAM-01` | Retained: only exact completion-declared paths are read; ZIPs/exclusions remain unopened downstream. |
| `W04-DESIGN-MANIFEST-BRIDGE-01` | Non-circular bridge retained and corrected to exactly 18 ordered `SourceFileDigest` rows plus literal strict `DataCoverage` fields/types/order/tuple serialization. |
| `W04-DESIGN-REBUILD-CLOCK-01` | Arbitrary checkpoint removed; post-integration code bytes/import closure/modes/lock are content-addressed and verified before build ID; generation clocks stay only in truthful receipts/boundaries. |
| `W04-DESIGN-POSSESSION-AUTHORITY-01` | Exact local map/profile/source digests, accountable master decision, separate independent review, final master acceptance, truthful availability, `UNMAPPED` unknowns, and no provider-native claim are normative. |
| `W04-DESIGN-GOLD-GRAIN-01` | Retained: neutral versioned role context is part of the key and cannot be overwritten by W05. |
| `W04-DESIGN-MINUTES-01` | Retained: nominal intervals are explicit; elapsed, terminal, minutes, and per-90 remain suppressed. |
| `W04-DESIGN-COVERAGE-01` | Retained for Gold, and now explicitly separated from field-exact strict source `DataCoverage`. |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | Retained: exact player×match grain, match-bound team, result independence, proof/lineage/coverage, and reconciliations. |

The four P1 defects and two P2 defects returned against R3 are therefore addressed by
implementable contracts and a complete ownership graph. This is a design claim only;
master and independent review remain required.

## 17. Stop rules and handoff

Stop rather than improvise if an accepted path/digest/count changes; a required
tenant, identity, semantic decision, independent review, acceptance clock, rights
authority, or code manifest is absent; an excluded stream would be opened; a runtime
semantic guess is proposed; action UTC or exact minutes would be fabricated; a code
closure/lock mismatch exists; a shared writer is ambiguous; or any dependency,
migration, provider, network, source-rights, local-only, or architecture change is
needed.

Implementation may begin only after master and independent acceptance of this R4.
This document does not self-approve.

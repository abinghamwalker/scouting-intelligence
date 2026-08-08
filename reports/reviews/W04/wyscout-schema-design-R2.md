# W04 Wyscout v5 canonical schema and rebuild design — R2

Status: **corrected implementation design for master review; not self-approved**

This is a complete replacement for R1. It covers only the frozen Wyscout Soccer match
event dataset, figshare collection v5, and the five authorised 2017/18 domestic
top-flight partitions. It was written without downloading, extracting, or inspecting a
football-data payload. It corrects the archive-directory scope, source-clock semantics,
and duplicate Gold field identified by the master while retaining the otherwise valid
R1 schemas, algorithms, gates, and implementation boundaries.

## 1. Authority and claim boundary

The controlling authorities are:

- `configs/sources/w04-provider.yaml`, including seven configured objects, five
  admitted domestic members per archive, two exact `known_scope_excluded` members per
  archive, and the frozen release timestamp;
- `reports/phase-gates/W04/archive-directory-preflight.md`, which proves each of
  `matches.zip` and `events.zip` has exactly seven directory entries: five admitted
  domestic members and two known tournament exclusions;
- the accepted `SourceSnapshotManifest` contract in
  `src/scouting/contracts/evidence.py`, which gives `acquired_at` and `available_at`
  independent factual meanings and imposes no generic ordering;
- the independently reproduced temporal-contract return at
  `reports/reviews/W04/returns/W04-CONTRACT-TEMPORAL-01-R1.md`;
- the approved blueprint and workflow, the W04 provider authority, guarded local
  storage boundary, and accepted W03 strict temporal-evidence floor.

The permitted claim is a frozen historical engineering and player-retrieval proof. The
design makes no claim about current players, current source continuity, current
scouting coverage, women or youth populations, prospective effectiveness, competition
strength, or parity with a current commercial Wyscout product.

No cloud resource, remote repository, hosted service, public endpoint, external model,
provider account, or deployment is part of this design.

## 2. Corrected source-clock semantics

### 2.1 Generic contract

`SourceSnapshotManifest` remains unchanged:

```text
acquired_at  = actual UTC instant when this project received the delivery
available_at = upstream UTC source/fact availability instant
```

Both are required, strict UTC, independently supplied facts. Neither is derived from
the other. The generic contract permits all truthful orderings:

```text
available_at < acquired_at   # publication before later local acquisition
available_at = acquired_at   # simultaneous publication/receipt
available_at > acquired_at   # receipt before an embargo or later fact availability
```

This design requests no W03 fixture, digest, consumer, schema, or migration change.
`TemporalEvidence` continues to enforce eligibility separately: every dependency
`observed_at` and `available_at` must be strictly earlier than the feature cutoff.
Cutoff equality fails closed.

### 2.2 Wyscout-specific admission

The Wyscout adapter applies narrower source-specific facts without changing the generic
contract:

```text
wyscout_available_at = 2020-01-28T14:24:27Z
wyscout_acquired_at  = actual completed local acquisition instant
require wyscout_acquired_at >= 2020-01-28T14:24:27Z
```

The exact release instant comes from the frozen collection authority. The acquisition
instant comes from the completed local receipt and must not be backdated to the release.
A Wyscout receipt earlier than the release is inconsistent with this frozen authority
and fails admission. Equality is structurally valid even though normal execution is
expected to be later.

The adapter must test:

1. the frozen 2020 release with a truthful later local acquisition;
2. equality at the frozen release;
3. rejection of a Wyscout acquisition earlier than the frozen release;
4. strict UTC, required fields, canonical JSON round-trip, attribution, digests,
   duplicate-object, and unknown-field controls;
5. downstream cutoff acceptance only when availability and observation are strictly
   before cutoff, with equality rejected; and
6. no change to the generic contract's legitimate embargo-after-receipt case.

## 3. Global invariants

1. IDs are lower-case canonical UUIDs derived deterministically from frozen source IDs;
   display names are never join keys.
2. Timestamps are UTC `timestamp[us, tz=UTC]`. Naive or non-UTC values fail.
3. Semantic payloads carry `schema_version`, `tenant_id`, source manifest ID,
   record/dependency lineage digest, `observed_at`, `available_at`, and `generated_at`.
4. `observed_at < feature_cutoff_ts` and
   `available_at < feature_cutoff_ts` are strict. Equality fails.
5. Every admitted Wyscout v5 record has
   `available_at=2020-01-28T14:24:27Z`; fetch/run time is never substituted.
6. No snapshot with a cutoff at or before the release is eligible.
7. Unversioned player-master attributes are not historical features. Match-bound team,
   lineup, substitution, and event evidence controls match context.
8. The four named tournament entries across the two archives are known scope
   exclusions, not unknown entries. Their payload bytes are never opened, extracted,
   admitted, parsed, transformed, hashed independently, or used.
9. Any other archive entry, unknown top-level field, unknown period, unavailable event
   or tag semantics, or identity conflict fails closed rather than being guessed.
10. The strictest effective rights control follows every derived product. Attribution
    is mandatory and external/raw export remains forbidden by project policy.
11. Payload content digests exclude wall-clock run metadata. Identical admitted inputs,
    schema/rule versions, and code produce byte-identical semantic outputs.

## 4. Authoritative objects, archive directory, and storage topology

### 4.1 Configured object set

The acquisition object set is exactly:

```text
competitions.json
teams.json
players.json
matches.zip
events.zip
eventid2name.csv
tags2name.csv
```

Configured URL, name, byte size, and MD5 are admission controls. Computed SHA-256 is the
immutable project object identity.

### 4.2 Exact archive directory contract

`matches.zip` must contain exactly these seven unique directory entries:

```text
ADMIT:
  matches_England.json
  matches_France.json
  matches_Germany.json
  matches_Italy.json
  matches_Spain.json
KNOWN_SCOPE_EXCLUDED:
  matches_European_Championship.json
  matches_World_Cup.json
```

`events.zip` must contain exactly these seven unique directory entries:

```text
ADMIT:
  events_England.json
  events_France.json
  events_Germany.json
  events_Italy.json
  events_Spain.json
KNOWN_SCOPE_EXCLUDED:
  events_European_Championship.json
  events_World_Cup.json
```

Directory admission is fail closed:

1. Read only the ZIP directory metadata first.
2. Reject absolute paths, parent traversal, links, directories, duplicate names,
   malformed names, encrypted entries, or unsafe entry types before any extraction.
3. Require equality between the observed entry-name set and the configured union of
   five admitted plus two known-excluded names for that archive.
4. A missing admitted entry, missing known-excluded entry, duplicate, or any eighth or
   otherwise undeclared entry fails the archive before any member is admitted.
5. For a configured admitted name, extract that one member through a bounded streaming
   reader into guarded local storage, enforce decompression limits, then compute the
   member SHA-256.
6. For a configured known-excluded name, record only the verified directory
   classification bound to the parent archive SHA-256. Do not open its member stream,
   read compressed payload bytes, extract, hash the member payload, parse, index,
   quarantine as a record, transform, or use it in any count or product.
7. Never call an unbounded or whole-archive extraction operation.

An archive passes with exactly five admitted and two known-excluded entries. The known
exclusions do not cause rejection and never become Bronze records. Any other entry
remains an unknown-member failure.

### 4.3 Guarded paths

```text
data/source/wyscout/v5/objects/<file_id>/<configured_name>
data/source/wyscout/v5/members/<archive_file_id>/<admitted_member_name>
data/working/wyscout/v5/bronze/<source_manifest_id>/<record_kind>/
data/working/wyscout/v5/silver/<build_id>/<product_name>/
data/working/wyscout/v5/gold/<build_id>/player_window/
data/manifests/wyscout/v5/<layer>/<content_digest>.manifest.json
```

Known-excluded members have no path under `members/`. Implementations resolve paths
through named guarded roots, never arbitrary absolute paths. Writes are payload-first
and completion-manifest last. Identical content is idempotent; conflicting content at
the same logical identity is an error.

## 5. Bronze boundaries

### 5.1 Physical boundaries

| Boundary | Grain and identity | Payload | Completion rule |
|---|---|---|---|
| `source_object` | Configured object keyed by `(source_manifest_id, file_id)` | Exact downloaded bytes | URL, name, size, MD5, and computed SHA-256 pass |
| `archive_directory_receipt` | One archive keyed by parent SHA-256 | Ordered entry names and classifications only | Exactly five admitted plus two known excluded; safe and unique |
| `source_archive_member` | Safely admitted member keyed by `(source_object_sha256, member_path)` | Exact admitted uncompressed bytes | Name is one of five admitted names; bounded extraction and member SHA-256 pass |
| `bronze_record_index` | Top-level JSON record or lookup row keyed by `(member_sha256, record_ordinal)` | Structural index and canonical record digest | Entire admitted member parses; every record receives an admission state |
| `bronze_quarantine` | Rejected admitted object/member/record | Bounded metadata, reason codes, field names, and digests | Written before a product is complete; excluded tournament payload is never copied here |
| `bronze_partition_manifest` | Record kind × admitted country | Counts and ordered record digests | Raw/index/quarantine counts reconcile |

### 5.2 Bronze record-index schema

All fields are required unless nullable is stated.

| Field | Type | Rule |
|---|---|---|
| `schema_version` | `int16` | Constant `1` |
| `tenant_id` | canonical UUID string | Explicit context |
| `source_manifest_id` | canonical UUID string | Accepted delivery |
| `source_object_file_id` | `int64` | Configured figshare file ID |
| `source_object_sha256` | lower-case SHA-256 | Downloaded object bytes |
| `source_member_path` | UTF-8 string | Configured plain object or admitted archive member only |
| `source_member_sha256` | lower-case SHA-256 | Exact admitted member bytes |
| `source_record_kind` | enum | `competition`, `team`, `player`, `match`, `event`, `event_type_lookup`, `tag_lookup` |
| `source_record_id` | string, nullable for lookup rows | Provider ID in canonical decimal text |
| `source_record_version` | string | `figshare-v5:<source_member_sha256>:<raw_record_sha256>` |
| `record_ordinal` | `int64 >= 0` | Original array/CSV order; evidence only |
| `raw_record_sha256` | lower-case SHA-256 | Canonical JSON value or canonical CSV-row digest |
| `raw_field_names` | sorted list of strings | Exact observed top-level field set |
| `parser_version` | string | Immutable parser/rule identifier |
| `admission_state` | enum | `admitted`, `quarantined_unknown_field`, `quarantined_invalid_shape`, `quarantined_conflict`, `scope_excluded` |
| `rejection_reason_codes` | sorted list of strings | Empty only when admitted |
| `observed_at` | UTC timestamp, nullable by kind | Match/event occurrence; reference entities may be null |
| `available_at` | UTC timestamp | Frozen collection release |
| `acquired_at` | UTC timestamp | Actual local receipt |
| `generated_at` | UTC timestamp | Index construction metadata only |
| `rights_policy_id` | string | Frozen W04 policy |
| `attribution_text` | string | Exact configured attribution |

`scope_excluded` is available for a structurally read record inside an admitted member
when a later reviewed record-level rule excludes it. It must not be used for the four
known-excluded archive members because their payloads are never read. A consumer
resolves raw evidence by admitted member digest and ordinal; canonical reserialization
is used for the record digest, not represented as original byte layout.

### 5.3 Schema admission rules

- Each record kind has a checked-in field registry classifying fields as
  `transformed`, `preserved_not_transformed`, or `forbidden`.
- An unknown field quarantines the record. Missing known optional fields are measured.
- IDs are integral, non-negative, and exactly representable as `int64`; booleans,
  floats, whitespace normalization, signs, leading-zero normalization, and lossy
  coercion are forbidden.
- Duplicate `(record_kind, source_record_id)` plus identical digest is idempotent.
  Different digests are `quarantined_conflict`; there is no last-write-wins.
- `dateutc`, `matchPeriod`, and `eventSec` are the only authorised occurrence inputs.
  File time, request time, acquisition time, and generation time are not observations.
- Unknown semantics may be preserved as evidence but are never inferred into Silver or
  Gold.

## 6. Canonical identities

### 6.1 Deterministic UUID algorithm

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
kind_namespace =
  UUIDv5(source_namespace, "<competition|season|team|player|match|event>")
canonical_id =
  UUIDv5(kind_namespace, "figshare-v5:<canonical-decimal-source-id>")

lineup_stint_id = UUIDv5(match_namespace,
  "stint:<team_source_id>:<player_source_id>:<stint_ordinal>:<ruleset_version>")
possession_id = UUIDv5(match_namespace,
  "possession:<possession_ordinal>:<ruleset_version>")
player_window_snapshot_id = UUIDv5(player_namespace,
  "window:<window_definition_id>:<cutoff_utc>:<dependency_lineage_hash>")
```

Names never enter an identity. Season IDs exist only for valid frozen source season
IDs.

### 6.2 Crosswalk

| Field | Type / rule |
|---|---|
| `identity_evidence_id` | Deterministic UUID from source identity and version |
| `tenant_id` | UUID |
| `entity_kind` | `competition`, `season`, `team`, `player`, `match`, `event` |
| `provider` | `wyscout_figshare` |
| `source_id` | Canonical decimal text |
| `source_version` | `figshare-v5:<raw_record_sha256>` |
| `canonical_id` | UUID; null unless resolved |
| `version` | Positive integer; initial frozen evidence is `1` |
| `match_method` | `exact` for a valid unique ID; `reviewed` only with reviewer evidence |
| `confidence` | `1.0` for structurally exact unique mapping |
| `state` | `resolved`, `review_required`, `rejected_missing_id`, `rejected_conflict`, `superseded` |
| `evidence_digest` | Canonical evidence and rule-version digest |
| `available_at` / `valid_from` | Frozen collection release |
| `valid_to` | Null unless separately evidenced supersession exists |
| `reviewed_by` | Required for `reviewed` |
| `reason_codes` | Sorted; empty only when structurally resolved |

Rules:

1. A unique valid non-zero provider ID within one entity kind maps to its deterministic
   UUID.
2. Player ID zero or missing means `provider_actor_unidentified`; no player zero or
   name match is created.
3. A referenced non-zero ID absent from admitted evidence enters `review_required` and
   blocks the reference from Gold.
4. Same source ID with different record digests is `rejected_conflict`.
5. Identical names do not merge different source IDs.
6. `currentTeamId` and unversioned player fields cannot create match-era membership.
7. Corrections require a new version, reviewer, reason, interval, and supersession
   digest; version 1 is immutable.

## 7. Silver schemas

### 7.1 Common lineage

Every Silver row includes:

```text
schema_version:int16
tenant_id:uuid-string
source_manifest_id:uuid-string
source_record_kind:string
source_record_id:string
source_record_version:string
source_record_sha256:sha256
identity_evidence_digests:list<sha256>
transformation_version:string
dependency_lineage_hash:sha256
observed_at:timestamp[us, UTC] nullable only for identity/reference entities
available_at:timestamp[us, UTC]
generated_at:timestamp[us, UTC]
rights_policy_id:string
```

The lineage hash covers ordered tuples
`(kind, id, digest, observed_at, available_at)`: source manifest, source record, then
sorted identity evidence.

### 7.2 `silver_match`

Grain: one admitted match.

| Field | Type / rule |
|---|---|
| `match_id` | Deterministic UUID primary key |
| `source_match_id` | Unique `int64` |
| `competition_id`, `season_id` | Resolved UUIDs |
| `home_team_id`, `away_team_id` | Required distinct match-bound UUIDs |
| `match_start_utc` | Strict `dateutc` UTC parse and base occurrence |
| `provider_status` | Preserved allowlisted value; no inferred mapping |
| `provider_duration` | Nullable preserved value |
| `home_score`, `away_score` | Nullable non-negative `int16`, match-bound |
| `winner_team_id` | Nullable; null for draw/unknown, otherwise a match team |
| `venue_text` | Nullable display evidence; not a feature |
| `match_coverage_state` | `structural_only`, `events_reconciled`, `lineups_reconciled`, `complete`, `failed` |
| `coverage_reason_codes` | Sorted; empty only when complete |

`observed_at=match_start_utc`; `available_at` is the release. File order cannot override
`dateutc`.

### 7.3 `silver_team`

Grain: one provider team identity at frozen v5.

| Field | Type / rule |
|---|---|
| `team_id` | UUID primary key |
| `source_team_id` | Unique `int64` |
| `display_name` | Display only |
| `official_name`, `team_type`, `area_source_id` | Nullable preserved values |
| `entity_eligibility` | `identity_only` |

Entity `observed_at` is null; master fields do not establish match membership.

### 7.4 `silver_player`

Grain: one provider player identity at frozen v5.

| Field | Type / rule |
|---|---|
| `player_id` | UUID primary key |
| `source_player_id` | Unique, non-zero `int64` |
| `display_name` | Review/display only |
| `provider_role_name` | Nullable publication-time description, not historical evidence |
| `provider_master_digest` | SHA-256 |
| `historical_feature_eligible` | Constant `false` |
| `entity_eligibility` | `identity_and_display_only` |

Birth date, height, weight, foot, nationality, and current team remain Bronze pending
later privacy, semantics, and validity review.

### 7.5 `silver_lineup_stint`

Grain: player × match × continuous derivable on-pitch interval.

| Field | Type / rule |
|---|---|
| `lineup_stint_id` | Deterministic derived UUID |
| `match_id`, `team_id`, `player_id` | Resolved UUIDs; team belongs to match |
| `stint_ordinal` | `int16 >= 0` |
| `start_elapsed_us_min`, `start_elapsed_us_max` | Inclusive non-negative bounds |
| `end_elapsed_us_min`, `end_elapsed_us_max` | Inclusive bounds not before start |
| `duration_us_min`, `duration_us_max` | `max(0,end_min-start_max)`, `end_max-start_min` |
| `start_reason` | `starting_lineup`, `substitution_in` |
| `end_reason` | `substitution_out`, `match_end`, `unresolved` |
| `boundary_precision` | `match_start`, `provider_minute`, `match_end`, `unknown` |
| `provider_substitution_ordinal` | Nullable source order |
| `simultaneous_group` | Nullable equal-minute group |
| `derivation_state` | `resolved`, `uncertain`, `failed` |
| `reason_codes` | Sorted; empty only when resolved |

Provider substitution minute `m` becomes
`[m*60_000_000, (m+1)*60_000_000-1]`; no exact second is fabricated. Starting players
begin at exact match start. Equal-minute substitutions share a simultaneous group.
Outgoing players must be on pitch, incoming players off pitch, and team count conserved.
Violations fail lineup derivation. Bench-only players have no stint. Match end requires
classified terminal evidence; maximum event time is only a lower bound. Unprovable
final boundaries make minutes an unavailable interval.

### 7.6 `silver_action`

Grain: one admitted event.

| Field | Type / rule |
|---|---|
| `action_id` | Deterministic event UUID |
| `source_event_id` | Unique `int64` |
| `match_id`, `team_id` | Resolved; team belongs to match |
| `player_id` | Nullable only for explicit zero/missing actor |
| `source_event_type_id`, `source_subevent_type_id` | Exact `int32` IDs |
| `source_event_name`, `source_subevent_name` | Must agree with admitted lookup |
| `period_code` | First pass only reviewed `1H`, `2H` |
| `period_elapsed_us` | Exact decimal `eventSec`, non-negative, <= 6 decimals |
| `match_elapsed_us` | 1H elapsed; 2H is `2_700_000_000 + period_elapsed_us` |
| `event_observed_at` | `match_start_utc + match_elapsed_us` |
| `origin_x_pct`, `origin_y_pct` | Nullable `decimal(6,3)` in `[0,100]` |
| `destination_x_pct`, `destination_y_pct` | Nullable second coordinate |
| `coordinate_frame` | `wyscout_attack_oriented_percent` |
| `tag_ids` | Sorted unique `int32` list |
| `semantic_family`, `outcome_code` | Nullable, reviewed lookup mapping only |
| `semantic_state` | `mapped`, `unmapped_event`, `unmapped_tag`, `invalid_coordinate`, `invalid_reference` |
| `source_record_ordinal` | Stable tie evidence only |
| `possession_eligible` | True only when required semantics resolve |

The parser reads the lexical number into `Decimal`, rejects non-finite, negative, or
more-than-six-decimal values, and converts exactly to microseconds without float or
rounding. Unknown lookup, extra positions, or invalid coordinates are never guessed.
Raw percentages are not converted to metres because pitch dimensions are absent.

### 7.7 `silver_possession`

Grain: one project-derived contiguous resolved-control sequence.

| Field | Type / rule |
|---|---|
| `possession_id` | Deterministic match/ruleset/ordinal UUID |
| `match_id` | UUID |
| `possession_ordinal` | `int32 >= 0` |
| `team_id` | Nullable only for uncertain/failed sequence |
| `start_action_id`, `end_action_id` | First/last unambiguous action |
| `start_match_elapsed_us`, `end_match_elapsed_us` | Non-decreasing `int64` |
| `resolved_action_count` | `int32 >= 1` |
| `boundary_action_count` | `int32 >= 0` |
| `derivation_version` | Ruleset and taxonomy versions |
| `derivation_state` | `resolved`, `uncertain`, `failed` |
| `reason_codes` | Sorted; empty only when resolved |
| `gold_eligible` | Resolved and match fully reconciled |

The separate action assignment is
`(action_id, possession_id nullable, assignment_state, reason_codes)`. Each action has
zero or one possession.

## 8. Deterministic possession derivation

The reviewed mapping assigns admitted event/subevent and tag IDs to:
`CONTROL`, `CONTESTED`, `DEAD_BALL`, `RESTART`, or `NON_CONTROL_ADMIN`. Unknown IDs are
`UNMAPPED`; names are display evidence, not substring rules.

For each match:

1. Validate event-ID uniqueness, resolved match/team references, classified periods,
   non-decreasing clocks, and finite coordinates. Structural conflicts fail the match.
2. Order by `(period_rank, period_elapsed_us, source_record_ordinal,
   source_event_id)`. Competing-team timestamp ties become
   `simultaneous_cross_team_actions`.
3. Resolved `CONTROL` or `RESTART` opens possession; same team continues it.
4. Opposing resolved control closes the prior possession at its last unambiguous action
   and opens a new one.
5. `DEAD_BALL` closes possession; mapping determines whether the action belongs to the
   prior sequence.
6. `CONTESTED`, administrative, missing-player, and unmapped actions enter a buffer.
   Same-team control may attach only explicitly attachable classes. A team change
   leaves the buffer unassigned and marks both boundaries contested. A period end
   before resolution makes the possession uncertain.
7. Period boundaries close possession; no possession crosses half-time.
8. Missing control team makes the boundary uncertain. Missing player alone reduces
   coverage without changing resolved team control.
9. Only deterministic boundaries emit `resolved`. Partial sequences are diagnostic
   `uncertain`, never Gold. Ordering, taxonomy, identity, or structural failures emit
   `failed`.

The result is project-derived and does not claim parity with a native commercial
possession product.

## 9. Temporal Gold player-window boundary

W04 Gold is evidence and coverage state for W05 feature registration, not a role score
or retrieval output.

### 9.1 Exact grain and key

There is exactly one `gold_player_window` row for:

```text
player_id
competition_id
season_id
window_definition_id
window_start_utc
window_end_utc
feature_cutoff_ts
dependency_lineage_hash
```

That ordered tuple is the logical uniqueness key. The player, competition, and season
identity fields appear once in the schema below; there is no duplicate identity row.

The initial window is:

```text
window_definition_id = "wyscout-v5-domestic-season-to-date-v1"
window_start_utc      = admitted competition-season start, inclusive
window_end_utc        = requested as-of match/date boundary, exclusive
feature_cutoff_ts     = explicit UTC instant strictly after release
```

A match enters only when `match_start_utc < window_end_utc` and every used dependency
has `observed_at < feature_cutoff_ts` and
`available_at < feature_cutoff_ts`. This is not a claim that the collection was
available during 2017/18.

### 9.2 Deduplicated `gold_player_window` schema

| Field | Type / rule |
|---|---|
| `player_window_snapshot_id` | Deterministic UUID from Section 6 |
| `player_id` | Resolved UUID; one occurrence |
| `competition_id` | Resolved UUID; one occurrence |
| `season_id` | Resolved UUID; one occurrence |
| `window_definition_id` | Frozen string |
| `window_start_utc`, `window_end_utc` | Half-open observed window |
| `role_context_state` | `unavailable_until_w05` |
| `match_count` | Distinct reconciled matches, `int32 >= 0` |
| `resolved_lineup_stint_count` | `int32 >= 0` |
| `minutes_lower`, `minutes_upper` | Nullable `decimal(10,3)` interval |
| `action_count` | `int64 >= 0` |
| `coordinate_known_action_count` | Complete-origin actions, `int64 >= 0` |
| `resolved_possession_action_count` | Nullable `int64 >= 0`; null unless match possession fully resolved |
| `unresolved_action_count` | Explicit ambiguous/missing semantics, `int64 >= 0` |
| `feature_names` | Ordered names from `match_count` through `unresolved_action_count` |
| `feature_schema_hash` | SHA-256 of names, order, Arrow types, semantics, missingness |
| `snapshot_as_of_ts` | Maximum admitted dependency observation |
| `available_at_watermark` | Maximum dependency availability |
| `valid_from_ts` | `max(snapshot_as_of_ts, available_at_watermark)` |
| `generated_at_ts` | Run metadata, not eligibility |
| `feature_cutoff_ts` | Strict upper bound later than release |
| `source_manifest_ids` | Ordered exact immutable source UUIDs |
| `dependency_lineage_hash` | Canonical dependency digest |
| `coverage_overall` | Reviewed `float64` in `[0,1]` |
| `coverage_dimensions` | Ordered identity, lineup, action, coordinate, possession, temporal structs |
| `missing_dimensions` | Sorted; never inferred from zero |
| `applicability_state` | `research_only`, `w04_data_ready`, `suppressed` |
| `applicability_reason_codes` | Sorted; empty only for `w04_data_ready` |

`snapshot_as_of_ts` cannot predate an admitted observation and `valid_from_ts` cannot
predate release. Missing availability suppresses the W05-consumable Gold manifest.
Later acquisition remains receipt evidence and never moves source availability into
2017/18.

## 10. Quality, reconciliation, and leakage gates

No weighted aggregate can waive a mandatory failure.

### 10.1 Source and archive

- Exactly seven configured source-object receipts; exact size and MD5; computed
  SHA-256 for each.
- `matches.zip`: exactly seven safe unique entries, exactly five admitted and exactly
  two known excluded.
- `events.zip`: exactly seven safe unique entries, exactly five admitted and exactly
  two known excluded.
- Across both archives: ten admitted member payloads, four verified directory-only
  exclusions, and zero other entries.
- Known-excluded payload streams opened, bytes read, files extracted, parsed records,
  member payload hashes, or downstream uses: exactly `0`.
- Unknown, missing, duplicate, link, absolute, parent-traversal, directory, encrypted,
  malformed, or unsafe entries: exactly `0` in an accepted archive.
- Every parsed admitted member reconciles:
  `records_seen = records_admitted + records_quarantined + records_scope_excluded`.
- Object, admitted-member, record-index, quarantine, and partition-manifest digests
  reconcile. Five-partition counts are measured, never copied from seven-competition
  publication totals.

### 10.2 Identity

- Competition, season, team, and match references resolve `100%`; duplicate or
  conflicting canonical IDs are zero.
- Every non-zero player ID used by Gold resolves exactly once.
- Zero/missing player remains explicit actor missingness.
- Gold-consumed `review_required` and `rejected_conflict` counts are zero.

### 10.3 Match, lineup, action, and possession

- Each match has two distinct resolved teams; every event team belongs to the match.
- Event rows reconcile exactly to admitted source event rows; no duplicate or silently
  dropped action IDs.
- Starting lineups contain no duplicate. Substitutions conserve on-pitch membership.
- Player/match stints do not overlap and team count never exceeds 11. Unknown removal
  semantics make minute products unavailable.
- Coordinates are measured by event/subevent family. Invalid coordinates are zero in
  Gold-eligible actions.
- Each action has zero or one possession assignment. Resolved possessions are ordered,
  non-overlapping, period-contained, and match-local.
- A Gold possession field requires `100%` resolved possession derivation for every
  contributing match; partial success is missing, not zero.

### 10.4 Temporal and missingness

- Post-cutoff observations admitted: `0`.
- At/after-cutoff availability admitted: `0`.
- Gold cutoffs at or before `2020-01-28T14:24:27Z`: `0` eligible rows.
- Missing availability in a W05-consumable row: `0`.
- Wyscout `acquired_at` earlier than release: `0` accepted manifests.
- Acquisition, availability, observation, and generation are separately named.
- Structural keys are non-null. Semantic null reason codes are frozen:
  `not_observed`, `not_applicable`, `unmapped`, `unresolved_identity`,
  `unresolved_boundary`, `scope_excluded`, `source_unavailable`.
- W04 performs no numeric imputation.

### 10.5 Range, consistency, and rights

- IDs satisfy their domains and uniqueness grain.
- Counts and minutes are non-negative; lower never exceeds upper.
- Clocks are non-negative, finite, classified, and non-decreasing within period.
- Coordinates are finite in `[0,100]` and retain their percentage frame.
- Scores are non-negative and winner/draw values agree with match teams.
- Coverage dimensions are in `[0,1]`; observed does not exceed expected.
- Derived manifests retain attribution and the effective no-external-export control.

## 11. Deterministic rebuild

The rebuild input identity is:

```text
SHA256(canonical_json({
  source_object_sha256s_in_config_order,
  archive_directory_entry_names_and_classifications_in_config_order,
  admitted_archive_member_sha256s_in_config_order,
  source_manifest_id,
  field_registry_hash,
  identity_ruleset_version,
  lineup_ruleset_version,
  event_taxonomy_map_hash,
  possession_ruleset_version,
  gold_schema_hash,
  feature_cutoff_ts,
  code_checkpoint
}))
```

No excluded member payload digest exists because excluded streams are never opened.
Their names/classifications are bound to the already verified parent archive SHA-256.

The rebuild:

1. starts with empty declared guarded working roots;
2. verifies object receipts and exact archive directories before reading admitted
   member payloads;
3. processes objects and domestic partitions in configured order;
4. sorts rows by canonical primary keys, never filesystem, map, locale, or wall-clock
   order;
5. uses exact decimal/integer normalization, canonical UTC, sorted reason/tag/lineage
   lists, and fixed Arrow/Parquet schemas and writer options;
6. writes immutable payloads atomically and completion manifests last;
7. computes semantic digests excluding `generated_at`, host path, elapsed time, and run
   ID, which remain in a separate operational receipt;
8. rebuilds raw-to-Gold twice in independent empty roots and requires equal Bronze,
   Silver, Gold, schema, count, and lineage digests; and
9. emits the first differing product, partition, key, column, and digests on mismatch,
   with no accepted manifest.

## 12. Serial and path-disjoint implementation map

The generic temporal contract correction and independent review are complete
prerequisites. They require no W03 migration. The master owns integration, dependencies,
migrations, registries, gate evidence, and Git.

| Order | Packet | Proposed exact write scope | Dependency / concurrency |
|---|---|---|---|
| 1 | `W04-DATA-CONTRACTS-R1` | `src/scouting/contracts/data.py`; `src/scouting/contracts/__init__.py`; `tests/contracts/test_w04_data_contracts.py`; return | Serial shared contract |
| 2 | `W04-ACQUISITION-R1` | `src/scouting/sources/wyscout.py`; `scripts/acquire_wyscout_v5.py`; `tests/unit/test_wyscout_acquisition.py`; return | After contracts; implements exact archive directory and Wyscout release-floor checks |
| 3 | `W04-BRONZE-R1` | `src/scouting/data_products/wyscout/bronze.py`; `tests/unit/test_wyscout_bronze.py`; return | After acquisition; serial before consumers |
| 4 | `W04-IDENTITY-R1` | `src/scouting/identity/wyscout.py`; `tests/unit/test_wyscout_identity.py`; return | After Bronze; serial identity authority |
| 5A | `W04-SILVER-ENTITY-STINT-R1` | `src/scouting/data_products/wyscout/entities.py`; `src/scouting/data_products/wyscout/lineups.py`; `tests/unit/test_wyscout_entities_lineups.py`; return | After identity; path-disjoint from 5B |
| 5B | `W04-SILVER-ACTION-R1` | `src/scouting/data_products/wyscout/actions.py`; `tests/unit/test_wyscout_actions.py`; return | After identity; path-disjoint from 5A |
| 6 | `W04-POSSESSION-R1` | `src/scouting/data_products/wyscout/possessions.py`; `tests/unit/test_wyscout_possessions.py`; return | After 5B and reviewed taxonomy map |
| 7 | `W04-GOLD-TEMPORAL-R1` | `src/scouting/data_products/wyscout/gold.py`; `tests/unit/test_wyscout_gold.py`; return | After 5A, 5B, 6; serial Gold writer |
| 8 | `W04-QUALITY-R1` | `src/scouting/data_products/wyscout/quality.py`; `tests/integration/test_wyscout_rebuild.py`; return | After products; no writer overlap |
| 9 | `W04-INDEPENDENT-REBUILD-R1` | `tests/security/test_w04_temporal_leakage.py`; `reports/reviews/W04/wyscout-rebuild-review-R1.md`; return | Test/report-only independent reviewer |

Before dispatch, the master verifies exact path ownership and no packet overlap.
Shared contracts, migrations, dependencies, registry exports, and integration remain
serial. If storage tables are insufficient, only a separate master-owned and
second-reviewed migration packet may modify them; this design grants no migration
authority.

## 13. Required evidence and stop rules

Each build retains:

- seven source-object receipts and exact archive-directory receipts;
- proof of five admitted and two unextracted known exclusions per archive;
- Bronze admission/quarantine and reconciliation;
- identity resolution and review;
- match/action/lineup/possession reconciliation;
- coverage, missingness, range, rights, and temporal evidence;
- measured five-partition dataset-card counts;
- two-run deterministic comparison;
- exact schema/ruleset hashes, attribution, policy, and local checkpoint.

Stop rather than improvise when:

- configured URL, size, MD5, SHA-256, directory set, or admitted member fails;
- any known-excluded stream would need to be opened or any unknown entry is present;
- a source ID or field registry fails;
- period, substitution, event, tag, possession, or identity semantics are unavailable;
- a real record lacks provable availability;
- a Wyscout receipt claims acquisition before the frozen release;
- a write would leave guarded roots;
- work requires a new source, licence, architecture, dependency, migration, remote
  service, cloud resource, public endpoint, external model, or broader claim.

The safe result is evidence plus a bounded master decision, never a guessed product.

## 14. R2 correction closure

- **W04-DESIGN-ARCHIVE-SCOPE-01:** corrected. Each archive must have exactly five
  admitted and two named known exclusions. Excluded payloads remain unopened and any
  other entry fails.
- **W04-DESIGN-CLOCK-ORDER-01:** corrected. The generic contract permits either
  truthful order; only Wyscout enforces acquisition at or after its frozen release.
  No W03 migration is requested.
- **W04-DESIGN-GOLD-DUPLICATE-01:** corrected. Gold identity fields appear exactly once
  and one explicit logical key defines row uniqueness.

Recommendation to master: **R2 is ready for independent review.** This is not
self-approval and does not claim the W04 phase gate has passed.


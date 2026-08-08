# W04 Wyscout v5 canonical schema and rebuild design — R1

Status: **implementation design for master review; not self-approved**

This design covers the frozen Wyscout Soccer match event dataset, figshare collection
v5, and only the five authorised 2017/18 domestic top-flight partitions. It was
produced without downloading or inspecting a football-data payload. It defines the
next implementation packets; it does not claim that an implementation or data gate has
passed.

## 1. Authority, claim boundary, and blocking precondition

The controlling authorities are:

- **A1:** `../scouting-ml-production-blueprint.html`, especially Sections 03–04,
  P2.1–P2.9, G2, Section 09, and decisions D1, D4, D6, D10–D13.
- **A2:** `../scouting-ml-agent-implementation-workflow.html`, especially W04 and its
  data-product verification requirements.
- **A3:** `configs/sources/w04-provider.yaml`, the normative object, archive, coverage,
  rights, attribution, acquisition, and temporal declaration.
- **A4:** `docs/dataset-cards/w04-source.md`, the intended-use, population, coverage,
  temporal, and non-claim card.
- **A5:** `reports/phase-gates/W04/provider-rights-research-packet.md`, including its
  2026-07-29 decision addendum and Wyscout figshare v5 dossier.
- **A6:** `src/scouting/contracts/evidence.py`, the accepted strict evidence and
  temporal contract floor.
- **A7:** `src/scouting/storage/guarded.py`, the immutable, atomic, path-guarded
  persistence boundary.
- **A8:** `src/scouting/sources/synthetic.py`, the accepted strict-before temporal,
  canonical digest, ambiguity, and fail-closed implementation pattern.

The permitted claim is a frozen historical engineering and player-retrieval proof.
This design makes no claim about current players, current source continuity, current
scouting coverage, women or youth populations, prospective effectiveness, competition
strength, or parity with a current commercial Wyscout product.

### Serial contract correction required before acquisition

The source authority fixes `source_available_at` at
`2020-01-28T14:24:27Z`, while an actual local acquisition necessarily occurs later.
`SourceSnapshotManifest` currently rejects `available_at < acquired_at`. Recording the
2020 release as a later local acquisition would fabricate evidence.

Before an acquisition packet can construct the accepted manifest, the master must issue
a serial, second-reviewed contract packet that distinguishes provider/publication
availability from local acquisition time, or corrects the ordering invariant so the
true release may precede the true fetch. The implementation must not set
`acquired_at=2020-01-28T14:24:27Z` unless that is genuinely the local acquisition time.
This is a contract-semantic correction, not authority to change the source, rights, or
local-only architecture.

The corrected invariant is exact:

```text
available_at = source publication/knowledge instant
acquired_at = actual completed local acquisition instant
require available_at <= acquired_at
```

The serial contract packet must add regression tests that:

1. accept Wyscout publication at `2020-01-28T14:24:27Z` with a truthful later local
   acquisition;
2. accept equality for an instantaneous synthetic publication/acquisition;
3. reject `available_at > acquired_at`;
4. retain strict UTC, unknown-field rejection, frozen JSON round-trip, and attribution
   validation;
5. accept TemporalEvidence only when the feature cutoff is strictly later than the
   publication/knowledge instant, and reject cutoff equality; and
6. identify and migrate any W03 synthetic consumer that currently treats
   `acquired_at` as an acquisition-start time before `available_at`. That consumer
   migration must be a separate master packet with regenerated fixture/lineage digests,
   not an implicit compatibility waiver.

## 2. Global invariants

These rules apply to every layer:

1. IDs are lower-case canonical UUIDs derived deterministically from frozen source IDs;
   display names are never join keys.
2. All timestamps are UTC `timestamp[us, tz=UTC]`. Naive or non-UTC values fail.
3. All semantic payloads carry `schema_version`, `tenant_id`, source manifest ID,
   record/dependency lineage digest, `observed_at`, `available_at`, and
   `generated_at`.
4. `observed_at < feature_cutoff_ts` and
   `available_at < feature_cutoff_ts` are both strict. Equality fails closed.
5. Every Wyscout v5 record has
   `available_at=2020-01-28T14:24:27Z`. Local fetch/run time is never substituted for
   evidence availability.
6. No historical snapshot with a cutoff at or before the release time is eligible.
7. Unversioned player-master attributes are never historical features. Match-bound
   team, lineup, substitution, and event evidence is authoritative for match context.
8. Unknown top-level fields, archive members, period codes, event/subevent semantics,
   tag semantics, or identity conflicts are retained as rejection evidence and are not
   guessed into Silver or Gold.
9. Source rights are the strictest effective control. The manifest classification is
   `OPEN`, derived/internal review are true, external/raw export is false under the
   stricter project boundary, and the exact A3 attribution is mandatory.
10. Payload content digests exclude wall-clock run metadata. The same admitted inputs,
    schema/rule versions, and code produce byte-identical semantic outputs.

## 3. Authoritative object and product topology

The acquisition object set is exactly the seven A3 objects:
`competitions.json`, `teams.json`, `players.json`, `matches.zip`, `events.zip`,
`eventid2name.csv`, and `tags2name.csv`. Size and MD5 are admission controls; a
computed SHA-256 is the immutable project identity.

Logical guarded paths are:

```text
data/source/wyscout/v5/objects/<file_id>/<configured_name>
data/source/wyscout/v5/members/<archive_file_id>/<allowlisted_member_name>
data/working/wyscout/v5/bronze/<source_manifest_id>/<record_kind>/
data/working/wyscout/v5/silver/<build_id>/<product_name>/
data/working/wyscout/v5/gold/<build_id>/player_window/
data/manifests/wyscout/v5/<layer>/<content_digest>.manifest.json
```

An implementation must resolve these through named `GuardedStorage` roots, never by
accepting an arbitrary absolute path. Writes are payload-first and completion-manifest
last. Repeating identical content is idempotent; conflicting content at the same
logical identity is an error.

## 4. Bronze boundaries

### 4.1 Physical Bronze objects

| Boundary | Grain and identity | Payload | Completion rule |
|---|---|---|---|
| `source_object` | One configured figshare file, key `(source_manifest_id, file_id)` | Exact downloaded bytes; never rewritten or decompressed in place | Exact URL allowlist, configured filename, exact byte size, expected MD5, computed SHA-256 |
| `source_archive_member` | One safely admitted member, key `(source_object_sha256, member_path)` | Exact uncompressed member bytes | Member path is relative, non-link, non-duplicate and on the five-name allowlist for its archive |
| `bronze_record_index` | One top-level JSON record or CSV lookup row, key `(member_sha256, record_ordinal)` | Structural index and canonical record digest; the raw payload remains in its member object | Entire member parses; field admission state recorded for every record |
| `bronze_quarantine` | One rejected object/member/record | Metadata, bounded reason codes, field names and digests; no confidential raw copy beyond the already guarded source object | Written for every rejection before a product is marked complete |
| `bronze_partition_manifest` | One object kind × country partition | Counts and ordered record digests | Written only when raw/index/quarantine counts reconcile |

Unknown archive members are not extracted or admitted. Under A3
`reject_unknown_members: true`, their presence prevents a completion manifest; the
implementation must not silently infer the excluded tournament filenames. If the real
archive contains undeclared members, the acquisition packet must stop for a master
authority correction rather than relaxing the allowlist.

### 4.2 Bronze record-index schema

All fields are required unless marked nullable.

| Field | Type | Rule |
|---|---|---|
| `schema_version` | `int16` | Constant `1` |
| `tenant_id` | canonical UUID string | Explicit single-tenant context |
| `source_manifest_id` | canonical UUID string | Accepted source delivery |
| `source_object_file_id` | `int64` | Exact A3 figshare file ID |
| `source_object_sha256` | 64-char lower-case hex | Digest of downloaded bytes |
| `source_member_path` | UTF-8 string | Configured filename or allowlisted archive member |
| `source_member_sha256` | 64-char lower-case hex | Digest of exact member bytes |
| `source_record_kind` | enum | `competition`, `team`, `player`, `match`, `event`, `event_type_lookup`, `tag_lookup` |
| `source_record_id` | UTF-8 string, nullable only for lookup rows | Provider record ID in canonical decimal text |
| `source_record_version` | UTF-8 string | `figshare-v5:<source_member_sha256>:<record_digest>` |
| `record_ordinal` | `int64 >= 0` | Original array/CSV order; evidence, not a semantic ordering claim |
| `raw_record_sha256` | 64-char lower-case hex | SHA-256 of canonical JSON value or canonical CSV row |
| `raw_field_names` | sorted list of strings | Exact observed top-level field set |
| `parser_version` | UTF-8 string | Immutable parser/rule identifier |
| `admission_state` | enum | `admitted`, `quarantined_unknown_field`, `quarantined_invalid_shape`, `quarantined_conflict`, `scope_excluded` |
| `rejection_reason_codes` | sorted list of strings | Empty only when admitted |
| `observed_at` | UTC timestamp, nullable by kind | Match/event occurrence; entity/lookups may be null |
| `available_at` | UTC timestamp | Always the frozen release time |
| `acquired_at` | UTC timestamp | Truthful local fetch completion time |
| `generated_at` | UTC timestamp | Index construction metadata only |
| `rights_policy_id` | UTF-8 string | Frozen W04 source-policy identifier |
| `attribution_text` | UTF-8 string | Exact A3 attribution |

The record index does not duplicate raw records. A consumer resolves the immutable
member by digest and record ordinal. Canonical re-serialisation is used only to compute
`raw_record_sha256`; it is not represented as the original byte layout.

### 4.3 Bronze schema admission

- Each record kind has a checked-in allowlist with fields classified as
  `transformed`, `preserved_not_transformed`, or `forbidden`.
- A field absent from the registry quarantines that record. A known optional field may
  be absent and is recorded in coverage.
- Provider IDs must be integral, non-negative, and exactly representable as `int64`.
  Boolean, float, whitespace-normalised, or lossy ID coercion is forbidden.
- Duplicate `(record_kind, source_record_id)` with the same record digest is
  idempotent. Different digests create `quarantined_conflict`; no last-write-wins rule
  exists in frozen v5.
- `dateutc`, `matchPeriod`, and `eventSec` are the only authorised occurrence-time
  inputs. File modification time, request time, and generated time are not evidence.
- The structural parser may preserve fields whose semantics are not used, but no
  downstream semantic mapping may be invented from their name.

## 5. Canonical identity design

### 5.1 Deterministic UUID algorithm

Freeze this exact algorithm and namespace strings in the identity contract:

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
         "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
kind_namespace =
  UUIDv5(source_namespace, "<competition|season|team|player|match|event>")
canonical_id =
  UUIDv5(kind_namespace, "figshare-v5:<canonical-decimal-source-id>")
```

Whitespace, signs, leading zeroes, float coercion, and display names never enter the
name string. A season ID is generated only when a valid frozen source season ID is
present. Derived IDs use their own namespace:

```text
lineup_stint_id = UUIDv5(match_namespace,
  "stint:<team_source_id>:<player_source_id>:<stint_ordinal>:<ruleset_version>")
possession_id = UUIDv5(match_namespace,
  "possession:<possession_ordinal>:<ruleset_version>")
player_window_snapshot_id = UUIDv5(player_namespace,
  "window:<window_definition_id>:<cutoff_utc>:<dependency_lineage_hash>")
```

### 5.2 Crosswalk schema and state machine

| Field | Type / rule |
|---|---|
| `identity_evidence_id` | Deterministic UUID from source identity + evidence version |
| `tenant_id` | Canonical UUID |
| `entity_kind` | `competition`, `season`, `team`, `player`, `match`, `event` |
| `provider` | Constant `wyscout_figshare` |
| `source_id` | Canonical decimal text |
| `source_version` | `figshare-v5:<raw_record_sha256>` |
| `canonical_id` | UUID; null unless state is resolved |
| `version` | Positive integer, `1` for the first frozen evidence |
| `match_method` | `exact` only for a valid unique provider ID; `reviewed` only with reviewer evidence |
| `confidence` | `1.0` for structurally exact unique source-ID mapping; no guessed intermediate value |
| `state` | `resolved`, `review_required`, `rejected_missing_id`, `rejected_conflict`, `superseded` |
| `evidence_digest` | Canonical digest of record IDs/digests and rule version |
| `available_at` | Frozen collection release |
| `valid_from` | Frozen collection release for this snapshot mapping |
| `valid_to` | Null unless a separately evidenced supersession exists |
| `reviewed_by` | Required only for `reviewed` |
| `reason_codes` | Sorted, non-empty unless structurally resolved |

Resolution rules:

1. A unique, valid, non-zero provider ID within one entity kind maps exactly to its
   deterministic canonical UUID.
2. Provider player ID `0` or a missing player ID means `provider_actor_unidentified`;
   it does not create player zero and does not name-match to a master record.
3. A referenced non-zero ID absent from its admitted master/match evidence enters
   `review_required` and blocks that reference from Gold.
4. Same source ID plus different record digests is `rejected_conflict`; frozen v5 has
   no correction ledger, so neither record silently supersedes the other.
5. Different source IDs with identical names remain different identities. Names,
   short names, current team, birth attributes, position labels, and nationality never
   auto-merge records.
6. Publication-time `currentTeamId` and other unversioned player-master fields may be
   stored as Bronze evidence but may not create match-era team membership.
7. Corrections require a new evidence version, reviewer, reason, valid interval, and
   supersession digest. They never mutate version 1.

## 6. Silver schemas

### 6.1 Common Silver lineage columns

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

`dependency_lineage_hash` is SHA-256 of canonical JSON containing the ordered
dependency tuples `(kind, id, digest, observed_at, available_at)`. Dependency order is
fixed as source manifest, source record, then sorted identity evidence.

### 6.2 `silver_match`

Grain: one admitted match.

| Field | Type | Null / semantic rule |
|---|---|---|
| `match_id` | UUID string | Deterministic canonical match ID; primary key |
| `source_match_id` | `int64` | Required and unique |
| `competition_id` | UUID string | Required resolved crosswalk |
| `season_id` | UUID string | Required resolved crosswalk |
| `home_team_id` / `away_team_id` | UUID string | Required, distinct, and match-bound |
| `match_start_utc` | UTC timestamp | Strict parse of `dateutc`; also base occurrence time |
| `provider_status` | string | Preserved exact allowlisted value; no invented status mapping |
| `provider_duration` | string, nullable | Preserved; semantics unavailable unless separately classified |
| `home_score` / `away_score` | `int16 >= 0`, nullable | Only from match-bound team data |
| `winner_team_id` | UUID string, nullable | Null for draw/unknown; must be one of the match teams |
| `venue_text` | string, nullable | Display evidence only; not a feature |
| `match_coverage_state` | enum | `structural_only`, `events_reconciled`, `lineups_reconciled`, `complete`, `failed` |
| `coverage_reason_codes` | sorted list of strings | Required unless `complete` |

`observed_at=match_start_utc`; `available_at` remains the collection release. Provider
`date` or file ordering never overrides `dateutc`.

### 6.3 `silver_team`

Grain: one provider team identity at frozen v5.

| Field | Type | Rule |
|---|---|---|
| `team_id` | UUID string | Primary key |
| `source_team_id` | `int64` | Required unique source key |
| `display_name` | string | Source display value; never an identity key |
| `official_name` | string, nullable | Display evidence only |
| `team_type` | string, nullable | Preserved provider value; no senior/youth inference |
| `area_source_id` | string, nullable | Preserved reference; no geography feature |
| `entity_eligibility` | enum | `identity_only`; team master fields do not establish match membership |

Entity `observed_at` is null because the frozen authority supplies no fact-validity
time. `available_at` is the collection release.

### 6.4 `silver_player`

Grain: one provider player identity at frozen v5.

| Field | Type | Rule |
|---|---|---|
| `player_id` | UUID string | Primary key |
| `source_player_id` | `int64` | Required unique non-zero source key |
| `display_name` | string | Display and review only; never identity matching |
| `provider_role_name` | string, nullable | Publication-time descriptive value; not historical role evidence |
| `provider_master_digest` | SHA-256 | Binds the exact master record |
| `historical_feature_eligible` | boolean | Constant `false` for unversioned master attributes |
| `entity_eligibility` | enum | `identity_and_display_only` |

Birth date, height, weight, foot, nationality, and current-team fields remain Bronze in
W04. They require later field-level privacy, semantics, and historical-validity review
before feature use. Match membership comes only from match-bound lineup, bench,
substitution, and event evidence.

### 6.5 `silver_lineup_stint`

Grain: player × match × continuous, derivable on-pitch interval.

| Field | Type | Rule |
|---|---|---|
| `lineup_stint_id` | UUID string | Deterministic derived ID |
| `match_id`, `team_id`, `player_id` | UUID strings | All resolved; team must be a match team |
| `stint_ordinal` | `int16 >= 0` | Ordered within player/match |
| `start_elapsed_us_min` / `start_elapsed_us_max` | `int64 >= 0` | Inclusive boundary bounds; equal only when exact |
| `end_elapsed_us_min` / `end_elapsed_us_max` | `int64 >= 0` | Inclusive boundary bounds; end bounds cannot precede start bounds |
| `duration_us_min` / `duration_us_max` | `int64 >= 0` | `max(0, end_min-start_max)` and `end_max-start_min` |
| `start_reason` | enum | `starting_lineup`, `substitution_in` |
| `end_reason` | enum | `substitution_out`, `match_end`, `unresolved` |
| `boundary_precision` | enum | `match_start`, `provider_minute`, `match_end`, `unknown` |
| `provider_substitution_ordinal` | `int32`, nullable | Original source order for evidence only |
| `simultaneous_group` | string, nullable | Same reported substitution minute; no invented order |
| `derivation_state` | enum | `resolved`, `uncertain`, `failed` |
| `reason_codes` | sorted list of strings | Empty only when resolved |

The authority states that stints must be reconstructed but does not establish
substitution-second precision or stoppage-time convention. Therefore a provider minute
`m` becomes the inclusive microsecond bounds
`[m*60_000_000, (m+1)*60_000_000-1]`, never a fabricated exact second. A proven exact
match boundary has equal minimum/maximum. Starting players begin at exact match start.
Substitutions are processed by reported minute and then source ordinal solely for
deterministic replay; equal-minute substitutions share a simultaneous group.

For every substitution, the outgoing player must be on pitch for that team, the
incoming player must not be on pitch, and the change must conserve the team count.
Violations make the match lineup derivation `failed`; no last-known lineup is guessed.
Bench-only players generate no on-pitch stint. Match end is taken only from an
explicitly classified provider duration/terminal rule. The maximum event clock is a
lower bound, never proof of the whistle time. Where match end is unprovable, the final
boundary is `unknown`, minutes are an interval, and minute-based Gold fields are
unavailable.

### 6.6 `silver_action`

Grain: one admitted provider event.

| Field | Type | Rule |
|---|---|---|
| `action_id` | UUID string | Deterministic from provider event ID |
| `source_event_id` | `int64` | Required unique within frozen snapshot |
| `match_id`, `team_id` | UUID strings | Required resolved references |
| `player_id` | UUID string, nullable | Null only for explicit provider missing/zero actor |
| `source_event_type_id` / `source_subevent_type_id` | `int32` | Preserved exact provider IDs |
| `source_event_name` / `source_subevent_name` | string | Must agree with admitted lookup; never parsed heuristically |
| `period_code` | enum | First pass admits only classified `1H` and `2H`; unknown codes quarantine the match for temporal products |
| `period_elapsed_us` | `int64 >= 0` | Exact decimal conversion of `eventSec`; more than six fractional digits quarantines the record |
| `match_elapsed_us` | `int64 >= 0` | `period_elapsed_us` for `1H`; `2_700_000_000 + period_elapsed_us` for `2H` |
| `event_observed_at` | UTC timestamp | `match_start_utc + match_elapsed_us` |
| `origin_x_pct` / `origin_y_pct` | `decimal(6,3)`, nullable | First coordinate, bounded `[0,100]` |
| `destination_x_pct` / `destination_y_pct` | `decimal(6,3)`, nullable | Second coordinate only; absent is not imputed |
| `coordinate_frame` | enum | `wyscout_attack_oriented_percent` |
| `tag_ids` | sorted unique list of `int32` | Exact provider tag IDs |
| `semantic_family` | enum, nullable | From versioned reviewed event/subevent lookup only |
| `outcome_code` | string, nullable | From versioned reviewed tag mapping only |
| `semantic_state` | enum | `mapped`, `unmapped_event`, `unmapped_tag`, `invalid_coordinate`, `invalid_reference` |
| `source_record_ordinal` | `int64` | Evidence for stable tie handling, not a claim of causal order |
| `possession_eligible` | boolean | True only when all possession-required semantics are resolved |

`eventSec` is treated as period-relative because A3/A5 define occurrence as match start
plus period and event seconds. The parser consumes the JSON lexical number into
`Decimal`, requires at most six fractional digits, and multiplies exactly by
`1_000_000`; it never passes through binary float or rounds. Negative, non-finite, or
unrepresentable values fail.
More than two positions, disagreement with lookup IDs/names, or unknown taxonomy never
creates an inferred action meaning. Raw percentage coordinates are not converted to
metres because pitch dimensions are absent.

### 6.7 `silver_possession`

Grain: one project-derived, contiguous resolved-control sequence.

| Field | Type | Rule |
|---|---|---|
| `possession_id` | UUID string | Deterministic match/ruleset/ordinal ID |
| `match_id` | UUID string | Required |
| `possession_ordinal` | `int32 >= 0` | Canonical order within match |
| `team_id` | UUID string, nullable | Null only for uncertain/failed sequence |
| `start_action_id` / `end_action_id` | UUID strings | First/last unambiguous action |
| `start_match_elapsed_us` / `end_match_elapsed_us` | `int64` | Non-decreasing |
| `resolved_action_count` | `int32 >= 1` | Actions unambiguously assigned |
| `boundary_action_count` | `int32 >= 0` | Buffered contested/unmapped actions |
| `derivation_version` | string | Frozen ruleset and taxonomy-map versions |
| `derivation_state` | enum | `resolved`, `uncertain`, `failed` |
| `reason_codes` | sorted list of strings | Empty only when resolved |
| `gold_eligible` | boolean | True only for resolved possessions in a fully reconciled match |

The action-to-possession relation is stored separately at grain action:
`(action_id, possession_id nullable, assignment_state, reason_codes)`. It is a
one-to-zero-or-one relationship; an action is never duplicated across possessions.

## 7. Deterministic possession derivation

The possession ruleset is a versioned mapping from admitted event/subevent IDs and tag
IDs to exactly five control classes:

`CONTROL`, `CONTESTED`, `DEAD_BALL`, `RESTART`, and `NON_CONTROL_ADMIN`.

The mapping may use the admitted `eventid2name.csv` and `tags2name.csv` only after a
reviewed mapping packet. Names are display evidence, not substring rules. An unmapped
ID is `UNMAPPED`; it is never assigned from football intuition.

For each match:

1. Validate unique event IDs, resolved match/team references, classified period codes,
   non-decreasing period clocks, and finite coordinates. A duplicate conflict, reversed
   period, or unknown period yields match state `failed` and no Gold-eligible
   possessions.
2. Order by `(period_rank, period_elapsed_us, source_record_ordinal,
   source_event_id)`. Original ordinal only resolves byte-identical timestamp ties.
   A tied group containing competing teams receives
   `simultaneous_cross_team_actions`.
3. `CONTROL` or `RESTART` with a resolved team starts a possession when none is open.
   The same team continues the open possession.
4. Opposing `CONTROL` or `RESTART` closes the previous possession at its last
   unambiguous action and starts a new possession at the current action.
5. `DEAD_BALL` closes the open possession. The dead-ball action is recorded as a
   boundary action unless the reviewed map explicitly declares it part of the prior
   sequence.
6. Consecutive `CONTESTED`, `NON_CONTROL_ADMIN`, missing-player, or unmapped actions
   enter a boundary buffer. On the next resolved control:
   - if control remains with the open team, the buffer may be attached only when every
     buffered class is explicitly attachable by the ruleset;
   - if control changes team, buffered actions remain unassigned and both adjacent
     possessions carry `contested_boundary`;
   - if the period ends first, the possession is `uncertain`.
7. A period boundary always closes the current possession. No possession crosses
   half-time.
8. A missing/unresolved team on a control-establishing action makes that boundary
   uncertain. A missing player alone does not change team control but reduces player
   coverage.
9. Emit `resolved` only if every boundary is deterministic under the reviewed map.
   Emit partial possessions as `uncertain` for diagnostics, never Gold. Emit `failed`
   when ordering, taxonomy, identity, or structural integrity cannot support a
   sequence.

This algorithm deliberately prefers missing possession features to a plausible but
unsupported chain. It does not claim equivalence to a native Wyscout commercial
possession product.

## 8. Temporal Gold player-window boundary

W04 Gold is an evidence/coverage state for later W05 feature registration. It is not a
role score, representation, or retrieval result.

### 8.1 Window and row identity

Each row is player × declared window × competition/season context. W04 uses
`role_context_state=unavailable_until_w05`; it does not invent a role label.

The first implementation supports one frozen definition:

```text
window_definition_id = "wyscout-v5-domestic-season-to-date-v1"
window_start = admitted competition-season start (inclusive)
window_end = requested as-of match/date boundary (exclusive)
feature_cutoff_ts = explicit UTC instant after collection release
```

A match enters only when `match_start_utc < window_end` and every used dependency has
both `observed_at < feature_cutoff_ts` and
`available_at < feature_cutoff_ts`. The window is not a claim that the collection was
available during 2017/18.

### 8.2 `gold_player_window` schema

| Field | Type | Rule |
|---|---|---|
| `player_window_snapshot_id` | UUID string | Deterministic ID defined in Section 5 |
| `player_id`, `competition_id`, `season_id` | UUID strings | Resolved identities |
| `window_definition_id` | string | Frozen definition |
| `window_start_utc` / `window_end_utc` | UTC timestamps | Half-open observed window |
| `role_context_state` | enum | Constant `unavailable_until_w05` |
| `match_count` | `int32 >= 0` | Distinct reconciled match count |
| `resolved_lineup_stint_count` | `int32 >= 0` | Exact count |
| `minutes_lower` / `minutes_upper` | `decimal(10,3)`, nullable | Interval; null if boundaries unprovable |
| `action_count` | `int64 >= 0` | Admitted player actions |
| `coordinate_known_action_count` | `int64 >= 0` | Complete origin coordinate |
| `resolved_possession_action_count` | `int64 >= 0`, nullable | Null when match possession state is not fully resolved |
| `unresolved_action_count` | `int64 >= 0` | Explicit missing/ambiguous semantic count |
| `feature_names` | ordered list of strings | Exact order shown above from `match_count` through `unresolved_action_count` |
| `feature_schema_hash` | SHA-256 | Canonical names + order + Arrow types + semantics + missingness |
| `snapshot_as_of_ts` | UTC timestamp | Maximum admitted dependency observation |
| `available_at_watermark` | UTC timestamp | Maximum dependency availability; for source evidence, collection release |
| `valid_from_ts` | UTC timestamp | `max(snapshot_as_of_ts, available_at_watermark)` |
| `generated_at_ts` | UTC timestamp | Run metadata, never eligibility evidence |
| `feature_cutoff_ts` | UTC timestamp | Strict upper bound; must be later than release |
| `source_manifest_ids` | ordered list of UUID strings | Exact immutable sources |
| `dependency_lineage_hash` | SHA-256 | Canonical dependency evidence |
| `coverage_overall` | `float64 [0,1]` | Reviewed aggregation of named dimensions |
| `coverage_dimensions` | ordered list of structs | Identity, lineup, action, coordinate, possession, temporal |
| `missing_dimensions` | sorted list of strings | Never inferred from zero |
| `applicability_state` | enum | `research_only`, `w04_data_ready`, `suppressed` |
| `applicability_reason_codes` | sorted list of strings | Non-empty unless `w04_data_ready` |

`snapshot_as_of_ts` is not allowed to predate an admitted observation and
`valid_from_ts` cannot predate collection release. If availability is missing, the row
is `research_only` and is not written to the W05-consumable Gold manifest. A later
local acquisition timestamp may appear in the run receipt but never moves evidence
back into 2017/18.

## 9. Quality, reconciliation, and leakage gates

No weighted aggregate can waive a failed mandatory gate.

### 9.1 Source and Bronze

- Exactly seven configured source-object receipts; exact configured size and MD5;
  computed SHA-256 for each.
- All five configured match members and all five configured event members present
  exactly once. Absolute paths, parent traversal, links, duplicates, or unknown members
  prevent completion under A3.
- For every parsed member:
  `records_seen = records_admitted + records_quarantined + records_scope_excluded`.
- Object, member, record-index, quarantine, and partition-manifest digests reconcile.
- Five-partition counts are measured, never copied from the seven-competition
  publication totals.

### 9.2 Identity

- Competition, season, team, and match: `100%` of admitted references resolved; zero
  duplicate/conflicting canonical IDs.
- Every non-zero player ID referenced by admitted lineup, substitution, or event
  evidence resolves exactly once before that fact is Gold-eligible.
- Provider player zero/missing is allowed only as explicit actor missingness; it never
  becomes a canonical player and never counts as resolved coverage.
- `review_required` and `rejected_conflict` counts must be zero for Gold-consumed
  records. They remain reported even when the affected match is excluded.

### 9.3 Match, lineup, action, and possession reconciliation

- Every match has exactly two distinct resolved teams, and every event team is one of
  them.
- Event rows reconcile exactly to the admitted source event-record count per match;
  there are no duplicate action IDs or silently dropped events.
- Starting lineups contain no duplicate player. Substitution-out is on pitch,
  substitution-in is off pitch, and team membership is match-bound.
- Stints for a player/match do not overlap. Team on-pitch count never exceeds 11.
  Unknown red-card/removal semantics are not guessed; affected minute products are
  unavailable.
- Coordinate completeness is reported by event/subevent family. Values outside
  `[0,100]`, non-finite values, and structurally impossible position arrays are zero in
  Gold-eligible actions.
- Every action has zero or one possession assignment. Resolved possessions are ordered,
  non-overlapping, period-contained, and use only actions from their match.
- Gold possession fields require `100%` resolved possession derivation for every match
  contributing to that field. Partial success is missingness, not zero.

### 9.4 Temporal and missingness

- Post-cutoff observations admitted: exactly `0`.
- At/after-cutoff availability admitted: exactly `0`.
- Gold cutoffs at or before `2020-01-28T14:24:27Z`: exactly `0` eligible rows.
- Missing availability in a W05-consumable row: exactly `0`.
- Source/local acquisition/generated timestamps are separately named and never
  substituted.
- Structural keys are non-null. Semantic nulls use reason codes drawn from a frozen
  registry: `not_observed`, `not_applicable`, `unmapped`, `unresolved_identity`,
  `unresolved_boundary`, `scope_excluded`, or `source_unavailable`.
- There is no numerical imputation in W04.

### 9.5 Range and consistency

- IDs: valid domains and uniqueness at declared grain.
- Counts/minutes: non-negative; lower bound never exceeds upper bound.
- Clocks: non-negative, finite, classified period, non-decreasing within period.
- Coordinates: finite and in `[0,100]`; percentage frame retained.
- Scores: non-negative and winner/draw semantics consistent with match teams.
- Coverage: every dimension in `[0,1]`, observed count no greater than expected count.
- Rights: every derived manifest retains attribution and an effective no-external-export
  control.

## 10. Deterministic rebuild protocol

The rebuild input identity is:

```text
SHA256(canonical_json({
  source_object_sha256s_in_config_order,
  archive_member_sha256s_in_config_order,
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

The implementation:

1. Starts from empty, declared guarded working roots.
2. Verifies source receipts and manifests before reading payload.
3. Processes object kinds in the configured order and country partitions in A3 order.
4. Sorts output rows only by declared canonical primary keys; it never relies on
   filesystem enumeration, hash-map order, locale, or wall clock.
5. Uses decimal/integer clock and coordinate normalisation, canonical UTC formatting,
   sorted reason/tag/dependency lists, and fixed Parquet writer/schema options.
6. Writes immutable payloads atomically, then completion manifests.
7. Computes a semantic content digest over payload bytes. `generated_at`, host path,
   elapsed time, and run ID belong to a separate operational receipt and are excluded
   from the equality digest.
8. Repeats the complete raw-to-Gold build twice in independent empty working roots.
   Every Bronze-index, Silver-product, Gold-product, schema, count, and lineage digest
   must be identical.
9. On mismatch, writes a first-difference report with product, partition, primary key,
   column, and both digests; no accepted manifest is published.

## 11. Serial and path-disjoint implementation map

The master owns integration, dependencies, migrations, registry aliases, gate evidence,
and Git. Suggested packets are:

| Order | Packet | Exact proposed write scope | Dependency / concurrency |
|---|---|---|---|
| 1 | `W04-EVIDENCE-CONTRACT-R1` | `src/scouting/contracts/evidence.py`; `tests/contracts/test_w04_source_temporal_contract.py`; its return | Serial, second reviewer; fixes truthful availability/acquisition semantics |
| 2 | `W04-DATA-CONTRACTS-R1` | `src/scouting/contracts/data.py`; `src/scouting/contracts/__init__.py`; `tests/contracts/test_w04_data_contracts.py`; its return | Serial shared contract; after order 1 |
| 3 | `W04-ACQUISITION-R1` | `src/scouting/sources/wyscout.py`; `scripts/acquire_wyscout_v5.py`; `tests/unit/test_wyscout_acquisition.py`; its return | After contracts; no data-product files |
| 4 | `W04-BRONZE-R1` | `src/scouting/data_products/wyscout/bronze.py`; `tests/unit/test_wyscout_bronze.py`; its return | After acquisition; serial before consumers |
| 5 | `W04-IDENTITY-R1` | `src/scouting/identity/wyscout.py`; `tests/unit/test_wyscout_identity.py`; its return | After Bronze; serial identity authority |
| 6A | `W04-SILVER-ENTITY-STINT-R1` | `src/scouting/data_products/wyscout/entities.py`; `src/scouting/data_products/wyscout/lineups.py`; `tests/unit/test_wyscout_entities_lineups.py`; its return | After identity; may run parallel with 6B |
| 6B | `W04-SILVER-ACTION-R1` | `src/scouting/data_products/wyscout/actions.py`; `tests/unit/test_wyscout_actions.py`; its return | After identity; path-disjoint from 6A |
| 7 | `W04-POSSESSION-R1` | `src/scouting/data_products/wyscout/possessions.py`; `tests/unit/test_wyscout_possessions.py`; its return | After 6B and reviewed taxonomy map |
| 8 | `W04-GOLD-TEMPORAL-R1` | `src/scouting/data_products/wyscout/gold.py`; `tests/unit/test_wyscout_gold.py`; its return | After 6A, 6B, 7; serial Gold writer |
| 9 | `W04-QUALITY-R1` | `src/scouting/data_products/wyscout/quality.py`; `tests/integration/test_wyscout_rebuild.py`; its return | After all products; no writer ownership overlaps |
| 10 | `W04-INDEPENDENT-REBUILD-R1` | `tests/security/test_w04_temporal_leakage.py`; `reports/reviews/W04/wyscout-rebuild-review-R1.md`; its return | Reviewer is test/report-only and must not change implementation |

Before dispatch, the master must replace directory-level descriptions with exact
allowed files and check that no existing packet owns them. Contracts, migrations,
dependency files, manifests/registry integration, and shared `__init__.py` exports
remain serial. If accepted W03 database tables are insufficient, a master-owned,
separately reviewed migration packet is required before any agent writes migration
files; no data agent may infer that authority from this design.

## 12. Required retained evidence and stop rules

Each build retains:

- source-object and member receipts;
- Bronze admission/quarantine report;
- identity resolution and review report;
- match/action/lineup/possession reconciliation report;
- coverage/missingness/range/temporal report;
- dataset card revision with measured five-partition counts;
- two-run deterministic rebuild comparison;
- attribution and rights-policy identifiers;
- exact schema/ruleset hashes and the local accepted checkpoint.

Stop rather than improvise when:

- the acquisition/availability contract correction is not accepted;
- a configured size/MD5, expected member, source ID, or field registry fails;
- unknown archive members conflict with the strict A3 policy;
- period, substitution, event, tag, or possession semantics are unavailable;
- identity conflicts cannot be resolved without a reviewer;
- a real record lacks provable availability;
- a write would leave guarded roots;
- the work would require a new source, licence, remote service, cloud resource, public
  endpoint, external model, or broader claim.

The result of such a stop is evidence and a bounded master decision, never a guessed
data product.

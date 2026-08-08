# W04 Wyscout v5 canonical schema and deterministic rebuild design — R3

Status: **implementation design for master and independent review; not self-approved**

This document replaces R2. It is a standalone, local-only design for the accepted
Wyscout Figshare v5 acquisition, the five admitted 2017/18 domestic partitions, and
the W04 Bronze-to-Gold proof. It consumes the accepted adapter interface in
`src/scouting/sources/wyscout.py` and measured profile
`reports/phase-gates/W04/source-schema-profile.md`; it does not redefine acquisition.

The binding evidence is:

- completion manifest:
  `data/source/wyscout/v5/completion-manifest.json`, SHA-256
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- measured profile R2, SHA-256
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- completion classification `wyscout_figshare_v5_cc_by_4`, licence
  `CC-BY-4.0`, source availability `2020-01-28T14:24:27Z`, and actual local
  acquisition `2026-07-29T15:51:08.598589Z`;
- 7 direct source objects, 10 separately durable admitted members, 4
  directory-only exclusions, 7 competitions, 142 teams, 3,603 players, 1,826
  matches, and 3,071,395 event records; and
- the accepted adapter's exact physical seam: `objects/<name>`,
  `archive-members/<admitted-name>`, and `completion-manifest.json`.

No provider access, payload inspection, dependency change, migration, external
service, deployment, hosted artifact, or broader source-rights decision is requested
by this design.

## 1. Claim boundary and global invariants

The permitted claim remains a frozen historical engineering and player-evidence
proof. It is not evidence of current players, current provider continuity, women or
youth coverage, live scouting coverage, prospective recruitment benefit, or
commercial Wyscout equivalence.

The implementation invariants are:

1. Downstream code consumes only paths recorded by the accepted completion manifest.
   It never reconstructs source-object/member paths from IDs or names.
2. `matches.zip` and `events.zip` are immutable acquisition evidence but are not
   opened downstream. Bronze reads their separately durable admitted members.
3. The four excluded members have no payload path and are never opened, copied,
   hashed as payloads, parsed, quarantined, counted as records, or transformed.
4. Provider record `id` is event-record identity; `eventId` is taxonomy identity.
   Names are display evidence and never identity or semantic matching keys.
5. JSON decimal values are parsed as `Decimal`; binary float is forbidden at source
   admission and transformation boundaries.
6. Unknown fields, periods, ID shapes, coordinate shapes, semantic mappings, terminal
   evidence, and authority versions fail closed. There is no best-effort coercion.
7. Semantic products contain no run clock, run ID, host path, elapsed runtime, or
   mutable receipt metadata.
8. Rights, identity, strict-cutoff, lineage, partition, and reconciliation failures
   cannot be waived by coverage or an average score.
9. W04 provides evidence and applicability, not a scouting score or recruitment
   decision.

## 2. Exact completion-declared source seam

The source root is exactly `data/source/wyscout/v5`. The completion document is read
first, checked against the accepted completion digest, parsed with strict keys, and
then used as the only path authority.

### 2.1 Direct source objects

| Logical path from `object_path` | Bytes | SHA-256 | Downstream payload access |
| --- | ---: | --- | --- |
| `objects/competitions.json` | 1,209 | `39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1` | read |
| `objects/teams.json` | 27,404 | `9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d` | read |
| `objects/players.json` | 1,737,347 | `877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e` | read |
| `objects/matches.zip` | 645,097 | `c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9` | never opened downstream |
| `objects/events.zip` | 77,323,413 | `877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45` | never opened downstream |
| `objects/eventid2name.csv` | 1,001 | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` | read |
| `objects/tags2name.csv` | 1,754 | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` | read |

### 2.2 Separately durable admitted members

| Logical path from `member_path` | Rows | Bytes | SHA-256 |
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

The parser performs normalised relative-path and beneath-root checks, then verifies
the declared size and SHA-256 while streaming the file. It requires all five match
members and all five event members. For each country suffix, distinct event
`matchId` must exactly equal match `wyId`; the accepted evidence is
England 380, France 380, Germany 306, Italy 380, and Spain 380.

The obsolete R2 layouts `objects/<file_id>/<name>` and
`members/<archive_file_id>/<name>` are prohibited. Layer manifests may have derived
paths, but a layer reader never uses those paths to infer a source path.

## 3. Non-circular completion-to-strict-manifest bridge

The provider completion document and strict `SourceSnapshotManifest` have different
jobs. The completion document is acquisition evidence. A single serial admission step
creates the strict cross-boundary artifact consumed by Bronze and every later layer.

### 3.1 Explicit bridge inputs

The admission step requires:

- accepted completion bytes and their SHA-256;
- an explicit immutable `TenantContext` supplied by the master-owned packet
  (`tenant_id` required, `club_id` nullable but fixed);
- bridge version `w04-wyscout-manifest-bridge-v1`;
- the accepted field-registry digest described in Section 6; and
- the accepted profile digest above for declared row-count evidence.

Missing tenant context is a stop, not a default tenant. The operational request trace
is not placed into semantic bytes.

### 3.2 IDs without self-reference

Canonical JSON means UTF-8, sorted keys, no insignificant whitespace, canonical UUID
text, canonical UTC text, and integers without coercion.

```text
manifest_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source-snapshot-manifest:wyscout:v1")

manifest_identity_input = canonical_json({
  bridge_version,
  completion_sha256,
  source_id,
  tenant_id,
  club_id
})

manifest_id =
  UUIDv5(manifest_namespace, SHA256(manifest_identity_input))

trace_id =
  UUIDv5(manifest_id, "semantic-manifest-trace:w04-wyscout:v1")
```

Neither UUID depends on strict-manifest bytes containing that UUID, so there is no
cycle. Re-admitting the same completion for the same tenant context produces the same
strict bytes. A real execution trace belongs only to the operational receipt.

### 3.3 Exact strict contract population

`SourceSnapshotManifest` is populated as follows:

| Contract field | Exact rule |
| --- | --- |
| `schema_version` | `1` |
| `manifest_id` | UUIDv5 rule above |
| `tenant_context` | exact master-supplied immutable context |
| `trace_id` | deterministic semantic trace above |
| `provider` | completion `provider` (`Wyscout`) |
| `provider_schema_version` | `figshare-v5+completion-v1+bridge-v1` |
| `classification.use_class` | `restricted`, reflecting the stricter local project control |
| `classification.derived_data_allowed` | `true` |
| `classification.internal_review_allowed` | `true` |
| `classification.export_allowed` | `false` |
| `classification.attribution_required` | `true` |
| `classification.attribution_text` | exact completion licence attribution text |
| `acquired_at` | exact completion acquisition time |
| `available_at` | exact completion source availability |
| `files` | ordered evidence below |
| `coverage` | exact admission coverage below |

`files` is ordered as: completion document, seven object records in completion order,
then ten admitted members in completion order. The completion document is represented
as `SourceFileDigest(object_path="completion-manifest.json",
sha256=<accepted digest>, size_bytes=<measured>, row_count=null)`. Each other row uses
the completion-declared path, size, and digest. Row counts are 7 competitions, 142
teams, 3,603 players, 36 event-map rows, 59 tag-map rows, the ten counts in Section
2.2, and null for the two ZIP objects. Excluded entries are coverage evidence, not
`files`, because they have no admitted path or payload digest.

Strict-manifest admission coverage has these six dimensions:

| Dimension | Numerator | Denominator | Accepted value |
| --- | ---: | ---: | ---: |
| `source_object_integrity` | verified completion object rows | 7 | 7/7 |
| `admitted_member_integrity` | streamed size/digest-valid members | 10 | 10/10 |
| `match_partition_presence` | non-empty admitted match partitions | 5 | 5/5 |
| `event_partition_presence` | non-empty admitted event partitions | 5 | 5/5 |
| `partition_match_id_alignment` | exact-equal country match-ID sets | 5 | 5/5 |
| `scope_exclusion_directory_only` | declared exclusions with no payload path/read | 4 | 4/4 |

For this strict manifest, dimension coverage is `numerator / denominator`,
zero denominator is invalid, `overall=min(dimension coverage)`, and
`missing_dimensions` is the sorted set of dimensions below 1. Admission requires
overall 1 and no missing dimension.

### 3.4 One downstream authority artifact

The only source-authority artifact read by Bronze is:

```text
data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json
```

It contains canonical `SourceSnapshotManifest` JSON. An existing path is idempotent
only when bytes match. Its SHA-256 is computed after serialization and returned by the
admission step; it is not embedded into bytes that determine `manifest_id`.

Bronze receives `(manifest_id, strict_manifest_sha256)` and verifies the artifact,
then verifies the listed completion document. Later layer manifests record the strict
manifest ID and digest plus their immediate parent-layer digest:

```text
data/manifests/wyscout/v5/bronze/<build_id>.manifest.json
data/manifests/wyscout/v5/silver/<build_id>.manifest.json
data/manifests/wyscout/v5/gold/<build_id>.manifest.json
```

Those layer manifests never replace, mutate, or become inputs to the source manifest.

## 4. Exact event clock and conservative cutoff

The profile proves only `1H` and `2H`, 1,541,033 and 1,530,362 events respectively.
`eventSec` is exact JSON decimal evidence with maximum scale 18. It does not provide a
second-half period-start UTC, a half-time duration, or a terminal.

The adapter validates a configured descriptive phrase about match/period/eventSec,
but emits no transformed event UTC. That phrase is not sufficient timestamp evidence.
This R3 action contract is the downstream authority and deliberately narrows the
representation to period-relative evidence.

### 4.1 `silver_action` clock fields

| Field | Type | Rule |
| --- | --- | --- |
| `period_code` | enum | only reviewed `1H`, `2H`; anything else quarantines the action and fails its partition |
| `period_rank` | `int8` | `1H=1`, `2H=2`, ordering only |
| `period_elapsed_seconds` | `decimal128(22,18)` | exact non-negative `eventSec`, padded to scale 18 without rounding |
| `period_elapsed_source_scale` | `int8` | exact lexical scale `0..18` |
| `occurrence_precision` | enum | constant `period_relative` |
| `period_start_utc` | UTC timestamp nullable | null in W04 |
| `event_observed_at` | UTC timestamp nullable | null in W04 |
| `event_cutoff_proof` | enum | `snapshot_available_before_cutoff` or `ineligible` |

There is no `match_elapsed_us` and no `match_start + 2,700 seconds` UTC. Cross-period
order is:

```text
(period_rank, period_elapsed_seconds, source_record_ordinal,
 source_event_record_id)
```

This produces deterministic 1H-before-2H order without asserting the duration between
periods. Within-period equal times use original ordinal then unique event record `id`.

### 4.2 Strict cutoff

Individual occurrence UTC is not needed to prove knowability. Every action is inside
the immutable snapshot whose upstream availability is exact. An action may contribute
only when all are true:

1. its event member and parent match are admitted by the strict manifest;
2. its parent match `match_start_utc < feature_cutoff_ts`;
3. strict-manifest `available_at < feature_cutoff_ts`;
4. every identity/taxonomy/schema dependency used is available strictly before the
   cutoff; and
5. the whole match is selected by the Gold match-start window rule, not by fabricated
   action UTC.

The source-manifest `EvidenceDependency` uses the snapshot availability instant as
its conservative `observed_at` and `available_at`: that is the exact instant at which
the complete frozen snapshot is evidenced upstream. Thus cutoff equality and any
cutoff at or before `2020-01-28T14:24:27Z` reject every W04 action. Acquisition and
generation clocks are never substituted.

Gold windows are explicitly **match-start windows**:
`window_start_utc <= match_start_utc < window_end_utc`. Actions inherit selection
only from their reconciled parent match. The product makes no within-match as-of
claim. A caller asking for a partial-match or action-instant cutoff receives
`unsupported_period_relative_occurrence`, not a partial action set.

Required clock challenges are:

- equal `eventSec` in 1H and 2H orders by period rank without UTC synthesis;
- late 1H `eventSec` still orders before early 2H;
- scale-18 decimals round-trip exactly;
- unknown period and non-finite/negative decimal fail;
- cutoff equal to release fails, cutoff after release passes only with all other
  dependencies strict-before; and
- no serialized field contains an inferred second-half UTC or half-time duration.

## 5. Semantic products and canonical identities

Canonical entity UUIDs retain the R2 algorithm:

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
kind_namespace = UUIDv5(source_namespace, "<kind>")
canonical_id =
  UUIDv5(kind_namespace, "figshare-v5:<canonical-decimal-source-id>")
```

Valid unique IDs map deterministically within one entity kind. Player ID zero remains
an unidentified actor, not a player. Non-zero references absent from admitted master
evidence enter review/quarantine; names and current-team attributes cannot repair
them. Corrections require new immutable identity-evidence versions.

All semantic Bronze, Silver, and Gold rows include schema/ruleset versions, tenant,
strict `source_manifest_id`, source record/member digests, identity evidence digests,
dependency lineage digest, source availability, and rights policy. They contain no
run-clock field.

## 6. Serial master-owned semantic authorities

Source structure does not prove field meaning or possession meaning. Two authority
packets must execute serially under the master before transformation packets.

### 6.1 Field-registry authority

Packet `W04-FIELD-REGISTRY-AUTHORITY-01-R1` owns only:

```text
configs/schema/wyscout-v5-field-registry-v1.yaml
tests/contracts/test_wyscout_field_registry_authority.py
reports/reviews/W04/wyscout-field-registry-authority-R1.md
reports/reviews/W04/returns/W04-FIELD-REGISTRY-AUTHORITY-01-R1.md
```

The artifact ID is `w04-wyscout-field-registry-v1`. Its top-level strict schema is:

```text
schema_version: 1
registry_id: w04-wyscout-field-registry-v1
source_id: wyscout-soccer-match-events-figshare-v5
completion_sha256: <accepted completion digest>
profile_sha256: <accepted R2 profile digest>
record_kinds:
  <kind>:
    source_paths: [exact completion-declared logical paths]
    required_fields: [sorted JSON paths]
    optional_fields: [sorted JSON paths]
    fields:
      <json_path>:
        observed_types: [sorted profile types]
        mode: transform | preserve_not_transformed | forbidden
        canonical_field: <string or null>
        nullable: <boolean>
        value_authority: structural | reviewed_semantic | none
        invalid_policy: quarantine_record | preserve_unmapped
unknown_field_policy: quarantine_record
unknown_record_kind_policy: reject_partition
canonicalization: project_canonical_json_v1
```

The registry digest is SHA-256 of canonical JSON obtained from the parsed YAML,
excluding no fields and containing no self-digest. The independent review records
that digest. The loader rejects unknown keys, duplicate paths, stale completion or
profile digests, observed-type mismatches, and any transform without
`reviewed_semantic` authority.

Required fabricated challenges cover every record kind plus: unknown top-level and
nested fields; missing required fields; nullable `currentTeamId`; mixed integer/string
area IDs; scale-18 `eventSec`; string `subEventId` preserved as unmapped rather than
coerced; one/two-position arrays; -1 and 101 coordinate anomalies; array
substitutions; literal string `"null"` substitutions; missing IDs; bool-as-int; and a
conflicting duplicate ID.

The authority review must explicitly decide the six literal `"null"` containers and
all field-to-canonical mappings. Until accepted, they remain preserved unmapped
evidence, not assumed empty arrays.

### 6.2 Possession-taxonomy authority

After the field registry, packet `W04-POSSESSION-TAXONOMY-AUTHORITY-01-R1` owns only:

```text
configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml
tests/contracts/test_wyscout_possession_taxonomy_authority.py
reports/reviews/W04/wyscout-possession-taxonomy-authority-R1.md
reports/reviews/W04/returns/W04-POSSESSION-TAXONOMY-AUTHORITY-01-R1.md
```

Artifact ID is `w04-wyscout-possession-taxonomy-v1`. It binds the completion,
profile, field-registry, event-map, and tag-map digests. Its strict schema is:

```text
schema_version: 1
taxonomy_id: w04-wyscout-possession-taxonomy-v1
source_id: <exact source ID>
bound_digests: {completion, profile, field_registry, event_map, tag_map}
classes: [CONTROL, CONTESTED, DEAD_BALL, RESTART, NON_CONTROL_ADMIN]
mappings:
  - event_id: int
    subevent_id: int | null
    required_tag_ids: [sorted int]
    forbidden_tag_ids: [sorted int]
    class: <exact class>
    control_team_source: action_team | opposing_team | none
    opens_control: bool
    closes_control: bool
    dead_ball_attachment: prior | next | neither
    contested_attachment: same_team_next | never
unknown_combination_policy: UNMAPPED
unknown_name_matching: forbidden
period_boundary_policy: close
simultaneous_cross_team_policy: uncertain_boundary
canonicalization: project_canonical_json_v1
```

Mappings must enumerate every reviewed event/subevent/tag predicate needed by the
admitted data. No label substring or implicit football convention is allowed.
Overlapping predicates, non-exhaustive reviewed combinations, stale lookup digests,
or unmapped actions required by a claimed resolved possession fail review.

Synthetic cases cover same-team continuation, opposing control, restart, dead ball
attached prior/next/neither, contested buffer resolution and non-resolution,
cross-team equal-clock actions, missing team, zero player, unknown mapping, and period
boundary. The taxonomy digest is SHA-256 of complete canonical parsed YAML; it is a
mandatory semantic build input.

## 7. Bronze and Silver products

### 7.1 Bronze record index

Bronze streams the five readable direct objects and ten admitted members named by the
strict manifest. Grain is `(source_file_sha256, record_ordinal)`. It records:

```text
tenant_id, source_manifest_id, source_file_path, source_file_sha256,
source_record_kind, source_record_id, record_ordinal, raw_record_sha256,
raw_field_paths, parser_version, field_registry_digest, admission_state,
reason_codes, source_available_at, rights_policy_id
```

`raw_record_sha256` is the canonical JSON value or canonical CSV row digest. Event
record identity is the unique `id`; `eventId` remains a taxonomy field. Quarantine
counts reconcile with records seen. Excluded members never create a Bronze row.

### 7.2 `silver_match`

Grain is one admitted match, keyed by deterministic `match_id`. Required fields are
source match ID, competition/season, two distinct match-bound team IDs,
`match_start_utc` from exact `dateutc`, preserved provider status and duration
category, member/record lineage, and reconciliation state. All 1,826 dates must
round-trip as `YYYY-MM-DD HH:MM:SS`; all measured durations are preserved as
`Regular`, without assigning 90 minutes or a terminal.

### 7.3 `silver_action`

Grain is one event record, keyed by unique provider record `id`. Required fields are:

```text
action_id, source_event_record_id, match_id, team_id, player_id nullable,
source_event_type_id, source_subevent_type_id nullable,
raw_subevent_id_type, period fields from Section 4,
position_0_x, position_0_y, position_1_x, position_1_y,
position_cardinality, coordinate_validation_state,
sorted_tag_ids, semantic_class nullable, semantic_state,
source_record_ordinal, source/member lineage, possession_eligible
```

Position indexes preserve source array order; they are not renamed origin/destination
until a reviewed registry grants that meaning. Valid coordinates are integers in
inclusive 0..100. The measured x=-1 and two y=101 values remain in Silver with
`coordinate_validation_state=out_of_range`, never clamped or Gold-coordinate
eligible. The 7,821 string subevent IDs remain type evidence and semantic-unmapped;
they are not parsed as integers.

Every one of 3,071,395 event IDs is unique; all match IDs resolve; every event team
belongs to its referenced match; and the member partition matches the match member.
Any implementation exception fails the affected partition.

### 7.4 `silver_lineup_stint`

Grain is player × match × continuous provider-nominal interval. It carries
match-bound team, player, start/end nominal-minute interval, boundary source,
substitution ordinal, derivation state, and exact match/member lineage. Section 8
freezes interval and suppression rules.

### 7.5 `silver_possession`

Grain is one contiguous, taxonomy-resolved control sequence within one match and
period. Its deterministic ID is UUIDv5 of match, taxonomy digest, possession ruleset,
period, and ordinal. It carries team, first/last action, action count, assignment
states, boundary reason, taxonomy digest, and lineage. Possessions never cross
periods. An action has zero or one possession assignment.

Possession implementation is forbidden until Section 6.2 is accepted. `UNMAPPED`,
cross-team simultaneous, missing-team, and unresolved contested boundaries produce
uncertain/unassigned evidence, not guessed control.

### 7.6 Blueprint-required `silver_player_match_fact`

The logical grain is exactly one resolved player × admitted match:

```text
(tenant_id, source_manifest_id, match_id, player_id,
 player_match_fact_schema_version)
```

Team is a required match-bound attribute. A player linked to two teams in one match is
a conflict, not two facts.

| Field family | Required fields and rules |
| --- | --- |
| Identity | deterministic `player_match_fact_id`, `player_id`, `match_id`, `team_id`, `competition_id`, `season_id` |
| Context | `team_context_state=match_bound`, provider side preserved, starting/bench/substitution/event-presence flags, no current-team field |
| Result-independent facts | action count, valid-coordinate action count, unresolved action count, possession-assigned action count nullable, lineup/stint counts; no score, winner, result, points, or outcome-derived feature |
| Minutes | nominal interval fields and states from Section 8; elapsed minute fields null in W04; `per90_eligible=false` |
| Coverage | six numerator/denominator/state structs from Section 10 plus applicability |
| Temporal | match start, source availability, strict cutoff state, period-relative action state |
| Lineage | strict manifest ID/digest, match/member/raw-record digests, ordered contributing action digest aggregate, identity evidence, registry/taxonomy/ruleset versions, dependency lineage hash |

Candidate pairs are the union of resolved non-zero player references in starting
lineup, bench, substitutions, and events. Zero event player IDs remain actor-missing
actions and do not create facts. The measured 23 unmapped bench references and 8
unmapped substitution-in references are retained in reconciliation/quarantine and
cannot be repaired by name.

Reconciliation is exact:

1. every resolved candidate pair produces exactly one fact;
2. every non-zero player-attributed event maps to exactly one fact for the same match
   and team;
3. summed fact action counts equal non-zero attributed admitted actions;
4. every resolved lineup/stint reference maps to exactly one fact;
5. no fact exists for an excluded member, unresolved identity, or cross-team conflict;
6. source-to-fact rejects and zero actors reconcile separately; and
7. reruns sort facts by `(match_id, player_id)` and produce identical lineage and
   semantic digests.

The measured 50,522 distinct non-zero event player-match pairs are an input
reconciliation count, not an assertion that all have valid minutes or lineup context.

## 8. Frozen nominal, elapsed, stoppage, terminal, and minute rules

The source profile explicitly reports exact terminal unsupported, exact player
minutes unsupported, and per-90 denominator unsupported.

### 8.1 Time meanings

- `period_elapsed_seconds` is exact provider period-relative clock evidence.
- `provider_substitution_minute` is an integer nominal match-minute label.
- `nominal time` is a provider label coordinate, not UTC elapsed time.
- `elapsed time` requires period-start/terminal evidence and is unavailable in W04.
- eventSec beyond 2,700 seconds is retained as period-relative stoppage evidence; it
  is not used to shift the next period or create a terminal.
- provider duration category `Regular` is descriptive only. It does not prove 90
  elapsed minutes, a 45-minute period, or an end instant.
- maximum event time is a lower-bound event observation within a period, never a
  terminal.

### 8.2 Nominal substitution intervals

For substitution minute integer `m`, the boundary is the half-open nominal interval
`[m, m+1)` minutes. Starting lineup begins at nominal 0. A substitution-in starts and
substitution-out ends in the same interval; equal-minute substitutions share a
simultaneous group and source ordinal is retained.

For calculation, a starting boundary has `min=max=0`; a substitution boundary has
`min=m` and exclusive supremum `max=m+1`.

For a stint with both start interval `[s0,s1)` and end interval `[e0,e1)`:

```text
nominal_duration_lower = max(0, e0 - s1)
nominal_duration_upper = max(0, e1 - s0)
```

Intervals with end definitely before start, incoming-already-active,
outgoing-not-active, duplicate starters, or two match teams for one player fail.
Bench-only evidence does not create an on-pitch stint.

### 8.3 Terminal and suppression

No accepted W04 field is terminal authority. Therefore:

- a stint not closed by a substitution has
  `terminal_state=unsupported_source_evidence`;
- its nominal duration upper bound is null and it is right-censored;
- no nominal interval is relabelled as elapsed minutes;
- `elapsed_minutes_lower` and `elapsed_minutes_upper` are null for all W04
  `player_match_fact` rows;
- no exact `minutes_played` is emitted; and
- every minutes-denominated or per-90 feature has state
  `suppressed_unsupported_denominator`.

Closed nominal stints may retain nominal lower/upper diagnostic intervals, but they
do not authorise per-90. A future terminal authority must be a new versioned,
master-reviewed input and rebuild; last event, `Regular`, 90, and maximum substitution
minute are explicitly forbidden substitutes.

Reconciliation reports counts of closed, right-censored, invalid, and no-stint facts;
it never sums null elapsed minutes into zero.

## 9. Possession derivation after authority

Actions order by Section 4. The accepted taxonomy, not names, supplies control class.
Within each match and period:

1. reviewed `CONTROL` or `RESTART` opens control for its mapped team;
2. same-team control continues;
3. opposing resolved control closes the prior sequence and opens another;
4. `DEAD_BALL` closes and attaches only as the taxonomy row says;
5. `CONTESTED` buffers and attaches only under its exact reviewed rule;
6. cross-team equal clocks mark an uncertain boundary;
7. unknown mapping or missing team remains unassigned;
8. period end closes the sequence; nothing crosses periods; and
9. only fully deterministic sequences are `resolved` and Gold eligible.

The product is a project-derived W04 taxonomy result, not a provider-native
possession claim.

## 10. Exact coverage equations and applicability

Coverage is computed per `gold_player_window` over its selected
`silver_player_match_fact` rows. Every dimension stores integer `numerator`,
`denominator`, decimal coverage, state, and sorted reason codes. Counts, not rounded
floats, are the authority.

| Dimension | Denominator `D` | Numerator `N` |
| --- | --- | --- |
| `identity` | all non-zero player reference occurrences in contributing lineup, bench, substitution, and event evidence | references resolved exactly once to the row player and correct match team |
| `lineup` | selected player-match candidate facts | facts with structurally reconciled formation membership/stint state, including explicit event-only/no-lineup state |
| `action` | admitted non-zero-player actions for the row player in selected matches | actions assigned exactly once to the correct player-match fact and team |
| `coordinate` | row actions for which the field registry marks positions applicable | applicable actions with allowed cardinality, all required axes present, numeric, and within inclusive 0..100 |
| `possession` | row actions the accepted taxonomy marks possession eligible | eligible actions assigned to exactly one resolved possession |
| `temporal` | strict source/identity/registry/taxonomy dependencies plus selected match/action dependency groups | dependencies with exact availability strictly before cutoff, matches starting before cutoff, and actions carrying snapshot-before-cutoff proof |

For a dimension:

```text
if D > 0: coverage = N / D
if D = 0 and dimension in {coordinate, possession}
   and the accepted registry/taxonomy proves no applicable evidence:
       coverage = 1, state = not_applicable_zero_denominator
otherwise if D = 0:
       coverage = 0, state = missing_zero_denominator
```

`N > D` is a hard reconciliation failure. With `D>0`, state is `complete` when
`N=D`, otherwise `partial`. `missing_dimensions` is the lexically sorted set of
dimensions in `partial`, `missing_zero_denominator`, `authority_missing`, or
`failed`. `not_applicable_zero_denominator` is not missing only for the two optional
dimensions and only with accepted authority.

```text
coverage_overall = minimum of the six dimension coverage values
```

There is no weighting or waiver.

### 10.1 Applicability decision table

Evaluate rows top to bottom:

| Condition | Applicability | Required reason |
| --- | --- | --- |
| prohibited/unknown rights, invalid strict manifest, unaccepted registry/taxonomy, partition mismatch, duplicate event identity, match/team conflict, identity conflict, lineage mismatch, or source/authority availability at-or-after cutoff | `suppressed` | exact hard-failure code |
| any mandatory identity/action/temporal denominator is zero, `N>D`, required dependency absent, or result requests minutes/per-90 | `suppressed` | `mandatory_coverage_or_denominator_failure` or `unsupported_minutes_denominator` |
| hard gates pass but any dimension is partial/missing, any player-match fact is right-censored/uncertain, or coordinate/possession evidence is incomplete | `research_only` | sorted incomplete dimensions/states |
| hard gates pass; every dimension is complete or authority-proven optional not-applicable; overall=1; missing dimensions empty | `w04_data_ready` for supported count/evidence features only | empty |

`w04_data_ready` never enables per-90 in W04. A request for an unsupported feature is
suppressed even when the row is otherwise data ready.

Build manifests also aggregate every numerator/denominator by partition and require
their sums to equal row-level totals.

## 11. Gold grain with neutral versioned role context

W04 emits one neutral, unscored role context:

```text
role_context_namespace =
  UUIDv5(NAMESPACE_URL, "urn:scouting-intelligence:role-context")
role_context_version = "w04-neutral-role-context-v1"
role_context_id =
  UUIDv5(role_context_namespace, "w04:neutral-unscoped:version:1")
role_context_state = "neutral_unscoped"
```

The exact `gold_player_window` uniqueness key is:

```text
(tenant_id, player_id, competition_id, season_id,
 role_context_id, role_context_version,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, dependency_lineage_hash)
```

The deterministic snapshot UUID covers the same ordered tuple. Required fields are
neutral role context, match count, action counts, coordinate/possession counts,
unresolved counts, the six coverage structs, applicability, strict temporal
evidence, source/feature/authority lineage, and supported-feature schema digest.
Minutes and per-90 fields carry the explicit suppressed state from Section 8, not
zeros.

W05 never mutates or silently rekeys the neutral row. It creates a new feature-schema
version with reviewed role-context IDs and either emits role-specific rows referencing
the neutral W04 lineage or supersedes them through an explicit versioned manifest.
Neutral and role-specific rows cannot collide.

## 12. Deterministic semantic identity and truthful operational receipts

### 12.1 Stable `build_id`

The build identity input is canonical JSON:

```text
{
  build_identity_version: "w04-wyscout-build-id-v1",
  tenant_context,
  completion_sha256,
  strict_manifest_id,
  strict_manifest_sha256,
  field_registry_id,
  field_registry_sha256,
  possession_taxonomy_id,
  possession_taxonomy_sha256,
  identity_ruleset_version,
  action_ruleset_version,
  lineup_ruleset_version,
  possession_ruleset_version,
  player_match_fact_schema_version,
  gold_schema_version,
  neutral_role_context_id,
  neutral_role_context_version,
  window_definition,
  feature_cutoff_ts,
  code_checkpoint
}
build_id = SHA256(canonical_json(input))
```

`code_checkpoint` is an immutable local checkpoint identifier supplied by the master;
implementation subagents neither discover nor change it. Build ID contains no run
clock, host, output root, random ID, or operational trace.

Semantic artifacts live under
`data/working/wyscout/v5/<layer>/<build_id>/<product>/`. Layer completion manifests
are written last and contain no run clocks.

### 12.2 Semantic and physical comparisons

Rows use fixed Arrow schemas, canonical UUID/UTC/decimal values, sorted list fields,
canonical nulls, primary-key row order, fixed partition order, and no generated
timestamp. The semantic digest is SHA-256 over:

```text
canonical schema descriptor
+ length-prefixed canonical row bytes in primary-key order
+ ordered parent/authority digests
```

Parquet uses exactly one `part-00000.parquet` per logical product partition, primary
key row order, and these locked options:

```text
format_version = "2.6"
row_group_size = 65536
compression = "zstd"
compression_level = 9
data_page_version = "2.0"
use_dictionary = false
write_statistics = true
write_page_index = false
use_byte_stream_split = false
coerce_timestamps = "us"
allow_truncated_timestamps = false
store_schema = true
```

Schema metadata is a lexically ordered map containing only schema/ruleset/authority
IDs and digests. The locked PyArrow version is recorded in the operational receipt,
not semantic metadata. Host paths and run metadata are absent. The physical digest is
SHA-256 of exact file bytes.

Two empty-root builds with the same build ID must have:

- equal row counts, schemas, partition manifests, lineage, and semantic digests; and
- equal physical file paths relative to the build root and equal file-byte digests.

Semantic mismatch is a data/rule failure. Semantic equality with physical inequality
is a writer-determinism failure. Neither is accepted.

Each execution separately writes a truthful operational receipt:

```text
runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json
```

Receipt fields are random `run_id`, operational `trace_id`, `started_at`,
`completed_at`, elapsed duration, local runtime/writer versions, requested root,
result state, build ID, and ordered semantic/physical digests. Receipt clocks must be
truthful and may differ. Receipts are excluded from semantic and physical product
comparisons and cannot alter build ID.

## 13. Quality and reconciliation gates

An accepted build requires:

- strict completion/manifest bridge reconciliation and exact 17 file rows;
- 7/142/3,603 direct records and exact ten member counts;
- 1,826 unique matches, 3,071,395 unique events, and zero event duplicates;
- five admitted competition IDs, 98 admitted team IDs, and five exact partition ID
  equalities;
- two teams per match, teamsData key/team equality, event match/team membership, and
  event-member partition exceptions all zero;
- 226,038 zero player actions separate, non-zero player misses zero, and
  player-match/event reconciliation exact;
- 40,172 lineup, 28,715 bench, and 10,423 substitution rows reconciled; the 23 bench
  and 8 substitution-in absent-master references remain explicit;
- only 1H/2H, exact Decimal scale at most 18, and no fabricated UTC;
- 709 one-position and 3,070,686 two-position arrays, with all three anomalies
  retained and excluded from valid-coordinate numerators;
- registry and taxonomy digests accepted before use;
- no result-derived player-match fact; no score/winner leakage into features;
- exact coverage equations and applicability state;
- W04 elapsed minutes/per-90 emitted exactly zero times;
- attribution and restricted local-only control inherited by every manifest; and
- two-root semantic and physical rebuild equality.

Any source count change is not silently compared to these accepted constants: it
requires a new completion/profile/authority version.

## 14. Serial and path-disjoint implementation packets

The master owns authority, shared contracts, integration, any migration, and review.
No migration is proposed: guarded Parquet/manifests satisfy W04. If a migration later
becomes necessary, work stops and a separate master-owned, serial, second-reviewed
packet must precede all consumers.

| Order | Packet | Exact write scope | Dependency/concurrency |
| ---: | --- | --- | --- |
| 1 | `W04-FIELD-REGISTRY-AUTHORITY-01-R1` | four paths in Section 6.1 | Master-owned serial authority |
| 2 | `W04-POSSESSION-TAXONOMY-AUTHORITY-01-R1` | four paths in Section 6.2 | Master-owned serial after 1 |
| 3 | `W04-DATA-CONTRACTS-01-R1` | `src/scouting/contracts/wyscout_data.py`; `tests/contracts/test_wyscout_data_contracts.py`; `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R1.md` | Shared contract, master-owned serial after 2 |
| 4 | `W04-MANIFEST-BRIDGE-01-R1` | `src/scouting/data_products/wyscout/manifest_bridge.py`; `tests/unit/test_wyscout_manifest_bridge.py`; `reports/reviews/W04/returns/W04-MANIFEST-BRIDGE-01-R1.md` | After 3; sole strict-manifest writer |
| 5 | `W04-BRONZE-01-R1` | `src/scouting/data_products/wyscout/bronze.py`; `tests/unit/test_wyscout_bronze.py`; `reports/reviews/W04/returns/W04-BRONZE-01-R1.md` | After 4 |
| 6 | `W04-IDENTITY-01-R1` | `src/scouting/identity/wyscout.py`; `tests/unit/test_wyscout_identity.py`; `reports/reviews/W04/returns/W04-IDENTITY-01-R1.md` | Serial identity authority after 5 |
| 7A | `W04-SILVER-MATCH-ENTITY-01-R1` | `src/scouting/data_products/wyscout/entities.py`; `tests/unit/test_wyscout_entities.py`; `reports/reviews/W04/returns/W04-SILVER-MATCH-ENTITY-01-R1.md` | After 6; path-disjoint with 7B/7C |
| 7B | `W04-SILVER-ACTION-01-R1` | `src/scouting/data_products/wyscout/actions.py`; `tests/unit/test_wyscout_actions.py`; `reports/reviews/W04/returns/W04-SILVER-ACTION-01-R1.md` | After 6; path-disjoint with 7A/7C |
| 7C | `W04-SILVER-LINEUP-01-R1` | `src/scouting/data_products/wyscout/lineups.py`; `tests/unit/test_wyscout_lineups.py`; `reports/reviews/W04/returns/W04-SILVER-LINEUP-01-R1.md` | After 6; path-disjoint with 7A/7B |
| 8 | `W04-POSSESSION-01-R1` | `src/scouting/data_products/wyscout/possessions.py`; `tests/unit/test_wyscout_possessions.py`; `reports/reviews/W04/returns/W04-POSSESSION-01-R1.md` | After 7B and accepted taxonomy; serial before facts |
| 9 | `W04-PLAYER-MATCH-FACT-01-R1` | `src/scouting/data_products/wyscout/player_match.py`; `tests/unit/test_wyscout_player_match.py`; `reports/reviews/W04/returns/W04-PLAYER-MATCH-FACT-01-R1.md` | After 7A/7B/7C/8 |
| 10 | `W04-GOLD-TEMPORAL-01-R1` | `src/scouting/data_products/wyscout/gold.py`; `tests/unit/test_wyscout_gold.py`; `reports/reviews/W04/returns/W04-GOLD-TEMPORAL-01-R1.md` | After 9; sole Gold writer |
| 11 | `W04-QUALITY-REBUILD-01-R1` | `src/scouting/data_products/wyscout/quality.py`; `tests/integration/test_wyscout_rebuild.py`; `reports/reviews/W04/returns/W04-QUALITY-REBUILD-01-R1.md` | After 10 |
| 12 | `W04-INDEPENDENT-REBUILD-REVIEW-01-R1` | `tests/security/test_w04_temporal_leakage.py`; `reports/reviews/W04/wyscout-rebuild-review-R1.md`; `reports/reviews/W04/returns/W04-INDEPENDENT-REBUILD-REVIEW-01-R1.md` | Independent test/report only after 11 |

Every path above is unique to its packet. Registry exports or shared `__init__.py`
changes, if needed, belong to one separate
master-owned serial integration packet; no implementation packet may opportunistically
edit them. Packets 7A–7C are the only planned parallel work.

## 15. Nine-finding closure

1. **`W04-DESIGN-EVENT-CLOCK-01` closed:** exact scale-18 period-relative decimal,
   deterministic period ordering, null event UTC, and snapshot-availability strict
   cutoff replace fabricated 2H UTC.
2. **`W04-DESIGN-SOURCE-SEAM-01` closed:** all source reads use the exact completion
   `object_path`/`member_path` values listed in Section 2.
3. **`W04-DESIGN-MANIFEST-BRIDGE-01` closed:** one serial non-circular UUIDv5 bridge
   supplies tenant, semantic trace, classification, 18 file evidences, coverage, and
   one strict downstream artifact.
4. **`W04-DESIGN-REBUILD-CLOCK-01` closed:** stable build ID and clock-free semantic
   rows are separate from truthful per-run receipts; semantic and physical comparisons
   are both exact.
5. **`W04-DESIGN-POSSESSION-AUTHORITY-01` closed:** serial master-owned field-registry
   and possession-taxonomy packets freeze paths, schemas, versions, digest rules,
   unknown behavior, and synthetic cases before transformation.
6. **`W04-DESIGN-GOLD-GRAIN-01` closed:** a deterministic versioned neutral role
   context is part of the Gold logical key and W05 expansion cannot overwrite it.
7. **`W04-DESIGN-MINUTES-01` closed:** nominal intervals are explicit, elapsed and
   terminal evidence remain unsupported, and every minutes/per-90 product is
   suppressed.
8. **`W04-DESIGN-COVERAGE-01` closed:** all six equations, zero-denominator cases,
   minimum overall, missing rules, and applicability decisions are frozen.
9. **`W04-DESIGN-PLAYER-MATCH-FACT-01` closed:** Section 7.6 defines the canonical
   match-bound Silver player fact, result-independent fields, lineage, coverage,
   minute state, and exact reconciliation.

## 16. Stop rules and handoff

Stop rather than improvise if any accepted digest/path/count changes; a required
tenant, registry, taxonomy, identity, terminal, availability, or rights authority is
absent; an excluded stream would be opened; semantics require name matching; a write
escapes guarded roots; or a dependency, migration, source-rights, local-only, or
architecture change is needed.

The current evidence supports the base W04 Gold grain with explicit research/suppressed
states. It does **not** support exact elapsed player minutes or per-90 features.
Implementation may proceed only through the serial/path-disjoint packets above after
master and independent acceptance of this R3 design.

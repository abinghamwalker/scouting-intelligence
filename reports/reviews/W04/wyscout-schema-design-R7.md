# W04 Wyscout v5 canonical schema and deterministic rebuild design — R7

Status: **implementation design for master and independent review; not self-approved**

R7 replaces R6 in full. It keeps every R6 schema, authority, temporal, path,
ownership, rebuild, and acceptance decision. It closes the two new P1 findings:

1. code provenance is now a deterministic **pre-execution distribution closure**,
   not a list inferred from repository imports; and
2. every record whose raw `kind` is not one of the seven known kinds enters a fixed,
   collision-checked `record_kind=unknown` rejected-record family whose path contains
   only a closed state token and a digest of the canonical original state/value.

The binding measured source evidence remains:

- completion manifest `data/source/wyscout/v5/completion-manifest.json`, 6,803 bytes,
  SHA-256 `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- source profile `reports/phase-gates/W04/source-schema-profile.md`, SHA-256
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- upstream availability `2020-01-28T14:24:27Z` and actual local acquisition
  `2026-07-29T15:51:08.598589Z`;
- classification `wyscout_figshare_v5_cc_by_4`, licence `CC-BY-4.0`,
  restricted project control, attribution required;
- 7 direct objects, 10 durable admitted archive members, 4 directory-only
  exclusions, 7 competitions, 142 teams, 3,603 players, 1,826 matches, and
  3,071,395 event records; and
- accepted source adapter `src/scouting/sources/wyscout.py`, which writes only
  `objects/<name>`, `archive-members/<name>`, and `completion-manifest.json`.

No provider access, excluded-payload read, network, download, wheelhouse acquisition,
dependency change, migration, new local root, ignore-rule change, container, hosted
artifact, runtime label guessing, export, remote mutation, or deployment is
authorised.

## 1. Claim boundary and invariants

The permitted claim is a frozen historical engineering and player-evidence proof.
It does not establish live or current coverage, provider continuity, exact minutes,
commercial-product equivalence, recruitment relevance, or prospective benefit.

The following rules are normative and fail closed.

1. Only completion-declared `object_path` and `member_path` values are readable.
   `matches.zip` and `events.zip` are hash evidence only; downstream code never opens
   them. The four excluded directories have no admitted payload path.
2. Provider record `id` identifies an event record; `eventId` identifies taxonomy.
   Names are display evidence, never identity or semantic matching keys.
3. JSON numbers are parsed as `Decimal`. Event occurrence is period-relative. No
   second-half UTC, half-time duration, terminal, minute, or continuous clock is
   invented.
4. Field, possession, identity, and supported-feature semantics are usable only
   after master decision, independent review, and master acceptance. Every recorded
   decision, review, acceptance, and correction clock is truthful.
5. Source validity and project knowability are distinct. Human authority is never
   backdated to the source release.
6. Existing `DependencyKind`, `IdentityEvidence`, `TemporalEvidence`, and
   `RetrievalResult` contracts remain unchanged. W04 adds strict local contracts and
   projects only compatible current resolved identity rows.
7. Bronze, Silver, Gold, semantic manifests, and semantic proofs contain no run ID,
   host path, elapsed duration, operational trace, or generation clock. The serving
   boundary alone samples a real generation clock.
8. Build identity closes over repository code, the exact selected `uv.lock`
   dependency closure, selected wheels, uv extracted trees, installed distribution
   files and their frozen ownership map, interpreter/libpython, standard library,
   and exact local resources before products are emitted.
9. An absent original wheel ZIP is never claimed verified. Lock hash/size are
   declaration evidence; uv extracted and installed trees are the locally verified
   byte evidence. Cache sidecars are not wheel archives.
10. Rights, identity, cutoff, authority, source, environment, cache association,
    selected-distribution equality, installed ownership, executable, resource,
    lineage, partition, quarantine, reconciliation, and sole-writer failures stop
    the build.
11. Generated identity, product, staging, and bytecode state stays beneath the
    approved `data/working` root. There is no new storage or ignore boundary.
12. The full `G-W04` gate precedes the acceptance integration commit and annotated
    accepted tag. Registry/checkpoint evidence lands in a distinct local ledger
    commit afterward.

## 2. Completion seam and exact source evidence

The source root is exactly `data/source/wyscout/v5`. The completion document is read
first and its digest checked. Each NFC POSIX-relative admitted path must resolve below
that root, be a regular non-symlink file, and match declared size and SHA-256.

Readable direct objects are:

```text
objects/competitions.json
objects/teams.json
objects/players.json
objects/eventid2name.csv
objects/tags2name.csv
```

The ten readable archive members are the five `matches_<country>.json` and five
`events_<country>.json` rows below. Directory scans, fallback archive extraction,
inferred layouts, symlinks, aliases, case-normalised substitutes, and undeclared
paths are forbidden. For each country, distinct event `matchId` equals match `wyId`:
England 380, France 380, Germany 306, Italy 380, Spain 380.

`TenantContext` is explicit: `tenant_id` has no default and `club_id` is nullable but
fixed. The semantic source manifest identity is:

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

Its existing `SourceSnapshotManifest.files` tuple is exactly:

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

Coverage is exact:

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

Values are strict Python `float` `1.0`; counts are strict non-negative `int`. Zero
expected counts, reordered rows, duplicate paths, 17/19 rows, or conceptual Gold
coverage fields fail. The sole manifest artifact is:

```text
data/manifests/wyscout/v5/source/<manifest_id>.source-snapshot-manifest.json
```

## 3. Accepted semantic and identity authorities

The profile proves shapes and counts, not meanings. Each authority follows master
decision → independent review → master acceptance, binds its candidate and upstream
digests, records real ordered clocks, and is unavailable unless review says `PASS`.

### 3.1 Field, possession, and supported-feature routes

Field authority is exactly:

```text
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json
configs/schema/wyscout-v5-field-registry-v1.yaml
reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json
```

It binds the completion/profile, event-map, tag-map, and every measured
`(record_kind,json_path)`. A field is exactly `TRANSFORM`, `PRESERVE_UNMAPPED`, or
`FORBIDDEN`. Unknown fields are unmapped. Unknown record kinds are whole rejected
records under Section 6.2; no field-level interpretation is attempted for them.

Possession authority, available only after field acceptance, is:

```text
reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json
configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml
reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json
```

Predicates use numeric `event_id`, nullable numeric `subevent_id`, sorted required
tag IDs, and sorted forbidden tag IDs. Results are exactly `CONTROL`, `CONTESTED`,
`DEAD_BALL`, `RESTART`, `NON_CONTROL_ADMIN`, or `UNMAPPED`. Unknown combinations are
unmapped; labels are not matched; provider-native possession is not claimed; period
boundaries close; simultaneous cross-team events make an uncertain boundary.

The supported-feature authority is accepted **before Gold**:

```text
reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json
configs/features/wyscout-v5-supported-count-features-v1.yaml
reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json
```

It exhaustively binds supported, suppressed, and unavailable fields; inputs,
aggregation, applicability, denominator, output type, reason, and schema version;
all accepted upstream authorities; product schemas; and neutral-role context.
Minutes, elapsed/rate/per-90, continuous-time, action-value, provider-possession,
outcome-dependent, role-inferred, and unsupported-denominator features are explicitly
unavailable or suppressed. Absence never grants permission. Canonical parsed YAML is
sorted-key JSON with schema-declared array order. Acceptance binds the registry
digest, avoiding a self-digest cycle.

### 3.2 Identity authority and approved generated root

The route is:

```text
reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json
configs/schema/wyscout-v5-identity-ruleset-v1.yaml
reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md
reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json
```

Canonical identity uses numeric source keys:

```text
source_namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
kind_namespace = UUIDv5(source_namespace, "<competition|team|player|match|action>")
canonical_id =
  UUIDv5(kind_namespace, "figshare-v5:<canonical-decimal-source-id>")
```

Zero is not a player identity. Names, current teams, and external knowledge cannot
repair malformed, duplicate, conflicting, or absent keys.

All generated identity state is beneath the already-approved root:

```text
data/working/wyscout/v5/identity/review-queues/
  <queue_sha256>.identity-review-queue.json
data/working/wyscout/v5/identity/bundles/
  <identity_bundle_sha256>.identity-bundle.json
data/working/wyscout/v5/identity/corrections/
  <correction_id>.identity-correction.json
```

The guarded category is `W04_IDENTITY_RUNTIME`; the identity runtime serializer is
the sole writer. Readers begin with one exact accepted bundle path/digest and may
open only queue/correction relative paths it names. Scans, newest-file selection,
unreferenced files, aliases, and alternate roots fail.

`W04IdentityCrosswalkRow` strictly includes tenant, entity kind, source identity and
row refs, manifest/ruleset authorities, nullable canonical ID, positive version,
classification and existing match method, confidence exactly 0.0/1.0, state,
valid/available clocks, reviewer, prior evidence digest, reasons, evidence digest,
row ID, and trace. Exact combinations are:

| Situation | State/effective state | Classification | Existing match method |
| --- | --- | --- | --- |
| unique valid same-kind key | `RESOLVED` | `SOURCE_KEY_DETERMINISTIC_RESOLUTION` | `DETERMINISTIC` |
| malformed/absent/duplicate/conflict | `REVIEW_REQUIRED` | `SOURCE_KEY_REVIEW_REQUIRED` | null |
| source player key zero | `REJECTED` | `PROVIDER_ZERO_ACTOR_REJECTION` | null |
| reviewed queue → entity | `RESOLVED` | `REVIEWED_QUEUE_RESOLUTION` | `REVIEWED` |
| reviewed queue → rejection | `REJECTED` | `REVIEWED_QUEUE_REJECTION` | null |
| direct resolved → entity | `RESOLVED` | `REVIEWED_DIRECT_SUPERSESSION_RESOLUTION` | `REVIEWED` |
| direct resolved → rejection | `REJECTED` | `REVIEWED_DIRECT_SUPERSESSION_REJECTION` | null |
| immutable prior row behind edge | effective `SUPERSEDED` | bundle index `ACCEPTED_SUPERSESSION_EDGE` | original bytes unchanged |

`IdentityMatchMethod.EXACT` is not used. Only a current effective `RESOLVED` row
projects to existing `IdentityEvidence`, renaming `identity_match_method` to
`method`. All non-resolved and superseded rows are excluded.

There are exactly two correction routes. A queue correction names one current
review-required item and exact queue snapshot digest and resolves or rejects it. A
direct supersession names one current resolved evidence digest and changes it to a
reviewed resolution or rejection; it has no queue item/snapshot/history fields and
creates no queue history. Both use master decision → independent review → master
acceptance, real clocks, immutable prior rows, version exactly prior+1, one accepted
edge, and a new bundle. Forks, gaps, route-field mixing, backdating, reviewer/master
collision, and unaccepted corrections fail. New bundle availability is the maximum
accepted authority/correction time and changes temporal/build identity.

## 4. Exact temporal and football products

W04 has exactly five temporal dependencies, sorted by existing enum rank then
canonical ID:

| Evidence | Existing `DependencyKind` | `valid_at` / observed | `available_at` |
| --- | --- | --- | --- |
| strict source manifest | `source_manifest` | source release | source release |
| accepted identity bundle | `identity_evidence` | identity decision | max authority/correction acceptance |
| accepted field registry | `feature_schema` | field decision | field acceptance |
| accepted possession taxonomy | `feature_schema` | possession decision | possession acceptance |
| accepted supported-feature registry | `feature_schema` | feature decision | feature acceptance |

Distinct IDs disambiguate the three `feature_schema` entries. The maximum
`available_at` must be `<= feature_cutoff_ts`; equality passes. Cutoffs before any
decision, review, acceptance, or accepted correction fail. Changing any accepted
clock changes dependency evidence and `build_id`.

The retained products are:

- Bronze canonical raw records and both quarantine families;
- Silver competition, team, player, match, action, lineup-stint, possession, and
  player-match-fact;
- Gold neutral `player-window` count features; and
- per-Gold-partition temporal boundary receipts plus one invocation receipt.

Actions keep source IDs, canonical actor/team/match/competition where resolved,
period code, `eventSec` as Decimal, deterministic period-relative order, numeric
taxonomy IDs, sorted tags, coordinates, source refs, authority IDs, and lineage.
They do not claim absolute event UTC. Match UTC is context only.

Lineup stints use only lineup, bench, substitution, and period-relative evidence.
Unknown entry/exit is explicit. No interval is converted to minutes. Possessions
are deterministic ordered state-machine segments with uncertainty flags and never
claim provider-native possession. Player-match facts are result-independent counts
at `(tenant,competition,season,match,player,team)` with neutral role context; no
home/away or winner/loser feature enters Gold. Gold grain is:

```text
(tenant_id, canonical_player_id, canonical_competition_id,
 canonical_season_id, neutral_role_context_id,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, feature_schema_hash)
```

All contributing matches satisfy match UTC within the half-open window and
dependency availability at cutoff. Coverage retains six equations: source objects,
admitted members, match partitions, event partitions, partition alignment, and
identity resolution/exact exclusion. Minutes and per-90 remain unavailable.

## 5. Exact generated paths, serializers, and atomic publication

The known record-kind enum is exactly:

```text
competition | team | player | event-taxonomy | tag-taxonomy | match | action
```

Known Bronze raw paths are:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  raw/record_kind=<known-kind>/source_sha256=<source_sha>/
  part-00000.parquet
```

The source SHA disambiguates country members. Bronze retains each complete parsed
record as canonical JSON and digest, exact source path/digest/ordinal, measured field
paths/types, accepted registry, admission state, source availability, tenant,
manifest, lineage, and inherited rights.

Known-record rejected fields use:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  quarantine/rejected-field/record_kind=<known-kind>/
  source_sha256=<source_sha>/part-00000.parquet
```

A row contains source ref, exact JSON path, canonical original value/digest, measured
JSON type, `PRESERVE_UNMAPPED|FORBIDDEN`, reason, accepted registry, and rights.

Unknown-record paths are defined separately and exhaustively in Section 6.2. Unknown
records never enter the known raw or rejected-field families.

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

The country token comes only from the admitted member filename. `entities.py` solely
serializes competition/team/player/match; `actions.py` action; `lineups.py`
lineup-stint; `possessions.py` possession; and `player_match.py`
player-match-fact. `silver_manifest.py` alone writes
`data/manifests/wyscout/v5/silver/<build_id>.manifest.json`.

For every non-empty contributing competition/window partition, Gold is:

```text
data/working/wyscout/v5/gold/build_id=<build_id>/player-window/
  competition_id=<uuid>/window_definition_id=<uuid>/
  window_start_utc=<utc>/window_end_utc=<utc>/
  feature_cutoff_ts=<utc>/part-00000.parquet
```

`gold.py` is sole Gold serializer and sole writer of
`data/manifests/wyscout/v5/gold/<build_id>.manifest.json`.

Receipts are:

```text
runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json
runs/w04/wyscout-rebuild/<build_id>/<run_id>/boundary/
  <sha256-of-exact-gold-relative-path>.temporal-boundary-receipt.json
```

`temporal_boundary.py` alone writes boundary receipts. `rebuild.py` orchestrates
named serializers and writes only the invocation receipt; it cannot serialize
products or layer manifests. Receipts contain real generation clocks/run identity
and are excluded from semantic payloads, manifests, and build ID.

Each serializer stages only within:

```text
data/working/wyscout/v5/.staging/<build_id>/<run_id>/
  bronze/<same final suffix>.partial
  silver/<product>/<same final suffix>.partial
  gold/<same final suffix>.partial
  runtime-pycache/
```

`runtime-pycache/` is not a product and must remain empty. A serializer writes,
flushes, closes, hashes, validates, rechecks code/environment closure, and atomically
renames. An existing unequal destination fails. Each layer manifest is written last
through an exact sibling partial and atomically renamed. Final readers open only
paths named exactly once by the completion manifest; missing, extra, partial, or
cross-layer paths fail.

Manifest entries contain repo-relative path, serializer/version, schema, row count,
semantic digest, physical SHA-256/size, ordered parents, partition values, rights,
and completion state. Empty quarantine partitions have manifest count zero and no
zero-row Parquet file. Bronze manifest references every raw/rejected-record/
rejected-field file. Silver references Bronze. Gold references Silver, five temporal
dependencies, accepted feature schema, and proofs.

## 6. R7 closure: unknown record kind and pre-execution environment

### 6.1 Dispatch is total and known kinds are unchanged

The Bronze dispatcher examines the raw top-level JSON member named exactly `kind`
before applying a kind-specific field registry. It records presence separately from
value. A record enters a known raw family only when the member is present, is a JSON
string, and equals one of the seven exact lower-case known tokens in Section 5.
There is no trimming, case folding, Unicode normalization, label lookup, plural
conversion, filename inference, or fallback.

Every other state goes to the unknown rejected-record route below. The entire record
is quarantined; the dispatcher performs no kind-specific field classification and
emits no rejected-field rows for it. It cannot reach Silver.

### 6.2 Fixed unknown partition and canonical original kind identity

Every unknown record uses this grammar:

```text
data/working/wyscout/v5/bronze/build_id=<build_id>/
  quarantine/rejected-record/record_kind=unknown/
  raw_kind_state=<closed-state-token>/
  raw_kind_sha256=<64-lowercase-hex>/
  source_sha256=<source_sha>/part-00000.parquet
```

`record_kind` is always the literal `unknown`; raw provider text is never a path
component. `raw_kind_state` is exactly one of:

| Token | Exact condition |
| --- | --- |
| `missing` | top-level member `kind` is absent |
| `null` | member is present and JSON null |
| `non-string` | member is present and a JSON boolean, number, array, or object |
| `string-unknown-safe` | member is a string, is not known, and matches ASCII `[A-Za-z][A-Za-z0-9_-]{0,63}` |
| `string-unsafe` | member is any other unknown string, including empty, `.`, `..`, slash/backslash, control, percent, non-ASCII, or longer text |

“Safe” affects only the state label; neither safe nor unsafe original text appears
in a path. Known tokens never enter either string state.

The exact digest preimage is the UTF-8 encoding of canonical JSON:

```json
{
  "envelope_version": "w04-raw-kind-v1",
  "state": "<UPPERCASE_STATE>",
  "value_present": true,
  "value": "<exact typed canonical JSON value>"
}
```

`UPPERCASE_STATE` is exactly `MISSING`, `NULL`, `NON_STRING`,
`STRING_UNKNOWN_SAFE`, or `STRING_UNSAFE`. For `MISSING`, `value_present=false` and
`value=null`; for `NULL`, `value_present=true` and `value=null`. That bit makes
missing and null distinct. For all other states, `value` is the original typed
semantic JSON value. Objects sort keys; arrays retain order; strings preserve the
exact Unicode scalar sequence without trimming, NFC, or case folding before the
fixed canonical encoder applies its escaping rules; numbers use the project
canonical `Decimal` representation; booleans remain
booleans. The standard project canonical JSON encoder uses sorted keys, no
insignificant whitespace, UTF-8, and its fixed escaping rules.

The digest is domain-separated and length-framed:

```text
envelope_bytes = canonical_json(envelope)
raw_kind_sha256 = lowercase_hex(SHA256(
  UTF8("w04-raw-kind-v1") || 0x00 ||
  UINT64_BE(len(envelope_bytes)) || envelope_bytes
))
```

The rejected-record row preserves:

```text
source path, source SHA-256, source ordinal
complete canonical raw record and raw-record SHA-256
raw_kind_state
raw_kind_value_present
raw_kind_original_value (typed JSON, nullable only with presence bit)
raw_kind_envelope_bytes
raw_kind_sha256
rejection_code = UNKNOWN_RECORD_KIND
accepted field-registry decision/review/acceptance IDs and digests
source valid/available times
tenant, manifest, row lineage, inherited rights
```

Before staging any partition, Bronze keeps a map from
`(raw_kind_state,raw_kind_sha256)` to exact `envelope_bytes`. Repeated identical
envelopes share a partition. If the same state/digest is observed with unequal bytes,
the complete Bronze invocation fails before final rename or manifest emission. It
never overwrites, merges, chooses first/last, adds a suffix, or changes hash
algorithm. The full 256-bit digest is used.

Examples required by contract:

- absent `kind` and present-null `kind` have distinct states and digests;
- `kind=17`, `kind=false`, `kind=[]`, and `kind={}` preserve distinct typed
  canonical values and do not collide;
- exact string `"Competition"` is `string-unknown-safe`, not `competition`;
- exact strings `"../action"` and `"a/b"` are `string-unsafe`, yield different
  digests, appear nowhere in their paths, cannot escape the fixed root, and produce
  identical relative paths/digests in two different absolute project roots;
- an injected digest collision fails the layer with no final payload or manifest;
- every unknown record appears exactly once in rejected-record reconciliation and
  zero times in known raw, rejected-field, Silver, and Gold.

`bronze.py` remains sole serializer for known raw and both quarantine families and
sole writer of `data/manifests/wyscout/v5/bronze/<build_id>.manifest.json`.

### 6.3 Deterministic conservative distribution closure

Admission has a hard setup precondition: the master has already executed exactly
`uv sync --locked --all-groups` for the repository and the exact interpreter. The
admission process itself is read-only and offline: it neither runs sync nor resolves,
installs, downloads, queries an index, or imports third-party code. It starts before
any W04/rebuild application code is executed.

R7 deliberately admits the conservative exact root all-groups lock closure. It does
not select distributions from repository AST imports. Therefore packages imported
only by another package, entry points, plugins, optional code paths, and native
extension wrappers are pre-admitted when they are in the selected lock closure.

Distribution identity is PEP 503 normalized:

```text
normalize(name) =
  lowercase(collapse_each_maximal_run_of("-", "_", ".")_to("-"))
```

Names must be valid Core Metadata names before normalization. Display spelling,
import root, dist-info spelling, wheel underscore spelling, case, `top_level.txt`,
and filesystem directory name are not distribution identity.

The exact target environment record is made before selection and binds:

```text
implementation name/version
Python full version = admitted interpreter's exact full version
ABI and ordered `packaging.tags.sys_tags()` sequence
sys_platform, os_name, platform_system, platform_machine, platform_release
root project normalized name/version/source
all group names selected, sorted lexicographically
marker environment values used
pyproject.toml SHA-256 and uv.lock SHA-256
uv executable path/version/physical SHA-256
```

#### 6.3.1 Root, group, extra, marker, and lock selection

The selected root is the unique `uv.lock` package whose normalized name and version
equal `[project]` and whose source is the exact editable `"."`. It is excluded from
the third-party set only after its identity is verified. A missing, duplicate, or
different root fails.

All dependency groups declared by `[dependency-groups]` in `pyproject.toml` are
selected, including `data`, `e2e`, `lint-type`, `model`, `orchestration`, `runtime`,
`security`, and `test`. The sorted group list must equal the root
`[package.dev-dependencies]` key set in `uv.lock`, and each locked direct edge must
match the corresponding declared requirement name/specifier. Root production
dependencies, if later added, are also selected. Optional project extras are not
silently selected merely because all groups are selected: an extra is selected only
when an exact selected root or dependency edge explicitly carries that extra.
Changing group or extra selection changes environment and build identity.

Starting with those root edges, selection recursively follows every locked
`dependencies` edge. A PEP 508 marker is evaluated against the exact frozen marker
environment; false edges are omitted, true/unmarked edges are followed. Edge extras
are recorded and activate only the named optional edges of that exact package.
Unknown marker variable, evaluation error, ambiguous extra, or an optional edge
without a selected extra fails. Dependency/package names are normalized before
matching.

If `uv.lock` contains multiple package candidates with the same normalized name,
their source/version/resolution markers must select exactly one for the target.
Zero or multiple true candidates fail; ordering never breaks a tie. Every reached
package's version and source identity are retained. Sources other than the explicitly
supported registry form fail for this W04 third-party closure; editable/path/VCS
third-party packages are not inferred. The graph is traversed to a fixed point and
then sorted by `(normalized_name, canonical_version, canonical_source_identity)`.

The result `L` is the immutable pre-execution selected set:

```text
L = {
  normalized_name, metadata_version, canonical_source_identity,
  active_parent_edges, selected_extras, evaluated_marker_evidence,
  selected_wheel_filename, wheel_tags, lock_sha256, lock_size
}
```

Every non-project member is retained even if the planned command is not expected to
import it. There is no direct-import pruning.

#### 6.3.2 Compatible wheel selection

For each member of `L`, parse every lock-declared wheel filename. Reject invalid
filenames and require the filename name/version to equal the selected normalized
distribution/version. A candidate is compatible when any of its tags occurs in the
frozen ordered `sys_tags()` sequence. Select the candidate whose best tag has the
lowest sequence index. Exactly one candidate may occupy that best rank; ambiguity
fails. If there is no compatible wheel, admission fails rather than selecting an
sdist or building locally.

The exact filename, complete declared tag set, lock SHA-256, size, URL path basename,
and selection rank enter the manifest. The URL is declaration metadata and is never
fetched.

For the reviewed macOS CPython 3.12 arm64 environment this necessarily includes:

```text
pydantic-core 2.46.4
pydantic_core-2.46.4-cp312-cp312-macosx_11_0_arm64.whl

polars-runtime-32 1.43.0
polars_runtime_32-1.43.0-cp310-abi3-macosx_11_0_arm64.whl
```

An ABI3 wheel is valid only through the same ordered tag compatibility test; the
name or suffix does not bypass it.

#### 6.3.3 Exact equality with installed distributions

Admission enumerates only the immediate `.dist-info` directories beneath the
resolved interpreter's exact `purelib` and `platlib` roots. Those roots must resolve
inside the admitted `.venv`, be non-symlink directories, and be the only third-party
site roots in `sys.path`. User site is disabled. `.pth` files are rejected unless
their bytes and non-executable path-only semantics are explicitly included in the
owning selected distribution's verified RECORD; executable `.pth`, external path
addition, `.egg`, and `.egg-info` fail.

Each `.dist-info/METADATA` must be a RECORD-owned regular file with exactly one
valid `Name` and `Version`. Its PEP 503 name and canonical version form installed
identity. Duplicate identities, malformed metadata, nested/aliased dist-info, and
one dist-info claiming a different identity fail.

The verified editable project distribution is identified separately by normalized
name `scouting-intelligence`, version `0.1.0`, exact editable source `"."`, and
its admitted project metadata. It is excluded from installed third-party set `I`.
No other installed object is excluded as “tooling” or “unused.”

Pre-execution admission requires exact set equality:

```text
{(normalized_name, canonical_version) for member in L}
==
{(normalized_name, canonical_version) for member in I}
```

It reports sorted `lock_only` and `installed_only` differences and fails if either
is non-empty. It also requires one-to-one selected-member ↔ installed-dist-info
association. Version equality without normalized name equality is insufficient.
This is the conservative environment rule corresponding to the setup command
`uv sync --locked --all-groups`.

#### 6.3.4 Apply R6 byte rules to every selected member

The following checks are performed independently for **every** member of `L`, not
just direct imports or the two named examples.

1. Compute the expected uv cache selector from PEP 503 name, exact version, and exact
   selected wheel tag tuple. It must be one symlink entry under the admitted
   `wheels-v5` PyPI cache route. Record the symlink's raw text exactly.
2. Resolve the symlink once. Its target must be one regular non-symlink
   `archive-v0/<opaque>` directory inside the same admitted cache root. Absolute raw
   symlink text is permitted only when the resolved target satisfies that
   containment. Chains, dangling links, escape, or shared ambiguous target fail.
3. Lock filename/hash/size and selector sidecars are operational association
   evidence only. A sidecar is never opened or described as a wheel ZIP. If the
   original wheel archive is absent, record
   `original_wheel_archive_present=false` and
   `original_wheel_archive_hash_verified=false`.
4. Parse the extracted tree's exact `.dist-info/RECORD`. Paths are canonical relative
   POSIX paths with no absolute path, `..`, duplicate, symlink, directory row, or
   escape. Except for the RECORD self-row, each row must contain a supported SHA-256
   and size. The physical extracted tree must equal the RECORD path set exactly;
   missing/unrecorded payload fails. RECORD self-row must have empty hash and size.
5. Hash every extracted file and build a length-framed sorted extracted-tree digest.
   This digest attests actual extracted bytes, not the absent archive.
6. Parse installed RECORD by the same path rules. Every installed payload file must
   be regular, non-symlink, contained, and hash/size verified. Installed tree equals
   its RECORD set plus only the exact generated allowance below.
7. Map extracted paths to installed paths using wheel installation rules including
   `.data/{purelib,platlib,scripts,headers,data}`. Unsupported scheme, collision, path
   escape, or overwrite fails. Every extracted payload maps exactly once.
8. Installed mapped bytes must equal extracted bytes. The only admitted
   installer-generated payloads are exact `INSTALLER` bytes `b"uv"` and exact empty
   `REQUESTED` bytes, with valid installed RECORD rows. No other added, modified, or
   omitted payload is allowed.
9. Installed RECORD is expected to differ from extracted RECORD only through the
   installed path rewrite and those two generated rows. RECORD self-row remains
   empty. The comparison is semantic row comparison, not a claim that RECORD bytes
   are identical.
10. Bytecode policy is closed: admitted runs use `-B` and
    `PYTHONDONTWRITEBYTECODE=1`; all pre-existing `*.pyc` and `__pycache__` paths in
    selected installation roots are enumerated and cause failure. The alternate
    run-local `runtime-pycache/` is configured as the sole possible target and must
    remain empty. A pyc is never silently treated as RECORD-owned source.

The reviewed examples preserve the measured rules: pydantic extracted/installed
RECORD row counts 111/113; pydantic-core 10/12; polars-runtime-32 7/9, with the two
extra rows exactly `INSTALLER` and `REQUESTED`. These counts are evidence for the
reviewed environment, not a shortcut around per-file validation.

#### 6.3.5 RECORD-derived import and file ownership

Installed RECORD is ownership authority. `top_level.txt`,
`importlib.metadata.packages_distributions()`, package names, and import ASTs are
advisory diagnostics only.

For each selected installed distribution, admission maps every verified RECORD path
to its unique owner. The same concrete normalized installed path in two RECORDs
fails. Importable candidates are derived as follows:

- a top-level `<identifier>.py` owns that module;
- a path beginning with a valid identifier directory contributes that import root,
  excluding `.dist-info`, `.data`, scripts, headers, and non-import schemes;
- package/submodule ownership follows the longest concrete RECORD-owned file path;
- an extension filename is parsed against the frozen interpreter's complete
  `EXTENSION_SUFFIXES`; removing exactly one matching suffix yields the module name;
  wheel ABI compatibility has already been proved and is not re-guessed;
- package data and native dependent libraries remain concrete file-owned even when
  they are not import roots.

A normal package root may have exactly one owner. A shared namespace root is allowed
only when no contributor RECORD owns an `__init__.py`, each search location is
inside an admitted site root, every concrete child file has exactly one owner, and
no two contributors claim the same module/subpackage/file. Namespace root ownership
is thus a set, but loaded concrete origin ownership is singular. An ambiguous
normal-package root, overlapping namespace child, duplicate native extension, or
unowned search location fails before execution.

Native extension origins are exact RECORD-owned files. Any shared library later
loaded from an admitted site root must also map to exactly one selected RECORD owner.
System/interpreter libraries must match the separately admitted interpreter/
libpython/system-loader closure. A site-root native image that is ambiguous or
unowned fails.

#### 6.3.6 Runtime loaded-owner subset; no expansion

Only after `L`, `I`, every wheel/cache/extracted/installed digest, and the ownership
map have been frozen may W04 code execute. The frozen distribution manifest is
immutable for the run.

An audit/import/loader observer records every loaded third-party module origin,
namespace search location, native extension, site-root shared image, and distribution
owner. Built-in/frozen modules and admitted stdlib are handled by the interpreter
closure. Each concrete third-party origin must be a verified RECORD path with one
owner in `L`; each namespace search location must be pre-admitted as above.

Let `R` be the set of owners actually loaded during the rebuild:

```text
R ⊆ L
```

`R` is evidence, not a new selection mechanism. Members of `L` may remain unloaded.
An owner outside `L`, unowned file, ambiguous owner, external site root, late `.pth`
addition, or mutated installed byte fails immediately. The observer never adds a
distribution, rescans the lock to expand a set, retries after admission, or changes
the code manifest/build ID. Dynamic import is allowed only when its concrete owner
was already in `L`.

`R` and the ordered origin/owner observation log are written to the invocation
receipt and controlling health evidence after execution. They are not inputs to
`build_id`, product paths, product rows, or semantic digests: making a post-execution
observation a build-ID input would create a cycle. The pre-execution `L` and frozen
ownership map are build inputs; the runtime observer proves only that execution
stayed within them. Equal two-root rebuilds must nevertheless report equal
origin/owner observations after removal of absolute-root prefixes.

Required positive closure proofs include:

```text
pydantic 2.13.4 -> pydantic-core 2.46.4
import pydantic loads pydantic_core files/native extension
both owners are in L before execution; pydantic-core is in R when loaded

polars 1.43.0 -> polars-runtime-32 1.43.0
import polars loads _polars_runtime_32 native content
both owners are in L before execution; polars-runtime-32 is in R when loaded
```

Required negative proofs inject: a duplicate concrete RECORD owner; two owners for a
non-namespace root; overlapping namespace child; native extension absent from all
RECORDs; installed-only distribution; lock-only distribution; and a dynamic import
whose distribution is not in `L`. Every case fails, and the final case proves the
manifest did not expand.

### 6.4 Repository, interpreter, standard library, and resources

Repository code selection remains a canonical allowlisted manifest after code
freeze. It includes exact repo-relative regular files required by W04/shared modules,
parses Python imports as a coverage check, rejects symlinks/escape/duplicates, and
hashes exact bytes. Import parsing no longer chooses distributions.

The admitted interpreter is the exact resolved `.venv/bin/python` regular executable
with path, version, implementation, ABI, physical SHA-256, and loader evidence.
`libpython` and required loader images are resolved and hashed. Standard-library
roots are resolved from that interpreter, exclude site-packages, and are manifest-
hashed with exact path rules. Imports outside repo, selected installed ownership,
stdlib, built-in/frozen, and admitted loader/system paths fail.

Local resources are a closed allowlist: accepted authority/config artifacts, source
manifest, identity bundle and named queue/corrections, exact window/cutoff config,
and neutral-role context. Each path and canonical/physical digest is bound. Broad
directory enumeration and post-closure discovery fail.

Environment keys are a fixed allowlist with canonical values; unknown behavior-
affecting variables fail. Locale/timezone/hash seed/bytecode/thread controls are
fixed. Network and provider interfaces are disabled. A pre-output recheck requires
the same code, distribution, installed, interpreter, stdlib, environment, and
resource digests.

## 7. Build identity and deterministic bytes

Canonical build input version is `w04-wyscout-build-id-v5`. It contains tenant;
source manifest; identity bundle/queue/ruleset/accepted corrections; field,
possession, and feature decision/review/acceptance IDs/digests; product schemas;
neutral context; window/cutoff; repository code manifest; selected all-groups lock
closure; wheel declarations; uv selector associations; extracted trees; installed
trees and frozen ownership map; interpreter/libpython;
stdlib; resources; and environment.

```text
build_id = SHA256(canonical_json(all semantic build-input fields))
```

Runtime loaded-owner evidence is a post-execution subset audit and is deliberately
excluded from this pre-execution identity. A missing acceptance, placeholder,
unverified member, mismatch, or pre-closure call makes build identity unavailable.
Branch, tag, commit, absent archive bytes, absolute output root, run ID, and clocks
do not participate.

Parquet remains version 2.6; one `part-00000.parquet` per logical partition; row
group 65,536; zstd level 9; data page 2.0; no dictionary or byte-stream split;
statistics on; page index off; timestamps microseconds without truncation; stored
schema. Rows use canonical UUID/UTC/Decimal/null/list forms and full primary-key
order. Semantic digests cover schema, length-framed rows, and ordered parents;
physical digests cover exact bytes.

Two-root review creates distinct empty project roots, reproduces the same admitted
environment and source, removes only each absolute root from evidence, and requires
equal final relative paths, schemas, rows, semantic/physical digests, manifests,
distribution closure, frozen ownership evidence, post-run origin/owner observations,
and unknown-kind partitions. Operational
receipt run IDs/clocks may differ only in their documented suffix evidence.

## 8. Quality, health, card, gate, and ownership

Quality retains exact source counts and five country equalities; unique matches/event
IDs; exactly two teams per match; zero match/team conflicts; 226,038 zero actors;
lineup/bench/substitution counts; 23/8 unresolved references; period/coordinate
constraints; accepted authorities; exactly five temporal dependencies; neutral,
result-independent facts; zero minute/per-90 output; six coverage equations;
verified full selected environment/resources; sole writers; quarantine
reconciliation; and two-root equality.

Health outputs are:

```text
reports/phase-gates/W04/data-health.json
reports/phase-gates/W04/data-health.md
```

Controlling JSON includes source/identity/temporal/rights metrics; rejected record
and field counts; unknown-kind states/digests/collision status; all-groups locked and
installed sets and exact equality; selected wheel/cache/extracted/installed evidence;
generated-file and pyc results; loaded-owner subset; interpreter/resources; path
ownership; and two-root equality.

The transformed card and independent review remain:

```text
docs/dataset-cards/w04-wyscout-transformed-v1.md
reports/reviews/W04/wyscout-transformed-dataset-card-independent-review-R1.md
```

The card binds build/layer/health digests and states intended/excluded use,
population/coverage, identity correction policy, transformations, supported/
suppressed features, time/minute limitations, coordinate/semantic bias, inherited
rights/attribution, and offline reproduction policy.

`G-W04` passes only when one manifested input deterministically rebuilds Gold from
raw evidence and all identity, reconciliation, temporal, rights, guarded-root,
environment, quarantine, manifest, card, independent-review, and exact-path checks
pass. No report is accepted until every required independent recommendation is
`PASS`.

Sole ownership remains serial. Authority candidates, reviews and acceptances are
separate owners. Bronze owns known raw plus both quarantine families. Identity owns
only its three generated roots. Disjoint Silver product owners write their named
families; Silver manifest is separate. Gold/temporal owns Gold, Gold manifest, and
boundary receipts. Rebuild only invokes and writes its receipt. Admission owns only
admission code/report and the immutable code/environment manifest. Quality, health,
card, independent reviews, master verification, gate, acceptance Git, and ledger are
subsequent serial owners. No directory shorthand grants cross-family writes.

## 9. Controlling two-local-commit acceptance ledger

The sequence remains exact:

1. Master completes implementation, readback, every independent review, candidate
   verification, machine gate, and acceptance rendering. Full `G-W04` passes while
   the phase registry remains pre-checkpoint.
2. Master creates local acceptance integration commit `C_accept` with exact message
   `phase(w04): accept governed data spine`.
3. Master creates annotated local tag `checkpoint/w04-accepted` on exactly
   `C_accept`. The tag is never moved.
4. Master resolves `C_accept` from the tag and writes the registry mutation with W04
   state/checkpoint, exact SHA/tag/message, gate/acceptance paths/digests, and
   evidence paths. The registry contains no ledger commit SHA.
5. Master writes `reports/verification/W04/clean-tree-report.md` as a predicate
   certificate. It names only the two ledger paths, records exact commands/results
   proving no unstaged/untracked path, empty remote list, active guard, and
   index/worktree equality, and contains no own digest, tree hash, or future commit
   SHA.
6. After staging exactly the registry and certificate, master repeats predicates and
   creates one local commit with exact message
   `orchestration(w04): record accepted checkpoint ledger`.
7. Master runs final read-only clean-tree, remote, guard, registry, and local-only
   verification. Empty output is required and no artifact is rewritten.

The accepted tag therefore names accepted product/evidence integration; later `HEAD`
is the ledger commit. Registry-before-tag cycles, self hashes, tag movement, a third
cleanup commit, waiver, or history rewrite are forbidden.

## 10. Required tests and closure

Retained R6 tests cover the exact 18 source rows, rights, authorities, identity
classification/projection, both correction routes, five temporal dependencies,
neutral football products, minute suppression, every path/serializer, staging and
atomic manifests, two roots, resource/interpreter/stdlib closure, health/card/gate,
and the two-commit ledger.

R7 adds mandatory tests:

1. Select all exact root dependency groups, explicit extras only, and marker-active
   recursive edges from `uv.lock`; reject group mismatch, false/ambiguous candidates,
   unsupported source, sdist fallback, and equal-rank wheels.
2. Require exact normalized `(name,version)` equality of selected lock closure `L`
   and installed non-project set `I`; reject either difference, duplicate identity,
   malformed metadata, egg state, external site root, and executable `.pth`.
3. Apply selector-symlink containment, extracted RECORD/tree hashing, install mapping,
   exact `INSTALLER=b"uv"`, empty `REQUESTED`, installed RECORD rewrite, no other
   extras, and empty bytecode policy to every member of `L`.
4. Prove `pydantic → pydantic-core` and `polars → polars-runtime-32`, including
   native origins, are present before code execution and later appear only as members
   of loaded-owner subset `R`.
5. Reject duplicate concrete owners, ambiguous non-namespace roots, overlapping
   namespace children, unowned native files, and runtime imports outside `L`; assert
   there is no runtime expansion or retry.
6. Exercise missing, null, all non-string JSON types, safe unknown string, and unsafe
   string `kind`. Prove exact state/value preservation and total dispatch.
7. Prove distinct unsafe strings neither collide nor escape, full digests are
   root-independent, injected digest collision aborts before final rename, and
   unknown rows never enter known raw, rejected-field, Silver, or Gold.

The seven R5 P1 closures remain: approved identity root; actual extracted/installed
bytes; accepted feature authority and fifth dependency; exact identity
classification methods; two correction routes; exact path/sole-writer grammar; and
the controlling two-commit ledger. R7 closes the two new P1s in Sections 6.2 and
6.3 without weakening any prior closure.

Stop instead of improvising if any path, digest, count, lock set, installed set, or
authority changes; a truthful clock is missing; an unknown would be guessed; an
excluded/source path would be read; event UTC/minutes would be fabricated; an absent
archive would be claimed verified; ownership is ambiguous; runtime wants an
unselected distribution; collision handling would mutate a path; a writer overlaps;
or any dependency, migration, provider, network, rights, architecture, local-only,
ignore, remote, or deployment change is needed.

Implementation begins only after master and another independent reviewer accept R7.
This document does not approve itself.

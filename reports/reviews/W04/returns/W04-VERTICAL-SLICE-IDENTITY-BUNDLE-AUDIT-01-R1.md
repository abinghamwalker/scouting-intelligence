# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-IDENTITY-BUNDLE-AUDIT-01`
- objective: Determine the smallest conformant accepted W04 identity bundle for
  the one-match/one-player four-feature proof and return its bounded serial
  implementation packet.

## Files changed

- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-IDENTITY-BUNDLE-AUDIT-01-R1.md`

## Summary

### Verdict

**PASS_TO_PACKET**, subject to the master freezing the two byte-level choices
listed under **Packet precondition**. Those choices close an implementation detail;
they do not change the approved architecture, source, identity policy, feature
roster, dependency policy, or local-only boundary.

The smallest honest bundle is **source-complete**, not one-match scoped. R20
requires the bundle to contain all four entity kinds and all master rows, plus
every referenced unresolved key, and to recompute its queue, effective index,
counts and history. A bundle containing only competition `364`, match `2499719`,
teams `1609/1631`, and player `285508` would falsely omit admitted identity state
and cannot supply R20's build-identity `identity_bundle_sha256`.

### Exact minimum bundle population

The initial bundle has no prior bundle, corrections, history or supersession:

| Entity kind | Effective state | Current rows |
| --- | --- | ---: |
| `COMPETITION` | `RESOLVED` | 7 |
| `TEAM` | `RESOLVED` | 142 |
| `PLAYER` | `RESOLVED` | 3,603 |
| `PLAYER` | `REVIEW_REQUIRED` | 15 |
| `PLAYER` | `REJECTED` | 1 |
| `MATCH` | `RESOLVED` | 1,826 |
| **total** |  | **5,594** |

Additional exact state is:

- `historical_row_digests=()`;
- `supersession_edges=()`;
- `accepted_corrections=()`;
- `prior_identity_bundle_id=null` and
  `prior_identity_bundle_sha256=null`;
- queue population: 15 `PLAYER/OPEN` items, 0 other items;
- the 23 non-zero absent bench occurrences aggregate by source identity and reason
  family to those 15 items;
- the 8 substitution-in misses are all provider player ID `0`. Together with the
  226,038 zero-player action rows they feed the one `PLAYER/REJECTED` current row.
  They do **not** enter the queue because the accepted player-zero policy is
  `REJECT` and the queue policy is exact unresolved **non-zero** references;
- the rejected zero row has 226,041 distinct top-level source-row references:
  226,038 action rows plus match ordinals Italy `327`, `373`, and `377`. The match
  raw-record digests are respectively
  `2ce947031911fe1c1f1ca678b0297c6e7f4f825a8b75e0cad0556ea5a5c1c1d9`,
  `d96e12bf4a4652d3512ae4e9bed6f69f188f3a0c8ce988818345880587bfc4c6`,
  and `be45ce847fc54f68add2c43a315413d29e6e96b2fd1405738aba4bf7ef5e1b32`.

Initial current rows use `version=1`, `valid_from=2020-01-28T14:24:27Z`,
`valid_to=null`, `available_at=2026-07-31T14:15:26Z`, `reviewed_by=null`, and
`supersedes_evidence_digest=null`. The valid combinations are exactly:

- unique positive same-kind master row: `RESOLVED`,
  `SOURCE_KEY_DETERMINISTIC_RESOLUTION`, `DETERMINISTIC`, canonical UUIDv5,
  confidence `1.0`;
- non-zero absent player master: `REVIEW_REQUIRED`,
  `SOURCE_KEY_REVIEW_REQUIRED`, null method/canonical ID, confidence `0.0`;
- player zero: `REJECTED`, `PROVIDER_ZERO_ACTOR_REJECTION`, null
  method/canonical ID, confidence `0.0`.

No name, label, current-team value, string integer, Boolean, float, zero-to-null
coercion, or external knowledge participates.

### Exact target source-key states

All five target keys occur exactly once in their admitted same-kind master member
and are `RESOLVED` at version 1:

| Kind/source key | Physical source row | Canonical raw-record SHA-256 | Canonical ID |
| --- | --- | --- | --- |
| `competition:364` | `objects/competitions.json#1` | `6a5916b3e5cf86d73a6409f159804eaa62dcef27614129a2e15a52b67207b36a` | `cb5c5317-fa4a-571e-93dc-ef6ce482eab7` |
| `team:1609` | `objects/teams.json#84` | `82dbdc6c1ec0ae9da8d63078b3815cb7e2ef84fc29bacac18c85e65b011d9d96` | `b5f2dd3c-0166-5384-99fa-0ed47cc7e44c` |
| `team:1631` | `objects/teams.json#54` | `be9e47831f6d86450cd3fa9fb7471e26da691fa793bdc0d06ffb929a757b8a10` | `5b353635-819b-5bd1-8ca2-5a7364042a96` |
| `player:285508` | `objects/players.json#757` | `c6f2f4c5b74563a12cdb78fa49ae295622f5f730ff980fdb220448a4b404e1ac` | `be8da881-2b15-513f-978f-6bb3865bc8e2` |
| `match:2499719` | `archive-members/matches_England.json#379` | `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86` | `bad97950-6fac-5cf0-a93c-094f91abbb9b` |

The match row independently reconciles `competitionId=364`,
`teamsData` keys and `teamId` values exactly `{1609,1631}`,
`seasonId=181150`, and `dateutc="2017-08-11 18:45:00"`.

`SourceIdentity` is exact `provider="Wyscout"`,
`source_version="figshare-v5"`, and source ID
`<competition|team|player|match>:<canonical-decimal-id>`. The UUID rule is the
accepted nested UUIDv5 source/kind namespace plus
`figshare-v5:<canonical-decimal-id>`.

### Exact initial review queue

Every item has kind `PLAYER`, state `OPEN`, reason family
`NONZERO_ABSENT_MASTER`, first-seen valid clock
`2020-01-28T14:24:27Z`, available clock `2026-07-31T14:15:26Z`, and null
disposition. References below are `path#ordinal` and aggregate repeated
occurrences rather than creating duplicate items:

| Player source ID | Exact source-row references |
| ---: | --- |
| 3689 | `matches_Spain.json#88` |
| 298776 | `matches_Spain.json#77` |
| 302605 | `matches_Germany.json#50` |
| 379199 | `matches_England.json#56`, `#69` |
| 381235 | `matches_France.json#235` |
| 447214 | `matches_England.json#68` |
| 470819 | `matches_England.json#65` |
| 471582 | `matches_France.json#21` |
| 475356 | `matches_Italy.json#59` |
| 488648 | `matches_Italy.json#59` |
| 497353 | `matches_Germany.json#44` |
| 503366 | `matches_Spain.json#40`, `#46`, `#55`, `#61`, `#71`, `#85`, `#95`, `#104` |
| 530062 | `matches_France.json#57` |
| 531447 | `matches_Italy.json#83` |
| 532900 | `matches_England.json#59` |

The runtime must derive each complete `WyscoutSourceRowReference`, including its
admitted member SHA-256 and canonical raw-record SHA-256, from verified source
bytes. The audit reproduced all 22 distinct parent raw digests; they must not be
hard-coded as a substitute for source verification.

### Authority bytes and clocks

- source manifest ID/digest:
  `4e16bdb5-afe7-5601-88ad-adc124cfce3b` /
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`;
- completion digest:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- field registry ID/canonical digest/acceptance digest:
  `w04-wyscout-field-registry-v2` /
  `93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959` /
  `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436`;
- identity decision ID/physical and canonical digest:
  `w04-wyscout-identity-ruleset-decisions-v1` /
  `6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192`;
- ruleset ID/physical digest/canonical digest:
  `w04-wyscout-identity-ruleset-v1` /
  `8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547` /
  `9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c`;
- review ID/physical digest/record digest:
  `w04-wyscout-identity-ruleset-independent-review-R1` /
  `62295d6a1da681fbec23285ca6c74124e3ef44fe3962c1472f0523ef46fb2a19` /
  `bbc24b7f4417d33b2daae2e85f69420b829dbbf61b61052d6d37a0934cf360a9`;
- acceptance ID/digest:
  `w04-wyscout-identity-ruleset-acceptance-v1` /
  `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86`;
- clocks: decision `2026-07-31T12:44:27Z`, review
  `2026-07-31T14:11:16Z`, acceptance `2026-07-31T14:15:26Z`.

Every current row, queue and bundle binds all applicable authority IDs and digests.
The identity dependency is observed at the decision clock, available at the
acceptance clock (there are no corrections), has digest equal to the accepted
bundle SHA-256, and has ID exactly
`UUIDv5(w04_dependency_namespace, "identity_bundle:" + bundle_sha256)`.

### Canonical order and hashes

- Canonical JSON is UTF-8, sorted object keys, compact separators, NFC strings,
  strict typed values, no duplicate/unknown keys, no floats, and one terminal
  newline only where the artifact contract expressly requires it.
- Crosswalk evidence SHA-256 covers every semantic field through sorted unique
  `reason_codes`; it excludes only `evidence_digest`, `crosswalk_row_id`, and
  `trace_id`. The row ID and trace use the exact R20 formulas. Versions are
  consecutive from one.
- Current rows sort by entity-kind rank `COMPETITION, TEAM, PLAYER, MATCH`, then
  provider, source ID, source version, version, evidence digest. Source row refs
  sort by completion path, physical ordinal, raw-record digest and are unique.
- Queue items sort by entity-kind rank, provider, source ID, source version,
  reason family, then UUID bytes. Queue counts are recomputed from items. Queue
  bytes exclude their digest; the filename is the SHA-256 of exact canonical
  bytes.
- Historical digests and correction rows sort lexically; supersession edges sort
  by prior digest then successor digest. Effective counts are recomputed from
  current rows and edges.
- Bundle bytes use the accepted R20/R5 closed fields, exclude their own digest and
  derived ID, and are content addressed by SHA-256. The bundle ID is derived only
  after byte hashing and is never embedded back into the preimage.

### Lineup decision for the four-feature proof

The identity bundle itself does not need a lineup-stint product. It does need all
five admitted match members to close referenced-player identity and its queue.

The downstream selected player is **not** event-only: in match `2499719`, player
`285508` is bench index `4` for team `1631` and is substitution index `1`,
`playerIn=285508`, `playerOut=192748`, nominal minute `82`. Therefore the product
slice must read and reconcile this target match formation and must not claim an
event-only/no-lineup state. The smallest truthful Silver proof includes one
right-censored stint beginning at nominal `[82,83)` with no invented terminal or
elapsed minutes. This does not add a feature: Gold remains limited to
`action_count`, `coordinate_known_action_count`, `match_count`, and
`resolved_possession_action_count`.

### Packet precondition

R20 fixes the semantic inputs but does not spell the UUID namespace/preimage for
`queue_item_id` byte-for-byte, nor a closed reason-code token for its non-zero
absent-master case. Before dispatch, the master must freeze these exact bounded
values in the packet and tests. Recommended minimal values are:

```text
identity_review_queue_namespace = UUIDv5(
  NAMESPACE_URL,
  "urn:scouting-intelligence:w04:wyscout:identity-review-queue:v1")
queue_item_id = UUIDv5(
  identity_review_queue_namespace,
  canonical_json({
    "entity_kind": "PLAYER",
    "reason_family": "NONZERO_ABSENT_MASTER",
    "source_identity": <complete SourceIdentity>,
    "source_manifest_id": <canonical UUID>,
    "tenant_id": <canonical UUID>
  }))
reason_codes = ("NONZERO_ABSENT_PLAYER_MASTER",)
```

This is an additive serialization decision, not new identity semantics. A runtime
producer must not invent a different separator, namespace, reason token, or
preimage.

### Bounded serial implementation packet

**Packet ID:** `W04-IDENTITY-BUNDLE-RUNTIME-01-R1`

**Objective:** implement, materialize, reopen and verify the one exact
source-complete initial identity queue and bundle described above; expose its
digest/derived ID for later build authority. Do not write Bronze, Silver, Gold,
build, receipt, code-manifest, or product bytes.

**Serial ownership:** one producer only; no delegation or Git. Because this closes
shared boundary bytes, a fresh independent reviewer and master reproduction are
mandatory before any consumer uses the bundle.

**Allowed code/test paths:**

- `src/scouting/contracts/wyscout_identity.py`
- `src/scouting/contracts/__init__.py` (only named W04 identity exports)
- `src/scouting/identity/wyscout.py`
- `src/scouting/identity/__init__.py`
- `tests/contracts/test_w04_wyscout_identity_bundle.py`
- `tests/unit/test_wyscout_identity.py`
- `reports/reviews/W04/returns/W04-IDENTITY-BUNDLE-RUNTIME-01-R1.md`

**Invoked runtime paths:**

- `data/working/wyscout/v5/identity/review-queues/<queue_sha256>.identity-review-queue.json`
- `data/working/wyscout/v5/identity/bundles/<identity_bundle_sha256>.identity-bundle.json`

No correction file is emitted because the accepted-correction set is empty.

**Required behavior:**

1. Reopen and verify the completion manifest, source snapshot manifest, all three
   identity authority artifacts and acceptance, and every exact master/match/action
   source member needed to recompute the full population. Never scan for newest or
   use an undeclared path.
2. Parse identity-bearing fields as strict JSON integers only. Reject duplicate,
   malformed, missing, zero (under its distinct policy), cross-kind and conflicting
   keys without name matching or coercion.
3. Build all 5,594 version-1 current rows and exact 15-item queue; aggregate source
   refs and fail if any count, membership, order, authority, clock, or digest differs.
4. Canonicalize once, calculate queue digest, write/confirm its exact guarded
   content-addressed path, reopen and compare exact bytes/digest.
5. Bind that queue path/digest into the initial bundle, canonicalize once,
   calculate bundle digest and derived dependency ID, write/confirm the exact
   guarded path, reopen and recursively recompute every row, count, queue and
   digest edge.
6. Equal existing bytes are idempotent; unequal existing content, a sidecar,
   partial, alias, scan, symlink, escape, stale queue/bundle or extra file fails
   closed. Do not clean or overwrite.

**Focused acceptance checks:**

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check \
  src/scouting/contracts/wyscout_identity.py src/scouting/identity/wyscout.py \
  tests/contracts/test_w04_wyscout_identity_bundle.py tests/unit/test_wyscout_identity.py
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check \
  src/scouting/contracts/wyscout_identity.py src/scouting/identity/wyscout.py \
  tests/contracts/test_w04_wyscout_identity_bundle.py tests/unit/test_wyscout_identity.py
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync mypy \
  src/scouting/contracts/wyscout_identity.py src/scouting/identity/wyscout.py
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q \
  tests/contracts/test_w04_wyscout_identity_bundle.py tests/unit/test_wyscout_identity.py \
  tests/contracts/test_w04_identity_ruleset_authority.py
```

Tests must include exact target rows/IDs, 5,594 counts, 23-to-15 queue aggregation,
8 substitution zeros excluded from queue, 226,041 zero-row source refs, repeated
byte-identical materialization/readback, and adversarial missing/additional/
duplicated/reordered/stale/cross-kind/cross-source/cross-tenant data. They must
reject strings such as `"285508"`, Booleans, floats, names, zero resolution,
queue omission, bundle omission, a digest-only witness, alternate preimage, wrong
clock, wrong authority digest and path scanning.

**Stop conditions:** any new dependency, source/provider acquisition, correction,
external identity, architecture/feature expansion, data-rights change, product
write, build-ID calculation, receipt, remote/network/cloud/container/CI/endpoint/
deployment action, or need to change R20/R21 bytes.

## Tests run

- complete reads of every `read_first` path: exit `0`.
- authority physical SHA-256 reproduction with `shasum -a 256`: exit `0`; exact
  decision, candidate, review and acceptance digests matched the accepted graph.
- locked/no-sync, bytecode-disabled source reconciliation over exact completion
  members: exit `0`; reproduced unique target master rows/ordinals/digests/UUIDs,
  target match/team/formation state, `23` absent bench occurrences aggregated to
  `15` non-zero queue identities, and all `8` substitution-in misses as player
  zero.
- canonical raw-record digest reproduction for all 22 distinct queued parent match
  rows and the three player-zero substitution parent rows: exit `0`.
- the first sandboxed uv attempt was denied read access to the local uv cache;
  rerunning the same read-only locked/no-sync command with approved cache access
  exited `0`. No sync, install or dependency mutation occurred.

## Artifacts/evidence

- audit and packet:
  `reports/reviews/W04/returns/W04-VERTICAL-SLICE-IDENTITY-BUNDLE-AUDIT-01-R1.md`
- controlling identity scope: R20 Section 4.2 and retained R5 Section 6.4.
- accepted authority:
  `configs/schema/wyscout-v5-identity-ruleset-v1.yaml` and the three named
  `reports/reviews/W04/authorities/wyscout-identity-*` artifacts.

## Risks

- A match-local bundle would be a P1 false completeness/build-authority claim.
- Treating the eight provider-zero substitution references as open queue items
  would violate the accepted player-zero and non-zero queue policies.
- Omitting target bench/substitution evidence would falsely describe player
  `285508` as event-only and overstate lineup coverage.
- Queue namespace/preimage or reason-code invention outside the master-frozen
  packet would create unaccepted bytes.
- Source-complete zero-reference collection is intentionally large; the producer
  must stream it under bounded memory and must not replace exact membership with a
  count-only witness.

## Follow-up items

- Master freezes the packet-precondition values, dispatches the serial producer,
  then obtains fresh independent byte/population review before admitting the
  bundle into the fifth dependency or build projection.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

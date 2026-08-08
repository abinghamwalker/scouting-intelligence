# W09 retained Wyscout data inventory and coverage baseline

Status: **READBACK PASS; G-RW1 NOT YET SATISFIED**
Inventory date: 2026-08-05
Scope: retained local Wyscout figshare v5 source, identity, Bronze, Silver and
Gold evidence only; no acquisition, mutation or external access was performed.

## Result and population boundary

The retained source snapshot is byte-present and reconciles exactly to the
authorised five-league 2017/18 universe: **1,826 matches, 3,071,395 actions,
142 source-catalogue teams and 3,603 source-catalogue players**. Those are four
different source counts, not an eligibility statement.

The retained identity bundle is source-complete for the admitted master catalogues and
matches. It deterministically resolves all 3,603 catalogue players, but it also records
15 non-zero player IDs seen only in lineup/bench evidence as `REVIEW_REQUIRED` and
rejects provider actor `player:0`. The interactive/future eligible player population is
therefore **not yet materialised and has no defensible count**. It will necessarily be
smaller than, or at most equal to, the resolved catalogue after minutes, coverage,
temporal, identity and feature-availability filters are applied.

The retained W04 canonical chain is intact but deliberately proof-only: two Bronze
files derived from one English event member, four Silver products covering one match,
and one Gold player-window row with four count features. It is not the full historical
research population and must not be used as retrieval-quality evidence. No synthetic
row appears in these Wyscout artifacts; synthetic catalogues remain test fixtures only.

## Source authority, rights and clocks

| Authority | Retained value |
| --- | --- |
| source | `wyscout-soccer-match-events-figshare-v5` |
| collection | `10.6084/m9.figshare.c.4415000.v5`, collection version 5 |
| source snapshot manifest ID | `4e16bdb5-afe7-5601-88ad-adc124cfce3b` |
| source snapshot manifest SHA-256 | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` |
| completion manifest SHA-256 | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| source completion index SHA-256 | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` |
| source availability floor | `2020-01-28T14:24:27Z` (frozen collection release) |
| local acquisition clock | `2026-07-29T15:51:08.598589Z` |
| licence/classification | CC BY 4.0 / `wyscout_figshare_v5_cc_by_4` / restricted local use |
| retained health evidence | `reports/phase-gates/W04/data-health.json`, SHA-256 `ecbf0e52ec702a42b06a2b0a0528bd1716ee7c2922ab4924e468cca83fd9cfd5` |

The licence evidence permits retention, transformation, model training/evaluation and
attributed derived use. The project boundary is stricter: raw export, network transfer
after acquisition, public/hosted display, external model calls, cloud storage,
deployment and publication are forbidden. Attribution is required:

> Data source: Pappalardo et al., Soccer match event dataset, supplied by Wyscout,
> figshare collection v5, licensed CC BY 4.0.

The project normalises the JSON, reconstructs lineup stints and possessions, and derives
player-window aggregates. `acquired_at` and generated times are operational evidence;
they are not backdated knowability. Matches are observed at `matches.dateutc`; event
occurrence is derived from match start, period and `eventSec`. Historical replay before
the collection availability floor is forbidden because v5 has no record-level
publication/correction clock.

`configs/policies/data-rights.yaml` is a default-deny policy whose W03 synthetic section
does not authorise real data. Its explicit W04 classification does authorise this exact
figshare v5 snapshot and matches `configs/sources/w04-provider.yaml`; no rights
contradiction was found.

## Acquired source objects

All paths in this table are below `data/source/wyscout/v5/objects/`. Physical byte size,
SHA-256 and configured MD5 were read back. JSON/CSV row counts are those bound by the
verified source snapshot manifest.

| Object | Bytes | MD5 | SHA-256 | Rows / observed schema |
| --- | ---: | --- | --- | --- |
| `competitions.json` | 1,209 | `3dc210a4805dda5337b0ff9f7eaa407a` | `39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1` | 7; JSON array fields `area, format, name, type, wyId` |
| `teams.json` | 27,404 | `1381ff9449f21105090729cf0e086b5b` | `9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d` | 142; `area, city, name, officialName, type, wyId` |
| `players.json` | 1,737,347 | `f28ddf6326281efeda6488b2169f5609` | `877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e` | 3,603; `birthArea, birthDate, currentNationalTeamId, currentTeamId, firstName, foot, height, lastName, middleName, passportArea, role, shortName, weight, wyId` |
| `matches.zip` | 645,097 | `51d80beb17480919f69a53a0152c2d71` | `c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9` | archive; admitted/excluded directory described below |
| `events.zip` | 77,323,413 | `7c20e8647e7eda58d7838a0c7b1ec6ab` | `877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45` | archive; admitted/excluded directory described below |
| `eventid2name.csv` | 1,001 | `46daf16100ece0c743eedc9adcfea162` | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` | 36; `event,subevent,event_label,subevent_label` |
| `tags2name.csv` | 1,754 | `e7acb14918d00e40c80a898b1da8fc39` | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` | 59; `Tag,Label,Description` |

The unversioned `players.json` profile attributes, including `currentTeamId`, must not be
treated as historical match facts. Historical team/season membership must come from
match and lineup evidence.

## Admitted five-league archive members

All paths are below `data/source/wyscout/v5/archive-members/`. Every admitted file exists
with the declared byte count and SHA-256. All five match partitions expose the same
top-level row fields `competitionId, date, dateutc, duration, gameweek, label, referees,
roundId, seasonId, status, teamsData, venue, winner, wyId`. All five event partitions
expose `eventId, eventName, eventSec, id, matchId, matchPeriod, playerId, positions,
subEventId, subEventName, tags, teamId`.

| League | Match rows | Match bytes | Match SHA-256 | Action rows | Action bytes | Action SHA-256 |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| England | 380 | 1,694,720 | `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29` | 643,150 | 188,888,614 | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` |
| France | 380 | 1,707,222 | `851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea` | 632,807 | 186,374,196 | `18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317` |
| Germany | 306 | 1,377,328 | `6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9` | 519,407 | 152,916,631 | `2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3` |
| Italy | 380 | 2,019,196 | `afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725` | 647,372 | 190,544,685 | `b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84` |
| Spain | 380 | 1,705,380 | `9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce` | 628,659 | 184,164,406 | `b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154` |
| **Total** | **1,826** |  |  | **3,071,395** |  |  |

The source-completion index independently binds all five event members. For each member,
`row_count == indexed_action_count == sum(period.action_count)`; its aggregate is
3,071,395 across 3,652 match-period groups. The retained health evidence also records
zero duplicate action IDs and five exact event/match partition ID alignments.

## Deliberately excluded archive members

The source admission policy excludes the two tournament partitions. Only their ZIP
directory entries were inspected; payloads were not extracted or admitted. Consequently
there is deliberately no retained payload SHA-256. The directory CRC32 is the only
retained checksum and must not be mislabelled as a payload digest.

| Archive member | Compressed bytes | Declared bytes | Directory CRC32 | Disposition |
| --- | ---: | ---: | --- | --- |
| `matches_European_Championship.json` | 19,805 | 312,151 | `9e64a3d4` | directory verified; payload not opened/admitted |
| `matches_World_Cup.json` | 25,498 | 395,677 | `649719a9` | directory verified; payload not opened/admitted |
| `events_European_Championship.json` | 1,869,471 | 22,954,338 | `13c071be` | directory verified; payload not opened/admitted |
| `events_World_Cup.json` | 2,440,430 | 29,981,214 | `053e0ae8` | directory verified; payload not opened/admitted |

## Source manifests and retention sidecars

| Artifact | Bytes | Physical SHA-256 | Schema / scope |
| --- | ---: | --- | --- |
| `data/source/wyscout/v5/completion-manifest.json` | 6,803 | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` | schema 1; state `complete`; 7 objects, 10 admitted members, 4 directory-only exclusions |
| `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json` | 4,199 | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | schema 1; provider schema `figshare-v5+completion-v1+bridge-v1`; 18 file entries |
| `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json` | 644,037 | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | `w04-wyscout-source-completion-index-v1`; five event members and 3,652 period groups |

There are 18 retained payload sidecars below `data/source/wyscout/v5/`. Each is schema
version 1 and binds its payload path, byte size and SHA-256 plus local-retention/raw-export
rules; the completion sidecar additionally asserts immutability. Their own physical
readback is:

| Sidecar path (relative to source root) | Bytes | SHA-256 |
| --- | ---: | --- |
| `completion-manifest.json.manifest.json` | 386 | `30c0349e3804b39338818861c726e980b72a78063df074448be13ad805416f7c` |
| `objects/competitions.json.manifest.json` | 469 | `99e61197cd3d83c04be40a91600e5cec39f543a7860d2c0da13e552f2708811f` |
| `objects/teams.json.manifest.json` | 463 | `d9debd063fad2ccca2502bd6233ade3922616b12c441354ed92630e81a079bfa` |
| `objects/players.json.manifest.json` | 467 | `cd58095b16e992f3c971ba5c6288cc0a017ebab05f1c75d9aba824316d9776ed` |
| `objects/matches.zip.manifest.json` | 456 | `b9a4642acff2f7376e6c69bed54fa2c65e8eb8e5fd9532b86a527a979eccc225` |
| `objects/events.zip.manifest.json` | 457 | `2e7f056ca657c2b75a654d3a72d84a29df1edcc67b938e8c839c1547a8d34cf5` |
| `objects/eventid2name.csv.manifest.json` | 468 | `ca7e6a1d91f61674db56dfbf329afe83aad3234de661a7828b31e653d8ab3a84` |
| `objects/tags2name.csv.manifest.json` | 465 | `0d22353e03630eb0a116fe78e68d66f37d6e9a590aecf32d89627bef61200f75` |
| `archive-members/matches_England.json.manifest.json` | 525 | `03c2a94d8be9566d36f8a72b0fd1dd14ad53969eedca6dcdd44c7f0a98e0e368` |
| `archive-members/matches_France.json.manifest.json` | 524 | `32434d72def865a887452ff8f01a19d7b2c471798841392c7a3cc4d1ce3fab58` |
| `archive-members/matches_Germany.json.manifest.json` | 525 | `2dad6140758c054e587d3a9daf0e8a5a9ecb2b90ddd1a5925b6ba14a833d02e5` |
| `archive-members/matches_Italy.json.manifest.json` | 523 | `d6faa38df63cfe3807fb2d184daebbb86c48a994c6e5f797f1f9005e6cce9d90` |
| `archive-members/matches_Spain.json.manifest.json` | 523 | `126616ca64976cd74d9c0c833a5d4463785ebe2b4e766882e1d15fbc235aa7bb` |
| `archive-members/events_England.json.manifest.json` | 525 | `dfa632a0795c3c4253f9ee013c6d96b5a6528489ced92c084a13caaef2a2d8b6` |
| `archive-members/events_France.json.manifest.json` | 524 | `e901d6c8c10072a948a169e0fb2038f8b822da60446c6c968274d06bf4a6e9f8` |
| `archive-members/events_Germany.json.manifest.json` | 525 | `7c1a1b4701f29aff58a10cce0f402e0993d2e49144a91eb4a9b80970dd7d52f5` |
| `archive-members/events_Italy.json.manifest.json` | 523 | `61d884fed37fac5e972ce894e7e5578597b5dd11c0043f454716e875c34ebb9e` |
| `archive-members/events_Spain.json.manifest.json` | 523 | `6762f64bc9ec4e1255d48f7828efb321631f3c7d87e87f21cf7caa672e99f3b6` |

## Player-population reconciliation

The full admitted JSON was streamed locally for this inventory. `lineup-referenced`
means the union of starting lineup, bench, substitution-in and substitution-out player
IDs in the 1,826 match objects. A zero is a provider sentinel, not a player.

| Population measure | Count | Interpretation |
| --- | ---: | --- |
| source player catalogue | 3,603 | all `players.json` rows; not eligibility |
| identity-resolved catalogue players | 3,603 | deterministic source-key mappings; no collision observed |
| distinct event-referenced non-zero player IDs | 2,568 | all are in the catalogue; 1,035 catalogue players have no event reference |
| zero-actor event rows | 226,038 | rejected sentinel evidence, not candidates |
| distinct lineup-referenced non-zero player IDs | 3,011 | 2,996 catalogue-resolved plus 15 absent-master IDs |
| source-catalogue players referenced by any lineup evidence | 2,996 | 607 catalogue players have no lineup reference |
| non-zero IDs in event-or-lineup union | 3,011 | 2,996 resolved catalogue IDs plus the same 15 absent-master IDs |
| lineup reference occurrences | 89,733 | 40,172 lineup + 28,715 bench + twice 10,423 substitutions |
| zero lineup occurrences | 8 | collapse to 3 distinct match source-row references in identity evidence |
| future eligible player-season/window rows | **unset** | must be built and reconciled by W09; cannot be inferred from 3,603 |

All event-referenced non-zero players are catalogued. The 15 absent-master IDs occur in
bench evidence, account for 23 distinct match-row references, and remain open rather than
being guessed. The 607 catalogued players with no event or lineup reference cannot enter
an evidence-based feature matrix merely because a master record exists.

## Identity bundle and review queue

| Artifact | Bytes | SHA-256 / identifier | Schema and scope |
| --- | ---: | --- | --- |
| `data/working/wyscout/v5/identity/bundles/4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80.identity-bundle.json` | 91,420,676 | bundle SHA-256 `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`; dependency ID `31638732-5b25-57db-9eb4-8e943a47a387` | schema 1 / `w04-wyscout-identity-bundle-v1`; 5,594 current rows and 5,594 effective-state rows |
| `data/working/wyscout/v5/identity/review-queues/e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51.identity-review-queue.json` | 17,412 | SHA-256 `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51` | schema 1 / `w04-wyscout-identity-review-queue-v1`; 15 `PLAYER:OPEN` items |

The bundle schema carries tenant and source-manifest authority; ruleset, decision,
independent-review and acceptance IDs/digests/clocks; `current_rows`;
`historical_row_digests`; an effective-state index; supersession edges; counts; the
content-addressed queue path/hash; accepted corrections; prior-bundle links; and observed
and availability clocks. Each crosswalk row carries entity/source identity, immutable
source-row references, canonical ID or explicit absence, version, classification and
match method, confidence, state, validity/availability, reviewer/supersession evidence,
reason codes, evidence digest, row ID and trace ID. The queue schema carries the same
authority graph plus canonically ordered items with source identity/rows, reason family,
first-seen and availability clocks, status and optional disposition.

Identity authority is ruleset `w04-wyscout-identity-ruleset-v1` at SHA-256
`9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c`.
It was decided at `2026-07-31T12:44:27Z`, independently reviewed at
`2026-07-31T14:11:16Z`, and accepted/available at `2026-07-31T14:15:26Z`.

| Entity/effective state | Rows | Method/status |
| --- | ---: | --- |
| competition resolved | 7 | source-key deterministic, confidence 1 |
| team resolved | 142 | source-key deterministic, confidence 1 |
| player resolved | 3,603 | source-key deterministic, confidence 1 |
| match resolved | 1,826 | source-key deterministic, confidence 1 |
| player review required | 15 | non-zero absent player master; canonical ID absent; confidence 0 |
| player rejected | 1 | provider zero actor; canonical ID absent; confidence 0 |

The bundle has 5,578 deterministic resolved rows, 15 review-required rows and one rejected
row. It contains no historical rows, supersession edges, accepted corrections or prior
bundle. There are zero duplicate source identities, zero duplicate resolved canonical IDs,
zero duplicate queue IDs and zero duplicate queue source identities. The rejected zero
row binds 226,038 action source rows plus 3 distinct match source rows; the latter contain
8 zero lineup occurrences. The 15 open queue items bind 23 match rows.

This bundle is **population-capable as the initial source-to-canonical identity authority**:
it covers every admitted master competition, team, player and match and all observed
absent/zero player identity exceptions across all five partitions. It is not itself an
eligibility, minutes, team-history or feature product. Open items must remain excluded or
explicitly unresolved; they must not be auto-merged.

## Retained canonical manifests and lineage

All three manifests are schema `w04-wyscout-layer-manifest-v1`, build
`b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79`,
source snapshot SHA-256 `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`,
source completion index SHA-256
`46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`,
feature schema SHA-256
`49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`,
and dependency-lineage hash
`ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d`.
The dependency set binds the source, identity bundle and three accepted schema authorities.

| Layer manifest | Bytes | Physical SHA-256 | Parent |
| --- | ---: | --- | --- |
| `data/manifests/wyscout/v5/bronze/b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79.manifest.json` | 5,662 | `abdc5d89fdac08638f4877f9a44dceb9356d789741bd93981cce4a9b6825d9c1` | none |
| `data/manifests/wyscout/v5/silver/b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79.manifest.json` | 9,618 | `089673ff01edd7de7b6e5777958d19cbaffaa9f429b042ab4986746d80a7c36a` | exact Bronze manifest path/hash above |
| `data/manifests/wyscout/v5/gold/b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79.manifest.json` | 5,705 | `08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068` | exact Silver manifest path/hash above |

Each Silver entry declares both Bronze artifacts as ordered parents. The Gold entry
declares all four Silver artifacts as ordered parents. Physical readback reproduced both
parent edges and every entry size, row count and physical digest. The build also binds
code manifest SHA-256
`c94e650146a982174820ba694a2dcd1b20dc6648426527213bf2e6de09861c2c`.

## Retained canonical physical artifacts

Paths are exact repository-relative paths. `Semantic` is the manifest semantic digest;
`Logical` is the reconstructed logical-byte digest retained by the accepted health report.

| Role / exact path | Rows | Bytes | Physical SHA-256 | Semantic SHA-256 | Logical SHA-256 |
| --- | ---: | ---: | --- | --- | --- |
| `BRONZE_REJECTED_FIELD`<br>`data/working/wyscout/v5/bronze/build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/quarantine/rejected-field/record_kind=action/source_sha256=301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad/part-00000.parquet` | 3,544 | 216,212 | `b2dc4e9265edb79402b19b739be2167dd2bdcaea9afdf9c1b9304953d9f2278e` | `2d0d05c88e00aa2484215f691f9ce7233324e8f0dbd9ea98e86e16e385c08825` | `7f0a9a567ee81cbfe652422d09208679de8bc2a2f80a699b198a920c0d979384` |
| `BRONZE_KNOWN_RECORD`<br>`data/working/wyscout/v5/bronze/build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/records/record_kind=action/source_sha256=301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad/part-00000.parquet` | 1,768 | 312,847 | `e48b203df0d2b83d53af9340cc76ec42a0bb138b5e9608284718d9f6854e9aaf` | `4186f51a8694be1ca4699baf0f3c77e24b2206cc63f18bb7954074cc186d76ca` | `749e51f850372dfd610ffaf2037c8520e94282bca2eeac20f7ef582181cc7faa` |
| `SILVER_ACTION`<br>`data/working/wyscout/v5/silver/build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/action/source_partition=england/part-00000.parquet` | 13 | 255,763 | `89e9645d9715fc155f09a5dae14ac261233aa7599b8266cbcef6a0b5eb86f53a` | `9d98a59a82a45bf077e72dfdb26545d24f3e718d3c8266b085ec95a03bba22d3` | `e6d7e2d1abcd6cc4595b0453797ccd5bb22577c3ed384231eacc5aface27f3b9` |
| `SILVER_LINEUP_STINT`<br>`data/working/wyscout/v5/silver/build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/lineup-stint/source_partition=england/part-00000.parquet` | 1 | 95,873 | `b05e1573cfee6cb3d2a44b675e72917dac70562af17e85494e2948934d15bda2` | `d5a83d1a820ec5197e18709b2ed966824c6edf836926cd8faddeab8617145c08` | `dbfb8c0befb5633d00191fd7680d90bd7af28c9df617ba1cc76442c2c0baac7b` |
| `SILVER_PLAYER_MATCH_FACT`<br>`data/working/wyscout/v5/silver/build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/player-match-fact/source_partition=england/part-00000.parquet` | 1 | 773,862 | `5b8bb0d0dcc1caf9709a1706041110ebadfd3ac14a590fefc4622cc5c41fa1da` | `a8db5735a2f0ec1ee37d46e9dc2985bb4d20b2ef08fc70acfc4e4eec38af5a0f` | `bd7c92d470bfb036a44057e014acd79d55aef4ed430086edb654e767327fb913` |
| `SILVER_POSSESSION`<br>`data/working/wyscout/v5/silver/build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/possession/source_partition=england/part-00000.parquet` | 2 | 329,897 | `a65461738eb21211cb9695af5bbdad9a28ea5f1280de2a3ae79559a555978878` | `bf1114a1d1b2b6325e3656aed297d5f3f7ec872b1485b47c65cb5c47a617417a` | `681f027ed5406f0e39b7c80bf25d5f093c64e111ef0df1fd62e4a717f30d9d5f` |
| `GOLD_PLAYER_WINDOW`<br>`data/working/wyscout/v5/gold/build_id=b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79/player-window/competition_id=cb5c5317-fa4a-571e-93dc-ef6ce482eab7/window_definition_id=a0af8d56-e41d-5467-b46e-82887c4861e0/window_start_utc=20170811T000000000000Z/window_end_utc=20170812T000000000000Z/feature_cutoff_ts=20260801T000000000000Z/part-00000.parquet` | 1 | 949,971 | `6e49b4322c766352fdc427b8d35d73ddaed036d0bd19f1d65435fe3a72edcd17` | `f1751b4f1ff7911ad339fa1954cd5c88483fc09c733547dba87d7aa301c1bffa` | `ef6a57e33a9702f48496570a05fba7f70b7478eb25a30902b75bc9ad4b594cc6` |

### Physical schemas and temporal fields

Parquet footer readback found these exact schema-version values:

- Bronze known record: `w04-wyscout-bronze-known-record-v1`; top level
  `schema_version, build_id, tenant_context, source_row, raw_record,
  raw_record_sha256, measured_raw_fields, admission, classification, lineage`.
- Bronze rejected field: `w04-wyscout-bronze-rejected-field-v1`; top level
  `schema_version, build_id, tenant_context, source_row, record_kind, json_path,
  original_value, original_value_sha256, measured_json_type,
  action_event_taxonomy_id, decision, reason_code, field_authority,
  classification, lineage`.
- Silver action: `w04-wyscout-silver-action-v1`; grain/key fields include
  `action_source_id, action_id, source_event_record_id, match_id, competition_id,
  player_id, team_id, action_event_taxonomy_id, action_subevent_taxonomy_id,
  action_period_code, period_rank, period_elapsed_seconds, source_record_ordinal,
  action_tag_ids, action_positions, possession_predicate_state,
  possession_period_sequence, possession_eligibility_state, occurrence_precision,
  occurrence_utc`, with common build/source/lineage fields.
- Silver lineup stint: `w04-wyscout-silver-lineup-stint-v1`; grain/key fields
  `lineup_stint_id, match_id, player_id, team_id, start_interval, end_interval,
  lower_bound_minutes, upper_bound_minutes, right_censored, elapsed_minutes,
  per90_eligible, suppression_reason`, with common build/source/lineage fields.
- Silver possession: `w04-wyscout-silver-possession-v1`; grain/key fields
  `possession_id, match_id, action_period_code, team_id, contributing_actions,
  action_ids, first_action_order, last_action_order, project_taxonomy_state,
  provider_native_claim`, with common build/source/lineage fields.
- Silver player-match fact: `w04-wyscout-player-match-fact-v1`; grain/key fields
  `source_manifest_id, match_id, player_id, competition_id, season_id,
  match_start_utc, match_team_id, lineup_evidence_present,
  contributing_lineup_stints, contributing_actions, contributing_possessions,
  action_count, coordinate_known_action_count,
  resolved_possession_action_count, right_censored_or_uncertain,
  elapsed_minutes, per90_eligible, coverage, applicability, temporal_proof`, with
  common build/source/lineage fields.
- Gold: `w04-wyscout-gold-player-window-v1`; grain/key fields `player_id,
  competition_id, season_id, role_context_id, role_context_version,
  role_context_state, window_definition_id, window_start_utc, window_end_utc,
  feature_cutoff_ts, dependency_lineage_hash, feature_schema_hash,
  temporal_proof, coverage, applicability, features,
  contributing_player_match_facts, contributing_player_match_keys`, with common
  build/source/lineage fields.

Nested schemas retain source-row references, classification, source authority,
authority clocks and dependency lineage. Thirty non-coverage decimals use the lossless
`decimal128(22,18)` value / `int8` exponent / `bool` negative-zero structure; six
coverage decimals remain canonical UTF-8.

The one Silver player-match starts `2017-08-11T18:45:00Z`. The one Gold window is
`2017-08-11T00:00:00Z` through `2017-08-12T00:00:00Z` with feature cutoff
`2026-08-01T00:00:00Z`. Its temporal receipt is `STRICT_BEFORE_CUTOFF_PASS`. Silver and
Gold rows declare `construction_authority_state=semantic_only_unchecked`; the accepted
W04 health evidence separately records byte-level readback and complete proof execution.
That state and proof scope must not be broadened into a population claim.

## W04 proof coverage is not W09 population coverage

The one Gold row has four supported result-independent counts: action count 2,
known-coordinate action count 2, match count 1 and resolved-possession action count 2.
Its identity `3/3`, lineup `1/1`, action `2/2`, coordinate `2/2`, possession `2/2` and
temporal `8/8` coverage ratios are internally complete for that one row. It binds 868
source-row references and one player-match fact, not 3,071,395 actions or the eligible
player population. Applicability is `research_only` because the lineup/minutes evidence
is `RIGHT_CENSORED_OR_UNCERTAIN`; exact minutes and per-90 are unsupported.

## Missing canonical products and builder reconciliation questions

The following are concretely absent and must be produced before G-RW1:

1. Full five-partition canonical Bronze records/quarantine; the retained Bronze is one
   English proof slice.
2. Full canonical match/action/lineup-stint/possession/player-match tables across all
   1,826 matches; the retained Silver contains 13 actions, one stint, two possessions and
   one player-match fact.
3. A unique, versioned player-season/window feature matrix with one eligibility outcome
   per resolved catalogue player, declared minutes/exposure, coverage, missingness,
   temporal cutoff, feature capability and exact source/canonical lineage.
4. A population-wide Gold product; the retained Gold has one row and four count features.
5. A versioned eligibility ledger, feature-matrix manifest and index inputs that prove no
   unresolved, zero-actor, synthetic, stale or duplicate candidate row is admitted.

The full feature-matrix builder must close these exact reconciliation questions and record
the answer/count for every branch:

- Starting from 3,603 resolved source-catalogue players, which are referenced by admitted
  match lineup evidence, have valid historical team/season membership, have usable
  exposure, meet the minimum-minutes policy, and have every required feature? The final
  included count plus mutually exclusive exclusion counts must equal 3,603.
- How are the 607 resolved catalogue players with no lineup/event evidence represented in
  the eligibility ledger, and how are the 1,035 without event evidence prevented from
  receiving fabricated zero-performance profiles?
- Are the 15 absent-master IDs and `player:0` excluded fail-closed at every canonical and
  retrieval boundary, with their 23 review rows and 226,041 rejected source-row
  references still auditable?
- What exact exposure is defensible when match period terminals are absent or censored?
  The builder must define lower/upper-bound, censoring and minimum-minutes semantics; it
  may not silently claim exact minutes or per-90 support from W04 evidence.
- What is the player-season/window key when a player appears for multiple teams, and how
  are transfers/team history derived from match evidence rather than unversioned
  `currentTeamId`?
- Which feature concepts are available from events alone, which require reconstructed
  possessions/lineups/coordinates, and what deterministic missingness or suppression
  state applies when a dependency is absent?
- What full-season window start/end and feature cutoff are used, and does every selected
  match, source availability, identity authority and schema authority satisfy the chosen
  cutoff without pretending v5 was knowable before `2020-01-28T14:24:27Z`?
- Does each canonical action preserve partition/match identity and zero duplicate action
  IDs; do event and match sets remain aligned in all five leagues after transformation?
- Does the matrix enforce exactly one row per declared player-season/window grain and
  reconcile unique canonical IDs, teams, matches, action coverage and missingness against
  this report?
- Does every matrix/index manifest bind source snapshot, source completion, identity
  bundle, canonical build, feature schema, eligibility policy, code and physical/semantic
  checksums, and fail closed on any stale or incompatible version?
- Can the interactive candidate population be proven to contain only governed historical
  Wyscout rows, with synthetic fixtures impossible outside automated test mode?

Until these questions are answered by a materialised and independently reviewed build,
G-RW1 remains open. This inventory supports engineering of the historical research
workbench; it does not establish football relevance, current-market coverage, recruitment
usefulness or G-RW4.

## Readback method

The inventory used only local read operations. It:

- hashed and sized all retained source payloads and their 18 retention sidecars;
- verified the source snapshot/completion manifests and completion-index content address;
- streamed all admitted event and match JSON to reconcile row and referenced-identity
  counts without writing derived data;
- hashed and summarised the 91 MB identity bundle and queue, including duplicate checks;
- opened every Parquet footer to confirm row count, schema and physical size, and compared
  every artifact hash and parent edge to the retained layer manifests; and
- compared the retained semantic/logical digests and temporal/coverage claims to the
  accepted W04 health evidence and dataset card.

No external source, provider account, network service, current licensed provider,
synthetic product row or destructive action was used.

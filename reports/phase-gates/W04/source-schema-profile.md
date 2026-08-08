# W04 Wyscout v5 source schema profile

> Measured aggregate evidence only. No raw records, player names, or inferred semantics.

## Provenance and scope

| Evidence | Measured/declaration value |
| --- | --- |
| source_id | wyscout-soccer-match-events-figshare-v5 |
| completion state | complete |
| classification | wyscout_figshare_v5_cc_by_4 |
| licence_id | CC-BY-4.0 |
| completion manifest SHA-256 | 69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1 |
| source_available_at | 2020-01-28T14:24:27Z |
| acquired_at | 2026-07-29T15:51:08.598589Z |
| admitted archive-member paths profiled | 10 |
| scope-excluded archive entries not opened | 4 |
| production source root | data/source/wyscout/v5 |
| production output | reports/phase-gates/W04/source-schema-profile.md |
| direct objects opened | competitions.json; teams.json; players.json; eventid2name.csv; tags2name.csv |

The profiler resolved source-data paths only from `object_path` or `member_path` values in the completion manifest. It has no ZIP-reading or network code. ZIP objects and scope-excluded entries were not opened.

### Completion-declared durable inventory

| Kind | Logical name | Completion-declared logical path | Bytes | SHA-256 | Profile access |
| --- | --- | --- | --- | --- | --- |
| completion source object | competitions.json | objects/competitions.json | 1209 | 39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1 | opened |
| completion source object | eventid2name.csv | objects/eventid2name.csv | 1001 | ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842 | opened |
| completion source object | events.zip | objects/events.zip | 77323413 | 877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45 | not opened |
| completion source object | matches.zip | objects/matches.zip | 645097 | c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9 | not opened |
| completion source object | players.json | objects/players.json | 1737347 | 877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e | opened |
| completion source object | tags2name.csv | objects/tags2name.csv | 1754 | e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922 | opened |
| completion source object | teams.json | objects/teams.json | 27404 | 9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d | opened |
| separately durable admitted member of events.zip | events_England.json | archive-members/events_England.json | 188888614 | 301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad | opened |
| separately durable admitted member of events.zip | events_France.json | archive-members/events_France.json | 186374196 | 18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317 | opened |
| separately durable admitted member of events.zip | events_Germany.json | archive-members/events_Germany.json | 152916631 | 2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3 | opened |
| separately durable admitted member of events.zip | events_Italy.json | archive-members/events_Italy.json | 190544685 | b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84 | opened |
| separately durable admitted member of events.zip | events_Spain.json | archive-members/events_Spain.json | 184164406 | b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154 | opened |
| separately durable admitted member of matches.zip | matches_England.json | archive-members/matches_England.json | 1694720 | 620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29 | opened |
| separately durable admitted member of matches.zip | matches_France.json | archive-members/matches_France.json | 1707222 | 851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea | opened |
| separately durable admitted member of matches.zip | matches_Germany.json | archive-members/matches_Germany.json | 1377328 | 6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9 | opened |
| separately durable admitted member of matches.zip | matches_Italy.json | archive-members/matches_Italy.json | 2019196 | afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725 | opened |
| separately durable admitted member of matches.zip | matches_Spain.json | archive-members/matches_Spain.json | 1705380 | 9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce | opened |

Object size/digest rows above are completion declarations bound by the manifest SHA-256. Every opened direct object and durable admitted member was also verified during profiling. Archive objects were not opened.

## Dataset counts

| Dataset/evidence | Count |
| --- | --- |
| competitions | 7 |
| teams | 142 |
| players | 3603 |
| matches | 1826 |
| events | 3071395 |
| match admitted members | 5 |
| event admitted members | 5 |
| event mapping CSV rows | 36 |
| tag mapping CSV rows | 59 |
| distinct competition wyId values | 7 |
| distinct team wyId values | 142 |
| distinct player wyId values | 3603 |
| distinct match wyId values | 1826 |
| distinct competition IDs referenced by admitted matches | 5 |
| distinct team IDs referenced by admitted matches | 98 |
| distinct event record id values | 3071395 |
| duplicate event record id values | 0 |

### Per-member row counts

| Member | Rows |
| --- | --- |
| events_England.json | 643150 |
| events_France.json | 632807 |
| events_Germany.json | 519407 |
| events_Italy.json | 647372 |
| events_Spain.json | 628659 |
| matches_England.json | 380 |
| matches_France.json | 380 |
| matches_Germany.json | 306 |
| matches_Italy.json | 380 |
| matches_Spain.json | 380 |

### Event-member to match-member partition equality

| Partition | Match member | Distinct match wyId | Event member | Distinct event matchId | Set relation |
| --- | --- | --- | --- | --- | --- |
| England | matches_England.json | 380 | events_England.json | 380 | equal |
| France | matches_France.json | 380 | events_France.json | 380 | equal |
| Germany | matches_Germany.json | 306 | events_Germany.json | 306 | equal |
| Italy | matches_Italy.json | 380 | events_Italy.json | 380 | equal |
| Spain | matches_Spain.json | 380 | events_Spain.json | 380 | equal |

## Measured relationships

| Relationship | Observed | Mapped | Unmapped | Zero-valued | Invalid/missing |
| --- | --- | --- | --- | --- | --- |
| match competitionId → competitions.wyId | 1826 | 1826 | 0 | 0 | 0 |
| teamsData key → teams.wyId | 3652 | 3652 | 0 | 0 | 0 |
| teamsData teamId → teams.wyId | 3652 | 3652 | 0 | 0 | 0 |
| event matchId → matches.wyId | 3071395 | 3071395 | 0 | 0 | 0 |
| event teamId → teams.wyId | 3071395 | 3071395 | 0 | 0 | 0 |
| event playerId → players.wyId | 3071395 | 2845357 | 0 | 226038 | 0 |
| event eventId → event mapping event | 3071395 | 3071395 | 0 | 0 | 0 |
| event subEventId → event mapping subevent | 3071395 | 3063574 | 0 | 0 | 7821 |
| event tag id → tag mapping Tag | 4336816 | 4336816 | 0 | 0 | 0 |
| lineup playerId → players.wyId | 40172 | 40172 | 0 | 0 | 0 |
| bench playerId → players.wyId | 28715 | 28692 | 23 | 0 | 0 |
| substitution playerIn → players.wyId | 10423 | 10415 | 8 | 0 | 0 |
| substitution playerOut → players.wyId | 10423 | 10423 | 0 | 0 | 0 |

`Zero-valued` is reported separately where measured for event player/team IDs. No meaning is assigned to zero.

### Match-bound and player-match aggregate evidence

| Evidence | Count |
| --- | --- |
| matches with teamsData entry count other than two | 0 |
| teamsData key/teamId mismatches | 0 |
| event teamId not in referenced match teamsData | 0 |
| event/member match-partition mismatches | 0 |
| duplicate match wyId values | 0 |
| non-zero event player references | 2845357 |
| distinct non-zero event player-match pairs | 50522 |
| matches with at least one non-zero event player | 1826 |

Player-match pairs above are event-presence aggregates only. They do not establish lineup status, time played, role context, minutes, or per-90 eligibility.

## Period, clock, and minutes evidence

| matchPeriod aggregate | Events | Numeric eventSec | Missing/invalid eventSec | eventSec min | eventSec max | Match-period maxima count | Min of maxima | Max of maxima |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1H | 1541033 | 1541033 | 0 | 0.020000000000010232 | 3302.282734 | 1826 | 2576.313699 | 3302.282734 |
| 2H | 1530362 | 1530362 | 0 | 0 | 3537.3560610000004 | 1826 | 2649.6185100000002 | 3537.3560610000004 |

| Evidence | Measured value |
| --- | --- |
| match duration field types | string:1826 |
| match dateutc field types | string:1826 |
| dateutc values matching YYYY-MM-DD HH:MM:SS | 1826 |
| dateutc values not matching YYYY-MM-DD HH:MM:SS | 0 |
| maximum measured eventSec decimal scale | 18 |
| formation structures present | 3652 |
| lineup rows | 40172 |
| bench rows | 28715 |
| substitution rows | 10423 |
| numeric substitution minute values | 10423 |
| missing/invalid substitution minute values | 0 |
| substitution minute minimum | 3 |
| substitution minute maximum | 97 |
| literal-null-string substitution containers | 6 |
| exact period terminal supported | no |
| exact player minutes supported | no |
| per-90 denominator supported | no |
| duration category Regular | 1826 |
| substitution container shape array | 3646 |
| substitution container shape string | 6 |

The event maxima are observed lower-bound evidence only. They do not establish an exact period terminal, elapsed match duration, stoppage-time rule, period-start UTC, or player minutes. Consequently, player-minute and per-90 products remain unsupported and must stay suppressed.

## Position cardinality and coordinate-domain evidence

| Evidence | Count |
| --- | --- |
| positions with one coordinate | 709 |
| positions with two coordinates | 3070686 |
| positions with other cardinality | 0 |
| coordinate values outside inclusive 0..100 | 3 |

| Axis | Numeric values | Missing/invalid | Lowest observed | Highest observed | Outside inclusive 0..100 |
| --- | --- | --- | --- | --- | --- |
| x | 6142081 | 0 | -1 | 100 | 1 |
| y | 6142081 | 0 | 0 | 101 | 2 |

Out-of-range coordinates are retained as anomaly evidence. The profiler does not clamp, repair, or discard them.

## CSV field shapes

### event mapping

| Column | Present | Empty | Lexical shapes |
| --- | --- | --- | --- |
| event | 36 | 0 | integer:36 |
| event_label | 36 | 0 | string:36 |
| subevent | 36 | 0 | integer:36 |
| subevent_label | 36 | 0 | string:36 |

### tag mapping

| Column | Present | Empty | Lexical shapes |
| --- | --- | --- | --- |
| Description | 59 | 0 | string:59 |
| Label | 59 | 0 | string:59 |
| Tag | 59 | 0 | integer:59 |

## JSON field presence and type shapes

### competitions

| Path | Observations | Nulls | Measured types |
| --- | --- | --- | --- |
| $ | 7 | 0 | object:7 |
| $.area | 7 | 0 | object:7 |
| $.area.alpha2code | 7 | 0 | string:7 |
| $.area.alpha3code | 7 | 0 | string:7 |
| $.area.id | 7 | 0 | integer:2, string:5 |
| $.area.name | 7 | 0 | string:7 |
| $.format | 7 | 0 | string:7 |
| $.name | 7 | 0 | string:7 |
| $.type | 7 | 0 | string:7 |
| $.wyId | 7 | 0 | integer:7 |

### teams

| Path | Observations | Nulls | Measured types |
| --- | --- | --- | --- |
| $ | 142 | 0 | object:142 |
| $.area | 142 | 0 | object:142 |
| $.area.alpha2code | 142 | 0 | string:142 |
| $.area.alpha3code | 142 | 0 | string:142 |
| $.area.id | 142 | 0 | integer:44, string:98 |
| $.area.name | 142 | 0 | string:142 |
| $.city | 142 | 0 | string:142 |
| $.name | 142 | 0 | string:142 |
| $.officialName | 142 | 0 | string:142 |
| $.type | 142 | 0 | string:142 |
| $.wyId | 142 | 0 | integer:142 |

### players

| Path | Observations | Nulls | Measured types |
| --- | --- | --- | --- |
| $ | 3603 | 0 | object:3603 |
| $.birthArea | 3603 | 0 | object:3603 |
| $.birthArea.alpha2code | 3603 | 0 | string:3603 |
| $.birthArea.alpha3code | 3603 | 0 | string:3603 |
| $.birthArea.id | 3603 | 0 | integer:1295, string:2308 |
| $.birthArea.name | 3603 | 0 | string:3603 |
| $.birthDate | 3603 | 0 | string:3603 |
| $.currentNationalTeamId | 3603 | 0 | integer:1357, string:2246 |
| $.currentTeamId | 3603 | 91 | integer:3468, null:91, string:44 |
| $.firstName | 3603 | 0 | string:3603 |
| $.foot | 3603 | 0 | string:3603 |
| $.height | 3603 | 0 | integer:3603 |
| $.lastName | 3603 | 0 | string:3603 |
| $.middleName | 3603 | 0 | string:3603 |
| $.passportArea | 3603 | 0 | object:3603 |
| $.passportArea.alpha2code | 3603 | 0 | string:3603 |
| $.passportArea.alpha3code | 3603 | 0 | string:3603 |
| $.passportArea.id | 3603 | 0 | integer:1295, string:2308 |
| $.passportArea.name | 3603 | 0 | string:3603 |
| $.role | 3603 | 0 | object:3603 |
| $.role.code2 | 3603 | 0 | string:3603 |
| $.role.code3 | 3603 | 0 | string:3603 |
| $.role.name | 3603 | 0 | string:3603 |
| $.shortName | 3603 | 0 | string:3603 |
| $.weight | 3603 | 0 | integer:3603 |
| $.wyId | 3603 | 0 | integer:3603 |

### matches

| Path | Observations | Nulls | Measured types |
| --- | --- | --- | --- |
| $ | 1826 | 0 | object:1826 |
| $.competitionId | 1826 | 0 | integer:1826 |
| $.date | 1826 | 0 | string:1826 |
| $.dateutc | 1826 | 0 | string:1826 |
| $.duration | 1826 | 0 | string:1826 |
| $.gameweek | 1826 | 0 | integer:1826 |
| $.label | 1826 | 0 | string:1826 |
| $.referees | 1826 | 0 | array:1826 |
| $.referees[] | 7482 | 0 | object:7482 |
| $.referees[].refereeId | 7482 | 0 | integer:7482 |
| $.referees[].role | 7482 | 0 | string:7482 |
| $.roundId | 1826 | 0 | integer:1826 |
| $.seasonId | 1826 | 0 | integer:1826 |
| $.status | 1826 | 0 | string:1826 |
| $.teamsData | 1826 | 0 | object:1826 |
| $.teamsData.* | 3652 | 0 | object:3652 |
| $.teamsData.*.coachId | 3652 | 0 | integer:3652 |
| $.teamsData.*.formation | 3652 | 0 | object:3652 |
| $.teamsData.*.formation.bench | 3652 | 0 | array:3652 |
| $.teamsData.*.formation.bench[] | 28715 | 0 | object:28715 |
| $.teamsData.*.formation.bench[].goals | 28715 | 0 | string:28715 |
| $.teamsData.*.formation.bench[].ownGoals | 28715 | 0 | string:28715 |
| $.teamsData.*.formation.bench[].playerId | 28715 | 0 | integer:28715 |
| $.teamsData.*.formation.bench[].redCards | 28715 | 0 | string:28715 |
| $.teamsData.*.formation.bench[].yellowCards | 28715 | 0 | string:28715 |
| $.teamsData.*.formation.lineup | 3652 | 0 | array:3652 |
| $.teamsData.*.formation.lineup[] | 40172 | 0 | object:40172 |
| $.teamsData.*.formation.lineup[].goals | 40172 | 0 | string:40172 |
| $.teamsData.*.formation.lineup[].ownGoals | 40172 | 0 | string:40172 |
| $.teamsData.*.formation.lineup[].playerId | 40172 | 0 | integer:40172 |
| $.teamsData.*.formation.lineup[].redCards | 40172 | 0 | string:40172 |
| $.teamsData.*.formation.lineup[].yellowCards | 40172 | 0 | string:40172 |
| $.teamsData.*.formation.substitutions | 3652 | 0 | array:3646, string:6 |
| $.teamsData.*.formation.substitutions[] | 10423 | 0 | object:10423 |
| $.teamsData.*.formation.substitutions[].minute | 10423 | 0 | integer:10423 |
| $.teamsData.*.formation.substitutions[].playerIn | 10423 | 0 | integer:10423 |
| $.teamsData.*.formation.substitutions[].playerOut | 10423 | 0 | integer:10423 |
| $.teamsData.*.hasFormation | 3652 | 0 | integer:3652 |
| $.teamsData.*.score | 3652 | 0 | integer:3652 |
| $.teamsData.*.scoreET | 3652 | 0 | integer:3652 |
| $.teamsData.*.scoreHT | 3652 | 0 | integer:3652 |
| $.teamsData.*.scoreP | 3652 | 0 | integer:3652 |
| $.teamsData.*.side | 3652 | 0 | string:3652 |
| $.teamsData.*.teamId | 3652 | 0 | integer:3652 |
| $.venue | 1826 | 0 | string:1826 |
| $.winner | 1826 | 0 | integer:1826 |
| $.wyId | 1826 | 0 | integer:1826 |

### events

| Path | Observations | Nulls | Measured types |
| --- | --- | --- | --- |
| $ | 3071395 | 0 | object:3071395 |
| $.eventId | 3071395 | 0 | integer:3071395 |
| $.eventName | 3071395 | 0 | string:3071395 |
| $.eventSec | 3071395 | 0 | integer:18, number:3071377 |
| $.id | 3071395 | 0 | integer:3071395 |
| $.matchId | 3071395 | 0 | integer:3071395 |
| $.matchPeriod | 3071395 | 0 | string:3071395 |
| $.playerId | 3071395 | 0 | integer:3071395 |
| $.positions | 3071395 | 0 | array:3071395 |
| $.positions[] | 6142081 | 0 | object:6142081 |
| $.positions[].x | 6142081 | 0 | integer:6142081 |
| $.positions[].y | 6142081 | 0 | integer:6142081 |
| $.subEventId | 3071395 | 0 | integer:3063574, string:7821 |
| $.subEventName | 3071395 | 0 | string:3071395 |
| $.tags | 3071395 | 0 | array:3071395 |
| $.tags[] | 4336816 | 0 | object:4336816 |
| $.tags[].id | 4336816 | 0 | integer:4336816 |
| $.teamId | 3071395 | 0 | integer:3071395 |

## Nullable and mixed-type evidence

| Dataset | Path | Observations | Nulls | Measured types |
| --- | --- | --- | --- | --- |
| competitions | $.area.id | 7 | 0 | integer:2, string:5 |
| teams | $.area.id | 142 | 0 | integer:44, string:98 |
| players | $.birthArea.id | 3603 | 0 | integer:1295, string:2308 |
| players | $.currentNationalTeamId | 3603 | 0 | integer:1357, string:2246 |
| players | $.currentTeamId | 3603 | 91 | integer:3468, null:91, string:44 |
| players | $.passportArea.id | 3603 | 0 | integer:1295, string:2308 |
| matches | $.teamsData.*.formation.substitutions | 3652 | 0 | array:3646, string:6 |
| events | $.eventSec | 3071395 | 0 | integer:18, number:3071377 |
| events | $.subEventId | 3071395 | 0 | integer:3063574, string:7821 |

## Design-facing unknowns and limits

- Identity: only within-snapshot ID membership was measured. No canonical cross-provider or cross-version identity evidence was profiled.
- Possession: field/type and mapping evidence does not prove possession boundaries, ownership rules, or event-to-possession semantics.
- Minutes: no exact period terminal or period-start UTC evidence was established. Lineup, bench, substitution-minute, duration-field, and eventSec aggregates are insufficient on their own to derive exact player minutes.
- Coverage: counts apply only to completion-declared admitted members and the five direct objects opened above. Scope-excluded archive entries remain outside evidence.
- Reconciliation: mapped, unmapped, zero-valued, and invalid/missing counts above are preserved separately; no repair, coercion, or semantic mapping was guessed.
- Labels: mapping CSV structure and numeric-key membership were measured, but label text was not emitted into this report.

## Reproduction

```text
uv run python scripts/profile_wyscout_v5.py --check
```

Production CLI source, output, and completion-digest overrides are rejected unless they resolve exactly to the repository-approved values recorded above. Internal fixture APIs remain parameterised for fabricated tests.

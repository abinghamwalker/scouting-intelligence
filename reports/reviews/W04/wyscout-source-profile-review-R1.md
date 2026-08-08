# W04 Wyscout source-profile independent review — R1

## Review decision

**Recommendation to master: REWORK.**

This is an independent-verifier recommendation, not task or phase approval. The master
retains gate authority.

The profile is deterministic, completion-digest-bound, aggregate-only, local-only, and
correct for the aggregate relationships it reports. It is not complete enough to serve
as the measured authority for the pending W04 schema-design R3 corrections. The packet
acceptance suite deliberately fails one completeness assertion and passes the other
nine tests.

## Scope and method

The producer script, producer tests, tracked profile, completion evidence, and
`data/source/wyscout/v5/**` were treated as immutable. The reviewer independently
streamed every completion-declared direct JSON object and all ten admitted archive
members. The two ZIP objects and four excluded competition members were not opened.
Every streamed file was checked against its completion-declared byte size and SHA-256.

The recomputation used `Decimal` for JSON numbers, bounded its undecoded JSON item
buffer to 16 MiB, retained only aggregate counters and bounded ID sets, and emitted no
raw record or player name. The producer's check mode was also challenged for static
network/archive imports, source/report mutation, and byte stability.

## Findings requiring rework

### P1 — Exact admitted paths and completion bridge are absent

The profile records the completion-manifest digest and counts opened paths, but it does
not emit the seven completion-declared object paths, the ten admitted member paths, the
completion classification, or `licence_id`. The pending schema-design R3 packet is
forbidden from reading `data/**`, yet corrections 2 and 3 require those exact paths and
a non-circular completion-to-layer bridge including classification and rights.

Bounded correction:

- add an aggregate provenance table copied exactly from the verified completion
  manifest with classification, licence ID, each object/member logical path, byte
  size, and digest;
- keep the completion-manifest digest as the root binding;
- distinguish archive objects from separately durable admitted members;
- do not emit signed URLs, raw records, or inferred semantics.

### P1 — Aggregate-only inventory does not prove five-league admitted coverage

The direct masters contain seven competitions and 142 teams. The admitted domestic
match members reference only five competition IDs and 98 team IDs. The tracked profile
reports only the direct 7/142 counts and global match/event totals. It omits the
per-member rows and therefore cannot prove that each league partition is present,
non-empty, non-duplicated, or aligned with its event member.

Independent admitted-member counts are:

| Member | Rows |
| --- | ---: |
| `matches_England.json` | 380 |
| `matches_France.json` | 380 |
| `matches_Germany.json` | 306 |
| `matches_Italy.json` | 380 |
| `matches_Spain.json` | 380 |
| `events_England.json` | 643150 |
| `events_France.json` | 632807 |
| `events_Germany.json` | 519407 |
| `events_Italy.json` | 647372 |
| `events_Spain.json` | 628659 |

For every suffix, the distinct `matchId` set in the event member exactly equals the
`wyId` set in the corresponding match member. The profile must publish this aggregate
partition evidence before R3 coverage formulae and applicability can be frozen.

### P1 — Event identity and match-bound fact prerequisites are missing

The profile reports distinct match `wyId` values but treats event `eventId` only as a
taxonomy relation. The event record's actual identity field is `id`. Independent
recomputation found 3,071,395 distinct event `id` values and zero duplicates.

The profile also proves global membership of event team and match IDs separately, but
does not prove the match-bound relation needed by `player_match_fact`. Independent
recomputation found:

- zero events whose `matchId` is absent;
- zero event/member partition mismatches;
- zero events whose `teamId` is outside the referenced match's `teamsData`;
- zero `teamsData` key-to-`teamId` mismatches;
- zero matches with a team-entry count other than two.

Bounded correction: report event-record identity uniqueness and these match-bound
relations, then add the aggregate player-match grain/reconciliation evidence required
to design the Silver fact. Do not infer minutes or role context from event presence.

### P2 — Temporal precision and minutes shapes are under-profiled

The producer parses `eventSec` as binary `float` and formats extrema with six
significant digits. Exact JSON lexical recomputation found a maximum decimal scale of
18, including binary-artifact tails. Therefore the current profile is insufficient to
choose a precision-aware period-relative representation for R3 correction 1.

Additional measured facts omitted from the profile are:

- all 1,826 `dateutc` values parse as `YYYY-MM-DD HH:MM:SS`;
- all 1,826 duration values are the literal category `Regular`;
- formation substitutions comprise 3,646 arrays and six literal `"null"` strings;
- period counts are 1,541,033 `1H` and 1,530,362 `2H` events.

The tracked report correctly states that observed period maxima do not establish exact
period terminals, period-start UTC, elapsed duration, or player minutes. That unknown
must remain explicit. Exact minutes and per-90 products must remain suppressed unless a
separate accepted authority establishes a denominator.

### P2 — Coordinate domain anomalies are hidden

Positions contain 709 one-coordinate arrays and 3,070,686 two-coordinate arrays.
Three coordinate values are outside the nominal inclusive 0–100 domain: two `y=101`
values and one `x=-1` value. The profile currently emits field/type shape only and
does not expose array cardinality, coordinate range, or anomaly count.

Bounded correction: add aggregate position cardinality, axis range, and out-of-range
counts. Preserve the three values as invalid/anomalous evidence; do not silently clamp
or repair them.

### P2 — Non-check output is not repository-bounded

Source reads are completion-declared and repository-bounded, and the profiler has
explicit caps for manifest/CSV bytes, JSON buffer, schema paths/depth, periods, and
distinct-ID collections. However, `--output` accepts an arbitrary `Path`, and the
atomic writer calls `os.replace` without proving that the target is the approved
tracked report beneath the project root.

Bounded correction: reject any output other than the resolved approved report path, or
remove the output override. Retain atomic same-directory replacement and check-mode
read-only behavior.

## Independently reconciled aggregate evidence

- Completion manifest SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`.
- Direct records: 7 competitions, 142 teams, 3,603 players.
- Admitted records: 1,826 unique matches and 3,071,395 unique event records.
- Periods: only `1H` and `2H`, with the counts stated above; no invalid `eventSec`.
- Formation rows: 40,172 lineup, 28,715 bench, 10,423 substitutions.
- Relationship exceptions match the tracked report: 23 bench player references and
  8 substitution-in player references are absent from the direct player master;
  substitution-out and lineup references have zero misses.
- Event player IDs: 226,038 zero-valued references and zero non-zero master misses.
- Event taxonomy: every event type maps; 7,821 subtype values are strings rather than
  integers; every integer subtype and all 4,336,816 tag references map.
- Position arrays and anomalies match the figures in the P2 finding above.

## Nine-correction sufficiency challenge

| R3 correction | Profile result | Review conclusion |
| ---: | --- | --- |
| 1 | `eventSec` extrema exist, but exact lexical precision is collapsed | **REWORK** |
| 2 | Completion digest exists, exact object/member paths do not | **REWORK** |
| 3 | Source/time binding exists, classification/licence/file bridge is incomplete | **REWORK** |
| 4 | Honest source-available/acquired clocks are present | Source evidence sufficient; semantic/physical build identity remains design-owned |
| 5 | Possession meaning is explicitly unknown | Sufficient only to require a serial master-owned authority packet; no possession claim is supported |
| 6 | Neutral role-context identity is not source-measurement-dependent | Design-owned; no source contradiction found |
| 7 | Terminal/minutes are correctly unknown, but duration/substitution values are under-profiled | **REWORK** and suppress unsupported per-90 |
| 8 | Global totals exist, but admitted league/member numerators and denominators do not | **REWORK** |
| 9 | Global ID membership exists, but event identity and match-bound/player-match grain do not | **REWORK** |

The report therefore does not yet supply every measured input required by the nine
open R3 corrections. Possession and role-context requirements must not be guessed to
make the profile appear complete.

## Controls that passed

- Completion binding, declared size, and digest verification passed for every opened
  durable object/member.
- The recomputation opened no ZIP object and no excluded European Championship or
  World Cup member.
- The tracked report contains no sampled player name and no raw record.
- Static inspection found no producer import of network or ZIP libraries.
- `profile_wyscout_v5.py --check` returned success; source file sizes/mtimes and report
  bytes were unchanged.
- The tracked profile SHA-256 remained
  `fca42b10f7b3f6053d561c3733b626dd8c92023a7fa5f5c3053cd6dd4260de5f`.
- Repository local-only verification passed with no failures.

## Verification

- `uv run pytest -q tests/unit/test_wyscout_profile.py tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `1`
  - result: `1 failed, 9 passed in 78.51s`
  - the sole failure enumerates the missing completion bridge, paths, per-member
    coverage, event identity, match-bound, temporal, substitution, and coordinate
    evidence.
- `uv run python scripts/profile_wyscout_v5.py --check`
  - exit status: `0`
  - result: profile check passed.
- `uv run ruff format --check tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: file already formatted.
- `uv run ruff check tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: all checks passed.
- `uv run mypy tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: no issues found.
- `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: status `PASS`; failures `[]`.

## Recommendation

**REWORK.** Keep the current report as a valid aggregate inventory, but do not mark the
source-profile prerequisite verified or dispatch schema-design R3 against it. Return
only the bounded producer corrections above, rerun this independent suite, and retain
all unsupported semantics as unknown.


# W04 Wyscout source profile review — R2

## Review decision

**Recommendation to master: ACCEPT.**

This is an independent-verifier recommendation, not task or phase approval. The master
retains gate authority.

The complete R1 recomputation and completeness gate was retained and rerun by a
different reviewer. The independent stream recomputed all profile claims from the
completion-declared durable snapshot rather than trusting producer counters. All six R1
defects are closed, every added R2 challenge passed, and no P0-P2 defect or packet stop
condition was reproduced.

## Scope and method

The verifier read only:

- the canonical completion document;
- the five required non-archive direct objects;
- the ten separately durable admitted match/event members;
- the tracked aggregate report and immutable producer source/tests.

The two ZIP objects and all four excluded member payloads remained unopened. Declared
paths were independently normalized, resolved strictly beneath the source root, checked
against the completion size/SHA-256, and recorded as opened before streaming. The
independent JSON parser used `Decimal` for every non-integral number and bounded
one-record streaming.

No Git command, network/provider call, data mutation, producer/config/script/source/
orchestration/dependency edit, protected fixture, profile-design work, or delegation
occurred.

## Six R1 defect closures

### W04-PROFILE-COMPLETION-BRIDGE-01 — closed

The tracked profile is bound to completion SHA-256
`69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
and now emits:

- classification `wyscout_figshare_v5_cc_by_4`;
- licence ID `CC-BY-4.0`;
- all seven completion source objects with exact logical path, byte count, and SHA-256;
- all ten separately durable admitted members with exact parent archive, logical path,
  byte count, and SHA-256;
- explicit `opened` versus `not opened` access state, distinguishing source ZIP objects
  from admitted durable member payloads.

The independent reviewer reconstructed and matched every exact inventory row.

### W04-PROFILE-PARTITION-COVERAGE-01 — closed

Independent row counts:

| Member | Rows |
| --- | ---: |
| `matches_England.json` | 380 |
| `matches_France.json` | 380 |
| `matches_Germany.json` | 306 |
| `matches_Italy.json` | 380 |
| `matches_Spain.json` | 380 |
| `events_England.json` | 643,150 |
| `events_France.json` | 632,807 |
| `events_Germany.json` | 519,407 |
| `events_Italy.json` | 647,372 |
| `events_Spain.json` | 628,659 |

Each event member's distinct `matchId` set is exactly equal to its paired match
member's distinct `wyId` set. The admitted matches reference exactly five competition
IDs and 98 team IDs, all present in the corresponding direct objects.

### W04-PROFILE-EVENT-IDENTITY-01 — closed

- Event rows: `3,071,395`
- Distinct event-record `id` values: `3,071,395`
- Duplicate event-record `id` values: `0`
- Matches: `1,826`, with zero duplicate `wyId`
- Matches with a teamsData entry count other than two: `0`
- teamsData key/team ID mismatches: `0`
- Event-to-match unmapped: `0`
- Event-member partition mismatches: `0`
- Event team IDs outside the referenced match teamsData: `0`
- Distinct non-zero event player/match pairs: `50,522`
- Matches with at least one non-zero event player: `1,826`

Player/match evidence is explicitly event-presence only. No lineup status, minutes,
role, or per-90 semantics are inferred.

### W04-PROFILE-TEMPORAL-MINUTES-01 — closed

The independent parser preserved exact source decimals:

| Period | Events | eventSec minimum | eventSec maximum | Match maxima | Minimum of maxima | Maximum of maxima |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `1H` | 1,541,033 | `0.020000000000010232` | `3302.282734` | 1,826 | `2576.313699` | `3302.282734` |
| `2H` | 1,530,362 | `0` | `3537.3560610000004` | 1,826 | `2649.6185100000002` | `3537.3560610000004` |

- Missing/invalid `eventSec`: `0`
- Maximum exact decimal scale: `18`
- `dateutc` matching `YYYY-MM-DD HH:MM:SS`: `1,826`
- Unparseable `dateutc`: `0`
- Duration category `Regular`: `1,826`
- Formation structures: `3,652`
- Substitution containers: `3,646` arrays and six literal `"null"` strings
- Substitution rows: `10,423`; minute minimum `3`, maximum `97`

The report correctly marks exact period terminal, exact player minutes, and per-90
denominator support as `no`.

### W04-PROFILE-COORDINATE-DOMAIN-01 — closed

- Positions with one coordinate: `709`
- Positions with two coordinates: `3,070,686`
- Other cardinalities: `0`
- Numeric x/y values: `6,142,081` per axis
- x range: `-1..100`, with one value outside inclusive `0..100`
- y range: `0..101`, with two values outside inclusive `0..100`
- Total retained anomalies: `3`

The report retains these anomalies and explicitly denies clamping, repair, or discard.

### W04-PROFILE-OUTPUT-PATH-01 — closed

The production boundary resolves and requires exactly:

- source: `data/source/wyscout/v5`;
- output: `reports/phase-gates/W04/source-schema-profile.md`;
- completion digest: the reviewed SHA-256 above.

Independent subprocess challenges for an unreviewed source root, unreviewed output path,
and alternate completion digest all returned `1`, emitted the expected boundary error,
created no alternate output, and left the tracked profile unchanged. Internal fixture
APIs remain parameterized, and the atomic same-directory `os.replace` write remains.

## Other independent evidence

### Referential/anomaly evidence

- Direct counts: 7 competitions, 142 teams, 3,603 players
- Match competition/team mapping failures: `0`
- Lineup player mapping failures: `0`
- Bench player IDs absent from players: `23`
- Substitution player-in IDs absent from players: `8`
- Substitution player-out IDs absent from players: `0`
- Zero-valued event player IDs: `226,038`
- Non-zero event player mapping failures: `0`
- Invalid/string event subtype IDs: `7,821`
- Valid subtype mapping failures: `0`
- Event tags: `4,336,816`, all mapped

The report preserves unmapped, zero-valued, and invalid evidence separately without
repair or semantic guessing.

### Privacy and access

The tracked report contains none of the independently collected player names, match
labels, or venue values. It emits aggregate field/type/count evidence only. Static and
runtime checks prove the profiler has no network or ZIP-reading import, opens no ZIP
object, and opens no European Championship or World Cup excluded path.

### Determinism

The tracked report is exactly `18,574` bytes with SHA-256
`569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`.
The security test retained the report bytes and all source file size/mtime values across
check mode. The separate production `--check` regeneration produced identical bytes.

## Schema-design R3 readiness

Every measured input requested by the R2 packet is present: provenance/inventory,
partition scope, event identity, two-team match structure, teamsData equality,
event-to-match/team relations, player/match presence, exact decimal and clock evidence,
substitution shapes, coordinate cardinality/domain, and known anomalies.

Unsupported semantics are explicit: canonical cross-version/provider identity,
possession boundaries/ownership, exact period terminal, exact player minutes, per-90
denominators, and excluded-competition coverage. No guessed input is presented as
design authority.

## Verification

- `uv run pytest -q tests/unit/test_wyscout_profile.py tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `15 passed in 91.69s`
- `uv run python scripts/profile_wyscout_v5.py --check`
  - exit status: `0`
  - result: profile check passed against the approved tracked output
- `uv run ruff format --check tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `1 file already formatted`
- `uv run ruff check tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `All checks passed!`
- `uv run mypy tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: status `PASS`; failures `[]`

## Residual risk

- The evidence is scoped to the frozen completion-declared five domestic partitions;
  excluded competitions remain deliberately outside the profile.
- The profile establishes measured schema and relationship evidence, not source-record
  truth or football-semantic correctness.
- Exact minutes and per-90 products remain unsupported and must remain suppressed until
  separately authoritative rules/evidence exist.
- The master retains task acceptance, schema-design dispatch, phase-gate, and
  checkpoint authority.

## Recommendation

**ACCEPT.** All six R1 defects are closed, the complete independent full-snapshot
recomputation passes, the tracked output is exact and privacy-safe, and no P0-P2 defect
remains. This is an independent recommendation to the master, not self-approval.

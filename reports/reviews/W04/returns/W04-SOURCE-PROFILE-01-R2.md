# Subagent return

## Task

- task_id: `W04-SOURCE-PROFILE-01-R2`
- objective: Close the six returned source-profile defects with exact aggregate provenance,
  partition, event-identity, match-bound, temporal/minutes, coordinate, and production-boundary
  evidence while retaining every R1 control.

## Files changed

- `scripts/profile_wyscout_v5.py`
- `tests/unit/test_wyscout_profile.py`
- `reports/phase-gates/W04/source-schema-profile.md`
- `reports/reviews/W04/returns/W04-SOURCE-PROFILE-01-R2.md`

## Summary

- Closed `W04-PROFILE-COMPLETION-BRIDGE-01`: the report now records exact completion
  classification and licence ID plus all seven source-object and ten separately durable
  admitted-member logical paths, byte sizes, and SHA-256 digests. Archive objects remain
  explicitly marked not opened.
- Closed `W04-PROFILE-PARTITION-COVERAGE-01`: emitted all ten per-member row counts, five
  admitted competition-ID and 98 admitted team-ID scope counts, and exact equality between
  each event member's distinct `matchId` set and the paired match member's `wyId` set.
- Closed `W04-PROFILE-EVENT-IDENTITY-01`: measured 3,071,395 distinct event record `id`
  values with zero duplicates, zero non-two-team matches, zero teamsData key/team-ID
  mismatches, zero event team-to-match exceptions, zero partition exceptions, and 50,522
  distinct non-zero event player-match pairs. The report explicitly treats the pairs as
  event-presence evidence rather than minutes or role context.
- Closed `W04-PROFILE-TEMPORAL-MINUTES-01`: the streaming JSON decoder now uses lossless
  `Decimal` parsing, emits exact period extrema and maximum decimal scale 18, proves all 1,826
  `dateutc` strings exactly match `YYYY-MM-DD HH:MM:SS`, records the 1,826 `Regular` duration
  category, distinguishes 3,646 substitution arrays from six literal `"null"` strings, and
  explicitly suppresses exact terminals, player minutes, and per-90 denominators.
- Closed `W04-PROFILE-COORDINATE-DOMAIN-01`: emitted position-array cardinalities, per-axis
  ranges, and three retained inclusive-0..100 anomalies: one x-axis and two y-axis values.
  No clamping, repair, or discard occurs.
- Closed `W04-PROFILE-OUTPUT-PATH-01`: production CLI source, output, and completion-digest
  values must resolve exactly to repository-approved constants. Parameterised internal
  `build_profile` and streaming APIs remain available for fabricated fixtures; atomic writes
  remain same-directory.
- Retained the completion SHA-256 binding, incremental per-item JSON memory bound, finite
  aggregate caps, aggregate-only privacy, admitted-only reads, per-opened-file size/digest
  verification, excluded/ZIP non-read controls, and deterministic output.

## Tests run

- command:
  `uv run pytest -q tests/unit/test_wyscout_profile.py tests/security/test_w04_wyscout_profile_review.py`
  - exit status: 0
  - result: `10 passed in 89.76s`; includes the retained unchanged independent R1 review gate
- command: `uv run python scripts/profile_wyscout_v5.py --check`
  - exit status: 0
  - result: full source recomputation completed and exact tracked-report bytes matched
- command:
  `uv run ruff format --check scripts/profile_wyscout_v5.py tests/unit/test_wyscout_profile.py`
  - exit status: 0
  - result: `2 files already formatted`
- command:
  `uv run ruff check scripts/profile_wyscout_v5.py tests/unit/test_wyscout_profile.py`
  - exit status: 0
  - result: `All checks passed!`
- command: `uv run mypy scripts/profile_wyscout_v5.py`
  - exit status: 0
  - result: `Success: no issues found in 1 source file`
- command: `uv run bandit -q scripts/profile_wyscout_v5.py`
  - exit status: 0
  - result: no findings
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: structured status `PASS`; all 25 checks passed with no failures
- additional focused correction check:
  `uv run pytest -q tests/security/test_w04_wyscout_profile_review.py::test_tracked_report_is_aggregate_only_and_contains_no_player_name`
  - exit status: 0
  - result: `1 passed in 15.83s`

## Artifacts/evidence

- `reports/phase-gates/W04/source-schema-profile.md`
  - SHA-256: `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`
  - size: 18,574 bytes
  - lines: 365
- Completion-manifest SHA-256 binding:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Admitted match-member rows: England 380, France 380, Germany 306, Italy 380,
  Spain 380.
- Admitted event-member rows: England 643,150, France 632,807, Germany 519,407,
  Italy 647,372, Spain 628,659.
- Event identity/match-bound exceptions: event-record duplicates 0, event/member partition
  mismatches 0, event team outside referenced match teamsData 0, teamsData key/team-ID
  mismatches 0.
- Coordinate evidence: 709 one-position arrays, 3,070,686 two-position arrays, x range -1..100
  with one anomaly, and y range 0..101 with two anomalies.
- Fabricated unit access audit continues to assert that archive objects and an excluded canary
  are never opened. It also verifies exact decimal-scale evidence, path inventory emission,
  partition equality, coordinate retention, and rejection of non-approved CLI paths.

## Risks

- Event-presence player-match pairs do not establish lineup status, playing time, role context,
  or a valid per-90 denominator.
- No exact period terminal, period-start UTC, elapsed duration rule, stoppage-time rule,
  possession boundary, or cross-provider identity authority is present in the admitted source.
  These remain explicit unknowns.
- Completion source-object size/digest rows for `matches.zip` and `events.zip` are declarations
  bound by the verified completion-manifest digest; the ZIP objects themselves are deliberately
  not opened. Every opened direct object and durable admitted member is independently
  size/digest-verified during each profile run.
- The three out-of-domain coordinates and unmapped lineup/substitution player references remain
  unrepaired evidence for downstream reconciliation.

## Follow-up items

- Schema design R3 may consume these measured aggregates but must preserve the unsupported
  minutes/per-90 and possession states rather than deriving semantics from event presence.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

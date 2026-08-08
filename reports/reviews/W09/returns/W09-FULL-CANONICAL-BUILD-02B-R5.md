# Subagent return

## Task

- task_id: `W09-FULL-CANONICAL-BUILD-02B`
- revision: `R5`
- objective: Inventory and conservatively classify the retained substitution-shape
  anomaly, preserve the exact/lower-bound/unusable minute policy, and complete a
  no-write action-plus-appearance projection.

## Status

- recommendation: **ACCEPT**
- The exact six raw substitution sentinels are classified without arbitrary shape
  coercion or action/current-team minute inference.
- Two adjacent, evidence-resolved appearance boundaries were found and bounded:
  14 late observed entries now supply their own zero-minute floor, and eight rejected
  `playerIn=0` occurrences are excluded individually while their distinct nonzero
  `playerOut` exits remain admitted.
- The caffeinated no-write projection completes across all 3,071,395 actions and
  68,864 canonical appearances. No further source conflict surfaced.

## Files changed

- `src/scouting/data_products/wyscout/historical.py`
- `tests/integration/test_w09_full_canonical_build.py`
- `reports/reviews/W09/returns/W09-FULL-CANONICAL-BUILD-02B-R5.md`

`src/scouting/sources/wyscout_historical.py` and its unit test remained unchanged in
R5; all R3/R4 adapter controls were preserved and rerun.

## Exact retained inventory

- Retained regular/played team rows with `hasFormation=1`: 3,652.
- `formation.substitutions` arrays: 3,646.
- Exact raw string `"null"` substitution sentinels: 6.
- No missing, JSON-null, object, numeric, Boolean or other string shape was observed.
- Every affected row has an 11-player lineup and a six- or seven-player bench.
- Exact affected match/team references:
  - England: `(2500039, 1628)`, `(2499990, 1609)`, `(2499992, 1646)`,
    `(2499980, 1628)`, `(2499941, 1628)`;
  - France: `(2501056, 3783)`.

The implementation pins this exact partition/match/team set and fails retained builds
if any raw shape or reference drifts.

## Conservative substitution-unavailable policy

- Only the exact source string `"null"` is admitted as unavailable substitution
  evidence. Arrays retain their strict existing path; every other type/string fails.
- Starting-lineup membership is direct evidence of play, but with no exit evidence its
  only safe exposure floor is zero minutes. Such rows are retained as
  `conservative_lower_bound`, `start=0`, `end=0`, `minutes=0`, right-censored, with an
  explicit unavailable-substitution basis.
- Bench membership does not prove entry. Those rows are retained as
  `bench_entry_unknown` with `unusable` minutes and no numeric exposure.
- Player action presence and `currentTeamId` are never used to infer membership or
  minutes. The manifest records both controls explicitly.

## Adjacent evidence reconciliation

### Observed entry after action-terminal floor

Fourteen substitutes enter slightly after the previous fallback terminal evidence
(`max(90, last action clock)`) and have no observed exit. The observed substitution
entry itself proves the match/player interval reaches that minute. The conservative
fallback is therefore `max(observed entry, action-terminal floor)`, yielding a
zero-minute lower bound in these 14 cases instead of an impossible negative interval.
This is substitution evidence, not inference from player action presence. The count is
recorded as `entry_after_action_terminal_lower_bound=14`.

### Repeated rejected zero entries

Exactly eight substitution rows across three Italian match/team formations repeat only
the rejected sentinel `playerIn=0`. No nonzero `playerIn` and no `playerOut` repeats.
Each nonzero exit remains a distinct valid boundary; every zero entry occurrence is
classified and excluded individually and is never collapsed into a fictional player:

- Italy `(2576016, 3164)`: outs `(333571, 90)`, `(37739, 90)`;
- Italy `(2575965, 3204)`: outs `(93341, 56)`, `(20661, 62)`, `(226200, 88)`;
- Italy `(2575959, 3158)`: outs `(23149, 74)`, `(44251, 81)`, `(3475, 84)`.

The exact partition/match/team/player-out/minute set is pinned. Any repeated nonzero
entry, repeated exit, duplicate zero occurrence, non-integral zero-entry minute or map
drift fails closed.

## Full no-write projection evidence

The caffeinated `audit_historical_appearance_projection` completed with exit status
`0` after traversing all five exact action payloads:

- canonical actions traversed: 3,071,395;
- optional `subEventId` sentinels: 7,821 with the accepted exact partition counts;
- coordinate anomalies: the accepted exact three actions/points;
- canonical appearances: 68,864;
- exact-minute appearances: 10,749;
- conservative-lower-bound appearances: 39,838;
- unusable appearances: 18,277;
- unavailable-substitution teams: 6 with the exact references above;
- zero-entry substitution occurrences excluded: 8 with all exits retained;
- observed-entry floors applied: 14;
- unresolved lineup occurrences excluded: 23;
- zero lineup occurrences excluded: 0;
- team rows without formation: 0;
- all action-file fingerprints remained stable.

The three minute-state counts reconcile exactly to 68,864.

## Checks run

- `uv run ruff format --check src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py tests/unit/test_w09_wyscout_historical_adapter.py tests/integration/test_w09_full_canonical_build.py`
  - exit status: `0`; all four files formatted.
- `uv run ruff check ...`
  - exit status: `0`; all checks passed.
- `uv run mypy src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py`
  - exit status: `0`; no issues in two source files.
- `uv run pytest -q tests/unit/test_w09_wyscout_historical_adapter.py tests/integration/test_w09_full_canonical_build.py`
  - exit status: `0`; 40 tests passed.
  - New cases cover the exact `"null"` sentinel, all rejected alternative shapes,
    zero-minute starter lower bounds, unusable bench-entry-unknown rows, late-entry
    floors, repeated zero-entry classification, retained nonzero exits and repeated
    nonzero-entry rejection.
- `.venv/bin/bandit -q -r src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py`
  - exit status: `0`; no security findings. The direct root-environment executable was
    used because the sandbox cannot read the existing external uv cache through the
    `uv run bandit` wrapper.

## Boundaries and follow-up

- No production artifact was generated by R5.
- `CANONICAL_BUILDER_VERSION` is now `w09-full-canonical-build-02b-r5`, so the next
  master materialization is content/version distinct from safely failed partial runs.
- The master may independently inspect and rerun R5, then materialize at the exact
  canonical production roots. W09-02C should remain paused until that manifest and all
  canonical artifacts reconcile.

## Scope confirmation

- no Git operations: confirmed.
- no dependency, lockfile, shared-contract or orchestration-control edits: confirmed.
- no network/provider access: confirmed.
- no action/current-team minute inference: confirmed.
- no arbitrary substitution-shape coercion: confirmed.
- no production artifact generation: confirmed.
- no edits outside the authorised R5 implementation/test/report paths: confirmed.

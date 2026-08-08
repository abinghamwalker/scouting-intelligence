# Subagent return

## Task

- task_id: `W04-SOURCE-PROFILE-01-R1`
- objective: Produce a deterministic, bounded-memory, completion-manifest-bound aggregate
  profile of the admitted Wyscout v5 source snapshot for downstream schema design.

## Files changed

- `scripts/profile_wyscout_v5.py`
- `tests/unit/test_wyscout_profile.py`
- `reports/phase-gates/W04/source-schema-profile.md`
- `reports/reviews/W04/returns/W04-SOURCE-PROFILE-01-R1.md`

## Summary

- Implemented a standard-library profiler with incremental UTF-8/top-level JSON-array
  decoding, per-file SHA-256 and byte-size verification, bounded record buffers, bounded
  schema paths, bounded distinct-ID/period aggregates, and capped manifest/CSV inputs.
- Bound source access to normalized `object_path` and `member_path` values read from the
  completion manifest. The implementation has no ZIP reader, URL client, provider call, or
  path reconstruction. It opens five required direct objects and all ten admitted extracted
  JSON members; ZIP objects and four scope-excluded archive entries are not opened.
- Normalized numeric object keys to aggregate `.*` schema paths. This prevents match-specific
  `teamsData` identifiers from entering the report or growing schema memory with record count.
- Emitted measured aggregate field presence/type shapes, dataset counts, ID reconciliation,
  period/eventSec ranges, lineup/bench/substitution evidence, and explicit identity,
  possession, minutes, coverage, and reconciliation limits. No raw records, player-name
  values, or mapping-label values are emitted.
- Production evidence includes 7 competitions, 142 teams, 3,603 players, 1,826 matches,
  3,071,395 events, 40,172 lineup rows, 28,715 bench rows, and 10,423 substitution rows.
- `--check` performs a complete source recomputation and compares exact output bytes without
  writing.

## Tests run

- command: `uv run pytest -q tests/unit/test_wyscout_profile.py`
  - exit status: 0
  - result: `4 passed in 0.13s`
- command: `uv run python scripts/profile_wyscout_v5.py --check`
  - exit status: 0
  - result: `profile check passed: reports/phase-gates/W04/source-schema-profile.md`
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
  - result: structured verifier status `PASS` with no failures

## Artifacts/evidence

- `reports/phase-gates/W04/source-schema-profile.md`
  - report SHA-256:
    `fca42b10f7b3f6053d561c3733b626dd8c92023a7fa5f5c3053cd6dd4260de5f`
  - report size: 11,687 bytes
  - report lines: 265
- Completion-manifest SHA-256 binding:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Fabricated-fixture access audit records every `Path.open` and asserts the observed set is a
  subset of the manifest plus the five required direct and admitted member paths. It also
  asserts both ZIP objects and an excluded canary remain unopened.
- Measured reconciliation evidence retains zero-valued IDs separately and reports 23 unmapped
  bench player IDs plus 8 unmapped substitution `playerIn` IDs without repair or guessed
  semantics.

## Risks

- The evidence cannot establish possession semantics, exact period terminals, period-start
  UTC, stoppage-time rules, or exact player minutes. The report explicitly preserves these as
  unknown.
- Counts and shapes apply only to the completion-declared admitted snapshot. Scope-excluded
  archive entries were intentionally not inspected.
- The profiler treats numeric string IDs and integer IDs as the same comparison key for
  measured within-snapshot reconciliation, while retaining their original measured JSON type
  shapes in the schema tables.

## Follow-up items

- Downstream schema design should preserve the reported null/mixed-type fields, zero-valued
  event player IDs, and unmapped lineup/substitution references as explicit evidence states.
- Exact minutes or possession derivation requires separately admitted evidence and rules; it
  must not be inferred from this profile alone.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

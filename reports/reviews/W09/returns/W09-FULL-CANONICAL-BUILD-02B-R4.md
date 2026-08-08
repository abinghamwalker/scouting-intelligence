# Subagent return

## Task

- task_id: `W09-FULL-CANONICAL-BUILD-02B`
- revision: `R4`
- objective: Preserve and classify the three retained out-of-domain coordinate
  points without changing or excluding their actions, then complete the full
  no-write canonical action traversal.

## Status

- recommendation: **ACCEPT**
- The approved bounded coordinate evidence-state policy is implemented.
- The no-write canonical projection now completes across all 3,071,395 actions with
  exact identity, optional-subevent, coordinate-anomaly and fingerprint reconciliation.
- No additional source conflict was found.

## Files changed

- `src/scouting/sources/wyscout_historical.py`
- `src/scouting/data_products/wyscout/historical.py`
- `tests/unit/test_w09_wyscout_historical_adapter.py`
- `tests/integration/test_w09_full_canonical_build.py`
- `reports/reviews/W09/returns/W09-FULL-CANONICAL-BUILD-02B-R4.md`

## Implementation

- Canonical actions now carry the closed `coordinate_evidence_state` value:
  `valid`, `absent`, or `invalid_out_of_range`.
- Every supplied coordinate remains a strict integer. Missing keys, floats, quoted
  numerics, Booleans, non-object points, non-array structures and more than two points
  fail closed.
- An action is `invalid_out_of_range` when any supplied coordinate lies outside the
  inclusive 0..100 domain. The original integers remain unchanged in `start_x`,
  `start_y`, `end_x` and `end_y`; the producer never clamps, wraps, nulls or drops the
  containing action.
- Retained builds require the exact accepted anomaly map:
  - Germany action `225765702`: point 1 `y=101`;
  - Germany action `225765704`: point 0 `y=101`;
  - Italy action `198907641`: point 0 `x=-1`.
- The manifest records the closed states, per-partition state counts, invalid-action
  counts, invalid-point count, exact action/point evidence and the rules that
  coordinate-independent actions remain admitted while coordinate coverage admits
  only `valid` evidence.
- The no-write audit exposes the same reconciled counts. Retained traversal fails if
  the exact anomaly identities, axes, point indices, values or counts drift.
- R3's provider-boundary `subEventId` handling remains intact: strict numeric JSON
  integers and nulls are preserved, only the exact empty sentinel becomes null, and
  every other type fails closed.

## Verification

- `uv run ruff format --check src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py tests/unit/test_w09_wyscout_historical_adapter.py tests/integration/test_w09_full_canonical_build.py`
  - exit status: `0`; all five files formatted.
- `uv run ruff check ...`
  - exit status: `0`; all checks passed.
- `uv run mypy src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py`
  - exit status: `0`; no issues in three source files.
- `uv run pytest -q tests/unit/test_w09_wyscout_historical_adapter.py tests/integration/test_w09_full_canonical_build.py`
  - exit status: `0`; 30 tests passed.
  - Coverage proves valid/absent/invalid state separation, raw `101` preservation,
    action retention, no clamping, exact fixture manifest counts, deterministic bytes,
    malformed coordinate rejection and all R2/R3 controls.
- `.venv/bin/bandit -q -r src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py`
  - exit status: `0`; no security findings. As in R3, the exact `uv run bandit`
    wrapper could not read the existing external uv cache in the sandbox, so the same
    root-environment executable was used directly.
- Caffeinated retained no-write canonical action projection:
  - exit status: `0`;
  - actions: `3,071,395`;
  - empty optional `subEventId` sentinels: `7,821`, exactly England 1,558, France
    1,543, Germany 1,219, Italy 1,620 and Spain 1,881;
  - invalid coordinate actions: `3`; invalid coordinate points: `3`;
  - coordinate state counts:
    - England: valid 643,150; absent 0; invalid 0;
    - France: valid 632,807; absent 0; invalid 0;
    - Germany: valid 519,405; absent 0; invalid 2;
    - Italy: valid 647,371; absent 0; invalid 1;
    - Spain: valid 628,659; absent 0; invalid 0.
  - every before/after action-file fingerprint remained stable.

## Boundaries and follow-up

- The coordinate state is evidence classification, not a provider schema correction.
- Coordinate-independent W09 counts may retain all three actions. Any later
  coordinate-derived feature or coverage calculation must require state `valid`.
- The master may now independently inspect R4, rerun its checks and execute the final
  production canonical materialization. This packet generated no production artifact.

## Scope confirmation

- no Git operations: confirmed.
- no dependency, lockfile, shared-contract or orchestration edits: confirmed.
- no network/provider access: confirmed.
- no final production artifacts: confirmed.
- no edits outside R4 `allowed_paths`: confirmed.

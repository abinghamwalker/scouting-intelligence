# Subagent return

## Task

- task_id: `W09-RESEARCH-STATE-04A`
- revision: `R2`
- objective: Adapt storage evidence to the independently tightened explanation and replay-receipt contracts without changing shared contracts, migrations or orchestration.

## Files changed

- `tests/integration/test_w09_research_storage.py`
- `reports/reviews/W09/returns/W09-RESEARCH-STATE-04A-R2.md`

`src/scouting/storage/research.py` required no semantic R2 edit: it already revalidates every submitted `ResearchReplayReceipt` through the current strict contract and binds the saved query digest to the stored experiment before insertion.

## Summary

- Updated Euclidean result fixtures to include `scaled_query_value` and `scaled_candidate_value` with exact per-term arithmetic: `scaled_contrast = scaled_candidate_value - scaled_query_value`, `contribution = weight * scaled_contrast**2`, and `score**2 = sum(contributions)`.
- Added an explicit SQLite/load round-trip asserting that the new scaled explanation operands and the full contribution object persist exactly in canonical `result_json`.
- Added a valid `RESULT_MISMATCH` receipt fixture with identical saved/replay query digests and pins but deliberately different replay result ID/digest. The receipt persists and round-trips with its closed mismatch status/reason.
- Added an adversarial receipt built with `model_construct`, a recomputed semantic receipt ID/digest and a different replay query digest. `ResearchExperimentStore.append_replay_receipt` revalidates it through `ResearchReplayReceipt`, rejects it as a contract-integrity error, and leaves the previously persisted receipt count unchanged. Persistence therefore cannot turn a different-query execution into `RESULT_MISMATCH` evidence.

## Exact checks

- `uv run ruff format --check src/scouting/storage/research.py tests/integration/test_w09_research_storage.py`
  - PASS: 2 files already formatted.
- `uv run ruff check src/scouting/storage/research.py tests/integration/test_w09_research_storage.py`
  - PASS: all checks passed.
- `uv run mypy src/scouting/storage/research.py`
  - PASS: no issues found in 1 source file.
- `uv run pytest -q tests/integration/test_w09_research_storage.py tests/integration/test_migrations.py tests/contracts/test_w09_research_contracts.py`
  - PASS: 32 tests passed in 0.48s.

## Boundaries

- The R2 change is automated fixture/evidence work only; no product claim was changed.
- No implementation outside the existing storage boundary was needed.
- The prior R1 persistence behavior, including canonical exact JSON, content addressing, conflict rollback, append-only triggers and W08 non-coupling, remains covered by the passing storage suite.

## Scope confirmation

- No Git operations were run.
- No dependency, lockfile, migration, contract, orchestration, package-export or W08 file was edited.
- All edits stayed inside the R2 allowed test and return-report paths.

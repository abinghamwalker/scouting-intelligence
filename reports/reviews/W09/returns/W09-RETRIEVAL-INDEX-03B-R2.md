# Subagent return

## Task

- task_id: `W09-RETRIEVAL-INDEX-03B`
- revision: `R2`
- objective: Preserve every legitimate player-by-competition-season row while rejecting
  duplicate grain semantics and retaining deterministic exhaustive indexing.

## Files changed

- `src/scouting/modeling/research.py`
- `tests/integration/test_w09_research_index_build.py`
- `reports/reviews/W09/returns/W09-RETRIEVAL-INDEX-03B-R2.md`

## Correction implemented

- Removed R1's incorrect global one-row-per-canonical-player restriction from both the governed
  matrix loader and immutable index loader.
- Retained global `grain_id` uniqueness and added explicit uniqueness for
  `(player_id, competition_id, season_id)`. The same canonical player can therefore appear in
  multiple competitions or seasons, but cannot appear twice inside one competition-season.
- Preserved canonical index order as `(player UUID bytes, grain_id)`. No row is deduplicated,
  sampled, inferred or silently discarded.
- Added a four-row fixture in which one canonical player has one row in each of two competitions.
  The loader retains both rows, the manifest reconciles four rows to three unique players, two
  independent index roots reproduce identical bytes, and the loaded candidate catalogue retains
  both competition-specific rows.
- Retained the existing matrix-level duplicate-player adversary as a same-competition-season
  rejection and added a separately re-digested index-catalogue forgery proving the index loader
  rejects the same player twice within one competition-season.
- All R1 physical/semantic tamper, path, temporal, stale, missingness, dtype/order, immutable-write,
  no-synthetic-authority and catalogue/vector consistency controls remain covered.

## Contract conclusion

The accepted contracts represent this behavior without conflict:

- `FeatureMatrixRow` is explicitly a player/competition-season row.
- `FeatureMatrixManifest.unique_matrix_player_count` may be smaller than `matrix_row_count`.
- Mandatory research filters bind every query to one `competition_id`; within-competition-season
  uniqueness therefore prevents duplicate canonical players in that query population without
  imposing a false global restriction on retained transfers or cross-competition history.

## Checks run

- `uv run ruff format --check src/scouting/modeling/research.py scripts/build_w09_research_index.py tests/unit/test_w09_research_index.py tests/integration/test_w09_research_index_build.py`
  - exit status: `0`
  - result: PASS — four files already formatted.
- `uv run ruff check src/scouting/modeling/research.py scripts/build_w09_research_index.py tests/unit/test_w09_research_index.py tests/integration/test_w09_research_index_build.py`
  - exit status: `0`
  - result: PASS — all checks passed.
- `uv run mypy src/scouting/modeling/research.py scripts/build_w09_research_index.py`
  - exit status: `0`
  - result: PASS — no issues found in two source files.
- `uv run pytest -q tests/unit/test_w09_research_index.py tests/integration/test_w09_research_index_build.py`
  - exit status: `0`
  - result: PASS — 21 tests passed in 0.90 seconds.
- `uv run bandit -q -r src/scouting/modeling/research.py scripts/build_w09_research_index.py`
  - exit status: `0`
  - result: PASS — no security findings.

## Artifacts and evidence

- implementation: `src/scouting/modeling/research.py`
- adversarial/reproducibility evidence: `tests/integration/test_w09_research_index_build.py`
- prior implementation return: `reports/reviews/W09/returns/W09-RETRIEVAL-INDEX-03B-R1.md`
- no production matrix or index artifact was generated.

## Residual risks and follow-up

- none within this bounded grain correction.
- The master should independently inspect the corrected uniqueness predicates and reproduce the
  exact checks before accepting 03B R2. Later serving must continue to enforce the mandatory
  competition filter and use the complete matching competition population before response limits.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no dependency, lockfile, configuration, CLI, orchestration-control, contract, feature, serving,
  web or production-artifact changes: confirmed.
- no edits outside the R2 allowed paths: confirmed.
- no network, provider access or external service: confirmed.
- no further delegation: confirmed.

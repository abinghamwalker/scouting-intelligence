# Subagent return

## Task

- task_id: `W10-V2-EVIDENCE-DESIGN-08A-R1`
- objective: Define a position-specific football role/style construct and prove which transparent
  model inputs and independent descriptors can be derived from retained governed W09 evidence.

## Files changed

- `reports/verification/W10/v2-evidence-capability-and-construct.md`
- `reports/reviews/W10/returns/W10-V2-EVIDENCE-DESIGN-08A-R1.md`

## Summary

- Fixed the construct as realised historical functional involvement/action-selection patterns, not
  W09 distance, reputation, player quality, recruitment usefulness or outcomes.
- Separated evidence quantity, the exact 16 `W09_INPUT` fields, independent descriptors, prior
  professional knowledge and unsupported inference.
- Bound the independent roster to exact canonical predicates for neutral recorded-coordinate
  distributions, non-W09 pass and duel subtype mixes, defensive/shot locations and narrow GK event
  evidence; documented raw denominators, coverage, missingness and zero semantics.
- Returned `YES` for DF/MD/FW and a deliberately narrow `YES` for GK, conditional on frozen
  query-level opportunity sufficiency. Explicitly requires GK redesign/removal if later authority
  asks for shot-stopping quality, shots faced, claims, goals prevented, errors or effectiveness.
- Traced the W09 scorer from the frozen registry through matrix/index construction and serving to
  the single shared vector scorer, proving the independent roster is outside ranking inputs.

## Tests run

- command: `jq` projections of the accepted canonical, feature-matrix and W09 index manifests
  - exit status: `0`
  - result: confirmed canonical build `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`,
    matrix `w09-historical-player-window-v1-a31511705ac15a5d`, 1,975 rows, the exact 16 ordered
    feature names and the pinned shared scorer.
- command: `UV_NO_CACHE=1 uv run --no-sync python` DuckDB read-only joins over the accepted matrix
  and five canonical action partitions
  - exit status: `0`
  - result: confirmed GK 136 / DF 713 / MD 711 / FW 415, every eligible row uses
    `conservative_lower_bound` minutes, and every eligible GK has retained pass, save-attempt,
    leaving-line, goal-kick and launch evidence (minima 75 / 16 / 4 / 34 / 12; minimum valid
    coordinate coverage 99.9285%).
- command: `UV_NO_CACHE=1 uv run --no-sync python` canonical Parquet schema inspection and distinct
  relevant event/sub-event label query
  - exit status: `0`
  - result: confirmed retained identity/time/taxonomy/tag/coordinate/coverage fields and exact
    labels for duel, pass, shot and GK predicates.
- command: targeted `rg`/`sed` inspection of
  `src/scouting/features/historical.py`, `src/scouting/modeling/research.py`,
  `src/scouting/serving/research.py` and `src/scouting/m0/scoring.py`
  - exit status: `0`
  - result: confirmed registry order enforcement and the only matrix-feature-to-index-to-scorer
    path. No independent descriptor is currently read by W09 ranking.

## Artifacts/evidence

- `reports/verification/W10/v2-evidence-capability-and-construct.md`
- `data/manifests/wyscout/v5/research/72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7.canonical-manifest.json`
- `data/manifests/wyscout/v5/research_features/w09-historical-player-window-v1-a31511705ac15a5d.feature-matrix.manifest.json`
- `runs/w09/historical-player-workbench-v1/manifest.json`

## Risks

- Opportunity thresholds are intentionally not inferred from observed minima; A2 must preregister
  them before participant exposure and exclude mandatory-family failures visibly.
- Every eligible minutes denominator is a conservative lower bound, so per-90 values may overstate
  rates based on unknown true minutes.
- Recorded coordinates lack governed attack-direction semantics. Neutral raw/binned distributions
  are supported; progressive/final-third/directional labels are not.
- Visible player identity can activate reputation knowledge. Assessment basis must remain explicit,
  and prior-knowledge-only responses must stay outside the primary construct analysis.
- GK evidence is sufficiently nontrivial for a narrow event-descriptive construct but cannot
  support quality/effectiveness or outcome claims.

## Follow-up items

- A2 must implement the fixed evidence classes, six availability states, exact raw
  numerator/denominator/coverage lineage, position roster, frozen opportunity thresholds and hard
  code-path separation from W09 ranking.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

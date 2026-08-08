# Subagent return

## Task

- task_id: W05-MODEL-01
- objective: Implement deterministic transparent M0 families and select a synthetic-development baseline only if it strictly clears both controls.

## Files changed

- configs/models/w05-m0-baselines-v1.json
- src/scouting/m0/__init__.py
- src/scouting/m0/core.py
- src/scouting/modeling/__init__.py
- src/scouting/modeling/baselines.py
- reports/reviews/W05/returns/W05-MODEL-01-R1.md

## Summary

- Implemented a partial deterministic M0 implementation: six-family fitter/writer, a read-only runtime loader/scorer with one canonical `M0DistanceRow`, canonical JSON, fixed-metadata NPZ output, UUID tie ordering, robust scaling, weighted cosine, canonical PCA, and taxonomy-object revalidation/pinning.
- Stop condition reached before adding the required selected artifact, development-query fixture, or focused test file: the selected role-aware/weighted family cannot strictly clear both accepted controls using the accepted synthetic fixture and taxonomy.
- No accepted feature fixture, role fixture, taxonomy, shared contract, W03/W04 evidence, or dependency was altered.

## Tests run

- `UV_CACHE_DIR=/tmp/w05-m0-uv-cache uv run --no-sync python -m compileall -q src/scouting/m0 src/scouting/modeling`
  - exit status: 0
  - result: partial runtime/trainer code compiled.
- Synthetic leave-one-query-out development probe, `k=3`, with query player self-excluded:
  - exit status: 0
  - result: `metadata_control=0.8518518518518519`; `raw_euclidean_control=0.8518518518518519`; `robust_scaled_cosine=0.7777777777777778`; `weighted_cosine=0.7777777777777778`; `pca=0.7777777777777778`; `role_aware_restriction=0.7777777777777778`.
- Bounded transparent configuration exploration (same fixture, no labels changed):
  - exit status: 0
  - result: all 729 global positive weighted-cosine vectors in `{0.1, 1, 10}^6`, with role-overlap restriction `0.0`, had best precision@3 `0.7777777777777778`; eight additional declared fixed configurations also each scored `0.7777777777777778`: `(4,4,1,0.25,0.25,0.25)/0.5`, `(4,1,4,0.25,0.25,0.25)/0.5`, `(0.25,0.25,0.25,4,1,1)/0.5`, `(4,4,4,0.25,0.25,0.25)/0.5`, `(10,10,10,0.1,0.1,0.1)/0.5`, `(1,1,1,1,1,1)/0.8`, `(4,4,4,0.25,0.25,0.25)/0.8`, and `(0.1,0.1,0.1,10,10,10)/0.8`.

## Artifacts/evidence

- Accepted feature registry identity: `w05-m0-feature-registry-v1` / `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644`.
- Accepted taxonomy identity: `w05-football-responsibility-taxonomy-v1` / `v1` / `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`.
- Attempted initial configuration digest: `baee765d393fade375fdd2428cf326272fc1427c2c953b32d6d25cbbefc7abbd`.
- Initial temporary family manifest digests: metadata `0bc0130cba106fd47b53016822b9184a917ee006da86f21e24c2cfeb999b4902`; raw `3994a9eef660f340231159f9b2ecb807d31871a3a79501867376b3afbd305ddd`; robust cosine `5d2894dbb73e852e70bebc4d0dba36a8be62ab5facf2902526733582afd03cd0`; weighted cosine `0a43ed6ab3437200e8d7ed801c50b0692cf98bb3fc56f811095b6b80c60a4946`; PCA `fafee662d9926354e73b7823c607d904af9c0f518e1704d54db95de7ddd1f7cb`; role-aware `cf69e38d2470428e9871d992588936ab26656d2570a9135dd71054d301f737a4`.

## Risks

- **STOP CONDITION:** no selected role-aware/weighted baseline can strictly exceed both controls on the accepted constructed fixture without an out-of-scope change to accepted feature/role/query labels or a materially different model/query behavior. The required artifact under `runs/w05/m0-baseline-v1` has intentionally not been written.
- The partial implementation is not ready for acceptance: the mandatory development-query fixture and focused adversarial test suite were not added because doing so would misrepresent a failed readiness gate as a selected baseline.

## Follow-up items

- Master decision required: reframe the model packet or obtain authority for a changed constructed-development evaluation/query design. Do not select or promote this baseline under the current accepted controls.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

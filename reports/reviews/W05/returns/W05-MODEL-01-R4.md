# Subagent return

## Task

- task_id: W05-MODEL-01
- objective: Close R3 representation and trust-pinning defects while preserving the frozen R3 M0 semantics and result.

## Files changed

- configs/models/w05-m0-baselines-v1.json
- src/scouting/m0/__init__.py
- src/scouting/m0/core.py
- src/scouting/modeling/baselines.py
- tests/fixtures/w05/m0-development-candidates-v1.json
- tests/fixtures/w05/m0-development-queries-v1.json
- tests/unit/test_w05_m0_models.py
- runs/w05/m0-baseline-v1/arrays.npz
- runs/w05/m0-baseline-v1/manifest.json
- runs/w05/m0-baseline-v1/configuration.json
- runs/w05/m0-baseline-v1/candidate-universe.json
- reports/reviews/W05/returns/W05-MODEL-01-R4.md

## Summary

- Expanded the frozen construction into explicit ordered 18-candidate and 18-query canonical fixtures. Candidate digest: `710c38554f33f8f650d814df1fee3c8bac7a8a2bc22804f93e3b9a8dfd1e50d9`; query digest: `fb027563b3f99f563d43f1b909c535f860f3d04d2d8aa0ed44e902fd2a37e900`.
- Added a source-pinned immutable typed configuration loader. Configuration digest: `275b5238ca8d1bae5ce5da00c34f62cba81ce40749da1f181bb8a9ae29418fd9`; candidate/query projection digests: `aaa9ee5d9c5347d6667f69efcce74d249d33a97b3199cd6f01c66b71d3d3081c` / `1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c`.
- Staged all six families in bounded temporary paths, verified their pre-pinned array payloads, then wrote the selected role-aware artifact once at `runs/w05/m0-baseline-v1/`. Selected manifest digest: `8183c1aa1c41321c7d81398392f61fbe7a9b890b2a0c5c3a8e1085fb9aff543a`.
- Exact pinned array payload digests: metadata `19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee`; raw `3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36`; robust `ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc`; weighted/role-aware `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801`; PCA `90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971`.
- R4 parity reproduction: metadata `0.1111111111111111`; raw `0.3333333333333333`; robust `1.0`; weighted `1.0`; PCA `1.0`; role-aware `1.0`.

## Tests run

- `uv run --no-sync python -c ...` staged six deterministic family artifacts in `/tmp` and verified the six pinned payload digests.
  - exit status: 0
- `uv run --no-sync python -c ...` wrote the selected artifact exactly once after staging.
  - exit status: 0
- `uv run --no-sync python -c ...` reproduced the frozen R3 six-score parity check.
  - exit status: 0
- `uv run --no-sync ruff format --check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py && uv run --no-sync ruff check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py && uv run --no-sync mypy src/scouting/m0 src/scouting/modeling && uv run --no-sync pytest -q tests/unit/test_w05_m0_models.py tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/contracts/test_w05_m0_contracts.py && uv run --no-sync lint-imports && uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: 62 tests passed; all focused checks passed.

## Artifacts/evidence

- `tests/fixtures/w05/m0-development-candidates-v1.json`
- `tests/fixtures/w05/m0-development-queries-v1.json`
- `configs/models/w05-m0-baselines-v1.json`
- `runs/w05/m0-baseline-v1/`

## Risks

- This is only constructed synthetic development readiness. It is never validation, W06/protected evidence, expert evidence, recruitment outcome, transfer, robustness, Wyscout, or production evidence.
- R1 negative evidence remains retained: metadata/raw `0.8518518518518519`; robust/weighted/PCA/role-aware `0.7777777777777778`; the 729-vector lattice and eight fixed variants did not improve the failed original fixture result.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

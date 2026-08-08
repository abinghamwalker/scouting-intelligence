# Subagent return

## Task

- task_id: W05-MODEL-01
- objective: Execute the preregistered synthetic M0 family comparison and selected role-aware artifact build.

## Files changed

- configs/models/w05-m0-baselines-v1.json
- src/scouting/m0/core.py
- src/scouting/modeling/baselines.py
- tests/fixtures/w05/m0-development-candidates-v1.json
- tests/fixtures/w05/m0-development-queries-v1.json
- runs/w05/m0-baseline-v1/arrays.npz
- runs/w05/m0-baseline-v1/manifest.json
- runs/w05/m0-baseline-v1/configuration.json
- runs/w05/m0-baseline-v1/candidate-universe.json
- reports/reviews/W05/returns/W05-MODEL-01-R3.md

## Summary

- Retained the one runtime scorer and six family implementations. The frozen R3 fixture construction uses 18 canonical UUIDs, cross-balanced metadata, responsibility-derived memberships, complete numeric values, and observed aerial zero.
- The one all-18 leave-one-out comparison reported precision@3: metadata `0.1111111111111111`, raw Euclidean `0.3333333333333333`, robust cosine `1.0`, weighted cosine `1.0`, PCA `1.0`, and role-aware restriction `1.0`. The selected family therefore strictly clears both controls.
- Selected artifact: `ad0bf692-e1d7-575c-af6a-12cefd19c776`; manifest digest `489b7db103aa964f70f2dd49be5bcf9c242c59d7163b1cb98656621bd83278d2`; array payload digest `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801`.
- Retained R1 negative evidence exactly: metadata/raw `0.8518518518518519`; robust/weighted/PCA/role-aware `0.7777777777777778`; the 729-vector positive-weight lattice and eight fixed variants did not improve it. R3 is solely a deliberately constructed synthetic-development readiness fact, not validation, protected evidence, expert review, recruitment effectiveness, robustness, transfer, Wyscout, or production evidence.

## Tests run

- `uv run --no-sync python -m compileall -q src/scouting/m0 src/scouting/modeling`
  - exit status: 0
  - result: M0 runtime/trainer compiled before the frozen comparison.
- Single R3 all-family local comparison over all 18 self-excluded queries, `k=3`
  - exit status: 0
  - result: six scores and stable per-query ranking digests were emitted; selected role-aware score was strictly above both controls.
- `uv run --no-sync pytest -q tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: 60 passed.
- `uv run --no-sync ruff format --check src/scouting/m0 src/scouting/modeling && uv run --no-sync ruff check src/scouting/m0 src/scouting/modeling && uv run --no-sync mypy src/scouting/m0 src/scouting/modeling && uv run --no-sync lint-imports && uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: formatting, lint, typing, import direction and local-only checks passed.

## Artifacts/evidence

- Candidate fixture digest: `74d83509066b07be6fbd03d7f55e24ee86c98533da08d4989530647f2ca5e79e`.
- Query fixture digest: `3acf17e5bf995ef883fdc03e3b62288e27f937a82ee92088453f292b9091cf13`.
- Configuration digest: `665dbc4bb0753ce59913b9fcd836842531f49ac88fd37d8eff129b0b8dfe8b38`.
- Selected artifact: `runs/w05/m0-baseline-v1/`.

## Risks

- **REWORK REQUIRED:** the candidate fixture is a compact declarative construction rather than the packet-required explicit 18-row JSON projection; the query fixture likewise lacks the required explicit ordered query rows.
- **REWORK REQUIRED:** configuration expected array payload digests and population projection pins remain empty, and candidate-universe JSON does not yet carry fixture/query pins. This means the current positive comparison and artifact are not acceptable evidence under R3’s typed-pinning requirements.
- No production or W06 claim is made.

## Follow-up items

- Replace the compact fixture declarations with exact canonical row/query projections, add the missing typed config and candidate-universe pins before any future authorised comparison, and add the packet-required dedicated M0 adversarial tests.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

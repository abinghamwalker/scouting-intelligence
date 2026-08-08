# Subagent return

## Task

- task_id: W05-MODEL-REVIEW-01
- objective: Independently verify the R5 M0 families, deterministic fit/reload, PCA canonicalization, artifact substitution closure, and frozen synthetic-development control improvement.

## Files changed

- reports/reviews/W05/w05-m0-model-independent-review-R1.md
- reports/reviews/W05/returns/W05-MODEL-REVIEW-01-R1.md

## Summary

- **Verdict: REWORK. P0: none.**
- **P1, blocker tests 1/2/3/4/6:** directly constructed typed authorities are not fully revalidated. Accepted-ID/digest objects admitted threshold `0.0` with changed role eligibility, selected-family drift, schema name/hash drift, contextual role-probability drift, and pre-cutoff lineage substitution.
- **P1, blocker tests 1/3/4/6:** exactly tied PCA variance is not canonical under valid basis rotation; components/transformed index/contribution evidence can differ.
- **P1, blocker tests 1/3/6:** noncanonical and duplicate-key `manifest.json` bytes load successfully.
- **P1, blocker tests 5/6:** fitting writes through an ancestor-symlinked destination. Root-symlink fitting and root/ancestor-symlink loading reject correctly.
- P2 only: list collections and redundant query/exclusion overlap are admitted; no independent blocker-test behavior change reproduced. No W10-only issue is used.
- Fresh two-root builds reproduced byte-identical four-file artifacts, exact payload digests, distances, contributions, ranking lists and scores for all six families. The selected score `1.0` strictly clears metadata `0.1111111111111111` and raw `0.3333333333333333`.

## Tests run

- `uv run pytest -q tests/unit/test_w05_m0_models.py tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: 65 passed in 1.20s.
- `uv run ruff check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py && uv run mypy src/scouting/m0 src/scouting/modeling && uv run lint-imports && uv run python scripts/verify_local_only.py`
  - exit status: 2
  - result: sandbox denied the global uv cache path before checks executed.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync ruff check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py && UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync mypy src/scouting/m0 src/scouting/modeling && UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync lint-imports && UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: lint, typing, import boundaries and local-only checks pass.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync ruff format --check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py`
  - exit status: 0
  - result: five files already formatted.
- Five bounded `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python -c '<inline independent probe>'` commands exercised two-root all-family rebuilds; direct typed-authority substitutions; PCA/zero/tie/query discipline; NPZ/manifest/symlink mutations; and fully re-signed disk substitutions.
  - exit status: 0 for the final bounded commands; one initial temp-root build exited 1 because `/var` resolves through `/private/var`, then the exact build was rerun under `/private/tmp`.
  - result: detailed commands, outputs and classifications are in `reports/reviews/W05/w05-m0-model-independent-review-R1.md`.

## Artifacts/evidence

- Independent review: `reports/reviews/W05/w05-m0-model-independent-review-R1.md`.
- Fresh build roots: `/private/tmp/w05-review-a-z3r19acd`, `/private/tmp/w05-review-b-o5a9vbto`.
- Configuration logical/physical digests: `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a` / `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`.
- Candidate logical/physical digests: `710c38554f33f8f650d814df1fee3c8bac7a8a2bc22804f93e3b9a8dfd1e50d9` / `5c6f4c26c2f9c71bacb1b13e80d5872b556001f55462a9cc359bf24be06317fc`.
- Query logical/physical digests: `fb027563b3f99f563d43f1b909c535f860f3d04d2d8aa0ed44e902fd2a37e900` / `1352ed759db30b4c430644893e558aa089e24153193f934cd124373cb6e29157`.
- Exact family artifact UUID / manifest / payload / score identities are tabulated in the independent review. Selected role-aware: `9a0d43c6-d177-51be-8280-3bf02bedbc99` / `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9` / `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` / `1.0`.

## Risks

- Current typed object constructors permit self-consistent authority substitution that changes eligibility, schema/explanation authority, and lineage while retaining accepted IDs/digests.
- Degenerate PCA payloads are not basis-canonical.
- Manifest physical bytes and fitting destination ancestry are not fail-closed.
- The positive comparison remains constructed synthetic-development readiness only, never validation, W06/protected evidence, expert evidence, recruitment outcome/effectiveness, robustness, transfer, provider/Wyscout, or production evidence.

## Follow-up items

- Revalidate complete config/registry/candidate/query authorities at every public fit/load/check boundary, including the accepted full candidate projection for metadata.
- Canonicalize tied PCA subspaces from an invariant projector.
- Route manifest through duplicate-key rejecting canonical JSON validation.
- Reject every fitting destination ancestor symlink.
- Add the missing mandatory adversarial tests; enforce tuple and overlap query inputs as bounded P2 hardening.

## Scope confirmation

- no Git operations: confirmed; no Git command was issued. The required local-only verifier performed its own read-only repository checks.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed; repository writes are exactly the two report files. Fresh artifacts and mutations were bounded to `/private/tmp`.

# Subagent return

## Task

- task_id: W05-MODEL-01
- objective: Close the R5 source-pinned typed-authority, canonical PCA, manifest and safe-write defects without changing frozen M0 evidence.

## Files changed

- src/scouting/m0/core.py
- src/scouting/modeling/baselines.py
- tests/unit/test_w05_m0_models.py
- reports/reviews/W05/returns/W05-MODEL-01-R6.md

## Summary

- Every fit, load and development-check boundary now reconstructs and pins the complete typed configuration, complete semantic registry projection, taxonomy wrapper and contract, candidate authority and query/peer-group authority. Re-signed typed substitutions fail before artifact I/O.
- Manifest input now passes through duplicate-key-rejecting exact canonical JSON parsing before contract validation and additionally pins registry decision/descriptor evidence, population/universe identities and counts, seed, serialization and PCA policies. Fitting rejects every existing destination ancestor that is a symlink or resolves to a different path.
- Exactly tied PCA groups round their symmetrized invariant projector to the fixed 15-decimal canonicalization precision before ordered standard-axis Gram-Schmidt. Untied groups retain their existing sign/order bytes; transformed vectors are derived after final components are chosen. A genuine 45-degree rotation and sign/permutation now produce exact identical tied bases.
- Manifest loading additionally rejects any self-consistent descriptor that declares big endianness or Fortran order. The production-API suite directly covers exact all-six ranking lists, all-family payloads/scores, byte-stable builds, typed forgeries, canonical-manifest duplicate keys, ancestor symlinks, tied-basis rotation invariance and re-signed descriptor attacks.

## Tests run

- `UV_CACHE_DIR=/private/tmp/w05-uv-cache uv run --no-sync ruff format --check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py` — exit 0; five files formatted.
- `UV_CACHE_DIR=/private/tmp/w05-uv-cache uv run --no-sync ruff check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py` — exit 0.
- `UV_CACHE_DIR=/private/tmp/w05-uv-cache uv run --no-sync mypy src/scouting/m0 src/scouting/modeling` — exit 0; four source files checked.
- `UV_CACHE_DIR=/private/tmp/w05-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_m0_models.py tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/contracts/test_w05_m0_contracts.py` — exit 0; 69 passed.
- `UV_CACHE_DIR=/private/tmp/w05-uv-cache uv run --no-sync lint-imports` — exit 0; three import contracts kept.
- `UV_CACHE_DIR=/private/tmp/w05-uv-cache uv run --no-sync python scripts/verify_local_only.py` — exit 0; PASS.
- `shasum -a 256 runs/w05/m0-baseline-v1/{arrays.npz,manifest.json,configuration.json,candidate-universe.json} configs/models/w05-m0-baselines-v1.json tests/fixtures/w05/m0-development-{candidates,queries}-v1.json` — exit 0; frozen physical identities below were exact.
- `git diff --check` — not run: R6 expressly forbids all Git operations; no Git command was issued.

## Artifacts/evidence

- Source identities: configuration logical `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`, registry `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644`, taxonomy `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`, selected population `60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086`, metadata population `b5efb54c2c30524ae5483a5082d32c391cff68be398e02a54506772b4b29fe21`, query projection `1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c`.
- Selected artifact: ID `9a0d43c6-d177-51be-8280-3bf02bedbc99`, manifest logical digest `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`; physical SHA-256 arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`, manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`, configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`, universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.
- Fixture physical SHA-256: candidates `5c6f4c26c2f9c71bacb1b13e80d5872b556001f55462a9cc359bf24be06317fc`; queries `1352ed759db30b4c430644893e558aa089e24153193f934cd124373cb6e29157`.
- Exact payloads / scores: metadata `19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee` / `0.1111111111111111`; raw `3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36` / `0.3333333333333333`; robust `ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc` / `1.0`; weighted `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` / `1.0`; PCA `90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971` / `1.0`; role-aware `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` / `1.0`.
- Full ranking lists are executable exact constants in `tests/unit/test_w05_m0_models.py`: metadata list; raw list; and the identical robust/weighted/PCA/role-aware similarity list. The command created and verified every family under `/private/tmp/w05-r6-evidence-4anrfd63`.

## Risks

- This is unchanged constructed synthetic-development-only evidence. It is not W06 evaluation, validation, expert evidence, provider evidence, a recruitment-outcome claim, protected evidence, production evidence, transfer or effectiveness evidence.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside allowed_paths: confirmed.

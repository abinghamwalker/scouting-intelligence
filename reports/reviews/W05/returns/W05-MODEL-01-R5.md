# Subagent return

## Task

- task_id: W05-MODEL-01
- objective: Close the frozen R4 M0 typed-authority, full-population, schema, safe-runtime and adversarial-test defects without changing fixture bytes, arrays or scores.

## Files changed

- configs/models/w05-m0-baselines-v1.json
- src/scouting/m0/__init__.py
- src/scouting/m0/core.py
- src/scouting/modeling/baselines.py
- tests/unit/test_w05_m0_models.py
- runs/w05/m0-baseline-v1/arrays.npz
- runs/w05/m0-baseline-v1/manifest.json
- runs/w05/m0-baseline-v1/configuration.json
- runs/w05/m0-baseline-v1/candidate-universe.json
- reports/reviews/W05/returns/W05-MODEL-01-R5.md

## Summary

- Replaced mapping-based configuration admission with the source-pinned immutable `M0Configuration`, explicit scalar/tuple/digest fields, strict canonical JSON/type validation and a single internal canonical mapping projection. The accepted R5 configuration digest is `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`; the selected `configuration.json` is byte-identical to the source config.
- Added immutable candidate and query fixture authorities. They reproduce exact canonical fixture bytes, logical identities, root/nested shape, 18-row ordering, feature materialisation, taxonomy membership, dependency identity/lineage, cutoff, claims and cross-pins. No fit/load/check API accepts loose candidate/query/role/peer-group mappings.
- The selected six-feature full candidate projection digest is `60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086`; the independently derived metadata-control projection digest is `b5efb54c2c30524ae5483a5082d32c391cff68be398e02a54506772b4b29fe21`; query projection remains `1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c`.
- Artifact load recomputes exact candidate universe, family schema, full lineage, model/index names, immutable artifact UUID and config-pinned array payload. It rejects mapping bypasses, canonical re-signs, symlink roots, unsafe ZIP members, object/dtype/shape/order/digest drift, malformed memberships and unsafe exclusions/exemplars. Loaded nested state and arrays are immutable.
- Metadata uses its accepted three-value schema; the five remaining families retain the frozen six-feature schema. PCA returns six original-feature contributions via the deterministic symmetric projection `C.T diag(q*c/(||q|| ||c||)) C`, with distance `1 + sum(contributions)`.
- Replaced the two smoke tests with direct all-family/rebuild/reload/PCA/exemplar/authority/re-sign/symlink/ZIP adversarial coverage using only production APIs and the one runtime scorer.

## Tests run

- `uv run ruff format --check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py`
  - exit status: 0
  - result: 5 files formatted.
- `uv run ruff check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py`
  - exit status: 0
  - result: all checks passed.
- `uv run mypy src/scouting/m0 src/scouting/modeling`
  - exit status: 0
  - result: success; 4 source files checked.
- `uv run pytest -q tests/unit/test_w05_m0_models.py tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: 65 passed; dedicated M0 suite contributes 5 direct adversarial tests.
- `uv run lint-imports`
  - exit status: 0
  - result: approved dependency direction retained.
- `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: local-only verification PASS.
- Staged all six families in `/private/tmp/w05-m0-r5-final-stage-typtvl7a` after the final config source pin was frozen, then wrote the selected path once.
  - exit status: 0
  - result: each staged payload exactly matched its frozen digest; selected role-aware artifact was then written once at `runs/w05/m0-baseline-v1/` and reloaded through the runtime.

## Artifacts/evidence

- Frozen physical fixture digests: candidates `5c6f4c26c2f9c71bacb1b13e80d5872b556001f55462a9cc359bf24be06317fc`; queries `1352ed759db30b4c430644893e558aa089e24153193f934cd124373cb6e29157`. Frozen logical fixture digests remain candidates `710c38554f33f8f650d814df1fee3c8bac7a8a2bc22804f93e3b9a8dfd1e50d9`; queries `fb027563b3f99f563d43f1b909c535f860f3d04d2d8aa0ed44e902fd2a37e900`.
- Staged artifact identities (family: artifact UUID / manifest digest / payload digest): metadata `5c3a6171-a333-5bd9-b500-82a0b24106f1` / `be1e17efdf4d614dc25bca9085b75d59144f8e18b34f313b94418b0e31ad5f6a` / `19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee`; raw `09d3296a-0d5a-5892-bfdd-5820073fe792` / `b277d26404a7010b0c0bb7440daef20242e9575df64efaed0ffc317f21db2f68` / `3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36`; robust `e4ab4661-faf4-5065-b43d-0d8fe8ba3c7d` / `069beffefba0ead2fd8c55515f75fe98a65c1085ba64f32367ee09faa56830e2` / `ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc`; weighted `33c7fd4b-21f6-52d7-be69-95277c0691b3` / `968f7f3b2d5b77578320851dccb00c7287e10bfcb39220ca8b9f9a022cbd12b8` / `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801`; PCA `c648fc03-4eec-510c-bf41-0b50515c1f47` / `d3970a614859ae98e285e47c1b2473c60a1f8743f563e68c85e4f6aa53cab035` / `90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971`; role-aware `9a0d43c6-d177-51be-8280-3bf02bedbc99` / `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9` / `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801`.
- Selected artifact: `runs/w05/m0-baseline-v1/`; file SHA-256 values are arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`, manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`, configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006` (identical to `configs/models/w05-m0-baselines-v1.json`), universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.
- One frozen all-18 leave-one-out development-only parity check: metadata `0.1111111111111111`, raw `0.3333333333333333`, robust `1.0`, weighted `1.0`, PCA `1.0`, role-aware `1.0`. Role-aware ranking digests are the 18 deterministic values emitted by the selected runtime build; the direct suite checks count, reload and scorer parity. R1 negative evidence is retained unchanged: metadata/raw `0.8518518518518519`; robust/weighted/PCA/role-aware `0.7777777777777778`; the 729-vector lattice and eight fixed variants did not improve that prior failed construction.

## Risks

- These results are deliberately constructed synthetic-development readiness evidence only. They are not validation, protected evidence, external-expert evidence, recruitment effectiveness, robustness, transfer, provider/Wyscout evidence, production evidence or a W06 claim.
- The selected artifact is local and source-pinned; master independent review must reproduce this evidence before acceptance.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

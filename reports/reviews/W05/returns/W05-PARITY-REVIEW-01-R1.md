# Subagent return

## Task

- task_id: W05-PARITY-REVIEW-01-R1
- objective: Independently prove W05 training-serving and batch-request parity, artifact reload determinism, exact evidence lineage, and the declared synthetic M0 control comparison.

## Files changed

- reports/reviews/W05/w05-training-serving-parity-independent-review-R1.md
- reports/reviews/W05/returns/W05-PARITY-REVIEW-01-R1.md

## Summary

- verdict: PASS; no W05 P0/P1 reproduced.
- exact registry/materialization/artifact/scorer/serving feature order and schema identity proved.
- two temporary roots reproduced byte-identical all-six artifacts, rankings, distances, contributions, PCA orientation, and scores; both roots were removed.
- direct scorer, single, batch, replay, and fresh-core query-player/exemplar results matched exactly.
- request identity, semantic filter permutation, evidence states, explanations, confidence, temporal lineage, and fail-closed substitutions passed.
- registered artifact hashes remained exact before and after every probe.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w05-parity-review-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/unit/test_w05_m0_models.py tests/contracts/test_w05_m0_contracts.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py`
  - exit status: 0
  - result: 75 passed in 1.34s
- command: packet `ruff check` command
  - exit status: 0
  - result: all checks passed
- command: packet `mypy` command
  - exit status: 0
  - result: no issues in nine source files
- command: `UV_CACHE_DIR=/private/tmp/w05-parity-review-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken
- command: `UV_CACHE_DIR=/private/tmp/w05-parity-review-uv-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS, no failures
- command: `UV_CACHE_DIR=/private/tmp/w05-parity-review-uv-cache uv run --no-sync python /private/tmp/w05_parity_probe.py`
  - exit status: 0
  - result: all parity, all-six rebuild, replay, cutoff, pin, lineage, score, hash-guard, and cleanup assertions passed
- command: `UV_CACHE_DIR=/private/tmp/w05-parity-review-uv-cache uv run --no-sync python /private/tmp/w05_parity_resign_probe.py`
  - exit status: 0
  - result: all 19 re-signed manifest/universe/configuration attacks rejected; temporary root removed

## Artifacts/evidence

- reports/reviews/W05/w05-training-serving-parity-independent-review-R1.md
- selected artifact: `9a0d43c6-d177-51be-8280-3bf02bedbc99`
- selected manifest: `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`
- result digest: `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`
- result/run/M0 IDs: `8a0c3594-0b40-572a-8a9a-aecaa0b6052e`, `332c42c4-6b0d-5fd5-b8aa-f09ae9ae501c`, `e77948a1-2987-514d-a585-cd54015e2152`
- lineage hash: `c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491`
- physical hashes: arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`; manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`; configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`; universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.
- exact scores: metadata `0.1111111111111111`; raw Euclidean `0.3333333333333333`; robust cosine `1.0`; weighted cosine `1.0`; PCA `1.0`; selected role-aware `1.0`.

## Risks

- no P0/P1 residual reproduced.
- existing P2 artifact-preflight ordering remains nonblocking: authorized local bytes may be read before some semantic rejection, but the scorer is not called and no result/evidence is emitted.
- evidence remains constructed synthetic-development resemblance only, not W06/protected, robustness, calibration, provider/expert, transfer, recruitment-outcome, recommendation, or production evidence.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed; all proof scripts and materialized roots were under `/private/tmp`, and all created materialization roots were removed

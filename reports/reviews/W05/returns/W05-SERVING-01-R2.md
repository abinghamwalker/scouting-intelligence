# Subagent return

## Task

- task_id: W05-SERVING-01
- objective: Correct the five reproduced serving P1 classes while retaining the accepted read-only M0 artifact, scorer, contracts, and claim boundary.

## Files changed

- src/scouting/serving/m0.py
- tests/integration/test_w05_m0_serving.py
- reports/reviews/W05/returns/W05-SERVING-01-R2.md

## Summary

- Every `M0ServingCore.serve` call now rebuilds the full pinned request from its Python semantic dump before artifact I/O, recomputes nested query/exclusion identities, and checks every accepted selected-artifact pin. Constructed or copied stale query/pin payloads fail before the loader or scorer.
- Result, run, and M0 UUIDs now use separate domains over the complete validated pinned-request digest, core version, and accepted artifact identity; request-byte changes cannot collide.
- Hard constraints are fully parsed, typed, operator-checked, and canonicalized before candidate scanning. Invalid later predicates fail closed regardless of an earlier false predicate; equivalent plans execute identically without rewriting the order-sensitive pinned request payload.
- Synthetic-development confidence is now explicitly `limited` with `synthetic_development_only` and `no_recommendation_evidence` limitations. The DataConfidenceEvidence and legacy DATA_CONFIDENCE dimension satisfy the exact contract projection `(reason_codes, limitations, applicability_limited)`. No-constraint requests no longer claim a constraint action.
- Temporal evidence now includes explicit candidate feature-row clocks and per-row feature-schema dependencies derived from player ID and exact row-lineage digest. Raw dependencies remain source manifests; no model/index/taxonomy availability time is fabricated.
- The accepted `scouting.m0` loader and `LoadedM0Artifact.score` remain the sole artifact/scoring path. Production API tests now spy both, cover stale mutation, pin rejection before loading, UUID collision resistance, filter-order fail closure/canonical execution, confidence projection, and truthful row watermarks.

## Tests run

- `shasum -a 256 runs/w05/m0-baseline-v1/arrays.npz runs/w05/m0-baseline-v1/manifest.json runs/w05/m0-baseline-v1/configuration.json runs/w05/m0-baseline-v1/candidate-universe.json` — exit 0 before and after checks; exact same four frozen hashes below.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync ruff format --check src/scouting/serving/m0.py src/scouting/serving/__init__.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py` — exit 0; four files already formatted.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync ruff check src/scouting/serving/m0.py src/scouting/serving/__init__.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py` — exit 0; all checks passed.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync mypy src/scouting/serving/m0.py src/scouting/serving/__init__.py` — exit 0; no issues in two source files.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync pytest -q tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py tests/unit/test_w05_m0_models.py tests/contracts/test_w05_m0_contracts.py` — exit 0; `44 passed in 1.08s`.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync lint-imports` — exit 0; all three contracts kept.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync python scripts/verify_local_only.py` — exit 0; PASS, no failures.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync python -c 'import runpy; values = runpy.run_path("tests/integration/test_w05_m0_serving.py"); core = values["core"].__wrapped__(); result = values["serve_m0_request"](core, values["_request"]()); print(result.result_digest)'` — exit 0; canonical R2 query-player result digest emitted below.

## Artifacts/evidence

- shared core: `m0-shared-core-v1`.
- selected artifact ID: `9a0d43c6-d177-51be-8280-3bf02bedbc99`; manifest digest: `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`; configuration digest: `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`; registry digest: `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644`; taxonomy digest: `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`.
- canonical R2 query-player result digest: `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`.
- frozen physical SHA-256 before/after: arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`; manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`; configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`; candidate universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Risks

- The corrected result remains constructed synthetic-development evidence only. It is not W06/W10 evaluation, robustness, expert/provider evidence, a recruitment outcome, transfer/effectiveness claim, protected evidence, or production recommendation.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

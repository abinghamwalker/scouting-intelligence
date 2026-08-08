# Subagent return

## Task

- task_id: W05-SERVING-01
- objective: Implement one read-only deterministic M0 retrieval/explanation core shared unchanged by request and batch entry points.

## Files changed

- src/scouting/serving/m0.py
- src/scouting/serving/__init__.py
- tests/integration/test_w05_m0_serving.py
- tests/e2e/test_w05_m0_retrieval.py
- reports/reviews/W05/returns/W05-SERVING-01-R1.md

## Summary

- Added `M0ServingCore` version `m0-shared-core-v1`, plus thin `serve_m0_request` and `serve_m0_batch` calls. The core permits only the exact registered `runs/w05/m0-baseline-v1` root and invokes the accepted `scouting.m0.load_m0_artifact` and its sole `score` path; it exposes no fit/write/update interface and imports no modeling, features, or provider/source module.
- Every result validates all request/query/artifact pins, deterministic UUIDs and digest, strict before-cutoff feature/dependency lineage, exact source/feature/model/index dependency projection, canonical tie ordering, declared candidate filters, exclusions, taxonomy role restriction, and query-player or sorted-exemplar modes.
- Evidence cards always expose the six canonical dimensions. Style is an explicit monotonic distance view, role evidence is taxonomy-bound, impact/trajectory/transfer risk are zero-sentinel unavailable non-ranking dimensions, and separately constructed data-confidence evidence never changes rank. The result and all candidates retain `claim_boundary=resemblance_only`; no overall, percentage, probability, value, transfer, success, or recommendation field is emitted.
- Tests prove request/batch/reload byte identity, shared-loader use, selected artifact byte preservation, filters, exemplar mode, unsupported-filter rejection, registered-root substitution rejection, and no fit/write/update surface.

## Tests run

- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync ruff format --check src/scouting/serving/m0.py src/scouting/serving/__init__.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py` — exit 0; four files already formatted.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync ruff check src/scouting/serving/m0.py src/scouting/serving/__init__.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py` — exit 0; all checks passed.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync mypy src/scouting/serving/m0.py src/scouting/serving/__init__.py` — exit 0; no issues in two source files.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync pytest -q tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py tests/unit/test_w05_m0_models.py tests/contracts/test_w05_m0_contracts.py` — exit 0; `42 passed in 1.02s`.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync lint-imports` — exit 0; all three dependency contracts kept and serving never imports provider adapters.
- `UV_CACHE_DIR=/private/tmp/w05-serving-uv-cache uv run --no-sync python scripts/verify_local_only.py` — exit 0; `PASS`, no failures.
- `shasum -a 256 runs/w05/m0-baseline-v1/arrays.npz runs/w05/m0-baseline-v1/manifest.json runs/w05/m0-baseline-v1/configuration.json runs/w05/m0-baseline-v1/candidate-universe.json` — exit 0; exact frozen hashes reproduced below.

## Artifacts/evidence

- shared core: `m0-shared-core-v1`.
- selected artifact ID: `9a0d43c6-d177-51be-8280-3bf02bedbc99`; manifest digest: `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`; configuration digest: `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`; registry digest: `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644`; taxonomy digest: `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`.
- example query-player result digest: `6e05031833c34d6b1dbab1f23e1e7eff8e7edcfe022092b267bfd4a4b1221996`; direct request, one-element batch, and immediate reload emitted byte-identical canonical JSON and this same digest.
- physical artifact SHA-256: arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`; manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`; configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`; candidate universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Risks

- The accepted artifact is constructed synthetic-development evidence only. This is not W06 evaluation, validation, robustness, expert/provider evidence, protected evidence, recruitment outcome, transfer/effectiveness, or production evidence.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

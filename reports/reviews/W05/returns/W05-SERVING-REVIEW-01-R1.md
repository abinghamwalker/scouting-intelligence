# Subagent return

## Task

- task_id: W05-SERVING-REVIEW-01
- objective: Independently prove or reject the W05 request/batch serving R1 under the six blocker tests and mandatory fresh attacks.

## Files changed

- reports/reviews/W05/w05-m0-serving-independent-review-R1.md
- reports/reviews/W05/returns/W05-SERVING-REVIEW-01-R1.md

## Summary

- Verdict: **REWORK**; no P0 and five reproducible P1 blocker classes.
- Reproduced stale nested resolved-query digest admission, distinct-request UUID collisions, order-dependent invalid-filter admission, false no-constraint/synthetic-applicability claims, and temporal watermark understatement/fabricated derived availability.
- Confirmed the positive boundary: request and batch use the same `M0ServingCore`, accepted loader, and `LoadedM0Artifact.score`; same-request and fresh-core bytes are stable; six dimensions and explanation projection are structurally exact; no second scoring implementation or direct training/provider/write path was found; all four artifact files remained immutable.
- Smallest bounded corrections are stated per P1 in the independent review. W06/W10 quality, expert/provider validation, production readiness, and outcomes were not used to fail R1.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w05-serving-review-uv-cache uv run --no-sync pytest -q tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py tests/unit/test_w05_m0_models.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: `42 passed in 1.00s`.
- command: inline `uv run --no-sync python -c` fresh boundary probe covering shared loader/scorer spies, batch/request bytes, carried-digest bypass, request UUID collisions, invalid-filter order, no-constraint/applicability reasons, and emitted-versus-feature-row watermarks
  - exit status: 0
  - result: two loader and two scorer calls for request+batch; identical same-request bytes; all five P1 classes reproduced.
- command: inline `uv run --no-sync python -c` fresh-core and valid-filter permutation probe
  - exit status: 0
  - result: fresh-core bytes equal; semantically identical valid filter permutations selected identical candidates but produced different result digests.
- command: inline `uv run --no-sync python -c` independently re-signed manifest and request-pin substitution matrix
  - exit status: 0
  - result: all 17 behavior-bearing manifest identity substitutions and all 18 request-pin substitutions were rejected; no artifact file was modified.
- command: `UV_CACHE_DIR=/private/tmp/w05-serving-review-uv-cache uv run --no-sync ruff check src/scouting/serving/m0.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w05-serving-review-uv-cache uv run --no-sync mypy src/scouting/serving/m0.py`
  - exit status: 0
  - result: no issues in one source file.
- command: `UV_CACHE_DIR=/private/tmp/w05-serving-review-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept.
- command: `UV_CACHE_DIR=/private/tmp/w05-serving-review-uv-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS, no failures.
- command: `shasum -a 256 runs/w05/m0-baseline-v1/{arrays.npz,manifest.json,configuration.json,candidate-universe.json}` before and after every probe
  - exit status: 0
  - result: all four hashes remained exact and unchanged.

## Artifacts/evidence

- reports/reviews/W05/w05-m0-serving-independent-review-R1.md
- shared core: `m0-shared-core-v1`
- artifact ID: `9a0d43c6-d177-51be-8280-3bf02bedbc99`
- manifest digest: `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`
- stable baseline result digest: `6e05031833c34d6b1dbab1f23e1e7eff8e7edcfe022092b267bfd4a4b1221996`
- physical hashes: arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`; manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`; configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`; candidate universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Risks

- P1 request-integrity, identity-collision, filtering, evidence-truth, and temporal-lineage blockers remain until bounded correction and fresh independent review.
- No P0 reproduced. No additional P2 is needed for this verdict; W06/W10 evaluation and production claims remain deferred.

## Follow-up items

- Issue bounded serving rework for the five P1 classes in the independent review, then rerun all mandatory attacks with direct normal-validation/model-construction, collision, filter-order, synthetic-limitation, and feature-row watermark probes.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

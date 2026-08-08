# Subagent return

## Task

- task_id: W05-SERVING-REVIEW-01
- objective: Independently prove or reject the bounded W05 serving R2 correction under the original six blocker tests and every reproduced R1 P1 attack.

## Files changed

- reports/reviews/W05/w05-m0-serving-independent-review-R2.md
- reports/reviews/W05/returns/W05-SERVING-REVIEW-01-R2.md

## Summary

- Verdict: **PASS**; no P0 or P1 reproduced.
- All five R1 P1 classes are closed: nested revalidation, request-bound UUID collisions, filter short-circuiting, false reasons/synthetic applicability, and understated/fabricated temporal evidence.
- Confirmed one public core, accepted loader, and `LoadedM0Artifact.score`; exact request/batch/fresh-core bytes; order-sensitive request identity with semantically identical filter execution; exact six states/confidence/explanations; frozen ranking geometry and artifact bytes.
- P2 only: some semantically invalid normally typed requests read the exact authorized local artifact before rejection. The scorer remains uncalled and no result/evidence/claim is emitted. This does not block R2 or begin W06/W10.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w05-serving-review-uv-cache uv run --no-sync pytest -q tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py tests/unit/test_w05_m0_models.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: `44 passed in 1.09s`.
- command: inline public single/batch stale `model_copy`/`model_construct` matrix with loader/scorer spies
  - exit status: 0
  - result: 34 behavior/pin mutations rejected through both APIs; rejected loader/scorer calls both zero; mapping rejected and ordinary typed input accepted.
- command: inline normally validated canonical-request collision/replay matrix
  - exit status: 0
  - result: 12 distinct admitted request cases; all three UUID domains independently unique; same single/batch/fresh-core JSON bytes exact.
- command: inline all-operator, invalid-order, and valid-permutation constraint matrix
  - exit status: 0
  - result: all 11 field/operator combinations executed; all 12 invalid permutations rejected; valid permutations had exact semantic scoring/state/explanation parity while retaining distinct request-bound IDs/digests.
- command: inline query-player/exemplar/exclusion/responsibility signal matrix
  - exit status: 0
  - result: admitted query-player, sorted-exemplar, and exclusion modes reproduced; absent/both/unknown/excluded/unknown-responsibility requests rejected without scoring.
- command: inline feature-row/source cutoff and accepted-lineage matrix
  - exit status: 0 after correcting a probe-only quoting error
  - result: all eight cutoff/after attacks rejected before scoring; exact 18 source plus 18 per-row feature dependencies, max clocks, lineage hash, and candidate binding reproduced; no fabricated model/index timestamp dependencies.
- command: inline re-signed pin/root/full-wire/frozen-geometry matrix
  - exit status: 0
  - result: all 17 behavior-bearing re-signed manifest substitutions and missing/extra/wrong roots rejected; public scored rows exactly matched the accepted scorer; six-state, limitation, reason, explanation, and forbidden-positive-claim checks passed.
- command: inline AST/public-surface and symlink-root inspection
  - exit status: 0
  - result: no forbidden direct imports; only public core method `serve`; fit/write/update/train/save absent; `/tmp` symlink root rejected.
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
- command: four-file `shasum -a 256` before and after every probe
  - exit status: 0
  - result: all frozen hashes remained exact.

## Artifacts/evidence

- reports/reviews/W05/w05-m0-serving-independent-review-R2.md
- shared core: `m0-shared-core-v1`
- artifact ID: `9a0d43c6-d177-51be-8280-3bf02bedbc99`
- manifest digest: `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`
- canonical R2 result digest: `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`
- result/run/M0 IDs: `8a0c3594-0b40-572a-8a9a-aecaa0b6052e`, `332c42c4-6b0d-5fd5-b8aa-f09ae9ae501c`, `e77948a1-2987-514d-a585-cd54015e2152`
- result lineage hash: `c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491`
- physical hashes: arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`; manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`; configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`; candidate universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Risks

- No P0/P1 residual. P2 preflight ordering is nonblocking and produces no result, ranking, evidence, or claim.
- Constructed synthetic development remains non-recommendation evidence and is not W06/W10 evaluation or production evidence.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

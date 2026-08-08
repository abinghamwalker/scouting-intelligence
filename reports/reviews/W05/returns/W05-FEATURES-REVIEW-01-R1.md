# Subagent return

## Task

- task_id: W05-FEATURES-REVIEW-01-R1
- objective: Independently verify the W05 feature registry, exact W04 bridge, synthetic-only separation, deterministic formulas/states and temporal-lineage fail-closed behavior.

## Files changed

- reports/reviews/W05/w05-feature-registry-independent-review-R1.md
- reports/reviews/W05/returns/W05-FEATURES-REVIEW-01-R1.md

## Summary

- Verdict: **REWORK — P0: 0; P1: 3; P2: 0**.
- P1-01: all affected hashes can be recomputed and a replacement root, crossed W04/synthetic family IDs, changed W04 descriptor, synthetic provider/expert description and replacement fixture identity are accepted because W05 root identities are not externally pinned.
- P1-02: arbitrary counts and a fabricated non-SHA dependency digest materialize as W04 real-governed Gold when the caller merely supplies `gold_row_state=accepted`; no accepted W04 product/Gold/row lineage is authenticated.
- P1-03: the canonical W04 bridge sets and the loader requires `production_evidence=true` and `protected_evaluation=true`, conflicting with the accepted W04 research-only boundary, G-W05's “no validation claim yet” rule and W06 ownership of protected evaluation.
- Current positive behavior remains reproducible: exact-four order, all 13 descriptor fields, 22 fixture rows, five distinct value/absence states, Decimal formulas, deterministic repeat materialization and strict row/dependency cutoff equality rejection.

## Tests run

- command: `uv run pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: 0
  - result: 183 passed in 9.68s.
- command: `uv run ruff check src/scouting/features tests/unit/test_w05_features.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/features`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `uv run lint-imports`
  - exit status: 2
  - result: the shared uv cache denied `/Users/adrian/.cache/uv/sdists-v9/.git` before import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-features-review-01-r1-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken; 42 files and 81 dependencies analyzed.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 checks passed.
- command: `UV_CACHE_DIR=/tmp/w05-features-review-01-r1-uv-cache uv run --no-sync python /tmp/w05_features_review_adversarial.py`
  - exit status: 0
  - result: reproduced current identity/state/time positives and all three P1 classes, including fully re-signed substitutions and unauthenticated W04 Gold admission.

## Artifacts/evidence

- reports/reviews/W05/w05-feature-registry-independent-review-R1.md
- registry logical digest: `5cf2864f763d4670a2baa882c1db32c88cf194f3da0b573b148be50641edd946`
- registry physical SHA-256: `c9c970a9209451679c471326719df30826dfabbbe62f8cb91897b89f494a105d`
- fixture logical digest: `cd5de08b648a94b0c8d3f2c8e5e84d330887381621492641a5e1514bbf8fc8a7`
- fixture physical SHA-256: `ff0a10ca4c093f8959b6319ee72bfbc12362e426f59c7f412e6c53b03b1196a1`
- W04 candidate physical SHA-256: `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`
- adversarial W04 fabricated-lineage hash admitted: `d2b5579de9dcd0eee88af739acef88764be1d914fe258e7a9e57b43bcff2fa1d`

## Risks

- Until bounded rework pins accepted W05 identities, authenticates accepted W04 Gold lineage and removes the premature production/protected claims, substituted feature semantics or fabricated W04 evidence can cross the public feature boundary while appearing internally self-consistent.
- The exact import-lint command is affected only by the pre-existing shared-cache permission issue; the packet-authorized isolated `--no-sync` execution passed and is not a product blocker.

## Follow-up items

- Bounded rework for P1-01 through P1-03, followed by fresh independent review with fully re-signed nested attacks.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

# Subagent return

## Task

- task_id: W05-CONTRACTS-TRUTH-REVIEW-03
- objective: Independently review and adversarially challenge the final split W05 contract truth surface.

## Files changed

- reports/reviews/W05/w05-m0-contract-truth-independent-review-R1.md
- reports/reviews/W05/returns/W05-CONTRACTS-TRUTH-REVIEW-03-R1.md

## Summary

- Verdict: **REWORK — P0: 0; P1: 3; P2: 0**.
- Reproduced digest-valid contradictions for MEASURED with legacy zero, state/legacy reason drift, and DATA_CONFIDENCE state-reason drift.
- Reproduced W04 real-governed manifests admitted as `ROLE_AWARE_RESTRICTION` and `METADATA_CONTROL` despite the accepted feature/claim boundary.
- Reproduced fitting-population/feature-matrix axis drift and PCA component count above both fitting-sample and feature bounds.
- Confirmed exact explanation equality, taxonomy content identity, negative-zero rejection, basic family topology, W04 exact-four feature width, and separate W04 candidate/decision/descriptor identities.
- Reproduced the unchanged W04 descriptor digest exactly as `fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e`.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: 0
  - result: 208 passed in 9.63s.
- command: `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/m0.py`
  - exit status: 0
  - result: success; no issues in 1 source file.
- command: `uv run lint-imports`
  - exit status: 2
  - result: sandbox denied read of `/Users/adrian/.cache/uv/sdists-v9/.git`.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-truth-review-03-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept; 0 broken; 40 files and 79 dependencies analyzed.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: status PASS; failures `[]`.
- command: strict public-model direct probes through `uv run python -B -`
  - exit status: 0 for the completed probe set
  - result: accepted all five requested contradiction classes; exact evidence is in the independent review.
- command: `uv run python -c '<derive W04 descriptor digest from unchanged accepted YAML>'`
  - exit status: 0
  - result: `fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e`.

## Artifacts/evidence

- reports/reviews/W05/w05-m0-contract-truth-independent-review-R1.md
- reports/reviews/W05/returns/W05-CONTRACTS-TRUTH-REVIEW-03-R1.md
- W04 descriptor digest: `fb562ddee18e008f26b9c865772ef217cb5b34243ae73eb69fad815da291778e`

## Risks

- P1 false evidence-state/confidence claims remain possible in a digest-valid result.
- P1 W04 evidence authority can be represented under incompatible model-family claims.
- P1 fitting/PCA manifest shapes can describe impossible training/artifact relationships.
- The exact import-lint command is blocked only by the unreadable shared uv cache; the isolated-cache equivalent passed.

## Follow-up items

- Add exact state-to-legacy score/reason and DATA_CONFIDENCE-state projection rules.
- Add explicit W04 evidence-class/model-family compatibility validation.
- Bind `FEATURE_MATRIX` to fitting population and cap PCA components by fitting samples and feature count.
- Add direct regression tests for each reproduced attack, then obtain fresh independent review.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

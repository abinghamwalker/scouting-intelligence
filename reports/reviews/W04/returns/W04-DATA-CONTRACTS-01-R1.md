# Subagent return

## Task

- task_id: W04-DATA-CONTRACTS-01-R1
- objective: Implement only the closed W04 Wyscout data-contract surface required by the smallest conformant in-memory one-match raw-to-Gold slice, without serializers, product bytes, manifests, receipts, runtime, or builds.

## Files changed

- src/scouting/contracts/wyscout_data.py
- tests/contracts/test_wyscout_data_contracts.py
- reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R1.md

## Summary

- Added strict, deeply immutable, extra-forbidden Wyscout contract models and deterministic canonical JSON for Decimal-preserving raw evidence.
- Bound the exact seven source kinds and path mapping, source-row and lineage evidence, seven-field accepted-authority references, Bronze known/rejected contracts, eight Silver product rows, Gold temporal/coverage/feature/player-window contracts, and Bronze-to-Silver-to-Gold manifest contracts.
- Closed action-subevent coercion, exact five-country and 17-path-role rules, exact primary keys, neutral role context, six coverage dimensions, four supported count features, five ordered temporal dependencies, and clock-free semantic proof.
- Added a fully in-memory one-match/seven-family fixture with negative matrices for discriminators, subevents, paths, temporal lineage, coverage, feature shape, immutability, serializer ownership, canonicalization, and exact enum/digest validation. No product, manifest, receipt, or data bytes are written.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: 2 files already formatted.
- command: `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: All checks passed.
- command: `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: Success; no issues found in 2 source files.
- command: `uv run lint-imports`
  - exit status: 0
  - result: 30 files and 46 dependencies analyzed; 3 contracts kept, 0 broken.
- command: `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: 0
  - result: 225 passed in 67.51s.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 repository local-only checks passed.

## Artifacts/evidence

- src/scouting/contracts/wyscout_data.py — SHA-256 `9d90641965ef6d9351d76785d5729cc932ed7ea3cae11ff931dcef3279148452`
- tests/contracts/test_wyscout_data_contracts.py — SHA-256 `568859f5879766c0470169e480177c3089b26788456c3133294e86ba2b0dc69a`
- All seven packet-fixed identity, source-manifest, field, possession, supported-feature, product-preimage, and schema-preimage SHA-256 bindings were rechecked and match exactly.

## Risks

- No known residual implementation risk. `uv run lint-imports` required the approved sandbox escalation solely to read uv's shared cache; the required command then passed unchanged.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

# Subagent return

## Task

- task_id: W04-DATA-CONTRACTS-01-R3
- objective: Correct the frozen W04 executable data contracts and focused tests so all seven independently reviewed R2 P1 findings and both additional master P1 findings fail closed at public constructors without changing accepted authorities, preimages, source evidence, or the four-feature roster.

## Files changed

- `src/scouting/contracts/wyscout_data.py`
- `tests/contracts/test_wyscout_data_contracts.py`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R3.md`

## Summary

- Bound `ActionSubeventOutcome` to raw event/subevent evidence and exact helper-derived output.
- Derived possession eligibility from the accepted 36-pair possession-v2 roster, including the exact eight ineligible pairs, and closed resolved counts against contributing possession membership.
- Made completion path plus zero-based ordinal the physical source-row key; every Silver/Gold row selects exact source evidence, action ordinal derives from its selected action row, and match country derives from its selected match row.
- Enforced content-addressed identity dependency UUIDv5 derivation from the dynamic bundle digest alongside existing exact clocks, dependency order, and lineage hash.
- Embedded the complete accepted 119-row field-v2 registry without file access and generalized `BronzeRejectedField` while retaining the exact R21 subevent rejection matrix.
- Made player-match facts carry ordered actions/possessions and derive all three fact counts; Gold retains exactly those counts plus distinct match count.
- Derived all six Gold coverage dimensions from selected facts and derived exact applicability state/reason unions, including the frozen uncertainty reason.
- Required positive row and byte counts for every materialized Parquet manifest entry.
- Added named regression matrices for all nine finding families, the full 36-pair possession roster, all source families, identity substitutions, generic registry rows, evidence leakage, six coverage dimensions, applicability reasons, and Bronze/Silver/Gold zero materialization.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: 2 files already formatted
- command: `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: all checks passed
- command: `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: success, no issues in 2 source files
- command: `uv run lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken
- command: `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: 0
  - result: 437 passed
- command: `uv run bandit -q -r src/scouting/contracts/wyscout_data.py`
  - exit status: 0
  - result: no findings
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS, 25 checks and zero failures

## Artifacts/evidence

- `src/scouting/contracts/wyscout_data.py` SHA-256 before final return creation: `53abc69b85a1a60c13107a8b0a09ee6e066e792b1667c866cf9a9c3f5fd242ff`
- `tests/contracts/test_wyscout_data_contracts.py` SHA-256 before final return creation: `f13b5ccb8930bef22c94f74feeda1b66c87224704458c0460de022e66af3764b`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R3.md`

## Risks

- No product, manifest, receipt, runtime, serializer, provider, dependency, lock, accepted authority, preimage, or source byte was changed or created.
- Residual risk is limited to independent review of the bounded constructor semantics.

## Follow-up items

- Independent R3 review and master verification.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

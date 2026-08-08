# Subagent return

## Task

- task_id: W04-DATA-CONTRACTS-01-R4
- objective: Correct only the three independently reproduced R3 P1 failures in the frozen W04 executable data contracts and focused tests: fact-level six-dimension coverage authority, accepted-position feature eligibility, and final possession-v2 same-period sequence resolution.

## Files changed

- `src/scouting/contracts/wyscout_data.py`
- `tests/contracts/test_wyscout_data_contracts.py`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R4.md`

## Summary

- Made `SilverPlayerMatchFact` carry closed contributing lineup, action, possession, source-row, and temporal evidence and derive all six R20 coverage numerator/denominator pairs from it. Every dimension now rejects an internally consistent caller mutation from the evidence-derived value to `2/2`.
- Derived `coordinate_known_action_count` and successful coordinate coverage from the exact accepted `POSITION_PRESENT` predicate: cardinality one or two, finite axes, and every axis within inclusive `0..100`. Out-of-bounds, mixed-validity, and three-position anomalies remain unchanged as evidence while the whole action is excluded from the feature and numerator.
- Separated exact possession-v2 predicate admission from final deterministic resolution. Added complete canonical same-match/same-period sequence evidence, exact action binding, frozen decision transitions, period-end buffer closure, equal-clock uncertainty handling, and exact resolved-group membership.
- Ensured explicit accepted `UNMAPPED` decision pairs remain predicate-admitted but final-ineligible; action-team predicates without a canonical team remain predicate-unmapped.
- Made singleton/period-ending contested actions final-ineligible, allowed them to attach only to the exact following resolved possession, rejected incomplete/duplicate/cross-scope sequence evidence and same-team possession subsets, and derived fact resolved counts from exact single possession membership.
- Added named public-constructor regressions for every packet-required R4 finding family while retaining the exact four-feature roster and prior contract closures.

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
  - result: 452 passed
- command: `uv run bandit -q -r src/scouting/contracts/wyscout_data.py`
  - exit status: 0
  - result: no findings
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS, 25 checks and zero failures

## Artifacts/evidence

- `src/scouting/contracts/wyscout_data.py` SHA-256 before final return creation: `2ca2862550c48a8db899f25c26612d694a7ca8041416cf0aae4dcd39b5a2bb5e`
- `tests/contracts/test_wyscout_data_contracts.py` SHA-256 before final return creation: `0ddb9e2bd31dded899a68b7b6344cf17321dffe947ab6dffc98267eb918bdc69`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R4.md`

## Risks

- No product, manifest, receipt, runtime, serializer, provider, dependency, lock, accepted authority, preimage, source, R20, or R21 byte was changed or created.
- Residual risk is limited to independent review of the bounded constructor semantics.

## Follow-up items

- Independent R4 review and master verification.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

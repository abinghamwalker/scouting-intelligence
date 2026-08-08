# Subagent return: W04-DATA-CONTRACTS-REVIEW-01-R1

## Task

- Task ID: `W04-DATA-CONTRACTS-REVIEW-01`
- Revision: `R1`
- Role: independent reviewer
- Result: **REWORK**
- Finding counts: P0 `0`, P1 `10`, P2 `0`

## Files changed

- `reports/reviews/W04/wyscout-data-contracts-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-REVIEW-01-R1.md`

No implementation, test, authority, configuration, or producer-evidence file was changed.

## Summary

All packet-listed inputs were read in full and every fixed-input digest was independently reproduced. The complete prescribed check set passes, including the 225-test focused suite and all 25 local-only checks. Full-line review and direct-constructor adversarial probes nevertheless found ten open P1 contract-closure defects. The implementation therefore does not meet the zero-open-P0-P2 acceptance rule.

The required bounded rework covers raw-kind model closure, strict event/subevent enforcement, zero-ID rejection, decimal128 bounds, exact authority clocks, cross-layer lineage equality, coverage proof states, immutable manifest linkage, Gold reconciliation, and end-to-end source/rights provenance. These defects are correctable within the frozen W04 data-contract scope; no new architecture revision is supported by the executable evidence.

## Verification performed

- `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — PASS; 2 files already formatted
- `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — PASS
- `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — PASS; no issues in 2 source files
- `uv run lint-imports` — PASS; 3 contracts kept, 0 broken
- `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` — PASS; 225 passed in 69.07s
- `uv run python scripts/verify_local_only.py` — PASS; 25/25
- Read-only adversarial constructor probes — reproduced every behavior cited in the review

The first sandboxed `lint-imports` attempt encountered a uv-cache permission error. The exact command was rerun through the approved uv execution boundary and passed.

## Artifacts and fixed-input identity

- Independent review: `reports/reviews/W04/wyscout-data-contracts-independent-review-R1.md`
- Independent review SHA-256: `862fa5513cd261fd95bcd921fb52631c90af56ff930ce968682059879761dee2`
- `src/scouting/contracts/wyscout_data.py`: `9d90641965ef6d9351d76785d5729cc932ed7ea3cae11ff931dcef3279148452`
- `tests/contracts/test_wyscout_data_contracts.py`: `568859f5879766c0470169e480177c3089b26788456c3133294e86ba2b0dc69a`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R1.md`: `abc9418fa0e61187097a6ff7ed11345f7e265703116aff1ad2a5ce30e200176a`
- All seven authority/preimage digests also reproduce exactly as recorded in the packet and independent review.

## Risks and follow-up

Downstream raw, Bronze, Silver, Gold, or product execution must not rely on the reviewed models until a bounded correction closes the ten findings, updates focused negative tests and producer evidence, passes the complete verification set, and receives a fresh independent review. The recommended next packet is a bounded data-contract implementation R2 packet; it should not expand provider, architecture, or product scope.

## Scope confirmation

- No Git operation was performed.
- No delegation or subagent was used.
- No dependency or environment state was changed.
- No provider acquisition, network write, cloud resource, hosted CI, public endpoint, or deployment was performed.
- The reviewer did not modify or approve implementation work.

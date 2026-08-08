# Subagent return: W04-DATA-CONTRACTS-REVIEW-01-R2

## Task

- Task ID: `W04-DATA-CONTRACTS-REVIEW-01`
- Revision: `R2`
- Role: fresh independent reviewer
- Result: **REWORK**
- Finding counts: P0 `0`, P1 `7`, P2 `0`

## Files changed

- `reports/reviews/W04/wyscout-data-contracts-independent-review-R2.md`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-REVIEW-01-R2.md`

No implementation, test, authority, configuration, orchestration, or prior
evidence file was changed.

## Summary

All packet-listed inputs and all 4,007 implementation/test lines were reviewed,
all fixed digests reproduced, the exact packet suite passed, and the 95-case R1
constructor closure selection passed. Fresh probes still found seven open P1
contract defects: forgeable emitted subevent outcomes; possession eligibility
not derived from possession v2; ambiguous physical source-row/partition
lineage; identity dependency substitution; unreconciled Gold coverage;
arbitrary applicability reasons; and zero-row, zero-byte Parquet entries.

These are bounded implementation/test defects. They do not demonstrate a
contradiction in R20/R21 and do not justify another architecture revision.

## Verification performed

- `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — PASS; 2 files already formatted
- `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — PASS
- `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — PASS; no issues in 2 files
- `uv run lint-imports` — PASS; 30 files, 46 dependencies, 3 contracts kept, 0 broken
- `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` — PASS; 370 passed in 77.84s
- `uv run bandit -q -r src/scouting/contracts/wyscout_data.py` — PASS
- `uv run python scripts/verify_local_only.py` — PASS; 25/25 and zero Git remotes
- R1 direct-constructor closure selection — PASS; 95 passed, 45 deselected in 0.23s
- Fresh validated-constructor probes — reproduced all seven open finding families

## Artifacts and fixed-input identity

- Independent review: `reports/reviews/W04/wyscout-data-contracts-independent-review-R2.md`
- Independent review SHA-256: `38f2bb9fd6971bf1e9a38aed44dd2acd59b3187124204b69152ad43c80bfcd8a`
- Corrected implementation: `87dc13ada636e018ff9dfc17b548942a1d93132db8a615248cc8be3b23ebe99d`
- Corrected focused tests: `1b5aafbd127cda6703dce8de358b10c6f4c467de0821601b6b358564a5dabd47`
- R2 producer return: `b855798a3be49093e0ceff78122bde3b2dcd893d99a1cafef43275f6138ad34c`
- R1 independent review: `862fa5513cd261fd95bcd921fb52631c90af56ff930ce968682059879761dee2`
- Identity acceptance: `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86`
- Source manifest: `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
- Field acceptance: `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436`
- Possession acceptance: `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1`
- Supported-feature acceptance: `d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c`
- Product-contract preimage: `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
- Schema-bundle preimage: `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`

## Risks and follow-up

Return the data-contract producer for bounded rework covering the seven P1
findings, regenerate producer evidence, rerun the complete packet suite, and
obtain a new independent review. Raw, Bronze, Silver, Gold, and product
implementation must not rely on this revision before acceptance.

## Scope confirmation

- The accepted feature roster remains exactly the four R21 count features.
- No Git operation, delegation, implementation change, or self-approval was performed.
- No dependency/environment mutation, provider access, network write, cloud
  resource, container, hosted CI, public endpoint, or deployment was performed.

# Subagent return

## Task

- task_id: `W04-BUILD-PRODUCT-AUTHORITY-DECISION-01-R1`
- objective: Freeze the exact user-authorized R4 W04 build/product decision surface and closed executable tests without creating any aggregate, product, manifest, receipt, build, or data byte.

## Files changed

- `reports/reviews/W04/authorities/wyscout-build-product-authority-decisions-v1.json`
- `tests/contracts/test_w04_wyscout_build_product_authority.py`
- `reports/reviews/W04/returns/W04-BUILD-PRODUCT-AUTHORITY-DECISION-01-R1.md`

## Summary

- Created one strict R20-canonical JSON-plus-one-LF authority decision with the exact master actor, truthful UTC decision clock, ID, schema version, and state `AUTHORITY_ONLY_NO_PRODUCT_BYTES`.
- Bound all 17 packet-fixed inputs by exact repository-relative path and physical SHA-256. All fixed digests were reproduced before editing.
- Froze the exact half-open one-match window, selected-match snapshot, strict cutoff, five-key 250-byte window identity preimage, SHA-256 and UUIDv5 derivation; the accepted source-completion index and exact `1H=901` / `2H=867` populations; the 23-root acyclic v2 aggregate materialization rules without an aggregate instance or future digest; the unchanged 25-key single-hash build projection/inverse; the exact nine-key and 15-key receipt contracts; and the sole two-key whole-`LayerManifest` semantic derivation for Bronze, Silver and Gold.
- Froze exact parent-summary reconciliation, manifest-derived one-Gold-product/one-boundary population and guarded readback, accepted-index lineage binding, all required substitution failures, and the exact four-feature conservative POC scope with strict integer-only event/subevent mapping and string preservation without coercion.
- Encoded explicit prohibitions on second semantic derivation, schema/root/population/feature expansion, placeholder/null/anticipated v2 digests, provider/network access, product/control/data/build/manifest/receipt writes, publication, cloud, containers, hosted CI, endpoints, remotes and deployment.
- Added closed tests for canonical bytes, full fixed-input readback, exact rosters and cardinalities, window digest/UUID reproduction, accepted index/period equality, acyclicity, absent future digests, four-feature scope, lifecycle separation, malformed review/acceptance failure, direct authority mutations, and absence of downstream product paths.

## Tests run

- command: fixed-binding `shasum -a 256` over all 17 input paths
  - exit status: `0`
  - result: every packet-fixed digest matched exactly before the first edit.
- command: `uv run ruff format tests/contracts/test_w04_wyscout_build_product_authority.py`
  - exit status: `0`
  - result: one new test file formatted.
- command: initial combined focused Ruff, mypy and pytest run
  - exit status: `1`
  - result: Ruff and mypy passed; pytest had only three test-expectation regex mismatches (`differs` versus messages containing `differ`). No authority behavior failed. The bounded assertion was corrected.
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_build_product_authority.py`
  - exit status: `0`
  - result: `21 passed` after the bounded correction.
- command: `uv run ruff format tests/contracts/test_w04_wyscout_build_product_authority.py && uv run ruff check tests/contracts/test_w04_wyscout_build_product_authority.py && uv run mypy tests/contracts/test_w04_wyscout_build_product_authority.py && uv run pytest -q tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: format unchanged; Ruff passed; mypy passed with no issues; `128 passed`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, all `25/25` local-only checks passed, zero configured remotes, active branch `main`, pre-push guard active.
- command: final `jq` cardinality/state predicates and `shasum -a 256` over the two implementation artifacts
  - exit status: `0`
  - result: exact `17/23/25/9/15/2/4` rosters and no-product state reproduced; artifact hashes below matched.

## Artifacts/evidence

- canonical decision physical SHA-256: `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`
- canonical decision canonical SHA-256: `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`
- canonical decision size: `16,947` bytes, including exactly one terminal LF
- closed contract test physical SHA-256: `94cafedb2c4d0e50aecebb8a52ffc6666f2f37607d14d7155f25a0d5aea18ed8`
- accepted completion-index physical/content-address SHA-256 remained `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
- R20 and R21 remained `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` and `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`.

## Risks

- The decision is intentionally authority-only and is not self-approved. Product/build implementation remains blocked until fresh independent review and master acceptance pass.
- No season UUID derivation or lineup population decision was introduced; any later evidence that accepted upstream authority is insufficient for required downstream fields must be returned to the master rather than inferred here.

## Follow-up items

- Dispatch the fixed decision and test bytes to a fresh independent authority reviewer, then perform master readback/acceptance only if that review returns `PASS` with no unresolved P0/P1/P2 findings.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml`, `uv.lock`, `.venv`, migrations and shared contracts were untouched.
- no edits outside `allowed_paths`: confirmed; exactly the three packet-owned paths above were created/changed.
- no provider/network, cloud, container, hosted-CI, endpoint, remote or deployment action: confirmed.

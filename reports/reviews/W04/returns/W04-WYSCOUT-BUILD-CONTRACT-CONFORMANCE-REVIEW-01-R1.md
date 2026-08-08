# Subagent return

## Task

- task_id: `W04-WYSCOUT-BUILD-CONTRACT-CONFORMANCE-REVIEW-01-R1`
- objective: Independently determine whether the frozen R3 receipt composition binds
  the exact authorized Gold schema identity and identify the smallest correction if
  it does not.

## Files changed

- `reports/reviews/W04/wyscout-build-contract-conformance-review-R1.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-BUILD-CONTRACT-CONFORMANCE-REVIEW-01-R1.md`

## Summary

- Recommendation: `REWORK`.
- Finding counts: `P0=0`, `P1=1`, `P2=0`.
- Finding `W04-BUILD-R3-P1-UNBOUND-GOLD-SCHEMA-IDENTITY`: receipt closure accepts
  multiple supported Arrow schema identities over the exact same authorized Gold
  row when product, manifest, boundary and receipt values are deterministically
  re-derived. Independently accepted variations were top-level nullability, field
  order and a nested integer width.
- R3 correctly closes both R1 findings: all three locally shaped invalid manifests
  are rejected by `LayerManifest`, and the former claim-only product/semantic/proof
  digest arguments no longer exist.
- The smallest correction must wait for and compose the already-planned accepted
  23-root canonical schema-bundle identity. The current R21 schema preimage is
  explicitly descriptor-only and cannot authorize Arrow order, types or nullability.
  No placeholder, caller digest or test-inferred schema is sufficient.
- This is a bounded serial sequencing correction and does not require a new schema
  root, product row, feature, population, dependency, architecture or external
  boundary.

## Tests run

- command: `shasum -a 256` over every packet-fixed binding
  - exit status: `0`
  - result: all expected hashes reproduced.
- command: `uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`.
- command: packet focused five-path `uv run pytest -q` matrix
  - exit status: `0`
  - result: `265 passed in 6.49s`.
- command: `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: `233 passed in 107.69s`.
- command: independent `uv run python -B -c` schema-substitution and R1-closure probe
  - exit status: `0`
  - result: nullability, field-order and nested-width schema substitutions were all
    accepted after consistent derivation; all three invalid manifest shapes were
    rejected; claim-only digest parameters were absent.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks and zero Git remotes.
- command: one read-only document inspection command had an accidental trailing bare
  `python` token
  - exit status: `127`
  - result: shell reported `command not found`; no interpreter started and no bytes
    changed. Every executed Python probe used `uv run`.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-build-contract-conformance-review-R1.md`
- finding: `W04-BUILD-R3-P1-UNBOUND-GOLD-SCHEMA-IDENTITY`
- independently accepted nullability semantic SHA-256:
  `bf50c562e0da76274cd39b0bf8b887d2b1b6f02702245d3412903bb7e54923d9`

## Risks

- Until the planned exact canonical schema authority is materialized and composed,
  a receipt can claim `COMPLETE` for a caller-selected supported Arrow schema that
  is not the one accepted v2 Gold schema identity.
- No other P0, P1 or P2 finding was identified in this bounded review.

## Follow-up items

- Materialize and independently accept the already-planned 23-root canonical schema
  bundle, then issue one bounded receipt-composition correction requiring the exact
  accepted Gold schema descriptor and repeat this substitution matrix.

## Scope confirmation

- no Git operations: confirmed; none performed
- no unauthorised dependency or lockfile changes: confirmed; none performed
- no edits outside `allowed_paths`: confirmed; only the two review outputs changed
- no implementation, test, authority, orchestration, config, product, data, run or
  verification edits: confirmed
- no provider/network, cloud, container, hosted CI, endpoint, deployment or public
  action: confirmed
- no delegation or self-approval: confirmed

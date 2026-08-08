# Subagent return

## Task

- task_id: `W04-WYSCOUT-BUILD-CONTRACT-01-R1`
- objective: Implement the strict standalone W04 build-contract module for the exact accepted
  five-key window, bounded season helper, five accepted authority rows, unchanged 25-key
  one-hash projection/inverse, closed receipts, and exactly the eight R4 result roles.

## Files changed

- `src/scouting/contracts/wyscout_build.py`
- `tests/contracts/test_w04_wyscout_build_contract.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-BUILD-CONTRACT-01-R1.md`

## Summary

- Implemented a standalone, strict, frozen Pydantic contract module using only the Python
  standard library and Pydantic. It imports no other `scouting` module and performs no
  filesystem, provider, network, process, product, manifest, aggregate, receipt, or run write.
- Reproduced the exact 250-byte five-key window preimage, its frozen SHA-256, the exact UUIDv5
  namespace/name chain, the half-open one-match window, strict cutoff, dependency-watermark,
  snapshot, and `valid_from` rules.
- Implemented the sole bounded season helper. It admits only `type(value) is int` and value
  `181150`, rejects Boolean/coerced/alternate values, and reproduces season UUID
  `4696aa1f-b512-5d18-af79-33cf031455cf` through the accepted two-stage UUIDv5 chain.
- Bound the exact five ordered accepted authority references and exact five ordered evidence
  dependencies. The season/lineup reference occurs only inside the existing
  `authority_rows` member; there is no sixth authority, season projection member, generic
  season identity kind, or identity-bundle expansion.
- Implemented the exact 25-key pre-build projection and 25-key post-hash invocation rosters.
  The build ID is exactly one SHA-256 of R20 canonical JSON without a terminal LF. The inverse
  removes only `build_id`, restores only `schema_version`, and checks byte-semantic equality of
  the other 24 values. The accepted v1 placeholder product/schema digests fail closed.
- Implemented the exact 15-key temporal-boundary receipt and nine-key rebuild-invocation
  receipt, with one-product boundary population, exact build/run/path/direct-path-digest,
  Gold-manifest summary, independently supplied lineage/product/proof, physical readback, and
  `started_at <= checked_at <= completed_at` checks.
- Implemented closed models for exactly the eight R4 result roles:
  `ENTRYPOINT_SOURCE_RESULT`, `COMPONENT_PROOF_RESULT`, `PRE_BUILD_ADMISSION_RESULT`,
  `REBUILD_RECEIPT_SUMMARY`, `LAYER_MANIFEST_SUMMARY`, `FINAL_RECHECK_RESULT`,
  `POST_BUILD_ID_REBUILD_RESULT`, and `CHILD_RESULT_ENVELOPE`, including their exact key
  rosters, cardinalities, role/payload/argv/path/digest relationships, v4 UUIDs, strict
  Boolean/integer separation, and fixed state values.
- Implemented exactly one layer-manifest semantic derivation: SHA-256 of the exact two-key
  wrapper containing the already closed-schema-validated complete parsed `LayerManifest` and
  `semantic_schema_version=w04-wyscout-layer-manifest-semantic-v1`, using R20 canonical JSON
  without a terminal LF. The companion equality check uses that same helper; it is not a
  second derivation. Tests reject entry digest, physical digest, other-layer digest, swapped
  digest, downstream-rehashed/substituted summary, terminal-LF, and field-omission/expansion
  alternatives.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `188 passed in 3.79s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; zero remotes, local `main`, Python `3.12.12`, one root uv project/lock/venv,
    and no hosted CI, deployment, containers, external services, public endpoints, or
    out-of-root configuration.

## Artifacts/evidence

- `src/scouting/contracts/wyscout_build.py`
  - producer-observed SHA-256:
    `70cd74bae74ce16431d88567372d8839c383a7bf3ad94838e9dd624c9d0eb03b`
- `tests/contracts/test_w04_wyscout_build_contract.py`
  - producer-observed SHA-256:
    `8f90074f3ca597e7d13dfdcf1829492dff627c80f06ee82a423fc7e797811630`
- Focused exhaustive contract test count: `27 passed`.
- Complete packet authority/composability test count: `188 passed`.

## Risks

- The sole semantic helper deliberately assumes its input is the complete exact parsed
  `LayerManifest` that has already passed the separately authorised closed v2 schema and
  guard-read validation. It does not create a second LayerManifest schema, aggregate, parser,
  materializer, or writer. A downstream implementation must preserve that required validation
  order before calling the pure derivation.
- This producer return is evidence only and is not independent review or self-acceptance.

## Follow-up items

- Master must independently inspect the three packet-owned files, rerun the acceptance checks,
  and dispatch a separate reviewer under non-overlapping review-only ownership.

## Scope confirmation

- no Git operations: confirmed; none performed
- no unauthorised dependency or lockfile changes: confirmed; none performed
- no edits outside `allowed_paths`: confirmed; only the three packet-owned paths above were
  created or changed

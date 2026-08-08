# Subagent return

## Task

- task_id: `W04-NESTED-PHYSICAL-PRIMARY-KEY-REVIEW-01-R1`
- objective: Freshly and independently verify the frozen nested
  physical-primary-key correction, exact role paths, fail-closed descriptor,
  Arrow and projected-key equality, and unchanged accepted aggregate bytes and
  digest meanings.
- reviewer state: `COMPLETE`
- verdict: `PASS`; `P0 0 / P1 0 / P2 0`

## Files changed

- `reports/reviews/W04/wyscout-nested-physical-primary-key-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-NESTED-PHYSICAL-PRIMARY-KEY-REVIEW-01-R1.md`

## Summary

- Verified all seven fixed bindings before and after review; all matched exactly.
- Re-derived all twelve exact descriptor-owned physical primary-key rosters from
  accepted logical keys and physical descriptors. Complete Bronze source-row
  identity, rejected-field `json_path`, Fact/Gold nested tenant paths and every
  accepted Fact/Gold key field are present in exact order.
- Confirmed import-time path validation and encoder-time descriptor/Arrow/path
  validation fail closed. Projected canonical key comparison requires exact
  runtime type and value and preserves arity, type homogeneity, uniqueness and
  canonical ordering.
- Independently rejected 26 malformed, missing, nullable, collection,
  non-scalar, Boolean/null, alias, duplicate, reordered, timestamp and projected
  type/value drift cases; accepted two valid nested/timestamp vectors.
- Public product encoding and Parquet readback passed for strict Fact and Gold
  rows using the exported nested role paths.
- Verified all three Gold timestamp key fields remain physical
  `timestamp[us, tz=UTC]` and inverse-project to exact canonical UTC string keys.
- Regenerated both accepted aggregates in memory and required byte-for-byte
  equality. Logical digests, physical sizes and physical hashes are unchanged.
- Found no P0, P1 or P2 defect.

## Tests run

All UV commands used `PYTHONDONTWRITEBYTECODE=1`, isolated
`UV_CACHE_DIR=/tmp/w04-nested-pk-review.TyzpyT`, `UV_LOCKED=1`,
`UV_NO_SYNC=1`, and `uv run --locked --no-sync`.

- command: `ruff format --check src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `4 files already formatted`
- command: `ruff check src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `mypy src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `Success: no issues found in 4 source files`
- command: `pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_v2_aggregates.py`
  - exit status: `0`
  - result: `360 passed in 57.45s`
- command: `bandit -q -r src/scouting/contracts/wyscout_schema.py src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings
- command: `lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`; 39 files and 74 dependencies analyzed
- command: `python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25 checks and zero failures
- command: `python scripts/materialize_wyscout_v5_contracts.py --check`
  - exit status: `0`
  - result: `PASS`; schema logical digest
    `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be`,
    product logical digest
    `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0`
- command: independent public Fact/Gold encode/readback, exact roster, timestamp
  and aggregate-byte probe
  - exit status: `0`
  - result: both roles encoded and reopened as one row; exact timestamps and both
    aggregate byte comparisons passed
- command: independent synthetic path/key adversarial probe
  - exit status: `0`
  - result: two valid encodes accepted; 26 malformed/drift/bypass cases rejected

## Artifacts/evidence

- Independent review:
  `reports/reviews/W04/wyscout-nested-physical-primary-key-independent-review-R1.md`
- Fixed producer-owned hashes rechecked after all gates:
  - schema runtime:
    `b76ff6d55f841594a337929c382137d27d841b37e49f0f40c1961b9af743bb54`
  - storage formats:
    `d5e6690f4b2467baeb364e2f8339b2b091f18bc01f8e18a96e8d770da66af9b6`
  - schema tests:
    `e6d14e9fb8787990716796b1e9031013a7386fae4d7637ccc77b28d746bb9817`
  - formats tests:
    `8fe2d3b587541ee4fd80c6e5604e788b48ef78ba4bdc608a9245b64b30afd345`
  - producer return:
    `287faf0eec55582e16d5e3354304e82f62e1ec3d337c41a6b0af2eefc23a7c91`
- Aggregate evidence:
  - schema: 12295 bytes, physical SHA-256
    `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45`,
    logical digest
    `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be`
  - product: 6386 bytes, physical SHA-256
    `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af`,
    logical digest
    `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0`

## Risks

- No known implementation defect or residual review blocker remains.
- Generic simple top-level key compatibility remains intentionally available in
  the encoder; the public W04 product serializer consumes the exported exact role
  roster, so accepted products are bound to the frozen physical paths.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed; none performed.
- no unauthorised dependency or lockfile changes: confirmed; all executions used
  the existing root environment with locked/no-sync and an isolated `/tmp` cache.
- no edits outside `allowed_paths`: confirmed; only the two reviewer artifacts
  listed above were written.

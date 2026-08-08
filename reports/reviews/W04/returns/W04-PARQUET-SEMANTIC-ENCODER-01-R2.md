# Subagent return

## Task

- task_id: `W04-PARQUET-SEMANTIC-ENCODER-01`
- objective: Correct only the R1 false semantic binding by proving exact typed
  correspondence between every explicit Arrow row and its canonical checked
  contract row, including strict Arrow-derived primary-key identity.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R2.md`

## Summary

- Verified all four R1 fixed candidate/review hashes before editing. The valid
  physical vector
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
  and semantic vector
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`
  remain unchanged.
- Added a closed recursive Arrow-to-contract projection. Before semantic hashing
  or Parquet encoding, every Arrow row is projected to one complete canonical JSON
  object and its canonical bytes must equal the supplied checked contract row
  byte-for-byte.
- The projection supports only null values and exact Arrow Boolean, signed/unsigned
  integers, finite floats, UTF-8 strings, decimals, `timestamp[us, tz=UTC]`, list,
  large-list, fixed-size-list, and struct values recursively. Decimal values render
  as their exact fixed-point strings. UTC timestamps render with `Z`, six digits
  when microseconds are nonzero, and no fractional part when zero.
- Binary, naive/non-UTC or non-microsecond timestamps, date/time/duration,
  dictionary, map, union, extension, non-finite float, and every other Arrow type
  fail closed. Nested struct/list field metadata, duplicate names, unsupported
  children, and forbidden nested nulls also fail closed.
- Contract object keys must equal the complete Arrow schema name set. Every primary-
  key field must be present in the Arrow schema. Each supplied key is compared to
  the value derived from the projected Arrow row using exact Python type identity
  and value equality, closing both `True == 1` and string/integer confusion.
- Added adversarial regressions for unchanged-contract non-key Arrow divergence,
  Arrow/caller-key divergence, string/integer and Boolean/integer keys, missing
  Arrow key fields, missing/extra contract fields, naive/non-UTC timestamps,
  decimal/list/large-list/fixed-list/struct projection, unsupported binary, and
  non-finite float.
- Preserved the complete R20 physical writer call, semantic framing, immutable
  result metadata, generic APIs, and legacy serializer behavior.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R1.md reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R1.md`
  - exit status: `0`
  - result: all packet-fixed pre-edit hashes matched exactly.
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: two files already formatted.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: no issues in two source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `61 passed in 2.12s`.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py::test_fixed_physical_and_semantic_vectors_are_repeatable tests/unit/test_w04_wyscout_product_formats.py::test_unchanged_contract_rejects_non_key_arrow_divergence tests/unit/test_w04_wyscout_product_formats.py::test_arrow_derived_key_rejects_caller_key_divergence tests/unit/test_w04_wyscout_product_formats.py::test_string_contract_keys_cannot_claim_integer_arrow_keys tests/unit/test_w04_wyscout_product_formats.py::test_boolean_arrow_keys_cannot_equal_integer_caller_keys`
  - exit status: `0`
  - result: `5 passed in 0.12s`; both valid vectors reproduced and all mandatory R1
    bypasses failed closed.
- command: `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 34 files and 60 dependencies analyzed; all three contracts kept.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 local-only checks passed with zero configured remotes.

## Artifacts/evidence

- `tests/unit/test_w04_wyscout_product_formats.py`
- R2 format implementation SHA-256:
  `cfa25e672072cba702d103a2a68c79f2895852ee91e966b998cc3a2e13beb5ea`
- R2 focused test SHA-256:
  `113af1f3b23aac813e0b8484b02348f53d96af0eb816cb495ae90325d5dd158f`
- preserved physical vector:
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- preserved semantic vector:
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`

## Risks

- No open producer-identified P0-P2 issue remains in this bounded correction.
  Independent review and master reproduction remain mandatory before any
  publication use.
- Product-family owners still supply the explicit typed Arrow table and checked
  canonical contract bytes. The encoder now proves their exact typed row/key
  correspondence but intentionally owns no product mapping or publication action.

## Follow-up items

- Master independently reproduces R2 and dispatches fresh independent byte/security
  review against the new fixed implementation and test hashes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- no product/control write, provider/network action, cloud, container, hosted CI,
  endpoint, remote, or deployment: confirmed

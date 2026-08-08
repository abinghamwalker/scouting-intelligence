# Subagent return

## Task

- task_id: `W04-EXACT-DECIMAL128-WITH-EXPONENT-01`
- objective: Implement the authorized exact reversible `decimal128(22,18)` physical projection with exponent and signed-zero preservation, strict inverse validation, and adversarial zero-hash/zero-write evidence.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-EXACT-DECIMAL128-WITH-EXPONENT-01-R1.md`

## Summary

- Added exactly one logical projection enum member, `EXACT_DECIMAL128_WITH_EXPONENT`, admitted only on an ordered metadata-free struct with non-null identity children `value: decimal128(22,18)`, `exponent: int8`, and `negative_zero: bool`; aliases, alternate order/name/type/nullability, decimal state, and logical-position state fail closed.
- Added public `exact_decimal128_with_exponent_to_w04_arrow`, accepting only a finite built-in `Decimal` and optional exact declared scale. It applies the accepted lexical capacity calculation, verifies declared scale equality, traps inexact scale-18 conversion, preserves the tuple exponent, and marks only signed numeric zero.
- Added the strict inverse before generic struct decoding. It validates exact physical type and runtime children, rejects nulls and nonzero negative-zero claims, traps inexact exponent reconstruction, restores signed zero, reruns capacity/source-scale validation, and emits `str(restored)` as the exact logical Decimal JSON string token before semantic hashing or writing.
- Kept `CANONICAL_DECIMAL_UTF8` and its coverage helper unchanged. Semantic digest framing/formula and generic serializer behavior remain unchanged. Replaced two pre-existing optimized-away `assert` statements in schema generation with explicit impossible-state `AssertionError` branches so the packet Bandit command passes without weakening validation.
- Added scale 0/18, positive exponent, trailing-zero, positive/negative signed-zero, upper/lower capacity edge, declared-scale, malformed logical/runtime value/exponent/sign/null, nonzero-negative-zero, rounding, descriptor drift, schema child/order/type/nullability/metadata drift, and instrumented zero-hash/zero-write coverage.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/verification/W04/wyscout-exact-decimal128-with-exponent-authorization-R1.md reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R5.md` before editing
  - exit status: `0`
  - result: fixed bindings matched exactly: formats `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c`, tests `8e68548967293b28e694359509667106951bdc5ba8e1636a541f81f7c3773e1a`, authorization `57ef5ce132f732457df6dac4bfd99c554ba5497a9759bd322d0093a5af8b3131`, blocked R5 return `7b85730b07f5cc1bbc26b988538fcca007ce32c99ec4342aac17db7b7fbb856b`.
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `293 passed in 2.52s`.
- command: `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 controls, zero configured remotes.
- command: first sandboxed combined acceptance attempt
  - exit status: `2`
  - result: uv cache access was denied at `/Users/adrian/.cache/uv/sdists-v9/.git`; the same checks were rerun with approved access to the existing local uv cache and passed.
- command: first escalated combined test/security/import/local-only attempt before explicit impossible-state correction
  - exit status: `1`
  - result: tests passed `293`; Bandit reported two pre-existing low-severity `assert_used` findings and stopped the chain. Both were converted to explicit impossible-state branches, after which the exact final acceptance sequence passed end to end.

## Artifacts/evidence

- `src/scouting/storage/formats.py`: SHA-256 `8fc57c2ceb8ac714cb2573802d7bc745afb05e67e2c14d302b6b06cd911086d6`
- `tests/unit/test_w04_wyscout_product_formats.py`: SHA-256 `f529ca1c87795e67ed17b62285e1df50fe5d85757e85de45a14a704d39a56660`
- authorization: SHA-256 `57ef5ce132f732457df6dac4bfd99c554ba5497a9759bd322d0093a5af8b3131`
- fixed blocked R5 return: SHA-256 `7b85730b07f5cc1bbc26b988538fcca007ce32c99ec4342aac17db7b7fbb856b`
- focused exact-decimal and regression evidence: `293 passed`; invalid inverse, descriptor, and physical-schema matrices assert semantic hash calls `0` and Parquet write calls `0`.

## Risks

- No logical W04 field is mapped to the new kind in this packet, by design; downstream R5 descriptor adoption remains required after independent review and master acceptance.
- No residual implementation, schema, leakage, security, or dependency risk identified within the packet scope.

## Follow-up items

- Resume the preserved R5 schema descriptor adoption only after fresh independent review and master acceptance of this exact candidate.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; edits are limited to the three paths listed above.

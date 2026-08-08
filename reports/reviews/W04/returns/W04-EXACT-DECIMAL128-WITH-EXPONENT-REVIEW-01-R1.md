# Subagent return

## Task

- task_id: `W04-EXACT-DECIMAL128-WITH-EXPONENT-REVIEW-01`
- objective: Independently review the exact Decimal projection candidate for
  lossless forward projection, strict inverse exponent/signed-zero reconstruction,
  exact physical schema closure, byte equality, zero-call failures, and preserved
  coverage/generic serializer behavior.

## Files changed

- `reports/reviews/W04/wyscout-exact-decimal128-with-exponent-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-EXACT-DECIMAL128-WITH-EXPONENT-REVIEW-01-R1.md`

## Summary

- Verdict: `REWORK`.
- Findings: `P0 0 / P1 1 / P2 0`.
- All four fixed hashes matched before review and immediately before rendering.
- P1 `W04_EXACT_DECIMAL_SIGN_BOOLEAN_NOT_AUTHORITATIVE`: inverse reconstruction
  toggles with `copy_negate()` rather than setting the zero sign from the Boolean.
  Numeric negative zero reconstructed as positive when the flag was true and
  remained negative when the flag was false.
- Existing tests miss the defect because present PyArrow construction normalizes
  the numeric decimal child to positive zero. All other bounded schema, capacity,
  byte-equality, zero-call, coverage, digest, generic-storage, static, security,
  import, and local-only evidence passed.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-EXACT-DECIMAL128-WITH-EXPONENT-01-R1.md reports/verification/W04/wyscout-exact-decimal128-with-exponent-authorization-R1.md`
  - exit status: `0`
  - result: all packet-fixed hashes matched before analysis and immediately before
    review rendering.
- command: `uv run python -c '<independent four-way signed-zero inverse probe>'`
  - exit status: `1` by design
  - result: positive-zero/true and positive-zero/false passed; negative-zero/true
    produced `0` instead of `-0`, and negative-zero/false produced `-0` instead of
    `0`.
- command: `uv run python -c '<independent exact Decimal success/schema/JSON-byte matrix>'`
  - exit status: `0`
  - result: 11/11 current-normalization vectors covered exponent `-18`, `0`, and
    positive values, trailing zeros, both signed zeros, minimum magnitudes, and
    signed capacity edges with exact child values and logical bytes.
- command: `uv run python -c '<independent inverse, schema, descriptor, forward and zero-call attack matrix>'`
  - exit status: `0`
  - result: 8 inverse/alias, 2 wrong-runtime-schema, 4 alternate-descriptor, and 9
    forward type/finite/scale/capacity attacks rejected; semantic hash calls `0`,
    Parquet writes `0`.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `293 passed in 2.48s`.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: no issues in 2 source files.
- command: `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: initial sandbox `2`, identical approved rerun `0`
  - result: no findings; first attempt was only an existing uv-cache read denial.
- command: `uv run lint-imports`
  - exit status: initial sandbox `2`, identical approved rerun `0`
  - result: `3 kept, 0 broken`; first attempt was only an existing uv-cache read
    denial.
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: 2 files already formatted.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 controls and zero configured remotes.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-exact-decimal128-with-exponent-independent-review-R1.md`
- fixed candidate formats SHA-256:
  `8fc57c2ceb8ac714cb2573802d7bc745afb05e67e2c14d302b6b06cd911086d6`
- fixed candidate tests SHA-256:
  `f529ca1c87795e67ed17b62285e1df50fe5d85757e85de45a14a704d39a56660`
- fixed producer return SHA-256:
  `369f3cdeed2a4424cf36146608e5fdfbcfeb15be52f13281f0e36f47d8b629eb`
- fixed authorization SHA-256:
  `57ef5ce132f732457df6dac4bfd99c554ba5497a9759bd322d0093a5af8b3131`

## Risks

- P1: the inverse does not make `negative_zero` authoritative if an exact physical
  decimal child arrives as negative zero, violating the explicit strict-inverse
  requirement.
- No other open P0-P2 issue was identified within this bounded review.

## Follow-up items

- Replace toggle behavior with explicit zero-sign setting and add the four-way
  numeric-zero-sign/Boolean direct inverse matrix; then freeze new hashes and obtain
  fresh independent review before R5 schema adoption resumes.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither
  `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; only the two report paths listed
  above were written.
- no implementation/test edits, delegation, or self-approval: confirmed.

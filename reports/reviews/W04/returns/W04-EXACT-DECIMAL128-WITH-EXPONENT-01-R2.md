# Subagent return

## Task

- task_id: `W04-EXACT-DECIMAL128-WITH-EXPONENT-01`
- objective: Correct R1 signed-zero reconstruction so `negative_zero` sets, rather than toggles, the logical zero sign and prove all four incoming-sign/Boolean combinations.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-EXACT-DECIMAL128-WITH-EXPONENT-01-R2.md`

## Summary

- After exact no-rounding exponent reconstruction, zero is now normalized with `copy_abs()` before a negative sign is applied if and only if `negative_zero` is true. An incoming numeric child's zero sign can no longer leak through or toggle the authoritative Boolean.
- The existing nonzero `negative_zero=true` rejection and every other R1 descriptor, capacity, inverse, coverage, digest, serializer, and boundary behavior remain unchanged.
- Added an exact-typed fake Arrow struct-scalar matrix that bypasses current PyArrow zero-sign normalization and crosses positive/negative numeric zero with false/true `negative_zero`; outputs are respectively `0`, `-0`, `0`, `-0`.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-EXACT-DECIMAL128-WITH-EXPONENT-01-R1.md reports/reviews/W04/wyscout-exact-decimal128-with-exponent-independent-review-R1.md reports/reviews/W04/returns/W04-EXACT-DECIMAL128-WITH-EXPONENT-REVIEW-01-R1.md`
  - exit status: `0`
  - result: all five R2 fixed bindings matched exactly before editing.
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: no issues in 2 source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `297 passed in 2.50s`; the full R1 suite remains green and the four new sign combinations pass.
- command: `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 controls and zero configured remotes.

## Artifacts/evidence

- `src/scouting/storage/formats.py`: SHA-256 `2dfdf3675a47f6c2b53478857de1af27aebecb85def8f0701e6ef86c65fafcc9`
- `tests/unit/test_w04_wyscout_product_formats.py`: SHA-256 `ba38c5a66f41aee8ef2b998f4622c71ec30f3b8861d7ef07d8540d001b0bee89`
- fixed R1 independent review: SHA-256 `137401e9a602d97c59a114c7419f3eb67748cd0ebc04fcbca8259ecc3af36532`
- fixed R1 reviewer return: SHA-256 `126949bd85d65ca3e6c63fdb461addec10cd0b96a694c97553fc4e1f1bc8ea3c`

## Risks

- No residual implementation, schema, security, scope, or dependency risk identified within this exact P1 correction.
- Schema adoption remains outside this packet and still requires fresh independent review and master acceptance.

## Follow-up items

- Obtain fresh independent review of the R2 candidate before resuming R5 schema adoption.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; edits are limited to the three paths listed above.

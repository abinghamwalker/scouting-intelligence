# Subagent return

## Task

- task_id: `W04-SEASON-LINEUP-PRODUCT-BINDING-DECISION-01-R1`
- objective: Freeze one additive decision-only authority for the exact authorized season UUID and sole right-censored lineup stint, with closed executable tests and no product/runtime bytes.

## Files changed

- `reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-decisions-v1.json`
- `tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
- `reports/reviews/W04/returns/W04-SEASON-LINEUP-PRODUCT-BINDING-DECISION-01-R1.md`

## Summary

- Froze one R20-canonical JSON-plus-one-LF authority with closed top-level and nested rosters, strict scalar types, NFC strings, truthful UTC decision clock, master actor `4efe5691-8903-5148-8275-30d2e7e8aed0`, and explicit `AUTHORITY_ONLY_NO_PRODUCT_BYTES` lifecycle.
- Bound the authorization, accepted build/product decision-review-acceptance-master chain, R20, R21, source manifest, completion index, and product contract runtime by exact relative path and physical SHA-256.
- Froze strict integer `seasonId=181150` from the exact match member/ordinal/raw record and the two-step UUIDv5 derivation to season UUID `4696aa1f-b512-5d18-af79-33cf031455cf`; no season identity-bundle kind/row or second derivation was added.
- Froze exactly one ordered lineup stint for match `2499719`, team `1631`, player `285508`, ordinal `0`, start `[82,83)`, absent end/minutes, right-censored, per-90 suppressed, with independently reproduced UUID `591cdf5b-2281-53c4-8225-150313ca2c01`.
- Restricted future consumption to the existing `authority_rows` member of the unchanged 25-key build projection and explicitly prohibited a 26th key, altered build hash, schema/feature/Gold/population expansion, product bytes, and non-local work.
- Added closed tests for canonical bytes, exact keys/types/values, UUID reproduction, raw source evidence, exact one-row population, adversarial mutations, fixed-byte preservation, lifecycle review/acceptance closure, and downstream-byte absence.

## Tests run

- command: `uv run ruff format --check tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `uv run ruff check tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `157 passed in 3.65s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, zero configured remotes, main branch, local push guard active, Python `3.12.12`, one root uv project, no hosted CI/deployment, no containers, no external service dependency.

## Artifacts/evidence

- `reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-decisions-v1.json` — SHA-256 `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e`
- `tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py` — SHA-256 `0b5b933575f22451b5474323188619acec659c7291262c2e457086319fe93e29`
- Exact source member evidence: `archive-members/matches_England.json`, SHA-256 `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29`, 380 rows, ordinal `379`, canonical raw-record SHA-256 `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`.
- Independent source evidence confirms player `285508` occurs once on team `1631`'s bench and once as `playerIn` at strict integer nominal minute `82`.

## Risks

- The authority remains intentionally decision-only. Product implementation remains prohibited until fresh independent review and master acceptance pass.
- No residual binding, schema, population, security, performance, or local-only uncertainty was found within this packet.

## Follow-up items

- Dispatch fresh independent review to an agent other than this producer, then master acceptance only if that review passes.

## Scope confirmation

- no Git operations: confirmed; none performed.
- no unauthorised dependency or lockfile changes: confirmed; none performed.
- no edits outside `allowed_paths`: confirmed; only the three packet-owned paths above were changed.

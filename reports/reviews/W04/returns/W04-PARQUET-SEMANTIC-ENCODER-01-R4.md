# Subagent return

## Task

- task_id: `W04-PARQUET-SEMANTIC-ENCODER-01`
- objective: Correct only R3's metadata-presence gap by requiring Arrow metadata
  to be absent (`None`) at every recursively validated schema and field boundary.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R4.md`

## Summary

- Verified all five packet-fixed R3 implementation, producer-return, independent-
  review and reviewer-return hashes before editing. Every observed SHA-256 matched
  the R4 packet exactly.
- Replaced only the four metadata truthiness checks in the shared closed W04 schema
  validator. Top-level schema, top-level field, struct-child field and list-family
  value-field metadata must now be exactly `None`; explicit empty `{}` and every
  non-empty mapping fail before semantic hashing or Parquet encoding.
- Recursive list validation remains shared by list, large-list and fixed-size-list
  types and recursively re-enters itself, so the presence rule applies at every
  nested depth without changing accepted type, name or nullability behavior.
- Added `None` versus `{}` differential coverage for all four boundaries. List
  coverage includes direct list, large-list, fixed-size-list and nested list value
  fields. Every altered schema is rejected through both the encoder and the public
  exact-schema semantic helper; non-empty variants are exercised through the same
  paths to preserve R2 closure.
- The top-level schema differential proves that PyArrow's absent and explicitly
  empty metadata schemas have distinct serialized bytes. It replaces the Parquet
  writer with a call counter and proves the empty and non-empty metadata variants
  fail before any writer call, while the semantic helper emits no digest.
- Preserved all public APIs, exact schema/descriptor validation, row/key
  congruence, recursive value projection, generic serializers, semantic framing,
  writer and row-group controls. No semantic preimage byte changed.
- Preserved the exact fixed physical vector
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
  and semantic vector
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R3.md reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R3.md reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R3.md`
  - exit status: `0`
  - result: all five packet-fixed pre-edit hashes matched exactly.
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: both files already formatted.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: no issues in two source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `81 passed in 2.14s` with no warnings.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py::test_schema_metadata_presence_none_vs_empty_fails_before_digest_or_write tests/unit/test_w04_wyscout_product_formats.py::test_recursive_field_metadata_presence_fails_encoder_and_helper tests/unit/test_w04_wyscout_product_formats.py::test_fixed_physical_and_semantic_vectors_are_repeatable`
  - exit status: `0`
  - result: `14 passed in 0.14s`; all R4 differentials and both fixed vectors
    passed before the complete focused suite.
- command: `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 34 files and 60 dependencies analyzed; all three contracts kept.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 controls passed, including zero configured remotes and
    no cloud, container, hosted CI, endpoint or deployment surface.

## Artifacts/evidence

- `src/scouting/storage/formats.py`
  - R4 SHA-256:
    `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4`
- `tests/unit/test_w04_wyscout_product_formats.py`
  - R4 SHA-256:
    `c0afb390ef44f19d4759b62495bc0125a14fb80ac0f1e4376972a798702e3a9f`
- preserved physical vector:
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- preserved semantic vector:
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`

## Risks

- No producer-identified P0-P2 issue remains within this bounded R4 correction.
  Fresh independent byte/security review and master reproduction are still
  mandatory before acceptance or downstream product work.
- PyArrow preserves explicit empty metadata as an observable alternate schema
  representation even where some field serializations compare similarly. R4
  deliberately rejects presence at the object boundary rather than relying on
  truthiness, rendering or equality normalization.

## Follow-up items

- Master freezes the exact R4 implementation/test/return hashes, independently
  reproduces the focused checks, and dispatches fresh independent review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- no data, authority, product, provider, network, cloud, container, hosted CI,
  endpoint, remote or deployment action: confirmed

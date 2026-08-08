# Subagent return

## Task

- task_id: `W04-PARQUET-SEMANTIC-ENCODER-01`
- objective: Add the additive explicit-schema R20 Wyscout product Parquet encoder
  and semantic digest without changing the generic storage serializers or writing
  product/control artifacts.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R1.md`

## Summary

- Preserved `canonical_json_bytes`, `canonical_jsonl_bytes`, `parquet_bytes`, and
  `read_parquet_bytes`; the existing guarded-storage test remains unchanged and
  passes.
- Added immutable schema/result metadata and the additive
  `encode_w04_wyscout_product_parquet` entry point. It accepts only a non-empty
  explicit `pa.Table` and a separately supplied exactly equal metadata-free
  `pa.Schema`; it performs no inference, cast, or value coercion.
- Enforced canonical schema role/field descriptors, exact Arrow field order/type/
  nullability, microsecond timestamp types, non-nullable values, exact row/schema/
  key cardinality, canonical key-field binding to each contract row, homogeneous
  key types, uniqueness, and full primary-key order.
- Encoded with the exact R20 controls: Parquet 2.6, row groups of 65,536, zstd
  level 9, data page 2.0, no dictionary, no byte-stream split, statistics enabled,
  no page index, microsecond timestamp coercion without truncation, and stored
  Arrow schema.
- Added `w04_wyscout_parquet_semantic_sha256` with the exact
  `w04-wyscout-parquet-semantic-v1` domain and unsigned-64-bit framing of the
  canonical schema descriptor, exact ordered canonical contract-row bytes, and
  exact sorted-unique safe parent paths. Bronze's empty parent tuple is accepted.
- Canonical contract-row re-encoding, duplicate JSON keys, duplicate rows,
  non-UTF-8/non-NFC/noncanonical bytes, unsafe/non-NFC/reordered/duplicate parents,
  and uint64 framing overflow all fail closed.
- Tests prove the 65,535/65,536/65,537 row boundaries produce row-group sizes
  `(65535)`, `(65536)`, and `(65536,1)` respectively and cover controlled physical,
  schema, semantic-row, parent, ordering, duplication, type, nullability,
  timestamp, metadata, and framing mutations.

## Tests run

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
  - result: final rerun `50 passed in 1.64s`.
- command: `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 31 files and 49 dependencies analyzed; all three contracts kept.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 local-only checks passed.
- command: initial sandboxed `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: `2`
  - result: sandbox denied read of the existing uv cache `.git` path; no scan or
    repository/product write occurred. The identical required command was rerun
    through the approved read boundary and passed.
- command: initial sandboxed `uv run lint-imports`
  - exit status: `2`
  - result: the same uv-cache read denial; the identical required command was
    rerun through the approved read boundary and passed.

## Artifacts/evidence

- `tests/unit/test_w04_wyscout_product_formats.py`
- fixed physical SHA-256:
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- fixed semantic SHA-256:
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`
- serializer version: `w04-wyscout-parquet-v1`
- semantic version: `w04-wyscout-parquet-semantic-v1`

## Risks

- Product-family owners must construct the already typed explicit Arrow table and
  provide the exact checked canonical contract rows and primary-key field tuple;
  this bounded storage encoder intentionally contains no product-contract mapping
  or publication authority.
- Physical publication/readback and sidecar-free no-replace promotion remain the
  separately owned staged-publisher packet; this task wrote no product, manifest,
  receipt, staging, or other control byte.

## Follow-up items

- Master independently reproduces this packet, then dispatches the separately
  bounded staged immutable publisher and independent byte/security review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- no product/control write, provider/network action, cloud, container, hosted CI,
  endpoint, remote, or deployment: confirmed

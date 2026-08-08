# Subagent return

## Task

- task_id: `W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01`
- objective: Independently review the exact R2 encoder candidate for closure of
  R1's row/key bypasses, exact recursive schema authority, fixed vectors and the
  mandatory direct-descriptor boundary.

## Files changed

- `reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R2.md`
- `reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R2.md`

## Summary

- Verdict: `REWORK`.
- Findings: `P0 0 / P1 2 / P2 0`.
- All fixed R2 hashes and both preserved vectors matched before analysis and
  immediately before review rendering.
- R1's non-key Arrow divergence, Arrow-key divergence, string/integer,
  Boolean/integer and missing-key bypasses now fail closed.
- P1 `W04_ENCODER_NESTED_LIST_METADATA_UNBOUND`: child metadata on list,
  large-list and fixed-list value fields is accepted but omitted from the schema
  descriptor. The differential proof produced equal descriptors and semantic
  digests but different Parquet physical digests.
- P1 `W04_SEMANTIC_DESCRIPTOR_TYPE_AUTHORITY_UNVALIDATED`: the public semantic
  helper emitted W04-domain digests for directly constructed descriptors claiming
  unsupported, malformed and metadata-like Arrow type text.
- Exact physical controls, recursive values outside the findings, three row-group
  boundaries, timestamp denial, framing, generic serializer preservation and
  local-only controls passed.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R2.md`
  - exit status: `0`
  - result: all three packet-fixed hashes matched before analysis and immediately
    before rendering.
- command: read-only shell `.pyc` census and complete content/metadata inventory,
  before and after all Python commands
  - exit status: `0`
  - result: unchanged 1,162 files / 150 cache directories; content digest
    `6cabbe001e27ade45328d7620b0dad60469d4e2d33af4542f66893a0ab0c956d`;
    metadata digest
    `8604aa63a0b70862ff284e1b2c1cb03703f440c258eeb05171816e60b32c605f`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <direct descriptor probe>`
  - exit status: initial sandbox `2`, identical approved rerun `0`
  - result: unsupported `binary`, malformed, nested and metadata-like direct type
    claims all received semantic digests, proving P1.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <R1 bypass, fixed-vector and framing probe>`
  - exit status: `0`
  - result: all R1 bypasses rejected; physical and semantic vectors plus independent
    framing reproduced.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <recursive projection and negative probe>`
  - exit status: `0`
  - result: decimal/list/struct/null/UTC projection passed; nested forbidden null,
    binary, non-finite float, non-UTC timestamp and struct metadata rejected.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <nested list metadata differential probe>`
  - exit status: `0`
  - result: descriptor equality `true`, semantic equality `true`, physical equality
    `false`; the same acceptance also reproduced for large- and fixed-list child
    metadata.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <Parquet controls, row groups and timestamp probe>`
  - exit status: `0`
  - result: exact controls passed; `[65535]`, `[65536]`, `[65536,1]`; nanosecond
    timestamp rejected.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `61 passed in 2.14s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 controls and zero configured remotes.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R2.md`
- physical vector:
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- semantic vector:
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`
- nested-metadata differential physical vectors:
  `57e1a32d8f8986a16ff9f320d2b40a63fe2d5df8deb1ece4a05e886a2d65f987`
  and
  `170d32afe4179362574c4e28c73112cfbb368fa8ee92037137e5ee208dbaa06c`.

## Risks

- P1: accepted nested list metadata can change physical Parquet bytes while the
  semantic descriptor and digest remain unchanged.
- P1: callers can mint W04-domain semantic digests for descriptor type claims the
  encoder rejects or cannot produce.
- No other open P0-P2 issue was identified in this bounded review.

## Follow-up items

- Return only the two bounded P1 corrections and direct/nested descriptor
  adversarial tests to the producer. Preserve the valid vectors and APIs, then
  obtain fresh master verification and independent review of new fixed hashes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation, test, data, product, manifest, receipt, source, provider,
  network, cloud, container, hosted CI, endpoint, remote or deployment action:
  confirmed
- no delegation or self-approval: confirmed

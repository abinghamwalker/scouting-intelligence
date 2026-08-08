# Subagent return

## Task

- task_id: `W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-REVIEW-01-R1`
- objective: Freshly and independently review the final R2 descriptor-led
  serializer candidate, preserved semantic preimage, strict inverse and
  fail-closed build boundary.

## Files changed

- `reports/reviews/W04/wyscout-logical-arrow-projection-implementation-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-REVIEW-01-R1.md`

## Summary

- Verdict: `REWORK`; findings `P0/P1/P2 = 0/1/0`.
- All packet-fixed hashes matched before analysis and before report rendering.
- Read every line of the two implementation modules and two test modules.
- Found one P1 exact-typed-writer bypass. Pydantic union-member instances made
  invalid through `model_copy(update=...)` or `model_construct` are not
  internally revalidated by `TypeAdapter.validate_python(..., strict=True)`.
  Boolean-as-integer is silently dumped as integer `1`, and an independently
  composed descriptor-led call accepted that changed logical value and wrote one
  Parquet row.
- The strict physical inverse, descriptor/schema enforcement, sole semantic
  preimage, fixed golden vectors, build fail-closed state and local-only boundary
  otherwise reproduced successfully.
- No implementation repair or self-approval was performed.

## Tests run

- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: four files already formatted.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: no issues in four files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `135 passed in 3.00s`.
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `179 passed in 3.96s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS `25/25`; zero configured remotes.
- command: focused four-test Gold readback/schema-unavailable probe through
  `uv run pytest -q`
  - exit status: `0`
  - result: `4 passed in 0.15s`.
- command: independent tagged-value valid/malformed matrix through
  `uv run python -`
  - exit status: `0`
  - result: seven valid variants; 18 malformed inputs rejected; zero malformed
    Parquet writes.
- command: independent tuple/list/recursive-metadata/descriptor matrix through
  `uv run python -`
  - exit status: `0`
  - result: six tuple, five list, eight metadata and eight descriptor attacks
    rejected; zero Parquet writes.
- command: independent signature, Gold readback, semantic-preimage and golden
  reconstruction through `uv run python -`
  - exit status: `0`
  - result: physical
    `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
    and semantic
    `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`
    reproduced.
- command: copied/constructed `CanonicalJsonValue` bypass and end-to-end
  encoder reproduction through `uv run python -`
  - exit status: `0`
  - result: P1 reproduced; stored Boolean became tagged integer `1`, and the
    changed value reached an 808-byte Parquet payload with SHA-256
    `644514dc529493293c6e8bbfa61eb185c7ac94218cb2238bfa3260f264e9f8c0`.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-logical-arrow-projection-implementation-independent-review-R1.md`
  - SHA-256: `8b40285f742be1434670fecca743c9d94c3513b1edc7e583ab073d913c9db9eb`
  - machine recommendation: `REWORK`
  - finding: `W04-LAP-IMPL-R1-P1-01`

## Risks

- The current public writer can silently coerce bypassed logical model state
  before the strict inverse, invalidating exact evidence semantics. The
  23-root producer must remain paused.
- No current root schema or product byte was found; the defect was reproduced
  only in memory during review.

## Follow-up items

- Bounded serializer/test rework: strictly revalidate raw direct and nested
  union-member state before serialization, add `model_copy` and
  `model_construct` adversarial cases, preserve all valid vectors, then obtain a
  fresh independent review and master acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

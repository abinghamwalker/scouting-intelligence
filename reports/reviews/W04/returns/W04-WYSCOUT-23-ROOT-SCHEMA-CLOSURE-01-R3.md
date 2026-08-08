# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R3`
- objective: Correct the four preserved R2 P1 findings within the bounded 23-root
  W04 schema closure and authorized two-field canonical-Decimal Arrow projection.
- final task-packet SHA-256:
  `0d578583e7896f110e566430f98a6600fc0d6872383fefb7b53e5824547649e4`

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `src/scouting/contracts/wyscout_schema.py`
- `tests/contracts/test_w04_wyscout_schema_closure.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R3.md`

## Summary

- Added the sole `CANONICAL_DECIMAL_UTF8` scalar projection kind. Its forward path
  accepts only an exact finite `Decimal`, canonicalizes signed zero to `0`, renders
  fixed-point text without exponent, removes only redundant fractional zeroes, and
  performs no rounding or LF framing. Its inverse requires exact UTF-8, parses
  directly to finite `Decimal`, canonicalizes again, and requires byte equality.
- Applied that projection by exact owning model/field identity only to
  `GoldCoverageDimension.coverage` and `GoldCoverage.coverage_overall`, including
  every nested occurrence. Every other Decimal remains `decimal128(22,18)`.
- Corrected all runtime predicate operands against their owning Pydantic field
  graphs and corrected the coordinate, dependency-clock, boundary-state,
  descriptor-range, four-data-authority, generic season and generic lineup claims.
- Classified runtime validators separately from five external/composed authority
  predicates for guarded completion, season UUID, exact one-lineup population,
  five-row build composition and complete LayerManifest receipt/readback closure.
- Embedded the exact frozen structured corpus for all 15 source members, four data
  authority rows/clocks, five build authority rows, five dependency rows, the
  119-row field registry and digests, strict subevent mapping/reasons, possession
  sets/equal-clock order, the one-match completion-index population, season/lineup
  binding, and sole R4 LayerManifest semantic/receipt composition.
- Expanded descriptor-led Arrow construction and inverse logical equality to both
  variants of all twelve Parquet roots, including nullable branches and nested
  tuple/list/model paths. Added independent operand resolution, corpus reproduction,
  authority-source hashing, placeholder attacks and the required Decimal vectors.

## Tests run

- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: 4 files already formatted
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: all checks passed
- command: `uv run mypy src/scouting/storage/formats.py src/scouting/contracts/wyscout_schema.py tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: no issues in 4 source files
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: 0
  - result: 540 passed in 119.40s
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: 0
  - result: 179 passed in 3.86s
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS 25/25; zero configured remotes

## Artifacts/evidence

- `src/scouting/storage/formats.py` SHA-256:
  `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c`
- `tests/unit/test_w04_wyscout_product_formats.py` SHA-256:
  `19cd38b7d104029f96c98243992fda126f7a448e71ee5c545128acf2699e17a4`
- `src/scouting/contracts/wyscout_schema.py` SHA-256:
  `fa2f0739a617ef112273e8b1010f2a7f81231027b28710198c55934e8363349e`
- `tests/contracts/test_w04_wyscout_schema_closure.py` SHA-256:
  `ef546491d8ad3618f5982f7a68d3ddeae1cf8c1317d8e9f0ead7c3cad97bc4b4`
- This return is producer evidence only; it does not self-approve the candidate.

## Risks

- Fresh independent review and master acceptance remain mandatory before the
  23-root producer or any product implementation resumes.
- Tagged canonical coverage text intentionally preserves exact reversible Decimal
  evidence at the cost of nested Parquet-native numeric querying for those two
  logical fields, exactly as authorized.

## Follow-up items

- Dispatch the bounded R3 candidate for fresh independent review, then master-run
  the complete repository gate and decide acceptance or bounded rework.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no product, aggregate, provider, network, cloud, container, CI, publication or
  deployment action: confirmed

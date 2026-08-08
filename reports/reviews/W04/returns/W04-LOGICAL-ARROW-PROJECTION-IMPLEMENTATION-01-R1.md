# Subagent return

## Task

- task_id: `W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-01-R1`
- objective: Implement only the accepted descriptor-led logical-to-Arrow
  projection correction while preserving the existing W04 semantic preimage,
  identity vectors, fail-closed Gold schema state, and local-only boundary.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `src/scouting/contracts/wyscout_build.py`
- `tests/contracts/test_w04_wyscout_build_contract.py`
- `reports/reviews/W04/returns/W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-01-R1.md`

## Summary

- Verified every packet-fixed SHA-256 before editing; no binding drift existed.
- Added the exact closed scalar, struct, list, field, and projection descriptor
  dataclasses/enums, recursive exact-runtime-type validation, and
  `arrow_schema_from_w04_projection`.
- Removed caller `schema`, `schema_role`, and semantic-schema-descriptor authority
  from both public encoder/hash APIs. Generated Arrow schemas now come only from
  the supplied exact projection descriptor, while tables are exact recursive
  readback witnesses.
- Implemented descriptor-directed identity objects, positional tuple structs,
  homogeneous lists, outer nullability, exact fixed cardinality, and recursive
  metadata absence.
- Implemented present `CanonicalJsonValue` as exact typed tagged canonical JSON in
  one non-null UTF-8 scalar without LF. The inverse strictly rejects invalid UTF-8,
  duplicate keys, invalid constants/float tokens, surrogates, non-NFC text,
  noncanonical bytes, and typed-union drift before hashing or writing.
- Preserved the sole `w04-wyscout-parquet-semantic-v1` framing and existing
  `WyscoutParquetSchemaDescriptor` bytes. Projection content adds no semantic
  preimage component or alternate derivation.
- Preserved exact identity physical SHA-256
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
  and semantic SHA-256
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.
- Removed Arrow table/schema/equivalent authority fields from
  `GoldProductReadback`. Receipt closure revalidates the exact logical one-match
  Gold row and then raises `GoldSchemaAuthorityUnavailableError`; no fixture,
  caller byte/digest, table, schema, or equivalent object can authorize a Gold
  root before the later accepted descriptor exists.
- Added the focused adversarial matrix for all seven tagged variants, nested mixed
  content, tagged-null versus outer-null, malformed inverse bytes, tuple/list
  schema drift, empty/nonempty sequence identity, fixed size, recursive metadata,
  alternate authority objects, unchanged golden vectors, and zero-write tripwires.

## Tests run

- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `4 files already formatted`.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: no issues in four source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `134 passed in 2.80s`.
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `179 passed in 3.81s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 controls; zero configured remotes.

## Artifacts/evidence

- `src/scouting/storage/formats.py` —
  `d1827127ce36a67dc49993f5cdb4cd18a5ab5bc62f3b753808529f66dba9f2c9`
- `tests/unit/test_w04_wyscout_product_formats.py` —
  `b5fe5aa5831755abe83cd8fd812538dbfbb091190a42430fb09c9141d7e33cce`
- `src/scouting/contracts/wyscout_build.py` —
  `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16`
- `tests/contracts/test_w04_wyscout_build_contract.py` —
  `ae2edd8c96794cf39cca2159b2a769858036ee5db9674cdefee07396c0a10693`

## Risks

- Tagged JSON is intentionally opaque to nested Parquet predicates, matching the
  accepted tradeoff.
- Gold receipt completion remains deliberately unavailable until a separately
  accepted exact `GOLD_PLAYER_WINDOW` projection descriptor exists.

## Follow-up items

- Fresh independent implementation review and master reproduction/acceptance are
  still required before the 23-root producer resumes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

# Subagent return

## Task

- task_id: `W04-PARQUET-SEMANTIC-ENCODER-01`
- objective: Correct only the two R2 schema-authority gaps by rejecting recursive
  list value-field metadata and requiring the public W04 semantic hash helper to
  validate an exact explicit Arrow schema before emitting a digest.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R3.md`

## Summary

- Verified all four R2 fixed hashes before editing. The R2 format, test, review,
  and review-return bytes matched the packet exactly.
- The closed recursive Arrow type validator now inspects the `value_field` of
  list, large-list, and fixed-size-list types at every depth. Each child name must
  be canonical, its nullability must be represented as a Boolean Arrow field
  property, and any child metadata fails closed before hashing or encoding.
- The public `w04_wyscout_parquet_semantic_sha256` boundary now requires a
  non-optional explicit `pa.Schema`. It runs that schema and the supplied
  descriptor role through the same closed validator used by the encoder, then
  requires exact equality between the derived and supplied descriptors before
  calculating the R20 digest.
- Removed the former descriptor-only validation path. There is no descriptor-only
  fallback or alternate public W04 semantic emitter; the encoder supplies its
  already checked explicit schema to the same helper.
- Added differential adversarial coverage for list, large-list, fixed-size-list,
  and recursively nested list child metadata. These tests prove the metadata-free
  variant is accepted while the physically distinct hidden-metadata variant is
  rejected even though PyArrow renders both type strings identically.
- Added direct helper boundary coverage for exact valid schema/descriptor use;
  omitted schema; fabricated binary, malformed, and metadata-like type text;
  mismatched field, nullability, order, and serializer; invalid role; actual binary
  schema; naive, non-UTC, and nanosecond timestamp schemas; and recursive child
  metadata. Added canonical list child-name and digest-bound role checks.
- Preserved the R20 semantic preimage and valid vectors exactly:
  physical `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
  and semantic `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.
  No generic serializer API or writer control changed.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R2.md reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R2.md`
  - exit status: `0`
  - result: all four packet-fixed pre-edit hashes matched exactly.
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: both files formatted.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: no issues in two source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `68 passed in 2.21s` with no warnings.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py::test_fixed_physical_and_semantic_vectors_are_repeatable tests/unit/test_w04_wyscout_product_formats.py::test_list_value_field_metadata_is_rejected_at_every_recursive_depth tests/unit/test_w04_wyscout_product_formats.py::test_list_value_field_name_must_be_canonical tests/unit/test_w04_wyscout_product_formats.py::test_public_semantic_helper_requires_exact_validated_arrow_schema tests/unit/test_w04_wyscout_product_formats.py::test_semantic_schema_role_is_validated_and_digest_bound`
  - exit status: `0`
  - result: `8 passed in 0.13s`; fixed vectors reproduced and all new R3
    boundaries failed closed under their adversarial cases.
- command: `uv run bandit -q -r src/scouting/storage/formats.py`
  - exit status: `0`
  - result: no findings. The unchanged command required approved read access to
    uv's cache metadata after the workspace sandbox denied that cache read.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 34 files and 60 dependencies analyzed; all three contracts kept. The
    unchanged command required approved read access to uv's cache metadata after
    the workspace sandbox denied that cache read.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 local-only checks passed, including zero configured
    remotes and no cloud, container, hosted CI, endpoint, or deployment surface.

## Artifacts/evidence

- `src/scouting/storage/formats.py`
  - R3 SHA-256:
    `76c46de2b54b4d69a9f7bef89b7976e00f9d384cddded50206de0f7fc3723edc`
- `tests/unit/test_w04_wyscout_product_formats.py`
  - R3 SHA-256:
    `38241e232f886c85d350a7fcd01d45ed4675abfc4ee69f012a807a9e0d80b54b`
- preserved physical vector:
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- preserved semantic vector:
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`

## Risks

- No producer-identified P0-P2 issue remains within this bounded R3 correction.
  Fresh independent byte/security review and master reproduction remain mandatory
  before the implementation can be accepted or any downstream product work resumes.
- The schema role is intentionally semantic input, not a property derivable from
  Arrow schema bytes. It must be canonical and is included in the exact derived
  descriptor and digest; a canonical different role therefore produces a different
  valid semantic digest rather than aliasing the original role.

## Follow-up items

- Master independently reproduces R3, freezes these implementation/test bytes, and
  dispatches a fresh independent review against their exact hashes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- no product/control write, provider/network action, cloud, container, hosted CI,
  endpoint, remote, or deployment: confirmed

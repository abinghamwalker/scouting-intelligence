# Subagent return

## Task

- task_id: `W04-LOGICAL-ARROW-PROJECTION-DECISION-01-R1`
- objective: Freeze the exact bounded logical-to-Arrow projection authorization as a canonical, progression-safe control-plane authority without implementation or schema/product bytes.

## Files changed

- `reports/reviews/W04/authorities/wyscout-logical-arrow-projection-decisions-v1.json`
- `tests/contracts/test_w04_logical_arrow_projection_authority.py`
- `reports/reviews/W04/returns/W04-LOGICAL-ARROW-PROJECTION-DECISION-01-R1.md`

## Summary

- Materialized one strict R20-canonical JSON authority object plus exactly one terminal LF with the packet-fixed decision ID, schema version, authority class, actor and clock.
- Bound all nine immutable authorization, readiness, R20/R21, accepted encoder-review and master-acceptance artifacts at their verified physical SHA-256 values.
- Froze present `CanonicalJsonValue` as strict non-null Arrow UTF-8 containing exact tagged logical JSON without LF, with strict duplicate-key/constant/UTF-8/typed/canonical byte-equality inverse validation and a distinct outer-optionality rule.
- Froze heterogeneous fixed tuples as descriptor-owned ordered structs and homogeneous variable/fixed sequences as descriptor-owned lists. Exact child names, positions, physical types, order, nullability and cardinality are accepted descriptor content and are never inferred from a row, fixture, observed value or empty sequence.
- Preserved the exact `w04-wyscout-parquet-semantic-v1` framed schema/ordered-logical-row/ordered-parent preimage and sole SHA-256 derivation. The correction can affect only the physical schema supplied through the existing descriptor input.
- Kept lifecycle state `AUTHORITY_ONLY_NO_SCHEMA_OR_PRODUCT_BYTES`; fresh authority review/master acceptance, serializer implementation review/master acceptance, and only then 23-root resumption are the exact progression.
- Added a focused progression-safe test that strict-loads and byte-reproduces the authority, validates every exact nested value and array order, verifies all immutable bindings, rejects representative rule drift and malformed canonical bytes, and does not inspect mutable implementation/product paths.

## Tests run

- command: fixed SHA-256 verification for all packet bindings before editing
  - exit status: `0`
  - result: all nine packet-fixed artifact hashes and packet SHA-256 matched exactly.
- command: `uv run ruff format --check tests/contracts/test_w04_logical_arrow_projection_authority.py`
  - exit status: initial `1`; final `0`
  - result: the initial check identified formatting-only changes; `uv run ruff format tests/contracts/test_w04_logical_arrow_projection_authority.py` formatted the owned test, and the required final check reported `1 file already formatted`.
- command: `uv run ruff check tests/contracts/test_w04_logical_arrow_projection_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy tests/contracts/test_w04_logical_arrow_projection_authority.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`.
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `187 passed in 5.76s` on the final acceptance run.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25/25 controls, zero configured remotes, Python 3.12.12, one root uv project, no cloud/container/hosted-CI/deployment state.

## Artifacts/evidence

- authority decision SHA-256: `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1`
- focused authority test SHA-256: `39406164139b1c016b67ab14289c93a41e0a69b1da6a1b85a0ad818732fc0750`
- task packet SHA-256 reproduced: `691c3e103222ffe265cc772e8bbb072b97ea99cf47f5701b48e7cee897e9917a`

## Risks

- The authority intentionally creates no Arrow descriptor, schema, serializer or product byte. Actual descriptor child names/types/order/nullability and implementation behavior remain subject to their required independent reviews and master acceptances.
- No product/publication authority is granted by this return or the focused passing checks.

## Follow-up items

- Fresh independent authority review, master authority acceptance, then a separately packeted serializer implementation/review/master-acceptance loop before the 23-root producer resumes.

## Scope confirmation

- no Git operations: confirmed; none performed.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; only the three packet-owned paths above were written.

# Subagent return

## Task

- task_id: `W04-LOGICAL-ARROW-PROJECTION-REVIEW-01-R1`
- objective: Freshly and independently review the bounded logical-to-Arrow
  projection authority before any serializer implementation or 23-root schema
  production.

## Files changed

- `reports/reviews/W04/authorities/wyscout-logical-arrow-projection-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-LOGICAL-ARROW-PROJECTION-REVIEW-01-R1.md`

## Summary

- Returned `PASS` with `P0=0`, `P1=0`, and `P2=0` after verifying every
  packet-fixed binding before analysis and again after the final checks.
- Strict-loaded and byte-reproduced the 7,985-byte canonical decision at SHA-256
  `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1`.
- Independently matched the decision to the exact user authorization: present
  tagged logical JSON in non-null Arrow UTF-8 without LF; strict duplicate-key,
  constant, UTF-8, typed, canonical-reencoding and byte-equality inverse;
  outer-null separation; descriptor-owned positional structs and homogeneous
  lists; and accepted-descriptor-only schema generation.
- Attacked invalid UTF-8, nested duplicate keys, invalid constants, floats,
  whitespace, key order, Unicode normalization, wrong discriminators, untagged
  null, Boolean-as-integer, tuple/list drift, schema inference, caller proof
  substitutes, Arrow union authority, and present-null/outer-null confusion.
- Confirmed the exact existing `w04-wyscout-parquet-semantic-v1` framed preimage
  and both accepted identity golden vectors remain unchanged. The correction can
  affect only the existing physical schema descriptor input and adds no digest
  field, preimage, formula, version, or derivation.
- Confirmed the authority is progression-safe and remains
  `AUTHORITY_ONLY_NO_SCHEMA_OR_PRODUCT_BYTES`, with no root, logical field,
  semantics, feature, population, dependency, provider access, publication,
  cloud, container, hosted-CI, endpoint, deployment, or Git-remote expansion.

## Tests run

- command: packet-fixed SHA-256 verification before analysis and after final
  materialization
  - exit status: `0`
  - result: all sixteen packet-fixed hashes matched on both checks; no drift.
- command: complete `read_first` readback, including all 4,516 R20 lines and all
  1,254 R21 lines
  - exit status: `0`
  - result: every required file was read completely before adjudication.
- command: `uv run ruff format --check tests/contracts/test_w04_logical_arrow_projection_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command: `uv run ruff check tests/contracts/test_w04_logical_arrow_projection_authority.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `uv run mypy tests/contracts/test_w04_logical_arrow_projection_authority.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`.
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: final run `187 passed in 5.85s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, all 25 controls, zero configured remotes, local Python 3.12.12
    root uv environment, no cloud/container/hosted-CI/deployment state.
- command: locked/no-sync independent canonical-decision reproduction
  - exit status: initial sandbox cache denial; authorized read-only retry `0`
  - result: exact 7,985 bytes and fixed decision SHA-256 reproduced.
- command: locked/no-sync independent seven-variant tagged-value probe
  - exit status: `0`
  - result: all seven variants round-tripped; present logical null was exact
    non-null `{"kind":"null","value":null}`; untagged null and Boolean integer
    failed.
- command: locked/no-sync independent strict-inverse attack probe
  - exit status: `0`
  - result: canonical nested value passed; 9/9 malformed cases failed, including
    nested duplicate keys, invalid UTF-8/constant/float, noncanonical spelling,
    non-NFC text, and wrong discriminator.
- command: canonical machine-fence extraction and strict reserialization
  - exit status: `0`
  - result: exactly one fence, exact review schema info string, canonical JSON
    body plus one LF, `PASS`, and empty findings reproduced.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/authorities/wyscout-logical-arrow-projection-independent-review-R1.md`
- independent review SHA-256:
  `b864fcf19a72f8680fdc125b1ac92e7674d5edbc853adba45f7b8284efe76f52`
- canonical decision SHA-256:
  `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1`
- packet SHA-256:
  `59196da67c9d10f4504e0399795f96b05453a7c177396ba9023f000dbed1dded`

## Risks

- This review accepts only the frozen representation authority. No concrete root
  descriptor, schema, implementation, product byte, or publication permission
  exists yet.
- Tagged UTF-8 intentionally sacrifices nested Parquet querying for the affected
  heterogeneous values; this is the explicitly authorized reversible-evidence
  tradeoff.

## Follow-up items

- Master independently reproduces this review, accepts or rejects the exact
  authority, then dispatches the separately bounded serializer implementation and
  fresh implementation review before resuming the 23-root producer.

## Scope confirmation

- no Git operations: confirmed; none performed.
- no unauthorised dependency or lockfile changes: confirmed; neither
  `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; only the two packet-owned report
  paths were written.

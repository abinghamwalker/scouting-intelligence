# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-PUBLISHER-AUDIT-01`
- objective: Produce executable evidence and the smallest serial packet sequence for
  the exact R20 Parquet, semantic-digest, and sidecar-free guarded publication seam.

## Files changed

- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-PUBLISHER-AUDIT-01-R1.md`

## Summary

### Verdict

`PASS_TO_PACKET`. The publication gap is additive and bounded. It does not require a
new dependency, architecture, root, product, provider action, network, container,
deployment, or change to R20/R21. Final product/manifest/receipt publication remains
blocked until the two packets below pass independent review.

### Executable comparison with the frozen R20 controls

An in-memory 65,537-row PyArrow probe compared current `parquet_bytes` with the exact
R20 `pq.write_table` controls. Current bytes were SHA-256
`d600e79649ae687ca1a45e7a6e054969dc876a2405fa7e687f98e348824625a2`
(131,812 bytes); the R20-controlled bytes were SHA-256
`c4ff7c10f37af918b8694abafc6de6d2b1e4b25d13047e26257b7557bac485f9`
(110,100 bytes). They were unequal.

| R20 control | Current evidence | Required packet behaviour |
| --- | --- | --- |
| Parquet 2.6 | PASS: metadata `2.6` | Pass `version="2.6"` explicitly. |
| one `part-00000.parquet` per non-empty logical partition | NOT OWNED by generic encoder | Product serializer supplies exactly one bounded table/path; empty partitions emit no Parquet. |
| row group 65,536 | FAIL: 65,537 rows produced one group | Pass `row_group_size=65536`; probe produced two groups. |
| zstd level 9 | PARTIAL: ZSTD, level omitted | Pass `compression="zstd", compression_level=9`. |
| data page 2.0 | PASS in source | Keep `data_page_version="2.0"`. |
| dictionary off | PASS: encodings `RLE, PLAIN` | Keep `use_dictionary=False`. |
| byte-stream split off | implicit only | Pass `use_byte_stream_split=False`. |
| statistics on | FAIL: `statistics_present=False` | Pass `write_statistics=True`; controlled probe was `True`. |
| page index off | implicit only | Pass `write_page_index=False`. |
| microsecond timestamps, no truncation | not explicit | Pass `coerce_timestamps="us", allow_truncated_timestamps=False`; a 1ns value failed with `ArrowInvalid`, as required. |
| stored schema | PASS: `ARROW:schema` present | Pass `store_schema=True`. |
| canonical types and fixed schema | FAIL-CLOSED surface absent | Require an explicit `pa.Schema`; reject inference, extras, type coercion and nullability drift. Project UUID/UTC/Decimal/list values before table creation. |
| full primary-key row order | NOT ENFORCED: input order retained | Each owner supplies its exact primary-key tuple; encoder rejects duplicate keys and any order unequal to `sorted(rows, key=key)`. |

The existing generic encoder must remain available for prior callers. The bounded
implementation should add an R20-specific function rather than silently changing
the bytes of unrelated artifacts.

### Exact semantic-digest contract to freeze in packet 1

Use serializer version `w04-wyscout-parquet-v1` and digest version
`w04-wyscout-parquet-semantic-v1`. All integers below are unsigned 64-bit big-endian;
`frame(x) = UINT64_BE(len(x)) || x`.

```text
schema_bytes = canonical JSON bytes of the closed serializer-owned descriptor:
  {schema_role, serializer_version, fields:[{name,arrow_type,nullable}, ...]}
row_bytes[i] = canonical_contract_json_bytes(the exact checked contract row)
parent_bytes[i] = UTF8(the exact repo-relative parent product path)

preimage =
  UTF8("w04-wyscout-parquet-semantic-v1") || 0x00 ||
  ASCII("S") || frame(schema_bytes) ||
  ASCII("R") || UINT64_BE(row_count) || concat(frame(row_bytes[i])) ||
  ASCII("P") || UINT64_BE(parent_count) || concat(frame(parent_bytes[i]))
semantic_sha256 = lowercase_hex(SHA256(preimage))
```

Rows must already be in the exact artifact primary-key order and be byte-distinct by
key. Parents must equal `tuple(sorted(set(parents)))`; Bronze uses zero parents.
Require counts to fit uint64, NFC/safe exact path bytes, closed schema descriptors,
non-empty rows, and exact re-encoding. This is domain-separated, unambiguous across
schema/row/parent boundaries, independent of Parquet physical bytes, and implements
R20's schema plus length-framed ordered rows and parents without changing its claim.

### Exact staged, sidecar-free publication design for packet 2

Add a separate guarded publication API; do not call `GuardedStorage.write_bytes`,
because it necessarily creates `<payload>.manifest.json` outside the frozen path set.

1. Configure only exact absolute named roots for Wyscout working data, Wyscout
   manifests, and W04 run receipts. Never configure the repository or `data` root.
2. Validate both relative paths with the existing bounded POSIX parser. Open every
   directory descriptor-relative with `O_DIRECTORY|O_NOFOLLOW`; require real
   directories, modes `0700`, containment, and same filesystem for promotion.
3. Create the exact serializer-owned `.partial` path with
   `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW`, mode `0600`. Write all bytes, `fsync`, close,
   reopen no-follow, and verify regular/non-symlink, mode, size, physical SHA-256,
   Parquet schema/settings/rows/semantic digest (or canonical manifest), and final
   code/environment/resource recheck.
4. Preflight the final path. Existing equal bytes are idempotent; existing unequal,
   symlink, non-regular, unsafe-mode, or cross-device destinations fail closed.
5. Promote with the repository's immutable no-replace primitive: descriptor-relative
   `os.link(stage, final, follow_symlinks=False)` followed only after success by
   descriptor-relative unlink of the staged name and directory `fsync`. This gives
   atomic final visibility without an overwrite race. On `FileExistsError`, reopen
   no-follow and accept only exact equal bytes. Never emit a sidecar.
6. On write, validation, recheck, link, or race failure, leave the exact staged
   evidence untouched; do not clean, truncate, repair, suffix, or overwrite it.
   Successful promotion alone removes the staged name. Final readback must equal the
   admitted bytes/digest before a layer manifest can reference it.
7. Publish all products first; publish each checked canonical layer manifest last via
   the same no-replace primitive. Receipt publication remains owned by its separately
   accepted receipt-content packet.

This is additive to existing `GuardedStorage` and preserves current sidecar behaviour
for existing callers. A hard-link promotion is permitted only for this staged
same-filesystem immutable path; tests must prove the final has one link after the
successful staged-name unlink and no alias remains.

### Smallest serial packet sequence and ownership

1. `W04-PARQUET-SEMANTIC-ENCODER-01-R1`
   - allowed: `src/scouting/storage/formats.py`,
     `tests/unit/test_w04_wyscout_product_formats.py`
   - add only the explicit-table R20 encoder, closed schema validation, exact
     primary-key validation and semantic framing above; retain generic APIs.
   - acceptance: known physical/semantic vectors; all controls in the table;
     65,535/65,536/65,537 group boundaries; reordered/duplicate row and parent
     rejection; timestamp truncation, schema/type/nullability/statistics/page-index/
     dictionary/byte-split/level mutations; deterministic repeat.

2. `W04-STAGED-IMMUTABLE-PUBLISHER-01-R1` (only after packet 1 master-verifies)
   - allowed: `src/scouting/storage/guarded.py`,
     `tests/unit/test_w04_staged_product_publisher.py`
   - add only the exact-root, sidecar-free stage/admit/no-replace promotion API above;
     do not modify existing writer semantics.
   - acceptance: successful bytes/readback/mode/link count; identical retry; unequal
     final; partial write; failed validation/recheck; stage/final parent and target
     symlinks; non-regular/unsafe modes; cross-device; link race; missing/extra
     sidecar assertion; all failures leave staged evidence and never alter final.

3. `W04-PUBLICATION-SECURITY-BYTE-REVIEW-01-R1`
   - allowed: one new review return only; read-only producer paths/tests.
   - independently reproduce every vector and adversarial publication test, confirm
     no product/control bytes were written, then return PASS/REWORK to the master.

The master can prepare packet 1 while the separate build/receipt-content authority
gap from `W04-VERTICAL-SLICE-CONTRACT-AUDIT-01-R1` is closed serially. Product
publication must wait for both streams; this publisher sequence itself has no wider
blocker.

## Tests run

- command: complete read of every packet `read_first` path plus bounded source search
  - exit status: `0`
  - result: current generic encoder and mandatory sidecar behaviour confirmed; exact
    R20 path/serializer/publication controls reconciled.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run python -B -c <in-memory PyArrow comparison>`
  - exit status: `0`
  - result: current `d600e7...25a2`, 131,812 bytes, one group, no statistics;
    R20-controlled `c4ff7c...85f9`, 110,100 bytes, two groups, statistics present;
    unequal bytes; nanosecond-to-microsecond loss rejected.
- command: initial sandboxed form of the same probe
  - exit status: `2`
  - result: sandbox denied read of a uv cache `.git` path; no Python/product action
    ran. The identical read-only probe was rerun through the approved uv boundary.

## Artifacts/evidence

- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-PUBLISHER-AUDIT-01-R1.md`
- current encoder probe SHA-256:
  `d600e79649ae687ca1a45e7a6e054969dc876a2405fa7e687f98e348824625a2`
- exact-control probe SHA-256:
  `c4ff7c10f37af918b8694abafc6de6d2b1e4b25d13047e26257b7557bac485f9`

## Risks

- P1: changing generic `parquet_bytes` would silently change unrelated artifact
  bytes; packet 1 must be additive.
- P1: `write_bytes` is not a product publisher because its sidecar expands the
  frozen path set.
- P1: preflight plus replacing `rename` is race-unsafe; use atomic no-replace link
  promotion and independently review its same-filesystem/link-count invariants.
- P1: a semantic digest over Parquet bytes, inferred schema, unordered rows, or
  unframed concatenation is not R20 semantic authority.
- P2: successful publication primitives do not provide build-ID or receipt-content
  authority; those remain the separate contract-audit closure.

## Follow-up items

- Master issues the three serial packets above and integrates them only after the
  separate build/receipt-content gap is accepted.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation, product/control bytes, provider/network action, cloud,
  container, hosted CI, endpoint, remote, or deployment: confirmed

# W04 Parquet semantic encoder independent review — R3

Date: 2026-07-31

Verdict: **REWORK**

Finding counts: **P0 0 / P1 1 / P2 0**

This is a fresh independent byte/security review of the exact R3 candidate fixed by
`W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R3`. It grants no product or publication
authority.

## Fixed candidate and chain of custody

All fixed bindings matched before analysis and immediately before review rendering:

| Binding | Observed SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `76c46de2b54b4d69a9f7bef89b7976e00f9d384cddded50206de0f7fc3723edc` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `38241e232f886c85d350a7fcd01d45ed4675abfc4ee69f012a807a9e0d80b54b` |
| R3 producer return | `ae16eafc67808fa1062c8bcd7a0110f657d29cd11bac6bbab84bfb7f28425645` |

The frozen R20 authority remained
`8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`.
The fixed physical vector reproduced as
`889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`;
the independently reconstructed semantic preimage reproduced
`6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

The preflight and final postflight read-only bytecode inventories were identical:
1,162 `.pyc` files in 150 `__pycache__` directories, content-stream digest
`4e5933f579d3c0017d7c07c55dc509bfb54530ba5f83d4561b5003d1331a03a1`
and path/mode/link-count/size stream digest
`dc6b98f574580d8dc42cbe1a1c0bab21ae948626bbbc1395c89113bc8a2b630a`.

## P1 — explicit empty schema metadata is accepted but unbound

Code: `W04_ENCODER_EMPTY_SCHEMA_METADATA_UNBOUND`

The R3 validator rejects metadata by truthiness. PyArrow distinguishes an absent
schema metadata map (`None`) from an explicitly present empty map (`{}`), but `{}`
is false in a Boolean test. Consequently, both the encoder and public semantic
helper accept an explicit empty schema metadata map as if metadata were absent.

The mandatory differential probe encoded the same one-row `record_id: int64`
table under two schemas. Their only difference was top-level schema metadata:

| Variant | Descriptor | Semantic SHA-256 | Physical SHA-256 | Bytes |
| --- | --- | --- | --- | ---: |
| metadata absent (`None`) | equal | equal | `c4860fb36155968ca678f1a1ace30f2469c2eab113e502daf679c5a50ddc774f` | 472 |
| explicit empty metadata (`{}`) | equal | equal | `7fa92ee32a81ce6aa07a3442a9e14f782dd6d04babef6021e291a6652e4e449e` | 492 |

Both encodes succeeded. Their `WyscoutParquetSchemaDescriptor` values and semantic
digests were identical, while their stored-schema Parquet bytes and physical
digests differed. The public semantic helper also accepted the empty-metadata
schema against the descriptor derived from the metadata-absent schema and emitted
the same semantic digest.

This is a false physical-to-semantic schema binding. It bypasses the packet's
metadata-free requirement through a distinct metadata representation not covered
by non-empty-map tests. Explicit empty metadata maps were also accepted on top-level
fields, struct children and list value fields. PyArrow currently normalizes those
field-level empty maps to equal serialized field bytes, but they still violate the
closed metadata-free boundary and must not remain an alternate accepted form.

### Bounded correction required

Reject metadata presence rather than metadata truthiness throughout the closed
recursive schema validator. In particular, require `metadata is None` for:

1. the schema;
2. every top-level field;
3. every struct child field; and
4. every list, large-list and fixed-size-list value field at every depth.

Add differential tests for `None` versus `{}` at all four boundaries. The
schema-level test must prove the physically different stored-schema variant fails
before semantic hashing or Parquet encoding. Preserve the R1 row/key closure, R2
non-empty recursive metadata closure, public exact-schema requirement, generic
serializer API, and both fixed vectors.

## Passing evidence outside the finding

- R2's non-empty metadata attacks failed closed for list, large-list,
  fixed-size-list and nested-list value fields through both encoder and public
  helper. Non-canonical list child names failed.
- The public helper rejected omitted schema, fabricated binary/malformed/
  metadata-like descriptor text, descriptor field/nullability/serializer mismatch,
  invalid role, an actual binary schema, naive and non-UTC timestamps, nanosecond
  timestamps and recursively hidden non-empty child metadata.
- R1's unchanged-key non-key divergence, Arrow-key divergence, string/integer and
  Boolean/integer key confusion, and missing Arrow key failed closed. Exact null,
  list, decimal, UTC-microsecond and struct recursion passed; decimal divergence,
  forbidden list nulls, binary values, non-finite floats and struct child metadata
  failed.
- Independent semantic framing separated parent sequences `("a", "bc")` and
  `("ab", "c")` despite equal unframed concatenation.
- Exact Parquet 2.6 bytes, stored schema, ZSTD compression, statistics, no
  dictionary, no byte-stream split, no column/offset indexes, deterministic
  readback and both fixed vectors reproduced. The source call preserves ZSTD level
  9, data-page 2.0, page index off and microsecond timestamps without truncation.
- Independent 65,535/65,536/65,537 probes produced `(65535)`, `(65536)` and
  `(65536,1)`. Nanosecond timestamps failed before encoding.
- The focused encoder and unchanged generic guarded-storage suites passed all 68
  tests. Local-only verification passed all 25 controls and reported zero remotes.

## Commands and results

- `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R3.md`
  - exit `0`; all three packet-fixed hashes matched before analysis and immediately
    before rendering.
- read-only shell `.pyc` census plus complete content and metadata streams
  - exit `0` preflight and postflight; counts and both digests were identical.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <None-versus-empty metadata representation probe>`
  - exit `0`; schema serialization differed for `None` versus `{}`; field/list
    empty maps remained explicitly observable as `{}`.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <empty-schema-metadata differential encoder probe>`
  - exit `0`; descriptor equality `true`, semantic equality `true`, physical
    equality `false`; exact physical digests and sizes are listed above.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <recursive metadata and public-helper attack probe>`
  - exit `0`; all 20 omitted-schema, descriptor, unsupported-type, timestamp and
    recursive non-empty-metadata cases rejected.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <row/key congruence and recursive-value attack probe>`
  - exit `0`; both valid recursive rows encoded and all 10 divergence,
    type-confusion, forbidden-null, unsupported and non-finite cases rejected.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent fixed-vector, framing, Parquet-control and row-group probe>`
  - exit `0`; both fixed vectors, framing separation, exact controls,
    `[65535]`, `[65536]`, `[65536,1]` and timestamp rejection reproduced.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <empty-metadata public-helper confirmation>`
  - exit `0`; helper accepted empty schema metadata; empty maps were observable at
    schema, top-field, struct-child and list-child boundaries.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit `0`; `68 passed in 2.06s`.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25/25 controls and zero configured remotes.

No Git command or product, manifest, receipt, source, provider, network, cloud,
container, hosted-CI, endpoint, remote or deployment action occurred.

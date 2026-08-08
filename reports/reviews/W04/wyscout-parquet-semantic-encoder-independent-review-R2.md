# W04 Parquet semantic encoder independent review — R2

Date: 2026-07-31

Verdict: **REWORK**

Finding counts: **P0 0 / P1 2 / P2 0**

This is a fresh independent byte/security review of the exact candidate fixed by
`W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R2`. It grants no publication or product
authority.

## Fixed candidate and chain of custody

All fixed bindings matched before analysis and matched again immediately before
this review was written:

| Binding | Observed SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `cfa25e672072cba702d103a2a68c79f2895852ee91e966b998cc3a2e13beb5ea` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `113af1f3b23aac813e0b8484b02348f53d96af0eb816cb495ae90325d5dd158f` |
| R2 producer return | `5c007e2f370c7e231ea83e6a19d3f0ce35121a17dbdb40ef12fe5d6624aee063` |

The fixed physical vector reproduced as
`889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`.
The independently reconstructed length-framed semantic preimage reproduced
`6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

The preflight and postflight read-only bytecode inventories were identical:
1,162 `.pyc` files in 150 `__pycache__` directories, content-inventory digest
`6cabbe001e27ade45328d7620b0dad60469d4e2d33af4542f66893a0ab0c956d`,
and path/mode/link-count/size inventory digest
`8604aa63a0b70862ff284e1b2c1cb03703f440c258eeb05171816e60b32c605f`.

## P1 — nested list child metadata is omitted from semantic authority

Code: `W04_ENCODER_NESTED_LIST_METADATA_UNBOUND`

`_validate_supported_arrow_type` validates the child type of `list`,
`large_list`, and `fixed_size_list`, but does not inspect the child
`value_field.metadata`. PyArrow's string rendering of those types omits that
metadata, and the schema descriptor is built from that string. As a result, the
encoder accepts physical Arrow schema metadata that neither appears in the schema
descriptor nor affects the semantic digest.

The independent differential probe encoded the same one-row table twice. The
only difference was metadata `{b"hidden": b"value"}` on the non-nullable list
item field. Both candidates were accepted. Their schema descriptors were equal and
their semantic SHA-256 values were equal to
`c94a0e014d54a2f19052335a7d7edb01ac54b36c1a93af106c5d1e545f92bb2a`,
but their physical SHA-256 values differed:

- no child metadata:
  `57e1a32d8f8986a16ff9f320d2b40a63fe2d5df8deb1ece4a05e886a2d65f987`;
- hidden child metadata:
  `170d32afe4179362574c4e28c73112cfbb368fa8ee92037137e5ee208dbaa06c`.

Direct probes showed the same acceptance for `large_list` and
`fixed_size_list`. This recreates a false physical-to-semantic binding at a nested
schema boundary even though R1's row-value binding is corrected.

### Bounded correction required

Reject metadata on every nested list value field before semantic hashing or
Parquet encoding, consistently across list, large-list and fixed-size-list. Add
positive and negative recursive-schema tests proving that nested metadata cannot
be erased by descriptor rendering and that equal semantic digests cannot describe
physically different accepted schemas. Preserve the fixed vectors and generic
serializer API.

## P1 — public semantic helper accepts unvalidated descriptor type claims

Code: `W04_SEMANTIC_DESCRIPTOR_TYPE_AUTHORITY_UNVALIDATED`

`w04_wyscout_parquet_semantic_sha256` is public and accepts a directly constructed
`WyscoutParquetSchemaDescriptor`. `_validate_schema_descriptor` checks only that
each `arrow_type` string is nonempty and NFC. It does not require the string to be
the canonical rendering of an encoder-supported Arrow type, nor apply the
encoder's recursive type, timestamp, metadata and nullability boundary.

The packet-mandated direct-descriptor probe obtained semantic digests for all of
the following unsupported or malformed claims:

| Direct `arrow_type` claim | Emitted semantic SHA-256 |
| --- | --- |
| `binary` | `4176755c30f7f5089be767fe75e08e7c165f8b7367d02c876411464e6f6af411` |
| `list<item: string not null>` supplied without an Arrow schema | `5536c28c64ca26fc09a2ac9f0da8dd86fc1655ee142df966c683fadec2ed1fa5` |
| metadata-like multiline `int64` text | `ecabdd51fef810b2404148a8f9e0ece6f7a395bd8dbe5468e7ed96e4d428d87e` |
| `not-an-arrow-type` | `96e8597c397485f9580667b32ba71fcca4c1407abd0c6b6a6016674016e70623` |

Callers can therefore create a digest carrying the W04 semantic domain and
serializer version for a schema the W04 encoder would reject or could never
produce. The review packet expressly requires `REWORK` for this condition.

### Bounded correction required

Make the public helper fail closed unless every descriptor field is the exact
canonical representation of the same closed recursive Arrow schema language
accepted by the encoder. Unsupported, malformed, metadata-like, non-UTC or
non-microsecond timestamp text and every representation that loses nested schema
authority must fail. Add direct-construction adversarial tests. Preserve the valid
fixed descriptors, vectors, semantic framing and generic serializer behavior.

## Passing evidence outside the findings

- R1's unchanged-key/non-key Arrow divergence, Arrow-key divergence,
  string/integer confusion, Boolean/integer confusion and absent Arrow key all
  failed closed before hashing or encoding in an independent probe.
- Exact full-row correspondence passed for null, decimal, list and nested struct
  values plus UTC microsecond timestamps. Forbidden nested nulls, binary values,
  non-finite floats, non-UTC timestamps and struct child metadata failed closed.
- Exact Parquet 2.6 bytes, stored schema, ZSTD encoding, statistics, no dictionary,
  no byte-stream split, no column/offset indexes, deterministic readback and the
  fixed physical vector reproduced.
- Independent 65,535/65,536/65,537 probes produced row-group sizes `(65535)`,
  `(65536)`, and `(65536, 1)`. Nanosecond timestamps failed before encoding.
- Independent semantic framing reproduced the fixed vector. The focused encoder
  and unchanged generic guarded-storage suites passed all 61 tests.
- Local-only verification passed all 25 controls and reported zero configured
  remotes.

## Commands and results

- `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R2.md`
  - exit `0`; all packet-fixed hashes matched before analysis and immediately
    before rendering.
- read-only shell `.pyc` census plus complete content and metadata inventory
  - exit `0` before and after all Python commands; counts and both digests were
    identical.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <mandatory direct-descriptor authority probe>`
  - initial sandbox attempt exited `2` because the sandbox denied the existing uv
    cache `.git` path; the identical approved read-boundary rerun exited `0` and
    emitted four unauthorized semantic digests, as listed above.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent R1 bypass, fixed-vector and framing probe>`
  - exit `0`; all five bypasses rejected and both fixed vectors/framing reproduced.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent recursive projection and failure probe>`
  - exit `0`; supported recursive forms passed; forbidden null, binary, non-finite,
    non-UTC and struct-metadata forms rejected.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <nested list metadata differential probe>`
  - exit `0`; equal descriptor and semantic digest but unequal physical digest.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent exact physical controls and row-group probe>`
  - exit `0`; row groups were `[65535]`, `[65536]`, `[65536,1]`; exact controls
    passed and nanosecond timestamp was rejected.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit `0`; `61 passed in 2.14s`.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25/25 local-only controls, zero configured remotes.

No product, manifest, receipt, source, provider, network, cloud, container, hosted
CI, endpoint, remote or deployment action occurred. No Git command was run.

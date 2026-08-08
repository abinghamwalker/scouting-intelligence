# W04 logical-to-Arrow projection implementation design R1

- Task: `W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-DESIGN-01-R1`
- Status: **IMPLEMENTABLE BOUNDED DESIGN — NOT AUTHORITY OR SELF-ACCEPTANCE**
- Scope: descriptor/encoder correction only; no implemented root, schema digest,
  product byte, manifest, receipt, provider access, dependency or deployment

## Frozen-input readback

All packet bindings were recomputed before this design was written:

| Input | Required and observed SHA-256 |
|---|---|
| authorization | `eeb28f62b631b70e6c7046f3e8a6cdba74c1a7a4996c7024e98c471b08b8dd69` |
| readiness audit | `f9961082a27b949da6b9c1647b50f9ce18b6862c66fb8c104826c4b20ca746a0` |
| R20 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| accepted encoder | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` |
| accepted encoder tests | `c0afb390ef44f19d4759b62495bc0125a14fb80ac0f1e4376972a798702e3a9f` |

No drift was found.

## Exact minimal descriptor

Add the following frozen, slot-based dataclasses and enums to
`scouting.storage.formats`. They are content values, contain no callback, and
are recursively validated before any table or row is inspected.

```text
WyscoutArrowScalarType =
  NULL | BOOL |
  INT8 | INT16 | INT32 | INT64 |
  UINT8 | UINT16 | UINT32 | UINT64 |
  FLOAT16 | FLOAT32 | FLOAT64 |
  UTF8 | DECIMAL128 | TIMESTAMP_US_UTC

WyscoutLogicalArrowProjectionKind =
  IDENTITY |
  CANONICAL_JSON_VALUE_UTF8 |
  OBJECT_STRUCT |
  POSITIONAL_TUPLE_STRUCT |
  HOMOGENEOUS_LIST

WyscoutArrowScalarNode(
  scalar_type,
  projection_kind,       # IDENTITY or CANONICAL_JSON_VALUE_UTF8 only
  decimal_precision,     # required only for DECIMAL128
  decimal_scale,         # required only for DECIMAL128
)

WyscoutArrowStructNode(
  projection_kind,       # OBJECT_STRUCT or POSITIONAL_TUPLE_STRUCT only
  children,              # ordered tuple[WyscoutArrowProjectionField, ...]
)

WyscoutArrowListNode(
  projection_kind,       # HOMOGENEOUS_LIST only
  list_kind,             # LIST | LARGE_LIST | FIXED_SIZE_LIST
  item,                  # one WyscoutArrowProjectionField
  fixed_size,            # positive int only for FIXED_SIZE_LIST; otherwise None
)

WyscoutArrowProjectionField(
  name,                   # canonical existing field-name grammar
  nullable,               # exact bool
  node,                   # one exact node above
  logical_position,       # int only for tuple children; otherwise None
)

WyscoutParquetProjectionDescriptor(
  schema_role,
  serializer_version,    # exactly w04-wyscout-parquet-v1
  fields,                 # non-empty ordered tuple of projection fields
)
```

`DECIMAL128` requires `1 <= precision <= 38` and
`-precision <= scale <= precision`; every other scalar requires both decimal
parameters to be `None`. `CANONICAL_JSON_VALUE_UTF8` requires physical `UTF8`
and no children. An object struct requires non-empty, unique canonical child
names and every child `logical_position=None`. A positional tuple requires
non-empty children whose physical order is exactly their unique
`logical_position=0..n-1` order. The position is recorded even though tuple
order is also physical order; this closes reorder-with-renaming substitutions.
A list has exactly one named item field, including its exact nullability and
node. Fixed-size lists require their exact positive size. Other lists require
`fixed_size=None`.

Metadata is not represented and must be absent from the generated schema at
the schema, top-field, struct-child and list-child levels. Descriptor objects
with a subclassed dataclass, list instead of tuple, non-`bool` nullability,
unknown enum value, extra semantic state, callback, `pa.Schema`, observed row,
or fixture inside them fail before schema construction.

## Exact API and authority boundary

The existing encoder becomes descriptor-led:

```text
arrow_schema_from_w04_projection(
  descriptor: WyscoutParquetProjectionDescriptor,
) -> pa.Schema

encode_w04_wyscout_product_parquet(
  table: pa.Table,
  *,
  projection_descriptor: WyscoutParquetProjectionDescriptor,
  primary_key_fields: tuple[str, ...],
  primary_keys: Iterable[tuple[str | int, ...]],
  contract_row_bytes: Iterable[bytes],
  parent_paths: Iterable[str],
) -> WyscoutParquetEncoding

w04_wyscout_parquet_semantic_sha256(
  *,
  projection_descriptor: WyscoutParquetProjectionDescriptor,
  contract_row_bytes: Iterable[bytes],
  parent_paths: Iterable[str],
) -> str
```

There is no `schema`, `schema_role`, schema callback, Boolean authority,
alternate descriptor, or inferred-row argument. The schema and role are derived
only from the descriptor. The supplied table is a physical readback witness;
its complete recursive schema must equal the generated schema with metadata
checked. `pa.Table.from_pylist`, `pa.table`, row/fixture inspection and PyArrow
inference are not used to generate the schema.

For this correction, tests use literal synthetic descriptors only to test the
mechanism. They are not accepted W04 root authority. The subsequent 23-root
producer must create each runtime descriptor only by strictly parsing that
root's independently accepted canonical `parquet_projection` content. Product
admission additionally binds that root content digest. Merely constructing an
equivalent Python descriptor, supplying a digest, or supplying a table does not
create accepted root authority.

## Projection behavior

Projection is recursively descriptor-directed in both directions:

- `IDENTITY` retains the accepted existing scalar conversion: booleans and
  integers preserve exact Python type; finite floats remain floats; UTF-8 is
  NFC text; finite decimal is the exact fixed-point string; UTC microsecond
  timestamp is the existing canonical UTC string.
- `OBJECT_STRUCT` maps exact physical child names to a logical JSON object.
- `POSITIONAL_TUPLE_STRUCT` maps physical child position `i` to logical JSON
  array position `i`; child names never become logical keys.
- `HOMOGENEOUS_LIST` maps its one descriptor-owned child recursively for every
  item. Empty and non-empty values use the same schema.
- outer Arrow null is handled only by the containing field's `nullable` flag.
  It yields logical outer null only when allowed. A non-nullable outer field or
  child rejects it before projection.

### Tagged `CanonicalJsonValue` writer

The writer accepts only an exact value validated by
`TypeAdapter(CanonicalJsonValue)`. It dumps the validated variant in JSON mode,
then applies the existing R20 canonical JSON rules: sorted object keys, no
insignificant whitespace, NFC Unicode scalar text, strict JSON numbers and
UTF-8. It returns the UTF-8 text scalar for those exact bytes **without** an LF.

Examples are logical tagged values, not raw JSON:

```text
CanonicalJsonNull()       -> {"kind":"null","value":null}
CanonicalJsonInteger(7)  -> {"kind":"integer","value":7}
```

The first example is a present non-null Arrow UTF-8 scalar. It is never Arrow
null. An optional logical field that is absent may be Arrow null only when the
outer field descriptor is nullable.

### Strict inverse order

For a non-null `CANONICAL_JSON_VALUE_UTF8` scalar, perform exactly:

1. require the physical node and scalar to be Arrow UTF-8;
2. recover its exact buffer bytes and strict UTF-8 decode;
3. tokenize JSON while rejecting duplicate keys at every depth, `NaN`,
   `Infinity`, `-Infinity`, and every lexical non-integer JSON number outside
   the tagged decimal string representation;
4. reject surrogates and non-NFC keys or string values recursively;
5. validate the decoded value with
   `TypeAdapter(CanonicalJsonValue).validate_json(..., strict=True)` so the
   discriminator, exact variant fields and strict value types are authoritative;
6. run the same writer on the typed result; and
7. require writer bytes to equal the recovered bytes byte-for-byte.

The logical row projection is the validated value's exact JSON-mode dump. Any
failure is `FormatError` and precedes semantic hashing and Parquet writing.
This ordering rejects noncanonical whitespace, key order, escapes, NFC and
integer spellings even when a permissive parser would produce an equal value.

## Complete validation order

The encoder order is fixed:

1. exact descriptor type and complete recursive invariants;
2. Arrow schema generation solely from that descriptor;
3. exact table type, table/generated-schema equality, non-empty row count, and
   outer non-nullability;
4. exact canonical contract-row parsing, count and uniqueness;
5. parent and primary-key grammar/count/order/uniqueness checks;
6. recursive inverse projection for each physical row, including child
   nullability and the tagged-JSON order above;
7. exact canonical projected-logical-row byte equality to its supplied contract
   row;
8. exact projected primary-key type/value equality;
9. unchanged semantic digest; then and only then
10. unchanged R20 Parquet write controls.

Descriptor/schema/value errors must not call `pq.write_table`.

## Digest and golden-vector preservation

`WyscoutParquetSchemaDescriptor`, its canonical byte format, serializer version
and field rows remain unchanged. It is derived from the generated Arrow schema.
The sole semantic preimage remains exactly:

```text
w04-wyscout-parquet-semantic-v1 || 0x00 || "S" ||
UINT64_BE(len(existing_schema_descriptor_bytes)) || existing_schema_descriptor_bytes ||
"R" || UINT64_BE(row_count) || each UINT64_BE(len(row)) || row ||
"P" || UINT64_BE(parent_count) || each UINT64_BE(len(path)) || UTF8(path)
```

Projection-descriptor bytes, projection-kind tokens and a projection digest are
not inserted. The later accepted root content binds the projection and its exact
generated Arrow schema through the already authorized schema-bundle/build
authority; the logical contract rows remain the semantic row evidence. This is
one digest path, not a parallel semantic digest.

The existing simple identity fixture must still produce exactly:

- schema-descriptor bytes already asserted by the accepted test;
- physical SHA-256
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`;
- semantic SHA-256
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

All Parquet settings, row/parent framing, versions and existing scalar
renderings remain unchanged.

## Exact implementation ownership

The smallest serial implementation packet should own only:

1. `src/scouting/storage/formats.py` — descriptor, schema builder, projection
   writer/inverse and descriptor-led arguments;
2. `tests/unit/test_w04_wyscout_product_formats.py` — existing tests mechanically
   moved to literal identity descriptors plus the focused matrix below;
3. `src/scouting/contracts/wyscout_build.py` — only the mechanical call-site
   shape/readback-field adaptation needed to remove caller-supplied schema
   authority; its existing `GoldSchemaAuthorityUnavailableError` remains the
   terminal behavior until a root descriptor is independently accepted;
4. `tests/contracts/test_w04_wyscout_build_contract.py` — only the corresponding
   static descriptor/readback fixture adaptation and proof that fixture
   inference remains unavailable; and
5. the implementation packet return.

No other source, test, config, authority, verification, data or orchestration
path is needed. If the build call-site cannot remain fail-closed before the
accepted root descriptor exists, stop rather than synthesize a descriptor from
its Gold fixture.

## Focused adversarial matrix

| Case | Required result |
|---|---|
| all seven present tagged variants, including nested mixed array/object | exact writer/inverse/contract-row round trip |
| present tagged JSON null | non-null UTF-8; never Arrow null |
| allowed outer absence vs forbidden non-nullable absence | first maps to outer null; second fails |
| invalid UTF-8; nested duplicate key; invalid constant or float token | fail before typed use/write |
| whitespace, key-order, escape, NFC, surrogate or number-spelling drift | byte-equality failure |
| missing/unknown/wrong discriminator; missing/extra/wrong-typed variant field | strict typed failure |
| tuple omission, addition, rename, reorder, duplicate/gapped position, type/nullability drift | descriptor/schema failure before value projection |
| tuple child null allowed vs forbidden | only exact child nullability passes |
| empty and non-empty homogeneous list | identical descriptor-derived schema and exact round trip |
| list child name/type/nullability/list-kind/fixed-size drift | fail closed |
| schema/field/struct/list metadata, caller schema/callback/digest/Boolean, observed-row inference | rejected or API-unrepresentable |
| existing identity fixture and independent semantic framing | exact accepted bytes and both golden hashes unchanged |
| monkeypatched `pq.write_table` on every malformed family | zero writes |

The focused command is:

```text
uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_build_contract.py
```

The implementer must also run the packet's Ruff and mypy checks through `uv`.
Fresh independent review must inspect both modified modules and independently
reproduce the matrix before master acceptance. Only then may the 23-root
producer resume.

## Residual boundary

Tagged text intentionally makes these heterogeneous raw values opaque to nested
Parquet predicates. That is the explicitly accepted tradeoff. The representation
is deterministic, reversible and evidence-preserving. No architecture expansion
or new dependency is required by this design.

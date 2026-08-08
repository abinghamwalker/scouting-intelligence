# W04 logical-to-Arrow projection implementation independent review R1

- Task: `W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-REVIEW-01-R1`
- Date: 2026-08-01
- Reviewer: fresh independent logical-to-Arrow implementation reviewer
- Verdict: **REWORK**
- Findings: **P0 0 / P1 1 / P2 0**
- Root-schema or product authority created by this review: **NO**

The descriptor-led schema and inverse paths are otherwise bounded and fail
closed, but the public tagged-value writer does not actually enforce its stated
strict typed-input boundary for already-created Pydantic model instances. A
bypassed integer model containing a Boolean is silently serialized as integer
`1`, and that changed meaning can pass the encoder and reach Parquet bytes.
The candidate therefore cannot be accepted or used by the 23-root producer.

## Frozen evidence admission

Every packet-fixed binding was recomputed before analysis and immediately before
this report. All matched exactly:

| Binding | Reproduced SHA-256 |
|---|---|
| review packet | `f4afbf9ae5996e76d79fafb7c8a9744955f4daa5da77ac0c4c6cb2d040500856` |
| authority decision | `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1` |
| authority review | `b864fcf19a72f8680fdc125b1ac92e7674d5edbc853adba45f7b8284efe76f52` |
| authority acceptance | `647ce58093485717a50037eeb6e46d09c2dfad88a8f60bdef7bce8d35f8d31c3` |
| authority master acceptance | `2918b19595297ecfcd029e1f04c2b6be23bcbfcc9b2c79e298222fd389435d86` |
| implementation design | `75cc8ff80cbb3c125a7164499b36c9cf1bad200ea1e8dcf096c019ad1c9adead` |
| R1 implementation packet | `b36793b729561521203ddb507161326340e2a14e73cc5616a59ae2eb18c6b6e5` |
| R2 correction packet | `4cf5c45c460fa275de88b608303e3b601267a6ad8465c2e47eb8bab35e78cf04` |
| R1 producer return | `197bb99e4fe6a6328a709f4af946166429e97aa8fed5858df2b6b954806e8372` |
| R2 producer return | `4f8cde34645c8cc5c9ab19cf05a1c9a3c5b50290615df352e551bda5b8caa934` |
| master candidate verification | `0c7c0a6bbeea40537be5248ece2c8e9f8248156d0adb7b6956f6345e4daceca7` |
| serializer implementation | `d1827127ce36a67dc49993f5cdb4cd18a5ab5bc62f3b753808529f66dba9f2c9` |
| serializer tests | `b5fe5aa5831755abe83cd8fd812538dbfbb091190a42430fb09c9141d7e33cce` |
| build contract | `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16` |
| build-contract tests | `f39e34daac144369444e1701003efdec0c1a97f83ba5fb0beecaf844c21e4692` |
| accepted encoder review | `eb5928d0bc06be4ecbe8317d9d3387e2db5d6d8631d08ac3dacbc45583c5ad9d` |
| accepted encoder master acceptance | `1cfcd5bde3128a7736c75360460e61f73cc9910772d80d5e0b062abb606ce519` |
| accepted build-contract master acceptance | `26026181020650779bd7319c0672abf5dc5e78313fd38a33aff385bcb65c3449` |

## P1 finding: already-created model instances bypass exact typed validation

Location: `src/scouting/storage/formats.py`,
`canonical_json_value_to_w04_arrow_utf8`, lines 648-655 in the reviewed bytes.

The writer calls
`TypeAdapter(CanonicalJsonValue).validate_python(value, strict=True)` and then
serializes the returned model. Pydantic does not revalidate the internal field
state of an already-created model instance by default. Both `model_construct`
and the ordinary public `model_copy(update=...)` method can therefore create an
exact union-member instance whose stored values violate the member's strict
field types. The adapter returns that instance; `model_dump(mode="json")` then
coerces or emits the invalid state.

Independent reproduction through the required root `uv` environment:

```text
uv run python - <<'PY'
from scouting.contracts.wyscout_data import (
    CanonicalJsonArray, CanonicalJsonBoolean, CanonicalJsonInteger
)
from scouting.storage.formats import canonical_json_value_to_w04_arrow_utf8

cases = {
    "integer_bool": CanonicalJsonInteger(value=1).model_copy(update={"value": True}),
    "integer_float": CanonicalJsonInteger(value=1).model_copy(update={"value": 1.0}),
    "boolean_int": CanonicalJsonBoolean(value=True).model_copy(update={"value": 1}),
    "array_dict": CanonicalJsonArray(
        value=(CanonicalJsonInteger(value=1),)
    ).model_copy(update={"value": ({"kind": "integer", "value": 1},)}),
}
for name, value in cases.items():
    print(name, canonical_json_value_to_w04_arrow_utf8(value))
PY
```

Observed exit `0` output:

```text
integer_bool {"kind":"integer","value":1}
integer_float {"kind":"integer","value":1.0}
boolean_int {"kind":"boolean","value":1}
array_dict {"kind":"array","value":[{"kind":"integer","value":1}]}
```

The first case is not only an invalid writer result. The independently composed
descriptor-led encoder accepted the emitted text and the same coerced logical
dump and wrote one Parquet row:

```text
{"malformed_runtime_value_type":"bool",
 "writer_text":"{\"kind\":\"integer\",\"value\":1}",
 "encoder_row_count":1,
 "parquet_size":808,
 "physical_sha256":"644514dc529493293c6e8bbfa61eb185c7ac94218cb2238bfa3260f264e9f8c0"}
```

This violates the accepted requirements
`typed_validation_before_encoding=EXACT_DISCRIMINATED_CANONICAL_JSON_VALUE`,
`EXACT_TAG_AND_CONTENT`, and the no-coercion evidence boundary. A Boolean stored
under the integer variant can be changed into integer `1` before the inverse
ever sees it. The strict inverse remains correct for supplied physical text, but
it cannot recover the pre-writer logical meaning that was already lost.

### Required bounded rework

1. Revalidate the raw runtime state of every present union member and every
   nested member before any Pydantic JSON serialization or coercive dump. An
   already-created instance must not be trusted merely because its class matches
   one union arm.
2. Reject direct and nested bypassed states created through both
   `model_copy(update=...)` and `model_construct`, including Boolean-as-integer,
   float-as-integer, integer-as-Boolean, string-as-integer, list-versus-tuple and
   bare-dict-versus-typed-child substitutions.
3. Add focused tests proving every such case raises `FormatError` before any
   encoder semantic hash or Parquet write. Retain all seven valid variants,
   tagged-null/outer-null distinction, malformed physical inverse cases and the
   two accepted golden digests unchanged.
4. Keep the rework within the serializer and its focused tests. Do not change a
   contract model, root descriptor, logical field, semantic preimage, feature,
   population, dependency, build behavior or product boundary unless a separate
   authority is obtained.

## Independently reproduced non-findings

Apart from the P1 writer-input failure:

- exact dataclass/enum runtime validation, zero-based positional tuple rules,
  list-kind/cardinality rules and recursive metadata absence held;
- six tuple-schema, five list-schema, eight recursive-metadata and eight
  malformed-descriptor/alternate-authority attacks all failed with zero calls to
  `pq.write_table`;
- all seven valid tagged variants round-tripped; present tagged null remained
  non-null UTF-8 and distinct from optional outer Arrow null;
- 18 physical tagged-value attacks covering invalid UTF-8, BOM, nested duplicate
  keys, constants, float/exponent tokens, whitespace, key order, escaping, NFC,
  surrogate, discriminator and typed-field drift failed with zero writes;
- encoder and semantic-helper signatures contain no caller schema, schema role,
  callback, Boolean, digest or alternate-authority parameter;
- the sole semantic preimage independently reproduced the exact physical digest
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
  and semantic digest
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`;
- the forbidden unavailable-schema digest domain/formula is absent; the fixed
  `H1` value is explicitly named `REJECTED_CALLER_GOLD_SEMANTIC_CLAIM` and cannot
  close a receipt;
- `GoldProductReadback` has only contract-row, physical-byte and temporal-proof
  fields, and exact logical readback still terminates with
  `GoldSchemaAuthorityUnavailableError`;
- no runtime root projection descriptor, root schema, schema bundle, W04
  Bronze/Silver/Gold product file, manifest, rebuild output, dependency,
  provider/network access, publication, cloud/container/CI/deployment or Git
  remote was created.

## Required commands and results

- Ruff format: exit `0`, four files already formatted.
- Ruff lint: exit `0`, all checks passed.
- mypy: exit `0`, no issues in four files.
- serializer plus build-contract suite: exit `0`, `135 passed in 3.00s`.
- authority/composability regression suite: exit `0`,
  `179 passed in 3.96s`.
- local-only verifier: exit `0`, PASS `25/25`, zero configured remotes.
- focused build fail-closed probe: exit `0`, `4 passed in 0.15s`.
- independent tagged inverse probe: exit `0`, seven valid variants and 18/18
  malformed inputs, zero malformed writes.
- independent tuple/list/metadata probe: exit `0`, 27/27 attacks, zero writes.
- independent semantic-preimage/golden/API probe: exit `0`, both frozen digests
  reproduced and caller schema authority remained unrepresentable.
- independent constructed/copied-model bypass probe: exit `0`, finding
  reproduced and one coerced row reached Parquet bytes.

## Final decision

`REWORK` with P0/P1/P2 = `0/1/0`. The 23-root producer must remain paused. A
fresh candidate, fresh independent review and separate master acceptance are
required after the exact typed-writer bypass is closed.

```w04-logical-arrow-projection-implementation-independent-review-v1
{"candidate_formats_sha256":"d1827127ce36a67dc49993f5cdb4cd18a5ab5bc62f3b753808529f66dba9f2c9","candidate_formats_test_sha256":"b5fe5aa5831755abe83cd8fd812538dbfbb091190a42430fb09c9141d7e33cce","finding_counts":{"P0":0,"P1":1,"P2":0},"findings":[{"finding_id":"W04-LAP-IMPL-R1-P1-01","severity":"P1","title":"Already-created CanonicalJsonValue models bypass exact typed writer validation"}],"recommendation":"REWORK","review_id":"w04-wyscout-logical-arrow-projection-implementation-independent-review-R1","review_schema_version":"w04-logical-arrow-projection-implementation-independent-review-v1","reviewed_at":"2026-08-01T16:53:23Z","reviewed_by":"ffd51cae-64d4-53de-9b27-e10980aeec22"}
```

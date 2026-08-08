# W04 exact Decimal128-with-exponent independent review — R2

Date: 2026-08-02

Verdict: **PASS**

Finding counts: **P0 0 / P1 0 / P2 0**

This is a fresh independent review of the exact candidate fixed by
`W04-EXACT-DECIMAL128-WITH-EXPONENT-REVIEW-01-R2`. It grants no schema-adoption,
product, checkpoint, or publication authority.

## Fixed candidate and chain of custody

All packet-fixed bindings matched before analysis and again immediately before
this review was rendered:

| Binding | Observed SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `2dfdf3675a47f6c2b53478857de1af27aebecb85def8f0701e6ef86c65fafcc9` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `ba38c5a66f41aee8ef2b998f4622c71ec30f3b8861d7ef07d8540d001b0bee89` |
| R2 producer return | `d06ff314c83c17964e96e6ea877e78187b9c7411d1b1ee12259f4f49b5e2556a` |
| R1 independent review | `137401e9a602d97c59a114c7419f3eb67748cd0ebc04fcbca8259ecc3af36532` |
| R1 reviewer return | `126949bd85d65ca3e6c63fdb461addec10cd0b96a694c97553fc4e1f1bc8ea3c` |

## R1 P1 closure

R1 finding `W04_EXACT_DECIMAL_SIGN_BOOLEAN_NOT_AUTHORITATIVE` is closed. After
no-rounding exponent reconstruction, the implementation clears a reconstructed
zero's incoming sign with `copy_abs()` and applies `copy_negate()` only when
`negative_zero` is true.

A fresh exact-typed fake struct scalar bypassed PyArrow's present zero-sign
normalisation and produced this complete matrix:

| Numeric child | `negative_zero` | Observed logical token | Required token |
| --- | ---: | --- | --- |
| `0E-18` | `false` | `0` | `0` |
| `0E-18` | `true` | `-0` | `-0` |
| `-0E-18` | `false` | `0` | `0` |
| `-0E-18` | `true` | `-0` | `-0` |

All four combinations passed. The Boolean alone now sets the logical zero sign;
the incoming numeric child's sign neither leaks nor toggles it. A true sign flag
on a nonzero remains rejected.

## Retained exactness and fail-closed evidence

- An independently derived 13-value matrix covered both signed capacity edges,
  both signed minimum magnitudes, exponents `-18`, `0`, and `+3`, significant
  trailing zeros, scale-18 values, and four logical signed-zero forms. Every
  forward child retained the source exponent, authoritative zero flag and exact
  `decimal128(22,18)` value. All 13 inverse tokens reproduced their expected
  canonical contract JSON bytes exactly.
- The generated schema was exactly ordered, non-null and metadata-free:
  `record_id: int64`, then `amount: struct<value: decimal128(22,18), exponent:
  int8, negative_zero: bool>`. Parquet readback retained that exact schema.
- Sixteen independent forward attacks rejected non-Decimal/non-finite values,
  false declared scales, source scale 19, five-digit integer capacity, and
  inadmissible positive zero/value exponents. Ten direct inverse attacks rejected
  rounding, nonzero sign claims, out-of-capacity exponents, over-capacity values,
  invalid runtime child values/types, null children, and wrong struct types.
- Ten alternate descriptors rejected child omission/addition/order/name,
  precision/scale/type/nullability and logical-position drift. Eleven physical
  schema attacks rejected outer/child type, name, order, nullability and metadata
  at schema, top-field and child-field boundaries.
- Ten exact-schema inverse and logical-alias attacks rejected rounding, forbidden
  signed-zero/nonzero combinations, exponent capacity failures, trailing-zero and
  signed-zero aliases, wrong logical JSON types, and null children. Instrumented
  semantic-hash calls and Parquet writes both remained exactly `0` across every
  descriptor, physical-schema, metadata, rounding and alias failure.
- Gold `coverage` and `coverage_overall` remain exact UTF-8 scalars with projection
  `CANONICAL_DECIMAL_UTF8`; neither was broadened to the candidate exact struct.
  The semantic version, length-framed schema/row/parent digest preimage, digest
  inputs, and generic serializer signatures remain unchanged. An independent
  preimage recomputation equalled the encoding's semantic SHA-256.

## Packet checks

- `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit `0`; `297 passed in 2.60s`.
- `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit `0`; all checks passed.
- `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit `0`; no issues in 2 source files.
- `uv run bandit -q -r src/scouting/storage/formats.py`
  - initial sandbox exit `2` because the existing uv-cache `.git` path was not
    readable; identical approved read-boundary rerun exit `0`, no findings.
- `uv run lint-imports`
  - initial sandbox exit `2` for the same uv-cache read denial; identical approved
    rerun exit `0`, `3 kept, 0 broken`.
- `uv run python scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25 controls and zero configured remotes.

## Independent probes

- `uv run python -c '<independent exact schema/success/JSON-byte/digest and four-way signed-zero probe>'`
  - exit `0`; 13/13 success vectors, 13/13 strict byte comparisons and all four
    signed-zero combinations passed; exact schema and independent digest matched.
- `uv run python -c '<independent forward, runtime-child, descriptor, physical-schema, metadata, rounding, alias and zero-call attack matrix>'`
  - exit `0`; 16 forward, 10 direct inverse, 10 descriptor, 11 physical-schema/
    metadata, and 10 inverse/alias attacks failed closed; hash calls `0`, writes
    `0`.
- `uv run python -c '<independent coverage, semantic-boundary and generic-serializer preservation probe>'`
  - exit `0`; coverage remained `CANONICAL_DECIMAL_UTF8`; semantic version,
    formula inputs and serializer signatures were unchanged; two unbounded
    canonical Decimal values retained exact no-rounding text.

No P0, P1 or P2 finding was identified within this bounded review. No Git
command, implementation/test edit, dependency/lock change, delegation, provider,
network, cloud, container, hosted-CI, deployment, product, schema-adoption or
publication action occurred.

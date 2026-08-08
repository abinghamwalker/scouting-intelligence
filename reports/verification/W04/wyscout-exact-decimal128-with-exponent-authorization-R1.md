# W04 EXACT_DECIMAL128_WITH_EXPONENT authorization R1

- Date: 2026-08-02
- Master: `/root`
- Decision: `AUTHORIZED_BOUNDED_PHYSICAL_CORRECTION`
- Governing authority: the standing bounded-correction authority dated 2026-08-02

The master authorizes one semantics-preserving logical-to-Arrow projection kind,
`EXACT_DECIMAL128_WITH_EXPONENT`, only for non-coverage logical `Decimal` fields
that were represented by scalar `decimal128(22,18)`. Coverage fields remain on
`CANONICAL_DECIMAL_UTF8`.

The exact physical Arrow value is one ordered, metadata-free struct with non-null
children:

1. `value: decimal128(22,18)`
2. `exponent: int8`
3. `negative_zero: bool`

Outer optionality remains owned only by the logical field. The forward projection
accepts an exact finite built-in `Decimal`, reruns the accepted decimal128(22,18)
capacity and source-scale rule, performs no rounding, copies the exact tuple
exponent, and sets `negative_zero` only for a signed numeric zero. The inverse
requires the exact struct name/type/order/nullability, rejects malformed or null
children and `negative_zero=true` for a nonzero value, reconstructs the exact
exponent with trapping/no-rounding arithmetic, restores signed zero, reruns the
same capacity/source-scale rule, and must reproduce the exact logical JSON bytes
before semantic hashing or Parquet writing.

The adversarial evidence must include scale 0 and 18, positive exponents,
significant trailing zeros, positive and negative zero, decimal capacity edges,
wrong exponent/sign types, malformed child names/order/nullability, null children,
schema metadata, exponent/value combinations that require rounding, out-of-capacity
values, and instrumented proof that invalid inputs reach neither semantic hashing
nor Parquet writing.

This correction changes only physical descriptors and unaccepted derived schema
content/digests. It does not change a logical model, root roster, logical field,
feature, product population, intended output, source/data-rights authority, digest
meaning or formula, dependency, provider/network boundary, service, deployment,
publication or cost.

Frozen inputs at authorization:

- `src/scouting/storage/formats.py`: `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c`
- `tests/unit/test_w04_wyscout_product_formats.py`: `8e68548967293b28e694359509667106951bdc5ba8e1636a541f81f7c3773e1a`
- R5 blocked producer return: `7b85730b07f5cc1bbc26b988538fcca007ce32c99ec4342aac17db7b7fbb856b`

The correction must complete producer, fresh independent review, and master
acceptance before the preserved partial R5 schema closure resumes.

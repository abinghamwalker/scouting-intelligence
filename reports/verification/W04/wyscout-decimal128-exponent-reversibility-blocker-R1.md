# W04 Decimal128 exponent reversibility blocker R1

- Date: 2026-08-01
- Master: `/root`
- Status: `BLOCKED_USER_AUTHORIZATION_REQUIRED`
- Trigger: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R5`

## Confirmed contradiction

The frozen logical contract admits finite Decimal values at lexical/source scales `0..18`. The accepted Arrow projection maps the non-coverage Decimal fields to scalar `decimal128(22,18)` and requires exact inverse contract-row byte equality.

A strict-valid SilverAction with:

```text
period_elapsed_seconds = Decimal("10")
event_sec_source_scale = 0
```

is read back by PyArrow as:

```text
Decimal("10.000000000000000000")
```

The canonical logical row contains string token `"10"`; the projected Arrow row contains `"10.000000000000000000"`. `encode_w04_wyscout_product_parquet` therefore correctly fails before semantic hashing/writing with `FormatError: Arrow row 0 does not exactly equal its contract row`.

The master reproduced this independently with a descriptor-only probe. The R5 producer reproduced it in the exact 29-row matrix: `27 passed, 1 failed`. Static formatting, lint and typing pass; its 56-binding AST audit reports zero direct-field omissions.

The loss is broader than trailing scale. A direct PyArrow probe shows that scalar `decimal128(22,18)` normalizes all of `0`, `-0`, `0.00`, `-0.00`, `10`, `10.0` and `10.00` to exponent `-18`, and it loses negative zero. Pydantic JSON-mode Decimal serialization preserves those distinctions. Positive Decimal exponents such as `1E+3` are another lexical state not recoverable from the fixed-scale value alone.

## Why the in-scope shortcuts are rejected

- Treating the scale-0 action as logical-validation-only would violate the frozen requirement that all 29 rows pass descriptor-led inverse equality.
- Comparing Decimal values numerically would allow physical bytes that cannot reproduce the semantic contract-row bytes and would weaken strict inverse evidence.
- Normalizing every logical Decimal to scale 18 would change the logical contract and source-fidelity semantics.
- Moving these values to plain UTF-8 would contradict the instruction to retain `decimal128(22,18)` for event seconds, coordinates and possession-order positions.

## Recommended bounded correction

Authorize one additive logical-to-Arrow projection kind, provisionally named `EXACT_DECIMAL128_WITH_EXPONENT`, only for non-coverage logical Decimal fields currently mapped to scalar `decimal128(22,18)`.

Its physical Arrow value is an exact ordered non-null struct:

1. `value`: `decimal128(22,18)`, preserving the queryable numeric value;
2. `exponent`: `int8`, preserving the exact logical Decimal exponent;
3. `negative_zero`: `bool`, preserving the sign only when the numeric value is zero.

Outer optionality remains owned by the logical field; no child uses Arrow null as logical state. Metadata remains absent.

Forward projection must require an exact finite Decimal satisfying the existing decimal128 capacity rules, write its numeric value without rounding, copy its exact exponent, and set `negative_zero` exactly from the Decimal tuple.

Inverse decoding must:

1. require the exact struct name/type/order/nullability;
2. require finite `decimal128(22,18)`, exact `int8` exponent, and exact Boolean sign state;
3. reject a nonzero value with `negative_zero=true`;
4. reconstruct the exact Decimal exponent with a trapping, no-rounding quantize and restore negative zero;
5. rerun the existing decimal capacity/source-scale rules; and
6. require exact byte equality with the Pydantic JSON-mode logical Decimal token before semantic hashing or Parquet writing.

This keeps coverage fields on the already accepted `CANONICAL_DECIMAL_UTF8` path. It keeps `decimal128(22,18)` as the numeric physical child for event seconds, coordinates and possession-order Decimal positions. It adds no logical model, root, logical field, feature, population, dependency, provider, service or deployment.

The correction necessarily changes the affected Arrow schema descriptors and therefore the affected canonical root-content bytes/digests and future physical Parquet schemas. No schema aggregate or W04 product has yet been accepted/materialized, so no product history would be rewritten. The semantic digest formula/path remains unchanged.

## Required loop if authorized

1. freeze a bounded projection design authority and adversarial vectors, including scale 0/18, positive exponent, trailing zeros, signed zero, capacity edges, malformed exponent/sign, rounding attempts, schema drift and zero-write failures;
2. separate implementation by a bounded producer;
3. fresh report-only independent review;
4. master acceptance and complete repository gate;
5. resume the preserved partial R5 schema correction and its fresh review.

No aggregate, Bronze/Silver/Gold product, provider access, Git operation, dependency, network, cloud, container, CI, publication or deployment work may resume before those gates pass.

## Frozen evidence

| Artifact | SHA-256 |
|---|---|
| accepted storage implementation | `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c` |
| R5 blocked producer return | `7b85730b07f5cc1bbc26b988538fcca007ce32c99ec4342aac17db7b7fbb856b` |
| partial R5 schema | `e86d8de760c545e14ddb46b4de216fdc94cefea8c5d2e745fd4e10b0b1ab0e1b` |
| partial R5 schema test | `7133e736c80af8c6f60ae31e78bbe3c5611f1eaa92ed7716a9bac9cbbb8cda40` |
| independent R5 oracle | `a3f15f92a14ff342efd0f5b2848b60eab4898ea79eb69c7fd6f09e6946077efa` |
| oracle return | `b09297fb45eb7a16f431959f7e7840b8ae930902928094079fd7e26b1ba79116` |

The existing local-only verifier remains PASS with zero remotes.

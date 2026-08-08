# W04 canonical Decimal Arrow projection authorization R1

Date: 2026-08-01

State: **AUTHORIZED — BOUNDED ADDITIVE CORRECTION**

## Trigger

This authority closes only P1-03 in the preserved failed R2 schema-closure
verification while returning P1-01, P1-02 and P1-04 to the same bounded R3 producer
rework. The failed R2 implementation and review evidence remain immutable evidence.

Bound master finding:
`reports/verification/W04/wyscout-23-root-schema-closure-R2-master-verification.md`
with SHA-256
`9c5092ccf75e4a77ebdb7079a1a3b4360b8b96e52823189355a1cd8e7953a76d`.

## Authorized correction

Add exactly one descriptor-owned logical-to-Arrow projection kind,
`CANONICAL_DECIMAL_UTF8`, and use it only for these logical model fields wherever
they occur in an accepted root descriptor:

1. `GoldCoverageDimension.coverage`
2. `GoldCoverage.coverage_overall`

For a present value, the Arrow UTF-8 scalar is the exact canonical finite Decimal
token already defined by the frozen logical contract: normalize every signed zero
to `0`; otherwise render fixed-point without exponent notation and remove redundant
trailing fractional zeros and a now-empty decimal point. The operation performs no
rounding and appends no terminal LF. The encoded value itself may not use Arrow null;
outer field optionality remains the sole null authority.

Inverse decoding must accept an exact UTF-8 string, strict-parse it directly to
`Decimal`, reject non-finite values, canonically re-encode it and require byte-for-byte
equality. Whitespace, a BOM, exponent aliases, leading plus, redundant integer or
fractional zeroes, signed zero, and any other non-canonical spelling fail closed.

Every other Decimal projection remains `decimal128(22,18)`, including action event
seconds, coordinates, and the Decimal position in possession/action order tuples.

## R3 acceptance boundary

The R3 producer must also correct all other preserved R2 P1 findings:

- predicate operands must resolve to their owning runtime fields or be explicitly
  classified as external/composed authority operands;
- exact frozen constants must replace labels, counts, placeholders and conceptual
  names wherever the predicate claims executable equality;
- tests must reproduce those operands and constants and execute descriptor-led
  forward/inverse equality for all twelve Parquet roots; and
- serialization tests must prove the exact two-field Decimal exception and the
  unchanged `decimal128(22,18)` treatment everywhere else.

## Prohibitions

This authorization changes no logical contract, root, field, semantic digest,
feature, population, dependency, source/provider access, publication or deployment.
It does not authorize rounding, quantization, a new schema root, a second schema or
semantic authority, product bytes, aggregates, cloud, containers, CI, network access,
dependency changes or Git operations by a subagent.

Fresh independent review and master acceptance are mandatory before aggregate or
product implementation resumes. If these requirements cannot be met inside this
boundary, work stops for user authorization rather than widening the correction.

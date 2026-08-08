# W04 23-root schema readiness blocker R1 master verification

Date: 2026-08-01

Verdict: `BLOCKED_BOUNDED_REPRESENTATION_AUTHORITY_REQUIRED`

The master inspected the complete readiness audit and independently reproduced its
executable blocker. All exact 23 required runtime root models exist. Roots 1–12 are
Parquet product roots; roots 13–23 are JSON-only.

The product contracts include recursive discriminated `CanonicalJsonValue` values
in all three Bronze roots and heterogeneous fixed tuples including possession order
keys and Gold player-match keys. These logical values cannot all be represented by
the current direct homogeneous Arrow mapping without a separately chosen reversible
projection.

An in-memory uv/PyArrow probe reproduced both boundaries:

- the accepted W04 format validator rejects a dense Arrow union with
  `FormatError: Arrow field 'canonical_json_value' has unsupported type ...`;
- PyArrow Parquet rejects the same union with
  `ArrowNotImplementedError: Unhandled type for Arrow to Parquet schema conversion`.

Fixture inference, observed-value narrowing, empty-list inference, or a caller-
selected schema would contradict the accepted R20/R21/R2 exact implemented-schema
rules. Freezing canonical JSON text or tagged structs without authorization would
instead invent a new serializer representation rule and change the accepted
`src/scouting/storage/formats.py` authority.

The smallest proposed correction is one additive schema-aware projection in the
sole existing W04 serializer path:

1. recursive/dynamic logical JSON projects to a non-null UTF-8 value containing
   its exact R20-canonical tagged logical JSON bytes, with no LF; inverse decoding
   must strict-parse, typed-validate, re-encode and require byte equality;
2. a heterogeneous fixed tuple projects to a non-null ordered Arrow struct with
   exact per-position child type/nullability and canonical positional field names;
   inverse decoding restores the exact ordered logical tuple;
3. homogeneous sequences retain the ordinary Arrow list mapping;
4. semantic hashing remains the sole accepted schema descriptor plus exact logical
   contract-row bytes and parent paths; the projection creates no second semantic
   digest or root.

This proposal changes no root roster, logical field, feature, population, provider,
dependency, project root, rights, local-only boundary, cloud/container/CI/deployment
state, or publication permission. It does require fresh user authorization because
it additively changes the frozen serializer authority before the 23-root schema
producer can truthfully emit executable schema content.

Evidence:

- readiness audit SHA-256:
  `f9961082a27b949da6b9c1647b50f9ce18b6862c66fb8c104826c4b20ca746a0`;
- readiness return SHA-256:
  `227801dd267622b2d4fae868d4e1f6648d4c35ada3f9b9aac9edc4b34e3e9819`;
- Git remotes remain empty and no implementation/schema/aggregate/product byte was
  created by the audit or this verification.

# W04 logical-to-Arrow projection authorization R1

Authorized at: `2026-08-01T15:44:40Z`

Status: `USER_AUTHORIZED_BOUNDED_ADDITIVE_CORRECTION`

The user explicitly authorizes one additive logical-to-Arrow representation rule
as the serial prerequisite to the exact 23-root implemented-schema closure.

The authority must freeze all of the following:

1. A present `CanonicalJsonValue` is typed-validated and dumped in JSON mode, then
   encoded as exact R20-canonical tagged logical JSON bytes with no terminal LF.
   Those bytes are strict UTF-8-decoded into one Arrow UTF-8 scalar.
2. Inverse decoding recovers the strict UTF-8 bytes, rejects duplicate object keys
   at every depth and non-JSON constants, validates the exact discriminated
   `CanonicalJsonValue` type, R20-canonical re-encodes it without LF, and requires
   byte-for-byte equality with the recovered bytes.
3. Outer logical optionality remains authoritative. An absent/outer-null optional
   value may use Arrow null only when the accepted logical field permits it. The
   `CanonicalJsonNull` variant is a present tagged logical value and must encode as
   a non-null UTF-8 scalar; Arrow null may never stand for canonical JSON null.
4. Every heterogeneous fixed tuple projects to an ordered positional Arrow struct.
   Its accepted descriptor contains every child's exact name, logical position,
   physical type, order and nullability. Serialization and inverse decoding require
   exact descriptor/struct equality and restore the exact logical tuple order.
5. Every homogeneous variable or fixed sequence projects to an Arrow list with the
   exact descriptor-owned child type/name/nullability. No observed value, empty
   sequence or fixture may determine its schema.
6. All recursive Arrow schema generation consumes only the independently accepted
   canonical descriptor content. Row, fixture, caller and observed-value inference
   are forbidden. A caller callback, Boolean, digest, alternate descriptor or
   equivalent-looking object cannot create accepted authority.
7. The existing W04 semantic digest derivation remains the sole derivation: exact
   physical Arrow schema descriptor, exact ordered logical contract-row bytes and
   exact ordered parent paths under the unchanged semantic version/preimage. The
   projection adds no digest, root or second semantic path.

Implementation and independent review must cover canonical JSON null versus outer
Arrow null, nested duplicate keys, invalid constants, invalid UTF-8, noncanonical
whitespace/key order/NFC/number forms, wrong discriminator, tagged-content drift,
tuple child omission/addition/reordering/renaming/type/nullability drift, homogeneous
empty and non-empty sequences, round-trip equality, schema derivation provenance,
and unchanged existing deterministic encoder vectors.

This authorization changes no schema root, logical field, logical semantics,
feature, population, dependency, provider access, rights, project root, local-only
boundary, product/publication permission, cloud/container/hosted-CI/deployment
state, or aggregate/build projection. It authorizes no 23-root schema byte or v2
digest before this correction receives its own fresh independent review and master
acceptance.

Controlling evidence retained unchanged:

- readiness audit:
  `f9961082a27b949da6b9c1647b50f9ce18b6862c66fb8c104826c4b20ca746a0`;
- readiness return:
  `227801dd267622b2d4fae868d4e1f6648d4c35ada3f9b9aac9edc4b34e3e9819`;
- master blocker verification:
  `d33eedb889c3b916e509a27d9a3383862793b16002639cf559ebe0f2fbc1af71`;
- accepted W04 Parquet encoder:
  `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4`.

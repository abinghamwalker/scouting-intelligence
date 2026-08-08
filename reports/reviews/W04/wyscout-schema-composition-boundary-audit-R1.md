# W04 Wyscout schema-composition boundary audit R1

Date: 2026-08-01

Task: `W04-WYSCOUT-SCHEMA-COMPOSITION-BOUNDARY-AUDIT-01`

Status: **bounded independent advisory audit**

Classification: **COMPOSITION_WITHIN_APPROVED_CHAIN — NO USER CLARIFICATION REQUIRED**

## Scope and independence

This audit determines only the smallest authority-preserving boundary by which W04
receipt closure can require the accepted canonical Gold Arrow schema identity. It
does not implement or approve a schema, change a frozen authority, create a digest,
write a product, or authorize publication. The auditor did not produce the R3 build
candidate, did not delegate, performed no Git operation, and changed only this
report and its required return.

## Fixed bindings

Every packet-fixed binding reproduced exactly before analysis:

| Artifact | Required and observed SHA-256 | Result |
| --- | --- | --- |
| audit packet | `a4b8630c42d8b3c48b4a4ded2e320cb42339730135f442250d9182dc3fa4a367` | PASS |
| R3 build contract | `ea0a5f4cd474a081d97b529e3ecf87f0e3852dccef0041f712544420c85d55fd` | PASS |
| R3 build tests | `c153c7a41120a88128301b18f6ee50f1721d0c65431eed1cc8136b5761d9d040` | PASS |
| R3 producer return | `dd50227ed1c9ab6fa8f21603a015a1d12a7a15f73da0fccadb6467a9ea38fb54` | PASS |
| R4 build/receipt audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` | PASS |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | PASS |
| R21 correction | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | PASS |

No fixed binding drifted.

## Authority trace and acceptance point

The frozen authority has two deliberately different schema nodes:

1. R21 Section 8 defines the v1 schema-bundle preimage as descriptor-only. Every
   descriptor carries
   `CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`, and R21 expressly
   forbids treating it as proof that a row schema or serializer exists. Its Gold
   descriptor therefore cannot establish Arrow field order, types, nested types,
   or nullability.
2. R2 Section 7.1 defines the later v2 implemented-schema bundle. The exact 23-root
   roster includes `GOLD_PLAYER_WINDOW`. Its row becomes usable only after the
   owning implementation has exported the complete canonical schema bytes and a
   fresh independent review has accepted the exact roster and content digests.
3. R2 Section 7.2 then materializes product-contract v2 from the accepted v2 schema
   bundle. R20's unchanged 25-key projection subsequently binds both accepted
   aggregate digests.
4. R2 Section 9 fixes the serial order: build-contract implementation and review;
   implemented-schema closure; v2 aggregate materialization and review; runtime
   admission/launcher; then rebuild and receipt publication. R3 Sections 3–6 and
   R4 Sections 3–6 apply at that later publication/readback composition point.

Consequently, exact Gold Arrow schema identity becomes accepted only at the planned
implemented-schema/aggregate gates. It is not fully derivable from an already
accepted implementation authority available to the current R3 build packet.

## Executable evidence from the frozen candidate

The current code confirms the authority gap rather than closing it:

- `GoldPlayerWindow` is the accepted typed JSON semantic row contract, but it does
  not define an Arrow schema descriptor or canonical Arrow nullability.
- `encode_w04_wyscout_product_parquet` validates that a supplied Arrow table equals
  a supplied Arrow schema and includes that supplied descriptor in its semantic
  digest. It intentionally accepts any supported explicit schema; it does not
  compare the descriptor with an accepted `GOLD_PLAYER_WINDOW` schema authority.
- `GoldProductReadback` therefore carries caller-selected `table` and `schema`
  values. `_validate_gold_product_readback` re-encodes those mutually consistent
  values but does not bind their schema descriptor to an accepted v2 schema row.
- The positive fixture constructs its Arrow schema by inspecting the one row and
  setting top-level nullability from whether that fixture value is null. That is a
  fixture-derived schema choice, not accepted canonical schema authority.
- The projection's `schema_bundle_digest` proves that a future aggregate identity
  is required, but receipt closure currently neither receives nor reopens the
  accepted bundle content and cannot map that digest to the supplied Arrow schema.

Thus a coherent alternate supported Arrow schema, including changed field
nullability with correspondingly re-encoded Parquet and rehashed downstream
claims, is not excluded by the current composition seam. Rehashing proves internal
consistency under the caller's schema; it does not prove canonical schema identity.

## Bounded option assessment

### 1. Direct exact-schema validator in the current build module

**Reject as the present authority boundary.** Hard-coding a complete Gold Arrow
schema in the build module before the 23-root owner/export/review gate would create
a second schema authority or pre-accept schema bytes. Deriving it from one row or
from Pydantic values would also be a second derivation and would not reproduce the
later canonical schema closure by authority. This option becomes valid only if it
delegates to the later accepted `GOLD_PLAYER_WINDOW` schema owner; at that point it
is no longer an independent current-module authority.

### 2. Callback or content input sourced from later schema authority

**Conditionally valid only as later composition.** An arbitrary callback, Boolean,
schema object, descriptor, or digest supplied by the caller remains caller
self-authorization. A valid composition input must be obtainable only from the
accepted implemented-schema authority and must content-bind the exact canonical
Gold schema identity and concrete Arrow schema. This must reuse the existing
`GOLD_PLAYER_WINDOW` root and accepted schema-bundle digest; it must not add an
attestation root, second schema, placeholder digest, or projection key.

### 3. Defer receipt-closure executability until schema authority exists

**Accept and recommend.** Packet 1 may define and independently review the
build/window/receipt/result contracts, but the Gold receipt-closure success path
must remain explicitly unavailable or fail closed at the schema seam. After the
23-root schema packet exports and independently accepts the exact
`GOLD_PLAYER_WINDOW` canonical schema, and after the existing v2 schema/product
aggregates are materialized, the later composition step may bind that accepted
schema content to the supplied Arrow table before any receipt can claim
`COMPLETE`.

This does not reorder the frozen chain. It enforces the order already stated by R2
Section 9 and preserves R3/R4's later readback semantics. Packet 1 precedes Packet
2 as approved; Packet 1 simply cannot independently claim the Packet-2 authority.

## Minimal authority-preserving boundary

The smallest safe boundary is:

```text
Packet 1 build-contract implementation
  -> contract models and non-schema validations available
  -> Gold receipt-closure success unavailable without accepted schema authority

Packet 2 exact 23-root implemented-schema closure
  -> canonical GOLD_PLAYER_WINDOW schema bytes exported
  -> exact schema content independently accepted

master-only v2 aggregate materialization
  -> accepted schema_bundle_digest
  -> accepted product_contract_digest

later runtime/publication composition
  -> concrete Gold Arrow schema equals accepted Gold root content
  -> projection aggregate digests equal accepted aggregates
  -> only then may R3/R4 receipt closure return success
```

The later composition may use a direct import from the accepted schema owner or a
content-bound authority value produced by it. The implementation choice must not
permit a general caller to manufacture an equivalent-looking authority. No exact
schema bytes, schema digest, or new adapter schema should be invented in the R3
correction.

## Classification and downstream instruction

This is **composition within the already approved chain**, not a frozen
architecture or sequencing change. No user clarification is required because:

- the 23-root closure, aggregate order, unchanged 25-key projection, and later
  publication position are already frozen by R2;
- no root, field, dependency, feature, writer, product population, or projection
  key changes;
- deferral prevents early authority rather than moving a gate; and
- publication was already prohibited before schema and aggregate acceptance.

The current R3 candidate must not be accepted as a complete executable receipt
closure while its caller-selected Arrow schema remains unbound. The bounded rework
is to make the seam fail closed/deferred, then let the planned schema and aggregate
packets supply the existing accepted authority before runtime or publication.

## Stop boundary

Stop and return for user clarification only if implementing this composition
requires changing the 23-root roster, the v2 materialization order, the 25-key
projection, product population, schema ownership, a dependency, or another frozen
architecture/local-only boundary. No such change is required by this audit.


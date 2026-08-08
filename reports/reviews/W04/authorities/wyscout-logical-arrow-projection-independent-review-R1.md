# W04 logical-to-Arrow projection independent authority review R1

- Task: `W04-LOGICAL-ARROW-PROJECTION-REVIEW-01-R1`
- Date: 2026-08-01
- Reviewer: fresh independent logical-to-Arrow authority reviewer
- Verdict: **PASS**
- Findings: **P0 0 / P1 0 / P2 0**
- Product or schema permission created by this review: **NO**

The exact authority is sound, bounded, reversible, and ready for separate master
acceptance. It freezes a representation contract only. It creates no implemented
descriptor, root schema, serializer, Parquet byte, product byte, or publication
authority.

## Frozen evidence admission

Every packet-fixed binding was recomputed before analysis and matched exactly:

| Binding | Reproduced SHA-256 |
|---|---|
| authorization | `eeb28f62b631b70e6c7046f3e8a6cdba74c1a7a4996c7024e98c471b08b8dd69` |
| decision packet | `691c3e103222ffe265cc772e8bbb072b97ea99cf47f5701b48e7cee897e9917a` |
| canonical decision | `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1` |
| authority test | `39406164139b1c016b67ab14289c93a41e0a69b1da6a1b85a0ad818732fc0750` |
| producer return | `b370980c7360fc79fd0dc896b21a0d335a5a6b33bb26cc9788aedb831fddf887` |
| master decision verification | `f8fd59d0267b86db2df752f3f2ccd390b35d72d1438056602752c7033d0a5433` |
| implementation design | `75cc8ff80cbb3c125a7164499b36c9cf1bad200ea1e8dcf096c019ad1c9adead` |
| implementation-design return | `e7d2448efa715ea699ada619ce2213141cbf8bf28150aaa8daf2226225379d80` |
| 23-root readiness audit | `f9961082a27b949da6b9c1647b50f9ce18b6862c66fb8c104826c4b20ca746a0` |
| R20 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| accepted encoder | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` |
| accepted encoder tests | `c0afb390ef44f19d4759b62495bc0125a14fb80ac0f1e4376972a798702e3a9f` |
| accepted encoder review | `eb5928d0bc06be4ecbe8317d9d3387e2db5d6d8631d08ac3dacbc45583c5ad9d` |
| accepted encoder master acceptance | `1cfcd5bde3128a7736c75360460e61f73cc9910772d80d5e0b062abb606ce519` |
| accepted build-contract master acceptance | `26026181020650779bd7319c0672abf5dc5e78313fd38a33aff385bcb65c3449` |

The decision strict-loaded as one R20-canonical JSON object plus exactly one
terminal LF, re-encoded byte-for-byte, measured 7,985 bytes, and reproduced the
fixed decision digest. Its nine bound evidence files also reproduce their frozen
digests.

## Exact authorization comparison

The decision matches every material rule in the user's authorization:

1. A present `CanonicalJsonValue` is exact tagged logical JSON in strict Arrow
   UTF-8. Typed validation precedes encoding, R20 canonicalization applies, and
   the encoded scalar has no terminal LF.
2. The inverse requires a non-null UTF-8 scalar, recovers strict UTF-8 bytes,
   rejects duplicate JSON keys at every depth and invalid constants, validates
   the exact discriminated logical union, canonical re-encodes, and requires
   byte-for-byte equality. The final equality closes whitespace, key-order,
   escape, NFC, numeric-spelling, discriminator, and tagged-content aliases.
3. Outer optionality alone controls Arrow null. The present logical null variant
   is the non-null text `{"kind":"null","value":null}`; the untagged Arrow-null
   representation is forbidden for that value.
4. A heterogeneous fixed tuple is an ordered positional struct. The accepted
   descriptor owns each child's `name`, zero-based contiguous
   `logical_position`, `physical_type`, order, and `nullable` value. Exact arity,
   schema equality, recursive child decoding, and tuple restoration are required.
5. A homogeneous variable or fixed sequence is a descriptor-owned Arrow list.
   The one child name, recursive physical type, nullability, sequence order, and
   any fixed cardinality come from the descriptor. Empty and non-empty values
   cannot select different schemas.
6. Recursive schema generation has one source: independently reviewed and
   master-accepted canonical descriptor content. Row, fixture, observed-value,
   empty-sequence, caller schema, callback, Boolean, digest, alternate descriptor,
   and equivalent-looking-object authority are all expressly denied.

The decision's lifecycle remains
`AUTHORITY_ONLY_NO_SCHEMA_OR_PRODUCT_BYTES`. Its ordered progression requires a
fresh authority review and master acceptance, then a separate serializer
implementation, fresh serializer review, and master serializer acceptance before
the 23-root producer resumes.

## Adversarial serialization review

An independent reference probe exercised all seven current tagged variants: null,
Boolean, integer, number, string, array, and object. Every canonical value
round-tripped under strict typed validation and exact re-encoding without an LF.
The present tagged null reproduced exactly as a non-null string. Untagged JSON
null and Boolean-as-integer failed typed validation.

A second inverse probe rejected invalid UTF-8, top-level and nested duplicate
keys, `NaN`, a JSON float token, noncanonical whitespace, reversed key order,
decomposed Unicode, and an unknown discriminator. These results confirm that the
authority's parse/typed-validation/re-encoding sequence is sufficient without a
lossy intermediate or permissive alias.

Tuple omission, addition, reordering, renaming, type drift, nullability drift,
duplicate or gapped positions, and logical arity drift are all excluded by the
combined descriptor and exact-schema rules. List child drift, list-cardinality
drift, and empty-value inference are likewise excluded. Arrow union authority is
expressly prohibited; tagged UTF-8 therefore remains the only authorized
representation for the heterogeneous recursive value.

The report-only implementation design is consistent with these rules but is not
itself authority. Its literal synthetic descriptors are confined to mechanism
tests and cannot authorize a W04 root. Any later product path must parse and bind
the exact separately accepted root descriptor content.

## Semantic digest and scope review

The sole semantic domain remains `w04-wyscout-parquet-semantic-v1`. The exact
framed preimage remains the existing schema-descriptor bytes, ordered unique
canonical logical contract rows, and ordered parent paths with their existing
markers, counts, and `UINT64_BE` length frames. The projection can change only the
already-existing physical schema descriptor input. It adds no field, version,
preimage component, projection digest, second formula, or second derivation.

The accepted identity fixture remains bound to physical digest
`889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
and semantic digest
`6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.
The focused suite reproduced both through the unchanged accepted encoder tests.

The authority changes no root, logical field, logical semantics, feature,
population, dependency, provider/right/access state, product/publication state,
project root, dependency/lock policy, cloud, container, hosted CI, endpoint,
deployment, or Git remote. The local-only verifier passed all 25 controls with
zero configured remotes.

## Test-quality and progression review

The authority test strict-loads and byte-reproduces the immutable decision,
validates the complete ordered rule objects, checks all bound evidence digests,
and fails representative canonical-byte and rule mutations. It binds no mutable
implementation hash, schema/product byte, or permanent absence of a future
separately authorized product path. It is therefore progression-safe.

Required checks all passed:

- Ruff format, Ruff lint, and mypy: pass;
- authority, R21 composability, and accepted encoder suite: `187 passed in 5.87s`;
- local-only verifier: `PASS`, 25/25 controls;
- independent canonical reproduction: pass, 7,985 bytes and exact decision hash;
- seven-variant tagged-value probe: pass;
- strict inverse malformed-input probe: 9/9 rejected.

## Final decision

`PASS` with no P0, P1, or P2 finding. This verdict recommends only master
acceptance of the exact authority decision. Serializer implementation and the
23-root producer remain separately gated.

```w04-logical-arrow-projection-authority-independent-review-v1
{"decision_id":"w04-wyscout-logical-arrow-projection-decisions-v1","decision_physical_sha256":"460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1","findings":[],"recommendation":"PASS","review_id":"w04-wyscout-logical-arrow-projection-independent-review-R1","review_schema_version":"w04-logical-arrow-projection-authority-independent-review-v1","reviewed_at":"2026-08-01T16:06:00Z","reviewed_by":"8681103d-9bc8-518c-abfb-161d1b05ccac"}
```

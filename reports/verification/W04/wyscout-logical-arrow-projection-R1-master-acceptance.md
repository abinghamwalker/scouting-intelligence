# W04 logical-to-Arrow projection R1 — master acceptance

Date: 2026-08-01

Decision: `ACCEPTED_BOUNDED_SERIALIZATION_AUTHORITY_IMPLEMENTATION_GATES_REQUIRED`

The master accepts the exact additive logical-to-Arrow representation authority
after fresh independent review and independent master reproduction. This accepts
no root descriptor, schema byte, product byte, semantic change, feature,
population, dependency, provider access, publication, deployment, cloud,
container, hosted CI, endpoint, or Git remote.

## Accepted chain

- user authorization:
  `eeb28f62b631b70e6c7046f3e8a6cdba74c1a7a4996c7024e98c471b08b8dd69`;
- decision packet:
  `691c3e103222ffe265cc772e8bbb072b97ea99cf47f5701b48e7cee897e9917a`;
- canonical decision:
  `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1`;
- progression-safe authority test:
  `39406164139b1c016b67ab14289c93a41e0a69b1da6a1b85a0ad818732fc0750`;
- producer return:
  `b370980c7360fc79fd0dc896b21a0d335a5a6b33bb26cc9788aedb831fddf887`;
- decision master verification:
  `f8fd59d0267b86db2df752f3f2ccd390b35d72d1438056602752c7033d0a5433`;
- report-only implementation design and return:
  `75cc8ff80cbb3c125a7164499b36c9cf1bad200ea1e8dcf096c019ad1c9adead` /
  `e7d2448efa715ea699ada619ce2213141cbf8bf28150aaa8daf2226225379d80`;
- independent review packet:
  `59196da67c9d10f4504e0399795f96b05453a7c177396ba9023f000dbed1dded`;
- independent PASS review and its canonical embedded record:
  `b864fcf19a72f8680fdc125b1ac92e7674d5edbc853adba45f7b8284efe76f52` /
  `121fb8c856bc9b31054171d445197f0ba25e6b138fa7198325b2f4fa679a91e7`;
- independent reviewer return:
  `e8a3c17f5ecb734759490eeeb39cea3a751d7ac27c3251d1ffdac74c8e0934db`;
- canonical acceptance:
  `647ce58093485717a50037eeb6e46d09c2dfad88a8f60bdef7bce8d35f8d31c3`.

## Master acceptance basis

- Complete review readback: PASS with P0/P1/P2 = `0/0/0`.
- All review-packet fixed bindings reproduced without drift.
- Review fence strict extraction and canonical record digest: PASS.
- Ruff format, Ruff lint, and mypy: PASS.
- Authority, R21 composability, and accepted encoder suite: `187 passed`.
- Local-only verifier: PASS, 25/25; `git remote -v` emitted nothing.
- Exact accepted physical identity digest remains
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`.
- Exact accepted semantic identity digest remains
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

## Accepted serialization boundary

- Present `CanonicalJsonValue` is exact R20-canonical tagged logical JSON in one
  non-null Arrow UTF-8 scalar without a terminal LF.
- The inverse requires strict UTF-8, duplicate-key and invalid-constant
  rejection, exact discriminated typed validation, canonical re-encoding, and
  byte-for-byte equality.
- Only outer accepted optionality may use Arrow null. Present canonical JSON null
  is the non-null tagged UTF-8 value.
- Heterogeneous fixed tuples are exact descriptor-owned ordered positional
  structs; homogeneous sequences are exact descriptor-owned Arrow lists.
- Schema generation has exactly one authority source: independently reviewed and
  master-accepted descriptor content. Row, fixture, observed-value,
  empty-sequence, caller schema/callback/Boolean/digest, alternate descriptor, or
  equivalent-looking-object inference is forbidden.
- The sole `w04-wyscout-parquet-semantic-v1` preimage and derivation remain
  unchanged. The correction can affect only the existing physical schema
  descriptor input and adds no new digest path.

## Progression decision

The bounded serializer implementation may now be dispatched under separate path
ownership. It must receive fresh independent implementation review and master
acceptance before the 23-root schema producer resumes. This authority acceptance
alone grants no schema or product implementation permission beyond that exact
serializer correction.

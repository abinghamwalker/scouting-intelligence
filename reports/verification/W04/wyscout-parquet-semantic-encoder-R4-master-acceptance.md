# W04 Parquet semantic encoder R4 master acceptance

Date: 2026-08-01

Decision: `ACCEPT`

The master accepts the exact R4 deterministic W04 Parquet encoder for bounded
downstream serializer use. R1-R3 and their failed reviews remain retained evidence.

## Accepted evidence

- implementation: `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4`
- tests: `c0afb390ef44f19d4759b62495bc0125a14fb80ac0f1e4376972a798702e3a9f`
- producer return: `b043cc215a3df053152798e46b1e2e819bdc36473da45a623b5439c90adb810b`
- independent review: `eb5928d0bc06be4ecbe8317d9d3387e2db5d6d8631d08ac3dacbc45583c5ad9d`
- reviewer return: `8a0164fd35865d9c094552a515005a6c93c495cbdf4a4736d260492b5bf4ace8`
- physical vector: `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- semantic vector: `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`

## Basis

- Master inspection and reproduction passed 81 combined encoder/guarded-storage
  tests, 14 direct R4 probes and every focused static, type, import, security,
  local-only, fixed-hash, diff and zero-remote check.
- Fresh independent review passed with `P0=0`, `P1=0`, `P2=0`. It rejected all
  36 empty/non-empty recursive metadata variants before any digest or writer call.
- The review independently reproduced all R1-R3 row/key/type, descriptor/helper,
  recursive schema/value, framing, fixed-vector, physical-control and row-group
  guarantees.
- Metadata must be absent (`None`) at schema, top-field, struct-child and every
  recursively nested list-family value-field boundary. No alternate physical schema
  representation can share the accepted semantic descriptor.

The accepted API is a serializer primitive only. It grants no schema-content,
build, product, receipt or publication authority.

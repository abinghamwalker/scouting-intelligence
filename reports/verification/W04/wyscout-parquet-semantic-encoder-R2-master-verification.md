# W04 Parquet semantic encoder R2 master verification

Date: 2026-07-31

Disposition: `MASTER_FOCUSED_CHECKS_PASS_AWAITING_FRESH_INDEPENDENT_REVIEW`

The master inspected the full bounded R2 correction and independently reproduced its
suite. R1's failed-review evidence remains retained. This freezes a new exact
candidate; it grants no publication authority.

## Exact candidate

- format implementation: `cfa25e672072cba702d103a2a68c79f2895852ee91e966b998cc3a2e13beb5ea`
- focused tests: `113af1f3b23aac813e0b8484b02348f53d96af0eb816cb495ae90325d5dd158f`
- R2 producer return: `5c007e2f370c7e231ea83e6a19d3f0ce35121a17dbdb40ef12fe5d6624aee063`
- preserved physical vector: `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- preserved semantic vector: `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`

## Master inspection

- Every combined Arrow row is recursively projected under its explicit supported
  type to a complete JSON object, and its canonical bytes must equal its supplied
  canonical checked-contract bytes before semantic hashing or Parquet encoding.
- Contract top-level keys must equal schema names. Primary-key fields must exist in
  the Arrow schema, and caller keys must exactly match Arrow-derived values by both
  type identity and value; string/integer and Boolean/integer confusion is closed.
- The projection admits only the packet's finite primitive, UTC-microsecond timestamp,
  decimal, list and struct forms, recursively enforcing nested field metadata,
  nullability, identifiers and supported children. Unsupported types fail closed.
- R1's unchanged-key/non-key divergence and all related bypasses now fail. The
  physical/semantic vectors and full R20 writer/framing behavior remain unchanged.
- The fresh review must also challenge direct construction of schema descriptors
  passed to the public semantic helper. A descriptor claiming an unsupported Arrow
  type must not become authoritative outside the encoder's supported-schema boundary.

## Independently reproduced checks

- Ruff format/check and mypy: PASS.
- encoder plus legacy guarded-storage suite: PASS, `61 passed in 2.09s`.
- focused Bandit: PASS.
- import-linter: PASS, 3/3 contracts kept.
- local-only verifier: PASS, 25/25 controls.
- exact candidate hashes and both preserved vectors: PASS.
- `git diff --check`: PASS.
- `git remote`: PASS, empty output.

Fresh independent review is required before master acceptance or publisher dispatch.

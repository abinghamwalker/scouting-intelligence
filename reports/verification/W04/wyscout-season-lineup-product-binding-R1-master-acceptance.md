# W04 season/lineup product-binding R1 master acceptance

Date: 2026-08-01

Decision: `ACCEPTED_BOUNDED_AUTHORITY_DOWNSTREAM_GATES_REQUIRED`

The master accepts the exact additive season UUID and cardinality-one lineup
population authority after bounded R2 test rework and fresh independent PASS.
This acceptance changes no R20/R21/R4, source, completion-index, identity-bundle,
schema-root, feature, Gold-population or local-only boundary.

## Accepted chain

- authorization:
  `9802e4ae037593c62db2b52d38acd4133e5a3d50e59e5ad346c982ad8cca47bb`;
- unchanged decision:
  `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e`;
- R2 tests:
  `3a4ed66082d16cf55a87921a742aea30f5600ad538f2664d0a65fe5be2b9e21f`,
  `12d7379b7594caaea2aed508fd1444cfa307d1911d8d12fb52222d050c0fc73b`,
  `6ae725e379a33cd0785b346fe4ddcdca3fdc296ff24a1f78697202834e7d0df6`;
- R2 producer return:
  `98cc732eeb79341fc7d58885825c808bae9fa3a1ac1beeedcafdb7e3cb885e74`;
- R2 master verification:
  `e573d849afcac3734c894d5f073871fd0eaf14ce7b3d7916e8c4b177053f6a2a`;
- fresh PASS review / embedded record:
  `3f88335db70609e90f0d02cbbc206752479f5300e196329fc48f07154899cf0f` /
  `cef416d4d99993db8ea07847a8e5c57ad6924f16f7ed8f7f0edf48a273efca44`;
- fresh reviewer return:
  `7a4f6c27e9a37ea7e747c3ada0f03a4778e8354624d605a715b98a7d695e98a3`;
- canonical acceptance:
  `6cbf2cd2aea87489854eee208ee4cbb3f7d3dc2c603d32aa306515418863c27e`.

The failed review remains byte-identical at SHA-256
`431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba`;
its retained return remains
`8218de5bb7e38114204d8c5a82586ff0718887c3ec3a2a682b216f367d91b547`.

## Acceptance basis

- Fresh review: `PASS`, P0/P1/P2 = `0/0/0`.
- Master live-lifecycle suite after fresh review: `169 passed in 3.72s`.
- Master lifecycle after canonical acceptance: `169 passed in 3.72s`.
- Local-only verifier: PASS, 25/25; `git remote` empty; diff check clean.
- Both UUIDv5 chains, strict source/member/ordinal/raw digest, exact one-row
  population and unchanged 25-key `authority_rows` integration reproduced.

The master's first acceptance serialization had SHA-256
`50c88db23b8b352aadab650ae4833caf9ad608fd9699fa8c0ee63797924cedd3`
and was rejected by the live canonical parser (`1 failed, 168 passed`) because
`review_record_sha256` preceded `review_recommendation`. The master changed only
that key order, reran the lifecycle, and accepted the final digest above.

## Exact accepted product bindings

- season source ID `181150` ->
  `4696aa1f-b512-5d18-af79-33cf031455cf` through the documented season UUIDv5
  namespace/name;
- exactly one lineup stint `591cdf5b-2281-53c4-8225-150313ca2c01` for match
  `2499719`, team `1631`, player `285508`, ordinal `0`, start `[82,83)`, absent
  terminal/minutes, right-censored, per-90 ineligible, reason
  `suppressed_unsupported_denominator`.

No identity-bundle kind, schema root, feature, Gold row or wider population is
accepted. Downstream implementation remains conditional on the complete
repository gate and the independently reviewed build/schema/aggregate/runtime
gates; this acceptance alone creates no product or publication permission.

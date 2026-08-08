# W04 logical-to-Arrow projection implementation R3 — master acceptance

- Accepted at: `2026-08-01T17:22:25Z`
- Master: `/root`
- Decision: `ACCEPTED_BOUNDED_SERIALIZER_PRIMITIVE_23_ROOT_PRODUCER_MAY_RESUME`

The master accepts the exact R3 descriptor-led serializer primitive after one
master R1 test-evidence correction, one independent R1 P1 finding, bounded R3
rework, fresh independent R2 PASS, and final independent master reproduction.

## Accepted implementation bytes

- serializer:
  `309ee2821913022c3ce82b713a53e74dd4ac3190af0047a621ba4ab2cd0f7209`;
- serializer tests:
  `0d6acf199d230257656f91c0c191c3bbef5dfb23c5cf49e6f731da4d57c8f317`;
- frozen runtime build contract:
  `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16`;
- frozen corrected build tests:
  `f39e34daac144369444e1701003efdec0c1a97f83ba5fb0beecaf844c21e4692`;
- R3 packet and return:
  `886b5c28192074d2fd494c178c47e36c54c327ade80d3fe4e9d8a4a47720e8a7` /
  `3ea3633cb6adcec96912e53b280b6ea3c19f41a8cb4f2340f7160d3bb68571a6`;
- R3 master verification:
  `208cd225cf8e0f0709cc5f8026f8d4de1efdac79aa755ece77f8b0eaaf824142`.

## Review chain

- preserved failed R1 review packet/review/return:
  `f4afbf9ae5996e76d79fafb7c8a9744955f4daa5da77ac0c4c6cb2d040500856` /
  `8b40285f742be1434670fecca743c9d94c3513b1edc7e583ab073d913c9db9eb` /
  `1a7db7673711a6fa3e824661ccb9a748c06daf62e769f328142c7f170b2eba32`;
- R1 finding: `W04-LAP-IMPL-R1-P1-01`;
- fresh R2 review packet:
  `b23ee7347ec4c2729900d0f5d9a4cf11a269f8196290f5f772954ad41f3dae99`;
- fresh R2 PASS review and canonical embedded record:
  `8552a5b98f4adf226dce019be62915f3dabcc26dc97275c9da39e6eb2ca73c0b` /
  `f457b9717771cae88e6c6cbcf80694054ae34a88e66810eee750ebb90c2fd045`;
- fresh R2 reviewer return:
  `dcb8562ffb2745d9256157289b40dc8c07f4af1579e96610fa0bff835f24524b`;
- fresh verdict: PASS, P0/P1/P2 = `0/0/0`.

## Master final reproduction

- Complete final review/return readback: PASS.
- All final candidate, failed-review and authority bindings: exact.
- Original constructed-model exploits: `4/4` rejected independently.
- Expanded copied/constructed bypass suite: `84 passed`.
- Ruff format/lint and mypy over all four final files: PASS.
- Serializer plus build-contract suite: `219 passed`.
- Authority/composability regression suite: `179 passed`.
- Local-only verifier: PASS, `25/25`; `git remote -v` emitted nothing.
- Accepted physical identity digest:
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`.
- Accepted semantic identity digest:
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

## Exact accepted boundary

The accepted primitive generates schemas only from exact recursive projection
descriptors, represents present canonical tagged JSON as non-null UTF-8 without
LF, strictly revalidates raw direct and nested logical state before serialization,
strictly decodes physical tagged text, restores descriptor-owned positional
tuples and homogeneous lists, rejects malformed input before hashing/writing, and
preserves the sole `w04-wyscout-parquet-semantic-v1` preimage.

The acceptance grants no root descriptor, root schema, schema bundle, product
byte, manifest, receipt, feature, population, dependency, provider access,
publication, deployment or external-infrastructure authority. Gold receipt
closure remains fail-closed until the separately accepted exact Gold root
descriptor exists.

## Progression decision

The exact 23-root schema producer may now resume under a new bounded packet. It
must freeze independently reviewable canonical root descriptors and physical
schema evidence; it may not create product bytes or resume aggregate/product
implementation until its own independent review and master acceptance pass.

# W04 logical-to-Arrow projection implementation R2 — master verification

- Verified at: `2026-08-01T16:41:46Z`
- Master: `/root`
- Commit base: `82a9f05b0db176dd55cbd4fa6b4388ec2b0a1906`
- Verdict: `PASS_READY_FOR_FRESH_INDEPENDENT_IMPLEMENTATION_REVIEW`

## Candidate chain

- R1 implementation packet:
  `b36793b729561521203ddb507161326340e2a14e73cc5616a59ae2eb18c6b6e5`;
- R1 producer return:
  `197bb99e4fe6a6328a709f4af946166429e97aa8fed5858df2b6b954806e8372`;
- R2 rework packet:
  `4cf5c45c460fa275de88b608303e3b601267a6ad8465c2e47eb8bab35e78cf04`;
- R2 producer return:
  `4f8cde34645c8cc5c9ab19cf05a1c9a3c5b50290615df352e551bda5b8caa934`;
- final serializer implementation:
  `d1827127ce36a67dc49993f5cdb4cd18a5ab5bc62f3b753808529f66dba9f2c9`;
- final serializer tests:
  `b5fe5aa5831755abe83cd8fd812538dbfbb091190a42430fb09c9141d7e33cce`;
- final runtime build contract:
  `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16`;
- final corrected build tests:
  `f39e34daac144369444e1701003efdec0c1a97f83ba5fb0beecaf844c21e4692`.

## Master R1 rejection and R2 disposition

The R1 source implementation and runtime behavior passed all executable checks,
but the master rejected its build-test helper because it introduced a novel
`w04-gold-schema-authority-unavailable` SHA-256 preimage and labelled the result
as semantic evidence. That test-only second semantic path violated the frozen
single-derivation boundary.

R2 removed the formula and uses only the pre-existing fixed `H1` value through
the explicit name `REJECTED_CALLER_GOLD_SEMANTIC_CLAIM`. A new test proves the
claim is present only in rejected fixture state and cannot authorize receipt
closure. The R1 serializer, serializer tests, runtime build contract, authority
bytes, and R1 evidence remain byte-identical.

## Master complete readback

The master inspected the complete serializer module and unit matrix, the runtime
build readback boundary, all changed build-test helpers/assertions, and both
producer returns. The candidate:

- generates Arrow schemas only from exact recursively validated descriptor
  content;
- removes caller schema/schema-role authority from the public encoder and
  semantic-hash APIs;
- implements exact tagged UTF-8 canonical JSON encoding and strict inverse;
- distinguishes outer Arrow null from present tagged canonical JSON null;
- restores positional structs as logical tuples and lists as homogeneous logical
  sequences under descriptor-owned child/cardinality rules;
- validates malformed input before semantic hashing and Parquet writing;
- preserves the sole existing semantic preimage and identity golden vectors;
- leaves Gold receipt closure fail-closed with
  `GoldSchemaAuthorityUnavailableError` and no caller table/schema/descriptor
  field in `GoldProductReadback`.

## Independently rerun checks

- Ruff format and lint over all four code/test files: PASS.
- mypy over all four code/test files: PASS.
- serializer plus build-contract suite: `135 passed`.
- authority/composability regression suite: `179 passed`.
- local-only verifier: PASS, `25/25`; zero Git remotes.
- forbidden unavailable-semantic domain/formula search: zero matches.
- final R1 source/runtime hashes: unchanged after R2.

## Boundary decision

The candidate creates no accepted root descriptor, root schema, schema bundle,
product file, manifest, receipt, feature, population, dependency, provider
access, publication or external infrastructure. A fresh independent
implementation review with zero P0/P1/P2 findings and separate master acceptance
remain mandatory before the 23-root producer resumes.

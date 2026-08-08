# W04 logical-to-Arrow projection implementation independent review R2

- Task: `W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-REVIEW-01-R2`
- Date: 2026-08-01
- Reviewer: fresh independent R3 logical-to-Arrow implementation reviewer
- Verdict: **PASS**
- Findings: **P0 0 / P1 0 / P2 0**
- Root-schema or product authority created by this review: **NO**

The exact R3 candidate closes `W04-LAP-IMPL-R1-P1-01`. Raw runtime state is
recovered recursively and checked before any Pydantic JSON dump. Both the exact
R1 exploit and the wider copied/constructed-model attack matrix now fail closed
before semantic hashing or Parquet writing. The descriptor, inverse, semantic
preimage, fixed vectors and build fail-closed boundary also pass fresh
independent reconstruction.

## Frozen evidence admission

Every packet-fixed binding was recomputed before analysis and after all probes.
All matched exactly:

| Binding | Reproduced SHA-256 |
|---|---|
| R2 review packet | `b23ee7347ec4c2729900d0f5d9a4cf11a269f8196290f5f772954ad41f3dae99` |
| authority decision | `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1` |
| authority acceptance | `647ce58093485717a50037eeb6e46d09c2dfad88a8f60bdef7bce8d35f8d31c3` |
| authority master acceptance | `2918b19595297ecfcd029e1f04c2b6be23bcbfcc9b2c79e298222fd389435d86` |
| failed R1 review packet | `f4afbf9ae5996e76d79fafb7c8a9744955f4daa5da77ac0c4c6cb2d040500856` |
| failed R1 review | `8b40285f742be1434670fecca743c9d94c3513b1edc7e583ab073d913c9db9eb` |
| failed R1 reviewer return | `1a7db7673711a6fa3e824661ccb9a748c06daf62e769f328142c7f170b2eba32` |
| R3 correction packet | `886b5c28192074d2fd494c178c47e36c54c327ade80d3fe4e9d8a4a47720e8a7` |
| R3 producer return | `3ea3633cb6adcec96912e53b280b6ea3c19f41a8cb4f2340f7160d3bb68571a6` |
| R3 master verification | `208cd225cf8e0f0709cc5f8026f8d4de1efdac79aa755ece77f8b0eaaf824142` |
| corrected serializer | `309ee2821913022c3ce82b713a53e74dd4ac3190af0047a621ba4ab2cd0f7209` |
| corrected serializer tests | `0d6acf199d230257656f91c0c191c3bbef5dfb23c5cf49e6f731da4d57c8f317` |
| frozen build contract | `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16` |
| frozen build tests | `f39e34daac144369444e1701003efdec0c1a97f83ba5fb0beecaf844c21e4692` |
| implementation design | `75cc8ff80cbb3c125a7164499b36c9cf1bad200ea1e8dcf096c019ad1c9adead` |
| accepted encoder review | `eb5928d0bc06be4ecbe8317d9d3387e2db5d6d8631d08ac3dacbc45583c5ad9d` |
| accepted encoder master acceptance | `1cfcd5bde3128a7736c75360460e61f73cc9910772d80d5e0b062abb606ce519` |
| accepted build master acceptance | `26026181020650779bd7319c0672abf5dc5e78313fd38a33aff385bcb65c3449` |

The failed R1 review and return remained byte-identical. The build module and
build tests also remained byte-identical across the correction.

## R1 P1 closure

The independent reproduction covered the four original malformed families:
Boolean-as-integer, float-as-integer, integer-as-Boolean and bare-dict-as-array
child. Each was created through both `model_copy(update=...)` and
`model_construct`, then submitted directly, nested in a constructed array and
nested in a constructed object. All `24/24` cases raised `FormatError`.

An expanded `32 x 3 = 96` raw-state matrix additionally attacked:

- exact class and model-field rosters, missing state, unknown extra state,
  explicit empty extra state and forbidden field-set state;
- enum-versus-string and wrong-arm discriminators;
- Boolean, float and string substitutions for integer, and integer for Boolean;
- list-versus-tuple, bare dict versus typed value/member, and wrong member-key
  types;
- duplicate and unsorted object members;
- non-finite Decimal values, non-NFC text and surrogate text; and
- every direct case recursively through both array and object containers.

All `96/96` cases failed. Instrumented tripwires observed zero Pydantic
`model_dump` calls for the malformed integer-arm cases, zero semantic-hash calls
and zero Parquet writes. Fresh validation retained the exact union arm for all
seven valid variants, including a finite Decimal and mixed recursive content.

The correction is sufficient because it requires exact model/member classes,
exact raw field dictionaries, no extra state, bounded field-set state, exact
enum discriminators, exact primitive/container types and exact recursive typed
children. It then constructs a fresh plain discriminated mapping and strictly
validates it before the first JSON-mode dump.

## Tagged value and strict inverse audit

- All seven present tagged variants encoded without a terminal LF and completed
  exact descriptor-led logical/physical round trips.
- Present tagged JSON null remained the non-null UTF-8 scalar
  `{"kind":"null","value":null}`. A separate optional outer absence remained
  Arrow null; the two-row distinction passed.
- `22/22` malformed physical cases failed before semantic hashing and writing.
  The matrix covered raw invalid UTF-8, BOM, terminal LF, top-level and nested
  duplicate keys, `NaN`, positive/negative infinity, decimal/exponent tokens,
  whitespace, key order, escaped spelling, non-NFC and surrogate text, unknown,
  missing and extra discriminator fields, wrong typed values, untagged null and
  an untagged array.
- The inverse therefore preserves strict UTF-8, duplicate/constant rejection,
  exact typed validation, canonical re-encoding and byte equality.

## Descriptor, tuple, list and schema audit

- `28/28` malformed descriptor attacks failed. These covered alternate objects,
  descriptor/field/node subclasses, invalid runtime enum and collection types,
  schema role/version/field roster, names/nullability/top-level positions,
  scalar/projection compatibility, decimal state, empty/list/duplicate structs,
  tuple position duplication/gaps/reordering and list kind/fixed-size drift.
- Exact positional tuples restored logical arrays in descriptor order for both
  present and nullable children.
- Empty and non-empty homogeneous lists used the same generated schema; a valid
  fixed-size list also round-tripped.
- `29/29` independently built physical-schema attacks failed before semantic
  hashing or writing: six tuple omissions/additions/renames/reorders/type and
  nullability changes, five list child/list-kind changes, and eighteen empty or
  nonempty metadata-presence changes across schema, top fields, nested structs,
  lists, struct-under-list and list-under-struct boundaries.
- Encoder and semantic-helper signatures expose only the projection descriptor,
  logical rows/keys and parents. Caller schema, callback, Boolean, digest and
  alternate schema authority are API-unrepresentable. Generated schemas are
  derived only from descriptor content, never row or fixture inference.

## Sole semantic derivation and fixed vectors

An independent identity fixture reproduced:

- physical SHA-256
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`;
- semantic SHA-256
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`;
- exact Parquet 2.6/ZSTD/statistics/no-dictionary/no-byte-stream-split/no-index
  controls; and
- a separately assembled `616`-byte semantic preimage with the accepted domain,
  `S/R/P` markers and unsigned-64 length framing.

The parent sequences `("a", "bc")` and `("ab", "c")` remained separated. No
projection-kind token or projection digest was present in the preimage. Source
search found one W04 Parquet semantic definition and call path only:
`WYSCOUT_PARQUET_SEMANTIC_VERSION`,
`w04_wyscout_parquet_semantic_sha256`, and the encoder call in
`src/scouting/storage/formats.py`. The distinct complete-LayerManifest semantic
derivation remains the frozen R4 two-key manifest authority, not a second
Parquet/product-row derivation.

The unavailable Gold fixture value is explicitly named
`REJECTED_CALLER_GOLD_SEMANTIC_CLAIM`; no unavailable-schema formula or accepted
placeholder claim exists.

## Frozen build and scope audit

`GoldProductReadback` still has exactly three content-bearing fields:
`contract_row_bytes`, `physical_bytes`, and `temporal_proof_bytes`. Caller table,
schema or projection-descriptor authority is unrepresentable. Fresh receipt
closure probes against the accepted fixture and a coherent substituted physical
claim both terminated with `GoldSchemaAuthorityUnavailableError` at the absent
accepted `GOLD_PLAYER_WINDOW` projection descriptor. Empty physical content was
rejected earlier.

No runtime root descriptor or schema exists outside the serializer primitive and
its tests. No Bronze, Silver or Gold product/manifests/rebuild output was found;
the pre-existing local W04 files remain limited to source/completion and identity
evidence. No feature, population, dependency, provider, publication, cloud,
container, hosted-CI, endpoint, deployment or Git remote change was observed.
The local-only verifier passed all `25/25` controls with zero configured remotes.

## Required commands and results

- Ruff format: exit `0`; four files already formatted.
- Ruff lint: exit `0`; all checks passed.
- mypy: exit `0`; no issues in four files.
- serializer plus build-contract suite: exit `0`; `219 passed in 2.94s`.
- authority/composability regression suite: exit `0`; `179 passed in 3.82s`.
- local-only verifier: exit `0`; PASS `25/25`, zero configured remotes.
- independent copied/constructed raw-state probe: exit `0`; original `24/24`
  and expanded `96/96` rejected, zero malformed dumps/hashes/writes, seven valid.
- independent tagged inverse probe: exit `0`; seven valid variants, exact
  tagged-null/outer-null distinction and `22/22` malformed rejections, zero
  malformed hashes/writes.
- independent descriptor/physical-schema probe: exit `0`; `28/28` descriptor and
  `29/29` physical attacks rejected, zero malformed hashes/writes.
- independent semantic reconstruction: exit `0`; both golden vectors, exact
  preimage, framing separation and physical controls reproduced.
- independent build fail-closed probe: exit `0`; closed three-field readback,
  caller-schema unrepresentability and unavailable-authority termination
  reproduced.
- final complete fixed-binding recheck: exit `0`; every fixed hash matched.

## Final decision

`PASS` with P0/P1/P2 = `0/0/0`. The exact R3 serializer candidate is suitable
for separate master acceptance. This review grants no root descriptor, schema,
product or publication authority; the 23-root producer remains paused until the
master accepts the candidate.

```w04-logical-arrow-projection-implementation-independent-review-v1
{"candidate_formats_sha256":"309ee2821913022c3ce82b713a53e74dd4ac3190af0047a621ba4ab2cd0f7209","candidate_formats_test_sha256":"0d6acf199d230257656f91c0c191c3bbef5dfb23c5cf49e6f731da4d57c8f317","finding_counts":{"P0":0,"P1":0,"P2":0},"findings":[],"recommendation":"PASS","review_id":"w04-wyscout-logical-arrow-projection-implementation-independent-review-R2","review_schema_version":"w04-logical-arrow-projection-implementation-independent-review-v1","reviewed_at":"2026-08-01T17:18:27Z","reviewed_by":"4811793e-9b1f-40a9-ba97-d37412a85c68"}
```

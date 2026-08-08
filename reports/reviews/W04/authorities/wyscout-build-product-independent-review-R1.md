# W04 build/product authority independent review R1

Date: 2026-08-01  
Task: `W04-BUILD-PRODUCT-AUTHORITY-REVIEW-01-R1`  
Reviewer: fresh independent build/product authority reviewer

## Verdict and downstream classification

`PASS_AUTHORITY_ONLY_PRODUCT_BLOCKED`

- Authority recommendation: `PASS`
- P0: `0`
- P1: `0`
- P2: `0`
- Product/build-contract dispatch: `BLOCKED_PENDING_BOUNDED_SEASON_AND_LINEUP_AUTHORITY`

The exact R4 decision is a sound authority-only freeze. It binds the authorized
inputs and closes the window, source-completion population, aggregate order,
single build hash, receipt rosters, Gold-manifest population, sole layer-manifest
semantic derivation, four-feature scope, lifecycle, and local-only prohibitions.
It neither creates nor permits any aggregate instance, build, product, manifest,
receipt, publication, or external action.

The accepted bytes do not, however, close two downstream inputs. Source
`seasonId=181150` has no accepted canonical season UUID rule, and the authentic
target-player bench/substitution evidence has no accepted exact zero-versus-one
lineup product population rule. Neither absence is a defect in this explicitly
decision-only freeze, but both are hard blockers to build-contract or product
dispatch. A later packet must not invent either value.

## 1. Fixed-byte admission

Every packet-fixed binding was reproduced before analysis:

| Artifact | Reproduced SHA-256 | Result |
|---|---|---|
| authority decision | `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d` | exact |
| authority test | `94cafedb2c4d0e50aecebb8a52ffc6666f2f37607d14d7155f25a0d5aea18ed8` | exact |
| producer return | `d4d1032d8fbf48f5c0789d8eadb2f46dec6dc1d7435da77283b29e1bcd056ecf` | exact |
| master focused verification | `21f424bac76eac85f36449673b737aadfa6fe7cca3c5e5af3393153b73a8d64c` | exact |
| R4 closure audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` | exact |
| R4 independent review | `288c58c29bbd572b8fe9bf5df9875d5a6b9c24cfca44923b8780e2dcb7bd7827` | exact |
| build/schema audit | `402106160add4af2d12b46022220b6d7d71b3f0243e85162b56fd1674c28fc24` | exact |
| vertical-slice audit | `ccc7a7c803cf2acfb5a787f0f8594c7f2c1c446ba3365ced84bcde2e35b3cad7` | exact |

The decision's 17 bound input paths were then independently reopened. All 17
physical hashes equal the ordered decision rows, including R20
`8cb2f0d4...78047`, R21 `faff34cc...7020`, R2/R3/R4, both v1 aggregate
preimages, source manifest/index, and all four accepted semantic/identity
authorities. The authority is strict canonical JSON plus exactly one terminal LF,
16,947 bytes, with no duplicate, omitted, unknown, or noncanonical key route.

## 2. Exact reconstruction

The five-key window object canonicalizes without a terminal LF to exactly 250
UTF-8 bytes. Its independently reproduced SHA-256 is
`3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327`.
Applying the fixed UUIDv5 namespace/name rule yields
`a0af8d56-e41d-5467-b46e-82887c4861e0`. The selected match is provider
`2499719`, canonical `bad97950-6fac-5cf0-a93c-094f91abbb9b`, inside the exact
half-open window, with snapshot `2017-08-11T18:45:00Z` and strict cutoff
`2026-08-01T00:00:00Z`.

The content-addressed completion index reproduced
`46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
Its exact England member binds source digest
`301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`
and the sole selected-match period population:

- `1H`: 901 actions, membership
  `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`;
- `2H`: 867 actions, membership
  `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`.

The aggregate dependency order contains eight unique nodes and orders complete
23-root schema closure before product contract, then the unchanged 25-key
pre-build projection. The projection has 25 unique keys; the inverse removes only
`build_id`, restores only `schema_version`, and a second build hash is explicitly
forbidden. Receipt surfaces remain exactly nine invocation keys and 15 boundary
keys with the exact interval predicate.

The layer graph is acyclic: accepted authorities lead to the complete schema
bundle, then product contract, then one 25-key build hash, product, complete
`LayerManifest`, independently reproduced same-layer summary,
boundary/invocation receipt, and child result. No edge points backwards.

For each layer, the sole semantic preimage has exactly the two keys
`layer_manifest` and `semantic_schema_version`, uses the complete parsed,
guard-read, closed-schema manifest object, and has no terminal LF. The manifest
contains no layer-level semantic digest, summary, receipt, or wrapper digest, so
the formula has no backward/self edge and admits no second preimage. Bronze has no
parent; Silver has exactly Bronze; Gold has exactly Silver. The Gold manifest is
the sole population root and must yield exactly one Gold product and one boundary.

## 3. Adversarial attacks

The independent attack matrix and the 128-test focused suite rejected:

- missing, additional, duplicate, or reordered 23-root, 25-key, 9-key, 15-key,
  summary, parent, feature, completion-period, and Gold/boundary populations;
- any changed bound-input digest, unknown/omitted top-level authority key,
  malformed/duplicate/noncanonical JSON, 26th projection key, second hash,
  product-permission flip, or lifecycle bypass;
- placeholder, null, anticipated, own, future-output, product, build, receipt, or
  forward/cyclic aggregate digest routes;
- partial-manifest derivation, physical/entry/other-layer digest copying,
  cross-layer swaps, alternate terminal-LF/preimage/version rules, and a second
  semantic derivation; and
- downstream rehashing of summaries, final recheck, receipts, or child wrappers
  after any direct summary substitution. Each case still fails at the earlier
  independently derived complete-manifest-to-same-layer-summary equality.

The lifecycle review parser fails closed on a malformed review, rejects master
self-review, forbids acceptance before review, and binds any later acceptance to
the exact decision, complete review bytes, and canonical embedded review record.
No downstream product, manifest, receipt, build, aggregate, run, or data byte was
present or created during review.

## 4. Season UUID gap

The exact source member
`data/source/wyscout/v5/archive-members/matches_England.json` reproduced physical
SHA-256 `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29`,
1,694,720 bytes and 380 rows. Match `2499719` occurs exactly once at physical
ordinal `379`, raw-record digest
`1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`,
and supplies strict integer `seasonId=181150`.

`SilverMatch`, `SilverPlayerMatchFact`, and `GoldPlayerWindow` require non-null
`season_id: StrictUuid`. Yet `WyscoutIdentityEntityKind` contains only
`COMPETITION`, `TEAM`, `PLAYER`, and `MATCH`; the accepted bundle has exactly
those entity families; and `canonical_source_uuid` admits only competition, team,
player, match, and action source kinds. No accepted byte defines a `SEASON` kind,
namespace, mapping, canonical UUID, or reviewed crosswalk row for `181150`.

Classification: this does not change R4's frozen build architecture, but downstream
implementation needs a bounded additive season semantic/identity authority. It
cannot be filled by reusing another entity namespace, hashing `181150` ad hoc, or
making the required UUID null.

## 5. Target lineup population gap

The same exact match row proves team `1631` contains target player `285508`
exactly once on the bench, zero times in the starting lineup, and exactly once as
`playerIn` at nominal minute `82` for `playerOut=192748`. The accepted identity
bundle independently resolves player `285508` to
`be8da881-2b15-513f-978f-6bb3865bc8e2` and match `2499719` to
`bad97950-6fac-5cf0-a93c-094f91abbb9b`.

R20 supplies a generic right-censored lineup-stint semantic and the 23-root roster
contains `SILVER_LINEUP_STINT`. The downstream audit nevertheless fixes a slice
instruction that omits lineup Parquet unless a later authority explicitly chooses
the evidenced one-row population. The present decision freezes only the exact
Gold one-product/one-boundary population; it does not make that Silver population
choice. Emitting one stint would override the omission/population instruction;
emitting zero would discard authentic known lineup evidence and contradict a claim
of complete lineup coverage.

Classification: downstream product dispatch needs a bounded additive exact lineup
population authority selecting the source-evidenced outcome. This is not permission
to add a feature, widen the source window, or infer elapsed/per-90 minutes, and the
review does not choose the rule.

## 6. Scope and final decision

The only valid packet classification is:

`PASS_AUTHORITY_ONLY_PRODUCT_BLOCKED — P0=0, P1=0, P2=0`

The exact R4 authority may proceed to master acceptance as an authority-only
record. Build-contract, schema/aggregate materialization that would consume the
missing fields, and all Bronze/Silver/Gold implementation or publication remain
blocked until fresh bounded user authority and independent review close both gaps.
No frozen R20/R21/v1/index/R2/R3/R4 byte needs to change to record this review.

```w04-build-product-authority-review-v1
{"decision_id":"w04-wyscout-build-product-authority-decisions-v1","decision_physical_sha256":"3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d","findings":[],"recommendation":"PASS","review_id":"w04-wyscout-build-product-independent-review-R1","review_schema_version":"w04-build-product-authority-independent-review-v1","reviewed_at":"2026-08-01T11:56:23Z","reviewed_by":"4e281150-503d-5400-9a4f-42a40f53593a"}
```

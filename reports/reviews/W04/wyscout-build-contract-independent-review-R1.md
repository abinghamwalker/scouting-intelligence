# W04 Wyscout build-contract independent review R1

Date: 2026-08-01

Review ID: `w04-wyscout-build-contract-independent-review-R1`

Candidate: corrected R2 standalone W04 build contract

Recommendation: **REWORK**

Finding counts: **P0=0, P1=2, P2=0**

## Scope and independence

This review was performed under packet
`W04-WYSCOUT-BUILD-CONTRACT-REVIEW-01-R1` without implementation, test,
dependency, authority, product, orchestration or Git changes. The reviewer did not
produce the candidate, did not delegate and does not approve its own work. The only
outputs are this report and its reviewer return.

## Fixed bindings

Every packet-fixed byte matched before candidate analysis:

| Artifact | Expected and reproduced SHA-256 |
| --- | --- |
| review packet | `42a96d89f3e7d5781a7f14ae4673b02629e46a16f0ce79ef117a235e0ed411c9` |
| R2 producer packet | `8995671c7591b022c36f755e065c5f12b0bfd9138bf6e1a7d40633c3f678d368` |
| R2 authority-audit return | `393113a0f7c06e876c20518a4dc8f7a0a3a016a33127e045a1f48fcf3925ea91` |
| R2 build contract | `ed7345a8bddbfcb0b26deef57fba09726ce05691e553e1fc1166308e449b06dd` |
| R2 build tests | `9a6446a441ebc8a625395418c0c914a76f980c43fe7e17bd2b40294db95fd1ec` |
| R2 producer return | `f69a00196915ac819c6debf06a9c2da034541ef8e1546fc134d77b2af5309912` |
| preserved R1 producer return | `3d6b6f017d1974620024bd32507b600340b65ef16f3c6a75aab738acbe3cd5c8` |
| complete repository gate | `22b0b73078d4d2f0cc7e5eed3920a5401fd3d0e02d9ee3c66d9c7af02f76f469` |
| build authority decision | `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d` |
| build authority acceptance | `9bcd9ef6f61b06f443a4d8f0d590db74559ee739976f285c41127da5ff1f5921` |
| season/lineup decision | `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e` |
| season/lineup acceptance | `6cbf2cd2aea87489854eee208ee4cbb3f7d3dc2c603d32aa306515418863c27e` |
| R4 build/receipt audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 correction | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| accepted Wyscout data contract | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` |

## Findings

### W04-BUILD-R2-P1-UNATTESTED-LAYER-MANIFESTS — P1

`validate_receipt_closure` documents that each supplied manifest has already passed
the accepted closed `LayerManifest` schema, but its executable boundary accepts an
ordinary `dict` and checks only a local subset of fields. No nominally typed value,
content-bound validation attestation or invocation of the accepted validator is
required (`src/scouting/contracts/wyscout_build.py:811-864`).

The positive fixtures expose the gap. Their Bronze and Silver entries contain only
`complete` and a one-key `path`; Gold also omits serializer, schema role, size,
parents, partitions and classification (`tests/contracts/test_w04_wyscout_build_contract.py:130-284`).
All three physical objects are accepted by `validate_receipt_closure`, while the
accepted `scouting.contracts.wyscout_data.LayerManifest.model_validate_json`
rejects them: Bronze has 12 schema errors, Silver 12 and Gold 8. This is not a
different semantic derivation; it is proof that the claimed prerequisite is absent
at the composition seam.

Independent executable reproduction printed:

```text
REPRODUCED_FAIL_OPEN_SCHEMA_ATTESTATION_AND_PRODUCT_REHASH 3
```

where `3` is the number of closure-accepted manifests rejected by the accepted
closed-schema validator.

This violates R4 Sections 3–5 and the R2 authority-audit requirement that a
previously validated object may establish schema validity only when it is strongly
typed or explicitly attested. A plain caller dictionary cannot establish that
authority.

### W04-BUILD-R2-P1-CALLER-DIGEST-REHASH — P1

The same closure accepts `gold_product_physical_sha256`,
`gold_product_semantic_sha256` and `temporal_proof_sha256` as caller-supplied
strings (`src/scouting/contracts/wyscout_build.py:805-807`). It compares those
claims only with the Gold entry and boundary receipt claims
(`src/scouting/contracts/wyscout_build.py:890-935`); it receives no product
physical bytes, validated product semantic value or validated temporal-proof
preimage/readback.

An independent coherent attack changed the Gold entry physical digest to `22...22`,
semantic digest to `33...33` and boundary temporal-proof digest to `44...44`, then
recomputed all three manifest summaries, the Gold-manifest binding, boundary bytes,
boundary summary and matching caller arguments. `validate_receipt_closure` returned
success. No genuine Gold product or temporal proof was supplied.

The producer negative test at
`tests/contracts/test_w04_wyscout_build_contract.py:920-950` changes a Gold entry
but deliberately leaves the boundary and caller values stale, so it does not test
the authority-required coherent downstream rehash. R4 Section 6 expressly requires
downstream rehashes to remain unable to cure an earlier product/readback mismatch.
Caller-supplied mutually agreeing digests do not prove product or proof bytes.

## Bounded executable rework

No architecture, schema-root, population, feature, dependency or local-only change
is required. Both corrections are composition of already-authorized roots:

1. Replace the plain parsed-manifest tuple member with a nominally typed or
   content-bound attested value that can only be produced after the existing
   `wyscout_data.LayerManifest` validator accepts the exact physical bytes. The
   standalone build module may use an internal non-root adapter/attestation and
   must still repeat physical bytes/digest/size, complete-object equality, R4
   semantic, frozen authority, parent and Gold-population equalities. Do not copy
   the LayerManifest schema or add a root.
2. Replace the three digest-only product/proof parameters with exact readback inputs
   or content-bound typed attestations from the already-authorized
   `GOLD_PLAYER_WINDOW` and temporal-proof roots. Independently derive the Gold
   product physical digest, semantic digest, row count and temporal-proof digest
   from those inputs before comparing them to the manifest and boundary. A Boolean,
   raw digest tuple or mutually agreeing caller claims remain insufficient.
3. Rebuild positive fixtures from objects that genuinely pass the accepted
   LayerManifest validator. Add adversarial tests for an invalid-but-locally-shaped
   manifest and for a coherent Gold physical/semantic/temporal substitution with
   every downstream wrapper rehashed. Both must fail at the prerequisite/readback
   boundary.
4. Preserve the exact 23 roots, five authorities, five dependencies, 25/25 one-hash
   projection/inverse, sole R4 semantic derivation, one-match/one-Gold population,
   four-feature scope and standalone/local-only boundary.

The correction can therefore remain a bounded R3 contract/test packet. It does not
require product publication or product bytes in the repository; synthetic in-memory
readbacks/typed values are sufficient for contract tests.

## Passing independent evidence

- The exact window, match, season and competition UUIDv5 chains reproduced:
  `a0af8d56-e41d-5467-b46e-82887c4861e0`,
  `bad97950-6fac-5cf0-a93c-094f91abbb9b`,
  `4696aa1f-b512-5d18-af79-33cf031455cf`, and
  `cb5c5317-fa4a-571e-93dc-ef6ce482eab7`.
- The exact five accepted authority rows, five dependency rows, 25-key projection,
  25-key invocation and strict one-hash inverse reproduced.
- The admission model enforces the exact 23 lexical stable-manifest fields, twenty
  ordered proofs, recomputed component/environment/proof-array digests, exact uv
  version and independent ordered count seam. The packet tests cover coherent
  component changes, each proof digest/count, order, missing/additional fields and
  Boolean counts.
- Static inspection confirmed standard-library plus Pydantic imports only, no other
  `scouting` import and no filesystem, network, provider, process or writer API in
  the contract module.
- Local-only verification passed all 25 checks with zero Git remotes and no cloud,
  container, hosted CI, endpoint, external service or deployment boundary.

## Checks

| Command | Exit | Result |
| --- | ---: | --- |
| `shasum -a 256` over the review packet and all fixed bindings | 0 | every expected digest reproduced |
| `uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | 2 files already formatted |
| `uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | all checks passed |
| `uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | no issues in 2 files |
| `uv run pytest -q tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py` | 0 | 199 passed in 4.09s |
| `uv run python scripts/verify_local_only.py` | 0 | PASS, 25/25 checks |
| independent LayerManifest-validation and coherent product/proof rehash probe | 0 | both P1 fail-open routes reproduced |
| independent UUID/projection/inverse probe | 0 | exact IDs, five/five rows and 25/25 projection reproduced |
| independent AST import-boundary probe | 0 | standalone imports only |

The first locked/no-sync independent probe attempt exited `2` because sandboxed uv
could not inspect its external cache; the same read-only probe through the packet's
accepted `uv run` route exited `0`. No candidate or environment bytes were changed.

## Verdict

`REWORK`. P0/P1/P2 are `0/2/0`, so the candidate is not accepted. No downstream
schema aggregate, product implementation or publication may rely on this receipt
closure until a bounded correction receives fresh independent review and master
acceptance.

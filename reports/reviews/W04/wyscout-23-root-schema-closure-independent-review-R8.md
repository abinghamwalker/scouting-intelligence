# W04 23-root schema closure independent review R8

- Date: 2026-08-02
- Task: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R8`
- Candidate: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R8`
- Verdict: **PASS**
- Findings: **P0 0 / P1 0 / P2 0**

## Fixed bindings

All six packet-fixed artifacts reproduced before review and again after every
candidate-facing check.

| Artifact | Required and observed SHA-256 |
| --- | --- |
| accepted R7 schema | `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4` |
| R8 schema test | `5daaa32082cc0f82ed9b8b0b61cc06fe9d2db633cb15ed9c9837e491f2b9a5b8` |
| R8 producer return | `2d92e13e53a2d8a8aa3104145c1947da882ef85eeb57bfcefc4acad4310a9a99` |
| R7 independent review | `f4c74753d9a168bb00ee503066e088ea897d445c6cd6bdbaa9a7b1be07bfc2ec` |
| R7 reviewer return | `2cacfc08b21f4c3dbf536d9037bb108afb09f25ca4b70ea830ffb43fa2b8d746` |
| frozen R5 acceptance oracle | `a3f15f92a14ff342efd0f5b2848b60eab4898ea79eb69c7fd6f09e6946077efa` |

The schema binding is unchanged from accepted R7 bytes. The R8 change remains
test-only.

## Independent exact matrix reconstruction

I instantiated the matrix through the ordinary strict runtime constructors and
read the validated models back dynamically. The exact root-cardinality vector is
`[2,5,7,1,1,1,1,3,2,2,2,2]`, totalling 29.

The three `SilverAction` rows independently reproduce all frozen Section 5.6
conditions:

- distinct canonical action IDs, source/action IDs `(5,6,7)`, source-event IDs,
  and physical source identities at ordinals `(0,1,2)`;
- one exact ACTION source row in each lineage and one exact sequence entry copying
  all action evidence fields;
- position counts `(0,1,2)` and declared seconds scales `(0,18,18)`;
- seconds `0`, `10.123456789012345678`, and
  `9999.999999999999999999`, with exponents `(0,-18,-18)` and the final value
  occupying all 22 decimal128 capacity digits without rounding;
- the null row has all five competition/player/team/event/subevent fields null,
  no positions, sorted tags, `PREDICATE_UNMAPPED`, `INELIGIBLE_UNMAPPED`, and no
  resolved-group membership;
- the admitted rows have exact CONTROL `(8,80)` and RESTART `(3,30)` decisions,
  `PREDICATE_ADMITTED`, `ELIGIBLE_RESOLVED`, and actual resolved-group membership;
- position `(x, exponent, y, exponent, bound)` state is exactly
  `(1.000000000000000000,-18,99.00,-2,true)`,
  `(0,0,100.000,-3,true)`, and
  `(99.000000000000000000,-18,1.0,-1,true)`.

The accepted `SILVER_ACTION` descriptor generated the physical Arrow schema for
each row. Strict inverse validation reproduced exact logical JSON bytes for all
three rows; their independently observed logical SHA-256 values are respectively
`d8821f7ff90ffab5189c6b2c4439b1970916203607049f16e63f66803d288775`,
`bd340d6d1c2c6844e7a44212d03bd1db08f22525863470ad462b892ef3706de2`,
and `a1cd12f177565a4565811a22fd4a255bd262535e3248c584daa8082a824bd353`.

## Retained R7 schema, ledger and Decimal proofs

I extracted the frozen JSONL directly from the R5 report markers rather than from
the candidate or test. It has 56 rows, 56 unique effective owner/validator
bindings, operations `P01` through `P56`, one terminal LF per row, and SHA-256
`c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`.
The independently normalized candidate ledger is byte-identical. Declared owners,
ordered operands and C/literal references match every oracle row. The closed
resolver contains exactly C1-C11 material and all references resolve; the focused
adversarial tests reject missing, unused, reordered and duplicated material.

Independent root export reconstruction retains exactly 23 roots in frozen order,
12 descriptor roots and 11 explicit JSON-only roots, with earlier-only closure
dependencies. Every R7 root-content digest is unchanged:

| Root | SHA-256 |
| --- | --- |
| `BRONZE_KNOWN_RECORD` | `942e5d35f6ca6c300dabd0f75abf3f2673535917960ad04018205f3d657ab3d2` |
| `BRONZE_REJECTED_RECORD` | `e96df3e3bb7a92314dfba6438926ab38c8aaa949627f22cec31a23426d0aef69` |
| `BRONZE_REJECTED_FIELD` | `a4e6ca9a6b10cefa7bff3a47b83b468d0533ffb2a2b1be3ad68efd0b1f561be5` |
| `SILVER_COMPETITION` | `64ba1d31e9cd38c977f6263979b273b7d0d01490c4498a6e5853753ce5689365` |
| `SILVER_TEAM` | `c5cac54dac5d2670726b2a3d3c0568cc5a70abe4cc3b5eb7c644b40191d27e1e` |
| `SILVER_PLAYER` | `d0a346d411f8fc397b58a0ced60462b1e266add31fea3aaf0ed1db0c17514218` |
| `SILVER_MATCH` | `894bbea506348c8df0fede02578cc8768fe33d2b978c32200309db1d6b771dc1` |
| `SILVER_ACTION` | `48e3d53d295f0007596381edd70d7a5adb1cbe38c44f526bcd263e784190eeaf` |
| `SILVER_LINEUP_STINT` | `83cab1bb4c6efa6685ec3b6a76f1b35717edc46ab47e20b61f85ca61b20fde59` |
| `SILVER_POSSESSION` | `89417ddea2384081124fa8c78f7bd607613b1f25d01e30ddbff9c9ac48d0cddd` |
| `SILVER_PLAYER_MATCH_FACT` | `2de9643f90b5db0232efcfe21507c1cac77f1b39794c34bf726af0642787d55d` |
| `GOLD_PLAYER_WINDOW` | `f51e55194c3e33521399a49ccbebb488e30690c377169c568b045533bc41987e` |
| `LAYER_MANIFEST` | `eb3eea153dd33542f066c8c9e8a1b2b189c65dbfd567f6887b680607a632c084` |
| `TEMPORAL_BOUNDARY_RECEIPT` | `8b5310a0171acd2a619a098268e30f041abd8be7a99ecdaa01c19b85de435c9a` |
| `REBUILD_INVOCATION_RECEIPT` | `29285dac1775a712c46521cb6bd071ee78b3878d789bec1da53a69d37883e48a` |
| `ENTRYPOINT_SOURCE_RESULT` | `6f03a0c392082dfebd2b5e4f350a4073099591396739a4d91dc8a0e55a9fa9f9` |
| `COMPONENT_PROOF_RESULT` | `8827dfc0fd28045eb1c295c58348c4595d0a0d610e9c9a3126151f3247bf6eb2` |
| `PRE_BUILD_ADMISSION_RESULT` | `c8d7e2b6d3e22c4dd11dd5ca67ce32bba5ff86f9d6ac698f13f536742c0716f1` |
| `REBUILD_RECEIPT_SUMMARY` | `628f0e1abde6db35071cea1b6c3aea229d7428065500804430309bfdfb85e761` |
| `LAYER_MANIFEST_SUMMARY` | `22e019b4ca289c9d391d7e5df181850fd4f08cbff52449d94d81f96358d4219a` |
| `FINAL_RECHECK_RESULT` | `3bcb9a39b8c8f22e80a63fc9f777c9bdff4fc8436c57915ae3d66640da9e93d6` |
| `POST_BUILD_ID_REBUILD_RESULT` | `a4e49960baefd34b3c0be0705f1cbbf166c9d89679be9b04699565baf107ee63` |
| `CHILD_RESULT_ENVELOPE` | `055086aafb9de829d0e8f7a4f6c6a5ab23b94c1c21f115573ab1b11eae1e8b8f` |

Descriptor traversal retains exactly 30 non-coverage
`EXACT_DECIMAL128_WITH_EXPONENT` paths and 30 ordered decimal128 value children.
Every exact struct is `value: decimal128(22,18)`, `exponent: int8`,
`negative_zero: bool`, all non-null and metadata-free. All six reachable coverage
paths remain `CANONICAL_DECIMAL_UTF8`. The accepted format tests retain strict
inverse reconstruction, signed-zero preservation, nonzero-negative-zero rejection,
capacity/source-scale validation and exact logical-byte reproduction.

## Executed checks and boundary

- Independent fixed-binding and root/ledger/descriptor/matrix probes: PASS.
- `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py`: PASS, `595 passed in 128.54s`.
- `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`: PASS, `179 passed in 3.80s`.
- `uv run ruff check src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`: PASS.
- `uv run mypy src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`: PASS, no issues in two files.
- `uv run python scripts/verify_local_only.py`: PASS, all `25/25` checks; main branch and zero remotes.

The first composite reviewer probe stopped before matrix execution because it
incorrectly assumed numeric iteration order for C1-C11 after canonical JSON object
key sorting. The corrected independent probe compared the exact resolver roster,
references and material without imposing that false post-decode ordering assumption
and passed. No candidate expected value or verdict condition changed.

No candidate/test edit, Git operation, dependency or lock change, provider/network
action, product write, cloud/container/CI action, publication or deployment
occurred.

Verdict: **PASS — P0 0 / P1 0 / P2 0**.

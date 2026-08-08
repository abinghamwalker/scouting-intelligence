# W04 Wyscout v2 aggregate materialization independent review R1

- Date: 2026-08-02
- Task: `W04-WYSCOUT-V2-AGGREGATE-MATERIALIZATION-REVIEW-01-R1`
- Candidate: `W04-WYSCOUT-V2-AGGREGATE-MATERIALIZATION-01-R1`
- Verdict: **PASS**
- Findings: **P0 0 / P1 0 / P2 0**

## Fixed-binding gate

Every packet-fixed binding was reproduced before candidate review. The two logical
identities hash the canonical body without its terminal LF; the two physical identities
hash the complete materialized file.

| Binding | Required and observed SHA-256 |
| --- | --- |
| aggregate implementation | `6cdbb9eaa7d18c5f07d42d6be33d91b014a34824610319f3e55cf5b383c07851` |
| deterministic materializer | `f42ce353382b08171c4495e36c0db00d2ea558b4ef8ca081821b13c3e18a4481` |
| aggregate tests | `6f44bea5569d95a21930f06031e0e78c7d789468d95b780c263f9be0506bc95e` |
| producer verification | `8b881b680816a320b56487d616c1464b0381d3da694d3fd7fc87298b98ac21c1` |
| schema-bundle v2 logical | `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be` |
| schema-bundle v2 physical | `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45` |
| product-contract v2 logical | `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0` |
| product-contract v2 physical | `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af` |

No fixed binding drifted during the review.

## Independent schema-bundle reconstruction

I reconstructed the schema aggregate directly from the accepted implemented-schema
exports, using an independent strict NFC JSON encoder with Unicode-key sorting, compact
separators and no terminal LF. The candidate config was compared only after the
independent object and digest existed.

The reconstruction proved:

- exactly 23 rows in the frozen root-role order, with 23 unique roles and 23 unique
  canonical schema IDs;
- every row has the exact six-key closed shape;
- all 23 root-content digests reproduce from independently canonicalized exported
  content;
- all 47 closure edges name existing roots, contain no duplicate dependency and point
  strictly to an earlier row, which excludes forward references and cycles;
- the top-level object has exactly the required eight keys and exact R20/R21, v1
  predecessor, identifier, root-roster and surface-closure bindings.

The independently reproduced root digests are:

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

The resulting no-LF body is byte-identical to the materialized body and reproduces
logical SHA-256 `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be`.
Adding exactly one LF reproduces physical SHA-256
`8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45`.

## Independent product-contract reconstruction

Only after reproducing the schema digest, I reconstructed the exact ten-key product
contract from the accepted schema constant corpus and frozen build/product authority.
The accepted authority JSON independently equals the exported completion-index binding,
window authority and both receipt contracts.

The reconstruction binds:

- the actual v2 schema digest above and exact v1 product predecessor;
- feature cutoff `2026-08-01T00:00:00Z`, exact selected-match window authority and
  completion-index population, including provider match `2499719` and periods
  `1H=901`, `2H=867`;
- the exact five-step publication order;
- both receipt schemas plus the sole layer-manifest receipt composition;
- exact layer order `BRONZE`, `SILVER`, `GOLD`, parent edges
  `BRONZE->[]`, `SILVER->[BRONZE]`, `GOLD->[SILVER]`;
- the sole two-key complete-manifest semantic wrapper, fixed semantic version, SHA-256
  algorithm, no terminal LF, all-three readback reconciliation and exact one-Gold/
  one-boundary population.

No aggregate contains its own digest or a forward aggregate identity. The resulting
no-LF product body reproduces logical SHA-256
`fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0`;
adding exactly one LF reproduces physical SHA-256
`7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af`.

## Adversarial and materializer review

The candidate validators rejected 23 independently constructed logical mutations:
missing, reordered and additional roots or top-level keys; duplicate schema IDs;
placeholder and swapped root digests; v1/predecessor substitution; self-reference;
forward and cyclic edges; wrong, v1 and self product-to-schema bindings; swapped
predecessor digest; publication reorder; swapped/placeholder receipts; and missing,
reordered or additional product keys.

The actual materializer `check()` was then exercised with in-memory read substitution,
without changing either config. It rejected all nine physical attacks: missing LF,
double LF, CRLF, BOM, malformed JSON, duplicate key, reordered key, additional key and
schema/product file substitution. The exact-byte check makes rehashed malformed,
placeholder, self, forward and cyclic physical candidates unequal as well.

The path guard independently rejected an absent path, a symlink mode, a regular file
with link count two and a before/after metadata change. Exact existing files made
`write()` idempotent without entering `os.open`; unequal existing bytes failed. Source
inspection confirms creation is limited to the two fixed config paths and uses exclusive
creation, complete-write looping, `fsync` and guarded readback. No product, data, run,
manifest, receipt or build instance is scanned or written.

## Fresh acceptance checks

- `uv run ruff format --check src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py tests/contracts/test_w04_wyscout_v2_aggregates.py`: PASS, three files already formatted.
- `uv run ruff check src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py tests/contracts/test_w04_wyscout_v2_aggregates.py`: PASS.
- `uv run mypy src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py`: PASS, no issues in two files.
- `uv run python scripts/materialize_wyscout_v5_contracts.py --check`: PASS with both exact logical digests.
- required aggregate/schema/build/product/cross-authority pytest suite: PASS,
  `231 passed in 53.21s`.
- `uv run bandit -q -r src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py`: PASS.
- `uv run lint-imports`: PASS, three contracts kept and zero broken.
- `uv run python scripts/verify_local_only.py`: PASS, all `25/25` checks, branch
  `main`, zero remotes.

The first two independent reconstruction attempts stopped because my review probe first
treated the exported row tuple as a JSON list and then referenced the semantic version
one level above its accepted `wrapper_fixed_member` location. Correcting only those
review-script assumptions produced the exact identities above; no candidate byte,
authority value or expected verdict changed.

No candidate, config, source, test, orchestration, dependency or lock byte was edited.
No Git, network/provider, product write, cloud/container/CI, deployment or publication
action occurred.

Verdict: **PASS — P0 0 / P1 0 / P2 0**.

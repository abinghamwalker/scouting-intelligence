# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R7`
- objective: Correct only the unaccepted R6 runtime-predicate metadata so the 56 reachable owner/validator bindings reproduce the frozen R5 oracle ledger byte-for-byte, while preserving the accepted Decimal projection, logical closure, runtime validators, and 29-row matrix.

## Files changed

- `src/scouting/contracts/wyscout_schema.py`
- `tests/contracts/test_w04_wyscout_schema_closure.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R7.md`

## Summary

- Replaced the unaccepted R6 alternate predicate semantics table with the exact frozen 56-row R5 JSONL ledger. Candidate normalization reproduces exactly 56 unique effective owner/validator bindings, ordered operations `P01` through `P56`, declared owners, operands, constants, and ledger SHA-256 `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`.
- Added `declared_owner_model` to emitted runtime predicates and verifies it against the actual Pydantic model MRO, including inherited bindings.
- Added a closed `C1` through `C11` resolver over already-frozen authority material. Runtime references and the exact-material E1/E2 uses close the full resolver; unknown, reordered, duplicate, missing, unresolved, empty, and unused references fail closed.
- Added an independent hardcoded copy of the exact 56 R5 JSONL rows to the tests. The test independently reproduces row count, unique binding count, `P01`-`P56` order, exact normalized candidate equality, and the frozen ledger digest; expected values are not derived from implementation tables.
- Retained the AST direct-field subset proof against oracle operands and independently checks declared owners through the runtime MRO.
- Added adversarial resolver/ledger mutations for missing material, unused material, reordered constants, and duplicate constants.
- Preserved E1-E8, the 23-root roster, 12 descriptor roots, 11 JSON-only roots, the accepted `EXACT_DECIMAL128_WITH_EXPONENT` mapping, coverage UTF-8 mapping, strict Decimal inverse/equality tests, and all 29 matrix rows without logical change.
- Candidate SHA-256 bindings after formatting:
  - `src/scouting/contracts/wyscout_schema.py`: `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4`
  - `tests/contracts/test_w04_wyscout_schema_closure.py`: `af355c891aa6472e778c2ad104ccd5a593700c9433bedaf3f7e2cc6f82eb8636`

## Tests run

- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `40 passed in 14.89s`
- command: `uv run ruff format --check src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `595 passed in 126.52s`
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `179 passed in 3.89s`
- command: `uv run bandit -q -r src/scouting/contracts/wyscout_schema.py`
  - exit status: `0`
  - result: no findings
- command: `uv run lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: overall `PASS`; main branch, zero remotes, no hosted CI/container/deployment/external-service boundary violations
- rework note: the first focused run after adding mutation cases produced `38 passed, 2 failed` because the test selected a canonical-key-sorted nested schema without predicates. The test was narrowed to select the first predicate-bearing schema; the rerun and all subsequent suites passed.
- environment note: initial sandboxed Bandit, import-linter, and derived-digest commands could not read `/Users/adrian/.cache/uv/sdists-v9/.git`. The exact commands were rerun with approval to read the existing uv cache and passed; no dependency or lockfile operation occurred.

## Artifacts/evidence

- independent frozen-ledger proof: 56 rows, 56 unique effective bindings, operations `P01`-`P56`, exact candidate-normalized bytes, SHA-256 `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`
- regenerated canonical 23-root content digests in frozen role order:
  - `BRONZE_KNOWN_RECORD`: `942e5d35f6ca6c300dabd0f75abf3f2673535917960ad04018205f3d657ab3d2`
  - `BRONZE_REJECTED_RECORD`: `e96df3e3bb7a92314dfba6438926ab38c8aaa949627f22cec31a23426d0aef69`
  - `BRONZE_REJECTED_FIELD`: `a4e6ca9a6b10cefa7bff3a47b83b468d0533ffb2a2b1be3ad68efd0b1f561be5`
  - `SILVER_COMPETITION`: `64ba1d31e9cd38c977f6263979b273b7d0d01490c4498a6e5853753ce5689365`
  - `SILVER_TEAM`: `c5cac54dac5d2670726b2a3d3c0568cc5a70abe4cc3b5eb7c644b40191d27e1e`
  - `SILVER_PLAYER`: `d0a346d411f8fc397b58a0ced60462b1e266add31fea3aaf0ed1db0c17514218`
  - `SILVER_MATCH`: `894bbea506348c8df0fede02578cc8768fe33d2b978c32200309db1d6b771dc1`
  - `SILVER_ACTION`: `48e3d53d295f0007596381edd70d7a5adb1cbe38c44f526bcd263e784190eeaf`
  - `SILVER_LINEUP_STINT`: `83cab1bb4c6efa6685ec3b6a76f1b35717edc46ab47e20b61f85ca61b20fde59`
  - `SILVER_POSSESSION`: `89417ddea2384081124fa8c78f7bd607613b1f25d01e30ddbff9c9ac48d0cddd`
  - `SILVER_PLAYER_MATCH_FACT`: `2de9643f90b5db0232efcfe21507c1cac77f1b39794c34bf726af0642787d55d`
  - `GOLD_PLAYER_WINDOW`: `f51e55194c3e33521399a49ccbebb488e30690c377169c568b045533bc41987e`
  - `LAYER_MANIFEST`: `eb3eea153dd33542f066c8c9e8a1b2b189c65dbfd567f6887b680607a632c084`
  - `TEMPORAL_BOUNDARY_RECEIPT`: `8b5310a0171acd2a619a098268e30f041abd8be7a99ecdaa01c19b85de435c9a`
  - `REBUILD_INVOCATION_RECEIPT`: `29285dac1775a712c46521cb6bd071ee78b3878d789bec1da53a69d37883e48a`
  - `ENTRYPOINT_SOURCE_RESULT`: `6f03a0c392082dfebd2b5e4f350a4073099591396739a4d91dc8a0e55a9fa9f9`
  - `COMPONENT_PROOF_RESULT`: `8827dfc0fd28045eb1c295c58348c4595d0a0d610e9c9a3126151f3247bf6eb2`
  - `PRE_BUILD_ADMISSION_RESULT`: `c8d7e2b6d3e22c4dd11dd5ca67ce32bba5ff86f9d6ac698f13f536742c0716f1`
  - `REBUILD_RECEIPT_SUMMARY`: `628f0e1abde6db35071cea1b6c3aea229d7428065500804430309bfdfb85e761`
  - `LAYER_MANIFEST_SUMMARY`: `22e019b4ca289c9d391d7e5df181850fd4f08cbff52449d94d81f96358d4219a`
  - `FINAL_RECHECK_RESULT`: `3bcb9a39b8c8f22e80a63fc9f777c9bdff4fc8436c57915ae3d66640da9e93d6`
  - `POST_BUILD_ID_REBUILD_RESULT`: `a4e49960baefd34b3c0be0705f1cbbf166c9d89679be9b04699565baf107ee63`
  - `CHILD_RESULT_ENVELOPE`: `055086aafb9de829d0e8f7a4f6c6a5ab23b94c1c21f115573ab1b11eae1e8b8f`

## Risks

- No known implementation, logical-contract, Decimal-reversibility, schema-roster, security, dependency, or local-only residual risk was found by the packet gates.
- The regenerated descriptor/root bytes and digests are derived and remain unaccepted until fresh independent review and master acceptance.

## Follow-up items

- Fresh independent R7 review and master acceptance of this candidate; producer self-approval is forbidden.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

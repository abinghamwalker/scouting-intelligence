# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R6`
- objective: Complete the preserved partial R5 23-root closure by adopting the accepted reversible exact Decimal struct only for non-coverage Decimal fields while retaining the exact predicate ledger and 29-row adversarial matrix.
- disposition: `IMPLEMENTED_FOR_INDEPENDENT_REVIEW`

## Files changed

- `src/scouting/contracts/wyscout_schema.py`
- `tests/contracts/test_w04_wyscout_schema_closure.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R6.md`

## Summary

- Verified all nine R6 fixed bindings before editing; the preserved partial R5 schema/test bytes were exact.
- Replaced every non-coverage logical Decimal projection formerly emitted as scalar `DECIMAL128(22,18)` with `EXACT_DECIMAL128_WITH_EXPONENT` and its exact ordered, non-null children: `value: DECIMAL128(22,18)`, `exponent: INT8`, and `negative_zero: BOOL`.
- Kept every `GoldCoverageDimension.coverage` and `GoldCoverage.coverage_overall` occurrence on scalar UTF-8 with `CANONICAL_DECIMAL_UTF8`.
- Updated canonical descriptor validation, forward/inverse declarative content, recursive descriptor instantiation, physical fixture projection, valid-model projection, Decimal path audits, and exact-schema assertions for the accepted struct.
- Added descriptor-owned executable vectors for source scales 0 and 18, positive exponent, significant trailing zeros, and signed zero. Each vector passed exact inverse logical JSON-byte equality through the accepted `SILVER_ACTION` descriptor.
- Preserved the partial-R5 56-binding runtime ledger, zero-omission direct-field AST audit, exact operations/operands/material constants, eight external predicates, 29 strict rows, frozen per-root cardinalities, seven tagged arms, five raw-kind states, distinct Bronze shapes, and SilverAction 0/1/2-position plus 0/18-scale/null-unmapped variants.
- Changed no logical model, root, logical field, feature, population, dependency, authority, digest meaning/formula, serializer implementation, aggregate, or product bytes.

## Tests run

- command: `shasum -a 256` over all nine R6 fixed bindings before editing
  - exit status: `0`
  - result: all exact, including partial R5 schema `e86d8de7...`, partial R5 test `7133e736...`, accepted formats `2dfdf367...`, accepted formats test `ba38c5a6...`, master acceptance `2ef88050...`, R5 oracle `a3f15f92...`, and oracle return `b09297fb...`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py` before editing
  - exit status: `1`
  - result: `27 passed, 1 failed`; reproduced the expected source-scale-0 scalar-decimal inverse mismatch and performed no write
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py` after implementation
  - exit status: `0`
  - result: `36 passed in 10.90s`
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
  - result: `591 passed in 123.77s`
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `179 passed in 3.91s`
- command: `uv run bandit -q -r src/scouting/contracts/wyscout_schema.py`
  - initial sandbox exit status: `2`
  - initial result: uv cache `.git` read denied before Bandit ran
  - identical approved read-boundary exit status: `0`
  - result: no findings
- command: `uv run lint-imports`
  - initial sandbox exit status: `2`
  - initial result: uv cache `.git` read denied before import-linter ran
  - identical approved read-boundary exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 controls; branch `main`; zero configured remotes

## Artifacts/evidence

- candidate schema SHA-256: `bbef5823bf1635d08362a3ee0a0876e2ac1ec04c2c502d4e67c61a4350ee7a71`
- candidate schema-test SHA-256: `dd8d66a1831ff7dfbd4a90c745607572a8c00358af4770d85e3e7ca115f3e500`
- accepted storage implementation retained SHA-256: `2dfdf3675a47f6c2b53478857de1af27aebecb85def8f0701e6ef86c65fafcc9`
- accepted storage test retained SHA-256: `ba38c5a66f41aee8ef2b998f4622c71ec30f3b8861d7ef07d8540d001b0bee89`
- runtime-predicate ledger: 56 reachable bindings, zero direct-field omissions; frozen oracle ledger SHA-256 `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`
- projection census: 30 non-coverage logical Decimal paths use exact outer structs with 30 `decimal128(22,18)` `value` children; six reachable coverage paths remain canonical UTF-8; 12 descriptors and 11 JSON-only roots remain exact
- strict model matrix: 29 rows with cardinality vector `[2,5,7,1,1,1,1,3,2,2,2,2]`
- derived canonical root-content SHA-256 values:
  - `BRONZE_KNOWN_RECORD`: `b2ffeddf98dc7abe1a69b423f3ddb49ed23c1547ec200c82ce0600afadeb5281`
  - `BRONZE_REJECTED_RECORD`: `93590613302d30ddaae70816d9fad4aa62ec2cdb2544445b1ecbebfae9d3d20b`
  - `BRONZE_REJECTED_FIELD`: `e61d5cb9ee93b89627cb25faf85ccc0915838e1c7428b9f7c70cffa4fe2eb914`
  - `SILVER_COMPETITION`: `3e5f6b5f6fe233d5baeecbb747d6b464694b2a6222913cdbdb05b3d265de5a71`
  - `SILVER_TEAM`: `109973956725cb6fc480f1d3e88780f70da384966a6792fd9b4d8ad97d5c75b1`
  - `SILVER_PLAYER`: `bf9b90da0d046a057e3a687fdb692d9c2ec354c10637813a960c755f8d5c62e9`
  - `SILVER_MATCH`: `3832125dc85c03b22d9f63acc620040b36c0d669e34b0b603dc6fb88eb5baeab`
  - `SILVER_ACTION`: `700d2562371920ccb436a91e94bb7ca04ef10ab2c208267e36b44a795e351ad4`
  - `SILVER_LINEUP_STINT`: `175749c7082d74d2f60885695895ba425dfcf20fc6739c48b1bb7df6988cea76`
  - `SILVER_POSSESSION`: `c1257820505342a9578710fa7468e692ef4d4b06720ea04fa8ff04aacd7bf77b`
  - `SILVER_PLAYER_MATCH_FACT`: `95b0be74e91bf0672b0f84ba79fb67ca56c1860afc0137fcd25be8cba1a464d1`
  - `GOLD_PLAYER_WINDOW`: `8305d419dd0eac8b3d69b51c7352985e346967a8bb9d860b6ca9a4088759e9da`
  - `LAYER_MANIFEST`: `0b57002f1367389b1ea098bf1cb0ccea0f815b49a42f7870efd8ad799bb17c07`
  - `TEMPORAL_BOUNDARY_RECEIPT`: `f11bd3626288059858919ad156fd64d314bd9d08b5b4c7126d736dd6a26984b7`
  - `REBUILD_INVOCATION_RECEIPT`: `c4c53e35738c7c1c0f6bde846a88b4e9852c67b9e8be126e57e5b2186aa08577`
  - `ENTRYPOINT_SOURCE_RESULT`: `3693f0227b20f303d02e037de5464c93ec4591f161fd7d93f138b25d63a4dfa6`
  - `COMPONENT_PROOF_RESULT`: `54f2f083553d767dbba9e6b67cb891b93a19b4c1b555f78a3da99160ad85f9c8`
  - `PRE_BUILD_ADMISSION_RESULT`: `87e5ed0738a70f028455d021a9337b96a4bdeba1d4e1c136217b17e82adfcdbf`
  - `REBUILD_RECEIPT_SUMMARY`: `54cef765f53e29b582419d2940516aafe2cbdc0feaac89fa8535a74b32f8e512`
  - `LAYER_MANIFEST_SUMMARY`: `985cdec740bf36d4cd0f6cd1125649131d11cc40109273851e8b2b7d79748817`
  - `FINAL_RECHECK_RESULT`: `f30a40867b12a4191d9c58ee60d619c3044a17d840a87dbe2ee73d476d1100c1`
  - `POST_BUILD_ID_REBUILD_RESULT`: `cbb3ea4ae8d343cbf4203dde3020b80047fc362cf9925421219ea69aa360b521`
  - `CHILD_RESULT_ENVELOPE`: `cbcb2cd027a4f82270b39ce320dfbbe2a03b63940e0a4854a5468738ef77af75`

## Risks

- No known residual implementation risk within the R6 boundary.
- The candidate is not self-approved; fresh independent review and master acceptance remain required.

## Follow-up items

- Fresh report-only independent review of the exact candidate hashes, followed by master reproduction and acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no serializer, aggregate, product, provider/network, cloud, container, hosted-CI, deployment, publication, credential, secret, or cost action: confirmed

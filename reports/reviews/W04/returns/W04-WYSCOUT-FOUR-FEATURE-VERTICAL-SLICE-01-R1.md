# Subagent return

## Task

- task_id: `W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-01-R1`
- objective: Implement and verify the exact accepted one-match Wyscout v5 raw-to-Gold vertical slice, complete layer manifests, temporal-boundary receipt, invocation receipt, isolated rebuild child, and adversarial local-only publication evidence.

## Files changed

- `src/scouting/data_products/wyscout/__init__.py` — `93efbee9739a38cb1c19e43013263fab4e73d0e839117f150464f23c1f430a08`
- `src/scouting/data_products/wyscout/bronze.py` — `672f2c88c6e43b154fd7e26710f5a3ba9d7712441a34d87397e926f90556cf36`
- `src/scouting/data_products/wyscout/actions.py` — `34c2ef74b564713c4f0255574d071453aa1ef5d6eb8cb4df5813aa6b62b57087`
- `src/scouting/data_products/wyscout/lineups.py` — `4c90c3a97b80cacea5046b945b797d6103c05888fca2dbbecf72c7bd49495b87`
- `src/scouting/data_products/wyscout/possessions.py` — `197a6883c03c7e7ea26854c75aa3813d5f606cefed396984e7d4f95593f30e84`
- `src/scouting/data_products/wyscout/player_match.py` — `784d6a50d6b2f455ed749839814a4c44e79895cd5094be1b2ab6f1ac3e6a75fd`
- `src/scouting/data_products/wyscout/silver_manifest.py` — `56628bb9b5b4595f429a487383f35bb659a60728537abad419474417d20c423a`
- `src/scouting/data_products/wyscout/gold.py` — `176495ded91497eca4ae8234889a7079d871eb65180b12fb0570cae4a62d4c04`
- `src/scouting/data_products/wyscout/temporal_boundary.py` — `c6a18363799cd714b38829412a0c5acda1fddd3b7c017e5135d6e8e41c1c2478`
- `src/scouting/data_products/wyscout/rebuild.py` — `b5e9c5a2e37d3c3190e26496b78fca7deab5f31779d79ecea34113e920f74e55`
- `scripts/rebuild_wyscout_v5.py` — `82d7a22cc9d48bca19e0f4a6d05f60995f7486df829585fa7bf0b9ab7434ba99`
- `tests/e2e/test_w04_wyscout_vertical_slice.py` — `5ce8de532124869eb7e88c55a5504db4d153222525cfa46eb897dc9232a4b83c`
- `tests/security/test_w04_wyscout_vertical_slice_publication.py` — `59e1f8837313690d38132442f789aa4ab4994291e2ef7455705347c1215d2e3e`
- `reports/reviews/W04/returns/W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-01-R1.md`

## Summary

- Reverified the immutable selected match and complete 901-plus-867 Action population using only accepted source, completion-index, identity, season/lineup, schema, aggregate, and runtime authorities.
- Emitted exactly 1,768 Bronze known Action rows and 3,544 schema-authorized rejected fields: 1,768 `$.eventName`, 1,768 `$.subEventName`, and eight failed `$.subEventId` transforms. Complete raw evidence remains losslessly retained; no zero-row, rejected-record, entity, provider-possession, or fifth-feature product is emitted.
- Built and immediately reverified exactly thirteen checked Silver Actions, the accepted one right-censored lineup stint, two checked complete possession groups, one checked player-match fact, and one checked Gold row with exact feature vector `(2,2,1,2)` and research-only reason `RIGHT_CENSORED_OR_UNCERTAIN`.
- Mechanically instantiated every Arrow projection through `w04_parquet_projection_content`, consumed the accepted nested descriptor-owned key paths through `w04_physical_primary_key_paths`, and required canonical ordering, lossless logical row reproduction, exact Decimal exponent/signed-zero projection, physical readback, and semantic digest equality.
- Published seven nonempty products before three checked complete manifests through the sidecar-free staged publisher. Exact product row counts are `[1768,3544,13,1,2,1,1]`; manifest entry counts are `[2,4,1]`; parent manifest chain is `()`, `(BRONZE)`, `(SILVER)`.
- Published one strict temporal-boundary receipt and one ordered invocation receipt only after full manifest/product/temporal readback closure. The upstream `validate_receipt_closure` legacy stop at `GoldSchemaAuthorityUnavailableError` is retained as an independent prefix check; the packet-authorized local closure completes the now-accepted Gold descriptor validation without changing digest meaning or formula.
- Implemented the frozen `python -S -B` rebuild child with exact-root stdlib bootstrap, closed-envelope/source/result descriptor validation, real retained clocks, framed result, complete code/environment/resource/PYC/code-manifest recheck before every atomic publication, and final retained recheck.
- Isolated smoke PASS build: `94dab66adfd75f8ff59000ab7c24d2e8811f517d12402fe7c5b9280fccee1e93`; exact run receipt path ends in `12345678-1234-4123-8123-123456789abc.receipt.json`.

## Tests run

- command: `UV_CACHE_DIR=/tmp/w04-vertical-slice-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check src/scouting/data_products/wyscout scripts/rebuild_wyscout_v5.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `13 files already formatted`
- command: `UV_CACHE_DIR=/tmp/w04-vertical-slice-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check src/scouting/data_products/wyscout scripts/rebuild_wyscout_v5.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `All checks passed`
- command: `UV_CACHE_DIR=/tmp/w04-vertical-slice-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync mypy src/scouting/data_products/wyscout scripts/rebuild_wyscout_v5.py`
  - exit status: `0`
  - result: `Success: no issues found in 11 source files`
- command: focused isolated determinism/security pytest roster for the two new test modules
  - exit status: `0`
  - result: `20 passed in 1410.30s (0:23:30)`; three genuine complete rebuilds, two same-run isolated mirrors, one different-run replay.
- command: `UV_CACHE_DIR=/tmp/w04-vertical-slice-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_vertical_slice_context.py tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `734 passed in 1473.04s (0:24:33)`
- command: `UV_CACHE_DIR=/tmp/w04-vertical-slice-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync bandit -q -r src/scouting/data_products/wyscout scripts/rebuild_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `UV_CACHE_DIR=/tmp/w04-vertical-slice-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `UV_CACHE_DIR=/tmp/w04-vertical-slice-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `status: PASS`, zero remotes, main branch, no hosted CI/container/deployment/external-service boundary violations.

## Artifacts/evidence

- Accepted nested physical primary-key authority: `reports/verification/W04/wyscout-nested-physical-primary-key-R1-master-acceptance.md`, SHA-256 `5d346c183ac97078a3c9bd2ebe8373ae68ca491487f3ff5ad3403d623cced9ec`.
- Independent isolated rebuild roots were pytest-owned temporary directories only. Complete no-follow recursive inventories of the exact real working, manifest, and run output roots were identical before and after all three rebuilds.
- Same invocation and run ID reproduced identical product, manifest, boundary-receipt, and invocation-receipt bytes across two independent exact-root mirrors. Different run ID retained identical product/manifest bytes and produced distinct run-scoped receipts.
- Adversarial evidence covers source/build/path/root/link/mode/network/provider/publication, temporal/manifest/receipt closure mutation, `-S -B` child bootstrap, and repository/component/resource/count/PYC/code-manifest retained-recheck drift.

## Risks

- Performance: complete nested lineage and independent contract reconstruction are intentionally expensive; the three-rebuild determinism fixture takes about 23–25 minutes. This is bounded test/runtime cost, not nondeterminism or an external wait.
- The existing upstream receipt validator still contains its historical explicit Gold-schema-unavailable terminal exception. The owned closure calls it for its full prefix validation and then completes the exact accepted descriptor-owned Gold readback. This bounded compatibility bridge should be removable when the upstream helper is separately advanced; current logical contracts and digest semantics are unchanged.
- Retained operational repository PYC/cache evidence was not cleaned, deleted, or modified intentionally. All final gates used `PYTHONDONTWRITEBYTECODE=1`; pytest used `-p no:cacheprovider`; the child classifies and requires exact pre/post PYC inventory equality.

## Follow-up items

- Independent review and master acceptance of this producer packet.

## Scope confirmation

- no Git operations: confirmed; the producer performed no Git operation or checkpoint.
- no unauthorised dependency or lockfile changes: confirmed; no dependency, provider, network, credential, cloud, deployment, publication, `pyproject.toml`, or `uv.lock` change.
- no edits outside `allowed_paths`: confirmed for producer edits; all implementation/test/report edits are within the packet roster. Isolated publications and UV cache used pytest-owned temporary roots and `/tmp`. Pre-existing/retained operational cache evidence was preserved without cleanup.

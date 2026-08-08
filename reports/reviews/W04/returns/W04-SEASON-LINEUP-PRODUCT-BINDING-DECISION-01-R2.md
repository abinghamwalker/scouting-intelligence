# Subagent return

## Task

- task_id: `W04-SEASON-LINEUP-PRODUCT-BINDING-DECISION-01-R2`
- objective: Replace three permanent repository product-absence assertions with progression-safe, side-effect-free authority/preimage loading tests while preserving every frozen non-test byte.

## Files changed

- `tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
- `tests/contracts/test_w04_wyscout_build_product_authority.py`
- `tests/contracts/test_w04_r21_control_preimages.py`
- `reports/reviews/W04/returns/W04-SEASON-LINEUP-PRODUCT-BINDING-DECISION-01-R2.md`

## Summary

- Replaced each unconditional `all(not destination.exists())` assertion with a before/after destination-state snapshot around exact authority or preimage loading. Real repository destinations may now be absent or present without affecting authority/preimage validation.
- Added writer-call tripwires for write-capable `Path.open` modes and path mutation/write methods. Each authority/preimage load proves it makes no writer call and cannot create, delete, rename, replace, touch, link, or alter a destination.
- Added isolated `tmp_path` progression coverage to all three modules for both wholly absent simulated destinations and a pre-existing simulated product or manifest containing exact sentinel bytes. No real product root is created by these tests.
- Retained explicit control-plane-only claims: both authorities continue to grant no product-byte permission, their lifecycle state is independent of product existence, the build authority continues to prohibit product writes/publication, and both R21 preimages remain descriptor/control-plane-only.
- Added no skip, xfail, environment flag, future task ID, placeholder gate path, dependency, runtime behavior, or product implementation.
- Preserved the live `REWORK` review and all authority, config, runtime, source, data, and prior evidence bytes.

## Tests run

- command: `uv run ruff format --check tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: `3 files already formatted`
- command: `uv run ruff check tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: `Success: no issues found in 3 source files`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_control_preimages.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `169 passed in 3.72s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25 checks, zero configured remotes, active `main`, local push guard active, Python `3.12.12`, one root uv project, no hosted CI/deployment, no containers, and no external service dependency.

## Artifacts/evidence

- correction authority unchanged: SHA-256 `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e`
- build authority unchanged: SHA-256 `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`
- failed review unchanged: SHA-256 `431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba`; embedded record SHA-256 `b1708640631732f304f6c07455ee1530ae0ef800a70276d29fd34b46fc484e3d`
- failed reviewer return unchanged: SHA-256 `8218de5bb7e38114204d8c5a82586ff0718887c3ec3a2a682b216f367d91b547`
- season/lineup authority test: before `0b5b933575f22451b5474323188619acec659c7291262c2e457086319fe93e29`; after `3a4ed66082d16cf55a87921a742aea30f5600ad538f2664d0a65fe5be2b9e21f`
- build/product authority test: before `94cafedb2c4d0e50aecebb8a52ffc6666f2f37607d14d7155f25a0d5aea18ed8`; after `12d7379b7594caaea2aed508fd1444cfa307d1911d8d12fb52222d050c0fc73b`
- R21 control-preimages test: before `b2bccb03e59c60a8d61439ea938e2da0fbb8a2bba2dcf77ff3549f2aabb54e53`; after `6ae725e379a33cd0785b346fe4ddcdca3fdc296ff24a1f78697202834e7d0df6`
- product-contract preimage unchanged: SHA-256 `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
- schema-bundle preimage unchanged: SHA-256 `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`

## Risks

- No residual progression defect was found in the three packet-owned permanent modules. Fresh independent review and master acceptance remain required before downstream implementation.

## Follow-up items

- Dispatch a fresh independent R2 review by an agent other than this producer.

## Scope confirmation

- no Git operations: confirmed; none performed.
- no unauthorised dependency or lockfile changes: confirmed; none performed.
- no edits outside `allowed_paths`: confirmed; only the three authorized test modules and this R2 return changed.
- no delegation or self-approval: confirmed.
- no authority, review, config, runtime, data, provider/network, product-root, cloud, container, hosted CI, deployment, publication, or external action: confirmed.

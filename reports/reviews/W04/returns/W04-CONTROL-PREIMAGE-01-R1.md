# Subagent return

## Task

- task_id: `W04-CONTROL-PREIMAGE-01`
- objective: Materialize only the two accepted-R21 descriptor-only canonical JSON control preimages and their exhaustive focused contract test.

## Files changed

- `configs/schema/wyscout-v5-product-contract-preimage-v1.json`
- `configs/schema/wyscout-v5-schema-bundle-preimage-v1.json`
- `tests/contracts/test_w04_r21_control_preimages.py`
- `reports/reviews/W04/returns/W04-CONTROL-PREIMAGE-01-R1.md`

## Summary

- Materialized the product-contract preimage as canonical compact UTF-8 JSON with sorted object keys, explicit R21 array order, no insignificant whitespace, and exactly one terminal LF.
- Bound immutable R20 physical SHA-256 `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` and accepted R21 physical SHA-256 `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`.
- Product-contract cardinalities are exactly 17 ordered path templates, 10 ordered serializer-owner rows with each of the 17 roles owned once, two primary-key contracts, and five ordered manifest/receipt rows. Layer order, identity, and closed no-product policy are exact.
- Materialized the schema-bundle sibling preimage under the same canonical byte rules and byte-equal authority links. It has exactly 16 descriptors, identical dependency order, earlier-only dependency edges, the exact descriptor-only surface literal, and the typed unresolved feature placeholder with `concrete_value=null`.
- Implemented six exhaustive focused tests covering canonical/physical byte identity, pinned hashes, exact keys/IDs/hashes/cardinalities/order, unique ownership, primary keys, manifest/receipt equality, earlier-only descriptor edges, sibling DAG and either-sibling-first topological presentations, forbidden descendant/runtime values and edges, typed unresolved placeholder, and absence of every product destination root.
- Neither preimage contains its own digest, the sibling digest, a concrete feature digest, downstream authority digest, clock, root, host, absolute path, concrete build/run ID, product output, generated manifest/receipt, or mutable runtime observation. Neither depends on the other.
- No field v2, possession v2, feature authority, cross-authority final test, Bronze, Silver, Gold, serializer, manifest, receipt, build, model, or product path was implemented or created.

## Tests run

- command: shell preflight of complete repository/site `.pyc` inventory before any Python helper
  - exit status: `0`
  - result: `PASS`; 59 repository pycs plus 1,086 site pycs equals 1,145 total; 19 repository plus 131 site `__pycache__` directories equals 150; inventory SHA-256 `0ace64f09a0c3de3564355a72d8171c3fbd14d6f771b9c4e44c420582c8958f9`; all four allowed paths and all seven product destination roots were absent.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `2` in the restricted sandbox, then `0` when rerun with approved access to the existing local uv cache
  - result: final `PASS`; `6 passed in 0.07s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all 25 local-only and one-root-uv-project checks passed.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `1` on the first bounded quality pass, then `0` after an `apply_patch`-only formatting correction
  - result: final `PASS`; `1 file already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: `PASS`; all checks passed.
- command: final shell SHA-256, line/byte cardinality, product-destination, and complete postflight `.pyc` inventory checks
  - exit status: `0`
  - result: `PASS`; hashes/cardinalities and inventory evidence are recorded below; all seven product destination roots remain absent.

## Artifacts/evidence

- `configs/schema/wyscout-v5-product-contract-preimage-v1.json`
  - bytes: `5473`
  - lines: `1`
  - physical SHA-256: `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
  - canonical SHA-256: `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
  - cardinalities: `17 path_templates / 10 serializer_ownership / 2 primary_key_contracts / 5 manifest_receipt_templates`
- `configs/schema/wyscout-v5-schema-bundle-preimage-v1.json`
  - bytes: `6104`
  - lines: `1`
  - physical SHA-256: `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`
  - canonical SHA-256: `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`
  - cardinality: `16 descriptors`; all dependency edges target earlier descriptors.
- `tests/contracts/test_w04_r21_control_preimages.py`
  - bytes: `18992`
  - lines: `569`
  - physical SHA-256: `b2bccb03e59c60a8d61439ea938e2da0fbb8a2bba2dcf77ff3549f2aabb54e53`
- accepted authorities independently reproduced before editing:
  - R20 physical SHA-256: `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
  - R21 physical SHA-256: `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`
  - R15 review physical SHA-256: `262fbf6f4cc3f239daebb8db69059d46125415647d58ffb432b630c44353c3aa`
- product destination inventory after final implementation edits:
  - absent: `data/working/wyscout/v5/bronze`
  - absent: `data/working/wyscout/v5/silver`
  - absent: `data/working/wyscout/v5/gold`
  - absent: `data/manifests/wyscout/v5/bronze`
  - absent: `data/manifests/wyscout/v5/silver`
  - absent: `data/manifests/wyscout/v5/gold`
  - absent: `runs/w04/wyscout-rebuild`
- final postflight bytecode inventory is byte-identical to preflight:
  - repository pycs: `59`
  - site pycs: `1086`
  - total pycs: `1145`
  - repository cache directories: `19`
  - site cache directories: `131`
  - total cache directories: `150`
  - inventory SHA-256: `0ace64f09a0c3de3564355a72d8171c3fbd14d6f771b9c4e44c420582c8958f9`

## Risks

- No residual implementation defect identified within the packet scope.
- These are inert control preimages only. They have not been independently reviewed or accepted, and they grant no field, possession, feature, data-product, serializer, build, model, or product authority.

## Follow-up items

- Independent master readback and `W04-CONTROL-PREIMAGE-REVIEW-01-R1`; no other follow-up is authorized by this return.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and `uv.lock` were not edited and no sync/install was run.
- no edits outside `allowed_paths`: confirmed; exactly the four packet-owned paths listed above were created or edited.

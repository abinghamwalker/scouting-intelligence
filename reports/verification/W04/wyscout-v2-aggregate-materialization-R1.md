# W04 Wyscout v2 aggregate materialization R1 — master verification

Date: 2026-08-02

## Decision

The producer packet is complete and ready for fresh independent review. The exact
acyclic aggregate graph was materialized in dependency order: the accepted
23-root implemented-schema bundle first, followed by the product contract bound
to that actual schema-bundle digest. No product, build, run, manifest, or receipt
instance was written.

## Fixed-input verification

All packet bindings reproduced before implementation:

- schema-closure master acceptance: `ff075ba6dcfed4bb1f9a10047bad0125ace3391edf5b885f3cde127feaf5f3e3`
- accepted schema implementation: `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4`
- accepted schema test: `5daaa32082cc0f82ed9b8b0b61cc06fe9d2db633cb15ed9c9837e491f2b9a5b8`
- schema independent review: `abdbe28dd2d7c57abc32a310db741e12af52c22172cd0039a6b9b16fa6dbcd35`
- build-product authority: `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`
- build-product acceptance: `9bcd9ef6f61b06f443a4d8f0d590db74559ee739976f285c41127da5ff1f5921`
- schema-bundle v1 physical predecessor: `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`
- product-contract v1 physical predecessor: `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`

## Accepted candidate identities

The logical identities hash the exact R20-canonical JSON body without a terminal
LF. The physical config files contain that body plus exactly one LF.

| Artifact | Logical SHA-256 | Physical SHA-256 |
| --- | --- | --- |
| schema bundle v2 | `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be` | `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45` |
| product contract v2 | `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0` | `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af` |

Candidate implementation hashes:

- `src/scouting/contracts/wyscout_aggregates.py`: `6cdbb9eaa7d18c5f07d42d6be33d91b014a34824610319f3e55cf5b383c07851`
- `scripts/materialize_wyscout_v5_contracts.py`: `f42ce353382b08171c4495e36c0db00d2ea558b4ef8ca081821b13c3e18a4481`
- `tests/contracts/test_w04_wyscout_v2_aggregates.py`: `6f44bea5569d95a21930f06031e0e78c7d789468d95b780c263f9be0506bc95e`

## Behaviour verified

- The schema object has exactly the frozen eight-key order, 23 implemented roots,
  exact root order, unique schema identities, reproduced root-content digests,
  and earlier-only closure edges.
- The product object has exactly the frozen ten-key order and binds the actual v2
  schema digest, exact completion-index/window authority, publication order, both
  receipt contracts, and the sole complete-LayerManifest semantic composition.
- Canonical validation rejects omissions, reordering, placeholders, predecessor
  digest substitution, swapped digests, forward edges, self-reference, receipt
  substitution, publication reordering, and extra keys.
- Materialization creates only absent owned files, rejects unsafe or unequal
  existing paths, checks stable single-link regular-file reads, and accepts exact
  bytes idempotently.

## Fresh gates

- `uv run ruff format --check ...`: PASS.
- `uv run ruff check ...`: PASS.
- `uv run mypy src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py`: PASS, 0 issues.
- `uv run python scripts/materialize_wyscout_v5_contracts.py --write`: PASS.
- `uv run python scripts/materialize_wyscout_v5_contracts.py --check`: PASS.
- focused aggregate suite: PASS, 17 tests in 34.26 seconds.
- aggregate/schema/build/product/cross-authority suite: PASS, 231 tests in 53.15 seconds.
- `uv run bandit -q -r ...`: PASS.
- `uv run lint-imports`: PASS, 3 contracts kept and 0 broken.
- `uv run python scripts/verify_local_only.py`: PASS, 25 checks and 0 failures.
- scoped `git diff --check`: PASS.

## Boundary

The implementation preserves the 25-key build projection and all logical digest
meanings/formulas. It adds no dependency, network/provider access, external
service, cloud/container/CI/deployment/publication path, product population, or
runtime output. Independent review and master acceptance remain required before
the aggregate gate is accepted.

# W05 training-serving parity independent review R1

## Verdict

**PASS.** No W05 P0/P1 reproduced. Fresh cross-layer probes prove exact training/reload, direct-scorer/single/batch/fresh-core, request replay, evidence-lineage, and six-family control-comparison parity. The registered selected artifact retained the same four SHA-256 values before and after every probe. No tuning, reselection, provider access, artifact mutation, or W06 protected evidence was used.

## Frozen authorities and feature/population parity

The sole selected feature tuple, in exact order, is:

1. `synthetic_progression_actions_per_90`
2. `synthetic_final_third_entries_per_90`
3. `synthetic_chance_creation_actions_per_90`
4. `synthetic_defensive_disruptions_per_90`
5. `synthetic_ball_retention_ratio`
6. `synthetic_aerial_involvements_per_90`

It is identical across the registry, candidate materialization, manifest, index vectors, scorer contributions, six-input explanations, and feature-schema evidence. Feature schema hash is `1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f`; registry digest is `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644`; taxonomy digest is `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`; configuration digest is `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`.

The fitting authority is `w05-synthetic-development-complete-rows-v1`, count 18, projection digest `60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086`. Its loaded UUID projection is the exact ascending sequence `20000000-0000-4000-8000-000000000001` through `...000018`; no alias, reorder, subset, or fallback was admitted. Candidate-universe ID/count/digest are `w05-synthetic-development-candidate-universe-v1`, 18, and `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

Selected artifact/model/index identities are:

- artifact `9a0d43c6-d177-51be-8280-3bf02bedbc99`;
- logical manifest `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`;
- model `w05-m0-role_aware_restriction-v1@v1`;
- index `w05-m0-role_aware_restriction-index-v1@v1`;
- lineage identity `e77de98a171447b8a3361161e5efbc8173909f933435f27ac99e0534c6d591c7`;
- shared serving core `m0-shared-core-v1`.

## Two-root training and reload proof

Two newly allocated `/private/tmp` roots were fitted once per family from the immutable authorities. For all six families, all four files were byte-identical between roots; canonical manifests, arrays, all 18 ranking digests, every all-candidate distance/contribution result, and scores were exact after reload. Both roots were removed after the proof.

| family | artifact UUID | manifest digest | array payload digest | precision@3 |
|---|---|---|---|---:|
| metadata_control | `5c3a6171-a333-5bd9-b500-82a0b24106f1` | `be1e17efdf4d614dc25bca9085b75d59144f8e18b34f313b94418b0e31ad5f6a` | `19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee` | `0.1111111111111111` |
| raw_euclidean_control | `09d3296a-0d5a-5892-bfdd-5820073fe792` | `b277d26404a7010b0c0bb7440daef20242e9575df64efaed0ffc317f21db2f68` | `3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36` | `0.3333333333333333` |
| robust_scaled_cosine | `e4ab4661-faf4-5065-b43d-0d8fe8ba3c7d` | `069beffefba0ead2fd8c55515f75fe98a65c1085ba64f32367ee09faa56830e2` | `ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc` | `1.0` |
| weighted_cosine | `33c7fd4b-21f6-52d7-be69-95277c0691b3` | `968f7f3b2d5b77578320851dccb00c7287e10bfcb39220ca8b9f9a022cbd12b8` | `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` | `1.0` |
| pca | `c648fc03-4eec-510c-bf41-0b50515c1f47` | `d3970a614859ae98e285e47c1b2473c60a1f8743f563e68c85e4f6aa53cab035` | `90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971` | `1.0` |
| role_aware_restriction | `9a0d43c6-d177-51be-8280-3bf02bedbc99` | `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9` | `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` | `1.0` |

PCA component and transformed-index descriptor digests were respectively `cba9973cb5dc04bf712517f5d7fb484b4e294e5e9c0ad4b8a895684fc61fd89b` and `40384470d2916e19b1d0c77a7eabdc79d1b3a4bd053f75fffecb6c4f3ebec698` in both roots, proving stable orientation and projection bytes.

The selected role-aware result `1.0` strictly exceeds metadata `0.1111111111111111` and raw Euclidean `0.3333333333333333` only on this one fixed constructed comparison. The score computation ran exactly once per fixed family; no search, retry, alternate parameter, threshold, weight, PCA count, seed, or candidate population was attempted.

## Direct, single, batch and replay parity

For query player `...000001`, accepted direct scoring, public single serving, one-item batch, repeated serving, and a separately constructed fresh core returned exactly:

| rank | candidate | distance | six contributions |
|---:|---|---:|---|
| 1 | `...000002` | `0.00013857118024163118` | `[-0.9988209902882081,0,0,0,0,-0.0010404385315502171]` |
| 2 | `...000003` | `0.000554708060777731` | `[-0.9990983827785352,0,0,0,0,-0.0003469091606869914]` |
| 3 | `...000004` | `0.0012485263821517822` | `[-0.9990983827785352,0,0,0,0,0.0003469091606869914]` |

The complete result JSON bytes were identical. Result digest is `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`; `m0_result_id` is `e77948a1-2987-514d-a585-cd54015e2152`; retrieval result/run IDs are `8a0c3594-0b40-572a-8a9a-aecaa0b6052e` and `332c42c4-6b0d-5fd5-b8aa-f09ae9ae501c`.

Sorted-exemplar mean scoring also matched direct scoring exactly, including all floats. Reversing valid constraint input order produced identical candidate geometry, states, and explanations, while retaining distinct order-sensitive request-bound IDs/digests. A normally valid changed request time produced distinct IDs in all three UUID domains. Thus semantic execution parity and canonical request identity both hold without collision.

Serving contains no feature transform or scoring arithmetic: it delegates ranking geometry once to `LoadedM0Artifact.score`. Exclusions, filter-permitted IDs, and the selected role restriction are converted only into scorer exclusions.

## Evidence, lineage, determinism and fail-closed attacks

The accepted result has exactly six dimension states and six explanation inputs per candidate, exact scorer contributions in manifest feature order, `resemblance_only`, LIMITED applicability, and limitations `synthetic_development_only` plus `no_recommendation_evidence`. Confidence is visible and nonranking.

Lineage hash is `c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491`, comprising exactly 18 `SOURCE_MANIFEST` and 18 per-row `FEATURE_SCHEMA` dependencies. Snapshot is `2025-01-03T00:00:00Z`; availability watermark and valid-from are `2025-01-04T00:00:00Z`. No fabricated model/index/taxonomy availability dependency exists.

Fresh attacks all failed closed:

- all 18 artifact/schema/taxonomy/configuration/fitting-population/candidate-universe/lineage/model/index request pins;
- query player, responsibilities, hard constraints, limit, cutoff, resolved-query digest, exclusion digest, and shared-core pins;
- all 17 independently re-signed manifest behavior/identity fields, plus re-signed candidate-universe content and configuration content;
- feature-row and source-dependency observed/available clocks independently placed exactly at cutoff and one second after cutoff (eight cases).

No substitution emitted a result or changed the registered artifact. The existing P2 preflight ordering—some normally typed semantic failures may read the already-authorized local artifact before rejecting without scorer/result/evidence—does not satisfy a W05 blocker test and does not affect parity.

## Registered artifact immutability

The following physical SHA-256 values were checked before and after every custom probe and were exact throughout:

- arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`;
- manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`;
- configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`;
- candidate universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Commands

- packet pytest command — exit 0, `75 passed in 1.34s`.
- packet Ruff command — exit 0, all checks passed.
- packet mypy command — exit 0, no issues in nine source files.
- `lint-imports` — exit 0, three contracts kept.
- `verify_local_only.py` — exit 0, PASS/no failures.
- `/private/tmp/w05_parity_probe.py` through the required `uv run --no-sync` environment — exit 0; all parity, replay, lineage, cutoff, pin, two-root, score, and cleanup assertions passed.
- `/private/tmp/w05_parity_resign_probe.py` through the required environment — exit 0; 19 independent re-signed substitutions rejected; temporary root removed.

## Development-only limitation

This PASS proves deterministic implementation parity and the declared fixed synthetic-development control comparison only. It is not W06/protected evaluation, robustness, calibration, provider or expert validation, transfer evidence, recruitment outcome/effectiveness, recommendation applicability, or production readiness.

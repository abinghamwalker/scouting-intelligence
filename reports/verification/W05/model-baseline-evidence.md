# W05 model and baseline evidence

This is a factual record of accepted W05 evidence, not a phase gate or a production-readiness claim.

## Frozen authorities

- Registry digest: `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644` (`configs/features/w05-m0-feature-registry-v1.json`).
- Feature-schema hash: `1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f`.
- Taxonomy digest: `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097` (`configs/roles/w05-football-responsibility-taxonomy-v1.json`).
- Configuration digest: `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a` (`runs/w05/m0-baseline-v1/configuration.json`).
- Fitting population: `w05-synthetic-development-complete-rows-v1`, count `18`, digest `60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086`.
- Query population: `w05-m0-development-queries-v1`, digest `1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c`.
- Candidate universe: `w05-synthetic-development-candidate-universe-v1`, count `18`, digest `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e` (`runs/w05/m0-baseline-v1/candidate-universe.json`).

## Selected fixed comparison

The selected family is `role_aware_restriction`: artifact `9a0d43c6-d177-51be-8280-3bf02bedbc99`, manifest digest `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`, model `w05-m0-role_aware_restriction-v1@v1`, and index `w05-m0-role_aware_restriction-index-v1@v1`. The result digest is `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`.

Its array payload digest is `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801`. Physical SHA-256 values are arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`, manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`, configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`, and candidate universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

Fixed synthetic-development scores are metadata control `0.1111111111111111`, raw Euclidean control `0.3333333333333333`, robust scaled cosine `1.0`, weighted cosine `1.0`, PCA `1.0`, and selected role-aware restriction `1.0`. This is a deterministic constructed synthetic comparison only: `resemblance_only`, not W06 evaluation, provider/expert validation, recruitment outcome, recommendation, or production evidence.

Sources: `orchestration/reviews/REVIEW-W05-MODEL-01-R6.yaml`, `reports/reviews/W05/w05-m0-model-independent-review-R2.md`, `orchestration/reviews/REVIEW-W05-PARITY-REVIEW-01-R1.yaml`, and `runs/w05/m0-baseline-v1/manifest.json`.

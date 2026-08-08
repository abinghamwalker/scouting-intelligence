# W07 scoring-path and accepted-identity parity

Status: **PASS**

W07 introduces no scorer. Retrieval calls the public `serve_m0_request` entry point;
comparison calls the public `serve_m0_batch` entry point. Both use the same loaded W05
`LoadedM0Artifact.score` path. W07 composition only validates identities and zips
returned evidence rows to stable synthetic labels; it performs no distance, ranking,
contribution, confidence or score arithmetic.

Executable spies prove direct and batch calls reach the same accepted scorer, preserve
byte-identical request/result payloads and retain the accepted result digest. The four
physical W05 artifact files were hashed before and after W07 requests and remained
unchanged.

## Accepted authority

| Identity | Accepted value |
|---|---|
| Selected family | `role_aware_restriction` |
| Feature registry digest | `c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644` |
| Exact-four W04 schema | `cf8847f2b1f70ebf293ce90e48817e80a4e47b78316079bd88e8c2a80bc08127` |
| Synthetic-development schema | `1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f` |
| Taxonomy digest | `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097` |
| Configuration digest | `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a` |
| Artifact | `9a0d43c6-d177-51be-8280-3bf02bedbc99` |
| Manifest digest | `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9` |
| Result digest | `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e` |
| Lineage hash | `c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491` |

The accepted W04 descriptive bridge remains exactly `action_count=2`,
`coordinate_known_action_count=2`, `match_count=1` and
`resolved_possession_action_count=2`. Elapsed minutes, rates and per-90 remain
`SUPPRESSED` and are never substituted.

Sources: `tests/integration/test_w07_local_evidence_app.py`,
`tests/integration/test_w05_m0_serving.py`, `tests/e2e/test_w05_m0_retrieval.py`,
`reports/verification/W05/training-serving-parity-report.md` and
`reports/reviews/W07/w07-application-independent-review-R1.md`.

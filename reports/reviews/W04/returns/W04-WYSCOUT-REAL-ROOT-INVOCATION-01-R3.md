# Subagent return

## Task

- task_id: `W04-WYSCOUT-REAL-ROOT-INVOCATION-01`
- revision: `R3`
- objective: Correct only the R2 outer transport-digest evidence predicate and
  obtain two additional fully wrapper-verified complete real-root invocations.

## Files changed

- `reports/verification/W04/wyscout-real-root-invocation-R3-master-acceptance.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-REAL-ROOT-INVOCATION-01-R3.md`
- additive ignored local outputs under the packet-authorised code-manifest,
  product, manifest, staging, and `runs/w04/wyscout-rebuild` paths

## Summary

- Retained R2 as core-complete/wrapper-unverified negative evidence.
- Corrected only the master-owned `/private/tmp` wrapper predicate to compare the
  returned post-uv transport digest against the exact mechanically constructed
  30-key child environment. No accepted launch or repository byte changed.
- Executed two additional wrapper-exit-0 `COMPLETE` invocations with distinct
  control/admission/rebuild UUIDv4 families.
- Retained one sandbox-denied pre-admission run-2 attempt as an empty control
  prefix and relaunched the unchanged wrapper with access to the existing local
  uv cache.
- Guard-read all three successful receipt families, all three layer manifests,
  seven Parquet products, all temporal receipts, the accepted and retained-old
  code manifests, and all 14 runtime prefixes. Reproduced the strict build
  projection/inverse, exact logical JSON bytes, physical/semantic digests,
  lineage, row counts, and cross-run stability.

## Tests run

- `zsh /private/tmp/w04-real-root-launch.zsh R3_VERIFIED_RUN_1`
  - exit status: `0`
  - result: `COMPLETE`; control `be5ce373-3287-49c9-b834-29c27f419afc`,
    admission `8b183c33-2c80-426c-a90b-07d14ed45732`, rebuild
    `d39ee14e-e1ff-4235-ae73-9169308a2b28`
- initial sandboxed `zsh /private/tmp/w04-real-root-launch.zsh R3_VERIFIED_RUN_2`
  - exit status: `70`
  - result: local uv-cache read denied before admission; no status line; retained
    empty control prefix `750827a1-d1cd-4d33-8118-5ac4d4e873e8`
- approved local-cache rerun of the unchanged R3 run-2 command
  - exit status: `0`
  - result: `COMPLETE`; control `5d1a224b-f833-4524-9ae7-6016c553b0b0`,
    admission `245a4003-ffce-4792-bb10-d7a91f68236c`, rebuild
    `5a802af6-6187-4374-ab8a-1bf64b8669ab`
- `uv run --offline python -B /private/tmp/w04-r3-master-readback.py`
  - exit status: `0`
  - result: `PASS`; exact three-run invocation/receipt closure, seven product
    readbacks, ordered row counts `[1768,3544,13,1,2,1,1]`, logical-byte and
    semantic reproduction, stable manifests/products, 14 empty runtime prefixes
- shell retained-root and PYC census
  - exit status: `0` for all census/digest/compare operations
  - result: additive retained-root inventory `174 -> 272` rows; site PYC `1218`
    and repository PYC `132` rows byte-identical pre/post
- `/private/tmp/w04-r3-producer-gate.zsh`
  - first exit status: `1` after all preceding checks passed
  - result: locked offline sync `83` resolved/`82` audited; Ruff, mypy, exact
    `286 passed in 1573.05s`, Bandit, import-linter and Git guard passed; local-only
    correctly rejected two current-host path literals in the retained R2 YAML
- bounded master-only orchestration correction and tail rerun
  - exit status: `0`
  - result: replaced only those two structured-config literals with digest-bound
    identity tokens; local-only `25/25` passed, diff-check passed, remotes empty,
    and retained-root/PYC post-gate censuses remained byte-identical

## Artifacts/evidence

- R3 packet SHA-256:
  `836fdbf323a725adf11f24a47198a1789c37a9c2cb093465db71e10c72c6c831`
- corrected retained R2 packet SHA-256:
  `207886a6c14bdb7415d96d532c073b1565d94f5188e8046a69f980f5619ac757`
- corrected wrapper SHA-256:
  `e5b557790d02c41f457c683d59756509c48df2b15854c4c6d6914feec875d537`
- master readback SHA-256:
  `760840e8113113db60c6228e6aacb90d0351bb7b5f0f793dd1002ece23b25e4b`
- accepted build/code manifest:
  `b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79` /
  `c94e650146a982174820ba694a2dcd1b20dc6648426527213bf2e6de09861c2c`
- R3 receipt SHA-256 values:
  `63b645423ca72edcb2055814293a0024d549bd01e45005136ff3730416530f10`,
  `db8501cf9c644644ca5ba614e87fea43d3d3c0568fcad405e028fb6d2ceace18`
- R3 boundary SHA-256 values:
  `a077a8a5385c633d1a6911717b843e2b7d60f5a6ac025136057ae810d9c595c2`,
  `16488eb7ad9d6021e4f442455427a6c2d16e3db21a336a60f515cfbd5b08ab00`
- retained-root post census:
  `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c`
- PYC census hashes:
  `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`,
  `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`

## Risks

- Fresh independent R3 review and master adjudication remain required.
- The retained-root census changes by design because successful and failed
  invocation evidence is additive. Product/manifests are content-addressed and
  independently verified byte-stable.

## Follow-up items

- Fresh independent R3 review; no producer-side follow-up.

## Scope confirmation

- no Git operations: confirmed
- no dependency or lockfile changes: confirmed
- no edits outside packet-authorised repository paths: confirmed; the corrected
  wrapper, audit, and census evidence are master-owned `/private/tmp` artifacts
- the master separately corrected and rebound only the two affected orchestration
  packet digests after the producer gate; this was not a producer/subagent edit
- no cleanup, reset, stash, overwrite, deployment, publication, or remote access:
  confirmed

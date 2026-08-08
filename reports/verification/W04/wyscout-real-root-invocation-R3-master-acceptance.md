# W04 Wyscout real-root invocation R3 master acceptance

- Date: `2026-08-03`
- Task: `W04-WYSCOUT-REAL-ROOT-INVOCATION-01-R3`
- Decision: **MASTER_ACCEPTED_AS_RETAINED_CHAIN_EVIDENCE; SUPERSEDED_FOR_FINAL_W04_CLOSURE**
- Accepted build: `b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79`
- Accepted code manifest: `c94e650146a982174820ba694a2dcd1b20dc6648426527213bf2e6de09861c2c`

## Bounded R2 evidence-wrapper correction

R2 completed the accepted launcher and rebuild core and immutably published its
code manifest, build, seven products, three layer manifests, invocation receipt,
and temporal-boundary receipt. The additional master evidence wrapper alone then
exited `1`: it compared the returned dynamic post-uv child transport digest to the
fixed normalized environment-authority digest. R2 remains retained as
core-complete/wrapper-unverified evidence and is not counted as an R3 verification
run.

R3 corrected only that outer predicate. The wrapper now mechanically constructs
the exact 30-key post-uv child environment, including venv-prefixed `PATH`,
`UV_RUN_RECURSION_DEPTH=1`, the fresh control prefix, and the inherited source
descriptor. It hashes those canonical JSON bytes and compares the returned
dynamic transport digest to that value. The fixed normalized environment digest
`d832fe0a0e8249465b1c77f135a5b8da07c100fee0586127cdf8a4099133eaf1`
remains bound independently in the accepted bootstrap tuple. No launcher,
admission, rebuild, logical contract, resource, product, manifest, digest formula,
dependency, source authority, or data-rights byte changed.

One initial R3 run-2 command was sandbox-denied before admission because `uv`
could not read its existing local cache. It emitted no status and left only empty
control prefix `750827a1-d1cd-4d33-8118-5ac4d4e873e8`; it is retained as negative
procedural evidence and does not count as a verification run. The unchanged
wrapper was then relaunched with read access to the existing local cache.

## Two additional fully wrapper-verified runs

| Binding | R3 verified run 1 | R3 verified run 2 |
| --- | --- | --- |
| control run ID | `be5ce373-3287-49c9-b834-29c27f419afc` | `5d1a224b-f833-4524-9ae7-6016c553b0b0` |
| admission run ID | `8b183c33-2c80-426c-a90b-07d14ed45732` | `245a4003-ffce-4792-bb10-d7a91f68236c` |
| rebuild run ID | `d39ee14e-e1ff-4235-ae73-9169308a2b28` | `5a802af6-6187-4374-ab8a-1bf64b8669ab` |
| outer transport SHA-256 | `573c7080a1b84759d6c4b80c73553cf298ae7b9d3ed664f94f4e9a477ed8a1fd` | `d17d0c6177cb9ad1921a62fcc70ba163ec5113f1bf6ea88a903a75cf77db5671` |
| rebuild receipt SHA-256 | `63b645423ca72edcb2055814293a0024d549bd01e45005136ff3730416530f10` | `db8501cf9c644644ca5ba614e87fea43d3d3c0568fcad405e028fb6d2ceace18` |
| boundary receipt SHA-256 | `a077a8a5385c633d1a6911717b843e2b7d60f5a6ac025136057ae810d9c595c2` | `16488eb7ad9d6021e4f442455427a6c2d16e3db21a336a60f515cfbd5b08ab00` |
| wrapper result | `COMPLETE`, exit `0` | `COMPLETE`, exit `0` |

Both returned the fixed build and code manifest. Their control, admission,
rebuild, receipt, and boundary paths are distinct UUIDv4-scoped families. The
R2 retained family remains build-identical with rebuild receipt
`a70a977f76f775e31f0ae3d9d7c28c51df99490733ebe76f20972107402d31cb`
and boundary receipt
`521581b50ca008a6c6e5ef6a7886018337ea904e896b85d9980d35a42f204f53`.

## Guarded cross-run readback

The master guard-read every published byte through
`/private/tmp/w04-r3-master-readback.py`, SHA-256
`760840e8113113db60c6228e6aacb90d0351bb7b5f0f793dd1002ece23b25e4b`.
The script strictly validated all three invocation receipts and their strict
projection/invocation inverses, reopened all three boundary receipts, reproduced
the sole build hash, guard-read all three canonical manifests, reopened all seven
Parquet products with their accepted root-owned descriptors, projected every
physical row back to canonical logical JSON bytes, and recomputed each semantic
digest. Result: **PASS**.

| Product role | Rows | Physical SHA-256 | Semantic SHA-256 | Reconstructed logical-byte SHA-256 |
| --- | ---: | --- | --- | --- |
| `BRONZE_KNOWN_RECORD` | 1768 | `e48b203df0d2b83d53af9340cc76ec42a0bb138b5e9608284718d9f6854e9aaf` | `4186f51a8694be1ca4699baf0f3c77e24b2206cc63f18bb7954074cc186d76ca` | `749e51f850372dfd610ffaf2037c8520e94282bca2eeac20f7ef582181cc7faa` |
| `BRONZE_REJECTED_FIELD` | 3544 | `b2dc4e9265edb79402b19b739be2167dd2bdcaea9afdf9c1b9304953d9f2278e` | `2d0d05c88e00aa2484215f691f9ce7233324e8f0dbd9ea98e86e16e385c08825` | `7f0a9a567ee81cbfe652422d09208679de8bc2a2f80a699b198a920c0d979384` |
| `SILVER_ACTION` | 13 | `89e9645d9715fc155f09a5dae14ac261233aa7599b8266cbcef6a0b5eb86f53a` | `9d98a59a82a45bf077e72dfdb26545d24f3e718d3c8266b085ec95a03bba22d3` | `e6d7e2d1abcd6cc4595b0453797ccd5bb22577c3ed384231eacc5aface27f3b9` |
| `SILVER_LINEUP_STINT` | 1 | `b05e1573cfee6cb3d2a44b675e72917dac70562af17e85494e2948934d15bda2` | `d5a83d1a820ec5197e18709b2ed966824c6edf836926cd8faddeab8617145c08` | `dbfb8c0befb5633d00191fd7680d90bd7af28c9df617ba1cc76442c2c0baac7b` |
| `SILVER_POSSESSION` | 2 | `a65461738eb21211cb9695af5bbdad9a28ea5f1280de2a3ae79559a555978878` | `bf1114a1d1b2b6325e3656aed297d5f3f7ec872b1485b47c65cb5c47a617417a` | `681f027ed5406f0e39b7c80bf25d5f093c64e111ef0df1fd62e4a717f30d9d5f` |
| `SILVER_PLAYER_MATCH_FACT` | 1 | `5b8bb0d0dcc1caf9709a1706041110ebadfd3ac14a590fefc4622cc5c41fa1da` | `a8db5735a2f0ec1ee37d46e9dc2985bb4d20b2ef08fc70acfc4e4eec38af5a0f` | `bd7c92d470bfb036a44057e014acd79d55aef4ed430086edb654e767327fb913` |
| `GOLD_PLAYER_WINDOW` | 1 | `6e49b4322c766352fdc427b8d35d73ddaed036d0bd19f1d65435fe3a72edcd17` | `f1751b4f1ff7911ad339fa1954cd5c88483fc09c733547dba87d7aa301c1bffa` | `ef6a57e33a9702f48496570a05fba7f70b7478eb25a30902b75bc9ad4b594cc6` |

The exact ordered row population is `[1768, 3544, 13, 1, 2, 1, 1]`.
The stable layer manifest hashes are Bronze
`abdc5d89fdac08638f4877f9a44dceb9356d789741bd93981cce4a9b6825d9c1`,
Silver `089673ff01edd7de7b6e5777958d19cbaffaa9f429b042ab4986746d80a7c36a`,
and Gold `08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068`.
All receipts bind that same immutable product/manifest set.

The accepted exact Decimal inverse was exercised on the real Silver products:
the ordered `value: decimal128(22,18)`, `exponent: int8`, `negative_zero: bool`
struct is strictly decoded, nonzero negative-zero flags are rejected by the
accepted inverse, the original exponent and signed zero are preserved, and every
reconstructed canonical logical JSON row reproduces the manifest semantic hash.
Coverage remains on `CANONICAL_DECIMAL_UTF8`.

## Retained-root and PYC evidence

- Pre-run `data/**` and `runs/**`: 174 census rows, SHA-256
  `b46c835ba721255c18b35f0076c40b0adcbdf92bd8625060597c9d02551534a4`.
- Post-run `data/**` and `runs/**`: 272 census rows, SHA-256
  `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c`.
  The additive difference is the retained R3 run/control/admission/receipt
  families and expected publication metadata; immutable content bindings above
  remain byte-identical.
- Selected site-packages PYC pre/post: 1,218 rows, byte-identical SHA-256
  `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`.
- Repository PYC pre/post: 132 rows, byte-identical SHA-256
  `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`.
- Launcher completion reported the same combined 1,350-row PYC authority digest
  `c083711fe51c3d79f46524c8365c583cac150d60d4d692fc29debc4680a1f731`
  for both R3 runs.
- Every one of the 14 retained control/admission/rebuild `runtime-pycache`
  prefixes, including all failed attempts, exists and is empty.
- The unaccepted pre-R10 code manifest
  `fb1bcca5772d71a0de2c116cd2539d1d2cd757554df8791dad8e0d952cf67083`
  remains present and digest-exact.

No data, run, failed prefix, product, manifest, or evidence was deleted, reset,
cleaned, stashed, restored, overwritten, deployed, or published externally.

## Fresh master gate and bounded orchestration rework

The master ran `/private/tmp/w04-r3-producer-gate.zsh` against the frozen R3
outputs. Locked offline sync resolved `83` packages and audited `82`; Ruff,
mypy, Bandit, import-linter, and the local Git guard passed; the exact six-file
population passed `286 passed in 1573.05s`.

The first local-only tail check then correctly rejected two absolute current-host
uv path literals in the retained R2 task-packet YAML. Those strings were evidence
configuration only, not runtime inputs. Under the standing bounded-correction
authority, the master replaced only those two YAML values with exact identity
tokens bound by the unchanged outer-environment digest; the literal paths remain
in human evidence and runtime observations. No runtime, product, manifest,
receipt, logical, digest-formula, or intended-output byte changed. The corrected
R2 packet SHA-256 is
`207886a6c14bdb7415d96d532c073b1565d94f5188e8046a69f980f5619ac757`;
the mechanically rebound R3 packet SHA-256 is
`836fdbf323a725adf11f24a47198a1789c37a9c2cb093465db71e10c72c6c831`.

The fresh local-only rerun passed all 25 checks with zero failures; `git diff
--check` passed and `git remote` remained empty. Complete post-gate retained-root,
site-PYC, and repository-PYC censuses were byte-identical to their post-run
snapshots: `272`, `1218`, and `132` rows with the same three hashes above.

## Disposition

Fresh independent R3 review completed with `PASS` and `P0/P1/P2 = 0/0/0`.
Its exact six-file gate passed `286 passed in 1586.84s (0:26:26)`; its fresh
local-only gate passed `25/25`; the retained-root, site-PYC and repository-PYC
inventories remained byte-identical. The independent review SHA-256 is
`74517a54520015bbeb179a921e93190a4dc07d5ae307a2ba735501a66a368ada`
and its mandatory return SHA-256 is
`eadd5f85e56b2a1a6fec1d48a32dc7a54f7f8993f9e0df513e5614d644f99767`.

R3 is therefore master-accepted for the exact frozen R3 packet and retained as
positive chain evidence. It is not the final W04 real-root authority. A later
master hierarchy readback found two bounded physical runtime-control defects
against the already-accepted effective R21/R20 authority: admission and launch
bound only the superseded 17-resource R20 subset rather than R21's exact ordered
30-resource roster, and `runtime_subset_digest` was populated with the full
installed-record closure digest rather than the final normalized loaded-owner
`R subset-of L` evidence. Those findings do not invalidate the truthful R3
execution or independent verdict, but they supersede R3 for final W04 closure.
The master has entered serial R11/R12 producer, fresh-review and master-acceptance
rework; two new real-root executions and a new independent review are mandatory
after those corrections. No R3 byte or retained run family is deleted or
rewritten.

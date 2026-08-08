# W04 identity-bundle runtime independent review R2

Date: 2026-07-31

Disposition: **PASS**

This fresh review examined the unchanged candidate fixed by
`W04-IDENTITY-BUNDLE-RUNTIME-REVIEW-01-R2` in an exclusive no-writer window. R1
is retained as invalidated chain-of-custody evidence and was not treated as an
acceptance. Every fixed binding, semantic/source recomputation, exact-address
readback, namespace/preimage, persistence, target-formation and local-only check
passed. The complete classified site and repository bytecode inventories and
their `__pycache__` directory censuses were byte-identical before and after every
Python-bearing command.

## Finding counts

| Severity | Count |
| --- | ---: |
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

There are no open implementation or review-chain findings.

## Frozen candidate verification

Every fixed packet binding was verified before merits work and again after
postflight:

- contracts:
  `8040279c825fc246900a07b257bab71b9ead3ff9850c4e7994501bd9d13d272f`;
- runtime:
  `a9bc386ec759252464e5d6b4b14b95082a3a4218a9a48cbea97ffbcbd11b95cd`;
- contract tests:
  `13ce12bb54ccd0880ab0865e3b33982bba1b0cfeb4fc59f070bde710e5dbc030`;
- runtime tests:
  `47e4f4aa0868e987fdc5961e6960b85456edcfa1a394b634664dff587225ae60`;
- producer return:
  `813b83bc5641f7a6322a529d3e513e284eca02302e3bfec5f6b2b20bac4e70b5`;
- additive namespace binding:
  `d28e808a91864156b479aa02647859aea8e08ad55b36e9b726192cd9413c84dd`;
- invalidated R1 review:
  `4eed7733df7c9cc468385b4c4dff07d2cbad3f211bb38602219cec2b0075b9a3`;
- invalidated R1 return:
  `6bcfc58bae4f003dfbd90afb9ff62be0e2aff4c1a8cb83cee5e7070be0194a8c`.

The identity artifacts remained exactly:

- queue: SHA-256
  `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51`,
  `17,412` bytes, regular file, link count one, mode `0600`;
- bundle: SHA-256
  `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`,
  `91,420,676` bytes, regular file, link count one, mode `0600`;
- derived identity dependency UUID:
  `31638732-5b25-57db-9eb4-8e943a47a387`.

The identity root contains only the two required parent directories and those two
content-addressed files. There is no correction, alias, sidecar, partial, stale,
extra or unreferenced identity artifact.

## Closed bytecode-inventory proof

The preflight was taken before any Python command. Each row bound relative path,
classification, size, mode, link count, device/inode identity, complete first
16-byte header/current magic, complete SHA-256, and source/owner association. All
present files classified with no unsafe, ambiguous or unclassified row.

| Inventory | Count | Full classified inventory SHA-256 | Path/file SHA-256 digest | Cache directories / digest |
| --- | ---: | --- | --- | --- |
| site preflight | 1,086 | `810c13b676e5be41bf334334dc927ead104648b397fbe17424cb0f30fefa0c01` | `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18` | 131 / `101b02d3767722fe1142cc5ea9a03400d7d2064b145152ed63f3a1e12ad7ee1c` |
| site postflight | 1,086 | `810c13b676e5be41bf334334dc927ead104648b397fbe17424cb0f30fefa0c01` | `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18` | 131 / `101b02d3767722fe1142cc5ea9a03400d7d2064b145152ed63f3a1e12ad7ee1c` |
| repository preflight | 76 | `9c540a46000bb1a1e44d6fd5fdeb75c8fb548c2f3f9c951f6e5cdf286a1d5bcb` | `431766856f97c87410e7013ddc0c327c7b22edaa9af31f1875c9a5f831175da5` | 19 / `2788e5e2eaeacca4878ab15d6baeef690cfd979cfb5255825e1cff0ccb6029c5` |
| repository postflight | 76 | `9c540a46000bb1a1e44d6fd5fdeb75c8fb548c2f3f9c951f6e5cdf286a1d5bcb` | `431766856f97c87410e7013ddc0c327c7b22edaa9af31f1875c9a5f831175da5` | 19 / `2788e5e2eaeacca4878ab15d6baeef690cfd979cfb5255825e1cff0ccb6029c5` |

The independently derived path/class/metadata/header/source-association digests
were also stable: site
`4e135b5486aa3bb74c619381211ae5bd069a1ddbd6f5ce8cc0f23e8859228460`
and repository
`1dff08e59bb89e2c8fd4e49defdb08841ea530b913e0c83bd0f37537f4a240ce`.

The site decomposition is 972 distribution-normal, 112 pytest-rewrite, one uv
bootstrap normal and the one exact optional inert six orphan. The repository
decomposition is 41 mapped normal, 32 mapped pytest-rewrite and the three exact
optional inert orphans. Relative to R20's dated R19 repository observation, the
current preflight has six additional mapped normal and twelve additional mapped
pytest files; all map to present repository sources. The cache-directory count and
three orphan predicates are unchanged. Operational count drift before this review
does not broaden stable authority; within-review inventory drift was exactly zero.

All Python-bearing commands began with `PYTHONDONTWRITEBYTECODE=1`, used
`uv run --locked --no-sync`, and used `python -B` for the local-only verifier and
standalone source helpers. The complete postflight files and directory lists
compared byte-for-byte equal with `cmp`. No cleanup, deletion, cache repair, sync,
environment recreation or mutation was attempted.

## Source recomputation and recursive exact-address readback

The independent helper asserted `sys.dont_write_bytecode is True` and the exact
environment value before importing project or installed modules. From the exact
source, manifest and identity roots it called `build_initial_identity_bundle(...)`
and then `load_initial_identity_bundle(...)` using only the computed exact bundle
digest. Complete object equality passed after the loader independently recomputed
the source population and recursively reopened the queue and bundle.

It reproduced:

- `5,594` current rows;
- `7 COMPETITION/RESOLVED`, `142 TEAM/RESOLVED`,
  `3,603 PLAYER/RESOLVED`, `15 PLAYER/REVIEW_REQUIRED`,
  `1 PLAYER/REJECTED`, and `1,826 MATCH/RESOLVED`;
- `23` absent-player source occurrences aggregated into `15` open queue items;
- `226,041` unique player-zero source-row references;
- both exact content addresses, their canonical bytes and the derived dependency
  UUID above.

All five target identities reproduced independently:

| Source identity | Exact source row | Raw-record SHA-256 | Canonical UUID |
| --- | --- | --- | --- |
| `competition:364` | `objects/competitions.json#1` | `6a5916b3e5cf86d73a6409f159804eaa62dcef27614129a2e15a52b67207b36a` | `cb5c5317-fa4a-571e-93dc-ef6ce482eab7` |
| `team:1609` | `objects/teams.json#84` | `82dbdc6c1ec0ae9da8d63078b3815cb7e2ef84fc29bacac18c85e65b011d9d96` | `b5f2dd3c-0166-5384-99fa-0ed47cc7e44c` |
| `team:1631` | `objects/teams.json#54` | `be9e47831f6d86450cd3fa9fb7471e26da691fa793bdc0d06ffb929a757b8a10` | `5b353635-819b-5bd1-8ca2-5a7364042a96` |
| `player:285508` | `objects/players.json#757` | `c6f2f4c5b74563a12cdb78fa49ae295622f5f730ff980fdb220448a4b404e1ac` | `be8da881-2b15-513f-978f-6bb3865bc8e2` |
| `match:2499719` | `archive-members/matches_England.json#379` | `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86` | `bad97950-6fac-5cf0-a93c-094f91abbb9b` |

The exact match row reconciled competition `364`, season `181150`, start
`2017-08-11 18:45:00`, and teams `{1609,1631}`. Player `285508` is team `1631`
bench index `4` and substitution index `1`, entering for player `192748` at
nominal minute `82`. This supports only the later right-censored `[82,83)` stint;
the review created no lineup, minutes, feature or product bytes.

## Namespace, preimage and fail-closed persistence review

The passing suite and standalone probes bind:

- queue namespace `UUIDv5(NAMESPACE_URL,
  "urn:scouting-intelligence:w04:wyscout:identity-review-queue:v1")`;
- the exact sorted-key compact five-field UTF-8 queue preimage with no newline;
- crosswalk namespace `fd7bb3ae-10f7-5856-99fb-3854d794273d`;
- the exact colon-separated tenant/kind/source/version/evidence preimage;
- fixed synthetic `player:379199` row UUID
  `45b2a06d-e200-5cb3-9c9d-8f429291ed31` and trace UUID
  `121e5662-35f6-5f12-8b3b-c458b30cc38a`.

Alternate namespace, newline, case, reason, semantic/reference and coercive
integer values fail. The `79` focused identity/authority tests additionally
exercise malformed/trailing/duplicate JSON, wrong roots, omissions, duplicates,
reordering, stale authorities and clocks, digest-only caller evidence, partial
inventories, sidecars, symlinks, unsafe modes and immutable unequal content.

Directory enumeration is reject-only exact-set enforcement, not selection:

1. the builder begins from exact source/manifest/authority paths and derives the
   sole queue and bundle names before inspecting the identity inventory;
2. the loader recomputes the complete source-derived build and compares the
   supplied digest with that derived address before inventory validation;
3. `_identity_inventory` exposes all present names only to `_check_inventory`;
   neither function returns or chooses newest/first/last authority; and
4. `_check_inventory` requires equality to the two already-derived filenames,
   while `_verify_reopened` opens only those exact paths and recursively proves
   queue equality with the review-required bundle population.

No scan discovers or selects an authority address. Additional, missing, stale or
partial state fails closed.

## Commands and results

- complete shell-only fixed-hash, artifact-type/size/mode and preflight
  classification: exit `0`, exact;
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q
  tests/contracts/test_w04_wyscout_identity_bundle.py
  tests/unit/test_wyscout_identity.py
  tests/contracts/test_w04_identity_ruleset_authority.py`: exit `0`,
  `79 passed in 24.57s`;
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B
  scripts/verify_local_only.py`: exit `0`, `PASS`, 25/25 controls;
- first standalone source helper: exit `1` because this reviewer incorrectly
  applied the synthetic test-vector evidence digest to the real source-complete
  `player:379199` row. It established no candidate failure and made no write;
  the assertion was corrected to construct the exact synthetic vector separately;
- corrected locked/no-sync, bytecode-disabled source recomputation and exact-address
  loader: exit `0`, all population, address, namespace, target and formation
  assertions passed;
- complete shell-only postflight classification and byte comparison: exit `0`,
  all four inventory/census files byte-identical;
- final candidate/artifact hash, size, link and mode recheck: exit `0`, unchanged.

No Git command was issued by this reviewer. The packet-required local-only verifier
performed only its own read-only repository safety checks. No provider/network,
build ID, Bronze/Silver/Gold, receipt, code manifest, product, cloud, container,
hosted CI, remote, public endpoint or deployment action occurred.

## Verdict

The unchanged identity candidate satisfies the bounded R2 review with zero open
P0-P2 findings and a valid no-write chain of custody. It is suitable for master
reproduction and acceptance. This verdict grants no independent product or build
authority.

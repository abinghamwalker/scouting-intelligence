# W04 identity-bundle runtime R2 master acceptance

Date: 2026-07-31

Decision: `ACCEPT`

The master accepts the unchanged source-complete identity runtime and its exact two
local content-addressed artifacts for bounded downstream W04 dependency use. The R1
review remains retained as invalidated chain-of-custody evidence; it was not used as
acceptance evidence.

## Accepted candidate

- contracts: `8040279c825fc246900a07b257bab71b9ead3ff9850c4e7994501bd9d13d272f`
- contract exports: `5db4077b4235856b25a6ed2f52f1b81c9f4649a0ed33751a6dced67af8103a0f`
- runtime: `a9bc386ec759252464e5d6b4b14b95082a3a4218a9a48cbea97ffbcbd11b95cd`
- runtime exports: `bcd60d47b7318ac7a04bb93897760943bd0003332a5c713691741bc468e7fa98`
- contract tests: `13ce12bb54ccd0880ab0865e3b33982bba1b0cfeb4fc59f070bde710e5dbc030`
- runtime tests: `47e4f4aa0868e987fdc5961e6960b85456edcfa1a394b634664dff587225ae60`
- producer return: `813b83bc5641f7a6322a529d3e513e284eca02302e3bfec5f6b2b20bac4e70b5`
- namespace addendum: `d28e808a91864156b479aa02647859aea8e08ad55b36e9b726192cd9413c84dd`

## Accepted artifacts

- review queue: `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51`,
  17,412 bytes, regular link-count-one file, mode `0600`.
- identity bundle: `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`,
  91,420,676 bytes, regular link-count-one file, mode `0600`.
- identity dependency UUID: `31638732-5b25-57db-9eb4-8e943a47a387`.

## Acceptance basis

- The master inspected the complete implementation, contract, tests, return and
  artifacts and independently reproduced 79 focused tests, all static/import/
  security/local-only controls, exact hashes, modes, inventory and source counts.
- Fresh R2 independent review passed with `P0=0`, `P1=0`, `P2=0`, independently
  rebuilding all 5,594 rows and recursively reopening the exact queue and bundle.
- That review reproduced 23 absent-player occurrences into 15 review items,
  226,041 rejected-zero references, all five target identity vectors and the target
  `[82,83)` right-censored formation evidence.
- Complete site (1,086 files) and repository (76 files) classified bytecode
  inventories and cache-directory censuses were byte-identical before and after the
  bytecode-disabled review.
- Directory enumeration was proven reject-only exact-set enforcement, never an
  authority-selection scan.

Independent review: `7dc36b07a3219bc4b1b75a5140920d5610ae9d438d375476c356c772a3fdaa68`.
Reviewer return: `6e508ba404ac8abd08eda2923b6f09f1b8602d19bc205d99b81d5178c0237453`.

This acceptance grants only the exact identity dependency. It grants no build ID,
Bronze, Silver, Gold, receipt, product or publication authority.

# W04 identity-bundle runtime R1 master verification

Date: 2026-07-31

Disposition: `MASTER_FOCUSED_CHECKS_PASS_AWAITING_INDEPENDENT_REVIEW`

The master inspected all 2,246 changed source/test/return lines, the two exact
materialized artifacts, and the additive namespace addendum, then independently
reproduced the complete packet suite. This freezes the exact candidate for fresh
critical review; it is not downstream build acceptance.

## Exact candidate

- identity contracts: `8040279c825fc246900a07b257bab71b9ead3ff9850c4e7994501bd9d13d272f`
- contract exports: `5db4077b310ffaf0695357d9787c100d7ec3d50fd75d52e58d042ba599233a0f`
- identity runtime: `a9bc386ec759252464e5d6b4b14b95082a3a4218a9a48cbea97ffbcbd11b95cd`
- identity exports: `bcd60d477a564b74ff5e71ae441929c86b74b39e6080c2d3f52232815bd0fa98`
- contract tests: `13ce12bb54ccd0880ab0865e3b33982bba1b0cfeb4fc59f070bde710e5dbc030`
- runtime tests: `47e4f4aa0868e987fdc5961e6960b85456edcfa1a394b634664dff587225ae60`
- producer return: `813b83bc5641f7a6322a529d3e513e284eca02302e3bfec5f6b2b20bac4e70b5`
- crosswalk namespace addendum: `d28e808a91864156b479aa02647859aea8e08ad55b36e9b726192cd9413c84dd`

## Materialized candidate

- queue: `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51`,
  17,412 bytes, mode `0600`.
- bundle: `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`,
  91,420,676 bytes, mode `0600`.
- derived identity dependency UUID: `31638732-5b25-57db-9eb4-8e943a47a387`.
- inventory: exactly those two content-addressed files, with no sidecar, correction,
  alias, partial, stale or extra artifact.

## Master inspection

- Exact authorities and every declared source member are nofollow-read, stable-file
  checked and whole-file hashed before strict streaming JSON projection. Identity
  fields reject Boolean, float, decimal and string coercion.
- The runtime recomputes 5,594 initial rows, the exact 23-to-15 review queue and all
  226,041 player-zero references from source bytes. It fixes all clocks, authority
  edges, source references, row digests, UUID preimages, ordering, counts and queue/
  bundle recursion.
- Queue and bundle bytes are canonical, sidecar-free and immutable. They are reopened
  nofollow, byte/digest/contract compared and recursively matched. Equal retries are
  idempotent; partial, additional, unsafe, symlink or unequal states fail closed.
- Caller bundle digests are considered only after complete source recomputation.
- The fresh review must adjudicate that directory inventory is used solely to reject
  unexpected artifacts, never to select an address/newest artifact, and therefore
  does not weaken R20's exact-address reader rule.

## Independently reproduced checks

- Ruff format/check and mypy: PASS.
- import-linter: PASS, 3/3 contracts kept.
- complete identity/authority suite: PASS, `79 passed in 24.51s`.
- focused Bandit: PASS.
- local-only verifier: PASS, 25/25 controls.
- all candidate/addendum/artifact hashes, sizes and modes: exact.
- `git diff --check`: PASS.
- `git remote`: PASS, empty output.

Fresh independent review is required before the bundle digest can feed build authority.

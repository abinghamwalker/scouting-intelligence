# W04 season/lineup product-binding R2 master verification

Date: 2026-08-01

Decision: `PASS_TO_FRESH_INDEPENDENT_REVIEW`

The master accepts the bounded R2 implementation for review only. The R2 changes
are confined to progression-safe test behavior; every authority, review,
configuration, runtime, source, data and product byte remains unchanged.

## Corrected test hashes

- season/lineup authority test:
  `3a4ed66082d16cf55a87921a742aea30f5600ad538f2664d0a65fe5be2b9e21f`;
- build/product authority test:
  `12d7379b7594caaea2aed508fd1444cfa307d1911d8d12fb52222d050c0fc73b`;
- R21 control-preimages test:
  `6ae725e379a33cd0785b346fe4ddcdca3fdc296ff24a1f78697202834e7d0df6`;
- R2 producer return:
  `98cc732eeb79341fc7d58885825c808bae9fa3a1ac1beeedcafdb7e3cb885e74`.

## Master inspection

Each module now snapshots product-destination state before and after exact
authority/preimage reads, installs writer-call tripwires, and proves byte/state
preservation. Each also exercises wholly absent and pre-existing simulated roots
under `tmp_path`. No real product root, skip, xfail, environment flag, future task
ID or placeholder gate is used.

The tests retain the semantic assertion that the authority/preimage itself is
control-plane-only and grants no product permission; later separately accepted
product existence no longer invalidates an immutable authority.

## Independent master results

- Ruff format: PASS, three files already formatted.
- Ruff lint: PASS.
- Mypy: PASS.
- Focused R2/build/R21 suite: PASS, `169 passed in 3.77s`.
- Local-only verifier: PASS, 25/25.
- `git diff --check`: PASS.
- `git remote`: empty.
- correction/build authority hashes: unchanged at
  `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e`
  and `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`.

The failed R1 review remains byte-identical at
`reports/reviews/W04/archive/wyscout-season-lineup-product-binding-independent-review-R1-rework-431e0cfb.md`
with SHA-256
`431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba`;
its original return remains retained at SHA-256
`8218de5bb7e38114204d8c5a82586ff0718887c3ec3a2a682b216f367d91b547`.

No master acceptance or product permission is granted until the fresh review
returns PASS and the master independently validates the complete lifecycle.

# W04 vertical-slice source adapter R2 master verification

Date: 2026-07-31

Disposition: `MASTER_FOCUSED_CHECKS_PASS_AWAITING_FRESH_INDEPENDENT_REVIEW`

The master inspected the complete bounded R2 correction and independently reproduced
its suite. R1's failed-review evidence is retained. This freezes a new exact candidate;
it is not acceptance.

## Exact candidate

- source implementation: `b1cdb309c3d81e7a3b0606987fdf6c456d61a66c393ca681d93e212e805ac43c`
- source tests: `1acb8908bd2cbb11a4f9e1d3d25ed270e5781c11e0cc6fa0c94b97d486e064f4`
- R2 producer return: `5b9fc93d2f9cd0d2e896a4fb55df3da2959b01c3b59515e65acd7d3aa48e1df9`
- accepted completion index: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- unchanged R20: `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- unchanged R21: `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`

## Master inspection

- Strict tag parsing now copies every sole strict-integer `id` into an unreachable
  dictionary exposed only through `MappingProxyType`; retained duplicate raw tags and
  sorted-unique possession tag projection are unchanged.
- Canonical encoding admits that immutable representation only for the exact sole-ID
  shape and renders the original JSON object bytes. Arbitrary mapping proxies remain
  rejected.
- The representative action-frame SHA-256 remains
  `5b94fec338d67564aa16e37b8eb60ec70995182c8a7dc1bd5d02c1e32b83ca4e`; its one-action
  membership remains `c245045382071ae38bf26557b2acb16282db1997e0fbaf50a9a9faafc8ba6d21`.
- Mutation through `VerifiedMatchAction.evidence.raw_tags` raises `TypeError`; the
  same authentic capability then revalidates exact `1H=901`, `2H=867` periods and
  their accepted membership digests.

## Independently reproduced checks

- Ruff format/check and mypy: PASS.
- import-linter: PASS, 3/3 contracts kept.
- combined source-index and data-contract suite: PASS, `286 passed in 116.73s`.
- focused Bandit: PASS.
- local-only verifier: PASS, 25/25 controls.
- accepted index/R20/R21 hashes: exact.
- `git diff --check`: PASS.
- `git remote`: PASS, empty output.

Fresh independent review of the new hashes is required before master acceptance.

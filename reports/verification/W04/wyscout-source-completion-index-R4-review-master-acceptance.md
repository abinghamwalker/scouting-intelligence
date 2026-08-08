# W04 source-completion-index R4 review master acceptance

Date: 2026-07-31

Disposition: `ACCEPTED`

The master accepts the exact R4 candidate after source/test inspection, independent
reproduction of all 500 focused tests, and two fresh parallel independent reviews.

## Accepted candidate

- completion implementation: `e7778db8c977b8461bb590f7174e4b519d7a2ba0a4171d99aa1fd686a6cd5302`
- contract implementation: `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932`
- completion tests: `05593a0a0afda62af2b6a2c8753a4f83e78fcbd363b89788751dd2055ed6dfeb`
- contract tests: `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e`
- producer return: `aa165fd8bc74d56e4e4e72da6d2cd7f11a2b65cc389f98efeafd3894b3c72a36`

## Independent decisions

- proof-graph review: PASS, P0=0/P1=0/P2=0,
  `43530d9fe7641a50a8684cecff308be0fdaf4f0718e994b1627e1a62fe23ebec`
- proof-graph return:
  `689a5826940faf6a25db4552dccb8fd40b041013e45f9cebb41feca8371c8142`
- semantic-regression review: PASS, P0=0/P1=0/P2=0,
  `45c6a96b43f600ac1f24d3b0dd9f11f5d14713ccb1560f95285e6bacd2805a4e`
- semantic-regression return:
  `3fe4f672a23f661351f44592e4055d3380e130629ce2337d462da72f3db1fffd`

The master confirms that exposed issuer/registry state cannot confer authority:
completion evidence is rechecked against the exact accepted population, and product
evidence is recursively rederived with exact type, value and completion-scope
equality. False match state, detached raw products, malformed evidence, cycles,
stale mutation, wrong type and cross-scope overlap fail closed. Valid directly
inserted evidence can pass only when it independently proves exactly the public
checked result.

The accepted index remains byte-exact at
`46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`,
with five members, 3,652 periods and 3,071,395 actions. R21 strict mapping,
equal-clock behavior, causal provenance, exact four features, five dependencies,
six coverage authorities and bounded one-match manifest scope remain intact.

Master-focused checks passed: Ruff, mypy, import-linter, Bandit, local-only 25/25,
and `500 passed in 172.34s`. `git diff --check` passed and `git remote` printed
nothing. The complete repository gate is the next mandatory action; product work
remains blocked until that gate passes.

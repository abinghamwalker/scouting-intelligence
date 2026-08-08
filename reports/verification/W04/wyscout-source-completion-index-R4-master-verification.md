# W04 source-completion-index R4 master verification

Date: 2026-07-31

Disposition: `MASTER_FOCUSED_CHECKS_PASS_AWAITING_PARALLEL_INDEPENDENT_REVIEW`

The master inspected the complete R4 source and regression changes and independently
reproduced the full packet suite. This freezes an exact candidate for fresh review;
it is not final acceptance.

## Exact candidate

- completion implementation: `e7778db8c977b8461bb590f7174e4b519d7a2ba0a4171d99aa1fd686a6cd5302`
- unchanged contract implementation: `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932`
- completion-index unit tests: `05593a0a0afda62af2b6a2c8753a4f83e78fcbd363b89788751dd2055ed6dfeb`
- Wyscout contract tests: `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e`
- R4 producer return: `aa165fd8bc74d56e4e4e72da6d2cd7f11a2b65cc389f98efeafd3894b3c72a36`

Frozen index and authorities remained exact:

- index: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- R20: `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- R21: `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`

## Master inspection

- Completion records retain the exact index, ordered source population and scope
  kind only. Each checked use re-executes accepted population equality and derives
  sequences, period keys and full-match state; no stored Boolean or sequence is
  authority.
- Product records retain exact construction kind, canonical payload and typed
  dependency graph. Each checked use recursively revalidates completion evidence and
  rederives the exact value and exact completion scope.
- Verification is cycle-safe and memoized only for one top-level consumption graph.
  Registry membership and issuer secrecy are lookup mechanisms, not authority.
- New regressions exercise exposed completion/product issuers, direct malformed and
  cross-scope registry records, false full-match evidence, detached raw Gold, scope
  overlap and cyclic product graphs.
- The real match 2499719 chain remains exact and asserts a single source-population
  verification across final manifest consumption. Its producer timing improved from
  197.56 to 106.98 seconds without deleting credited negative coverage.
- The public R3 checked API, raw `semantic_only_unchecked` state, exact four-feature
  Gold vector and one-match manifest scope are unchanged.

## Independently reproduced checks

- `uv sync --locked --all-groups`: PASS.
- focused Ruff format/check: PASS.
- focused mypy: PASS.
- import-linter: PASS, 3/3 contracts kept.
- exact six-module focused suite: PASS, `500 passed in 172.34s`.
- focused Bandit: PASS.
- local-only verifier: PASS, 25/25 controls.
- `git diff --check`: PASS.
- `git remote`: PASS, empty output.

Fresh independent capability/proof-graph and semantic-regression reviews are now
required in parallel. The complete repository master gate remains blocked until both
reviews pass and the master accepts them.

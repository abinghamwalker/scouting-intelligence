# Subagent return

## Task

- task_id: `W04-SOURCE-COMPLETION-INDEX-REVIEW-04-R1`
- objective: Freshly and independently review the exact R4 proof graph and return PASS only if exposed issuers or mutable registries cannot make incomplete, malformed, detached, cyclic or cross-scope evidence pass checked consumption.

## Files changed

- `reports/reviews/W04/wyscout-source-completion-index-proof-graph-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-REVIEW-04-R1.md`

## Summary

- Disposition: **PASS**.
- Findings: P0 `0`, P1 `0`, P2 `0`.
- Recomputed all six packet bindings before analysis; all matched exactly.
- Independently inspected every completion/product proof record, verification context,
  weak registry getter/issuer, checked builder, recursive verifier and
  `require_checked_product` boundary.
- Confirmed registries and exposed issuer closures are lookup mechanisms only. Every
  checked use revalidates exact retained source evidence or recursively reconstructs
  the exact product and completion scopes.
- Challenged false period-to-match state, nonaccepted action population, malformed
  completion/product evidence, detached raw product, cyclic and incomplete recursive
  graphs, stale registry mutation, wrong exact type, memoization identity separation,
  overlapping scopes and full-match/period cross-scope overlap. All failed closed.
- Confirmed a registry-forged completion or product passes only when complete retained
  evidence independently rederives exactly the value and scope the public checked path
  authorizes.
- Reproduced normal match `2499719` as `901 + 867 = 1768` and confirmed one completion
  verification per top-level graph. The full regression retained checked Action,
  Possession, Fact, Gold and exact one-match manifest construction.
- Reproduced the original fail-fast reader bypass as closed. No `model_construct` was
  used or credited.

## Tests run

- command: `shasum -a 256 src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R4.md`
  - exit status: 0
  - result: exact expected digests `e7778db8...5302`, `154f1ae9...7932`, `05593a0a...dfeb`, `139683be...5be9e`, and `aa165fd8...2a36` matched.
- command: `shasum -a 256 data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - exit status: 0
  - result: immutable index digest matched `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: 0
  - result: `500 passed in 175.09s`.
- command: `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py`
  - exit status: 2 on the first sandboxed attempt, then 0 on the approved read-only rerun
  - result: initial failure was only unreadable existing shared uv-cache metadata; rerun completed with no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS, 25/25 local-only controls, zero failures.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run python -` with the bounded in-memory issuer/registry/proof-graph script recorded in the review evidence
  - exit status: 2 on the first sandboxed cache-read attempt, then 0 on the approved read-only rerun
  - result: false match, nonaccepted population, malformed scope/kind/payload/dependencies, detached product, stale records, cycle, incomplete recursion, wrong type and live-identity memoization checks failed closed; valid forged evidence exactly rederived; one top-level completion verification observed.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run python -` with the corrected fresh-scope overlap and exact-match script recorded in the review evidence
  - exit status: 0
  - result: full-match/period overlap rejected; exact match `2499719`, `(901, 867)`, total `1768` confirmed.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-source-completion-index-proof-graph-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-REVIEW-04-R1.md`
- Candidate source SHA-256: `e7778db8c977b8461bb590f7174e4b519d7a2ba0a4171d99aa1fd686a6cd5302`.
- Candidate contract SHA-256: `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932`.
- Candidate source-test SHA-256: `05593a0a0afda62af2b6a2c8753a4f83e78fcbd363b89788751dd2055ed6dfeb`.
- Candidate contract-test SHA-256: `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e`.
- R4 producer return SHA-256: `aa165fd8bc74d56e4e4e72da6d2cd7f11a2b65cc389f98efeafd3894b3c72a36`.
- Accepted completion-index SHA-256: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.

## Risks

- Exact source-population reconstruction remains deliberately substantial, but the
  complete packet suite finished within its accepted bound and memoization was observed
  at exactly one population verification per top-level graph.
- Exposed registry/issuer objects remain mutable and introspectable, but the completed
  probes confirm they cannot substitute for independently reverified evidence.
- Residual uncertainty: none identified within the R4 packet scope.

## Follow-up items

- Master reproduction and acceptance; no bounded correction is requested.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- no provider/network, product write, cloud/container/CI, endpoint, remote or deployment action: confirmed

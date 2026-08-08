# Subagent return

## Task

- task_id: W04-SOURCE-COMPLETION-INDEX-01-R4
- objective: Correct `W04SCIIDXR3CAPR1-P1-001` by making every checked completion and product consumption independently re-verifiable from exact retained source population and construction-graph evidence.

## Files changed

- `src/scouting/sources/wyscout_completion_index.py`
- `tests/unit/test_wyscout_source_completion_index.py`
- `tests/contracts/test_wyscout_data_contracts.py`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R4.md`

`src/scouting/contracts/wyscout_data.py` was inspected and verified but did not require a byte change.

## Summary

- Completion records now retain the exact accepted `SourceCompletionIndex`, exact ordered action population and declared period/match scope only. Every top-level checked use reruns the accepted population comparison and derives fresh reader-built period sequences, period keys and full-match state from that evidence.
- Product records now retain an exact construction kind, canonical caller payload and typed dependency graph. Every checked use recursively verifies its completion/product dependencies, recomputes the exact Action, Possession, Fact, Gold or manifest value and requires equality with the retained value and completion scopes.
- Verification is acyclic. A per-top-level-call context memoizes already-verified authentic handles only inside that consumption graph, so a shared source population is fully revalidated once per graph without treating registry membership or issuer secrecy as authority.
- Public R3 checked builders and `require_checked_product` retain their signatures and successful match `2499719` flow. The real-source path still proves the exact `901 + 867 = 1768` match population, Action to Possession to Fact to Gold to one-match manifest composition, and Gold feature vector `(2, 0, 1, 2)`.
- Added adversarial regression coverage for callable closure introspection, false full-match issuer calls, malformed and cross-scope completion registry inserts, overlapping independently issued completion scopes, detached raw Gold reissue through the exposed product issuer, malformed product registry inserts and recursive product cycles.
- Preserved accepted index bytes and address. No product bytes, provider access, dependencies, external services, containers or deployment were introduced.

## Tests run

- command: `uv run ruff format --check src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: 4 files already formatted
- command: `uv run ruff check src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: all checks passed
- command: `uv run mypy src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: 0
  - result: no issues in 4 source files
- command: `uv run lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: 0
  - result: 500 passed in 173.87 seconds
- command: `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py`
  - exit status: 0
  - result: no findings
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; zero Git remotes, local `main`, Python 3.12.12, one root uv project, no hosted CI/deployment, no containers and no external-service dependency
- command: `uv run pytest -q` for the five new introspection/registry/cycle regression tests
  - exit status: 0
  - result: 5 passed in 4.42 seconds
- command: `/usr/bin/time -p uv run pytest -q tests/contracts/test_wyscout_data_contracts.py::test_real_match_checked_path_reaches_gold_and_exact_scoped_manifest`
  - exit status: 0
  - result: 1 passed in 106.98 seconds; real 107.12 seconds

## Artifacts/evidence

- Accepted completion index SHA-256 remained `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
- R4 source SHA-256: `e7778db8c977b8461bb590f7174e4b519d7a2ba0a4171d99aa1fd686a6cd5302`.
- Unchanged contract SHA-256: `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932`.
- R4 source-test SHA-256: `05593a0a0afda62af2b6a2c8753a4f83e78fcbd363b89788751dd2055ed6dfeb`.
- R4 contract-test SHA-256: `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e`.
- The deterministic performance guard in the real-source test observes exactly one `_verify_completion_evidence` call for the final top-level manifest consumption graph.
- Before context threading and removal of repeated real-source-only negative calls, the same positive test took 197.56 seconds. The accepted bounded path now takes 106.98 seconds, a 45.8% reduction, while independently revalidating every top-level checked use.

## Risks

- Exact source-population and Pydantic graph reconstruction is deliberately substantial: the real-source accepted vertical path takes 106.98 seconds and the full packet pytest selection takes 173.87 seconds. Both are below the three-minute guard and are bounded by deterministic one-verification-per-population-per-top-level-graph coverage.
- Process-local weak registries remain lookup caches, but standard introspection/mutation is explicitly tested and cannot make malformed, incomplete, detached or cyclic evidence pass checked consumption.
- Residual uncertainty: none identified within the R4 scope.

## Follow-up items

- Fresh independent R4 review and master acceptance are required before product implementation resumes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

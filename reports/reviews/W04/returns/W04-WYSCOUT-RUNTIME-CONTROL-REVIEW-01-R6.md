# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R6`
- objective: Freshly and independently challenge the complete R6 outer
  `W04_LOCAL_CONTROL` bootstrap, retained launcher-source descriptor, closed v4
  tuple/environment, whole-launch PYC equality, exact child chronology, and
  canonical completion without producer edits or real-root publication.

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R6.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R6.md`

## Summary

- Returned **REWORK** with `P0/P1/P2 = 0/1/0`.
- Fixed R6 bindings and historical R5/product acceptance bindings matched.
- The exact `237`-test population and every static/security/local-only gate
  passed, and shell preflight/postflight PYC inventories were exactly equal.
- Finding `W04-RUNTIME-R6-P1-01`: the first-user-code encoding verifier does not
  implement R20's admitted-stdlib-parent, exact-owner, and exact pre-guard
  file-backed-module-census predicates. It opens a complete absolute source path
  with leaf-only `O_NOFOLLOW`, checks only final-file kind/mode/links/size/digest,
  omits source/parent owner and contained parent traversal/identity, and checks
  presence of the three named modules without rejecting a fourth file-backed
  preload. This leaves a fail-open substitution/race gap before guard
  installation.
- Producer evidence is correctly bounded: the exact uv probe reaches a later
  rejection in a deliberately incomplete isolated repository, while the isolated
  full chronology substitutes child executors. Neither proves unmocked real-root
  completion; the later master-owned two-real-run packet remains sole authority.

## Tests run

- command: `uv run --locked --no-sync ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `3 files already formatted`
- command: `uv run --locked --no-sync ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run --locked --no-sync mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `Success: no issues found in 3 source files`
- command: `uv run --locked --no-sync pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `237 passed in 1476.22s (0:24:36)`
- command: `uv run --locked --no-sync bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `uv run --locked --no-sync lint-imports --no-cache`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks, zero failures
- command: identical shell-only preflight/postflight PYC inventory
  - exit status: `0`
  - result: site `1,087` pycs / `131` cache directories and repository `111` /
    `21`; both complete digests exactly equal

## Artifacts/evidence

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R6.md`:
  SHA-256 `6ba86ce454aee332b66bde6db0a1141511a33404054910996e521745ea8200bf`
- site PYC inventory SHA-256:
  `5459cbafa61d1f2c58a1313d008fd068bef9d15e5e30e47700d66ebed0dd1598`
- repository PYC inventory SHA-256:
  `e930505226115d5e9f6ddfb7de200dafe504632e603251fa84a6280640081167`
- admission child SHA-256:
  `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
- launcher SHA-256:
  `ecfb3b1714b7a6caf607d9ae4393b3130e04045c717f5965207a804356b580f7`
- runtime tests SHA-256:
  `ad6027133eccb451fd9ab9d7135e60ccab50335d7acfdd25b008565bba323116`
- producer return SHA-256:
  `092421174a1c19bc9ccb4ca2fbc5bb610d2c237c318940b516ddbf92aa7edc54`
- producer packet SHA-256:
  `6a900a2232443006b62580a4f815e476c941181ca0ad1e0d83021603cade87a5`

## Risks

- P1 runtime-admission risk remains until the three encoding sources are opened
  through retained admitted-parent directory descriptors with exact owner and
  stable identity checks, and the pre-guard file-backed-module census is exact.
- The initial sandboxed static attempts exited `2` before executing because the
  sandbox denied the admitted uv cache's internal `.git`; approved read-only cache
  access was then used and all required gates passed. No network or dependency
  change occurred.
- The packet lists two Git checks but also states `git_operations: forbidden`.
  No direct Git command was run. The required local-only verifier's embedded
  read-only policy checks reported zero configured remotes and branch `main`.

## Follow-up items

- Issue bounded R7 rework for `W04-RUNTIME-R6-P1-01`, add intermediate-parent,
  owner, and fourth-file-backed-module attacks, freeze new hashes, rerun the exact
  complete gate/PYC equality, and obtain a fresh independent review before any
  real-root run.

## Scope confirmation

- no Git operations: confirmed; no direct Git command was run
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

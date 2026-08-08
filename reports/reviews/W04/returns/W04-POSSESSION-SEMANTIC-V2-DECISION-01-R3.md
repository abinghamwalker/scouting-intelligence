# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R3`
- objective: Correct only P1
  `MULTISCOPE_POSSESSION_ID_INPUT_ORDER_DEPENDENCE` so deterministic resolved
  possession ordinals and identifiers are scoped to the exact match-period.

## Files changed

- `tests/contracts/test_w04_possession_semantic_v2_authority.py`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-DECISION-01-R3.md`

## Summary

- Moved the test-only resolver's possession ordinal from one global counter to a
  counter initialized independently inside each exact
  `(action_match_source_id, action_period_code)` scope.
- Preserved deterministic R20 ordering within each scope and the existing
  selector/sequence separation. Presentation order from another scope can no
  longer affect an action's resolved possession identifier or eligibility.
- Added a focused two-scope regression with interleaved actions and their
  reversed presentation. It requires complete per-`source_event_record_id`
  result dictionaries to be identical and asserts the exact scope-local
  identifiers `100:1H:possession:1`, `100:1H:possession:2`, and
  `200:2H:possession:1`.
- The regression exposes R2's global-counter behavior because reversing the
  first-presented scope changes its global ordinals. It passes after the R3
  scope-local correction.
- Retained the decision, candidate, five bound inputs, exact 17-key accepted v1
  predecessor, all 36 predicates, policies, R1/R2 evidence, review and
  acceptance boundary, later-authority boundary, and all product paths
  unchanged.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: `0`
  - result: `328 passed in 25.72s`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; failures empty; all 25 named checks passed
- note: the initial sandboxed pytest invocation exited `2` because the sandbox
  could not read the existing user uv cache. The exact locked/no-sync command
  was rerun with approved cache access and passed; no sync, install, clean, or
  repair occurred.

## Artifacts/evidence

- preserved decision physical/canonical SHA-256:
  `8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425`
- preserved candidate physical SHA-256:
  `24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187`
- preserved candidate parsed canonical JSON SHA-256:
  `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881`
- predecessor R2 focused contract physical SHA-256:
  `abe342c9cdec1ea35fd799a1205a9e99b1f4a2fdd2ac6dd2ae30f26b40f1dc98`
- corrected R3 focused contract physical SHA-256:
  `1a2bd111c046781c3e4fe6ebff58a716f1bf793a3df29ea2aaf073fc9896100c`
- preserved R2 producer return SHA-256:
  `80c86eeb2cef54b84ccc5b9c64e8dc08c4dfdbabdea061ef45c8b95134e5e3a7`
- preserved R1 evidence:
  - producer return:
    `a84a82e19f8fa75a7cd167dd92e178cc463feadbe9772d7715f9413b0c9289f8`
  - independent `REWORK` review:
    `71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a`
  - independent-review return:
    `fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90`
- frozen possession-v1 physical hashes remained exact:
  - decision:
    `4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71`
  - candidate:
    `e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d`
  - acceptance:
    `f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112`
- shell-only pre-Python bytecode inventory:
  - `.pyc` files: `1,145`
  - `.pyc` symlinks: `0`
  - `__pycache__` directories: `150`
  - serialized rows: `1,295` (`78` repo, `1,217` site)
  - serialized bytes: `222,755`
  - SHA-256:
    `13fcf204919e60067fa57a0d4c5032b039875872a442f165593484cf6e3a8f52`
- terminal post-return inventory reproduced every value above byte-for-byte.

## Risks

- This bounded R3 producer correction is not an independent review or
  acceptance. Feature authority, cross-authority composition, Bronze, Silver,
  Gold, build, model, and product work remain blocked.
- The resolver remains executable contract evidence only; this packet grants no
  product-code ownership and writes no product artifact.

## Follow-up items

- A separate owner must independently review the corrected R3 focused
  executable evidence before any acceptance or later-authority progression.

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`; exactly the two R3-owned paths
  above were changed
- no delegation, self-approval, provider/network access, review, acceptance,
  feature/cross-authority work, or product implementation: `confirmed`

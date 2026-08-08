# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R4`
- objective: Correct only P1 `REVIEW_ID_PATH_DRIFT` in the focused executable
  authority contract while preserving both failed review generations as exact
  historical non-authority.

## Files changed

- `tests/contracts/test_w04_possession_semantic_v2_authority.py`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-DECISION-01-R4.md`

## Summary

- Removed the invented current `v2-R2` review ID/path. `REVIEW_ID` and
  `REVIEW_PATH` now use only the R21-fixed
  `w04-wyscout-possession-semantic-independent-review-v2-R1` route.
- Replaced the stale requirement that the fixed path always contain failed R1
  bytes with an exact closed set containing only the two enumerated failed
  physical hashes:
  `71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a`
  and
  `609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a`.
- The actual progression reader converts fixed-path bytes with either exact
  failed digest to no current review. This requires decision-only state with no
  acceptance and no later authority; neither failed review can become current
  authority.
- All other present fixed-path bytes continue through the complete strict
  review validator. No unknown or merely invalid review is ignored.
- Added regressions for the exact fixed route, both enumerated historical
  failed hashes, decision-only/no-acceptance/no-later-authority behavior,
  unknown invalid review rejection, and normal fixed `v2-R1` PASS/REWORK
  progression.
- Preserved the decision, candidate, five inputs, exact 17-key accepted v1
  predecessor, all 36 predicates, selector/sequence separation, scope-local
  deterministic possession IDs, every prior semantic test, and all R1-R3
  evidence.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: `0`
  - result: final formatted bytes passed; `332 passed in 27.67s`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: initial `1`, final `0`
  - result: initial check requested two exact line-wrapping changes; those were
    applied with `apply_patch`, and the final result was
    `1 file already formatted`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; failures empty; all 25 named checks passed

## Artifacts/evidence

- predecessor R3 focused contract physical SHA-256:
  `1a2bd111c046781c3e4fe6ebff58a716f1bf793a3df29ea2aaf073fc9896100c`
- corrected R4 focused contract physical SHA-256:
  `dd4167747b71203390ba04d7c0899dc98099e203368ba5b3c3942b1b9a6e3116`
- preserved decision physical/canonical SHA-256:
  `8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425`
- preserved candidate physical SHA-256:
  `24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187`
- preserved candidate parsed canonical JSON SHA-256:
  `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881`
- preserved failed review generations:
  - R1 review:
    `71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a`
  - R1 review return:
    `fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90`
  - R2 review at the fixed path:
    `609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a`
  - R2 review return:
    `974d8418a7408eca3be338b0f8ae9211fb5df37eb9827c70251843051d404a23`
- preserved producer returns:
  - R1:
    `a84a82e19f8fa75a7cd167dd92e178cc463feadbe9772d7715f9413b0c9289f8`
  - R2:
    `80c86eeb2cef54b84ccc5b9c64e8dc08c4dfdbabdea061ef45c8b95134e5e3a7`
  - R3:
    `9a8afaed03a01760f3e352c5bd45c060cff3c07537a34ff7bdbdc09ac59c1bde`
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

- The fixed review path currently contains the known failed R2 review and is
  therefore correctly treated as historical non-authority. This packet does not
  create a valid review or acceptance.
- Possession-v2 acceptance, feature authority, cross-authority composition,
  Bronze, Silver, Gold, build, model, and product work remain blocked.

## Follow-up items

- A separate independent reviewer must write a valid fresh review at the fixed
  `v2-R1` path using the master-fixed canonical UUIDv5 actor before any
  acceptance or later-authority progression.

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`; exactly the two R4-owned paths
  above were changed
- no delegation, self-approval, provider/network access, decision/candidate or
  review edit, acceptance, feature/cross-authority work, or product
  implementation: `confirmed`

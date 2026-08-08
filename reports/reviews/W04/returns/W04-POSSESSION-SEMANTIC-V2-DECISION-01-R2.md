# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R2`
- objective: Correct only P1 `SEQUENCE_RESOLUTION_OVERCLAIM` by separating exact
  canonical predicate selection from deterministic ordered same-period possession
  resolution.

## Files changed

- `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json`
- `configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml`
- `tests/contracts/test_w04_possession_semantic_v2_authority.py`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-DECISION-01-R2.md`

## Summary

- Reworked the strict four-field selector so it emits only
  `PREDICATE_ADMITTED` with the exact predicate or `PREDICATE_UNMAPPED`. Selector
  lookup never emits `possession_eligibility_state`.
- Added a closed declarative same-period sequence policy with the exact R20 order
  `(period_rank, period_elapsed_seconds, source_record_ordinal,
  source_event_record_id)`, match/period scope, control/restart opening,
  same-team continuation, opposing-team close/open, dead-ball attachment,
  contested attachment/buffering, cross-team equal-clock uncertainty,
  period-boundary closure/buffer unassignment, and forbidden cross-period state.
- Added a focused test-only deterministic resolver. It consumes selector results
  in exact R20 order and emits `ELIGIBLE_RESOLVED` only after assignment to
  exactly one deterministic resolved possession. Unassigned, ambiguous,
  buffered-at-boundary, administrative, selector-unmapped, missing/unknown-team,
  and cross-period cases emit `INELIGIBLE_UNMAPPED`.
- Added positive executable evidence for control and restart opening, same-team
  continuation, opposing-team transition, preceding dead-ball attachment, and
  contested buffering resolved by a following same-period possession.
- Added negative executable evidence for isolated lookup, both unassigned and
  predecessor-less dead balls, unresolved contested buffering, administration,
  exact and invalid selector-unmapped actions, missing and unknown teams,
  equal-clock cross-team uncertainty, period closure, and attempted cross-period
  state.
- Retained all five bound inputs, the exact 17-key accepted v1 predecessor, all
  36 v1 predicates and their order, decision/candidate IDs and schemas, strict
  selector type/coercion/raw/name/label boundaries, progression gates, and
  no-product paths. Materialized the fresh truthful decision clock
  `2026-07-30T22:14:21Z`.
- Preserved the R1 producer return and independent `REWORK` review as immutable
  historical evidence. Future corrected review progression uses the distinct
  synthetic R2 review identity; no corrected review or acceptance was created.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `67 passed in 2.92s`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: `0`
  - result: `327 passed in 25.60s`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; failures empty; all 25 named checks passed

## Artifacts/evidence

- decision physical/canonical SHA-256:
  `8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425`
- candidate physical SHA-256:
  `24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187`
- candidate parsed canonical JSON SHA-256:
  `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881`
- focused contract physical SHA-256:
  `abe342c9cdec1ea35fd799a1205a9e99b1f4a2fdd2ac6dd2ae30f26b40f1dc98`
- exact structure readback: 10 decision keys, 9 candidate keys, 9 policy keys,
  36 predicates, 18 `ACTION_TEAM` predicates, 18 `NONE` predicates
- exact decision distribution retained:
  `CONTESTED=4`, `CONTROL=11`, `DEAD_BALL=8`,
  `NON_CONTROL_ADMIN=2`, `RESTART=7`, `UNMAPPED=4`
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
  - serialized rows: `1,295`
  - serialized bytes: `222,756`
  - SHA-256:
    `13c4a2423e093fb6dc2fc74eb4a9c0f46d87395e7bcaaefc0aca271e97929c57`
- terminal post-return inventory reproduced every value above byte-for-byte.

## Risks

- This bounded producer correction is not a corrected independent review or
  acceptance. Possession construction, feature authority, cross-authority
  composition, Bronze, Silver, Gold, build, model, and product work remain
  blocked.
- The executable resolver is contract evidence only; it grants no product-code
  ownership and writes no product artifact.

## Follow-up items

- A separate owner must independently review the corrected R2 decision,
  candidate, and focused executable evidence.
- Only after a valid corrected PASS review may the master separately materialize
  and verify possession-v2 acceptance.

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`; exactly the four R2-owned paths
  above were changed
- no delegation, provider/network access, corrected review, acceptance,
  feature/cross-authority work, or product implementation: `confirmed`

# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R2`
- objective: Independently review the corrected possession-v2 authority and R3
  executable evidence against frozen R20/R21, reporting every P0-P2 finding.

## Files changed

- `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R2.md`

## Summary

- Issued `REWORK` with exactly two P1 findings and no P0/P2 findings.
- Independently reconstructed the five exact bound inputs, exact 17-key accepted
  possession-v1 predecessor, ten-key decision, nine-key candidate, physical and
  canonical digests, all 36 byte-semantically unchanged v1 predicates, exact
  predicate distribution, policies, actors, and clocks.
- Independently challenged strict selector types, missing values, booleans,
  numeric-looking strings, null, non-integer numbers, arrays/objects, unknown
  pairs, missing/mistyped/unsorted/duplicate tags, synthetic required/forbidden
  tags, invalid teams, and raw/rejected/name/label alternatives. The selector
  admitted only accepted canonical inputs and never emitted final eligibility.
- Independently challenged same-period control/restart opening, same-team
  continuation, opposing-team transition, predecessor dead-ball attachment,
  contested buffering, administration, equal-clock cross-team uncertainty,
  period closure, no cross-period state, exactly-one assignment, and reversed
  multi-scope input order. The R2/R3 semantic resolver behavior passed.
- Found P1 `REVIEW_ID_PATH_DRIFT`: the R3 focused contract invents an
  `...independent-review-v2-R2` ID/path while frozen R21 and the packet fix the
  current review at `...independent-review-v2-R1`; the test simultaneously
  requires that fixed path to retain the archived failed review.
- Found P1 `OUTSIDE_ROOT_PACKET_CONFIG`: the dispatched master-owned packet
  embeds an absolute `/private/tmp` archive path, causing its mandatory
  `verify_local_only.py` command to fail `no_outside_root_config`.
- Preserved and verified the failed R1 review/return bytes in the retained
  archive before replacing the fixed review path. No candidate, test, v1
  authority, packet, acceptance, later authority, or product path was edited.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: `2` on the initial sandboxed attempt
  - result: existing user uv cache was outside the read sandbox; no repository
    or environment mutation occurred
- command: same exact focused suite with approved existing-cache read, before
  replacing the fixed review
  - exit status: `0`
  - result: `328 passed in 34.20s`; this green state retained the failed review
    at the fixed path and therefore did not establish valid R21 progression
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<independent candidate and selector reconstruction>'`
  - exit status: `0`
  - result: `PASS_INDEPENDENT_RECONSTRUCTION_AND_SELECTOR_CHALLENGE`; five
    inputs, seventeen prior-authority fields, and 36 predicates
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<independent same-period sequence challenge>'`
  - exit status: `0`
  - result: `PASS_INDEPENDENT_SEQUENCE_CHALLENGE`; exact scope-local possession
    identifiers and all positive/negative sequence cases passed
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `1`
  - result: 24 checks passed; `no_outside_root_config` failed on
    `orchestration/task_packets/W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R2.yaml`
    containing the absolute retained-archive path
- command: locked/no-sync standard-library canonical review-record validation
  - exit status: `0`
  - result: exact 12-key canonical `REWORK` record with two findings and one
    terminal LF
- command: exact focused suite after replacing the R21-fixed review path
  - exit status: `1`
  - result: `327 passed, 1 failed`; the sole failure at focused-test line 1400
    requires the same fixed current review path to retain the failed R1 SHA-256,
    directly reproducing `REVIEW_ID_PATH_DRIFT`

## Artifacts/evidence

- review:
  `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md`
- recommendation and finding cardinality:
  `REWORK`; `P0=0`, `P1=2`, `P2=0`
- review physical SHA-256:
  `609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a`
- canonical review-record SHA-256:
  `de5227391e050a87c731491528627f14e654ba4a64ca4f6b4087c21895ad9d4f`
- decision physical/canonical SHA-256:
  `8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425`
- candidate physical SHA-256:
  `24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187`
- candidate parsed canonical JSON SHA-256:
  `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881`
- focused executable contract SHA-256:
  `1a2bd111c046781c3e4fe6ebff58a716f1bf793a3df29ea2aaf073fc9896100c`
- preserved failed R1 archive:
  - review:
    `71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a`
  - return:
    `fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90`
- preserved producer returns:
  - R1:
    `a84a82e19f8fa75a7cd167dd92e178cc463feadbe9772d7715f9413b0c9289f8`
  - R2:
    `80c86eeb2cef54b84ccc5b9c64e8dc08c4dfdbabdea061ef45c8b95134e5e3a7`
  - R3:
    `9a8afaed03a01760f3e352c5bd45c060cff3c07537a34ff7bdbdc09ac59c1bde`
- shell-only pre-Python inventory:
  - `.pyc` files: `1,145`
  - `.pyc` symlinks: `0`
  - `__pycache__` directories: `150`
  - serialized rows: `1,295`
  - serialized bytes: `280,836`
  - SHA-256:
    `7b524d72e074c254ca8bacc14fb86b158d739fc21add45733bbd0d0156efc479`
- terminal post-return inventory reproduced the preflight byte-for-byte.

## Risks

- Possession-v2 acceptance cannot bind a valid current review while the
  executable contract expects a different, unauthorized review route and the
  packet's own local-only check fails.
- The semantic selector/resolver evidence itself passed the independent
  challenges; both defects are bounded to master-owned orchestration and the
  frozen focused contract. No architecture, provider/right, root, dependency,
  storage, network, cloud, container, endpoint, hosted-CI, deployment, or
  product change is required.

## Follow-up items

- Return the focused contract for bounded correction to use the one R21-fixed
  review ID/path while retaining failed R1 bytes only as immutable historical
  evidence.
- Correct the master-owned packet's outside-root absolute archive value so the
  mandatory local-only verifier passes, without deleting or rewriting the
  archive.
- Obtain a new fresh independent review after both corrections. Do not create
  possession-v2 acceptance or start later authority/product work before then.

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`; exactly the two packet-owned
  paths above were changed
- no delegation, self-approval, provider/network access, candidate/test/v1
  edit, acceptance, feature/cross-authority work, Bronze, Silver, Gold, build,
  model, product, cloud, container, endpoint, hosted CI, or deployment:
  `confirmed`

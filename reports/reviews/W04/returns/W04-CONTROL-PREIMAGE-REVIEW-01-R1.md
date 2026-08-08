# Subagent return

## Task

- task_id: `W04-CONTROL-PREIMAGE-REVIEW-01-R1`
- objective: Perform a fresh independent no-write review of both canonical R21
  control preimages and their focused test, recommending PASS only with zero
  P0-P2 findings.

## Files changed

- `reports/reviews/W04/wyscout-r21-control-preimage-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-CONTROL-PREIMAGE-REVIEW-01-R1.md`

## Summary

- Read every packet-listed authority in full, including immutable R20, accepted
  R21, R15, both complete one-line preimages, all 569 focused-test lines, and
  complete producer/master evidence.
- Independently reproduced canonical and physical preimage SHA-256 values
  `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
  and
  `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`.
- Reconstructed exact closed keys, 17 product path rows, ten sorted owners with
  once-only ownership, two primary keys, five manifest/receipt rows, 16
  descriptors, identical dependency order, earlier-only dependency edges,
  exact descriptor-only literal, and typed-null feature placeholder.
- Proved byte-equal authority links, no sibling edge, no self/sibling/future
  digest, no concrete feature hash, and valid topological presentation with
  either sibling first.
- Ran the six focused tests and an independent in-memory challenge that passed
  three positive semantic checks and rejected 14 negative mutations.
- Confirmed all seven product destination roots and every named next-stage
  field-v2, possession-v2, feature, and cross-authority test path are absent.
- Local-only verification passed all 25 checks.
- Finding counts are `P0=0`, `P1=0`, `P2=0`; recommendation is `PASS`, without
  self-acceptance or downstream authority.

## Tests run

- command: shell-only complete repository/site `.pyc` and cache-directory
  preflight inventory
  - exit status: `0`
  - result: `PASS`; required inventory has 1,145 pycs, 150 `__pycache__`
    directories, and 1,296 lines including header; retained SHA-256
    `b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777`.
    A 1,299-line diagnostic superset also retained three tool-cache rows.
- command: `shasum -a 256` over R20, R21, R15, both preimages, and the focused
  test, plus `wc -l -c` over both preimages and test
  - exit status: `0`
  - result: `PASS`; all expected hashes and exact `5473/1`, `6104/1`,
    `18992/569` byte/line cardinalities reproduced.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `2` in the restricted sandbox because the existing uv-cache
    `.git` was unreadable, then `0` with approved read access
  - result: final `PASS`; `6 passed in 0.09s`; no sync or repository mutation.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent mutation harness>`
  - exit status: `0`
  - result: `PASS`; three positive semantic checks passed and 14 targeted
    structural/DAG/digest/runtime negative mutations were rejected.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all 25 local-only and one-root-uv checks passed.
- command: shell checks for seven destination roots and all named downstream
  authority/test paths
  - exit status: `0`
  - result: `PASS`; every checked destination and descendant was absent.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -S -B -c <report acceptance assertions>`
  - exit status: `0`
  - result: `PASS`; report exists, exceeds 12,000 bytes, states recommendation
    and P0/P1/P2, and contains both pinned hashes.
- command: final repeat of the identical shell-only inventory plus `cmp` and
  `shasum -a 256`
  - exit status: `0`
  - result: `PASS`; required postflight is byte-identical to required
    preflight, 1,296 lines, same SHA-256
    `b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777`.
    The preserved diagnostic superset differs only in `.pytest_cache`, which is
    outside the R20 `.pyc`/`__pycache__` inventory; no cleanup was attempted.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-r21-control-preimage-independent-review-R1.md`
  - recommendation: `PASS`
  - findings: `P0=0`, `P1=0`, `P2=0`
- product preimage physical/canonical SHA-256:
  `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
- schema preimage physical/canonical SHA-256:
  `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`
- focused-test physical SHA-256:
  `b2bccb03e59c60a8d61439ea938e2da0fbb8a2bba2dcf77ff3549f2aabb54e53`
- preflight inventory:
  `/tmp/W04-CONTROL-PREIMAGE-REVIEW-01-R1.pre.required.inventory`
- postflight inventory:
  `/tmp/W04-CONTROL-PREIMAGE-REVIEW-01-R1.post.required.inventory`
- preserved broader diagnostic inventories:
  `/tmp/W04-CONTROL-PREIMAGE-REVIEW-01-R1.pre.inventory` and
  `/tmp/W04-CONTROL-PREIMAGE-REVIEW-01-R1.post.inventory`

## Risks

- No P0-P2 defect remains within the packet scope.
- These are inert control preimages only. Future field, possession, feature,
  cross-authority, gate, build, and product obligations remain unavailable
  until their separate serial packets and master decisions.
- This independent recommendation does not self-accept the artifacts.

## Follow-up items

- Master readback and acceptance/rework decision for this independent review;
  no downstream work is authorized by this return.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no dependency,
  lock, sync, install, or environment mutation was performed.
- no edits outside `allowed_paths`: confirmed; exactly the two packet-owned
  review/return paths listed above were created.

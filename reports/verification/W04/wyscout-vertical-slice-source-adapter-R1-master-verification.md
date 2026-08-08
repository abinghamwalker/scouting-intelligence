# W04 vertical-slice source adapter R1 master verification

Date: 2026-07-31

Disposition: `MASTER_FOCUSED_CHECKS_PASS_AWAITING_INDEPENDENT_REVIEW`

The master inspected the complete bounded source-adapter candidate and independently
reproduced its packet suite. This freezes the exact candidate below for fresh review;
it is not final acceptance.

## Exact candidate

- source implementation: `3050b7a3c0ff47442db973fb18fee70c8bf3256827936739e63f87947cd07bed`
- source-adapter tests: `d01a630f1ce2c345597dde7fef81589ca14e8690515e67d8ff476d1f4063423d`
- producer return: `c14691f01e8575d91e06882bcd2e1c78ee628d6993d1c89391590b93e957a0b1`
- accepted completion index: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- unchanged R20 authority: `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- unchanged R21 authority: `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`

## Master inspection

- The public loader rejects any unaccepted index, member path or match ID before
  source-member access and resolves only the frozen England event-member authority.
- It verifies stable source-manifest bytes, content-addressed index bytes and the
  exact member binding before nofollow-reading and hashing the whole 188,888,614-byte
  member. It requires all 643,150 decoded rows before selection.
- Physical ordinals are assigned before strict-integer match filtering. Each selected
  raw action is projected without coercion, canonically ordered, compared with both
  accepted match periods and bound to its raw-record digest.
- The result exposes 1,768 deeply immutable raw/evidence pairs plus the authentic
  checked completion capability. It creates no Bronze, Silver, Gold, manifest,
  receipt or other product byte.
- Adversarial tests fail closed for wrong pins, row-count drift, string match IDs,
  selected-action omission/addition/duplication/reordering, nested mutation and
  source-byte mutation.

## Independently reproduced checks

- focused Ruff format/check: PASS.
- focused mypy: PASS.
- import-linter: PASS, 3/3 contracts kept.
- combined source-index and data-contract suite: PASS, `286 passed in 114.45s`.
- focused Bandit: PASS.
- local-only verifier: PASS, 25/25 controls.
- `git diff --check`: PASS.
- `git remote`: PASS, empty output.

Fresh independent review is required before master acceptance or downstream use.

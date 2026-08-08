# Subagent return

## Task

- task_id: `W04-FEATURE-REGISTRY-REVIEW-01-R1`
- objective: Independently challenge the frozen R21 supported-feature decision,
  candidate, lineage, applicability, and progression, recommending `PASS` only
  with zero P0-P2 findings.

## Files changed

- `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-REVIEW-01-R1.md`

## Summary

- Independently reproduced the exact decision and candidate digests, closed
  schemas, ten accepted bindings, fifteen ordered feature rows, exact `4/4/7`
  state split, exact four-feature supported roster, candidate restatement,
  UUIDv5 actor separation, clock progression, and no-product boundary.
- Confirmed every supported input name is an accepted field-v2 canonical output,
  and confirmed `resolved_possession_action_count` retains only its three exact
  input fields with `ELIGIBLE_RESOLVED` as a separate applicability condition.
- Returned `REWORK` with an authority-proof P2:
  `APPLICABILITY_ACCEPTED_EVIDENCE_GAP`. The focused helper admitted null or
  boolean action IDs, null/empty/out-of-range positions, a null match ID, and
  mistyped possession selector IDs because it checks key presence rather than
  accepted evidence validity.
- Returned a second P2, `BYTECODE_INVENTORY_DRIFT`, because the terminal
  repository inventory contained five net-new `.pyc` files and therefore could
  not reproduce the packet's preflight chain of custody. Recent writes included
  security and W03 governance paths outside this review's bounded commands. No
  cleanup or repair was attempted.
- The exact R21 authority decision and candidate require no change. Rework is
  bounded to the focused applicability validation and missing negative cases.

## Tests run

- command: shell-only recursive preflight `.pyc` / `__pycache__` inventory
  - exit status: `0`
  - result: `1,145` `.pyc`, path-list SHA-256
    `0b44f044af2f627e3650d8607c5604977e2adb8353ff5e3fd4fe2336b951b418`;
    `150` `__pycache__`, path-list SHA-256
    `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.
- command: packet-focused authority/preimage `pytest` command
  - exit status: `2` before Python startup in the managed sandbox
  - result: existing external uv-cache read denied; no test executed and no
    repository or environment write occurred.
- command: packet-focused authority/preimage `pytest` command with access to the
  existing local uv cache
  - exit status: `0`
  - result: `290 passed in 27.73s`.
- command: focused Ruff format check
  - exit status: `0`
  - result: `1 file already formatted`.
- command: focused Ruff lint
  - exit status: `0`
  - result: `All checks passed!`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `25/25 PASS`; configured remotes zero.
- command: locked/no-sync bytecode-disabled independent reconstruction
  - exit status: `0`
  - result: exact eight decision keys, seven candidate keys, ten bindings,
    fifteen unique ordered rows, `4/4/7` state split, exact four supported
    names, all supported inputs accepted, semantic restatement true, actual
    state `DECISION_ONLY`, no cross-authority path, and no product path.
- command: locked/no-sync bytecode-disabled applicability challenge
  - exit status: `0`
  - result: `action_none=True`, `action_bool=True`,
    `position_none=True`, `position_empty=True`,
    `position_out_of_range=True`, `match_none=True`, and
    `resolved_invalid_ids=True`; this is the P2 evidence.
- command: shell-only terminal `.pyc` / `__pycache__` inventory
  - exit status: `0`
  - result: `1,150` `.pyc`, path-list SHA-256
    `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`;
    `150` `__pycache__`, path-list SHA-256
    `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.
    This differs from the preflight by five net-new `.pyc` paths and invalidates
    the no-write review harness.

## Artifacts/evidence

- review:
  `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
- decision physical/canonical SHA-256:
  `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`
- candidate physical SHA-256:
  `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`
- candidate canonical SHA-256:
  `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`
- focused contract physical SHA-256:
  `976eeea142ee96d8c4274bb22dd8637c7486c6a1b71aec591f69962117501411`
- recommendation: `REWORK`
- findings: `P0=0`, `P1=0`, `P2=2`

## Risks

- Until the focused applicability proof rejects invalid canonical identifiers
  and non-accepted position evidence, a later implementation could pass this
  packet gate while counting evidence the frozen authority does not accept.
- Feature acceptance and all later authority/product work remain blocked.
- The current review run cannot become acceptance evidence because its terminal
  bytecode inventory differs from its preflight inventory.

## Follow-up items

- Bounded producer rework: preserve the exact decision/candidate bytes; strengthen
  only `tests/contracts/test_w04_supported_feature_authority.py` so applicability
  requires valid accepted identifier and position evidence, with explicit
  negative cases reproducing every value in this review challenge.
- Fresh independent review on the same fixed R1 route after master readback and
  bounded rework, beginning only when a stable bytecode inventory can be held
  through the review.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no sync, install,
  dependency, `pyproject.toml`, or `uv.lock` change occurred.
- no edits outside `allowed_paths`: confirmed; only the two exact reviewer-owned
  paths were created.
- no delegation: confirmed.
- no self-approval: confirmed; recommendation is independent `REWORK`, not
  acceptance.
- no candidate, test, predecessor, preimage, acceptance, cross-authority,
  identity, Bronze, Silver, Gold, build, product, network, cloud, container,
  endpoint, hosted-CI, deployment, or external-service work: confirmed.

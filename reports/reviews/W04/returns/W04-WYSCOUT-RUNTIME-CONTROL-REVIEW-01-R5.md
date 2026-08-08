# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R5`
- objective: Freshly and independently verify the sole R5 complete
  cache-directory lstat correction and every retained exact runtime-control
  predicate without modifying producer bytes.

## Decision

- verdict: `PASS`
- findings: `P0/P1/P2 = 0/0/0`
- review artifact:
  `reports/reviews/W04/wyscout-runtime-control-independent-review-R5.md`

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R5.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R5.md`

## Summary

- Verified all six fixed SHA-256 bindings before review and unchanged after the
  last bounded command; producer bytes remained read-only.
- Confirmed both independent collectors construct exact ten-field cache-directory
  rows from one no-follow `lstat`, compare complete rows at retained boundaries,
  keep them outside stable identity, and preserve zero child PYC content reads.
- Independently reproduced exact-row equality plus same-path replacement,
  same-inode clock, link/size/entry, directory-symlink, and mode attacks for both
  collectors. Every mutation differed or rejected as required.
- Independently reconstructed equal child/launcher authority, the exact twenty-
  component count sequence, 81 selected wheels, 9,595 mapped destinations, 5,859
  PYC source rows, four orphan predicates, and equal live ownership semantics over
  1,185 PYC plus 151 cache directories.
- Reproduced exact Bandit data and Greenlet headers mappings with singular
  same-owner mode/hash/size equality.
- The complete final-hash suite passed `203 passed in 114.29s`; the isolated actual
  two-run admission passed `1 passed in 30.38s`, including immutable replay,
  projection/inverse, no rebuild, and no real-root publication.
- Identical shell pre/post inventories: site `1,087` pycs / `131` caches, digest
  `65008a9a79e39e50ca20f01c917c3ddf1554f0cf35eb27c523efeed204a0815d`;
  repository `98` pycs / `20` caches, digest
  `d39602d310be5fb5ccd8f2e86715a468e8502996b87d74b2fd32dfadec9822d2`.

## Tests run

- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: three files already formatted.
- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed.
- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: no issues in three source files.
- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: exactly `203 passed in 114.29s`.
- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_runtime_control.py::test_actual_admission_is_two_run_deterministic_idempotent_and_no_rebuild -vv`
  - exit status: `0`
  - result: `1 passed in 30.38s`.
- command: independent `uv run --locked --no-sync python -S -B -c ...`
  cache-directory attack helper
  - exit status: `0`
  - result: both exact rows and replacement/clock/link-size-entry/symlink/mode
    attacks passed for child and launcher.
- command: corrected independent `uv run --locked --no-sync python -S -B -c ...`
  authority/mapping/PYC helper
  - exit status: `0`
  - result: equal authorities/counts/PYC policy, 81 wheels, 9,595 mappings, and
    equal canonically sorted live ownership projections.
- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings.
- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<isolated> UV_NO_SYNC=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks and zero failures.
- command: shell-only preflight/postflight lstat/header/content inventories and
  final `sha256sum` binding recheck
  - exit status: `0`
  - result: inventories identical, both real roots absent, and all six bindings
    exact.

The first sandboxed static-check attempts exited `2` only because existing uv-cache
read access was denied; the approved locked/no-sync reruns passed. A reviewer-only
authority helper also initially exited `1` at its final normalized tuple assertion
because the projection retained different full-row sort orders. All prior equality
assertions had passed; canonically sorting the common projections corrected the
review helper and the rerun exited `0`. Neither event changed producer or repository
authority bytes.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/wyscout-runtime-control-independent-review-R5.md`
- mandatory reviewer return:
  `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R5.md`
- fixed producer implementation/test/return artifacts remain at packet-bound
  hashes.

## Risks

- No known residual P0, P1, or P2 defect within the R5 packet.
- The previously documented same-trust-domain transient replace-and-restore
  residual remains unchanged and is not broadened by this correction.

## Follow-up items

- none

## Scope confirmation

- producer bytes read-only: confirmed
- no real-root code-manifest or admission publication: confirmed
- no Git mutation or unauthorised Git operation: confirmed; only the required
  local-only verifier's embedded read-only predicates ran
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside the two allowed review paths: confirmed

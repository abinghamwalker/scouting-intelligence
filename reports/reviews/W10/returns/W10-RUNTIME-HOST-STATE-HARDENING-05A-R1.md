# Subagent return

## Task

- task_id: `W10-RUNTIME-HOST-STATE-HARDENING-05A:R1`
- objective: Implement independent portable PYC/cache security projections and bounded
  audit-only classifications while preserving every W04 runtime-security witness.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W10/returns/W10-RUNTIME-HOST-STATE-HARDENING-05A-R1.md`

## Summary

- Added exact frozen post-W04 source rosters independently to child and launcher. Same-tag
  cache rows outside that roster still fail closed and gain no source authority.
- Kept the exact R12 `cpython-314` predicate ahead of every generic classification. Unrelated
  foreign-interpreter rows are bounded metadata-only audit rows; an extra foreign row for the
  protected R12 source remains rejected.
- Preserved a stale pre-rename W10 integration cache as explicit negative evidence through one
  exact retired-cache predicate. The retired source spelling is absent from the active roster,
  the source must remain absent, and predicate substitution fails closed.
- Added independent child/launcher portable security projections with no cross-import or
  cross-call. Repeated admission and outer-control checks compare stable authority plus the
  protected portable projection, while raw device/inode/clock/cache-directory metadata remains
  retained only as audit evidence.
- Kept the raw inventory digest in completion health, labelled it
  `AUDIT_ONLY_ZERO_READ_USE`, and added a portable security-projection digest. Neither raw nor
  portable health evidence enters the stable/product authority.
- Added witnesses for bounded same-tag and foreign audit rows, exact-roster/predicate
  substitution rejection, child/launcher projection equality, portable host-metadata drift,
  raw-versus-portable health digests, retained outer snapshots, and zero cache mutation paths.
  No existing W04 test was removed, skipped, xfailed, or weakened.

## Tests run

- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `296 passed in 118.33s (0:01:58)`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_v2_aggregates.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `116 passed in 53.01s`
- command: `uv run pytest -q tests/security/test_w04_wyscout_vertical_slice_publication.py tests/e2e/test_w04_wyscout_vertical_slice.py`
  - exit status: `0`
  - result: `39 passed in 1389.50s (0:23:09)`
- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `3 files already formatted`
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`

## Artifacts/evidence

- `reports/reviews/W10/returns/W10-RUNTIME-HOST-STATE-HARDENING-05A-R1.md`
- Pre-implementation reproduction: `3 failed, 284 passed`; each failure was an accepted
  post-W04 same-tag cache row being treated as a required stable source row.
- Final full runtime evidence: `296 passed`, including the three original production-path
  failures and every retained W04 negative/substitution/zero-read/use witness.

## Risks

- Raw inventory hashes intentionally remain host-specific audit diagnostics. Portable security
  equality excludes raw host clocks, inodes, devices, cache-directory sizes/link counts, and
  unprotected audit-row sizes; unsafe file type, symlink, mode, hardlink, grammar, containment,
  exact R12 metadata, and exact predicate/roster changes still fail before projection.
- The security/E2E gate is CPU-heavy (`23:09`) but completed without timeout or diagnostics.

## Follow-up items

- none

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`

## Master remediation after independent review

The independent review exercised runtime admission after normal complete-suite imports and found
the initial post-W04 cache roster incomplete. The master reconciled both independent exact copies
with all 42 additional live-source caches observed from ordinary W05–W10 tests, added a
seven-source cross-layer regression and preserved unmanifested current-tag rejection. The final
retained runtime-control suite passed 298/298 from the naturally materialised repository state.

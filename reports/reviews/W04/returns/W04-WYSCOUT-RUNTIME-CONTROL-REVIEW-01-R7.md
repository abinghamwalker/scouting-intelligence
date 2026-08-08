# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R7`
- objective: Freshly and independently adjudicate the R7 admitted-parent,
  exact-owner and pre-guard file-backed-module-census correction, including the
  disclosed pre-baseline operational-PYC rewrite, without editing producer/PYC
  bytes or publishing to real roots.

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R7.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R7.md`

## Summary

- Decision: `REWORK`, with `P0/P1/P2 = 0/2/0`.
- Verified every fixed binding and retained the R7 no-follow stdlib/encodings
  descriptor chain, exact owner/mode/leaf bytes/EOF/stability correction and all
  frozen R6 tuple/environment/argv/FD/prefix/chronology/product predicates.
- Found `W04-RUNTIME-R7-P1-01`: a fourth module with forged
  `__spec__.origin="built-in"` and unrelated `__file__` bypasses the pre-guard
  census because the remainder is not authenticated against resident
  built-in/frozen interpreter authority.
- Found `W04-RUNTIME-R7-P1-02`: the outer audit guard denies every in-place PYC
  open, but the direct outer authority collector immediately opens every PYC to
  hash it. CPython exposes the `Path` operand to the audit event as `str`, so the
  admitted real outer path is constructively rejected before admission.
- Adjudicated the disclosed PYC rewrite as a contained, fully disclosed
  producer process/scope defect. The PYC stayed operational-only, excluded from
  stable identity, and byte-identical across the complete review; it was never
  cleaned, restored, rewritten, or concealed.

## Tests run

- command: locked/no-sync Ruff format/check and mypy over the three frozen review
  files, with bytecode disabled and caches disabled/redirected
  - exit status: `0`
  - result: formatted; lint clean; no type errors
- command: exact required six-file `pytest -q -p no:cacheprovider` population
  through locked/no-sync `python -B`
  - exit status: `0`
  - result: `244 passed in 1474.71s (0:24:34)`
- command: focused exact-uv R7 direct-launch population
  - exit status: `0`
  - result: `14 passed, 75 deselected in 3.48s`
- command: independent disguised-built-in/file-backed exact-uv attack in a
  pytest temporary root
  - exit status: `1` (expected review assertion failure)
  - result: attack passed the census and reached later missing `__init__.py`
  rejection instead of the mandatory pre-guard census rejection
- command: locked/no-sync `python -B` CPython `os.open(Path)` audit-target probe
  - exit status: `0`
  - result: audit target was `str`, authenticating constructive PYC denial
- command: Bandit, import-linter with no cache, and local-only verifier
  - exit status: `0`
  - result: no Bandit findings; 3 kept/0 broken; local-only PASS 25/25
- command: identical shell-only complete PYC preflight/postflight and final
  fixed-binding recheck
  - exit status: `0`
  - result: all counts, inventory bytes/digests and eight bindings exact

## Artifacts/evidence

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R7.md`
- selected site PYC inventory: `1087` files, `131` cache directories, digest
  `901abd68c87e15406f70097884dbeb093647bf815a0a05b8ba0c976efdb9bb91`
- repository PYC inventory: `111` files, `21` cache directories, digest
  `033830d929d1c55cd1dd08884d0a017da28b475a35f9878264b4d2abe8e5b0fc`
- disclosed launcher PYC SHA-256:
  `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`

## Risks

- The accepted real-root runtime must not be invoked until both P1 findings are
  corrected, freshly reviewed, and master-accepted. Current direct outer control
  cannot constructively pass its existing PYC inventory.
- The producer's direct exact-uv tests use a deliberately incomplete isolated
  repository and therefore do not prove unmocked real-root completion.

## Follow-up items

- Bounded R8 producer correction authenticating built-in/frozen remainder cases
  and removing the outer Python PYC byte-read/guard contradiction without
  weakening bytecode denial or moving PYC bytes into stable identity.
- Add disguised built-in/frozen/alias attacks and a positive exact outer fixture
  with present classified PYC rows, then obtain a fresh independent review.

## Scope confirmation

- no Git operations: confirmed; no direct Git command was run
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed; only the two review paths above
  were written, and temporary attack evidence remained under `/tmp`/pytest roots

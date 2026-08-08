# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R20`
- objective: Produce the standalone R20 replacement that preserves every accepted
  R19 closure while correcting executable-shebang authority with an exact
  constructive `python`/`python3` selector, executable census v3, and
  code/environment manifest v15.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R20.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R20.md`

## Summary

- Produced a complete standalone R20 replacement of R19. It preserves all accepted
  R19 merits and records the valid R12 P1 finding without self-approving R20.
- Corrected Class-E/P shebang authority constructively: exactly four complete
  `(owner, entry-point name, group, target)` tuples select `python3`; the other 29
  Class-E rows plus the sole Class-P row select `python`; Ruff remains the sole
  Class-W binary. The complete executable census remains 35 rows, 33 E/one P/one
  W, across 21 owners, with an exact 30-`python`/four-`python3` text-wrapper
  split.
- Bound the four current `python3` rows to their exact owner, RECORD row, target,
  size, complete SHA-256, RECORD digest, regular/non-symlink/single-link/mode
  predicates, current first line, and deterministic post-first-LF template body.
- Preserved the exact three-alias topology and
  `w04-venv-wrapper-interpreter-alias-v2`. `python` and `python3` are distinct
  selected roles even though contained `python3 -> python` reaches the same frozen
  physical Python 3.12.12 executable; `python3.12` and every other Class-E/P
  shebang spelling remain forbidden.
- Defined two exact Class-E templates and distinct root-independent normalization
  tokens: `#!<W04_VENV_WRAPPER_PYTHON>\n` and
  `#!<W04_VENV_WRAPPER_PYTHON3>\n`. Every later byte is retained unchanged; no
  generic either-alias, realpath-only, `sys.executable`, fallback, repair, env,
  flag-bearing, or external-root route is admitted.
- Bumped only `w04-installed-executable-census-v3` and
  `w04-code-environment-admission-v15`. Propagated v15 through admission
  input/result, canonical manifest, readback/equality, component proof, tests,
  health, projection/final recheck, two-root proof, gate, and ledger. There is no
  stale v14 acceptance route.
- Preserved the exact 119-pair roster and `10/11/26/47/18/4/3` decomposition,
  strict UUID `ActorId`, twelve-field/six-row possession closure, approved field
  contract-test path, 17 resources, stable `v4/v2/v2` process/bootstrap versions,
  `16/8/10/25/25/20` cardinalities, 24-key intersection, twenty component proofs,
  H1/H2 construction, one-SHA build-ID algorithm, sole writers, and two-commit
  ledger.
- Preserved the R19 operational pyc evidence snapshot and incident: site `1,086`
  and repository `58` in `19` cache directories, with each future bounded run
  governed by its own complete shell preflight and byte-identical postflight.
- Created no implementation script, configuration, product data, orchestration
  mutation, dependency/lock change, parent-workspace path, cleanup, or repair.

## Tests run

- command: exact packet acceptance shell block around
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -S -B -c "import os,sys; from pathlib import Path; ..."`
  - exit status: `0`
  - result: PASS; R20 is `245,957` bytes, exceeds `230,000`, contains executable
    census v3, manifest v15, the `python3` stable token, and all four exact
    exceptional wrapper names. Immediate counts remained site/repository
    `1,086`/`58`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; controlling JSON reported `status: PASS`, `failures: []`, and
    all 25 local-only/one-root-uv checks passed. Immediate counts remained
    site/repository `1,086`/`58`.
- command: complete read-only shell inventory before Python and after each bounded
  helper, recording every pyc path, kind, size, mode, link count, device/inode,
  modification/change clocks, first 16 bytes, and complete SHA-256, plus every
  `__pycache__` directory row; compare with `cmp`
  - exit status: `0`
  - result: PASS; every postflight was byte-identical to preflight: site
    `1,086` pycs in `131` cache directories and repository `58` pycs in `19`
    cache directories. No creation, deletion, rename, content/header, mode/link,
    identity, or directory drift occurred.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R20.md`
- Exact selected wrapper sets: 29 E plus one P use `python`; four E use
  `python3`; Ruff is W.
- Exact exceptional rows: `detect-secrets`, `detect-secrets-hook`, `httpx`, and
  `pip-licenses`.
- Stable schema versions: `w04-local-control-bootstrap-v4`,
  `w04-outer-environment-bootstrap-v2`,
  `w04-child-environment-input-v2`,
  `w04-installed-executable-census-v3`, and
  `w04-code-environment-admission-v15`.
- Stable cardinalities retained: `16/8/10/25/25/20`.
- Full preflight/postflight inventory equality: site `1,086/131`, repository
  `58/19`.

## Risks

- R20 remains an implementation candidate pending master and separate independent
  review; this return is not an approval.
- The four absolute current-host shebang lines and complete physical wrapper
  digests are operational evidence. Stable identity is limited to the constructive
  tuple selector, exact alias roles/chains, normalized template bytes, and closed
  census row authority.
- No cleanup or repair was performed. Future validity continues to depend on each
  bounded run's own complete preflight/postflight identity.
- The first sandboxed acceptance attempt could not read the external uv cache and
  did not start Python. Its complete shell postflight was identical; the same
  locked/no-sync command was then rerun with the required cache-read authority and
  passed.
- No implementation, configuration, orchestration, source, test, dependency,
  lockfile, provider, network, data, migration, Git, deployment, or self-approval
  action was performed.

## Follow-up items

- `none`

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`

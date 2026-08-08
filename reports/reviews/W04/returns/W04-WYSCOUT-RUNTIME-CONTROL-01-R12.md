# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01`
- revision: `R12`
- objective: Complete only the authorized six-failure correction: classify the
  retained foreign-cache-tag PYC by exact zero-read denial metadata in both
  independent collectors, refresh the mechanically inherited v2 aggregate body
  constants, and correct the exposed Darwin empty-directory link-count
  invariant.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R12.md`

## Summary

- Added one exact predicate in both independently implemented PYC policy and
  inventory paths for
  `scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc`:
  `REPOSITORY_FOREIGN_CACHE_TAG_DENIED` under
  `FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ`, tag `cpython-314`, mode `0o644`,
  link count `1`, and size `190312`.
- Both collectors now classify that path by contained `lstat` metadata only.
  They never open, read, hash, inspect a header/magic value, import, execute,
  repair, rename, delete, or otherwise mutate the PYC. The emitted denied row
  has `source_authority=None`, no owner, and no digest; the required stable
  source is recorded separately as a prerequisite and grants the PYC no source,
  component, build, product, or execution authority.
- Tightened the prerequisite source binding to one exact seven-field
  `REPOSITORY_CODE_MANIFEST` row for
  `scripts/admit_wyscout_v5_runtime.py`: exact owner/path, normal and pytest
  cache-name forms, valid SHA-256 shape, exact source size, singular regular
  mode-`0644` no-follow metadata, and no additional fields or duplicate row.
- Kept all other foreign tag/path cases fail closed. Added dual-collector
  positive and adversarial coverage for missing or substituted predicate fields,
  path escape, wrong tag/path/role/class/policy/mode/size/source authority,
  duplicate/missing predicate, missing/wrong/malformed/duplicate source row,
  wrong source owner/class/path/digest/size/mode, source symlink/hardlink, denied
  file missing/wrong path/wrong tag/extra foreign tag/mode/size/symlink/hardlink,
  and attempted open/read/use.
- Refreshed only the launcher's mechanically inherited accepted descriptor-only
  v2 body constants and their frozen test values:
  - schema bundle:
    `a0daa1a22619bf2719ff67d1a22f4495a8de0ea8884f53bb5f05276c9b71ddc0`
  - product contract:
    `a50dd67b5ab989c783d67cda3cc0fe15229b6991de342d74bbdc3c40a465c832`
- The two real preparation regressions then advanced past the original PYC
  failure and exposed one bounded physical evidence defect: an empty mode-`0700`
  Darwin directory has exact `st_nlink=2`, while the validator incorrectly used
  file-style `1`. Corrected the exact invariant to `2` and added a coherent
  false-evidence rejection test. This changes no logical product, manifest,
  receipt, build formula, digest meaning, or execution behavior.
- Applied repository Ruff formatting only to the three allowed implementation
  and test files after the final controlling steer. No further runtime cycle or
  host-state rework was opened.

## Tests run

- command: focused dual-collector foreign-PYC and existing PYC census tests
  before final formatting
  - exit status: `0`
  - result: `87 passed, 199 deselected in 0.50s`
- command: focused exact outer no-read and refreshed v2 aggregate binding tests
  - exit status: `0`
  - result: `2 passed, 284 deselected in 0.78s`
- command: first four-case real-admission regression rerun
  - exit status: `1`
  - result: the two retained-authority cases passed; the two preparation cases
    advanced past the foreign PYC and exposed the exact Darwin directory
    `st_nlink=2` validator defect (`2 passed, 2 failed in 34.41s`)
- command: focused process-evidence and foreign-PYC proof after bounded
  directory-link correction
  - exit status: `0`
  - result: `82 passed, 205 deselected in 0.32s`
- command: final two preparation regressions after directory-link correction
  - exit status: `0`
  - result: `2 passed, 285 deselected in 56.44s`
- command: final-byte rerun of the other two retained-authority regressions
  - exit status: `0`
  - result: `2 passed, 285 deselected in 10.93s`
- command: complete runtime-control unit suite before final mechanical formatting
  - exit status: `0`
  - result: `287 passed in 90.74s`
- command: companion W04 build-contract, vertical-slice publication-security,
  and end-to-end vertical-slice suites before final mechanical formatting
  - exit status: `0`
  - result: `95 passed in 1443.76s (0:24:03)`
- command: final `ruff format` followed by `ruff format --check` over the exact
  three changed source/test paths
  - exit status: `0`
  - result: `3 files reformatted`; repeated check: `3 files already formatted`
- command: final `ruff check` over the exact three changed source/test paths
  - exit status: `0`
  - result: `All checks passed!`
- command: final `mypy` over the exact three changed source/test paths
  - exit status: `0`
  - result: `Success: no issues found in 3 source files`
- command: smallest affected post-format foreign-PYC, process-evidence, aggregate
  binding, exact child/launcher row, and zero-read tests
  - exit status: `0`
  - result: `85 passed, 202 deselected in 0.37s`

Every producer Python/pytest execution set `PYTHONDONTWRITEBYTECODE=1`. Synthetic
PYC test bytes were created only below pytest temporary roots. No producer test
opened or mutated the retained incident PYC, and no complete-gate rerun was
performed before review/master acceptance.

## Artifacts/evidence

- governing correction authorization SHA-256:
  `7a53b093388567947154c04969c0c40e314360ac87c3bfd8ba9459f651eef41c`
- master-derived v2 preimage verification SHA-256:
  `5fd5259ea305d348909760e5f1cd3778b0bc9400697b926a0b6f25dadcf6faf2`
- final candidate SHA-256 values:
  - `scripts/admit_wyscout_v5_runtime.py`:
    `db6ffbada5e271310b2b2495b264475d0ace27dfe0e4a0b35077a471fbde5be0`
  - `scripts/launch_wyscout_v5.py`:
    `827714c8baefbf37fe2f216972d00027d8931df45ba95e48002fee5a168a1353`
  - `tests/unit/test_w04_wyscout_runtime_control.py`:
    `8083ea75b0ddfe3939b9fad306bbb612ce0e95da7be40a9dc8ee10fe3a1d4392`
- failed-gate shell-only pre/post preservation evidence inherited unchanged:
  - selected-site PYC: `1218` rows, SHA-256
    `bd0b8036ffff7542a4216db800622c9379e953d7cbd38b45ab464636ca4001dd`
  - repository PYC: `133` rows, SHA-256
    `d3f27229f8b43fd3fc1aba948462b6fb8a872790f4def522e494090ff444ff8d`
  - retained `data/**` and `runs/**`: `272` rows, SHA-256
    `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c`
- retained incident PYC shell-observed digest remains incident evidence only and
  is not present in either collector's policy or emitted inventory row.

## Risks

- Fresh independent R12 review and master acceptance remain required before the
  mandatory complete gate is rerun.
- Exact `st_nlink=2` is the governed Darwin empty-directory physical invariant.
  Cross-host directory-link portability assurance is deferred to W10 hardening
  and is not an R12 or W04 acceptance dependency under the final controlling
  steer.
- A later accepted repository-code manifest, build ID, products, manifests, and
  receipts may change only as mechanical consequences of the corrected governed
  source and accepted descriptor-only preimage bytes. This producer performed no
  real-root derivation, rebuild, publication, or checkpoint.

## Follow-up items

- Fresh independent R12 review and master acceptance only; R12 is terminal and
  no R13 or additional W04 runtime authority is requested.

## Scope confirmation

- no Git operations: confirmed
- no dependency, lockfile, network, provider, credential, container, cloud,
  deployment, or publication change: confirmed
- no edits outside the R12 allowed paths: confirmed
- no retained PYC, `data/**`, `runs/**`, manifest, product, receipt, or real-root
  staging mutation: confirmed

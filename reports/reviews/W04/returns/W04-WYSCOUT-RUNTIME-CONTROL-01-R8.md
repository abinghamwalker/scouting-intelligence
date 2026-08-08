# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01-R8`
- objective: Correct only `W04-RUNTIME-R7-P1-01` and
  `W04-RUNTIME-R7-P1-02` by authenticating the complete first-user resident
  module roster and making the outer PYC census strictly metadata-only while
  retaining unconditional Python-role PYC denial.

## Files changed

- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R8.md`

## Summary

- Replaced mutable-origin-only pre-guard classification with the exact ordered
  23-name CPython 3.12.12 startup roster and a complete distinct-object census.
  Every admitted built-in row must be registered in resident
  `sys.builtin_module_names` and use the exact resident `BuiltinImporter`, with
  exact spec/name/origin/location and absent file/cache shapes. Every frozen row
  must satisfy resident `_imp.is_frozen`, use the exact resident
  `FrozenImporter`, and match its exact root-relative file-or-`None` and absent
  cache shapes.
- Authenticated all three distinct encoding rows through the exact resident
  `SourceFileLoader` type and loader object, exact spec/name/origin/file,
  control-prefix cache candidate, package parent/location, and loader name/path.
  The exact `__main__` spec/file/cache/package and source-loader case is also
  closed. Extra, missing, reordered, duplicated, aliased, disguised built-in,
  forged-frozen, loader, spec, file, and cached substitutions now fail before
  guard installation.
- Replaced only launcher `_independent_pyc_inventory` byte/header/hash reads with
  one no-follow `os.stat` snapshot per present PYC. It requires a real regular
  mode-`0644`, link-count-one row and binds the child collector's exact complete
  operational row: class, role, path, source mapping, device, inode, size,
  `mtime_ns`, and `ctime_ns`. Exact orphan size/source-absence and complete cache
  directory rows remain enforced. Launcher and frozen admission-child collectors
  now return byte-for-byte equal rows on identical site/repository fixtures.
- Preserved the unconditional installed `.pyc`/`.pyo` audit denial. An isolated
  audit subprocess proves classified site and repository rows complete with zero
  PYC open events. A direct exact-uv fixture contains a classified site PYC plus
  a `/bin/cp` copy of the disclosed repository launcher-PYC row, proves the
  metadata census returns under the installed denial, and reaches a deliberate
  later control-flow marker without PYC access or real-root publication.
- Retained every R7 descriptor/owner/parent/leaf/source/tuple/environment/argv/
  FD/prefix/chronology attack and added direct disguised built-in-with-file,
  unregistered built-in-without-file, forged-frozen, unregistered alias, and
  loader/spec/file/cached attacks. The admission child, disclosed operational
  PYC, tuple fields, environment algorithm, child/rebuild behavior, stable source
  map, logical contracts, products, dependencies, lock state, and digest meaning
  remain unchanged.

## Tests run

- command: `uv run --locked --no-sync ruff format --check scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run --locked --no-sync ruff check --no-cache scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run --locked --no-sync python -B -m mypy scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run --locked --no-sync python -B -m pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `257 passed in 1476.00s (0:24:35)`
- command: `uv run --locked --no-sync python -B -m bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `uv run --locked --no-sync lint-imports --no-cache`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks, zero failures
- command: focused exact-uv/authenticated-roster/audit population through
  locked/no-sync `python -B`, with pytest cache disabled
  - exit status: `0`
  - result: `26 passed, 76 deselected in 6.95s`
- command: focused PYC population through locked/no-sync `python -B`, with
  pytest cache disabled
  - exit status: `0`
  - result: `22 passed, 80 deselected in 0.89s`

All Python-backed commands used `PYTHONDONTWRITEBYTECODE=1` and an empty
`/tmp/w04-r8-...` `PYTHONPYCACHEPREFIX`; direct Python invocations also used
`-B`. Ruff, mypy, pytest, and import-linter caches were disabled or redirected
under `/tmp`.

## Artifacts/evidence

- `orchestration/task_packets/W04-WYSCOUT-RUNTIME-CONTROL-01-R8.yaml`:
  SHA-256 `6a16ff130a802dafe924a4a47011bc08b6e1eed3f7c7e6b30ebf4df32f8c00d8`
- `scripts/admit_wyscout_v5_runtime.py`: unchanged SHA-256
  `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
- `scripts/launch_wyscout_v5.py`: SHA-256
  `e7cf10d5f11871bc48911a5dc9ea8b58ce9a6477e6df0935475f053874b6e2d5`
- `tests/unit/test_w04_wyscout_runtime_control.py`: SHA-256
  `01007463ac8cb52d67bdfb2b6784f36fab9cdf7a8ddf35c24a9149512d3707e0`
- The complete identical shell preflight/postflight PYC inventory is site
  files/directories `1087/131`, digest
  `819de2cdba2f81c2cc505a46d39cc51bdbda884c01c8db4a784e6d36783f430b`,
  and repository files/directories `111/21`, digest
  `ee0920cef338cece5f6400f8981763234408c3567c05ad656a567b460f3cbbfe`.
- `scripts/__pycache__/launch_wyscout_v5.cpython-312.pyc` remained exact across
  implementation and the complete gate: mode `0644`, link count `1`, size
  `199084`, device `16777231`, inode `91632142`, mtime/ctime `1785700057`,
  SHA-256 `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`.

## Risks

- The direct exact-uv present-PYC proof uses an isolated repository and a
  deliberate post-census control-flow marker. It proves the actual collector can
  return with classified PYC rows under unconditional denial, but intentionally
  does not claim an unmocked real-root admission/rebuild or publication.
- PYC magic/header/content SHA-256 remain shell/master operational evidence, not
  Python-role reads or stable digest meaning. Ordinary content/header mutation
  changes bound clocks and fails metadata equality; adversarial preservation of
  all metadata is still caught only by the required shell pre/post byte census.
- Fresh independent R8 review and master acceptance remain required before any
  real-root execution.

## Follow-up items

- Fresh independent R8 review and master acceptance; no producer-side follow-up.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed; the admission child and disclosed
  repository launcher PYC remained byte-for-byte unchanged

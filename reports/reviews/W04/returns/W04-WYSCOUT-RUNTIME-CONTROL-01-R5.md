# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01-R5`
- objective: Close the sole R4 finding by binding complete no-follow cache-directory
  lstat identity and clocks independently in both operational PYC inventories while
  preserving stable authority meanings and zero child PYC content reads.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R5.md`

## Summary

- Verified all six R5 fixed bindings exactly before editing: R4 admission child
  `c91f98c8d02a647d1eada8636f864382c6c7468c2d9b9b61cff51db92ac3f94e`,
  launcher `5c4c081b5b5049de6f9aad444e95ccf2e4d38fa7484d56add67cd1cb03b193a0`,
  tests `215d4c08af21e2768a98c16defa80c4bfefa44fb690dbe1fbc295cea254f0bad`,
  producer return `959fbdeb9b5dd3800b4d007227ccfd29c3ed798afbcf187b518736144f2291ee`,
  R4 review `74e5ff009bac72196739551f4c1aca724f9710636cce39ab429da1394d4514ab`,
  and R4 reviewer return
  `926bfbb77f6f3561e94f2f75f3e5113266748d02e55a01d36505ec5e8cf4156f`.
- Both independently implemented PYC collectors now build every
  `CACHE_DIRECTORY` row from one `os.lstat` result and bind exact role, relative
  path, entry kind, device, inode, mode, link count, size, mtime, and ctime. Both
  retain the real non-link mode-`0755` predicate.
- The existing child reconstruction/pre-result and launcher reconstruction
  pre/post equality boundaries compare the enriched complete rows automatically.
  The rows remain operational and are not added to the stable PYC policy or any
  stable identity digest.
- The child collector still performs no PYC content open, read, header read, or
  hash and does not call the launcher collector. All R4 classification, source-map,
  orphan, PEP 427 mapping, and stable digest formulas remain unchanged.
- Added direct child and launcher evidence for the exact complete row, persistent
  same-path mode-`0755` directory replacement, same-inode clock drift,
  link-count/size/entry drift, directory symlink substitution, and unsafe mode.
- Frozen final source SHA-256 values after the last edit are admission child
  `cba67d6a143951cbeefa2e63063f5f09aab73f6ec435a1378fb2451d59950cb5`,
  launcher `d3ac8c84995c8475b0a4df983899ebf6b364f047dcbba45c411d55b62c808740`,
  and tests `61f1d770d1b662df0f30c6d4bc54aace9f0fa1069d32501c7d466be908b66fb4`.

## Tests run

- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py -k 'cache_directory'`
  - exit status: `0`
  - result: `12 passed, 56 deselected in 0.14s`; both collectors rejected or
    detected every exact R5 directory attack.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py -k 'pyc or cache_directory'`
  - exit status: `0`
  - result: `20 passed, 48 deselected in 0.10s`, including the zero-child-content-read
    and independent-collector predicates.
- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: three files already formatted.
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: no issues in three source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py::test_actual_admission_is_two_run_deterministic_idempotent_and_no_rebuild -vv`
  - exit status: `0`
  - result: final-hash isolated actual admission `1 passed in 29.79s` (`real 29.93s`).
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: complete final-hash population `203 passed in 111.41s` (`real 111.56s`).
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks and zero failures; main branch and zero remotes.

All Python-backed commands ran through `uv`; existing uv-cache access was read-only.
No sync, provider/network operation, dependency change, real-root publication, or
rebuild execution was performed.

## Artifacts/evidence

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R5.md`

## Risks

- No known residual defect within the R5 packet. Final acceptance remains subject
  to fresh independent review and master reproduction.
- Directory identity and clocks are intentionally operational and can differ
  across roots; they affect only bounded-run drift comparison, never stable build
  identity.

## Follow-up items

- Fresh independent R5 review of the frozen source/test/return hashes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no real-root write or publication: confirmed

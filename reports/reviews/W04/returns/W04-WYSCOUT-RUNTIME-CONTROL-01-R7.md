# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01-R7`
- objective: Correct only independent finding `W04-RUNTIME-R6-P1-01` by
  proving the exact pre-guard file-backed-module census and reading the three
  admitted encoding sources through retained no-follow stdlib-parent
  descriptors with exact owner and stable identity, without changing the
  accepted child, tuple, environment, product, digest meaning, or any real root.

## Files changed

- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R7.md`
- `scripts/__pycache__/launch_wyscout_v5.cpython-312.pyc` was an existing
  untracked operational-PYC artifact accidentally rewritten once by a
  pre-baseline `python -m py_compile` syntax check. It was not deleted,
  restored, further touched, or concealed; exact evidence is recorded below.

## Summary

- Added an inline first-user-code `sys.modules` census. It requires the exact
  distinct `encodings.aliases`, `encodings`, and `encodings.utf_8` objects with
  their accepted absolute origin/file spellings; permits only the exact
  `__main__` special row plus built-in/frozen remainder; and rejects a fourth
  file-backed module, duplicate object, origin alias, missing row, or other
  non-built-in/non-frozen resident entry before audit-guard installation.
- Replaced absolute source reopens with one retained descriptor chain from `/`
  through every `sys.base_prefix/lib/python3.12` component and then its
  `encodings` child. Every component is descriptor-relative `O_DIRECTORY` plus
  `O_NOFOLLOW`, is a real safe-mode directory with retained path/descriptor
  identity, and cannot transition from the admitted current owner back to
  another owner. The stdlib and `encodings` leaves require exact mode `0755`
  and the exact current admitted UID/GID.
- Opened only `__init__.py`, `aliases.py`, and `utf_8.py` relative to the
  retained `encodings` descriptor with `O_NOFOLLOW`. Each leaf requires exact
  current UID/GID, regular mode `0644`, link count one, exact size, complete
  positional bytes, exact EOF, and frozen SHA-256. Parent and leaf security-
  relevant `fstat` snapshots plus descriptor-relative path bindings must remain
  identical after all three reads. Device, inode, and clock observations remain
  operational and do not enter the complete v4 tuple or digest meaning.
- Added direct exact-uv attacks for a fourth file-backed module, duplicate
  encoding module object, accepted-origin alias, intermediate `encodings`
  symlink, retained-parent replacement, retained-leaf replacement, and
  simulated source-owner drift. The positive direct launch passes the exact
  census/owner/descriptor predicates and reaches the deliberately later
  isolated-repository runtime rejection. All retained R6 attacks remain green.
- The R6 admission child stayed byte-identical and no tuple field, environment
  algorithm, child behavior, dependency, lock, logical contract, product,
  digest formula, or real-root byte changed.

## Tests run

- command: `uv run ruff format --check scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `244 passed in 1474.91s (0:24:34)`
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `uv run lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks, zero failures
- command: focused exact-uv R7 direct-launch population under
  `python -B -m pytest`, with bytecode and pytest caches disabled
  - exit status: `0`
  - result: `14 passed, 75 deselected in 3.48s`

## Artifacts/evidence

- `scripts/admit_wyscout_v5_runtime.py`: unchanged SHA-256
  `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
- `scripts/launch_wyscout_v5.py`: SHA-256
  `7f49b838dd9298997dceb298f40c02a7a647f0373b56b1e3784f28b2633d36be`
- `tests/unit/test_w04_wyscout_runtime_control.py`: SHA-256
  `9ff4b47bd00c963652140ede0474e388d8b553234e5269b892e0cf84b9336927`
- `orchestration/task_packets/W04-WYSCOUT-RUNTIME-CONTROL-01-R7.yaml`:
  SHA-256 `db313fecc2389d34bfd387b6649ed3d919c6497610d475853fd3704e985ed05b`
- Immediately before the final bounded acceptance run, the complete shell PYC
  inventory was frozen as site files/directories `1087/131`, digest
  `819de2cdba2f81c2cc505a46d39cc51bdbda884c01c8db4a784e6d36783f430b`,
  and repository files/directories `111/21`, digest
  `ee0920cef338cece5f6400f8981763234408c3567c05ad656a567b460f3cbbfe`.
  The identical shell postflight reproduced all four counts and both digests
  byte-for-byte.
- The accidental pre-baseline rewrite affected only
  `scripts/__pycache__/launch_wyscout_v5.cpython-312.pyc`, now mode `0644`,
  link count `1`, size `199084`, SHA-256
  `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`.
  It invalidated the earlier repository PYC preflight digest
  `3b6d73fb9d6ef01d7e04c995e7256f46814f8ce2445ad4276b0e88fdb75a3b28`;
  per R20 Section 8.6.4, the complete inventory immediately before the bounded
  acceptance run above is the authoritative baseline. Every subsequent Python
  command used `PYTHONDONTWRITEBYTECODE=1`; direct Python commands also used
  `-B`, and caches were disabled or redirected to `/tmp`.

## Risks

- The pre-baseline operational-PYC rewrite is a disclosed producer process/scope
  defect for independent adjudication. It did not affect accepted source,
  dependency, lock, tuple, logical, product, digest-meaning, or real-root bytes;
  it was frozen without cleanup and the authoritative complete acceptance
  baseline/postflight are identical.
- Producer evidence intentionally does not write admitted real roots. The exact
  uv process tests prove the corrected first-user-code boundary in isolated
  roots and then reject deliberately incomplete later runtime authority. The
  master-owned real execution remains the sole authority for real publication.
- Required uv commands used sandbox escalation only to read the already admitted
  local uv cache. No network, dependency, provider, credential, or cost was
  introduced.

## Follow-up items

- Fresh independent R7 review and master acceptance before any real-root run.

## Scope confirmation

- no Git operations: no Git mutation or checkpoint; one read-only `git status
  --short` inspection was run while preserving the complete dirty tree
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: not confirmed; the single accidental
  pre-baseline rewrite of the existing untracked launcher PYC is fully disclosed
  above, was not cleaned/restored, and remained byte-identical across the
  authoritative final acceptance gate

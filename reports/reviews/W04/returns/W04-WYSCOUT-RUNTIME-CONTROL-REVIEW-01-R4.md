# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R4`
- objective: Freshly and independently verify the final R4 mapped external
  RECORD and actual-PYC corrections plus every retained R3 predicate without
  modifying producer bytes.

## Decision

- verdict: `REWORK`
- findings: `P0/P1/P2 = 0/1/0`
- review artifact:
  `reports/reviews/W04/wyscout-runtime-control-independent-review-R4.md`

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R4.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R4.md`

## Summary

- Verified all six fixed SHA-256 bindings exactly and rechecked the four R4
  producer artifacts unchanged after the last bounded review command.
- The complete final-hash population collected exactly 191 tests and passed
  `191 passed in 118.18s`; every static, security, import-boundary, and local-only
  gate also passed.
- Independently reconstructed equal child/launcher maps over 81 selected wheels
  and 9,595 destinations. Bandit's exact data row and Greenlet's exact headers
  row matched singular same-owner installed rows, bytes, digest, size, and mode.
- The isolated actual two-run admission passed `1 passed in 29.83s`, including
  twenty-component/count/repository equality, immutable replay, projection/
  inverse, no rebuild, and no real-root publication.
- Reproduced one P1 fail-open state: replacing a mode-`0755`
  `tests/__pycache__` at the same path changed inode and ctime/mtime but returned
  equal child and launcher inventories. Both cache-directory rows omit device,
  inode, link count, size, mtime, and ctime.
- Recorded the smallest R5 correction: bind complete cache-directory lstat rows
  in both operational inventories and add same-path replacement/clock plus
  link/mode/size attacks without adding child PYC content reads.
- Pre/post shell-only inventories were identical: site `1,087` pycs / `131`
  caches, digest `bb9bbe481f43fdf51ec6628a154e467f4e26f0bc835a3405c3970327266c991f`;
  repository `98` pycs / `20` caches, digest
  `c8f0019a59afbdfced37c95c7433ab09def222c5635e13792fdafbf5c2b56306`.

## Tests run

- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: three files already formatted.
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: no issues in three source files.
- command: required four-file pytest population
  - exit status: `0`
  - result: exactly `191 passed in 118.18s`.
- command: isolated `test_actual_admission_is_two_run_deterministic_idempotent_and_no_rebuild`
  - exit status: `0`
  - result: `1 passed in 29.83s`.
- command: no-site child-versus-launcher live PEP 427 reconstruction
  - exit status: `0`
  - result: equal maps over 81 wheels / 9,595 destinations; exact Bandit and
    Greenlet rows reproduced.
- command: isolated same-path cache-directory replacement attack
  - exit status: `0`
  - result: lstat identity/clocks changed, but both snapshots remained equal.
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `uv run python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks and zero failures.

All Python commands used `PYTHONDONTWRITEBYTECODE=1`, an isolated empty
`PYTHONPYCACHEPREFIX`, and `UV_NO_SYNC=1`. Required uv-cache reads used approved
read access; no sync or environment mutation occurred.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/wyscout-runtime-control-independent-review-R4.md`
- mandatory reviewer return:
  `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R4.md`
- fixed producer implementation/test/return artifacts remain at packet-bound
  hashes.

## Risks

- Both operational PYC collectors fail open to a persistent same-path
  cache-directory identity/clock replacement when type and mode remain accepted.
- All other challenged R2/R3 predicates passed, but they cannot offset the P1 or
  authorize build admission.

## Follow-up items

- Add complete cache-directory lstat metadata to both operational inventory rows,
  compare it across every reconstruction/pre-post boundary, and add exact
  identity/clock/link/mode/size attacks.
- Freeze R5 hashes, rerun the complete 191-plus-correction gate and actual two-run
  admission, and obtain fresh independent review.

## Scope confirmation

- producer bytes read-only: confirmed
- no real-root publication or rebuild execution: confirmed
- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside the two allowed review paths: confirmed

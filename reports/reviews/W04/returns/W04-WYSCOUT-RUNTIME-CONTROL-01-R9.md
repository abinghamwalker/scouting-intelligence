# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01`
- revision: `R9`
- objective: Correct only `W04-RUNTIME-R8-P1-01` by binding the governed
  startup roster to its exact earliest resident objects and completing the
  built-in/frozen package, parent, and search-location shape authority while
  preserving the accepted R8 roster and metadata-only PYC closure.

## Files changed

- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R9.md`

## Summary

- Made the first direct-execution statements require the exact ordered
  23-name startup roster and capture its exact ordered name/object-reference
  pairs before any helper definition. The same earliest block captures the
  exact resident `BuiltinImporter` and `FrozenImporter` objects.
- Captured immutable normalized `(name, __package__, spec.parent,
  spec.submodule_search_locations)` scalar tuples for all 19 governed
  built-in/frozen rows. The accepted startup shape is exact empty package,
  empty parent, and absent search locations for every row.
- Extended the full first-user verifier to require the live 23 ordered names
  and objects to be exactly the captured pairs by object identity, and to
  require both live importer authorities to be the exact captured objects.
  Every built-in/frozen row now matches its earliest shape snapshot plus all
  retained R8 registration, `is_frozen`, name, origin, loader, file, cache,
  location, and distinctness predicates.
- Added direct exact-uv attacks for fully shaped registered built-in and frozen
  object replacement; independent built-in and frozen package, parent, and
  search-location mutation; and both resident importer-authority mutations.
  Added a structural proof that the direct branch captures startup bindings
  before the first helper definition.
- Preserved all R8 encoding, owner/parent/leaf, tuple, environment, argv, FD,
  prefix, chronology, PYC-denial, and present-PYC cases. The admission child is
  byte-identical. The launcher PYC census remains strictly metadata-only and
  Python roles retain unconditional `.pyc`/`.pyo` read denial.

## Tests run

- command: `uv run --locked --no-sync ruff format --check scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run --locked --no-sync ruff check --no-cache scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run --locked --no-sync python -B -m mypy --cache-dir=/tmp/w04-r9-final-mypy scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run --locked --no-sync python -B -m pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `268 passed in 1485.40s (0:24:45)`
- command: `uv run --locked --no-sync python -B -m bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `uv run --locked --no-sync lint-imports --no-cache`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks, zero failures
- command: focused exact-uv earliest-object/complete-shape and direct-branch
  structure population through locked/no-sync `python -B`, with pytest cache
  disabled
  - exit status: `0`
  - result: `36 passed, 77 deselected in 10.08s`
- command: focused preserved-PYC population through locked/no-sync `python -B`,
  with pytest cache disabled
  - exit status: `0`
  - result: `22 passed, 91 deselected in 0.93s`

The seven required acceptance commands ran sequentially in the single retained
shell session `37785`. All Python-backed commands used
`PYTHONDONTWRITEBYTECODE=1` and the empty
`/tmp/w04-r9-final-pycache` `PYTHONPYCACHEPREFIX`; direct Python invocations
also used `-B`. Ruff, mypy, pytest, and import-linter caches were disabled or
redirected under `/tmp`.

## Artifacts/evidence

- `orchestration/task_packets/W04-WYSCOUT-RUNTIME-CONTROL-01-R9.yaml`:
  SHA-256 `d09461cc3c48191f977282c6aaf23c0ea983ea49c917054bc8390925b96634c7`
- `scripts/admit_wyscout_v5_runtime.py`: unchanged SHA-256
  `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
- `scripts/launch_wyscout_v5.py`: SHA-256
  `6211ff1cd0b51bdd3ab24fe26358077f46f1ad0526ff60126776606ca01243eb`
- `tests/unit/test_w04_wyscout_runtime_control.py`: SHA-256
  `12924b9905a8334c4a6f83bb00b170059be0bb965a1d3d6b4f0c09d364a95abf`
- Shell-only PYC census helper: `/tmp/w04-r9-pyc-census.sh`, SHA-256
  `2702b38453c95e428e9289cfc0bd6a9d0f1a748aeb33f1bad1e1c7033eaf4a6d`.
  It records relative path, entry type, mode, link count, size, device, inode,
  mtime, ctime, first 16 content bytes, and complete SHA-256 for every PYC/PYO,
  plus metadata for every `__pycache__` directory.
- Exact reproduction commands:
  - `/tmp/w04-r9-pyc-census.sh SITE /Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence/.venv/lib/python3.12/site-packages /tmp/w04-r9-site-pyc-pre.tsv`
  - `/tmp/w04-r9-pyc-census.sh REPO /Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence /tmp/w04-r9-repo-pyc-pre.tsv`
  - `/tmp/w04-r9-pyc-census.sh SITE /Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence/.venv/lib/python3.12/site-packages /tmp/w04-r9-site-pyc-post.tsv`
  - `/tmp/w04-r9-pyc-census.sh REPO /Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence /tmp/w04-r9-repo-pyc-post.tsv`
  - `cmp -s /tmp/w04-r9-site-pyc-pre.tsv /tmp/w04-r9-site-pyc-post.tsv`
  - `cmp -s /tmp/w04-r9-repo-pyc-pre.tsv /tmp/w04-r9-repo-pyc-post.tsv`
- Site preflight/postflight are byte-identical: 1,087 files, 131 directories,
  1,218 rows, TSV SHA-256
  `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`.
- Repository preflight/postflight are byte-identical: 111 files, 21
  directories, 132 rows, TSV SHA-256
  `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`.
- `scripts/__pycache__/launch_wyscout_v5.cpython-312.pyc` remained exact across
  implementation and the complete gate: mode `0644`, link count `1`, size
  `199084`, device `16777231`, inode `91632142`, mtime/ctime `1785700057`, first
  16 bytes `cb0d0d0a00000000cf9e6f6a47c90200`, SHA-256
  `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`.

## Risks

- The direct exact-uv adversarial proofs use isolated launcher copies and
  deliberate pre-verifier source injection. They exercise the actual earliest
  capture and full verifier without claiming an unmocked real-root admission,
  rebuild, or publication.
- PYC magic/header/content SHA-256 remain shell/master operational evidence,
  never Python-role authority or stable digest meaning. The launcher and child
  continue to bind metadata only and deny every Python-role PYC read.
- Fresh independent R9 review and master acceptance remain required before any
  real-root execution.

## Follow-up items

- Fresh independent R9 review and master acceptance; no producer-side follow-up.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed; `/tmp` shell-only evidence was
  created at the master's explicit request, while the admission child and
  disclosed repository launcher PYC remained byte-for-byte unchanged

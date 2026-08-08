# Subagent return

## Task

- task_id: W03-STORAGE-01
- objective: Implement guarded, deterministic local artifact persistence for W03 without introducing a second storage authority.

## Files changed

- `src/scouting/storage/__init__.py`
- `src/scouting/storage/formats.py`
- `src/scouting/storage/guarded.py`
- `tests/unit/test_guarded_storage.py`
- `reports/reviews/W03/returns/W03-STORAGE-01-R1.md`

## Summary

- Added a closed, named-root `GuardedStorage` API. Configuration requires explicit
  absolute and distinct roots; artifact calls reject unknown roots, absolute paths,
  parent traversal, malformed separators, excess depth/length, parent symlinks, target
  symlinks, non-regular targets, and pre-existing files with unsafe modes.
- All traversal and file operations below a root are descriptor-relative and
  no-follow. New directories are mode `0700`; payloads and manifests are mode `0600`.
- Writes use a same-directory temporary file, complete writes plus `fsync`, and an
  atomic hard-link create that cannot replace an existing target. Temporary files are
  removed after both success and failure.
- Content-identical retries are successful no-ops. Different bytes or different
  completion metadata at an existing path fail closed without replacing content.
- Completion manifests are deterministic canonical JSON and are persisted only after
  the durable payload. They record complete state, payload path, SHA-256, byte count,
  media type, lineage, and retention metadata.
- Added canonical JSON and JSONL serialization plus deterministic Parquet encoding and
  readback. JSON rejects unsupported values, non-string keys, NaN, and infinities;
  Parquet fixes column ordering and disables value-dependent dictionary/statistics
  encoding.
- Added 19 tests for configuration boundaries, traversal and symlink escape, target
  modes, manifest ordering/content, partial-write cleanup, hashes, immutable conflicts,
  idempotent retries, canonical formats, and deterministic Parquet readback.

## Tests run

- command: `uv run pytest -q tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `19 passed in 0.47s` on the final required run.
- command: `uv run ruff format --check src/scouting/storage tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `5 files already formatted` on the final required run.
- command: `uv run ruff check src/scouting/storage tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `All checks passed!` on the final required run.
- command: `uv run mypy src/scouting/storage`
  - exit status: `0`
  - result: `Success: no issues found in 4 source files` on the final required run.
- command: `uv run bandit -q -r src/scouting/storage`
  - exit status: `0`
  - result: no findings on the final required run.
- command: `uv run ruff format src/scouting/storage tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: mechanical correction after the first format check reported two unformatted
    files.
- initial verification:
  - `pytest` passed all 19 tests.
  - format check exited `1`, Ruff check exited `1`, and mypy exited `1`; these identified
    formatting and Python 3.12/type-stub annotations, which were corrected before the
    final suite.
  - one parallel Bandit invocation and one chained suite invocation exited `2` because
    the sandbox denied the shared uv cache path. Each required command was then rerun
    successfully through `uv` with the approved cache access.

## Artifacts/evidence

- `src/scouting/storage/guarded.py`
- `src/scouting/storage/formats.py`
- `tests/unit/test_guarded_storage.py`
- `reports/reviews/W03/returns/W03-STORAGE-01-R1.md`

## Risks

- Durability depends on the local filesystem honoring file and directory `fsync` plus
  atomic same-directory hard-link creation; network and object filesystems are outside
  W03's local-only boundary.
- Completion is intentionally two-step: a process failure after durable payload
  creation but before manifest creation leaves an incomplete payload, never a false
  completion marker. An identical retry safely completes the manifest.
- Parquet byte determinism is bounded to the locked PyArrow implementation; a future
  dependency upgrade must reverify hashes before acceptance.

## Follow-up items

- The master should independently inspect all five files and rerun the five packet
  acceptance checks before accepting this task.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml`
  nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed.

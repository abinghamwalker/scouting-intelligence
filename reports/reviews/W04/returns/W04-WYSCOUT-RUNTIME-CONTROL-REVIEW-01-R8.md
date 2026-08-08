# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R8`
- objective: Freshly and independently adjudicate the R8 authenticated
  resident-module roster and metadata-only in-process PYC closure without
  editing producer/PYC bytes or publishing to real roots.

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R8.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R8.md`

## Summary

- Decision: `REWORK`, with `P0/P1/P2 = 0/1/0`.
- Retained R8's exact 23-name/order census, distinct-object check, resident
  importer/registration predicates, exact encoding/`__main__` rows, and all
  frozen R7 tuple/environment/argv/FD/prefix/chronology/product predicates.
- Retained the launcher metadata-only PYC correction. The launcher contains no
  PYC open/read/pread/hash/header/magic access, returns the admission child's
  exact metadata rows, operates under unconditional PYC read denial, and reaches
  its later control marker with classified site/repository PYC fixtures.
- Found `W04-RUNTIME-R8-P1-01`: a distinct replacement object at the already
  registered built-in name `time`, carrying the exact implemented resident
  importer/spec/name/origin/file/cache/package fields, passes the first-user
  verifier. Built-in/frozen `__package__`, spec parent and submodule-location
  shapes are also untested and unchecked; a direct shape substitution likewise
  passes. Exact order and pairwise object uniqueness do not bind the current
  object to the original startup resident object.
- Adjudicated the disclosed launcher PYC as one preserved operational-only
  repository-normal row. It stayed byte-identical and was never rewritten,
  removed, restored, imported or read through Python.

## Tests run

- command: locked/no-sync Ruff format check over admission child, launcher and
  runtime-control tests
  - exit status: `0`
  - result: `3 files already formatted`
- command: locked/no-sync Ruff check with cache disabled
  - exit status: `0`
  - result: `All checks passed!`
- command: locked/no-sync `python -B -m mypy` with review-only cache over the
  same three files
  - exit status: `0`
  - result: `Success: no issues found in 3 source files`
- command: focused locked/no-sync R8 roster/PYC test population
  - exit status: `0`
  - result: `47 passed, 55 deselected in 7.50s`
- command: exact required six-file locked/no-sync `python -B -m pytest -q -p
  no:cacheprovider` population; preserved unified process session `3929`, not
  restarted
  - exit status: `0`
  - result: `257 passed in 1483.18s (0:24:43)`
- command: isolated exact-uv registered-name replacement review case
  - exit status: `0` for the review helper
  - result: replacement passed the pre-guard verifier; execution failed only
    later when `threading` requested absent `time.monotonic`
- command: isolated exact-uv built-in package/parent/location review case
  - exit status: `0` for the review helper
  - result: substitution passed the verifier and reached the deliberately later
    isolated-repository `__init__.py` rejection
- command: locked/no-sync Bandit over admission child and launcher
  - exit status: `0`
  - result: no findings
- command: locked/no-sync `lint-imports --no-cache`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: locked/no-sync `python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks, zero failures, branch `main`, zero configured
    remotes and active pre-push guard
- command: identical complete shell PYC preflight/postflight plus final fixed-
  binding recheck
  - exit status: `0`
  - result: both inventory files byte-identical and all eight bindings exact

All Python-backed review commands used locked/no-sync uv,
`PYTHONDONTWRITEBYTECODE=1`, `python -B`, a review-only
`PYTHONPYCACHEPREFIX`, and disabled or redirected tool caches. The first
sandboxed metadata-shape helper attempt exited `2` on denied read access to the
existing local uv cache before executing the probe; the same offline command
then ran with read-only cache access. No network, sync, dependency operation or
repository change occurred.

The packet names direct `git diff --check` and `git remote`, but governing
subagent authority and the resumed instruction prohibit Git commands. No direct
Git command was run. The required local-only verifier's embedded read-only checks
confirmed main, zero remotes and the guard.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R8.md`:
  SHA-256 `0f4a023fc55c7800f91e9e1f7247059c747d42dd69108e86266ba4e34b7f645c`
- review packet: SHA-256
  `bb7211210edff4cfe4a801f5ceb4e9eb615bba4fa10e3624df98e83f72a013bc`
- producer packet: SHA-256
  `6a16ff130a802dafe924a4a47011bc08b6e1eed3f7c7e6b30ebf4df32f8c00d8`
- admission child: SHA-256
  `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
- launcher: SHA-256
  `e7cf10d5f11871bc48911a5dc9ea8b58ce9a6477e6df0935475f053874b6e2d5`
- runtime tests: SHA-256
  `01007463ac8cb52d67bdfb2b6784f36fab9cdf7a8ddf35c24a9149512d3707e0`
- producer return: SHA-256
  `40a877805b20e4ca9cdd6d8489c3b1074e81de19efbc3c8975abbebf4ef01446`
- R7 independent review: SHA-256
  `d6ef3e0d3930dd212f53cee51ad33802279707f3fc828e52e776822388913ea1`
- complete site PYC inventory: `1,087` files, `131` cache directories,
  SHA-256 `d579cb89cfd3665928eda9e3d6663bcbe64cd74633d6250b163881d01ed9d0c4`
- complete repository PYC inventory: `111` files, `21` cache directories,
  SHA-256 `8101925c6f3b9359c0a27d3e309a42ad6731b4dbae1c6079af1833a075b9729e`
- disclosed launcher PYC: mode `0644`, link count `1`, size `199084`, device
  `16777231`, inode `91632142`, header
  `cb0d0d0a00000000cf9e6f6a47c90200`, SHA-256
  `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`

## Risks

- A real-root outer launch must remain blocked until
  `W04-RUNTIME-R8-P1-01` is corrected, freshly reviewed, and master-accepted.
- Metadata-only Python inventories intentionally cannot prove content/header
  identity when every bound metadata field is equal. Complete shell pre/post
  evidence remains the sole byte authority, and the documented transient
  replace-and-restore residual remains unchanged.
- The exact-uv present-PYC positive fixture deliberately stops after metadata
  census and a later control marker; it does not claim unmocked real-root
  admission/rebuild or publication.

## Follow-up items

- Bounded R9 correction: freeze the exact startup resident object identities at
  the earliest executable point, compare them in the full verifier, close exact
  built-in/frozen package/parent/location shapes, add registered-name and shape
  substitutions, retain metadata-only PYC behavior, then obtain fresh independent
  review and master acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed; only the two R8 review paths were
  written, and temporary review fixtures remained under `/private/tmp`

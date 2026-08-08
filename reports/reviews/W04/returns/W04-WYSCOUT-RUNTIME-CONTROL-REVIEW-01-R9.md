# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R9`
- objective: Freshly and independently adjudicate the R9 earliest startup-object/importer
  binding and complete built-in/frozen shape closure while retaining the R8 exact
  roster, metadata-only PYC behavior and disclosed operational-PYC evidence,
  without producer edits or real-root publication.

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R9.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R9.md`

## Summary

- Decision: **PASS**, with `P0/P1/P2 = 0/0/0`.
- Verified every packet binding before merits and again after the complete gate.
- Independently proved the earliest exact 23 ordered name/object captures, exact
  resident importer captures, and complete 19-row immutable normalized shape
  captures precede the first helper and all later launcher behavior.
- Independently challenged registered built-in/frozen replacements, every
  built-in/frozen package/parent/search-location field, both importer authorities,
  and add/remove/reorder/alias/duplicate cases. Every case rejected before first-
  user continuation.
- Retained the R8 metadata-only PYC collector, exact admission-child complete-row
  equality, unconditional PYC/PYO denial, encoding/transport/product predicates,
  local-only closure, and disclosed launcher-PYC evidence.
- Ran the exact `268`-test final-hash population once, without restart or repeat.
- The optional first custom roster harness used a noncanonical `/var` fixture and
  hit an earlier prefix precondition. Its assertion closed retained session
  `10474` only after the mandatory test/static gate was complete. Master classified
  this as bounded review-harness procedural rework. Sealing session `78303`
  corrected only that harness, performed direct-import audit and final postflight,
  and did not repeat pytest.

## Tests run

- command: locked/no-sync Ruff format check over admission, launcher and runtime tests
  - exit status: `0`
  - result: `3 files already formatted`
- command: locked/no-sync Ruff check with cache disabled
  - exit status: `0`
  - result: `All checks passed!`
- command: locked/no-sync mypy over admission, launcher and runtime tests with a
  review-only cache
  - exit status: `0`
  - result: `Success: no issues found in 3 source files`
- command: focused exact-uv earliest-object/shape, structural-trace, authority,
  encoding and metadata-only PYC population
  - exit status: `0`
  - result: `32 passed in 9.28s`
- command: exact required locked/no-sync six-file `python -B -m pytest -q -p
  no:cacheprovider` population in retained session `10474`, pytest PID `31543`
  - exit status: `0`
  - result: `268 passed in 1505.74s (0:25:05)`
- command: locked/no-sync Bandit over admission and launcher
  - exit status: `0`
  - result: no findings
- command: locked/no-sync import-linter with cache disabled
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: locked/no-sync local-only verifier
  - exit status: `0`
  - result: `PASS`, 25 checks, zero failures, branch `main`, zero remotes
- command: corrected canonical-`/private/tmp` independent exact-uv
  add/remove/reorder/alias/duplicate harness in sealing session `78303`
  - exit status: `0`
  - result: five of five rejected before first-user continuation
- command: isolated direct-import audit under locked/no-sync `python -B`
  - exit status: `0`
  - result: direct branch skipped and zero audited mutations
- command: fresh complete shell PYC pre/post inventories and byte comparisons
  - exit status: `0`
  - result: SITE and REPO `cmp` both zero; `1,218` and `132` rows respectively
- command: final fixed-binding SHA-256 recheck
  - exit status: `0`
  - result: every binding exact

The initial sandboxed focused command exited `2` before collection because it
could not read an already admitted local uv-cache `.git` path. It executed no
test and changed no repository file. The same offline locked/no-sync focused
command passed with read-only cache access.

Direct `git diff --check` and `git remote` were not run because reviewer Git
operations are forbidden. The required local-only verifier performed its
embedded read-only branch/remote/guard checks. The master retains direct Git and
checkpoint authority.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R9.md`
  - SHA-256: `cf4d4df85c4960930fd02d653636358d705dd8b05e8b343e349480197561b02a`
- `/tmp/w04-r9-review-site-pyc-pre.tsv` and
  `/tmp/w04-r9-review-site-pyc-post.tsv`
  - byte-identical; SHA-256:
    `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`
  - `1,218` rows: `1,087` PYC and `131` cache directories
- `/tmp/w04-r9-review-repo-pyc-pre.tsv` and
  `/tmp/w04-r9-review-repo-pyc-post.tsv`
  - byte-identical; SHA-256:
    `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`
  - `132` rows: `111` PYC and `21` cache directories
- exact full-gate retained shell: session `10474`, shell PID `30617`; closed by
  the disclosed optional-harness assertion only after required gates completed
- final sealing shell: session `78303`, shell PID `40432`
- disclosed launcher PYC SHA-256:
  `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`

## Risks

- No review finding. The accepted operational residual is unchanged: a
  hypothetical PYC replacement preserving every Python-observed metadata field
  between shell inventory endpoints remains outside Python authority; complete
  shell header/hash inventories bind both endpoints.
- The retained-shell closure was review-harness procedural rework, fully
  disclosed and bounded after the mandatory gate; it did not alter producer,
  PYC, product, or real-root bytes and pytest was not repeated.

## Follow-up items

- Master acceptance and W04 continuation/checkpoint under sole master Git authority.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed for repository bytes; review-only
  fixtures/caches were confined to `/private/tmp` or `/tmp`

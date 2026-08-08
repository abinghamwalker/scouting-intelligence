# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R10`
- objective: Freshly and independently adjudicate the bounded R10 canonical-JSON
  tuple reconstruction correction without editing producer, PYC, product,
  manifest, staging, data, run, or real-root bytes.

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R10.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R10.md`

## Summary

- Decision: **PASS**, with `P0/P1/P2 = 0/0/0`.
- Verified every R10 packet binding before merits and again after the complete
  gate. Preserved the retained unaccepted code manifest, all `data/**` and
  `runs/**` content, staging prefixes, products, manifests, receipts, sources,
  tests, contracts, and PYC bytes.
- Independently proved that the child boundary requires one exact built-in dict
  with the ordered 25-key roster and exact built-in lists for both declared tuple
  fields. It constructs a new ordered dict, changes only those outer lists to
  tuples, and preserves every nested object plus every other value by identity.
- Reconstructed through the same canonical child transport decoder, validated
  strictly, reproduced the exact five authority and five dependency rows, both
  projection/invocation inverses, the sole build-ID formula, and unchanged
  canonical logical JSON bytes.
- Independently rejected top-level and tuple-field subclasses/types,
  missing/extra/reordered keys, individual tuple substitution, authority and
  dependency add/remove/reorder/value/type mutations, nested extra/mistyped
  rows, top-level drift, invalid build identity, and other strict model failures.
- Traced strict validation and enclosing build equality before
  `_publication_roots` and every product/manifest/receipt writer.
- Ran the exact required `286`-test population and all named static, security,
  import-boundary, and local-only checks in fresh retained session `45530`.

## Tests run

- command: final independent canonical transport/boundary harness under
  locked/no-sync offline `python -B`
  - exit status: `0`
  - result: 41 rejection attacks plus positive transport, identity, inverse,
    build-formula, logical-byte, and source-order proofs passed
- command: locked/no-sync Ruff format check over candidate rebuild child and
  security tests
  - exit status: `0`
  - result: `2 files already formatted`
- command: locked/no-sync Ruff check with cache disabled
  - exit status: `0`
  - result: `All checks passed!`
- command: locked/no-sync `python -B -m mypy` over the candidate rebuild child
  and security tests with a review-only cache
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: exact required locked/no-sync offline six-file `python -B -m pytest
  -q -p no:cacheprovider` population in retained session `45530`, shell PID
  `76704`, pytest uv PID `76731`
  - exit status: `0`
  - result: `286 passed in 1494.82s (0:24:54)`
- command: locked/no-sync Bandit over admission, launcher, and rebuild child
  - exit status: `0`
  - result: no findings
- command: locked/no-sync import-linter with cache disabled
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: locked/no-sync local-only verifier
  - exit status: `0`
  - result: PASS, 25 checks, zero failures, branch `main`, zero remotes
- command: fresh complete shell-only site-PYC, repository-PYC, and retained
  `data/**`/`runs/**` inventories plus byte comparisons
  - exit status: `0`
  - result: all three final pre/post pairs byte-identical
- command: final fixed-binding SHA-256 recheck
  - exit status: `0`
  - result: every binding exact

The first review-local boundary harness omitted a `/tmp` script import path and
exited before importing the producer; its corrected final form passed. The first
full-gate shell incorrectly exported an empty noncanonical `UV_CACHE_DIR` and
ran without the required read-only local-cache access. Retained session `43103`
(shell PID `50667`, pytest uv PID `50706`) completed with exit `1` and
`246 passed, 40 failed in 1443.64s`; every traceback was the absent `/tmp`
archive or sandbox denial of the accepted cache. This was bounded review-harness
procedural rework, not a producer finding. Its fresh postflight inventories were
unchanged. The fresh corrected session removed the override, used offline
read-only access to the admitted cache, and passed completely.

Direct `git diff --check` and `git remote` were not run because reviewer Git
operations are forbidden. The required local-only verifier performed its
embedded read-only branch, remote, and guard checks. Direct Git and checkpoint
evidence remain master-owned.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R10.md`
  - SHA-256: `331082c9482cabae5957e950e0b61683194138e979c6cff07eff06cf51ae80d6`
- `/tmp/w04-r10-review-boundary.py`
  - SHA-256: `d1fdd0e4d85a9f50d0d67b2021ac84a435708d949bc111e9d6d805f5d33ad60d`
- `/tmp/w04-r10-review-gate-rerun.zsh`
  - SHA-256: `ee07ea9a08e25333b95fa101a8b5b9d17be25950e6f335b401b96a919796de5e`
- final selected site-packages PYC inventories:
  `/tmp/w04-r10-review-final-site-pre.tsv` and
  `/tmp/w04-r10-review-final-site-post.tsv`
  - `1,218` rows: `1,087` PYC files plus `131` cache directories
  - byte-identical SHA-256:
    `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`
- final repository PYC inventories:
  `/tmp/w04-r10-review-final-repo-pre.tsv` and
  `/tmp/w04-r10-review-final-repo-post.tsv`
  - `132` rows: `111` PYC files plus `21` cache directories
  - byte-identical SHA-256:
    `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`
- final complete retained-root inventories:
  `/tmp/w04-r10-review-final-retained-pre.tsv` and
  `/tmp/w04-r10-review-final-retained-post.tsv`
  - `81` rows; byte-identical SHA-256:
    `e62878d96c76cc67a0fc0690fed674c1c61c2b82981a472b21649ffd981a686b`
- retained authoritative gate: session `45530`, shell PID `76704`, pytest uv
  PID `76731`
- disclosed launcher PYC SHA-256:
  `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`

## Risks

- No review finding. The future accepted code manifest and build ID will change
  mechanically when derived from the corrected source byte; no logical value or
  digest meaning/formula changes.
- The accepted R9 PYC residual is unchanged: a hypothetical replace-and-restore
  event preserving all Python-observed metadata between shell endpoints remains
  outside Python authority; complete shell inventories bind both endpoints.
- The disclosed first gate failure was reviewer-harness procedural rework and
  left producer, PYC, product, manifest, staging, data, run, and real-root bytes
  unchanged.

## Follow-up items

- Master acceptance and master-owned continuation of the real-root invocation
  packet; no producer-side follow-up.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed for repository bytes; review-only
  harnesses, caches, and inventories were confined to `/private/tmp` or `/tmp`

# Subagent return

## Task

- task_id: `W04-SOURCE-MANIFEST-BRIDGE-REVIEW-01-R1`
- objective: Independently review the frozen Wyscout source-manifest bridge and
  reproduce its focused executable evidence against the real local source.

## Files changed

- `reports/reviews/W04/wyscout-source-manifest-bridge-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-MANIFEST-BRIDGE-REVIEW-01-R1.md`

## Summary

- Independently read every packet-listed authority and every producer-owned byte.
- Reproduced all four fixed physical SHA-256 bindings, the 4,199-byte manifest,
  mode `0600`, link count one, exact manifest/trace UUIDv5 identities, strict
  canonical readback, restricted rights, two fixed clocks, 18 ordered files, and
  six exact complete coverage dimensions.
- Recomputed physical size and SHA-256 for all 18 real source paths and parsed row
  counts independently with `jq`/CSV checks; every R20 row matched exactly.
- Reproduced all focused format, lint, type, test, CLI, mutation, path, symlink,
  conflict, tenant, temporal, rights, coverage, no-network, and no-product evidence.
- Repeated materialization confirmation and proved the immutable artifact retained
  the same inode, size, mode, link count, timestamp, digest, and bytes.
- Findings are `P0=0`, `P1=0`, `P2=0`; recommendation is `PASS` without
  self-acceptance or downstream product authority.

## Tests run

- command: `shasum -a 256` and `wc -c` over the exact 18 R20 source paths
  - exit status: `0`
  - result: every fixed size and SHA-256 matched; total physical bytes measured
    `991136406`.
- command: `jq 'length'` over the 13 admitted JSON arrays plus independent CSV
  header/data-row checks
  - exit status: `0`
  - result: exact row counts reproduced: `7`, `142`, `3603`, five match counts
    `380/380/306/380/380`, five event counts
    `643150/632807/519407/647372/628659`, and CSV `36/59`.
- command: `uv run ruff format --check src/scouting/sources/wyscout_manifest.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/sources/wyscout_manifest.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `uv run mypy src/scouting/sources/wyscout_manifest.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`.
- command: `uv run pytest -q tests/unit/test_wyscout_source_manifest.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `139 passed in 67.99s`.
- command: `uv run python -m scouting.sources.wyscout_manifest --source-root data/source/wyscout/v5 --manifest-root data/manifests --tenant-id 65a43912-d412-5ff9-a364-7f84d1ad6c5d`
  - exit status: `0` on each of two independent confirmations
  - result: exact path confirmed with SHA-256
    `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
    and size `4199`; artifact metadata and bytes were unchanged.
- command: `uv run python -B -c '<independent SourceSnapshotManifest, canonical-byte, UUIDv5, rights, coverage, mode and link assertions>'`
  - exit status: `0`
  - result: exact IDs/digest, `files=18`, `dimensions=6`, `canonical=true`,
    `mode=0600`, and `nlink=1` reproduced.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-source-manifest-bridge-independent-review-R1.md`
  - recommendation: `PASS`
  - findings: `P0=0`, `P1=0`, `P2=0`
- source manifest ID: `4e16bdb5-afe7-5601-88ad-adc124cfce3b`
- trace ID: `2c441714-d968-5495-8339-c85ecaf5f596`
- source manifest physical SHA-256:
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`

## Risks

- No P0-P2 defect remains within this packet.
- The accepted surface is source-manifest evidence only; identity and every data
  product remain separately gated.

## Follow-up items

- Master readback, independent reproduction, and accept/rework decision; none
  otherwise.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no sync, install,
  dependency, or lock change was performed.
- no edits outside `allowed_paths`: confirmed; exactly the two review-owned paths
  listed above were created.

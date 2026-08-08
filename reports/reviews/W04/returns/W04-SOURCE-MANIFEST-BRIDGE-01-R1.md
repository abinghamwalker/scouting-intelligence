# Subagent return

## Task

- task_id: `W04-SOURCE-MANIFEST-BRIDGE-01-R1`
- objective: Implement and execute the sole strict bridge from the frozen Wyscout completion evidence to one immutable `SourceSnapshotManifest` for the explicit local POC tenant.

## Files changed

- `src/scouting/sources/wyscout_manifest.py`
- `tests/unit/test_wyscout_source_manifest.py`
- `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json`
- `reports/reviews/W04/returns/W04-SOURCE-MANIFEST-BRIDGE-01-R1.md`

## Summary

- Added one closed Wyscout completion-to-contract bridge with an exact, ordered 18-row R20 source-evidence roster. It performs descriptor-contained, no-follow regular-file reads; validates every physical size and SHA-256; and measures every declared JSON-array or CSV row count without archive-member discovery or ZIP extraction.
- Added strict completion-manifest canonical-byte, key, identity, source-clock, rights, collection, seven-object, ten-member, and four directory-only exclusion validation. No completion value is derived from current time, filesystem time, provider payload dispatch, discovery, or a network call.
- Reproduced the exact R20 UUIDv5 derivation, including the repository canonical JSON terminal LF, yielding manifest ID `4e16bdb5-afe7-5601-88ad-adc124cfce3b` and trace ID `2c441714-d968-5495-8339-c85ecaf5f596` for tenant `65a43912-d412-5ff9-a364-7f84d1ad6c5d` and `club_id=null`.
- Populated the existing strict `SourceSnapshotManifest` with provider schema `figshare-v5+completion-v1+bridge-v1`, exact acquisition/source clocks, restricted use, derived/internal review allowed, export false, required exact attribution, exact ordered files, and exact six-dimension 1.0 source coverage.
- Added a sole canonical materializer for the exact content-addressed path. It writes atomically without a companion sidecar, confirms equal existing bytes idempotently, rejects unequal existing bytes, and reopens/readbacks the contract bytes.
- Added 32 focused positive and negative tests covering the real frozen source, fixed identities, file roster/counts, canonical round-trip, temporal and rights mutation, root/path/symlink denial, measurement drift, missing/extra/reordered evidence, coverage, UUID sensitivity, immutable idempotency/conflict, and absence of product/network authority.
- Created no Bronze, Silver, Gold, identity runtime, receipt, rebuild, model, network, remote, cloud, container, CI, endpoint, or deployment path.

## Tests run

- command: `uv run ruff format --check src/scouting/sources/wyscout_manifest.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check src/scouting/sources/wyscout_manifest.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/sources/wyscout_manifest.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- command: `uv run pytest -q tests/unit/test_wyscout_source_manifest.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `139 passed in 64.49s` (`32` bridge tests plus `107` frozen R21 cross-authority tests)
- command: `uv run python -m scouting.sources.wyscout_manifest --source-root data/source/wyscout/v5 --manifest-root data/manifests --tenant-id 65a43912-d412-5ff9-a364-7f84d1ad6c5d`
  - exit status: `0`
  - result: created the exact manifest; SHA-256 `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`; `4,199` bytes
- command: identical materialization command repeated without changing any input
  - exit status: `0`
  - result: confirmed the existing exact bytes; identical SHA-256 and size; no conflict and no second artifact
- command: `uv run --locked --no-sync python -c '<strict SourceSnapshotManifest readback and canonical-byte assertions>'`
  - exit status: `0`
  - result: `manifest_id=4e16bdb5-afe7-5601-88ad-adc124cfce3b trace_id=2c441714-d968-5495-8339-c85ecaf5f596 files=18 dimensions=6 canonical=true`

## Artifacts/evidence

- bridge SHA-256: `ef16a489a13dffab7cf2b609f81d2a229a012ec5b92ba4debee0f628b35e721c`
- focused-test SHA-256: `c7c71cf5abc9b996b7c93ed9b7005b1469f5614ba9d2653a74dc135310e038d1`
- source manifest path: `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json`
- source manifest SHA-256: `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
- source manifest physical evidence: mode `0600`, size `4,199`, link count `1`
- source manifest contract evidence: manifest ID `4e16bdb5-afe7-5601-88ad-adc124cfce3b`; trace ID `2c441714-d968-5495-8339-c85ecaf5f596`; `18` ordered file rows; `6` ordered complete coverage dimensions; canonical readback true

## Risks

- Row counting for the physically pinned JSON arrays is a bounded streaming structural count. Full payload meaning remains outside this bridge; the exact size and SHA-256 checks make any byte mutation fail before its measured count can be accepted.
- The source manifest is the strict source-evidence prerequisite only. It grants no identity resolution or product-layer authority.

## Follow-up items

- Independent R1 review and master reproduction of the packet checks and artifact readback.

## Scope confirmation

- no Git operations: confirmed; no Git command or `.git` mutation was performed
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor `uv.lock` was changed
- no edits outside `allowed_paths`: confirmed; only the four exact packet-owned paths listed above were created or edited

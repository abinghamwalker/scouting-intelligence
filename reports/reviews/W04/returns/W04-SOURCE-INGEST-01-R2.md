# Subagent return

## Task

- task_id: W04-SOURCE-INGEST-01-R2
- objective: Close the R1 real-endpoint redirect defect and freeze every reviewed authority-bearing W04 source value without weakening existing acquisition controls.

## Files changed

- src/scouting/sources/wyscout.py
- src/scouting/sources/__init__.py
- tests/unit/test_wyscout_source.py
- reports/reviews/W04/returns/W04-SOURCE-INGEST-01-R2.md

## Summary

- Added a strict `WyscoutRedirectAuthority` parsed from the exact reviewed `redirect_authority` declaration. The loader rejects missing, extra, mistyped, reordered, or changed authority values, and the downloader also rejects runtime dataclass reconstruction that broadens the frozen redirect authority.
- Replaced unconditional redirect denial with a production transport handler that allows exactly one HTTP 302 from the exact reviewed `ndownloader.figshare.com/files/{file_id}` source URL.
- The only accepted delivery target is exact lowercase HTTPS origin `s3-eu-west-1.amazonaws.com`, exact `/pfigshare-u-files/{file_id}/{name}` path, and exactly the six declared AWS v4 query keys.
- The amended `credential_separator_encoding: literal_slash` value is strictly loaded and frozen. The observed raw `/` credential separators are accepted; percent-encoded, mixed, double-encoded, backslash, empty-segment, and extra-segment representations are denied.
- Credential access keys are bounded to 16–128 uppercase ASCII letters or digits. Tests exercise both accepted boundaries and reject short, long, lowercase, and punctuation-bearing aliases.
- The signed target is validated before any response-body read: canonical algorithm, same-date credential scope, `eu-west-1/s3/aws4_request`, host-only signed headers, canonical 1–60 second expiry, canonical UTC signature date, lowercase 64-hex signature, key-specific canonical query encoding, and no userinfo, port, fragment, host/path/file/query aliases, or second hop.
- Signed delivery URLs remain transient. They are neither placed in completion evidence nor printed by the CLI; the stable reviewed Figshare source URL remains the recorded object URL.
- Retained injected opener compatibility for fully synthetic tests and direct synthetic responses. The production CLI uses the strict one-hop handler.
- Expanded configuration freezing across identity, purpose, allowed/forbidden claims, rights, evidence URLs, attribution/change notice, coverage, exact object order/identity, archive policy, temporal semantics, acquisition flags/roots/verification order, and redirect authority.
- Added representative mutation tests for every authority group, an exact observed literal-slash signed-hop test, handler status/second-hop tests, runtime-authority expansion evidence, access-key boundary tests, and adversarial tests for every material signed-target and credential-separator mutation. All invalid final URLs are rejected before the synthetic response body is read.
- All R1 archive, manifest-last, exact replay, digest, retry, import-safety, and no-network tests remain green.

## Tests run

- command: `uv run pytest -q tests/unit/test_wyscout_source.py`
  - exit status: 0
  - result: 81 passed in 0.71s
- command: `uv run ruff format --check src/scouting/sources/wyscout.py src/scouting/sources/__init__.py scripts/acquire_wyscout_v5.py tests/unit/test_wyscout_source.py`
  - exit status: 0
  - result: 4 files already formatted
- command: `uv run ruff check src/scouting/sources/wyscout.py src/scouting/sources/__init__.py scripts/acquire_wyscout_v5.py tests/unit/test_wyscout_source.py`
  - exit status: 0
  - result: all checks passed
- command: `uv run mypy src/scouting/sources/wyscout.py scripts/acquire_wyscout_v5.py`
  - exit status: 0
  - result: success, no issues found in 2 source files
- command: `uv run bandit -q src/scouting/sources/wyscout.py scripts/acquire_wyscout_v5.py`
  - exit status: 2 in the workspace sandbox, then 0 with approved cache access
  - result: the sandboxed attempt could not read `/Users/adrian/.cache/uv/sdists-v9/.git`; the approved rerun completed with no findings

## Artifacts/evidence

- reports/reviews/W04/returns/W04-SOURCE-INGEST-01-R2.md
- tests/unit/test_wyscout_source.py

## Risks

- This subagent did not access the provider or any real payload. The master must reproduce the real one-hop acquisition against the reviewed endpoint and verify completion evidence.
- The injected opener remains a trusted synthetic-test seam and does not expose redirect history. Real acquisition through the CLI uses the strict stateful handler that enforces the one-hop limit.
- The downstream `SourceSnapshotManifest` temporal-validator integration precondition disclosed in R1 remains outside this packet: frozen source availability legitimately predates actual acquisition.

## Follow-up items

- Master: independently run the packet checks and the bounded real acquisition, confirming the live redirect is accepted and no transient signed URL appears in durable or console evidence.
- Master: resolve the previously disclosed downstream `SourceSnapshotManifest` temporal-validator integration precondition.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no provider/network/data/config/orchestration access beyond read-only required inputs: confirmed; no provider request or payload access occurred
- no delegation or self-approval: confirmed

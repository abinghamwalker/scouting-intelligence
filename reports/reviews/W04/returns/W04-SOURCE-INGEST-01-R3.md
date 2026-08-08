# Subagent return

## Task

- task_id: W04-SOURCE-INGEST-01-R3
- objective: Close the oversized signed-expiry domain-error defect without changing the accepted R2 redirect authority or any other acquisition boundary.

## Files changed

- src/scouting/sources/wyscout.py
- tests/unit/test_wyscout_source.py
- reports/reviews/W04/returns/W04-SOURCE-INGEST-01-R3.md

## Summary

- Added a lexical digit-length bound for `X-Amz-Expires` before integer conversion. The bound is derived from the frozen 60-second authority, so provider-controlled decimal text longer than two digits cannot reach `int()`.
- Retained the existing strict ASCII-decimal, canonical representation, and numeric `1..60` checks. No redirect authority, query representation, transport, archive, completion, replay, storage, or local-only behavior changed.
- Added a producer regression using a fabricated 5,000-digit expiry. It proves the adapter raises `WyscoutDownloadError` before body read, closes the response, and leaves the temporary working directory empty.
- Retained all R1/R2 producer evidence unchanged and green.

## Tests run

- command: `uv run pytest -q tests/unit/test_wyscout_source.py tests/security/test_w04_wyscout_ingest_review.py::test_malformed_numeric_expiry_is_domain_error_before_body_read`
  - exit status: 0
  - result: 91 passed in 0.91s
- command: `uv run ruff format --check src/scouting/sources/wyscout.py tests/unit/test_wyscout_source.py`
  - exit status: 0
  - result: 2 files already formatted
- command: `uv run ruff check src/scouting/sources/wyscout.py tests/unit/test_wyscout_source.py`
  - exit status: 0
  - result: all checks passed
- command: `uv run mypy src/scouting/sources/wyscout.py`
  - exit status: 0
  - result: success, no issues found in 1 source file
- command: `uv run bandit -q src/scouting/sources/wyscout.py`
  - exit status: 2 in the workspace sandbox, then 0 with approved cache access
  - result: the sandboxed attempt could not read `/Users/adrian/.cache/uv/sdists-v9/.git`; the approved rerun completed with no findings

## Artifacts/evidence

- reports/reviews/W04/returns/W04-SOURCE-INGEST-01-R3.md
- tests/unit/test_wyscout_source.py
- retained independent regression: `tests/security/test_w04_wyscout_ingest_review.py::test_malformed_numeric_expiry_is_domain_error_before_body_read`

## Risks

- No provider endpoint or real payload was accessed. The master retains independent review, real-acquisition, integration, and phase-gate authority.
- No residual risk specific to `W04-INGEST-EXPIRY-DOMAIN-01` is known after the producer and retained independent regression passed.

## Follow-up items

- Master: reproduce the packet evidence and redispatch the complete independent ingest review matrix.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no reviewer-test, configuration, orchestration, script, storage, data, or container edits: confirmed; required inputs were read only
- no provider, network, or real-payload access: confirmed
- no delegation or self-approval: confirmed

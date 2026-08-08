# Subagent return

## Task

- task_id: `W04-SOURCE-INGEST-REVIEW-01-R2`
- objective: Independently review the corrected W04 R2 Wyscout acquisition seam and
  complete the redirect, archive, completion, replay, temporal, rights, and local-only
  challenge matrix unless a packet stop condition reproduces.

## Files changed

- `tests/security/test_w04_wyscout_ingest_review.py`
- `reports/reviews/W04/wyscout-ingest-review-R2.md`
- `reports/reviews/W04/returns/W04-SOURCE-INGEST-REVIEW-01-R2.md`

## Summary

- Adapted all R1 reviewer regressions to the canonical R2 configuration.
- Proved canonical redirect authority and frozen identity/rights evidence now load and
  reject the retained mutations correctly.
- Proved a fabricated exact signed destination with observed literal `/` credential
  separators executes and reads its body only after validation.
- Independently rejected percent-encoded, mixed, double-encoded, backslash, empty,
  extra-segment, short, long, and lowercase credential variants before body read, with
  response closure and temporary cleanup.
- Independently proved non-302 statuses, wrong origin, and a second hop reject.
- Challenged nine malformed numeric expiry representations.
- Reproduced one P2 defect: a 5,000-digit ASCII decimal escapes as raw `ValueError`
  instead of `WyscoutDownloadError`. The body remains unread, response closes, and
  temporary bytes are removed.
- Stopped the remaining independent matrix when the packet's P2 stop condition fired.
- Recommendation: **REWORK**. This is not self-approval.

## Tests run

- command:
  `uv run pytest -q tests/unit/test_wyscout_source.py tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `1`
  - result: `1 failed, 102 passed in 0.88s`; retained P2 evidence
- command:
  `uv run ruff format --check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command:
  `uv run ruff check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: validator status `PASS`; failures `[]`

## Artifacts/evidence

- `tests/security/test_w04_wyscout_ingest_review.py`
  - `test_canonical_redirect_authority_is_loaded_as_runtime_authority`
  - `test_fabricated_reviewed_one_hop_redirect_is_accepted`
  - `test_reviewed_identity_and_rights_cannot_change_while_loading`
  - `test_credential_aliases_reject_before_body_read`
  - `test_redirect_status_origin_and_second_hop_are_exact`
  - `test_malformed_numeric_expiry_is_domain_error_before_body_read`
- `reports/reviews/W04/wyscout-ingest-review-R2.md`
- Combined result: `1 failed, 102 passed in 0.88s`
- Local-only validator: `PASS`

## Risks

- The malformed expiry is rejected before content read but escapes the documented
  source-domain exception boundary.
- The independent archive/completion/replay/temporal/rights matrix remains incomplete
  because the mandatory P2 stop condition fired.
- No real endpoint, provider payload, archive, protected fixture, data root, or
  container was accessed.

## Follow-up items

- Producer to bound expiry text before `int(...)` or translate conversion failure to
  `WyscoutDownloadError`, retaining zero reads and cleanup.
- Producer to add an oversized-decimal regression.
- Master to dispatch the complete independent ingest review again after correction.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no producer, configuration, policy, dependency, orchestration, script, storage,
  container, data, run-artifact, or protected-fixture edits: confirmed.
- no provider, network, real payload, archive, external service, credential, public
  bind, cloud, or deployment access: confirmed.
- no delegation: confirmed.
- no self-approval: confirmed; **REWORK** is an independent recommendation.

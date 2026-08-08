# Subagent return

## Task

- task_id: `W04-SOURCE-INGEST-REVIEW-01`
- objective: Independently challenge the Wyscout v5 acquisition and raw-admission
  implementation against the frozen W04 authority and return an ACCEPT-or-REWORK
  recommendation.

## Files changed

- `tests/security/test_w04_wyscout_ingest_review.py`
- `reports/reviews/W04/wyscout-ingest-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-INGEST-REVIEW-01-R1.md`

## Summary

- Added independent stop-condition regressions with a global real-network denial and
  only fabricated in-memory transport/payload evidence.
- Reproduced a P1 integration defect: the producer loader rejects the canonical
  `acquisition.redirect_authority`, so the reviewed source cannot load or acquire.
- Retained a conforming fabricated one-hop signed redirect test for the required
  producer correction.
- Reproduced a second P1 defect: eight exact reviewed identity/rights fields can change
  while the pre-redirect parser still loads.
- Stopped the remaining challenge matrix when the packet's P1 stop condition fired.
- Recommendation to master: **REWORK**. This recommendation is not self-approval.
- Froze the executable R1 evidence before separate producer R2 edits began; later
  producer state was not assessed as part of this decision.

## Tests run

- command: `uv run pytest -q tests/unit/test_wyscout_source.py tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 1
  - result: `4 failed, 4 passed, 21 errors in 0.73s`; retained P1 evidence
- command: `uv run ruff format --check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 0
  - result: `1 file already formatted`
- command: `uv run ruff check tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 0
  - result: `All checks passed!`
- command: `uv run mypy tests/security/test_w04_wyscout_ingest_review.py`
  - exit status: 0
  - result: `Success: no issues found in 1 source file`

## Artifacts/evidence

- `tests/security/test_w04_wyscout_ingest_review.py`
- `reports/reviews/W04/wyscout-ingest-review-R1.md`
- master-supplied read-only endpoint preflight: exact Figshare URL returns HTTP 302 to
  short-lived signed `s3-eu-west-1.amazonaws.com/pfigshare-u-files/...`

## Risks

- The R1 source seam was non-executable because authority and producer schemas
  disagreed.
- The R1 default transport rejected the redirect required by the authorised
  endpoint.
- Reviewed rights and attribution evidence can be changed before loading and can flow
  into completion evidence.
- The full archive/replay review matrix remains uncompleted because the mandatory P1
  stop condition fired.

## Follow-up items

- Producer to implement and freeze the exact one-hop redirect authority, with
  destination validation before opening.
- Producer to freeze every reviewed identity and rights-evidence field and add complete
  mutation coverage.
- Master to dispatch an independent R2 ingest review after the producer suite passes
  against the canonical authority.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

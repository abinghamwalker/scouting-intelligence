# Subagent return

## Task

- task_id: W03-VERTICAL-01
- objective: Correct only the four vertical-boundary defects recorded in
  `REVIEW-W03-VERTICAL-01-R1`.

## Files changed

- src/scouting/serving/synthetic.py
- src/scouting/workflow/service.py
- src/scouting/web/app.py
- services/api/main.py
- tests/e2e/test_w03_vertical_journey.py
- tests/security/test_application_authorization.py
- reports/reviews/W03/returns/W03-VERTICAL-01-R2.md

## Summary

- `SyntheticDomainSnapshot.from_path` now requires a relative named domain and an
  explicit allowed fixture root. It rejects absolute paths, traversal, non-domain
  names, missing roots/files, directories, outside-root resolution, and escaped
  symlinks before content is read.
- Development remains the default partition. A master caller can explicitly select
  `protected_test`; the envelope partition must match the selection. API composition
  uses `SCOUTING_SYNTHETIC_FIXTURE_ROOT`, optional
  `SCOUTING_SYNTHETIC_DOMAIN_NAME=domain.json`, and optional
  `SCOUTING_SYNTHETIC_PARTITION=development`.
- Protected-input behavior is tested only with a temporary synthetic envelope created
  beneath pytest's temporary root. No protected fixture file or protected expected
  output was accessed.
- Fixed read/export endpoints authenticate a principal, retain an append-only denial
  attempt through the central app-role/transaction-local tenant boundary, and then
  return only `{"detail":"action denied"}`. The audit row attributes actor, tenant,
  request, target and action but has no before/after evidence digest. Export carries
  only the contract-required non-sensitive `denied_attempt` scope marker.
- Added real-boundary regressions for unknown API sessions, cross-tenant API input,
  content-free confidential read/export denial audits, exact observed/available
  cutoff exclusion, explicit model/index unavailable states with no result fallback,
  guarded domain reads, explicit temporary protected selection, and the real worker
  entrypoint proving `scouting_app`, transaction-local tenant context, and
  `listener_started=false`.
- Runtime serving/workflow/web/API modules contain no assertion-output filename or
  read path.

## Tests run

- command: `SCOUTING_DATABASE_URL='<redacted master-supplied loopback URL>' uv run pytest -q tests/e2e/test_w03_vertical_journey.py tests/integration/test_w03_local_telemetry.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: 22 passed; one upstream Starlette/httpx deprecation warning.
- command: `uv run ruff format --check src/scouting/serving src/scouting/workflow src/scouting/web services/api tests/e2e/test_w03_vertical_journey.py tests/integration/test_w03_local_telemetry.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: 11 files already formatted.
- command: `uv run ruff check src/scouting/serving src/scouting/workflow src/scouting/web services/api tests/e2e/test_w03_vertical_journey.py tests/integration/test_w03_local_telemetry.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/serving src/scouting/workflow src/scouting/web services/api`
  - exit status: 0
  - result: no issues found in 8 source files.
- command: `uv run bandit -q -r src/scouting/serving src/scouting/workflow src/scouting/web services/api`
  - exit status: 0
  - result: no findings.
- command: `! rg -n "expected_retrieval\\.json" src/scouting/serving src/scouting/workflow src/scouting/web services/api`
  - exit status: 0
  - result: no runtime reference found.
- correction evidence: the first bounded pytest attempt exited 2 during collection
  because `services/` is not an installed top-level package. The focused worker test
  was corrected to execute the real `services/worker/main.py` entrypoint with
  `runpy.run_path`; it does not change worker code or packaging.

## Artifacts/evidence

- reports/reviews/W03/returns/W03-VERTICAL-01-R2.md
- tests/e2e/test_w03_vertical_journey.py
- tests/security/test_application_authorization.py
- guarded input selections: `development`, `protected_test`
- denial audit target type: `confidential_evidence.denied_attempt`
- database application identity asserted by journey, denial-attempt, readiness, and
  worker tests: `scouting_app`
- temporary protected fixture ID: `w03-temporary-protected-envelope`

## Risks

- No protected fixture or protected expected output was accessed. The master still
  owns the brokered protected run and its gate decision.
- Root/candidate resolution rejects escaped symlinks before I/O, but the threat model's
  residual filesystem race risk remains; W03 does not claim protection against all
  filesystem race conditions.
- Evidence remains synthetic seam evidence only and makes no security, model-quality,
  expert-relevance, pilot, or recruitment-outcome claim.
- TestClient continues to emit the existing upstream Starlette/httpx deprecation
  warning. Changing dependencies is outside this packet.

## Follow-up items

- Master independently review the R2 changes, rerun all checks, and broker any
  protected-input gate without exposing protected expected output to the implementer.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.

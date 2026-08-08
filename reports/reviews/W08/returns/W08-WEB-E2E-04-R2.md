# W08-WEB-E2E-04-R2 return

## Objective

Correct the existing local W08 HTTP seam so submitted CSRF is required, status-only
brief transitions preserve historical content, and the study launcher is loopback-only
and fresh-root fail-closed.

## Changed files

- `src/scouting/web/w08.py`
- `scripts/run_w08_study.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `reports/reviews/W08/returns/W08-WEB-E2E-04-R2.md`

## Route/domain and policy map

- `POST /w08/login` → `LocalSessionService.login`; opaque local session/CSRF pair.
- `POST /w08/logout` → `LocalSessionService.revoke`; supplied hidden CSRF is required.
- `POST /w08/briefs` and status routes → `R1WorkflowService`; supplied hidden CSRF
  is required and service audit/authorisation remains authoritative.
- `GET /w08/briefs/{id}` → tenant-scoped SQL followed by `R1AuthorizationPolicy`
  resource filtering; scout access additionally requires approved status.
- `GET /w08/export/{id}` → `LocalEvidenceExporter.read`; denial is generic.
- `GET /w08/audit` → admin policy boundary; no audit mutation route exists.

The version builder now retains prior responsibilities, constraints, preferences,
exemplars and submitted timestamp for status-only revisions. Study preparation refuses
an existing non-empty root, uses random ephemeral credentials, and calls Uvicorn only
with `host="127.0.0.1"` and a bounded unprivileged `--port`.

## Checks

```text
uv run ruff format --check src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# exit 0
uv run ruff check ...same files...
# exit 0
uv run mypy src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py
# exit 0, Success: no issues found in 3 source files
uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# exit 0, 4 passed; one existing Starlette TestClient deprecation warning
```

Test count: 2 authorised/basic journey witnesses; 2 denied/CSRF/security witnesses.

## Truthful residuals

**REWORK REQUIRED — do not accept this packet.** The specified HTTP composition still
lacks the full service-backed shortlist, scout-observation, export-create/revoke,
optimistic-concurrency/recovery routes and their dense TestClient coverage. It also
lacks browser/Playwright evidence, which R2 explicitly excludes. The remaining work
does not appear to require a shared service or contract change, but it was not completed
in this bounded return. No automated fixture or UI action is representative-user
evidence; W06 remains NO_GO/resemblance_only/synthetic_development_only/LIMITED.

No Git operations, dependency/lock changes, protected-output access, external service,
network call, or edits outside the allowed paths were made.

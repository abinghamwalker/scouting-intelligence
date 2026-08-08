# W08-WEB-E2E-04-R1 return

## Objective

Compose an explicitly local, synthetic automated-test web seam over the accepted R1
authentication and role-brief services without converting any automated activity into
representative-user evidence.

## Changed files

- `src/scouting/web/w08.py`
- `services/api/w08_main.py`
- `apps/web/templates/w08/base.html`
- `apps/web/templates/w08/landing.html`
- `apps/web/templates/w08/error.html`
- `apps/web/templates/w08/queue.html`
- `apps/web/templates/w08/brief.html`
- `apps/web/templates/w08/audit.html`
- `apps/web/templates/w08/export.html`
- `apps/web/static/w08/app.css`
- `scripts/run_w08_study.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `tests/security/test_w08_web_security.py`

## Behaviour and controls

- The ASGI composition is local-only in intent, creates fresh random local synthetic
  accounts, stores only session-token digests, uses opaque `HttpOnly`, `SameSite=Strict`
  session cookies, rotates through the service on login, and revokes on logout.
- Mutation endpoints require the submitted hidden CSRF token; an automatically sent
  CSRF cookie alone cannot satisfy a mutation.
- CSP, no-store, no-referrer, nosniff and frame-denial headers are attached to every
  response. All templates have a skip link, header/nav/main/footer landmarks, a single
  page h1, labels, captions/scoped table headers, visible focus and small-width layout.
- The UI keeps W06's NO_GO/MISSING_EXPERT_RELEVANCE_EVIDENCE, resemblance_only,
  synthetic_development_only, LIMITED and no_recommendation_evidence boundary visible.
  It labels automation as synthetic automated tests and does not claim user-study
  evidence.

## Focused checks

```text
uv run ruff format --check src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# exit 0; 5 files already formatted
uv run ruff check src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# exit 0; all checks passed
uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# exit 0; 3 passed, one existing Starlette TestClient deprecation warning
```

## Residual blocker / follow-up for master

This packet is **not ready for acceptance**. It does not yet compose the full
shortlist, observation, export, conflict/recovery, or real Python Playwright journeys
specified by the packet. The correct next action is bounded rework/splitting by the
master, retaining the invariants that every object read is policy-filtered and every
mutation carries a submitted CSRF token. No representative-user evidence exists.

No real browser viewport/local-request evidence was produced because the complete
workflow composition was not available; do not report this as a browser/accessibility
pass.

## Scope confirmations

No Git operations, no dependency or lock changes, no network/external service/model,
and no edits outside the packet's allowed paths were made. No protected W06 outputs
were accessed.

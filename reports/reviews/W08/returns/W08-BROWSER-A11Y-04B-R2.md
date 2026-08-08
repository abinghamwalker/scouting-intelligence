# W08-BROWSER-A11Y-04B-R2 return

## Task

- task ID: `W08-BROWSER-A11Y-04B`, revision `R2`
- objective: fresh reproduction of the loopback-only W08 real-browser and accessibility
  witnesses after R1's process-only rejection.
- invariant: every exercised persona/record is a synthetic automated test, never
  representative-user evidence; browser requests resolve only to `127.0.0.1`.

## Direct inspection and R1 disposition

I directly inspected the R1 packet and return, the W08 moderated-study protocol, the
W07 browser/accessibility evidence, W08 route composition, all W08 templates and CSS,
the W08 Playwright witness, and the W08 integration/security witnesses. I adopted the
R1 presentation/test implementation unchanged: the R1 CSS changes are bounded to
box-sizing, visible focus for `select`/`textarea`, wrapping, and mobile-safe control
widths; no correction was warranted by a fresh reproduction.

Directly inspected implementation/test paths:

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/base.html`
- `apps/web/templates/w08/landing.html`
- `apps/web/templates/w08/queue.html`
- `apps/web/templates/w08/brief.html`
- `apps/web/templates/w08/shortlist.html`
- `apps/web/templates/w08/entry.html`
- `apps/web/templates/w08/audit.html`
- `apps/web/templates/w08/export.html`
- `apps/web/templates/w08/exports.html`
- `apps/web/templates/w08/error.html`
- `apps/web/static/w08/app.css`
- `tests/e2e/test_w08_local_workflow_playwright.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `tests/security/test_w08_web_security.py`

Changed paths: this return only.

## Fresh R2 checks

All commands ran from the repository root and exited `0`:

```text
uv run ruff format --check src/scouting/web/w08.py tests/e2e/test_w08_local_workflow_playwright.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# 4 files already formatted

uv run ruff check src/scouting/web/w08.py tests/e2e/test_w08_local_workflow_playwright.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# All checks passed

uv run mypy src/scouting/web/w08.py
# Success: no issues found in 1 source file

uv run pytest -q tests/e2e/test_w08_local_workflow_playwright.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# 13 passed, 1 Starlette TestClient third-party deprecation warning, 22.45s
```

## Browser, accessibility and evidence-honesty witnesses

- Real headless Chromium starts a fresh uvicorn application on an ephemeral
  `http://127.0.0.1:<port>` listener. The complete synthetic analyst, approver, scout
  and admin journey passed: draft/create/submit/approve, replay link, shortlist and
  longlist, scout assignment, disagreement plus amendment, stale conflict with reload,
  hold/reject/reconsider with next action, invalid-export generic denial then retry,
  export/read/revoke/audit, forced session expiry/re-authentication, and sign-out
  denial.
- The browser request capture asserts every captured request host is `127.0.0.1`.
  The application mounts only the local stylesheet; the test makes no external,
  provider, model, service or public-endpoint request.
- Keyboard evidence passed: first Tab exposes a visible skip link, Enter moves focus
  to `main`, subsequent link/select/button focus has a non-zero outline, and forms are
  activated from the real browser.
- Semantic evidence passed at `1440x900`, `390x844`, and `320x700`: one each of
  header/nav/main/footer and h1; explicit sign-in labels; captioned/scoped tables;
  and `document.body.scrollWidth <= window.innerWidth` before and after analyst
  sign-in. Error recovery uses an explicit visible reload/retry link.
- The landing/footer/boundary and exercised workflow text explicitly distinguish
  synthetic automated tests from representative-user evidence and preserve
  `NO_GO`, `MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`,
  `synthetic_development_only`, `LIMITED`, and `no_recommendation_evidence`.

## Residual risks and follow-up

The passing automation establishes only local UI/workflow/accessibility mechanics. It
does not provide any participant result, expert relevance, retrieval/model-quality,
recruitment, transferability, price/value or production-readiness evidence. The
remaining gate is the prepared, genuinely moderated five-representative-user study in
`reports/verification/W08/moderated-study-protocol.md`; its five participant capture
records must be independently reviewed by the master.

## Scope confirmation

- No Git command of any kind was run.
- No dependency or lockfile changed.
- No protected W06 output was accessed.
- No participant evidence was created or implied.
- No file outside the packet's allowed paths was edited.

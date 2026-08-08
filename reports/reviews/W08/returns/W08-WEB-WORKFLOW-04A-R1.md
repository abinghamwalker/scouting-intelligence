# W08-WEB-WORKFLOW-04A-R1 return

## Scope and invariant

Implemented the local W08 presentation seam only.  Every shortlist and observation
read is tenant-scoped and policy-filtered; each mutation requires an authenticated
local principal plus submitted CSRF token and delegates to the existing workflow or
observation service.  The HTTP layer does not write workflow tables directly.

## Changed paths

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/base.html`
- `apps/web/templates/w08/queue.html`
- `apps/web/templates/w08/shortlist.html`
- `apps/web/templates/w08/entry.html`
- `tests/integration/test_w08_local_workflow_app.py`
- `tests/security/test_w08_web_security.py`

The packet did not modify contracts, services, policy, migrations, orchestration,
dependency state, Git state, protected W06 output, export implementation, or a
browser/E2E harness.

## Route/service and policy boundary

- Brief transitions use the narrow `/status/{action}` route.  Retrieval links and
  shortlist creation retain their dedicated routes.
- Queue, shortlist and entry reads are tenant-scoped.  Scout entry visibility is
  limited to the assigned-scoped resource; other roles are evaluated using the
  existing `R1Policy` resource rules.
- Entry transitions, comments, shortlist creation and entry creation delegate to
  `R1WorkflowService`.  Observation creation/amendment delegates to
  `ScoutObservationService`.
- Conflicting entry or observation versions return `409` with a safe reload path.
- Observation amendment controls are rendered only for the authenticated author's
  latest visible version.  Both creation and amendment require an explicit local
  evidence kind and reference.  Amendments preserve the stored evidence origin.
- UI boundary text continues to state that fixtures are synthetic automated tests,
  not representative-user evidence, and that model output is advisory.

## Focused verification

All commands exited 0:

```text
uv run ruff format src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py
uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
uv run mypy src/scouting/web/w08.py
uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
```

Focused pytest result: **5 passed** (one third-party TestClient deprecation warning).
The integration journey covers synthetic local login, submitted-CSRF denial, role
brief approval, pinned retrieval linkage, shortlist entry creation, assignment,
stale-lock conflict recovery, structured observation creation, immutable amendment
and an approver's absence of scout amendment controls.  Security tests in the
focused command remain included.

## Residual boundaries

This packet does not assert a representative-user result, model quality,
recruitment success, expert relevance, recommendation, transferability or
production readiness.  W06 remains `NO_GO` for
`MISSING_EXPERT_RELEVANCE_EVIDENCE`; the claim boundary remains
`resemblance_only`, synthetic-development-only and `LIMITED`.  Local browser,
accessibility, export and human-study acceptance remain for their owning packets
and the master gate.

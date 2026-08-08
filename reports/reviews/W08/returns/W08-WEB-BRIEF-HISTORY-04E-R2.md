# Subagent return

## Task

- task_id: `W08-WEB-BRIEF-HISTORY-04E`, revision `R2`
- invariant: status decisions preserve the old interpretation; correction appends a new attributable draft while rejection remains immutable.

## Files changed

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/queue.html`
- `apps/web/templates/w08/brief.html`
- `reports/reviews/W08/returns/W08-WEB-BRIEF-HISTORY-04E-R2.md`

## Summary and control map

- Added a service-backed rejected-to-draft correction route. It parses replacement
  title, responsibilities, constraint, preference and exemplars, uses a submitted
  lock, retains template/taxonomy/owner/visibility/trace identity, clears decision and
  submission fields by constructing a DRAFT, and delegates to the unchanged workflow
  service.
- Reject now requires a controlled `RoleBriefRejectionReason` plus note; malformed
  reasons return the generic denial rather than escaping as a 500.
- Queue creation is analyst-only and presents a retained supported W07 responsibility.
  Detail renders full immutable interpretation/decision fields. Controls are analyst
  submit/correct/replay, approver approve/reject, and no scout/admin mutation control.
- Status routes copy all persisted interpretation values; only correction reads the
  submitted replacement values.

## Tests run

- `uv run ruff format --check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0.
- `uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0.
- `uv run mypy src/scouting/web/w08.py` — exit 0.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0; 5 passed (one third-party TestClient deprecation warning).

## Risks and follow-up

- The unchanged lifecycle requires six revisions for create → submit → reject →
  correct draft → resubmit → approve, whereas the packet calls this a five-version
  chain. This is a packet wording inconsistency, not a history rewrite; the route
  implements the lawful six-step lifecycle. The required explicit six-step TestClient
  witness and stale/invalid count assertions remain a bounded follow-up for master
  review/rework. Replay equality and candidate membership remain deferred to 04F.

## Scope confirmation

- no Git operations, dependency/lock edits, protected-output access or out-of-scope edits.

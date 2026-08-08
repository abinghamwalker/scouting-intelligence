# Subagent return

## Task

- task_id: `W08-WEB-EXPORT-UI-04I`, revision `R1`
- invariant: rendered export controls use server-verified exact objects and appear only for unchanged-policy-authorised principals.

## Files changed

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/shortlist.html`
- `reports/reviews/W08/returns/W08-WEB-EXPORT-UI-04I-R1.md`

## Summary

- Shortlist detail derives `can_export` from `evidence_export.create` and the exact
  shortlist `R1Resource`. When policy authorises it, the form carries only hidden,
  server-verified brief ID/version, shortlist ID, and replay-link ID; no free-form
  object identity is exposed. Scout/admin and unauthorised owner-only views receive no
  control.
- Existing inventory/read/revoke routes remain exporter/audit verified and
  policy-filtered. This packet did not change exporter, audit, schema, or policy code.

## Tests run

- `uv run ruff format src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py` — exit 0.
- `uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0.
- `uv run mypy src/scouting/web/w08.py` — exit 0.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py` — exit 0; 21 passed, one third-party TestClient deprecation warning.

## Follow-up

- Fresh independent review should verify full analyst/approver create-read-revoke UI
  navigation and absent controls as part of 04I acceptance. Adversarial export depth
  remains explicitly out of scope for 04J.

## Scope confirmation

- no Git, dependency/lock, protected-output or forbidden-path changes.

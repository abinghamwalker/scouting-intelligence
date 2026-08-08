# W08-WEB-EXPORT-JOURNEY-04K-R1 return

Invariant: verified safe metadata is reachable only for the analyst owner or approver;
revoked and other-owner packs are never rendered readable.

Changed files: `src/scouting/web/w08.py`, `apps/web/templates/w08/export.html`,
`apps/web/templates/w08/exports.html`, and this return. The pack view now renders only
classification, evidence/claim/applicability, versions, IDs/digests, checksum, receipt
and limitations—not the raw underlying payload—and provides a CSRF-bound revocation
form. Successful revocation redirects to `/w08/exports`; inventory makes revoked rows
plain text with retained reason/time, never a pack link.

Focused checks:

```text
uv run ruff format --check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# pass after formatting
uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py
# exit 0
uv run mypy src/scouting/web/w08.py
# exit 0
uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py
# exit 0; 21 passed, one existing TestClient deprecation warning
```

The existing focused export/security suite witnessed policy denial, revocation,
tamper/confidentiality and append-only controls. A new dedicated role-complete browser
journey was not added in this return; retain that as follow-up rather than claiming it.
No Git, dependency/lock, protected-output, external destination, or out-of-scope edits.

# Subagent return

## Task

- task_id: `W08-WEB-EXPORT-04C`, revision `R1`
- invariant: export/audit routes expose no cross-role, tenant or object information,
  and all export mutations remain exporter-backed and fail closed.

## Files changed

- `src/scouting/web/w08.py`
- `reports/reviews/W08/returns/W08-WEB-EXPORT-04C-R1.md`

## Summary

- Added exporter-only local create (`POST /w08/exports`) and append-only revoke
  (`POST /w08/export/{pack_id}/revoke`) routes. They create opaque server IDs and
  delegate directly to `LocalEvidenceExporter`; no external destination exists.
- Existing verified read remains exporter-backed. Audit rendering now calls
  `AuditLedger.verify` first and denies on integrity failure.
- The shared form boundary accepts only `application/x-www-form-urlencoded`, rejects
  oversized declared/actual bodies before field parsing, decodes strict UTF-8, and
  converts malformed boundary input to generic denial without echoing submitted data.

## Route map

- create: authenticated analyst/approver CSRF form → `LocalEvidenceExporter.export`.
- read: same-tenant exporter or approver → `LocalEvidenceExporter.read` verified bytes.
- revoke: authenticated CSRF form with non-empty reason → `LocalEvidenceExporter.revoke`.
- audit: admin only → tenant `AuditLedger.verify` then append-only receipts.

## Tests run

- `uv run ruff format --check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0.
- `uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0.
- `uv run mypy src/scouting/web/w08.py` — exit 0.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py` — exit 0; 21 passed, one third-party TestClient deprecation warning.

## Risks and follow-up

- Existing exporter integration/security suites provide export, revocation, tamper,
  idempotency and confidentiality coverage. Fresh HTTP-specific export route tests and
  visible inventory/create UI remain an independent-review follow-up if required.
- W06 remains `NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE`; `resemblance_only`,
  `synthetic_development_only`, `LIMITED`, and `no_recommendation_evidence` are unchanged.

## Scope confirmation

- no Git operations, dependency/lock changes, protected-output access or out-of-scope edits.

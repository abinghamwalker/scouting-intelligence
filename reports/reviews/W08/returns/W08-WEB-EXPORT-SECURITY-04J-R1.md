# Subagent return

## Task

- task_id: `W08-WEB-EXPORT-SECURITY-04J`, revision `R1`
- objective: add route-level adversarial, bounded-input, tamper, and recovery
  evidence for the local evidence-pack presentation path.
- invariant: denied, malformed, replayed, tampered, and injected-failure HTTP
  requests change no export, revocation, audit, or evidence-pack state and disclose
  no protected or private value.

## Files changed

- `src/scouting/web/w08.py`
- `tests/security/test_w08_web_security.py`
- `reports/reviews/W08/returns/W08-WEB-EXPORT-SECURITY-04J-R1.md`

## Summary

- The shared URL-encoded parser now checks each incoming stream chunk against the
  remaining 64 KiB capacity before retaining it.  It continues to reject missing or
  wrong media type, non-decimal or over-limit declared length, malformed UTF-8, and
  all multipart/file-upload input through the generic denial surface.
- Added a single synthetic TestClient witness that records exact baseline tuples
  `(evidence_exports, evidence_export_revocations, audit_events, audit_receipts,
  evidence-pack file manifest)` before every denied/malformed/failure request.
- Witnessed analyst/approver success; scout/admin/other-analyst/foreign-tenant IDOR
  denial; missing/bad CSRF; wrong object tuple; repeat create idempotency; repeated
  revoke/read-after-revoke denial; and no secret-marker echo.
- Added a private `OWNER_ONLY` synthetic scout observation before export and proved
  its marker is absent from the canonical evidence-pack bytes exported by the
  unassigned analyst.
- Witnessed byte tamper and 64-lowercase-hex receipt-digest corruption (after the
  test deliberately removes the append-only trigger) across inventory, read, create,
  and revoke.  All four fail closed with their baseline unchanged.
- Injected audit append, guarded storage write/read, and the real SQLAlchemy
  `Connection.execute` `INSERT INTO evidence_exports` boundary.  Each creation/read
  failure returned generic denial with exact baseline retained; removal of each
  injection allowed one successful retry.

## Tests run

- `uv run ruff format --check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: 3 files already formatted.
- `uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: all checks passed.
- `uv run mypy src/scouting/web/w08.py`
  - exit status: 0
  - result: success; no issues in 1 source file.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: 23 passed; one third-party `TestClient` deprecation warning.
- `uv run bandit -q src/scouting/web/w08.py`
  - exit status: 0
  - result: no findings (exit 0).

## Artifacts/evidence

- `tests/security/test_w08_web_security.py::test_synthetic_automated_export_adversarial_atomicity_and_input_boundaries`
- This return document.

## Risks

- These are synthetic automated route witnesses, not representative-user evidence,
  scout judgement, positive model-quality evidence, or a W06 claim-boundary change.
- The test deliberately bypasses the audit-receipt update trigger only in its isolated
  temporary SQLite database to prove the retained ledger verifier fails closed; it
  does not alter production schema or policy.

## Follow-up items

- Fresh independent security review of the packet changes and master reproduction.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected-output access, external service/network use, or delegation: confirmed.
- no edits outside `allowed_paths`: confirmed.

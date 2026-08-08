# Subagent return

## Task

- task_id: W08-EXPORT-IMPORT-BOUNDARY-05E-R1
- objective: Relocate the local evidence-export application service from operations to workflow without changing export, authorisation, audit, or storage behaviour.
- invariant: The exporter remains fail-closed and functionally identical; callers import it from workflow; operations is telemetry-only; all approved import contracts pass.

## Files changed

- `src/scouting/operations/evidence_export.py` (removed after content-preserving relocation)
- `src/scouting/operations/__init__.py`
- `src/scouting/workflow/evidence_export.py` (new sole exporter implementation)
- `src/scouting/workflow/__init__.py`
- `src/scouting/web/w08.py`
- `tests/integration/test_w08_evidence_export.py`
- `tests/security/test_w08_export_boundaries.py`
- `reports/reviews/W08/returns/W08-EXPORT-IMPORT-BOUNDARY-05E-R1.md`

## Summary

- Relocated `LocalEvidenceExporter`, `EvidenceExportDenied`, `EvidenceExportIntegrityError`, and `EvidenceExportResult` from `scouting.operations.evidence_export` to `scouting.workflow.evidence_export` with exact pre-move implementation content.
- Routed the W08 web composition and the two exporter-focused test modules through `scouting.workflow`; switched the direct policy-path test import to `scouting.workflow.evidence_export`.
- Restored `scouting.operations` to its telemetry-only `LocalTelemetry` and `TelemetrySnapshot` surface. No compatibility re-export was added.
- Import graph before: `web.w08` and exporter tests -> `scouting.operations` -> `operations.evidence_export` -> `policy`/`audit`/`storage`. Import graph after: `web.w08` and exporter tests -> `scouting.workflow` -> `workflow.evidence_export` -> `policy`/`audit`/`storage`; `scouting.operations` -> `telemetry` only.
- Confirmed no functional line delta in the exporter beyond module/package routing: relocated file content exactly matches the pre-move source; old module is absent.

## Tests run

- command: `uv run ruff format --check src/scouting/operations/__init__.py src/scouting/workflow/__init__.py src/scouting/workflow/evidence_export.py src/scouting/web/w08.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_local_workflow_app.py tests/e2e/test_w08_local_workflow_playwright.py`
  - exit status: 0
  - result: 9 files already formatted.
- command: `uv run ruff check src/scouting/operations/__init__.py src/scouting/workflow/__init__.py src/scouting/workflow/evidence_export.py src/scouting/web/w08.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_local_workflow_app.py tests/e2e/test_w08_local_workflow_playwright.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/workflow/evidence_export.py src/scouting/web/w08.py`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `uv run lint-imports`
  - exit status: 0
  - result: 3 contracts kept: current approved dependency direction, serving/source boundary, and workflow-policy/source boundary.
- command: `uv run pytest -q tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_local_workflow_app.py tests/e2e/test_w08_local_workflow_playwright.py`
  - exit status: 0
  - result: 37 passed in 25.50s; one third-party Starlette TestClient deprecation warning.
- command: `uv run bandit -q src/scouting/workflow/evidence_export.py src/scouting/web/w08.py`
  - exit status: 0
  - result: no findings.

## Artifacts/evidence

- `reports/reviews/W08/returns/W08-EXPORT-IMPORT-BOUNDARY-05E-R1.md`
- Import-contract evidence: 3/3 contracts kept.
- Security/export/browser regression evidence: focused pytest 37 passed; focused Bandit no findings.

## Risks

- No functional, authorisation, audit, storage, claim-boundary, or import-policy residual identified within this packet. The retained third-party TestClient deprecation warning is outside packet scope.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed; no Git command or Git-invoking verifier was run.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected-output or participant-evidence access, creation, inference, or representation: confirmed.
- no edits outside `allowed_paths`: confirmed.

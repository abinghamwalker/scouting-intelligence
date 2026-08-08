# Subagent return

## Task

- task_id/revision: W08-AUDIT-EXPORT-TAMPER-05A-R1
- invariant: No audited mutation, export, verified read or revocation proceeds over a malformed tenant ledger; assignment-based private export scope belongs only to a current, enabled, same-tenant actor explicitly holding `scout`.

## Files changed

- `src/scouting/audit/ledger.py`
- `src/scouting/operations/evidence_export.py`
- `tests/security/test_w08_auth_audit.py`
- `tests/security/test_w08_export_boundaries.py`
- `tests/integration/test_w08_evidence_export.py`
- `reports/reviews/W08/returns/W08-AUDIT-EXPORT-TAMPER-05A-R1.md`

## Audit precondition and assignment-qualification logic

- `AuditLedger.append` now verifies the complete existing tenant chain before it creates an event or receipt. `verify` rejects orphan events, orphan/cross-tenant receipt events, sequence gaps, digest-chain errors, malformed JSON export scopes, malformed UUID/timestamp values and SQL/row-shape failures as `AuditIntegrityError`.
- Local export creation, verified read and revoke each verify the tenant ledger before selection, storage, row writes or return. A malformed ledger is surfaced as a fail-closed `EvidenceExportIntegrityError`.
- Current assignment is derived only from each entry's `latest_revision`, then qualified by joins to an enabled same-tenant local account and explicit `scout` role. Earlier assignments, analyst-only accounts, disabled scouts and non-matching tenant rows are not included in either authorisation scope or `workflow_action_origins` visibility.
- The W06 boundary is unchanged: `NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`, `synthetic_development_only` and `LIMITED` remain fixed. All fixtures are synthetic automated mechanics, not participant or representative-user evidence.

## Tampering, rollback and confidentiality results

- An orphan audit event causes a caught attempted append to fail before creating a new receipt; the caller retains exactly its pre-existing event/receipt counts.
- After a valid export, injected orphan audit state blocks new export, verified read and revoke before any new evidence row, revocation, receipt or bytes appear.
- A former assignment has no private-content or origin side channel. A valid current multi-role analyst/scout sees only legitimately assigned owner-only scope; an author sees their own scope. Analyst-only and disabled latest assignments yield no private content and no `human_entered_local` origin.
- Existing savepoint rollback, idempotency, tamper, revocation, path and policy-drift witnesses remain green.

## Tests run

- command: `uv run ruff format --check src/scouting/audit/ledger.py src/scouting/operations/evidence_export.py tests/security/test_w08_auth_audit.py tests/security/test_w08_export_boundaries.py tests/integration/test_w08_evidence_export.py`
  - exit status: 0
  - result: 5 files already formatted.
- command: `uv run ruff check src/scouting/audit/ledger.py src/scouting/operations/evidence_export.py tests/security/test_w08_auth_audit.py tests/security/test_w08_export_boundaries.py tests/integration/test_w08_evidence_export.py`
  - exit status: 0
  - result: all focused lint checks passed.
- command: `uv run mypy src/scouting/audit/ledger.py src/scouting/operations/evidence_export.py`
  - exit status: 0
  - result: success; no issues found in 2 source files.
- command: `uv run pytest -q tests/security/test_w08_auth_audit.py tests/security/test_w08_export_boundaries.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py`
  - exit status: 0
  - result: 31 passed in 0.99s.
- command: `uv run bandit -q src/scouting/audit/ledger.py src/scouting/operations/evidence_export.py`
  - exit status: 0
  - result: 0; no reported findings.

## Residual risks/follow-ups

- Same-host database administrators remain in the local trust domain; tamper detection is application-level and not external notarisation.
- Master should independently reproduce the packet checks and obtain fresh independent security review before acceptance. Genuine moderated representative-user evidence remains a separate, unmet gate.

## Scope confirmation

- no Git operations: confirmed.
- no dependency or lockfile changes: confirmed.
- no protected-output or external access: confirmed.
- no edits outside `allowed_paths`: confirmed.

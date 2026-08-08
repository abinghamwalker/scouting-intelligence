# Subagent return

## Task

- task_id: W08-EXPORT-03-R1
- objective: Implement a fail-closed, local-only, policy-bound evidence-pack export with immutable guarded bytes, append-only receipts, revocation and recovery checks.

## Files changed

- `src/scouting/operations/evidence_export.py`
- `src/scouting/operations/__init__.py`
- `tests/integration/test_w08_evidence_export.py`
- `tests/security/test_w08_export_boundaries.py`
- `reports/reviews/W08/returns/W08-EXPORT-03-R1.md`

## Summary

- `LocalEvidenceExporter` validates the complete retained authorisation policy through `R1AuthorizationPolicy` and exact retained export-policy contents before each sensitive operation; policy drift defaults to denial.
- Evidence packs have no destination argument and are written only to the declared `evidence_packs` `GuardedStorage` root using an immutable, canonical JSON path derived only from UUIDs. The pack includes classification, selected underlying workflow values, model/data/taxonomy versions, fixed W06 limitations, SHA-256 checksums and its audit receipt.
- Every generated record is explicitly `synthetic_automated_test`; the fixed language remains `NO_GO`, `MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`, `synthetic_development_only` and `LIMITED`.
- Selection is tenant-scoped and authorisation-bound. Owner-only observations are emitted only for their author or a currently assigned exporter; team observations remain team-visible. Password/session/provider fields are never selected.
- Export and revocation operations use database savepoints. Audit receipt plus export intent are inserted before artifact creation; a caught storage/audit failure rolls back export, audit and revocation rows, and an identical retry succeeds exactly once. Guarded storage rejects traversal and symlink escape; digest/classification/claim-boundary checks reject tampered readback.

## Tests run

- command: `uv run ruff format --check src/scouting/operations/evidence_export.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/operations/evidence_export.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: all focused lint checks passed.
- command: `uv run mypy src/scouting/operations/evidence_export.py`
  - exit status: 0
  - result: success; no issues found in 1 source file.
- command: `uv run pytest -q tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_auth_audit.py tests/unit/test_guarded_storage.py`
  - exit status: 0
  - result: 32 passed in 0.69s; fixtures are synthetic automated mechanics only.

## Artifacts/evidence

- `src/scouting/operations/evidence_export.py`: W08 local export/revocation implementation.
- `tests/integration/test_w08_evidence_export.py`: canonical/idempotent export, confidentiality filtering, audit receipt, savepoint recovery and retry witnesses.
- `tests/security/test_w08_export_boundaries.py`: role/tenant denial, tamper, append-only revocation, policy drift and guarded-path witnesses.
- `reports/reviews/W08/returns/W08-EXPORT-03-R1.md`: this packet handback.

## Risks

- Local same-host administrators remain within the shared trust domain; the hash chain makes application-level tampering detectable but is not an external notarisation service.
- Representative-user moderated workflow evidence is intentionally absent and cannot be inferred from these synthetic automated tests.

## Follow-up items

- Master: independently reproduce the packet checks, verify composition with the workflow service/UI, and obtain an independent security review before acceptance.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

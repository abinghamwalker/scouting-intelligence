# Subagent return

## Task

- task_id: `W08-EXPORT-BYTE-TAMPER-05C`, revision `R1`
- objective: Correct the independent-review P1 so byte-tampered immutable evidence
  packs fail closed for inventory and revocation as well as readback and idempotent
  create.
- invariant: With a valid database and audit chain, a missing, unreadable,
  malformed, noncanonical, classification/claim-boundary-invalid, or
  digest-mismatched immutable pack makes inventory, read, idempotent create, and
  revoke fail generically without a database, receipt, revocation, or file change.

## Files changed

- `src/scouting/operations/evidence_export.py`
- `src/scouting/web/w08.py`
- `tests/integration/test_w08_evidence_export.py`
- `tests/security/test_w08_web_security.py`
- `reports/reviews/W08/returns/W08-EXPORT-BYTE-TAMPER-05C-R1.md`

## Summary

- Added `LocalEvidenceExporter.verify_persisted_pack`, the exporter-owned public
  boundary for guarded storage reads, SHA-256 verification, strict UTF-8/JSON
  decoding, canonical-JSON bytes, classification, claim-boundary, model-evidence,
  and applicability checks. Readback and idempotent create use it through the
  existing verification paths.
- Inventory now verifies every policy-visible row before rendering. Revocation
  selects the exact `relative_path` and verifies it after authorisation but before
  any revocation/audit append.
- The route adversarial witness now uses separate fresh applications: byte tamper
  alone denies inventory/read/idempotent-create/revoke; receipt-ledger corruption
  alone denies the same matrix. Neither matrix shares a fault.
- Core synthetic witnesses cover missing bytes, invalid UTF-8, malformed JSON,
  noncanonical JSON, a forged matching digest with bad classification, a forged
  matching digest with bad claim boundary, and ordinary digest mismatch. For each
  fault, read/idempotent-create/revoke reject and retain the exact post-export
  baseline `(evidence_exports=1, revocations=0, audit_events=1, audit_receipts=1)`.
  The isolated forged-metadata variants drop only the temporary database's
  `evidence_exports_reject_update` trigger before mutation; they do not alter the
  application schema or policy.

## Verification map and baselines

| Boundary | Verification | Baseline/result |
| --- | --- | --- |
| Exporter read | public persisted-pack verifier | all byte variants reject before disclosure |
| Idempotent create | existing-row persisted-pack verifier | all byte variants reject; no new row/receipt/file |
| Inventory | verifies every visible metadata row before template rendering | isolated byte-only and ledger-only HTTP matrices return generic 403 and retain their complete `(exports, revocations, events, receipts, file-manifest)` tuple |
| Revoke | verifies selected pack before nested insert/audit append | all core and HTTP byte variants retain revocations `0`; no audit append |
| Retry | guarded-storage read fault removed | one revoke succeeds exactly once: `(1,0,1,1)` becomes `(1,1,2,2)` |

## Tests run

- `uv run ruff format --check src/scouting/operations/evidence_export.py src/scouting/web/w08.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: 6 files already formatted.
- `uv run ruff check src/scouting/operations/evidence_export.py src/scouting/web/w08.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py`
  - exit status: 0; all checks passed.
- `uv run mypy src/scouting/operations/evidence_export.py src/scouting/web/w08.py`
  - exit status: 0; no issues in 2 source files.
- `uv run pytest -q tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/security/test_w08_auth_audit.py`
  - exit status: 0; 47 passed, with one third-party Starlette TestClient deprecation warning.
- `uv run bandit -q src/scouting/operations/evidence_export.py src/scouting/web/w08.py`
  - exit status: 0; no findings.

## Artifacts/evidence

- `tests/integration/test_w08_evidence_export.py::test_persisted_pack_faults_block_read_idempotency_and_revoke_atomically`
- `tests/integration/test_w08_evidence_export.py::test_unreadable_pack_removal_of_fault_allows_one_verified_retry`
- `tests/security/test_w08_web_security.py::test_synthetic_automated_export_adversarial_atomicity_and_input_boundaries`
- `reports/reviews/W08/returns/W08-EXPORT-BYTE-TAMPER-05C-R1.md`

## Risks

- The retained witnesses are synthetic automated checks. They are not scout
  judgements, representative-user participation, model evidence, or a change to the
  W06 `NO_GO` / `resemblance_only` / `synthetic_development_only` / `LIMITED`
  boundary.
- A caller that can bypass both the local database's append-only trigger and alter
  storage bytes still cannot make these policy-visible paths accept a noncanonical
  or boundary-invalid pack; the temporary forged-metadata cases demonstrate that
  fail-closed property.

## Follow-up items

- Fresh independent security review of this bounded P1 correction.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no protected-output access, external/network/provider activity, delegation, or
  participant evidence creation: confirmed.

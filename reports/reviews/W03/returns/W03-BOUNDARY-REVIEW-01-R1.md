# Subagent return

## Task

- task_id: `W03-BOUNDARY-REVIEW-01`
- objective: Independently audit the completed W03 contract, temporal, guarded
  storage, migration/RLS, authorisation, serving, audit, import, and local-runtime
  boundaries.

## Files changed

- `tests/security/test_w03_boundary_audit.py`
- `reports/reviews/W03/boundary-audit.md`
- `reports/reviews/W03/returns/W03-BOUNDARY-REVIEW-01-R1.md`

## Summary

- Added ten independent reviewer challenges without using the producer expected-result
  oracle or any protected fixture.
- Verified strict contracts, equality cutoff rejection, canonical lineage and tamper
  rejection, ambiguous identity exclusion, guarded path/symlink rejection, non-owner
  RLS, audit immutability, confidential-response minimisation, a fresh application
  journey, missing-model fail-closed behaviour, local telemetry/runtime controls, and
  import-linter contracts.
- Reproduced one `P1` same-tenant object-authorisation/integrity defect: analyst B can
  reuse analyst A's persisted role-brief ID/version, receive `200`, and create
  retrieval/audit activity against A's brief because the workflow authorises the
  inbound owner and silently ignores the database conflict.
- Recommendation: **REWORK**. This is a reviewer recommendation only, not
  self-approval or a phase-gate decision.

## Tests run

- command:
  `SCOUTING_DATABASE_URL='postgresql+psycopg://scouting_owner:***@127.0.0.1:55432/scouting' uv run pytest -q tests/security/test_w03_boundary_audit.py`
  - exit status: `1`
  - result: `9 passed, 1 failed, 1 warning`; the retained failure is the P1
    same-tenant persisted-owner collision regression.
- command:
  `uv run ruff format --check tests/security/test_w03_boundary_audit.py`
  - exit status: `0`
  - result: one file already formatted.
- command:
  `uv run ruff check tests/security/test_w03_boundary_audit.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run lint-imports --no-cache`
  - exit status: `0`
  - result: 27 files and 37 dependencies analysed; three contracts kept, zero
    broken.
- command:
  `uv run python -c "from pathlib import Path; text=Path('reports/reviews/W03/boundary-audit.md').read_text(); assert all(term in text for term in ['W03.1', 'W03.2', 'W03.3', 'W03.4', 'W03.5', 'W03.6', 'G-W03', 'G1'])"`
  - exit status: `0`
  - result: all required mapping terms present.

## Artifacts/evidence

- `tests/security/test_w03_boundary_audit.py`
  - failing reproduction:
    `test_same_tenant_existing_brief_owner_collision_is_denied`
- `reports/reviews/W03/boundary-audit.md`
  - full readback, requirement mapping, ranked defect, reproduction, and bounded
    correction
- `orchestration/reviews/REVIEW-W03-VERTICAL-01-R5.yaml`
  - final producer master review read as input only
- `orchestration/reviews/REVIEW-W03-ARCHITECTURE-01-R1.yaml`
  - final architecture master review read as input only

## Risks

- `P1`: persisted object ownership is not checked when a role-brief create collides
  within the same tenant. A valid second analyst can attach retrieval and audit
  activity to the first analyst's brief.
- The same silent-conflict pattern exists for client-supplied shortlist IDs and must
  receive the same conflict-aware ownership/idempotency treatment.
- W03 remains deterministic synthetic evidence only. Protected-fixture, fresh-sync,
  phase-gate, and checkpoint authority remains with the master.

## Follow-up items

- In the existing workflow transaction, make role-brief and shortlist inserts
  conflict-aware: accept only exact same-owner immutable idempotent replay; deny every
  owner/content mismatch before downstream or audit writes.
- Add same-tenant two-analyst role-brief and shortlist collision regressions and rerun
  this reviewer packet after master acceptance of the correction.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no Docker operations: confirmed
- no protected fixture or protected expected-result access: confirmed

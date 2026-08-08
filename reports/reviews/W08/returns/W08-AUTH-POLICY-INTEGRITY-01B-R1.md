# Subagent return

## Task

- task_id: W08-AUTH-POLICY-INTEGRITY-01B-R1
- objective: Prove retained deny-by-default policy semantics, TEAM/OWNER_ONLY decisions, and caught account-creation failures remain fail-closed and atomic.

## Files changed

- src/scouting/policy/r1.py
- tests/security/test_w08_auth_audit.py
- reports/reviews/W08/returns/W08-AUTH-POLICY-INTEGRITY-01B-R1.md

## Summary

- Bound runtime startup to every retained W08 authorisation semantic: schema version, policy ID, status, default-deny value, exact role grants, exact global denies, exact `admin_not_granted`, and all visibility settings. Any mismatch raises before authorisation.
- Corrected TEAM semantics to the retained policy: any same-tenant principal with an explicit action grant may access `TEAM`; actions containing `assigned` still require owner/assignment; `OWNER_ONLY` always requires owner/assignment. Tenant, unknown/ungranted-action, and implicit-admin denials remain generic and fail closed.
- Wrapped the multi-row account, credential, and role inserts in a nested SQLAlchemy savepoint. A caught role foreign-key failure now rolls back every newly inserted account row and credential before returning the generic authentication failure.
- The evidence is synthetic automated security testing only. It makes no representative-user, security-certification, model-quality, or production-readiness claim.

## Tests run

- command: `uv run ruff format --check src/scouting/policy/r1.py src/scouting/audit/ledger.py tests/security/test_w08_auth_audit.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/policy/r1.py src/scouting/audit/ledger.py tests/security/test_w08_auth_audit.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/policy/r1.py src/scouting/audit/ledger.py`
  - exit status: 0
  - result: no issues found in 2 source files.
- command: `uv run pytest -q tests/security/test_w08_auth_audit.py tests/security/test_application_authorization.py tests/security/test_database_boundaries.py`
  - exit status: 0
  - result: 26 passed in 0.69s.

## Artifacts/evidence

- `tests/security/test_w08_auth_audit.py` — synthetic positive and adversarial witnesses for policy drift, TEAM and OWNER_ONLY access, assignment, tenant denial, admin denial, savepoint rollback, sessions, and receipt tampering.
- `src/scouting/policy/r1.py` — retained-policy binding, deny-by-default visibility enforcement, and savepoint-atomic account creation.

## Risks

- The local SQLite host administrator remains in the same trust domain; receipt verification is tamper-evident, not an independent trust service.
- These synthetic automated tests do not satisfy W08’s moderated representative-user requirement.

## Follow-up items

- Master reproduction and fresh independent security review are required before packet acceptance.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no external access or protected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

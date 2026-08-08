# Subagent return

## Task

- task_id: W08-AUTH-AUDIT-01-R1
- objective: Implement local R1 identities, password-backed revocable sessions, deny-by-default object authorisation, and hash-chained append-only audit receipts.

## Files changed

- src/scouting/policy/r1.py
- src/scouting/policy/__init__.py
- src/scouting/audit/ledger.py
- src/scouting/audit/__init__.py
- tests/security/test_w08_auth_audit.py
- reports/reviews/W08/returns/W08-AUTH-AUDIT-01-R1.md

## Summary

- Added the four local role definitions and a local SQLite-backed account/session service. Passwords use salted `hashlib.scrypt`, including the unknown-account dummy path; sessions and CSRF values are represented in SQLite only as HMAC digests. Sessions have positive TTL validation, explicit revocation, and rotation that revokes the superseded session.
- Added a fail-closed R1 action policy that validates the retained `w08-authorization-v1` file at construction and rejects policy/grant drift. Tenant mismatch, unknown/ungranted actions, ownership mismatch, missing assignment, invalid visibility, global prohibited actions, and the absence of an explicit grant deny with a generic response. Admin is intentionally not granted recruitment approval.
- Added transactional audit receipt append and full chain verification. The receipt digest binds the predecessor, sequence, event digest, and event ID; direct database receipt mutation is rejected by the migration trigger and inserted malformed data is detected by verification.
- Added synthetic automated security tests only. They make no real-user, moderated-study, security-certification, model-quality, or production-readiness claim.

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
  - result: 19 passed in 0.63s.

## Artifacts/evidence

- `tests/security/test_w08_auth_audit.py` — synthetic automated authentication, authorisation, session, CSRF, privacy, and audit-tampering evidence.
- `src/scouting/policy/r1.py` — local R1 session and object-authorisation implementation.
- `src/scouting/audit/ledger.py` — local transactional receipt-chain implementation.

## Risks

- Local SQLite and its host administrator remain within the same trust domain; receipt verification is tamper-evident, not a separate trust service.
- The service is a policy primitive and has not yet been wired to the web/API composition path; that belongs to a separately owned packet.
- Tests are synthetic automated system evidence and do not satisfy the representative-user gate.

## Follow-up items

- Master to reproduce the focused suite after integration and submit the packet to independent security review.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

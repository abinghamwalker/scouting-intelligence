# W08 authentication and authorisation report

Status: **AUTOMATED MECHANICS AND INDEPENDENT REVIEW PASS; HUMAN STUDY PENDING**

The local-only identity layer implements analyst, scout, approver and admin accounts.
Passwords are salted `scrypt` values; session and CSRF secrets are persisted only as
HMAC digests. Sessions have positive TTL validation, explicit expiry, revocation and
rotation with revocation of the superseded token. The study harness can expire exactly
one current unrevoked session by actor ID without reading a token or password.

The `w08-authorization-v1` policy is loaded fail closed and binds its schema version,
policy ID/status, default deny, exact grants, global denies, visibility rules and
explicitly absent admin recruitment authority. Unknown actions, tenant mismatch,
wrong owner/assignment, disabled actors, policy drift, invalid visibility and absent
grants return generic denials before mutation.

Object visibility is:

- `TEAM`: same-tenant principals need an explicit action grant;
- assignment-scoped actions additionally require current ownership/assignment;
- `OWNER_ONLY`: author or current valid owner/assignment only;
- admin: local account administration/audit only, never implicit recruitment or
  evidence-export authority.

Positive and negative synthetic witnesses cover login, unknown-account dummy work,
CSRF, expiry, revocation, fixation-resistant rotation, policy drift, same/cross-tenant
access, current/former assignment, admin denial, account-creation rollback and audit
tampering. Producer-focused results include 26 auth/policy/database tests and the
study-harness reproduction includes 18 harness/auth tests, all passing.

Fresh independent R4 review passed with P0/P1/P2/P3 all zero and 72 focused tests.
It independently proved that every applicable grant composes by union across
analyst/scout/approver multi-role accounts, while scout-only, OWNER_ONLY, former-
assignment and cross-tenant paths remain denied generically.

This is local workflow security evidence, not an external security certification or
representative-user result.

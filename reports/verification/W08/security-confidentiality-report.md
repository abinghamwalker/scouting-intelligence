# W08 security and confidentiality report

Status: **AUTOMATED, MASTER AND FRESH INDEPENDENT REVIEW PASS; HUMAN STUDY PENDING**

W08 is local-only and deny by default. The master reproduced the authentication,
authorisation, web, audit, export, concurrency and recovery corrections without any
external account, service, model call, container, remote, public endpoint or protected
W06 output.

## Control outcomes

| Control | Master automated outcome |
| --- | --- |
| Local identities and sessions | PASS — salted `scrypt`, digest-only token/CSRF persistence, positive TTL, expiry, revocation, rotation and disabled-account denial |
| Role and object authorisation | PASS — exact policy binding, default deny, tenant/owner/current-assignment checks, explicit multi-role union and generic IDOR denial |
| Scout brief/replay confidentiality | PASS — pre-approval briefs are absent; approved metadata does not expose a link/projection/control until the exact current assignment; removal/reassignment revokes visibility |
| Private/team visibility | PASS — TEAM still requires a grant; OWNER_ONLY requires owner or exact current assignment; former and foreign actors deny |
| Privileged local export | PASS — scoped owner/approver creation, admin/scout/other-owner/foreign denial, no external destination |
| Pack and audit tampering | PASS — canonical bytes, checksum, classification/claim binding, inventory/read/create/revoke verification and full receipt identity/context/time binding |
| Sensitive input and file handling | PASS — bounded URL-encoded bodies, strict UTF-8, media-type denial, path/root/symlink guards and non-echoing generic errors |
| Replay and candidate handling | PASS — pinned request/result/run/lineage/version identity and persisted ordered-candidate allowlist; no protected-output reconstruction |
| Concurrency and recovery | PASS — optimistic conflicts preserve the winner; storage, SQL and audit faults are atomic and one clean retry succeeds without duplicate state |
| Browser and accessibility mechanics | PASS — local Chromium plus master browser review at 1440, 390 and 320 pixels, keyboard/focus/landmark/label checks and no body overflow |

## Independent-review history

R1 failed with three P1 findings: synthetic automation was structured as human-origin,
byte tampering did not independently block inventory/revocation, and receipt identity/
tenant/time were not fully digest-bound. All three received bounded corrections and
were independently closed in R2.

R2 then failed with two P1 scout web disclosures and one P2 mixed-role composition
defect. The bounded 04P correction now uses a shared brief predicate and a separate
exact-link predicate, adds an explicit owner-only replay grant, enumerates every owned
action rather than inferring suffix semantics, and covers TEAM, OWNER_ONLY,
assignment-clearance/reassignment, mixed-role and cross-tenant paths. The master
reproduction passed 31 focused tests plus Ruff, mypy and Bandit.

R3 closed those findings but found one P2 fail-closed multi-role shortlist/transition
composition defect. The narrowed 04Q correction now shares one target-to-actions
mapping between service enforcement and presentation and authorises the exact resource
when any independently applicable grant succeeds. Master reproduction passed 33 tests
plus Ruff, mypy and Bandit.

Fresh independent R4 review returned **PASS**, with P0/P1/P2/P3 all zero, 72 focused
tests passing, clean Bandit and independent positive/negative probes for legitimate
multi-role, scout current/unassigned/former, OWNER_ONLY and foreign-tenant paths. No
security rework remains. Security automation cannot satisfy the separate five-person
moderated representative-user gate.

## Trust and claim limits

SQLite triggers and digest chains are tamper-evident within the local application
trust boundary; they are not external notarisation against a hostile machine owner.
No workflow success establishes model relevance, recommendation quality, transfer
value, recruitment success or production readiness. W06 remains `NO_GO` solely for
`MISSING_EXPERT_RELEVANCE_EVIDENCE`, with `resemblance_only`,
`synthetic_development_only`, `LIMITED` applicability and
`no_recommendation_evidence`.

# W08 independent security and confidentiality review R3

## Review identity and verdict

- Review ID: `W08-INDEPENDENT-SECURITY-05-R3`
- Reviewer role: independent security/confidentiality reviewer; report-only
- Verdict: **FAIL**
- Severity totals: **P0 0 / P1 0 / P2 1 / P3 0**
- Representative-user gate: **PENDING — 0/5 genuine authorised reviewed records**

The two R2 P1 disclosure paths and the exact R2 P2 own-draft path are corrected. All
three earlier R1 P1 corrections also reproduce as closed. The full packet-focused
suite passes with 70 tests and Bandit reports no issue. However, fresh inspection and
an independent TestClient probe found another role-presence override in shortlist and
entry reads. It violates the R3 packet's explicit requirement that multi-role grants
compose by union. This is a denial of an explicitly granted workflow capability, not
a confidentiality disclosure, so it is P2; it nevertheless leaves the packet's
definition incomplete and requires rework before this review can PASS.

Synthetic automation is mechanics evidence only. It is not representative-user
evidence and cannot satisfy the separate five-person gate.

## Reviewed scope

I read `AGENTS.md`, both complete controlling HTML plans, the R1/R2/R3 independent
review packets, the complete R1 and R2 reviews, the correction packets and returns,
and the return template. The correction/control packet and return paths were:

- `orchestration/task_packets/W08-WEB-SCOUT-BRIEF-AUTHZ-04P-R1.yaml`
- `reports/reviews/W08/returns/W08-WEB-SCOUT-BRIEF-AUTHZ-04P-R1.md`
- `orchestration/task_packets/W08-AUDIT-RECEIPT-BINDING-05B-R1.yaml`
- `reports/reviews/W08/returns/W08-AUDIT-RECEIPT-BINDING-05B-R1.md`
- `orchestration/task_packets/W08-WEB-EVIDENCE-ORIGIN-04N-R1.yaml`
- `reports/reviews/W08/returns/W08-WEB-EVIDENCE-ORIGIN-04N-R1.md`
- `orchestration/task_packets/W08-EXPORT-BYTE-TAMPER-05C-R1.yaml`
- `reports/reviews/W08/returns/W08-EXPORT-BYTE-TAMPER-05C-R1.md`
- `orchestration/task_packets/W08-BROWSER-A11Y-04B-R2.yaml`
- `reports/reviews/W08/returns/W08-BROWSER-A11Y-04B-R2.md`
- `orchestration/task_packets/W08-BROWSER-OVERFLOW-04M-R1.yaml`
- `reports/reviews/W08/returns/W08-BROWSER-OVERFLOW-04M-R1.md`

Exact implementation/configuration paths reviewed:

- `configs/policies/w08-authorization.yaml`
- `configs/policies/w08-export.yaml`
- `migrations/versions/0002_w08_workflow.sql`
- `src/scouting/contracts/workflow.py`
- `src/scouting/contracts/audit.py`
- `src/scouting/policy/r1.py`
- `src/scouting/audit/ledger.py`
- `src/scouting/workflow/r1.py`
- `src/scouting/observations/r1.py`
- `src/scouting/operations/evidence_export.py`
- `src/scouting/web/w08.py`
- `services/api/w08_main.py`
- `scripts/run_w08_study.py`
- `apps/web/templates/w08/base.html`
- `apps/web/templates/w08/landing.html`
- `apps/web/templates/w08/queue.html`
- `apps/web/templates/w08/brief.html`
- `apps/web/templates/w08/shortlist.html`
- `apps/web/templates/w08/entry.html`
- `apps/web/templates/w08/audit.html`
- `apps/web/templates/w08/export.html`
- `apps/web/templates/w08/exports.html`
- `apps/web/templates/w08/error.html`
- `apps/web/static/w08/app.css`

Exact test paths reviewed and executed:

- `tests/contracts/test_w08_workflow_contracts.py`
- `tests/security/test_w08_auth_audit.py`
- `tests/security/test_w08_workflow_access.py`
- `tests/security/test_w08_export_boundaries.py`
- `tests/security/test_w08_web_security.py`
- `tests/integration/test_w08_workflow.py`
- `tests/integration/test_w08_evidence_export.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `tests/integration/test_w08_study_harness.py`
- `tests/e2e/test_w08_local_workflow_playwright.py`

Exact retained W08 evidence paths reviewed:

- `reports/verification/W08/moderated-study-protocol.md`
- `reports/verification/W08/moderated-study-capture-template.yaml`
- `reports/verification/W08/moderated-study-summary-template.yaml`
- `reports/verification/W08/authentication-authorization-report.md`
- `reports/verification/W08/workflow-audit-export-recovery-report.md`
- `reports/verification/W08/browser-accessibility-report.md`
- `reports/verification/W08/limitations.md`
- `reports/verification/W08/protected-output-boundary.md`
- `reports/verification/W08/representative-user-evidence-status.md`

Protected W06 expected outputs, `tests/fixtures/synthetic/protected/**`, and
`reports/evaluation/W06/**` were not opened, searched, or reconstructed.

## Commands and results

1. Complete focused pytest command exactly as specified by the packet:

   `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/security/test_w08_auth_audit.py tests/security/test_w08_workflow_access.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/integration/test_w08_study_harness.py tests/e2e/test_w08_local_workflow_playwright.py`

   Exit 0: **70 passed**, one third-party Starlette TestClient deprecation warning,
   26.83 seconds.

2. Packet Bandit command:

   `uv run bandit -q -r src/scouting/policy/r1.py src/scouting/audit/ledger.py src/scouting/workflow/r1.py src/scouting/observations/r1.py src/scouting/operations/evidence_export.py src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py`

   The first sandboxed attempt exited 2 before scanning because the sandbox denied
   uv-cache access at `/Users/adrian/.cache/uv/sdists-v9/.git`. No Git executable or
   Git command was invoked and no repository path changed. The same packet command
   was rerun through the approved read-only `uv run bandit` boundary and exited 0
   with no findings.

3. Focused correction matrix:

   `uv run pytest -q tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_scout_brief_and_replay_authorization_matrix tests/security/test_w08_auth_audit.py::test_receipt_identity_context_and_time_tampering_fail_before_next_action tests/integration/test_w08_evidence_export.py::test_persisted_pack_faults_block_read_idempotency_and_revoke_atomically tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_shortlist_assignment_observation_and_conflict tests/integration/test_w08_study_harness.py::test_human_mode_route_origin_is_server_selected_mechanics_only tests/security/test_w08_web_security.py::test_synthetic_automated_export_adversarial_atomicity_and_input_boundaries`

   Exit 0: **14 passed**, one third-party warning, 3.34 seconds.

4. Fresh independent mixed-role TestClient probe executed through
   `uv run python -` using a temporary database and
   `WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST` only.

   Exit 0 result:
   `{'create_brief': 303, 'create_shortlist': 303, 'roles': ['analyst', 'scout'], 'policy_shortlist_read': True, 'shortlist_get': 404, 'marker_disclosed': False}`.

## Findings

### P0

None.

### P1

None.

### P2-01 — Scout role presence still overrides explicit shortlist-read grants

Evidence: `R1AuthorizationPolicy.authorize` correctly unions every role's grant set at
`src/scouting/policy/r1.py:393-407`. In contrast, `can_read_entry` selects only
`shortlist.read_assigned` whenever the principal has the scout role at
`src/scouting/web/w08.py:1173-1186`; it never tries an independently applicable
`shortlist.read` grant. `shortlist_detail` repeats the role-presence override at
`src/scouting/web/w08.py:1368-1383`: it checks `shortlist.read` only when the scout role
is absent and otherwise requires at least one currently assigned visible entry.
The service has an analogous action-selection branch for non-special transitions at
`src/scouting/workflow/r1.py:803-814`, choosing the analyst-owned action whenever the
analyst role is present rather than evaluating all explicit grants.

Preconditions: a valid multi-role account containing scout plus analyst or approver.
The reproduced case used an analyst+scout who created and owned an approved TEAM brief,
replay link, and empty shortlist. The policy explicitly returned true for that
principal's `shortlist.read`, but `GET /w08/shortlists/{id}` returned 404 solely because
the account also had the scout role. Once unassigned entries exist, the same branch
also removes them from that principal's queue and direct entry routes. An
analyst+approver non-owner can likewise lose an approver transition grant when the
service selects `shortlist_entry.transition_owned` based only on analyst presence.

Impact: this does not disclose another object or broaden privilege; it denies an
explicitly granted workflow capability and makes legitimate multi-role use internally
inconsistent. It is the same class of composition defect as R2 P2, beyond the brief
route corrected in 04P.

Required correction: use union semantics at every route/service action choice. For
shortlist/entry reads, honour an applicable `shortlist.read` grant first, then fall
back to `shortlist.read_assigned` with current assignment. For transitions, accept a
target only when at least one explicit applicable grant for that target and resource
succeeds; do not select one action from role presence. Add route and service witnesses
for analyst+scout owner TEAM and OWNER_ONLY access, approver+scout TEAM access,
analyst+approver non-owner transition behaviour, scout-only assigned/unassigned and
former-assignee denial, and cross-tenant denial. The fix must not broaden scout-only
access or replay-link assignment rules.

### P3

None.

## R2 finding outcomes

- **R2 P1-01 scout pre-approval queue/detail disclosure: CLOSED.** The shared
  `can_read_brief` predicate honours `role_brief.read`, otherwise requires both an
  approved latest revision and `role_brief.read_approved`. Fresh focused execution
  proves draft, submitted, and rejected TEAM markers absent from a scout queue and
  generic 404 on detail, while approved TEAM metadata is visible.
- **R2 P1-02 unassigned replay/candidate disclosure: CLOSED.** Brief visibility and
  link visibility are separate. `can_read_retrieval_link` requires creator ownership,
  approver read, or an exact-link current latest assignment plus
  `retrieval_link.read_assigned`. Unassigned and former-assigned scouts receive no link
  ID, projection, query digest, ordered candidate or selectable candidate control;
  the current assignee receives them, and reassignment removes the former assignee.
  Cross-tenant and non-owner `OWNER_ONLY` cases deny generically.
- **R2 P2-01 mixed analyst+scout own-draft detail: CLOSED for the exact reported
  path.** The mixed principal receives its own draft detail through the analyst
  `role_brief.read` grant. P2-01 above records the remaining equivalent override on
  shortlist/entry routes and transition action selection.

The explicit analyst `retrieval_link.read_owned` grant is present in both retained
YAML and the exact code allowlist. `_OWNED_ACTIONS` explicitly enumerates all eight
retained owner-scoped actions rather than inferring ownership from a suffix. TEAM
still requires an action grant; OWNER_ONLY still requires owner/current assignment.
Those policy-level semantics pass. The remaining defect is composition above that
policy layer.

## Earlier R1 P1 closure outcomes

- **Server-controlled evidence origin: CLOSED.** `create_w08_app` requires the
  keyword-only origin and captures it in application state/route composition. Form
  and header input cannot select it. Synthetic/browser apps use
  `synthetic_automated_test`; the local service/study runtime uses
  `human_entered_local`. Creation/amendment, database, render, audit/export origin
  witnesses pass. Automated records are never counted as participant evidence.
- **Persisted pack byte tamper denial: CLOSED.** The single persisted-pack verifier
  checks guarded identity, bytes/digest, strict UTF-8/JSON, canonical encoding,
  classification and fixed claim/model/applicability fields. Inventory, read,
  idempotent create and revoke verify before success. Isolated byte and ledger
  mutations fail closed with export/revocation/audit/file baselines unchanged; retry
  after removing the injected fault succeeds exactly once.
- **Receipt identity/context/time binding: CLOSED.** The canonical receipt digest now
  binds tenant ID, receipt ID, predecessor digest, event digest, sequence, event ID and
  recorded-at. Verification strictly parses and compares each field plus event/tenant
  linkage. Same-format receipt-ID, timestamp, and tenant mutations fail verification
  before the next audited action and preserve row baselines.

## Control-area outcomes

- **Authentication/session/CSRF: PASS.** Salted scrypt, dummy unknown-user work,
  HMAC-stored tokens, positive TTL, expiry, revocation, rotation/fixation resistance,
  SameSite/HttpOnly session cookie, mutation CSRF, disabled accounts, unknown action,
  role escalation and generic denial witnesses pass. The local cookie is deliberately
  not `Secure` because this authorised runtime is loopback HTTP only.
- **Object authorisation/confidentiality: PASS for disclosure boundaries; FAIL for
  complete composition.** IDOR, tenant, OWNER_ONLY, team grants, private observation,
  current/former assignment, replay/candidate allowlist and privileged export
  non-disclosure pass. P2-01 is a fail-closed availability/composition defect.
- **Export/confidentiality: PASS.** Export creation is limited to explicit analyst or
  approver authority and matching objects. Inventory/read/revoke are tenant/object
  scoped, byte-verified, classification-bound, local-path guarded and generic on
  denial. Private content is filtered by authorship/current assignment/TEAM visibility.
- **Audit/concurrency/recovery: PASS.** Append-only triggers, seven-field receipt
  binding, orphan/digest detection, nested transactional savepoints, optimistic locks,
  idempotent retries and injected storage/audit/SQL failure baselines pass.
- **Input/path/file handling: PASS.** URL-encoded media type only, 64 KiB streaming
  bound before retention, strict UTF-8, no multipart/file upload, local relative
  evidence references, traversal/symlink denial and non-echoing errors remain covered.
- **Browser/accessibility: PASS for automated mechanics.** Five real Chromium tests
  cover the complete role journey, loopback-only requests, keyboard skip/focus,
  landmarks/labels/headings/table semantics, recovery affordances and body-width
  checks at 1440, 390 and 320 pixels. The 320-pixel history table remains an internal
  scroll container rather than clipping evidence. This is not a human usability result.
- **W06 claim/protected boundary: PASS.** UI, reports and exports retain `NO_GO`, sole
  reason `MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`,
  `synthetic_development_only`, `LIMITED`, and `no_recommendation_evidence`. No
  relevance, recommendation, transfer, recruitment-success, price/value or
  production-readiness claim was found. Protected expected outputs were not accessed.

## Representative-user evidence

Synthetic automation is not representative-user evidence. The W08 directory contains
the protocol and template-only capture/summary instruments but no completed capture
record. Exact status:

- required genuine authorised reviewed representative-user records: **5**
- present genuine authorised reviewed representative-user records: **0**
- present participant results: **0**
- synthetic personas counted: **0**
- G-W08/G4 human gate: **PENDING**

Five distinct qualifying, authorised and consenting people must still cover analyst,
scout and approver/meeting responsibilities, complete T1-T7 unaided, avoid unsupported
inference, and have de-identified checksummed captures and summary independently
reviewed. Automation cannot be converted into that evidence.

## Required rework and disposition

**FAIL.** Correct P2-01 across shortlist/entry read and transition action selection,
add the mixed-role/adversarial witnesses described above, rerun the complete focused
suite and Bandit, and obtain a fresh independent review. There are no open P0/P1
security/confidentiality/audit/accessibility/evidence-honesty findings, but this R3
packet cannot PASS while its explicit all-actions union invariant is false. Separately,
W08 cannot be verified/checkpointed/closed until the genuine-user gate reaches 5/5.

## Scope confirmation

- Changed path: `reports/reviews/W08/w08-independent-security-review-R3.md` only.
- No Git command or Git-invoking verifier/script was run.
- No product, test, config, migration, orchestration, dependency or lockfile edit was made.
- No protected W06 expected output or protected fixture was accessed or reconstructed.
- No external network, provider, identity, model, service or public endpoint was used.
- No participant evidence was created, inferred or represented.
- No delegation was used.

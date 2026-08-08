# W08 independent security and confidentiality review R4

## Review identity and verdict

- Review ID: `W08-MULTIROLE-AUTHZ-REVIEW-05D-R1`
- Reviewer role: fresh independent security/confidentiality reviewer; report-only
- Verdict: **PASS**
- Severity totals: **P0 0 / P1 0 / P2 0 / P3 0**
- Representative-user gate: **PENDING — 0/5 genuine authorised reviewed records**

The narrowed all-actions multi-role union invariant now holds. The exact R3
policy-true/route-404 case independently reproduces as policy true and route 200 for
the legitimate analyst+scout owner. The positive and negative read/transition
matrices pass without exposing unassigned, former-assigned, private or foreign-tenant
resources. The complete focused suite passes with 72 tests and Bandit reports no
finding. No open security, confidentiality, authorisation, audit, accessibility or
evidence-honesty finding remains in this review scope.

This PASS is not a W08 phase closure. Synthetic automation is mechanics evidence
only. The separate G-W08/G4 representative-user gate remains pending at 0/5 and must
not be inferred from this review.

## Reviewed scope

I read `AGENTS.md`, both complete controlling HTML plans, the R3 review, the 04P and
04Q correction packets and returns, and the return template. The exact control and
prior-evidence paths were:

- `orchestration/task_packets/W08-MULTIROLE-AUTHZ-REVIEW-05D-R1.yaml`
- `reports/reviews/W08/w08-independent-security-review-R3.md`
- `orchestration/task_packets/W08-MULTIROLE-SHORTLIST-AUTHZ-04Q-R1.yaml`
- `reports/reviews/W08/returns/W08-MULTIROLE-SHORTLIST-AUTHZ-04Q-R1.md`
- `orchestration/task_packets/W08-WEB-SCOUT-BRIEF-AUTHZ-04P-R1.yaml`
- `reports/reviews/W08/returns/W08-WEB-SCOUT-BRIEF-AUTHZ-04P-R1.md`
- `orchestration/templates/subagent_return.md`

Exact implementation/configuration/schema paths reviewed:

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
- `reports/verification/W08/limitations.md`
- `reports/verification/W08/protected-output-boundary.md`
- `reports/verification/W08/representative-user-evidence-status.md`

Protected W06 expected outputs, `tests/fixtures/synthetic/protected/**`, and
`reports/evaluation/W06/**` were not opened, searched, reconstructed or inferred.

## Commands and results

1. Independent exact R3 TestClient probe through `uv run python -`, using a temporary
   database and `WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST` only.

   Exit 0 result:

   ```text
   {'policy_TEAM': True, 'mixed_route_TEAM': 200,
    'scout_route_TEAM': 404, 'approver_scout_route_TEAM': 200,
    'policy_OWNER_ONLY': True, 'mixed_route_OWNER_ONLY': 200,
    'scout_route_OWNER_ONLY': 404,
    'approver_scout_route_OWNER_ONLY': 404,
    'foreign_route_TEAM': 404, 'scout_marker_disclosed': False}
   ```

2. Independent focused union/boundary matrix:

   `uv run pytest -q tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_scout_brief_and_replay_authorization_matrix tests/security/test_w08_workflow_access.py::test_ordinary_transition_uses_any_applicable_explicit_grant tests/security/test_w08_workflow_access.py::test_special_transition_targets_keep_their_sole_grant tests/integration/test_w08_workflow.py::test_synthetic_automated_role_brief_to_observation_journey`

   Exit 0: **4 passed**, one third-party Starlette TestClient deprecation warning,
   1.17 seconds.

3. Complete focused pytest command exactly as specified:

   `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/security/test_w08_auth_audit.py tests/security/test_w08_workflow_access.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/integration/test_w08_study_harness.py tests/e2e/test_w08_local_workflow_playwright.py`

   Exit 0: **72 passed**, one third-party Starlette TestClient deprecation warning,
   26.73 seconds.

4. Packet Bandit command:

   `uv run bandit -q -r src/scouting/policy/r1.py src/scouting/audit/ledger.py src/scouting/workflow/r1.py src/scouting/observations/r1.py src/scouting/operations/evidence_export.py src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py`

   The first sandboxed attempt exited 2 before scanning because access to uv cache
   metadata at `/Users/adrian/.cache/uv/sdists-v9/.git` was denied. No Git executable
   or Git command was invoked and no repository file was changed. The identical
   read-only command was rerun through the approved `uv run bandit` boundary and
   exited 0 with no findings.

## Independent multi-role matrices

### Read union

| Principal/resource | Result and grant |
| --- | --- |
| Analyst+scout owner, empty TEAM shortlist | 200 through explicit `shortlist.read` |
| Analyst+scout owner, empty OWNER_ONLY shortlist | 200 through owner-applicable `shortlist.read` |
| Approver+scout, TEAM shortlist without assignment | 200 through explicit `shortlist.read` |
| Approver+scout, non-owned OWNER_ONLY shortlist | generic 404 |
| Scout only, exact current assigned entry | shortlist and entry 200 through `shortlist.read_assigned` |
| Scout only, unassigned entry | generic 404; no replay/candidate projection |
| Scout only, former assignment after clearance/reassignment | generic 404; replay/candidate projection removed |
| Scout only, non-owned private object | generic 404; marker absent |
| Foreign tenant using the same object identifiers | brief, shortlist and entry generic 404 |

The exact R3 defect is closed at `src/scouting/web/w08.py:1175-1199`: the shared
entry/shortlist decisions first evaluate the independently applicable
`shortlist.read` grant and then the exact assigned-entry fallback. The shortlist
route applies that decision before rendering at `src/scouting/web/w08.py:1371-1374`,
while replay-link projection remains independently assignment-scoped at
`src/scouting/web/w08.py:274-325`.

### Transition union and special-target isolation

| Target/principal | Result and grant |
| --- | --- |
| Ordinary target, analyst owner | allow through `shortlist_entry.transition_owned` |
| Ordinary target, approver | allow through `shortlist_entry.transition` |
| Ordinary target, analyst+approver non-owner | allow through approver `transition`; inapplicable analyst owner grant does not suppress it |
| Ordinary target, analyst non-owner only | deny |
| `shortlist` | only `shortlist_entry.approve` applies |
| `hold` | only `shortlist_entry.hold` applies |
| `rejected` | only `shortlist_entry.reject_with_reason` applies |

`entry_transition_actions` defines the sole target mapping at
`src/scouting/workflow/r1.py:77-90`. Service enforcement applies `any` over those
actions against one exact resource at `src/scouting/workflow/r1.py:510-520` and
`src/scouting/workflow/r1.py:806-825`. The rendered target list calls the same helper
and evaluates the same union at `src/scouting/web/w08.py:1201-1227`; presentation and
service action semantics therefore agree.

## Role-presence selector inspection

I inspected the material W08 service, web, observation, export and template paths for
another branch that selects or suppresses an action merely because a role is present.
No residual composition defect was found.

- Policy grants are unioned across every principal role at
  `src/scouting/policy/r1.py:405-427`; owner, assignment, visibility and tenant checks
  are then applied to the exact resource.
- Brief read and replay-link read independently try each applicable explicit grant at
  `src/scouting/web/w08.py:255-325`; scout presence does not override analyst or
  approver access.
- Shortlist/entry read and transitions use the shared union decisions described
  above.
- Template role checks expose forms or navigation for actions granted only to that
  named role; route/service authorization remains authoritative. Their state branches
  are mutually exclusive lifecycle states and do not suppress a second applicable
  grant.
- The direct admin check protects the admin-only audit route. Export inventory allows
  analyst-owned packs and intentionally lets an explicit approver role see the
  tenant-scoped inventory; creation/read/revoke still use policy and exporter object
  checks. Neither branch creates a multi-role denial or disclosure.

## R3 and earlier closure outcomes

- **R3 P2-01 shortlist/entry role-presence override: CLOSED.** The independent probe
  changed the exact policy-true analyst+scout owner outcome from the recorded R3 404
  to 200 for TEAM and OWNER_ONLY. Approver+scout TEAM and analyst+approver non-owner
  transition witnesses pass. Scout-only current/unassigned/former, OWNER_ONLY and
  foreign-tenant boundaries remain exact.
- **R2 P1-01 scout pre-approval brief disclosure: CLOSED.** Draft, submitted and
  rejected TEAM brief markers remain absent from scout queue/detail; approved brief
  metadata alone is readable.
- **R2 P1-02 unassigned replay/candidate disclosure: CLOSED.** Exact-link current
  assignment is still required. Unassigned/former scouts receive no link, projection,
  digest, candidate marker or control; current assignees do; reassignment removes the
  former assignee.
- **R2 P2-01 mixed analyst+scout own draft: CLOSED.** The owner reads its draft through
  the analyst `role_brief.read` grant.
- **R1 server-controlled evidence origin: CLOSED.** Origin remains application-state
  controlled; request form/header input cannot manufacture participant evidence.
- **R1 persisted-pack byte tamper denial: CLOSED.** Strict persisted-pack byte,
  canonical payload, identity, classification and fixed-claim verification remains
  fail-closed before inventory/read/idempotent creation/revocation success.
- **R1 receipt identity/context/time binding: CLOSED.** Receipt verification remains
  bound to tenant, receipt/predecessor/event digests, sequence, event ID and recorded
  time before the next audited action.

## Control-area outcomes

- **Authentication/session/CSRF: PASS.** Password hashing, dummy unknown-user work,
  HMAC token storage, TTL/expiry/revocation/rotation, fixation resistance, cookie
  controls, mutation CSRF, disabled-account denial, unknown-action denial, role
  escalation denial and generic errors pass. The local cookie remains intentionally
  non-`Secure` for the authorised loopback-HTTP-only runtime.
- **Object authorisation/confidentiality: PASS.** The all-actions union invariant now
  holds without weakening tenant, IDOR, owner, current-assignment, private observation,
  replay/candidate or generic-denial boundaries.
- **Export/confidentiality: PASS.** Create/read/inventory/revoke remain explicitly
  authorised, tenant/object scoped, local-path guarded, byte verified,
  classification-bound and generic on denial; non-visible private content is absent.
- **Audit/concurrency/recovery: PASS.** Append-only triggers, complete receipt binding,
  orphan/digest detection, nested savepoints, optimistic locks, idempotent retry and
  injected storage/audit/SQL failure atomicity all pass.
- **Input/path/file handling: PASS.** Bounded URL-encoded input, strict UTF-8, local
  relative references, traversal/symlink denial and non-echoing failure behaviour pass.
- **Browser/accessibility: PASS for automated mechanics.** The five real-Chromium
  journeys in the focused suite cover loopback-only requests, full role workflow,
  keyboard skip/focus, landmarks/labels/headings/table semantics, recovery controls
  and body-width checks at 1440, 390 and 320 pixels. The narrow history table remains
  an internal scroll region. This is not a human usability result.
- **W06 claim/protected boundary: PASS.** Retained UI/report/export wording remains
  `NO_GO`, sole reason `MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`,
  `synthetic_development_only`, `LIMITED`, and `no_recommendation_evidence`. No
  relevance, recommendation, transfer, recruitment-success, price/value or
  production-readiness claim was found. Protected expected outputs were not accessed.

## Findings

### P0

None.

### P1

None.

### P2

None.

### P3

None.

## Representative-user evidence

The repository retains a protocol and template-only capture/summary instruments, not
participant results. Exact status:

- required genuine authorised reviewed representative-user records: **5**
- present genuine authorised reviewed representative-user records: **0**
- present participant results: **0**
- synthetic personas counted: **0**
- G-W08/G4 human gate: **PENDING**

No participant evidence was created, inferred, reconstructed or represented in this
review. Five distinct qualifying, authorised and consenting people must still cover
analyst, scout and approver/meeting responsibilities, pass T1-T7 unaided without an
unsupported inference, and have de-identified checksummed captures and summary
independently reviewed.

## Disposition

**PASS.** Zero open P0/P1/P2/P3 security, confidentiality, authorisation, audit,
accessibility or evidence-honesty findings remain in the narrowed review. No security
rework is required. Master reproduction/acceptance remains required, and W08 must not
be verified, checkpointed or closed until the separate genuine-user gate reaches 5/5.

## Scope confirmation

- Changed path: `reports/reviews/W08/w08-independent-security-review-R4.md` only.
- No Git command or Git-invoking verifier/script was run.
- No product, test, config, migration, orchestration, dependency or lockfile edit was made.
- No protected W06 expected output or protected fixture was accessed or reconstructed.
- No external network, provider, identity, model, service or public endpoint was used.
- No participant evidence was created, inferred or represented.
- No delegation was used.

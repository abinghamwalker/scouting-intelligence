# W08 independent security review R2

- Review ID: `W08-INDEPENDENT-SECURITY-05-R2`
- Reviewer role: independent reviewer (`gpt-5.6-sol`, medium)
- Verdict: **FAIL**
- Severity totals: **P0 0 / P1 2 / P2 1 / P3 0**
- Human gate: **PENDING — 0/5 genuine representative-user records**

This is a fresh independent review of the corrected W08 implementation. The three
R1 P1 corrections are closed by code inspection and independent focused tests, but
fresh adversarial TestClient probes found two separate scout disclosure paths and
one mixed-role authorisation-composition defect. The P1 findings block W08 security
acceptance. Passing automated tests are mechanics evidence only and are not
representative-user evidence.

## Scope reviewed

I read every `read_first` item in
`orchestration/task_packets/W08-INDEPENDENT-SECURITY-05-R2.yaml`, including the two
controlling documents, the R1 review and correction returns, policies, migration,
contracts, policy/session/audit/workflow/observation/export/web/study code, all W08
templates and CSS, the complete named contract/security/integration/E2E tests, and
the retained W08 study and verification reports. I also inspected the correction
tests and independently exercised the affected routes and persisted evidence.

The reviewed implementation paths were:

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
- `apps/web/templates/w08/*.html`
- `apps/web/static/w08/app.css`
- every test and retained report named by the R2 packet

## Independent checks

The first attempted `uv run` probe exited 2 because the sandbox denied access to a
uv cache path. It made no repository change. The same read-only checks were then
run under the approved `uv run` execution boundary.

1. Targeted R1-correction regression selection:

   `uv run pytest -q tests/security/test_w08_auth_audit.py::test_receipt_identity_context_and_time_tampering_fail_before_next_action tests/integration/test_w08_evidence_export.py::test_persisted_pack_faults_block_read_idempotency_and_revoke_atomically tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_shortlist_assignment_observation_and_conflict tests/integration/test_w08_study_harness.py::test_human_mode_route_origin_is_server_selected_mechanics_only tests/security/test_w08_web_security.py::test_synthetic_automated_export_adversarial_atomicity_and_input_boundaries`

   Exit 0: **13 passed**, one Starlette deprecation warning, 2.73s.

2. Complete focused suite exactly as specified by the R2 packet:

   `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/security/test_w08_auth_audit.py tests/security/test_w08_workflow_access.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/integration/test_w08_study_harness.py tests/e2e/test_w08_local_workflow_playwright.py`

   Exit 0: **69 passed**, one Starlette deprecation warning, 26.14s.

3. Packet-specified Bandit scan:

   `uv run bandit -q -r src/scouting/policy/r1.py src/scouting/audit/ledger.py src/scouting/workflow/r1.py src/scouting/observations/r1.py src/scouting/operations/evidence_export.py src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py`

   Exit 0: no findings.

4. Fresh draft-brief scout probe, using a temporary database and local TestClient:

   - analyst created a team-visible draft containing a unique marker;
   - an otherwise unassigned same-tenant scout requested `/w08/queue` and the exact
     brief detail URL.

   Exit 0 result:
   `{'queue_status': 200, 'draft_marker_in_queue': True, 'detail_status': 404}`.

5. Fresh approved-link scout probe, using a temporary database and local
   TestClient:

   - analyst created/submitted an approved brief and created its replay link;
   - no shortlist or assignment was created for the scout;
   - the otherwise unassigned same-tenant scout requested the brief detail URL.

   Exit 0 result:
   `{'detail_status': 200, 'replay_heading': True, 'ordered_candidates': True, 'unassigned_marker': True}`.

6. Fresh mixed analyst+scout probe, using a temporary database and local
   TestClient:

   - a local account with both roles created its own draft successfully;
   - its queue and direct detail were requested in the same authenticated session.

   Exit 0 result:
   `{'create_status': 303, 'queue_status': 200, 'own_draft_in_queue': True, 'own_draft_detail_status': 404}`.
   The queue visibility is only a consequence of P1-01; the direct 404 proves the
   independent mixed-role composition defect.

All custom probes used `WorkflowEvidenceOrigin.SYNTHETIC_AUTOMATED_TEST`, local
temporary files and no network or external service.

## R1 P1 closure outcomes

### Evidence-origin authority — CLOSED

The app factory now requires a keyword-only server-selected `evidence_origin`; it
is retained in app state and captured by the route composition. Synthetic app and
browser witnesses select `synthetic_automated_test`, while the local service/study
harness selects `human_entered_local`. Hostile form/header values cannot select or
override the origin. Create and amendment paths persist the server-selected value,
and the DB/render/audit/export witnesses retain it. No automated origin is counted
as participant evidence.

### Persisted evidence-pack byte tampering — CLOSED

`verify_persisted_pack` verifies storage identity, bytes, SHA-256, strict UTF-8 and
JSON decoding, canonical serialization, classification, claim boundary and
model/applicability fields. Inventory and revocation invoke verification before
their success actions. The isolated byte- and ledger-tamper matrices deny
inventory/read/idempotent create/revoke atomically and preserve the expected audit
and revocation state.

### Audit-receipt identity/context/time binding — CLOSED

The receipt digest now binds tenant ID, receipt ID, predecessor digest, event
digest, sequence, event ID and recorded-at. Verification selects and strictly
parses those fields. Independent regression witnesses detect same-format UUID,
tenant and timestamp mutations before the next privileged action.

## Findings

### P0

None.

### P1-01 — An unassigned scout can enumerate unapproved team brief metadata

Evidence: `src/scouting/web/w08.py:388-400` filters queue briefs by the scout action
`role_brief.read_approved`, but does not check that the latest revision is actually
approved. The policy declaration at
`configs/policies/w08-authorization.yaml:23-27` names the limited grant explicitly.
The detail route correctly applies the missing status condition at
`src/scouting/web/w08.py:820-831`, which is why the same object returns generic 404
there while its title, identifier and status are visible in the queue.

Preconditions: any valid same-tenant scout session and a team-visible draft,
submitted or rejected brief. The scout need not own the brief or have any shortlist
assignment.

Impact: confidential pre-approval role requirements, titles, lifecycle state and
object identifiers are disclosed to a role whose retained permission is limited to
approved briefs. This is a direct authorisation/confidentiality boundary failure.

Required correction: before policy evaluation or rendering, restrict the scout
queue projection to rows whose latest status is `approved`. Add adversarial route
tests showing draft, submitted and rejected team briefs are absent, an approved
brief is present, and unknown/foreign/private objects remain indistinguishable.

### P1-02 — An unassigned scout can read replay-link and ordered-candidate data

Evidence: the scout policy grants `retrieval_link.read_assigned` at
`configs/policies/w08-authorization.yaml:27`. After authorising the approved brief,
`src/scouting/web/w08.py:832-856` loads and renders every replay link and its exact
projection without any `retrieval_link.read_assigned` decision or resource
assignment check. The independent probe received 200 and saw the replay heading,
unique brief marker and ordered candidate content despite no shortlist, entry or
scout assignment.

Preconditions: any valid same-tenant scout session and any team-visible approved
brief with a replay link. No shortlist assignment is required.

Impact: replay identifiers, query digest/context, lineage/model/index/taxonomy/data
versions and ordered synthetic candidate IDs are disclosed beyond the explicit
assigned-only grant. Fixed limitation wording does not repair the object-level
authorisation failure.

Required correction: do not render a replay link to a scout unless the link is
connected through a shortlist/entry that is currently assigned to that scout, and
authorise the corresponding resource with `retrieval_link.read_assigned`. Preserve
analyst/approver access according to their explicit grants. Add independent
positive/negative route tests for unassigned, assigned, reassigned/former-assignee,
cross-tenant and private/team cases, including the absence of link/projection data
from both response body and selectable controls.

### P2-01 — Mixed analyst+scout accounts cannot read their own draft brief detail

Evidence: `R1AuthorizationPolicy.authorize` unions the grants of all principal
roles (`src/scouting/policy/r1.py:392-407`), and local accounts support multiple
roles. The queue and detail composition instead selects
`role_brief.read_approved` whenever `LocalRole.SCOUT` is present
(`src/scouting/web/w08.py:393-399` and `src/scouting/web/w08.py:820-829`), even when
the same principal also has the analyst `role_brief.read` grant and owns the
object. A mixed account can create its draft but gets 404 for its own detail.

Preconditions: a valid local account with both analyst and scout roles creates or
owns a non-approved brief.

Impact: an authorised multi-role workflow is internally inconsistent and the user
cannot review or submit the object they just created. Applying the narrow P1-01
status fix alone would also remove the accidental queue visibility and leave the
created draft unreachable through both routes.

Required correction: derive the permitted action from all applicable grants and
object context rather than treating presence of the scout role as an override.
Retain the scout-only approved restriction, while allowing a genuine analyst grant
to operate under its existing tenant/ownership/visibility rules. Add mixed-role
route tests for own and non-owned draft/approved briefs and ensure role composition
does not broaden assigned-only replay-link access.

### P3

None.

## Control outcomes

- **Authentication/session/CSRF: PASS.** Local password handling, generic login
  denial, expiry, revocation, session rotation/fixation resistance, SameSite/
  HttpOnly cookies, mutation CSRF and local-only composition passed the reviewed
  tests. No role self-escalation path was found.
- **Object authorisation/confidentiality: FAIL.** Tenant and private observation
  boundaries, assignment checks for shortlist entries and generic unknown-object
  handling passed, but P1-01 and P1-02 disclose brief/replay content beyond the
  scout grants. P2-01 breaks declared multi-role semantics.
- **Export/confidentiality boundary: PASS for the export subsystem.** Privileged
  export creation, revocation, canonical byte verification, tamper denial,
  classification/checksum/limitations and private-observation exclusion passed.
  The overall confidentiality verdict remains FAIL because of the web disclosures.
- **Audit/concurrency/recovery: PASS.** Append-only receipts, full identity/context/
  time binding, tamper detection, optimistic conflicts, atomic denials, recoverable
  export failure and revocation checks passed.
- **Input/file/replay controls: PASS except P1-02.** Local-root/path/symlink,
  malformed input, candidate allowlist and persisted projection integrity checks
  passed. Replay integrity is sound, but replay-link visibility is not.
- **Browser/accessibility: PASS for automated evidence.** The complete E2E subset
  passed keyboard navigation, visible focus, landmarks/labels and responsive
  layouts at 1440px, 390px and 320px. This is automated mechanics evidence, not a
  moderated usability result.
- **Evidence honesty and W06 boundary: PASS.** Retained wording remains `NO_GO`,
  sole reason `MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`,
  `synthetic_development_only`, `LIMITED`, and `no_recommendation_evidence`.
  Workflow completion is not represented as relevance, recommendation,
  transferability, price/value, recruitment-success or production evidence.
- **Protected outputs: PASS.** I did not open, inspect or reconstruct protected W06
  expected outputs or `reports/evaluation/W06/**`.

## Representative-user gate

There are **0/5** genuine authorised reviewed representative-user records and zero
completed moderated-study results. The protocol and capture/summary templates are
complete, but automation and synthetic personas cannot satisfy the gate. After the
security findings are corrected and freshly independently reviewed, five distinct
authorised consenting representative users must collectively cover analyst, scout
and approver roles; each must complete T1–T7 unaided with no unsupported inference
or unresolved P0/P1, and the checksummed captures and synthesis must be
independently reviewed.

## Final disposition and mandatory return

**FAIL.** Correct P1-01 and P1-02, correct P2-01, reproduce focused checks, and
obtain a fresh independent security review. W08 must not be marked VERIFIED,
accepted or closed while either P1 remains. Even after technical acceptance, the
separate 0/5 representative-user gate remains pending.

I performed no Git operation, made no product/test/config/orchestration/dependency
edit, accessed no protected W06 output, contacted no external service, and created
or inferred no participant evidence. The only repository mutation is this review
report at the packet-authorised path.

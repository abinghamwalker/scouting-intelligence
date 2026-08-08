# W08 independent security review — R1

## Review identity and verdict

- Review ID: `W08-INDEPENDENT-SECURITY-05-R1`
- Reviewer role: independent reviewer; this reviewer produced none of the W08 implementation.
- Verdict: **FAIL**
- P0 findings: 0
- P1 findings: 3
- P2 findings: 0
- P3 findings: 0

The focused automated suite and Bandit scan pass, but passing automation does not
overcome the three code/evidence-grounded integrity findings below. The evidence-origin
finding is also an evidence-honesty failure. Under the packet's acceptance rule, these
P1 findings require bounded correction and a fresh independent review.

## Reviewed scope

I read `AGENTS.md`, the complete W08/P4 controlling sections, every `read_first` path
in `orchestration/task_packets/W08-INDEPENDENT-SECURITY-05-R1.yaml`, and the retained
W08 verification reports that were present at review time. Protected W06 expected
outputs and `reports/evaluation/W06/**` were not accessed.

Exact implementation/configuration paths reviewed:

- `migrations/versions/0002_w08_workflow.sql`
- `configs/policies/w08-authorization.yaml`
- `configs/policies/w08-export.yaml`
- `src/scouting/contracts/workflow.py`
- `src/scouting/contracts/audit.py`
- `src/scouting/policy/r1.py`
- `src/scouting/audit/ledger.py`
- `src/scouting/workflow/r1.py`
- `src/scouting/observations/r1.py`
- `src/scouting/operations/evidence_export.py`
- `src/scouting/web/w08.py`
- `scripts/run_w08_study.py`
- `apps/web/templates/w08/base.html`
- `apps/web/templates/w08/brief.html`
- `apps/web/templates/w08/entry.html`
- `apps/web/templates/w08/shortlist.html`
- `apps/web/templates/w08/audit.html`
- `apps/web/templates/w08/export.html`
- `apps/web/templates/w08/exports.html`
- `apps/web/templates/w08/error.html`
- `apps/web/templates/w08/landing.html`
- `apps/web/templates/w08/queue.html`
- `apps/web/static/w08/app.css`
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

Exact implementation packet paths reviewed:

- `orchestration/task_packets/W08-AUTH-AUDIT-01-R1.yaml`
- `orchestration/task_packets/W08-AUTH-POLICY-INTEGRITY-01B-R1.yaml`
- `orchestration/task_packets/W08-WORKFLOW-02-R1.yaml`
- `orchestration/task_packets/W08-WORKFLOW-02-R2.yaml`
- `orchestration/task_packets/W08-WORKFLOW-INTEGRITY-02B-R1.yaml`
- `orchestration/task_packets/W08-WORKFLOW-INTEGRITY-02B-R2.yaml`
- `orchestration/task_packets/W08-EXPORT-03-R1.yaml`
- `orchestration/task_packets/W08-EXPORT-INTEGRITY-03B-R1.yaml`
- `orchestration/task_packets/W08-EXPORT-INTEGRITY-03B-R2.yaml`
- `orchestration/task_packets/W08-AUDIT-EXPORT-TAMPER-05A-R1.yaml`
- `orchestration/task_packets/W08-REPLAY-CONTRACT-02C-R1.yaml`
- `orchestration/task_packets/W08-WEB-E2E-04-R1.yaml`
- `orchestration/task_packets/W08-WEB-E2E-04-R2.yaml`
- `orchestration/task_packets/W08-WEB-WORKFLOW-04A-R2.yaml`
- `orchestration/task_packets/W08-WEB-BRIEF-04D-R2.yaml`
- `orchestration/task_packets/W08-WEB-BRIEF-HISTORY-04E-R2.yaml`
- `orchestration/task_packets/W08-WEB-BRIEF-WITNESS-04G-R1.yaml`
- `orchestration/task_packets/W08-WEB-REPLAY-GUARD-04F-R1.yaml`
- `orchestration/task_packets/W08-WEB-REPLAY-GUARD-04F-R2.yaml`
- `orchestration/task_packets/W08-WEB-EXPORT-04C-R1.yaml`
- `orchestration/task_packets/W08-WEB-EXPORT-04C-R2.yaml`
- `orchestration/task_packets/W08-WEB-EXPORT-UI-04I-R2.yaml`
- `orchestration/task_packets/W08-WEB-EXPORT-JOURNEY-WITNESS-04L-R2.yaml`
- `orchestration/task_packets/W08-WEB-EXPORT-SECURITY-04J-R1.yaml`
- `orchestration/task_packets/W08-BROWSER-A11Y-04B-R1.yaml`
- `orchestration/task_packets/W08-BROWSER-A11Y-04B-R2.yaml`
- `orchestration/task_packets/W08-BROWSER-OVERFLOW-04M-R1.yaml`
- `orchestration/task_packets/W08-STUDY-HARNESS-07A-R1.yaml`

Their corresponding returns listed in this review packet were also read in full.

## Commands and results

1. `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/security/test_w08_auth_audit.py tests/security/test_w08_workflow_access.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/integration/test_w08_study_harness.py tests/e2e/test_w08_local_workflow_playwright.py`
   - Exit: 0
   - Result: **57 passed**, one third-party Starlette TestClient deprecation warning,
     25.27 seconds.
2. `uv run bandit -q -r src/scouting/policy/r1.py src/scouting/audit/ledger.py src/scouting/workflow/r1.py src/scouting/observations/r1.py src/scouting/operations/evidence_export.py src/scouting/web/w08.py scripts/run_w08_study.py`
   - First sandboxed attempt: exit 2 because the existing uv cache path was not
     readable in the sandbox.
   - Approved local-cache retry: exit 0, no Bandit finding.

Process disclosure: before the master removed it from the packet and clarified that
it was master-owned, I ran the then-listed `uv run python
scripts/verify_local_only.py` once. It exited 1 and internally invoked read-only Git.
I issued no direct Git command and performed no Git mutation. I did not run it again
after the clarification. Its result is not used as the product-security verdict in
this report.

## Findings

### P1 — Synthetic automated scout actions are persisted as human-entered evidence

Evidence:

- `src/scouting/web/w08.py:1566-1581` constructs every web comment with
  `WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL`.
- `src/scouting/web/w08.py:1591-1627` constructs every web scout observation with
  `WorkflowEvidenceOrigin.HUMAN_ENTERED_LOCAL`.
- `tests/e2e/test_w08_local_workflow_playwright.py:98-155` explicitly identifies the
  journey as synthetic automation, then submits an invented synthetic observation and
  amendment through those routes.
- `tests/integration/test_w08_local_workflow_app.py:913-948` submits a value named
  `Synthetic automated observation` and positively asserts that the rendered origin is
  `human_entered_local`.
- `src/scouting/operations/evidence_export.py:554-563` propagates those origin values
  into an evidence pack's `workflow_action_origins`.
- This contradicts `reports/verification/W08/limitations.md:19-21`, which says every
  automated scout observation/action is labelled synthetic, and the controlling rule
  that automated personas and fixtures are not scout or representative-user evidence.

Precondition and impact: any TestClient or Playwright automation that submits the
ordinary W08 comment/observation forms produces attributable records and export
metadata labelled as human-entered. The text may contain the word “Synthetic”, but the
structured provenance claims a human origin. This fabricates the provenance of an
invented scout judgement and makes retained evidence reports materially false.

Required correction: select origin through a server-controlled runtime mode that is
not form-editable. Automated app/test runtimes must write
`SYNTHETIC_AUTOMATED_TEST`; only a genuine moderated-study runtime may write
`HUMAN_ENTERED_LOCAL`. Add database, rendered-history, audit-digest and export-origin
witnesses for both modes, and correct any report that claims the current automation is
already labelled synthetic. Do not infer representative-user participation from the
human-entered mechanical label.

### P1 — Byte tampering remains active in inventory and can be revoked without verification

Evidence:

- The packet requires isolated byte tamper to make read, inventory, create and revoke
  fail closed (`orchestration/task_packets/W08-WEB-EXPORT-SECURITY-04J-R1.yaml:58-70`).
- `src/scouting/web/w08.py:1000-1024` verifies only the audit chain, then renders export
  rows and claimed SHA-256 values directly from SQLite. It does not verify active pack
  bytes.
- `src/scouting/operations/evidence_export.py:335-407` verifies the ledger and database
  row before revocation, but never reads or hashes the evidence-pack bytes.
- `tests/security/test_w08_web_security.py:307-312` proves only that direct read rejects
  altered bytes. At lines 313-318 it then corrupts the audit ledger before the
  inventory/create/revoke matrix at lines 319-331. Those latter denials are caused by
  the malformed ledger, so the test does not establish independent byte-tamper denial
  for inventory or revoke.
- `reports/reviews/W08/returns/W08-WEB-EXPORT-SECURITY-04J-R1.md` describes the combined
  case as if the required all-route byte-tamper invariant were established.

Precondition and impact: if a guarded pack file is altered while its database and
audit rows remain intact, verified read and idempotent recreate reject it, but the
inventory can still present it as active with the persisted checksum, and revoke can
append a valid revocation/audit event over an already-invalid artifact. The UI and
audit history therefore cease to be a fail-closed account of verified export state.

Required correction: route inventory through exporter-owned verified metadata (or
verify every active row's guarded bytes before rendering), and verify immutable bytes
before revocation as required by the retained packet. Split the test into independent
byte-tamper and ledger-corruption cases; for each route, assert status, response
non-disclosure, and exact database/audit/file baselines before introducing any second
fault.

### P1 — Receipt identity and recording time are outside the verified audit digest

Evidence:

- `src/scouting/audit/ledger.py:79-88` computes a receipt digest from predecessor,
  event digest, sequence and audit-event ID only.
- `src/scouting/audit/ledger.py:127-160` generates `audit_receipt_id` and
  `recorded_at`, but neither value participates in the receipt digest.
- `src/scouting/audit/ledger.py:188-236` does not select or validate the stored
  `audit_receipt_id` or `recorded_at` while verifying a chain.
- Both values are normative fields of `AuditReceipt` at
  `src/scouting/contracts/audit.py:79-90`. The implementation and reports describe
  complete receipt verification and database-tamper rejection.

Precondition and impact: after bypassing the SQLite update trigger in an isolated
compromise test (the same adversarial precondition already used by W08 tamper tests),
an attacker can alter a receipt identifier or substitute any recording timestamp and
`AuditLedger.verify` will still pass. The material event and order remain intact, but
the receipt's asserted identity/time are not tamper-evident. That is a P1 audit-
integrity gap under the packet's complete-chain requirement.

Required correction: include all immutable receipt identity/context fields that are
claimed as verified—at minimum receipt ID and recorded-at, with tenant binding—in the
canonical receipt digest, and make `verify` parse and compare them. Add isolated
same-length/valid-format mutations for each field after deliberately removing only the
test database trigger; every mutation must fail closed without new action/receipt
state.

## Outcome by control area

### Authentication and authorisation

The inspected implementation is deny-by-default and binds the retained policy exactly.
Focused tests pass for salted scrypt passwords, dummy unknown-account work, HMAC-token
storage, positive TTL, expiry, revocation, service-level rotation/fixation defence,
CSRF, unknown roles/actions, disabled accounts, tenant separation, owner/current-
assignment rules, admin non-escalation and generic IDOR denial. I found no independent
P0/P1 authentication or object-authorisation bypass.

### Confidentiality and export

Role and tenant export denials, current versus former assignment, author visibility,
private-record filtering, path traversal/symlink rejection, bounded URL-encoded input,
strict UTF-8, no multipart path, idempotency and response non-echo witnesses pass.
Confidentiality mechanics are otherwise sound, but export integrity **fails** because
active inventory and revocation do not independently reject altered pack bytes.

### Audit, concurrency and recovery

Material service mutations use nested savepoints, hash-chained audit events and
optimistic locks. Stale writes, invalid transitions, injected audit/storage/SQL
failures and retry witnesses pass without partial database rows. Existing event-chain
and digest corruption is detected. Audit integrity nevertheless **fails** because
receipt identity/recording time are not bound or checked, and the export revocation
path can extend valid audit state over an unverified pack.

### Browser and accessibility

The five retained real-Chromium tests are part of the 57 passing focused tests. They
exercise the complete local multi-role workflow, loopback-only requests, skip-link and
visible-focus behaviour, labels/landmarks/headings/table semantics, recovery affordance
and 1440/390/320 layouts. The 320-pixel history table remains internally scrollable
without body overflow. I found no independent P0/P1 accessibility defect. These are
synthetic automated browser mechanics only; their current database provenance bug is
the separate P1 evidence-honesty finding above.

### W06 claim and protected-output boundary

Displayed and exported model wording retains `NO_GO`, sole reason
`MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`,
`synthetic_development_only`, `LIMITED` and `no_recommendation_evidence`. I found no
positive relevance, recommendation, transfer, recruitment-success, price/value or
production-ready claim. No protected W06 expected output was opened or reconstructed.

## Representative-user evidence

Synthetic automation is not representative-user evidence. The repository contains
the protocol and template-only instruments, but no participant directory or completed
capture record. Exact status at this review:

- required genuine reviewed representative-user records: 5
- present genuine reviewed representative-user records: **0**
- gate status: **not satisfied**

Even after the three P1 corrections pass fresh independent review, W08 cannot be
verified, accepted, checkpointed or closed until five distinct authorised and
consenting representative users complete T1–T7 as specified and their de-identified
records, mechanical receipts and summary receive independent review.

## Required rework and return conditions

1. Correct server-controlled automated versus genuine-study evidence origin and
   remove the current synthetic-as-human witness/report contradiction.
2. Make byte-tampered pack inventory and revocation independently fail closed and add
   fault-isolated route witnesses.
3. Bind and verify immutable receipt identity/time/tenant metadata and add direct
   tamper witnesses.
4. Re-run the focused functional/security/browser suite and Bandit, then commission a
   fresh independent review by a reviewer who did not perform the corrections.
5. Keep W08 below `VERIFIED`; do not create an acceptance commit/tag and do not begin
   W09 while the findings or five-user gate remain open.

## Scope confirmation

- Product code, tests, configurations, orchestration and dependencies edited: **none**.
- Changed path: `reports/reviews/W08/w08-independent-security-review-R1.md` only.
- Git: no direct Git command and no Git mutation. Process exception disclosed above:
  the formerly packet-listed local-only verifier internally ran read-only Git once
  before the master clarification arrived.
- External/network/provider/model activity: none.
- Protected W06 output access or reconstruction: none.
- Participant/result fabrication: none.
- Delegation: none.

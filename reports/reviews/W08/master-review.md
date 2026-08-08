# W08 master review

Disposition: **AUTOMATED ACCEPT / G-W08A PENDING / G-W08B BLOCKED**

W08's authorised implementation, automated verification, security review, browser
and accessibility review, recovery review and evidence preparation are accepted for
the local mechanics they prove. W08 is not accepted as a phase and G-W08B (legacy
G-W08) does not pass: no genuine representative-user record exists (`0/5`). The
truthful lifecycle state is `MASTER_REVIEW`. The newly authorized G-W08A path is also
pending (`0/1`): it changes progression policy, not the evidence result.

## Integrated scope

The accepted unattended implementation covers local analyst, scout, approver and
admin identities; password and session controls; default-deny role/object policy;
versioned briefs and pinned retrieval replay; shortlist ownership, assignments,
transitions, comments and optimistic concurrency; structured scout observations,
visibility, disagreement, amendments and history; authorised local evidence-pack
export; append-only audit receipts; and the complete local web workflow. The study
harness, protocol, capture template, summary template and morning handoff are ready
for genuine participation.

The implementation is retained in two non-acceptance commits:

- `8d6a7b1b202b83486618d018c7cb1d408fa11e48` — local scouting workflow;
- `b12f9c897a94a618944b080f7b78e92be0b3e1c4` — exact-byte exporter relocation into
  the workflow application layer, preserving all import contracts.

Forty-six bounded task packets and 41 producer returns cover the serial and
path-disjoint work. Product changes span `src/scouting/{policy,workflow,observations,
audit,web}`, the embedded migration/storage surface, `services/api`, W08 templates and
CSS, the local study runner, policies, and contract/integration/security/E2E tests.

## Independent-review disposition

- R1: FAIL, P0 0 / P1 3. Closed server-controlled automated evidence origin,
  persisted-byte tamper enforcement and fully bound audit receipts.
- R2: FAIL, P0 0 / P1 2 / P2 1. Closed scout pre-approval disclosure, unassigned
  replay/candidate disclosure and mixed-role own-draft composition.
- R3: FAIL, P0 0 / P1 0 / P2 1. Closed role-presence override in multi-role shortlist
  and transition selection.
- R4: PASS, P0/P1/P2/P3 all zero; 72 focused tests and Bandit clean.
- Fresh exporter/import-boundary review: PASS, P0/P1/P2/P3 all zero; exact Git blob
  identity independently reproduced, all three import contracts kept, 72 focused
  tests and Bandit clean.

No producer approved its own material work. Two packet YAML plain-scalar colon defects
were corrected mechanically after the exact packet content had already been read and
executed; all 46 W08 packets parse now. This was an orchestration-format correction,
not a product or evidence change.

## Accepted unattended invariants

1. Authentication, expiry, revocation, fixation resistance, CSRF and disabled-user
   denial operate locally with no external identity or network dependency.
2. Authorisation is deny-by-default and binds tenant, owner, current assignment and
   any independently applicable explicit multi-role grant; IDOR and privilege
   escalation probes deny.
3. Historical brief, retrieval, shortlist and observation interpretation is versioned
   and replayable; human actions are attributable, reversible and audit-linked.
4. Private/team observations, comments and exports respect the intended
   confidentiality boundary. Inventory, create, read and revoke verify persisted pack
   bytes before disclosure or state change.
5. Append-only receipts bind actor, tenant, session, action, target, timestamp and
   evidence hash. SQL, storage and audit failures are atomic and a clean retry does
   not duplicate state.
6. Optimistic conflicts preserve the winning write and expose a visible recovery
   path. Input, path, media-type, UTF-8, size and symlink guards fail closed.
7. Automated Chromium and master browser inspection pass the core role journeys,
   expired/denied sessions, conflict recovery, keyboard/focus/landmark/label checks,
   and desktop, 390-pixel and 320-pixel layouts without body overflow.
8. Every automated actor and fixture is labelled synthetic automation. Workflow
   completion is mechanics evidence only and cannot become model-quality or human
   evidence.
9. The W06 boundary remains `NO_GO`, sole reason
   `MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`,
   `synthetic_development_only`, `LIMITED`, and `no_recommendation_evidence`.
   Protected W06 expected outputs were not opened or reconstructed.
10. No remote, external provider, model call, service, container, Node runtime, cloud
    resource, deployment, W09 challenger work or W10 shadow-pilot work was introduced.

## Gate decision

G-W08A may pass after one genuine operator pilot completes T1–T7, receipts and the
claim boundary reproduce, no P0/P1 remains and independent review passes. That exact
decision authorizes bounded local W09 challenger experimentation only; the current
G-W08A result is `PENDING`.

G-W08B remains blocked solely by genuine participation. Five distinct, authorised and
consenting representative users covering analyst, scout and approver/meeting
responsibilities must each complete T1-T7 unaided with all core tasks `PASS`, no
unsupported model/recruitment inference and no P0/P1 finding. Their de-identified
captures, local database/export receipts, checksums and summary must then be
reproduced and independently reviewed.

Until G-W08B evidence exists, do not create the W08 acceptance commit or
`checkpoint/w08-accepted` and do not mark W08 VERIFIED/CHECKPOINTED/CLOSED. Do not
begin W09 until G-W08A records `PASS / DEVELOPMENT_PROGRESSION_AUTHORIZED`; after that
decision, W09 remains restricted to the retained bounded local experimentation scope.

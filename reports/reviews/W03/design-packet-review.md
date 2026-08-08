# W03 design-packet review

- Review task: `W03-DESIGN-REVIEW-00`, revision `R1`
- Reviewer role: independent verifier
- Scope: packet decomposition and gate design only; no implementation artifact was reviewed or approved
- Recommendation: **REWORK before dispatching W03 storage, fixture, database, or vertical-journey implementation**

## Controlling requirements

This review applies the following controls:

- `../scouting-ml-agent-implementation-workflow.html`, §08 W03.1–W03.6 and
  `G-W03`, requires contracts, guarded storage, database/migration work,
  deterministic fixtures, one role-brief-to-audit vertical journey, and a
  subsequent independent boundary audit.
- `../scouting-ml-production-blueprint.html`, §08 P0.1–P0.9, P1.1–P1.8 and
  `G1`, requires the decision/claim/rights/evaluation/security controls, strict
  contracts, database/migrations, guarded storage, executable authentication
  and authorisation, master-run verification, local telemetry, and deterministic
  synthetic fixtures.
- `../scouting-ml-agent-implementation-workflow.html`, §§03, 04 and 09, and
  `AGENTS.md` §§Authority and Task lifecycle, reserve integration, verification,
  acceptance, Git, dependency, and checkpoint authority to the master; require
  disjoint parallel writes; and require separate review of high-risk contracts,
  migrations, storage, authorisation, and serving boundaries.
- `orchestration/ownership.yaml` marks contracts, migrations, guarded storage,
  temporal eligibility, and authorisation as high-risk review areas and keeps
  shared contracts and migrations serial.

## Executive decision

The five implementation packets that exist are generally bounded and
path-disjoint, but the decomposition is incomplete. There is no W03.5
vertical-journey packet in either `orchestration/phase_registry.yaml` or the
reviewed packet set, and there is no post-implementation W03.6 boundary-audit
packet. `W03-DESIGN-REVIEW-00` cannot substitute for W03.6 because it runs
before storage, migration, authZ, and serving artifacts exist.

Consequently neither `G-W03` nor blueprint `G1` can be satisfied: there is no
owned implementation for application startup, test-user authentication,
application-level deny-by-default authorisation, the complete synthetic
request, local telemetry, or the independent review of the finished high-risk
boundaries.

## W03.1–W03.6 mapping

| Requirement | Current packet coverage | Assessment |
| --- | --- | --- |
| **W03.1** strict foundation contracts | `W03-CONTRACTS-01-R1` owns strict UUID/UTC/tenant, temporal/source, role-brief, retrieval, shortlist-entry, and audit models plus contract tests. | **Partial.** The core scope is correctly isolated and serial. The packet should explicitly require a versioned identity-crosswalk shape and the blueprint quality controls for JSON round-trip and compatibility/version behaviour, rather than the less precise phrase “identity evidence.” |
| **W03.2** guarded local persistence | `W03-STORAGE-01-R1` owns bounded roots, symlink/traversal rejection, atomic immutable formats, hashes, manifests, and idempotency. | **Covered by design.** Its dependency on accepted contracts is correct, and its paths are disjoint from database persistence. |
| **W03.3** database schemas and first migration | `W03-DATABASE-01-R1` owns loopback Compose, Alembic, foundation migration, PostgreSQL persistence, RLS, append-only audit, and tests. | **Partial.** Scope and serial migration ownership are explicit, but the acceptance criteria should prove cross-tenant denial through the non-owner application role and audit update/delete rejection under the runtime role, not merely that policies and triggers are present. |
| **W03.4** deterministic synthetic domain | `W03-FIXTURES-01-R1` owns two competitions, teams/matches/players, ambiguous identity, late and prohibited future facts, expected retrieval, and deterministic tests. | **Partial.** It depends only on contracts even though `W03-GOVERNANCE-01-R1` freezes the replay cutoff, required negative cases, and protected-fixture rules. The fixture can therefore be authored concurrently against a different evaluation contract. |
| **W03.5** one vertical journey | No packet or registry task exists. | **Missing implementation.** No owner, paths, dependencies, tests, or stop conditions cover role brief → deterministic fixture retrieval → explanation → shortlist entry → audit, test-user authN, app authZ, local telemetry, health/readiness, or an end-to-end request. |
| **W03.6** independent boundary audit | `W03-DESIGN-REVIEW-00-R1` reviews decomposition before downstream dispatch. No post-implementation reviewer packet exists. | **Missing independent verification.** A pre-implementation design review cannot inspect storage escape, applied migrations/RLS, temporal rejection, authZ enforcement, or serving-path behaviour. The master also cannot use this report as reviewer acceptance of artifacts that did not yet exist. |

## Blueprint P0 control mapping

| Control | Coverage or disposition | Assessment |
| --- | --- | --- |
| **P0.1** user and decision discovery | Governance is forbidden from inventing real-user evidence and only materialises the approved roles/jobs. | **Explicitly unresolved, not an implementation omission to fabricate.** Actual interviews require named domain users. W03 may proceed as a synthetic spine, but no report should claim full P0/G0 discovery closure. This must close before a real-user pilot gate. |
| **P0.2** product claim and non-claims | `W03-GOVERNANCE-01-R1` requires evidence-only discovery, resemblance-not-outcome boundaries, and R0/R1/R2 cut lines. | **Covered.** |
| **P0.3** role-brief and shortlist state machines | Contracts include role-brief and shortlist-entry shapes; governance requires a journey, but neither packet requires the defined owners, transitions, approvals, rejection reasons, visibility, and retention rules named by P0.3. | **Missing design control.** Full workflow implementation belongs to later W08/P4, but the state-machine definition is a P0 prerequisite and should be added to the W03 governance deliverable. |
| **P0.4** data and rights inventory | Governance covers generated, local, non-personal, non-exported W03 fixtures. Real provider/right/coverage selection is assigned by the workflow to W04.1. | **Correctly split.** Synthetic rights must close now; real-source inventory is later-phase work and must close before W04 ingestion, not be claimed at W03. |
| **P0.5** risk register/threat model | Governance requires identity, leakage, path, tenant/authZ, confidentiality, audit, secret, and misuse threats with fail-closed controls. | **Covered.** |
| **P0.6** evaluation contract | Governance requires replay cutoff, negatives, metrics, protected fixture, and minimum gate. | **Covered in intent, but must precede fixtures.** |
| **P0.7** local-only boundary | Existing W01 controls plus governance local-review and data-rights policies preserve loopback/local-only operation. | **Covered.** |
| **P0.8** toolchain/orchestration ADRs | W01/W02 and ADRs 0001/0002 are prior accepted controls. | **Previously covered.** |
| **P0.9** phase evidence/return templates | W02 created the packet/review/return controls; every reviewed packet names the mandatory return. | **Previously covered.** |

The blueprint `G0` claim therefore remains intentionally narrower than a
real-data or real-user gate: claim boundary, synthetic rights, evaluation, and
threat controls can close in W03, while real user discovery and provider rights
remain visibly open for their named later decisions.

## Blueprint P1 and G1 mapping

| Control | Coverage | Assessment |
| --- | --- | --- |
| **P1.1** local uv monorepo scaffold | Accepted W01 foundation. | **Previously covered.** |
| **P1.2** strict base contracts | `W03-CONTRACTS-01-R1`. | **Partial**, subject to the identity-crosswalk and round-trip/compatibility clarifications above. |
| **P1.3** database and migrations | `W03-DATABASE-01-R1`. | **Covered in design**, subject to executable RLS/audit enforcement tests. |
| **P1.4** guarded artifact paths | `W03-STORAGE-01-R1`. | **Covered in design.** |
| **P1.5** local authN/authZ spine | Governance owns only policy YAML; database owns tenant RLS. No packet owns local users/sessions, runtime policy enforcement, a test user, or negative object/action tests through the application. | **Missing implementation.** This belongs in the absent W03.5 packet for the synthetic spine; richer workflow auth remains later W08. |
| **P1.6** master-run verification pipeline | Accepted W01/W02 controls; final W03 rerun remains master-only. | **Previously covered; final execution is master work.** |
| **P1.7** instrument the empty vertical slice | No packet owns request IDs, local structured logs/traces/metrics, health/readiness, or a diagnostic report. | **Missing implementation.** It should be an explicit W03.5 deliverable, not inferred from a future phase. |
| **P1.8** deterministic synthetic fixtures | `W03-FIXTURES-01-R1`. | **Covered in design**, after dependency repair. |

`G1`/`G-W03` outcome mapping:

- Fresh locked sync: retained as a master gate responsibility; the accepted
  dependency packet is the prerequisite.
- Migrations apply and local services start: database packet covers PostgreSQL
  and Redis, but no application/worker startup is owned.
- Test user authenticates: missing.
- Synthetic request runs end to end: missing W03.5.
- Telemetry is written locally: missing P1.7 ownership.
- Future data fails closed: contracts plus fixture packets cover the unit-level
  proof; the vertical packet must prove the same boundary end to end.
- Contract/storage/authZ checks pass: contract and storage checks exist;
  executable application authZ checks do not.
- Master and reviewer reports agree: master review is retained correctly, but a
  post-implementation W03.6 reviewer packet is missing.

## Path overlap, concurrency, and dependency order

### Safe aspects

- Contracts, governance, guarded storage, fixtures, database, and each return
  file have disjoint declared write paths.
- Storage owns `src/scouting/storage/__init__.py`, `guarded.py`, and
  `formats.py`; database owns only `src/scouting/storage/postgres.py`, so their
  implementation scopes do not overlap.
- Contracts are dispatched serially before storage, fixtures, or database, as
  required by `ownership.yaml`.
- The sole migration packet has explicit migration ownership and no concurrent
  migration writer. Dependency/lock files and Git remain master-only.
- Governance and the pre-dispatch design review can run beside contracts
  because their writes are disjoint and neither changes shared contracts or
  migrations.

### Required order repairs

1. Make `W03-FIXTURES-01` depend on both `W03-CONTRACTS-01:ACCEPTED` and
   `W03-GOVERNANCE-01:ACCEPTED`, and require it to read the accepted evaluation
   contract and synthetic data-rights policy.
2. Add a W03.5 vertical-journey packet depending on accepted contracts,
   governance, storage, fixtures, and database work. Integration should be
   serial after those producers, not dispatched in the same implementation
   wave.
3. Add a W03.6 independent boundary-review packet depending on the accepted
   W03.1–W03.5 artifacts. It must run after implementation and before the master
   gate decision.

## Master/subagent authority review

- Every reviewed implementation packet forbids delegation and Git operations,
  excludes dependency/lock changes, and names a unique return path. These
  controls correctly retain Git, integration, gate, and checkpoint authority
  with the master.
- The database packet expressly allocates the otherwise master-controlled
  migration paths and keeps them serial. That is a valid bounded allocation,
  but it triggers the mandatory separate migration review.
- The current design-review packet makes a recommendation only; it does not
  approve its own work or any implementation.
- The missing post-implementation W03.6 packet is an authority defect, not just
  an evidence-document omission. Without it, the master has no independent
  reviewer return for the high-risk contract, temporal, migration, guarded
  storage, authZ, and serving boundaries required by the workflow and
  `ownership.yaml`.
- `W03-GOVERNANCE-01-R1` calls its YAML “strict,” but its only direct YAML check
  is `yaml.safe_load`. Parsing does not prove required keys, deny-by-default
  semantics, role/action completeness, or loopback-only values. A semantic
  validator/test must be part of that packet or the later vertical packet.

## Ranked defects

### P0 — gate blockers

1. **No W03.5 vertical-journey packet or registry task.**  
   Controlling requirements: workflow W03.5 and `G-W03`; blueprint P1.5, P1.7,
   `G1`, and the §12 “Practical first scaffold.”  
   Affected decomposition: all current W03 packets/registry.  
   Required correction: add a serial integration packet with exact paths and
   tests for authenticated role brief → deterministic retrieval/explanation →
   shortlist → append-only audit, cross-tenant/action denial, local
   health/telemetry, and an end-to-end future-data rejection.

2. **No post-implementation W03.6 boundary-audit packet.**  
   Controlling requirements: workflow W03.6, `G-W03`, and §09 step 8;
   `AGENTS.md` high-risk review discipline; `ownership.yaml` high-risk areas.  
   Affected decomposition: `W03-DESIGN-REVIEW-00` and the absent final reviewer
   task.  
   Required correction: create a separate independent reviewer packet after
   W03.1–W03.5; the current design review must remain pre-dispatch evidence only.

### P1 — unsafe ambiguity or incomplete acceptance

3. **Fixture/evaluation dependency is reversed or absent.**  
   Controlling requirements: blueprint P0.6 and P1.8; workflow Ready rule and
   W03.4.  
   Affected packet: `W03-FIXTURES-01-R1`.  
   Required correction: depend on accepted governance/evaluation controls and
   read their replay cutoff, negative cases, and protected-fixture rule.

4. **Executable authN/authZ and local telemetry have no owner.**  
   Controlling requirements: blueprint P1.5, P1.7 and `G1`; workflow
   `G-W03`.  
   Affected packets: governance defines policy and database defines RLS, but
   neither implements the application/runtime boundary.  
   Required correction: assign this scope and negative tests explicitly to
   W03.5.

5. **P0.3 state-machine definition is not a deliverable.**  
   Controlling requirement: blueprint P0.3.  
   Affected packet: `W03-GOVERNANCE-01-R1`.  
   Required correction: define owners, transitions, approvals, rejection
   reasons, visibility, and retention now; keep the richer workflow
   implementation in W08/P4.

6. **“Strict YAML” has only a parse check.**  
   Controlling requirements: governance packet definition of done, blueprint
   P1.5, and `G1` authZ requirement.  
   Affected packet: `W03-GOVERNANCE-01-R1`.  
   Required correction: add schema/semantic assertions for required fields,
   deny-by-default, the four roles, explicit action mapping, synthetic-only
   rights, and loopback-only environment values.

7. **Contract and database acceptance criteria under-specify boundary proofs.**  
   Controlling requirements: blueprint P1.2/P1.3 and §09 contract/API/security
   tests.  
   Affected packets: `W03-CONTRACTS-01-R1`,
   `W03-DATABASE-01-R1`.  
   Required correction: explicitly test versioned crosswalk evidence, JSON
   round-trip/version compatibility, non-owner cross-tenant RLS denial, and
   runtime-role audit update/delete rejection.

### P2 — control-plane clarity

8. **Specialist role names are not mapped explicitly in ownership policy.**  
   Controlling requirement: workflow §03 specialist lanes and
   `orchestration/ownership.yaml`.  
   Affected packets: governance, storage, fixture, and database use granular
   `assigned_role` names not present as lane keys. Their explicit allowed paths
   bound the work, so this is not a current gate blocker, but the master should
   record how those roles map to `contracts_platform`, `data_identity`, or the
   default master lane before automated ownership validation relies on the
   names.

## Required decomposition before downstream dispatch

The smallest safe rework is:

1. Repair the fixture dependency and governance semantic acceptance.
2. Clarify the contract/database boundary tests.
3. Add W03.5 with serial dependencies on all W03 producers and explicit authN,
   authZ, telemetry, E2E, and fail-closed scope.
4. Add W03.6 as a genuinely post-implementation independent review.
5. Keep actual provider-rights work in W04 and full collaborative workflow in
   W08; do not pull those later-phase implementations into W03.

## Recommendation

**REWORK.** The existing packets are a sound base, but dispatching storage,
fixtures, or database before the dependency repair and missing task packets are
recorded would leave known holes in the only path to `G-W03`/`G1`. This
recommendation is a design challenge for the master; it is not self-approval,
implementation acceptance, or permission to checkpoint W03.

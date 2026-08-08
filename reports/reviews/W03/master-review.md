# W03 master review

Decision: **ACCEPT for checkpoint**

## Scope and authority

- Root:
  `/Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence`
- Branch: `main`
- Start tag: `checkpoint/w03-start`, resolving to accepted W02 commit
  `8e40321fc6d87bbd8adac4ba3efc85eee41554c5`
- Git remotes: none
- Master-owned areas: dependencies/lock, migrations, shared orchestration,
  integration, protected gate, evidence, and every Git action
- Subagent Git, Docker, protected-fixture, dependency, and self-approval actions: none

The master read every changed implementation, test, configuration, migration,
orchestration, return, review, and evidence file. The two controlling HTML documents
and unrelated work were not modified.

## Orchestration and rework record

W03 was decomposed into bounded dependency, contracts, governance/design, storage,
fixture, database, vertical, architecture, and independent-review packets. Each
subagent received exact path ownership, no Git authority, and a mandatory return.

The master rejected incomplete or unsafe candidates rather than waiving defects:

- contracts and governance each required R2 corrections;
- fixture R2 added strict `observed_at >= cutoff` rejection;
- vertical R1–R5 closed protected-input isolation, request-bound identity/lineage,
  artifact provenance, and bounded explanation rendering;
- protected attempts R1–R3 remain as negative evidence; R4 passes exact output,
  explanations, temporal admission/rejection, and repeat digest;
- independent boundary R1 found a P1 same-tenant persisted-owner collision after the
  producer suite had passed;
- vertical R6 changed all five material inserts from silent conflict acceptance to
  insert-or-exact-canonical-verify behavior inside one transaction;
- independent boundary R2 passed 17 adversarial tests, including later shortlist and
  entry collisions, four same-owner immutable-content mismatches, victim-state
  preservation, zero denied side effects, and exact replay.

No reviewer approved its own implementation. The master independently reproduced every
accepted packet and every retained failure.

## Architecture, security, and data boundaries

- Import-linter enforces the approved dependency direction and forbids serving,
  workflow, and policy from importing provider adapters.
- Contracts reject unknown fields, non-UTC values, temporal equality/future evidence,
  lineage mismatch, and candidate/result tampering.
- PostgreSQL uses a non-login, non-superuser, non-bypass application role, transaction
  local tenant context, RLS, and append-only audit controls.
- Guarded storage rejects traversal and escaped-directory symlinks before I/O.
- Authentication/authorization is deny-by-default and confidential denials are
  content-free but append-only audited.
- Telemetry is local, redacts sensitive fields, exports nowhere, and services bind only
  to loopback.
- The protected synthetic partition remained master-only throughout implementation
  and independent review.

## Master gate

The full locked suite passed with 185 tests, 101 formatted files, 37 strictly typed
source files, three import contracts, Bandit, governance, exact protected output,
active push guard, local-only verifier, Compose validation, healthy loopback services,
and empty `git remote` output.

The first full-suite run exposed one stale W02 unit assertion that still capped
authorization at W02. The master updated it to verify the user-approved continuous
W03–W11 authority and dynamic phase dependency chain; the complete suite then passed.

No architecture, project-root, dependency-policy, or local-only boundary change was
required.


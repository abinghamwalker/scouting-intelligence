# W03 independent boundary audit — R2

- Task: `W03-BOUNDARY-REVIEW-01-R2`
- Reviewer role: independent verifier
- Review date: 2026-07-29
- Recommendation: **ACCEPT**
- Defects: no reproduced `P0`, `P1`, or `P2` defect
- Protected-fixture status: not accessed; no protected expected result was opened,
  read, or executed by this reviewer

## Executive result

The R6 persisted-object correction closes the R1 same-tenant role-brief collision.
Independent challenges at the role-brief, shortlist, and shortlist-entry boundaries
all returned the generic `403 {"detail":"action denied"}` response. Complete JSONB
snapshots of the victim role brief, shortlist, and shortlist entry were unchanged,
and the denied analyst produced zero role-brief, retrieval, candidate, shortlist,
entry, or audit effects.

The reviewer also challenged same-owner immutable mismatches at four conflict-aware
boundaries: role-brief content, a derived retrieval keyed by an existing request ID,
shortlist identity/content, and shortlist-entry rationale. Each mismatch failed closed
and the complete attempted-effect vector remained unchanged. An exact canonical replay
was accepted deterministically: both responses contained the same retrieval result and
shortlist entry, exactly one row remained at each of the five material boundaries, and
each distinct successful API request retained its own four append-only audit events.

All ten original R1 boundary challenges remain present and pass. The expanded reviewer
suite reports **17 passed**, and all three import-direction contracts remain kept.
This supports an **ACCEPT** recommendation for W03.1–W03.6, `G-W03`, and the reviewed
W03 contribution to blueprint `G1`. This is a reviewer recommendation, not
self-approval; the master retains the protected gate and phase decision.

## Controlling and reviewed artifacts

The reviewer read the complete R2 packet-required control set:

- `AGENTS.md`
- `../scouting-ml-production-blueprint.html`
- `../scouting-ml-agent-implementation-workflow.html`
- `orchestration/task_packets/W03-BOUNDARY-REVIEW-01-R2.yaml`
- `orchestration/reviews/REVIEW-W03-BOUNDARY-REVIEW-01-R1.yaml`
- `orchestration/reviews/REVIEW-W03-VERTICAL-01-R6.yaml`
- `reports/reviews/W03/boundary-audit.md`
- `reports/reviews/W03/returns/W03-VERTICAL-01-R6.md`
- `docs/architecture/evaluation-contract.md`
- `docs/architecture/threat-model.md`
- `src/scouting/workflow/service.py`
- `tests/e2e/test_w03_vertical_journey.py`
- `tests/security/test_w03_boundary_audit.py`
- `orchestration/templates/subagent_return.md`

The R6 implementation was inspected read-only. Each of the five material writes now
uses insert-or-verify behavior in the existing transaction. A suppressed conflict is
accepted only when every persisted immutable column is equal with null-safe comparison;
a hidden, absent, owner-mismatched, or content-mismatched row raises the existing
generic denial. Untargeted conflict handling on retrieval, candidate, and entry writes
also covers their alternate unique constraints.

No implementation, configuration, dependency, migration, orchestration, fixture,
producer test, or R1 report was edited. No artifact under the protected synthetic
fixture tree and no protected expected output was accessed.

## Independent executable evidence

The reviewer test creates fresh strict contracts and identifiers and checks invariants
directly. It does not use a producer expected-result oracle.

| Reviewer challenge | Result | Independent evidence |
| --- | --- | --- |
| Retained R1 role-brief owner collision | PASS | Analyst B receives generic denial; full victim snapshot unchanged; attempted-effect vector is `(0, 0, 0, 0, 0, 0)` |
| Same-tenant shortlist owner collision | PASS | Denial occurs after earlier candidate work would have been attempted; transaction leaves zero attacker material/audit effects |
| Same-tenant shortlist-entry owner collision | PASS | Latest material conflict still rolls back role brief, retrieval, candidate, shortlist, and audit writes |
| Same-owner role-brief immutable mismatch | PASS | Changed title under the canonical ID is denied; stored victim content and counts are unchanged |
| Same-owner derived-retrieval immutable mismatch | PASS | Existing retrieval request ID with different canonical brief/trace relationships is denied; the new brief is rolled back |
| Same-owner shortlist immutable mismatch | PASS | Existing shortlist ID with different role-brief relationship/title is denied; preceding writes are rolled back |
| Same-owner shortlist-entry immutable mismatch | PASS | Existing entry ID with changed rationale is denied after exact earlier-boundary replay; no row or audit changes |
| Exact same-owner canonical replay | PASS | Two `200` responses have identical result and entry; effects per request are `(1, 1, 1, 1, 1, 4)` |
| Strict unknown-field/non-UTC input and cutoff-equality rejection | PASS | Original R1 contract challenge retained |
| Canonical lineage binding and result/candidate tamper rejection | PASS | Original R1 lineage challenge retained |
| Ambiguous identity exclusion despite strong pre-cutoff fact | PASS | Original R1 identity challenge retained |
| Traversal and escaped-directory symlink rejection before I/O | PASS | Original R1 guarded-storage challenge retained |
| Application-role RLS and append-only audit enforcement | PASS | Original R1 database challenge retained |
| Unknown action, cross-tenant policy, authentication, and confidential minimisation | PASS | Original R1 policy challenge retained |
| Fresh role brief → retrieval → explanation → shortlist → audit journey | PASS | Original R1 vertical challenge retained |
| Missing model without silent substitution | PASS | Original R1 fail-closed serving challenge retained |
| Loopback runtime, worker, telemetry, and unsafe DB URL controls | PASS | Original R1 local-runtime challenge retained |
| Declared dependency direction and provider isolation | PASS | 27 files and 37 dependencies analysed; 3 contracts kept, 0 broken |

The final reviewer pytest result is **17 passed, 1 deprecation warning**. The warning
comes from the installed FastAPI/Starlette `TestClient` compatibility layer and is not
an observed W03 boundary failure.

## R1 correction readback

The R1 failure allowed analyst B to reuse analyst A's role-brief ID/version because the
workflow authorised inbound owner data and silently ignored a persistence conflict.
R6 replaced that behavior with an exact persisted-row check inside the same
transaction.

The retained role-brief challenge now passes without weakening its expected boundary:

1. Analyst A persists a fresh role brief, retrieval, shortlist, entry, and audits.
2. Analyst B in the same tenant submits A's role-brief ID/version while naming B as
   owner.
3. The request returns only `403 {"detail":"action denied"}`.
4. A full before/after snapshot confirms A's brief, shortlist, and entry are unchanged.
5. Counts scoped to B's attempted brief, retrieval request, candidate chain, shortlist,
   entry, and request audit are all zero.

The additive shortlist and shortlist-entry collisions demonstrate that the correction
also holds when denial occurs later in the transaction. The earlier writes and audit
events are not partially committed.

## Requirement-to-evidence mapping

| Requirement | Independent R2 evidence | Assessment |
| --- | --- | --- |
| **W03.1** strict foundation contracts | Unknown fields and non-UTC input reject; both cutoff equality cases reject; canonical lineage binds; mutated result/candidate lineage rejects; fresh journey IDs and versions remain consistent. | PASS |
| **W03.2** guarded local persistence | Relative traversal and an escaped directory symlink reject before I/O, with both outside targets remaining absent. | PASS |
| **W03.3** database, RLS, and append-only audit | `scouting_app` remains non-owner/non-bypass; cross-tenant visibility and write attempts deny; application and owner audit mutation attempts fail; late journey conflicts roll back all preceding writes and audits. | PASS |
| **W03.4** deterministic synthetic fixture | Manifest digest and temporal admission are checked directly; equality and missing evidence reject; ambiguous identity is excluded; no protected fixture or expected output was used. | PASS |
| **W03.5** vertical journey | Fresh journey, confidential minimisation, missing-model failure, local runtime, and audit sequence pass. Role-brief, shortlist, and entry owner collisions and four same-owner content mismatches fail closed; exact canonical replay is deterministic and material-idempotent. | PASS |
| **W03.6** independent boundary audit | Complete R2 readback, all original and additive executable challenges, import-linter rerun, report, and mandatory return are complete with no implementation edit. | COMPLETE — ACCEPT RECOMMENDATION |
| **G-W03** synthetic spine | Contract, temporal, guarded storage, RLS, authorisation, serving, audit, local runtime, import direction, persisted ownership, rollback, and replay boundaries all pass this independent review. | ACCEPT RECOMMENDATION |
| **G1** foundation gate | The reviewed W03 local DB/application/worker foundation is deny-by-default for the challenged persisted-object cases and remains loopback-only. Master-owned fresh-sync, protected, and checkpoint evidence remains outside this review. | ACCEPT RECOMMENDATION FOR REVIEWED W03 EVIDENCE |

## Command results

All commands used the repository's locked `uv` environment. Database-backed checks
used only the master-supplied loopback review database URL, redacted here.

- Baseline retained-R1 rerun before additive test edits:
  `uv run pytest -q tests/security/test_w03_boundary_audit.py`
  - exit `0`
  - `10 passed, 1 warning`
- Final expanded reviewer suite:
  `uv run pytest -q tests/security/test_w03_boundary_audit.py`
  - exit `0`
  - `17 passed, 1 warning`
- `uv run ruff format --check tests/security/test_w03_boundary_audit.py`
  - exit `0`
  - one file already formatted
- `uv run ruff check tests/security/test_w03_boundary_audit.py`
  - exit `0`
  - all checks passed
- `uv run lint-imports --no-cache`
  - exit `0`
  - 27 files and 37 dependencies analysed; all three contracts kept

## Residual boundary

- Insert-or-verify comparisons cover the current immutable schema. A future migration
  adding an immutable material column must extend the corresponding comparison.
- Exact replay intentionally means material idempotency, not audit suppression:
  distinct successful API requests each append four audit events.
- This review establishes deterministic W03 synthetic controls only. It does not claim
  real-data quality, model performance, expert relevance, usability, privacy,
  penetration-test, disaster-recovery, or production-security evidence.
- The master retains protected-fixture execution, fresh locked-sync/integration
  evidence, the phase decision, and every Git/checkpoint action.

## Recommendation

**ACCEPT.** The R1 `P1` is independently closed, the later shortlist and entry
boundaries fail closed with full rollback, same-owner content mismatches deny, exact
canonical replay is deterministic and material-idempotent, and every original
boundary/import challenge passes. This is a recommendation to the master and not a
phase-gate approval.

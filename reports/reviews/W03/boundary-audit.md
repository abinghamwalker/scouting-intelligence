# W03 independent boundary audit

- Task: `W03-BOUNDARY-REVIEW-01-R1`
- Reviewer role: independent verifier
- Review date: 2026-07-29
- Recommendation: **REWORK**
- Defects: one `P1`; no `P0` or `P2`
- Protected-fixture status: not accessed; the master-owned protected result was not
  opened, read, or executed by this reviewer

## Executive result

The strict-contract, cutoff-equality, lineage, ambiguous-identity, guarded-storage,
non-owner RLS, audit-immutability, confidential-response, missing-model, telemetry,
loopback-runtime, and import-direction challenges passed.

The completed application does not, however, deny one same-tenant object-ownership
mismatch. A second authenticated analyst can submit another analyst's existing
`role_brief_id` and version while naming themselves as owner in the inbound payload.
The application authorises the unpersisted payload, silently ignores the conflicting
role-brief insert, and continues to create retrieval and audit activity attached to the
first analyst's persisted brief. The request returns `200` rather than a generic denial.

This is a `P1` authorisation and audit-integrity defect. It violates threat `T04`, the
evaluation contract's object-ownership negative case, and the frozen policy's object
rules. It prevents W03.5, `G-W03`, and blueprint `G1` from passing without rework.

## Controlling and reviewed artifacts

The reviewer read the complete packet-required control set:

- `AGENTS.md`
- `../scouting-ml-production-blueprint.html`
- `../scouting-ml-agent-implementation-workflow.html`
- `orchestration/task_packets/W03-BOUNDARY-REVIEW-01-R1.yaml`
- `docs/architecture/evaluation-contract.md`
- `docs/architecture/threat-model.md`
- `reports/reviews/W03/design-packet-review.md`
- `orchestration/reviews/REVIEW-W03-CONTRACTS-01-R2.yaml`
- `orchestration/reviews/REVIEW-W03-GOVERNANCE-01-R2.yaml`
- `orchestration/reviews/REVIEW-W03-STORAGE-01-R1.yaml`
- `orchestration/reviews/REVIEW-W03-FIXTURES-01-R2.yaml`
- `orchestration/reviews/REVIEW-W03-DATABASE-01-R1.yaml`
- `orchestration/reviews/REVIEW-W03-VERTICAL-01-R5.yaml`
- `orchestration/reviews/REVIEW-W03-ARCHITECTURE-01-R1.yaml`
- `orchestration/templates/subagent_return.md`

The reviewer independently inspected these implementation and configuration artifacts:

- Contract floor:
  `src/scouting/contracts/{primitives,evidence,retrieval,workflow,audit}.py` and
  `src/scouting/contracts/__init__.py`
- Fixture/temporal admission:
  `src/scouting/sources/synthetic.py` and
  `tests/fixtures/synthetic/domain.json`
- Guarded persistence:
  `src/scouting/storage/{guarded,formats,postgres}.py` and
  `src/scouting/storage/__init__.py`
- Policy:
  `src/scouting/policy/{authentication,authorization,eligibility}.py`,
  `src/scouting/policy/__init__.py`,
  `configs/policies/authorization.yaml`, and
  `configs/policies/data-rights.yaml`
- Serving and workflow:
  `src/scouting/serving/synthetic.py`,
  `src/scouting/serving/__init__.py`,
  `src/scouting/workflow/service.py`, and
  `src/scouting/workflow/__init__.py`
- Audit and telemetry:
  `src/scouting/audit/writer.py`,
  `src/scouting/operations/telemetry.py`, and
  `src/scouting/operations/__init__.py`
- Composition and presentation:
  `src/scouting/web/app.py`,
  `services/api/main.py`,
  `services/worker/main.py`, and
  `apps/web/templates/w03_journey.html`
- Database:
  `migrations/versions/0001_foundation.py`
- Local/runtime controls:
  `configs/environments/local-only.yaml`,
  `configs/environments/w03-local-review.yaml`, and `compose.yaml`
- Import boundaries:
  the `[tool.importlinter]` and three declared contract sections in
  `pyproject.toml`
- Existing test context used only for independent setup/readback:
  `tests/security/test_database_boundaries.py`,
  `tests/security/test_application_authorization.py`, and the W03 journey/setup
  portions of `tests/e2e/test_w03_vertical_journey.py`
- Reviewer-owned executable evidence:
  `tests/security/test_w03_boundary_audit.py`

No artifact under the protected synthetic fixture tree and no protected expected output
was accessed.

## Independent executable evidence

The reviewer test does not compare the journey to the producer's development expected
result. It creates fresh strict role-brief and retrieval contracts, uses fresh request
and workflow identifiers, and checks invariants directly.

| Reviewer challenge | Result | Evidence |
| --- | --- | --- |
| Strict unknown-field and non-UTC contract rejection | PASS | `test_strict_contracts_and_cutoff_equality_fail_closed` |
| `observed_at == cutoff` and `available_at == cutoff` rejection | PASS | Same test; both equality cases denied and temporal contract construction rejected |
| Canonical dependency-lineage hash and exact source-manifest digest binding | PASS | `test_runtime_lineage_is_canonical_and_tampering_is_rejected` |
| Result/candidate lineage tamper rejection | PASS | Same test; both mutated JSON payloads rejected by strict contracts |
| Ambiguous identity exclusion despite a stronger eligible-looking fact | PASS | `test_ambiguous_identity_is_ineligible_even_with_strong_pre_cutoff_fact` |
| Traversal and escaped-directory symlink rejection before outside write | PASS | `test_guarded_storage_rejects_traversal_and_escaped_symlink_before_io` |
| `scouting_app` non-owner attributes and cross-tenant RLS read/write denial | PASS | `test_non_owner_rls_and_audit_immutability_hold_in_one_review_transaction` |
| Audit update/delete denial for application role and owner-trigger mutation rejection | PASS | Same DB transaction test |
| Unknown action, cross-tenant policy, and unauthenticated request denial | PASS | `test_app_policy_denies_unknown_context_and_minimises_confidential_response` |
| Confidential denial response minimisation plus content-free denial audit | PASS | Same test |
| Same-tenant persisted role-brief owner collision | **FAIL** | `test_same_tenant_existing_brief_owner_collision_is_denied` returned `200`, with persisted owner A, retrieval trace B, and audit actor B |
| Fresh role brief → retrieval → explanation → shortlist → audit journey | PASS | `test_full_app_journey_binds_contracts_lineage_and_append_only_audit` |
| Missing model artifact without silent substitution | PASS | `test_missing_model_fails_closed_without_silent_substitution` |
| Loopback health/readiness, no worker listener, telemetry redaction/no export, unsafe DB URL denial, loopback Compose ports | PASS | `test_local_runtime_and_telemetry_have_no_public_or_confidential_export` |
| Declared layer and forbidden provider-source import contracts | PASS | `uv run lint-imports --no-cache`: 27 files, 37 dependencies, 3 kept, 0 broken |

Final reviewer pytest result: **9 passed, 1 failed, 1 deprecation warning**. The warning
comes from the installed FastAPI/Starlette `TestClient` compatibility layer and does
not affect the reproduced authorisation failure.

## Ranked defect

### P1 — same-tenant role-brief ID collision bypasses persisted ownership

Requirements:

- `docs/architecture/threat-model.md`, `T04`: same-tenant and object checks must deny
  object-owner mismatch.
- `docs/architecture/evaluation-contract.md`: cross-tenant or object-ownership
  mismatch must deny without returning confidential object content.
- `configs/policies/authorization.yaml`: missing owner/visibility defaults to deny and
  role-brief updates require owner or approver.
- Workflow W03.5 and blueprint P1.5/G1: application authorisation must be executable
  and deny by default.

Reproduction:

1. Analyst A submits a fresh synthetic journey and persists role brief ID/version
   `X/1`.
2. Analyst B is a different authenticated `analyst` in the same tenant.
3. Analyst B submits another journey using `X/1`, but the inbound brief names B as its
   owner and uses B's fresh trace/request data.
4. Expected: generic `403 action denied` and no material writes.
5. Observed: `200 OK`.
6. DB evidence obtained through `scouting_app` shows the persisted brief remains owned
   by A, the new retrieval uses B's trace, and the new `role_brief.approved` audit
   event records B as actor.

Executable reproduction:

```text
SCOUTING_DATABASE_URL='postgresql+psycopg://scouting_owner:***@127.0.0.1:55432/scouting' \
uv run pytest -q tests/security/test_w03_boundary_audit.py
```

The failing assertion is
`tests/security/test_w03_boundary_audit.py:671`. The implementation first checks the
owner declared by the inbound contract at
`src/scouting/workflow/service.py:150`, then
`_insert_role_brief` silently accepts an existing `(role_brief_id, version)` through
`ON CONFLICT DO NOTHING` at `src/scouting/workflow/service.py:413`. It never verifies
the persisted object's owner or immutable content before continuing.

Bounded required correction:

1. Make role-brief creation conflict-aware inside the existing workflow transaction.
2. If `(role_brief_id, version)` is absent, insert it.
3. If it exists, allow an idempotent replay only when tenant, persisted owner, trace,
   version, and every immutable brief field exactly match the inbound contract.
4. On any owner or content mismatch, raise the existing generic application denial (or
   a non-disclosing conflict mapped to denial) before retrieval, shortlist, or audit
   writes.
5. Apply the same conflict-aware ownership rule to the client-supplied shortlist ID,
   which currently uses the same silent-conflict pattern.
6. Add a two-analyst, same-tenant regression proving both role-brief and shortlist ID
   collisions roll back with no audit or downstream writes.

The correction belongs to workflow implementation and its existing application/E2E
tests. Those paths are outside this review packet, so the reviewer made no correction.

## Requirement-to-evidence mapping

| Requirement | Independent evidence | Assessment |
| --- | --- | --- |
| **W03.1** strict foundation contracts | Unknown fields and non-UTC input reject; strict cutoff equality rejects; runtime result/candidate lineage tampering rejects; brief/request/version/cutoff identifiers bind in the fresh journey. | PASS |
| **W03.2** guarded local persistence | Relative traversal and an escaped directory symlink are rejected before I/O; both asserted outside targets remain absent. | PASS |
| **W03.3** database/migration/RLS/audit | `scouting_app` is no-login/non-super/non-bypass; tenant A cannot see or write tenant B; audit update/delete fails for app role and owner mutation hits the append-only trigger. | PASS |
| **W03.4** deterministic synthetic fixture | Development manifest digest validates; equality/missing facts reject; ambiguous identity is excluded even after injection of a strong pre-cutoff fact; no protected fixture was used. | PASS |
| **W03.5** vertical journey | Fresh happy-path journey, confidential minimisation, fail-closed missing model, non-owner DB context, audit sequence, telemetry, health, worker, and local-only checks pass. Same-tenant persisted-object ownership does not fail closed. | **REWORK — P1** |
| **W03.6** independent boundary audit | Reviewer readback, executable challenge, import-linter rerun, ranked defect, bounded correction, report, and mandatory return are complete; this is a recommendation only. | COMPLETE WITH REWORK RECOMMENDATION |
| **G-W03** synthetic spine | Contract, storage, temporal, RLS, audit, serving, local runtime, and import boundaries support the gate, but application object-authorisation has a reproduced P1 non-pass. | **REWORK** |
| **G1** foundation gate | The reviewed local DB/app/worker path runs and telemetry remains local; however blueprint P1.5/G1 deny-by-default authorisation is incomplete for persisted same-tenant ownership. Master-only fresh-sync and protected-gate evidence remain outside this reviewer run. | **REWORK** |

## Command results

All commands used the root `uv` environment. Database-backed checks used only the
approved loopback URL supplied by the master.

- `uv run pytest -q tests/security/test_w03_boundary_audit.py`
  - exit `1`
  - `9 passed, 1 failed, 1 warning`
  - intended failing regression:
    `test_same_tenant_existing_brief_owner_collision_is_denied`
- `uv run ruff format --check tests/security/test_w03_boundary_audit.py`
  - exit `0`
  - one file already formatted
- `uv run ruff check tests/security/test_w03_boundary_audit.py`
  - exit `0`
  - all checks passed
- `uv run lint-imports --no-cache`
  - exit `0`
  - 27 files and 37 dependencies analysed; all three contracts kept
- Boundary-report term check from the packet
  - exit `0`
  - all of `W03.1`–`W03.6`, `G-W03`, and `G1` present

## Residual boundary

This review establishes only the deterministic W03 synthetic controls. It does not
claim real-data quality, model performance, expert relevance, usability, privacy,
penetration-test, recovery, or production-security evidence. The master retains the
protected-fixture gate, fresh locked-sync/integration rerun, phase decision, and every
Git/checkpoint action.

## Recommendation

**REWORK.** Correct and independently retest the same-tenant persisted-object ownership
collision before the master can accept W03.5, `G-W03`, or `G1`.


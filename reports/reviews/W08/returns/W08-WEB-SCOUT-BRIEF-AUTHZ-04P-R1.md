# Subagent return

## Task

- task_id: `W08-WEB-SCOUT-BRIEF-AUTHZ-04P-R1`
- objective: Correct the R2 scout brief/replay disclosures and mixed-role composition through explicit, deny-by-default policy predicates.
- invariant: A scout-only principal sees only approved briefs and only the exact replay links connected to a current assigned shortlist entry; analyst/approver grants compose by union and no scout-role presence overrides another explicit grant.

## Files changed

- `configs/policies/w08-authorization.yaml`
- `src/scouting/policy/r1.py`
- `src/scouting/web/w08.py`
- `tests/security/test_w08_auth_audit.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `reports/reviews/W08/returns/W08-WEB-SCOUT-BRIEF-AUTHZ-04P-R1.md`

## Summary

- Added the explicit analyst grant `retrieval_link.read_owned` to the retained policy allowlist and its exact Python allowlist binding. It is not inferred from any other analyst grant.
- Replaced the prior global `action.endswith("_owned")` behaviour with an explicit `_OWNED_ACTIONS` set: `role_brief.update_owned`, `role_brief.submit_owned`, `role_brief.version_owned`, `retrieval_link.create_owned`, `retrieval_link.read_owned`, `shortlist.create_owned`, `shortlist_entry.add_owned`, and `shortlist_entry.transition_owned`. The security test proves every enumerated action is allowed only to the owner for both `TEAM` and `OWNER_ONLY`, and denied to a non-owner for both. No other suffix has ownership semantics implicitly.
- Added shared `can_read_brief` composition used by both queue and detail. It first honours `role_brief.read`; only if that explicit grant is absent does it allow `role_brief.read_approved` for the approved latest revision. Thus an analyst+scout owner reads an own draft through the analyst grant while a scout-only user cannot enumerate draft, submitted, or rejected briefs.
- Added `can_read_retrieval_link`. Analyst access requires `retrieval_link.read_owned` and the link creator as owner; approver access requires `retrieval_link.read`; scout access requires both `retrieval_link.read_assigned` and a latest shortlist-entry revision for that exact link assigned to that actor. It is used in both brief-detail rendering and shortlist link/candidate composition.
- Added synthetic automated route witnesses for the status, TEAM/OWNER_ONLY, exact-link assignment, unassignment, reassignment, cross-tenant, and mixed-role matrix. No synthetic fixture is claimed as scout or representative-user evidence.

## Decision tables

### Brief decision

| Principal / object | `TEAM` draft, submitted, rejected | `TEAM` approved | `OWNER_ONLY` approved, non-owner |
| --- | --- | --- | --- |
| Scout only | deny / absent from queue / generic 404 | allow brief metadata only | deny / absent / generic 404 |
| Analyst owner | allow through `role_brief.read` | allow through `role_brief.read` | allow through `role_brief.read` |
| Approver | allow through `role_brief.read` | allow through `role_brief.read` | normal visibility enforcement |
| Analyst + scout owner | allow through analyst `role_brief.read` | allow through analyst `role_brief.read` | allow through analyst grant when owner |

### Exact replay-link decision

| Principal / link condition | Link/projection/ordered candidate control |
| --- | --- |
| Analyst link creator with `retrieval_link.read_owned` | allow |
| Analyst not link creator | deny |
| Approver with `retrieval_link.read` and visible resource | allow |
| Scout, approved brief, no shortlist entry | deny |
| Scout, entry exists but unassigned | deny; shortlist alternate route is generic 404 |
| Scout, latest entry assigned through this exact link | allow |
| Former scout after latest revision clears/reassigns assignment | deny; shortlist alternate route is generic 404 |
| Current replacement scout | allow |
| Foreign tenant / unrelated role | generic deny |

## R2 reproduction matrix

| R2 probe | Before correction | After correction witness |
| --- | --- | --- |
| P1-01 same-tenant scout queue for TEAM draft/submitted/rejected | title, identifier and status disclosed | all three markers absent; direct detail is 404 |
| P1-02 same-tenant unassigned scout reads approved brief with link | 200 with replay heading, projection and ordered candidate data | brief metadata remains 200, while link UUID, `Exact local replay projection`, `Query digest and mode`, candidate marker and candidate control are absent; the linked shortlist route is generic 404 |
| P2 mixed analyst+scout own draft detail | own draft detail 404 because scout role overrode analyst | own draft detail 200 through the analyst `role_brief.read` grant |

### Assignment transition matrix

| Latest shortlist entry state | Scout A replay visibility | Scout B replay visibility |
| --- | --- | --- |
| no entry | deny | deny |
| `scout`, assigned to A through exact link | allow | deny |
| `monitor`, assignment cleared | deny / shortlist 404 | deny |
| `scout`, reassigned to B through exact link | deny | allow |

The route witness also proves an approved `OWNER_ONLY` brief plus exact link remains absent to the non-owner scout, while the approved `TEAM` brief is visible without exposing its unassigned replay link.

## Tests run

- `uv run ruff format --check src/scouting/policy/r1.py src/scouting/web/w08.py tests/security/test_w08_auth_audit.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: 5 files already formatted.
- `uv run ruff check src/scouting/policy/r1.py src/scouting/web/w08.py tests/security/test_w08_auth_audit.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: all checks passed.
- `uv run mypy src/scouting/policy/r1.py src/scouting/web/w08.py`
  - exit status: 0
  - result: success; no issues in 2 source files.
- `uv run pytest -q tests/security/test_w08_auth_audit.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py`
  - exit status: 0
  - result: 31 passed; one existing Starlette TestClient deprecation warning; 4.99s.
- `uv run bandit -q src/scouting/policy/r1.py src/scouting/web/w08.py`
  - exit status: 0
  - result: no findings.

## Artifacts/evidence

- `reports/reviews/W08/returns/W08-WEB-SCOUT-BRIEF-AUTHZ-04P-R1.md`
- `tests/security/test_w08_auth_audit.py::test_deny_by_default_owner_assignment_visibility_and_admin_boundary`
- `tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_scout_brief_and_replay_authorization_matrix`

## Risks

- The OWNER_ONLY route case deliberately removes the append-only test-fixture trigger before updating the two persisted brief projections; this simulates an existing valid private state only in a temporary synthetic test database. It is not an application mutation path.
- This producer evidence is automated mechanics/security evidence only. It does not close the five-person moderated representative-user gate and does not alter the W06 NO_GO / resemblance-only / synthetic-development-only / LIMITED boundary.

## Follow-up items

- Fresh independent security review is required before acceptance, per the parent packet and R2 disposition.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no protected-output inspection, external activity, participant evidence creation, or out-of-scope workflow/export/audit core change: confirmed.

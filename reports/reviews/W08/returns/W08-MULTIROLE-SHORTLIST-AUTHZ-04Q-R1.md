# Subagent return

## Task

- task_id: `W08-MULTIROLE-SHORTLIST-AUTHZ-04Q-R1`
- objective: Correct shortlist/entry read and transition grant composition while retaining every scout-only, visibility, assignment, and tenant boundary.
- invariant: For one shortlist or entry resource, access succeeds when at least one explicit applicable grant held by the principal authorises it; role presence never chooses or suppresses another grant, while scout-only access still requires exact current assignment and all owner, visibility and tenant restrictions remain unchanged.

## Files changed

- `src/scouting/workflow/r1.py`
- `src/scouting/web/w08.py`
- `tests/integration/test_w08_workflow.py`
- `tests/security/test_w08_workflow_access.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `reports/reviews/W08/returns/W08-MULTIROLE-SHORTLIST-AUTHZ-04Q-R1.md`

## Summary

- Added one side-effect-free `entry_transition_actions` helper. Both service enforcement and rendered transition controls call it. Ordinary targets evaluate `transition_owned` and `transition` as an explicit union; `shortlist`, `hold`, and `rejected` retain only their respective approve, hold, and reject grants.
- Added `_require_any` at the service boundary so an actual `transition_entry` authorises the exact target resource through any independently applicable explicit action. The integration witness uses an analyst+approver non-owner principal to transition a TEAM entry successfully via the approver grant, despite its inapplicable analyst owner grant.
- Replaced shortlist/entry scout-role branching with shared union read decisions: `shortlist.read` is evaluated first; only then can the exact current-entry assignment satisfy `shortlist.read_assigned`. The shortlist route uses that same decision before rendering, and entry rows remain filtered by it.
- Added route witnesses for analyst+scout owner TEAM and OWNER_ONLY empty shortlists, approver+scout TEAM read without assignment, and scout-only current/unassigned/former/cross-tenant outcomes. Exact-link replay checks are unchanged.

## Decision matrices

### Read decision

| Principal / resource | Result |
| --- | --- |
| Analyst+scout owner, TEAM or OWNER_ONLY shortlist | allow through explicit `shortlist.read`, including no-entry shortlist |
| Approver+scout, TEAM shortlist | allow through explicit `shortlist.read` without scout assignment |
| Scout only, current exact entry assignment | allow shortlist and entry through `shortlist.read_assigned` |
| Scout only, unassigned or former entry | generic 404 |
| Scout only, private non-owner or foreign tenant | generic 404 |

### Transition decision

| Target / principal | Result |
| --- | --- |
| Ordinary target, analyst owner | allow through `shortlist_entry.transition_owned` |
| Ordinary target, approver (including analyst+approver non-owner) | allow through `shortlist_entry.transition` |
| Ordinary target, analyst non-owner alone | deny |
| `shortlist` | only `shortlist_entry.approve` |
| `hold` | only `shortlist_entry.hold` |
| `rejected` | only `shortlist_entry.reject_with_reason` |

## R3 probe and boundary witnesses

| Probe | Before | After |
| --- | --- | --- |
| Analyst+scout owner requests empty TEAM shortlist | policy `shortlist.read`: true; route: 404 | policy-granted route: 200 |
| Analyst+scout owner requests empty OWNER_ONLY shortlist | role-presence branch could require an entry | route: 200 via owner’s explicit `shortlist.read` |
| Approver+scout requests TEAM shortlist with no scout assignment | scout presence could force assigned-only path | route: 200 via approver’s explicit `shortlist.read` |
| Analyst+approver non-owner ordinary transition | analyst role could select owned-only action and deny | actual service `transition_entry`: succeeds via approver `transition` |

The route matrix explicitly retains scout-only unassigned and former-assignee 404s, current-assignee shortlist/entry 200s, and foreign-tenant brief/shortlist/entry 404s. The retained private non-owner scout 404 and exact-link replay visibility matrix continue to pass.

## Tests run

- `uv run ruff format --check src/scouting/workflow/r1.py src/scouting/web/w08.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py tests/integration/test_w08_local_workflow_app.py`
  - exit status: 0
  - result: 5 files already formatted.
- `uv run ruff check src/scouting/workflow/r1.py src/scouting/web/w08.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py tests/integration/test_w08_local_workflow_app.py`
  - exit status: 0
  - result: all checks passed.
- `uv run mypy src/scouting/workflow/r1.py src/scouting/web/w08.py`
  - exit status: 0
  - result: success; no issues in 2 source files.
- `uv run pytest -q tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_auth_audit.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: 33 passed; one existing third-party Starlette TestClient deprecation warning; 5.30s.
- `uv run bandit -q src/scouting/workflow/r1.py src/scouting/web/w08.py`
  - exit status: 0
  - result: no findings.

## Artifacts/evidence

- `tests/integration/test_w08_workflow.py::test_synthetic_automated_role_brief_to_observation_journey`
- `tests/security/test_w08_workflow_access.py::test_ordinary_transition_uses_any_applicable_explicit_grant`
- `tests/security/test_w08_workflow_access.py::test_special_transition_targets_keep_their_sole_grant`
- `tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_scout_brief_and_replay_authorization_matrix`
- `reports/reviews/W08/returns/W08-MULTIROLE-SHORTLIST-AUTHZ-04Q-R1.md`

## Risks

- This is synthetic automated mechanics/security evidence only; it does not satisfy the five-person representative-user gate.
- The shared helper is intentionally limited to transition action selection; policy evaluation remains the sole authority for tenant, visibility, owner, and current-assignment constraints.

## Follow-up items

- Fresh independent security review and master reproduction are required before acceptance.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no protected-output inspection, participant-evidence creation, external activity, or out-of-scope audit/export/configuration change: confirmed.

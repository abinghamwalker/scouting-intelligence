# W08-WORKFLOW-INTEGRITY-02B-R2 return — COMPLETE

## Task and exact identity-role invariant

Decision fields must name the authenticated approver, and every non-null scout
assignment must name an enabled account with an explicit `scout` role in the same local
tenant. Initial longlist creation is always unassigned.

## Exact changed files

- `src/scouting/workflow/r1.py`
- `tests/integration/test_w08_workflow.py`
- `reports/reviews/W08/returns/W08-WORKFLOW-INTEGRITY-02B-R2.md`

## Positive and negative proof

- `APPROVED` and `REJECTED` role-brief revisions now require both `created_by` and
  `decided_by` to equal the authenticated approver before the container/revision/audit
  mutation. A forged `decided_by` is denied.
- Initial `LONGLIST` entry creation rejects any `assigned_scout_id`; assignment is
  possible only through a later immutable revision.
- Every later non-null assignment is resolved with one tenant-scoped account/role
  lookup requiring `enabled=1` and `role='scout'`. The outward failure is the generic
  `R1AuthorizationDenied`, without revealing whether account existence, tenant,
  enabled status or role caused the denial.
- The synthetic journey retains a valid assigned scout path. It additionally proves
  denial before mutation for a disabled scout, wrong-tenant lookup scope, analyst-only,
  approver-only, admin-only and unknown actors, plus attempted initial assignment.
  Existing role/entry attribution, chain identity, reconsideration, rollback and W06
  claim-boundary witnesses remain green.

Fixtures are still `synthetic_automated_test`; they are not real scout evidence. W06
remains `NO_GO` solely for `MISSING_EXPERT_RELEVANCE_EVIDENCE`, with
`resemblance_only`, `synthetic_development_only`, and `LIMITED` applicability.

## Commands and results

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | 4 files formatted |
| `uv run ruff check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | passed |
| `uv run mypy src/scouting/workflow/r1.py src/scouting/observations/r1.py` | 0 | success, 2 source files |
| `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py tests/security/test_w08_auth_audit.py` | 0 | 22 passed in 0.68s |

## Residual risks and boundary confirmations

Independent security review and representative-user moderated evidence remain outside
this producer packet. No Git operation, dependency/lock change, external access,
protected-output access, destructive action, or edit outside the allowlist occurred.

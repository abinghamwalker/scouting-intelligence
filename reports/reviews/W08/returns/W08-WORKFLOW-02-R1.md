# W08-WORKFLOW-02-R1 return — STOPPED

## Objective

Implement the transactional local R1 role-brief, retrieval-link, shortlist, comment,
and scout-observation workflow over the master-owned contracts and migration.

## Exact changed files

- `src/scouting/workflow/r1.py`
- `src/scouting/workflow/__init__.py`
- `src/scouting/observations/r1.py`
- `src/scouting/observations/__init__.py`
- `tests/integration/test_w08_workflow.py`
- `tests/security/test_w08_workflow_access.py`
- `reports/reviews/W08/returns/W08-WORKFLOW-02-R1.md`

## Implemented behaviour and choices

- Added transactional role-brief drafts/submission/approval transitions, immutable
  revisions, replay links pinned to `resemblance_only`,
  `synthetic_development_only`, `LIMITED`, and an explicit W06
  `NO_GO`/`MISSING_EXPERT_RELEVANCE_EVIDENCE` limitation.
- Added shortlist creation, longlist addition, legal state transition enforcement,
  optimistic lock checks, immutable revision inserts, synthetic-only comments, and
  audit receipt writes inside nested transactions so an audit failure rolls back the
  material write.
- Added assigned-scout, private/team visibility-aware observation creation,
  amendment/version history, structured rubric/confidence/local evidence references,
  disagreement, and audit receipts. Test fixtures are explicitly
  `synthetic_automated_test`; no fixture is presented as a real scout judgement.
- Added positive journey, stale-write/no-partial-mutation, audit-failure rollback and
  retry, IDOR/cross-object denial, scout/approver separation, and private visibility
  tests.

## Stop condition — master decision required

The required **new linked entry reconsideration** after a `REJECTED` shortlist entry
cannot be implemented faithfully within this packet. The master-owned migration has
`UNIQUE (tenant_id, shortlist_id, player_id)` on `shortlist_entry_workflows` and does
not contain a `previous_entry_id`/reconsideration linkage. The master-owned contract
also has no linkage field. Therefore a new entry for the same candidate cannot be
stored or linked without a migration/contract change, both forbidden to this packet.

The implementation intentionally leaves `REJECTED` terminal rather than inventing a
link in rationale text or silently replacing history. The smallest sound correction is
a master-owned migration and contract extension for a nullable immutable predecessor
entry identifier (and a revised uniqueness rule that permits a later reconsideration
entry while retaining one active candidate entry), followed by a narrowly revised
workflow packet.

## Commands and results

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check src/scouting/workflow/r1.py src/scouting/observations/r1.py` | 0 | formatted |
| `uv run ruff check src/scouting/workflow/r1.py src/scouting/observations/r1.py` | 0 | passed |
| `uv run mypy src/scouting/workflow/r1.py src/scouting/observations/r1.py` | 0 | passed |
| `uv run pytest -q tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | 5 passed |
| `uv run ruff format --check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | formatted |
| `uv run ruff check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | passed |
| `uv run mypy src/scouting/workflow/r1.py src/scouting/observations/r1.py` | 0 | passed |
| `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py tests/security/test_w08_auth_audit.py` | 0 | 14 passed |

## Evidence and identifiers

- Synthetic journey: `tests/integration/test_w08_workflow.py::test_synthetic_automated_role_brief_to_observation_journey`
- Audit rollback/retry: `tests/integration/test_w08_workflow.py::test_audit_failure_rolls_back_material_write_and_retry_recovers`
- Object access denial: `tests/security/test_w08_workflow_access.py::test_cross_object_and_role_escalation_are_denied`
- Stop-condition evidence: `migrations/versions/0002_w08_workflow.sql` table
  `shortlist_entry_workflows`, unique candidate constraint; no linked predecessor
  column in either relevant table.

## Residual risks and follow-up

- Do not accept this packet until the master resolves the reconsideration schema/
  contract conflict and a revised packet tests that invariant.
- Independent security review must still inspect the producer changes after the
  correction.

## Boundary confirmations

No Git operation was run. No dependency or lock file was changed. No path outside the
packet allowlist was edited. No protected W06 output was accessed, and no external
service, model call, provider, or remote was used.

# W08-WORKFLOW-02-R2 return — COMPLETE

## Objective

Complete the local R1 workflow under the narrowed invariant that reconsideration of a
rejected candidate appends immutable revision `N+1` to the same shortlist entry.

## Exact changed files in R2

- `src/scouting/workflow/r1.py`
- `tests/integration/test_w08_workflow.py`
- `reports/reviews/W08/returns/W08-WORKFLOW-02-R2.md`

## Behaviour and invariant proof

- Added exactly one legal entry transition: `REJECTED -> LONGLIST`. It uses the
  existing `shortlist_entry_id`, increments `revision` and `lock_version`, and writes
  a new append-only audit receipt. The rejected revision and its controlled reason are
  retained unchanged.
- Reconsideration requires a non-empty contract-validated transition reason and
  requires `changed_by` to be the authenticated principal. It cannot silently
  attribute a human action to another actor.
- Every entry transition now rejects any attempt to rewrite its shortlist, player,
  role-brief/version, replayable retrieval link, or owner. A second entry for the
  same shortlist/player is explicitly denied before a database mutation.
- The synthetic automated journey proves revisions
  `longlist -> scout -> rejected -> longlist` on one entry ID, keeps the rejection
  reason and player ID, rolls back a forced audit failure without advancing the
  container, retries to append exactly one revision/receipt, rejects a stale retry,
  and denies duplicate entry creation. Fixtures remain
  `synthetic_automated_test`; no assertion is real scout evidence.
- Replay links retain the W06 claim boundary: `NO_GO`, sole
  `MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`,
  `synthetic_development_only`, and `LIMITED`.

## Commands and results

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | four files formatted |
| `uv run ruff check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | passed |
| `uv run mypy src/scouting/workflow/r1.py src/scouting/observations/r1.py` | 0 | success, 2 source files |
| `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py tests/security/test_w08_auth_audit.py` | 0 | 15 passed in 0.61s |

## Evidence identifiers

- Reconsideration, duplicate, stale and audit-retry witness:
  `tests/integration/test_w08_workflow.py::test_synthetic_automated_role_brief_to_observation_journey`
- Separate material-action rollback/retry witness:
  `tests/integration/test_w08_workflow.py::test_audit_failure_rolls_back_material_write_and_retry_recovers`
- Cross-object, role-escalation and private-visibility witnesses:
  `tests/security/test_w08_workflow_access.py`

## Residual risks and follow-ups

- This is tested local workflow mechanics only. It is not representative-user,
  moderated-study, expert-relevance, recommendation, outcome, price/value, or
  production evidence.
- Independent review must inspect the complete R1 implementation and the narrowed
  same-entry reconsideration invariant before master acceptance.

## Boundary confirmations

No Git operation was run. No dependency or lock file was changed. No edit was made
outside this packet's allowlist. No protected W06 output, external service, model call,
provider, remote, or destructive action was used.

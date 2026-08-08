# W08-WORKFLOW-INTEGRITY-02B-R1 return — COMPLETE

## Task and invariant

Prove that the authenticated principal, pinned approved brief/retrieval chain, and
candidate/observation identity cannot diverge across any local R1 workflow revision.

## Exact changed files

- `src/scouting/workflow/r1.py`
- `src/scouting/observations/r1.py`
- `tests/integration/test_w08_workflow.py`
- `reports/reviews/W08/returns/W08-WORKFLOW-INTEGRITY-02B-R1.md`

## Corrections and adversarial proof

- Role-brief creation and every role-brief transition now require `created_by` to be
  the authenticated principal. Shortlist-entry creation and every entry transition
  require `changed_by` to be that principal. Observation creation/amendment requires
  `author_id` to be that principal.
- Initial entry creation proves one persisted, same-tenant chain: shortlist owner and
  role-brief/version match the revision; that brief is approved; and its retrieval
  link exists and names the same role-brief/version. The existing later-revision
  identity checks retain shortlist/player/brief version/retrieval link/owner.
- Observation amendments now retain the prior observation's entry ID, author and
  `evidence_origin`; a synthetic automated observation cannot be moved to another
  candidate or laundered into `human_entered_local` evidence.
- Submit, approve, reject and retire transitions compare the full replayable brief
  interpretation (owner, visibility, title/template/taxonomy, responsibilities,
  constraints, preferences and exemplars) with the immediately prior revision.
  They are status-only transitions; substantive edits require a new draft revision.
- The synthetic adversarial witness attempts forged entry attribution, a persisted
  shortlist/brief/retrieval mismatch, observation movement/provenance laundering,
  approval-content rewrite and forged brief creator. Each is rejected before writes;
  revision, observation and audit-receipt counts remain unchanged. Existing forced
  audit failure/retry witnesses remain green.

All fixtures remain explicitly `synthetic_automated_test`. The W06 boundary remains
`NO_GO` solely for `MISSING_EXPERT_RELEVANCE_EVIDENCE`, with
`resemblance_only`, `synthetic_development_only`, and `LIMITED`; nothing here is human
or expert evidence.

## Commands and results

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | 4 files formatted |
| `uv run ruff check src/scouting/workflow/r1.py src/scouting/observations/r1.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py` | 0 | passed |
| `uv run mypy src/scouting/workflow/r1.py src/scouting/observations/r1.py` | 0 | success, 2 source files |
| `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/integration/test_w08_workflow.py tests/security/test_w08_workflow_access.py tests/security/test_w08_auth_audit.py` | 0 | 15 passed in 0.60s |

## Evidence and residual follow-up

- Adversarial identity/provenance witness:
  `tests/integration/test_w08_workflow.py::test_synthetic_automated_role_brief_to_observation_journey`.
- Audit rollback/retry witness:
  `tests/integration/test_w08_workflow.py::test_audit_failure_rolls_back_material_write_and_retry_recovers`.
- Independent security review is still required before master acceptance. Automated
  evidence does not satisfy the later representative-user moderated-study gate.

## Boundary confirmations

No Git operation, dependency or lock change, external access, protected-output access,
or destructive action occurred. No file outside the packet allowlist was edited.

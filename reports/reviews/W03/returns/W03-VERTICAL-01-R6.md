# Subagent return

## Task

- task_id: W03-VERTICAL-01-R6
- objective: Make all silent material journey insert conflicts enforce persisted
  ownership and immutable content while preserving exact canonical replay.

## Files changed

- src/scouting/workflow/service.py
- tests/e2e/test_w03_vertical_journey.py
- reports/reviews/W03/returns/W03-VERTICAL-01-R6.md

## Summary

- Converted role-brief, retrieval-run, candidate-result, shortlist and shortlist-entry
  persistence to insert-or-verify behavior inside the existing transaction.
- Every material insert now uses `ON CONFLICT ... DO NOTHING RETURNING`. A conflict
  triggers a tenant-visible database comparison of every immutable stored column using
  `IS NOT DISTINCT FROM`.
- Comparisons cover tenant, owner where present, trace, version, relationships,
  timestamps, status/state, title and rationale, model/index/lineage identifiers,
  player/rank/score/confidence, claim boundary and canonical JSONB content.
- A hidden, absent or mismatched conflict row raises the existing
  `PermissionError("action denied")`. The unchanged web boundary maps this to the
  existing generic `403 {"detail":"action denied"}` response.
- Retrieval, candidate and shortlist-entry inserts use untargeted conflict suppression
  so alternate unique-key collisions are also verified by canonical ID and denied when
  no exact canonical row exists.
- Because verification remains inside the existing journey transaction, a late
  shortlist or entry mismatch rolls back earlier role-brief, retrieval, candidate and
  audit writes.
- Exact same-owner, same-content replay is accepted without duplicating any material
  row; each separately requested successful material action retains its own four
  append-only audit events.
- Extended the existing e2e harness with a second same-tenant analyst and added focused
  role-brief, shortlist and shortlist-entry collision regressions. Each proves generic
  denial, unchanged victim ownership and zero attacker role-brief, retrieval,
  candidate, shortlist, entry and audit effects.
- Added an explicit exact canonical replay regression proving one stored row at every
  material boundary and four audit events for each of two successful requests.
- The unchanged independent reviewer collision test now passes.

## Tests run

- command: `uv run ruff format src/scouting/workflow tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: 1 file reformatted; 2 files unchanged.
- command: `uv run ruff check src/scouting/workflow tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/workflow`
  - exit status: 0
  - result: no issues found in 2 source files.
- command: `SCOUTING_DATABASE_URL='<redacted master-supplied loopback URL>' uv run pytest -q tests/e2e/test_w03_vertical_journey.py tests/security/test_w03_boundary_audit.py`
  - exit status: 0
  - result: 53 passed; one existing Starlette/httpx deprecation warning.
- command: `uv run ruff format --check src/scouting/workflow tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/workflow tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/workflow`
  - exit status: 0
  - result: no issues found in 2 source files.
- command: `uv run bandit -q -r src/scouting/workflow`
  - initial sandbox exit status: 2
  - initial result: restricted sandbox could not read an existing uv cache path.
  - approved rerun exit status: 0
  - approved rerun result: no findings.
- command: `! rg -n "expected_retrieval\\.json" src/scouting/workflow`
  - exit status: 0
  - result: no runtime reference found.
- command: `rg -n "ON CONFLICT|_require_exact_persisted_row|RETURNING (role_brief_id|retrieval_run_id|candidate_result_id|shortlist_id|shortlist_entry_id)" src/scouting/workflow/service.py`
  - exit status: 0
  - result: all five material conflict sites have `RETURNING` and exact-row
    verification.

## Artifacts/evidence

- reports/reviews/W03/returns/W03-VERTICAL-01-R6.md
- unchanged reviewer regression:
  `test_same_tenant_existing_brief_owner_collision_is_denied`
- new collision regression:
  `test_same_tenant_material_owner_collisions_deny_and_roll_back`
  - role-brief collision
  - shortlist collision
  - shortlist-entry collision
- new replay regression:
  `test_exact_same_owner_material_replay_is_idempotent`
- combined database-backed result: 53 passed.

## Risks

- Conflict verification compares the complete currently persisted immutable schema. A
  later migration that adds a new immutable material column must extend the matching
  workflow comparison in the same change.
- Exact replays preserve one material row but intentionally append audit events for
  distinct successful API requests; this records each human material action rather
  than silently suppressing it.
- PostgreSQL and the existing tenant-local application-role transaction remain the
  authority. This packet does not claim general concurrency, penetration-test,
  production-security or real-data evidence.
- No protected fixture or protected expected output was accessed. The master retains
  the protected gate and all acceptance authority.
- TestClient continues to emit the existing upstream Starlette/httpx deprecation
  warning. Dependency changes are outside this packet.

## Follow-up items

- Master independently inspect the complete comparisons, reproduce the packet checks
  and decide the W03 gate. No implementation follow-up is claimed by this subagent.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no Docker operations: confirmed; no Docker command was run.
- no delegation: confirmed.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no migrations, contracts, policies, configs, web, reviewer test/report,
  orchestration or fixture edits: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no protected fixture or protected expected-output access: confirmed.
- no scripts or `reports/verification/W03` access: confirmed.
- no external service, public bind or destructive action: confirmed.
- no self-approval or gate claim: confirmed.

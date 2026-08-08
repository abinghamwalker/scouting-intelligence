# Subagent return

## Task

- task_id: `W08-REPLAY-CONTRACT-02C`, revision `R1`
- objective: retain exactly one truthful replay-query mode in a W08 retrieval link.

## Files changed

- `src/scouting/contracts/workflow.py`
- `migrations/versions/0002_w08_workflow.sql`
- `src/scouting/workflow/r1.py`
- `src/scouting/operations/evidence_export.py`
- `tests/contracts/test_w08_workflow_contracts.py`
- `tests/integration/test_w08_evidence_export.py`
- `tests/security/test_w08_export_boundaries.py`
- `reports/reviews/W08/returns/W08-REPLAY-CONTRACT-02C-R1.md`

## Summary

- `ReplayableRetrievalLink.query_player_id` is now optional and
  `exemplar_player_ids` is an immutable tuple. Its validator admits exactly one mode:
  a player with no exemplars, or a non-empty unique exemplar set with no player.
- The SQLite retrieval-link row mirrors these fields: nullable player, required JSON
  exemplar array, valid-array check and an exact-one-mode check. Player-query fixtures
  explicitly persist `[]` rather than relying on positional column order.
- `R1WorkflowService` inserts both fields in one append-only link row, so its existing
  model-dump audit digest carries the complete selected mode. `LocalEvidenceExporter`
  decodes `exemplar_player_ids` alongside limitations, preserving canonical underlying
  values rather than an opaque JSON string.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/workflow.py src/scouting/workflow/r1.py src/scouting/operations/evidence_export.py tests/contracts/test_w08_workflow_contracts.py tests/integration/test_migrations.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: 8 files already formatted.
- command: `uv run ruff check src/scouting/contracts/workflow.py src/scouting/workflow/r1.py src/scouting/operations/evidence_export.py tests/contracts/test_w08_workflow_contracts.py tests/integration/test_migrations.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/workflow.py src/scouting/workflow/r1.py src/scouting/operations/evidence_export.py`
  - exit status: 0
  - result: success; no issues in 3 source files.
- command: `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/integration/test_migrations.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: 27 passed.

## Artifacts/evidence

- Contract witness covers player mode, exemplar mode, neither, both and duplicate
  exemplar rejection. The export witness persists an exemplar-only SQL row and proves
  its ordered IDs export as a decoded canonical list (and player mode fixtures retain
  explicit `[]`). Migration/integration/export/security suites remain green.

## Risks

- SQLite validates JSON shape and exact-one mode; canonical UUID validation and
  duplicate prevention are fail-closed in the contract before service/audit insertion.
  A subsequent web packet must supply exact replay inputs, never substitute one exemplar
  as a query player. W06 claims remain unchanged.

## Follow-up items

- Fresh independent review and master reproduction; then resume the blocked brief replay
  packet under this corrected contract.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no protected-output access: confirmed
- no edits outside `allowed_paths`: confirmed

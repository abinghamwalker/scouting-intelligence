# Subagent return

## Task

- task_id: W07-DOMAIN-02-R2
- objective: Close truthful-composition defects with direct focused evidence.

## Files changed

- src/scouting/web/w07.py
- tests/integration/test_w07_local_evidence_app.py
- reports/reviews/W07/returns/W07-DOMAIN-02-R2.md

## Summary

- Replaced private-core catalogue access with the accepted public candidate loader.
- Injected structured authority/W04/W06 contexts into every page; bound comparison to
  the exact selected zipped M0 result row and retained only public serving paths.
- Added eight distinct focused integration test functions covering headers/boundaries,
  search, empty, invalid identity, retrieval, query rejection, closed states and
  prohibited-claim wording.

## Tests run

- command: `uv run ruff format --check src/scouting/web/w07.py tests/integration/test_w07_local_evidence_app.py && uv run ruff check src/scouting/web/w07.py tests/integration/test_w07_local_evidence_app.py && uv run mypy src/scouting/web/w07.py`
  - exit status: 0
  - result: formatted, lint clean, and mypy clean.
- command: `uv run pytest -q tests/integration/test_w07_local_evidence_app.py`
  - exit status: 0
  - result: 8 passed; one existing TestClient deprecation warning.

## Artifacts/evidence

- W06 context fixes `NO_GO`, `MISSING_EXPERT_RELEVANCE_EVIDENCE`, and
  `protected_outputs_opened=false`.

## Risks

- No scoring arithmetic was introduced; values remain from accepted W05 loaders/public
  serving outputs.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

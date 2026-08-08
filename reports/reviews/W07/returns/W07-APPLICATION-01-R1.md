# Subagent return

## Task

- task_id: W07-APPLICATION-01-R1
- objective: Implement the bounded local W07 evidence application.

## Files changed

- src/scouting/web/w07.py
- src/scouting/web/__init__.py
- services/api/w07_main.py
- apps/web/templates/w07/landing.html
- apps/web/templates/w07/retrieval.html
- apps/web/templates/w07/evidence.html
- apps/web/static/w07/app.css
- tests/integration/test_w07_local_evidence_app.py
- tests/e2e/test_w07_local_evidence_playwright.py
- reports/reviews/W07/returns/W07-APPLICATION-01-R1.md

## Summary

- Local read-only evidence surfaces wrap only the public M0 request and batch paths.

## Tests run

- command: uv run ruff format --check ... && uv run ruff check ... && uv run mypy ... && uv run pytest ... && uv run lint-imports
  - exit status: 2
  - result: stopped before checks because uv could not open `/Users/adrian/.cache/uv/sdists-v9/.git` (Operation not permitted).
- command: uv run pytest -q tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py
  - exit status: 1, then corrected forbidden wording; rerun blocked by the same uv cache permission failure.

## Artifacts/evidence

- src/scouting/web/w07.py

## Risks

- Focused verification remains required because the managed sandbox denies uv access to its cache metadata.

## Follow-up items

- Re-run the packet acceptance checks in an environment where uv can read its locked cache.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

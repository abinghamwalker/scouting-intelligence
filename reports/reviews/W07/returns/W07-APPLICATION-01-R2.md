# Subagent return

## Task

- task_id: W07-APPLICATION-01-R2
- objective: Correct the W07 application P1 findings and prove a local browser journey.

## Files changed

- src/scouting/web/w07.py
- src/scouting/web/__init__.py
- apps/web/templates/w07/landing.html
- apps/web/templates/w07/search.html
- apps/web/templates/w07/player.html
- apps/web/templates/w07/result.html
- apps/web/templates/w07/state.html
- apps/web/templates/w07/evidence.html
- tests/e2e/test_w07_local_evidence_playwright.py
- tests/integration/test_w07_local_evidence_app.py
- reports/reviews/W07/returns/W07-APPLICATION-01-R2.md

## Summary

- Mounted bounded local CSS, added the complete local evidence route set and explicit
  states, and preserved the W03 exports with one W07 factory export.
- Retrieval uses only `serve_m0_request`; comparison uses only `serve_m0_batch`.
  Templates expose pinned identities, resemblance geometry, contribution evidence,
  W04’s four exact count values and the W06 NO_GO boundary.
- The browser witness uses `playwright.sync_api` with the existing local Chrome binary,
  real loopback uvicorn, desktop/mobile viewports, keyboard activation and external
  request interception.

## Tests run

- command: `uv run ruff format --check src/scouting/web/w07.py src/scouting/web/__init__.py services/api/w07_main.py tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py`
  - exit status: 0
  - result: 5 files already formatted.
- command: `uv run ruff check src/scouting/web/w07.py src/scouting/web/__init__.py services/api/w07_main.py tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/web/w07.py src/scouting/web/__init__.py services/api/w07_main.py`
  - exit status: 0
  - result: success; no issues in 3 source files.
- command: `uv run pytest -q tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py`
  - exit status: 0
  - result: 9 passed; one existing TestClient deprecation warning.
- command: `uv run lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken.

## Artifacts/evidence

- accepted result digest: `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`
- accepted lineage: `c291a1b99937100b9934537dc92d4628cd130684cc84388f8aebe109708e7491`
- browser: existing `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

## Risks

- The application remains local-only, synthetic-development-only and NO_GO; it makes
  no validation, recommendation, outcome or production claim.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

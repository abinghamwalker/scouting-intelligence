# Subagent return

## Task

- task_id: W07-DOMAIN-02-R1
- objective: Prove truthful W07 composition from accepted local authorities and the public W05 serving path.

## Files changed

- src/scouting/web/w07.py
- reports/reviews/W07/returns/W07-DOMAIN-02-R1.md

## Summary

- Authorities are built once at app creation and the accepted 18-row local candidate
  catalogue is the sole search/player identity source.
- Search has bounded query/position filters; malformed or unknown player, query and
  comparison identities return explicit unavailable evidence without scorer invocation.
- Query retrieval calls only `serve_m0_request`; a selected query/candidate comparison
  calls only `serve_m0_batch` and rejects candidates absent from its returned rows.
- Evidence states are closed (`loading`, `empty`, `unavailable`, `error`, `no-go`),
  unknown states return 404, and CSP/no-store/referrer protections are added.

## Tests run

- command: `uv run ruff check src/scouting/web/w07.py src/scouting/web/__init__.py services/api/w07_main.py tests/integration/test_w07_local_evidence_app.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/web/w07.py src/scouting/web/__init__.py services/api/w07_main.py`
  - exit status: 0
  - result: success; no issues in 3 source files.
- command: `uv run pytest -q tests/integration/test_w07_local_evidence_app.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py`
  - exit status: 0
  - result: 7 passed; one existing TestClient deprecation warning.

## Artifacts/evidence

- public serving paths: `serve_m0_request`, `serve_m0_batch`
- W06 decision: `NO_GO`, `MISSING_EXPERT_RELEVANCE_EVIDENCE`, protected outputs unopened.

## Risks

- Presentation templates remain separately owned; this packet provides their complete
  governed route/context surface without accessing protected evidence.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

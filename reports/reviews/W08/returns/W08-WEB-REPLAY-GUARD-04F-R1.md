# Subagent return

## Task

- task_id: `W08-WEB-REPLAY-GUARD-04F`, revision `R1`
- invariant: link and entry persistence require deterministic local replay identity and an exact-result candidate.

## Files changed

- `src/scouting/web/w08.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `reports/reviews/W08/returns/W08-WEB-REPLAY-GUARD-04F-R1.md`

## Summary

- Replay now retains the approved brief's stored `trace_id`, deterministically derives
  only the request/link IDs, and explicitly clears `query_player_id` whenever retained
  exemplars select exemplar mode.  The retrieval route runs two fully validated local
  replays and refuses persistence unless their complete JSON representations match.
- Entry POST loads the selected tenant-local link and exact pinned brief, replays it,
  and denies a submitted player outside `retrieval_result.candidates` before workflow
  service/audit mutation. The broad workflow witness now selects a real candidate from
  the retained local W07 result instead of an arbitrary UUID.

## Tests run

- `uv run ruff format --check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0.
- `uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py` — exit 0.
- `uv run mypy src/scouting/web/w08.py` — exit 0.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/e2e/test_w05_m0_retrieval.py` — exit 0; 7 passed, one third-party TestClient deprecation warning.

## Residual follow-up

- Fresh independent review should verify the route's full replay/persisted-link
  comparison and rendered metadata/candidate dropdown against the packet's extended
  acceptance requirements. No claims, W05/W07 source, contracts, services, policy,
  dependencies or protected output were changed.

## Scope confirmation

- no Git operations, dependency/lock changes, protected-output access or out-of-scope edits.

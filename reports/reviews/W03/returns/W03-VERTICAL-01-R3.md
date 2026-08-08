# Subagent return

## Task

- task_id: W03-VERTICAL-01-R3
- objective: Correct only the three vertical-boundary defects recorded in
  `REVIEW-W03-VERTICAL-01-PROTECTED-R1`.

## Files changed

- src/scouting/serving/synthetic.py
- tests/e2e/test_w03_vertical_journey.py
- reports/reviews/W03/returns/W03-VERTICAL-01-R3.md

## Summary

- Candidate selection no longer names or filters for the development metric. It first
  applies the role brief's supported hard constraints, request exclusions, and
  ambiguity quarantine, then ranks admitted facts with a deterministic tie-break.
- Candidate reason codes and explanation text are derived from the selected metric and
  player position. The reviewed development response remains byte-equal to its
  existing oracle.
- Retrieval result and run IDs are deterministically and bijectively derived from the
  retrieval request ID using separate UUID-domain offsets. The development request
  retains its reviewed IDs, identical requests are stable, and distinct request IDs
  produce distinct IDs.
- All source-manifest, feature-schema, model-artifact, and retrieval-index observation
  and availability timestamps are explicit fields on `SyntheticArtifactCatalog`.
  Lineage construction now consumes only snapshot/catalog data.
- Added a temporary development-derived envelope marked `protected_test` that changes
  the metric, request ID, catalog identifiers/digests/timestamps, exclusion, and
  competing fact values. It verifies hard constraints, exclusions, ambiguity
  quarantine, alternate-metric selection, repeated-call stability, distinct
  request-bound IDs, and exact catalog-backed lineage.
- Existing tests continue to prove explicitly unavailable model/index behavior without
  fallback.

## Tests run

- command: `uv run ruff format src/scouting/serving tests/e2e/test_w03_vertical_journey.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: 2 files reformatted; 2 files unchanged.
- command: `uv run ruff check src/scouting/serving tests/e2e/test_w03_vertical_journey.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/serving`
  - exit status: 0
  - result: no issues found in 2 source files.
- command: `SCOUTING_DATABASE_URL='<redacted master-supplied loopback URL>' uv run pytest -q tests/e2e/test_w03_vertical_journey.py tests/security/test_application_authorization.py`
  - initial sandbox attempt exit status: 2
  - initial result: the restricted sandbox could not read an existing uv cache path.
  - approved rerun exit status: 0
  - approved rerun result: 21 passed; one existing Starlette/httpx deprecation
    warning.
- command: `uv run ruff format --check src/scouting/serving tests/e2e/test_w03_vertical_journey.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: 4 files already formatted.
- command: `uv run ruff check src/scouting/serving tests/e2e/test_w03_vertical_journey.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/serving`
  - exit status: 0
  - result: no issues found in 2 source files.
- command: `uv run bandit -q -r src/scouting/serving`
  - initial sandbox attempt exit status: 2
  - initial result: the restricted sandbox could not read an existing uv cache path.
  - approved rerun exit status: 0
  - approved rerun result: no findings.
- command: `! rg -n "expected_retrieval\\.json" src/scouting/serving`
  - exit status: 0
  - result: no runtime reference found.

## Artifacts/evidence

- reports/reviews/W03/returns/W03-VERTICAL-01-R3.md
- tests/e2e/test_w03_vertical_journey.py
- alternate fixture ID: `w03-temporary-alternate-partition`
- alternate partition: `protected_test`
- alternate metric: `alternate_signal_per_90`
- alternate request IDs:
  `c0000000-0000-4000-8000-000000000202` and
  `c0000000-0000-4000-8000-000000000203`
- development oracle assertion remains unchanged and passed.

## Risks

- The selection seam compares the numeric values supplied by the synthetic fixture; it
  does not claim cross-provider metric calibration, model quality, expert relevance,
  pilot readiness, or recruitment outcome quality.
- Hard-constraint evaluation is deliberately fail-closed outside the bounded supported
  player fields and categorical operators.
- No protected fixture or protected expected output was accessed. The master still
  owns independent review and any brokered protected-input gate.
- TestClient continues to emit the existing upstream Starlette/httpx deprecation
  warning. Dependency changes are outside this packet.

## Follow-up items

- Master independently review the R3 changes, rerun the bounded checks, and broker any
  protected-input gate without exposing protected expected output to the implementer.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no Docker operations: confirmed; no Docker command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.
- no access to protected fixture/output paths: confirmed.
- no writes to `reports/verification/W03`: confirmed.
- no self-approval or protected-gate claim: confirmed.

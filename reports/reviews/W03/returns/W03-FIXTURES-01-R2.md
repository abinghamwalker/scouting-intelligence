# Subagent return

## Task

- task_id: `W03-FIXTURES-01`
- objective: Correct `OBSERVATION_AT_CUTOFF_ADMITTED` without changing the frozen
  fixtures or any contract, dependency, storage, database, or application surface.

## Files changed

- `src/scouting/sources/synthetic.py`
- `tests/unit/test_synthetic_fixture.py`
- `reports/reviews/W03/returns/W03-FIXTURES-01-R2.md`

## Summary

- Added an explicit strict-before observation boundary to the raw fact admission path.
  Facts with `observed_at >= decision_cutoff_ts` cannot enter `admitted_facts`.
- Added the stable rejection reason `post_cutoff_observation`, distinct from
  `post_cutoff_availability` and `missing_temporal_evidence`.
- Preserved the fixture expectation invariant: a fixture that marks an at/after-cutoff
  observation as admissible is rejected as malformed rather than silently changing its
  expected outcome.
- Added focused tests for observation exactly equal to the cutoff, observation after the
  cutoff, availability earlier than both unsafe observation times, and the distinct
  rejection reason.
- Existing digest assertions passed unchanged:
  - development domain:
    `03972808bd6628dd4ffb66a975108bb15f649a0b778e493c85874ef107953e2a`
  - development expected:
    `f0948134aa0b02595e2974ff6ca264496db401c68d937bf8b8d594561f57e0e9`
  - protected domain:
    `51f56f2bc9d88196e1b37b6f28c9879a1cdc4ee4db5727a955c5c188b9bfbd7f`
  - protected expected:
    `9c3c0b65d53e8a4fefdd160ba38b1bf016671cf0aaa97d7fdc08c3a238b4fdf6`

## Tests run

- command: `uv run pytest -q tests/unit/test_synthetic_fixture.py`
  - exit status: `0`
  - result: `10 passed`
- command:
  `uv run ruff format --check src/scouting/sources tests/unit/test_synthetic_fixture.py`
  - exit status: `0`
  - result: `3 files already formatted`
- command: `uv run ruff check src/scouting/sources tests/unit/test_synthetic_fixture.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/sources`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run bandit -q -r src/scouting/sources`
  - first sandboxed exit status: `2`
  - first result: uv could not read `/Users/adrian/.cache/uv/sdists-v9/.git` under the
    workspace sandbox; this was an environment permission failure before Bandit ran.
  - final escalated exit status: `0`
  - final result: no Bandit findings
- command:
  `UV_CACHE_DIR=/private/tmp/w03-fixture-r2-uv-cache uv run --no-sync bandit -q -r
  src/scouting/sources`
  - exit status: `0`
  - result: no Bandit findings using an isolated temporary uv cache

## Artifacts/evidence

- `src/scouting/sources/synthetic.py`
- `tests/unit/test_synthetic_fixture.py`
- `reports/reviews/W03/returns/W03-FIXTURES-01-R2.md`
- Regression identities:
  `test_observation_at_or_after_cutoff_fails_closed_even_if_available_earlier` and
  `test_observation_cutoff_rejection_reason_is_distinct_from_availability`

## Risks

- none

## Follow-up items

- Master to independently read the three R2 paths and rerun the five packet checks.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no fixture edits: confirmed
- no edits outside `allowed_paths`: confirmed

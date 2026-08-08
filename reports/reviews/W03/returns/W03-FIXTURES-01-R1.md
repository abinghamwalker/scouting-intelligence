# Subagent return

## Task

- task_id: `W03-FIXTURES-01`
- objective: Create deterministic development and protected synthetic football fixtures,
  with strict temporal admission and contract-valid expected W03 journey payloads.

## Files changed

- `src/scouting/sources/__init__.py`
- `src/scouting/sources/synthetic.py`
- `tests/fixtures/synthetic/domain.json`
- `tests/fixtures/synthetic/expected_retrieval.json`
- `tests/fixtures/synthetic/protected/domain.json`
- `tests/fixtures/synthetic/protected/expected_retrieval.json`
- `tests/unit/test_synthetic_fixture.py`
- `reports/reviews/W03/returns/W03-FIXTURES-01-R1.md`

## Summary

- Added a synthetic-only fixture loader that verifies exact envelope fields, the
  `w03_synthetic_generated` rights classification, canonical SHA-256 payload digests,
  stable canonical UUIDs, UTC timestamps, domain references, fixture security cases,
  source-manifest lineage, contract relationships, and tenant/trace consistency.
- Temporal admission is fail-closed and strict-before: facts with
  `available_at >= decision_cutoff_ts` are excluded, as are facts with missing
  availability evidence. Rejected facts retain an explicit reason and cannot enter
  the admitted deterministic order.
- Added a development domain containing two competitions, four teams, six players,
  two matches, one unresolved provider identity, one eligible late-arriving fact, one
  fact available exactly at the cutoff, and one fact missing availability evidence.
  It also freezes path-escape, unknown-role, cross-tenant, confidential read/export,
  and audit mutation/deletion attempts for the later W03 boundary journey.
- Added contract-valid role brief, retrieval request, complete evidence/explanation
  result, shortlist target, source manifest, canonical dependency lineage, and expected
  material-action audit sequence.
- Added a physically separated protected fixture with different domain entities,
  cutoff, expected journey, source/index identifiers, and immutable domain/expected
  digests. Its expected output must remain master-brokered.
- Development domain digest:
  `03972808bd6628dd4ffb66a975108bb15f649a0b778e493c85874ef107953e2a`.
- Development expected digest:
  `f0948134aa0b02595e2974ff6ca264496db401c68d937bf8b8d594561f57e0e9`.
- Protected domain digest:
  `51f56f2bc9d88196e1b37b6f28c9879a1cdc4ee4db5727a955c5c188b9bfbd7f`.
- Protected expected digest:
  `9c3c0b65d53e8a4fefdd160ba38b1bf016671cf0aaa97d7fdc08c3a238b4fdf6`.

## Tests run

- command: `uv run pytest -q tests/unit/test_synthetic_fixture.py`
  - exit status: `0`
  - result: `7 passed`
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

## Artifacts/evidence

- `tests/fixtures/synthetic/domain.json`
- `tests/fixtures/synthetic/expected_retrieval.json`
- `tests/fixtures/synthetic/protected/domain.json`
- `tests/fixtures/synthetic/protected/expected_retrieval.json`
- `tests/unit/test_synthetic_fixture.py`
- `reports/reviews/W03/returns/W03-FIXTURES-01-R1.md`

## Risks

- The protected expected output is logically and physically separated, but local
  filesystem readability cannot itself enforce evaluation blinding. The master must
  withhold `tests/fixtures/synthetic/protected/expected_retrieval.json` from downstream
  implementer packets and broker the preregistered protected run.
- All data, identities, evidence, scores, lineage artifacts, and expected outcomes are
  synthetic foundation fixtures. They support no real-data, relevance, security,
  usability, pilot, or model-performance claim.

## Follow-up items

- Master to inspect every changed file, rerun all four packet checks, and broker the
  protected comparison only after the W03 vertical implementation is preregistered.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

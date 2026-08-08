# Subagent return

## Task

- task_id: `W03-CONTRACTS-01`
- objective: Implement the strict, immutable W03 cross-boundary contracts and executable
  contract tests for the synthetic vertical slice.

## Files changed

- `src/scouting/contracts/__init__.py`
- `src/scouting/contracts/primitives.py`
- `src/scouting/contracts/evidence.py`
- `src/scouting/contracts/workflow.py`
- `src/scouting/contracts/retrieval.py`
- `src/scouting/contracts/audit.py`
- `tests/contracts/test_foundation_contracts.py`
- `reports/reviews/W03/returns/W03-CONTRACTS-01-R1.md`

## Summary

- Added a shared Pydantic v2 contract base configured for strict validation, unknown-field
  rejection, frozen instances, and validated defaults.
- Added semantic strict UUID aliases, tenant and trace contexts, positive optimistic
  versions, bounded numeric primitives, and UTC-only instants that reject naive or
  non-zero-offset datetimes without coercion.
- Added immutable source digests, licence/use classification, source manifests, coverage,
  source identities, versioned identity evidence, dependency lineage, and temporal
  evidence.
- Temporal evidence verifies the exact dependency availability watermark, rejects
  dependencies available after the feature cutoff, derives `valid_from_ts` consistently,
  ties source manifest IDs to lineage, and checks lineage digests.
- Added versioned tenant-scoped role briefs and shortlist entries with trace IDs,
  optimistic versions, immutable tuple payloads, uniqueness checks, and complete
  model-assisted shortlist provenance.
- Added versioned tenant-scoped retrieval requests/results. Each candidate must expose all
  six evidence dimensions, confidence/applicability, coverage, lineage, and reason codes.
  The only admissible claim boundary is `resemblance_only`; unknown outcome claims are
  rejected.
- Added tenant-, actor-, request-, and trace-scoped audit events with explicit requirements
  for exports and overrides.
- Added 15 focused contract tests covering strict UUID/UTC parsing, JSON round trips,
  unknown fields, frozen models, source-right fail-closure, identity accountability,
  future-data rejection, watermark/validity integrity, tenant/version requirements,
  shortlist provenance, retrieval evidence completeness, the resemblance-only boundary,
  and audit context.

## Tests run

- command: `uv run pytest -q tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: `15 passed in 0.14s`
- command:
  `uv run ruff format --check src/scouting/contracts tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: `7 files already formatted`
- command:
  `uv run ruff check src/scouting/contracts tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/contracts`
  - exit status: `0`
  - result: `Success: no issues found in 6 source files`

## Artifacts/evidence

- `tests/contracts/test_foundation_contracts.py`
- `reports/reviews/W03/returns/W03-CONTRACTS-01-R1.md`
- Contract schema identifier: `schema_version = 1`
- Retrieval claim identifier: `resemblance_only`

## Risks

- Consumer integration with storage, serving, workflow persistence, and application code is
  intentionally outside this packet and has not been exercised here.
- These high-risk shared contracts still require the master's independent readback/rerun
  and the separately required W03 boundary review before acceptance.
- Future schema evolution will require explicit compatibility/version policy; the current
  contracts intentionally accept only schema version `1`.

## Follow-up items

- None within `W03-CONTRACTS-01`; proceed to mandatory master verification and independent
  W03 contract-boundary review.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor
  `uv.lock` was modified.
- no edits outside `allowed_paths`: confirmed.

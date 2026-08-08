# Subagent return

## Task

- task_id: `W04-CONTRACT-TEMPORAL-01-R1`
- objective: Correct the generic source-manifest temporal contract so actual local
  acquisition and upstream source availability remain distinct truthful instants,
  including Wyscout release in 2020 before local acquisition in 2026.

## Files changed

- `src/scouting/contracts/evidence.py`
- `tests/contracts/test_foundation_contracts.py`
- `reports/reviews/W04/returns/W04-CONTRACT-TEMPORAL-01-R1.md`

## Summary

- Removed only the invalid `available_at >= acquired_at` ordering assumption from
  `SourceSnapshotManifest`.
- Documented `acquired_at` as the actual local receipt instant and `available_at` as
  the upstream source/fact availability instant. Both remain independently required
  strict UTC fields, and neither is derived from the other.
- Retained the existing duplicate source-object-path validator without weakening the
  strict frozen base model, file digest, size/count, coverage, rights, or schema
  controls.
- Added validation for all three legitimate orderings:
  - Wyscout source availability in 2020 before local acquisition in 2026;
  - availability equal to acquisition;
  - embargo-like availability after local receipt.
- Added explicit tests proving both timestamps remain required and reject naive or
  non-UTC values.
- Added explicit duplicate-object-path and unknown-field regressions.
- Left `TemporalEvidence` and all strict-before-cutoff dependency rules unchanged.

## Tests run

- command: `uv run pytest -q tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result before implementation: `32 passed`.
- command:
  `uv run ruff format src/scouting/contracts/evidence.py tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: two files left unchanged.
- command: `uv run pytest -q tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result after implementation: `42 passed`.
- command:
  `uv run ruff format --check src/scouting/contracts/evidence.py tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: two files already formatted.
- command:
  `uv run ruff check src/scouting/contracts/evidence.py tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/evidence.py`
  - exit status: `0`
  - result: no issues found in one source file.
- command: `uv run bandit -q src/scouting/contracts/evidence.py`
  - exit status: `0`
  - result: no findings.

## Artifacts/evidence

- `src/scouting/contracts/evidence.py`
  - `SourceSnapshotManifest` field semantics and duplicate-only coherence validator
- `tests/contracts/test_foundation_contracts.py`
  - `test_source_manifest_accepts_independent_acquisition_and_availability_orderings`
  - `test_source_manifest_requires_both_temporal_instants`
  - `test_source_manifest_rejects_non_utc_temporal_instants`
  - `test_source_manifest_rejects_duplicate_object_paths_and_unknown_fields`
- Final bounded contract result: `42 passed`.

## Risks

- The contract can require both independent timestamps and preserve their exact values,
  but it cannot prove that a producer supplied truthful provenance. Source adapters and
  acquisition evidence must populate the fields from their declared authorities.
- Removing the invalid cross-clock ordering is intentional. Historical eligibility
  remains enforced separately by dependency `available_at` and the strict feature
  cutoff in `TemporalEvidence`.
- This packet changes no field name or serialized shape and requires no migration.
- The master retains mandatory second review and acceptance authority for this shared
  contract change.

## Follow-up items

- Master assign or perform the required second review of the shared contract change
  and independently rerun the bounded checks. No broader temporal architecture or
  migration change is requested.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.
- no field rename, migration, source-adapter, identity, data-product, configuration,
  orchestration, data, or run-artifact change: confirmed.
- no protected fixture access: confirmed.
- no provider data, network access, external service, credential, public bind, or
  deployment: confirmed.
- no delegation: confirmed.
- no Docker operation: confirmed.
- no self-approval or phase-gate claim: confirmed; acceptance remains with the master
  and required second reviewer.

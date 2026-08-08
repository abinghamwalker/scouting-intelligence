# Subagent return

## Task

- task_id: W05-CONTRACTS-01
- objective: Add strictly additive typed W05 boundary contracts for deterministic feature state, roles, M0 artifacts, pinned serving, explanations, separate confidence evidence, and stable result identity without changing W03/W04 contracts.

## Files changed

- src/scouting/contracts/m0.py
- src/scouting/contracts/__init__.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-01-R1.md

## Summary

- Added immutable, strict W05 M0 contracts for explicit finite feature states (`VALUE`, `ZERO`, `MISSING`, `SUPPRESSED`, `UNAVAILABLE`), including fail-closed numeric/reason-code combinations.
- Added a versioned football-responsibility taxonomy, deterministic source-label mappings, and contextual ordered probabilistic role membership with exact decimal-total and taxonomy-binding checks.
- Added the closed transparent M0 model-family and serialization-format enums plus an artifact manifest pinning exact ordered feature names/schema hash, taxonomy, configuration, fitting population, payload, model/index, lineage, seed, and format identities.
- Added a pinned serving request that rejects every artifact/schema/taxonomy/configuration/population/lineage/model/index substitution.
- Added an M0 result wrapper retaining the existing resemblance-only `RetrievalResult`, separate data-confidence evidence, deterministic structured explanation inputs/reason codes, and verified canonical JSON SHA-256 result digest.
- Re-exported only the additive public W05 contract surface and added focused strict-parsing, JSON round-trip, unknown-field, and adversarial invariant coverage.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/m0.py src/scouting/contracts/__init__.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/contracts/m0.py src/scouting/contracts/__init__.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/m0.py src/scouting/contracts/__init__.py`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py`
  - exit status: 0
  - result: 47 passed in 0.13s.
- command: `uv run lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken; 40 files and 78 dependencies analysed.

## Artifacts/evidence

- src/scouting/contracts/m0.py
- tests/contracts/test_w05_m0_contracts.py
- reports/reviews/W05/returns/W05-CONTRACTS-01-R1.md
- Result digests use canonical sorted-key, compact JSON (excluding `result_digest`) and SHA-256; the wrapper validates the supplied digest against that projection.

## Risks

- The contracts deliberately expose no validation-quality, expert-review, performance, forecast, blended-match, learned-ranker, or W06 partition claim. Those later concerns require separate governed artifacts and evaluation gates.
- `PinnedM0ServingRequest.require_matching_artifact` is an explicit serving-boundary assertion; its caller must invoke it before loading/scoring an artifact.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

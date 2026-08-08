# Subagent return

## Task

- task_id: W06-EVAL-CORE-01-R1
- objective: Implement fail-closed, content-addressed W06 evaluation contracts and one deterministic public-fixture metric/bootstrap core without producing or accessing protected evidence.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/contracts/__init__.py
- src/scouting/evaluation/__init__.py
- src/scouting/evaluation/core.py
- tests/contracts/test_w06_evaluation_contracts.py
- tests/unit/test_w06_evaluation_metrics.py
- tests/fixtures/w06/public-evaluation-v1.json
- reports/reviews/W06/returns/W06-EVAL-CORE-01-R1.md

## Summary

- Added immutable, strict, self-digesting contracts for protocol/query/exemplar identity, governed reviewer identity, relevance/pair/hard-negative evidence, adjudication, exclusive FIT/TUNE/CALIBRATION/PROTECTED_TEST/PROSPECTIVE membership, protected one-use access records, runs, metrics, intervals, slices, failures, and ACCEPT_CLAIM/NARROW_APPLICABILITY/NO_GO decisions.
- Bundle validation rejects unknown/duplicate/cross-partition inputs, query/candidate overlap, post-cutoff evidence, prohibited rights, and reviewer substitution. Metrics preserve abstention, absent labels, zero/insufficient denominators, and undersized candidate universes as labelled unavailable states; no missing value is zero-filled.
- The reusable core provides Precision/Recall/NDCG@k, coverage, deterministic query-unit percentile bootstrap, Spearman, Jaccard/top-k overlap, churn, and canonical disagreement lists. Only the public fixture is used and it is explicitly implementation-only, never human-expert/protected/claim evidence.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 1
  - result: blocked by global UV cache sandbox access (`.cache/uv/sdists-v9/.git`).
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-uv-cache uv run --no-sync pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: 4 passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-uv-cache uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-uv-cache uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in 3 source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: contracts/import direction kept.

## Artifacts/evidence

- public fixture: `tests/fixtures/w06/public-evaluation-v1.json`; SHA-256 `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`.
- deterministic bootstrap public-test resample digest: `56cae9b0461497b65e9046f1935d5b3b13cb09c73fd01a5256d4e89d9df23c12` (seed `17`, 50 resamples, confidence `0.9`, `k=2`).

## Risks

- No governed expert relevance population, calibration evidence, transfer population, prospective outcomes, or protected W06 result exists in this scope; any such gate must remain NO_GO/explicitly unavailable until master-owned evidence is supplied.
- Future protected execution must bind the contract digests to a one-use broker record and retain missing/abstained denominators; the public fixture cannot be promoted into human or protected evidence.

## Follow-up items

- Master/reviewer: bind authentic governed evidence and any protected broker result to these contracts; do not tune protocol thresholds from public fixture values.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

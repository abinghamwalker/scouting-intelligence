# Subagent return

## Task

- task_id: W06-EVAL-CORE-01-R2
- objective: Correct the bounded R1 protected-decision, aggregate-evidence, metric, comparison and bootstrap defects without accessing protected evidence.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/contracts/__init__.py
- src/scouting/evaluation/__init__.py
- src/scouting/evaluation/core.py
- tests/contracts/test_w06_evaluation_contracts.py
- tests/unit/test_w06_evaluation_metrics.py
- reports/reviews/W06/returns/W06-EVAL-CORE-01-R2.md

## Summary

- W06-EC-R1-01: bundle validation now rejects fixture evidence in CALIBRATION, PROTECTED_TEST and PROSPECTIVE memberships; enforces query cutoff, candidate-universe and roster/rubric bindings. Access retains the protected one-use condition.
- W06-EC-R1-02: protocol roots bind canonical query/reviewer/membership digest sequences; bundle has a self-verifying aggregate digest and validates canonical/unique query, roster, membership, candidate and adjudication references.
- W06-EC-R1-03: ranking input is now a complete frozen universe of mutually exclusive RELEVANT/PARTIAL/IRRELEVANT/UNJUDGED/ABSTAIN labels. Evaluation requires declared k and returns explicit unavailable results for incomplete labels or insufficient universes.
- W06-EC-R1-04: rank comparison reranks the shared intersection for bounded Spearman, reports overlap count/rate and bounded replacement churn, and adds explicit eligible pair-preference and exact-label inter-rater agreement functions.
- W06-EC-R1-05: protocol freezes resampling unit/seed/count/confidence/percentile method, metric roster and missingness/partial policy. Bootstrap digest binds query IDs, values, metric, k, settings and resample outputs.

## Tests run

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
- Metric/interval/bundle/run/gate identities are self-verifying canonical SHA-256 fields; this packet deliberately produces no protected bundle/run/gate identity or result.

## Risks

- No governed human reviewer, protected population, protected access consumption, protected result, threshold, calibration, transfer or prospective evidence was created or accessed. Any future ACCEPT_CLAIM remains subject to master-owned protected execution and independent review.
- Public fixture evidence remains structurally implementation-only and cannot support a claim.

## Follow-up items

- Master/reviewer: independently challenge the nested protected access/run/gate relation using governed evidence when such evidence exists; this packet did not execute or freeze a protected result.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

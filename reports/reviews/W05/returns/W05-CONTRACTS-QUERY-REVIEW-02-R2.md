# Subagent return

## Task

- task_id: W05-CONTRACTS-QUERY-REVIEW-02
- objective: Independently confirm the expected resolved-query digest rejects same-ID semantic substitution without regressing accepted query/ranking checks.

## Files changed

- reports/reviews/W05/w05-m0-query-ranking-contracts-independent-review-R2.md
- reports/reviews/W05/returns/W05-CONTRACTS-QUERY-REVIEW-02-R2.md

## Summary

- Verdict: **PASS**; **P0: 0; P1: 0; P2: 0**.
- Confirmed `expected_resolved_query_digest` is explicitly supplied, exactly cross-checked against the self-verified nested query digest, and included in the outer result digest projection.
- Reproduced the R1 responsibility/weight substitution with tenant, trace, brief ID/version, taxonomy, cutoff, limit, exclusions, artifact pins, and the independent expected pin held fixed; recomputing `resolved_query_digest` and `result_digest` now rejects for the exact expected-query-digest mismatch.
- Confirmed negative-zero distance/contribution, request/result tenant/trace/brief/cutoff/claim drift, fully recomputed exclusion drift, feature-axis mismatch, and inverse-UUID equal ties all reject.
- Found no blocker under any of the six W05 tests and no regression or out-of-scope truth work.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py`
  - exit status: 0
  - result: 58 passed in 0.18s.
- command: `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/m0.py`
  - exit status: 0
  - result: success; no issues in 1 source file.
- command: `uv run lint-imports`
  - exit status: 2
  - result: sandbox denied `/Users/adrian/.cache/uv/sdists-v9/.git` before analysis.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-query-review-02-r2-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken; 40 files and 79 dependencies analyzed.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: local-only status PASS with failures `[]`.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-query-review-02-r2-uv-cache uv run --no-sync python -B - <<'PY' ... PY`
  - exit status: 0
  - result: fixed-pin same-ID attack, outer-pin binding, negative-zero, identity/claim, exclusion, feature-axis, and inverse-tie probes all rejected.

## Artifacts/evidence

- reports/reviews/W05/w05-m0-query-ranking-contracts-independent-review-R2.md
- `SAME_ID_QUERY_FIXED_PIN_REJECTED expected_resolved_query_digest must match resolved_query.resolved_query_digest`
- `OUTER_RESULT_BINDS_EXPECTED_PIN_REJECTED result_digest must equal`
- `EXCLUSION_DRIFT_REJECTED cannot include a pinned excluded player`
- `FEATURE_AXIS_MISMATCH_REJECTED must exactly match artifact feature_names length`
- `INVERSE_UUID_EQUAL_TIE_REJECTED distance then canonical player UUID bytes`

## Risks

- The exact import-lint invocation remains blocked by sandbox visibility of the shared uv cache; the isolated local-cache rerun passed and is not a W05 product finding.
- Candidate-specific evidence, W04 descriptor/array semantics, and explanation equality remain intentionally outside this bounded review.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

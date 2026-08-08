# Subagent return

## Task

- task_id: W05-CONTRACTS-QUERY-REVIEW-02
- objective: Independently adversarially review the split W05 resolved-query and scored-candidate contract surface without editing candidate source or tests.

## Files changed

- reports/reviews/W05/w05-m0-query-ranking-contracts-independent-review-R1.md
- reports/reviews/W05/returns/W05-CONTRACTS-QUERY-REVIEW-02-R1.md

## Summary

- Verdict: **REWORK**; **P0: 0; P1: 1; P2: 0**.
- Confirmed complete typed query fields, request overlap checks, finite canonical scored-candidate values, artifact feature-axis cardinality, deterministic distance/UUID ordering, and exact result/request identity, limit, exclusion, and claim checks.
- Reproduced one P1 under blocker tests 1, 2, 3, 4, and 6: semantic resolved-query content can be substituted under the same role-brief ID/version after recomputing both `resolved_query_digest` and `result_digest` because no independent expected resolved-query digest is retained.
- Confirmed blocker test 5 passes and confirmed the producer did not enter candidate-specific dimension state, W04 descriptor/array truth, or explanation-equality scope reserved to the serial follow-on packet.
- Smallest bounded correction: add an independently supplied expected resolved-query digest beside the complete typed query, cross-check it against the query's verified digest, and add the direct same-ID semantic substitution test.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py`
  - exit status: 0
  - result: 57 passed in 0.18s.
- command: `uv run ruff check src/scouting/contracts/m0.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/contracts/m0.py`
  - exit status: 0
  - result: success; no issues in 1 source file.
- command: `uv run lint-imports`
  - exit status: 2
  - result: sandbox denied `/Users/adrian/.cache/uv/sdists-v9/.git` before import analysis.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-query-review-02-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken; 40 files and 79 dependencies analyzed.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: local-only status PASS with failures `[]`.
- command: `UV_CACHE_DIR=/tmp/w05-contracts-query-review-02-uv-cache uv run --no-sync python -B - <<'PY' ... PY`
  - exit status: 0
  - result: same-ID query substitution accepted; negative-zero distance/contribution, tenant/trace/brief/cutoff identity drift, exclusion drift, and inverse-UUID equal tie all rejected.

## Artifacts/evidence

- reports/reviews/W05/w05-m0-query-ranking-contracts-independent-review-R1.md
- direct probe identifier: `SAME_ID_QUERY_SUBSTITUTION_ACCEPTED ('progression',)`
- direct negative-zero identifiers: `NEGATIVE_ZERO_REJECTED distance`, `NEGATIVE_ZERO_REJECTED contributions`
- direct ordering identifier: `INVERSE_UUID_EQUAL_TIE_REJECTED`

## Risks

- A serving/result projection can authenticate a substituted semantic query under an unchanged role-brief identity; this is a W05 P1 correctness, lineage/parity, and claim-integrity blocker.
- The exact import-lint invocation remains blocked by sandbox visibility of the shared uv cache; the isolated local-cache rerun passed and is not a W05 product finding.
- Candidate-specific truth work remains intentionally deferred to `W05-CONTRACTS-TRUTH-03`.

## Follow-up items

- Issue the smallest bounded correction described above, add the semantic same-ID recomputed-digest test, and obtain fresh independent review.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.

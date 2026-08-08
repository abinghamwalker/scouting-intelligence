# Subagent return

## Task

- task_id: `W06-EVAL-CORE-REVIEW-01-R1`
- objective: Independently review the W06 evaluation contracts, ranking metrics, deterministic intervals and public fixtures for reproducible defects affecting metric values, denominators, partitions, digests, leakage, the protected gate or claims.

## Files changed

- `reports/reviews/W06/evaluation-core-independent-review-R1.md`
- `reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R1.md`

## Summary

- Verdict: **REWORK**; highest severity **P0**.
- Findings: **1 P0, 4 P1, 1 P2**.
- P0: the protected gate is not relationally bound. Valid constructors accepted implementation-fixture evidence in `PROTECTED_TEST`, a future query cutoff, a mismatched reusable non-one-use FIT access digest, an empty protected run and an `ACCEPT_CLAIM` gate whose protocol differs from the run.
- P1: aggregate roots do not bind nested evidence; re-signed reviewer/rubric/label substitutions, duplicate relevance, reversed same-ID pairs and nonexistent adjudication references validate.
- P1: arbitrary undeclared `k` computes; unjudged candidates silently act as irrelevant/zero; out-of-universe labels change Recall; per-item abstention and ties are unrepresentable; partial Precision/Recall policy is undeclared.
- P1: partial-universe Spearman returned `-1` for the same relative order and `-7` out of range; disjoint top-2 churn returned `2.0`; pair-preference, eligible inter-rater agreement and explicit overlap metrics are absent.
- P1: bootstrap/result/interval settings and digests are not protocol-bound; invalid metric arithmetic, inverted/unmatched intervals, empty runs and order-dependent run digests validate.
- P2: four tests pass but do not cover those invariants; the public JSON fixture is never loaded by the tests.

## Finding table

| ID | Severity | Result |
| --- | --- | --- |
| `W06-EC-R1-01` | P0 | Protected access/run/gate/claim binding bypass. |
| `W06-EC-R1-02` | P1 | Nested-root, substitution, duplicate and adjudication failures. |
| `W06-EC-R1-03` | P1 | Declared-k, missing/unjudged/abstention, partial, universe and tie failures. |
| `W06-EC-R1-04` | P1 | Incorrect Spearman, unbounded churn and missing required metrics. |
| `W06-EC-R1-05` | P1 | Bootstrap/result/interval/run binding and stability failures. |
| `W06-EC-R1-06` | P2 | Materially incomplete tests and unused public fixture. |

Exact formulas, counterexamples, accepted digest identifiers, evidence lines, direct answers to all eight review questions and bounded corrections are in `reports/reviews/W06/evaluation-core-independent-review-R1.md`.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 2
  - result: global uv cache sandbox denial at `/Users/adrian/.cache/uv/sdists-v9/.git`; no tests ran.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: 4 passed in 0.16s.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in 3 source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken.
- command family: task-specific-cache `uv run --no-sync python -c` metric, contract and fixture probes whose exact semantic inputs, returned values and identifiers are recorded in the independent report.
  - exit status: 0 for the final three probes.
  - result: all reported counterexamples reproduced; fixture SHA-256 `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6` and two-row count reproduced.
- exploratory note: two initial contract-probe helper iterations exited 1 before testing a contract because the helper did not yet reproduce Pydantic default/nested canonicalization; corrected probe results use normal validated constructors.
- command: `test -s reports/reviews/W06/evaluation-core-independent-review-R1.md`
  - exit status: 0
  - result: independent report exists and is non-empty.
- command: `test -s reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R1.md`
  - exit status: 0
  - result: mandatory return exists and is non-empty.

## Artifacts/evidence

- Full independent review: `reports/reviews/W06/evaluation-core-independent-review-R1.md`
- Primary code evidence: `src/scouting/contracts/evaluation.py:99-141`, `205-291`, `294-354`, `390-427`; `src/scouting/evaluation/core.py:15-93`.
- Test evidence: `tests/contracts/test_w06_evaluation_contracts.py:32-54`; `tests/unit/test_w06_evaluation_metrics.py:7-28`.
- Public fixture: `tests/fixtures/w06/public-evaluation-v1.json`; SHA-256 `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`.
- Key reproduced identifiers: accepted invalid metric digest `0e3b07a3504dab6d01abf6ac10680a1977133596d74d2a851e0a4c3065da0e5c`; accepted inverted interval digest `6189314f40b51bdc6e4aa65393e3a670a8f011548640653ff68a472be46e57f6`; bootstrap digest collision `51b70694b610e2c65de96af6f7487a89cfb9301728ad9e9ae4c14fb393e52c41`; order-dependent run digests `8538f6e977e977a12001bf3c1b2b15eb223ee97a9743cace412a8ccd7c742bc3` and `34c80d94c3fbe20fc95542648c7e454e2271bf43984b4720dfbee20f7456f884`.

## Risks

- Leakage: future query cutoffs and fixture authority can enter a protected path; one-use access is not consumed or bound.
- Schema/digest: no bundle/adjudication/access aggregate binds protocol roots to actual nested objects or canonical order.
- Interval/statistics: settings, inputs, arithmetic and result links are not frozen or validated; required pair/agreement metrics are absent.
- Applicability: opaque slice digests do not establish protocol population or a valid narrowing decision.
- Claim: `ACCEPT_CLAIM` can validate without governed expert evidence or any metric result.

## Follow-up items

- Issue bounded rework for every P0/P1 correction and the adversarial coverage listed in the full report.
- Obtain a fresh independent material review before any protected execution or claim decision.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no implementation/test/fixture/orchestration edits: confirmed.
- no delegation or self-approval: confirmed.

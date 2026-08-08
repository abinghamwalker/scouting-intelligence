# Subagent return

## Task

- task_id: W06-EVAL-GATE-BINDING-02-R1
- objective: Bind protected gate decisions to one validated protocol and exact canonical evaluated protected-query population, while retaining only coherent negative evidence or explicit missing-population `NO_GO` decisions.

## Files changed

- src/scouting/contracts/evaluation.py
- tests/contracts/test_w06_evaluation_contracts.py
- reports/reviews/W06/returns/W06-EVAL-GATE-BINDING-02-R1.md

## Summary

- Added `EvaluatedQueryRoster`, a non-empty, unique, canonical query-ID tuple with a recomputed roster digest.
- Access and runs now embed the same roster and digest. Persisted `MetricResult` and `BootstrapInterval` carry that exact digest; run validation rejects result/interval population substitution.
- Gate validation now requires identical protocol digests for gate, bundle and run; its roster must exactly equal all and only `PROTECTED_TEST` bundle queries. Every evaluated query therefore exists in the bundle and has the run partition.
- `ACCEPT_CLAIM` and `NARROW_APPLICABILITY` both require governed relevance for every evaluated protected query and computed primary results/intervals bound to that population.
- `NO_GO` permits exactly two shapes: neither bundle nor run and precisely one explicit `MISSING_EXPERT_RELEVANCE_EVIDENCE` or `MISSING_PROTECTED_POPULATION` reason; or both bundle and fully linked run. Exactly-one-object orphan shapes reject.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py && UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r1-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r1-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py && UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r1-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r1-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py && UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: `8 passed in 0.20s`; Ruff passed; mypy reported no issues; import direction kept with 3 contracts and 0 broken.

## Artifacts/evidence

- focused public-only contract matrix: `tests/contracts/test_w06_evaluation_contracts.py`.
- mixed FIT/PROTECTED_TEST bundle with a protected run whose roster selected the FIT query: rejected with `evaluated query roster must exactly cover the protected bundle population`.
- gate protocol substituted for a different bundle protocol: rejected with `gate run must bind this protected protocol and bundle`.
- protected `NARROW_APPLICABILITY` with zero relevance: rejected with `claim or narrowing requires governed evidence for every evaluated protected query`.
- metric population digest substituted from `query` to `querytwo`: rejected at run construction with `result must bind the run evaluated query population`.
- complete linked negative protected bundle/run `NO_GO`: accepted; explicit no-object `MISSING_PROTECTED_POPULATION` `NO_GO`: accepted; run-only `NO_GO`: rejected.

## Risks

- metric: core metric arithmetic and ranking behaviour were intentionally unchanged; the serial second split owns remaining value/missingness corrections.
- identity: comparison, pair/agreement, slice and failure identity work remains reserved for the serial second split.
- interval: this change proves the stored interval population digest matches the run; independent production resample recomputation remains a later execution concern.
- leakage/applicability/claim: no protected expected output, protected result, threshold, positive claim, external evidence or provider access was used. Future protected evaluation still requires master-owned execution and review.

## Follow-up items

- Serial second split: address the R3 value, pair/comparison identity, interval-range, capability and duplicate-child persistence findings without altering this gate-population lineage relation.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

# Subagent return

## Task

- task_id: W06-EVAL-CORE-REVIEW-01-R3
- objective: Independently determine whether W06 evaluation contracts and metrics fail
  closed for values, partitions, negative evidence, intervals and protected claims.

## Files changed

- reports/reviews/W06/evaluation-core-independent-review-R3.md
- reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R3.md

## Summary

- verdict: **RETURN FOR REWORK**.
- exact remaining inventory: **1 P0, 4 P1, 1 P2**.
- P0: an accepted claim can use mixed FIT/PROTECTED_TEST memberships without a
  run-level evaluated-query roster and can substitute a bundle protocol; protected
  narrowing validates without relevance and with only an unsupported result.
- P1: complete negative evidence cannot be retained by `NO_GO`, while an orphan run can;
  precision is incorrectly unavailable for a complete zero-positive ranking; pair
  missingness and comparison identities are ambiguous; negative sufficient statistics,
  out-of-unit interval bounds, duplicate slice/failure rows, and unsupported primary
  metric configurations validate.
- P2: the focused suite omits these cases and the literal Ruff check fails.

### R2 closure matrix

| R2 family | R3 status | Severity |
|---|---|---:|
| W06-EC-R1-01 protected decision relation | OPEN, partial closure | P0 |
| W06-EC-R1-02 canonical aggregate | CLOSED | none |
| W06-EC-R1-03 value/missingness policy | OPEN, substantial partial closure | P1 |
| W06-EC-R1-04 comparison/pair/agreement | OPEN, partial closure | P1 |
| W06-EC-R1-05 metric/interval/run persistence | OPEN, substantial partial closure | P1 |

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: `6 passed in 0.16s`.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 1
  - result: `I001` unsorted imports in `src/scouting/contracts/__init__.py`.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: success, no issues in three source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-review-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- command family: public-only `UV_CACHE_DIR=... PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python -c ...` constructor and metric probes documented in the review report.
  - exit status: 0 for every probe
  - result: independently reproduced every stated P0/P1 counterexample and R2 closure; no protected path accessed.
- command: `test -s reports/reviews/W06/evaluation-core-independent-review-R3.md`
  - exit status: 0
  - result: review exists and is non-empty.
- command: `test -s reports/reviews/W06/returns/W06-EVAL-CORE-REVIEW-01-R3.md`
  - exit status: 0
  - result: return exists and is non-empty.

## Artifacts/evidence

- full review: `reports/reviews/W06/evaluation-core-independent-review-R3.md`.
- negative-stat `MetricResult`: `af706ff4f29d3a37b0b7689415e4d1735756059fb6b0f534a1e8857822f002dd`.
- mixed-membership accepted gate, independent equivalent:
  `6a8fb2d6680f040a3e7148cc8b03464c2840526427f7447332e0434f6986a884`.
- protocol-substituted accepted gate:
  `22920e4fb7b1dd319082abd854dbbd82806207d114daa9a70d1a5b79f75a6925`.
- zero-relevance narrowed gate, independent equivalent:
  `d8c6564b1a1f9fab2c32b87375f9b206b6b2871ec34121bb13897c9b43cad3e1`.
- out-of-unit precision interval/run:
  `784ec217b0cdd509e97a27d79e02e77bba1ec1a1bcd92d945381ae2dbe14ec04` /
  `b0d90cf25d63341e2ff8b67466211a1a5fadf2ad3a7f397fc433607fba09254e`.
- orphan-run `NO_GO`: `66c5c94e21114b772ca7e2d0bc82e5be658c4b317795b1df37d8ed6ac409be73`.
- missing-population `NO_GO`: `1142b95b5cd05703e79e1b788735fca0f92414ac1e5ee4104a694ee9b0da3606`.
- pair identity collision:
  `b44ef7b7e5e47692b010fbe0efd9e7e32f72f01bfaf74592781b732eee7060f6`.
- duplicate slice/failure/run identities:
  `6c501b99c770e3b697a12d9bc5c2e79e283933ab200ed162f2a3b10109934cd9` /
  `a77daf1a2a5772a4d1dd706547358436b6586ea952b8e39d032c96e5caab03f7` /
  `bb807e8a572233fd8d28e668901f4c7ba479f543518508e8ecbf4d12a18f411b`.

## Risks

- leakage/partition: accepted values are not bound to the evaluated protected query set;
  bundle protocol substitution remains possible.
- schema/identity: negative sufficient statistics, broad unit intervals, identity
  collisions and duplicate result rows remain valid.
- interval/configuration: an unsupported primary metric protocol validates even though
  bootstrap and positive-gate assembly cannot support it.
- applicability/claim: narrowing can lack governed relevance; defined zero precision is
  discarded and missing pair predictions count as errors.

## Follow-up items

1. Serial R4-A: bind gate/bundle/run protocol and evaluated protected query population;
   implement complete-evidence and missing-population `NO_GO` shapes.
2. Serial R4-B: correct metric availability, pair missingness, statistic/interval ranges,
   capability validation, canonical result identities and uniqueness; add regressions
   and sort exports.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorized dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider or credential access: confirmed.
- no edits outside `allowed_paths`: confirmed; only the two report paths above changed.

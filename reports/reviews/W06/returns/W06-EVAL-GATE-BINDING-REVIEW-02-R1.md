# Subagent return

## Task

- task_id: W06-EVAL-GATE-BINDING-REVIEW-02
- objective: Independently decide whether W06 protocol, protected population, access,
  result, interval, and retained negative evidence now form one fail-closed relation.

## Files changed

- reports/reviews/W06/evaluation-gate-binding-independent-review-R1.md
- reports/reviews/W06/returns/W06-EVAL-GATE-BINDING-REVIEW-02-R1.md

## Summary

- fresh verdict: **RETURN FOR REWORK — 1 P0, 1 P1**.
- **P0:** `ACCEPT_CLAIM` and `NARROW_APPLICABILITY` accept a protected population whose
  only governed relevance is `ABSTAIN`; gate identities were
  `506ba104393a275f2a1a4a1f3916429ea0ac170fd76e3af488e5a028c27dd1f3`
  and `80ba94ad92d69df980046bb1e5a8ce425294fc72893661faae8b60f35ab82e9a`.
- **P1:** a foreign-population slice metric and an absent-query failure validate inside
  a protected run and through retained linked `NO_GO`; gate identities were
  `0b359ea3623bebcdfc8305fc0d575511aa245c20e38d8e89e78b8f658854636b`
  and `318ea9d3b3638431cfa40d7d28af73b625b62f24578ef5e6b4188eb4b4eef559`.
- exact R3 mixed-membership, protocol-substitution, and zero-evidence narrowing
  constructors now reject. Coherent positive decisions, a complete linked negative
  `NO_GO`, and each single explicit no-object missing-population reason validate;
  bundle-only and run-only negative shapes reject.

## Reproduction matrix

| Relation | Fresh result | Severity |
|---|---|---:|
| gate/bundle/run protocol | substitutions reject | closure |
| exact protected roster | non-protected, absent, mixed-entry, and omitted queries reject | closure |
| access/top-level result/interval population | roster/digest substitutions reject | closure |
| positive evidence | zero rows reject; all-abstain rows accept | **P0** |
| positive primary result/interval | unsupported primary and missing interval reject | closure |
| missing-population `NO_GO` | either one explicit missing reason accepts; arbitrary/multiple reject | closure |
| retained `NO_GO` shape | both linked accepts; either orphan rejects | closure |
| retained run children | foreign slice metric and absent-query failure accept | **P1** |

## Tests run

- command: corrected 33-case public-constructor matrix via
  `UV_CACHE_DIR=/private/tmp/w06-eval-gate-binding-review-r1-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python - <<'PY' ... PY`
  - exit status: 0
  - result: 28 expected closures and five unexpected accepts comprising the two exact
    findings above.
- command: focused eight-witness public-constructor matrix through the same `uv` form
  - exit status: 0
  - result: reproduced both findings and the computed-result/interval negative controls.
- command: `PYTEST_ADDOPTS='-p no:cacheprovider' uv run --no-sync pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: `8 passed in 0.29s`.
- command: `uv run --no-sync ruff check src/scouting/contracts/evaluation.py tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run --no-sync mypy src/scouting/contracts/evaluation.py`
  - exit status: 0
  - result: success; no issues in one source file.
- command: `uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- command: both packet `test -s` report checks
  - exit status: 0
  - result: independent review and mandatory return both exist and are non-empty.
- command: initial inline probe harness before digest-helper correction
  - exit status: 1
  - result: harness omitted default fields from a digest preimage; no verdict relied on
    that run.

## Artifacts/evidence

- reports/reviews/W06/evaluation-gate-binding-independent-review-R1.md
- reports/reviews/W06/returns/W06-EVAL-GATE-BINDING-REVIEW-02-R1.md

## Risks

- population/leakage: top-level binding closes; nested slice metrics and failures escape.
- applicability/claim: governed abstention can satisfy the positive evidence predicate.
- negative retention: the two object shapes are correct, but retained children are not
  fully population-bound.
- interval: top-level population and required-primary interval checks closed.
- reserved metric-value/identity defects: acknowledged and not re-reviewed except where
  nested child identity crosses the new population relation.

## Follow-up items

- Require at least one eligible non-`ABSTAIN` governed relevance judgment per evaluated
  protected query for both positive decisions.
- Bind every nested slice metric to the run roster (or an explicit constrained slice
  sub-roster) and require every failure query ID to belong to the run roster.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

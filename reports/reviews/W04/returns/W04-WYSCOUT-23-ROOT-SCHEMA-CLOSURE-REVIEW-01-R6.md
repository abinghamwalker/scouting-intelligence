# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R6`
- objective: freshly verify the fixed R6 23-root schema closure against the frozen
  R5 56-binding predicate oracle and focused Decimal/matrix/root-digest evidence
- disposition: `REWORK_P1_01`
- findings: `P0 0 / P1 1 / P2 0`

## Files changed

- `reports/reviews/W04/wyscout-23-root-schema-closure-independent-review-R6.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R6.md`

## Summary

- Reproduced all seven fixed hashes before review and immediately before rendering.
- Independently extracted 56 unique JSONL oracle rows and reproduced ledger SHA-256
  `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`.
- Candidate and oracle have the same 56/56 owner/validator roster.
- Exact frozen-oracle comparison is operation `0/56`, ordered operands `10/56`,
  material constants `0/56`, and complete rows `0/56`.
- Candidate exports and test-owned expectations agree `56/56`, proving the current
  test freezes the alternate candidate ledger rather than the independent oracle.
- Raised one bounded P1. No separate obvious Decimal, 29-row or root-digest blocker
  appeared in the focused schema suite.

## Tests run

- command: `shasum -a 256` over all seven packet-fixed artifacts before review and
  immediately before rendering
  - exit status: `0` both times
  - result: every required SHA-256 exact
- command: read-only `uv run python` extraction/comparison of frozen oracle JSONL,
  candidate exports and test-owned `EXPECTED_RUNTIME_BINDING_LEDGER`
  - exit status: `0`
  - result: oracle rows/keys `56/56`, candidate rows `56`, test rows `56`, key sets
    exact; operation `0/56`, operands `10/56`, constants `0/56`, candidate/test
    `56/56`, complete oracle rows `0/56`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `36 passed in 10.98s`
- command: `uv run pytest --collect-only -q tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `2`
  - result: a later nonessential collection-only invocation was denied while uv
    inspected its cache `.git`; no test ran and the already-completed focused suite
    remained passing

## Artifacts/evidence

- `reports/reviews/W04/wyscout-23-root-schema-closure-independent-review-R6.md`
- frozen oracle ledger SHA-256:
  `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`
- exact finding: `P1-01 candidate/test predicate ledger drift from frozen oracle`

## Risks

- The current ledger gate is self-consistent but not oracle-anchored, so it can pass
  while all 56 complete oracle rows differ.
- No additional obvious risk was observed in the focused Decimal, 29-row matrix or
  root-content/digest families.

## Follow-up items

- Reconcile all 56 candidate semantics and test-owned expectations to the frozen
  P01-P56 ledger, then regenerate derived root bytes/digests and obtain fresh review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no 591-test suite rerun: confirmed
- no delegation, provider/network, product write, cloud/container/CI, publication
  or deployment action: confirmed

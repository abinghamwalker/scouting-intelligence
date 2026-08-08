# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R7`
- objective: independently verify the fixed R7 23-root closure against the frozen
  predicate, constant, Decimal, root and 29-row matrix oracles
- disposition: `REWORK_P1_01`
- findings: `P0 0 / P1 1 / P2 0`

## Files changed

- `reports/reviews/W04/wyscout-23-root-schema-closure-independent-review-R7.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R7.md`

## Summary

- Reproduced all seven fixed hashes.
- Independently reproduced the 56-row oracle SHA `c36ad1932...`; candidate equality
  is 56/56, including declared-owner/MRO and direct-field operand coverage.
- Reproduced C1-C11 material closure, distinct E1-E8, 23 roots, 12 descriptor/11
  JSON-only split, earlier-only dependencies, root digests and retained Decimal
  projection roster.
- Raised P1-01 because the three test matrix SilverAction rows reuse one action and
  source identity and omit exact frozen null/zero, scale-18, RESTART and
  `9999.999999999999999999` boundary variants. The current assertions do not detect
  those omissions.

## Tests run

- command: `shasum -a 256` over all seven fixed artifacts, twice
  - exit status: `0`
  - result: every required hash exact
- command: read-only `uv run python` oracle/candidate/root/resolver reconstruction
  - exit status: `0`
  - result: ledger 56/56 and `c36ad1932...`; C1-C11, E1-E8, 23 roots and digests exact
- command: read-only `PYTHONPATH=tests/contracts uv run python` matrix probe
  - exit status: `0` after approved read-only uv-cache rerun
  - result: 29 rows and exact cardinalities, but SilverAction unique action/source
    identities `1/1`, null row seconds `11`, one-position scale `0`, capacity boundary
    absent and two-position RESTART absent
- broad packet gates: not rerun after the definitive P1, per master direction

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/wyscout-23-root-schema-closure-independent-review-R7.md`
- independent review SHA-256:
  `f4c74753d9a168bb00ee503066e088ea897d445c6cd6bdbaa9a7b1be07bfc2ec`
- frozen/candidate ledger SHA-256:
  `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`

## Risks

- The current green test can accept a matrix that does not exercise the exact
  frozen SilverAction variants, so the 29-row adversarial evidence is incomplete.

## Follow-up items

- Bounded test-fixture rework for the exact R5 Section 5.6 SilverAction rows and
  assertions, followed by a fresh independent review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no candidate or test edits: confirmed
- no delegation: confirmed

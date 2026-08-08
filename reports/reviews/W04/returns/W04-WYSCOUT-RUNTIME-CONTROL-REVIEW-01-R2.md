# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R2`
- objective: Independently review the fixed R2 Wyscout runtime-control child and
  separately retained launcher authority without modifying producer bytes.

## Decision

- verdict: `REWORK`
- findings: `P0/P1/P2 = 0/2/0`
- review artifact:
  `reports/reviews/W04/wyscout-runtime-control-independent-review-R2.md`

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R2.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R2.md`

## Summary

- Verified the four fixed SHA-256 bindings exactly: child
  `cd8a12da6b9db08c9041823c8b99fae782cf7ff99a72628970354a105c36ce67`,
  launcher
  `c56263cc5c4ba79a7dce5ba3ce3623def04b29933a5fdc8f0f0187d1aaf6332d`,
  tests `3ea58958683ff6d1e244925fc98a8cce77d89e34f2814a9b43f2003b656aac6a`,
  and producer return
  `a97a8a28e3e0d9f39def99f3614dd1d6e5d507c6ab08c5a5096f8c7be83ed45e`.
- Returned P1 for semantic exactness: both collectors accept a forbidden
  two-hop wheel-cache symlink, omit complete five-scheme PEP 427 mapping and
  collision/overwrite/escape proof, and accept a fourth interpreter alias.
- The child also admits arbitrary bootstrap/direct-url bytes and a fourth `.pth`;
  its editable digest is lock inputs plus repository `src/` rows rather than the
  exact normalized editable RECORD/metadata/direct-url/uv-cache predicate.
- Recorded the remaining concise omissions: exact global installed
  ownership/generated-byte closure; exact alias/link mode/inode/loader/ABI
  closure; and complete outer/admission/rebuild environment and control rechecks.
- Returned a second P1 because the launcher is now source-independent but repeats
  the same omitted acceptance predicates, so child/launcher agreement still
  accepts shared semantic substitutions.
- Recorded the hash-matched producer return's green formatting, lint, typing,
  bounded-test, Bandit, import-linter, local-only and direct child/launcher
  comparison gates as producer evidence only.

## Tests run

- None. The review instruction prohibited rerunning tests; all reported R2 gate
  results are explicitly attributed to the hash-matched producer return.

## Risks

- Current child/launcher agreement and content addressing can bless a forbidden
  runtime as a new internally consistent manifest instead of rejecting it.
- The separate launcher implementation is not yet a complete independent
  acceptance oracle because it reconstructs the same incomplete semantics.

## Follow-up items

- Implement exact one-hop cache association and complete five-scheme PEP 427
  mapping, uniqueness, collision, overwrite and escape closure.
- Close bootstrap/`.pth`, editable distribution, installed ownership/generated
  bytes, interpreter/alias/loader/ABI and outer/admission/rebuild predicates in
  both independently implemented collectors.
- Add isolated rejection and child-versus-launcher disagreement tests, then obtain
  a fresh independent review.

## Scope confirmation

- producer bytes read-only: confirmed
- no tests run: confirmed
- no Git operations: confirmed
- no dependency, lock, runtime-data, manifest or rebuild writes: confirmed
- no edits outside the two review paths: confirmed

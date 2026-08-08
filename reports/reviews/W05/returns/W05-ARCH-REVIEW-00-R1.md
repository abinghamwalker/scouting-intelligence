# Subagent return

## Task

- task_id: `W05-ARCH-REVIEW-00`
- objective: Independently challenge the W05 architecture and acceptance surface and
  report only reproducible, scope-bound risks before implementation fans out.

## Files changed

- `reports/reviews/W05/w05-architecture-preflight-R1.md`
- `reports/reviews/W05/returns/W05-ARCH-REVIEW-00-R1.md`

## Summary

- Produced an evidence-backed architecture preflight with verdict
  **REWORK BEFORE W05 IMPLEMENTATION FAN-OUT**.
- Recorded no P0 findings and four P1 findings: real/synthetic feature-authority
  ambiguity; incomplete safe-array/PCA identity; incomplete query/roster/tie/result-byte
  identity; and contradictory/unsupported confidence and explanation truth.
- Classified every finding under the six user-defined W05 blocker tests.
- Answered every packet review question, supplied the exact serial dependency order,
  adversarial substitutions, the minimum synthetic-development comparison, a concrete
  W05 acceptance matrix, and an explicit W10-only host-state separation.
- Recommended only bounded corrections to unaccepted additive W05 contracts and tests;
  no accepted W03/W04 byte or authority needs to change.

## Tests run

- command: `test -s reports/reviews/W05/w05-architecture-preflight-R1.md`
  - exit status: `0`
  - result: PASS; architecture preflight exists and is non-empty
- command: `test -s reports/reviews/W05/returns/W05-ARCH-REVIEW-00-R1.md`
  - exit status: `0`
  - result: PASS; mandatory return exists and is non-empty
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; all 25 local-only/one-root-uv checks passed with no failures

## Artifacts/evidence

- `reports/reviews/W05/w05-architecture-preflight-R1.md`
- Controlling accepted W04 source feature boundary:
  `docs/dataset-cards/w04-wyscout-transformed-v1.md`
- W10 separation authority:
  `reports/verification/W04/w10-deferred-runtime-host-state-hardening-backlog-R1.md`
- W05/W06 gate boundary:
  `../scouting-ml-agent-implementation-workflow.html` lines 990-1014

## Risks

- W05 remains blocked from safe fan-out until the four P1 contract ambiguities receive
  bounded correction and fresh review.
- Even after W05 passes, synthetic-development discrimination is not expert relevance,
  protected evaluation, transfer evidence, calibration, or product validation; those
  claims remain W06-only.
- Host-specific PYC/cache/inode/link/timestamp/temp-path observations remain W10-only
  unless a reproducible path satisfies a W05 blocker test.

## Follow-up items

- Correct and independently re-review `W05-CONTRACTS-01` before registry/taxonomy/model/
  serving fan-out.
- Dispatch and accept W05 work serially: contracts → feature registry → taxonomy → model
  artifact → serving core → parity evidence.
- Preserve the exact W04 four-count real boundary and label broader inputs
  synthetic-development-only.

## Scope confirmation

- no Git operations: confirmed; no Git command was run
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no provider/network/external service access: confirmed
- no delegation or self-approval: confirmed

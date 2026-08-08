# Subagent return

## Task

- task_id: `W04-REPOSITORY-PROGRESSION-GUARD-REVIEW-01-R1`
- objective: Independently attempt to invalidate the exact R2 repository progression-guard correction and return PASS only if every evidence substitution fails closed.

## Files changed

- `reports/reviews/W04/wyscout-repository-progression-guard-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-REPOSITORY-PROGRESSION-GUARD-REVIEW-01-R1.md`

## Summary

- Decision: `REWORK`; exact finding counts `P0=0`, `P1=1`, `P2=0`.
- Verified every packet-fixed candidate and evidence hash before analysis and again after execution.
- Confirmed exact accepted four-path evidence succeeds in both fixtures, all 15 declared mutations per fixture reject, the lower-authority validators and governed path rosters remain present, and the central R21 lifecycle still owns complete progression.
- Independently demonstrated that both helpers accept a paired replacement of the complete review bytes and canonical gate record when the accepted report and return bytes are replayed. The required bounded correction is an exact accepted review digest binding plus a direct combined-substitution test in each fixture.
- Changed no implementation, test, authority, gate, data, orchestration, verification, dependency or product path.

## Tests run

- command: `uv run ruff format --check tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run pytest -q tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `357 passed in 23.14s`
- command: `uv run pytest -vv tests/contracts/test_w04_field_semantic_v2_authority.py::test_actual_progression_requires_exact_complete_r21_gate_evidence tests/contracts/test_w04_possession_semantic_v2_authority.py::test_actual_progression_requires_exact_complete_r21_gate_evidence`
  - exit status: `0`
  - result: all 30 named single-mutation cases passed in `0.07s`
- command: independent in-memory `uv run python -c` combined-substitution harness
  - exit status: `0`
  - result: exact evidence passed; duplicate/cross-wired evidence rejected; paired review-plus-record substitution returned `ACCEPT_UNEXPECTED` in both fixtures
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25/25 controls; zero configured remotes and local pre-push guard intact

## Artifacts/evidence

- independent review: `reports/reviews/W04/wyscout-repository-progression-guard-independent-review-R1.md`
- review SHA-256: `865d1b7af38a9ff54d860117b970dd9b9adf041726ec5c05896f3b3525f7b8a0`
- field fixture SHA-256: `c254430b6bafcb378896636d2c22c51080c69f83c666b0e79fb0162afd84f99d`
- possession fixture SHA-256: `eb56aaa34838f2d28eeb7d6a1f1e8f5cc56ab5a52eeab44fd82ebfd5e2158a94`
- executable failure: `PROGRESSION_GATE_PAIRED_REVIEW_RECORD_SUBSTITUTION`

## Risks

- Until bounded rework is accepted, the lower-authority progression helpers can be satisfied by a review/gate-record pair that differs from the accepted gate evidence while replaying the accepted report and return.

## Follow-up items

- Return a bounded R3 test-only correction binding the exact accepted review digest and adding the paired review-plus-record substitution to both adversarial rosters; then obtain fresh independent review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

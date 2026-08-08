# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-04-R1
- objective: Add deterministic, fail-closed W06 robustness, control, applicability and failure-register behavior over the accepted evaluation core.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/contracts/__init__.py
- src/scouting/evaluation/__init__.py
- src/scouting/evaluation/robustness.py
- tests/contracts/test_w06_robustness_contracts.py
- tests/unit/test_w06_robustness.py
- tests/fixtures/w06/public-robustness-v1.json
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-04-R1.md

## Summary

- Added strict, digest-bound governed-population, stress specification/result, control, applicability, failure-case and failure-register contracts. They reject unknown fields through the shared strict base, noncanonical/duplicate populations, invalid status/value shapes, invalid threshold specifications, substituted protocol bindings, incomplete computed results, and invalid retained-case counts.
- Added a small composition layer that calls the accepted `bootstrap_interval` and `rank_comparison` core functions. Stress tests fail closed with `UNSUPPORTED_INSUFFICIENT_EVIDENCE` and exact deficit strings when their frozen population minima are unmet. Controls use the frozen bootstrap seed and retain the ordered shuffle identity.
- Applicability is always `UNSUPPORTED` for fixture execution and preserves `MISSING_EXPERT_RELEVANCE_EVIDENCE`; absent mandatory transfer inventory stays explicit. Failure retention is deterministic worst-ten, or every case with the exact shortfall.
- Public fixture digest: `3faba3693b28c887b0d411f0ac300fbfb166a1230727c06eeb319095ca26c549`.
- Pinned public identities: governed inventory `c8c0f26e1a41b84015eacb0aa3f05cf731f12d195cf216b905cf796818875479`, unsupported applicability `c3b086bdf03935ec05c1feea67c495355c1b7d67dd17185e6e728b9bb53850ed`, and twelve-case worst-ten register `e455999973f2c91a6c3e9ce76f117ef1b2d85a8e90eabe3d2bb0d60d9937ec56`.
- Computed-versus-unsupported matrix: split-half requires `eligible_observations>=4` and two nonempty halves; rolling windows require three distinct windows; minutes sensitivity requires every declared threshold to have an eligible observation; walk-forward requires two ordered windows and train-before-test; leave competition/team/provider and intersection source comparison require two governed groups. Any deficit yields no metric or interval.

## Tests run

- command: `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: 14 passed.
- command: `uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in four source files.
- command: `uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- command: `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: `3faba3693b28c887b0d411f0ac300fbfb166a1230727c06eeb319095ca26c549`.

## Artifacts/evidence

- tests/fixtures/w06/public-robustness-v1.json — prominent `IMPLEMENTATION_FIXTURE_ONLY` and non-expert/non-empirical notice.
- src/scouting/evaluation/robustness.py — deterministic core-composition implementation.

## Risks

- This is implementation-only evidence; it establishes no human-expert relevance, transfer, calibration, provider, prospective, protected, recruitment-outcome, empirical applicability, or positive product claim.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider access, model/protocol tuning, or edits outside `allowed_paths`: confirmed.

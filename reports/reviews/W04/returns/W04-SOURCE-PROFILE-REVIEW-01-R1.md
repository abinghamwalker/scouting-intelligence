# Subagent return

## Task

- task_id: `W04-SOURCE-PROFILE-REVIEW-01-R1`
- objective: Independently verify that the measured Wyscout source profile is
  deterministic, completion-bound, aggregate-only, complete enough for schema design,
  and derived solely from admitted durable paths.

## Files changed

- `tests/security/test_w04_wyscout_profile_review.py`
- `reports/reviews/W04/wyscout-source-profile-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-PROFILE-REVIEW-01-R1.md`

## Summary

- Independently streamed and hash/size-verified every completion-declared direct JSON
  object and all ten admitted archive members without opening ZIPs or excluded
  members.
- Recomputed direct, admitted, per-member, period, ID, formation, mapping, temporal,
  position, and match-bound relationships using exact `Decimal` JSON numbers.
- Proved check mode is static-network/archive-free, read-only, byte-stable, and
  aggregate-only; local-only verification also passes.
- Reproduced P1/P2 completeness and path-control defects: missing exact completion
  bridge/paths, admitted league coverage, event-record identity, match-bound fact
  evidence, exact temporal precision, minutes shapes, coordinate anomalies, and
  repository-bounded output.
- Challenged all nine schema-design R3 corrections. Corrections 1, 2, 3, 7, 8, and 9
  lack required measured inputs; 5 must remain unknown pending serial master-owned
  authority, and 4/6 are design-owned.
- Recommendation: **REWORK**. This is not self-approval.

## Tests run

- command:
  `uv run pytest -q tests/unit/test_wyscout_profile.py tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `1`
  - result: `1 failed, 9 passed in 78.51s`; sole failure is the intentional
    source-profile completeness gate enumerating every missing required aggregate.
- command: `uv run python scripts/profile_wyscout_v5.py --check`
  - exit status: `0`
  - result: `profile check passed: reports/phase-gates/W04/source-schema-profile.md`
- command:
  `uv run ruff format --check tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `uv run ruff check tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: validator status `PASS`; failures `[]`

## Artifacts/evidence

- `tests/security/test_w04_wyscout_profile_review.py`
  - manifest-declared streamed recomputation with a 16 MiB item buffer
  - per-member/admitted coverage and cross-partition reconciliation
  - event-record identity, mapping, match-bound team, period/time, formation/minutes
    shapes, coordinates, privacy, excluded-member, determinism, and path checks
- `reports/reviews/W04/wyscout-source-profile-review-R1.md`
- Completion SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Reproduced gate: one expected completeness failure, nine passes.

## Risks

- Schema design must not consume the current global counts as five-league coverage.
- Binary-float formatting hides exact `eventSec` lexical scale up to 18 decimal
  places.
- Exact minutes/terminal and possession semantics remain unsupported and must not be
  inferred.
- Three coordinate values are outside 0–100 and need explicit anomaly policy.
- Arbitrary non-check output paths remain possible until producer rework.

## Follow-up items

- Return a bounded producer rework packet covering only the findings in the audit.
- Rerun this independent suite after producer correction; do not dispatch schema
  design R3 until it passes.

## Scope confirmation

- no Git operations: one read-only `git status --short` inspection was invoked during
  reviewer workspace inspection; no Git metadata/state mutation, add, commit, tag,
  branch, remote, or hook operation occurred.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no producer, orchestration, configuration, source, data, migration, run, dependency,
  or protected-fixture edits: confirmed.
- no provider, network, external service, archive extraction, cloud, container,
  public endpoint, or deployment access: confirmed.
- no delegation: confirmed.
- no self-approval: confirmed; **REWORK** is an independent recommendation.

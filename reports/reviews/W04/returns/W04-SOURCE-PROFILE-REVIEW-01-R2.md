# Subagent return

## Task

- task_id: `W04-SOURCE-PROFILE-REVIEW-01-R2`
- objective: Independently verify the corrected measured Wyscout profile and all six
  R1 defects without Git, provider access, data mutation, or producer-count trust.

## Files changed

- `tests/security/test_w04_wyscout_profile_review.py`
- `reports/reviews/W04/wyscout-source-profile-review-R2.md`
- `reports/reviews/W04/returns/W04-SOURCE-PROFILE-REVIEW-01-R2.md`

## Summary

- Retained the complete R1 independent recomputation and completeness gate.
- Extended the bounded full-snapshot stream to independently compute exact Decimal
  eventSec ranges/scale and per-match-period maxima, substitution-minute bounds,
  player/match pair coverage, coordinate axis ranges/anomaly split, and identifying
  label privacy.
- Reconciled every exact completion object/member inventory row and bound the tracked
  report to exact byte count/SHA-256.
- Added independent production CLI challenges proving unreviewed source, output, and
  digest overrides fail without output or tracked-report mutation.
- Confirmed all six R1 defects are closed and every schema-design R3 input is measured
  or explicitly unsupported.
- Recommendation: **ACCEPT**. This is not self-approval.

## Tests run

- command:
  `uv run pytest -q tests/unit/test_wyscout_profile.py tests/security/test_w04_wyscout_profile_review.py`
  - exit status: `0`
  - result: `15 passed in 91.69s`
- command: `uv run python scripts/profile_wyscout_v5.py --check`
  - exit status: `0`
  - result: profile check passed against the approved tracked output
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
- `reports/reviews/W04/wyscout-source-profile-review-R2.md`
- Completion SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Profile bytes/SHA-256:
  `18,574` /
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`
- Independent aggregates: 1,826 matches; 3,071,395 events; 50,522 non-zero
  player/match pairs; three retained coordinate anomalies

## Risks

- Evidence covers only the five completion-admitted domestic partitions; scope
  exclusions remain unprofiled by design.
- Exact player minutes and per-90 denominators remain unsupported and must stay
  suppressed.
- Aggregate integrity does not establish individual record-level football semantics.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no producer, config, source, script, orchestration, dependency, migration, data,
  run, profile-design, container, or protected-fixture edits: confirmed.
- no provider, network, external-service, credential, remote, cloud, deployment, or
  public-bind access: confirmed.
- no ZIP object or excluded-member payload was opened: confirmed.
- no delegation: confirmed.
- no self-approval: confirmed; **ACCEPT** is an independent recommendation.

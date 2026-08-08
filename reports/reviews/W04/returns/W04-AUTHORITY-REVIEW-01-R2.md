# Subagent return

## Task

- task_id: `W04-AUTHORITY-REVIEW-01-R2`
- objective: Independently rerun the W04 authority boundary after the approved URL
  exception was bound to literal absolute path equality, retain all R1 challenges, and
  recommend ACCEPT or further REWORK.

## Files changed

- `reports/reviews/W04/authority-boundary-audit-R2.md`
- `reports/reviews/W04/returns/W04-AUTHORITY-REVIEW-01-R2.md`

## Summary

- Read back the verifier-only correction: `is_allowed_config_url` now requires direct
  equality with `ROOT / W04_SOURCE_CONFIG` plus exact URL allowlist membership.
- Confirmed the literal canonical authority path remains allowed.
- Confirmed both the R1 parent-segment alias and symlink alias now reject.
- Retained and reran the unchanged independent R1 URL, rights-inheritance,
  archive/five-competition, temporal-availability, claim-boundary, and cross-artifact
  challenges.
- Confirmed the producer independently added parent and symlink alias regressions.
- No new `P0`–`P2` defect was reproduced.
- Recommendation: **ACCEPT**. This is a reviewer recommendation only and not
  self-approval or a phase decision.

## Tests run

- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: `26 passed`.
- command:
  `uv run ruff format --check tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: one file already formatted.
- command:
  `uv run ruff check tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: all checks passed.
- command:
  `uv run mypy tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: no issues found in one source file.

## Artifacts/evidence

- `tests/security/test_w04_source_authority_boundary.py`
  - unchanged retained R1 independent challenge matrix
  - `test_url_exception_rejects_nonliteral_authority_path_variants` now passes
- `tests/governance/test_w04_source_authority.py`
  - producer-owned canonical, parent-path, and symlink regressions pass
- `reports/reviews/W04/authority-boundary-audit-R2.md`
  - complete correction readback, evidence mapping, residual boundary, and final
    ACCEPT recommendation
- Combined executable result: `26 passed`.

## Risks

- The URL exception is intentionally literal-path and exact-string based. Any future
  authority relocation or URL revision must receive an explicit reviewed change.
- This static review does not claim provider acquisition, file digests, extraction,
  record counts, data quality, modeling, or serving evidence.
- The master retains fresh integration, local-only, phase-gate, and checkpoint
  authority.

## Follow-up items

- Master independently inspect this R2 audit and return, reproduce the bounded checks,
  and decide the W04 authority task. No implementation correction is requested by this
  review.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.
- no reviewer-test changes: confirmed; every R1 challenge remains unchanged.
- no implementation, configuration, authority, policy, documentation, orchestration,
  fixture, data, or run-artifact edits: confirmed.
- no protected fixture or real provider-data access: confirmed.
- no network access, external service, credential, public bind, or deployment:
  confirmed.
- no delegation: confirmed.
- no Docker operation: confirmed.
- no self-approval or phase-gate claim: confirmed; **ACCEPT** is a recommendation to
  the master.

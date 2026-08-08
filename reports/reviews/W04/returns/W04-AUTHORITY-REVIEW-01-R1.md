# Subagent return

## Task

- task_id: `W04-AUTHORITY-REVIEW-01-R1`
- objective: Independently challenge the frozen Wyscout v5 source authority,
  local-only URL exception, rights inheritance, five-competition boundary, temporal
  availability, and claim restrictions.

## Files changed

- `tests/security/test_w04_source_authority_boundary.py`
- `reports/reviews/W04/authority-boundary-audit-R1.md`
- `reports/reviews/W04/returns/W04-AUTHORITY-REVIEW-01-R1.md`

## Summary

- Added independent exact-URL and equivalent-URL-spelling denial checks.
- Added rights-inheritance mutations proving the upstream CC BY grant cannot enable
  project raw export, post-acquisition network transfer, external sharing, remote
  storage, public display, or external model use.
- Added exact five-domestic-partition, tournament/unknown/traversal member, and archive
  safety-switch challenges.
- Added temporal mutations proving availability cannot precede the frozen collection
  release or use acquisition time, plus six forbidden-claim mutations.
- Reproduced one `P2`: `is_allowed_config_url` resolves the authority path before
  comparison, so a `..` alias and a symlink alias both inherit the normative config's
  URL exception.
- Recommendation: **REWORK**. This is a reviewer recommendation only and not
  self-approval or a phase decision.

## Tests run

- command: `uv run pytest -q tests/governance/test_w04_source_authority.py`
  - exit status: `0`
  - result: `7 passed`.
- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit status: `1`
  - result: `25 passed, 1 failed`; the sole failure is the retained non-literal
    authority-path reproduction.
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
  - failing reproduction:
    `test_url_exception_rejects_nonliteral_authority_path_variants`
  - passing URL, rights, archive, temporal, and claim-boundary challenges
- `reports/reviews/W04/authority-boundary-audit-R1.md`
  - complete readback, evidence mapping, ranked defect, reproduction, bounded
    correction, and REWORK recommendation
- Combined executable result: `25 passed, 1 failed`.

## Risks

- `P2`: a non-literal alias of the normative W04 config inherits the local-only URL
  exception because the verifier resolves the input path before comparing it.
- Arbitrary external destinations were not admitted; exact URL membership still
  rejects every challenged URL variant.
- This review does not claim acquired provider files, safe extraction, data quality,
  record counts, modeling, or serving evidence.
- The master retains correction allocation, rerun, phase-gate, and checkpoint
  authority.

## Follow-up items

- Require literal absolute equality with
  `ROOT / "configs/sources/w04-provider.yaml"` before granting the reviewed URL
  exception; do not follow symlinks or normalize parent segments for this identity
  check.
- Add producer-owned regressions for parent-path and symlink aliases.
- Rerun this independent reviewer packet after master acceptance of the bounded
  correction.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.
- no implementation, configuration, policy, documentation, orchestration, fixture,
  data, or run-artifact edits: confirmed.
- no protected fixture or real provider-data access: confirmed.
- no network access, external service, credential, public bind, or deployment:
  confirmed.
- no delegation: confirmed.
- no Docker operation: confirmed.
- no self-approval or phase-gate claim: confirmed; **REWORK** is a recommendation to
  the master.

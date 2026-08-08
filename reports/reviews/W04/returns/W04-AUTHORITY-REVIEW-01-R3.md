# Subagent return

## Task

- task_id: `W04-AUTHORITY-REVIEW-01-R3`
- objective: Independently review the archive-scope correction so each Wyscout ZIP has
  five admitted domestic members plus two exact known scope-excluded tournament
  entries with no extraction/admission authority, while every other member fails
  closed.

## Files changed

- `tests/security/test_w04_source_authority_boundary.py`
- `reports/reviews/W04/authority-boundary-audit-R3.md`
- `reports/reviews/W04/returns/W04-AUTHORITY-REVIEW-01-R3.md`

## Summary

- Retained every R1/R2 URL, path, rights, archive, temporal, claim, and
  cross-artifact challenge.
- Extended the independent archive invariant to require exactly five unique admitted
  and two unique known-excluded members per archive.
- Verified both seven-entry declared sets exactly match the recorded directory
  preflight without opening either ZIP or member payload.
- Proved admitted and excluded sets are disjoint and the handling authority is exactly
  directory verification without extraction or admission.
- Added four reclassification mutations proving neither tournament member can enter
  its archive’s admitted list.
- Added six representative unknown/eighth-member mutations and four admitted/excluded
  duplicate mutations, all of which fail the frozen scope.
- Retained mandatory rejection for unknown members, links, absolute paths, and parent
  paths.
- No new `P0`–`P2` defect was reproduced.
- Recommendation: **ACCEPT**. This is a reviewer recommendation only and not
  self-approval or a phase decision.

## Tests run

- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - baseline result before R3 additions: `26 passed`.
- command:
  `uv run ruff format tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: one file reformatted, then left unchanged after the parsing correction.
- command:
  `uv run ruff check tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: all checks passed.
- command:
  `uv run mypy tests/security/test_w04_source_authority_boundary.py`
  - exit status: `0`
  - result: no issues found in one source file.
- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - initial expanded exit status: `1`
  - initial expanded result: `40 passed, 3 failed`; reviewer-only Markdown parsing and
    equivalent-wording assumptions, not authority failures.
- command:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - final exit status: `0`
  - final result: `43 passed`.
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
  - `test_archive_scope_matches_exact_recorded_seven_entry_preflight`
  - `test_known_tournament_members_are_disjoint_and_have_no_payload_authority`
  - `test_scope_excluded_members_cannot_be_reclassified_as_admitted`
  - `test_any_other_archive_member_remains_unknown_and_denied`
  - `test_duplicate_archive_members_fail_the_frozen_scope`
- `reports/reviews/W04/authority-boundary-audit-R3.md`
  - complete correction readback, evidence mapping, residual boundary, and ACCEPT
    recommendation
- Final combined result: `43 passed`.

## Risks

- This packet verifies authority declarations and recorded directory evidence; it does
  not implement or test ZIP extraction, archive-bomb controls, acquired digest checks,
  record counts, or data-product construction.
- The reviewer did not access provider archives or real payloads. Preflight facts came
  only from the master-owned report.
- A future archive member or scope change must receive explicit authority and remain
  unknown/denied until reviewed.
- The master retains acquisition, full integration, phase-gate, and checkpoint
  authority.

## Follow-up items

- Master independently inspect the additive reviewer tests and R3 artifacts, reproduce
  the bounded checks, and decide the authority review. No correction is requested by
  this reviewer.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.
- no source, configuration, authority, policy, documentation, orchestration,
  migration, implementation, data, or run-artifact edits: confirmed.
- no protected fixture, provider archive, or real provider-payload access: confirmed.
- no network access, external service, credential, public bind, or deployment:
  confirmed.
- no delegation: confirmed.
- no Docker operation: confirmed.
- no self-approval or phase-gate claim: confirmed; **ACCEPT** is a recommendation to
  the master.

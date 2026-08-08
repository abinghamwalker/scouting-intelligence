# Subagent return

## Task

- task_id/revision: W08-EXPORT-INTEGRITY-03B-R2
- objective: Prove that only an entry's latest assignment can confer non-author access to its `OWNER_ONLY` history in a local evidence pack.

## Exact current-assignment invariant

- Assignment-based access is derived solely by joining each shortlist entry to its `latest_revision`; an assignment in any earlier retained revision is never used as a visibility grant.
- An otherwise authorised exporter sees `TEAM` records, records they authored, and `OWNER_ONLY` records belonging to entries currently assigned to them. Full retained history remains included only after that per-record visibility decision.
- The pack's `workflow_action_origins` is calculated only from included comment and observation rows. A former assignee therefore receives neither another author's private record nor that record's `human_entered_local` origin as a side channel.

## Files changed

- `src/scouting/operations/evidence_export.py`
- `tests/security/test_w08_export_boundaries.py`
- `reports/reviews/W08/returns/W08-EXPORT-INTEGRITY-03B-R2.md`

## Positive/negative proof

- The new synthetic automated adversarial witness makes one analyst the entry's former assignee in revision 1, a second analyst its current assignee in revision 2, and a third analyst the private-record author.
- The former assignee retains a separate current assignment so they are permitted to export the shared shortlist, but their pack omits the target's owner-only comment and observation and has `workflow_action_origins == ["synthetic_automated_test"]`.
- The current assignee receives those owner-only rows and both exact origins. The author receives their own owner-only rows despite assignment being on a different entry. All three receive the team record.
- The model/evaluation boundary is unmodified: `NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE`, `resemblance_only`, `synthetic_development_only`, and `LIMITED` remain fixed; no participant evidence is asserted.

## Tests run

- command: `uv run ruff format --check src/scouting/operations/evidence_export.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/operations/evidence_export.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: all focused lint checks passed.
- command: `uv run mypy src/scouting/operations/evidence_export.py`
  - exit status: 0
  - result: success; no issues found in 1 source file.
- command: `uv run pytest -q tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_auth_audit.py tests/unit/test_guarded_storage.py`
  - exit status: 0
  - result: 42 passed in 0.83s, including current-assignee, former-assignee, author, history, tamper, revocation and recovery witnesses.

## Risks

- Current assignment and current author status are evaluated at export time. This is deliberate fail-closed local access control; it does not recreate former grants.
- Local same-host administrator risk and the genuine moderated representative-user evidence requirement remain unresolved and unchanged.

## Scope confirmation

- no Git operations: confirmed.
- no dependency or lockfile changes: confirmed.
- no external access or protected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

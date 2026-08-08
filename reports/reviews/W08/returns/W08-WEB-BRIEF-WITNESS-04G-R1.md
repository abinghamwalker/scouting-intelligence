# Subagent return

## Task

- task_id: `W08-WEB-BRIEF-WITNESS-04G`, revision `R1`
- objective: close the local role-brief history seam with a lawful six-version
  witness and fixed public W07 brief-input controls.
- exact invariant: create, submit, reject, correct, resubmit and approve append
  exactly versions `1..6`; a failed role, tenant, form, CSRF or stale-correction
  attempt changes neither revision count, lock version nor role-brief audit count.

## Files changed

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/queue.html`
- `apps/web/templates/w08/brief.html`
- `tests/integration/test_w08_local_workflow_app.py`
- `reports/reviews/W08/returns/W08-WEB-BRIEF-WITNESS-04G-R1.md`

## Summary

- The queue obtains its fixed options from `w07_default_request()` at render time:
  template `w08-local-template`, taxonomy
  `w05-football-responsibility-taxonomy-v1` / `v1`, responsibilities
  `advance_play_final_third` and `progress_through_pressure`, public query-player
  exemplar `20000000-0000-4000-8000-000000000001`, and the supported local control
  constraint `synthetic_age_years` / `at_most` / `40`.
- The create and correction forms have no free-form taxonomy or UUID field. Their
  server parser validates responsibility, preference dimension/weight,
  constraint and exemplar against the same retained allowlists before any write.
- Status reconstruction now faithfully rehydrates persisted enum and UUID fields,
  allowing exact immutable content to flow from create through submit/reject and
  correction through resubmit/approval without replay changes.
- The history table uses scoped headers and explicitly says retained weights are
  replay context, not W05 scoring or quality evidence.

## Six-version field map and negative witnesses

| Version | Status | Created by | Content |
| --- | --- | --- | --- |
| 1 | draft | analyst | original title, `advance_play_final_third`, age-at-most 40, weight 0.5, public W07 exemplar |
| 2 | submitted | analyst | identical to v1 |
| 3 | rejected | approver | identical to v1; `requirements_unclear` and retained controlled note |
| 4 | draft | analyst | corrected title and `progress_through_pressure`; submission/decision fields cleared |
| 5 | submitted | analyst | identical to v4 |
| 6 | approved | approver | identical to v4 |

- The TestClient witness asserts all six rows, `lock_version == latest_version == 6`,
  six matching role-brief audit receipts, stable template/taxonomy/trace/owner,
  attributable actors and required timestamps.
- Direct scout/admin creation, invalid responsibility/constraint/preference/exemplar,
  invalid rejection reason, bad CSRF, stale correction and a foreign local-runtime
  brief ID return generic denial and retain the baseline `(revision_count, lock,
  audit_count) == (6, 6, 6)`.

## Tests run

- `uv run ruff format --check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: 3 files already formatted.
- `uv run ruff check src/scouting/web/w08.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: all checks passed.
- `uv run mypy src/scouting/web/w08.py`
  - exit status: 0
  - result: success; one source file.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: 6 passed; one pre-existing third-party TestClient deprecation warning.

## Artifacts/evidence

- `tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_six_version_brief_witness_and_atomic_denials`
- `reports/reviews/W08/returns/W08-WEB-BRIEF-WITNESS-04G-R1.md`

## Risks

- This is explicitly synthetic automated system evidence only. It establishes no
  representative-user result, expert relevance, model quality, recommendation or
  production-readiness claim.

## Follow-up items

- Independent review and master reproduction of this packet are required before
  acceptance; representative-user participation remains outside this packet.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

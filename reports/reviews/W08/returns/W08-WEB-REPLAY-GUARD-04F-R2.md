# Subagent return

## Task

- task_id: `W08-WEB-REPLAY-GUARD-04F`, revision `R2`
- invariant: existing and newly created links equal a fresh exact double replay, and
  the UI can submit only ordered candidates from that same persisted link's fresh result.

## Files changed

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/brief.html`
- `apps/web/templates/w08/shortlist.html`
- `tests/integration/test_w08_local_workflow_app.py`
- `reports/reviews/W08/returns/W08-WEB-REPLAY-GUARD-04F-R2.md`

## Summary

- Added one exact fresh replay projection containing tenant, deterministic link ID,
  request ID/requested-at, retained trace/brief/version, query digest/mode/exemplars,
  result/run/wrapper/lineage digests, model/index/taxonomy/candidate-universe identity,
  ordered candidate IDs, applicability and limitations.
- Every retrieval-link POST now runs fresh double replay before the existing-link
  branch. Existing links are checked field-for-field against the fresh projection;
  deterministic link ID, owner/creator, and offset-aware created-at window are also
  checked. A valid retry writes neither another link nor another receipt.
- Brief detail fails closed on a mismatching persisted link and renders every projection
  field, requested-at, and explicit `NO_GO` / `resemblance_only` /
  `synthetic_development_only` / `LIMITED` / `no_recommendation_evidence` boundary.
  It restores the analyst shortlist-creation form using only verified exact links.
- Shortlist detail fresh-verifies each exact link and offers one ordered
  `candidate_selection` dropdown of `link_id:player_id` values. It has no free-form
  player field. Entry POST rechecks brief/version ownership, projection equality and
  exact candidate membership before service/audit mutation.

## Projection and route map

- `POST /w08/briefs/{brief_id}/retrieval`: fresh-double replay → complete projection
  → existing persisted-link equality comparison or one immutable link write.
- `GET /w08/briefs/{brief_id}`: fresh projection equality check and complete metadata
  rendering; mismatch is generic denial.
- `GET /w08/shortlists/{shortlist_id}`: verified-link ordered candidate dropdown.
- `POST /w08/shortlists/{shortlist_id}/entries`: selected link belongs to exact
  shortlist brief/version → projection comparison → candidate membership allowlist →
  unchanged workflow service mutation.

## Witnesses

- Valid repeat leaves one link and one link-create audit receipt.
- Positive candidate is selected from the rendered W08 exemplar-plus-constraint replay,
  never a W07 default player-query result.
- Random candidate and a candidate selection from another link/brief return generic
  denial with entry/audit counts unchanged.
- The append-only trigger rejects a direct persisted-link update. In a fresh isolated
  `tmp_path` test database only, the exact link-update trigger is then dropped and one
  digest is corrupted; both detail and idempotent link POST fail closed with counts
  unchanged. No repository/runtime database was altered.
- An injected alternating second replay projection denies link creation with unchanged
  link/audit counts.

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
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/e2e/test_w05_m0_retrieval.py`
  - exit status: 0
  - result: 8 passed; one third-party TestClient deprecation warning.

## Artifacts/evidence

- `tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_replay_guard_projection_and_candidate_allowlist`
- `reports/reviews/W08/returns/W08-WEB-REPLAY-GUARD-04F-R2.md`

## Risks

- These are synthetic automated mechanics tests only; they provide no representative-
  user, expert relevance, model-quality, recommendation, transfer, value or
  production-readiness evidence.

## Follow-up items

- Independent review and master reproduction remain required before acceptance.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

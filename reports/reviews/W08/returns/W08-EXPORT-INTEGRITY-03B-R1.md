# Subagent return

## Task

- task_id: W08-EXPORT-INTEGRITY-03B-R1
- objective: Correct the local evidence pack so it exports complete authorised history and exact persisted workflow-action provenance without widening the model claim boundary.

## Files changed

- `src/scouting/operations/evidence_export.py`
- `tests/integration/test_w08_evidence_export.py`
- `tests/security/test_w08_export_boundaries.py`
- `reports/reviews/W08/returns/W08-EXPORT-INTEGRITY-03B-R1.md`

## Exact history/provenance invariant

- For the selected same-tenant shortlist, the canonical pack contains every retained shortlist-entry revision ordered by `(shortlist_entry_id, revision)`, every exporter-visible comment ordered by `(created_at, comment_id)`, and every exporter-visible observation version ordered by `(observation_id, version)`.
- A `TEAM` record is included only inside the already-authorised shortlist scope. An `OWNER_ONLY` comment or observation is included only when the exporter authored it or is currently assigned to its shortlist entry. Private rows are omitted without an existence indicator.
- `workflow_action_origins` is the exact sorted set of persisted `evidence_origin` values from those included comments and observation versions. It does not relabel human-entered records as synthetic, or vice versa.
- These workflow-origin labels do not affect model facts: `model_evidence` remains `synthetic_development_only`, `claim_boundary` remains `resemblance_only`, `applicability` remains `LIMITED`, and limitations retain W06 `NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE`.

## Summary

- Removed the latest-only filters for shortlist revisions and observation versions; added authorised immutable comment history.
- Recomputed underlying-values and evidence-pack hashes over that complete visible history, with the idempotent export reconstruction exercised on mixed provenance data.
- Stored the construction-time retained export policy path and validate that same path at export, read and revoke. A later drift of a custom retained path now denies export.
- Replaced the inaccurate blanket `synthetic_automated_test` workflow-provenance marker with the exact `workflow_action_origins` set. The fixtures are still synthetic automated test mechanics; a `human_entered_local` stored label is not asserted to be representative-user or moderated-study evidence.

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
  - result: 41 passed in 0.80s; all inputs are synthetic automated mechanics, not representative-user evidence.

## Adversarial proof and key choices

- The mixed-history witness includes two retained entry revisions, two visible comments with distinct persisted origins, two visible observation versions, and private comment/observation rows. It proves deterministic complete-history inclusion, exact sorted provenance, fixed model boundary and non-disclosure of private text.
- Existing focused witnesses remain green for IDOR/role denial, policy drift, tampering, append-only revocation, guarded path hazards, nested-savepoint recovery and identical retry.

## Risks

- Authorisation is evaluated against current tenant, visibility and assignment context; historic access grants are intentionally not replayed as a means to expose a currently private record.
- Local same-host administrator risk and the absence of genuine moderated representative-user evidence remain unchanged.

## Follow-up items

- Master: independently reproduce these checks and request fresh independent security review of complete-history visibility filtering before packet acceptance.

## Scope confirmation

- no Git operations: confirmed.
- no dependency or lockfile changes: confirmed.
- no external access or protected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

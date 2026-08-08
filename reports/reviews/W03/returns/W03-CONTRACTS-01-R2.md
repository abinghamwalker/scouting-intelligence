# Subagent return

## Task

- task_id: `W03-CONTRACTS-01`
- objective: Correct only the four contract-integrity defects recorded by the master,
  including the strict-before temporal-boundary governance addendum.

## Files changed

- `src/scouting/contracts/evidence.py`
- `src/scouting/contracts/workflow.py`
- `src/scouting/contracts/retrieval.py`
- `src/scouting/contracts/audit.py`
- `tests/contracts/test_foundation_contracts.py`
- `reports/reviews/W03/returns/W03-CONTRACTS-01-R2.md`

## Summary

- `RETRIEVAL_LINEAGE_NOT_BOUND_TO_TEMPORAL_PROOF`: added the required
  `retrieval_run_id` and made `RetrievalResult` reject every candidate whose complete
  dependency lineage differs from the result's validated temporal-evidence lineage.
  Focused tests cover matching, mismatched, and future candidate lineage.
- `AUDIT_MUTATION_DIGESTS_OPTIONAL`: enforced the action matrix: `CREATE` requires only
  `after_digest`; `UPDATE` and `OVERRIDE` require both digests; `DELETE` requires only
  `before_digest`. Existing override-reason requirements remain intact. Positive cases
  and every missing/incoherent digest side are tested.
- `ROLE_BRIEF_APPROVAL_TIME_UNPROVABLE`: added required `created_at` and optional
  `approved_at`. Approved briefs require an approval instant at or after creation;
  non-approved statuses reject an approval instant.
- `IDENTITY_VALID_INTERVAL_ABSENT`: added required `valid_from` and optional `valid_to`
  while preserving supersession evidence. Inverted intervals are rejected.
- Governance addendum: lineage evidence items now carry explicit `observed_at` and
  `available_at`. Both must be strictly before `feature_cutoff_ts`; equality at the
  cutoff is ineligible. Separate equality-boundary tests cover both timestamps.
- Expanded the focused suite from 15 to 32 passing tests without changing the dependency
  or primitive contracts.

## Tests run

- command: `uv run pytest -q tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: `32 passed in 0.12s`
- command:
  `uv run ruff format --check src/scouting/contracts tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: `7 files already formatted`
- command:
  `uv run ruff check src/scouting/contracts tests/contracts/test_foundation_contracts.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/contracts`
  - exit status: `0`
  - result: `Success: no issues found in 6 source files`
- command: `uv run bandit -q -r src/scouting/contracts`
  - first exit status: `2`
  - first result: workspace sandbox denied access to uv's existing external cache path;
    no source finding was emitted.
  - final exit status: `0`
  - final result: identical command rerun with narrowly scoped approval to read the uv
    cache; no Bandit findings.

## Artifacts/evidence

- `tests/contracts/test_foundation_contracts.py`
- `reports/reviews/W03/returns/W03-CONTRACTS-01-R2.md`
- Retrieval lineage binding:
  `RetrievalResult.temporal_evidence.dependency_lineage`
- Strict-before boundary:
  `EvidenceDependency.observed_at` and `EvidenceDependency.available_at`

## Risks

- The newly required `observed_at`, role-brief lifecycle timestamps, identity validity
  interval, and retrieval-run identifier must be populated by future consumers; consumer
  integration is intentionally outside this packet.
- The high-risk contract correction still requires the master's independent readback,
  rerun, and boundary review before acceptance.

## Follow-up items

- None within `W03-CONTRACTS-01-R2`; proceed to mandatory master verification.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor
  `uv.lock` was modified.
- no edits outside `allowed_paths`: confirmed.

# Subagent return

## Task

- task_id: W03-VERTICAL-01-R4
- objective: Remove development-only presentation constants by binding candidate and
  explanation presentation evidence to a strict immutable artifact profile.

## Files changed

- src/scouting/serving/__init__.py
- src/scouting/serving/synthetic.py
- tests/e2e/test_w03_vertical_journey.py
- reports/reviews/W03/returns/W03-VERTICAL-01-R4.md

## Summary

- Added and exported `RetrievalPresentationProfile`, a frozen slotted profile carried
  by `SyntheticArtifactCatalog`.
- The profile contains only six evidence dimensions, candidate confidence,
  limitations and reason codes, plus explanation reasons and a candidate-name
  template. It contains no player/candidate identity, rank, tenant, cutoff or lineage.
- Profile construction validates the complete unique dimension set, strict finite
  unit-interval scores/confidences, non-empty unique bounded reason-code tuples,
  non-empty unique bounded limitations, and exactly one plain
  `{candidate_display_name}` explanation field with no traversal, conversion or
  format specification.
- Candidate identity still comes from admitted evidence after hard constraints,
  exclusions and ambiguity quarantine. Rank remains assigned by the selection path;
  coverage remains computed from admitted/rejected evidence; lineage remains computed
  from snapshot/catalog artifacts.
- Every fixed candidate dimension, candidate confidence/limitation/reason, and
  explanation reason/template is now populated from the selected catalog profile.
  No partition branch was added.
- The development profile preserves the exact frozen development response.
- The temporary development-derived alternate-partition test now supplies a wholly
  different artifact profile and proves its scores, confidences, reasons, limitations
  and rendered explanation while the evidence-selected candidate, rank, dynamic
  coverage and catalog lineage remain independent.
- Existing repeated-input stability, distinct request-bound IDs, and missing
  model/index unavailable behavior remain covered.

## Tests run

- command: `uv run ruff format src/scouting/serving tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: 2 files reformatted; 1 file unchanged.
- command: `uv run ruff check src/scouting/serving tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/serving`
  - exit status: 0
  - result: no issues found in 2 source files.
- command: `SCOUTING_DATABASE_URL='<redacted master-supplied loopback URL>' uv run pytest -q tests/e2e/test_w03_vertical_journey.py`
  - first exit status: 1
  - first result: 32 passed, 1 development-oracle mismatch, and one existing
    Starlette/httpx warning. The mismatch was an incorrectly transcribed development
    role reason (`fullback` instead of the previously derived `wide`); only that
    profile value was corrected.
  - corrected rerun exit status: 0
  - corrected rerun result: 33 passed and one existing Starlette/httpx deprecation
    warning.
- The remaining packet checks were left for the master's independent review after the
  master requested the single corrected bounded rerun followed by immediate handback.

## Artifacts/evidence

- reports/reviews/W03/returns/W03-VERTICAL-01-R4.md
- exported type: `scouting.serving.RetrievalPresentationProfile`
- development factory: `RetrievalPresentationProfile.development()`
- alternate temporary fixture ID: `w03-temporary-alternate-partition`
- alternate profile explanation reason: `alternate_explanation_profile`
- corrected development e2e result: 33 passed.

## Risks

- Profile validity establishes strict presentation shape and provenance separation; it
  does not claim model quality, expert relevance, cross-provider score calibration,
  pilot readiness or recruitment-outcome quality.
- Presentation profiles are trusted artifact inputs selected by composition. The
  profile cannot override eligibility, identity, rank, tenant, cutoff, dynamic coverage
  or lineage.
- No protected fixture or protected expected output was accessed. The master still
  owns independent review and any brokered protected-input gate.
- TestClient continues to emit the existing upstream Starlette/httpx deprecation
  warning. Dependency changes are outside this packet.

## Follow-up items

- Master independently review the R4 changes and run the remaining packet checks
  (`ruff format --check`, final `ruff check`, final `mypy`, `bandit`, and runtime
  expected-output reference guard) before brokering any protected-input gate.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no Docker operations: confirmed; no Docker command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.
- no access to protected fixture/output paths: confirmed.
- no access to scripts or `reports/verification/W03`: confirmed.
- no self-approval or protected-gate claim: confirmed.

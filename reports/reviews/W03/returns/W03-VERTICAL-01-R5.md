# Subagent return

## Task

- task_id: W03-VERTICAL-01-R5
- objective: Correct the explanation-template constraint to support bounded static
  explanations without changing retrieval, eligibility, artifact-profile provenance or
  result behavior.

## Files changed

- src/scouting/serving/synthetic.py
- tests/e2e/test_w03_vertical_journey.py
- reports/reviews/W03/returns/W03-VERTICAL-01-R5.md

## Summary

- Explanation validation now accepts exactly two modes:
  - a bounded non-empty static string with no format field; or
  - a template with exactly one plain `candidate_display_name` field.
- Static explanations return byte-for-byte unchanged, including escaped-brace text;
  the candidate name is not interpolated into static content.
- Single-field templates continue to use Python's safe named substitution after strict
  validation and preserve candidate-name brace characters as literal inserted data.
- Unknown and positional fields, repeated/multiple fields, traversal, conversions,
  format specifications and malformed braces remain rejected.
- Added focused regressions for static rendering, single-field rendering, unknown and
  positional fields, multiple placeholders, traversal, conversion, format
  specification and both unmatched brace directions.
- Candidate selection, rank, IDs, artifact-carried presentation values, lineage,
  coverage, unavailable states, development oracle and alternate-profile behavior were
  not changed.

## Tests run

- command: `uv run ruff format src/scouting/serving tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: 1 file reformatted; 2 files unchanged.
- command: `SCOUTING_DATABASE_URL='<redacted master-supplied loopback URL>' uv run pytest -q tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: 39 passed; one existing Starlette/httpx deprecation warning.
- command: `uv run ruff format --check src/scouting/serving tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: 3 files already formatted.
- command: `uv run ruff check src/scouting/serving tests/e2e/test_w03_vertical_journey.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/serving`
  - initial exit status: 1
  - initial result: one helper return annotation treated `Formatter.parse`'s
    `format_spec` as always `str`, while its type is `str | None`.
  - correction: widened only the private helper's return annotation to `str | None`.
  - corrected exit status: 0
  - corrected result: no issues found in 2 source files.
- command: `uv run bandit -q -r src/scouting/serving`
  - initial sandbox exit status: 2
  - initial result: restricted sandbox could not read an existing uv cache path.
  - approved rerun exit status: 0
  - approved rerun result: no findings.
- command: `! rg -n "expected_retrieval\\.json" src/scouting/serving`
  - exit status: 0
  - result: no runtime reference found.
- final repeated Ruff format/check and runtime reference checks:
  - exit status: 0
  - result: formatted, lint-clean and no runtime oracle reference.

## Artifacts/evidence

- reports/reviews/W03/returns/W03-VERTICAL-01-R5.md
- accepted static examples:
  - `This is a bounded static explanation.`
  - `This static explanation preserves {{literal braces}} unchanged.`
- accepted named template:
  - `Evidence is shown for {candidate_display_name}.`
- corrected database-backed e2e result: 39 passed.

## Risks

- Static explanation strings intentionally preserve escaped brace pairs literally
  rather than applying formatting semantics, because static mode must render unchanged.
- Candidate-name mode permits only one plain field and performs no expression,
  traversal, conversion or format-specification evaluation.
- No protected fixture or expected output was accessed. The master still owns
  independent review and any brokered protected-input gate.
- This remains synthetic seam evidence and makes no model-quality, expert-relevance,
  pilot or recruitment-outcome claim.
- TestClient continues to emit the existing upstream Starlette/httpx deprecation
  warning. Dependency changes are outside this packet.

## Follow-up items

- Master independently review the R5 changes, reproduce the exact checks and broker any
  protected-input gate without exposing protected output to the implementer.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no Docker operations: confirmed; no Docker command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.
- no protected fixture or protected expected-output access: confirmed.
- no scripts or `reports/verification/W03` access: confirmed.
- no external service, public bind or destructive action: confirmed.
- no self-approval or protected-gate claim: confirmed.

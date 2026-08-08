# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-SOURCE-ADAPTER-01`
- objective: Add one narrow public source-owned adapter that returns the exact verified raw records and completion evidence for the admitted England match `2499719` without creating product bytes.

## Files changed

- `src/scouting/sources/wyscout_completion_index.py`
- `tests/unit/test_wyscout_source_completion_index.py`
- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-ADAPTER-01-R1.md`

## Summary

- Added public immutable `VerifiedMatchAction` and `VerifiedMatchPopulation` result types and `load_verified_match_population`.
- The adapter pins the accepted completion-index address, England event member and match source ID before member access; validates exact root arguments; verifies stable source-manifest bytes; loads and validates the content-addressed index; and confirms its exact member digest/count binding.
- The adapter nofollow-reads the complete 188,888,614-byte member through the existing source guard, requires exactly 643,150 decoded rows, enumerates physical ordinals before strict match filtering, and projects selected rows through `completion_action_evidence` without coercion.
- It canonical-sorts all selected evidence, validates exact full-match equality for the indexed `901 + 867 = 1,768` period population, issues the authentic checked-match capability, and only then returns 1,768 deeply immutable raw/evidence pairs. Each pair retains canonical raw bytes whose SHA-256 is checked against `raw_record_sha256`.
- Hardened the existing source-manifest byte verifier with before/after stable-file metadata comparison. Existing accepted index, R4 checked APIs, strict subevent/equal-clock behavior, and all product/data bytes remain unchanged.
- Added focused positive and adversarial coverage for strict input pins, immutable nested raw JSON, exact real counts, row truncation/addition, non-strict row identity, selected-action omission/addition/duplication/reordering, and source mutation.

## Tests run

- command: `uv run ruff format --check src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: no issues in 2 source files.
- command: `uv run lint-imports`
  - initial sandbox exit status: `2`
  - initial result: the sandbox denied read access to the existing shared uv cache; no test or implementation failure.
  - escalated cache-read rerun exit status: `0`
  - result: 3 contracts kept, 0 broken.
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: `286 passed in 115.66s`.
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py -k 'verified_match_adapter or verified_member_reader'`
  - exit status: `0`
  - result: `16 passed, 37 deselected in 3.14s`.
- command: `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py`
  - initial sandbox exit status: `2`
  - initial result: the sandbox denied read access to the existing shared uv cache; no security finding.
  - escalated cache-read rerun exit status: `0`
  - result: no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: repository local-only boundary `PASS`, 25 checks and zero failures.

## Artifacts/evidence

- implementation SHA-256: `3050b7a3c0ff47442db973fb18fee70c8bf3256827936739e63f87947cd07bed`
- focused-test SHA-256: `d01a630f1ce2c345597dde7fef81589ca14e8690515e67d8ff476d1f4063423d`
- accepted completion-index binding: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- accepted member binding: `archive-members/events_England.json`, SHA-256 `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`, 188,888,614 bytes, 643,150 rows.
- accepted match result: source ID `2499719`, 1,768 actions, `1H=901`, `2H=867`.

## Risks

- The frozen POC adapter intentionally buffers and decodes the one admitted 188,888,614-byte member before returning anything. This preserves safe post-EOF verification and is within the approved one-and-done local POC bound, but it is not a general streaming ingestion design.
- The immutable result is evidence-bearing but not independently authoritative: downstream product construction must retain and consume its authentic `CheckedCompletionPopulation`, as required by the existing R4 checked boundaries.

## Follow-up items

- Master must inspect all three files and independently rerun the packet acceptance checks before allocating any product materialization packet.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

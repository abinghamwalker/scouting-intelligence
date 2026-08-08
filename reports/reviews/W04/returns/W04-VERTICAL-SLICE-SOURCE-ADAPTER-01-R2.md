# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-SOURCE-ADAPTER-01`
- objective: Correct only the R1 mutable `CompletionActionEvidence.raw_tags` defect while preserving exact action-frame, membership, accepted-index and source-adapter behavior.

## Files changed

- `src/scouting/sources/wyscout_completion_index.py`
- `tests/unit/test_wyscout_source_completion_index.py`
- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-ADAPTER-01-R2.md`

## Summary

- Verified every packet-fixed R1 implementation, test, review, review-return, accepted-index and England-member SHA-256 before editing; all matched exactly.
- `_raw_tags_and_projection` still requires an exact JSON list of exact `{"id": strict_int}` dictionaries and still preserves duplicate raw tags while projecting sorted unique tag IDs. After validation, each retained tag is now copied into an otherwise unreachable dictionary exposed only through `MappingProxyType`, closing the normal caller mutation path.
- The canonical encoder accepts the immutable representation only when it is exactly one mapping proxy with the sole key `id` and a strict integer value. Other proxy shapes and non-strict values fail closed; ordinary canonical JSON behavior is unchanged.
- Fixed pre-correction vector assertions prove the representative action-frame remains 595 bytes with SHA-256 `5b94fec338d67564aa16e37b8eb60ec70995182c8a7dc1bd5d02c1e32b83ca4e`, and its one-action membership remains `c245045382071ae38bf26557b2acb16282db1997e0fbaf50a9a9faafc8ba6d21`.
- The real adapter regression now attempts `action.evidence.raw_tags[0]["id"] = 999999`, receives `TypeError`, and then independently consumes the same authentic checked capability with exact periods `1H=901` and `2H=867`. Their accepted membership digests remain `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b` and `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`.
- The existing accepted-index test rehashed the stored bytes to `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`; no frozen index, R20/R21 authority, source, product, dependency or other byte was changed.

## Tests run

- command: pre-edit `shasum -a 256 src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py reports/reviews/W04/wyscout-vertical-slice-source-adapter-independent-review-R1.md reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-ADAPTER-REVIEW-01-R1.md data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json data/source/wyscout/v5/archive-members/events_England.json`
  - exit status: `0`
  - result: all packet-fixed hashes matched exactly before editing.
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
  - exit status: `0`
  - result: 3 contracts kept, 0 broken.
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: `286 passed in 114.36s`.
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py -k 'action_projection or verified_match_adapter_returns'`
  - exit status: `0`
  - result: `2 passed, 51 deselected in 2.66s`.
- command: `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: repository local-only boundary `PASS`, 25 checks and zero failures.

## Artifacts/evidence

- R2 implementation SHA-256: `b1cdb309c3d81e7a3b0606987fdf6c456d61a66c393ca681d93e212e805ac43c`
- R2 source-test SHA-256: `1acb8908bd2cbb11a4f9e1d3d25ed270e5781c11e0cc6fa0c94b97d486e064f4`
- unchanged accepted index: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- unchanged England member: `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`
- retained failed-review evidence: `reports/reviews/W04/wyscout-vertical-slice-source-adapter-independent-review-R1.md`

## Risks

- No known residual P0-P2 issue in this bounded correction. Acceptance remains solely with fresh independent review and master reproduction.
- The previously accepted bounded memory-resident whole-member read remains unchanged; this packet does not generalize it into a streaming ingestion design.

## Follow-up items

- Fresh independent review must reproduce tag-evidence immutability, exact checked-capability reuse, fixed vectors and accepted-index identity before master acceptance or product dispatch.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

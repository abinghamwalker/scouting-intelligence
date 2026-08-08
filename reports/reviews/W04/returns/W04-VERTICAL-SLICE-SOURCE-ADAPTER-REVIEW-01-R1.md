# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-SOURCE-ADAPTER-REVIEW-01`
- objective: Independently review the exact bounded public source adapter for fail-closed whole-member verification, immutable raw/evidence binding and exact accepted match-population equality.

## Files changed

- `reports/reviews/W04/wyscout-vertical-slice-source-adapter-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-ADAPTER-REVIEW-01-R1.md`

## Summary

- Verdict: `REWORK`.
- Open findings: `P0=0`, `P1=1`, `P2=0`.
- All fixed candidate, index and source-member hashes and the exact member size matched.
- The source/index/member/row-count/full-match verification sequence is fail closed,
  physical ordinals precede strict filtering, and the exact `901 + 867 = 1768`
  population retains the authentic checked capability.
- One bounded P1 remains: `CompletionActionEvidence.raw_tags` retains mutable source
  dictionaries. A caller can mutate a normal adapter result and thereby poison the
  membership preimage inside its authentic checked completion capability. This
  violates the explicit deep-immutability requirement.

## Tests run

- command: `shasum -a 256 src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-ADAPTER-01-R1.md`
  - exit status: `0`
  - result: exact fixed candidate hashes matched.
- command: `shasum -a 256 data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - exit status: `0`
  - result: exact accepted index hash matched.
- command: `wc -c data/source/wyscout/v5/archive-members/events_England.json`
  - exit status: `0`
  - result: exact `188888614`-byte member size matched.
- command: `shasum -a 256 data/source/wyscout/v5/archive-members/events_England.json`
  - exit status: `0`
  - result: exact accepted member hash matched.
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py -k 'verified_match_adapter or verified_member_reader'`
  - exit status: `0`
  - result: `16 passed, 37 deselected in 3.16s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: local-only boundary `PASS`, 25 checks and zero failures.
- command: two read-only `uv run python -c` mutation probes against the exact adapter
  - exit status: `0`
  - result: `raw_tags[0]` is a mutable `dict`; assignment succeeds; the next checked-completion validation fails with `population membership differs from completion index`.

## Artifacts/evidence

- independent review: `reports/reviews/W04/wyscout-vertical-slice-source-adapter-independent-review-R1.md`
- exact defect locus: `src/scouting/sources/wyscout_completion_index.py:475-488`, `:546`, `:1048-1055`
- accepted index: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- exact member: `archive-members/events_England.json`, SHA-256 `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`, `188888614` bytes, `643150` rows.

## Risks

- P1: a returned authority-bearing evidence graph is caller-mutable through nested tag dictionaries; downstream use is blocked pending bounded correction and fresh review.
- No other P0-P2 finding remains open in the reviewed source-adapter scope.

## Follow-up items

- Deep-freeze returned evidence tag mappings without changing canonical action-frame bytes or the accepted index, add the missing mutation regression, and submit the newly hashed candidate for fresh independent review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

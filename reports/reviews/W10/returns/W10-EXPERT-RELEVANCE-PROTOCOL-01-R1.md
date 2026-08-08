# W10 expert-relevance protocol implementation return

## Task

- task_id: `W10-EXPERT-RELEVANCE-PROTOCOL-01`
- objective: Freeze the draft G-RW4 protocol, exact W09-bound query pack, participant-safe
  presentation, contracts and an evidence-honest pre-study boundary.

## Files changed

- `orchestration/task_packets/W10-EXPERT-RELEVANCE-PROTOCOL-01-R1.yaml`
- `reports/reviews/W10/returns/W10-EXPERT-RELEVANCE-PROTOCOL-01-R1.md`
- `src/scouting/contracts/expert_relevance.py`
- `src/scouting/contracts/__init__.py`
- `scripts/build_w10_expert_protocol.py`
- `configs/evaluation/w10-expert-relevance-protocol-v1.json`
- `configs/evaluation/w10-frozen-query-pack-v1.json`
- `configs/evaluation/w10-expert-study-presentation-v1.json`
- `tests/contracts/test_w10_expert_relevance_contracts.py`
- `reports/verification/W10/preflight.md`
- `reports/verification/W10/expert-relevance-protocol.md`

## Summary

- Frozen a draft protocol with eight balanced historical-player queries, five accepted W09
  retrieved candidates and five blinded governed controls per query, plus two exact delayed
  repeat anchors.
- Bound every query to exact W09 request, result and product identities while excluding evaluator
  provenance, arm, rank, score and protected labels from the participant-safe presentation.
- Preregistered eligibility, consent, completion, coverage, metric, uncertainty, agreement,
  repeat-consistency, PASS, FAIL and INSUFFICIENT_EVIDENCE rules before any formal response.
- Added strict contracts for approval, sessions, judgements, submissions, receipts and results.
- Bound the exact participant-keyed interleaving algorithm, ten-primary repeat delay,
  nonterminal constraint and nonadjacency constraint into the final presentation digest.
- Retained the protocol as a frozen draft awaiting separate human approval; no participant or
  outcome evidence was created.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w10_expert_relevance_contracts.py`
  - exit status: `0`
  - result: `8 passed`
- command: `uv run ruff format --check src/scouting/contracts/expert_relevance.py scripts/build_w10_expert_protocol.py tests/contracts/test_w10_expert_relevance_contracts.py`
  - exit status: `0`
  - result: all files formatted
- command: `uv run ruff check src/scouting/contracts/expert_relevance.py scripts/build_w10_expert_protocol.py tests/contracts/test_w10_expert_relevance_contracts.py`
  - exit status: `0`
  - result: all checks passed
- command: `uv run mypy src/scouting/contracts/expert_relevance.py scripts/build_w10_expert_protocol.py`
  - exit status: `0`
  - result: no issues

## Artifacts/evidence

- Protocol digest: `7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f`
- Query-pack digest: `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5`
- Presentation digest: `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`
- `reports/verification/W10/preflight.md`
- `reports/verification/W10/expert-relevance-protocol.md`

## Risks

- The protocol has not been approved by the user and no real eligible expert has participated.
  G-RW4 therefore has no positive or negative formal result.
- Eight queries support this bounded preregistered gate; subgroup outputs remain descriptive and
  cannot justify broader recruitment or current-market claims.

## Follow-up items

- Present the concise protocol decision page and one local continuation URL after the independently
  reviewed engineering-ready candidate is complete.
- Collect only authentic eligible expert submissions after explicit approval.

## Scope confirmation

- Git operations were performed only by the master as authorised.
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

# Subagent return

## Task

- task_id: `W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01`
- objective: Independently review the additive W04 Parquet encoder and semantic
  digest for exact physical controls, unambiguous binding and strict fail-closed
  schema/key/row behaviour.

## Files changed

- `reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R1.md`

## Summary

- Verdict: `REWORK`.
- Findings: `P0 0 / P1 1 / P2 0`.
- All fixed candidate hashes and both fixed vectors matched.
- Exact physical controls, framing, three row-group boundaries, timestamp denial,
  generic serializer preservation and local-only controls passed.
- P1 `W04_ENCODER_ARROW_CONTRACT_ROW_BINDING_MISSING`: the encoder hashes supplied
  contract rows without proving they represent the Arrow table. A changed non-key
  Arrow value produced different physical bytes but the unchanged baseline semantic
  digest. String keys for integer Arrow columns and Boolean `true` against integer
  key `1` were also accepted.
- Bounded rework must add exact full-row Arrow-to-contract correspondence and strict
  Arrow-derived key/type binding with the adversarial tests named in the review.

## Tests run

- command: `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R1.md`
  - exit status: `0`
  - result: all packet-fixed hashes matched before analysis and before rendering.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent fixed-vector, semantic-preimage, framing and mandatory divergence probe>`
  - exit status: initial sandbox `2`, approved identical rerun `0`
  - result: fixed vectors reproduced; framing/uint64 controls passed; non-key
    divergence and string/Boolean key-type bypasses were accepted, proving P1.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent row-group/timestamp probe>`
  - exit status: `0`
  - result: `[65535]`, `[65536]`, `[65536,1]`; nanosecond timestamp rejected.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `50 passed in 1.74s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 local-only controls, zero configured remotes.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R1.md`
- physical vector:
  `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- semantic vector:
  `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`

## Risks

- P1: until corrected, a caller can pair Parquet physical bytes with a semantic
  digest that claims different row values; publication use is unsafe.
- No other open P0-P2 finding was identified in this bounded review.

## Follow-up items

- Return only the bounded P1 correction and named adversarial tests to the producer,
  then obtain fresh master verification and independent review of new fixed hashes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation, test, data, product, manifest, receipt, source, provider,
  network, cloud, container, hosted CI, endpoint, remote or deployment action:
  confirmed
- no delegation or self-approval: confirmed

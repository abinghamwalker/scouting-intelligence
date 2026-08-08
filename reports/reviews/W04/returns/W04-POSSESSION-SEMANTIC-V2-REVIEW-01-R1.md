# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R1`
- objective: Independently review the possession-v2 authority and focused
  contract against R20/R21, including the distinction between exact predicate
  lookup and completed same-period possession resolution.

## Files changed

- `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R1.md`

## Summary

- Reconstructed the exact decision and candidate bytes, physical/canonical
  digests, five bound inputs, 17-key v1 predecessor, and 36 predicate rows.
- Confirmed all 36 predicate rows remain byte-semantically equal to v1, with
  the exact `4/11/8/2/7/4` decision distribution and `18/18`
  `ACTION_TEAM`/`NONE` split.
- Confirmed the strict canonical selector rejects missing, mistyped, boolean,
  string, numeric-looking-string, null, non-integer, unsorted/duplicate-tag,
  unknown-pair, and missing required-team cases, and does not consume raw,
  rejected, name, or label values.
- Issued `REWORK` with one P1 finding,
  `SEQUENCE_RESOLUTION_OVERCLAIM`: the candidate and focused helper assign
  `ELIGIBLE_RESOLVED` immediately after exact non-`UNMAPPED` predicate lookup
  without proving the unchanged R20 ordered same-period sequence rules.
- No candidate, test, acceptance, downstream authority, or product path was
  changed or created.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<independent candidate reconstruction>'`
  - exit status: `2` on the first sandboxed attempt
  - result: the existing uv cache was outside the restricted read sandbox; no
    project file or environment was changed
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<independent candidate reconstruction>'`
  - exit status: `0` after approved local-cache read
  - result: canonical candidate SHA-256
    `54c2dcca6e84ef1cdb174a41a4c35f05a224f216513bdf1408422aa7c93f7452`;
    10 decision keys, 9 candidate keys, 5 inputs, 17 predecessor keys, 36
    predicates; v1 predicate equality confirmed
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: `0`
  - result: `321 passed in 25.04s`; the actual authority state is valid
    `REVIEW_REWORK`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25 checks, failures empty

## Artifacts/evidence

- review:
  `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md`
- review ID:
  `w04-wyscout-possession-semantic-independent-review-v2-R1`
- recommendation and finding cardinality: `REWORK`; `P0=0`, `P1=1`, `P2=0`
- review physical SHA-256:
  `71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a`
- fenced canonical review-record SHA-256:
  `9d42535376164183079ab642f51a43b35bda33e660627ebcce98e166787bd111`
- decision physical/canonical SHA-256:
  `3198178feef14886be3cf65dbc98a0b3b34d87a74102d2c54a470e23079a4973`
- candidate physical SHA-256:
  `6c739f674894d6c605cbd5beccb0ad074f0b64f2447efe664438764458b84d7c`
- candidate canonical SHA-256:
  `54c2dcca6e84ef1cdb174a41a4c35f05a224f216513bdf1408422aa7c93f7452`
- focused contract physical SHA-256:
  `1e19d73952711affbb85707a8b21269a02f0aba6653d9faf319b49eb4b89dbe4`
- shell-only pre-Python inventory: 1,145 `.pyc` files, 150
  `__pycache__` directories, 1,295 sorted path rows, SHA-256
  `38de1f6ddc5e8086bba61d3c63dfb2acd71a7e00a1c3a7b0c17fbf492601c034`

## Risks

- Possession-v2 cannot be accepted in its current form. Treating predicate
  admission as sequence resolution would overcount
  `resolved_possession_action_count`, especially for contested, dead-ball, and
  administrative actions whose attachment depends on surrounding same-period
  state.
- This is bounded authority/test rework. No architecture, product, provider,
  rights, dependency/lock, storage, or local-only change is required by the
  finding.

## Follow-up items

- Return the possession-v2 decision/candidate/focused contract to the producer
  for bounded rework that separates exact predicate lookup from deterministic
  same-period sequence resolution and adds positive/negative R20 sequence
  cases.
- Repeat fresh independent review after the corrected candidate and focused
  contract pass master readback. Do not create possession-v2 acceptance or
  downstream feature/product authority before then.

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`
- no delegation, self-approval, provider/network access, candidate/test edit,
  acceptance, feature/cross-authority work, or product implementation:
  `confirmed`

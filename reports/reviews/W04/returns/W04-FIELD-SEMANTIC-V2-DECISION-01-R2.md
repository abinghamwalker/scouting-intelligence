# Subagent return

## Task

- task_id: W04-FIELD-SEMANTIC-V2-DECISION-01-R2
- objective: Materialize the unchanged R21 field-semantic v2 decision and candidate at their exact absolute project-root paths, with a focused fail-closed contract suite.

## Files changed

- reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json
- configs/schema/wyscout-v5-field-registry-v2.yaml
- tests/contracts/test_w04_field_semantic_v2_authority.py
- reports/reviews/W04/returns/W04-FIELD-SEMANTIC-V2-DECISION-01-R2.md

## Summary

- Recreated the canonical field-v2 decision and strict YAML candidate from the accepted field-v1 authorities and the single frozen R21 `(action, $.subEventId)` replacement.
- Preserved the exact 119-row R20 roster and all source shapes: 118 rows are semantically identical to v1 and row index 106 is the sole changed row.
- Closed the ten input bindings, seventeen-key immutable v1 prior authority, strict-integer frozen taxonomy-pair transform, all seven preserve-unmapped reasons, and exact no-coercion behavior.
- Added progression-safe future review and acceptance validation. Absence is valid now; a future state must use the exact v2 IDs and digests, an independent canonical actor, ordered truthful clocks, a valid `PASS`, and v1 supersession.
- Kept all review, acceptance, possession-v2, feature, cross-authority, product, build, manifest, receipt, serializer, provider, network, and deployment work absent.
- R1-P1-01 is closed: both accidental parent-workspace directory chains remained absent, and every patch header used an exact absolute R2 `allowed_paths` target.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_wyscout_field_registry_authority.py`
  - exit status: 0
  - result: 271 passed in 37.13s
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: 0
  - result: 1 file already formatted
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: 0
  - result: All checks passed
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; no failures
- command: fresh R2 shell-only repository/site pyc and `__pycache__` inventory before Python, repeated after this final return edit and compared with `cmp`
  - exit status: 0
  - result: 1,296-line preflight and terminal inventories are byte-identical; SHA-256 `fa317c8a32e8ec7df9b0b4a76b73829fb5c8533fbc7141b09738c39fd617796f`

## Artifacts/evidence

- decision ID: `w04-wyscout-field-semantic-decisions-v2`
- decision clock: `2026-07-30T20:22:17Z`
- decision physical/canonical SHA-256: `cd4d51c0d7c365b73b0c23997716eb7755797889dca1fc545772263dc9924736`
- registry ID: `w04-wyscout-field-registry-v2`
- registry physical SHA-256: `15023556072f90b1e956277f255dc4a1df0bea78a5dcbb14b4863346ff9b5193`
- registry canonical SHA-256: `93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959`
- focused test physical SHA-256: `12a93afb72019f36e2c775a8e2898029fac8a26466e57114430edcc39e575d2f`
- exact frozen taxonomy: 36 unique `(event_id, subevent_id)` pairs from source SHA-256 `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`
- parent-workspace accidental `reports` and `configs` chains: absent before edits, after every repository materialization, and at completion

## Risks

- The candidates remain control-plane evidence only. They grant no field-v2 acceptance, downstream semantic authority, or product authority until separate independent review, master acceptance, and the complete R21 gate pass.

## Follow-up items

- Run the separately owned field-v2 independent-review packet; only a valid independent `PASS` may proceed to the master acceptance packet.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

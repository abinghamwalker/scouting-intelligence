# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R18`
- objective: Correct only the three master-reproduced R17 regressions while
  preserving every passing R17 standalone, host-normalized, field-roster, and
  downstream authority closure.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R18.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R18.md`

## Summary

- Produced a full standalone R18 replacement that retains the complete R17
  architecture, exact 119-row field roster and `10/11/26/47/18/4/3` counts,
  semantic authority routes, local-only runtime closure, products, gates,
  ownership graph, two-root proof, and two-commit ledger.
- Restored the existing
  `src/scouting/contracts/primitives.py` authority contract exactly:
  `ActorId = StrictUuid`. Every FIELD, POSSESSION, SUPPORTED_FEATURE, and
  IDENTITY `decided_by`, `reviewed_by`, and `accepted_by` field now requires
  strict UUID validation and canonical lowercase RFC 4122 UUID JSON spelling.
  Arbitrary report-local ASCII actor grammars are forbidden. The existing
  accepted-by/decided-by equality, independent-reviewer distinctness, clocks,
  and cross-artifact equality rules remain binding.
- Restored the complete possession predicate row. Every decision, including
  `UNMAPPED`, explicitly carries selectors, `decision`,
  `control_team_source`, `opens_control`, `closes_control`,
  `dead_ball_attachment`, `contested_attachment`, `rationale`, and
  `decided_by`. R18 closes strict JSON types, required/non-null behavior, the
  complete valid combination union for all six decisions, explicit `UNMAPPED`
  values, row/top-level actor equality, canonical taxonomy byte equality, and
  fail-closed rejection cases.
- Restored
  `tests/contracts/test_wyscout_field_registry_authority.py` everywhere and
  removed the unauthorized
  `tests/contracts/test_w04_field_semantic_authority.py` alternate.
- Retained the stable `w04-local-control-bootstrap-v4`,
  `w04-outer-environment-bootstrap-v2`,
  `w04-child-environment-input-v2`, and
  `w04-code-environment-admission-v14` preimages and versions unchanged because
  none of the three report-level semantic corrections changes an executable
  canonical preimage schema.

## Tests run

- command: `uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R18.md'); s=p.read_text(); assert p.stat().st_size > 220000; assert 'tests/contracts/test_wyscout_field_registry_authority.py' in s; assert 'tests/contracts/test_w04_field_semantic_authority.py' not in s"`
  - exit status: `0`
  - result: PASS; the standalone design exceeds 220,000 bytes, contains the
    approved field contract-test path, and contains no unauthorized alternate.
    The initial sandboxed attempt exited `2` because the sandbox could not read
    `/Users/adrian/.cache/uv/sdists-v9/.git`; the exact command was rerun
    unchanged with approved uv-cache access and passed.
- command: `uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; controlling JSON reported `status: PASS`, `failures: []`, and
    all 25 local-only/one-root-uv checks passed.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R18.md`
- R17 read-only integrity remained SHA-256
  `f8dcfead8bef0fa36719e643f5c3d61f116b361603ca2d3d4af7e46848e16195`,
  equal to the master-recorded R17 digest.
- Exact field roster retained: `10 + 11 + 26 + 47 + 18 + 4 + 3 = 119`.
- Stable schema versions retained: `v4/v2/v2/v14`.
- Stable schema cardinalities retained: `16/8/10/25/25/20`.

## Risks

- No implementation, configuration, orchestration, source, test, dependency,
  lockfile, provider, network, data, migration, Git, deployment, or
  self-approval action was performed. Future authority and implementation work
  remains blocked behind the separately owned decision, independent-review,
  master-acceptance, implementation, verification, and gate packets named by
  the design.

## Follow-up items

- `none`

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`

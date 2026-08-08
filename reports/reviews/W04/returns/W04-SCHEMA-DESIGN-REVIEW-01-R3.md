# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-REVIEW-01-R3`
- objective: Independently verify the standalone R4 W04 schema/rebuild design, all
  six R3 review corrections, retention of the five closed findings, and
  ownership-complete readiness for bounded implementation packets.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-independent-review-R3.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R3.md`

## Summary

- Recommendation: **REWORK**.
- No P0 or separate P2 defect was found; four remaining defects are ranked P1.
- The reviewed identity bundle is backdated to source release despite covering later
  identity decision, independent-review, and acceptance evidence.
- W04.3 lacks a complete identity bundle/crosswalk schema, confidence threshold,
  durable review queue, versioned correction workflow, and exact artifact owners.
- The packet graph omits the source-manifest runtime output, identity artifacts,
  data-health surface, transformed dataset card, and master phase-gate evidence.
- The code manifest is non-circular and verifies repository Python before `build_id`,
  but does not bind exact installed third-party executable contents or arbitrary
  behavior-affecting local non-Python resources.
- The semantic authority, exact 18-row manifest, and strict source coverage R3
  defects close. All five retained prior closures survive.

## Tests run

- command: `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-independent-review-R3.md'); assert p.is_file() and p.stat().st_size > 7000"`
  - exit status: 0
  - result: PASS; the independent audit exists and exceeds 7,000 bytes.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 local-only, container-free, dependency, environment, and
    guarded-root checks passed.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-independent-review-R3.md`
- `reports/reviews/W04/wyscout-schema-design-R4.md`
- `reports/reviews/W04/wyscout-schema-design-independent-review-R2.md`
- `src/scouting/contracts/evidence.py`
- `src/scouting/contracts/retrieval.py`
- `docs/architecture/evaluation-contract.md`
- `reports/phase-gates/W04/source-schema-profile.md`
- `docs/dataset-cards/w04-source.md`
- `../scouting-ml-production-blueprint.html`
- `../scouting-ml-agent-implementation-workflow.html`

## Risks

- A source-release clock on a later reviewed identity bundle admits a project ruleset
  before it was knowable.
- Unowned identity queue/correction artifacts cannot satisfy W04.3 or safely evolve
  canonical identities.
- Missing data-health/card/gate owners prevent a truthful W04 phase completion.
- Same-version modified dependencies or unbound local resources can execute under an
  unchanged code manifest/build ID.

## Follow-up items

- Produce a bounded R5 design satisfying the seven acceptance gates in the
  independent audit, then obtain a fresh independent review before implementation.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

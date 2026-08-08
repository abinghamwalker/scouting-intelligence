# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R5`
- objective: Produce the final standalone W04 schema/rebuild design, close all four
  P1 findings returned against R4, retain prior accepted closures, and leave the
  result ready for master and independent review.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R5.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R5.md`

## Summary

- Replaced R4 in full with a standalone R5 design.
- Separated identity source validity from project knowability: identity decision,
  independent review, master acceptance, and correction clocks are truthful;
  acceptance controls `available_at`; cutoff before or equal to acceptance rejects.
- Defined the complete W04.3 lifecycle for competition, team, player, and match:
  strict crosswalk rows, exact 1.0/0.0 resolution states, non-null-only projection
  into existing `IdentityEvidence`, content-addressed queue and bundle, immutable
  correction/supersession chains, deterministic IDs/digests, and distinct owners.
- Closed executable and resource identity over deterministic `uv.lock` wheel
  selection, exact selected artifact hashes, installed distribution/`RECORD` bytes,
  interpreter/libpython and standard-library bytes, repository code, and a closed
  local non-Python allowlist. Every component digest is verified before and included
  in `build_id`; negative tamper tests are assigned.
- Completed ownership for strict source and identity runtime outputs, P2.8 data
  health, the separate P2.9 transformed dataset card and independent card review,
  master verification, `G-W04` gate artifacts, master-only phase registry update,
  and master-only local checkpoint commit/tag.
- Retained the accepted completion-only source seam, exact 18 ordered
  `SourceFileDigest` rows, strict source `DataCoverage`, project-defined field and
  possession authority, period-relative/clock-free temporal proof and truthful
  boundary adapter, neutral Gold grain, minute/per-90 suppression, Gold coverage,
  and result-independent player-match fact.

## Tests run

- command: `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R5.md'); assert p.is_file() and p.stat().st_size > 15000"`
  - exit status: `0`
  - result: PASS; design exists and is 69,415 bytes.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; validator status `PASS`, 25 checks passed, zero failures.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R5.md`
  - size: 69,415 bytes
  - SHA-256:
    `6a22b742e6e84124a4cef3dd0c3b8c2c2e2bef16cfc5759d34cc4905ad5bb37f`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R5.md`
- local-only verification: `status=PASS`, `failures=[]`

## Risks

- This is an implementation design, not implementation or acceptance. Its authority,
  runtime, health, card, verification, gate, registry, and checkpoint artifacts
  remain future work owned by the graph.
- Master and independent reviewers must validate the design; this return does not
  self-approve it.

## Follow-up items

- Master review and independent schema-design review of R5.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

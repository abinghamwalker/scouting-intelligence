# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-REVIEW-01-R2`
- objective: Independently review the measured-evidence-grounded W04 schema/rebuild
  R3 design, verify closure of all nine prior findings, and determine whether it is
  safe to decompose into implementation packets.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-independent-review-R2.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R2.md`

## Summary

- Recommendation: **REWORK**.
- Found no P0 issue, four P1 issues, and two P2 issues.
- Five prior findings close, two are partial, and two remain open.
- P1 stops are: unbound `code_checkpoint`; undefined clock-free strict temporal
  boundary and incomplete dependency mapping; absent semantic authority source for
  field/possession decisions; and ownership-incomplete packet decomposition.
- P2 corrections are: the exact 17-versus-18 strict-manifest contradiction and
  field-inexact source coverage population.
- No implementation packet is safe to dispatch until the R4 correction gates in the
  audit are met.

## Tests run

- command: `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-independent-review-R2.md'); assert p.is_file() and p.stat().st_size > 6000"`
  - exit status: 0
  - result: PASS; the independent audit exists and exceeds 6,000 bytes.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all local-only, container-free, one-root, dependency, and
    configuration boundary checks passed.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-independent-review-R2.md`
- `reports/reviews/W04/wyscout-schema-design-R3.md`
- `reports/phase-gates/W04/source-schema-profile.md`
- `data/source/wyscout/v5/completion-manifest.json`
- `src/scouting/contracts/evidence.py`
- `src/scouting/contracts/retrieval.py`
- `docs/architecture/evaluation-contract.md`

## Risks

- A stale or arbitrary `code_checkpoint` could make a build ID misrepresent the
  implementation that produced it.
- Current strict `TemporalEvidence` requires a generation clock, contradicting the
  design's clock-free semantic rows unless an explicit boundary contract/adapter is
  defined.
- Possession mappings would require guessed semantics without a named reviewed
  authority.
- Shared integration, layer manifests, and checkpoint/rebuild orchestration do not
  yet have exact sole-writer packets.

## Follow-up items

- Produce a bounded R4 design satisfying the seven acceptance gates in the
  independent audit, then obtain a fresh independent review before implementation.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

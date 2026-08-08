# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01`
- objective: Correct the complete W04 implementation design for the proven archive
  directory, generic/Wyscout clock boundaries, and deduplicated Gold schema while
  retaining the valid R1 design and gates.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R2.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R2.md`

## Summary

- Replaced R1 with a complete standalone R2 design.
- Defined each archive as exactly five admitted plus two exact known-excluded entries;
  known exclusions pass directory classification but their streams and payload bytes
  are never opened, extracted, admitted, parsed, hashed independently, or used.
- Required failure for missing, duplicate, unsafe, or any eighth/undeclared entry.
- Preserved the generic `SourceSnapshotManifest` clocks as independently ordered
  truthful facts and added only a Wyscout adapter rule requiring actual acquisition at
  or after the frozen release.
- Explicitly requested no W03 fixture, digest, schema, consumer, or migration change.
- Deduplicated the Gold identity fields and defined one exact logical uniqueness key.
- Retained exact Bronze, identity, Silver, possession, Gold, quality, temporal,
  deterministic-rebuild, evidence, and serial/path-disjoint implementation rules.
- Recommendation to master: ready for independent R2 review, not self-approved.

## Tests run

- command: `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R2.md'); assert p.is_file() and p.stat().st_size > 5000"`
  - exit status: `0`
  - result: design exists and is `37,209` bytes.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all 21 local-only and one-root project checks passed, including
    zero configured remotes, the pre-push guard, and no hosted CI or deployment.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R2.md`
- `reports/phase-gates/W04/archive-directory-preflight.md`
- `reports/reviews/W04/returns/W04-CONTRACT-TEMPORAL-01-R1.md`

## Risks

- Source truth still depends on acquisition code applying the exact configured
  directory and temporal authorities; this design does not itself ingest data.
- Excluded member safety requires the acquisition implementation to inspect central
  directory metadata without opening excluded member streams.

## Follow-up items

- Master to reproduce checks, inspect both allowed-path files, and send R2 to
  independent review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no code, configuration, orchestration, test, migration, data, or run change:
  confirmed
- no provider payload access, network access, external service, or deployment:
  confirmed
- no delegation or self-approval: confirmed

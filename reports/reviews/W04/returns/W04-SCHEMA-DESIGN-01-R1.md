# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01`
- objective: Produce an implementation-ready, fail-closed canonical schema and rebuild
  design for the frozen Wyscout figshare v5 source without implementation or payload
  inspection.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R1.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R1.md`

## Summary

- Defined the exact raw-object, safe archive-member, record-index, quarantine, and
  Bronze completion-manifest boundaries, including record-level lineage fields and
  unknown-field/member failure policy.
- Defined a deterministic UUIDv5 hierarchy and explicit resolved, review, missing,
  conflict, and supersession identity rules. Display names and unversioned player-master
  attributes never create historical identity/team joins.
- Specified exact Silver match, team, player, lineup-stint, action, possession, and
  action-to-possession schemas, including types, nullability, lineage, bounded time and
  coordinate representation, and explicit uncertainty/failure states.
- Specified a deterministic possession state machine whose semantics come only from a
  reviewed event/subevent/tag mapping. Unmapped or contested boundaries are uncertain
  or failed and are never guessed into Gold.
- Specified the W04 Gold player-window boundary and base coverage features. Because all
  source records first become knowable at collection release, no cutoff at or before
  `2020-01-28T14:24:27Z` is eligible, and no 2017/18 match-era availability claim is
  made.
- Defined exact source, identity, reconciliation, missingness, range, temporal, rights,
  and two-empty-root deterministic-rebuild gates.
- Proposed ten serial/path-disjoint master packets with exact implementation and test
  paths.
- Identified one high-risk serial precondition: `SourceSnapshotManifest` currently
  rejects a truthful publication time earlier than local acquisition. The report fixes
  the intended invariant as `available_at <= acquired_at`, lists six required
  regressions, and calls out the necessary explicit W03 consumer migration.

## Tests run

- command:
  `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R1.md'); assert p.is_file() and p.stat().st_size > 5000"`
  - exit status: `0`
  - result: design exists and is above the 5,000-byte minimum
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 21 local-only/one-root checks passed, zero failures, zero Git remotes

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R1.md`
- Contract-correction invariant:
  `available_at = source publication/knowledge instant`,
  `acquired_at = actual completed local acquisition instant`,
  `available_at <= acquired_at`
- Frozen source availability boundary: `2020-01-28T14:24:27Z`

## Risks

- High risk: the serial evidence-contract correction and explicit W03 consumer
  migration must pass second review before source acquisition. Fabricating acquisition
  time is forbidden.
- The strict A3 unknown-archive-member policy may stop acquisition if the configured
  archives contain undeclared members. No payload was inspected, so this remains an
  intentional fail-closed gate, not an inferred exception.
- Provider substitution, event/tag, and possession semantics outside the frozen
  authority remain unavailable. The design quarantines or suppresses affected products
  until a reviewed mapping exists.

## Follow-up items

- Master to issue and second-review the serial evidence-contract correction before
  acquisition.
- Master to convert the proposed implementation map into exact packets, preserving the
  serial contract/identity/Gold boundaries and the one allowed 6A/6B path-disjoint
  parallel pair.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no provider payload download or inspection: confirmed
- no code, configuration, test, orchestration, data, run, or migration edits: confirmed
- no delegation: confirmed
- no edits outside `allowed_paths`: confirmed

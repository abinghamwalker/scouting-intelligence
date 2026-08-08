# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R3`
- objective: Produce one standalone implementable W04 schema and deterministic rebuild design,
  grounded in the accepted adapter R3 and measured profile R2, that explicitly closes all nine
  returned findings without guessing source semantics.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R3.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R3.md`

## Summary

- Replaced fabricated event UTC with exact `decimal128(22,18)` period-relative evidence,
  explicit source scale, deterministic period/event ordering, null occurrence UTC, and a
  conservative snapshot-availability strict-cutoff proof. Partial-match/action-instant cutoffs
  are unsupported.
- Froze the accepted adapter seam: completion first, then only the exact seven `object_path` and
  ten `member_path` values. The two ZIP payloads and four excluded member payloads remain
  unopened downstream.
- Defined a non-circular UUIDv5 completion-to-`SourceSnapshotManifest` bridge with explicit
  master-supplied tenant context, deterministic semantic trace, strict classification mapping,
  18 ordered file evidences, six exact admission-coverage dimensions, and one canonical
  downstream source-manifest artifact.
- Removed run clocks from semantic products, defined stable `build_id` inputs, fixed canonical
  semantic digests and exact Parquet writer options, required semantic and physical two-root
  equality, and separated truthful random/run-clock operational receipts.
- Added serial master-owned field-registry and possession-taxonomy authority packets with exact
  owned paths, schemas, version IDs, digest rules, unknown behavior, and fabricated challenge
  cases. Possession implementation cannot precede those accepted authorities.
- Added deterministic `w04-neutral-role-context-v1` identity to the Gold logical key and froze
  non-mutating W05 expansion behavior.
- Distinguished provider nominal, period-relative, elapsed, stoppage, and terminal meanings;
  froze substitution intervals and right-censoring; and suppressed every W04 elapsed-minute
  and per-90 product.
- Froze six coverage numerators/denominators, mandatory/optional zero-denominator behavior,
  minimum overall aggregation, missing-dimension rules, and the ordered
  suppressed/research-only/data-ready decision table.
- Added blueprint-required `silver_player_match_fact`: exact player × match grain, match-bound
  team/context, result-independent facts, nominal/elapsed minute states, six coverage structs,
  strict temporal/lineage fields, and exact action/lineup/identity reconciliation.
- Proposed twelve implementation packets. Shared authority/contracts and all writers are serial;
  only three path-disjoint Silver packets may run concurrently. No migration is proposed, and
  any future migration requires a separate master-owned serial second-reviewed packet.

## Tests run

- command:
  `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R3.md'); assert p.is_file() and p.stat().st_size > 8000"`
  - exit status: 0
  - result: design exists and is 45,508 bytes
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: structured status `PASS`; all 25 checks passed with no failures

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R3.md`
  - SHA-256: `119b2d9f514fabb515ce8ff389396d3101fb8ea8f697164530cc44a55477c391`
  - size: 45,508 bytes
  - lines: 898
- Accepted completion binding:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Accepted measured profile binding:
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`
- Sections 2–15 contain exact source paths, bridge mapping, clock/cutoff contract,
  authority schemas, product schemas, minute rules, possession behavior, coverage equations,
  role context, build/receipt identity, reconciliation gates, implementation ownership, and
  finding-by-finding closure.

## Risks

- Exact event occurrence UTC, period starts, match terminals, elapsed player minutes, and per-90
  denominators are absent from the accepted source evidence. The design suppresses those claims
  rather than inventing them.
- Possession behavior remains unavailable until the proposed master-owned taxonomy authority is
  accepted. Labels or football conventions cannot substitute for that authority.
- The strict manifest requires a real immutable tenant context from the master-owned admission
  packet; the design deliberately provides no default tenant UUID.
- Three coordinate anomalies and unmatched bench/substitution references remain explicit
  incomplete evidence and can keep affected products research-only or suppressed.
- This document is an implementation proposal for master and independent review, not approval
  of the task or W04 phase.

## Follow-up items

- Master and independent reviewer must accept or return this R3 design before dispatching the
  serial authority and implementation packets in Section 14.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

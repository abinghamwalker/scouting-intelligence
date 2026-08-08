# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R4`
- objective: Produce a standalone R4 W04 schema/rebuild design that retains the five
  accepted R3 closures and implementably corrects all four P1 and two P2 defects
  returned against R3 without changing architecture, rights, dependencies, migrations,
  or the local-only boundary.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R4.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R4.md`

## Summary

- Replaced arbitrary `code_checkpoint` text with a content-addressed
  `w04_post_integration_code_manifest`: exact non-circular schema, full W04 package
  seed plus repository-local AST import closure, lock inputs, selected distribution
  verification, exact byte/size/executable handling, symlink/generated/dynamic-import
  rejection, dirty and untracked byte treatment, serial post-integration freeze,
  independent reproduction, and mandatory runtime equality before `build_id`.
- Defined the complete strict clock-free
  `W04SemanticTemporalProof` with fields, types, canonical dependency ordering/hashing,
  feature-schema hashing, strict-before-cutoff rules, and validators. Defined a
  truthful one-clock boundary adapter that adds `generated_at_ts` only while building
  the unchanged existing `TemporalEvidence`/`RetrievalResult`, outside semantic
  Bronze/Silver/Gold bytes.
- Mapped the strict source manifest to existing `source_manifest`, the deterministic
  identity bundle to `identity_evidence`, and the accepted field registry and project
  possession taxonomy to existing `feature_schema`. Specified deterministic UUIDv5
  rules and truthful observed/available clocks. Kept match and action evidence in an
  exact `W04SourceRowRef` lineage contract instead of inventing dependency kinds.
- Made semantic authority explicit and normative: exact completion/profile/event-map/
  tag-map paths and digests feed a master-authored decision, separately owned
  independent review, and final master acceptance for field and possession decisions.
  Acceptance digests and clocks enter lineage/build identity. Unknowns remain
  `UNMAPPED`; runtime label matching and provider-native possession claims are
  forbidden.
- Defined exactly 18 ordered strict `SourceFileDigest` rows—completion, seven objects,
  and ten members—with exact path, byte, digest, and row-count values.
- Populated strict source `CoverageDimension` and `DataCoverage` with their literal
  contract field names, strict float/count types, exact order, six-element dimension
  tuple, empty missing tuple, and JSON array serialization, explicitly separated from
  richer Gold coverage.
- Replaced the R3 decomposition with a 23-step ownership-complete graph. Field and
  possession decisions/reviews/acceptances, shared contracts/exports, the strict
  source manifest, Bronze/Silver/Gold layer manifests, code admission, empty-root
  rebuild entry point, and final independent review each have a sole named owner and
  exact scope. Only the three path-disjoint Silver producers may run in parallel.
- Retained the five accepted closures: exact completion-declared source seam,
  versioned neutral Gold role context, elapsed-minute/per-90 suppression, exact Gold
  coverage/applicability equations, and result-independent Silver
  `player_match_fact`.
- The design is explicitly for master and independent review and does not self-approve.

## Tests run

- command:
  `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R4.md'); assert p.is_file() and p.stat().st_size > 12000"`
  - exit status: `0`
  - result: PASS; the design is 61,110 bytes.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; status `PASS`, 25 checks, no failures.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R4.md`
  - lines: `1,112`
  - bytes: `61,110`
  - SHA-256:
    `53d5a6c7226a16ea9e98601ad598541fed59ac93b4c3b375e3c1c6010237ace4`
- Binding completion SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Binding profile SHA-256:
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`

## Risks

- The design intentionally leaves authority artifact contents and availability clocks
  to the future accountable master/independent-review route. Until those immutable
  artifacts are accepted, possession remains unavailable and unknown semantics remain
  `UNMAPPED`.
- The implementation graph and code-manifest verifier still require master and
  independent implementation review; this design provides no self-approval.
- Exact elapsed player minutes, period terminals, per-90 denominators, action UTC, and
  provider-native possession remain unsupported by the source and are explicitly
  suppressed rather than estimated.

## Follow-up items

- Master independently read and review the complete R4 design, reproduce both packet
  checks, and dispatch an independent schema-design review only if the six R3 defects
  and five retained closures are confirmed.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither
  `pyproject.toml` nor `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; only the two files listed above were
  created or edited.

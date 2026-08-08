# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01` revision `R6`
- objective: Produce the final standalone W04 schema/rebuild design that closes the
  seven P1 defects returned against R5 while retaining every prior accepted closure
  and approved boundary.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R6.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R6.md`

## Summary

- Produced a 59,353-byte standalone R6 design retaining the exact source seam,
  18-row manifest, strict source coverage, rights, field/possession authorities,
  identity clocks, period-relative temporal proof, neutral Gold grain,
  minutes/per-90 suppression, coverage equations, result-independent player-match
  fact, health/card evidence, independent reviews, and `G-W04`.
- Moved every identity bundle, review queue, and normalized correction family under
  exact `data/working/wyscout/v5/identity` subtrees, with guarded-reader,
  serializer, manifest-reference, ownership, and test rules.
- Replaced the unavailable wheel-ZIP premise with an offline uv
  `wheels-v5`-symlink-to-`archive-v0` extracted-tree algorithm. It separates
  lock-declared archive metadata from locally verified extracted/installed bytes and
  explicitly records that absent original wheel ZIP hashes/sizes are not verified.
  Installed `RECORD`, `INSTALLER=b"uv"`, empty `REQUESTED`, rewritten `RECORD`, and
  denied/enumerated generated CPython bytecode rules are exact.
- Added supported-feature master decision, independent review, and master acceptance
  before Gold; added the accepted registry as the fifth exact temporal dependency
  and updated clocks, hashes, resources, build identity, ordering, watermark, owners,
  and cutoff-negative tests.
- Added a W04-only classification-method representation for all resolved,
  review-required, rejected, reviewed resolution/rejection, direct supersession, and
  effective superseded states while leaving the existing `IdentityEvidence`
  contract/enum unchanged and projecting only valid current resolved rows.
- Defined discriminated `QUEUE_DISPOSITION` and
  `DIRECT_CURRENT_RESOLVED_SUPERSESSION` correction routes. The direct route creates
  no queue item, transition, snapshot, or history and retains the prior queue digest.
- Enumerated deterministic, non-overlapping Bronze raw/quarantine, every Silver
  product, Gold partition, staging, receipt, and manifest formula; assigned sole
  serializers; constrained the rebuild owner to invocation/receipt; and defined
  atomic completion, exact manifest references, two-root, and no-overlap tests.
- Reconciled acceptance with the controlling workflow: full gate, acceptance
  integration commit and accepted tag, then registry/checkpoint and clean-tree
  predicate evidence in one separate local ledger commit without self-referential
  SHA fields. Retained exact accepted message/tag
  `phase(w04): accept governed data spine` /
  `checkpoint/w04-accepted`.

## Tests run

- command:
  `uv run python -c "from pathlib import Path;
  p=Path('reports/reviews/W04/wyscout-schema-design-R6.md');
  assert p.is_file() and p.stat().st_size > 18000"`
  - exit status: `0`
  - result: PASS; R6 exists and measured 59,353 bytes before this return was written.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; validator reported 25 checks passed, zero failures.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R6.md`
- Design-time local cache evidence is recorded truthfully in R6 as uv
  `wheels-v5/pypi/<name>/<version-tags>` symlinks to `archive-v0/<opaque-key>`
  extracted directories, not wheel archives.
- Installed-distribution evidence observed for the design includes strict installed
  `RECORD` rows for `INSTALLER` (2-byte `uv`) and `REQUESTED` (0 bytes), plus
  generated in-place bytecode that the R6 execution boundary enumerates and denies.

## Risks

- R6 remains a design candidate and is not self-approved. A separate independent
  read-only review and master reproduction are required before implementation
  dispatch.
- Opaque uv cache target keys and host paths are operational admission-receipt
  evidence only; stable extracted-tree/installed byte digests, not those host
  details, enter build identity.
- No implementation or runtime artifact has been created by this design packet.

## Follow-up items

- Master to inspect R6, reproduce the two packet checks, and dispatch an independent
  R6 review. Do not dispatch implementation or `G-W04` until that review and master
  acceptance pass.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither
  `pyproject.toml` nor `uv.lock` was edited, and no dependency/provider/network
  acquisition occurred.
- no edits outside `allowed_paths`: confirmed; only the two exact report paths
  listed above were created.

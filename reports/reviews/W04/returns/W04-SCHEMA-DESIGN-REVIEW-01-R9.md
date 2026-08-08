# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-REVIEW-01-R9`
- objective: Independently challenge the complete standalone R15 W04 schema and
  deterministic rebuild design, reproduce every material current-environment
  claim, and accept only when all P0-P2 concerns are closed.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-independent-review-R9.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R9.md`

## Summary

- Decision: **REWORK**.
- Found one P1 implementation-blocking contradiction in the exact closed
  environment. Normal resolution of the repeatedly mandated literal
  `uv run --locked --no-sync ...` command through R15's exact `PATH` makes uv set
  `UV=/opt/homebrew/bin/uv`; R15 instead requires the physical
  `/opt/homebrew/Cellar/uv/0.9.21/bin/uv` value.
- Reproduced the mismatch from the complete 29-name closed outer map and a second
  minimal closed control, even when the physical path was supplied as the input
  `UV` value. It changes the outer and both child expected maps and therefore
  blocks their base-digest, tuple/envelope, and first-instruction equality checks.
- Proved a bounded correction exists: a separately forced physical OS executable
  target with visible `argv[0]="uv"` yields the desired physical `UV` value. R15
  does not currently specify or admit this split. R16 must bind that exec target,
  or admit the logical symlink value and exact resolution, across all three roles.
- Independently reproduced the passing R15 corrections: exact unique 25/25
  projection/invocation keys, 24 common values, projection-only `schema_version`,
  invocation-only `build_id`, one projection hash, deterministic child
  reconstruction, and no completed-instance cycle or operational preimage value.
- Reproduced the accepted five-field `EvidenceDependency` JSON contract, forbidden
  aliases, exact enum order, five-row cardinality, strict cutoff equality failures,
  and lineage/watermark design.
- Reproduced 16/8/10/25 envelope cardinalities, no-site behavior, descriptor
  preservation, `L == I`, three denied `.pth` classes, editable evidence, the
  35-row/21-owner executable census with 33/1/1 classes, three interpreter
  aliases, encoding sources, 1,075-site and 58/19-repository pyc observations,
  four optional orphan predicates, 18 source rows, and 17 resources.
- Read back and challenged the retained source/rights, identity, football-product,
  six-plus-six coverage, strict temporal, unknown-quarantine, path, publication,
  writer, health/card/gate, two-root, and two-local-commit controls. No other P0-P2
  defect was found.
- No candidate correction or implementation was performed.

## Tests run

- command: mechanically parse R15 projection and invocation key lists
  - exit status: `0`
  - result: PASS; 25/25 unique and sorted, 24 common,
    projection-only `schema_version`, invocation-only `build_id`.
- command: mechanically parse R15 child schema tables
  - exit status: `0`
  - result: PASS; exact unique `16/8/10/25` cardinalities.
- command: `uv run --locked --no-sync python -B -c '<EvidenceDependency JSON probe>'`
  - exit status: `0`
  - result: PASS; exact five fields and canonical JSON; `dependency_kind`,
    `manifest_id`, and `manifest_sha256` rejected as extras.
- command: `uv run --locked --no-sync python -B -c '<strict temporal probe>'`
  - exit status: `0`
  - result: PASS; observed, available, and watermark equality with cutoff each
    rejected.
- command: complete and minimal closed `env -i` uv transformation probes
  - exit status: `0`
  - result: **P1 reproduced**; count/depth/PATH pass, but actual
    `UV=/opt/homebrew/bin/uv` contradicts the required physical spelling.
- command: separate physical-exec-target control with visible `argv[0]="uv"`
  - exit status: `0`
  - result: PASS as correction evidence; uv then sets physical Cellar `UV`.
- command: inherited descriptor through
  `uv run --locked --no-sync python -S -B`
  - exit status: `0`
  - result: PASS for descriptor 9; regular file, offset zero, inheritable,
    `FD_CLOEXEC` clear.
- command: locked all-groups versus installed normalized set comparison
  - exit status: `0`
  - result: PASS; 82 selected/installed members including editable root, empty
    normalized `comm -3`; uv reported 83 resolved graph packages.
- command: read-only `.pth`, editable, interpreter, uv, encoding-source,
  executable RECORD/entry-point, and pyc inspections
  - exit status: `0`
  - result: PASS; exact three `.pth`, 35 rows/21 owners, 33 E/1 P/1 W, three
    aliases, 1,075 site pycs, and 58 repository pycs in 19 caches with three
    exact source-absent repository orphans.
- command: source/profile SHA-256 plus R15 source/resource table parsing
  - exit status: `0`
  - result: PASS; completion/profile digests match, 18 unique source rows and 17
    unique resources.
- command: `uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-independent-review-R9.md'); assert p.is_file() and p.stat().st_size > 15000"`
  - exit status: `0`
  - result: PASS; the independent review exists and exceeds 15,000 bytes.
- command: `uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; 25 checks, zero failures, zero configured remotes, active local
    push guard, one root uv project, Python 3.12.12, no hosted CI/deployment,
    container definition, or external-service dependency.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-independent-review-R9.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R9.md`
- `reports/reviews/W04/wyscout-schema-design-R15.md`
- `reports/verification/W04/wyscout-schema-design-R15-master-verification.md`
- `src/scouting/contracts/evidence.py`
- `reports/phase-gates/W04/source-schema-profile.md`
- current local uv, venv metadata, installed RECORD/entry-point, executable,
  interpreter, encoding-source, and bytecode evidence read in place

## Risks

- P1: the documented exact outer and child environments cannot pass under normal
  resolution of the visible `uv` token because the actual uv-set path is logical
  while the design requires physical. Silently choosing a separate physical exec
  target would improvise an unstated process authority.
- The bounded correction does not require any provider, rights, dependency,
  network, cloud, deployment, architecture, storage-root, or local-only change.

## Follow-up items

- Dispatch standalone R16 to freeze the outer and child uv exec-target/value
  contract consistently, then repeat master and independent review before W04
  implementation.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

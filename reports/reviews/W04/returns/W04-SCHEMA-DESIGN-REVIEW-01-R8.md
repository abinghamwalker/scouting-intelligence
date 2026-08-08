# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-REVIEW-01-R8`
- objective: Independently challenge the complete standalone R11 W04 schema and
  deterministic rebuild design, reproduce its material environment claims, and
  accept only if every P0-P2 concern is closed.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-independent-review-R8.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R8.md`

## Summary

- Decision: **REWORK**.
- Reproduced a P1 current-environment contradiction: the repository contains 58
  pycs in 19 cache directories, not R11's 56/17. The true split is 38 normal-name
  plus 20 pytest; only 35 normal files map to present `.py` sources. The three
  source-absent normal-name files are the two omitted migration pycs and the one
  already-enumerated PostgreSQL orphan. R11 has no allowed class for the two
  migration files and forbids cleanup.
- Found a second P1 design gap: the external launcher owns all pre-interpreter,
  result-channel, code-manifest publication, build-ID handoff, and child-launch
  operations but has no exact implementation path/bytes, authority, channel
  grammar, sole owner, or stable manifest row. The two named inner Python scripts
  cannot perform those operations before their interpreters exist.
- Reproduced the passing locked/no-sync no-site behavior, exact all-groups
  installed equality, Packaging bootstrap, three `.pth` classes, editable
  metadata, 35-row executable census with 33/1/1 classes and 21 owners, three
  interpreter aliases, 1,075-site-pyc inventory and exact optional-six/bootstrap
  hashes, source/temporal/key/coverage/path contracts, 17 resources, sole writers,
  health/card/gate structure, two-root stable split, and two-local-commit ledger.
- Proposed bounded R12 corrections only; no candidate repair was performed.

## Tests run

- command: `uv run --locked --no-sync python -S -B -c '<no-site environment probe>'`
  - exit status: `0`
  - result: PASS; `python3`, no site-packages/editable source path, `_virtualenv`
    and Coverage absent, bytecode writing disabled.
- command: `uv tree --locked --all-groups --depth 100`
  - exit status: `0`
  - result: PASS; 83 packages including the editable root.
- command: `uv pip list --python .venv/bin/python --format json`
  - exit status: `0`
  - result: PASS; 83 installed distributions including the editable root.
- command: exact normalized name/version `comm -3` between locked all-groups tree
  and installed list
  - exit status: `0`
  - result: PASS; empty difference, 82 third parties plus editable root.
- command: read-only `.pth`, editable metadata, RECORD executable, interpreter
  alias, pyc count, magic, size, and SHA-256 inspections
  - exit status: `0`
  - result: PASS for all retained claims except the documented repository-pyc
    contradiction.
- command: `uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-independent-review-R8.md'); assert p.is_file() and p.stat().st_size > 10000"`
  - exit status: `0`
  - result: PASS; the independent review exists and exceeds 10,000 bytes.
- command: `uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; 25 checks, zero failures, zero configured remotes, active local
    push guard, one root uv project, Python 3.12.12, no hosted CI/deployment,
    container definition, or external-service dependency.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-independent-review-R8.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R8.md`
- `reports/reviews/W04/wyscout-schema-design-R11.md`
- `reports/phase-gates/W04/source-schema-profile.md`
- `data/source/wyscout/v5/completion-manifest.json`
- current `.venv` installed metadata, RECORD, executable, interpreter alias, and
  bytecode evidence read in place
- current whole-repository bytecode inventory read in place

## Risks

- P1: the current environment is not admissible under R11 because two
  source-absent migration pycs have no exhaustive class and cleanup is forbidden.
- P1: launcher behavior would have to be improvised outside admitted
  code/ownership, weakening the claimed exact process, manifest, and mutation
  boundaries.
- No provider, rights, dependency, network, cloud, deployment, storage-root,
  architecture, or local-only change is required for bounded rework.

## Follow-up items

- Dispatch a bounded standalone R12 design correction for the two P1 findings,
  then repeat master and independent review before implementation.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

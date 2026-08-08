# W04 Wyscout schema design R6 — master verification

## Decision

`REWORK`. The master read the full 1,153-line R6 design and 98-line return, read the
complete independent R5 review and return, reran both packet suites, and reproduced
the two new P1 defects. All seven P1 defects returned against R5 are materially
closed and protected from regression.

## Artifact integrity

- R6 design: `59,353` bytes; SHA-256
  `332000a700a5c435cfcfe041205b7e87dd7788400883eca95e97e4221d3cfde0`.
- R6 return: SHA-256
  `8dc7b6d769a0be29028ec8f2d2ccc05ff3c87782d9f7fb7f6c440aa150140200`.
- Independent R5 review: `24,120` bytes; SHA-256
  `c285b7e88079f203321f5dde6baeb9f111c48a9d8a545d7484bf6e4ad21b1631`.
- Independent return: SHA-256
  `139a98b68d874acc02bebeb097b16c56d99e5ba2c931a96dd8d5b03e5caeec66`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.

## Reproduced findings

1. R6 selects external distribution owners only from direct repository AST imports,
   but admitted packages import separately owned runtime distributions. The current
   environment maps `pydantic` and `pydantic_core` to distinct owners, and `polars`
   and `_polars_runtime_32` to `polars` and `polars-runtime-32`. R6 then rejects an
   import from an unadmitted owner, so the positive rebuild is not closed before
   execution.
2. R6 restricts `kind` to seven known tokens while requiring unknown record kinds
   to write `quarantine/rejected-record/record_kind=<kind>/...`. Missing, unsafe, or
   unknown raw kinds therefore have no legal deterministic path.

## Checks

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- R6 size assertion: PASS; `59,353` bytes.
- Independent-review size assertion: PASS; `24,120` bytes.
- Both `uv run python scripts/verify_local_only.py` reproductions: PASS; 25 checks.
- Runtime distribution-owner reproduction: PASS; separate owners observed for both
  Pydantic and Polars edges.
- Orchestration YAML parsing and registry task-ID uniqueness: PASS.
- `git diff --check`: PASS.
- `git remote`: PASS; no output.

## Rework boundary

`W04-SCHEMA-DESIGN-01-R7` owns only a replacement standalone design and return. It
must conservatively close the pre-execution distribution set and define safe
unknown-kind quarantine paths. It may not change dependencies, code, configuration,
data, Git state, source rights, provider state, or local-only architecture. A fresh
independent review remains mandatory before implementation.

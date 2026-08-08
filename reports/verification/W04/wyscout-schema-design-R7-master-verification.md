# W04 Wyscout schema design R7 — master verification

## Decision

`REWORK`. The master read all 1,019 R7 design lines and the full return, read the
complete independent R6 review and return, reran the packet checks, and reproduced
all eight P1 and two P2 findings. No R7 implementation packet is authorised.

## Integrity

- R7 design: `52,872` bytes; SHA-256
  `38d6cddb96562681149563d9b210622e2098bb660eef5981604d584847f46590`.
- R7 return: SHA-256
  `c7fc0ff775cc6d08da682ce9c8109954ab28da1a0f13717290e0d6d7709b0a58`.
- Independent R6 review: `21,790` bytes; SHA-256
  `d90fe1b1292d7bb4260f15130a6381b323ee73381c92d9889d88a46d7ff470c8`.
- Independent return: SHA-256
  `0030b0c0ec1eff54e06f8780c1663f8f7c1b77bdbf2b69a40fa6599c150913b7`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.

## Reproduced evidence

- Existing temporal contracts and R6 require strict-before; R7 explicitly lets
  equality pass.
- R7 changes the accepted Gold key, player-match key, known Bronze path and Gold
  coverage dimensions.
- The accepted source profile has no top-level `$.kind`; record family comes from
  completion path/file group.
- The all-groups installed state has 35 `../../../bin/*` RECORD rows across 21
  owners. Pytest adds `py.test` and `pytest` plus `INSTALLER`/`REQUESTED`, and its
  wrappers contain the absolute venv interpreter shebang.
- Current selected site roots contain 130 `__pycache__` directories and 1,075 pyc
  files, so R7's fatal-absence rule cannot pass after the approved uv workflow.
- R7 places the uv executable's absolute path in semantic environment identity and
  replaces R6's exact 17 resources with non-reproducible categories.

## Checks

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- R7 size assertion: PASS; `52,872` bytes.
- Independent-review size assertion: PASS; `21,790` bytes.
- Local-only verification: PASS; 25 checks, zero failures.
- Console-script inventory: PASS as evidence; 35 rows/21 owners.
- Bytecode inventory: PASS as evidence; 130 directories/1,075 files.
- Orchestration YAML parsing/registry uniqueness: PASS.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

## Rework boundary

R8 is report-only. It must retain the complete distribution closure and safe unknown
partition while restoring exact R6 temporal, product, coverage, path and resource
contracts and making existing uv-generated scripts/bytecode truthfully admissible
but unreadable. No architecture, dependency, environment cleanup, source, provider,
network, Git or local-only change is permitted.

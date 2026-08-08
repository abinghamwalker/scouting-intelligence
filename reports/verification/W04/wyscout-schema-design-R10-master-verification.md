# W04 Wyscout schema design R10 — master verification

## Decision

`REWORK`. The master read all 2,004 R10 design lines and the complete final return,
began review with a fresh `uv sync --locked --all-groups`, and reproduced the
packet and measured-environment evidence. R10 closes R9's stage-0/build-ID cycle,
repository orphan, source-complete bytecode authority, and three-alias findings.
One P1 command-boundary contradiction and one P2 lineage label remain; independent
review and implementation stay blocked.

## Integrity

- R10 design: `105,527` bytes.
- R10 design SHA-256:
  `6a29effd281e9860ff93df0ece239392f061b48ada1c1503692366be0d99ebf0`.
- R10 final return: `4,200` bytes; SHA-256
  `03eff69cbac933595058b806a049d7b3dfe9b31c019b05ed01c7259e84d6c62e`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Final return records both packet checks PASS after the master removed its own
  invalid `../reports/**` packet literal.

## Retained closures

R10 now has a constructive pre-build admission prefix, immutable code-manifest
boundary, post-build-ID rebuild prefix, two distinct `-S -B` processes, a stable
source map over every admitted `.py`, optional exact site-six and repository-
PostgreSQL inert orphans, and the exact three `python`/`python3`/`python3.12`
aliases. Its current site/repository census and two-root stable/operational split
match master evidence. All earlier source, rights, strict temporal, identity, key,
coverage, path, executable, resource, gate, ownership, and ledger rules remain.

## Findings

### P1 — plain `uv run` does not enforce the stated read-only boundary

R10 states that admission does not sync, resolve, install, or mutate the
environment, but both process commands are written as plain:

```text
uv run python -S -B ...
```

Plain `uv run` may reconcile the project environment before launching Python. The
master proved the constructive existing-environment command is:

```text
uv run --locked --no-sync python -S -B ...
```

It reports the exact `.venv/bin/python3` launch alias, has no site-packages path,
and does not import `_virtualenv`. R11 must use this exact uv flag contract for both
processes, reject omitted/reordered/contradictory mutation-enabling modes, and still
perform its own complete lock/install equality verification inside stage 0.

The design should name the exact repository entry points
`scripts/admit_wyscout_v5_runtime.py` and `scripts/rebuild_wyscout_v5.py` so the
externally hashed bytes and process roles are constructive. This names future
implementation paths only; R11 remains report-only.

### P2 — stale revision lineage

R10 ends by saying “R9 closes the returned R8 master findings.” It must state that
R10 closes the returned R9 master findings. The stale label makes the standalone
artifact lineage false even though the retained content is present.

## Checks

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- R10 size assertion: PASS; `105,527` bytes.
- Local-only verification: PASS; 25 checks, zero failures.
- Exact locked/no-sync/no-site probe: PASS; `.venv/bin/python3`, `_virtualenv`
  absent, no site-packages path.
- R10 source/temporal/key/coverage/resource/ledger readback: PASS.
- R10 executable/alias/`.pth`/pyc/prefix readback: PASS except the command flag
  contradiction above.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No dependency, lock, architecture, provider, network, storage, environment cleanup,
Git history, or local-only change is authorised.

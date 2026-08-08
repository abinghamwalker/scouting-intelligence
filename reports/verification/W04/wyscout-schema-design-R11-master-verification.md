# W04 Wyscout schema design R11 — master verification

## Decision

`ACCEPT` as the candidate for independent review. The master read all 2,058 R11
design lines, the complete 53-line return, and the full R10-to-R11 diff. R11 closes
the remaining process-launch and lineage findings without changing architecture,
dependencies, source rights, provider access, storage roots, or the local-only
boundary. W04 implementation remains blocked until independent review passes and
the master reproduces that result.

## Integrity and scope

- R11 design: `108,939` bytes; SHA-256
  `e5f62fa74ecfa701e753318d085f34e0d8fb6dc23147983aed0c711a3f713a8c`.
- R11 return: `3,192` bytes; SHA-256
  `7f285a16a1d13dcbd10ead767fc4f9116adb507ec5d2fa752e8a1e6752affd38`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership was limited to the R11 design and return.
- Neither future implementation entry point exists.
- No stray parent `reports` tree exists.

## R10 closure

Both Python process roles now bind exact ordered commands:

```text
uv run --locked --no-sync python -S -B scripts/admit_wyscout_v5_runtime.py
uv run --locked --no-sync python -S -B scripts/rebuild_wyscout_v5.py
```

The design rejects missing, reordered, duplicated, or extra launch tokens, plain
`uv run`, environment reconciliation, alternate interpreters or entry points,
generated scripts, and site startup. It retains an independent stage-0 check of
`pyproject.toml`, `uv.lock`, the complete selected lock closure `L`, installed set
`I`, and exact `L == I`. The stable launch contract binds argv, role, uv
version/physical digest, and repository entry-point paths/bytes while keeping
root-bearing launch spelling operational. The final lineage now truthfully says
R11 closes the returned R10 findings.

## Retained standalone contract

Master readback confirmed that R11 retains the strict source envelope and complete
18-row source evidence; strict-before temporal cutoff; exact player-match and Gold
keys; distinct six-dimensional source and Gold coverage; fixed Bronze, Silver,
Gold, quarantine, staging, manifest, and receipt paths; exact 17-resource
allowlist; two-prefix/two-process ordering; constructive no-site Packaging
bootstrap; three denied `.pth` classes and editable-root normalization; the
35-row executable census and three interpreter aliases; source-complete pyc
authority with the two exact optional inert-orphan predicates; stable versus
operational identity; health/card/gate ownership; and the two-local-commit
acceptance ledger.

## Reproduced checks

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- R11 retained-contract assertion: PASS; 12 required anchors, future scripts
  absent, and no plain `uv run python -S -B` spelling.
- Exact locked/no-sync/no-site probe: PASS; `.venv/bin/python3`,
  no site-packages path, `_virtualenv` and `coverage` absent, bytecode writing
  disabled.
- Local-only verification: PASS; 25 checks, zero failures.
- Orchestration YAML: PASS; 121 files parsed, 23 registry task IDs, zero
  duplicates.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.
- Parent-scope check: PASS; no `../reports`.

No cloud resource, hosted CI, public endpoint, remote, container, or deployment
was created. Independent high-risk review is the next required boundary.

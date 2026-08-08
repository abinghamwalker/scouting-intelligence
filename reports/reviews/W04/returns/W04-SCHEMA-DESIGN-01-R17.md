# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R17`
- objective: Retain every passing R16 and independent R10 closure while removing all actual uv host spellings from stable identity and making all four W04 semantic-authority routes standalone, exact, acyclic, and implementable.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R17.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R17.md`

## Summary

- Produced a full standalone R17 replacement retaining the R16 source, product, temporal, runtime, executable, alias, bytecode, resource, projection, build, two-root, gate, ownership, and ledger closures.
- Replaced stable uv host-path authority with `w04-local-control-bootstrap-v4` role tokens and an exact root-independent symlink/relative-target/one-contained-hop/final-regular-executable policy while preserving the current host's exact logical path, 26-byte raw target, physical path, byte/version/mode/size checks, normal literal selection, outer/child maps, and direct-physical/either-spelling/post-hoc-realpath denials as operational admission evidence only.
- Advanced the stable code/environment manifest to `w04-code-environment-admission-v14`; retained outer `w04-outer-environment-bootstrap-v2` and child `w04-child-environment-input-v2` because their normalized schemas and token bytes remain byte-for-byte unchanged.
- Added the exact `H1/H2` host-spelling-only perturbation proof requiring equal normalized environments, `environment_digest`, canonical code-manifest bytes and SHA-256, 25-key projection bytes, and `build_id`.
- Added a closed common authority canonicalization/review/acceptance protocol and complete field, possession, identity, and supported-feature routes with exact paths, fixed IDs, physical/canonical digest graphs, actors, clocks, dependencies, seven-field authority rows, packet IDs, path ownership, and rejection suites.
- Embedded the normative field roster of exactly 119 unique profile pairs with mechanically confirmed family counts: competition 10, team 11, player 26, match 47, action 18, event taxonomy 4, and tag taxonomy 3.
- Preserved the exact 17-resource physical-digest role while specifying canonical registry digests for downstream authority/dependency identity.

## Tests run

- command: `uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R17.md'); assert p.is_file() and p.stat().st_size > 190000"`
  - exit status: `0`
  - result: PASS; design exists and is 223,111 bytes. The initial sandboxed attempt exited `2` because the sandbox could not read `/Users/adrian/.cache/uv/sdists-v9/.git`; the exact command was rerun unchanged with approved uv-cache access and passed.
- command: `uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; controlling JSON reported `status: PASS`, `failures: []`, and all 25 local-only/one-root-uv checks passed.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R17.md`
- Exact field roster audit: `10 + 11 + 26 + 47 + 18 + 4 + 3 = 119`, with 119 unique ordered rows.
- `w04-local-control-bootstrap-v4`
- `w04-code-environment-admission-v14`
- `w04-outer-environment-bootstrap-v2` retained byte-identically
- `w04-child-environment-input-v2` retained byte-identically

## Risks

- No implementation, provider, network, data, configuration, migration, dependency, lockfile, Git, or self-approval action was performed. All future authority artifacts and runtime scripts remain blocked behind the separately owned packets, independent reviews, master acceptances, and gates named by the design.

## Follow-up items

- `none`

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`

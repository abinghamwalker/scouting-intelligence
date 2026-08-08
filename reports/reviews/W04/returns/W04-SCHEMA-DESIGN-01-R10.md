# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R10`
- objective: Retain every R9 and earlier closure while removing the stage-0/build-ID cycle, correcting current repository bytecode classification, making stable bytecode authority source-complete and inventory-independent, and admitting exactly the three measured venv interpreter aliases.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R10.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R10.md`

## Summary

- Replaced R9 in full while preserving its source, rights, temporal, identity, football-product, coverage, path, serializer, Packaging/bootstrap, `.pth`, editable-root, executable, resource, gate, ownership, and two-local-commit closures.
- Defined the exact pre-build admission prefix `data/working/wyscout/v5/.staging/admission/admission_run_id=<uuid>/runtime-pycache/`, selected before stage 0 without a build ID.
- Ordered two distinct `-S -B` Python processes: stage 0 returns the immutable code/environment manifest; build identity forms only after that manifest is frozen; a separate rebuild process then selects `data/working/wyscout/v5/.staging/<build_id>/<run_id>/runtime-pycache/`.
- Required both process-specific prefixes to be safe and empty before and after their process, with `PYTHONDONTWRITEBYTECODE=1`, zero in-place pyc reads/changes, no cleanup, no prefix reuse, and no operational ID/path in stable identity.
- Replaced inventory-derived bytecode authority with a complete sorted stable map over every admitted RECORD-owned third-party `.py`, repository-code-manifest-owned `.py`, and the exact uv-bootstrap source, independent of whether a pyc exists.
- Classified the first-root repository observation as exactly 56 pyc in 17 cache directories: 35 source-mapped normal, 20 source-mapped pytest-9.1.1 rewrite, and the optional source-absent inert PostgreSQL orphan.
- Bound the optional PostgreSQL orphan at `src/scouting/storage/__pycache__/postgres.cpython-312.pyc` to current magic `cb0d0d0a`, tag `cpython-312`, SHA-256 `ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac`, size `4,230`, and mode `0o644` when present; it grants no authority and may be absent in a fresh root.
- Retained the optional exact site-six inert-orphan predicate and made current 1,075-site/56-repository inventories first-root operational observations rather than two-root stable equality requirements.
- Corrected the interpreter alias closure to exactly three distinct mode-`0o755` symlinks: `python ->` admitted physical Python 3.12.12, `python3 -> python`, and `python3.12 -> python`; both relative chains are stable, while root-bearing spellings and `uv run python -> python3` remain operational.
- Updated manifest/build algorithm labels to `w04-code-environment-admission-v7` and `w04-wyscout-build-id-v8`.

## Tests run

- command: `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R10.md'); assert p.is_file() and p.stat().st_size > 22000"`
  - exit status: `0`
  - result: PASS; the exact R10 design exists and exceeds the required size.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; status `PASS`, failures `[]`, including `no_outside_root_config: found: []`.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R10.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R10.md`
- The earlier local-only verifier blocker was master-owned R10 packet text containing the redundant literal `../reports/**`. The master removed that literal; the exact verifier now passes with no failures.

## Risks

- The earlier packet-text blocker is resolved by the master and did not require a producer edit outside the return path in this follow-up.
- No design correction conflict was found.

## Follow-up items

- `none`

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no network/provider access, dependency/environment cleanup, delegation, or self-approval: confirmed
- no transient or persistent `../reports` output path/directory was created: confirmed

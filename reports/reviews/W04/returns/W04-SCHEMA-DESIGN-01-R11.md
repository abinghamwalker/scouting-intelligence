# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R11`
- objective: Retain every R10 and earlier closure while enforcing exact locked/no-sync uv process launches, naming both future repository entry points, and correcting the standalone revision lineage.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R11.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R11.md`

## Summary

- Replaced R10 in full while preserving every source, rights, strict temporal, identity/correction, key, source/Gold coverage, path/serializer, no-site Packaging bootstrap, three-`.pth`, editable-root, 35-executable, three-alias, two-prefix/two-process, source-complete pyc/orphan, resource, build/two-root, health/card, gate, ownership, and two-local-commit closure.
- Bound the pre-build admission process to exactly `uv run --locked --no-sync python -S -B scripts/admit_wyscout_v5_runtime.py`.
- Bound the post-build-ID rebuild process to exactly `uv run --locked --no-sync python -S -B scripts/rebuild_wyscout_v5.py`.
- Defined both as exact eight-token argv from the repository root. Missing, reordered, duplicated, or extra flags/arguments; plain `uv run`; sync/reconciliation; alternate interpreters or entry points; generated-script execution; and site initialization fail.
- Required stage 0 to continue independently verifying `pyproject.toml`, `uv.lock`, complete `L`, installed `I`, and `L==I`; the uv flags do not replace byte admission.
- Bound stable launch evidence to ordered argv, process role, uv version and physical digest, and both repository-relative entry-point paths/bytes. Root-bearing uv spelling and the observed `python3` launch alias remain operational.
- Named `scripts/admit_wyscout_v5_runtime.py` and `scripts/rebuild_wyscout_v5.py` as future implementation paths only; neither script was created or edited.
- Updated the stable manifest/build algorithm labels to `w04-code-environment-admission-v8` and `w04-wyscout-build-id-v9` to cover the added stable launch contract.
- Corrected final lineage to state that R11 closes the returned R10 master findings without self-approval.

## Tests run

- command: `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R11.md'); assert p.is_file() and p.stat().st_size > 22000"`
  - exit status: `0`
  - result: PASS; the exact R11 design exists and exceeds the required size.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; validator status `PASS`, failures `[]`, all 25 reported checks passed.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R11.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R11.md`

## Risks

- No residual design, scope, dependency, environment, architecture, provider, network, or local-only conflict found.

## Follow-up items

- `none`

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no network/provider access, environment mutation/cleanup, delegation, or self-approval: confirmed
- future entry-point scripts were not created or edited: confirmed

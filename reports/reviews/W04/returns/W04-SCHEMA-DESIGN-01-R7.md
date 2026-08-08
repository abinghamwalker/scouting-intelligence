# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R7`
- objective: Replace the R6 Wyscout schema design with a standalone R7 that closes
  the two new P1 findings while retaining all seven R5 closures.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R7.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R7.md`

## Summary

- Replaced direct-import distribution selection with a deterministic conservative
  pre-execution closure rooted at exact `uv sync --locked --all-groups` selection.
- Defined PEP 503 identity, root/group/extra/marker recursion, compatible-wheel
  selection, exact locked-versus-installed equality, per-member uv cache/extracted/
  installed byte checks, installed RECORD-derived file/import ownership, namespace
  and native-extension rules, a runtime loaded-owner subset, and no runtime
  admission expansion.
- Added explicit positive proofs for `pydantic → pydantic-core` and
  `polars → polars-runtime-32`, plus ambiguous, unowned, installed-only, lock-only,
  and late-dynamic-import negative proofs.
- Defined a fixed `record_kind=unknown` rejected-record partition with a closed
  raw-kind state token and domain-separated canonical state/value SHA-256. Covered
  missing, null, non-string, safe unknown string, and unsafe string states; preserved
  original typed values; failed digest collisions; prevented path escape; and
  excluded unknown records from known raw, rejected-field, Silver, and Gold.
- Retained the seven R5 closures and the R6 source, schema, identity, temporal,
  serializer, two-root, health/card/gate, and controlling two-commit ledger design.

## Tests run

- command:
  `uv run python -c "from pathlib import Path;
  p=Path('reports/reviews/W04/wyscout-schema-design-R7.md');
  assert p.is_file() and p.stat().st_size > 18000"`
  - exit status: `0`
  - result: PASS; standalone design exists and is 52,872 bytes.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; validator reported `status=PASS` and no failures.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R7.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R7.md`

## Risks

- The artifact is an implementation design, not an implementation or approval.
  Admission and quarantine implementations must reproduce the exact closed
  algorithms and negative proofs before `G-W04` can pass.

## Follow-up items

- Master readback and independent review; this producer did not self-approve.

## Scope confirmation

- no Git operations: yes
- no unauthorised dependency or lockfile changes: yes
- no edits outside `allowed_paths`: yes

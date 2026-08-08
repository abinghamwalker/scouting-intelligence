# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01`
- objective: Produce the final standalone R8 W04 Wyscout design, retaining R7's
  distribution and unknown-kind closures plus every accepted R6/R5 boundary while
  correcting the eight P1 and two P2 regressions returned against R7.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R8.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R8.md`

## Summary

- Restored strict-before temporal eligibility for every dependency and authority:
  `observed_at < cutoff`, `available_at < cutoff`, and aggregate watermark
  `< cutoff`; equality fails.
- Retained the fixed `record_kind=unknown` partition/digest while making the strict
  source-record envelope and exact completion-path map the sole record-family
  authority; provider payload cannot select a family.
- Restored the exact known Bronze `records/record_kind=...` path, exact
  player-match key, and exact Gold key. Kept `feature_schema_hash` as a required
  non-key proof field.
- Restored source `DataCoverage` and separate exact Gold
  identity/lineup/action/coordinate/possession/temporal integer coverage equations,
  zero-denominator rules, minimum, and applicability ordering.
- Retained conservative all-groups `L == I` closure and added exact safe
  `entry_points.txt`-derived console/gui script admission, controlled
  `../../../bin/<safe-name>` resolution, actual byte/hash/size/mode/shebang checks,
  rebuild denial, and reviewed stable shebang normalization.
- Restored pre-existing pyc enumeration without cleanup, current cache-tag/magic and
  singular RECORD-owned source mapping, operational hashes, stable policy/source
  map, early alternate prefix, `-B`, `PYTHONDONTWRITEBYTECODE=1`, and zero rebuild
  pyc reads/new or changed bytecode.
- Kept uv version and physical executable digest stable while moving its resolved
  absolute path to operational evidence only.
- Restored the exact 17-path resource allowlist and kept strict source, identity,
  runtime, resource, parent-product, and output categories disjoint.
- Retained the complete source/rights, authority, identity/correction, football,
  path/serializer, build/two-root, health/card/gate, ownership, and two-local-commit
  ledger graph for W04.1-W04.7, P2.1-P2.9, and `G-W04`.

## Tests run

- command: `uv run python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R8.md'); assert p.is_file() and p.stat().st_size > 22000"`
  - exit status: `0`
  - result: PASS; the standalone R8 design exists and exceeds 22,000 bytes.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; status `PASS`, 25 checks passed, zero failures.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R8.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R8.md`
- `orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-01-R7.yaml`
- `reports/reviews/W04/wyscout-schema-design-independent-review-R6.md`

## Risks

- R8 is an implementation design and does not self-approve. Master readback and a
  separate independent review remain the acceptance authorities.
- No dependency, provider, rights, network, migration, storage-root, environment
  cleanup, Git, or local-only boundary change was made or proposed.

## Follow-up items

- Master and independent reviewer should reproduce the R8 algorithms and decide
  acceptance; no implementer-side follow-up remains.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

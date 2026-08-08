# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R19`
- objective: Produce the standalone R19 replacement that preserves accepted R18,
  refreshes the truthful operational bytecode evidence, and closes the no-write
  independent-review harness without changing stable schema authority.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R19.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R19.md`

## Summary

- Produced a complete standalone R19 replacement of R18. It preserves the
  accepted R18 merits and explicitly records that invalid independent review R11
  issued no R18 merits verdict.
- Preserved the complete 119-pair field roster and `10/11/26/47/18/4/3`
  decomposition, strict UUID `ActorId`, all twelve possession-predicate fields,
  approved field contract-test path, temporal/identity/football-product
  contracts, exact path/serializer/resource closures, root uv launch, H1/H2
  proof, 24-key intersection, and `16/8/10/25/25/20` stable cardinalities.
- Refreshed the R19 operational evidence snapshot to site `1,086`: `973` normal
  lexical names = `972` distribution-source mappings + one uv-bootstrap mapping,
  `112` pytest rewrites, and optional-six present. Repository evidence remains
  `58` pycs in `19` cache directories = `35` mapped normal + `20` mapped pytest
  + the three exact optional inert orphans.
- Preserved the exact eleven-file Packaging-cache incident: every path, installed
  source sibling, size, mode `0o644`, link count `1`, magic `cb0d0d0a`, shared
  modification epoch/time, and SHA-256. The files are classifiable
  `SITE_DISTRIBUTION_NORMAL` operational caches and confer no stable authority.
- Replaced fixed future-count admission with actual-run read-only preflight:
  every site/repository pyc must classify, unclassified state fails, and the
  complete postflight inventory must be byte-identical to preflight. Creation,
  deletion, mutation, or other drift invalidates the run; cleanup never converts
  failure into success.
- Updated health and required-test contracts to record the actual run preflight
  decomposition and its delta from the R19 evidence snapshot. A later actual
  count need not equal `1,086` when mapped cache state changed before preflight.
- Added the closed independent-review harness: shell census/inventory before any
  Python import; locked/no-sync root uv only; `PYTHONDONTWRITEBYTECODE=1` and
  `python -B` for every helper; `python -S -B` when installed packages are
  unnecessary; first-instruction control verification for installed-package
  helpers; identical shell postflight; and no cleanup, repair, sync, cache purge,
  or environment recreation. The harness is review procedure, not stable build
  input.
- Retained the stable `w04-local-control-bootstrap-v4`,
  `w04-outer-environment-bootstrap-v2`,
  `w04-child-environment-input-v2`, and
  `w04-code-environment-admission-v14` preimages and version literals unchanged.

## Tests run

- command: exact packet acceptance shell block around
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R19.md'); s=p.read_text(); assert p.stat().st_size > 225000; assert '1,086' in s and '1,075' not in s; assert 'PYTHONDONTWRITEBYTECODE=1' in s and 'python -B' in s"`
  - exit status: `0`
  - result: PASS; R19 is `236,602` bytes, contains the required current evidence
    and no stale prior count, contains both bytecode-denial controls, and the
    before/after site and repository pyc counts were equal.
- command: before/after site/repository pyc-count guards around
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; controlling JSON reported `status: PASS`, `failures: []`, and
    all 25 local-only/one-root-uv checks passed. Site/repository counts remained
    `1,086`/`58`.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R19.md`
- Exact R19 observed bytecode decomposition:
  `1,086 = 972 + 1 + 112 + 1`; repository `58/19 = 35 + 20 + 3`.
- Exact incident roster: eleven mapped normal Packaging pycs with present
  installed source siblings and the shared incident timestamp.
- Stable schema versions retained: `v4/v2/v2/v14`.
- Stable schema cardinalities retained: `16/8/10/25/25/20`.

## Risks

- R11 remains invalid and non-adjudicating; R19 does not use it as a merits
  approval or rejection.
- No cleanup or repair was performed. The eleven operational files remain
  classifiable evidence, and future review/runtime validity depends on each
  bounded run's own exact preflight/postflight identity.
- No implementation, configuration, orchestration, source, test, dependency,
  lockfile, provider, network, data, migration, Git, deployment, or
  self-approval action was performed.

## Follow-up items

- `none`

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`

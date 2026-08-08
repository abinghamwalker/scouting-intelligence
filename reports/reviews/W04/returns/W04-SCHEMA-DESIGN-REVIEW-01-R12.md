# Subagent return — W04-SCHEMA-DESIGN-REVIEW-01-R12

## Files changed

- `reports/reviews/W04/wyscout-schema-design-independent-review-R12.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R12.md`

## Summary

Completed the fresh independent merits review of all 4,357 R19 lines under the
required bytecode-denying preflight/postflight procedure.

Recommendation: **REWORK**

Finding:

- `R12-P1-01` — R19 requires every one of the 33 Class-E installed wrappers to
  use exactly `.venv/bin/python` and explicitly rejects `python3`. Four current
  singularly RECORD-owned wrappers use `.venv/bin/python3`: `detect-secrets`,
  `detect-secrets-hook`, `httpx`, and `pip-licenses`. Their remaining wrapper
  bytes match the required deterministic template. Because admission is
  read-only/no-sync and every executable row is mandatory, the current root
  cannot pass R19 admission.

P0: 0. P1: 1. P2: 0.

## Tests run

- shell-only pyc preflight inventory — exit 0; site 1,086, repository 58; exact
  metadata/content/combined digests recorded in the review.
- bytecode-disabled locked/no-sync static field/profile reproduction — exit 0;
  exact 119 unique pairs, profile equality and 10/11/26/47/18/4/3.
- bytecode-disabled strict ActorId/EvidenceDependency reproduction — exit 0;
  strict/canonical actor behavior and closed five-key dependency reproduced.
- bytecode-disabled complete site/repository pyc classification — exit 0;
  site 972 distribution normal + 1 uv bootstrap + 112 pytest + 1 optional six;
  repository 35 normal + 20 pytest + 3 exact inert orphans; eleven Packaging rows
  exact.
- bytecode-disabled lock/install/wheel reproduction — exit 0 after bounded helper
  canonicalization correction; L=I=82, no differences, 81 compatible selected
  wheels, required native examples exact.
- bytecode-disabled complete executable census — candidate assertion failed at
  `detect-secrets`; bounded follow-up exit 0 and isolated exactly four
  first-line-only mismatches while reproducing 35=33E+1P+1W and 21 owners.
- bytecode-disabled `.pth`, Python alias/physical and uv identity checks — exit 0.
- bytecode-disabled source-evidence hashing — exit 0; all 18 physical rows and
  991,136,406 bytes matched.
- bytecode-disabled schema/cardinality/projection check — exit 0; exact
  16/8/10/25/25/20, 24-key intersection, 12/6 possession, 29/32 environments.
- packet report-size/recommendation acceptance check — exit 0; report existed,
  exceeded 35,000 bytes and contained a recommendation.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B
  scripts/verify_local_only.py` — exit 0; PASS, 25 checks, zero failures.
- identical shell pyc postflight — PASS_IDENTICAL; 1,086 site / 58 repository,
  20,047,587 / 1,475,178 bytes, and every metadata/content/combined digest
  exactly equal preflight.

## Artifacts/evidence

- Independent review:
  `reports/reviews/W04/wyscout-schema-design-independent-review-R12.md`
- Return:
  `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R12.md`
- Preflight global combined inventory:
  `5a332924c77f4418cee2b1024cca2e235d0f3c837c077de9cc451b666ef92d96`
- Postflight global combined inventory:
  `5a332924c77f4418cee2b1024cca2e235d0f3c837c077de9cc451b666ef92d96`
- Inventory equality: `PASS_IDENTICAL`

## Risks

- Open P1 prevents the executable-admission stage from succeeding against the
  current locked root.
- The review chain is valid: mandatory final postflight exactly equals
  preflight. No cleanup or repair was performed.
- Future runtime/product implementation remains outside this design-review task.

## Follow-up items

- Produce a bounded replacement design that truthfully closes the four exact
  wrapper shebang rows and updates affected stable manifest/schema authority, or
  separately establish and review a reproducible environment whose bytes satisfy
  the claimed template.
- Run a fresh master verification and different independent merits review.

## Scope confirmation

- no Git operations
- no dependency or lockfile changes
- no `.venv`/pyc cleanup, repair, sync, purge or recreation
- no provider/network, implementation, configuration, data, cloud, container or
  deployment action
- no edits outside the two allowed report paths

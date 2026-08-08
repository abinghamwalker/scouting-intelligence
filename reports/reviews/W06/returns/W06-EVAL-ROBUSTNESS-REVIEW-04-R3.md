# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-REVIEW-04-R3
- objective: Perform the final fresh public-only R3 review of exact stress/control
  lineage, unsupported-fixture authority, and deterministic identity retention.

## Files changed

- reports/reviews/W06/evaluation-robustness-independent-review-R3.md
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R3.md

## Summary

- final verdict: **REWORK — 0 P0, 4 P1**.
- exact stress master witness
  `013da049ef32c63d7bf5d40e825b7d377000cca70fe8b6c86fb2becb05797598`:
  **ACCEPTED** by the normal constructor with split IDs/specification and rolling-window
  ranked rows/per-query/aggregate/interval children; split comparison rankings remain.
- exact metadata master witness
  `75b2bc182bbd1e72816de51ce7516e1cf1ee2475328aa49cbabca80485699e1b`:
  **ACCEPTED** by the normal constructor with `bb...bb`, obs2/obs3 input and stale
  obs0/obs1 baseline/null/comparison children.
- the control-authority class remains open: arbitrary bare `bb...bb` metadata authority
  normally computes control `fd55e1eeaf2c977f0aa38156af350fb98f1b56a8b77d50aca10681cec86a74ba`
  over generic rows, with unchanged children and no content-addressed authority object.
- fixture SHA is exactly
  `eee02e82271041c0da10f1474770f983d920b7cff32e08f670e03ac614104b00`,
  but the fixture contains only a computed population, does not drive its pair-absence
  field, and pins no literal stress/control/applicability identities.
- fresh sparse split correctly returns typed unsupported
  `26e4845c435365032b7b87870d18e61ee082ecd5962ab69d5afca0de5884af25`;
  fresh otherwise sufficient incoherent-label spec `f314dffd...aca2` and
  common-candidate spec `131b4a15...f00c` instead raise from an invalid empty-deficit
  unsupported object.

## Narrow constructor/fixture matrix

| Surface | Outcome |
|---|---|
| Split with rolling children | `013da049...97598` accepted — open P1 |
| Metadata with foreign input/stale children | `75b2bc18...e1b` accepted — open P1 |
| Bare metadata authority | `fd55e1ee...a74ba` accepted — same open control-authority P1 |
| Public computed stress roster | all 8 computed; identities recorded in detailed report but unpinned |
| Sparse split | `26e4845c...af25` typed unsupported; absent from fixture |
| Incoherent label/common candidates | raises empty-deficit validation error — open P1 |
| Pair absence | `4f4f1a15...c98a` typed unsupported, no values/permutation; fixture field unused |
| Applicability | `211213b1...58f5`, exact expert/pair missing evidence; identity unpinned |

## Tests run

- command: packet focused pytest with task-local UV cache
  - exit status: 0
  - result: `15 passed in 0.23s`.
- command: packet focused Ruff check with task-local caches
  - exit status: 0
  - result: all checks passed.
- command: packet focused mypy with task-local caches
  - exit status: 0
  - result: no issues in four source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-r3-review-lint-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- command: `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: exact fixture SHA above.
- command: public exact master-witness probe via `uv run --no-sync python`
  - exit status: 0
  - result: both exact witnesses accepted.
- command: public unsupported/incoherence and retained-R2 closure probes via
  `uv run --no-sync python`
  - exit status: 0
  - result: exact outcomes recorded in the detailed report; complete walk-forward,
    source-intersection absence, strict k binding, label-only shuffle, failure source,
    static claims and caller-deficit rejection retained.
- command: initial four UV checks without a task-local cache
  - exit status: 2 each
  - result: sandbox denied the global UV cache before execution; all were rerun
    successfully with task-local `/private/tmp` caches and `--no-sync`.

## Artifacts/evidence

- reports/reviews/W06/evaluation-robustness-independent-review-R3.md
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R3.md
- public fixture SHA:
  `eee02e82271041c0da10f1474770f983d920b7cff32e08f670e03ac614104b00`
- detailed exact constructor, identity, unsupported and retained-closure evidence is in
  the independent review report.

## Risks

- remaining P0: none.
- remaining P1: four — stress child lineage; control input/child plus bare authority
  substitution; fixture unsupported/pair/identity authority; invalid empty-deficit
  handling for incoherent labels/common candidates.
- remaining risk is high until the smallest correction in the detailed report is
  implemented and freshly reviewed.
- evidence remains implementation-only and supports no expert, protected, transfer,
  calibration, prospective, provider, recruitment-outcome, or empirical claim.

## Follow-up items

- Derive stress/control children and input identities at normal construction from exact
  embedded inputs; use a verifiable kind-specific authority object; make public fixture
  bytes drive computed and unsupported populations, pair absence and literal identities;
  return exact typed evidence for incoherent/common-candidate deficits; then obtain a
  fresh independent review.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider/credential access: confirmed.
- no implementation or test edits: confirmed.
- no edits outside `allowed_paths`: confirmed.

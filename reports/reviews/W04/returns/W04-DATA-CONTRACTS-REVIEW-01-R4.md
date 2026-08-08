# Subagent return: W04-DATA-CONTRACTS-REVIEW-01-R4

## Task

- task_id: `W04-DATA-CONTRACTS-REVIEW-01`
- objective: Perform a fresh independent, read-only review of the bounded W04
  data-contract R4 correction, including source-bound completeness and equal-clock
  cross-team adversarial challenges.
- result: **REWORK**
- findings: P0 `0`, P1 `2`, P2 `0`
- architecture revision required: **No**

## Files changed

- `reports/reviews/W04/wyscout-data-contracts-independent-review-R4.md`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-REVIEW-01-R4.md`

No implementation, test, config, orchestration, authority, source, preimage, prior
review, verification, producer return, dependency, lockfile, product, manifest,
receipt, runtime, serializer, or build byte was changed.

## Summary

The three R3 finding families close at the submitted selected-evidence boundary:
all six Fact/Gold `2/2` coverage forgeries reject; out-of-bounds, mixed, and
three-position anomalies remain evidence but count zero and reject forged counts;
and singleton contested evidence remains unresolved with zero Fact/Gold count.

Two new P1 findings remain:

1. `W04DCR4-P1-001`: a caller can remove a physical source action from the declared
   complete period, lower the mirrored count, and build a consistent Action,
   Possession, Fact, and Gold chain while lineage still contains the omitted row.
   Fact coverage is exact only over the caller-selected subset. Sequence entries can
   also use an action UUID not bound to the provider event ID, and causal other-player
   sequence rows need not reach Fact/Gold provenance.
2. `W04DCR4-P1-002`: two cross-team CONTROL actions at the same clock leave the first
   action `ELIGIBLE_RESOLVED` and Gold-counted because the uncertainty branch clears
   active state without removing the already-appended first action group.

Both require bounded contract/factory and regression-test correction under existing
R20/R21 authority. Neither requires or authorises architecture, feature, product,
provider-rights, dependency, storage, runtime, or scope revision.

## Tests run

- Public-constructor R4 adversarial matrix — exit `0`:
  - six-dimension Fact and Gold forgeries: rejected;
  - out-of-bounds, mixed, and three-position Fact/Gold drift: valid zero, forgeries
    rejected;
  - singleton contested Fact/Gold promotion: valid zero, forgeries rejected;
  - source-action truncation through Gold: **accepted** with lineage ordinals `(0,1)`,
    period/Fact ordinals `(1)`, and Fact/Gold action count `1`;
  - arbitrary noncanonical other sequence action ID: **accepted**;
  - equal-clock cross-team CONTROL through Gold: **accepted** with states
    `ELIGIBLE_RESOLVED` and `INELIGIBLE_UNMAPPED`, Gold resolved count `1`.
- `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — exit `0`; 2 files already formatted.
- `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — exit `0`; all checks passed.
- `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — exit `0`; no issues in 2 source files.
- `uv run lint-imports` — exit `0`; 30 files, 46 dependencies, 3 contracts kept, 0 broken.
- `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` — exit `0`; 452 passed in 73.68s.
- `uv run bandit -q -r src/scouting/contracts/wyscout_data.py` — exit `0`; no findings.
- `uv run python scripts/verify_local_only.py` — exit `0`; PASS, 25/25 and zero configured remotes.

Initial sandboxed import-lint and Bandit attempts exited `2` solely because the
sandbox denied shared uv-cache metadata reads. Exact approved read-only reruns passed;
no environment or dependency state changed.

## Artifacts/evidence

- Independent review:
  `reports/reviews/W04/wyscout-data-contracts-independent-review-R4.md`
- Independent review SHA-256:
  `765d3b190246e8c821e9484f6d7bdd035fba7f989776e2fa2b45caa5e8606071`
- Reviewed implementation SHA-256:
  `2ca2862550c48a8db899f25c26612d694a7ca8041416cf0aae4dcd39b5a2bb5e`
- Focused test SHA-256:
  `0ddb9e2bd31dded899a68b7b6344cf17321dffe947ab6dffc98267eb918bdc69`
- R4 producer return SHA-256:
  `f66c4ea9133a23394d67d81d4f7badf989be39594eb2fec7165f9928a429be68`
- Supplemental R4 master verification SHA-256:
  `cd6243bc96081281230a4c8b60161ad5d191904a6b19f57ffc84b24ee524a95f`
- Every packet fixed authority/source/preimage/prior-review binding matched; the exact
  table is in the independent review.

## Risks

The accepted four-feature Gold surface can currently undercount source actions and
promote one side of a simultaneous cross-team boundary as resolved while reporting
coverage derived from incomplete selected evidence. Product implementation must not
rely on R4 before correction, fresh review, and master acceptance.

## Follow-up items

- Bind complete period and player-match/coverage populations to independently
  recomputable admitted Bronze/source evidence; bind every sequence action identity
  and semantic input to that evidence and retain all causal source rows.
- Unassign both sides of equal-clock cross-team CONTROL and dependent contested
  evidence without discarding genuinely deterministic pre-clock group members.
- Add direct public-constructor regressions for truncation/period omission,
  noncanonical sequence identities, other-player provenance, all six source
  populations, and equal-clock behavior through Gold.
- Rerun the exact packet suite and obtain a fresh independent review with zero P0-P2.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- frozen authority and no architecture revision: confirmed
- exactly four supported features retained: confirmed
- no provider access, network/cloud/container/external service, endpoint, hosted CI,
  deployment, serializer, product byte, manifest, receipt, runtime, or build created:
  confirmed

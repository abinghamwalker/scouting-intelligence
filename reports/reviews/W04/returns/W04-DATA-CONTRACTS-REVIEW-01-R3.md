# Subagent return: W04-DATA-CONTRACTS-REVIEW-01-R3

## Task

- task_id: `W04-DATA-CONTRACTS-REVIEW-01`
- objective: Independently reproduce the three suspected W04 R3 public-constructor
  failures and issue the acceptance disposition under frozen authority.
- result: **REWORK**
- findings: P0 `0`, P1 `3`, P2 `0`

## Files changed

- `reports/reviews/W04/wyscout-data-contracts-independent-review-R3.md`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-REVIEW-01-R3.md`

No implementation, test, config, authority, source, product, dependency, lock,
orchestration, verification, or prior evidence file was changed.

## Summary

Three direct probes through validated public constructors reproduced:

1. all six `SilverPlayerMatchFact` coverage dimensions can be changed from fixture
   `1/1` to `2/2`, after which Gold accepts and aggregates `2/2`;
2. `ActionPosition(x=-1, ..., within_accepted_bounds=False)` is accepted and counted
   as `coordinate_known_action_count=1` in both Fact and Gold despite frozen
   `PRESERVE_AND_INELIGIBLE` authority; and
3. contested pair `(1,10)` is accepted as `ELIGIBLE_RESOLVED`, a singleton
   possession, and a fact count of one without the required following resolved
   same-period possession.

Each is P1 and requires bounded contract/test rework. None requires or authorises an
architecture, product, authority, provider-rights, dependency, or scope revision.

## Tests run

- Public-constructor probe matrix — exit `0`; all three invalid states printed
  `ACCEPTED` with the exact values recorded in the independent review.
- `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — exit `0`; 2 files already formatted.
- `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — exit `0`; all checks passed.
- `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` — exit `0`; no issues in 2 files.
- `uv run lint-imports` — exit `0`; 3 contracts kept, 0 broken.
- `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` — exit `0`; 437 passed in 88.83s.
- `uv run bandit -q -r src/scouting/contracts/wyscout_data.py` — exit `0`; no findings.
- `uv run python scripts/verify_local_only.py` — exit `0`; PASS, 25/25, zero remotes.

Initial sandboxed import-lint and Bandit attempts exited `2` solely because the
workspace sandbox denied shared uv-cache metadata reads. Exact reruns with approved
read access produced the passing results above; no state was mutated.

## Artifacts/evidence

- Independent review:
  `reports/reviews/W04/wyscout-data-contracts-independent-review-R3.md`
- Independent review SHA-256:
  `a86e30a1d56ae1c88f9bbb36e067f74f4fb234664a4ba08e9e05589b2e2bb066`
- Implementation SHA-256:
  `53abc69b85a1a60c13107a8b0a09ee6e066e792b1667c866cf9a9c3f5fd242ff`
- Focused tests SHA-256:
  `f13b5ccb8930bef22c94f74feeda1b66c87224704458c0460de022e66af3764b`
- All packet fixed authority/source/preimage/prior-return bindings matched;
  the exact table is in the independent review.

## Risks

The accepted four-feature Gold surface can currently promote forged coverage,
ineligible coordinate evidence, and unresolved contested-possession evidence. Product
implementation must not rely on R3 before correction and fresh independent review.

## Follow-up items

- Bound coverage at the Fact evidence boundary before Gold aggregation.
- Exclude preserved out-of-bounds positions from accepted coordinate counts.
- Enforce possession-v2 contested buffering/unassignment until following resolved
  same-period control.
- Add direct Fact/Gold and possession-sequence regressions, rerun the packet suite,
  and obtain a fresh independent review.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- frozen authority and no architecture revision: confirmed
- no provider access, network/cloud/container/external service, endpoint, hosted CI,
  deployment, serializer, product byte, manifest, receipt, runtime, or build created:
  confirmed

# Subagent return

## Task

- task_id: `W04-SOURCE-COMPLETION-INDEX-REVIEW-01-R1`
- objective: Independently and adversarially review the exact W04 source-completion-
  index R2 candidate, provenance/lineage binding and equal-clock correction, returning
  PASS only if the completion reader is the executable product completeness boundary.
- disposition: **REWORK**
- findings: P0 `0`, P1 `1`, P2 `0`

## Files changed

- `reports/reviews/W04/wyscout-source-completion-index-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-REVIEW-01-R1.md`

## Summary

- Verified every packet fixed binding before analysis.
- Independently recomputed all five frozen event-member SHA-256 digests, byte sizes,
  top-level row counts, exact aggregate `3071395`, accepted index content address and
  size, completion/source-manifest digests, and frozen R20/R21 digests.
- Independently reprojected real match `2499719`, period `1H`: its `901` physical
  actions reproduce accepted membership digest
  `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`.
- Reproduced rejection of a self-consistent unaccepted index, address spoof, every
  required supplied-population mutation, whole-period, whole-indexed-period and
  whole-match omission.
- Reproduced strict integer/no-coercion behavior and distinct missing/null/unmapped
  raw evidence; reproduced the equal-clock, contested-buffer, provenance and
  completion-digest lineage closures.
- Confirmed the Gold roster remains exactly four supported count features.
- Opened `W04SCIIDXR1-P1-001`: public checked constructors return accepted Gold from
  a caller-selected singleton sequence carrying a non-index membership digest while
  every completion-reader function is fail-fast and receives zero calls. The stated
  test-only/direct-model restriction is therefore conventional rather than executable.
- Required one bounded correction making every authorized downstream product
  construction/materialization path execute the accepted reader comparison and reject
  direct low-level evidence as completeness authority. No broader architecture
  revision is required by the finding.

## Tests run

- command:
  `shasum -a 256 src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R2.md`
  - exit status: `0`
  - result: all six packet bindings matched; index size `644037` and aggregate
    `3071395` matched.
- command:
  `uv run ruff format --check src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: four files already formatted.
- command:
  `uv run ruff check src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: all checks passed.
- command:
  `uv run mypy src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: success; no issues in four files.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 31 files, 49 dependencies, all three contracts kept.
- command:
  `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: `0`
  - result: all `488` independently collected tests passed.
- command:
  `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; all 25 checks passed with zero failures and zero configured remotes.
- command:
  `uv run pytest -q` for the three equal-clock regressions and completion-digest
  boundary regression named in the review.
  - exit status: `0`
  - result: `4 passed in 0.18s`.
- command: independent raw-member `shasum`, `wc -c`, and `jq length` matrix.
  - exit status: `0`
  - result: all five fixed member digests/sizes/counts matched; totals `902888532`
    bytes and `3071395` rows.
- command: bounded `uv run python -c` period rederivation, accepted-address probe,
  strict-type/missing-null probe, population mutation matrix, whole-match omission,
  and fail-fast-reader Gold bypass probe.
  - exit status: `0` for every credited probe.
  - result: all required positive/negative index behaviors reproduced; bypass probe
    returned accepted four-feature Gold with arbitrary membership digest and zero
    reader calls.

The first combined prescribed-check attempt was rejected before execution because
the sandbox could not read existing shared uv-cache metadata. The exact unchanged
commands were rerun with read access and passed. No environment or dependency state
was changed.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/wyscout-source-completion-index-independent-review-R1.md`
  - SHA-256:
    `14d800764f2c2c0d7d50b93c05233b416e796033b107da81a5e80d4a37c48a55`
- accepted immutable index:
  `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
- open finding: `W04SCIIDXR1-P1-001`
- decisive executable output:
  `BYPASS_ACCEPTED ... membership=999...999 period_action_count=1 sequence_actions=1 completion_reader_calls=0`

## Risks

- P1: an authorized downstream implementation can presently construct accepted
  Silver/Gold contract values from a caller-selected subset without executing the
  completion reader. Product implementation must not resume on this candidate.
- No other open P0/P1/P2 finding was identified in the reviewed scope.

## Follow-up items

- Return only `W04SCIIDXR1-P1-001` for bounded enforcement rework.
- Obtain fresh independent review of the corrected exact candidate before the full
  repository master gate or product implementation resumes.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no delegation or self-approval: confirmed.
- no implementation, test, source, data, manifest, index, frozen authority,
  orchestration, product/runtime, cloud, container, provider, network, external
  service, endpoint, hosted CI, remote or deployment change/access: confirmed.

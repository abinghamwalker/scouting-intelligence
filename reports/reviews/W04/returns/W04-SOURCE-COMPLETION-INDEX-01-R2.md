# Subagent return

## Task

- task_id: `W04-SOURCE-COMPLETION-INDEX-01-R2`
- objective: Correct only `W04SCIR1-P1-001` by pinning every public
  completion-index validation, load, materialization, population-validation, and
  factory boundary to the accepted R1 content address while retaining independent
  content recomputation.

## Files changed

- `src/scouting/sources/wyscout_completion_index.py`
- `tests/unit/test_wyscout_source_completion_index.py`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R2.md`

## Summary

- Added the exact local accepted-index binding
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
- `validate_index` now rejects any stored address other than that binding before
  treating the candidate as authority. It still independently reconstructs the
  canonical payload from the candidate structure, recomputes SHA-256, compares the
  canonical bytes and stored address, and requires the recomputed address itself to
  equal the accepted binding.
- `load_source_completion_index` now rejects any caller-selected digest other than
  the accepted digest before root resolution or file opening. For the accepted
  argument it retains the existing payload SHA-256 recomputation, strict canonical
  parsing, structural validation, and filename/payload address equality checks.
- `materialize_source_completion_index` now validates and pins the index before path
  resolution or immutable-file access. Accepted materialization remains byte-
  idempotent.
- Existing whole-period/whole-match validators and factories already enter through
  `validate_index`; named regressions now prove that all four inherit the exact
  accepted-address pin.
- Added the master adversarial case: mutate one period membership digest, recompute
  internally self-consistent canonical bytes and SHA-256, and prove rejection solely
  because its address is not accepted. The test-forged address is
  `8c5d76e515abc90a9d8a7884af4cb3130d201689d5a56f2caa936446b6f3fade`.
- Added a separate address-spoof case proving that replacing the stored digest with
  the accepted digest does not bypass independent canonical-content recomputation.
- Added reject-before-open and reject-before-materialization-path regressions.
- The accepted index artifact, Wyscout contracts and contract tests, frozen evidence,
  source, data, orchestration, dependencies, and lock state were not edited.

## Tests run

- command:
  `uv run ruff format --check src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command:
  `uv run ruff check src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: all checks passed.
- command:
  `uv run mypy src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: success; no issues in 2 source files.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 31 files and 49 dependencies analyzed; all three contracts kept and zero
    broken.
- command:
  `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `365 passed in 11.15s`.
- command: `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; all 25 local-only and one-root-uv checks passed with zero failures.
- command: bounded read-only forged-address reproduction with `uv run python -c`
  - exit status: `0`
  - result: recomputed forged address
    `8c5d76e515abc90a9d8a7884af4cb3130d201689d5a56f2caa936446b6f3fade`,
    distinct from the accepted address.

The first combined acceptance-check attempt exited before running checks because the
workspace sandbox denied read access to shared uv-cache metadata. The exact command
was immediately rerun with approved cache access and passed as reported; no dependency
or environment state changed.

## Artifacts/evidence

- accepted immutable index binding:
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- `src/scouting/sources/wyscout_completion_index.py`
  - SHA-256:
    `d81acf16302ce47bffe6461181163e1607b8744ca68f75e5719a2e50c7e43285`
- `tests/unit/test_wyscout_source_completion_index.py`
  - SHA-256:
    `8b4194574e0d362c7ddcf43b3d6787de5672a9a71d1c938b20a5eb70781f2cef`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R2.md`

## Risks

- This producer return is implementation evidence, not independent review or master
  acceptance. The master should reproduce the exact self-consistent forged-index and
  reject-before-open probes.
- No residual implementation blocker was encountered.

## Follow-up items

- Independent master review of the exact R2 source/test hashes and accepted-index
  preservation.

## Scope confirmation

- no Git operations: confirmed.
- no delegation or self-approval: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no source, index artifact, data, contract, contract-test, orchestration, frozen
  evidence, prior-return, product, provider, network, cloud, container, hosted CI,
  endpoint, remote, or deployment access/change: confirmed.

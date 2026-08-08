# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R3`
- objective: Freshly and independently verify the corrected frozen R20 v15
  admission child and separate launcher against every R2 fail-open state and the
  full fixed-hash R3 gate without modifying producer bytes.

## Decision

- verdict: `REWORK`
- findings: `P0/P1/P2 = 0/2/0`
- review artifact:
  `reports/reviews/W04/wyscout-runtime-control-independent-review-R3.md`

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R3.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R3.md`

## Summary

- Verified all six fixed SHA-256 bindings exactly and rechecked them unchanged
  after the last bounded review command.
- The static quality, security, import-boundary and local-only checks pass.
- The full required 178-test fixed-hash gate fails `168 passed, 10 failed in
  35.95s`. Both collectors' final bin-only RECORD path exception rejects the
  frozen Bandit `data` and Greenlet `headers` PEP 427 installed rows. The retained
  launcher stops before admission, so the actual two-run proof does not execute.
- Confirmed a separate fail-open repository-pyc predicate: the launcher accepts an
  unmanifested `.py` plus pytest pyc as `REPOSITORY_PYTEST_REWRITE`, and the
  targeted candidate counterexample passes. The child does not independently
  enumerate actual pycs, so its repeated stable reconstruction cannot close this
  attack.
- Recorded exact bounded corrections for complete mapped external RECORD paths and
  closed launcher/child pyc source ownership plus pre/result inventory equality.
- Pre/post no-write inventories are identical: site digest
  `2f36c7b70cf5946f60f3595a673bdc9a771e46266403ddd331cabb46436e8fcb`
  over 1,087 pycs; repository digest
  `a19d7ec64519ca895895e4953c09de26e6d826562d36fa4d96487d4382f7e1d3`
  over 98 pycs.

## Tests run

- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: three files already formatted.
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: success, no issues in three files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `1`
  - result: `168 passed, 10 failed in 35.95s`; common final-hash RECORD rejection,
    including failure of the actual two-run admission test before child launch.
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `uv run python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks and zero failures.
- command: targeted
  `test_source_present_pytest_pyc_is_operational_denied_and_unchanged`
  - exit status: `0`
  - result: `1 passed in 0.06s`, reproducing fail-open acceptance of an
    unmanifested repository source/pyc.

All Python commands used `PYTHONDONTWRITEBYTECODE=1` and `UV_NO_SYNC=1`.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/wyscout-runtime-control-independent-review-R3.md`
- mandatory reviewer return:
  `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R3.md`
- fixed producer implementations/tests remain at the packet-bound hashes.

## Risks

- The current frozen runtime cannot admit its own accepted installation, so no
  build authority can be issued.
- An unmanifested repository source plus matching pyc is accepted by the launcher,
  while the child supplies no independent actual-pyc inventory check; shared or
  child-only bytecode substitution remains fail-open.

## Follow-up items

- Correct both installed RECORD collectors to admit only singular, exact
  five-scheme PEP 427-derived external destinations while retaining escape,
  collision, overwrite, ownership, byte/hash/size and mode rejection.
- Remove the unmanifested-source pyc acceptance; independently enumerate and
  compare actual site/repository pyc inventories in the child as well as launcher.
- Add positive Bandit-data/Greenlet-headers cases and negative external-path and
  unmanifested-source/pyc cases, freeze new hashes, and obtain fresh full review.

## Scope confirmation

- producer bytes read-only: confirmed
- no real-root publication or rebuild execution: confirmed
- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside the two allowed review paths: confirmed

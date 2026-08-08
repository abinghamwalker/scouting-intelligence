# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01`
- objective: Independently review the exact W04 admission child and sole launcher
  control plane through v15 code-manifest authority, immutable publication,
  one 25-key build projection and strict inverse invocation.

## Files changed

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R1.md`

## Summary

- Decision: `REWORK`; findings `P0/P1/P2 = 0/2/0`.
- Verified every packet fixed binding and all implementation-packet upstream fixed
  bindings before merits review. Producer bytes were not edited.
- Read the packet and every `read_first` file completely and reconstructed the
  ordered twenty manifest values, environment digest, content-addressed UUIDv5,
  exact 25-key projection, sole contract build ID and strict post-hash inverse.
- Ran two actual locked/no-sync, no-site, no-bytecode admission subprocesses under
  distinct direct non-symlink isolated mode-`0700` roots and operational UUIDs.
  Their manifests, build IDs and invocations were identical; immutable replay was
  safe; no rebuild prefix or rebuild/product/layer/receipt/run execution occurred.
- Returned P1 because the admission child issues v15 component digests without
  performing the accepted selector/lock/extracted/installed/executable/alias/
  stdlib/pyc/environment predicates. The result is internally deterministic but
  does not have the accepted component meanings and can admit drift by changing
  the resulting manifest/build instead of rejecting it.
- Returned a second P1 because the launcher imports the admission child and calls
  its `collect_stable_authority()` as its retained expected authority. Child and
  launcher therefore compare two executions of one oracle; shared omissions and
  substitutions agree rather than fail closed.
- Smallest rework surface is the existing producer-owned
  `scripts/admit_wyscout_v5_runtime.py`, `scripts/launch_wyscout_v5.py`, and
  `tests/unit/test_w04_wyscout_runtime_control.py`. No contract, aggregate,
  publisher, digest meaning, roster, logical model, dependency or root change is
  required.

## Tests run

- command: fixed SHA-256 and logical no-LF digest verification with `shasum` and
  read-only terminal-LF removal
  - exit status: `0`
  - result: all seven review bindings and five additional implementation bindings
    matched exactly.
- command: read-only preflight/postflight site and repository pyc content and
  metadata inventories
  - exit status: `0`
  - result: before/after counts remained `1087/98`; content digests remained
    `d1929771...6ee` / `17fa94b3...a23`; metadata digests remained
    `beb14c19...c26` / `49eadfc4...6e1`.
- command: locked/no-sync `uv run --locked --no-sync python -S -B -c <independent two-run admission harness>` with `PYTHONDONTWRITEBYTECODE=1`
  - exit status: `0`
  - result: byte-identical 2,249-byte manifests, equal build and invocation,
    content-addressed replay, no rebuild prefix and no rebuild execution.
- command: locked/no-sync `uv run --locked --no-sync python -S -B -c <independent projection/build/inverse reconstruction>` with `PYTHONDONTWRITEBYTECODE=1`
  - exit status: `0`
  - result: manifest `8650022a...d69`, UUIDv5 `4399f636-4348-5cd8-92be-f1b7bf27ea84`,
    environment `6261ace2...b0d`, build `f61a6e43...fc0`, exact 25/25 keys and
    strict inverse reproduced.
- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: three files already formatted.
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: success, no issues in three source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `161 passed in 35.86s`.
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no security findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks and zero failures.

All Python-bearing commands ran with `PYTHONDONTWRITEBYTECODE=1`, `UV_LOCKED=1`
and `UV_NO_SYNC=1`; direct Python helpers additionally used `-B` and `-S`.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-runtime-control-independent-review-R1.md`
- isolated operational evidence root:
  `/private/tmp/w04-independent-runtime-apxdo9fa`
- stable identities: manifest
  `8650022adb35503e543f21c88dd52c1da223483c5aaa6f16ba430be763765d69`,
  build `f61a6e4360c2a83a6009703985e7893f6408e83bd7d1ccc2187d5db4b62f5fc0`,
  invocation `25838f8099504f262e1a988e8b21283f76a55efdf48c624002f1072feb2106bc`.

## Risks

- Current admission output must not be master-accepted as an exact v15
  code/environment authority: materially incomplete checks are represented as if
  their accepted semantics had been proved.
- Current child/launcher agreement is not independent evidence because both sides
  use the same collector implementation.
- The documented same-trust-domain transient replace-and-restore residual remains
  after rework; this review does not broaden that accepted residual.

## Follow-up items

- Issue bounded producer rework on the three existing producer paths, preserving
  every fixed logical model/digest meaning/roster/dependency/root boundary.
- Obtain a fresh independent review after correction with the full v15 mutation
  matrix and child-vs-launcher oracle-disagreement proof.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

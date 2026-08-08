# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01`
- objective: Implement the exact local-only W04 admission child and sole launcher
  control plane through immutable code-manifest readback, one pre-build projection
  hash, strict inverse invocation construction, and a frozen non-executing rebuild
  plan.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R1.md`

## Summary

- Implemented the stdlib-only `PRE_BUILD_ADMISSION` child under the exact frozen
  locked/no-sync, no-site, no-bytecode argv. It accepts only the canonical common
  16-key and admission 8-key envelope, verifies the closed child environment and
  inherited source/result descriptors, guard-reads the explicit repository,
  pyproject/lock, installed RECORD, executable, interpreter/stdlib/uv and exact
  17-resource rosters, and derives the exact ordered twenty stable components with
  positive evidence counts.
- The child returns one canonical `w04-child-result-v2` / `PreBuildAdmissionResult`
  in the exact `W04CRSLT` v1 length-and-SHA-256 frame. It does not publish the
  manifest, calculate a build ID, create a rebuild prefix, or write product,
  layer, receipt, run or real-root bytes.
- Implemented the sole launcher path with bounded concurrent frame/stdout/stderr
  draining, one monotonic deadline, exact exit/EOF/frame/canonical-model checks,
  retained descriptor equality, independently retained component/proof comparison,
  and empty-prefix postcheck.
- The launcher guard-reads the accepted v2 config physical bytes and requires the
  logical no-LF identities `ba5db90f...63be` and `fe68e8f...fc0`. It publishes or
  confirms only the content-addressed code manifest through the accepted
  sidecar-free `WyscoutStagedPublisher`, reopens it, and requires exact byte,
  digest, size and UUIDv5 equality.
- Only after immutable readback, the launcher constructs `PreBuildProjection`,
  computes the sole build hash through `build_id_for_projection()`, constructs the
  post-hash invocation through `invocation_from_projection()`, and requires exact
  `projection_from_invocation()` equality. It returns a frozen plan with the code
  path, Bronze/Silver/Gold paths, rebuild prefix/receipt paths, exact
  `REBUILD_ARGV`, and caller-supplied strict v4 run ID.
- `execute_rebuild_child()` exposes the final generic exact-argv subprocess/result
  validation surface for the downstream accepted rebuild. Preparation never calls
  it, and the currently absent rebuild entrypoint was not executed.
- Two actual locked/no-sync admission subprocesses using different operational
  admission/run UUIDs produced one stable manifest, build ID and invocation;
  immutable replay retained the same final inode. Tests also prove no real code,
  admission, product, layer, receipt or run root was written.

Final candidate SHA-256 values:

- admission child: `dc162985e6bccaa4ea4161d22ddf89c2b2017968c4703e65dc1c37645e78602a`
- launcher: `4e97bb9828453c184dca14c78c71e2659df628d6aec6b459e41faf5e5da719a1`
- adversarial tests: `f596c5f353f162f16bc9e43cc0cb43e2c8d9553271ccb979075e98613e750422`
- final reconstructed repository-code authority:
  `2b9466c0e114a9dfa2ed7b1aaf7a12c9a9689649ab5d59bbe34dbe2c288a7df2`
- final local-resource component:
  `c62f263346fdb058c88e8bc48512fe976315c468b0c6a134ac9451a58e34f772`
- final selected-lock-closure component:
  `ab757c2402c989bf10fa66e2f93d1ebdf1199a04ee4af33cfc7822d963147f8a`
- exact evidence counts:
  `(1,1,1,35,298,82,1,1,17,1,1,1,82,1,1,3,1,1,5,298)`.

## Tests run

- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all three files already formatted.
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: success, no issues in three source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `161 passed in 36.27s`.
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no security findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks and zero failures; main branch and zero remotes.
- command: direct `collect_stable_authority(Path.cwd())` reconstruction under
  `uv run`
  - exit status: `0`
  - result: exact repository/local-resource/lock identities and all twenty positive
    counts above reproduced.

## Artifacts/evidence

- implementation and runtime evidence:
  `scripts/admit_wyscout_v5_runtime.py`, `scripts/launch_wyscout_v5.py`
- actual-subprocess, two-run, immutable-replay, inverse and attack evidence:
  `tests/unit/test_w04_wyscout_runtime_control.py`
- accepted v2 identities consumed:
  schema `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be`,
  product `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0`

## Risks

- The R20 same-trust-domain transient path replace-and-restore residual remains;
  persistent replacements, descriptor/path drift and bounded races fail, but this
  local checkpoint design is not a cryptographic prevention boundary.
- The real rebuild entrypoint is deliberately absent in this packet. Its generic
  exact-argv executor is implemented and statically checked, but actual completion
  execution/result and product receipts remain for the downstream serial product
  packet and its independent review.
- Admission is intentionally fixed to the accepted current macOS arm64 Python
  3.12.12 / uv 0.9.21 environment; environmental drift fails closed rather than
  updating authority implicitly.

## Follow-up items

- Fresh independent review must reconstruct the manifest/components and repeat the
  actual isolated two-run subprocess, immutable replay, attacks, projection hash
  and inverse before master acceptance.
- After acceptance, the downstream rebuild packet may implement the currently
  absent rebuild entrypoint without editing these accepted control scripts.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

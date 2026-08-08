# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01-R2`
- objective: Correct both R1 critical review findings by replacing abbreviated
  R20 component claims with exact constructive predicates and replacing the
  launcher's shared child collector with an independent retained reconstruction.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R2.md`

## Summary

- Reconstructed the complete ordered Packaging compatible-tag selector, marker
  environment, eight-group marker/extra dependency traversal, parent edges and
  singular best compatible wheel for all 81 selected distributions.
- Proved exact lock/installed distribution equality, every installed RECORD
  declaration and generated INSTALLER/REQUESTED/self row, with bytecode paths
  rejected before target reads. Verified every selected cache association,
  complete extracted RECORD tree, declaration hash/size and PEP 427
  extracted-to-installed mapping.
- Constructed the exact 35-row executable authority: 33 direct entry-point
  wrappers, one pip interpreter-version alias and one Ruff wheel script; 21
  owners; exact groups/targets; four-tuple `python3` selection; 30 `python` and
  four `python3` wrappers; complete template-byte verification and distinct
  root-independent normalization. Installed RECORD stable identity now uses
  those verified normalized wrapper rows rather than root-bearing bytes.
- Verified the complete 748-row stdlib authority, all three exact interpreter
  alias chains, frozen interpreter/ABI/extension/libpython authority and a
  normal logical `uv --version` observation through the accepted one-hop link.
- Built the source-complete stable PYC map from every selected RECORD-owned
  source, repository-code source and `_virtualenv.py`, with the four exact
  optional source-absent orphan predicates. The launcher separately classifies
  complete actual site/repository PYC inventories, guard-reads every actual PYC,
  rejects a fifth source-absent orphan, and requires exact pre/post equality.
  Source-present non-stable test PYC rows remain operational denied evidence and
  do not enter stable identity.
- Closed the environment authority over every expected key/value plus the full
  required-absent roster.
- Removed the launcher admission-module loader entirely. The launcher does not
  import, execute or call child collector code; it separately reconstructs all
  twenty component values, evidence counts and repository digest from retained
  authorities. Executable and extracted component hashes are derived from full
  reconstructed detail, not retained digest literals.
- Expanded adversarial tests for shared-oracle substitution, source-level
  independence, environment closure, wrapper digest mutation, source-present
  denied/unchanged PYC and fifth source-absent orphan failure. Existing frame,
  immutable publisher, two-run admission, projection/inverse and no-rebuild
  behaviour remains green.

Final candidate SHA-256 values:

- admission child: `cd8a12da6b9db08c9041823c8b99fae782cf7ff99a72628970354a105c36ce67`
- launcher: `c56263cc5c4ba79a7dce5ba3ce3623def04b29933a5fdc8f0f0187d1aaf6332d`
- adversarial tests: `3ea58958683ff6d1e244925fc98a8cce77d89e34f2814a9b43f2003b656aac6a`
- reconstructed repository-code authority:
  `0b7f161a7a85eac0f60e1f204e2caab216f991e916ffcdf58de8caef39188f5f`
- local-resource component:
  `c62f263346fdb058c88e8bc48512fe976315c468b0c6a134ac9451a58e34f772`
- selected-lock-closure component:
  `71e19fea7a508cfe462c047775e494509813ce7612c16a98d46af57f254d8bfd`
- installed-record component:
  `d555808bed04421dcb3b1f3999cf290c36fae324ccb811143123db70b7a9d70b`
- executable component:
  `3378e7407967128fe37b8569f6e90ecb7b0a3762078fd6156f435f695f6debb3`
- extracted-runtime component:
  `e785af59b5e1d364535b7205b4707d75e767b5b66241ee1a52514a3c04e2805b`
- PYC source-map component:
  `78bb13f1a84114cb711d5c111ec48518370dc55687c463e3e1bd7be45eb2c5c8`
- exact evidence counts:
  `(1,1,1,35,81,81,1,1,17,1,1,1,81,1,1,748,1,1,5,81)`.

## Tests run

- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: three files already formatted.
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: success, no issues in three source files.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `166 passed in 71.34s`.
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no security findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks and zero failures; main branch and zero remotes.
- command: fresh child/launcher direct authority comparison under `uv run`
  - exit status: `0`
  - result: repository digest, all twenty components and all twenty counts equal.

## Artifacts/evidence

- exact implementation: `scripts/admit_wyscout_v5_runtime.py`,
  `scripts/launch_wyscout_v5.py`
- mutation, actual-subprocess, immutable replay and independence evidence:
  `tests/unit/test_w04_wyscout_runtime_control.py`
- producer return:
  `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R2.md`

## Risks

- The accepted same-trust-domain transient replacement residual remains; exact
  descriptor/path/inventory pre/post checks reject persistent or observed drift,
  but this local-only design is not a cryptographic prevention boundary.
- The reconstructed environment is deliberately frozen to the accepted macOS
  arm64 Python 3.12.12 / uv 0.9.21 authority. Host/runtime drift fails closed.
- The rebuild entrypoint remains downstream work and was not executed by this
  packet; the generic exact-argv executor and no-execution launch plan remain
  verified.

## Follow-up items

- Fresh independent R2 review must reconstruct the child and launcher vectors,
  rerun actual admission/idempotence and all mutation/security/local-only checks.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

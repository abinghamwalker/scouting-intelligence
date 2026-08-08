# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01-R6`
- objective: Close the real-invocation gap through the exact R20 outer argv while
  preserving R5/product authority, using only isolated producer evidence and no
  Git or real-root publication.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R6.md`

## Summary

- Made the direct-launch bootstrap the first executable source statement. It uses
  only resident built-in/frozen `sys`, `posix`, and `_io` capabilities plus
  embedded strict base64url, canonical-JSON, and pure SHA-256 implementations
  before installing the outer audit/open guard and allowing further imports.
- The bootstrap now proves the exact closed uv-transformed environment, complete
  34-field root-independent `w04-local-control-bootstrap-v4` tuple, admitted cwd
  and script argv projection, Python identity, three exact encoding sources and
  absent alternate cache candidates, master-opened launcher path/descriptor
  identity and bytes, zero descriptor offset, inheritable first state, exact
  inherited-FD census, and empty mode-0700 control prefix. It then retains the
  launcher descriptor noninheritable through both children and closes it once.
- Replaced the four-field preparation stand-in with independent launcher/child
  reconstruction of the complete v4 tuple. The actual child envelope consumes
  the retained launcher digest rather than reopening launcher bytes.
- Implemented the direct outer execution: snapshot complete stable plus PYC
  authority before UUID sampling; sample bounded distinct admission/rebuild
  UUIDv4s; derive the exact cwd-bound final/staging roots; perform admission,
  immutable code-manifest publication, and one rebuild; recheck stable/PYC,
  launcher, control, child-prefix, and staging identities; require all three
  runtime-pycache leaves empty; and emit one canonical
  `w04-local-control-completion-v1` value with the transport digest, receipt
  identity, and PYC health decomposition.
- Closed two post-product-state defects without cleanup: added only the exact
  packet-listed e2e/security test sources to both independent PYC maps, and made
  the child include mode `0o644` in present authorized-downstream repository rows
  to equal the retained launcher reconstruction.
- Added isolated positive/adversarial coverage for the actual eight-token uv
  bootstrap path, closed environment/tuple/argv mutation, missing/extra/offset
  descriptors, retained descriptor/control drift, cwd and UUID replay, fixed root
  derivation, child failure, whole-run PYC retention, and canonical completion.

## Tests run

- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `3 files already formatted`
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: `Success: no issues found in 3 source files`
- command: `uv run pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `237 passed in 1433.97s (0:23:53)`
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `uv run lint-imports`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks, zero failures

## Artifacts/evidence

- `scripts/admit_wyscout_v5_runtime.py`: SHA-256
  `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
- `scripts/launch_wyscout_v5.py`: SHA-256
  `ecfb3b1714b7a6caf607d9ae4393b3130e04045c717f5965207a804356b580f7`
- `tests/unit/test_w04_wyscout_runtime_control.py`: SHA-256
  `ad6027133eccb451fd9ab9d7135e60ccab50335d7acfdd25b008565bba323116`
- `orchestration/task_packets/W04-WYSCOUT-RUNTIME-CONTROL-01-R6.yaml`:
  SHA-256 `6a900a2232443006b62580a4f815e476c941181ca0ad1e0d83021603cade87a5`

## Risks

- Producer evidence intentionally does not write the admitted real roots. The
  exact uv process test proves the complete first-instruction/bootstrap path in
  an isolated root and then rejects its deliberately incomplete repository; the
  isolated full outer orchestration test proves prepare-to-rebuild sequencing and
  canonical completion with substituted child executors. The master-owned real
  two-run packet remains the sole authority for one unmocked real-root completion.
- The packet-wide uv commands required sandbox escalation only to read the already
  admitted local uv cache path. No network, dependency, lockfile, or provider
  change occurred.

## Follow-up items

- Independent R6 review, then master acceptance and the separately controlled
  one-real-root execution.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

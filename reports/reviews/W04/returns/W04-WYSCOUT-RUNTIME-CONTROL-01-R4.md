# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01-R4`
- objective: Correct the two bounded R3 findings by deriving external installed
  RECORD authority solely from complete PEP 427 mappings and independently
  closing actual PYC ownership/inventory in child and launcher, while preserving
  every green R3 predicate and the R20 child no-PYC-content-read boundary.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R4.md`

## Summary

- Both collectors now derive a complete operational destination map from every
  verified non-self extracted RECORD payload across wheel root and
  `.data/{purelib,platlib,scripts,headers,data}`. Each destination binds singular
  normalized owner, source RECORD path, scheme, mode, SHA-256 and size before any
  external installed row can be accepted.
- Separate child and launcher validators reconstruct every installed RECORD
  destination. They require canonical relative spelling, venv containment,
  singular ownership, mapped/installed owner and byte/mode equality, complete
  installed ownership for every extracted payload, and no collision, overwrite,
  alias or escape. The exact Bandit `../../../share/man/man1/bandit.1` data row
  and Greenlet `../../../include/site/python3.12/greenlet/greenlet.h` headers row
  pass only through this derivation. Exact controlled bin rows remain governed by
  the existing 35-row executable authority.
- Removed `OPERATIONAL_NON_STABLE_SOURCE_DENIED`. Both PYC collectors now reject
  every non-orphan PYC whose derived source is absent from the frozen source map,
  even when a same-named unmanifested `.py` exists.
- Froze the 43 already-present repository test sources that own retained pytest
  rewrite caches as explicit repository-code/source-map rows. This is an exact
  allowlist, not a scan-based promotion rule; a newly created source remains
  unmanifested and is rejected.
- Added a child-owned, independently implemented census of every site/repository
  PYC and `__pycache__` directory. It validates path/tag/source/orphan ownership
  and exact lstat kind/mode/link/size/identity/clock state, excludes `.venv` from
  repository traversal, and compares complete snapshots both within and across
  the two admission reconstructions immediately before result framing.
- Preserved R20 role separation: the child PYC census performs no PYC content
  open/read/hash. Launcher preflight independently retains no-follow content,
  magic, timestamp-mode, exact orphan hash/size and complete pre/post inventory
  checks. Operational child inventory rows remain excluded from stable identity.
- Added independent child/launcher attacks for unmanifested-source PYC, creation,
  deletion, content, header, mode and symlink drift, plus a source-level assertion
  that the child census contains no content-read primitive or launcher collector.
  Added positive Bandit/Greenlet fixtures and negative unmapped, owner-swapped,
  colliding and escaping external RECORD fixtures against both validators.

Final frozen SHA-256 values:

- admission child: `c91f98c8d02a647d1eada8636f864382c6c7468c2d9b9b61cff51db92ac3f94e`
- launcher: `5c4c081b5b5049de6f9aad444e95ccf2e4d38fa7484d56add67cd1cb03b193a0`
- runtime-control tests: `215d4c08af21e2768a98c16defa80c4bfefa44fb690dbe1fbc295cea254f0bad`
- reconstructed repository-code authority:
  `7325d7a4334a46883a5a9545a61d4348212badf3b0ad05e4a52df576b5833aa9`
- editable-root component:
  `2916dc972c89da7c7c5a2ea6b3ef6e45069ae91a1c72087cb522fb9238e55428`
- PYC source-map component:
  `093068f85a68421d176fcf3ab2fdf9bb122679c43048d0baa804c10a2aa56586`
- installed RECORD component:
  `73c9aaea089238ea3fef228d075ad0adce9c8697467fdebb7b6d24139cd010ca`
- extracted-runtime component:
  `e785af59b5e1d364535b7205b4707d75e767b5b66241ee1a52514a3c04e2805b`
- exact evidence counts:
  `(1,1,1,35,81,81,1,1,17,1,1,1,81,1,1,748,1,1,3,81)`

## Tests run

- command: `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: three files already formatted against final hashes.
- command: `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: all checks passed against final hashes.
- command: `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `0`
  - result: success, no issues in three source files against final hashes.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: complete final-hash population passed; collect-only confirmed exactly
    `191 tests`.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py::test_actual_admission_is_two_run_deterministic_idempotent_and_no_rebuild -vv`
  - exit status: `0`
  - result: `1 passed in 28.68s` against the final source hashes; both complete
    child/launcher authorities agreed, immutable replay was idempotent, projection
    and strict inverse passed, no rebuild ran and no real-root publication occurred.
- command: bounded R4 external-mapping/PYC attack slice
  - exit status: `0`
  - result: `14 passed, 42 deselected`.
- command: `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: three contracts kept, zero broken.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS, 25 checks and zero failures; main branch and zero remotes.
- command: fresh final-hash retained authority reconstruction
  - exit status: `0`
  - result: all twenty values/counts reconstructed; actual two-run admission
    independently established equality with the child.

## Artifacts/evidence

- exact admission implementation and lstat-only child PYC census:
  `scripts/admit_wyscout_v5_runtime.py`
- independent retained mapping, PYC content preflight and rebuild controls:
  `scripts/launch_wyscout_v5.py`
- positive/negative mapping and PYC drift evidence:
  `tests/unit/test_w04_wyscout_runtime_control.py`
- mandatory producer return:
  `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R4.md`

## Risks

- Authority remains deliberately frozen to the accepted current macOS arm64
  Python 3.12.12, uv 0.9.21, installation layout and retained operational PYC
  population. Drift fails closed.
- Child lstat snapshots detect creation, deletion, link, mode, size, identity and
  clock drift without violating zero content reads. Exact PYC content/magic/hash
  enforcement remains intentionally owned by independent launcher preflight.
- The downstream rebuild entrypoint remains absent, so the previously strengthened
  exact rebuild executor is not executed by this packet. Launch preparation still
  proves no rebuild occurs before immutable manifest readback and sole build-ID.
- Same-trust-domain transient replacement remains the accepted local residual;
  no-follow byte checks plus independent complete pre/post inventories reject
  persistent or observed drift but do not form a separate isolation boundary.

## Follow-up items

- Fresh independent R4 review must bind these final hashes, reproduce the exact
  Bandit/Greenlet mappings, attack every external-row and PYC mutation, rerun the
  complete 191-test final-hash gate and actual two-run admission, and confirm the
  child PYC census performs zero PYC content reads.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

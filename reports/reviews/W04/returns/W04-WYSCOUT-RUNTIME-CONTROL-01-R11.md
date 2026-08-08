# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01`
- revision: `R11`
- objective: Correct only the accepted-runtime local-resource roster from the
  superseded R20 ordered 17-resource subset to the effective R21 exact ordered
  30-resource authority in admission and launch.

## Files changed

- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/launch_wyscout_v5.py`
- `tests/unit/test_w04_wyscout_runtime_control.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R11.md`

## Summary

- Appended the exact R21 members 18 through 30 to both duplicated runtime
  resource tuples. Members 1 through 17 remain unchanged and in their original
  positions; admission and launcher now expose identical exact 30-member tuples.
- Changed only the local-resource component algorithm token in both runtime
  paths to `w04-local-resource-exact-30-v1`. The existing ordered-row
  construction, physical file/mode/hash/size checks, stable digest construction,
  authority validation, and fail-closed launch comparison remain unchanged.
- Froze the mechanically derived 30-row local-resource detail digest as
  `29d8a7cf4c4acab8a52d6008fc5f8975509cc445f5680e45e5974687e65c7bfb`
  and proved admission/launcher row, mode, digest, algorithm, and cardinality
  equality.
- Added direct adversarial coverage for omission, insertion, duplicate, reorder,
  both v1/v2 substitution directions, obsolete or drifted algorithm token, and
  row-content mutation. Each mutation diverges from the launcher's exact
  accepted component authority and is rejected by the existing strict component
  authority validator.
- Corrected the existing retained-resource cardinality assertion from the
  superseded 17-member count to the accepted exact 30-member count. No product,
  logical schema, root roster, serialization, inverse, build formula, digest
  meaning, retained evidence, or physical product byte changed.

## Tests run

- command: preliminary `uv run --locked --no-sync ruff format --check` over the
  four packet test/implementation paths
  - exit status: `1`
  - result: only the allowed runtime unit test required mechanical Ruff wrapping;
    Ruff formatting was applied to that allowed path and the repeated check passed
- command: focused `pytest -k r21_runtime_resource` on the runtime unit test
  - exit status: `0`
  - result: `10 passed, 113 deselected`
- command: first seven-check R11 producer gate
  - exit status: `130` after intentionally stopping only the producer's exact
    gate job
  - result: exposed one stale existing assertion expecting 17 resources; this was
    bounded rework, the assertion was corrected to 30, and focused regression
    proof then passed (`1 passed`)
- command: `uv run --locked --no-sync ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `4 files already formatted`
- command: `uv run --locked --no-sync ruff check --no-cache` over the same four
  paths
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run --locked --no-sync python -B -m mypy` over the same four paths
  - exit status: `0`
  - result: `Success: no issues found in 4 source files`
- command: `uv run --locked --no-sync python -B -m pytest -q -p no:cacheprovider tests/unit/test_w04_wyscout_runtime_control.py tests/security/test_w04_wyscout_vertical_slice_publication.py tests/contracts/test_w04_wyscout_build_contract.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/unit/test_w04_staged_product_publisher.py tests/contracts/test_w04_wyscout_v2_aggregates.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `403 passed in 1501.91s (0:25:01)`
- command: `uv run --locked --no-sync python -B -m bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py scripts/rebuild_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `uv run --locked --no-sync lint-imports --no-cache`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, all 25 checks, `main`, zero remotes

The final seven mandatory checks ran sequentially in retained exec session
`36015`, shell PID `53096`; pytest `uv` PID `53114`. Every Python-backed command
used `PYTHONDONTWRITEBYTECODE=1`, a `/tmp/w04-r11-producer-gate-pycache`
`PYTHONPYCACHEPREFIX`, and `python -B`; Ruff and mypy caches were disabled or
redirected under `/tmp`. The earlier bounded-rework gate was session `3835`,
shell PID `42962`, pytest `uv` PID `43018`, and only that exact producer-owned
gate job was stopped.

## Artifacts/evidence

- R11 task packet SHA-256:
  `dd047fbbe8ad9199dddcc23a6970ee351b9f0c6b62c3776cab2f0879a54d7804`
- Candidate SHA-256 values:
  - `scripts/admit_wyscout_v5_runtime.py`:
    `68cb2e96a8006ab7e529d614d037a18e4b0dbd982c0c3e119ef23319f66b78cc`
  - `scripts/launch_wyscout_v5.py`:
    `db77870605410ca16554b5ed869a6304c2b24b60122b21f1646b2d09c3dc2779`
  - `tests/unit/test_w04_wyscout_runtime_control.py`:
    `bd65a02b5dfa73e1f6bbf7d5e3bf32937c62233c9f12f07eeca4a9de65313332`
  - unchanged `tests/security/test_w04_wyscout_vertical_slice_publication.py`:
    `5907b945fa61855ff1104a2e03dd13057a76863251258b8a53088e322b44d18d`
- Governing/fixed bindings were exact before editing and remained exact after the
  final gate:
  - R21 design:
    `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`
  - R21 independent review:
    `262fbf6f4cc3f239daebb8db69059d46125415647d58ffb432b630c44353c3aa`
  - R21 master acceptance:
    `5a50b633e7ea4384fb65dd4008f8fb25da0cbf40d42b4408687315adde07b85f`
  - R10 runtime master acceptance:
    `1f7c09f15ea7ae8f3fbac9f517ad2e9b444b177da719751013eae5c2b867562a`
  - R10 runtime independent review:
    `331082c9482cabae5957e950e0b61683194138e979c6cff07eff06cf51ae80d6`
  - R10 producer return:
    `56004852a1868b89579d65ee781b5ef9a26b922451f25dbbe61f1b94aaa55854`
- Final gate helper `/tmp/w04-r11-producer-gate.zsh` SHA-256:
  `0fb02fb675479fc0cb3f43ce50eb6128d031e34570cb20add6ebcb51f7146241`
- Complete shell-only PYC census used frozen helper
  `/tmp/w04-r9-pyc-census.sh`, SHA-256
  `2702b38453c95e428e9289cfc0bd6a9d0f1a748aeb33f1bad1e1c7033eaf4a6d`:
  - site pre/post: 1,218 rows, byte-identical SHA-256
    `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`
  - repository pre/post: 132 rows, byte-identical SHA-256
    `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`
- Complete retained `data/**` and `runs/**` shell census used
  `/tmp/w04-r11-retained-census.sh`, SHA-256
  `d14125f29a98e2689bf415daa41ff0fbc3250963531230977b7ed1aa32e26f17`:
  pre/post 272 rows, byte-identical SHA-256
  `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c`.

## Risks

- Fresh independent R11 review and master acceptance remain required before this
  bounded runtime correction is accepted.
- A later accepted repository-code manifest, build ID, products, manifests, and
  receipts may change only as mechanical consequences of the corrected governed
  source bytes. This producer packet intentionally performed no real-root run,
  derivation, cleanup, checkpoint, publication, or Git operation.

## Follow-up items

- Fresh independent R11 review and master acceptance; no producer-side follow-up.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed; only `/tmp` gate/cache/census
  evidence was created outside the repository, without altering retained data,
  runs, manifests, staging, products, dependencies, or PYC bytes

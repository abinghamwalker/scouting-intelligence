# Subagent return

## Task

- task_id: `W04-WYSCOUT-RUNTIME-CONTROL-01`
- revision: `R10`
- objective: Reconstruct only the two declared tuple fields from their canonical
  rebuild-child JSON arrays before strict `RebuildInvocation` validation, without
  changing any logical value, inverse, product, or digest formula.

## Files changed

- `scripts/rebuild_wyscout_v5.py`
- `tests/security/test_w04_wyscout_vertical_slice_publication.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-RUNTIME-CONTROL-01-R10.md`

## Summary

- Added one pure rebuild-invocation JSON boundary with the exact ordered 25-key
  roster. It rejects every non-object and any missing, extra, or reordered key.
- Requires `authority_rows` and `dependency_rows` to be exact JSON `list`
  instances. It constructs a new ordered object in which only those two arrays
  become tuples; all nested elements and the other 23 values are retained
  without coercion, filtering, sorting, defaulting, or copying.
- The rebuild child now passes that reconstructed object directly to
  `RebuildInvocation.model_validate(..., strict=True)`. Every existing exact
  five-row authority/dependency predicate, inverse, projection hash, build ID,
  clock, digest, and model validator remains the sole semantic authority.
- Added an exact canonical JSON round-trip proof: the accepted invocation decodes
  with arrays, reconstructs to tuples, validates strictly, reproduces both
  projection inverses exactly, and preserves the canonical logical JSON bytes.
- Added direct rejection proofs for a tuple already present at the JSON boundary;
  missing, extra, and reordered invocation keys; four non-array tuple-field
  cases; authority/dependency order, cardinality, and value drift; nested extra
  and mistyped fields; and a mistyped top-level model field.
- Retained the accepted admission child, launcher, R9 runtime tests, disclosed
  operational PYC, unaccepted admitted code manifest, all data/runs/staging
  evidence, dependencies, lock state, product population, physical products, and
  digest meaning/formula byte-for-byte. No real-root retry was performed.

## Tests run

- command: preliminary `uv run --locked --no-sync ruff format --check scripts/rebuild_wyscout_v5.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `1`
  - result: one allowed test file required mechanical Ruff formatting; Ruff
    formatting was applied only to the two allowed implementation paths
- command: preliminary `uv run --locked --no-sync python -B -m mypy scripts/rebuild_wyscout_v5.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `1`
  - result: the newly precise invocation return type exposed one obsolete ignore
    and existing heterogeneous-fixture inference; annotations/casts were corrected
    only in the allowed security test without changing test behavior
- command: focused `uv run --locked --no-sync python -B -m pytest -q -p no:cacheprovider tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `31 passed in 1.15s`
- command: `uv run --locked --no-sync ruff format --check scripts/rebuild_wyscout_v5.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run --locked --no-sync ruff check --no-cache scripts/rebuild_wyscout_v5.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run --locked --no-sync python -B -m mypy --cache-dir=/tmp/w04-r10-final-mypy scripts/rebuild_wyscout_v5.py tests/security/test_w04_wyscout_vertical_slice_publication.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run --locked --no-sync python -B -m pytest -q -p no:cacheprovider tests/security/test_w04_wyscout_vertical_slice_publication.py tests/contracts/test_w04_wyscout_build_contract.py tests/unit/test_w04_wyscout_runtime_control.py tests/e2e/test_w04_wyscout_vertical_slice.py tests/unit/test_w04_staged_product_publisher.py tests/contracts/test_w04_wyscout_v2_aggregates.py`
  - exit status: `0`
  - result: `286 passed in 1493.76s (0:24:53)`
- command: `uv run --locked --no-sync python -B -m bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py scripts/rebuild_wyscout_v5.py`
  - exit status: `0`
  - result: no findings
- command: `uv run --locked --no-sync lint-imports --no-cache`
  - exit status: `0`
  - result: `3 kept, 0 broken`
- command: `uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks, zero failures

The seven mandatory acceptance checks ran sequentially in retained exec session
`75016`, shell PID `21627`; pytest PID `21654`. Every Python-backed command used
`PYTHONDONTWRITEBYTECODE=1`, a `/tmp/w04-r10-...`
`PYTHONPYCACHEPREFIX`, and `python -B`. Tool caches were disabled or redirected
under `/tmp`.

## Artifacts/evidence

- R10 packet SHA-256:
  `d6c0872b86928dc1a53ed0476f26be7ae9ace500bdaae3e25c8a535e5356748f`
- `scripts/rebuild_wyscout_v5.py` SHA-256:
  `fff279d4d4a6a1c76ea6ee2cc9c7a88a4d5fd2c56ca677984a1dcce765ef9339`
- `tests/security/test_w04_wyscout_vertical_slice_publication.py` SHA-256:
  `5907b945fa61855ff1104a2e03dd13057a76863251258b8a53088e322b44d18d`
- Retained fixed bindings remained exact:
  - admission child: `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
  - launcher: `6211ff1cd0b51bdd3ab24fe26358077f46f1ad0526ff60126776606ca01243eb`
  - R9 runtime tests: `12924b9905a8334c4a6f83bb00b170059be0bb965a1d3d6b4f0c09d364a95abf`
  - disclosed launcher PYC: `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e`
  - retained unaccepted code manifest:
    `fb1bcca5772d71a0de2c116cd2539d1d2cd757554df8791dad8e0d952cf67083`
- Complete retained `data/**` and `runs/**` shell census:
  - helper `/tmp/w04-r10-retained-census.sh`, SHA-256
    `03013802f0af3c79fbccd9861ad65bfa9c4588f389a78ddbab365a642b8ecdcf`
  - `/tmp/w04-r10-retained-pre.tsv` and
    `/tmp/w04-r10-retained-post.tsv`: 81 rows, byte-identical SHA-256
    `e62878d96c76cc67a0fc0690fed674c1c61c2b82981a472b21649ffd981a686b`
- Complete shell-only PYC census used the frozen helper
  `/tmp/w04-r9-pyc-census.sh`, SHA-256
  `2702b38453c95e428e9289cfc0bd6a9d0f1a748aeb33f1bad1e1c7033eaf4a6d`:
  - site pre/post: 1,087 files plus 131 directories, 1,218 rows,
    byte-identical SHA-256
    `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`
  - repository pre/post: 111 files plus 21 directories, 132 rows,
    byte-identical SHA-256
    `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`

## Risks

- Fresh independent R10 review and master acceptance remain required before the
  master may decide whether to perform a later real-root retry.
- A future accepted repository-code manifest and build ID will mechanically
  change when they are derived from the corrected rebuild-child source. This
  packet intentionally preserved the retained unaccepted manifest and performed
  no derivation, cleanup, publication, or retry.

## Follow-up items

- Fresh independent R10 review and master acceptance; no producer-side follow-up.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed; `/tmp` read-only census evidence
  was created without altering repository, data, runs, manifests, staging, or PYC
  bytes

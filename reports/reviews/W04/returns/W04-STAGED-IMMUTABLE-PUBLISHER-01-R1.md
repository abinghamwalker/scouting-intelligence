# Subagent return

## Task

- task_id: `W04-STAGED-IMMUTABLE-PUBLISHER-01-R1`
- objective: Implement the R20 sidecar-free, staged, immutable local publisher with
  adversarial temporary-root tests and no real product write.

## Files changed

- `src/scouting/storage/wyscout_publication.py`
- `tests/unit/test_w04_staged_product_publisher.py`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-01-R1.md`

## Summary

- Added one standalone `WyscoutStagedPublisher`; it neither imports nor wraps
  `GuardedStorage.write_bytes` and creates no digest or completion sidecar.
- The constructor accepts a closed mapping of canonical root names to distinct,
  absolute, pre-existing final/staging roots. It descriptor-walks every absolute
  component without following links, fixes each root identity, requires exact
  `0700` root mode and one filesystem, and rejects aliases or undeclared roots.
- Publication tails are bounded normalized POSIX paths. Absolute, empty, dot,
  dot-dot, duplicate-separator, backslash, NUL, over-depth, over-length,
  non-canonical, and final `.partial` paths fail before a product write.
- Nested directories are created descriptor-relatively at `0700`. The exact staged
  name is the final basename plus `.partial`; its file is created once at `0600`,
  written completely, file/directory-fsynced, closed, reopened no-follow, compared
  to its original device/inode/mode/link/size state, and passed as immutable bytes
  to the caller validator.
- The final code/environment/resource callback must succeed with exact `None`.
  Staged bytes and the named staging/final parent identities are re-opened and
  rechecked immediately before promotion.
- Promotion is same-filesystem `os.link` with source/destination directory
  descriptors and no replacement. A target appearance is a race, never an equal
  replay shortcut. After link, both names and bytes must identify the validated
  inode with link count two; the final directory is fsynced, the staged name is
  unlinked, the staging directory is fsynced, and a fresh named-root no-follow
  readback must prove the final has link count one and the exact physical digest.
- A pre-existing final is idempotent only when it is a regular `0600`, one-link,
  exact-byte file and it passes validation, final recheck and fresh named-path
  readback. Unequal bytes, unsafe mode/link/type, link/source/parent races and
  cross-device promotion fail closed without replacement.
- Failures before successful staged-name unlink retain the serializer-owned staged
  evidence. The implementation never calls `chmod`, never repairs attacker-owned
  objects, and returns only a frozen result containing root, relative path, exact
  byte count, physical SHA-256 and created/replayed state.
- The temporary-root suite covers exact replay, unequal final, staged/final
  symlink/hardlink/FIFO/directory attacks, path/root traversal and aliases, exact
  permissions, partial writes, validator/recheck/falsey-result failures, file and
  directory fsync failures, no-follow reopen failure, mode/link mutation, target
  link race, cross-device simulation, nested symlink escape, parent/root identity
  replacement, unlink failure evidence, callback order and final link/readback.

Candidate bindings:

```text
corrected packet = 99921ecc50e6a60bd5a482473cc1cdb051c0aced025f278decbff48e8a26d5fe
publisher = a43126421f1576abc5c142fe53d9ac0bfd397d06a34be0b101f9802f986fde9d
tests = 23e35833c7765e7c782ef55052bcc25b93fea57d693ce99b535560fe7ffa5c8e
```

Every fixed packet binding was reproduced before editing and again after the
master corrected only the nonexistent acceptance-test path:

```text
complete repository gate = 22b0b73078d4d2f0cc7e5eed3920a5401fd3d0e02d9ee3c66d9c7af02f76f469
R4 audit                 = a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222
R20                      = 8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047
R21                      = faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020
GuardedStorage           = 62a026560c4821d123d42afcd3438be18572ec0fef03f1747a0cbcfa97f030ef
Parquet encoder          = bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4
```

## Tests run

- command: `shasum -a 256` over all six fixed bindings
  - exit status: `0`
  - result: every value matched before editing and after the packet correction.
- command: `uv run ruff format --check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - bounded-iteration exit status: `1`; one import-order finding was corrected.
  - final exit status: `0`; `All checks passed!`.
- command: `uv run mypy src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`.
- command: `uv run pytest -q tests/unit/test_w04_staged_product_publisher.py`
  - bounded-iteration exit status: `1`; `8 failed, 40 passed`, all confined to the
    test setup directory helper and corrected without weakening assertions.
  - intermediate exit status: `0`; `48 passed in 0.19s`.
  - final exit status: `0`; `50 passed in 0.24s` after parent-rename/path-binding
    coverage was added.
- command: `uv run pytest -q tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `131 passed in 2.11s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, zero failures, all 25 checks passed.
- command: `uv run bandit -q -r src/scouting/storage/wyscout_publication.py`
  - first sandboxed exit status: `2`; the sandbox denied read-only access to the
    existing external uv cache before the scan or repository code ran.
  - approved read-only rerun exit status: `0`; no Bandit finding.
- command: `find data/working/wyscout/v5 -name '*.partial' -print`
  - exit status: `0`
  - result: no real staged partial exists.
- command: locked `uv run python -B` census for real Bronze/Silver/Gold,
  layer-manifest and `runs/w04/wyscout-rebuild` roots
  - first sandboxed exit status: `2`; the external uv-cache read was denied before
    code execution.
  - approved read-only rerun exit status: `0`
  - result: `present_real_product_roots: []`.

## Artifacts/evidence

- `src/scouting/storage/wyscout_publication.py`
  - SHA-256:
    `a43126421f1576abc5c142fe53d9ac0bfd397d06a34be0b101f9802f986fde9d`
- `tests/unit/test_w04_staged_product_publisher.py`
  - SHA-256:
    `23e35833c7765e7c782ef55052bcc25b93fea57d693ce99b535560fe7ffa5c8e`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-01-R1.md`

## Risks

- This is deliberately POSIX-only: no-replace publication depends on hard-link
  semantics and fails closed with `PublicationCrossDeviceError` across filesystems.
- If an error occurs after the final link is created but before staged-name unlink,
  both names are retained with link count two for investigation; no success result
  is returned. Downstream code must treat any raised exception as unpublished.
- The module is intentionally not re-exported through
  `src/scouting/storage/__init__.py`, which was forbidden. Downstream accepted code
  must import the additive module directly until the master separately owns any
  integration surface.
- Independent review and master reproduction remain mandatory; this return is not
  acceptance and grants no real product publication.

## Follow-up items

- Dispatch the bounded independent publisher review named by the accepted audit;
  fix both candidate hashes above and reproduce every adversarial path, race,
  failure-evidence, mode/link and readback case before master acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no edits to `GuardedStorage`, formats, `__init__`, contracts, authority, data,
  orchestration or dependency files: confirmed
- no real product, manifest, run, provider, network, cloud, container, CI,
  deployment or public-endpoint action: confirmed

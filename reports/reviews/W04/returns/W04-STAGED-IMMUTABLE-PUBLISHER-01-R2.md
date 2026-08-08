# Subagent return

## Task

- task_id: `W04-STAGED-IMMUTABLE-PUBLISHER-01-R2`
- objective: Close the R1 publisher to the exact three W04 root names and add
  executable evidence for both uncovered post-link fsync failure boundaries.

## Files changed

- `src/scouting/storage/wyscout_publication.py`
- `tests/unit/test_w04_staged_product_publisher.py`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-01-R2.md`

## Summary

- Replaced the generic root-name regular expression with the closed literal set
  `wyscout-working`, `wyscout-manifests`, and `w04-rebuild-runs`.
- The constructor accepts any non-empty subset of only those names. Runtime root
  selection also rejects any other string or type before parsing a tail, opening a
  publication parent, or writing a directory/file.
- Updated every positive publisher test to use `wyscout-working`. Added a
  three-root temporary-mirror test that declares and successfully publishes once
  through each exact name.
- Added fail-before-write coverage for `silver`, `bronze`, `gold`, `manifests`,
  `runs`, canonical-looking/arbitrary aliases, the empty string and representative
  non-string values. No test hard-codes a real repository root.
- Added targeted final-parent fsync injection after hard-link creation. The call
  raises without a result; final and staged names retain the exact validated inode,
  bytes, `0600` mode and link count two, while unrelated pre-existing final evidence
  remains byte- and inode-identical.
- Added targeted staging-parent fsync injection after staged-name unlink. The call
  raises without a result; the staged name is absent, the final retains the exact
  bytes at `0600` with link count one, and unrelated pre-existing final evidence is
  unchanged.
- Preserved all other R1 validation, no-follow traversal, staged evidence,
  no-replace linking, replay, mode, race, cross-device and guarded-readback behavior.

Bindings:

```text
R2 packet = bab41bf6e8d7e9b01c2820f3f288ae92559d30cd4d8f0d3d290119afe0ed1a50
R2 publisher = 9805dbad85cdcf7c49c50634e31eefda4c1eef7b3f22cc0d969e98f93b0c3a6f
R2 tests = d509b04df48c9dfbeb6661e5bab9e32dd74ce9c8d2243b70b77f5a52b95681e5
```

Every R2 fixed binding matched before editing, including the exact R1 packet,
publisher, test and return hashes and all frozen R20/R21/R4/storage/encoder inputs.

## Tests run

- command: `shasum -a 256` over the R2 packet and all ten fixed bindings
  - exit status: `0`
  - result: all expected values matched before editing.
- command: `uv run ruff format --check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `uv run mypy src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`.
- command: `uv run pytest -q tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `66 passed in 0.22s`.
- command: `uv run pytest -q tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `147 passed in 2.19s`.
- command: `uv run bandit -q -r src/scouting/storage/wyscout_publication.py`
  - exit status: `0`
  - result: no Bandit finding.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, zero failures and all 25 checks passed.
- command: `find data/working/wyscout/v5 -name '*.partial' -print`
  - exit status: `0`
  - result: no real staged partial exists.
- command: locked `uv run python -B` census for real Bronze/Silver/Gold,
  layer-manifest and `runs/w04/wyscout-rebuild` roots
  - exit status: `0`
  - result: `present_real_product_roots: []`.

## Artifacts/evidence

- `src/scouting/storage/wyscout_publication.py`
  - SHA-256:
    `9805dbad85cdcf7c49c50634e31eefda4c1eef7b3f22cc0d969e98f93b0c3a6f`
- `tests/unit/test_w04_staged_product_publisher.py`
  - SHA-256:
    `d509b04df48c9dfbeb6661e5bab9e32dd74ce9c8d2243b70b77f5a52b95681e5`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-01-R2.md`

## Risks

- Post-link final-parent fsync failure deliberately retains two names/link count two
  as failed evidence. Post-unlink staging-parent fsync failure necessarily retains
  only the one-link final name. Both states raise and must be treated as unpublished
  pending investigation.
- This remains a POSIX same-filesystem primitive. Downstream wiring, real root
  creation and product publication are outside this packet and remain gated.
- Independent review and master reproduction remain mandatory; this return is not
  acceptance.

## Follow-up items

- Obtain fresh independent R2 publisher review fixing the two candidate hashes and
  reproducing root closure plus both exact post-link evidence states.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no edit to the R1 return, GuardedStorage, formats, `__init__`, contracts,
  authorities, data, orchestration or dependencies: confirmed
- no real product, sidecar, provider, network, cloud, container, CI, deployment or
  public-endpoint action: confirmed

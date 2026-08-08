# Subagent return

## Task

- task_id: `W04-STAGED-IMMUTABLE-PUBLISHER-01-R3`
- objective: Correct the equal-final replay staged-appearance race with one final
  identity-bound no-follow absence checkpoint and adversarial tests.

## Files changed

- `src/scouting/storage/wyscout_publication.py`
- `tests/unit/test_w04_staged_product_publisher.py`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-01-R3.md`

## Summary

- In the existing equal-final replay branch, after the caller validator, final
  code/environment/resource recheck and fresh immutable-final readback, the
  publisher now reopens the originally fixed staging root and exact named staging
  parent descriptor-relatively without following links.
- Replay success is returned only when the exact serializer-owned `.partial` name
  is still absent and the reopened parent has the originally observed device/inode.
- A newly appeared safe regular staged file raises `PublicationRaceError`.
  Symlink, hardlink, FIFO, directory, unsafe mode/link count and other nonregular
  states raise `PublicationPathSecurityError`. A disappeared or replaced staging
  parent raises `PublicationRaceError`. Nothing is unlinked, chmodded, repaired,
  replaced or reinterpreted on any of those paths.
- Added an isolated regular-file replay reproduction proving no result, unchanged
  final identity/bytes and retained raced staged bytes.
- Added parameterized replay coverage for symlink, two-link hardlink, FIFO,
  directory and unsafe-mode evidence, with exact retained-state assertions.
- Added disappeared-parent and same-path replacement-parent replay cases. Both
  retain the immutable final and the raced evidence in the moved original parent.
- Preserved the exact three-name root vocabulary, both post-link fsync evidence
  boundaries and every R1/R2 path, mode, link, no-follow, replay, race,
  no-sidecar/no-replace and guarded-readback behavior.

Bindings:

```text
R3 packet = 8253d13832db1eb0fdb4d8cedb7829768524ebe9028ed2964591ec53068fa2cf
R3 publisher = 01b56c0400af0a4fba1adbf06b53b4e94a8571be66c7e0770ca6d72b4c740c13
R3 tests = 639503018a5528ad8463d21e68fbfd0133e09c9884838a2422daf911173f709e
```

Every R3 fixed binding matched before editing, including the exact R2 packet,
publisher, tests and return; the failed independent review and reviewer return; and
all frozen R20/R21/R4/storage/encoder inputs. Failed-review evidence was not edited.

## Tests run

- command: `shasum -a 256` over the R3 packet and all twelve fixed bindings
  - exit status: `0`
  - result: every expected value matched before editing.
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
  - result: `74 passed in 0.26s`.
- command: `uv run pytest -q tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `155 passed in 2.17s`.
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
    `01b56c0400af0a4fba1adbf06b53b4e94a8571be66c7e0770ca6d72b4c740c13`
- `tests/unit/test_w04_staged_product_publisher.py`
  - SHA-256:
    `639503018a5528ad8463d21e68fbfd0133e09c9884838a2422daf911173f709e`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-01-R3.md`

## Risks

- Accepted same-trust-domain residual: a staged name that appears and disappears
  entirely between filesystem checkpoints cannot be cryptographically excluded.
  An artifact present at the final identity-bound checkpoint is never reported as
  replay success.
- This remains a POSIX same-filesystem primitive. Downstream wiring and any real
  product publication remain separately gated.
- Independent review and master reproduction remain mandatory; this return is not
  acceptance.

## Follow-up items

- Obtain a fresh independent R3 publisher review fixing the two candidate hashes
  and independently reproducing every final-checkpoint staged/parent race.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no edit to failed review evidence, R1/R2 returns, GuardedStorage, formats,
  `__init__`, contracts, authorities, data, orchestration or dependencies: confirmed
- no real product, sidecar, provider, network, cloud, container, CI, deployment or
  public-endpoint action: confirmed

# Subagent return

## Task

- task_id: `W04-STAGED-IMMUTABLE-PUBLISHER-REVIEW-01-R2`
- objective: Independently review the R3 staged immutable publisher correction,
  reproduce the failed R1 replay race and every R3 final-checkpoint adversary, and
  return PASS only with no P0/P1/P2 findings.

## Files changed

- `reports/reviews/W04/wyscout-staged-product-publisher-independent-review-R2.md`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-REVIEW-01-R2.md`

## Summary

- Recommendation: `PASS`.
- Finding counts: `P0=0`, `P1=0`, `P2=0`.
- All fourteen packet-fixed candidate, failed-review, authority, storage, encoder
  and prior-gate bindings matched exactly before analysis. Candidate and failed R1
  evidence hashes remained unchanged after review.
- The exact failed R1 equal-final race was independently reproduced against R3.
  R3 returned no result, raised `PublicationRaceError`, preserved the immutable
  final and retained the newly appeared exact `.partial` evidence.
- Independent final-checkpoint attacks for a regular file, symlink, hardlink,
  FIFO, directory, unsafe mode, disappeared parent and same-path replacement
  parent all raised the required race/security class without repair or evidence
  loss.
- Exact three-root closure and both post-link fsync evidence states were also
  independently reproduced. Full static, type, test, security and local-only
  checks passed; pre/post bytecode inventories were identical.
- The exact accepted residual remains: a same-trust-domain staged name appearing
  and disappearing wholly between checkpoints is not cryptographically excluded.
  Any artifact present at the final checkpoint is never success.

## Tests run

- command: `shasum -a 256` over the R2 review packet and all fourteen fixed
  bindings
  - exit status: `0`
  - result: every expected digest reproduced exactly.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync mypy src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q -p no:cacheprovider tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `155 passed in 2.16s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync bandit -q -r src/scouting/storage/wyscout_publication.py`
  - exit status: `0`
  - result: no Bandit finding.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, zero failures and all 25 checks passed.
- command: independent locked/no-sync R1-race plus eight-state final-checkpoint
  probe in `/private/tmp/w04-publisher-r2-review-lzbuqugu`
  - first sandboxed exit status: `2`; existing external uv-cache read was denied
    before Python or repository code ran.
  - approved read-only rerun exit status: `0`
  - result: `R1_RACE_AND_R3_FINAL_CHECKPOINTS_PASS`; every state failed closed
    with exact final and raced-evidence assertions.
- command: independent locked/no-sync three-root vocabulary and two-boundary fsync
  probe in `/private/tmp/w04-publisher-r2-boundaries-myyfyhod`
  - exit status: `0`
  - result: `ROOT_VOCABULARY_AND_POST_LINK_FSYNC_PASS`.
- command: read-only preflight/postflight site and repository pyc path/content and
  path/mode/link/size inventories
  - exit status: `0`
  - result: site count `1086`, repository count `86`; every pre/post digest was
    identical, as recorded in the review.
- command: real W04 `.partial` and Bronze/Silver/Gold/staging/manifest/run-root
  absence checks
  - exit status: `0`
  - result: no real partial or product/control root exists.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-staged-product-publisher-independent-review-R2.md`
  - SHA-256:
    `77516478c9dd386f0e44179c1cf8219fd925f26b0460a73c771fb4f5e409d1c5`
- retained R3 adversary evidence:
  `/private/tmp/w04-publisher-r2-review-lzbuqugu`
- retained R2 root/fsync evidence:
  `/private/tmp/w04-publisher-r2-boundaries-myyfyhod`

## Risks

- Accepted same-trust-domain residual: a staged name that appears and disappears
  entirely between checkpoints cannot be cryptographically excluded. Eliminating
  it requires a different execution primitive/trust boundary outside this packet.
- This remains a POSIX same-filesystem primitive. Downstream wiring and any real
  product publication remain separately gated.
- This PASS is independent evidence, not self-approval; master readback,
  reproduction and acceptance remain mandatory.

## Follow-up items

- Master independently read back this review and return, reproduce the bounded
  evidence and accept or return rework before downstream product publication.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation, test, GuardedStorage, encoder, product, data, authority,
  orchestration or verification edit: confirmed
- no real product/partial path, provider/network, cloud, container, hosted CI,
  endpoint, deployment or public action: confirmed
- no delegation or self-approval: confirmed

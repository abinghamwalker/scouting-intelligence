# Subagent return

## Task

- task_id: `W04-STAGED-IMMUTABLE-PUBLISHER-REVIEW-01-R1`
- objective: Independently review the corrected R2 staged immutable publisher
  against the frozen W04 sidecar-free/no-replace contract and adversarial failure
  states.

## Files changed

- `reports/reviews/W04/wyscout-staged-product-publisher-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-STAGED-IMMUTABLE-PUBLISHER-REVIEW-01-R1.md`

## Summary

- Recommendation: `REWORK`.
- Finding counts: `P0=0`, `P1=1`, `P2=0`.
- Every review-packet and fixed candidate/authority hash matched before analysis.
- Independent reproduction found that the equal-final replay branch returns
  `created=False` success when the exact serializer-owned `.partial` appears during
  `final_recheck`. The final remains exact, but the newly appeared `0600` staged
  evidence also remains, so a filesystem race is reported as successful publication.
- The bounded correction is a final fresh no-follow absence check of the exact staged
  name, bound to the fixed staging root/parent, before equal-final replay success,
  plus focused adversarial coverage. No architecture or product expansion is needed.
- All other reviewed surfaces passed: exact three-name root closure, aliases and
  non-string rejection before write, path/mode/link/nonregular coverage, both exact
  post-link fsync failure states, no sidecars/repair/replacement, frozen storage and
  encoder bytes, local-only controls and absence of real product outputs.

## Tests run

- command: `shasum -a 256` over the review packet and all twelve fixed bindings
  - exit status: `0`
  - result: every expected digest reproduced exactly.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - first sandboxed exit status: `2`; external uv-cache access was denied before the
    tool ran.
  - approved read-only rerun exit status: `0`
  - result: `2 files already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - first sandboxed exit status: `2`; external uv-cache access was denied before the
    tool ran.
  - approved read-only rerun exit status: `0`
  - result: `All checks passed!`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync mypy src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py`
  - first sandboxed exit status: `2`; external uv-cache access was denied before the
    tool ran.
  - approved read-only rerun exit status: `0`
  - result: `Success: no issues found in 2 source files`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q -p no:cacheprovider tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit status: `0`
  - result: `147 passed in 2.13s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync bandit -q -r src/scouting/storage/wyscout_publication.py`
  - first sandboxed exit status: `2`; external uv-cache access was denied before the
    tool ran.
  - approved read-only rerun exit status: `0`
  - result: no Bandit finding.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python scripts/verify_local_only.py`
  - first sandboxed exit status: `2`; external uv-cache access was denied before the
    script ran.
  - approved read-only rerun exit status: `0`
  - result: `PASS`, zero failures and all 25 checks passed.
- command: independent isolated equal-final staged-appearance race probe through
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c ...`
  - exit status: `0`
  - result: `outcome=returned_success`, `result_created=false`,
    `staged_exists=true`, `staged_mode=0o600`, `final_unchanged=true`; P1 reproduced.
- command: independent isolated constructor/selection vocabulary probe through
  locked/no-sync uv Python
  - exit status: `0`
  - result: all three exact roots admitted; 13/13 constructor and 13/13 selection
    aliases/non-strings rejected; `no_write=true`.
- command: independent isolated post-link fsync boundary probe through locked/no-sync
  uv Python
  - exit status: `0`
  - result: final-parent failure retained the exact two-link staged/final inode;
    staging-parent failure retained the exact one-link final with staged absent;
    both raised and preserved unrelated evidence.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-staged-product-publisher-independent-review-R1.md`
  - SHA-256:
    `6e574fde38eefba002db7568596f10346beb7d6e16c7149bdda2af6cb402a7d3`
- Finding:
  `W04-PUBLISHER-R2-P1-REPLAY-STAGED-APPEARANCE-RACE`

## Risks

- Until corrected, an equal-final replay can report success while a newly appeared
  serializer-owned staged artifact remains. Downstream code could treat an ambiguous
  failed/raced state as accepted immutable publication.
- No other P0, P1 or P2 finding was identified in the bounded review.

## Follow-up items

- Issue one bounded publisher correction for the replay staged-name recheck and its
  adversarial test, then obtain a fresh independent review before downstream product
  publication.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation, test, GuardedStorage, encoder, product, data, authority,
  orchestration or verification edit: confirmed
- no real product/partial path, provider/network, cloud, container, hosted CI,
  endpoint, deployment or public action: confirmed
- no delegation or self-approval: confirmed

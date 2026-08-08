# Subagent return

## Task

- task_id: `W04-IDENTITY-BUNDLE-RUNTIME-REVIEW-01-R1`
- objective: Independently reproduce and critically review the exact source-complete
  W04 identity queue/bundle candidate, its additive namespace binding, recursive
  readback and fail-closed local persistence.
- disposition: `REWORK`; review chain invalidated before a final merits `PASS`.

## Files changed

- `reports/reviews/W04/wyscout-identity-bundle-runtime-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-IDENTITY-BUNDLE-RUNTIME-REVIEW-01-R1.md`

## Summary

- Candidate hashes, artifact addresses, sizes and `0600` modes were exact before
  review and remained exact afterward.
- Independent source recomputation plus exact-address recursive loading exited `0`
  and reproduced `5,594` rows, the exact state counts, `23`-to-`15` queue
  aggregation, `226,041` zero references, both content addresses, dependency UUID,
  five target identity vectors, and the target `[82,83)` right-censored formation
  evidence.
- Namespace/preimage, strict integer, canonical ordering, recursive equality,
  immutable persistence and adversarial acceptance probes passed.
- Inventory enumeration is reject-only exact-set validation. It never selects,
  discovers or returns an authority address, so no implementation selection-scan
  defect was found.
- Finding counts: `P0=0`, `P1=1`, `P2=0`.
- P1 `REVIEW_REPOSITORY_PYC_INVENTORY_DRIFT`: repository pyc count stayed `76`,
  but full byte and metadata inventory digests changed between preflight and
  postflight. R20 Section 8.6.5 invalidates the review regardless of whether the
  concurrent mutation touched candidate files. No cleanup or repair was attempted.

## Tests run

- command: fixed `shasum -a 256` plus artifact `stat` checks
  - exit status: `0`
  - result: every packet binding exact; queue `17,412` bytes and bundle
    `91,420,676` bytes, both regular `0600` files.
- command: complete read-only site/repository pyc preflight and source-based
  classifier
  - exit status: `0`
  - result: site `1,086` and repository `76`; zero unsafe/unclassified files.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q
  tests/contracts/test_w04_wyscout_identity_bundle.py
  tests/unit/test_wyscout_identity.py
  tests/contracts/test_w04_identity_ruleset_authority.py`
  - exit status: `0`
  - result: `79 passed in 24.62s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 controls.
- command: locked/no-sync `python -B` source recomputation followed by
  `load_initial_identity_bundle` at the exact derived digest
  - exit status: `0`
  - result: complete equality and all population/target/formation assertions passed.
- command: complete read-only site/repository pyc postflight
  - exit status: `0`
  - result: predicate failed; site unchanged, repository byte digest changed
    `14cbf20f... -> 414cae97...` and metadata digest changed
    `1f37e9d2... -> 5c050708...` at unchanged count `76`.
- command: final candidate/artifact hash, size and mode recheck
  - exit status: `0`
  - result: frozen identity candidate and artifacts remained exact.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/wyscout-identity-bundle-runtime-independent-review-R1.md`
- queue SHA-256:
  `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51`
- bundle SHA-256:
  `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`
- identity dependency UUID: `31638732-5b25-57db-9eb4-8e943a47a387`

## Risks

- No candidate implementation P0-P2 finding was established, but the invalidated
  no-write chain means that observation cannot be promoted to acceptance.
- Running critical independent reviews concurrently with another repository writer
  can repeat the same unconditional R20 inventory failure.

## Follow-up items

- Re-dispatch the same frozen candidate to a fresh reviewer only after all other
  repository-writing agents are idle. Use pre-start bytecode denial for every
  Python helper and require byte-identical pre/post inventories. Do not alter or
  clean the candidate or current cache evidence.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation: confirmed
- no self-approval: confirmed
- no build ID, Bronze/Silver/Gold, receipt, provider/network, cloud/container/CI,
  remote, endpoint or deployment action: confirmed

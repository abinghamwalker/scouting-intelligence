# Subagent return

## Task

- task_id: `W04-WYSCOUT-BUILD-CONTRACT-REVIEW-01-R1`
- objective: Independently review the corrected R2 W04 build contract against the
  frozen R20, R21, R4, build/product and season/lineup authorities, including exact
  v15 admission proof binding and composed three-manifest receipt closure.

## Files changed

- `reports/reviews/W04/wyscout-build-contract-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-BUILD-CONTRACT-REVIEW-01-R1.md`

## Summary

- Recommendation: `REWORK`.
- Finding counts: `P0=0`, `P1=2`, `P2=0`.
- Every packet-fixed candidate, evidence and authority digest reproduced exactly
  before analysis.
- `W04-BUILD-R2-P1-UNATTESTED-LAYER-MANIFESTS`: the receipt closure accepts plain
  dictionaries as allegedly prevalidated manifests. Its three positive physical
  manifests all pass the closure but fail the accepted `LayerManifest` validator
  with 12, 12 and 8 errors. The composition seam therefore does not establish the
  required accepted closed-schema prerequisite.
- `W04-BUILD-R2-P1-CALLER-DIGEST-REHASH`: coherent replacement of Gold product
  physical and semantic digests plus the boundary temporal-proof digest is accepted
  when manifest summaries, boundary bytes and caller digest arguments are rehashed
  consistently. No actual product or proof readback/typed authority is supplied.
- The smallest correction is to compose the already-authorized LayerManifest,
  `GOLD_PLAYER_WINDOW` and temporal-proof roots through nominally typed or
  content-bound readback attestations, while independently deriving their digests.
  This adds no schema root, feature, population, dependency, architecture or
  external boundary and requires no real product write.
- The exact window/season/competition identities, five authority rows, five
  dependencies, 25/25 one-hash inverse, v15 23-field/twenty-proof admission contract,
  standalone imports and local-only controls otherwise passed the bounded review.

## Tests run

- command: `shasum -a 256` over the review packet and every fixed binding
  - exit status: `0`
  - result: all expected hashes reproduced, including contract
    `ed7345a8bddbfcb0b26deef57fba09726ce05691e553e1fc1166308e449b06dd`
    and tests
    `9a6446a441ebc8a625395418c0c914a76f980c43fe7e17bd2b40294db95fd1ec`.
- command: `uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `2 files already formatted`.
- command: `uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`.
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `199 passed in 4.09s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25 checks, zero failures and zero Git remotes.
- command: independent `uv run python -B -c` accepted-validator and coherent-rehash
  probe
  - initial locked/no-sync sandbox exit status: `2`; external uv-cache inspection was
    denied before the probe ran.
  - accepted packet-route exit status: `0`
  - result: `REPRODUCED_FAIL_OPEN_SCHEMA_ATTESTATION_AND_PRODUCT_REHASH 3`;
    closure accepted all three manifests rejected by the accepted schema validator
    and accepted coherent downstream product/proof digest substitutions.
- command: independent `uv run python -B -c` UUID/projection/inverse reconstruction
  - exit status: `0`
  - result: exact match, season and competition identities plus 25/25 projection
    reproduced.
- command: independent `uv run python -B -c` AST import-boundary inspection
  - exit status: `0`
  - result: only standard-library and Pydantic imports; no `scouting` import.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-build-contract-independent-review-R1.md`
  - SHA-256:
    `71191b27210014bf5767cad542f2f66d090a6868aa01290aba7583f4aac8e05c`
- Findings:
  - `W04-BUILD-R2-P1-UNATTESTED-LAYER-MANIFESTS`
  - `W04-BUILD-R2-P1-CALLER-DIGEST-REHASH`

## Risks

- Until corrected, a `COMPLETE` receipt can be declared over manifests that never
  passed the accepted closed schema and over coherently rehashed caller claims that
  are not bound to Gold product or temporal-proof readback.
- No other P0, P1 or P2 finding was identified within this bounded review.

## Follow-up items

- Issue one bounded R3 build-contract/test correction for the two composition seams,
  then obtain a fresh independent review and master acceptance before downstream
  schema aggregate, product implementation or publication relies on the closure.

## Scope confirmation

- no Git operations: confirmed; none performed
- no unauthorised dependency or lockfile changes: confirmed; none performed
- no edits outside `allowed_paths`: confirmed; only the two review-report paths
  listed above were created
- no implementation, tests, orchestration, authority, product, data, run or
  verification changes: confirmed
- no provider/network, cloud, container, hosted CI, endpoint, deployment or public
  action: confirmed
- no delegation or self-approval: confirmed

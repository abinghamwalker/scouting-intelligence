# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R4`
- objective: Correct only the three R3 master findings: exact frozen authority
  objects, complete executable build/completion/receipt predicate constants, and
  valid model-led all-twelve-root serialization evidence.

## Files changed

- `src/scouting/contracts/wyscout_schema.py`
- `tests/contracts/test_w04_wyscout_schema_closure.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R4.md`

`src/scouting/storage/formats.py` remains byte-identical to the accepted R3 input
(`84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c`).

## Summary

- Corrected the frozen match raw-record digest to
  `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`.
- Exported exact deep-equal in-memory copies of the accepted
  `completion_index_binding`, `build_identity`, `window_authority`,
  `layer_manifest_authority`, `receipt_contracts`, `source_binding`,
  `season_binding`, `lineup_population`, and `build_projection_binding` objects.
- Exported eight separate external/composed predicates E1-E8. Expanded every
  reachable R4 build validator predicate to its complete owning field roster and
  material component, argv, preimage, inverse, path, receipt, and readback constants.
- Preserved the owning-model transitive definition closures. `WindowIdentity` and
  `PreBuildProjection` are not injected as unreachable schemas; their frozen
  semantics are represented only by E4/E8 composed constants.
- Added a frozen independent 56-row runtime ledger digest and eight-predicate
  external ledger digest, plus direct material-constant checks against contract
  owners and accepted authority JSON loaded only by tests.
- Replaced descriptor-generated pseudo-logical round-trip evidence with exactly 29
  accepted Pydantic root instances. Every instance survives fresh strict validation,
  is mechanically projected only from its accepted descriptor, and passes exact
  Arrow inverse equality to its serialization-mode contract row.
- The matrix covers two known Bronze rows, all five raw-kind states, all seven tagged
  rejected-field arms, three action variants, open/closed lineups, an equal-clock
  survivor possession, precision-38 `1/3` fact/Gold coverage, and a lineup-only
  right-censored zero-denominator fact/Gold row.
- Added zero-Parquet-write assertions for every canonical-Decimal alias family,
  non-string physical scalars, Arrow null misuse, nonfinite values, and invalid
  UTF-8 while retaining the accepted R3 projection implementation.

## Tests run

- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: `4 files already formatted`
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/storage/formats.py src/scouting/contracts/wyscout_schema.py tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: `Success: no issues found in 4 source files`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: 0
  - result: `526 passed in 123.55s`
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: 0
  - result: `179 passed in 3.95s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS, 25/25 checks; branch `main`; zero remotes.
- command: independent exact-authority/roster probe
  - exit status: 0
  - result: nine authority subobjects deep-equal; 23 roots; eight external predicates;
    wrong R3 digest absent; unreachable schema injection absent.
- command: `git diff --check -- <four R4 implementation/test paths>`
  - exit status: 0
  - result: no whitespace errors.

## Artifacts/evidence

- `src/scouting/storage/formats.py` SHA-256:
  `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c`
- `tests/unit/test_w04_wyscout_product_formats.py` SHA-256:
  `8e68548967293b28e694359509667106951bdc5ba8e1636a541f81f7c3773e1a`
- `src/scouting/contracts/wyscout_schema.py` SHA-256:
  `67b29d6f13228f8e9ba87468545457961c6fdf808831aa1d2ae08ef12d2b7c3b`
- `tests/contracts/test_w04_wyscout_schema_closure.py` SHA-256:
  `c6ae3c4c469c0fec819a18ee3d929ec9cd291f386ff8dae2fb44394173fa7c42`

## Risks

- No residual implementation blocker identified. This return is producer evidence,
  not independent review or master acceptance.
- No product, aggregate, manifest, receipt, provider, network, publication, or
  deployment action was performed.

## Follow-up items

- Independent R4 review and master acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

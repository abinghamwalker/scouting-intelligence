# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R4`
- objective: independently review the frozen R4 23-root schema-closure candidate
  against all four returned P1 families without repairing implementation
- verdict: **REWORK**
- findings: **P0 0 / P1 2 / P2 0**

## Files changed

- `reports/reviews/W04/wyscout-23-root-schema-closure-independent-review-R4.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R4.md`

## Summary

- Reproduced every fixed binding before analysis and before return.
- Fully read `AGENTS.md`, the review and producer packets, every named authority,
  verification/oracle report, both frozen contract owners, the storage projection,
  schema producer, and both candidate test files.
- Independently traversed the frozen root annotations and actual validator bodies.
  The emitted roster contains 56 reachable bindings, but 26 owner/validator bindings
  omit at least one material directly read runtime field. This is P1-01.
- Executed and inspected the 29-row matrix. It has the claimed row/root counts and
  strict validation, but misses the required Bronze-known seven-arm/nested shapes,
  Bronze-rejected distinct raw shapes, and Silver-action required-null/unmapped and
  zero-scale variants. This is P1-02.
- Independently confirmed passing frozen-constant deep equality for all nine
  authority subobjects, exact E1-E8 source hashes, the corrected raw digest, and the
  complete build/completion/layer/receipt constants.
- Independently confirmed the bounded canonical-Decimal projection: six reachable
  physical UTF-8 paths from only the two authorized logical owners, 30 unchanged
  decimal128(22,18) paths, strict canonical inverse, and zero-write malformed cases.

## Tests run

- command: `shasum -a 256 orchestration/task_packets/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R4.yaml reports/verification/W04/wyscout-23-root-schema-closure-R4-master-pre-review.md reports/verification/W04/wyscout-23-root-schema-closure-R3-master-verification.md reports/reviews/W04/wyscout-schema-closure-R3-acceptance-oracle-R1.md src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R4.md`
  - exit status: 0
  - result: every packet-fixed SHA-256 reproduced
- command: `uv run python -c '<independent root-annotation traversal, validator-source AST and emitted-operand comparison>'`
  - exit status: 0
  - result: 60 reachable models, 56 emitted predicate bindings, 26 bindings with
    missing directly read fields
- command: `uv run python -c '<independent authority JSON equality, E1-E8 cited-source hashing and frozen constant attack>'`
  - exit status: 0
  - result: nine exact authority subobjects; all cited hashes reproduced; 13
    completion keys/eight requirements; 25 build keys; accepted raw digest present;
    stale digest absent
- command: `uv run python -c '<independent descriptor Decimal/path census>'`
  - exit status: 0
  - result: 6 canonical-Decimal paths; 30 decimal128 paths, all `(22,18)`; 11
    JSON-only roots
- command: `uv run python -c '<executable 29-row fixture matrix variant inspection>'`
  - exit status: 0
  - result: 29 rows/12 roots, while reproducing the missing variants in P1-02
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: 4 files already formatted
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: all checks passed
- command: `uv run mypy src/scouting/storage/formats.py src/scouting/contracts/wyscout_schema.py tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: 0
  - result: no issues in 4 files
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: 0
  - result: `526 passed in 124.19s`
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: 0
  - result: `179 passed in 3.99s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS, 25/25; branch `main`; zero remotes

## Artifacts/evidence

- `reports/reviews/W04/wyscout-23-root-schema-closure-independent-review-R4.md`
- P1-01: 26 reachable predicate bindings with missing direct runtime operands;
  representative exact omissions and bounded correction are recorded in the review
- P1-02: executable matrix kind/shape/action-state evidence and bounded fixture
  correction are recorded in the review
- passed families: all nine frozen authorities/composition and bounded Decimal
  projection/serialization are recorded in the review

## Risks

- The current authority can overstate executable runtime predicate closure because
  the emitted operand subset does not disclose all equality inputs used by validators.
- The current green 29-row test can regress required tagged-JSON/raw-shape/action
  variants without failing.
- No architecture, product-scope, provider, dependency, or local-only blocker was
  found; both findings are bounded rework.

## Follow-up items

- Expand only the existing runtime predicate operands/material constants to cover
  every actual validator input and add an independent expected-ledger completeness
  assertion.
- Replace only the deficient rows in the exact 29-row matrix and assert the missing
  variant properties explicitly.
- Obtain a fresh independent review and master acceptance after the bounded rework.

## Scope confirmation

- no Git operations: confirmed; no Git command was issued by this reviewer. The
  packet-mandated local-only verifier performed its own read-only branch/remote
  checks and reported `main` with zero remotes.
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation, test, packet, authority, verification, product, data, provider,
  network, cloud, container, CI, publication, deployment, or remote action: confirmed
- no delegation and no self-approval: confirmed

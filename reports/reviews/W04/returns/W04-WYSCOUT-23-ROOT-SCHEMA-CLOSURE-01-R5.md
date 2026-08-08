# Subagent return — BLOCKED

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R5`
- objective: Correct only R4 P1-01 runtime-predicate closure and R4 P1-02 Bronze/SilverAction variants while preserving every accepted projection and canonical-Decimal boundary.
- disposition: `BLOCKED_STOP_CONDITION`

## Files changed

- `src/scouting/contracts/wyscout_schema.py`
- `tests/contracts/test_w04_wyscout_schema_closure.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R5.md`

## Summary

- Preserved the current partial R5 bytes after the master confirmed the executable conflict below is a genuine R5 stop condition.
- Corrected the runtime predicate authority to name the material inputs omitted by R4 P1-01, including all nine inherited product-row bindings and the Bronze, Action, fact, Gold, LayerManifest, entry, applicability, and temporal bindings.
- Added a test-owned explicit ledger keyed by owner and validator. It freezes operation, ordered operands, material-constant key roster, and exact material-constant content digest for all 56 reachable bindings.
- Added an independent AST direct-field probe. The probe reports 56 reachable bindings and zero direct-field omissions.
- Added the required distinct Bronze-known and Bronze-rejected-record raw shapes, reproduced digests/source rows/lineage, and explicit property assertions.
- Added three fresh-valid SilverAction variants with one, zero, and two positions; source scales 0 and 18; and a null player/team/event/subevent action deriving `PREDICATE_UNMAPPED` and `INELIGIBLE_UNMAPPED`.
- Did not change the accepted Arrow projection, storage implementation, logical models, authorities, roots, features, populations, or dependencies.

## Tests run

- command: `uv run --locked --no-sync ruff format --check src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run --locked --no-sync ruff check src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run --locked --no-sync mypy src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: local uv direct-validator AST audit over the exported closure
  - exit status: `0`
  - result: `bindings 56 missing []`
- command: `uv run --locked --no-sync pytest -q tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `1`
  - result: `27 passed, 1 failed in 9.22s`
  - deterministic failure: the fresh-valid source-scale-0 `SilverAction` reaches `encode_w04_wyscout_product_parquet`, where the frozen `DECIMAL128(22,18)` Arrow projection converts logical `Decimal("10")` to physical/readback `Decimal("10.000000000000000000")`; the encoder correctly rejects this because the Arrow row no longer byte-semantically equals the canonical contract row.
- remaining R5 acceptance commands were not run after the master confirmed the stop condition.

## Artifacts/evidence

- partial R5 schema SHA-256: `e86d8de760c545e14ddb46b4de216fdc94cefea8c5d2e745fd4e10b0b1ab0e1b`
- partial R5 schema-test SHA-256: `7133e736c80af8c6f60ae31e78bbe3c5611f1eaa92ed7716a9bac9cbbb8cda40`
- accepted storage implementation remains unchanged: `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c`
- accepted storage test remains unchanged: `8e68548967293b28e694359509667106951bdc5ba8e1636a541f81f7c3773e1a`
- failed executable evidence is the focused pytest traceback at `encode_w04_wyscout_product_parquet` with `FormatError: Arrow row 0 does not exactly equal its contract row`.

## Risks

- The R5 packet requires a source-scale-0 SilverAction in the 29-row matrix while also requiring every accepted projection/canonical-Decimal behavior to remain unchanged.
- A fixed Arrow decimal with scale 18 cannot reversibly retain the lexical/source scale 0 of the logical Decimal. Making that row physically round-trip would require changing accepted projection or inverse-decoding behavior, which is outside R5 and expressly forbidden.
- Skipping physical round-trip for the scale-0 row or accepting normalized scale-18 contract bytes would weaken the pre-existing descriptor/contract-row equality gate and was not attempted.
- This return is not a PASS and does not self-approve the partial R5 changes.

## Follow-up items

- Master/user architecture decision is required before R5 can pass: either authorize a broader reversible Decimal projection/inverse correction or explicitly redefine the scale-0 variant as logical-validation-only. Neither change is authorized by R5.

## Scope confirmation

- no Git operations: yes
- no unauthorised dependency or lockfile changes: yes
- no edits outside `allowed_paths`: yes
- no provider/network, cloud, container, CI, publication, deployment, aggregate, or product action: yes

# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R8`
- objective: Correct only the test-owned three-row SilverAction matrix so every frozen R5 Section 5.6 variant is strict-validated and asserted exactly while preserving the accepted R7 schema bytes.

## Files changed

- `tests/contracts/test_w04_wyscout_schema_closure.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R8.md`

## Summary

- Replaced the three matrix-owned SilverAction rows with strict-runtime-validated `SA-NULL-UNMAPPED`, `SA-ONE-POSITION`, and `SA-TWO-POSITION` rows in frozen order.
- Each row owns a distinct canonical action identity, source event/action ID `(5,6,7)`, physical action source row ordinal `(0,1,2)`, exact one-action period sequence, and lineage containing exactly its matching action source row.
- `SA-NULL-UNMAPPED` has all five required nullable identity/taxonomy fields explicitly null, no positions, sorted tags, `Decimal("0")` with lexical scale `0`, `PREDICATE_UNMAPPED`, and `INELIGIBLE_UNMAPPED`; its action does not occur in a resolved group.
- `SA-ONE-POSITION` has one in-bounds position, exact independently retained position-axis scales, non-null team, CONTROL pair `(8,80)`, `Decimal("10.123456789012345678")`/scale `18`, admitted state, and resolved eligibility.
- `SA-TWO-POSITION` has two ordered in-bounds positions with independently retained axis scales and bound flags, non-null team, RESTART pair `(3,30)`, admitted/resolved state, and the exact no-rounding decimal128(22,18) capacity-boundary value `Decimal("9999.999999999999999999")`/scale `18`.
- Added independent assertions for action/source/physical-source uniqueness, `(0,1,2)` positions, `(0,18,18)` declared scales, exact Decimal strings/exponents and 22 boundary digits, sorted tags, exact sequence/lineage equality, all five null fields, CONTROL versus RESTART decisions, admitted/unmapped states, actual resolved-group membership, and descriptor-led exact logical JSON-byte reproduction through Parquet encoding.
- Preserved the 29-row total, the exact root cardinality vector, and all non-action matrix assertions. The existing non-action possession row retains its prior nested action values through an equivalent strict reconstruction.
- Accepted schema SHA-256 remains unchanged: `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4`.
- R8 test SHA-256: `5daaa32082cc0f82ed9b8b0b61cc06fe9d2db633cb15ed9c9837e491f2b9a5b8`.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `40 passed in 15.50s`
- command: `uv run ruff format --check tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `uv run ruff check tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy tests/contracts/test_w04_wyscout_schema_closure.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: `595 passed in 127.56s`
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `179 passed in 3.91s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: overall `PASS`; main branch, zero remotes, and no hosted CI, container, deployment, or external-service boundary violation
- rework note: the first focused run after adding explicit descriptor evidence produced `39 passed, 1 failed` because the test compared two intentionally different descriptor model types. The encode itself and every fixture assertion passed. The assertion was corrected to the exact cross-type schema-role and serializer-version bindings; the focused rerun and all packet gates passed.

## Artifacts/evidence

- strict R5 Section 5.6 matrix fixtures and assertions: `tests/contracts/test_w04_wyscout_schema_closure.py`
- accepted unchanged schema SHA-256: `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4`
- R8 test SHA-256: `5daaa32082cc0f82ed9b8b0b61cc06fe9d2db633cb15ed9c9837e491f2b9a5b8`

## Risks

- No known matrix-completeness, Decimal-capacity, identity, lineage, schema, dependency, or local-only residual risk was found by the packet gates.
- Producer evidence remains unaccepted until fresh independent review and master acceptance.

## Follow-up items

- Fresh independent R8 review and master acceptance; producer self-approval is forbidden.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no accepted schema edit: confirmed
- no delegation: confirmed

# Subagent return

## Task

- task_id: `W04-DATA-CONTRACTS-01-R2`
- objective: Close all ten accepted R1 P1 findings at every public W04 Wyscout data-contract constructor while preserving R20/R21, the accepted authorities and preimages, the exact four-feature scope, and the local-only/no-product boundary.

## Files changed

- `src/scouting/contracts/wyscout_data.py`
- `tests/contracts/test_wyscout_data_contracts.py`
- `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R2.md`

## Summary

- Closed direct `RawKindEvidence` construction by deriving the complete missing/null/non-string/safe/unsafe state, rejecting known tokens, and recomputing the framed canonical digest.
- Bound `SilverAction` to the exact 36 strict-integer event/subevent pairs, positive equal provider/action source IDs, action-family row membership, and exact finite decimal128(22,18) lexical scale/capacity. Bound rejected subevent fields to the accepted path, raw type/value, decision, reason, authority, rights, lineage, and action source family.
- Enforced strict positive non-boolean source IDs for competition, team, player, match, and action at the UUID helper and every public entity/action constructor.
- Added exact source receipt/availability, tenant, restricted-rights, source-row-count, authority-reference, decision/review/acceptance-clock, dependency-hash, and source-family evidence closure across Bronze, Silver, Gold, temporal proof, and manifests.
- Made optional zero-denominator coverage proof-bearing, made authority-missing/failed states representable only fail-closed, and enforced suppressed/research-only/data-ready applicability order at player-match and Gold boundaries.
- Closed manifest filename/layer/build, non-empty entry, safe preceding-layer parent, same-build parent product, schema-role, path-partition, tenant, rights, feature-schema, authority-clock, and dependency-lineage invariants.
- Reconciled Gold contributor facts and derived keys to tenant/manifest/player/competition/season/schema/window/authority state, then recomputed only `action_count`, `coordinate_known_action_count`, distinct `match_count`, and `resolved_possession_action_count`.
- Expanded the focused in-memory suite from 44 to 140 tests with direct-constructor, mutation, and cross-authority matrices for all ten findings. No serializer, product byte, manifest file, receipt, runtime, build, provider access, or architecture revision was created.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run lint-imports`
  - exit status: `0`
  - result: `30 files, 46 dependencies; 3 contracts kept, 0 broken`
- command: `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: `0`
  - result: `370 passed in 78.27s`; focused contract coverage is `140 passed`
- command: `uv run bandit -q -r src/scouting/contracts/wyscout_data.py`
  - exit status: `0`
  - result: no findings
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all 25 local-only checks passed

## Artifacts/evidence

- `src/scouting/contracts/wyscout_data.py` SHA-256: `87dc13ada636e018ff9dfc17b548942a1d93132db8a615248cc8be3b23ebe99d`
- `tests/contracts/test_wyscout_data_contracts.py` SHA-256: `1b5aafbd127cda6703dce8de358b10c6f4c467de0821601b6b358564a5dabd47`
- Fixed-input digest readback matched:
  - R1 independent review: `862fa5513cd261fd95bcd921fb52631c90af56ff930ce968682059879761dee2`
  - identity acceptance: `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86`
  - source manifest: `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
  - field-v2 acceptance: `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436`
  - possession-v2 acceptance: `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1`
  - supported-feature acceptance: `d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c`
  - product-contract preimage: `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
  - schema-bundle preimage: `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`

## Risks

- Residual uncertainty is limited to fresh independent review. The implementation is deliberately constructor-only and in-memory; no production materialization path was exercised or authorized.

## Follow-up items

- Fresh independent review of `W04-DATA-CONTRACTS-01-R2`.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

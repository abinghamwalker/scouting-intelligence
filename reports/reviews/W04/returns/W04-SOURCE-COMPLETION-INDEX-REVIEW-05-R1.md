# Subagent return

## Task

- task_id: W04-SOURCE-COMPLETION-INDEX-REVIEW-05
- objective: Independently confirm that the exact R4 capability correction preserved the accepted R3 source-completion-index semantics, provenance, derivation, and bounded-manifest result.

## Files changed

- `reports/reviews/W04/wyscout-source-completion-index-R4-semantic-regression-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-REVIEW-05-R1.md`

## Summary

- Recorded `PASS` with `P0=0`, `P1=0`, `P2=0` for the exact fixed R4 candidate.
- Reproduced the accepted index as five members, `3,652` periods, and `3,071,395` actions without changing its bytes.
- Confirmed strict integer-only event/subevent projection, retained unmapped strings, group-first equal-clock behavior, complete causal provenance, exact four-feature and five-dependency lineage derivation, six fixed coverage dimensions, and exact one-match manifest scope.
- Confirmed match `2499719` requires all `901 + 867 = 1,768` actions across two periods while its selected player's exact causal provenance contains the contributing `867`-row period only; no all-index completeness claim is made.

## Tests run

- command: `shasum -a 256 src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json reports/reviews/W04/wyscout-source-completion-index-semantic-independent-review-R1.md`
  - exit status: 0
  - result: all six fixed bindings matched exactly
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_wyscout_data_contracts.py -k 'integer or string_subevent or equal_clock or causal or completion_index or real_match_checked_path or gold or manifest'`
  - exit status: 0
  - result: `98 passed, 279 deselected in 111.83s`
- command: `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py::test_recomputed_lineage_and_cross_boundary_equality_are_mandatory tests/contracts/test_wyscout_data_contracts.py::test_temporal_proof_has_exact_five_ordered_dependencies_and_valid_from tests/contracts/test_wyscout_data_contracts.py::test_temporal_proof_rejects_wrong_cardinality_duplicate_and_lineage_drift`
  - exit status: 0
  - result: `3 passed in 0.20s`
- command: `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py::test_action_subevent_no_coercion_matrix tests/contracts/test_wyscout_data_contracts.py::test_action_subevent_emits_only_admitted_strict_integer_pair tests/contracts/test_w04_r21_cross_authority_composability.py::test_language_bool_as_int_is_explicitly_excluded tests/contracts/test_w04_r21_cross_authority_composability.py::test_non_strict_subevent_values_preserve_raw_evidence_without_coercion tests/contracts/test_w04_r21_cross_authority_composability.py::test_unknown_integers_never_emit_canonical_subevent`
  - exit status: 0
  - result: `27 passed in 0.22s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: `PASS`; all 25 controls passed
## Artifacts/evidence

- `reports/reviews/W04/wyscout-source-completion-index-R4-semantic-regression-review-R1.md`
- independent read-only probe results, all exit `0`: exact index/member/period/action reconciliation; match `2499719` was `901 + 867 = 1,768`; selected target was two `2H` actions with `867` causal source rows; string subevent remained unmapped and numeric-string/Boolean event IDs were rejected
- accepted index SHA-256: `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- R4 implementation SHA-256: `e7778db8c977b8461bb590f7174e4b519d7a2ba0a4171d99aa1fd686a6cd5302`
- R4 source-test SHA-256: `05593a0a0afda62af2b6a2c8753a4f83e78fcbd363b89788751dd2055ed6dfeb`
- R4 contract-test SHA-256: `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e`

## Risks

- No open P0, P1, or P2 finding within the bounded semantic-regression scope.
- The real-source proof remains intentionally substantial (`111.83s` in the packet selection); this is bounded local verification, not a semantic defect.

## Follow-up items

- Master acceptance after the separate independent capability/proof-graph review; no semantic rework requested.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

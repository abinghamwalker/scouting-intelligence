# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-SOURCE-AUDIT-01`
- objective: Audit the frozen Wyscout source and accepted completion-index APIs for the exact smallest real one-match, one-player vertical slice without changing source, product, test, run, or control bytes.

## Files changed

- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-AUDIT-01-R1.md`

## Summary

- Verdict: `PASS` for a bounded source-to-checked-population route; no architecture, dependency, feature-roster, provider, cloud/container, endpoint, CI, remote, or deployment expansion is required.
- Material implementation constraint: a real raw-field projection derives Gold `(action_count=2, coordinate_known_action_count=2, match_count=1, resolved_possession_action_count=2)`. The previously exercised test-only checked-product fixture derives `(2, 0, 1, 2)` only because `_real_checked_action_payload` replaces both records' valid raw `positions` with `action_positions=()`. Production must follow the accepted `POSITION_ARRAY` authority, not copy that test fixture.

### Frozen bindings

| Binding | Exact value |
| --- | --- |
| source manifest ID | `4e16bdb5-afe7-5601-88ad-adc124cfce3b` |
| source manifest physical SHA-256 | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` |
| completion-manifest SHA-256 | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| England event member | `archive-members/events_England.json` |
| England member SHA-256 | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` |
| England member size / rows | `188,888,614` bytes / `643,150` rows |
| completion-index SHA-256 | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` |
| completion-index size / scope | `644,037` bytes / 5 members / 3,652 match-period rows / 3,071,395 actions |

The source manifest binds these values at `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json`. The accepted index binds the manifest ID, manifest physical digest, completion-manifest digest, exact member paths/digests/counts, canonical period order, aggregate reconciliation, and its own content address (`src/scouting/sources/wyscout_completion_index.py:708`, `:899`).

### Exact guarded extraction route

1. Load the accepted index only by the pinned address through `load_source_completion_index` (`src/scouting/sources/wyscout_completion_index.py:899`). This verifies filename address, payload address, strict canonical JSON, exact five-member ordering, uniqueness, per-member row reconciliation, aggregate count, source-manifest binding, and accepted content address.
2. Verify the stored source-manifest bytes through the accepted source boundary (`_validate_source_manifest_bytes`, `src/scouting/sources/wyscout_completion_index.py:588`). For a complete bridge remeasurement, `build_source_snapshot_manifest` uses `_measure_source_file` over every declared object/member (`src/scouting/sources/wyscout_manifest.py:489`, `:706`).
3. Resolve only the frozen England `EventMemberSpec`, then read it through the source-owned guarded boundary `_read_verified_member` (`src/scouting/sources/wyscout_completion_index.py:563`). It uses `_open_regular_beneath` (`src/scouting/sources/wyscout_manifest.py:438`) with no-follow descriptor traversal, requires a regular file, hashes in 1 MiB chunks, caps bytes at the declared size, compares stable file identity/metadata before and after, and returns no payload until exact size and SHA-256 pass. The operation is bounded by the frozen 188,888,614-byte member.
4. Strict-decode the verified payload through `_decode_action_member` (`:475`), require exactly 643,150 rows, enumerate before filtering so `source_record_ordinal` remains the physical zero-based ordinal, select strict integer `matchId == 2499719`, and project each row with public `completion_action_evidence` (`:489`).
5. Canonically sort by `(period_rank, Decimal(eventSec token), physical ordinal, provider event ID)`, compare all 1,768 actions through public `validate_match_population` (`:971`), then issue the opaque full-match capability through `validate_checked_match_population` (`:1194`). Any missing/additional/duplicated/reordered/stale/cross-member/cross-match/cross-period row fails closed.

The guarded reader currently buffers the one verified member after chunked hashing rather than exposing a streaming record iterator. That is acceptable for this frozen POC bound and was reproduced in 2.7 seconds locally. If an iterator is desired, it must be exposed from `scouting.sources` as a public adapter that withholds selected records/authority until EOF, stable-file, size, digest, and row-count checks all pass. `scripts/profile_wyscout_v5.iter_json_array` is not a product authority: it is a profiling helper, uses ordinary path opening, and yields records before final whole-file digest verification.

### Exact match and selected player

| Scope | Count | Membership SHA-256 |
| --- | ---: | --- |
| match `2499719`, `1H` | 901 | `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b` |
| match `2499719`, `2H` | 867 | `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16` |
| full checked match | 1,768 | exact union of both indexed periods |

- selected source player ID: `285508`
- canonical player UUID: `be8da881-2b15-513f-978f-6bb3865bc8e2`
- source team ID: `1631`
- canonical team UUID: `5b353635-819b-5bd1-8ca2-5a7364042a96`
- canonical match UUID: `bad97950-6fac-5cf0-a93c-094f91abbb9b`
- selection rule reproduced from production values: among players whose complete match actions are all in resolved possession groups and have one team, choose `(fewest actions, canonical UUID bytes)`; the result has exactly two actions, both in `2H`.

| Provider event / canonical action | Ordinal | Clock | Strict event/subevent | Tags | Raw-record SHA-256 |
| --- | ---: | ---: | --- | --- | --- |
| `177960876` / `c07bc150-6b89-5149-a8ec-d7555749f351` | 1615 | `2447.598183` | `(8, 85)` | `[1801]` | `3e1f3dbcb733c2265e036841d90108bfddd528f229286bfe40e1d8dfbcbc505a` |
| `177961018` / `9af787ac-0a79-5286-8a9c-f99c42304920` | 1733 | `2846.386421` | `(8, 86)` | `[901, 1802]` | `1811f2c3da8797f0a4cc4a8eceb416bec03b75a50292bfe82f216e88dc93e221` |

The two target actions intersect two resolved same-team possession groups containing 7 and 6 actions respectively. A faithful Silver slice therefore needs 13 checked action products to construct the two complete checked possessions, while the selected player-match fact contributes only the target player's two actions. Both target actions share the accepted full `2H` sequence, so exact causal fact provenance contains all 867 `2H` source rows; the full-match capability still requires both periods and all 1,768 actions.

### Four deterministic feature facts

- `action_count = 2`: the selected player's exact complete action set.
- `coordinate_known_action_count = 2`: event `177960876` has accepted positions `(49,49)` and `(30,41)`; event `177961018` has `(74,63)` and `(86,47)`. Each action has exactly two finite integer `(x,y)` positions within inclusive `0..100`. The accepted `POSITION_ARRAY` transform is at `configs/schema/wyscout-v5-field-registry-v2.yaml:1133`, and the contract predicate is `src/scouting/contracts/wyscout_data.py:1464`.
- `match_count = 1`: one exact canonical match.
- `resolved_possession_action_count = 2`: each selected-player action has exactly one membership in one of the two resolved groups.

The test-only `_real_checked_action_payload` at `tests/contracts/test_wyscout_data_contracts.py:647` hard-codes `action_positions=()` and is the sole reason `test_real_match_checked_path_reaches_gold_and_exact_scoped_manifest` (`:2980`) expects coordinate count zero. It proves completion-capability composition, not actual field ingestion. Copying it into production would conflict with the accepted raw-field authority.

### Reusable versus test-only surfaces

- Public production surfaces suitable for the product path: `load_source_completion_index`, `completion_action_evidence`, `validate_match_population`, `validate_checked_match_population`, all checked Silver/Gold/manifest builders, and `require_checked_product` in `scouting.sources.wyscout_completion_index`; `canonical_source_uuid` and strict Wyscout contracts in `scouting.contracts.wyscout_data`.
- Source-owned private primitives may support a new public extraction adapter inside `scouting.sources`, but `data_products` should not bind directly to `_EVENT_MEMBERS`, `_read_verified_member`, `_decode_action_member`, `_validate_source_manifest_bytes`, or bridge underscored functions.
- Never import production behavior from `real_checked_match_population`, `_real_checked_action_payload`, or `test_real_match_checked_path_reaches_gold_and_exact_scoped_manifest` in `tests/contracts/test_wyscout_data_contracts.py`; nor from the unit fixtures in `tests/unit/test_wyscout_source_completion_index.py`.

## Tests run

- command: `shasum -a 256 data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - exit status: `0`
  - result: exact physical SHA-256 values `8fb6eb...89bd` and `46a224...87df`.
- command: read-only `uv run python -c` guarded source/index/match/target probe using the existing project environment
  - exit status: `0`
  - result: exact index/member reconciliation; `901 + 867 = 1,768`; target source player `285508`; two `2H` actions; two resolved groups of 7 and 6 actions; 867 causal rows; raw accepted positions on both target actions.
- command: `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py::test_exact_content_address_and_five_member_reconciliation tests/unit/test_wyscout_source_completion_index.py::test_exact_real_period_population_validates tests/unit/test_wyscout_source_completion_index.py::test_public_match_factory_builds_every_exact_source_bound_period tests/unit/test_wyscout_source_completion_index.py::test_exact_match_comparison_issues_opaque_nonreplayable_capability`
  - exit status: `0`
  - result: `4 passed in 4.62s`.

## Artifacts/evidence

- this report: `reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-AUDIT-01-R1.md`
- accepted source manifest: `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json`
- accepted index: `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`

## Risks

- `P1 implementation constraint`: importing the test-only action payload or preserving its coordinate-zero expectation would silently discard accepted source coordinate evidence and produce a false Gold value. The correct raw-ingestion expectation is `(2, 2, 1, 2)`.
- `P2 maintainability`: the exact guarded member extraction functions are private. Add one narrow public source-owned adapter before product code consumes them; this is an additive module-boundary change, not an architecture or dependency revision.
- The POC read is deliberately bounded but memory-resident at 188,888,614 raw bytes plus decoded objects. It is sufficient for this one-and-done local frozen slice; no new dependency is needed.

## Follow-up items

- Product packet must encode the real coordinate expectation `(2, 2, 1, 2)` and forbid imports from tests.
- Allocate a narrow `scouting.sources` path to expose the verified one-match population without leaking underscored source primitives into `data_products`.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

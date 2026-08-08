# W04 Wyscout data contracts independent review R1

## Review identity

- Task: `W04-DATA-CONTRACTS-REVIEW-01`, revision `R1`
- Role: independent reviewer
- Disposition: **REWORK**
- Reviewed scope: the W04 executable Wyscout data-contract implementation and its focused test suite, against the accepted R20 authorities as superseded by the bounded R21 field and possession correction.
- Open findings: P0 `0`, P1 `10`, P2 `0`
- Acceptance rule: PASS is unavailable while any P0-P2 finding remains open.

The six prescribed checks pass, but passing those checks does not establish contract closure. Independent constructor-level probes reproduce multiple ways to create records that contradict the accepted authorities. No finding requires a new architecture revision: each is a bounded implementation, test, or evidence correction within the existing W04 data-contract scope.

## Materials and digest reproduction

Every file listed in `W04-DATA-CONTRACTS-REVIEW-01-R1.yaml` was read in full. The following fixed inputs were independently hashed before review:

| Material | SHA-256 | Result |
|---|---:|---|
| `src/scouting/contracts/wyscout_data.py` | `9d90641965ef6d9351d76785d5729cc932ed7ea3cae11ff931dcef3279148452` | match |
| `tests/contracts/test_wyscout_data_contracts.py` | `568859f5879766c0470169e480177c3089b26788456c3133294e86ba2b0dc69a` | match |
| `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R1.md` | `abc9418fa0e61187097a6ff7ed11345f7e265703116aff1ad2a5ce30e200176a` | match |
| `reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json` | `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86` | match |
| `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json` | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | match |
| `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json` | `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436` | match |
| `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json` | `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1` | match |
| `reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json` | `d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c` | match |
| `configs/schema/wyscout-v5-product-contract-preimage-v1.json` | `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293` | match |
| `configs/schema/wyscout-v5-schema-bundle-preimage-v1.json` | `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f` | match |

## Required verification results

| Check | Result | Independent observation |
|---|---|---|
| `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | PASS | 2 files already formatted |
| `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | PASS | no lint errors |
| `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | PASS | no type errors in 2 source files |
| `uv run lint-imports` | PASS | 30 files, 46 dependencies, 3 contracts kept, 0 broken |
| `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` | PASS | 225 passed in 69.07s |
| `uv run python scripts/verify_local_only.py` | PASS | all 25 checks passed |

The first sandboxed `lint-imports` invocation could not access the existing uv cache because of filesystem permissions. The exact command was rerun with the approved uv execution boundary and passed. This was an execution-environment artifact, not a repository failure.

## Findings

### W04DC-P1-001 — Raw-kind evidence can be forged at the public model boundary

`RawKindEvidence` validates only a subset of relationships between `state`, raw type, and raw value (`wyscout_data.py:390-436`). The factory at `wyscout_data.py:459-488` applies more rules, but callers can instantiate the exported model directly and bypass those rules.

Independent probes accepted all of the following contradictory states:

- `string-unknown-safe` with `../action`;
- `string-unknown-safe` with the known token `action`;
- `string-unsafe` with the safe value `Competition`.

This breaks the R21 exact raw-kind classification and quarantine boundary. The model itself must enforce the complete classification invariant; factory-only enforcement is insufficient. Add direct-constructor negative tests for safe, unsafe, known, non-string, and unmapped states.

### W04DC-P1-002 — The strict integer-only action/subevent contract is bypassable downstream

The helper around `wyscout_data.py:1329-1427` correctly distinguishes admitted pairs, but `SilverAction` at `wyscout_data.py:804-856` does not require its integer `(event_id, subevent_id)` pair to be one of the admitted pairs. A direct constructor accepted `(99, 999)`. `BronzeRejectedField` at `wyscout_data.py:650-684` also accepted a forbidden field with an arbitrary decision and arbitrary rejection reason.

R21 requires exact admitted integer pairs and exact raw evidence for every non-emitted value; strings remain unmapped or quarantined without coercion. Close this invariant at every exported product model, not only in a helper, and test direct construction. Rejected-field evidence must bind the exact raw path, raw type/value, authority decision, and reason required by the accepted registry.

### W04DC-P1-003 — Accepted zero-source policy is not enforced

`canonical_source_uuid` accepts zero for all five canonical entity kinds (`wyscout_data.py:687-707`), while the accepted field registry has `zero_policy: REJECT` for canonical competition, team, player, match, and action source IDs. `SilverCompetition`, `SilverTeam`, `SilverMatch`, and `SilverAction` inherit that gap; `SilverPlayer` already rejects zero at its model boundary.

Independent probes confirmed that `canonical_source_uuid` generates a stable UUID from zero for every one of the five kinds, and that direct constructors accept zero for competition, team, match, and action. The `SilverPlayer` constructor correctly rejected zero. Enforce the authority's strictly positive source-ID domain at every remaining public boundary and add a complete zero-ID rejection matrix.

### W04DC-P1-004 — Decimal128(22,18) precision enforcement accepts overflow

The coordinate/decimal guard at `wyscout_data.py:804-856` derives precision from the coefficient digit tuple but does not account for a positive decimal exponent. `Decimal("1E+30")` was accepted even though it exceeds decimal128(22,18). That permits a value outside the frozen schema contract.

Implement exact finite decimal128(22,18) validation for total integer and fractional capacity, including scientific notation, and add boundary, overflow, NaN, and infinity tests. Canonical serialization must only receive values that satisfy this product-domain constraint.

### W04DC-P1-005 — Temporal evidence is not bound to the exact accepted authority clocks

The dependency and temporal models at `wyscout_data.py:1055-1197` validate authority IDs and digests but do not bind the exact `observed_at`/`available_at` clocks from the accepted authorities. The test fixture itself uses later, incorrect decision clocks (`test_wyscout_data_contracts.py:98-107`) instead of the authority values:

- field decision: `2026-07-30T20:22:17Z`;
- possession decision: `2026-07-30T22:14:21Z`;
- feature decision: `2026-07-31T08:37:00Z`;
- identity decision: `2026-07-31T12:44:27Z`.

These clocks were independently re-read from the four hashed decision files. Each decision-file SHA-256 exactly equals the `decision_sha256` recorded by its accepted authority: field `cd4d51c0d7c365b73b0c23997716eb7755797889dca1fc545772263dc9924736`, possession `8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425`, feature `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`, and identity `6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192`.

Because the wrong-clock fixture passes, its lineage/build preimage is not the frozen authority preimage. Bind every dependency to its exact authority clock and add one negative test per clock plus a positive test using the accepted values.

### W04DC-P1-006 — Row lineage and temporal-proof lineage can disagree

`WyscoutRowLineage` at `wyscout_data.py:567-599` accepts a dependency-lineage hash without recomputing it from the attached authority dependency set. Gold validation at `wyscout_data.py:1257-1326` does not require the base row lineage to equal the attached temporal proof lineage.

An independent probe replaced a Gold row's base dependency hash with `9999…9999` while retaining the original temporal proof; validation accepted it. Make dependency lineage a single derivable invariant and require equality across row lineage, temporal proof, layer manifest, and build preimage. Add mutation tests at each boundary.

### W04DC-P1-007 — Coverage/applicability states are neither provable nor fully representable

Coverage validation at `wyscout_data.py:939-1033` automatically allows zero denominators for coordinate and possession dimensions to become `not_applicable_zero_denominator` without carrying the authority proof required by R21. A probe using an unproven optional zero denominator was accepted.

At the same time, the declared `authority_missing` and `failed` enum states cannot satisfy the current denominator/status validator, so the exact hard-failure cases cannot be represented. This creates both a false-readiness path and an unusable failure path. Require explicit authority evidence for each authority-proven zero denominator, permit the exact missing/failed states with their required evidence, and test the complete six-dimension state matrix.

### W04DC-P1-008 — Layer manifests do not close the build and parent chain

The manifest models at `wyscout_data.py:1533-1664` do not establish the exact immutable layer graph required by the accepted authorities:

- the digest embedded in a manifest filename need not equal `build_id`;
- a manifest can have zero entries;
- a parent manifest path such as `../escape` is accepted;
- parent build ID and parent path are not bound to each other or to the exact role/path convention;
- entry schema roles and partition values are not exhaustively constrained;
- Gold does not bind the exact feature, dependency, and temporal evidence chain.

All reproduced constructor probes passed. Enforce canonical, safe relative paths; filename/build equality; non-empty exact-layer entries; ordered parent identity; exact schema roles; exact partition grammar; and the Gold authority lineage. Add negative tests for every mutation above.

### W04DC-P1-009 — Gold aggregates are not reconciled to their contributing facts

Gold validation at `wyscout_data.py:1257-1326` checks that contributing keys are sorted and unique and that feature component counts do not exceed action count. It does not require contributing keys to identify the Gold player/competition/season/schema, and it does not reconcile feature counts to the selected Silver facts.

Independent probes accepted:

- a Gold row for one player with an unrelated player-match key and arbitrary schema digest;
- `action_count = 999` with only one contributing fact key.

Bind contributing keys to the Gold grouping dimensions and frozen schema, and require deterministic reconciliation of the four supported R21 features to the selected Silver fact set. Add mismatch tests for identity, authority digest, fact count, action count, and every supported feature.

### W04DC-P1-010 — Source, provenance, and rights evidence remains structurally incomplete

The exported models do not yet form a closed proof from the exact source row to each layer:

- `BronzeKnownRecord` at `wyscout_data.py:602-620` omits the required measured raw paths/types, admission decision, source availability, and rights evidence;
- `BronzeRejectedRecord` at `wyscout_data.py:623-647` omits equivalent lineage, classification, and authority-clock evidence;
- generic Silver/Gold lineage can name an unrelated source family or row;
- `source_record_ordinal` is not bounded by the accepted source manifest row count, permitting phantom source rows;
- rights/export/attribution conditions are represented by a digest or broad enum but are not tied to the accepted source authority and downstream manifestation.

Define the minimum evidence-bearing fields necessary to prove the already-approved source, rights, admission, and row-lineage relationships. Enforce the manifest row bound and exact source-family identity. Add direct constructor and cross-layer mutation tests. This is a closure correction within the frozen architecture, not a request to add a new provider or product feature.

## Required bounded rework

Return the producer packet for a bounded R2 correction that:

1. closes all ten public-constructor invariants above;
2. replaces the stale authority clocks in the focused fixture with the exact accepted clocks;
3. adds adversarial direct-constructor and cross-authority composability tests reproducing every finding;
4. regenerates producer evidence and fixed-input digests;
5. reruns the complete prescribed verification set and returns the result for a fresh independent review.

The correction must remain limited to the executable W04 data contracts, their focused tests, and their evidence. No Bronze/Silver/Gold ingestion execution or product work should use these models until the fresh review passes.

## Scope and independence confirmation

- No implementation or test file was modified.
- No Git operation was performed.
- No dependency, environment, provider acquisition, hosted service, deployment, or external endpoint was created or changed.
- The review did not approve its own work.
- The findings do not demonstrate a contradiction in R20/R21 and do not justify another architecture revision.

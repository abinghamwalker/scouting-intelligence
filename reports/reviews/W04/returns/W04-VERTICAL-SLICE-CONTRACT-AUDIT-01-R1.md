# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-CONTRACT-AUDIT-01`
- objective: Audit the existing contract/build path for the smallest honest
  one-match/one-player raw-to-Gold W04 slice.

## Files changed

- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-CONTRACT-AUDIT-01-R1.md`

## Summary

### Verdict

**BLOCKED for final product publication; otherwise PASS for implementation that
stops before final product/manifest/receipt writes.** The checked product graph is
composable without new features, provider access, dependencies, architecture,
cloud, containers or deployment. Three existing publication gaps must not be
filled ad hoc:

1. Receipt paths/owners are modeled, but there is no executable content model for
   `RebuildInvocationReceipt` or `TemporalBoundaryReceipt`.
2. No accepted executable pre-build projection/code-environment launcher exists to
   derive the non-placeholder R20 `build_id`.
3. `parquet_bytes` does not match R20's frozen Parquet settings, and
   `GuardedStorage.write_bytes` adds a `<product>.manifest.json` sidecar outside the
   frozen W04 product path set.

These are bounded approved-W04 implementation/authority gaps, not evidence for a
broader architecture revision.

### Exact producer contract

Use these public boundaries in order:

1. `load_source_completion_index` (`wyscout_completion_index.py:899`), whole-file
   source SHA/size/row verification, `completion_action_evidence` (`:489`) for every
   physical ordinal, then `validate_checked_match_population` (`:1165`) with every
   indexed period of exactly one match in canonical order.
2. Bronze: `canonicalize_json_value` (`wyscout_data.py:188`),
   `WyscoutSourceRecordEnvelope` (`:410`), `BronzeKnownRecord` (`:768`), and required
   `BronzeRejectedField` (`:984`). Bronze has no checked builder; its serializer
   must itself prove exact equality to the checked match population.
3. Silver: `build_checked_silver_action`,
   `build_checked_silver_possession`,
   `build_checked_silver_player_match_fact`, then
   `build_checked_layer_manifest` (public bindings at
   `wyscout_completion_index.py:1685-1818`).
4. Gold: `build_checked_gold_player_window`, then
   `build_checked_layer_manifest`.
5. Immediately at every Silver/Gold row or manifest write boundary, call
   `require_checked_product(handle, expected_type=ExactModel)` (`:1222`) and
   serialize only that exact return. A direct model, copied dump, rehydrated value,
   Boolean/count/digest witness or detached handle is not authority.

Exact relevant models and fields are:

- `BronzeKnownRecord`: build/tenant/source row/raw value/raw digest/measured fields/
  admission/classification/lineage.
- `SilverAction` (`wyscout_data.py:1485`): shared build/tenant/index/source rows/
  lineage plus action/source/match/competition/player/team IDs, strict event and
  subevent IDs, period/order/Decimal clock/scale, tags, positions, predicate and
  eligibility state. The checked builder alone inserts the complete authentic
  `possession_period_sequence`. String subevents stay unmapped (`None`) and raw;
  never coerce them.
- `SilverPossession` (`:1658`): possession/match/period/team plus exact checked
  Actions. The checked builder derives source rows, actions, IDs and order bounds.
- `SilverPlayerMatchFact` (`:2179`): source/match/player/competition/season/team,
  match start, evidence collections, the three Silver counts, uncertainty,
  null minutes/per90 false, coverage/applicability and temporal proof. The checked
  builder derives source rows and all contributors and proves complete row-player
  match Actions.
- `GoldPlayerWindow` (`:2597`): player/competition/season/neutral role/window/cutoff,
  lineage/feature schema/temporal proof/coverage/applicability, Facts and feature
  vector. The checked builder derives source rows, Facts and Fact keys.
- `GoldFeatureValues` (`:2580`) is closed to exactly `action_count`,
  `coordinate_known_action_count`, `match_count`, and
  `resolved_possession_action_count`.
- Every row uses exact accepted source classification/authority, four authority
  references/clocks, the accepted completion-index digest, sorted physical source
  rows, and the five dependencies in `dependency_sort_key` order with recomputed
  `dependency_lineage_hash`. `W04SemanticTemporalProof` (`:2099`) requires every
  source/dependency/authority clock strictly before cutoff.

### Smallest honest artifact population

- Scope: frozen `archive-members/events_England.json`; one complete indexed match;
  all 1,768 source actions (901 1H, 867 2H); one player; one window; four features.
  Do not claim complete England, provider, source-manifest or W04 coverage.
- Bronze: all 1,768 known action rows plus every required rejected-field row from
  the accepted field/R21 route. Two target rows cannot honestly back a whole-match
  completion capability.
- Silver Action: selected player's two Actions plus every Action in each complete
  resolved possession group intersecting them.
- Silver Possession: exactly those complete resolved groups.
- Silver Fact: one checked player-match Fact, no invented lineup/minutes/per90.
- Gold: one checked player-window row with the source-audited vector `(2,2,1,2)`
  and one Fact. Preserve and validate the two target Actions' accepted positions;
  do not reuse the older contract test's deliberately empty-position payload.
- Manifests: Bronze actual non-empty files; Silver Action/Possession/Fact only;
  Gold PlayerWindow only. Pass every materialized checked Silver product to its
  checked manifest, and the checked Gold to its checked manifest. Omit fake/empty
  entity or lineup Parquet.

### Exact paths/manifests/serialization

Use `WyscoutProductPath` (`wyscout_data.py:2924`) for:

- Bronze known/rejected-field Action paths under the frozen
  `build_id=<sha>/.../source_sha256=<England-sha>/part-00000.parquet` templates;
- Silver Action/Possession/PlayerMatchFact with
  `source_partition=england/part-00000.parquet`;
- one Gold PlayerWindow path with lowercase UUIDs and UTC
  `YYYYMMDDTHHMMSSffffffZ`; and
- exact same-build Bronze/Silver/Gold manifest paths.

Ownership is fixed to `bronze.py`, `actions.py`, `possessions.py`,
`player_match.py`, `silver_manifest.py`, `gold.py`, `rebuild.py`, and
`temporal_boundary.py`. `LayerManifestEntry` (`:2995`) requires exact owner/role,
positive rows/bytes, semantic and physical SHA-256, sorted parent paths and exact
partition values, restricted rights and completion. Silver parents are same-build
Bronze product paths; Gold parents are same-build Silver paths. `LayerManifest`
(`:3093`) requires exact source/index/tenant/rights/clocks/feature/dependency
bindings, sorted entries and exactly one preceding-layer manifest, and must itself
come through `build_checked_layer_manifest`.

R20 freezes Parquet v2.6, 65,536-row groups, zstd 9, data page 2.0, dictionary and
byte-stream split off, statistics on, page index off, microsecond timestamps without
truncation, stored schema, canonical primary-key order, and semantic digests over
schema plus length-framed ordered rows and parents. The generic
`src/scouting/storage/formats.py:66` differs (including statistics off), so it is
not accepted product-byte authority as written. A bounded guarded, sidecar-free,
staged atomic product publisher is also required before final writes.

### Build/receipt rule and producer checklist

R20's sole build algorithm is one SHA-256 of canonical
`w04-wyscout-pre-build-projection-v1`, with exactly its 25 stable fields and no
`build_id`/run/path/host/output values. Only after hashing may the 24 non-schema
fields be copied and `build_id` inserted into the exact 25-key
`w04-rebuild-invocation-v1`. `run_id` is one operational lowercase UUIDv4. Paths:

- `runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json`
- `runs/w04/wyscout-rebuild/<build_id>/<run_id>/boundary/<sha256-of-exact-gold-relative-path>.temporal-boundary-receipt.json`

The current code validates these path roles only; the schema-bundle preimage labels
their content surfaces `CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`,
and the required launcher/admission/rebuild scripts do not exist. Therefore:

1. implement/test the exact in-memory Bronze-to-Gold checked graph and deterministic
   row projections without final writes;
2. separately close and independently review the approved build, receipt-content,
   exact Parquet and guarded publication surfaces;
3. only then publish, build checked manifests, issue receipts and perform two
   rebuilds requiring equal build ID, paths, semantics and physical product/
   manifest digests (only operational run/receipt values may differ).

## Tests run

- complete reads of all `read_first` files: exit `0`; all authorities inspected.
- `uv run python -c <model/signature introspection>`: exit `0`; exact fields and
  public signatures confirmed, including absence of receipt-content models.
- bounded `rg`/`sed` review of R20 and real checked-path tests: exit `0`; confirmed
  the 25-field one-hash build rule and checked construction path. The parallel
  source audit supplied the exact raw-evidence vector `(2,2,1,2)`.

## Artifacts/evidence

- this audit: `reports/reviews/W04/returns/W04-VERTICAL-SLICE-CONTRACT-AUDIT-01-R1.md`
- accepted completion index SHA-256:
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`

## Risks

- P1: arbitrary build/receipt bytes would bypass accepted authority.
- P1: generic Parquet/sidecar behavior conflicts with frozen byte/path closure.
- P1: partial Bronze behind whole-match capability would overclaim completeness.
- P2: checked graph validity does not grant wider population completeness.

## Follow-up items

- issue a serial bounded correction/implementation packet for the already-approved
  build, receipt-content, exact Parquet and guarded publication surfaces; until it
  passes, product work must stop before final artifact/manifest/receipt writes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

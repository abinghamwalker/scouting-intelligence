# W04 schema-closure R5 acceptance oracle R1

- Date: 2026-08-01
- Task: `W04-WYSCOUT-SCHEMA-CLOSURE-R5-ACCEPTANCE-ORACLE-01-R1`
- Status: **EXPECTED VALUES COMPLETE — NO CANDIDATE VERDICT**
- Boundary: implementation-independent, report-only expected values

Neither `src/scouting/contracts/wyscout_schema.py` nor
`tests/contracts/test_w04_wyscout_schema_closure.py` was read, imported, executed or
hashed. No storage implementation or storage test was inspected.

## 1. Frozen-input readback

Every packet-fixed binding reproduced before derivation.

| Artifact | Required and observed SHA-256 |
| --- | --- |
| task packet | `276c6b970d376e3ff37c454e392164f291b1abc219e463911526dab4efaa8c89` |
| `src/scouting/contracts/primitives.py` | `ee3fa657174cc949a5b7a389d60560abbdef596dbab913060a70516f0b988691` |
| `src/scouting/contracts/evidence.py` | `ff771aee3c9e23eb9ebe7e3919f75557f919919b232f752c4f708abf6c7cce10` |
| `src/scouting/contracts/wyscout_data.py` | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` |
| `src/scouting/contracts/wyscout_build.py` | `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16` |
| `tests/contracts/test_wyscout_data_contracts.py` | `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e` |
| R3 acceptance oracle | `de4a4119cf1a1158156d55f49f26bae8c1c08b46d36f93bb6c6afe102fdd145f` |
| R4 independent review | `676f911ad8e2ad4bff9900e7b53b7d57408a69b51f35f3dc61dc865666abed65` |
| R4 master verification | `956c6463ba34db257cae64c20e3924e0796672a447938af0d4ad9dabbab85a0b` |

The build/product and season/lineup authority JSON bytes were also read in full.
This oracle refers to their already-frozen comparison corpora as C1-C11 exactly as
defined in the fixed R3 oracle. It does not restate, replace or mutate those bytes.

## 2. Independent reachability method and result

The roots are the frozen ordered roster from the runtime census/readiness audit:
`BronzeKnownRecord`, `BronzeRejectedRecord`, `BronzeRejectedField`,
`SilverCompetition`, `SilverTeam`, `SilverPlayer`, `SilverMatch`, `SilverAction`,
`SilverLineupStint`, `SilverPossession`, `SilverPlayerMatchFact`,
`GoldPlayerWindow`, `LayerManifest`, `TemporalBoundaryReceipt`,
`RebuildInvocationReceipt`, `EntrypointSourceResult`, `ComponentProofResult`,
`PreBuildAdmissionResult`, `RebuildReceiptSummary`, `LayerManifestSummary`,
`FinalRecheckResult`, `PostBuildIdRebuildResult`, and `ChildResultEnvelope`.

For each root I generated Pydantic's serialization schema from the frozen runtime
contract and followed its ordered `$defs` references, resolving model names only in
`wyscout_data` and `wyscout_build`. This is necessary for the recursive
`CanonicalJsonValue` alias: a direct `model_fields` annotation walk yields 54
models/55 validators because Pydantic's resolved recursive annotation does not
enumerate all seven arm wrappers. The actual serialization closure adds exactly
`CanonicalJsonArray`, `CanonicalJsonBoolean`, `CanonicalJsonInteger`,
`CanonicalJsonNull`, `CanonicalJsonNumber`, and `CanonicalJsonString`; only
`CanonicalJsonNumber` adds a validator. The exact result is therefore **60 reachable
models and 56 effective owner/validator bindings**.

The ordered reachable-model roster is:

```text
BronzeKnownRecord, CanonicalJsonArray, CanonicalJsonBoolean,
CanonicalJsonInteger, CanonicalJsonMember, CanonicalJsonNull,
CanonicalJsonNumber, CanonicalJsonObject, CanonicalJsonString,
DependencyLineage, EvidenceDependency, RawFieldMeasurement,
SourceUseClassification, TenantContext, WyscoutAuthorityClock,
WyscoutAuthorityReference, WyscoutRowLineage, WyscoutSourceAuthority,
WyscoutSourceRowReference, BronzeRejectedRecord, RawKindEvidence,
WyscoutRawSourceRowReference, BronzeRejectedField, SilverCompetition,
SilverTeam, SilverPlayer, SilverMatch, SilverAction, ActionPosition,
PossessionPeriodSequence, PossessionSequenceAction, SilverLineupStint,
NominalMinuteInterval, SilverPossession, SilverPlayerMatchFact, GoldCoverage,
GoldCoverageDimension, W04ApplicabilityAssessment, W04SemanticTemporalProof,
GoldPlayerWindow, GoldFeatureValues, LayerManifest, LayerManifestEntry,
ManifestPartitionValue, ParentLayerManifest, WyscoutProductPath,
TemporalBoundaryReceipt, RebuildInvocationReceipt, AuthorityRow,
BoundaryReceiptSummary, DependencyRow, LayerManifestSummary,
RebuildInvocation, EntrypointSourceResult, ComponentProofResult,
PreBuildAdmissionResult, RebuildReceiptSummary, FinalRecheckResult,
PostBuildIdRebuildResult, ChildResultEnvelope
```

`WindowIdentity`, `PreBuildProjection`, `WyscoutSourceRecordEnvelope`,
`ActionSubeventOutcome`, `_ProjectionCommon`, and `WyscoutProductRow` are not
reachable serialized definitions. Inherited validators are instead bound to each
reachable concrete owner: the product-row validator has nine bindings and the raw
source-row validator has the two correct concrete bindings.

## 3. Operand normalization and operation catalogue

An operand is a serialized top-level field of the effective owner. Operand order is
the first lexical read in the validator body after collapsing a nested read such as
`lineage.source_authority.tenant_context` to `lineage`. A whole-object helper input
remains the owning top-level operand; the operation catalogue below freezes the
helper's nested reads. `model_dump()` comparisons expand to all serialized fields in
model-field order. Method/property names such as `is_finite`, `as_tuple`, `split`,
`encode`, and `lower` are operations, not invented field paths.

The operation IDs in the comparison ledger have these exact meanings:

| IDs | Exact direct/composed operation and material helper closure |
| --- | --- |
| P01 | SHA-256 of `canonical_raw_json_bytes(raw_record)` equals both declared raw digests; source row occurs in lineage; `_top_level_measurements(raw_record)` equals `measured_raw_fields`; exact tenant, lineage tenant and C3 rights. |
| P02 | Every Unicode code point in `key` is outside `U+D800..U+DFFF`. |
| P03 | `value.is_finite()` is true. |
| P04 | Member keys are unique and exactly Unicode-lexically sorted. |
| P05 | Every `(dependency.kind, dependency.dependency_id)` pair is unique. |
| P06 | Prohibited use forces derived/internal/export false; required attribution forces non-null attribution text. |
| P07 | The clock triple equals the C3 row selected by kind and is ordered decided <= reviewed <= accepted. |
| P08 | The complete seven-field JSON dump equals the C3 data-authority row selected by kind. |
| P09 | C1 manifest/index values; exact ordered four C3 authorities and clocks; exact source authority; source physical keys sorted unique; `_validate_exact_dependency_lineage` enforces the exact C8 five-row order/content/hash. |
| P10 | Exact C1 manifest/release/acquisition/no-club tenant plus exact C3 restricted classification. |
| P11, P15 | C1 manifest ID; completion path selects exactly one C2 member; member digest equal; ordinal in `[0,row_count)`. P11 is the inherited body effective on the typed source row; P15 is the raw-row owner. |
| P12 | Typed `record_kind` equals the C2 member kind selected by completion path. |
| P13 | Recompute raw digest; exact tenant/rights/lineage tenant; at least one lineage row equals the raw reference on path/member digest/ordinal/raw digest. |
| P14 | Derive the five raw-kind states from presence and exact tagged value; reject known source-kind strings; classify other strings with `^[A-Za-z][A-Za-z0-9_-]{0,63}$`; exact canonical envelope; digest `SHA256(b"w04-raw-kind-v1\\x00" + UINT64_BE(len(envelope)) + envelope)`. |
| P16 | Source kind, tagged kind, raw-value digest, FIELD authority and C4 row agree. `action/$.subEventId` preserves/quarantines using C5/C6 and rejects an admitted integer pair; all other rows follow the exact registry decision/reason. Exact tenant/rights/source membership. |
| P17, P19, P21, P23, P25, P30, P33, P35, P41 | Exact no-club tenant; C1 index equals lineage; tenant equals lineage source authority; selected physical keys sorted unique and every selected row occurs in lineage. These are nine separate effective bindings. |
| P18, P20, P22 | Exactly one source row of respectively competition/team/player kind; strict positive source ID; canonical source UUID equals declared UUID. |
| P24 | Exactly one match row; source partition equals its C2 country; canonical match UUID; exactly two distinct team UUIDs in byte order. No season-population claim. |
| P26 | Exactly one action row; canonical action UUID/source ID/ordinal equality; finite nonnegative exact decimal128(22,18) seconds at declared scale; sorted-unique tags; strict C5 subevent relation; `_possession_predicate_state`; exact same-match/period C1-index sequence membership with all twelve evidence values equal; eligibility equals `_resolved_possession_groups`. |
| P27 | Both axes pass exact decimal128(22,18) capacity at lexical scale; bound flag is identity-equal to both axes lying in closed `[0,100]`; no clamping. |
| P28 | C1 index; count equals action length; same match/period; `action_order_key` sorted unique; action IDs and physical rows independently unique. Exact C7 population equality remains external E1. |
| P29 | Action source kind/ordinal; canonical action UUID; finite nonnegative seconds; sorted-unique tags. Its `action_order_key` is `(period_rank, seconds, ordinal, source_event_id)`. |
| P31 | Exactly one match source row. Open end requires right-censored and both derived bounds null. Closed end requires a start, not censored, and bounds `max(0,end.lower-start.upper)` / `max(0,end.upper-start.lower)`. C9 sole population remains external E2. |
| P32 | `upper == lower + 1`. |
| P34 | Actions unique and ordered by `(action_order_key, action_id.bytes)`; one equal complete sequence; exact one `_resolved_possession_groups` group for team; shared build/tenant/lineage/match/period and resolved eligibility; complete causal rows and derived IDs/first/last order. Equal-clock ambiguity is group-first and clears only the current group/buffer. |
| P36 | Exact C1 source; lineup/action/possession identities, canonical orders, scope and byte-semantic equality; evidence nonempty; per-period player actions equal the complete-sequence player subset; each eligible action occurs in exactly one possession and ineligible actions in none; source rows/counts/lineage/proof/cutoff/coverage/applicability recompute exactly. |
| P37 | Six dimension names in enum order; missing-dimension lexical set derives from non-complete states; overall coverage is the minimum. |
| P38 | Numerator <= denominator and reasons sorted unique. Authority missing/failed, positive-denominator exact precision-38 division, authority-proven coordinate/FIELD or possession/POSSESSION zero, unproven optional zero, and mandatory zero follow the disjoint frozen branches. |
| P39 | Reasons sorted unique; `W04_DATA_READY` has none; every other applicability state has at least one. |
| P40 | Exact C8 five dependencies and C1 index; exact C3 source/clocks; every bound clock before cutoff; watermark maximum and before cutoff; `valid_from=max(snapshot,watermark)`; singleton C1 manifest; C8 feature digest; both lineage hashes recompute. |
| P42 | Exact role context/version/state; half-open window; proof/lineage/source/clocks/feature equalities; fact keys sorted unique and exact; all facts share build/tenant/source/player/competition/season/lineage/proof and lie in window/before cutoff; source union, four feature sums, coverage and applicability recompute. C9 population remains external E2. |
| P43 | Coordinate-known and resolved-possession action counts are each <= action count. |
| P44 | Manifest path/layer/build, C1 source/index, no-club tenant, C3 rights/clocks, C8 feature/lineage and hash exact; entries sorted unique and same layer/build; exact Bronze/Silver/Gold parent rule. |
| P45 | Serializer is sole path-role owner; schema role equals path role; partition rows equal sorted-unique path segments; C3 rights; parent paths sorted unique; exact preceding-layer/same-build parent rule. |
| P46 | Parent layer is not Gold; exact same-build `data/manifests/wyscout/v5/<layer>/<build>.manifest.json`. |
| P47 | NFC relative path full-matches the exact role pattern; every UUID and UTC token canonically round-trips. |
| P48 | Safe Gold manifest/product paths; exact same-build Gold manifest path and one-match product pattern; SHA-256 of product-path UTF-8 equals declared relative-path digest. |
| P49 | Build equals invocation; start <= completion; exact Bronze/Silver/Gold same-build layer summaries; exactly one boundary at the deterministic build/run/product-path-digest path. |
| P50 | Complete seven-field dump equals the C3 five-row build authority selected by kind. |
| P51 | Parsed observed instant <= parsed available instant. |
| P52 | Exact C3 five authority rows and C8 five dependency rows; code-manifest UUID binds digest; v1 product/schema placeholders forbidden; exact C10 post-hash order; inverse to the sole pre-build projection reproduces `build_id`. |
| P53 | Relative path equals the final argv token selected by child role. |
| P54 | Admission prefix/UUID; exactly the ordered twenty C10 component keys; component proof hash; strict base64url manifest decode/digest/closed roster; schema/repository/environment equality; environment digest and each named component proof recompute. |
| P55 | Rebuild prefix and receipt path derive from build/run; exact three layer summaries and paths; final recheck build/run/receipt digest; layer-set digest recomputed from all summaries. |
| P56 | Entrypoint role equals child role; admission/rebuild arm and payload kind are disjoint; repository/environment/entrypoint equalities; ordered argv SHA-256 equals the exact C10 argv. |

All element-level reads named above are part of their owning collection operand; no
caller-supplied Boolean, digest, count or witness replaces a composed operation.

Every P01-P56 row is classified `RUNTIME_MODEL_VALIDATOR`. Its ordered `operands`
are the direct owner fields; its P operation includes the material same-contract
helper/property closure described above. The separately classified
`EXTERNAL_GUARDED_OR_COMPOSED_AUTHORITY` predicates are:

| ID | Exact external operation/operands |
| --- | --- |
| E1 | Guard-read the fixed C7 index path and verify content address, C1 source manifest/member, canonical ordering/uniqueness, aggregate count and exact supplied sequence/set equality for match 2499719: 1H `901` / `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`, 2H `867` / `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`; fail missing/additional/duplicate/reordered/stale/cross-period or caller-only witnesses. |
| E2 | Strict source season `181150` reproduces `4696aa1f-b512-5d18-af79-33cf031455cf`; guard exact sole lineup source/member/ordinal/raw digest and UUIDs, `[82,83)`, open end/bounds/elapsed, right-censored/per90/suppression state; fail population or ordinal substitution. |
| E3 | Issue checked Silver/Gold only after E1 exact equality; include other-player causal actions used by possession semantics. Runtime consistency/count/digest/Boolean alone is insufficient. |
| E4 | Exact C3 five-authority/C8 five-dependency C10 25-key preimage, one SHA path and inverse replacing only schema-version/build-ID; reject a sixth row/26th field/key reorder/v1 placeholder/second hash. |
| E5 | Guard-read and closed-schema-validate all three manifests; reproduce physical digest/size; sole semantic preimage is exact keys `layer_manifest,semantic_schema_version`, complete parsed manifest, literal `w04-wyscout-layer-manifest-semantic-v1`, R20 canonical bytes without LF. |
| E6 | Bronze parent empty, Silver exactly Bronze, Gold exactly Silver, same build; Gold manifest yields exactly one ordered product and identical boundary population; reopen and bind all product/boundary evidence. |
| E7 | Exact three summaries/one boundary and `started_at<=checked_at<=completed_at`; downstream rehash cannot repair a semantic substitution; child role/payload/argv/environment/repository bind exactly. |
| E8 | Exactly 23 roots, 12 accepted-descriptor Parquet / 11 explicit JSON-only; earlier-only dependencies; schema only from accepted descriptor; strict inverse before equality; exactly the authorized tagged-JSON and canonical-Decimal paths. |

E1-E8 are not emitted as model validators and do not increase the 56-row runtime
ledger.

## 4. Canonical 56-binding comparison ledger

The comparison bytes are the exact UTF-8 JSON Lines between the markers below,
including one LF after every row and no other bytes. Object keys use the exact order
`constants,declared_owner,operation,operands,owner,validator`, compact separators
and `ensure_ascii=False`. The SHA-256 is recorded after the block.
`declared_owner` distinguishes inherited validators; `owner` is the
reachable effective binding. Literal constants prefixed `L:` and C1-C11 references
compose with the exact operation catalogue above.

<!-- BEGIN R5_RUNTIME_PREDICATE_LEDGER_JSONL -->
```jsonl
{"constants":["C1","C3"],"declared_owner":"BronzeKnownRecord","operation":"P01","operands":["raw_record","raw_record_sha256","source_row","lineage","measured_raw_fields","tenant_context","classification"],"owner":"BronzeKnownRecord","validator":"raw_record_is_preserved_once"}
{"constants":["L:U+D800..U+DFFF"],"declared_owner":"CanonicalJsonMember","operation":"P02","operands":["key"],"owner":"CanonicalJsonMember","validator":"key_is_unicode_scalar_text"}
{"constants":["L:finite Decimal"],"declared_owner":"CanonicalJsonNumber","operation":"P03","operands":["value"],"owner":"CanonicalJsonNumber","validator":"number_is_finite"}
{"constants":["L:Unicode lexical sort"],"declared_owner":"CanonicalJsonObject","operation":"P04","operands":["value"],"owner":"CanonicalJsonObject","validator":"members_are_unique_and_sorted"}
{"constants":["C8"],"declared_owner":"DependencyLineage","operation":"P05","operands":["dependencies"],"owner":"DependencyLineage","validator":"dependencies_are_unique"}
{"constants":["C3"],"declared_owner":"SourceUseClassification","operation":"P06","operands":["use_class","derived_data_allowed","internal_review_allowed","export_allowed","attribution_required","attribution_text"],"owner":"SourceUseClassification","validator":"prohibit_unlicensed_use"}
{"constants":["C3"],"declared_owner":"WyscoutAuthorityClock","operation":"P07","operands":["decided_at","reviewed_at","accepted_at","authority_kind"],"owner":"WyscoutAuthorityClock","validator":"clocks_are_the_accepted_authority_clocks"}
{"constants":["C3"],"declared_owner":"WyscoutAuthorityReference","operation":"P08","operands":["acceptance_id","acceptance_sha256","authority_kind","candidate_id","candidate_sha256","review_id","review_sha256"],"owner":"WyscoutAuthorityReference","validator":"reference_is_the_accepted_authority"}
{"constants":["C1","C3","C8"],"declared_owner":"WyscoutRowLineage","operation":"P09","operands":["source_manifest_id","source_manifest_sha256","source_completion_index_sha256","authority_references","authority_clocks","source_authority","source_rows","dependency_lineage"],"owner":"WyscoutRowLineage","validator":"lineage_is_closed"}
{"constants":["C1","C3"],"declared_owner":"WyscoutSourceAuthority","operation":"P10","operands":["source_manifest_id","source_manifest_sha256","tenant_context","available_at","acquired_at","classification"],"owner":"WyscoutSourceAuthority","validator":"source_authority_is_exact"}
{"constants":["C1","C2"],"declared_owner":"WyscoutRawSourceRowReference","operation":"P11","operands":["source_manifest_id","completion_relative_path","source_sha256","source_record_ordinal"],"owner":"WyscoutSourceRowReference","validator":"source_row_is_manifested"}
{"constants":["C2"],"declared_owner":"WyscoutSourceRowReference","operation":"P12","operands":["completion_relative_path","record_kind"],"owner":"WyscoutSourceRowReference","validator":"record_kind_matches_completion_path"}
{"constants":["C1","C3"],"declared_owner":"BronzeRejectedRecord","operation":"P13","operands":["raw_record_sha256","raw_record","tenant_context","classification","lineage","source_row"],"owner":"BronzeRejectedRecord","validator":"rejected_record_is_closed"}
{"constants":["L:w04-raw-kind-v1\\x00","L:uint64-be","L:^[A-Za-z][A-Za-z0-9_-]{0,63}$"],"declared_owner":"RawKindEvidence","operation":"P14","operands":["value_present","value","raw_kind_state","envelope_bytes","raw_kind_sha256"],"owner":"RawKindEvidence","validator":"evidence_matches_state_and_framed_digest"}
{"constants":["C1","C2"],"declared_owner":"WyscoutRawSourceRowReference","operation":"P15","operands":["source_manifest_id","completion_relative_path","source_sha256","source_record_ordinal"],"owner":"WyscoutRawSourceRowReference","validator":"source_row_is_manifested"}
{"constants":["C1","C3","C4","C5","C6"],"declared_owner":"BronzeRejectedField","operation":"P16","operands":["source_row","record_kind","original_value","measured_json_type","original_value_sha256","field_authority","json_path","decision","reason_code","action_event_taxonomy_id","classification","tenant_context","lineage"],"owner":"BronzeRejectedField","validator":"rejected_value_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P17","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverCompetition","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(competition)"],"declared_owner":"SilverCompetition","operation":"P18","operands":["source_rows","competition_id","competition_source_id"],"owner":"SilverCompetition","validator":"competition_identity_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P19","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverTeam","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(team)"],"declared_owner":"SilverTeam","operation":"P20","operands":["source_rows","team_id","team_source_id"],"owner":"SilverTeam","validator":"team_identity_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P21","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPlayer","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(player)"],"declared_owner":"SilverPlayer","operation":"P22","operands":["source_rows","player_id","player_source_id"],"owner":"SilverPlayer","validator":"player_identity_is_exact_and_nonzero"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P23","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverMatch","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C2","L:canonical_source_uuid(match)","L:UUID.bytes sort"],"declared_owner":"SilverMatch","operation":"P24","operands":["source_rows","source_partition","match_id","match_source_id","team_ids"],"owner":"SilverMatch","validator":"match_identity_and_teams_are_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P25","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverAction","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C5","C6","L:decimal128(22,18)"],"declared_owner":"SilverAction","operation":"P26","operands":["source_rows","action_id","action_source_id","source_event_record_id","source_record_ordinal","period_elapsed_seconds","event_sec_source_scale","action_tag_ids","action_subevent_taxonomy_id","action_event_taxonomy_id","team_id","possession_predicate_state","possession_period_sequence","match_id","action_period_code","lineage","player_id","period_rank","possession_eligibility_state"],"owner":"SilverAction","validator":"action_is_strict_and_orderable"}
{"constants":["L:decimal128(22,18)","L:[0,100]"],"declared_owner":"ActionPosition","operation":"P27","operands":["x","y","within_accepted_bounds"],"owner":"ActionPosition","validator":"bound_flag_preserves_anomalies_without_clamping"}
{"constants":["C1"],"declared_owner":"PossessionPeriodSequence","operation":"P28","operands":["source_completion_index_sha256","period_action_count","actions","match_id","action_period_code"],"owner":"PossessionPeriodSequence","validator":"period_sequence_is_complete_unique_and_ordered"}
{"constants":["L:canonical_source_uuid(action)","L:canonical action order"],"declared_owner":"PossessionSequenceAction","operation":"P29","operands":["source_row","source_record_ordinal","action_id","source_event_record_id","period_elapsed_seconds","action_tag_ids"],"owner":"PossessionSequenceAction","validator":"sequence_action_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P30","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverLineupStint","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:half-open nominal minute"],"declared_owner":"SilverLineupStint","operation":"P31","operands":["source_rows","start_interval","end_interval","right_censored","lower_bound_minutes","upper_bound_minutes"],"owner":"SilverLineupStint","validator":"stint_bounds_are_interval_derived"}
{"constants":["L:upper=lower+1"],"declared_owner":"NominalMinuteInterval","operation":"P32","operands":["upper","lower"],"owner":"NominalMinuteInterval","validator":"interval_is_one_nominal_minute"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P33","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPossession","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C5","C6","L:equal-clock group-first"],"declared_owner":"SilverPossession","operation":"P34","operands":["contributing_actions","team_id","build_id","tenant_context","lineage","match_id","action_period_code","source_rows","action_ids","first_action_order","last_action_order"],"owner":"SilverPossession","validator":"possession_is_one_ordered_same_period_sequence"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P35","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPlayerMatchFact","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C8","L:fact derivations"],"declared_owner":"SilverPlayerMatchFact","operation":"P36","operands":["source_manifest_id","contributing_lineup_stints","build_id","tenant_context","lineage","match_id","player_id","match_team_id","lineup_evidence_present","contributing_actions","competition_id","contributing_possessions","source_rows","action_count","coordinate_known_action_count","resolved_possession_action_count","temporal_proof","match_start_utc","coverage","right_censored_or_uncertain","applicability"],"owner":"SilverPlayerMatchFact","validator":"player_match_key_and_state_are_exact"}
{"constants":["L:six CoverageDimensionName values"],"declared_owner":"GoldCoverage","operation":"P37","operands":["dimensions","missing_dimensions","coverage_overall"],"owner":"GoldCoverage","validator":"six_dimensions_are_exact"}
{"constants":["C3","L:precision-38 exact division"],"declared_owner":"GoldCoverageDimension","operation":"P38","operands":["numerator","denominator","reason_codes","state","coverage","zero_denominator_authority","name"],"owner":"GoldCoverageDimension","validator":"coverage_is_exact"}
{"constants":["L:W04_DATA_READY"],"declared_owner":"W04ApplicabilityAssessment","operation":"P39","operands":["reason_codes","state"],"owner":"W04ApplicabilityAssessment","validator":"reasons_are_sorted_unique"}
{"constants":["C1","C3","C8","C10"],"declared_owner":"W04SemanticTemporalProof","operation":"P40","operands":["dependency_lineage","source_completion_index_sha256","source_authority","authority_clocks","feature_cutoff_ts","available_at_watermark","valid_from_ts","snapshot_as_of_ts","dependency_lineage_hash","source_manifest_ids","feature_schema_hash"],"owner":"W04SemanticTemporalProof","validator":"proof_has_exact_five_strict_dependencies"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P41","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"GoldPlayerWindow","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C8","C10","L:four-feature sums"],"declared_owner":"GoldPlayerWindow","operation":"P42","operands":["role_context_id","role_context_version","role_context_state","window_start_utc","window_end_utc","feature_cutoff_ts","temporal_proof","dependency_lineage_hash","lineage","feature_schema_hash","contributing_player_match_facts","contributing_player_match_keys","build_id","tenant_context","player_id","competition_id","season_id","source_rows","features","coverage","applicability"],"owner":"GoldPlayerWindow","validator":"gold_key_and_feature_state_are_exact"}
{"constants":["L:component<=action"],"declared_owner":"GoldFeatureValues","operation":"P43","operands":["coordinate_known_action_count","action_count","resolved_possession_action_count"],"owner":"GoldFeatureValues","validator":"component_counts_cannot_exceed_actions"}
{"constants":["C1","C3","C8","C10"],"declared_owner":"LayerManifest","operation":"P44","operands":["manifest_path","layer","source_manifest_id","source_manifest_sha256","source_completion_index_sha256","build_id","tenant_context","classification","source_available_at","source_acquired_at","authority_clocks","feature_schema_hash","dependency_lineage","dependency_lineage_hash","entries","parent_layer_manifests"],"owner":"LayerManifest","validator":"layer_order_and_entries_are_exact"}
{"constants":["C3","C10"],"declared_owner":"LayerManifestEntry","operation":"P45","operands":["serializer","path","schema_role","partition_values","classification","ordered_parent_paths"],"owner":"LayerManifestEntry","validator":"entry_binds_owner_rights_and_partition_order"}
{"constants":["C10"],"declared_owner":"ParentLayerManifest","operation":"P46","operands":["layer","build_id","relative_path"],"owner":"ParentLayerManifest","validator":"parent_path_is_exact_and_safe"}
{"constants":["C10","L:NFC","L:canonical UUID/UTC"],"declared_owner":"WyscoutProductPath","operation":"P47","operands":["relative_path","path_role"],"owner":"WyscoutProductPath","validator":"path_is_the_exact_role_template"}
{"constants":["C10","L:SHA256(path UTF-8)"],"declared_owner":"TemporalBoundaryReceipt","operation":"P48","operands":["gold_manifest_relative_path","gold_product_relative_path","build_id","gold_relative_path_sha256"],"owner":"TemporalBoundaryReceipt","validator":"exact_paths"}
{"constants":["C10","C11"],"declared_owner":"RebuildInvocationReceipt","operation":"P49","operands":["build_id","rebuild_invocation","started_at","completed_at","layer_manifests","boundary_receipts","run_id"],"owner":"RebuildInvocationReceipt","validator":"exact_receipt"}
{"constants":["C3"],"declared_owner":"AuthorityRow","operation":"P50","operands":["acceptance_id","acceptance_sha256","authority_kind","candidate_id","candidate_sha256","review_id","review_sha256"],"owner":"AuthorityRow","validator":"equals_accepted_row"}
{"constants":["C8"],"declared_owner":"DependencyRow","operation":"P51","operands":["observed_at","available_at"],"owner":"DependencyRow","validator":"clocks_are_ordered"}
{"constants":["C3","C8","C10","L:single build hash"],"declared_owner":"RebuildInvocation","operation":"P52","operands":["authority_rows","dependency_rows","code_manifest_id","code_manifest_sha256","product_contract_digest","schema_bundle_digest","build_id"],"owner":"RebuildInvocation","validator":"exact_invocation"}
{"constants":["C10"],"declared_owner":"EntrypointSourceResult","operation":"P53","operands":["role","relative_path"],"owner":"EntrypointSourceResult","validator":"exact_role_path"}
{"constants":["C10","L:SHA256 canonical JSON","L:base64url"],"declared_owner":"PreBuildAdmissionResult","operation":"P54","operands":["admission_run_id","admission_prefix_relative_path","component_proofs","component_proofs_sha256","canonical_manifest_bytes_b64u","canonical_manifest_sha256","manifest_schema_version","repository_code_sha256","environment_digest"],"owner":"PreBuildAdmissionResult","validator":"exact_admission_result"}
{"constants":["C10","C11","L:SHA256 canonical JSON"],"declared_owner":"PostBuildIdRebuildResult","operation":"P55","operands":["build_id","run_id","rebuild_prefix_relative_path","rebuild_receipt","layer_manifests","final_recheck"],"owner":"PostBuildIdRebuildResult","validator":"exact_rebuild_result"}
{"constants":["C10","L:SHA256 ordered argv"],"declared_owner":"ChildResultEnvelope","operation":"P56","operands":["entrypoint_source","child_role","payload_kind","result","expected_repository_code_sha256","child_environment_sha256","ordered_argv_sha256"],"owner":"ChildResultEnvelope","validator":"exact_role_payload_binding"}
```
<!-- END R5_RUNTIME_PREDICATE_LEDGER_JSONL -->

Canonical ledger row count: `56`.

Canonical ledger SHA-256: `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`.

## 5. Exact corrected 29-row acceptance roster

Every row below must be created through ordinary strict Pydantic validation from a
complete input mapping. `model_construct`, fixture/row schema inference, mutation
after validation, or a caller schema/digest/callback is not acceptance evidence.
The root cardinality vector in frozen role order is exactly
`[2,5,7,1,1,1,1,3,2,2,2,2]`, whose sum is `29`.

### 5.1 Common construction equalities

These equalities apply before the variant-specific requirements:

1. Every raw logical value is a correctly tagged `CanonicalJsonValue` tree. Each
   raw digest is `SHA256(canonical_raw_json_bytes(value))`; Bronze-known equality
   extends to `source_row.raw_record_sha256`, and Bronze raw/source rows occur in
   their exact lineage.
2. `measured_raw_fields` is exactly `_top_level_measurements(raw_record)` in raw
   member order. Every `original_value_sha256` is recomputed from the tagged value.
3. Every lineage has exact C1 manifest/index bindings, C3 authorities/clocks/source
   authority, sorted-unique physical source rows, and exact C8 dependency lineage.
   Every product row's selected source rows are sorted unique and contained in that
   lineage. Tenant and classification are the fixed no-club/restricted objects.
4. Entity/action IDs use `canonical_source_uuid(kind, strict_positive_source_id)`.
   Season/lineup UUID reproduction and their sole population remain external E2,
   not a generic runtime-validator claim.
5. Every action has exactly one selected ACTION row. Its sequence entry is an exact
   twelve-field copy of the action evidence; sequence count equals length, match and
   period agree, order/action/physical identities are unique, and all sequence rows
   occur in lineage. E1 must separately prove the supplied complete period
   population before checked product issuance.
6. Fact and Gold rows recompute all counts, source unions, ordered keys, coverage,
   applicability, lineage/proof equality and four feature sums; no copied witness
   substitutes for those derivations.

### 5.2 Bronze known — exactly 2

- `BK-ALL-ARMS`: one top-level object whose recursively visited kind set is exactly
  all seven of `null, boolean, integer, number, string, array, object`. It must
  include a present tagged null and at least one array containing both a nested
  object and another array. A sufficient shape is a sorted-member object with one
  `allArms` array containing one value of every arm (with the object and array arms
  nontrivial) plus a scalar member; the exact top-level measurements and all three
  raw-digest equalities must be derived from that object.
- `BK-EMPTY-NESTED`: a different top-level member roster and different raw digest,
  containing both an empty array and an empty object below the top level. It must
  not reuse `BK-ALL-ARMS`'s raw object or merely reorder equal members. Its top-level
  measurements are independently recomputed.

Explicit matrix assertions: two unique canonical raw-object byte strings; first
recursive kind set equals the seven-arm set; second contains both empty composite
forms; both whole raw objects project as one tagged UTF-8 scalar.

### 5.3 Bronze rejected record — exactly 5

Use one row for each exact `RawKindState`, with five pairwise-distinct canonical raw
objects and independently derived raw/envelope digests:

| Variant | `value_present` / tagged value | Exact state | Required distinct shape property |
| --- | --- | --- | --- |
| `BRR-MISSING` | `false` / tagged null | `missing` | Kind member absent; another member proves the object is nonempty. |
| `BRR-NULL` | `true` / tagged null | `null` | Kind member present null. |
| `BRR-NONSTRING` | `true` / a non-string arm, e.g. integer | `non-string` | Add a different nested composite member. |
| `BRR-SAFE` | `true` / unknown string matching the safe regex | `string-unknown-safe` | Use a safe value not equal to any known `SourceRecordKind`. |
| `BRR-UNSAFE` | `true` / string failing the safe regex | `string-unsafe` | Use a lexically different unsafe value and object roster. |

For each row derive `envelope_bytes = _raw_kind_envelope_bytes(state,
value_present,value)` and
`raw_kind_sha256 = SHA256(b"w04-raw-kind-v1\x00" + UINT64_BE(len(envelope_bytes))
+ envelope_bytes)`. Assertions require five states, five canonical raw-object byte
strings, five independently correct raw digests, and no reused raw-object shape.

### 5.4 Bronze rejected field — exactly 7

All seven rows use an ACTION source row, `record_kind=action`,
`json_path=$.subEventId`, `decision=PRESERVE_UNMAPPED`, the exact FIELD authority,
and one respective direct tagged arm: null, boolean, integer, number, string, array,
object. `measured_json_type == original_value.kind` and the original-value digest is
recomputed. The exact C6 reason is, respectively:

```text
ACTION_SUBEVENT_NULL_UNMAPPED
ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER
ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY
ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED
ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED
ACTION_SUBEVENT_ARRAY_UNMAPPED
ACTION_SUBEVENT_OBJECT_UNMAPPED
```

The integer row supplies a strict integer not in C5 for its non-null strict integer
`action_event_taxonomy_id`; it must not accidentally form an admitted pair. Other
arms retain their exact raw value without coercion. Matrix assertions require each
of the seven arms and each reason exactly once.

### 5.5 Entity and match roots — exactly 1 each

- `SILVER_COMPETITION`, `SILVER_TEAM`, and `SILVER_PLAYER`: one positive provider
  ID, exactly one correctly typed source row, and the independently reproduced
  canonical UUID.
- `SILVER_MATCH`: exactly one MATCH row, path-derived country partition, canonical
  match UUID, two distinct team UUIDs sorted by `.bytes`, and otherwise generic
  contract-valid competition/season/time fields. The row must not be presented as
  runtime proof of season 181150; that equality is E2.

### 5.6 Silver action — exactly 3 corrected variants

The three rows must use distinct action/source identities and each must have an
internally exact sequence and lineage as specified in 5.1.

| Variant | Required exact state |
| --- | --- |
| `SA-NULL-UNMAPPED` | `competition_id`, `player_id`, `team_id`, `action_event_taxonomy_id`, and `action_subevent_taxonomy_id` are present fields with value null; `action_positions=()`; sorted tags; `_possession_predicate_state(None,None,None,tags)=PREDICATE_UNMAPPED`; no resolved group contains the action, so eligibility is `INELIGIBLE_UNMAPPED`; `period_elapsed_seconds=Decimal("0")` with `event_sec_source_scale=0`. |
| `SA-ONE-POSITION` | One in-bounds `ActionPosition`; non-null team; a C5-admitted CONTROL pair such as `(8,80)`; `PREDICATE_ADMITTED` and `ELIGIBLE_RESOLVED`; one-action resolved sequence; seconds retain lexical scale 18. |
| `SA-TWO-POSITION` | Two ordered in-bounds positions; non-null team; a C5-admitted RESTART pair such as `(3,30)`; `PREDICATE_ADMITTED` and `ELIGIBLE_RESOLVED`; one-action resolved sequence; seconds retain lexical scale 18. |

Across the latter two rows, one seconds value must reach decimal128(22,18)'s exact
capacity boundary, for example `Decimal("9999.999999999999999999")`, without
rounding. Position axes independently retain their supplied exact scale and bound
flags. Explicit assertions require position lengths `{0,1,2}`, source scales
including both `0` and `18`, a required-null/unmapped/ineligible row, and two
admitted/resolved rows. Pair `(2,24)` is not an acceptable substitute for the null
unmapped row because it is predicate-admitted.

### 5.7 Lineup, possession, fact and Gold — exactly 2 each

- `SILVER_LINEUP_STINT`: one authorized-style open row with start `[82,83)`, null
  end/bounds/elapsed, right-censored true, per90 false and fixed suppression; and one
  generic closed row with non-null start/end, right-censored false and both bounds
  recomputed by P31. Both select exactly one MATCH row. Only E2 can assert the sole
  authorized lineup population.
- `SILVER_POSSESSION`: one ordinary resolved control/restart group; one sequence in
  which an earlier completed resolved group remains after a later equal-clock group
  contains more than one controlling team. Each emitted possession equals one
  surviving `_resolved_possession_groups` group, uses the complete causal row union,
  and derives both heterogeneous order tuples exactly.
- `SILVER_PLAYER_MATCH_FACT`: one action-derived fact with nonempty actions,
  resolved possession evidence and an exact precision-38 `1/3` coverage dimension;
  one lineup-only/right-censored fact with empty action/possession sequences and an
  authority-proven zero-denominator coordinate or possession dimension. Counts,
  source rows, coverage, applicability and temporal equalities must be recomputed.
- `GOLD_PLAYER_WINDOW`: one aggregate containing the action-derived fact and the
  precision-38 `1/3` value both directly and nested; one aggregate propagating the
  lineup-only right-censoring and authority-proven zero denominator. Each uses an
  exact ordered fact-key roster, source-row union, four conservative feature sums,
  six-dimension coverage and derived applicability.

### 5.8 Required explicit matrix assertions

The acceptance test must fail if it only checks row counts. It must independently
assert the seven-arm/mixed/present-null and empty-composite Bronze-known properties;
five raw-kind states plus five unique raw shapes; seven rejected-field arms/reasons;
the exact three SilverAction tuples including null/unmapped/scale-zero; open/closed
lineup; ordinary/equal-clock possession; action-derived/lineup-only fact; and both
Gold propagation branches. All 29 logical rows must share one descriptor per root
regardless of empty/nonempty content, and every descriptor must come only from the
accepted root content, never any of these rows.

## 6. Executed evidence

All probes were read-only and imported only the frozen primitives/evidence/data/build
contracts:

| Probe | Exact result |
| --- | --- |
| Serialization-schema reachability plus lexical validator AST derivation, compared to the report ledger | PASS: `reachable_models=60`, `bindings=56`, inherited product bindings `9`, exact owner/name/declared-owner/operand equality |
| Ledger JSONL parse/order/hash | PASS: rows `56`, unique binding keys `56`, operations P01-P56, SHA-256 `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d` |
| Variant derivation using canonical JSON, raw-kind, subevent, possession and decimal helpers | PASS: seven Bronze-known arms/two shapes; five raw-kind states/five shapes; seven rejected-field arms/reasons; SilverAction states unmapped/admitted/admitted and scales 0/18; cardinality 29 |
| Final fixed-input `shasum -a 256` | PASS: packet and all eight fixed bindings reproduced; authority decisions remained `3da3baa...` and `3afdb281...` |
| `uv run python scripts/verify_local_only.py` | PASS: `25/25`, branch `main`, zero remotes |

The failed first draft of the variant probe used a wrong keyword for the public
two-positional-argument `classify_action_subevent` helper and raised `TypeError`
before any assertion or write. The corrected probe used the actual frozen signature
and passed; no expected value changed.

## 7. Oracle verdict and boundary

Verdict: **EXPECTED VALUES COMPLETE — NO CANDIDATE VERDICT**.

No contradiction requiring an architecture, root, logical field, semantic path,
feature, population, dependency, provider, publication or deployment change was
found. This report does not approve an R5 implementation. A separate producer must
compare to this expected ledger and variant roster; a fresh independent reviewer
and the master must then reproduce the result.

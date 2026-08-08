# W04 23-root runtime constraint census R2

- Task: `W04-WYSCOUT-23-ROOT-RUNTIME-CONSTRAINT-CENSUS-01-R2`
- Purpose: implementation-independent oracle over the frozen runtime contracts
- Scope: report only; no producer candidate, schema bytes, schema content digest, product, or aggregate was inspected or produced
- Supersession: this complete R2 census preserves R1 as failed/superseded evidence and
  supersedes R1 only for `CanonicalJsonValue` projection paths

## 1. R2 fixed-input readback

The R2 packet-fixed inputs were checked before analysis. Every observed SHA-256
equalled the packet binding.

| Input | Bound/observed SHA-256 |
| --- | --- |
| R1 packet | `d0025c2086a52722a4dcdabee7f6b192930df0c6e5dd97b8e14c5896e4451519` |
| R1 census | `6c8a5fd11d908727371a87b8f90032add5a3e80de1dba16daa785e805f149455` |
| R1 return | `545ac57ac471b8375dd1e01fc7a1150439c48fcf6c05ac6d6cc5d1181bbd6d9b` |
| logical-to-Arrow projection decision | `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1` |
| `formats.py` | `309ee2821913022c3ce82b713a53e74dd4ac3190af0047a621ba4ab2cd0f7209` |
| product-format tests | `0d6acf199d230257656f91c0c191c3bbef5dfb23c5cf49e6f731da4d57c8f317` |

The producer module, its tests, and its return were deliberately not opened.

## 2. Census notation and universal rules

In the field rosters below:

- `R` means the field is required at Pydantic construction time.
- `D(value)` means the runtime supplies that exact default when the field is absent.
- `T?` means the logical value may be null; it does not mean the field may be omitted.
- `tuple[T,...]` is a homogeneous sequence. A tuple with separately declared position
  types is a fixed tuple. `min=n`/`max=n` are Pydantic cardinality constraints.
- Every listed field participates in ordinary `model_dump(mode="json")` output,
  including fields supplied by defaults. Requiredness, defaulting, and logical
  nullability are three separate claims and must be represented separately.

All models are frozen and strict and reject additional fields. The Wyscout data
contracts inherit the repository `ContractModel`, which also validates defaults.
The standalone build contracts inherit their own strict, frozen,
`extra="forbid"` base. UUID objects are strict in Python mode and canonical UUID
strings on the JSON wire. `UtcInstant` is timezone-aware with offset exactly zero.
`Sha256Digest`/`Sha256` is a strict lowercase 64-hex string.

Primitive constraint aliases used below are:

| Alias | Exact obligation |
| --- | --- |
| `StrictPositiveInt` | exact `int`, excluding `bool`, `>=1` |
| `StrictNonNegativeInt` | exact `int`, excluding `bool`, `>=0` |
| `JsonInteger` | exact `int`, `0..9007199254740991` |
| `StrictDecimal` | exact `Decimal`; additional finiteness/capacity comes from the named validator |
| `ReasonCode` | strict string matching `^[A-Z][A-Z0-9_]{1,127}$` |
| `JsonPath` | strict string matching `^\$(?:\.[A-Za-z][A-Za-z0-9]*(?:\[\])?|\.\*)*$` |
| build `UtcInstant` | strict canonical UTC string `YYYY-MM-DDTHH:MM:SS[.ffffff]Z` |
| build `RelativePath` | strict nonempty `[A-Za-z0-9._=/-]+`, plus the path-safety predicates where invoked |
| `UuidV4` / `UuidV5` | canonical lowercase UUID with exact version nibble and RFC variant |

## 3. Exact 23-root order and serialized fields

The order is frozen. The annotation and field sequence below are the runtime
serialization order, including inherited fields.

### 3.1 Parquet roots 1–12

1. `BRONZE_KNOWN_RECORD` — `BronzeKnownRecord`

   `schema_version:Literal[w04-wyscout-bronze-known-record-v1] D(same); build_id:Sha256Digest R; tenant_context:TenantContext R; source_row:WyscoutSourceRowReference R; raw_record:CanonicalJsonObject R; raw_record_sha256:Sha256Digest R; measured_raw_fields:tuple[RawFieldMeasurement,...] R min=1; admission:Literal[ADMITTED_BY_EXACT_COMPLETION_PATH] D(same); classification:SourceUseClassification R; lineage:WyscoutRowLineage R`

2. `BRONZE_REJECTED_RECORD` — `BronzeRejectedRecord`

   `schema_version:Literal[w04-wyscout-bronze-rejected-record-v1] D(same); build_id:Sha256Digest R; tenant_context:TenantContext R; source_row:WyscoutRawSourceRowReference R; raw_record:CanonicalJsonObject R; raw_record_sha256:Sha256Digest R; raw_kind:RawKindEvidence R; rejection_code:Literal[UNKNOWN_RECORD_KIND] D(same); classification:SourceUseClassification R; lineage:WyscoutRowLineage R`

3. `BRONZE_REJECTED_FIELD` — `BronzeRejectedField`

   `schema_version:Literal[w04-wyscout-bronze-rejected-field-v1] D(same); build_id:Sha256Digest R; tenant_context:TenantContext R; source_row:WyscoutSourceRowReference R; record_kind:SourceRecordKind R; json_path:JsonPath R; original_value:CanonicalJsonValue R; original_value_sha256:Sha256Digest R; measured_json_type:CanonicalJsonKind R; action_event_taxonomy_id:StrictNonNegativeInt? D(null); decision:RejectedFieldDecision R; reason_code:ReasonCode R; field_authority:WyscoutAuthorityReference R; classification:SourceUseClassification R; lineage:WyscoutRowLineage R`

4. `SILVER_COMPETITION` — `SilverCompetition`

   `construction_authority_state:Literal[semantic_only_unchecked] D(same); build_id:Sha256Digest R; tenant_context:TenantContext R; source_completion_index_sha256:Sha256Digest R; source_rows:tuple[WyscoutSourceRowReference,...] R min=1; lineage:WyscoutRowLineage R; competition_schema_version:Literal[w04-wyscout-silver-competition-v1] D(same); competition_source_id:StrictPositiveInt R; competition_id:StrictUuid R`

5. `SILVER_TEAM` — `SilverTeam`

   `construction_authority_state; build_id; tenant_context; source_completion_index_sha256; source_rows; lineage` are the same six inherited fields and states as root 4, followed by `team_schema_version:Literal[w04-wyscout-silver-team-v1] D(same); team_source_id:StrictPositiveInt R; team_id:StrictUuid R`.

6. `SILVER_PLAYER` — `SilverPlayer`

   The same six inherited fields are followed by `player_schema_version:Literal[w04-wyscout-silver-player-v1] D(same); player_source_id:StrictPositiveInt R; player_id:StrictUuid R`.

7. `SILVER_MATCH` — `SilverMatch`

   The same six inherited fields are followed by `match_schema_version:Literal[w04-wyscout-silver-match-v1] D(same); match_source_id:StrictPositiveInt R; match_id:StrictUuid R; competition_id:StrictUuid R; season_id:StrictUuid R; season_source_id:StrictNonNegativeInt R; match_start_utc:UtcInstant R; team_ids:tuple[StrictUuid,StrictUuid] R min=2 max=2; source_partition:CountryPartition R`.

8. `SILVER_ACTION` — `SilverAction`

   The same six inherited fields are followed by `action_schema_version:Literal[w04-wyscout-silver-action-v1] D(same); action_source_id:StrictPositiveInt R; action_id:StrictUuid R; source_event_record_id:StrictPositiveInt R; match_id:StrictUuid R; competition_id:StrictUuid? R; player_id:StrictUuid? R; team_id:StrictUuid? R; action_event_taxonomy_id:StrictNonNegativeInt? R; action_subevent_taxonomy_id:StrictNonNegativeInt? R; action_period_code:str R length=1..16; period_rank:StrictNonNegativeInt R; period_elapsed_seconds:StrictDecimal R; event_sec_source_scale:int R 0..18; source_record_ordinal:StrictNonNegativeInt R; action_tag_ids:tuple[StrictNonNegativeInt,...] R; action_positions:tuple[ActionPosition,...] R; possession_predicate_state:PossessionPredicateState R; possession_period_sequence:PossessionPeriodSequence R; possession_eligibility_state:PossessionEligibilityState R; occurrence_precision:Literal[period_relative] D(same); occurrence_utc:None D(null)`.

9. `SILVER_LINEUP_STINT` — `SilverLineupStint`

   The same six inherited fields are followed by `lineup_stint_schema_version:Literal[w04-wyscout-silver-lineup-stint-v1] D(same); lineup_stint_id:StrictUuid R; match_id:StrictUuid R; player_id:StrictUuid R; team_id:StrictUuid R; start_interval:NominalMinuteInterval? R; end_interval:NominalMinuteInterval? R; lower_bound_minutes:StrictNonNegativeInt? R; upper_bound_minutes:StrictNonNegativeInt? R; right_censored:bool R; elapsed_minutes:None D(null); per90_eligible:Literal[false] D(false); suppression_reason:Literal[suppressed_unsupported_denominator] D(same)`.

10. `SILVER_POSSESSION` — `SilverPossession`

   The same six inherited fields are followed by `possession_schema_version:Literal[w04-wyscout-silver-possession-v1] D(same); possession_id:StrictUuid R; match_id:StrictUuid R; action_period_code:str R length=1..16; team_id:StrictUuid R; contributing_actions:tuple[SilverAction,...] R min=1; action_ids:tuple[StrictUuid,...] R min=1; first_action_order:tuple[StrictNonNegativeInt,StrictDecimal,StrictNonNegativeInt,StrictNonNegativeInt] R; last_action_order:same R; project_taxonomy_state:Literal[project_defined_resolved] D(same); provider_native_claim:Literal[false] D(false)`.

11. `SILVER_PLAYER_MATCH_FACT` — `SilverPlayerMatchFact`

   The same six inherited fields are followed by `player_match_fact_schema_version:Literal[w04-wyscout-player-match-fact-v1] D(same); source_manifest_id:StrictUuid R; match_id:StrictUuid R; player_id:StrictUuid R; competition_id:StrictUuid R; season_id:StrictUuid R; match_start_utc:UtcInstant R; match_team_id:StrictUuid? R; lineup_evidence_present:bool R; contributing_lineup_stints:tuple[SilverLineupStint,...] R; contributing_actions:tuple[SilverAction,...] R; contributing_possessions:tuple[SilverPossession,...] R; action_count:StrictNonNegativeInt R; coordinate_known_action_count:StrictNonNegativeInt R; resolved_possession_action_count:StrictNonNegativeInt R; right_censored_or_uncertain:bool R; elapsed_minutes:None D(null); per90_eligible:Literal[false] D(false); coverage:GoldCoverage R; applicability:W04ApplicabilityAssessment R; temporal_proof:W04SemanticTemporalProof R`.

12. `GOLD_PLAYER_WINDOW` — `GoldPlayerWindow`

   The same six inherited fields are followed by `gold_schema_version:Literal[w04-wyscout-gold-player-window-v1] D(same); player_id:StrictUuid R; competition_id:StrictUuid R; season_id:StrictUuid R; role_context_id:StrictUuid R; role_context_version:Literal[w04-neutral-role-context-v1] R; role_context_state:Literal[neutral_unscoped] R; window_definition_id:StrictUuid R; window_start_utc:UtcInstant R; window_end_utc:UtcInstant R; feature_cutoff_ts:UtcInstant R; dependency_lineage_hash:Sha256Digest R; feature_schema_hash:Sha256Digest R; temporal_proof:W04SemanticTemporalProof R; coverage:GoldCoverage R; applicability:W04ApplicabilityAssessment R; features:GoldFeatureValues R; contributing_player_match_facts:tuple[SilverPlayerMatchFact,...] R min=1; contributing_player_match_keys:tuple[tuple[StrictUuid,StrictUuid,StrictUuid,StrictUuid,str],...] R min=1`.

### 3.2 JSON roots 13–23

13. `LAYER_MANIFEST` — `LayerManifest`

   `manifest_schema_version:Literal[w04-wyscout-layer-manifest-v1] D(same); construction_authority_state:Literal[semantic_only_unchecked] D(same); layer:Layer R; build_id:Sha256Digest R; manifest_path:WyscoutProductPath R; source_manifest_id:StrictUuid R; source_manifest_sha256:Sha256Digest R; source_completion_index_sha256:Sha256Digest R; tenant_context:TenantContext R; classification:SourceUseClassification R; source_available_at:UtcInstant R; source_acquired_at:UtcInstant R; authority_clocks:tuple[WyscoutAuthorityClock,...] R min=4 max=4; feature_schema_hash:Sha256Digest R; dependency_lineage_hash:Sha256Digest R; dependency_lineage:DependencyLineage R; entries:tuple[LayerManifestEntry,...] R min=1; parent_layer_manifests:tuple[ParentLayerManifest,...] R; complete:Literal[true] D(true)`.

14. `TEMPORAL_BOUNDARY_RECEIPT` — `TemporalBoundaryReceipt`

   `build_id:Sha256 R; checked_at:build-UtcInstant R; dependency_lineage_hash:Sha256 R; feature_cutoff_ts:Literal[2026-08-01T00:00:00Z] D(same); gold_manifest_relative_path:RelativePath R; gold_manifest_sha256:Sha256 R; gold_product_physical_sha256:Sha256 R; gold_product_relative_path:RelativePath R; gold_product_semantic_sha256:Sha256 R; gold_relative_path_sha256:Sha256 R; row_count:Literal[1] D(1); run_id:UuidV4 R; schema_version:Literal[w04-wyscout-temporal-boundary-receipt-v1] D(same); temporal_proof_sha256:Sha256 R; verification_state:Literal[STRICT_BEFORE_CUTOFF_PASS] D(same)`.

15. `REBUILD_INVOCATION_RECEIPT` — `RebuildInvocationReceipt`

   `boundary_receipts:tuple[BoundaryReceiptSummary,...] R; build_id:Sha256 R; completed_at:build-UtcInstant R; layer_manifests:tuple[LayerManifestSummary,...] R; rebuild_invocation:RebuildInvocation R; result_state:Literal[COMPLETE] D(same); run_id:UuidV4 R; schema_version:Literal[w04-wyscout-rebuild-invocation-receipt-v1] D(same); started_at:build-UtcInstant R`.

16. `ENTRYPOINT_SOURCE_RESULT` — `EntrypointSourceResult`

   `descriptor_cloexec:Literal[false] D(false); descriptor_inheritable:Literal[true] D(true); descriptor_number:int R 3..2147483647; device:JsonInteger R; inode:StrictPositiveInt R; link_count:Literal[1] D(1); mode:Literal[420] D(420); offset_after:Literal[0] D(0); offset_before:Literal[0] D(0); relative_path:RelativePath R; role:ChildRole R; sha256:Sha256 R; size_bytes:int R 1..16777216; source_eof:Literal[true] D(true)`.

17. `COMPONENT_PROOF_RESULT` — `ComponentProofResult`

   `component_key:ComponentKey R; evidence_row_count:int R 1..10000000; value_json_sha256:Sha256 R`.

18. `PRE_BUILD_ADMISSION_RESULT` — `PreBuildAdmissionResult`

   `admission_prefix_relative_path:RelativePath R; admission_run_id:UuidV4 R; canonical_manifest_bytes_b64u:Base64Url R; canonical_manifest_sha256:Sha256 R; component_proofs:tuple[ComponentProofResult,...] R; component_proofs_sha256:Sha256 R; environment_digest:Sha256 R; manifest_schema_version:Literal[w04-code-environment-admission-v15] D(same); repository_code_sha256:Sha256 R`.

19. `REBUILD_RECEIPT_SUMMARY` — `RebuildReceiptSummary`

   `relative_path:RelativePath R; sha256:Sha256 R; size_bytes:int R 1..16777216`.

20. `LAYER_MANIFEST_SUMMARY` — `LayerManifestSummary`

   `layer:Literal[BRONZE,SILVER,GOLD] R; manifest_relative_path:RelativePath R; manifest_sha256:Sha256 R; manifest_size_bytes:int R 1..16777216; semantic_sha256:Sha256 R`.

21. `FINAL_RECHECK_RESULT` — `FinalRecheckResult`

   `build_id:Sha256 R; child_environment_sha256:Sha256 R; entrypoint_descriptor_match:Literal[true] D(true); entrypoint_sha256:Sha256 R; environment_digest:Sha256 R; in_place_pyc_unchanged:Literal[true] D(true); layer_manifest_set_sha256:Sha256 R; rebuild_prefix_empty:Literal[true] D(true); rebuild_receipt_sha256:Sha256 R; repository_code_sha256:Sha256 R; repository_pyc_inventory_sha256:Sha256 R; resource_digest:Sha256 R; run_id:UuidV4 R; runtime_subset_digest:Sha256 R; schema_version:Literal[w04-rebuild-final-recheck-v1] D(same); selected_prefix_role:Literal[POST_BUILD_ID_REBUILD] D(same); site_pyc_inventory_sha256:Sha256 R`.

22. `POST_BUILD_ID_REBUILD_RESULT` — `PostBuildIdRebuildResult`

   `build_id:Sha256 R; final_recheck:FinalRecheckResult R; layer_manifests:tuple[LayerManifestSummary,...] R; rebuild_prefix_relative_path:RelativePath R; rebuild_receipt:RebuildReceiptSummary R; run_id:UuidV4 R`.

23. `CHILD_RESULT_ENVELOPE` — `ChildResultEnvelope`

   `child_environment_sha256:Sha256 R; child_role:Literal[PRE_BUILD_ADMISSION,POST_BUILD_ID_REBUILD] R; entrypoint_source:EntrypointSourceResult R; expected_repository_code_sha256:Sha256 R; launcher_sha256:Sha256 R; nonce:Sha256 R; ordered_argv_sha256:Sha256 R; payload_kind:Literal[CODE_ENVIRONMENT_MANIFEST,REBUILD_COMPLETION] R; result:PreBuildAdmissionResult|PostBuildIdRebuildResult R; schema_version:Literal[w04-child-result-v2] D(same)`.

## 4. Transitive named support closure

The following support objects are reachable from the roots. Field order is exact;
`R` and `D` retain Section 2 meanings.

### 4.1 Shared data supports

- `TenantContext`: `tenant_id:StrictUuid R; club_id:StrictUuid? D(null)`.
- `SourceUseClassification`: `use_class:LicenceUseClass R; derived_data_allowed:bool R; internal_review_allowed:bool R; export_allowed:bool R; attribution_required:bool R; attribution_text:NonEmptyString? D(null)`.
- `EvidenceDependency`: `kind:DependencyKind R; dependency_id:StrictUuid R; digest:Sha256Digest R; observed_at:UtcInstant R; available_at:UtcInstant R`.
- `DependencyLineage`: `lineage_hash:Sha256Digest R; dependencies:tuple[EvidenceDependency,...] R min=1`.
- `WyscoutRawSourceRowReference`: `source_manifest_id:StrictUuid R; completion_relative_path:strict str R; source_sha256:Sha256Digest R; source_record_ordinal:StrictNonNegativeInt R`.
- `WyscoutSourceRowReference`: the preceding four fields, then `record_kind:SourceRecordKind R; raw_record_sha256:Sha256Digest R`.
- `WyscoutAuthorityReference`: `acceptance_id:strict str R; acceptance_sha256:Sha256Digest R; authority_kind:AuthorityKind R; candidate_id:strict str R; candidate_sha256:Sha256Digest R; review_id:strict str R; review_sha256:Sha256Digest R`.
- `WyscoutAuthorityClock`: `authority_kind:AuthorityKind R; decided_at:UtcInstant R; reviewed_at:UtcInstant R; accepted_at:UtcInstant R`.
- `WyscoutSourceAuthority`: `source_manifest_id:StrictUuid R; source_manifest_sha256:Sha256Digest R; tenant_context:TenantContext R; available_at:UtcInstant R; acquired_at:UtcInstant R; classification:SourceUseClassification R`.
- `WyscoutRowLineage`: `source_manifest_id:StrictUuid R; source_manifest_sha256:Sha256Digest R; source_completion_index_sha256:Sha256Digest R; source_rows:tuple[WyscoutSourceRowReference,...] R min=1; authority_references:tuple[WyscoutAuthorityReference,...] R min=max=4; authority_clocks:tuple[WyscoutAuthorityClock,...] R min=max=4; source_authority:WyscoutSourceAuthority R; dependency_lineage:DependencyLineage R`.
- `RawFieldMeasurement`: `json_path:JsonPath R; measured_json_type:CanonicalJsonKind R`.
- `RawKindEvidence`: `envelope_version D(w04-raw-kind-v1); raw_kind_state; value_present; value:CanonicalJsonValue; envelope_bytes:bytes; raw_kind_sha256`.
- `ActionPosition`: `x:StrictDecimal; y:StrictDecimal; within_accepted_bounds:bool`.
- `PossessionSequenceAction`: `action_id:StrictUuid R; source_event_record_id:StrictPositiveInt R; source_row:WyscoutSourceRowReference R; match_id:StrictUuid R; player_id:StrictUuid? R; team_id:StrictUuid? R; action_event_taxonomy_id:StrictNonNegativeInt? R; action_subevent_taxonomy_id:StrictNonNegativeInt? R; action_period_code:strict str R length=1..16; period_rank:StrictNonNegativeInt R; period_elapsed_seconds:StrictDecimal R; source_record_ordinal:StrictNonNegativeInt R; action_tag_ids:tuple[StrictNonNegativeInt,...] R`.
- `PossessionPeriodSequence`: `construction_authority_state:Literal[semantic_only_unchecked] D(same); match_id:StrictUuid R; source_completion_index_sha256:Sha256Digest R; source_completion_membership_sha256:Sha256Digest R; action_period_code:strict str R length=1..16; period_action_count:StrictPositiveInt R; actions:tuple[PossessionSequenceAction,...] R min=1; complete_period_evidence:Literal[true] D(true)`.
- `NominalMinuteInterval`: `lower:StrictNonNegativeInt; upper:StrictPositiveInt`.
- `GoldCoverageDimension`: `name:GoldCoverageDimensionName R; numerator:StrictNonNegativeInt R; denominator:StrictNonNegativeInt R; coverage:StrictDecimal R; state:GoldCoverageState R; reason_codes:tuple[ReasonCode,...] D(()); zero_denominator_authority:WyscoutAuthorityReference? D(null)`.
- `GoldCoverage`: `dimensions:tuple[GoldCoverageDimension,...] R min=max=6; coverage_overall:StrictDecimal R; missing_dimensions:tuple[GoldCoverageDimensionName,...] R`.
- `W04ApplicabilityAssessment`: `state:W04Applicability R; reason_codes:tuple[ReasonCode,...] R`.
- `W04SemanticTemporalProof`: `semantic_proof_schema_version D(w04-wyscout-semantic-temporal-proof-v1); snapshot_as_of_ts; available_at_watermark; valid_from_ts; feature_cutoff_ts; source_manifest_ids(min=max=1); source_completion_index_sha256; feature_schema_hash; dependency_lineage_hash; dependency_lineage; source_authority; authority_clocks(min=max=4); occurrence_precision D(period_relative); partial_match_claim_supported D(false)`.
- `GoldFeatureValues`: `action_count:StrictNonNegativeInt R; coordinate_known_action_count:StrictNonNegativeInt R; match_count:StrictNonNegativeInt R; resolved_possession_action_count:StrictNonNegativeInt R`.
- `WyscoutProductPath`: `path_role:ProductPathRole R; relative_path:strict str R`.
- `ManifestPartitionValue`: `key` matching `^[a-z][a-z0-9_]{0,63}$`; `value` length `1..512`.
- `LayerManifestEntry`: `path:WyscoutProductPath R; serializer:strict str R; serializer_version:strict str R length=1..128; schema_role:strict str R length=1..128; row_count:StrictPositiveInt R; semantic_sha256:Sha256Digest R; physical_sha256:Sha256Digest R; size_bytes:StrictPositiveInt R; ordered_parent_paths:tuple[str,...] R; partition_values:tuple[ManifestPartitionValue,...] R; classification:SourceUseClassification R; complete:Literal[true] D(true)`.
- `ParentLayerManifest`: `layer:Layer R; build_id:Sha256Digest R; relative_path:strict str R; sha256:Sha256Digest R`.

### 4.2 Canonical JSON discriminated union

`CanonicalJsonValue` is discriminated by `kind` and has exactly seven arms:

- `CanonicalJsonNull`: `kind D(null); value D(null)`.
- `CanonicalJsonBoolean`: `kind D(boolean); value:bool R`.
- `CanonicalJsonInteger`: `kind D(integer); value:strict int R`.
- `CanonicalJsonNumber`: `kind D(number); value:StrictDecimal R`.
- `CanonicalJsonString`: `kind D(string); value:strict str R`.
- `CanonicalJsonArray`: `kind D(array); value:tuple[CanonicalJsonValue,...] R`.
- `CanonicalJsonObject`: `kind D(object); value:tuple[CanonicalJsonMember,...] R`, where
  `CanonicalJsonMember` is `key:strict str R; value:CanonicalJsonValue R`.

The recursive union is the logical evidence type needed for strict inverse
validation. It is not an Arrow union authority or recursive Arrow schema: at any
field boundary declared as `CanonicalJsonValue` or one of its seven concrete arms,
the complete present value projects as one tagged UTF-8 scalar.

### 4.3 Build/result supports

- `BoundaryReceiptSummary`: `gold_relative_path; relative_path; sha256; size_bytes(1..16777216)`.
- `RebuildInvocation`: exact 25 fields in this order:
  `authority_rows, build_id, code_manifest_id, code_manifest_sha256, dependency_rows, dependency_watermark, environment_digest, feature_cutoff_ts, feature_schema_hash, identity_bundle_id, identity_bundle_sha256, local_resource_digest, product_contract_digest, role_context_id, role_context_state, role_context_version, schema_bundle_digest, selected_lock_closure_digest, source_manifest_id, source_manifest_sha256, tenant_club_id, tenant_id, window_definition_id, window_end_utc, window_start_utc`.
- `AuthorityRow`: `acceptance_id; acceptance_sha256; authority_kind; candidate_id; candidate_sha256; review_id; review_sha256`.
- `DependencyRow`: `kind; dependency_id; digest; observed_at; available_at`.

`RebuildInvocation` defaults/fixed values are: five ordered accepted authority rows;
five ordered dependency rows; watermark `2026-07-31T14:15:26Z`; cutoff
`2026-08-01T00:00:00Z`; feature digest fixed by accepted authority; fixed identity
bundle, role context, source manifest, tenant/no club, window ID, and half-open window.
The remaining digest values and `build_id` are required.

### 4.4 Enum and literal closure

The enum values that enter the roots/support closure are:

- `SourceRecordKind`: `competition, team, player, event-taxonomy, tag-taxonomy, match, action`.
- `CountryPartition`: `england, france, germany, italy, spain`.
- `CanonicalJsonKind`: `null, boolean, integer, number, string, array, object`.
- `RawKindState`: `missing, null, non-string, string-unknown-safe, string-unsafe`.
- `RejectedFieldDecision`: `PRESERVE_UNMAPPED, FORBIDDEN`.
- data `AuthorityKind`: `FIELD, POSSESSION, SUPPORTED_FEATURE, IDENTITY`.
- `PossessionPredicateState`: `PREDICATE_ADMITTED, PREDICATE_UNMAPPED`.
- `PossessionEligibilityState`: `ELIGIBLE_RESOLVED, INELIGIBLE_UNMAPPED`.
- `GoldCoverageDimensionName`: `identity, lineup, action, coordinate, possession, temporal` in that order.
- `GoldCoverageState`: `complete, partial, not_applicable_zero_denominator, missing_zero_denominator, authority_missing, failed`.
- `W04Applicability`: `suppressed, research_only, w04_data_ready`.
- `Layer`: `BRONZE, SILVER, GOLD`.
- `LicenceUseClass`: `open, internal, restricted, prohibited`.
- `DependencyKind`: `source_manifest, identity_evidence, feature_schema, model_artifact, retrieval_index`.
- `ChildRole`: `PRE_BUILD_ADMISSION, POST_BUILD_ID_REBUILD`.
- `LayerName`: `BRONZE, SILVER, GOLD`.
- build `AuthorityKind`: `FIELD, POSSESSION, SUPPORTED_FEATURE, IDENTITY, SEASON_LINEUP_PRODUCT_BINDING`.
- build `DependencyKind`: `source_manifest, identity_evidence, feature_schema`.
- `ProductPathRole`: `BRONZE_KNOWN_RECORD, BRONZE_REJECTED_RECORD,
  BRONZE_REJECTED_FIELD, SILVER_COMPETITION, SILVER_TEAM, SILVER_PLAYER,
  SILVER_MATCH, SILVER_ACTION, SILVER_LINEUP_STINT, SILVER_POSSESSION,
  SILVER_PLAYER_MATCH_FACT, GOLD_PLAYER_WINDOW, BRONZE_MANIFEST,
  SILVER_MANIFEST, GOLD_MANIFEST, REBUILD_INVOCATION_RECEIPT,
  TEMPORAL_BOUNDARY_RECEIPT`.
- `ChildResultEnvelope.result` is exactly the two-arm object union
  `PreBuildAdmissionResult|PostBuildIdRebuildResult`; role and payload kind select
  the permitted arm.
- `ComponentKey` is exactly this ordered twenty-value literal:
  `child_result_contract_digest, editable_root_digest, environment_values_digest,
  executable_census_digest, extracted_runtime_digest,
  installed_record_runtime_digest, interpreter_digest,
  local_launcher_control_digest, local_resource_digest, lock_inputs_digest,
  process_launch_contract_digest, pyc_policy_source_map_digest,
  selected_lock_closure_digest, selector, selector_bootstrap_digest, stdlib_digest,
  uv_physical_sha256, uv_version, venv_bootstrap_digest, wheel_declaration_digest`.
  No twenty-first value is admitted.

## 5. Declarative validator predicate ledger

This section records operands and constants, rather than validator names alone.
Every predicate is conjunctive with strict field parsing, closed objects, and all
nested support predicates.

### 5.1 Canonical JSON, rights, source and lineage

1. Canonical numbers require `value.is_finite()`. Object member keys contain no
   code point in `U+D800..U+DFFF`. Object keys are unique and equal their ascending
   Python/Unicode order.
2. Restricted source rights are the exact accepted object: use class restricted;
   derived/internal review true; export false; attribution required with the exact
   Wyscout/Pappalardo CC BY 4.0 text. Independently, a prohibited classification
   cannot grant derived, review, or export use, and required attribution cannot
   omit text.
3. A raw source-row reference requires source manifest ID
   `4e16bdb5-afe7-5601-88ad-adc124cfce3b`; its path must be one of the exact admitted
   object/member paths; `source_sha256` must equal that path's frozen member digest;
   and `0 <= source_record_ordinal <` its frozen row count. The admitted counts are
   7, 142, 3603, 36, 59, 380/380/306/380/380 match rows, and
   643150/632807/519407/647372/628659 action rows by the five country paths.
   A typed source-row additionally requires the exact path-to-record-kind mapping.
4. Raw-kind evidence derives its state from `(value_present, exact union arm,
   string token)`. Missing requires typed canonical null; known seven kind strings
   are forbidden; safe unknown strings alone match
   `^[A-Za-z][A-Za-z0-9_-]{0,63}$`. `envelope_bytes` must equal the exact canonical
   state/presence/value envelope, and `raw_kind_sha256` must equal SHA-256 of
   `b"w04-raw-kind-v1\x00" || UINT64_BE(len(envelope_bytes)) || envelope_bytes`.
5. Each authority reference must equal the entire accepted seven-field row selected
   by its authority kind. Each authority clock triple must equal the frozen triple
   for that kind and satisfy `decided_at <= reviewed_at <= accepted_at`.
6. Source authority equals the frozen source manifest ID/digest, no-club tenant,
   release `2020-01-28T14:24:27Z`, acquisition
   `2026-07-29T15:51:08.598589Z`, and accepted rights object.
7. Row lineage equals the frozen source manifest and completion-index identities;
   authority references and clocks equal the accepted four rows in enum order;
   source authority is exact; physical `(completion_relative_path, ordinal)` keys
   are sorted and unique; and dependency lineage passes the exact five-row closure.
8. Dependency lineage has unique `(kind, dependency_id)`. W04 adds: exactly five
   rows in `dependency_sort_key` order; one source manifest, one identity evidence,
   three feature schemas, no model/retrieval rows; frozen IDs/digests/clocks for
   source, identity, field, possession and feature; and a recomputed lineage hash
   over all five rows plus the completion-index digest.

Rejected substitutions include bool-as-int, unknown/aliased path, wrong member
digest, ordinal equal to row count, mixed authority versions, reordered/duplicated
source rows or dependencies, a sixth dependency, and a copied but unreproduced
lineage hash.

### 5.2 Bronze and common product predicates

1. Known Bronze recomputes canonical raw bytes once: the digest must equal both
   `raw_record_sha256` and `source_row.raw_record_sha256`; the exact source row must
   occur in lineage; measured `(path,type)` rows must exactly equal all top-level
   raw object members; tenant equals the accepted no-club tenant and lineage tenant;
   rights equal accepted rights.
2. Rejected record recomputes its raw-record digest; tenant and rights are exact;
   and lineage must contain a row equal in physical path, member digest, ordinal,
   and raw-record digest to the raw reference.
3. Rejected field requires source-row kind equality; retained value arm equals
   measured JSON type; retained-value digest is recomputed; field authority is the
   exact accepted field-v2 row; and `(record_kind,json_path)` exists in the 119-row
   registry. For `action/$.subEventId`, exact reason mapping is string/boolean/null/
   number/array/object/unknown-integer, decision is `PRESERVE_UNMAPPED`, and an
   admitted integer event/subevent pair cannot be rejected. Every other row forbids
   action-event evidence, rejects a measured type outside registry support, rejects
   a `TRANSFORM` row, and requires exact registry decision plus reason
   `FIELD_V2_<decision>`. Tenant, rights, and source-row membership are exact.
4. Every Silver/Gold product row requires the accepted no-club tenant, the frozen
   completion-index digest equal both row and lineage, source-row keys sorted unique,
   and every selected source row present in lineage.

### 5.3 Entity, action, lineup and possession predicates

1. Competition/team/player select exactly one physical row of the matching family
   and reproduce the canonical UUIDv5 from the strict positive source ID. Match
   selects exactly one match row, derives country from its member path, reproduces
   match UUIDv5, and has exactly two distinct UUIDs ordered by UUID bytes.
2. `ActionPosition` requires each axis to be finite `decimal128(22,18)` capacity
   with exact lexical scale; `within_accepted_bounds` equals
   `0 <= x <= 100 and 0 <= y <= 100`. Values are preserved, never clamped.
3. A possession-sequence action selects an action-family source row; its ordinal
   equals the source row ordinal; action UUIDv5 derives from strict positive source
   event ID; elapsed seconds are finite and nonnegative; tag IDs are sorted unique.
4. A period sequence binds the accepted completion-index digest; declared count
   equals `len(actions)`; every action has the same match and period; action order
   keys `(period_rank, seconds, source ordinal, source event ID)` are sorted and
   unique; action UUIDs are unique; and physical rows are unique.
5. Silver action selects exactly one action row; action UUID derives from
   `action_source_id`; source event ID equals source ID; ordinal equals selected
   row; seconds are finite, nonnegative and exact `decimal128(22,18)` with declared
   scale `0..18`; tags are sorted unique. A non-null subevent requires a non-null
   event and an exact admitted strict-integer pair. Predicate state is recomputed
   from event/subevent/team/tags. The period sequence has the same match/period,
   all sequence source rows occur in lineage, and it contains this action exactly
   once with equality across all twelve sequence/action evidence fields.
   Eligibility is `ELIGIBLE_RESOLVED` iff the action ID occurs in the deterministic
   possession groups, otherwise `INELIGIBLE_UNMAPPED`.
6. Nominal interval requires `upper = lower + 1`. An open lineup requires either
   interval absent, `right_censored=true`, and both minute bounds null. A closed
   lineup requires bounds exactly
   `(max(0,end.lower-start.upper), max(0,end.upper-start.lower))` and
   `right_censored=false`. It selects exactly one match-family source row; elapsed
   minutes remain null, per-90 false, and suppression reason fixed by the fields.
7. Silver possession requires contributing actions unique and ordered by
   `(action_order_key, action_id.bytes)`; every action uses one identical complete
   sequence; the action IDs equal exactly one resolved group for `team_id`; every
   action has the same build, tenant, lineage, match and period and is resolved;
   control/restart action team equals possession team. `source_rows` are exactly the
   sorted set of all complete-sequence source rows; `action_ids` derive from the
   contributing actions; first/last order equal the first/last action keys.
8. Equal-clock resolution is group-first: more than one controlling team at one
   `(period_rank,seconds)` clears dependent contested buffer and current active
   group for that clock, while a strictly earlier completed group remains. No
   action crosses a period.

The exact admitted pair sets and decision sets in `wyscout_data.py` are operands,
not prose labels. In particular the 36 admitted event/subevent pairs, sorted-unique
tags, required team for restart/control, and the contested/dead-ball/admin/restart/
control/unmapped sets must be represented as closed constants or structured set
membership predicates.

### 5.4 Coverage, fact, Gold and temporal predicates

1. Coverage requires `numerator <= denominator` and sorted-unique reasons. Failed or
   authority-missing states have numerator/coverage zero, nonempty reasons, and no
   zero-denominator authority. For positive denominators, no zero proof is allowed,
   coverage equals exact Decimal `N/D`, state is complete iff `N=D` else partial,
   complete has no reasons and partial has reasons. Only coordinate/possession may
   use authority-proven zero-denominator coverage one with the matching FIELD or
   POSSESSION authority; unproven optional zero is missing with coverage zero;
   mandatory zero is missing with coverage zero and reasons.
2. Gold coverage has exactly six dimensions in enum order. `missing_dimensions` is
   the lexical set of partial/missing/authority-missing/failed dimensions and
   `coverage_overall` is the exact minimum. Applicability reasons are sorted unique;
   non-ready requires reasons and data-ready forbids them.
3. Temporal proof binds the accepted completion index and exact five dependency
   closure, has unique `(kind,id)` and exact 1/1/3 kind counts, exact source authority
   and authority clocks, and requires every dependency observed/available clock,
   source acquisition, and every authority decision/review/acceptance strictly
   before cutoff. Watermark equals the maximum dependency availability and is
   strict-before; valid-from equals `max(snapshot,watermark)`; snapshot is
   strict-before. Both lineage hashes are recomputed; source manifest tuple is the
   exact singleton; feature schema digest is the accepted one.
4. Player-match fact requires source manifest equality; lineup rows unique by ID and
   ordered by ID bytes; each lineup shares build/tenant/lineage/match/player/team;
   the presence Boolean equals `bool(lineups)`. Actions are unique/canonical and
   share build/tenant/lineage/match/player/competition/team. At least lineup or
   action evidence exists. For each match/period, all selected actions share one
   complete sequence and selected player actions equal the complete sequence's
   player subset. Possessions are unique/order-canonical, cannot leak identity, and
   selected action evidence is byte-semantically equal. Each eligible resolved
   selected action has exactly one possession membership and each ineligible action
   zero. Fact source rows equal the sorted union of lineup and all causal sequence
   rows. The three feature counts derive exactly from actions, accepted positions,
   and membership. Lineage/source authority/clocks equal temporal proof; match start
   is strict-before cutoff; coverage and applicability are recomputed exactly.
5. Gold requires the exact neutral role-context UUID/version/state; start is before
   end; cutoff/lineage/source authority/clocks/feature schema equal temporal proof
   and accepted constants. Fact keys are unique and sorted and the separate key
   tuple equals them. Each fact shares build/tenant/source/player/competition/
   season/lineage/proof, lies in the half-open window, and is strict-before cutoff.
   Source rows equal the sorted union from facts. Four features are exact sums plus
   distinct match count. Six-dimensional coverage aggregates from facts and
   applicability is recomputed, including any right-censoring uncertainty.
6. `GoldFeatureValues` independently rejects either coordinate-known or resolved-
   possession count greater than action count.

### 5.5 Path and manifest predicates

1. Product paths are NFC and match the exact role-specific regular expression.
   Every embedded UUID has canonical spelling; every embedded six-fraction UTC token
   parses to a real instant. No role can borrow another role's path.
2. A parent manifest cannot be GOLD and its path is exactly
   `data/manifests/wyscout/v5/<layer-lower>/<build_id>.manifest.json`.
3. Manifest entry serializer equals the sole owner for its path role; schema role
   equals path role. Partition values are exactly all path `key=value` segments,
   sorted by key and unique. Rights are exact; parent product paths are sorted
   unique. Bronze has no parent products; Silver/Gold has nonempty preceding-layer
   parents and every parent contains the same build ID.
4. Layer manifest path role, layer, filename and build agree; source manifest/index,
   tenant, rights, source clocks, authority clocks and feature schema are exact;
   dependency lineage and hash are recomputed. Entry paths are sorted unique, stay
   in layer, and contain the build. Bronze has no parent layer; Silver has exactly
   one Bronze parent; Gold exactly one Silver parent; parent build equals child.

### 5.6 Build, receipts and result predicates

1. Window identity is the exact five-field object; its canonical preimage has length
   250 and the frozen content identity, and its UUIDv5 chain reproduces
   `a0af8d56-e41d-5467-b46e-82887c4861e0`. The half-open window is
   `[2017-08-11T00:00:00Z,2017-08-12T00:00:00Z)`, selected match/snapshot is
   `2017-08-11T18:45:00Z`, cutoff is `2026-08-01T00:00:00Z`, every dependency clock
   is strict-before, watermark is their maximum, and valid-from is
   `max(snapshot,watermark)`.
2. The bounded season helper accepts only exact `int` 181150 and reproduces season
   UUID `4696aa1f-b512-5d18-af79-33cf031455cf`; bool and every other value fail.
3. Each build authority row equals its complete accepted fixed row. Dependency
   `observed_at <= available_at`. Rebuild invocation requires the accepted ordered
   five authority and five dependency rows, code-manifest UUIDv5 derived from its
   digest, neither historical v1 aggregate placeholder, exact 25-key order, and
   `build_id = SHA256(canonical exact 25-key pre-build projection)`. Removing only
   build ID and inserting only projection schema version is the strict inverse.
4. Boundary receipt paths are safe; Gold manifest path is the exact same-build path;
   Gold product path matches the one-match fixed pattern; direct UTF-8 path SHA
   equals `gold_relative_path_sha256`.
5. Invocation receipt build equals nested invocation, `started_at <= completed_at`,
   layer rows are exactly `BRONZE,SILVER,GOLD` with exact same-build paths, exactly
   one boundary exists, and its safe path equals the deterministic build/run/Gold
   path.
6. Entrypoint role selects exactly the admission or rebuild script path. Admission
   prefix derives from admission UUID; component proof keys are exactly the ordered
   twenty; proof-array digest is recomputed; base64url manifest is canonical,
   1..12000000 bytes, digest-equal, duplicate-key-free canonical JSON with exact
   stable roster; result schema/repository/environment equal manifest; environment
   digest covers exact components; every component proof covers its named value.
7. Post-build result prefix and receipt path derive from build/run; layer summaries
   are exact ordered three with exact paths; final recheck build/run and receipt
   digest agree; layer-set digest is recomputed from all summary rows.
8. Child envelope entrypoint role equals child role. Admission role requires
   `CODE_ENVIRONMENT_MANIFEST` plus exact admission result and repository digest;
   rebuild role requires `REBUILD_COMPLETION` plus exact rebuild result and equal
   repository/environment/entrypoint digests. Ordered argv digest is recomputed from
   the one exact role argv.
9. Complete receipt closure additionally guard-reads all three complete canonical
   LayerManifest bytes, validates the typed object, physical digest/size, frozen
   authority/lineage, and sole two-key complete-manifest semantic derivation;
   reconciles Bronze->Silver->Gold parent summaries; derives exactly one complete
   Gold product; revalidates its logical row/proof and one-match/season population;
   binds every Gold physical/semantic/count value; reopens the boundary; and enforces
   `started_at <= checked_at <= completed_at`. These are composition predicates, not
   fields trusted from a summary.

## 6. Projection-sensitive paths for the 12 Parquet roots

The accepted projection rules are invariant:

- a present field whose declared logical type is `CanonicalJsonValue` or any one of
  its seven concrete arms is one complete non-null Arrow UTF-8 scalar containing
  exact canonical tagged logical JSON without LF; Arrow null is allowed only for
  separately authoritative outer logical absence;
- inverse decoding is strict UTF-8, duplicate-key/invalid-constant rejection,
  discriminated typed validation, canonical re-encoding, and byte equality;
- a heterogeneous fixed tuple is an ordered positional struct with descriptor-owned
  exact child names, positions, types and nullability;
- homogeneous variable or fixed sequences are Arrow lists with descriptor-owned
  item name/type/nullability/cardinality;
- named model objects are ordered structs; accepted scalar identity mappings retain
  strict widths, `decimal128` precision/scale and `timestamp[us,tz=UTC]` as frozen by
  the descriptor and R20 physical rules;
- schema/field/list/struct metadata is absent recursively; schema comes only from
  accepted descriptor content, never a row or fixture.

Path notation: `[*]` is one sequence element; `{a,b}` expands to both named fields;
`L` means the shared lineage timestamp expansion
`lineage.source_authority.{available_at,acquired_at}`, `lineage.authority_clocks[*].{decided_at,reviewed_at,accepted_at}` and
`lineage.dependency_lineage.dependencies[*].{observed_at,available_at}`.

| Root | Canonical JSON tagged-UTF8 paths | Heterogeneous fixed-tuple paths | Homogeneous sequence/list paths (direct and distinctive transitive) | Decimal paths | UTC timestamp paths |
| --- | --- | --- | --- | --- | --- |
| Bronze known | `raw_record` (direct `CanonicalJsonObject` arm) | none | `measured_raw_fields`, lineage sequences | any nested number arm remains inside the complete `raw_record` tagged UTF-8 scalar | `L` |
| Bronze rejected record | `raw_record` (direct `CanonicalJsonObject` arm); `raw_kind.value` (direct union) | none | lineage sequences | any number arm remains inside its complete tagged UTF-8 field scalar | `L` |
| Bronze rejected field | `original_value` (direct union) | none | lineage sequences | any number arm remains inside the complete `original_value` tagged UTF-8 scalar | `L` |
| Silver competition | none | none | `source_rows`, lineage sequences | none | `L` |
| Silver team | none | none | `source_rows`, lineage sequences | none | `L` |
| Silver player | none | none | `source_rows`, lineage sequences | none | `L` |
| Silver match | none | none (`team_ids` is homogeneous fixed length 2) | `source_rows`, `team_ids`, lineage sequences | none | `match_start_utc`, `L` |
| Silver action | none | none | `source_rows`, `action_tag_ids`, `action_positions`, `possession_period_sequence.actions`, each sequence action's `action_tag_ids`, lineage sequences | `period_elapsed_seconds`; `action_positions[*].{x,y}`; `possession_period_sequence.actions[*].period_elapsed_seconds` | `L` |
| Silver lineup | none | none | `source_rows`, lineage sequences | none | `L` |
| Silver possession | none | `first_action_order`, `last_action_order` with positions `(int,Decimal,int,int)` | `source_rows`, `contributing_actions`, `action_ids`, and all action sequences | order position 1; every nested SilverAction decimal path | `L` and each nested action's lineage timestamps |
| Silver player-match fact | none | transitive `contributing_possessions[*].{first_action_order,last_action_order}` | `source_rows`, `contributing_lineup_stints`, `contributing_actions`, `contributing_possessions`, `coverage.dimensions`, `coverage.missing_dimensions`, temporal lineage sequences | `coverage.coverage_overall`; `coverage.dimensions[*].coverage`; nested action/possession decimals | `match_start_utc`; all `temporal_proof.{snapshot_as_of_ts,available_at_watermark,valid_from_ts,feature_cutoff_ts}` plus its source/authority/dependency clocks; `L`; nested rows |
| Gold player window | none | `contributing_player_match_keys[*]` with positions `(UUID,UUID,UUID,UUID,str)`; all nested possession order tuples | `source_rows`, `contributing_player_match_facts`, `contributing_player_match_keys`, `coverage.dimensions`, `coverage.missing_dimensions`, all nested fact sequences | Gold coverage decimals and every nested fact/action/possession decimal path | `window_start_utc`, `window_end_utc`, `feature_cutoff_ts`, temporal-proof clocks, `L`, and all nested fact timestamps |

These four direct field occurrences are the complete `CanonicalJsonValue`/concrete-
arm projection roster in the twelve Parquet roots: `BronzeKnownRecord.raw_record`,
`BronzeRejectedRecord.raw_record`, `BronzeRejectedRecord.raw_kind.value`, and
`BronzeRejectedField.original_value`. Each whole present field is exactly one
`CANONICAL_JSON_VALUE_UTF8` scalar. Its `kind`, member tuple and every nested
array/object/member/variant remain inside the tagged logical JSON text; none becomes
an Arrow struct, list, child or recursively decomposed union. The seven-arm support
closure remains authoritative only for strict inverse validation. Present canonical
JSON null is non-null tagged UTF-8 text, never Arrow null; optional outer absence
retains its separately authoritative nullable state.

The census intentionally does not select a descriptor precision, scale, integer
width, child name, or nullability. The producer must freeze those exact values from
the accepted logical constraints and the sole serializer descriptor vocabulary;
fixture-observed maxima are not authority. In particular action seconds/positions
must accommodate the exact `decimal128(22,18)` rule, while derived coverage decimals
must accommodate their exact recomputed Decimal values without rounding or string/
float coercion.

Roots 13–23 are JSON-only and require the explicit
`NOT_APPLICABLE_JSON_ONLY` projection state. Omission, null, or a placeholder
projection is not equivalent.

## 7. High-risk omission and substitution attacks for producer review

1. **Runtime default versus required wire member.** Dropping a defaulted literal
   from canonical schema content would change the serialized object even though the
   constructor can supply it. Review every `D(...)` field as present in canonical
   output and separately record construction requiredness/defaulting.
2. **Authenticity is external to direct product construction.** Every Silver/Gold
   root says `construction_authority_state="semantic_only_unchecked"`. A caller can
   construct an internally coherent object, even with a copied real membership
   digest. Only the accepted completion reader can issue authentic checked products.
   A root schema must not claim that its Pydantic validator proves source completion.
3. **Completion-index binding is stronger than a field equality.** The period model
   checks the frozen index digest, cardinality, scope, order and uniqueness, but does
   not itself recompute `source_completion_membership_sha256`. The guarded reader
   must verify the index content address, source binding, exact one-match scope
   (provider `2499719`, canonical `bad97950-6fac-5cf0-a93c-094f91abbb9b`), period
   `1H` count `901` and membership digest
   `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`,
   period `2H` count `867` and membership digest
   `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`,
   aggregate reconciliation and supplied-population equality. A Boolean, count or
   submitted-population digest is insufficient.
4. **One-lineup-row product authority.** The authorized POC population is exactly
   match `2499719`, team `1631`, player `285508`, stint ordinal `0`, ID
   `591cdf5b-2281-53c4-8225-150313ca2c01`, start `[82,83)`, no end, right-censored,
   ruleset `w04-wyscout-lineup-stint-v1`, no minute bounds/elapsed/per-90, reason
   `suppressed_unsupported_denominator`.
   `SilverLineupStint` enforces interval state but does not hard-code that one
   instance or population count. Review must keep generic schema constraints
   distinct from later exact population/manifest reconciliation.
5. **Season binding is composed authority.** The only W04 season source value is
   strict integer `181150`, reproducing UUID
   `4696aa1f-b512-5d18-af79-33cf031455cf`. `SilverMatch` carries both fields but its
   local validator does not reproduce the season mapping; the accepted build helper
   and Gold readback do. Do not invent a local validator, and do not omit the
   composed identity obligation from product review.
6. **Rejected-field recursive traversal.** Attack a raw object/array containing
   nested canonical null, Decimal, duplicate/out-of-order member state, surrogate,
   mutated discriminator, or forged Pydantic state. Tagged UTF-8 inverse validation
   must reject all drift and must never turn present canonical null into Arrow null.
7. **Strict subevent route.** Attack all strings including numeric-looking forms,
   bool-as-int, null, decimals/exponents, arrays, objects, unknown integers, missing
   event, and label/name substitution. Only a strict admitted integer pair emits;
   every other input remains typed rejected evidence with exact reason.
8. **Equal-clock possession.** Attack input order within an equal clock, two
   controlling teams, dependent contested buffers, and an earlier completed group.
   The group-first rule must be declarative; a simple row-by-row state transition is
   not equivalent.
9. **Causal source traversal.** Fact and possession `source_rows` cover complete
   causal sequences, including other-player actions that determine possession.
   Omitting a non-selected player's causal source row is a completeness failure.
10. **Temporal cutoff.** Attack equality at cutoff for dependency observed/available,
    source acquisition, all authority clocks, snapshot, watermark and fact match
    start. Every specified comparison is strict `<`; the cross-receipt operational
    clock predicate separately uses `started_at <= checked_at <= completed_at`.
11. **Layer-manifest closure.** A valid `LayerManifest` object is not sufficient for
    a complete receipt. Independently reproduce all three physical identities and
    the sole two-key complete-manifest semantic value, exact parent summaries,
    one Gold entry, product/proof bytes and boundary bytes. Rehashing downstream
    wrappers cannot repair an earlier substitution.
12. **Build projection and receipt/result binding.** Attack a sixth authority, sixth
    dependency, 26th projection field, reordered key, historical placeholder,
    second build hash, changed role/payload union arm, cross-run/build path, wrong
    manifest order, proof-array drift, or final-recheck digest drift.
13. **Schema inference.** Empty and nonempty lists, different canonical JSON arms,
    nullable observations and fixture integer maxima must generate the identical
    accepted schema. Caller schema/digest/callback/equivalent object cannot select
    descriptor content.
14. **Physical type exactness.** Mutate integer width/signedness, Decimal precision/
    scale, timestamp unit/timezone, field/list/struct child nullability, tuple child
    name/order/position, list child name, or any recursive metadata. Each mutation
    must fail exact schema equality before write/read acceptance.
15. **Root and dependency closure.** Exactly the 23 roles in Section 3 exist, with
    earlier-only dependencies from the readiness audit. A support type is inlined
    transitively, not promoted to a 24th root. JSON-only roots never acquire an Arrow
    schema. No product/aggregate identity enters root content.

## 8. Oracle boundary

This census describes the frozen inputs and the predicates an eventual independent
review must reproduce. It does not evaluate a producer candidate, approve any schema
content, choose physical descriptor details, calculate schema bytes or schema
content digests, or authorize aggregate/product materialization.

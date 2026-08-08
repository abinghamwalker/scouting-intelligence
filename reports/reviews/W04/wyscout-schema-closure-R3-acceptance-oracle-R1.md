# W04 schema-closure R3 acceptance oracle R1

- Task: `W04-WYSCOUT-SCHEMA-CLOSURE-R3-ACCEPTANCE-ORACLE-01-R1`
- Status: implementation-independent expected-value evidence; not candidate review or acceptance
- Candidate boundary: `wyscout_schema.py`, `formats.py`, their focused tests and the R3 producer return were not opened, imported, executed or judged

## 1. Frozen-input readback

Every packet-fixed binding reproduced before analysis.

| Input | Required and observed SHA-256 |
| --- | --- |
| `wyscout_data.py` | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` |
| `wyscout_build.py` | `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16` |
| corrected constraint census R2 | `3ac167f4a63f26d930abe039ec7417637d204f984db6f0cc578dd322526c2120` |
| schema-closure R2 master rework | `9c5092ccf75e4a77ebdb7079a1a3b4360b8b96e52823189355a1cd8e7953a76d` |
| canonical-Decimal authorization | `cddc7fae1ac256b2312a34dc1291dddebdff35162321b0215580103ba6569b5e` |

Additional read-first authority identities reproduced during the oracle analysis:
R20 `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`,
R21 `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`,
readiness audit `f9961082a27b949da6b9c1647b50f9ce18b6862c66fb8c104826c4b20ca746a0`,
R4 receipt audit `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222`,
and build/product authority `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d`.

No frozen-authority contradiction was found. The corrected tagged-JSON boundary and
the additive Decimal boundary compose: a `CanonicalJsonNumber.value` nested inside a
complete `CanonicalJsonValue` field remains inside that field's tagged UTF-8 scalar;
it is not a separately projected Decimal field.

## 2. Reproduction convention

Corpus digests below use this report-only comparison encoding:

```python
json.dumps(
    normalized_value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

Enums are replaced by `.value`, Pydantic rows by `model_dump(mode="json")`, tuples
by arrays, sets by sorted arrays, and mappings by string keys. This is an oracle
comparison encoding only; it does not create or alter any product digest path.

The exact validator inventory is reproducible without candidate imports by iterating
`vars(wyscout_data)` and `vars(wyscout_build)`, selecting classes with
`__pydantic_decorators__`, and reading each `model_validators` member. The result is
`51` distinct validator bodies and `61` effective class bindings: the difference is
the inherited `WyscoutProductRow` validator on nine concrete rows and the inherited
raw-source-row validator on `WyscoutSourceRowReference`. There are no field-validator
bodies in this closure.

## 3. Exact runtime validator oracle

Every row below names the real owning model, only resolvable runtime operand paths,
the operation, and the exact constants or corpus references. All objects are strict,
frozen and `extra="forbid"`; type/field constraints remain conjunctive with these
whole-object predicates.

### 3.1 Canonical JSON, source, authority and lineage

| Owner and validator | Exact executable predicate |
| --- | --- |
| `CanonicalJsonNumber.number_is_finite` | `value.is_finite()` must be true. |
| `CanonicalJsonMember.key_is_unicode_scalar_text` | For every character in `key`, its code point is outside `U+D800..U+DFFF`. |
| `CanonicalJsonObject.members_are_unique_and_sorted` | `keys=tuple(member.key for member in value)`; require `len(keys)==len(set(keys))` and `keys==tuple(sorted(keys))`. |
| `SourceUseClassification.prohibit_unlicensed_use` | If `use_class==prohibited`, all of `derived_data_allowed`, `internal_review_allowed`, `export_allowed` are false; `attribution_required` implies non-null `attribution_text`. |
| `WyscoutRawSourceRowReference.source_row_is_manifested` | `source_manifest_id` equals C1; `completion_relative_path` selects exactly one C2 row; `source_sha256` equals its digest; `0 <= source_record_ordinal < row_count`. This same inherited body is effective on `WyscoutSourceRowReference`. |
| `WyscoutSourceRowReference.record_kind_matches_completion_path` | `record_kind` is identical to the C2 row's `record_kind`. |
| `WyscoutSourceRecordEnvelope.envelope_is_exact` | Derive `source_row_reference`; require its `raw_record_sha256 == SHA256(canonical_raw_json_bytes(raw_record))`. |
| `RawKindEvidence.evidence_matches_state_and_framed_digest` | Derive `raw_kind_state` from `value_present` and the exact `value` arm: missing requires typed null; present null -> `null`; non-string -> `non-string`; known seven source-kind strings reject; other strings use safe regex `^[A-Za-z][A-Za-z0-9_-]{0,63}$` vs unsafe. Require exact canonical `envelope_bytes`; require `raw_kind_sha256=SHA256(b"w04-raw-kind-v1\x00" || UINT64_BE(len(envelope_bytes)) || envelope_bytes)`. |
| `WyscoutAuthorityReference.reference_is_the_accepted_authority` | The complete seven-field `model_dump(mode="json")` equals the C3 data-authority row selected by `authority_kind`. |
| `WyscoutAuthorityClock.clocks_are_the_accepted_authority_clocks` | `(decided_at,reviewed_at,accepted_at)` equals the C3 triple selected by `authority_kind`, and `decided_at <= reviewed_at <= accepted_at`. |
| `WyscoutSourceAuthority.source_authority_is_exact` | Exact C1 manifest ID/digest, no-club tenant, release `2020-01-28T14:24:27Z`, acquisition `2026-07-29T15:51:08.598589Z`, and exact restricted-rights object from C3. There is no `provider` operand. |
| `DependencyLineage.dependencies_are_unique` | `(dependency.kind,dependency.dependency_id)` is unique across `dependencies`. |
| `WyscoutRowLineage.lineage_is_closed` | Manifest ID/digest and completion-index digest equal C1; `authority_references` equal the four C3 rows in enum order; `authority_clocks` equal four C3 rows; `source_authority` equals the preceding exact object; physical `(completion_relative_path,source_record_ordinal)` keys are sorted unique; dependency lineage passes C8 exact five-row order/content/hash. |

### 3.2 Bronze, entity, action, lineup and possession

| Owner and validator | Exact executable predicate |
| --- | --- |
| `BronzeKnownRecord.raw_record_is_preserved_once` | Recompute canonical raw digest and require equality to both `raw_record_sha256` and `source_row.raw_record_sha256`; require `source_row in lineage.source_rows`; `measured_raw_fields` equals every top-level `$.<member.key>` and member kind in raw-member order; tenant/no-club, lineage tenant and C3 rights are exact. |
| `BronzeRejectedRecord.rejected_record_is_closed` | Recompute `raw_record_sha256`; require exact tenant/rights and lineage tenant; at least one lineage row equals the raw reference on completion path, source digest, ordinal and raw-record digest. |
| `BronzeRejectedField.rejected_value_is_exact` | `source_row.record_kind==record_kind`; `original_value.kind==measured_json_type`; recompute `original_value_sha256`; `field_authority` equals FIELD C3 row; `(record_kind,json_path)` selects a C4 row. For `action/$.subEventId`, require `PRESERVE_UNMAPPED`, C6 reason by exact arm, and reject a C5-admitted integer pair. Otherwise event evidence is null, kind belongs to registry kinds, `TRANSFORM` cannot be rejected, and decision/reason equal `<registry decision>`/`FIELD_V2_<decision>`. Tenant, rights and source membership are exact. |
| `WyscoutProductRow.tenant_is_the_fixed_poc_context` | Effective on the base plus all eight Silver rows and the Gold row. Exact no-club tenant; `source_completion_index_sha256` equals C1 and lineage; tenant equals source authority; selected `(path,ordinal)` keys are sorted unique; every selected row occurs in lineage. |
| `SilverCompetition.competition_identity_is_exact` | Exactly one selected `competition` row; `competition_id=canonical_source_uuid(competition,competition_source_id)` with strict positive ID. |
| `SilverTeam.team_identity_is_exact` | Exactly one selected `team` row; `team_id=canonical_source_uuid(team,team_source_id)` with strict positive ID. |
| `SilverPlayer.player_identity_is_exact_and_nonzero` | Exactly one selected `player` row; `player_id=canonical_source_uuid(player,player_source_id)` with strict positive ID. |
| `SilverMatch.match_identity_and_teams_are_exact` | Exactly one selected `match` row; `source_partition` equals that path's country; `match_id=canonical_source_uuid(match,match_source_id)`; `team_ids` has two distinct UUIDs ordered by `.bytes`. It does not establish season 181150. |
| `ActionPosition.bound_flag_preserves_anomalies_without_clamping` | Validate `x` and `y` at exact `decimal128(22,18)` capacity/lexical scale; `within_accepted_bounds is (0 <= x <= 100 and 0 <= y <= 100)`. Values are never clamped. |
| `PossessionSequenceAction.sequence_action_is_exact` | `source_row.record_kind==action`; ordinal equals source-row ordinal; `action_id=canonical_source_uuid(action,source_event_record_id)`; `period_elapsed_seconds` finite and `>=0`; `action_tag_ids==tuple(sorted(set(action_tag_ids)))`. |
| `PossessionPeriodSequence.period_sequence_is_complete_unique_and_ordered` | Index digest equals C1; `period_action_count==len(actions)`; every action shares `match_id` and `action_period_code`; action order `(period_rank,period_elapsed_seconds,source_record_ordinal,source_event_record_id)` is sorted unique; action IDs and physical `(path,ordinal)` rows are independently unique. It does not prove C7 source completeness. |
| `SilverAction.action_is_strict_and_orderable` | Exactly one action source row; UUID from `action_source_id`; `source_event_record_id==action_source_id`; ordinal equals source row; seconds finite, nonnegative and exact `decimal128(22,18)` with `event_sec_source_scale`; tags sorted unique; non-null subevent implies event and C5 pair; predicate state is recomputed from C5/C6 possession constants; sequence match/period/lineage scope is equal; this action occurs exactly once in the sequence and its twelve shared evidence fields are equal; eligibility equals membership in deterministic possession groups. |
| `NominalMinuteInterval.interval_is_one_nominal_minute` | `upper==lower+1`. |
| `SilverLineupStint.stint_bounds_are_interval_derived` | If `end_interval is None`: `right_censored=true` and both minute bounds null; else `start_interval` exists, `right_censored=false`, and bounds equal `max(0,end.lower-start.upper)` / `max(0,end.upper-start.lower)`. Exactly one match source row. `elapsed_minutes` remains null, `per90_eligible=false`, suppression fixed by literal fields. It does not establish the C9 one-row population. |
| `SilverPossession.possession_is_one_ordered_same_period_sequence` | Contributing actions are unique and ordered by `(action_order_key,action_id.bytes)`; every action shares one equal complete sequence; `action_ids` equal exactly one deterministic resolved group for `team_id`; actions share build/tenant/lineage/match/period and resolved eligibility; control/restart team equals possession team; `source_rows` equals sorted complete-sequence causal rows; `action_ids`, `first_action_order`, `last_action_order` derive from actions. Equal-clock grouping is group-first: multiple controlling teams clear only the dependent current group/buffer, preserving earlier completed groups. |
| `ActionSubeventOutcome.emitting_and_rejected_states_are_disjoint` | Recompute `(canonical_value,rejected_raw_value,reason_code)` from `action_event_taxonomy_id` and exact `raw_subevent` arm. Emit only a strict integer in C5 with strict integer event; otherwise retain the exact raw value and select the C6 reason. |

### 3.3 Coverage, temporal, fact, Gold, paths and manifests

| Owner and validator | Exact executable predicate |
| --- | --- |
| `GoldCoverageDimension.coverage_is_exact` | `numerator<=denominator`; reasons sorted unique. `authority_missing/failed` -> numerator and coverage zero, nonempty reasons, no zero proof. Positive denominator -> no zero proof, exact precision-38 `Decimal(numerator)/Decimal(denominator)`, state complete iff equal counts else partial, complete has no reasons and partial has reasons. Zero coordinate/possession may be authority-proven coverage one using respectively FIELD/POSSESSION; unproven optional zero is missing/zero; every mandatory zero is missing/zero with reasons and no proof. |
| `GoldCoverage.six_dimensions_are_exact` | Dimension names equal all six enum values in enum order; `missing_dimensions` equals the lexical set whose states are partial/missing/authority-missing/failed; `coverage_overall==min(dimension.coverage)`. |
| `W04ApplicabilityAssessment.reasons_are_sorted_unique` | `reason_codes` sorted unique; `W04_DATA_READY` forbids reasons; every other state requires reasons. |
| `W04SemanticTemporalProof.proof_has_exact_five_strict_dependencies` | Completion digest C1; dependencies equal C8 order/content and unique 1 source/1 identity/3 feature kinds; source authority and four clocks exact; all dependency observed/available, source acquisition, and every authority clock are `< feature_cutoff_ts`; watermark is max availability and `< cutoff`; `valid_from_ts=max(snapshot,watermark)`; snapshot `< cutoff`; both lineage hashes recompute from five rows plus index; source manifests exactly singleton C1; feature schema exact C8. |
| `SilverPlayerMatchFact.player_match_key_and_state_are_exact` | Source manifest C1; lineup IDs unique/byte-ordered and each shares build/tenant/lineage/match/player/team; presence equals `bool(lineups)`; actions unique/canonical and share identity/scope; at least lineup or action evidence; per match/period the selected player actions equal the complete sequence's player subset; possessions unique/order-canonical with byte-semantically equal selected action evidence and no identity leak; each eligible selected action belongs to exactly one possession, ineligible to zero; source rows equal lineup plus all causal sequence rows; three counts derive exactly; lineage/source/clocks equal proof; match start `< cutoff`; coverage/applicability recompute. |
| `GoldFeatureValues.component_counts_cannot_exceed_actions` | Both `coordinate_known_action_count<=action_count` and `resolved_possession_action_count<=action_count`. |
| `GoldPlayerWindow.gold_key_and_feature_state_are_exact` | Exact role context UUID `3a17850f-5ac4-5ad8-ac9a-b753f10bdf77`, version/state; start `<` end; cutoff/lineage/source/clocks/feature digest equal proof and C8; fact keys sorted unique and explicit key tuple equal; facts share build/tenant/C1 source/player/competition/season/lineage/proof, lie in half-open window and before cutoff; source rows equal union; four features are sums plus distinct match count; six-dimensional coverage and applicability recompute. |
| `WyscoutProductPath.path_is_the_exact_role_template` | `relative_path` is NFC and full-matches the exact `_PATH_PATTERNS[path_role]`; every UUID token round-trips canonically; every UTC token parses as a real `%Y%m%dT%H%M%S%fZ` instant. |
| `ParentLayerManifest.parent_path_is_exact_and_safe` | `layer != GOLD`; path exactly `data/manifests/wyscout/v5/<layer-lower>/<build_id>.manifest.json`. |
| `LayerManifestEntry.entry_binds_owner_rights_and_partition_order` | Serializer equals sole owner of path role; schema role equals path role; partition values equal sorted unique path `key=value` segments; classification is C3; parent paths sorted unique; Bronze has none, Silver/Gold have nonempty preceding-layer parents, each containing the same build ID. |
| `LayerManifest.layer_order_and_entries_are_exact` | Manifest path role/layer/filename/build agree; C1 source/index, tenant, rights, source clocks, authority clocks, feature digest and C8 lineage/hash exact; entry paths sorted unique, same layer/build; Bronze no parent, Silver exactly Bronze, Gold exactly Silver, with parent build equal. |

### 3.4 Build, receipt and child-result validators

| Owner and validator | Exact executable predicate |
| --- | --- |
| `WindowIdentity.identity_reproduces_frozen_uuid` | R20 canonical bytes length `250`, SHA `3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327`; UUIDv5 URL namespace `urn:scouting-intelligence:w04:wyscout:window-definition:v1`, then name `single-match-poc:<sha>`, yields `a0af8d56-e41d-5467-b46e-82887c4861e0`. |
| `AuthorityRow.equals_accepted_row` | Complete seven-field row equals the C3 build-authority row selected by `authority_kind`; build composition has five rows, while data lineage has four. |
| `DependencyRow.clocks_are_ordered` | Parsed `observed_at<=available_at`; there are no cutoff operands on this owner. |
| `PreBuildProjection.exact_projection` | `_validate_common`: exact five C3 authority rows, five C8 dependency rows, watermark/cutoff/feature/identity/role/source/tenant/window constants; neither v1 aggregate placeholder; field order exactly C10 pre-build 25 keys. |
| `RebuildInvocation.exact_invocation` | Exact five authority and dependency rows; `code_manifest_id` UUIDv5 from digest; v1 product/schema placeholders forbidden; post-hash key order exactly C10; removing only `build_id`, inserting only projection schema version and retaining other 24 values produces projection whose sole hash equals `build_id`. |
| `TemporalBoundaryReceipt.exact_paths` | Relative paths safe; Gold manifest exact same-build path; Gold product full-matches the exact one-match path; `gold_relative_path_sha256=SHA256(gold_product_relative_path UTF-8)`. Literal `verification_state=STRICT_BEFORE_CUTOFF_PASS`, never `VERIFIED`. |
| `RebuildInvocationReceipt.exact_receipt` | Build equals invocation; `started_at<=completed_at`; summaries exactly Bronze/Silver/Gold with same-build paths; exactly one boundary; its safe path equals deterministic build/run/Gold-relative-path digest path. |
| `EntrypointSourceResult.exact_role_path` | `relative_path` equals last token of C10 admission or rebuild argv by role. `descriptor_number` is any strict integer `3..2147483647`, not fixed to 3. |
| `PreBuildAdmissionResult.exact_admission_result` | Prefix from admission UUID; component keys exactly ordered C10 twenty; proof digest recomputed; canonical base64url manifest 1..12,000,000 bytes, digest-equal, closed roster; schema/repository/environment equal result; environment digest covers components; each proof covers its named component. |
| `PostBuildIdRebuildResult.exact_rebuild_result` | Prefix and receipt path derive from build/run; layer summaries exact Bronze/Silver/Gold and paths; final recheck build/run and receipt digest equal; layer-set digest recomputed from all summary rows. |
| `ChildResultEnvelope.exact_role_payload_binding` | Entrypoint role equals child role. Admission requires `CODE_ENVIRONMENT_MANIFEST`, admission arm and repository equality. Rebuild requires `REBUILD_COMPLETION`, rebuild arm and repository/environment/entrypoint equalities. Ordered argv digest equals SHA of the exact selected C10 argv. |

### 3.5 Explicit rejection of the preserved R2 false operand claims

The following conceptual operands must not be emitted as runtime-field paths:

| Owner | Forbidden R2 operands | Correct runtime operands / classification |
| --- | --- | --- |
| `ActionPosition` | `in_unit_interval` | `x`, `y`, `within_accepted_bounds`; bounds are `0..100`. |
| `DependencyRow` | `valid_from`, `feature_cutoff_ts` | `observed_at`, `available_at`; relation is `<=`. |
| `PossessionPeriodSequence` | `completion_index_sha256`, `match_source_id`, `action_count`, `ordered_membership_sha256` | `source_completion_index_sha256`, `match_id`, `period_action_count`, `actions`; exact population/digest is external E1. |
| `PossessionSequenceAction` | `action_source_id`, `match_source_id`, `raw_record_sha256` | `source_event_record_id`, `match_id`, `source_row` plus the remaining declared fields. |
| `RawKindEvidence` | `state`, `envelope_sha256`, `witness` | `raw_kind_state`, `envelope_bytes`, `raw_kind_sha256`, `value_present`, `value`. |
| `SourceUseClassification` | `licence_use_class`, `commercial_use_allowed`, `redistribution_allowed` | `use_class`, `derived_data_allowed`, `internal_review_allowed`, `export_allowed`, attribution fields. |
| `WyscoutAuthorityClock` | `available_at`, `valid_from` | `decided_at`, `reviewed_at`, `accepted_at`. |
| `WyscoutRawSourceRowReference` | `raw_record_sha256` | Only manifest ID, completion path, member digest, ordinal; typed subclass adds kind/raw digest. |
| `WyscoutSourceAuthority` | `provider` | Manifest ID/digest, tenant, `available_at`, `acquired_at`, classification. |
| `SilverMatch` / `SilverLineupStint` | season-181150 or sole lineup population as local predicates | External E2; neither generic validator establishes them. |

## 4. Guarded-reader and composed external authority oracle

These are deliberately separate from runtime model validators.

| ID | Frozen authority source | Exact external operands and operation |
| --- | --- | --- |
| E1 source completion | build/product authority `completion_index_binding` (C7), frozen index content address C1 | Guard-read only the fixed index path; verify content address, source manifest/member binding, canonical action ordering and uniqueness, aggregate source count, and exact supplied sequence/set equality. Exact selected match `2499719` / canonical `bad97950-6fac-5cf0-a93c-094f91abbb9b`; 1H count/digest `901`/`473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`; 2H `867`/`b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`; reject missing/additional/duplicate/reordered/stale/cross-period rows and every caller Boolean/count/witness/submitted-population-only digest. |
| E2 season and lineup | accepted season/lineup decision C9 plus build helper/readback | Strict integer `181150` alone reproduces season UUID. Exact one-row lineup population with source/member/ordinal/raw digest, source IDs and UUIDs, start `[82,83)`, no end/bounds/elapsed, right-censored, per90 false and fixed suppression. Reject omission/addition/duplicate/reorder/alternative ordinal or inferred terminal/minutes. |
| E3 checked-product issuance | completion reader plus runtime roots whose state is `semantic_only_unchecked` | Only after E1 exact equality may checked Silver/Gold be issued; direct Pydantic consistency, copied count, membership digest or Boolean is insufficient. Causal source rows include other-player actions used by possession semantics. |
| E4 build projection composition | C3 five build authorities, C8 dependencies, C10 keys, build/product authority | Exact 25-key preimage; one SHA path; post-hash inverse replaces only schema-version/build-ID; no sixth authority, dependency, 26th field, alternate key order, v1 placeholder or second build hash. |
| E5 layer semantic closure | R4 audit | Guard-read and closed-schema-validate all three complete manifests. Sole preimage has exactly keys `layer_manifest`, `semantic_schema_version`, with complete parsed manifest and literal `w04-wyscout-layer-manifest-semantic-v1`; R20 canonical JSON without LF; SHA-256. Reproduce each summary physical digest/size and semantic digest independently before Gold selection. |
| E6 parent and population closure | R4 audit plus C11 receipt constants | Bronze parent empty; Silver exactly Bronze physical summary; Gold exactly Silver; all same build. Gold manifest yields exactly one ordered Gold product; boundary population equals it. Reopen Gold and boundary bytes and bind path/hash/size/semantic/count/lineage/temporal/build/run. |
| E7 receipt clocks/results | R4 audit and build contract composition functions | Exact three summaries, one boundary, `started_at<=checked_at<=completed_at`; downstream rehash cannot repair a substituted layer semantic; child result binds role/payload/argv/environment/repository. |
| E8 schema acceptance | readiness audit, corrected R2 census and Decimal authorization | Exactly 23 roots, first 12 descriptor-bearing, last 11 explicit `NOT_APPLICABLE_JSON_ONLY`; earlier-only dependencies; schema only from accepted descriptor; exact inverse before logical equality; exactly the CJV scalar paths and exactly the two C12 Decimal paths. This oracle supplies expected values but cannot approve the candidate. |

## 5. Frozen constant corpora

### C1 core source/build constants

`source_manifest_id=4e16bdb5-afe7-5601-88ad-adc124cfce3b`,
`source_manifest_sha256=8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`,
`source_completion_index_sha256=46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`,
tenant `65a43912-d412-5ff9-a364-7f84d1ad6c5d`, club null, feature digest
`49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`,
identity bundle `31638732-5b25-57db-9eb4-8e943a47a387` /
`4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`.

### C2 admitted source-member map

Normalized count `15`, comparison SHA-256
`dbfe3ff7dbf3be827e27165c49b3e8861b538e5cf33003cfde784754daa465f4`.

| Path | Kind | Country | Rows | SHA-256 |
| --- | --- | --- | ---: | --- |
| `objects/competitions.json` | competition | null | 7 | `39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1` |
| `objects/teams.json` | team | null | 142 | `9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d` |
| `objects/players.json` | player | null | 3603 | `877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e` |
| `objects/eventid2name.csv` | event-taxonomy | null | 36 | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` |
| `objects/tags2name.csv` | tag-taxonomy | null | 59 | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` |
| `archive-members/matches_England.json` | match | england | 380 | `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29` |
| `archive-members/matches_France.json` | match | france | 380 | `851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea` |
| `archive-members/matches_Germany.json` | match | germany | 306 | `6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9` |
| `archive-members/matches_Italy.json` | match | italy | 380 | `afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725` |
| `archive-members/matches_Spain.json` | match | spain | 380 | `9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce` |
| `archive-members/events_England.json` | action | england | 643150 | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` |
| `archive-members/events_France.json` | action | france | 632807 | `18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317` |
| `archive-members/events_Germany.json` | action | germany | 519407 | `2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3` |
| `archive-members/events_Italy.json` | action | italy | 647372 | `b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84` |
| `archive-members/events_Spain.json` | action | spain | 628659 | `b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154` |

Executable source: sorted `_SOURCE_PATH_ROWS.items()` in `wyscout_data.py`, normalized
as `{path,record_kind,country,sha256,row_count}`.

### C3 authority rows, clocks and rights

- Four data authority references, exact order FIELD/POSSESSION/SUPPORTED_FEATURE/IDENTITY:
  comparison SHA `d1201327fa99e739b126ddc484982fa5afeebd207f7bafca8b7553ea9abf5e5e`.
- Four authority clocks in that order: comparison SHA
  `e6149227c79f04acee10ef5ffce5ad92a386b0c21d095ca7a803c311a7b79153`.
- Five build authority rows append only SEASON_LINEUP_PRODUCT_BINDING: comparison SHA
  `af3b07e42bdfe3cd99fb680c61c8aea8d10a4a25dd397791bbb25f87e06c2cec`.

| Kind | Candidate SHA | Review SHA | Acceptance SHA | decided / reviewed / accepted |
| --- | --- | --- | --- | --- |
| FIELD | `93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959` | `76c4744d302b4c6d86f4d537498695e365f0d3c733211bfafcb1e5c2805c0886` | `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436` | `2026-07-30T20:22:17Z` / `2026-07-30T21:15:45Z` / `2026-07-30T21:21:23Z` |
| POSSESSION | `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881` | `c1e249c377d11258415cea84e83f0d3742436ebcb7aa640b885c44d245cb1e97` | `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1` | `2026-07-30T22:14:21Z` / `2026-07-31T08:24:02Z` / `2026-07-31T08:28:40Z` |
| SUPPORTED_FEATURE | `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f` | `a692cc4aaa002882f92209256f1bdecb96b3eb6bdba8a9bc3f645569daa31c73` | `d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c` | `2026-07-31T08:37:00Z` / `2026-07-31T10:07:30Z` / `2026-07-31T10:15:16Z` |
| IDENTITY | `9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c` | `62295d6a1da681fbec23285ca6c74124e3ef44fe3962c1472f0523ef46fb2a19` | `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86` | `2026-07-31T12:44:27Z` / `2026-07-31T14:11:16Z` / `2026-07-31T14:15:26Z` |
| SEASON_LINEUP_PRODUCT_BINDING (build only) | `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e` | `3f88335db70609e90f0d02cbbc206752479f5300e196329fc48f07154899cf0f` | `6cbf2cd2aea87489854eee208ee4cbb3f7d3dc2c603d32aa306515418863c27e` | composed build authority; not a data-lineage clock row |

Rights: `restricted`, derived/internal review true, export false, attribution required,
text exactly `Data source: Pappalardo et al., Soccer match event dataset, supplied by Wyscout, figshare collection v5, licensed CC BY 4.0.`

Exact row IDs are mechanically selected by `accepted_authority_references()` /
`accepted_authority_rows()`: candidate IDs `w04-wyscout-field-registry-v2`,
`w04-wyscout-possession-taxonomy-v2`, `w04-wyscout-supported-count-features-v1`,
`w04-wyscout-identity-ruleset-v1`, and
`w04-wyscout-season-lineup-product-binding-decisions-v1`. Review IDs are
`w04-wyscout-field-semantic-independent-review-v2-R1`,
`w04-wyscout-possession-semantic-independent-review-v2-R1`,
`w04-wyscout-supported-feature-registry-independent-review-R1`,
`w04-wyscout-identity-ruleset-independent-review-R1`, and
`w04-wyscout-season-lineup-product-binding-independent-review-R1`. Acceptance IDs
are `w04-wyscout-field-semantic-acceptance-v2`,
`w04-wyscout-possession-semantic-acceptance-v2`,
`w04-wyscout-supported-feature-registry-acceptance-v1`,
`w04-wyscout-identity-ruleset-acceptance-v1`, and
`w04-wyscout-season-lineup-product-binding-acceptance-v1`. Their complete
seven-field rows, including these exact IDs and the digests above, are committed by
the two comparison hashes.

### C4 field registry

Exactly `119` normalized rows; comparison SHA
`f9d72b83b51a6a908443f8bd0b342ae9590158a835e10900b3a69424d762912d`.
Each row is `{record_kind,json_path,decision,admitted_kinds}` with kinds sorted.
The authoritative embedded corpus is `_FIELD_REGISTRY_ROWS_TEXT` parsed by
`_field_registry_rows()`; its accepted candidate digest is
`93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959`.
The parser itself asserts count 119. Executable extraction is:

```python
rows = [
    {
        "record_kind": k[0].value,
        "json_path": k[1],
        "decision": v[0],
        "admitted_kinds": sorted(x.value for x in v[1]),
    }
    for k, v in sorted(
        _FIELD_REGISTRY_ROWS.items(), key=lambda item: (item[0][0].value, item[0][1])
    )
]
```

### C5/C6 strict subevent and possession constants

The exact 36 admitted pairs, comparison SHA
`561669e7d61585151611fab182ced94848dc1c3b5a99dcf6373db78b8f6429ff`:

```text
(1,10..13); (2,20..27); (3,30..36); (4,40); (5,50..51); (6,60);
(7,70..72); (8,80..86); (9,90..91); (10,100)
```

Exact seven non-emitting reasons, in enum order, comparison SHA
`85241c55c65b2f0d9c023bb4581e0dcc05a82ea0871cbb0771c177d25de5f00b`:

```text
ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED
ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER
ACTION_SUBEVENT_NULL_UNMAPPED
ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED
ACTION_SUBEVENT_ARRAY_UNMAPPED
ACTION_SUBEVENT_OBJECT_UNMAPPED
ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY
```

Possession corpus comparison SHA
`ed36cd10970b81e4e6092f59a4a49af4d391d9505ff4fade1abe74b353a866d9`:

- contested `(1,10..13)`;
- dead-ball preceding `(2,20),(2,21),(2,22),(2,27),(5,50),(6,60)`;
- dead-ball unassigned `(2,23),(5,51)`;
- non-control admin `(2,24),(2,26)`;
- explicit unmapped `(2,25),(4,40),(9,90),(9,91)`;
- restart `(3,30..36)`;
- control `(7,70..72),(8,80..86),(10,100)`.

Tags must be sorted unique. Restart/control additionally requires a team. The
decision order and equal-clock algorithm in Section 3.2 are part of this corpus;
the pair sets alone are not sufficient.

### C7 completion-index binding

The exact 13-key authority object has comparison SHA
`1927b170924e764cd01351c699d2173e0edbf9a58360866b11c9abeccf6ca097`.
Its exact identity values are C1, index path
`data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`,
source member `archive-members/events_England.json` /
`301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` /
`643150`,
provider/canonical match `2499719` / `bad97950-6fac-5cf0-a93c-094f91abbb9b`,
and the exact two period rows in E1. The eight verifier/rejection tokens in the
authority object are operands, not labels replacing their values.

### C8 five dependency rows

Comparison SHA `27dc516cf9b5e9c13eaa6f29926115ca679113640df635da6ae1d17397e15bf5`;
accepted lineage hash with C1 index
`ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d`.

| Kind / ID | Digest | observed -> available |
| --- | --- | --- |
| source_manifest / `4e16bdb5-afe7-5601-88ad-adc124cfce3b` | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | `2020-01-28T14:24:27Z` -> same |
| identity_evidence / `31638732-5b25-57db-9eb4-8e943a47a387` | `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80` | `2026-07-31T12:44:27Z` -> `14:15:26Z` |
| feature_schema / `32351f4a-4c59-567f-87b5-15364a8d4f47` | `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f` | `2026-07-31T08:37:00Z` -> `10:15:16Z` |
| feature_schema / `342eb513-ad1c-5d65-aea5-abc2d9c14383` | `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881` | `2026-07-30T22:14:21Z` -> `2026-07-31T08:28:40Z` |
| feature_schema / `f65e539c-0021-53b6-9b20-27bc2aefad3d` | `93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959` | `2026-07-30T20:22:17Z` -> `21:21:23Z` |

### C9 exact season and lineup population

Decision physical SHA `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e`.
Season object comparison SHA `bceaf3eb5da3874cb93ca097b8e0d02d165196e28f12a390fd865c119281495b`;
lineup object comparison SHA `256a83de64cbc134192d6f472a331d93aef2f48cfc17b1eb67d5b74412346ee8`.

- strict source integer `181150`, name `figshare-v5:181150`, UUID
  `4696aa1f-b512-5d18-af79-33cf031455cf`;
- exact lineup: match source/canonical `2499719` /
  `bad97950-6fac-5cf0-a93c-094f91abbb9b`; team `1631` /
  `5b353635-819b-5bd1-8ca2-5a7364042a96`; player `285508` /
  `be8da881-2b15-513f-978f-6bb3865bc8e2`; ordinal `0`; ruleset
  `w04-wyscout-lineup-stint-v1`; ID `591cdf5b-2281-53c4-8225-150313ca2c01`;
  start `{lower:82,upper:83}`, end/bounds/elapsed null, right-censored true,
  per90 false, suppression `suppressed_unsupported_denominator`;
- source match member `archive-members/matches_England.json`, digest
  `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29`,
  count `380`, ordinal `379`, raw digest
  `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`.

### C10/C11 build and receipt constants

- Pre-build exact 25-key order:
  `authority_rows, code_manifest_id, code_manifest_sha256, dependency_rows,
  dependency_watermark, environment_digest, feature_cutoff_ts, feature_schema_hash,
  identity_bundle_id, identity_bundle_sha256, local_resource_digest,
  product_contract_digest, role_context_id, role_context_state,
  role_context_version, schema_bundle_digest, schema_version,
  selected_lock_closure_digest, source_manifest_id, source_manifest_sha256,
  tenant_club_id, tenant_id, window_definition_id, window_end_utc,
  window_start_utc`; comparison SHA
  `644984459e6c0c431125a47c69ce755aa04899d710c59d34593e6eec7d43dce4`.
- Post-hash order replaces only `schema_version` with `build_id` at position 2;
  comparison SHA `affe479019a5e8c0a07e952b2e79176d43f045044f4c19a0d4cc16f31e5a114a`.
- Window `[2017-08-11T00:00:00Z,2017-08-12T00:00:00Z)`, selected/snapshot
  `2017-08-11T18:45:00Z`, cutoff `2026-08-01T00:00:00Z`, watermark
  `2026-07-31T14:15:26Z`; comparison authority SHA
  `847d5d36434ba35271288c324bd02ecc794708c85772f662a355f907ab325a6f`.
- Exact component-key count 20 and comparison SHA
  `e76f1e7325e92b94bed90c5adc15ea3c7451796962c87e81c0e792b6be0b9ac8`:
  `child_result_contract_digest, editable_root_digest, environment_values_digest,
  executable_census_digest, extracted_runtime_digest,
  installed_record_runtime_digest, interpreter_digest,
  local_launcher_control_digest, local_resource_digest, lock_inputs_digest,
  process_launch_contract_digest, pyc_policy_source_map_digest,
  selected_lock_closure_digest, selector, selector_bootstrap_digest, stdlib_digest,
  uv_physical_sha256, uv_version, venv_bootstrap_digest, wheel_declaration_digest`.
- Admission argv is exactly
  `["uv","run","--locked","--no-sync","python","-S","-B","scripts/admit_wyscout_v5_runtime.py"]`,
  comparison SHA `ff4326bfb665ed302173149d98ef444a97512ffc3724d96a68eb88f8322c6a9c`;
  rebuild changes only the last path to `scripts/rebuild_wyscout_v5.py`, comparison
  SHA `c5232e3658f08d2435fe9123b5c50770f3600155ef994cbea9096aaea8a61e24`.
- Receipt-contract two-object comparison SHA
  `ca4e37152b14d3bd4545ec943a2949809f5635bebf9d250e15f5a9bd70789d5b`;
  boundary state exactly `STRICT_BEFORE_CUTOFF_PASS`, row count 1; invocation state
  `COMPLETE`, exact three layer summaries and one boundary.
- R4 layer-semantic preimage is exactly
  `{"layer_manifest":<complete parsed LayerManifest object>,"semantic_schema_version":"w04-wyscout-layer-manifest-semantic-v1"}`
  under R20 canonical UTF-8 with no LF; no entry/physical/other-layer/downstream
  digest is substitutable.

## 6. Exact Decimal projection oracle

### 6.1 Owning fields and all twelve-root reachability

There are eight independently projected Decimal field/tuple positions. Exactly two
owning logical fields use `CANONICAL_DECIMAL_UTF8`; all other independently projected
positions use `decimal128(22,18)`.

| Owning field or position | Reachable root paths | Projection |
| --- | --- | --- |
| `ActionPosition.x` | Silver action `action_positions[*].x`; nested through possession, fact and Gold | `decimal128(22,18)` |
| `ActionPosition.y` | same `.y` paths | `decimal128(22,18)` |
| `PossessionSequenceAction.period_elapsed_seconds` | Silver action `possession_period_sequence.actions[*]`; nested through possession, fact and Gold | `decimal128(22,18)` |
| `SilverAction.period_elapsed_seconds` | Silver action; possession `contributing_actions[*]`; fact; Gold | `decimal128(22,18)` |
| `SilverPossession.first_action_order[1]` | possession, fact, Gold | `decimal128(22,18)` |
| `SilverPossession.last_action_order[1]` | possession, fact, Gold | `decimal128(22,18)` |
| `GoldCoverageDimension.coverage` | player-match fact `coverage.dimensions[*].coverage`; Gold direct coverage and nested facts | `CANONICAL_DECIMAL_UTF8` |
| `GoldCoverage.coverage_overall` | player-match fact `coverage.coverage_overall`; Gold direct coverage and nested facts | `CANONICAL_DECIMAL_UTF8` |

The logical `CanonicalJsonNumber.value` is also a `Decimal`, but at the four CJV
field boundaries it is nested inside the complete `CANONICAL_JSON_VALUE_UTF8`
scalar. It has no independent Arrow field/child and therefore is not a ninth Decimal
projection position. Treating it as `decimal128` would contradict the corrected R2
tagged-scalar authority.

| Parquet root | Decimal-sensitive paths |
| --- | --- |
| Bronze known | number variants remain inside `raw_record` tagged UTF-8 |
| Bronze rejected record | number variants remain inside `raw_record` / `raw_kind.value` tagged UTF-8 |
| Bronze rejected field | number variant remains inside `original_value` tagged UTF-8 |
| Silver competition/team/player/match/lineup | none |
| Silver action | direct seconds, positions x/y, sequence seconds: all decimal128 |
| Silver possession | both order-tuple positions plus all nested action paths: decimal128 |
| Silver player-match fact | two coverage owning fields canonical UTF-8; all nested action/possession positions decimal128 |
| Gold player window | direct and nested coverage owning fields canonical UTF-8; all action/possession positions decimal128 |

### 6.2 Canonical Decimal token matrix

Forward accepts exact finite `Decimal`, performs no rounding, normalizes signed zero,
uses fixed-point/no exponent, strips redundant trailing fractional zeros and an empty
point, and emits UTF-8 without LF.

| Logical input | Exact forward token |
| --- | --- |
| `Decimal("0")`, `Decimal("-0")`, `Decimal("-0.000")` | `0` |
| `Decimal("1")` | `1` |
| `Decimal("-1")` | `-1` |
| `Decimal("1.2300")` | `1.23` |
| `Decimal("1E+3")` | `1000` |
| valid precision-38 `1/3` | `0.33333333333333333333333333333333333333` |
| `Decimal("1E-100")` | `0.` then 99 zeroes then `1` |
| `Decimal("1E+100")` | `1` then 100 zeroes |

Inverse must strict UTF-8 decode, parse directly to finite Decimal, canonicalize by
the same writer and require byte equality. Exact accepted tokens include the forward
outputs above. Each of the following independently fails before semantic use/write:

| Rejected input family | Required examples/reason |
| --- | --- |
| Arrow null | encoded value is present/non-null; outer optionality alone can authorize null |
| invalid UTF-8 / BOM / LF | invalid bytes, `\ufeff1`, `1\n` |
| whitespace | ` 1`, `1 `, `\t1` |
| aliases/sign | `+1`, `-0`, `-0.0` |
| leading/redundant zeros | `01`, `00`, `1.0`, `1.2300`, `0.10` |
| exponent or incomplete decimal aliases | `1e3`, `1E+3`, `.1`, `1.` |
| non-finite/JSON constants | `NaN`, `sNaN`, `Infinity`, `-Infinity` |
| non-string physical scalar | integer, float, Decimal object, binary scalar |

Every malformed family must be proven to result in zero Parquet writes. Mutation of
either authorized owning field to decimal128, or any other projected Decimal to
canonical UTF-8, is an exact descriptor failure.

## 7. Minimum all-twelve-root valid row/variant matrix

The lower-bound matrix below is `29` distinct valid logical rows across twelve root
tables. Nested rows may be reused as evidence, but every listed root must itself be
descriptor-led encoded, inverse-projected, and byte-equal to canonical contract
rows. Empty/nonempty variants must generate the identical descriptor schema.

| Root | Minimum distinct valid rows | Required variants exercised |
| --- | ---: | --- |
| Bronze known | 2 | One object containing all seven nested CJV arms (including mixed nested array/object and present null); one materially different empty/nested shape. Whole `raw_record` remains one scalar. |
| Bronze rejected record | 5 | Exact raw-kind states missing, null, non-string, safe unknown string, unsafe string; include different raw-object shapes. |
| Bronze rejected field | 7 | Direct `original_value` arm null/boolean/integer/number/string/array/object, with exact subevent quarantine reason; integer is unknown, not a C5-admitted pair. |
| Silver competition | 1 | Exact single competition source/UUID. |
| Silver team | 1 | Exact single team source/UUID. |
| Silver player | 1 | Exact single player source/UUID. |
| Silver match | 1 | Match source/country, ordered distinct teams, generic valid season fields; verify C9 remains external. |
| Silver action | 3 | Required-null identity/taxonomy fields with empty positions and unmapped eligibility; admitted one-position row; admitted two-position row. Exercise zero/maximum scale and decimal128 capacity. |
| Silver lineup stint | 2 | Authorized-style open/right-censored row with null end/bounds; generic valid closed row with non-null end and derived bounds. |
| Silver possession | 2 | One resolved control/restart group; one valid earlier resolved group surviving an equal-clock ambiguous group, exercising both heterogeneous order structs. |
| Silver player-match fact | 2 | Action-derived fact with valid `1/3` coverage and all nested decimal128 paths; lineup-only/right-censored or authority-proven zero-denominator variant. Required empty and nonempty sequences both exercised. |
| Gold player window | 2 | Gold aggregate containing precision-38 `1/3` direct/nested coverage; second row propagating right-censoring/zero-denominator authority. Four features and fact keys recompute exactly. |

Additional acceptance mutations are mandatory: each of the nine invalid R2 operand
records, coordinate `0..1`, boundary `VERIFIED`, descriptor number fixed to 3,
four/five authority roster conflation, runtime season/lineup overclaim, missing corpus
member, symbolic placeholder replacement, source truncation/reorder/omission,
integer width/signedness, Decimal kind/precision/scale, tuple name/order/position,
list child name/type/nullability, any recursive metadata, row/fixture inference,
caller schema/digest/callback and JSON-only projection omission must fail closed.

## 8. Oracle verdict and boundary

Verdict: **EXPECTED VALUES COMPLETE — NO CANDIDATE VERDICT**.

The frozen inputs compose without an architecture or product contradiction. This
report neither asserts that the R3 candidate implements these values nor authorizes
schema, aggregate, product, manifest, receipt or deployment bytes. A fresh reviewer
must compare the separately returned candidate against this oracle, and the master
must independently reproduce both before acceptance.

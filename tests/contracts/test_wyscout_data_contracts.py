"""Closed in-memory evidence for the W04 Wyscout data-contract surface."""

from __future__ import annotations

import hashlib
import pickle
from copy import copy, deepcopy
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, TypedDict, cast
from uuid import UUID, uuid5

import pytest
from pydantic import ValidationError

from scouting.contracts import wyscout_data as wyscout_contract
from scouting.contracts.evidence import (
    DependencyKind,
    DependencyLineage,
    EvidenceDependency,
    LicenceUseClass,
    SourceUseClassification,
)
from scouting.contracts.primitives import TenantContext
from scouting.contracts.wyscout_data import (
    FEATURE_DEPENDENCY_ID,
    FEATURE_SCHEMA_HASH,
    FIELD_DEPENDENCY_ID,
    POSSESSION_DEPENDENCY_ID,
    ROLE_CONTEXT_ID,
    ROLE_CONTEXT_STATE,
    ROLE_CONTEXT_VERSION,
    SOURCE_COMPLETION_INDEX_SHA256,
    SOURCE_MANIFEST_ID,
    SOURCE_MANIFEST_SHA256,
    ActionPosition,
    ActionSubeventOutcome,
    ActionSubeventReason,
    AuthorityKind,
    BronzeKnownRecord,
    BronzeRejectedField,
    BronzeRejectedRecord,
    CanonicalJsonArray,
    CanonicalJsonBoolean,
    CanonicalJsonInteger,
    CanonicalJsonKind,
    CanonicalJsonNull,
    CanonicalJsonNumber,
    CanonicalJsonObject,
    CanonicalJsonString,
    CountryPartition,
    GoldCoverage,
    GoldCoverageDimension,
    GoldCoverageDimensionName,
    GoldCoverageState,
    GoldFeatureValues,
    GoldPlayerWindow,
    Layer,
    LayerManifest,
    LayerManifestEntry,
    ManifestPartitionValue,
    NominalMinuteInterval,
    ParentLayerManifest,
    PossessionEligibilityState,
    PossessionPeriodSequence,
    PossessionPredicateState,
    PossessionSequenceAction,
    ProductPathRole,
    RawFieldMeasurement,
    RawKindEvidence,
    RawKindState,
    RejectedFieldDecision,
    SilverAction,
    SilverCompetition,
    SilverLineupStint,
    SilverMatch,
    SilverPlayer,
    SilverPlayerMatchFact,
    SilverPossession,
    SilverTeam,
    SourceRecordKind,
    W04Applicability,
    W04ApplicabilityAssessment,
    W04SemanticTemporalProof,
    WyscoutAuthorityClock,
    WyscoutAuthorityReference,
    WyscoutProductPath,
    WyscoutRawSourceRowReference,
    WyscoutRowLineage,
    WyscoutSourceRecordEnvelope,
    WyscoutSourceRowReference,
    accepted_authority_clocks,
    accepted_authority_references,
    accepted_source_authority,
    accepted_source_classification,
    canonical_contract_json_bytes,
    canonical_raw_json_bytes,
    canonical_source_uuid,
    canonicalize_json_value,
    classify_action_subevent,
    classify_raw_record_kind,
    dependency_lineage_hash,
    dependency_sort_key,
    identity_dependency_id,
)
from scouting.sources import wyscout_completion_index as completion_index

BUILD_ID = "a" * 64
IDENTITY_DIGEST = "1" * 64
SEMANTIC_DIGEST = "2" * 64
PHYSICAL_DIGEST = "3" * 64
RUN_ID = UUID("12345678-1234-4234-9234-123456789abc")
WINDOW_ID = UUID("7fa795be-b7bd-53e5-bd8f-67f6253dc6ed")
SEASON_ID = UUID("81892a9c-1194-56b5-9b16-79a607bd108c")
IDENTITY_BUNDLE_ID = identity_dependency_id(IDENTITY_DIGEST)

SOURCE_RELEASE = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
FIELD_DECIDED = datetime(2026, 7, 30, 20, 22, 17, tzinfo=UTC)
FIELD_ACCEPTED = datetime(2026, 7, 30, 21, 21, 23, tzinfo=UTC)
POSSESSION_DECIDED = datetime(2026, 7, 30, 22, 14, 21, tzinfo=UTC)
POSSESSION_ACCEPTED = datetime(2026, 7, 31, 8, 28, 40, tzinfo=UTC)
FEATURE_DECIDED = datetime(2026, 7, 31, 8, 37, tzinfo=UTC)
FEATURE_ACCEPTED = datetime(2026, 7, 31, 10, 15, 16, tzinfo=UTC)
IDENTITY_DECIDED = datetime(2026, 7, 31, 12, 44, 27, tzinfo=UTC)
IDENTITY_ACCEPTED = datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC)
CUTOFF = datetime(2026, 8, 1, tzinfo=UTC)
WINDOW_START = datetime(2018, 1, 1, tzinfo=UTC)
WINDOW_END = datetime(2019, 1, 1, tzinfo=UTC)

SOURCE_ROWS = (
    (
        "archive-members/events_England.json",
        SourceRecordKind.ACTION,
        "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad",
        {"eventId": 7, "id": 5, "subEventId": 70},
    ),
    (
        "archive-members/matches_England.json",
        SourceRecordKind.MATCH,
        "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29",
        {"wyId": 4},
    ),
    (
        "objects/competitions.json",
        SourceRecordKind.COMPETITION,
        "39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1",
        {"kind": "player", "wyId": 1},
    ),
    (
        "objects/eventid2name.csv",
        SourceRecordKind.EVENT_TAXONOMY,
        "ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842",
        {"event": 7, "subevent": 70},
    ),
    (
        "objects/players.json",
        SourceRecordKind.PLAYER,
        "877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e",
        {"wyId": 3},
    ),
    (
        "objects/tags2name.csv",
        SourceRecordKind.TAG_TAXONOMY,
        "e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922",
        {"Tag": 101},
    ),
    (
        "objects/teams.json",
        SourceRecordKind.TEAM,
        "9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d",
        {"wyId": 2},
    ),
)


def restricted_rights() -> SourceUseClassification:
    return accepted_source_classification()


def tenant() -> TenantContext:
    return TenantContext(tenant_id=UUID("65a43912-d412-5ff9-a364-7f84d1ad6c5d"))


class CommonRowInput(TypedDict):
    build_id: str
    tenant_context: TenantContext
    source_completion_index_sha256: str
    lineage: WyscoutRowLineage


def make_dependencies() -> tuple[EvidenceDependency, ...]:
    rows = (
        EvidenceDependency(
            kind=DependencyKind.SOURCE_MANIFEST,
            dependency_id=SOURCE_MANIFEST_ID,
            digest=SOURCE_MANIFEST_SHA256,
            observed_at=SOURCE_RELEASE,
            available_at=SOURCE_RELEASE,
        ),
        EvidenceDependency(
            kind=DependencyKind.IDENTITY_EVIDENCE,
            dependency_id=IDENTITY_BUNDLE_ID,
            digest=IDENTITY_DIGEST,
            observed_at=IDENTITY_DECIDED,
            available_at=IDENTITY_ACCEPTED,
        ),
        EvidenceDependency(
            kind=DependencyKind.FEATURE_SCHEMA,
            dependency_id=FIELD_DEPENDENCY_ID,
            digest=("93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959"),
            observed_at=FIELD_DECIDED,
            available_at=FIELD_ACCEPTED,
        ),
        EvidenceDependency(
            kind=DependencyKind.FEATURE_SCHEMA,
            dependency_id=POSSESSION_DEPENDENCY_ID,
            digest=("3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881"),
            observed_at=POSSESSION_DECIDED,
            available_at=POSSESSION_ACCEPTED,
        ),
        EvidenceDependency(
            kind=DependencyKind.FEATURE_SCHEMA,
            dependency_id=FEATURE_DEPENDENCY_ID,
            digest=FEATURE_SCHEMA_HASH,
            observed_at=FEATURE_DECIDED,
            available_at=FEATURE_ACCEPTED,
        ),
    )
    return tuple(sorted(rows, key=dependency_sort_key))


def make_dependency_lineage() -> DependencyLineage:
    dependencies = make_dependencies()
    return DependencyLineage(
        lineage_hash=dependency_lineage_hash(dependencies),
        dependencies=dependencies,
    )


def make_envelopes() -> tuple[WyscoutSourceRecordEnvelope, ...]:
    envelopes: list[WyscoutSourceRecordEnvelope] = []
    for path, kind, digest, raw in SOURCE_ROWS:
        raw_record = canonicalize_json_value(raw)
        if not isinstance(raw_record, CanonicalJsonObject):
            raise AssertionError("fixture source rows must be JSON objects")
        envelopes.append(
            WyscoutSourceRecordEnvelope(
                source_manifest_id=SOURCE_MANIFEST_ID,
                completion_relative_path=path,
                source_sha256=digest,
                source_record_ordinal=0,
                record_kind=kind,
                raw_record=raw_record,
            )
        )
    return tuple(envelopes)


def make_lineage() -> WyscoutRowLineage:
    return WyscoutRowLineage(
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        source_rows=tuple(envelope.source_row_reference for envelope in make_envelopes()),
        authority_references=accepted_authority_references(),
        authority_clocks=accepted_authority_clocks(),
        source_authority=accepted_source_authority(),
        dependency_lineage=make_dependency_lineage(),
    )


def make_temporal_proof() -> W04SemanticTemporalProof:
    lineage = make_dependency_lineage()
    return W04SemanticTemporalProof(
        snapshot_as_of_ts=SOURCE_RELEASE,
        available_at_watermark=IDENTITY_ACCEPTED,
        valid_from_ts=IDENTITY_ACCEPTED,
        feature_cutoff_ts=CUTOFF,
        source_manifest_ids=(SOURCE_MANIFEST_ID,),
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        dependency_lineage_hash=lineage.lineage_hash,
        dependency_lineage=lineage,
        source_authority=accepted_source_authority(),
        authority_clocks=accepted_authority_clocks(),
    )


def measurements(raw_record: CanonicalJsonObject) -> tuple[RawFieldMeasurement, ...]:
    return tuple(
        RawFieldMeasurement(
            json_path=f"$.{member.key}",
            measured_json_type=member.value.kind,
        )
        for member in raw_record.value
    )


def complete_coverage() -> GoldCoverage:
    return GoldCoverage(
        dimensions=tuple(
            GoldCoverageDimension(
                name=name,
                numerator=7 if name is GoldCoverageDimensionName.TEMPORAL else 1,
                denominator=7 if name is GoldCoverageDimensionName.TEMPORAL else 1,
                coverage=Decimal(1),
                state=GoldCoverageState.COMPLETE,
            )
            for name in GoldCoverageDimensionName
        ),
        coverage_overall=Decimal(1),
        missing_dimensions=(),
    )


def evidence_coverage(
    *,
    identity_count: int,
    action_count: int,
    coordinate_numerator: int,
    coordinate_denominator: int,
    possession_numerator: int,
    possession_denominator: int,
    temporal_count: int,
) -> GoldCoverage:
    counts = {
        GoldCoverageDimensionName.IDENTITY: (identity_count, identity_count),
        GoldCoverageDimensionName.LINEUP: (1, 1),
        GoldCoverageDimensionName.ACTION: (action_count, action_count),
        GoldCoverageDimensionName.COORDINATE: (
            coordinate_numerator,
            coordinate_denominator,
        ),
        GoldCoverageDimensionName.POSSESSION: (
            possession_numerator,
            possession_denominator,
        ),
        GoldCoverageDimensionName.TEMPORAL: (temporal_count, temporal_count),
    }
    reasons = {
        GoldCoverageDimensionName.COORDINATE: "COORDINATE_EVIDENCE_INCOMPLETE",
        GoldCoverageDimensionName.POSSESSION: "POSSESSION_EVIDENCE_INCOMPLETE",
    }
    dimensions: list[GoldCoverageDimension] = []
    for name in GoldCoverageDimensionName:
        numerator, denominator = counts[name]
        if denominator:
            state = (
                GoldCoverageState.COMPLETE
                if numerator == denominator
                else GoldCoverageState.PARTIAL
            )
            dimensions.append(
                GoldCoverageDimension(
                    name=name,
                    numerator=numerator,
                    denominator=denominator,
                    coverage=Decimal(numerator) / Decimal(denominator),
                    state=state,
                    reason_codes=(reasons[name],) if state is GoldCoverageState.PARTIAL else (),
                )
            )
        else:
            authority_kind = (
                AuthorityKind.FIELD
                if name is GoldCoverageDimensionName.COORDINATE
                else AuthorityKind.POSSESSION
            )
            reason = (
                "NO_APPLICABLE_COORDINATE_EVIDENCE"
                if name is GoldCoverageDimensionName.COORDINATE
                else "NO_POSSESSION_ELIGIBLE_ACTIONS"
            )
            dimensions.append(
                GoldCoverageDimension(
                    name=name,
                    numerator=0,
                    denominator=0,
                    coverage=Decimal(1),
                    state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
                    reason_codes=(reason,),
                    zero_denominator_authority=next(
                        row
                        for row in accepted_authority_references()
                        if row.authority_kind is authority_kind
                    ),
                )
            )
    frozen = tuple(dimensions)
    missing = tuple(
        sorted(
            (
                dimension.name
                for dimension in frozen
                if dimension.state is GoldCoverageState.PARTIAL
            ),
            key=lambda name: name.value,
        )
    )
    return GoldCoverage(
        dimensions=frozen,
        coverage_overall=min(dimension.coverage for dimension in frozen),
        missing_dimensions=missing,
    )


def data_ready() -> W04ApplicabilityAssessment:
    return W04ApplicabilityAssessment(state=W04Applicability.W04_DATA_READY, reason_codes=())


def make_silver_rows() -> tuple[
    SilverCompetition,
    SilverTeam,
    SilverPlayer,
    SilverMatch,
    SilverAction,
    SilverLineupStint,
    SilverPossession,
    SilverPlayerMatchFact,
]:
    lineage = make_lineage()
    common: CommonRowInput = {
        "build_id": BUILD_ID,
        "tenant_context": tenant(),
        "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
        "lineage": lineage,
    }
    competition_id = canonical_source_uuid(SourceRecordKind.COMPETITION, 1)
    team_id = canonical_source_uuid(SourceRecordKind.TEAM, 2)
    opponent_id = canonical_source_uuid(SourceRecordKind.TEAM, 22)
    player_id = canonical_source_uuid(SourceRecordKind.PLAYER, 3)
    match_id = canonical_source_uuid(SourceRecordKind.MATCH, 4)
    action_id = canonical_source_uuid(SourceRecordKind.ACTION, 5)
    source_by_kind = {row.record_kind: row for row in lineage.source_rows}
    competition = SilverCompetition(
        **common,
        source_rows=(source_by_kind[SourceRecordKind.COMPETITION],),
        competition_source_id=1,
        competition_id=competition_id,
    )
    team_row = SilverTeam(
        **common,
        source_rows=(source_by_kind[SourceRecordKind.TEAM],),
        team_source_id=2,
        team_id=team_id,
    )
    player = SilverPlayer(
        **common,
        source_rows=(source_by_kind[SourceRecordKind.PLAYER],),
        player_source_id=3,
        player_id=player_id,
    )
    team_ids = (
        (team_id, opponent_id) if team_id.bytes < opponent_id.bytes else (opponent_id, team_id)
    )
    match = SilverMatch(
        **common,
        source_rows=(source_by_kind[SourceRecordKind.MATCH],),
        match_source_id=4,
        match_id=match_id,
        competition_id=competition_id,
        season_id=SEASON_ID,
        season_source_id=2018,
        match_start_utc=datetime(2018, 6, 1, 12, tzinfo=UTC),
        team_ids=team_ids,
        source_partition=CountryPartition.ENGLAND,
    )
    action_sequence = PossessionPeriodSequence(
        match_id=match_id,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        source_completion_membership_sha256="9" * 64,
        action_period_code="1H",
        period_action_count=1,
        actions=(
            PossessionSequenceAction(
                action_id=action_id,
                source_event_record_id=5,
                source_row=source_by_kind[SourceRecordKind.ACTION],
                match_id=match_id,
                player_id=player_id,
                team_id=team_id,
                action_event_taxonomy_id=7,
                action_subevent_taxonomy_id=70,
                action_period_code="1H",
                period_rank=1,
                period_elapsed_seconds=Decimal("10.250"),
                source_record_ordinal=0,
                action_tag_ids=(),
            ),
        ),
    )
    action = SilverAction(
        **common,
        source_rows=(source_by_kind[SourceRecordKind.ACTION],),
        action_source_id=5,
        action_id=action_id,
        source_event_record_id=5,
        match_id=match_id,
        competition_id=competition_id,
        player_id=player_id,
        team_id=team_id,
        action_event_taxonomy_id=7,
        action_subevent_taxonomy_id=70,
        action_period_code="1H",
        period_rank=1,
        period_elapsed_seconds=Decimal("10.250"),
        event_sec_source_scale=3,
        source_record_ordinal=0,
        action_tag_ids=(),
        action_positions=(
            ActionPosition(x=Decimal(50), y=Decimal(60), within_accepted_bounds=True),
        ),
        possession_predicate_state=PossessionPredicateState.PREDICATE_ADMITTED,
        possession_period_sequence=action_sequence,
        possession_eligibility_state=PossessionEligibilityState.ELIGIBLE_RESOLVED,
    )
    lineup = SilverLineupStint(
        **common,
        source_rows=(source_by_kind[SourceRecordKind.MATCH],),
        lineup_stint_id=uuid5(match_id, f"lineup:{player_id}:{team_id}"),
        match_id=match_id,
        player_id=player_id,
        team_id=team_id,
        start_interval=NominalMinuteInterval(lower=0, upper=1),
        end_interval=NominalMinuteInterval(lower=90, upper=91),
        lower_bound_minutes=89,
        upper_bound_minutes=91,
        right_censored=False,
    )
    possession = SilverPossession(
        **common,
        source_rows=action.source_rows,
        possession_id=uuid5(match_id, "1H:possession:1"),
        match_id=match_id,
        action_period_code="1H",
        team_id=team_id,
        contributing_actions=(action,),
        action_ids=(action_id,),
        first_action_order=action.action_order_key,
        last_action_order=action.action_order_key,
    )
    fact = SilverPlayerMatchFact(
        **common,
        source_rows=action.source_rows,
        source_manifest_id=SOURCE_MANIFEST_ID,
        match_id=match_id,
        player_id=player_id,
        competition_id=competition_id,
        season_id=SEASON_ID,
        match_start_utc=datetime(2018, 6, 1, 12, tzinfo=UTC),
        match_team_id=team_id,
        lineup_evidence_present=False,
        contributing_lineup_stints=(),
        contributing_actions=(action,),
        contributing_possessions=(possession,),
        action_count=1,
        coordinate_known_action_count=1,
        resolved_possession_action_count=1,
        right_censored_or_uncertain=False,
        coverage=complete_coverage(),
        applicability=data_ready(),
        temporal_proof=make_temporal_proof(),
    )
    return competition, team_row, player, match, action, lineup, possession, fact


def make_gold() -> GoldPlayerWindow:
    *_, fact = make_silver_rows()
    return GoldPlayerWindow(
        build_id=BUILD_ID,
        tenant_context=tenant(),
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        source_rows=fact.source_rows,
        lineage=make_lineage(),
        player_id=fact.player_id,
        competition_id=fact.competition_id,
        season_id=fact.season_id,
        role_context_id=ROLE_CONTEXT_ID,
        role_context_version="w04-neutral-role-context-v1",
        role_context_state="neutral_unscoped",
        window_definition_id=WINDOW_ID,
        window_start_utc=WINDOW_START,
        window_end_utc=WINDOW_END,
        feature_cutoff_ts=CUTOFF,
        dependency_lineage_hash=fact.temporal_proof.dependency_lineage_hash,
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        temporal_proof=fact.temporal_proof,
        coverage=complete_coverage(),
        applicability=data_ready(),
        features=GoldFeatureValues(
            action_count=1,
            coordinate_known_action_count=1,
            match_count=1,
            resolved_possession_action_count=1,
        ),
        contributing_player_match_facts=(fact,),
        contributing_player_match_keys=(fact.primary_key,),
    )


def _closure_value(function: object, name: str) -> object:
    inspected = cast(Any, function)
    values = dict(
        zip(
            inspected.__code__.co_freevars,
            (cell.cell_contents for cell in inspected.__closure__),
            strict=True,
        )
    )
    return cast(object, values[name])


@pytest.fixture(scope="module")
def real_checked_match_population() -> tuple[
    completion_index.SourceCompletionIndex,
    tuple[completion_index.CompletionActionEvidence, ...],
]:
    index = completion_index.load_source_completion_index(
        manifest_root=Path("data/manifests"),
        index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
    )
    match_source_id = index.members[0].periods[0].match_source_id
    spec = completion_index._EVENT_MEMBERS[0]
    records = completion_index._decode_action_member(
        Path("data/source/wyscout/v5", spec.path).read_bytes(),
        context=spec.path,
    )
    actions = tuple(
        sorted(
            (
                completion_index.completion_action_evidence(
                    source_member_path=spec.path,
                    source_member_sha256=spec.sha256,
                    source_record_ordinal=ordinal,
                    raw_record=record,
                )
                for ordinal, record in enumerate(records)
                if record["matchId"] == match_source_id
            ),
            key=lambda action: action.order_key,
        )
    )
    return index, actions


def _real_checked_action_payload(
    *,
    evidence: completion_index.CompletionActionEvidence,
    entry: PossessionSequenceAction,
    lineage: WyscoutRowLineage,
    resolved_action_ids: set[UUID],
) -> dict[str, object]:
    scale = max(0, -cast(int, entry.period_elapsed_seconds.as_tuple().exponent))
    return {
        "build_id": BUILD_ID,
        "tenant_context": tenant(),
        "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
        "source_rows": (entry.source_row,),
        "lineage": lineage,
        "action_source_id": evidence.source_event_record_id,
        "action_id": entry.action_id,
        "source_event_record_id": evidence.source_event_record_id,
        "match_id": entry.match_id,
        "competition_id": canonical_source_uuid(SourceRecordKind.COMPETITION, 1),
        "player_id": entry.player_id,
        "team_id": entry.team_id,
        "action_event_taxonomy_id": entry.action_event_taxonomy_id,
        "action_subevent_taxonomy_id": entry.action_subevent_taxonomy_id,
        "action_period_code": entry.action_period_code,
        "period_rank": entry.period_rank,
        "period_elapsed_seconds": entry.period_elapsed_seconds,
        "event_sec_source_scale": scale,
        "source_record_ordinal": entry.source_record_ordinal,
        "action_tag_ids": entry.action_tag_ids,
        "action_positions": (),
        "possession_predicate_state": wyscout_contract._possession_predicate_state(
            entry.action_event_taxonomy_id,
            entry.action_subevent_taxonomy_id,
            entry.team_id,
            entry.action_tag_ids,
        ),
        "possession_eligibility_state": (
            PossessionEligibilityState.ELIGIBLE_RESOLVED
            if entry.action_id in resolved_action_ids
            else PossessionEligibilityState.INELIGIBLE_UNMAPPED
        ),
    }


def action_payload_with_sequence_updates(
    action: SilverAction,
    **updates: object,
) -> dict[str, Any]:
    payload = action.model_dump()
    payload.update(updates)
    sequence = dict(payload["possession_period_sequence"])
    entries = [dict(entry) for entry in sequence["actions"]]
    own_index = next(
        index for index, entry in enumerate(entries) if entry["action_id"] == payload["action_id"]
    )
    mirrored = {
        "source_event_record_id",
        "match_id",
        "player_id",
        "team_id",
        "action_event_taxonomy_id",
        "action_subevent_taxonomy_id",
        "action_period_code",
        "period_rank",
        "period_elapsed_seconds",
        "source_record_ordinal",
        "action_tag_ids",
    }
    for key in mirrored & updates.keys():
        entries[own_index][key] = updates[key]
    if "source_rows" in updates:
        entries[own_index]["source_row"] = payload["source_rows"][0]
    if "match_id" in updates:
        sequence["match_id"] = updates["match_id"]
    if "action_period_code" in updates:
        sequence["action_period_code"] = updates["action_period_code"]
    sequence["actions"] = tuple(entries)
    payload["possession_period_sequence"] = sequence
    return payload


def make_following_control_evidence() -> tuple[
    PossessionPeriodSequence,
    tuple[SilverAction, SilverAction],
    SilverPossession,
    SilverPlayerMatchFact,
]:
    *_, base_action, _, base_possession, base_fact = make_silver_rows()
    second_source_row = WyscoutSourceRowReference(
        source_manifest_id=SOURCE_MANIFEST_ID,
        completion_relative_path=SOURCE_ROWS[0][0],
        source_sha256=SOURCE_ROWS[0][2],
        source_record_ordinal=1,
        record_kind=SourceRecordKind.ACTION,
        raw_record_sha256="8" * 64,
    )
    lineage_payload = make_lineage().model_dump()
    lineage_payload["source_rows"] = tuple(
        sorted(
            (*make_lineage().source_rows, second_source_row),
            key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
        )
    )
    lineage = WyscoutRowLineage.model_validate(lineage_payload)
    second_action_id = canonical_source_uuid(SourceRecordKind.ACTION, 6)
    sequence = PossessionPeriodSequence(
        match_id=base_action.match_id,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        source_completion_membership_sha256="9" * 64,
        action_period_code=base_action.action_period_code,
        period_action_count=2,
        actions=(
            PossessionSequenceAction(
                action_id=base_action.action_id,
                source_event_record_id=base_action.source_event_record_id,
                source_row=base_action.source_rows[0],
                match_id=base_action.match_id,
                player_id=base_action.player_id,
                team_id=base_action.team_id,
                action_event_taxonomy_id=1,
                action_subevent_taxonomy_id=10,
                action_period_code=base_action.action_period_code,
                period_rank=base_action.period_rank,
                period_elapsed_seconds=base_action.period_elapsed_seconds,
                source_record_ordinal=base_action.source_record_ordinal,
                action_tag_ids=(),
            ),
            PossessionSequenceAction(
                action_id=second_action_id,
                source_event_record_id=6,
                source_row=second_source_row,
                match_id=base_action.match_id,
                player_id=base_action.player_id,
                team_id=base_action.team_id,
                action_event_taxonomy_id=7,
                action_subevent_taxonomy_id=70,
                action_period_code=base_action.action_period_code,
                period_rank=base_action.period_rank,
                period_elapsed_seconds=Decimal("11.000"),
                source_record_ordinal=1,
                action_tag_ids=(),
            ),
        ),
    )
    first_payload = base_action.model_dump()
    first_payload.update(
        lineage=lineage,
        action_event_taxonomy_id=1,
        action_subevent_taxonomy_id=10,
        possession_period_sequence=sequence,
        possession_predicate_state=PossessionPredicateState.PREDICATE_ADMITTED,
        possession_eligibility_state=PossessionEligibilityState.ELIGIBLE_RESOLVED,
    )
    first = SilverAction.model_validate(first_payload)
    second_payload = base_action.model_dump()
    second_payload.update(
        lineage=lineage,
        source_rows=(second_source_row,),
        action_source_id=6,
        action_id=second_action_id,
        source_event_record_id=6,
        action_event_taxonomy_id=7,
        action_subevent_taxonomy_id=70,
        period_elapsed_seconds=Decimal("11.000"),
        source_record_ordinal=1,
        possession_period_sequence=sequence,
        possession_predicate_state=PossessionPredicateState.PREDICATE_ADMITTED,
        possession_eligibility_state=PossessionEligibilityState.ELIGIBLE_RESOLVED,
    )
    second = SilverAction.model_validate(second_payload)
    possession_payload = base_possession.model_dump()
    possession_payload.update(
        lineage=lineage,
        source_rows=(base_action.source_rows[0], second_source_row),
        contributing_actions=(first, second),
        action_ids=(first.action_id, second.action_id),
        first_action_order=first.action_order_key,
        last_action_order=second.action_order_key,
    )
    possession = SilverPossession.model_validate(possession_payload)
    fact_payload = base_fact.model_dump()
    fact_payload.update(
        lineage=lineage,
        source_rows=(base_action.source_rows[0], second_source_row),
        contributing_actions=(first, second),
        contributing_possessions=(possession,),
        action_count=2,
        coordinate_known_action_count=2,
        resolved_possession_action_count=2,
        coverage=evidence_coverage(
            identity_count=2,
            action_count=2,
            coordinate_numerator=2,
            coordinate_denominator=2,
            possession_numerator=2,
            possession_denominator=2,
            temporal_count=8,
        ),
    )
    fact = SilverPlayerMatchFact.model_validate(fact_payload)
    return sequence, (first, second), possession, fact


def valid_paths() -> tuple[WyscoutProductPath, ...]:
    competition_id = canonical_source_uuid(SourceRecordKind.COMPETITION, 1)
    utc_start = "20180101T000000000000Z"
    utc_end = "20190101T000000000000Z"
    utc_cutoff = "20260801T000000000000Z"
    values = {
        ProductPathRole.BRONZE_KNOWN_RECORD: (
            f"data/working/wyscout/v5/bronze/build_id={BUILD_ID}/records/"
            f"record_kind=action/source_sha256={'4' * 64}/part-00000.parquet"
        ),
        ProductPathRole.BRONZE_REJECTED_RECORD: (
            f"data/working/wyscout/v5/bronze/build_id={BUILD_ID}/quarantine/"
            "rejected-record/record_kind=unknown/raw_kind_state=string-unsafe/"
            f"raw_kind_sha256={'5' * 64}/source_sha256={'4' * 64}/part-00000.parquet"
        ),
        ProductPathRole.BRONZE_REJECTED_FIELD: (
            f"data/working/wyscout/v5/bronze/build_id={BUILD_ID}/quarantine/"
            f"rejected-field/record_kind=action/source_sha256={'4' * 64}/"
            "part-00000.parquet"
        ),
        ProductPathRole.SILVER_COMPETITION: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/competition/"
            "source_partition=global/part-00000.parquet"
        ),
        ProductPathRole.SILVER_TEAM: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/team/"
            "source_partition=global/part-00000.parquet"
        ),
        ProductPathRole.SILVER_PLAYER: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/player/"
            "source_partition=global/part-00000.parquet"
        ),
        ProductPathRole.SILVER_MATCH: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/match/"
            "source_partition=england/part-00000.parquet"
        ),
        ProductPathRole.SILVER_ACTION: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/action/"
            "source_partition=england/part-00000.parquet"
        ),
        ProductPathRole.SILVER_LINEUP_STINT: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/lineup-stint/"
            "source_partition=england/part-00000.parquet"
        ),
        ProductPathRole.SILVER_POSSESSION: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/possession/"
            "source_partition=england/part-00000.parquet"
        ),
        ProductPathRole.SILVER_PLAYER_MATCH_FACT: (
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/player-match-fact/"
            "source_partition=england/part-00000.parquet"
        ),
        ProductPathRole.GOLD_PLAYER_WINDOW: (
            f"data/working/wyscout/v5/gold/build_id={BUILD_ID}/player-window/"
            f"competition_id={competition_id}/window_definition_id={WINDOW_ID}/"
            f"window_start_utc={utc_start}/window_end_utc={utc_end}/"
            f"feature_cutoff_ts={utc_cutoff}/part-00000.parquet"
        ),
        ProductPathRole.BRONZE_MANIFEST: (
            f"data/manifests/wyscout/v5/bronze/{BUILD_ID}.manifest.json"
        ),
        ProductPathRole.SILVER_MANIFEST: (
            f"data/manifests/wyscout/v5/silver/{BUILD_ID}.manifest.json"
        ),
        ProductPathRole.GOLD_MANIFEST: (f"data/manifests/wyscout/v5/gold/{BUILD_ID}.manifest.json"),
        ProductPathRole.REBUILD_INVOCATION_RECEIPT: (
            f"runs/w04/wyscout-rebuild/{BUILD_ID}/{RUN_ID}.receipt.json"
        ),
        ProductPathRole.TEMPORAL_BOUNDARY_RECEIPT: (
            f"runs/w04/wyscout-rebuild/{BUILD_ID}/{RUN_ID}/boundary/"
            f"{'6' * 64}.temporal-boundary-receipt.json"
        ),
    }
    return tuple(
        WyscoutProductPath(path_role=role, relative_path=values[role]) for role in ProductPathRole
    )


def manifest_entry(
    path: WyscoutProductPath,
    serializer: str,
    ordered_parent_paths: tuple[str, ...] = (),
) -> LayerManifestEntry:
    partitions = tuple(
        sorted(
            (
                ManifestPartitionValue(key=segment.split("=", 1)[0], value=segment.split("=", 1)[1])
                for segment in path.relative_path.split("/")
                if "=" in segment
            ),
            key=lambda value: value.key,
        )
    )
    return LayerManifestEntry(
        path=path,
        serializer=serializer,
        serializer_version="w04-contract-fixture-v1",
        schema_role=path.path_role.value,
        row_count=1,
        semantic_sha256=SEMANTIC_DIGEST,
        physical_sha256=PHYSICAL_DIGEST,
        size_bytes=1,
        ordered_parent_paths=ordered_parent_paths,
        partition_values=partitions,
        classification=restricted_rights(),
    )


def make_rejected_field(
    original_value: Any,
    *,
    action_event_taxonomy_id: int = 7,
) -> BronzeRejectedField:
    canonical = (
        original_value
        if isinstance(
            original_value,
            (
                CanonicalJsonArray,
                CanonicalJsonBoolean,
                CanonicalJsonInteger,
                CanonicalJsonNull,
                CanonicalJsonNumber,
                CanonicalJsonObject,
                CanonicalJsonString,
            ),
        )
        else canonicalize_json_value(original_value)
    )
    reason_by_kind = {
        CanonicalJsonKind.STRING: ActionSubeventReason.STRING.value,
        CanonicalJsonKind.BOOLEAN: ActionSubeventReason.BOOLEAN.value,
        CanonicalJsonKind.NULL: ActionSubeventReason.NULL.value,
        CanonicalJsonKind.NUMBER: ActionSubeventReason.NUMBER.value,
        CanonicalJsonKind.ARRAY: ActionSubeventReason.ARRAY.value,
        CanonicalJsonKind.OBJECT: ActionSubeventReason.OBJECT.value,
        CanonicalJsonKind.INTEGER: ActionSubeventReason.UNKNOWN_INTEGER.value,
    }
    envelope = make_envelopes()[0]
    return BronzeRejectedField(
        build_id=BUILD_ID,
        tenant_context=tenant(),
        source_row=envelope.source_row_reference,
        record_kind=SourceRecordKind.ACTION,
        json_path="$.subEventId",
        original_value=canonical,
        original_value_sha256=hashlib.sha256(canonical_raw_json_bytes(canonical)).hexdigest(),
        measured_json_type=canonical.kind,
        action_event_taxonomy_id=action_event_taxonomy_id,
        decision=RejectedFieldDecision.PRESERVE_UNMAPPED,
        reason_code=reason_by_kind[canonical.kind],
        field_authority=accepted_authority_references()[0],
        classification=restricted_rights(),
        lineage=make_lineage(),
    )


def make_alternate_dependency_lineage() -> DependencyLineage:
    dependencies = list(make_dependencies())
    identity_index = next(
        index
        for index, dependency in enumerate(dependencies)
        if dependency.kind is DependencyKind.IDENTITY_EVIDENCE
    )
    payload = dependencies[identity_index].model_dump()
    payload["digest"] = "9" * 64
    payload["dependency_id"] = identity_dependency_id(payload["digest"])
    dependencies[identity_index] = EvidenceDependency.model_validate(payload)
    ordered = tuple(sorted(dependencies, key=dependency_sort_key))
    return DependencyLineage(
        lineage_hash=dependency_lineage_hash(ordered),
        dependencies=ordered,
    )


def test_one_match_seven_family_fixture_closes_bronze_all_silver_and_gold() -> None:
    envelopes = make_envelopes()
    lineage = make_lineage()
    bronze = tuple(
        BronzeKnownRecord(
            build_id=BUILD_ID,
            tenant_context=tenant(),
            source_row=envelope.source_row_reference,
            raw_record=envelope.raw_record,
            raw_record_sha256=envelope.source_row_reference.raw_record_sha256,
            measured_raw_fields=measurements(envelope.raw_record),
            classification=restricted_rights(),
            lineage=lineage,
        )
        for envelope in envelopes
    )
    silver = make_silver_rows()
    gold = make_gold()

    assert tuple(row.source_row.record_kind for row in bronze) == (
        SourceRecordKind.ACTION,
        SourceRecordKind.MATCH,
        SourceRecordKind.COMPETITION,
        SourceRecordKind.EVENT_TAXONOMY,
        SourceRecordKind.PLAYER,
        SourceRecordKind.TAG_TAXONOMY,
        SourceRecordKind.TEAM,
    )
    assert len(silver) == 8
    assert silver[4].action_order_key == (1, Decimal("10.250"), 0, 5)
    assert silver[7].primary_key == gold.contributing_player_match_keys[0]
    assert gold.features.model_dump() == {
        "action_count": 1,
        "coordinate_known_action_count": 1,
        "match_count": 1,
        "resolved_possession_action_count": 1,
    }
    assert len(gold.primary_key) == 11
    assert FEATURE_SCHEMA_HASH not in gold.primary_key
    assert gold.applicability.state is W04Applicability.W04_DATA_READY


def test_country_members_and_bronze_raw_digest_validation_are_exact() -> None:
    assert tuple(CountryPartition) == (
        CountryPartition.ENGLAND,
        CountryPartition.FRANCE,
        CountryPartition.GERMANY,
        CountryPartition.ITALY,
        CountryPartition.SPAIN,
    )
    assert tuple(CountryPartition.__members__) == (
        "ENGLAND",
        "FRANCE",
        "GERMANY",
        "ITALY",
        "SPAIN",
    )

    envelope = make_envelopes()[0]
    with pytest.raises(ValidationError, match="Bronze raw record digest"):
        BronzeKnownRecord(
            build_id=BUILD_ID,
            tenant_context=tenant(),
            source_row=envelope.source_row_reference,
            raw_record=envelope.raw_record,
            raw_record_sha256="0" * 64,
            measured_raw_fields=measurements(envelope.raw_record),
            classification=restricted_rights(),
            lineage=make_lineage(),
        )


def test_canonical_raw_values_are_deeply_immutable_and_decimal_preserving() -> None:
    raw = canonicalize_json_value({"z": Decimal("1.2500"), "a": [True, None, {"x": "unchanged"}]})
    assert canonical_raw_json_bytes(raw) == b'{"a":[true,null,{"x":"unchanged"}],"z":1.25}'
    assert canonical_raw_json_bytes(raw) == canonical_raw_json_bytes(raw)
    with pytest.raises(ValidationError, match="frozen"):
        raw.value = ()
    with pytest.raises(TypeError, match="unsupported parsed JSON value"):
        canonicalize_json_value(1.25)


def test_envelope_kind_comes_only_from_exact_completion_path() -> None:
    competition = make_envelopes()[2]
    assert competition.record_kind is SourceRecordKind.COMPETITION
    assert isinstance(competition.raw_record, CanonicalJsonObject)
    assert b'"kind":"player"' in canonical_raw_json_bytes(competition.raw_record)
    payload = competition.model_dump()
    payload["record_kind"] = SourceRecordKind.PLAYER
    with pytest.raises(ValidationError, match="record_kind must come only"):
        WyscoutSourceRecordEnvelope.model_validate(payload)


@pytest.mark.parametrize(
    ("present", "value", "state"),
    (
        (False, None, RawKindState.MISSING),
        (True, None, RawKindState.NULL),
        (True, False, RawKindState.NON_STRING),
        (True, 17, RawKindState.NON_STRING),
        (True, [], RawKindState.NON_STRING),
        (True, {}, RawKindState.NON_STRING),
        (True, "Competition", RawKindState.STRING_UNKNOWN_SAFE),
        (True, "../action", RawKindState.STRING_UNSAFE),
        (True, "a/b", RawKindState.STRING_UNSAFE),
    ),
)
def test_unknown_discriminator_states_are_closed_and_root_safe(
    present: bool,
    value: object,
    state: RawKindState,
) -> None:
    evidence = classify_raw_record_kind(value_present=present, value=value)
    assert evidence.raw_kind_state is state
    assert len(evidence.raw_kind_sha256) == 64
    assert str(value) not in evidence.raw_kind_sha256


def test_missing_null_and_unsafe_discriminators_have_distinct_full_digests() -> None:
    rows = (
        classify_raw_record_kind(value_present=False),
        classify_raw_record_kind(value_present=True, value=None),
        classify_raw_record_kind(value_present=True, value="../action"),
        classify_raw_record_kind(value_present=True, value="a/b"),
    )
    assert len({row.raw_kind_sha256 for row in rows}) == 4
    with pytest.raises(ValueError, match="known record kinds"):
        classify_raw_record_kind(value_present=True, value="action")


def test_rejected_record_and_rejected_field_retain_exact_raw_evidence() -> None:
    envelope = make_envelopes()[0]
    raw_kind = classify_raw_record_kind(value_present=True, value="../action")
    rejected_record = BronzeRejectedRecord(
        build_id=BUILD_ID,
        tenant_context=tenant(),
        source_row=WyscoutRawSourceRowReference(
            source_manifest_id=envelope.source_manifest_id,
            completion_relative_path=envelope.completion_relative_path,
            source_sha256=envelope.source_sha256,
            source_record_ordinal=envelope.source_record_ordinal,
        ),
        raw_record=envelope.raw_record,
        raw_record_sha256=envelope.source_row_reference.raw_record_sha256,
        raw_kind=raw_kind,
        classification=restricted_rights(),
        lineage=make_lineage(),
    )
    rejected_value = canonicalize_json_value("10")
    rejected_field = BronzeRejectedField(
        build_id=BUILD_ID,
        tenant_context=tenant(),
        source_row=envelope.source_row_reference,
        record_kind=SourceRecordKind.ACTION,
        json_path="$.subEventId",
        original_value=rejected_value,
        original_value_sha256=(
            __import__("hashlib").sha256(canonical_raw_json_bytes(rejected_value)).hexdigest()
        ),
        measured_json_type=CanonicalJsonKind.STRING,
        action_event_taxonomy_id=7,
        decision=RejectedFieldDecision.PRESERVE_UNMAPPED,
        reason_code="ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED",
        field_authority=accepted_authority_references()[0],
        classification=restricted_rights(),
        lineage=make_lineage(),
    )
    assert rejected_record.rejection_code == "UNKNOWN_RECORD_KIND"
    assert rejected_field.original_value == rejected_value


@pytest.mark.parametrize(
    ("raw", "reason"),
    (
        (CanonicalJsonString(value="10"), ActionSubeventReason.STRING),
        (CanonicalJsonString(value=" 10"), ActionSubeventReason.STRING),
        (CanonicalJsonString(value="+10"), ActionSubeventReason.STRING),
        (CanonicalJsonString(value="010"), ActionSubeventReason.STRING),
        (CanonicalJsonBoolean(value=True), ActionSubeventReason.BOOLEAN),
        (CanonicalJsonBoolean(value=False), ActionSubeventReason.BOOLEAN),
        (CanonicalJsonNull(), ActionSubeventReason.NULL),
        (CanonicalJsonNumber(value=Decimal("10.0")), ActionSubeventReason.NUMBER),
        (CanonicalJsonArray(value=()), ActionSubeventReason.ARRAY),
        (CanonicalJsonObject(value=()), ActionSubeventReason.OBJECT),
        (CanonicalJsonInteger(value=999), ActionSubeventReason.UNKNOWN_INTEGER),
    ),
)
def test_action_subevent_no_coercion_matrix(
    raw: Any,
    reason: ActionSubeventReason,
) -> None:
    outcome = classify_action_subevent(7, raw)
    assert outcome.canonical_value is None
    assert outcome.rejected_raw_value is raw
    assert outcome.reason_code is reason


def test_action_subevent_emits_only_admitted_strict_integer_pair() -> None:
    outcome = classify_action_subevent(7, CanonicalJsonInteger(value=70))
    assert outcome.canonical_value == 70
    assert outcome.rejected_raw_value is None
    with pytest.raises(ValidationError):
        CanonicalJsonInteger(value=True)


def test_authority_rows_are_exact_seven_fields_and_fixed_order() -> None:
    rows = accepted_authority_references()
    assert tuple(row.authority_kind.value for row in rows) == (
        "FIELD",
        "POSSESSION",
        "SUPPORTED_FEATURE",
        "IDENTITY",
    )
    assert all(len(row.model_dump()) == 7 for row in rows)
    payload = rows[0].model_dump()
    payload["candidate_sha256"] = "0" * 64
    with pytest.raises(ValidationError, match="differs from the accepted"):
        WyscoutAuthorityReference.model_validate(payload)


def test_temporal_proof_has_exact_five_ordered_dependencies_and_valid_from() -> None:
    proof = make_temporal_proof()
    assert len(proof.dependency_lineage.dependencies) == 5
    assert proof.valid_from_ts == max(proof.snapshot_as_of_ts, IDENTITY_ACCEPTED)
    assert proof.available_at_watermark < proof.feature_cutoff_ts
    dumped = proof.model_dump()
    assert "generated_at_ts" not in dumped
    assert not any("run" in key or "host" in key or "output" in key for key in dumped)


@pytest.mark.parametrize("clock_field", ("observed_at", "available_at"))
def test_temporal_proof_rejects_clock_equal_to_cutoff(clock_field: str) -> None:
    proof = make_temporal_proof()
    dependencies = list(proof.dependency_lineage.dependencies)
    payload = dependencies[-1].model_dump()
    payload[clock_field] = CUTOFF
    dependencies[-1] = EvidenceDependency.model_validate(payload)
    dependencies_tuple = tuple(sorted(dependencies, key=dependency_sort_key))
    lineage = DependencyLineage(
        lineage_hash=dependency_lineage_hash(dependencies_tuple),
        dependencies=dependencies_tuple,
    )
    proof_payload = proof.model_dump()
    proof_payload["dependency_lineage"] = lineage
    proof_payload["dependency_lineage_hash"] = lineage.lineage_hash
    proof_payload["available_at_watermark"] = max(
        dependency.available_at for dependency in dependencies_tuple
    )
    with pytest.raises(ValidationError, match="authority|strictly before cutoff|watermark"):
        W04SemanticTemporalProof.model_validate(proof_payload)


def test_temporal_proof_rejects_wrong_cardinality_duplicate_and_lineage_drift() -> None:
    proof = make_temporal_proof()
    dependencies = proof.dependency_lineage.dependencies[:-1]
    payload = proof.model_dump()
    payload["dependency_lineage"] = DependencyLineage(
        lineage_hash=dependency_lineage_hash(dependencies),
        dependencies=dependencies,
    )
    payload["dependency_lineage_hash"] = dependency_lineage_hash(dependencies)
    with pytest.raises(ValidationError, match="exactly five"):
        W04SemanticTemporalProof.model_validate(payload)
    duplicates = proof.dependency_lineage.dependencies + (proof.dependency_lineage.dependencies[0],)
    with pytest.raises(ValidationError, match="unique"):
        DependencyLineage(
            lineage_hash=dependency_lineage_hash(duplicates),
            dependencies=duplicates,
        )
    payload = proof.model_dump()
    payload["dependency_lineage_hash"] = "f" * 64
    with pytest.raises(ValidationError, match="lineage hash"):
        W04SemanticTemporalProof.model_validate(payload)


def test_gold_coverage_is_exact_six_dimension_minimum_and_lexical_missing_set() -> None:
    dimensions = list(complete_coverage().dimensions)
    dimensions[1] = GoldCoverageDimension(
        name=GoldCoverageDimensionName.LINEUP,
        numerator=1,
        denominator=2,
        coverage=Decimal("0.5"),
        state=GoldCoverageState.PARTIAL,
        reason_codes=("LINEUP_PARTIAL",),
    )
    dimensions[4] = GoldCoverageDimension(
        name=GoldCoverageDimensionName.POSSESSION,
        numerator=0,
        denominator=0,
        coverage=Decimal(1),
        state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
        reason_codes=("NO_APPLICABLE_POSSESSION",),
        zero_denominator_authority=accepted_authority_references()[1],
    )
    coverage = GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal("0.5"),
        missing_dimensions=(GoldCoverageDimensionName.LINEUP,),
    )
    assert coverage.coverage_overall == Decimal("0.5")
    assert GoldCoverageDimensionName.POSSESSION not in coverage.missing_dimensions


def test_gold_coverage_negative_matrix_closes_integer_zero_and_order_routes() -> None:
    with pytest.raises(ValidationError, match="cannot exceed"):
        GoldCoverageDimension(
            name=GoldCoverageDimensionName.ACTION,
            numerator=2,
            denominator=1,
            coverage=Decimal(2),
            state=GoldCoverageState.PARTIAL,
        )
    with pytest.raises(ValidationError, match="mandatory zero denominator"):
        GoldCoverageDimension(
            name=GoldCoverageDimensionName.IDENTITY,
            numerator=0,
            denominator=0,
            coverage=Decimal(1),
            state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
        )
    dimensions = tuple(reversed(complete_coverage().dimensions))
    with pytest.raises(ValidationError, match="fixed order"):
        GoldCoverage(
            dimensions=dimensions,
            coverage_overall=Decimal(1),
            missing_dimensions=(),
        )


def test_gold_features_are_exact_four_counts_and_forbid_outcomes_rates_and_roles() -> None:
    features = make_gold().features
    assert set(features.model_dump()) == {
        "action_count",
        "coordinate_known_action_count",
        "match_count",
        "resolved_possession_action_count",
    }
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        GoldFeatureValues.model_validate(
            {
                "action_count": 1,
                "coordinate_known_action_count": 1,
                "match_count": 1,
                "resolved_possession_action_count": 1,
                "actions_per_90": 90,
            }
        )
    payload = make_gold().model_dump()
    payload["current_team_id"] = str(UUID(int=1))
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        GoldPlayerWindow.model_validate(payload)


def test_exact_player_match_and_gold_primary_keys_remain_collision_closed() -> None:
    *_, fact = make_silver_rows()
    gold = make_gold()
    assert fact.primary_key == (
        tenant().tenant_id,
        SOURCE_MANIFEST_ID,
        fact.match_id,
        fact.player_id,
        "w04-wyscout-player-match-fact-v1",
    )
    assert gold.primary_key[-1] == gold.dependency_lineage_hash
    assert gold.role_context_id == ROLE_CONTEXT_ID
    assert gold.role_context_version == ROLE_CONTEXT_VERSION
    assert gold.role_context_state == ROLE_CONTEXT_STATE


def test_all_seventeen_path_roles_accept_only_exact_templates() -> None:
    paths = valid_paths()
    assert tuple(path.path_role for path in paths) == tuple(ProductPathRole)
    assert len(paths) == 17
    assert "/records/record_kind=" in paths[0].relative_path
    assert "/raw/" not in paths[0].relative_path
    assert "source_partition=england" in paths[6].relative_path
    assert "20180101T000000000000Z" in paths[11].relative_path


@pytest.mark.parametrize(
    ("role", "path"),
    (
        (
            ProductPathRole.BRONZE_KNOWN_RECORD,
            f"data/working/wyscout/v5/bronze/build_id={BUILD_ID}/raw/record_kind=action/"
            f"source_sha256={'4' * 64}/part-00000.parquet",
        ),
        (
            ProductPathRole.SILVER_ACTION,
            f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/action/"
            "source_partition=England/part-00000.parquet",
        ),
        (
            ProductPathRole.GOLD_PLAYER_WINDOW,
            f"data/working/wyscout/v5/gold/build_id={BUILD_ID}/player-window/"
            f"competition_id={UUID(int=1)}/window_definition_id={WINDOW_ID}/"
            "window_start_utc=20180101T000000Z/window_end_utc=20190101T000000000000Z/"
            "feature_cutoff_ts=20260801T000000000000Z/part-00000.parquet",
        ),
        (
            ProductPathRole.REBUILD_INVOCATION_RECEIPT,
            f"runs/w04/wyscout-rebuild/{BUILD_ID}/../escape.receipt.json",
        ),
    ),
)
def test_path_negative_matrix_rejects_literal_country_utc_and_escape_drift(
    role: ProductPathRole,
    path: str,
) -> None:
    with pytest.raises(ValidationError, match="exact path role"):
        WyscoutProductPath(path_role=role, relative_path=path)


def test_layer_manifests_enforce_exact_bronze_silver_gold_order_without_writes() -> None:
    paths = {path.path_role: path for path in valid_paths()}
    bronze = LayerManifest(
        layer=Layer.BRONZE,
        build_id=BUILD_ID,
        manifest_path=paths[ProductPathRole.BRONZE_MANIFEST],
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        tenant_context=tenant(),
        classification=restricted_rights(),
        source_available_at=SOURCE_RELEASE,
        source_acquired_at=accepted_source_authority().acquired_at,
        authority_clocks=accepted_authority_clocks(),
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        dependency_lineage_hash=make_dependency_lineage().lineage_hash,
        dependency_lineage=make_dependency_lineage(),
        entries=(manifest_entry(paths[ProductPathRole.BRONZE_KNOWN_RECORD], "bronze.py"),),
        parent_layer_manifests=(),
    )
    silver = LayerManifest(
        layer=Layer.SILVER,
        build_id=BUILD_ID,
        manifest_path=paths[ProductPathRole.SILVER_MANIFEST],
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        tenant_context=tenant(),
        classification=restricted_rights(),
        source_available_at=SOURCE_RELEASE,
        source_acquired_at=accepted_source_authority().acquired_at,
        authority_clocks=accepted_authority_clocks(),
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        dependency_lineage_hash=make_dependency_lineage().lineage_hash,
        dependency_lineage=make_dependency_lineage(),
        entries=(
            manifest_entry(
                paths[ProductPathRole.SILVER_ACTION],
                "actions.py",
                (paths[ProductPathRole.BRONZE_KNOWN_RECORD].relative_path,),
            ),
        ),
        parent_layer_manifests=(
            ParentLayerManifest(
                layer=Layer.BRONZE,
                build_id=BUILD_ID,
                relative_path=bronze.manifest_path.relative_path,
                sha256=SEMANTIC_DIGEST,
            ),
        ),
    )
    gold = LayerManifest(
        layer=Layer.GOLD,
        build_id=BUILD_ID,
        manifest_path=paths[ProductPathRole.GOLD_MANIFEST],
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        tenant_context=tenant(),
        classification=restricted_rights(),
        source_available_at=SOURCE_RELEASE,
        source_acquired_at=accepted_source_authority().acquired_at,
        authority_clocks=accepted_authority_clocks(),
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        dependency_lineage_hash=make_dependency_lineage().lineage_hash,
        dependency_lineage=make_dependency_lineage(),
        entries=(
            manifest_entry(
                paths[ProductPathRole.GOLD_PLAYER_WINDOW],
                "gold.py",
                (paths[ProductPathRole.SILVER_PLAYER_MATCH_FACT].relative_path,),
            ),
        ),
        parent_layer_manifests=(
            ParentLayerManifest(
                layer=Layer.SILVER,
                build_id=BUILD_ID,
                relative_path=silver.manifest_path.relative_path,
                sha256=SEMANTIC_DIGEST,
            ),
        ),
    )
    assert (bronze.layer, silver.layer, gold.layer) == (
        Layer.BRONZE,
        Layer.SILVER,
        Layer.GOLD,
    )
    payload = gold.model_dump()
    payload["parent_layer_manifests"][0]["layer"] = Layer.BRONZE
    with pytest.raises(ValidationError, match="parent manifest|Bronze-to-Silver-to-Gold"):
        LayerManifest.model_validate(payload)


def test_manifest_entry_rejects_serializer_ownership_overlap() -> None:
    action_path = valid_paths()[7]
    with pytest.raises(ValidationError, match="does not own"):
        manifest_entry(action_path, "entities.py")


def test_contract_json_is_canonical_and_no_contract_helper_writes_files() -> None:
    gold = make_gold()
    encoded = canonical_contract_json_bytes(gold)
    assert encoded == canonical_contract_json_bytes(gold)
    assert encoded.startswith(b'{"applicability"')
    assert not encoded.endswith(b"\n")
    assert not hasattr(gold, "write")
    assert not hasattr(gold, "serialize")


@pytest.mark.parametrize(
    ("raw_value", "forged_state"),
    (
        ("Competition", RawKindState.STRING_UNSAFE),
        ("../action", RawKindState.STRING_UNKNOWN_SAFE),
        (17, RawKindState.NULL),
        (None, RawKindState.NON_STRING),
    ),
)
def test_raw_kind_direct_constructor_rejects_every_forged_state(
    raw_value: object,
    forged_state: RawKindState,
) -> None:
    evidence = classify_raw_record_kind(value_present=True, value=raw_value)
    payload = evidence.model_dump()
    payload["raw_kind_state"] = forged_state
    with pytest.raises(ValidationError, match="must be derived"):
        RawKindEvidence.model_validate(payload)


def test_raw_kind_direct_constructor_rejects_known_token_and_digest_mutation() -> None:
    evidence = classify_raw_record_kind(value_present=True, value="Competition")
    known_payload = evidence.model_dump()
    known_payload["value"] = CanonicalJsonString(value="action")
    with pytest.raises(ValidationError, match="known record kinds"):
        RawKindEvidence.model_validate(known_payload)
    digest_payload = evidence.model_dump()
    digest_payload["raw_kind_sha256"] = "0" * 64
    with pytest.raises(ValidationError, match="framed envelope digest"):
        RawKindEvidence.model_validate(digest_payload)


def test_silver_action_direct_constructor_rejects_unaccepted_pair_and_event_id_drift() -> None:
    action = make_silver_rows()[4]
    pair_payload = action.model_dump()
    pair_payload["action_event_taxonomy_id"] = 99
    pair_payload["action_subevent_taxonomy_id"] = 999
    with pytest.raises(ValidationError, match="admitted strict integer pair"):
        SilverAction.model_validate(pair_payload)
    id_payload = action.model_dump()
    id_payload["source_event_record_id"] = action.action_source_id + 1
    with pytest.raises(ValidationError, match="must equal the action source ID"):
        SilverAction.model_validate(id_payload)
    team_payload = action.model_dump()
    team_payload["team_id"] = None
    with pytest.raises(ValidationError, match="predicate admission|complete-sequence"):
        SilverAction.model_validate(team_payload)


@pytest.mark.parametrize(
    "raw_value",
    (
        "10",
        True,
        None,
        Decimal("10.0"),
        [],
        {},
        999,
    ),
)
def test_rejected_subevent_constructor_accepts_only_exact_field_v2_route(
    raw_value: object,
) -> None:
    rejected = make_rejected_field(raw_value)
    assert rejected.decision is RejectedFieldDecision.PRESERVE_UNMAPPED
    payload = rejected.model_dump()
    payload["reason_code"] = "ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED"
    if rejected.reason_code == payload["reason_code"]:
        payload["reason_code"] = "ACTION_SUBEVENT_OBJECT_UNMAPPED"
    with pytest.raises(ValidationError, match="decision/reason"):
        BronzeRejectedField.model_validate(payload)


def test_rejected_subevent_rejects_admitted_integer_path_type_and_decision_drift() -> None:
    with pytest.raises(ValidationError, match="cannot be rejected"):
        make_rejected_field(70)
    rejected = make_rejected_field("10")
    mutations: tuple[tuple[str, object], ...] = (
        ("json_path", "$.eventId"),
        ("measured_json_type", CanonicalJsonKind.INTEGER),
        ("decision", RejectedFieldDecision.FORBIDDEN),
    )
    for field, value in mutations:
        payload = rejected.model_dump()
        payload[field] = value
        with pytest.raises(ValidationError):
            BronzeRejectedField.model_validate(payload)
    family_payload = rejected.model_dump()
    family_payload["source_row"] = make_envelopes()[6].source_row_reference
    with pytest.raises(ValidationError, match="record_kind"):
        BronzeRejectedField.model_validate(family_payload)


@pytest.mark.parametrize("invalid_source_id", (0, -1, True))
@pytest.mark.parametrize(
    "record_kind",
    (
        SourceRecordKind.COMPETITION,
        SourceRecordKind.TEAM,
        SourceRecordKind.PLAYER,
        SourceRecordKind.MATCH,
        SourceRecordKind.ACTION,
    ),
)
def test_canonical_source_uuid_rejects_nonpositive_and_boolean_ids(
    record_kind: SourceRecordKind,
    invalid_source_id: object,
) -> None:
    with pytest.raises(ValueError, match="strict positive"):
        canonical_source_uuid(record_kind, invalid_source_id)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("row_index", "source_id_field"),
    (
        (0, "competition_source_id"),
        (1, "team_source_id"),
        (2, "player_source_id"),
        (3, "match_source_id"),
        (4, "action_source_id"),
    ),
)
@pytest.mark.parametrize("invalid_source_id", (0, -1, True))
def test_every_public_entity_action_constructor_rejects_invalid_source_ids(
    row_index: int,
    source_id_field: str,
    invalid_source_id: object,
) -> None:
    row = make_silver_rows()[row_index]
    payload = row.model_dump()
    payload[source_id_field] = invalid_source_id
    with pytest.raises(ValidationError):
        type(row).model_validate(payload)


@pytest.mark.parametrize(
    ("value", "source_scale"),
    (
        (Decimal("1E+4"), 0),
        (Decimal("1.0000000000000000000"), 19),
        (Decimal("NaN"), 0),
        (Decimal("Infinity"), 0),
        (Decimal("10.250"), 2),
    ),
)
def test_action_decimal128_rejects_exponent_scale_nonfinite_and_lexical_drift(
    value: Decimal,
    source_scale: int,
) -> None:
    payload = action_payload_with_sequence_updates(
        make_silver_rows()[4], period_elapsed_seconds=value
    )
    payload["event_sec_source_scale"] = source_scale
    with pytest.raises(ValidationError):
        SilverAction.model_validate(payload)


@pytest.mark.parametrize(
    ("value", "source_scale"),
    (
        (Decimal("9999"), 0),
        (Decimal("1E+3"), 0),
        (Decimal("9999.123456789012345678"), 18),
        (Decimal("0.000000000000000001"), 18),
    ),
)
def test_action_decimal128_accepts_exact_capacity_boundaries(
    value: Decimal,
    source_scale: int,
) -> None:
    payload = action_payload_with_sequence_updates(
        make_silver_rows()[4], period_elapsed_seconds=value
    )
    payload["event_sec_source_scale"] = source_scale
    assert SilverAction.model_validate(payload).period_elapsed_seconds == value


@pytest.mark.parametrize("clock_index", range(4))
@pytest.mark.parametrize("clock_field", ("decided_at", "reviewed_at", "accepted_at"))
def test_every_authority_clock_is_exact_at_direct_constructor(
    clock_index: int,
    clock_field: str,
) -> None:
    payload = accepted_authority_clocks()[clock_index].model_dump()
    payload[clock_field] = datetime(2026, 7, 31, 15, tzinfo=UTC)
    with pytest.raises(ValidationError, match="accepted records"):
        WyscoutAuthorityClock.model_validate(payload)


@pytest.mark.parametrize("dependency_index", range(5))
@pytest.mark.parametrize("clock_field", ("observed_at", "available_at"))
def test_every_dependency_clock_is_bound_to_accepted_authority(
    dependency_index: int,
    clock_field: str,
) -> None:
    dependencies = list(make_dependencies())
    payload = dependencies[dependency_index].model_dump()
    payload[clock_field] = datetime(2026, 7, 31, 15, tzinfo=UTC)
    dependencies[dependency_index] = EvidenceDependency.model_validate(payload)
    ordered = tuple(sorted(dependencies, key=dependency_sort_key))
    drifted = DependencyLineage(
        lineage_hash=dependency_lineage_hash(ordered),
        dependencies=ordered,
    )
    lineage_payload = make_lineage().model_dump()
    lineage_payload["dependency_lineage"] = drifted
    with pytest.raises(ValidationError, match="dependency|authority|manifest"):
        WyscoutRowLineage.model_validate(lineage_payload)


def test_recomputed_lineage_and_cross_boundary_equality_are_mandatory() -> None:
    dependencies = make_dependencies()
    forged = DependencyLineage(lineage_hash="f" * 64, dependencies=dependencies)
    lineage_payload = make_lineage().model_dump()
    lineage_payload["dependency_lineage"] = forged
    with pytest.raises(ValidationError, match="recomputed"):
        WyscoutRowLineage.model_validate(lineage_payload)

    alternate = make_alternate_dependency_lineage()
    alternate_lineage_payload = make_lineage().model_dump()
    alternate_lineage_payload["dependency_lineage"] = alternate
    alternate_lineage = WyscoutRowLineage.model_validate(alternate_lineage_payload)
    fact_payload = make_silver_rows()[-1].model_dump()
    fact_payload["lineage"] = alternate_lineage
    with pytest.raises(ValidationError, match="authority|temporal-proof"):
        SilverPlayerMatchFact.model_validate(fact_payload)
    gold_payload = make_gold().model_dump()
    gold_payload["lineage"] = alternate_lineage
    with pytest.raises(ValidationError, match="must equal temporal-proof"):
        GoldPlayerWindow.model_validate(gold_payload)


@pytest.mark.parametrize(
    ("dimension_name", "authority_index"),
    (
        (GoldCoverageDimensionName.COORDINATE, 0),
        (GoldCoverageDimensionName.POSSESSION, 1),
    ),
)
def test_optional_zero_coverage_requires_exact_corresponding_authority(
    dimension_name: GoldCoverageDimensionName,
    authority_index: int,
) -> None:
    with pytest.raises(ValidationError, match="exact accepted authority"):
        GoldCoverageDimension(
            name=dimension_name,
            numerator=0,
            denominator=0,
            coverage=Decimal(1),
            state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
            reason_codes=("NO_APPLICABLE_EVIDENCE",),
        )
    proof = accepted_authority_references()[authority_index]
    assert (
        GoldCoverageDimension(
            name=dimension_name,
            numerator=0,
            denominator=0,
            coverage=Decimal(1),
            state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
            reason_codes=("NO_APPLICABLE_EVIDENCE",),
            zero_denominator_authority=proof,
        ).coverage
        == 1
    )


def test_coverage_failure_states_are_representable_but_never_data_ready() -> None:
    dimensions = list(complete_coverage().dimensions)
    dimensions[2] = GoldCoverageDimension(
        name=GoldCoverageDimensionName.ACTION,
        numerator=0,
        denominator=1,
        coverage=Decimal(0),
        state=GoldCoverageState.FAILED,
        reason_codes=("ACTION_RECONCILIATION_FAILED",),
    )
    failed_coverage = GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal(0),
        missing_dimensions=(GoldCoverageDimensionName.ACTION,),
    )
    payload = make_silver_rows()[-1].model_dump()
    payload["coverage"] = failed_coverage
    with pytest.raises(ValidationError, match="coverage must derive"):
        SilverPlayerMatchFact.model_validate(payload)


def test_partial_or_uncertain_facts_are_research_only_in_exact_gate_order() -> None:
    dimensions = list(complete_coverage().dimensions)
    dimensions[1] = GoldCoverageDimension(
        name=GoldCoverageDimensionName.LINEUP,
        numerator=1,
        denominator=2,
        coverage=Decimal("0.5"),
        state=GoldCoverageState.PARTIAL,
        reason_codes=("LINEUP_PARTIAL",),
    )
    partial = GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal("0.5"),
        missing_dimensions=(GoldCoverageDimensionName.LINEUP,),
    )
    payload = make_silver_rows()[-1].model_dump()
    payload["coverage"] = partial
    payload["applicability"] = W04ApplicabilityAssessment(
        state=W04Applicability.RESEARCH_ONLY,
        reason_codes=("LINEUP_PARTIAL",),
    )
    with pytest.raises(ValidationError, match="coverage must derive"):
        SilverPlayerMatchFact.model_validate(payload)
    uncertain_payload = make_silver_rows()[-1].model_dump()
    uncertain_payload["right_censored_or_uncertain"] = True
    uncertain_payload["applicability"] = W04ApplicabilityAssessment(
        state=W04Applicability.RESEARCH_ONLY,
        reason_codes=("RIGHT_CENSORED_OR_UNCERTAIN",),
    )
    assert SilverPlayerMatchFact.model_validate(uncertain_payload).applicability.state is (
        W04Applicability.RESEARCH_ONLY
    )


def make_bronze_manifest() -> LayerManifest:
    paths = {path.path_role: path for path in valid_paths()}
    lineage = make_dependency_lineage()
    return LayerManifest(
        layer=Layer.BRONZE,
        build_id=BUILD_ID,
        manifest_path=paths[ProductPathRole.BRONZE_MANIFEST],
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        tenant_context=tenant(),
        classification=restricted_rights(),
        source_available_at=SOURCE_RELEASE,
        source_acquired_at=accepted_source_authority().acquired_at,
        authority_clocks=accepted_authority_clocks(),
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        dependency_lineage_hash=lineage.lineage_hash,
        dependency_lineage=lineage,
        entries=(manifest_entry(paths[ProductPathRole.BRONZE_KNOWN_RECORD], "bronze.py"),),
        parent_layer_manifests=(),
    )


def test_manifest_direct_constructors_close_filename_empty_parent_schema_and_partitions() -> None:
    bronze = make_bronze_manifest()
    filename_payload = bronze.model_dump()
    filename_payload["manifest_path"]["relative_path"] = (
        f"data/manifests/wyscout/v5/bronze/{'b' * 64}.manifest.json"
    )
    with pytest.raises(ValidationError, match="filename/layer/build"):
        LayerManifest.model_validate(filename_payload)
    empty_payload = bronze.model_dump()
    empty_payload["entries"] = ()
    with pytest.raises(ValidationError):
        LayerManifest.model_validate(empty_payload)
    with pytest.raises(ValidationError, match="exact safe same-build path"):
        ParentLayerManifest(
            layer=Layer.BRONZE,
            build_id=BUILD_ID,
            relative_path="../escape",
            sha256=SEMANTIC_DIGEST,
        )
    entry = bronze.entries[0]
    schema_payload = entry.model_dump()
    schema_payload["schema_role"] = ProductPathRole.SILVER_ACTION.value
    with pytest.raises(ValidationError, match="schema_role"):
        LayerManifestEntry.model_validate(schema_payload)
    partition_payload = entry.model_dump()
    partition_payload["partition_values"] = partition_payload["partition_values"][:-1]
    with pytest.raises(ValidationError, match="partition values"):
        LayerManifestEntry.model_validate(partition_payload)


def test_manifest_rejects_cross_layer_parent_tenant_rights_feature_and_lineage_drift() -> None:
    paths = {path.path_role: path for path in valid_paths()}
    with pytest.raises(ValidationError, match="preceding layer"):
        manifest_entry(
            paths[ProductPathRole.SILVER_ACTION],
            "actions.py",
            (paths[ProductPathRole.SILVER_TEAM].relative_path,),
        )
    bronze = make_bronze_manifest()
    tenant_payload = bronze.model_dump()
    tenant_payload["tenant_context"] = TenantContext(tenant_id=UUID(int=1))
    with pytest.raises(ValidationError, match="source authority"):
        LayerManifest.model_validate(tenant_payload)
    feature_payload = bronze.model_dump()
    feature_payload["feature_schema_hash"] = "f" * 64
    with pytest.raises(ValidationError, match="feature schema"):
        LayerManifest.model_validate(feature_payload)
    lineage_payload = bronze.model_dump()
    lineage_payload["dependency_lineage_hash"] = "f" * 64
    with pytest.raises(ValidationError, match="lineage hash"):
        LayerManifest.model_validate(lineage_payload)
    rights_payload = bronze.entries[0].model_dump()
    rights_payload["classification"] = SourceUseClassification(
        use_class=LicenceUseClass.OPEN,
        derived_data_allowed=True,
        internal_review_allowed=True,
        export_allowed=True,
        attribution_required=False,
    )
    with pytest.raises(ValidationError, match="exact restricted"):
        LayerManifestEntry.model_validate(rights_payload)


@pytest.mark.parametrize(
    "feature_name",
    (
        "action_count",
        "coordinate_known_action_count",
        "match_count",
        "resolved_possession_action_count",
    ),
)
def test_gold_recomputes_each_of_the_exact_four_features(feature_name: str) -> None:
    payload = make_gold().model_dump()
    payload["features"][feature_name] += 1
    with pytest.raises(ValidationError):
        GoldPlayerWindow.model_validate(payload)


def test_gold_rejects_arbitrary_keys_fact_identity_schema_and_window_selection() -> None:
    gold = make_gold()
    key_payload = gold.model_dump()
    original_key = key_payload["contributing_player_match_keys"][0]
    key_payload["contributing_player_match_keys"] = ((UUID(int=1), *original_key[1:]),)
    with pytest.raises(ValidationError, match="keys must derive"):
        GoldPlayerWindow.model_validate(key_payload)
    identity_payload = gold.model_dump()
    identity_fact = dict(identity_payload["contributing_player_match_facts"][0])
    identity_fact["player_id"] = UUID(int=2)
    with pytest.raises(ValidationError, match="leaks across fact identity"):
        SilverPlayerMatchFact.model_validate(identity_fact)
    schema_payload = gold.model_dump()
    schema_fact = dict(schema_payload["contributing_player_match_facts"][0])
    schema_fact["player_match_fact_schema_version"] = "arbitrary"
    schema_payload["contributing_player_match_facts"] = (schema_fact,)
    with pytest.raises(ValidationError):
        GoldPlayerWindow.model_validate(schema_payload)
    window_payload = gold.model_dump()
    window_fact = dict(window_payload["contributing_player_match_facts"][0])
    window_fact["match_start_utc"] = WINDOW_END
    window_payload["contributing_player_match_facts"] = (window_fact,)
    with pytest.raises(ValidationError, match="outside the Gold window"):
        GoldPlayerWindow.model_validate(window_payload)


@pytest.mark.parametrize(
    ("path", "kind", "digest", "row_count"),
    (
        (SOURCE_ROWS[0][0], SOURCE_ROWS[0][1], SOURCE_ROWS[0][2], 643150),
        (SOURCE_ROWS[1][0], SOURCE_ROWS[1][1], SOURCE_ROWS[1][2], 380),
        (SOURCE_ROWS[2][0], SOURCE_ROWS[2][1], SOURCE_ROWS[2][2], 7),
        (SOURCE_ROWS[3][0], SOURCE_ROWS[3][1], SOURCE_ROWS[3][2], 36),
        (SOURCE_ROWS[4][0], SOURCE_ROWS[4][1], SOURCE_ROWS[4][2], 3603),
        (SOURCE_ROWS[5][0], SOURCE_ROWS[5][1], SOURCE_ROWS[5][2], 59),
        (SOURCE_ROWS[6][0], SOURCE_ROWS[6][1], SOURCE_ROWS[6][2], 142),
    ),
)
def test_source_ordinal_is_strictly_below_exact_manifested_row_count(
    path: str,
    kind: SourceRecordKind,
    digest: str,
    row_count: int,
) -> None:
    with pytest.raises(ValidationError, match="below the manifested row count"):
        WyscoutRawSourceRowReference(
            source_manifest_id=SOURCE_MANIFEST_ID,
            completion_relative_path=path,
            source_sha256=digest,
            source_record_ordinal=row_count,
        )
    assert (
        WyscoutRawSourceRowReference(
            source_manifest_id=SOURCE_MANIFEST_ID,
            completion_relative_path=path,
            source_sha256=digest,
            source_record_ordinal=row_count - 1,
        ).source_record_ordinal
        == row_count - 1
    )
    assert kind in SourceRecordKind


def test_bronze_requires_exact_measurements_tenant_rights_and_source_membership() -> None:
    envelope = make_envelopes()[0]
    base = BronzeKnownRecord(
        build_id=BUILD_ID,
        tenant_context=tenant(),
        source_row=envelope.source_row_reference,
        raw_record=envelope.raw_record,
        raw_record_sha256=envelope.source_row_reference.raw_record_sha256,
        measured_raw_fields=measurements(envelope.raw_record),
        classification=restricted_rights(),
        lineage=make_lineage(),
    )
    measurement_payload = base.model_dump()
    measurement_payload["measured_raw_fields"] = measurement_payload["measured_raw_fields"][:-1]
    with pytest.raises(ValidationError, match="exactly cover"):
        BronzeKnownRecord.model_validate(measurement_payload)
    tenant_payload = base.model_dump()
    tenant_payload["tenant_context"] = TenantContext(tenant_id=UUID(int=1))
    with pytest.raises(ValidationError, match="no-club tenant"):
        BronzeKnownRecord.model_validate(tenant_payload)
    rights_payload = base.model_dump()
    rights_payload["classification"]["export_allowed"] = True
    with pytest.raises(ValidationError, match="restricted rights"):
        BronzeKnownRecord.model_validate(rights_payload)
    lineage_payload = make_lineage().model_dump()
    lineage_payload["source_rows"] = (make_envelopes()[1].source_row_reference,)
    wrong_lineage = WyscoutRowLineage.model_validate(lineage_payload)
    membership_payload = base.model_dump()
    membership_payload["lineage"] = wrong_lineage
    with pytest.raises(ValidationError, match="must occur in lineage"):
        BronzeKnownRecord.model_validate(membership_payload)


def test_source_authority_and_silver_source_family_fail_closed() -> None:
    source_payload = accepted_source_authority().model_dump()
    source_payload["acquired_at"] = SOURCE_RELEASE
    with pytest.raises(ValidationError, match="accepted source snapshot"):
        type(accepted_source_authority()).model_validate(source_payload)

    lineage_payload = make_lineage().model_dump()
    lineage_payload["source_rows"] = (make_envelopes()[6].source_row_reference,)
    team_only_lineage = WyscoutRowLineage.model_validate(lineage_payload)
    competition_payload = make_silver_rows()[0].model_dump()
    competition_payload["lineage"] = team_only_lineage
    with pytest.raises(ValidationError, match="selected source row"):
        SilverCompetition.model_validate(competition_payload)


def test_r3_forged_subevent_outcome_direct_constructor_fails_closed() -> None:
    raw = CanonicalJsonInteger(value=70)
    with pytest.raises(ValidationError, match="derive exactly"):
        ActionSubeventOutcome(
            action_event_taxonomy_id=7,
            raw_subevent=raw,
            canonical_value=999,
        )
    with pytest.raises(ValidationError, match="derive exactly"):
        ActionSubeventOutcome(
            action_event_taxonomy_id=7,
            raw_subevent=CanonicalJsonString(value="70"),
            rejected_raw_value=CanonicalJsonString(value="70"),
            reason_code=ActionSubeventReason.UNKNOWN_INTEGER,
        )


_POSSESSION_INELIGIBLE_PAIRS = {
    (2, 23),
    (2, 24),
    (2, 25),
    (2, 26),
    (4, 40),
    (5, 51),
    (9, 90),
    (9, 91),
}
_POSSESSION_ADMITTED_PAIRS = (
    (1, 10),
    (1, 11),
    (1, 12),
    (1, 13),
    (2, 20),
    (2, 21),
    (2, 22),
    (2, 23),
    (2, 24),
    (2, 25),
    (2, 26),
    (2, 27),
    (3, 30),
    (3, 31),
    (3, 32),
    (3, 33),
    (3, 34),
    (3, 35),
    (3, 36),
    (4, 40),
    (5, 50),
    (5, 51),
    (6, 60),
    (7, 70),
    (7, 71),
    (7, 72),
    (8, 80),
    (8, 81),
    (8, 82),
    (8, 83),
    (8, 84),
    (8, 85),
    (8, 86),
    (9, 90),
    (9, 91),
    (10, 100),
)


@pytest.mark.parametrize("event_subevent", _POSSESSION_ADMITTED_PAIRS)
def test_r3_all_36_pairs_preserve_predicate_admission_and_singleton_sequence_state(
    event_subevent: tuple[int, int],
) -> None:
    payload = action_payload_with_sequence_updates(
        make_silver_rows()[4],
        action_event_taxonomy_id=event_subevent[0],
        action_subevent_taxonomy_id=event_subevent[1],
    )
    payload["possession_predicate_state"] = PossessionPredicateState.PREDICATE_ADMITTED
    singleton_resolved = event_subevent[0] in {3, 7, 8, 10}
    expected = (
        PossessionEligibilityState.ELIGIBLE_RESOLVED
        if singleton_resolved
        else PossessionEligibilityState.INELIGIBLE_UNMAPPED
    )
    payload["possession_eligibility_state"] = expected
    assert SilverAction.model_validate(payload).possession_eligibility_state is expected
    payload["possession_eligibility_state"] = (
        PossessionEligibilityState.ELIGIBLE_RESOLVED
        if expected is PossessionEligibilityState.INELIGIBLE_UNMAPPED
        else PossessionEligibilityState.INELIGIBLE_UNMAPPED
    )
    with pytest.raises(ValidationError, match="possession eligibility"):
        SilverAction.model_validate(payload)


def test_r3_physical_source_key_rejects_digest_drift_but_distinct_paths_share_ordinal() -> None:
    lineage = make_lineage()
    assert len({row.source_record_ordinal for row in lineage.source_rows}) == 1
    assert len(lineage.source_rows) == 7
    original = lineage.source_rows[0]
    forged = WyscoutSourceRowReference.model_validate(
        {**original.model_dump(), "raw_record_sha256": "f" * 64}
    )
    payload = lineage.model_dump()
    payload["source_rows"] = tuple(
        sorted(
            (*lineage.source_rows, forged),
            key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
        )
    )
    with pytest.raises(ValidationError, match="physical path/ordinal"):
        WyscoutRowLineage.model_validate(payload)


def test_r3_every_silver_row_selects_exact_source_and_match_partition_is_derived() -> None:
    rows = make_silver_rows()
    assert {row.record_kind for row in make_lineage().source_rows} == set(SourceRecordKind)
    assert all(row.source_rows for row in rows)
    payload = rows[3].model_dump()
    payload["source_partition"] = CountryPartition.FRANCE
    with pytest.raises(ValidationError, match="country partition"):
        SilverMatch.model_validate(payload)
    action_payload = rows[4].model_dump()
    action_payload["source_record_ordinal"] = 1
    with pytest.raises(ValidationError, match="derive from its selected source row"):
        SilverAction.model_validate(action_payload)


@pytest.mark.parametrize("mutated_field", ("dependency_id", "digest"))
def test_r3_identity_dependency_id_and_digest_substitutions_fail_closed(
    mutated_field: str,
) -> None:
    dependencies = list(make_dependencies())
    index = next(
        index
        for index, dependency in enumerate(dependencies)
        if dependency.kind is DependencyKind.IDENTITY_EVIDENCE
    )
    payload = dependencies[index].model_dump()
    payload[mutated_field] = UUID(int=1) if mutated_field == "dependency_id" else "9" * 64
    dependencies[index] = EvidenceDependency.model_validate(payload)
    ordered = tuple(sorted(dependencies, key=dependency_sort_key))
    lineage_payload = make_lineage().model_dump()
    lineage_payload["dependency_lineage"] = DependencyLineage(
        lineage_hash=dependency_lineage_hash(ordered),
        dependencies=ordered,
    )
    with pytest.raises(ValidationError, match="identity dependency"):
        WyscoutRowLineage.model_validate(lineage_payload)


@pytest.mark.parametrize(
    ("json_path", "decision", "reason"),
    (
        ("$.format", RejectedFieldDecision.PRESERVE_UNMAPPED, "FIELD_V2_PRESERVE_UNMAPPED"),
        ("$.name", RejectedFieldDecision.FORBIDDEN, "FIELD_V2_FORBIDDEN"),
    ),
)
def test_r3_generic_field_v2_preserve_and_forbidden_rows_are_exact(
    json_path: str,
    decision: RejectedFieldDecision,
    reason: str,
) -> None:
    value = CanonicalJsonString(value="retained")
    source_row = make_envelopes()[2].source_row_reference
    rejected = BronzeRejectedField(
        build_id=BUILD_ID,
        tenant_context=tenant(),
        source_row=source_row,
        record_kind=SourceRecordKind.COMPETITION,
        json_path=json_path,
        original_value=value,
        original_value_sha256=hashlib.sha256(canonical_raw_json_bytes(value)).hexdigest(),
        measured_json_type=CanonicalJsonKind.STRING,
        decision=decision,
        reason_code=reason,
        field_authority=accepted_authority_references()[0],
        classification=restricted_rights(),
        lineage=make_lineage(),
    )
    assert rejected.decision is decision
    payload = rejected.model_dump()
    payload["reason_code"] = "UNRELATED_REASON"
    with pytest.raises(ValidationError, match="decision/reason"):
        BronzeRejectedField.model_validate(payload)


def test_r3_transformable_generic_registry_row_cannot_be_quarantined() -> None:
    value = CanonicalJsonInteger(value=1)
    with pytest.raises(ValidationError, match="transformable"):
        BronzeRejectedField(
            build_id=BUILD_ID,
            tenant_context=tenant(),
            source_row=make_envelopes()[2].source_row_reference,
            record_kind=SourceRecordKind.COMPETITION,
            json_path="$.wyId",
            original_value=value,
            original_value_sha256=hashlib.sha256(canonical_raw_json_bytes(value)).hexdigest(),
            measured_json_type=CanonicalJsonKind.INTEGER,
            decision=RejectedFieldDecision.PRESERVE_UNMAPPED,
            reason_code="FIELD_V2_PRESERVE_UNMAPPED",
            field_authority=accepted_authority_references()[0],
            classification=restricted_rights(),
            lineage=make_lineage(),
        )


def test_r3_unknown_pair_rejection_allows_absent_canonical_event_evidence() -> None:
    rejected = make_rejected_field(999, action_event_taxonomy_id=7)
    payload = rejected.model_dump()
    payload["action_event_taxonomy_id"] = None
    assert BronzeRejectedField.model_validate(payload).action_event_taxonomy_id is None


@pytest.mark.parametrize(
    "feature_name",
    ("action_count", "coordinate_known_action_count", "resolved_possession_action_count"),
)
def test_r3_fact_counts_are_derived_from_closed_action_and_possession_evidence(
    feature_name: str,
) -> None:
    payload = make_silver_rows()[-1].model_dump()
    payload[feature_name] += 1
    with pytest.raises(ValidationError, match="feature counts"):
        SilverPlayerMatchFact.model_validate(payload)


def test_r3_fact_rejects_missing_possession_membership_and_action_leakage() -> None:
    fact = make_silver_rows()[-1]
    missing_membership = fact.model_dump()
    missing_membership["contributing_possessions"] = ()
    with pytest.raises(ValidationError, match="single membership"):
        SilverPlayerMatchFact.model_validate(missing_membership)
    leaked_action_payload = action_payload_with_sequence_updates(
        fact.contributing_actions[0],
        player_id=canonical_source_uuid(SourceRecordKind.PLAYER, 99),
    )
    leaked_action = SilverAction.model_validate(leaked_action_payload)
    leaked_fact = fact.model_dump()
    leaked_fact["contributing_actions"] = (leaked_action,)
    with pytest.raises(ValidationError, match="leaks across fact identity"):
        SilverPlayerMatchFact.model_validate(leaked_fact)


def test_r3_possession_rejects_action_scope_and_evidence_leakage() -> None:
    possession = make_silver_rows()[6]
    leaked_action_payload = action_payload_with_sequence_updates(
        possession.contributing_actions[0],
        team_id=canonical_source_uuid(SourceRecordKind.TEAM, 99),
    )
    leaked_action = SilverAction.model_validate(leaked_action_payload)
    payload = possession.model_dump()
    payload["contributing_actions"] = (leaked_action,)
    with pytest.raises(ValidationError, match="complete resolved sequence group|scope"):
        SilverPossession.model_validate(payload)


@pytest.mark.parametrize("dimension_index", range(6))
def test_r3_gold_rejects_coverage_drift_in_each_of_six_dimensions(
    dimension_index: int,
) -> None:
    gold = make_gold()
    dimensions = list(gold.coverage.dimensions)
    original = dimensions[dimension_index]
    dimensions[dimension_index] = GoldCoverageDimension(
        name=original.name,
        numerator=2,
        denominator=2,
        coverage=Decimal(1),
        state=GoldCoverageState.COMPLETE,
    )
    payload = gold.model_dump()
    payload["coverage"] = GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal(1),
        missing_dimensions=(),
    )
    with pytest.raises(ValidationError, match="aggregate exactly"):
        GoldPlayerWindow.model_validate(payload)


@pytest.mark.parametrize(
    ("dimension", "authority_kind"),
    (
        (GoldCoverageDimensionName.COORDINATE, AuthorityKind.FIELD),
        (GoldCoverageDimensionName.POSSESSION, AuthorityKind.POSSESSION),
    ),
)
def test_r3_gold_aggregates_optional_zero_denominator_authority(
    dimension: GoldCoverageDimensionName,
    authority_kind: AuthorityKind,
) -> None:
    authority = next(
        row for row in accepted_authority_references() if row.authority_kind is authority_kind
    )
    *_, base_action, _, base_possession, base_fact = make_silver_rows()
    dimensions = list(complete_coverage().dimensions)
    index = list(GoldCoverageDimensionName).index(dimension)
    possessions: tuple[SilverPossession, ...]
    if dimension is GoldCoverageDimensionName.COORDINATE:
        action_payload = base_action.model_dump()
        action_payload["action_positions"] = ()
        action = SilverAction.model_validate(action_payload)
        possession_payload = base_possession.model_dump()
        possession_payload["contributing_actions"] = (action,)
        possession = SilverPossession.model_validate(possession_payload)
        possessions = (possession,)
        coordinate_count = 0
        resolved_count = 1
        reason = "NO_APPLICABLE_COORDINATE_EVIDENCE"
    else:
        action_payload = action_payload_with_sequence_updates(
            base_action,
            action_event_taxonomy_id=2,
            action_subevent_taxonomy_id=24,
        )
        action_payload["possession_predicate_state"] = PossessionPredicateState.PREDICATE_ADMITTED
        action_payload["possession_eligibility_state"] = (
            PossessionEligibilityState.INELIGIBLE_UNMAPPED
        )
        action = SilverAction.model_validate(action_payload)
        possessions = ()
        coordinate_count = 1
        resolved_count = 0
        reason = "NO_POSSESSION_ELIGIBLE_ACTIONS"
    dimensions[index] = GoldCoverageDimension(
        name=dimension,
        numerator=0,
        denominator=0,
        coverage=Decimal(1),
        state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
        reason_codes=(reason,),
        zero_denominator_authority=authority,
    )
    coverage = GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal(1),
        missing_dimensions=(),
    )
    fact_payload = base_fact.model_dump()
    fact_payload["contributing_actions"] = (action,)
    fact_payload["contributing_possessions"] = possessions
    fact_payload["coordinate_known_action_count"] = coordinate_count
    fact_payload["resolved_possession_action_count"] = resolved_count
    fact_payload["coverage"] = coverage
    fact = SilverPlayerMatchFact.model_validate(fact_payload)
    gold_payload = make_gold().model_dump()
    gold_payload["coverage"] = coverage
    gold_payload["contributing_player_match_facts"] = (fact,)
    gold_payload["contributing_player_match_keys"] = (fact.primary_key,)
    gold_payload["features"]["coordinate_known_action_count"] = coordinate_count
    gold_payload["features"]["resolved_possession_action_count"] = resolved_count
    assert GoldPlayerWindow.model_validate(gold_payload).coverage == coverage


@pytest.mark.parametrize(
    "reason_codes",
    (
        (),
        ("LINEUP_PARTIAL", "UNRELATED_REASON"),
        ("UNRELATED_REASON",),
    ),
)
def test_r3_applicability_reason_drift_fails_closed(
    reason_codes: tuple[str, ...],
) -> None:
    dimensions = list(complete_coverage().dimensions)
    dimensions[1] = GoldCoverageDimension(
        name=GoldCoverageDimensionName.LINEUP,
        numerator=1,
        denominator=2,
        coverage=Decimal("0.5"),
        state=GoldCoverageState.PARTIAL,
        reason_codes=("LINEUP_PARTIAL",),
    )
    payload = make_silver_rows()[-1].model_dump()
    payload["coverage"] = GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal("0.5"),
        missing_dimensions=(GoldCoverageDimensionName.LINEUP,),
    )
    payload["applicability"] = {
        "state": W04Applicability.RESEARCH_ONLY,
        "reason_codes": reason_codes,
    }
    with pytest.raises(ValidationError):
        SilverPlayerMatchFact.model_validate(payload)


@pytest.mark.parametrize(
    ("role", "parents"),
    (
        (ProductPathRole.BRONZE_KNOWN_RECORD, ()),
        (
            ProductPathRole.SILVER_ACTION,
            (
                f"data/working/wyscout/v5/bronze/build_id={BUILD_ID}/records/"
                f"record_kind=action/source_sha256={'4' * 64}/part-00000.parquet",
            ),
        ),
        (
            ProductPathRole.GOLD_PLAYER_WINDOW,
            (
                f"data/working/wyscout/v5/silver/build_id={BUILD_ID}/player-match-fact/"
                "source_partition=england/part-00000.parquet",
            ),
        ),
    ),
)
@pytest.mark.parametrize("count_field", ("row_count", "size_bytes"))
def test_r3_zero_materialization_is_absence_not_a_manifest_entry(
    role: ProductPathRole,
    parents: tuple[str, ...],
    count_field: str,
) -> None:
    path = next(path for path in valid_paths() if path.path_role is role)
    serializer = {
        ProductPathRole.BRONZE_KNOWN_RECORD: "bronze.py",
        ProductPathRole.SILVER_ACTION: "actions.py",
        ProductPathRole.GOLD_PLAYER_WINDOW: "gold.py",
    }[role]
    payload = manifest_entry(path, serializer, ordered_parent_paths=parents).model_dump()
    payload[count_field] = 0
    with pytest.raises(ValidationError):
        LayerManifestEntry.model_validate(payload)


@pytest.mark.parametrize("dimension_index", range(6))
def test_r4_fact_rejects_every_internally_consistent_coverage_2_of_2_forgery(
    dimension_index: int,
) -> None:
    fact = make_silver_rows()[-1]
    dimensions = list(fact.coverage.dimensions)
    dimensions[dimension_index] = GoldCoverageDimension(
        name=dimensions[dimension_index].name,
        numerator=2,
        denominator=2,
        coverage=Decimal(1),
        state=GoldCoverageState.COMPLETE,
    )
    payload = fact.model_dump()
    payload["coverage"] = GoldCoverage(
        dimensions=tuple(dimensions),
        coverage_overall=Decimal(1),
        missing_dimensions=(),
    )
    with pytest.raises(ValidationError, match="coverage must derive exactly"):
        SilverPlayerMatchFact.model_validate(payload)


@pytest.mark.parametrize(
    "positions",
    (
        (ActionPosition(x=Decimal(-1), y=Decimal(50), within_accepted_bounds=False),),
        (
            ActionPosition(x=Decimal(50), y=Decimal(60), within_accepted_bounds=True),
            ActionPosition(x=Decimal(50), y=Decimal(101), within_accepted_bounds=False),
        ),
        (
            ActionPosition(x=Decimal(10), y=Decimal(20), within_accepted_bounds=True),
            ActionPosition(x=Decimal(30), y=Decimal(40), within_accepted_bounds=True),
            ActionPosition(x=Decimal(50), y=Decimal(60), within_accepted_bounds=True),
        ),
    ),
)
def test_r4_out_of_bounds_or_mixed_positions_propagate_ineligible_fact_to_gold(
    positions: tuple[ActionPosition, ...],
) -> None:
    *_, base_action, _, base_possession, base_fact = make_silver_rows()
    action_payload = base_action.model_dump()
    action_payload["action_positions"] = positions
    action = SilverAction.model_validate(action_payload)
    assert all(position in action.action_positions for position in positions)
    possession_payload = base_possession.model_dump()
    possession_payload["contributing_actions"] = (action,)
    possession = SilverPossession.model_validate(possession_payload)
    coverage = evidence_coverage(
        identity_count=1,
        action_count=1,
        coordinate_numerator=0,
        coordinate_denominator=1,
        possession_numerator=1,
        possession_denominator=1,
        temporal_count=7,
    )
    applicability = W04ApplicabilityAssessment(
        state=W04Applicability.RESEARCH_ONLY,
        reason_codes=("COORDINATE_EVIDENCE_INCOMPLETE",),
    )
    fact_payload = base_fact.model_dump()
    fact_payload.update(
        contributing_actions=(action,),
        contributing_possessions=(possession,),
        coordinate_known_action_count=0,
        coverage=coverage,
        applicability=applicability,
    )
    fact = SilverPlayerMatchFact.model_validate(fact_payload)
    assert fact.coordinate_known_action_count == 0
    forged_fact = fact.model_dump()
    forged_fact["coordinate_known_action_count"] = 1
    with pytest.raises(ValidationError, match="feature counts"):
        SilverPlayerMatchFact.model_validate(forged_fact)
    gold_payload = make_gold().model_dump()
    gold_payload.update(
        coverage=coverage,
        applicability=applicability,
        contributing_player_match_facts=(fact,),
        contributing_player_match_keys=(fact.primary_key,),
    )
    gold_payload["features"]["coordinate_known_action_count"] = 0
    gold = GoldPlayerWindow.model_validate(gold_payload)
    assert gold.features.coordinate_known_action_count == 0


def test_r4_singleton_and_period_end_contested_action_remain_unassigned() -> None:
    *_, base_action, _, base_possession, base_fact = make_silver_rows()
    payload = action_payload_with_sequence_updates(
        base_action,
        action_event_taxonomy_id=1,
        action_subevent_taxonomy_id=10,
    )
    payload["possession_predicate_state"] = PossessionPredicateState.PREDICATE_ADMITTED
    payload["possession_eligibility_state"] = PossessionEligibilityState.INELIGIBLE_UNMAPPED
    contested = SilverAction.model_validate(payload)
    forged = contested.model_dump()
    forged["possession_eligibility_state"] = PossessionEligibilityState.ELIGIBLE_RESOLVED
    with pytest.raises(ValidationError, match="complete same-period sequence"):
        SilverAction.model_validate(forged)
    possession_payload = base_possession.model_dump()
    possession_payload.update(
        contributing_actions=(contested,),
        action_ids=(contested.action_id,),
    )
    with pytest.raises(ValidationError, match="complete resolved sequence group"):
        SilverPossession.model_validate(possession_payload)
    coverage = evidence_coverage(
        identity_count=1,
        action_count=1,
        coordinate_numerator=1,
        coordinate_denominator=1,
        possession_numerator=0,
        possession_denominator=1,
        temporal_count=7,
    )
    fact_payload = base_fact.model_dump()
    fact_payload.update(
        contributing_actions=(contested,),
        contributing_possessions=(),
        resolved_possession_action_count=0,
        coverage=coverage,
        applicability=W04ApplicabilityAssessment(
            state=W04Applicability.RESEARCH_ONLY,
            reason_codes=("POSSESSION_EVIDENCE_INCOMPLETE",),
        ),
    )
    assert SilverPlayerMatchFact.model_validate(fact_payload).resolved_possession_action_count == 0


def test_r4_contested_attaches_only_to_exact_following_resolved_control() -> None:
    sequence, actions, possession, fact = make_following_control_evidence()
    assert sequence.period_action_count == 2
    assert tuple(action.possession_eligibility_state for action in actions) == (
        PossessionEligibilityState.ELIGIBLE_RESOLVED,
        PossessionEligibilityState.ELIGIBLE_RESOLVED,
    )
    assert possession.action_ids == tuple(action.action_id for action in actions)
    assert fact.resolved_possession_action_count == 2


def test_r4_duplicate_incomplete_and_same_team_subset_period_evidence_fail_closed() -> None:
    sequence, actions, possession, _ = make_following_control_evidence()
    incomplete = sequence.model_dump()
    incomplete["actions"] = (incomplete["actions"][0],)
    with pytest.raises(ValidationError, match="cardinality"):
        PossessionPeriodSequence.model_validate(incomplete)
    duplicate = sequence.model_dump()
    duplicate["actions"] = (duplicate["actions"][0], duplicate["actions"][0])
    with pytest.raises(ValidationError, match="unique canonical order|unique action"):
        PossessionPeriodSequence.model_validate(duplicate)
    subset = possession.model_dump()
    subset.update(
        source_rows=actions[1].source_rows,
        contributing_actions=(actions[1],),
        action_ids=(actions[1].action_id,),
        first_action_order=actions[1].action_order_key,
        last_action_order=actions[1].action_order_key,
    )
    with pytest.raises(ValidationError, match="complete resolved sequence group"):
        SilverPossession.model_validate(subset)


@pytest.mark.parametrize("scope_field", ("match_id", "action_period_code"))
def test_r4_complete_period_sequence_rejects_cross_match_or_period_leakage(
    scope_field: str,
) -> None:
    sequence, *_ = make_following_control_evidence()
    payload = sequence.model_dump()
    entries = [dict(entry) for entry in payload["actions"]]
    entries[1][scope_field] = UUID(int=1) if scope_field == "match_id" else "2H"
    payload["actions"] = tuple(entries)
    with pytest.raises(ValidationError, match="cannot cross match or period"):
        PossessionPeriodSequence.model_validate(payload)


def test_r4_resolved_possession_count_cannot_drift_from_complete_membership() -> None:
    *_, fact = make_following_control_evidence()
    payload = fact.model_dump()
    payload["resolved_possession_action_count"] = 1
    with pytest.raises(ValidationError, match="feature counts"):
        SilverPlayerMatchFact.model_validate(payload)


def _equal_clock_sequence(
    specifications: tuple[tuple[int, UUID, int, int, Decimal], ...],
) -> PossessionPeriodSequence:
    *_, base_action, _, _, _ = make_silver_rows()
    entries = tuple(
        PossessionSequenceAction(
            action_id=canonical_source_uuid(SourceRecordKind.ACTION, source_id),
            source_event_record_id=source_id,
            source_row=WyscoutSourceRowReference(
                source_manifest_id=SOURCE_MANIFEST_ID,
                completion_relative_path=SOURCE_ROWS[0][0],
                source_sha256=SOURCE_ROWS[0][2],
                source_record_ordinal=ordinal,
                record_kind=SourceRecordKind.ACTION,
                raw_record_sha256=f"{source_id % 10}" * 64,
            ),
            match_id=base_action.match_id,
            player_id=base_action.player_id,
            team_id=team_id,
            action_event_taxonomy_id=event_id,
            action_subevent_taxonomy_id=subevent_id,
            action_period_code="1H",
            period_rank=1,
            period_elapsed_seconds=event_second,
            source_record_ordinal=ordinal,
            action_tag_ids=(),
        )
        for ordinal, (source_id, team_id, event_id, subevent_id, event_second) in enumerate(
            specifications
        )
    )
    return PossessionPeriodSequence(
        match_id=base_action.match_id,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        source_completion_membership_sha256="9" * 64,
        action_period_code="1H",
        period_action_count=len(entries),
        actions=entries,
    )


def test_equal_clock_opposing_control_is_group_first_and_wholly_unassigned() -> None:
    team_a = canonical_source_uuid(SourceRecordKind.TEAM, 2)
    team_b = canonical_source_uuid(SourceRecordKind.TEAM, 22)
    sequence = _equal_clock_sequence(
        (
            (5, team_a, 7, 70, Decimal("10.000")),
            (6, team_b, 7, 70, Decimal("10.000")),
        )
    )
    assert wyscout_contract._resolved_possession_groups(sequence) == ()


def test_equal_clock_ambiguity_does_not_erase_strictly_preexisting_possession() -> None:
    team_a = canonical_source_uuid(SourceRecordKind.TEAM, 2)
    team_b = canonical_source_uuid(SourceRecordKind.TEAM, 22)
    sequence = _equal_clock_sequence(
        (
            (5, team_a, 7, 70, Decimal("9.000")),
            (6, team_a, 7, 70, Decimal("10.000")),
            (7, team_b, 7, 70, Decimal("10.000")),
        )
    )
    assert wyscout_contract._resolved_possession_groups(sequence) == (
        (team_a, (canonical_source_uuid(SourceRecordKind.ACTION, 5),)),
    )


def test_equal_clock_ambiguity_discards_dependent_contested_buffer() -> None:
    team_a = canonical_source_uuid(SourceRecordKind.TEAM, 2)
    team_b = canonical_source_uuid(SourceRecordKind.TEAM, 22)
    sequence = _equal_clock_sequence(
        (
            (5, team_a, 1, 10, Decimal("9.000")),
            (6, team_a, 7, 70, Decimal("10.000")),
            (7, team_b, 7, 70, Decimal("10.000")),
        )
    )
    assert wyscout_contract._resolved_possession_groups(sequence) == ()


def test_possession_fact_and_gold_provenance_cover_other_player_causal_action() -> None:
    sequence, actions, possession, _ = make_following_control_evidence()
    other_player_id = canonical_source_uuid(SourceRecordKind.PLAYER, 33)
    sequence_payload = sequence.model_dump()
    sequence_entries = [dict(entry) for entry in sequence_payload["actions"]]
    sequence_entries[1]["player_id"] = other_player_id
    sequence_payload["actions"] = tuple(sequence_entries)
    cross_player_sequence = PossessionPeriodSequence.model_validate(sequence_payload)
    first_payload = actions[0].model_dump()
    first_payload["possession_period_sequence"] = cross_player_sequence
    first = SilverAction.model_validate(first_payload)
    second_payload = actions[1].model_dump()
    second_payload.update(
        player_id=other_player_id,
        possession_period_sequence=cross_player_sequence,
    )
    second = SilverAction.model_validate(second_payload)
    possession_payload = possession.model_dump()
    possession_payload["contributing_actions"] = (first, second)
    cross_player_possession = SilverPossession.model_validate(possession_payload)
    assert cross_player_possession.source_rows == tuple(
        entry.source_row for entry in cross_player_sequence.actions
    )

    base_fact = make_silver_rows()[-1]
    fact_payload = base_fact.model_dump()
    fact_payload.update(
        lineage=first.lineage,
        source_rows=cross_player_possession.source_rows,
        contributing_actions=(first,),
        contributing_possessions=(cross_player_possession,),
    )
    fact = SilverPlayerMatchFact.model_validate(fact_payload)
    assert second.source_rows[0] in fact.source_rows
    forged = fact.model_dump()
    forged["source_rows"] = first.source_rows
    with pytest.raises(ValidationError, match="causal contributing evidence"):
        SilverPlayerMatchFact.model_validate(forged)

    gold_payload = make_gold().model_dump()
    gold_payload.update(
        lineage=fact.lineage,
        source_rows=fact.source_rows,
        contributing_player_match_facts=(fact,),
        contributing_player_match_keys=(fact.primary_key,),
    )
    gold = GoldPlayerWindow.model_validate(gold_payload)
    assert second.source_rows[0] in gold.source_rows


def test_completion_index_digest_is_dependency_hashed_and_cannot_drift_at_boundaries() -> None:
    dependencies = make_dependencies()
    assert dependency_lineage_hash(
        dependencies,
        source_completion_index_sha256="f" * 64,
    ) != dependency_lineage_hash(dependencies)

    lineage_payload = make_lineage().model_dump()
    lineage_payload["source_completion_index_sha256"] = "f" * 64
    with pytest.raises(ValidationError, match="completion index"):
        WyscoutRowLineage.model_validate(lineage_payload)

    proof_payload = make_temporal_proof().model_dump()
    proof_payload["source_completion_index_sha256"] = "f" * 64
    with pytest.raises(ValidationError, match="completion index"):
        W04SemanticTemporalProof.model_validate(proof_payload)

    sequence_payload = make_silver_rows()[4].possession_period_sequence.model_dump()
    sequence_payload["source_completion_index_sha256"] = "f" * 64
    with pytest.raises(ValidationError, match="completion index"):
        PossessionPeriodSequence.model_validate(sequence_payload)

    for row in (make_silver_rows()[6], make_silver_rows()[7], make_gold()):
        payload = row.model_dump()
        payload["source_completion_index_sha256"] = "f" * 64
        with pytest.raises(ValidationError, match="completion index"):
            type(row).model_validate(payload)


def test_direct_and_dump_copied_product_models_are_semantic_only_not_checked() -> None:
    rows = make_silver_rows()
    gold = make_gold()
    assert all(
        row.construction_authority_state == "semantic_only_unchecked" for row in (*rows, gold)
    )
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="type is not authentic"):
        completion_index.require_checked_product(gold, expected_type=GoldPlayerWindow)
    copied_gold = GoldPlayerWindow.model_validate(gold.model_dump())
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="type is not authentic"):
        completion_index.require_checked_product(copied_gold, expected_type=GoldPlayerWindow)
    with pytest.raises(TypeError, match="issued only"):
        completion_index.CheckedProduct[GoldPlayerWindow]()
    substituted = object.__new__(completion_index.CheckedProduct)
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="not issued"):
        completion_index.require_checked_product(substituted, expected_type=GoldPlayerWindow)


def test_introspected_product_issuer_cannot_reissue_detached_raw_value() -> None:
    public_issue = _closure_value(completion_index.build_checked_gold_player_window, "issue")
    registry_issuer = cast(
        completion_index._IssueProduct,
        _closure_value(public_issue, "issuer"),
    )
    detached = registry_issuer(
        completion_index._CheckedProductRecord(
            construction_kind="gold_player_window",
            value=make_gold(),
            completions=(),
            payload_items=(),
        )
    )
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="graph is malformed"):
        completion_index.require_checked_product(detached, expected_type=GoldPlayerWindow)


def test_product_registry_insertion_fails_for_malformed_records_and_cycles() -> None:
    registry = cast(
        Any,
        _closure_value(completion_index._get_checked_product, "product_records"),
    )
    malformed = object.__new__(completion_index.CheckedProduct)
    registry[malformed] = make_gold()
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="record is malformed"):
        completion_index.require_checked_product(malformed, expected_type=GoldPlayerWindow)

    cyclic = object.__new__(completion_index.CheckedProduct)
    registry[cyclic] = completion_index._CheckedProductRecord(
        construction_kind="gold_player_window",
        value=make_gold(),
        completions=(),
        payload_items=(),
        fact_dependencies=(cast(Any, cyclic),),
    )
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="contains a cycle"):
        completion_index.require_checked_product(cyclic, expected_type=GoldPlayerWindow)


def test_copied_real_membership_digest_direct_gold_remains_unchecked() -> None:
    *_, base_action, _, base_possession, base_fact = make_silver_rows()
    sequence_payload = base_action.possession_period_sequence.model_dump()
    sequence_payload["source_completion_membership_sha256"] = (
        "473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b"
    )
    copied_digest_sequence = PossessionPeriodSequence.model_validate(sequence_payload)
    action_payload = base_action.model_dump()
    action_payload["possession_period_sequence"] = copied_digest_sequence
    action = SilverAction.model_validate(action_payload)
    possession_payload = base_possession.model_dump()
    possession_payload["contributing_actions"] = (action,)
    possession = SilverPossession.model_validate(possession_payload)
    fact_payload = base_fact.model_dump()
    fact_payload.update(
        contributing_actions=(action,),
        contributing_possessions=(possession,),
    )
    fact = SilverPlayerMatchFact.model_validate(fact_payload)
    gold_payload = make_gold().model_dump()
    gold_payload.update(
        contributing_player_match_facts=(fact,),
        contributing_player_match_keys=(fact.primary_key,),
    )
    gold = GoldPlayerWindow.model_validate(gold_payload)
    assert gold.contributing_player_match_facts[0].contributing_actions[
        0
    ].possession_period_sequence.source_completion_membership_sha256 == (
        "473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b"
    )
    assert gold.construction_authority_state == "semantic_only_unchecked"
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="type is not authentic"):
        completion_index.require_checked_product(gold, expected_type=GoldPlayerWindow)


def test_fail_fast_completion_reader_makes_checked_gold_bypass_impossible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    index = completion_index.load_source_completion_index(
        manifest_root=Path("data/manifests"),
        index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
    )
    reader_calls: list[str] = []

    def fail_fast(*_args: object, **_kwargs: object) -> None:
        reader_calls.append("called")
        raise completion_index.WyscoutCompletionIndexError("reader fail-fast")

    for name in (
        "load_source_completion_index",
        "validate_index",
        "validate_match_period_population",
        "validate_match_population",
        "build_possession_period_sequence",
        "build_match_period_sequences",
    ):
        monkeypatch.setattr(completion_index, name, fail_fast)
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="reader fail-fast"):
        completion_index.validate_checked_match_population(index=index, actions=())
    assert reader_calls == ["called"]

    direct_gold = make_gold()
    assert direct_gold.construction_authority_state == "semantic_only_unchecked"
    with pytest.raises(completion_index.WyscoutCompletionIndexError, match="type is not authentic"):
        completion_index.require_checked_product(direct_gold, expected_type=GoldPlayerWindow)


def test_real_match_checked_path_reaches_gold_and_exact_scoped_manifest(
    real_checked_match_population: tuple[
        completion_index.SourceCompletionIndex,
        tuple[completion_index.CompletionActionEvidence, ...],
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    index, population = real_checked_match_population
    checked_match = completion_index.validate_checked_match_population(
        index=index,
        actions=population,
    )
    sequences = checked_match.sequences
    entries = tuple(entry for sequence in sequences for entry in sequence.actions)
    evidence_by_ordinal = {action.source_record_ordinal: action for action in population}
    resolved_groups = tuple(
        (sequence, team_id, action_ids)
        for sequence in sequences
        for team_id, action_ids in wyscout_contract._resolved_possession_groups(sequence)
    )
    resolved_action_ids = {
        action_id for _sequence, _team_id, action_ids in resolved_groups for action_id in action_ids
    }
    entries_by_player: dict[UUID, list[PossessionSequenceAction]] = {}
    for entry in entries:
        if entry.player_id is not None and entry.team_id is not None:
            entries_by_player.setdefault(entry.player_id, []).append(entry)
    eligible_players = tuple(
        player_id
        for player_id, player_entries in entries_by_player.items()
        if {entry.action_id for entry in player_entries} <= resolved_action_ids
        and len({entry.team_id for entry in player_entries}) == 1
    )
    target_player = min(
        eligible_players,
        key=lambda player_id: (len(entries_by_player[player_id]), player_id.bytes),
    )
    target_entries = tuple(entries_by_player[target_player])
    target_action_ids = {entry.action_id for entry in target_entries}
    target_groups = tuple(
        group for group in resolved_groups if target_action_ids.intersection(group[2])
    )
    required_action_ids = target_action_ids | {
        action_id for _sequence, _team_id, action_ids in target_groups for action_id in action_ids
    }

    base_lineage = make_lineage()
    lineage_payload = base_lineage.model_dump()
    lineage_payload["source_rows"] = tuple(
        sorted(
            (
                *(
                    row
                    for row in base_lineage.source_rows
                    if row.record_kind is not SourceRecordKind.ACTION
                ),
                *(entry.source_row for entry in entries),
            ),
            key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
        )
    )
    lineage = WyscoutRowLineage.model_validate(lineage_payload)
    entry_by_action_id = {entry.action_id: entry for entry in entries}
    checked_actions: dict[UUID, completion_index.CheckedProduct[SilverAction]] = {}
    for action_id in required_action_ids:
        entry = entry_by_action_id[action_id]
        checked_actions[action_id] = completion_index.build_checked_silver_action(
            completion=checked_match,
            payload=_real_checked_action_payload(
                evidence=evidence_by_ordinal[entry.source_record_ordinal],
                entry=entry,
                lineage=lineage,
                resolved_action_ids=resolved_action_ids,
            ),
        )
    checked_possessions_by_id: list[
        tuple[UUID, completion_index.CheckedProduct[SilverPossession]]
    ] = []
    for sequence, team_id, action_ids in target_groups:
        possession_id = uuid5(
            sequence.match_id,
            f"checked:{sequence.action_period_code}:{action_ids[0]}",
        )
        checked_possessions_by_id.append(
            (
                possession_id,
                completion_index.build_checked_silver_possession(
                    completion=checked_match,
                    payload={
                        "build_id": BUILD_ID,
                        "tenant_context": tenant(),
                        "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
                        "lineage": lineage,
                        "possession_id": possession_id,
                        "match_id": sequence.match_id,
                        "action_period_code": sequence.action_period_code,
                        "team_id": team_id,
                    },
                    contributing_actions=tuple(
                        checked_actions[action_id] for action_id in action_ids
                    ),
                ),
            )
        )
    checked_possessions = tuple(
        possession
        for _possession_id, possession in sorted(
            checked_possessions_by_id,
            key=lambda item: item[0].bytes,
        )
    )
    target_checked_actions = tuple(
        checked_actions[entry.action_id]
        for entry in sorted(
            target_entries,
            key=lambda entry: entry.action_order_key,
        )
    )
    target_team = target_entries[0].team_id
    if target_team is None:
        raise AssertionError("selected checked player must retain a source team")
    action_count = len(target_checked_actions)
    fact_coverage = evidence_coverage(
        identity_count=action_count,
        action_count=action_count,
        coordinate_numerator=0,
        coordinate_denominator=0,
        possession_numerator=action_count,
        possession_denominator=action_count,
        temporal_count=6 + action_count,
    )
    temporal_proof = make_temporal_proof()
    checked_fact = completion_index.build_checked_silver_player_match_fact(
        completion=checked_match,
        payload={
            "build_id": BUILD_ID,
            "tenant_context": tenant(),
            "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
            "lineage": lineage,
            "source_manifest_id": SOURCE_MANIFEST_ID,
            "match_id": sequences[0].match_id,
            "player_id": target_player,
            "competition_id": canonical_source_uuid(SourceRecordKind.COMPETITION, 1),
            "season_id": SEASON_ID,
            "match_start_utc": datetime(2018, 6, 1, 12, tzinfo=UTC),
            "match_team_id": target_team,
            "action_count": action_count,
            "coordinate_known_action_count": 0,
            "resolved_possession_action_count": action_count,
            "right_censored_or_uncertain": False,
            "coverage": fact_coverage,
            "applicability": data_ready(),
            "temporal_proof": temporal_proof,
        },
        contributing_lineup_stints=(),
        contributing_actions=target_checked_actions,
        contributing_possessions=checked_possessions,
    )
    checked_gold = completion_index.build_checked_gold_player_window(
        payload={
            "build_id": BUILD_ID,
            "tenant_context": tenant(),
            "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
            "lineage": lineage,
            "player_id": target_player,
            "competition_id": canonical_source_uuid(SourceRecordKind.COMPETITION, 1),
            "season_id": SEASON_ID,
            "role_context_id": ROLE_CONTEXT_ID,
            "role_context_version": ROLE_CONTEXT_VERSION,
            "role_context_state": ROLE_CONTEXT_STATE,
            "window_definition_id": WINDOW_ID,
            "window_start_utc": WINDOW_START,
            "window_end_utc": WINDOW_END,
            "feature_cutoff_ts": CUTOFF,
            "dependency_lineage_hash": temporal_proof.dependency_lineage_hash,
            "feature_schema_hash": FEATURE_SCHEMA_HASH,
            "temporal_proof": temporal_proof,
            "coverage": fact_coverage,
            "applicability": data_ready(),
            "features": GoldFeatureValues(
                action_count=action_count,
                coordinate_known_action_count=0,
                match_count=1,
                resolved_possession_action_count=action_count,
            ),
        },
        contributing_player_match_facts=(checked_fact,),
    )
    gold = completion_index.require_checked_product(
        checked_gold,
        expected_type=GoldPlayerWindow,
    )
    assert gold.features == GoldFeatureValues(
        action_count=2,
        coordinate_known_action_count=0,
        match_count=1,
        resolved_possession_action_count=2,
    )

    paths = {path.path_role: path for path in valid_paths()}
    raw_gold_manifest = LayerManifest(
        layer=Layer.GOLD,
        build_id=BUILD_ID,
        manifest_path=paths[ProductPathRole.GOLD_MANIFEST],
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        tenant_context=tenant(),
        classification=restricted_rights(),
        source_available_at=SOURCE_RELEASE,
        source_acquired_at=accepted_source_authority().acquired_at,
        authority_clocks=accepted_authority_clocks(),
        feature_schema_hash=FEATURE_SCHEMA_HASH,
        dependency_lineage_hash=make_dependency_lineage().lineage_hash,
        dependency_lineage=make_dependency_lineage(),
        entries=(
            manifest_entry(
                paths[ProductPathRole.GOLD_PLAYER_WINDOW],
                "gold.py",
                (paths[ProductPathRole.SILVER_PLAYER_MATCH_FACT].relative_path,),
            ),
        ),
        parent_layer_manifests=(
            ParentLayerManifest(
                layer=Layer.SILVER,
                build_id=BUILD_ID,
                relative_path=paths[ProductPathRole.SILVER_MANIFEST].relative_path,
                sha256=SEMANTIC_DIGEST,
            ),
        ),
    )
    checked_manifest = completion_index.build_checked_layer_manifest(
        payload=raw_gold_manifest.model_dump(),
        completions=(checked_match,),
        contributing_products=(checked_gold,),
    )
    completion_verifications = 0
    exact_completion_verifier = completion_index._verify_completion_evidence

    def counted_completion_verifier(
        record: completion_index._CheckedCompletionRecord,
    ) -> completion_index._VerifiedCompletionRecord:
        nonlocal completion_verifications
        completion_verifications += 1
        return exact_completion_verifier(record)

    monkeypatch.setattr(
        completion_index,
        "_verify_completion_evidence",
        counted_completion_verifier,
    )
    assert (
        completion_index.require_checked_product(
            checked_manifest,
            expected_type=LayerManifest,
        ).layer
        is Layer.GOLD
    )
    assert completion_verifications == 1
    with pytest.raises(TypeError, match="cannot be copied"):
        copy(checked_gold)
    with pytest.raises(TypeError, match="cannot be copied"):
        deepcopy(checked_gold)
    with pytest.raises(TypeError, match="cannot be serialized"):
        pickle.dumps(checked_gold)

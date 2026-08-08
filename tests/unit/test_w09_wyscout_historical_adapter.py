from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest

from scouting.contracts.wyscout_identity import WyscoutIdentityEntityKind
from scouting.sources import wyscout_historical as historical_source
from scouting.sources.wyscout_historical import (
    ADMITTED_PARTITIONS,
    EMPTY_SUB_EVENT_ID_SENTINEL_COUNT,
    EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS,
    RIGHTS_CLASSIFICATION,
    SOURCE_ACTION_COUNT,
    SOURCE_MATCH_COUNT,
    SOURCE_PLAYER_COUNT,
    SOURCE_TEAM_COUNT,
    HistoricalIdentityAuthority,
    HistoricalPartition,
    WyscoutHistoricalAdapter,
    WyscoutHistoricalError,
    WyscoutHistoricalPathError,
)


def _canonical(kind: str, source_id: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"w09-test:{kind}:{source_id}"))


def _fixture_adapter(
    *,
    duplicate_action: bool = False,
    sub_event_ids: tuple[object, object] = (85, 85),
) -> WyscoutHistoricalAdapter:
    partition = HistoricalPartition(
        name="Fixture",
        match_relative_path="archive-members/matches_Fixture.json",
        match_sha256="1" * 64,
        match_count=1,
        action_relative_path="archive-members/events_Fixture.json",
        action_sha256="2" * 64,
        action_count=2,
    )
    identity = HistoricalIdentityAuthority(
        resolved={
            WyscoutIdentityEntityKind.COMPETITION: {100: _canonical("competition", 100)},
            WyscoutIdentityEntityKind.TEAM: {
                10: _canonical("team", 10),
                20: _canonical("team", 20),
            },
            WyscoutIdentityEntityKind.PLAYER: {1: _canonical("player", 1)},
            WyscoutIdentityEntityKind.MATCH: {1000: _canonical("match", 1000)},
        },
        unresolved_player_source_ids=frozenset({999}),
        rejected_player_source_ids=frozenset({0}),
        player_source_reference_counts={999: 1, 0: 1},
        bundle_sha256="3" * 64,
        available_at=datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC),
    )
    match = {
        "wyId": 1000,
        "competitionId": 100,
        "seasonId": 200,
        "dateutc": "2018-01-01 12:00:00",
        "duration": "Regular",
        "status": "Played",
        "label": "A - B, 0 - 0",
        "venue": "Ground",
        "teamsData": {
            "10": {"teamId": 10, "hasFormation": 0},
            "20": {"teamId": 20, "hasFormation": 0},
        },
    }
    actions = [
        {
            "id": 500,
            "matchId": 1000,
            "playerId": 1,
            "teamId": 10,
            "eventId": 8,
            "eventName": "Pass",
            "subEventId": sub_event_ids[0],
            "subEventName": "Simple pass",
            "matchPeriod": "1H",
            "eventSec": 10,
            "tags": [],
            "positions": [{"x": 20, "y": 30}, {"x": 40, "y": 30}],
        },
        {
            "id": 500 if duplicate_action else 501,
            "matchId": 1000,
            "playerId": 0,
            "teamId": 20,
            "eventId": 8,
            "eventName": "Pass",
            "subEventId": sub_event_ids[1],
            "subEventName": "Simple pass",
            "matchPeriod": "2H",
            "eventSec": 10,
            "tags": [],
            "positions": [{"x": 80, "y": 70}, {"x": 60, "y": 70}],
        },
    ]
    return WyscoutHistoricalAdapter.from_test_fixture(
        catalogues={
            "competitions": [{"wyId": 100, "name": "Fixture League"}],
            "teams": [
                {"wyId": 10, "name": "A"},
                {"wyId": 20, "name": "B"},
            ],
            "players": [
                {
                    "wyId": 1,
                    "shortName": "Player One",
                    "role": {"code2": "DF"},
                }
            ],
        },
        matches={"Fixture": [match]},
        actions={"Fixture": actions},
        identity=identity,
        partitions=[partition],
    )


def test_retained_authority_declares_exact_recorded_universe() -> None:
    assert len(ADMITTED_PARTITIONS) == 5
    assert sum(partition.match_count for partition in ADMITTED_PARTITIONS) == SOURCE_MATCH_COUNT
    assert sum(partition.action_count for partition in ADMITTED_PARTITIONS) == SOURCE_ACTION_COUNT
    assert SOURCE_TEAM_COUNT == 142
    assert SOURCE_PLAYER_COUNT == 3_603
    assert RIGHTS_CLASSIFICATION == "wyscout_figshare_v5_cc_by_4"
    assert EMPTY_SUB_EVENT_ID_SENTINEL_COUNT == 7_821
    assert EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS == {
        "England": 1_558,
        "France": 1_543,
        "Germany": 1_219,
        "Italy": 1_620,
        "Spain": 1_881,
    }
    paths = {
        path
        for partition in ADMITTED_PARTITIONS
        for path in (partition.match_relative_path, partition.action_relative_path)
    }
    assert len(paths) == 10
    assert all("*" not in path and not path.endswith(".manifest.json") for path in paths)


def test_fixture_rows_are_unavailable_until_authorities_are_verified() -> None:
    adapter = _fixture_adapter()
    with pytest.raises(WyscoutHistoricalError, match="verified"):
        adapter.load_catalogue("players")
    adapter.verify()
    batches = list(adapter.iter_partition_action_batches(adapter.partitions[0], batch_size=1))
    assert [batch.to_pylist()[0]["source_record_ordinal"] for batch in batches] == [0, 1]
    assert adapter.identity.canonical_id(WyscoutIdentityEntityKind.PLAYER, 999) is None
    assert adapter.identity.canonical_id(WyscoutIdentityEntityKind.PLAYER, 0) is None


def test_optional_sub_event_id_empty_sentinel_and_integer_share_int_or_null_contract() -> None:
    adapter = _fixture_adapter(sub_event_ids=("", 85)).verify()
    rows = [
        row
        for batch in adapter.iter_partition_action_batches(adapter.partitions[0], batch_size=1)
        for row in batch.to_pylist()
    ]
    assert [row["subEventId"] for row in rows] == [None, 85]
    assert [row["adapter_sub_event_id_was_empty_string"] for row in rows] == [True, False]


@pytest.mark.parametrize("invalid", ["85", " ", True, 85.0, "not-an-id"])
def test_optional_sub_event_id_rejects_every_other_source_type(invalid: object) -> None:
    adapter = _fixture_adapter(sub_event_ids=(invalid, 85)).verify()
    with pytest.raises(WyscoutHistoricalError, match="strict integer, null, or the exact empty"):
        list(adapter.iter_partition_action_batches(adapter.partitions[0]))


def test_population_audit_reconciles_partition_and_zero_actor() -> None:
    audit = _fixture_adapter().verify().audit_action_population()
    assert audit.action_count == audit.unique_action_count == 2
    assert audit.zero_actor_action_count == 1
    assert audit.match_ids_by_partition == {"Fixture": frozenset({1000})}


def test_duplicate_action_identity_fails_closed() -> None:
    with pytest.raises(WyscoutHistoricalError, match="duplicated"):
        _fixture_adapter(duplicate_action=True).verify().audit_action_population()


def test_production_adapter_rejects_alternate_roots_before_reading(tmp_path: Path) -> None:
    adapter = WyscoutHistoricalAdapter(
        source_root=tmp_path / "source",
        manifest_root=tmp_path / "manifests",
        identity_root=tmp_path / "identity",
    )
    with pytest.raises(WyscoutHistoricalPathError, match="exact retained roots"):
        adapter.verify()


def test_action_fingerprint_rejects_change_after_authority_binding(tmp_path: Path) -> None:
    action_path = tmp_path / "events_Fixture.json"
    action_path.write_bytes(b"[]")
    fingerprint = historical_source._regular_file_fingerprint(action_path)
    action_path.write_bytes(b"[{}]")
    with pytest.raises(WyscoutHistoricalError, match="changed after authority verification"):
        historical_source._require_unchanged_regular_file(action_path, fingerprint)

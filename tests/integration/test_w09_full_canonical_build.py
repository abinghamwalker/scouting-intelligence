from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pyarrow.parquet as pq  # type: ignore[import-untyped]
import pytest

from scouting.contracts.wyscout_identity import WyscoutIdentityEntityKind
from scouting.data_products.wyscout import historical as historical_product
from scouting.data_products.wyscout.historical import (
    HistoricalCanonicalBuildError,
    audit_historical_action_projection,
    audit_historical_appearance_projection,
    build_historical_canonical,
)
from scouting.sources.wyscout_historical import (
    HistoricalIdentityAuthority,
    HistoricalPartition,
    WyscoutHistoricalAdapter,
    WyscoutHistoricalError,
)


def _canonical(kind: str, source_id: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"w09-integration:{kind}:{source_id}"))


def _player(source_id: int, position: str) -> dict[str, object]:
    return {
        "wyId": source_id,
        "shortName": f"Real Fixture Player {source_id}",
        "firstName": "Real",
        "middleName": "",
        "lastName": f"Player {source_id}",
        "birthDate": "1990-01-01",
        "role": {"code2": position},
        "foot": "right",
        "height": 180,
        "weight": 75,
        # This deliberately wrong contemporary value must never reach membership output.
        "currentTeamId": 999_999,
    }


def _action(
    action_id: int,
    *,
    player_id: int,
    team_id: int,
    period: str,
    seconds: int,
    tags: list[int] | None = None,
    sub_event_id: object = 85,
    positions: object = None,
) -> dict[str, object]:
    return {
        "id": action_id,
        "matchId": 1000,
        "playerId": player_id,
        "teamId": team_id,
        "eventId": 8,
        "eventName": "Pass",
        "subEventId": sub_event_id,
        "subEventName": "Simple pass",
        "matchPeriod": period,
        "eventSec": seconds,
        "tags": [{"id": value} for value in (tags or [])],
        "positions": ([{"x": 10, "y": 20}, {"x": 30, "y": 40}] if positions is None else positions),
    }


def _adapter(
    *,
    duplicate_actions: bool = False,
    substitutions_unavailable: bool = False,
    zero_player_in_substitutions: bool = False,
    substitution_minute: int = 60,
    identity_available_at: datetime = datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC),
) -> WyscoutHistoricalAdapter:
    actions = [
        _action(
            500,
            player_id=1,
            team_id=10,
            period="1H",
            seconds=600,
            sub_event_id="",
            positions=[{"x": 10, "y": 20}, {"x": 30, "y": 101}],
        ),
        _action(501, player_id=4, team_id=20, period="2H", seconds=1500, tags=[1701]),
        _action(
            501 if duplicate_actions else 502,
            player_id=0,
            team_id=20,
            period="2H",
            seconds=2700,
            positions=[],
        ),
    ]
    partition = HistoricalPartition(
        name="Fixture",
        match_relative_path="archive-members/matches_Fixture.json",
        match_sha256="1" * 64,
        match_count=1,
        action_relative_path="archive-members/events_Fixture.json",
        action_sha256="2" * 64,
        action_count=len(actions),
    )
    resolved_players = {source_id: _canonical("player", source_id) for source_id in range(1, 7)}
    identity = HistoricalIdentityAuthority(
        resolved={
            WyscoutIdentityEntityKind.COMPETITION: {100: _canonical("competition", 100)},
            WyscoutIdentityEntityKind.TEAM: {
                10: _canonical("team", 10),
                20: _canonical("team", 20),
            },
            WyscoutIdentityEntityKind.PLAYER: resolved_players,
            WyscoutIdentityEntityKind.MATCH: {1000: _canonical("match", 1000)},
        },
        unresolved_player_source_ids=frozenset({999}),
        rejected_player_source_ids=frozenset({0}),
        player_source_reference_counts={999: 1, 0: 2},
        bundle_sha256="3" * 64,
        available_at=identity_available_at,
    )
    match = {
        "wyId": 1000,
        "competitionId": 100,
        "seasonId": 200,
        "dateutc": "2018-01-01 12:00:00",
        "duration": "Regular",
        "status": "Played",
        "label": "Fixture A - Fixture B, 0 - 0",
        "venue": "Fixture Ground",
        "teamsData": {
            "10": {
                "teamId": 10,
                "hasFormation": 1,
                "formation": {
                    "lineup": [{"playerId": 1}, {"playerId": 2}],
                    "bench": [{"playerId": 3}, {"playerId": 999}],
                    "substitutions": [
                        {
                            "playerIn": 3,
                            "playerOut": 1,
                            "minute": substitution_minute,
                        }
                    ],
                },
            },
            "20": {
                "teamId": 20,
                "hasFormation": 1,
                "formation": {
                    "lineup": [{"playerId": 4}, {"playerId": 5}],
                    "bench": [{"playerId": 6}, {"playerId": 0}],
                    "substitutions": (
                        "null"
                        if substitutions_unavailable
                        else [
                            {"playerIn": 0, "playerOut": 4, "minute": 50},
                            {"playerIn": 0, "playerOut": 5, "minute": 60},
                        ]
                        if zero_player_in_substitutions
                        else []
                    ),
                },
            },
        },
    }
    return WyscoutHistoricalAdapter.from_test_fixture(
        catalogues={
            "competitions": [
                {
                    "wyId": 100,
                    "name": "Fixture League",
                    "area": {"name": "Fixtureland"},
                    "format": "Domestic league",
                    "type": "club",
                }
            ],
            "teams": [
                {
                    "wyId": 10,
                    "name": "Fixture A",
                    "officialName": "Fixture A FC",
                    "city": "A",
                    "area": {"name": "Fixtureland"},
                },
                {
                    "wyId": 20,
                    "name": "Fixture B",
                    "officialName": "Fixture B FC",
                    "city": "B",
                    "area": {"name": "Fixtureland"},
                },
            ],
            "players": [
                _player(1, "DF"),
                _player(2, "MD"),
                _player(3, "FW"),
                _player(4, "DF"),
                _player(5, "MD"),
                _player(6, "GK"),
            ],
        },
        matches={"Fixture": [match]},
        actions={"Fixture": actions},
        identity=identity,
        partitions=[partition],
    )


def _physical_path(root: Path, logical_path: str) -> Path:
    prefix = "data/working/wyscout/v5/research/"
    assert logical_path.startswith(prefix)
    return root / logical_path.removeprefix(prefix)


def test_small_fixture_build_is_deterministic_reconciled_and_preserves_w04(
    tmp_path: Path,
) -> None:
    w04_sentinel = tmp_path / "data/working/wyscout/v5/gold/w04-sentinel.parquet"
    w04_sentinel.parent.mkdir(parents=True)
    w04_sentinel.write_bytes(b"accepted-w04-proof")

    first_root = tmp_path / "first/research"
    second_root = tmp_path / "second/research"
    first = build_historical_canonical(
        adapter=_adapter(),
        research_root=first_root,
        research_manifest_root=tmp_path / "first/manifests",
    )
    second = build_historical_canonical(
        adapter=_adapter(),
        research_root=second_root,
        research_manifest_root=tmp_path / "second/manifests",
    )

    assert first.build_id == second.build_id
    assert first.manifest_sha256 == second.manifest_sha256
    assert [
        (artifact.role, artifact.relative_path, artifact.row_count, artifact.sha256)
        for artifact in first.artifacts
    ] == [
        (artifact.role, artifact.relative_path, artifact.row_count, artifact.sha256)
        for artifact in second.artifacts
    ]
    assert w04_sentinel.read_bytes() == b"accepted-w04-proof"
    assert first.manifest["test_fixture"] is True
    assert first.manifest["rights"] == {
        "classification": "wyscout_figshare_v5_cc_by_4",
        "attribution": (
            "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
            "Wyscout, figshare collection v5, licensed CC BY 4.0."
        ),
        "local_only": True,
        "raw_export_allowed": False,
    }
    assert first.manifest["canonical_counts"] == {
        "competitions": 1,
        "teams": 2,
        "players": 6,
        "matches": 1,
        "actions": 3,
        "appearances": 6,
        "identity_exclusions": 2,
    }
    assert first.manifest["optional_sub_event_id"] == {
        "adapter_contract": "strict_integer_or_null",
        "raw_empty_string_sentinel_normalized_to_null": True,
        "empty_string_sentinel_count": 1,
        "empty_string_sentinel_counts_by_partition": {"Fixture": 1},
    }
    coordinate_evidence = first.manifest["coordinate_evidence"]
    assert coordinate_evidence == {
        "states": ["valid", "absent", "invalid_out_of_range"],
        "raw_strict_integers_preserved": True,
        "clamped_nulled_or_dropped": False,
        "coordinate_independent_actions_retained": True,
        "coordinate_coverage_admits_only_state": "valid",
        "state_counts_by_partition": {
            "Fixture": {"absent": 1, "invalid_out_of_range": 1, "valid": 1}
        },
        "invalid_action_count": 1,
        "invalid_point_count": 1,
        "invalid_action_counts_by_partition": {"Fixture": 1},
        "invalid_actions": [
            {
                "source_partition": "Fixture",
                "source_action_id": 500,
                "invalid_points": [{"point_index": 1, "axis": "y", "raw_value": 101}],
            }
        ],
    }

    by_role = {artifact.role: artifact for artifact in first.artifacts}
    actions = (
        pq.ParquetFile(_physical_path(first_root, by_role["canonical_actions"].relative_path))
        .read()
        .to_pylist()
    )
    invalid_action = next(row for row in actions if row["source_action_id"] == 500)
    assert invalid_action["end_y"] == 101
    assert invalid_action["coordinate_evidence_state"] == "invalid_out_of_range"
    assert len(actions) == 3
    players = pq.read_table(_physical_path(first_root, by_role["canonical_players"].relative_path))
    assert "currentTeamId" not in players.schema.names
    appearances = pq.read_table(
        _physical_path(first_root, by_role["canonical_appearances"].relative_path)
    ).to_pylist()
    by_player = {row["source_player_id"]: row for row in appearances}
    assert (by_player[1]["minute_state"], by_player[1]["minutes"]) == ("exact", 60.0)
    assert (by_player[2]["minute_state"], by_player[2]["minutes"]) == (
        "conservative_lower_bound",
        90.0,
    )
    assert (by_player[3]["minute_state"], by_player[3]["minutes"]) == (
        "conservative_lower_bound",
        30.0,
    )
    assert (by_player[4]["minute_state"], by_player[4]["minutes"]) == ("exact", 70.0)
    assert by_player[6]["minute_state"] == "unusable"
    assert 0 not in by_player and 999 not in by_player

    exclusions = pq.read_table(
        _physical_path(first_root, by_role["identity_exclusions"].relative_path)
    ).to_pylist()
    assert {(row["source_player_id"], row["identity_state"]) for row in exclusions} == {
        (0, "rejected"),
        (999, "review_required"),
    }
    assert all(row["canonical_player_id"] is None for row in exclusions)
    manifest_bytes = (
        tmp_path / "first/manifests" / first.manifest_relative_path.rsplit("/", 1)[-1]
    ).read_bytes()
    assert json.loads(manifest_bytes)["canonical_build_id"] == first.build_id


def test_provider_unicode_escapes_are_normalised_once_in_canonical_text(
    tmp_path: Path,
) -> None:
    adapter = _adapter()
    fixture = adapter._fixture_data
    assert fixture is not None
    catalogues = deepcopy(fixture.catalogues)
    catalogues["players"][0]["shortName"] = r"\u0130. G\u00fcndo\u011fan"
    catalogues["players"][0]["firstName"] = r"\u0130lkay"
    catalogues["players"][0]["lastName"] = r"Gu\u0308ndo\u011fan"
    catalogues["players"][1]["shortName"] = "José Fixture"
    unicode_adapter = WyscoutHistoricalAdapter.from_test_fixture(
        catalogues=catalogues,
        matches=fixture.matches,
        actions=fixture.actions,
        identity=adapter._fixture_identity,
        partitions=adapter.partitions,
    )

    result = build_historical_canonical(
        adapter=unicode_adapter,
        research_root=tmp_path / "research",
        research_manifest_root=tmp_path / "manifests",
    )
    players_artifact = next(
        artifact for artifact in result.artifacts if artifact.role == "canonical_players"
    )
    players = pq.read_table(
        _physical_path(tmp_path / "research", players_artifact.relative_path)
    ).to_pylist()
    by_source_id = {row["source_player_id"]: row for row in players}

    assert by_source_id[1]["display_name"] == "İ. Gündoğan"
    assert by_source_id[1]["first_name"] == "İlkay"
    assert by_source_id[1]["last_name"] == "Gündoğan"
    assert by_source_id[2]["display_name"] == "José Fixture"
    assert all("\\u" not in row["display_name"] for row in players)


@pytest.mark.parametrize(
    "invalid_name, message",
    [
        (r"Broken \u12G4", "malformed Unicode escape"),
        (r"Broken \uD83D", "unpaired Unicode surrogate"),
        (r"Broken \uD83D\u0041", "invalid Unicode surrogate pair"),
        (r"Broken \u005cu00e9", "nested Unicode escape"),
        ("Broken \ud83d", "unpaired Unicode surrogate"),
        ("Broken \udc00", "unpaired Unicode surrogate"),
    ],
)
def test_invalid_provider_unicode_escapes_fail_before_artifact_writes(
    tmp_path: Path,
    invalid_name: str,
    message: str,
) -> None:
    adapter = _adapter()
    fixture = adapter._fixture_data
    assert fixture is not None
    catalogues = deepcopy(fixture.catalogues)
    catalogues["players"][0]["shortName"] = invalid_name
    invalid_adapter = WyscoutHistoricalAdapter.from_test_fixture(
        catalogues=catalogues,
        matches=fixture.matches,
        actions=fixture.actions,
        identity=adapter._fixture_identity,
        partitions=adapter.partitions,
    )
    research_root = tmp_path / "research"

    with pytest.raises(HistoricalCanonicalBuildError, match=message):
        build_historical_canonical(
            adapter=invalid_adapter,
            research_root=research_root,
            research_manifest_root=tmp_path / "manifests",
        )
    assert not research_root.exists()


def test_no_write_action_projection_traverses_fixture_and_reconciles_sentinel(
    tmp_path: Path,
) -> None:
    audit = audit_historical_action_projection(adapter=_adapter())
    assert audit.action_count == 3
    assert audit.empty_sub_event_id_sentinel_count == 1
    assert audit.empty_sub_event_id_sentinel_counts == {"Fixture": 1}
    assert audit.coordinate_evidence_state_counts == {
        "Fixture": {"absent": 1, "invalid_out_of_range": 1, "valid": 1}
    }
    assert audit.invalid_coordinate_action_count == 1
    assert audit.invalid_coordinate_point_count == 1
    assert list(tmp_path.iterdir()) == []


def test_exact_null_substitution_sentinel_is_conservative_and_audited(
    tmp_path: Path,
) -> None:
    result = build_historical_canonical(
        adapter=_adapter(substitutions_unavailable=True),
        research_root=tmp_path / "research",
        research_manifest_root=tmp_path / "manifests",
    )
    by_role = {artifact.role: artifact for artifact in result.artifacts}
    appearances = (
        pq.ParquetFile(
            _physical_path(
                tmp_path / "research",
                by_role["canonical_appearances"].relative_path,
            )
        )
        .read()
        .to_pylist()
    )
    by_player = {row["source_player_id"]: row for row in appearances}
    for source_player_id in (4, 5):
        row = by_player[source_player_id]
        assert row["lineup_role"] == "starter"
        assert row["minute_state"] == "conservative_lower_bound"
        assert row["minutes"] == row["start_minute"] == row["end_minute"] == 0.0
        assert row["evidence_basis"] == ("starting_lineup_with_unavailable_substitution_evidence")
    assert by_player[6]["lineup_role"] == "bench_entry_unknown"
    assert by_player[6]["minute_state"] == "unusable"
    assert by_player[6]["minutes"] is None
    assert result.manifest["substitution_evidence"] == {
        "states": ["available_array", "unavailable_exact_null_string_sentinel"],
        "accepted_unavailable_raw_value": "null",
        "arbitrary_shape_coercion": False,
        "unavailable_team_count": 1,
        "unavailable_team_counts_by_partition": {"Fixture": 1},
        "unavailable_teams": [
            {
                "source_partition": "Fixture",
                "source_match_id": 1000,
                "source_team_id": 20,
            }
        ],
        "zero_player_in_policy": (
            "exclude every rejected zero-entry occurrence while retaining its "
            "distinct nonzero playerOut exit boundary"
        ),
        "zero_player_in_occurrence_count": 0,
        "zero_player_in_occurrence_counts_by_partition": {"Fixture": 0},
        "zero_player_in_occurrences": [],
        "starter_policy": (
            "retain a conservative zero-minute lower bound from starting-lineup "
            "evidence without inferring an exit"
        ),
        "bench_policy": ("retain as unusable bench-entry-unknown evidence without inferring play"),
        "action_presence_used_for_minutes": False,
        "current_team_id_used_for_membership": False,
    }
    audit = audit_historical_appearance_projection(adapter=_adapter(substitutions_unavailable=True))
    assert audit.appearance_count == 6
    assert audit.substitution_unavailable_team_count == 1
    assert audit.substitution_unavailable_teams == {"Fixture": ((1000, 20),)}
    assert audit.zero_player_in_substitution_count == 0
    assert audit.zero_player_in_substitutions == {}


def test_repeated_zero_player_in_rows_retain_distinct_nonzero_exits(
    tmp_path: Path,
) -> None:
    result = build_historical_canonical(
        adapter=_adapter(zero_player_in_substitutions=True),
        research_root=tmp_path / "research",
        research_manifest_root=tmp_path / "manifests",
    )
    by_role = {artifact.role: artifact for artifact in result.artifacts}
    appearances = (
        pq.ParquetFile(
            _physical_path(
                tmp_path / "research",
                by_role["canonical_appearances"].relative_path,
            )
        )
        .read()
        .to_pylist()
    )
    by_player = {row["source_player_id"]: row for row in appearances}
    assert by_player[4]["minute_state"] == "exact"
    assert by_player[4]["minutes"] == 50.0
    assert by_player[5]["minute_state"] == "exact"
    assert by_player[5]["minutes"] == 60.0
    assert 0 not in by_player
    evidence = result.manifest["substitution_evidence"]
    assert evidence["zero_player_in_occurrence_count"] == 2
    assert evidence["zero_player_in_occurrence_counts_by_partition"] == {"Fixture": 2}
    assert evidence["zero_player_in_occurrences"] == [
        {
            "source_partition": "Fixture",
            "source_match_id": 1000,
            "source_team_id": 20,
            "source_player_out_id": 4,
            "minute": 50,
        },
        {
            "source_partition": "Fixture",
            "source_match_id": 1000,
            "source_team_id": 20,
            "source_player_out_id": 5,
            "minute": 60,
        },
    ]
    audit = audit_historical_appearance_projection(
        adapter=_adapter(zero_player_in_substitutions=True)
    )
    assert audit.zero_player_in_substitution_count == 2
    assert audit.zero_player_in_substitutions == {"Fixture": ((1000, 20, 4, 50), (1000, 20, 5, 60))}


def test_repeated_nonzero_player_in_still_fails_closed() -> None:
    adapter = _adapter()
    fixture = adapter._fixture_data
    assert fixture is not None
    matches = deepcopy(fixture.matches)
    team_row = matches["Fixture"][0]["teamsData"]["20"]
    team_row["formation"]["substitutions"] = [
        {"playerIn": 6, "playerOut": 4, "minute": 50},
        {"playerIn": 6, "playerOut": 5, "minute": 60},
    ]
    bad_adapter = WyscoutHistoricalAdapter.from_test_fixture(
        catalogues=fixture.catalogues,
        matches=matches,
        actions=fixture.actions,
        identity=adapter._fixture_identity,
        partitions=adapter.partitions,
    )
    with pytest.raises(
        HistoricalCanonicalBuildError,
        match="duplicate substitution boundary",
    ):
        audit_historical_appearance_projection(adapter=bad_adapter)


def test_late_observed_entry_is_its_own_zero_minute_lower_bound(
    tmp_path: Path,
) -> None:
    result = build_historical_canonical(
        adapter=_adapter(substitution_minute=95),
        research_root=tmp_path / "research",
        research_manifest_root=tmp_path / "manifests",
    )
    by_role = {artifact.role: artifact for artifact in result.artifacts}
    appearances = (
        pq.ParquetFile(
            _physical_path(
                tmp_path / "research",
                by_role["canonical_appearances"].relative_path,
            )
        )
        .read()
        .to_pylist()
    )
    substitute = next(row for row in appearances if row["source_player_id"] == 3)
    assert substitute["start_minute"] == substitute["end_minute"] == 95.0
    assert substitute["minutes"] == 0.0
    assert substitute["minute_state"] == "conservative_lower_bound"
    assert substitute["evidence_basis"] == (
        "observed_entry_and_regular_duration_or_last_event_lower_bound"
    )
    assert (
        result.manifest["minute_evidence"]["counts"]["entry_after_action_terminal_lower_bound"] == 1
    )


@pytest.mark.parametrize("invalid", [None, "NULL", "", {}, 1, [1]])
def test_only_exact_null_string_is_admitted_for_unavailable_substitutions(
    invalid: object,
) -> None:
    adapter = _adapter()
    fixture = adapter._fixture_data
    assert fixture is not None
    matches = deepcopy(fixture.matches)
    team_row = matches["Fixture"][0]["teamsData"]["20"]
    team_row["formation"]["substitutions"] = invalid
    bad_adapter = WyscoutHistoricalAdapter.from_test_fixture(
        catalogues=fixture.catalogues,
        matches=matches,
        actions=fixture.actions,
        identity=adapter._fixture_identity,
        partitions=adapter.partitions,
    )
    with pytest.raises(
        HistoricalCanonicalBuildError,
        match="formation substitutions are not objects",
    ):
        audit_historical_appearance_projection(adapter=bad_adapter)


@pytest.mark.parametrize("invalid", ["85", " ", True, 85.0, "not-an-id"])
def test_canonical_projection_rejects_non_integer_sub_event_values(
    tmp_path: Path,
    invalid: object,
) -> None:
    adapter = _adapter()
    fixture = adapter._fixture_data
    assert fixture is not None
    bad_actions = [dict(row) for row in fixture.actions["Fixture"]]
    bad_actions[0]["subEventId"] = invalid
    bad_adapter = WyscoutHistoricalAdapter.from_test_fixture(
        catalogues=fixture.catalogues,
        matches=fixture.matches,
        actions={"Fixture": bad_actions},
        identity=adapter._fixture_identity,
        partitions=adapter.partitions,
    )
    with pytest.raises(WyscoutHistoricalError, match="strict integer, null, or the exact empty"):
        audit_historical_action_projection(adapter=bad_adapter)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "positions",
    [
        [{"x": 10.0, "y": 20}],
        [{"x": "10", "y": 20}],
        [{"x": True, "y": 20}],
        [{"x": 10}],
        [{"x": 10, "y": 20}, {"x": 30, "y": 40}, {"x": 50, "y": 60}],
        "not-an-array",
    ],
)
def test_coordinate_structure_and_types_remain_strict(
    tmp_path: Path,
    positions: object,
) -> None:
    adapter = _adapter()
    fixture = adapter._fixture_data
    assert fixture is not None
    bad_actions = [dict(row) for row in fixture.actions["Fixture"]]
    bad_actions[0]["positions"] = positions
    bad_adapter = WyscoutHistoricalAdapter.from_test_fixture(
        catalogues=fixture.catalogues,
        matches=fixture.matches,
        actions={"Fixture": bad_actions},
        identity=adapter._fixture_identity,
        partitions=adapter.partitions,
    )
    with pytest.raises(
        (HistoricalCanonicalBuildError, WyscoutHistoricalError),
        match="position|positions",
    ):
        audit_historical_action_projection(adapter=bad_adapter)
    assert list(tmp_path.iterdir()) == []


def test_duplicate_action_keys_fail_before_any_artifact_write(tmp_path: Path) -> None:
    research_root = tmp_path / "research"
    with pytest.raises(WyscoutHistoricalError, match="duplicated"):
        build_historical_canonical(
            adapter=_adapter(duplicate_actions=True),
            research_root=research_root,
            research_manifest_root=tmp_path / "manifests",
        )
    assert not research_root.exists()


def test_source_authority_equal_to_cutoff_fails_strict_before(tmp_path: Path) -> None:
    cutoff = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
    with pytest.raises(HistoricalCanonicalBuildError, match="strictly before"):
        build_historical_canonical(
            adapter=_adapter(identity_available_at=datetime(2019, 1, 1, tzinfo=UTC)),
            research_root=tmp_path / "research",
            research_manifest_root=tmp_path / "manifests",
            feature_cutoff_ts=cutoff,
        )


def test_identity_authority_equal_to_cutoff_fails_strict_before(tmp_path: Path) -> None:
    cutoff = datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC)
    with pytest.raises(HistoricalCanonicalBuildError, match="strictly before"):
        build_historical_canonical(
            adapter=_adapter(identity_available_at=cutoff),
            research_root=tmp_path / "research",
            research_manifest_root=tmp_path / "manifests",
            feature_cutoff_ts=cutoff,
        )


def test_match_time_equal_to_cutoff_fails_strict_before(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        historical_product,
        "SOURCE_AVAILABLE_AT",
        datetime(2017, 1, 1, tzinfo=UTC),
    )
    with pytest.raises(HistoricalCanonicalBuildError, match="selected match times"):
        build_historical_canonical(
            adapter=_adapter(identity_available_at=datetime(2017, 1, 1, tzinfo=UTC)),
            research_root=tmp_path / "research",
            research_manifest_root=tmp_path / "manifests",
            feature_cutoff_ts=datetime(2018, 1, 1, 12, 0, tzinfo=UTC),
        )


def test_retained_build_rejects_alternate_output_roots_before_verification_or_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = WyscoutHistoricalAdapter.retained()

    def unexpected_verify() -> WyscoutHistoricalAdapter:
        raise AssertionError("retained authority verification should not run")

    monkeypatch.setattr(adapter, "verify", unexpected_verify)
    research_root = tmp_path / "alternate-research"
    manifest_root = tmp_path / "alternate-manifests"
    with pytest.raises(HistoricalCanonicalBuildError, match="exact canonical production"):
        build_historical_canonical(
            adapter=adapter,
            research_root=research_root,
            research_manifest_root=manifest_root,
        )
    assert not research_root.exists()
    assert not manifest_root.exists()

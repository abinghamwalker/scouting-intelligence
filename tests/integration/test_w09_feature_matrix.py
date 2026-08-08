from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.compute as pc  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
import pytest

from scouting.contracts.research import (
    EligibilityReason,
    FeatureValueState,
    canonical_research_digest,
)
from scouting.contracts.wyscout_identity import WyscoutIdentityEntityKind
from scouting.data_products.wyscout.historical import build_historical_canonical
from scouting.features.historical import (
    HistoricalFeatureBuildError,
    HistoricalFeatureBuildMode,
    build_historical_feature_matrix,
)
from scouting.modeling.research import ResearchIndexBuildMode, load_feature_matrix
from scouting.sources.wyscout_historical import (
    HistoricalIdentityAuthority,
    HistoricalPartition,
    WyscoutHistoricalAdapter,
)
from scouting.storage.formats import canonical_json_bytes

_CANONICAL_PREFIX = "data/working/wyscout/v5/research/"


def _canonical(kind: str, source_id: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"w09-feature-fixture:{kind}:{source_id}"))


def _player(source_id: int, position: str) -> dict[str, object]:
    return {
        "wyId": source_id,
        "shortName": f"Historical Fixture Player {source_id}",
        "firstName": "Historical",
        "middleName": "",
        "lastName": f"Player {source_id}",
        "birthDate": "1990-01-01",
        "role": {"code2": position},
        "foot": "right",
        "height": 180,
        "weight": 75,
        "currentTeamId": 999999,
    }


def _action(
    action_id: int,
    match_id: int,
    player_id: int,
    team_id: int,
    *,
    event_id: int = 8,
    sub_event_id: int | None = 85,
    tags: list[int] | None = None,
    valid_coordinates: bool = True,
) -> dict[str, object]:
    return {
        "id": action_id,
        "matchId": match_id,
        "playerId": player_id,
        "teamId": team_id,
        "eventId": event_id,
        "eventName": "Fixture event",
        "subEventId": sub_event_id,
        "subEventName": "Fixture sub-event",
        "matchPeriod": "1H",
        "eventSec": 600,
        "tags": [{"id": value} for value in (tags or [])],
        "positions": (
            [{"x": 10, "y": 20}, {"x": 30, "y": 40}]
            if valid_coordinates
            else [{"x": 10, "y": 20}, {"x": 30, "y": 101}]
        ),
    }


def _adapter(*, reverse_actions: bool = False) -> WyscoutHistoricalAdapter:
    matches: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    match_identities: dict[int, str] = {}
    for index in range(6):
        match_id = 1000 + index
        match_identities[match_id] = _canonical("match", match_id)
        first_lineup = [{"playerId": 1}, {"playerId": 2}]
        first_bench = [{"playerId": 3}, {"playerId": 4}, {"playerId": 7}]
        if index == 0:
            first_bench.extend(({"playerId": 999}, {"playerId": 0}))
        substitutions: list[dict[str, int]] = [{"playerIn": 4, "playerOut": 1, "minute": 90}]
        if index < 5:
            first_lineup.append({"playerId": 5})
            substitutions.append({"playerIn": 7, "playerOut": 5, "minute": 90})
        else:
            first_bench.append({"playerId": 5})
        matches.append(
            {
                "wyId": match_id,
                "competitionId": 100,
                "seasonId": 200,
                "dateutc": f"2018-01-{index + 1:02d} 12:00:00",
                "duration": "Regular",
                "status": "Played",
                "label": f"Fixture A - Fixture B, match {index + 1}",
                "venue": "Fixture Ground",
                "teamsData": {
                    "10": {
                        "teamId": 10,
                        "hasFormation": 1,
                        "formation": {
                            "lineup": first_lineup,
                            "bench": first_bench,
                            "substitutions": substitutions,
                        },
                    },
                    "20": {
                        "teamId": 20,
                        "hasFormation": 1,
                        "formation": {
                            "lineup": [{"playerId": 6}],
                            "bench": [],
                            "substitutions": [],
                        },
                    },
                },
            }
        )
        actions.extend(
            (
                _action(
                    5000 + index * 10,
                    match_id,
                    1,
                    10,
                    tags=[1801, 302] if index == 0 else [],
                    valid_coordinates=index != 0,
                ),
                _action(5001 + index * 10, match_id, 5 if index < 5 else 2, 10),
                _action(5002 + index * 10, match_id, 6, 20, event_id=1, tags=[703]),
            )
        )
    actions.append(_action(5999, 1000, 0, 20))
    if reverse_actions:
        actions.reverse()
    partition = HistoricalPartition(
        name="Fixture",
        match_relative_path="archive-members/matches_Fixture.json",
        match_sha256="1" * 64,
        match_count=len(matches),
        action_relative_path="archive-members/events_Fixture.json",
        action_sha256="2" * 64,
        action_count=len(actions),
    )
    identity = HistoricalIdentityAuthority(
        resolved={
            WyscoutIdentityEntityKind.COMPETITION: {100: _canonical("competition", 100)},
            WyscoutIdentityEntityKind.TEAM: {
                10: _canonical("team", 10),
                20: _canonical("team", 20),
            },
            WyscoutIdentityEntityKind.PLAYER: {
                source_id: _canonical("player", source_id) for source_id in range(1, 8)
            },
            WyscoutIdentityEntityKind.MATCH: match_identities,
        },
        unresolved_player_source_ids=frozenset({999}),
        rejected_player_source_ids=frozenset({0}),
        player_source_reference_counts={999: 1, 0: 2},
        bundle_sha256="3" * 64,
        available_at=datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC),
    )
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
                _player(1, "DF")
                | {
                    "shortName": r"\u0130. G\u00fcndo\u011fan",
                    "firstName": r"\u0130lkay",
                    "lastName": r"Gu\u0308ndo\u011fan",
                },
                _player(2, "MD"),
                _player(3, "FW"),
                _player(4, "FW"),
                _player(5, "MD"),
                _player(6, "GK"),
                _player(7, "FW"),
            ],
        },
        matches={"Fixture": matches},
        actions={"Fixture": actions},
        identity=identity,
        partitions=[partition],
    )


def _canonical_fixture(tmp_path: Path, *, reverse_actions: bool = False) -> tuple[Path, Path]:
    research_root = tmp_path / "canonical"
    manifest_root = tmp_path / "canonical-manifests"
    result = build_historical_canonical(
        adapter=_adapter(reverse_actions=reverse_actions),
        research_root=research_root,
        research_manifest_root=manifest_root,
    )
    manifest_name = result.manifest_relative_path.rsplit("/", 1)[-1]
    return manifest_root / manifest_name, research_root


def _replace_role_table(
    manifest_path: Path,
    canonical_root: Path,
    *,
    role: str,
    table: pa.Table,
) -> None:
    manifest = json.loads(manifest_path.read_bytes())
    descriptor = next(item for item in manifest["artifacts"] if item["role"] == role)
    relative = descriptor["path"]
    assert relative.startswith(_CANONICAL_PREFIX)
    physical = canonical_root / relative.removeprefix(_CANONICAL_PREFIX)
    pq.write_table(table, physical)
    payload = physical.read_bytes()
    descriptor["row_count"] = table.num_rows
    descriptor["size_bytes"] = len(payload)
    descriptor["sha256"] = hashlib.sha256(payload).hexdigest()
    count_name = {
        "canonical_appearances": "appearances",
        "canonical_players": "players",
    }[role]
    manifest["canonical_counts"][count_name] = table.num_rows
    manifest_path.write_bytes(canonical_json_bytes(manifest))


def test_fixture_matrix_reconciles_full_population_boundary_and_index_seam(
    tmp_path: Path,
) -> None:
    canonical_manifest, canonical_root = _canonical_fixture(tmp_path)
    feature_root = tmp_path / "features"
    result = build_historical_feature_matrix(
        canonical_manifest_path=canonical_manifest,
        canonical_artifact_root=canonical_root,
        feature_root=feature_root,
        feature_manifest_root=tmp_path / "feature-manifests",
        mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
        action_batch_size=2,
    )
    assert result.matrix_manifest_path.name.endswith(".feature-matrix.manifest.json")
    expected_suffix = canonical_research_digest(
        {
            "canonical_build_digest": result.manifest.canonical_build_digest,
            "code_digest": result.manifest.code_digest,
            "code_version": result.manifest.code_version,
            "feature_registry_digest": result.manifest.feature_registry_digest,
            "eligibility_policy_digest": result.manifest.eligibility_policy_digest,
        }
    )[:16]
    assert result.matrix_version.endswith(expected_suffix)
    assert result.manifest.catalogue_player_count == 7
    assert result.manifest.population_decision_count == 7
    assert result.manifest.eligibility_decision_count == 7
    assert result.manifest.matrix_row_count == 4
    assert {item.role for item in result.manifest.files} == {
        "player_catalogue",
        "population_decisions",
        "eligibility_decisions",
        "feature_matrix_rows",
    }
    matrix_artifact = next(
        item for item in result.manifest.files if item.role == "feature_matrix_rows"
    )
    assert matrix_artifact.relative_path.endswith(".parquet")
    matrix_table = pq.ParquetFile(feature_root / matrix_artifact.relative_path).read()
    assert matrix_table.num_rows == result.manifest.matrix_row_count
    assert matrix_table.schema.names == [
        "schema_version",
        "grain_id",
        "player_id",
        "display_name",
        "competition_id",
        "competition_name",
        "season_id",
        "position_code",
        "team_ids",
        "team_names",
        "minute_state",
        "minutes",
        "match_count",
        "features",
        "missing_feature_names",
        "coverage",
        "window_start_utc",
        "window_end_utc",
        "feature_cutoff_ts",
        "dataset_manifest_digest",
        "identity_bundle_digest",
        "canonical_build_digest",
        "feature_registry_digest",
        "eligibility_policy_digest",
        "eligibility_decision_digest",
        "source_lineage_digest",
        "source_action_count",
        "contains_synthetic_data",
    ]
    loaded = load_feature_matrix(
        result.matrix_manifest_path,
        artifact_root=feature_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    decisions = {row.source_player_id: row for row in loaded.eligibility_decisions}
    assert decisions["3"].reason is EligibilityReason.UNUSABLE_MINUTES
    assert decisions["4"].reason is EligibilityReason.BELOW_MINIMUM_MINUTES
    assert decisions["5"].minutes == 450.0
    assert decisions["5"].eligible is True
    assert decisions["1"].minute_state.value == "exact"
    assert decisions["2"].minute_state.value == "conservative_lower_bound"
    by_source = {row.source_player_id: row for row in loaded.catalogue}
    assert by_source["1"].display_name == "İ. Gündoğan"
    first_row = next(row for row in loaded.rows if row.player_id == by_source["1"].player_id)
    assert first_row.display_name == "İ. Gündoğan"
    assert first_row.coverage.coordinate_actions_observed == 5
    assert first_row.coverage.coordinate_actions_expected == 6
    assert first_row.features[0].state is FeatureValueState.VALUE
    second_row = next(row for row in loaded.rows if row.player_id == by_source["2"].player_id)
    assert second_row.features[4].feature_name == "shots_per90"
    assert second_row.features[4].state is FeatureValueState.ZERO
    assert second_row.features[4].numerator == 0.0
    fifth_row = next(row for row in loaded.rows if row.player_id == by_source["5"].player_id)
    assert fifth_row.coverage.lineup_matches_observed == 5
    assert fifth_row.coverage.lineup_matches_expected == 6
    assert all(row.contains_synthetic_data is False for row in loaded.rows)


def test_fixture_matrix_bytes_and_semantic_digests_are_reproducible(tmp_path: Path) -> None:
    canonical_manifest, canonical_root = _canonical_fixture(tmp_path)
    first = build_historical_feature_matrix(
        canonical_manifest_path=canonical_manifest,
        canonical_artifact_root=canonical_root,
        feature_root=tmp_path / "first/features",
        feature_manifest_root=tmp_path / "first/manifests",
        mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
        action_batch_size=1,
    )
    second = build_historical_feature_matrix(
        canonical_manifest_path=canonical_manifest,
        canonical_artifact_root=canonical_root,
        feature_root=tmp_path / "second/features",
        feature_manifest_root=tmp_path / "second/manifests",
        mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
        action_batch_size=10_000,
    )
    assert first.matrix_manifest_sha256 == second.matrix_manifest_sha256
    assert first.matrix_manifest_path.read_bytes() == second.matrix_manifest_path.read_bytes()
    assert [
        (item.role, item.row_count, item.sha256, item.semantic_digest)
        for item in first.manifest.files
    ] == [
        (item.role, item.row_count, item.sha256, item.semantic_digest)
        for item in second.manifest.files
    ]
    first_by_role = {item.role: item for item in first.manifest.files}
    second_by_role = {item.role: item for item in second.manifest.files}
    for role in first_by_role:
        assert (tmp_path / "first/features" / first_by_role[role].relative_path).read_bytes() == (
            tmp_path / "second/features" / second_by_role[role].relative_path
        ).read_bytes()


def test_ordered_action_key_lineage_detects_adversarial_reordering(tmp_path: Path) -> None:
    first_manifest, first_canonical_root = _canonical_fixture(tmp_path / "first-canonical")
    second_manifest, second_canonical_root = _canonical_fixture(
        tmp_path / "second-canonical", reverse_actions=True
    )
    first_root = tmp_path / "first-features"
    second_root = tmp_path / "second-features"
    first = build_historical_feature_matrix(
        canonical_manifest_path=first_manifest,
        canonical_artifact_root=first_canonical_root,
        feature_root=first_root,
        feature_manifest_root=tmp_path / "first-feature-manifests",
        mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
        action_batch_size=2,
    )
    second = build_historical_feature_matrix(
        canonical_manifest_path=second_manifest,
        canonical_artifact_root=second_canonical_root,
        feature_root=second_root,
        feature_manifest_root=tmp_path / "second-feature-manifests",
        mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
        action_batch_size=3,
    )
    first_loaded = load_feature_matrix(
        first.matrix_manifest_path,
        artifact_root=first_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    second_loaded = load_feature_matrix(
        second.matrix_manifest_path,
        artifact_root=second_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    first_by_player = {row.player_id: row for row in first_loaded.rows}
    second_by_player = {row.player_id: row for row in second_loaded.rows}
    player_id = next(row.player_id for row in first_loaded.catalogue if row.source_player_id == "1")
    assert tuple(item.value for item in first_by_player[player_id].features) == tuple(
        item.value for item in second_by_player[player_id].features
    )
    assert (
        first_by_player[player_id].source_lineage_digest
        != second_by_player[player_id].source_lineage_digest
    )


def test_stale_canonical_cutoff_fails_before_feature_write(tmp_path: Path) -> None:
    canonical_manifest, canonical_root = _canonical_fixture(tmp_path)
    payload = json.loads(canonical_manifest.read_bytes())
    payload["authorities"]["feature_cutoff_ts"] = "2026-08-06T00:00:00Z"
    stale = tmp_path / "stale.canonical-manifest.json"
    stale.write_bytes(canonical_json_bytes(payload))
    feature_root = tmp_path / "features"
    with pytest.raises(HistoricalFeatureBuildError, match="stale or incompatible"):
        build_historical_feature_matrix(
            canonical_manifest_path=stale,
            canonical_artifact_root=canonical_root,
            feature_root=feature_root,
            feature_manifest_root=tmp_path / "feature-manifests",
            mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
        )
    assert not feature_root.exists()


def test_duplicate_appearance_grain_fails_before_feature_write(tmp_path: Path) -> None:
    canonical_manifest, canonical_root = _canonical_fixture(tmp_path)
    manifest = json.loads(canonical_manifest.read_bytes())
    descriptor = next(
        item for item in manifest["artifacts"] if item["role"] == "canonical_appearances"
    )
    physical = canonical_root / descriptor["path"].removeprefix(_CANONICAL_PREFIX)
    table = pq.ParquetFile(physical).read()
    duplicated = pa.concat_tables((table, table.slice(0, 1)))
    _replace_role_table(
        canonical_manifest,
        canonical_root,
        role="canonical_appearances",
        table=duplicated,
    )
    feature_root = tmp_path / "features"
    with pytest.raises(HistoricalFeatureBuildError, match="appearance grain is duplicated"):
        build_historical_feature_matrix(
            canonical_manifest_path=canonical_manifest,
            canonical_artifact_root=canonical_root,
            feature_root=feature_root,
            feature_manifest_root=tmp_path / "feature-manifests",
            mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
            action_batch_size=2,
        )
    assert not feature_root.exists()


def test_resolved_actions_without_appearance_grain_fail_with_inventory(tmp_path: Path) -> None:
    canonical_manifest, canonical_root = _canonical_fixture(tmp_path)
    manifest = json.loads(canonical_manifest.read_bytes())
    descriptor = next(
        item for item in manifest["artifacts"] if item["role"] == "canonical_appearances"
    )
    physical = canonical_root / descriptor["path"].removeprefix(_CANONICAL_PREFIX)
    table = pq.ParquetFile(physical).read()
    retained = table.filter(pc.not_equal(table["source_player_id"], 6))
    _replace_role_table(
        canonical_manifest,
        canonical_root,
        role="canonical_appearances",
        table=retained,
    )
    feature_root = tmp_path / "features"
    with pytest.raises(
        HistoricalFeatureBuildError,
        match=r"actions=6, grains=1, players=1, matches=6",
    ):
        build_historical_feature_matrix(
            canonical_manifest_path=canonical_manifest,
            canonical_artifact_root=canonical_root,
            feature_root=feature_root,
            feature_manifest_root=tmp_path / "feature-manifests",
            mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
            action_batch_size=2,
        )
    assert not feature_root.exists()


def test_unsupported_canonical_position_fails_without_imputation(tmp_path: Path) -> None:
    canonical_manifest, canonical_root = _canonical_fixture(tmp_path)
    manifest = json.loads(canonical_manifest.read_bytes())
    descriptor = next(item for item in manifest["artifacts"] if item["role"] == "canonical_players")
    physical = canonical_root / descriptor["path"].removeprefix(_CANONICAL_PREFIX)
    table = pq.ParquetFile(physical).read()
    rows = table.to_pylist()
    rows[0]["position_code"] = "XX"
    incompatible = pa.Table.from_pylist(rows, schema=table.schema)
    _replace_role_table(
        canonical_manifest,
        canonical_root,
        role="canonical_players",
        table=incompatible,
    )
    feature_root = tmp_path / "features"
    with pytest.raises(HistoricalFeatureBuildError, match="position is unsupported"):
        build_historical_feature_matrix(
            canonical_manifest_path=canonical_manifest,
            canonical_artifact_root=canonical_root,
            feature_root=feature_root,
            feature_manifest_root=tmp_path / "feature-manifests",
            mode=HistoricalFeatureBuildMode.TEST_FIXTURE,
            action_batch_size=2,
        )
    assert not feature_root.exists()

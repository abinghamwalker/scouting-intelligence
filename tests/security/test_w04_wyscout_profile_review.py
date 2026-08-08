from __future__ import annotations

import ast
import codecs
import csv
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import cast

import pytest

_ROOT = Path(__file__).parents[2]
_SOURCE_ROOT = _ROOT / "data/source/wyscout/v5"
_MANIFEST_PATH = _SOURCE_ROOT / "completion-manifest.json"
_PROFILE_PATH = _ROOT / "reports/phase-gates/W04/source-schema-profile.md"
_SCRIPT_PATH = _ROOT / "scripts/profile_wyscout_v5.py"
_COMPLETION_SHA256 = "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
_PROFILE_SHA256 = "569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649"
_PROFILE_SIZE_BYTES = 18_574
_CHUNK_BYTES = 1 << 20
_MAX_ITEM_CHARS = 16 << 20

_EXPECTED_MATCH_COUNTS = {
    "matches_England.json": 380,
    "matches_France.json": 380,
    "matches_Germany.json": 306,
    "matches_Italy.json": 380,
    "matches_Spain.json": 380,
}
_EXPECTED_EVENT_COUNTS = {
    "events_England.json": 643_150,
    "events_France.json": 632_807,
    "events_Germany.json": 519_407,
    "events_Italy.json": 647_372,
    "events_Spain.json": 628_659,
}
_EXPECTED_PERIOD_COUNTS = {"1H": 1_541_033, "2H": 1_530_362}


def _object(value: object, context: str) -> dict[str, object]:
    assert isinstance(value, dict), f"{context} must be an object"
    assert all(isinstance(key, str) for key in value), f"{context} keys must be strings"
    return cast(dict[str, object], value)


def _array(value: object, context: str) -> list[object]:
    assert isinstance(value, list), f"{context} must be an array"
    return cast(list[object], value)


def _text(record: Mapping[str, object], key: str, context: str) -> str:
    value = record.get(key)
    assert isinstance(value, str) and value, f"{context}.{key} must be non-empty text"
    return value


def _integer(value: object, context: str) -> int:
    assert isinstance(value, int) and not isinstance(value, bool), f"{context} must be an integer"
    return value


def _declared_path(root: Path, raw: object) -> Path:
    assert isinstance(raw, str) and raw
    assert "\\" not in raw
    logical = PurePosixPath(raw)
    assert not logical.is_absolute()
    assert all(part not in {"", ".", ".."} for part in logical.parts)
    candidate = root.joinpath(*logical.parts)
    assert not candidate.is_symlink()
    resolved_root = root.resolve(strict=True)
    resolved = candidate.resolve(strict=True)
    resolved.relative_to(resolved_root)
    return resolved


def _verify_file(path: Path, expected_sha256: str, expected_size: int) -> None:
    digest = hashlib.sha256()
    measured_size = 0
    with path.open("rb") as source:
        while chunk := source.read(_CHUNK_BYTES):
            digest.update(chunk)
            measured_size += len(chunk)
    assert measured_size == expected_size
    assert digest.hexdigest() == expected_sha256


def _iter_json_array(
    path: Path,
    *,
    expected_sha256: str,
    expected_size: int,
) -> Iterator[dict[str, object]]:
    decoder = codecs.getincrementaldecoder("utf-8")()
    json_decoder = json.JSONDecoder(parse_float=Decimal)
    digest = hashlib.sha256()
    measured_size = 0
    buffer = ""
    position = 0
    eof = False

    with path.open("rb") as source:

        def fill() -> bool:
            nonlocal buffer, eof, measured_size
            if eof:
                return False
            raw = source.read(_CHUNK_BYTES)
            if raw:
                digest.update(raw)
                measured_size += len(raw)
                buffer += decoder.decode(raw)
                assert len(buffer) - position <= _MAX_ITEM_CHARS
                return True
            buffer += decoder.decode(b"", final=True)
            eof = True
            return False

        def skip_space() -> None:
            nonlocal position
            while True:
                while position < len(buffer) and buffer[position].isspace():
                    position += 1
                if position < len(buffer) or not fill():
                    return

        skip_space()
        assert position < len(buffer) and buffer[position] == "["
        position += 1
        expecting_value = True
        while True:
            skip_space()
            assert position < len(buffer)
            if expecting_value and buffer[position] == "]":
                position += 1
                break
            if not expecting_value:
                if buffer[position] == ",":
                    position += 1
                    expecting_value = True
                    continue
                assert buffer[position] == "]"
                position += 1
                break
            while True:
                try:
                    value, end = json_decoder.raw_decode(buffer, position)
                except json.JSONDecodeError:
                    assert not eof
                    fill()
                    continue
                position = end
                break
            yield _object(value, f"record in {path.name}")
            expecting_value = False
            if position > _CHUNK_BYTES:
                buffer = buffer[position:]
                position = 0
        while not eof:
            fill()
        assert not buffer[position:].strip()

    assert measured_size == expected_size
    assert digest.hexdigest() == expected_sha256


@dataclass(frozen=True)
class Declared:
    name: str
    path: Path
    sha256: str
    size_bytes: int


@dataclass
class Evidence:
    manifest: dict[str, object]
    opened_paths: set[Path] = field(default_factory=set)
    direct_counts: dict[str, int] = field(default_factory=dict)
    match_counts: dict[str, int] = field(default_factory=dict)
    event_counts: dict[str, int] = field(default_factory=dict)
    match_ids_by_suffix: dict[str, set[int]] = field(default_factory=dict)
    event_match_ids_by_suffix: dict[str, set[int]] = field(default_factory=dict)
    competition_ids: set[int] = field(default_factory=set)
    team_ids: set[int] = field(default_factory=set)
    player_ids: set[int] = field(default_factory=set)
    admitted_competition_ids: set[int] = field(default_factory=set)
    admitted_team_ids: set[int] = field(default_factory=set)
    match_ids: set[int] = field(default_factory=set)
    event_record_ids: set[int] = field(default_factory=set)
    event_record_duplicates: int = 0
    period_counts: Counter[str] = field(default_factory=Counter)
    event_seconds_invalid: int = 0
    event_seconds_max_scale: int = 0
    event_seconds_minimum: dict[str, Decimal] = field(default_factory=dict)
    event_seconds_maximum: dict[str, Decimal] = field(default_factory=dict)
    match_period_maximum: dict[tuple[int, str], Decimal] = field(default_factory=dict)
    dateutc_parseable: int = 0
    duration_values: Counter[str] = field(default_factory=Counter)
    substitution_shapes: Counter[str] = field(default_factory=Counter)
    null_string_substitution_containers: int = 0
    lineup_rows: int = 0
    bench_rows: int = 0
    substitution_rows: int = 0
    substitution_minute_minimum: int | None = None
    substitution_minute_maximum: int | None = None
    team_entry_count_errors: int = 0
    match_competition_unmapped: int = 0
    match_team_unmapped: int = 0
    team_key_id_mismatches: int = 0
    lineup_player_unmapped: int = 0
    bench_player_unmapped: int = 0
    substitution_player_in_unmapped: int = 0
    substitution_player_out_unmapped: int = 0
    event_match_unmapped: int = 0
    event_member_mismatches: int = 0
    event_team_not_in_match: int = 0
    event_player_zero: int = 0
    event_player_unmapped: int = 0
    event_type_unmapped: int = 0
    event_subtype_invalid: int = 0
    event_subtype_unmapped: int = 0
    event_tag_count: int = 0
    event_tag_unmapped: int = 0
    coordinate_invalid: int = 0
    position_length_counts: Counter[int] = field(default_factory=Counter)
    coordinate_minimum: dict[str, int] = field(default_factory=dict)
    coordinate_maximum: dict[str, int] = field(default_factory=dict)
    coordinate_out_of_range: Counter[str] = field(default_factory=Counter)
    player_names: set[str] = field(default_factory=set)
    private_entity_labels: set[str] = field(default_factory=set)
    event_map_ids: set[int] = field(default_factory=set)
    subevent_map_ids: set[int] = field(default_factory=set)
    tag_map_ids: set[int] = field(default_factory=set)
    duplicate_event_map_ids: int = 0
    duplicate_subevent_map_ids: int = 0
    duplicate_tag_map_ids: int = 0
    players_by_match: dict[int, set[int]] = field(default_factory=dict)


def _declared(record: Mapping[str, object], path_key: str) -> Declared:
    path = _declared_path(_SOURCE_ROOT, record.get(path_key))
    return Declared(
        name=_text(record, "name", "manifest record"),
        path=path,
        sha256=_text(record, "sha256", "manifest record"),
        size_bytes=_integer(record.get("size_bytes"), "manifest size_bytes"),
    )


def _consume_mapping_csv(declared: Declared, evidence: Evidence) -> None:
    payload = declared.path.read_bytes()
    evidence.opened_paths.add(declared.path)
    assert len(payload) == declared.size_bytes
    assert hashlib.sha256(payload).hexdigest() == declared.sha256
    rows = csv.DictReader(payload.decode("utf-8-sig").splitlines())
    assert rows.fieldnames is not None
    for row in rows:
        if declared.name == "eventid2name.csv":
            event_id = int(cast(str, row["event"]))
            subevent_id = int(cast(str, row["subevent"]))
            if event_id in evidence.event_map_ids:
                evidence.duplicate_event_map_ids += 1
            if subevent_id in evidence.subevent_map_ids:
                evidence.duplicate_subevent_map_ids += 1
            evidence.event_map_ids.add(event_id)
            evidence.subevent_map_ids.add(subevent_id)
        else:
            tag_id = int(cast(str, row["Tag"]))
            if tag_id in evidence.tag_map_ids:
                evidence.duplicate_tag_map_ids += 1
            evidence.tag_map_ids.add(tag_id)


def _scope_suffix(member_name: str) -> str:
    prefix, suffix = member_name.split("_", maxsplit=1)
    assert prefix in {"matches", "events"}
    assert suffix.endswith(".json")
    return suffix


def _recompute() -> Evidence:
    manifest_bytes = _MANIFEST_PATH.read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest() == _COMPLETION_SHA256
    manifest = _object(json.loads(manifest_bytes), "completion manifest")
    assert manifest.get("state") == "complete"
    evidence = Evidence(manifest=manifest, opened_paths={_MANIFEST_PATH.resolve()})

    direct_records = [
        _object(value, f"objects[{index}]")
        for index, value in enumerate(_array(manifest.get("objects"), "objects"))
    ]
    direct = {
        _text(record, "name", "object"): _declared(record, "object_path")
        for record in direct_records
    }
    assert set(direct) == {
        "competitions.json",
        "teams.json",
        "players.json",
        "matches.zip",
        "events.zip",
        "eventid2name.csv",
        "tags2name.csv",
    }

    _consume_mapping_csv(direct["eventid2name.csv"], evidence)
    _consume_mapping_csv(direct["tags2name.csv"], evidence)
    for name, target, name_fields in (
        ("competitions.json", evidence.competition_ids, ()),
        ("teams.json", evidence.team_ids, ()),
        (
            "players.json",
            evidence.player_ids,
            ("firstName", "middleName", "lastName", "shortName"),
        ),
    ):
        declared = direct[name]
        evidence.opened_paths.add(declared.path)
        count = 0
        for record in _iter_json_array(
            declared.path,
            expected_sha256=declared.sha256,
            expected_size=declared.size_bytes,
        ):
            target.add(_integer(record.get("wyId"), f"{name}.wyId"))
            for field_name in name_fields:
                value = record.get(field_name)
                if isinstance(value, str) and len(value.strip()) >= 4:
                    if name == "players.json":
                        evidence.player_names.add(value)
                    else:
                        evidence.private_entity_labels.add(value)
            count += 1
        evidence.direct_counts[name] = count

    admitted_records = [
        _object(value, f"admitted[{index}]")
        for index, value in enumerate(
            _array(manifest.get("admitted_archive_members"), "admitted members")
        )
    ]
    admitted = [
        (_text(record, "archive_name", "admitted member"), _declared(record, "member_path"))
        for record in admitted_records
    ]
    assert len(admitted) == 10

    match_team_ids: dict[int, set[int]] = {}
    match_suffix: dict[int, str] = {}
    for archive_name, declared in admitted:
        if archive_name != "matches.zip":
            continue
        evidence.opened_paths.add(declared.path)
        suffix = _scope_suffix(declared.name)
        member_match_ids: set[int] = set()
        count = 0
        for record in _iter_json_array(
            declared.path,
            expected_sha256=declared.sha256,
            expected_size=declared.size_bytes,
        ):
            for field_name in ("label", "venue"):
                value = record.get(field_name)
                if isinstance(value, str) and len(value.strip()) >= 4:
                    evidence.private_entity_labels.add(value)
            match_id = _integer(record.get("wyId"), "match.wyId")
            assert match_id not in evidence.match_ids
            evidence.match_ids.add(match_id)
            member_match_ids.add(match_id)
            match_suffix[match_id] = suffix
            competition_id = _integer(record.get("competitionId"), "match.competitionId")
            evidence.admitted_competition_ids.add(competition_id)
            if competition_id not in evidence.competition_ids:
                evidence.match_competition_unmapped += 1
            dateutc = record.get("dateutc")
            if isinstance(dateutc, str):
                try:
                    datetime.strptime(dateutc, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
                else:
                    evidence.dateutc_parseable += 1
            duration = record.get("duration")
            evidence.duration_values[
                duration if isinstance(duration, str) else f"<{type(duration).__name__}>"
            ] += 1
            teams_data = record.get("teamsData")
            assert isinstance(teams_data, Mapping)
            if len(teams_data) != 2:
                evidence.team_entry_count_errors += 1
            teams_for_match: set[int] = set()
            for raw_key, raw_team in teams_data.items():
                team = _object(raw_team, "teamsData entry")
                team_key = int(cast(str, raw_key))
                team_id = _integer(team.get("teamId"), "teamsData.teamId")
                if team_key != team_id:
                    evidence.team_key_id_mismatches += 1
                if team_id not in evidence.team_ids:
                    evidence.match_team_unmapped += 1
                teams_for_match.add(team_id)
                evidence.admitted_team_ids.add(team_id)
                formation = _object(team.get("formation"), "formation")
                for location in ("lineup", "bench"):
                    rows = _array(formation.get(location), f"formation.{location}")
                    if location == "lineup":
                        evidence.lineup_rows += len(rows)
                    else:
                        evidence.bench_rows += len(rows)
                    for raw_row in rows:
                        row = _object(raw_row, f"formation.{location}[]")
                        player_id = _integer(
                            row.get("playerId"),
                            f"formation.{location}[].playerId",
                        )
                        if player_id not in evidence.player_ids:
                            if location == "lineup":
                                evidence.lineup_player_unmapped += 1
                            else:
                                evidence.bench_player_unmapped += 1
                substitutions = formation.get("substitutions")
                shape = (
                    "array"
                    if isinstance(substitutions, list)
                    else "string"
                    if isinstance(substitutions, str)
                    else type(substitutions).__name__
                )
                evidence.substitution_shapes[shape] += 1
                if isinstance(substitutions, str):
                    if substitutions == "null":
                        evidence.null_string_substitution_containers += 1
                elif isinstance(substitutions, list):
                    evidence.substitution_rows += len(substitutions)
                    for raw_substitution in substitutions:
                        substitution = _object(
                            raw_substitution,
                            "formation.substitutions[]",
                        )
                        minute = _integer(
                            substitution.get("minute"),
                            "formation.substitutions[].minute",
                        )
                        evidence.substitution_minute_minimum = (
                            minute
                            if evidence.substitution_minute_minimum is None
                            else min(evidence.substitution_minute_minimum, minute)
                        )
                        evidence.substitution_minute_maximum = (
                            minute
                            if evidence.substitution_minute_maximum is None
                            else max(evidence.substitution_minute_maximum, minute)
                        )
                        player_in = _integer(
                            substitution.get("playerIn"),
                            "formation.substitutions[].playerIn",
                        )
                        player_out = _integer(
                            substitution.get("playerOut"),
                            "formation.substitutions[].playerOut",
                        )
                        if player_in not in evidence.player_ids:
                            evidence.substitution_player_in_unmapped += 1
                        if player_out not in evidence.player_ids:
                            evidence.substitution_player_out_unmapped += 1
            match_team_ids[match_id] = teams_for_match
            count += 1
        evidence.match_counts[declared.name] = count
        evidence.match_ids_by_suffix[suffix] = member_match_ids

    for archive_name, declared in admitted:
        if archive_name != "events.zip":
            continue
        evidence.opened_paths.add(declared.path)
        suffix = _scope_suffix(declared.name)
        event_match_ids: set[int] = set()
        count = 0
        for record in _iter_json_array(
            declared.path,
            expected_sha256=declared.sha256,
            expected_size=declared.size_bytes,
        ):
            event_record_id = _integer(record.get("id"), "event.id")
            if event_record_id in evidence.event_record_ids:
                evidence.event_record_duplicates += 1
            evidence.event_record_ids.add(event_record_id)

            match_id = _integer(record.get("matchId"), "event.matchId")
            event_match_ids.add(match_id)
            if match_id not in evidence.match_ids:
                evidence.event_match_unmapped += 1
            if match_suffix.get(match_id) != suffix:
                evidence.event_member_mismatches += 1
            team_id = _integer(record.get("teamId"), "event.teamId")
            if team_id not in match_team_ids.get(match_id, set()):
                evidence.event_team_not_in_match += 1

            player_id = _integer(record.get("playerId"), "event.playerId")
            if player_id == 0:
                evidence.event_player_zero += 1
            else:
                evidence.players_by_match.setdefault(match_id, set()).add(player_id)
                if player_id not in evidence.player_ids:
                    evidence.event_player_unmapped += 1

            event_type_id = _integer(record.get("eventId"), "event.eventId")
            if event_type_id not in evidence.event_map_ids:
                evidence.event_type_unmapped += 1
            event_subtype_id = record.get("subEventId")
            if isinstance(event_subtype_id, int) and not isinstance(event_subtype_id, bool):
                if event_subtype_id not in evidence.subevent_map_ids:
                    evidence.event_subtype_unmapped += 1
            else:
                evidence.event_subtype_invalid += 1
            tags = _array(record.get("tags"), "event.tags")
            evidence.event_tag_count += len(tags)
            for raw_tag in tags:
                tag_id = _integer(_object(raw_tag, "event.tags[]").get("id"), "event tag id")
                if tag_id not in evidence.tag_map_ids:
                    evidence.event_tag_unmapped += 1

            period = record.get("matchPeriod")
            period_key = period if isinstance(period, str) else f"<{type(period).__name__}>"
            evidence.period_counts[period_key] += 1
            event_sec = record.get("eventSec")
            event_second: Decimal | None = None
            if isinstance(event_sec, (int, Decimal)) and not isinstance(event_sec, bool):
                event_second = Decimal(event_sec)
                if event_second.is_finite():
                    exponent = event_second.as_tuple().exponent
                    assert isinstance(exponent, int)
                    evidence.event_seconds_max_scale = max(
                        evidence.event_seconds_max_scale,
                        max(0, -exponent),
                    )
                    evidence.event_seconds_minimum[period_key] = min(
                        evidence.event_seconds_minimum.get(period_key, event_second),
                        event_second,
                    )
                    evidence.event_seconds_maximum[period_key] = max(
                        evidence.event_seconds_maximum.get(period_key, event_second),
                        event_second,
                    )
                    maximum_key = (match_id, period_key)
                    evidence.match_period_maximum[maximum_key] = max(
                        evidence.match_period_maximum.get(maximum_key, event_second),
                        event_second,
                    )
                else:
                    evidence.event_seconds_invalid += 1
            else:
                evidence.event_seconds_invalid += 1

            positions = record.get("positions")
            if not isinstance(positions, list):
                evidence.coordinate_invalid += 1
            else:
                evidence.position_length_counts[len(positions)] += 1
                for raw_position in positions:
                    position = _object(raw_position, "event.positions[]")
                    for axis in ("x", "y"):
                        coordinate = position.get(axis)
                        if not isinstance(coordinate, int) or isinstance(coordinate, bool):
                            evidence.coordinate_invalid += 1
                        else:
                            evidence.coordinate_minimum[axis] = min(
                                evidence.coordinate_minimum.get(axis, coordinate),
                                coordinate,
                            )
                            evidence.coordinate_maximum[axis] = max(
                                evidence.coordinate_maximum.get(axis, coordinate),
                                coordinate,
                            )
                            if not 0 <= coordinate <= 100:
                                evidence.coordinate_invalid += 1
                                evidence.coordinate_out_of_range[axis] += 1
            count += 1
        evidence.event_counts[declared.name] = count
        evidence.event_match_ids_by_suffix[suffix] = event_match_ids

    return evidence


@pytest.fixture(scope="module")
def evidence() -> Evidence:
    return _recompute()


def test_completion_binding_inventory_and_independent_aggregate_counts(
    evidence: Evidence,
) -> None:
    excluded = [
        _object(value, f"excluded[{index}]")
        for index, value in enumerate(
            _array(
                evidence.manifest.get("scope_excluded_archive_members"),
                "scope exclusions",
            )
        )
    ]
    assert len(excluded) == 4
    assert {_text(record, "name", "excluded member") for record in excluded} == {
        "matches_European_Championship.json",
        "matches_World_Cup.json",
        "events_European_Championship.json",
        "events_World_Cup.json",
    }
    assert evidence.direct_counts == {
        "competitions.json": 7,
        "teams.json": 142,
        "players.json": 3_603,
    }
    assert evidence.match_counts == _EXPECTED_MATCH_COUNTS
    assert evidence.event_counts == _EXPECTED_EVENT_COUNTS
    assert len(evidence.match_ids) == 1_826
    assert len(evidence.event_record_ids) == 3_071_395
    assert evidence.event_record_duplicates == 0
    assert evidence.period_counts == _EXPECTED_PERIOD_COUNTS
    assert evidence.event_seconds_invalid == 0
    assert evidence.event_seconds_max_scale == 18


def test_match_bound_scope_and_major_relations_recompute(evidence: Evidence) -> None:
    assert len(evidence.admitted_competition_ids) == 5
    assert evidence.admitted_competition_ids <= evidence.competition_ids
    assert len(evidence.admitted_team_ids) == 98
    assert evidence.admitted_team_ids <= evidence.team_ids
    assert evidence.dateutc_parseable == 1_826
    assert evidence.duration_values == {"Regular": 1_826}
    assert evidence.substitution_shapes == {"array": 3_646, "string": 6}
    assert evidence.null_string_substitution_containers == 6
    assert evidence.lineup_rows == 40_172
    assert evidence.bench_rows == 28_715
    assert evidence.substitution_rows == 10_423
    assert evidence.substitution_minute_minimum == 3
    assert evidence.substitution_minute_maximum == 97
    assert evidence.team_entry_count_errors == 0
    assert evidence.match_competition_unmapped == 0
    assert evidence.match_team_unmapped == 0
    assert evidence.team_key_id_mismatches == 0
    assert evidence.lineup_player_unmapped == 0
    assert evidence.bench_player_unmapped == 23
    assert evidence.substitution_player_in_unmapped == 8
    assert evidence.substitution_player_out_unmapped == 0
    assert evidence.event_match_unmapped == 0
    assert evidence.event_member_mismatches == 0
    assert evidence.event_team_not_in_match == 0
    assert evidence.event_player_zero == 226_038
    assert evidence.event_player_unmapped == 0
    assert evidence.event_type_unmapped == 0
    assert evidence.event_subtype_invalid == 7_821
    assert evidence.event_subtype_unmapped == 0
    assert evidence.event_tag_count == 4_336_816
    assert evidence.event_tag_unmapped == 0
    assert evidence.coordinate_invalid == 3
    assert evidence.coordinate_minimum == {"x": -1, "y": 0}
    assert evidence.coordinate_maximum == {"x": 100, "y": 101}
    assert evidence.coordinate_out_of_range == {"x": 1, "y": 2}
    assert set(evidence.position_length_counts) <= {1, 2}
    assert evidence.position_length_counts[1] == 709
    assert evidence.position_length_counts[2] == 3_070_686
    assert evidence.duplicate_event_map_ids > 0
    assert evidence.duplicate_subevent_map_ids == 0
    assert evidence.duplicate_tag_map_ids == 0
    assert len(evidence.players_by_match) == 1_826
    assert sum(map(len, evidence.players_by_match.values())) == 50_522
    for suffix, match_ids in evidence.match_ids_by_suffix.items():
        assert evidence.event_match_ids_by_suffix[suffix] == match_ids


def test_exact_decimal_and_match_period_extrema_recompute(
    evidence: Evidence,
) -> None:
    assert evidence.event_seconds_minimum == {
        "1H": Decimal("0.020000000000010232"),
        "2H": Decimal("0"),
    }
    assert evidence.event_seconds_maximum == {
        "1H": Decimal("3302.282734"),
        "2H": Decimal("3537.3560610000004"),
    }
    maxima_by_period = {
        period: [
            maximum
            for (_match_id, match_period), maximum in evidence.match_period_maximum.items()
            if match_period == period
        ]
        for period in ("1H", "2H")
    }
    assert {period: len(maxima) for period, maxima in maxima_by_period.items()} == {
        "1H": 1_826,
        "2H": 1_826,
    }
    assert {period: (min(maxima), max(maxima)) for period, maxima in maxima_by_period.items()} == {
        "1H": (Decimal("2576.313699"), Decimal("3302.282734")),
        "2H": (
            Decimal("2649.6185100000002"),
            Decimal("3537.3560610000004"),
        ),
    }


def test_tracked_report_is_aggregate_only_and_contains_no_player_name(
    evidence: Evidence,
) -> None:
    report = _PROFILE_PATH.read_text(encoding="utf-8")
    for player_name in evidence.player_names:
        assert player_name not in report
    for private_label in evidence.private_entity_labels:
        assert private_label not in report
    assert not any(path.name in {"matches.zip", "events.zip"} for path in evidence.opened_paths)
    assert all("European_Championship" not in str(path) for path in evidence.opened_paths)
    assert all("World_Cup" not in str(path) for path in evidence.opened_paths)


def test_report_exposes_partition_scope_and_r3_required_measured_inputs(
    evidence: Evidence,
) -> None:
    report = _PROFILE_PATH.read_text(encoding="utf-8")
    licence = _object(evidence.manifest.get("licence"), "completion licence")
    required_evidence = [
        f"| classification | {evidence.manifest['classification']} |",
        f"| licence_id | {licence['licence_id']} |",
        (
            "| source_available_at | "
            f"{_object(evidence.manifest['acquisition'], 'acquisition')['source_available_at']} |"
        ),
        (
            "| acquired_at | "
            f"{_object(evidence.manifest['acquisition'], 'acquisition')['acquired_at']} |"
        ),
        *(
            f"| {member_name} | {row_count} |"
            for member_name, row_count in evidence.match_counts.items()
        ),
        *(
            f"| {member_name} | {row_count} |"
            for member_name, row_count in evidence.event_counts.items()
        ),
        f"| distinct competition IDs referenced by admitted matches | "
        f"{len(evidence.admitted_competition_ids)} |",
        f"| distinct team IDs referenced by admitted matches | {len(evidence.admitted_team_ids)} |",
        f"| distinct event record id values | {len(evidence.event_record_ids)} |",
        "| duplicate event record id values | 0 |",
        "| event teamId not in referenced match teamsData | 0 |",
        "| event/member match-partition mismatches | 0 |",
        "| distinct non-zero event player-match pairs | 50522 |",
        "| matches with at least one non-zero event player | 1826 |",
        "| dateutc values matching YYYY-MM-DD HH:MM:SS | 1826 |",
        "| duration category Regular | 1826 |",
        "| literal-null-string substitution containers | 6 |",
        "| maximum measured eventSec decimal scale | 18 |",
        "| positions with one coordinate | 709 |",
        "| positions with two coordinates | 3070686 |",
        "| coordinate values outside inclusive 0..100 | 3 |",
        "| x | 6142081 | 0 | -1 | 100 | 1 |",
        "| y | 6142081 | 0 | 0 | 101 | 2 |",
        (
            "| 1H | 1541033 | 1541033 | 0 | 0.020000000000010232 | "
            "3302.282734 | 1826 | 2576.313699 | 3302.282734 |"
        ),
        (
            "| 2H | 1530362 | 1530362 | 0 | 0 | 3537.3560610000004 | "
            "1826 | 2649.6185100000002 | 3537.3560610000004 |"
        ),
        "| exact period terminal supported | no |",
        "| exact player minutes supported | no |",
        "| per-90 denominator supported | no |",
    ]
    required_paths = [
        _text(_object(raw, "manifest object"), "object_path", "manifest object")
        for raw in _array(evidence.manifest.get("objects"), "objects")
    ]
    required_paths.extend(
        _text(_object(raw, "admitted member"), "member_path", "admitted member")
        for raw in _array(
            evidence.manifest.get("admitted_archive_members"),
            "admitted_archive_members",
        )
    )
    missing = [line for line in required_evidence if line not in report]
    missing.extend(f"path: {path}" for path in required_paths if path not in report)
    assert not missing, "tracked profile omits R3-required aggregate evidence:\n" + "\n".join(
        missing
    )


def test_report_binds_every_completion_inventory_row_and_exact_bytes(
    evidence: Evidence,
) -> None:
    report_bytes = _PROFILE_PATH.read_bytes()
    report = report_bytes.decode()
    assert len(report_bytes) == _PROFILE_SIZE_BYTES
    assert hashlib.sha256(report_bytes).hexdigest() == _PROFILE_SHA256

    direct_names_opened = {
        "competitions.json",
        "teams.json",
        "players.json",
        "eventid2name.csv",
        "tags2name.csv",
    }
    for raw in _array(evidence.manifest.get("objects"), "objects"):
        record = _object(raw, "manifest object")
        name = _text(record, "name", "manifest object")
        access = "opened" if name in direct_names_opened else "not opened"
        exact_row = (
            f"| completion source object | {name} | "
            f"{_text(record, 'object_path', 'manifest object')} | "
            f"{_integer(record.get('size_bytes'), 'manifest object size')} | "
            f"{_text(record, 'sha256', 'manifest object')} | {access} |"
        )
        assert exact_row in report

    for raw in _array(
        evidence.manifest.get("admitted_archive_members"),
        "admitted archive members",
    ):
        record = _object(raw, "admitted member")
        archive_name = _text(record, "archive_name", "admitted member")
        exact_row = (
            f"| separately durable admitted member of {archive_name} | "
            f"{_text(record, 'name', 'admitted member')} | "
            f"{_text(record, 'member_path', 'admitted member')} | "
            f"{_integer(record.get('size_bytes'), 'admitted member size')} | "
            f"{_text(record, 'sha256', 'admitted member')} | opened |"
        )
        assert exact_row in report


def test_check_mode_is_static_network_free_read_only_and_byte_stable() -> None:
    module = ast.parse(_SCRIPT_PATH.read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".", maxsplit=1)[0]
        for node in ast.walk(module)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".", maxsplit=1)[0]
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    assert imported_roots.isdisjoint({"httpx", "requests", "socket", "urllib", "zipfile"})

    before_report = _PROFILE_PATH.read_bytes()
    declared_paths = [
        path for path in _SOURCE_ROOT.rglob("*") if path.is_file() and not path.is_symlink()
    ]
    before_stats = {path: (path.stat().st_size, path.stat().st_mtime_ns) for path in declared_paths}
    completed = subprocess.run(  # noqa: S603
        [sys.executable, str(_SCRIPT_PATH), "--check"],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert _PROFILE_PATH.read_bytes() == before_report
    assert {
        path: (path.stat().st_size, path.stat().st_mtime_ns) for path in declared_paths
    } == before_stats


@pytest.mark.parametrize(
    ("option", "value", "expected_error"),
    (
        (
            "--source-root",
            "unreviewed-source",
            "production source root must be the repository-approved",
        ),
        (
            "--output",
            "unreviewed-profile.md",
            "production output must be the repository-approved",
        ),
        (
            "--expected-completion-sha256",
            "0" * 64,
            "production completion SHA-256 override is not permitted",
        ),
    ),
)
def test_production_cli_rejects_every_unreviewed_path_or_digest_override(
    tmp_path: Path,
    option: str,
    value: str,
    expected_error: str,
) -> None:
    before_report = _PROFILE_PATH.read_bytes()
    override = tmp_path / value if option != "--expected-completion-sha256" else value
    completed = subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(_SCRIPT_PATH),
            "--check",
            option,
            str(override),
        ],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert expected_error in completed.stderr
    assert _PROFILE_PATH.read_bytes() == before_report
    assert not (tmp_path / "unreviewed-profile.md").exists()


def test_profile_bounds_are_finite_and_output_path_is_not_guarded() -> None:
    module_text = _SCRIPT_PATH.read_text(encoding="utf-8")
    assert "MAX_JSON_BUFFER_CHARS" in module_text
    assert "MAX_SCHEMA_PATHS" in module_text
    assert "MAX_SCHEMA_DEPTH" in module_text
    assert "MAX_MANIFEST_BYTES" in module_text
    assert "MAX_CSV_BYTES" in module_text
    assert math.isfinite(float(_MAX_ITEM_CHARS))
    assert 'parser.add_argument("--output", type=Path' in module_text
    assert "source_root.resolve() != DEFAULT_SOURCE_ROOT" in module_text
    assert "output.resolve() != DEFAULT_OUTPUT" in module_text
    assert "expected_digest != EXPECTED_COMPLETION_SHA256" in module_text
    assert "os.replace(temporary_path, path)" in module_text

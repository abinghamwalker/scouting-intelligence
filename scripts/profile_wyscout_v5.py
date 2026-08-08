#!/usr/bin/env python3
"""Deterministically profile the completion-declared Wyscout v5 snapshot.

The profiler deliberately has no archive or network support. Every source-data
path it opens is taken verbatim from an admitted completion-manifest record.
Only aggregate field/type/count evidence is emitted.
"""

from __future__ import annotations

import argparse
import codecs
import csv
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any, cast

EXPECTED_COMPLETION_SHA256 = "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = (REPOSITORY_ROOT / "data/source/wyscout/v5").resolve()
DEFAULT_OUTPUT = (REPOSITORY_ROOT / "reports/phase-gates/W04/source-schema-profile.md").resolve()
CHUNK_BYTES = 1 << 20
MAX_JSON_BUFFER_CHARS = 16 << 20
MAX_SCHEMA_PATHS = 2_000
MAX_SCHEMA_DEPTH = 8
MAX_MANIFEST_BYTES = 4 << 20
MAX_CSV_BYTES = 4 << 20
MAX_DISTINCT_IDS = 2_000_000
MAX_PERIOD_VALUES = 128
MAX_MATCH_PERIOD_PAIRS = 2_000_000
MAX_EVENT_RECORD_IDS = 4_000_000
MAX_PLAYER_MATCH_PAIRS = 4_000_000
MAX_DURATION_CATEGORIES = 128
DATEUTC_FORMAT = "%Y-%m-%d %H:%M:%S"

JsonObject = dict[str, Any]


class ProfileError(RuntimeError):
    """Raised when declared source evidence is unsafe, incomplete, or inconsistent."""


def _value_type(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, (float, Decimal)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, list):
        return "array"
    return "unsupported"


def _id_key(value: object) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return f"i:{value}"
    if isinstance(value, str) and value:
        integer = _integer_value(value)
        if integer is not None:
            return f"i:{integer}"
        return f"s:{value}"
    return None


def _integer_value(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _decimal_value(value: object) -> Decimal | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal) and value.is_finite():
        return value
    return None


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_declared_path(root: Path, raw_path: object) -> Path:
    if not isinstance(raw_path, str) or not raw_path:
        raise ProfileError("manifest path must be a non-empty string")
    if "\\" in raw_path:
        raise ProfileError("manifest paths must use POSIX separators")
    logical_path = PurePosixPath(raw_path)
    if logical_path.is_absolute() or any(part in {"", ".", ".."} for part in logical_path.parts):
        raise ProfileError("manifest path is not a normalized relative path")
    resolved_root = root.resolve()
    resolved_path = (resolved_root / Path(*logical_path.parts)).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ProfileError("manifest path escapes the source root") from exc
    return resolved_path


def _require_dict(value: object, context: str) -> JsonObject:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ProfileError(f"{context} must be an object with string keys")
    return cast(JsonObject, value)


def _require_list(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise ProfileError(f"{context} must be an array")
    return cast(list[object], value)


def _required_string(record: Mapping[str, object], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise ProfileError(f"{context}.{key} must be a non-empty string")
    return value


def _required_nonnegative_int(record: Mapping[str, object], key: str, context: str) -> int:
    value = record.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProfileError(f"{context}.{key} must be a non-negative integer")
    return value


@dataclass
class FieldStats:
    observations: int = 0
    nulls: int = 0
    types: Counter[str] = field(default_factory=Counter)

    def add(self, value: object) -> None:
        self.observations += 1
        value_type = _value_type(value)
        self.types[value_type] += 1
        if value is None:
            self.nulls += 1


@dataclass
class SchemaStats:
    records: int = 0
    fields: dict[str, FieldStats] = field(default_factory=dict)

    def add_record(self, record: object) -> None:
        self.records += 1
        self._visit("$", record, 0)

    def _visit(self, path: str, value: object, depth: int) -> None:
        if depth > MAX_SCHEMA_DEPTH:
            return
        if path not in self.fields:
            if len(self.fields) >= MAX_SCHEMA_PATHS:
                raise ProfileError("schema path limit exceeded")
            self.fields[path] = FieldStats()
        self.fields[path].add(value)
        if isinstance(value, Mapping):
            for key, child in value.items():
                if not isinstance(key, str):
                    raise ProfileError("JSON object key is not a string")
                # Numeric object keys are record identifiers (for example teamsData keys).
                # Aggregate them into one shape path instead of retaining raw IDs or growing
                # schema memory in proportion to record count.
                schema_key = "*" if _integer_value(key) is not None else key
                self._visit(f"{path}.{schema_key}", child, depth + 1)
        elif isinstance(value, list):
            child_path = f"{path}[]"
            for child in value:
                self._visit(child_path, child, depth + 1)


@dataclass
class CsvColumnStats:
    present: int = 0
    empty: int = 0
    lexical_types: Counter[str] = field(default_factory=Counter)

    def add(self, value: str | None) -> None:
        if value is None:
            return
        self.present += 1
        if not value:
            self.empty += 1
            self.lexical_types["empty"] += 1
        elif _integer_value(value) is not None:
            self.lexical_types["integer"] += 1
        else:
            self.lexical_types["string"] += 1


@dataclass
class CsvStats:
    rows: int = 0
    columns: dict[str, CsvColumnStats] = field(default_factory=dict)


@dataclass
class NumericRange:
    count: int = 0
    missing_or_invalid: int = 0
    minimum: Decimal | None = None
    maximum: Decimal | None = None

    def add(self, value: object) -> None:
        number = _decimal_value(value)
        if number is None:
            self.missing_or_invalid += 1
            return
        self.count += 1
        self.minimum = number if self.minimum is None else min(self.minimum, number)
        self.maximum = number if self.maximum is None else max(self.maximum, number)


@dataclass
class ProfileState:
    schemas: dict[str, SchemaStats] = field(
        default_factory=lambda: {
            "competitions": SchemaStats(),
            "teams": SchemaStats(),
            "players": SchemaStats(),
            "matches": SchemaStats(),
            "events": SchemaStats(),
        }
    )
    csv_schemas: dict[str, CsvStats] = field(default_factory=dict)
    competition_ids: set[str] = field(default_factory=set)
    team_ids: set[str] = field(default_factory=set)
    player_ids: set[str] = field(default_factory=set)
    match_ids: set[str] = field(default_factory=set)
    event_map_ids: set[int] = field(default_factory=set)
    subevent_map_ids: set[int] = field(default_factory=set)
    tag_map_ids: set[int] = field(default_factory=set)
    relation_counts: Counter[str] = field(default_factory=Counter)
    period_counts: Counter[str] = field(default_factory=Counter)
    event_seconds: dict[str, NumericRange] = field(default_factory=dict)
    event_seconds_max_scale: int = 0
    match_period_maximum: dict[tuple[str, str], Decimal] = field(default_factory=dict)
    substitution_minutes: NumericRange = field(default_factory=NumericRange)
    duration_types: Counter[str] = field(default_factory=Counter)
    duration_categories: Counter[str] = field(default_factory=Counter)
    match_dateutc_types: Counter[str] = field(default_factory=Counter)
    dateutc_parseable: int = 0
    dateutc_unparseable: int = 0
    substitution_shapes: Counter[str] = field(default_factory=Counter)
    literal_null_string_substitutions: int = 0
    member_counts: dict[str, int] = field(default_factory=dict)
    match_member_names: dict[str, str] = field(default_factory=dict)
    event_member_names: dict[str, str] = field(default_factory=dict)
    match_ids_by_partition: dict[str, set[str]] = field(default_factory=dict)
    event_match_ids_by_partition: dict[str, set[str]] = field(default_factory=dict)
    match_partition_by_id: dict[str, str] = field(default_factory=dict)
    match_team_ids: dict[str, set[str]] = field(default_factory=dict)
    admitted_competition_ids: set[str] = field(default_factory=set)
    admitted_team_ids: set[str] = field(default_factory=set)
    event_record_ids: set[int] = field(default_factory=set)
    event_record_duplicates: int = 0
    nonzero_player_match_pairs: set[tuple[str, str]] = field(default_factory=set)
    matches_with_nonzero_event_player: set[str] = field(default_factory=set)
    position_cardinalities: Counter[int] = field(default_factory=Counter)
    coordinate_ranges: dict[str, NumericRange] = field(
        default_factory=lambda: {"x": NumericRange(), "y": NumericRange()}
    )
    coordinate_out_of_range: Counter[str] = field(default_factory=Counter)
    match_member_count: int = 0
    event_member_count: int = 0


@dataclass(frozen=True)
class DeclaredFile:
    logical_name: str
    path: Path
    sha256: str
    size_bytes: int
    declared_path: str = ""


@dataclass(frozen=True)
class Completion:
    raw: JsonObject
    digest: str
    direct: dict[str, DeclaredFile]
    admitted: tuple[tuple[str, DeclaredFile], ...]
    excluded_count: int


def _declared_file(
    root: Path,
    record: Mapping[str, object],
    *,
    path_key: str,
    context: str,
) -> DeclaredFile:
    logical_name = _required_string(record, "name", context)
    declared_path = _required_string(record, path_key, context)
    path = _safe_declared_path(root, declared_path)
    sha256 = _required_string(record, "sha256", context)
    if len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
        raise ProfileError(f"{context}.sha256 is not a lowercase SHA-256 digest")
    size_bytes = _required_nonnegative_int(record, "size_bytes", context)
    return DeclaredFile(logical_name, path, sha256, size_bytes, declared_path)


def load_completion(root: Path, expected_digest: str) -> Completion:
    manifest_path = root / "completion-manifest.json"
    if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ProfileError("completion manifest exceeds bounded parser limit")
    manifest_bytes = manifest_path.read_bytes()
    digest = _sha256_bytes(manifest_bytes)
    if digest != expected_digest:
        raise ProfileError(
            f"completion manifest SHA-256 mismatch: expected {expected_digest}, measured {digest}"
        )
    try:
        raw_value = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProfileError("completion manifest is not valid UTF-8 JSON") from exc
    raw = _require_dict(raw_value, "completion manifest")
    if raw.get("state") != "complete":
        raise ProfileError("completion manifest state is not complete")

    direct: dict[str, DeclaredFile] = {}
    for index, value in enumerate(_require_list(raw.get("objects"), "completion manifest.objects")):
        record = _require_dict(value, f"objects[{index}]")
        declared = _declared_file(root, record, path_key="object_path", context=f"objects[{index}]")
        if declared.logical_name in direct:
            raise ProfileError(f"duplicate object name: {declared.logical_name}")
        direct[declared.logical_name] = declared

    admitted: list[tuple[str, DeclaredFile]] = []
    admitted_paths: set[Path] = set()
    for index, value in enumerate(
        _require_list(
            raw.get("admitted_archive_members"),
            "completion manifest.admitted_archive_members",
        )
    ):
        record = _require_dict(value, f"admitted_archive_members[{index}]")
        archive_name = _required_string(
            record, "archive_name", f"admitted_archive_members[{index}]"
        )
        declared = _declared_file(
            root,
            record,
            path_key="member_path",
            context=f"admitted_archive_members[{index}]",
        )
        if declared.path in admitted_paths:
            raise ProfileError(f"duplicate admitted member path: {declared.logical_name}")
        admitted_paths.add(declared.path)
        admitted.append((archive_name, declared))

    excluded = _require_list(
        raw.get("scope_excluded_archive_members"),
        "completion manifest.scope_excluded_archive_members",
    )
    return Completion(raw, digest, direct, tuple(admitted), len(excluded))


def _verify_digest_and_size(
    declared: DeclaredFile, measured_digest: str, measured_size: int
) -> None:
    if measured_size != declared.size_bytes:
        raise ProfileError(
            f"declared file size mismatch for {declared.logical_name}: "
            f"expected {declared.size_bytes}, measured {measured_size}"
        )
    if measured_digest != declared.sha256:
        raise ProfileError(f"declared file SHA-256 mismatch for {declared.logical_name}")


def iter_json_array(
    declared: DeclaredFile,
    *,
    chunk_bytes: int = CHUNK_BYTES,
    max_buffer_chars: int = MAX_JSON_BUFFER_CHARS,
) -> Iterator[object]:
    """Yield one top-level array item at a time while hashing the declared file."""
    if chunk_bytes <= 0 or max_buffer_chars <= 0:
        raise ValueError("streaming limits must be positive")
    decoder = codecs.getincrementaldecoder("utf-8")()
    json_decoder = json.JSONDecoder(parse_float=Decimal)
    digest = hashlib.sha256()
    measured_size = 0
    buffer = ""
    position = 0
    eof = False

    with declared.path.open("rb") as source:

        def fill() -> bool:
            nonlocal buffer, eof, measured_size
            if eof:
                return False
            raw_chunk = source.read(chunk_bytes)
            if raw_chunk:
                digest.update(raw_chunk)
                measured_size += len(raw_chunk)
                try:
                    buffer += decoder.decode(raw_chunk)
                except UnicodeDecodeError as exc:
                    raise ProfileError(f"{declared.logical_name} is not valid UTF-8") from exc
                if len(buffer) - position > max_buffer_chars:
                    raise ProfileError(
                        f"JSON item exceeds bounded parser limit in {declared.logical_name}"
                    )
                return True
            try:
                buffer += decoder.decode(b"", final=True)
            except UnicodeDecodeError as exc:
                raise ProfileError(f"{declared.logical_name} is not valid UTF-8") from exc
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
        if position >= len(buffer) or buffer[position] != "[":
            raise ProfileError(f"{declared.logical_name} must contain a top-level JSON array")
        position += 1
        expecting_value = True

        while True:
            skip_space()
            if position >= len(buffer):
                raise ProfileError(f"truncated JSON array in {declared.logical_name}")
            if expecting_value and buffer[position] == "]":
                position += 1
                break
            if not expecting_value:
                if buffer[position] == ",":
                    position += 1
                    expecting_value = True
                    continue
                if buffer[position] == "]":
                    position += 1
                    break
                raise ProfileError(f"invalid JSON array separator in {declared.logical_name}")

            while True:
                try:
                    value, end = json_decoder.raw_decode(buffer, position)
                except json.JSONDecodeError as exc:
                    if eof:
                        raise ProfileError(
                            f"invalid JSON array item in {declared.logical_name}"
                        ) from exc
                    if not fill() and position >= len(buffer):
                        raise ProfileError(
                            f"truncated JSON array item in {declared.logical_name}"
                        ) from exc
                    continue
                position = end
                break
            yield value
            expecting_value = False
            if position > chunk_bytes:
                buffer = buffer[position:]
                position = 0

        while not eof:
            fill()
        if buffer[position:].strip():
            raise ProfileError(f"trailing content after JSON array in {declared.logical_name}")

    _verify_digest_and_size(declared, digest.hexdigest(), measured_size)


def _read_verified_csv(
    declared: DeclaredFile,
    consume_row: Callable[[Mapping[str, str | None]], None],
) -> CsvStats:
    if declared.size_bytes > MAX_CSV_BYTES:
        raise ProfileError(f"{declared.logical_name} exceeds bounded CSV parser limit")
    digest = hashlib.sha256()
    measured_size = 0
    raw_chunks: list[bytes] = []
    with declared.path.open("rb") as source:
        while chunk := source.read(CHUNK_BYTES):
            digest.update(chunk)
            measured_size += len(chunk)
            raw_chunks.append(chunk)
    _verify_digest_and_size(declared, digest.hexdigest(), measured_size)
    try:
        text = b"".join(raw_chunks).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ProfileError(f"{declared.logical_name} is not valid UTF-8 CSV") from exc

    rows = csv.DictReader(text.splitlines())
    if rows.fieldnames is None or len(set(rows.fieldnames)) != len(rows.fieldnames):
        raise ProfileError(f"{declared.logical_name} has missing or duplicate CSV headers")
    stats = CsvStats(columns={name: CsvColumnStats() for name in rows.fieldnames})
    for row in rows:
        if None in row:
            raise ProfileError(f"{declared.logical_name} has a row wider than its header")
        stats.rows += 1
        for name, column_stats in stats.columns.items():
            column_stats.add(row.get(name))
        consume_row(row)
    return stats


def _record_id(target: set[str], value: object) -> None:
    key = _id_key(value)
    if key is not None:
        if key not in target and len(target) >= MAX_DISTINCT_IDS:
            raise ProfileError("distinct ID limit exceeded")
        target.add(key)


def _mapped_relation(
    counts: Counter[str],
    prefix: str,
    value: object,
    known: set[str],
    *,
    zero_is_separate: bool = False,
) -> None:
    counts[f"{prefix}.observed"] += 1
    key = _id_key(value)
    if key is None:
        counts[f"{prefix}.invalid_or_missing"] += 1
    elif zero_is_separate and key == "i:0":
        counts[f"{prefix}.zero"] += 1
    elif key in known:
        counts[f"{prefix}.mapped"] += 1
    else:
        counts[f"{prefix}.unmapped"] += 1


def _consume_entity(state: ProfileState, dataset: str, value: object) -> None:
    record = _require_dict(value, f"{dataset} record")
    state.schemas[dataset].add_record(record)
    target = {
        "competitions": state.competition_ids,
        "teams": state.team_ids,
        "players": state.player_ids,
    }[dataset]
    _record_id(target, record.get("wyId"))


def _formation_rows(value: object, name: str, counts: Counter[str]) -> list[JsonObject]:
    if value is None:
        return []
    if not isinstance(value, list):
        counts[f"{name}.invalid"] += 1
        return []
    rows: list[JsonObject] = []
    for item in value:
        if isinstance(item, dict) and all(isinstance(key, str) for key in item):
            rows.append(cast(JsonObject, item))
        else:
            counts[f"{name}.invalid"] += 1
    counts[f"{name}.rows"] += len(rows)
    return rows


def _partition_key(logical_name: str, prefix: str) -> str:
    marker = f"{prefix}_"
    if not logical_name.startswith(marker) or not logical_name.endswith(".json"):
        raise ProfileError(f"unexpected admitted {prefix} member name: {logical_name}")
    partition = logical_name[len(marker) : -len(".json")]
    if not partition:
        raise ProfileError(f"empty partition in admitted member name: {logical_name}")
    return partition


def _consume_match(state: ProfileState, value: object, partition: str) -> None:
    record = _require_dict(value, "match record")
    state.schemas["matches"].add_record(record)
    match_key = _id_key(record.get("wyId"))
    if match_key is not None and match_key in state.match_ids:
        state.relation_counts["match.wyId.duplicates"] += 1
    _record_id(state.match_ids, record.get("wyId"))
    if match_key is not None:
        state.match_ids_by_partition.setdefault(partition, set()).add(match_key)
        existing_partition = state.match_partition_by_id.get(match_key)
        if existing_partition is not None and existing_partition != partition:
            state.relation_counts["match.partition.duplicates"] += 1
        state.match_partition_by_id[match_key] = partition

    competition_key = _id_key(record.get("competitionId"))
    if competition_key is not None:
        state.admitted_competition_ids.add(competition_key)
    _mapped_relation(
        state.relation_counts,
        "match.competitionId",
        record.get("competitionId"),
        state.competition_ids,
    )
    duration = record.get("duration")
    state.duration_types[_value_type(duration)] += 1
    duration_category = duration if isinstance(duration, str) else f"<{_value_type(duration)}>"
    if (
        duration_category not in state.duration_categories
        and len(state.duration_categories) >= MAX_DURATION_CATEGORIES
    ):
        raise ProfileError("duration category limit exceeded")
    state.duration_categories[duration_category] += 1
    dateutc = record.get("dateutc")
    state.match_dateutc_types[_value_type(dateutc)] += 1
    if isinstance(dateutc, str):
        try:
            parsed_dateutc = datetime.strptime(dateutc, DATEUTC_FORMAT)
        except ValueError:
            state.dateutc_unparseable += 1
        else:
            if parsed_dateutc.strftime(DATEUTC_FORMAT) == dateutc:
                state.dateutc_parseable += 1
            else:
                state.dateutc_unparseable += 1
    else:
        state.dateutc_unparseable += 1

    teams_data = record.get("teamsData")
    if not isinstance(teams_data, Mapping):
        state.relation_counts["match.teamsData.invalid_or_missing"] += 1
        if match_key is not None:
            state.match_team_ids[match_key] = set()
        return
    state.relation_counts["match.teamsData.matches_present"] += 1
    if len(teams_data) != 2:
        state.relation_counts["match.teamsData.not_two_entries"] += 1
    teams_for_match: set[str] = set()
    for team_key, raw_team in teams_data.items():
        state.relation_counts["match.teamsData.team_entries"] += 1
        _mapped_relation(
            state.relation_counts,
            "match.teamsData.key",
            team_key,
            state.team_ids,
        )
        if not isinstance(raw_team, Mapping):
            state.relation_counts["match.teamsData.invalid_team_entry"] += 1
            continue
        team_id_key = _id_key(raw_team.get("teamId"))
        if _id_key(team_key) != team_id_key:
            state.relation_counts["match.teamsData.key_teamId_mismatch"] += 1
        if team_id_key is not None:
            teams_for_match.add(team_id_key)
            state.admitted_team_ids.add(team_id_key)
        _mapped_relation(
            state.relation_counts,
            "match.teamsData.teamId",
            raw_team.get("teamId"),
            state.team_ids,
        )
        formation = raw_team.get("formation")
        if not isinstance(formation, Mapping):
            state.relation_counts["match.formation.invalid_or_missing"] += 1
            continue
        state.relation_counts["match.formation.present"] += 1
        for name in ("lineup", "bench"):
            for row in _formation_rows(
                formation.get(name), f"match.formation.{name}", state.relation_counts
            ):
                _mapped_relation(
                    state.relation_counts,
                    f"match.formation.{name}.playerId",
                    row.get("playerId"),
                    state.player_ids,
                )
        substitutions = formation.get("substitutions")
        substitution_shape = _value_type(substitutions)
        state.substitution_shapes[substitution_shape] += 1
        if substitutions == "null":
            state.literal_null_string_substitutions += 1
        for row in _formation_rows(
            substitutions,
            "match.formation.substitutions",
            state.relation_counts,
        ):
            state.substitution_minutes.add(row.get("minute"))
            for key in ("playerIn", "playerOut"):
                _mapped_relation(
                    state.relation_counts,
                    f"match.formation.substitutions.{key}",
                    row.get(key),
                    state.player_ids,
                )
    if match_key is not None:
        state.match_team_ids[match_key] = teams_for_match


def _period_key(value: object) -> str:
    if isinstance(value, str) and value:
        return value
    return f"<{_value_type(value)}>"


def _consume_event(state: ProfileState, value: object, partition: str) -> None:
    record = _require_dict(value, "event record")
    state.schemas["events"].add_record(record)
    event_record_id = _integer_value(record.get("id"))
    if event_record_id is None:
        state.relation_counts["event.id.invalid_or_missing"] += 1
    elif event_record_id in state.event_record_ids:
        state.event_record_duplicates += 1
    else:
        if len(state.event_record_ids) >= MAX_EVENT_RECORD_IDS:
            raise ProfileError("event record ID limit exceeded")
        state.event_record_ids.add(event_record_id)

    match_key = _id_key(record.get("matchId"))
    if match_key is not None:
        state.event_match_ids_by_partition.setdefault(partition, set()).add(match_key)
    if match_key is None or state.match_partition_by_id.get(match_key) != partition:
        state.relation_counts["event.member_partition_mismatch"] += 1
    _mapped_relation(
        state.relation_counts,
        "event.matchId",
        record.get("matchId"),
        state.match_ids,
    )
    _mapped_relation(
        state.relation_counts,
        "event.teamId",
        record.get("teamId"),
        state.team_ids,
        zero_is_separate=True,
    )
    team_key = _id_key(record.get("teamId"))
    if (
        match_key is None
        or team_key is None
        or team_key not in state.match_team_ids.get(match_key, set())
    ):
        state.relation_counts["event.teamId.not_in_match_teamsData"] += 1
    _mapped_relation(
        state.relation_counts,
        "event.playerId",
        record.get("playerId"),
        state.player_ids,
        zero_is_separate=True,
    )
    player_key = _id_key(record.get("playerId"))
    if player_key is not None and player_key != "i:0" and match_key is not None:
        pair = (match_key, player_key)
        if (
            pair not in state.nonzero_player_match_pairs
            and len(state.nonzero_player_match_pairs) >= MAX_PLAYER_MATCH_PAIRS
        ):
            raise ProfileError("non-zero player-match pair limit exceeded")
        state.nonzero_player_match_pairs.add(pair)
        state.matches_with_nonzero_event_player.add(match_key)

    event_id = _integer_value(record.get("eventId"))
    state.relation_counts["event.eventId.observed"] += 1
    if event_id is None:
        state.relation_counts["event.eventId.invalid_or_missing"] += 1
    elif event_id in state.event_map_ids:
        state.relation_counts["event.eventId.mapped"] += 1
    else:
        state.relation_counts["event.eventId.unmapped"] += 1

    subevent_id = _integer_value(record.get("subEventId"))
    state.relation_counts["event.subEventId.observed"] += 1
    if subevent_id is None:
        state.relation_counts["event.subEventId.invalid_or_missing"] += 1
    elif subevent_id in state.subevent_map_ids:
        state.relation_counts["event.subEventId.mapped"] += 1
    else:
        state.relation_counts["event.subEventId.unmapped"] += 1

    tags = record.get("tags")
    if not isinstance(tags, list):
        state.relation_counts["event.tags.invalid_or_missing"] += 1
    else:
        state.relation_counts["event.tags.arrays"] += 1
        for tag in tags:
            state.relation_counts["event.tags.entries"] += 1
            tag_id = _integer_value(tag.get("id")) if isinstance(tag, Mapping) else None
            if tag_id is None:
                state.relation_counts["event.tags.invalid_id"] += 1
            elif tag_id in state.tag_map_ids:
                state.relation_counts["event.tags.mapped"] += 1
            else:
                state.relation_counts["event.tags.unmapped"] += 1

    period = _period_key(record.get("matchPeriod"))
    if period not in state.period_counts and len(state.period_counts) >= MAX_PERIOD_VALUES:
        raise ProfileError("matchPeriod category limit exceeded")
    state.period_counts[period] += 1
    event_second = record.get("eventSec")
    state.event_seconds.setdefault(period, NumericRange()).add(event_second)
    second_number = _decimal_value(event_second)
    if isinstance(event_second, Decimal):
        exponent = event_second.as_tuple().exponent
        if isinstance(exponent, int):
            state.event_seconds_max_scale = max(
                state.event_seconds_max_scale,
                max(0, -exponent),
            )
    if second_number is not None and match_key is not None:
        key = (match_key, period)
        previous = state.match_period_maximum.get(key)
        if previous is None and len(state.match_period_maximum) >= MAX_MATCH_PERIOD_PAIRS:
            raise ProfileError("match-period aggregate limit exceeded")
        if previous is None or second_number > previous:
            state.match_period_maximum[key] = second_number

    positions = record.get("positions")
    if not isinstance(positions, list):
        state.relation_counts["event.positions.invalid_or_missing"] += 1
        return
    state.position_cardinalities[len(positions)] += 1
    for position in positions:
        if not isinstance(position, Mapping):
            state.relation_counts["event.positions.invalid_item"] += 1
            continue
        for axis in ("x", "y"):
            coordinate = position.get(axis)
            state.coordinate_ranges[axis].add(coordinate)
            numeric_coordinate = _decimal_value(coordinate)
            if numeric_coordinate is None:
                state.relation_counts[f"event.positions.{axis}.invalid_or_missing"] += 1
            elif numeric_coordinate < 0 or numeric_coordinate > 100:
                state.coordinate_out_of_range[axis] += 1


def _consume_event_mapping(state: ProfileState, row: Mapping[str, str | None]) -> None:
    event_id = _integer_value(row.get("event"))
    subevent_id = _integer_value(row.get("subevent"))
    if event_id is not None:
        state.event_map_ids.add(event_id)
    if subevent_id is not None:
        state.subevent_map_ids.add(subevent_id)


def _consume_tag_mapping(state: ProfileState, row: Mapping[str, str | None]) -> None:
    tag_id = _integer_value(row.get("Tag"))
    if tag_id is not None:
        state.tag_map_ids.add(tag_id)


def _required_direct(completion: Completion, logical_name: str) -> DeclaredFile:
    declared = completion.direct.get(logical_name)
    if declared is None:
        raise ProfileError(f"completion manifest does not declare required object {logical_name}")
    return declared


def profile_completion(completion: Completion) -> ProfileState:
    state = ProfileState()

    mapping_files = {
        "eventid2name.csv": (
            "event mapping",
            lambda row: _consume_event_mapping(state, row),
        ),
        "tags2name.csv": ("tag mapping", lambda row: _consume_tag_mapping(state, row)),
    }
    for logical_name, (dataset_name, consumer) in mapping_files.items():
        state.csv_schemas[dataset_name] = _read_verified_csv(
            _required_direct(completion, logical_name),
            consumer,
        )

    for logical_name, dataset in (
        ("competitions.json", "competitions"),
        ("teams.json", "teams"),
        ("players.json", "players"),
    ):
        for value in iter_json_array(_required_direct(completion, logical_name)):
            _consume_entity(state, dataset, value)

    matches: list[DeclaredFile] = []
    events: list[DeclaredFile] = []
    for archive_name, declared in completion.admitted:
        if archive_name == "matches.zip":
            matches.append(declared)
        elif archive_name == "events.zip":
            events.append(declared)
        else:
            raise ProfileError(
                f"admitted member {declared.logical_name} has unsupported archive declaration"
            )
    if not matches or not events:
        raise ProfileError("completion manifest must admit both match and event members")

    state.match_member_count = len(matches)
    for declared in matches:
        partition = _partition_key(declared.logical_name, "matches")
        if partition in state.match_member_names:
            raise ProfileError(f"duplicate admitted match partition: {partition}")
        state.match_member_names[partition] = declared.logical_name
        count = 0
        for value in iter_json_array(declared):
            _consume_match(state, value, partition)
            count += 1
        state.member_counts[declared.logical_name] = count

    state.event_member_count = len(events)
    for declared in events:
        partition = _partition_key(declared.logical_name, "events")
        if partition in state.event_member_names:
            raise ProfileError(f"duplicate admitted event partition: {partition}")
        state.event_member_names[partition] = declared.logical_name
        count = 0
        for value in iter_json_array(declared):
            _consume_event(state, value, partition)
            count += 1
        state.member_counts[declared.logical_name] = count
    return state


def _format_types(types: Counter[str]) -> str:
    return ", ".join(f"{name}:{types[name]}" for name in sorted(types))


def _format_number(value: Decimal | None) -> str:
    if value is None:
        return "not observed"
    return format(value, "f")


def _escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> list[str]:
    lines = [
        "| " + " | ".join(_escape_cell(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(_escape_cell(cell) for cell in row) + " |" for row in rows)
    return lines


def _manifest_text(completion: Completion, section: str, key: str) -> str:
    nested = _require_dict(completion.raw.get(section), f"completion manifest.{section}")
    value = nested.get(key)
    return str(value) if value is not None else "not declared"


def _declared_inventory_rows(completion: Completion) -> list[list[object]]:
    opened_direct = {
        "competitions.json",
        "teams.json",
        "players.json",
        "eventid2name.csv",
        "tags2name.csv",
    }
    rows: list[list[object]] = []
    for declared in sorted(completion.direct.values(), key=lambda item: item.logical_name):
        profile_access = "opened" if declared.logical_name in opened_direct else "not opened"
        rows.append(
            [
                "completion source object",
                declared.logical_name,
                declared.declared_path,
                declared.size_bytes,
                declared.sha256,
                profile_access,
            ]
        )
    for archive_name, declared in sorted(
        completion.admitted,
        key=lambda item: (item[0], item[1].logical_name),
    ):
        rows.append(
            [
                f"separately durable admitted member of {archive_name}",
                declared.logical_name,
                declared.declared_path,
                declared.size_bytes,
                declared.sha256,
                "opened",
            ]
        )
    return rows


def _partition_rows(state: ProfileState) -> list[list[object]]:
    rows: list[list[object]] = []
    partitions = sorted(set(state.match_member_names) | set(state.event_member_names))
    for partition in partitions:
        match_ids = state.match_ids_by_partition.get(partition, set())
        event_match_ids = state.event_match_ids_by_partition.get(partition, set())
        rows.append(
            [
                partition,
                state.match_member_names.get(partition, "not admitted"),
                len(match_ids),
                state.event_member_names.get(partition, "not admitted"),
                len(event_match_ids),
                "equal" if match_ids == event_match_ids else "not equal",
            ]
        )
    return rows


def _relationship_rows(state: ProfileState) -> list[list[object]]:
    groups = (
        ("match.competitionId", "match competitionId → competitions.wyId"),
        ("match.teamsData.key", "teamsData key → teams.wyId"),
        ("match.teamsData.teamId", "teamsData teamId → teams.wyId"),
        ("event.matchId", "event matchId → matches.wyId"),
        ("event.teamId", "event teamId → teams.wyId"),
        ("event.playerId", "event playerId → players.wyId"),
        ("event.eventId", "event eventId → event mapping event"),
        ("event.subEventId", "event subEventId → event mapping subevent"),
    )
    rows: list[list[object]] = []
    for prefix, label in groups:
        rows.append(
            [
                label,
                state.relation_counts[f"{prefix}.observed"],
                state.relation_counts[f"{prefix}.mapped"],
                state.relation_counts[f"{prefix}.unmapped"],
                state.relation_counts[f"{prefix}.zero"],
                state.relation_counts[f"{prefix}.invalid_or_missing"],
            ]
        )
    rows.append(
        [
            "event tag id → tag mapping Tag",
            state.relation_counts["event.tags.entries"],
            state.relation_counts["event.tags.mapped"],
            state.relation_counts["event.tags.unmapped"],
            0,
            state.relation_counts["event.tags.invalid_id"],
        ]
    )
    for location in ("lineup", "bench"):
        prefix = f"match.formation.{location}.playerId"
        rows.append(
            [
                f"{location} playerId → players.wyId",
                state.relation_counts[f"{prefix}.observed"],
                state.relation_counts[f"{prefix}.mapped"],
                state.relation_counts[f"{prefix}.unmapped"],
                0,
                state.relation_counts[f"{prefix}.invalid_or_missing"],
            ]
        )
    for key in ("playerIn", "playerOut"):
        prefix = f"match.formation.substitutions.{key}"
        rows.append(
            [
                f"substitution {key} → players.wyId",
                state.relation_counts[f"{prefix}.observed"],
                state.relation_counts[f"{prefix}.mapped"],
                state.relation_counts[f"{prefix}.unmapped"],
                0,
                state.relation_counts[f"{prefix}.invalid_or_missing"],
            ]
        )
    return rows


def render_report(completion: Completion, state: ProfileState) -> bytes:
    lines = [
        "# W04 Wyscout v5 source schema profile",
        "",
        "> Measured aggregate evidence only. No raw records, player names, or inferred semantics.",
        "",
        "## Provenance and scope",
        "",
    ]
    lines.extend(
        _table(
            ("Evidence", "Measured/declaration value"),
            (
                ("source_id", completion.raw.get("source_id", "not declared")),
                ("completion state", completion.raw.get("state", "not declared")),
                ("classification", completion.raw.get("classification", "not declared")),
                ("licence_id", _manifest_text(completion, "licence", "licence_id")),
                ("completion manifest SHA-256", completion.digest),
                (
                    "source_available_at",
                    _manifest_text(completion, "acquisition", "source_available_at"),
                ),
                ("acquired_at", _manifest_text(completion, "acquisition", "acquired_at")),
                ("admitted archive-member paths profiled", len(completion.admitted)),
                ("scope-excluded archive entries not opened", completion.excluded_count),
                ("production source root", "data/source/wyscout/v5"),
                (
                    "production output",
                    "reports/phase-gates/W04/source-schema-profile.md",
                ),
                (
                    "direct objects opened",
                    "competitions.json; teams.json; players.json; eventid2name.csv; tags2name.csv",
                ),
            ),
        )
    )
    lines.extend(
        [
            "",
            "The profiler resolved source-data paths only from `object_path` or `member_path` "
            "values in the completion manifest. It has no ZIP-reading or network code. ZIP "
            "objects and scope-excluded entries were not opened.",
            "",
            "### Completion-declared durable inventory",
            "",
        ]
    )
    lines.extend(
        _table(
            (
                "Kind",
                "Logical name",
                "Completion-declared logical path",
                "Bytes",
                "SHA-256",
                "Profile access",
            ),
            _declared_inventory_rows(completion),
        )
    )
    lines.extend(
        [
            "",
            "Object size/digest rows above are completion declarations bound by the manifest "
            "SHA-256. Every opened direct object and durable admitted member was also verified "
            "during profiling. Archive objects were not opened.",
            "",
            "## Dataset counts",
            "",
        ]
    )
    count_rows: list[list[object]] = []
    for dataset in ("competitions", "teams", "players", "matches", "events"):
        count_rows.append([dataset, state.schemas[dataset].records])
    count_rows.extend(
        [
            ["match admitted members", state.match_member_count],
            ["event admitted members", state.event_member_count],
            ["event mapping CSV rows", state.csv_schemas["event mapping"].rows],
            ["tag mapping CSV rows", state.csv_schemas["tag mapping"].rows],
            ["distinct competition wyId values", len(state.competition_ids)],
            ["distinct team wyId values", len(state.team_ids)],
            ["distinct player wyId values", len(state.player_ids)],
            ["distinct match wyId values", len(state.match_ids)],
            [
                "distinct competition IDs referenced by admitted matches",
                len(state.admitted_competition_ids),
            ],
            [
                "distinct team IDs referenced by admitted matches",
                len(state.admitted_team_ids),
            ],
            ["distinct event record id values", len(state.event_record_ids)],
            ["duplicate event record id values", state.event_record_duplicates],
        ]
    )
    lines.extend(_table(("Dataset/evidence", "Count"), count_rows))
    lines.extend(["", "### Per-member row counts", ""])
    lines.extend(
        _table(
            ("Member", "Rows"),
            [[name, state.member_counts[name]] for name in sorted(state.member_counts)],
        )
    )
    lines.extend(["", "### Event-member to match-member partition equality", ""])
    lines.extend(
        _table(
            (
                "Partition",
                "Match member",
                "Distinct match wyId",
                "Event member",
                "Distinct event matchId",
                "Set relation",
            ),
            _partition_rows(state),
        )
    )

    lines.extend(["", "## Measured relationships", ""])
    lines.extend(
        _table(
            (
                "Relationship",
                "Observed",
                "Mapped",
                "Unmapped",
                "Zero-valued",
                "Invalid/missing",
            ),
            _relationship_rows(state),
        )
    )
    lines.extend(
        [
            "",
            "`Zero-valued` is reported separately where measured for event player/team IDs. "
            "No meaning is assigned to zero.",
            "",
            "### Match-bound and player-match aggregate evidence",
            "",
        ]
    )
    bound_rows: list[list[object]] = [
        [
            "matches with teamsData entry count other than two",
            state.relation_counts["match.teamsData.not_two_entries"],
        ],
        [
            "teamsData key/teamId mismatches",
            state.relation_counts["match.teamsData.key_teamId_mismatch"],
        ],
        [
            "event teamId not in referenced match teamsData",
            state.relation_counts["event.teamId.not_in_match_teamsData"],
        ],
        [
            "event/member match-partition mismatches",
            state.relation_counts["event.member_partition_mismatch"],
        ],
        ["duplicate match wyId values", state.relation_counts["match.wyId.duplicates"]],
        [
            "non-zero event player references",
            state.relation_counts["event.playerId.mapped"]
            + state.relation_counts["event.playerId.unmapped"],
        ],
        [
            "distinct non-zero event player-match pairs",
            len(state.nonzero_player_match_pairs),
        ],
        [
            "matches with at least one non-zero event player",
            len(state.matches_with_nonzero_event_player),
        ],
    ]
    lines.extend(_table(("Evidence", "Count"), bound_rows))
    lines.extend(
        [
            "",
            "Player-match pairs above are event-presence aggregates only. They do not establish "
            "lineup status, time played, role context, minutes, or per-90 eligibility.",
            "",
            "## Period, clock, and minutes evidence",
            "",
        ]
    )
    period_rows: list[list[object]] = []
    for period in sorted(state.period_counts):
        numeric = state.event_seconds[period]
        maxima = [
            maximum
            for (_match_id, match_period), maximum in state.match_period_maximum.items()
            if match_period == period
        ]
        period_rows.append(
            [
                period,
                state.period_counts[period],
                numeric.count,
                numeric.missing_or_invalid,
                _format_number(numeric.minimum),
                _format_number(numeric.maximum),
                len(maxima),
                _format_number(min(maxima) if maxima else None),
                _format_number(max(maxima) if maxima else None),
            ]
        )
    lines.extend(
        _table(
            (
                "matchPeriod aggregate",
                "Events",
                "Numeric eventSec",
                "Missing/invalid eventSec",
                "eventSec min",
                "eventSec max",
                "Match-period maxima count",
                "Min of maxima",
                "Max of maxima",
            ),
            period_rows,
        )
    )
    clock_rows: list[list[object]] = [
        ["match duration field types", _format_types(state.duration_types)],
        ["match dateutc field types", _format_types(state.match_dateutc_types)],
        ["dateutc values matching YYYY-MM-DD HH:MM:SS", state.dateutc_parseable],
        ["dateutc values not matching YYYY-MM-DD HH:MM:SS", state.dateutc_unparseable],
        ["maximum measured eventSec decimal scale", state.event_seconds_max_scale],
        [
            "formation structures present",
            state.relation_counts["match.formation.present"],
        ],
        ["lineup rows", state.relation_counts["match.formation.lineup.rows"]],
        ["bench rows", state.relation_counts["match.formation.bench.rows"]],
        [
            "substitution rows",
            state.relation_counts["match.formation.substitutions.rows"],
        ],
        ["numeric substitution minute values", state.substitution_minutes.count],
        [
            "missing/invalid substitution minute values",
            state.substitution_minutes.missing_or_invalid,
        ],
        ["substitution minute minimum", _format_number(state.substitution_minutes.minimum)],
        ["substitution minute maximum", _format_number(state.substitution_minutes.maximum)],
        [
            "literal-null-string substitution containers",
            state.literal_null_string_substitutions,
        ],
        ["exact period terminal supported", "no"],
        ["exact player minutes supported", "no"],
        ["per-90 denominator supported", "no"],
    ]
    for category in sorted(state.duration_categories):
        clock_rows.append([f"duration category {category}", state.duration_categories[category]])
    for shape in sorted(state.substitution_shapes):
        clock_rows.append(
            [f"substitution container shape {shape}", state.substitution_shapes[shape]]
        )
    lines.extend(["", *_table(("Evidence", "Measured value"), clock_rows)])
    lines.extend(
        [
            "",
            "The event maxima are observed lower-bound evidence only. They do not establish an "
            "exact period terminal, elapsed match duration, stoppage-time rule, period-start UTC, "
            "or player minutes. Consequently, player-minute and per-90 products remain "
            "unsupported and must stay suppressed.",
            "",
            "## Position cardinality and coordinate-domain evidence",
            "",
        ]
    )
    position_rows: list[list[object]] = [
        ["positions with one coordinate", state.position_cardinalities[1]],
        ["positions with two coordinates", state.position_cardinalities[2]],
        [
            "positions with other cardinality",
            sum(
                count
                for cardinality, count in state.position_cardinalities.items()
                if cardinality not in {1, 2}
            ),
        ],
        [
            "coordinate values outside inclusive 0..100",
            sum(state.coordinate_out_of_range.values()),
        ],
    ]
    lines.extend(_table(("Evidence", "Count"), position_rows))
    coordinate_rows: list[list[object]] = []
    for axis in ("x", "y"):
        coordinate_range = state.coordinate_ranges[axis]
        coordinate_rows.append(
            [
                axis,
                coordinate_range.count,
                coordinate_range.missing_or_invalid,
                _format_number(coordinate_range.minimum),
                _format_number(coordinate_range.maximum),
                state.coordinate_out_of_range[axis],
            ]
        )
    lines.extend(
        [
            "",
            *_table(
                (
                    "Axis",
                    "Numeric values",
                    "Missing/invalid",
                    "Lowest observed",
                    "Highest observed",
                    "Outside inclusive 0..100",
                ),
                coordinate_rows,
            ),
            "",
            "Out-of-range coordinates are retained as anomaly evidence. The profiler does not "
            "clamp, repair, or discard them.",
            "",
            "## CSV field shapes",
            "",
        ]
    )
    for dataset in ("event mapping", "tag mapping"):
        stats = state.csv_schemas[dataset]
        lines.extend([f"### {dataset}", ""])
        rows = [
            [
                column,
                column_stats.present,
                column_stats.empty,
                _format_types(column_stats.lexical_types),
            ]
            for column, column_stats in sorted(stats.columns.items())
        ]
        lines.extend(_table(("Column", "Present", "Empty", "Lexical shapes"), rows))
        lines.append("")

    lines.extend(["## JSON field presence and type shapes", ""])
    for dataset in ("competitions", "teams", "players", "matches", "events"):
        schema = state.schemas[dataset]
        lines.extend([f"### {dataset}", ""])
        schema_rows = [
            [path, stats.observations, stats.nulls, _format_types(stats.types)]
            for path, stats in sorted(schema.fields.items())
        ]
        lines.extend(_table(("Path", "Observations", "Nulls", "Measured types"), schema_rows))
        lines.append("")

    nullable_or_mixed: list[list[object]] = []
    for dataset in ("competitions", "teams", "players", "matches", "events"):
        for path, field_stats in sorted(state.schemas[dataset].fields.items()):
            non_null_types = {name for name in field_stats.types if name != "null"}
            if field_stats.nulls or len(non_null_types) > 1:
                nullable_or_mixed.append(
                    [
                        dataset,
                        path,
                        field_stats.observations,
                        field_stats.nulls,
                        _format_types(field_stats.types),
                    ]
                )
    lines.extend(["## Nullable and mixed-type evidence", ""])
    if nullable_or_mixed:
        lines.extend(
            _table(
                ("Dataset", "Path", "Observations", "Nulls", "Measured types"),
                nullable_or_mixed,
            )
        )
    else:
        lines.append("No null or mixed non-null type shapes were measured.")

    lines.extend(
        [
            "",
            "## Design-facing unknowns and limits",
            "",
            "- Identity: only within-snapshot ID membership was measured. No canonical "
            "cross-provider or cross-version identity evidence was profiled.",
            "- Possession: field/type and mapping evidence does not prove possession boundaries, "
            "ownership rules, or event-to-possession semantics.",
            "- Minutes: no exact period terminal or period-start UTC evidence was established. "
            "Lineup, bench, substitution-minute, duration-field, and eventSec aggregates are "
            "insufficient on their own to derive exact player minutes.",
            "- Coverage: counts apply only to completion-declared admitted members and the five "
            "direct objects opened above. Scope-excluded archive entries remain outside evidence.",
            "- Reconciliation: mapped, unmapped, zero-valued, and invalid/missing counts above "
            "are preserved separately; no repair, coercion, or semantic mapping was guessed.",
            "- Labels: mapping CSV structure and numeric-key membership were measured, but label "
            "text was not emitted into this report.",
            "",
            "## Reproduction",
            "",
            "```text",
            "uv run python scripts/profile_wyscout_v5.py --check",
            "```",
            "",
            "Production CLI source, output, and completion-digest overrides are rejected unless "
            "they resolve exactly to the repository-approved values recorded above. Internal "
            "fixture APIs remain parameterised for fabricated tests.",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def build_profile(source_root: Path, expected_completion_sha256: str) -> bytes:
    completion = load_completion(source_root, expected_completion_sha256)
    state = profile_completion(completion)
    return render_report(completion, state)


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
        help="must resolve to the repository-approved Wyscout v5 source root",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--expected-completion-sha256",
        default=EXPECTED_COMPLETION_SHA256,
        help="required SHA-256 binding for completion-manifest.json",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated bytes differ from the existing output; never write",
    )
    return parser.parse_args(argv)


def _validate_production_boundary(
    source_root: Path,
    output: Path,
    expected_digest: str,
) -> None:
    if source_root.resolve() != DEFAULT_SOURCE_ROOT:
        raise ProfileError(
            "production source root must be the repository-approved data/source/wyscout/v5 path"
        )
    if output.resolve() != DEFAULT_OUTPUT:
        raise ProfileError(
            "production output must be the repository-approved "
            "reports/phase-gates/W04/source-schema-profile.md path"
        )
    if expected_digest != EXPECTED_COMPLETION_SHA256:
        raise ProfileError("production completion SHA-256 override is not permitted")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_root = cast(Path, args.source_root)
    output = cast(Path, args.output)
    expected_digest = cast(str, args.expected_completion_sha256)
    try:
        _validate_production_boundary(source_root, output, expected_digest)
        report = build_profile(source_root, expected_digest)
        if cast(bool, args.check):
            try:
                existing = output.read_bytes()
            except FileNotFoundError:
                print(f"profile check failed: output does not exist: {output}", file=sys.stderr)
                return 1
            if existing != report:
                print(
                    f"profile check failed: generated bytes differ from {output}",
                    file=sys.stderr,
                )
                return 1
            print(f"profile check passed: {output}")
            return 0
        _atomic_write(output, report)
        print(f"wrote deterministic aggregate profile: {output}")
        return 0
    except (OSError, ProfileError, ValueError) as exc:
        print(f"profile failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

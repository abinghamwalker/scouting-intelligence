"""Deterministic full-population canonical projection for W09 research.

This producer consumes only a verified :mod:`scouting.sources.wyscout_historical`
adapter.  Provider payloads stop here: later feature, retrieval, serving and web
layers consume the emitted canonical Parquet and manifest only.
"""

from __future__ import annotations

import hashlib
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import cast

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]

from scouting.contracts.code_digest import governed_code_digest
from scouting.contracts.wyscout_data import SourceRecordKind, canonical_source_uuid
from scouting.contracts.wyscout_identity import WyscoutIdentityEntityKind
from scouting.sources.wyscout_historical import (
    ATTRIBUTION,
    EMPTY_SUB_EVENT_ID_SENTINEL_COUNT,
    EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS,
    IDENTITY_AVAILABLE_AT,
    PROJECT_ROOT,
    RIGHTS_CLASSIFICATION,
    SOURCE_AVAILABLE_AT,
    SOURCE_COMPLETION_INDEX_SHA256,
    SOURCE_MANIFEST_ID,
    SOURCE_MANIFEST_SHA256,
    HistoricalPartition,
    HistoricalPopulationAudit,
    WyscoutHistoricalAdapter,
    strict_decimal,
    strict_int,
)
from scouting.storage.formats import canonical_json_bytes
from scouting.storage.guarded import ArtifactReceipt, GuardedStorage

CANONICAL_SCHEMA_VERSION = "w09-historical-canonical-v1"
CANONICAL_MANIFEST_SCHEMA_VERSION = "w09-historical-canonical-manifest-v1"
CANONICAL_BUILDER_VERSION = "w09-full-canonical-build-02b-r6-unicode"
DEFAULT_FEATURE_CUTOFF = datetime(2026, 8, 5, tzinfo=UTC)
PRODUCTION_RESEARCH_ROOT = PROJECT_ROOT / "data/working/wyscout/v5/research"
PRODUCTION_RESEARCH_MANIFEST_ROOT = PROJECT_ROOT / "data/manifests/wyscout/v5/research"
_DISMISSAL_TAGS = frozenset({1701, 1703})
_COORDINATE_STATES = ("valid", "absent", "invalid_out_of_range")
_RETAINED_COORDINATE_ANOMALIES: dict[str, dict[int, tuple[tuple[int, str, int], ...]]] = {
    "Germany": {
        225765702: ((1, "y", 101),),
        225765704: ((0, "y", 101),),
    },
    "Italy": {
        198907641: ((0, "x", -1),),
    },
}
_RETAINED_NULL_SUBSTITUTION_SENTINELS: dict[str, frozenset[tuple[int, int]]] = {
    "England": frozenset(
        {
            (2500039, 1628),
            (2499990, 1609),
            (2499992, 1646),
            (2499980, 1628),
            (2499941, 1628),
        }
    ),
    "France": frozenset({(2501056, 3783)}),
}
_RETAINED_ZERO_PLAYER_IN_SUBSTITUTIONS: dict[str, frozenset[tuple[int, int, int, int]]] = {
    "Italy": frozenset(
        {
            (2576016, 3164, 333571, 90),
            (2576016, 3164, 37739, 90),
            (2575965, 3204, 93341, 56),
            (2575965, 3204, 20661, 62),
            (2575965, 3204, 226200, 88),
            (2575959, 3158, 23149, 74),
            (2575959, 3158, 44251, 81),
            (2575959, 3158, 3475, 84),
        }
    )
}


class HistoricalCanonicalBuildError(RuntimeError):
    """Raised when raw evidence cannot support one deterministic canonical build."""


@dataclass(frozen=True, slots=True)
class CanonicalArtifact:
    role: str
    relative_path: str
    row_count: int
    sha256: str
    size_bytes: int
    schema_version: str


@dataclass(frozen=True, slots=True)
class HistoricalCanonicalBuildResult:
    build_id: str
    canonical_root_relative_path: str
    manifest_relative_path: str
    manifest_sha256: str
    manifest_size_bytes: int
    artifacts: tuple[CanonicalArtifact, ...]
    manifest: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class HistoricalActionProjectionAudit:
    action_count: int
    empty_sub_event_id_sentinel_count: int
    empty_sub_event_id_sentinel_counts: Mapping[str, int]
    coordinate_evidence_state_counts: Mapping[str, Mapping[str, int]]
    invalid_coordinate_action_count: int
    invalid_coordinate_point_count: int


@dataclass(frozen=True, slots=True)
class HistoricalAppearanceProjectionAudit:
    appearance_count: int
    minute_evidence_counts: Mapping[str, int]
    substitution_unavailable_team_count: int
    substitution_unavailable_teams: Mapping[str, tuple[tuple[int, int], ...]]
    zero_player_in_substitution_count: int
    zero_player_in_substitutions: Mapping[str, tuple[tuple[int, int, int, int], ...]]


@dataclass(frozen=True, slots=True)
class _MatchContext:
    source_match_id: int
    match_id: str
    source_competition_id: int
    competition_id: str
    season_id: str
    match_start_utc: datetime
    partition: str
    source_member_path: str
    source_record_ordinal: int
    duration: str
    source_row: Mapping[str, object]


@dataclass(slots=True)
class _ActionEvidenceSummary:
    terminal_lower_bound: dict[int, Decimal]
    dismissals: dict[tuple[int, int], Decimal]
    empty_sub_event_id_sentinel_counts: dict[str, int]
    coordinate_evidence_state_counts: dict[str, dict[str, int]]
    invalid_coordinate_actions: dict[str, dict[int, tuple[tuple[int, str, int], ...]]]
    unresolved_action_rows: int = 0
    rejected_action_rows: int = 0


@dataclass(frozen=True, slots=True)
class _CanonicalPopulation:
    audit: HistoricalPopulationAudit
    competition_rows: list[dict[str, object]]
    team_rows: list[dict[str, object]]
    player_rows: list[dict[str, object]]
    match_rows: list[dict[str, object]]
    match_contexts: Mapping[int, _MatchContext]
    code_digest: str
    build_id: str


@dataclass(frozen=True, slots=True)
class _CanonicalMaterialization:
    artifacts: tuple[CanonicalArtifact, ...]
    action_summary: _ActionEvidenceSummary
    appearance_rows: list[dict[str, object]]
    minute_counts: Mapping[str, int]
    substitution_unavailable_teams: Mapping[str, set[tuple[int, int]]]
    zero_player_in_substitutions: Mapping[str, set[tuple[int, int, int, int]]]
    exclusions: list[dict[str, object]]
    canonical_counts: Mapping[str, int]
    source_counts: Mapping[str, int]
    empty_sub_event_id_sentinel_count: int
    invalid_coordinate_action_count: int
    invalid_coordinate_point_count: int


_STRING = pa.string()
_UTC_TS = pa.timestamp("us", tz="UTC")

_COMPETITION_SCHEMA = pa.schema(
    [
        pa.field("schema_version", _STRING, nullable=False),
        pa.field("source_competition_id", pa.int64(), nullable=False),
        pa.field("competition_id", _STRING, nullable=False),
        pa.field("name", _STRING, nullable=False),
        pa.field("area_name", _STRING, nullable=True),
        pa.field("format", _STRING, nullable=True),
        pa.field("competition_type", _STRING, nullable=True),
        pa.field("source_available_at", _UTC_TS, nullable=False),
        pa.field("identity_available_at", _UTC_TS, nullable=False),
        pa.field("feature_cutoff_ts", _UTC_TS, nullable=False),
    ]
)

_TEAM_SCHEMA = pa.schema(
    [
        pa.field("schema_version", _STRING, nullable=False),
        pa.field("source_team_id", pa.int64(), nullable=False),
        pa.field("team_id", _STRING, nullable=False),
        pa.field("name", _STRING, nullable=False),
        pa.field("official_name", _STRING, nullable=True),
        pa.field("city", _STRING, nullable=True),
        pa.field("area_name", _STRING, nullable=True),
        pa.field("source_available_at", _UTC_TS, nullable=False),
        pa.field("identity_available_at", _UTC_TS, nullable=False),
        pa.field("feature_cutoff_ts", _UTC_TS, nullable=False),
    ]
)

_PLAYER_SCHEMA = pa.schema(
    [
        pa.field("schema_version", _STRING, nullable=False),
        pa.field("source_player_id", pa.int64(), nullable=False),
        pa.field("player_id", _STRING, nullable=False),
        pa.field("display_name", _STRING, nullable=False),
        pa.field("first_name", _STRING, nullable=True),
        pa.field("middle_name", _STRING, nullable=True),
        pa.field("last_name", _STRING, nullable=True),
        pa.field("birth_date", _STRING, nullable=True),
        pa.field("position_code", _STRING, nullable=False),
        pa.field("foot", _STRING, nullable=True),
        pa.field("height_cm", pa.int16(), nullable=True),
        pa.field("weight_kg", pa.int16(), nullable=True),
        pa.field("source_available_at", _UTC_TS, nullable=False),
        pa.field("identity_available_at", _UTC_TS, nullable=False),
        pa.field("feature_cutoff_ts", _UTC_TS, nullable=False),
    ]
)

_MATCH_SCHEMA = pa.schema(
    [
        pa.field("schema_version", _STRING, nullable=False),
        pa.field("source_match_id", pa.int64(), nullable=False),
        pa.field("match_id", _STRING, nullable=False),
        pa.field("source_competition_id", pa.int64(), nullable=False),
        pa.field("competition_id", _STRING, nullable=False),
        pa.field("season_id", _STRING, nullable=False),
        pa.field("match_start_utc", _UTC_TS, nullable=False),
        pa.field("duration", _STRING, nullable=False),
        pa.field("status", _STRING, nullable=False),
        pa.field("label", _STRING, nullable=False),
        pa.field("venue", _STRING, nullable=True),
        pa.field("source_partition", _STRING, nullable=False),
        pa.field("source_member_path", _STRING, nullable=False),
        pa.field("source_record_ordinal", pa.int32(), nullable=False),
        pa.field("team_ids", pa.list_(_STRING), nullable=False),
        pa.field("source_available_at", _UTC_TS, nullable=False),
        pa.field("identity_available_at", _UTC_TS, nullable=False),
        pa.field("feature_cutoff_ts", _UTC_TS, nullable=False),
    ]
)

_ACTION_SCHEMA = pa.schema(
    [
        pa.field("schema_version", _STRING, nullable=False),
        pa.field("canonical_build_id", _STRING, nullable=False),
        pa.field("source_partition", _STRING, nullable=False),
        pa.field("source_member_path", _STRING, nullable=False),
        pa.field("source_member_sha256", _STRING, nullable=False),
        pa.field("source_record_ordinal", pa.int64(), nullable=False),
        pa.field("source_action_id", pa.int64(), nullable=False),
        pa.field("action_id", _STRING, nullable=False),
        pa.field("source_match_id", pa.int64(), nullable=False),
        pa.field("match_id", _STRING, nullable=False),
        pa.field("source_competition_id", pa.int64(), nullable=False),
        pa.field("competition_id", _STRING, nullable=False),
        pa.field("season_id", _STRING, nullable=False),
        pa.field("source_player_id", pa.int64(), nullable=False),
        pa.field("player_id", _STRING, nullable=True),
        pa.field("player_identity_state", _STRING, nullable=False),
        pa.field("source_team_id", pa.int64(), nullable=False),
        pa.field("team_id", _STRING, nullable=False),
        pa.field("event_id", pa.int32(), nullable=False),
        pa.field("event_name", _STRING, nullable=False),
        pa.field("sub_event_id", pa.int32(), nullable=True),
        pa.field("sub_event_name", _STRING, nullable=True),
        pa.field("period_code", _STRING, nullable=False),
        pa.field("period_rank", pa.int8(), nullable=False),
        pa.field("event_seconds", pa.float64(), nullable=False),
        pa.field("absolute_minute", pa.float64(), nullable=False),
        pa.field("occurrence_utc", _UTC_TS, nullable=False),
        pa.field("tag_ids", pa.list_(pa.int32()), nullable=False),
        pa.field("start_x", pa.int16(), nullable=True),
        pa.field("start_y", pa.int16(), nullable=True),
        pa.field("end_x", pa.int16(), nullable=True),
        pa.field("end_y", pa.int16(), nullable=True),
        pa.field("coordinate_evidence_state", _STRING, nullable=False),
        pa.field("source_available_at", _UTC_TS, nullable=False),
        pa.field("identity_available_at", _UTC_TS, nullable=False),
        pa.field("feature_cutoff_ts", _UTC_TS, nullable=False),
    ]
)

_APPEARANCE_SCHEMA = pa.schema(
    [
        pa.field("schema_version", _STRING, nullable=False),
        pa.field("canonical_build_id", _STRING, nullable=False),
        pa.field("source_match_id", pa.int64(), nullable=False),
        pa.field("match_id", _STRING, nullable=False),
        pa.field("source_competition_id", pa.int64(), nullable=False),
        pa.field("competition_id", _STRING, nullable=False),
        pa.field("season_id", _STRING, nullable=False),
        pa.field("source_team_id", pa.int64(), nullable=False),
        pa.field("team_id", _STRING, nullable=False),
        pa.field("source_player_id", pa.int64(), nullable=False),
        pa.field("player_id", _STRING, nullable=False),
        pa.field("lineup_role", _STRING, nullable=False),
        pa.field("minute_state", _STRING, nullable=False),
        pa.field("start_minute", pa.float64(), nullable=True),
        pa.field("end_minute", pa.float64(), nullable=True),
        pa.field("minutes", pa.float64(), nullable=True),
        pa.field("right_censored", pa.bool_(), nullable=False),
        pa.field("evidence_basis", _STRING, nullable=False),
        pa.field("match_start_utc", _UTC_TS, nullable=False),
        pa.field("source_partition", _STRING, nullable=False),
        pa.field("source_member_path", _STRING, nullable=False),
        pa.field("source_record_ordinal", pa.int32(), nullable=False),
        pa.field("source_available_at", _UTC_TS, nullable=False),
        pa.field("identity_available_at", _UTC_TS, nullable=False),
        pa.field("feature_cutoff_ts", _UTC_TS, nullable=False),
    ]
)

_EXCLUSION_SCHEMA = pa.schema(
    [
        pa.field("schema_version", _STRING, nullable=False),
        pa.field("source_player_id", pa.int64(), nullable=False),
        pa.field("canonical_player_id", _STRING, nullable=True),
        pa.field("identity_state", _STRING, nullable=False),
        pa.field("reason", _STRING, nullable=False),
        pa.field("source_reference_count", pa.int64(), nullable=False),
        pa.field("candidate_eligible", pa.bool_(), nullable=False),
        pa.field("identity_bundle_sha256", _STRING, nullable=False),
        pa.field("identity_available_at", _UTC_TS, nullable=False),
        pa.field("feature_cutoff_ts", _UTC_TS, nullable=False),
    ]
)


def _normalise_provider_text(value: str) -> str:
    """Decode one provider Unicode-escape layer without altering valid Unicode text."""

    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise HistoricalCanonicalBuildError("source text has an unpaired Unicode surrogate")

    pieces: list[str] = []
    cursor = 0
    while True:
        marker = value.find("\\u", cursor)
        if marker < 0:
            pieces.append(value[cursor:])
            break
        pieces.append(value[cursor:marker])
        token = value[marker + 2 : marker + 6]
        if (
            len(token) != 4
            or not token.isascii()
            or any(character not in "0123456789abcdefABCDEF" for character in token)
        ):
            raise HistoricalCanonicalBuildError("source text has a malformed Unicode escape")
        code_unit = int(token, 16)
        cursor = marker + 6
        if 0xD800 <= code_unit <= 0xDBFF:
            if not value.startswith("\\u", cursor):
                raise HistoricalCanonicalBuildError("source text has an unpaired Unicode surrogate")
            low_token = value[cursor + 2 : cursor + 6]
            if (
                len(low_token) != 4
                or not low_token.isascii()
                or any(character not in "0123456789abcdefABCDEF" for character in low_token)
            ):
                raise HistoricalCanonicalBuildError(
                    "source text has a malformed Unicode surrogate pair"
                )
            low_unit = int(low_token, 16)
            if not 0xDC00 <= low_unit <= 0xDFFF:
                raise HistoricalCanonicalBuildError(
                    "source text has an invalid Unicode surrogate pair"
                )
            code_point = 0x10000 + ((code_unit - 0xD800) << 10) + (low_unit - 0xDC00)
            pieces.append(chr(code_point))
            cursor += 6
        elif 0xDC00 <= code_unit <= 0xDFFF:
            raise HistoricalCanonicalBuildError("source text has an unpaired Unicode surrogate")
        else:
            pieces.append(chr(code_unit))
    normalised = unicodedata.normalize("NFC", "".join(pieces))
    if "\\u" in normalised:
        raise HistoricalCanonicalBuildError("source text has a nested Unicode escape")
    return normalised


def _required_text(value: object, *, context: str) -> str:
    if type(value) is not str:
        raise HistoricalCanonicalBuildError(f"{context} must be non-empty source text")
    normalised = _normalise_provider_text(value)
    if not normalised.strip():
        raise HistoricalCanonicalBuildError(f"{context} must be non-empty source text")
    return normalised


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise HistoricalCanonicalBuildError("optional source text has a non-string value")
    normalised = _normalise_provider_text(value)
    return normalised or None


def _nested_name(value: object) -> str | None:
    if type(value) is not dict:
        return None
    name = cast(dict[str, object], value).get("name")
    return _optional_text(name)


def _optional_int(value: object, *, context: str) -> int | None:
    if value is None:
        return None
    return strict_int(value, context=context)


def _position_code(row: Mapping[str, object]) -> str:
    role = row.get("role")
    if type(role) is not dict:
        raise HistoricalCanonicalBuildError("player role is absent")
    code = cast(dict[str, object], role).get("code2")
    if code not in {"GK", "DF", "MD", "FW"}:
        raise HistoricalCanonicalBuildError("player role code is unsupported")
    return code


def _parse_match_start(value: object) -> datetime:
    text = _required_text(value, context="match.dateutc")
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError as exc:
        raise HistoricalCanonicalBuildError("match.dateutc format is unsupported") from exc
    return parsed


def _parquet_bytes(rows: Sequence[Mapping[str, object]], schema: pa.Schema) -> bytes:
    if not rows:
        raise HistoricalCanonicalBuildError("canonical artifact cannot be empty")
    table = pa.Table.from_pylist([dict(row) for row in rows], schema=schema).combine_chunks()
    sink = pa.BufferOutputStream()
    pq.write_table(
        table,
        sink,
        version="2.6",
        row_group_size=65_536,
        compression="zstd",
        compression_level=9,
        data_page_version="2.0",
        use_dictionary=False,
        use_byte_stream_split=False,
        write_statistics=True,
        write_page_index=False,
        coerce_timestamps="us",
        allow_truncated_timestamps=False,
        store_schema=True,
    )
    return cast(bytes, sink.getvalue().to_pybytes())


def _parquet_batch_bytes(batches: Sequence[pa.RecordBatch], schema: pa.Schema) -> bytes:
    if not batches:
        raise HistoricalCanonicalBuildError("canonical action artifact cannot be empty")
    table = pa.Table.from_batches(batches, schema=schema)
    sink = pa.BufferOutputStream()
    pq.write_table(
        table,
        sink,
        version="2.6",
        row_group_size=65_536,
        compression="zstd",
        compression_level=9,
        data_page_version="2.0",
        use_dictionary=False,
        use_byte_stream_split=False,
        write_statistics=True,
        write_page_index=False,
        coerce_timestamps="us",
        allow_truncated_timestamps=False,
        store_schema=True,
    )
    return cast(bytes, sink.getvalue().to_pybytes())


def _canonical_code_digest() -> str:
    return governed_code_digest(
        (
            Path(__file__),
            Path(__file__).resolve().parents[2] / "sources/wyscout_historical.py",
        )
    )


def _build_id(
    *,
    adapter: WyscoutHistoricalAdapter,
    feature_cutoff_ts: datetime,
    code_digest: str,
) -> str:
    payload = canonical_json_bytes(
        {
            "adapter": "wyscout-figshare-v5-historical-v1",
            "builder_version": CANONICAL_BUILDER_VERSION,
            "canonical_schema_version": CANONICAL_SCHEMA_VERSION,
            "code_digest": code_digest,
            "feature_cutoff_ts": _utc_text(feature_cutoff_ts),
            "identity_bundle_sha256": adapter.identity.bundle_sha256,
            "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
            "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
            "test_fixture": adapter.is_test_fixture,
        }
    )
    return hashlib.sha256(payload).hexdigest()


def _common_clocks(feature_cutoff_ts: datetime) -> dict[str, datetime]:
    return {
        "source_available_at": SOURCE_AVAILABLE_AT,
        "identity_available_at": IDENTITY_AVAILABLE_AT,
        "feature_cutoff_ts": feature_cutoff_ts,
    }


def _utc_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _project_competitions(
    adapter: WyscoutHistoricalAdapter, feature_cutoff_ts: datetime
) -> tuple[list[dict[str, object]], dict[int, str]]:
    rows: list[dict[str, object]] = []
    names: dict[int, str] = {}
    clocks = _common_clocks(feature_cutoff_ts)
    for source in adapter.load_catalogue("competitions"):
        source_id = strict_int(source.get("wyId"), context="competition.wyId")
        canonical_id = adapter.identity.canonical_id(
            WyscoutIdentityEntityKind.COMPETITION, source_id
        )
        if canonical_id is None:
            raise HistoricalCanonicalBuildError("competition identity is unresolved")
        name = _required_text(source.get("name"), context="competition.name")
        names[source_id] = name
        rows.append(
            {
                "schema_version": CANONICAL_SCHEMA_VERSION,
                "source_competition_id": source_id,
                "competition_id": canonical_id,
                "name": name,
                "area_name": _nested_name(source.get("area")),
                "format": _optional_text(source.get("format")),
                "competition_type": _optional_text(source.get("type")),
                **clocks,
            }
        )
    rows.sort(key=lambda row: cast(str, row["competition_id"]))
    return rows, names


def _project_teams(
    adapter: WyscoutHistoricalAdapter, feature_cutoff_ts: datetime
) -> tuple[list[dict[str, object]], dict[int, str]]:
    rows: list[dict[str, object]] = []
    names: dict[int, str] = {}
    clocks = _common_clocks(feature_cutoff_ts)
    for source in adapter.load_catalogue("teams"):
        source_id = strict_int(source.get("wyId"), context="team.wyId")
        canonical_id = adapter.identity.canonical_id(WyscoutIdentityEntityKind.TEAM, source_id)
        if canonical_id is None:
            raise HistoricalCanonicalBuildError("team identity is unresolved")
        name = _required_text(source.get("name"), context="team.name")
        names[source_id] = name
        rows.append(
            {
                "schema_version": CANONICAL_SCHEMA_VERSION,
                "source_team_id": source_id,
                "team_id": canonical_id,
                "name": name,
                "official_name": _optional_text(source.get("officialName")),
                "city": _optional_text(source.get("city")),
                "area_name": _nested_name(source.get("area")),
                **clocks,
            }
        )
    rows.sort(key=lambda row: cast(str, row["team_id"]))
    return rows, names


def _project_players(
    adapter: WyscoutHistoricalAdapter, feature_cutoff_ts: datetime
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    clocks = _common_clocks(feature_cutoff_ts)
    for source in adapter.load_catalogue("players"):
        source_id = strict_int(source.get("wyId"), context="player.wyId")
        canonical_id = adapter.identity.canonical_id(WyscoutIdentityEntityKind.PLAYER, source_id)
        if canonical_id is None:
            raise HistoricalCanonicalBuildError("catalogue player identity is unresolved")
        display_name = (
            _optional_text(source.get("shortName"))
            or " ".join(
                value
                for value in (
                    _optional_text(source.get("firstName")),
                    _optional_text(source.get("lastName")),
                )
                if value is not None
            ).strip()
        )
        if not display_name:
            raise HistoricalCanonicalBuildError("player has no governed display name")
        rows.append(
            {
                "schema_version": CANONICAL_SCHEMA_VERSION,
                "source_player_id": source_id,
                "player_id": canonical_id,
                "display_name": display_name,
                "first_name": _optional_text(source.get("firstName")),
                "middle_name": _optional_text(source.get("middleName")),
                "last_name": _optional_text(source.get("lastName")),
                "birth_date": _optional_text(source.get("birthDate")),
                "position_code": _position_code(source),
                "foot": _optional_text(source.get("foot")),
                "height_cm": _optional_int(source.get("height"), context="player.height"),
                "weight_kg": _optional_int(source.get("weight"), context="player.weight"),
                **clocks,
            }
        )
    rows.sort(key=lambda row: cast(str, row["player_id"]))
    return rows


def _team_ids_from_match(
    adapter: WyscoutHistoricalAdapter, source: Mapping[str, object]
) -> list[str]:
    teams = source.get("teamsData")
    if type(teams) is not dict or len(teams) != 2:
        raise HistoricalCanonicalBuildError("match must contain exactly two team rows")
    result: list[str] = []
    for team_row in cast(dict[str, object], teams).values():
        if type(team_row) is not dict:
            raise HistoricalCanonicalBuildError("match team row is not an object")
        source_team_id = strict_int(
            cast(dict[str, object], team_row).get("teamId"), context="match.teamId"
        )
        team_id = adapter.identity.canonical_id(WyscoutIdentityEntityKind.TEAM, source_team_id)
        if team_id is None:
            raise HistoricalCanonicalBuildError("match team identity is unresolved")
        result.append(team_id)
    if len(set(result)) != 2:
        raise HistoricalCanonicalBuildError("match canonical team IDs are duplicated")
    return sorted(result)


def _project_matches(
    adapter: WyscoutHistoricalAdapter, feature_cutoff_ts: datetime
) -> tuple[list[dict[str, object]], dict[int, _MatchContext]]:
    rows: list[dict[str, object]] = []
    contexts: dict[int, _MatchContext] = {}
    clocks = _common_clocks(feature_cutoff_ts)
    for partition in adapter.partitions:
        for ordinal, source in enumerate(adapter.load_partition_matches(partition)):
            source_match_id = strict_int(source.get("wyId"), context="match.wyId")
            if source_match_id in contexts:
                raise HistoricalCanonicalBuildError("source match ID is duplicated")
            match_id = adapter.identity.canonical_id(
                WyscoutIdentityEntityKind.MATCH, source_match_id
            )
            source_competition_id = strict_int(
                source.get("competitionId"), context="match.competitionId"
            )
            competition_id = adapter.identity.canonical_id(
                WyscoutIdentityEntityKind.COMPETITION, source_competition_id
            )
            if match_id is None or competition_id is None:
                raise HistoricalCanonicalBuildError("match authority identity is unresolved")
            start = _parse_match_start(source.get("dateutc"))
            duration = _required_text(source.get("duration"), context="match.duration")
            status = _required_text(source.get("status"), context="match.status")
            if duration != "Regular" or status != "Played":
                raise HistoricalCanonicalBuildError(
                    "initial W09 window requires played regular matches"
                )
            context = _MatchContext(
                source_match_id=source_match_id,
                match_id=match_id,
                source_competition_id=source_competition_id,
                competition_id=competition_id,
                season_id=str(strict_int(source.get("seasonId"), context="match.seasonId")),
                match_start_utc=start,
                partition=partition.name,
                source_member_path=partition.match_relative_path,
                source_record_ordinal=ordinal,
                duration=duration,
                source_row=source,
            )
            contexts[source_match_id] = context
            rows.append(
                {
                    "schema_version": CANONICAL_SCHEMA_VERSION,
                    "source_match_id": source_match_id,
                    "match_id": match_id,
                    "source_competition_id": source_competition_id,
                    "competition_id": competition_id,
                    "season_id": context.season_id,
                    "match_start_utc": start,
                    "duration": duration,
                    "status": status,
                    "label": _required_text(source.get("label"), context="match.label"),
                    "venue": _optional_text(source.get("venue")),
                    "source_partition": partition.name.lower(),
                    "source_member_path": partition.match_relative_path,
                    "source_record_ordinal": ordinal,
                    "team_ids": _team_ids_from_match(adapter, source),
                    **clocks,
                }
            )
    rows.sort(key=lambda row: cast(str, row["match_id"]))
    return rows, contexts


def _tag_ids(value: object) -> list[int]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise HistoricalCanonicalBuildError("action tags are not an array")
    result: set[int] = set()
    for item in value:
        if type(item) is not dict:
            raise HistoricalCanonicalBuildError("action tag is not an object")
        result.add(strict_int(cast(dict[str, object], item).get("id"), context="tag.id"))
    return sorted(result)


def _positions(
    value: object,
) -> tuple[
    int | None,
    int | None,
    int | None,
    int | None,
    str,
    tuple[tuple[int, str, int], ...],
]:
    if value is None:
        return None, None, None, None, "absent", ()
    if not isinstance(value, (list, tuple)):
        raise HistoricalCanonicalBuildError("action positions are not an array")
    points = list(value)
    if len(points) > 2:
        raise HistoricalCanonicalBuildError("action positions contain more than two points")
    if not points:
        return None, None, None, None, "absent", ()

    invalid: list[tuple[int, str, int]] = []

    def point(index: int) -> tuple[int | None, int | None]:
        if index >= len(points):
            return None, None
        item = points[index]
        if type(item) is not dict:
            raise HistoricalCanonicalBuildError("action position is not an object")
        mapping = cast(dict[str, object], item)
        x = strict_int(mapping.get("x"), context="position.x")
        y = strict_int(mapping.get("y"), context="position.y")
        if not 0 <= x <= 100:
            invalid.append((index, "x", x))
        if not 0 <= y <= 100:
            invalid.append((index, "y", y))
        return x, y

    start_x, start_y = point(0)
    end_x, end_y = point(1)
    state = "invalid_out_of_range" if invalid else "valid"
    return start_x, start_y, end_x, end_y, state, tuple(invalid)


def _require_retained_coordinate_anomalies(summary: _ActionEvidenceSummary) -> None:
    actual = {
        partition: actions
        for partition, actions in summary.invalid_coordinate_actions.items()
        if actions
    }
    if actual != _RETAINED_COORDINATE_ANOMALIES:
        raise HistoricalCanonicalBuildError("retained coordinate anomaly reconciliation drifted")


def _period(period: object) -> tuple[str, int, Decimal]:
    if period == "1H":
        return "1H", 1, Decimal(0)
    if period == "2H":
        return "2H", 2, Decimal(45)
    raise HistoricalCanonicalBuildError("action period is outside admitted regular halves")


def _action_batches_for_partition(
    *,
    adapter: WyscoutHistoricalAdapter,
    partition: HistoricalPartition,
    match_contexts: Mapping[int, _MatchContext],
    build_id: str,
    feature_cutoff_ts: datetime,
    summary: _ActionEvidenceSummary,
) -> tuple[list[pa.RecordBatch], int]:
    batches: list[pa.RecordBatch] = []
    row_count = 0
    for batch in adapter.iter_partition_action_batches(partition):
        rows: list[dict[str, object]] = []
        for source in batch.to_pylist():
            was_empty_sub_event_id = source.get("adapter_sub_event_id_was_empty_string")
            if type(was_empty_sub_event_id) is not bool:
                raise HistoricalCanonicalBuildError(
                    "adapter subEventId sentinel evidence is absent"
                )
            summary.empty_sub_event_id_sentinel_counts[partition.name] = (
                summary.empty_sub_event_id_sentinel_counts.get(partition.name, 0)
                + int(was_empty_sub_event_id)
            )
            source_match_id = strict_int(source.get("matchId"), context="action.matchId")
            context = match_contexts.get(source_match_id)
            if context is None or context.partition != partition.name:
                raise HistoricalCanonicalBuildError("action match/partition is not canonical")
            source_player_id = strict_int(source.get("playerId"), context="action.playerId")
            player_id = adapter.identity.canonical_id(
                WyscoutIdentityEntityKind.PLAYER, source_player_id
            )
            if player_id is not None:
                identity_state = "resolved"
            elif source_player_id in adapter.identity.unresolved_player_source_ids:
                identity_state = "review_required"
                summary.unresolved_action_rows += 1
            elif source_player_id in adapter.identity.rejected_player_source_ids:
                identity_state = "rejected"
                summary.rejected_action_rows += 1
            else:
                raise HistoricalCanonicalBuildError("action player identity is unclassified")
            source_team_id = strict_int(source.get("teamId"), context="action.teamId")
            team_id = adapter.identity.canonical_id(WyscoutIdentityEntityKind.TEAM, source_team_id)
            if team_id is None:
                raise HistoricalCanonicalBuildError("action team identity is unresolved")
            period_code, period_rank, period_offset = _period(source.get("matchPeriod"))
            event_seconds = strict_decimal(source.get("eventSec"), context="action.eventSec")
            if event_seconds < 0:
                raise HistoricalCanonicalBuildError("action event clock is negative")
            absolute_minute = period_offset + event_seconds / Decimal(60)
            summary.terminal_lower_bound[source_match_id] = max(
                summary.terminal_lower_bound.get(source_match_id, Decimal(90)),
                Decimal(90),
                absolute_minute,
            )
            tags = _tag_ids(source.get("tags"))
            if player_id is not None and _DISMISSAL_TAGS.intersection(tags):
                key = (source_match_id, source_player_id)
                summary.dismissals[key] = min(
                    summary.dismissals.get(key, absolute_minute), absolute_minute
                )
            source_action_id = strict_int(source.get("id"), context="action.id")
            (
                start_x,
                start_y,
                end_x,
                end_y,
                coordinate_evidence_state,
                invalid_coordinate_points,
            ) = _positions(source.get("positions"))
            state_counts = summary.coordinate_evidence_state_counts.setdefault(
                partition.name,
                {state: 0 for state in _COORDINATE_STATES},
            )
            state_counts[coordinate_evidence_state] += 1
            if invalid_coordinate_points:
                partition_anomalies = summary.invalid_coordinate_actions.setdefault(
                    partition.name, {}
                )
                if source_action_id in partition_anomalies:
                    raise HistoricalCanonicalBuildError(
                        "coordinate anomaly action identity is duplicated"
                    )
                partition_anomalies[source_action_id] = invalid_coordinate_points
            sub_event = source.get("subEventId")
            sub_event_id = (
                None if sub_event is None else strict_int(sub_event, context="action.subEventId")
            )
            ordinal = strict_int(
                source.get("source_record_ordinal"), context="action.source_record_ordinal"
            )
            rows.append(
                {
                    "schema_version": CANONICAL_SCHEMA_VERSION,
                    "canonical_build_id": build_id,
                    "source_partition": partition.name.lower(),
                    "source_member_path": partition.action_relative_path,
                    "source_member_sha256": partition.action_sha256,
                    "source_record_ordinal": ordinal,
                    "source_action_id": source_action_id,
                    "action_id": str(
                        canonical_source_uuid(SourceRecordKind.ACTION, source_action_id)
                    ),
                    "source_match_id": source_match_id,
                    "match_id": context.match_id,
                    "source_competition_id": context.source_competition_id,
                    "competition_id": context.competition_id,
                    "season_id": context.season_id,
                    "source_player_id": source_player_id,
                    "player_id": player_id,
                    "player_identity_state": identity_state,
                    "source_team_id": source_team_id,
                    "team_id": team_id,
                    "event_id": strict_int(source.get("eventId"), context="action.eventId"),
                    "event_name": _required_text(
                        source.get("eventName"), context="action.eventName"
                    ),
                    "sub_event_id": sub_event_id,
                    "sub_event_name": _optional_text(source.get("subEventName")),
                    "period_code": period_code,
                    "period_rank": period_rank,
                    "event_seconds": float(event_seconds),
                    "absolute_minute": float(absolute_minute),
                    "occurrence_utc": context.match_start_utc
                    + timedelta(minutes=float(absolute_minute)),
                    "tag_ids": tags,
                    "start_x": start_x,
                    "start_y": start_y,
                    "end_x": end_x,
                    "end_y": end_y,
                    "coordinate_evidence_state": coordinate_evidence_state,
                    **_common_clocks(feature_cutoff_ts),
                }
            )
        rows.sort(key=lambda row: cast(int, row["source_record_ordinal"]))
        batches.append(pa.RecordBatch.from_pylist(rows, schema=_ACTION_SCHEMA))
        row_count += len(rows)
    return batches, row_count


def audit_historical_action_projection(
    *,
    adapter: WyscoutHistoricalAdapter,
    feature_cutoff_ts: datetime = DEFAULT_FEATURE_CUTOFF,
) -> HistoricalActionProjectionAudit:
    """Traverse the exact canonical action projection without writing artifacts."""

    if feature_cutoff_ts.tzinfo is None or feature_cutoff_ts.utcoffset() != timedelta(0):
        raise HistoricalCanonicalBuildError("feature cutoff must be timezone-aware UTC")
    feature_cutoff_ts = feature_cutoff_ts.astimezone(UTC)
    adapter.verify()
    if max(SOURCE_AVAILABLE_AT, adapter.identity.available_at) >= feature_cutoff_ts:
        raise HistoricalCanonicalBuildError(
            "required authorities must be strictly before the feature cutoff"
        )
    _match_rows, match_contexts = _project_matches(adapter, feature_cutoff_ts)
    if any(context.match_start_utc >= feature_cutoff_ts for context in match_contexts.values()):
        raise HistoricalCanonicalBuildError(
            "selected match times must be strictly before the feature cutoff"
        )
    code_digest = _canonical_code_digest()
    build_id = _build_id(
        adapter=adapter,
        feature_cutoff_ts=feature_cutoff_ts,
        code_digest=code_digest,
    )
    summary = _ActionEvidenceSummary(
        terminal_lower_bound={},
        dismissals={},
        empty_sub_event_id_sentinel_counts={},
        coordinate_evidence_state_counts={},
        invalid_coordinate_actions={},
    )
    action_count = 0
    for partition in adapter.partitions:
        _batches, partition_count = _action_batches_for_partition(
            adapter=adapter,
            partition=partition,
            match_contexts=match_contexts,
            build_id=build_id,
            feature_cutoff_ts=feature_cutoff_ts,
            summary=summary,
        )
        if partition_count != partition.action_count:
            raise HistoricalCanonicalBuildError("canonical action partition count drifted")
        action_count += partition_count
    sentinel_count = sum(summary.empty_sub_event_id_sentinel_counts.values())
    if not adapter.is_test_fixture and (
        action_count != 3_071_395
        or sentinel_count != EMPTY_SUB_EVENT_ID_SENTINEL_COUNT
        or summary.empty_sub_event_id_sentinel_counts != dict(EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS)
    ):
        raise HistoricalCanonicalBuildError(
            "retained optional subEventId missingness reconciliation drifted"
        )
    if not adapter.is_test_fixture:
        _require_retained_coordinate_anomalies(summary)
    invalid_action_count = sum(
        len(actions) for actions in summary.invalid_coordinate_actions.values()
    )
    invalid_point_count = sum(
        len(points)
        for actions in summary.invalid_coordinate_actions.values()
        for points in actions.values()
    )
    return HistoricalActionProjectionAudit(
        action_count=action_count,
        empty_sub_event_id_sentinel_count=sentinel_count,
        empty_sub_event_id_sentinel_counts=dict(
            sorted(summary.empty_sub_event_id_sentinel_counts.items())
        ),
        coordinate_evidence_state_counts={
            partition: dict(sorted(counts.items()))
            for partition, counts in sorted(summary.coordinate_evidence_state_counts.items())
        },
        invalid_coordinate_action_count=invalid_action_count,
        invalid_coordinate_point_count=invalid_point_count,
    )


def _formation_lists(
    team_row: Mapping[str, object],
) -> tuple[list[int], list[int], list[dict[str, object]] | None]:
    if strict_int(team_row.get("hasFormation"), context="team.hasFormation") != 1:
        return [], [], []
    formation = team_row.get("formation")
    if type(formation) is not dict:
        raise HistoricalCanonicalBuildError("declared formation is absent")
    value = cast(dict[str, object], formation)

    def players(key: str) -> list[int]:
        raw = value.get(key)
        if type(raw) is not list:
            raise HistoricalCanonicalBuildError(f"formation {key} is not an array")
        result: list[int] = []
        for item in raw:
            if type(item) is not dict:
                raise HistoricalCanonicalBuildError(f"formation {key} row is not an object")
            result.append(
                strict_int(
                    cast(dict[str, object], item).get("playerId"),
                    context=f"{key}.playerId",
                )
            )
        if len(result) != len(set(result)):
            raise HistoricalCanonicalBuildError(f"formation {key} repeats a player")
        return result

    substitutions = value.get("substitutions")
    if type(substitutions) is str and substitutions == "null":
        return players("lineup"), players("bench"), None
    if type(substitutions) is not list or any(type(item) is not dict for item in substitutions):
        raise HistoricalCanonicalBuildError("formation substitutions are not objects")
    return players("lineup"), players("bench"), cast(list[dict[str, object]], substitutions)


def _require_retained_substitution_sentinels(
    actual: Mapping[str, set[tuple[int, int]]],
) -> None:
    projected = {
        partition: frozenset(references) for partition, references in actual.items() if references
    }
    if projected != _RETAINED_NULL_SUBSTITUTION_SENTINELS:
        raise HistoricalCanonicalBuildError(
            "retained null substitution sentinel reconciliation drifted"
        )


def _require_retained_zero_player_in_substitutions(
    actual: Mapping[str, set[tuple[int, int, int, int]]],
) -> None:
    projected = {
        partition: frozenset(references) for partition, references in actual.items() if references
    }
    if projected != _RETAINED_ZERO_PLAYER_IN_SUBSTITUTIONS:
        raise HistoricalCanonicalBuildError(
            "retained zero playerIn substitution reconciliation drifted"
        )


def _project_appearances(
    *,
    adapter: WyscoutHistoricalAdapter,
    match_contexts: Mapping[int, _MatchContext],
    action_summary: _ActionEvidenceSummary,
    build_id: str,
    feature_cutoff_ts: datetime,
) -> tuple[
    list[dict[str, object]],
    dict[str, int],
    dict[str, set[tuple[int, int]]],
    dict[str, set[tuple[int, int, int, int]]],
]:
    rows: list[dict[str, object]] = []
    substitution_unavailable_teams: dict[str, set[tuple[int, int]]] = {}
    zero_player_in_substitutions: dict[str, set[tuple[int, int, int, int]]] = {}
    counts = {
        "exact": 0,
        "conservative_lower_bound": 0,
        "unusable": 0,
        "unresolved_lineup_occurrences_excluded": 0,
        "zero_lineup_occurrences_excluded": 0,
        "team_rows_without_formation": 0,
        "entry_after_action_terminal_lower_bound": 0,
        "zero_player_in_substitution_occurrences_excluded": 0,
    }
    for context in match_contexts.values():
        teams_data = context.source_row.get("teamsData")
        if type(teams_data) is not dict:
            raise HistoricalCanonicalBuildError("match teamsData is absent")
        for raw_team in cast(dict[str, object], teams_data).values():
            if type(raw_team) is not dict:
                raise HistoricalCanonicalBuildError("match team row is not an object")
            team_row = cast(dict[str, object], raw_team)
            source_team_id = strict_int(team_row.get("teamId"), context="match.teamId")
            team_id = adapter.identity.canonical_id(WyscoutIdentityEntityKind.TEAM, source_team_id)
            if team_id is None:
                raise HistoricalCanonicalBuildError("formation team identity is unresolved")
            lineup, bench, substitutions = _formation_lists(team_row)
            if not lineup and not bench:
                counts["team_rows_without_formation"] += 1
                continue
            if set(lineup).intersection(bench):
                raise HistoricalCanonicalBuildError("player appears in both lineup and bench")
            sub_in: dict[int, Decimal] = {}
            sub_out: dict[int, Decimal] = {}
            substitutions_unavailable = substitutions is None
            if substitutions_unavailable:
                references = substitution_unavailable_teams.setdefault(context.partition, set())
                reference = (context.source_match_id, source_team_id)
                if reference in references:
                    raise HistoricalCanonicalBuildError(
                        "null substitution sentinel team reference is duplicated"
                    )
                references.add(reference)
            else:
                for substitution in cast(list[dict[str, object]], substitutions):
                    minute = strict_decimal(
                        substitution.get("minute"), context="substitution.minute"
                    )
                    if minute < 0:
                        raise HistoricalCanonicalBuildError("substitution minute is negative")
                    player_in = strict_int(
                        substitution.get("playerIn"), context="substitution.playerIn"
                    )
                    player_out = strict_int(
                        substitution.get("playerOut"), context="substitution.playerOut"
                    )
                    if player_out in sub_out or (player_in != 0 and player_in in sub_in):
                        raise HistoricalCanonicalBuildError(
                            "player has duplicate substitution boundary"
                        )
                    sub_out[player_out] = minute
                    if player_in == 0:
                        if minute != minute.to_integral_value():
                            raise HistoricalCanonicalBuildError(
                                "zero playerIn substitution minute is not integral"
                            )
                        zero_reference = (
                            context.source_match_id,
                            source_team_id,
                            player_out,
                            int(minute),
                        )
                        zero_references = zero_player_in_substitutions.setdefault(
                            context.partition, set()
                        )
                        if zero_reference in zero_references:
                            raise HistoricalCanonicalBuildError(
                                "zero playerIn substitution occurrence is duplicated"
                            )
                        zero_references.add(zero_reference)
                        counts["zero_player_in_substitution_occurrences_excluded"] += 1
                    else:
                        sub_in[player_in] = minute
            participants = [*lineup, *sorted(set(sub_in) - set(lineup))]
            unused_bench = sorted(set(bench) - set(sub_in))
            bench_role = "bench_entry_unknown" if substitutions_unavailable else "unused_bench"
            for source_player_id, lineup_role in [
                *((player, "starter") for player in lineup),
                *((player, "substitute") for player in sorted(set(participants) - set(lineup))),
                *((player, bench_role) for player in unused_bench),
            ]:
                player_id = adapter.identity.canonical_id(
                    WyscoutIdentityEntityKind.PLAYER, source_player_id
                )
                if player_id is None:
                    if source_player_id == 0:
                        counts["zero_lineup_occurrences_excluded"] += 1
                    elif source_player_id in adapter.identity.unresolved_player_source_ids:
                        counts["unresolved_lineup_occurrences_excluded"] += 1
                    else:
                        raise HistoricalCanonicalBuildError(
                            "formation player identity is unclassified"
                        )
                    continue
                if lineup_role in {"unused_bench", "bench_entry_unknown"}:
                    minute_state = "unusable"
                    start: Decimal | None = None
                    end: Decimal | None = None
                    minutes: Decimal | None = None
                    right_censored = False
                    basis = (
                        "bench_with_unavailable_substitution_evidence"
                        if lineup_role == "bench_entry_unknown"
                        else "bench_evidence_without_entry"
                    )
                elif substitutions_unavailable:
                    start = Decimal(0)
                    end = Decimal(0)
                    minutes = Decimal(0)
                    minute_state = "conservative_lower_bound"
                    right_censored = True
                    basis = "starting_lineup_with_unavailable_substitution_evidence"
                else:
                    start = Decimal(0) if lineup_role == "starter" else sub_in[source_player_id]
                    boundary_candidates = [
                        value
                        for value in (
                            sub_out.get(source_player_id),
                            action_summary.dismissals.get(
                                (context.source_match_id, source_player_id)
                            ),
                        )
                        if value is not None
                    ]
                    if boundary_candidates:
                        end = min(boundary_candidates)
                        minute_state = "exact"
                        right_censored = False
                        basis = "lineup_and_observed_exit_boundary"
                    else:
                        action_terminal_lower_bound = action_summary.terminal_lower_bound.get(
                            context.source_match_id, Decimal(90)
                        )
                        if start > action_terminal_lower_bound:
                            counts["entry_after_action_terminal_lower_bound"] += 1
                        end = max(start, action_terminal_lower_bound)
                        minute_state = "conservative_lower_bound"
                        right_censored = True
                        basis = "observed_entry_and_regular_duration_or_last_event_lower_bound"
                    if end < start:
                        raise HistoricalCanonicalBuildError("appearance end precedes start")
                    minutes = end - start
                counts[minute_state] += 1
                rows.append(
                    {
                        "schema_version": CANONICAL_SCHEMA_VERSION,
                        "canonical_build_id": build_id,
                        "source_match_id": context.source_match_id,
                        "match_id": context.match_id,
                        "source_competition_id": context.source_competition_id,
                        "competition_id": context.competition_id,
                        "season_id": context.season_id,
                        "source_team_id": source_team_id,
                        "team_id": team_id,
                        "source_player_id": source_player_id,
                        "player_id": player_id,
                        "lineup_role": lineup_role,
                        "minute_state": minute_state,
                        "start_minute": None if start is None else float(start),
                        "end_minute": None if end is None else float(end),
                        "minutes": None if minutes is None else float(minutes),
                        "right_censored": right_censored,
                        "evidence_basis": basis,
                        "match_start_utc": context.match_start_utc,
                        "source_partition": context.partition.lower(),
                        "source_member_path": context.source_member_path,
                        "source_record_ordinal": context.source_record_ordinal,
                        **_common_clocks(feature_cutoff_ts),
                    }
                )
    rows.sort(
        key=lambda row: (
            cast(str, row["match_id"]),
            cast(str, row["team_id"]),
            cast(str, row["player_id"]),
        )
    )
    keys = [(row["match_id"], row["team_id"], row["player_id"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise HistoricalCanonicalBuildError("canonical appearance grain is duplicated")
    return (
        rows,
        counts,
        substitution_unavailable_teams,
        zero_player_in_substitutions,
    )


def audit_historical_appearance_projection(
    *,
    adapter: WyscoutHistoricalAdapter,
    feature_cutoff_ts: datetime = DEFAULT_FEATURE_CUTOFF,
) -> HistoricalAppearanceProjectionAudit:
    """Traverse canonical actions and appearances without writing any artifact."""

    if feature_cutoff_ts.tzinfo is None or feature_cutoff_ts.utcoffset() != timedelta(0):
        raise HistoricalCanonicalBuildError("feature cutoff must be timezone-aware UTC")
    feature_cutoff_ts = feature_cutoff_ts.astimezone(UTC)
    adapter.verify()
    if max(SOURCE_AVAILABLE_AT, adapter.identity.available_at) >= feature_cutoff_ts:
        raise HistoricalCanonicalBuildError(
            "required authorities must be strictly before the feature cutoff"
        )
    _match_rows, match_contexts = _project_matches(adapter, feature_cutoff_ts)
    if any(context.match_start_utc >= feature_cutoff_ts for context in match_contexts.values()):
        raise HistoricalCanonicalBuildError(
            "selected match times must be strictly before the feature cutoff"
        )
    code_digest = _canonical_code_digest()
    build_id = _build_id(
        adapter=adapter,
        feature_cutoff_ts=feature_cutoff_ts,
        code_digest=code_digest,
    )
    action_summary = _ActionEvidenceSummary(
        terminal_lower_bound={},
        dismissals={},
        empty_sub_event_id_sentinel_counts={},
        coordinate_evidence_state_counts={},
        invalid_coordinate_actions={},
    )
    action_count = 0
    for partition in adapter.partitions:
        _batches, partition_count = _action_batches_for_partition(
            adapter=adapter,
            partition=partition,
            match_contexts=match_contexts,
            build_id=build_id,
            feature_cutoff_ts=feature_cutoff_ts,
            summary=action_summary,
        )
        if partition_count != partition.action_count:
            raise HistoricalCanonicalBuildError("canonical action partition count drifted")
        action_count += partition_count
    sentinel_count = sum(action_summary.empty_sub_event_id_sentinel_counts.values())
    if not adapter.is_test_fixture and (
        action_count != 3_071_395
        or sentinel_count != EMPTY_SUB_EVENT_ID_SENTINEL_COUNT
        or action_summary.empty_sub_event_id_sentinel_counts
        != dict(EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS)
    ):
        raise HistoricalCanonicalBuildError(
            "retained optional subEventId missingness reconciliation drifted"
        )
    if not adapter.is_test_fixture:
        _require_retained_coordinate_anomalies(action_summary)
    (
        appearance_rows,
        minute_counts,
        unavailable_teams,
        zero_player_in_substitutions,
    ) = _project_appearances(
        adapter=adapter,
        match_contexts=match_contexts,
        action_summary=action_summary,
        build_id=build_id,
        feature_cutoff_ts=feature_cutoff_ts,
    )
    if not adapter.is_test_fixture:
        _require_retained_substitution_sentinels(unavailable_teams)
        _require_retained_zero_player_in_substitutions(zero_player_in_substitutions)
    return HistoricalAppearanceProjectionAudit(
        appearance_count=len(appearance_rows),
        minute_evidence_counts=dict(sorted(minute_counts.items())),
        substitution_unavailable_team_count=sum(
            len(references) for references in unavailable_teams.values()
        ),
        substitution_unavailable_teams={
            partition: tuple(sorted(references))
            for partition, references in sorted(unavailable_teams.items())
        },
        zero_player_in_substitution_count=sum(
            len(references) for references in zero_player_in_substitutions.values()
        ),
        zero_player_in_substitutions={
            partition: tuple(sorted(references))
            for partition, references in sorted(zero_player_in_substitutions.items())
        },
    )


def _identity_exclusions(
    adapter: WyscoutHistoricalAdapter, feature_cutoff_ts: datetime
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source_id in sorted(adapter.identity.unresolved_player_source_ids):
        rows.append(
            {
                "schema_version": CANONICAL_SCHEMA_VERSION,
                "source_player_id": source_id,
                "canonical_player_id": None,
                "identity_state": "review_required",
                "reason": "nonzero_absent_player_master",
                "source_reference_count": adapter.identity.player_source_reference_counts.get(
                    source_id, 0
                ),
                "candidate_eligible": False,
                "identity_bundle_sha256": adapter.identity.bundle_sha256,
                "identity_available_at": adapter.identity.available_at,
                "feature_cutoff_ts": feature_cutoff_ts,
            }
        )
    for source_id in sorted(adapter.identity.rejected_player_source_ids):
        rows.append(
            {
                "schema_version": CANONICAL_SCHEMA_VERSION,
                "source_player_id": source_id,
                "canonical_player_id": None,
                "identity_state": "rejected",
                "reason": "provider_zero_actor_rejection",
                "source_reference_count": adapter.identity.player_source_reference_counts.get(
                    source_id, 0
                ),
                "candidate_eligible": False,
                "identity_bundle_sha256": adapter.identity.bundle_sha256,
                "identity_available_at": adapter.identity.available_at,
                "feature_cutoff_ts": feature_cutoff_ts,
            }
        )
    return rows


def _write_artifact(
    *,
    storage: GuardedStorage,
    build_id: str,
    role: str,
    tail: str,
    rows: Sequence[Mapping[str, object]],
    schema: pa.Schema,
) -> CanonicalArtifact:
    return _write_artifact_payload(
        storage=storage,
        build_id=build_id,
        role=role,
        tail=tail,
        payload=_parquet_bytes(rows, schema),
        row_count=len(rows),
        identity_bundle_sha256=str(rows[0].get("identity_bundle_sha256", "bound-in-manifest")),
    )


def _write_artifact_payload(
    *,
    storage: GuardedStorage,
    build_id: str,
    role: str,
    tail: str,
    payload: bytes,
    row_count: int,
    identity_bundle_sha256: str,
) -> CanonicalArtifact:
    relative = f"build_id={build_id}/canonical/{tail}"
    receipt = storage.write_bytes(
        "research",
        relative,
        payload,
        media_type="application/vnd.apache.parquet",
        lineage={
            "build_id": build_id,
            "identity_bundle_sha256": identity_bundle_sha256,
            "role": role,
            "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        },
        retention={
            "classification": RIGHTS_CLASSIFICATION,
            "local_only": True,
            "raw_export_allowed": False,
        },
    )
    return CanonicalArtifact(
        role=role,
        relative_path=f"data/working/wyscout/v5/research/{receipt.relative_path}",
        row_count=row_count,
        sha256=receipt.sha256,
        size_bytes=receipt.size_bytes,
        schema_version=CANONICAL_SCHEMA_VERSION,
    )


def _source_counts(adapter: WyscoutHistoricalAdapter) -> dict[str, int]:
    if adapter.is_test_fixture:
        return {
            "matches": sum(partition.match_count for partition in adapter.partitions),
            "actions": sum(partition.action_count for partition in adapter.partitions),
            "teams": len(adapter.load_catalogue("teams")),
            "players": len(adapter.load_catalogue("players")),
            "competitions": len(adapter.load_catalogue("competitions")),
        }
    return {
        "matches": 1_826,
        "actions": 3_071_395,
        "teams": 142,
        "players": 3_603,
        "competitions": 7,
    }


def _prepare_canonical_population(
    *,
    adapter: WyscoutHistoricalAdapter,
    feature_cutoff_ts: datetime,
) -> _CanonicalPopulation:
    adapter.verify()
    if max(SOURCE_AVAILABLE_AT, adapter.identity.available_at) >= feature_cutoff_ts:
        raise HistoricalCanonicalBuildError(
            "required authorities must be strictly before the feature cutoff"
        )
    population_audit = adapter.audit_action_population()
    competition_rows, _competition_names = _project_competitions(adapter, feature_cutoff_ts)
    team_rows, _team_names = _project_teams(adapter, feature_cutoff_ts)
    player_rows = _project_players(adapter, feature_cutoff_ts)
    match_rows, match_contexts = _project_matches(adapter, feature_cutoff_ts)
    if any(context.match_start_utc >= feature_cutoff_ts for context in match_contexts.values()):
        raise HistoricalCanonicalBuildError(
            "selected match times must be strictly before the feature cutoff"
        )

    code_digest = _canonical_code_digest()
    build_id = _build_id(
        adapter=adapter,
        feature_cutoff_ts=feature_cutoff_ts,
        code_digest=code_digest,
    )
    return _CanonicalPopulation(
        audit=population_audit,
        competition_rows=competition_rows,
        team_rows=team_rows,
        player_rows=player_rows,
        match_rows=match_rows,
        match_contexts=match_contexts,
        code_digest=code_digest,
        build_id=build_id,
    )


def _materialize_canonical_population(
    *,
    adapter: WyscoutHistoricalAdapter,
    research_root: Path,
    feature_cutoff_ts: datetime,
    population: _CanonicalPopulation,
) -> _CanonicalMaterialization:
    build_id = population.build_id
    competition_rows = population.competition_rows
    team_rows = population.team_rows
    player_rows = population.player_rows
    match_rows = population.match_rows
    match_contexts = population.match_contexts
    storage = GuardedStorage({"research": research_root.resolve()})
    artifacts: list[CanonicalArtifact] = []
    for role, tail, rows, schema in (
        (
            "canonical_competitions",
            "competitions/part-00000.parquet",
            competition_rows,
            _COMPETITION_SCHEMA,
        ),
        ("canonical_teams", "teams/part-00000.parquet", team_rows, _TEAM_SCHEMA),
        ("canonical_players", "players/part-00000.parquet", player_rows, _PLAYER_SCHEMA),
        ("canonical_matches", "matches/part-00000.parquet", match_rows, _MATCH_SCHEMA),
    ):
        artifacts.append(
            _write_artifact(
                storage=storage,
                build_id=build_id,
                role=role,
                tail=tail,
                rows=rows,
                schema=schema,
            )
        )

    action_summary = _ActionEvidenceSummary(
        terminal_lower_bound={},
        dismissals={},
        empty_sub_event_id_sentinel_counts={},
        coordinate_evidence_state_counts={},
        invalid_coordinate_actions={},
    )
    for partition in adapter.partitions:
        action_batches, row_count = _action_batches_for_partition(
            adapter=adapter,
            partition=partition,
            match_contexts=match_contexts,
            build_id=build_id,
            feature_cutoff_ts=feature_cutoff_ts,
            summary=action_summary,
        )
        if row_count != partition.action_count:
            raise HistoricalCanonicalBuildError("canonical action partition count drifted")
        artifacts.append(
            _write_artifact_payload(
                storage=storage,
                build_id=build_id,
                role="canonical_actions",
                tail=f"actions/source_partition={partition.name.lower()}/part-00000.parquet",
                payload=_parquet_batch_bytes(action_batches, _ACTION_SCHEMA),
                row_count=row_count,
                identity_bundle_sha256=adapter.identity.bundle_sha256,
            )
        )

    (
        appearance_rows,
        minute_counts,
        substitution_unavailable_teams,
        zero_player_in_substitutions,
    ) = _project_appearances(
        adapter=adapter,
        match_contexts=match_contexts,
        action_summary=action_summary,
        build_id=build_id,
        feature_cutoff_ts=feature_cutoff_ts,
    )
    if not adapter.is_test_fixture:
        _require_retained_substitution_sentinels(substitution_unavailable_teams)
        _require_retained_zero_player_in_substitutions(zero_player_in_substitutions)
    empty_sub_event_id_sentinel_count = sum(
        action_summary.empty_sub_event_id_sentinel_counts.values()
    )
    if not adapter.is_test_fixture and (
        empty_sub_event_id_sentinel_count != EMPTY_SUB_EVENT_ID_SENTINEL_COUNT
        or action_summary.empty_sub_event_id_sentinel_counts
        != dict(EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS)
    ):
        raise HistoricalCanonicalBuildError(
            "retained optional subEventId missingness reconciliation drifted"
        )
    if not adapter.is_test_fixture:
        _require_retained_coordinate_anomalies(action_summary)
    invalid_coordinate_action_count = sum(
        len(actions) for actions in action_summary.invalid_coordinate_actions.values()
    )
    invalid_coordinate_point_count = sum(
        len(points)
        for actions in action_summary.invalid_coordinate_actions.values()
        for points in actions.values()
    )
    artifacts.append(
        _write_artifact(
            storage=storage,
            build_id=build_id,
            role="canonical_appearances",
            tail="appearances/part-00000.parquet",
            rows=appearance_rows,
            schema=_APPEARANCE_SCHEMA,
        )
    )
    exclusions = _identity_exclusions(adapter, feature_cutoff_ts)
    artifacts.append(
        _write_artifact(
            storage=storage,
            build_id=build_id,
            role="identity_exclusions",
            tail="identity-exclusions/part-00000.parquet",
            rows=exclusions,
            schema=_EXCLUSION_SCHEMA,
        )
    )

    canonical_counts = {
        "competitions": len(competition_rows),
        "teams": len(team_rows),
        "players": len(player_rows),
        "matches": len(match_rows),
        "actions": sum(
            artifact.row_count for artifact in artifacts if artifact.role == "canonical_actions"
        ),
        "appearances": len(appearance_rows),
        "identity_exclusions": len(exclusions),
    }
    source_counts = _source_counts(adapter)
    if not adapter.is_test_fixture and (
        canonical_counts["players"] != source_counts["players"]
        or canonical_counts["teams"] != source_counts["teams"]
        or canonical_counts["matches"] != source_counts["matches"]
        or canonical_counts["actions"] != source_counts["actions"]
    ):
        raise HistoricalCanonicalBuildError("canonical/source population does not reconcile")
    return _CanonicalMaterialization(
        artifacts=tuple(artifacts),
        action_summary=action_summary,
        appearance_rows=appearance_rows,
        minute_counts=minute_counts,
        substitution_unavailable_teams=substitution_unavailable_teams,
        zero_player_in_substitutions=zero_player_in_substitutions,
        exclusions=exclusions,
        canonical_counts=canonical_counts,
        source_counts=source_counts,
        empty_sub_event_id_sentinel_count=empty_sub_event_id_sentinel_count,
        invalid_coordinate_action_count=invalid_coordinate_action_count,
        invalid_coordinate_point_count=invalid_coordinate_point_count,
    )


def _canonical_manifest(
    *,
    adapter: WyscoutHistoricalAdapter,
    feature_cutoff_ts: datetime,
    population: _CanonicalPopulation,
    materialization: _CanonicalMaterialization,
) -> dict[str, object]:
    build_id = population.build_id
    code_digest = population.code_digest
    population_audit = population.audit
    artifacts = materialization.artifacts
    action_summary = materialization.action_summary
    minute_counts = materialization.minute_counts
    substitution_unavailable_teams = materialization.substitution_unavailable_teams
    zero_player_in_substitutions = materialization.zero_player_in_substitutions
    canonical_counts = materialization.canonical_counts
    source_counts = materialization.source_counts
    empty_sub_event_id_sentinel_count = materialization.empty_sub_event_id_sentinel_count
    invalid_coordinate_action_count = materialization.invalid_coordinate_action_count
    invalid_coordinate_point_count = materialization.invalid_coordinate_point_count
    manifest: dict[str, object] = {
        "schema_version": 1,
        "manifest_schema_version": CANONICAL_MANIFEST_SCHEMA_VERSION,
        "canonical_schema_version": CANONICAL_SCHEMA_VERSION,
        "canonical_build_id": build_id,
        "builder_version": CANONICAL_BUILDER_VERSION,
        "code_digest": code_digest,
        "provider_adapter": "wyscout-figshare-v5-historical-v1",
        "provider_neutral_boundary": "canonical-football-research-v1",
        "test_fixture": adapter.is_test_fixture,
        "rights": {
            "classification": RIGHTS_CLASSIFICATION,
            "attribution": ATTRIBUTION,
            "local_only": True,
            "raw_export_allowed": False,
        },
        "authorities": {
            "source_manifest_id": SOURCE_MANIFEST_ID,
            "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
            "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
            "identity_bundle_sha256": adapter.identity.bundle_sha256,
            "source_available_at": _utc_text(SOURCE_AVAILABLE_AT),
            "identity_available_at": _utc_text(adapter.identity.available_at),
            "feature_cutoff_ts": _utc_text(feature_cutoff_ts),
        },
        "source_counts": source_counts,
        "canonical_counts": canonical_counts,
        "identity_audit": {
            "resolved_players": canonical_counts["players"],
            "review_required_players_excluded": len(adapter.identity.unresolved_player_source_ids),
            "rejected_players_excluded": len(adapter.identity.rejected_player_source_ids),
            "unresolved_action_rows": action_summary.unresolved_action_rows,
            "rejected_action_rows": action_summary.rejected_action_rows,
            "zero_actor_action_rows": population_audit.zero_actor_action_count,
            "current_team_id_used_for_membership": False,
        },
        "minute_evidence": {
            "policy": "lineup-substitution-dismissal-v1",
            "exact": "observed entry and exit boundaries",
            "conservative_lower_bound": (
                "observed entry through a supported lower-bound exit; starting-lineup "
                "rows with unavailable substitutions retain only a zero-minute lower bound"
            ),
            "unusable": (
                "bench evidence without observed entry, including benches whose "
                "substitution evidence is unavailable"
            ),
            "silent_ninety_minute_assumption": False,
            "action_presence_used_for_minutes": False,
            "observed_entry_floor_applied": True,
            "counts": minute_counts,
        },
        "substitution_evidence": {
            "states": ["available_array", "unavailable_exact_null_string_sentinel"],
            "accepted_unavailable_raw_value": "null",
            "arbitrary_shape_coercion": False,
            "unavailable_team_count": sum(
                len(references) for references in substitution_unavailable_teams.values()
            ),
            "unavailable_team_counts_by_partition": {
                partition: len(substitution_unavailable_teams.get(partition, set()))
                for partition in sorted({item.name for item in adapter.partitions})
            },
            "unavailable_teams": [
                {
                    "source_partition": partition,
                    "source_match_id": match_id,
                    "source_team_id": team_id,
                }
                for partition, references in sorted(substitution_unavailable_teams.items())
                for match_id, team_id in sorted(references)
            ],
            "zero_player_in_policy": (
                "exclude every rejected zero-entry occurrence while retaining its "
                "distinct nonzero playerOut exit boundary"
            ),
            "zero_player_in_occurrence_count": sum(
                len(references) for references in zero_player_in_substitutions.values()
            ),
            "zero_player_in_occurrence_counts_by_partition": {
                partition: len(zero_player_in_substitutions.get(partition, set()))
                for partition in sorted({item.name for item in adapter.partitions})
            },
            "zero_player_in_occurrences": [
                {
                    "source_partition": partition,
                    "source_match_id": match_id,
                    "source_team_id": team_id,
                    "source_player_out_id": player_out,
                    "minute": minute,
                }
                for partition, references in sorted(zero_player_in_substitutions.items())
                for match_id, team_id, player_out, minute in sorted(references)
            ],
            "starter_policy": (
                "retain a conservative zero-minute lower bound from starting-lineup "
                "evidence without inferring an exit"
            ),
            "bench_policy": (
                "retain as unusable bench-entry-unknown evidence without inferring play"
            ),
            "action_presence_used_for_minutes": False,
            "current_team_id_used_for_membership": False,
        },
        "optional_sub_event_id": {
            "adapter_contract": "strict_integer_or_null",
            "raw_empty_string_sentinel_normalized_to_null": True,
            "empty_string_sentinel_count": empty_sub_event_id_sentinel_count,
            "empty_string_sentinel_counts_by_partition": dict(
                sorted(action_summary.empty_sub_event_id_sentinel_counts.items())
            ),
        },
        "coordinate_evidence": {
            "states": list(_COORDINATE_STATES),
            "raw_strict_integers_preserved": True,
            "clamped_nulled_or_dropped": False,
            "coordinate_independent_actions_retained": True,
            "coordinate_coverage_admits_only_state": "valid",
            "state_counts_by_partition": {
                partition: dict(sorted(counts.items()))
                for partition, counts in sorted(
                    action_summary.coordinate_evidence_state_counts.items()
                )
            },
            "invalid_action_count": invalid_coordinate_action_count,
            "invalid_point_count": invalid_coordinate_point_count,
            "invalid_action_counts_by_partition": {
                partition: len(action_summary.invalid_coordinate_actions.get(partition, {}))
                for partition in sorted(action_summary.coordinate_evidence_state_counts)
            },
            "invalid_actions": [
                {
                    "source_partition": partition,
                    "source_action_id": action_id,
                    "invalid_points": [
                        {"point_index": index, "axis": axis, "raw_value": value}
                        for index, axis, value in points
                    ],
                }
                for partition, actions in sorted(action_summary.invalid_coordinate_actions.items())
                for action_id, points in sorted(actions.items())
            ],
        },
        "partitions": [
            {
                "name": partition.name,
                "match_path": partition.match_relative_path,
                "match_sha256": partition.match_sha256,
                "match_count": partition.match_count,
                "action_path": partition.action_relative_path,
                "action_sha256": partition.action_sha256,
                "action_count": partition.action_count,
                "aligned_match_count": len(population_audit.match_ids_by_partition[partition.name]),
            }
            for partition in adapter.partitions
        ],
        "artifacts": [
            {
                "role": artifact.role,
                "path": artifact.relative_path,
                "row_count": artifact.row_count,
                "sha256": artifact.sha256,
                "size_bytes": artifact.size_bytes,
                "schema_version": artifact.schema_version,
            }
            for artifact in artifacts
        ],
        "limitations": [
            "Historical 2017/18 evidence; not current-market coverage.",
            "Terminal player intervals without observed exits are conservative lower bounds.",
            "Six team formations have unavailable substitution evidence; their starters "
            "retain zero-minute lower bounds and their bench entries remain unknown.",
            "This build is canonical evidence, not football relevance or recruitment advice.",
        ],
    }
    return manifest


def build_historical_canonical(
    *,
    adapter: WyscoutHistoricalAdapter,
    research_root: Path,
    research_manifest_root: Path,
    feature_cutoff_ts: datetime = DEFAULT_FEATURE_CUTOFF,
) -> HistoricalCanonicalBuildResult:
    """Build or confirm one immutable, content-addressed canonical population."""

    if not adapter.is_test_fixture and (
        research_root != PRODUCTION_RESEARCH_ROOT
        or research_manifest_root != PRODUCTION_RESEARCH_MANIFEST_ROOT
    ):
        raise HistoricalCanonicalBuildError(
            "retained builds require the exact canonical production research roots"
        )
    if feature_cutoff_ts.tzinfo is None or feature_cutoff_ts.utcoffset() != timedelta(0):
        raise HistoricalCanonicalBuildError("feature cutoff must be timezone-aware UTC")
    feature_cutoff_ts = feature_cutoff_ts.astimezone(UTC)
    population = _prepare_canonical_population(
        adapter=adapter,
        feature_cutoff_ts=feature_cutoff_ts,
    )
    materialization = _materialize_canonical_population(
        adapter=adapter,
        research_root=research_root,
        feature_cutoff_ts=feature_cutoff_ts,
        population=population,
    )
    manifest = _canonical_manifest(
        adapter=adapter,
        feature_cutoff_ts=feature_cutoff_ts,
        population=population,
        materialization=materialization,
    )
    build_id = population.build_id
    artifacts = materialization.artifacts
    manifest_storage = GuardedStorage({"manifests": research_manifest_root.resolve()})
    manifest_receipt: ArtifactReceipt = manifest_storage.write_json(
        "manifests",
        f"{build_id}.canonical-manifest.json",
        manifest,
        lineage={
            "build_id": build_id,
            "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
            "identity_bundle_sha256": adapter.identity.bundle_sha256,
        },
        retention={
            "classification": RIGHTS_CLASSIFICATION,
            "local_only": True,
            "raw_export_allowed": False,
        },
    )
    return HistoricalCanonicalBuildResult(
        build_id=build_id,
        canonical_root_relative_path=f"data/working/wyscout/v5/research/build_id={build_id}",
        manifest_relative_path=(
            "data/manifests/wyscout/v5/research/" + manifest_receipt.relative_path
        ),
        manifest_sha256=manifest_receipt.sha256,
        manifest_size_bytes=manifest_receipt.size_bytes,
        artifacts=tuple(artifacts),
        manifest=manifest,
    )


__all__ = [
    "CANONICAL_BUILDER_VERSION",
    "CANONICAL_MANIFEST_SCHEMA_VERSION",
    "CANONICAL_SCHEMA_VERSION",
    "DEFAULT_FEATURE_CUTOFF",
    "CanonicalArtifact",
    "HistoricalCanonicalBuildError",
    "HistoricalCanonicalBuildResult",
    "HistoricalActionProjectionAudit",
    "HistoricalAppearanceProjectionAudit",
    "audit_historical_action_projection",
    "audit_historical_appearance_projection",
    "build_historical_canonical",
]

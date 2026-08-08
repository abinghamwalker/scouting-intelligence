"""Read-only exact match-context join for the bounded W04 Wyscout slice."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Final, cast
from uuid import UUID

from scouting.contracts.wyscout_build import bounded_season_uuid
from scouting.contracts.wyscout_data import SourceRecordKind, WyscoutSourceRowReference
from scouting.contracts.wyscout_identity import (
    WyscoutIdentityEntityKind,
    WyscoutIdentityState,
)
from scouting.identity import wyscout as identity
from scouting.sources import wyscout_completion_index as completion
from scouting.sources import wyscout_manifest as bridge

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SOURCE_ROOT_RELATIVE = Path("data/source/wyscout/v5")
_MANIFEST_ROOT_RELATIVE = Path("data/manifests")
_IDENTITY_ROOT_RELATIVE = Path("data/working/wyscout/v5/identity")

SOURCE_MANIFEST_ID: Final = UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b")
SOURCE_MANIFEST_SHA256: Final = "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
SOURCE_COMPLETION_INDEX_SHA256: Final = (
    "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
)
IDENTITY_BUNDLE_ID: Final = UUID("31638732-5b25-57db-9eb4-8e943a47a387")
IDENTITY_BUNDLE_SHA256: Final = "4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80"

MATCH_MEMBER_PATH: Final = "archive-members/matches_England.json"
MATCH_MEMBER_SHA256: Final = "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29"
MATCH_MEMBER_SIZE_BYTES: Final = 1_694_720
MATCH_MEMBER_ROW_COUNT: Final = 380
MATCH_SOURCE_RECORD_ORDINAL: Final = 379
MATCH_RAW_RECORD_SHA256: Final = "1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86"

EVENT_MEMBER_PATH: Final = "archive-members/events_England.json"
EVENT_MEMBER_SHA256: Final = "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad"
MATCH_SOURCE_ID: Final = 2_499_719
COMPETITION_SOURCE_ID: Final = 364
SEASON_SOURCE_ID: Final = 181_150
TEAM_SOURCE_IDS: Final = (1_609, 1_631)
TARGET_TEAM_SOURCE_ID: Final = 1_631
TARGET_PLAYER_SOURCE_ID: Final = 285_508
MATCH_START_UTC: Final = "2017-08-11T18:45:00Z"

MATCH_ID: Final = UUID("bad97950-6fac-5cf0-a93c-094f91abbb9b")
COMPETITION_ID: Final = UUID("cb5c5317-fa4a-571e-93dc-ef6ce482eab7")
SEASON_ID: Final = UUID("4696aa1f-b512-5d18-af79-33cf031455cf")
TEAM_IDS: Final = (
    UUID("b5f2dd3c-0166-5384-99fa-0ed47cc7e44c"),
    UUID("5b353635-819b-5bd1-8ca2-5a7364042a96"),
)
TARGET_PLAYER_ID: Final = UUID("be8da881-2b15-513f-978f-6bb3865bc8e2")

_EXPECTED_PERIODS: Final = (
    (
        "1H",
        901,
        "473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b",
    ),
    (
        "2H",
        867,
        "b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16",
    ),
)
_CHUNK_SIZE = 1024 * 1024


class WyscoutVerticalSliceContextError(RuntimeError):
    """The selected source/identity/event context differs from accepted evidence."""


class WyscoutVerticalSliceContextPathError(WyscoutVerticalSliceContextError):
    """An exact context root or selected member has an unsafe physical path."""


@dataclass(frozen=True, slots=True)
class VerifiedIdentityBinding:
    """One exact source integer joined to its accepted canonical identity."""

    entity_kind: WyscoutIdentityEntityKind
    source_id: int
    canonical_id: UUID


@dataclass(frozen=True, slots=True)
class VerifiedMatchContext:
    """The sole immutable W04 selected-match context and checked action population."""

    source_manifest_id: UUID
    source_manifest_sha256: str
    identity_bundle_id: UUID
    identity_bundle_sha256: str
    match_source_row: WyscoutSourceRowReference
    match: VerifiedIdentityBinding
    competition: VerifiedIdentityBinding
    season_source_id: int
    season_id: UUID
    teams: tuple[VerifiedIdentityBinding, VerifiedIdentityBinding]
    target_team: VerifiedIdentityBinding
    target_player: VerifiedIdentityBinding
    match_start_utc: str
    target_substitution_minute: int
    raw_match: Mapping[str, object]
    canonical_raw_match: bytes
    event_population: completion.VerifiedMatchPopulation
    period_action_counts: tuple[tuple[str, int], tuple[str, int]]
    period_membership_sha256: tuple[str, str]


def _strict_positive(value: object, *, context: str) -> int:
    if type(value) is not int or value <= 0:
        raise WyscoutVerticalSliceContextError(f"{context} must be a strict positive integer")
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise WyscoutVerticalSliceContextError(f"match source repeats key {key!r}")
        result[key] = value
    return result


def _require_exact_absolute_root(path: Path, relative: Path, *, context: str) -> Path:
    expected = _PROJECT_ROOT / relative
    if not isinstance(path, Path) or not path.is_absolute() or path != expected:
        raise WyscoutVerticalSliceContextPathError(
            f"{context} must be the exact absolute repository {relative.as_posix()} root"
        )
    return expected


def _read_exact_match_member(source_root: Path) -> bytes:
    try:
        with bridge._open_regular_beneath(source_root, MATCH_MEMBER_PATH) as descriptor:
            before = os.fstat(descriptor)
            if (
                not stat.S_ISREG(before.st_mode)
                or stat.S_IMODE(before.st_mode) != 0o600
                or before.st_nlink != 1
            ):
                raise WyscoutVerticalSliceContextPathError(
                    "selected match member must be one regular 0600 file"
                )
            digest = hashlib.sha256()
            chunks: list[bytes] = []
            size = 0
            while chunk := os.read(descriptor, _CHUNK_SIZE):
                size += len(chunk)
                if size > MATCH_MEMBER_SIZE_BYTES:
                    raise WyscoutVerticalSliceContextError(
                        "selected match member exceeds its accepted byte size"
                    )
                digest.update(chunk)
                chunks.append(chunk)
            after = os.fstat(descriptor)
    except WyscoutVerticalSliceContextError:
        raise
    except (OSError, bridge.WyscoutSourceManifestError) as exc:
        if isinstance(exc, OSError) and exc.errno not in {errno.ELOOP, errno.ENOTDIR}:
            raise WyscoutVerticalSliceContextPathError(
                "selected match member cannot be read safely"
            ) from exc
        raise WyscoutVerticalSliceContextPathError(
            "selected match member contains a link or nonregular path"
        ) from exc
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable):
        raise WyscoutVerticalSliceContextError("selected match member changed during read")
    if size != MATCH_MEMBER_SIZE_BYTES or digest.hexdigest() != MATCH_MEMBER_SHA256:
        raise WyscoutVerticalSliceContextError(
            "selected match member size or SHA-256 differs from accepted evidence"
        )
    return b"".join(chunks)


def _decode_match_member(payload: bytes) -> list[dict[str, object]]:
    try:
        decoded = json.loads(
            payload,
            parse_float=Decimal,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutVerticalSliceContextError("selected match member is not strict JSON") from exc
    if type(decoded) is not list or any(type(row) is not dict for row in decoded):
        raise WyscoutVerticalSliceContextError(
            "selected match member must be one JSON array of objects"
        )
    rows = cast(list[dict[str, object]], decoded)
    if len(rows) != MATCH_MEMBER_ROW_COUNT:
        raise WyscoutVerticalSliceContextError(
            "selected match member row cardinality differs from accepted evidence"
        )
    return rows


def _strict_player_ids(value: object, *, context: str) -> tuple[int, ...]:
    if type(value) is not list:
        raise WyscoutVerticalSliceContextError(f"{context} must be an exact JSON array")
    result: list[int] = []
    for ordinal, item in enumerate(cast(list[object], value)):
        if type(item) is not dict:
            raise WyscoutVerticalSliceContextError(f"{context}[{ordinal}] must be an object")
        row = cast(dict[str, object], item)
        result.append(
            _strict_positive(row.get("playerId"), context=f"{context}[{ordinal}].playerId")
        )
    return tuple(result)


def _strict_substitutions(value: object, *, context: str) -> tuple[tuple[int, int, int], ...]:
    if type(value) is not list:
        raise WyscoutVerticalSliceContextError(f"{context} must be an exact JSON array")
    result: list[tuple[int, int, int]] = []
    for ordinal, item in enumerate(cast(list[object], value)):
        if type(item) is not dict:
            raise WyscoutVerticalSliceContextError(f"{context}[{ordinal}] must be an object")
        row = cast(dict[str, object], item)
        if set(row) != {"minute", "playerIn", "playerOut"}:
            raise WyscoutVerticalSliceContextError(
                f"{context}[{ordinal}] keys differ from the accepted substitution shape"
            )
        result.append(
            (
                _strict_positive(row.get("playerIn"), context=f"{context}.playerIn"),
                _strict_positive(row.get("playerOut"), context=f"{context}.playerOut"),
                _strict_positive(row.get("minute"), context=f"{context}.minute"),
            )
        )
    return tuple(result)


def _validate_selected_match(rows: list[dict[str, object]]) -> tuple[dict[str, object], bytes]:
    selected: list[tuple[int, dict[str, object]]] = []
    for ordinal, row in enumerate(rows):
        source_id = _strict_positive(row.get("wyId"), context=f"match[{ordinal}].wyId")
        if source_id == MATCH_SOURCE_ID:
            selected.append((ordinal, row))
    if len(selected) != 1 or selected[0][0] != MATCH_SOURCE_RECORD_ORDINAL:
        raise WyscoutVerticalSliceContextError(
            "selected match must occur exactly once at source ordinal 379"
        )
    row = selected[0][1]
    canonical = completion._canonical_value_bytes(row)
    if hashlib.sha256(canonical).hexdigest() != MATCH_RAW_RECORD_SHA256:
        raise WyscoutVerticalSliceContextError("selected match raw-record digest drifted")
    if (
        _strict_positive(row.get("competitionId"), context="competitionId") != COMPETITION_SOURCE_ID
        or _strict_positive(row.get("seasonId"), context="seasonId") != SEASON_SOURCE_ID
        or row.get("dateutc") != "2017-08-11 18:45:00"
    ):
        raise WyscoutVerticalSliceContextError(
            "selected match competition, season, or UTC start drifted"
        )
    teams_value = row.get("teamsData")
    if type(teams_value) is not dict:
        raise WyscoutVerticalSliceContextError("teamsData must be an exact JSON object")
    teams = cast(dict[str, object], teams_value)
    if set(teams) != {str(source_id) for source_id in TEAM_SOURCE_IDS}:
        raise WyscoutVerticalSliceContextError("selected match teams differ from 1609 and 1631")

    target_bench_count = 0
    target_lineup_count = 0
    target_substitutions: list[tuple[int, int, int]] = []
    target_substitution_out_count = 0
    for team_source_id in TEAM_SOURCE_IDS:
        team_value = teams[str(team_source_id)]
        if type(team_value) is not dict:
            raise WyscoutVerticalSliceContextError("teamsData team value must be an object")
        team = cast(dict[str, object], team_value)
        if _strict_positive(team.get("teamId"), context="teamsData.teamId") != team_source_id:
            raise WyscoutVerticalSliceContextError("teamsData key/teamId binding drifted")
        formation_value = team.get("formation")
        if type(formation_value) is not dict:
            raise WyscoutVerticalSliceContextError("selected team formation must be an object")
        formation = cast(dict[str, object], formation_value)
        bench = _strict_player_ids(
            formation.get("bench"), context=f"teamsData[{team_source_id}].formation.bench"
        )
        lineup = _strict_player_ids(
            formation.get("lineup"), context=f"teamsData[{team_source_id}].formation.lineup"
        )
        substitutions = _strict_substitutions(
            formation.get("substitutions"),
            context=f"teamsData[{team_source_id}].formation.substitutions",
        )
        if team_source_id == TARGET_TEAM_SOURCE_ID:
            target_bench_count += bench.count(TARGET_PLAYER_SOURCE_ID)
            target_lineup_count += lineup.count(TARGET_PLAYER_SOURCE_ID)
            target_substitutions.extend(
                item for item in substitutions if item[0] == TARGET_PLAYER_SOURCE_ID
            )
            target_substitution_out_count += sum(
                item[1] == TARGET_PLAYER_SOURCE_ID for item in substitutions
            )
        elif (
            TARGET_PLAYER_SOURCE_ID in bench
            or TARGET_PLAYER_SOURCE_ID in lineup
            or any(TARGET_PLAYER_SOURCE_ID in item[:2] for item in substitutions)
        ):
            raise WyscoutVerticalSliceContextError("target player crosses selected match teams")
    if target_bench_count != 1 or target_lineup_count != 0:
        raise WyscoutVerticalSliceContextError(
            "target player must occur exactly once on team 1631 bench and not its lineup"
        )
    if (
        len(target_substitutions) != 1
        or target_substitutions[0][2] != 82
        or target_substitution_out_count != 0
    ):
        raise WyscoutVerticalSliceContextError(
            "target player must have exactly one team 1631 minute-82 substitution-in"
        )
    return row, canonical


def _identity_binding(
    build: identity.WyscoutIdentityBuild,
    *,
    entity_kind: WyscoutIdentityEntityKind,
    source_id: int,
    canonical_id: UUID,
) -> VerifiedIdentityBinding:
    source_identity = f"{entity_kind.value.lower()}:{source_id}"
    rows = tuple(
        row
        for row in build.bundle.current_rows
        if row.entity_kind is entity_kind and row.source_identity.source_id == source_identity
    )
    if (
        len(rows) != 1
        or rows[0].state is not WyscoutIdentityState.RESOLVED
        or rows[0].canonical_id != canonical_id
    ):
        raise WyscoutVerticalSliceContextError(
            f"accepted identity bundle does not resolve exact {source_identity}"
        )
    return VerifiedIdentityBinding(
        entity_kind=entity_kind,
        source_id=source_id,
        canonical_id=canonical_id,
    )


def _validate_event_population(
    population: completion.VerifiedMatchPopulation,
) -> tuple[tuple[tuple[str, int], tuple[str, int]], tuple[str, str]]:
    if (
        population.index.sha256 != SOURCE_COMPLETION_INDEX_SHA256
        or population.source_member_path != EVENT_MEMBER_PATH
        or population.match_source_id != MATCH_SOURCE_ID
        or len(population.actions) != 1_768
    ):
        raise WyscoutVerticalSliceContextError("verified event population identity/count drifted")
    evidence = tuple(action.evidence for action in population.actions)
    if tuple(action.order_key for action in evidence) != tuple(
        sorted(action.order_key for action in evidence)
    ) or len(
        {(action.source_record_ordinal, action.source_event_record_id) for action in evidence}
    ) != len(evidence):
        raise WyscoutVerticalSliceContextError(
            "verified event population is reordered or duplicated"
        )
    if any(
        action.source_member_path != EVENT_MEMBER_PATH
        or action.source_member_sha256 != EVENT_MEMBER_SHA256
        or action.match_source_id != MATCH_SOURCE_ID
        for action in evidence
    ):
        raise WyscoutVerticalSliceContextError("verified event population crosses source scope")
    if any(
        hashlib.sha256(action.canonical_raw_record).hexdigest() != action.evidence.raw_record_sha256
        for action in population.actions
    ):
        raise WyscoutVerticalSliceContextError("verified event raw-record digest drifted")
    periods = completion.validate_match_population(index=population.index, actions=evidence)
    actual = tuple(
        (period.action_period_code, period.action_count, period.membership_sha256)
        for period in periods
    )
    if actual != _EXPECTED_PERIODS:
        raise WyscoutVerticalSliceContextError("verified event period population drifted")
    sequences = population.completion.sequences
    if (
        tuple(
            (
                sequence.action_period_code,
                sequence.period_action_count,
                sequence.source_completion_membership_sha256,
            )
            for sequence in sequences
        )
        != _EXPECTED_PERIODS
    ):
        raise WyscoutVerticalSliceContextError("checked event capability population drifted")
    return (
        cast(
            tuple[tuple[str, int], tuple[str, int]],
            tuple((code, count) for code, count, _digest in _EXPECTED_PERIODS),
        ),
        cast(tuple[str, str], tuple(digest for _code, _count, digest in _EXPECTED_PERIODS)),
    )


def load_verified_match_context(
    *,
    source_root: Path,
    manifest_root: Path,
    identity_root: Path,
    source_manifest_sha256: str,
    source_completion_index_sha256: str,
    identity_bundle_sha256: str,
) -> VerifiedMatchContext:
    """Load the sole selected match only after exact source/identity/event equality."""

    source = _require_exact_absolute_root(source_root, _SOURCE_ROOT_RELATIVE, context="source root")
    manifests = _require_exact_absolute_root(
        manifest_root, _MANIFEST_ROOT_RELATIVE, context="manifest root"
    )
    identities = _require_exact_absolute_root(
        identity_root, _IDENTITY_ROOT_RELATIVE, context="identity root"
    )
    if (
        type(source_manifest_sha256) is not str
        or source_manifest_sha256 != SOURCE_MANIFEST_SHA256
        or type(source_completion_index_sha256) is not str
        or source_completion_index_sha256 != SOURCE_COMPLETION_INDEX_SHA256
        or type(identity_bundle_sha256) is not str
        or identity_bundle_sha256 != IDENTITY_BUNDLE_SHA256
    ):
        raise WyscoutVerticalSliceContextError("context authority digest argument drifted")

    rows = _decode_match_member(_read_exact_match_member(source))
    raw_match, canonical_raw_match = _validate_selected_match(rows)
    season_id = bounded_season_uuid(raw_match["seasonId"])
    if season_id != SEASON_ID:
        raise WyscoutVerticalSliceContextError("accepted season UUID binding drifted")

    identity_build = identity.load_initial_identity_bundle(
        source_root=source,
        manifest_root=manifests,
        identity_root=identities,
        identity_bundle_sha256=identity_bundle_sha256,
    )
    if (
        identity_build.bundle_sha256 != IDENTITY_BUNDLE_SHA256
        or identity_build.bundle_id != IDENTITY_BUNDLE_ID
        or identity_build.bundle.source_manifest_id != SOURCE_MANIFEST_ID
        or identity_build.bundle.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
    ):
        raise WyscoutVerticalSliceContextError("accepted identity bundle binding drifted")

    match = _identity_binding(
        identity_build,
        entity_kind=WyscoutIdentityEntityKind.MATCH,
        source_id=MATCH_SOURCE_ID,
        canonical_id=MATCH_ID,
    )
    competition = _identity_binding(
        identity_build,
        entity_kind=WyscoutIdentityEntityKind.COMPETITION,
        source_id=COMPETITION_SOURCE_ID,
        canonical_id=COMPETITION_ID,
    )
    teams = cast(
        tuple[VerifiedIdentityBinding, VerifiedIdentityBinding],
        tuple(
            _identity_binding(
                identity_build,
                entity_kind=WyscoutIdentityEntityKind.TEAM,
                source_id=source_id,
                canonical_id=canonical_id,
            )
            for source_id, canonical_id in zip(TEAM_SOURCE_IDS, TEAM_IDS, strict=True)
        ),
    )
    target_player = _identity_binding(
        identity_build,
        entity_kind=WyscoutIdentityEntityKind.PLAYER,
        source_id=TARGET_PLAYER_SOURCE_ID,
        canonical_id=TARGET_PLAYER_ID,
    )

    event_population = completion.load_verified_match_population(
        source_root=source,
        manifest_root=manifests,
        index_sha256=source_completion_index_sha256,
        source_member_path=EVENT_MEMBER_PATH,
        match_source_id=MATCH_SOURCE_ID,
    )
    period_counts, period_digests = _validate_event_population(event_population)
    immutable_raw = completion._immutable_json(raw_match)
    if not isinstance(immutable_raw, Mapping):
        raise AssertionError("immutable selected match unexpectedly ceased to be a mapping")
    match_source_row = WyscoutSourceRowReference(
        source_manifest_id=SOURCE_MANIFEST_ID,
        completion_relative_path=MATCH_MEMBER_PATH,
        source_sha256=MATCH_MEMBER_SHA256,
        source_record_ordinal=MATCH_SOURCE_RECORD_ORDINAL,
        record_kind=SourceRecordKind.MATCH,
        raw_record_sha256=MATCH_RAW_RECORD_SHA256,
    )
    return VerifiedMatchContext(
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        identity_bundle_id=IDENTITY_BUNDLE_ID,
        identity_bundle_sha256=IDENTITY_BUNDLE_SHA256,
        match_source_row=match_source_row,
        match=match,
        competition=competition,
        season_source_id=SEASON_SOURCE_ID,
        season_id=season_id,
        teams=teams,
        target_team=teams[1],
        target_player=target_player,
        match_start_utc=MATCH_START_UTC,
        target_substitution_minute=82,
        raw_match=cast(Mapping[str, object], immutable_raw),
        canonical_raw_match=canonical_raw_match,
        event_population=event_population,
        period_action_counts=period_counts,
        period_membership_sha256=period_digests,
    )


__all__ = [
    "VerifiedIdentityBinding",
    "VerifiedMatchContext",
    "WyscoutVerticalSliceContextError",
    "WyscoutVerticalSliceContextPathError",
    "load_verified_match_context",
]

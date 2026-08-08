"""Verified local adapter for the retained five-league Wyscout snapshot.

The adapter is deliberately narrower than a general JSON reader.  Production
construction accepts only the frozen W04 roots and authorities.  Tests may use the
explicit ``from_test_fixture`` boundary; that boundary is never selected implicitly.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import duckdb
import pyarrow as pa  # type: ignore[import-untyped]

from scouting.contracts.wyscout_identity import (
    WyscoutIdentityBundle,
    WyscoutIdentityEntityKind,
    WyscoutIdentityState,
)
from scouting.sources import wyscout_manifest as source_bridge
from scouting.sources.wyscout_completion_index import (
    SourceCompletionIndex,
    load_source_completion_index,
)
from scouting.storage.formats import canonical_json_bytes

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = PROJECT_ROOT / "data/source/wyscout/v5"
SOURCE_MANIFEST_ROOT = PROJECT_ROOT / "data/manifests"
IDENTITY_ROOT = PROJECT_ROOT / "data/working/wyscout/v5/identity"

SOURCE_MANIFEST_ID = "4e16bdb5-afe7-5601-88ad-adc124cfce3b"
SOURCE_MANIFEST_SHA256 = "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
SOURCE_COMPLETION_INDEX_SHA256 = "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
IDENTITY_BUNDLE_SHA256 = "4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80"
SOURCE_AVAILABLE_AT = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
IDENTITY_AVAILABLE_AT = datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC)
SOURCE_MATCH_COUNT = 1_826
SOURCE_ACTION_COUNT = 3_071_395
SOURCE_TEAM_COUNT = 142
SOURCE_PLAYER_COUNT = 3_603
RESOLVED_COMPETITION_COUNT = 7
UNRESOLVED_PLAYER_COUNT = 15
REJECTED_PLAYER_COUNT = 1
ZERO_ACTOR_ACTION_COUNT = 226_038
EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS: Mapping[str, int] = {
    "England": 1_558,
    "France": 1_543,
    "Germany": 1_219,
    "Italy": 1_620,
    "Spain": 1_881,
}
EMPTY_SUB_EVENT_ID_SENTINEL_COUNT = 7_821
_EMPTY_SUB_EVENT_SENTINEL_FIELD = "adapter_sub_event_id_was_empty_string"
ATTRIBUTION = (
    "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
    "Wyscout, figshare collection v5, licensed CC BY 4.0."
)
RIGHTS_CLASSIFICATION = "wyscout_figshare_v5_cc_by_4"


class WyscoutHistoricalError(RuntimeError):
    """Raised when a retained authority or a canonical source invariant fails."""


class WyscoutHistoricalPathError(WyscoutHistoricalError):
    """Raised when production construction is asked to use any other root."""


@dataclass(frozen=True, slots=True)
class HistoricalPartition:
    """One exact admitted league pair."""

    name: str
    match_relative_path: str
    match_sha256: str
    match_count: int
    action_relative_path: str
    action_sha256: str
    action_count: int


ADMITTED_PARTITIONS = (
    HistoricalPartition(
        "England",
        "archive-members/matches_England.json",
        "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29",
        380,
        "archive-members/events_England.json",
        "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad",
        643_150,
    ),
    HistoricalPartition(
        "France",
        "archive-members/matches_France.json",
        "851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea",
        380,
        "archive-members/events_France.json",
        "18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317",
        632_807,
    ),
    HistoricalPartition(
        "Germany",
        "archive-members/matches_Germany.json",
        "6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9",
        306,
        "archive-members/events_Germany.json",
        "2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3",
        519_407,
    ),
    HistoricalPartition(
        "Italy",
        "archive-members/matches_Italy.json",
        "afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725",
        380,
        "archive-members/events_Italy.json",
        "b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84",
        647_372,
    ),
    HistoricalPartition(
        "Spain",
        "archive-members/matches_Spain.json",
        "9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce",
        380,
        "archive-members/events_Spain.json",
        "b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154",
        628_659,
    ),
)


@dataclass(frozen=True, slots=True)
class CatalogueSpec:
    relative_path: str
    sha256: str
    row_count: int


CATALOGUES: dict[str, CatalogueSpec] = {
    "competitions": CatalogueSpec(
        "objects/competitions.json",
        "39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1",
        7,
    ),
    "teams": CatalogueSpec(
        "objects/teams.json",
        "9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d",
        SOURCE_TEAM_COUNT,
    ),
    "players": CatalogueSpec(
        "objects/players.json",
        "877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e",
        SOURCE_PLAYER_COUNT,
    ),
}


@dataclass(frozen=True, slots=True)
class HistoricalIdentityAuthority:
    """Accepted source-key resolutions and visible fail-closed exclusions."""

    resolved: Mapping[WyscoutIdentityEntityKind, Mapping[int, str]]
    unresolved_player_source_ids: frozenset[int]
    rejected_player_source_ids: frozenset[int]
    player_source_reference_counts: Mapping[int, int]
    bundle_sha256: str
    available_at: datetime

    def canonical_id(self, entity_kind: WyscoutIdentityEntityKind, source_id: int) -> str | None:
        return self.resolved.get(entity_kind, {}).get(source_id)


@dataclass(frozen=True, slots=True)
class HistoricalPopulationAudit:
    action_count: int
    unique_action_count: int
    zero_actor_action_count: int
    match_ids_by_partition: Mapping[str, frozenset[int]]


@dataclass(frozen=True, slots=True)
class _RegularFileFingerprint:
    device: int
    inode: int
    mode: int
    link_count: int
    size_bytes: int
    modified_at_ns: int


@dataclass(frozen=True, slots=True)
class _FixtureData:
    catalogues: Mapping[str, tuple[dict[str, object], ...]]
    matches: Mapping[str, tuple[dict[str, object], ...]]
    actions: Mapping[str, tuple[dict[str, object], ...]]


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise WyscoutHistoricalError(f"source JSON repeats key {key!r}")
        value[key] = item
    return value


def _stable_regular_bytes(path: Path) -> bytes:
    try:
        before = path.stat(follow_symlinks=False)
    except FileNotFoundError as exc:
        raise WyscoutHistoricalError(f"required retained file is absent: {path}") from exc
    if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode):
        raise WyscoutHistoricalPathError(f"retained authority is not a regular file: {path}")
    with path.open("rb") as handle:
        payload = handle.read()
    after = path.stat(follow_symlinks=False)
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable):
        raise WyscoutHistoricalError(f"retained authority changed during read: {path}")
    return payload


def _regular_file_fingerprint(path: Path) -> _RegularFileFingerprint:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, os.O_RDONLY | nofollow)
    except FileNotFoundError as exc:
        raise WyscoutHistoricalError(f"required retained file is absent: {path}") from exc
    except OSError as exc:
        raise WyscoutHistoricalPathError(
            f"retained action path cannot be opened without following links: {path}"
        ) from exc
    try:
        metadata = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if not stat.S_ISREG(metadata.st_mode):
        raise WyscoutHistoricalPathError(f"retained action is not a regular file: {path}")
    return _RegularFileFingerprint(
        device=metadata.st_dev,
        inode=metadata.st_ino,
        mode=metadata.st_mode,
        link_count=metadata.st_nlink,
        size_bytes=metadata.st_size,
        modified_at_ns=metadata.st_mtime_ns,
    )


def _require_unchanged_regular_file(path: Path, expected: _RegularFileFingerprint) -> None:
    if _regular_file_fingerprint(path) != expected:
        raise WyscoutHistoricalError(
            f"retained action changed after authority verification: {path}"
        )


def _decode_array(payload: bytes, *, context: str) -> tuple[dict[str, object], ...]:
    try:
        decoded = json.loads(
            payload,
            parse_float=Decimal,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutHistoricalError(f"{context} is not strict JSON") from exc
    if type(decoded) is not list or any(type(row) is not dict for row in decoded):
        raise WyscoutHistoricalError(f"{context} must be one JSON array of objects")
    return tuple(cast(list[dict[str, object]], decoded))


def _optional_sub_event_id(
    value: object,
    *,
    encoded_json_token: bool,
) -> tuple[int | None, bool]:
    """Project the one admitted optional sentinel to the int-or-null contract."""

    projected = value
    if encoded_json_token and value is not None:
        if type(value) is not str:
            raise WyscoutHistoricalError("action.subEventId JSON token must be text")
        try:
            projected = json.loads(value, parse_float=Decimal)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise WyscoutHistoricalError("action.subEventId JSON token is invalid") from exc
    if projected is None:
        return None, False
    if type(projected) is int:
        return projected, False
    if type(projected) is str and projected == "":
        return None, True
    raise WyscoutHistoricalError(
        "action.subEventId must be a strict integer, null, or the exact empty sentinel"
    )


def _normalise_action_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    encoded_json_token: bool,
) -> tuple[list[dict[str, object]], int]:
    result: list[dict[str, object]] = []
    sentinel_count = 0
    for row in rows:
        if _EMPTY_SUB_EVENT_SENTINEL_FIELD in row:
            raise WyscoutHistoricalError("source action uses a reserved adapter field")
        sub_event_id, was_empty = _optional_sub_event_id(
            row.get("subEventId"),
            encoded_json_token=encoded_json_token,
        )
        projected = dict(row)
        projected["subEventId"] = sub_event_id
        projected[_EMPTY_SUB_EVENT_SENTINEL_FIELD] = was_empty
        if not encoded_json_token:
            positions = projected.get("positions")
            if positions is not None:
                if not isinstance(positions, (list, tuple)):
                    raise WyscoutHistoricalError("action positions are not an array")
                for point in positions:
                    if type(point) is not dict:
                        raise WyscoutHistoricalError("action position is not an object")
                    mapping = cast(dict[str, object], point)
                    _strict_int(mapping.get("x"), context="action position.x")
                    _strict_int(mapping.get("y"), context="action position.y")
        sentinel_count += int(was_empty)
        result.append(projected)
    return result, sentinel_count


def _source_id(row: Mapping[str, object], *, prefix: str) -> int:
    source_identity = row.get("source_identity")
    if type(source_identity) is not dict:
        raise WyscoutHistoricalError("identity row lacks exact source_identity")
    raw = cast(dict[str, object], source_identity).get("source_id")
    if type(raw) is not str or not raw.startswith(prefix + ":"):
        raise WyscoutHistoricalError("identity source kind differs from row kind")
    token = raw.removeprefix(prefix + ":")
    if not token.isascii() or not token.isdecimal():
        raise WyscoutHistoricalError("identity source ID is not canonical decimal text")
    return int(token)


class WyscoutHistoricalAdapter:
    """Read canonical-source inputs only after all declared authorities agree."""

    def __init__(
        self,
        *,
        source_root: Path,
        manifest_root: Path,
        identity_root: Path,
        fixture_data: _FixtureData | None = None,
        fixture_identity: HistoricalIdentityAuthority | None = None,
        fixture_partitions: Sequence[HistoricalPartition] | None = None,
    ) -> None:
        self.source_root = source_root
        self.manifest_root = manifest_root
        self.identity_root = identity_root
        self._fixture_data = fixture_data
        self._fixture_identity = fixture_identity
        self.partitions = tuple(fixture_partitions or ADMITTED_PARTITIONS)
        self._verified_identity: HistoricalIdentityAuthority | None = None
        self._completion_index: SourceCompletionIndex | None = None
        self._action_fingerprints: dict[str, _RegularFileFingerprint] = {}

    @classmethod
    def retained(cls) -> WyscoutHistoricalAdapter:
        """Construct the sole production adapter over the retained local roots."""

        return cls(
            source_root=SOURCE_ROOT,
            manifest_root=SOURCE_MANIFEST_ROOT,
            identity_root=IDENTITY_ROOT,
        )

    @classmethod
    def from_test_fixture(
        cls,
        *,
        catalogues: Mapping[str, Sequence[Mapping[str, object]]],
        matches: Mapping[str, Sequence[Mapping[str, object]]],
        actions: Mapping[str, Sequence[Mapping[str, object]]],
        identity: HistoricalIdentityAuthority,
        partitions: Sequence[HistoricalPartition],
    ) -> WyscoutHistoricalAdapter:
        """Construct an unmistakable automated-test-only adapter."""

        names = tuple(partition.name for partition in partitions)
        if set(matches) != set(names) or set(actions) != set(names):
            raise WyscoutHistoricalError("fixture partitions do not align")
        if set(catalogues) != set(CATALOGUES):
            raise WyscoutHistoricalError("fixture catalogues must declare all three kinds")
        fixture = _FixtureData(
            catalogues={key: tuple(dict(row) for row in rows) for key, rows in catalogues.items()},
            matches={key: tuple(dict(row) for row in rows) for key, rows in matches.items()},
            actions={key: tuple(dict(row) for row in rows) for key, rows in actions.items()},
        )
        return cls(
            source_root=Path("/__w09_test_fixture_source__"),
            manifest_root=Path("/__w09_test_fixture_manifests__"),
            identity_root=Path("/__w09_test_fixture_identity__"),
            fixture_data=fixture,
            fixture_identity=identity,
            fixture_partitions=partitions,
        )

    @property
    def is_test_fixture(self) -> bool:
        return self._fixture_data is not None

    @property
    def identity(self) -> HistoricalIdentityAuthority:
        if self._verified_identity is None:
            raise WyscoutHistoricalError("adapter must be verified before identity access")
        return self._verified_identity

    def verify(self) -> WyscoutHistoricalAdapter:
        """Reconcile source, completion and identity authorities before any row read."""

        if self._fixture_data is not None:
            if self._fixture_identity is None:
                raise WyscoutHistoricalError("fixture identity authority is absent")
            self._validate_fixture_counts()
            self._verified_identity = self._fixture_identity
            return self
        if (
            self.source_root != SOURCE_ROOT
            or self.manifest_root != SOURCE_MANIFEST_ROOT
            or self.identity_root != IDENTITY_ROOT
        ):
            raise WyscoutHistoricalPathError("production roots must be the exact retained roots")
        manifest = source_bridge.build_source_snapshot_manifest(
            source_root=self.source_root,
            tenant_id=source_bridge._TENANT_ID,
        )
        payload = canonical_json_bytes(manifest.model_dump(mode="json"))
        if (
            str(manifest.manifest_id) != SOURCE_MANIFEST_ID
            or hashlib.sha256(payload).hexdigest() != SOURCE_MANIFEST_SHA256
            or manifest.available_at != SOURCE_AVAILABLE_AT
        ):
            raise WyscoutHistoricalError("retained source manifest authority drifted")
        self._completion_index = load_source_completion_index(
            manifest_root=self.manifest_root,
            index_sha256=SOURCE_COMPLETION_INDEX_SHA256,
        )
        if self._completion_index.aggregate_action_count != SOURCE_ACTION_COUNT:
            raise WyscoutHistoricalError("completion action count drifted")
        self._verify_completion_partitions(self._completion_index)
        self._action_fingerprints = {
            partition.action_relative_path: _regular_file_fingerprint(
                self.source_root / partition.action_relative_path
            )
            for partition in self.partitions
        }
        self._verified_identity = self._load_identity_authority()
        return self

    def _validate_fixture_counts(self) -> None:
        fixture = self._fixture_data
        if fixture is None:
            raise WyscoutHistoricalError("fixture validation requires explicit fixture data")
        for partition in self.partitions:
            if len(fixture.matches[partition.name]) != partition.match_count:
                raise WyscoutHistoricalError("fixture match count differs from its authority")
            if len(fixture.actions[partition.name]) != partition.action_count:
                raise WyscoutHistoricalError("fixture action count differs from its authority")

    def _verify_completion_partitions(self, index: SourceCompletionIndex) -> None:
        indexed = {member.path: member for member in index.members}
        if set(indexed) != {partition.action_relative_path for partition in self.partitions}:
            raise WyscoutHistoricalError("completion index is not the exact five-partition set")
        for partition in self.partitions:
            member = indexed[partition.action_relative_path]
            if (
                member.sha256 != partition.action_sha256
                or member.row_count != partition.action_count
                or member.indexed_action_count != partition.action_count
            ):
                raise WyscoutHistoricalError(f"completion binding drifted for {partition.name}")

    def _load_identity_authority(self) -> HistoricalIdentityAuthority:
        path = self.identity_root / "bundles" / (f"{IDENTITY_BUNDLE_SHA256}.identity-bundle.json")
        payload = _stable_regular_bytes(path)
        if hashlib.sha256(payload).hexdigest() != IDENTITY_BUNDLE_SHA256:
            raise WyscoutHistoricalError("accepted identity bundle bytes drifted")
        try:
            bundle = WyscoutIdentityBundle.model_validate_json(payload, strict=True)
        except ValueError as exc:
            raise WyscoutHistoricalError("accepted identity bundle contract failed") from exc
        if (
            str(bundle.source_manifest_id) != SOURCE_MANIFEST_ID
            or bundle.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
            or bundle.available_at != IDENTITY_AVAILABLE_AT
        ):
            raise WyscoutHistoricalError("identity authority binding drifted")
        resolved: dict[WyscoutIdentityEntityKind, dict[int, str]] = {
            kind: {} for kind in WyscoutIdentityEntityKind
        }
        unresolved: set[int] = set()
        rejected: set[int] = set()
        reference_counts: dict[int, int] = {}
        for row in bundle.current_rows:
            source_id = _source_id(
                row.model_dump(mode="python"),
                prefix=row.entity_kind.value.lower(),
            )
            if row.state is WyscoutIdentityState.RESOLVED:
                if row.canonical_id is None:
                    raise WyscoutHistoricalError("resolved identity lacks canonical UUID")
                resolved[row.entity_kind][source_id] = str(row.canonical_id)
            elif row.state is WyscoutIdentityState.REVIEW_REQUIRED:
                unresolved.add(source_id)
                reference_counts[source_id] = len(row.source_row_refs)
            elif row.state is WyscoutIdentityState.REJECTED:
                rejected.add(source_id)
                reference_counts[source_id] = len(row.source_row_refs)
        expected_counts = {
            WyscoutIdentityEntityKind.COMPETITION: RESOLVED_COMPETITION_COUNT,
            WyscoutIdentityEntityKind.TEAM: SOURCE_TEAM_COUNT,
            WyscoutIdentityEntityKind.PLAYER: SOURCE_PLAYER_COUNT,
            WyscoutIdentityEntityKind.MATCH: SOURCE_MATCH_COUNT,
        }
        if any(len(resolved[kind]) != count for kind, count in expected_counts.items()):
            raise WyscoutHistoricalError("resolved identity counts drifted")
        if len(unresolved) != UNRESOLVED_PLAYER_COUNT or rejected != {0}:
            raise WyscoutHistoricalError("player identity exclusions drifted")
        return HistoricalIdentityAuthority(
            resolved=resolved,
            unresolved_player_source_ids=frozenset(unresolved),
            rejected_player_source_ids=frozenset(rejected),
            player_source_reference_counts=reference_counts,
            bundle_sha256=IDENTITY_BUNDLE_SHA256,
            available_at=IDENTITY_AVAILABLE_AT,
        )

    def load_catalogue(self, kind: str) -> tuple[dict[str, object], ...]:
        self._require_verified()
        if kind not in CATALOGUES:
            raise WyscoutHistoricalError(f"unsupported catalogue kind: {kind}")
        if self._fixture_data is not None:
            return self._fixture_data.catalogues[kind]
        spec = CATALOGUES[kind]
        payload = _stable_regular_bytes(self.source_root / spec.relative_path)
        if hashlib.sha256(payload).hexdigest() != spec.sha256:
            raise WyscoutHistoricalError(f"{kind} catalogue checksum drifted")
        rows = _decode_array(payload, context=spec.relative_path)
        if len(rows) != spec.row_count:
            raise WyscoutHistoricalError(f"{kind} catalogue count drifted")
        return rows

    def load_partition_matches(
        self, partition: HistoricalPartition
    ) -> tuple[dict[str, object], ...]:
        self._require_partition(partition)
        if self._fixture_data is not None:
            return self._fixture_data.matches[partition.name]
        payload = _stable_regular_bytes(self.source_root / partition.match_relative_path)
        if hashlib.sha256(payload).hexdigest() != partition.match_sha256:
            raise WyscoutHistoricalError(f"{partition.name} match checksum drifted")
        rows = _decode_array(payload, context=partition.match_relative_path)
        if len(rows) != partition.match_count:
            raise WyscoutHistoricalError(f"{partition.name} match count drifted")
        return rows

    def iter_partition_action_batches(
        self,
        partition: HistoricalPartition,
        *,
        batch_size: int = 65_536,
    ) -> Iterator[pa.RecordBatch]:
        """Yield one exact admitted member in source order, never via a glob."""

        self._require_partition(partition)
        if type(batch_size) is not int or batch_size < 1:
            raise WyscoutHistoricalError("action batch size must be a positive integer")
        if self._fixture_data is not None:
            rows = self._fixture_data.actions[partition.name]
            for start in range(0, len(rows), batch_size):
                raw_projected = [
                    {"source_record_ordinal": index, **row}
                    for index, row in enumerate(rows[start : start + batch_size], start=start)
                ]
                projected, _sentinel_count = _normalise_action_rows(
                    raw_projected,
                    encoded_json_token=False,
                )
                yield pa.RecordBatch.from_pylist(projected)
            return
        path = self.source_root / partition.action_relative_path
        self._require_action_fingerprint(partition)
        connection = duckdb.connect(database=":memory:")
        try:
            connection.execute("SET preserve_insertion_order = true")
            reader = connection.execute(
                "SELECT row_number() OVER () - 1 AS source_record_ordinal, * "
                "FROM read_json_auto(?, format='array')",
                [os.fspath(path)],
            ).fetch_record_batch(rows_per_batch=batch_size)
            observed = 0
            empty_sub_event_sentinels = 0
            for batch in reader:
                observed += batch.num_rows
                projected, batch_sentinel_count = _normalise_action_rows(
                    batch.to_pylist(),
                    encoded_json_token=True,
                )
                empty_sub_event_sentinels += batch_sentinel_count
                yield pa.RecordBatch.from_pylist(projected)
            if observed != partition.action_count:
                raise WyscoutHistoricalError(f"{partition.name} yielded action count drifted")
            expected_sentinels = EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS[partition.name]
            if empty_sub_event_sentinels != expected_sentinels:
                raise WyscoutHistoricalError(
                    f"{partition.name} empty subEventId sentinel count drifted"
                )
        finally:
            try:
                connection.close()
            finally:
                self._require_action_fingerprint(partition)

    def audit_action_population(self) -> HistoricalPopulationAudit:
        """Prove uniqueness and partition/match alignment before materialization."""

        self._require_verified()
        if self._fixture_data is None:
            return self._audit_retained_action_population()
        action_ids: set[int] = set()
        match_ids_by_partition: dict[str, frozenset[int]] = {}
        zero_count = 0
        action_count = 0
        for partition in self.partitions:
            partition_matches: set[int] = set()
            for batch in self.iter_partition_action_batches(partition):
                for row in batch.to_pylist():
                    action_id = _strict_int(row.get("id"), context="action.id")
                    match_id = _strict_int(row.get("matchId"), context="action.matchId")
                    player_id = _strict_int(row.get("playerId"), context="action.playerId")
                    if action_id in action_ids:
                        raise WyscoutHistoricalError("source action ID is duplicated")
                    action_ids.add(action_id)
                    partition_matches.add(match_id)
                    action_count += 1
                    zero_count += int(player_id == 0)
            match_ids_by_partition[partition.name] = frozenset(partition_matches)
            declared_match_ids = {
                _strict_int(row.get("wyId"), context="match.wyId")
                for row in self.load_partition_matches(partition)
            }
            if partition_matches != declared_match_ids:
                raise WyscoutHistoricalError(
                    f"event/match partition alignment failed for {partition.name}"
                )
        return HistoricalPopulationAudit(
            action_count=action_count,
            unique_action_count=len(action_ids),
            zero_actor_action_count=zero_count,
            match_ids_by_partition=match_ids_by_partition,
        )

    def _audit_retained_action_population(self) -> HistoricalPopulationAudit:
        self._require_all_action_fingerprints()
        partitions_by_path = {
            os.fspath(self.source_root / partition.action_relative_path): partition
            for partition in self.partitions
        }
        paths = list(partitions_by_path)
        connection = duckdb.connect(database=":memory:")
        try:
            aggregates = connection.execute(
                "WITH actions AS ("
                "SELECT * FROM read_json_auto(?, format='array', filename=true)"
                ") "
                "SELECT filename, count(*), count(DISTINCT id), "
                "count_if(playerId = 0), list_sort(list(DISTINCT matchId)) "
                "FROM actions GROUP BY GROUPING SETS ((filename), ()) "
                "ORDER BY filename NULLS FIRST",
                [paths],
            ).fetchall()
            if len(aggregates) != len(self.partitions) + 1 or aggregates[0][0] is not None:
                raise WyscoutHistoricalError("retained action aggregate is absent")
            action_count, unique_count, zero_count = (
                strict_int(value, context="retained action aggregate")
                for value in aggregates[0][1:4]
            )
            match_ids_by_partition: dict[str, frozenset[int]] = {}
            seen_paths: set[str] = set()
            for raw_path, _count, _unique_count, _zero_count, raw_match_ids in aggregates[1:]:
                action_path = str(raw_path)
                partition = partitions_by_path.get(action_path)
                if partition is None or action_path in seen_paths:
                    raise WyscoutHistoricalError("retained action partition aggregate drifted")
                seen_paths.add(action_path)
                action_match_ids = frozenset(
                    strict_int(value, context="action.matchId") for value in raw_match_ids
                )
                declared_match_ids = frozenset(
                    strict_int(row.get("wyId"), context="match.wyId")
                    for row in self.load_partition_matches(partition)
                )
                if action_match_ids != declared_match_ids:
                    raise WyscoutHistoricalError(
                        f"event/match partition alignment failed for {partition.name}"
                    )
                match_ids_by_partition[partition.name] = action_match_ids
            if seen_paths != set(partitions_by_path):
                raise WyscoutHistoricalError("retained action partition aggregate is incomplete")
        finally:
            try:
                connection.close()
            finally:
                self._require_all_action_fingerprints()
        if (
            action_count != SOURCE_ACTION_COUNT
            or unique_count != SOURCE_ACTION_COUNT
            or zero_count != ZERO_ACTOR_ACTION_COUNT
        ):
            raise WyscoutHistoricalError("full action population reconciliation drifted")
        return HistoricalPopulationAudit(
            action_count=action_count,
            unique_action_count=unique_count,
            zero_actor_action_count=zero_count,
            match_ids_by_partition=match_ids_by_partition,
        )

    def _require_action_fingerprint(self, partition: HistoricalPartition) -> None:
        expected = self._action_fingerprints.get(partition.action_relative_path)
        if expected is None:
            raise WyscoutHistoricalError("retained action fingerprint authority is absent")
        _require_unchanged_regular_file(
            self.source_root / partition.action_relative_path,
            expected,
        )

    def _require_all_action_fingerprints(self) -> None:
        for partition in self.partitions:
            self._require_action_fingerprint(partition)

    def _require_partition(self, partition: HistoricalPartition) -> None:
        self._require_verified()
        if partition not in self.partitions:
            raise WyscoutHistoricalError("partition is not admitted by this adapter")
        for relative in (partition.match_relative_path, partition.action_relative_path):
            if relative.endswith(".manifest.json") or "*" in relative or "?" in relative:
                raise WyscoutHistoricalPathError("admitted source paths must be exact payloads")

    def _require_verified(self) -> None:
        if self._verified_identity is None:
            raise WyscoutHistoricalError("adapter authority must be verified before rows")


def _strict_int(value: object, *, context: str) -> int:
    if type(value) is not int:
        raise WyscoutHistoricalError(f"{context} must be a strict integer")
    return value


def strict_int(value: object, *, context: str) -> int:
    """Public strict projection helper shared with the canonical producer."""

    return _strict_int(value, context=context)


def strict_decimal(value: object, *, context: str) -> Decimal:
    """Return a finite source number without Boolean/string coercion."""

    if type(value) is int:
        return Decimal(value)
    if type(value) is float:
        projected = Decimal(str(value))
    elif type(value) is Decimal:
        projected = value
    else:
        raise WyscoutHistoricalError(f"{context} must be a source JSON number")
    if not projected.is_finite():
        raise WyscoutHistoricalError(f"{context} must be finite")
    return projected


__all__ = [
    "ADMITTED_PARTITIONS",
    "ATTRIBUTION",
    "CATALOGUES",
    "EMPTY_SUB_EVENT_ID_SENTINEL_COUNT",
    "EMPTY_SUB_EVENT_ID_SENTINEL_COUNTS",
    "IDENTITY_AVAILABLE_AT",
    "IDENTITY_BUNDLE_SHA256",
    "PROJECT_ROOT",
    "REJECTED_PLAYER_COUNT",
    "RESOLVED_COMPETITION_COUNT",
    "RIGHTS_CLASSIFICATION",
    "SOURCE_ACTION_COUNT",
    "SOURCE_AVAILABLE_AT",
    "SOURCE_COMPLETION_INDEX_SHA256",
    "SOURCE_MANIFEST_ID",
    "SOURCE_MANIFEST_SHA256",
    "SOURCE_MATCH_COUNT",
    "SOURCE_PLAYER_COUNT",
    "SOURCE_TEAM_COUNT",
    "UNRESOLVED_PLAYER_COUNT",
    "ZERO_ACTOR_ACTION_COUNT",
    "HistoricalIdentityAuthority",
    "HistoricalPartition",
    "HistoricalPopulationAudit",
    "WyscoutHistoricalAdapter",
    "WyscoutHistoricalError",
    "WyscoutHistoricalPathError",
    "strict_decimal",
    "strict_int",
]

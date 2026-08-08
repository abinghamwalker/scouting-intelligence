"""Governed W09 historical player-window feature-matrix construction."""

from __future__ import annotations

import hashlib
import json
import math
import stat
import struct
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, Literal, cast
from uuid import NAMESPACE_URL, UUID, uuid5

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.compute as pc  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
from pydantic import ValidationError

from scouting.contracts.code_digest import governed_code_digest
from scouting.contracts.research import (
    EligibilityDecision,
    EligibilityReason,
    EligibilityReasonCount,
    FeatureMatrixManifest,
    FeatureMatrixRow,
    FeatureValueState,
    MatrixCatalogueEntry,
    MinuteEvidenceState,
    PopulationDecisionReason,
    ResearchArtifactFile,
    ResearchCoverage,
    ResearchFeatureValue,
    SourcePopulationDecision,
    canonical_research_digest,
    population_referred_grain_digest,
    rows_semantic_digest,
)
from scouting.storage.formats import canonical_json_bytes, canonical_jsonl_bytes
from scouting.storage.guarded import GuardedStorage

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CANONICAL_MANIFEST_ROOT = PROJECT_ROOT / "data/manifests/wyscout/v5/research"
DEFAULT_CANONICAL_ARTIFACT_ROOT = PROJECT_ROOT
DEFAULT_FEATURE_ROOT = PROJECT_ROOT / "data/working/wyscout/v5/research_features"
DEFAULT_FEATURE_MANIFEST_ROOT = PROJECT_ROOT / "data/manifests/wyscout/v5/research_features"
DEFAULT_REGISTRY_PATH = PROJECT_ROOT / "configs/features/w09-historical-player-window-v1.json"

CANONICAL_MANIFEST_SCHEMA_VERSION = "w09-historical-canonical-manifest-v1"
CANONICAL_SCHEMA_VERSION = "w09-historical-canonical-v1"
CANONICAL_BUILDER_VERSION = "w09-full-canonical-build-02b-r6-unicode"
FEATURE_MATRIX_VERSION = "w09-historical-player-window-v1"
FEATURE_CODE_VERSION = "w09-full-feature-matrix-02c-r1"
ELIGIBILITY_POLICY_VERSION = "w09-eligibility-v1"
MINIMUM_MINUTES = 450.0
CANONICAL_LOGICAL_PREFIX = "data/working/wyscout/v5/research/"
FEATURE_LOGICAL_PREFIX = "data/working/wyscout/v5/research_features/"

CANONICAL_ROLES = frozenset(
    {
        "canonical_competitions",
        "canonical_teams",
        "canonical_players",
        "canonical_matches",
        "canonical_actions",
        "canonical_appearances",
        "identity_exclusions",
    }
)
FEATURE_ARTIFACT_PATHS: Mapping[str, str] = {
    "player_catalogue": "player-catalogue.jsonl",
    "population_decisions": "population-decisions.jsonl",
    "eligibility_decisions": "eligibility-decisions.jsonl",
    "feature_matrix_rows": "feature-matrix-rows.parquet",
}
POSITION_CODES = frozenset({"GK", "DF", "MD", "FW"})
PLAYED_MINUTE_STATES = frozenset({"exact", "conservative_lower_bound"})

_STRING = pa.string()
_FEATURE_VALUE_TYPE = pa.struct(
    [
        pa.field("feature_name", _STRING, nullable=False),
        pa.field("state", _STRING, nullable=False),
        pa.field("value", pa.float64(), nullable=True),
        pa.field("numerator", pa.float64(), nullable=True),
        pa.field("denominator", pa.float64(), nullable=True),
        pa.field("reason", _STRING, nullable=True),
    ]
)
_COVERAGE_TYPE = pa.struct(
    [
        pa.field("lineup_matches_observed", pa.int64(), nullable=False),
        pa.field("lineup_matches_expected", pa.int64(), nullable=False),
        pa.field("action_matches_observed", pa.int64(), nullable=False),
        pa.field("action_matches_expected", pa.int64(), nullable=False),
        pa.field("coordinate_actions_observed", pa.int64(), nullable=False),
        pa.field("coordinate_actions_expected", pa.int64(), nullable=False),
    ]
)
_FEATURE_MATRIX_SCHEMA = pa.schema(
    [
        pa.field("schema_version", pa.int64(), nullable=False),
        pa.field("grain_id", _STRING, nullable=False),
        pa.field("player_id", _STRING, nullable=False),
        pa.field("display_name", _STRING, nullable=False),
        pa.field("competition_id", _STRING, nullable=False),
        pa.field("competition_name", _STRING, nullable=False),
        pa.field("season_id", _STRING, nullable=False),
        pa.field("position_code", _STRING, nullable=False),
        pa.field("team_ids", pa.list_(pa.field("item", _STRING, nullable=False)), nullable=False),
        pa.field("team_names", pa.list_(pa.field("item", _STRING, nullable=False)), nullable=False),
        pa.field("minute_state", _STRING, nullable=False),
        pa.field("minutes", pa.float64(), nullable=False),
        pa.field("match_count", pa.int64(), nullable=False),
        pa.field(
            "features",
            pa.list_(pa.field("item", _FEATURE_VALUE_TYPE, nullable=False)),
            nullable=False,
        ),
        pa.field(
            "missing_feature_names",
            pa.list_(pa.field("item", _STRING, nullable=False)),
            nullable=False,
        ),
        pa.field("coverage", _COVERAGE_TYPE, nullable=False),
        pa.field("window_start_utc", _STRING, nullable=False),
        pa.field("window_end_utc", _STRING, nullable=False),
        pa.field("feature_cutoff_ts", _STRING, nullable=False),
        pa.field("dataset_manifest_digest", _STRING, nullable=False),
        pa.field("identity_bundle_digest", _STRING, nullable=False),
        pa.field("canonical_build_digest", _STRING, nullable=False),
        pa.field("feature_registry_digest", _STRING, nullable=False),
        pa.field("eligibility_policy_digest", _STRING, nullable=False),
        pa.field("eligibility_decision_digest", _STRING, nullable=False),
        pa.field("source_lineage_digest", _STRING, nullable=False),
        pa.field("source_action_count", pa.int64(), nullable=False),
        pa.field("contains_synthetic_data", pa.bool_(), nullable=False),
    ]
)


class HistoricalFeatureBuildError(ValueError):
    """Raised before incompatible historical evidence can become a matrix."""


class HistoricalFeatureBuildMode(StrEnum):
    """Explicit separation between retained evidence and test fixtures."""

    PRODUCTION = "production"
    VERIFICATION = "verification"
    TEST_FIXTURE = "test_fixture"


@dataclass(frozen=True, slots=True)
class HistoricalFeatureDefinition:
    """One fixed ordered event-count predicate."""

    name: str
    event_id: int | None = None
    sub_event_id: int | None = None
    required_tag_id: int | None = None
    excluded_tag_id: int | None = None
    excluded_event_id: int | None = None

    def matches(self, action: Mapping[str, object]) -> bool:
        """Return whether a canonical action satisfies this exact predicate."""

        event_id = action.get("event_id")
        sub_event_id = action.get("sub_event_id")
        raw_tags = action.get("tag_ids")
        if not isinstance(raw_tags, list):
            raise HistoricalFeatureBuildError("canonical action tag_ids must be a list")
        if any(type(tag) is not int for tag in raw_tags):
            raise HistoricalFeatureBuildError("canonical action tag_ids must be strict integers")
        tags = set(cast(list[int], raw_tags))
        return (
            (self.event_id is None or event_id == self.event_id)
            and (self.excluded_event_id is None or event_id != self.excluded_event_id)
            and (self.sub_event_id is None or sub_event_id == self.sub_event_id)
            and (self.required_tag_id is None or self.required_tag_id in tags)
            and (self.excluded_tag_id is None or self.excluded_tag_id not in tags)
        )


@dataclass(frozen=True, slots=True)
class HistoricalFeatureRegistry:
    """Validated fixed registry and policy authority."""

    registry_version: str
    registry_digest: str
    window_start_utc: datetime
    window_end_utc: datetime
    feature_cutoff_ts: datetime
    eligibility_policy_digest: str
    features: tuple[HistoricalFeatureDefinition, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HistoricalFeatureBuildResult:
    """Immutable feature build receipts for master verification."""

    matrix_version: str
    matrix_manifest_path: Path
    matrix_manifest_sha256: str
    manifest: FeatureMatrixManifest


@dataclass(frozen=True, slots=True)
class _CanonicalDataset:
    manifest: Mapping[str, object]
    manifest_payload: bytes
    competitions: tuple[dict[str, object], ...]
    teams: tuple[dict[str, object], ...]
    players: tuple[dict[str, object], ...]
    matches: tuple[dict[str, object], ...]
    action_paths: tuple[Path, ...]
    action_count: int
    appearances: tuple[dict[str, object], ...]
    exclusions: tuple[dict[str, object], ...]


@dataclass(slots=True)
class _ActionAggregate:
    numerators: list[int]
    source_action_count: int
    coordinate_actions_observed: int
    match_ids: set[str]
    lineage_hasher: Any


type _Grain = tuple[UUID, UUID, str]


@dataclass(frozen=True, slots=True)
class _CanonicalLookups:
    competitions: Mapping[UUID, Mapping[str, object]]
    teams: Mapping[UUID, Mapping[str, object]]
    players: Mapping[UUID, Mapping[str, object]]
    matches: Mapping[UUID, Mapping[str, object]]
    catalogue: tuple[MatrixCatalogueEntry, ...]


@dataclass(frozen=True, slots=True)
class _AppearanceIndex:
    by_grain: Mapping[_Grain, tuple[dict[str, object], ...]]
    teams_by_grain_match: Mapping[tuple[_Grain, UUID], frozenset[UUID]]
    invalid_grains: frozenset[_Grain]


@dataclass(frozen=True, slots=True)
class _ActionScan:
    aggregates: Mapping[_Grain, _ActionAggregate]
    invalid_grains: frozenset[_Grain]


@dataclass(frozen=True, slots=True)
class _GrainLedgers:
    eligibility: tuple[EligibilityDecision, ...]
    matrix: tuple[FeatureMatrixRow, ...]
    player_grains: Mapping[UUID, tuple[str, ...]]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256_and_size(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _utc(value: object, *, label: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif type(value) is str:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HistoricalFeatureBuildError(f"{label} is not an ISO-8601 instant") from exc
    else:
        raise HistoricalFeatureBuildError(f"{label} is not a UTC instant")
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise HistoricalFeatureBuildError(f"{label} must be timezone-aware UTC")
    return parsed.astimezone(UTC)


def _json_object(payload: bytes, *, label: str) -> dict[str, object]:
    try:
        decoded = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HistoricalFeatureBuildError(f"{label} is not strict JSON") from exc
    if not isinstance(decoded, dict) or canonical_json_bytes(decoded) != payload:
        raise HistoricalFeatureBuildError(f"{label} is not one canonical JSON object")
    return cast(dict[str, object], decoded)


def _safe_path(root: Path, relative_path: str) -> Path:
    path = PurePosixPath(relative_path)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in relative_path.split("/")):
        raise HistoricalFeatureBuildError("canonical artifact path is unsafe")
    root_absolute = root.absolute()
    if not root_absolute.is_dir() or root_absolute.is_symlink():
        raise HistoricalFeatureBuildError("canonical artifact root is absent or unsafe")
    current = root_absolute
    for index, part in enumerate(relative_path.split("/")):
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError as exc:
            raise HistoricalFeatureBuildError(
                f"canonical artifact is absent: {relative_path}"
            ) from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise HistoricalFeatureBuildError("canonical artifact path contains a symlink")
        if index < len(relative_path.split("/")) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise HistoricalFeatureBuildError("canonical artifact parent is not a directory")
    if not stat.S_ISREG(current.lstat().st_mode):
        raise HistoricalFeatureBuildError("canonical artifact is not a regular file")
    return current


def _canonical_artifact_path(
    root: Path,
    logical_path: str,
    *,
    mode: HistoricalFeatureBuildMode,
) -> Path:
    relative = logical_path
    if mode is HistoricalFeatureBuildMode.TEST_FIXTURE:
        if not logical_path.startswith(CANONICAL_LOGICAL_PREFIX):
            raise HistoricalFeatureBuildError("fixture canonical path has an incompatible prefix")
        relative = logical_path.removeprefix(CANONICAL_LOGICAL_PREFIX)
    return _safe_path(root, relative)


def _all_equal(column: object, value: object) -> bool:
    result = pc.all(pc.equal(column, value)).as_py()
    return result is True


def _validate_action_authority_table(
    parquet_file: pq.ParquetFile,
    *,
    build_id: str,
    cutoff: datetime,
) -> None:
    columns = (
        "schema_version",
        "canonical_build_id",
        "source_available_at",
        "identity_available_at",
        "feature_cutoff_ts",
    )
    for batch in parquet_file.iter_batches(batch_size=65_536, columns=columns):
        if (
            not _all_equal(batch["schema_version"], CANONICAL_SCHEMA_VERSION)
            or not _all_equal(batch["canonical_build_id"], build_id)
            or not _all_equal(batch["feature_cutoff_ts"], cutoff)
            or pc.any(pc.greater_equal(batch["source_available_at"], cutoff)).as_py() is True
            or pc.any(pc.greater_equal(batch["identity_available_at"], cutoff)).as_py() is True
        ):
            raise HistoricalFeatureBuildError("canonical action authority drifted")


def _required_mapping(value: object, *, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise HistoricalFeatureBuildError(f"{label} must be an object")
    return cast(dict[str, object], value)


def _required_int(value: object, *, label: str) -> int:
    if type(value) is not int or value < 0:
        raise HistoricalFeatureBuildError(f"{label} must be a non-negative strict integer")
    return value


def _required_text(value: object, *, label: str) -> str:
    if type(value) is not str or not value:
        raise HistoricalFeatureBuildError(f"{label} must be non-empty text")
    return value


def load_historical_feature_registry(
    path: Path = DEFAULT_REGISTRY_PATH,
) -> HistoricalFeatureRegistry:
    """Load and validate the exact W09 feature order and eligibility policy."""

    payload = path.read_bytes()
    try:
        decoded = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HistoricalFeatureBuildError("historical feature registry is not strict JSON") from exc
    if not isinstance(decoded, dict):
        raise HistoricalFeatureBuildError("historical feature registry is not a JSON object")
    raw = cast(dict[str, object], decoded)
    if (
        raw.get("schema_version") != 1
        or raw.get("registry_id") != FEATURE_MATRIX_VERSION
        or raw.get("registry_version") != FEATURE_MATRIX_VERSION
    ):
        raise HistoricalFeatureBuildError("historical feature registry version is incompatible")
    policy = _required_mapping(raw.get("eligibility_policy"), label="eligibility policy")
    expected_policy = {
        "version": ELIGIBILITY_POLICY_VERSION,
        "minimum_minutes": MINIMUM_MINUTES,
        "played_minute_states": ["exact", "conservative_lower_bound"],
        "exact_total_requires_every_played_stint_exact": True,
        "all_unusable_is_unusable": True,
        "action_presence_used_for_minutes": False,
        "current_team_id_used_for_membership": False,
    }
    if policy != expected_policy:
        raise HistoricalFeatureBuildError("historical eligibility policy is incompatible")
    raw_features = raw.get("features")
    if not isinstance(raw_features, list):
        raise HistoricalFeatureBuildError("historical feature registry has no ordered features")
    definitions: list[HistoricalFeatureDefinition] = []
    for index, raw_feature in enumerate(raw_features):
        feature = _required_mapping(raw_feature, label=f"feature {index}")
        if feature.get("unit") != "count_per_90_governed_minutes":
            raise HistoricalFeatureBuildError("historical feature unit is incompatible")
        predicate = _required_mapping(feature.get("predicate"), label=f"feature {index} predicate")
        if not predicate or not set(predicate) <= {
            "event_id",
            "sub_event_id",
            "required_tag_id",
            "excluded_tag_id",
            "excluded_event_id",
        }:
            raise HistoricalFeatureBuildError("historical feature predicate is incompatible")
        if any(type(value) is not int for value in predicate.values()):
            raise HistoricalFeatureBuildError("historical feature predicate ids must be integers")
        definitions.append(
            HistoricalFeatureDefinition(
                name=_required_text(feature.get("name"), label=f"feature {index} name"),
                event_id=cast(int | None, predicate.get("event_id")),
                sub_event_id=cast(int | None, predicate.get("sub_event_id")),
                required_tag_id=cast(int | None, predicate.get("required_tag_id")),
                excluded_tag_id=cast(int | None, predicate.get("excluded_tag_id")),
                excluded_event_id=cast(int | None, predicate.get("excluded_event_id")),
            )
        )
    expected = (
        ("passes_per90", 8, None, None, None, None),
        ("accurate_passes_per90", 8, None, 1801, None, None),
        ("crosses_per90", 8, 80, None, None, None),
        ("smart_passes_per90", 8, 86, None, None, None),
        ("shots_per90", 10, None, None, None, None),
        ("shots_on_target_per90", 10, None, 1801, None, None),
        ("goals_per90", None, None, 101, 102, 9),
        ("key_passes_per90", None, None, 302, None, None),
        ("assists_per90", None, None, 301, None, None),
        ("duels_per90", 1, None, None, None, None),
        ("duels_won_per90", 1, None, 703, None, None),
        ("interceptions_per90", None, None, 1401, None, None),
        ("clearances_per90", None, 71, None, None, None),
        ("accelerations_per90", None, 70, None, None, None),
        ("fouls_per90", 2, None, None, None, None),
        ("touches_per90", None, 72, None, None, None),
    )
    observed = tuple(
        (
            item.name,
            item.event_id,
            item.sub_event_id,
            item.required_tag_id,
            item.excluded_tag_id,
            item.excluded_event_id,
        )
        for item in definitions
    )
    if observed != expected:
        raise HistoricalFeatureBuildError("historical feature order or predicates drifted")
    limitations = raw.get("limitations")
    if (
        not isinstance(limitations, list)
        or not limitations
        or any(type(item) is not str or not item for item in limitations)
    ):
        raise HistoricalFeatureBuildError("historical feature limitations are absent")
    return HistoricalFeatureRegistry(
        registry_version=FEATURE_MATRIX_VERSION,
        registry_digest=_sha256(canonical_json_bytes(raw)),
        window_start_utc=_utc(raw.get("window_start_utc"), label="registry window start"),
        window_end_utc=_utc(raw.get("window_end_utc"), label="registry window end"),
        feature_cutoff_ts=_utc(raw.get("feature_cutoff_ts"), label="registry cutoff"),
        eligibility_policy_digest=canonical_research_digest(policy),
        features=tuple(definitions),
        limitations=tuple(cast(list[str], limitations)),
    )


def feature_numerators(
    actions: Sequence[Mapping[str, object]],
    registry: HistoricalFeatureRegistry,
) -> tuple[int, ...]:
    """Count every coordinate-independent retained action by fixed predicate."""

    return tuple(
        sum(feature.matches(action) for action in actions) for feature in registry.features
    )


def aggregate_governed_minutes(
    appearances: Sequence[Mapping[str, object]],
) -> tuple[MinuteEvidenceState, float | None, int]:
    """Aggregate only canonical played stints without action-based inference."""

    played: list[tuple[str, float]] = []
    for appearance in appearances:
        state = appearance.get("minute_state")
        minutes = appearance.get("minutes")
        if state in PLAYED_MINUTE_STATES:
            if type(minutes) not in {int, float}:
                raise HistoricalFeatureBuildError("played appearance minutes are invalid")
            numeric_minutes = cast(int | float, minutes)
            if numeric_minutes < 0:
                raise HistoricalFeatureBuildError("played appearance minutes are invalid")
            played.append(
                (_required_text(state, label="played minute state"), float(numeric_minutes))
            )
        elif state == "unusable":
            if minutes is not None:
                raise HistoricalFeatureBuildError("unusable appearance carries minutes")
        else:
            raise HistoricalFeatureBuildError("appearance minute state is incompatible")
    if not played:
        return MinuteEvidenceState.UNUSABLE, None, 0
    total = float(math.fsum(minutes for _, minutes in played))
    state = (
        MinuteEvidenceState.EXACT
        if all(item_state == "exact" for item_state, _ in played)
        else MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND
    )
    return state, total, len(played)


def _load_canonical_dataset(
    manifest_path: Path,
    *,
    artifact_root: Path,
    mode: HistoricalFeatureBuildMode,
    registry: HistoricalFeatureRegistry,
) -> _CanonicalDataset:
    if mode in {
        HistoricalFeatureBuildMode.PRODUCTION,
        HistoricalFeatureBuildMode.VERIFICATION,
    } and (
        manifest_path.parent != DEFAULT_CANONICAL_MANIFEST_ROOT
        or artifact_root != DEFAULT_CANONICAL_ARTIFACT_ROOT
    ):
        raise HistoricalFeatureBuildError("production canonical roots must be exact")
    manifest_payload = _safe_path(manifest_path.parent, manifest_path.name).read_bytes()
    manifest = _json_object(manifest_payload, label="canonical manifest")
    if (
        manifest.get("schema_version") != 1
        or manifest.get("manifest_schema_version") != CANONICAL_MANIFEST_SCHEMA_VERSION
        or manifest.get("canonical_schema_version") != CANONICAL_SCHEMA_VERSION
        or manifest.get("builder_version") != CANONICAL_BUILDER_VERSION
    ):
        raise HistoricalFeatureBuildError("canonical manifest schema or builder is incompatible")
    fixture = manifest.get("test_fixture")
    if fixture is not (mode is HistoricalFeatureBuildMode.TEST_FIXTURE):
        raise HistoricalFeatureBuildError("canonical fixture boundary does not match build mode")
    rights = _required_mapping(manifest.get("rights"), label="canonical rights")
    if rights != {
        "classification": "wyscout_figshare_v5_cc_by_4",
        "attribution": (
            "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
            "Wyscout, figshare collection v5, licensed CC BY 4.0."
        ),
        "local_only": True,
        "raw_export_allowed": False,
    }:
        raise HistoricalFeatureBuildError("canonical rights authority is incompatible")
    authorities = _required_mapping(manifest.get("authorities"), label="canonical authorities")
    cutoff = _utc(authorities.get("feature_cutoff_ts"), label="canonical cutoff")
    source_available = _utc(authorities.get("source_available_at"), label="source authority")
    identity_available = _utc(authorities.get("identity_available_at"), label="identity authority")
    if (
        cutoff != registry.feature_cutoff_ts
        or max(source_available, identity_available) >= cutoff
        or registry.window_end_utc >= cutoff
    ):
        raise HistoricalFeatureBuildError("canonical temporal authority is stale or incompatible")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise HistoricalFeatureBuildError("canonical manifest has no artifacts")
    by_role: dict[str, list[dict[str, object]]] = defaultdict(list)
    for index, item in enumerate(artifacts):
        descriptor = _required_mapping(item, label=f"canonical artifact {index}")
        role = _required_text(descriptor.get("role"), label="canonical artifact role")
        if role not in CANONICAL_ROLES:
            raise HistoricalFeatureBuildError("canonical manifest has an unexpected role")
        by_role[role].append(descriptor)
    singleton_roles = CANONICAL_ROLES - {"canonical_actions"}
    if set(by_role) != CANONICAL_ROLES or any(len(by_role[role]) != 1 for role in singleton_roles):
        raise HistoricalFeatureBuildError("canonical artifact role coverage is incompatible")
    if not by_role["canonical_actions"]:
        raise HistoricalFeatureBuildError("canonical action partitions are absent")

    loaded: dict[str, list[dict[str, object]]] = defaultdict(list)
    loaded_counts: Counter[str] = Counter()
    action_paths: list[Path] = []
    build_id = _required_text(manifest.get("canonical_build_id"), label="canonical build id")
    seen_paths: set[str] = set()
    for role in sorted(by_role):
        for descriptor in by_role[role]:
            logical_path = _required_text(descriptor.get("path"), label="canonical artifact path")
            if logical_path in seen_paths:
                raise HistoricalFeatureBuildError("canonical manifest repeats an artifact path")
            seen_paths.add(logical_path)
            physical = _canonical_artifact_path(artifact_root, logical_path, mode=mode)
            physical_sha256, physical_size = _file_sha256_and_size(physical)
            if (
                physical_sha256 != descriptor.get("sha256")
                or physical_size != descriptor.get("size_bytes")
                or descriptor.get("schema_version") != CANONICAL_SCHEMA_VERSION
            ):
                raise HistoricalFeatureBuildError("canonical artifact physical authority drifted")
            # Read one exact file, not a partition-inferred dataset. Canonical action
            # paths deliberately contain ``source_partition=...`` while the file also
            # carries that governed column.
            parquet_file = pq.ParquetFile(physical)
            row_count = parquet_file.metadata.num_rows
            if row_count != descriptor.get("row_count"):
                raise HistoricalFeatureBuildError("canonical artifact row count drifted")
            if role == "canonical_actions":
                _validate_action_authority_table(
                    parquet_file,
                    build_id=build_id,
                    cutoff=cutoff,
                )
                action_paths.append(physical)
                loaded_counts[role] += row_count
                continue
            table = parquet_file.read()
            rows = [cast(dict[str, object], row) for row in table.to_pylist()]
            for row in rows:
                if row.get("schema_version") != CANONICAL_SCHEMA_VERSION:
                    raise HistoricalFeatureBuildError("canonical row schema version drifted")
                if "canonical_build_id" in row and row["canonical_build_id"] != build_id:
                    raise HistoricalFeatureBuildError("canonical row build id drifted")
                row_cutoff = _utc(row.get("feature_cutoff_ts"), label="canonical row cutoff")
                row_source = row.get("source_available_at")
                row_identity = row.get("identity_available_at")
                if row_cutoff != cutoff or (
                    row_source is not None
                    and row_identity is not None
                    and max(
                        _utc(row_source, label="row source authority"),
                        _utc(row_identity, label="row identity authority"),
                    )
                    >= cutoff
                ):
                    raise HistoricalFeatureBuildError("canonical row temporal authority drifted")
            loaded[role].extend(rows)
            loaded_counts[role] += len(rows)
    canonical_counts = _required_mapping(manifest.get("canonical_counts"), label="canonical counts")
    expected_counts = {
        "canonical_competitions": "competitions",
        "canonical_teams": "teams",
        "canonical_players": "players",
        "canonical_matches": "matches",
        "canonical_actions": "actions",
        "canonical_appearances": "appearances",
        "identity_exclusions": "identity_exclusions",
    }
    for role, count_name in expected_counts.items():
        if loaded_counts[role] != _required_int(
            canonical_counts.get(count_name), label=f"canonical count {count_name}"
        ):
            raise HistoricalFeatureBuildError("canonical counts do not reconcile")
    return _CanonicalDataset(
        manifest=manifest,
        manifest_payload=manifest_payload,
        competitions=tuple(loaded["canonical_competitions"]),
        teams=tuple(loaded["canonical_teams"]),
        players=tuple(loaded["canonical_players"]),
        matches=tuple(loaded["canonical_matches"]),
        action_paths=tuple(sorted(action_paths, key=lambda path: path.as_posix())),
        action_count=loaded_counts["canonical_actions"],
        appearances=tuple(loaded["canonical_appearances"]),
        exclusions=tuple(loaded["identity_exclusions"]),
    )


def _grain_id(player_id: UUID, competition_id: UUID, season_id: str) -> str:
    return f"player={player_id}|competition={competition_id}|season={season_id}"


def _source_lineage_digest(
    canonical_build_digest: str,
    appearances: Sequence[Mapping[str, object]],
    *,
    action_lineage_digest: str,
    source_action_count: int,
) -> str:
    projection = {
        "canonical_build_digest": canonical_build_digest,
        "appearances": [
            {
                "match_id": row["match_id"],
                "team_id": row["team_id"],
                "minute_state": row["minute_state"],
                "minutes": row["minutes"],
                "source_member_path": row["source_member_path"],
                "source_record_ordinal": row["source_record_ordinal"],
            }
            for row in appearances
        ],
        "ordered_action_key_digest": action_lineage_digest,
        "source_action_count": source_action_count,
    }
    return canonical_research_digest(projection)


def _new_action_aggregate(feature_count: int) -> _ActionAggregate:
    hasher = hashlib.sha256()
    hasher.update(b"w09-historical-action-lineage-v1\x00")
    return _ActionAggregate(
        numerators=[0] * feature_count,
        source_action_count=0,
        coordinate_actions_observed=0,
        match_ids=set(),
        lineage_hasher=hasher,
    )


def _cached_uuid(value: object, *, label: str, cache: dict[str, UUID]) -> UUID:
    encoded = _required_text(value, label=label)
    cached = cache.get(encoded)
    if cached is None:
        cached = UUID(encoded)
        cache[encoded] = cached
    return cached


def _action_lineage_key(row: Mapping[str, object]) -> bytes:
    action_id = UUID(_required_text(row.get("action_id"), label="action id"))
    source_action_id = _required_int(row.get("source_action_id"), label="source action id")
    source_record_ordinal = _required_int(row.get("source_record_ordinal"), label="action ordinal")
    source_member = _required_text(
        row.get("source_member_path"), label="action source member"
    ).encode("utf-8")
    source_partition = _required_text(row.get("source_partition"), label="action partition").encode(
        "utf-8"
    )
    if (
        source_action_id >= 2**64
        or source_record_ordinal >= 2**64
        or len(source_member) >= 2**32
        or len(source_partition) >= 2**32
    ):
        raise HistoricalFeatureBuildError("action lineage key exceeds its fixed framing")
    header = struct.pack(
        ">16sQQII",
        action_id.bytes,
        source_action_id,
        source_record_ordinal,
        len(source_member),
        len(source_partition),
    )
    return header + source_member + source_partition


def _stream_action_aggregates(
    dataset: _CanonicalDataset,
    *,
    registry: HistoricalFeatureRegistry,
    players: Mapping[UUID, Mapping[str, object]],
    teams: Mapping[UUID, Mapping[str, object]],
    matches: Mapping[UUID, Mapping[str, object]],
    appearance_index: _AppearanceIndex,
    batch_size: int,
) -> _ActionScan:
    if type(batch_size) is not int or batch_size <= 0:
        raise HistoricalFeatureBuildError("action batch size must be a positive strict integer")
    columns = (
        "source_partition",
        "source_member_path",
        "source_record_ordinal",
        "source_action_id",
        "action_id",
        "match_id",
        "competition_id",
        "season_id",
        "player_id",
        "team_id",
        "event_id",
        "sub_event_id",
        "tag_ids",
        "coordinate_evidence_state",
    )
    expected_paths = tuple(sorted(dataset.action_paths, key=lambda path: path.as_posix()))
    if dataset.action_paths != expected_paths:
        raise HistoricalFeatureBuildError("canonical action paths are not explicitly ordered")
    aggregates: dict[_Grain, _ActionAggregate] = {}
    invalid_grains: set[_Grain] = set()
    scanned_count = 0
    unmatched_action_count = 0
    unmatched_grains: set[_Grain] = set()
    unmatched_players: set[UUID] = set()
    unmatched_matches: set[UUID] = set()
    uuid_cache: dict[str, UUID] = {}
    for path in dataset.action_paths:
        parquet_file = pq.ParquetFile(path)
        for batch in parquet_file.iter_batches(batch_size=batch_size, columns=columns):
            rows = cast(list[dict[str, object]], batch.to_pylist())
            scanned_count += len(rows)
            for row in rows:
                raw_player_id = row.get("player_id")
                if raw_player_id is None:
                    continue
                player_id = _cached_uuid(
                    raw_player_id,
                    label="action player",
                    cache=uuid_cache,
                )
                competition_id = _cached_uuid(
                    row.get("competition_id"),
                    label="action competition",
                    cache=uuid_cache,
                )
                season_id = _required_text(row.get("season_id"), label="action season")
                grain = (player_id, competition_id, season_id)
                match_id = _cached_uuid(row.get("match_id"), label="action match", cache=uuid_cache)
                team_id = _cached_uuid(row.get("team_id"), label="action team", cache=uuid_cache)
                match = matches.get(match_id)
                if player_id not in players or match is None or team_id not in teams:
                    raise HistoricalFeatureBuildError(
                        "resolved canonical action identity is absent"
                    )
                if grain not in appearance_index.by_grain:
                    unmatched_action_count += 1
                    unmatched_grains.add(grain)
                    unmatched_players.add(player_id)
                    unmatched_matches.add(match_id)
                    continue
                appearances_in_match = appearance_index.teams_by_grain_match.get(
                    (grain, match_id), frozenset()
                )
                if (
                    str(competition_id) != match.get("competition_id")
                    or season_id != match.get("season_id")
                    or team_id not in appearances_in_match
                ):
                    invalid_grains.add(grain)
                aggregate = aggregates.get(grain)
                if aggregate is None:
                    aggregate = _new_action_aggregate(len(registry.features))
                    aggregates[grain] = aggregate
                aggregate.source_action_count += 1
                aggregate.match_ids.add(str(match_id))
                if row.get("coordinate_evidence_state") == "valid":
                    aggregate.coordinate_actions_observed += 1
                for index, definition in enumerate(registry.features):
                    if definition.matches(row):
                        aggregate.numerators[index] += 1
                action_key = _action_lineage_key(row)
                aggregate.lineage_hasher.update(len(action_key).to_bytes(8, "big"))
                aggregate.lineage_hasher.update(action_key)
    if scanned_count != dataset.action_count:
        raise HistoricalFeatureBuildError("streamed canonical action count drifted")
    if unmatched_action_count:
        raise HistoricalFeatureBuildError(
            "resolved canonical actions lack appearance-established membership: "
            f"actions={unmatched_action_count}, grains={len(unmatched_grains)}, "
            f"players={len(unmatched_players)}, matches={len(unmatched_matches)}"
        )
    return _ActionScan(
        aggregates=aggregates,
        invalid_grains=frozenset(invalid_grains),
    )


def _dataset_manifest_digest(dataset: _CanonicalDataset) -> str:
    manifest = dataset.manifest
    return canonical_research_digest(
        {
            "canonical_build_id": manifest["canonical_build_id"],
            "canonical_schema_version": manifest["canonical_schema_version"],
            "provider_adapter": manifest["provider_adapter"],
            "provider_neutral_boundary": manifest["provider_neutral_boundary"],
            "rights": manifest["rights"],
            "authorities": manifest["authorities"],
            "source_counts": manifest["source_counts"],
            "canonical_counts": manifest["canonical_counts"],
        }
    )


def _build_canonical_lookups(
    dataset: _CanonicalDataset,
    registry: HistoricalFeatureRegistry,
) -> _CanonicalLookups:
    competitions: dict[UUID, Mapping[str, object]] = {}
    for row in dataset.competitions:
        competition_id = UUID(_required_text(row.get("competition_id"), label="competition id"))
        if competition_id in competitions:
            raise HistoricalFeatureBuildError("canonical competition identity is duplicated")
        competitions[competition_id] = row

    teams: dict[UUID, Mapping[str, object]] = {}
    for row in dataset.teams:
        team_id = UUID(_required_text(row.get("team_id"), label="team id"))
        if team_id in teams:
            raise HistoricalFeatureBuildError("canonical team identity is duplicated")
        teams[team_id] = row

    players: dict[UUID, Mapping[str, object]] = {}
    source_players: set[str] = set()
    catalogue_rows: list[MatrixCatalogueEntry] = []
    for row in dataset.players:
        player_id = UUID(_required_text(row.get("player_id"), label="player id"))
        source_player_id = str(_required_int(row.get("source_player_id"), label="source player id"))
        position = row.get("position_code")
        if position not in POSITION_CODES:
            raise HistoricalFeatureBuildError("canonical player position is unsupported")
        if player_id in players or source_player_id in source_players:
            raise HistoricalFeatureBuildError("canonical player identity is duplicated")
        players[player_id] = row
        source_players.add(source_player_id)
        catalogue_rows.append(
            MatrixCatalogueEntry(
                source_player_id=source_player_id,
                player_id=player_id,
                display_name=_required_text(row.get("display_name"), label="display name"),
                position_code=cast(Literal["GK", "DF", "MD", "FW"], position),
                contains_synthetic_data=False,
            )
        )

    matches: dict[UUID, Mapping[str, object]] = {}
    for row in dataset.matches:
        match_id = UUID(_required_text(row.get("match_id"), label="match id"))
        competition_id = UUID(_required_text(row.get("competition_id"), label="match competition"))
        raw_team_ids = row.get("team_ids")
        if (
            match_id in matches
            or competition_id not in competitions
            or not isinstance(raw_team_ids, list)
            or not raw_team_ids
            or any(UUID(cast(str, value)) not in teams for value in raw_team_ids)
        ):
            raise HistoricalFeatureBuildError("canonical match membership is incompatible")
        if not (
            registry.window_start_utc
            <= _utc(row.get("match_start_utc"), label="match start")
            < registry.window_end_utc
        ):
            raise HistoricalFeatureBuildError("canonical match falls outside the fixed window")
        matches[match_id] = row

    return _CanonicalLookups(
        competitions=competitions,
        teams=teams,
        players=players,
        matches=matches,
        catalogue=tuple(sorted(catalogue_rows, key=lambda row: row.player_id.bytes)),
    )


def _build_appearance_index(
    dataset: _CanonicalDataset,
    lookups: _CanonicalLookups,
) -> _AppearanceIndex:
    by_grain: dict[_Grain, list[dict[str, object]]] = defaultdict(list)
    teams_by_grain_match: dict[tuple[_Grain, UUID], set[UUID]] = defaultdict(set)
    seen_appearance_keys: set[tuple[UUID, UUID]] = set()
    invalid_grains: set[_Grain] = set()
    for row in dataset.appearances:
        player_id = UUID(_required_text(row.get("player_id"), label="appearance player"))
        competition_id = UUID(
            _required_text(row.get("competition_id"), label="appearance competition")
        )
        match_id = UUID(_required_text(row.get("match_id"), label="appearance match"))
        team_id = UUID(_required_text(row.get("team_id"), label="appearance team"))
        season_id = _required_text(row.get("season_id"), label="appearance season")
        key = (player_id, match_id)
        if key in seen_appearance_keys:
            raise HistoricalFeatureBuildError("canonical appearance grain is duplicated")
        seen_appearance_keys.add(key)
        grain = (player_id, competition_id, season_id)
        match = lookups.matches.get(match_id)
        if player_id not in lookups.players or match is None:
            raise HistoricalFeatureBuildError("canonical appearance identity is absent")
        match_teams = cast(list[str], match.get("team_ids"))
        if (
            str(competition_id) != match.get("competition_id")
            or season_id != match.get("season_id")
            or str(team_id) not in match_teams
            or team_id not in lookups.teams
            or row.get("source_player_id") != lookups.players[player_id].get("source_player_id")
        ):
            invalid_grains.add(grain)
        by_grain[grain].append(row)
        teams_by_grain_match[(grain, match_id)].add(team_id)
    return _AppearanceIndex(
        by_grain={grain: tuple(rows) for grain, rows in by_grain.items()},
        teams_by_grain_match={
            key: frozenset(team_ids) for key, team_ids in teams_by_grain_match.items()
        },
        invalid_grains=frozenset(invalid_grains),
    )


def _eligibility_reason(
    *,
    grain: _Grain,
    minute_state: MinuteEvidenceState,
    minutes: float | None,
    invalid_grains: frozenset[_Grain],
) -> EligibilityReason:
    if minute_state is MinuteEvidenceState.UNUSABLE:
        return EligibilityReason.UNUSABLE_MINUTES
    if grain in invalid_grains:
        return EligibilityReason.INVALID_HISTORICAL_MEMBERSHIP
    if minutes is not None and minutes < MINIMUM_MINUTES:
        return EligibilityReason.BELOW_MINIMUM_MINUTES
    return EligibilityReason.ELIGIBLE


def _build_grain_ledgers(
    *,
    dataset: _CanonicalDataset,
    registry: HistoricalFeatureRegistry,
    lookups: _CanonicalLookups,
    appearance_index: _AppearanceIndex,
    action_scan: _ActionScan,
) -> _GrainLedgers:
    invalid_grains = appearance_index.invalid_grains | action_scan.invalid_grains
    canonical_build_digest = _sha256(dataset.manifest_payload)
    dataset_digest = _dataset_manifest_digest(dataset)
    authorities = _required_mapping(dataset.manifest.get("authorities"), label="authorities")
    identity_digest = _required_text(
        authorities.get("identity_bundle_sha256"), label="identity bundle digest"
    )
    eligibility: list[EligibilityDecision] = []
    matrix: list[FeatureMatrixRow] = []
    player_grains: dict[UUID, list[str]] = defaultdict(list)

    for grain in sorted(
        appearance_index.by_grain,
        key=lambda item: (item[0].bytes, item[1].bytes, item[2]),
    ):
        player_id, competition_id, season_id = grain
        appearance_rows = sorted(
            appearance_index.by_grain[grain],
            key=lambda row: (
                UUID(cast(str, row["match_id"])).bytes,
                UUID(cast(str, row["team_id"])).bytes,
            ),
        )
        action_aggregate = action_scan.aggregates.get(grain)
        if action_aggregate is None:
            action_aggregate = _new_action_aggregate(len(registry.features))
        grain_id = _grain_id(player_id, competition_id, season_id)
        player_grains[player_id].append(grain_id)
        minute_state, minutes, played_match_count = aggregate_governed_minutes(appearance_rows)
        reason = _eligibility_reason(
            grain=grain,
            minute_state=minute_state,
            minutes=minutes,
            invalid_grains=invalid_grains,
        )
        appearance_match_ids = {row["match_id"] for row in appearance_rows}
        decision = EligibilityDecision(
            source_player_id=str(lookups.players[player_id]["source_player_id"]),
            grain_id=grain_id,
            player_id=player_id,
            competition_id=competition_id,
            season_id=season_id,
            eligibility_policy_version=ELIGIBILITY_POLICY_VERSION,
            eligibility_policy_digest=registry.eligibility_policy_digest,
            minute_state=minute_state,
            minutes=minutes,
            minimum_minutes=MINIMUM_MINUTES,
            eligible=reason is EligibilityReason.ELIGIBLE,
            reason=reason,
            feature_cutoff_ts=registry.feature_cutoff_ts,
            temporal_authorities_strictly_before_cutoff=True,
            source_match_count=len(appearance_match_ids),
            source_action_count=action_aggregate.source_action_count,
            required_missing_features=(),
        )
        eligibility.append(decision)
        if not decision.eligible:
            continue
        if minutes is None or minutes <= 0 or played_match_count <= 0:
            raise HistoricalFeatureBuildError("eligible grain lacks governed positive exposure")
        feature_values = tuple(
            ResearchFeatureValue(
                feature_name=definition.name,
                state=FeatureValueState.ZERO if numerator == 0 else FeatureValueState.VALUE,
                value=0.0 if numerator == 0 else float(numerator * 90.0 / minutes),
                numerator=float(numerator),
                denominator=minutes,
            )
            for definition, numerator in zip(
                registry.features,
                action_aggregate.numerators,
                strict=True,
            )
        )
        played_appearances = [
            row for row in appearance_rows if row["minute_state"] in PLAYED_MINUTE_STATES
        ]
        team_ids = tuple(
            sorted(
                {UUID(cast(str, row["team_id"])) for row in played_appearances},
                key=lambda value: value.bytes,
            )
        )
        team_names = tuple(
            _required_text(lookups.teams[team_id].get("name"), label="team name")
            for team_id in team_ids
        )
        played_match_ids = {row["match_id"] for row in played_appearances}
        matrix.append(
            FeatureMatrixRow(
                grain_id=grain_id,
                player_id=player_id,
                display_name=_required_text(
                    lookups.players[player_id].get("display_name"), label="display name"
                ),
                competition_id=competition_id,
                competition_name=_required_text(
                    lookups.competitions[competition_id].get("name"), label="competition name"
                ),
                season_id=season_id,
                position_code=cast(
                    Literal["GK", "DF", "MD", "FW"],
                    lookups.players[player_id]["position_code"],
                ),
                team_ids=team_ids,
                team_names=team_names,
                minute_state=cast(
                    Literal[
                        MinuteEvidenceState.EXACT,
                        MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND,
                    ],
                    minute_state,
                ),
                minutes=minutes,
                match_count=played_match_count,
                features=feature_values,
                missing_feature_names=(),
                coverage=ResearchCoverage(
                    lineup_matches_observed=len(played_match_ids),
                    lineup_matches_expected=len(appearance_match_ids),
                    action_matches_observed=len(action_aggregate.match_ids & played_match_ids),
                    action_matches_expected=len(played_match_ids),
                    coordinate_actions_observed=action_aggregate.coordinate_actions_observed,
                    coordinate_actions_expected=action_aggregate.source_action_count,
                ),
                window_start_utc=registry.window_start_utc,
                window_end_utc=registry.window_end_utc,
                feature_cutoff_ts=registry.feature_cutoff_ts,
                dataset_manifest_digest=dataset_digest,
                identity_bundle_digest=identity_digest,
                canonical_build_digest=canonical_build_digest,
                feature_registry_digest=registry.registry_digest,
                eligibility_policy_digest=registry.eligibility_policy_digest,
                eligibility_decision_digest=canonical_research_digest(decision),
                source_lineage_digest=_source_lineage_digest(
                    canonical_build_digest,
                    appearance_rows,
                    action_lineage_digest=action_aggregate.lineage_hasher.hexdigest(),
                    source_action_count=action_aggregate.source_action_count,
                ),
                source_action_count=action_aggregate.source_action_count,
                contains_synthetic_data=False,
            )
        )
    matrix_rows = tuple(sorted(matrix, key=lambda row: (row.player_id.bytes, row.grain_id)))
    if not matrix_rows:
        raise HistoricalFeatureBuildError("canonical fixture has no eligible matrix rows")
    return _GrainLedgers(
        eligibility=tuple(sorted(eligibility, key=lambda row: (row.player_id.bytes, row.grain_id))),
        matrix=matrix_rows,
        player_grains={
            player_id: tuple(grain_ids) for player_id, grain_ids in player_grains.items()
        },
    )


def _population_ledger(
    catalogue: Sequence[MatrixCatalogueEntry],
    player_grains: Mapping[UUID, tuple[str, ...]],
) -> tuple[SourcePopulationDecision, ...]:
    return tuple(
        SourcePopulationDecision(
            source_player_id=row.source_player_id,
            player_id=row.player_id,
            lineup_evidence_present=bool(player_grains.get(row.player_id)),
            grain_ids=player_grains.get(row.player_id, ()),
            reason=(
                PopulationDecisionReason.REFERRED_TO_WINDOW_ELIGIBILITY
                if player_grains.get(row.player_id)
                else PopulationDecisionReason.NO_LINEUP_EVIDENCE
            ),
        )
        for row in catalogue
    )


def _construct_ledgers(
    dataset: _CanonicalDataset,
    registry: HistoricalFeatureRegistry,
    *,
    action_batch_size: int,
) -> tuple[
    tuple[MatrixCatalogueEntry, ...],
    tuple[SourcePopulationDecision, ...],
    tuple[EligibilityDecision, ...],
    tuple[FeatureMatrixRow, ...],
]:
    lookups = _build_canonical_lookups(dataset, registry)
    appearance_index = _build_appearance_index(dataset, lookups)
    action_scan = _stream_action_aggregates(
        dataset,
        registry=registry,
        players=lookups.players,
        teams=lookups.teams,
        matches=lookups.matches,
        appearance_index=appearance_index,
        batch_size=action_batch_size,
    )
    grain_ledgers = _build_grain_ledgers(
        dataset=dataset,
        registry=registry,
        lookups=lookups,
        appearance_index=appearance_index,
        action_scan=action_scan,
    )
    population = _population_ledger(lookups.catalogue, grain_ledgers.player_grains)
    return (
        lookups.catalogue,
        population,
        grain_ledgers.eligibility,
        grain_ledgers.matrix,
    )


def _artifact_descriptor(
    *, role: str, relative_path: str, payload: bytes, row_count: int, semantic_digest: str
) -> ResearchArtifactFile:
    return ResearchArtifactFile(
        role=role,
        relative_path=relative_path,
        row_count=row_count,
        size_bytes=len(payload),
        sha256=_sha256(payload),
        semantic_digest=semantic_digest,
    )


def _feature_matrix_parquet_bytes(rows: Sequence[FeatureMatrixRow]) -> bytes:
    projections = [row.model_dump(mode="json") for row in rows]
    table = pa.Table.from_pylist(projections, schema=_FEATURE_MATRIX_SCHEMA).combine_chunks()
    if table.num_rows != len(rows) or not table.schema.equals(_FEATURE_MATRIX_SCHEMA):
        raise HistoricalFeatureBuildError("feature matrix Arrow projection drifted")
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
        store_schema=True,
    )
    return cast(bytes, sink.getvalue().to_pybytes())


def discover_canonical_manifest(
    root: Path = DEFAULT_CANONICAL_MANIFEST_ROOT,
) -> Path:
    """Require exactly one accepted canonical manifest for a production build."""

    candidates = tuple(sorted(root.glob("*.canonical-manifest.json"))) if root.is_dir() else ()
    if len(candidates) != 1:
        raise HistoricalFeatureBuildError("exactly one accepted canonical manifest is required")
    return candidates[0]


def build_historical_feature_matrix(
    *,
    canonical_manifest_path: Path,
    canonical_artifact_root: Path,
    feature_root: Path,
    feature_manifest_root: Path,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    mode: HistoricalFeatureBuildMode = HistoricalFeatureBuildMode.PRODUCTION,
    action_batch_size: int = 65_536,
) -> HistoricalFeatureBuildResult:
    """Materialise complete governed ledgers and eligible historical feature rows."""

    if mode is HistoricalFeatureBuildMode.PRODUCTION and (
        feature_root != DEFAULT_FEATURE_ROOT
        or feature_manifest_root != DEFAULT_FEATURE_MANIFEST_ROOT
        or registry_path != DEFAULT_REGISTRY_PATH
    ):
        raise HistoricalFeatureBuildError("production feature roots and registry must be exact")
    if mode is HistoricalFeatureBuildMode.VERIFICATION and (
        feature_root.absolute() == DEFAULT_FEATURE_ROOT.absolute()
        or feature_manifest_root.absolute() == DEFAULT_FEATURE_MANIFEST_ROOT.absolute()
        or registry_path != DEFAULT_REGISTRY_PATH
    ):
        raise HistoricalFeatureBuildError(
            "verification builds require temporary feature roots and the exact registry"
        )
    if mode is HistoricalFeatureBuildMode.TEST_FIXTURE and (
        feature_root.absolute() == DEFAULT_FEATURE_ROOT.absolute()
        or feature_manifest_root.absolute() == DEFAULT_FEATURE_MANIFEST_ROOT.absolute()
    ):
        raise HistoricalFeatureBuildError("test fixtures cannot write to production feature roots")
    registry = load_historical_feature_registry(registry_path)
    dataset = _load_canonical_dataset(
        canonical_manifest_path,
        artifact_root=canonical_artifact_root,
        mode=mode,
        registry=registry,
    )
    catalogue, population, eligibility, matrix = _construct_ledgers(
        dataset,
        registry,
        action_batch_size=action_batch_size,
    )
    typed_rows: Mapping[str, Sequence[Any]] = {
        "player_catalogue": catalogue,
        "population_decisions": population,
        "eligibility_decisions": eligibility,
        "feature_matrix_rows": matrix,
    }
    canonical_build_digest = _sha256(dataset.manifest_payload)
    code_digest = governed_code_digest((Path(__file__), registry_path))
    version_suffix = canonical_research_digest(
        {
            "canonical_build_digest": canonical_build_digest,
            "code_digest": code_digest,
            "code_version": FEATURE_CODE_VERSION,
            "feature_registry_digest": registry.registry_digest,
            "eligibility_policy_digest": registry.eligibility_policy_digest,
        }
    )[:16]
    matrix_version = f"{FEATURE_MATRIX_VERSION}-{version_suffix}"
    version_root = f"matrix_version={matrix_version}"
    storage = GuardedStorage({"features": feature_root.resolve()})
    descriptors: list[ResearchArtifactFile] = []
    lineage = {
        "canonical_build_digest": canonical_build_digest,
        "feature_registry_digest": registry.registry_digest,
        "eligibility_policy_digest": registry.eligibility_policy_digest,
    }
    retention = {
        "classification": "wyscout_figshare_v5_cc_by_4",
        "local_only": True,
        "raw_export_allowed": False,
    }
    for role in FEATURE_ARTIFACT_PATHS:
        rows = typed_rows[role]
        is_matrix = role == "feature_matrix_rows"
        payload = (
            _feature_matrix_parquet_bytes(cast(Sequence[FeatureMatrixRow], rows))
            if is_matrix
            else canonical_jsonl_bytes([row.model_dump(mode="json") for row in rows])
        )
        tail = f"{version_root}/{FEATURE_ARTIFACT_PATHS[role]}"
        storage.write_bytes(
            "features",
            tail,
            payload,
            media_type=("application/vnd.apache.parquet" if is_matrix else "application/x-ndjson"),
            lineage=lineage,
            retention=retention,
        )
        logical_path = (
            FEATURE_LOGICAL_PREFIX + tail if mode is HistoricalFeatureBuildMode.PRODUCTION else tail
        )
        descriptors.append(
            _artifact_descriptor(
                role=role,
                relative_path=logical_path,
                payload=payload,
                row_count=len(rows),
                semantic_digest=rows_semantic_digest(rows),
            )
        )
    source_manifest_id = UUID(
        _required_text(
            _required_mapping(dataset.manifest["authorities"], label="authorities").get(
                "source_manifest_id"
            ),
            label="source manifest id",
        )
    )
    authorities = _required_mapping(dataset.manifest["authorities"], label="authorities")
    identity_audit = _required_mapping(dataset.manifest["identity_audit"], label="identity audit")
    reason_counts = Counter(row.reason for row in eligibility)
    manifest_values: dict[str, object] = {
        "schema_version": 1,
        "manifest_id": uuid5(NAMESPACE_URL, f"scouting:w09:feature-matrix:{matrix_version}"),
        "matrix_version": matrix_version,
        "matrix_digest": rows_semantic_digest(matrix),
        "generated_at": registry.feature_cutoff_ts,
        "feature_cutoff_ts": registry.feature_cutoff_ts,
        "window_start_utc": registry.window_start_utc,
        "window_end_utc": registry.window_end_utc,
        "dataset_version": _required_text(
            dataset.manifest.get("canonical_build_id"), label="canonical build id"
        ),
        "dataset_manifest_digest": _dataset_manifest_digest(dataset),
        "source_manifest_id": source_manifest_id,
        "source_manifest_digest": _required_text(
            authorities.get("source_manifest_sha256"), label="source manifest digest"
        ),
        "source_completion_digest": _required_text(
            authorities.get("source_completion_index_sha256"),
            label="source completion digest",
        ),
        "identity_bundle_digest": _required_text(
            authorities.get("identity_bundle_sha256"), label="identity digest"
        ),
        "canonical_build_version": _required_text(
            dataset.manifest.get("builder_version"), label="canonical builder"
        ),
        "canonical_build_digest": canonical_build_digest,
        "feature_registry_version": registry.registry_version,
        "feature_registry_digest": registry.registry_digest,
        "eligibility_policy_version": ELIGIBILITY_POLICY_VERSION,
        "eligibility_policy_digest": registry.eligibility_policy_digest,
        "code_version": FEATURE_CODE_VERSION,
        "code_digest": code_digest,
        "feature_names": tuple(item.name for item in registry.features),
        "catalogue_player_count": len(catalogue),
        "population_decision_count": len(population),
        "population_referred_count": sum(row.lineup_evidence_present for row in population),
        "population_referred_grain_count": sum(len(row.grain_ids) for row in population),
        "population_referred_grain_ledger_digest": population_referred_grain_digest(population),
        "population_no_lineup_count": sum(not row.lineup_evidence_present for row in population),
        "unresolved_identity_count": _required_int(
            identity_audit.get("review_required_players_excluded"),
            label="unresolved identity count",
        ),
        "rejected_identity_count": _required_int(
            identity_audit.get("rejected_players_excluded"), label="rejected identity count"
        ),
        "rejected_actor_action_count": _required_int(
            identity_audit.get("rejected_action_rows"), label="rejected action count"
        ),
        "eligibility_decision_count": len(eligibility),
        "unique_eligibility_grain_count": len({row.grain_id for row in eligibility}),
        "eligibility_ledger_digest": rows_semantic_digest(eligibility),
        "eligibility_reason_counts": tuple(
            EligibilityReasonCount(reason=reason, count=reason_counts[reason])
            for reason in EligibilityReason
        ),
        "matrix_row_count": len(matrix),
        "unique_matrix_grain_count": len({row.grain_id for row in matrix}),
        "unique_matrix_player_count": len({row.player_id for row in matrix}),
        "files": tuple(descriptors),
        "contains_synthetic_rows": False,
        "limitations": registry.limitations,
        "manifest_digest": "0" * 64,
        "claim_boundary": "historical_resemblance_research_only",
    }
    draft = cast(Any, FeatureMatrixManifest).model_construct(**manifest_values)
    manifest_values["manifest_digest"] = canonical_research_digest(draft.digest_projection())
    try:
        manifest = FeatureMatrixManifest.model_validate(manifest_values)
    except ValidationError as exc:
        raise HistoricalFeatureBuildError("constructed feature manifest is incompatible") from exc
    manifest_payload = canonical_json_bytes(manifest.model_dump(mode="json"))
    manifest_storage = GuardedStorage({"manifests": feature_manifest_root.resolve()})
    manifest_tail = f"{matrix_version}.feature-matrix.manifest.json"
    manifest_storage.write_bytes(
        "manifests",
        manifest_tail,
        manifest_payload,
        media_type="application/json",
        lineage=lineage,
        retention=retention,
    )
    return HistoricalFeatureBuildResult(
        matrix_version=matrix_version,
        matrix_manifest_path=feature_manifest_root / manifest_tail,
        matrix_manifest_sha256=_sha256(manifest_payload),
        manifest=manifest,
    )


__all__ = [
    "DEFAULT_CANONICAL_ARTIFACT_ROOT",
    "DEFAULT_CANONICAL_MANIFEST_ROOT",
    "DEFAULT_FEATURE_MANIFEST_ROOT",
    "DEFAULT_FEATURE_ROOT",
    "DEFAULT_REGISTRY_PATH",
    "ELIGIBILITY_POLICY_VERSION",
    "FEATURE_MATRIX_VERSION",
    "HistoricalFeatureBuildError",
    "HistoricalFeatureBuildMode",
    "HistoricalFeatureBuildResult",
    "HistoricalFeatureDefinition",
    "HistoricalFeatureRegistry",
    "aggregate_governed_minutes",
    "build_historical_feature_matrix",
    "discover_canonical_manifest",
    "feature_numerators",
    "load_historical_feature_registry",
]

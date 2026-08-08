"""Deterministic robust-scaling artifacts for governed W09 research retrieval."""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import stat
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, cast
from uuid import NAMESPACE_URL, UUID, uuid5

import numpy as np
import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
from pydantic import AfterValidator, Field, ValidationError, model_validator

from scouting.contracts.evidence import Sha256Digest
from scouting.contracts.primitives import (
    CanonicalPlayerId,
    ContractModel,
    NonEmptyString,
    NonNegativeInt,
    PositiveInt,
    SchemaVersion,
    StrictUuid,
    UtcInstant,
)
from scouting.contracts.research import (
    EligibilityDecision,
    EligibilityReason,
    FeatureMatrixManifest,
    FeatureMatrixRow,
    FeatureValueState,
    MatrixCatalogueEntry,
    MinuteEvidenceState,
    ResearchArtifactFile,
    ResearchCoverage,
    ResearchFeatureValue,
    ResearchIndexManifest,
    ResearchMethod,
    SourcePopulationDecision,
    canonical_research_digest,
    population_referred_grain_digest,
    rows_semantic_digest,
)
from scouting.contracts.validation import revalidate_exact_contract
from scouting.storage.formats import canonical_json_bytes, canonical_jsonl_bytes

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FEATURE_MANIFEST_ROOT = PROJECT_ROOT / "data/manifests/wyscout/v5/research_features"
DEFAULT_MATRIX_ARTIFACT_ROOT = PROJECT_ROOT
DEFAULT_INDEX_ROOT = PROJECT_ROOT / "runs/w09/historical-player-workbench-v1"
DEFAULT_MODEL_CONFIG_PATH = PROJECT_ROOT / "configs/models/w09-historical-retrieval-v1.json"
SHARED_SCORER_SOURCE_PATH = Path(__file__).resolve().parents[1] / "m0/scoring.py"

PLAYER_CATALOGUE_ROLE = "player_catalogue"
POPULATION_DECISIONS_ROLE = "population_decisions"
ELIGIBILITY_DECISIONS_ROLE = "eligibility_decisions"
FEATURE_MATRIX_ROWS_ROLE = "feature_matrix_rows"
MATRIX_ARTIFACT_ROLES = frozenset(
    {
        PLAYER_CATALOGUE_ROLE,
        POPULATION_DECISIONS_ROLE,
        ELIGIBILITY_DECISIONS_ROLE,
        FEATURE_MATRIX_ROWS_ROLE,
    }
)

SCALER_CENTER_ROLE = "scaler_center"
SCALER_SCALE_ROLE = "scaler_scale"
INDEX_VECTORS_ROLE = "index_vectors"
INDEX_CATALOGUE_ROLE = "candidate_catalogue"
MODEL_CONFIGURATION_ROLE = "model_configuration"
INDEX_ARTIFACT_PATHS: Mapping[str, str] = {
    SCALER_CENTER_ROLE: "scaler-center.npy",
    SCALER_SCALE_ROLE: "scaler-scale.npy",
    INDEX_VECTORS_ROLE: "index-vectors.npy",
    INDEX_CATALOGUE_ROLE: "candidate-catalogue.jsonl",
    MODEL_CONFIGURATION_ROLE: "model-configuration.json",
}


class ResearchIndexBuildError(ValueError):
    """Raised when governed index construction or verification fails closed."""


class ResearchIndexBuildMode(StrEnum):
    """The explicit boundary separating product construction from test fixtures."""

    PRODUCTION = "production"
    VERIFICATION = "verification"
    TEST_FIXTURE = "test_fixture"


def _reject_negative_zero(value: float) -> float:
    if value == 0.0 and math.copysign(1.0, value) < 0.0:
        raise ValueError("negative zero is not canonical")
    return value


type FiniteValue = Annotated[
    float,
    Field(strict=True, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]
type PositiveFiniteValue = Annotated[
    float,
    Field(strict=True, gt=0.0, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]


class ResearchModelConfiguration(ContractModel):
    """Provider-neutral, self-digested index construction policy."""

    schema_version: SchemaVersion = 1
    configuration_id: Literal["w09-historical-retrieval-v1"]
    configuration_version: Literal["v1"]
    model_version: Literal["w09-robust-scaled-transparent-baselines-v1"]
    index_version: Literal["w09-historical-player-index-v1"]
    scorer_version: Literal["w09-shared-vector-scorer-v1"]
    center_statistic: Literal["median"]
    scale_statistic: Literal["interquartile_range"]
    quantile_method: Literal["linear"]
    constant_feature_policy: Literal["retain_with_unit_scale"]
    row_order: Literal["canonical_player_uuid_bytes_then_grain_id"]
    dtype: Literal["little_endian_float64"]
    memory_order: Literal["C"]
    methods: tuple[ResearchMethod, ResearchMethod]
    full_population_scoring: Literal[True]
    pre_limit: Literal[False]
    approximate_nearest_neighbour: Literal[False]
    configuration_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"configuration_digest"})

    @model_validator(mode="after")
    def configuration_is_exact(self) -> ResearchModelConfiguration:
        expected_methods = (
            ResearchMethod.WEIGHTED_EUCLIDEAN,
            ResearchMethod.WEIGHTED_COSINE,
        )
        if self.methods != expected_methods:
            raise ValueError("configuration must declare both transparent methods in order")
        if self.configuration_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("model configuration digest does not match its projection")
        return self


class IndexCatalogueEntry(ContractModel):
    """One immutable index ordinal with the raw values needed for explanation."""

    schema_version: SchemaVersion = 1
    ordinal: NonNegativeInt
    grain_id: NonEmptyString
    player_id: CanonicalPlayerId
    display_name: NonEmptyString
    competition_id: StrictUuid
    competition_name: NonEmptyString
    season_id: NonEmptyString
    position_code: Literal["GK", "DF", "MD", "FW"]
    team_ids: tuple[StrictUuid, ...]
    team_names: tuple[NonEmptyString, ...]
    minutes: PositiveFiniteValue
    minute_state: Literal["exact", "conservative_lower_bound"]
    match_count: PositiveInt
    source_action_count: NonNegativeInt
    feature_values: Annotated[tuple[FiniteValue, ...], Field(min_length=1)]
    feature_cutoff_ts: UtcInstant
    source_lineage_digest: Sha256Digest
    eligibility_decision_digest: Sha256Digest
    contains_synthetic_data: Literal[False] = False

    @model_validator(mode="after")
    def row_is_supported(self) -> IndexCatalogueEntry:
        if not self.team_ids or len(self.team_ids) != len(self.team_names):
            raise ValueError("index catalogue team identities must be present and aligned")
        return self


@dataclass(frozen=True, slots=True)
class LoadedFeatureMatrix:
    """Fully verified W09 matrix authority ready for deterministic fitting."""

    manifest: FeatureMatrixManifest
    rows: tuple[FeatureMatrixRow, ...]
    catalogue: tuple[MatrixCatalogueEntry, ...]
    population_decisions: tuple[SourcePopulationDecision, ...]
    eligibility_decisions: tuple[EligibilityDecision, ...]


@dataclass(frozen=True, slots=True)
class RobustScaledMatrix:
    """Canonical robust scaler and complete scaled population."""

    center: np.ndarray
    scale: np.ndarray
    vectors: np.ndarray


@dataclass(frozen=True, slots=True)
class LoadedResearchIndex:
    """Verified, read-only in-process W09 retrieval artifact."""

    manifest: ResearchIndexManifest
    configuration: ResearchModelConfiguration
    center: np.ndarray
    scale: np.ndarray
    vectors: np.ndarray
    catalogue: tuple[IndexCatalogueEntry, ...]


def _authority_model[T: ContractModel](
    value: T,
    model: type[T],
    *,
    label: str,
    error_type: type[ValueError],
) -> T:
    return revalidate_exact_contract(value, model, label=label, error_type=error_type)


def _authority_rows[T: ContractModel](
    values: tuple[T, ...],
    model: type[T],
    *,
    label: str,
    error_type: type[ValueError],
) -> tuple[T, ...]:
    if type(values) is not tuple:
        raise TypeError(f"{label} must be an exact tuple")
    return tuple(
        _authority_model(
            value,
            model,
            label=f"{label}[{index}]",
            error_type=error_type,
        )
        for index, value in enumerate(values)
    )


def _authority_array(
    value: np.ndarray,
    *,
    label: str,
    shape: tuple[int, ...],
    error_type: type[ValueError],
    private_copy: bool,
) -> np.ndarray:
    if type(value) is not np.ndarray:
        raise TypeError(f"{label} must be an exact ndarray")
    if (
        value.dtype.str != "<f8"
        or value.shape != shape
        or not value.flags.c_contiguous
        or value.flags.writeable
        or (value.ndim > 1 and value.flags.f_contiguous and min(value.shape) > 1)
        or not np.all(np.isfinite(value))
        or np.any(np.signbit(value) & (value == 0.0))
    ):
        raise error_type(f"{label} must be a finite read-only C-order little-endian float64 array")
    if not private_copy:
        return value
    canonical = np.array(value, dtype="<f8", order="C", copy=True)
    canonical[canonical == 0.0] = 0.0
    private = np.frombuffer(canonical.tobytes(order="C"), dtype="<f8").reshape(shape)
    if private.flags.writeable or not private.flags.c_contiguous:
        raise error_type(f"{label} private immutable copy failed")
    return private


def verify_readonly_array(
    value: np.ndarray,
    *,
    label: str,
    shape: tuple[int, ...],
    error_type: type[ValueError] = ResearchIndexBuildError,
    private_copy: bool = True,
) -> np.ndarray:
    """Validate one canonical array and optionally return a private immutable copy."""

    return _authority_array(
        value,
        label=label,
        shape=shape,
        error_type=error_type,
        private_copy=private_copy,
    )


def verify_feature_matrix_authority(
    matrix: LoadedFeatureMatrix,
    *,
    error_type: type[ValueError] = ResearchIndexBuildError,
) -> LoadedFeatureMatrix:
    """Verify and privately re-materialise one complete in-memory matrix authority."""

    if type(matrix) is not LoadedFeatureMatrix:
        raise TypeError("matrix must be an exact LoadedFeatureMatrix")
    manifest = _authority_model(
        matrix.manifest,
        FeatureMatrixManifest,
        label="matrix manifest",
        error_type=error_type,
    )
    rows = _authority_rows(
        matrix.rows,
        FeatureMatrixRow,
        label="matrix rows",
        error_type=error_type,
    )
    catalogue = _authority_rows(
        matrix.catalogue,
        MatrixCatalogueEntry,
        label="matrix catalogue",
        error_type=error_type,
    )
    population = _authority_rows(
        matrix.population_decisions,
        SourcePopulationDecision,
        label="population decisions",
        error_type=error_type,
    )
    eligibility = _authority_rows(
        matrix.eligibility_decisions,
        EligibilityDecision,
        label="eligibility decisions",
        error_type=error_type,
    )
    roles = {item.role: item for item in manifest.files}
    if set(roles) != MATRIX_ARTIFACT_ROLES:
        raise error_type("matrix manifest artifact roles are incompatible")
    populations: tuple[tuple[str, Sequence[ContractModel]], ...] = (
        (PLAYER_CATALOGUE_ROLE, catalogue),
        (POPULATION_DECISIONS_ROLE, population),
        (ELIGIBILITY_DECISIONS_ROLE, eligibility),
        (FEATURE_MATRIX_ROWS_ROLE, rows),
    )
    for role, values in populations:
        descriptor = roles[role]
        if descriptor.row_count != len(values) or descriptor.semantic_digest != (
            rows_semantic_digest(values)
        ):
            raise error_type(f"matrix in-memory evidence drifts for role {role}")
    if (
        len(catalogue) != manifest.catalogue_player_count
        or len(population) != manifest.population_decision_count
        or len(eligibility) != manifest.eligibility_decision_count
        or len(rows) != manifest.matrix_row_count
        or roles[FEATURE_MATRIX_ROWS_ROLE].semantic_digest != manifest.matrix_digest
        or roles[ELIGIBILITY_DECISIONS_ROLE].semantic_digest != manifest.eligibility_ledger_digest
        or population_referred_grain_digest(population)
        != manifest.population_referred_grain_ledger_digest
    ):
        raise error_type("matrix manifest counts or ledger digests drift")

    catalogue_ids = tuple(item.player_id for item in catalogue)
    catalogue_sources = tuple(item.source_player_id for item in catalogue)
    if (
        len(catalogue_ids) != len(set(catalogue_ids))
        or len(catalogue_sources) != len(set(catalogue_sources))
        or catalogue_ids != tuple(sorted(catalogue_ids, key=lambda item: item.bytes))
    ):
        raise error_type("matrix catalogue identities are not unique and ordered")
    catalogue_by_id = {item.player_id: item for item in catalogue}
    if tuple(item.player_id for item in population) != catalogue_ids or any(
        item.source_player_id != catalogue_by_id[item.player_id].source_player_id
        for item in population
    ):
        raise error_type("population decisions drift from the matrix catalogue")

    referred: dict[str, SourcePopulationDecision] = {}
    for population_decision in population:
        for grain_id in population_decision.grain_ids:
            if grain_id in referred:
                raise error_type("population decisions contain a duplicate grain")
            referred[grain_id] = population_decision
    eligibility_by_grain: dict[str, EligibilityDecision] = {}
    for eligibility_decision in eligibility:
        if eligibility_decision.grain_id in eligibility_by_grain:
            raise error_type("eligibility decisions contain a duplicate grain")
        owner = referred.get(eligibility_decision.grain_id)
        if owner is None or (
            owner.player_id != eligibility_decision.player_id
            or owner.source_player_id != eligibility_decision.source_player_id
        ):
            raise error_type("eligibility identity does not bind its referred grain")
        if (
            eligibility_decision.eligibility_policy_version != manifest.eligibility_policy_version
            or eligibility_decision.eligibility_policy_digest != manifest.eligibility_policy_digest
            or eligibility_decision.feature_cutoff_ts != manifest.feature_cutoff_ts
        ):
            raise error_type("eligibility policy or cutoff pin drifts")
        eligibility_by_grain[eligibility_decision.grain_id] = eligibility_decision
    if set(eligibility_by_grain) != set(referred) or eligibility != tuple(
        sorted(eligibility, key=lambda item: (item.player_id.bytes, item.grain_id))
    ):
        raise error_type("eligibility decisions are incomplete or unordered")
    observed_reasons = {reason: 0 for reason in EligibilityReason}
    for eligibility_decision in eligibility:
        observed_reasons[eligibility_decision.reason] += 1
    if observed_reasons != {item.reason: item.count for item in manifest.eligibility_reason_counts}:
        raise error_type("eligibility reason counts drift from decisions")

    if rows != tuple(sorted(rows, key=lambda item: (item.player_id.bytes, item.grain_id))):
        raise error_type("matrix rows are not in canonical order")
    grain_ids = tuple(item.grain_id for item in rows)
    player_windows = tuple((item.player_id, item.competition_id, item.season_id) for item in rows)
    if len(grain_ids) != len(set(grain_ids)):
        raise error_type("matrix contains a duplicate grain")
    if len(player_windows) != len(set(player_windows)):
        raise error_type("matrix contains a duplicate player/competition/season grain")
    if len({item.player_id for item in rows}) != manifest.unique_matrix_player_count:
        raise error_type("matrix unique player count drifts")
    for row in rows:
        row_eligibility = eligibility_by_grain.get(row.grain_id)
        identity = catalogue_by_id.get(row.player_id)
        if row_eligibility is None or identity is None:
            raise error_type("matrix row is absent from its governed ledgers")
        if (
            not row_eligibility.eligible
            or row_eligibility.player_id != row.player_id
            or row_eligibility.competition_id != row.competition_id
            or row_eligibility.season_id != row.season_id
            or row.eligibility_decision_digest != canonical_research_digest(row_eligibility)
            or identity.display_name != row.display_name
            or identity.position_code != row.position_code
        ):
            raise error_type("matrix row eligibility or identity binding drifts")
        if (
            row.window_start_utc != manifest.window_start_utc
            or row.window_end_utc != manifest.window_end_utc
            or row.feature_cutoff_ts != manifest.feature_cutoff_ts
            or row.dataset_manifest_digest != manifest.dataset_manifest_digest
            or row.identity_bundle_digest != manifest.identity_bundle_digest
            or row.canonical_build_digest != manifest.canonical_build_digest
            or row.feature_registry_digest != manifest.feature_registry_digest
            or row.eligibility_policy_digest != manifest.eligibility_policy_digest
        ):
            raise error_type("matrix row temporal or lineage pins drift")
        if tuple(item.feature_name for item in row.features) != manifest.feature_names:
            raise error_type("matrix feature order is incompatible")
        if row.missing_feature_names or any(
            item.state not in {FeatureValueState.VALUE, FeatureValueState.ZERO}
            or item.value is None
            for item in row.features
        ):
            raise error_type("eligible matrix row has an absent active feature")
    return LoadedFeatureMatrix(
        manifest=manifest,
        rows=rows,
        catalogue=catalogue,
        population_decisions=population,
        eligibility_decisions=eligibility,
    )


def verify_research_index_authority(
    index: LoadedResearchIndex,
    *,
    matrix: LoadedFeatureMatrix | FeatureMatrixManifest,
    error_type: type[ValueError] = ResearchIndexBuildError,
    private_array_copy: bool = True,
) -> LoadedResearchIndex:
    """Verify and privately re-materialise one complete in-memory index authority."""

    if type(index) is not LoadedResearchIndex:
        raise TypeError("index must be an exact LoadedResearchIndex")
    manifest = _authority_model(
        index.manifest,
        ResearchIndexManifest,
        label="index manifest",
        error_type=error_type,
    )
    configuration = _authority_model(
        index.configuration,
        ResearchModelConfiguration,
        label="model configuration",
        error_type=error_type,
    )
    catalogue = _authority_rows(
        index.catalogue,
        IndexCatalogueEntry,
        label="index catalogue",
        error_type=error_type,
    )
    feature_count = len(manifest.feature_names)
    center = _authority_array(
        index.center,
        label="scaler center",
        shape=(feature_count,),
        error_type=error_type,
        private_copy=private_array_copy,
    )
    scale = _authority_array(
        index.scale,
        label="scaler scale",
        shape=(feature_count,),
        error_type=error_type,
        private_copy=private_array_copy,
    )
    vectors = _authority_array(
        index.vectors,
        label="index vectors",
        shape=(manifest.candidate_count, feature_count),
        error_type=error_type,
        private_copy=private_array_copy,
    )
    if np.any(scale <= 0.0):
        raise error_type("scaler scale must be strictly positive")
    roles = {item.role: item for item in manifest.files}
    if set(roles) != set(INDEX_ARTIFACT_PATHS) or any(
        roles[role].relative_path != path for role, path in INDEX_ARTIFACT_PATHS.items()
    ):
        raise error_type("index artifact roles or paths are incompatible")
    matrix_manifest = matrix.manifest if isinstance(matrix, LoadedFeatureMatrix) else matrix
    expected_matrix_pins = (
        matrix_manifest.feature_cutoff_ts,
        matrix_manifest.matrix_version,
        matrix_manifest.manifest_digest,
        matrix_manifest.matrix_digest,
        matrix_manifest.identity_bundle_digest,
        matrix_manifest.feature_registry_version,
        matrix_manifest.feature_registry_digest,
        matrix_manifest.eligibility_policy_version,
        matrix_manifest.eligibility_policy_digest,
        matrix_manifest.feature_names,
        matrix_manifest.matrix_row_count,
    )
    index_matrix_pins = (
        manifest.feature_cutoff_ts,
        manifest.matrix_version,
        manifest.matrix_manifest_digest,
        manifest.matrix_digest,
        manifest.identity_bundle_digest,
        manifest.feature_registry_version,
        manifest.feature_registry_digest,
        manifest.eligibility_policy_version,
        manifest.eligibility_policy_digest,
        manifest.feature_names,
        manifest.candidate_count,
    )
    if index_matrix_pins != expected_matrix_pins:
        raise error_type("index is stale or incompatible with the matrix")
    try:
        scorer_code_digest = _scorer_code_digest()
    except ResearchIndexBuildError as exc:
        raise error_type(str(exc)) from exc
    if (
        manifest.model_configuration_digest != configuration.configuration_digest
        or manifest.model_version != configuration.model_version
        or manifest.index_version != configuration.index_version
        or manifest.scorer_version != configuration.scorer_version
        or manifest.methods != configuration.methods
        or manifest.scorer_code_digest != scorer_code_digest
        or roles[MODEL_CONFIGURATION_ROLE].row_count != 1
        or roles[MODEL_CONFIGURATION_ROLE].semantic_digest != configuration.configuration_digest
    ):
        raise error_type("index configuration or scorer pin is stale")
    array_evidence = (
        (SCALER_CENTER_ROLE, center, 1),
        (SCALER_SCALE_ROLE, scale, 1),
        (INDEX_VECTORS_ROLE, vectors, len(catalogue)),
    )
    for role, array, row_count in array_evidence:
        if roles[role].row_count != row_count or roles[role].semantic_digest != (
            _array_semantic_digest(role, array)
        ):
            raise error_type(f"in-memory index array drifts for role {role}")
    if (
        len(catalogue) != manifest.candidate_count
        or roles[INDEX_CATALOGUE_ROLE].row_count != len(catalogue)
        or roles[INDEX_CATALOGUE_ROLE].semantic_digest != rows_semantic_digest(catalogue)
        or manifest.catalogue_digest != roles[INDEX_CATALOGUE_ROLE].semantic_digest
        or tuple(item.ordinal for item in catalogue) != tuple(range(len(catalogue)))
    ):
        raise error_type("index catalogue count, order or digest drifts")
    keys = tuple((item.player_id.bytes, item.grain_id) for item in catalogue)
    grain_ids = tuple(item.grain_id for item in catalogue)
    player_windows = tuple(
        (item.player_id, item.competition_id, item.season_id) for item in catalogue
    )
    if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
        raise error_type("candidate catalogue identity order is incompatible")
    if len(grain_ids) != len(set(grain_ids)):
        raise error_type("candidate catalogue contains a duplicate grain")
    if len(player_windows) != len(set(player_windows)):
        raise error_type("candidate catalogue contains a duplicate player/competition/season grain")
    if any(len(item.feature_values) != feature_count for item in catalogue):
        raise error_type("candidate catalogue feature shape is incompatible")
    if isinstance(matrix, LoadedFeatureMatrix):
        if len(catalogue) != len(matrix.rows):
            raise error_type("index catalogue does not exhaust the matrix")
        for row, indexed in zip(matrix.rows, catalogue, strict=True):
            expected = (
                row.grain_id,
                row.player_id,
                row.display_name,
                row.competition_id,
                row.competition_name,
                row.season_id,
                row.position_code,
                row.team_ids,
                row.team_names,
                row.minutes,
                row.minute_state.value,
                row.match_count,
                row.source_action_count,
                tuple(cast(float, item.value) for item in row.features),
                row.feature_cutoff_ts,
                row.source_lineage_digest,
                row.eligibility_decision_digest,
            )
            actual = (
                indexed.grain_id,
                indexed.player_id,
                indexed.display_name,
                indexed.competition_id,
                indexed.competition_name,
                indexed.season_id,
                indexed.position_code,
                indexed.team_ids,
                indexed.team_names,
                indexed.minutes,
                indexed.minute_state,
                indexed.match_count,
                indexed.source_action_count,
                indexed.feature_values,
                indexed.feature_cutoff_ts,
                indexed.source_lineage_digest,
                indexed.eligibility_decision_digest,
            )
            if actual != expected:
                raise error_type("index catalogue row drifts from the exact matrix row")
    raw = np.ascontiguousarray([item.feature_values for item in catalogue], dtype="<f8")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        expected_vectors = np.ascontiguousarray((raw - center) / scale, dtype="<f8")
    if not np.array_equal(expected_vectors, vectors):
        raise error_type("index vectors do not reproduce from raw catalogue values")
    return LoadedResearchIndex(
        manifest=manifest,
        configuration=configuration,
        center=center,
        scale=scale,
        vectors=vectors,
        catalogue=catalogue,
    )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _safe_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    parts = value.split("/")
    if path.is_absolute() or any(part in {"", ".", ".."} for part in parts):
        raise ResearchIndexBuildError("artifact path must be a normal safe relative path")
    return value


def _safe_regular_bytes(root: Path, relative_path: str) -> bytes:
    """Read a regular file under one real root without traversing symlinks."""

    relative = _safe_relative_path(relative_path)
    root_absolute = root.absolute()
    if (
        not root_absolute.exists()
        or root_absolute.is_symlink()
        or not root_absolute.is_dir()
        or root_absolute.resolve(strict=True) != root_absolute
    ):
        raise ResearchIndexBuildError("artifact root is absent or unsafe")
    current = root_absolute
    parts = relative.split("/")
    for index, part in enumerate(parts):
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError as exc:
            raise ResearchIndexBuildError(f"required artifact is absent: {relative}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise ResearchIndexBuildError(f"artifact path contains a symlink: {relative}")
        if index < len(parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise ResearchIndexBuildError(f"artifact parent is not a directory: {relative}")
    if not stat.S_ISREG(current.lstat().st_mode):
        raise ResearchIndexBuildError(f"artifact is not a regular file: {relative}")
    try:
        return current.read_bytes()
    except OSError as exc:
        raise ResearchIndexBuildError(f"artifact cannot be read: {relative}") from exc


def _canonical_json_object(payload: bytes, *, label: str) -> dict[str, object]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResearchIndexBuildError(f"{label} is not strict JSON") from exc
    if type(value) is not dict or canonical_json_bytes(value) != payload:
        raise ResearchIndexBuildError(f"{label} is not one canonical JSON object")
    return cast(dict[str, object], value)


def _validate_json_row[T: ContractModel](model: type[T], payload: bytes, *, label: str) -> T:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResearchIndexBuildError(f"{label} is not strict JSON") from exc
    if type(value) is not dict or canonical_json_bytes(value) != payload:
        raise ResearchIndexBuildError(f"{label} is not canonical JSON")
    try:
        return model.model_validate_json(payload)
    except ValidationError as exc:
        raise ResearchIndexBuildError(f"{label} violates its strict contract") from exc


def _validate_python_row[T: ContractModel](model: type[T], value: object, *, label: str) -> T:
    if type(value) is not dict:
        raise ResearchIndexBuildError(f"{label} must be a Python object row")
    if model is not FeatureMatrixRow:
        raise ResearchIndexBuildError(f"{label} has no governed Parquet Python projection")
    try:
        row = dict(value)
        row["player_id"] = UUID(cast(str, row["player_id"]))
        row["competition_id"] = UUID(cast(str, row["competition_id"]))
        row["team_ids"] = tuple(UUID(item) for item in cast(list[str], row["team_ids"]))
        row["team_names"] = tuple(cast(list[str], row["team_names"]))
        row["minute_state"] = MinuteEvidenceState(cast(str, row["minute_state"]))
        row["features"] = tuple(
            ResearchFeatureValue.model_validate(
                {
                    **feature,
                    "state": FeatureValueState(cast(str, feature["state"])),
                }
            )
            for feature in cast(list[dict[str, object]], row["features"])
        )
        row["missing_feature_names"] = tuple(cast(list[str], row["missing_feature_names"]))
        row["coverage"] = ResearchCoverage.model_validate(row["coverage"])
        for field in ("window_start_utc", "window_end_utc", "feature_cutoff_ts"):
            row[field] = datetime.fromisoformat(cast(str, row[field]))
        return cast(T, FeatureMatrixRow.model_validate(row))
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        raise ResearchIndexBuildError(f"{label} violates its strict contract") from exc


def _load_contract_rows[T: ContractModel](
    payload: bytes,
    relative_path: str,
    model: type[T],
) -> tuple[T, ...]:
    if relative_path.endswith(".jsonl"):
        if not payload or not payload.endswith(b"\n"):
            raise ResearchIndexBuildError("JSONL artifact must be non-empty and newline terminated")
        encoded = payload.splitlines(keepends=True)
        return tuple(
            _validate_json_row(model, row, label=f"{relative_path} row {index}")
            for index, row in enumerate(encoded)
        )
    if relative_path.endswith(".json"):
        try:
            value = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ResearchIndexBuildError(f"{relative_path} is not strict JSON") from exc
        if type(value) is not list or canonical_json_bytes(value) != payload:
            raise ResearchIndexBuildError(f"{relative_path} must be one canonical JSON array")
        return tuple(
            _validate_json_row(
                model,
                canonical_json_bytes(row),
                label=f"{relative_path} row {index}",
            )
            for index, row in enumerate(value)
        )
    if relative_path.endswith(".parquet"):
        try:
            table = pq.read_table(pa.BufferReader(payload))
        except (OSError, pa.ArrowException) as exc:
            raise ResearchIndexBuildError(f"{relative_path} is not readable Parquet") from exc
        return tuple(
            _validate_python_row(
                model,
                row,
                label=f"{relative_path} row {index}",
            )
            for index, row in enumerate(table.to_pylist())
        )
    raise ResearchIndexBuildError("contract-row artifacts must be JSON, JSONL, or Parquet")


def _verify_contract_artifact[T: ContractModel](
    *,
    root: Path,
    descriptor: ResearchArtifactFile,
    model: type[T],
) -> tuple[T, ...]:
    payload = _safe_regular_bytes(root, descriptor.relative_path)
    if len(payload) != descriptor.size_bytes or _sha256(payload) != descriptor.sha256:
        raise ResearchIndexBuildError(f"physical artifact drift for role {descriptor.role}")
    rows = _load_contract_rows(payload, descriptor.relative_path, model)
    if len(rows) != descriptor.row_count:
        raise ResearchIndexBuildError(f"row-count drift for role {descriptor.role}")
    if rows_semantic_digest(rows) != descriptor.semantic_digest:
        raise ResearchIndexBuildError(f"semantic artifact drift for role {descriptor.role}")
    return rows


def _require_mode_paths(
    *,
    mode: ResearchIndexBuildMode,
    manifest_root: Path | None = None,
    manifest_path: Path | None = None,
    matrix_root: Path | None = None,
    output_root: Path | None = None,
    config_path: Path | None = None,
) -> None:
    if type(mode) is not ResearchIndexBuildMode:
        raise ResearchIndexBuildError("an exact research index build mode is required")
    resolved_manifest_root = (
        manifest_root
        if manifest_root is not None
        else manifest_path.parent
        if manifest_path is not None
        else None
    )
    if mode is ResearchIndexBuildMode.TEST_FIXTURE:
        fixture_roots = (
            (resolved_manifest_root, DEFAULT_FEATURE_MANIFEST_ROOT),
            (matrix_root, DEFAULT_MATRIX_ARTIFACT_ROOT),
            (output_root, DEFAULT_INDEX_ROOT),
        )
        if any(
            actual is not None and actual.absolute() == governed.absolute()
            for actual, governed in fixture_roots
        ):
            raise ResearchIndexBuildError(
                "test-fixture construction cannot target governed W09 artifact roots"
            )
        return
    if mode is ResearchIndexBuildMode.VERIFICATION:
        verification_roots = (
            (resolved_manifest_root, DEFAULT_FEATURE_MANIFEST_ROOT),
            (matrix_root, DEFAULT_MATRIX_ARTIFACT_ROOT),
            (output_root, DEFAULT_INDEX_ROOT),
        )
        if any(
            actual is not None and actual.absolute() == governed.absolute()
            for actual, governed in verification_roots
        ) or (config_path is not None and config_path.absolute() != DEFAULT_MODEL_CONFIG_PATH):
            raise ResearchIndexBuildError(
                "verification requires temporary artifact roots and the governed model config"
            )
        return
    expected = (
        (resolved_manifest_root, DEFAULT_FEATURE_MANIFEST_ROOT),
        (matrix_root, DEFAULT_MATRIX_ARTIFACT_ROOT),
        (output_root, DEFAULT_INDEX_ROOT),
        (config_path, DEFAULT_MODEL_CONFIG_PATH),
    )
    for actual, governed in expected:
        if actual is not None and actual.absolute() != governed.absolute():
            raise ResearchIndexBuildError("production construction requires the governed W09 paths")


def discover_feature_matrix_manifest(
    manifest_root: Path = DEFAULT_FEATURE_MANIFEST_ROOT,
    *,
    mode: ResearchIndexBuildMode = ResearchIndexBuildMode.PRODUCTION,
) -> Path:
    """Find exactly one accepted feature manifest; never choose newest or fall back."""

    _require_mode_paths(
        mode=mode,
        manifest_root=manifest_root,
    )
    if not manifest_root.exists() or manifest_root.is_symlink() or not manifest_root.is_dir():
        raise ResearchIndexBuildError("accepted W09 feature manifest root is absent or unsafe")
    candidates = tuple(
        sorted(
            (
                item
                for item in manifest_root.iterdir()
                if item.name.endswith(".manifest.json")
                and not item.name.endswith(".manifest.json.manifest.json")
            ),
            key=lambda item: item.name,
        )
    )
    if len(candidates) != 1 or candidates[0].is_symlink() or not candidates[0].is_file():
        raise ResearchIndexBuildError("exactly one accepted W09 feature manifest is required")
    return candidates[0]


def load_feature_matrix(
    manifest_path: Path,
    *,
    artifact_root: Path,
    mode: ResearchIndexBuildMode = ResearchIndexBuildMode.PRODUCTION,
) -> LoadedFeatureMatrix:
    """Load and reconcile every governed matrix authority before fitting."""

    _require_mode_paths(mode=mode, manifest_path=manifest_path, matrix_root=artifact_root)
    manifest_payload = _safe_regular_bytes(manifest_path.parent, manifest_path.name)
    _canonical_json_object(manifest_payload, label="feature matrix manifest")
    try:
        manifest = FeatureMatrixManifest.model_validate_json(manifest_payload)
    except ValidationError as exc:
        raise ResearchIndexBuildError("feature matrix manifest is incompatible") from exc
    roles = {item.role: item for item in manifest.files}
    if set(roles) != MATRIX_ARTIFACT_ROLES:
        raise ResearchIndexBuildError("feature matrix manifest has incompatible artifact roles")

    catalogue = cast(
        tuple[MatrixCatalogueEntry, ...],
        _verify_contract_artifact(
            root=artifact_root,
            descriptor=roles[PLAYER_CATALOGUE_ROLE],
            model=MatrixCatalogueEntry,
        ),
    )
    population = cast(
        tuple[SourcePopulationDecision, ...],
        _verify_contract_artifact(
            root=artifact_root,
            descriptor=roles[POPULATION_DECISIONS_ROLE],
            model=SourcePopulationDecision,
        ),
    )
    eligibility = cast(
        tuple[EligibilityDecision, ...],
        _verify_contract_artifact(
            root=artifact_root,
            descriptor=roles[ELIGIBILITY_DECISIONS_ROLE],
            model=EligibilityDecision,
        ),
    )
    matrix_rows = cast(
        tuple[FeatureMatrixRow, ...],
        _verify_contract_artifact(
            root=artifact_root,
            descriptor=roles[FEATURE_MATRIX_ROWS_ROLE],
            model=FeatureMatrixRow,
        ),
    )
    return verify_feature_matrix_authority(
        LoadedFeatureMatrix(
            manifest=manifest,
            rows=matrix_rows,
            catalogue=catalogue,
            population_decisions=population,
            eligibility_decisions=eligibility,
        )
    )


def load_model_configuration(path: Path = DEFAULT_MODEL_CONFIG_PATH) -> ResearchModelConfiguration:
    payload = _safe_regular_bytes(path.parent, path.name)
    _canonical_json_object(payload, label="research model configuration")
    try:
        return ResearchModelConfiguration.model_validate_json(payload)
    except ValidationError as exc:
        raise ResearchIndexBuildError("research model configuration is incompatible") from exc


def fit_robust_scaler(matrix: np.ndarray) -> RobustScaledMatrix:
    """Fit median/IQR scaling across every row without sampling or imputation."""

    values = np.asarray(matrix)
    if (
        values.dtype != np.dtype("<f8")
        or values.ndim != 2
        or values.shape[0] < 1
        or values.shape[1] < 1
        or not values.flags.c_contiguous
        or not np.all(np.isfinite(values))
    ):
        raise ResearchIndexBuildError(
            "robust scaling requires a complete C-order little-endian float64 matrix"
        )
    center = np.ascontiguousarray(np.median(values, axis=0), dtype="<f8")
    lower = np.quantile(values, 0.25, axis=0, method="linear")
    upper = np.quantile(values, 0.75, axis=0, method="linear")
    scale = np.ascontiguousarray(upper - lower, dtype="<f8")
    if not np.all(np.isfinite(center)) or not np.all(np.isfinite(scale)) or np.any(scale < 0.0):
        raise ResearchIndexBuildError("robust scaler statistics are outside the finite domain")
    scale[scale == 0.0] = 1.0
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        vectors = np.ascontiguousarray((values - center) / scale, dtype="<f8")
    if not np.all(np.isfinite(vectors)):
        raise ResearchIndexBuildError("robust scaling produced a non-finite vector")
    for array in (center, scale, vectors):
        array[array == 0.0] = 0.0
        array.setflags(write=False)
    return RobustScaledMatrix(center=center, scale=scale, vectors=vectors)


def _array_payload(array: np.ndarray) -> bytes:
    output = io.BytesIO()
    np.lib.format.write_array(
        output,
        np.ascontiguousarray(array, dtype="<f8"),
        version=(2, 0),
        allow_pickle=False,
    )
    return output.getvalue()


def _array_semantic_digest(role: str, array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array, dtype="<f8")
    return canonical_research_digest(
        {
            "data_sha256": _sha256(contiguous.tobytes(order="C")),
            "dtype": "<f8",
            "memory_order": "C",
            "role": role,
            "schema_version": 1,
            "shape": list(contiguous.shape),
        }
    )


def _scorer_code_digest() -> str:
    path = SHARED_SCORER_SOURCE_PATH
    if path.is_symlink() or not path.is_file():
        raise ResearchIndexBuildError("shared scorer source path is unsafe")
    return _sha256(path.read_bytes())


def _artifact_file(
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


def _require_safe_destination(destination: Path) -> Path:
    absolute = destination.absolute()
    for ancestor in (absolute, *absolute.parents):
        if not ancestor.exists():
            continue
        if ancestor.is_symlink() or ancestor.resolve(strict=True) != ancestor:
            raise ResearchIndexBuildError("index destination contains an unsafe ancestor")
    absolute.mkdir(mode=0o700, parents=True, exist_ok=True)
    if absolute.is_symlink() or not absolute.is_dir() or absolute.resolve(strict=True) != absolute:
        raise ResearchIndexBuildError("index destination is unsafe")
    return absolute


def _preflight_and_write(destination: Path, payloads: Mapping[str, bytes]) -> None:
    for name, payload in payloads.items():
        target = destination / _safe_relative_path(name)
        if target.exists():
            if target.is_symlink() or not target.is_file() or target.read_bytes() != payload:
                raise ResearchIndexBuildError(f"immutable index artifact conflicts at {name}")
    directory_descriptor = os.open(
        destination,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        for name, payload in payloads.items():
            target = destination / name
            if target.exists():
                continue
            temporary_name = f".{name}.{uuid.uuid4().hex}.tmp"
            temporary_descriptor: int | None = None
            temporary_exists = False
            try:
                temporary_descriptor = os.open(
                    temporary_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                    dir_fd=directory_descriptor,
                )
                temporary_exists = True
                view = memoryview(payload)
                while view:
                    written = os.write(temporary_descriptor, view)
                    if written <= 0:
                        raise ResearchIndexBuildError("immutable artifact write made no progress")
                    view = view[written:]
                os.fsync(temporary_descriptor)
                os.close(temporary_descriptor)
                temporary_descriptor = None
                try:
                    os.link(
                        temporary_name,
                        name,
                        src_dir_fd=directory_descriptor,
                        dst_dir_fd=directory_descriptor,
                        follow_symlinks=False,
                    )
                except FileExistsError as exc:
                    if (
                        target.is_symlink()
                        or not target.is_file()
                        or target.read_bytes() != payload
                    ):
                        raise ResearchIndexBuildError(
                            f"immutable index artifact conflicts at {name}"
                        ) from exc
                else:
                    os.fsync(directory_descriptor)
            finally:
                if temporary_descriptor is not None:
                    os.close(temporary_descriptor)
                if temporary_exists:
                    try:
                        os.unlink(temporary_name, dir_fd=directory_descriptor)
                    except FileNotFoundError:
                        pass
    finally:
        os.close(directory_descriptor)


def _index_catalogue(rows: Sequence[FeatureMatrixRow]) -> tuple[IndexCatalogueEntry, ...]:
    return tuple(
        IndexCatalogueEntry(
            ordinal=index,
            grain_id=row.grain_id,
            player_id=row.player_id,
            display_name=row.display_name,
            competition_id=row.competition_id,
            competition_name=row.competition_name,
            season_id=row.season_id,
            position_code=row.position_code,
            team_ids=row.team_ids,
            team_names=row.team_names,
            minutes=row.minutes,
            minute_state=cast(Literal["exact", "conservative_lower_bound"], row.minute_state.value),
            match_count=row.match_count,
            source_action_count=row.source_action_count,
            feature_values=tuple(cast(float, feature.value) for feature in row.features),
            feature_cutoff_ts=row.feature_cutoff_ts,
            source_lineage_digest=row.source_lineage_digest,
            eligibility_decision_digest=row.eligibility_decision_digest,
        )
        for index, row in enumerate(rows)
    )


def build_research_index(
    *,
    matrix_manifest_path: Path,
    matrix_artifact_root: Path,
    output_root: Path,
    model_config_path: Path = DEFAULT_MODEL_CONFIG_PATH,
    mode: ResearchIndexBuildMode = ResearchIndexBuildMode.PRODUCTION,
) -> ResearchIndexManifest:
    """Build immutable exhaustive retrieval arrays over the exact eligible matrix."""

    _require_mode_paths(
        mode=mode,
        manifest_path=matrix_manifest_path,
        matrix_root=matrix_artifact_root,
        output_root=output_root,
        config_path=model_config_path,
    )
    loaded = load_feature_matrix(
        matrix_manifest_path,
        artifact_root=matrix_artifact_root,
        mode=mode,
    )
    configuration = load_model_configuration(model_config_path)
    raw = np.ascontiguousarray(
        [[cast(float, feature.value) for feature in row.features] for row in loaded.rows],
        dtype="<f8",
    )
    fitted = fit_robust_scaler(raw)
    catalogue = _index_catalogue(loaded.rows)
    catalogue_payload = canonical_jsonl_bytes([row.model_dump(mode="json") for row in catalogue])
    config_payload = canonical_json_bytes(configuration.model_dump(mode="json"))
    payloads = {
        INDEX_ARTIFACT_PATHS[SCALER_CENTER_ROLE]: _array_payload(fitted.center),
        INDEX_ARTIFACT_PATHS[SCALER_SCALE_ROLE]: _array_payload(fitted.scale),
        INDEX_ARTIFACT_PATHS[INDEX_VECTORS_ROLE]: _array_payload(fitted.vectors),
        INDEX_ARTIFACT_PATHS[INDEX_CATALOGUE_ROLE]: catalogue_payload,
        INDEX_ARTIFACT_PATHS[MODEL_CONFIGURATION_ROLE]: config_payload,
    }
    files = (
        _artifact_file(
            role=SCALER_CENTER_ROLE,
            relative_path=INDEX_ARTIFACT_PATHS[SCALER_CENTER_ROLE],
            payload=payloads[INDEX_ARTIFACT_PATHS[SCALER_CENTER_ROLE]],
            row_count=1,
            semantic_digest=_array_semantic_digest(SCALER_CENTER_ROLE, fitted.center),
        ),
        _artifact_file(
            role=SCALER_SCALE_ROLE,
            relative_path=INDEX_ARTIFACT_PATHS[SCALER_SCALE_ROLE],
            payload=payloads[INDEX_ARTIFACT_PATHS[SCALER_SCALE_ROLE]],
            row_count=1,
            semantic_digest=_array_semantic_digest(SCALER_SCALE_ROLE, fitted.scale),
        ),
        _artifact_file(
            role=INDEX_VECTORS_ROLE,
            relative_path=INDEX_ARTIFACT_PATHS[INDEX_VECTORS_ROLE],
            payload=payloads[INDEX_ARTIFACT_PATHS[INDEX_VECTORS_ROLE]],
            row_count=len(loaded.rows),
            semantic_digest=_array_semantic_digest(INDEX_VECTORS_ROLE, fitted.vectors),
        ),
        _artifact_file(
            role=INDEX_CATALOGUE_ROLE,
            relative_path=INDEX_ARTIFACT_PATHS[INDEX_CATALOGUE_ROLE],
            payload=catalogue_payload,
            row_count=len(catalogue),
            semantic_digest=rows_semantic_digest(catalogue),
        ),
        _artifact_file(
            role=MODEL_CONFIGURATION_ROLE,
            relative_path=INDEX_ARTIFACT_PATHS[MODEL_CONFIGURATION_ROLE],
            payload=config_payload,
            row_count=1,
            semantic_digest=configuration.configuration_digest,
        ),
    )
    scorer_digest = _scorer_code_digest()
    catalogue_digest = rows_semantic_digest(catalogue)
    identity = uuid5(
        NAMESPACE_URL,
        "\0".join(
            (
                "urn:scouting-intelligence:w09:research-index:v1",
                loaded.manifest.manifest_digest,
                loaded.manifest.matrix_digest,
                configuration.configuration_digest,
                scorer_digest,
                catalogue_digest,
                *[file.sha256 for file in files],
            )
        ),
    )
    manifest_payload: dict[str, Any] = {
        "schema_version": 1,
        "index_id": str(identity),
        "index_version": configuration.index_version,
        "generated_at": loaded.manifest.generated_at.isoformat().replace("+00:00", "Z"),
        "feature_cutoff_ts": loaded.manifest.feature_cutoff_ts.isoformat().replace("+00:00", "Z"),
        "matrix_version": loaded.manifest.matrix_version,
        "matrix_manifest_digest": loaded.manifest.manifest_digest,
        "matrix_digest": loaded.manifest.matrix_digest,
        "identity_bundle_digest": loaded.manifest.identity_bundle_digest,
        "feature_registry_version": loaded.manifest.feature_registry_version,
        "feature_registry_digest": loaded.manifest.feature_registry_digest,
        "eligibility_policy_version": loaded.manifest.eligibility_policy_version,
        "eligibility_policy_digest": loaded.manifest.eligibility_policy_digest,
        "model_version": configuration.model_version,
        "model_configuration_digest": configuration.configuration_digest,
        "scorer_version": configuration.scorer_version,
        "scorer_code_digest": scorer_digest,
        "methods": [method.value for method in configuration.methods],
        "feature_names": list(loaded.manifest.feature_names),
        "candidate_count": len(loaded.rows),
        "catalogue_digest": catalogue_digest,
        "files": [file.model_dump(mode="json") for file in files],
        "contains_synthetic_rows": False,
        "limitations": [
            "Historical 2017/18 resemblance evidence is not current-market coverage.",
            (
                "Robust scaling uses the full eligible population; constant features are "
                "retained with unit scale."
            ),
            (
                "Both methods score every admitted row in process; no ANN or pre-limit "
                "approximation is used."
            ),
            (
                "No football-expert relevance, recruitment usefulness, outcome, value or "
                "recommendation claim is supported."
            ),
        ],
        "claim_boundary": "historical_resemblance_research_only",
    }
    manifest_payload["manifest_digest"] = canonical_research_digest(
        {
            key: value
            for key, value in manifest_payload.items()
            if key not in {"manifest_digest", "generated_at"}
        }
    )
    try:
        manifest = ResearchIndexManifest.model_validate_json(canonical_json_bytes(manifest_payload))
    except ValidationError as exc:
        raise ResearchIndexBuildError("constructed research index manifest is invalid") from exc
    payloads["manifest.json"] = canonical_json_bytes(manifest.model_dump(mode="json"))
    destination = _require_safe_destination(output_root)
    _preflight_and_write(destination, payloads)
    return manifest


def _load_array(
    *, root: Path, descriptor: ResearchArtifactFile, role: str, shape: tuple[int, ...]
) -> np.ndarray:
    payload = _safe_regular_bytes(root, descriptor.relative_path)
    if len(payload) != descriptor.size_bytes or _sha256(payload) != descriptor.sha256:
        raise ResearchIndexBuildError(f"physical index artifact drift for role {role}")
    try:
        array = np.load(io.BytesIO(payload), allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise ResearchIndexBuildError(f"index array cannot be loaded for role {role}") from exc
    if (
        not isinstance(array, np.ndarray)
        or array.dtype.str != "<f8"
        or array.shape != shape
        or not array.flags.c_contiguous
        or (array.ndim > 1 and array.flags.f_contiguous and min(array.shape) > 1)
        or not np.all(np.isfinite(array))
        or np.any(np.signbit(array) & (array == 0.0))
    ):
        raise ResearchIndexBuildError(f"index array dtype/order/shape is invalid for role {role}")
    array = np.ascontiguousarray(array, dtype="<f8")
    if _array_semantic_digest(role, array) != descriptor.semantic_digest:
        raise ResearchIndexBuildError(f"semantic index artifact drift for role {role}")
    array.setflags(write=False)
    return array


def load_research_index(
    index_root: Path,
    *,
    matrix_manifest: FeatureMatrixManifest,
    mode: ResearchIndexBuildMode = ResearchIndexBuildMode.PRODUCTION,
) -> LoadedResearchIndex:
    """Load an immutable index and fail closed on bytes, scorer, or matrix drift."""

    _require_mode_paths(mode=mode, output_root=index_root)
    manifest_payload = _safe_regular_bytes(index_root, "manifest.json")
    _canonical_json_object(manifest_payload, label="research index manifest")
    try:
        manifest = ResearchIndexManifest.model_validate_json(manifest_payload)
    except ValidationError as exc:
        raise ResearchIndexBuildError("research index manifest is incompatible") from exc
    roles = {item.role: item for item in manifest.files}
    if set(roles) != set(INDEX_ARTIFACT_PATHS) or any(
        roles[role].relative_path != path for role, path in INDEX_ARTIFACT_PATHS.items()
    ):
        raise ResearchIndexBuildError("research index artifact roster is incompatible")

    config_descriptor = roles[MODEL_CONFIGURATION_ROLE]
    config_payload = _safe_regular_bytes(index_root, config_descriptor.relative_path)
    _canonical_json_object(config_payload, label="model configuration artifact")
    if (
        len(config_payload) != config_descriptor.size_bytes
        or _sha256(config_payload) != config_descriptor.sha256
    ):
        raise ResearchIndexBuildError("model configuration physical artifact drift")
    try:
        configuration = ResearchModelConfiguration.model_validate_json(config_payload)
    except ValidationError as exc:
        raise ResearchIndexBuildError("model configuration artifact is incompatible") from exc

    feature_count = len(manifest.feature_names)
    center = _load_array(
        root=index_root,
        descriptor=roles[SCALER_CENTER_ROLE],
        role=SCALER_CENTER_ROLE,
        shape=(feature_count,),
    )
    scale = _load_array(
        root=index_root,
        descriptor=roles[SCALER_SCALE_ROLE],
        role=SCALER_SCALE_ROLE,
        shape=(feature_count,),
    )
    vectors = _load_array(
        root=index_root,
        descriptor=roles[INDEX_VECTORS_ROLE],
        role=INDEX_VECTORS_ROLE,
        shape=(manifest.candidate_count, feature_count),
    )

    catalogue_descriptor = roles[INDEX_CATALOGUE_ROLE]
    catalogue_payload = _safe_regular_bytes(index_root, catalogue_descriptor.relative_path)
    if (
        len(catalogue_payload) != catalogue_descriptor.size_bytes
        or _sha256(catalogue_payload) != catalogue_descriptor.sha256
    ):
        raise ResearchIndexBuildError("candidate catalogue physical artifact drift")
    catalogue = cast(
        tuple[IndexCatalogueEntry, ...],
        _load_contract_rows(
            catalogue_payload,
            catalogue_descriptor.relative_path,
            IndexCatalogueEntry,
        ),
    )
    return verify_research_index_authority(
        LoadedResearchIndex(
            manifest=manifest,
            configuration=configuration,
            center=center,
            scale=scale,
            vectors=vectors,
            catalogue=catalogue,
        ),
        matrix=matrix_manifest,
        private_array_copy=False,
    )


__all__ = [
    "DEFAULT_FEATURE_MANIFEST_ROOT",
    "DEFAULT_INDEX_ROOT",
    "DEFAULT_MATRIX_ARTIFACT_ROOT",
    "DEFAULT_MODEL_CONFIG_PATH",
    "ELIGIBILITY_DECISIONS_ROLE",
    "FEATURE_MATRIX_ROWS_ROLE",
    "INDEX_ARTIFACT_PATHS",
    "INDEX_CATALOGUE_ROLE",
    "INDEX_VECTORS_ROLE",
    "IndexCatalogueEntry",
    "LoadedFeatureMatrix",
    "LoadedResearchIndex",
    "MATRIX_ARTIFACT_ROLES",
    "MODEL_CONFIGURATION_ROLE",
    "MatrixCatalogueEntry",
    "PLAYER_CATALOGUE_ROLE",
    "POPULATION_DECISIONS_ROLE",
    "ResearchIndexBuildError",
    "ResearchIndexBuildMode",
    "ResearchModelConfiguration",
    "RobustScaledMatrix",
    "SCALER_CENTER_ROLE",
    "SCALER_SCALE_ROLE",
    "build_research_index",
    "discover_feature_matrix_manifest",
    "fit_robust_scaler",
    "load_feature_matrix",
    "load_model_configuration",
    "load_research_index",
    "population_referred_grain_digest",
    "rows_semantic_digest",
    "verify_feature_matrix_authority",
    "verify_readonly_array",
    "verify_research_index_authority",
]

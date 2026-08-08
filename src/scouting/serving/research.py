"""Strict in-process retrieval over one exact governed W09 matrix and index."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import RLock
from types import MappingProxyType
from typing import cast
from uuid import NAMESPACE_URL, uuid5

import numpy as np
from pydantic import ValidationError

from scouting.contracts.numerics import (
    StableNormalizationError,
    stable_weighted_unit_components,
)
from scouting.contracts.primitives import ContractModel
from scouting.contracts.research import (
    FeatureContribution,
    FeatureMatrixManifest,
    FeatureMatrixRow,
    ResearchCandidate,
    ResearchComparison,
    ResearchComparisonRequest,
    ResearchIndexManifest,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchQueryResult,
    ResearchVersionPins,
    RetrievalPopulationCounts,
    canonical_research_digest,
)
from scouting.contracts.validation import revalidate_exact_contract
from scouting.m0.scoring import (
    ScoredVectorRow,
    VectorCandidateKey,
    VectorScoringMethod,
    score_vector_rows,
)
from scouting.modeling.research import (
    IndexCatalogueEntry,
    LoadedFeatureMatrix,
    LoadedResearchIndex,
    verify_feature_matrix_authority,
    verify_readonly_array,
    verify_research_index_authority,
)

_RESULT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w09:research-query-result:v1",
)
_HISTORICAL_LIMITATION = (
    "Historical 2017/18 resemblance evidence only; this is not current-market coverage."
)
_EXPERT_LIMITATION = (
    "G-RW4 expert relevance evidence is absent; no future-performance, value, "
    "availability, fit, outcome or decision claim is supported."
)
_VECTOR_SLICE_CACHE_LIMIT = 64


class ResearchServingError(ValueError):
    """A pinned W09 serving input or loaded authority failed closed."""


class ResearchServingConflictError(ResearchServingError):
    """A request conflicts with the loaded immutable serving authority."""


def _fresh_model[T: ContractModel](value: T, model: type[T], *, label: str) -> T:
    return revalidate_exact_contract(
        value,
        model,
        label=label,
        error_type=ResearchServingError,
    )


def _validate_matrix_authority(matrix: LoadedFeatureMatrix) -> LoadedFeatureMatrix:
    return verify_feature_matrix_authority(
        matrix,
        error_type=ResearchServingConflictError,
    )


def _validate_index_authority(
    index: LoadedResearchIndex,
    *,
    matrix: LoadedFeatureMatrix,
) -> LoadedResearchIndex:
    return verify_research_index_authority(
        index,
        matrix=matrix,
        error_type=ResearchServingConflictError,
    )


def _validated_array(
    value: np.ndarray,
    *,
    label: str,
    shape: tuple[int, ...],
) -> np.ndarray:
    """Compatibility wrapper over the shared canonical array authority."""

    return verify_readonly_array(
        value,
        label=label,
        shape=shape,
        error_type=ResearchServingConflictError,
    )


def _derived_pins(
    matrix: LoadedFeatureMatrix,
    index: LoadedResearchIndex,
) -> ResearchVersionPins:
    matrix_manifest = matrix.manifest
    index_manifest = index.manifest
    return ResearchVersionPins(
        feature_cutoff_ts=matrix_manifest.feature_cutoff_ts,
        dataset_version=matrix_manifest.dataset_version,
        dataset_manifest_digest=matrix_manifest.dataset_manifest_digest,
        identity_bundle_digest=matrix_manifest.identity_bundle_digest,
        canonical_build_digest=matrix_manifest.canonical_build_digest,
        matrix_version=matrix_manifest.matrix_version,
        matrix_manifest_digest=matrix_manifest.manifest_digest,
        matrix_digest=matrix_manifest.matrix_digest,
        feature_registry_version=matrix_manifest.feature_registry_version,
        feature_registry_digest=matrix_manifest.feature_registry_digest,
        eligibility_policy_version=matrix_manifest.eligibility_policy_version,
        eligibility_policy_digest=matrix_manifest.eligibility_policy_digest,
        model_version=index_manifest.model_version,
        model_configuration_digest=index_manifest.model_configuration_digest,
        scorer_version=index_manifest.scorer_version,
        scorer_code_digest=index_manifest.scorer_code_digest,
        index_version=index_manifest.index_version,
        index_manifest_digest=index_manifest.manifest_digest,
        catalogue_digest=index_manifest.catalogue_digest,
    )


def _validated_generated_at(value: datetime, *, request: ResearchQueryRequest) -> datetime:
    if type(value) is not datetime:
        raise TypeError("generated_at must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ResearchServingError("generated_at must be timezone-aware UTC")
    if value < request.requested_at:
        raise ResearchServingError("result cannot be generated before its request")
    return value


def _deduplicated(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


@dataclass(frozen=True, slots=True, init=False)
class ResearchServingService:
    """Immutable serving authority over one exact matrix, index, and pin set."""

    _matrix: LoadedFeatureMatrix
    _index: LoadedResearchIndex
    _pins: ResearchVersionPins
    _rows_by_grain: Mapping[str, FeatureMatrixRow]
    _catalogue_by_key: Mapping[VectorCandidateKey, IndexCatalogueEntry]
    _candidate_keys: tuple[VectorCandidateKey, ...]
    _feature_indices: Mapping[str, int]
    _vector_slice_cache: OrderedDict[tuple[int, ...], np.ndarray]
    _vector_slice_lock: RLock

    def __init__(
        self,
        *,
        matrix: LoadedFeatureMatrix,
        index: LoadedResearchIndex,
        pins: ResearchVersionPins,
    ) -> None:
        validated_matrix = _validate_matrix_authority(matrix)
        validated_index = _validate_index_authority(index, matrix=validated_matrix)
        validated_pins = _fresh_model(pins, ResearchVersionPins, label="research version pins")
        derived = _derived_pins(validated_matrix, validated_index)
        try:
            validated_pins.assert_compatible(derived)
        except ValueError as exc:
            raise ResearchServingConflictError(
                "submitted service pins are stale or incompatible"
            ) from exc
        rows_by_grain = {item.grain_id: item for item in validated_matrix.rows}
        catalogue_by_key = {
            VectorCandidateKey(player_id=item.player_id, grain_id=item.grain_id): item
            for item in validated_index.catalogue
        }
        candidate_keys = tuple(
            VectorCandidateKey(player_id=item.player_id, grain_id=item.grain_id)
            for item in validated_index.catalogue
        )
        feature_indices = {
            name: index for index, name in enumerate(validated_index.manifest.feature_names)
        }
        object.__setattr__(self, "_matrix", validated_matrix)
        object.__setattr__(self, "_index", validated_index)
        object.__setattr__(self, "_pins", validated_pins)
        object.__setattr__(self, "_rows_by_grain", MappingProxyType(rows_by_grain))
        object.__setattr__(self, "_catalogue_by_key", MappingProxyType(catalogue_by_key))
        object.__setattr__(self, "_candidate_keys", candidate_keys)
        object.__setattr__(self, "_feature_indices", MappingProxyType(feature_indices))
        object.__setattr__(self, "_vector_slice_cache", OrderedDict())
        object.__setattr__(self, "_vector_slice_lock", RLock())

    @property
    def pins(self) -> ResearchVersionPins:
        return self._pins

    @property
    def matrix_manifest(self) -> FeatureMatrixManifest:
        return self._matrix.manifest

    @property
    def matrix_rows(self) -> tuple[FeatureMatrixRow, ...]:
        """Validated frozen rows for the governed player catalogue."""

        return self._matrix.rows

    @property
    def index_manifest(self) -> ResearchIndexManifest:
        return self._index.manifest

    def execute_query(
        self,
        request: ResearchQueryRequest,
        *,
        generated_at: datetime,
    ) -> ResearchQueryResult:
        """Score the entire admitted population, then apply the response limit."""

        validated = _fresh_model(request, ResearchQueryRequest, label="research query")
        generated = _validated_generated_at(generated_at, request=validated)
        try:
            validated.pins.assert_compatible(self._pins)
        except ValueError as exc:
            raise ResearchServingConflictError("query pins are stale or incompatible") from exc
        if validated.method not in self._index.manifest.methods:
            raise ResearchServingError("query method is not declared by the pinned index")
        active_names = tuple(item.feature_name for item in validated.weights)
        try:
            active_indices = tuple(self._feature_indices[name] for name in active_names)
        except KeyError as exc:
            raise ResearchServingError("query contains an unknown active feature") from exc
        if active_indices != tuple(sorted(active_indices)):
            raise ResearchServingError(
                "active feature names must be an ordered subset of the index registry"
            )
        weights = np.ascontiguousarray(
            [item.weight for item in validated.weights],
            dtype="<f8",
        )
        query_raw = self._query_raw_values(validated, active_indices)
        center = np.ascontiguousarray(self._index.center[list(active_indices)], dtype="<f8")
        scale = np.ascontiguousarray(self._index.scale[list(active_indices)], dtype="<f8")
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            query_scaled = np.ascontiguousarray((query_raw - center) / scale, dtype="<f8")
        if not np.all(np.isfinite(query_scaled)):
            raise ResearchServingError("query robust scaling produced a non-finite value")
        query_scaled[query_scaled == 0.0] = 0.0

        admitted, population, lower_bound_count = self._filter_population(validated)
        vectors = self._vector_slice(active_indices)
        try:
            scored = score_vector_rows(
                query=query_scaled,
                candidate_vectors=vectors,
                candidate_keys=self._candidate_keys,
                method=VectorScoringMethod(validated.method.value),
                weights=weights,
                admitted=admitted,
                limit=validated.limit,
                candidate_keys_validated=True,
            )
        except ValueError as exc:
            raise ResearchServingError("shared scorer rejected the pinned query") from exc
        if len(scored) != min(population.scored_rows, validated.limit):
            raise ResearchServingConflictError(
                "scorer result count drifted from population accounting"
            )
        candidates = self._candidates(
            scored=scored,
            request=validated,
            active_indices=active_indices,
            query_raw=query_raw,
            query_scaled=query_scaled,
            weights=weights,
        )
        warnings = list(
            _deduplicated(
                (
                    _HISTORICAL_LIMITATION,
                    _EXPERT_LIMITATION,
                    *self._matrix.manifest.limitations,
                    *self._index.manifest.limitations,
                )
            )
        )
        if lower_bound_count:
            warnings.append(
                f"{lower_bound_count} scored player row(s) use conservative lower-bound minutes."
            )
        result_id = uuid5(
            _RESULT_NAMESPACE,
            f"{validated.query_digest}\0{self._index.manifest.manifest_digest}",
        )
        warnings_tuple = tuple(warnings)
        draft = ResearchQueryResult.model_construct(
            result_id=result_id,
            request=validated,
            generated_at=generated,
            population=population,
            candidates=candidates,
            warnings=warnings_tuple,
            result_digest="0" * 64,
        )
        try:
            return ResearchQueryResult(
                result_id=result_id,
                request=validated,
                generated_at=generated,
                population=population,
                candidates=candidates,
                warnings=warnings_tuple,
                result_digest=canonical_research_digest(draft.digest_projection()),
            )
        except ValidationError as exc:
            raise ResearchServingError("constructed research result contract rejected") from exc

    def compare(
        self,
        request: ResearchComparisonRequest,
        result: ResearchQueryResult,
    ) -> ResearchComparison:
        """Return exact matrix rows only for candidates from one exact served result."""

        validated_request = _fresh_model(
            request,
            ResearchComparisonRequest,
            label="comparison request",
        )
        validated_result = _fresh_model(
            result,
            ResearchQueryResult,
            label="research result",
        )
        expected_result_id = uuid5(
            _RESULT_NAMESPACE,
            f"{validated_result.request.query_digest}\0{self._index.manifest.manifest_digest}",
        )
        if validated_result.result_id != expected_result_id:
            raise ResearchServingConflictError(
                "result identity conflicts with the pinned serving authority"
            )
        if (
            validated_request.result_id != validated_result.result_id
            or validated_request.result_digest != validated_result.result_digest
            or validated_request.query_digest != validated_result.request.query_digest
            or validated_request.pins != self._pins
        ):
            raise ResearchServingConflictError("comparison request is stale or mismatched")
        candidates = {item.grain_id: item for item in validated_result.candidates}
        if not set(validated_request.grain_ids).issubset(candidates):
            raise ResearchServingError("comparison contains a non-candidate grain")
        rows = tuple(self._rows_by_grain[grain_id] for grain_id in validated_request.grain_ids)
        for row in rows:
            candidate = candidates[row.grain_id]
            if (
                row.player_id != candidate.player_id
                or row.competition_id != candidate.competition_id
                or row.position_code != candidate.position_code
            ):
                raise ResearchServingConflictError(
                    "comparison row identity drifts from its candidate"
                )
        draft = ResearchComparison.model_construct(
            request=validated_request,
            rows=rows,
            comparison_digest="0" * 64,
        )
        try:
            return ResearchComparison(
                request=validated_request,
                rows=rows,
                comparison_digest=canonical_research_digest(
                    draft.model_dump(mode="json", exclude={"comparison_digest"})
                ),
            )
        except ValidationError as exc:
            raise ResearchServingError("constructed comparison contract rejected") from exc

    def _vector_slice(self, active_indices: tuple[int, ...]) -> np.ndarray:
        with self._vector_slice_lock:
            cached = self._vector_slice_cache.get(active_indices)
            if cached is not None:
                self._vector_slice_cache.move_to_end(active_indices)
                return cached
        vectors = np.ascontiguousarray(
            self._index.vectors[:, list(active_indices)],
            dtype="<f8",
        )
        vectors.setflags(write=False)
        with self._vector_slice_lock:
            existing = self._vector_slice_cache.get(active_indices)
            if existing is not None:
                self._vector_slice_cache.move_to_end(active_indices)
                return existing
            self._vector_slice_cache[active_indices] = vectors
            if len(self._vector_slice_cache) > _VECTOR_SLICE_CACHE_LIMIT:
                self._vector_slice_cache.popitem(last=False)
        return vectors

    def _query_raw_values(
        self,
        request: ResearchQueryRequest,
        active_indices: tuple[int, ...],
    ) -> np.ndarray:
        if request.mode is ResearchQueryMode.WEIGHTED_PROFILE:
            values = [item.value for item in request.profile]
        else:
            if request.exemplar_grain_id is None:
                raise AssertionError("validated exemplar query lost its grain")
            row = self._rows_by_grain.get(request.exemplar_grain_id)
            if row is None:
                raise ResearchServingError("exemplar grain is absent from the pinned matrix")
            values = [cast(float, row.features[index].value) for index in active_indices]
        raw = np.ascontiguousarray(values, dtype="<f8")
        if raw.shape != (len(active_indices),) or not np.all(np.isfinite(raw)):
            raise ResearchServingError("query contains an unavailable active feature value")
        raw[raw == 0.0] = 0.0
        return raw

    def _filter_population(
        self,
        request: ResearchQueryRequest,
    ) -> tuple[np.ndarray, RetrievalPopulationCounts, int]:
        season_id = request.filters.season_id
        if season_id is None:
            raise ResearchServingError("an explicit season_id filter is required")
        admitted = np.zeros(len(self._index.catalogue), dtype=np.bool_)
        competition_rows = 0
        position_exclusions = 0
        minimum_minutes_exclusions = 0
        explicit_exclusions = 0
        exemplar_exclusions = 0
        lower_bound_count = 0
        excluded_ids = set(request.filters.excluded_player_ids)
        for index, row in enumerate(self._index.catalogue):
            if row.competition_id != request.filters.competition_id or row.season_id != season_id:
                continue
            competition_rows += 1
            if (
                request.filters.position_codes
                and row.position_code not in request.filters.position_codes
            ):
                position_exclusions += 1
            elif (
                request.filters.minimum_minutes is not None
                and row.minutes < request.filters.minimum_minutes
            ):
                minimum_minutes_exclusions += 1
            elif row.player_id in excluded_ids:
                explicit_exclusions += 1
            elif request.exemplar_grain_id == row.grain_id:
                exemplar_exclusions += 1
            else:
                admitted[index] = True
                if row.minute_state == "conservative_lower_bound":
                    lower_bound_count += 1
        scored_rows = int(np.count_nonzero(admitted))
        population = RetrievalPopulationCounts(
            matrix_rows=len(self._index.catalogue),
            competition_rows=competition_rows,
            position_exclusions=position_exclusions,
            minimum_minutes_exclusions=minimum_minutes_exclusions,
            explicit_player_exclusions=explicit_exclusions,
            exemplar_self_exclusions=exemplar_exclusions,
            filter_admitted_rows=scored_rows,
            missing_feature_exclusions=0,
            scored_rows=scored_rows,
            returned_rows=min(request.limit, scored_rows),
        )
        return admitted, population, lower_bound_count

    def _candidates(
        self,
        *,
        scored: tuple[ScoredVectorRow, ...],
        request: ResearchQueryRequest,
        active_indices: tuple[int, ...],
        query_raw: np.ndarray,
        query_scaled: np.ndarray,
        weights: np.ndarray,
    ) -> tuple[ResearchCandidate, ...]:
        candidates: list[ResearchCandidate] = []
        normalized_query_components: tuple[float, ...] | None = None
        query_is_zero = False
        weighted_values = tuple(map(float, weights))
        if request.method is ResearchMethod.WEIGHTED_COSINE:
            try:
                normalized_query_components, query_is_zero = stable_weighted_unit_components(
                    tuple(map(float, query_scaled)),
                    weighted_values,
                )
            except StableNormalizationError as exc:
                raise ResearchServingError("cosine explanation normalization failed") from exc
        for rank, scored_row in enumerate(scored, start=1):
            indexed = self._catalogue_by_key.get(scored_row.key)
            if indexed is None:
                raise ResearchServingError("scorer returned an unknown candidate identity")
            raw = np.ascontiguousarray(
                [indexed.feature_values[index] for index in active_indices],
                dtype="<f8",
            )
            scaled = np.ascontiguousarray(
                self._index.vectors[indexed.ordinal, list(active_indices)],
                dtype="<f8",
            )
            normalized_query: tuple[float, ...] | None = None
            normalized_candidate: tuple[float, ...] | None = None
            if request.method is ResearchMethod.WEIGHTED_COSINE:
                try:
                    candidate_components, candidate_zero = stable_weighted_unit_components(
                        tuple(map(float, scaled)),
                        weighted_values,
                    )
                except StableNormalizationError as exc:
                    raise ResearchServingError("cosine explanation normalization failed") from exc
                if query_is_zero or candidate_zero:
                    normalized_query = tuple(0.0 for _ in active_indices)
                    normalized_candidate = tuple(0.0 for _ in active_indices)
                else:
                    if normalized_query_components is None:
                        raise AssertionError("cosine query components were not prepared")
                    normalized_query = normalized_query_components
                    normalized_candidate = candidate_components
            contributions = tuple(
                FeatureContribution(
                    feature_name=request.weights[index].feature_name,
                    query_value=float(query_raw[index]),
                    candidate_value=float(raw[index]),
                    scaled_query_value=float(query_scaled[index]),
                    scaled_candidate_value=float(scaled[index]),
                    scaled_contrast=float(scaled[index] - query_scaled[index]),
                    weight=float(weights[index]),
                    normalized_query_component=(
                        normalized_query[index] if normalized_query is not None else None
                    ),
                    normalized_candidate_component=(
                        normalized_candidate[index] if normalized_candidate is not None else None
                    ),
                    contribution=scored_row.contributions[index],
                )
                for index in range(len(active_indices))
            )
            limitations = [
                _HISTORICAL_LIMITATION,
                _EXPERT_LIMITATION,
            ]
            if indexed.minute_state == "conservative_lower_bound":
                limitations.append(
                    "Minutes are a conservative lower bound, so eligibility evidence is weaker."
                )
            try:
                candidates.append(
                    ResearchCandidate(
                        rank=rank,
                        grain_id=indexed.grain_id,
                        player_id=indexed.player_id,
                        display_name=indexed.display_name,
                        competition_id=indexed.competition_id,
                        position_code=indexed.position_code,
                        minutes=indexed.minutes,
                        score=scored_row.distance,
                        contributions=contributions,
                        missing_features=(),
                        limitations=tuple(limitations),
                    )
                )
            except ValidationError as exc:
                raise ResearchServingError("constructed candidate contract rejected") from exc
        return tuple(candidates)


__all__ = [
    "ResearchServingConflictError",
    "ResearchServingError",
    "ResearchServingService",
]

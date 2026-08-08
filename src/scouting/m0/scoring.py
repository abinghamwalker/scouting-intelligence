"""Provider-neutral deterministic vector scoring shared by M0 and W09."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

import numpy as np

from scouting.contracts.numerics import (
    StableNormalizationError,
    stable_finite_sum,
    stable_weighted_unit_components,
)


class VectorScoringError(ValueError):
    """Raised when scoring inputs are incomplete, unsafe, or incompatible."""


class VectorScoringMethod(StrEnum):
    """Transparent baseline geometries supported by the shared scorer."""

    WEIGHTED_EUCLIDEAN = "weighted_euclidean"
    WEIGHTED_COSINE = "weighted_cosine"


@dataclass(frozen=True, slots=True)
class VectorCandidateKey:
    """Stable identity and final deterministic tie key for one matrix row."""

    player_id: UUID
    grain_id: str = ""


@dataclass(frozen=True, slots=True)
class ScoredVectorRow:
    """One score with contributions in the caller's declared feature order."""

    key: VectorCandidateKey
    distance: float
    contributions: tuple[float, ...]


def _canonical_finite_float(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise VectorScoringError("scoring produced a non-finite value")
    return 0.0 if result == 0.0 else result


def _exact_scored_row(
    *,
    query: np.ndarray,
    candidate: np.ndarray,
    key: VectorCandidateKey,
    method: VectorScoringMethod,
    weights: np.ndarray,
    normalized_query: tuple[float, ...],
    contribution_projection: np.ndarray | None,
) -> ScoredVectorRow:
    """Reconcile one selected row through the stable explanation path."""

    with np.errstate(over="ignore", invalid="ignore"):
        contrast = candidate - query
    if not np.all(np.isfinite(contrast)):
        raise VectorScoringError("feature contrast overflowed")
    if method is VectorScoringMethod.WEIGHTED_EUCLIDEAN:
        with np.errstate(over="ignore", invalid="ignore"):
            raw_contributions = weights * np.square(contrast)
        contributions = tuple(_canonical_finite_float(item) for item in raw_contributions)
        try:
            squared_distance = stable_finite_sum(contributions)
        except StableNormalizationError as exc:
            raise VectorScoringError("Euclidean contribution sum overflowed") from exc
        distance = _canonical_finite_float(np.sqrt(squared_distance))
    else:
        try:
            normalized_candidate, candidate_is_zero = stable_weighted_unit_components(
                tuple(map(float, candidate)), tuple(map(float, weights))
            )
        except StableNormalizationError as exc:
            raise VectorScoringError("candidate normalization failed") from exc
        if candidate_is_zero:
            contribution_count = (
                query.shape[0]
                if contribution_projection is None
                else contribution_projection.shape[1]
            )
            contributions = tuple(0.0 for _ in range(contribution_count))
            distance = 1.0
        else:
            terms = np.asarray(normalized_query, dtype="<f8") * np.asarray(
                normalized_candidate, dtype="<f8"
            )
            if contribution_projection is None:
                contributions = tuple(_canonical_finite_float(-item) for item in terms)
            else:
                contributions = tuple(
                    _canonical_finite_float(-item)
                    for item in np.sum(terms[:, None] * contribution_projection, axis=0)
                )
            try:
                contribution_sum = stable_finite_sum(contributions)
            except StableNormalizationError as exc:
                raise VectorScoringError("cosine contribution sum overflowed") from exc
            reconciled = _canonical_finite_float(1.0 + contribution_sum)
            if reconciled < -1e-12 or reconciled > 2.0 + 1e-12:
                raise VectorScoringError("cosine distance is outside its finite range")
            distance = 0.0 if reconciled < 0.0 else 2.0 if reconciled > 2.0 else reconciled
    return ScoredVectorRow(key=key, distance=distance, contributions=contributions)


def _bulk_cosine_distances(
    candidates: np.ndarray,
    *,
    weights: np.ndarray,
    normalized_query: tuple[float, ...],
) -> np.ndarray:
    """Return stable vectorized ranking distances for admitted candidates."""

    positive = weights > 0.0
    active = candidates[:, positive]
    active_weights = weights[positive]
    value_scale = np.max(np.abs(active), axis=1)
    zero_rows = value_scale == 0.0
    safe_value_scale = np.where(zero_rows, 1.0, value_scale)
    relative = active / safe_value_scale[:, None]
    with np.errstate(over="ignore", invalid="ignore"):
        weighted_relative = relative * np.sqrt(active_weights)[None, :]
    component_scale = np.max(np.abs(weighted_relative), axis=1)
    zero_rows |= component_scale == 0.0
    safe_component_scale = np.where(zero_rows, 1.0, component_scale)
    stable_base = weighted_relative / safe_component_scale[:, None]
    norms = np.linalg.norm(stable_base, axis=1)
    invalid = (~zero_rows) & ((norms == 0.0) | ~np.isfinite(norms))
    if np.any(invalid) or not np.all(np.isfinite(stable_base)):
        raise VectorScoringError("candidate normalization failed")
    normalized = stable_base / np.where(zero_rows, 1.0, norms)[:, None]
    query_active = np.asarray(normalized_query, dtype="<f8")[positive]
    similarities = np.einsum("ij,j->i", normalized, query_active, optimize=True)
    distances = np.ascontiguousarray(1.0 - similarities, dtype="<f8")
    distances[zero_rows] = 1.0
    if not np.all(np.isfinite(distances)):
        raise VectorScoringError("cosine population distance is non-finite")
    np.clip(distances, 0.0, 2.0, out=distances)
    distances[distances == 0.0] = 0.0
    return distances


def score_vector_rows(
    *,
    query: np.ndarray,
    candidate_vectors: np.ndarray,
    candidate_keys: tuple[VectorCandidateKey, ...],
    method: VectorScoringMethod,
    weights: np.ndarray | None = None,
    admitted: np.ndarray | None = None,
    contribution_projection: np.ndarray | None = None,
    limit: int | None = None,
    candidate_keys_validated: bool = False,
) -> tuple[ScoredVectorRow, ...]:
    """Score all admitted rows before applying a deterministic response limit."""
    if type(method) is not VectorScoringMethod:
        raise VectorScoringError("method must be an exact VectorScoringMethod")
    query_vector = np.asarray(query)
    vectors = np.asarray(candidate_vectors)
    if query_vector.dtype != np.dtype("<f8") or vectors.dtype != np.dtype("<f8"):
        raise VectorScoringError("query and candidate vectors must be little-endian float64")
    if query_vector.ndim != 1 or vectors.ndim != 2 or vectors.shape[1] != query_vector.shape[0]:
        raise VectorScoringError("query and candidate vector shapes are incompatible")
    if type(candidate_keys_validated) is not bool:
        raise VectorScoringError("candidate_keys_validated must be an exact bool")
    if vectors.shape[0] != len(candidate_keys) or (
        not candidate_keys_validated and len(set(candidate_keys)) != len(candidate_keys)
    ):
        raise VectorScoringError("candidate keys must be unique and match vector rows")
    if not np.all(np.isfinite(query_vector)) or not np.all(np.isfinite(vectors)):
        raise VectorScoringError("scoring vectors must contain only finite values")
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 1):
        raise VectorScoringError("limit must be a positive integer or None")

    feature_weights = (
        np.ones(query_vector.shape[0], dtype="<f8") if weights is None else np.asarray(weights)
    )
    if (
        feature_weights.dtype != np.dtype("<f8")
        or feature_weights.shape != query_vector.shape
        or not np.all(np.isfinite(feature_weights))
        or np.any(feature_weights < 0.0)
        or np.any(np.signbit(feature_weights) & (feature_weights == 0.0))
        or not np.any(feature_weights > 0.0)
    ):
        raise VectorScoringError("weights must be finite non-negative float64 with a positive item")

    admitted_rows = (
        np.ones(vectors.shape[0], dtype=np.bool_) if admitted is None else np.asarray(admitted)
    )
    if admitted_rows.dtype != np.dtype("bool") or admitted_rows.shape != (vectors.shape[0],):
        raise VectorScoringError("admitted mask must be one boolean per candidate")

    projection: np.ndarray | None = None
    if contribution_projection is not None:
        projection = np.asarray(contribution_projection)
        if (
            method is not VectorScoringMethod.WEIGHTED_COSINE
            or projection.dtype != np.dtype("<f8")
            or projection.ndim != 2
            or projection.shape[0] != query_vector.shape[0]
            or not np.all(np.isfinite(projection))
        ):
            raise VectorScoringError("contribution projection is incompatible")

    normalized_query: tuple[float, ...] = ()
    if method is VectorScoringMethod.WEIGHTED_COSINE:
        try:
            normalized_query, query_is_zero = stable_weighted_unit_components(
                tuple(map(float, query_vector)), tuple(map(float, feature_weights))
            )
        except StableNormalizationError as exc:
            raise VectorScoringError("query normalization failed") from exc
        if query_is_zero:
            raise VectorScoringError("cosine query vector has zero weighted norm")

    admitted_indices = np.flatnonzero(admitted_rows)
    if admitted_indices.size == 0:
        return ()
    admitted_vectors = vectors[admitted_indices]
    with np.errstate(over="ignore", invalid="ignore"):
        population_contrasts = admitted_vectors - query_vector
    if not np.all(np.isfinite(population_contrasts)):
        raise VectorScoringError("feature contrast overflowed")
    if method is VectorScoringMethod.WEIGHTED_EUCLIDEAN:
        with np.errstate(over="ignore", invalid="ignore"):
            squared_distances = np.einsum(
                "ij,j,ij->i",
                population_contrasts,
                feature_weights,
                population_contrasts,
                optimize=True,
            )
        if np.any(~np.isfinite(squared_distances)):
            for local_index in np.flatnonzero(~np.isfinite(squared_distances)):
                source_index = int(admitted_indices[local_index])
                _exact_scored_row(
                    query=query_vector,
                    candidate=vectors[source_index],
                    key=candidate_keys[source_index],
                    method=method,
                    weights=feature_weights,
                    normalized_query=normalized_query,
                    contribution_projection=projection,
                )
            raise VectorScoringError("Euclidean population distance is non-finite")
        population_distances = np.sqrt(squared_distances)
    else:
        population_distances = _bulk_cosine_distances(
            admitted_vectors,
            weights=feature_weights,
            normalized_query=normalized_query,
        )
    local_order = sorted(
        range(len(admitted_indices)),
        key=lambda local_index: (
            float(population_distances[local_index]),
            candidate_keys[int(admitted_indices[local_index])].player_id.bytes,
            candidate_keys[int(admitted_indices[local_index])].grain_id,
        ),
    )
    if limit is not None:
        local_order = local_order[:limit]
    rows = [
        _exact_scored_row(
            query=query_vector,
            candidate=vectors[source_index],
            key=candidate_keys[source_index],
            method=method,
            weights=feature_weights,
            normalized_query=normalized_query,
            contribution_projection=projection,
        )
        for local_index in local_order
        for source_index in (int(admitted_indices[local_index]),)
    ]
    return tuple(
        sorted(
            rows,
            key=lambda row: (row.distance, row.key.player_id.bytes, row.key.grain_id),
        )
    )


__all__ = [
    "ScoredVectorRow",
    "VectorCandidateKey",
    "VectorScoringError",
    "VectorScoringMethod",
    "score_vector_rows",
]

"""Stable numeric primitives shared by strict contracts and runtime scoring."""

from __future__ import annotations

import math
import sys
from collections.abc import Sequence


class StableNormalizationError(ValueError):
    """Weighted vector normalization is outside the supported finite domain."""


def stable_finite_sum(values: Sequence[float]) -> float:
    """Sum finite terms while translating aggregate overflow to a controlled error."""

    try:
        result = math.fsum(float(value) for value in values)
    except OverflowError as exc:
        raise StableNormalizationError("finite terms overflowed during summation") from exc
    if not math.isfinite(result):
        raise StableNormalizationError("summation result is not finite")
    return 0.0 if result == 0.0 else result


def stable_weighted_unit_components(
    values: Sequence[float],
    weights: Sequence[float],
) -> tuple[tuple[float, ...], bool]:
    """Return scale-invariant weighted unit components and a zero-vector flag.

    The ordinary path intentionally retains the direct float64 arithmetic used by the
    accepted W05 scorer. A rescaled path is selected only when multiplication overflows
    or the rounded direct components do not form a unit vector, including subnormals.
    """

    if len(values) != len(weights) or not values:
        raise StableNormalizationError("values and weights must have equal positive length")
    numeric_values = tuple(float(value) for value in values)
    numeric_weights = tuple(float(weight) for weight in weights)
    if not all(math.isfinite(value) for value in numeric_values):
        raise StableNormalizationError("normalization values must be finite")
    if not all(math.isfinite(weight) and weight >= 0.0 for weight in numeric_weights):
        raise StableNormalizationError("normalization weights must be finite and non-negative")
    if not any(weight > 0.0 for weight in numeric_weights):
        raise StableNormalizationError("normalization requires a positive weight")

    square_roots = tuple(math.sqrt(weight) for weight in numeric_weights)
    direct = tuple(root * value for root, value in zip(square_roots, numeric_values, strict=True))
    if all(math.isfinite(component) for component in direct):
        direct_norm = math.hypot(*direct)
        if math.isfinite(direct_norm) and direct_norm >= sys.float_info.min:
            normalized = tuple(component / direct_norm for component in direct)
            squared_norm = math.fsum(component * component for component in normalized)
            if math.isfinite(squared_norm) and math.isclose(
                squared_norm, 1.0, rel_tol=1e-12, abs_tol=1e-12
            ):
                return tuple(0.0 if value == 0.0 else value for value in normalized), False
        elif direct_norm == 0.0 and not any(numeric_values):
            return tuple(0.0 for _ in numeric_values), True

    value_scale = max(
        abs(value)
        for value, weight in zip(numeric_values, numeric_weights, strict=True)
        if weight > 0.0
    )
    if value_scale == 0.0:
        return tuple(0.0 for _ in numeric_values), True
    relative_values = tuple(
        0.0 if weight == 0.0 else value / value_scale
        for value, weight in zip(numeric_values, numeric_weights, strict=True)
    )
    weighted_relative = tuple(
        root * value for root, value in zip(square_roots, relative_values, strict=True)
    )
    if not all(math.isfinite(component) for component in weighted_relative):
        raise StableNormalizationError("weighted normalization components overflowed")
    component_scale = max(abs(component) for component in weighted_relative)
    if component_scale == 0.0:
        return tuple(0.0 for _ in numeric_values), True
    stable_base = tuple(component / component_scale for component in weighted_relative)
    stable_norm = math.hypot(*stable_base)
    if not math.isfinite(stable_norm) or stable_norm == 0.0:
        raise StableNormalizationError("weighted normalization norm is invalid")
    normalized = tuple(component / stable_norm for component in stable_base)
    squared_norm = math.fsum(component * component for component in normalized)
    if not math.isfinite(squared_norm) or not math.isclose(
        squared_norm, 1.0, rel_tol=1e-12, abs_tol=1e-12
    ):
        raise StableNormalizationError("weighted normalized components do not form a unit vector")
    return tuple(0.0 if value == 0.0 else value for value in normalized), False


__all__ = [
    "StableNormalizationError",
    "stable_finite_sum",
    "stable_weighted_unit_components",
]

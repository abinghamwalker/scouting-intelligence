from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from scouting.contracts.research import ResearchMethod
from scouting.modeling.research import (
    DEFAULT_MODEL_CONFIG_PATH,
    ResearchIndexBuildError,
    fit_robust_scaler,
    load_model_configuration,
)


def test_model_configuration_declares_only_transparent_exhaustive_baselines() -> None:
    configuration = load_model_configuration(DEFAULT_MODEL_CONFIG_PATH)

    assert configuration.methods == (
        ResearchMethod.WEIGHTED_EUCLIDEAN,
        ResearchMethod.WEIGHTED_COSINE,
    )
    assert configuration.full_population_scoring is True
    assert configuration.pre_limit is False
    assert configuration.approximate_nearest_neighbour is False
    assert configuration.constant_feature_policy == "retain_with_unit_scale"


def test_model_configuration_digest_rejects_semantic_drift(tmp_path: Path) -> None:
    payload = DEFAULT_MODEL_CONFIG_PATH.read_text()
    path = tmp_path / "configuration.json"
    path.write_text(payload.replace('"median"', '"not-median"'))

    with pytest.raises(ResearchIndexBuildError, match="configuration"):
        load_model_configuration(path)


def test_median_iqr_scaling_retains_constant_features_with_unit_scale() -> None:
    matrix = np.array([[1.0, 5.0], [2.0, 5.0], [100.0, 5.0]], dtype="<f8", order="C")

    fitted = fit_robust_scaler(matrix)

    assert fitted.center == pytest.approx(np.array([2.0, 5.0], dtype="<f8"))
    assert fitted.scale == pytest.approx(np.array([49.5, 1.0], dtype="<f8"))
    assert fitted.vectors.shape == matrix.shape
    assert fitted.vectors[:, 1] == pytest.approx(np.zeros(3))
    assert fitted.center.dtype.str == "<f8"
    assert fitted.scale.dtype.str == "<f8"
    assert fitted.vectors.dtype.str == "<f8"
    assert not fitted.center.flags.writeable
    assert not fitted.scale.flags.writeable
    assert not fitted.vectors.flags.writeable


@pytest.mark.parametrize(
    "matrix",
    (
        np.array([[1.0, float("nan")]], dtype="<f8"),
        np.array([[1.0, 2.0]], dtype=">f8"),
        np.array([], dtype="<f8").reshape(0, 2),
        np.asfortranarray(np.array([[1.0, 2.0], [3.0, 4.0]], dtype="<f8")),
    ),
)
def test_scaler_rejects_incomplete_dtype_or_order_drift(matrix: np.ndarray) -> None:
    with pytest.raises(ResearchIndexBuildError, match="little-endian|complete"):
        fit_robust_scaler(matrix)


def test_scaler_never_samples_or_discards_rows() -> None:
    matrix = np.arange(34.0, dtype="<f8").reshape(17, 2)

    fitted = fit_robust_scaler(matrix)

    assert fitted.vectors.shape[0] == 17
    reconstructed = fitted.vectors * fitted.scale + fitted.center
    assert reconstructed == pytest.approx(matrix)

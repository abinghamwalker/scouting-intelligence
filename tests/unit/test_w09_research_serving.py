from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

from scouting.contracts.research import (
    ResearchVersionPins,
)
from scouting.serving.research import (
    ResearchServingError,
    _deduplicated,
    _fresh_model,
    _validated_array,
)


def _pins() -> ResearchVersionPins:
    return ResearchVersionPins(
        feature_cutoff_ts=datetime(2026, 8, 1, tzinfo=UTC),
        dataset_version="dataset-v1",
        dataset_manifest_digest="1" * 64,
        identity_bundle_digest="2" * 64,
        canonical_build_digest="3" * 64,
        matrix_version="matrix-v1",
        matrix_manifest_digest="4" * 64,
        matrix_digest="5" * 64,
        feature_registry_version="registry-v1",
        feature_registry_digest="6" * 64,
        eligibility_policy_version="eligibility-v1",
        eligibility_policy_digest="7" * 64,
        model_version="model-v1",
        model_configuration_digest="8" * 64,
        scorer_version="scorer-v1",
        scorer_code_digest="9" * 64,
        index_version="index-v1",
        index_manifest_digest="a" * 64,
        catalogue_digest="b" * 64,
    )


def test_fresh_model_revalidates_and_rejects_inexact_contract_types() -> None:
    pins = _pins()

    assert _fresh_model(pins, ResearchVersionPins, label="pins") == pins
    with pytest.raises(TypeError, match="exact ResearchVersionPins"):
        _fresh_model(object(), ResearchVersionPins, label="pins")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "mutate, match",
    (
        (lambda value: value.setflags(write=True), "read-only"),
        (lambda value: value.__setitem__(0, float("nan")), "finite read-only"),
        (lambda value: value.__setitem__(0, -0.0), "finite read-only"),
    ),
)
def test_array_authority_fails_closed_on_mutability_and_noncanonical_values(
    mutate: object,
    match: str,
) -> None:
    array = np.array([1.0, 2.0], dtype="<f8")
    array.setflags(write=False)
    if match != "read-only":
        array.setflags(write=True)
    mutate(array)  # type: ignore[operator]
    if match != "read-only":
        array.setflags(write=False)

    with pytest.raises(ResearchServingError, match=match):
        _validated_array(array, label="fixture", shape=(2,))


def test_array_authority_accepts_only_exact_read_only_canonical_shape() -> None:
    array = np.array([5e-324, 0.0], dtype="<f8")
    array.setflags(write=False)

    private = _validated_array(array, label="fixture", shape=(2,))
    assert private is not array
    assert np.array_equal(private, array)
    with pytest.raises(ValueError, match="WRITEABLE"):
        private.setflags(write=True)
    with pytest.raises(ResearchServingError, match="finite read-only"):
        _validated_array(array, label="fixture", shape=(1, 2))


def test_warning_deduplication_preserves_first_seen_order() -> None:
    assert _deduplicated(("historical", "missing", "historical", "expert")) == (
        "historical",
        "missing",
        "expert",
    )


def test_research_serving_does_not_reach_dormant_or_builder_paths() -> None:
    source = (Path(__file__).resolve().parents[2] / "src/scouting/serving/research.py").read_text(
        encoding="utf-8"
    )

    for forbidden in (
        "scouting.serving.synthetic",
        "scouting.serving.m0",
        "scouting.web.w07",
        "scouting.web.w08",
        "build_research_index(",
        "load_research_index(",
        "load_feature_matrix(",
    ):
        assert forbidden not in source

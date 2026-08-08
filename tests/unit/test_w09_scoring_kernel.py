"""Provider-neutral parity and explanation tests for the shared W09 scorer."""

from __future__ import annotations

from uuid import UUID

import numpy as np
import pytest

import scouting.m0.scoring as scoring_kernel
from scouting.contracts.research import FeatureContribution
from scouting.m0.scoring import (
    VectorCandidateKey,
    VectorScoringError,
    VectorScoringMethod,
    score_vector_rows,
)


def _keys() -> tuple[VectorCandidateKey, ...]:
    return (
        VectorCandidateKey(UUID("20000000-0000-4000-8000-000000000002"), "b"),
        VectorCandidateKey(UUID("20000000-0000-4000-8000-000000000001"), "a"),
        VectorCandidateKey(UUID("20000000-0000-4000-8000-000000000001"), "b"),
    )


def test_weighted_euclidean_contributions_reconcile_and_limit_after_admission() -> None:
    rows = score_vector_rows(
        query=np.array([0.0, 0.0], dtype="<f8"),
        candidate_vectors=np.array([[1.0, 2.0], [1.0, 2.0], [9.0, 9.0]], dtype="<f8"),
        candidate_keys=_keys(),
        method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
        weights=np.array([4.0, 1.0], dtype="<f8"),
        admitted=np.array([True, True, False], dtype=np.bool_),
        limit=1,
    )
    assert len(rows) == 1
    assert rows[0].key == _keys()[1]
    assert rows[0].contributions == (4.0, 4.0)
    assert rows[0].distance ** 2 == pytest.approx(sum(rows[0].contributions))


def test_weighted_cosine_signed_terms_reconcile_and_ties_use_full_key() -> None:
    rows = score_vector_rows(
        query=np.array([1.0, 1.0], dtype="<f8"),
        candidate_vectors=np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]], dtype="<f8"),
        candidate_keys=_keys(),
        method=VectorScoringMethod.WEIGHTED_COSINE,
        weights=np.array([2.0, 1.0], dtype="<f8"),
    )
    assert [row.key for row in rows] == [_keys()[1], _keys()[2], _keys()[0]]
    for row in rows:
        assert row.distance == pytest.approx(1.0 + sum(row.contributions))
        assert len(row.contributions) == 2
        assert not any(value == 0.0 and np.signbit(value) for value in row.contributions)


def test_kernel_rejects_nonfinite_vectors_and_invalid_weights() -> None:
    query = np.array([0.0, 1.0], dtype="<f8")
    vectors = np.array([[1.0, 2.0]], dtype="<f8")
    keys = (_keys()[0],)
    with pytest.raises(VectorScoringError, match="positive"):
        score_vector_rows(
            query=query,
            candidate_vectors=vectors,
            candidate_keys=keys,
            method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
            weights=np.array([0.0, 0.0], dtype="<f8"),
        )
    with pytest.raises(VectorScoringError, match="finite"):
        score_vector_rows(
            query=np.array([float("nan"), 1.0], dtype="<f8"),
            candidate_vectors=vectors,
            candidate_keys=keys,
            method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
        )
    with pytest.raises(VectorScoringError, match="exact VectorScoringMethod"):
        score_vector_rows(
            query=query,
            candidate_vectors=vectors,
            candidate_keys=keys,
            method="not_a_method",  # type: ignore[arg-type]
        )
    with pytest.raises(VectorScoringError, match="weights"):
        score_vector_rows(
            query=query,
            candidate_vectors=vectors,
            candidate_keys=keys,
            method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
            weights=np.array([-0.0, 1.0], dtype="<f8"),
        )
    with pytest.raises(VectorScoringError, match="unique"):
        score_vector_rows(
            query=query,
            candidate_vectors=np.array([[1.0, 2.0], [2.0, 3.0]], dtype="<f8"),
            candidate_keys=(keys[0], keys[0]),
            method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
        )
    with pytest.raises(VectorScoringError, match="exact bool"):
        score_vector_rows(
            query=query,
            candidate_vectors=vectors,
            candidate_keys=keys,
            method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
            candidate_keys_validated=1,  # type: ignore[arg-type]
        )


def test_zero_norm_cosine_query_fails_closed() -> None:
    with pytest.raises(VectorScoringError, match="zero weighted norm"):
        score_vector_rows(
            query=np.zeros(2, dtype="<f8"),
            candidate_vectors=np.array([[1.0, 2.0]], dtype="<f8"),
            candidate_keys=(_keys()[0],),
            method=VectorScoringMethod.WEIGHTED_COSINE,
        )


def test_cosine_stable_normalization_is_reserved_for_returned_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = scoring_kernel.stable_weighted_unit_components
    calls = 0

    def counted(
        values: tuple[float, ...],
        weights: tuple[float, ...],
    ) -> tuple[tuple[float, ...], bool]:
        nonlocal calls
        calls += 1
        return original(values, weights)

    monkeypatch.setattr(scoring_kernel, "stable_weighted_unit_components", counted)
    candidates = np.arange(2, 202, dtype="<f8").reshape(100, 2)
    keys = tuple(VectorCandidateKey(UUID(int=index + 1), str(index)) for index in range(100))
    rows = score_vector_rows(
        query=np.array([1.0, 1.0], dtype="<f8"),
        candidate_vectors=candidates,
        candidate_keys=keys,
        method=VectorScoringMethod.WEIGHTED_COSINE,
        limit=2,
        candidate_keys_validated=True,
    )

    assert len(rows) == 2
    assert calls == 3


def test_kernel_zero_terms_round_trip_through_strict_contribution_contract() -> None:
    rows = score_vector_rows(
        query=np.array([1.0, 1.0], dtype="<f8"),
        candidate_vectors=np.array([[1.0, 0.0]], dtype="<f8"),
        candidate_keys=(_keys()[0],),
        method=VectorScoringMethod.WEIGHTED_COSINE,
        weights=np.array([1.0, 1.0], dtype="<f8"),
    )
    for index, contribution in enumerate(rows[0].contributions):
        FeatureContribution(
            feature_name=f"feature_{index}",
            query_value=1.0,
            candidate_value=float(index == 0),
            scaled_query_value=1.0,
            scaled_candidate_value=float(index == 0),
            scaled_contrast=float(index == 0) - 1.0,
            weight=1.0,
            normalized_query_component=2**-0.5,
            normalized_candidate_component=float(index == 0),
            contribution=contribution,
        )


def test_kernel_uses_overflow_stable_cosine_norms_and_rejects_euclidean_overflow() -> None:
    key = (_keys()[0],)
    cosine = score_vector_rows(
        query=np.array([1e308, 1e308], dtype="<f8"),
        candidate_vectors=np.array([[1.0, 1.0]], dtype="<f8"),
        candidate_keys=key,
        method=VectorScoringMethod.WEIGHTED_COSINE,
    )
    assert cosine[0].distance == pytest.approx(0.0, abs=1e-15)
    assert cosine[0].contributions == pytest.approx((-0.5, -0.5))

    with pytest.raises(VectorScoringError, match="contrast overflowed"):
        score_vector_rows(
            query=np.array([1e308, 0.0], dtype="<f8"),
            candidate_vectors=np.array([[-1e308, 0.0]], dtype="<f8"),
            candidate_keys=key,
            method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
        )
    with pytest.raises(VectorScoringError, match="contrast overflowed"):
        score_vector_rows(
            query=np.array([1e308, 1e308], dtype="<f8"),
            candidate_vectors=np.array([[-1e308, -1e308]], dtype="<f8"),
            candidate_keys=key,
            method=VectorScoringMethod.WEIGHTED_COSINE,
        )


@pytest.mark.parametrize(
    "magnitude",
    (5e-324, 1e-323, 5e-323, 1e-322, 1e-320, 1e-310, 1e-308, 1e-307),
)
def test_cosine_subnormal_scale_is_invariant_and_explanations_reconcile(
    magnitude: float,
) -> None:
    rows = score_vector_rows(
        query=np.array([magnitude, magnitude], dtype="<f8"),
        candidate_vectors=np.array([[1.0, 1.0]], dtype="<f8"),
        candidate_keys=(_keys()[0],),
        method=VectorScoringMethod.WEIGHTED_COSINE,
    )
    assert rows[0].distance == pytest.approx(0.0, abs=1e-15)
    assert 1.0 + sum(rows[0].contributions) == pytest.approx(rows[0].distance, abs=1e-15)


def test_zero_weight_extreme_dimension_cannot_hide_an_active_subnormal_direction() -> None:
    rows = score_vector_rows(
        query=np.array([1e308, 1e-308], dtype="<f8"),
        candidate_vectors=np.array([[0.0, 1.0]], dtype="<f8"),
        candidate_keys=(_keys()[0],),
        method=VectorScoringMethod.WEIGHTED_COSINE,
        weights=np.array([0.0, 1.0], dtype="<f8"),
    )
    assert rows[0].distance == pytest.approx(0.0, abs=1e-15)
    assert rows[0].contributions == (0.0, -1.0)
    assert 1.0 + sum(rows[0].contributions) == rows[0].distance


def test_euclidean_finite_terms_that_overflow_the_aggregate_fail_closed() -> None:
    with pytest.raises(VectorScoringError, match="contribution sum overflowed"):
        score_vector_rows(
            query=np.array([0.0, 0.0], dtype="<f8"),
            candidate_vectors=np.array([[1e154, 1e154]], dtype="<f8"),
            candidate_keys=(_keys()[0],),
            method=VectorScoringMethod.WEIGHTED_EUCLIDEAN,
        )

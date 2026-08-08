from __future__ import annotations

from pathlib import Path

import pytest

from scouting.contracts.research import MinuteEvidenceState
from scouting.features.historical import (
    DEFAULT_REGISTRY_PATH,
    HistoricalFeatureBuildError,
    aggregate_governed_minutes,
    feature_numerators,
    load_historical_feature_registry,
)


def _action(
    *, event_id: int, sub_event_id: int | None = None, tags: list[int] | None = None
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "sub_event_id": sub_event_id,
        "tag_ids": tags or [],
        "coordinate_evidence_state": "invalid_out_of_range",
    }


def test_fixed_registry_has_exact_order_and_predicates() -> None:
    registry = load_historical_feature_registry()
    assert tuple(item.name for item in registry.features) == (
        "passes_per90",
        "accurate_passes_per90",
        "crosses_per90",
        "smart_passes_per90",
        "shots_per90",
        "shots_on_target_per90",
        "goals_per90",
        "key_passes_per90",
        "assists_per90",
        "duels_per90",
        "duels_won_per90",
        "interceptions_per90",
        "clearances_per90",
        "accelerations_per90",
        "fouls_per90",
        "touches_per90",
    )
    numerators = feature_numerators(
        (
            _action(event_id=8, tags=[1801, 302]),
            _action(event_id=8, sub_event_id=80),
            _action(event_id=10, tags=[101, 1801]),
            _action(event_id=10, tags=[101, 102]),
            _action(event_id=9, sub_event_id=90, tags=[101]),
            _action(event_id=3, sub_event_id=35, tags=[101]),
            _action(event_id=1, tags=[703, 1401]),
            _action(event_id=2, sub_event_id=72, tags=[301]),
            _action(event_id=7, sub_event_id=70),
            _action(event_id=7, sub_event_id=71),
        ),
        registry,
    )
    assert numerators == (2, 1, 1, 0, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1)


def test_zero_numerators_are_observed_counts_not_coordinate_missingness() -> None:
    registry = load_historical_feature_registry()
    assert feature_numerators((_action(event_id=99),), registry) == (0,) * 16


def test_governed_minutes_preserve_exact_lower_bound_and_unused_bench() -> None:
    exact = {"minute_state": "exact", "minutes": 300.0}
    lower = {"minute_state": "conservative_lower_bound", "minutes": 150.0}
    unused = {"minute_state": "unusable", "minutes": None}
    assert aggregate_governed_minutes((exact, unused)) == (
        MinuteEvidenceState.EXACT,
        300.0,
        1,
    )
    assert aggregate_governed_minutes((exact, lower, unused)) == (
        MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND,
        450.0,
        2,
    )
    assert aggregate_governed_minutes((unused,)) == (MinuteEvidenceState.UNUSABLE, None, 0)
    assert aggregate_governed_minutes(
        ({"minute_state": "conservative_lower_bound", "minutes": 0.0},)
    ) == (MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND, 0.0, 1)


def test_registry_rejects_policy_drift_before_feature_work(tmp_path: Path) -> None:
    payload = DEFAULT_REGISTRY_PATH.read_text()
    bad_path = tmp_path / "registry.json"
    bad_path.write_text(payload.replace('"minimum_minutes": 450.0', '"minimum_minutes": 449.0'))
    with pytest.raises(HistoricalFeatureBuildError, match="policy is incompatible"):
        load_historical_feature_registry(bad_path)

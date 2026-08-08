"""Public R3 embedded-input contract regressions."""

import pytest
from pydantic import ValidationError

from scouting.contracts.evaluation import (
    DeficitKind,
    PopulationDeficit,
    RankedObservation,
    RelevanceLabel,
    _digest,
)


def make(cls: object, payload: dict[str, object], name: str) -> object:
    draft = cls.model_construct(**payload)  # type: ignore[union-attr]
    payload[name] = _digest(draft.model_dump(mode="json"), name)  # type: ignore[union-attr]
    return cls(**payload)  # type: ignore[operator]


def test_ranked_observations_are_complete_score_ordered_embedded_evidence() -> None:
    observation = make(
        RankedObservation,
        {
            "row_id": "row",
            "query_id": "query",
            "candidate_ids": ("beta", "alpha"),
            "scores": (2.0, 1.0),
            "labels": (RelevanceLabel.IRRELEVANT, RelevanceLabel.RELEVANT),
        },
        "ranking_digest",
    )
    assert observation.ranking_digest
    with pytest.raises(ValidationError, match="score-desc"):
        make(
            RankedObservation,
            {
                "row_id": "bad",
                "query_id": "query",
                "candidate_ids": ("alpha", "beta"),
                "scores": (1.0, 2.0),
                "labels": (RelevanceLabel.RELEVANT, RelevanceLabel.IRRELEVANT),
            },
            "ranking_digest",
        )


def test_typed_deficits_cannot_be_caller_asserted_when_population_is_sufficient() -> None:
    with pytest.raises(ValidationError, match="unmet"):
        make(
            PopulationDeficit,
            {
                "kind": DeficitKind.PER_UNIT_OBSERVATIONS,
                "scope": "query",
                "observed": 4,
                "required": 4,
            },
            "deficit_digest",
        )

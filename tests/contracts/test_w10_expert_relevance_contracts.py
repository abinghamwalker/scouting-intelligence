"""W10 protocol, query-freeze and participant-safe projection contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scouting.contracts.expert_relevance import (  # noqa: E402
    CandidateOrigin,
    EvidenceBand,
    ExpertRelevanceProtocol,
    ExpertStudyPresentationBundle,
    FrozenExpertQueryPack,
    QueryDifficulty,
)
from scouting.contracts.research import canonical_research_digest  # noqa: E402
from scripts.build_w10_expert_protocol import build_w10_authority  # noqa: E402
from services.api.w09_main import load_production_w09_runtime  # noqa: E402

_PROTOCOL = _ROOT / "configs/evaluation/w10-expert-relevance-protocol-v1.json"
_QUERY_PACK = _ROOT / "configs/evaluation/w10-frozen-query-pack-v1.json"
_PRESENTATION = _ROOT / "configs/evaluation/w10-expert-study-presentation-v1.json"
_FORBIDDEN_PARTICIPANT_KEYS = {
    "control_match_rule",
    "control_rank",
    "difficulty",
    "evidence_band",
    "exemplar_competition_id",
    "exemplar_grain_id",
    "exemplar_player_id",
    "exemplar_season_id",
    "grain_id",
    "origin",
    "player_id",
    "retrieval_rank",
    "retrieval_score",
    "w09_generated_at",
    "w09_request_digest",
    "w09_result_digest",
    "w09_result_id",
}


def _payload(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_bytes()))


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in _all_keys(child)}
    if isinstance(value, list):
        return {key for child in value for key in _all_keys(child)}
    return set()


def test_frozen_protocol_and_query_pack_parse_with_exact_balanced_authority() -> None:
    protocol = ExpertRelevanceProtocol.model_validate_json(_PROTOCOL.read_bytes())
    query_pack = FrozenExpertQueryPack.model_validate_json(_QUERY_PACK.read_bytes())

    protocol.w09_pins.assert_compatible(query_pack.w09_pins)
    assert len(query_pack.queries) == 8
    assert {query.exemplar_position_code for query in query_pack.queries} == {
        "GK",
        "DF",
        "MD",
        "FW",
    }
    assert {query.evidence_band for query in query_pack.queries} == set(EvidenceBand)
    assert {query.difficulty for query in query_pack.queries} == set(QueryDifficulty)
    assert len({query.exemplar_competition_id for query in query_pack.queries}) == 5
    assert (
        sum(
            candidate.origin is CandidateOrigin.RETRIEVED
            for query in query_pack.queries
            for candidate in query.candidates
        )
        == 40
    )
    assert (
        sum(
            candidate.origin is CandidateOrigin.CONTROL
            for query in query_pack.queries
            for candidate in query.candidates
        )
        == 40
    )


def test_control_evidence_bands_are_paired_to_retrieved_ranks() -> None:
    query_pack = FrozenExpertQueryPack.model_validate_json(_QUERY_PACK.read_bytes())
    boundary = 1_800.0

    for query in query_pack.queries:
        retrieved = {
            candidate.retrieval_rank: candidate
            for candidate in query.candidates
            if candidate.origin is CandidateOrigin.RETRIEVED
        }
        controls = {
            candidate.control_rank: candidate
            for candidate in query.candidates
            if candidate.origin is CandidateOrigin.CONTROL
        }
        assert set(retrieved) == set(controls) == {1, 2, 3, 4, 5}
        assert all(
            (retrieved[rank].minutes >= boundary) == (controls[rank].minutes >= boundary)
            for rank in retrieved
        )


def test_builder_does_not_conflate_superseded_v1_with_current_w09() -> None:
    _, service = load_production_w09_runtime()
    protocol, query_pack, presentation = build_w10_authority(service)
    historical_protocol = ExpertRelevanceProtocol.model_validate_json(_PROTOCOL.read_bytes())
    historical_query_pack = FrozenExpertQueryPack.model_validate_json(_QUERY_PACK.read_bytes())
    historical_presentation = ExpertStudyPresentationBundle.model_validate_json(
        _PRESENTATION.read_bytes()
    )

    assert protocol.w09_pins == query_pack.w09_pins == service.pins
    assert historical_protocol.w09_pins == historical_query_pack.w09_pins
    assert historical_protocol.w09_pins != service.pins
    assert protocol != historical_protocol
    assert query_pack != historical_query_pack
    assert presentation != historical_presentation


def test_participant_bundle_is_physically_separate_and_contains_no_protected_keys() -> None:
    query_pack = FrozenExpertQueryPack.model_validate_json(_QUERY_PACK.read_bytes())
    presentation = ExpertStudyPresentationBundle.model_validate_json(_PRESENTATION.read_bytes())
    payload = _payload(_PRESENTATION)

    assert presentation.query_pack_digest == query_pack.query_pack_digest
    assert presentation.repeat_anchor_candidate_ids == query_pack.repeat_anchor_candidate_ids
    assert _all_keys(payload).isdisjoint(_FORBIDDEN_PARTICIPANT_KEYS)
    protected_ids = {
        candidate.candidate_id for query in query_pack.queries for candidate in query.candidates
    }
    presented_ids = {
        candidate.candidate_id for query in presentation.queries for candidate in query.candidates
    }
    assert presented_ids == protected_ids


def test_w09_result_authority_substitution_invalidates_nested_query_digest() -> None:
    payload = _payload(_QUERY_PACK)
    payload["queries"][0]["w09_result_digest"] = "f" * 64

    with pytest.raises(ValidationError, match="query digest"):
        FrozenExpertQueryPack.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize(
    ("path", "model_type", "field", "replacement"),
    (
        (_PROTOCOL, ExpertRelevanceProtocol, "title", "mutated protocol title"),
        (_QUERY_PACK, FrozenExpertQueryPack, "query_selection_rule", "mutated query rule"),
        (_PRESENTATION, ExpertStudyPresentationBundle, "query_order_rule", "mutated order"),
    ),
)
def test_decision_bearing_mutation_changes_digest_and_stale_digest_is_rejected(
    path: Path,
    model_type: type[Any],
    field: str,
    replacement: str,
) -> None:
    payload = _payload(path)
    if model_type is ExpertRelevanceProtocol:
        digest_field = "protocol_digest"
    elif model_type is FrozenExpertQueryPack:
        digest_field = "query_pack_digest"
    else:
        digest_field = "presentation_digest"
    prior_digest = payload[digest_field]
    payload[field] = replacement

    projection = {key: value for key, value in payload.items() if key != digest_field}
    assert canonical_research_digest(projection) != prior_digest
    with pytest.raises(ValidationError, match="digest"):
        model_type.model_validate_json(json.dumps(payload))

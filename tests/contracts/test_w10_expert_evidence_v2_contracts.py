"""Contract boundaries for W10 participant evidence and v2 responses."""

from __future__ import annotations

import inspect
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from scouting.contracts import expert_relevance
from scouting.contracts.expert_relevance import (
    AssessmentBasisV2,
    CandidateEvidenceJudgementV2,
    EvidenceCoverageV2,
    EvidenceFamilyV2,
    EvidenceGapV2,
    EvidenceGlossaryEntryV2,
    EvidenceMetricV2,
    EvidenceOpportunityComponentV2,
    EvidencePlayerContextV2,
    EvidenceQuantityV2,
    EvidenceSufficiencyV2,
    ExpertEvidencePolicyV2,
    ExpertStudyPresentationBundle,
    JudgementState,
    ParticipantExpertEvidenceBundleV2,
    UnsupportedInferenceV2,
    participant_keyed_candidate_order,
)
from scouting.contracts.research import canonical_research_digest
from scouting.storage.formats import canonical_json_bytes

_ROOT = Path(__file__).resolve().parents[2]
_POLICY = _ROOT / "configs/evaluation/w10-expert-evidence-presentation-v2.json"
_V1_PRESENTATION = _ROOT / "configs/evaluation/w10-expert-study-presentation-v1.json"
_V2_PARTICIPANT_TEMPLATE = _ROOT / "apps/web/templates/w10_expert_study/v2_legacy_participant.html"
_FIXED_SYNTHETIC_PARTICIPANT_DIGESTS = tuple(f"{value:064x}" for value in range(1, 201))
_FIXED_SYNTHETIC_CANDIDATE_IDS = tuple(
    UUID(f"00000000-0000-0000-0000-{value:012d}") for value in range(1, 11)
)
_V2_EVIDENCE_FIELD_VISIBILITY: dict[type[Any], dict[str, frozenset[str]]] = {
    ParticipantExpertEvidenceBundleV2: {
        "rendered": frozenset(
            {
                "context",
                "w09_inputs",
                "independent_descriptors",
                "unsupported_inferences",
                "glossary",
            }
        ),
        "internal": frozenset(
            {
                "schema_version",
                "evidence_version",
                "policy_digest",
                "canonical_build_id",
                "matrix_version",
                "matrix_digest",
                "md_subrubric",
                "bundle_digest",
                "claim_boundary",
            }
        ),
    },
    EvidencePlayerContextV2: {
        "rendered": frozenset(
            {
                "display_name",
                "competition_name",
                "season_label",
                "position_code",
                "team_names",
                "quantity",
            }
        ),
        "internal": frozenset({"window_start_utc", "window_end_utc"}),
    },
    EvidenceQuantityV2: {
        "rendered": frozenset({"governed_minutes", "minute_state"}),
        "internal": frozenset(
            {
                "evidence_class",
                "match_count",
                "retained_action_count",
                "lineup_match_coverage",
                "action_match_coverage",
                "coordinate_coverage",
                "limitation",
            }
        ),
    },
    EvidenceCoverageV2: {
        "rendered": frozenset({"definition"}),
        "internal": frozenset({"observed", "expected", "proportion"}),
    },
    EvidenceFamilyV2: {
        "rendered": frozenset(
            {"label", "definition", "availability", "mandatory_for_selected_rubric", "metrics"}
        ),
        "internal": frozenset(
            {
                "family_id",
                "purpose",
                "used_by_w09_ranking",
                "exact_family_predicate",
                "raw_opportunity_denominator",
                "opportunity_floor",
                "opportunity_components",
                "threshold_policy_version",
                "threshold_rationale",
            }
        ),
    },
    EvidenceOpportunityComponentV2: {
        "rendered": frozenset(),
        "internal": frozenset(
            {
                "component_id",
                "exact_predicate",
                "raw_opportunity_denominator",
                "opportunity_floor",
                "coverage",
            }
        ),
    },
    EvidenceMetricV2: {
        "rendered": frozenset(
            {
                "metric_id",
                "label",
                "definition",
                "availability",
                "unit",
                "raw_opportunity_denominator",
                "raw_value",
                "within_position_percentile",
                "coverage",
                "limitation",
            }
        ),
        "internal": frozenset(
            {
                "purpose",
                "used_by_w09_ranking",
                "exact_predicate",
                "raw_numerator",
                "governed_minutes_denominator",
                "minute_state",
                "position_reference",
                "position_reference_count",
                "derivation_version",
                "source_lineage_digest",
            }
        ),
    },
    EvidenceGlossaryEntryV2: {
        "rendered": frozenset(
            {
                "label",
                "definition",
                "denominator_definition",
                "direction_notice",
                "coverage_definition",
                "limitation",
                "purpose",
                "used_by_w09_ranking",
            }
        ),
        "internal": frozenset({"metric_id"}),
    },
    UnsupportedInferenceV2: {
        "rendered": frozenset({"label"}),
        "internal": frozenset(
            {"inference_id", "definition", "evidence_class", "availability", "limitation"}
        ),
    },
}
_V2_RENDERED_FIELD_TOKENS = {
    (ParticipantExpertEvidenceBundleV2, "context"): "player.context",
    (ParticipantExpertEvidenceBundleV2, "w09_inputs"): "player.w09_inputs",
    (
        ParticipantExpertEvidenceBundleV2,
        "independent_descriptors",
    ): "player.independent_descriptors",
    (ParticipantExpertEvidenceBundleV2, "unsupported_inferences"): "player.unsupported_inferences",
    (ParticipantExpertEvidenceBundleV2, "glossary"): "task[1].exemplar.glossary",
    (EvidencePlayerContextV2, "display_name"): "player.context.display_name",
    (EvidencePlayerContextV2, "competition_name"): "player.context.competition_name",
    (EvidencePlayerContextV2, "season_label"): "player.context.season_label",
    (EvidencePlayerContextV2, "position_code"): "player.context.position_code",
    (EvidencePlayerContextV2, "team_names"): "player.context.team_names",
    (EvidencePlayerContextV2, "quantity"): "player.context.quantity",
    (EvidenceQuantityV2, "governed_minutes"): "player.context.quantity.governed_minutes",
    (EvidenceQuantityV2, "minute_state"): "player.context.quantity.minute_state",
    (EvidenceCoverageV2, "definition"): "metric.coverage.definition",
    (EvidenceFamilyV2, "label"): "family.label",
    (EvidenceFamilyV2, "definition"): "family.definition",
    (EvidenceFamilyV2, "availability"): "family.availability",
    (EvidenceFamilyV2, "mandatory_for_selected_rubric"): "family.mandatory_for_selected_rubric",
    (EvidenceFamilyV2, "metrics"): "family.metrics",
    (EvidenceMetricV2, "metric_id"): "metric.metric_id",
    (EvidenceMetricV2, "label"): "metric.label",
    (EvidenceMetricV2, "definition"): "metric.definition",
    (EvidenceMetricV2, "availability"): "metric.availability",
    (EvidenceMetricV2, "unit"): "metric.unit",
    (EvidenceMetricV2, "raw_opportunity_denominator"): "metric.raw_opportunity_denominator",
    (EvidenceMetricV2, "raw_value"): "metric.raw_value",
    (EvidenceMetricV2, "within_position_percentile"): "metric.within_position_percentile",
    (EvidenceMetricV2, "coverage"): "metric.coverage",
    (EvidenceMetricV2, "limitation"): "metric.limitation",
    (EvidenceGlossaryEntryV2, "label"): "item.label",
    (EvidenceGlossaryEntryV2, "definition"): "item.definition",
    (EvidenceGlossaryEntryV2, "denominator_definition"): "item.denominator_definition",
    (EvidenceGlossaryEntryV2, "direction_notice"): "item.direction_notice",
    (EvidenceGlossaryEntryV2, "coverage_definition"): "item.coverage_definition",
    (EvidenceGlossaryEntryV2, "limitation"): "item.limitation",
    (EvidenceGlossaryEntryV2, "purpose"): "item.purpose",
    (EvidenceGlossaryEntryV2, "used_by_w09_ranking"): "item.used_by_w09_ranking",
    (UnsupportedInferenceV2, "label"): "item.label",
}


def _response(**updates: Any) -> CandidateEvidenceJudgementV2:
    values: dict[str, Any] = {
        "response_version": "w10-expert-evidence-response-v2",
        "judgement_id": uuid4(),
        "session_id": uuid4(),
        "participant_id": uuid4(),
        "presentation_id": uuid4(),
        "query_id": uuid4(),
        "candidate_id": uuid4(),
        "comparison_digest": "1" * 64,
        "position_code": "GK",
        "md_subrubric": None,
        "state": JudgementState.RATED,
        "evidence_sufficiency": EvidenceSufficiencyV2.SUFFICIENT,
        "assessment_basis": AssessmentBasisV2.SUPPLIED_EVIDENCE,
        "relevance_rating": 3,
        "confidence": 4,
        "evidence_gap": None,
        "cited_independent_family_ids": ("ID-PASS-01",),
        "explanation": None,
        "recorded_at": datetime(2026, 8, 6, tzinfo=UTC),
    }
    values.update(updates)
    draft = CandidateEvidenceJudgementV2.model_construct(**values, judgement_digest="0" * 64)
    values["judgement_digest"] = canonical_research_digest(draft.digest_projection())
    return CandidateEvidenceJudgementV2(**values)


def test_policy_freezes_exact_w09_roster_threshold_status_and_md_comparability() -> None:
    policy = ExpertEvidencePolicyV2.model_validate_json(_POLICY.read_bytes())

    assert len(policy.feature_names) == 16
    assert policy.feature_names[0] == "passes_per90"
    assert policy.feature_names[-1] == "touches_per90"
    assert policy.threshold_status.endswith("not_scientifically_validated")
    assert policy.stability_validation_required_before_formal_freeze is True
    assert policy.thresholds.defending_duels_valid_starts == 5
    assert policy.thresholds.interceptions_valid_starts == 5
    assert policy.thresholds.clearances_valid_starts == 3
    assert policy.md_comparison_rule.startswith("one_branch_frozen_per_task")


def _mutated_policy(**updates: Any) -> dict[str, Any]:
    payload = json.loads(_POLICY.read_text())
    payload.update(updates)
    projection = {key: value for key, value in payload.items() if key != "policy_digest"}
    payload["policy_digest"] = canonical_research_digest(projection)
    return payload


def test_policy_rejects_directional_location_labels_with_recomputed_self_digest() -> None:
    payload = _mutated_policy(location_bins=[f"left_flank_{index}" for index in range(9)])

    with pytest.raises(ValidationError, match="location-bin roster and order"):
        ExpertEvidencePolicyV2.model_validate_json(json.dumps(payload))


def test_policy_rejects_modified_forbidden_roster_with_recomputed_self_digest() -> None:
    payload = json.loads(_POLICY.read_text())
    payload["forbidden_direction_semantics"][0] = "directional_progression"
    projection = {key: value for key, value in payload.items() if key != "policy_digest"}
    payload["policy_digest"] = canonical_research_digest(projection)

    with pytest.raises(ValidationError, match="direction-semantics roster and order"):
        ExpertEvidencePolicyV2.model_validate_json(json.dumps(payload))


def test_policy_rejects_reordered_bins_and_recomputed_definition_drift() -> None:
    payload = json.loads(_POLICY.read_text())
    payload["location_bins"][0], payload["location_bins"][1] = (
        payload["location_bins"][1],
        payload["location_bins"][0],
    )
    projection = {key: value for key, value in payload.items() if key != "policy_digest"}
    payload["policy_digest"] = canonical_research_digest(projection)
    with pytest.raises(ValidationError, match="location-bin roster and order"):
        ExpertEvidencePolicyV2.model_validate_json(json.dumps(payload))

    payload = _mutated_policy(threshold_rationale="Recomputed but unauthorised definition drift.")
    with pytest.raises(ValidationError, match="independently accepted pin"):
        ExpertEvidencePolicyV2.model_validate_json(json.dumps(payload))


def test_v1_presentation_bytes_and_digest_remain_exactly_compatible() -> None:
    original = _V1_PRESENTATION.read_bytes()
    presentation = ExpertStudyPresentationBundle.model_validate_json(original)

    assert presentation.presentation_digest == (
        "4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96"
    )
    assert canonical_json_bytes(presentation.model_dump(mode="json")) == original


def test_participant_keyed_order_differs_for_distinct_participant_digests() -> None:
    first = participant_keyed_candidate_order(
        _FIXED_SYNTHETIC_PARTICIPANT_DIGESTS[0], _FIXED_SYNTHETIC_CANDIDATE_IDS
    )
    second = participant_keyed_candidate_order(
        _FIXED_SYNTHETIC_PARTICIPANT_DIGESTS[1], _FIXED_SYNTHETIC_CANDIDATE_IDS
    )

    assert first != second


def test_fixed_participant_roster_breaks_retrieved_first_authority_correlation() -> None:
    retrieved = set(_FIXED_SYNTHETIC_CANDIDATE_IDS[:5])
    retrieved_counts_by_ordinal = tuple(
        sum(
            participant_keyed_candidate_order(participant_digest, _FIXED_SYNTHETIC_CANDIDATE_IDS)[
                ordinal
            ]
            in retrieved
            for participant_digest in _FIXED_SYNTHETIC_PARTICIPANT_DIGESTS
        )
        for ordinal in range(10)
    )

    assert retrieved_counts_by_ordinal == (101, 111, 85, 95, 99, 104, 108, 90, 107, 100)
    assert sum(retrieved_counts_by_ordinal[:5]) == 491


def test_permutation_key_reads_only_participant_digest_and_candidate_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    participant_digest = _FIXED_SYNTHETIC_PARTICIPANT_DIGESTS[0]
    candidate_ids = _FIXED_SYNTHETIC_CANDIDATE_IDS[:3]
    observed_keys: list[tuple[str, UUID | int | str]] = []

    def capture(key: str, candidate_id: UUID | int | str) -> bytes:
        observed_keys.append((key, candidate_id))
        return str(candidate_id).encode()

    monkeypatch.setattr(expert_relevance, "_schedule_order", capture)
    participant_keyed_candidate_order(participant_digest, candidate_ids)

    assert tuple(inspect.signature(participant_keyed_candidate_order).parameters) == (
        "participant_digest",
        "candidate_ids",
    )
    assert observed_keys == [(participant_digest, candidate_id) for candidate_id in candidate_ids]


def test_every_constructed_v2_evidence_field_is_rendered_or_explicitly_internal() -> None:
    template = _V2_PARTICIPANT_TEMPLATE.read_text()
    rendered_pairs: set[tuple[type[Any], str]] = set()

    for model, visibility in _V2_EVIDENCE_FIELD_VISIBILITY.items():
        rendered = visibility["rendered"]
        internal = visibility["internal"]
        assert rendered.isdisjoint(internal)
        assert rendered | internal == set(model.model_fields)
        rendered_pairs.update((model, field) for field in rendered)

    assert set(_V2_RENDERED_FIELD_TOKENS) == rendered_pairs
    assert all(token in template for token in _V2_RENDERED_FIELD_TOKENS.values())


def test_v2_response_requires_independent_evidence_for_primary_construct() -> None:
    response = _response()
    assert response.assessment_basis is AssessmentBasisV2.SUPPLIED_EVIDENCE

    payload = response.model_dump(mode="python")
    payload["cited_independent_family_ids"] = ()
    payload["judgement_digest"] = "0" * 64
    with pytest.raises(ValidationError, match="cite an independent"):
        CandidateEvidenceJudgementV2(**payload)


def test_prior_knowledge_only_is_retained_as_a_non_primary_sensitivity_lane() -> None:
    response = _response(
        assessment_basis=AssessmentBasisV2.PRIOR_PROFESSIONAL_KNOWLEDGE,
        cited_independent_family_ids=(),
    )
    assert response.state is JudgementState.RATED
    assert not response.cited_independent_family_ids


@pytest.mark.parametrize(
    "updates,match",
    (
        ({"evidence_sufficiency": EvidenceSufficiencyV2.INSUFFICIENT}, "rated.*sufficient"),
        (
            {
                "state": JudgementState.UNABLE_TO_ASSESS,
                "relevance_rating": None,
                "confidence": None,
                "assessment_basis": AssessmentBasisV2.UNABLE_TO_ASSESS,
                "evidence_sufficiency": EvidenceSufficiencyV2.SUFFICIENT,
                "cited_independent_family_ids": (),
            },
            "unable.*insufficient",
        ),
        (
            {
                "state": JudgementState.ABSTAIN,
                "relevance_rating": 2,
                "confidence": None,
            },
            "cannot carry ratings",
        ),
    ),
)
def test_v2_response_state_sufficiency_and_ratings_cannot_collapse(
    updates: dict[str, Any], match: str
) -> None:
    values = _response().model_dump(mode="python")
    values.update(updates)
    values["judgement_digest"] = "0" * 64
    with pytest.raises(ValidationError, match=match):
        CandidateEvidenceJudgementV2(**values)


def test_unable_response_requires_explicit_gap_and_no_rating() -> None:
    response = _response(
        state=JudgementState.UNABLE_TO_ASSESS,
        relevance_rating=None,
        confidence=None,
        assessment_basis=AssessmentBasisV2.UNABLE_TO_ASSESS,
        evidence_sufficiency=EvidenceSufficiencyV2.INSUFFICIENT,
        evidence_gap=EvidenceGapV2.MISSING_DESCRIPTOR,
        cited_independent_family_ids=(),
        explanation="The required descriptor did not provide enough evidence.",
    )
    assert response.relevance_rating is None
    assert response.evidence_gap is EvidenceGapV2.MISSING_DESCRIPTOR


def test_response_citations_must_match_position_and_selected_branch() -> None:
    with pytest.raises(ValidationError, match="mandatory family roster"):
        _response(cited_independent_family_ids=("ID-DEFLOC-01",))


def test_insufficient_response_requires_qualitative_note() -> None:
    with pytest.raises(ValidationError, match="qualitative explanation"):
        _response(
            state=JudgementState.UNABLE_TO_ASSESS,
            relevance_rating=None,
            confidence=None,
            assessment_basis=AssessmentBasisV2.UNABLE_TO_ASSESS,
            evidence_sufficiency=EvidenceSufficiencyV2.INSUFFICIENT,
            evidence_gap=EvidenceGapV2.COVERAGE_LIMITATION,
            cited_independent_family_ids=(),
        )


def test_response_digest_rejects_semantic_mutation() -> None:
    payload = _response().model_dump(mode="json")
    payload["confidence"] = 2
    with pytest.raises(ValidationError, match="digest"):
        CandidateEvidenceJudgementV2.model_validate_json(json.dumps(payload))


def test_independent_descriptor_identifiers_are_absent_from_w09_execution_path() -> None:
    independent_tokens = (
        "ID-LOC-01",
        "ID-PASS-01",
        "ID-DUEL-01",
        "ID-DEFLOC-01",
        "ID-SHOTLOC-01",
        "ID-GK-01",
    )
    paths = (
        _ROOT / "src/scouting/features/historical.py",
        _ROOT / "src/scouting/modeling/research.py",
        _ROOT / "src/scouting/serving/research.py",
        _ROOT / "src/scouting/m0/scoring.py",
        _ROOT / "configs/features/w09-historical-player-window-v1.json",
        _ROOT / "configs/models/w09-historical-retrieval-v1.json",
    )
    execution_text = "\n".join(path.read_text() for path in paths)
    assert all(token not in execution_text for token in independent_tokens)

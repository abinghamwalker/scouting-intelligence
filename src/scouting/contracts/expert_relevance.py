"""Strict W10 contracts for protected football-expert relevance evidence."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from enum import StrEnum
from fractions import Fraction
from typing import Annotated, Any, Literal, Self
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import Field, StringConstraints, model_validator

from .evidence import Sha256Digest
from .primitives import (
    ContractModel,
    NonEmptyString,
    NonNegativeInt,
    PositiveInt,
    SchemaVersion,
    StrictUuid,
    UnitInterval,
    UtcInstant,
)
from .research import ResearchVersionPins, canonical_research_digest

_PARTICIPANT_CODE = re.compile(r"^[A-Z0-9][A-Z0-9-]{5,31}$")

type FiniteScore = Annotated[float, Field(strict=True, allow_inf_nan=False)]
type NonNegativeScore = Annotated[
    float,
    Field(strict=True, ge=0.0, allow_inf_nan=False),
]
type RelevanceRating = Annotated[int, Field(strict=True, ge=0, le=4)]
type ConfidenceRating = Annotated[int, Field(strict=True, ge=1, le=5)]
type PositionCode = Literal["GK", "DF", "MD", "FW"]
type ClaimBoundary = Literal["football_relevance_only_not_recruitment_advice"]
type ParticipantCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z0-9][A-Z0-9-]{5,31}$"),
]

EXPERT_RELEVANCE_CLAIM_BOUNDARY: ClaimBoundary = "football_relevance_only_not_recruitment_advice"


class StudyMode(StrEnum):
    """Mutually exclusive evidence lanes."""

    DEVELOPMENT = "DEVELOPMENT"
    MECHANICS_PILOT = "MECHANICS_PILOT"
    FORMAL_G_RW4 = "FORMAL_G_RW4"


class ExpertExperienceKind(StrEnum):
    PROFESSIONAL_SCOUTING = "professional_scouting"
    RECRUITMENT_ANALYSIS = "recruitment_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    PROFESSIONAL_COACHING = "professional_coaching"
    PROFESSIONAL_PLAYING = "professional_playing"


class QueryDifficulty(StrEnum):
    STRAIGHTFORWARD = "straightforward"
    DIFFICULT = "difficult"


class EvidenceBand(StrEnum):
    LOWER = "lower"
    HIGHER = "higher"


class CandidateOrigin(StrEnum):
    RETRIEVED = "retrieved"
    CONTROL = "control"


class JudgementState(StrEnum):
    RATED = "rated"
    ABSTAIN = "abstain"
    UNABLE_TO_ASSESS = "unable_to_assess"


class PresentationKind(StrEnum):
    PRIMARY = "primary"
    REPEAT = "repeat"


class QualitativeFailureCategory(StrEnum):
    ROLE_MISMATCH = "role_mismatch"
    STYLE_MISMATCH = "style_mismatch"
    LEVEL_OR_CONTEXT_MISMATCH = "level_or_context_mismatch"
    SAMPLE_OR_EVIDENCE_TOO_WEAK = "sample_or_evidence_too_weak"
    IDENTITY_OR_POSITION_AMBIGUITY = "identity_or_position_ambiguity"
    OTHER = "other"


class ExpertGateDecisionKind(StrEnum):
    # Tri-state research-gate label, not a credential.
    PASS = "PASS"  # nosec B105
    FAIL = "FAIL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RatingAnchor(ContractModel):
    value: RelevanceRating
    label: NonEmptyString
    definition: NonEmptyString


class ExpertEligibilityProtocol(ContractModel):
    minimum_years_experience: PositiveInt
    accepted_experience: Annotated[tuple[ExpertExperienceKind, ...], Field(min_length=1)]
    requires_recent_player_assessment: bool
    recent_assessment_window_years: PositiveInt
    conflict_policy: NonEmptyString

    @model_validator(mode="after")
    def eligibility_is_coherent(self) -> Self:
        if len(self.accepted_experience) != len(set(self.accepted_experience)):
            raise ValueError("accepted expert experience kinds must be unique")
        return self


class StudyCompletionRules(ContractModel):
    minimum_eligible_participants: PositiveInt
    required_query_count: PositiveInt
    candidate_depth_per_query: PositiveInt
    retrieved_candidates_per_query: PositiveInt
    control_candidates_per_query: PositiveInt
    repeated_judgements_per_participant: PositiveInt
    minimum_non_abstaining_raters_per_candidate: PositiveInt
    minimum_participant_completion_rate: UnitInterval
    minimum_query_coverage_rate: UnitInterval
    minimum_rated_repeat_pair_rate: UnitInterval

    @model_validator(mode="after")
    def completion_is_coherent(self) -> Self:
        if (
            self.retrieved_candidates_per_query + self.control_candidates_per_query
            != self.candidate_depth_per_query
        ):
            raise ValueError("retrieved and control depth must equal candidate depth")
        if self.minimum_non_abstaining_raters_per_candidate > self.minimum_eligible_participants:
            raise ValueError("candidate rater minimum cannot exceed participant minimum")
        return self


class ExpertGateThresholds(ContractModel):
    relevant_rating_floor: RelevanceRating
    minimum_retrieved_precision_at_k: UnitInterval
    minimum_mean_ndcg_at_k: UnitInterval
    minimum_retrieved_control_relevant_rate_lift: FiniteScore
    minimum_paired_ndcg_delta: FiniteScore
    paired_ndcg_confidence: UnitInterval
    paired_ndcg_bootstrap_resamples: PositiveInt
    paired_ndcg_bootstrap_seed: NonNegativeInt
    paired_ndcg_interval_method: Literal["paired_percentile_query_bootstrap"]
    paired_ndcg_lower_bound_must_exceed: NonNegativeScore
    minimum_ordinal_agreement: FiniteScore
    ordinal_agreement_method: Literal[
        "mean_pairwise_one_minus_absolute_rating_difference_over_four"
    ]
    maximum_repeat_mean_absolute_difference: NonNegativeScore
    minimum_repeat_within_one_rate: UnitInterval
    ndcg_k: PositiveInt
    precision_k: PositiveInt

    @model_validator(mode="after")
    def thresholds_are_coherent(self) -> Self:
        if self.relevant_rating_floor < 1:
            raise ValueError("relevant rating floor must distinguish relevance from zero")
        if not -1.0 <= self.minimum_ordinal_agreement <= 1.0:
            raise ValueError("ordinal agreement threshold must be in [-1, 1]")
        if self.minimum_retrieved_control_relevant_rate_lift <= 0.0:
            raise ValueError("retrieved-control lift threshold must be positive")
        if self.minimum_paired_ndcg_delta <= 0.0:
            raise ValueError("paired NDCG delta threshold must be positive")
        if self.paired_ndcg_confidence <= 0.5:
            raise ValueError("paired NDCG confidence must exceed one half")
        if self.paired_ndcg_lower_bound_must_exceed != 0.0:
            raise ValueError("W10 v1 freezes the paired NDCG lower-bound threshold at zero")
        return self


class ExpertRelevanceProtocol(ContractModel):
    """Decision-bearing preregistration, immutable under its semantic digest."""

    schema_version: SchemaVersion = 1
    protocol_id: StrictUuid
    protocol_version: Literal["w10-expert-relevance-protocol-v1"]
    title: NonEmptyString
    research_question: NonEmptyString
    relevance_definition: NonEmptyString
    limitations_notice: NonEmptyString
    consent_and_local_data_handling: NonEmptyString
    pseudonymous_identifier_policy: NonEmptyString
    missing_response_policy: NonEmptyString
    subgroup_reporting_policy: NonEmptyString
    qualitative_reason_policy: NonEmptyString
    protected_label_policy: NonEmptyString
    threshold_freeze_policy: NonEmptyString
    participant_denominator_policy: NonEmptyString
    query_denominator_policy: NonEmptyString
    metric_policy: NonEmptyString
    repeat_question_policy: NonEmptyString
    pass_criteria: NonEmptyString
    fail_criteria: NonEmptyString
    insufficient_evidence_criteria: NonEmptyString
    eligibility: ExpertEligibilityProtocol
    rating_anchors: Annotated[tuple[RatingAnchor, ...], Field(min_length=5, max_length=5)]
    confidence_minimum: Literal[1]
    confidence_maximum: Literal[5]
    completion: StudyCompletionRules
    thresholds: ExpertGateThresholds
    w09_pins: ResearchVersionPins
    formal_candidate_provenance_blinded: Literal[True] = True
    pilot_formal_separation_required: Literal[True] = True
    protected_labels_may_train_model: Literal[False] = False
    protocol_digest: Sha256Digest
    claim_boundary: ClaimBoundary = EXPERT_RELEVANCE_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"protocol_digest"})

    @model_validator(mode="after")
    def protocol_is_coherent(self) -> Self:
        anchor_values = tuple(anchor.value for anchor in self.rating_anchors)
        if anchor_values != (0, 1, 2, 3, 4):
            raise ValueError("rating anchors must cover 0..4 in order")
        if self.completion.required_query_count != 8:
            raise ValueError("W10 protocol v1 freezes exactly eight queries")
        if self.completion.candidate_depth_per_query != 10:
            raise ValueError("W10 protocol v1 freezes candidate depth at ten")
        if self.thresholds.ndcg_k != self.completion.retrieved_candidates_per_query:
            raise ValueError("NDCG k must equal retrieved depth")
        if self.thresholds.precision_k != self.completion.retrieved_candidates_per_query:
            raise ValueError("precision k must equal retrieved depth")
        if self.protocol_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("protocol digest must equal its canonical semantic projection")
        return self


class ProtocolApproval(ContractModel):
    """Human product-owner approval for one exact protocol/query authority."""

    schema_version: SchemaVersion = 1
    approval_id: StrictUuid
    protocol_version: Literal["w10-expert-relevance-protocol-v1"]
    protocol_digest: Sha256Digest
    query_pack_version: Literal["w10-frozen-query-pack-v1"]
    query_pack_digest: Sha256Digest
    approved_at: UtcInstant
    approved_by_pseudonym: ParticipantCode
    confirmation: Literal[
        "I approve this exact protocol and frozen query pack for formal G-RW4 participation."
    ]
    approval_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"approval_digest"})

    @model_validator(mode="after")
    def approval_is_coherent(self) -> Self:
        if self.approval_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("approval digest must bind exact protocol and query pack")
        return self


class FrozenCandidate(ContractModel):
    """Protected query-pack candidate; origin is never exposed in participant payloads."""

    candidate_id: StrictUuid
    grain_id: NonEmptyString
    player_id: StrictUuid
    display_name: NonEmptyString
    competition_id: StrictUuid
    competition_name: NonEmptyString
    season_id: NonEmptyString
    position_code: PositionCode
    team_names: tuple[NonEmptyString, ...]
    minutes: NonNegativeScore
    origin: CandidateOrigin
    retrieval_rank: PositiveInt | None = None
    retrieval_score: NonNegativeScore | None = None
    control_rank: PositiveInt | None = None
    control_match_rule: NonEmptyString | None = None

    @model_validator(mode="after")
    def origin_is_coherent(self) -> Self:
        if self.origin is CandidateOrigin.RETRIEVED:
            if self.retrieval_rank is None or self.retrieval_score is None:
                raise ValueError("retrieved candidates require rank and score")
            if self.control_match_rule is not None:
                raise ValueError("retrieved candidates cannot carry a control rule")
            if self.control_rank is not None:
                raise ValueError("retrieved candidates cannot carry a control rank")
        else:
            if self.retrieval_rank is not None or self.retrieval_score is not None:
                raise ValueError("controls cannot carry retrieval rank or score")
            if self.control_match_rule is None or self.control_rank is None:
                raise ValueError("controls require their deterministic rank and matching rule")
        return self


class FrozenExpertQuery(ContractModel):
    query_id: StrictUuid
    query_code: NonEmptyString
    w09_request_digest: Sha256Digest
    w09_result_id: StrictUuid
    w09_result_digest: Sha256Digest
    w09_generated_at: UtcInstant
    exemplar_grain_id: NonEmptyString
    exemplar_player_id: StrictUuid
    exemplar_display_name: NonEmptyString
    exemplar_competition_id: StrictUuid
    exemplar_competition_name: NonEmptyString
    exemplar_season_id: NonEmptyString
    exemplar_position_code: PositionCode
    exemplar_team_names: tuple[NonEmptyString, ...]
    exemplar_minutes: NonNegativeScore
    evidence_band: EvidenceBand
    difficulty: QueryDifficulty
    football_prompt: NonEmptyString
    candidates: Annotated[tuple[FrozenCandidate, ...], Field(min_length=10, max_length=10)]
    query_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"query_digest"})

    @model_validator(mode="after")
    def query_is_coherent(self) -> Self:
        ids = tuple(candidate.candidate_id for candidate in self.candidates)
        grains = tuple(candidate.grain_id for candidate in self.candidates)
        if len(ids) != len(set(ids)) or len(grains) != len(set(grains)):
            raise ValueError("query candidates must be unique")
        if self.exemplar_grain_id in grains:
            raise ValueError("the exemplar cannot appear as its own candidate")
        origins = tuple(candidate.origin for candidate in self.candidates)
        if (
            origins.count(CandidateOrigin.RETRIEVED) != 5
            or origins.count(CandidateOrigin.CONTROL) != 5
        ):
            raise ValueError("each query must contain five retrieved and five controls")
        if any(
            candidate.position_code != self.exemplar_position_code for candidate in self.candidates
        ):
            raise ValueError("all candidates must match the exemplar position group")
        if self.query_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("query digest must equal its semantic projection")
        return self


class FrozenExpertQueryPack(ContractModel):
    schema_version: SchemaVersion = 1
    query_pack_id: StrictUuid
    query_pack_version: Literal["w10-frozen-query-pack-v1"]
    built_at: UtcInstant
    w09_pins: ResearchVersionPins
    query_selection_rule: NonEmptyString
    control_selection_rule: NonEmptyString
    participant_order_rule: NonEmptyString
    queries: Annotated[tuple[FrozenExpertQuery, ...], Field(min_length=8, max_length=8)]
    repeat_anchor_candidate_ids: Annotated[
        tuple[StrictUuid, ...], Field(min_length=2, max_length=2)
    ]
    contains_synthetic_rows: Literal[False] = False
    query_pack_digest: Sha256Digest
    claim_boundary: ClaimBoundary = EXPERT_RELEVANCE_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"query_pack_digest"})

    @model_validator(mode="after")
    def pack_is_coherent(self) -> Self:
        query_ids = tuple(query.query_id for query in self.queries)
        query_codes = tuple(query.query_code for query in self.queries)
        if len(query_ids) != len(set(query_ids)) or len(query_codes) != len(set(query_codes)):
            raise ValueError("frozen query identities must be unique")
        for position in ("GK", "DF", "MD", "FW"):
            subset = tuple(
                query for query in self.queries if query.exemplar_position_code == position
            )
            if len(subset) != 2 or {query.evidence_band for query in subset} != set(EvidenceBand):
                raise ValueError("each position requires lower and higher evidence queries")
        if {query.difficulty for query in self.queries} != set(QueryDifficulty):
            raise ValueError("query pack must include straightforward and difficult cases")
        if sum(query.difficulty is QueryDifficulty.STRAIGHTFORWARD for query in self.queries) != 4:
            raise ValueError("query pack requires four cases per difficulty class")
        competition_ids = {query.exemplar_competition_id for query in self.queries}
        if len(competition_ids) != 5:
            raise ValueError("query pack must cover all five retained competitions")
        all_candidates = {
            candidate.candidate_id for query in self.queries for candidate in query.candidates
        }
        if len(self.repeat_anchor_candidate_ids) != len(set(self.repeat_anchor_candidate_ids)):
            raise ValueError("repeat anchors must be unique")
        if any(anchor not in all_candidates for anchor in self.repeat_anchor_candidate_ids):
            raise ValueError("repeat anchors must reference frozen candidates")
        if self.query_pack_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("query-pack digest must equal its canonical semantic projection")
        return self


class PresentedCandidate(ContractModel):
    """Participant-safe candidate projection with no provenance or score fields."""

    candidate_id: StrictUuid
    display_name: NonEmptyString
    competition_name: NonEmptyString
    season_label: NonEmptyString
    position_code: PositionCode
    team_names: tuple[NonEmptyString, ...]
    minutes: NonNegativeScore


class PresentedExpertQuery(ContractModel):
    """Participant-safe exemplar and candidates for one blinded query."""

    query_id: StrictUuid
    query_code: NonEmptyString
    exemplar_display_name: NonEmptyString
    exemplar_competition_name: NonEmptyString
    exemplar_season_label: NonEmptyString
    exemplar_position_code: PositionCode
    exemplar_team_names: tuple[NonEmptyString, ...]
    exemplar_minutes: NonNegativeScore
    football_prompt: NonEmptyString
    candidates: Annotated[tuple[PresentedCandidate, ...], Field(min_length=10, max_length=10)]

    @model_validator(mode="after")
    def presentation_is_coherent(self) -> Self:
        candidate_ids = tuple(candidate.candidate_id for candidate in self.candidates)
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("presented candidates must be unique")
        if any(
            candidate.position_code != self.exemplar_position_code for candidate in self.candidates
        ):
            raise ValueError("presented candidates must match the exemplar position group")
        return self


class ExpertStudyPresentationBundle(ContractModel):
    """Physically separate, participant-safe projection of a frozen query pack."""

    schema_version: SchemaVersion = 1
    presentation_version: Literal["w10-expert-study-presentation-v1"]
    protocol_digest: Sha256Digest
    query_pack_digest: Sha256Digest
    query_order_rule: NonEmptyString
    candidate_order_rule: NonEmptyString
    schedule_rule: Literal["w10-participant-keyed-interleaved-v1"]
    minimum_repeat_primary_delay: PositiveInt
    repeat_must_be_nonterminal: Literal[True]
    repeats_must_be_nonadjacent: Literal[True]
    queries: Annotated[tuple[PresentedExpertQuery, ...], Field(min_length=8, max_length=8)]
    repeat_anchor_candidate_ids: Annotated[
        tuple[StrictUuid, ...], Field(min_length=2, max_length=2)
    ]
    presentation_digest: Sha256Digest
    claim_boundary: ClaimBoundary = EXPERT_RELEVANCE_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"presentation_digest"})

    @model_validator(mode="after")
    def bundle_is_coherent(self) -> Self:
        query_ids = tuple(query.query_id for query in self.queries)
        if len(query_ids) != len(set(query_ids)):
            raise ValueError("presented query identities must be unique")
        presented_candidates = {
            candidate.candidate_id for query in self.queries for candidate in query.candidates
        }
        if len(self.repeat_anchor_candidate_ids) != len(set(self.repeat_anchor_candidate_ids)):
            raise ValueError("presented repeat anchors must be unique")
        if any(anchor not in presented_candidates for anchor in self.repeat_anchor_candidate_ids):
            raise ValueError("presented repeat anchors must reference participant-safe candidates")
        if self.presentation_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("presentation digest must equal its participant-safe projection")
        return self


class EvidencePurposeV2(StrEnum):
    """The only playing-evidence purposes admitted to participant metric rows."""

    W09_INPUT = "W09_INPUT"
    INDEPENDENT_DESCRIPTOR = "INDEPENDENT_DESCRIPTOR"


class EvidenceAvailabilityV2(StrEnum):
    """Non-collapsible A1 availability states."""

    OBSERVED_VALUE = "observed_value"
    OBSERVED_ZERO = "observed_zero"
    INSUFFICIENT_OPPORTUNITIES = "insufficient_opportunities"
    NOT_APPLICABLE = "not_applicable"
    NOT_CAPTURED = "not_captured"
    INVALID_MISSING = "invalid_missing"


class MdEvidenceSubrubricV2(StrEnum):
    """Frozen comparable branch used by both players in one MD comparison."""

    DEFENSIVE = "DEFENSIVE"
    SHOOTING = "SHOOTING"


class EvidenceMetricUnitV2(StrEnum):
    SHARE = "share"
    COUNT_PER_90_GOVERNED_MINUTES = "count_per_90_governed_minutes"


type IndependentFamilyIdV2 = Literal[
    "ID-LOC-01",
    "ID-PASS-01",
    "ID-DUEL-01",
    "ID-DEFLOC-01",
    "ID-SHOTLOC-01",
    "ID-GK-01",
]

_INDEPENDENT_FAMILY_ORDER_V2 = (
    "ID-LOC-01",
    "ID-PASS-01",
    "ID-DUEL-01",
    "ID-DEFLOC-01",
    "ID-SHOTLOC-01",
    "ID-GK-01",
)
_W09_METRIC_IDS_V2 = (
    "w09.passes_per90",
    "w09.accurate_passes_per90",
    "w09.crosses_per90",
    "w09.smart_passes_per90",
    "w09.shots_per90",
    "w09.shots_on_target_per90",
    "w09.goals_per90",
    "w09.key_passes_per90",
    "w09.assists_per90",
    "w09.duels_per90",
    "w09.duels_won_per90",
    "w09.interceptions_per90",
    "w09.clearances_per90",
    "w09.accelerations_per90",
    "w09.fouls_per90",
    "w09.touches_per90",
)
_NEUTRAL_BIN_IDS_V2 = (
    "recorded_x_0_33__recorded_y_0_33",
    "recorded_x_0_33__recorded_y_34_66",
    "recorded_x_0_33__recorded_y_67_100",
    "recorded_x_34_66__recorded_y_0_33",
    "recorded_x_34_66__recorded_y_34_66",
    "recorded_x_34_66__recorded_y_67_100",
    "recorded_x_67_100__recorded_y_0_33",
    "recorded_x_67_100__recorded_y_34_66",
    "recorded_x_67_100__recorded_y_67_100",
)
_FORBIDDEN_DIRECTION_SEMANTICS_V2 = (
    "progressive",
    "final_third",
    "attacking_direction",
    "left_flank",
    "right_flank",
    "toward_goal",
)
_ACCEPTED_EXPERT_EVIDENCE_POLICY_DIGEST_V2 = (
    "867ea773892b4bfb8dc33b0ccc3f141ae1c04027d19b6ebe2fad8e0f47468a9d"
)
_ACCEPTED_EXPERT_EVIDENCE_BUNDLE_PINS_V2 = {
    (
        "72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7",
        "w09-historical-player-window-v1-a31511705ac15a5d",
        "428d25ed4f1fd5dec7df74f30905db875cd548270fc2824b431e1bc8a6447cc1",
    ): "7bfb2615b6029d2404add8dd3dd1350c0521d5f6330c233498f3c3d7f788673f",
    (
        "2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e",
        "w09-historical-player-window-v1-ad74298cf718d6f6",
        "49bf6f72d2e564fa5c421c2eb36f70ceb57810a44c1442da9e14a3db6b799bb9",
    ): "e2ee046a037eaed710e41796ed247897d4c8810443d84b73f8ef4607704756af",
    (
        "2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e",
        "w09-historical-player-window-v1-a9f7cc2d5fc12ea0",
        "20752d615978eb908a313dff346bff258a255602dff639c520e3dc45cb29bb42",
    ): _ACCEPTED_EXPERT_EVIDENCE_POLICY_DIGEST_V2,
}
_EXPECTED_FAMILY_METRICS_V2: dict[str, tuple[str, ...]] = {
    "W09-INPUT-01": _W09_METRIC_IDS_V2,
    "ID-LOC-01": tuple(f"loc.{value}" for value in _NEUTRAL_BIN_IDS_V2),
    "ID-PASS-01": tuple(f"pass.sub_event_{value}_share" for value in (81, 83, 84, 85)),
    "ID-DUEL-01": tuple(f"duel.sub_event_{value}_share" for value in (10, 11, 12, 13)),
    "ID-DEFLOC-01": tuple(
        f"defloc.{component}.{value}"
        for component in ("defending_duel", "interception", "clearance")
        for value in _NEUTRAL_BIN_IDS_V2
    ),
    "ID-SHOTLOC-01": tuple(f"shotloc.{value}" for value in _NEUTRAL_BIN_IDS_V2),
    "ID-GK-01": (
        "gk.goal_kicks_per90",
        "gk.leaving_line_per90",
        "gk.reflex_share",
        "gk.generic_save_share",
    ),
}
_EXPECTED_OPPORTUNITY_COMPONENTS_V2: dict[str, tuple[str, ...]] = {
    "W09-INPUT-01": ("governed_matrix_row",),
    "ID-LOC-01": ("valid_starts",),
    "ID-PASS-01": ("all_passes",),
    "ID-DUEL-01": ("all_duels",),
    "ID-DEFLOC-01": (
        "defending_duel_valid_starts",
        "interception_valid_starts",
        "clearance_valid_starts",
    ),
    "ID-SHOTLOC-01": ("valid_shot_starts",),
    "ID-GK-01": ("save_attempts", "leaving_line_actions", "goal_kicks"),
}
_COMMON_UNSUPPORTED_IDS_V2 = (
    "general.causal_tactics",
    "general.off_ball_movement",
    "general.pressing_intensity",
    "general.possession_responsibility",
    "general.role_instructions",
    "general.formation_adjustment",
    "general.opponent_context",
    "general.current_future_ability",
    "general.availability_fit_value",
    "general.recruitment_outcomes",
)
_POSITION_UNSUPPORTED_IDS_V2: dict[str, tuple[str, ...]] = {
    "GK": (
        "gk.shots_faced",
        "gk.save_percentage",
        "gk.shot_stopping_quality",
        "gk.goals_conceded",
        "gk.expected_goals",
        "gk.goals_prevented",
        "gk.claims_cross_dominance",
        "gk.errors",
        "gk.sweeping_effectiveness",
    ),
    "DF": ("df.off_ball_defensive_role",),
    "MD": ("md.off_ball_midfield_role",),
    "FW": ("fw.off_ball_attacking_role",),
}


def mandatory_independent_family_ids_v2(
    position_code: PositionCode,
    md_subrubric: MdEvidenceSubrubricV2 | None,
) -> tuple[IndependentFamilyIdV2, ...]:
    """Return the exact ordered independent roster admissible for one comparison."""

    if position_code == "MD":
        if md_subrubric is None:
            raise ValueError("MD evidence requires an explicit comparison sub-rubric")
        branch: IndependentFamilyIdV2 = (
            "ID-DEFLOC-01" if md_subrubric is MdEvidenceSubrubricV2.DEFENSIVE else "ID-SHOTLOC-01"
        )
        return ("ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", branch)
    if md_subrubric is not None:
        raise ValueError("only MD comparisons may declare an MD sub-rubric")
    rosters: dict[str, tuple[IndependentFamilyIdV2, ...]] = {
        "GK": ("ID-LOC-01", "ID-PASS-01", "ID-GK-01"),
        "DF": ("ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-DEFLOC-01"),
        "FW": ("ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-SHOTLOC-01"),
    }
    return rosters[position_code]


type PercentileV2 = Annotated[float, Field(strict=True, ge=0.0, le=100.0)]


class EvidenceCoverageV2(ContractModel):
    observed: NonNegativeInt
    expected: NonNegativeInt
    proportion: UnitInterval | None
    definition: NonEmptyString

    @model_validator(mode="after")
    def coverage_is_exact(self) -> Self:
        if self.observed > self.expected:
            raise ValueError("evidence coverage observed cannot exceed expected")
        if self.expected == 0:
            if self.proportion is not None:
                raise ValueError("zero expected coverage cannot carry a proportion")
        elif self.proportion != self.observed / self.expected:
            raise ValueError("evidence coverage proportion must equal its exact counts")
        return self


class EvidenceMetricV2(ContractModel):
    """One scalar participant metric with exact purpose, evidence and missingness."""

    metric_id: NonEmptyString
    label: NonEmptyString
    definition: NonEmptyString
    purpose: EvidencePurposeV2
    used_by_w09_ranking: bool
    availability: EvidenceAvailabilityV2
    unit: EvidenceMetricUnitV2
    exact_predicate: NonEmptyString
    raw_numerator: NonNegativeInt | None
    raw_opportunity_denominator: NonNegativeScore | None
    raw_value: FiniteScore | None
    within_position_percentile: PercentileV2 | None
    governed_minutes_denominator: NonNegativeScore
    minute_state: Literal["exact", "conservative_lower_bound"]
    coverage: EvidenceCoverageV2
    position_reference: NonEmptyString
    position_reference_count: NonNegativeInt
    derivation_version: Literal["w10-expert-evidence-derivation-v2"]
    source_lineage_digest: Sha256Digest
    limitation: NonEmptyString

    @model_validator(mode="after")
    def metric_is_evidence_honest(self) -> Self:
        if self.used_by_w09_ranking != (self.purpose is EvidencePurposeV2.W09_INPUT):
            raise ValueError("used_by_w09_ranking must be fixed by evidence purpose")
        observed = self.availability in {
            EvidenceAvailabilityV2.OBSERVED_VALUE,
            EvidenceAvailabilityV2.OBSERVED_ZERO,
        }
        if observed:
            if (
                self.raw_numerator is None
                or self.raw_opportunity_denominator is None
                or self.raw_opportunity_denominator == 0
                or self.raw_value is None
                or self.within_position_percentile is None
            ):
                raise ValueError("observed metrics require exact value, counts and percentile")
            if self.position_reference_count == 0:
                raise ValueError("observed metrics require a positive comparable reference count")
            if (self.availability is EvidenceAvailabilityV2.OBSERVED_ZERO) != (
                self.raw_numerator == 0
            ):
                raise ValueError("observed_zero must mean an exact zero numerator")
            if self.unit is EvidenceMetricUnitV2.SHARE and self.raw_value != (
                self.raw_numerator / self.raw_opportunity_denominator
            ):
                raise ValueError("share values must reconstruct from exact raw counts")
            if self.unit is EvidenceMetricUnitV2.COUNT_PER_90_GOVERNED_MINUTES:
                if self.raw_opportunity_denominator != self.governed_minutes_denominator:
                    raise ValueError("per-90 raw denominator must equal governed minutes")
                if self.raw_value != (
                    self.raw_numerator * 90.0 / self.governed_minutes_denominator
                ):
                    raise ValueError("per-90 values must reconstruct from count and minutes")
        elif self.availability is EvidenceAvailabilityV2.INSUFFICIENT_OPPORTUNITIES:
            if (
                self.raw_numerator is None
                or self.raw_opportunity_denominator is None
                or self.raw_value is not None
                or self.within_position_percentile is not None
            ):
                raise ValueError(
                    "insufficient opportunity metrics show counts but suppress estimates"
                )
        elif any(
            item is not None
            for item in (
                self.raw_numerator,
                self.raw_opportunity_denominator,
                self.raw_value,
                self.within_position_percentile,
            )
        ):
            raise ValueError("unavailable metrics cannot masquerade as numeric evidence")
        return self


class EvidenceOpportunityComponentV2(ContractModel):
    component_id: NonEmptyString
    exact_predicate: NonEmptyString
    raw_opportunity_denominator: NonNegativeInt
    opportunity_floor: NonNegativeInt
    coverage: EvidenceCoverageV2

    @model_validator(mode="after")
    def component_is_exact(self) -> Self:
        if self.raw_opportunity_denominator != self.coverage.observed:
            raise ValueError("component denominator must equal its predicate coverage numerator")
        return self


class EvidenceFamilyV2(ContractModel):
    family_id: Literal[
        "W09-INPUT-01",
        "ID-LOC-01",
        "ID-PASS-01",
        "ID-DUEL-01",
        "ID-DEFLOC-01",
        "ID-SHOTLOC-01",
        "ID-GK-01",
    ]
    label: NonEmptyString
    definition: NonEmptyString
    purpose: EvidencePurposeV2
    used_by_w09_ranking: bool
    availability: EvidenceAvailabilityV2
    exact_family_predicate: NonEmptyString
    raw_opportunity_denominator: NonNegativeInt | None
    opportunity_floor: NonNegativeInt | None
    opportunity_components: Annotated[
        tuple[EvidenceOpportunityComponentV2, ...], Field(min_length=1)
    ]
    threshold_policy_version: Literal["w10-evidence-opportunity-thresholds-v2-prepilot"]
    threshold_rationale: NonEmptyString
    mandatory_for_selected_rubric: bool
    metrics: tuple[EvidenceMetricV2, ...]

    @model_validator(mode="after")
    def family_is_coherent(self) -> Self:
        if self.used_by_w09_ranking != (self.purpose is EvidencePurposeV2.W09_INPUT):
            raise ValueError("family W09-use flag must be fixed by purpose")
        if not self.metrics:
            raise ValueError("evidence families require explicit metric rows")
        if len({item.component_id for item in self.opportunity_components}) != len(
            self.opportunity_components
        ):
            raise ValueError("family opportunity components must be unique")
        if (
            tuple(item.component_id for item in self.opportunity_components)
            != _EXPECTED_OPPORTUNITY_COMPONENTS_V2[self.family_id]
        ):
            raise ValueError("family opportunity-component roster or order drifted")
        if len({metric.metric_id for metric in self.metrics}) != len(self.metrics):
            raise ValueError("evidence family metric ids must be unique")
        expected_metric_ids = _EXPECTED_FAMILY_METRICS_V2[self.family_id]
        if tuple(metric.metric_id for metric in self.metrics) != expected_metric_ids:
            raise ValueError("evidence family metric roster or order drifted")
        if self.availability is EvidenceAvailabilityV2.NOT_APPLICABLE:
            if self.raw_opportunity_denominator is not None or self.opportunity_floor is not None:
                raise ValueError("not-applicable family cannot expose a composite opportunity")
        elif len(self.opportunity_components) == 1:
            component = self.opportunity_components[0]
            if (
                self.raw_opportunity_denominator != component.raw_opportunity_denominator
                or self.opportunity_floor != component.opportunity_floor
            ):
                raise ValueError("single-component family summary must equal its component")
        elif self.raw_opportunity_denominator is not None or self.opportunity_floor is not None:
            raise ValueError("multi-component family cannot expose a misleading composite minimum")
        observed = self.availability in {
            EvidenceAvailabilityV2.OBSERVED_VALUE,
            EvidenceAvailabilityV2.OBSERVED_ZERO,
        }
        component_sufficient = tuple(
            item.raw_opportunity_denominator >= item.opportunity_floor
            for item in self.opportunity_components
        )
        if observed and not all(component_sufficient):
            raise ValueError("observed family requires every component opportunity floor")
        if self.availability is EvidenceAvailabilityV2.INSUFFICIENT_OPPORTUNITIES and all(
            component_sufficient
        ):
            raise ValueError("insufficient family requires a component below its opportunity floor")
        if any(
            metric.purpose is not self.purpose
            or metric.used_by_w09_ranking != self.used_by_w09_ranking
            for metric in self.metrics
        ):
            raise ValueError("family metrics must preserve purpose separation")
        if self.mandatory_for_selected_rubric and self.availability not in {
            EvidenceAvailabilityV2.OBSERVED_VALUE,
            EvidenceAvailabilityV2.OBSERVED_ZERO,
        }:
            raise ValueError("a mandatory family must be comparably observed")
        return self


class EvidenceQuantityV2(ContractModel):
    """Evidence amount and context, explicitly not a role/style metric."""

    evidence_class: Literal["EVIDENCE_QUANTITY"] = "EVIDENCE_QUANTITY"
    governed_minutes: NonNegativeScore
    minute_state: Literal["exact", "conservative_lower_bound"]
    match_count: PositiveInt
    retained_action_count: NonNegativeInt
    lineup_match_coverage: EvidenceCoverageV2
    action_match_coverage: EvidenceCoverageV2
    coordinate_coverage: EvidenceCoverageV2
    limitation: NonEmptyString


class EvidencePlayerContextV2(ContractModel):
    """Required participant context with no internal stable player/grain identity."""

    display_name: NonEmptyString
    competition_name: NonEmptyString
    season_label: NonEmptyString
    window_start_utc: UtcInstant
    window_end_utc: UtcInstant
    position_code: PositionCode
    team_names: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    quantity: EvidenceQuantityV2

    @model_validator(mode="after")
    def context_is_temporal(self) -> Self:
        if self.window_start_utc >= self.window_end_utc:
            raise ValueError("evidence window must have positive duration")
        return self


class EvidenceGlossaryEntryV2(ContractModel):
    metric_id: NonEmptyString
    label: NonEmptyString
    definition: NonEmptyString
    denominator_definition: NonEmptyString
    direction_notice: Literal[
        "Descriptive only; no better/worse, attacking-direction or pitch-side meaning."
    ]
    coverage_definition: NonEmptyString
    limitation: NonEmptyString
    purpose: EvidencePurposeV2
    used_by_w09_ranking: bool

    @model_validator(mode="after")
    def glossary_purpose_is_fixed(self) -> Self:
        if self.used_by_w09_ranking != (self.purpose is EvidencePurposeV2.W09_INPUT):
            raise ValueError("glossary W09-use flag must be fixed by purpose")
        return self


class EvidenceOpportunityThresholdsV2(ContractModel):
    valid_starts: Literal[100]
    passes: Literal[25]
    duels: Literal[20]
    defending_duels_valid_starts: Literal[5]
    interceptions_valid_starts: Literal[5]
    clearances_valid_starts: Literal[3]
    shots_valid_starts: Literal[10]
    goalkeeper_save_attempts: Literal[10]
    goalkeeper_leaving_line_actions: Literal[3]
    goalkeeper_goal_kicks: Literal[20]
    minimum_coordinate_coverage: UnitInterval


class ExpertEvidencePolicyV2(ContractModel):
    """Preregistered derivation rules; thresholds are pre-pilot measurement rules."""

    schema_version: Literal[2] = 2
    policy_version: Literal["w10-expert-evidence-policy-v2-prepilot"]
    evidence_version: Literal["w10-expert-evidence-presentation-v2"]
    derivation_version: Literal["w10-expert-evidence-derivation-v2"]
    threshold_policy_version: Literal["w10-evidence-opportunity-thresholds-v2-prepilot"]
    threshold_status: Literal[
        "preregistered_pre_pilot_measurement_rules_not_scientifically_validated"
    ]
    threshold_rationale: NonEmptyString
    stability_validation_required_before_formal_freeze: Literal[True]
    canonical_build_id: Literal["2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e"]
    matrix_version: Literal["w09-historical-player-window-v1-a9f7cc2d5fc12ea0"]
    matrix_digest: Literal["20752d615978eb908a313dff346bff258a255602dff639c520e3dc45cb29bb42"]
    feature_names: Annotated[tuple[NonEmptyString, ...], Field(min_length=16, max_length=16)]
    location_bins: Annotated[tuple[NonEmptyString, ...], Field(min_length=9, max_length=9)]
    percentile_method: Literal[
        "within_broad_position_midrank_100_times_less_plus_half_equal_over_observed"
    ]
    comparable_states: tuple[Literal["observed_value"], Literal["observed_zero"]]
    md_comparison_rule: Literal[
        "one_branch_frozen_per_task_and_shared_by_exemplar_and_every_candidate"
    ]
    thresholds: EvidenceOpportunityThresholdsV2
    forbidden_direction_semantics: Annotated[tuple[NonEmptyString, ...], Field(min_length=6)]
    policy_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"policy_digest"})

    @model_validator(mode="after")
    def policy_is_exact(self) -> Self:
        expected_features = (
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
        if self.feature_names != expected_features:
            raise ValueError("v2 policy must freeze the exact ordered W09 feature roster")
        if self.thresholds.minimum_coordinate_coverage != 0.95:
            raise ValueError("v2 coordinate coverage floor must remain exactly 0.95")
        if self.location_bins != _NEUTRAL_BIN_IDS_V2:
            raise ValueError("neutral location-bin roster and order must remain exact")
        if self.forbidden_direction_semantics != _FORBIDDEN_DIRECTION_SEMANTICS_V2:
            raise ValueError("forbidden direction-semantics roster and order must remain exact")
        if self.comparable_states != ("observed_value", "observed_zero"):
            raise ValueError("percentiles admit only comparable observed states")
        if self.policy_digest != _ACCEPTED_EXPERT_EVIDENCE_POLICY_DIGEST_V2:
            raise ValueError("v2 evidence policy digest must match the independently accepted pin")
        if self.policy_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("v2 evidence policy digest must bind all derivation rules")
        return self


class UnsupportedInferenceV2(ContractModel):
    """Explicit not-captured construct boundary with no numeric representation."""

    inference_id: NonEmptyString
    label: NonEmptyString
    definition: NonEmptyString
    evidence_class: Literal["UNSUPPORTED_INFERENCE"] = "UNSUPPORTED_INFERENCE"
    availability: Literal[EvidenceAvailabilityV2.NOT_CAPTURED]
    limitation: NonEmptyString


class ParticipantExpertEvidenceBundleV2(ContractModel):
    """One self-digested participant-safe v2 player evidence panel."""

    schema_version: Literal[2] = 2
    evidence_version: Literal["w10-expert-evidence-presentation-v2"]
    policy_digest: Sha256Digest
    canonical_build_id: Sha256Digest
    matrix_version: NonEmptyString
    matrix_digest: Sha256Digest
    context: EvidencePlayerContextV2
    md_subrubric: MdEvidenceSubrubricV2 | None
    w09_inputs: EvidenceFamilyV2
    independent_descriptors: tuple[EvidenceFamilyV2, ...]
    unsupported_inferences: tuple[UnsupportedInferenceV2, ...]
    glossary: tuple[EvidenceGlossaryEntryV2, ...]
    bundle_digest: Sha256Digest
    claim_boundary: ClaimBoundary = EXPERT_RELEVANCE_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"bundle_digest"})

    @model_validator(mode="after")
    def bundle_is_coherent(self) -> Self:
        expected_policy_digest = _ACCEPTED_EXPERT_EVIDENCE_BUNDLE_PINS_V2.get(
            (self.canonical_build_id, self.matrix_version, self.matrix_digest)
        )
        if expected_policy_digest != self.policy_digest:
            raise ValueError("v2 evidence pins do not bind an accepted policy issue")
        if self.w09_inputs.family_id != "W09-INPUT-01" or (
            self.w09_inputs.purpose is not EvidencePurposeV2.W09_INPUT
        ):
            raise ValueError("v2 evidence requires one exact W09 input family")
        if not self.w09_inputs.mandatory_for_selected_rubric:
            raise ValueError("the exact W09 input family must remain mandatory transparency")
        if any(
            family.purpose is not EvidencePurposeV2.INDEPENDENT_DESCRIPTOR
            for family in self.independent_descriptors
        ):
            raise ValueError("independent descriptor family purpose drifted")
        family_ids = tuple(family.family_id for family in self.independent_descriptors)
        if family_ids != _INDEPENDENT_FAMILY_ORDER_V2:
            raise ValueError("independent evidence families must use the exact ordered roster")
        if (self.context.position_code == "MD") != (self.md_subrubric is not None):
            raise ValueError("MD evidence requires one explicit comparable sub-rubric")
        mandatory = set(
            mandatory_independent_family_ids_v2(self.context.position_code, self.md_subrubric)
        )
        marked_mandatory = {
            family.family_id
            for family in self.independent_descriptors
            if family.mandatory_for_selected_rubric
        }
        if marked_mandatory != mandatory:
            raise ValueError("position/sub-rubric mandatory family roster drifted")
        inference_ids = tuple(item.inference_id for item in self.unsupported_inferences)
        if inference_ids != (
            *_COMMON_UNSUPPORTED_IDS_V2,
            *_POSITION_UNSUPPORTED_IDS_V2[self.context.position_code],
        ):
            raise ValueError("position-specific unsupported-inference roster or order drifted")
        metric_rows = (self.w09_inputs.metrics,) + tuple(
            family.metrics for family in self.independent_descriptors
        )
        metrics = tuple(metric for rows in metric_rows for metric in rows)
        glossary_ids = tuple(item.metric_id for item in self.glossary)
        if glossary_ids != tuple(metric.metric_id for metric in metrics):
            raise ValueError("glossary must cover every displayed metric in display order")
        if any(
            glossary.label != metric.label
            or glossary.definition != metric.definition
            or glossary.coverage_definition != metric.coverage.definition
            or glossary.purpose is not metric.purpose
            or glossary.used_by_w09_ranking != metric.used_by_w09_ranking
            for glossary, metric in zip(self.glossary, metrics, strict=True)
        ):
            raise ValueError("glossary content must exactly reconstruct from its metric")
        if self.bundle_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("v2 bundle digest must bind exact participant-safe evidence")
        return self


class ParticipantEvidenceComparisonV2(ContractModel):
    """The exact participant-safe exemplar/candidate pair authority."""

    schema_version: Literal[2] = 2
    comparison_version: Literal["w10-expert-evidence-comparison-v2"]
    policy_digest: Sha256Digest
    position_code: PositionCode
    md_subrubric: MdEvidenceSubrubricV2 | None
    exemplar: ParticipantExpertEvidenceBundleV2
    candidate: ParticipantExpertEvidenceBundleV2
    comparison_digest: Sha256Digest
    claim_boundary: ClaimBoundary = EXPERT_RELEVANCE_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"comparison_digest"})

    @model_validator(mode="after")
    def comparison_is_exact(self) -> Self:
        panels = (self.exemplar, self.candidate)
        if self.exemplar.bundle_digest == self.candidate.bundle_digest:
            raise ValueError("comparison exemplar and candidate must be distinct panels")
        if any(
            panel.context.position_code != self.position_code
            or panel.policy_digest != self.policy_digest
            or panel.evidence_version != "w10-expert-evidence-presentation-v2"
            or panel.md_subrubric is not self.md_subrubric
            for panel in panels
        ):
            raise ValueError("comparison panels must share exact position, policy and MD branch")
        if (
            self.exemplar.context.season_label != self.candidate.context.season_label
            or self.exemplar.context.window_start_utc != self.candidate.context.window_start_utc
            or self.exemplar.context.window_end_utc != self.candidate.context.window_end_utc
        ):
            raise ValueError("comparison panels must share the exact historical evidence window")

        def family_semantics(family: EvidenceFamilyV2) -> tuple[Any, ...]:
            return (
                family.family_id,
                family.label,
                family.definition,
                family.purpose,
                family.used_by_w09_ranking,
                family.exact_family_predicate,
                family.threshold_policy_version,
                family.threshold_rationale,
                family.mandatory_for_selected_rubric,
                tuple(
                    (
                        component.component_id,
                        component.exact_predicate,
                        component.opportunity_floor,
                        component.coverage.definition,
                    )
                    for component in family.opportunity_components
                ),
                tuple(
                    (
                        metric.metric_id,
                        metric.label,
                        metric.definition,
                        metric.purpose,
                        metric.used_by_w09_ranking,
                        metric.unit,
                        metric.exact_predicate,
                        metric.coverage.definition,
                        metric.position_reference,
                        metric.derivation_version,
                        metric.limitation,
                    )
                    for metric in family.metrics
                ),
            )

        semantic_families = tuple(
            tuple(
                family_semantics(family)
                for family in (panel.w09_inputs, *panel.independent_descriptors)
            )
            for panel in panels
        )
        if semantic_families[0] != semantic_families[1]:
            raise ValueError("comparison panels must use symmetric evidence semantics")
        if self.exemplar.glossary != self.candidate.glossary:
            raise ValueError("comparison panels must share one exact evidence glossary")
        if self.exemplar.unsupported_inferences != self.candidate.unsupported_inferences:
            raise ValueError("comparison panels must share exact unsupported-inference semantics")
        mandatory_independent_family_ids_v2(self.position_code, self.md_subrubric)
        if self.comparison_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("comparison digest must bind the exact evidence pair")
        return self


class EvidenceSufficiencyV2(StrEnum):
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"


class AssessmentBasisV2(StrEnum):
    SUPPLIED_EVIDENCE = "supplied_evidence"
    PRIOR_PROFESSIONAL_KNOWLEDGE = "prior_professional_knowledge"
    BOTH = "both"
    UNABLE_TO_ASSESS = "unable_to_assess"


class EvidenceGapV2(StrEnum):
    SPARSE_OPPORTUNITIES = "sparse_opportunities"
    MISSING_DESCRIPTOR = "missing_descriptor"
    COVERAGE_LIMITATION = "coverage_limitation"
    CONTEXT_AMBIGUITY = "context_ambiguity"
    OTHER = "other"


class CandidateEvidenceJudgementV2(ContractModel):
    """Separate v2 response semantics; v1 judgement bytes remain unchanged."""

    schema_version: Literal[2] = 2
    response_version: Literal["w10-expert-evidence-response-v2"]
    judgement_id: StrictUuid
    session_id: StrictUuid
    participant_id: StrictUuid
    presentation_id: StrictUuid
    query_id: StrictUuid
    candidate_id: StrictUuid
    comparison_digest: Sha256Digest
    position_code: PositionCode
    md_subrubric: MdEvidenceSubrubricV2 | None
    state: JudgementState
    evidence_sufficiency: EvidenceSufficiencyV2
    assessment_basis: AssessmentBasisV2
    relevance_rating: RelevanceRating | None = None
    confidence: ConfidenceRating | None = None
    evidence_gap: EvidenceGapV2 | None = None
    cited_independent_family_ids: tuple[IndependentFamilyIdV2, ...]
    explanation: NonEmptyString | None = None
    recorded_at: UtcInstant
    judgement_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"judgement_digest"})

    @model_validator(mode="after")
    def response_is_construct_valid(self) -> Self:
        if len(self.cited_independent_family_ids) != len(set(self.cited_independent_family_ids)):
            raise ValueError("cited independent descriptor families must be unique")
        mandatory = set(mandatory_independent_family_ids_v2(self.position_code, self.md_subrubric))
        if not set(self.cited_independent_family_ids).issubset(mandatory):
            raise ValueError("response citations must be a subset of its mandatory family roster")
        if self.state is JudgementState.RATED:
            if self.relevance_rating is None or self.confidence is None:
                raise ValueError("rated v2 responses require relevance and confidence")
            if self.evidence_sufficiency is not EvidenceSufficiencyV2.SUFFICIENT:
                raise ValueError("rated v2 responses require sufficient evidence")
        elif self.relevance_rating is not None or self.confidence is not None:
            raise ValueError("abstain/unable v2 responses cannot carry ratings")
        if self.state is JudgementState.UNABLE_TO_ASSESS:
            if (
                self.evidence_sufficiency is not EvidenceSufficiencyV2.INSUFFICIENT
                or self.assessment_basis is not AssessmentBasisV2.UNABLE_TO_ASSESS
            ):
                raise ValueError("unable responses require explicit insufficient evidence")
        elif self.assessment_basis is AssessmentBasisV2.UNABLE_TO_ASSESS:
            raise ValueError("unable assessment basis requires unable response state")
        if (self.evidence_sufficiency is EvidenceSufficiencyV2.INSUFFICIENT) != (
            self.evidence_gap is not None
        ):
            raise ValueError("insufficient evidence requires one qualitative evidence gap")
        if self.evidence_sufficiency is EvidenceSufficiencyV2.INSUFFICIENT and (
            self.explanation is None
        ):
            raise ValueError("insufficient evidence requires a qualitative explanation")
        uses_supplied = self.assessment_basis in {
            AssessmentBasisV2.SUPPLIED_EVIDENCE,
            AssessmentBasisV2.BOTH,
        }
        if uses_supplied and not self.cited_independent_family_ids:
            raise ValueError(
                "supplied-evidence responses must cite an independent descriptor family"
            )
        if not uses_supplied and self.cited_independent_family_ids:
            raise ValueError(
                "prior-knowledge/unable responses cannot cite supplied descriptor families"
            )
        if self.judgement_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("v2 judgement digest must bind exact response semantics")
        return self


class HistoricalComparisonJudgementV1(ContractModel):
    """Response contract for the participant-language pilot presentation.

    The football-relevance semantics intentionally inherit the accepted v2
    construct checks.  The distinct version prevents the reworked instrument
    from being confused with responses captured by the stopped presentation.
    """

    schema_version: Literal[3] = 3
    response_version: Literal["historical-player-comparison-response-v1"]
    judgement_id: StrictUuid
    session_id: StrictUuid
    participant_id: StrictUuid
    presentation_id: StrictUuid
    query_id: StrictUuid
    candidate_id: StrictUuid
    comparison_digest: Sha256Digest
    position_code: PositionCode
    md_subrubric: MdEvidenceSubrubricV2 | None
    state: JudgementState
    evidence_sufficiency: EvidenceSufficiencyV2
    assessment_basis: AssessmentBasisV2
    relevance_rating: RelevanceRating | None = None
    confidence: ConfidenceRating | None = None
    evidence_gap: EvidenceGapV2 | None = None
    cited_independent_family_ids: tuple[IndependentFamilyIdV2, ...]
    statistics_used_to_find_similar_players_helped: bool
    explanation: NonEmptyString | None = None
    recorded_at: UtcInstant
    judgement_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"judgement_digest"})

    @model_validator(mode="after")
    def response_is_construct_valid(self) -> Self:
        if len(self.cited_independent_family_ids) != len(set(self.cited_independent_family_ids)):
            raise ValueError("cited additional-evidence sections must be unique")
        mandatory = set(mandatory_independent_family_ids_v2(self.position_code, self.md_subrubric))
        if not set(self.cited_independent_family_ids).issubset(mandatory):
            raise ValueError("response citations must be a subset of its mandatory family roster")
        if self.state is JudgementState.RATED:
            if self.relevance_rating is None or self.confidence is None:
                raise ValueError("rated responses require credibility and confidence")
            if self.evidence_sufficiency is not EvidenceSufficiencyV2.SUFFICIENT:
                raise ValueError("a fair rated comparison requires sufficient information")
        elif self.relevance_rating is not None or self.confidence is not None:
            raise ValueError("an unrated response cannot carry credibility or confidence")
        if self.state is JudgementState.UNABLE_TO_ASSESS:
            if (
                self.evidence_sufficiency is not EvidenceSufficiencyV2.INSUFFICIENT
                or self.assessment_basis is not AssessmentBasisV2.UNABLE_TO_ASSESS
            ):
                raise ValueError("unable responses require explicit insufficient information")
        elif self.assessment_basis is AssessmentBasisV2.UNABLE_TO_ASSESS:
            raise ValueError("unable assessment basis requires unable response state")
        if (self.evidence_sufficiency is EvidenceSufficiencyV2.INSUFFICIENT) != (
            self.evidence_gap is not None
        ):
            raise ValueError("missing important information requires one reason")
        if self.evidence_sufficiency is EvidenceSufficiencyV2.INSUFFICIENT and (
            self.explanation is None
        ):
            raise ValueError("missing important information requires an explanation")
        uses_supplied = self.assessment_basis in {
            AssessmentBasisV2.SUPPLIED_EVIDENCE,
            AssessmentBasisV2.BOTH,
        }
        if uses_supplied and not self.cited_independent_family_ids:
            raise ValueError("answers based on this form must cite Additional playing evidence")
        if not uses_supplied and (
            self.cited_independent_family_ids or self.statistics_used_to_find_similar_players_helped
        ):
            raise ValueError(
                "prior-knowledge or unable responses cannot cite information from the form"
            )
        if self.judgement_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("comparison response digest must bind the exact answers")
        return self


class HistoricalComparisonPilotDebriefV1(ContractModel):
    """Pilot usability evidence kept separate from football-relevance ratings."""

    schema_version: Literal[1] = 1
    debrief_version: Literal["historical-player-comparison-debrief-v1"]
    debrief_id: StrictUuid
    session_id: StrictUuid
    participant_id: StrictUuid
    names_or_minutes_only_for_any_comparison: bool
    names_or_minutes_only_details: NonEmptyString | None = None
    any_position_lacked_enough_evidence: bool
    position_evidence_details: NonEmptyString | None = None
    any_label_chart_warning_or_navigation_unclear: bool
    interface_clarity_details: NonEmptyString | None = None
    form_appeared_to_reveal_system_preference: bool
    preference_revelation_details: NonEmptyString | None = None
    recorded_at: UtcInstant
    debrief_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"debrief_digest"})

    @model_validator(mode="after")
    def debrief_is_exact(self) -> Self:
        pairs = (
            (
                self.names_or_minutes_only_for_any_comparison,
                self.names_or_minutes_only_details,
            ),
            (self.any_position_lacked_enough_evidence, self.position_evidence_details),
            (
                self.any_label_chart_warning_or_navigation_unclear,
                self.interface_clarity_details,
            ),
            (
                self.form_appeared_to_reveal_system_preference,
                self.preference_revelation_details,
            ),
        )
        if any(answer != (details is not None) for answer, details in pairs):
            raise ValueError("each yes pilot-feedback answer requires its own explanation")
        if self.debrief_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("pilot debrief digest must bind the exact usability responses")
        return self


def validate_response_comparison_v2(
    response: CandidateEvidenceJudgementV2 | HistoricalComparisonJudgementV1,
    comparison: ParticipantEvidenceComparisonV2,
) -> None:
    """Fail closed unless a response binds the exact pair and observed mandatory evidence."""

    if (
        response.comparison_digest != comparison.comparison_digest
        or response.position_code != comparison.position_code
        or response.md_subrubric is not comparison.md_subrubric
    ):
        raise ValueError("response does not bind the exact evidence comparison")
    families_by_panel = tuple(
        {family.family_id: family for family in panel.independent_descriptors}
        for panel in (comparison.exemplar, comparison.candidate)
    )
    observed = {
        EvidenceAvailabilityV2.OBSERVED_VALUE,
        EvidenceAvailabilityV2.OBSERVED_ZERO,
    }
    if any(
        families[family_id].availability not in observed
        or not families[family_id].mandatory_for_selected_rubric
        for family_id in response.cited_independent_family_ids
        for families in families_by_panel
    ):
        raise ValueError("response cites evidence not observed and mandatory in both panels")


class ParticipantEligibility(ContractModel):
    schema_version: SchemaVersion = 1
    participant_id: StrictUuid
    participant_code_digest: Sha256Digest
    assessed_at: UtcInstant
    years_experience: NonNegativeInt
    experience_kinds: Annotated[tuple[ExpertExperienceKind, ...], Field(min_length=1)]
    assessed_players_within_window: bool
    conflict_declared: bool
    conflict_note: NonEmptyString | None = None
    eligible: bool
    eligibility_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"eligibility_digest"})

    @model_validator(mode="after")
    def eligibility_is_coherent(self) -> Self:
        if len(self.experience_kinds) != len(set(self.experience_kinds)):
            raise ValueError("participant experience kinds must be unique")
        if self.conflict_declared != (self.conflict_note is not None):
            raise ValueError("conflict note must match declared conflict state")
        if self.eligibility_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("eligibility digest is incompatible")
        return self


class ConsentRecord(ContractModel):
    schema_version: SchemaVersion = 1
    consent_id: StrictUuid
    participant_id: StrictUuid
    protocol_digest: Sha256Digest
    query_pack_digest: Sha256Digest
    consented_at: UtcInstant
    voluntary_participation: bool
    local_pseudonymous_storage: bool
    withdrawal_before_submission_understood: bool
    immutable_after_submission_understood: bool
    research_limitations_understood: bool
    consent_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"consent_digest"})

    @model_validator(mode="after")
    def consent_is_coherent(self) -> Self:
        decisions = (
            self.voluntary_participation,
            self.local_pseudonymous_storage,
            self.withdrawal_before_submission_understood,
            self.immutable_after_submission_understood,
            self.research_limitations_understood,
        )
        if not all(decisions):
            raise ValueError("every consent item must be explicitly accepted")
        if self.consent_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("consent digest is incompatible")
        return self


class CandidatePresentation(ContractModel):
    presentation_id: StrictUuid
    query_id: StrictUuid
    candidate_id: StrictUuid
    presentation_ordinal: PositiveInt
    kind: PresentationKind
    repeat_of_presentation_id: StrictUuid | None = None

    @model_validator(mode="after")
    def repeat_is_coherent(self) -> Self:
        if (self.kind is PresentationKind.REPEAT) != (self.repeat_of_presentation_id is not None):
            raise ValueError("repeat presentation must bind its primary presentation")
        return self


_PRESENTATION_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:expert-study-presentation:v1",
)


def _schedule_order(key: str, value: UUID | int | str) -> bytes:
    return hashlib.sha256(f"{key}\0{value}".encode()).digest()


def participant_keyed_candidate_order[T: UUID | str](
    participant_digest: str,
    candidate_ids: Sequence[T],
) -> tuple[T, ...]:
    """Return a provenance-blind participant-keyed candidate permutation."""

    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("participant-keyed candidate identities must be unique")
    return tuple(
        sorted(
            candidate_ids,
            key=lambda candidate_id: _schedule_order(participant_digest, candidate_id),
        )
    )


def build_formal_candidate_presentations(
    presentation: ExpertStudyPresentationBundle,
    *,
    session_id: UUID,
    participant_digest: str,
) -> tuple[CandidatePresentation, ...]:
    """Reconstruct the exact frozen participant-keyed formal schedule."""

    if presentation.schedule_rule != "w10-participant-keyed-interleaved-v1":
        raise ValueError("unsupported formal presentation schedule rule")
    formal_anchor_ids = frozenset(presentation.repeat_anchor_candidate_ids)
    ordered_queries = tuple(
        sorted(
            presentation.queries,
            key=lambda item: (
                0
                if any(candidate.candidate_id in formal_anchor_ids for candidate in item.candidates)
                else 1,
                _schedule_order(participant_digest, item.query_id),
            ),
        )
    )
    primary: list[CandidatePresentation] = []
    for query in ordered_queries:
        candidate_by_id = {item.candidate_id: item for item in query.candidates}
        candidate_ids = participant_keyed_candidate_order(
            f"{participant_digest}\0{query.query_id}",
            tuple(candidate_by_id),
        )
        for candidate_id in candidate_ids:
            candidate = candidate_by_id[candidate_id]
            presentation_id = uuid5(
                _PRESENTATION_NAMESPACE,
                f"{session_id}\0primary\0{query.query_id}\0{candidate.candidate_id}",
            )
            primary.append(
                CandidatePresentation(
                    presentation_id=presentation_id,
                    query_id=query.query_id,
                    candidate_id=candidate.candidate_id,
                    presentation_ordinal=len(primary) + 1,
                    kind=PresentationKind.PRIMARY,
                    repeat_of_presentation_id=None,
                )
            )
    primary_by_candidate = {item.candidate_id: item for item in primary}
    try:
        repeat_anchors = tuple(
            sorted(
                (
                    primary_by_candidate[candidate_id]
                    for candidate_id in presentation.repeat_anchor_candidate_ids
                ),
                key=lambda item: _schedule_order(
                    f"{participant_digest}\0formal-repeat-order",
                    item.candidate_id,
                ),
            )
        )
    except KeyError as exc:
        raise ValueError("formal repeat anchor is absent from presentations") from exc

    repeat_slots: dict[int, CandidatePresentation] = {}
    for anchor in repeat_anchors:
        candidate_slots = tuple(
            slot
            for slot in range(
                anchor.presentation_ordinal + presentation.minimum_repeat_primary_delay,
                len(primary),
            )
            if slot not in repeat_slots
        )
        if not candidate_slots:
            raise ValueError("participant-keyed repeat has no delayed nonterminal slot")
        slot = min(
            candidate_slots,
            key=lambda value: _schedule_order(
                f"{participant_digest}\0repeat-slot\0{anchor.candidate_id}",
                value,
            ),
        )
        repeat_slots[slot] = anchor

    scheduled: list[CandidatePresentation] = []
    for primary_count, item in enumerate(primary, start=1):
        scheduled.append(item.model_copy(update={"presentation_ordinal": len(scheduled) + 1}))
        placed_anchor = repeat_slots.get(primary_count)
        if placed_anchor is not None:
            scheduled.append(
                CandidatePresentation(
                    presentation_id=uuid5(
                        _PRESENTATION_NAMESPACE,
                        f"{session_id}\0repeat\0{placed_anchor.presentation_id}",
                    ),
                    query_id=placed_anchor.query_id,
                    candidate_id=placed_anchor.candidate_id,
                    presentation_ordinal=len(scheduled) + 1,
                    kind=PresentationKind.REPEAT,
                    repeat_of_presentation_id=placed_anchor.presentation_id,
                )
            )
    if (
        presentation.repeat_must_be_nonterminal
        and scheduled[-1].kind is not PresentationKind.PRIMARY
    ):
        raise ValueError("formal repeat schedule must be nonterminal")
    if presentation.repeats_must_be_nonadjacent and any(
        left.kind is PresentationKind.REPEAT and right.kind is PresentationKind.REPEAT
        for left, right in zip(scheduled, scheduled[1:], strict=False)
    ):
        raise ValueError("formal repeats must be nonadjacent")
    return tuple(scheduled)


class StudySession(ContractModel):
    schema_version: SchemaVersion = 1
    session_id: StrictUuid
    mode: StudyMode
    participant_id: StrictUuid
    protocol_digest: Sha256Digest
    query_pack_digest: Sha256Digest
    approval_digest: Sha256Digest | None
    eligibility_digest: Sha256Digest
    consent_digest: Sha256Digest
    started_at: UtcInstant
    last_activity_at: UtcInstant
    presentations: Annotated[tuple[CandidatePresentation, ...], Field(min_length=1)]
    submitted_at: UtcInstant | None = None

    @model_validator(mode="after")
    def session_is_coherent(self) -> Self:
        if self.last_activity_at < self.started_at:
            raise ValueError("session activity cannot precede its start")
        if self.submitted_at is not None and self.submitted_at < self.last_activity_at:
            raise ValueError("submission cannot precede latest activity")
        if self.mode is StudyMode.FORMAL_G_RW4 and self.approval_digest is None:
            raise ValueError("formal sessions require exact protocol approval")
        if self.mode is not StudyMode.FORMAL_G_RW4 and self.approval_digest is not None:
            raise ValueError("non-formal sessions cannot carry formal approval")
        ordinals = tuple(item.presentation_ordinal for item in self.presentations)
        if sorted(ordinals) != list(range(1, len(ordinals) + 1)):
            raise ValueError("presentation ordinals must be contiguous from one")
        ids = tuple(item.presentation_id for item in self.presentations)
        if len(ids) != len(set(ids)):
            raise ValueError("presentation identities must be unique")
        by_id = {item.presentation_id: item for item in self.presentations}
        for item in self.presentations:
            if item.kind is not PresentationKind.REPEAT:
                continue
            repeat_reference = item.repeat_of_presentation_id
            if repeat_reference is None:
                raise ValueError("repeat presentation must bind its primary presentation")
            primary = by_id.get(repeat_reference)
            if primary is None or primary.kind is not PresentationKind.PRIMARY:
                raise ValueError("repeat presentation must reference a primary presentation")
            if primary.presentation_ordinal >= item.presentation_ordinal:
                raise ValueError("repeat presentation must follow its primary")
            if primary.query_id != item.query_id or primary.candidate_id != item.candidate_id:
                raise ValueError("repeat presentation must preserve query and candidate identity")
        return self


class CandidateJudgement(ContractModel):
    schema_version: SchemaVersion = 1
    judgement_id: StrictUuid
    session_id: StrictUuid
    participant_id: StrictUuid
    presentation_id: StrictUuid
    query_id: StrictUuid
    candidate_id: StrictUuid
    state: JudgementState
    relevance_rating: RelevanceRating | None = None
    confidence: ConfidenceRating | None = None
    failure_category: QualitativeFailureCategory | None = None
    explanation: NonEmptyString | None = None
    recorded_at: UtcInstant
    judgement_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"judgement_digest"})

    @model_validator(mode="after")
    def judgement_is_coherent(self) -> Self:
        if self.state is JudgementState.RATED:
            if self.relevance_rating is None or self.confidence is None:
                raise ValueError("rated judgements require relevance and confidence")
        elif self.relevance_rating is not None or self.confidence is not None:
            raise ValueError("abstain/unable judgements cannot carry ratings")
        if self.judgement_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("judgement digest is incompatible")
        return self


class FormalStudySubmission(ContractModel):
    schema_version: SchemaVersion = 1
    submission_id: StrictUuid
    mode: Literal[StudyMode.FORMAL_G_RW4]
    session_id: StrictUuid
    participant_id: StrictUuid
    protocol_digest: Sha256Digest
    query_pack_digest: Sha256Digest
    approval_digest: Sha256Digest
    w09_pins: ResearchVersionPins
    session: StudySession
    eligibility: ParticipantEligibility
    consent: ConsentRecord
    submitted_at: UtcInstant
    judgements: Annotated[tuple[CandidateJudgement, ...], Field(min_length=1)]
    submission_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"submission_digest"})

    @model_validator(mode="after")
    def submission_is_coherent(self) -> Self:
        if self.session.mode is not StudyMode.FORMAL_G_RW4:
            raise ValueError("formal submissions require a formal session")
        if self.session.session_id != self.session_id:
            raise ValueError("embedded session identity does not match submission")
        if self.session.participant_id != self.participant_id:
            raise ValueError("embedded session participant does not match submission")
        if self.session.protocol_digest != self.protocol_digest:
            raise ValueError("embedded session protocol does not match submission")
        if self.session.query_pack_digest != self.query_pack_digest:
            raise ValueError("embedded session query pack does not match submission")
        if self.session.approval_digest != self.approval_digest:
            raise ValueError("embedded session approval does not match submission")
        if self.session.eligibility_digest != self.eligibility.eligibility_digest:
            raise ValueError("embedded session eligibility does not match submission")
        if self.session.consent_digest != self.consent.consent_digest:
            raise ValueError("embedded session consent does not match submission")
        if self.session.submitted_at != self.submitted_at:
            raise ValueError("embedded session submission time does not match submission")
        if len(self.session.presentations) != 82:
            raise ValueError("W10 formal submission requires exactly 82 presentations")
        if sum(item.kind is PresentationKind.PRIMARY for item in self.session.presentations) != 80:
            raise ValueError("W10 formal submission requires exactly 80 primary presentations")
        if sum(item.kind is PresentationKind.REPEAT for item in self.session.presentations) != 2:
            raise ValueError("W10 formal submission requires exactly two repeat presentations")
        if not self.eligibility.eligible:
            raise ValueError("formal submissions require an eligible participant")
        if self.eligibility.participant_id != self.participant_id:
            raise ValueError("eligibility participant does not match submission")
        if self.consent.participant_id != self.participant_id:
            raise ValueError("consent participant does not match submission")
        if self.consent.protocol_digest != self.protocol_digest:
            raise ValueError("consent protocol does not match submission")
        if self.consent.query_pack_digest != self.query_pack_digest:
            raise ValueError("consent query pack does not match submission")
        judgement_ids = tuple(value.judgement_id for value in self.judgements)
        presentation_ids = tuple(value.presentation_id for value in self.judgements)
        if len(judgement_ids) != len(set(judgement_ids)):
            raise ValueError("submission judgement identities must be unique")
        if len(presentation_ids) != len(set(presentation_ids)):
            raise ValueError("submission must contain one judgement per presentation")
        presentations_by_id = {value.presentation_id: value for value in self.session.presentations}
        if set(presentation_ids) != set(presentations_by_id):
            raise ValueError("submission judgements must cover every frozen presentation")
        if any(
            value.session_id != self.session_id or value.participant_id != self.participant_id
            for value in self.judgements
        ):
            raise ValueError("submission judgements must bind its session and participant")
        if any(
            value.query_id != presentations_by_id[value.presentation_id].query_id
            or value.candidate_id != presentations_by_id[value.presentation_id].candidate_id
            for value in self.judgements
        ):
            raise ValueError("submission judgements must match their frozen presentations")
        if self.submission_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("submission digest is incompatible")
        return self


class CompletionReceipt(ContractModel):
    schema_version: SchemaVersion = 1
    receipt_id: StrictUuid
    submission_id: StrictUuid
    participant_id: StrictUuid
    protocol_digest: Sha256Digest
    query_pack_digest: Sha256Digest
    submission_digest: Sha256Digest
    issued_at: UtcInstant
    formal_evidence_recorded: Literal[True]
    receipt_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"receipt_digest"})

    @model_validator(mode="after")
    def receipt_is_coherent(self) -> Self:
        if self.receipt_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("completion receipt digest is incompatible")
        return self


class RateContrastEvidence(ContractModel):
    retrieved_relevant_count: NonNegativeInt
    retrieved_rated_count: PositiveInt
    retrieved_rate: UnitInterval
    control_relevant_count: NonNegativeInt
    control_rated_count: PositiveInt
    control_rate: UnitInterval

    @model_validator(mode="after")
    def evidence_is_coherent(self) -> Self:
        if self.retrieved_relevant_count > self.retrieved_rated_count:
            raise ValueError("retrieved relevant count cannot exceed rated count")
        if self.control_relevant_count > self.control_rated_count:
            raise ValueError("control relevant count cannot exceed rated count")
        if self.retrieved_rate != self.retrieved_relevant_count / self.retrieved_rated_count:
            raise ValueError("retrieved rate must equal its declared counts")
        if self.control_rate != self.control_relevant_count / self.control_rated_count:
            raise ValueError("control rate must equal its declared counts")
        return self


class MetricValue(ContractModel):
    metric_name: NonEmptyString
    value: FiniteScore | None
    numerator: Annotated[int, Field(strict=True)]
    denominator: NonNegativeInt
    supported: bool
    limitation: NonEmptyString | None = None
    rate_contrast: RateContrastEvidence | None = None

    @model_validator(mode="after")
    def metric_is_coherent(self) -> Self:
        if self.supported != (self.value is not None):
            raise ValueError("supported metric must have exactly one value")
        if not self.supported and self.limitation is None:
            raise ValueError("unsupported metrics require a limitation")
        if self.denominator == 0 and self.supported:
            raise ValueError("zero-denominator metrics cannot be authoritative")
        is_supported_lift = (
            self.metric_name == "retrieved_control_relevant_rate_lift" and self.supported
        )
        if is_supported_lift != (self.rate_contrast is not None):
            raise ValueError("supported relevant-rate lift requires exact two-arm evidence")
        if self.rate_contrast is not None:
            exact_lift = Fraction(
                self.rate_contrast.retrieved_relevant_count,
                self.rate_contrast.retrieved_rated_count,
            ) - Fraction(
                self.rate_contrast.control_relevant_count,
                self.rate_contrast.control_rated_count,
            )
            if (
                self.value != float(exact_lift)
                or self.numerator != exact_lift.numerator
                or self.denominator != exact_lift.denominator
            ):
                raise ValueError("lift value must equal its exact declared evidence")
        return self


class SubgroupResult(ContractModel):
    dimension: NonEmptyString
    value: NonEmptyString
    participant_count: NonNegativeInt
    query_count: NonNegativeInt
    rated_judgement_count: NonNegativeInt
    relevant_judgement_count: NonNegativeInt
    retrieved_precision_at_k: FiniteScore | None
    mean_ndcg_at_k: FiniteScore | None


class ExpertRelevanceStudyResult(ContractModel):
    schema_version: SchemaVersion = 1
    result_id: StrictUuid
    protocol_digest: Sha256Digest
    query_pack_digest: Sha256Digest
    approval_digest: Sha256Digest | None
    evaluated_at: UtcInstant
    included_submission_digests: tuple[Sha256Digest, ...]
    excluded_submission_count: NonNegativeInt
    eligible_participant_count: NonNegativeInt
    completed_participant_count: NonNegativeInt
    query_count: NonNegativeInt
    candidate_count: NonNegativeInt
    rated_judgement_count: NonNegativeInt
    abstention_count: NonNegativeInt
    unable_to_assess_count: NonNegativeInt
    missing_judgement_count: NonNegativeInt
    metrics: tuple[MetricValue, ...]
    position_subgroups: tuple[SubgroupResult, ...]
    competition_subgroups: tuple[SubgroupResult, ...]
    confidence_distribution: tuple[
        NonNegativeInt, NonNegativeInt, NonNegativeInt, NonNegativeInt, NonNegativeInt
    ]
    qualitative_failure_categories: dict[QualitativeFailureCategory, NonNegativeInt]
    decision: ExpertGateDecisionKind
    decision_reasons: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    negative_result_retained: Literal[True]
    result_digest: Sha256Digest
    claim_boundary: ClaimBoundary = EXPERT_RELEVANCE_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"result_digest"})

    @model_validator(mode="after")
    def result_is_coherent(self) -> Self:
        if len(self.included_submission_digests) != len(set(self.included_submission_digests)):
            raise ValueError("included formal submissions must be unique")
        metric_names = tuple(metric.metric_name for metric in self.metrics)
        if len(metric_names) != len(set(metric_names)):
            raise ValueError("result metric names must be unique")
        if sum(self.confidence_distribution) > self.rated_judgement_count:
            raise ValueError("confidence distribution cannot exceed rated judgements")
        if self.result_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("study result digest is incompatible")
        return self


def participant_code_digest(code: str) -> Sha256Digest:
    """Return a one-way canonical identity for an uppercase pseudonymous code."""

    if type(code) is not str or _PARTICIPANT_CODE.fullmatch(code) is None:
        raise ValueError("participant code must be 6-32 uppercase alphanumeric/hyphen characters")
    return canonical_research_digest({"participant_code": code})


__all__ = [
    "CandidateJudgement",
    "CandidateEvidenceJudgementV2",
    "CandidateOrigin",
    "CandidatePresentation",
    "CompletionReceipt",
    "ConsentRecord",
    "EvidenceBand",
    "EvidenceAvailabilityV2",
    "EvidenceGapV2",
    "EvidenceCoverageV2",
    "EvidenceFamilyV2",
    "EvidenceGlossaryEntryV2",
    "EvidenceMetricV2",
    "EvidenceMetricUnitV2",
    "EvidenceOpportunityComponentV2",
    "EvidenceOpportunityThresholdsV2",
    "EvidencePlayerContextV2",
    "EvidencePurposeV2",
    "EvidenceQuantityV2",
    "EvidenceSufficiencyV2",
    "EXPERT_RELEVANCE_CLAIM_BOUNDARY",
    "AssessmentBasisV2",
    "ExpertEligibilityProtocol",
    "ExpertEvidencePolicyV2",
    "ExpertExperienceKind",
    "ExpertGateDecisionKind",
    "ExpertGateThresholds",
    "ExpertRelevanceProtocol",
    "ExpertRelevanceStudyResult",
    "ExpertStudyPresentationBundle",
    "FormalStudySubmission",
    "FrozenCandidate",
    "FrozenExpertQuery",
    "FrozenExpertQueryPack",
    "HistoricalComparisonJudgementV1",
    "HistoricalComparisonPilotDebriefV1",
    "JudgementState",
    "MetricValue",
    "MdEvidenceSubrubricV2",
    "ParticipantEvidenceComparisonV2",
    "ParticipantEligibility",
    "ParticipantExpertEvidenceBundleV2",
    "PresentedCandidate",
    "PresentedExpertQuery",
    "PresentationKind",
    "ProtocolApproval",
    "QualitativeFailureCategory",
    "QueryDifficulty",
    "RatingAnchor",
    "StudyCompletionRules",
    "StudyMode",
    "StudySession",
    "SubgroupResult",
    "UnsupportedInferenceV2",
    "mandatory_independent_family_ids_v2",
    "participant_code_digest",
    "participant_keyed_candidate_order",
    "validate_response_comparison_v2",
]

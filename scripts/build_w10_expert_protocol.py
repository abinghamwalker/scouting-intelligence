"""Freeze the W10 expert-relevance protocol and blinded W09 query authority."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast
from uuid import NAMESPACE_URL, UUID, uuid5

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scouting.contracts.expert_relevance import (
    CandidateOrigin,
    EvidenceBand,
    ExpertEligibilityProtocol,
    ExpertExperienceKind,
    ExpertGateThresholds,
    ExpertRelevanceProtocol,
    ExpertStudyPresentationBundle,
    FrozenCandidate,
    FrozenExpertQuery,
    FrozenExpertQueryPack,
    PresentedCandidate,
    PresentedExpertQuery,
    QueryDifficulty,
    RatingAnchor,
    StudyCompletionRules,
)
from scouting.contracts.research import (
    FeatureMatrixRow,
    FeatureWeight,
    ResearchFilters,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    canonical_research_digest,
)
from scouting.serving.research import ResearchServingService
from scouting.storage.formats import canonical_json_bytes
from services.api.w09_main import load_production_w09_runtime

_BUILT_AT = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)
_GENERATED_AT = _BUILT_AT + timedelta(seconds=1)
_NAMESPACE = uuid5(NAMESPACE_URL, "urn:scouting-intelligence:w10:expert-relevance:v1")
_PROTOCOL_PATH = Path("configs/evaluation/w10-expert-relevance-protocol-v1.json")
_QUERY_PACK_PATH = Path("configs/evaluation/w10-frozen-query-pack-v1.json")
_PRESENTATION_PATH = Path("configs/evaluation/w10-expert-study-presentation-v1.json")
_EVIDENCE_MINUTES_BOUNDARY = 1_800.0
_SEASON_LABEL = "Retained 2017/18 historical competition season"


@dataclass(frozen=True, slots=True)
class QuerySpecification:
    code: str
    exemplar_grain_id: str
    evidence_band: EvidenceBand
    difficulty: QueryDifficulty


_QUERY_SPECIFICATIONS = (
    QuerySpecification(
        code="W10-Q01-ITALY-GK-HIGHER",
        exemplar_grain_id=(
            "player=003dec57-15d5-560d-99b4-7a250b47012d|"
            "competition=86c98bf2-f02b-5286-a13e-4bd614834ac0|season=181248"
        ),
        evidence_band=EvidenceBand.HIGHER,
        difficulty=QueryDifficulty.STRAIGHTFORWARD,
    ),
    QuerySpecification(
        code="W10-Q02-FRANCE-DF-LOWER",
        exemplar_grain_id=(
            "player=00ad914d-96ef-5d61-a297-16a2bb7c214f|"
            "competition=8cc4a37d-8bec-5972-a266-39e0d0286835|season=181189"
        ),
        evidence_band=EvidenceBand.LOWER,
        difficulty=QueryDifficulty.DIFFICULT,
    ),
    QuerySpecification(
        code="W10-Q03-GERMANY-MD-LOWER",
        exemplar_grain_id=(
            "player=009e8f08-f8ae-59f1-b263-85a4f086ddf9|"
            "competition=ed85774b-400d-5ab7-8868-22af34cc07ca|season=181137"
        ),
        evidence_band=EvidenceBand.LOWER,
        difficulty=QueryDifficulty.DIFFICULT,
    ),
    QuerySpecification(
        code="W10-Q04-SPAIN-FW-HIGHER",
        exemplar_grain_id=(
            "player=023b3e13-3cc7-50b7-9d93-afda3613983b|"
            "competition=f3fccd8e-2d90-598b-9ac0-e3b5f86bfc18|season=181144"
        ),
        evidence_band=EvidenceBand.HIGHER,
        difficulty=QueryDifficulty.STRAIGHTFORWARD,
    ),
    QuerySpecification(
        code="W10-Q05-ENGLAND-GK-LOWER",
        exemplar_grain_id=(
            "player=1eb4874b-ea0c-5589-8038-0c18a37aecf2|"
            "competition=cb5c5317-fa4a-571e-93dc-ef6ce482eab7|season=181150"
        ),
        evidence_band=EvidenceBand.LOWER,
        difficulty=QueryDifficulty.DIFFICULT,
    ),
    QuerySpecification(
        code="W10-Q06-SPAIN-DF-HIGHER",
        exemplar_grain_id=(
            "player=bdcdc190-ab89-58f8-9d2a-763f41df1f21|"
            "competition=f3fccd8e-2d90-598b-9ac0-e3b5f86bfc18|season=181144"
        ),
        evidence_band=EvidenceBand.HIGHER,
        difficulty=QueryDifficulty.STRAIGHTFORWARD,
    ),
    QuerySpecification(
        code="W10-Q07-ITALY-MD-HIGHER",
        exemplar_grain_id=(
            "player=ca6f3025-5a74-5b00-8166-55f7f5d21bad|"
            "competition=86c98bf2-f02b-5286-a13e-4bd614834ac0|season=181248"
        ),
        evidence_band=EvidenceBand.HIGHER,
        difficulty=QueryDifficulty.STRAIGHTFORWARD,
    ),
    QuerySpecification(
        code="W10-Q08-FRANCE-FW-LOWER",
        exemplar_grain_id=(
            "player=baf789bd-0ac7-55d3-a71d-ff35b65da209|"
            "competition=8cc4a37d-8bec-5972-a266-39e0d0286835|season=181189"
        ),
        evidence_band=EvidenceBand.LOWER,
        difficulty=QueryDifficulty.DIFFICULT,
    ),
)


def _uuid(label: str) -> UUID:
    return uuid5(_NAMESPACE, label)


def _with_digest(model: Any, model_type: type[Any], digest_field: str) -> Any:
    values = model.model_dump(mode="python", exclude={digest_field})
    values[digest_field] = canonical_research_digest(model.digest_projection())
    return model_type(**values)


def _protocol(service: ResearchServingService) -> ExpertRelevanceProtocol:
    draft = ExpertRelevanceProtocol.model_construct(
        protocol_id=_uuid("protocol"),
        protocol_version="w10-expert-relevance-protocol-v1",
        title="W10 football-expert relevance validation of historical similarity retrieval",
        research_question=(
            "For frozen historical player exemplars, do eligible football-domain experts rate "
            "the accepted W09 system's five most statistically similar same-position players "
            "as more football-relevant than five blinded governed controls?"
        ),
        relevance_definition=(
            "A candidate is relevant when the expert judges that the candidate's observed "
            "historical playing profile is a credible football comparison to the exemplar for "
            "role and style analysis. This is resemblance evidence only, not recruitment advice."
        ),
        limitations_notice=(
            "The study uses retained 2017/18 historical evidence, measures expert-perceived "
            "football relevance, and does not establish current ability, future performance, "
            "price, availability, squad fit, transfer suitability, or outcome improvement."
        ),
        consent_and_local_data_handling=(
            "Participation is voluntary. Eligibility, consent, ratings, confidence, optional "
            "football explanations, timestamps, and a one-way participant-code digest are stored "
            "only in local SQLite and immutable local evidence files. No name or contact detail is "
            "requested. A participant may stop before submission; formal submission is immutable."
        ),
        pseudonymous_identifier_policy=(
            "Use a participant-provided 6-32 character uppercase alphanumeric/hyphen code. Store "
            "only its canonical SHA-256 digest and a deterministic UUID derived from that digest."
        ),
        missing_response_policy=(
            "Abstain and unable-to-assess are explicit non-rated outcomes. Omitted presentations "
            "are missing. None enter relevance or NDCG numerators; all remain in coverage and "
            "missingness denominators. A formal participant completes only all 82 presentations."
        ),
        subgroup_reporting_policy=(
            "Report position and competition subgroups with exact participant, query, rated, and "
            "relevant denominators. Subgroups are descriptive and cannot override the primary gate."
        ),
        qualitative_reason_policy=(
            "Optional explanations and failure categories are retained verbatim locally, "
            "summarized by preregistered category counts, and never used to tune W09 on this "
            "protected partition."
        ),
        protected_label_policy=(
            "Formal labels are one-use protected evaluation evidence. They may be evaluated and "
            "reported, but never used for W09 training, ranking changes, query changes, threshold "
            "selection, or challenger development. Any later challenger requires a disjoint phase."
        ),
        threshold_freeze_policy=(
            "All query composition, inclusion rules, metrics, resampling settings, and PASS/FAIL/"
            "INSUFFICIENT_EVIDENCE thresholds are frozen under this digest before formal consent."
        ),
        participant_denominator_policy=(
            "Eligible participants with an immutable complete formal submission are included once. "
            "Pilot, development, ineligible, duplicate, stale, incomplete, or withdrawn records "
            "are excluded and counted. At least five eligible completed experts are required."
        ),
        query_denominator_policy=(
            "All eight frozen queries and all 80 primary candidates remain in coverage "
            "denominators. Each candidate requires at least three non-abstaining ratings. The two "
            "repeat presentations enter consistency metrics only and never relevance denominators."
        ),
        metric_policy=(
            "Mean 0-4 primary ratings define candidate gains. Per query, retrieved and control "
            "NDCG@5 use their frozen ranks and the ideal top five gains pooled across all ten, "
            "then macro-average over eight queries. Precision@5 macro-averages retrieved "
            "candidates' relevant-rating rates. Lift is the overall retrieved minus control "
            "relevant-rating rate. The primary effect is the eight paired NDCG deltas. A fully "
            "rated all-zero pooled query gives both arms NDCG 0.0 as complete negative evidence."
        ),
        repeat_question_policy=(
            "Two delayed blinded candidate repeats are participant-keyed and interleaved before "
            "the terminal presentation. Repeats are excluded from every relevance numerator and "
            "denominator and used only for mean absolute rating difference and within-one-point "
            "consistency among pairs with two rated answers. At least 80% of the expected repeat "
            "pairs must have two rated answers for the consistency metrics to be authoritative."
        ),
        pass_criteria=(
            "PASS requires exact authority and integrity, every completion rule, retrieved "  # nosec B106
            "precision@5 >= 0.60, mean retrieved NDCG@5 >= 0.65, retrieved-control relevant-rate "
            "lift >= 0.20, paired NDCG@5 delta >= 0.05 with paired 95% query-bootstrap lower bound "
            "> 0.0, ordinal agreement >= 0.40, repeat MAD <= 1.0, and repeat within-one >= 0.80."
        ),
        fail_criteria=(
            "FAIL applies to stale/substituted authority, protected-label leakage or reuse, or a "
            "complete compatible formal study that misses any preregistered PASS threshold. The "
            "negative result is immutable evidence and cannot authorize tuning on this partition."
        ),
        insufficient_evidence_criteria=(
            "INSUFFICIENT_EVIDENCE applies when formal approval or evidence is absent, fewer than "
            "five eligible experts complete all 82 presentations, any query/candidate lacks "
            "required coverage or three non-abstaining raters, fewer than 80% of expected repeat "
            "pairs have two rated answers, or a required metric has no valid denominator."
        ),
        eligibility=ExpertEligibilityProtocol(
            minimum_years_experience=2,
            accepted_experience=(
                ExpertExperienceKind.PROFESSIONAL_SCOUTING,
                ExpertExperienceKind.RECRUITMENT_ANALYSIS,
                ExpertExperienceKind.PERFORMANCE_ANALYSIS,
                ExpertExperienceKind.PROFESSIONAL_COACHING,
                ExpertExperienceKind.PROFESSIONAL_PLAYING,
            ),
            requires_recent_player_assessment=True,
            recent_assessment_window_years=5,
            conflict_policy=(
                "Declare present or recent professional responsibility for a displayed player or "
                "club. A material conflict makes the participant ineligible for the formal study; "
                "the declaration and optional note are retained locally."
            ),
        ),
        rating_anchors=(
            RatingAnchor(
                value=0, label="Not relevant", definition="No credible football comparison."
            ),
            RatingAnchor(
                value=1, label="Weak", definition="Only a remote or superficial comparison."
            ),
            RatingAnchor(
                value=2,
                label="Plausible",
                definition="Some useful similarity, with material mismatch.",
            ),
            RatingAnchor(
                value=3, label="Relevant", definition="A credible and useful role/style comparison."
            ),
            RatingAnchor(
                value=4,
                label="Strongly relevant",
                definition="A particularly strong role/style comparison.",
            ),
        ),
        confidence_minimum=1,
        confidence_maximum=5,
        completion=StudyCompletionRules(
            minimum_eligible_participants=5,
            required_query_count=8,
            candidate_depth_per_query=10,
            retrieved_candidates_per_query=5,
            control_candidates_per_query=5,
            repeated_judgements_per_participant=2,
            minimum_non_abstaining_raters_per_candidate=3,
            minimum_participant_completion_rate=1.0,
            minimum_query_coverage_rate=1.0,
            minimum_rated_repeat_pair_rate=0.80,
        ),
        thresholds=ExpertGateThresholds(
            relevant_rating_floor=3,
            minimum_retrieved_precision_at_k=0.60,
            minimum_mean_ndcg_at_k=0.65,
            minimum_retrieved_control_relevant_rate_lift=0.20,
            minimum_paired_ndcg_delta=0.05,
            paired_ndcg_confidence=0.95,
            paired_ndcg_bootstrap_resamples=2_000,
            paired_ndcg_bootstrap_seed=10_202_608,
            paired_ndcg_interval_method="paired_percentile_query_bootstrap",
            paired_ndcg_lower_bound_must_exceed=0.0,
            minimum_ordinal_agreement=0.40,
            ordinal_agreement_method=(
                "mean_pairwise_one_minus_absolute_rating_difference_over_four"
            ),
            maximum_repeat_mean_absolute_difference=1.0,
            minimum_repeat_within_one_rate=0.80,
            ndcg_k=5,
            precision_k=5,
        ),
        w09_pins=service.pins,
        protocol_digest="0" * 64,
    )
    return cast(
        ExpertRelevanceProtocol, _with_digest(draft, ExpertRelevanceProtocol, "protocol_digest")
    )


def _request(
    service: ResearchServingService,
    *,
    query_id: UUID,
    exemplar: FeatureMatrixRow,
) -> ResearchQueryRequest:
    weights = tuple(
        FeatureWeight(feature_name=name, weight=1.0)
        for name in service.index_manifest.feature_names
    )
    draft = ResearchQueryRequest.model_construct(
        query_id=query_id,
        requested_at=_BUILT_AT,
        feature_cutoff_ts=service.pins.feature_cutoff_ts,
        pins=service.pins,
        mode=ResearchQueryMode.EXEMPLAR,
        method=ResearchMethod.WEIGHTED_EUCLIDEAN,
        exemplar_grain_id=exemplar.grain_id,
        profile=(),
        weights=weights,
        filters=ResearchFilters(
            competition_id=exemplar.competition_id,
            season_id=exemplar.season_id,
            position_codes=(exemplar.position_code,),
        ),
        limit=5,
        query_digest="0" * 64,
    )
    return ResearchQueryRequest(
        **draft.model_dump(mode="python", exclude={"query_digest"}),
        query_digest=canonical_research_digest(draft.digest_projection()),
    )


def _candidate(
    *,
    query_id: UUID,
    row: FeatureMatrixRow,
    origin: CandidateOrigin,
    rank: int,
    score: float | None = None,
) -> FrozenCandidate:
    is_retrieved = origin is CandidateOrigin.RETRIEVED
    return FrozenCandidate(
        candidate_id=_uuid(f"candidate:{query_id}:{row.grain_id}"),
        grain_id=row.grain_id,
        player_id=row.player_id,
        display_name=row.display_name,
        competition_id=row.competition_id,
        competition_name=row.competition_name,
        season_id=row.season_id,
        position_code=row.position_code,
        team_names=row.team_names,
        minutes=row.minutes,
        origin=origin,
        retrieval_rank=rank if is_retrieved else None,
        retrieval_score=score if is_retrieved else None,
        control_rank=None if is_retrieved else rank,
        control_match_rule=(
            None
            if is_retrieved
            else (
                "same competition and position, plus the same frozen 1800-minute evidence band "
                "as the retrieved candidate at the paired rank; canonical hash order"
            )
        ),
    )


def _query_pack(service: ResearchServingService) -> FrozenExpertQueryPack:
    rows_by_grain = {row.grain_id: row for row in service.matrix_rows}
    frozen_queries: list[FrozenExpertQuery] = []
    for specification in _QUERY_SPECIFICATIONS:
        exemplar = rows_by_grain.get(specification.exemplar_grain_id)
        if exemplar is None:
            raise ValueError(f"accepted W09 exemplar is absent: {specification.code}")
        actual_band = (
            EvidenceBand.HIGHER
            if exemplar.minutes >= _EVIDENCE_MINUTES_BOUNDARY
            else EvidenceBand.LOWER
        )
        if actual_band is not specification.evidence_band:
            raise ValueError(f"frozen evidence band drifted: {specification.code}")
        query_id = _uuid(f"query:{specification.code}")
        request = _request(service, query_id=query_id, exemplar=exemplar)
        result = service.execute_query(request, generated_at=_GENERATED_AT)
        retrieved = tuple(
            _candidate(
                query_id=query_id,
                row=rows_by_grain[item.grain_id],
                origin=CandidateOrigin.RETRIEVED,
                rank=item.rank,
                score=item.score,
            )
            for item in result.candidates
        )
        excluded_grains = {exemplar.grain_id, *(item.grain_id for item in result.candidates)}
        control_pool = [
            row
            for row in service.matrix_rows
            if row.competition_id == exemplar.competition_id
            and row.position_code == exemplar.position_code
            and row.grain_id not in excluded_grains
        ]
        if len(retrieved) != 5:
            raise ValueError(f"frozen query has insufficient candidates: {specification.code}")
        chosen_controls: list[FeatureMatrixRow] = []
        for retrieved_candidate in result.candidates:
            retrieved_row = rows_by_grain[retrieved_candidate.grain_id]
            retrieved_higher_band = retrieved_row.minutes >= _EVIDENCE_MINUTES_BOUNDARY
            eligible_controls = [
                row
                for row in control_pool
                if row not in chosen_controls
                and (row.minutes >= _EVIDENCE_MINUTES_BOUNDARY) == retrieved_higher_band
            ]
            eligible_controls.sort(
                key=lambda row: canonical_research_digest(
                    {
                        "rule": "w10-governed-paired-control-canonical-hash-v1",
                        "query_id": str(query_id),
                        "retrieval_rank": retrieved_candidate.rank,
                        "grain_id": row.grain_id,
                    }
                )
            )
            if not eligible_controls:
                raise ValueError(
                    f"frozen query lacks a band-matched control: {specification.code} "
                    f"rank {retrieved_candidate.rank}"
                )
            chosen_controls.append(eligible_controls[0])
        frozen_controls = tuple(
            _candidate(
                query_id=query_id,
                row=row,
                origin=CandidateOrigin.CONTROL,
                rank=rank,
            )
            for rank, row in enumerate(chosen_controls, start=1)
        )
        draft = FrozenExpertQuery.model_construct(
            query_id=query_id,
            query_code=specification.code,
            w09_request_digest=result.request.query_digest,
            w09_result_id=result.result_id,
            w09_result_digest=result.result_digest,
            w09_generated_at=result.generated_at,
            exemplar_grain_id=exemplar.grain_id,
            exemplar_player_id=exemplar.player_id,
            exemplar_display_name=exemplar.display_name,
            exemplar_competition_id=exemplar.competition_id,
            exemplar_competition_name=exemplar.competition_name,
            exemplar_season_id=exemplar.season_id,
            exemplar_position_code=exemplar.position_code,
            exemplar_team_names=exemplar.team_names,
            exemplar_minutes=exemplar.minutes,
            evidence_band=specification.evidence_band,
            difficulty=specification.difficulty,
            football_prompt=(
                "Using only the historical information shown, rate how relevant each candidate is "
                "as a football role/style comparison to the exemplar. Do not infer current status, "
                "future performance, price, availability, squad fit, or transfer suitability."
            ),
            candidates=(*retrieved, *frozen_controls),
            query_digest="0" * 64,
        )
        frozen_queries.append(
            cast(FrozenExpertQuery, _with_digest(draft, FrozenExpertQuery, "query_digest"))
        )
    draft_pack = FrozenExpertQueryPack.model_construct(
        query_pack_id=_uuid("query-pack"),
        query_pack_version="w10-frozen-query-pack-v1",
        built_at=_BUILT_AT,
        w09_pins=service.pins,
        query_selection_rule=(
            "Eight named real W09 exemplars: two per position, four lower/four higher 1800-minute "
            "bands, four straightforward/four difficult, covering every retained competition."
        ),
        control_selection_rule=(
            "For each exemplar, exclude exemplar and retrieved rows; retain same competition, "
            "position and the paired retrieved row's frozen 1800-minute evidence band; select one "
            "per retrieval rank by canonical salted grain digest without replacement."
        ),
        participant_order_rule=(
            "Each participant receives a deterministic SHA-256-keyed query order and blinded "
            "candidate permutation derived from participant digest, with two delayed repeat "
            "anchors."
        ),
        queries=tuple(frozen_queries),
        repeat_anchor_candidate_ids=(
            frozen_queries[1].candidates[0].candidate_id,
            frozen_queries[6].candidates[0].candidate_id,
        ),
        query_pack_digest="0" * 64,
    )
    return cast(
        FrozenExpertQueryPack,
        _with_digest(draft_pack, FrozenExpertQueryPack, "query_pack_digest"),
    )


def _presentation(
    *,
    protocol: ExpertRelevanceProtocol,
    query_pack: FrozenExpertQueryPack,
) -> ExpertStudyPresentationBundle:
    queries = tuple(
        PresentedExpertQuery(
            query_id=query.query_id,
            query_code=query.query_code,
            exemplar_display_name=query.exemplar_display_name,
            exemplar_competition_name=query.exemplar_competition_name,
            exemplar_season_label=_SEASON_LABEL,
            exemplar_position_code=query.exemplar_position_code,
            exemplar_team_names=query.exemplar_team_names,
            exemplar_minutes=query.exemplar_minutes,
            football_prompt=query.football_prompt,
            candidates=tuple(
                PresentedCandidate(
                    candidate_id=candidate.candidate_id,
                    display_name=candidate.display_name,
                    competition_name=candidate.competition_name,
                    season_label=_SEASON_LABEL,
                    position_code=candidate.position_code,
                    team_names=candidate.team_names,
                    minutes=candidate.minutes,
                )
                for candidate in sorted(query.candidates, key=lambda value: str(value.candidate_id))
            ),
        )
        for query in query_pack.queries
    )
    draft = ExpertStudyPresentationBundle.model_construct(
        presentation_version="w10-expert-study-presentation-v1",
        protocol_digest=protocol.protocol_digest,
        query_pack_digest=query_pack.query_pack_digest,
        query_order_rule=(
            "repeat-anchor query stratum first; participant-digest-keyed deterministic "
            "permutation within the anchor and non-anchor strata"
        ),
        candidate_order_rule=(
            "participant-digest-and-query-keyed deterministic permutation; provenance, rank, "
            "score, internal grain identifiers, evidence band and difficulty are absent"
        ),
        schedule_rule="w10-participant-keyed-interleaved-v1",
        minimum_repeat_primary_delay=10,
        repeat_must_be_nonterminal=True,
        repeats_must_be_nonadjacent=True,
        queries=queries,
        repeat_anchor_candidate_ids=query_pack.repeat_anchor_candidate_ids,
        presentation_digest="0" * 64,
    )
    return cast(
        ExpertStudyPresentationBundle,
        _with_digest(draft, ExpertStudyPresentationBundle, "presentation_digest"),
    )


def build_w10_authority(
    service: ResearchServingService,
) -> tuple[ExpertRelevanceProtocol, FrozenExpertQueryPack, ExpertStudyPresentationBundle]:
    """Build and validate all three frozen W10 authorities in memory."""

    protocol = _protocol(service)
    query_pack = _query_pack(service)
    presentation = _presentation(protocol=protocol, query_pack=query_pack)
    return protocol, query_pack, presentation


def _write_once(path: Path, payload: bytes, *, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to replace incompatible frozen authority: {path}")
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol-path", type=Path, default=_PROTOCOL_PATH)
    parser.add_argument("--query-pack-path", type=Path, default=_QUERY_PACK_PATH)
    parser.add_argument("--presentation-path", type=Path, default=_PRESENTATION_PATH)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        _, service = load_production_w09_runtime(utc_clock=lambda: _GENERATED_AT)
        protocol, query_pack, presentation = build_w10_authority(service)
        _write_once(
            arguments.protocol_path,
            canonical_json_bytes(protocol.model_dump(mode="json")),
            mode=0o444,
        )
        _write_once(
            arguments.query_pack_path,
            canonical_json_bytes(query_pack.model_dump(mode="json")),
            mode=0o400,
        )
        _write_once(
            arguments.presentation_path,
            canonical_json_bytes(presentation.model_dump(mode="json")),
            mode=0o444,
        )
    except (FileExistsError, OSError, TypeError, ValueError) as exc:
        print(f"W10 protocol freeze failed: {exc}", file=sys.stderr)
        return 1
    print(
        canonical_json_bytes(
            {
                "presentation_digest": presentation.presentation_digest,
                "protocol_digest": protocol.protocol_digest,
                "query_pack_digest": query_pack.query_pack_digest,
                "query_count": len(query_pack.queries),
                "state": "FROZEN_DRAFT_AWAITING_HUMAN_APPROVAL",
            }
        ).decode("utf-8"),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

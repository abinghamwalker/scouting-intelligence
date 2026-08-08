"""Public implementation-only adversarial W06 metric regressions."""
# ruff: noqa: E501

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scouting.contracts.evaluation import (
    AgreementMethod,
    BootstrapMethod,
    EvaluationEvidence,
    EvaluationProtocol,
    EvidenceAuthority,
    MetricName,
    MissingnessPolicy,
    PairPredictionState,
    PairPreferenceEvidence,
    RelevanceLabel,
    ReviewerAuthority,
    ReviewerIdentity,
    RubricAuthority,
    TiePolicy,
    _digest,
)
from scouting.contracts.evaluation_calculations import derive_ranking_metric_children
from scouting.contracts.evidence import LicenceUseClass
from scouting.evaluation import (
    AgreementRow,
    LabelState,
    PairPrediction,
    RankedItem,
    RankingRow,
    bootstrap_interval,
    evaluate_ranking,
    inter_rater_agreement,
    pair_preference_accuracy,
    rank_comparison,
)

HASH = "a" * 64
NOW = datetime(2026, 1, 1, tzinfo=UTC)


def model(cls: object, payload: dict[str, object], digest_name: str) -> object:
    draft = cls.model_construct(**payload)  # type: ignore[union-attr]
    payload[digest_name] = _digest(draft.model_dump(mode="json"), digest_name)  # type: ignore[union-attr]
    return cls(**payload)  # type: ignore[operator]


def protocol(*, partial_counts: bool = False) -> EvaluationProtocol:
    rubric = model(
        RubricAuthority, {"rubric_id": "rubric", "authority_record_digest": HASH}, "rubric_digest"
    )
    payload = {
        "schema_version": 1,
        "protocol_id": "public",
        "protocol_version": 1,
        "claim_boundary": "resemblance_only",
        "declared_k": (1, 2, 3),
        "decision_cutoff_ts": NOW,
        "rubric": rubric,
        "rubric_digest": rubric.rubric_digest,
        "query_digest": HASH,
        "reviewer_roster_digest": HASH,
        "partition_digest": HASH,
        "partial_gain": 0.5,
        "partial_counts_for_precision_recall": partial_counts,
        "missingness_policy": MissingnessPolicy.REQUIRE_COMPLETE,
        "tie_policy": TiePolicy.SCORE_DESC_CANDIDATE_ID,
        "agreement_method": AgreementMethod.EXACT_PERCENT_AGREEMENT,
        "resampling_unit": "query",
        "bootstrap_seed": 17,
        "bootstrap_resamples": 50,
        "bootstrap_confidence": 0.9,
        "bootstrap_method": BootstrapMethod.PERCENTILE,
        "primary_metrics": (MetricName.PRECISION,),
        "secondary_metrics": (MetricName.RECALL, MetricName.NDCG, MetricName.COVERAGE),
    }
    return model(EvaluationProtocol, payload, "protocol_digest")


def reviewer(key: str) -> ReviewerIdentity:
    return model(
        ReviewerIdentity,
        {
            "reviewer_key": key,
            "authority": ReviewerAuthority.GOVERNED_HUMAN_EXPERT,
            "authority_record_digest": HASH,
            "credential_digest": HASH,
            "permitted_use": LicenceUseClass.OPEN,
        },
        "reviewer_digest",
    )


def evidence(
    evidence_id: str, reviewer_identity: ReviewerIdentity, label: RelevanceLabel, rubric_digest: str
) -> EvaluationEvidence:
    return model(
        EvaluationEvidence,
        {
            "evidence_id": evidence_id,
            "query_id": "query",
            "candidate_id": "alpha",
            "reviewer_key": reviewer_identity.reviewer_key,
            "reviewer_digest": reviewer_identity.reviewer_digest,
            "rubric_id": "rubric",
            "rubric_digest": rubric_digest,
            "label": label,
            "authority": EvidenceAuthority.GOVERNED_HUMAN_EXPERT,
            "provenance_digest": HASH,
            "rights_use": LicenceUseClass.OPEN,
            "available_at": NOW,
        },
        "evidence_digest",
    )


def test_public_fixture_digest_and_metric_path_are_executable() -> None:
    path = Path(__file__).parents[1] / "fixtures/w06/public-evaluation-v1.json"
    raw = path.read_bytes()
    fixture = json.loads(raw)
    assert (
        hashlib.sha256(raw).hexdigest()
        == "f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6"
    )
    assert fixture["evidence_class"] == "IMPLEMENTATION_FIXTURE_ONLY"
    assert "not human-expert" in fixture["claim_notice"]
    rows = []
    for fixture_row in fixture["rows"]:
        labels = {candidate: LabelState.RELEVANT for candidate in fixture_row["relevant"]}
        labels.update({candidate: LabelState.PARTIAL for candidate in fixture_row["partial"]})
        ranking = tuple(fixture_row["ranking"])
        items = tuple(
            RankedItem(
                candidate, float(len(ranking) - index), labels.get(candidate, LabelState.IRRELEVANT)
            )
            for index, candidate in enumerate(ranking)
        )
        rows.append(RankingRow(fixture_row["query_id"], tuple(sorted(ranking)), items))
    values = [evaluate_ranking(protocol(), row, 2)[MetricName.PRECISION].value for row in rows]
    assert values == [0.5, 0.5]
    aggregate, interval = bootstrap_interval(protocol(), tuple(rows), 2, MetricName.PRECISION)
    assert aggregate.value == 0.5 and interval.resample_digest is not None


def test_partial_missingness_scores_and_ties_are_exact_and_fail_closed() -> None:
    row = RankingRow(
        "query",
        ("alpha", "beta"),
        (
            RankedItem("alpha", 1.0, LabelState.RELEVANT),
            RankedItem("beta", 0.5, LabelState.PARTIAL),
        ),
    )
    results = evaluate_ranking(protocol(partial_counts=False), row, 2)
    assert results[MetricName.PRECISION].value == 0.5
    assert results[MetricName.RECALL].value == 1.0
    assert results[MetricName.NDCG].value == 1.0
    partial_only = RankingRow("query", ("alpha",), (RankedItem("alpha", 1.0, LabelState.PARTIAL),))
    partial_results = evaluate_ranking(protocol(partial_counts=False), partial_only, 1)
    assert partial_results[MetricName.PRECISION].value == 0.0
    assert partial_results[MetricName.RECALL].reason == "no_eligible_relevance_denominator"
    irrelevant = RankingRow("query", ("alpha",), (RankedItem("alpha", 1.0, LabelState.IRRELEVANT),))
    assert evaluate_ranking(protocol(), irrelevant, 1)[MetricName.PRECISION].value == 0.0
    with pytest.raises(ValueError, match="finite canonical"):
        RankedItem("alpha", float("nan"), LabelState.RELEVANT)
    with pytest.raises(ValueError, match="finite canonical"):
        RankedItem("alpha", -0.0, LabelState.RELEVANT)
    with pytest.raises(ValueError, match="tie policy"):
        evaluate_ranking(
            protocol(),
            RankingRow(
                "query",
                ("alpha", "beta"),
                (
                    RankedItem("beta", 1.0, LabelState.RELEVANT),
                    RankedItem("alpha", 1.0, LabelState.IRRELEVANT),
                ),
            ),
            1,
        )


def test_shared_calculation_is_the_cross_surface_metric_and_bootstrap_authority() -> None:
    """Core adapters and primitive calculation retain values, identities and boundaries."""
    active = protocol(partial_counts=True)
    row = RankingRow(
        "query",
        ("alpha", "beta"),
        (
            RankedItem("alpha", 1, LabelState.RELEVANT),
            RankedItem("beta", 0.0, LabelState.PARTIAL),
        ),
    )
    primitive_row = (("query", ("alpha", "beta"), (1, 0.0), ("RELEVANT", "PARTIAL")),)
    for metric in (MetricName.PRECISION, MetricName.RECALL, MetricName.NDCG, MetricName.COVERAGE):
        calculated = derive_ranking_metric_children(
            protocol_digest=active.protocol_digest,
            declared_k=active.declared_k,
            partial_gain=active.partial_gain,
            partial_counts_for_precision_recall=active.partial_counts_for_precision_recall,
            bootstrap_seed=active.bootstrap_seed,
            bootstrap_resamples=active.bootstrap_resamples,
            bootstrap_confidence=active.bootstrap_confidence,
            bootstrap_method=active.bootstrap_method.value,
            rows=primitive_row,
            metric=metric.value,
            k=1,
        )
        core = evaluate_ranking(active, row, 1)[metric]
        aggregate, interval = bootstrap_interval(active, (row,), 1, metric)
        assert core.result_digest == calculated.per_query[0]["result_digest"]
        assert aggregate.result_digest == calculated.aggregate["result_digest"]
        assert interval.interval_digest == calculated.interval["interval_digest"]
    with pytest.raises(ValueError, match="declared"):
        derive_ranking_metric_children(
            protocol_digest=active.protocol_digest,
            declared_k=active.declared_k,
            partial_gain=active.partial_gain,
            partial_counts_for_precision_recall=active.partial_counts_for_precision_recall,
            bootstrap_seed=active.bootstrap_seed,
            bootstrap_resamples=active.bootstrap_resamples,
            bootstrap_confidence=active.bootstrap_confidence,
            bootstrap_method=active.bootstrap_method.value,
            rows=primitive_row,
            metric=MetricName.PRECISION.value,
            k=999,
        )


def test_comparison_and_governed_pair_agreement_rows_are_traceable() -> None:
    active_protocol = protocol()
    low_common = rank_comparison(active_protocol, "query", ("alpha", "x"), ("alpha", "y"), 1)
    distinct_inputs = rank_comparison(active_protocol, "query", ("alpha", "z"), ("alpha", "y"), 1)
    assert (
        low_common.spearman is None
        and low_common.overlap_count == 1
        and low_common.candidate_churn == 0.0
    )
    assert (
        low_common.result_digest
        == "5febc6782ae9e260f943e22f682ed9e32947bc3f14f1e15956e8606b5d9d786c"
    )
    assert low_common.result_digest != distinct_inputs.result_digest
    assert (
        rank_comparison(
            active_protocol, "query", ("x", "alpha", "beta"), ("alpha", "beta", "y"), 2
        ).spearman
        == 1.0
    )
    human_one, human_two = reviewer("humanone"), reviewer("humantwo")
    preference = model(
        PairPreferenceEvidence,
        {
            "preference_id": "pair",
            "query_id": "query",
            "left_candidate_id": "alpha",
            "right_candidate_id": "beta",
            "preferred_candidate_id": "alpha",
            "abstained": False,
            "reviewer_key": human_one.reviewer_key,
            "reviewer_digest": human_one.reviewer_digest,
            "rubric_id": "rubric",
            "rubric_digest": active_protocol.rubric_digest,
            "provenance_digest": HASH,
            "rights_use": LicenceUseClass.OPEN,
            "available_at": NOW,
        },
        "preference_digest",
    )
    pair = pair_preference_accuracy(
        active_protocol,
        (PairPrediction(preference, human_one, PairPredictionState.PREDICTED, "alpha"),),
    )
    wrong_pair = pair_preference_accuracy(
        active_protocol,
        (PairPrediction(preference, human_one, PairPredictionState.PREDICTED, "beta"),),
    )
    missing_pair = pair_preference_accuracy(
        active_protocol, (PairPrediction(preference, human_one, PairPredictionState.MISSING),)
    )
    assert (
        pair.value == 1.0
        and pair.result_digest == "78250572322fbb52efdae3c2bf4a9214d4124f7b766c0a325aff98a9675ca515"
    )
    assert (
        pair.result_digest != wrong_pair.result_digest
        and missing_pair.reason == "missing_pair_prediction"
    )
    substituted_preference = model(
        PairPreferenceEvidence,
        {
            "preference_id": "pairsub",
            "query_id": "query",
            "left_candidate_id": "alpha",
            "right_candidate_id": "beta",
            "preferred_candidate_id": "alpha",
            "abstained": False,
            "reviewer_key": human_one.reviewer_key,
            "reviewer_digest": human_one.reviewer_digest,
            "rubric_id": "rubric",
            "rubric_digest": HASH,
            "provenance_digest": HASH,
            "rights_use": LicenceUseClass.OPEN,
            "available_at": NOW,
        },
        "preference_digest",
    )
    with pytest.raises(ValueError, match="protocol rubric"):
        pair_preference_accuracy(
            active_protocol,
            (
                PairPrediction(
                    substituted_preference, human_one, PairPredictionState.PREDICTED, "alpha"
                ),
            ),
        )
    left, right = (
        evidence("left", human_one, RelevanceLabel.RELEVANT, active_protocol.rubric_digest),
        evidence("right", human_two, RelevanceLabel.RELEVANT, active_protocol.rubric_digest),
    )
    agreement = inter_rater_agreement(
        active_protocol, (AgreementRow(left, right, human_one, human_two),)
    )
    reversed_agreement = inter_rater_agreement(
        active_protocol, (AgreementRow(right, left, human_two, human_one),)
    )
    assert (
        agreement.value == 1.0
        and agreement.result_digest
        == "d20633a5ce1bd3377fec6109a2d09111d8d1e36c2d6a11f8ab9af2a262fbf1e4"
    )
    assert agreement.result_digest == reversed_agreement.result_digest
    bad_rubric = evidence("bad", human_one, RelevanceLabel.RELEVANT, HASH)
    bad_rubric_right = evidence("badright", human_two, RelevanceLabel.RELEVANT, HASH)
    with pytest.raises(ValueError, match="protocol rubric"):
        inter_rater_agreement(
            active_protocol, (AgreementRow(bad_rubric, bad_rubric_right, human_one, human_two),)
        )

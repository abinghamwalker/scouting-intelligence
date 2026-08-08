"""Public-only adversarial regressions for the W06 relational contracts."""
# ruff: noqa: E501

import subprocess
import sys
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from scouting.contracts.evaluation import (
    AgreementMethod,
    BootstrapInterval,
    BootstrapMethod,
    EvaluatedQueryRoster,
    EvaluationAccessRecord,
    EvaluationBundle,
    EvaluationEvidence,
    EvaluationPartition,
    EvaluationProtocol,
    EvaluationQuery,
    EvaluationRun,
    EvidenceAuthority,
    FailureResult,
    GateDecision,
    GateDecisionKind,
    MetricName,
    MetricResult,
    MetricStatus,
    MissingnessPolicy,
    PartitionMembership,
    RankComparisonResult,
    RelevanceLabel,
    ReviewerAuthority,
    ReviewerIdentity,
    RubricAuthority,
    SliceResult,
    TiePolicy,
    _digest,
    _sequence_digest,
)
from scouting.contracts.evidence import LicenceUseClass
from scouting.evaluation import LabelState, RankedItem, RankingRow, bootstrap_interval

HASH = "a" * 64
NOW = datetime(2026, 1, 1, tzinfo=UTC)


def model(cls: object, payload: dict[str, object], digest_name: str) -> object:
    draft = cls.model_construct(**payload)  # type: ignore[union-attr]
    payload[digest_name] = _digest(draft.model_dump(mode="json"), digest_name)  # type: ignore[union-attr]
    return cls(**payload)  # type: ignore[operator]


def public_bundle(
    *,
    cutoff: datetime = NOW,
    duplicate: bool = False,
    reordered: bool = False,
    partition: EvaluationPartition = EvaluationPartition.FIT,
    governed: bool = False,
    relevance_present: bool = True,
    mixed: bool = False,
    label: RelevanceLabel = RelevanceLabel.RELEVANT,
    mixed_abstain: bool = False,
) -> EvaluationBundle:
    rubric = model(
        RubricAuthority, {"rubric_id": "rubric", "authority_record_digest": HASH}, "rubric_digest"
    )
    reviewer_authority = (
        ReviewerAuthority.GOVERNED_HUMAN_EXPERT
        if governed
        else ReviewerAuthority.IMPLEMENTATION_FIXTURE
    )
    evidence_authority = (
        EvidenceAuthority.GOVERNED_HUMAN_EXPERT
        if governed
        else EvidenceAuthority.IMPLEMENTATION_FIXTURE
    )
    reviewer = model(
        ReviewerIdentity,
        {
            "reviewer_key": "reviewer",
            "authority": reviewer_authority,
            "authority_record_digest": HASH,
            "credential_digest": HASH,
            "permitted_use": LicenceUseClass.OPEN,
        },
        "reviewer_digest",
    )
    candidates = ("alpha", "beta")
    query = model(
        EvaluationQuery,
        {
            "query_id": "query",
            "role_brief_id": "brief",
            "role_brief_digest": HASH,
            "exemplar_ids": (),
            "exemplar_digest": HASH,
            "candidate_universe_digest": _sequence_digest(candidates),
            "candidate_ids": candidates,
            "feature_cutoff_ts": cutoff,
        },
        "query_digest",
    )
    membership = model(
        PartitionMembership, {"query_id": "query", "partition": partition}, "membership_digest"
    )
    queries = (query,)
    memberships = (membership,)
    if mixed:
        query_two = model(
            EvaluationQuery,
            {
                "query_id": "querytwo",
                "role_brief_id": "brieftwo",
                "role_brief_digest": HASH,
                "exemplar_ids": (),
                "exemplar_digest": HASH,
                "candidate_universe_digest": _sequence_digest(candidates),
                "candidate_ids": candidates,
                "feature_cutoff_ts": cutoff,
            },
            "query_digest",
        )
        membership_two = model(
            PartitionMembership,
            {"query_id": "querytwo", "partition": EvaluationPartition.PROTECTED_TEST},
            "membership_digest",
        )
        queries = (query, query_two)
        memberships = (membership, membership_two)
    protocol = model(
        EvaluationProtocol,
        {
            "schema_version": 1,
            "protocol_id": "public",
            "protocol_version": 1,
            "claim_boundary": "resemblance_only",
            "declared_k": (1,),
            "decision_cutoff_ts": NOW + timedelta(days=1),
            "rubric": rubric,
            "rubric_digest": rubric.rubric_digest,
            "query_digest": _sequence_digest(tuple(item.query_digest for item in queries)),
            "reviewer_roster_digest": _sequence_digest((reviewer.reviewer_digest,)),
            "partition_digest": _sequence_digest(
                tuple(item.membership_digest for item in memberships)
            ),
            "partial_gain": 0.5,
            "partial_counts_for_precision_recall": False,
            "missingness_policy": MissingnessPolicy.REQUIRE_COMPLETE,
            "tie_policy": TiePolicy.SCORE_DESC_CANDIDATE_ID,
            "agreement_method": AgreementMethod.EXACT_PERCENT_AGREEMENT,
            "resampling_unit": "query",
            "bootstrap_seed": 7,
            "bootstrap_resamples": 5,
            "bootstrap_confidence": 0.8,
            "bootstrap_method": BootstrapMethod.PERCENTILE,
            "primary_metrics": (MetricName.PRECISION,),
            "secondary_metrics": (),
        },
        "protocol_digest",
    )
    relevance_one = model(
        EvaluationEvidence,
        {
            "evidence_id": "eone",
            "query_id": "query",
            "candidate_id": "alpha",
            "reviewer_key": "reviewer",
            "reviewer_digest": reviewer.reviewer_digest,
            "rubric_id": "rubric",
            "rubric_digest": rubric.rubric_digest,
            "label": label,
            "authority": evidence_authority,
            "provenance_digest": HASH,
            "rights_use": LicenceUseClass.OPEN,
            "available_at": NOW,
        },
        "evidence_digest",
    )
    relevance = (
        (relevance_one, relevance_one)
        if duplicate
        else ((relevance_one,) if relevance_present else ())
    )
    if mixed_abstain:
        abstaining = model(
            EvaluationEvidence,
            {
                "evidence_id": "etwo",
                "query_id": "query",
                "candidate_id": "beta",
                "reviewer_key": "reviewer",
                "reviewer_digest": reviewer.reviewer_digest,
                "rubric_id": "rubric",
                "rubric_digest": rubric.rubric_digest,
                "label": RelevanceLabel.ABSTAIN,
                "authority": evidence_authority,
                "provenance_digest": HASH,
                "rights_use": LicenceUseClass.OPEN,
                "available_at": NOW,
            },
            "evidence_digest",
        )
        relevance = (relevance_one, abstaining)
    if reordered:
        relevance_two = model(
            EvaluationEvidence,
            {
                "evidence_id": "etwo",
                "query_id": "query",
                "candidate_id": "beta",
                "reviewer_key": "reviewer",
                "reviewer_digest": reviewer.reviewer_digest,
                "rubric_id": "rubric",
                "rubric_digest": rubric.rubric_digest,
                "label": RelevanceLabel.IRRELEVANT,
                "authority": evidence_authority,
                "provenance_digest": HASH,
                "rights_use": LicenceUseClass.OPEN,
                "available_at": NOW,
            },
            "evidence_digest",
        )
        relevance = (relevance_two, relevance_one)
    payload = {
        "schema_version": 1,
        "protocol": protocol,
        "queries": queries,
        "reviewers": (reviewer,),
        "relevance": relevance,
        "preferences": (),
        "hard_negatives": (),
        "adjudications": (),
        "memberships": memberships,
        "candidate_manifest_digest": _sequence_digest(
            tuple(f"{item.query_id}:{item.candidate_universe_digest}" for item in queries)
        ),
    }
    return model(EvaluationBundle, payload, "bundle_digest")


def roster(*query_ids: str) -> EvaluatedQueryRoster:
    ids = query_ids or ("query",)
    return EvaluatedQueryRoster(query_ids=ids, evaluated_query_digest=_sequence_digest(ids))


def metric_result(
    evaluated_roster: EvaluatedQueryRoster | None = None, protocol_digest: str = HASH
) -> MetricResult:
    population = evaluated_roster or roster()
    return model(
        MetricResult,
        {
            "metric": MetricName.PRECISION,
            "k": 1,
            "protocol_digest": protocol_digest,
            "evaluated_query_digest": population.evaluated_query_digest,
            "input_digest": HASH,
            "value": 1.0,
            "numerator": 1.0,
            "denominator": 1.0,
            "status": MetricStatus.COMPUTED,
        },
        "result_digest",
    )


def linked_run(
    bundle: EvaluationBundle,
    *,
    partition: EvaluationPartition,
    evaluated_roster: EvaluatedQueryRoster | None = None,
) -> EvaluationRun:
    population = evaluated_roster or roster()
    result = metric_result(population, bundle.protocol.protocol_digest)
    access = model(
        EvaluationAccessRecord,
        {
            "access_id": "access",
            "protocol_digest": bundle.protocol.protocol_digest,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": population,
            "evaluated_query_digest": population.evaluated_query_digest,
            "partition": partition,
            "accessor_key": "operator",
            "purpose": "public-test",
            "accessed_at": NOW,
            "one_use": True,
            "consumed_by_run_id": "run",
        },
        "access_digest",
    )
    interval = model(
        BootstrapInterval,
        {
            "metric_result_digest": result.result_digest,
            "protocol_digest": bundle.protocol.protocol_digest,
            "evaluated_query_digest": population.evaluated_query_digest,
            "input_digest": HASH,
            "point_value": 1.0,
            "resample_digest": HASH,
            "seed": 7,
            "resamples": 5,
            "confidence": 0.8,
            "method": BootstrapMethod.PERCENTILE,
            "lower": 1.0,
            "upper": 1.0,
            "status": MetricStatus.COMPUTED,
        },
        "interval_digest",
    )
    return model(
        EvaluationRun,
        {
            "run_id": "run",
            "protocol": bundle.protocol,
            "access": access,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": population,
            "evaluated_query_digest": population.evaluated_query_digest,
            "partition": partition,
            "metric_results": (result,),
            "intervals": (interval,),
            "slices": (),
            "failures": (),
        },
        "run_digest",
    )


def test_candidate_roster_cutoff_and_canonical_evidence_reject_attacks() -> None:
    with pytest.raises(ValidationError, match="candidate_universe_digest"):
        model(
            EvaluationQuery,
            {
                "query_id": "query",
                "role_brief_id": "brief",
                "role_brief_digest": HASH,
                "exemplar_ids": (),
                "exemplar_digest": HASH,
                "candidate_universe_digest": HASH,
                "candidate_ids": ("alpha",),
                "feature_cutoff_ts": NOW,
            },
            "query_digest",
        )
    with pytest.raises(ValidationError, match="feature cutoff"):
        public_bundle(cutoff=NOW + timedelta(days=2))
    with pytest.raises(ValidationError, match="unique IDs and semantic keys"):
        public_bundle(duplicate=True)
    with pytest.raises(ValidationError, match="canonically ordered"):
        public_bundle(reordered=True)


def test_optimized_python_still_rejects_missing_computed_metric_values() -> None:
    witness = """
from pydantic import ValidationError
from scouting.contracts.evaluation import MetricName, MetricResult, MetricStatus

try:
    MetricResult(
        metric=MetricName.PRECISION,
        k=1,
        protocol_digest="a" * 64,
        evaluated_query_digest="a" * 64,
        input_digest="a" * 64,
        status=MetricStatus.COMPUTED,
        result_digest="a" * 64,
    )
except ValidationError as error:
    if "computed metrics require value and sufficient statistics" in str(error):
        print("rejected")
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-O", "-c", witness], check=True, capture_output=True, text=True
    )
    assert completed.stdout.strip() == "rejected"


def test_relational_access_run_gate_chain_rejects_the_retained_p0_constructor() -> None:
    bundle = public_bundle()
    result = metric_result(protocol_digest=bundle.protocol.protocol_digest)
    access = model(
        EvaluationAccessRecord,
        {
            "access_id": "access",
            "protocol_digest": bundle.protocol.protocol_digest,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": roster(),
            "evaluated_query_digest": roster().evaluated_query_digest,
            "partition": EvaluationPartition.FIT,
            "accessor_key": "operator",
            "purpose": "public-test",
            "accessed_at": NOW,
            "one_use": True,
            "consumed_by_run_id": "run",
        },
        "access_digest",
    )
    with pytest.raises(ValidationError, match="access must be consumed"):
        model(
            EvaluationRun,
            {
                "run_id": "run",
                "protocol": bundle.protocol,
                "access": access,
                "bundle_digest": bundle.bundle_digest,
                "candidate_manifest_digest": bundle.candidate_manifest_digest,
                "evaluated_queries": roster(),
                "evaluated_query_digest": roster().evaluated_query_digest,
                "partition": EvaluationPartition.PROTECTED_TEST,
                "metric_results": (result,),
                "intervals": (),
                "slices": (),
                "failures": (),
            },
            "run_digest",
        )
    with pytest.raises(ValidationError, match="claim and narrowing"):
        model(
            GateDecision,
            {
                "gate_id": "gate",
                "decision": GateDecisionKind.ACCEPT_CLAIM,
                "protocol": bundle.protocol,
                "claim_boundary": "resemblance_only",
                "reason_codes": ("public-only",),
            },
            "gate_digest",
        )
    with pytest.raises(ValidationError, match="one_use"):
        model(
            EvaluationAccessRecord,
            {
                "access_id": "access",
                "protocol_digest": bundle.protocol.protocol_digest,
                "bundle_digest": bundle.bundle_digest,
                "candidate_manifest_digest": bundle.candidate_manifest_digest,
                "evaluated_queries": roster(),
                "evaluated_query_digest": roster().evaluated_query_digest,
                "partition": EvaluationPartition.FIT,
                "accessor_key": "operator",
                "purpose": "public-test",
                "accessed_at": NOW,
                "one_use": False,
                "consumed_by_run_id": "run",
            },
            "access_digest",
        )


def test_metric_interval_and_run_links_reject_arithmetic_and_opaque_identity() -> None:
    bundle = public_bundle()
    with pytest.raises(ValidationError, match="numerator divided"):
        model(
            MetricResult,
            {
                "metric": MetricName.PRECISION,
                "k": 1,
                "protocol_digest": bundle.protocol.protocol_digest,
                "evaluated_query_digest": roster().evaluated_query_digest,
                "input_digest": HASH,
                "value": 2.0,
                "numerator": 1.0,
                "denominator": 2.0,
                "status": MetricStatus.COMPUTED,
            },
            "result_digest",
        )
    with pytest.raises(ValidationError, match="sufficient statistics"):
        model(
            MetricResult,
            {
                "metric": MetricName.PRECISION,
                "k": 1,
                "protocol_digest": bundle.protocol.protocol_digest,
                "evaluated_query_digest": roster().evaluated_query_digest,
                "input_digest": HASH,
                "value": 0.5,
                "numerator": -1.0,
                "denominator": -2.0,
                "status": MetricStatus.COMPUTED,
            },
            "result_digest",
        )
    with pytest.raises(ValidationError, match="computed metrics cannot retain"):
        model(
            MetricResult,
            {
                "metric": MetricName.PRECISION,
                "k": 1,
                "protocol_digest": bundle.protocol.protocol_digest,
                "evaluated_query_digest": roster().evaluated_query_digest,
                "input_digest": HASH,
                "value": 1.0,
                "numerator": 1.0,
                "denominator": 1.0,
                "status": MetricStatus.COMPUTED,
                "reason": "unsupported",
            },
            "result_digest",
        )
    result = metric_result(protocol_digest=bundle.protocol.protocol_digest)
    with pytest.raises(ValidationError, match="contain the point"):
        model(
            BootstrapInterval,
            {
                "metric_result_digest": result.result_digest,
                "protocol_digest": bundle.protocol.protocol_digest,
                "evaluated_query_digest": roster().evaluated_query_digest,
                "input_digest": HASH,
                "point_value": 1.0,
                "resample_digest": HASH,
                "seed": 7,
                "resamples": 5,
                "confidence": 0.8,
                "method": BootstrapMethod.PERCENTILE,
                "lower": 1.0,
                "upper": 0.0,
                "status": MetricStatus.COMPUTED,
            },
            "interval_digest",
        )
    with pytest.raises(ValidationError, match=r"within \[0, 1\]"):
        model(
            BootstrapInterval,
            {
                "metric_result_digest": result.result_digest,
                "protocol_digest": bundle.protocol.protocol_digest,
                "evaluated_query_digest": roster().evaluated_query_digest,
                "input_digest": HASH,
                "point_value": 0.5,
                "resample_digest": HASH,
                "seed": 7,
                "resamples": 5,
                "confidence": 0.8,
                "method": BootstrapMethod.PERCENTILE,
                "lower": -1.0,
                "upper": 2.0,
                "status": MetricStatus.COMPUTED,
            },
            "interval_digest",
        )
    with pytest.raises(ValidationError, match="computed intervals cannot retain"):
        model(
            BootstrapInterval,
            {
                "metric_result_digest": result.result_digest,
                "protocol_digest": bundle.protocol.protocol_digest,
                "evaluated_query_digest": roster().evaluated_query_digest,
                "input_digest": HASH,
                "point_value": 1.0,
                "resample_digest": HASH,
                "seed": 7,
                "resamples": 5,
                "confidence": 0.8,
                "method": BootstrapMethod.PERCENTILE,
                "lower": 1.0,
                "upper": 1.0,
                "status": MetricStatus.COMPUTED,
                "reason": "unsupported",
            },
            "interval_digest",
        )
    access = model(
        EvaluationAccessRecord,
        {
            "access_id": "access",
            "protocol_digest": bundle.protocol.protocol_digest,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": roster(),
            "evaluated_query_digest": roster().evaluated_query_digest,
            "partition": EvaluationPartition.FIT,
            "accessor_key": "operator",
            "purpose": "public-test",
            "accessed_at": NOW,
            "one_use": True,
            "consumed_by_run_id": "run",
        },
        "access_digest",
    )
    interval = model(
        BootstrapInterval,
        {
            "metric_result_digest": result.result_digest,
            "protocol_digest": bundle.protocol.protocol_digest,
            "evaluated_query_digest": roster().evaluated_query_digest,
            "input_digest": HASH,
            "point_value": 1.0,
            "resample_digest": HASH,
            "seed": 7,
            "resamples": 5,
            "confidence": 0.8,
            "method": BootstrapMethod.PERCENTILE,
            "lower": 1.0,
            "upper": 1.0,
            "status": MetricStatus.COMPUTED,
        },
        "interval_digest",
    )
    run = model(
        EvaluationRun,
        {
            "run_id": "run",
            "protocol": bundle.protocol,
            "access": access,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": roster(),
            "evaluated_query_digest": roster().evaluated_query_digest,
            "partition": EvaluationPartition.FIT,
            "metric_results": (result,),
            "intervals": (interval,),
            "slices": (),
            "failures": (),
        },
        "run_digest",
    )
    assert run.run_digest and interval.interval_digest
    unsupported_payload = bundle.protocol.model_dump(mode="python")
    unsupported_payload["rubric"] = bundle.protocol.rubric
    unsupported_payload["primary_metrics"] = (MetricName.AGREEMENT,)
    with pytest.raises(ValidationError, match="protected bootstrap"):
        model(EvaluationProtocol, unsupported_payload, "protocol_digest")
    slice_result = model(
        SliceResult,
        {
            "slice_id": "slice",
            "definition_digest": HASH,
            "metric_results": (result,),
            "status": MetricStatus.COMPUTED,
        },
        "slice_digest",
    )
    failure = model(
        FailureResult,
        {
            "failure_id": "failure",
            "query_id": "query",
            "category": "public-test",
            "evidence_digest": HASH,
        },
        "failure_digest",
    )
    with pytest.raises(ValidationError, match="slices require unique"):
        model(
            EvaluationRun,
            {
                "run_id": "run",
                "protocol": bundle.protocol,
                "access": access,
                "bundle_digest": bundle.bundle_digest,
                "candidate_manifest_digest": bundle.candidate_manifest_digest,
                "evaluated_queries": roster(),
                "evaluated_query_digest": roster().evaluated_query_digest,
                "partition": EvaluationPartition.FIT,
                "metric_results": (result,),
                "intervals": (interval,),
                "slices": (slice_result, slice_result),
                "failures": (),
            },
            "run_digest",
        )
    with pytest.raises(ValidationError, match="failures require unique"):
        model(
            EvaluationRun,
            {
                "run_id": "run",
                "protocol": bundle.protocol,
                "access": access,
                "bundle_digest": bundle.bundle_digest,
                "candidate_manifest_digest": bundle.candidate_manifest_digest,
                "evaluated_queries": roster(),
                "evaluated_query_digest": roster().evaluated_query_digest,
                "partition": EvaluationPartition.FIT,
                "metric_results": (result,),
                "intervals": (interval,),
                "slices": (),
                "failures": (failure, failure),
            },
            "run_digest",
        )


def test_rank_comparison_contract_rejects_impossible_correlation_and_set_arithmetic() -> None:
    incomplete = {
        "protocol_digest": "90b2603b78c7f714cfb724579992b3caeb94a39e52715555db0d2ec0bf070f07",
        "evaluated_query_digest": roster().evaluated_query_digest,
        "k": 1,
        "left_input_digest": HASH,
        "right_input_digest": "b" * 64,
        "spearman": 1.0,
        "overlap_count": None,
        "overlap_rate": None,
        "jaccard": None,
        "candidate_churn": None,
        "disagreements": (),
        "reason": None,
    }
    with pytest.raises(ValidationError, match="computed Spearman requires top-k set metrics"):
        model(RankComparisonResult, incomplete, "result_digest")
    assert (
        incomplete["result_digest"]
        == "54cb89310bf9d6feaa7d15cc608f6262adc947f762ddb23d49cfbffe21322231"
    )
    payload = {
        "protocol_digest": HASH,
        "evaluated_query_digest": roster().evaluated_query_digest,
        "k": 1,
        "left_input_digest": HASH,
        "right_input_digest": "b" * 64,
        "spearman": 2.0,
        "overlap_count": 1,
        "overlap_rate": 1.0,
        "jaccard": 1.0,
        "candidate_churn": 0.0,
        "disagreements": (),
        "reason": None,
    }
    with pytest.raises(ValidationError, match="Spearman correlation"):
        model(RankComparisonResult, payload, "result_digest")
    payload["spearman"] = 1.0
    payload["overlap_count"] = 2
    with pytest.raises(ValidationError, match="overlap cannot exceed k"):
        model(RankComparisonResult, payload, "result_digest")


def test_core_metric_and_interval_persist_without_lineage_dropping_translation() -> None:
    bundle = public_bundle()
    row = RankingRow(
        "query",
        ("alpha", "beta"),
        (
            RankedItem("alpha", 1.0, LabelState.RELEVANT),
            RankedItem("beta", 0.0, LabelState.IRRELEVANT),
        ),
    )
    core_metric, core_interval = bootstrap_interval(
        bundle.protocol, (row,), 1, MetricName.PRECISION
    )
    access = model(
        EvaluationAccessRecord,
        {
            "access_id": "access",
            "protocol_digest": bundle.protocol.protocol_digest,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": roster(),
            "evaluated_query_digest": roster().evaluated_query_digest,
            "partition": EvaluationPartition.FIT,
            "accessor_key": "operator",
            "purpose": "public-test",
            "accessed_at": NOW,
            "one_use": True,
            "consumed_by_run_id": "run",
        },
        "access_digest",
    )
    run = model(
        EvaluationRun,
        {
            "run_id": "run",
            "protocol": bundle.protocol,
            "access": access,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": roster(),
            "evaluated_query_digest": roster().evaluated_query_digest,
            "partition": EvaluationPartition.FIT,
            "metric_results": (core_metric,),
            "intervals": (core_interval,),
            "slices": (),
            "failures": (),
        },
        "run_digest",
    )
    assert run.metric_results[0].result_digest == core_metric.result_digest
    assert run.intervals[0].interval_digest == core_interval.interval_digest
    assert (
        core_metric.result_digest
        == "f021adec1d57a5f54eec235273a66ef6a0a6665599c56cc7843169f0b0cb562e"
    )
    assert (
        core_interval.interval_digest
        == "79322b611e83d790af4052a63225d0cbe82c878d04c1ffda07e7fbef7ac1003a"
    )
    assert (
        core_metric.protocol_digest
        == core_interval.protocol_digest
        == bundle.protocol.protocol_digest
    )
    assert core_metric.input_digest == core_interval.input_digest


def test_gate_population_lineage_and_two_no_go_shapes_are_fail_closed() -> None:
    protected = public_bundle(partition=EvaluationPartition.PROTECTED_TEST, governed=True)
    run = linked_run(protected, partition=EvaluationPartition.PROTECTED_TEST)
    complete_negative = model(
        GateDecision,
        {
            "gate_id": "nogo",
            "decision": GateDecisionKind.NO_GO,
            "protocol": protected.protocol,
            "bundle": protected,
            "run": run,
            "claim_boundary": "resemblance_only",
            "reason_codes": ("negative-evidence",),
        },
        "gate_digest",
    )
    assert complete_negative.gate_digest
    missing_population = model(
        GateDecision,
        {
            "gate_id": "missing",
            "decision": GateDecisionKind.NO_GO,
            "protocol": protected.protocol,
            "claim_boundary": "resemblance_only",
            "reason_codes": ("MISSING_PROTECTED_POPULATION",),
        },
        "gate_digest",
    )
    assert missing_population.gate_digest
    with pytest.raises(ValidationError, match="neither object or both"):
        model(
            GateDecision,
            {
                "gate_id": "orphan",
                "decision": GateDecisionKind.NO_GO,
                "protocol": protected.protocol,
                "run": run,
                "claim_boundary": "resemblance_only",
                "reason_codes": ("negative-evidence",),
            },
            "gate_digest",
        )
    empty = public_bundle(
        partition=EvaluationPartition.PROTECTED_TEST, governed=True, relevance_present=False
    )
    with pytest.raises(ValidationError, match="governed evidence"):
        model(
            GateDecision,
            {
                "gate_id": "narrow",
                "decision": GateDecisionKind.NARROW_APPLICABILITY,
                "protocol": empty.protocol,
                "bundle": empty,
                "run": linked_run(empty, partition=EvaluationPartition.PROTECTED_TEST),
                "claim_boundary": "resemblance_only",
                "reason_codes": ("empty-evidence",),
            },
            "gate_digest",
        )


def test_gate_rejects_mixed_protocol_and_population_substitution() -> None:
    mixed = public_bundle(mixed=True, governed=True)
    with pytest.raises(ValidationError, match="exactly cover"):
        model(
            GateDecision,
            {
                "gate_id": "mixed",
                "decision": GateDecisionKind.ACCEPT_CLAIM,
                "protocol": mixed.protocol,
                "bundle": mixed,
                "run": linked_run(mixed, partition=EvaluationPartition.PROTECTED_TEST),
                "claim_boundary": "resemblance_only",
                "reason_codes": ("mixed",),
            },
            "gate_digest",
        )
    protected = public_bundle(partition=EvaluationPartition.PROTECTED_TEST, governed=True)
    different_protocol = public_bundle().protocol
    with pytest.raises(ValidationError, match="protected protocol"):
        model(
            GateDecision,
            {
                "gate_id": "substitute",
                "decision": GateDecisionKind.ACCEPT_CLAIM,
                "protocol": different_protocol,
                "bundle": protected,
                "run": linked_run(protected, partition=EvaluationPartition.PROTECTED_TEST),
                "claim_boundary": "resemblance_only",
                "reason_codes": ("substitute",),
            },
            "gate_digest",
        )
    bundle = public_bundle()
    incorrect_population = roster("querytwo")
    result = metric_result(incorrect_population)
    access = model(
        EvaluationAccessRecord,
        {
            "access_id": "access",
            "protocol_digest": bundle.protocol.protocol_digest,
            "bundle_digest": bundle.bundle_digest,
            "candidate_manifest_digest": bundle.candidate_manifest_digest,
            "evaluated_queries": roster(),
            "evaluated_query_digest": roster().evaluated_query_digest,
            "partition": EvaluationPartition.FIT,
            "accessor_key": "operator",
            "purpose": "public-test",
            "accessed_at": NOW,
            "one_use": True,
            "consumed_by_run_id": "run",
        },
        "access_digest",
    )
    with pytest.raises(ValidationError, match="result must bind"):
        model(
            EvaluationRun,
            {
                "run_id": "run",
                "protocol": bundle.protocol,
                "access": access,
                "bundle_digest": bundle.bundle_digest,
                "candidate_manifest_digest": bundle.candidate_manifest_digest,
                "evaluated_queries": roster(),
                "evaluated_query_digest": roster().evaluated_query_digest,
                "partition": EvaluationPartition.FIT,
                "metric_results": (result,),
                "intervals": (),
                "slices": (),
                "failures": (),
            },
            "run_digest",
        )


def test_all_abstain_positive_gates_and_foreign_run_children_reject() -> None:
    abstaining = public_bundle(
        partition=EvaluationPartition.PROTECTED_TEST, governed=True, label=RelevanceLabel.ABSTAIN
    )
    abstaining_run = linked_run(abstaining, partition=EvaluationPartition.PROTECTED_TEST)
    for decision in (GateDecisionKind.ACCEPT_CLAIM, GateDecisionKind.NARROW_APPLICABILITY):
        with pytest.raises(ValidationError, match="governed evidence"):
            model(
                GateDecision,
                {
                    "gate_id": f"abstain-{decision.value.lower()}",
                    "decision": decision,
                    "protocol": abstaining.protocol,
                    "bundle": abstaining,
                    "run": abstaining_run,
                    "claim_boundary": "resemblance_only",
                    "reason_codes": ("abstain",),
                },
                "gate_digest",
            )
    mixed_abstaining = public_bundle(
        partition=EvaluationPartition.PROTECTED_TEST, governed=True, mixed_abstain=True
    )
    mixed_abstaining_run = linked_run(
        mixed_abstaining, partition=EvaluationPartition.PROTECTED_TEST
    )
    for decision in (GateDecisionKind.ACCEPT_CLAIM, GateDecisionKind.NARROW_APPLICABILITY):
        with pytest.raises(ValidationError, match="governed evidence"):
            model(
                GateDecision,
                {
                    "gate_id": f"mixed-abstain-{decision.value.lower()}",
                    "decision": decision,
                    "protocol": mixed_abstaining.protocol,
                    "bundle": mixed_abstaining,
                    "run": mixed_abstaining_run,
                    "claim_boundary": "resemblance_only",
                    "reason_codes": ("mixed-abstain",),
                },
                "gate_digest",
            )

    bundle = public_bundle()
    base_run = linked_run(bundle, partition=EvaluationPartition.FIT)
    foreign_metric = metric_result(roster("foreign"))
    foreign_slice = model(
        SliceResult,
        {
            "slice_id": "slice",
            "definition_digest": HASH,
            "metric_results": (foreign_metric,),
            "status": MetricStatus.COMPUTED,
        },
        "slice_digest",
    )
    with pytest.raises(ValidationError, match="slice metric results"):
        model(
            EvaluationRun,
            {
                "run_id": base_run.run_id,
                "protocol": base_run.protocol,
                "access": base_run.access,
                "bundle_digest": base_run.bundle_digest,
                "candidate_manifest_digest": base_run.candidate_manifest_digest,
                "evaluated_queries": base_run.evaluated_queries,
                "evaluated_query_digest": base_run.evaluated_query_digest,
                "partition": base_run.partition,
                "metric_results": base_run.metric_results,
                "intervals": base_run.intervals,
                "slices": (foreign_slice,),
                "failures": (),
            },
            "run_digest",
        )
    foreign_failure = model(
        FailureResult,
        {
            "failure_id": "failure",
            "query_id": "foreign",
            "category": "public-test",
            "evidence_digest": HASH,
        },
        "failure_digest",
    )
    with pytest.raises(ValidationError, match="failure query"):
        model(
            EvaluationRun,
            {
                "run_id": base_run.run_id,
                "protocol": base_run.protocol,
                "access": base_run.access,
                "bundle_digest": base_run.bundle_digest,
                "candidate_manifest_digest": base_run.candidate_manifest_digest,
                "evaluated_queries": base_run.evaluated_queries,
                "evaluated_query_digest": base_run.evaluated_query_digest,
                "partition": base_run.partition,
                "metric_results": base_run.metric_results,
                "intervals": base_run.intervals,
                "slices": (),
                "failures": (foreign_failure,),
            },
            "run_digest",
        )

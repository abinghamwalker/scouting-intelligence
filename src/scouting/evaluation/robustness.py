"""Embedded-input W06 robustness experiments; public fixtures never impersonate experts."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from scouting.contracts.evaluation import (
    ApplicabilityAssessment,
    ApplicabilityState,
    ControlInput,
    ControlKind,
    DeficitKind,
    DeterministicControlResult,
    EvaluationProtocol,
    FailureCase,
    FailureCaseRegister,
    GovernedPopulationMember,
    MetricName,
    PopulationDeficit,
    RankedObservation,
    RelevanceLabel,
    RobustnessStatus,
    StressCohort,
    StressComparison,
    StressTestKind,
    StressTestResult,
    StressTestSpecification,
    _digest,
    _sequence_digest,
    derive_cohort_ranked_rows,
    derive_label_null_rows,
    derive_label_permutation,
    derive_rank_comparison,
    derive_ranking_metric_children,
)
from scouting.contracts.primitives import ContractModel

from .core import (
    LabelState,
    RankedItem,
    RankingRow,
)


def _contract[ContractT: ContractModel](
    cls: type[ContractT], payload: dict[str, object], digest: str
) -> ContractT:
    draft = cls.model_construct(**payload)  # type: ignore[arg-type]
    payload[digest] = _digest(draft.model_dump(mode="json"), digest)
    return cls(**payload)


def _row(observation: RankedObservation) -> RankingRow:
    labels = {
        "RELEVANT": LabelState.RELEVANT,
        "IRRELEVANT": LabelState.IRRELEVANT,
        "PARTIAL": LabelState.PARTIAL,
    }
    return RankingRow(
        observation.query_id,
        tuple(sorted(observation.candidate_ids)),
        tuple(
            RankedItem(candidate, score, labels[label.value])
            for candidate, score, label in zip(
                observation.candidate_ids, observation.scores, observation.labels, strict=True
            )
        ),
    )


def _observation(row_id: str, query_id: str, items: tuple[RankedItem, ...]) -> RankedObservation:
    labels = {
        LabelState.RELEVANT: RelevanceLabel.RELEVANT,
        LabelState.IRRELEVANT: RelevanceLabel.IRRELEVANT,
        LabelState.PARTIAL: RelevanceLabel.PARTIAL,
    }
    payload: dict[str, object] = {
        "row_id": row_id,
        "query_id": query_id,
        "candidate_ids": tuple(item.candidate_id for item in items),
        "scores": tuple(item.score for item in items),
        "labels": tuple(labels[item.label] for item in items),
    }
    return _contract(RankedObservation, payload, "ranking_digest")


def _aggregate(
    specification: StressTestSpecification,
    cohort_id: str,
    members: tuple[GovernedPopulationMember, ...],
) -> tuple[RankedObservation, ...]:
    return derive_cohort_ranked_rows(
        specification, cohort_id, tuple(sorted(member.observation_id for member in members))
    )


def _cohort(
    specification: StressTestSpecification,
    cohort_id: str,
    members: tuple[GovernedPopulationMember, ...],
) -> StressCohort:
    rows = _aggregate(specification, cohort_id, members)
    per_query, metric, interval = derive_ranking_metric_children(
        specification.protocol, rows, specification.metric, specification.k
    )
    return _contract(
        StressCohort,
        {
            "cohort_id": cohort_id,
            "observation_ids": tuple(sorted(member.observation_id for member in members)),
            "evaluated_query_ids": tuple(row.query_id for row in rows),
            "observation_digest": _sequence_digest(
                tuple(sorted(member.observation_id for member in members)),
            ),
            "candidate_roster_digest": _digest(
                {"rows": tuple(row.ranking_digest for row in rows)}, "omitted"
            ),
            "ranked_rows": rows,
            "per_query_results": per_query,
            "metric_result": metric,
            "interval": interval,
        },
        "cohort_digest",
    )


def _comparisons(
    specification: StressTestSpecification, left: StressCohort, right: StressCohort
) -> tuple[StressComparison, ...]:
    left_rows = {row.query_id: row for row in left.ranked_rows}
    right_rows = {row.query_id: row for row in right.ranked_rows}
    output: list[StressComparison] = []
    for query in sorted(set(left_rows) & set(right_rows)):
        a, b = left_rows[query], right_rows[query]
        common = tuple(sorted(set(a.candidate_ids) & set(b.candidate_ids)))
        if len(common) < specification.k:
            raise ValueError(
                f"query={query}:comparison_common_candidate_count={len(common)}<{specification.k}"
            )
        one, two = sorted((left.cohort_digest, right.cohort_digest))
        left_row, right_row = (a, b) if one == left.cohort_digest else (b, a)
        comparison = derive_rank_comparison(
            specification.protocol,
            query,
            tuple(candidate for candidate in left_row.candidate_ids if candidate in common),
            tuple(candidate for candidate in right_row.candidate_ids if candidate in common),
            specification.k,
        )
        output.append(
            _contract(
                StressComparison,
                {
                    "left_cohort_digest": one,
                    "right_cohort_digest": two,
                    "query_id": query,
                    "common_candidate_digest": _sequence_digest(common),
                    "left_ranking": left_row,
                    "right_ranking": right_row,
                    "comparison": comparison,
                },
                "comparison_digest",
            )
        )
    return tuple(output)


def _unsupported(specification: StressTestSpecification) -> StressTestResult:
    draft = StressTestResult.model_construct(
        specification=specification,
        status=RobustnessStatus.UNSUPPORTED_INSUFFICIENT_EVIDENCE,
        cohorts=(),
        comparisons=(),
        deficits=(),
        result_digest="a" * 64,
    )
    return _contract(
        StressTestResult,
        {
            "specification": specification,
            "status": RobustnessStatus.UNSUPPORTED_INSUFFICIENT_EVIDENCE,
            "deficits": draft._expected_deficits(),
        },
        "result_digest",
    )


def evaluate_stress_test(specification: StressTestSpecification) -> StressTestResult:
    """Execute only the single frozen specification and its embedded observations."""
    members = specification.inventory.members
    draft = StressTestResult.model_construct(
        specification=specification,
        status=RobustnessStatus.UNSUPPORTED_INSUFFICIENT_EVIDENCE,
        cohorts=(),
        comparisons=(),
        deficits=(),
        result_digest="a" * 64,
    )
    if draft._expected_deficits():
        return _unsupported(specification)
    kind = specification.kind
    by_query: dict[str, list[GovernedPopulationMember]] = defaultdict(list)
    for member in members:
        by_query[member.query_id].append(member)
    if kind is StressTestKind.SPLIT_HALF_RELIABILITY:
        groups = [
            (
                "half-a",
                tuple(
                    member
                    for values in by_query.values()
                    for index, member in enumerate(values)
                    if index % 2 == 0
                ),
            ),
            (
                "half-b",
                tuple(
                    member
                    for values in by_query.values()
                    for index, member in enumerate(values)
                    if index % 2 == 1
                ),
            ),
        ]
    elif kind is StressTestKind.ROLLING_WINDOW_STABILITY:
        windows = sorted({(member.chronological_index, member.window_id) for member in members})
        groups = [
            (
                f"window-{index:04d}",
                tuple(member for member in members if member.window_id == window),
            )
            for index, (_, window) in enumerate(windows)
        ]
    elif kind is StressTestKind.MINUTES_SAMPLE_SENSITIVITY:
        groups = [
            (
                f"minutes-{threshold}",
                tuple(member for member in members if member.minutes >= threshold),
            )
            for threshold in specification.thresholds
        ]
    elif kind is StressTestKind.TIME_WALK_FORWARD:
        cutoff = specification.walk_forward_cutoff_index
        if cutoff is None:
            raise ValueError("walk-forward requires an embedded declared cutoff index")
        groups = [
            (
                "train-earlier",
                tuple(member for member in members if member.chronological_index <= cutoff),
            ),
            (
                "test-later",
                tuple(member for member in members if member.chronological_index > cutoff),
            ),
        ]
    else:
        field = {
            StressTestKind.LEAVE_COMPETITION_OUT: "competition_id",
            StressTestKind.LEAVE_TEAM_OUT: "team_id",
            StressTestKind.LEAVE_PROVIDER_OUT: "provider_id",
            StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON: "provider_id",
        }[kind]
        values = sorted({str(getattr(member, field)) for member in members})
        groups = [
            (
                f"provider-{value}"
                if kind is StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON
                else f"leave-{value}",
                tuple(
                    member
                    for member in members
                    if (
                        getattr(member, field) == value
                        if kind is StressTestKind.INTERSECTION_ONLY_SOURCE_COMPARISON
                        else getattr(member, field) != value
                    )
                ),
            )
            for value in values
        ]
    try:
        cohorts = tuple(_cohort(specification, name, selected) for name, selected in groups)
        pairs = (
            ((cohorts[0], cohorts[1]),)
            if kind in {StressTestKind.SPLIT_HALF_RELIABILITY, StressTestKind.TIME_WALK_FORWARD}
            else tuple(zip(cohorts, cohorts[1:], strict=False))
            if kind
            in {StressTestKind.ROLLING_WINDOW_STABILITY, StressTestKind.MINUTES_SAMPLE_SENSITIVITY}
            else tuple(combinations(cohorts, 2))
        )
        comparisons = tuple(
            item for left, right in pairs for item in _comparisons(specification, left, right)
        )
    except ValueError:
        return _unsupported(specification)
    return _contract(
        StressTestResult,
        {
            "specification": specification,
            "status": RobustnessStatus.COMPUTED,
            "cohorts": tuple(sorted(cohorts, key=lambda item: item.cohort_id)),
            "comparisons": tuple(
                sorted(
                    comparisons,
                    key=lambda item: (
                        item.left_cohort_digest,
                        item.right_cohort_digest,
                        item.query_id,
                    ),
                )
            ),
        },
        "result_digest",
    )


def evaluate_control(
    protocol: EvaluationProtocol, input: ControlInput
) -> DeterministicControlResult:
    """Run only embedded typed control evidence; absent governed pair evidence is closed."""
    if input.k not in protocol.declared_k:
        raise ValueError("control k must be declared")
    if input.control is ControlKind.SHUFFLED_PAIR:
        deficit_payload = {
            "kind": DeficitKind.GOVERNED_PAIR_EVIDENCE,
            "scope": "MISSING_GOVERNED_PAIR_EVIDENCE",
            "observed": 0,
            "required": 1,
        }
        deficit = _contract(PopulationDeficit, deficit_payload, "deficit_digest")
        return _contract(
            DeterministicControlResult,
            {
                "control": input.control,
                "protocol": protocol,
                "input": input,
                "seed": protocol.bootstrap_seed,
                "status": RobustnessStatus.UNSUPPORTED_INSUFFICIENT_EVIDENCE,
                "deficits": (deficit,),
            },
            "control_digest",
        )
    baseline_observations, challenger_observations = input.baseline_rows, input.challenger_rows
    permutation: tuple[str, ...] = ()
    null_observations = input.challenger_rows
    if input.control is ControlKind.SHUFFLED_LABEL:
        null_observations = derive_label_null_rows(input.challenger_rows, protocol.bootstrap_seed)
        challenger_observations = null_observations
        permutation = derive_label_permutation(input.challenger_rows, protocol.bootstrap_seed)
    baseline_per_query, baseline, _ = derive_ranking_metric_children(
        protocol, baseline_observations, MetricName.PRECISION, input.k
    )
    null_per_query, null, _ = derive_ranking_metric_children(
        protocol, challenger_observations, MetricName.PRECISION, input.k
    )
    comparisons = tuple(
        sorted(
            (
                derive_rank_comparison(
                    protocol,
                    row.query_id,
                    tuple(row.candidate_ids),
                    tuple(challenger.candidate_ids),
                    input.k,
                )
                for row, challenger in zip(
                    baseline_observations, challenger_observations, strict=True
                )
            ),
            key=lambda item: item.result_digest,
        )
    )
    payload: dict[str, object] = {
        "control": input.control,
        "protocol": protocol,
        "input": input,
        "seed": protocol.bootstrap_seed,
        "status": RobustnessStatus.COMPUTED,
        "baseline_rows": input.baseline_rows,
        "null_rows": challenger_observations,
        "baseline_per_query_results": baseline_per_query,
        "null_per_query_results": null_per_query,
        "baseline_result": baseline,
        "null_result": null,
        "comparisons": comparisons,
    }
    if permutation:
        payload.update(
            {"permutation": permutation, "permutation_digest": _sequence_digest(permutation)}
        )
    return _contract(DeterministicControlResult, payload, "control_digest")


def register_failures(cases: tuple[FailureCase, ...]) -> FailureCaseRegister:
    ordered = tuple(sorted(cases, key=lambda item: (-item.severity, item.case_id)))
    if cases != ordered:
        raise ValueError("failure source cases must be canonical")
    return _contract(
        FailureCaseRegister,
        {
            "source_cases": cases,
            "source_digest": _sequence_digest(tuple(item.case_digest for item in cases)),
            "retained_cases": cases[:10],
            "total_case_count": len(cases),
            "shortfall": max(0, 10 - len(cases)),
        },
        "register_digest",
    )


def assess_applicability(
    inventory: object,
    stress_results: tuple[StressTestResult, ...],
    control_results: tuple[DeterministicControlResult, ...],
) -> ApplicabilityAssessment:
    # Existing contract derives result deficits; claims are frozen here, never caller authority.
    from scouting.contracts.evaluation import GovernedPopulationInventory

    if not isinstance(inventory, GovernedPopulationInventory):
        raise TypeError("inventory must be a GovernedPopulationInventory")
    missing = {"MISSING_EXPERT_RELEVANCE_EVIDENCE"}
    for stress_result in stress_results:
        for deficit in stress_result.deficits:
            missing.add(
                f"MISSING_{stress_result.specification.kind.value}:{deficit.kind.value}:{deficit.scope}"
            )
    for control_result in control_results:
        for deficit in control_result.deficits:
            missing.add(deficit.scope)
    return _contract(
        ApplicabilityAssessment,
        {
            "inventory": inventory,
            "state": ApplicabilityState.UNSUPPORTED,
            "stress_results": tuple(
                sorted(stress_results, key=lambda item: item.specification.kind.value)
            ),
            "control_results": tuple(sorted(control_results, key=lambda item: item.control.value)),
            "missing_evidence": tuple(sorted(missing)),
            "supported_population": ("IMPLEMENTATION_FIXTURE_ONLY",),
            "exclusions": ("NO_EMPIRICAL_TRANSFER_OR_EXPERT_EVIDENCE",),
            "non_claims": (
                "NOT_HUMAN_EXPERT_EVIDENCE",
                "NOT_PROTECTED_OR_PROSPECTIVE_EVIDENCE",
                "NOT_PROVIDER_OR_RECRUITMENT_OUTCOME_EVIDENCE",
            ),
        },
        "assessment_digest",
    )

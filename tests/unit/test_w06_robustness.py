"""R4 public fixture drives every robustness authority and identity."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from scouting.contracts.evaluation import (
    AgreementMethod,
    BootstrapMethod,
    ControlAuthorityKind,
    ControlBaselineAuthority,
    ControlInput,
    ControlKind,
    DeficitKind,
    EvaluationProtocol,
    EvidenceAuthority,
    FailureCase,
    FailureCategory,
    GovernedPopulationInventory,
    GovernedPopulationMember,
    MetricName,
    MissingnessPolicy,
    RankedObservation,
    RelevanceLabel,
    RubricAuthority,
    StressTestKind,
    StressTestSpecification,
    TiePolicy,
    _digest,
)
from scouting.evaluation import (
    assess_applicability,
    evaluate_control,
    evaluate_stress_test,
    register_failures,
)

HASH = "a" * 64
FIXTURE_SHA = "b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6"


def make(cls: object, payload: dict[str, object], name: str) -> object:
    draft = cls.model_construct(**payload)  # type: ignore[union-attr]
    payload[name] = _digest(draft.model_dump(mode="json"), name)  # type: ignore[union-attr]
    return cls(**payload)  # type: ignore[operator]


def fixture_data() -> dict[str, object]:
    return json.loads(
        (Path(__file__).parents[1] / "fixtures/w06/public-robustness-v1.json").read_bytes()
    )


def protocol_from(fixture: dict[str, object]) -> EvaluationProtocol:
    data = fixture["protocol"]  # type: ignore[index]
    rubric = make(
        RubricAuthority, {"rubric_id": "rubric", "authority_record_digest": HASH}, "rubric_digest"
    )
    return make(
        EvaluationProtocol,
        {
            "protocol_id": data["id"],
            "protocol_version": 1,
            "claim_boundary": "resemblance_only",
            "declared_k": tuple(data["declared_k"]),
            "decision_cutoff_ts": datetime(2026, 1, 1, tzinfo=UTC),
            "rubric": rubric,
            "rubric_digest": rubric.rubric_digest,
            "query_digest": HASH,
            "reviewer_roster_digest": HASH,
            "partition_digest": HASH,
            "partial_gain": 0.5,
            "partial_counts_for_precision_recall": False,
            "missingness_policy": MissingnessPolicy.REQUIRE_COMPLETE,
            "tie_policy": TiePolicy.SCORE_DESC_CANDIDATE_ID,
            "agreement_method": AgreementMethod.EXACT_PERCENT_AGREEMENT,
            "resampling_unit": "query",
            "bootstrap_seed": data["bootstrap_seed"],
            "bootstrap_resamples": data["bootstrap_resamples"],
            "bootstrap_confidence": data["bootstrap_confidence"],
            "bootstrap_method": BootstrapMethod.PERCENTILE,
            "primary_metrics": (MetricName.PRECISION,),
            "secondary_metrics": (MetricName.RECALL, MetricName.NDCG, MetricName.COVERAGE),
        },
        "protocol_digest",
    )  # type: ignore[return-value]


def inventory_from(
    protocol: EvaluationProtocol, observations: list[object]
) -> GovernedPopulationInventory:
    members = []
    for item in observations:
        ranking = item["ranking"]  # type: ignore[index]
        row = make(
            RankedObservation,
            {
                "row_id": item["id"],
                "query_id": item["query"],
                "candidate_ids": tuple(value[0] for value in ranking),
                "scores": tuple(float(value[1]) for value in ranking),
                "labels": tuple(RelevanceLabel(value[2]) for value in ranking),
            },
            "ranking_digest",
        )
        members.append(
            make(
                GovernedPopulationMember,
                {
                    "observation_id": item["id"],
                    "query_id": item["query"],
                    "competition_id": item["competition"],
                    "team_id": item["team"],
                    "provider_id": item["provider"],
                    "window_id": item["window"],
                    "chronological_index": item["index"],
                    "minutes": item["minutes"],
                    "authority": EvidenceAuthority.IMPLEMENTATION_FIXTURE,
                    "ranking": row,
                },
                "member_digest",
            )
        )
    return make(
        GovernedPopulationInventory,
        {"protocol_digest": protocol.protocol_digest, "members": tuple(members)},
        "inventory_digest",
    )  # type: ignore[return-value]


def spec(
    protocol: EvaluationProtocol,
    inventory: GovernedPopulationInventory,
    kind: StressTestKind,
    fixture: dict[str, object],
) -> StressTestSpecification:
    return make(
        StressTestSpecification,
        {
            "test_id": f"stress-{kind.value}",
            "kind": kind,
            "protocol": protocol,
            "inventory": inventory,
            "metric": MetricName.PRECISION,
            "k": 1,
            "thresholds": (45, 90) if kind is StressTestKind.MINUTES_SAMPLE_SENSITIVITY else (),
            "walk_forward_cutoff_index": fixture["walk_forward_cutoff_index"]
            if kind is StressTestKind.TIME_WALK_FORWARD
            else None,
        },
        "specification_digest",
    )  # type: ignore[return-value]


def controls_from(
    fixture: dict[str, object], protocol: EvaluationProtocol, inventory: GovernedPopulationInventory
) -> tuple[object, ...]:
    rows = {member.observation_id: member.ranking for member in inventory.members}
    values = []
    for definition in fixture["controls"]:  # type: ignore[index]
        baseline = tuple(rows[row_id] for row_id in definition["baseline_observation_ids"])
        challenger = tuple(rows[row_id] for row_id in definition["challenger_observation_ids"])
        authority_data = definition["authority"]
        authority = make(
            ControlBaselineAuthority,
            {
                "kind": ControlAuthorityKind(authority_data["kind"]),
                "evidence_class": EvidenceAuthority(authority_data["evidence_class"]),
                "authority_id": authority_data["authority_id"],
                "source_artifact_digest": authority_data["source_artifact_digest"],
                "method_definition_digest": authority_data["method_definition_digest"],
                "baseline_ranking_digests": tuple(row.ranking_digest for row in baseline),
                "challenger_ranking_digests": tuple(row.ranking_digest for row in challenger),
            },
            "authority_digest",
        )
        assert authority.authority_digest == authority_data["authority_digest"]
        input = make(
            ControlInput,
            {
                "control": ControlKind(definition["control"]),
                "authority": authority,
                "k": definition["k"],
                "baseline_rows": baseline,
                "challenger_rows": challenger,
            },
            "input_digest",
        )
        values.append((input, evaluate_control(protocol, input)))
    return tuple(values)


def test_public_fixture_computed_and_unsupported_stresses_pin_identities() -> None:
    raw = (Path(__file__).parents[1] / "fixtures/w06/public-robustness-v1.json").read_bytes()
    fixture = fixture_data()
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA
    protocol = protocol_from(fixture)
    inventory = inventory_from(protocol, fixture["observations"])  # type: ignore[arg-type]
    computed = tuple(
        evaluate_stress_test(spec(protocol, inventory, kind, fixture)) for kind in StressTestKind
    )
    assert all(result.status.value == "COMPUTED" for result in computed)
    sparse = inventory_from(protocol, fixture["unsupported_observations"])  # type: ignore[arg-type]
    unsupported = evaluate_stress_test(
        spec(protocol, sparse, StressTestKind.SPLIT_HALF_RELIABILITY, fixture)
    )
    assert unsupported.status.value == "UNSUPPORTED_INSUFFICIENT_EVIDENCE"
    expected = fixture["expected_identities"]  # type: ignore[index]
    assert computed[0].result_digest == expected["computed_stress"]
    assert unsupported.result_digest == expected["unsupported_stress"]
    assert tuple(deficit.deficit_digest for deficit in unsupported.deficits) == tuple(
        expected["unsupported_deficits"]
    )


def test_controls_pair_applicability_failure_and_mutation_are_fixture_driven() -> None:
    fixture = fixture_data()
    protocol = protocol_from(fixture)
    inventory = inventory_from(protocol, fixture["observations"])  # type: ignore[arg-type]
    controls = controls_from(fixture, protocol, inventory)
    inputs, results = zip(*controls, strict=True)
    expected = fixture["expected_identities"]  # type: ignore[index]
    assert tuple(item.input_digest for item in inputs) == tuple(expected["control_inputs"])
    assert tuple(item.control_digest for item in results) == tuple(expected["control_results"])
    pair = results[-1]
    assert (
        pair.status.value == "UNSUPPORTED_INSUFFICIENT_EVIDENCE"
        and pair.control_digest == expected["pair_control"]
    )
    stresses = tuple(
        sorted(
            (
                evaluate_stress_test(spec(protocol, inventory, kind, fixture))
                for kind in StressTestKind
            ),
            key=lambda item: item.specification.kind.value,
        )
    )
    assessment = assess_applicability(
        inventory, stresses, tuple(sorted(results, key=lambda item: item.control.value))
    )
    assert assessment.assessment_digest == expected["applicability"]
    cases = tuple(
        make(
            FailureCase,
            {
                "case_id": item["case_id"],
                "query_id": item["query_id"],
                "category": FailureCategory(item["category"]),
                "severity": item["severity"],
                "evidence_digest": item["evidence_digest"],
            },
            "case_digest",
        )
        for item in fixture["failure_cases"]
    )  # type: ignore[index]
    register = register_failures(cases)
    assert register.register_digest == expected["failure_register"]
    mutated = fixture_data()
    mutated["observations"][0]["ranking"][0][1] = 99
    changed = inventory_from(protocol, mutated["observations"])
    assert changed.inventory_digest != inventory.inventory_digest


def test_incoherent_and_common_candidate_specs_are_typed_unsupported() -> None:
    fixture = fixture_data()
    protocol = protocol_from(fixture)
    for key, kind in (
        ("incoherent_observations", DeficitKind.INCOHERENT_LABEL_EVIDENCE),
        ("common_candidate_observations", DeficitKind.INSUFFICIENT_COMMON_CANDIDATES),
    ):
        observations = fixture[key]
        inventory = inventory_from(protocol, observations)  # type: ignore[arg-type]
        result = evaluate_stress_test(
            spec(protocol, inventory, StressTestKind.ROLLING_WINDOW_STABILITY, fixture)
        )
        assert result.status.value == "UNSUPPORTED_INSUFFICIENT_EVIDENCE"
        assert any(deficit.kind is kind for deficit in result.deficits)


def test_r3_witnesses_and_stale_children_reject_at_normal_construction() -> None:
    fixture = fixture_data()
    protocol = protocol_from(fixture)
    inventory = inventory_from(protocol, fixture["observations"])  # type: ignore[arg-type]
    split = evaluate_stress_test(
        spec(protocol, inventory, StressTestKind.SPLIT_HALF_RELIABILITY, fixture)
    )
    rolling = evaluate_stress_test(
        spec(protocol, inventory, StressTestKind.ROLLING_WINDOW_STABILITY, fixture)
    )
    bad = split.cohorts[0].model_copy(update={"ranked_rows": rolling.cohorts[0].ranked_rows})
    payload = split.model_dump(mode="python")
    payload["cohorts"] = (bad, *split.cohorts[1:])
    payload["result_digest"] = _digest(
        {key: value for key, value in payload.items() if key != "result_digest"}, "result_digest"
    )
    with pytest.raises(ValidationError, match="ranked rows"):
        type(split)(**payload)
    input, control = controls_from(fixture, protocol, inventory)[1]
    forged_input = input.model_copy(
        update={
            "baseline_rows": (inventory.members[2].ranking,),
            "challenger_rows": (inventory.members[3].ranking,),
        }
    )
    payload = control.model_dump(mode="python")
    payload["input"] = forged_input
    payload["control_digest"] = _digest(
        {key: value for key, value in payload.items() if key != "control_digest"}, "control_digest"
    )
    with pytest.raises(ValidationError, match="authority|rows|metric"):
        type(control)(**payload)


def test_original_numeric_child_substitution_parents_reject_at_normal_construction() -> None:
    """The three original re-signed numeric substitutions remain invalid."""
    fixture = fixture_data()
    protocol = protocol_from(fixture)
    inventory = inventory_from(protocol, fixture["observations"])  # type: ignore[arg-type]
    input, control = controls_from(fixture, protocol, inventory)[1]

    comparison = control.comparisons[0].model_dump(mode="python")  # type: ignore[union-attr]
    assert comparison["spearman"] == -0.19999999999999996
    comparison["spearman"] = 0.0
    comparison["result_digest"] = _digest(
        {key: value for key, value in comparison.items() if key != "result_digest"}, "result_digest"
    )
    changed_comparison = type(control.comparisons[0])(**comparison)  # type: ignore[index]
    payload = control.model_dump(mode="python")
    payload["comparisons"] = (changed_comparison,)
    payload["control_digest"] = _digest(
        {key: value for key, value in payload.items() if key != "control_digest"}, "control_digest"
    )
    assert payload["control_digest"] == (
        "fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb"
    )
    with pytest.raises(
        ValidationError, match="control comparison values must equal canonical derivation"
    ):
        type(control)(**payload)

    aggregate = control.baseline_result.model_dump(mode="python")  # type: ignore[union-attr]
    assert aggregate["value"] == aggregate["numerator"] == 1.0
    aggregate.update({"value": 0.0, "numerator": 0.0})
    aggregate["result_digest"] = _digest(
        {key: value for key, value in aggregate.items() if key != "result_digest"}, "result_digest"
    )
    changed_aggregate = type(control.baseline_result)(**aggregate)  # type: ignore[arg-type]
    payload = control.model_dump(mode="python")
    payload["baseline_result"] = changed_aggregate
    payload["control_digest"] = _digest(
        {key: value for key, value in payload.items() if key != "control_digest"}, "control_digest"
    )
    assert payload["control_digest"] == (
        "e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815"
    )
    with pytest.raises(
        ValidationError, match="control metric values must equal canonical derivation"
    ):
        type(control)(**payload)

    split = evaluate_stress_test(
        spec(protocol, inventory, StressTestKind.SPLIT_HALF_RELIABILITY, fixture)
    )
    aggregate = split.cohorts[0].metric_result.model_dump(mode="python")
    assert aggregate["value"] == 1.0 and aggregate["numerator"] == 2.0
    aggregate.update({"value": 0.0, "numerator": 0.0})
    aggregate["result_digest"] = _digest(
        {key: value for key, value in aggregate.items() if key != "result_digest"}, "result_digest"
    )
    changed_aggregate = type(split.cohorts[0].metric_result)(**aggregate)
    interval = split.cohorts[0].interval.model_dump(mode="python")
    assert interval["point_value"] == 1.0
    interval["metric_result_digest"] = changed_aggregate.result_digest
    interval["interval_digest"] = _digest(
        {key: value for key, value in interval.items() if key != "interval_digest"},
        "interval_digest",
    )
    changed_interval = type(split.cohorts[0].interval)(**interval)
    cohort = split.cohorts[0].model_dump(mode="python")
    cohort["metric_result"] = changed_aggregate
    cohort["interval"] = changed_interval
    cohort["cohort_digest"] = _digest(
        {key: value for key, value in cohort.items() if key != "cohort_digest"}, "cohort_digest"
    )
    changed_cohort = type(split.cohorts[0])(**cohort)
    payload = split.model_dump(mode="python")
    payload["cohorts"] = (changed_cohort, *split.cohorts[1:])
    comparisons = []
    for comparison in split.comparisons:
        child = comparison.model_dump(mode="python")
        if child["left_cohort_digest"] == split.cohorts[0].cohort_digest:
            child["left_cohort_digest"] = changed_cohort.cohort_digest
        if child["right_cohort_digest"] == split.cohorts[0].cohort_digest:
            child["right_cohort_digest"] = changed_cohort.cohort_digest
        child["comparison_digest"] = _digest(
            {key: value for key, value in child.items() if key != "comparison_digest"},
            "comparison_digest",
        )
        comparisons.append(type(comparison)(**child))
    payload["comparisons"] = tuple(comparisons)
    payload["result_digest"] = _digest(
        {key: value for key, value in payload.items() if key != "result_digest"}, "result_digest"
    )
    assert payload["result_digest"] == (
        "2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404"
    )
    with pytest.raises(
        ValidationError, match="stress metric and interval values must equal canonical derivation"
    ):
        type(split)(**payload)

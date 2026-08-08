"""Evaluate the preregistered W09 goal-event semantic uplift locally."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from uuid import NAMESPACE_URL, UUID, uuid5

from scouting.contracts.research import (
    FeatureWeight,
    ResearchFilters,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    canonical_research_digest,
)
from scouting.evaluation.research import research_version_pins
from scouting.modeling.research import (
    DEFAULT_FEATURE_MANIFEST_ROOT,
    DEFAULT_INDEX_ROOT,
    DEFAULT_MATRIX_ARTIFACT_ROOT,
    ResearchIndexBuildMode,
    discover_feature_matrix_manifest,
    load_feature_matrix,
    load_research_index,
)
from scouting.serving.research import ResearchServingService

DEFAULT_CONFIG = Path("configs/evaluation/w09-semantic-uplift-evaluation-v1.json")


class SemanticUpliftEvaluationError(RuntimeError):
    """Raised when the preregistered semantic evaluation cannot be reproduced."""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("baseline", "post_uplift"), required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--feature-manifest-root", type=Path, default=DEFAULT_FEATURE_MANIFEST_ROOT)
    parser.add_argument("--matrix-artifact-root", type=Path, default=DEFAULT_MATRIX_ARTIFACT_ROOT)
    parser.add_argument("--index-root", type=Path, default=DEFAULT_INDEX_ROOT)
    parser.add_argument(
        "--verification-input",
        action="store_true",
        help="Read only clean-root verification matrix and index artifacts.",
    )
    return parser


def _utc(value: object, *, label: str) -> datetime:
    if not isinstance(value, str):
        raise SemanticUpliftEvaluationError(f"{label} must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise SemanticUpliftEvaluationError(f"{label} must be timezone-aware")
    return parsed


def _load_config(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_bytes())
    if not isinstance(raw, dict):
        raise SemanticUpliftEvaluationError("evaluation config must be a JSON object")
    config = cast(dict[str, Any], raw)
    declared = config.get("configuration_digest")
    projection = {key: value for key, value in config.items() if key != "configuration_digest"}
    if declared != canonical_research_digest(projection):
        raise SemanticUpliftEvaluationError("evaluation configuration digest mismatch")
    if config.get("schema_version") != 1:
        raise SemanticUpliftEvaluationError("unsupported evaluation configuration schema")
    return config


def _goal_totals(matrix: object) -> tuple[int, dict[str, int]]:
    rows = getattr(matrix, "rows")
    by_position: dict[str, int] = {}
    for row in rows:
        goal = next(item for item in row.features if item.feature_name == "goals_per90")
        numerator = int(goal.numerator)
        if float(numerator) != goal.numerator:
            raise SemanticUpliftEvaluationError("goal numerator is not an exact integer")
        by_position[row.position_code] = by_position.get(row.position_code, 0) + numerator
    return sum(by_position.values()), dict(sorted(by_position.items()))


def _request(
    *,
    service: ResearchServingService,
    config: Mapping[str, Any],
    scenario: Mapping[str, Any],
    method: str,
    profile_name: str,
) -> ResearchQueryRequest:
    feature_names = cast(list[str], config["feature_names"])
    profiles = cast(dict[str, dict[str, float]], config["weight_profiles"])
    profile = profiles[profile_name]
    if list(profile) != feature_names:
        raise SemanticUpliftEvaluationError("weight profile order differs from feature registry")
    weights = tuple(
        FeatureWeight(feature_name=name, weight=float(profile[name])) for name in feature_names
    )
    case_id = f"{scenario['scenario_id']}::{method}::{profile_name}"
    draft = ResearchQueryRequest.model_construct(
        query_id=uuid5(NAMESPACE_URL, f"w09-semantic-uplift-v1::{case_id}"),
        requested_at=_utc(config["requested_at"], label="requested_at"),
        feature_cutoff_ts=service.pins.feature_cutoff_ts,
        pins=service.pins,
        mode=ResearchQueryMode.EXEMPLAR,
        method=ResearchMethod(method),
        exemplar_grain_id=scenario["exemplar_grain_id"],
        profile=(),
        weights=weights,
        filters=ResearchFilters(
            competition_id=UUID(cast(str, scenario["target_competition_id"])),
            season_id=cast(str, scenario["target_season_id"]),
            position_codes=(cast(Any, scenario["position_code"]),),
            minimum_minutes=float(config["minimum_minutes"]),
            excluded_player_ids=(),
        ),
        limit=int(config["limit"]),
        query_digest="0" * 64,
    )
    return ResearchQueryRequest(
        query_id=draft.query_id,
        requested_at=draft.requested_at,
        feature_cutoff_ts=draft.feature_cutoff_ts,
        pins=draft.pins,
        mode=draft.mode,
        method=draft.method,
        exemplar_grain_id=draft.exemplar_grain_id,
        profile=draft.profile,
        weights=draft.weights,
        filters=draft.filters,
        limit=draft.limit,
        query_digest=canonical_research_digest(draft.digest_projection()),
    )


def _case_payload(
    *,
    service: ResearchServingService,
    config: Mapping[str, Any],
    scenario: Mapping[str, Any],
    method: str,
    profile_name: str,
) -> dict[str, Any]:
    request = _request(
        service=service,
        config=config,
        scenario=scenario,
        method=method,
        profile_name=profile_name,
    )
    result = service.execute_query(
        request,
        generated_at=_utc(config["generated_at"], label="generated_at"),
    )
    expected_scored = int(scenario["expected_scored_rows"])
    if result.population.scored_rows != expected_scored:
        raise SemanticUpliftEvaluationError(
            f"{scenario['scenario_id']} scored {result.population.scored_rows}, expected "
            f"{expected_scored}"
        )
    candidates: list[dict[str, Any]] = []
    for candidate in result.candidates:
        goal = next(item for item in candidate.contributions if item.feature_name == "goals_per90")
        payload: dict[str, Any] = {
            "rank": candidate.rank,
            "grain_id": candidate.grain_id,
            "display_name": candidate.display_name,
            "score": candidate.score,
            "goal_contribution": goal.contribution,
        }
        if request.method is ResearchMethod.WEIGHTED_EUCLIDEAN:
            squared_distance = candidate.score * candidate.score
            payload["goal_squared_distance_share"] = (
                goal.contribution / squared_distance if squared_distance else 0.0
            )
        candidates.append(payload)
    return {
        "case_id": f"{scenario['scenario_id']}::{method}::{profile_name}",
        "scenario_id": scenario["scenario_id"],
        "position_code": scenario["position_code"],
        "method": method,
        "weight_profile": profile_name,
        "query_digest": request.query_digest,
        "result_digest": result.result_digest,
        "population": result.population.model_dump(mode="json"),
        "candidates": candidates,
    }


def _weight_sensitivity(cases: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    indexed = {cast(str, item["case_id"]): item for item in cases}
    output: list[dict[str, Any]] = []
    for method in ("weighted_euclidean", "weighted_cosine"):
        equal = indexed[f"kante-england-md::{method}::equal"]
        defensive = indexed[f"kante-england-md::{method}::defensive_reweight"]
        equal_names = [
            item["display_name"] for item in cast(list[dict[str, Any]], equal["candidates"])
        ]
        defensive_names = [
            item["display_name"] for item in cast(list[dict[str, Any]], defensive["candidates"])
        ]
        output.append(
            {
                "method": method,
                "top_10_overlap": len(set(equal_names) & set(defensive_names)),
                "entrants": [name for name in defensive_names if name not in equal_names],
                "exits": [name for name in equal_names if name not in defensive_names],
            }
        )
    return output


def _compare(
    current: Sequence[Mapping[str, Any]],
    baseline_path: Path,
    *,
    minimum_overlap: int,
) -> tuple[list[dict[str, Any]], bool]:
    baseline_raw = cast(dict[str, Any], json.loads(baseline_path.read_bytes()))
    baseline_cases = {
        cast(str, item["case_id"]): item
        for item in cast(list[dict[str, Any]], baseline_raw["cases"])
    }
    comparisons: list[dict[str, Any]] = []
    passed = True
    for case in current:
        case_id = cast(str, case["case_id"])
        before = baseline_cases.get(case_id)
        if before is None:
            raise SemanticUpliftEvaluationError(f"baseline is missing case {case_id}")
        before_population = cast(dict[str, Any], before["population"])
        after_population = cast(dict[str, Any], case["population"])
        population_unchanged = before_population == after_population
        before_names = [
            item["display_name"] for item in cast(list[dict[str, Any]], before["candidates"])
        ]
        after_names = [
            item["display_name"] for item in cast(list[dict[str, Any]], case["candidates"])
        ]
        overlap = len(set(before_names) & set(after_names))
        overlap_required = case["position_code"] != "GK"
        case_passed = population_unchanged and (not overlap_required or overlap >= minimum_overlap)
        passed = passed and case_passed
        comparisons.append(
            {
                "case_id": case_id,
                "population_unchanged": population_unchanged,
                "top_10_overlap": overlap,
                "minimum_overlap_required": minimum_overlap if overlap_required else None,
                "entrants": [name for name in after_names if name not in before_names],
                "exits": [name for name in before_names if name not in after_names],
                "passed": case_passed,
            }
        )
    return comparisons, passed


def _write_immutable(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise SemanticUpliftEvaluationError(f"refusing to replace incompatible output: {path}")
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        config = _load_config(arguments.config)
        mode = (
            ResearchIndexBuildMode.VERIFICATION
            if arguments.verification_input
            else ResearchIndexBuildMode.PRODUCTION
        )
        manifest_path = discover_feature_matrix_manifest(
            arguments.feature_manifest_root,
            mode=mode,
        )
        matrix = load_feature_matrix(
            manifest_path,
            artifact_root=arguments.matrix_artifact_root,
            mode=mode,
        )
        index = load_research_index(
            arguments.index_root,
            matrix_manifest=matrix.manifest,
            mode=mode,
        )
        service = ResearchServingService(
            matrix=matrix,
            index=index,
            pins=research_version_pins(matrix.manifest, index.manifest),
        )
        cases = [
            _case_payload(
                service=service,
                config=config,
                scenario=scenario,
                method=method,
                profile_name=profile_name,
            )
            for scenario in cast(list[dict[str, Any]], config["scenarios"])
            for method in cast(list[str], scenario["methods"])
            for profile_name in cast(list[str], scenario["weight_profiles"])
        ]
        total_goals, goals_by_position = _goal_totals(matrix)
        source_reconciliation = cast(dict[str, Any], config["source_reconciliation"])
        expected_goals = int(
            source_reconciliation[
                "current_goal_numerator"
                if arguments.phase == "baseline"
                else "expected_post_uplift_goal_numerator"
            ]
        )
        if total_goals != expected_goals:
            raise SemanticUpliftEvaluationError(
                f"goal numerator total {total_goals} does not equal expected {expected_goals}"
            )
        comparisons: list[dict[str, Any]] = []
        criteria_passed: bool | None = None
        if arguments.phase == "post_uplift":
            if arguments.baseline is None:
                raise SemanticUpliftEvaluationError("post_uplift evaluation requires --baseline")
            comparisons, criteria_passed = _compare(
                cases,
                arguments.baseline,
                minimum_overlap=int(
                    cast(dict[str, Any], config["success_criteria"])[
                        "minimum_non_goalkeeper_top_10_overlap"
                    ]
                ),
            )
            if not criteria_passed:
                raise SemanticUpliftEvaluationError("preregistered comparison criteria failed")
        elif arguments.baseline is not None:
            raise SemanticUpliftEvaluationError("baseline phase does not accept --baseline")
        draft: dict[str, Any] = {
            "schema_version": 1,
            "evaluation_id": config["evaluation_id"],
            "configuration_digest": config["configuration_digest"],
            "phase": arguments.phase,
            "claim_boundary": config["claim_boundary"],
            "authority": service.pins.model_dump(mode="json"),
            "matrix_row_count": len(matrix.rows),
            "goal_numerator_total": total_goals,
            "goal_numerator_by_position": goals_by_position,
            "source_reconciliation": source_reconciliation,
            "cases": cases,
            "weight_sensitivity": _weight_sensitivity(cases),
            "baseline_comparisons": comparisons,
            "preregistered_criteria_passed": criteria_passed,
            "limitations": [
                "This evaluation measures semantic correction, deterministic execution and "
                "ranking churn; it does not measure football relevance.",
                "Top-ten overlap is a preregistered rejection guard, not a quality threshold.",
                "All governed minutes are conservative lower bounds.",
            ],
        }
        draft["evaluation_digest"] = canonical_research_digest(draft)
        payload = (
            json.dumps(draft, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"
        ).encode()
        _write_immutable(arguments.output, payload)
    except (OSError, ValueError, KeyError, SemanticUpliftEvaluationError) as exc:
        print(f"W09 semantic uplift evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "evaluation_digest": draft["evaluation_digest"],
                "goal_numerator_total": total_goals,
                "output": str(arguments.output),
                "phase": arguments.phase,
                "query_case_count": len(cases),
                "state": "confirmed",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

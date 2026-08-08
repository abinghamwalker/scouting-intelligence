"""Deterministic engineering evaluation for the frozen W09 retained-data suite."""

from __future__ import annotations

import json
import math
import stat
from collections import defaultdict
from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Literal, cast
from uuid import UUID

import numpy as np
from pydantic import AfterValidator, Field, ValidationError, model_validator

from scouting.contracts.evidence import Sha256Digest
from scouting.contracts.numerics import (
    StableNormalizationError,
    stable_finite_sum,
    stable_weighted_unit_components,
)
from scouting.contracts.primitives import (
    ContractModel,
    NonEmptyString,
    NonNegativeInt,
    PositiveInt,
    SchemaVersion,
    StrictUuid,
    UtcInstant,
)
from scouting.contracts.research import (
    RESEARCH_CLAIM_BOUNDARY,
    FeatureMatrixManifest,
    FeatureMatrixRow,
    FeatureValueState,
    FeatureWeight,
    NamedFeatureValue,
    ResearchFilters,
    ResearchIndexManifest,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchQueryResult,
    ResearchVersionPins,
    RetrievalPopulationCounts,
    canonical_research_digest,
)
from scouting.contracts.validation import revalidate_exact_contract
from scouting.serving.research import ResearchServingError, ResearchServingService
from scouting.storage.formats import FormatError, canonical_json_bytes

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_EVALUATION_CONFIG_PATH = (
    PROJECT_ROOT / "configs/evaluation/w09-frozen-retrieval-evaluation-v1.json"
)

_REQUIRED_LIMITATIONS = (
    (
        "Historical resemblance is not football relevance or recruitment usefulness, and "
        "the frozen suite contains no relevance labels."
    ),
    (
        "All 1,975 eligible retained rows use conservative-lower-bound minutes, so their "
        "per-90 rates may be overstated."
    ),
    (
        "Only five domestic competitions pass the current eligibility and closed-window "
        "policy; this is not current-market coverage."
    ),
)
_REQUIRED_WEAKNESSES = (
    (
        "G-RW4 expert validation does not exist; no football-quality, recommendation, value, "
        "availability, fit or outcome claim is supported."
    ),
    (
        "Weight-perturbation stability metrics are sensitivity evidence only and do not "
        "validate rankings or define a football-acceptable threshold."
    ),
)


def _reject_negative_zero(value: float) -> float:
    if value == 0.0 and math.copysign(1.0, value) < 0.0:
        raise ValueError("negative zero is not canonical")
    return value


type FiniteFloat = Annotated[
    float,
    Field(strict=True, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]
type NonNegativeFloat = Annotated[
    float,
    Field(strict=True, ge=0.0, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]
type PositiveFloat = Annotated[
    float,
    Field(strict=True, gt=0.0, allow_inf_nan=False),
    AfterValidator(_reject_negative_zero),
]


class ResearchEvaluationError(ValueError):
    """A frozen evaluation authority or computed witness failed closed."""


class FilterWitnessKind(StrEnum):
    """Closed engineering behaviours witnessed by frozen retained-data queries."""

    EXEMPLAR_SELF_EXCLUSION = "exemplar_self_exclusion"
    POSITION_FILTER = "position_filter"
    MINIMUM_MINUTES_POLICY_FLOOR = "minimum_minutes_policy_floor"
    MINIMUM_MINUTES_ABOVE_POLICY = "minimum_minutes_above_policy"
    EXPLICIT_PLAYER_EXCLUSION = "explicit_player_exclusion"
    FULL_SCORE_BEFORE_LIMIT = "full_score_before_limit"
    EMPTY_ADMISSION = "empty_admission"


class FrozenQueryCase(ContractModel):
    """One exact real-grain query definition inside the retained frozen suite."""

    schema_version: SchemaVersion = 1
    case_id: NonEmptyString
    query_id: StrictUuid
    mode: ResearchQueryMode
    method: ResearchMethod
    source_grain_id: NonEmptyString
    weights: Annotated[tuple[FeatureWeight, ...], Field(min_length=1)]
    filters: ResearchFilters
    limit: Annotated[int, Field(strict=True, ge=1, le=100)]
    witnesses: tuple[FilterWitnessKind, ...] = ()
    case_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"case_digest"})

    @model_validator(mode="after")
    def case_is_coherent(self) -> FrozenQueryCase:
        names = tuple(item.feature_name for item in self.weights)
        if len(names) != len(set(names)) or not any(item.weight > 0.0 for item in self.weights):
            raise ValueError("case weights must be unique with at least one positive item")
        if len(self.witnesses) != len(set(self.witnesses)):
            raise ValueError("case witnesses must be unique")
        if self.case_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("case digest must match its canonical projection")
        return self


class FrozenWeightPerturbation(ContractModel):
    """One explicitly bounded case pair used only for sensitivity evidence."""

    schema_version: SchemaVersion = 1
    perturbation_id: NonEmptyString
    baseline_case_id: NonEmptyString
    perturbed_case_id: NonEmptyString
    maximum_absolute_weight_delta: PositiveFloat
    top_k: Annotated[int, Field(strict=True, ge=1, le=100)]
    perturbation_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"perturbation_digest"})

    @model_validator(mode="after")
    def perturbation_is_coherent(self) -> FrozenWeightPerturbation:
        if self.baseline_case_id == self.perturbed_case_id:
            raise ValueError("perturbation cases must be distinct")
        if self.perturbation_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("perturbation digest must match its canonical projection")
        return self


class FrozenResearchEvaluationSuite(ContractModel):
    """Self-digested retained-data suite with exact matrix/index/query authority."""

    schema_version: SchemaVersion = 1
    suite_id: StrictUuid
    suite_version: Literal["w09-frozen-retrieval-evaluation-v1"]
    requested_at: UtcInstant
    first_generated_at: UtcInstant
    second_generated_at: UtcInstant
    evaluated_at: UtcInstant
    pins: ResearchVersionPins
    feature_names: Annotated[tuple[NonEmptyString, ...], Field(min_length=1)]
    matrix_row_count: Literal[1975]
    unique_matrix_player_count: Literal[1965]
    source_player_count: Literal[3603]
    eligible_competition_count: Literal[5]
    minimum_minutes_policy: PositiveFloat
    all_eligible_minutes_are_lower_bound: Literal[True]
    scaler_center_statistic: Literal["median"]
    scaler_scale_statistic: Literal["interquartile_range"]
    scaler_quantile_method: Literal["linear"]
    constant_feature_policy: Literal["retain_with_unit_scale"]
    cases: Annotated[tuple[FrozenQueryCase, ...], Field(min_length=1)]
    perturbations: Annotated[tuple[FrozenWeightPerturbation, ...], Field(min_length=1)]
    limitations: tuple[NonEmptyString, ...]
    weaknesses: tuple[NonEmptyString, ...]
    contains_synthetic_rows: Literal[False] = False
    suite_digest: Sha256Digest
    claim_boundary: Literal["historical_resemblance_research_only"] = RESEARCH_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"suite_digest"})

    @model_validator(mode="after")
    def suite_is_coherent(self) -> FrozenResearchEvaluationSuite:
        if not (
            self.pins.feature_cutoff_ts
            <= self.requested_at
            <= self.first_generated_at
            < self.second_generated_at
            <= self.evaluated_at
        ):
            raise ValueError("suite clocks must be ordered after the pinned cutoff")
        if self.minimum_minutes_policy != 450.0:
            raise ValueError("frozen suite minimum-minutes policy must remain exactly 450")
        if len(self.feature_names) != len(set(self.feature_names)):
            raise ValueError("suite feature names must be unique")
        case_ids = tuple(item.case_id for item in self.cases)
        query_ids = tuple(item.query_id for item in self.cases)
        if len(case_ids) != len(set(case_ids)) or len(query_ids) != len(set(query_ids)):
            raise ValueError("suite case and query identities must be unique")
        if {item.mode for item in self.cases} != set(ResearchQueryMode) or {
            item.method for item in self.cases
        } != set(ResearchMethod):
            raise ValueError("suite must cover both query modes and both retrieval methods")
        observed_witnesses = {value for item in self.cases for value in item.witnesses}
        if observed_witnesses != set(FilterWitnessKind):
            raise ValueError("suite must declare every required filter witness")
        if self.limitations != _REQUIRED_LIMITATIONS or self.weaknesses != _REQUIRED_WEAKNESSES:
            raise ValueError("suite claim limitations and weaknesses are exact and cannot drift")
        cases_by_id = {item.case_id: item for item in self.cases}
        perturbation_ids = tuple(item.perturbation_id for item in self.perturbations)
        if len(perturbation_ids) != len(set(perturbation_ids)):
            raise ValueError("suite perturbation identities must be unique")
        for perturbation in self.perturbations:
            if (
                perturbation.baseline_case_id not in cases_by_id
                or perturbation.perturbed_case_id not in cases_by_id
            ):
                raise ValueError("perturbation cases must exist in the frozen suite")
        if self.suite_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("suite digest must match its canonical projection")
        return self


class QueryReproducibilityWitness(ContractModel):
    schema_version: SchemaVersion = 1
    case_id: NonEmptyString
    query: ResearchQueryRequest
    first_result: ResearchQueryResult
    second_generated_at: UtcInstant
    second_result_id: StrictUuid
    second_result_digest: Sha256Digest
    candidate_order_digest: Sha256Digest
    score_digest: Sha256Digest
    explanation_digest: Sha256Digest
    population_reproduced: Literal[True]
    candidate_order_reproduced: Literal[True]
    scores_reproduced: Literal[True]
    explanations_reproduced: Literal[True]
    witness_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"witness_digest"})

    @model_validator(mode="after")
    def witness_is_coherent(self) -> QueryReproducibilityWitness:
        if self.first_result.request != self.query:
            raise ValueError("reproducibility result must bind the exact frozen query")
        if (
            self.second_generated_at <= self.first_result.generated_at
            or self.second_result_id != self.first_result.result_id
            or self.second_result_digest != self.first_result.result_digest
        ):
            raise ValueError("second execution must reproduce exact result identity and digest")
        if self.witness_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("reproducibility witness digest is incompatible")
        return self


class ExplanationConsistencyWitness(ContractModel):
    schema_version: SchemaVersion = 1
    case_id: NonEmptyString
    candidate_rows_checked: NonNegativeInt
    contribution_terms_checked: NonNegativeInt
    zero_weight_terms_checked: NonNegativeInt
    deterministic_tie_pairs_checked: NonNegativeInt
    missing_feature_count: Literal[0]
    scaler_semantics: Literal["median_iqr_linear_constant_unit_scale"]
    explanation_digest: Sha256Digest


class FilterBehaviourWitness(ContractModel):
    schema_version: SchemaVersion = 1
    case_id: NonEmptyString
    kind: FilterWitnessKind
    population: RetrievalPopulationCounts
    passed: Literal[True]
    witness_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"witness_digest"})

    @model_validator(mode="after")
    def witness_is_coherent(self) -> FilterBehaviourWitness:
        if self.witness_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("filter witness digest is incompatible")
        return self


class RankDisplacement(ContractModel):
    grain_id: NonEmptyString
    baseline_rank: PositiveInt
    perturbed_rank: PositiveInt
    absolute_displacement: NonNegativeInt

    @model_validator(mode="after")
    def displacement_is_coherent(self) -> RankDisplacement:
        if self.absolute_displacement != abs(self.baseline_rank - self.perturbed_rank):
            raise ValueError("absolute rank displacement is inconsistent")
        return self


class ScoreChange(ContractModel):
    grain_id: NonEmptyString
    baseline_score: NonNegativeFloat
    perturbed_score: NonNegativeFloat
    absolute_change: NonNegativeFloat

    @model_validator(mode="after")
    def change_is_coherent(self) -> ScoreChange:
        if not math.isclose(
            self.absolute_change,
            abs(self.baseline_score - self.perturbed_score),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError("absolute score change is inconsistent")
        return self


class WeightStabilityWitness(ContractModel):
    schema_version: SchemaVersion = 1
    perturbation_id: NonEmptyString
    baseline_case_id: NonEmptyString
    perturbed_case_id: NonEmptyString
    maximum_absolute_weight_delta: PositiveFloat
    observed_maximum_absolute_weight_delta: PositiveFloat
    top_k: PositiveInt
    top_k_overlap_count: NonNegativeInt
    top_k_overlap_fraction: NonNegativeFloat
    rank_displacements: tuple[RankDisplacement, ...]
    mean_absolute_rank_displacement: NonNegativeFloat
    score_changes: tuple[ScoreChange, ...]
    sensitivity_only: Literal[True]
    validates_ranking_quality: Literal[False]
    witness_digest: Sha256Digest

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"witness_digest"})

    @model_validator(mode="after")
    def witness_is_coherent(self) -> WeightStabilityWitness:
        if self.observed_maximum_absolute_weight_delta > (
            self.maximum_absolute_weight_delta
        ) and not math.isclose(
            self.observed_maximum_absolute_weight_delta,
            self.maximum_absolute_weight_delta,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError("observed perturbation exceeds its declared bound")
        if not math.isclose(
            self.top_k_overlap_fraction,
            self.top_k_overlap_count / self.top_k,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError("top-k overlap fraction is inconsistent")
        expected_mean = (
            sum(item.absolute_displacement for item in self.rank_displacements)
            / len(self.rank_displacements)
            if self.rank_displacements
            else 0.0
        )
        if not math.isclose(
            self.mean_absolute_rank_displacement,
            expected_mean,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError("mean rank displacement is inconsistent")
        if self.witness_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("stability witness digest is incompatible")
        return self


class CompetitionCoverage(ContractModel):
    competition_id: StrictUuid
    competition_name: NonEmptyString
    matrix_rows: PositiveInt
    queried_case_count: NonNegativeInt
    returned_unique_grain_count: NonNegativeInt


class EvaluationCoverage(ContractModel):
    schema_version: SchemaVersion = 1
    matrix_row_count: Literal[1975]
    unique_matrix_player_count: Literal[1965]
    source_player_count: Literal[3603]
    query_case_count: PositiveInt
    source_grain_count: PositiveInt
    unique_returned_grain_count: NonNegativeInt
    unique_returned_player_count: NonNegativeInt
    returned_candidate_matrix_coverage: NonNegativeFloat
    total_scored_row_evaluations: NonNegativeInt
    competition_coverage: Annotated[tuple[CompetitionCoverage, ...], Field(min_length=5)]

    @model_validator(mode="after")
    def coverage_is_coherent(self) -> EvaluationCoverage:
        if not math.isclose(
            self.returned_candidate_matrix_coverage,
            self.unique_returned_grain_count / self.matrix_row_count,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError("returned-candidate matrix coverage is inconsistent")
        if sum(item.matrix_rows for item in self.competition_coverage) != self.matrix_row_count:
            raise ValueError("competition matrix coverage must exhaust the matrix")
        return self


class ResearchRetrievalEvaluationResult(ContractModel):
    """Canonical engineering evidence; it deliberately contains no relevance metric."""

    schema_version: SchemaVersion = 1
    suite_id: StrictUuid
    suite_version: Literal["w09-frozen-retrieval-evaluation-v1"]
    suite_digest: Sha256Digest
    evaluated_at: UtcInstant
    pins: ResearchVersionPins
    query_witnesses: Annotated[tuple[QueryReproducibilityWitness, ...], Field(min_length=1)]
    explanation_witnesses: Annotated[tuple[ExplanationConsistencyWitness, ...], Field(min_length=1)]
    filter_witnesses: Annotated[tuple[FilterBehaviourWitness, ...], Field(min_length=1)]
    stability_witnesses: Annotated[tuple[WeightStabilityWitness, ...], Field(min_length=1)]
    coverage: EvaluationCoverage
    limitations: tuple[NonEmptyString, ...]
    weaknesses: tuple[NonEmptyString, ...]
    result_digest: Sha256Digest
    claim_boundary: Literal["historical_resemblance_research_only"] = RESEARCH_CLAIM_BOUNDARY

    def digest_projection(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"result_digest"})

    @model_validator(mode="after")
    def result_is_coherent(self) -> ResearchRetrievalEvaluationResult:
        case_ids = tuple(item.case_id for item in self.query_witnesses)
        if tuple(item.case_id for item in self.explanation_witnesses) != case_ids:
            raise ValueError("explanation witnesses must follow exact query order")
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("evaluation query case identities must be unique")
        if self.limitations != _REQUIRED_LIMITATIONS or self.weaknesses != _REQUIRED_WEAKNESSES:
            raise ValueError("evaluation claim limitations and weaknesses cannot drift")
        if self.result_digest != canonical_research_digest(self.digest_projection()):
            raise ValueError("evaluation result digest is incompatible")
        return self


def research_version_pins(
    matrix: FeatureMatrixManifest,
    index: ResearchIndexManifest,
) -> ResearchVersionPins:
    """Derive the only compatible research pin set from exact accepted manifests."""

    return ResearchVersionPins(
        feature_cutoff_ts=matrix.feature_cutoff_ts,
        dataset_version=matrix.dataset_version,
        dataset_manifest_digest=matrix.dataset_manifest_digest,
        identity_bundle_digest=matrix.identity_bundle_digest,
        canonical_build_digest=matrix.canonical_build_digest,
        matrix_version=matrix.matrix_version,
        matrix_manifest_digest=matrix.manifest_digest,
        matrix_digest=matrix.matrix_digest,
        feature_registry_version=matrix.feature_registry_version,
        feature_registry_digest=matrix.feature_registry_digest,
        eligibility_policy_version=matrix.eligibility_policy_version,
        eligibility_policy_digest=matrix.eligibility_policy_digest,
        model_version=index.model_version,
        model_configuration_digest=index.model_configuration_digest,
        scorer_version=index.scorer_version,
        scorer_code_digest=index.scorer_code_digest,
        index_version=index.index_version,
        index_manifest_digest=index.manifest_digest,
        catalogue_digest=index.catalogue_digest,
    )


def _safe_canonical_json(path: Path) -> bytes:
    absolute = path.absolute()
    for ancestor in (absolute, *absolute.parents):
        if not ancestor.exists():
            continue
        if ancestor.is_symlink() or ancestor.resolve(strict=True) != ancestor:
            raise ResearchEvaluationError("frozen evaluation suite path has an unsafe ancestor")
    if absolute.is_symlink() or not absolute.is_file():
        raise ResearchEvaluationError("frozen evaluation suite path is absent or unsafe")
    try:
        metadata = absolute.lstat()
    except OSError as exc:
        raise ResearchEvaluationError("frozen evaluation suite cannot be inspected") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise ResearchEvaluationError("frozen evaluation suite must be a regular file")
    try:
        payload = absolute.read_bytes()
        decoded = json.loads(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResearchEvaluationError("frozen evaluation suite is not strict JSON") from exc
    try:
        canonical = canonical_json_bytes(decoded)
    except FormatError as exc:
        raise ResearchEvaluationError("frozen evaluation suite is not canonical JSON") from exc
    if type(decoded) is not dict or canonical != payload:
        raise ResearchEvaluationError("frozen evaluation suite must be one canonical JSON object")
    return payload


def _fresh[T: ContractModel](value: T, model: type[T], *, label: str) -> T:
    return revalidate_exact_contract(
        value,
        model,
        label=label,
        error_type=ResearchEvaluationError,
    )


def _row_feature_values(row: FeatureMatrixRow) -> Mapping[str, float]:
    values: dict[str, float] = {}
    for feature in row.features:
        if (
            feature.state not in {FeatureValueState.VALUE, FeatureValueState.ZERO}
            or feature.value is None
        ):
            raise ResearchEvaluationError("frozen source row contains missing feature evidence")
        values[feature.feature_name] = feature.value
    return values


def _case_query(
    suite: FrozenResearchEvaluationSuite,
    case: FrozenQueryCase,
    rows_by_grain: Mapping[str, FeatureMatrixRow],
) -> ResearchQueryRequest:
    source = rows_by_grain.get(case.source_grain_id)
    if source is None:
        raise ResearchEvaluationError("frozen query source grain is outside the governed matrix")
    source_values = _row_feature_values(source)
    active_names = tuple(item.feature_name for item in case.weights)
    profile = (
        tuple(
            NamedFeatureValue(feature_name=name, value=source_values[name]) for name in active_names
        )
        if case.mode is ResearchQueryMode.WEIGHTED_PROFILE
        else ()
    )
    draft = ResearchQueryRequest.model_construct(
        query_id=case.query_id,
        requested_at=suite.requested_at,
        feature_cutoff_ts=suite.pins.feature_cutoff_ts,
        pins=suite.pins,
        mode=case.mode,
        method=case.method,
        exemplar_grain_id=(
            case.source_grain_id if case.mode is ResearchQueryMode.EXEMPLAR else None
        ),
        profile=profile,
        weights=case.weights,
        filters=case.filters,
        limit=case.limit,
        query_digest="0" * 64,
    )
    try:
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
    except (KeyError, ValidationError) as exc:
        raise ResearchEvaluationError("frozen query cannot be materialised") from exc


def _validate_perturbations(suite: FrozenResearchEvaluationSuite) -> None:
    cases = {item.case_id: item for item in suite.cases}
    for perturbation in suite.perturbations:
        baseline = cases[perturbation.baseline_case_id]
        changed = cases[perturbation.perturbed_case_id]
        if (
            baseline.mode is not changed.mode
            or baseline.method is not changed.method
            or baseline.source_grain_id != changed.source_grain_id
            or baseline.filters != changed.filters
            or baseline.limit != changed.limit
            or tuple(item.feature_name for item in baseline.weights)
            != tuple(item.feature_name for item in changed.weights)
            or perturbation.top_k > min(baseline.limit, changed.limit)
        ):
            raise ResearchEvaluationError(
                "perturbation cases may differ only by bounded feature weights and identity"
            )
        deltas = tuple(
            abs(left.weight - right.weight)
            for left, right in zip(baseline.weights, changed.weights, strict=True)
        )
        observed = max(deltas)
        exceeds_bound = observed > perturbation.maximum_absolute_weight_delta and not math.isclose(
            observed,
            perturbation.maximum_absolute_weight_delta,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
        if not any(delta > 0.0 for delta in deltas) or exceeds_bound:
            raise ResearchEvaluationError("declared weight perturbation is absent or out of bound")


def load_frozen_evaluation_suite(
    path: Path,
    *,
    service: ResearchServingService,
) -> FrozenResearchEvaluationSuite:
    """Load one canonical suite and bind every real grain and pin to the service."""

    if type(service) is not ResearchServingService:
        raise TypeError("service must be an exact ResearchServingService")
    payload = _safe_canonical_json(path)
    try:
        suite = FrozenResearchEvaluationSuite.model_validate_json(payload)
    except ValidationError as exc:
        raise ResearchEvaluationError("frozen evaluation suite contract rejected") from exc
    _validate_suite_authority(suite, service=service)
    return suite


def _validate_suite_authority(
    suite: FrozenResearchEvaluationSuite,
    *,
    service: ResearchServingService,
) -> None:
    """Bind an already validated suite to the exact live matrix/index authority."""

    try:
        suite.pins.assert_compatible(service.pins)
    except ValueError as exc:
        raise ResearchEvaluationError("frozen evaluation pins are stale or incompatible") from exc
    matrix = service.matrix_manifest
    rows = service.matrix_rows
    if (
        suite.feature_names != service.index_manifest.feature_names
        or suite.feature_names != matrix.feature_names
        or suite.matrix_row_count != matrix.matrix_row_count
        or suite.unique_matrix_player_count != matrix.unique_matrix_player_count
        or suite.source_player_count != matrix.catalogue_player_count
        or len(rows) != suite.matrix_row_count
        or len({row.player_id for row in rows}) != suite.unique_matrix_player_count
        or not all(row.minute_state.value == "conservative_lower_bound" for row in rows)
    ):
        raise ResearchEvaluationError("frozen suite population or feature authority drifts")
    rows_by_grain = {row.grain_id: row for row in rows}
    source_rows: list[FeatureMatrixRow] = []
    for case in suite.cases:
        source = rows_by_grain.get(case.source_grain_id)
        if source is None or source.contains_synthetic_data:
            raise ResearchEvaluationError("frozen suite contains an absent or synthetic grain")
        if source.competition_id != case.filters.competition_id:
            raise ResearchEvaluationError("frozen source grain and query competition drift")
        indices = tuple(suite.feature_names.index(item.feature_name) for item in case.weights)
        if indices != tuple(sorted(indices)):
            raise ResearchEvaluationError(
                "frozen case feature weights must be an ordered registry subset"
            )
        _case_query(suite, case, rows_by_grain)
        source_rows.append(source)
    if {row.position_code for row in source_rows} != {"GK", "DF", "MD", "FW"}:
        raise ResearchEvaluationError("frozen suite must cover all four matrix positions")
    if len({row.competition_id for row in source_rows}) < 3:
        raise ResearchEvaluationError("frozen suite must cover at least three competitions")
    if len({row.competition_id for row in rows}) != suite.eligible_competition_count:
        raise ResearchEvaluationError("eligible competition count drifts from frozen evidence")
    _validate_perturbations(suite)


def _same_float(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)


def _scaler(
    rows: tuple[FeatureMatrixRow, ...],
    registry: tuple[str, ...],
) -> tuple[np.ndarray, np.ndarray]:
    raw = np.ascontiguousarray(
        [[_row_feature_values(row)[name] for name in registry] for row in rows],
        dtype="<f8",
    )
    center = np.ascontiguousarray(np.median(raw, axis=0), dtype="<f8")
    lower = np.quantile(raw, 0.25, axis=0, method="linear")
    upper = np.quantile(raw, 0.75, axis=0, method="linear")
    scale = np.ascontiguousarray(upper - lower, dtype="<f8")
    scale[scale == 0.0] = 1.0
    center[center == 0.0] = 0.0
    if not np.all(np.isfinite(center)) or not np.all(np.isfinite(scale)) or np.any(scale <= 0.0):
        raise ResearchEvaluationError("evaluation scaler reproduction failed")
    return center, scale


def _verify_explanations(
    *,
    case: FrozenQueryCase,
    query: ResearchQueryRequest,
    result: ResearchQueryResult,
    rows: tuple[FeatureMatrixRow, ...],
    registry: tuple[str, ...],
    center: np.ndarray,
    scale: np.ndarray,
) -> ExplanationConsistencyWitness:
    rows_by_grain = {row.grain_id: row for row in rows}
    active_names = tuple(item.feature_name for item in query.weights)
    active_indices = tuple(registry.index(name) for name in active_names)
    if query.mode is ResearchQueryMode.EXEMPLAR:
        source = rows_by_grain.get(cast(str, query.exemplar_grain_id))
        if source is None:
            raise ResearchEvaluationError("exemplar explanation source is absent")
        query_raw = tuple(_row_feature_values(source)[name] for name in active_names)
    else:
        query_raw = tuple(item.value for item in query.profile)
    query_scaled = tuple(
        (query_raw[index] - float(center[registry_index])) / float(scale[registry_index])
        for index, registry_index in enumerate(active_indices)
    )
    weights = tuple(item.weight for item in query.weights)
    zero_terms = 0
    terms_checked = 0
    ties_checked = 0
    previous: tuple[float, bytes, str] | None = None
    evidence: list[dict[str, object]] = []
    for candidate in result.candidates:
        row = rows_by_grain.get(candidate.grain_id)
        if row is None or row.player_id != candidate.player_id:
            raise ResearchEvaluationError("result candidate is outside the governed matrix")
        if candidate.missing_features:
            raise ResearchEvaluationError("scored result exposes missing active features")
        candidate_values = _row_feature_values(row)
        raw = tuple(candidate_values[name] for name in active_names)
        scaled = tuple(
            (raw[index] - float(center[registry_index])) / float(scale[registry_index])
            for index, registry_index in enumerate(active_indices)
        )
        if tuple(item.feature_name for item in candidate.contributions) != active_names:
            raise ResearchEvaluationError("candidate explanation feature order drifts")
        try:
            normalized_query, query_zero = stable_weighted_unit_components(
                query_scaled,
                weights,
            )
            normalized_candidate, candidate_zero = stable_weighted_unit_components(
                scaled,
                weights,
            )
        except StableNormalizationError as exc:
            raise ResearchEvaluationError("explanation normalization reproduction failed") from exc
        expected_contributions: list[float] = []
        for index, contribution in enumerate(candidate.contributions):
            contrast = scaled[index] - query_scaled[index]
            if not all(
                (
                    _same_float(contribution.query_value, query_raw[index]),
                    _same_float(contribution.candidate_value, raw[index]),
                    _same_float(contribution.scaled_query_value, query_scaled[index]),
                    _same_float(contribution.scaled_candidate_value, scaled[index]),
                    _same_float(contribution.scaled_contrast, contrast),
                    _same_float(contribution.weight, weights[index]),
                )
            ):
                raise ResearchEvaluationError("raw or scaled explanation operand is inconsistent")
            if query.method is ResearchMethod.WEIGHTED_EUCLIDEAN:
                expected = weights[index] * contrast * contrast
                if (
                    contribution.normalized_query_component is not None
                    or contribution.normalized_candidate_component is not None
                ):
                    raise ResearchEvaluationError("Euclidean explanation has cosine operands")
            else:
                zero_norm = query_zero or candidate_zero
                expected_query = 0.0 if zero_norm else normalized_query[index]
                expected_candidate = 0.0 if zero_norm else normalized_candidate[index]
                if (
                    contribution.normalized_query_component is None
                    or contribution.normalized_candidate_component is None
                    or not _same_float(
                        contribution.normalized_query_component,
                        expected_query,
                    )
                    or not _same_float(
                        contribution.normalized_candidate_component,
                        expected_candidate,
                    )
                ):
                    raise ResearchEvaluationError("cosine normalized operand is inconsistent")
                expected = -(expected_query * expected_candidate)
            if not _same_float(contribution.contribution, expected):
                raise ResearchEvaluationError("feature contribution does not reproduce")
            if weights[index] == 0.0:
                zero_terms += 1
                if contribution.contribution != 0.0:
                    raise ResearchEvaluationError("zero-weight feature contributes to score")
            expected_contributions.append(expected)
            terms_checked += 1
        try:
            contribution_sum = stable_finite_sum(tuple(expected_contributions))
        except StableNormalizationError as exc:
            raise ResearchEvaluationError("explanation contribution sum is invalid") from exc
        expected_score = (
            math.sqrt(contribution_sum)
            if query.method is ResearchMethod.WEIGHTED_EUCLIDEAN
            else 1.0 + contribution_sum
        )
        if not _same_float(candidate.score, expected_score):
            raise ResearchEvaluationError("candidate score does not reproduce from explanation")
        order_key = (candidate.score, candidate.player_id.bytes, candidate.grain_id)
        if previous is not None and previous[0] == order_key[0]:
            ties_checked += 1
            if previous > order_key:
                raise ResearchEvaluationError("deterministic tie order is inconsistent")
        previous = order_key
        evidence.append(
            {
                "candidate": candidate.grain_id,
                "score": candidate.score,
                "terms": [item.model_dump(mode="json") for item in candidate.contributions],
            }
        )
    digest = canonical_research_digest({"case_id": case.case_id, "evidence": evidence})
    return ExplanationConsistencyWitness(
        case_id=case.case_id,
        candidate_rows_checked=len(result.candidates),
        contribution_terms_checked=terms_checked,
        zero_weight_terms_checked=zero_terms,
        deterministic_tie_pairs_checked=ties_checked,
        missing_feature_count=0,
        scaler_semantics="median_iqr_linear_constant_unit_scale",
        explanation_digest=digest,
    )


def _population_reconciles(population: RetrievalPopulationCounts) -> bool:
    filter_exclusions = (
        population.position_exclusions
        + population.minimum_minutes_exclusions
        + population.explicit_player_exclusions
        + population.exemplar_self_exclusions
    )
    return (
        population.competition_rows == filter_exclusions + population.filter_admitted_rows
        and population.filter_admitted_rows
        == population.missing_feature_exclusions + population.scored_rows
    )


def _filter_witness(
    *,
    suite: FrozenResearchEvaluationSuite,
    case: FrozenQueryCase,
    kind: FilterWitnessKind,
    result: ResearchQueryResult,
) -> FilterBehaviourWitness:
    population = result.population
    passed = _population_reconciles(population)
    if kind is FilterWitnessKind.EXEMPLAR_SELF_EXCLUSION:
        passed = (
            passed
            and case.mode is ResearchQueryMode.EXEMPLAR
            and (population.exemplar_self_exclusions == 1)
        )
    elif kind is FilterWitnessKind.POSITION_FILTER:
        passed = passed and bool(case.filters.position_codes) and population.position_exclusions > 0
    elif kind is FilterWitnessKind.MINIMUM_MINUTES_POLICY_FLOOR:
        passed = passed and case.filters.minimum_minutes == suite.minimum_minutes_policy
    elif kind is FilterWitnessKind.MINIMUM_MINUTES_ABOVE_POLICY:
        passed = (
            passed
            and case.filters.minimum_minutes is not None
            and case.filters.minimum_minutes > suite.minimum_minutes_policy
            and population.minimum_minutes_exclusions > 0
        )
    elif kind is FilterWitnessKind.EXPLICIT_PLAYER_EXCLUSION:
        passed = (
            passed
            and bool(case.filters.excluded_player_ids)
            and population.explicit_player_exclusions > 0
        )
    elif kind is FilterWitnessKind.FULL_SCORE_BEFORE_LIMIT:
        passed = (
            passed
            and population.scored_rows > case.limit
            and population.returned_rows == case.limit
        )
    else:
        passed = passed and population.scored_rows == 0 and population.returned_rows == 0
    if not passed:
        raise ResearchEvaluationError(f"filter witness failed: {kind.value}")
    draft = FilterBehaviourWitness.model_construct(
        case_id=case.case_id,
        kind=kind,
        population=population,
        passed=True,
        witness_digest="0" * 64,
    )
    return FilterBehaviourWitness(
        case_id=case.case_id,
        kind=kind,
        population=population,
        passed=True,
        witness_digest=canonical_research_digest(draft.digest_projection()),
    )


def _query_witness(
    *,
    case: FrozenQueryCase,
    query: ResearchQueryRequest,
    first: ResearchQueryResult,
    second: ResearchQueryResult,
) -> QueryReproducibilityWitness:
    same_candidates = first.candidates == second.candidates
    same_population = first.population == second.population
    same_warnings = first.warnings == second.warnings
    if (
        first.result_id != second.result_id
        or first.result_digest != second.result_digest
        or not same_candidates
        or not same_population
        or not same_warnings
    ):
        raise ResearchEvaluationError("frozen query did not reproduce exact semantic results")
    order_digest = canonical_research_digest(
        {"order": [[item.rank, str(item.player_id), item.grain_id] for item in first.candidates]}
    )
    score_digest = canonical_research_digest(
        {"scores": [[item.grain_id, item.score] for item in first.candidates]}
    )
    explanation_digest = canonical_research_digest(
        {
            "explanations": [
                [
                    item.grain_id,
                    [term.model_dump(mode="json") for term in item.contributions],
                ]
                for item in first.candidates
            ]
        }
    )
    draft = QueryReproducibilityWitness.model_construct(
        case_id=case.case_id,
        query=query,
        first_result=first,
        second_generated_at=second.generated_at,
        second_result_id=second.result_id,
        second_result_digest=second.result_digest,
        candidate_order_digest=order_digest,
        score_digest=score_digest,
        explanation_digest=explanation_digest,
        population_reproduced=True,
        candidate_order_reproduced=True,
        scores_reproduced=True,
        explanations_reproduced=True,
        witness_digest="0" * 64,
    )
    return QueryReproducibilityWitness(
        **draft.model_dump(mode="python", exclude={"witness_digest"}),
        witness_digest=canonical_research_digest(draft.digest_projection()),
    )


def _stability_witness(
    perturbation: FrozenWeightPerturbation,
    cases: Mapping[str, FrozenQueryCase],
    results: Mapping[str, ResearchQueryResult],
) -> WeightStabilityWitness:
    baseline_case = cases[perturbation.baseline_case_id]
    perturbed_case = cases[perturbation.perturbed_case_id]
    baseline = results[baseline_case.case_id]
    changed = results[perturbed_case.case_id]
    deltas = tuple(
        abs(left.weight - right.weight)
        for left, right in zip(baseline_case.weights, perturbed_case.weights, strict=True)
    )
    observed_delta = max(deltas)
    k = perturbation.top_k
    base_top = tuple(item.grain_id for item in baseline.candidates[:k])
    changed_top = tuple(item.grain_id for item in changed.candidates[:k])
    overlap = set(base_top) & set(changed_top)
    missing_rank = k + 1
    base_ranks = {grain_id: rank for rank, grain_id in enumerate(base_top, start=1)}
    changed_ranks = {grain_id: rank for rank, grain_id in enumerate(changed_top, start=1)}
    union = tuple(sorted(set(base_top) | set(changed_top)))
    displacements = tuple(
        RankDisplacement(
            grain_id=grain_id,
            baseline_rank=base_ranks.get(grain_id, missing_rank),
            perturbed_rank=changed_ranks.get(grain_id, missing_rank),
            absolute_displacement=abs(
                base_ranks.get(grain_id, missing_rank) - changed_ranks.get(grain_id, missing_rank)
            ),
        )
        for grain_id in union
    )
    baseline_scores = {item.grain_id: item.score for item in baseline.candidates[:k]}
    changed_scores = {item.grain_id: item.score for item in changed.candidates[:k]}
    score_changes = tuple(
        ScoreChange(
            grain_id=grain_id,
            baseline_score=baseline_scores[grain_id],
            perturbed_score=changed_scores[grain_id],
            absolute_change=abs(baseline_scores[grain_id] - changed_scores[grain_id]),
        )
        for grain_id in sorted(overlap)
    )
    mean_displacement = (
        sum(item.absolute_displacement for item in displacements) / len(displacements)
        if displacements
        else 0.0
    )
    draft = WeightStabilityWitness.model_construct(
        perturbation_id=perturbation.perturbation_id,
        baseline_case_id=baseline_case.case_id,
        perturbed_case_id=perturbed_case.case_id,
        maximum_absolute_weight_delta=perturbation.maximum_absolute_weight_delta,
        observed_maximum_absolute_weight_delta=observed_delta,
        top_k=k,
        top_k_overlap_count=len(overlap),
        top_k_overlap_fraction=len(overlap) / k,
        rank_displacements=displacements,
        mean_absolute_rank_displacement=mean_displacement,
        score_changes=score_changes,
        sensitivity_only=True,
        validates_ranking_quality=False,
        witness_digest="0" * 64,
    )
    return WeightStabilityWitness(
        perturbation_id=perturbation.perturbation_id,
        baseline_case_id=baseline_case.case_id,
        perturbed_case_id=perturbed_case.case_id,
        maximum_absolute_weight_delta=perturbation.maximum_absolute_weight_delta,
        observed_maximum_absolute_weight_delta=observed_delta,
        top_k=k,
        top_k_overlap_count=len(overlap),
        top_k_overlap_fraction=len(overlap) / k,
        rank_displacements=displacements,
        mean_absolute_rank_displacement=mean_displacement,
        score_changes=score_changes,
        sensitivity_only=True,
        validates_ranking_quality=False,
        witness_digest=canonical_research_digest(draft.digest_projection()),
    )


def _coverage(
    suite: FrozenResearchEvaluationSuite,
    service: ResearchServingService,
    cases: Mapping[str, FrozenQueryCase],
    results: Mapping[str, ResearchQueryResult],
) -> EvaluationCoverage:
    rows = service.matrix_rows
    returned = {
        candidate.grain_id: candidate
        for result in results.values()
        for candidate in result.candidates
    }
    grouped: dict[UUID, list[FeatureMatrixRow]] = defaultdict(list)
    for row in rows:
        grouped[row.competition_id].append(row)
    competition_coverage = tuple(
        CompetitionCoverage(
            competition_id=competition_id,
            competition_name=competition_rows[0].competition_name,
            matrix_rows=len(competition_rows),
            queried_case_count=sum(
                1 for case in cases.values() if case.filters.competition_id == competition_id
            ),
            returned_unique_grain_count=sum(
                1 for candidate in returned.values() if candidate.competition_id == competition_id
            ),
        )
        for competition_id, competition_rows in sorted(
            grouped.items(), key=lambda item: item[0].bytes
        )
    )
    return EvaluationCoverage(
        matrix_row_count=suite.matrix_row_count,
        unique_matrix_player_count=suite.unique_matrix_player_count,
        source_player_count=suite.source_player_count,
        query_case_count=len(cases),
        source_grain_count=len({item.source_grain_id for item in cases.values()}),
        unique_returned_grain_count=len(returned),
        unique_returned_player_count=len({item.player_id for item in returned.values()}),
        returned_candidate_matrix_coverage=len(returned) / suite.matrix_row_count,
        total_scored_row_evaluations=sum(
            result.population.scored_rows for result in results.values()
        ),
        competition_coverage=competition_coverage,
    )


def run_research_evaluation(
    suite: FrozenResearchEvaluationSuite,
    *,
    service: ResearchServingService,
) -> ResearchRetrievalEvaluationResult:
    """Execute every frozen query twice and emit deterministic engineering evidence."""

    if type(service) is not ResearchServingService:
        raise TypeError("service must be an exact ResearchServingService")
    validated = _fresh(suite, FrozenResearchEvaluationSuite, label="evaluation suite")
    _validate_suite_authority(validated, service=service)
    rows = service.matrix_rows
    rows_by_grain = {row.grain_id: row for row in rows}
    registry = service.index_manifest.feature_names
    center, scale = _scaler(rows, registry)
    query_witnesses: list[QueryReproducibilityWitness] = []
    explanation_witnesses: list[ExplanationConsistencyWitness] = []
    filter_witnesses: list[FilterBehaviourWitness] = []
    results: dict[str, ResearchQueryResult] = {}
    cases = {item.case_id: item for item in validated.cases}
    for case in validated.cases:
        query = _case_query(validated, case, rows_by_grain)
        try:
            first = service.execute_query(query, generated_at=validated.first_generated_at)
            second = service.execute_query(query, generated_at=validated.second_generated_at)
        except ResearchServingError as exc:
            raise ResearchEvaluationError(f"frozen query failed: {case.case_id}") from exc
        query_witnesses.append(_query_witness(case=case, query=query, first=first, second=second))
        explanation_witnesses.append(
            _verify_explanations(
                case=case,
                query=query,
                result=first,
                rows=rows,
                registry=registry,
                center=center,
                scale=scale,
            )
        )
        filter_witnesses.extend(
            _filter_witness(
                suite=validated,
                case=case,
                kind=kind,
                result=first,
            )
            for kind in case.witnesses
        )
        results[case.case_id] = first
    stability = tuple(
        _stability_witness(perturbation, cases, results) for perturbation in validated.perturbations
    )
    coverage = _coverage(validated, service, cases, results)
    query_witness_tuple = tuple(query_witnesses)
    explanation_witness_tuple = tuple(explanation_witnesses)
    filter_witness_tuple = tuple(filter_witnesses)
    draft = ResearchRetrievalEvaluationResult.model_construct(
        suite_id=validated.suite_id,
        suite_version=validated.suite_version,
        suite_digest=validated.suite_digest,
        evaluated_at=validated.evaluated_at,
        pins=validated.pins,
        query_witnesses=query_witness_tuple,
        explanation_witnesses=explanation_witness_tuple,
        filter_witnesses=filter_witness_tuple,
        stability_witnesses=stability,
        coverage=coverage,
        limitations=validated.limitations,
        weaknesses=validated.weaknesses,
        result_digest="0" * 64,
    )
    try:
        return ResearchRetrievalEvaluationResult(
            suite_id=validated.suite_id,
            suite_version=validated.suite_version,
            suite_digest=validated.suite_digest,
            evaluated_at=validated.evaluated_at,
            pins=validated.pins,
            query_witnesses=query_witness_tuple,
            explanation_witnesses=explanation_witness_tuple,
            filter_witnesses=filter_witness_tuple,
            stability_witnesses=stability,
            coverage=coverage,
            limitations=validated.limitations,
            weaknesses=validated.weaknesses,
            result_digest=canonical_research_digest(draft.digest_projection()),
        )
    except ValidationError as exc:
        raise ResearchEvaluationError("constructed evaluation result contract rejected") from exc


def render_evaluation_payload(result: ResearchRetrievalEvaluationResult) -> bytes:
    """Return canonical JSON bytes suitable for master-owned local publication."""

    validated = _fresh(
        result,
        ResearchRetrievalEvaluationResult,
        label="evaluation result",
    )
    try:
        return canonical_json_bytes(validated.model_dump(mode="json"))
    except FormatError as exc:
        raise ResearchEvaluationError("evaluation result is not canonical JSON") from exc


__all__ = [
    "DEFAULT_EVALUATION_CONFIG_PATH",
    "CompetitionCoverage",
    "EvaluationCoverage",
    "ExplanationConsistencyWitness",
    "FilterBehaviourWitness",
    "FilterWitnessKind",
    "FrozenQueryCase",
    "FrozenResearchEvaluationSuite",
    "FrozenWeightPerturbation",
    "QueryReproducibilityWitness",
    "RankDisplacement",
    "ResearchEvaluationError",
    "ResearchRetrievalEvaluationResult",
    "ScoreChange",
    "WeightStabilityWitness",
    "load_frozen_evaluation_suite",
    "render_evaluation_payload",
    "research_version_pins",
    "run_research_evaluation",
]

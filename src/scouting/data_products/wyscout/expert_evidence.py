"""Deterministic participant-safe W10 v2 evidence derivation from accepted W09 rows."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pyarrow.parquet as pq  # type: ignore[import-untyped]
from pydantic import ValidationError

from scouting.contracts.expert_relevance import (
    EvidenceAvailabilityV2,
    EvidenceCoverageV2,
    EvidenceFamilyV2,
    EvidenceGlossaryEntryV2,
    EvidenceMetricUnitV2,
    EvidenceMetricV2,
    EvidenceOpportunityComponentV2,
    EvidencePlayerContextV2,
    EvidencePurposeV2,
    EvidenceQuantityV2,
    ExpertEvidencePolicyV2,
    MdEvidenceSubrubricV2,
    ParticipantEvidenceComparisonV2,
    ParticipantExpertEvidenceBundleV2,
    UnsupportedInferenceV2,
)
from scouting.contracts.research import (
    FeatureMatrixRow,
    FeatureValueState,
    canonical_research_digest,
)
from scouting.modeling.research import (
    DEFAULT_MATRIX_ARTIFACT_ROOT,
    LoadedFeatureMatrix,
    load_feature_matrix,
)
from scouting.storage.formats import canonical_json_bytes

PROJECT_ROOT = Path(__file__).resolve().parents[4]
POLICY_PATH = PROJECT_ROOT / "configs/evaluation/w10-expert-evidence-presentation-v2.json"
CANONICAL_MANIFEST_PATH = PROJECT_ROOT / (
    "data/manifests/wyscout/v5/research/"
    "2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e"
    ".canonical-manifest.json"
)
MATRIX_MANIFEST_PATH = PROJECT_ROOT / (
    "data/manifests/wyscout/v5/research_features/"
    "w09-historical-player-window-v1-a9f7cc2d5fc12ea0.feature-matrix.manifest.json"
)
_ACCEPTED_CANONICAL_MANIFEST_DIGEST_V2 = (
    "0105267ae0f107a63fad33b24adecdb3c4bb2e900bdf79a505e9ad4af6264b43"
)
_ACCEPTED_CANONICAL_BUILD_ID_V2 = "2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e"

_SEASON_LABEL = "Retained 2017/18 historical competition season"
_THRESHOLD_RATIONALE = (
    "Pre-pilot opportunity floor frozen before participant exposure; it suppresses sparse "
    "estimates but is not a scientifically validated reliability cutoff."
)
_MINUTE_LIMITATION = (
    "Governed minutes are a conservative lower bound, so per-90 rates may exceed rates based "
    "on unknown true minutes."
)
_NEUTRAL_DIRECTION_NOTICE = (
    "Descriptive only; no better/worse, attacking-direction or pitch-side meaning."
)
_FORBIDDEN_PARTICIPANT_KEYS = frozenset(
    {
        "origin",
        "retrieval_rank",
        "retrieval_score",
        "similarity",
        "distance",
        "score",
        "control_rank",
        "control_match_rule",
        "control_selection_rule",
        "evidence_band",
        "difficulty",
        "repeat_anchor_candidate_ids",
        "repeat_of_presentation_id",
        "presentation_kind",
        "expected_outcome",
        "expected_result",
        "previous_response",
        "aggregate_response",
        "grain_id",
        "player_id",
        "candidate_id",
        "query_id",
    }
)
_FORBIDDEN_PARTICIPANT_VALUES = frozenset(
    {"retrieved", "control", "straightforward", "difficult", "lower", "higher"}
)

_FEATURE_DETAILS: Mapping[str, tuple[str, str, str]] = {
    "passes_per90": (
        "Passes per 90",
        "Recorded event-8 passes per 90 governed minutes.",
        "event_id == 8",
    ),
    "accurate_passes_per90": (
        "Accurate passes per 90",
        "Recorded event-8 passes carrying tag 1801 per 90 governed minutes.",
        "event_id == 8 and tag_ids contains 1801",
    ),
    "crosses_per90": (
        "Crosses per 90",
        "Recorded event-8/sub-event-80 crosses per 90 governed minutes.",
        "event_id == 8 and sub_event_id == 80",
    ),
    "smart_passes_per90": (
        "Smart passes per 90",
        "Recorded event-8/sub-event-86 smart passes per 90 governed minutes.",
        "event_id == 8 and sub_event_id == 86",
    ),
    "shots_per90": (
        "Shots per 90",
        "Recorded event-10 shots per 90 governed minutes.",
        "event_id == 10",
    ),
    "shots_on_target_per90": (
        "Shots on target per 90",
        "Recorded event-10 actions carrying tag 1801 per 90 governed minutes.",
        "event_id == 10 and tag_ids contains 1801",
    ),
    "goals_per90": (
        "Goals per 90",
        "Recorded non-event-9 actions carrying tag 101 and not tag 102 per 90 governed minutes.",
        "event_id != 9 and tag_ids contains 101 and does not contain 102",
    ),
    "key_passes_per90": (
        "Key passes per 90",
        "Recorded actions carrying tag 302 per 90 governed minutes.",
        "tag_ids contains 302",
    ),
    "assists_per90": (
        "Assists per 90",
        "Recorded actions carrying tag 301 per 90 governed minutes.",
        "tag_ids contains 301",
    ),
    "duels_per90": (
        "Duels per 90",
        "Recorded event-1 duels per 90 governed minutes.",
        "event_id == 1",
    ),
    "duels_won_per90": (
        "Duels won per 90",
        "Recorded event-1 actions carrying tag 703 per 90 governed minutes.",
        "event_id == 1 and tag_ids contains 703",
    ),
    "interceptions_per90": (
        "Interceptions per 90",
        "Recorded actions carrying tag 1401 per 90 governed minutes.",
        "tag_ids contains 1401",
    ),
    "clearances_per90": (
        "Clearances per 90",
        "Recorded sub-event-71 actions per 90 governed minutes.",
        "sub_event_id == 71",
    ),
    "accelerations_per90": (
        "Accelerations per 90",
        "Recorded sub-event-70 actions per 90 governed minutes.",
        "sub_event_id == 70",
    ),
    "fouls_per90": (
        "Fouls per 90",
        "Recorded event-2 fouls per 90 governed minutes.",
        "event_id == 2",
    ),
    "touches_per90": (
        "Touches per 90",
        "Recorded sub-event-72 actions per 90 governed minutes.",
        "sub_event_id == 72",
    ),
}


class ExpertEvidenceBuildError(ValueError):
    """Raised before incomplete, stale or protected evidence can reach participant bytes."""


@dataclass(slots=True)
class _SpatialComponent:
    total: int = 0
    valid: int = 0
    bins: list[int] = field(default_factory=lambda: [0] * 9)


@dataclass(slots=True)
class _Aggregate:
    total_actions: int = 0
    starts: _SpatialComponent = field(default_factory=_SpatialComponent)
    passes: int = 0
    pass_subtypes: dict[int, int] = field(default_factory=dict)
    duels: int = 0
    duel_subtypes: dict[int, int] = field(default_factory=dict)
    defending_duels: _SpatialComponent = field(default_factory=_SpatialComponent)
    interceptions: _SpatialComponent = field(default_factory=_SpatialComponent)
    clearances: _SpatialComponent = field(default_factory=_SpatialComponent)
    shots: _SpatialComponent = field(default_factory=_SpatialComponent)
    gk_goal_kicks: int = 0
    gk_leaving_line: int = 0
    gk_save_attempts: int = 0
    gk_reflexes: int = 0
    gk_generic_saves: int = 0


@dataclass(frozen=True, slots=True)
class _RawMetric:
    metric_id: str
    label: str
    definition: str
    unit: EvidenceMetricUnitV2
    predicate: str
    numerator: int | None
    denominator: float | int | None
    value: float | None
    coverage: EvidenceCoverageV2


@dataclass(frozen=True, slots=True)
class _RawFamily:
    family_id: str
    label: str
    definition: str
    predicate: str
    availability: EvidenceAvailabilityV2
    denominator: int | None
    floor: int | None
    coverage: EvidenceCoverageV2
    opportunity_components: tuple[_RawOpportunity, ...]
    metrics: tuple[_RawMetric, ...]


@dataclass(frozen=True, slots=True)
class _RawOpportunity:
    component_id: str
    predicate: str
    denominator: int
    floor: int
    coverage: EvidenceCoverageV2


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_expert_evidence_policy_v2(path: Path = POLICY_PATH) -> ExpertEvidencePolicyV2:
    """Load the exact self-digested pre-pilot measurement policy."""

    try:
        policy = ExpertEvidencePolicyV2.model_validate_json(path.read_bytes())
    except (OSError, ValidationError) as exc:
        raise ExpertEvidenceBuildError("v2 evidence policy is absent or incompatible") from exc
    return policy


def _bin_index(x: int, y: int) -> int:
    def band(value: int) -> int:
        if not 0 <= value <= 100:
            raise ExpertEvidenceBuildError("valid canonical coordinate is outside 0..100")
        return 0 if value <= 33 else (1 if value <= 66 else 2)

    return band(x) * 3 + band(y)


def _add_spatial(component: _SpatialComponent, row: Mapping[str, object]) -> None:
    component.total += 1
    if row.get("coordinate_evidence_state") != "valid":
        return
    x, y = row.get("start_x"), row.get("start_y")
    if type(x) is not int or type(y) is not int:
        raise ExpertEvidenceBuildError("valid coordinate evidence lacks a strict start point")
    component.valid += 1
    component.bins[_bin_index(x, y)] += 1


def aggregate_actions_v2(
    rows: Sequence[FeatureMatrixRow], action_paths: Sequence[Path]
) -> dict[str, _Aggregate]:
    """Aggregate only accepted independent predicates, never W09 vectors or scorer inputs."""

    grains = {
        (str(row.player_id), str(row.competition_id), row.season_id): row.grain_id for row in rows
    }
    aggregates = {row.grain_id: _Aggregate() for row in rows}
    columns = (
        "canonical_build_id",
        "player_id",
        "competition_id",
        "season_id",
        "event_id",
        "sub_event_id",
        "tag_ids",
        "start_x",
        "start_y",
        "coordinate_evidence_state",
        "source_available_at",
        "identity_available_at",
        "feature_cutoff_ts",
    )
    for path in action_paths:
        for batch in pq.ParquetFile(path).iter_batches(batch_size=65_536, columns=columns):
            for action in cast(list[dict[str, object]], batch.to_pylist()):
                if action.get("canonical_build_id") != _ACCEPTED_CANONICAL_BUILD_ID_V2:
                    raise ExpertEvidenceBuildError("canonical action build identity drifted")
                if any(
                    action.get(name) is None
                    for name in (
                        "source_available_at",
                        "identity_available_at",
                        "feature_cutoff_ts",
                    )
                ) or max(
                    cast(datetime, action["source_available_at"]),
                    cast(datetime, action["identity_available_at"]),
                ) >= cast(datetime, action["feature_cutoff_ts"]):
                    raise ExpertEvidenceBuildError("canonical action temporal authority drifted")
                grain_id = grains.get(
                    (
                        cast(str, action.get("player_id")),
                        cast(str, action.get("competition_id")),
                        cast(str, action.get("season_id")),
                    )
                )
                if grain_id is None:
                    continue
                aggregate = aggregates[grain_id]
                aggregate.total_actions += 1
                _add_spatial(aggregate.starts, action)
                event_id = action.get("event_id")
                sub_event_id = action.get("sub_event_id")
                tags = action.get("tag_ids")
                if not isinstance(tags, list) or any(type(tag) is not int for tag in tags):
                    raise ExpertEvidenceBuildError("canonical action tags are incompatible")
                if event_id == 8:
                    aggregate.passes += 1
                    if sub_event_id in {81, 83, 84, 85}:
                        aggregate.pass_subtypes[sub_event_id] = (
                            aggregate.pass_subtypes.get(sub_event_id, 0) + 1
                        )
                if event_id == 1:
                    aggregate.duels += 1
                    if sub_event_id in {10, 11, 12, 13}:
                        aggregate.duel_subtypes[sub_event_id] = (
                            aggregate.duel_subtypes.get(sub_event_id, 0) + 1
                        )
                if event_id == 1 and sub_event_id == 12:
                    _add_spatial(aggregate.defending_duels, action)
                if 1401 in tags:
                    _add_spatial(aggregate.interceptions, action)
                if sub_event_id == 71:
                    _add_spatial(aggregate.clearances, action)
                if event_id == 10:
                    _add_spatial(aggregate.shots, action)
                if event_id == 3 and sub_event_id == 34:
                    aggregate.gk_goal_kicks += 1
                if event_id == 4 and sub_event_id == 40:
                    aggregate.gk_leaving_line += 1
                if event_id == 9 and sub_event_id in {90, 91}:
                    aggregate.gk_save_attempts += 1
                    aggregate.gk_reflexes += int(sub_event_id == 90)
                    aggregate.gk_generic_saves += int(sub_event_id == 91)
    return aggregates


def _coverage(observed: int, expected: int, definition: str) -> EvidenceCoverageV2:
    return EvidenceCoverageV2(
        observed=observed,
        expected=expected,
        proportion=None if expected == 0 else observed / expected,
        definition=definition,
    )


def _family_state(
    *, sufficient: bool, invalid: bool, numerators: Sequence[int]
) -> EvidenceAvailabilityV2:
    if invalid:
        return EvidenceAvailabilityV2.INVALID_MISSING
    if not sufficient:
        return EvidenceAvailabilityV2.INSUFFICIENT_OPPORTUNITIES
    return (
        EvidenceAvailabilityV2.OBSERVED_VALUE
        if any(numerators)
        else EvidenceAvailabilityV2.OBSERVED_ZERO
    )


def _spatial_metrics(
    *, prefix: str, label: str, predicate: str, component: _SpatialComponent, bins: Sequence[str]
) -> tuple[_RawMetric, ...]:
    component_coverage = _coverage(
        component.valid,
        component.total,
        f"valid starts for {predicate} / all retained actions for that exact predicate",
    )
    return tuple(
        _RawMetric(
            metric_id=f"{prefix}.{bin_name}",
            label=f"{label}: {bin_name}",
            definition=f"Share of qualifying valid recorded starts in neutral bin {bin_name}.",
            unit=EvidenceMetricUnitV2.SHARE,
            predicate=f"{predicate} and valid start in {bin_name}",
            numerator=count,
            denominator=component.valid,
            value=None if component.valid == 0 else count / component.valid,
            coverage=component_coverage,
        )
        for bin_name, count in zip(bins, component.bins, strict=True)
    )


def _raw_families(
    row: FeatureMatrixRow, aggregate: _Aggregate, policy: ExpertEvidencePolicyV2
) -> dict[str, _RawFamily]:
    thresholds = policy.thresholds
    coverage_floor = thresholds.minimum_coordinate_coverage
    starts_coverage = _coverage(
        aggregate.starts.valid,
        aggregate.starts.total,
        "valid recorded starts / retained player actions",
    )
    loc_invalid = (
        starts_coverage.proportion is not None and starts_coverage.proportion < coverage_floor
    )
    loc_state = _family_state(
        sufficient=aggregate.starts.valid >= thresholds.valid_starts,
        invalid=loc_invalid,
        numerators=aggregate.starts.bins,
    )
    loc = _RawFamily(
        "ID-LOC-01",
        "Neutral recorded start locations",
        "Neutral fixed-bin distribution of valid recorded starts.",
        "any retained player action with coordinate_evidence_state == valid",
        loc_state,
        aggregate.starts.valid,
        thresholds.valid_starts,
        starts_coverage,
        (
            _RawOpportunity(
                "valid_starts",
                "any retained player action with coordinate_evidence_state == valid",
                aggregate.starts.valid,
                thresholds.valid_starts,
                starts_coverage,
            ),
        ),
        _spatial_metrics(
            prefix="loc",
            label="Recorded start",
            predicate="coordinate_evidence_state == valid",
            component=aggregate.starts,
            bins=policy.location_bins,
        ),
    )
    pass_labels = {81: "Hand pass", 83: "High pass", 84: "Launch", 85: "Simple pass"}
    pass_coverage = _coverage(
        aggregate.passes,
        aggregate.passes,
        "retained event-8 passes / retained event-8 passes",
    )
    pass_metrics = tuple(
        _RawMetric(
            f"pass.sub_event_{sub_event_id}_share",
            f"{label} share",
            f"Recorded sub-event-{sub_event_id} share of every event-8 pass; other pass "
            "subtypes remain in the denominator.",
            EvidenceMetricUnitV2.SHARE,
            f"event_id == 8 and sub_event_id == {sub_event_id}",
            aggregate.pass_subtypes.get(sub_event_id, 0),
            aggregate.passes,
            None
            if aggregate.passes == 0
            else aggregate.pass_subtypes.get(sub_event_id, 0) / aggregate.passes,
            pass_coverage,
        )
        for sub_event_id, label in pass_labels.items()
    )
    pass_state = _family_state(
        sufficient=aggregate.passes >= thresholds.passes,
        invalid=False,
        numerators=tuple(metric.numerator or 0 for metric in pass_metrics),
    )
    passing = _RawFamily(
        "ID-PASS-01",
        "Passing subtype distribution",
        "Four non-W09 pass subtype shares among all event-8 passes.",
        "event_id == 8; displayed subtypes 81,83,84,85; denominator retains every event-8 pass",
        pass_state,
        aggregate.passes,
        thresholds.passes,
        pass_coverage,
        (
            _RawOpportunity(
                "all_passes",
                "event_id == 8",
                aggregate.passes,
                thresholds.passes,
                pass_coverage,
            ),
        ),
        pass_metrics,
    )
    duel_labels = {
        10: "Air duel",
        11: "Ground attacking duel",
        12: "Ground defending duel",
        13: "Ground loose-ball duel",
    }
    duel_coverage = _coverage(
        aggregate.duels,
        aggregate.duels,
        "retained event-1 duels / retained event-1 duels",
    )
    duel_metrics = tuple(
        _RawMetric(
            f"duel.sub_event_{sub_event_id}_share",
            f"{label} share",
            f"Recorded sub-event-{sub_event_id} share of every event-1 duel.",
            EvidenceMetricUnitV2.SHARE,
            f"event_id == 1 and sub_event_id == {sub_event_id}",
            aggregate.duel_subtypes.get(sub_event_id, 0),
            aggregate.duels,
            None
            if aggregate.duels == 0
            else aggregate.duel_subtypes.get(sub_event_id, 0) / aggregate.duels,
            duel_coverage,
        )
        for sub_event_id, label in duel_labels.items()
    )
    duel_state = _family_state(
        sufficient=aggregate.duels >= thresholds.duels,
        invalid=False,
        numerators=tuple(metric.numerator or 0 for metric in duel_metrics),
    )
    duels = _RawFamily(
        "ID-DUEL-01",
        "Duel subtype distribution",
        "Four recorded duel subtype shares among all event-1 duels; no win or quality inference.",
        "event_id == 1; sub_event_id in 10,11,12,13",
        duel_state,
        aggregate.duels,
        thresholds.duels,
        duel_coverage,
        (
            _RawOpportunity(
                "all_duels",
                "event_id == 1",
                aggregate.duels,
                thresholds.duels,
                duel_coverage,
            ),
        ),
        duel_metrics,
    )
    defensive_components = (
        (
            "defending_duel",
            "Defending duel",
            "event_id == 1 and sub_event_id == 12",
            aggregate.defending_duels,
            thresholds.defending_duels_valid_starts,
        ),
        (
            "interception",
            "Interception",
            "tag_ids contains 1401",
            aggregate.interceptions,
            thresholds.interceptions_valid_starts,
        ),
        (
            "clearance",
            "Clearance",
            "sub_event_id == 71",
            aggregate.clearances,
            thresholds.clearances_valid_starts,
        ),
    )
    defensive_metrics = tuple(
        metric
        for prefix, label, predicate, component, _floor in defensive_components
        for metric in _spatial_metrics(
            prefix=f"defloc.{prefix}",
            label=label,
            predicate=predicate,
            component=component,
            bins=policy.location_bins,
        )
    )
    defensive_sufficient = all(
        component.valid >= floor for *_, component, floor in defensive_components
    )
    defensive_invalid = any(
        component.total > 0 and component.valid / component.total < coverage_floor
        for *_, component, _floor in defensive_components
    )
    defensive_state = _family_state(
        sufficient=defensive_sufficient,
        invalid=defensive_invalid,
        numerators=tuple(metric.numerator or 0 for metric in defensive_metrics),
    )
    defensive = _RawFamily(
        "ID-DEFLOC-01",
        "Neutral defensive-action locations",
        "Separate neutral distributions for defending duels, interceptions and clearances.",
        "separate components: event 1/sub-event 12; tag 1401; sub-event 71; valid starts only",
        defensive_state,
        None,
        None,
        _coverage(
            sum(component.valid for *_, component, _floor in defensive_components),
            sum(component.total for *_, component, _floor in defensive_components),
            "valid component starts / all separately retained defensive components",
        ),
        tuple(
            _RawOpportunity(
                f"{prefix}_valid_starts",
                predicate,
                component.valid,
                floor,
                _coverage(
                    component.valid,
                    component.total,
                    f"valid {label.casefold()} starts / all retained component actions",
                ),
            )
            for prefix, label, predicate, component, floor in defensive_components
        ),
        defensive_metrics,
    )
    shot_coverage = _coverage(
        aggregate.shots.valid, aggregate.shots.total, "valid shot starts / all event-10 shots"
    )
    shot_invalid = (
        shot_coverage.proportion is not None and shot_coverage.proportion < coverage_floor
    )
    shot_state = _family_state(
        sufficient=aggregate.shots.valid >= thresholds.shots_valid_starts,
        invalid=shot_invalid,
        numerators=aggregate.shots.bins,
    )
    shooting = _RawFamily(
        "ID-SHOTLOC-01",
        "Neutral shot start locations",
        "Neutral valid-start distribution for recorded event-10 shots; no chance-quality "
        "inference.",
        "event_id == 10 and coordinate_evidence_state == valid",
        shot_state,
        aggregate.shots.valid,
        thresholds.shots_valid_starts,
        shot_coverage,
        (
            _RawOpportunity(
                "valid_shot_starts",
                "event_id == 10 and coordinate_evidence_state == valid",
                aggregate.shots.valid,
                thresholds.shots_valid_starts,
                shot_coverage,
            ),
        ),
        _spatial_metrics(
            prefix="shotloc",
            label="Recorded shot start",
            predicate="event_id == 10 and coordinate_evidence_state == valid",
            component=aggregate.shots,
            bins=policy.location_bins,
        ),
    )
    gk_sufficient = (
        aggregate.gk_save_attempts >= thresholds.goalkeeper_save_attempts
        and aggregate.gk_leaving_line >= thresholds.goalkeeper_leaving_line_actions
        and aggregate.gk_goal_kicks >= thresholds.goalkeeper_goal_kicks
    )
    gk_goal_coverage = _coverage(
        aggregate.gk_goal_kicks,
        aggregate.gk_goal_kicks,
        "retained goal kicks / same retained opportunity set",
    )
    gk_leaving_coverage = _coverage(
        aggregate.gk_leaving_line,
        aggregate.gk_leaving_line,
        "retained leaving-line actions / same retained opportunity set",
    )
    gk_save_coverage = _coverage(
        aggregate.gk_save_attempts,
        aggregate.gk_save_attempts,
        "retained event-9 sub-events 90/91 / same retained opportunity set",
    )
    gk_metrics = (
        _RawMetric(
            "gk.goal_kicks_per90",
            "Goal kicks per 90",
            "Recorded event-3/sub-event-34 involvement per 90 governed minutes.",
            EvidenceMetricUnitV2.COUNT_PER_90_GOVERNED_MINUTES,
            "event_id == 3 and sub_event_id == 34",
            aggregate.gk_goal_kicks,
            row.minutes,
            aggregate.gk_goal_kicks * 90.0 / row.minutes,
            gk_goal_coverage,
        ),
        _RawMetric(
            "gk.leaving_line_per90",
            "Leaving-line actions per 90",
            "Recorded event-4/sub-event-40 involvement per 90 governed minutes; not success "
            "or effectiveness.",
            EvidenceMetricUnitV2.COUNT_PER_90_GOVERNED_MINUTES,
            "event_id == 4 and sub_event_id == 40",
            aggregate.gk_leaving_line,
            row.minutes,
            aggregate.gk_leaving_line * 90.0 / row.minutes,
            gk_leaving_coverage,
        ),
        _RawMetric(
            "gk.reflex_share",
            "Reflex save-attempt share",
            "Recorded sub-event-90 share of event-9 save-attempt rows; not shots faced or "
            "save percentage.",
            EvidenceMetricUnitV2.SHARE,
            "event_id == 9 and sub_event_id == 90",
            aggregate.gk_reflexes,
            aggregate.gk_save_attempts,
            aggregate.gk_reflexes / aggregate.gk_save_attempts
            if aggregate.gk_save_attempts
            else None,
            gk_save_coverage,
        ),
        _RawMetric(
            "gk.generic_save_share",
            "Generic save-attempt share",
            "Recorded sub-event-91 share of event-9 save-attempt rows; not shots faced or "
            "save percentage.",
            EvidenceMetricUnitV2.SHARE,
            "event_id == 9 and sub_event_id == 91",
            aggregate.gk_generic_saves,
            aggregate.gk_save_attempts,
            aggregate.gk_generic_saves / aggregate.gk_save_attempts
            if aggregate.gk_save_attempts
            else None,
            gk_save_coverage,
        ),
    )
    gk_state = _family_state(
        sufficient=gk_sufficient,
        invalid=False,
        numerators=(aggregate.gk_goal_kicks, aggregate.gk_leaving_line, aggregate.gk_save_attempts),
    )
    goalkeeper = _RawFamily(
        "ID-GK-01",
        "Narrow goalkeeper involvement mix",
        "Goal-kick and leaving-line involvement plus save-attempt/reflex mix; never effectiveness.",
        "event 3/sub-event 34; event 4/sub-event 40; event 9/sub-events 90,91",
        gk_state,
        None,
        None,
        gk_save_coverage,
        (
            _RawOpportunity(
                "save_attempts",
                "event_id == 9 and sub_event_id in 90,91",
                aggregate.gk_save_attempts,
                thresholds.goalkeeper_save_attempts,
                gk_save_coverage,
            ),
            _RawOpportunity(
                "leaving_line_actions",
                "event_id == 4 and sub_event_id == 40",
                aggregate.gk_leaving_line,
                thresholds.goalkeeper_leaving_line_actions,
                gk_leaving_coverage,
            ),
            _RawOpportunity(
                "goal_kicks",
                "event_id == 3 and sub_event_id == 34",
                aggregate.gk_goal_kicks,
                thresholds.goalkeeper_goal_kicks,
                gk_goal_coverage,
            ),
        ),
        gk_metrics,
    )
    return {
        family.family_id: family
        for family in (loc, passing, duels, defensive, shooting, goalkeeper)
    }


def _midrank_percentile(value: float, population: Sequence[float]) -> float:
    if not population:
        raise ExpertEvidenceBuildError("percentile reference population is empty")
    less = sum(item < value for item in population)
    equal = sum(item == value for item in population)
    return 100.0 * (less + 0.5 * equal) / len(population)


def _not_applicable(raw: _RawFamily) -> _RawFamily:
    return _RawFamily(
        raw.family_id,
        raw.label,
        raw.definition,
        raw.predicate,
        EvidenceAvailabilityV2.NOT_APPLICABLE,
        None,
        None,
        _coverage(0, 0, "family excluded by the frozen position rubric"),
        tuple(
            _RawOpportunity(
                item.component_id,
                item.predicate,
                0,
                item.floor,
                _coverage(0, 0, "component excluded by the frozen position rubric"),
            )
            for item in raw.opportunity_components
        ),
        tuple(
            _RawMetric(
                metric.metric_id,
                metric.label,
                metric.definition,
                metric.unit,
                metric.predicate,
                None,
                None,
                None,
                _coverage(0, 0, "metric excluded by the frozen position rubric"),
            )
            for metric in raw.metrics
        ),
    )


def _position_family(position: str, family_id: str, raw: _RawFamily) -> _RawFamily:
    applicable: Mapping[str, frozenset[str]] = {
        "GK": frozenset({"ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-GK-01"}),
        "DF": frozenset({"ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-DEFLOC-01", "ID-SHOTLOC-01"}),
        "MD": frozenset({"ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-DEFLOC-01", "ID-SHOTLOC-01"}),
        "FW": frozenset({"ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-DEFLOC-01", "ID-SHOTLOC-01"}),
    }
    return raw if family_id in applicable[position] else _not_applicable(raw)


def _availability_for_metric(raw: _RawFamily, metric: _RawMetric) -> EvidenceAvailabilityV2:
    if raw.availability in {
        EvidenceAvailabilityV2.NOT_APPLICABLE,
        EvidenceAvailabilityV2.NOT_CAPTURED,
        EvidenceAvailabilityV2.INVALID_MISSING,
    }:
        return raw.availability
    if raw.availability is EvidenceAvailabilityV2.INSUFFICIENT_OPPORTUNITIES:
        return raw.availability
    return (
        EvidenceAvailabilityV2.OBSERVED_ZERO
        if metric.numerator == 0
        else EvidenceAvailabilityV2.OBSERVED_VALUE
    )


def _metric_contract(
    *,
    raw_family: _RawFamily,
    metric: _RawMetric,
    row: FeatureMatrixRow,
    percentile: float | None,
    position_reference_count: int,
) -> EvidenceMetricV2:
    availability = _availability_for_metric(raw_family, metric)
    observed = availability in {
        EvidenceAvailabilityV2.OBSERVED_VALUE,
        EvidenceAvailabilityV2.OBSERVED_ZERO,
    }
    counts_visible = observed or availability is EvidenceAvailabilityV2.INSUFFICIENT_OPPORTUNITIES
    return EvidenceMetricV2(
        metric_id=metric.metric_id,
        label=metric.label,
        definition=metric.definition,
        purpose=EvidencePurposeV2.INDEPENDENT_DESCRIPTOR,
        used_by_w09_ranking=False,
        availability=availability,
        unit=metric.unit,
        exact_predicate=metric.predicate,
        raw_numerator=metric.numerator if counts_visible else None,
        raw_opportunity_denominator=metric.denominator if counts_visible else None,
        raw_value=metric.value if observed else None,
        within_position_percentile=percentile if observed else None,
        governed_minutes_denominator=row.minutes,
        minute_state=cast(Any, row.minute_state),
        coverage=metric.coverage,
        position_reference=f"all comparable observed {row.position_code} matrix rows",
        position_reference_count=position_reference_count,
        derivation_version="w10-expert-evidence-derivation-v2",
        source_lineage_digest=row.source_lineage_digest,
        limitation=(
            _MINUTE_LIMITATION
            + " Recorded coordinates are neutral bins without direction, pitch-side or "
            "quality meaning."
        ),
    )


def _w09_family(
    row: FeatureMatrixRow,
    *,
    rows_by_position: Sequence[FeatureMatrixRow],
    policy: ExpertEvidencePolicyV2,
) -> EvidenceFamilyV2:
    references = {
        name: [
            cast(
                float,
                next(
                    feature.value for feature in reference.features if feature.feature_name == name
                ),
            )
            for reference in rows_by_position
        ]
        for name in policy.feature_names
    }
    metrics: list[EvidenceMetricV2] = []
    for name, feature in zip(policy.feature_names, row.features, strict=True):
        if (
            feature.feature_name != name
            or feature.state
            not in {
                FeatureValueState.VALUE,
                FeatureValueState.ZERO,
            }
            or feature.value is None
            or feature.numerator is None
            or feature.denominator is None
        ):
            raise ExpertEvidenceBuildError("eligible W09 feature evidence is missing or reordered")
        if (
            feature.denominator != row.minutes
            or feature.value != feature.numerator * 90.0 / row.minutes
        ):
            raise ExpertEvidenceBuildError("W09 per-90 value does not reconstruct exactly")
        if not float(feature.numerator).is_integer():
            raise ExpertEvidenceBuildError("W09 event numerator is not an exact count")
        label, definition, predicate = _FEATURE_DETAILS[name]
        numerator = int(feature.numerator)
        metrics.append(
            EvidenceMetricV2(
                metric_id=f"w09.{name}",
                label=label,
                definition=definition,
                purpose=EvidencePurposeV2.W09_INPUT,
                used_by_w09_ranking=True,
                availability=(
                    EvidenceAvailabilityV2.OBSERVED_ZERO
                    if numerator == 0
                    else EvidenceAvailabilityV2.OBSERVED_VALUE
                ),
                unit=EvidenceMetricUnitV2.COUNT_PER_90_GOVERNED_MINUTES,
                exact_predicate=predicate,
                raw_numerator=numerator,
                raw_opportunity_denominator=row.minutes,
                raw_value=feature.value,
                within_position_percentile=_midrank_percentile(feature.value, references[name]),
                governed_minutes_denominator=row.minutes,
                minute_state=cast(Any, row.minute_state),
                coverage=_coverage(
                    row.source_action_count,
                    row.source_action_count,
                    "retained player actions / retained player actions searched by the exact "
                    "predicate",
                ),
                position_reference=f"all comparable observed {row.position_code} matrix rows",
                position_reference_count=len(references[name]),
                derivation_version="w10-expert-evidence-derivation-v2",
                source_lineage_digest=row.source_lineage_digest,
                limitation=_MINUTE_LIMITATION,
            )
        )
    return EvidenceFamilyV2(
        family_id="W09-INPUT-01",
        label="Frozen W09 scorer inputs",
        definition="The exact 16 ordered per-90 fields consumed by frozen W09 ranking.",
        purpose=EvidencePurposeV2.W09_INPUT,
        used_by_w09_ranking=True,
        availability=EvidenceAvailabilityV2.OBSERVED_VALUE,
        exact_family_predicate="exact ordered W09 feature registry predicates",
        raw_opportunity_denominator=row.source_action_count,
        opportunity_floor=0,
        opportunity_components=(
            EvidenceOpportunityComponentV2(
                component_id="governed_matrix_row",
                exact_predicate="exact ordered W09 feature registry predicates",
                raw_opportunity_denominator=row.source_action_count,
                opportunity_floor=0,
                coverage=_coverage(
                    row.source_action_count,
                    row.source_action_count,
                    "retained player actions / same retained matrix action set",
                ),
            ),
        ),
        threshold_policy_version="w10-evidence-opportunity-thresholds-v2-prepilot",
        threshold_rationale="W09 eligibility already governs these exact frozen matrix fields.",
        mandatory_for_selected_rubric=True,
        metrics=tuple(metrics),
    )


def _glossary(metrics: Sequence[EvidenceMetricV2]) -> tuple[EvidenceGlossaryEntryV2, ...]:
    return tuple(
        EvidenceGlossaryEntryV2(
            metric_id=metric.metric_id,
            label=metric.label,
            definition=metric.definition,
            denominator_definition=(
                "The raw opportunity denominator shown on this metric; per-90 rows additionally "
                "use governed minutes."
            ),
            direction_notice=cast(Any, _NEUTRAL_DIRECTION_NOTICE),
            coverage_definition=metric.coverage.definition,
            limitation=metric.limitation,
            purpose=metric.purpose,
            used_by_w09_ranking=metric.used_by_w09_ranking,
        )
        for metric in metrics
    )


def _unsupported_inferences(position_code: str) -> tuple[UnsupportedInferenceV2, ...]:
    common = (
        ("general.causal_tactics", "Causal tactics"),
        ("general.off_ball_movement", "Off-ball movement"),
        ("general.pressing_intensity", "Pressing intensity"),
        ("general.possession_responsibility", "True possession responsibility"),
        ("general.role_instructions", "Role instructions"),
        ("general.formation_adjustment", "Formation-adjusted behaviour"),
        ("general.opponent_context", "Opponent/context adjustment"),
        ("general.current_future_ability", "Current ability or future performance"),
        ("general.availability_fit_value", "Availability, team fit or value"),
        ("general.recruitment_outcomes", "Recruitment or transfer outcomes"),
    )
    position_specific: Mapping[str, tuple[tuple[str, str], ...]] = {
        "GK": (
            ("gk.shots_faced", "Shots faced"),
            ("gk.save_percentage", "Save percentage"),
            ("gk.shot_stopping_quality", "Shot-stopping quality"),
            ("gk.goals_conceded", "Goals conceded"),
            ("gk.expected_goals", "xG or post-shot xG"),
            ("gk.goals_prevented", "Goals prevented"),
            ("gk.claims_cross_dominance", "Claims or cross dominance"),
            ("gk.errors", "Goalkeeper errors"),
            ("gk.sweeping_effectiveness", "Sweeping effectiveness"),
        ),
        "DF": (("df.off_ball_defensive_role", "Off-ball defensive role"),),
        "MD": (("md.off_ball_midfield_role", "Off-ball midfield role"),),
        "FW": (("fw.off_ball_attacking_role", "Off-ball attacking role"),),
    }
    return tuple(
        UnsupportedInferenceV2(
            inference_id=inference_id,
            label=label,
            definition=f"The retained canonical source does not establish {label.casefold()}.",
            evidence_class="UNSUPPORTED_INFERENCE",
            availability=EvidenceAvailabilityV2.NOT_CAPTURED,
            limitation=(
                "Unavailable evidence is never inferred, imputed, rendered as zero or "
                "described as an estimate."
            ),
        )
        for inference_id, label in (*common, *position_specific[position_code])
    )


def build_expert_evidence_bundles_v2(
    matrix: LoadedFeatureMatrix,
    *,
    action_paths: Sequence[Path],
    selected_grain_ids: Sequence[str],
    md_subrubrics: Mapping[str, MdEvidenceSubrubricV2] | None = None,
    policy: ExpertEvidencePolicyV2 | None = None,
) -> tuple[ParticipantExpertEvidenceBundleV2, ...]:
    """Build exact participant panels; mandatory-family failures are query-ineligible errors."""

    active_policy = policy or load_expert_evidence_policy_v2()
    if (
        matrix.manifest.matrix_version != active_policy.matrix_version
        or matrix.manifest.matrix_digest != active_policy.matrix_digest
        or matrix.manifest.canonical_build_digest != _ACCEPTED_CANONICAL_MANIFEST_DIGEST_V2
        or matrix.manifest.feature_names != active_policy.feature_names
    ):
        raise ExpertEvidenceBuildError("accepted W09 matrix authority is incompatible")
    if len(selected_grain_ids) != len(set(selected_grain_ids)):
        raise ExpertEvidenceBuildError("selected evidence grains must be unique")
    rows_by_grain = {row.grain_id: row for row in matrix.rows}
    try:
        selected_rows = tuple(rows_by_grain[grain_id] for grain_id in selected_grain_ids)
    except KeyError as exc:
        raise ExpertEvidenceBuildError("selected grain is absent from accepted W09") from exc
    branches = md_subrubrics or {}
    if set(branches) - set(selected_grain_ids):
        raise ExpertEvidenceBuildError("MD sub-rubric contains an unselected grain")
    if any((row.position_code == "MD") != (row.grain_id in branches) for row in selected_rows):
        raise ExpertEvidenceBuildError("every selected MD and only MD requires a frozen sub-rubric")
    aggregates = aggregate_actions_v2(matrix.rows, action_paths)
    raw_by_grain = {
        row.grain_id: _raw_families(row, aggregates[row.grain_id], active_policy)
        for row in matrix.rows
    }
    if any(
        aggregates[row.grain_id].total_actions != row.source_action_count for row in matrix.rows
    ):
        raise ExpertEvidenceBuildError(
            "canonical descriptor action counts do not reconcile to the W09 matrix"
        )
    rows_by_position = {
        position: tuple(row for row in matrix.rows if row.position_code == position)
        for position in ("GK", "DF", "MD", "FW")
    }
    family_order = (
        "ID-LOC-01",
        "ID-PASS-01",
        "ID-DUEL-01",
        "ID-DEFLOC-01",
        "ID-SHOTLOC-01",
        "ID-GK-01",
    )
    positioned_raw_by_grain = {
        row.grain_id: {
            family_id: _position_family(
                row.position_code,
                family_id,
                raw_by_grain[row.grain_id][family_id],
            )
            for family_id in family_order
        }
        for row in matrix.rows
    }
    independent_reference_values: dict[tuple[str, str, str], list[float]] = {}
    for position_code, position_rows in rows_by_position.items():
        for reference in position_rows:
            for family_id in family_order:
                reference_raw = positioned_raw_by_grain[reference.grain_id][family_id]
                if reference_raw.availability not in {
                    EvidenceAvailabilityV2.OBSERVED_VALUE,
                    EvidenceAvailabilityV2.OBSERVED_ZERO,
                }:
                    continue
                for metric in reference_raw.metrics:
                    if metric.value is not None:
                        independent_reference_values.setdefault(
                            (position_code, family_id, metric.metric_id), []
                        ).append(metric.value)
    bundles: list[ParticipantExpertEvidenceBundleV2] = []
    for row in selected_rows:
        branch = branches.get(row.grain_id)
        mandatory = {
            "GK": {"ID-LOC-01", "ID-PASS-01", "ID-GK-01"},
            "DF": {"ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-DEFLOC-01"},
            "FW": {"ID-LOC-01", "ID-PASS-01", "ID-DUEL-01", "ID-SHOTLOC-01"},
            "MD": {
                "ID-LOC-01",
                "ID-PASS-01",
                "ID-DUEL-01",
                "ID-DEFLOC-01" if branch is MdEvidenceSubrubricV2.DEFENSIVE else "ID-SHOTLOC-01",
            },
        }[row.position_code]
        families: list[EvidenceFamilyV2] = []
        for family_id in family_order:
            raw = positioned_raw_by_grain[row.grain_id][family_id]
            if family_id in mandatory and raw.availability not in {
                EvidenceAvailabilityV2.OBSERVED_VALUE,
                EvidenceAvailabilityV2.OBSERVED_ZERO,
            }:
                raise ExpertEvidenceBuildError(
                    f"selected row is query-ineligible: mandatory {family_id} is "
                    f"{raw.availability.value}"
                )
            metrics: list[EvidenceMetricV2] = []
            for metric in raw.metrics:
                percentile: float | None = None
                reference_values = independent_reference_values.get(
                    (row.position_code, family_id, metric.metric_id), []
                )
                if (
                    raw.availability
                    in {
                        EvidenceAvailabilityV2.OBSERVED_VALUE,
                        EvidenceAvailabilityV2.OBSERVED_ZERO,
                    }
                    and metric.value is not None
                ):
                    percentile = _midrank_percentile(metric.value, reference_values)
                metrics.append(
                    _metric_contract(
                        raw_family=raw,
                        metric=metric,
                        row=row,
                        percentile=percentile,
                        position_reference_count=len(reference_values),
                    )
                )
            families.append(
                EvidenceFamilyV2(
                    family_id=cast(Any, family_id),
                    label=raw.label,
                    definition=raw.definition,
                    purpose=EvidencePurposeV2.INDEPENDENT_DESCRIPTOR,
                    used_by_w09_ranking=False,
                    availability=raw.availability,
                    exact_family_predicate=raw.predicate,
                    raw_opportunity_denominator=raw.denominator,
                    opportunity_floor=raw.floor,
                    opportunity_components=tuple(
                        EvidenceOpportunityComponentV2(
                            component_id=item.component_id,
                            exact_predicate=item.predicate,
                            raw_opportunity_denominator=item.denominator,
                            opportunity_floor=item.floor,
                            coverage=item.coverage,
                        )
                        for item in raw.opportunity_components
                    ),
                    threshold_policy_version="w10-evidence-opportunity-thresholds-v2-prepilot",
                    threshold_rationale=_THRESHOLD_RATIONALE,
                    mandatory_for_selected_rubric=family_id in mandatory,
                    metrics=tuple(metrics),
                )
            )
        w09 = _w09_family(
            row,
            rows_by_position=rows_by_position[row.position_code],
            policy=active_policy,
        )
        coordinate_coverage = _coverage(
            aggregates[row.grain_id].starts.valid,
            aggregates[row.grain_id].starts.total,
            "valid recorded starts / retained player actions",
        )
        all_metrics = (*w09.metrics, *(metric for family in families for metric in family.metrics))
        draft = ParticipantExpertEvidenceBundleV2.model_construct(
            evidence_version="w10-expert-evidence-presentation-v2",
            policy_digest=active_policy.policy_digest,
            canonical_build_id=active_policy.canonical_build_id,
            matrix_version=active_policy.matrix_version,
            matrix_digest=active_policy.matrix_digest,
            context=EvidencePlayerContextV2(
                display_name=row.display_name,
                competition_name=row.competition_name,
                season_label=_SEASON_LABEL,
                window_start_utc=row.window_start_utc,
                window_end_utc=row.window_end_utc,
                position_code=row.position_code,
                team_names=row.team_names,
                quantity=EvidenceQuantityV2(
                    governed_minutes=row.minutes,
                    minute_state=cast(Any, row.minute_state),
                    match_count=row.match_count,
                    retained_action_count=row.source_action_count,
                    lineup_match_coverage=_coverage(
                        row.coverage.lineup_matches_observed,
                        row.coverage.lineup_matches_expected,
                        "lineup matches observed / lineup matches expected",
                    ),
                    action_match_coverage=_coverage(
                        row.coverage.action_matches_observed,
                        row.coverage.action_matches_expected,
                        "action matches observed / action matches expected",
                    ),
                    coordinate_coverage=coordinate_coverage,
                    limitation=_MINUTE_LIMITATION,
                ),
            ),
            md_subrubric=branch,
            w09_inputs=w09,
            independent_descriptors=tuple(families),
            unsupported_inferences=_unsupported_inferences(row.position_code),
            glossary=_glossary(all_metrics),
            bundle_digest="0" * 64,
        )
        payload = draft.model_dump(mode="python", exclude={"bundle_digest"})
        payload["bundle_digest"] = canonical_research_digest(draft.digest_projection())
        try:
            bundles.append(ParticipantExpertEvidenceBundleV2(**payload))
        except ValidationError as exc:
            raise ExpertEvidenceBuildError(
                f"selected row is query-ineligible under the frozen rubric: {row.display_name}"
            ) from exc
    return tuple(bundles)


def build_participant_evidence_comparison_v2(
    exemplar: ParticipantExpertEvidenceBundleV2,
    candidate: ParticipantExpertEvidenceBundleV2,
) -> ParticipantEvidenceComparisonV2:
    """Bind exactly two participant panels under one comparable position/rubric digest."""

    if (
        exemplar.context.position_code != candidate.context.position_code
        or exemplar.policy_digest != candidate.policy_digest
        or exemplar.md_subrubric is not candidate.md_subrubric
    ):
        raise ExpertEvidenceBuildError(
            "evidence comparison panels must share position, policy and MD branch"
        )
    draft = ParticipantEvidenceComparisonV2.model_construct(
        comparison_version="w10-expert-evidence-comparison-v2",
        policy_digest=exemplar.policy_digest,
        position_code=exemplar.context.position_code,
        md_subrubric=exemplar.md_subrubric,
        exemplar=exemplar,
        candidate=candidate,
        comparison_digest="0" * 64,
    )
    payload = draft.model_dump(mode="python", exclude={"comparison_digest"})
    payload["comparison_digest"] = canonical_research_digest(draft.digest_projection())
    try:
        return ParticipantEvidenceComparisonV2(**payload)
    except ValidationError as exc:
        raise ExpertEvidenceBuildError("participant evidence comparison is incompatible") from exc


def load_production_evidence_inputs_v2() -> tuple[LoadedFeatureMatrix, tuple[Path, ...]]:
    """Verify exact accepted matrix and canonical action artifact bytes."""

    matrix = load_feature_matrix(MATRIX_MANIFEST_PATH, artifact_root=DEFAULT_MATRIX_ARTIFACT_ROOT)
    try:
        manifest_path = _safe_single_link_file(CANONICAL_MANIFEST_PATH, root=PROJECT_ROOT)
        manifest_payload = manifest_path.read_bytes()
        if (
            hashlib.sha256(manifest_payload).hexdigest() != _ACCEPTED_CANONICAL_MANIFEST_DIGEST_V2
            or matrix.manifest.canonical_build_digest != _ACCEPTED_CANONICAL_MANIFEST_DIGEST_V2
        ):
            raise ExpertEvidenceBuildError("canonical manifest digest is not the accepted pin")
        manifest = json.loads(manifest_payload)
    except ExpertEvidenceBuildError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExpertEvidenceBuildError("canonical manifest is absent or invalid") from exc
    if (
        canonical_json_bytes(manifest) != manifest_payload
        or manifest.get("canonical_build_id") != _ACCEPTED_CANONICAL_BUILD_ID_V2
    ):
        raise ExpertEvidenceBuildError("canonical manifest identity or bytes drifted")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ExpertEvidenceBuildError("canonical artifact authority is absent")
    action_paths: list[Path] = []
    for descriptor in artifacts:
        if not isinstance(descriptor, dict) or descriptor.get("role") != "canonical_actions":
            continue
        relative = descriptor.get("path")
        if type(relative) is not str or relative.startswith("/") or ".." in relative.split("/"):
            raise ExpertEvidenceBuildError("canonical action path is unsafe")
        path = _safe_single_link_file(PROJECT_ROOT / relative, root=PROJECT_ROOT)
        if _sha256(path) != descriptor.get("sha256"):
            raise ExpertEvidenceBuildError("canonical action physical authority drifted")
        if path.stat().st_size != descriptor.get("size_bytes"):
            raise ExpertEvidenceBuildError("canonical action size authority drifted")
        action_paths.append(path)
    if len(action_paths) != 5:
        raise ExpertEvidenceBuildError("exact canonical action partition roster is absent")
    return matrix, tuple(action_paths)


def _safe_single_link_file(path: Path, *, root: Path) -> Path:
    """Reject symlinked components, root escapes and hard-linked physical aliases."""

    try:
        lexical_path = path.absolute()
        resolved_root = root.resolve(strict=True)
        resolved_path = path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
        stat = resolved_path.stat()
    except (OSError, ValueError) as exc:
        raise ExpertEvidenceBuildError("canonical physical authority is unsafe") from exc
    if resolved_path != lexical_path or not resolved_path.is_file() or stat.st_nlink != 1:
        raise ExpertEvidenceBuildError("canonical physical authority is unsafe")
    return resolved_path


def _participant_safe_bytes_v2(
    value: ParticipantExpertEvidenceBundleV2 | ParticipantEvidenceComparisonV2,
) -> bytes:
    payload = value.model_dump(mode="json")

    def inspect(value: object) -> None:
        if isinstance(value, dict):
            if _FORBIDDEN_PARTICIPANT_KEYS.intersection(value):
                raise ExpertEvidenceBuildError("protected provenance key reached participant bytes")
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
        elif isinstance(value, str) and value.casefold() in _FORBIDDEN_PARTICIPANT_VALUES:
            raise ExpertEvidenceBuildError("protected provenance value reached participant bytes")

    inspect(payload)
    return canonical_json_bytes(payload)


def participant_safe_evidence_bytes_v2(bundle: ParticipantExpertEvidenceBundleV2) -> bytes:
    """Serialize one panel only; panel lists are not an authorised task pack."""

    return _participant_safe_bytes_v2(bundle)


def participant_safe_comparison_bytes_v2(
    comparison: ParticipantEvidenceComparisonV2,
) -> bytes:
    """Serialize the exact pair authority after protected-field inspection."""

    return _participant_safe_bytes_v2(comparison)


__all__ = [
    "CANONICAL_MANIFEST_PATH",
    "MATRIX_MANIFEST_PATH",
    "POLICY_PATH",
    "ExpertEvidenceBuildError",
    "aggregate_actions_v2",
    "build_expert_evidence_bundles_v2",
    "build_participant_evidence_comparison_v2",
    "load_expert_evidence_policy_v2",
    "load_production_evidence_inputs_v2",
    "participant_safe_evidence_bytes_v2",
    "participant_safe_comparison_bytes_v2",
]

"""Deterministic W03 retrieval over a validated development-domain snapshot."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from string import Formatter
from typing import Any, Literal, Protocol, cast
from uuid import UUID

from scouting.contracts import (
    ApplicabilityState,
    ConfidenceAssessment,
    CoverageDimension,
    DataCoverage,
    DependencyKind,
    DependencyLineage,
    EvidenceDependency,
    EvidenceDimension,
    EvidenceDimensionName,
    RetrievalCandidate,
    RetrievalRequest,
    RetrievalResult,
    RoleBrief,
    TemporalEvidence,
)

_DOMAIN_SCHEMA_VERSION = 1
_DEVELOPMENT_CLASSIFICATION = "w03_synthetic_generated"
_UUID_MODULUS = 1 << 128
_RESULT_ID_DOMAIN_OFFSET = 1 << 124
_RUN_ID_DOMAIN_OFFSET = 2 << 124
type FixturePartition = Literal["development", "protected_test"]


class ServingDenied(ValueError):
    """Fail-closed serving input or evidence rejection."""


class EligibilityDecisionLike(Protocol):
    """Structural boundary for a policy admission outcome."""

    admitted: bool
    reason_code: str


class SyntheticRightsEvaluator(Protocol):
    """Serving-side interface implemented by the W03 rights policy."""

    classification: str

    def decide_fact(
        self,
        *,
        classification: str | None,
        observed_at: datetime,
        available_at: datetime | None,
        cutoff: datetime,
        generated: bool,
        identity_unambiguous: bool,
    ) -> object: ...


@dataclass(frozen=True, slots=True)
class SyntheticPlayer:
    """Synthetic player attributes needed by the declared hard constraint."""

    player_id: UUID
    display_name: str
    position: str


@dataclass(frozen=True, slots=True)
class SyntheticFact:
    """One admitted, strictly pre-cutoff synthetic fact."""

    fact_id: UUID
    player_id: UUID
    metric: str
    value: float
    observed_at: datetime
    available_at: datetime


@dataclass(frozen=True, slots=True)
class RejectedEvidence:
    """One fact suppressed with a bounded reason."""

    fact_id: UUID
    reason_code: str


@dataclass(frozen=True, slots=True)
class SyntheticDomainSnapshot:
    """Validated domain input held in memory before request handling."""

    fixture_id: str
    partition: FixturePartition
    manifest_digest: str
    classification: str
    decision_cutoff_ts: datetime
    players: tuple[SyntheticPlayer, ...]
    admitted_facts: tuple[SyntheticFact, ...]
    rejected_facts: tuple[RejectedEvidence, ...]
    ambiguous_player_ids: frozenset[UUID]

    @classmethod
    def from_path(
        cls,
        domain_name: str | Path,
        *,
        allowed_fixture_root: Path,
        expected_partition: FixturePartition = "development",
        rights_policy: SyntheticRightsEvaluator,
    ) -> SyntheticDomainSnapshot:
        """Resolve and load one explicitly partitioned domain beneath an allowed root."""
        if expected_partition not in {"development", "protected_test"}:
            raise ServingDenied("domain partition selection is invalid")
        path = _resolve_domain_path(
            domain_name,
            allowed_fixture_root=allowed_fixture_root,
        )
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ServingDenied("domain fixture is unavailable") from exc
        if not isinstance(document, dict) or set(document) != {"manifest", "payload"}:
            raise ServingDenied("domain envelope is invalid")
        manifest = _object(document["manifest"], context="domain manifest")
        payload = _object(document["payload"], context="domain payload")
        if manifest.get("schema_version") != _DOMAIN_SCHEMA_VERSION:
            raise ServingDenied("domain schema version is unsupported")
        partition = manifest.get("partition")
        if partition != expected_partition:
            raise ServingDenied("domain partition does not match the explicit selection")
        classification = manifest.get("classification")
        if classification != rights_policy.classification:
            raise ServingDenied("domain rights classification is denied")
        digest = _canonical_digest(payload)
        if manifest.get("content_digest") != digest:
            raise ServingDenied("domain manifest digest does not match its content")

        cutoff = _utc(payload.get("decision_cutoff_ts"), context="decision cutoff")
        players = _players(payload.get("players"))
        ambiguous = _ambiguous_players(payload.get("identity_records"))
        admitted, rejected = _facts(
            payload.get("facts"),
            classification=cast(str, classification),
            cutoff=cutoff,
            ambiguous_player_ids=ambiguous,
            rights_policy=rights_policy,
        )
        fixture_id = manifest.get("fixture_id")
        if not isinstance(fixture_id, str) or not fixture_id.strip():
            raise ServingDenied("domain fixture id is invalid")
        return cls(
            fixture_id=fixture_id,
            partition=expected_partition,
            manifest_digest=digest,
            classification=cast(str, classification),
            decision_cutoff_ts=cutoff,
            players=players,
            admitted_facts=admitted,
            rejected_facts=rejected,
            ambiguous_player_ids=ambiguous,
        )


@dataclass(frozen=True, slots=True)
class RetrievalPresentationProfile:
    """Strict immutable presentation evidence selected with an artifact catalog."""

    dimensions: tuple[EvidenceDimension, ...]
    candidate_confidence: ConfidenceAssessment
    candidate_reason_codes: tuple[str, ...]
    explanation_reason_codes: tuple[str, ...]
    explanation_template: str

    def __post_init__(self) -> None:
        if not isinstance(self.dimensions, tuple):
            raise TypeError("presentation dimensions must be a tuple")
        if len(self.dimensions) != len(EvidenceDimensionName):
            raise ValueError("presentation profile must define all six dimensions")
        if not all(isinstance(dimension, EvidenceDimension) for dimension in self.dimensions):
            raise TypeError("presentation dimensions must be evidence dimensions")
        dimension_names = tuple(dimension.name for dimension in self.dimensions)
        if len(dimension_names) != len(set(dimension_names)):
            raise ValueError("presentation dimensions must be unique")
        if set(dimension_names) != set(EvidenceDimensionName):
            raise ValueError("presentation profile must define all six dimensions")
        for dimension in self.dimensions:
            _validate_unit_interval(
                dimension.score,
                context=f"{dimension.name.value} score",
            )
            _validate_unit_interval(
                dimension.confidence,
                context=f"{dimension.name.value} confidence",
            )
            _validate_text_tuple(
                dimension.reason_codes,
                context=f"{dimension.name.value} reason codes",
            )
        if not isinstance(self.candidate_confidence, ConfidenceAssessment):
            raise TypeError("candidate confidence must be a confidence assessment")
        _validate_unit_interval(
            self.candidate_confidence.score,
            context="candidate confidence score",
        )
        _validate_text_tuple(
            self.candidate_confidence.limitations,
            context="candidate limitations",
        )
        _validate_text_tuple(
            self.candidate_reason_codes,
            context="candidate reason codes",
        )
        _validate_text_tuple(
            self.explanation_reason_codes,
            context="explanation reason codes",
        )
        _validate_explanation_template(self.explanation_template)

    @classmethod
    def development(cls) -> RetrievalPresentationProfile:
        """Return the frozen development presentation evidence."""
        return cls(
            dimensions=(
                EvidenceDimension(
                    name=EvidenceDimensionName.STYLE_RESEMBLANCE,
                    score=0.82,
                    confidence=0.8,
                    reason_codes=("synthetic_progressive_actions_match",),
                ),
                EvidenceDimension(
                    name=EvidenceDimensionName.ROLE_COMPATIBILITY,
                    score=0.9,
                    confidence=1.0,
                    reason_codes=("synthetic_position_constraint_met",),
                ),
                EvidenceDimension(
                    name=EvidenceDimensionName.IMPACT,
                    score=0.6,
                    confidence=0.5,
                    reason_codes=("synthetic_impact_evidence_limited",),
                ),
                EvidenceDimension(
                    name=EvidenceDimensionName.TRAJECTORY,
                    score=0.5,
                    confidence=0.4,
                    reason_codes=("synthetic_trajectory_evidence_limited",),
                ),
                EvidenceDimension(
                    name=EvidenceDimensionName.TRANSFER_RISK,
                    score=0.5,
                    confidence=0.2,
                    reason_codes=("synthetic_transfer_data_unavailable",),
                ),
                EvidenceDimension(
                    name=EvidenceDimensionName.DATA_CONFIDENCE,
                    score=0.67,
                    confidence=1.0,
                    reason_codes=("synthetic_temporal_coverage_partial",),
                ),
            ),
            candidate_confidence=ConfidenceAssessment(
                score=0.67,
                applicability=ApplicabilityState.LIMITED,
                limitations=(
                    "Synthetic W03 contract evidence only",
                    "No expert relevance or model-performance claim",
                ),
            ),
            candidate_reason_codes=(
                "synthetic_progressive_wide_role_match",
                "resemblance_only",
            ),
            explanation_reason_codes=(
                "synthetic_progressive_wide_role_match",
                "synthetic_temporal_coverage_partial",
            ),
            explanation_template=(
                "{candidate_display_name} resembles the synthetic brief on declared "
                "progressive-action evidence; this is not a prediction of recruitment "
                "success."
            ),
        )

    def render_explanation(self, *, candidate_display_name: str) -> str:
        """Render static text unchanged or safely populate the sole permitted field."""
        if not isinstance(candidate_display_name, str) or not candidate_display_name.strip():
            raise ServingDenied("candidate display name is invalid")
        if not _explanation_template_fields(self.explanation_template):
            return self.explanation_template
        return self.explanation_template.format(candidate_display_name=candidate_display_name)


@dataclass(frozen=True, slots=True)
class SyntheticArtifactCatalog:
    """Pinned synthetic seam evidence; none means explicitly unavailable."""

    source_manifest_id: UUID
    feature_schema_id: UUID
    feature_schema_hash: str
    model_artifact_id: UUID | None
    model_artifact_digest: str | None
    model_version: str | None
    retrieval_index_id: UUID | None
    retrieval_index_digest: str | None
    index_version: str | None
    presentation_profile: RetrievalPresentationProfile
    source_observed_at: datetime
    source_available_at: datetime
    feature_schema_observed_at: datetime
    feature_schema_available_at: datetime
    model_artifact_observed_at: datetime
    model_artifact_available_at: datetime
    retrieval_index_observed_at: datetime
    retrieval_index_available_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.presentation_profile, RetrievalPresentationProfile):
            raise TypeError("artifact presentation profile is invalid")

    @classmethod
    def development(cls) -> SyntheticArtifactCatalog:
        """Return the reviewed W03 development seam identifiers."""
        return cls(
            source_manifest_id=UUID("90000000-0000-4000-8000-000000000101"),
            feature_schema_id=UUID("90000000-0000-4000-8000-000000000102"),
            feature_schema_hash="1" * 64,
            model_artifact_id=UUID("90000000-0000-4000-8000-000000000103"),
            model_artifact_digest="2" * 64,
            model_version="w03-synthetic-deterministic-retrieval-v1",
            retrieval_index_id=UUID("90000000-0000-4000-8000-000000000104"),
            retrieval_index_digest="3" * 64,
            index_version="w03-development-index-v1",
            presentation_profile=RetrievalPresentationProfile.development(),
            source_observed_at=datetime(2026, 2, 12, 8, 0, tzinfo=UTC),
            source_available_at=datetime(2026, 2, 12, 8, 30, tzinfo=UTC),
            feature_schema_observed_at=datetime(2026, 1, 1, tzinfo=UTC),
            feature_schema_available_at=datetime(2026, 1, 1, tzinfo=UTC),
            model_artifact_observed_at=datetime(2026, 2, 20, 10, 0, tzinfo=UTC),
            model_artifact_available_at=datetime(2026, 2, 20, 10, 0, tzinfo=UTC),
            retrieval_index_observed_at=datetime(2026, 2, 20, 11, 0, tzinfo=UTC),
            retrieval_index_available_at=datetime(2026, 2, 20, 12, 0, tzinfo=UTC),
        )


@dataclass(frozen=True, slots=True)
class ServingExplanation:
    """Non-predictive explanation rendered without presentation arithmetic."""

    player_id: UUID
    claim_boundary: Literal["resemblance_only"]
    reason_codes: tuple[str, ...]
    summary: str


@dataclass(frozen=True, slots=True)
class ServingOutcome:
    """Either a contract-valid result or a labelled unavailable state."""

    status: Literal["available", "unavailable"]
    result: RetrievalResult | None
    explanations: tuple[ServingExplanation, ...]
    admitted_fact_ids: tuple[UUID, ...]
    rejected_evidence: tuple[RejectedEvidence, ...]
    missing_evidence: tuple[str, ...] = ()


class SyntheticServingService:
    """One retrieval seam over preloaded, rights-valid temporal evidence."""

    def __init__(
        self,
        snapshot: SyntheticDomainSnapshot,
        *,
        artifacts: SyntheticArtifactCatalog,
    ) -> None:
        self.snapshot = snapshot
        self.artifacts = artifacts

    def retrieve(
        self,
        role_brief: RoleBrief,
        request: RetrievalRequest,
    ) -> ServingOutcome:
        """Return deterministic resemblance evidence without a quality claim."""
        self._validate_request(role_brief, request)
        missing = self._missing_artifacts()
        if missing:
            return ServingOutcome(
                status="unavailable",
                result=None,
                explanations=(),
                admitted_fact_ids=tuple(fact.fact_id for fact in self.snapshot.admitted_facts),
                rejected_evidence=self.snapshot.rejected_facts,
                missing_evidence=missing,
            )

        selected_evidence = self._candidate_evidence(role_brief, request)
        candidates: tuple[RetrievalCandidate, ...]
        explanations: tuple[ServingExplanation, ...]
        lineage = self._lineage()
        if selected_evidence is None:
            candidates = ()
            explanations = ()
        else:
            candidate_player, _selected_fact = selected_evidence
            coverage = self._coverage()
            profile = self.artifacts.presentation_profile
            candidates = (
                self._retrieval_candidate(
                    candidate_player,
                    lineage,
                    coverage,
                    rank=1,
                    profile=profile,
                ),
            )
            explanations = (
                ServingExplanation(
                    player_id=candidate_player.player_id,
                    claim_boundary="resemblance_only",
                    reason_codes=profile.explanation_reason_codes,
                    summary=profile.render_explanation(
                        candidate_display_name=candidate_player.display_name
                    ),
                ),
            )

        generated_at = request.requested_at + timedelta(seconds=1)
        temporal = TemporalEvidence(
            snapshot_as_of_ts=request.feature_cutoff_ts - timedelta(seconds=1),
            available_at_watermark=lineage.available_at_watermark,
            valid_from_ts=request.feature_cutoff_ts - timedelta(seconds=1),
            generated_at_ts=generated_at,
            feature_cutoff_ts=request.feature_cutoff_ts,
            source_manifest_ids=(self.artifacts.source_manifest_id,),
            feature_schema_hash=self.artifacts.feature_schema_hash,
            dependency_lineage_hash=lineage.lineage_hash,
            dependency_lineage=lineage,
        )
        retrieval_result_id, retrieval_run_id = _derive_retrieval_ids(request.retrieval_request_id)
        result = RetrievalResult(
            retrieval_result_id=retrieval_result_id,
            retrieval_request_id=request.retrieval_request_id,
            retrieval_run_id=retrieval_run_id,
            tenant_context=request.tenant_context,
            version=1,
            trace_id=request.trace_id,
            role_brief_id=role_brief.role_brief_id,
            role_brief_version=role_brief.version,
            model_version=cast(str, self.artifacts.model_version),
            index_version=cast(str, self.artifacts.index_version),
            generated_at=generated_at,
            temporal_evidence=temporal,
            candidates=candidates,
        )
        return ServingOutcome(
            status="available",
            result=result,
            explanations=explanations,
            admitted_fact_ids=tuple(fact.fact_id for fact in self.snapshot.admitted_facts),
            rejected_evidence=self.snapshot.rejected_facts,
        )

    def _validate_request(self, role_brief: RoleBrief, request: RetrievalRequest) -> None:
        if role_brief.status.value != "approved":
            raise ServingDenied("retrieval requires an approved role brief")
        if role_brief.tenant_context != request.tenant_context:
            raise ServingDenied("retrieval tenant context mismatch")
        if role_brief.trace_id != request.trace_id:
            raise ServingDenied("retrieval trace context mismatch")
        if (
            request.role_brief_id != role_brief.role_brief_id
            or request.role_brief_version != role_brief.version
        ):
            raise ServingDenied("retrieval request does not bind the role brief version")
        if request.feature_cutoff_ts != self.snapshot.decision_cutoff_ts:
            raise ServingDenied("retrieval cutoff does not match the frozen domain")

    def _missing_artifacts(self) -> tuple[str, ...]:
        missing: list[str] = []
        if (
            self.artifacts.model_artifact_id is None
            or self.artifacts.model_artifact_digest is None
            or self.artifacts.model_version is None
        ):
            missing.append("model_artifact")
        if (
            self.artifacts.retrieval_index_id is None
            or self.artifacts.retrieval_index_digest is None
            or self.artifacts.index_version is None
        ):
            missing.append("retrieval_index")
        return tuple(missing)

    def _candidate_evidence(
        self,
        role_brief: RoleBrief,
        request: RetrievalRequest,
    ) -> tuple[SyntheticPlayer, SyntheticFact] | None:
        eligible_players = {
            player.player_id: player
            for player in self.snapshot.players
            if player.player_id not in self.snapshot.ambiguous_player_ids
            and player.player_id not in request.excluded_player_ids
            and _matches_hard_constraints(player, role_brief)
        }
        eligible_facts = [
            fact for fact in self.snapshot.admitted_facts if fact.player_id in eligible_players
        ]
        if not eligible_facts:
            return None
        selected = max(
            eligible_facts,
            key=lambda fact: (
                fact.value,
                fact.metric,
                fact.observed_at,
                fact.available_at,
                str(fact.player_id),
                str(fact.fact_id),
            ),
        )
        return eligible_players[selected.player_id], selected

    def _lineage(self) -> DependencyLineage:
        dependencies = (
            EvidenceDependency(
                kind=DependencyKind.SOURCE_MANIFEST,
                dependency_id=self.artifacts.source_manifest_id,
                digest=self.snapshot.manifest_digest,
                observed_at=self.artifacts.source_observed_at,
                available_at=self.artifacts.source_available_at,
            ),
            EvidenceDependency(
                kind=DependencyKind.FEATURE_SCHEMA,
                dependency_id=self.artifacts.feature_schema_id,
                digest=self.artifacts.feature_schema_hash,
                observed_at=self.artifacts.feature_schema_observed_at,
                available_at=self.artifacts.feature_schema_available_at,
            ),
            EvidenceDependency(
                kind=DependencyKind.MODEL_ARTIFACT,
                dependency_id=cast(UUID, self.artifacts.model_artifact_id),
                digest=cast(str, self.artifacts.model_artifact_digest),
                observed_at=self.artifacts.model_artifact_observed_at,
                available_at=self.artifacts.model_artifact_available_at,
            ),
            EvidenceDependency(
                kind=DependencyKind.RETRIEVAL_INDEX,
                dependency_id=cast(UUID, self.artifacts.retrieval_index_id),
                digest=cast(str, self.artifacts.retrieval_index_digest),
                observed_at=self.artifacts.retrieval_index_observed_at,
                available_at=self.artifacts.retrieval_index_available_at,
            ),
        )
        digest = _canonical_digest(
            {"dependencies": [dependency.model_dump(mode="json") for dependency in dependencies]}
        )
        return DependencyLineage(lineage_hash=digest, dependencies=dependencies)

    @staticmethod
    def _retrieval_candidate(
        player: SyntheticPlayer,
        lineage: DependencyLineage,
        coverage: DataCoverage,
        *,
        rank: int,
        profile: RetrievalPresentationProfile,
    ) -> RetrievalCandidate:
        return RetrievalCandidate(
            player_id=player.player_id,
            rank=rank,
            evidence_dimensions=profile.dimensions,
            confidence=profile.candidate_confidence,
            coverage=coverage,
            lineage=lineage,
            reason_codes=profile.candidate_reason_codes,
        )

    def _coverage(self) -> DataCoverage:
        observed_count = len(self.snapshot.admitted_facts)
        expected_count = observed_count + len(self.snapshot.rejected_facts)
        overall = round(observed_count / expected_count, 4) if expected_count else 0.0
        return DataCoverage(
            overall=overall,
            dimensions=(
                CoverageDimension(
                    name="temporally_eligible_facts",
                    coverage=overall,
                    observed_count=observed_count,
                    expected_count=expected_count,
                ),
            ),
            missing_dimensions=("real_provider_evidence", "expert_labels"),
        )


def _derive_retrieval_ids(request_id: UUID) -> tuple[UUID, UUID]:
    """Derive stable request-bound IDs with bijective result/run domain offsets."""
    result_id = UUID(int=(request_id.int + _RESULT_ID_DOMAIN_OFFSET) % _UUID_MODULUS)
    run_id = UUID(int=(request_id.int + _RUN_ID_DOMAIN_OFFSET) % _UUID_MODULUS)
    return result_id, run_id


def _matches_hard_constraints(
    player: SyntheticPlayer,
    role_brief: RoleBrief,
) -> bool:
    attributes = {
        "display_name": player.display_name,
        "player_id": str(player.player_id),
        "position": player.position,
    }
    for constraint in role_brief.hard_constraints:
        actual = attributes.get(constraint.field)
        if actual is None:
            raise ServingDenied("unsupported hard-constraint field")
        operator = constraint.operator.value
        if operator == "equals" and actual != constraint.value:
            return False
        if operator == "not_equals" and actual == constraint.value:
            return False
        if operator == "in":
            choices = {choice.strip() for choice in constraint.value.split(",") if choice.strip()}
            if not choices or actual not in choices:
                return False
        if operator in {"at_least", "at_most"}:
            raise ServingDenied("unsupported hard-constraint operator")
    return True


def _validate_unit_interval(value: object, *, context: str) -> None:
    if type(value) is not float or not 0.0 <= value <= 1.0:
        raise ValueError(f"{context} must be a finite strict float in [0, 1]")


def _validate_text_tuple(values: object, *, context: str) -> None:
    if not isinstance(values, tuple) or not values:
        raise ValueError(f"{context} must be a non-empty tuple")
    if any(
        type(value) is not str or not value or value != value.strip() or len(value) > 512
        for value in values
    ):
        raise ValueError(f"{context} must contain bounded non-empty strings")
    if len(values) != len(set(values)):
        raise ValueError(f"{context} must be unique")


def _validate_explanation_template(template: object) -> None:
    if (
        type(template) is not str
        or not template
        or template != template.strip()
        or len(template) > 512
    ):
        raise ValueError("explanation template must be a bounded non-empty string")
    fields = _explanation_template_fields(template)
    if fields not in ((), (("candidate_display_name", "", None),)):
        raise ValueError(
            "explanation template must be static or contain one plain candidate display name"
        )


def _explanation_template_fields(
    template: str,
) -> tuple[tuple[str, str | None, str | None], ...]:
    try:
        parsed = tuple(Formatter().parse(template))
    except ValueError as exc:
        raise ValueError("explanation template is invalid") from exc
    return tuple(
        (field_name, format_spec, conversion)
        for _, field_name, format_spec, conversion in parsed
        if field_name is not None
    )


def _canonical_digest(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _resolve_domain_path(
    domain_name: str | Path,
    *,
    allowed_fixture_root: Path,
) -> Path:
    relative = Path(domain_name)
    if relative.is_absolute() or ".." in relative.parts or relative.name != "domain.json":
        raise ServingDenied("domain path must be a relative domain name")
    try:
        root = allowed_fixture_root.resolve(strict=True)
    except OSError as exc:
        raise ServingDenied("allowed fixture root is unavailable") from exc
    if not root.is_dir():
        raise ServingDenied("allowed fixture root must be a directory")
    try:
        resolved = (root / relative).resolve(strict=True)
    except OSError as exc:
        raise ServingDenied("domain fixture is unavailable") from exc
    if not resolved.is_relative_to(root):
        raise ServingDenied("domain path escapes the allowed fixture root")
    if not resolved.is_file():
        raise ServingDenied("domain fixture is unavailable")
    return resolved


def _object(value: object, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ServingDenied(f"{context} must be an object")
    return cast(Mapping[str, Any], value)


def _array(value: object, *, context: str) -> list[object]:
    if not isinstance(value, list):
        raise ServingDenied(f"{context} must be an array")
    return cast(list[object], value)


def _uuid(value: object, *, context: str) -> UUID:
    if not isinstance(value, str):
        raise ServingDenied(f"{context} must be a UUID")
    try:
        return UUID(value)
    except ValueError as exc:
        raise ServingDenied(f"{context} must be a UUID") from exc


def _utc(value: object, *, context: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ServingDenied(f"{context} must be UTC")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ServingDenied(f"{context} must be UTC") from exc
    if parsed.utcoffset() != timedelta(0):
        raise ServingDenied(f"{context} must be UTC")
    return parsed


def _players(value: object) -> tuple[SyntheticPlayer, ...]:
    players: list[SyntheticPlayer] = []
    seen: set[UUID] = set()
    for index, raw in enumerate(_array(value, context="players")):
        item = _object(raw, context=f"players[{index}]")
        player_id = _uuid(item.get("id"), context=f"players[{index}].id")
        display_name = item.get("display_name")
        position = item.get("position")
        if (
            player_id in seen
            or not isinstance(display_name, str)
            or not display_name.strip()
            or not isinstance(position, str)
            or not position.strip()
        ):
            raise ServingDenied("player fixture is invalid")
        seen.add(player_id)
        players.append(SyntheticPlayer(player_id, display_name, position))
    return tuple(players)


def _ambiguous_players(value: object) -> frozenset[UUID]:
    ambiguous: set[UUID] = set()
    for index, raw in enumerate(_array(value, context="identity_records")):
        item = _object(raw, context=f"identity_records[{index}]")
        status = item.get("resolution_status")
        if status == "review_required":
            if item.get("canonical_player_id") is not None:
                raise ServingDenied("ambiguous identity guessed a canonical player")
            candidates = _array(
                item.get("candidate_player_ids"),
                context=f"identity_records[{index}].candidate_player_ids",
            )
            if len(candidates) < 2:
                raise ServingDenied("ambiguous identity lacks review candidates")
            ambiguous.update(
                _uuid(candidate, context="ambiguous candidate") for candidate in candidates
            )
        elif status != "resolved":
            raise ServingDenied("identity status is unsupported")
    return frozenset(ambiguous)


def _facts(
    value: object,
    *,
    classification: str,
    cutoff: datetime,
    ambiguous_player_ids: frozenset[UUID],
    rights_policy: SyntheticRightsEvaluator,
) -> tuple[tuple[SyntheticFact, ...], tuple[RejectedEvidence, ...]]:
    admitted: list[SyntheticFact] = []
    rejected: list[RejectedEvidence] = []
    for index, raw in enumerate(_array(value, context="facts")):
        item = _object(raw, context=f"facts[{index}]")
        fact_id = _uuid(item.get("fact_id"), context=f"facts[{index}].fact_id")
        player_id = _uuid(item.get("player_id"), context=f"facts[{index}].player_id")
        observed_at = _utc(item.get("observed_at"), context=f"facts[{index}].observed_at")
        raw_available = item.get("available_at")
        available_at = (
            None
            if raw_available is None
            else _utc(raw_available, context=f"facts[{index}].available_at")
        )
        decision = cast(
            EligibilityDecisionLike,
            rights_policy.decide_fact(
                classification=classification,
                observed_at=observed_at,
                available_at=available_at,
                cutoff=cutoff,
                generated=True,
                identity_unambiguous=player_id not in ambiguous_player_ids,
            ),
        )
        if not decision.admitted:
            rejected.append(RejectedEvidence(fact_id, decision.reason_code))
            continue
        metric = item.get("metric")
        raw_value = item.get("value")
        if (
            not isinstance(metric, str)
            or not metric.strip()
            or isinstance(raw_value, bool)
            or not isinstance(raw_value, (int, float))
            or available_at is None
        ):
            raise ServingDenied("eligible fact payload is invalid")
        admitted.append(
            SyntheticFact(
                fact_id=fact_id,
                player_id=player_id,
                metric=metric,
                value=float(raw_value),
                observed_at=observed_at,
                available_at=available_at,
            )
        )
    admitted.sort(key=lambda fact: (fact.available_at, str(fact.fact_id)))
    rejected.sort(key=lambda fact: str(fact.fact_id))
    return tuple(admitted), tuple(rejected)

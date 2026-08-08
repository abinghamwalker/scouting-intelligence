"""Read-only deterministic serving for the accepted W05 M0 artifact.

This module intentionally contains no fitting, scaling, or distance arithmetic.  The
accepted :mod:`scouting.m0` loader owns artifact validation and its ``score`` method
owns all retrieval geometry.  The two public entry points below are deliberately
thin calls to :class:`M0ServingCore` so a batch replay cannot diverge from a request
replay.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from scouting.contracts import (
    RESEMBLANCE_ONLY_CLAIM,
    ApplicabilityState,
    ConfidenceAssessment,
    CoverageDimension,
    DataConfidenceEvidence,
    DataCoverage,
    DependencyKind,
    DependencyLineage,
    EvidenceDependency,
    EvidenceDimension,
    EvidenceDimensionName,
    FeatureValue,
    FeatureValueState,
    M0CandidateDimensionEvidence,
    M0CandidateExplanation,
    M0DimensionEvidence,
    M0DimensionEvidenceState,
    M0EvidenceClass,
    M0ExplanationInput,
    M0RetrievalResult,
    M0ScoredCandidate,
    M0TiePolicy,
    PinnedM0ServingRequest,
    RetrievalCandidate,
    RetrievalResult,
    TemporalEvidence,
)
from scouting.m0 import M0RuntimeError, load_m0_artifact

M0_SERVING_CORE_VERSION = "m0-shared-core-v1"
"""The sole version accepted by this serving implementation."""

_SERVING_NAMESPACE = UUID("d734f678-3b28-5b69-9183-6dbfb0a21e22")
_REGISTERED_ARTIFACT_ROOT = Path(__file__).resolve().parents[3] / "runs" / "w05" / "m0-baseline-v1"
_SUPPORTED_CONSTRAINT_FIELDS = frozenset(
    {
        "synthetic_position_code",
        "synthetic_age_years",
        "synthetic_elapsed_minutes",
    }
)
_EXPECTED_ARTIFACT_PINS = {
    "expected_artifact_id": "9a0d43c6-d177-51be-8280-3bf02bedbc99",
    "expected_artifact_manifest_digest": (
        "2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9"
    ),
    "expected_feature_schema_hash": (
        "1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f"
    ),
    "expected_taxonomy_id": "w05-football-responsibility-taxonomy-v1",
    "expected_taxonomy_version": "v1",
    "expected_taxonomy_digest": "59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097",
    "expected_configuration_digest": (
        "5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a"
    ),
    "expected_fitting_population_id": "w05-synthetic-development-complete-rows-v1",
    "expected_fitting_population_count": 18,
    "expected_fitting_population_manifest_digest": (
        "60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086"
    ),
    "expected_candidate_universe_id": "w05-synthetic-development-candidate-universe-v1",
    "expected_candidate_universe_count": 18,
    "expected_candidate_universe_manifest_digest": (
        "2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e"
    ),
    "expected_lineage_identity": "e77de98a171447b8a3361161e5efbc8173909f933435f27ac99e0534c6d591c7",
    "expected_model_id": "w05-m0-role_aware_restriction-v1",
    "expected_model_version": "v1",
    "expected_index_id": "w05-m0-role_aware_restriction-index-v1",
    "expected_index_version": "v1",
}


class M0ServingError(ValueError):
    """Raised when serving cannot prove a complete pinned, local M0 replay."""


class M0ServingReason(StrEnum):
    """Closed serving reason-code vocabulary in canonical emission order."""

    ARTIFACT_PINNED = "artifact_pinned"
    TEMPORAL_LINEAGE_PINNED = "temporal_lineage_pinned"
    QUERY_PLAYER_RESOLVED = "query_player_resolved"
    EXEMPLAR_QUERY_RESOLVED = "exemplar_query_resolved"
    HARD_CONSTRAINTS_APPLIED = "hard_constraints_applied"
    ROLE_RESTRICTION_APPLIED = "role_restriction_applied"
    STYLE_DISTANCE_VIEW = "style_distance_view"
    ROLE_COMPATIBILITY_MEASURED = "role_compatibility_measured"
    ROLE_COMPATIBILITY_ZERO = "role_compatibility_zero"
    COVERAGE_COMPLETE = "coverage_complete"
    SYNTHETIC_DEVELOPMENT_ONLY = "synthetic_development_only"
    NO_RECOMMENDATION_EVIDENCE = "no_recommendation_evidence"
    APPLICABILITY_LIMITED = "applicability_limited"
    APPLICABILITY_APPLICABLE = "applicability_applicable"
    IMPACT_UNAVAILABLE = "impact_unavailable"
    TRAJECTORY_UNAVAILABLE = "trajectory_unavailable"
    TRANSFER_RISK_UNAVAILABLE = "transfer_risk_unavailable"
    W04_ROLE_UNAVAILABLE = "w04_role_compatibility_unavailable"


_REASON_ORDER = tuple(M0ServingReason)


def _canonical_reasons(*reasons: M0ServingReason) -> tuple[str, ...]:
    """Return distinct closed reasons in their one declared wire order."""
    selected = set(reasons)
    return tuple(reason.value for reason in _REASON_ORDER if reason in selected)


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def _request_digest(request: PinnedM0ServingRequest) -> str:
    """Hash the complete normally validated pinned-request wire projection."""
    return _digest(request.model_dump(mode="json"))


def _identifier(
    domain: str,
    request_digest: str,
    artifact_id: UUID,
    artifact_manifest_digest: str,
) -> UUID:
    """Derive a domain-separated UUID from all serving-relevant request identity."""
    return uuid5(
        _SERVING_NAMESPACE,
        "|".join(
            (
                domain,
                M0_SERVING_CORE_VERSION,
                request_digest,
                str(artifact_id),
                artifact_manifest_digest,
            )
        ),
    )


@dataclass(frozen=True, slots=True)
class _ConstraintPlan:
    """One prevalidated canonical hard predicate; execution never parses user input."""

    field: str
    operator: str
    value: str | float | tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _ResultContext:
    """Validated state needed to assemble one immutable serving result."""

    request: PinnedM0ServingRequest
    manifest: Any
    scored_rows: tuple[Any, ...]
    rows: Mapping[UUID, Mapping[str, Any]]
    query_values: tuple[FeatureValue, ...]
    query_roles: Mapping[str, float]
    lineage: DependencyLineage
    temporal: TemporalEvidence
    mode_reason: M0ServingReason
    constraints_applied: bool


def _as_utc(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise M0ServingError(f"{label} is unavailable")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise M0ServingError(f"{label} is invalid") from error
    if parsed.tzinfo is None:
        raise M0ServingError(f"{label} must be UTC-aware")
    return parsed


def _feature_value(value: object) -> FeatureValue:
    """Project an admitted raw feature state without imputing any value."""
    if not isinstance(value, Mapping):
        raise M0ServingError("feature evidence is unavailable")
    state = value.get("state")
    numeric = value.get("numeric_value")
    if state == FeatureValueState.VALUE.value:
        if isinstance(numeric, bool) or not isinstance(numeric, (int, float)):
            raise M0ServingError("feature value is unavailable")
        return FeatureValue(state=FeatureValueState.VALUE, numeric_value=float(numeric))
    if state == FeatureValueState.ZERO.value:
        return FeatureValue(state=FeatureValueState.ZERO, numeric_value=0.0)
    reason = value.get("reason_code")
    if not isinstance(reason, str) or not reason:
        raise M0ServingError("feature absence lacks a reason")
    try:
        return FeatureValue(state=FeatureValueState(str(state)), reason_code=reason)
    except ValueError as error:
        raise M0ServingError("feature state is unsupported") from error


def _canonical_float(value: float) -> float:
    """Preserve scorer values while converting its representational ``-0.0`` to ``+0.0``."""
    return 0.0 if value == 0.0 else value


class M0ServingCore:
    """The one read-only M0 retrieval and explanation path.

    Authorities are injected by composition.  That keeps serving independent of the
    feature, role, provider, and training modules while requiring the shared loader to
    authenticate every authority and the registered artifact on every invocation.
    """

    def __init__(
        self,
        *,
        registry: Any,
        taxonomy: Any,
        configuration: Any,
        candidates: Any,
        queries: Any,
        artifact_root: str | Path = _REGISTERED_ARTIFACT_ROOT,
    ) -> None:
        root = Path(artifact_root)
        try:
            registered = _REGISTERED_ARTIFACT_ROOT.resolve(strict=True)
            supplied = root.resolve(strict=True)
        except OSError as error:
            raise M0ServingError("registered M0 artifact root is unavailable") from error
        if root.is_symlink() or supplied != registered:
            raise M0ServingError("M0 artifact root is not the exact registered bundle")
        self._artifact_root = registered
        self._registry = registry
        self._taxonomy = taxonomy
        self._configuration = configuration
        self._candidates = candidates
        self._queries = queries

    def serve(self, request: PinnedM0ServingRequest) -> M0RetrievalResult:
        """Return one fully pinned result using the shared loader and scorer only."""
        request = self._validated_request(request)
        if request.shared_core_version != M0_SERVING_CORE_VERSION:
            raise M0ServingError("pinned request selects an unsupported serving core")
        if request.tie_policy is not M0TiePolicy.SCORE_DISTANCE_THEN_CANONICAL_PLAYER_UUID_BYTES:
            raise M0ServingError("pinned request selects an unsupported tie policy")
        if request.retrieval_request.claim_boundary != RESEMBLANCE_ONLY_CLAIM:
            raise M0ServingError("only resemblance-only retrieval is supported")

        try:
            loaded = load_m0_artifact(
                self._artifact_root,
                taxonomy=self._taxonomy,
                registry=self._registry,
                configuration=self._configuration,
                candidates=self._candidates,
                queries=self._queries,
            )
            request.require_matching_artifact(loaded.manifest)
        except (M0RuntimeError, ValueError) as error:
            raise M0ServingError("accepted M0 artifact authority is unavailable") from error

        constraint_plan = self._constraint_plan(request.resolved_query.hard_constraints)
        rows = self._candidate_rows()
        query_values, query_roles, mode_reason = self._resolve_query(request, rows)
        permitted_ids = self._permitted_candidate_ids(request, rows, query_roles, constraint_plan)
        requested_exclusions = set(request.retrieval_request.excluded_player_ids)
        scorer_exclusions = tuple(
            sorted(
                requested_exclusions | (set(loaded.player_ids) - permitted_ids),
                key=lambda player_id: player_id.bytes,
            )
        )
        query = request.resolved_query
        try:
            scored_rows = loaded.score(
                query.query_player_id,
                limit=query.limit,
                excluded_player_ids=scorer_exclusions,
                exemplar_player_ids=tuple(
                    sorted(query.exemplar_player_ids, key=lambda item: item.bytes)
                ),
            )
        except M0RuntimeError as error:
            raise M0ServingError("shared M0 scorer rejected the pinned query") from error

        temporal, lineage = self._temporal_evidence(request, loaded.manifest, rows)
        return self._result(
            _ResultContext(
                request=request,
                manifest=loaded.manifest,
                scored_rows=scored_rows,
                rows=rows,
                query_values=query_values,
                query_roles=query_roles,
                lineage=lineage,
                temporal=temporal,
                mode_reason=mode_reason,
                constraints_applied=bool(constraint_plan),
            )
        )

    @staticmethod
    def _validated_request(request: PinnedM0ServingRequest) -> PinnedM0ServingRequest:
        """Rebuild all nested semantics so constructed or copied stale pins fail closed."""
        if not isinstance(request, PinnedM0ServingRequest):
            raise M0ServingError("a pinned M0 serving request is required")
        try:
            rebuilt = PinnedM0ServingRequest.model_validate(request.model_dump(mode="python"))
            query = rebuilt.resolved_query
            if query.resolved_query_digest != query.computed_resolved_query_digest:
                raise ValueError("resolved query digest drift")
            if rebuilt.expected_resolved_query_digest != query.resolved_query_digest:
                raise ValueError("resolved query expected digest drift")
            if (
                rebuilt.ordered_exclusion_digest
                != PinnedM0ServingRequest.ordered_exclusion_digest_for(
                    rebuilt.retrieval_request.excluded_player_ids
                )
            ):
                raise ValueError("exclusion digest drift")
            if any(
                str(getattr(rebuilt, field)) != str(expected)
                for field, expected in _EXPECTED_ARTIFACT_PINS.items()
            ):
                raise ValueError("accepted artifact pin drift")
        except ValueError as error:
            raise M0ServingError("pinned serving request failed normal validation") from error
        return rebuilt

    def _candidate_rows(self) -> Mapping[UUID, Mapping[str, Any]]:
        rows: dict[UUID, Mapping[str, Any]] = {}
        source_rows = getattr(self._candidates, "rows", ())
        if not isinstance(source_rows, tuple):
            raise M0ServingError("candidate authority is unavailable")
        for source in source_rows:
            if not isinstance(source, Mapping):
                raise M0ServingError("candidate authority row is invalid")
            feature = source.get("feature_row")
            role = source.get("role_row")
            if not isinstance(feature, Mapping) or not isinstance(role, Mapping):
                raise M0ServingError("candidate evidence is incomplete")
            try:
                player_id = UUID(str(feature["player_id"]))
            except (KeyError, ValueError) as error:
                raise M0ServingError("candidate identity is invalid") from error
            if player_id in rows or role.get("player_id") != str(player_id):
                raise M0ServingError("candidate authority identities are invalid")
            rows[player_id] = source
        if not rows:
            raise M0ServingError("candidate authority has no rows")
        return rows

    def _validate_row_time(self, row: Mapping[str, Any], cutoff: datetime) -> None:
        feature = row["feature_row"]
        if not isinstance(feature, Mapping):
            raise M0ServingError("feature evidence is incomplete")
        if _as_utc(feature.get("feature_cutoff_ts"), "feature cutoff") != cutoff:
            raise M0ServingError("query evidence cutoff does not match the pinned request")
        if _as_utc(feature.get("observed_at"), "feature observed_at") >= cutoff:
            raise M0ServingError("post-cutoff feature evidence is forbidden")
        if _as_utc(feature.get("available_at"), "feature available_at") >= cutoff:
            raise M0ServingError("post-cutoff feature availability is forbidden")
        identity = feature.get("dependency_identity")
        if not isinstance(identity, Mapping) or not isinstance(identity.get("dependencies"), tuple):
            raise M0ServingError("dependency lineage is unavailable")
        for dependency in identity["dependencies"]:
            if not isinstance(dependency, Mapping):
                raise M0ServingError("dependency lineage is invalid")
            if _as_utc(dependency.get("observed_at"), "dependency observed_at") >= cutoff:
                raise M0ServingError("post-cutoff dependency observation is forbidden")
            if _as_utc(dependency.get("available_at"), "dependency available_at") >= cutoff:
                raise M0ServingError("post-cutoff dependency availability is forbidden")

    def _resolve_query(
        self,
        request: PinnedM0ServingRequest,
        rows: Mapping[UUID, Mapping[str, Any]],
    ) -> tuple[tuple[FeatureValue, ...], Mapping[str, float], M0ServingReason]:
        query = request.resolved_query
        has_player = query.query_player_id is not None
        has_exemplars = bool(query.exemplar_player_ids)
        if has_player == has_exemplars:
            raise M0ServingError("provide exactly one query player or exemplar set")
        excluded = set(request.retrieval_request.excluded_player_ids)
        if has_player:
            player_id = query.query_player_id
            if player_id is None:  # pragma: no cover - guarded by has_player
                raise M0ServingError("query player is unavailable")
            if player_id in excluded or player_id not in rows:
                raise M0ServingError("query player is excluded or unknown")
            row = rows[player_id]
            self._validate_row_time(row, query.feature_cutoff_ts)
            return (
                self._row_feature_values(row),
                self._role_memberships(row),
                M0ServingReason.QUERY_PLAYER_RESOLVED,
            )

        exemplar_ids = tuple(sorted(query.exemplar_player_ids, key=lambda item: item.bytes))
        if set(exemplar_ids) & excluded:
            raise M0ServingError("exemplar player is excluded")
        exemplar_rows: list[Mapping[str, Any]] = []
        for player_id in exemplar_ids:
            exemplar_row = rows.get(player_id)
            if exemplar_row is None:
                raise M0ServingError("exemplar player is unknown")
            self._validate_row_time(exemplar_row, query.feature_cutoff_ts)
            exemplar_rows.append(exemplar_row)
        vectors = tuple(self._row_feature_values(row) for row in exemplar_rows)
        if not vectors:
            raise M0ServingError("query has no admitted signal")
        if any(
            value.state not in {FeatureValueState.VALUE, FeatureValueState.ZERO}
            for vector in vectors
            for value in vector
        ):
            raise M0ServingError("exemplar query has incomplete feature evidence")
        averaged = tuple(
            self._mean_feature_value(tuple(vector[index] for vector in vectors))
            for index in range(len(vectors[0]))
        )
        role_names = tuple(sorted(self._role_memberships(exemplar_rows[0])))
        roles = {
            role: math.fsum(self._role_memberships(row)[role] for row in exemplar_rows)
            / len(exemplar_rows)
            for role in role_names
        }
        return averaged, roles, M0ServingReason.EXEMPLAR_QUERY_RESOLVED

    @staticmethod
    def _mean_feature_value(values: tuple[FeatureValue, ...]) -> FeatureValue:
        mean = math.fsum(float(value.numeric_value or 0.0) for value in values) / len(values)
        if mean == 0.0:
            return FeatureValue(state=FeatureValueState.ZERO, numeric_value=0.0)
        return FeatureValue(state=FeatureValueState.VALUE, numeric_value=mean)

    @staticmethod
    def _row_feature_values(row: Mapping[str, Any]) -> tuple[FeatureValue, ...]:
        feature = row["feature_row"]
        values = feature.get("expected_feature_values") if isinstance(feature, Mapping) else None
        if not isinstance(values, tuple) or not values:
            raise M0ServingError("feature values are unavailable")
        return tuple(_feature_value(value) for value in values)

    @staticmethod
    def _role_memberships(row: Mapping[str, Any]) -> Mapping[str, float]:
        role = row["role_row"]
        memberships = role.get("expected_role_probabilities") if isinstance(role, Mapping) else None
        if not isinstance(memberships, tuple):
            raise M0ServingError("role evidence is unavailable")
        result: dict[str, float] = {}
        for item in memberships:
            if not isinstance(item, Mapping) or not isinstance(item.get("role_code"), str):
                raise M0ServingError("role membership is invalid")
            probability = item.get("probability")
            if isinstance(probability, bool) or not isinstance(probability, (int, float)):
                raise M0ServingError("role membership is invalid")
            result[item["role_code"]] = float(probability)
        if not result or math.fsum(result.values()) != 1.0:
            raise M0ServingError("role membership evidence is incomplete")
        return result

    def _permitted_candidate_ids(
        self,
        request: PinnedM0ServingRequest,
        rows: Mapping[UUID, Mapping[str, Any]],
        query_roles: Mapping[str, float],
        constraints: tuple[_ConstraintPlan, ...],
    ) -> set[UUID]:
        taxonomy = getattr(self._taxonomy, "contract", self._taxonomy)
        taxonomy_roles = getattr(taxonomy, "roles", ())
        relevant_roles = {
            role.code
            for role in taxonomy_roles
            if any(
                code in request.resolved_query.responsibilities
                for code in role.responsibility_codes
            )
        }
        if not relevant_roles:
            raise M0ServingError("resolved responsibilities are absent from taxonomy")
        permitted: set[UUID] = set()
        for player_id, row in rows.items():
            self._validate_row_time(row, request.retrieval_request.feature_cutoff_ts)
            if not self._matches_constraints(row, constraints):
                continue
            memberships = self._role_memberships(row)
            if not any(memberships.get(role, 0.0) > 0.0 for role in relevant_roles):
                continue
            # The shared scorer remains authoritative for its selected role-aware
            # overlap threshold.  This only enforces the resolved taxonomy boundary.
            if not any(query_roles.get(role, 0.0) >= 0.0 for role in query_roles):
                raise M0ServingError("query role evidence is unavailable")
            permitted.add(player_id)
        return permitted

    @staticmethod
    def _constraint_plan(constraints: Iterable[Any]) -> tuple[_ConstraintPlan, ...]:
        """Validate all predicates before candidate scanning, then canonicalize execution order."""
        plan: list[_ConstraintPlan] = []
        for constraint in constraints:
            field = getattr(constraint, "field", None)
            operator_value = getattr(getattr(constraint, "operator", None), "value", None)
            raw = getattr(constraint, "value", None)
            if field not in _SUPPORTED_CONSTRAINT_FIELDS:
                raise M0ServingError("hard constraint field is unsupported")
            if not isinstance(operator_value, str) or not isinstance(raw, str):
                raise M0ServingError("hard constraint is invalid")
            if field == "synthetic_position_code":
                if operator_value not in {"equals", "not_equals", "in"}:
                    raise M0ServingError("position constraint operator is unsupported")
                if operator_value == "in":
                    members = tuple(sorted(set(raw.split(","))))
                    if not members or any(
                        not member or member != member.strip() for member in members
                    ):
                        raise M0ServingError("position IN constraint is invalid")
                    plan.append(_ConstraintPlan(field, operator_value, members))
                else:
                    if not raw or raw != raw.strip():
                        raise M0ServingError("position constraint value is invalid")
                    plan.append(_ConstraintPlan(field, operator_value, raw))
                continue
            if operator_value not in {"equals", "not_equals", "at_least", "at_most"}:
                raise M0ServingError("numeric constraint operator is unsupported")
            try:
                numeric = float(raw)
            except ValueError as error:
                raise M0ServingError("numeric constraint value is invalid") from error
            if not math.isfinite(numeric):
                raise M0ServingError("numeric constraint value is invalid")
            plan.append(_ConstraintPlan(field, operator_value, numeric))
        return tuple(sorted(plan, key=lambda item: (item.field, item.operator, repr(item.value))))

    @staticmethod
    def _matches_constraints(
        row: Mapping[str, Any], constraints: Iterable[_ConstraintPlan]
    ) -> bool:
        feature = row["feature_row"]
        if not isinstance(feature, Mapping):
            raise M0ServingError("candidate filter evidence is unavailable")
        for constraint in constraints:
            field = constraint.field
            value = feature.get(field)
            if value is None:
                raise M0ServingError("candidate filter evidence is unavailable")
            operator = constraint.operator
            raw = constraint.value
            if field == "synthetic_position_code":
                if operator == "equals":
                    accepted = value == raw
                elif operator == "not_equals":
                    accepted = value != raw
                else:
                    if not isinstance(raw, tuple):  # pragma: no cover - plan invariant
                        raise M0ServingError("position execution plan is invalid")
                    accepted = value in raw
            else:
                expected = raw
                if (
                    not isinstance(expected, float)
                    or isinstance(value, bool)
                    or not isinstance(value, (int, float))
                ):
                    raise M0ServingError("numeric filter evidence is unavailable")
                actual = float(value)
                accepted = {
                    "equals": actual == expected,
                    "not_equals": actual != expected,
                    "at_least": actual >= expected,
                    "at_most": actual <= expected,
                }[operator]
            if not accepted:
                return False
        return True

    def _temporal_evidence(
        self,
        request: PinnedM0ServingRequest,
        manifest: Any,
        rows: Mapping[UUID, Mapping[str, Any]],
    ) -> tuple[TemporalEvidence, DependencyLineage]:
        dependencies: list[EvidenceDependency] = []
        for player_id in sorted(rows, key=lambda item: item.bytes):
            feature = rows[player_id]["feature_row"]
            identity = feature["dependency_identity"]
            for raw in identity["dependencies"]:
                dependencies.append(
                    EvidenceDependency(
                        kind=DependencyKind.SOURCE_MANIFEST,
                        dependency_id=UUID(str(raw["dependency_id"])),
                        digest=str(raw["digest"]),
                        observed_at=_as_utc(raw["observed_at"], "dependency observed_at"),
                        available_at=_as_utc(raw["available_at"], "dependency available_at"),
                    )
                )
            row_lineage_digest = identity.get("lineage_hash")
            if not isinstance(row_lineage_digest, str):
                raise M0ServingError("feature-row lineage digest is unavailable")
            dependencies.append(
                EvidenceDependency(
                    kind=DependencyKind.FEATURE_SCHEMA,
                    dependency_id=uuid5(
                        _SERVING_NAMESPACE,
                        f"feature-schema|{player_id}|{row_lineage_digest}",
                    ),
                    digest=manifest.feature_schema_hash,
                    observed_at=_as_utc(feature.get("observed_at"), "feature observed_at"),
                    available_at=_as_utc(feature.get("available_at"), "feature available_at"),
                )
            )
        if not dependencies:
            raise M0ServingError("artifact lineage has no source dependencies")
        latest_observed = max(item.observed_at for item in dependencies)
        latest_available = max(item.available_at for item in dependencies)
        lineage_payload = [item.model_dump(mode="json") for item in dependencies]
        lineage = DependencyLineage(
            lineage_hash=_digest(lineage_payload), dependencies=tuple(dependencies)
        )
        generated = request.retrieval_request.requested_at
        temporal = TemporalEvidence(
            snapshot_as_of_ts=latest_observed,
            available_at_watermark=latest_available,
            valid_from_ts=max(latest_observed, latest_available),
            generated_at_ts=generated,
            feature_cutoff_ts=request.retrieval_request.feature_cutoff_ts,
            source_manifest_ids=tuple(
                item.dependency_id
                for item in dependencies
                if item.kind is DependencyKind.SOURCE_MANIFEST
            ),
            feature_schema_hash=manifest.feature_schema_hash,
            dependency_lineage_hash=lineage.lineage_hash,
            dependency_lineage=lineage,
        )
        return temporal, lineage

    def _result(self, context: _ResultContext) -> M0RetrievalResult:
        request = context.request
        manifest = context.manifest
        scored_rows = context.scored_rows
        rows = context.rows
        query_values = context.query_values
        query_roles = context.query_roles
        lineage = context.lineage
        temporal = context.temporal
        mode_reason = context.mode_reason
        constraints_applied = context.constraints_applied
        if len(query_values) != len(manifest.feature_names):
            raise M0ServingError("query feature order does not match the artifact")
        candidates: list[RetrievalCandidate] = []
        scored: list[M0ScoredCandidate] = []
        confidence_items: list[DataConfidenceEvidence] = []
        states: list[M0CandidateDimensionEvidence] = []
        explanations: list[M0CandidateExplanation] = []
        synthetic_limitations = (
            M0ServingReason.SYNTHETIC_DEVELOPMENT_ONLY.value,
            M0ServingReason.NO_RECOMMENDATION_EVIDENCE.value,
        )
        for rank, row in enumerate(scored_rows, 1):
            candidate_values = self._row_feature_values(rows[row.player_id])
            if len(candidate_values) != len(manifest.feature_names):
                raise M0ServingError("candidate feature order does not match the artifact")
            expected_feature_count = len(manifest.feature_names)
            observed_feature_count = sum(
                value.state in {FeatureValueState.VALUE, FeatureValueState.ZERO}
                for value in candidate_values
            )
            feature_coverage = observed_feature_count / expected_feature_count
            coverage = DataCoverage(
                overall=feature_coverage,
                dimensions=(
                    CoverageDimension(
                        name="feature_completeness",
                        coverage=feature_coverage,
                        observed_count=observed_feature_count,
                        expected_count=expected_feature_count,
                    ),
                    CoverageDimension(
                        name="role_completeness",
                        coverage=1.0,
                        observed_count=1,
                        expected_count=1,
                    ),
                    CoverageDimension(
                        name="temporal_lineage",
                        coverage=1.0,
                        observed_count=1,
                        expected_count=1,
                    ),
                ),
            )
            confidence = ConfidenceAssessment(
                score=feature_coverage,
                applicability=ApplicabilityState.LIMITED,
                limitations=synthetic_limitations,
            )
            candidate_roles = self._role_memberships(rows[row.player_id])
            role_score = math.fsum(
                min(query_roles.get(role, 0.0), candidate_roles.get(role, 0.0))
                for role in sorted(query_roles)
            )
            style_score = 1.0 / (1.0 + row.distance)
            style_reasons = _canonical_reasons(M0ServingReason.STYLE_DISTANCE_VIEW)
            confidence_reasons = _canonical_reasons(
                M0ServingReason.COVERAGE_COMPLETE,
                M0ServingReason.SYNTHETIC_DEVELOPMENT_ONLY,
                M0ServingReason.NO_RECOMMENDATION_EVIDENCE,
                M0ServingReason.APPLICABILITY_LIMITED,
            )
            unavailable = {
                EvidenceDimensionName.IMPACT: M0ServingReason.IMPACT_UNAVAILABLE,
                EvidenceDimensionName.TRAJECTORY: M0ServingReason.TRAJECTORY_UNAVAILABLE,
                EvidenceDimensionName.TRANSFER_RISK: M0ServingReason.TRANSFER_RISK_UNAVAILABLE,
            }
            role_absent = manifest.evidence_class is M0EvidenceClass.W04_REAL_GOVERNED
            role_state = (
                M0DimensionEvidenceState.UNAVAILABLE
                if role_absent
                else M0DimensionEvidenceState.ZERO
                if role_score == 0.0
                else M0DimensionEvidenceState.MEASURED
            )
            role_reasons = _canonical_reasons(
                M0ServingReason.W04_ROLE_UNAVAILABLE
                if role_absent
                else M0ServingReason.ROLE_COMPATIBILITY_ZERO
                if role_score == 0.0
                else M0ServingReason.ROLE_COMPATIBILITY_MEASURED
            )
            dimensions = (
                EvidenceDimension(
                    name=EvidenceDimensionName.STYLE_RESEMBLANCE,
                    score=style_score,
                    confidence=1.0,
                    reason_codes=style_reasons,
                ),
                EvidenceDimension(
                    name=EvidenceDimensionName.ROLE_COMPATIBILITY,
                    score=0.0 if role_absent else role_score,
                    confidence=0.0 if role_absent else 1.0,
                    reason_codes=role_reasons,
                ),
                *tuple(
                    EvidenceDimension(
                        name=name,
                        score=0.0,
                        confidence=0.0,
                        reason_codes=_canonical_reasons(reason),
                    )
                    for name, reason in unavailable.items()
                ),
                EvidenceDimension(
                    name=EvidenceDimensionName.DATA_CONFIDENCE,
                    score=confidence.score,
                    confidence=coverage.overall,
                    reason_codes=confidence_reasons,
                ),
            )
            candidate_reasons = _canonical_reasons(
                M0ServingReason.ARTIFACT_PINNED,
                M0ServingReason.TEMPORAL_LINEAGE_PINNED,
                mode_reason,
                M0ServingReason.ROLE_RESTRICTION_APPLIED,
                M0ServingReason.STYLE_DISTANCE_VIEW,
                *((M0ServingReason.HARD_CONSTRAINTS_APPLIED,) if constraints_applied else ()),
            )
            candidates.append(
                RetrievalCandidate(
                    player_id=row.player_id,
                    rank=rank,
                    evidence_dimensions=dimensions,
                    confidence=confidence,
                    coverage=coverage,
                    lineage=lineage,
                    reason_codes=candidate_reasons,
                )
            )
            scored.append(
                M0ScoredCandidate(
                    player_id=row.player_id,
                    rank=rank,
                    distance=row.distance,
                    query_feature_values=query_values,
                    candidate_feature_values=candidate_values,
                    contributions=tuple(_canonical_float(value) for value in row.contributions),
                )
            )
            confidence_items.append(
                DataConfidenceEvidence(
                    player_id=row.player_id,
                    score=confidence.score,
                    coverage=coverage,
                    applicability=confidence.applicability,
                    limitations=confidence.limitations,
                    reason_codes=_canonical_reasons(M0ServingReason.COVERAGE_COMPLETE),
                )
            )
            states.append(
                M0CandidateDimensionEvidence(
                    player_id=row.player_id,
                    rank=rank,
                    dimensions=(
                        M0DimensionEvidence(
                            name=EvidenceDimensionName.STYLE_RESEMBLANCE,
                            state=M0DimensionEvidenceState.MEASURED,
                            reason_codes=style_reasons,
                            contributes_to_ranking=True,
                        ),
                        M0DimensionEvidence(
                            name=EvidenceDimensionName.ROLE_COMPATIBILITY,
                            state=role_state,
                            reason_codes=role_reasons,
                            contributes_to_ranking=not role_absent,
                        ),
                        *tuple(
                            M0DimensionEvidence(
                                name=name,
                                state=M0DimensionEvidenceState.UNAVAILABLE,
                                reason_codes=_canonical_reasons(reason),
                                contributes_to_ranking=False,
                            )
                            for name, reason in unavailable.items()
                        ),
                        M0DimensionEvidence(
                            name=EvidenceDimensionName.DATA_CONFIDENCE,
                            state=M0DimensionEvidenceState.MEASURED,
                            reason_codes=confidence_reasons,
                            contributes_to_ranking=False,
                        ),
                    ),
                )
            )
            explanations.append(
                M0CandidateExplanation(
                    player_id=row.player_id,
                    rank=rank,
                    inputs=tuple(
                        M0ExplanationInput(
                            feature_name=feature_name,
                            query_value=query_value,
                            candidate_value=candidate_value,
                            contribution=_canonical_float(contribution),
                        )
                        for feature_name, query_value, candidate_value, contribution in zip(
                            manifest.feature_names,
                            query_values,
                            candidate_values,
                            row.contributions,
                            strict=True,
                        )
                    ),
                    reason_codes=_canonical_reasons(
                        mode_reason,
                        M0ServingReason.STYLE_DISTANCE_VIEW,
                        M0ServingReason.ROLE_RESTRICTION_APPLIED,
                    ),
                )
            )
        result = RetrievalResult(
            retrieval_result_id=_identifier(
                "retrieval-result",
                _request_digest(request),
                manifest.artifact_id,
                manifest.artifact_manifest_digest,
            ),
            retrieval_request_id=request.retrieval_request.retrieval_request_id,
            retrieval_run_id=_identifier(
                "retrieval-run",
                _request_digest(request),
                manifest.artifact_id,
                manifest.artifact_manifest_digest,
            ),
            tenant_context=request.retrieval_request.tenant_context,
            version=request.retrieval_request.version,
            trace_id=request.retrieval_request.trace_id,
            role_brief_id=request.retrieval_request.role_brief_id,
            role_brief_version=request.retrieval_request.role_brief_version,
            model_version=manifest.model_version,
            index_version=manifest.index_version,
            generated_at=temporal.generated_at_ts,
            temporal_evidence=temporal,
            candidates=tuple(candidates),
        )
        payload = {
            "schema_version": 1,
            "m0_result_id": str(
                _identifier(
                    "m0-result",
                    _request_digest(request),
                    manifest.artifact_id,
                    manifest.artifact_manifest_digest,
                )
            ),
            "retrieval_result": result.model_dump(mode="json"),
            "artifact_manifest": manifest.model_dump(mode="json"),
            "pinned_serving_request": request.model_dump(mode="json"),
            "scored_candidates": [item.model_dump(mode="json") for item in scored],
            "data_confidence_evidence": [item.model_dump(mode="json") for item in confidence_items],
            "dimension_evidence": [item.model_dump(mode="json") for item in states],
            "explanations": [item.model_dump(mode="json") for item in explanations],
        }
        return M0RetrievalResult(
            m0_result_id=_identifier(
                "m0-result",
                _request_digest(request),
                manifest.artifact_id,
                manifest.artifact_manifest_digest,
            ),
            retrieval_result=result,
            artifact_manifest=manifest,
            pinned_serving_request=request,
            scored_candidates=tuple(scored),
            data_confidence_evidence=tuple(confidence_items),
            dimension_evidence=tuple(states),
            explanations=tuple(explanations),
            result_digest=M0RetrievalResult.digest_for_payload(payload),
        )


def serve_m0_request(core: M0ServingCore, request: PinnedM0ServingRequest) -> M0RetrievalResult:
    """Thin single-request entry point sharing exactly the common core."""
    return core.serve(request)


def serve_m0_batch(
    core: M0ServingCore, requests: Iterable[PinnedM0ServingRequest]
) -> tuple[M0RetrievalResult, ...]:
    """Thin batch entry point; every item traverses the same core unchanged."""
    return tuple(core.serve(request) for request in requests)

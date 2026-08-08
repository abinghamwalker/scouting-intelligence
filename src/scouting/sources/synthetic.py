"""Deterministic, synthetic-only W03 fixture loading and temporal admission."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, Literal, cast
from uuid import UUID

from pydantic import ValidationError

from scouting.contracts import (
    DependencyKind,
    RetrievalRequest,
    RetrievalResult,
    RoleBrief,
    ShortlistEntry,
    SourceSnapshotManifest,
)

FIXTURE_SCHEMA_VERSION = 1
W03_SYNTHETIC_CLASSIFICATION = "w03_synthetic_generated"


class FixtureValidationError(ValueError):
    """Raised when a frozen fixture is malformed, mutable, or unsafe to admit."""


@dataclass(frozen=True, slots=True)
class SyntheticFact:
    """A temporally eligible synthetic observation admitted to the replay."""

    fact_id: UUID
    player_id: UUID
    metric: str
    value: float
    observed_at: datetime
    available_at: datetime
    expected_admission: bool
    arrival_class: Literal["on_time", "late"]


@dataclass(frozen=True, slots=True)
class RejectedFact:
    """A raw fact excluded from the replay with an explicit fail-closed reason."""

    fact_id: UUID
    reason: Literal[
        "missing_temporal_evidence",
        "post_cutoff_availability",
        "post_cutoff_observation",
    ]


@dataclass(frozen=True, slots=True)
class LoadedSyntheticFixture:
    """Validated W03 fixture and its contract-bound expected journey."""

    fixture_id: str
    partition: Literal["development", "protected_test"]
    manifest_digest: str
    expected_manifest_digest: str
    decision_cutoff_ts: datetime
    admitted_facts: tuple[SyntheticFact, ...]
    rejected_facts: tuple[RejectedFact, ...]
    ambiguous_source_ids: tuple[str, ...]
    role_brief: RoleBrief
    retrieval_request: RetrievalRequest
    retrieval_result: RetrievalResult
    shortlist_entry: ShortlistEntry
    source_manifest: SourceSnapshotManifest


def canonical_payload_digest(payload: Mapping[str, Any]) -> str:
    """Return the stable SHA-256 digest of a JSON-compatible payload."""
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(canonical).hexdigest()


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FixtureValidationError(f"unable to read fixture {path}: {exc}") from exc
    if not isinstance(decoded, dict):
        raise FixtureValidationError(f"fixture {path} must contain one JSON object")
    return decoded


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: set[str],
    *,
    context: str,
) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise FixtureValidationError(
            f"{context} keys must be exact; missing={missing}, unknown={unknown}"
        )


def _parse_uuid(value: object, *, context: str) -> UUID:
    if not isinstance(value, str):
        raise FixtureValidationError(f"{context} must be a UUID string")
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise FixtureValidationError(f"{context} must be a valid UUID") from exc
    if str(parsed) != value:
        raise FixtureValidationError(f"{context} must use canonical lowercase UUID form")
    return parsed


def _parse_utc(value: object, *, context: str) -> datetime:
    if not isinstance(value, str):
        raise FixtureValidationError(f"{context} must be an RFC 3339 UTC string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FixtureValidationError(f"{context} must be a valid RFC 3339 instant") from exc
    if parsed.utcoffset() != timedelta(0) or not value.endswith("Z"):
        raise FixtureValidationError(f"{context} must be expressed canonically in UTC with Z")
    return parsed


def _validated_envelope(
    path: Path,
    *,
    expected_partition: Literal["development", "protected_test"] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    document = _load_json_object(path)
    _require_exact_keys(document, {"manifest", "payload"}, context=str(path))
    manifest = document["manifest"]
    payload = document["payload"]
    if not isinstance(manifest, dict) or not isinstance(payload, dict):
        raise FixtureValidationError(f"{path} manifest and payload must be JSON objects")
    _require_exact_keys(
        manifest,
        {"schema_version", "fixture_id", "partition", "classification", "content_digest"},
        context=f"{path} manifest",
    )
    if manifest["schema_version"] != FIXTURE_SCHEMA_VERSION:
        raise FixtureValidationError(f"{path} has an unsupported fixture schema version")
    if manifest["classification"] != W03_SYNTHETIC_CLASSIFICATION:
        raise FixtureValidationError(f"{path} is not classified as W03 synthetic generated")
    if manifest["partition"] not in {"development", "protected_test"}:
        raise FixtureValidationError(f"{path} has an unknown fixture partition")
    if expected_partition is not None and manifest["partition"] != expected_partition:
        raise FixtureValidationError(
            f"{path} partition is {manifest['partition']}, expected {expected_partition}"
        )
    expected_digest = canonical_payload_digest(payload)
    if manifest["content_digest"] != expected_digest:
        raise FixtureValidationError(f"{path} content digest mismatch: expected {expected_digest}")
    return manifest, payload


def _require_non_empty_string(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FixtureValidationError(f"{context} must be a non-empty string")
    return value


def _validate_domain_collections(
    payload: Mapping[str, Any],
    *,
    context: str,
) -> set[UUID]:
    required = {
        "decision_cutoff_ts",
        "competitions",
        "teams",
        "players",
        "matches",
        "identity_records",
        "facts",
        "negative_cases",
    }
    _require_exact_keys(payload, required, context=context)

    collections = ("competitions", "teams", "players", "matches", "identity_records", "facts")
    for name in collections:
        if not isinstance(payload[name], list):
            raise FixtureValidationError(f"{context}.{name} must be a JSON array")
    if not isinstance(payload["negative_cases"], dict):
        raise FixtureValidationError(f"{context}.negative_cases must be a JSON object")
    if len(payload["competitions"]) != 2:
        raise FixtureValidationError(f"{context} must contain exactly two competitions")
    if len(payload["teams"]) < 4:
        raise FixtureValidationError(f"{context} must contain at least four teams")

    identifiers: dict[str, set[UUID]] = {}
    item_keys = {
        "competitions": {"id", "name"},
        "teams": {"id", "competition_id", "name"},
        "players": {"id", "team_id", "display_name", "position"},
        "matches": {
            "id",
            "competition_id",
            "home_team_id",
            "away_team_id",
            "started_at",
        },
    }
    for collection_name in ("competitions", "teams", "players", "matches"):
        seen: set[UUID] = set()
        for index, item in enumerate(payload[collection_name]):
            if not isinstance(item, dict):
                raise FixtureValidationError(
                    f"{context}.{collection_name}[{index}] must be a JSON object"
                )
            item_context = f"{context}.{collection_name}[{index}]"
            _require_exact_keys(item, item_keys[collection_name], context=item_context)
            entity_id = _parse_uuid(
                item.get("id"),
                context=f"{item_context}.id",
            )
            if entity_id in seen:
                raise FixtureValidationError(
                    f"{context}.{collection_name} contains duplicate id {entity_id}"
                )
            seen.add(entity_id)
        identifiers[collection_name] = seen

    competition_ids = identifiers["competitions"]
    team_ids = identifiers["teams"]
    player_ids = identifiers["players"]
    team_competitions: dict[UUID, UUID] = {}
    competitions = cast(list[dict[str, Any]], payload["competitions"])
    teams = cast(list[dict[str, Any]], payload["teams"])
    players = cast(list[dict[str, Any]], payload["players"])
    matches = cast(list[dict[str, Any]], payload["matches"])
    for index, competition in enumerate(competitions):
        _require_non_empty_string(
            competition["name"],
            context=f"{context}.competitions[{index}].name",
        )
    for index, team in enumerate(teams):
        competition_id = _parse_uuid(
            team["competition_id"],
            context=f"{context}.teams[{index}].competition_id",
        )
        if competition_id not in competition_ids:
            raise FixtureValidationError(f"{context}.teams[{index}] has unknown competition")
        team_id = _parse_uuid(team["id"], context=f"{context}.teams[{index}].id")
        team_competitions[team_id] = competition_id
        _require_non_empty_string(team["name"], context=f"{context}.teams[{index}].name")
    for index, player in enumerate(players):
        team_id = _parse_uuid(
            player["team_id"],
            context=f"{context}.players[{index}].team_id",
        )
        if team_id not in team_ids:
            raise FixtureValidationError(f"{context}.players[{index}] has unknown team")
        _require_non_empty_string(
            player["display_name"],
            context=f"{context}.players[{index}].display_name",
        )
        _require_non_empty_string(
            player["position"],
            context=f"{context}.players[{index}].position",
        )
    for index, match in enumerate(matches):
        item_context = f"{context}.matches[{index}]"
        competition_id = _parse_uuid(
            match["competition_id"],
            context=f"{item_context}.competition_id",
        )
        home_team_id = _parse_uuid(
            match["home_team_id"],
            context=f"{item_context}.home_team_id",
        )
        away_team_id = _parse_uuid(
            match["away_team_id"],
            context=f"{item_context}.away_team_id",
        )
        if home_team_id == away_team_id:
            raise FixtureValidationError(f"{item_context} cannot match a team against itself")
        if (
            home_team_id not in team_ids
            or away_team_id not in team_ids
            or competition_id not in competition_ids
        ):
            raise FixtureValidationError(f"{item_context} has an unknown domain reference")
        if (
            team_competitions[home_team_id] != competition_id
            or team_competitions[away_team_id] != competition_id
        ):
            raise FixtureValidationError(f"{item_context} teams must belong to its competition")
        _parse_utc(match["started_at"], context=f"{item_context}.started_at")

    negative_cases = cast(dict[str, Any], payload["negative_cases"])
    _require_exact_keys(
        negative_cases,
        {
            "attempted_storage_path",
            "authorised_actor",
            "unauthorised_actor",
            "cross_tenant_actor",
            "confidential_evidence",
            "attempted_actions",
        },
        context=f"{context}.negative_cases",
    )
    escape = _require_non_empty_string(
        negative_cases["attempted_storage_path"],
        context=f"{context}.negative_cases.attempted_storage_path",
    )
    if ".." not in Path(escape).parts:
        raise FixtureValidationError(f"{context} must contain an attempted storage path escape")

    actor_keys = {"actor_id", "tenant_id", "role"}
    actors: dict[str, tuple[UUID, str]] = {}
    for actor_name in ("authorised_actor", "unauthorised_actor", "cross_tenant_actor"):
        actor = negative_cases[actor_name]
        if not isinstance(actor, dict):
            raise FixtureValidationError(f"{context}.negative_cases.{actor_name} must be an object")
        _require_exact_keys(
            actor,
            actor_keys,
            context=f"{context}.negative_cases.{actor_name}",
        )
        _parse_uuid(
            actor["actor_id"],
            context=f"{context}.negative_cases.{actor_name}.actor_id",
        )
        actors[actor_name] = (
            _parse_uuid(
                actor["tenant_id"],
                context=f"{context}.negative_cases.{actor_name}.tenant_id",
            ),
            _require_non_empty_string(
                actor["role"],
                context=f"{context}.negative_cases.{actor_name}.role",
            ),
        )
    if actors["authorised_actor"][0] != actors["unauthorised_actor"][0]:
        raise FixtureValidationError(
            f"{context} unauthorised actor must exercise same-tenant denial"
        )
    if actors["authorised_actor"][0] == actors["cross_tenant_actor"][0]:
        raise FixtureValidationError(f"{context} cross-tenant actor must use another tenant")
    if actors["unauthorised_actor"][1] != "unknown":
        raise FixtureValidationError(f"{context} unknown actor role must exercise default deny")

    confidential = negative_cases["confidential_evidence"]
    if not isinstance(confidential, dict):
        raise FixtureValidationError(f"{context}.negative_cases.confidential_evidence is invalid")
    _require_exact_keys(
        confidential,
        {"evidence_id", "tenant_id", "classification", "exportable"},
        context=f"{context}.negative_cases.confidential_evidence",
    )
    _parse_uuid(
        confidential["evidence_id"],
        context=f"{context}.negative_cases.confidential_evidence.evidence_id",
    )
    confidential_tenant = _parse_uuid(
        confidential["tenant_id"],
        context=f"{context}.negative_cases.confidential_evidence.tenant_id",
    )
    if confidential_tenant != actors["authorised_actor"][0]:
        raise FixtureValidationError(f"{context} confidential evidence tenant is inconsistent")
    if (
        confidential["classification"] != "synthetic_confidential"
        or confidential["exportable"] is not False
    ):
        raise FixtureValidationError(f"{context} confidential fixture must be non-exportable")
    attempted_actions = negative_cases["attempted_actions"]
    if not isinstance(attempted_actions, list) or set(attempted_actions) != {
        "confidential_evidence.read_unauthorised",
        "confidential_evidence.export_unauthorised",
        "audit_event.update",
        "audit_event.delete",
    }:
        raise FixtureValidationError(f"{context} must contain all required security attempts")
    return player_ids


def _parse_facts(
    raw_facts: list[object],
    *,
    cutoff: datetime,
    context: str,
) -> tuple[tuple[SyntheticFact, ...], tuple[RejectedFact, ...]]:
    admitted: list[SyntheticFact] = []
    rejected: list[RejectedFact] = []
    seen: set[UUID] = set()
    exact_keys = {
        "fact_id",
        "player_id",
        "metric",
        "value",
        "observed_at",
        "available_at",
        "expected_admission",
        "arrival_class",
    }

    for index, raw in enumerate(raw_facts):
        item_context = f"{context}.facts[{index}]"
        if not isinstance(raw, dict):
            raise FixtureValidationError(f"{item_context} must be a JSON object")
        _require_exact_keys(raw, exact_keys, context=item_context)
        fact_id = _parse_uuid(raw["fact_id"], context=f"{item_context}.fact_id")
        if fact_id in seen:
            raise FixtureValidationError(f"{context} contains duplicate fact id {fact_id}")
        seen.add(fact_id)
        player_id = _parse_uuid(raw["player_id"], context=f"{item_context}.player_id")
        observed_at = _parse_utc(raw["observed_at"], context=f"{item_context}.observed_at")
        expected_admission = raw["expected_admission"]
        if not isinstance(expected_admission, bool):
            raise FixtureValidationError(f"{item_context}.expected_admission must be boolean")
        arrival_class = raw["arrival_class"]
        if arrival_class not in {"on_time", "late"}:
            raise FixtureValidationError(f"{item_context}.arrival_class is unsupported")

        if observed_at >= cutoff:
            if expected_admission:
                raise FixtureValidationError(
                    f"{item_context} cannot expect admission for an observation "
                    "at or after the cutoff"
                )
            rejected.append(RejectedFact(fact_id, "post_cutoff_observation"))
            continue

        available_value = raw["available_at"]
        if available_value is None:
            if expected_admission:
                raise FixtureValidationError(
                    f"{item_context} cannot expect admission without available_at"
                )
            rejected.append(RejectedFact(fact_id, "missing_temporal_evidence"))
            continue

        available_at = _parse_utc(
            available_value,
            context=f"{item_context}.available_at",
        )
        if available_at >= cutoff:
            if expected_admission:
                raise FixtureValidationError(
                    f"{item_context} cannot expect admission at or after the cutoff"
                )
            rejected.append(RejectedFact(fact_id, "post_cutoff_availability"))
            continue
        if not expected_admission:
            raise FixtureValidationError(
                f"{item_context} rejects a temporally eligible fact without a supported reason"
            )
        if not isinstance(raw["metric"], str) or not raw["metric"].strip():
            raise FixtureValidationError(f"{item_context}.metric must be non-empty")
        if isinstance(raw["value"], bool) or not isinstance(raw["value"], (int, float)):
            raise FixtureValidationError(f"{item_context}.value must be numeric")
        if arrival_class == "late" and available_at <= observed_at:
            raise FixtureValidationError(
                f"{item_context} late fact must become available after it was observed"
            )

        admitted.append(
            SyntheticFact(
                fact_id=fact_id,
                player_id=player_id,
                metric=raw["metric"],
                value=float(raw["value"]),
                observed_at=observed_at,
                available_at=available_at,
                expected_admission=expected_admission,
                arrival_class=arrival_class,
            )
        )

    admitted.sort(key=lambda fact: (fact.available_at, str(fact.fact_id)))
    rejected.sort(key=lambda fact: str(fact.fact_id))
    return tuple(admitted), tuple(rejected)


def _ambiguous_source_ids(
    raw_identities: list[object],
    *,
    player_ids: set[UUID],
    context: str,
) -> tuple[str, ...]:
    ambiguous: list[str] = []
    for index, raw in enumerate(raw_identities):
        item_context = f"{context}.identity_records[{index}]"
        if not isinstance(raw, dict):
            raise FixtureValidationError(f"{item_context} must be a JSON object")
        _require_exact_keys(
            raw,
            {
                "provider",
                "source_id",
                "source_version",
                "resolution_status",
                "canonical_player_id",
                "candidate_player_ids",
            },
            context=item_context,
        )
        _require_non_empty_string(raw["provider"], context=f"{item_context}.provider")
        _require_non_empty_string(raw["source_version"], context=f"{item_context}.source_version")
        source_id = raw.get("source_id")
        status = raw.get("resolution_status")
        if not isinstance(source_id, str) or not source_id:
            raise FixtureValidationError(f"{item_context}.source_id must be non-empty")
        if status not in {"resolved", "review_required"}:
            raise FixtureValidationError(f"{item_context}.resolution_status is unsupported")
        if status == "review_required":
            if raw.get("canonical_player_id") is not None:
                raise FixtureValidationError(
                    f"{item_context} ambiguous identity cannot guess a canonical player"
                )
            candidates = raw.get("candidate_player_ids")
            if not isinstance(candidates, list) or len(candidates) < 2:
                raise FixtureValidationError(
                    f"{item_context} ambiguous identity needs at least two candidates"
                )
            parsed_candidates = {
                _parse_uuid(
                    candidate,
                    context=f"{item_context}.candidate_player_ids[{candidate_index}]",
                )
                for candidate_index, candidate in enumerate(candidates)
            }
            if len(parsed_candidates) != len(candidates) or not parsed_candidates <= player_ids:
                raise FixtureValidationError(
                    f"{item_context} ambiguity candidates must be distinct domain players"
                )
            ambiguous.append(source_id)
        else:
            canonical_player_id = _parse_uuid(
                raw["canonical_player_id"],
                context=f"{item_context}.canonical_player_id",
            )
            if canonical_player_id not in player_ids:
                raise FixtureValidationError(
                    f"{item_context} resolved identity must reference a domain player"
                )
            if raw["candidate_player_ids"] != []:
                raise FixtureValidationError(
                    f"{item_context} resolved identity cannot retain ambiguity candidates"
                )
    if len(ambiguous) != 1:
        raise FixtureValidationError(f"{context} must retain exactly one ambiguous identity")
    return tuple(sorted(ambiguous))


def _validate_expected_payload(
    payload: Mapping[str, Any],
    *,
    domain_digest: str,
    domain_size_bytes: int,
    domain_fact_count: int,
    domain_player_ids: set[UUID],
    cutoff: datetime,
    context: str,
) -> tuple[
    SourceSnapshotManifest,
    RoleBrief,
    RetrievalRequest,
    RetrievalResult,
    ShortlistEntry,
]:
    _require_exact_keys(
        payload,
        {
            "source_manifest",
            "role_brief",
            "retrieval_request",
            "retrieval_result",
            "explanations",
            "shortlist_entry",
            "expected_audit_actions",
        },
        context=context,
    )
    try:
        source_manifest = SourceSnapshotManifest.model_validate_json(
            json.dumps(payload["source_manifest"])
        )
        role_brief = RoleBrief.model_validate_json(json.dumps(payload["role_brief"]))
        request = RetrievalRequest.model_validate_json(json.dumps(payload["retrieval_request"]))
        result = RetrievalResult.model_validate_json(json.dumps(payload["retrieval_result"]))
        shortlist_entry = ShortlistEntry.model_validate_json(json.dumps(payload["shortlist_entry"]))
    except ValidationError as exc:
        raise FixtureValidationError(f"{context} violates W03 contracts: {exc}") from exc

    source_files = source_manifest.files
    if len(source_files) != 1 or source_files[0].sha256 != domain_digest:
        raise FixtureValidationError(f"{context} source manifest must bind the domain digest")
    source_object_path = PurePosixPath(source_files[0].object_path)
    if (
        source_object_path.is_absolute()
        or ".." in source_object_path.parts
        or source_object_path.parts[:3] != ("tests", "fixtures", "synthetic")
    ):
        raise FixtureValidationError(f"{context} source manifest object path is outside fixtures")
    if (
        source_files[0].size_bytes != domain_size_bytes
        or source_files[0].row_count != domain_fact_count
    ):
        raise FixtureValidationError(f"{context} source manifest size or row count is stale")
    if (
        source_manifest.classification.export_allowed
        or not source_manifest.classification.internal_review_allowed
    ):
        raise FixtureValidationError(f"{context} source manifest violates local-only data rights")
    if request.feature_cutoff_ts != cutoff:
        raise FixtureValidationError(f"{context} request cutoff differs from domain cutoff")
    if result.temporal_evidence.feature_cutoff_ts != cutoff:
        raise FixtureValidationError(f"{context} result cutoff differs from domain cutoff")
    if request.role_brief_id != role_brief.role_brief_id:
        raise FixtureValidationError(f"{context} request does not bind the role brief")
    if request.role_brief_version != role_brief.version:
        raise FixtureValidationError(f"{context} request does not bind the role brief version")
    if result.retrieval_request_id != request.retrieval_request_id:
        raise FixtureValidationError(f"{context} result does not bind the request")
    if (
        result.role_brief_id != role_brief.role_brief_id
        or result.role_brief_version != role_brief.version
    ):
        raise FixtureValidationError(f"{context} result does not bind the role brief version")
    tenant_contexts = {
        source_manifest.tenant_context,
        role_brief.tenant_context,
        request.tenant_context,
        result.tenant_context,
        shortlist_entry.tenant_context,
    }
    if len(tenant_contexts) != 1:
        raise FixtureValidationError(f"{context} expected journey crosses tenant ownership")
    trace_ids = {
        source_manifest.trace_id,
        role_brief.trace_id,
        request.trace_id,
        result.trace_id,
        shortlist_entry.trace_id,
    }
    if len(trace_ids) != 1:
        raise FixtureValidationError(f"{context} expected journey has inconsistent trace IDs")

    lineage = result.temporal_evidence.dependency_lineage
    computed_lineage_hash = canonical_payload_digest(
        {
            "dependencies": [
                dependency.model_dump(mode="json") for dependency in lineage.dependencies
            ]
        }
    )
    if lineage.lineage_hash != computed_lineage_hash:
        raise FixtureValidationError(f"{context} lineage hash is not canonical")
    source_dependencies = [
        dependency
        for dependency in lineage.dependencies
        if dependency.kind is DependencyKind.SOURCE_MANIFEST
    ]
    if (
        len(source_dependencies) != 1
        or source_dependencies[0].dependency_id != source_manifest.manifest_id
        or source_dependencies[0].digest != domain_digest
    ):
        raise FixtureValidationError(f"{context} lineage must bind the exact source manifest")
    feature_dependencies = [
        dependency
        for dependency in lineage.dependencies
        if dependency.kind is DependencyKind.FEATURE_SCHEMA
    ]
    if (
        len(feature_dependencies) != 1
        or feature_dependencies[0].digest != result.temporal_evidence.feature_schema_hash
    ):
        raise FixtureValidationError(f"{context} lineage must bind the feature schema")
    for required_kind in (DependencyKind.MODEL_ARTIFACT, DependencyKind.RETRIEVAL_INDEX):
        if sum(dependency.kind is required_kind for dependency in lineage.dependencies) != 1:
            raise FixtureValidationError(
                f"{context} lineage must bind exactly one {required_kind.value}"
            )
    candidate_ids = {candidate.player_id for candidate in result.candidates}
    if not candidate_ids or not candidate_ids <= domain_player_ids:
        raise FixtureValidationError(f"{context} candidates must be domain players")
    if shortlist_entry.player_id not in candidate_ids:
        raise FixtureValidationError(f"{context} shortlist target must be a returned candidate")
    if shortlist_entry.retrieval_run_id != result.retrieval_run_id:
        raise FixtureValidationError(f"{context} shortlist must retain retrieval provenance")
    if shortlist_entry.rank_at_addition != next(
        candidate.rank
        for candidate in result.candidates
        if candidate.player_id == shortlist_entry.player_id
    ):
        raise FixtureValidationError(f"{context} shortlist rank does not match the result")
    if shortlist_entry.model_version_at_addition != result.model_version:
        raise FixtureValidationError(f"{context} shortlist model version does not match the result")

    explanations = payload["explanations"]
    if not isinstance(explanations, list) or len(explanations) != len(result.candidates):
        raise FixtureValidationError(f"{context} must explain every returned candidate")
    explained_ids: set[UUID] = set()
    for index, explanation in enumerate(explanations):
        if not isinstance(explanation, dict):
            raise FixtureValidationError(f"{context}.explanations[{index}] must be an object")
        _require_exact_keys(
            explanation,
            {"player_id", "claim_boundary", "reason_codes", "summary"},
            context=f"{context}.explanations[{index}]",
        )
        explained_ids.add(
            _parse_uuid(
                explanation["player_id"],
                context=f"{context}.explanations[{index}].player_id",
            )
        )
        if explanation["claim_boundary"] != "resemblance_only":
            raise FixtureValidationError(f"{context} explanation exceeds the claim boundary")
        if not isinstance(explanation["summary"], str) or not explanation["summary"].strip():
            raise FixtureValidationError(f"{context} explanation summary must be non-empty")
        if not isinstance(explanation["reason_codes"], list) or not explanation["reason_codes"]:
            raise FixtureValidationError(f"{context} explanation reason_codes must be non-empty")
    if explained_ids != candidate_ids:
        raise FixtureValidationError(f"{context} explanation identities must match candidates")

    audit_actions = payload["expected_audit_actions"]
    if not isinstance(audit_actions, list) or audit_actions != [
        "role_brief.approved",
        "retrieval.executed",
        "evidence.viewed",
        "shortlist.entry_created",
    ]:
        raise FixtureValidationError(f"{context} has an unexpected audit sequence")
    return source_manifest, role_brief, request, result, shortlist_entry


def load_synthetic_fixture(
    domain_path: Path,
    expected_path: Path,
    *,
    expected_partition: Literal["development", "protected_test"] | None = None,
) -> LoadedSyntheticFixture:
    """Validate and load one frozen domain/expected pair without admitting future facts."""
    domain_manifest, domain_payload = _validated_envelope(
        domain_path,
        expected_partition=expected_partition,
    )
    expected_manifest, expected_payload = _validated_envelope(
        expected_path,
        expected_partition=expected_partition,
    )
    if domain_manifest["fixture_id"] != expected_manifest["fixture_id"]:
        raise FixtureValidationError("domain and expected fixtures have different fixture IDs")
    if domain_manifest["partition"] != expected_manifest["partition"]:
        raise FixtureValidationError("domain and expected fixtures have different partitions")

    context = str(domain_path)
    player_ids = _validate_domain_collections(domain_payload, context=context)
    cutoff = _parse_utc(
        domain_payload["decision_cutoff_ts"],
        context=f"{context}.decision_cutoff_ts",
    )
    facts_raw = cast(list[object], domain_payload["facts"])
    identities_raw = cast(list[object], domain_payload["identity_records"])
    for index, raw_fact in enumerate(facts_raw):
        if not isinstance(raw_fact, dict):
            raise FixtureValidationError(f"{context}.facts[{index}] must be a JSON object")
        if (
            _parse_uuid(
                raw_fact.get("player_id"),
                context=f"{context}.facts[{index}].player_id",
            )
            not in player_ids
        ):
            raise FixtureValidationError(f"{context}.facts[{index}] has an unknown player")
    admitted, rejected = _parse_facts(facts_raw, cutoff=cutoff, context=context)
    ambiguous_ids = _ambiguous_source_ids(
        identities_raw,
        player_ids=player_ids,
        context=context,
    )
    source_manifest, role_brief, request, result, shortlist_entry = _validate_expected_payload(
        expected_payload,
        domain_digest=domain_manifest["content_digest"],
        domain_size_bytes=domain_path.stat().st_size,
        domain_fact_count=len(facts_raw),
        domain_player_ids=player_ids,
        cutoff=cutoff,
        context=str(expected_path),
    )
    return LoadedSyntheticFixture(
        fixture_id=domain_manifest["fixture_id"],
        partition=domain_manifest["partition"],
        manifest_digest=domain_manifest["content_digest"],
        expected_manifest_digest=expected_manifest["content_digest"],
        decision_cutoff_ts=cutoff,
        admitted_facts=admitted,
        rejected_facts=rejected,
        ambiguous_source_ids=ambiguous_ids,
        role_brief=role_brief,
        retrieval_request=request,
        retrieval_result=result,
        shortlist_entry=shortlist_entry,
        source_manifest=source_manifest,
    )

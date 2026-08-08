"""Fail-closed typed authorities and the single M0 artifact scorer."""

from __future__ import annotations

import hashlib
import json
import math
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast
from uuid import UUID, uuid5

import numpy as np

from scouting.contracts.m0 import (
    FootballResponsibilityTaxonomy,
    M0ArrayDtype,
    M0ArraySemanticRole,
    M0ArtifactManifest,
    M0Endianness,
    M0MemoryOrder,
    M0ModelFamily,
)
from scouting.features.registry import FeatureRegistry, materialize_synthetic_row
from scouting.features.registry import canonical_json_bytes as registry_canonical_json_bytes
from scouting.roles.taxonomy import RoleTaxonomy, contextual_role_membership
from scouting.storage.formats import canonical_json_bytes

from .scoring import VectorCandidateKey, VectorScoringMethod, score_vector_rows


class M0RuntimeError(ValueError):
    """Raised when a development authority or artifact is unsafe or substituted."""


_ARTIFACT_FILES = ("arrays.npz", "manifest.json", "configuration.json", "candidate-universe.json")
_NAMESPACE = UUID("8a65a0f1-c48a-5ad2-a5e2-4271f68e0bce")
_ACCEPTED_TAXONOMY = (
    "w05-football-responsibility-taxonomy-v1",
    "v1",
    "59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097",
)
_CANDIDATE_FIXTURE = (
    "w05-m0-development-candidates-v1",
    "v1",
    "710c38554f33f8f650d814df1fee3c8bac7a8a2bc22804f93e3b9a8dfd1e50d9",
)
_QUERY_FIXTURE = (
    "w05-m0-development-queries-v1",
    "v1",
    "fb027563b3f99f563d43f1b909c535f860f3d04d2d8aa0ed44e902fd2a37e900",
)
_ACCEPTED_CONFIGURATION = (
    "w05-m0-baselines-v1",
    "v1",
    "5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a",
)
_FAMILY_DIGESTS = {
    "metadata_control": "19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee",
    "raw_euclidean_control": "3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36",
    "robust_scaled_cosine": "ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc",
    "weighted_cosine": "c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801",
    "pca": "90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971",
    "role_aware_restriction": "c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801",
}
_ACCEPTED_CONFIGURATION_MAPPING = {
    "candidate_fixture_digest": _CANDIDATE_FIXTURE[2],
    "candidate_fixture_id": _CANDIDATE_FIXTURE[0],
    "candidate_population_projection_digest": (
        "60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086"
    ),
    "comparison_k": 3,
    "configuration_digest": _ACCEPTED_CONFIGURATION[2],
    "configuration_id": _ACCEPTED_CONFIGURATION[0],
    "configuration_version": _ACCEPTED_CONFIGURATION[1],
    "deterministic_seed": 20260803,
    "expected_array_payload_digests": _FAMILY_DIGESTS,
    "pca_component_count": 3,
    "query_fixture_digest": _QUERY_FIXTURE[2],
    "query_fixture_id": _QUERY_FIXTURE[0],
    "query_population_projection_digest": (
        "1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c"
    ),
    "role_aware_minimum_overlap": 0.75,
    "selected_model_family": M0ModelFamily.ROLE_AWARE_RESTRICTION.value,
    "weighted_cosine_weights": (2.0, 2.0, 2.0, 2.0, 1.0, 0.1),
}
_CANDIDATE_AUTHORITY_DIGEST = "863d54904bffe072bfc230c62d7ca0c80a58026f8bde9c52e727f06dd563979c"
_QUERY_AUTHORITY_DIGEST = "1671c5da518476fd16a5c2eef975359a46416a0f265daa030df32edfb6d10a3d"
_REGISTRY_SEMANTIC_DIGEST = "c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644"
_CONFIG_KEYS = frozenset(
    {
        "candidate_fixture_digest",
        "candidate_fixture_id",
        "candidate_fixture_id",
        "candidate_population_projection_digest",
        "comparison_k",
        "configuration_digest",
        "configuration_id",
        "configuration_version",
        "deterministic_seed",
        "expected_array_payload_digests",
        "pca_component_count",
        "query_fixture_digest",
        "query_fixture_id",
        "query_population_projection_digest",
        "role_aware_minimum_overlap",
        "selected_model_family",
        "weighted_cosine_weights",
    }
)
_CANDIDATE_ROOT_KEYS = frozenset(
    {
        "candidates",
        "archetype_notice",
        "candidate_fixture_id",
        "candidate_fixture_version",
        "claim",
        "context_id",
        "development_only",
        "evidence_class",
        "external_expert_label",
        "family_digest",
        "family_id",
        "feature_cutoff_ts",
        "feature_schema_hash",
        "fixture_digest",
        "fixture_id",
        "fixture_version",
        "nuisance_notice",
        "production_claim",
        "protected",
        "provider_source",
        "recruitment_outcome",
        "registry_digest",
        "registry_id",
        "synthetic_development",
        "taxonomy_digest",
        "taxonomy_id",
        "taxonomy_version",
    }
)
_QUERY_ROOT_KEYS = frozenset(
    {
        "candidate_fixture_digest",
        "candidate_fixture_id",
        "claim",
        "development_only",
        "evidence_class",
        "external_expert_label",
        "feature_cutoff_ts",
        "fixture_digest",
        "fixture_id",
        "fixture_version",
        "production_claim",
        "protected",
        "provider_source",
        "queries",
        "query_fixture_id",
        "query_fixture_version",
        "recruitment_outcome",
    }
)
_FEATURE_ROW_KEYS = frozenset(
    {
        "available_at",
        "constructed_development_peer_group",
        "dependency_identity",
        "expected_feature_values",
        "feature_cutoff_ts",
        "observed_at",
        "player_id",
        "raw_numerator_inputs",
        "state_overrides",
        "synthetic_age_years",
        "synthetic_elapsed_minutes",
        "synthetic_position_code",
    }
)
_ROLE_ROW_KEYS = frozenset(
    {
        "context_id",
        "expected_role_probabilities",
        "player_id",
        "responsibility_evidence",
        "source_label_prior",
    }
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise M0RuntimeError("JSON contains duplicate object keys")
        result[key] = value
    return result


def _bad_constant(_: str) -> Any:
    raise M0RuntimeError("JSON non-finite constants are forbidden")


def _read_canonical_json(path: Path) -> dict[str, Any]:
    try:
        payload = path.read_bytes()
        parsed = json.loads(payload, object_pairs_hook=_json_pairs, parse_constant=_bad_constant)
    except (OSError, json.JSONDecodeError, M0RuntimeError) as error:
        raise M0RuntimeError(f"cannot load canonical JSON {path.name}") from error
    if not isinstance(parsed, dict) or canonical_json_bytes(parsed) != payload:
        raise M0RuntimeError(f"{path.name} is not exact canonical JSON")
    return parsed


def _exact_keys(value: object, keys: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise M0RuntimeError(f"{label} keys are not exact")
    return value


def _sha(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(item not in "0123456789abcdef" for item in value)
    ):
        raise M0RuntimeError(f"{label} must be a lowercase SHA-256")
    return value


def _strict_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise M0RuntimeError(f"{label} must be a finite JSON number")
    return float(value)


def _validated_taxonomy(
    taxonomy: RoleTaxonomy | FootballResponsibilityTaxonomy,
) -> FootballResponsibilityTaxonomy:
    contract = taxonomy.contract if isinstance(taxonomy, RoleTaxonomy) else taxonomy
    if not isinstance(contract, FootballResponsibilityTaxonomy):
        raise M0RuntimeError("a validated FootballResponsibilityTaxonomy is required")
    try:
        validated = FootballResponsibilityTaxonomy.model_validate(
            contract.model_dump(mode="python")
        )
    except ValueError as error:
        raise M0RuntimeError("taxonomy public revalidation failed") from error
    if (
        validated.taxonomy_id,
        validated.taxonomy_version,
        validated.taxonomy_digest,
    ) != _ACCEPTED_TAXONOMY:
        raise M0RuntimeError("taxonomy is not the accepted W05 authority")
    if isinstance(taxonomy, RoleTaxonomy) and (
        taxonomy.canonical_order != "responsibility_code_role_code_source_label"
        or taxonomy.expert_validation_status != "NOT_PERFORMED"
        or taxonomy.external_expert_evidence != ()
        or taxonomy.claim != "synthetic_development_taxonomy_only"
        or taxonomy.exemplar_notice
        != "Exemplars may be an additional retrieval query signal but never replace the "
        "falsifiable responsibility taxonomy."
    ):
        raise M0RuntimeError("taxonomy wrapper claim authority drift")
    return validated


@dataclass(frozen=True, slots=True)
class M0Configuration:
    """The sole accepted, immutable configuration authority."""

    configuration_id: str
    configuration_version: str
    configuration_digest: str
    deterministic_seed: int
    weighted_cosine_weights: tuple[float, float, float, float, float, float]
    pca_component_count: int
    role_aware_minimum_overlap: float
    selected_model_family: M0ModelFamily
    comparison_k: int
    candidate_fixture_id: str
    candidate_fixture_digest: str
    candidate_population_projection_digest: str
    query_fixture_id: str
    query_fixture_digest: str
    query_population_projection_digest: str
    expected_array_payload_digests: Mapping[str, str]

    def canonical_mapping(self) -> Mapping[str, Any]:
        """Return the immutable canonical payload for internal artifact serialization."""
        return MappingProxyType(
            {
                "configuration_id": self.configuration_id,
                "configuration_version": self.configuration_version,
                "configuration_digest": self.configuration_digest,
                "deterministic_seed": self.deterministic_seed,
                "weighted_cosine_weights": self.weighted_cosine_weights,
                "pca_component_count": self.pca_component_count,
                "role_aware_minimum_overlap": self.role_aware_minimum_overlap,
                "selected_model_family": self.selected_model_family.value,
                "comparison_k": self.comparison_k,
                "candidate_fixture_id": self.candidate_fixture_id,
                "candidate_fixture_digest": self.candidate_fixture_digest,
                "candidate_population_projection_digest": (
                    self.candidate_population_projection_digest
                ),
                "query_fixture_id": self.query_fixture_id,
                "query_fixture_digest": self.query_fixture_digest,
                "query_population_projection_digest": self.query_population_projection_digest,
                "expected_array_payload_digests": self.expected_array_payload_digests,
            }
        )


def _configuration_identity(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    supplied = payload.pop("configuration_digest", None)
    digest = _sha256(canonical_json_bytes(payload))
    if supplied != digest:
        raise M0RuntimeError("configuration digest drift")
    return digest


def _validated_configuration(configuration: M0Configuration) -> M0Configuration:
    """Reconstruct and pin every typed configuration field at each public boundary."""
    if not isinstance(configuration, M0Configuration):
        raise M0RuntimeError("an M0Configuration authority is required")
    mapping = dict(configuration.canonical_mapping())
    if (
        set(mapping) != _CONFIG_KEYS
        or _configuration_identity(mapping) != _ACCEPTED_CONFIGURATION[2]
        or canonical_json_bytes(mapping) != canonical_json_bytes(_ACCEPTED_CONFIGURATION_MAPPING)
    ):
        raise M0RuntimeError("typed configuration authority drift")
    return configuration


def _semantic_value(value: Any) -> Any:
    """Project frozen typed authorities back to their complete canonical JSON semantics."""
    if is_dataclass(value) and not isinstance(value, type):
        result = {
            field.name: _semantic_value(getattr(value, field.name)) for field in fields(value)
        }
        # FeatureSchema's normal schema wire format does not carry control_only;
        # its typed representation does so solely to bind definition interpretation.
        if type(value).__name__ == "FeatureSchema" and not getattr(value, "control_only"):
            result.pop("control_only")
        return result
    if isinstance(value, Mapping):
        return {key: _semantic_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_semantic_value(item) for item in value]
    return value


def _validated_registry(registry: FeatureRegistry) -> FeatureRegistry:
    """Bind the full immutable registry projection, not merely its carried digest."""
    if not isinstance(registry, FeatureRegistry):
        raise M0RuntimeError("a FeatureRegistry authority is required")
    projection = _semantic_value(registry)
    if not isinstance(projection, dict):  # pragma: no cover - dataclass invariant
        raise M0RuntimeError("registry semantic projection is invalid")
    declared = projection.pop("registry_digest", None)
    if (
        declared != registry.registry_digest
        or _sha256(registry_canonical_json_bytes(projection)) != _REGISTRY_SEMANTIC_DIGEST
        or registry.registry_digest
        != "c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644"
    ):
        raise M0RuntimeError("registry semantic authority drift")
    return registry


def load_m0_configuration(path: str | Path) -> M0Configuration:
    value = _read_canonical_json(Path(path))
    if (
        set(value) != _CONFIG_KEYS
        or _configuration_identity(value) != value["configuration_digest"]
    ):
        raise M0RuntimeError("configuration keys or digest are invalid")
    if (
        value.get("configuration_id"),
        value.get("configuration_version"),
        value.get("configuration_digest"),
    ) != _ACCEPTED_CONFIGURATION:
        raise M0RuntimeError("configuration identity is not accepted")
    if value["deterministic_seed"] != 20260803 or isinstance(value["deterministic_seed"], bool):
        raise M0RuntimeError("configuration deterministic seed drift")
    if value["pca_component_count"] != 3 or isinstance(value["pca_component_count"], bool):
        raise M0RuntimeError("configuration PCA count drift")
    if value["comparison_k"] != 3 or isinstance(value["comparison_k"], bool):
        raise M0RuntimeError("configuration k drift")
    if value["selected_model_family"] != M0ModelFamily.ROLE_AWARE_RESTRICTION.value:
        raise M0RuntimeError("configuration selected family drift")
    if (value["candidate_fixture_id"], value["candidate_fixture_digest"]) != (
        _CANDIDATE_FIXTURE[0],
        _CANDIDATE_FIXTURE[2],
    ):
        raise M0RuntimeError("candidate fixture pin drift")
    if (value["query_fixture_id"], value["query_fixture_digest"]) != (
        _QUERY_FIXTURE[0],
        _QUERY_FIXTURE[2],
    ):
        raise M0RuntimeError("query fixture pin drift")
    weights = value["weighted_cosine_weights"]
    if (
        not isinstance(weights, list)
        or len(weights) != 6
        or tuple(_strict_number(item, "weight") for item in weights)
        != (2.0, 2.0, 2.0, 2.0, 1.0, 0.1)
    ):
        raise M0RuntimeError("configuration weights drift")
    overlap = _strict_number(value["role_aware_minimum_overlap"], "role overlap")
    if overlap != 0.75:
        raise M0RuntimeError("configuration role threshold drift")
    digests = value["expected_array_payload_digests"]
    if (
        not isinstance(digests, dict)
        or set(digests) != set(_FAMILY_DIGESTS)
        or any(_sha(digests[key], key) != expected for key, expected in _FAMILY_DIGESTS.items())
    ):
        raise M0RuntimeError("configuration array digest pins drift")
    for key in ("candidate_population_projection_digest", "query_population_projection_digest"):
        _sha(value[key], key)
    return _validated_configuration(
        M0Configuration(
            configuration_id=value["configuration_id"],
            configuration_version=value["configuration_version"],
            configuration_digest=value["configuration_digest"],
            deterministic_seed=value["deterministic_seed"],
            weighted_cosine_weights=cast(
                tuple[float, float, float, float, float, float],
                tuple(float(item) for item in weights),
            ),
            pca_component_count=value["pca_component_count"],
            role_aware_minimum_overlap=overlap,
            selected_model_family=M0ModelFamily(value["selected_model_family"]),
            comparison_k=value["comparison_k"],
            candidate_fixture_id=value["candidate_fixture_id"],
            candidate_fixture_digest=value["candidate_fixture_digest"],
            candidate_population_projection_digest=value["candidate_population_projection_digest"],
            query_fixture_id=value["query_fixture_id"],
            query_fixture_digest=value["query_fixture_digest"],
            query_population_projection_digest=value["query_population_projection_digest"],
            expected_array_payload_digests=MappingProxyType(dict(digests)),
        )
    )


@dataclass(frozen=True, slots=True)
class M0DevelopmentCandidates:
    """Validated immutable reproduction of the frozen candidate universe."""

    fixture_id: str
    fixture_version: str
    fixture_digest: str
    rows: tuple[Mapping[str, Any], ...]
    peer_groups: Mapping[UUID, str]

    def population_projection(
        self, registry: FeatureRegistry, *, metadata: bool = False
    ) -> tuple[Mapping[str, Any], ...]:
        result: list[Mapping[str, Any]] = []
        positions = {"CENTRAL": 0.0, "DEFENSIVE": 1.0, "WIDE": 2.0}
        for candidate in self.rows:
            row = candidate["feature_row"]
            feature_values = tuple(
                float(item["numeric_value"]) for item in row["expected_feature_values"]
            )
            values: tuple[float, ...]
            if metadata:
                values = (
                    positions[row["synthetic_position_code"]],
                    float(row["synthetic_age_years"]),
                    float(row["synthetic_elapsed_minutes"]),
                )
            else:
                values = feature_values
            result.append(
                MappingProxyType(
                    {
                        "player_id": row["player_id"],
                        "feature_values": values,
                        "metadata": MappingProxyType(
                            {
                                "synthetic_position_code": row["synthetic_position_code"],
                                "synthetic_age_years": row["synthetic_age_years"],
                                "synthetic_elapsed_minutes": row["synthetic_elapsed_minutes"],
                            }
                        ),
                        "context_id": candidate["role_row"]["context_id"],
                        "contextual_role_memberships": candidate["role_row"][
                            "expected_role_probabilities"
                        ],
                        "feature_cutoff_ts": row["feature_cutoff_ts"],
                        "dependency_identity": row["dependency_identity"],
                        "dependency_lineage_hash": row["dependency_identity"]["lineage_hash"],
                    }
                )
            )
        return tuple(result)

    def population_digest(self, registry: FeatureRegistry, *, metadata: bool = False) -> str:
        return _sha256(
            canonical_json_bytes(self.population_projection(registry, metadata=metadata))
        )


@dataclass(frozen=True, slots=True)
class M0DevelopmentQueries:
    """Validated immutable reproduction of the frozen ordered query authority."""

    fixture_id: str
    fixture_version: str
    fixture_digest: str
    queries: tuple[Mapping[str, Any], ...]

    def projection_digest(self) -> str:
        return _sha256(canonical_json_bytes(self.queries))


def _validated_candidates(
    candidates: M0DevelopmentCandidates, *, registry: FeatureRegistry, taxonomy: RoleTaxonomy
) -> M0DevelopmentCandidates:
    """Require the complete frozen candidate authority, including source order and rows."""
    _validated_registry(registry)
    _validated_taxonomy(taxonomy)
    if not isinstance(candidates, M0DevelopmentCandidates):
        raise M0RuntimeError("an M0DevelopmentCandidates authority is required")
    projection = {
        "fixture_id": candidates.fixture_id,
        "fixture_version": candidates.fixture_version,
        "fixture_digest": candidates.fixture_digest,
        "rows": candidates.rows,
        "peer_groups": {str(key): value for key, value in candidates.peer_groups.items()},
    }
    if (
        (candidates.fixture_id, candidates.fixture_version, candidates.fixture_digest)
        != _CANDIDATE_FIXTURE
        or _sha256(canonical_json_bytes(projection)) != _CANDIDATE_AUTHORITY_DIGEST
        or len(candidates.rows) != 18
        or tuple(candidates.peer_groups)
        != tuple(UUID(row["feature_row"]["player_id"]) for row in candidates.rows)
    ):
        raise M0RuntimeError("typed candidate authority drift")
    return candidates


def _validated_queries(
    queries: M0DevelopmentQueries,
    *,
    candidates: M0DevelopmentCandidates,
    configuration: M0Configuration,
) -> M0DevelopmentQueries:
    """Require exact frozen query order, IDs and peer-group projection."""
    _validated_configuration(configuration)
    if not isinstance(queries, M0DevelopmentQueries):
        raise M0RuntimeError("an M0DevelopmentQueries authority is required")
    projection = {
        "fixture_id": queries.fixture_id,
        "fixture_version": queries.fixture_version,
        "fixture_digest": queries.fixture_digest,
        "queries": queries.queries,
    }
    if (
        (queries.fixture_id, queries.fixture_version, queries.fixture_digest) != _QUERY_FIXTURE
        or _sha256(canonical_json_bytes(projection)) != _QUERY_AUTHORITY_DIGEST
        or len(queries.queries) != len(candidates.rows)
        or queries.projection_digest() != configuration.query_population_projection_digest
    ):
        raise M0RuntimeError("typed query authority drift")
    for query, candidate in zip(queries.queries, candidates.rows, strict=True):
        player_id = UUID(candidate["feature_row"]["player_id"])
        if (
            query["player_id"] != str(player_id)
            or query["relevant_peer_group"] != candidates.peer_groups[player_id]
            or query["k"] != configuration.comparison_k
            or query["self_excluded"] is not True
        ):
            raise M0RuntimeError("typed query peer-group authority drift")
    return queries


def load_m0_development_candidates(
    path: str | Path, *, registry: FeatureRegistry, taxonomy: RoleTaxonomy
) -> M0DevelopmentCandidates:
    _validated_registry(registry)
    _validated_taxonomy(taxonomy)
    raw = _read_canonical_json(Path(path))
    if set(raw) != _CANDIDATE_ROOT_KEYS:
        raise M0RuntimeError("candidate fixture root keys are not exact")
    payload = dict(raw)
    if (
        _sha256(
            canonical_json_bytes(
                {key: value for key, value in payload.items() if key != "fixture_digest"}
            )
        )
        != raw["fixture_digest"]
    ):
        raise M0RuntimeError("candidate fixture digest drift")
    if (raw["fixture_id"], raw["fixture_version"], raw["fixture_digest"]) != _CANDIDATE_FIXTURE:
        raise M0RuntimeError("candidate fixture source pin drift")
    if (
        raw["registry_id"],
        raw["registry_digest"],
        raw["family_id"],
        raw["family_digest"],
        raw["feature_schema_hash"],
    ) != (
        registry.registry_id,
        registry.registry_digest,
        registry.synthetic_family.family_id,
        registry.synthetic_family.family_digest,
        registry.synthetic_family.schema.schema_hash,
    ):
        raise M0RuntimeError("candidate feature authority pin drift")
    if (raw["taxonomy_id"], raw["taxonomy_version"], raw["taxonomy_digest"]) != (
        taxonomy.taxonomy_id,
        taxonomy.taxonomy_version,
        taxonomy.taxonomy_digest,
    ):
        raise M0RuntimeError("candidate taxonomy pin drift")
    claims = {
        "synthetic_development": True,
        "development_only": True,
        "protected": False,
        "recruitment_outcome": False,
        "external_expert_label": False,
        "production_claim": False,
    }
    if (
        any(raw.get(key) is not expected for key, expected in claims.items())
        or raw.get("claim") != "constructed_W05_M0_development_only"
        or raw.get("evidence_class") != "synthetic_development"
        or raw.get("provider_source") != "NONE"
    ):
        raise M0RuntimeError("candidate claim pin drift")
    candidates = raw["candidates"]
    if not isinstance(candidates, list) or len(candidates) != 18:
        raise M0RuntimeError("candidate count drift")
    rows: list[Mapping[str, Any]] = []
    groups: dict[UUID, str] = {}
    roles = tuple(sorted(item.code for item in taxonomy.contract.roles))
    for ordinal, candidate in enumerate(candidates, 1):
        candidate = _exact_keys(candidate, frozenset({"feature_row", "role_row"}), "candidate")
        feature = _exact_keys(candidate["feature_row"], _FEATURE_ROW_KEYS, "candidate feature row")
        role = _exact_keys(candidate["role_row"], _ROLE_ROW_KEYS, "candidate role row")
        expected_id = f"20000000-0000-4000-8000-{ordinal:012d}"
        if feature["player_id"] != expected_id or role["player_id"] != expected_id:
            raise M0RuntimeError("candidate UUID/order drift")
        materialized = materialize_synthetic_row(feature, registry)
        expected_values = [
            item.model_dump(mode="json", exclude_none=True) for item in materialized.values
        ]
        if feature["expected_feature_values"] != expected_values:
            raise M0RuntimeError("candidate feature reproduction drift")
        membership = contextual_role_membership(
            player_id=UUID(expected_id),
            context_id=role["context_id"],
            taxonomy=taxonomy,
            responsibility_evidence=role["responsibility_evidence"],
            source_label_prior=role["source_label_prior"],
        )
        expected_memberships = [item.model_dump(mode="json") for item in membership.memberships]
        values = role["expected_role_probabilities"]
        if (
            values != expected_memberships
            or not isinstance(values, list)
            or tuple(item.get("role_code") for item in values) != roles
        ):
            raise M0RuntimeError("candidate role reproduction/order drift")
        if (
            any(
                isinstance(item.get("probability"), bool)
                or not isinstance(item.get("probability"), (int, float))
                or not math.isfinite(item["probability"])
                or not 0.0 <= item["probability"] <= 1.0
                for item in values
            )
            or math.fsum(item["probability"] for item in values) != 1.0
        ):
            raise M0RuntimeError("candidate role probability drift")
        rows.append(_deep_freeze(candidate))
        groups[UUID(expected_id)] = feature["constructed_development_peer_group"]
    return M0DevelopmentCandidates(
        raw["fixture_id"],
        raw["fixture_version"],
        raw["fixture_digest"],
        tuple(rows),
        MappingProxyType(groups),
    )


def load_m0_development_queries(
    path: str | Path, *, candidates: M0DevelopmentCandidates, configuration: M0Configuration
) -> M0DevelopmentQueries:
    _validated_configuration(configuration)
    if not isinstance(candidates, M0DevelopmentCandidates):
        raise M0RuntimeError("an M0DevelopmentCandidates authority is required")
    raw = _read_canonical_json(Path(path))
    if set(raw) != _QUERY_ROOT_KEYS:
        raise M0RuntimeError("query fixture root keys are not exact")
    if (
        _sha256(
            canonical_json_bytes(
                {key: value for key, value in raw.items() if key != "fixture_digest"}
            )
        )
        != raw["fixture_digest"]
        or (raw["fixture_id"], raw["fixture_version"], raw["fixture_digest"]) != _QUERY_FIXTURE
    ):
        raise M0RuntimeError("query fixture identity drift")
    if (
        raw["candidate_fixture_digest"] != candidates.fixture_digest
        or raw["candidate_fixture_digest"] != configuration.candidate_fixture_digest
    ):
        raise M0RuntimeError("query/candidate cross pin drift")
    claims = {
        "development_only": True,
        "protected": False,
        "recruitment_outcome": False,
        "external_expert_label": False,
        "production_claim": False,
    }
    if (
        any(raw.get(key) is not expected for key, expected in claims.items())
        or raw.get("claim") != "constructed_W05_M0_development_only"
        or raw.get("evidence_class") != "synthetic_development"
        or raw.get("provider_source") != "NONE"
    ):
        raise M0RuntimeError("query claim pin drift")
    queries = raw["queries"]
    ids = tuple(UUID(candidate["feature_row"]["player_id"]) for candidate in candidates.rows)
    if not isinstance(queries, list) or len(queries) != len(ids):
        raise M0RuntimeError("query count drift")
    expected_keys = {"k", "player_id", "relevant_peer_group", "self_excluded"}
    for query, player_id in zip(queries, ids, strict=True):
        if (
            not isinstance(query, dict)
            or set(query) != expected_keys
            or query["player_id"] != str(player_id)
            or query["k"] != configuration.comparison_k
            or query["self_excluded"] is not True
            or query["relevant_peer_group"] != candidates.peer_groups[player_id]
        ):
            raise M0RuntimeError("query projection/order drift")
    frozen = tuple(_deep_freeze(item) for item in queries)
    authority = M0DevelopmentQueries(
        raw["fixture_id"], raw["fixture_version"], raw["fixture_digest"], frozen
    )
    if authority.projection_digest() != configuration.query_population_projection_digest:
        raise M0RuntimeError("query population projection pin drift")
    return authority


def _require_root(root: Path) -> Path:
    absolute = root.absolute()
    if root.is_symlink() or absolute.is_symlink():
        raise M0RuntimeError("artifact root symlink is forbidden")
    try:
        resolved = root.resolve(strict=True)
    except OSError as error:
        raise M0RuntimeError("artifact root is unavailable") from error
    if absolute != resolved or not resolved.is_dir():
        raise M0RuntimeError("artifact root path is unsafe")
    if tuple(sorted(item.name for item in resolved.iterdir())) != tuple(sorted(_ARTIFACT_FILES)):
        raise M0RuntimeError("artifact root contains missing or extra entries")
    for name in _ARTIFACT_FILES:
        item = resolved / name
        if item.is_symlink() or not item.is_file() or item.resolve() != item:
            raise M0RuntimeError("artifact entry is unsafe")
    return resolved


def _array_bytes(array: np.ndarray) -> bytes:
    return np.ascontiguousarray(array).tobytes(order="C")


def _validate_arrays(
    npz_path: Path, manifest: M0ArtifactManifest
) -> Mapping[M0ArraySemanticRole, np.ndarray]:
    expected_names = tuple(descriptor.name + ".npy" for descriptor in manifest.array_descriptors)
    if any(
        descriptor.endianness is not M0Endianness.LITTLE
        or descriptor.memory_order is not M0MemoryOrder.C
        for descriptor in manifest.array_descriptors
    ):
        raise M0RuntimeError("array descriptors must declare little-endian C-order payloads")
    try:
        with zipfile.ZipFile(npz_path) as archive:
            infos = archive.infolist()
            if (
                tuple(item.filename for item in infos) != expected_names
                or archive.comment
                or any(
                    item.is_dir()
                    or item.flag_bits
                    or item.compress_type != zipfile.ZIP_STORED
                    or item.date_time != (1980, 1, 1, 0, 0, 0)
                    or item.external_attr != (0o600 << 16)
                    or item.file_size <= 0
                    for item in infos
                )
            ):
                raise M0RuntimeError("NPZ members are unsafe")
        with np.load(npz_path, allow_pickle=False) as archive:
            if tuple(item + ".npy" for item in archive.files) != expected_names:
                raise M0RuntimeError("NPZ array names/order differ")
            arrays = {
                descriptor.semantic_role: archive[descriptor.name]
                for descriptor in manifest.array_descriptors
            }
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        raise M0RuntimeError("unsafe or unreadable arrays.npz") from error
    payload = bytearray()
    for descriptor in manifest.array_descriptors:
        array = arrays[descriptor.semantic_role]
        dtype = np.dtype("<f8" if descriptor.dtype is M0ArrayDtype.FLOAT64 else "u1")
        if (
            array.dtype != dtype
            or array.shape != descriptor.shape
            or not array.flags.c_contiguous
            or array.dtype.hasobject
            or len(_array_bytes(array)) != descriptor.byte_length
            or _sha256(_array_bytes(array)) != descriptor.digest
        ):
            raise M0RuntimeError("array descriptor does not match payload")
        payload.extend(descriptor.name.encode("ascii"))
        payload.extend(b"\0")
        payload.extend(_array_bytes(array))
        array.setflags(write=False)
    if _sha256(bytes(payload)) != manifest.array_payload_digest:
        raise M0RuntimeError("array payload digest mismatch")
    return MappingProxyType(arrays)


def _uuid_rows(array: np.ndarray) -> tuple[UUID, ...]:
    try:
        rows = tuple(UUID(bytes=bytes(item)) for item in array)
    except (TypeError, ValueError) as error:
        raise M0RuntimeError("index player IDs are not UUID bytes") from error
    if len(rows) != len(set(rows)) or tuple(sorted(rows, key=lambda item: item.bytes)) != rows:
        raise M0RuntimeError("candidate UUID order is not canonical")
    return rows


@dataclass(frozen=True, slots=True)
class M0DistanceRow:
    player_id: UUID
    distance: float
    contributions: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class LoadedM0Artifact:
    manifest: M0ArtifactManifest
    configuration: M0Configuration
    candidate_universe: Mapping[str, Any]
    arrays: Mapping[M0ArraySemanticRole, np.ndarray]
    player_ids: tuple[UUID, ...]
    _memberships: Mapping[UUID, Mapping[str, float]]

    def score(
        self,
        query_player_id: UUID | None = None,
        *,
        limit: int = 3,
        excluded_player_ids: tuple[UUID, ...] = (),
        exemplar_player_ids: tuple[UUID, ...] = (),
    ) -> tuple[M0DistanceRow, ...]:
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 1
            or (query_player_id is None) == (not exemplar_player_ids)
        ):
            raise M0RuntimeError("provide exactly one indexed query or exemplars")
        if (
            any(not isinstance(item, UUID) for item in excluded_player_ids)
            or len(excluded_player_ids) != len(set(excluded_player_ids))
            or any(not isinstance(item, UUID) for item in exemplar_player_ids)
            or len(exemplar_player_ids) != len(set(exemplar_player_ids))
        ):
            raise M0RuntimeError("exclusions and exemplars must be unique UUID tuples")
        if set(excluded_player_ids) & set(exemplar_player_ids):
            raise M0RuntimeError("exclusions cannot overlap exemplars")
        vectors = self.arrays[M0ArraySemanticRole.INDEX_VECTORS]
        if query_player_id is not None:
            if not isinstance(query_player_id, UUID):
                raise M0RuntimeError("query must be a UUID")
            try:
                query = vectors[self.player_ids.index(query_player_id)]
            except ValueError as error:
                raise M0RuntimeError("query is absent") from error
            roles = self._memberships[query_player_id]
            excluded = set(excluded_player_ids) | {query_player_id}
        else:
            ordered = tuple(sorted(exemplar_player_ids, key=lambda item: item.bytes))
            try:
                query = np.mean(
                    vectors[[self.player_ids.index(item) for item in ordered]],
                    axis=0,
                    dtype=np.float64,
                )
            except ValueError as error:
                raise M0RuntimeError("exemplar is absent") from error
            codes = tuple(next(iter(self._memberships.values())).keys())
            roles = {
                code: math.fsum(self._memberships[item][code] for item in ordered) / len(ordered)
                for code in codes
            }
            excluded = set(excluded_player_ids) | set(ordered)
        components = self.arrays.get(M0ArraySemanticRole.PCA_COMPONENTS)
        if self.manifest.model_family is M0ModelFamily.PCA and (
            components is None or components.shape[1] != 6
        ):
            raise M0RuntimeError("PCA component projection is invalid")
        contribution_projection = (
            np.square(components)
            if self.manifest.model_family is M0ModelFamily.PCA and components is not None
            else None
        )
        admitted = np.array(
            [
                player_id not in excluded
                and not (
                    self.manifest.model_family is M0ModelFamily.ROLE_AWARE_RESTRICTION
                    and math.fsum(
                        min(roles[code], self._memberships[player_id][code]) for code in roles
                    )
                    < self.configuration.role_aware_minimum_overlap
                )
                for player_id in self.player_ids
            ],
            dtype=np.bool_,
        )
        scored = score_vector_rows(
            query=query,
            candidate_vectors=vectors,
            candidate_keys=tuple(VectorCandidateKey(item) for item in self.player_ids),
            method=(
                VectorScoringMethod.WEIGHTED_EUCLIDEAN
                if self.manifest.model_family
                in {M0ModelFamily.METADATA_CONTROL, M0ModelFamily.RAW_EUCLIDEAN_CONTROL}
                else VectorScoringMethod.WEIGHTED_COSINE
            ),
            admitted=admitted,
            contribution_projection=contribution_projection,
            limit=limit,
        )
        return tuple(
            M0DistanceRow(row.key.player_id, row.distance, row.contributions) for row in scored
        )


def _identity(
    family: M0ModelFamily,
    configuration: M0Configuration,
    registry: FeatureRegistry,
    taxonomy: FootballResponsibilityTaxonomy,
    population_digest: str,
    lineage: str,
    payload: str,
) -> UUID:
    return uuid5(
        _NAMESPACE,
        "|".join(
            (
                family.value,
                configuration.configuration_digest,
                registry.registry_digest,
                taxonomy.taxonomy_digest,
                population_digest,
                lineage,
                payload,
            )
        ),
    )


def load_m0_artifact(
    root: str | Path,
    *,
    taxonomy: RoleTaxonomy | FootballResponsibilityTaxonomy,
    registry: FeatureRegistry,
    configuration: M0Configuration,
    candidates: M0DevelopmentCandidates,
    queries: M0DevelopmentQueries,
) -> LoadedM0Artifact:
    _validated_configuration(configuration)
    _validated_registry(registry)
    if not isinstance(taxonomy, RoleTaxonomy):
        raise M0RuntimeError("a RoleTaxonomy authority is required")
    _validated_candidates(candidates, registry=registry, taxonomy=taxonomy)
    _validated_queries(queries, candidates=candidates, configuration=configuration)
    contract = _validated_taxonomy(taxonomy)
    artifact_root = _require_root(Path(root))
    disk_config = _read_canonical_json(artifact_root / "configuration.json")
    if canonical_json_bytes(disk_config) != canonical_json_bytes(configuration.canonical_mapping()):
        raise M0RuntimeError("artifact configuration substitution")
    universe = _read_canonical_json(artifact_root / "candidate-universe.json")
    try:
        manifest = M0ArtifactManifest.model_validate_json(
            canonical_json_bytes(_read_canonical_json(artifact_root / "manifest.json"))
        )
    except ValueError as error:
        raise M0RuntimeError("artifact manifest validation failed") from error
    schema = (
        registry.synthetic_family.metadata_control_schema
        if manifest.model_family is M0ModelFamily.METADATA_CONTROL
        else registry.synthetic_family.schema
    )
    if schema is None:
        raise M0RuntimeError("metadata schema unavailable")
    metadata = manifest.model_family is M0ModelFamily.METADATA_CONTROL
    expected_projection = candidates.population_projection(registry, metadata=metadata)
    expected_population_digest = _sha256(canonical_json_bytes(expected_projection))
    if (
        not metadata
        and expected_population_digest != configuration.candidate_population_projection_digest
    ):
        raise M0RuntimeError("selected candidate population pin drift")
    expected_universe = {
        "schema_version": 1,
        "candidate_universe_id": "w05-synthetic-development-candidate-universe-v1",
        "evidence_class": "synthetic_development",
        "feature_schema_hash": schema.schema_hash,
        "feature_cutoff_ts": "2026-08-01T00:00:00Z",
        "feature_names": [item.name for item in schema.features],
        "candidate_fixture_id": candidates.fixture_id,
        "candidate_fixture_digest": candidates.fixture_digest,
        "query_fixture_id": queries.fixture_id,
        "query_fixture_digest": queries.fixture_digest,
        "candidate_population_projection_digest": expected_population_digest,
        "query_population_projection_digest": queries.projection_digest(),
        "taxonomy_id": contract.taxonomy_id,
        "taxonomy_version": contract.taxonomy_version,
        "taxonomy_digest": contract.taxonomy_digest,
        "development_only": True,
        "protected": False,
        "recruitment_outcome": False,
        "external_expert_label": False,
        "production_claim": False,
        "candidates": list(expected_projection),
    }
    universe_digest = _sha256(canonical_json_bytes(expected_universe))
    lineage = _sha256(
        canonical_json_bytes([item["dependency_lineage_hash"] for item in expected_projection])
    )
    if (
        canonical_json_bytes(universe) != canonical_json_bytes(expected_universe)
        or manifest.candidate_universe_manifest_digest != universe_digest
        or manifest.fitting_population_manifest_digest != expected_population_digest
        or manifest.lineage_identity != lineage
    ):
        raise M0RuntimeError("candidate universe/lineage substitution")
    if (
        manifest.feature_schema_hash,
        tuple(manifest.feature_names),
        manifest.feature_registry_id,
        manifest.feature_registry_canonical_digest,
        manifest.feature_registry_decision_digest,
        manifest.feature_descriptor_digest,
        manifest.evidence_class.value,
        manifest.taxonomy_id,
        manifest.taxonomy_version,
        manifest.taxonomy_digest,
        manifest.configuration_digest,
        manifest.model_id,
        manifest.model_version,
        manifest.index_id,
        manifest.index_version,
        manifest.fitting_population_id,
        manifest.fitting_population_count,
        manifest.candidate_universe_id,
        manifest.candidate_universe_count,
        manifest.deterministic_seed,
        manifest.serialization_format.value,
        manifest.pca_orientation_policy.value if manifest.pca_orientation_policy else None,
        (
            manifest.pca_component_tie_order_policy.value
            if manifest.pca_component_tie_order_policy
            else None
        ),
    ) != (
        schema.schema_hash,
        tuple(item.name for item in schema.features),
        registry.registry_id,
        registry.registry_digest,
        registry.registry_digest,
        registry.synthetic_family.family_digest,
        "synthetic_development",
        contract.taxonomy_id,
        contract.taxonomy_version,
        contract.taxonomy_digest,
        configuration.configuration_digest,
        f"w05-m0-{manifest.model_family.value}-v1",
        "v1",
        f"w05-m0-{manifest.model_family.value}-index-v1",
        "v1",
        "w05-synthetic-development-complete-rows-v1",
        18,
        "w05-synthetic-development-candidate-universe-v1",
        18,
        configuration.deterministic_seed,
        "numpy_npz",
        "lowest_index_max_abs_pivot_non_negative"
        if manifest.model_family is M0ModelFamily.PCA
        else None,
        "explained_variance_descending_then_component_bytes"
        if manifest.model_family is M0ModelFamily.PCA
        else None,
    ):
        raise M0RuntimeError("manifest accepted identity substitution")
    arrays = _validate_arrays(artifact_root / "arrays.npz", manifest)
    if configuration.expected_array_payload_digests.get(
        manifest.model_family.value
    ) != manifest.array_payload_digest or manifest.artifact_id != _identity(
        manifest.model_family,
        configuration,
        registry,
        contract,
        expected_population_digest,
        lineage,
        manifest.array_payload_digest,
    ):
        raise M0RuntimeError("artifact identity or payload pin drift")
    player_ids = _uuid_rows(arrays[M0ArraySemanticRole.INDEX_PLAYER_IDS])
    if player_ids != tuple(UUID(item["player_id"]) for item in expected_projection):
        raise M0RuntimeError("indexed candidate population drift")
    roles = tuple(sorted(item.code for item in contract.roles))
    memberships: dict[UUID, Mapping[str, float]] = {}
    for item in expected_projection:
        raw = item["contextual_role_memberships"]
        if (
            tuple(entry["role_code"] for entry in raw) != roles
            or math.fsum(_strict_number(entry["probability"], "role probability") for entry in raw)
            != 1.0
        ):
            raise M0RuntimeError("role membership state drift")
        memberships[UUID(item["player_id"])] = MappingProxyType(
            {entry["role_code"]: float(entry["probability"]) for entry in raw}
        )
    return LoadedM0Artifact(
        manifest,
        configuration,
        _deep_freeze(universe),
        arrays,
        player_ids,
        MappingProxyType(memberships),
    )

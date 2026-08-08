"""Deterministic fitting and safe writing for the six approved M0 families."""

from __future__ import annotations

import hashlib
import io
import os
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from uuid import UUID

import numpy as np
from sklearn.decomposition import PCA  # type: ignore[import-untyped]

from scouting.contracts.m0 import (
    M0ArrayDescriptor,
    M0ArrayDtype,
    M0ArraySemanticRole,
    M0ArtifactManifest,
    M0Endianness,
    M0MemoryOrder,
    M0ModelFamily,
)
from scouting.features.registry import (
    FeatureRegistry,
    MaterializedFeatureRow,
    materialize_synthetic_row,
)
from scouting.m0.core import (
    M0Configuration,
    M0DevelopmentCandidates,
    M0DevelopmentQueries,
    _identity,
    _validated_candidates,
    _validated_configuration,
    _validated_queries,
    _validated_registry,
    _validated_taxonomy,
    load_m0_artifact,
)
from scouting.roles.taxonomy import RoleTaxonomy
from scouting.storage.formats import canonical_json_bytes


class M0TrainingError(ValueError):
    """Raised for rejected M0 fitting populations or deterministic write failures."""


_ARRAY_NAMES = {
    M0ArraySemanticRole.FEATURE_MATRIX: "feature_matrix",
    M0ArraySemanticRole.SCALER_CENTER: "scaler_center",
    M0ArraySemanticRole.SCALER_SCALE: "scaler_scale",
    M0ArraySemanticRole.FEATURE_WEIGHTS: "feature_weights",
    M0ArraySemanticRole.PCA_COMPONENTS: "pca_components",
    M0ArraySemanticRole.PCA_EXPLAINED_VARIANCE: "pca_explained_variance",
    M0ArraySemanticRole.INDEX_VECTORS: "index_vectors",
    M0ArraySemanticRole.INDEX_PLAYER_IDS: "index_player_ids",
}


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _numeric_values(materialized: MaterializedFeatureRow) -> tuple[float, ...]:
    result: list[float] = []
    for value in materialized.values:
        if value.numeric_value is None:
            raise M0TrainingError("incomplete or absent numeric feature state is not admitted")
        result.append(float(value.numeric_value))
    return tuple(result)


def canonical_feature_value_projection(
    materialized: MaterializedFeatureRow,
) -> list[dict[str, Any]]:
    """Return the accepted fixture wire projection without numeric null fields."""
    return [value.model_dump(mode="json", exclude_none=True) for value in materialized.values]


def _thaw(value: Any) -> Any:
    """Make an internal materializer input without accepting caller mappings."""
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _population(
    candidates: M0DevelopmentCandidates,
    *,
    registry: FeatureRegistry,
    taxonomy: RoleTaxonomy,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    rows: list[dict[str, Any]] = []
    seen: set[UUID] = set()
    for candidate in candidates.rows:
        raw = _thaw(candidate["feature_row"])
        role = candidate["role_row"]
        try:
            UUID(str(raw["player_id"]))
        except (KeyError, ValueError) as error:
            raise M0TrainingError("feature candidate has no valid player ID") from error
        try:
            materialized = materialize_synthetic_row(raw, registry)
            values = _numeric_values(materialized)
        except (ValueError, M0TrainingError) as error:
            raise M0TrainingError("typed candidate failed feature materialization") from error
        player_id = materialized.player_id
        if player_id in seen:
            raise M0TrainingError("duplicate fitting player ID")
        seen.add(player_id)
        if raw["feature_cutoff_ts"] != "2026-08-01T00:00:00Z":
            raise M0TrainingError("post-cutoff feature lineage is not admitted")
        rows.append(
            {
                "player_id": player_id,
                "feature_values": values,
                "metadata": {
                    "synthetic_position_code": raw["synthetic_position_code"],
                    "synthetic_age_years": raw["synthetic_age_years"],
                    "synthetic_elapsed_minutes": raw["synthetic_elapsed_minutes"],
                },
                "feature_cutoff_ts": raw["feature_cutoff_ts"],
                "dependency_lineage_hash": materialized.dependency_lineage_hash,
                "dependency_identity": raw["dependency_identity"],
                "context_id": role["context_id"],
                "contextual_role_memberships": role["expected_role_probabilities"],
            }
        )
    rows.sort(key=lambda row: row["player_id"].bytes)
    if len(rows) != 18:
        raise M0TrainingError("typed candidate authority must admit its full population")
    return rows, np.asarray([row["feature_values"] for row in rows], dtype="<f8", order="C")


def _metadata_matrix(rows: Sequence[Mapping[str, Any]]) -> np.ndarray:
    codes = {
        code: index
        for index, code in enumerate(
            sorted({row["metadata"]["synthetic_position_code"] for row in rows})
        )
    }
    return np.asarray(
        [
            (
                float(codes[row["metadata"]["synthetic_position_code"]]),
                float(row["metadata"]["synthetic_age_years"]),
                float(row["metadata"]["synthetic_elapsed_minutes"]),
            )
            for row in rows
        ],
        dtype="<f8",
        order="C",
    )


def _canonical_pca(
    matrix: np.ndarray, component_count: int, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fitted = PCA(n_components=component_count, svd_solver="full", random_state=seed).fit(matrix)
    components = np.asarray(fitted.components_, dtype="<f8", order="C")
    variance = np.asarray(fitted.explained_variance_, dtype="<f8")
    for index, component in enumerate(components):
        maximum = np.max(np.abs(component))
        pivot = int(np.flatnonzero(np.abs(component) == maximum)[0])
        if component[pivot] < 0:
            components[index] *= -1.0
    order = sorted(
        range(len(variance)), key=lambda index: (-variance[index], components[index].tobytes())
    )
    components = np.ascontiguousarray(components[order], dtype="<f8")
    variance = np.ascontiguousarray(variance[order], dtype="<f8")
    # A non-tied component retains the R5 sign/order bytes exactly.  For an exactly
    # tied eigenspace, its projector is invariant to SVD rotation; projecting the
    # standard axes and applying ordered Gram-Schmidt creates one canonical basis.
    start = 0
    while start < len(variance):
        stop = start + 1
        while stop < len(variance) and variance[stop] == variance[start]:
            stop += 1
        if stop - start > 1:
            components[start:stop] = _canonical_tied_basis(components[start:stop])
        start = stop
    return components, variance, np.ascontiguousarray(matrix @ components.T, dtype="<f8")


def _canonical_tied_basis(components: np.ndarray) -> np.ndarray:
    """Canonicalize a tied subspace from its rounded invariant projector.

    Fifteen decimal places are the fixed on-wire precision for tied-subspace
    canonicalization only. This removes insignificant SVD rotation residue (including
    45-degree rotations) before the ordered standard-axis Gram-Schmidt policy.
    """
    projector = components.T @ components
    projector = np.round((projector + projector.T) / 2.0, 15)
    basis: list[np.ndarray] = []
    for axis in range(projector.shape[0]):
        vector = np.asarray(projector[:, axis], dtype="<f8")
        for prior in basis:
            vector -= np.dot(vector, prior) * prior
        magnitude = float(np.linalg.norm(vector))
        if magnitude > 1e-12:
            basis.append(np.ascontiguousarray(vector / magnitude, dtype="<f8"))
        if len(basis) == components.shape[0]:
            break
    if len(basis) != components.shape[0]:  # pragma: no cover - projector rank invariant
        raise M0TrainingError("tied PCA projector cannot form a canonical basis")
    return np.asarray(basis, dtype="<f8")


def _require_safe_destination(destination: Path) -> Path:
    """Reject every existing symlink or resolve-drifting ancestor before writing."""
    absolute = destination.absolute()
    ancestors = (absolute, *absolute.parents)
    for ancestor in ancestors:
        if not ancestor.exists():
            continue
        try:
            resolved = ancestor.resolve(strict=True)
        except OSError as error:
            raise M0TrainingError("artifact destination ancestor is unavailable") from error
        if ancestor.is_symlink() or resolved != ancestor:
            raise M0TrainingError("artifact destination ancestor is unsafe")
    absolute.mkdir(mode=0o700, parents=True, exist_ok=True)
    if absolute.is_symlink() or not absolute.is_dir() or absolute.resolve(strict=True) != absolute:
        raise M0TrainingError("artifact destination is unsafe")
    return absolute


def _npz_bytes(arrays: Sequence[tuple[str, np.ndarray]]) -> bytes:
    """Build a non-executable NPZ with fixed ZIP metadata and ordered members."""
    output = io.BytesIO()
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True
    ) as archive:
        for name, array in arrays:
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.ascontiguousarray(array), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o600 << 16
            archive.writestr(info, buffer.getvalue())
    return output.getvalue()


def _descriptor(role: M0ArraySemanticRole, array: np.ndarray) -> M0ArrayDescriptor:
    dtype = (
        M0ArrayDtype.UINT8 if role is M0ArraySemanticRole.INDEX_PLAYER_IDS else M0ArrayDtype.FLOAT64
    )
    payload = np.ascontiguousarray(array).tobytes(order="C")
    return M0ArrayDescriptor(
        name=_ARRAY_NAMES[role],
        semantic_role=role,
        dtype=dtype,
        shape=array.shape,
        endianness=M0Endianness.LITTLE,
        memory_order=M0MemoryOrder.C,
        byte_length=len(payload),
        digest=_sha256(payload),
    )


def _write_immutable(path: Path, payload: bytes) -> None:
    if path.exists():
        if not path.is_file() or path.is_symlink() or path.read_bytes() != payload:
            raise M0TrainingError(f"immutable artifact conflict for {path.name}")
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        os.write(descriptor, payload)
    finally:
        os.close(descriptor)


def fit_m0_artifact(
    family: M0ModelFamily,
    *,
    candidates: M0DevelopmentCandidates,
    taxonomy: RoleTaxonomy,
    registry: FeatureRegistry,
    configuration: M0Configuration,
    artifact_directory: str | Path,
) -> M0ArtifactManifest:
    """Fit exactly one approved M0 family and write its four immutable artifact files."""
    if not isinstance(family, M0ModelFamily):
        raise M0TrainingError("an approved M0ModelFamily is required")
    if not isinstance(candidates, M0DevelopmentCandidates) or not isinstance(
        configuration, M0Configuration
    ):
        raise M0TrainingError("fitting requires typed candidate and configuration authorities")
    if not isinstance(taxonomy, RoleTaxonomy):
        raise M0TrainingError("fitting requires a RoleTaxonomy authority")
    try:
        _validated_configuration(configuration)
        _validated_registry(registry)
        _validated_candidates(candidates, registry=registry, taxonomy=taxonomy)
    except ValueError as error:
        raise M0TrainingError("typed fitting authority drift") from error
    contract = _validated_taxonomy(taxonomy)
    rows, raw_matrix = _population(candidates, registry=registry, taxonomy=taxonomy)
    metadata = _metadata_matrix(rows)
    feature_names = tuple(item.name for item in registry.synthetic_family.schema.features)
    matrix = raw_matrix
    arrays: list[tuple[M0ArraySemanticRole, np.ndarray]] = []
    if family is M0ModelFamily.METADATA_CONTROL:
        matrix = metadata
        if registry.synthetic_family.metadata_control_schema is None:
            raise M0TrainingError("metadata control schema is absent")
        feature_names = tuple(
            item.name for item in registry.synthetic_family.metadata_control_schema.features
        )
        vectors = matrix
    elif family is M0ModelFamily.RAW_EUCLIDEAN_CONTROL:
        vectors = matrix
    else:
        center = np.ascontiguousarray(np.median(matrix, axis=0), dtype="<f8")
        scale = np.ascontiguousarray(
            np.quantile(matrix, 0.75, axis=0) - np.quantile(matrix, 0.25, axis=0), dtype="<f8"
        )
        scale[scale == 0.0] = 1.0
        scaled = np.ascontiguousarray((matrix - center) / scale, dtype="<f8")
        arrays.extend(
            [(M0ArraySemanticRole.SCALER_CENTER, center), (M0ArraySemanticRole.SCALER_SCALE, scale)]
        )
        if family in {M0ModelFamily.WEIGHTED_COSINE, M0ModelFamily.ROLE_AWARE_RESTRICTION}:
            weights = np.ascontiguousarray(
                np.asarray(configuration.weighted_cosine_weights, dtype="<f8"), dtype="<f8"
            )
            arrays.append((M0ArraySemanticRole.FEATURE_WEIGHTS, weights))
            vectors = np.ascontiguousarray(scaled * weights, dtype="<f8")
        elif family is M0ModelFamily.PCA:
            components, variance, vectors = _canonical_pca(
                scaled, configuration.pca_component_count, configuration.deterministic_seed
            )
            arrays.extend(
                [
                    (M0ArraySemanticRole.PCA_COMPONENTS, components),
                    (M0ArraySemanticRole.PCA_EXPLAINED_VARIANCE, variance),
                ]
            )
        else:
            vectors = scaled
    ids = np.ascontiguousarray(
        np.asarray([list(row["player_id"].bytes) for row in rows], dtype=np.uint8), dtype=np.uint8
    )
    ordered_arrays = [
        (M0ArraySemanticRole.FEATURE_MATRIX, matrix),
        *arrays,
        (M0ArraySemanticRole.INDEX_VECTORS, vectors),
        (M0ArraySemanticRole.INDEX_PLAYER_IDS, ids),
    ]
    descriptors = tuple(_descriptor(role, array) for role, array in ordered_arrays)
    bundle = M0ArtifactManifest.descriptor_bundle_digest_for(descriptors)
    payload_digest = _sha256(
        b"".join(
            _ARRAY_NAMES[role].encode("ascii") + b"\0" + array.tobytes(order="C")
            for role, array in ordered_arrays
        )
    )
    if configuration.expected_array_payload_digests.get(family.value) != payload_digest:
        raise M0TrainingError("computed array payload does not match pinned configuration")
    schema = (
        registry.synthetic_family.metadata_control_schema
        if family is M0ModelFamily.METADATA_CONTROL
        else registry.synthetic_family.schema
    )
    if schema is None:
        raise M0TrainingError("metadata schema is absent")
    projection = candidates.population_projection(
        registry, metadata=family is M0ModelFamily.METADATA_CONTROL
    )
    population_digest = _sha256(canonical_json_bytes(projection))
    if (
        family is not M0ModelFamily.METADATA_CONTROL
        and population_digest != configuration.candidate_population_projection_digest
    ):
        raise M0TrainingError("full selected population projection pin drift")
    candidate_universe = {
        "schema_version": 1,
        "candidate_universe_id": "w05-synthetic-development-candidate-universe-v1",
        "evidence_class": "synthetic_development",
        "feature_schema_hash": schema.schema_hash,
        "feature_cutoff_ts": "2026-08-01T00:00:00Z",
        "feature_names": list(feature_names),
        "candidate_fixture_id": candidates.fixture_id,
        "candidate_fixture_digest": candidates.fixture_digest,
        "query_fixture_id": configuration.query_fixture_id,
        "query_fixture_digest": configuration.query_fixture_digest,
        "candidate_population_projection_digest": population_digest,
        "query_population_projection_digest": configuration.query_population_projection_digest,
        "taxonomy_id": contract.taxonomy_id,
        "taxonomy_version": contract.taxonomy_version,
        "taxonomy_digest": contract.taxonomy_digest,
        "development_only": True,
        "protected": False,
        "recruitment_outcome": False,
        "external_expert_label": False,
        "production_claim": False,
        "candidates": list(projection),
    }
    universe_digest = _sha256(canonical_json_bytes(candidate_universe))
    lineage = _sha256(canonical_json_bytes([row["dependency_lineage_hash"] for row in projection]))
    identity = _identity(
        family, configuration, registry, contract, population_digest, lineage, payload_digest
    )
    manifest_payload: dict[str, Any] = {
        "schema_version": 1,
        "artifact_id": str(identity),
        "model_family": family.value,
        "feature_names": list(feature_names),
        "feature_schema_hash": schema.schema_hash,
        "feature_registry_id": registry.registry_id,
        "feature_registry_canonical_digest": registry.registry_digest,
        "feature_registry_decision_digest": registry.registry_digest,
        "feature_descriptor_digest": registry.synthetic_family.family_digest,
        "evidence_class": "synthetic_development",
        "taxonomy_id": contract.taxonomy_id,
        "taxonomy_version": contract.taxonomy_version,
        "taxonomy_digest": contract.taxonomy_digest,
        "configuration_digest": configuration.configuration_digest,
        "fitting_population_id": "w05-synthetic-development-complete-rows-v1",
        "fitting_population_count": len(rows),
        "fitting_population_manifest_digest": population_digest,
        "candidate_universe_id": candidate_universe["candidate_universe_id"],
        "candidate_universe_count": len(rows),
        "candidate_universe_manifest_digest": universe_digest,
        "array_payload_digest": payload_digest,
        "array_descriptors": [item.model_dump(mode="json") for item in descriptors],
        "array_descriptor_bundle_digest": bundle,
        "model_id": f"w05-m0-{family.value}-v1",
        "model_version": "v1",
        "index_id": f"w05-m0-{family.value}-index-v1",
        "index_version": "v1",
        "lineage_identity": lineage,
        "deterministic_seed": configuration.deterministic_seed,
        "serialization_format": "numpy_npz",
        "pca_orientation_policy": "lowest_index_max_abs_pivot_non_negative"
        if family is M0ModelFamily.PCA
        else None,
        "pca_component_tie_order_policy": "explained_variance_descending_then_component_bytes"
        if family is M0ModelFamily.PCA
        else None,
    }
    manifest_payload["artifact_manifest_digest"] = M0ArtifactManifest.digest_for_payload(
        manifest_payload
    )
    # The shared contract is strict for Python-mode construction.  Canonical JSON is
    # the artifact boundary and therefore the appropriate public wire revalidation.
    manifest = M0ArtifactManifest.model_validate_json(canonical_json_bytes(manifest_payload))
    destination = _require_safe_destination(Path(artifact_directory))
    _write_immutable(
        destination / "arrays.npz",
        _npz_bytes([(_ARRAY_NAMES[role], array) for role, array in ordered_arrays]),
    )
    _write_immutable(
        destination / "configuration.json", canonical_json_bytes(configuration.canonical_mapping())
    )
    _write_immutable(
        destination / "candidate-universe.json", canonical_json_bytes(candidate_universe)
    )
    _write_immutable(
        destination / "manifest.json", canonical_json_bytes(manifest.model_dump(mode="json"))
    )
    return manifest


def run_synthetic_development_check(
    artifact_directory: str | Path,
    *,
    taxonomy: RoleTaxonomy,
    registry: FeatureRegistry,
    configuration: M0Configuration,
    candidates: M0DevelopmentCandidates,
    queries: M0DevelopmentQueries,
) -> dict[str, Any]:
    """Report constructed leave-one-query-out peer precision using the runtime scorer."""
    if not isinstance(candidates, M0DevelopmentCandidates) or not isinstance(
        queries, M0DevelopmentQueries
    ):
        raise M0TrainingError("development check requires typed fixture authorities")
    try:
        _validated_configuration(configuration)
        _validated_registry(registry)
        if not isinstance(taxonomy, RoleTaxonomy):
            raise M0TrainingError("a RoleTaxonomy authority is required")
        _validated_candidates(candidates, registry=registry, taxonomy=taxonomy)
        _validated_queries(queries, candidates=candidates, configuration=configuration)
    except ValueError as error:
        raise M0TrainingError("development-check authority drift") from error
    loaded = load_m0_artifact(
        artifact_directory,
        taxonomy=taxonomy,
        registry=registry,
        configuration=configuration,
        candidates=candidates,
        queries=queries,
    )
    rankings: list[str] = []
    scores: list[float] = []
    for query in queries.queries:
        player_id = UUID(query["player_id"])
        rows = loaded.score(player_id, limit=configuration.comparison_k)
        rankings.append(_sha256(canonical_json_bytes([str(row.player_id) for row in rows])))
        scores.append(
            sum(
                candidates.peer_groups[row.player_id] == query["relevant_peer_group"]
                for row in rows
            )
            / configuration.comparison_k
        )
    return {
        "mean_constructed_peer_group_precision_at_k": sum(scores) / len(scores),
        "ranking_digests": rankings,
        "k": configuration.comparison_k,
    }

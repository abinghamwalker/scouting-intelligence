"""Versioned deterministic feature-registry and materialisation boundaries."""

from .registry import (
    FeatureDefinition,
    FeatureFamily,
    FeatureRegistry,
    FeatureRegistryError,
    FeatureSchema,
    MaterializedFeatureRow,
    canonical_digest,
    canonical_json_bytes,
    load_feature_registry,
    load_synthetic_development_fixture,
    materialize_synthetic_row,
    materialize_w04_real_row,
)

__all__ = [
    "FeatureDefinition",
    "FeatureFamily",
    "FeatureRegistry",
    "FeatureRegistryError",
    "FeatureSchema",
    "MaterializedFeatureRow",
    "canonical_digest",
    "canonical_json_bytes",
    "load_feature_registry",
    "load_synthetic_development_fixture",
    "materialize_synthetic_row",
    "materialize_w04_real_row",
]

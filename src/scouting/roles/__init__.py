"""Contextual, responsibility-first football role taxonomy boundaries."""

from .taxonomy import (
    RoleTaxonomy,
    RoleTaxonomyError,
    canonical_digest,
    canonical_json_bytes,
    contextual_role_membership,
    load_role_taxonomy,
    load_synthetic_role_fixture,
)

__all__ = [
    "RoleTaxonomy",
    "RoleTaxonomyError",
    "canonical_digest",
    "canonical_json_bytes",
    "contextual_role_membership",
    "load_role_taxonomy",
    "load_synthetic_role_fixture",
]

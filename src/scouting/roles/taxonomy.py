"""Deterministic contextual membership for the W05 responsibility taxonomy.

This module never assigns a permanent player role.  A membership is calculated for
one explicit player and context using only the supplied, declared responsibility
evidence and an optional admitted contextual source-label prior.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID

from scouting.contracts.m0 import (
    ContextualRoleMembership,
    FootballResponsibilityTaxonomy,
    RoleMembershipProbability,
)


class RoleTaxonomyError(ValueError):
    """Raised when taxonomy content or contextual membership is not exact."""


_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "taxonomy_id",
        "taxonomy_version",
        "canonical_order",
        "expert_validation_status",
        "external_expert_evidence",
        "claim",
        "exemplar_notice",
        "responsibilities",
        "roles",
        "deterministic_mappings",
        "taxonomy_digest",
    }
)
_RESPONSIBILITY_KEYS = frozenset({"code", "label", "description"})
_ROLE_KEYS = frozenset({"code", "label", "responsibility_codes"})
_MAPPING_KEYS = frozenset({"source_label", "role_code"})
_FIXTURE_KEYS = frozenset(
    {
        "fixture_id",
        "fixture_version",
        "taxonomy_id",
        "taxonomy_version",
        "taxonomy_digest",
        "feature_fixture_id",
        "feature_fixture_digest",
        "claim",
        "rows",
        "fixture_digest",
    }
)
_FIXTURE_ROW_KEYS = frozenset(
    {
        "player_id",
        "context_id",
        "feature_cutoff_ts",
        "source_label_prior",
        "responsibility_evidence",
        "expected_memberships",
    }
)
_MEMBERSHIP_KEYS = frozenset({"role_code", "probability"})

_CANONICAL_ORDER = "responsibility_code_role_code_source_label"
_EXPERT_STATUS = "NOT_PERFORMED"
_CLAIM = "synthetic_development_taxonomy_only"
_EXEMPLAR_NOTICE = (
    "Exemplars may be an additional retrieval query signal but never replace the "
    "falsifiable responsibility taxonomy."
)
_ACCEPTED_TAXONOMY_IDENTITY = (
    "w05-football-responsibility-taxonomy-v1",
    "v1",
    "59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097",
)
_ACCEPTED_FIXTURE_IDENTITY = (
    "w05-synthetic-development-roles-v1",
    "v1",
    "d087269c83342051fe0274641d91ac1598963af88fda81bf7d5e95916f389b67",
)


def canonical_json_bytes(value: Any) -> bytes:
    """Return the compact, sorted-key JSON representation used for all digests."""
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


def canonical_digest(value: Mapping[str, Any], digest_key: str) -> str:
    """Hash a mapping after excluding exactly its self-referential digest."""
    if digest_key not in value:
        raise RoleTaxonomyError(f"missing {digest_key}")
    payload = dict(value)
    payload.pop(digest_key)
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _require_exact_keys(value: Mapping[str, Any], expected: frozenset[str], context: str) -> None:
    actual = frozenset(value)
    if actual != expected:
        raise RoleTaxonomyError(
            f"{context} keys must be exact; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _require_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise RoleTaxonomyError(f"{context} must be a non-empty string")
    return value


def _require_sha256(value: object, context: str) -> str:
    text = _require_string(value, context)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise RoleTaxonomyError(f"{context} must be a lowercase SHA-256 digest")
    return text


def _mapping(value: object, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise RoleTaxonomyError(f"{context} must be an object")
    return value


def _load_exact_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RoleTaxonomyError(f"{path} is not JSON") from error
    if not isinstance(value, dict):
        raise RoleTaxonomyError(f"{path} root must be an object")
    if raw != canonical_json_bytes(value) + b"\n":
        raise RoleTaxonomyError(f"{path} must use exact compact canonical JSON bytes")
    return value


@dataclass(frozen=True)
class RoleTaxonomy:
    """Validated taxonomy content plus its explicitly bounded claims."""

    contract: FootballResponsibilityTaxonomy
    canonical_order: str
    expert_validation_status: str
    external_expert_evidence: tuple[object, ...]
    claim: str
    exemplar_notice: str

    @property
    def taxonomy_id(self) -> str:
        return self.contract.taxonomy_id

    @property
    def taxonomy_version(self) -> str:
        return self.contract.taxonomy_version

    @property
    def taxonomy_digest(self) -> str:
        return self.contract.taxonomy_digest


def load_role_taxonomy(path: str | Path) -> RoleTaxonomy:
    """Load a canonical responsibility taxonomy and reject semantic substitutions."""
    value = _load_exact_json(Path(path))
    _require_exact_keys(value, _ROOT_KEYS, "role taxonomy")
    if canonical_digest(value, "taxonomy_digest") != value["taxonomy_digest"]:
        raise RoleTaxonomyError("taxonomy_digest must equal the canonical taxonomy SHA-256")
    if (
        value["taxonomy_id"],
        value["taxonomy_version"],
        value["taxonomy_digest"],
    ) != _ACCEPTED_TAXONOMY_IDENTITY:
        raise RoleTaxonomyError("taxonomy accepted-identity mismatch")
    if value["canonical_order"] != _CANONICAL_ORDER:
        raise RoleTaxonomyError("taxonomy canonical_order is not the declared v1 order")
    if value["expert_validation_status"] != _EXPERT_STATUS:
        raise RoleTaxonomyError("taxonomy expert_validation_status must be NOT_PERFORMED")
    if value["external_expert_evidence"] != []:
        raise RoleTaxonomyError("taxonomy external_expert_evidence must be empty")
    if value["claim"] != _CLAIM:
        raise RoleTaxonomyError("taxonomy claim must remain synthetic_development_taxonomy_only")
    if value["exemplar_notice"] != _EXEMPLAR_NOTICE:
        raise RoleTaxonomyError("taxonomy exemplar notice must retain the falsifiability boundary")
    raw_responsibilities = value["responsibilities"]
    raw_roles = value["roles"]
    raw_mappings = value["deterministic_mappings"]
    if not all(isinstance(item, dict) for item in raw_responsibilities):
        raise RoleTaxonomyError("taxonomy responsibilities must be objects")
    if not all(isinstance(item, dict) for item in raw_roles):
        raise RoleTaxonomyError("taxonomy roles must be objects")
    if not all(isinstance(item, dict) for item in raw_mappings):
        raise RoleTaxonomyError("taxonomy deterministic mappings must be objects")
    for item in raw_responsibilities:
        _require_exact_keys(item, _RESPONSIBILITY_KEYS, "taxonomy responsibility")
    for item in raw_roles:
        _require_exact_keys(item, _ROLE_KEYS, "taxonomy role")
    for item in raw_mappings:
        _require_exact_keys(item, _MAPPING_KEYS, "taxonomy deterministic mapping")
    contract_payload = {
        **value,
        "external_expert_evidence": tuple(value["external_expert_evidence"]),
        "responsibilities": tuple(raw_responsibilities),
        "roles": tuple(
            {**item, "responsibility_codes": tuple(item["responsibility_codes"])}
            for item in raw_roles
        ),
        "deterministic_mappings": tuple(raw_mappings),
    }
    try:
        contract = FootballResponsibilityTaxonomy.model_validate(contract_payload)
    except ValueError as error:
        raise RoleTaxonomyError(str(error)) from error
    return RoleTaxonomy(
        contract=contract,
        canonical_order=_CANONICAL_ORDER,
        expert_validation_status=_EXPERT_STATUS,
        external_expert_evidence=(),
        claim=_CLAIM,
        exemplar_notice=_EXEMPLAR_NOTICE,
    )


def _evidence_decimal(value: object, responsibility_code: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise RoleTaxonomyError(f"responsibility evidence {responsibility_code} must be numeric")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise RoleTaxonomyError(
            f"responsibility evidence {responsibility_code} must be a valid decimal"
        ) from error
    if not result.is_finite() or result < 0:
        raise RoleTaxonomyError(
            f"responsibility evidence {responsibility_code} must be finite and non-negative"
        )
    return result


def contextual_role_membership(
    *,
    player_id: UUID,
    context_id: str,
    taxonomy: RoleTaxonomy,
    responsibility_evidence: Mapping[str, object],
    source_label_prior: str | None = None,
) -> ContextualRoleMembership:
    """Return one exact, ordered, contextual probability distribution.

    A declared responsibility contributes its supplied non-negative evidence to each
    role that declares it.  An admitted source label adds exactly one declared prior
    unit to its mapped role.  No other weights, labels, exemplars, or player history
    enter the calculation.
    """
    if not isinstance(player_id, UUID):
        raise RoleTaxonomyError("player_id must be a UUID")
    if not isinstance(context_id, str) or not context_id:
        raise RoleTaxonomyError("context_id is mandatory and must be a non-empty string")
    if not isinstance(responsibility_evidence, Mapping):
        raise RoleTaxonomyError("responsibility_evidence must be a mapping")
    declared_responsibilities = {item.code for item in taxonomy.contract.responsibilities}
    unknown = set(responsibility_evidence) - declared_responsibilities
    if unknown:
        raise RoleTaxonomyError(f"unknown responsibility evidence codes: {sorted(unknown)}")
    evidence = {
        code: _evidence_decimal(value, code) for code, value in responsibility_evidence.items()
    }
    mapped_role: str | None = None
    if source_label_prior is not None:
        if not isinstance(source_label_prior, str) or not source_label_prior:
            raise RoleTaxonomyError("source_label_prior must be a non-empty admitted label or null")
        mappings = {
            mapping.source_label: mapping.role_code
            for mapping in taxonomy.contract.deterministic_mappings
        }
        if source_label_prior not in mappings:
            raise RoleTaxonomyError("source_label_prior is not declared by the taxonomy")
        mapped_role = mappings[source_label_prior]
    scores = {
        role.code: sum(
            (evidence.get(code, Decimal()) for code in role.responsibility_codes), Decimal()
        )
        + (Decimal(1) if role.code == mapped_role else Decimal())
        for role in taxonomy.contract.roles
    }
    total = sum(scores.values(), Decimal())
    if total == 0:
        raise RoleTaxonomyError(
            "all-zero responsibility evidence without an admitted prior fails closed"
        )
    quantum = Decimal("0.0000000000000001")
    ordered_codes = sorted(scores)
    probabilities: list[RoleMembershipProbability] = []
    remaining = Decimal(1)
    for code in ordered_codes[:-1]:
        probability = (scores[code] / total).quantize(quantum, rounding=ROUND_DOWN)
        remaining -= probability
        probabilities.append(
            RoleMembershipProbability(role_code=code, probability=float(probability))
        )
    probabilities.append(
        RoleMembershipProbability(role_code=ordered_codes[-1], probability=float(remaining))
    )
    membership = ContextualRoleMembership(
        player_id=player_id,
        context_id=context_id,
        taxonomy_id=taxonomy.taxonomy_id,
        taxonomy_version=taxonomy.taxonomy_version,
        taxonomy_digest=taxonomy.taxonomy_digest,
        memberships=tuple(probabilities),
    )
    membership.require_matching_taxonomy(taxonomy.contract)
    return membership


def load_synthetic_role_fixture(
    path: str | Path, taxonomy: RoleTaxonomy
) -> tuple[Mapping[str, Any], ...]:
    """Load and reproduce every synthetic contextual membership fixture row."""
    value = _load_exact_json(Path(path))
    _require_exact_keys(value, _FIXTURE_KEYS, "synthetic role fixture")
    if canonical_digest(value, "fixture_digest") != value["fixture_digest"]:
        raise RoleTaxonomyError("role fixture_digest must equal canonical fixture SHA-256")
    if (
        value["fixture_id"],
        value["fixture_version"],
        value["fixture_digest"],
    ) != _ACCEPTED_FIXTURE_IDENTITY:
        raise RoleTaxonomyError("role fixture accepted-identity mismatch")
    if (
        value["taxonomy_id"],
        value["taxonomy_version"],
        value["taxonomy_digest"],
    ) != (taxonomy.taxonomy_id, taxonomy.taxonomy_version, taxonomy.taxonomy_digest):
        raise RoleTaxonomyError("role fixture taxonomy identity mismatch")
    _require_string(value["feature_fixture_id"], "feature_fixture_id")
    _require_sha256(value["feature_fixture_digest"], "feature_fixture_digest")
    if value["claim"] != "synthetic_development_membership_fixture_only":
        raise RoleTaxonomyError("role fixture must remain synthetic-development-only")
    rows = value["rows"]
    if not isinstance(rows, list) or not rows:
        raise RoleTaxonomyError("role fixture rows must be a non-empty list")
    observed: list[Mapping[str, Any]] = []
    for row in rows:
        row = _mapping(row, "role fixture row")
        _require_exact_keys(row, _FIXTURE_ROW_KEYS, "role fixture row")
        try:
            player_id = UUID(_require_string(row["player_id"], "role fixture player_id"))
        except ValueError as error:
            raise RoleTaxonomyError("role fixture player_id must be a UUID") from error
        _require_string(row["feature_cutoff_ts"], "role fixture feature_cutoff_ts")
        source_label = row["source_label_prior"]
        if source_label is not None:
            _require_string(source_label, "role fixture source_label_prior")
        evidence = _mapping(row["responsibility_evidence"], "role fixture evidence")
        membership = contextual_role_membership(
            player_id=player_id,
            context_id=_require_string(row["context_id"], "role fixture context_id"),
            taxonomy=taxonomy,
            responsibility_evidence=evidence,
            source_label_prior=source_label,
        )
        expected = row["expected_memberships"]
        if not isinstance(expected, list) or not expected:
            raise RoleTaxonomyError("role fixture expected_memberships must be a non-empty list")
        if any(not isinstance(item, dict) for item in expected):
            raise RoleTaxonomyError("role fixture expected memberships must be objects")
        for item in expected:
            _require_exact_keys(item, _MEMBERSHIP_KEYS, "role fixture expected membership")
        expected_wire = tuple(
            RoleMembershipProbability(role_code=item["role_code"], probability=item["probability"])
            for item in expected
        )
        if membership.memberships != expected_wire:
            raise RoleTaxonomyError("role fixture expected memberships do not reproduce inference")
        observed.append(row)
    return tuple(observed)


__all__ = [
    "RoleTaxonomy",
    "RoleTaxonomyError",
    "canonical_digest",
    "canonical_json_bytes",
    "contextual_role_membership",
    "load_role_taxonomy",
    "load_synthetic_role_fixture",
]

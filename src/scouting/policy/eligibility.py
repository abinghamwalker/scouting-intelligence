"""Synthetic-only data-rights and strict-before temporal eligibility."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]


@dataclass(frozen=True, slots=True)
class EligibilityDecision:
    """Admission outcome for one evidence fact."""

    admitted: bool
    reason_code: str


def _mapping(value: object, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping")
    return cast(Mapping[str, Any], value)


class SyntheticRightsPolicy:
    """Enforce the frozen non-exportable W03 synthetic classification."""

    def __init__(self, *, policy_id: str, classification: str) -> None:
        self.policy_id = policy_id
        self.classification = classification

    @classmethod
    def from_path(cls, path: Path) -> SyntheticRightsPolicy:
        """Load and validate the frozen synthetic data-rights boundary."""
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        root = _mapping(raw, context="data rights policy")
        classification = _mapping(
            root.get("authorised_classification"),
            context="authorised classification",
        )
        export = _mapping(root.get("export"), context="export policy")
        if root.get("policy_id") != "w03-synthetic-data-rights-v1":
            raise ValueError("unexpected data-rights policy id")
        if root.get("default") != "deny":
            raise ValueError("data-rights policy must remain deny by default")
        if classification.get("id") != "w03_synthetic_generated":
            raise ValueError("unexpected W03 synthetic classification")
        if any(export.get(field) is not False for field in export):
            raise ValueError("W03 data-rights policy cannot permit export")
        return cls(
            policy_id=cast(str, root["policy_id"]),
            classification=cast(str, classification["id"]),
        )

    def decide_fact(
        self,
        *,
        classification: str | None,
        observed_at: datetime,
        available_at: datetime | None,
        cutoff: datetime,
        generated: bool,
        identity_unambiguous: bool,
    ) -> EligibilityDecision:
        """Admit only generated, unambiguous, strictly pre-cutoff evidence."""
        if classification != self.classification:
            return EligibilityDecision(False, "rights_classification_denied")
        if not generated:
            return EligibilityDecision(False, "not_reviewed_synthetic_generation")
        if available_at is None:
            return EligibilityDecision(False, "missing_temporal_evidence")
        if observed_at >= cutoff:
            return EligibilityDecision(False, "post_cutoff_observation")
        if available_at >= cutoff:
            return EligibilityDecision(False, "post_cutoff_availability")
        if not identity_unambiguous:
            return EligibilityDecision(False, "identity_review_required")
        return EligibilityDecision(True, "eligible")

    def require_export_allowed(self) -> None:
        """W03 export is frozen off for every actor and object."""
        raise PermissionError("action denied")

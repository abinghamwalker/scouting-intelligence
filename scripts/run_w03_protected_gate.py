"""Master-only broker for the frozen W03 protected synthetic serving gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from scouting.contracts import DependencyKind
from scouting.policy import SyntheticRightsPolicy
from scouting.serving import (
    RetrievalPresentationProfile,
    SyntheticArtifactCatalog,
    SyntheticDomainSnapshot,
    SyntheticServingService,
)
from scouting.sources.synthetic import load_synthetic_fixture

ROOT = Path(__file__).resolve().parents[1]
PROTECTED_ROOT = ROOT / "tests/fixtures/synthetic/protected"


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _protected_artifacts() -> tuple[
    SyntheticArtifactCatalog,
    dict[str, Any],
]:
    fixture = load_synthetic_fixture(
        PROTECTED_ROOT / "domain.json",
        PROTECTED_ROOT / "expected_retrieval.json",
        expected_partition="protected_test",
    )
    expected_result = fixture.retrieval_result
    if len(expected_result.candidates) != 1:
        raise ValueError("protected fixture must contain one expected candidate")
    expected_document = json.loads(
        (PROTECTED_ROOT / "expected_retrieval.json").read_text(encoding="utf-8")
    )
    expected_explanations = expected_document["payload"]["explanations"]
    if not isinstance(expected_explanations, list) or len(expected_explanations) != 1:
        raise ValueError("protected fixture must contain one expected explanation")
    expected_explanation = expected_explanations[0]
    if not isinstance(expected_explanation, dict):
        raise ValueError("protected expected explanation is invalid")
    explanation_summary = expected_explanation.get("summary")
    if not isinstance(explanation_summary, str):
        raise ValueError("protected expected explanation summary is invalid")
    expected_candidate = expected_result.candidates[0]
    dependencies = {
        dependency.kind: dependency
        for dependency in expected_result.temporal_evidence.dependency_lineage.dependencies
    }
    source = dependencies[DependencyKind.SOURCE_MANIFEST]
    feature = dependencies[DependencyKind.FEATURE_SCHEMA]
    model = dependencies[DependencyKind.MODEL_ARTIFACT]
    index = dependencies[DependencyKind.RETRIEVAL_INDEX]
    return (
        SyntheticArtifactCatalog(
            source_manifest_id=source.dependency_id,
            feature_schema_id=feature.dependency_id,
            feature_schema_hash=feature.digest,
            model_artifact_id=model.dependency_id,
            model_artifact_digest=model.digest,
            model_version=expected_result.model_version,
            retrieval_index_id=index.dependency_id,
            retrieval_index_digest=index.digest,
            index_version=expected_result.index_version,
            presentation_profile=RetrievalPresentationProfile(
                dimensions=expected_candidate.evidence_dimensions,
                candidate_confidence=expected_candidate.confidence,
                candidate_reason_codes=expected_candidate.reason_codes,
                explanation_reason_codes=tuple(expected_explanation["reason_codes"]),
                explanation_template=explanation_summary,
            ),
            source_observed_at=source.observed_at,
            source_available_at=source.available_at,
            feature_schema_observed_at=feature.observed_at,
            feature_schema_available_at=feature.available_at,
            model_artifact_observed_at=model.observed_at,
            model_artifact_available_at=model.available_at,
            retrieval_index_observed_at=index.observed_at,
            retrieval_index_available_at=index.available_at,
        ),
        {
            "fixture": fixture,
            "expected_result": expected_result.model_dump(mode="json"),
            "expected_explanations": expected_explanations,
        },
    )


def main() -> int:
    """Run the preregistered comparison and disclose only bounded gate evidence."""
    artifacts, expected = _protected_artifacts()
    fixture = expected["fixture"]
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    snapshot = SyntheticDomainSnapshot.from_path(
        "domain.json",
        allowed_fixture_root=PROTECTED_ROOT,
        expected_partition="protected_test",
        rights_policy=rights,
    )
    service = SyntheticServingService(snapshot, artifacts=artifacts)
    first = service.retrieve(fixture.role_brief, fixture.retrieval_request)
    second = service.retrieve(fixture.role_brief, fixture.retrieval_request)

    actual_result = None if first.result is None else first.result.model_dump(mode="json")
    second_result = None if second.result is None else second.result.model_dump(mode="json")
    actual_explanations = [
        {
            "player_id": str(explanation.player_id),
            "claim_boundary": explanation.claim_boundary,
            "reason_codes": list(explanation.reason_codes),
            "summary": explanation.summary,
        }
        for explanation in first.explanations
    ]
    expected_candidate_ids = {
        candidate.player_id for candidate in fixture.retrieval_result.candidates
    }
    actual_candidate_ids = (
        set()
        if first.result is None
        else {candidate.player_id for candidate in first.result.candidates}
    )
    expected_rejected = {rejected.fact_id: rejected.reason for rejected in fixture.rejected_facts}
    actual_rejected = {
        rejected.fact_id: rejected.reason_code for rejected in first.rejected_evidence
    }
    admitted_ids = {fact.fact_id for fact in fixture.admitted_facts}
    post_cutoff_ids = {
        rejected.fact_id
        for rejected in fixture.rejected_facts
        if rejected.reason in {"post_cutoff_observation", "post_cutoff_availability"}
    }

    checks = {
        "fixture_contract_valid": True,
        "protected_partition_selected": snapshot.partition == "protected_test",
        "serving_available": first.status == "available" and first.result is not None,
        "candidate_identity_match": actual_candidate_ids == expected_candidate_ids,
        "result_contract_match": actual_result == expected["expected_result"],
        "explanations_match": actual_explanations == expected["expected_explanations"],
        "admitted_fact_set_match": set(first.admitted_fact_ids) == admitted_ids,
        "rejected_fact_reasons_match": actual_rejected == expected_rejected,
        "post_cutoff_admitted_zero": not (set(first.admitted_fact_ids) & post_cutoff_ids),
        "repeat_result_stable": actual_result == second_result,
    }
    passed = all(checks.values())
    report = {
        "schema_version": 1,
        "gate_id": "W03-PROTECTED-SYNTHETIC-01",
        "partition": "PROTECTED_TEST",
        "claim_boundary": "foundation_properties_only",
        "checks": checks,
        "result_digest": None if actual_result is None else _digest(actual_result),
        "expected_result_digest": _digest(expected["expected_result"]),
        "repeat_result_digest": None if second_result is None else _digest(second_result),
        "decision": "PASS" if passed else "REWORK",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

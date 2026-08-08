from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from scouting.sources.synthetic import (
    FixtureValidationError,
    _parse_facts,
    canonical_payload_digest,
    load_synthetic_fixture,
)

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic"
DEVELOPMENT_DOMAIN = FIXTURE_ROOT / "domain.json"
DEVELOPMENT_EXPECTED = FIXTURE_ROOT / "expected_retrieval.json"
PROTECTED_DOMAIN = FIXTURE_ROOT / "protected" / "domain.json"
PROTECTED_EXPECTED = FIXTURE_ROOT / "protected" / "expected_retrieval.json"


def _read_json(path: Path) -> dict[str, Any]:
    decoded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def _write_envelope(path: Path, document: dict[str, Any]) -> None:
    payload = document["payload"]
    assert isinstance(payload, dict)
    manifest = document["manifest"]
    assert isinstance(manifest, dict)
    manifest["content_digest"] = canonical_payload_digest(payload)
    path.write_text(json.dumps(document), encoding="utf-8")


def test_development_fixture_is_contract_valid_and_deterministic() -> None:
    first = load_synthetic_fixture(
        DEVELOPMENT_DOMAIN,
        DEVELOPMENT_EXPECTED,
        expected_partition="development",
    )
    second = load_synthetic_fixture(
        DEVELOPMENT_DOMAIN,
        DEVELOPMENT_EXPECTED,
        expected_partition="development",
    )

    assert first == second
    assert first.fixture_id == "w03-synthetic-development-v1"
    assert first.partition == "development"
    assert (
        first.manifest_digest == "03972808bd6628dd4ffb66a975108bb15f649a0b778e493c85874ef107953e2a"
    )
    assert first.expected_manifest_digest == (
        "f0948134aa0b02595e2974ff6ca264496db401c68d937bf8b8d594561f57e0e9"
    )
    assert [str(fact.fact_id) for fact in first.admitted_facts] == [
        "50000000-0000-4000-8000-000000000101",
        "50000000-0000-4000-8000-000000000102",
        "50000000-0000-4000-8000-000000000104",
        "50000000-0000-4000-8000-000000000103",
    ]
    assert first.retrieval_result.candidates[0].player_id == first.shortlist_entry.player_id
    assert first.retrieval_result.claim_boundary == "resemblance_only"


def test_ambiguous_identity_is_retained_without_a_guessed_canonical_player() -> None:
    fixture = load_synthetic_fixture(DEVELOPMENT_DOMAIN, DEVELOPMENT_EXPECTED)
    domain = _read_json(DEVELOPMENT_DOMAIN)
    identity_records = domain["payload"]["identity_records"]

    assert fixture.ambiguous_source_ids == ("syn-dev-ambiguous-fullback",)
    ambiguous = next(
        identity
        for identity in identity_records
        if identity["source_id"] == fixture.ambiguous_source_ids[0]
    )
    assert ambiguous["resolution_status"] == "review_required"
    assert ambiguous["canonical_player_id"] is None
    assert len(ambiguous["candidate_player_ids"]) == 2


def test_late_fact_is_attributable_and_future_or_missing_facts_are_not_admitted() -> None:
    fixture = load_synthetic_fixture(DEVELOPMENT_DOMAIN, DEVELOPMENT_EXPECTED)
    late = next(fact for fact in fixture.admitted_facts if fact.arrival_class == "late")

    assert late.fact_id == UUID("50000000-0000-4000-8000-000000000103")
    assert late.observed_at < late.available_at < fixture.decision_cutoff_ts
    assert {(str(fact.fact_id), fact.reason) for fact in fixture.rejected_facts} == {
        (
            "50000000-0000-4000-8000-000000000105",
            "post_cutoff_availability",
        ),
        (
            "50000000-0000-4000-8000-000000000106",
            "missing_temporal_evidence",
        ),
    }
    admitted_ids = {str(fact.fact_id) for fact in fixture.admitted_facts}
    assert "50000000-0000-4000-8000-000000000105" not in admitted_ids
    assert "50000000-0000-4000-8000-000000000106" not in admitted_ids


def test_fact_at_exact_cutoff_fails_closed_even_if_marked_for_admission(
    tmp_path: Path,
) -> None:
    document = _read_json(DEVELOPMENT_DOMAIN)
    facts = document["payload"]["facts"]
    future = next(
        fact for fact in facts if fact["fact_id"] == "50000000-0000-4000-8000-000000000105"
    )
    future["expected_admission"] = True
    mutated_domain = tmp_path / "domain.json"
    _write_envelope(mutated_domain, document)

    with pytest.raises(
        FixtureValidationError,
        match="cannot expect admission at or after the cutoff",
    ):
        load_synthetic_fixture(mutated_domain, DEVELOPMENT_EXPECTED)


@pytest.mark.parametrize(
    "observed_at",
    [
        "2026-03-01T00:00:00Z",
        "2026-03-01T00:00:01Z",
    ],
)
def test_observation_at_or_after_cutoff_fails_closed_even_if_available_earlier(
    tmp_path: Path,
    observed_at: str,
) -> None:
    document = _read_json(DEVELOPMENT_DOMAIN)
    facts = document["payload"]["facts"]
    admitted = next(
        fact for fact in facts if fact["fact_id"] == "50000000-0000-4000-8000-000000000101"
    )
    admitted["observed_at"] = observed_at
    mutated_domain = tmp_path / "domain.json"
    _write_envelope(mutated_domain, document)

    with pytest.raises(
        FixtureValidationError,
        match="cannot expect admission for an observation at or after the cutoff",
    ):
        load_synthetic_fixture(mutated_domain, DEVELOPMENT_EXPECTED)


def test_observation_cutoff_rejection_reason_is_distinct_from_availability() -> None:
    document = _read_json(DEVELOPMENT_DOMAIN)
    facts = document["payload"]["facts"]
    raw_fact = next(
        fact for fact in facts if fact["fact_id"] == "50000000-0000-4000-8000-000000000101"
    ).copy()
    raw_fact["observed_at"] = "2026-03-01T00:00:00Z"
    raw_fact["expected_admission"] = False

    admitted, rejected = _parse_facts(
        [raw_fact],
        cutoff=datetime.fromisoformat("2026-03-01T00:00:00+00:00"),
        context="observation-cutoff-test",
    )

    assert admitted == ()
    assert len(rejected) == 1
    assert rejected[0].reason == "post_cutoff_observation"


def test_manifest_digest_detects_silent_fixture_mutation(tmp_path: Path) -> None:
    document = _read_json(DEVELOPMENT_DOMAIN)
    document["payload"]["players"][0]["display_name"] = "Silently changed"
    mutated_domain = tmp_path / "domain.json"
    mutated_domain.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(FixtureValidationError, match="content digest mismatch"):
        load_synthetic_fixture(mutated_domain, DEVELOPMENT_EXPECTED)


def test_unknown_rights_classification_is_denied(tmp_path: Path) -> None:
    document = _read_json(DEVELOPMENT_DOMAIN)
    document["manifest"]["classification"] = "unknown"
    mutated_domain = tmp_path / "domain.json"
    mutated_domain.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(FixtureValidationError, match="not classified"):
        load_synthetic_fixture(mutated_domain, DEVELOPMENT_EXPECTED)


def test_protected_fixture_is_separate_contract_valid_and_digest_distinct() -> None:
    development = load_synthetic_fixture(DEVELOPMENT_DOMAIN, DEVELOPMENT_EXPECTED)
    protected = load_synthetic_fixture(
        PROTECTED_DOMAIN,
        PROTECTED_EXPECTED,
        expected_partition="protected_test",
    )

    assert protected.fixture_id == "w03-synthetic-protected-v1"
    assert protected.partition == "protected_test"
    assert protected.manifest_digest == (
        "51f56f2bc9d88196e1b37b6f28c9879a1cdc4ee4db5727a955c5c188b9bfbd7f"
    )
    assert protected.expected_manifest_digest == (
        "9c3c0b65d53e8a4fefdd160ba38b1bf016671cf0aaa97d7fdc08c3a238b4fdf6"
    )
    assert protected.manifest_digest != development.manifest_digest
    assert protected.expected_manifest_digest != development.expected_manifest_digest
    assert protected.role_brief.role_brief_id != development.role_brief.role_brief_id
    assert protected.retrieval_result.candidates[0].player_id == protected.shortlist_entry.player_id

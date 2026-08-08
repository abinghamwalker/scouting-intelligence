"""Focused adversarial coverage for W05 contextual responsibility membership."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from scouting.contracts.m0 import FootballResponsibilityTaxonomy
from scouting.roles.taxonomy import (
    RoleTaxonomyError,
    canonical_digest,
    canonical_json_bytes,
    contextual_role_membership,
    load_role_taxonomy,
    load_synthetic_role_fixture,
)

ROOT = Path(__file__).parents[2]
TAXONOMY_PATH = ROOT / "configs/roles/w05-football-responsibility-taxonomy-v1.json"
FEATURE_FIXTURE_PATH = ROOT / "tests/fixtures/w05/synthetic-development-features-v1.json"
ROLE_FIXTURE_PATH = ROOT / "tests/fixtures/w05/synthetic-development-roles-v1.json"
PLAYER = UUID("10000000-0000-4000-8000-000000000001")


def test_taxonomy_and_fixture_are_exact_self_verifying_canonical_bytes() -> None:
    taxonomy_raw = json.loads(TAXONOMY_PATH.read_bytes())
    fixture_raw = json.loads(ROLE_FIXTURE_PATH.read_bytes())
    assert TAXONOMY_PATH.read_bytes() == canonical_json_bytes(taxonomy_raw) + b"\n"
    assert ROLE_FIXTURE_PATH.read_bytes() == canonical_json_bytes(fixture_raw) + b"\n"
    assert canonical_digest(taxonomy_raw, "taxonomy_digest") == taxonomy_raw["taxonomy_digest"]
    assert canonical_digest(fixture_raw, "fixture_digest") == fixture_raw["fixture_digest"]


def test_fixture_aligns_to_every_complete_synthetic_feature_player_window() -> None:
    taxonomy = load_role_taxonomy(TAXONOMY_PATH)
    rows = load_synthetic_role_fixture(ROLE_FIXTURE_PATH, taxonomy)
    features = json.loads(FEATURE_FIXTURE_PATH.read_bytes())
    assert {(row["player_id"], row["feature_cutoff_ts"]) for row in rows} == {
        (row["player_id"], row["feature_cutoff_ts"]) for row in features["complete_rows"]
    }


def test_membership_is_repeatable_sorted_and_contextual() -> None:
    taxonomy = load_role_taxonomy(TAXONOMY_PATH)
    first = contextual_role_membership(
        player_id=PLAYER,
        context_id="window-one",
        taxonomy=taxonomy,
        responsibility_evidence={"progress_through_pressure": 6, "retain_recycle_possession": 2},
        source_label_prior="CENTRAL_MIDFIELD",
    )
    repeated = contextual_role_membership(
        player_id=PLAYER,
        context_id="window-one",
        taxonomy=taxonomy,
        responsibility_evidence={"progress_through_pressure": 6, "retain_recycle_possession": 2},
        source_label_prior="CENTRAL_MIDFIELD",
    )
    other_context = contextual_role_membership(
        player_id=PLAYER,
        context_id="window-two",
        taxonomy=taxonomy,
        responsibility_evidence={"threaten_penalty_area": 8, "secure_first_contact": 4},
    )
    assert first == repeated
    assert [item.role_code for item in first.memberships] == sorted(
        item.role_code for item in first.memberships
    )
    assert sum(item.probability for item in first.memberships) == pytest.approx(1.0)
    assert first.memberships != other_context.memberships
    assert first.context_id != other_context.context_id


@pytest.mark.parametrize(
    ("evidence", "prior"),
    [({}, None), ({"unknown_responsibility": 1}, None), ({"create_chances": -1}, None)],
)
def test_membership_fails_closed_for_absent_unknown_or_negative_evidence(
    evidence: dict[str, int], prior: str | None
) -> None:
    with pytest.raises(RoleTaxonomyError):
        contextual_role_membership(
            player_id=PLAYER,
            context_id="window",
            taxonomy=load_role_taxonomy(TAXONOMY_PATH),
            responsibility_evidence=evidence,
            source_label_prior=prior,
        )


def test_resigned_same_id_taxonomy_substitution_and_dangling_mapping_reject(tmp_path: Path) -> None:
    raw = json.loads(TAXONOMY_PATH.read_bytes())
    raw["roles"][0]["label"] = "altered contextual responsibilities"
    raw["taxonomy_digest"] = canonical_digest(raw, "taxonomy_digest")
    changed = tmp_path / "changed.json"
    changed.write_bytes(canonical_json_bytes(raw) + b"\n")
    with pytest.raises(RoleTaxonomyError, match="accepted-identity"):
        load_role_taxonomy(changed)

    raw = json.loads(TAXONOMY_PATH.read_bytes())
    raw["deterministic_mappings"][0]["role_code"] = "missing_role"
    raw["taxonomy_digest"] = canonical_digest(raw, "taxonomy_digest")
    dangling = tmp_path / "dangling.json"
    dangling.write_bytes(canonical_json_bytes(raw) + b"\n")
    with pytest.raises(RoleTaxonomyError):
        load_role_taxonomy(dangling)


def test_taxonomy_explicitly_has_no_expert_validation_or_permanent_player_label() -> None:
    taxonomy = load_role_taxonomy(TAXONOMY_PATH)
    assert taxonomy.expert_validation_status == "NOT_PERFORMED"
    assert taxonomy.external_expert_evidence == ()
    assert taxonomy.claim == "synthetic_development_taxonomy_only"
    assert "permanent" not in taxonomy.__dict__
    assert "never replace" in taxonomy.exemplar_notice


def test_loaded_contract_round_trips_and_recomputes_the_full_taxonomy_digest() -> None:
    taxonomy = load_role_taxonomy(TAXONOMY_PATH)
    round_tripped = FootballResponsibilityTaxonomy.model_validate(
        taxonomy.contract.model_dump(mode="python")
    )
    assert round_tripped == taxonomy.contract
    assert (
        FootballResponsibilityTaxonomy.digest_for_payload(taxonomy.contract.model_dump(mode="json"))
        == taxonomy.taxonomy_digest
    )


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("claim", "expert_validated", "claim"),
        ("exemplar_notice", "exemplars replace taxonomy", "exemplar notice"),
        ("expert_validation_status", "PERFORMED", "expert_validation_status"),
    ],
)
def test_resigned_claim_boundary_substitutions_fail_after_identity_repin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, replacement: str, message: str
) -> None:
    raw = json.loads(TAXONOMY_PATH.read_bytes())
    raw[field] = replacement
    raw["taxonomy_digest"] = canonical_digest(raw, "taxonomy_digest")
    changed = tmp_path / f"changed-{field}.json"
    changed.write_bytes(canonical_json_bytes(raw) + b"\n")
    import scouting.roles.taxonomy as taxonomy_module

    monkeypatch.setattr(
        taxonomy_module,
        "_ACCEPTED_TAXONOMY_IDENTITY",
        (raw["taxonomy_id"], raw["taxonomy_version"], raw["taxonomy_digest"]),
    )
    with pytest.raises(RoleTaxonomyError, match=message):
        load_role_taxonomy(changed)

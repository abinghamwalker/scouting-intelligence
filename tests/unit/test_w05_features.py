"""Focused adversarial checks for the bounded W05 feature registry."""

from __future__ import annotations

import ast
import hashlib
import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

import scouting.features.registry as feature_registry_module
from scouting.contracts.m0 import FeatureValueState
from scouting.features import (
    FeatureRegistryError,
    canonical_json_bytes,
    load_feature_registry,
    load_synthetic_development_fixture,
    materialize_synthetic_row,
    materialize_w04_real_row,
)
from scouting.features.registry import _W04_DEPENDENCIES, _W04_GOLD_PROJECTION, _W04_LINEAGE_HASH

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "configs/features/w05-m0-feature-registry-v1.json"
FIXTURE_PATH = ROOT / "tests/fixtures/w05/synthetic-development-features-v1.json"


def _load(path: Path) -> dict[str, object]:
    """Read one compact JSON proof object for controlled mutation."""
    value = json.loads(path.read_bytes())
    assert isinstance(value, dict)
    return value


def _write_canonical(path: Path, value: object) -> None:
    """Write the exact file wire format expected by the loader."""
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _rehash(value: dict[str, object], key: str) -> None:
    """Deliberately re-sign one self-verifying object for substitution probes."""
    payload = dict(value)
    payload.pop(key)
    value[key] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _resign_registry(value: dict[str, object]) -> None:
    """Re-sign every nested candidate hash to prove external pins are authoritative."""
    families = value["families"]
    assert isinstance(families, list)
    for family in families:
        assert isinstance(family, dict)
        for key in ("schema", "metadata_control_schema"):
            schema = family[key]
            if schema is not None:
                assert isinstance(schema, dict)
                _rehash(schema, "schema_hash")
        _rehash(family, "family_digest")
    _rehash(value, "registry_digest")


def _lineage(number: int = 99) -> dict[str, object]:
    """Return an exact local pre-cutoff dependency identity."""
    dependencies = [
        {
            "dependency_id": f"10000000-0000-4000-8000-{number:012d}",
            "digest": hashlib.sha256(f"lineage-{number}".encode()).hexdigest(),
            "observed_at": "2025-01-01T00:00:00Z",
            "available_at": "2025-01-02T00:00:00Z",
        }
    ]
    return {
        "lineage_hash": hashlib.sha256(canonical_json_bytes(dependencies)).hexdigest(),
        "dependencies": dependencies,
    }


@pytest.fixture
def registry():  # type: ignore[no-untyped-def]
    """Load the exact W05 registry for each isolated adversarial test."""
    return load_feature_registry(REGISTRY_PATH)


def test_registry_and_fixture_reproduce_digests_exact_bytes_and_order(registry) -> None:  # type: ignore[no-untyped-def]
    """The byte-level roots, W04 closure, schemas, and fixture all reproduce."""
    raw = REGISTRY_PATH.read_bytes()
    fixture_raw = FIXTURE_PATH.read_bytes()
    assert raw == canonical_json_bytes(_load(REGISTRY_PATH)) + b"\n"
    assert fixture_raw == canonical_json_bytes(_load(FIXTURE_PATH)) + b"\n"
    assert (
        registry.registry_digest
        == "c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644"
    )
    assert (
        registry.w04_family.schema.schema_hash
        == "cf8847f2b1f70ebf293ce90e48817e80a4e47b78316079bd88e8c2a80bc08127"
    )
    assert (
        registry.synthetic_family.schema.schema_hash
        == "1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f"
    )
    assert registry.synthetic_family.metadata_control_schema is not None
    assert registry.synthetic_family.metadata_control_schema.control_only is True
    assert tuple(item.name for item in registry.w04_family.schema.features) == (
        "action_count",
        "coordinate_known_action_count",
        "match_count",
        "resolved_possession_action_count",
    )
    rows = load_synthetic_development_fixture(FIXTURE_PATH, registry)
    assert len(rows) == 22
    assert len({row["constructed_development_peer_group"] for row in rows[:18]}) == 3


@pytest.mark.parametrize("mutation", ["unknown", "duplicate_order", "digest_drift", "reorder"])
def test_registry_rejects_unknown_duplicate_digest_and_reordered_content(
    tmp_path: Path, mutation: str
) -> None:
    """No re-signed or structurally ambiguous registry can be silently admitted."""
    value = _load(REGISTRY_PATH)
    families = value["families"]
    assert isinstance(families, list)
    synthetic = families[1]
    assert isinstance(synthetic, dict)
    schema = synthetic["schema"]
    assert isinstance(schema, dict)
    features = schema["features"]
    assert isinstance(features, list)
    if mutation == "unknown":
        synthetic["unknown_key"] = "forbidden"
    elif mutation == "duplicate_order":
        assert isinstance(features[1], dict)
        features[1]["order"] = 1
    elif mutation == "reorder":
        features[0], features[1] = features[1], features[0]
    else:
        value["registry_digest"] = "0" * 64
    path = tmp_path / "registry.json"
    _write_canonical(path, value)
    with pytest.raises(FeatureRegistryError):
        load_feature_registry(path)


@pytest.mark.parametrize(
    "attack", ["root_id", "family_crosswire", "w04_descriptor", "synthetic_claim"]
)
def test_fully_resigned_registry_substitutions_reject(tmp_path: Path, attack: str) -> None:
    """Independent accepted pins reject candidates even after every nested hash is renewed."""
    value = _load(REGISTRY_PATH)
    families = value["families"]
    assert isinstance(families, list)
    if attack == "root_id":
        value["registry_id"] = "attacker-resigned-registry"
    elif attack == "family_crosswire":
        assert isinstance(families[0], dict) and isinstance(families[1], dict)
        families[0]["family_id"], families[1]["family_id"] = (
            families[1]["family_id"],
            families[0]["family_id"],
        )
    elif attack == "w04_descriptor":
        assert isinstance(families[0], dict)
        schema = families[0]["schema"]
        assert isinstance(schema, dict) and isinstance(schema["features"], list)
        assert isinstance(schema["features"][0], dict)
        schema["features"][0]["unit"] = "goals"
    else:
        assert isinstance(families[1], dict)
        schema = families[1]["schema"]
        assert isinstance(schema, dict) and isinstance(schema["features"], list)
        assert isinstance(schema["features"][0], dict)
        schema["features"][0]["football_definition"] = "Wyscout production expert label"
    _resign_registry(value)
    path = tmp_path / "resigned.json"
    _write_canonical(path, value)
    with pytest.raises(FeatureRegistryError, match="accepted-identity|forbidden claim"):
        load_feature_registry(path)


def test_synthetic_fixture_states_and_materialization_are_deterministic(registry) -> None:  # type: ignore[no-untyped-def]
    """Observed zero and all absence states remain distinct across repeated calculation."""
    rows = load_synthetic_development_fixture(FIXTURE_PATH, registry)
    edge_rows = rows[-4:]
    states = {
        value.state
        for row in edge_rows
        for value in materialize_synthetic_row(row, registry).values
    }
    assert states >= {
        FeatureValueState.MISSING,
        FeatureValueState.SUPPRESSED,
        FeatureValueState.UNAVAILABLE,
        FeatureValueState.ZERO,
    }
    first = materialize_synthetic_row(rows[0], registry)
    second = materialize_synthetic_row(rows[0], registry)
    assert first == second
    assert all(value.state is not FeatureValueState.MISSING for value in first.values)


def test_synthetic_rejects_cutoff_equality_lineage_and_schema_substitution(
    tmp_path: Path,
    registry,  # type: ignore[no-untyped-def]
) -> None:
    """Temporal equality and identity changes fail closed rather than changing a result."""
    row = deepcopy(load_synthetic_development_fixture(FIXTURE_PATH, registry)[0])
    assert isinstance(row, dict)
    row["available_at"] = row["feature_cutoff_ts"]
    with pytest.raises(FeatureRegistryError, match="strictly before"):
        materialize_synthetic_row(row, registry)
    row = deepcopy(load_synthetic_development_fixture(FIXTURE_PATH, registry)[0])
    assert isinstance(row, dict)
    lineage = row["dependency_identity"]
    assert isinstance(lineage, dict)
    lineage["lineage_hash"] = "0" * 64
    with pytest.raises(FeatureRegistryError, match="lineage_hash"):
        materialize_synthetic_row(row, registry)
    fixture = _load(FIXTURE_PATH)
    fixture["family_id"] = "w05-w04-real-governed-bridge-v1"
    _rehash(fixture, "fixture_digest")
    path = tmp_path / "identity-swapped.json"
    _write_canonical(path, fixture)
    with pytest.raises(FeatureRegistryError, match="accepted-identity"):
        load_synthetic_development_fixture(path, registry)


def test_w04_exact_four_bridge_rejects_extended_or_post_cutoff_rows(registry) -> None:  # type: ignore[no-untyped-def]
    """The real bridge cannot add rates, copy authority, or admit post-cutoff data."""
    assert registry.w04_family.w04_authority is not None
    row: dict[str, object] = {
        **_W04_GOLD_PROJECTION,
        "evidence_class": "w04_real_governed",
        "w04_authority": dict(registry.w04_family.w04_authority),
        "dependency_identity": {
            "lineage_hash": _W04_LINEAGE_HASH,
            "dependencies": list(_W04_DEPENDENCIES),
        },
        "counts": {
            "action_count": 2,
            "coordinate_known_action_count": 2,
            "match_count": 1,
            "resolved_possession_action_count": 2,
        },
    }
    materialized = materialize_w04_real_row(row, registry)
    assert tuple(value.numeric_value for value in materialized.values) == (2.0, 2.0, 1.0, 2.0)
    expanded = deepcopy(row)
    assert isinstance(expanded["counts"], dict)
    expanded["counts"]["actions_per_90"] = 1
    with pytest.raises(FeatureRegistryError, match="exact accepted four"):
        materialize_w04_real_row(expanded, registry)
    fabricated = deepcopy(row)
    fabricated["player_id"] = "90000000-0000-4000-8000-000000000002"
    with pytest.raises(FeatureRegistryError, match="projection identity"):
        materialize_w04_real_row(fabricated, registry)
    reordered = deepcopy(row)
    assert isinstance(reordered["dependency_identity"], dict)
    dependencies = reordered["dependency_identity"]["dependencies"]
    assert isinstance(dependencies, list)
    dependencies.reverse()
    with pytest.raises(FeatureRegistryError, match="dependency envelope"):
        materialize_w04_real_row(reordered, registry)
    post_cutoff = deepcopy(row)
    post_cutoff["available_at_watermark"] = "2026-08-01T00:00:00Z"
    with pytest.raises(FeatureRegistryError, match="projection identity"):
        materialize_w04_real_row(post_cutoff, registry)


@pytest.mark.parametrize("substitution", [True, 1.0, False, 0, 2])
def test_w04_gold_row_count_requires_non_boolean_integer_one(
    registry,
    substitution: object,  # type: ignore[no-untyped-def]
) -> None:
    """JSON booleans and floats cannot satisfy the accepted one-row identity pin."""
    assert registry.w04_family.w04_authority is not None
    row: dict[str, object] = {
        **_W04_GOLD_PROJECTION,
        "evidence_class": "w04_real_governed",
        "w04_authority": dict(registry.w04_family.w04_authority),
        "dependency_identity": {
            "lineage_hash": _W04_LINEAGE_HASH,
            "dependencies": list(_W04_DEPENDENCIES),
        },
        "counts": {
            "action_count": 2,
            "coordinate_known_action_count": 2,
            "match_count": 1,
            "resolved_possession_action_count": 2,
        },
    }
    row["gold_row_count"] = substitution
    with pytest.raises(FeatureRegistryError, match="gold_row_count"):
        materialize_w04_real_row(row, registry)


def test_w04_gold_row_count_integer_one_retains_accepted_result(registry) -> None:  # type: ignore[no-untyped-def]
    """The ordinary JSON integer one retains the exact accepted projection result."""
    assert registry.w04_family.w04_authority is not None
    row: dict[str, object] = {
        **_W04_GOLD_PROJECTION,
        "evidence_class": "w04_real_governed",
        "w04_authority": dict(registry.w04_family.w04_authority),
        "dependency_identity": {
            "lineage_hash": _W04_LINEAGE_HASH,
            "dependencies": list(_W04_DEPENDENCIES),
        },
        "counts": {
            "action_count": 2,
            "coordinate_known_action_count": 2,
            "match_count": 1,
            "resolved_possession_action_count": 2,
        },
    }
    row["gold_row_count"] = 1
    result = materialize_w04_real_row(row, registry)
    assert tuple(value.numeric_value for value in result.values) == (2.0, 2.0, 1.0, 2.0)


def test_fixture_digest_drift_and_noncanonical_bytes_reject(tmp_path: Path, registry) -> None:  # type: ignore[no-untyped-def]
    """Fixture digest and physical-byte substitutions cannot be normalized away."""
    fixture = _load(FIXTURE_PATH)
    fixture["fixture_digest"] = "f" * 64
    drifted = tmp_path / "drifted.json"
    _write_canonical(drifted, fixture)
    with pytest.raises(FeatureRegistryError, match="fixture_digest"):
        load_synthetic_development_fixture(drifted, registry)
    noncanonical = tmp_path / "noncanonical.json"
    noncanonical.write_bytes(FIXTURE_PATH.read_bytes() + b" ")
    with pytest.raises(FeatureRegistryError, match="exact compact canonical"):
        load_synthetic_development_fixture(noncanonical, registry)


def test_production_feature_registry_contains_no_assert_nodes() -> None:
    """Runtime security gates must survive optimized Python execution."""
    source = Path(feature_registry_module.__file__).read_text(encoding="utf-8")
    assert not any(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(source)))


def test_terminal_validation_gates_fail_closed_without_asserts(registry) -> None:  # type: ignore[no-untyped-def]
    """Former terminal asserts raise the public registry error for every invalid boundary."""
    synthetic_without_controls = replace(registry.synthetic_family, metadata_control_schema=None)
    registry_without_controls = replace(
        registry,
        families=(registry.w04_family, synthetic_without_controls),
    )
    with pytest.raises(FeatureRegistryError, match="metadata-control schema is required"):
        feature_registry_module._require_accepted_registry_identity(registry_without_controls)
    with pytest.raises(FeatureRegistryError, match="observed feature calculation requires"):
        feature_registry_module._feature_value("observed", None, None)

    row: dict[str, object] = {
        **_W04_GOLD_PROJECTION,
        "evidence_class": "w04_real_governed",
        "w04_authority": dict(registry.w04_family.w04_authority or {}),
        "dependency_identity": {
            "lineage_hash": _W04_LINEAGE_HASH,
            "dependencies": list(_W04_DEPENDENCIES),
        },
        "counts": {
            "action_count": 2,
            "coordinate_known_action_count": 2,
            "match_count": 1,
            "resolved_possession_action_count": 2,
        },
    }
    registry_without_authority = replace(
        registry,
        families=(replace(registry.w04_family, w04_authority=None), registry.synthetic_family),
    )
    with pytest.raises(FeatureRegistryError, match="W04 authority is required"):
        materialize_w04_real_row(row, registry_without_authority)

    malformed_dependencies = deepcopy(row)
    malformed_dependencies["dependency_identity"] = {
        "lineage_hash": _W04_LINEAGE_HASH,
        "dependencies": ["not-a-mapping"],
    }
    with pytest.raises(FeatureRegistryError, match="W04 dependency entries must be objects"):
        materialize_w04_real_row(malformed_dependencies, registry)

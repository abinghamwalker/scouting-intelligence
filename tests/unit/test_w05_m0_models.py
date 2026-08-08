"""Direct R5 adversarial coverage for the frozen synthetic M0 baseline packet."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pytest

from scouting.contracts.m0 import M0ArrayDescriptor, M0ArtifactManifest, M0ModelFamily
from scouting.features.registry import load_feature_registry
from scouting.m0 import (
    M0RuntimeError,
    load_m0_artifact,
    load_m0_configuration,
    load_m0_development_candidates,
    load_m0_development_queries,
)
from scouting.modeling import M0TrainingError, fit_m0_artifact, run_synthetic_development_check
from scouting.modeling.baselines import _canonical_tied_basis
from scouting.roles.taxonomy import load_role_taxonomy
from scouting.storage.formats import canonical_json_bytes

ROOT = Path(__file__).parents[2]
EXPECTED = {
    "metadata_control": "19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee",
    "raw_euclidean_control": "3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36",
    "robust_scaled_cosine": "ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc",
    "weighted_cosine": "c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801",
    "pca": "90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971",
    "role_aware_restriction": "c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801",
}
_RANKINGS = {
    "metadata_control": (
        "3724f895afdeaf000d7e53b22f1b5e6c2429dace7db3067e48ddce6423943226",
        "697d4fde20af41aa58cfbaba83a9528649e3254654776f64bb1aef7873fccb5e",
        "897ffc66f8850ff694682495440690de90f261b48736e8dacd80d9feaccaccfb",
        "81c76ac02e2f0234d7080ec91fc76638981e0238ddd197eca296d24bbba583c2",
        "040ea427b0b6f4b6b8171ff1af3b2b08373a24129cc45afc63a055c6a06f8f8d",
        "ba7faa4ccff945efd5b796b6359afa6dd4a7daf42630b0bb3bef5727c9b0a221",
        "03056e537864a31fbf21db57ea44f07c126d0c5110aee3457c71887cb7d60c18",
        "c9809e2d4d42b44a13fc70970063e0dcecffb2318291abbbc5b6acb807011d72",
        "eda80340631d5b59c5cb149a3a8d2856c34c5835130a975af7d8af62d2a18413",
        "c96df990779ab05e26e27e5b2fc4ea5e54b0dbb2cbd79df8e6f5de8da40815f8",
        "bb435b78f54cc19daf28e2126adffa6f77b16f740f09e4a5ecfd53c5836e0a01",
        "286c6e6935cb0b8007fbb8b23dabac5557e4f5f109c9827c8fbf1a0df7157cb7",
        "d517dc261456bb564e57cca73c89403dc35ca0c09ac61aa7c7fbcaf982c85621",
        "35ddf8f846f0f928de60f0959dfe6238f2fcb9d83e3600431e2a81c76223773e",
        "b568712dcbde3c29ade76c72382d7dcb5f7446701827228773a2b65e35a4e89f",
        "46d844bd61e72c42d5e3630130012bc9207275319e1a1973bd25157e951d8aa3",
        "d7fb3702afa9cf4bf0590f29a92e52904b8d01fa2f6de19b850bfeaf59281e5a",
        "f9357a7cfc37d7504fa74bef33e90e6f76d5549b3539e767e25c4f2d46d2e671",
    ),
    "raw_euclidean_control": (
        "3724f895afdeaf000d7e53b22f1b5e6c2429dace7db3067e48ddce6423943226",
        "697d4fde20af41aa58cfbaba83a9528649e3254654776f64bb1aef7873fccb5e",
        "897ffc66f8850ff694682495440690de90f261b48736e8dacd80d9feaccaccfb",
        "d128cda704ecbf89189a52adb7717398b6555474fc96c5834761c9d6dd9c7051",
        "040ea427b0b6f4b6b8171ff1af3b2b08373a24129cc45afc63a055c6a06f8f8d",
        "ba7faa4ccff945efd5b796b6359afa6dd4a7daf42630b0bb3bef5727c9b0a221",
        "71098451c5c6f025b1d03eaab59d45c9d8ec2f3ab201c32f0d8e31cd520cc391",
        "e947ca44ac129bf416aad65761d244830452039c385d04919f44234dc06ffa99",
        "d8bc2e2e616810d19c839a2a04fff3aff5704777564efdda8dc201a1c24b99d5",
        "4b28d60a3af5ef5004af985c7753d7ca951688a0cdf2975514906ba939fe9b8e",
        "216acee63d4aa03a1cb4cd07952dbb4d06568c4f84fba4795c01ebd589a9deb0",
        "9a1bb8ae79d21a9d42564acbfaab7470e25ddc5c3b506c729ac1b522634763fc",
        "7a372a8b5ddc48c2cd3d03df40883272c4e599e11e5c5e80f4b8c669a728e8f6",
        "31dc7eb693b183fb6acb097ec9d892b93d7ba2edad85d10e5ba0250b23a61d95",
        "0a8a326d865c4f1b6ff0bcbc47d827c2b3baa62c8200b5cc7e48ab479c4e1c74",
        "db26d0c6c3d85315cd80e6aaf1e2b77d387c80f487ce31054be29210685a4423",
        "1e9d6e499a95ced25964ba0a61d3b743a0e00b2ea2295d128292dd146ba163cf",
        "7bfca8e5b06474270bc5f65891ed6e11651ca675da1307ddca902f9ac07d8e00",
    ),
    "similarity": (
        "a0ed83ee80b9447534ceb033f27459cd1c403eeae21c56fadd716accde1eadf5",
        "ab313239e97b484f85bc13a0566532ba46b5a3c88a697431f51223224465714c",
        "bd45d530b14272c350db04c554399fbfe32be52a9dee1bd4752aabf4988bbd63",
        "bf35fd0adbe6468bf5063242c9a58ad7d86fa5f2b0573bd6e00af6ee5f6a1924",
        "f993359a83bb7cd584e5125a418f8f7b26aaf82eef3ee71cd4ccd0b46b624576",
        "15635fd6a44d6a03520498287721004c284302ea4da1c3ce9b3285543509fb8c",
        "c1f12a735a710073951b61e2c84b0d7fa7b942e056b5cd3b700d0801781967d4",
        "e1ded08d97507ffab1674cb384bd1b8e043f0eaf705990a7b3311d504ed4325f",
        "80d07c6a1515ffab5c50c3ea93087cd4a3ca00b3658fa3f7299e0c74e7da1a18",
        "3d325c633ebb2ce229112b2c9f0318ce4196637a65ff584dbbe9d86f709805d8",
        "dae4ea7bff9956bb355ebb9f25a5d823a9a99f4a901f3b5c5fe9bdcb1ad5f1de",
        "7b48087c009ba041ff12ea301257e4747b8250fb7f611262613b2f8be3a11c17",
        "089dfd92bb48eb60f89b02ee4a19b83ab53919731545329a9d8cb5d69e02597f",
        "2261c6571a139a751f94ad3a525147552ac8daf03eda9b85d067d1779617f657",
        "721db055470ea8eb611f0a5919661b38174624a730ce14a91b85985ba8e6ec97",
        "f50cecad7f207508a173890b036b151e163040f420a53bf48fd36d562eb7c23d",
        "27c90a8c002daa243965ae048c9901e84641cc9243148e510fb4e132fa90868c",
        "f0d4b01931be2b26b76638308409e7e31755aa21f5bf15e959e9566d8d488e70",
    ),
}


@pytest.fixture()
def authorities() -> tuple[object, object, object, object, object]:
    registry = load_feature_registry(ROOT / "configs/features/w05-m0-feature-registry-v1.json")
    taxonomy = load_role_taxonomy(
        ROOT / "configs/roles/w05-football-responsibility-taxonomy-v1.json"
    )
    config = load_m0_configuration(ROOT / "configs/models/w05-m0-baselines-v1.json")
    candidates = load_m0_development_candidates(
        ROOT / "tests/fixtures/w05/m0-development-candidates-v1.json",
        registry=registry,
        taxonomy=taxonomy,
    )
    queries = load_m0_development_queries(
        ROOT / "tests/fixtures/w05/m0-development-queries-v1.json",
        candidates=candidates,
        configuration=config,
    )
    return registry, taxonomy, config, candidates, queries


def _fit(directory: Path, family: M0ModelFamily, authorities: tuple[object, ...]) -> object:
    registry, taxonomy, config, candidates, _ = authorities
    return fit_m0_artifact(
        family,
        candidates=candidates,
        taxonomy=taxonomy,
        registry=registry,
        configuration=config,
        artifact_directory=directory,
    )


def _loaded(directory: Path, authorities: tuple[object, ...]) -> object:
    registry, taxonomy, config, candidates, queries = authorities
    return load_m0_artifact(
        directory,
        taxonomy=taxonomy,
        registry=registry,
        configuration=config,
        candidates=candidates,
        queries=queries,
    )


def test_frozen_typed_authorities_reproduce_all_fixture_pins(
    authorities: tuple[object, ...],
) -> None:
    registry, _, config, candidates, queries = authorities
    assert config.candidate_population_projection_digest == candidates.population_digest(registry)
    assert config.query_population_projection_digest == queries.projection_digest()
    assert len(candidates.rows) == len(queries.queries) == 18
    assert candidates.rows[0]["feature_row"]["expected_feature_values"][-1]["state"] == "zero"
    with pytest.raises(TypeError):
        candidates.rows[0]["feature_row"]["player_id"] = "changed"
    with pytest.raises(TypeError):
        config.expected_array_payload_digests["pca"] = "0" * 64


def test_all_six_families_rebuild_payloads_schemas_scores_and_rankings(
    tmp_path: Path, authorities: tuple[object, ...]
) -> None:
    registry, taxonomy, config, candidates, queries = authorities
    scores = {}
    for family in M0ModelFamily:
        manifest = _fit(tmp_path / family.value, family, authorities)
        assert manifest.array_payload_digest == EXPECTED[family.value]
        loaded = _loaded(tmp_path / family.value, authorities)
        expected_count = 3 if family is M0ModelFamily.METADATA_CONTROL else 6
        assert len(loaded.manifest.feature_names) == expected_count
        assert len(loaded.player_ids) == 18
        check = run_synthetic_development_check(
            tmp_path / family.value,
            taxonomy=taxonomy,
            registry=registry,
            configuration=config,
            candidates=candidates,
            queries=queries,
        )
        scores[family.value] = check["mean_constructed_peer_group_precision_at_k"]
        expected_rankings = _RANKINGS[
            family.value
            if family.value in {"metadata_control", "raw_euclidean_control"}
            else "similarity"
        ]
        assert tuple(check["ranking_digests"]) == expected_rankings
    assert scores == {
        "metadata_control": 0.1111111111111111,
        "raw_euclidean_control": 0.3333333333333333,
        "robust_scaled_cosine": 1.0,
        "weighted_cosine": 1.0,
        "pca": 1.0,
        "role_aware_restriction": 1.0,
    }


def test_selected_rebuild_bytes_reload_pca_and_exemplar_behaviour(
    tmp_path: Path, authorities: tuple[object, ...]
) -> None:
    first, second = tmp_path / "one", tmp_path / "two"
    _fit(first, M0ModelFamily.ROLE_AWARE_RESTRICTION, authorities)
    _fit(second, M0ModelFamily.ROLE_AWARE_RESTRICTION, authorities)
    assert (first / "configuration.json").read_bytes() == (
        ROOT / "configs/models/w05-m0-baselines-v1.json"
    ).read_bytes()
    for name in ("arrays.npz", "configuration.json", "candidate-universe.json", "manifest.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    pca_directory = tmp_path / "pca"
    _fit(pca_directory, M0ModelFamily.PCA, authorities)
    pca = _loaded(pca_directory, authorities)
    rows = pca.score(pca.player_ids[0], limit=3)
    assert all(len(row.contributions) == 6 for row in rows)
    assert all(
        row.distance == pytest.approx(1.0 + sum(row.contributions), abs=1e-15) for row in rows
    )
    exemplar = pca.score(exemplar_player_ids=(pca.player_ids[2], pca.player_ids[1]), limit=3)
    reversed_exemplar = pca.score(
        exemplar_player_ids=(pca.player_ids[1], pca.player_ids[2]), limit=3
    )
    assert exemplar == reversed_exemplar


def test_typed_authority_and_re_signed_substitution_attacks_fail_closed(
    tmp_path: Path, authorities: tuple[object, ...]
) -> None:
    registry, taxonomy, config, candidates, queries = authorities
    with pytest.raises(M0TrainingError):
        fit_m0_artifact(
            M0ModelFamily.PCA,
            candidates=candidates,
            taxonomy=taxonomy,
            registry=registry,
            configuration=MappingProxyType({}),
            artifact_directory=tmp_path / "invalid",
        )
    re_signed_config = json.loads((ROOT / "configs/models/w05-m0-baselines-v1.json").read_bytes())
    re_signed_config["role_aware_minimum_overlap"] = 0.5
    re_signed_config["configuration_digest"] = hashlib.sha256(
        canonical_json_bytes(
            {key: value for key, value in re_signed_config.items() if key != "configuration_digest"}
        )
    ).hexdigest()
    config_path = tmp_path / "re-signed-config.json"
    config_path.write_bytes(canonical_json_bytes(re_signed_config))
    with pytest.raises(M0RuntimeError):
        load_m0_configuration(config_path)
    directory = tmp_path / "artifact"
    _fit(directory, M0ModelFamily.ROLE_AWARE_RESTRICTION, authorities)
    universe = json.loads((directory / "candidate-universe.json").read_bytes())
    universe["candidates"][0]["metadata"]["synthetic_age_years"] = 99
    (directory / "candidate-universe.json").write_bytes(canonical_json_bytes(universe))
    with pytest.raises(M0RuntimeError):
        _loaded(directory, authorities)
    shutil.rmtree(directory)
    _fit(directory, M0ModelFamily.ROLE_AWARE_RESTRICTION, authorities)
    manifest = json.loads((directory / "manifest.json").read_bytes())
    manifest["model_id"] = "w05-m0-pca-v1"
    manifest["artifact_manifest_digest"] = M0ArtifactManifest.digest_for_payload(manifest)
    (directory / "manifest.json").write_bytes(canonical_json_bytes(manifest))
    with pytest.raises(M0RuntimeError):
        _loaded(directory, authorities)
    with pytest.raises(M0RuntimeError):
        load_m0_artifact(
            directory,
            taxonomy=taxonomy,
            registry=registry,
            configuration=config.canonical_mapping(),
            candidates=candidates,
            queries=queries,
        )


def test_safe_runtime_rejects_symlink_zip_and_query_exemplar_overlap(
    tmp_path: Path, authorities: tuple[object, ...]
) -> None:
    directory = tmp_path / "artifact"
    _fit(directory, M0ModelFamily.ROLE_AWARE_RESTRICTION, authorities)
    loaded = _loaded(directory, authorities)
    with pytest.raises(M0RuntimeError):
        loaded.score(
            exemplar_player_ids=(loaded.player_ids[0],),
            excluded_player_ids=(loaded.player_ids[0],),
        )
    link = tmp_path / "artifact-link"
    link.symlink_to(directory, target_is_directory=True)
    with pytest.raises(M0RuntimeError):
        _loaded(link, authorities)
    arrays = directory / "arrays.npz"
    with zipfile.ZipFile(arrays, "a") as archive:
        archive.writestr("extra.npy", b"not-an-array")
    with pytest.raises(M0RuntimeError):
        _loaded(directory, authorities)


def test_complete_typed_authorities_manifest_bytes_and_write_ancestors_fail_closed(
    tmp_path: Path, authorities: tuple[object, ...]
) -> None:
    registry, taxonomy, config, candidates, queries = authorities
    with pytest.raises(M0TrainingError):
        _fit(
            tmp_path / "forged-config",
            M0ModelFamily.PCA,
            (
                registry,
                taxonomy,
                replace(config, role_aware_minimum_overlap=0.0),
                candidates,
                queries,
            ),
        )
    forged_feature = replace(registry.synthetic_family.schema.features[0], name="forged_feature")
    forged_schema = replace(
        registry.synthetic_family.schema,
        features=(forged_feature, *registry.synthetic_family.schema.features[1:]),
    )
    forged_family = replace(registry.synthetic_family, schema=forged_schema)
    forged_registry = replace(registry, families=(registry.w04_family, forged_family))
    with pytest.raises(M0TrainingError):
        _fit(
            tmp_path / "forged-registry",
            M0ModelFamily.PCA,
            (
                forged_registry,
                taxonomy,
                config,
                candidates,
                queries,
            ),
        )
    with pytest.raises(M0TrainingError):
        _fit(
            tmp_path / "forged-candidates",
            M0ModelFamily.PCA,
            (
                registry,
                taxonomy,
                config,
                replace(candidates, peer_groups=MappingProxyType({})),
                queries,
            ),
        )
    with pytest.raises(M0TrainingError):
        run_synthetic_development_check(
            tmp_path / "missing",
            taxonomy=taxonomy,
            registry=registry,
            configuration=config,
            candidates=candidates,
            queries=replace(queries, queries=queries.queries[:-1]),
        )
    directory = tmp_path / "artifact"
    _fit(directory, M0ModelFamily.ROLE_AWARE_RESTRICTION, authorities)
    (directory / "manifest.json").write_bytes(b'{"schema_version":1,"schema_version":1}')
    with pytest.raises(M0RuntimeError):
        _loaded(directory, authorities)
    ancestor = tmp_path / "real-ancestor"
    ancestor.mkdir()
    linked = tmp_path / "linked-ancestor"
    linked.symlink_to(ancestor, target_is_directory=True)
    with pytest.raises(M0TrainingError):
        _fit(linked / "artifact", M0ModelFamily.PCA, authorities)


@pytest.mark.parametrize("field,value", (("endianness", "big"), ("memory_order", "fortran")))
def test_re_signed_manifest_descriptor_byte_order_and_layout_fail_closed(
    tmp_path: Path, authorities: tuple[object, ...], field: str, value: str
) -> None:
    directory = tmp_path / field
    _fit(directory, M0ModelFamily.ROLE_AWARE_RESTRICTION, authorities)
    payload = json.loads((directory / "manifest.json").read_bytes())
    payload["array_descriptors"][0][field] = value
    payload["array_descriptor_bundle_digest"] = M0ArtifactManifest.descriptor_bundle_digest_for(
        tuple(
            M0ArrayDescriptor.model_validate_json(canonical_json_bytes(item))
            for item in payload["array_descriptors"]
        )
    )
    payload["artifact_manifest_digest"] = M0ArtifactManifest.digest_for_payload(payload)
    (directory / "manifest.json").write_bytes(canonical_json_bytes(payload))
    with pytest.raises(M0RuntimeError):
        _loaded(directory, authorities)


def test_tied_pca_projector_basis_is_rotation_and_sign_invariant() -> None:
    basis = np.asarray(((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)), dtype="<f8")
    sine = np.sqrt(0.5)
    rotated = np.asarray(((sine, sine, 0.0), (-sine, sine, 0.0)), dtype="<f8")
    signed_permuted = np.asarray(((0.0, -1.0, 0.0), (-1.0, 0.0, 0.0)), dtype="<f8")
    assert np.array_equal(_canonical_tied_basis(basis), _canonical_tied_basis(rotated))
    assert np.array_equal(_canonical_tied_basis(basis), _canonical_tied_basis(signed_permuted))

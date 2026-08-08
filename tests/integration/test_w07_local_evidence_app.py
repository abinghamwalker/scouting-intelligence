"""Executable acceptance evidence for the W07 local-only evidence interface."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from fastapi.testclient import TestClient

from scouting.m0 import LoadedM0Artifact
from scouting.web import w07

ROOT = Path(__file__).parents[2]
ARTIFACT_ROOT = ROOT / "runs/w05/m0-baseline-v1"
QUERY_ID = UUID("20000000-0000-4000-8000-000000000001")
ARTIFACT_SHA256 = {
    "arrays.npz": "73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6",
    "candidate-universe.json": "2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e",
    "configuration.json": "d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006",
    "manifest.json": "c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a",
}
EXPECTED_PINS = {
    "artifact_id": "9a0d43c6-d177-51be-8280-3bf02bedbc99",
    "manifest_digest": "2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9",
    "feature_schema": "1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f",
    "taxonomy_digest": "59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097",
    "configuration_digest": "5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a",
    "lineage_identity": "e77de98a171447b8a3361161e5efbc8173909f933435f27ac99e0534c6d591c7",
}


def _artifact_hashes() -> dict[str, str]:
    return {path.name: sha256(path.read_bytes()).hexdigest() for path in ARTIFACT_ROOT.iterdir()}


def test_catalogue_has_exactly_18_stable_labels_and_all_filter_modes() -> None:
    """Labels are catalogue identities, never renumbered after a filter is applied."""
    with TestClient(w07.create_w07_app()) as client:
        catalogue = client.get("/w07/search")
        assert catalogue.status_code == 200
        all_rows = catalogue.text
        assert all_rows.count("/w07/player/") == 18
        assert "Synthetic candidate 01" in all_rows
        for position in ("CENTRAL", "DEFENSIVE", "WIDE"):
            filtered = client.get("/w07/search", params={"position": position})
            assert filtered.status_code == 200
            assert filtered.text.count("/w07/player/") == 6
        player_id = "20000000-0000-4000-8000-000000000004"
        assert client.get("/w07/search", params={"q": player_id}).text.count("/w07/player/") == 1
        by_label = client.get("/w07/search", params={"q": "Synthetic candidate 04"})
        assert player_id in by_label.text
        central = client.get("/w07/search", params={"position": "CENTRAL"}).text
        assert "Synthetic candidate 04" in central
        assert "Synthetic candidate 01" in central
        assert "Synthetic candidate 02" not in central
        assert (
            "No accepted candidates match"
            in client.get("/w07/search", params={"q": "not-a-candidate"}).text
        )
        assert (
            "No accepted candidates match"
            in client.get("/w07/search", params={"position": "INVALID"}).text
        )


def test_known_player_displays_exact_feature_role_cutoff_and_lineage() -> None:
    """The record page exposes the admitted evidence, not a generic substitute."""
    core, candidates = w07._core()
    del core
    row = next(
        item for item in candidates.rows if item["feature_row"]["player_id"] == str(QUERY_ID)
    )
    feature = row["feature_row"]
    role = row["role_row"]
    with TestClient(w07.create_w07_app()) as client:
        response = client.get(f"/w07/player/{QUERY_ID}")
    assert response.status_code == 200
    for value in (
        str(QUERY_ID),
        feature["synthetic_position_code"],
        str(feature["synthetic_age_years"]),
        feature["feature_cutoff_ts"],
        feature["dependency_identity"]["lineage_hash"],
        *(str(value) for value in feature["raw_numerator_inputs"].values()),
        *(item["role_code"] for item in role["expected_role_probabilities"]),
    ):
        assert value in response.text


def test_malformed_or_unknown_identity_is_unavailable_without_serving_or_scoring() -> None:
    """Identity validation fails before either public serving entrance or scorer can run."""
    with (
        patch("scouting.web.w07.serve_m0_request", wraps=w07.serve_m0_request) as single,
        patch("scouting.web.w07.serve_m0_batch", wraps=w07.serve_m0_batch) as batch,
        patch.object(
            LoadedM0Artifact, "score", autospec=True, wraps=LoadedM0Artifact.score
        ) as score,
        TestClient(w07.create_w07_app()) as client,
    ):
        for bad in ("not-a-uuid", "20000000-0000-4000-8000-000000000099"):
            assert "UNAVAILABLE" in client.get(f"/w07/player/{bad}").text
            assert "UNAVAILABLE" in client.get(f"/w07/retrieval/{bad}").text
            assert "UNAVAILABLE" in client.get(f"/w07/compare/{bad}/{bad}").text
    assert single.call_count == batch.call_count == score.call_count == 0


def test_retrieval_and_comparison_use_only_public_serving_paths_and_shared_scorer() -> None:
    """Web retrieval is direct, comparison is batch, and neither reimplements scoring."""
    before = _artifact_hashes()
    observed = []
    with (
        patch("scouting.web.w07.serve_m0_request", wraps=w07.serve_m0_request) as single,
        patch("scouting.web.w07.serve_m0_batch", wraps=w07.serve_m0_batch) as batch,
        patch.object(
            LoadedM0Artifact, "score", autospec=True, wraps=LoadedM0Artifact.score
        ) as score,
        TestClient(w07.create_w07_app()) as client,
    ):
        direct = client.get(f"/w07/retrieval/{QUERY_ID}")
        assert direct.status_code == 200
        request = single.call_args.args[1]
        observed.append(single.call_args.args[0].serve(request))
        candidate = observed[0].scored_candidates[0].player_id
        comparison = client.get(f"/w07/compare/{QUERY_ID}/{candidate}")
        assert comparison.status_code == 200
        batch_request = batch.call_args.args[1][0]
        observed.append(batch.call_args.args[0].serve(batch_request))
    assert single.call_count == 1
    assert batch.call_count == 1
    assert score.call_count == 4
    assert observed[0].model_dump_json() == observed[1].model_dump_json()
    assert observed[0].result_digest == observed[1].result_digest
    assert _artifact_hashes() == before == ARTIFACT_SHA256


def test_result_displays_pinned_result_context_exact_digests_and_explanation_values() -> None:
    """Every returned row must carry honest ranking and provenance evidence."""
    with TestClient(w07.create_w07_app()) as client:
        response = client.get(f"/w07/retrieval/{QUERY_ID}")
    assert response.status_code == 200
    result = w07.serve_m0_request(w07._core()[0], w07.default_request(QUERY_ID))
    expected = {
        **EXPECTED_PINS,
        "model_id": result.artifact_manifest.model_id,
        "model_version": result.artifact_manifest.model_version,
        "index_id": result.artifact_manifest.index_id,
        "index_version": result.artifact_manifest.index_version,
        "result_digest": result.result_digest,
        "feature_cutoff_ts": (
            result.retrieval_result.temporal_evidence.feature_cutoff_ts.isoformat()
        ),
        "applicability": result.retrieval_result.candidates[0].confidence.applicability.value,
        "limitations": "; ".join(result.retrieval_result.candidates[0].confidence.limitations),
    }
    for value in expected.values():
        assert str(value) in response.text
    for candidate, explanation in zip(
        result.retrieval_result.candidates, result.explanations, strict=True
    ):
        assert str(candidate.rank) in response.text
        for reason in candidate.reason_codes:
            assert reason in response.text
        assert candidate.confidence.applicability.value in response.text
        for limitation in candidate.confidence.limitations:
            assert limitation in response.text
        for item in explanation.inputs:
            assert item.feature_name in response.text
            assert str(item.contribution) in response.text


def test_closed_states_headers_stylesheet_local_only_and_claim_boundary() -> None:
    """The explicit evidence states and every response remain local and non-promotional."""
    forbidden = (
        "match percentage:",
        "blended score:",
        "recommended candidate",
        "predicted outcome",
        "market value",
        "production-ready",
    )
    with TestClient(w07.create_w07_app()) as client:
        stylesheet = client.get("/static/w07/app.css")
        assert stylesheet.status_code == 200
        for state in ("loading", "empty", "unavailable", "error", "no-go"):
            response = client.get(f"/w07/state/{state}")
            assert response.status_code == 200
            assert state.upper() in response.text
            assert f"state-{state}" in response.text
            assert "no-store" == response.headers["cache-control"]
            assert response.headers["referrer-policy"] == "no-referrer"
            assert "default-src 'self'" in response.headers["content-security-policy"]
        assert client.get("/w07/state/unknown").status_code == 404
        for route in (
            "/w07",
            "/w07/search",
            f"/w07/player/{QUERY_ID}",
            f"/w07/retrieval/{QUERY_ID}",
        ):
            text = client.get(route).text.lower()
            assert all(term not in text for term in forbidden)
            assert "http://" not in text and "https://" not in text
        evidence = client.get("/w07/evidence").text
        for value in (
            "2 actions",
            "2 coordinate-known actions",
            "1 match",
            "2 resolved-possession actions",
            "SUPPRESSED",
        ):
            assert value in evidence

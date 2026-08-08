from __future__ import annotations

import hashlib
import io
import json
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import numpy as np
import pytest

from scouting.contracts.research import (
    EligibilityDecision,
    EligibilityReason,
    EligibilityReasonCount,
    FeatureMatrixManifest,
    FeatureMatrixRow,
    FeatureValueState,
    MinuteEvidenceState,
    PopulationDecisionReason,
    ResearchArtifactFile,
    ResearchCoverage,
    ResearchFeatureValue,
    SourcePopulationDecision,
    canonical_research_digest,
)
from scouting.modeling.research import (
    DEFAULT_INDEX_ROOT,
    DEFAULT_MATRIX_ARTIFACT_ROOT,
    DEFAULT_MODEL_CONFIG_PATH,
    ELIGIBILITY_DECISIONS_ROLE,
    FEATURE_MATRIX_ROWS_ROLE,
    INDEX_ARTIFACT_PATHS,
    INDEX_CATALOGUE_ROLE,
    INDEX_VECTORS_ROLE,
    PLAYER_CATALOGUE_ROLE,
    POPULATION_DECISIONS_ROLE,
    MatrixCatalogueEntry,
    ResearchIndexBuildError,
    ResearchIndexBuildMode,
    build_research_index,
    load_feature_matrix,
    load_research_index,
    population_referred_grain_digest,
    rows_semantic_digest,
)
from scouting.storage.formats import canonical_json_bytes, canonical_jsonl_bytes

_GENERATED = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)
_CUTOFF = datetime(2026, 8, 1, 0, 0, tzinfo=UTC)
_WINDOW_START = datetime(2017, 7, 1, 0, 0, tzinfo=UTC)
_WINDOW_END = datetime(2018, 7, 1, 0, 0, tzinfo=UTC)
_COMPETITION = UUID("30000000-0000-4000-8000-000000000001")
_SECOND_COMPETITION = UUID("30000000-0000-4000-8000-000000000002")
_TEAM = UUID("40000000-0000-4000-8000-000000000001")
_SECOND_TEAM = UUID("40000000-0000-4000-8000-000000000002")
_PLAYERS = tuple(UUID(f"20000000-0000-4000-8000-{index:012d}") for index in range(1, 5))
_DIGESTS = {
    name: str(index) * 64
    for index, name in enumerate(
        (
            "dataset",
            "source",
            "completion",
            "identity",
            "canonical",
            "registry",
            "policy",
            "code",
            "lineage",
        ),
        start=1,
    )
}


def _feature(name: str, value: float) -> ResearchFeatureValue:
    return ResearchFeatureValue(
        feature_name=name,
        state=FeatureValueState.ZERO if value == 0.0 else FeatureValueState.VALUE,
        value=value,
        numerator=value,
        denominator=90.0,
    )


def _decision(
    index: int,
    *,
    competition_id: UUID = _COMPETITION,
    grain_suffix: str = "",
    season_id: str = "2017-18",
) -> EligibilityDecision:
    return EligibilityDecision(
        source_player_id=str(index),
        grain_id=f"competition-season-player-{index}{grain_suffix}",
        player_id=_PLAYERS[index - 1],
        competition_id=competition_id,
        season_id=season_id,
        eligibility_policy_version="w09-eligibility-v1",
        eligibility_policy_digest=_DIGESTS["policy"],
        minute_state=MinuteEvidenceState.EXACT,
        minutes=900.0 + index,
        minimum_minutes=450.0,
        eligible=True,
        reason=EligibilityReason.ELIGIBLE,
        feature_cutoff_ts=_CUTOFF,
        temporal_authorities_strictly_before_cutoff=True,
        source_match_count=10,
        source_action_count=100 + index,
    )


def _matrix_row(
    index: int,
    decision: EligibilityDecision,
    *,
    passes_per_90: float | None = None,
) -> FeatureMatrixRow:
    second_competition = decision.competition_id == _SECOND_COMPETITION
    return FeatureMatrixRow(
        grain_id=decision.grain_id,
        player_id=decision.player_id,
        display_name=f"Historical Fixture Player {index}",
        competition_id=decision.competition_id,
        competition_name=(
            "Second Historical Fixture League"
            if second_competition
            else "Historical Fixture League"
        ),
        season_id=decision.season_id,
        position_code=("GK", "DF", "MD")[index - 1],
        team_ids=(_SECOND_TEAM if second_competition else _TEAM,),
        team_names=(
            "Second Historical Fixture FC" if second_competition else "Historical Fixture FC",
        ),
        minute_state=MinuteEvidenceState.EXACT,
        minutes=cast(float, decision.minutes),
        match_count=10,
        features=(
            _feature(
                "passes_per_90",
                (float((1, 2, 100)[index - 1]) if passes_per_90 is None else passes_per_90),
            ),
            _feature("shots_per_90", 5.0),
        ),
        missing_feature_names=(),
        coverage=ResearchCoverage(
            lineup_matches_observed=10,
            lineup_matches_expected=10,
            action_matches_observed=10,
            action_matches_expected=10,
            coordinate_actions_observed=100,
            coordinate_actions_expected=100,
        ),
        window_start_utc=_WINDOW_START,
        window_end_utc=_WINDOW_END,
        feature_cutoff_ts=_CUTOFF,
        dataset_manifest_digest=_DIGESTS["dataset"],
        identity_bundle_digest=_DIGESTS["identity"],
        canonical_build_digest=_DIGESTS["canonical"],
        feature_registry_digest=_DIGESTS["registry"],
        eligibility_policy_digest=_DIGESTS["policy"],
        eligibility_decision_digest=canonical_research_digest(decision),
        source_lineage_digest=_DIGESTS["lineage"],
        source_action_count=cast(int, decision.source_action_count),
    )


def _write_private(path: Path, payload: bytes) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.write_bytes(payload)
    os.chmod(path, 0o600)


def _descriptor(
    role: str, path: str, rows: tuple[Any, ...], payload: bytes
) -> ResearchArtifactFile:
    return ResearchArtifactFile(
        role=role,
        relative_path=path,
        row_count=len(rows),
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        semantic_digest=rows_semantic_digest(rows),
    )


def _manifest_payload(
    *,
    catalogue: tuple[MatrixCatalogueEntry, ...],
    population: tuple[SourcePopulationDecision, ...],
    eligibility: tuple[EligibilityDecision, ...],
    matrix: tuple[FeatureMatrixRow, ...],
    files: tuple[ResearchArtifactFile, ...],
) -> dict[str, Any]:
    matrix_file = next(item for item in files if item.role == FEATURE_MATRIX_ROWS_ROLE)
    eligibility_file = next(item for item in files if item.role == ELIGIBILITY_DECISIONS_ROLE)
    reasons = {reason: 0 for reason in EligibilityReason}
    for decision in eligibility:
        reasons[decision.reason] += 1
    return {
        "schema_version": 1,
        "manifest_id": "50000000-0000-4000-8000-000000000001",
        "matrix_version": "w09-historical-player-window-v1",
        "matrix_digest": matrix_file.semantic_digest,
        "generated_at": _GENERATED.isoformat().replace("+00:00", "Z"),
        "feature_cutoff_ts": _CUTOFF.isoformat().replace("+00:00", "Z"),
        "window_start_utc": _WINDOW_START.isoformat().replace("+00:00", "Z"),
        "window_end_utc": _WINDOW_END.isoformat().replace("+00:00", "Z"),
        "dataset_version": "wyscout-2017-18-v1",
        "dataset_manifest_digest": _DIGESTS["dataset"],
        "source_manifest_id": "60000000-0000-4000-8000-000000000001",
        "source_manifest_digest": _DIGESTS["source"],
        "source_completion_digest": _DIGESTS["completion"],
        "identity_bundle_digest": _DIGESTS["identity"],
        "canonical_build_version": "w09-historical-canonical-v1",
        "canonical_build_digest": _DIGESTS["canonical"],
        "feature_registry_version": "w09-historical-player-window-v1",
        "feature_registry_digest": _DIGESTS["registry"],
        "eligibility_policy_version": "w09-eligibility-v1",
        "eligibility_policy_digest": _DIGESTS["policy"],
        "code_version": "fixture-code-v1",
        "code_digest": _DIGESTS["code"],
        "feature_names": ["passes_per_90", "shots_per_90"],
        "catalogue_player_count": len(catalogue),
        "population_decision_count": len(population),
        "population_referred_count": 3,
        "population_referred_grain_count": len(eligibility),
        "population_referred_grain_ledger_digest": population_referred_grain_digest(population),
        "population_no_lineup_count": 1,
        "unresolved_identity_count": 0,
        "rejected_identity_count": 0,
        "rejected_actor_action_count": 0,
        "eligibility_decision_count": len(eligibility),
        "unique_eligibility_grain_count": len(eligibility),
        "eligibility_ledger_digest": eligibility_file.semantic_digest,
        "eligibility_reason_counts": [
            EligibilityReasonCount(reason=reason, count=count).model_dump(mode="json")
            for reason, count in reasons.items()
        ],
        "matrix_row_count": len(matrix),
        "unique_matrix_grain_count": len(matrix),
        "unique_matrix_player_count": len({row.player_id for row in matrix}),
        "files": [item.model_dump(mode="json") for item in files],
        "contains_synthetic_rows": False,
        "limitations": ["Automated synthetic fixture authority; never a product candidate source."],
        "claim_boundary": "historical_resemblance_research_only",
    }


def _self_digest_manifest(payload: dict[str, Any]) -> bytes:
    payload["manifest_digest"] = canonical_research_digest(
        {
            key: value
            for key, value in payload.items()
            if key not in {"manifest_digest", "generated_at"}
        }
    )
    return canonical_json_bytes(payload)


def _feature_fixture(
    root: Path,
    *,
    cross_competition: bool = False,
    cross_season: bool = False,
) -> tuple[Path, FeatureMatrixManifest]:
    if cross_competition and cross_season:
        raise ValueError("fixture can vary competition or season, not both")
    catalogue = tuple(
        MatrixCatalogueEntry(
            source_player_id=str(index),
            player_id=player_id,
            display_name=f"Historical Fixture Player {index}",
            position_code=("GK", "DF", "MD", "FW")[index - 1],
        )
        for index, player_id in enumerate(_PLAYERS, start=1)
    )
    population_rows: list[SourcePopulationDecision] = []
    for index, player_id in enumerate(_PLAYERS, start=1):
        grain_ids: tuple[str, ...]
        if index == 1 and (cross_competition or cross_season):
            grain_ids = (
                "competition-season-player-1",
                (
                    "competition-season-player-1-transfer"
                    if cross_competition
                    else "competition-season-player-1-next-season"
                ),
            )
        elif index <= 3:
            grain_ids = (f"competition-season-player-{index}",)
        else:
            grain_ids = ()
        population_rows.append(
            SourcePopulationDecision(
                source_player_id=str(index),
                player_id=player_id,
                lineup_evidence_present=index <= 3,
                grain_ids=grain_ids,
                reason=(
                    PopulationDecisionReason.REFERRED_TO_WINDOW_ELIGIBILITY
                    if index <= 3
                    else PopulationDecisionReason.NO_LINEUP_EVIDENCE
                ),
            )
        )
    population = tuple(population_rows)
    eligibility_rows = [_decision(index) for index in range(1, 4)]
    matrix_rows = [
        _matrix_row(index, decision) for index, decision in enumerate(eligibility_rows, start=1)
    ]
    if cross_competition:
        transfer_decision = _decision(
            1,
            competition_id=_SECOND_COMPETITION,
            grain_suffix="-transfer",
        )
        eligibility_rows.append(transfer_decision)
        matrix_rows.append(_matrix_row(1, transfer_decision, passes_per_90=4.0))
    if cross_season:
        next_season_decision = _decision(
            1,
            grain_suffix="-next-season",
            season_id="2018-19",
        )
        eligibility_rows.append(next_season_decision)
        matrix_rows.append(_matrix_row(1, next_season_decision, passes_per_90=4.0))
    eligibility = tuple(
        sorted(
            eligibility_rows,
            key=lambda row: (row.player_id.bytes, row.grain_id),
        )
    )
    matrix = tuple(sorted(matrix_rows, key=lambda row: (row.player_id.bytes, row.grain_id)))
    records: tuple[tuple[str, str, tuple[Any, ...]], ...] = (
        (PLAYER_CATALOGUE_ROLE, "artifacts/player-catalogue.jsonl", catalogue),
        (POPULATION_DECISIONS_ROLE, "artifacts/population-decisions.jsonl", population),
        (ELIGIBILITY_DECISIONS_ROLE, "artifacts/eligibility-decisions.jsonl", eligibility),
        (FEATURE_MATRIX_ROWS_ROLE, "artifacts/feature-matrix-rows.jsonl", matrix),
    )
    files: list[ResearchArtifactFile] = []
    for role, relative_path, rows in records:
        payload = canonical_jsonl_bytes([row.model_dump(mode="json") for row in rows])
        _write_private(root / relative_path, payload)
        files.append(_descriptor(role, relative_path, rows, payload))
    manifest_payload = _manifest_payload(
        catalogue=catalogue,
        population=population,
        eligibility=eligibility,
        matrix=matrix,
        files=tuple(files),
    )
    encoded = _self_digest_manifest(manifest_payload)
    manifest_path = root / "manifests/matrix.manifest.json"
    _write_private(manifest_path, encoded)
    return manifest_path, FeatureMatrixManifest.model_validate_json(encoded)


def _rewrite_manifest(path: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    payload = cast(dict[str, Any], json.loads(path.read_bytes()))
    mutate(payload)
    _write_private(path, _self_digest_manifest(payload))


def _rewrite_matrix_rows(
    root: Path,
    manifest_path: Path,
    mutate: Callable[[list[dict[str, Any]]], None],
) -> None:
    manifest = cast(dict[str, Any], json.loads(manifest_path.read_bytes()))
    file = next(item for item in manifest["files"] if item["role"] == FEATURE_MATRIX_ROWS_ROLE)
    path = root / cast(str, file["relative_path"])
    rows = [json.loads(line) for line in path.read_bytes().splitlines()]
    mutate(rows)
    payload = canonical_jsonl_bytes(rows)
    _write_private(path, payload)
    semantic = hashlib.sha256(canonical_json_bytes(rows)).hexdigest()
    file.update(
        {
            "row_count": len(rows),
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "semantic_digest": semantic,
        }
    )
    manifest["matrix_digest"] = semantic
    _write_private(manifest_path, _self_digest_manifest(manifest))


def _index_manifest(root: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((root / "manifest.json").read_bytes()))


def _rewrite_index_manifest(root: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    manifest = _index_manifest(root)
    mutate(manifest)
    _write_private(root / "manifest.json", _self_digest_manifest(manifest))


def test_build_is_two_root_byte_reproducible_and_loads_read_only(tmp_path: Path) -> None:
    manifest_path, matrix_manifest = _feature_fixture(tmp_path / "matrix")
    first = tmp_path / "first-index"
    second = tmp_path / "second-index"

    first_manifest = build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=tmp_path / "matrix",
        output_root=first,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    second_manifest = build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=tmp_path / "matrix",
        output_root=second,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )

    assert first_manifest == second_manifest
    assert first_manifest.candidate_count == 3
    assert first_manifest.contains_synthetic_rows is False
    assert first_manifest.methods == (
        "weighted_euclidean",
        "weighted_cosine",
    )
    for name in (*INDEX_ARTIFACT_PATHS.values(), "manifest.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    loaded = load_research_index(
        first,
        matrix_manifest=matrix_manifest,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    assert loaded.vectors.shape == (3, 2)
    assert loaded.center == pytest.approx(np.array([2.0, 5.0]))
    assert loaded.scale == pytest.approx(np.array([49.5, 1.0]))
    assert [row.player_id for row in loaded.catalogue] == list(_PLAYERS[:3])
    assert not loaded.vectors.flags.writeable


def test_same_player_across_competitions_is_retained_and_reproducible(
    tmp_path: Path,
) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, matrix_manifest = _feature_fixture(matrix_root, cross_competition=True)
    loaded_matrix = load_feature_matrix(
        manifest_path,
        artifact_root=matrix_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    assert matrix_manifest.matrix_row_count == 4
    assert matrix_manifest.unique_matrix_player_count == 3
    assert [row.player_id for row in loaded_matrix.rows].count(_PLAYERS[0]) == 2
    assert {row.competition_id for row in loaded_matrix.rows if row.player_id == _PLAYERS[0]} == {
        _COMPETITION,
        _SECOND_COMPETITION,
    }

    first_root = tmp_path / "first-index"
    second_root = tmp_path / "second-index"
    first = build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=matrix_root,
        output_root=first_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    second = build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=matrix_root,
        output_root=second_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    assert first == second
    assert first.candidate_count == 4
    for name in (*INDEX_ARTIFACT_PATHS.values(), "manifest.json"):
        assert (first_root / name).read_bytes() == (second_root / name).read_bytes()
    loaded_index = load_research_index(
        first_root,
        matrix_manifest=matrix_manifest,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    assert [row.player_id for row in loaded_index.catalogue].count(_PLAYERS[0]) == 2


def test_loader_rejects_physical_and_semantic_matrix_tampering(tmp_path: Path) -> None:
    physical_root = tmp_path / "physical"
    manifest_path, _ = _feature_fixture(physical_root)
    matrix_path = physical_root / "artifacts/feature-matrix-rows.jsonl"
    _write_private(matrix_path, matrix_path.read_bytes() + b"\n")
    with pytest.raises(ResearchIndexBuildError, match="physical"):
        load_feature_matrix(
            manifest_path,
            artifact_root=physical_root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )

    semantic_root = tmp_path / "semantic"
    semantic_manifest, _ = _feature_fixture(semantic_root)

    def forge_semantic(payload: dict[str, Any]) -> None:
        file = next(item for item in payload["files"] if item["role"] == FEATURE_MATRIX_ROWS_ROLE)
        file["semantic_digest"] = "f" * 64
        payload["matrix_digest"] = "f" * 64

    _rewrite_manifest(semantic_manifest, forge_semantic)
    with pytest.raises(ResearchIndexBuildError, match="semantic"):
        load_feature_matrix(
            semantic_manifest,
            artifact_root=semantic_root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


def test_loader_rejects_path_escape_before_reading(tmp_path: Path) -> None:
    root = tmp_path / "matrix"
    manifest_path, _ = _feature_fixture(root)

    def escape(payload: dict[str, Any]) -> None:
        payload["files"][0]["relative_path"] = "../outside.jsonl"

    _rewrite_manifest(manifest_path, escape)
    with pytest.raises(ResearchIndexBuildError, match="manifest is incompatible"):
        load_feature_matrix(
            manifest_path,
            artifact_root=root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


@pytest.mark.parametrize("duplicate", ("grain", "player"))
def test_loader_rejects_duplicate_matrix_grain_or_player(tmp_path: Path, duplicate: str) -> None:
    root = tmp_path / duplicate
    manifest_path, _ = _feature_fixture(root)

    def duplicate_value(rows: list[dict[str, Any]]) -> None:
        if duplicate == "grain":
            rows[1]["grain_id"] = rows[0]["grain_id"]
        else:
            rows[1]["player_id"] = rows[0]["player_id"]

    _rewrite_matrix_rows(root, manifest_path, duplicate_value)
    with pytest.raises(ResearchIndexBuildError, match=f"duplicate {duplicate}"):
        load_feature_matrix(
            manifest_path,
            artifact_root=root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


def test_loader_rejects_absent_active_feature_and_temporal_pin_drift(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing"
    missing_manifest, _ = _feature_fixture(missing_root)

    def make_missing(rows: list[dict[str, Any]]) -> None:
        rows[1]["features"][0] = {
            "feature_name": "passes_per_90",
            "state": "missing",
            "value": None,
            "numerator": None,
            "denominator": None,
            "reason": "fixture absence",
        }
        rows[1]["missing_feature_names"] = ["passes_per_90"]

    _rewrite_matrix_rows(missing_root, missing_manifest, make_missing)
    with pytest.raises(ResearchIndexBuildError, match="absent active feature"):
        load_feature_matrix(
            missing_manifest,
            artifact_root=missing_root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )

    temporal_root = tmp_path / "temporal"
    temporal_manifest, _ = _feature_fixture(temporal_root)

    def drift_cutoff(rows: list[dict[str, Any]]) -> None:
        rows[0]["feature_cutoff_ts"] = "2026-08-02T00:00:00Z"

    _rewrite_matrix_rows(temporal_root, temporal_manifest, drift_cutoff)
    with pytest.raises(ResearchIndexBuildError, match="temporal or lineage"):
        load_feature_matrix(
            temporal_manifest,
            artifact_root=temporal_root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


def test_production_mode_rejects_fixture_roots_and_synthetic_row_marker(tmp_path: Path) -> None:
    root = tmp_path / "matrix"
    manifest_path, _ = _feature_fixture(root)
    with pytest.raises(ResearchIndexBuildError, match="governed W09 paths"):
        build_research_index(
            matrix_manifest_path=manifest_path,
            matrix_artifact_root=root,
            output_root=tmp_path / "index",
            model_config_path=DEFAULT_MODEL_CONFIG_PATH,
            mode=ResearchIndexBuildMode.PRODUCTION,
        )

    def mark_synthetic(rows: list[dict[str, Any]]) -> None:
        rows[0]["contains_synthetic_data"] = True

    _rewrite_matrix_rows(root, manifest_path, mark_synthetic)
    with pytest.raises(ResearchIndexBuildError, match="strict contract"):
        load_feature_matrix(
            manifest_path,
            artifact_root=root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


def test_fixture_mode_rejects_governed_artifact_roots(tmp_path: Path) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, _ = _feature_fixture(matrix_root)

    with pytest.raises(ResearchIndexBuildError, match="cannot target governed"):
        build_research_index(
            matrix_manifest_path=manifest_path,
            matrix_artifact_root=matrix_root,
            output_root=DEFAULT_INDEX_ROOT,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )
    with pytest.raises(ResearchIndexBuildError, match="cannot target governed"):
        load_feature_matrix(
            manifest_path,
            artifact_root=DEFAULT_MATRIX_ARTIFACT_ROOT,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


def test_index_write_failure_never_publishes_partial_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, _ = _feature_fixture(matrix_root)
    index_root = tmp_path / "index"
    original_write = os.write
    writes = 0

    def fail_after_partial_write(descriptor: int, payload: Any) -> int:
        nonlocal writes
        writes += 1
        if writes == 1:
            data = memoryview(payload)
            original_write(descriptor, data[: min(8, len(data))])
            raise OSError("simulated index write failure")
        return original_write(descriptor, payload)

    monkeypatch.setattr("scouting.modeling.research.os.write", fail_after_partial_write)
    with pytest.raises(OSError, match="simulated index write failure"):
        build_research_index(
            matrix_manifest_path=manifest_path,
            matrix_artifact_root=matrix_root,
            output_root=index_root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )

    assert tuple(index_root.iterdir()) == ()


def test_index_loader_rejects_stale_matrix_and_immutable_conflict(tmp_path: Path) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, matrix_manifest = _feature_fixture(matrix_root)
    index_root = tmp_path / "index"
    build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=matrix_root,
        output_root=index_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )

    stale_payload = matrix_manifest.model_dump(mode="json")
    stale_payload["matrix_version"] = "stale-matrix-v2"
    stale = FeatureMatrixManifest.model_validate_json(_self_digest_manifest(stale_payload))
    with pytest.raises(ResearchIndexBuildError, match="stale or incompatible"):
        load_research_index(
            index_root,
            matrix_manifest=stale,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )

    _write_private(index_root / "scaler-center.npy", b"incompatible")
    with pytest.raises(ResearchIndexBuildError, match="immutable index artifact conflicts"):
        build_research_index(
            matrix_manifest_path=manifest_path,
            matrix_artifact_root=matrix_root,
            output_root=index_root,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


def test_index_loader_rejects_catalogue_vector_contradiction(tmp_path: Path) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, matrix_manifest = _feature_fixture(matrix_root)
    index_root = tmp_path / "index"
    build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=matrix_root,
        output_root=index_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    catalogue_path = index_root / INDEX_ARTIFACT_PATHS[INDEX_CATALOGUE_ROLE]
    rows = [json.loads(line) for line in catalogue_path.read_bytes().splitlines()]
    rows[0]["feature_values"][0] = 99.0
    payload = canonical_jsonl_bytes(rows)
    _write_private(catalogue_path, payload)
    semantic = hashlib.sha256(canonical_json_bytes(rows)).hexdigest()

    def bind_catalogue_forgery(manifest: dict[str, Any]) -> None:
        file = next(item for item in manifest["files"] if item["role"] == INDEX_CATALOGUE_ROLE)
        file.update(
            {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
                "semantic_digest": semantic,
            }
        )
        manifest["catalogue_digest"] = semantic

    _rewrite_index_manifest(index_root, bind_catalogue_forgery)
    with pytest.raises(ResearchIndexBuildError, match="do not reproduce"):
        load_research_index(
            index_root,
            matrix_manifest=matrix_manifest,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


def test_index_loader_rejects_same_player_twice_within_competition_season(
    tmp_path: Path,
) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, matrix_manifest = _feature_fixture(matrix_root)
    index_root = tmp_path / "index"
    build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=matrix_root,
        output_root=index_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    catalogue_path = index_root / INDEX_ARTIFACT_PATHS[INDEX_CATALOGUE_ROLE]
    rows = [json.loads(line) for line in catalogue_path.read_bytes().splitlines()]
    rows[1]["player_id"] = rows[0]["player_id"]
    payload = canonical_jsonl_bytes(rows)
    _write_private(catalogue_path, payload)
    semantic = hashlib.sha256(canonical_json_bytes(rows)).hexdigest()

    def bind_duplicate(manifest: dict[str, Any]) -> None:
        file = next(item for item in manifest["files"] if item["role"] == INDEX_CATALOGUE_ROLE)
        file.update(
            {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
                "semantic_digest": semantic,
            }
        )
        manifest["catalogue_digest"] = semantic

    _rewrite_index_manifest(index_root, bind_duplicate)
    with pytest.raises(
        ResearchIndexBuildError,
        match="duplicate player/competition/season",
    ):
        load_research_index(
            index_root,
            matrix_manifest=matrix_manifest,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )


@pytest.mark.parametrize("encoding", ("big_endian", "fortran"))
def test_index_loader_rejects_dtype_and_memory_order_forgery(tmp_path: Path, encoding: str) -> None:
    matrix_root = tmp_path / "matrix"
    manifest_path, matrix_manifest = _feature_fixture(matrix_root)
    index_root = tmp_path / "index"
    build_research_index(
        matrix_manifest_path=manifest_path,
        matrix_artifact_root=matrix_root,
        output_root=index_root,
        mode=ResearchIndexBuildMode.TEST_FIXTURE,
    )
    target = index_root / INDEX_ARTIFACT_PATHS[INDEX_VECTORS_ROLE]
    if encoding == "big_endian":
        forged = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=">f8")
    else:
        forged = np.asfortranarray(np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype="<f8"))
    buffer = io.BytesIO()
    np.lib.format.write_array(buffer, forged, version=(2, 0), allow_pickle=False)
    payload = buffer.getvalue()
    _write_private(target, payload)

    def bind_forgery(manifest: dict[str, Any]) -> None:
        file = next(item for item in manifest["files"] if item["role"] == INDEX_VECTORS_ROLE)
        file.update(
            {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
                "semantic_digest": "f" * 64,
            }
        )

    _rewrite_index_manifest(index_root, bind_forgery)
    with pytest.raises(ResearchIndexBuildError, match="dtype/order/shape"):
        load_research_index(
            index_root,
            matrix_manifest=matrix_manifest,
            mode=ResearchIndexBuildMode.TEST_FIXTURE,
        )

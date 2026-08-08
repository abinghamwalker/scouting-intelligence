"""Integration evidence for immutable W09 research experiment persistence."""

from __future__ import annotations

import ast
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError

from scouting.contracts.research import (
    FeatureContribution,
    FeatureMatrixRow,
    FeatureValueState,
    FeatureWeight,
    MinuteEvidenceState,
    NamedFeatureValue,
    ResearchCandidate,
    ResearchComparison,
    ResearchComparisonRequest,
    ResearchCoverage,
    ResearchFeatureValue,
    ResearchFilters,
    ResearchMethod,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchQueryResult,
    ResearchReplayReason,
    ResearchReplayReceipt,
    ResearchReplayStatus,
    ResearchReportDescriptor,
    ResearchVersionPins,
    RetrievalPopulationCounts,
    SavedResearchExperiment,
    canonical_research_digest,
)
from scouting.storage.embedded import create_embedded_engine
from scouting.storage.formats import canonical_json_bytes
from scouting.storage.guarded import GuardedStorage, sha256_hex
from scouting.storage.research import (
    RESEARCH_REPORT_ROOT_NAME,
    ResearchExperimentNotFoundError,
    ResearchExperimentStore,
    ResearchStorageConflictError,
    ResearchStorageIntegrityError,
    research_replay_receipt_id,
    research_report_relative_path,
)

_CUTOFF = datetime(2019, 1, 1, tzinfo=UTC)
_REQUESTED = datetime(2026, 8, 5, 10, 0, tzinfo=UTC)
_RESULT_GENERATED = datetime(2026, 8, 5, 10, 1, tzinfo=UTC)
_REPORT_GENERATED = datetime(2026, 8, 5, 10, 2, tzinfo=UTC)
_EXPERIMENT_CREATED = datetime(2026, 8, 5, 10, 3, tzinfo=UTC)
_REPLAYED = datetime(2026, 8, 5, 10, 4, tzinfo=UTC)
_COMPETITION_ID = UUID("10000000-0000-0000-0000-000000000001")


def _digest(value: int) -> str:
    return f"{value:064x}"


def _pins() -> ResearchVersionPins:
    return ResearchVersionPins(
        feature_cutoff_ts=_CUTOFF,
        dataset_version="wyscout-2017-18-v1",
        dataset_manifest_digest=_digest(1),
        identity_bundle_digest=_digest(2),
        canonical_build_digest=_digest(3),
        matrix_version="player-season-v1",
        matrix_manifest_digest=_digest(4),
        matrix_digest=_digest(5),
        feature_registry_version="features-v1",
        feature_registry_digest=_digest(6),
        eligibility_policy_version="minutes-v1",
        eligibility_policy_digest=_digest(7),
        model_version="robust-scaling-v1",
        model_configuration_digest=_digest(8),
        scorer_version="weighted-distance-v1",
        scorer_code_digest=_digest(9),
        index_version="historical-index-v1",
        index_manifest_digest=_digest(10),
        catalogue_digest=_digest(11),
    )


def _request(*, limit: int = 1) -> ResearchQueryRequest:
    fields = {
        "query_id": UUID("30000000-0000-0000-0000-000000000001"),
        "requested_at": _REQUESTED,
        "feature_cutoff_ts": _CUTOFF,
        "pins": _pins(),
        "mode": ResearchQueryMode.WEIGHTED_PROFILE,
        "method": ResearchMethod.WEIGHTED_EUCLIDEAN,
        "profile": (NamedFeatureValue(feature_name="actions_per_90", value=1.0),),
        "weights": (FeatureWeight(feature_name="actions_per_90", weight=1.0),),
        "filters": ResearchFilters(competition_id=_COMPETITION_ID, season_id="2017-18"),
        "limit": limit,
    }
    draft = ResearchQueryRequest.model_construct(**fields, query_digest=_digest(0))
    return ResearchQueryRequest(
        **fields,
        query_digest=canonical_research_digest(draft.digest_projection()),
    )


def _result(request: ResearchQueryRequest) -> ResearchQueryResult:
    candidates = tuple(
        ResearchCandidate(
            rank=rank,
            grain_id=f"player-season:{rank}",
            player_id=UUID(f"20000000-0000-0000-0000-{rank:012d}"),
            display_name=f"Historical Player {rank}",
            competition_id=_COMPETITION_ID,
            position_code="MD",
            minutes=1_500.0,
            score=float(rank),
            contributions=(
                FeatureContribution(
                    feature_name="actions_per_90",
                    query_value=1.0,
                    candidate_value=float(rank + 1),
                    scaled_query_value=0.25,
                    scaled_candidate_value=float(rank) + 0.25,
                    scaled_contrast=float(rank),
                    weight=1.0,
                    contribution=float(rank * rank),
                ),
            ),
            limitations=("historical resemblance is not recruitment usefulness",),
        )
        for rank in range(1, request.limit + 1)
    )
    fields = {
        "result_id": UUID("40000000-0000-0000-0000-000000000001"),
        "request": request,
        "generated_at": _RESULT_GENERATED,
        "population": RetrievalPopulationCounts(
            matrix_rows=2,
            competition_rows=2,
            position_exclusions=0,
            minimum_minutes_exclusions=0,
            explicit_player_exclusions=0,
            exemplar_self_exclusions=0,
            filter_admitted_rows=2,
            missing_feature_exclusions=2 - len(candidates),
            scored_rows=len(candidates),
            returned_rows=len(candidates),
        ),
        "candidates": candidates,
        "warnings": ("Historical research only; no football relevance validation.",),
    }
    draft = ResearchQueryResult.model_construct(**fields, result_digest=_digest(0))
    return ResearchQueryResult(
        **fields,
        result_digest=canonical_research_digest(draft.digest_projection()),
    )


def _experiment(
    *,
    experiment_id: UUID | None = None,
    name: str = "W09 historical-player baseline",
    report_bytes: bytes | None = None,
    report_relative_path: str | None = None,
    include_comparison: bool = False,
) -> tuple[SavedResearchExperiment, bytes]:
    payload = canonical_json_bytes({"claim": "historical resemblance research only"})
    if report_bytes is not None:
        payload = report_bytes
    report_digest = sha256_hex(payload)
    request = _request(limit=2 if include_comparison else 1)
    result = _result(request)
    comparison = _comparison(request, result) if include_comparison else None
    report = ResearchReportDescriptor(
        report_format="json",
        report_relative_path=(
            report_relative_path
            if report_relative_path is not None
            else research_report_relative_path(report_digest, "json")
        ),
        report_digest=report_digest,
        generated_at=_REPORT_GENERATED,
        pins=request.pins,
        query_digest=request.query_digest,
        result_digest=result.result_digest,
        comparison_digest=comparison.comparison_digest if comparison is not None else None,
    )
    fields = {
        "experiment_id": experiment_id or UUID("50000000-0000-0000-0000-000000000001"),
        "name": name,
        "note": "Frozen local research evidence.",
        "created_at": _EXPERIMENT_CREATED,
        "request": request,
        "result": result,
        "comparison": comparison,
        "report": report,
    }
    draft = SavedResearchExperiment.model_construct(**fields, experiment_digest=_digest(0))
    experiment = SavedResearchExperiment(
        **fields,
        experiment_digest=canonical_research_digest(
            draft.model_dump(mode="json", exclude={"experiment_digest"})
        ),
    )
    return experiment, payload


def _comparison(
    query: ResearchQueryRequest,
    result: ResearchQueryResult,
) -> ResearchComparison:
    grain_ids = tuple(candidate.grain_id for candidate in result.candidates)
    request_fields = {
        "comparison_id": UUID("60000000-0000-0000-0000-000000000001"),
        "result_id": result.result_id,
        "result_digest": result.result_digest,
        "query_digest": query.query_digest,
        "pins": query.pins,
        "grain_ids": grain_ids,
    }
    request_draft = ResearchComparisonRequest.model_construct(
        **request_fields,
        comparison_request_digest=_digest(0),
    )
    comparison_request = ResearchComparisonRequest(
        **request_fields,
        comparison_request_digest=canonical_research_digest(request_draft.digest_projection()),
    )
    rows = tuple(
        _comparison_row(candidate, query.pins, ordinal)
        for ordinal, candidate in enumerate(result.candidates, start=1)
    )
    comparison_draft = ResearchComparison.model_construct(
        request=comparison_request,
        rows=rows,
        comparison_digest=_digest(0),
    )
    return ResearchComparison(
        request=comparison_request,
        rows=rows,
        comparison_digest=canonical_research_digest(
            comparison_draft.model_dump(mode="json", exclude={"comparison_digest"})
        ),
    )


def _comparison_row(
    candidate: ResearchCandidate,
    pins: ResearchVersionPins,
    ordinal: int,
) -> FeatureMatrixRow:
    return FeatureMatrixRow(
        grain_id=candidate.grain_id,
        player_id=candidate.player_id,
        display_name=candidate.display_name,
        competition_id=candidate.competition_id,
        competition_name="Historical Competition",
        season_id="2017-18",
        position_code=candidate.position_code,
        team_ids=(UUID(f"70000000-0000-0000-0000-{ordinal:012d}"),),
        team_names=(f"Historical Team {ordinal}",),
        minute_state=MinuteEvidenceState.EXACT,
        minutes=candidate.minutes,
        match_count=20,
        features=(
            ResearchFeatureValue(
                feature_name="actions_per_90",
                state=FeatureValueState.VALUE,
                value=float(ordinal + 1),
            ),
        ),
        missing_feature_names=(),
        coverage=ResearchCoverage(
            lineup_matches_observed=20,
            lineup_matches_expected=20,
            action_matches_observed=20,
            action_matches_expected=20,
            coordinate_actions_observed=100,
            coordinate_actions_expected=100,
        ),
        window_start_utc=datetime(2017, 7, 1, tzinfo=UTC),
        window_end_utc=datetime(2018, 7, 1, tzinfo=UTC),
        feature_cutoff_ts=pins.feature_cutoff_ts,
        dataset_manifest_digest=pins.dataset_manifest_digest,
        identity_bundle_digest=pins.identity_bundle_digest,
        canonical_build_digest=pins.canonical_build_digest,
        feature_registry_digest=pins.feature_registry_digest,
        eligibility_policy_digest=pins.eligibility_policy_digest,
        eligibility_decision_digest=_digest(20 + ordinal),
        source_lineage_digest=_digest(30 + ordinal),
        source_action_count=100,
    )


def _receipt(
    experiment: SavedResearchExperiment,
    *,
    replay_receipt_id: UUID | None = None,
) -> ResearchReplayReceipt:
    base = {
        "experiment_id": experiment.experiment_id,
        "saved_experiment_digest": experiment.experiment_digest,
        "saved_query_digest": experiment.request.query_digest,
        "replay_query_digest": experiment.request.query_digest,
        "replayed_at": _REPLAYED,
        "saved_pins": experiment.request.pins,
        "loaded_pins": experiment.request.pins,
        "original_result_id": experiment.result.result_id,
        "replay_result_id": experiment.result.result_id,
        "original_result_digest": experiment.result.result_digest,
        "replay_result_digest": experiment.result.result_digest,
        "status": ResearchReplayStatus.REPRODUCED,
        "reason": ResearchReplayReason.EXACT_REPRODUCTION,
    }
    identity_draft = ResearchReplayReceipt.model_construct(
        replay_receipt_id=UUID(int=0),
        **base,
        receipt_digest=_digest(0),
    )
    receipt_id = replay_receipt_id or research_replay_receipt_id(identity_draft)
    digest_draft = ResearchReplayReceipt.model_construct(
        replay_receipt_id=receipt_id,
        **base,
        receipt_digest=_digest(0),
    )
    return ResearchReplayReceipt(
        replay_receipt_id=receipt_id,
        **base,
        receipt_digest=canonical_research_digest(digest_draft.digest_projection()),
    )


def _result_mismatch_receipt(
    experiment: SavedResearchExperiment,
    *,
    replay_query_digest: str | None = None,
    validate: bool = True,
) -> ResearchReplayReceipt:
    base = {
        "experiment_id": experiment.experiment_id,
        "saved_experiment_digest": experiment.experiment_digest,
        "saved_query_digest": experiment.request.query_digest,
        "replay_query_digest": replay_query_digest or experiment.request.query_digest,
        "replayed_at": _REPLAYED,
        "saved_pins": experiment.request.pins,
        "loaded_pins": experiment.request.pins,
        "original_result_id": experiment.result.result_id,
        "replay_result_id": UUID("40000000-0000-0000-0000-000000000099"),
        "original_result_digest": experiment.result.result_digest,
        "replay_result_digest": _digest(61),
        "status": ResearchReplayStatus.RESULT_MISMATCH,
        "reason": ResearchReplayReason.DETERMINISTIC_RESULT_MISMATCH,
    }
    identity_draft = ResearchReplayReceipt.model_construct(
        replay_receipt_id=UUID(int=0),
        **base,
        receipt_digest=_digest(0),
    )
    receipt_id = research_replay_receipt_id(identity_draft)
    digest_draft = ResearchReplayReceipt.model_construct(
        replay_receipt_id=receipt_id,
        **base,
        receipt_digest=_digest(0),
    )
    receipt_digest = canonical_research_digest(digest_draft.digest_projection())
    if not validate:
        return ResearchReplayReceipt.model_construct(
            replay_receipt_id=receipt_id,
            **base,
            receipt_digest=receipt_digest,
        )
    return ResearchReplayReceipt(
        replay_receipt_id=receipt_id,
        **base,
        receipt_digest=receipt_digest,
    )


@pytest.fixture
def persisted(
    tmp_path: Path,
) -> Iterator[tuple[ResearchExperimentStore, Engine, GuardedStorage]]:
    engine = create_embedded_engine(
        tmp_path / "research.sqlite3",
        allowed_root=tmp_path,
    )
    storage = GuardedStorage({RESEARCH_REPORT_ROOT_NAME: tmp_path / "research-reports"})
    yield ResearchExperimentStore(engine, storage), engine, storage
    engine.dispose()


def test_save_load_list_and_identical_retry_preserve_exact_contract_json(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, storage = persisted
    experiment, report_bytes = _experiment()

    assert store.save_experiment(experiment, report_bytes) == experiment
    assert store.save_experiment(experiment, report_bytes) == experiment
    assert store.load_experiment(experiment.experiment_id) == experiment
    assert store.load_report_bytes(experiment.experiment_id) == report_bytes
    summaries = store.list_experiments()
    assert len(summaries) == 1
    assert summaries[0].experiment_id == experiment.experiment_id
    assert summaries[0].result_id == experiment.result.result_id
    assert summaries[0].report_digest == experiment.report.report_digest
    assert summaries[0].report_format == experiment.report.report_format
    assert summaries[0].experiment_digest == experiment.experiment_digest
    assert (
        storage.read_bytes(
            RESEARCH_REPORT_ROOT_NAME,
            experiment.report.report_relative_path,
        )
        == report_bytes
    )

    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    "SELECT request_json, result_json, comparison_json, report_json "
                    "FROM research_experiments"
                )
            )
            .mappings()
            .one()
        )
    assert (
        row["request_json"]
        == canonical_json_bytes(experiment.request.model_dump(mode="json")).decode()
    )
    assert (
        row["result_json"]
        == canonical_json_bytes(experiment.result.model_dump(mode="json")).decode()
    )
    assert row["comparison_json"] is None
    assert (
        row["report_json"]
        == canonical_json_bytes(experiment.report.model_dump(mode="json")).decode()
    )


def test_list_experiments_uses_only_summary_columns_and_never_reads_reports(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, _, storage = persisted
    experiment, report_bytes = _experiment()
    store.save_experiment(experiment, report_bytes)

    def reject_full_load(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise AssertionError("list attempted full experiment verification")

    monkeypatch.setattr(store, "_verified_experiment_from_row", reject_full_load)
    monkeypatch.setattr(storage, "read_bytes", reject_full_load)

    summaries = store.list_experiments()
    assert len(summaries) == 1
    assert summaries[0].experiment_id == experiment.experiment_id
    assert summaries[0].report_digest == experiment.report.report_digest


def test_scaled_explanation_operands_round_trip_exactly(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    experiment, report_bytes = _experiment()

    store.save_experiment(experiment, report_bytes)
    loaded = store.load_experiment(experiment.experiment_id)
    contribution = loaded.result.candidates[0].contributions[0]
    assert contribution.scaled_query_value == 0.25
    assert contribution.scaled_candidate_value == 1.25
    assert contribution.scaled_contrast == 1.0
    assert contribution.contribution == 1.0

    with engine.connect() as connection:
        persisted_result = connection.execute(
            text("SELECT result_json FROM research_experiments")
        ).scalar_one()
    persisted_contribution = json.loads(persisted_result)["candidates"][0]["contributions"][0]
    assert persisted_contribution == contribution.model_dump(mode="json")


def test_non_null_comparison_round_trips_exactly(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    experiment, report_bytes = _experiment(include_comparison=True)

    assert experiment.comparison is not None
    assert store.save_experiment(experiment, report_bytes) == experiment
    assert store.load_experiment(experiment.experiment_id) == experiment
    with engine.connect() as connection:
        comparison_json = connection.execute(
            text("SELECT comparison_json FROM research_experiments")
        ).scalar_one()
    assert (
        comparison_json
        == canonical_json_bytes(experiment.comparison.model_dump(mode="json")).decode()
    )


def test_same_experiment_id_cannot_bind_different_immutable_state(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    original, report_bytes = _experiment()
    conflicting, _ = _experiment(
        experiment_id=original.experiment_id,
        name="A different immutable experiment",
    )
    store.save_experiment(original, report_bytes)

    with pytest.raises(ResearchStorageConflictError, match="different immutable state"):
        store.save_experiment(conflicting, report_bytes)
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM research_experiments")).scalar_one() == 1
        )


def test_identical_content_address_can_be_shared_by_distinct_experiments(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    first, report_bytes = _experiment()
    second, _ = _experiment(
        experiment_id=UUID("50000000-0000-0000-0000-000000000002"),
        name="Second saved view of the same frozen result",
    )

    assert store.save_experiment(first, report_bytes) == first
    assert store.save_experiment(second, report_bytes) == second
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM research_experiments")).scalar_one() == 2
        )


@pytest.mark.parametrize(
    "payload,path_factory,error",
    [
        (
            b'{"claim":"different bytes"}',
            None,
            "report bytes do not match report_digest",
        ),
        (
            None,
            lambda digest: f"reports/{digest}.json",
            "not the digest content address",
        ),
    ],
)
def test_report_digest_and_content_address_mismatch_leave_no_database_state(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
    payload: bytes | None,
    path_factory: object,
    error: str,
) -> None:
    store, engine, _ = persisted
    experiment, report_bytes = _experiment()
    submitted = payload if payload is not None else report_bytes
    if callable(path_factory):
        replacement_path = path_factory(experiment.report.report_digest)
        experiment, report_bytes = _experiment(report_relative_path=replacement_path)
        submitted = report_bytes

    with pytest.raises(ResearchStorageIntegrityError, match=error):
        store.save_experiment(experiment, submitted)
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM research_experiments")).scalar_one() == 0
        )


def test_noncanonical_json_report_and_guarded_traversal_fail_closed(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    noncanonical = b'{ "claim": "historical resemblance research only" }'
    experiment, _ = _experiment(report_bytes=noncanonical)
    with pytest.raises(ResearchStorageIntegrityError, match="not canonical"):
        store.save_experiment(experiment, noncanonical)

    valid, report_bytes = _experiment()
    unsafe_report = valid.report.model_copy(
        update={"report_relative_path": f"../{valid.report.report_digest}.json"}
    )
    unsafe = valid.model_copy(update={"report": unsafe_report})
    with pytest.raises(ResearchStorageIntegrityError, match="contract rejected"):
        store.save_experiment(unsafe, report_bytes)

    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM research_experiments")).scalar_one() == 0
        )


def test_guarded_artifact_conflict_rolls_back_database_insert(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, storage = persisted
    experiment, report_bytes = _experiment()
    storage.write_bytes(
        RESEARCH_REPORT_ROOT_NAME,
        experiment.report.report_relative_path,
        b"conflicting artifact bytes",
        media_type="application/json",
        lineage={"source": "conflict fixture"},
        retention={"append_only": True},
    )

    with pytest.raises(ResearchStorageConflictError, match="content address conflicts"):
        store.save_experiment(experiment, report_bytes)
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM research_experiments")).scalar_one() == 0
        )


def test_missing_experiment_fails_closed(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, _, _ = persisted
    missing_id = uuid4()
    with pytest.raises(ResearchExperimentNotFoundError):
        store.load_experiment(missing_id)
    with pytest.raises(ResearchExperimentNotFoundError):
        store.list_replay_receipts(missing_id)


def test_replay_receipt_round_trip_is_idempotent_and_keeps_exact_pins(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    experiment, report_bytes = _experiment()
    store.save_experiment(experiment, report_bytes)
    receipt = _receipt(experiment)

    assert store.append_replay_receipt(receipt) == receipt.replay_receipt_id
    assert store.append_replay_receipt(receipt) == receipt.replay_receipt_id
    assert store.list_replay_receipts(experiment.experiment_id) == (receipt,)
    assert receipt.saved_pins == experiment.request.pins
    assert receipt.loaded_pins == experiment.request.pins

    with engine.connect() as connection:
        row = (
            connection.execute(
                text("SELECT reproduced, receipt_json FROM research_replay_receipts")
            )
            .mappings()
            .one()
        )
    assert row["reproduced"] == 1
    assert row["receipt_json"] == canonical_json_bytes(receipt.model_dump(mode="json")).decode()


def test_result_mismatch_receipt_requires_and_persists_the_exact_saved_query(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    experiment, report_bytes = _experiment()
    store.save_experiment(experiment, report_bytes)
    valid = _result_mismatch_receipt(experiment)

    assert store.append_replay_receipt(valid) == valid.replay_receipt_id
    assert store.list_replay_receipts(experiment.experiment_id) == (valid,)
    assert valid.saved_query_digest == experiment.request.query_digest
    assert valid.replay_query_digest == experiment.request.query_digest
    assert valid.status is ResearchReplayStatus.RESULT_MISMATCH

    evasion = _result_mismatch_receipt(
        experiment,
        replay_query_digest=_digest(62),
        validate=False,
    )
    with pytest.raises(ResearchStorageIntegrityError, match="receipt contract rejected"):
        store.append_replay_receipt(evasion)
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM research_replay_receipts")).scalar_one()
            == 1
        )


def test_receipt_must_bind_full_experiment_and_deterministic_identity(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    experiment, report_bytes = _experiment()
    store.save_experiment(experiment, report_bytes)

    wrong_id = _receipt(experiment, replay_receipt_id=uuid4())
    with pytest.raises(ResearchStorageIntegrityError, match="deterministic semantic identity"):
        store.append_replay_receipt(wrong_id)

    valid = _receipt(experiment)
    altered_fields = {
        field_name: getattr(valid, field_name)
        for field_name in ResearchReplayReceipt.model_fields
        if field_name not in {"replay_receipt_id", "receipt_digest"}
    }
    altered_fields["saved_experiment_digest"] = _digest(63)
    altered_identity_draft = ResearchReplayReceipt.model_construct(
        replay_receipt_id=UUID(int=0),
        **altered_fields,
        receipt_digest=_digest(0),
    )
    altered_id = research_replay_receipt_id(altered_identity_draft)
    altered_digest_draft = ResearchReplayReceipt.model_construct(
        replay_receipt_id=altered_id,
        **altered_fields,
        receipt_digest=_digest(0),
    )
    altered = ResearchReplayReceipt(
        replay_receipt_id=altered_id,
        **altered_fields,
        receipt_digest=canonical_research_digest(altered_digest_draft.digest_projection()),
    )
    with pytest.raises(ResearchStorageIntegrityError, match="saved experiment digest"):
        store.append_replay_receipt(altered)

    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM research_replay_receipts")).scalar_one()
            == 0
        )


def test_sqlite_triggers_keep_experiments_and_receipts_append_only(
    persisted: tuple[ResearchExperimentStore, Engine, GuardedStorage],
) -> None:
    store, engine, _ = persisted
    experiment, report_bytes = _experiment()
    store.save_experiment(experiment, report_bytes)
    receipt = _receipt(experiment)
    store.append_replay_receipt(receipt)

    mutations = (
        "UPDATE research_experiments SET name = 'changed'",
        "DELETE FROM research_experiments",
        "UPDATE research_replay_receipts SET reproduced = 0",
        "DELETE FROM research_replay_receipts",
    )
    for statement in mutations:
        with pytest.raises(IntegrityError, match="append-only"):
            with engine.begin() as connection:
                connection.execute(text(statement))


def test_research_storage_has_no_w08_auth_or_audit_dependency() -> None:
    module_path = Path(__file__).resolve().parents[2] / "src/scouting/storage/research.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imports.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    forbidden_segments = {"auth", "audit", "workflow", "w08"}
    assert all(forbidden_segments.isdisjoint(name.split(".")) for name in imports)

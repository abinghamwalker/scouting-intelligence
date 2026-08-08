"""SQLite and browser-boundary integration tests for the W10 study console."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest
from fastapi.testclient import TestClient

from scouting.contracts.expert_relevance import (
    AssessmentBasisV2,
    EvidenceSufficiencyV2,
    ExpertExperienceKind,
    ExpertRelevanceProtocol,
    ExpertStudyPresentationBundle,
    JudgementState,
    PresentationKind,
    StudyMode,
)
from scouting.contracts.research import canonical_research_digest
from scouting.storage.expert_study import (
    PROTOCOL_APPROVAL_CONFIRMATION,
    ExpertStudyConfigurationError,
    ExpertStudyConflictError,
    ExpertStudyIntegrityError,
    ExpertStudyPreparationError,
    ExpertStudyStore,
    PreparedStudySession,
    StudySessionSnapshot,
    V2MechanicsPilotStore,
)
from scouting.storage.formats import canonical_json_bytes
from scouting.web.w10_expert_study import (
    create_w10_expert_study_app,
    create_w10_v2_mechanics_pilot_app,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 5, 18, 0, tzinfo=UTC)
CONSENT = {
    "voluntary_participation": True,
    "local_pseudonymous_storage": True,
    "withdrawal_before_submission_understood": True,
    "immutable_after_submission_understood": True,
    "research_limitations_understood": True,
}


def _v2_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> V2MechanicsPilotStore:
    """Build only participant-safe fixture authority beneath pytest's temporary root."""
    from scouting.data_products.wyscout.expert_evidence import (
        build_participant_evidence_comparison_v2,
    )

    fixture_spec = importlib.util.spec_from_file_location(
        "w10_v2_evidence_fixture", ROOT / "tests/unit/test_w10_expert_evidence_v2.py"
    )
    assert fixture_spec is not None and fixture_spec.loader is not None
    fixture_module = importlib.util.module_from_spec(fixture_spec)
    fixture_spec.loader.exec_module(fixture_module)
    fixture_bundles = fixture_module._fixture_bundles

    exemplar, candidate = fixture_bundles(monkeypatch)
    comparison = build_participant_evidence_comparison_v2(exemplar, candidate)
    authority = {
        "schema_version": 2,
        "authority_version": "w10-v2-mechanics-pilot-authority-v1",
        "lane": "MECHANICS_PILOT",
        "comparisons": [comparison.model_dump(mode="json")],
    }
    path = tmp_path / "mechanics-pilot-authority-v1.json"
    path.write_bytes(canonical_json_bytes(authority))
    return V2MechanicsPilotStore(
        database_path=tmp_path / "mechanics-pilot-v2.sqlite3",
        authority_path=path,
        allowed_root=tmp_path,
        clock=lambda: NOW,
    )


def _authority() -> tuple[ExpertRelevanceProtocol, ExpertStudyPresentationBundle]:
    return (
        ExpertRelevanceProtocol.model_validate_json(
            (ROOT / "configs/evaluation/w10-expert-relevance-protocol-v1.json").read_bytes()
        ),
        ExpertStudyPresentationBundle.model_validate_json(
            (ROOT / "configs/evaluation/w10-expert-study-presentation-v1.json").read_bytes()
        ),
    )


def _stores(root: Path) -> tuple[ExpertStudyStore, ExpertStudyStore]:
    root.mkdir(parents=True, exist_ok=True)
    protocol, presentation = _authority()
    return (
        ExpertStudyStore(
            database_path=root / "pilot.sqlite3",
            capture_root=root / "pilot-captures",
            allowed_root=root,
            mode=StudyMode.MECHANICS_PILOT,
            protocol=protocol,
            presentation=presentation,
            test_only=True,
            clock=lambda: NOW,
        ),
        ExpertStudyStore(
            database_path=root / "formal.sqlite3",
            capture_root=root / "formal-captures",
            allowed_root=root,
            mode=StudyMode.FORMAL_G_RW4,
            protocol=protocol,
            presentation=presentation,
            test_only=True,
            clock=lambda: NOW,
        ),
    )


def _prepare(store: ExpertStudyStore, code: str) -> PreparedStudySession:
    return store.prepare_session(
        participant_code=code,
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )


def _record_current(
    store: ExpertStudyStore,
    capability: str,
    snapshot: StudySessionSnapshot,
    *,
    ordinal: int,
) -> StudySessionSnapshot:
    task = store.current_task(snapshot)
    assert task is not None
    command_id = uuid5(
        NAMESPACE_URL,
        f"w10-test-judgement:{snapshot.session.session_id}:{task.presentation.presentation_id}",
    )
    request_digest = hashlib.sha256(f"request:{command_id}".encode()).hexdigest()
    state = (
        JudgementState.ABSTAIN
        if ordinal == 0
        else JudgementState.UNABLE_TO_ASSESS
        if ordinal == 1
        else JudgementState.RATED
    )
    return store.record_judgement(
        capability=capability,
        command_id=command_id,
        expected_revision=snapshot.revision,
        request_digest=request_digest,
        presentation_id=task.presentation.presentation_id,
        state=state,
        relevance_rating=3 if state is JudgementState.RATED else None,
        confidence=4 if state is JudgementState.RATED else None,
        failure_category=None,
        explanation="Historical role and style fit." if state is JudgementState.RATED else None,
    )


def _record_remaining(
    store: ExpertStudyStore,
    capability: str,
    snapshot: StudySessionSnapshot,
) -> StudySessionSnapshot:
    while store.current_task(snapshot) is not None:
        snapshot = _record_current(
            store,
            capability,
            snapshot,
            ordinal=snapshot.answered_count,
        )
    return snapshot


def _session_form(csrf: str, code: str, lane: str = "pilot") -> dict[str, str]:
    return {
        "csrf": csrf,
        "participant_code": code,
        "years_experience": "3",
        "experience_professional_scouting": "true",
        "assessed_players_within_window": "true",
        **{name: "true" for name in CONSENT},
        "lane": lane,
    }


def test_pilot_is_separate_resumable_idempotent_and_immutable(tmp_path: Path) -> None:
    pilot, _ = _stores(tmp_path)
    prepared = _prepare(pilot, "PILOT-01")
    snapshot = prepared.snapshot

    assert snapshot.total_count == 22
    assert (
        sum(item.kind is PresentationKind.PRIMARY for item in snapshot.session.presentations) == 20
    )
    assert sum(item.kind is PresentationKind.REPEAT for item in snapshot.session.presentations) == 2
    assert snapshot.session.approval_digest is None
    assert pilot.load_session(prepared.capability).session == snapshot.session

    task = pilot.current_task(snapshot)
    assert task is not None
    command_id = uuid5(NAMESPACE_URL, "pilot-idempotency-command")
    request_digest = hashlib.sha256(b"pilot-idempotency-request").hexdigest()
    with pytest.raises(TypeError, match="lowercase SHA-256"):
        pilot.record_judgement(
            capability=prepared.capability,
            command_id=command_id,
            expected_revision=0,
            request_digest="A" * 64,
            presentation_id=task.presentation.presentation_id,
            state=JudgementState.ABSTAIN,
            relevance_rating=None,
            confidence=None,
            failure_category=None,
            explanation=None,
        )
    first = pilot.record_judgement(
        capability=prepared.capability,
        command_id=command_id,
        expected_revision=0,
        request_digest=request_digest,
        presentation_id=task.presentation.presentation_id,
        state=JudgementState.ABSTAIN,
        relevance_rating=None,
        confidence=None,
        failure_category=None,
        explanation=None,
    )
    exact_retry = pilot.record_judgement(
        capability=prepared.capability,
        command_id=command_id,
        expected_revision=0,
        request_digest=request_digest,
        presentation_id=task.presentation.presentation_id,
        state=JudgementState.ABSTAIN,
        relevance_rating=None,
        confidence=None,
        failure_category=None,
        explanation=None,
    )
    assert exact_retry.revision == first.revision == 1
    assert exact_retry.judgements == first.judgements

    with pytest.raises(ExpertStudyConflictError, match="different exact operation or request"):
        pilot.record_judgement(
            capability=prepared.capability,
            command_id=command_id,
            expected_revision=1,
            request_digest="f" * 64,
            presentation_id=task.presentation.presentation_id,
            state=JudgementState.ABSTAIN,
            relevance_rating=None,
            confidence=None,
            failure_category=None,
            explanation=None,
        )
    with pytest.raises(ExpertStudyConflictError, match="revision is stale"):
        pilot.record_judgement(
            capability=prepared.capability,
            command_id=uuid5(NAMESPACE_URL, "pilot-stale-command"),
            expected_revision=0,
            request_digest="e" * 64,
            presentation_id=snapshot.session.presentations[1].presentation_id,
            state=JudgementState.ABSTAIN,
            relevance_rating=None,
            confidence=None,
            failure_category=None,
            explanation=None,
        )

    completed_snapshot = _record_remaining(pilot, prepared.capability, first)
    correction_target = completed_snapshot.session.presentations[0]
    correction_command = uuid5(NAMESPACE_URL, "pilot-pre-submit-correction")
    correction_digest = hashlib.sha256(b"pilot-pre-submit-correction").hexdigest()
    completed_snapshot = pilot.revise_judgement(
        capability=prepared.capability,
        command_id=correction_command,
        expected_revision=completed_snapshot.revision,
        request_digest=correction_digest,
        presentation_id=correction_target.presentation_id,
        state=JudgementState.RATED,
        relevance_rating=2,
        confidence=3,
        failure_category=None,
        explanation="Corrected before immutable submission.",
    )
    corrected = next(
        item
        for item in completed_snapshot.judgements
        if item.presentation_id == correction_target.presentation_id
    )
    assert corrected.state is JudgementState.RATED
    assert corrected.relevance_rating == 2
    exact_correction_retry = pilot.revise_judgement(
        capability=prepared.capability,
        command_id=correction_command,
        expected_revision=completed_snapshot.revision - 1,
        request_digest=correction_digest,
        presentation_id=correction_target.presentation_id,
        state=JudgementState.RATED,
        relevance_rating=2,
        confidence=3,
        failure_category=None,
        explanation="Corrected before immutable submission.",
    )
    assert exact_correction_retry.revision == completed_snapshot.revision
    with sqlite3.connect(tmp_path / "pilot.sqlite3") as connection:
        history = connection.execute(
            "SELECT revision_ordinal, supersedes_judgement_digest FROM "
            "study_judgement_revisions WHERE session_id = ? AND presentation_id = ? "
            "ORDER BY revision_ordinal",
            (str(completed_snapshot.session.session_id), str(correction_target.presentation_id)),
        ).fetchall()
        assert len(history) == 2
        assert history[0][1] is None
        assert history[1][1] is not None
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE study_judgement_revisions SET supersedes_judgement_digest = NULL "
                "WHERE session_id = ? AND presentation_id = ? AND revision_ordinal = 2",
                (
                    str(completed_snapshot.session.session_id),
                    str(correction_target.presentation_id),
                ),
            )
    final_presentation = completed_snapshot.session.presentations[-1]
    final_judgement_command = uuid5(
        NAMESPACE_URL,
        f"w10-test-judgement:{completed_snapshot.session.session_id}:"
        f"{final_presentation.presentation_id}",
    )
    final_judgement_digest = hashlib.sha256(
        f"request:{final_judgement_command}".encode()
    ).hexdigest()
    with pytest.raises(ExpertStudyConflictError, match="different exact operation"):
        pilot.complete_session(
            capability=prepared.capability,
            command_id=final_judgement_command,
            expected_revision=completed_snapshot.revision,
            request_digest=final_judgement_digest,
        )
    completion_command = uuid5(NAMESPACE_URL, "pilot-completion-command")
    completion_digest = hashlib.sha256(b"pilot-completion-request").hexdigest()
    completion = pilot.complete_session(
        capability=prepared.capability,
        command_id=completion_command,
        expected_revision=completed_snapshot.revision,
        request_digest=completion_digest,
    )
    retry = pilot.complete_session(
        capability=prepared.capability,
        command_id=completion_command,
        expected_revision=completed_snapshot.revision,
        request_digest=completion_digest,
    )
    assert retry == completion
    assert completion["formal_evidence_recorded"] is False
    assert completion["record_type"] == "w10_expert_relevance_mechanics_pilot_capture"

    captures = tuple((tmp_path / "pilot-captures").rglob("*.json"))
    assert len(captures) == 1
    capture_bytes = captures[0].read_bytes()
    assert capture_bytes == canonical_json_bytes(json.loads(capture_bytes))
    assert "formal-submissions" not in captures[0].as_posix()
    assert not (tmp_path / "pilot-captures/formal-submissions").exists()
    with pytest.raises(ExpertStudyPreparationError, match="pilot authority"):
        pilot.export_formal_evidence(tmp_path / "pilot-export.json")

    sealed = pilot.load_session(prepared.capability)
    assert sealed.complete
    with pytest.raises(ExpertStudyConflictError, match="completed study session is immutable"):
        pilot.record_judgement(
            capability=prepared.capability,
            command_id=uuid5(NAMESPACE_URL, "post-completion-command"),
            expected_revision=sealed.revision,
            request_digest="d" * 64,
            presentation_id=sealed.session.presentations[0].presentation_id,
            state=JudgementState.ABSTAIN,
            relevance_rating=None,
            confidence=None,
            failure_category=None,
            explanation=None,
        )


def test_formal_test_only_journey_uses_exact_keyed_repeats_and_concurrent_submit(
    tmp_path: Path,
) -> None:
    _, formal = _stores(tmp_path / "first")
    approval = formal.record_protocol_approval(
        approved_by_pseudonym="OWNER-01",
        confirmation=PROTOCOL_APPROVAL_CONFIRMATION,
    )
    prepared = _prepare(formal, "EXPERT-01")
    snapshot = prepared.snapshot

    assert snapshot.total_count == 82
    assert snapshot.session.approval_digest == approval.approval_digest
    assert snapshot.session.eligibility_digest == snapshot.eligibility.eligibility_digest
    assert snapshot.session.consent_digest == snapshot.consent.consent_digest
    primary = tuple(
        item for item in snapshot.session.presentations if item.kind is PresentationKind.PRIMARY
    )
    repeats = tuple(
        item for item in snapshot.session.presentations if item.kind is PresentationKind.REPEAT
    )
    assert all(item.kind is PresentationKind.PRIMARY for item in primary)
    assert all(item.kind is PresentationKind.REPEAT for item in repeats)
    assert {item.candidate_id for item in repeats} == set(
        formal.presentation.repeat_anchor_candidate_ids
    )
    assert snapshot.session.presentations[-1].kind is PresentationKind.PRIMARY
    assert all(item.presentation_ordinal < 82 for item in repeats)
    presentations_by_id = {item.presentation_id: item for item in snapshot.session.presentations}
    for repeat in repeats:
        anchor = presentations_by_id[repeat.repeat_of_presentation_id]
        intervening_primary_count = sum(
            item.kind is PresentationKind.PRIMARY
            and anchor.presentation_ordinal
            < item.presentation_ordinal
            < repeat.presentation_ordinal
            for item in snapshot.session.presentations
        )
        assert intervening_primary_count >= 10

    _, second_formal = _stores(tmp_path / "second")
    second_formal.record_protocol_approval(
        approved_by_pseudonym="OWNER-01",
        confirmation=PROTOCOL_APPROVAL_CONFIRMATION,
    )
    same_participant = _prepare(second_formal, "EXPERT-01")
    assert tuple(
        (item.query_id, item.candidate_id, item.kind)
        for item in same_participant.snapshot.session.presentations
    ) == tuple(
        (item.query_id, item.candidate_id, item.kind) for item in snapshot.session.presentations
    )

    complete_snapshot = _record_remaining(formal, prepared.capability, snapshot)
    assert complete_snapshot.answered_count == 82
    assert {item.state for item in complete_snapshot.judgements} >= {
        JudgementState.RATED,
        JudgementState.ABSTAIN,
        JudgementState.UNABLE_TO_ASSESS,
    }
    command_id = uuid5(NAMESPACE_URL, "formal-concurrent-completion")
    request_digest = hashlib.sha256(b"formal-concurrent-request").hexdigest()

    def submit() -> object:
        return formal.complete_session(
            capability=prepared.capability,
            command_id=command_id,
            expected_revision=complete_snapshot.revision,
            request_digest=request_digest,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(executor.map(lambda _: submit(), range(2)))
    assert results[0] == results[1]
    result = results[0]
    assert isinstance(result, dict)
    assert result["record_type"] == "w10_expert_relevance_test_only_formal_capture"
    assert result["test_only"] is True
    assert result["formal_evidence_recorded"] is False
    assert not (tmp_path / "first/formal-captures/formal-submissions").exists()
    assert not (tmp_path / "first/formal-captures/formal-receipts").exists()
    test_captures = tuple(
        (tmp_path / "first/formal-captures/test-only-formal-captures").rglob("*.json")
    )
    assert len(test_captures) == 1
    with pytest.raises(ExpertStudyPreparationError, match="TEST_ONLY"):
        formal.export_formal_evidence(tmp_path / "first/formal-export.json")


def test_completed_browser_session_detaches_without_mutating_evidence_and_next_resumes(
    tmp_path: Path,
) -> None:
    protocol, presentation = _authority()
    pilot, formal = _stores(tmp_path)
    app = create_w10_expert_study_app(
        protocol=protocol,
        presentation=presentation,
        pilot_store=pilot,
        formal_store=formal,
        allow_test_host=True,
    )
    client = TestClient(app, base_url="http://127.0.0.1")
    home = client.get("/w10")
    csrf = home.cookies["w10_study_csrf"]

    started = client.post(
        "/w10/sessions",
        data=_session_form(csrf, "PILOT-11"),
        follow_redirects=True,
    )
    assert started.status_code == 200
    assert "0 / 22" in started.text
    first_capability = client.cookies["w10_study_capability"]
    assert "0 / 22" in client.get("/w10").text

    refused = client.post(
        "/w10/detach",
        data={"csrf": csrf},
        follow_redirects=True,
    )
    assert refused.status_code == 409
    assert "in-progress session remains attached for safe resume" in refused.text
    assert client.cookies["w10_study_capability"] == first_capability

    complete_snapshot = _record_remaining(
        pilot,
        first_capability,
        pilot.load_session(first_capability),
    )
    review_page = client.get("/w10")
    assert "Review and correct responses before sealing" in review_page.text
    assert "Save append-only correction" in review_page.text
    assert "presentation kind" in review_page.text
    assert "repeat_of_presentation_id" not in review_page.text
    pilot.complete_session(
        capability=first_capability,
        command_id=uuid5(NAMESPACE_URL, "browser-first-completion"),
        expected_revision=complete_snapshot.revision,
        request_digest=hashlib.sha256(b"browser-first-completion").hexdigest(),
    )
    completion_page = client.get("/w10")
    assert "Finish and prepare next participant" in completion_page.text

    detached = client.post(
        "/w10/detach",
        data={"csrf": csrf},
        follow_redirects=True,
    )
    assert detached.status_code == 200
    assert "Start a pseudonymous local session" in detached.text
    assert "w10_study_capability" not in client.cookies
    assert pilot.load_session(first_capability).complete

    next_started = client.post(
        "/w10/sessions",
        data=_session_form(csrf, "PILOT-12"),
        follow_redirects=True,
    )
    assert next_started.status_code == 200
    assert "0 / 22" in next_started.text
    assert client.cookies["w10_study_capability"] != first_capability
    assert "0 / 22" in client.get("/w10").text


def test_existing_sqlite_authority_drift_fails_closed(tmp_path: Path) -> None:
    pilot, _ = _stores(tmp_path)
    _prepare(pilot, "PILOT-21")
    with sqlite3.connect(tmp_path / "pilot.sqlite3") as connection:
        connection.execute(
            "UPDATE expert_study_authority SET presentation_digest = ? WHERE authority_key = 1",
            ("0" * 64,),
        )

    protocol, presentation = _authority()
    reopened = ExpertStudyStore(
        database_path=tmp_path / "pilot.sqlite3",
        capture_root=tmp_path / "pilot-captures",
        allowed_root=tmp_path,
        mode=StudyMode.MECHANICS_PILOT,
        protocol=protocol,
        presentation=presentation,
        test_only=True,
        clock=lambda: NOW,
    )
    with pytest.raises(ExpertStudyConfigurationError, match="authority is incompatible"):
        _prepare(reopened, "PILOT-22")


def test_store_rejects_symlinked_or_hardlinked_paths_and_capture_collisions(
    tmp_path: Path,
) -> None:
    protocol, presentation = _authority()
    guarded = tmp_path / "guarded"
    guarded.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (guarded / "linked-parent").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ExpertStudyConfigurationError, match="symlink component"):
        ExpertStudyStore(
            database_path=guarded / "linked-parent/pilot.sqlite3",
            capture_root=guarded / "captures",
            allowed_root=guarded,
            mode=StudyMode.MECHANICS_PILOT,
            protocol=protocol,
            presentation=presentation,
            test_only=True,
        )
    with pytest.raises(ExpertStudyConfigurationError, match="symlink component"):
        ExpertStudyStore(
            database_path=guarded / "pilot.sqlite3",
            capture_root=guarded / "linked-parent/captures",
            allowed_root=guarded,
            mode=StudyMode.MECHANICS_PILOT,
            protocol=protocol,
            presentation=presentation,
            test_only=True,
        )

    original = guarded / "original.sqlite3"
    original.touch()
    (guarded / "pilot.sqlite3").hardlink_to(original)
    with pytest.raises(ExpertStudyConfigurationError, match="single-link regular file"):
        ExpertStudyStore(
            database_path=guarded / "pilot.sqlite3",
            capture_root=guarded / "captures",
            allowed_root=guarded,
            mode=StudyMode.MECHANICS_PILOT,
            protocol=protocol,
            presentation=presentation,
            test_only=True,
        )

    collision_root = tmp_path / "collision"
    pilot, _ = _stores(collision_root)
    prepared = _prepare(pilot, "PILOT-31")
    snapshot = _record_remaining(pilot, prepared.capability, prepared.snapshot)
    pilot.complete_session(
        capability=prepared.capability,
        command_id=uuid5(NAMESPACE_URL, "collision-completion"),
        expected_revision=snapshot.revision,
        request_digest=hashlib.sha256(b"collision-completion").hexdigest(),
    )
    capture = next((collision_root / "pilot-captures").rglob("*.json"))
    (collision_root / "capture-alias.json").hardlink_to(capture)
    with pytest.raises(ExpertStudyIntegrityError, match="unsafe collision"):
        pilot._write_content_addressed(  # noqa: SLF001 - integration safety boundary
            "pilot-captures",
            capture.stem,
            capture.read_bytes(),
        )
    with pytest.raises(ExpertStudyIntegrityError, match="not a single-link regular file"):
        pilot.load_session(prepared.capability)

    export_outside = tmp_path / "export-outside"
    export_outside.mkdir()
    (collision_root / "export-link").symlink_to(export_outside, target_is_directory=True)
    with pytest.raises(ExpertStudyConfigurationError, match="symlink component"):
        pilot._prepare_exclusive_export_target(  # noqa: SLF001 - path safety boundary
            collision_root / "export-link/formal-evidence.json"
        )


def test_v2_revalidates_database_confinement_on_every_public_operation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    guarded = tmp_path / "v2-guarded"
    guarded.mkdir()
    store = _v2_store(guarded, monkeypatch)
    capability, initial = store.prepare_session(
        participant_code="V2-CONFINEMENT-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    token, comparison, *_ = store.task(capability) or pytest.fail("missing v2 task")
    saved = store.record(
        capability=capability,
        command_id=uuid5(NAMESPACE_URL, "v2-confinement-record"),
        expected_revision=initial.revision,
        request_digest=hashlib.sha256(b"v2-confinement-record").hexdigest(),
        presentation_token=token,
        state=JudgementState.RATED,
        evidence_sufficiency=EvidenceSufficiencyV2.SUFFICIENT,
        assessment_basis=AssessmentBasisV2.SUPPLIED_EVIDENCE,
        relevance_rating=3,
        confidence=4,
        evidence_gap=None,
        citations=(
            next(
                family.label
                for family in comparison.exemplar.independent_descriptors
                if family.mandatory_for_selected_rubric
            ),
        ),
        explanation=None,
    )
    database = guarded / "mechanics-pilot-v2.sqlite3"
    escaped_database = tmp_path / "escaped-mechanics-pilot-v2.sqlite3"
    database.replace(escaped_database)
    database.symlink_to(escaped_database)

    with pytest.raises(ExpertStudyConfigurationError, match="symlink component"):
        store.load_session(capability)
    with pytest.raises(ExpertStudyConfigurationError, match="symlink component"):
        store.record(
            capability=capability,
            command_id=uuid5(NAMESPACE_URL, "v2-confinement-correction"),
            expected_revision=saved.revision,
            request_digest=hashlib.sha256(b"v2-confinement-correction").hexdigest(),
            presentation_token=token,
            state=JudgementState.RATED,
            evidence_sufficiency=EvidenceSufficiencyV2.SUFFICIENT,
            assessment_basis=AssessmentBasisV2.SUPPLIED_EVIDENCE,
            relevance_rating=3,
            confidence=3,
            evidence_gap=None,
            citations=(
                next(
                    family.label
                    for family in comparison.exemplar.independent_descriptors
                    if family.mandatory_for_selected_rubric
                ),
            ),
            explanation=None,
        )
    with pytest.raises(ExpertStudyConfigurationError, match="symlink component"):
        store.complete(
            capability=capability,
            command_id=uuid5(NAMESPACE_URL, "v2-confinement-complete"),
            expected_revision=saved.revision,
            request_digest=hashlib.sha256(b"v2-confinement-complete").hexdigest(),
        )

    with pytest.raises(ExpertStudyConfigurationError, match="filesystem root"):
        V2MechanicsPilotStore(
            database_path=guarded / "mechanics-pilot-v2.sqlite3",
            authority_path=guarded / "mechanics-pilot-authority-v1.json",
            allowed_root=Path("/"),
        )

    hardlink_root = tmp_path / "v2-hardlink"
    hardlink_root.mkdir()
    hardlink_store = _v2_store(hardlink_root, monkeypatch)
    hardlink_capability, _ = hardlink_store.prepare_session(
        participant_code="V2-HARDLINK-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    hardlink_database = hardlink_root / "mechanics-pilot-v2.sqlite3"
    outside_hardlink = tmp_path / "outside-hardlink.sqlite3"
    hardlink_database.replace(outside_hardlink)
    hardlink_database.hardlink_to(outside_hardlink)
    with pytest.raises(ExpertStudyConfigurationError, match="single-link regular file"):
        hardlink_store.load_session(hardlink_capability)

    nonregular_root = tmp_path / "v2-nonregular"
    nonregular_root.mkdir()
    nonregular_store = _v2_store(nonregular_root, monkeypatch)
    nonregular_capability, _ = nonregular_store.prepare_session(
        participant_code="V2-NONREGULAR-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    nonregular_database = nonregular_root / "mechanics-pilot-v2.sqlite3"
    nonregular_database.replace(tmp_path / "outside-nonregular.sqlite3")
    with pytest.raises(ExpertStudyConfigurationError, match="disappeared after initialization"):
        nonregular_store.load_session(nonregular_capability)
    nonregular_database.mkdir()
    with pytest.raises(ExpertStudyConfigurationError, match="single-link regular file"):
        nonregular_store.load_session(nonregular_capability)

    authority_root = tmp_path / "v2-authority-symlink"
    authority_root.mkdir()
    authority_store = _v2_store(authority_root, monkeypatch)
    authority_capability, _ = authority_store.prepare_session(
        participant_code="V2-AUTHORITY-PATH-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    authority_path = authority_root / "mechanics-pilot-authority-v1.json"
    outside_authority = tmp_path / "outside-mechanics-pilot-authority-v1.json"
    authority_path.replace(outside_authority)
    authority_path.symlink_to(outside_authority)
    with pytest.raises(ExpertStudyConfigurationError, match="symlink component"):
        authority_store.load_session(authority_capability)

    with pytest.raises(ExpertStudyConfigurationError, match="inside their guarded root"):
        V2MechanicsPilotStore(
            database_path=tmp_path / "outside/mechanics-pilot-v2.sqlite3",
            authority_path=authority_root / "mechanics-pilot-authority-v1.json",
            allowed_root=authority_root,
        )


def test_v2_each_connection_attests_exact_schema_trigger_and_authority_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _v2_store(tmp_path, monkeypatch)
    capability, initial = store.prepare_session(
        participant_code="V2-SCHEMA-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    token, comparison, *_ = store.task(capability) or pytest.fail("missing schema test task")
    saved = store.record(
        capability=capability,
        command_id=uuid5(NAMESPACE_URL, "v2-schema-record"),
        expected_revision=initial.revision,
        request_digest=hashlib.sha256(b"v2-schema-record").hexdigest(),
        presentation_token=token,
        state=JudgementState.RATED,
        evidence_sufficiency=EvidenceSufficiencyV2.SUFFICIENT,
        assessment_basis=AssessmentBasisV2.SUPPLIED_EVIDENCE,
        relevance_rating=3,
        confidence=4,
        evidence_gap=None,
        citations=(
            next(
                family.label
                for family in comparison.exemplar.independent_descriptors
                if family.mandatory_for_selected_rubric
            ),
        ),
        explanation=None,
    )
    database = tmp_path / "mechanics-pilot-v2.sqlite3"
    with sqlite3.connect(database) as con:
        original = con.execute(
            "SELECT judgement_json FROM v2_judgements WHERE session_id=?",
            (str(saved.session_id),),
        ).fetchone()[0]
        mutation = json.loads(original)
        mutation["confidence"] = 3
        mutation["judgement_digest"] = canonical_research_digest(
            {key: value for key, value in mutation.items() if key != "judgement_digest"}
        )
        encoded = canonical_json_bytes(mutation).decode()
        con.execute("DROP TRIGGER v2_revisions_no_update")
        con.execute("DROP TRIGGER v2_commands_no_update")
        con.execute(
            "UPDATE v2_judgements SET judgement_json=? WHERE session_id=?",
            (encoded, str(saved.session_id)),
        )
        con.execute(
            "UPDATE v2_judgement_revisions SET judgement_json=? WHERE session_id=?",
            (encoded, str(saved.session_id)),
        )
        con.execute(
            "UPDATE v2_commands SET response_json=? WHERE session_id=? AND command_kind='record'",
            (encoded, str(saved.session_id)),
        )

    for operation in (
        lambda: store.load_session(capability),
        lambda: store.review_tasks(capability),
        lambda: store.complete(
            capability=capability,
            command_id=uuid5(NAMESPACE_URL, "v2-schema-complete"),
            expected_revision=saved.revision,
            request_digest=hashlib.sha256(b"v2-schema-complete").hexdigest(),
        ),
    ):
        with pytest.raises(ExpertStudyConfigurationError, match="table or trigger SQL"):
            operation()

    with sqlite3.connect(database) as con:
        con.execute(
            "CREATE TRIGGER v2_revisions_no_update BEFORE UPDATE "
            "ON v2_judgement_revisions BEGIN SELECT RAISE(ABORT, 'altered revision guard'); END"
        )
        con.execute(
            "CREATE TRIGGER v2_commands_no_update BEFORE UPDATE "
            "ON v2_commands BEGIN SELECT RAISE(ABORT, 'altered command guard'); END"
        )
    with pytest.raises(ExpertStudyConfigurationError, match="table or trigger SQL"):
        store.load_session(capability)

    authority_root = tmp_path / "authority-row"
    authority_root.mkdir()
    authority_store = _v2_store(authority_root, monkeypatch)
    authority_capability, _ = authority_store.prepare_session(
        participant_code="V2-AUTHORITY-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    with sqlite3.connect(authority_root / "mechanics-pilot-v2.sqlite3") as con:
        con.execute("UPDATE v2_authority SET presentation_count=99 WHERE key=1")
    with pytest.raises(ExpertStudyConfigurationError, match="authority is incompatible"):
        authority_store.load_session(authority_capability)


def test_v2_recovery_replay_concurrency_and_immutable_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dedicated v2 contract: no v1 approval, opaque token and sealed SQLite history."""
    store = _v2_store(tmp_path, monkeypatch)
    capability, initial = store.prepare_session(
        participant_code="V2-EXPERT-01",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    token, comparison, _ordinal, _total = store.task(capability) or pytest.fail("missing v2 task")
    assert len(token) > 20 and str(initial.session_id) not in token
    # A pseudonym is an identifier, not a recovery secret. Re-entry cannot
    # rotate or take over the original browser capability.
    with pytest.raises(ExpertStudyConflictError, match="resume from the original browser"):
        store.prepare_session(
            participant_code="V2-EXPERT-01",
            years_experience=3,
            experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
            assessed_players_within_window=True,
            conflict_declared=False,
            conflict_note=None,
            consent_items=CONSENT,
        )
    snapshot = store.load_session(capability)
    assert snapshot.session_id == initial.session_id
    command = uuid5(NAMESPACE_URL, "v2-record")
    digest = hashlib.sha256(b"v2-server-computed-form-bytes").hexdigest()
    kwargs = dict(
        capability=capability,
        command_id=command,
        expected_revision=0,
        request_digest=digest,
        presentation_token=token,
        state=JudgementState.RATED,
        evidence_sufficiency=EvidenceSufficiencyV2.SUFFICIENT,
        assessment_basis=AssessmentBasisV2.SUPPLIED_EVIDENCE,
        relevance_rating=3,
        confidence=4,
        evidence_gap=None,
        citations=(
            next(
                family.label
                for family in comparison.exemplar.independent_descriptors
                if family.mandatory_for_selected_rubric
            ),
        ),
        explanation=None,
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        recorded = list(pool.map(lambda _: store.record(**kwargs), range(2)))
    saved = recorded[0]
    assert recorded[1].revision == saved.revision
    assert store.record(**kwargs).revision == saved.revision  # exact replay
    with pytest.raises(ExpertStudyConflictError, match="reused"):
        store.record(**(kwargs | {"request_digest": "f" * 64}))
    with pytest.raises(ExpertStudyConflictError, match="reused"):
        store.complete(
            capability=capability,
            command_id=command,
            expected_revision=saved.revision,
            request_digest=digest,
        )
    other_capability, other_snapshot = store.prepare_session(
        participant_code="V2-EXPERT-02",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_COACHING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    other_token, *_ = store.task(other_capability) or pytest.fail("missing second v2 task")
    with pytest.raises(ExpertStudyConflictError, match="reused"):
        store.record(
            **(
                kwargs
                | {
                    "capability": other_capability,
                    "expected_revision": other_snapshot.revision,
                    "presentation_token": other_token,
                }
            )
        )
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(
            pool.map(
                lambda _: store.complete(
                    capability=capability,
                    command_id=uuid5(NAMESPACE_URL, "v2-complete"),
                    expected_revision=saved.revision,
                    request_digest=hashlib.sha256(b"v2-complete").hexdigest(),
                ),
                range(2),
            )
        )
    assert outcomes[0].complete and outcomes[1].complete
    with sqlite3.connect(tmp_path / "mechanics-pilot-v2.sqlite3") as con:
        con.row_factory = sqlite3.Row
        receipt = con.execute(
            "SELECT receipt_json,receipt_digest FROM v2_completions WHERE session_id=?",
            (str(saved.session_id),),
        ).fetchone()
        assert receipt is not None
        session_id = str(saved.session_id)
        current_response_digests = [
            json.loads(row["judgement_json"])["judgement_digest"]
            for row in con.execute(
                "SELECT j.judgement_json FROM v2_judgements j "
                "JOIN v2_presentations p ON p.session_id=j.session_id "
                "AND p.presentation_id=j.presentation_id "
                "WHERE j.session_id=? ORDER BY p.ordinal",
                (session_id,),
            )
        ]
        assert json.loads(receipt["receipt_json"])["response_digests"] == current_response_digests
        assert (
            hashlib.sha256(receipt["receipt_json"].encode()).hexdigest()
            == receipt["receipt_digest"]
        )
        for invalid_complete in (2, -1, None):
            with pytest.raises(sqlite3.IntegrityError):
                con.execute(
                    "UPDATE v2_sessions SET complete=? WHERE session_id=?",
                    (invalid_complete, str(other_snapshot.session_id)),
                )
        with pytest.raises(sqlite3.IntegrityError, match="requires its exact receipt"):
            con.execute(
                "UPDATE v2_sessions SET complete=1 WHERE session_id=?",
                (str(other_snapshot.session_id),),
            )
        with pytest.raises(sqlite3.IntegrityError, match="schedule is sealed"):
            con.execute(
                "INSERT INTO v2_presentations VALUES(?,?,?,?,?)",
                (str(other_snapshot.session_id), 2, "extra-active", "x" * 32, "{}"),
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute("DELETE FROM v2_judgements")
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute("UPDATE v2_sessions SET complete=0 WHERE session_id=?", (session_id,))
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute("UPDATE v2_sessions SET revision=99 WHERE session_id=?", (session_id,))
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute("DELETE FROM v2_sessions WHERE session_id=?", (session_id,))
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute(
                "UPDATE v2_judgements SET judgement_json='{}' WHERE session_id=?", (session_id,)
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute(
                "INSERT INTO v2_judgement_revisions VALUES(?,?,?,?,?,?)",
                (session_id, "new-presentation", 1, "late-command", 3, "{}"),
            )
        with pytest.raises(sqlite3.IntegrityError, match="schedule"):
            con.execute("UPDATE v2_presentations SET ordinal=99 WHERE session_id=?", (session_id,))
        with pytest.raises(sqlite3.IntegrityError, match="schedule"):
            con.execute("DELETE FROM v2_presentations WHERE session_id=?", (session_id,))
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute(
                "INSERT INTO v2_presentations VALUES(?,?,?,?,?)",
                (session_id, 99, "new-presentation", "new-token", "{}"),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            con.execute("DELETE FROM v2_commands")
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            con.execute(
                "INSERT INTO v2_commands VALUES(?,?,?,?,?,?)",
                ("late-command", session_id, 3, "record", "f" * 64, "{}"),
            )
    assert store.load_session(capability).complete
    reopened = V2MechanicsPilotStore(
        database_path=tmp_path / "mechanics-pilot-v2.sqlite3",
        authority_path=tmp_path / "mechanics-pilot-authority-v1.json",
        allowed_root=tmp_path,
    )
    assert reopened.load_session(capability).complete
    # If a local corruptor removes the write-side trigger, the read-side receipt
    # reconstruction still rejects a canonical, semantically valid response change.
    with sqlite3.connect(tmp_path / "mechanics-pilot-v2.sqlite3") as con:
        judgement_text = con.execute(
            "SELECT judgement_json FROM v2_judgements WHERE session_id=?", (str(saved.session_id),)
        ).fetchone()[0]
        mutated = json.loads(judgement_text)
        mutated["confidence"] = 3
        mutated["judgement_digest"] = canonical_research_digest(
            {key: value for key, value in mutated.items() if key != "judgement_digest"}
        )
        con.execute("DROP TRIGGER v2_completed_no_judgement_update")
        con.execute("DROP TRIGGER v2_revisions_no_update")
        con.execute("DROP TRIGGER v2_commands_no_update")
        encoded_mutation = canonical_json_bytes(mutated).decode()
        con.execute(
            "UPDATE v2_judgements SET judgement_json=? WHERE session_id=?",
            (encoded_mutation, str(saved.session_id)),
        )
        con.execute(
            "UPDATE v2_judgement_revisions SET judgement_json=? WHERE session_id=?",
            (encoded_mutation, str(saved.session_id)),
        )
        con.execute(
            "UPDATE v2_commands SET response_json=? WHERE session_id=? AND command_kind='record'",
            (encoded_mutation, str(saved.session_id)),
        )
        con.execute(
            "CREATE TRIGGER v2_completed_no_judgement_update BEFORE UPDATE ON "
            "v2_judgements WHEN (SELECT complete FROM v2_sessions WHERE "
            "session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, "
            "'final v2 submission is immutable'); END"
        )
        con.execute(
            "CREATE TRIGGER v2_revisions_no_update BEFORE UPDATE ON "
            "v2_judgement_revisions BEGIN SELECT RAISE(ABORT, "
            "'v2 revisions are append-only'); END"
        )
        con.execute(
            "CREATE TRIGGER v2_commands_no_update BEFORE UPDATE ON v2_commands "
            "BEGIN SELECT RAISE(ABORT, 'v2 commands are append-only'); END"
        )
    with pytest.raises(ExpertStudyIntegrityError, match="completion receipt"):
        store.load_session(capability)

    # An active current response cannot be replaced by another canonical,
    # self-digested response without an exact linked correction event.
    active_root = tmp_path / "active-history"
    active_root.mkdir()
    active_store = _v2_store(active_root, monkeypatch)
    active_capability, active_initial = active_store.prepare_session(
        participant_code="V2-EXPERT-HISTORY",
        years_experience=3,
        experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
        assessed_players_within_window=True,
        conflict_declared=False,
        conflict_note=None,
        consent_items=CONSENT,
    )
    active_token, active_comparison, *_ = active_store.task(active_capability) or pytest.fail(
        "missing history test task"
    )
    active_saved = active_store.record(
        capability=active_capability,
        command_id=uuid5(NAMESPACE_URL, "v2-active-history-record"),
        expected_revision=active_initial.revision,
        request_digest=hashlib.sha256(b"v2-active-history-record").hexdigest(),
        presentation_token=active_token,
        state=JudgementState.RATED,
        evidence_sufficiency=EvidenceSufficiencyV2.SUFFICIENT,
        assessment_basis=AssessmentBasisV2.SUPPLIED_EVIDENCE,
        relevance_rating=3,
        confidence=4,
        evidence_gap=None,
        citations=(
            next(
                family.label
                for family in active_comparison.exemplar.independent_descriptors
                if family.mandatory_for_selected_rubric
            ),
        ),
        explanation=None,
    )
    active_database = active_root / "mechanics-pilot-v2.sqlite3"
    with sqlite3.connect(active_database) as con:
        original = con.execute(
            "SELECT judgement_json FROM v2_judgements WHERE session_id=?",
            (str(active_saved.session_id),),
        ).fetchone()[0]
        active_mutation = json.loads(original)
        active_mutation["confidence"] = 3
        active_mutation["judgement_digest"] = canonical_research_digest(
            {key: value for key, value in active_mutation.items() if key != "judgement_digest"}
        )
        con.execute(
            "UPDATE v2_judgements SET judgement_json=? WHERE session_id=?",
            (canonical_json_bytes(active_mutation).decode(), str(active_saved.session_id)),
        )
        retained_revision, retained_command = con.execute(
            "SELECT r.judgement_json,c.response_json "
            "FROM v2_judgement_revisions r JOIN v2_commands c "
            "ON c.command_id=r.command_id WHERE r.session_id=?",
            (str(active_saved.session_id),),
        ).fetchone()
        assert retained_revision == retained_command == original
    with pytest.raises(ExpertStudyIntegrityError, match="append-only history"):
        active_store.load_session(active_capability)
    with pytest.raises(ExpertStudyIntegrityError, match="append-only history"):
        active_store.review_tasks(active_capability)
    with pytest.raises(ExpertStudyIntegrityError, match="append-only history"):
        active_store.complete(
            capability=active_capability,
            command_id=uuid5(NAMESPACE_URL, "v2-active-history-complete"),
            expected_revision=active_saved.revision,
            request_digest=hashlib.sha256(b"v2-active-history-complete").hexdigest(),
        )
    # An old partial v2 database cannot be treated as a migration target.
    stale = tmp_path / "stale"
    stale.mkdir()
    (stale / "mechanics-pilot-authority-v1.json").write_bytes(
        (tmp_path / "mechanics-pilot-authority-v1.json").read_bytes()
    )
    sqlite3.connect(stale / "mechanics-pilot-v2.sqlite3").execute(
        "CREATE TABLE v2_sessions (x TEXT)"
    )
    with pytest.raises(ExpertStudyConfigurationError, match="predates"):
        _v2 = V2MechanicsPilotStore(
            database_path=stale / "mechanics-pilot-v2.sqlite3",
            authority_path=stale / "mechanics-pilot-authority-v1.json",
            allowed_root=stale,
        )
        _v2.prepare_session(
            participant_code="V2-EXPERT-02",
            years_experience=3,
            experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
            assessed_players_within_window=True,
            conflict_declared=False,
            conflict_note=None,
            consent_items=CONSENT,
        )
    for old_version in ("v1", "v2"):
        old_contract = tmp_path / f"old-contract-{old_version}"
        old_contract.mkdir()
        (old_contract / "mechanics-pilot-authority-v1.json").write_bytes(
            (tmp_path / "mechanics-pilot-authority-v1.json").read_bytes()
        )
        old_database = old_contract / "mechanics-pilot-v2.sqlite3"
        with sqlite3.connect(old_database) as con:
            con.execute(
                "CREATE TABLE v2_schema_contract "
                "(key INTEGER PRIMARY KEY CHECK(key=1), contract TEXT NOT NULL)"
            )
            con.execute(
                "INSERT INTO v2_schema_contract VALUES(1,?)",
                (f"w10-v2-mechanics-pilot-sqlite-contract-{old_version}",),
            )
        old_store = V2MechanicsPilotStore(
            database_path=old_database,
            authority_path=old_contract / "mechanics-pilot-authority-v1.json",
            allowed_root=old_contract,
        )
        with pytest.raises(ExpertStudyConfigurationError, match="schema contract is incompatible"):
            old_store.prepare_session(
                participant_code=f"V2-EXPERT-OLD-{old_version.upper()}",
                years_experience=3,
                experience_kinds=(ExpertExperienceKind.PROFESSIONAL_SCOUTING,),
                assessed_players_within_window=True,
                conflict_declared=False,
                conflict_note=None,
                consent_items=CONSENT,
            )
        with sqlite3.connect(old_database) as con:
            assert con.execute(
                "SELECT name FROM sqlite_master WHERE name LIKE 'v2_%' ORDER BY name"
            ).fetchall() == [("v2_schema_contract",)]


def test_v2_web_rejects_malformed_eligibility_without_500(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _v2_store(tmp_path, monkeypatch)
    client = TestClient(create_w10_v2_mechanics_pilot_app(store=store, allow_test_host=True))
    csrf = client.get("/w10/v2").cookies["w10_study_csrf"]
    response = client.post(
        "/w10/v2/sessions",
        data={
            "csrf": csrf,
            "participant_code": "V2-EXPERT-03",
            "years_experience": "not-a-number",
            "experience_professional_playing": "true",
            "assessed_players_within_window": "true",
            **{name: "true" for name in CONSENT},
        },
    )
    assert response.status_code == 422
    assert "years of experience must be a whole number" in response.text
    assert "Start a pseudonymous v2 pilot session" in response.text


def test_v2_duplicate_pseudonym_is_a_bounded_conflict_and_original_cookie_resumes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _v2_store(tmp_path, monkeypatch)
    app = create_w10_v2_mechanics_pilot_app(store=store, allow_test_host=True)
    original = TestClient(app)
    duplicate = TestClient(app)

    def entry(client: TestClient) -> dict[str, str]:
        csrf = client.get("/w10/v2").cookies["w10_study_csrf"]
        return {
            "csrf": csrf,
            "participant_code": "V2-DUPLICATE-01",
            "years_experience": "3",
            "experience_professional_scouting": "true",
            "assessed_players_within_window": "true",
            **{name: "true" for name in CONSENT},
        }

    started = original.post("/w10/v2/sessions", data=entry(original), follow_redirects=False)
    assert started.status_code == 303
    resumed = original.get("/w10/v2")
    assert resumed.status_code == 200
    assert "Historical role/style comparison 1 of 1" in resumed.text

    conflict = duplicate.post("/w10/v2/sessions", data=entry(duplicate))
    assert conflict.status_code == 409
    assert "resume from the original browser" in conflict.text
    assert "w10_v2_pilot_capability" not in duplicate.cookies

    resumed_again = original.get("/w10/v2")
    assert resumed_again.status_code == 200
    assert "Historical role/style comparison 1 of 1" in resumed_again.text

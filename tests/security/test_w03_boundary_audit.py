"""Independent executable audit of the completed W03 high-risk boundaries."""

from __future__ import annotations

import hashlib
import json
import runpy
import secrets
from collections.abc import Iterator
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import yaml  # type: ignore[import-untyped]
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DBAPIError

from scouting.audit import AuditWriter
from scouting.contracts import (
    ConstraintOperator,
    DependencyKind,
    DependencyLineage,
    EvidenceDependency,
    RetrievalRequest,
    RetrievalResult,
    RoleBrief,
    RoleBriefStatus,
    RoleConstraint,
    TemporalEvidence,
    TenantContext,
)
from scouting.operations import LocalTelemetry
from scouting.policy import (
    AuthorizationPolicy,
    AuthorizationRequest,
    ResourceContext,
    SessionAuthenticator,
    SyntheticAccount,
    SyntheticPrincipal,
    SyntheticRightsPolicy,
)
from scouting.serving import (
    SyntheticArtifactCatalog,
    SyntheticDomainSnapshot,
    SyntheticServingService,
)
from scouting.serving.synthetic import SyntheticFact
from scouting.storage import (
    GuardedStorage,
    InvalidArtifactPathError,
    PathEscapeError,
)
from scouting.storage.embedded import (
    EMBEDDED_DATABASE_USER,
    EmbeddedDatabaseConfigurationError,
    create_embedded_engine,
    resolve_database_path,
)
from scouting.web import W03WebSettings, create_app
from scouting.workflow import ApplicationDatabase, WorkflowService

ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT_FIXTURE_ROOT = ROOT / "tests/fixtures/synthetic"
DOMAIN_PATH = DEVELOPMENT_FIXTURE_ROOT / "domain.json"
AUTHORIZATION_PATH = ROOT / "configs/policies/authorization.yaml"
RIGHTS_PATH = ROOT / "configs/policies/data-rights.yaml"
LOCAL_REVIEW_PATH = ROOT / "configs/environments/w03-local-review.yaml"

TENANT_ID = UUID("70000000-0000-4000-8000-000000000101")
ACTOR_ID = UUID("60000000-0000-4000-8000-000000000101")
OTHER_ACTOR_ID = UUID("60000000-0000-4000-8000-000000000199")
SELECTED_PLAYER_ID = UUID("30000000-0000-4000-8000-000000000101")
AMBIGUOUS_PLAYER_IDS = frozenset(
    {
        UUID("30000000-0000-4000-8000-000000000105"),
        UUID("30000000-0000-4000-8000-000000000106"),
    }
)
CUTOFF = datetime(2026, 3, 1, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class AppHarness:
    client: TestClient
    database: ApplicationDatabase
    workflow: WorkflowService
    telemetry: LocalTelemetry
    token: str
    other_analyst_token: str
    snapshot: SyntheticDomainSnapshot
    artifacts: SyntheticArtifactCatalog


@pytest.fixture(scope="module")
def database_engine(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Engine]:
    database_root = tmp_path_factory.mktemp("w03-boundary")
    engine = create_embedded_engine(
        database_root / "boundary.sqlite3",
        allowed_root=database_root,
    )
    _seed_journey_prerequisites(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="module")
def rights_policy() -> SyntheticRightsPolicy:
    return SyntheticRightsPolicy.from_path(RIGHTS_PATH)


@pytest.fixture(scope="module")
def domain_snapshot(
    rights_policy: SyntheticRightsPolicy,
) -> SyntheticDomainSnapshot:
    return SyntheticDomainSnapshot.from_path(
        DOMAIN_PATH.name,
        allowed_fixture_root=DEVELOPMENT_FIXTURE_ROOT,
        expected_partition="development",
        rights_policy=rights_policy,
    )


@pytest.fixture(scope="module")
def app_harness(
    database_engine: Engine,
    domain_snapshot: SyntheticDomainSnapshot,
) -> Iterator[AppHarness]:
    artifacts = SyntheticArtifactCatalog.development()
    authorization = AuthorizationPolicy.from_path(
        AUTHORIZATION_PATH,
        known_actor_ids=(ACTOR_ID, OTHER_ACTOR_ID),
    )
    database = ApplicationDatabase(database_engine, tenant_id=TENANT_ID)
    workflow = WorkflowService(
        database=database,
        authorization=authorization,
        serving=SyntheticServingService(domain_snapshot, artifacts=artifacts),
        audit_writer=AuditWriter(),
    )
    token = secrets.token_urlsafe(32)
    other_analyst_token = secrets.token_urlsafe(32)
    telemetry = LocalTelemetry()
    app = create_app(
        authenticator=SessionAuthenticator(
            {
                token: SyntheticAccount(ACTOR_ID, TENANT_ID, ("analyst",)),
                other_analyst_token: SyntheticAccount(
                    OTHER_ACTOR_ID,
                    TENANT_ID,
                    ("analyst",),
                ),
            }
        ),
        workflow=workflow,
        telemetry=telemetry,
        settings=W03WebSettings(
            tenant_id=TENANT_ID,
            authorization_policy_id=authorization.policy_id,
            data_rights_policy_id="w03-synthetic-data-rights-v1",
            source_manifest_id=artifacts.source_manifest_id,
            source_manifest_digest=domain_snapshot.manifest_digest,
            template_path=ROOT / "apps/web/templates/w03_journey.html",
        ),
    )
    with TestClient(app) as client:
        yield AppHarness(
            client=client,
            database=database,
            workflow=workflow,
            telemetry=telemetry,
            token=token,
            other_analyst_token=other_analyst_token,
            snapshot=domain_snapshot,
            artifacts=artifacts,
        )


def test_strict_contracts_and_cutoff_equality_fail_closed(
    rights_policy: SyntheticRightsPolicy,
) -> None:
    brief, _ = _review_contracts()
    unknown_field = brief.model_dump(mode="json")
    unknown_field["unreviewed_field"] = "must fail"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        RoleBrief.model_validate_json(json.dumps(unknown_field))

    non_utc = brief.model_dump(mode="json")
    non_utc["created_at"] = "2026-02-28T23:00:00+01:00"
    with pytest.raises(ValidationError, match="expressed in UTC"):
        RoleBrief.model_validate_json(json.dumps(non_utc))

    availability_equal = rights_policy.decide_fact(
        classification=rights_policy.classification,
        observed_at=CUTOFF - timedelta(hours=2),
        available_at=CUTOFF,
        cutoff=CUTOFF,
        generated=True,
        identity_unambiguous=True,
    )
    assert availability_equal.admitted is False
    assert availability_equal.reason_code == "post_cutoff_availability"

    observation_equal = rights_policy.decide_fact(
        classification=rights_policy.classification,
        observed_at=CUTOFF,
        available_at=CUTOFF - timedelta(hours=1),
        cutoff=CUTOFF,
        generated=True,
        identity_unambiguous=True,
    )
    assert observation_equal.admitted is False
    assert observation_equal.reason_code == "post_cutoff_observation"

    dependency_id = uuid4()
    dependency = EvidenceDependency(
        kind=DependencyKind.SOURCE_MANIFEST,
        dependency_id=dependency_id,
        digest="a" * 64,
        observed_at=CUTOFF - timedelta(hours=2),
        available_at=CUTOFF,
    )
    lineage = DependencyLineage(
        lineage_hash="b" * 64,
        dependencies=(dependency,),
    )
    with pytest.raises(ValidationError, match="available_at must be before"):
        TemporalEvidence(
            snapshot_as_of_ts=CUTOFF - timedelta(seconds=1),
            available_at_watermark=CUTOFF,
            valid_from_ts=CUTOFF,
            generated_at_ts=CUTOFF + timedelta(seconds=1),
            feature_cutoff_ts=CUTOFF,
            source_manifest_ids=(dependency_id,),
            feature_schema_hash="c" * 64,
            dependency_lineage_hash=lineage.lineage_hash,
            dependency_lineage=lineage,
        )


def test_runtime_lineage_is_canonical_and_tampering_is_rejected(
    domain_snapshot: SyntheticDomainSnapshot,
) -> None:
    artifacts = SyntheticArtifactCatalog.development()
    brief, request = _review_contracts()
    outcome = SyntheticServingService(domain_snapshot, artifacts=artifacts).retrieve(
        brief,
        request,
    )

    assert outcome.status == "available"
    assert outcome.result is not None
    result = outcome.result
    lineage = result.temporal_evidence.dependency_lineage
    expected_hash = hashlib.sha256(
        json.dumps(
            {
                "dependencies": [
                    dependency.model_dump(mode="json") for dependency in lineage.dependencies
                ]
            },
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    assert lineage.lineage_hash == expected_hash
    assert result.temporal_evidence.dependency_lineage_hash == expected_hash
    assert result.temporal_evidence.source_manifest_ids == (artifacts.source_manifest_id,)
    source_dependency = next(
        dependency
        for dependency in lineage.dependencies
        if dependency.kind is DependencyKind.SOURCE_MANIFEST
    )
    assert source_dependency.digest == domain_snapshot.manifest_digest
    assert {dependency.kind for dependency in lineage.dependencies} == {
        DependencyKind.SOURCE_MANIFEST,
        DependencyKind.FEATURE_SCHEMA,
        DependencyKind.MODEL_ARTIFACT,
        DependencyKind.RETRIEVAL_INDEX,
    }
    assert all(candidate.lineage == lineage for candidate in result.candidates)

    tampered = result.model_dump(mode="json")
    tampered["temporal_evidence"]["dependency_lineage_hash"] = "f" * 64
    with pytest.raises(ValidationError, match="dependency_lineage_hash must match"):
        RetrievalResult.model_validate_json(json.dumps(tampered))

    candidate_tamper = result.model_dump(mode="json")
    candidate_tamper["candidates"][0]["lineage"]["lineage_hash"] = "e" * 64
    with pytest.raises(ValidationError, match="candidate lineage must exactly match"):
        RetrievalResult.model_validate_json(json.dumps(candidate_tamper))


def test_ambiguous_identity_is_ineligible_even_with_strong_pre_cutoff_fact(
    domain_snapshot: SyntheticDomainSnapshot,
    rights_policy: SyntheticRightsPolicy,
) -> None:
    ambiguous_player_id = min(AMBIGUOUS_PLAYER_IDS, key=str)
    decision = rights_policy.decide_fact(
        classification=rights_policy.classification,
        observed_at=CUTOFF - timedelta(days=2),
        available_at=CUTOFF - timedelta(days=1),
        cutoff=CUTOFF,
        generated=True,
        identity_unambiguous=False,
    )
    assert decision.admitted is False
    assert decision.reason_code == "identity_review_required"

    synthetic_snapshot = replace(
        domain_snapshot,
        admitted_facts=(
            SyntheticFact(
                fact_id=uuid4(),
                player_id=ambiguous_player_id,
                metric="wide_overlaps_per_90",
                value=999.0,
                observed_at=CUTOFF - timedelta(days=2),
                available_at=CUTOFF - timedelta(days=1),
            ),
        ),
        rejected_facts=(),
    )
    brief, request = _review_contracts(position="full_back")
    outcome = SyntheticServingService(
        synthetic_snapshot,
        artifacts=SyntheticArtifactCatalog.development(),
    ).retrieve(brief, request)

    assert outcome.status == "available"
    assert outcome.result is not None
    assert outcome.result.candidates == ()
    assert outcome.explanations == ()
    assert ambiguous_player_id not in {
        candidate.player_id for candidate in outcome.result.candidates
    }


def test_guarded_storage_rejects_traversal_and_escaped_symlink_before_io(
    tmp_path: Path,
) -> None:
    root = tmp_path / "guarded"
    outside = tmp_path / "outside"
    outside.mkdir()
    storage = GuardedStorage({"audit": root})
    write_options = {
        "media_type": "application/octet-stream",
        "lineage": {"review": "W03.2"},
        "retention": {"class": "review-temporary"},
    }

    with pytest.raises(InvalidArtifactPathError, match="normal relative path"):
        storage.write_bytes(
            "audit",
            "../outside/traversal.bin",
            b"must-not-escape",
            **write_options,
        )
    assert not (outside / "traversal.bin").exists()

    (root / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(PathEscapeError, match="not a real directory"):
        storage.write_bytes(
            "audit",
            "linked/symlink.bin",
            b"must-not-follow",
            **write_options,
        )
    assert not (outside / "symlink.bin").exists()


def test_single_tenant_boundary_and_audit_immutability_hold_in_embedded_runtime(
    database_engine: Engine,
) -> None:
    audit_event_id = uuid4()
    database = ApplicationDatabase(database_engine, tenant_id=TENANT_ID)
    with database.transaction(TENANT_ID) as (_, identity):
        assert identity.current_user == EMBEDDED_DATABASE_USER
    with pytest.raises(PermissionError, match="action denied"):
        with database.transaction(uuid4()):
            pass

    with database_engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO audit_events (
                    audit_event_id, tenant_id, trace_id, request_id, actor_id,
                    action, target_type, target_id, occurred_at, after_digest
                )
                VALUES (
                    :event_id, :tenant_id, :trace_id, :request_id, :actor_id,
                    'create', 'boundary.review', :target_id, :occurred_at, :after_digest
                )
                """
            ),
            {
                "event_id": audit_event_id,
                "tenant_id": TENANT_ID,
                "trace_id": uuid4(),
                "request_id": uuid4(),
                "actor_id": uuid4(),
                "target_id": SELECTED_PLAYER_ID,
                "occurred_at": "2026-07-29T00:00:00+00:00",
                "after_digest": "d" * 64,
            },
        )

    for statement in (
        "UPDATE audit_events SET reason = 'tamper' WHERE audit_event_id = :event_id",
        "DELETE FROM audit_events WHERE audit_event_id = :event_id",
    ):
        with pytest.raises(DBAPIError, match="append-only"):
            with database_engine.begin() as connection:
                connection.execute(text(statement), {"event_id": audit_event_id})

    with database_engine.connect() as connection:
        assert (
            connection.execute(
                text("SELECT count(*) FROM audit_events WHERE audit_event_id = :event_id"),
                {"event_id": audit_event_id},
            ).scalar_one()
            == 1
        )


def test_app_policy_denies_unknown_context_and_minimises_confidential_response(
    app_harness: AppHarness,
) -> None:
    policy = AuthorizationPolicy.from_path(
        AUTHORIZATION_PATH,
        known_actor_ids=(ACTOR_ID,),
    )
    principal = SyntheticPrincipal(ACTOR_ID, TENANT_ID, ("analyst",))
    resource = ResourceContext(
        resource_type="retrieval",
        resource_id=uuid4(),
        tenant_id=TENANT_ID,
        owner_actor_id=ACTOR_ID,
        visibility="OWNER_ONLY",
    )
    unknown_action = policy.authorize(
        AuthorizationRequest(
            principal=principal,
            action="unregistered.material.action",
            resource=resource,
            request_id=uuid4(),
        )
    )
    assert not unknown_action.allowed
    assert unknown_action.reason_code == "unknown_or_ungranted_action"

    cross_tenant = policy.authorize(
        AuthorizationRequest(
            principal=principal,
            action="retrieval.create",
            resource=replace(resource, tenant_id=uuid4()),
            request_id=uuid4(),
        )
    )
    assert not cross_tenant.allowed
    assert cross_tenant.reason_code == "cross_tenant"

    unauthenticated = app_harness.client.get("/w03")
    assert unauthenticated.status_code == 401
    assert unauthenticated.json() == {"detail": "session authentication failed"}

    evidence_id = uuid4()
    request_id = uuid4()
    response = app_harness.client.post(
        "/api/w03/confidential-evidence/read",
        headers={
            "Authorization": f"Bearer {app_harness.token}",
            "x-request-id": str(request_id),
        },
        json={"evidence_id": str(evidence_id)},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "action denied"}
    assert str(evidence_id) not in response.text
    assert "confidential" not in response.text
    assert "classification" not in response.text

    with app_harness.database.transaction(TENANT_ID) as (connection, identity):
        assert identity.current_user == EMBEDDED_DATABASE_USER
        row = connection.execute(
            text(
                """
                SELECT action, target_type, target_id, before_digest, after_digest,
                       reason, export_scope
                FROM audit_events
                WHERE request_id = :request_id
                """
            ),
            {"request_id": request_id},
        ).one()
    assert row.action == "read"
    assert row.target_type == "confidential_evidence.denied_attempt"
    assert row.target_id == str(evidence_id)
    assert row.before_digest is None
    assert row.after_digest is None
    assert row.reason == "authorization_denied"
    assert json.loads(row.export_scope) == []


def test_same_tenant_existing_brief_owner_collision_is_denied(
    app_harness: AppHarness,
) -> None:
    _assert_same_tenant_material_owner_collision_is_denied(
        app_harness,
        collision_target="role_brief",
    )


@pytest.mark.parametrize("collision_target", ("shortlist", "shortlist_entry"))
def test_same_tenant_late_material_owner_collisions_have_zero_effects(
    app_harness: AppHarness,
    collision_target: str,
) -> None:
    _assert_same_tenant_material_owner_collision_is_denied(
        app_harness,
        collision_target=collision_target,
    )


def _assert_same_tenant_material_owner_collision_is_denied(
    app_harness: AppHarness,
    *,
    collision_target: str,
) -> None:
    victim_brief, victim_request = _review_contracts()
    victim_shortlist_id = uuid4()
    victim_entry_id = uuid4()
    victim = app_harness.client.post(
        "/api/w03/journey",
        headers={"Authorization": f"Bearer {app_harness.token}"},
        json=_journey_payload(
            brief=victim_brief,
            request=victim_request,
            shortlist_id=victim_shortlist_id,
            shortlist_entry_id=victim_entry_id,
            rationale="Victim-owned synthetic review object",
        ),
    )
    assert victim.status_code == 200, victim.text
    victim_before = _victim_material_snapshot(
        app_harness.database,
        role_brief_id=victim_brief.role_brief_id,
        role_brief_version=victim_brief.version,
        shortlist_id=victim_shortlist_id,
        shortlist_entry_id=victim_entry_id,
    )

    attacker_brief, attacker_request = _review_contracts(
        actor_id=OTHER_ACTOR_ID,
        role_brief_id=(victim_brief.role_brief_id if collision_target == "role_brief" else None),
    )
    attacker_shortlist_id = victim_shortlist_id if collision_target == "shortlist" else uuid4()
    attacker_entry_id = victim_entry_id if collision_target == "shortlist_entry" else uuid4()
    collision_request_id = uuid4()
    effects_before = _attempt_effects(
        app_harness.database,
        actor_id=OTHER_ACTOR_ID,
        role_brief_id=attacker_brief.role_brief_id,
        retrieval_request_id=attacker_request.retrieval_request_id,
        shortlist_id=attacker_shortlist_id,
        shortlist_entry_id=attacker_entry_id,
        request_id=collision_request_id,
    )
    assert effects_before == (0, 0, 0, 0, 0, 0)

    collision = app_harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {app_harness.other_analyst_token}",
            "x-request-id": str(collision_request_id),
        },
        json=_journey_payload(
            brief=attacker_brief,
            request=attacker_request,
            shortlist_id=attacker_shortlist_id,
            shortlist_entry_id=attacker_entry_id,
            rationale=f"Must not reuse another analyst's {collision_target}",
        ),
    )

    assert collision.status_code == 403
    assert collision.json() == {"detail": "action denied"}
    assert _attempt_effects(
        app_harness.database,
        actor_id=OTHER_ACTOR_ID,
        role_brief_id=attacker_brief.role_brief_id,
        retrieval_request_id=attacker_request.retrieval_request_id,
        shortlist_id=attacker_shortlist_id,
        shortlist_entry_id=attacker_entry_id,
        request_id=collision_request_id,
    ) == (0, 0, 0, 0, 0, 0)
    assert (
        _victim_material_snapshot(
            app_harness.database,
            role_brief_id=victim_brief.role_brief_id,
            role_brief_version=victim_brief.version,
            shortlist_id=victim_shortlist_id,
            shortlist_entry_id=victim_entry_id,
        )
        == victim_before
    )


@pytest.mark.parametrize(
    "mismatch_target",
    ("role_brief", "retrieval", "shortlist", "shortlist_entry"),
)
def test_same_owner_immutable_mismatches_are_denied_and_rolled_back(
    app_harness: AppHarness,
    mismatch_target: str,
) -> None:
    victim_brief, victim_request = _review_contracts()
    victim_shortlist_id = uuid4()
    victim_entry_id = uuid4()
    victim_rationale = "Canonical same-owner immutable review object"
    victim = app_harness.client.post(
        "/api/w03/journey",
        headers={"Authorization": f"Bearer {app_harness.token}"},
        json=_journey_payload(
            brief=victim_brief,
            request=victim_request,
            shortlist_id=victim_shortlist_id,
            shortlist_entry_id=victim_entry_id,
            rationale=victim_rationale,
        ),
    )
    assert victim.status_code == 200, victim.text
    victim_before = _victim_material_snapshot(
        app_harness.database,
        role_brief_id=victim_brief.role_brief_id,
        role_brief_version=victim_brief.version,
        shortlist_id=victim_shortlist_id,
        shortlist_entry_id=victim_entry_id,
    )

    attempted_brief = victim_brief
    attempted_request = victim_request
    attempted_shortlist_id = victim_shortlist_id
    attempted_entry_id = victim_entry_id
    attempted_rationale = victim_rationale
    if mismatch_target == "role_brief":
        attempted_brief = victim_brief.model_copy(
            update={"title": "Changed title under the same canonical brief ID"}
        )
    elif mismatch_target == "retrieval":
        attempted_brief, attempted_request = _review_contracts()
        attempted_request = attempted_request.model_copy(
            update={
                "retrieval_request_id": victim_request.retrieval_request_id,
            }
        )
        attempted_shortlist_id = uuid4()
        attempted_entry_id = uuid4()
    elif mismatch_target == "shortlist":
        attempted_brief, attempted_request = _review_contracts()
        attempted_entry_id = uuid4()
    else:
        attempted_rationale = "Changed rationale under the same canonical entry ID"

    attempt_request_id = uuid4()
    effects_before = _attempt_effects(
        app_harness.database,
        actor_id=ACTOR_ID,
        role_brief_id=attempted_brief.role_brief_id,
        retrieval_request_id=attempted_request.retrieval_request_id,
        shortlist_id=attempted_shortlist_id,
        shortlist_entry_id=attempted_entry_id,
        request_id=attempt_request_id,
    )
    denied = app_harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {app_harness.token}",
            "x-request-id": str(attempt_request_id),
        },
        json=_journey_payload(
            brief=attempted_brief,
            request=attempted_request,
            shortlist_id=attempted_shortlist_id,
            shortlist_entry_id=attempted_entry_id,
            rationale=attempted_rationale,
        ),
    )

    assert denied.status_code == 403
    assert denied.json() == {"detail": "action denied"}
    assert (
        _attempt_effects(
            app_harness.database,
            actor_id=ACTOR_ID,
            role_brief_id=attempted_brief.role_brief_id,
            retrieval_request_id=attempted_request.retrieval_request_id,
            shortlist_id=attempted_shortlist_id,
            shortlist_entry_id=attempted_entry_id,
            request_id=attempt_request_id,
        )
        == effects_before
    )
    assert effects_before[-1] == 0
    assert (
        _victim_material_snapshot(
            app_harness.database,
            role_brief_id=victim_brief.role_brief_id,
            role_brief_version=victim_brief.version,
            shortlist_id=victim_shortlist_id,
            shortlist_entry_id=victim_entry_id,
        )
        == victim_before
    )


def test_exact_same_owner_canonical_replay_is_idempotent(
    app_harness: AppHarness,
) -> None:
    brief, request = _review_contracts()
    shortlist_id = uuid4()
    shortlist_entry_id = uuid4()
    payload = _journey_payload(
        brief=brief,
        request=request,
        shortlist_id=shortlist_id,
        shortlist_entry_id=shortlist_entry_id,
        rationale="Independent exact canonical replay evidence",
    )
    first_request_id = uuid4()
    replay_request_id = uuid4()

    first = app_harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {app_harness.token}",
            "x-request-id": str(first_request_id),
        },
        json=payload,
    )
    replay = app_harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {app_harness.token}",
            "x-request-id": str(replay_request_id),
        },
        json=payload,
    )

    assert first.status_code == 200, first.text
    assert replay.status_code == 200, replay.text
    assert replay.json()["result"] == first.json()["result"]
    assert replay.json()["shortlist_entry"] == first.json()["shortlist_entry"]
    first_effects = _attempt_effects(
        app_harness.database,
        actor_id=ACTOR_ID,
        role_brief_id=brief.role_brief_id,
        retrieval_request_id=request.retrieval_request_id,
        shortlist_id=shortlist_id,
        shortlist_entry_id=shortlist_entry_id,
        request_id=first_request_id,
    )
    replay_effects = _attempt_effects(
        app_harness.database,
        actor_id=ACTOR_ID,
        role_brief_id=brief.role_brief_id,
        retrieval_request_id=request.retrieval_request_id,
        shortlist_id=shortlist_id,
        shortlist_entry_id=shortlist_entry_id,
        request_id=replay_request_id,
    )
    assert first_effects == (1, 1, 1, 1, 1, 4)
    assert replay_effects == (1, 1, 1, 1, 1, 4)


def test_full_app_journey_binds_contracts_lineage_and_append_only_audit(
    app_harness: AppHarness,
) -> None:
    brief, retrieval_request = _review_contracts()
    request_id = uuid4()
    response = app_harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {app_harness.token}",
            "x-request-id": str(request_id),
        },
        json={
            "role_brief": brief.model_dump(mode="json"),
            "retrieval_request": retrieval_request.model_dump(mode="json"),
            "shortlist_id": str(uuid4()),
            "shortlist_entry_id": str(uuid4()),
            "rationale": "Independent W03 boundary-review shortlist evidence",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    result = RetrievalResult.model_validate_json(json.dumps(body["result"]))
    assert result.retrieval_request_id == retrieval_request.retrieval_request_id
    assert result.role_brief_id == brief.role_brief_id
    assert result.role_brief_version == brief.version
    assert result.temporal_evidence.feature_cutoff_ts == CUTOFF
    assert body["data_manifest_digest"] == app_harness.snapshot.manifest_digest
    assert body["lineage_hash"] == result.temporal_evidence.dependency_lineage_hash
    assert body["model_quality_claim"] is False
    assert body["claim_boundary"] == "resemblance_only"
    assert [candidate.player_id for candidate in result.candidates] == [SELECTED_PLAYER_ID]
    assert not AMBIGUOUS_PLAYER_IDS.intersection(
        candidate.player_id for candidate in result.candidates
    )
    assert {item["reason_code"] for item in body["rejected_evidence"]} == {
        "post_cutoff_availability",
        "missing_temporal_evidence",
    }
    assert body["database_context"] == {
        "current_user": EMBEDDED_DATABASE_USER,
        "tenant_id": str(TENANT_ID),
        "transaction_local": True,
    }

    with app_harness.database.transaction(TENANT_ID) as (connection, _):
        actions = list(
            connection.execute(
                text(
                    """
                    SELECT target_type
                    FROM audit_events
                    WHERE request_id = :request_id
                    ORDER BY occurred_at, target_type
                    """
                ),
                {"request_id": request_id},
            ).scalars()
        )
    assert actions == [
        "role_brief.approved",
        "retrieval.executed",
        "evidence.viewed",
        "shortlist.entry_created",
    ]


def test_missing_model_fails_closed_without_silent_substitution(
    domain_snapshot: SyntheticDomainSnapshot,
) -> None:
    artifacts = replace(
        SyntheticArtifactCatalog.development(),
        model_artifact_id=None,
        model_artifact_digest=None,
        model_version=None,
    )
    brief, request = _review_contracts()
    outcome = SyntheticServingService(
        domain_snapshot,
        artifacts=artifacts,
    ).retrieve(brief, request)

    assert outcome.status == "unavailable"
    assert outcome.result is None
    assert outcome.explanations == ()
    assert outcome.missing_evidence == ("model_artifact",)


def test_local_runtime_and_telemetry_have_no_public_or_confidential_export(
    app_harness: AppHarness,
) -> None:
    health = app_harness.client.get("/health")
    assert health.status_code == 200
    assert health.json()["exposure"] == "loopback_only"
    readiness = app_harness.client.get("/ready")
    assert readiness.status_code == 200
    assert readiness.json()["database_user"] == EMBEDDED_DATABASE_USER
    assert readiness.json()["telemetry_export"] == "disabled"

    worker_run_once = runpy.run_path(str(ROOT / "services/worker/main.py"))["run_once"]
    worker = worker_run_once(
        workflow=app_harness.workflow,
        tenant_id=TENANT_ID,
        telemetry=app_harness.telemetry,
    )
    assert worker.status == "ready"
    assert worker.database_user == EMBEDDED_DATABASE_USER
    assert worker.listener_started is False

    marker = "review-confidential-marker"
    app_harness.telemetry.log(
        "review_redaction_probe",
        actor_id=ACTOR_ID,
        path="/review",
        confidential_payload=marker,
        authorization=app_harness.token,
    )
    serialized = app_harness.telemetry.serialized_snapshot()
    assert marker not in serialized
    assert app_harness.token not in serialized

    with pytest.raises(EmbeddedDatabaseConfigurationError, match="guarded root"):
        resolve_database_path(
            ROOT.parent / "escaped.sqlite3",
            allowed_root=ROOT,
        )

    local_review = yaml.safe_load(LOCAL_REVIEW_PATH.read_text(encoding="utf-8"))
    assert local_review["network"]["bind_scope"] == "loopback_only"
    assert local_review["network"]["public_bind_allowed"] is False
    assert local_review["telemetry"]["hosted_telemetry_allowed"] is False
    assert local_review["telemetry"]["external_telemetry_export_allowed"] is False

    assert local_review["runtime"]["containers_allowed"] is False
    assert local_review["services"]["embedded_sqlite"]["required"] is True
    assert not (ROOT / "compose.yaml").exists()


def _journey_payload(
    *,
    brief: RoleBrief,
    request: RetrievalRequest,
    shortlist_id: UUID,
    shortlist_entry_id: UUID,
    rationale: str,
) -> dict[str, object]:
    return {
        "role_brief": brief.model_dump(mode="json"),
        "retrieval_request": request.model_dump(mode="json"),
        "shortlist_id": str(shortlist_id),
        "shortlist_entry_id": str(shortlist_entry_id),
        "rationale": rationale,
    }


def _attempt_effects(
    database: ApplicationDatabase,
    *,
    actor_id: UUID,
    role_brief_id: UUID,
    retrieval_request_id: UUID,
    shortlist_id: UUID,
    shortlist_entry_id: UUID,
    request_id: UUID,
) -> tuple[int, int, int, int, int, int]:
    with database.transaction(TENANT_ID) as (connection, _):
        row = connection.execute(
            text(
                """
                SELECT
                    (
                        SELECT count(*)
                        FROM role_briefs
                        WHERE role_brief_id = :role_brief_id
                          AND owner_id = :actor_id
                    ),
                    (
                        SELECT count(*)
                        FROM retrieval_runs
                        WHERE retrieval_request_id = :retrieval_request_id
                    ),
                    (
                        SELECT count(*)
                        FROM candidate_results AS candidate
                        JOIN retrieval_runs AS retrieval
                          ON retrieval.tenant_id = candidate.tenant_id
                         AND retrieval.retrieval_run_id = candidate.retrieval_run_id
                        WHERE retrieval.retrieval_request_id = :retrieval_request_id
                    ),
                    (
                        SELECT count(*)
                        FROM shortlists
                        WHERE shortlist_id = :shortlist_id
                          AND owner_id = :actor_id
                    ),
                    (
                        SELECT count(*)
                        FROM shortlist_entries
                        WHERE shortlist_entry_id = :shortlist_entry_id
                          AND owner_id = :actor_id
                    ),
                    (
                        SELECT count(*)
                        FROM audit_events
                        WHERE request_id = :request_id
                    )
                """
            ),
            {
                "actor_id": actor_id,
                "role_brief_id": role_brief_id,
                "retrieval_request_id": retrieval_request_id,
                "shortlist_id": shortlist_id,
                "shortlist_entry_id": shortlist_entry_id,
                "request_id": request_id,
            },
        ).one()
    return tuple(row)


def _victim_material_snapshot(
    database: ApplicationDatabase,
    *,
    role_brief_id: UUID,
    role_brief_version: int,
    shortlist_id: UUID,
    shortlist_entry_id: UUID,
) -> tuple[object, object, object]:
    with database.transaction(TENANT_ID) as (connection, _):
        return _material_snapshot(
            connection,
            role_brief_id=role_brief_id,
            role_brief_version=role_brief_version,
            shortlist_id=shortlist_id,
            shortlist_entry_id=shortlist_entry_id,
        )


def _material_snapshot(
    connection: Connection,
    *,
    role_brief_id: UUID,
    role_brief_version: int,
    shortlist_id: UUID,
    shortlist_entry_id: UUID,
) -> tuple[object, object, object]:
    parameters = {
        "role_brief_id": role_brief_id,
        "role_brief_version": role_brief_version,
        "shortlist_id": shortlist_id,
        "shortlist_entry_id": shortlist_entry_id,
    }
    brief = (
        connection.execute(
            text(
                """
            SELECT *
            FROM role_briefs
            WHERE role_brief_id = :role_brief_id
              AND version = :role_brief_version
            """
            ),
            parameters,
        )
        .mappings()
        .one()
    )
    shortlist = (
        connection.execute(
            text("SELECT * FROM shortlists WHERE shortlist_id = :shortlist_id"),
            parameters,
        )
        .mappings()
        .one()
    )
    entry = (
        connection.execute(
            text("SELECT * FROM shortlist_entries WHERE shortlist_entry_id = :shortlist_entry_id"),
            parameters,
        )
        .mappings()
        .one()
    )
    return (
        tuple(sorted(brief.items())),
        tuple(sorted(shortlist.items())),
        tuple(sorted(entry.items())),
    )


def _review_contracts(
    *,
    position: str = "wide_forward",
    actor_id: UUID = ACTOR_ID,
    role_brief_id: UUID | None = None,
) -> tuple[RoleBrief, RetrievalRequest]:
    brief_id = role_brief_id or uuid4()
    trace_id = uuid4()
    brief = RoleBrief(
        role_brief_id=brief_id,
        tenant_context=TenantContext(tenant_id=TENANT_ID),
        version=1,
        trace_id=trace_id,
        owner_id=actor_id,
        title=f"Independent review {position}",
        taxonomy_version="w03-review-taxonomy-v1",
        status=RoleBriefStatus.APPROVED,
        created_at=CUTOFF - timedelta(hours=2),
        approved_at=CUTOFF - timedelta(hours=1),
        responsibilities=("inspect synthetic evidence",),
        hard_constraints=(
            RoleConstraint(
                field="position",
                operator=ConstraintOperator.EQUALS,
                value=position,
            ),
        ),
    )
    request = RetrievalRequest(
        retrieval_request_id=uuid4(),
        tenant_context=brief.tenant_context,
        version=1,
        trace_id=trace_id,
        role_brief_id=brief_id,
        role_brief_version=brief.version,
        requested_at=CUTOFF + timedelta(minutes=5),
        feature_cutoff_ts=CUTOFF,
        limit=10,
    )
    return brief, request


def _seed_journey_prerequisites(engine: Engine) -> None:
    """Idempotent owner-only setup for the fixed development identity."""
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO tenants (tenant_id, slug, display_name, created_at)
                VALUES (
                    :tenant_id, 'w03-development-tenant',
                    'W03 Development Tenant', '2026-01-01T00:00:00Z'
                )
                ON CONFLICT (tenant_id) DO NOTHING
                """
            ),
            {"tenant_id": TENANT_ID},
        )
        connection.execute(
            text(
                """
                INSERT INTO canonical_players (
                    player_id, tenant_id, display_name, provenance, valid_from,
                    version, created_at
                )
                VALUES (
                    :player_id, :tenant_id, 'Synthetic Player Alder',
                    '{"classification":"w03_synthetic_generated"}',
                    '2026-01-01T00:00:00Z', 1, '2026-01-01T00:00:00Z'
                )
                ON CONFLICT (player_id) DO NOTHING
                """
            ),
            {"player_id": SELECTED_PLAYER_ID, "tenant_id": TENANT_ID},
        )
        stored_tenant = connection.execute(
            text(
                """
                SELECT tenant_id
                FROM canonical_players
                WHERE player_id = :player_id
                """
            ),
            {"player_id": SELECTED_PLAYER_ID},
        ).scalar_one()
        assert stored_tenant == str(TENANT_ID)

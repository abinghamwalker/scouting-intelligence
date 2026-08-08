"""Positive and fail-closed evidence for the W03 vertical journey."""

from __future__ import annotations

import copy
import hashlib
import json
import runpy
import secrets
from collections.abc import Iterator
from dataclasses import FrozenInstanceError, dataclass, fields, replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

from scouting.audit import AuditWriteError, AuditWriter
from scouting.contracts import (
    ApplicabilityState,
    AuditEvent,
    ConfidenceAssessment,
    DependencyKind,
    EvidenceDimension,
    EvidenceDimensionName,
    RetrievalRequest,
    RoleBrief,
)
from scouting.operations import LocalTelemetry
from scouting.policy import (
    AuthorizationPolicy,
    SessionAuthenticator,
    SyntheticAccount,
    SyntheticPrincipal,
    SyntheticRightsPolicy,
)
from scouting.serving import (
    RetrievalPresentationProfile,
    SyntheticArtifactCatalog,
    SyntheticDomainSnapshot,
    SyntheticServingService,
)
from scouting.storage.embedded import EMBEDDED_DATABASE_USER, create_embedded_engine
from scouting.web import W03WebSettings, create_app
from scouting.workflow import (
    ApplicationDatabase,
    JourneyCommand,
    WorkflowService,
)

ROOT = Path(__file__).resolve().parents[2]
DOMAIN_PATH = ROOT / "tests/fixtures/synthetic/domain.json"
EXPECTED_PATH = ROOT / "tests/fixtures/synthetic/expected_retrieval.json"
TENANT_ID = UUID("70000000-0000-4000-8000-000000000101")
ACTOR_ID = UUID("60000000-0000-4000-8000-000000000101")
OTHER_ACTOR_ID = UUID("60000000-0000-4000-8000-000000000102")


@dataclass(frozen=True, slots=True)
class JourneyHarness:
    client: TestClient
    database: ApplicationDatabase
    workflow: WorkflowService
    principal: SyntheticPrincipal
    token: str
    other_token: str
    telemetry: LocalTelemetry
    engine: Engine


@pytest.fixture(scope="module")
def harness(tmp_path_factory: pytest.TempPathFactory) -> Iterator[JourneyHarness]:
    database_root = tmp_path_factory.mktemp("w03-e2e")
    engine = create_embedded_engine(
        database_root / "journey.sqlite3",
        allowed_root=database_root,
    )
    _seed_prerequisites(engine)
    authorization = AuthorizationPolicy.from_path(
        ROOT / "configs/policies/authorization.yaml",
        known_actor_ids=(ACTOR_ID, OTHER_ACTOR_ID),
    )
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    snapshot = SyntheticDomainSnapshot.from_path(
        DOMAIN_PATH.name,
        allowed_fixture_root=DOMAIN_PATH.parent,
        rights_policy=rights,
    )
    artifacts = SyntheticArtifactCatalog.development()
    database = ApplicationDatabase(engine, tenant_id=TENANT_ID)
    workflow = WorkflowService(
        database=database,
        authorization=authorization,
        serving=SyntheticServingService(snapshot, artifacts=artifacts),
        audit_writer=AuditWriter(),
    )
    token = secrets.token_urlsafe(32)
    other_token = secrets.token_urlsafe(32)
    account = SyntheticAccount(ACTOR_ID, TENANT_ID, ("analyst",))
    other_account = SyntheticAccount(OTHER_ACTOR_ID, TENANT_ID, ("analyst",))
    principal = SyntheticPrincipal(ACTOR_ID, TENANT_ID, ("analyst",))
    telemetry = LocalTelemetry()
    app = create_app(
        authenticator=SessionAuthenticator(
            {
                token: account,
                other_token: other_account,
            }
        ),
        workflow=workflow,
        telemetry=telemetry,
        settings=W03WebSettings(
            tenant_id=TENANT_ID,
            authorization_policy_id=authorization.policy_id,
            data_rights_policy_id=rights.policy_id,
            source_manifest_id=artifacts.source_manifest_id,
            source_manifest_digest=snapshot.manifest_digest,
            template_path=ROOT / "apps/web/templates/w03_journey.html",
        ),
    )
    with TestClient(app) as client:
        yield JourneyHarness(
            client,
            database,
            workflow,
            principal,
            token,
            other_token,
            telemetry,
            engine,
        )
    engine.dispose()


def test_role_brief_to_append_only_audit_matches_development_oracle(
    harness: JourneyHarness,
) -> None:
    expected = _expected_payload()
    journey_payload = {
        "role_brief": expected["role_brief"],
        "retrieval_request": expected["retrieval_request"],
        "shortlist_id": expected["shortlist_entry"]["shortlist_id"],
        "shortlist_entry_id": expected["shortlist_entry"]["shortlist_entry_id"],
        "rationale": expected["shortlist_entry"]["rationale"],
    }

    assert harness.client.get("/health").json()["exposure"] == "loopback_only"
    readiness = harness.client.get("/ready").json()
    assert readiness["database_user"] == EMBEDDED_DATABASE_USER
    assert readiness["tenant_id"] == str(TENANT_ID)
    html = harness.client.get(
        "/w03",
        headers={"Authorization": f"Bearer {harness.token}"},
    )
    assert html.status_code == 200
    assert "does not make a recruitment decision" in html.text

    response = harness.client.post(
        "/api/w03/journey",
        headers={"Authorization": f"Bearer {harness.token}"},
        json=journey_payload,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["result"] == expected["retrieval_result"]
    assert body["explanations"] == expected["explanations"]
    assert body["shortlist_entry"] == expected["shortlist_entry"]
    assert body["audit_actions"] == expected["expected_audit_actions"]
    assert body["database_context"] == {
        "current_user": EMBEDDED_DATABASE_USER,
        "tenant_id": str(TENANT_ID),
        "transaction_local": True,
    }
    assert body["model_quality_claim"] is False
    assert body["policy_ids"] == [
        "w03-authorization-v1",
        "w03-synthetic-data-rights-v1",
    ]
    assert body["admitted_fact_ids"] == [
        "50000000-0000-4000-8000-000000000101",
        "50000000-0000-4000-8000-000000000102",
        "50000000-0000-4000-8000-000000000104",
        "50000000-0000-4000-8000-000000000103",
    ]
    assert body["rejected_evidence"] == [
        {
            "fact_id": "50000000-0000-4000-8000-000000000105",
            "reason_code": "post_cutoff_availability",
        },
        {
            "fact_id": "50000000-0000-4000-8000-000000000106",
            "reason_code": "missing_temporal_evidence",
        },
    ]

    with harness.database.transaction(TENANT_ID) as (connection, identity):
        assert identity.current_user == EMBEDDED_DATABASE_USER
        audit_actions = connection.execute(
            text(
                """
                SELECT target_type
                FROM audit_events
                WHERE request_id = :request_id
                ORDER BY occurred_at, target_type
                """
            ),
            {"request_id": UUID(body["request_id"])},
        ).scalars()
        assert list(audit_actions) == expected["expected_audit_actions"]


def test_audit_failure_rolls_back_the_material_write(harness: JourneyHarness) -> None:
    expected = _expected_payload()
    original_brief = RoleBrief.model_validate_json(json.dumps(expected["role_brief"]))
    role_brief_id = uuid4()
    brief = original_brief.model_copy(update={"role_brief_id": role_brief_id})
    original_request = RetrievalRequest.model_validate_json(
        json.dumps(expected["retrieval_request"])
    )
    retrieval_request = original_request.model_copy(
        update={
            "retrieval_request_id": uuid4(),
            "role_brief_id": role_brief_id,
        }
    )
    authorization = AuthorizationPolicy.from_path(
        ROOT / "configs/policies/authorization.yaml",
        known_actor_ids=(ACTOR_ID,),
    )
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    serving = SyntheticServingService(
        SyntheticDomainSnapshot.from_path(
            DOMAIN_PATH.name,
            allowed_fixture_root=DOMAIN_PATH.parent,
            rights_policy=rights,
        ),
        artifacts=SyntheticArtifactCatalog.development(),
    )
    failing_workflow = WorkflowService(
        database=harness.database,
        authorization=authorization,
        serving=serving,
        audit_writer=_FailingAuditWriter(),
    )

    with pytest.raises(AuditWriteError, match="forced test audit failure"):
        failing_workflow.execute_journey(
            principal=harness.principal,
            request_id=uuid4(),
            command=JourneyCommand(
                role_brief=brief,
                retrieval_request=retrieval_request,
                shortlist_id=uuid4(),
                shortlist_entry_id=uuid4(),
                rationale="Synthetic rollback verification",
            ),
        )

    with harness.database.transaction(TENANT_ID) as (connection, _):
        count = connection.execute(
            text(
                """
                SELECT count(*)
                FROM role_briefs
                WHERE role_brief_id = :role_brief_id
                """
            ),
            {"role_brief_id": role_brief_id},
        ).scalar_one()
        assert count == 0


@pytest.mark.parametrize(
    "collision_target",
    ["role_brief", "shortlist", "shortlist_entry"],
)
def test_same_tenant_material_owner_collisions_deny_and_roll_back(
    harness: JourneyHarness,
    collision_target: str,
) -> None:
    victim_brief, victim_request = _fresh_journey_contracts(ACTOR_ID)
    victim_shortlist_id = uuid4()
    victim_entry_id = uuid4()
    victim_response = harness.client.post(
        "/api/w03/journey",
        headers={"Authorization": f"Bearer {harness.token}"},
        json=_contract_journey_payload(
            brief=victim_brief,
            request=victim_request,
            shortlist_id=victim_shortlist_id,
            shortlist_entry_id=victim_entry_id,
            rationale="Victim-owned synthetic collision evidence",
        ),
    )
    assert victim_response.status_code == 200, victim_response.text

    attacker_role_brief_id = (
        victim_brief.role_brief_id if collision_target == "role_brief" else uuid4()
    )
    attacker_brief, attacker_request = _fresh_journey_contracts(
        OTHER_ACTOR_ID,
        role_brief_id=attacker_role_brief_id,
    )
    attacker_shortlist_id = victim_shortlist_id if collision_target == "shortlist" else uuid4()
    attacker_entry_id = victim_entry_id if collision_target == "shortlist_entry" else uuid4()
    attacker_request_id = uuid4()
    collision = harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {harness.other_token}",
            "x-request-id": str(attacker_request_id),
        },
        json=_contract_journey_payload(
            brief=attacker_brief,
            request=attacker_request,
            shortlist_id=attacker_shortlist_id,
            shortlist_entry_id=attacker_entry_id,
            rationale=f"Attacker {collision_target} collision must roll back",
        ),
    )

    assert collision.status_code == 403
    assert collision.json() == {"detail": "action denied"}
    with harness.database.transaction(TENANT_ID) as (connection, _):
        attacker_effects = connection.execute(
            text(
                """
                SELECT
                    (
                        SELECT count(*)
                        FROM role_briefs
                        WHERE role_brief_id = :role_brief_id
                          AND owner_id = :attacker_id
                    ) AS role_brief_count,
                    (
                        SELECT count(*)
                        FROM retrieval_runs
                        WHERE retrieval_request_id = :retrieval_request_id
                    ) AS retrieval_count,
                    (
                        SELECT count(*)
                        FROM candidate_results AS candidate
                        JOIN retrieval_runs AS retrieval
                          ON retrieval.tenant_id = candidate.tenant_id
                         AND retrieval.retrieval_run_id = candidate.retrieval_run_id
                        WHERE retrieval.retrieval_request_id = :retrieval_request_id
                    ) AS candidate_count,
                    (
                        SELECT count(*)
                        FROM shortlists
                        WHERE shortlist_id = :shortlist_id
                          AND owner_id = :attacker_id
                    ) AS shortlist_count,
                    (
                        SELECT count(*)
                        FROM shortlist_entries
                        WHERE shortlist_entry_id = :shortlist_entry_id
                          AND owner_id = :attacker_id
                    ) AS entry_count,
                    (
                        SELECT count(*)
                        FROM audit_events
                        WHERE request_id = :request_id
                    ) AS audit_count
                """
            ),
            {
                "attacker_id": OTHER_ACTOR_ID,
                "role_brief_id": attacker_brief.role_brief_id,
                "retrieval_request_id": attacker_request.retrieval_request_id,
                "shortlist_id": attacker_shortlist_id,
                "shortlist_entry_id": attacker_entry_id,
                "request_id": attacker_request_id,
            },
        ).one()
        victim_owners = connection.execute(
            text(
                """
                SELECT
                    (
                        SELECT owner_id
                        FROM role_briefs
                        WHERE role_brief_id = :role_brief_id
                          AND version = :role_brief_version
                    ) AS role_brief_owner,
                    (
                        SELECT owner_id
                        FROM shortlists
                        WHERE shortlist_id = :shortlist_id
                    ) AS shortlist_owner,
                    (
                        SELECT owner_id
                        FROM shortlist_entries
                        WHERE shortlist_entry_id = :shortlist_entry_id
                    ) AS entry_owner
                """
            ),
            {
                "role_brief_id": victim_brief.role_brief_id,
                "role_brief_version": victim_brief.version,
                "shortlist_id": victim_shortlist_id,
                "shortlist_entry_id": victim_entry_id,
            },
        ).one()

    assert tuple(attacker_effects) == (0, 0, 0, 0, 0, 0)
    assert tuple(victim_owners) == (str(ACTOR_ID), str(ACTOR_ID), str(ACTOR_ID))


def test_exact_same_owner_material_replay_is_idempotent(
    harness: JourneyHarness,
) -> None:
    brief, request = _fresh_journey_contracts(ACTOR_ID)
    shortlist_id = uuid4()
    shortlist_entry_id = uuid4()
    payload = _contract_journey_payload(
        brief=brief,
        request=request,
        shortlist_id=shortlist_id,
        shortlist_entry_id=shortlist_entry_id,
        rationale="Exact canonical replay evidence",
    )
    first_request_id = uuid4()
    repeated_request_id = uuid4()

    first = harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {harness.token}",
            "x-request-id": str(first_request_id),
        },
        json=payload,
    )
    repeated = harness.client.post(
        "/api/w03/journey",
        headers={
            "Authorization": f"Bearer {harness.token}",
            "x-request-id": str(repeated_request_id),
        },
        json=payload,
    )

    assert first.status_code == 200, first.text
    assert repeated.status_code == 200, repeated.text
    assert repeated.json()["result"] == first.json()["result"]
    assert repeated.json()["shortlist_entry"] == first.json()["shortlist_entry"]
    with harness.database.transaction(TENANT_ID) as (connection, _):
        counts = connection.execute(
            text(
                """
                SELECT
                    (
                        SELECT count(*)
                        FROM role_briefs
                        WHERE role_brief_id = :role_brief_id
                          AND version = :role_brief_version
                    ) AS role_brief_count,
                    (
                        SELECT count(*)
                        FROM retrieval_runs
                        WHERE retrieval_request_id = :retrieval_request_id
                    ) AS retrieval_count,
                    (
                        SELECT count(*)
                        FROM candidate_results AS candidate
                        JOIN retrieval_runs AS retrieval
                          ON retrieval.tenant_id = candidate.tenant_id
                         AND retrieval.retrieval_run_id = candidate.retrieval_run_id
                        WHERE retrieval.retrieval_request_id = :retrieval_request_id
                    ) AS candidate_count,
                    (
                        SELECT count(*)
                        FROM shortlists
                        WHERE shortlist_id = :shortlist_id
                    ) AS shortlist_count,
                    (
                        SELECT count(*)
                        FROM shortlist_entries
                        WHERE shortlist_entry_id = :shortlist_entry_id
                    ) AS entry_count,
                    (
                        SELECT count(*)
                        FROM audit_events
                        WHERE request_id IN (:first_request_id, :repeated_request_id)
                    ) AS audit_count
                """
            ),
            {
                "role_brief_id": brief.role_brief_id,
                "role_brief_version": brief.version,
                "retrieval_request_id": request.retrieval_request_id,
                "shortlist_id": shortlist_id,
                "shortlist_entry_id": shortlist_entry_id,
                "first_request_id": first_request_id,
                "repeated_request_id": repeated_request_id,
            },
        ).one()
    assert tuple(counts) == (1, 1, 1, 1, 1, 8)


def test_unknown_session_and_cross_tenant_api_requests_deny_generically(
    harness: JourneyHarness,
) -> None:
    payload = _journey_payload()
    unknown = harness.client.post(
        "/api/w03/journey",
        headers={"Authorization": f"Bearer {secrets.token_urlsafe(32)}"},
        json=payload,
    )
    assert unknown.status_code == 401
    assert unknown.json() == {"detail": "session authentication failed"}
    assert "role_brief" not in unknown.text

    cross_tenant_payload = copy.deepcopy(payload)
    cross_tenant_payload["role_brief"]["tenant_context"]["tenant_id"] = (
        "70000000-0000-4000-8000-000000000102"
    )
    denied = harness.client.post(
        "/api/w03/journey",
        headers={"Authorization": f"Bearer {harness.token}"},
        json=cross_tenant_payload,
    )
    assert denied.status_code == 403
    assert denied.json() == {"detail": "action denied"}
    assert "retrieval_result" not in denied.text


@pytest.mark.parametrize(
    ("action", "database_action", "expected_scope"),
    [
        ("read", "read", []),
        ("export", "export", ["denied_attempt"]),
    ],
)
def test_confidential_denial_is_content_free_and_append_only_audited(
    harness: JourneyHarness,
    action: str,
    database_action: str,
    expected_scope: list[str],
) -> None:
    evidence_id = uuid4()
    response = harness.client.post(
        f"/api/w03/confidential-evidence/{action}",
        headers={"Authorization": f"Bearer {harness.token}"},
        json={"evidence_id": str(evidence_id)},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "action denied"}
    assert str(evidence_id) not in response.text
    assert str(evidence_id) not in harness.telemetry.serialized_snapshot()

    request_id = UUID(response.headers["x-request-id"])
    with harness.database.transaction(TENANT_ID) as (connection, identity):
        row = connection.execute(
            text(
                """
                SELECT
                    actor_id, tenant_id, action, target_type, target_id,
                    before_digest, after_digest, reason, export_scope
                FROM audit_events
                WHERE request_id = :request_id
                """
            ),
            {"request_id": request_id},
        ).one()
    assert identity.current_user == EMBEDDED_DATABASE_USER
    assert row.actor_id == str(ACTOR_ID)
    assert row.tenant_id == str(TENANT_ID)
    assert row.action == database_action
    assert row.target_type == "confidential_evidence.denied_attempt"
    assert row.target_id == str(evidence_id)
    assert row.before_digest is None
    assert row.after_digest is None
    assert row.reason == "authorization_denied"
    assert json.loads(row.export_scope) == expected_scope


def test_exact_cutoff_facts_are_excluded_through_serving(
    tmp_path: Path,
) -> None:
    document = _development_domain_document()
    payload = document["payload"]
    cutoff = payload["decision_cutoff_ts"]
    payload["facts"].extend(
        [
            {
                "fact_id": "50000000-0000-4000-8000-000000000107",
                "player_id": "30000000-0000-4000-8000-000000000101",
                "metric": "progressive_actions_per_90",
                "value": 99.0,
                "observed_at": cutoff,
                "available_at": "2026-02-28T23:59:59Z",
                "expected_admission": False,
                "arrival_class": "on_time",
            },
            {
                "fact_id": "50000000-0000-4000-8000-000000000108",
                "player_id": "30000000-0000-4000-8000-000000000101",
                "metric": "progressive_actions_per_90",
                "value": 98.0,
                "observed_at": "2026-02-28T23:59:59Z",
                "available_at": cutoff,
                "expected_admission": False,
                "arrival_class": "late",
            },
        ]
    )
    fixture_root = tmp_path / "fixture"
    _write_domain_document(fixture_root, document)
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    snapshot = SyntheticDomainSnapshot.from_path(
        "domain.json",
        allowed_fixture_root=fixture_root,
        rights_policy=rights,
    )
    role_brief, retrieval_request = _expected_contracts()
    outcome = SyntheticServingService(
        snapshot,
        artifacts=SyntheticArtifactCatalog.development(),
    ).retrieve(role_brief, retrieval_request)

    assert outcome.status == "available"
    assert outcome.result is not None
    rejected = {item.fact_id: item.reason_code for item in outcome.rejected_evidence}
    assert rejected[UUID("50000000-0000-4000-8000-000000000107")] == ("post_cutoff_observation")
    assert rejected[UUID("50000000-0000-4000-8000-000000000108")] == ("post_cutoff_availability")
    assert all(
        fact_id not in outcome.admitted_fact_ids
        for fact_id in (
            UUID("50000000-0000-4000-8000-000000000107"),
            UUID("50000000-0000-4000-8000-000000000108"),
        )
    )


@pytest.mark.parametrize(
    ("catalog", "missing"),
    [
        (
            replace(
                SyntheticArtifactCatalog.development(),
                model_artifact_id=None,
                model_artifact_digest=None,
                model_version=None,
            ),
            ("model_artifact",),
        ),
        (
            replace(
                SyntheticArtifactCatalog.development(),
                retrieval_index_id=None,
                retrieval_index_digest=None,
                index_version=None,
            ),
            ("retrieval_index",),
        ),
    ],
)
def test_missing_model_or_index_is_labelled_unavailable_without_fallback(
    catalog: SyntheticArtifactCatalog,
    missing: tuple[str, ...],
) -> None:
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    snapshot = SyntheticDomainSnapshot.from_path(
        DOMAIN_PATH.name,
        allowed_fixture_root=DOMAIN_PATH.parent,
        rights_policy=rights,
    )
    role_brief, retrieval_request = _expected_contracts()
    outcome = SyntheticServingService(snapshot, artifacts=catalog).retrieve(
        role_brief,
        retrieval_request,
    )
    assert outcome.status == "unavailable"
    assert outcome.result is None
    assert outcome.explanations == ()
    assert outcome.missing_evidence == missing


def test_presentation_profile_is_immutable_and_carries_no_serving_context() -> None:
    profile = RetrievalPresentationProfile.development()
    profile_fields = {field.name for field in fields(profile)}

    assert profile_fields.isdisjoint(
        {
            "candidate_id",
            "cutoff",
            "feature_cutoff_ts",
            "lineage",
            "player_id",
            "rank",
            "tenant",
            "tenant_context",
        }
    )
    with pytest.raises(FrozenInstanceError):
        setattr(profile, "explanation_template", "{candidate_display_name}")


@pytest.mark.parametrize("invalid_value", [-0.01, 1.01, float("nan"), float("inf"), 1, True])
def test_presentation_profile_rejects_invalid_unit_interval_values(
    invalid_value: object,
) -> None:
    profile = RetrievalPresentationProfile.development()
    invalid_dimension = profile.dimensions[0].model_copy(update={"score": invalid_value})

    with pytest.raises(ValueError, match="strict float"):
        replace(
            profile,
            dimensions=(invalid_dimension, *profile.dimensions[1:]),
        )


@pytest.mark.parametrize(
    ("field_name", "reason_codes"),
    [
        ("dimension", ()),
        ("dimension", ("duplicate_reason", "duplicate_reason")),
        ("candidate", ()),
        ("candidate", ("duplicate_reason", "duplicate_reason")),
        ("explanation", ()),
        ("explanation", ("duplicate_reason", "duplicate_reason")),
    ],
)
def test_presentation_profile_rejects_empty_or_duplicate_reason_codes(
    field_name: str,
    reason_codes: tuple[str, ...],
) -> None:
    profile = RetrievalPresentationProfile.development()
    if field_name == "dimension":
        invalid_dimension = profile.dimensions[0].model_copy(update={"reason_codes": reason_codes})
        changes: dict[str, object] = {"dimensions": (invalid_dimension, *profile.dimensions[1:])}
    elif field_name == "candidate":
        changes = {"candidate_reason_codes": reason_codes}
    else:
        changes = {"explanation_reason_codes": reason_codes}

    with pytest.raises(ValueError, match="non-empty tuple|unique"):
        replace(profile, **changes)


@pytest.mark.parametrize(
    "limitations",
    [
        (),
        ("",),
        ("duplicate limitation", "duplicate limitation"),
    ],
)
def test_presentation_profile_rejects_invalid_limitations(
    limitations: tuple[str, ...],
) -> None:
    profile = RetrievalPresentationProfile.development()
    invalid_confidence = profile.candidate_confidence.model_copy(
        update={"limitations": limitations}
    )

    with pytest.raises(ValueError, match="candidate limitations"):
        replace(profile, candidate_confidence=invalid_confidence)


@pytest.mark.parametrize(
    "template",
    [
        "This is a bounded static explanation.",
        "This static explanation preserves {{literal braces}} unchanged.",
    ],
)
def test_presentation_profile_accepts_and_preserves_static_explanations(
    template: str,
) -> None:
    profile = replace(
        RetrievalPresentationProfile.development(),
        explanation_template=template,
    )

    assert profile.render_explanation(candidate_display_name="Ignored Candidate Name") == template


def test_presentation_profile_safely_populates_one_plain_candidate_field() -> None:
    profile = replace(
        RetrievalPresentationProfile.development(),
        explanation_template="Evidence is shown for {candidate_display_name}.",
    )

    assert profile.render_explanation(candidate_display_name="Candidate {Literal}") == (
        "Evidence is shown for Candidate {Literal}."
    )


@pytest.mark.parametrize(
    "template",
    [
        "",
        "{player_name} has alternate evidence.",
        "{} has alternate evidence.",
        "{candidate_display_name} and {candidate_display_name} have evidence.",
        "{candidate_display_name} has {other_field}.",
        "{candidate_display_name!r} has alternate evidence.",
        "{candidate_display_name.name} has alternate evidence.",
        "{candidate_display_name:>20} has alternate evidence.",
        "{candidate_display_name",
        "candidate_display_name}",
    ],
)
def test_presentation_profile_rejects_unsafe_explanation_templates(
    template: str,
) -> None:
    with pytest.raises(ValueError, match="explanation template"):
        replace(
            RetrievalPresentationProfile.development(),
            explanation_template=template,
        )


def test_alternate_partition_selection_ids_and_lineage_are_generic_and_stable(
    tmp_path: Path,
) -> None:
    document = _development_domain_document()
    manifest = document["manifest"]
    payload = document["payload"]
    assert isinstance(manifest, dict)
    assert isinstance(payload, dict)
    manifest["fixture_id"] = "w03-temporary-alternate-partition"
    manifest["partition"] = "protected_test"
    facts = payload["facts"]
    assert isinstance(facts, list)
    for fact in facts:
        assert isinstance(fact, dict)
        fact["metric"] = "alternate_signal_per_90"
        if fact["fact_id"] == "50000000-0000-4000-8000-000000000104":
            fact["value"] = 150.0
        if fact["fact_id"] in {
            "50000000-0000-4000-8000-000000000105",
            "50000000-0000-4000-8000-000000000106",
        }:
            fact["value"] = 200.0
            fact["observed_at"] = "2026-02-20T20:00:00Z"
            fact["available_at"] = "2026-02-21T09:00:00Z"

    fixture_root = tmp_path / "alternate-fixture"
    _write_domain_document(fixture_root, document)
    rights = SyntheticRightsPolicy.from_path(ROOT / "configs/policies/data-rights.yaml")
    snapshot = SyntheticDomainSnapshot.from_path(
        "domain.json",
        allowed_fixture_root=fixture_root,
        expected_partition="protected_test",
        rights_policy=rights,
    )
    alternate_profile = _alternate_presentation_profile()
    catalog = replace(
        SyntheticArtifactCatalog.development(),
        source_manifest_id=UUID("91000000-0000-4000-8000-000000000101"),
        feature_schema_id=UUID("91000000-0000-4000-8000-000000000102"),
        feature_schema_hash="4" * 64,
        model_artifact_id=UUID("91000000-0000-4000-8000-000000000103"),
        model_artifact_digest="5" * 64,
        model_version="w03-alternate-model-seam-v1",
        retrieval_index_id=UUID("91000000-0000-4000-8000-000000000104"),
        retrieval_index_digest="6" * 64,
        index_version="w03-alternate-index-seam-v1",
        presentation_profile=alternate_profile,
        source_observed_at=datetime(2026, 1, 2, tzinfo=UTC),
        source_available_at=datetime(2026, 1, 3, tzinfo=UTC),
        feature_schema_observed_at=datetime(2026, 1, 4, tzinfo=UTC),
        feature_schema_available_at=datetime(2026, 1, 5, tzinfo=UTC),
        model_artifact_observed_at=datetime(2026, 1, 6, tzinfo=UTC),
        model_artifact_available_at=datetime(2026, 1, 7, tzinfo=UTC),
        retrieval_index_observed_at=datetime(2026, 1, 8, tzinfo=UTC),
        retrieval_index_available_at=datetime(2026, 1, 9, tzinfo=UTC),
    )
    role_brief, development_request = _expected_contracts()
    request = development_request.model_copy(
        update={
            "retrieval_request_id": UUID("c0000000-0000-4000-8000-000000000202"),
            "excluded_player_ids": (UUID("30000000-0000-4000-8000-000000000101"),),
        }
    )
    serving = SyntheticServingService(snapshot, artifacts=catalog)
    first = serving.retrieve(role_brief, request)
    repeated = serving.retrieve(role_brief, request)

    assert first == repeated
    assert first.result is not None
    assert first.explanations == repeated.explanations
    assert first.result.retrieval_result_id == UUID("d0000000-0000-4000-8000-000000000202")
    assert first.result.retrieval_run_id == UUID("e0000000-0000-4000-8000-000000000202")
    assert [candidate.player_id for candidate in first.result.candidates] == [
        UUID("30000000-0000-4000-8000-000000000102")
    ]
    candidate = first.result.candidates[0]
    assert candidate.rank == 1
    assert candidate.evidence_dimensions == alternate_profile.dimensions
    assert candidate.confidence == alternate_profile.candidate_confidence
    assert candidate.reason_codes == alternate_profile.candidate_reason_codes
    assert candidate.coverage.overall == 0.6667
    assert first.explanations[0].reason_codes == (alternate_profile.explanation_reason_codes)
    assert first.explanations[0].summary == (
        "Synthetic Player Birch is presented by the alternate artifact profile "
        "without a recruitment-success prediction."
    )
    assert "progressive-action" not in first.explanations[0].summary

    other_request = request.model_copy(
        update={"retrieval_request_id": UUID("c0000000-0000-4000-8000-000000000203")}
    )
    other = serving.retrieve(role_brief, other_request)
    assert other.result is not None
    assert other.result.retrieval_result_id != first.result.retrieval_result_id
    assert other.result.retrieval_run_id != first.result.retrieval_run_id

    dependencies = {
        dependency.kind: dependency
        for dependency in first.result.temporal_evidence.dependency_lineage.dependencies
    }
    assert dependencies[DependencyKind.SOURCE_MANIFEST].dependency_id == (
        catalog.source_manifest_id
    )
    assert dependencies[DependencyKind.SOURCE_MANIFEST].digest == snapshot.manifest_digest
    assert dependencies[DependencyKind.SOURCE_MANIFEST].observed_at == (catalog.source_observed_at)
    assert dependencies[DependencyKind.SOURCE_MANIFEST].available_at == (
        catalog.source_available_at
    )
    assert dependencies[DependencyKind.FEATURE_SCHEMA].dependency_id == (catalog.feature_schema_id)
    assert dependencies[DependencyKind.FEATURE_SCHEMA].digest == catalog.feature_schema_hash
    assert dependencies[DependencyKind.FEATURE_SCHEMA].observed_at == (
        catalog.feature_schema_observed_at
    )
    assert dependencies[DependencyKind.FEATURE_SCHEMA].available_at == (
        catalog.feature_schema_available_at
    )
    assert dependencies[DependencyKind.MODEL_ARTIFACT].dependency_id == (catalog.model_artifact_id)
    assert dependencies[DependencyKind.MODEL_ARTIFACT].digest == (catalog.model_artifact_digest)
    assert dependencies[DependencyKind.MODEL_ARTIFACT].observed_at == (
        catalog.model_artifact_observed_at
    )
    assert dependencies[DependencyKind.MODEL_ARTIFACT].available_at == (
        catalog.model_artifact_available_at
    )
    assert dependencies[DependencyKind.RETRIEVAL_INDEX].dependency_id == (
        catalog.retrieval_index_id
    )
    assert dependencies[DependencyKind.RETRIEVAL_INDEX].digest == (catalog.retrieval_index_digest)
    assert dependencies[DependencyKind.RETRIEVAL_INDEX].observed_at == (
        catalog.retrieval_index_observed_at
    )
    assert dependencies[DependencyKind.RETRIEVAL_INDEX].available_at == (
        catalog.retrieval_index_available_at
    )


def test_worker_readiness_uses_app_role_and_starts_no_listener(
    harness: JourneyHarness,
) -> None:
    telemetry = LocalTelemetry()
    worker_namespace = runpy.run_path(str(ROOT / "services/worker/main.py"))
    run_once = worker_namespace["run_once"]
    assert callable(run_once)
    check = run_once(
        workflow=harness.workflow,
        tenant_id=TENANT_ID,
        telemetry=telemetry,
    )
    assert check.status == "ready"
    assert check.database_user == EMBEDDED_DATABASE_USER
    assert check.tenant_id == TENANT_ID
    assert check.listener_started is False
    assert telemetry.snapshot().metrics["worker_checks_total"] == 1


class _FailingAuditWriter(AuditWriter):
    def append(self, connection: Connection, event: AuditEvent) -> None:
        del connection, event
        raise AuditWriteError("forced test audit failure")


def _expected_payload() -> dict[str, object]:
    document = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    payload = document["payload"]
    assert isinstance(payload, dict)
    return payload


def _journey_payload() -> dict[str, object]:
    expected = _expected_payload()
    shortlist_entry = expected["shortlist_entry"]
    assert isinstance(shortlist_entry, dict)
    return {
        "role_brief": copy.deepcopy(expected["role_brief"]),
        "retrieval_request": copy.deepcopy(expected["retrieval_request"]),
        "shortlist_id": shortlist_entry["shortlist_id"],
        "shortlist_entry_id": shortlist_entry["shortlist_entry_id"],
        "rationale": shortlist_entry["rationale"],
    }


def _expected_contracts() -> tuple[RoleBrief, RetrievalRequest]:
    expected = _expected_payload()
    role_brief = RoleBrief.model_validate_json(json.dumps(expected["role_brief"]))
    retrieval_request = RetrievalRequest.model_validate_json(
        json.dumps(expected["retrieval_request"])
    )
    return role_brief, retrieval_request


def _fresh_journey_contracts(
    actor_id: UUID,
    *,
    role_brief_id: UUID | None = None,
) -> tuple[RoleBrief, RetrievalRequest]:
    template_brief, template_request = _expected_contracts()
    brief_id = role_brief_id or uuid4()
    trace_id = uuid4()
    brief = template_brief.model_copy(
        update={
            "role_brief_id": brief_id,
            "trace_id": trace_id,
            "owner_id": actor_id,
            "title": f"Synthetic collision {brief_id.hex[:8]} {actor_id.hex[-4:]}",
        }
    )
    request = template_request.model_copy(
        update={
            "retrieval_request_id": uuid4(),
            "trace_id": trace_id,
            "role_brief_id": brief_id,
            "role_brief_version": brief.version,
        }
    )
    return brief, request


def _contract_journey_payload(
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


def _alternate_presentation_profile() -> RetrievalPresentationProfile:
    dimensions = tuple(
        EvidenceDimension(
            name=name,
            score=0.11 + index / 100,
            confidence=0.21 + index / 100,
            reason_codes=(f"alternate_{name.value}_reason",),
        )
        for index, name in enumerate(EvidenceDimensionName)
    )
    return RetrievalPresentationProfile(
        dimensions=dimensions,
        candidate_confidence=ConfidenceAssessment(
            score=0.73,
            applicability=ApplicabilityState.APPLICABLE,
            limitations=(
                "Alternate artifact profile evidence only",
                "Alternate evidence remains non-predictive",
            ),
        ),
        candidate_reason_codes=(
            "alternate_candidate_profile",
            "resemblance_only",
        ),
        explanation_reason_codes=("alternate_explanation_profile",),
        explanation_template=(
            "{candidate_display_name} is presented by the alternate artifact profile "
            "without a recruitment-success prediction."
        ),
    )


def _development_domain_document() -> dict[str, object]:
    document = json.loads(DOMAIN_PATH.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return copy.deepcopy(document)


def _write_domain_document(
    fixture_root: Path,
    document: dict[str, object],
) -> None:
    manifest = document["manifest"]
    payload = document["payload"]
    assert isinstance(manifest, dict)
    assert isinstance(payload, dict)
    manifest["content_digest"] = hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    fixture_root.mkdir()
    (fixture_root / "domain.json").write_text(
        json.dumps(document),
        encoding="utf-8",
    )


def _seed_prerequisites(engine: Engine) -> None:
    """Owner-only fixture setup; application code never receives this connection."""
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
                INSERT INTO canonical_teams (
                    team_id, tenant_id, display_name, provenance, valid_from,
                    version, created_at
                )
                VALUES (
                    :team_id, :tenant_id, 'Synthetic Northbridge Athletic',
                    '{"classification":"w03_synthetic_generated"}',
                    '2026-01-01T00:00:00Z', 1, '2026-01-01T00:00:00Z'
                )
                ON CONFLICT (team_id) DO NOTHING
                """
            ),
            {
                "team_id": UUID("20000000-0000-4000-8000-000000000101"),
                "tenant_id": TENANT_ID,
            },
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
            {
                "player_id": UUID("30000000-0000-4000-8000-000000000101"),
                "tenant_id": TENANT_ID,
            },
        )

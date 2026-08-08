"""Synthetic automated confidentiality and tamper tests for W08 export."""
# ruff: noqa: E501

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from scouting.policy import LocalRole, R1Principal
from scouting.storage import GuardedStorage, InvalidArtifactPathError
from scouting.storage.embedded import create_embedded_engine
from scouting.workflow import (
    EvidenceExportDenied,
    EvidenceExportIntegrityError,
    LocalEvidenceExporter,
)


@pytest.fixture
def export_runtime(
    tmp_path: Path,
) -> tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID]:
    engine = create_embedded_engine(tmp_path / "security-export.sqlite3", allowed_root=tmp_path)
    storage = GuardedStorage({"evidence_packs": tmp_path / "evidence-packs"})
    tenant, analyst, scout, brief, retrieval, shortlist = (uuid4() for _ in range(6))
    now = "2026-08-04T00:00:00+00:00"
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO tenants VALUES (:tenant, :slug, 'Synthetic', :now)"),
            {"tenant": tenant, "slug": f"security-{tenant.hex}", "now": now},
        )
        for actor, role in ((analyst, "analyst"), (scout, "scout")):
            connection.execute(
                text("INSERT INTO local_accounts VALUES (:actor, :tenant, :name, 1, :now, NULL)"),
                {"actor": actor, "tenant": tenant, "name": f"Synthetic {role}", "now": now},
            )
            connection.execute(
                text("INSERT INTO local_account_roles VALUES (:actor, :role, :now, :analyst)"),
                {"actor": actor, "role": role, "now": now, "analyst": analyst},
            )
        connection.execute(
            text(
                "INSERT INTO role_brief_workflows VALUES (:brief, :tenant, :analyst, 'TEAM', 1, 1, :now, :now)"
            ),
            {"brief": brief, "tenant": tenant, "analyst": analyst, "now": now},
        )
        connection.execute(
            text("""INSERT INTO role_brief_revisions VALUES
            (:brief, :tenant, 1, NULL, :trace, :analyst, :analyst, 'TEAM', 'Synthetic role', 'template-v1', 'taxonomy-v1', 'approved',
            '[\"synthetic responsibility\"]', '[]', '[]', '[]', 'synthetic approval', NULL, NULL, :now, :now, :analyst, :now)"""),
            {"brief": brief, "tenant": tenant, "trace": uuid4(), "analyst": analyst, "now": now},
        )
        connection.execute(
            text("""INSERT INTO replayable_retrieval_links (retrieval_link_id, tenant_id, role_brief_id, role_brief_version, retrieval_request_id, retrieval_result_id, retrieval_run_id, query_player_id, exemplar_player_ids, model_version, index_version, data_version, taxonomy_version, result_digest, lineage_digest, claim_boundary, evidence_class, applicability, limitations, created_by, created_at) VALUES
            (:retrieval, :tenant, :brief, 1, :request, :result, :run, :player, '[]', 'model-v1', 'index-v1', 'data-v1', 'taxonomy-v1',
            :result_digest, :lineage_digest, 'resemblance_only', 'synthetic_development_only', 'LIMITED', '[\"synthetic mechanics only\"]', :analyst, :now)"""),
            {
                "retrieval": retrieval,
                "tenant": tenant,
                "brief": brief,
                "request": uuid4(),
                "result": uuid4(),
                "run": uuid4(),
                "player": uuid4(),
                "result_digest": "a" * 64,
                "lineage_digest": "b" * 64,
                "analyst": analyst,
                "now": now,
            },
        )
        connection.execute(
            text(
                "INSERT INTO workflow_shortlists VALUES (:shortlist, :tenant, :brief, 1, :analyst, 'TEAM', 'Synthetic shortlist', 1, :now, :now)"
            ),
            {
                "shortlist": shortlist,
                "tenant": tenant,
                "brief": brief,
                "analyst": analyst,
                "now": now,
            },
        )
    try:
        yield engine, storage, tenant, analyst, scout, brief, retrieval, shortlist
    finally:
        engine.dispose()


def _principal(actor: UUID, tenant: UUID, role: LocalRole) -> R1Principal:
    return R1Principal(actor, tenant, frozenset({role}), uuid4())


def _export(
    exporter: LocalEvidenceExporter,
    connection: object,
    principal: R1Principal,
    brief: UUID,
    retrieval: UUID,
    shortlist: UUID,
    pack: UUID,
) -> object:
    return exporter.export(  # type: ignore[arg-type]
        connection,
        principal=principal,
        evidence_pack_id=pack,
        role_brief_id=brief,
        role_brief_version=1,
        retrieval_link_id=retrieval,
        shortlist_id=shortlist,
        trace_id=uuid4(),
        request_id=uuid4(),
    )


def test_admin_and_cross_tenant_idor_are_denied(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    exporter = LocalEvidenceExporter(storage)
    with engine.begin() as connection:
        with pytest.raises(EvidenceExportDenied):
            _export(
                exporter,
                connection,
                _principal(analyst, tenant, LocalRole.ADMIN),
                brief,
                retrieval,
                shortlist,
                uuid4(),
            )
        with pytest.raises(EvidenceExportDenied):
            _export(
                exporter,
                connection,
                _principal(analyst, uuid4(), LocalRole.ANALYST),
                brief,
                retrieval,
                shortlist,
                uuid4(),
            )


def test_tamper_and_append_only_revocation_deny_readback(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    exporter = LocalEvidenceExporter(storage)
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    with engine.begin() as connection:
        result = _export(exporter, connection, principal, brief, retrieval, shortlist, uuid4())
    location = next((storage._roots["evidence_packs"]).rglob("*.json"))
    if location.name.endswith("manifest.json"):
        location = next(
            path
            for path in storage._roots["evidence_packs"].rglob("*.json")
            if not path.name.endswith("manifest.json")
        )
    location.chmod(0o600)
    location.write_text("{}", encoding="utf-8")
    with engine.begin() as connection, pytest.raises(EvidenceExportIntegrityError):
        exporter.read(connection, principal=principal, evidence_pack_id=result.evidence_pack_id)
    # A fresh pack exercises an actual durable revocation after the tamper witness.
    with engine.begin() as connection:
        fresh = _export(exporter, connection, principal, brief, retrieval, shortlist, uuid4())
        exporter.revoke(
            connection,
            principal=principal,
            evidence_pack_id=fresh.evidence_pack_id,
            reason="synthetic compromise response",
            trace_id=uuid4(),
            request_id=uuid4(),
        )
        with pytest.raises(EvidenceExportDenied):
            exporter.read(connection, principal=principal, evidence_pack_id=fresh.evidence_pack_id)
        with pytest.raises(Exception, match="append-only"):
            connection.execute(
                text("DELETE FROM evidence_export_revocations WHERE evidence_pack_id = :id"),
                {"id": fresh.evidence_pack_id},
            )


def test_guarded_storage_rejects_traversal_absolute_and_symlink_hazards(tmp_path: Path) -> None:
    storage = GuardedStorage({"evidence_packs": tmp_path / "packs"})
    for path in ("../outside.json", "/tmp/outside.json", "folder/../../outside.json"):
        with pytest.raises(InvalidArtifactPathError):
            storage.write_bytes(
                "evidence_packs",
                path,
                b"x",
                media_type="application/json",
                lineage={"x": 1},
                retention={"x": 1},
            )
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "packs" / "escaped").symlink_to(outside, target_is_directory=True)
    with pytest.raises(Exception, match="path component"):
        storage.write_bytes(
            "evidence_packs",
            "escaped/pack.json",
            b"x",
            media_type="application/json",
            lineage={"x": 1},
            retention={"x": 1},
        )


def test_private_history_uses_only_latest_assignment_without_origin_side_channel(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    former_assignee, current_assignee, private_author = uuid4(), uuid4(), uuid4()
    target_entry, former_grant_entry, author_grant_entry = uuid4(), uuid4(), uuid4()
    now = "2026-08-04T00:00:00+00:00"
    with engine.begin() as connection:
        for actor, name, roles in (
            (former_assignee, "Former synthetic analyst-scout", ("analyst", "scout")),
            (current_assignee, "Current synthetic analyst-scout", ("analyst", "scout")),
            (private_author, "Author synthetic analyst-approver", ("analyst", "approver")),
        ):
            connection.execute(
                text("INSERT INTO local_accounts VALUES (:actor, :tenant, :name, 1, :now, NULL)"),
                {"actor": actor, "tenant": tenant, "name": name, "now": now},
            )
            for role in roles:
                connection.execute(
                    text("INSERT INTO local_account_roles VALUES (:actor, :role, :now, :owner)"),
                    {"actor": actor, "role": role, "now": now, "owner": analyst},
                )
        for entry, latest in ((target_entry, 2), (former_grant_entry, 1), (author_grant_entry, 1)):
            connection.execute(
                text(
                    "INSERT INTO shortlist_entry_workflows VALUES (:entry, :tenant, :shortlist, :player, :latest, :latest, :now, :now)"
                ),
                {
                    "entry": entry,
                    "tenant": tenant,
                    "shortlist": shortlist,
                    "player": uuid4(),
                    "latest": latest,
                    "now": now,
                },
            )

        def revision(entry: UUID, number: int, previous: int | None, assigned: UUID | None) -> None:
            connection.execute(
                text("""INSERT INTO shortlist_entry_revisions
                (shortlist_entry_id, tenant_id, shortlist_id, revision, previous_revision,
                 role_brief_id, role_brief_version, player_id, state, owner_id, assigned_scout_id,
                 retrieval_link_id, rationale, transition_reason, changed_by, created_at)
                VALUES (:entry, :tenant, :shortlist, :revision, :previous, :brief, 1, :player,
                 'scout', :owner, :assigned, :retrieval, 'synthetic rationale',
                 'synthetic assignment', :owner, :now)"""),
                {
                    "entry": entry,
                    "tenant": tenant,
                    "shortlist": shortlist,
                    "revision": number,
                    "previous": previous,
                    "brief": brief,
                    "player": uuid4(),
                    "owner": analyst,
                    "assigned": assigned,
                    "retrieval": retrieval,
                    "now": now,
                },
            )

        revision(target_entry, 1, None, former_assignee)
        revision(target_entry, 2, 1, current_assignee)
        revision(former_grant_entry, 1, None, former_assignee)
        revision(author_grant_entry, 1, None, private_author)
        for body, visibility, origin in (
            ("team record", "TEAM", "synthetic_automated_test"),
            ("private former-assignee secret", "OWNER_ONLY", "human_entered_local"),
        ):
            connection.execute(
                text("""INSERT INTO shortlist_comments
                (comment_id, tenant_id, shortlist_entry_id, author_id, visibility, body,
                 evidence_origin, created_at)
                VALUES (:id, :tenant, :entry, :author, :visibility, :body, :origin, :now)"""),
                {
                    "id": uuid4(),
                    "tenant": tenant,
                    "entry": target_entry,
                    "author": private_author,
                    "visibility": visibility,
                    "body": body,
                    "origin": origin,
                    "now": now,
                },
            )
        for summary, visibility, origin in (
            ("team observation", "TEAM", "synthetic_automated_test"),
            ("private former-assignee observation", "OWNER_ONLY", "human_entered_local"),
        ):
            connection.execute(
                text("""INSERT INTO scout_observations
                (observation_id, tenant_id, version, previous_version, shortlist_entry_id,
                 author_id, visibility, dimensions, overall_confidence, evidence_references,
                 summary, disagreement, disagreement_reason, recommended_next_action,
                 evidence_origin, created_at)
                VALUES (:id, :tenant, 1, NULL, :entry, :author, :visibility, :dimensions,
                 0.5, '[]', :summary, 0, NULL, 'synthetic next action', :origin, :now)"""),
                {
                    "id": uuid4(),
                    "tenant": tenant,
                    "entry": target_entry,
                    "author": private_author,
                    "visibility": visibility,
                    "dimensions": '[{"dimension":"role_execution","rating":3}]',
                    "summary": summary,
                    "origin": origin,
                    "now": now,
                },
            )

    exporter = LocalEvidenceExporter(storage)
    former_principal = R1Principal(
        former_assignee, tenant, frozenset({LocalRole.ANALYST, LocalRole.SCOUT}), uuid4()
    )
    current_principal = R1Principal(
        current_assignee, tenant, frozenset({LocalRole.ANALYST, LocalRole.SCOUT}), uuid4()
    )
    author_principal = R1Principal(
        private_author, tenant, frozenset({LocalRole.ANALYST, LocalRole.APPROVER}), uuid4()
    )
    with engine.begin() as connection:
        former = exporter.read(
            connection,
            principal=former_principal,
            evidence_pack_id=_export(
                exporter,
                connection,
                former_principal,
                brief,
                retrieval,
                shortlist,
                uuid4(),
            ).evidence_pack_id,
        )
        current = exporter.read(
            connection,
            principal=current_principal,
            evidence_pack_id=_export(
                exporter,
                connection,
                current_principal,
                brief,
                retrieval,
                shortlist,
                uuid4(),
            ).evidence_pack_id,
        )
        author = exporter.read(
            connection,
            principal=author_principal,
            evidence_pack_id=_export(
                exporter,
                connection,
                author_principal,
                brief,
                retrieval,
                shortlist,
                uuid4(),
            ).evidence_pack_id,
        )
    assert "private former-assignee" not in str(former)
    assert former["workflow_action_origins"] == ["synthetic_automated_test"]
    assert "team record" in str(former)
    assert "private former-assignee secret" in str(current)
    assert "private former-assignee observation" in str(current)
    assert current["workflow_action_origins"] == ["human_entered_local", "synthetic_automated_test"]
    assert "private former-assignee secret" in str(author)
    assert author["workflow_action_origins"] == ["human_entered_local", "synthetic_automated_test"]


def test_disabled_or_analyst_only_latest_assignments_grant_no_private_scope(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    analyst_only, disabled_scout, private_author = uuid4(), uuid4(), uuid4()
    entries = (
        (uuid4(), analyst_only, "analyst-only private"),
        (uuid4(), disabled_scout, "disabled private"),
    )
    now = "2026-08-04T00:00:00+00:00"
    with engine.begin() as connection:
        for actor, enabled, role in ((analyst_only, 1, "analyst"), (disabled_scout, 0, "scout")):
            connection.execute(
                text(
                    "INSERT INTO local_accounts VALUES (:actor, :tenant, :name, :enabled, :now, :disabled_at)"
                ),
                {
                    "actor": actor,
                    "tenant": tenant,
                    "name": "Synthetic assignment actor",
                    "enabled": enabled,
                    "now": now,
                    "disabled_at": None if enabled else now,
                },
            )
            connection.execute(
                text("INSERT INTO local_account_roles VALUES (:actor, :role, :now, :owner)"),
                {"actor": actor, "role": role, "now": now, "owner": analyst},
            )
        connection.execute(
            text(
                "INSERT INTO local_accounts VALUES (:actor, :tenant, 'Synthetic private author', 1, :now, NULL)"
            ),
            {"actor": private_author, "tenant": tenant, "now": now},
        )
        connection.execute(
            text("INSERT INTO local_account_roles VALUES (:actor, 'analyst', :now, :owner)"),
            {"actor": private_author, "now": now, "owner": analyst},
        )
        for entry, assigned, label in entries:
            connection.execute(
                text(
                    "INSERT INTO shortlist_entry_workflows VALUES (:entry, :tenant, :shortlist, :player, 1, 1, :now, :now)"
                ),
                {
                    "entry": entry,
                    "tenant": tenant,
                    "shortlist": shortlist,
                    "player": uuid4(),
                    "now": now,
                },
            )
            connection.execute(
                text("""INSERT INTO shortlist_entry_revisions
                (shortlist_entry_id, tenant_id, shortlist_id, revision, previous_revision,
                role_brief_id, role_brief_version, player_id, state, owner_id, assigned_scout_id,
                retrieval_link_id, rationale, transition_reason, changed_by, created_at)
                VALUES (:entry, :tenant, :shortlist, 1, NULL, :brief, 1, :player, 'scout',
                :owner, :assigned, :retrieval, 'synthetic rationale', 'synthetic assignment',
                :owner, :now)"""),
                {
                    "entry": entry,
                    "tenant": tenant,
                    "shortlist": shortlist,
                    "brief": brief,
                    "player": uuid4(),
                    "owner": analyst,
                    "assigned": assigned,
                    "retrieval": retrieval,
                    "now": now,
                },
            )
            connection.execute(
                text("""INSERT INTO shortlist_comments
                (comment_id, tenant_id, shortlist_entry_id, author_id, visibility, body, evidence_origin, created_at)
                VALUES (:id, :tenant, :entry, :author, 'OWNER_ONLY', :body, 'human_entered_local', :now)"""),
                {
                    "id": uuid4(),
                    "tenant": tenant,
                    "entry": entry,
                    "author": private_author,
                    "body": label,
                    "now": now,
                },
            )
            connection.execute(
                text("""INSERT INTO scout_observations
                (observation_id, tenant_id, version, previous_version, shortlist_entry_id, author_id,
                visibility, dimensions, overall_confidence, evidence_references, summary, disagreement,
                disagreement_reason, recommended_next_action, evidence_origin, created_at)
                VALUES (:id, :tenant, 1, NULL, :entry, :author, 'OWNER_ONLY', :dimensions, 0.5,
                '[]', :summary, 0, NULL, 'synthetic next action', 'human_entered_local', :now)"""),
                {
                    "id": uuid4(),
                    "tenant": tenant,
                    "entry": entry,
                    "author": private_author,
                    "dimensions": '[{"dimension":"role_execution","rating":3}]',
                    "summary": f"{label} observation",
                    "now": now,
                },
            )
    exporter = LocalEvidenceExporter(storage)
    with engine.begin() as connection:
        pack = _export(
            exporter,
            connection,
            _principal(analyst, tenant, LocalRole.ANALYST),
            brief,
            retrieval,
            shortlist,
            uuid4(),
        )
        payload = exporter.read(
            connection,
            principal=_principal(analyst, tenant, LocalRole.ANALYST),
            evidence_pack_id=pack.evidence_pack_id,
        )
    assert "analyst-only private" not in str(payload)
    assert "disabled private" not in str(payload)
    assert payload["workflow_action_origins"] == []


def test_export_policy_drift_fails_closed(tmp_path: Path) -> None:
    storage = GuardedStorage({"evidence_packs": tmp_path / "packs"})
    drifted = tmp_path / "w08-export.yaml"
    drifted.write_text(
        "schema_version: 1\npolicy_id: w08-local-export-v1\ndefault: allow\n",
        encoding="utf-8",
    )
    with pytest.raises(EvidenceExportDenied):
        LocalEvidenceExporter(storage, export_policy_path=drifted)


def test_retained_custom_policy_path_is_revalidated_on_every_export(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
    tmp_path: Path,
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    from scouting.workflow.evidence_export import _EXPORT_POLICY_PATH

    retained = tmp_path / "retained-export-policy.yaml"
    retained.write_text(_EXPORT_POLICY_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    exporter = LocalEvidenceExporter(storage, export_policy_path=retained)
    retained.write_text("schema_version: 1\npolicy_id: drifted\n", encoding="utf-8")
    with engine.begin() as connection, pytest.raises(EvidenceExportDenied):
        _export(
            exporter,
            connection,
            _principal(analyst, tenant, LocalRole.ANALYST),
            brief,
            retrieval,
            shortlist,
            uuid4(),
        )

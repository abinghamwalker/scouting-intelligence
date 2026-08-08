"""Synthetic automated integration tests for W08 local evidence-pack mechanics."""
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from scouting.audit import AuditIntegrityError, AuditLedger
from scouting.policy import LocalRole, R1Principal
from scouting.storage import GuardedStorage, StorageError
from scouting.storage.embedded import create_embedded_engine
from scouting.workflow import EvidenceExportIntegrityError, LocalEvidenceExporter


@pytest.fixture
def export_runtime(
    tmp_path: Path,
) -> tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID]:
    engine = create_embedded_engine(tmp_path / "export.sqlite3", allowed_root=tmp_path)
    storage = GuardedStorage({"evidence_packs": tmp_path / "evidence-packs"})
    tenant, analyst, scout, brief, retrieval, shortlist = (uuid4() for _ in range(6))
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tenants (tenant_id, slug, display_name, created_at) VALUES (:id, :slug, 'Synthetic', :now)"
            ),
            {"id": tenant, "slug": f"synthetic-{tenant.hex}", "now": "2026-08-04T00:00:00+00:00"},
        )
        for actor, name in ((analyst, "Synthetic Analyst"), (scout, "Synthetic Scout")):
            connection.execute(
                text(
                    "INSERT INTO local_accounts (actor_id, tenant_id, display_name, enabled, created_at) VALUES (:id, :tenant, :name, 1, :now)"
                ),
                {"id": actor, "tenant": tenant, "name": name, "now": "2026-08-04T00:00:00+00:00"},
            )
        for actor, role in ((analyst, "analyst"), (scout, "scout")):
            connection.execute(
                text(
                    "INSERT INTO local_account_roles (actor_id, role, assigned_at, assigned_by) VALUES (:id, :role, :now, :by)"
                ),
                {"id": actor, "role": role, "now": "2026-08-04T00:00:00+00:00", "by": analyst},
            )
        connection.execute(
            text("""INSERT INTO role_brief_workflows (role_brief_id, tenant_id, owner_id, visibility, lock_version, latest_version, created_at, updated_at)
            VALUES (:id, :tenant, :owner, 'TEAM', 1, 1, :now, :now)"""),
            {"id": brief, "tenant": tenant, "owner": analyst, "now": "2026-08-04T00:00:00+00:00"},
        )
        connection.execute(
            text("""INSERT INTO role_brief_revisions (role_brief_id, tenant_id, version, previous_version, trace_id, owner_id, created_by, visibility,
            title, template_id, taxonomy_version, status, responsibilities, hard_constraints, preferences, exemplar_player_ids, transition_reason,
            submitted_at, decided_at, decided_by, created_at)
            VALUES (:id, :tenant, 1, NULL, :trace, :owner, :owner, 'TEAM', 'Synthetic Role', 'template-v1', 'taxonomy-v1', 'approved',
            '[\"synthetic responsibility\"]', '[]', '[]', '[]', 'synthetic approval', :now, :now, :owner, :now)"""),
            {
                "id": brief,
                "tenant": tenant,
                "trace": uuid4(),
                "owner": analyst,
                "now": "2026-08-04T00:00:00+00:00",
            },
        )
        connection.execute(
            text("""INSERT INTO replayable_retrieval_links (retrieval_link_id, tenant_id, role_brief_id, role_brief_version, retrieval_request_id,
            retrieval_result_id, retrieval_run_id, query_player_id, exemplar_player_ids, model_version, index_version, data_version, taxonomy_version, result_digest,
            lineage_digest, claim_boundary, evidence_class, applicability, limitations, created_by, created_at)
            VALUES (:id, :tenant, :brief, 1, :request, :result, :run, :player, '[]', 'model-v1', 'index-v1', 'data-v1', 'taxonomy-v1', :digest,
            :lineage, 'resemblance_only', 'synthetic_development_only', 'LIMITED', '[\"synthetic mechanics only\"]', :owner, :now)"""),
            {
                "id": retrieval,
                "tenant": tenant,
                "brief": brief,
                "request": uuid4(),
                "result": uuid4(),
                "run": uuid4(),
                "player": uuid4(),
                "digest": "a" * 64,
                "lineage": "b" * 64,
                "owner": analyst,
                "now": "2026-08-04T00:00:00+00:00",
            },
        )
        connection.execute(
            text("""INSERT INTO workflow_shortlists (shortlist_id, tenant_id, role_brief_id, role_brief_version, owner_id, visibility, title,
            lock_version, created_at, updated_at) VALUES (:id, :tenant, :brief, 1, :owner, 'TEAM', 'Synthetic shortlist', 1, :now, :now)"""),
            {
                "id": shortlist,
                "tenant": tenant,
                "brief": brief,
                "owner": analyst,
                "now": "2026-08-04T00:00:00+00:00",
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
    return exporter.export(  # type: ignore[union-attr]
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


def test_export_is_canonical_idempotent_and_records_hash_chained_audit(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    exporter = LocalEvidenceExporter(storage)
    pack = uuid4()
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    with engine.begin() as connection:
        first = _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        second = _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        assert first == second
        loaded = exporter.read(connection, principal=principal, evidence_pack_id=pack)
        assert loaded["workflow_action_origins"] == []
        assert loaded["claim_boundary"] == "resemblance_only"
        assert loaded["model_evidence"] == "synthetic_development_only"
        assert loaded["applicability"] == "LIMITED"
        assert "audit_receipt" in loaded
        assert connection.execute(text("SELECT count(*) FROM evidence_exports")).scalar_one() == 1
        AuditLedger().verify(connection, tenant_id=tenant)


def test_export_decodes_exemplar_mode_retrieval_inputs(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, _, brief, _, shortlist = export_runtime
    exporter = LocalEvidenceExporter(storage)
    retrieval, first_exemplar, second_exemplar = uuid4(), uuid4(), uuid4()
    with engine.begin() as connection:
        connection.execute(
            text("""INSERT INTO replayable_retrieval_links (retrieval_link_id, tenant_id, role_brief_id, role_brief_version, retrieval_request_id, retrieval_result_id, retrieval_run_id, query_player_id, exemplar_player_ids, model_version, index_version, data_version, taxonomy_version, result_digest, lineage_digest, claim_boundary, evidence_class, applicability, limitations, created_by, created_at)
            VALUES (:id, :tenant, :brief, 1, :request, :result, :run, NULL, :exemplars, 'model-v1', 'index-v1', 'data-v1', 'taxonomy-v1', :digest, :lineage, 'resemblance_only', 'synthetic_development_only', 'LIMITED', '[\"synthetic mechanics only\"]', :owner, :now)"""),
            {
                "id": retrieval,
                "tenant": tenant,
                "brief": brief,
                "request": uuid4(),
                "result": uuid4(),
                "run": uuid4(),
                "exemplars": f'["{first_exemplar}","{second_exemplar}"]',
                "digest": "a" * 64,
                "lineage": "b" * 64,
                "owner": analyst,
                "now": "2026-08-04T00:00:00+00:00",
            },
        )
        pack = uuid4()
        _export(
            exporter,
            connection,
            _principal(analyst, tenant, LocalRole.ANALYST),
            brief,
            retrieval,
            shortlist,
            pack,
        )
        payload = exporter.read(
            connection,
            principal=_principal(analyst, tenant, LocalRole.ANALYST),
            evidence_pack_id=pack,
        )
    link = payload["underlying_values"]["retrieval_link"]  # type: ignore[index]
    assert link["query_player_id"] is None
    assert link["exemplar_player_ids"] == [str(first_exemplar), str(second_exemplar)]


def test_export_rollback_keeps_database_empty_when_storage_or_audit_fails(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    exporter = LocalEvidenceExporter(storage)

    def unavailable(*args: object, **kwargs: object) -> object:
        raise StorageError("synthetic storage fault")

    monkeypatch.setattr(storage, "write_bytes", unavailable)
    with pytest.raises(EvidenceExportIntegrityError):
        with engine.begin() as connection:
            _export(exporter, connection, principal, brief, retrieval, shortlist, uuid4())
    with engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM evidence_exports")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 0

    class FailingLedger(AuditLedger):
        def append(self, connection: object, event: object) -> object:
            raise AuditIntegrityError("synthetic audit fault")

    failed_audit = LocalEvidenceExporter(storage, audit_ledger=FailingLedger())
    with pytest.raises(EvidenceExportIntegrityError):
        with engine.begin() as connection:
            _export(failed_audit, connection, principal, brief, retrieval, shortlist, uuid4())
    with engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM evidence_exports")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 0


def test_malformed_ledger_blocks_export_read_and_revoke_without_new_state(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    exporter = LocalEvidenceExporter(storage)
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    with engine.begin() as connection:
        existing = _export(exporter, connection, principal, brief, retrieval, shortlist, uuid4())
        connection.execute(
            text("""INSERT INTO audit_events (
            audit_event_id, tenant_id, trace_id, request_id, actor_id, action, target_type,
            target_id, occurred_at, after_digest, export_scope
            ) VALUES (:id, :tenant, :trace, :request, :actor, 'create', 'synthetic.orphan',
            :target, :occurred, :digest, '[]')"""),
            {
                "id": uuid4(),
                "tenant": tenant,
                "trace": uuid4(),
                "request": uuid4(),
                "actor": analyst,
                "target": uuid4(),
                "occurred": "2026-08-04T00:00:00+00:00",
                "digest": "a" * 64,
            },
        )
        before_bytes = sorted(
            path.name for path in storage._roots["evidence_packs"].rglob("*.json")
        )
        with pytest.raises(EvidenceExportIntegrityError, match="audit ledger rejected"):
            _export(exporter, connection, principal, brief, retrieval, shortlist, uuid4())
        with pytest.raises(EvidenceExportIntegrityError, match="audit ledger rejected"):
            exporter.read(
                connection, principal=principal, evidence_pack_id=existing.evidence_pack_id
            )
        with pytest.raises(EvidenceExportIntegrityError, match="audit ledger rejected"):
            exporter.revoke(
                connection,
                principal=principal,
                evidence_pack_id=existing.evidence_pack_id,
                reason="synthetic revoke",
                trace_id=uuid4(),
                request_id=uuid4(),
            )
        assert connection.execute(text("SELECT count(*) FROM evidence_exports")).scalar_one() == 1
        assert (
            connection.execute(
                text("SELECT count(*) FROM evidence_export_revocations")
            ).scalar_one()
            == 0
        )
        assert connection.execute(text("SELECT count(*) FROM audit_receipts")).scalar_one() == 1
        assert (
            sorted(path.name for path in storage._roots["evidence_packs"].rglob("*.json"))
            == before_bytes
        )


def test_caught_failure_uses_savepoint_and_identical_retry_succeeds_once(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    exporter = LocalEvidenceExporter(storage)
    pack = uuid4()

    def unavailable(*args: object, **kwargs: object) -> object:
        raise StorageError("synthetic storage fault")

    with engine.begin() as connection, monkeypatch.context() as patch:
        patch.setattr(storage, "write_bytes", unavailable)
        with pytest.raises(EvidenceExportIntegrityError):
            _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        assert connection.execute(text("SELECT count(*) FROM evidence_exports")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 0
    with engine.begin() as connection:
        succeeded = _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        assert succeeded.evidence_pack_id == pack
        assert connection.execute(text("SELECT count(*) FROM evidence_exports")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 1

    class FailingLedger(AuditLedger):
        def append(self, connection: object, event: object) -> object:
            raise AuditIntegrityError("synthetic audit fault")

    failing = LocalEvidenceExporter(storage, audit_ledger=FailingLedger())
    with engine.begin() as connection:
        with pytest.raises(EvidenceExportIntegrityError):
            failing.revoke(
                connection,
                principal=principal,
                evidence_pack_id=pack,
                reason="synthetic failure",
                trace_id=uuid4(),
                request_id=uuid4(),
            )
        assert (
            connection.execute(
                text("SELECT count(*) FROM evidence_export_revocations")
            ).scalar_one()
            == 0
        )
        assert connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 1


def test_export_excludes_private_observation_not_owned_by_exporter(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, scout, brief, retrieval, shortlist = export_runtime
    entry, observation = uuid4(), uuid4()
    with engine.begin() as connection:
        connection.execute(
            text("""INSERT INTO shortlist_entry_workflows (shortlist_entry_id, tenant_id, shortlist_id, player_id, lock_version, latest_revision, created_at, updated_at)
        VALUES (:id, :tenant, :shortlist, :player, 1, 1, :now, :now)"""),
            {
                "id": entry,
                "tenant": tenant,
                "shortlist": shortlist,
                "player": uuid4(),
                "now": "2026-08-04T00:00:00+00:00",
            },
        )
        connection.execute(
            text("""INSERT INTO scout_observations (observation_id, tenant_id, version, previous_version, shortlist_entry_id, author_id, visibility, dimensions, overall_confidence, evidence_references, summary, disagreement, disagreement_reason, recommended_next_action, evidence_origin, created_at)
        VALUES (:id, :tenant, 1, NULL, :entry, :author, 'OWNER_ONLY', :dimensions, 0.5, '[]', 'Private synthetic note', 0, NULL, 'retain for review', 'synthetic_automated_test', :now)"""),
            {
                "id": observation,
                "tenant": tenant,
                "entry": entry,
                "author": scout,
                "dimensions": '[{"dimension":"role_execution","rating":3}]',
                "now": "2026-08-04T00:00:00+00:00",
            },
        )
    exporter = LocalEvidenceExporter(storage)
    with engine.begin() as connection:
        result = _export(
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
            evidence_pack_id=result.evidence_pack_id,
        )
    assert payload["underlying_values"]["scout_observations_visible_to_exporter"] == []  # type: ignore[index]


def test_export_retains_all_visible_history_and_exact_action_origins(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
) -> None:
    engine, storage, tenant, analyst, scout, brief, retrieval, shortlist = export_runtime
    entry, team_observation, private_observation = uuid4(), uuid4(), uuid4()
    now = "2026-08-04T00:00:00+00:00"
    with engine.begin() as connection:
        connection.execute(
            text("""INSERT INTO shortlist_entry_workflows VALUES
            (:entry, :tenant, :shortlist, :player, 2, 2, :now, :now)"""),
            {
                "entry": entry,
                "tenant": tenant,
                "shortlist": shortlist,
                "player": uuid4(),
                "now": now,
            },
        )
        for revision, state, previous, assigned in (
            (1, "longlist", None, None),
            (2, "scout", 1, scout),
        ):
            connection.execute(
                text("""INSERT INTO shortlist_entry_revisions
                (shortlist_entry_id, tenant_id, shortlist_id, revision, previous_revision,
                role_brief_id, role_brief_version, player_id, state, owner_id, assigned_scout_id,
                retrieval_link_id, rationale, transition_reason, changed_by, created_at)
                VALUES (:entry, :tenant, :shortlist, :revision, :previous, :brief, 1, :player,
                :state, :analyst, :assigned, :retrieval, 'synthetic rationale',
                'synthetic transition', :analyst, :now)"""),
                {
                    "entry": entry,
                    "tenant": tenant,
                    "shortlist": shortlist,
                    "revision": revision,
                    "previous": previous,
                    "brief": brief,
                    "player": uuid4(),
                    "state": state,
                    "analyst": analyst,
                    "assigned": assigned,
                    "retrieval": retrieval,
                    "now": now,
                },
            )
        for comment_id, author, visibility, body, origin, created_at in (
            (uuid4(), scout, "TEAM", "visible automated comment", "synthetic_automated_test", now),
            (
                uuid4(),
                analyst,
                "OWNER_ONLY",
                "visible human-entered comment",
                "human_entered_local",
                "2026-08-04T00:01:00+00:00",
            ),
            (
                uuid4(),
                scout,
                "OWNER_ONLY",
                "private comment must not leak",
                "human_entered_local",
                "2026-08-04T00:02:00+00:00",
            ),
        ):
            connection.execute(
                text("""INSERT INTO shortlist_comments
                (comment_id, tenant_id, shortlist_entry_id, author_id, visibility, body,
                evidence_origin, created_at)
                VALUES (:id, :tenant, :entry, :author, :visibility, :body, :origin, :now)"""),
                {
                    "id": comment_id,
                    "tenant": tenant,
                    "entry": entry,
                    "author": author,
                    "visibility": visibility,
                    "body": body,
                    "origin": origin,
                    "now": created_at,
                },
            )
        for observation_id, version, previous, visibility, summary, origin in (
            (team_observation, 1, None, "TEAM", "visible version one", "synthetic_automated_test"),
            (team_observation, 2, 1, "TEAM", "visible version two", "human_entered_local"),
            (
                private_observation,
                1,
                None,
                "OWNER_ONLY",
                "private observation must not leak",
                "human_entered_local",
            ),
        ):
            connection.execute(
                text("""INSERT INTO scout_observations
                (observation_id, tenant_id, version, previous_version, shortlist_entry_id,
                author_id, visibility, dimensions, overall_confidence, evidence_references,
                summary, disagreement, disagreement_reason, recommended_next_action,
                evidence_origin, created_at)
                VALUES (:id, :tenant, :version, :previous, :entry, :scout, :visibility,
                :dimensions, 0.5, '[]', :summary, 0, NULL, 'synthetic next action', :origin, :now)"""),
                {
                    "id": observation_id,
                    "tenant": tenant,
                    "version": version,
                    "previous": previous,
                    "entry": entry,
                    "scout": scout,
                    "visibility": visibility,
                    "dimensions": '[{"dimension":"role_execution","rating":3}]',
                    "summary": summary,
                    "origin": origin,
                    "now": now,
                },
            )
    exporter = LocalEvidenceExporter(storage)
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    with engine.begin() as connection:
        pack = uuid4()
        result = _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        assert result == _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        payload = exporter.read(
            connection, principal=principal, evidence_pack_id=result.evidence_pack_id
        )
    underlying = payload["underlying_values"]  # type: ignore[assignment]
    assert [row["revision"] for row in underlying["shortlist_entry_revisions"]] == [1, 2]  # type: ignore[index]
    assert [row["body"] for row in underlying["shortlist_comments_visible_to_exporter"]] == [  # type: ignore[index]
        "visible automated comment",
        "visible human-entered comment",
    ]
    assert [row["version"] for row in underlying["scout_observations_visible_to_exporter"]] == [
        1,
        2,
    ]  # type: ignore[index]
    assert payload["workflow_action_origins"] == ["human_entered_local", "synthetic_automated_test"]
    assert payload["claim_boundary"] == "resemblance_only"
    assert payload["model_evidence"] == "synthetic_development_only"
    assert payload["applicability"] == "LIMITED"
    assert "private comment must not leak" not in str(payload)
    assert "private observation must not leak" not in str(payload)


@pytest.mark.parametrize(
    "fault",
    (
        "missing",
        "unreadable_utf8",
        "malformed_json",
        "noncanonical",
        "classification",
        "claim_boundary",
        "digest_mismatch",
    ),
)
def test_persisted_pack_faults_block_read_idempotency_and_revoke_atomically(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
    fault: str,
) -> None:
    """Synthetic core witness for every persisted-byte verification boundary."""
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    exporter = LocalEvidenceExporter(storage)
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    pack = uuid4()
    with engine.begin() as connection:
        result = _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
    path = storage._roots["evidence_packs"] / result.relative_path
    original = path.read_bytes()
    replacement: bytes | None = None
    if fault == "missing":
        path.unlink()
    elif fault == "unreadable_utf8":
        replacement = b"\xff"
    elif fault == "malformed_json":
        replacement = b"{"
    elif fault == "noncanonical":
        replacement = b" { }"
    elif fault in {"classification", "claim_boundary"}:
        modified = json.loads(original.decode("utf-8"))
        modified["classification" if fault == "classification" else "claim_boundary"] = (
            "not-w08-local" if fault == "classification" else "not-resemblance"
        )
        replacement = json.dumps(
            modified, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    else:
        path.write_bytes(original + b"x")
    if replacement is not None:
        path.write_bytes(replacement)
        with engine.begin() as connection:
            # This isolated adversarial database deliberately removes only the
            # append-only metadata guard.  It proves byte verification remains
            # fail-closed even if an attacker can forge a matching stored digest.
            connection.execute(text("DROP TRIGGER evidence_exports_reject_update"))
            connection.execute(
                text("UPDATE evidence_exports SET sha256=:digest WHERE evidence_pack_id=:pack"),
                {"digest": hashlib.sha256(replacement).hexdigest(), "pack": pack},
            )
    with engine.begin() as connection:
        baseline = tuple(
            int(connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one())
            for table in (
                "evidence_exports",
                "evidence_export_revocations",
                "audit_events",
                "audit_receipts",
            )
        )
        with pytest.raises(EvidenceExportIntegrityError):
            exporter.read(connection, principal=principal, evidence_pack_id=pack)
        with pytest.raises(EvidenceExportIntegrityError):
            _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        with pytest.raises(EvidenceExportIntegrityError):
            exporter.revoke(
                connection,
                principal=principal,
                evidence_pack_id=pack,
                reason="synthetic integrity probe",
                trace_id=uuid4(),
                request_id=uuid4(),
            )
        assert baseline == tuple(
            int(connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one())
            for table in (
                "evidence_exports",
                "evidence_export_revocations",
                "audit_events",
                "audit_receipts",
            )
        )


def test_unreadable_pack_removal_of_fault_allows_one_verified_retry(
    export_runtime: tuple[Engine, GuardedStorage, UUID, UUID, UUID, UUID, UUID, UUID],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, storage, tenant, analyst, _, brief, retrieval, shortlist = export_runtime
    exporter = LocalEvidenceExporter(storage)
    principal = _principal(analyst, tenant, LocalRole.ANALYST)
    pack = uuid4()
    with engine.begin() as connection:
        _export(exporter, connection, principal, brief, retrieval, shortlist, pack)
        baseline = int(
            connection.execute(
                text("SELECT count(*) FROM evidence_export_revocations")
            ).scalar_one()
        )
        with monkeypatch.context() as patch:
            patch.setattr(
                storage,
                "read_bytes",
                lambda *args, **kwargs: (_ for _ in ()).throw(OSError("synthetic unreadable")),
            )
            with pytest.raises(EvidenceExportIntegrityError):
                exporter.revoke(
                    connection,
                    principal=principal,
                    evidence_pack_id=pack,
                    reason="synthetic integrity probe",
                    trace_id=uuid4(),
                    request_id=uuid4(),
                )
        assert (
            connection.execute(
                text("SELECT count(*) FROM evidence_export_revocations")
            ).scalar_one()
            == baseline
        )
        exporter.revoke(
            connection,
            principal=principal,
            evidence_pack_id=pack,
            reason="synthetic verified retry",
            trace_id=uuid4(),
            request_id=uuid4(),
        )
        assert (
            connection.execute(
                text("SELECT count(*) FROM evidence_export_revocations")
            ).scalar_one()
            == baseline + 1
        )

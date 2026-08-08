BEGIN IMMEDIATE;

CREATE TABLE local_accounts (
    actor_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    created_at TEXT NOT NULL,
    disabled_at TEXT,
    UNIQUE (tenant_id, actor_id),
    CHECK ((enabled = 1 AND disabled_at IS NULL) OR (enabled = 0 AND disabled_at IS NOT NULL))
) STRICT;

CREATE TABLE local_account_roles (
    actor_id TEXT NOT NULL REFERENCES local_accounts (actor_id),
    role TEXT NOT NULL CHECK (role IN ('analyst', 'scout', 'approver', 'admin')),
    assigned_at TEXT NOT NULL,
    assigned_by TEXT NOT NULL REFERENCES local_accounts (actor_id),
    PRIMARY KEY (actor_id, role)
) STRICT;

CREATE TABLE local_password_credentials (
    actor_id TEXT PRIMARY KEY REFERENCES local_accounts (actor_id),
    salt_hex TEXT NOT NULL CHECK (
        length(salt_hex) = 32 AND salt_hex NOT GLOB '*[^0-9a-f]*'
    ),
    password_digest TEXT NOT NULL CHECK (
        length(password_digest) = 64 AND password_digest NOT GLOB '*[^0-9a-f]*'
    ),
    scrypt_n INTEGER NOT NULL CHECK (scrypt_n >= 16384),
    scrypt_r INTEGER NOT NULL CHECK (scrypt_r >= 8),
    scrypt_p INTEGER NOT NULL CHECK (scrypt_p >= 1),
    created_at TEXT NOT NULL
) STRICT;

CREATE TABLE local_sessions (
    session_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    token_digest TEXT NOT NULL UNIQUE CHECK (
        length(token_digest) = 64 AND token_digest NOT GLOB '*[^0-9a-f]*'
    ),
    csrf_digest TEXT NOT NULL CHECK (
        length(csrf_digest) = 64 AND csrf_digest NOT GLOB '*[^0-9a-f]*'
    ),
    issued_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    revoked_at TEXT,
    replaced_by_session_id TEXT REFERENCES local_sessions (session_id),
    FOREIGN KEY (tenant_id, actor_id) REFERENCES local_accounts (tenant_id, actor_id),
    CHECK (expires_at > issued_at),
    CHECK (last_seen_at >= issued_at),
    CHECK (revoked_at IS NULL OR revoked_at >= issued_at),
    CHECK (replaced_by_session_id IS NULL OR revoked_at IS NOT NULL)
) STRICT;

CREATE TABLE role_brief_workflows (
    role_brief_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    owner_id TEXT NOT NULL,
    visibility TEXT NOT NULL CHECK (visibility IN ('OWNER_ONLY', 'TEAM')),
    lock_version INTEGER NOT NULL CHECK (lock_version >= 1),
    latest_version INTEGER NOT NULL CHECK (latest_version >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (tenant_id, role_brief_id),
    FOREIGN KEY (tenant_id, owner_id) REFERENCES local_accounts (tenant_id, actor_id),
    CHECK (updated_at >= created_at)
) STRICT;

CREATE TABLE role_brief_revisions (
    role_brief_id TEXT NOT NULL REFERENCES role_brief_workflows (role_brief_id),
    tenant_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 1),
    previous_version INTEGER,
    trace_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_by TEXT NOT NULL,
    visibility TEXT NOT NULL CHECK (visibility IN ('OWNER_ONLY', 'TEAM')),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    template_id TEXT NOT NULL CHECK (length(trim(template_id)) > 0),
    taxonomy_version TEXT NOT NULL CHECK (length(trim(taxonomy_version)) > 0),
    status TEXT NOT NULL CHECK (
        status IN ('draft', 'submitted', 'approved', 'rejected', 'retired')
    ),
    responsibilities TEXT NOT NULL CHECK (
        json_valid(responsibilities) AND json_type(responsibilities) = 'array'
        AND json_array_length(responsibilities) >= 1
    ),
    hard_constraints TEXT NOT NULL CHECK (
        json_valid(hard_constraints) AND json_type(hard_constraints) = 'array'
    ),
    preferences TEXT NOT NULL CHECK (
        json_valid(preferences) AND json_type(preferences) = 'array'
    ),
    exemplar_player_ids TEXT NOT NULL CHECK (
        json_valid(exemplar_player_ids) AND json_type(exemplar_player_ids) = 'array'
    ),
    transition_reason TEXT NOT NULL CHECK (length(trim(transition_reason)) > 0),
    rejection_reason TEXT CHECK (
        rejection_reason IS NULL OR rejection_reason IN (
            'requirements_unclear', 'constraints_unapproved',
            'rights_or_policy_conflict', 'evidence_definition_incomplete', 'other'
        )
    ),
    decision_note TEXT,
    submitted_at TEXT,
    decided_at TEXT,
    decided_by TEXT,
    created_at TEXT NOT NULL,
    PRIMARY KEY (role_brief_id, version),
    UNIQUE (tenant_id, role_brief_id, version),
    FOREIGN KEY (tenant_id, role_brief_id)
        REFERENCES role_brief_workflows (tenant_id, role_brief_id),
    FOREIGN KEY (tenant_id, owner_id) REFERENCES local_accounts (tenant_id, actor_id),
    FOREIGN KEY (tenant_id, created_by) REFERENCES local_accounts (tenant_id, actor_id),
    FOREIGN KEY (tenant_id, decided_by) REFERENCES local_accounts (tenant_id, actor_id),
    CHECK ((version = 1 AND previous_version IS NULL) OR previous_version = version - 1),
    CHECK (status <> 'rejected' OR rejection_reason IS NOT NULL)
) STRICT;

CREATE TABLE replayable_retrieval_links (
    retrieval_link_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    role_brief_id TEXT NOT NULL,
    role_brief_version INTEGER NOT NULL,
    retrieval_request_id TEXT NOT NULL,
    retrieval_result_id TEXT NOT NULL,
    retrieval_run_id TEXT NOT NULL,
    query_player_id TEXT,
    exemplar_player_ids TEXT NOT NULL CHECK (
        json_valid(exemplar_player_ids) AND json_type(exemplar_player_ids) = 'array'
    ),
    model_version TEXT NOT NULL,
    index_version TEXT NOT NULL,
    data_version TEXT NOT NULL,
    taxonomy_version TEXT NOT NULL,
    result_digest TEXT NOT NULL CHECK (
        length(result_digest) = 64 AND result_digest NOT GLOB '*[^0-9a-f]*'
    ),
    lineage_digest TEXT NOT NULL CHECK (
        length(lineage_digest) = 64 AND lineage_digest NOT GLOB '*[^0-9a-f]*'
    ),
    claim_boundary TEXT NOT NULL CHECK (claim_boundary = 'resemblance_only'),
    evidence_class TEXT NOT NULL CHECK (evidence_class = 'synthetic_development_only'),
    applicability TEXT NOT NULL CHECK (applicability = 'LIMITED'),
    limitations TEXT NOT NULL CHECK (
        json_valid(limitations) AND json_type(limitations) = 'array'
        AND json_array_length(limitations) >= 1
    ),
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, retrieval_link_id),
    FOREIGN KEY (tenant_id, role_brief_id, role_brief_version)
        REFERENCES role_brief_revisions (tenant_id, role_brief_id, version),
    FOREIGN KEY (tenant_id, created_by) REFERENCES local_accounts (tenant_id, actor_id)
    ,CHECK (
        (query_player_id IS NOT NULL AND json_array_length(exemplar_player_ids) = 0)
        OR (query_player_id IS NULL AND json_array_length(exemplar_player_ids) >= 1)
    )
) STRICT;

CREATE TABLE workflow_shortlists (
    shortlist_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    role_brief_id TEXT NOT NULL,
    role_brief_version INTEGER NOT NULL,
    owner_id TEXT NOT NULL,
    visibility TEXT NOT NULL CHECK (visibility IN ('OWNER_ONLY', 'TEAM')),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    lock_version INTEGER NOT NULL CHECK (lock_version >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (tenant_id, shortlist_id),
    FOREIGN KEY (tenant_id, role_brief_id, role_brief_version)
        REFERENCES role_brief_revisions (tenant_id, role_brief_id, version),
    FOREIGN KEY (tenant_id, owner_id) REFERENCES local_accounts (tenant_id, actor_id),
    CHECK (updated_at >= created_at)
) STRICT;

CREATE TABLE shortlist_entry_workflows (
    shortlist_entry_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    shortlist_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    lock_version INTEGER NOT NULL CHECK (lock_version >= 1),
    latest_revision INTEGER NOT NULL CHECK (latest_revision >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (tenant_id, shortlist_entry_id),
    UNIQUE (tenant_id, shortlist_id, player_id),
    FOREIGN KEY (tenant_id, shortlist_id)
        REFERENCES workflow_shortlists (tenant_id, shortlist_id),
    CHECK (updated_at >= created_at)
) STRICT;

CREATE TABLE shortlist_entry_revisions (
    shortlist_entry_id TEXT NOT NULL REFERENCES shortlist_entry_workflows (shortlist_entry_id),
    tenant_id TEXT NOT NULL,
    shortlist_id TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK (revision >= 1),
    previous_revision INTEGER,
    role_brief_id TEXT NOT NULL,
    role_brief_version INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK (
        state IN ('longlist', 'monitor', 'scout', 'shortlist', 'hold', 'rejected')
    ),
    owner_id TEXT NOT NULL,
    assigned_scout_id TEXT,
    retrieval_link_id TEXT NOT NULL,
    rationale TEXT NOT NULL CHECK (length(trim(rationale)) > 0),
    transition_reason TEXT NOT NULL CHECK (length(trim(transition_reason)) > 0),
    rejection_reason TEXT CHECK (
        rejection_reason IS NULL OR rejection_reason IN (
            'outside_brief', 'insufficient_evidence', 'identity_unresolved',
            'rights_or_eligibility', 'scout_not_recommended', 'duplicate_candidate', 'other'
        )
    ),
    hold_reason TEXT CHECK (
        hold_reason IS NULL OR hold_reason IN (
            'awaiting_evidence', 'identity_review', 'rights_review',
            'availability_review', 'other'
        )
    ),
    reason_note TEXT,
    next_action TEXT,
    next_action_owner_id TEXT,
    changed_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (shortlist_entry_id, revision),
    UNIQUE (tenant_id, shortlist_entry_id, revision),
    FOREIGN KEY (tenant_id, shortlist_entry_id)
        REFERENCES shortlist_entry_workflows (tenant_id, shortlist_entry_id),
    FOREIGN KEY (tenant_id, shortlist_id)
        REFERENCES workflow_shortlists (tenant_id, shortlist_id),
    FOREIGN KEY (tenant_id, retrieval_link_id)
        REFERENCES replayable_retrieval_links (tenant_id, retrieval_link_id),
    FOREIGN KEY (tenant_id, owner_id) REFERENCES local_accounts (tenant_id, actor_id),
    FOREIGN KEY (tenant_id, assigned_scout_id)
        REFERENCES local_accounts (tenant_id, actor_id),
    FOREIGN KEY (tenant_id, next_action_owner_id)
        REFERENCES local_accounts (tenant_id, actor_id),
    FOREIGN KEY (tenant_id, changed_by) REFERENCES local_accounts (tenant_id, actor_id),
    CHECK ((revision = 1 AND previous_revision IS NULL) OR previous_revision = revision - 1),
    CHECK ((state = 'rejected') = (rejection_reason IS NOT NULL)),
    CHECK ((state = 'hold') = (hold_reason IS NOT NULL)),
    CHECK ((next_action IS NULL) = (next_action_owner_id IS NULL)),
    CHECK (state <> 'scout' OR assigned_scout_id IS NOT NULL)
) STRICT;

CREATE TABLE shortlist_comments (
    comment_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    shortlist_entry_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    visibility TEXT NOT NULL CHECK (visibility IN ('OWNER_ONLY', 'TEAM')),
    body TEXT NOT NULL CHECK (length(trim(body)) > 0),
    evidence_origin TEXT NOT NULL CHECK (
        evidence_origin IN ('synthetic_automated_test', 'human_entered_local')
    ),
    created_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id, shortlist_entry_id)
        REFERENCES shortlist_entry_workflows (tenant_id, shortlist_entry_id),
    FOREIGN KEY (tenant_id, author_id) REFERENCES local_accounts (tenant_id, actor_id)
) STRICT;

CREATE TABLE scout_observations (
    observation_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    version INTEGER NOT NULL CHECK (version >= 1),
    previous_version INTEGER,
    shortlist_entry_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    visibility TEXT NOT NULL CHECK (visibility IN ('OWNER_ONLY', 'TEAM')),
    dimensions TEXT NOT NULL CHECK (
        json_valid(dimensions) AND json_type(dimensions) = 'array'
        AND json_array_length(dimensions) >= 1
    ),
    overall_confidence REAL NOT NULL CHECK (overall_confidence >= 0 AND overall_confidence <= 1),
    evidence_references TEXT NOT NULL CHECK (
        json_valid(evidence_references) AND json_type(evidence_references) = 'array'
    ),
    summary TEXT NOT NULL CHECK (length(trim(summary)) > 0),
    disagreement INTEGER NOT NULL CHECK (disagreement IN (0, 1)),
    disagreement_reason TEXT,
    recommended_next_action TEXT NOT NULL CHECK (length(trim(recommended_next_action)) > 0),
    evidence_origin TEXT NOT NULL CHECK (
        evidence_origin IN ('synthetic_automated_test', 'human_entered_local')
    ),
    created_at TEXT NOT NULL,
    PRIMARY KEY (observation_id, version),
    UNIQUE (tenant_id, observation_id, version),
    FOREIGN KEY (tenant_id, shortlist_entry_id)
        REFERENCES shortlist_entry_workflows (tenant_id, shortlist_entry_id),
    FOREIGN KEY (tenant_id, author_id) REFERENCES local_accounts (tenant_id, actor_id),
    CHECK ((version = 1 AND previous_version IS NULL) OR previous_version = version - 1),
    CHECK ((disagreement = 1) = (disagreement_reason IS NOT NULL))
) STRICT;

CREATE TABLE evidence_exports (
    evidence_pack_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    generated_by TEXT NOT NULL,
    classification TEXT NOT NULL CHECK (
        classification = 'w08_local_confidential_synthetic_workflow'
    ),
    relative_path TEXT NOT NULL UNIQUE CHECK (
        length(trim(relative_path)) > 0 AND instr(relative_path, '..') = 0
    ),
    sha256 TEXT NOT NULL CHECK (
        length(sha256) = 64 AND sha256 NOT GLOB '*[^0-9a-f]*'
    ),
    limitations TEXT NOT NULL CHECK (
        json_valid(limitations) AND json_type(limitations) = 'array'
        AND json_array_length(limitations) >= 1
    ),
    generated_at TEXT NOT NULL,
    UNIQUE (tenant_id, evidence_pack_id),
    FOREIGN KEY (tenant_id, generated_by) REFERENCES local_accounts (tenant_id, actor_id)
) STRICT;

CREATE TABLE evidence_export_revocations (
    revocation_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    evidence_pack_id TEXT NOT NULL,
    revoked_by TEXT NOT NULL,
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    revoked_at TEXT NOT NULL,
    UNIQUE (tenant_id, evidence_pack_id),
    FOREIGN KEY (tenant_id, evidence_pack_id)
        REFERENCES evidence_exports (tenant_id, evidence_pack_id),
    FOREIGN KEY (tenant_id, revoked_by) REFERENCES local_accounts (tenant_id, actor_id)
) STRICT;

CREATE TABLE audit_receipts (
    audit_receipt_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    sequence INTEGER NOT NULL CHECK (sequence >= 1),
    audit_event_id TEXT NOT NULL REFERENCES audit_events (audit_event_id),
    previous_receipt_digest TEXT CHECK (
        previous_receipt_digest IS NULL OR (
            length(previous_receipt_digest) = 64
            AND previous_receipt_digest NOT GLOB '*[^0-9a-f]*'
        )
    ),
    event_digest TEXT NOT NULL CHECK (
        length(event_digest) = 64 AND event_digest NOT GLOB '*[^0-9a-f]*'
    ),
    receipt_digest TEXT NOT NULL UNIQUE CHECK (
        length(receipt_digest) = 64 AND receipt_digest NOT GLOB '*[^0-9a-f]*'
    ),
    recorded_at TEXT NOT NULL,
    UNIQUE (tenant_id, sequence),
    UNIQUE (tenant_id, audit_event_id),
    CHECK ((sequence = 1) = (previous_receipt_digest IS NULL))
) STRICT;

CREATE INDEX ix_local_sessions_actor_expiry
    ON local_sessions (tenant_id, actor_id, expires_at);
CREATE INDEX ix_role_brief_workflows_owner
    ON role_brief_workflows (tenant_id, owner_id, updated_at DESC);
CREATE INDEX ix_workflow_shortlists_owner
    ON workflow_shortlists (tenant_id, owner_id, updated_at DESC);
CREATE INDEX ix_shortlist_entry_workflows_shortlist
    ON shortlist_entry_workflows (tenant_id, shortlist_id, updated_at DESC);
CREATE INDEX ix_scout_observations_entry
    ON scout_observations (tenant_id, shortlist_entry_id, created_at DESC);

CREATE TRIGGER role_brief_revisions_reject_update
BEFORE UPDATE ON role_brief_revisions BEGIN
    SELECT RAISE(ABORT, 'role_brief_revisions are append-only');
END;
CREATE TRIGGER role_brief_revisions_reject_delete
BEFORE DELETE ON role_brief_revisions BEGIN
    SELECT RAISE(ABORT, 'role_brief_revisions are append-only');
END;
CREATE TRIGGER replayable_retrieval_links_reject_update
BEFORE UPDATE ON replayable_retrieval_links BEGIN
    SELECT RAISE(ABORT, 'replayable_retrieval_links are append-only');
END;
CREATE TRIGGER replayable_retrieval_links_reject_delete
BEFORE DELETE ON replayable_retrieval_links BEGIN
    SELECT RAISE(ABORT, 'replayable_retrieval_links are append-only');
END;
CREATE TRIGGER shortlist_entry_revisions_reject_update
BEFORE UPDATE ON shortlist_entry_revisions BEGIN
    SELECT RAISE(ABORT, 'shortlist_entry_revisions are append-only');
END;
CREATE TRIGGER shortlist_entry_revisions_reject_delete
BEFORE DELETE ON shortlist_entry_revisions BEGIN
    SELECT RAISE(ABORT, 'shortlist_entry_revisions are append-only');
END;
CREATE TRIGGER shortlist_comments_reject_update
BEFORE UPDATE ON shortlist_comments BEGIN
    SELECT RAISE(ABORT, 'shortlist_comments are append-only');
END;
CREATE TRIGGER shortlist_comments_reject_delete
BEFORE DELETE ON shortlist_comments BEGIN
    SELECT RAISE(ABORT, 'shortlist_comments are append-only');
END;
CREATE TRIGGER scout_observations_reject_update
BEFORE UPDATE ON scout_observations BEGIN
    SELECT RAISE(ABORT, 'scout_observations are append-only');
END;
CREATE TRIGGER scout_observations_reject_delete
BEFORE DELETE ON scout_observations BEGIN
    SELECT RAISE(ABORT, 'scout_observations are append-only');
END;
CREATE TRIGGER evidence_exports_reject_update
BEFORE UPDATE ON evidence_exports BEGIN
    SELECT RAISE(ABORT, 'evidence_exports are append-only');
END;
CREATE TRIGGER evidence_exports_reject_delete
BEFORE DELETE ON evidence_exports BEGIN
    SELECT RAISE(ABORT, 'evidence_exports are append-only');
END;
CREATE TRIGGER evidence_export_revocations_reject_update
BEFORE UPDATE ON evidence_export_revocations BEGIN
    SELECT RAISE(ABORT, 'evidence_export_revocations are append-only');
END;
CREATE TRIGGER evidence_export_revocations_reject_delete
BEFORE DELETE ON evidence_export_revocations BEGIN
    SELECT RAISE(ABORT, 'evidence_export_revocations are append-only');
END;
CREATE TRIGGER audit_receipts_reject_update
BEFORE UPDATE ON audit_receipts BEGIN
    SELECT RAISE(ABORT, 'audit_receipts are append-only');
END;
CREATE TRIGGER audit_receipts_reject_delete
BEFORE DELETE ON audit_receipts BEGIN
    SELECT RAISE(ABORT, 'audit_receipts are append-only');
END;

INSERT INTO schema_migrations (version, name, applied_at)
VALUES (2, '0002_w08_workflow', '2026-08-04T20:00:00+00:00');

PRAGMA user_version = 2;
COMMIT;

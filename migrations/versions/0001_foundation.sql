BEGIN IMMEDIATE;

CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL
) STRICT;

CREATE TABLE tenants (
    tenant_id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE CHECK (length(trim(slug)) > 0),
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0),
    created_at TEXT NOT NULL
) STRICT;

CREATE TRIGGER tenants_reject_second_identity
BEFORE INSERT ON tenants
FOR EACH ROW
WHEN EXISTS (
    SELECT 1
    FROM tenants
    WHERE tenant_id <> NEW.tenant_id
)
BEGIN
    SELECT RAISE(ABORT, 'embedded runtime is single-tenant');
END;

CREATE TABLE canonical_teams (
    team_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0),
    provenance TEXT NOT NULL CHECK (json_valid(provenance) AND json_type(provenance) = 'object'),
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, team_id),
    CHECK (valid_to IS NULL OR valid_to >= valid_from)
) STRICT;

CREATE TABLE canonical_players (
    player_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0),
    provenance TEXT NOT NULL CHECK (json_valid(provenance) AND json_type(provenance) = 'object'),
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, player_id),
    CHECK (valid_to IS NULL OR valid_to >= valid_from)
) STRICT;

CREATE TABLE competitions (
    competition_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id),
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0),
    country_code TEXT NOT NULL CHECK (
        length(country_code) = 2
        AND country_code = upper(country_code)
    ),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, competition_id)
) STRICT;

CREATE TABLE seasons (
    season_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    competition_id TEXT NOT NULL,
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0),
    valid_from TEXT NOT NULL,
    valid_to TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, season_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    FOREIGN KEY (tenant_id, competition_id)
        REFERENCES competitions (tenant_id, competition_id),
    CHECK (valid_to >= valid_from)
) STRICT;

CREATE TABLE matches (
    match_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    competition_id TEXT NOT NULL,
    season_id TEXT NOT NULL,
    home_team_id TEXT NOT NULL,
    away_team_id TEXT NOT NULL,
    scheduled_at TEXT NOT NULL,
    actual_started_at TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('scheduled', 'in_progress', 'complete', 'cancelled')
    ),
    data_coverage TEXT NOT NULL CHECK (
        json_valid(data_coverage) AND json_type(data_coverage) = 'object'
    ),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, match_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    FOREIGN KEY (tenant_id, competition_id)
        REFERENCES competitions (tenant_id, competition_id),
    FOREIGN KEY (tenant_id, season_id)
        REFERENCES seasons (tenant_id, season_id),
    FOREIGN KEY (tenant_id, home_team_id)
        REFERENCES canonical_teams (tenant_id, team_id),
    FOREIGN KEY (tenant_id, away_team_id)
        REFERENCES canonical_teams (tenant_id, team_id),
    CHECK (home_team_id <> away_team_id)
) STRICT;

CREATE TABLE role_briefs (
    role_brief_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 1),
    trace_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    team_id TEXT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    taxonomy_version TEXT NOT NULL CHECK (length(trim(taxonomy_version)) > 0),
    status TEXT NOT NULL CHECK (status IN ('draft', 'approved', 'archived')),
    responsibilities TEXT NOT NULL CHECK (
        json_valid(responsibilities)
        AND json_type(responsibilities) = 'array'
        AND json_array_length(responsibilities) >= 1
    ),
    hard_constraints TEXT NOT NULL DEFAULT '[]' CHECK (
        json_valid(hard_constraints) AND json_type(hard_constraints) = 'array'
    ),
    preferences TEXT NOT NULL DEFAULT '[]' CHECK (
        json_valid(preferences) AND json_type(preferences) = 'array'
    ),
    exemplar_player_ids TEXT NOT NULL DEFAULT '[]' CHECK (
        json_valid(exemplar_player_ids) AND json_type(exemplar_player_ids) = 'array'
    ),
    created_at TEXT NOT NULL,
    approved_at TEXT,
    PRIMARY KEY (role_brief_id, version),
    UNIQUE (tenant_id, role_brief_id, version),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    FOREIGN KEY (tenant_id, team_id)
        REFERENCES canonical_teams (tenant_id, team_id),
    CHECK (
        (
            status = 'approved'
            AND approved_at IS NOT NULL
            AND approved_at >= created_at
        )
        OR (status <> 'approved' AND approved_at IS NULL)
    )
) STRICT;

CREATE TABLE retrieval_runs (
    retrieval_run_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    retrieval_request_id TEXT NOT NULL UNIQUE,
    retrieval_result_id TEXT UNIQUE,
    role_brief_id TEXT NOT NULL,
    role_brief_version INTEGER NOT NULL CHECK (role_brief_version >= 1),
    trace_id TEXT NOT NULL,
    feature_cutoff_ts TEXT NOT NULL,
    generated_at TEXT,
    model_version TEXT NOT NULL CHECK (length(trim(model_version)) > 0),
    index_version TEXT NOT NULL CHECK (length(trim(index_version)) > 0),
    dependency_lineage_hash TEXT NOT NULL CHECK (
        length(dependency_lineage_hash) = 64
        AND dependency_lineage_hash NOT GLOB '*[^0-9a-f]*'
    ),
    status TEXT NOT NULL CHECK (status IN ('started', 'complete', 'failed')),
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, retrieval_run_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    FOREIGN KEY (tenant_id, role_brief_id, role_brief_version)
        REFERENCES role_briefs (tenant_id, role_brief_id, version),
    CHECK (generated_at IS NULL OR generated_at >= feature_cutoff_ts),
    CHECK (
        (
            status = 'complete'
            AND retrieval_result_id IS NOT NULL
            AND generated_at IS NOT NULL
        )
        OR (status <> 'complete' AND retrieval_result_id IS NULL)
    )
) STRICT;

CREATE TABLE candidate_results (
    candidate_result_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    retrieval_run_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    rank INTEGER NOT NULL CHECK (rank >= 1),
    score REAL NOT NULL CHECK (score >= 0 AND score <= 1),
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    evidence_dimensions TEXT NOT NULL CHECK (
        json_valid(evidence_dimensions)
        AND json_type(evidence_dimensions) = 'object'
    ),
    reason_codes TEXT NOT NULL CHECK (
        json_valid(reason_codes)
        AND json_type(reason_codes) = 'array'
        AND json_array_length(reason_codes) >= 1
    ),
    claim_boundary TEXT NOT NULL DEFAULT 'resemblance_only'
        CHECK (claim_boundary = 'resemblance_only'),
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, retrieval_run_id, player_id),
    UNIQUE (tenant_id, retrieval_run_id, rank),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    FOREIGN KEY (tenant_id, retrieval_run_id)
        REFERENCES retrieval_runs (tenant_id, retrieval_run_id),
    FOREIGN KEY (tenant_id, player_id)
        REFERENCES canonical_players (tenant_id, player_id)
) STRICT;

CREATE TABLE shortlists (
    shortlist_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    role_brief_id TEXT NOT NULL,
    role_brief_version INTEGER NOT NULL,
    owner_id TEXT NOT NULL,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (tenant_id, shortlist_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    FOREIGN KEY (tenant_id, role_brief_id, role_brief_version)
        REFERENCES role_briefs (tenant_id, role_brief_id, version),
    CHECK (updated_at >= created_at)
) STRICT;

CREATE TABLE shortlist_entries (
    shortlist_entry_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    shortlist_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    retrieval_run_id TEXT,
    rank_at_addition INTEGER,
    model_version_at_addition TEXT,
    state TEXT NOT NULL CHECK (
        state IN ('longlist', 'monitor', 'scout', 'shortlist', 'hold', 'rejected')
    ),
    owner_id TEXT NOT NULL,
    rationale TEXT NOT NULL CHECK (length(trim(rationale)) > 0),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (tenant_id, shortlist_entry_id),
    UNIQUE (tenant_id, shortlist_id, player_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    FOREIGN KEY (tenant_id, shortlist_id)
        REFERENCES shortlists (tenant_id, shortlist_id),
    FOREIGN KEY (tenant_id, player_id)
        REFERENCES canonical_players (tenant_id, player_id),
    FOREIGN KEY (tenant_id, retrieval_run_id)
        REFERENCES retrieval_runs (tenant_id, retrieval_run_id),
    CHECK (updated_at >= created_at),
    CHECK (
        (
            retrieval_run_id IS NULL
            AND rank_at_addition IS NULL
            AND model_version_at_addition IS NULL
        )
        OR (
            retrieval_run_id IS NOT NULL
            AND rank_at_addition >= 1
            AND length(trim(model_version_at_addition)) > 0
        )
    )
) STRICT;

CREATE TABLE audit_events (
    audit_event_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (
        action IN ('read', 'create', 'update', 'delete', 'export', 'override')
    ),
    target_type TEXT NOT NULL CHECK (length(trim(target_type)) > 0),
    target_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    before_digest TEXT CHECK (
        before_digest IS NULL
        OR (
            length(before_digest) = 64
            AND before_digest NOT GLOB '*[^0-9a-f]*'
        )
    ),
    after_digest TEXT CHECK (
        after_digest IS NULL
        OR (
            length(after_digest) = 64
            AND after_digest NOT GLOB '*[^0-9a-f]*'
        )
    ),
    reason TEXT,
    export_scope TEXT NOT NULL DEFAULT '[]' CHECK (
        json_valid(export_scope) AND json_type(export_scope) = 'array'
    ),
    UNIQUE (tenant_id, audit_event_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
    CHECK (
        (action = 'create' AND before_digest IS NULL AND after_digest IS NOT NULL)
        OR (
            action IN ('update', 'override')
            AND before_digest IS NOT NULL
            AND after_digest IS NOT NULL
        )
        OR (action = 'delete' AND before_digest IS NOT NULL AND after_digest IS NULL)
        OR action IN ('read', 'export')
    ),
    CHECK (action <> 'export' OR json_array_length(export_scope) >= 1),
    CHECK (action <> 'override' OR length(trim(reason)) > 0)
) STRICT;

CREATE INDEX ix_canonical_players_tenant_name
    ON canonical_players (tenant_id, display_name);
CREATE INDEX ix_canonical_teams_tenant_name
    ON canonical_teams (tenant_id, display_name);
CREATE INDEX ix_matches_tenant_scheduled
    ON matches (tenant_id, scheduled_at DESC);
CREATE INDEX ix_role_briefs_tenant_status
    ON role_briefs (tenant_id, status, created_at DESC);
CREATE INDEX ix_retrieval_runs_tenant_created
    ON retrieval_runs (tenant_id, created_at DESC);
CREATE INDEX ix_shortlist_entries_tenant_state
    ON shortlist_entries (tenant_id, state, updated_at DESC);
CREATE INDEX ix_audit_events_tenant_occurred
    ON audit_events (tenant_id, occurred_at DESC, audit_event_id);

CREATE TRIGGER audit_events_reject_update
BEFORE UPDATE ON audit_events
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'audit_events are append-only');
END;

CREATE TRIGGER audit_events_reject_delete
BEFORE DELETE ON audit_events
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'audit_events are append-only');
END;

INSERT INTO schema_migrations (version, name, applied_at)
VALUES (1, '0001_foundation', '2026-07-29T00:00:00+00:00');

PRAGMA user_version = 1;
COMMIT;

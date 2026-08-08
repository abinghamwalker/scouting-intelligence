BEGIN IMMEDIATE;

CREATE TABLE research_experiments (
    experiment_id TEXT PRIMARY KEY,
    schema_version INTEGER NOT NULL CHECK (schema_version = 1),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    note TEXT,
    created_at TEXT NOT NULL,
    query_id TEXT NOT NULL,
    result_id TEXT NOT NULL,
    dataset_version TEXT NOT NULL CHECK (length(trim(dataset_version)) > 0),
    dataset_manifest_digest TEXT NOT NULL CHECK (
        length(dataset_manifest_digest) = 64
        AND dataset_manifest_digest NOT GLOB '*[^0-9a-f]*'
    ),
    matrix_version TEXT NOT NULL CHECK (length(trim(matrix_version)) > 0),
    matrix_digest TEXT NOT NULL CHECK (
        length(matrix_digest) = 64 AND matrix_digest NOT GLOB '*[^0-9a-f]*'
    ),
    index_version TEXT NOT NULL CHECK (length(trim(index_version)) > 0),
    index_manifest_digest TEXT NOT NULL CHECK (
        length(index_manifest_digest) = 64
        AND index_manifest_digest NOT GLOB '*[^0-9a-f]*'
    ),
    request_json TEXT NOT NULL CHECK (
        json_valid(request_json) AND json_type(request_json) = 'object'
    ),
    result_json TEXT NOT NULL CHECK (
        json_valid(result_json) AND json_type(result_json) = 'object'
    ),
    comparison_json TEXT CHECK (
        comparison_json IS NULL
        OR (json_valid(comparison_json) AND json_type(comparison_json) = 'object')
    ),
    report_json TEXT NOT NULL CHECK (
        json_valid(report_json) AND json_type(report_json) = 'object'
    ),
    report_digest TEXT NOT NULL CHECK (
        length(report_digest) = 64 AND report_digest NOT GLOB '*[^0-9a-f]*'
    ),
    report_relative_path TEXT NOT NULL CHECK (
        length(trim(report_relative_path)) > 0
        AND substr(report_relative_path, 1, 1) <> '/'
        AND instr(report_relative_path, '..') = 0
    ),
    experiment_digest TEXT NOT NULL UNIQUE CHECK (
        length(experiment_digest) = 64 AND experiment_digest NOT GLOB '*[^0-9a-f]*'
    )
) STRICT;

CREATE TABLE research_replay_receipts (
    replay_receipt_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES research_experiments (experiment_id),
    replayed_at TEXT NOT NULL,
    reproduced INTEGER NOT NULL CHECK (reproduced IN (0, 1)),
    original_result_digest TEXT NOT NULL CHECK (
        length(original_result_digest) = 64
        AND original_result_digest NOT GLOB '*[^0-9a-f]*'
    ),
    replay_result_digest TEXT NOT NULL CHECK (
        length(replay_result_digest) = 64
        AND replay_result_digest NOT GLOB '*[^0-9a-f]*'
    ),
    receipt_json TEXT NOT NULL CHECK (
        json_valid(receipt_json) AND json_type(receipt_json) = 'object'
    )
) STRICT;

CREATE INDEX ix_research_experiments_created
    ON research_experiments (created_at DESC, experiment_id);
CREATE INDEX ix_research_replay_receipts_experiment
    ON research_replay_receipts (experiment_id, replayed_at DESC);

CREATE TRIGGER research_experiments_reject_update
BEFORE UPDATE ON research_experiments BEGIN
    SELECT RAISE(ABORT, 'research_experiments are append-only');
END;
CREATE TRIGGER research_experiments_reject_delete
BEFORE DELETE ON research_experiments BEGIN
    SELECT RAISE(ABORT, 'research_experiments are append-only');
END;
CREATE TRIGGER research_replay_receipts_reject_update
BEFORE UPDATE ON research_replay_receipts BEGIN
    SELECT RAISE(ABORT, 'research_replay_receipts are append-only');
END;
CREATE TRIGGER research_replay_receipts_reject_delete
BEFORE DELETE ON research_replay_receipts BEGIN
    SELECT RAISE(ABORT, 'research_replay_receipts are append-only');
END;

INSERT INTO schema_migrations (version, name, applied_at)
VALUES (3, '0003_w09_research', '2026-08-05T00:00:00+00:00');

PRAGMA user_version = 3;
COMMIT;

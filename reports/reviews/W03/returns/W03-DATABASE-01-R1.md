# Subagent return

## Task

- task_id: W03-DATABASE-01
- objective: Implement the first append-only PostgreSQL/pgvector migration, local
  loopback-only Compose services, and executable migration/security tests for W03.

## Files changed

- compose.yaml
- .env.example
- alembic.ini
- migrations/__init__.py
- migrations/env.py
- migrations/script.py.mako
- migrations/versions/__init__.py
- migrations/versions/0001_foundation.py
- src/scouting/storage/postgres.py
- scripts/apply_migrations.py
- tests/integration/test_migrations.py
- tests/security/test_database_boundaries.py
- reports/reviews/W03/returns/W03-DATABASE-01-R1.md

## Summary

- Replaced the W01 Compose placeholder with cached PostgreSQL 16/pgvector and Redis 7
  services whose published ports are loopback-only, whose image tags are not
  `latest`, and whose PostgreSQL password must be supplied through the local
  environment.
- Added a fail-closed SQLAlchemy URL boundary. `SCOUTING_DATABASE_URL` is mandatory,
  must use `postgresql+psycopg`, must name a user and database, must resolve through
  an explicit loopback authority, and cannot override the host through connection
  query parameters.
- Added Alembic revision `0001_foundation`. It creates the vector extension, canonical
  tenant/team/player/competition/season/match tables, versioned role-brief and
  shortlist workflow tables, retrieval/vector metadata, candidate results, and
  append-only audit events.
- Added composite tenant foreign keys, positive optimistic versions, lifecycle and
  digest checks, contract-aligned shortlist provenance constraints, tenant indexes,
  and a six-dimensional pgvector column with an HNSW cosine index.
- Added a `scouting_app` non-login, non-owner, non-superuser, non-bypass role. Every
  tenant table has enabled and forced row-level security, with a deny-on-missing
  tenant policy. Runtime audit access is select/insert only and an independent
  trigger rejects owner-level update/delete attempts.
- The migration is append-only: upgrade is idempotent through Alembic and downgrade
  fails explicitly. Tests create only regex-guarded temporary W03 databases and
  remove them after each module.

## Tests run

- command: `uv run python -c "<loopback PostgreSQL SELECT 1 health assertion>"`
  - exit status: 0
  - result: PostgreSQL returned `1`.
- command: `uv run python -c "<Compose boundary and Redis TCP health assertions>"`
  - exit status: 0
  - result: exact cached image tags, loopback port bindings, environment-only
    PostgreSQL password interpolation, and Redis loopback reachability passed.
- command: `uv run pytest -q tests/integration/test_migrations.py tests/security/test_database_boundaries.py`
  - exit status: 0
  - result: 7 passed in 0.74s against the master-started local PostgreSQL service.
- command: `uv run ruff format --check migrations src/scouting/storage/postgres.py scripts/apply_migrations.py tests/integration/test_migrations.py tests/security/test_database_boundaries.py`
  - exit status: 0
  - result: 8 files already formatted.
- command: `uv run ruff check migrations src/scouting/storage/postgres.py scripts/apply_migrations.py tests/integration/test_migrations.py tests/security/test_database_boundaries.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/postgres.py scripts/apply_migrations.py`
  - exit status: 0
  - result: no issues in 2 source files.
- command: `uv run bandit -q -r migrations src/scouting/storage/postgres.py scripts/apply_migrations.py`
  - exit status: 0
  - result: no findings.

## Artifacts/evidence

- Alembic revision: `0001_foundation`
- PostgreSQL extension evidence: `vector` installed in each isolated migrated test
  database and `player_representations.embedding` verified as dimension 6.
- Tenant-boundary evidence:
  `tests/security/test_database_boundaries.py` verifies role flags, policies, forced
  RLS on all 13 tenant tables, fail-closed missing context, cross-tenant read/write
  denial, runtime audit mutation denial, and trigger-enforced owner mutation denial.
- Migration evidence:
  `tests/integration/test_migrations.py` verifies an empty-database upgrade, second
  idempotent upgrade, the expected schema, vector extension, optimistic version
  constraint, and cross-tenant composite foreign-key rejection.

## Risks

- `scouting_app` is deliberately `NOLOGIN`; application database work must enter it
  with transaction-local role and tenant context. A later composition packet must
  centralise that transaction wrapper so callers cannot accidentally use the local
  owner connection directly.
- The approved cached image tags are version-line tags rather than immutable digests.
  The master should record local image identities/container scan evidence at the W03
  gate without pulling or publishing an image.
- This first migration is intentionally not reversible. Future schema changes must
  follow expand-migrate-contract with a separate restore rehearsal.

## Follow-up items

- Master independently applies/replays `0001_foundation`, runs the packet suite, and
  reviews the role-use boundary before acceptance.
- The authorised W03 composition packet should use `SET LOCAL ROLE scouting_app` and
  a transaction-local `scouting.tenant_id` for every application transaction.

## Scope confirmation

- no Git operations: confirmed; no Git command or `.git` edit was performed.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.

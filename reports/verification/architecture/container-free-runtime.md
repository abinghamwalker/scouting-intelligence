# Container-free runtime architecture amendment verification

- Date: 2026-07-29
- Authority: explicit user decision; ADR 0004
- Scope: runtime, persistence, dependencies, governance and controlling plans
- Result: PASS, with an unrelated pre-existing W04 test rework item recorded below

## Implemented boundary

- Deleted the Compose definition and PostgreSQL/Alembic implementation.
- Removed direct PostgreSQL, pgvector, Psycopg, Alembic and MLflow dependencies.
- Removed the transitive Docker SDK and service-oriented MLflow dependency tree from
  `uv.lock`.
- Added a guarded SQLite database path with no listener or credentials.
- Added an append-only SQLite migration with foreign keys, JSON validation, optimistic
  version constraints, a one-tenant trigger and audit update/delete rejection triggers.
- Retained Parquet/DuckDB/Polars for analytical products and made versioned local
  artifacts plus in-process Python the vector-retrieval authority.
- Replaced Redis/queue assumptions with in-process or guarded-file jobs, cache and locks.
- Superseded ADR 0003; amended both controlling HTML plans, the master plan, phase
  registry, environment policies, threat model, README and agent instructions.
- Added repository verification that rejects container definitions, external-service
  dependencies, forbidden packages in the lockfile, or missing plan/ADR authority.

## Verification

| Command/check | Result |
| --- | --- |
| `uv lock --check` | PASS; 83 packages resolved |
| `uv sync --locked --all-groups` | PASS; removed 58 obsolete/service packages from the environment |
| `uv run python scripts/apply_migrations.py` | PASS; embedded migration applies with no service |
| `uv run ruff format --check .` | PASS; 137 files formatted |
| `uv run ruff check .` | PASS |
| `uv run mypy src/scouting scripts services` | PASS; 43 source files |
| `uv run lint-imports` | PASS; 3 contracts kept |
| `uv run bandit -q -r scripts src services` | PASS |
| Container-free governance/storage targeted tests | PASS; 41 tests |
| Runtime regression excluding the three unrelated W04 Wyscout rework files | PASS; 229 tests |
| `uv run python scripts/verify_local_only.py` | PASS; container definition, dependency, lock and authority gates pass |
| `uv run python scripts/install_local_git_guards.py --check` | PASS |
| `git diff --check` | PASS |
| `git remote` | PASS; empty |
| Docker process inspection | PASS; no `scouting-intelligence` containers exist |

The unfiltered repository suite ran 383 collected tests. It reached 310 passes, then
reported 19 failures and 54 setup errors exclusively in the existing uncommitted W04
Wyscout redirect-authority work. The reviewed YAML contains
`credential_separator_encoding`, while its parser and tests still reject that field.
That independent W04 `REWORK` state was not altered as part of this architecture
amendment.

The former `scouting-intelligence_scouting_postgres_data` Docker volume remains
retained. It was not deleted or migrated; preserving it keeps the change recoverable.

## Reintroduction control

No later phase may add a container, external operational/vector database, external
cache, external queue or mandatory service process. ADR 0004 requires retained
necessity evidence, explicit user approval, a new ADR, amendments to both controlling
plans and a governance-gate amendment before implementation.

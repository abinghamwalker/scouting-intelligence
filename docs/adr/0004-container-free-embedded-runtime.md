# ADR 0004: Container-free embedded runtime

- Status: Accepted
- Decision date: 2026-07-29
- Decision owner: User
- Scope: Programme-wide; all current and future waves
- Supersedes: ADR 0003 and the Compose allowance in ADR 0001

## Context

The approved local workflow is single-user, single-tenant and runs from one
`uv`-managed Python environment. The implemented Redis service had no application
consumer. PostgreSQL-specific roles, row-level security and pgvector added a service,
credentials, ports and container lifecycle before concurrent users, remote deployment
or measured vector-search constraints existed.

The user explicitly decided that containers are not part of this workflow and asked
that later phases must not silently reinstate them.

## Decision

- The reference runtime is container-free. Dockerfiles, Compose files, development
  containers and required container images are forbidden.
- SQLite is the embedded authoritative store for operational workflow and audit state.
  Its database file stays under `data/working/` by default, opens no listener, needs no
  credentials and enforces one tenant per database.
- Versioned append-only SQLite migrations retain foreign keys, optimistic versions,
  JSON validation and database-level audit immutability.
- Guarded Parquet plus DuckDB/Polars remains the analytical store.
- Vector representations are immutable, versioned local artifacts. Retrieval runs
  in-process through the shared Python serving core until retained scale/latency/recall
  evidence justifies a different design.
- Scheduled work, bounded caches and locks run in-process or through guarded local
  files. Redis, external queues and cache servers are forbidden.
- FastAPI, workers, migrations, tests, modelling and evaluation all run through the
  one root `uv` environment.
- PostgreSQL, pgvector, Psycopg, Redis clients, container SDKs and orchestration
  dependencies whose only purpose is external service management are not runtime
  dependencies.

## Change control

No later task, wave, agent or dependency packet may add a container definition,
external operational database, cache server, queue service or mandatory service
process. Reintroduction requires all of the following before implementation:

1. retained evidence showing that the embedded design fails a declared requirement;
2. explicit user approval of the proposed replacement;
3. a new accepted ADR;
4. matching amendments to both controlling HTML plans; and
5. an updated repository governance gate.

Scale, familiarity, production convention or a future-plan placeholder is not
sufficient authority.

## Consequences

Local setup and verification require only `uv`; tests create isolated temporary
database files. Database-enforced multi-tenant row-level security is intentionally
absent because the database itself rejects a second tenant. A future multi-user or
remote programme is a separate architecture decision, not an automatic continuation
of this one.

Historical W03 reports remain accurate evidence of what was previously tested, but
they do not authorise the superseded runtime.


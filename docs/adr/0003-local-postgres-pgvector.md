# ADR 0003: Local PostgreSQL/pgvector and Redis services

- Status: Superseded by ADR 0004 on 2026-07-29
- Decision owners: User-approved plans; master review required for integration
- Controlling wave: W03

This document is retained as historical W03 evidence only. It is not authority for
current or future implementation.

## Context

The modular monolith needs a transactional operational store for canonical entities,
tenant-aware workflow, append-only audit metadata and moderate vector retrieval. It
also needs a bounded local mechanism for asynchronous exports, caching and run locks.
The authorised programme remains local and uses one uv-managed Python project; no cloud
or public service is allowed.

## Decision

- Run PostgreSQL with the pgvector extension as a local Docker Compose service.
- Use PostgreSQL as the authoritative home for canonical entities, crosswalks, role
  briefs, shortlists, observations, retrieval metadata, audit events and vector-index
  records.
- Run Redis as a local Docker Compose service, limited to asynchronous work, bounded
  cache entries and run locks. Redis is never the authoritative home of a decision,
  audit record, manifest or rights state.
- Bind published service interfaces to loopback only. Do not expose a public endpoint
  or create a cloud-managed service.
- Run FastAPI and the worker from the root uv environment. They share versioned
  contracts and the one serving core.
- Keep immutable source/data/model/evaluation payloads in guarded project-local
  artifact storage; PostgreSQL stores their queryable metadata and manifest references.
- Pin local service versions in the master-owned Compose configuration and keep
  credentials out of committed configuration.
- Treat pgvector index/model changes as immutable new versions selected through a
  controlled alias or version reference; never mutate the reader's evidence silently.

## Consequences

The first local system can use database transactions, constraints, optimistic locking,
row ownership and relational joins without introducing a separate vector platform.
Redis can be lost or flushed without losing authoritative state. Backup, restore,
capacity, concurrency and failover evidence remain later-gate work and are not claimed
by this ADR.

## Rejected alternatives

- **Dedicated vector database:** rejected until measured recall or latency proves
  pgvector insufficient for the declared workload.
- **Event-streaming platform:** rejected because the local workflow has no evidenced
  event volume that requires one.
- **Cloud-managed database/cache or public service:** prohibited by the local-only
  boundary.
- **Separate model-serving database/service:** rejected until independent scaling is
  demonstrated; it would create a second serving path before one is needed.
- **Redis as durable workflow or audit storage:** rejected because cache/queue loss must
  not alter authoritative evidence or decisions.

## Revisit triggers

Revisit this decision only when retained measurements show one of the following:

- PostgreSQL/pgvector cannot meet the declared recall, latency or capacity gate;
- real asynchronous work demonstrates Redis is unnecessary or insufficient;
- an approved multi-tenant or remote deployment changes isolation, availability,
  backup or managed-service requirements;
- local failure/recovery evidence identifies a material safety problem with the
  topology.

Any remote or managed alternative additionally requires explicit user approval of a
separate deployment plan.

## Authority trace

- `../scouting-ml-production-blueprint.html`: sections 03, 04, 08 (P1.3) and decisions
  D6 and D10.
- `../scouting-ml-agent-implementation-workflow.html`: sections 01 and 05, and waves
  W03 and W10.

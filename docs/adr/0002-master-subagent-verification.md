# ADR 0002: Master-owned, verification-gated agent delivery

- Status: Accepted
- Decision owners: User and master orchestrator
- Controlling wave: W02

## Context

Parallel agents can accelerate bounded implementation, but shared contracts, migrations,
dependency state, integration files, and acceptance evidence require one authority.

## Decision

- The master owns planning, packets, dependencies, integration, independent
  verification, rework decisions, commits, and tags.
- Subagents receive one path-scoped packet, run only named uv checks, produce the
  mandatory handback, and perform no Git operation.
- Incomplete scope, return, implementation, or evidence is `REWORK`; there is no partial
  acceptance.
- Parallel dispatch requires path-disjoint write scopes and is prohibited for shared
  contracts, migrations, dependencies/lockfiles, registries/aliases, and integration
  files.
- Machine-readable phase, task-return, local-only, and parallel-safety verification
  support—but never replace—the master's readback and rerun.

## Rejected options

- Subagent-authored commits or self-approval.
- Open-ended phase assignments without allowed/forbidden paths.
- Parallel writes to shared contracts or integration surfaces.
- Acceptance based only on a worker's reported checks.

## Consequences

The repository retains task packets, returns, master reviews, failures, corrections, and
gate evidence. Negative results remain visible, and only the master creates checkpoints.

## Revisit trigger

Revisit only through a user-approved workflow change backed by a successful bounded
control-plane drill and an updated threat/integrity review.

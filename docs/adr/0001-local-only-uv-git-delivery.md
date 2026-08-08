# ADR 0001: Local-only uv and Git delivery

- Status: Accepted
- Decision owners: User and master orchestrator
- Controlling waves: W01–W11

## Context

The approved plans require a reproducible local build without creating a source-control
remote, hosted CI, cloud resource, public endpoint, or deployment programme.

## Decision

- Use one root uv project with Python 3.12, `pyproject.toml`, `uv.lock`, and `.venv`.
- Run Python commands through `uv`; do not create alternate Python or Node authorities.
- Use local Git on `main` as the evidence ledger.
- Require zero remotes and a deliberately failing repository-local pre-push hook.
- Keep generated data/runs ignored while committing reviewed manifests and gate reports.
- Use no container or Compose definition; ADR 0004 supersedes the earlier placeholder
  allowance and requires explicit user approval before any external service is added.

## Rejected options

- Git remote, pull request, or hosted CI as the acceptance mechanism.
- Cloud/public deployment during the approved local programme.
- Nested Python projects/environments or a Node package-manager layer.
- Direct Git/URL package dependencies.

## Consequences

Every master review begins with locked uv synchronisation and ends with local-only,
empty-remote, clean-tree evidence. Local package-index resolution remains allowed under
the controlling plans.

## Revisit trigger

Only explicit user approval of a separate source-control/deployment plan after the local
pilot may supersede this decision.

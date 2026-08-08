# Master task return

## Task

- task_id: W03-DEPS-01
- objective: Add only the direct Python dependencies required by the W03 foundation gate.

## Files changed

- pyproject.toml
- uv.lock
- reports/reviews/W03/returns/W03-DEPS-01-R1.md
- orchestration/reviews/REVIEW-W03-DEPS-01-R1.yaml

## Summary

- Added direct runtime declarations for Alembic, SQLAlchemy, Psycopg, pgvector, and
  OpenTelemetry SDK.
- Added HTTPX to the test group and detect-secrets/pip-licenses to the security group.
- Resolved and synced the single shared lock/environment only through uv.

## Tests run

- `uv lock --check` — exit 0; 142 packages resolved.
- `uv sync --locked --all-groups` — exit 0; 139 installed packages audited.
- `uv run python scripts/verify_local_only.py` — exit 0; all 21 checks passed.

## Artifacts/evidence

- pyproject.toml
- uv.lock
- orchestration/reviews/REVIEW-W03-DEPS-01-R1.yaml

## Risks

- New packages expand the local dependency surface; W03 licence, secret, dependency,
  and security checks remain mandatory at the phase gate.

## Follow-up items

- Exercise every direct dependency in W03 tests and remove any unused declaration before
  checkpointing.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

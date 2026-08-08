# Subagent return — partial implementation

## Task

- task_id: `W08-WEB-EXPORT-04C`, revision `R2`
- invariant: no HTTP request may expose or mutate a pack outside exporter policy,
  verified bytes and append-only audit state; malformed or oversized input must fail
  before side effects.

## Files changed

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/exports.html`
- `reports/reviews/W08/returns/W08-WEB-EXPORT-04C-R2.md`

## Completed bounded work

- Replaced full body buffering in the shared form parser with incremental
  `request.stream()` accumulation capped at 64 KiB. It checks exact URL-encoded
  media type, decimal declared content length, actual byte size, and strict UTF-8;
  malformed form input reaches the generic ValueError denial handler.
- Changed export creation identity to deterministic opaque UUIDv5 values derived from
  tenant, actor and exact brief/version/link/shortlist tuple, including server-derived
  trace and request IDs.
- Added `GET /w08/exports`: analyst/approver-only inventory, tenant audit-chain
  verification before query, analyst-own/approver-tenant filtering, and a safe local
  template exposing only pack identity, classification, checksum, generator/time,
  revocation status/reason and limitations.

## Checks completed

- `uv run ruff format src/scouting/web/w08.py` — exit 0.
- `uv run mypy src/scouting/web/w08.py` — exit 0.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py` — exit 0; 21 passed, one third-party TestClient deprecation warning.

## Unfinished mandatory gaps

- The shortlist page does not yet expose the required authorised exporter-backed
  create form with non-editable exact brief/version/link/shortlist context.
- No R2 route-level TestClient witnesses were added for create/read/revoke/inventory,
  role/tenant/IDOR/CSRF denial, deterministic repeat, tamper/recovery, or boundary
  unchanged-count assertions.
- Verified pack revoke UX and redirect/inventory assertions remain unimplemented.

## Scope confirmation

- no Git operations, dependency/lock changes, protected-output access, delegation or
  edits outside allowed paths.

# W08-WEB-EXPORT-JOURNEY-WITNESS-04L-R2 return

## Task

- task_id: `W08-WEB-EXPORT-JOURNEY-WITNESS-04L`, revision `R2`
- objective: add the one complete authorised, idempotent and revocable local export
  TestClient journey without changing the frozen production/templates surface.
- invariant: existing production/templates remain frozen; the complete authorised,
  idempotent, revoked and denied journey is established in one isolated automated test.

## Files changed

- `tests/integration/test_w08_local_workflow_app.py`
- `reports/reviews/W08/returns/W08-WEB-EXPORT-JOURNEY-WITNESS-04L-R2.md`

## Summary

- Added `test_synthetic_automated_complete_authorised_export_journey_witness`.
  It creates a retained approved exemplar brief, exact replay and TEAM shortlist via
  HTTP; extracts the rendered hidden export tuple; creates the deterministic local
  pack; and checks the verified projection, non-empty revoke action and
  evidence-honest non-disclosure wording.
- The same POST is idempotent: it retains one export row, one export audit event and
  one matching receipt. The analyst-owner and approver can read/inventory the pack;
  a second same-tenant analyst has an empty inventory and receives read/revoke denial;
  scout and admin have neither export navigation/form nor direct inventory/create/read/
  revoke access.
- Owner revocation records the reason and timestamp in the non-link inventory row,
  blocks subsequent readback, and leaves exactly one revocation plus one revocation
  audit receipt. The witness is explicitly synthetic automated test evidence, not
  representative-user evidence.

## Tests run

- `uv run ruff format --check tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: 2 files already formatted.
- `uv run ruff check tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py`
  - exit status: 0
  - result: all checks passed.
- `uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/integration/test_w08_evidence_export.py tests/security/test_w08_export_boundaries.py`
  - exit status: 0
  - result: 22 passed in 2.38s; one existing Starlette TestClient deprecation warning.

## Artifacts/evidence

- `tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_complete_authorised_export_journey_witness`
- This return.

## Risks

- No residual live product defect reproduced. The journey is an automated synthetic
  fixture and cannot satisfy the W08 representative-user evidence gate.

## Follow-up items

- Independent review and the separately authorised representative-user study remain
  required; none within this packet.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no protected-output access: confirmed
- no edits outside `allowed_paths`: confirmed

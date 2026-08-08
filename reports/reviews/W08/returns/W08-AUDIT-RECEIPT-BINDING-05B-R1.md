# Subagent return

## Task

- task_id: `W08-AUDIT-RECEIPT-BINDING-05B-R1`
- objective: Bind and verify every claimed immutable receipt identity/context field
  in the local append-only audit digest.
- invariant: Tenant ID, receipt ID, audit-event ID, predecessor digest, event digest,
  sequence, and recorded-at timestamp are canonical digest inputs; a valid-format
  isolated mutation rejects verification before another audited action.

## Files changed

- `src/scouting/audit/ledger.py`
- `tests/security/test_w08_auth_audit.py`
- `reports/reviews/W08/returns/W08-AUDIT-RECEIPT-BINDING-05B-R1.md`

## Summary

- The previous receipt digest map was `{previous_receipt_digest, event_digest,
  sequence, audit_event_id}`. It did not bind receipt identity, recording time, or
  tenant context.
- The corrected canonical JSON digest map is `{tenant_id, audit_receipt_id,
  previous_receipt_digest, event_digest, sequence, audit_event_id, recorded_at}`;
  JSON keys are sorted and compactly encoded before SHA-256.
- Receipt ID and `recorded_at` are generated before digest construction. Verification
  selects every receipt field, requires canonical UUIDs, exact offset-bearing
  ISO-8601 timestamps, and lowercase 64-character hex digests, joins events on both
  event ID and tenant, recomputes the event digest and receipt digest, and checks the
  predecessor/sequence chain.
- The isolated temporary-database witness drops only the receipt update trigger for
  all cases. It applies same-format receipt-ID and recording-time changes. Because the
  local runtime deliberately permits one tenant, the tenant case additionally disables
  SQLite foreign-key enforcement solely in the adversarial temporary connection to
  forge a valid-format distinct tenant ID. Each case rejects `verify` and a following
  `append`, with `audit_events` and `audit_receipts` count baselines unchanged.

## Tests run

- `uv run ruff format --check src/scouting/audit/ledger.py tests/security/test_w08_auth_audit.py`
  - exit status: 0
  - result: 2 files already formatted.
- `uv run ruff check src/scouting/audit/ledger.py tests/security/test_w08_auth_audit.py`
  - exit status: 0
  - result: all checks passed.
- `uv run mypy src/scouting/audit/ledger.py`
  - exit status: 0
  - result: success; no issues in 1 source file.
- `uv run pytest -q tests/security/test_w08_auth_audit.py tests/security/test_w08_export_boundaries.py tests/integration/test_w08_evidence_export.py`
  - exit status: 0
  - result: 30 passed in 1.07s.
- `uv run bandit -q src/scouting/audit/ledger.py`
  - exit status: 0
  - result: no findings.

## Artifacts/evidence

- `tests/security/test_w08_auth_audit.py::test_receipt_identity_context_and_time_tampering_fail_before_next_action`
- `reports/reviews/W08/returns/W08-AUDIT-RECEIPT-BINDING-05B-R1.md`

## Risks

- The adversarial tenant mutation necessarily disables SQLite foreign-key enforcement
  in its isolated temporary connection because production deliberately enforces a
  single tenant. This is not a production configuration change; it proves digest
  verification still rejects even after that additional storage-level compromise.
- No migration was changed, so existing receipts created under the former unbound
  digest map will fail closed under the corrected verifier. W08 is unaccepted local
  work with no retained production ledger requiring compatibility migration.

## Follow-up items

- Fresh independent security review is required; this producer does not approve its
  own correction.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no protected-output access, external/network activity, participant evidence, or
  out-of-scope work: confirmed.

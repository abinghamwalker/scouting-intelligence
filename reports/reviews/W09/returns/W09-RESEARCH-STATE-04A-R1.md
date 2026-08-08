# Subagent return

## Task

- task_id: `W09-RESEARCH-STATE-04A`
- revision: `R1`
- objective: Implement immutable SQLite experiment/replay persistence and content-addressed GuardedStorage research reports without W08 coupling.

## Files changed

- `src/scouting/storage/research.py`
- `tests/integration/test_w09_research_storage.py`
- `reports/reviews/W09/returns/W09-RESEARCH-STATE-04A-R1.md`

## Summary

- Added a typed `ResearchExperimentStore` over an injected SQLite SQLAlchemy engine and `GuardedStorage`.
- Saved experiments persist canonical, exact request/result/optional-comparison/report JSON. The authoritative `report_json` round-trips the complete `ResearchReportDescriptor`, including its independent `generated_at`; no report field is reconstructed from redundant database columns.
- Report bytes are admitted only when their SHA-256 digest, strict UTF-8 representation, canonical JSON form where applicable, format suffix and `sha256/<prefix>/<digest>.<format>` content address agree with the contract.
- SQLite intent is inserted before guarded report persistence inside one transaction. Guarded conflicts roll the row back. Exact retries are idempotent, and an already-created byte-identical content address can be adopted safely. Stable report lineage permits distinct immutable experiments to share the same exact content address.
- Loads and lists revalidate the complete strict experiment contract, canonical JSON bytes, redundant IDs/version pins/report columns and guarded report bytes before returning state.
- Replay receipts use a deterministic UUIDv5 semantic identity, retain exact saved and loaded pins, and are checked against the saved experiment ID/digest, query digest, original result ID/digest and all saved pins. Exact retries are idempotent; conflicting or incorrectly bound receipts fail closed.
- No W08 workflow, authentication, authorisation, audit or export module is imported.

## Tests and evidence

- `uv run ruff format --check src/scouting/storage/research.py tests/integration/test_w09_research_storage.py`
  - PASS: 2 files already formatted.
- `uv run ruff check src/scouting/storage/research.py tests/integration/test_w09_research_storage.py`
  - PASS: all checks passed.
- `uv run mypy src/scouting/storage/research.py`
  - PASS: no issues found in 1 source file.
- `uv run pytest -q tests/integration/test_w09_research_storage.py tests/integration/test_migrations.py`
  - PASS: 17 tests passed in 0.40s.

The integration tests cover canonical exact JSON round-trips (including a non-null comparison and exact report descriptor), report byte/digest/path rejection, noncanonical JSON and traversal rejection, same-ID conflict, identical retry, content-address sharing, guarded-artifact conflict rollback, missing experiments, deterministic replay identity, full saved-experiment receipt binding, exact saved/loaded pins, receipt idempotency, all four append-only triggers and an AST import tripwire for W08/auth/audit dependencies.

## Risks and boundaries

- A process failure after immutable report creation but before SQLite commit can leave an unreferenced content-addressed artifact. It cannot expose a partial database experiment; a byte-identical retry safely adopts the artifact, while a conflict fails closed. Automatic orphan collection is deliberately outside this packet.
- This store verifies report payload bytes, contract bindings and GuardedStorage's immutable write behavior. It does not assert football relevance or recruitment usefulness.
- The additive migration and shared research contracts were master-owned. The implementation uses the migration's authoritative `report_json` column and made no migration or contract edits.

## Scope confirmation

- No Git operations were run.
- No dependency, lockfile, migration, shared-contract, orchestration-control, storage-export or W08 file was edited.
- All edits stayed inside the packet's three allowed paths.

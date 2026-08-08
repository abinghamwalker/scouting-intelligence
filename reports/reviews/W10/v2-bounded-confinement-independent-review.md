# W10 v2 bounded-confinement independent PRE-PILOT re-review

- Review class: **fresh bounded PRE-PILOT scientific/security/integration re-review**
- Date: 2026-08-06
- Candidate status: **PASS for this bounded correction — no open P0-P3**
- Scope: current v2 filesystem confinement and exact SQLite attestation correction, the post-W04
  audit-only roster integration, and regression challenges against the previously closed W10 v2
  findings
- Explicit exclusion: **this is not `W10-V2-INDEPENDENT-REVIEW-08F`, A4 or phase acceptance,
  approval, pilot evidence, A5 authority, freeze, formal-study authority, G-RW4, W10 closure or W11
  authority.** It does not authorise participant approach or external access.

## Decision

No P0, P1, P2 or P3 was found in the current bounded candidate. The original five PRE-PILOT
findings, including the four implementation findings, remain closed. The later contract-v3
exact-current/history finding also remains closed and is strengthened by per-connection schema SQL
attestation. This review found no regression in v1/formal/approval isolation, protected-provenance
exclusion, W09 noninterference or local-only operation.

The candidate may therefore be treated as technically clear for this bounded correction only.
Progression remains a master decision under the v2 addendum and cannot be inferred from this
report.

## Findings

**No open P0-P3.**

## Filesystem confinement

`V2MechanicsPilotStore` rejects a filesystem-root `allowed_root`, requires the guarded root to be a
real non-symlink directory, and requires both database and authority paths to remain lexically and
physically beneath it. Before schema setup and before every operational SQLite connection it
rechecks path components, requires the authority and any initialized database to be single-link
regular files, requires an initialized database still to exist, and re-hashes the exact authority
bytes. Root escape, symlink, hardlink, directory/nonregular and missing-file substitutions fail
closed.

An independent temporary-store probe moved an initialized database outside the guarded root and
replaced its governed path with a symlink. Instrumenting `sqlite3.connect` then proved that
`load_session`, `record` and `complete` each rejected the symlink with **zero SQLite open calls**.
The same zero-open instrumentation independently rejected database hardlink, database-directory,
missing-database, authority-symlink and authority-hardlink substitutions. Constructor probes also
rejected `/` as `allowed_root` and rejected a database path outside its authority root.

## Exact SQLite contract and history attestation

Every operational connection validates the exact contract-v3 row, exact authority row, and a
canonical `sqlite_master` projection against independently pinned digest
`a2b5eb22b8fbc2be9802797ccab3689610e8b870f7aa3efbefe365e6cdb560a0`. The projection contains
every object named `v2_%` and every explicitly defined trigger or index attached to a `v2_%` table,
including an attacker-chosen non-v2 object name. Exact table SQL represents SQLite's implicit
autoindexes. The live freshly initialized schema independently recomputed to the pinned digest.

Independent mutations produced the following results:

- dropping the revision and command update guards, then coherently changing current judgement,
  linked revision and record-command response to the same different canonical self-digested bytes,
  made load, correction review and completion all fail at schema attestation;
- recreating those trigger names with altered SQL still failed attestation;
- adding a non-v2-named trigger, a non-v2-named index attached to a v2 table, or a `v2_*` view each
  changed the projection and was rejected;
- changing the exact authority row was rejected by the retained focused regression;
- after exact trigger restoration, a coherent completed current/revision/command response rewrite
  passed schema attestation but still failed the independent completion-receipt reconstruction
  against its original ordered response digests;
- schema-contract v1 and v2 databases were rejected, and read-back showed that each still contained
  only its original `v2_schema_contract` table: no contract-v3 object was partially created.

These results preserve both layers: exact physical schema/trigger authority is checked before
evidence reconstruction, while the receipt remains an independent semantic seal after exact schema
restoration.

## Post-W04 audit-only integration

AST-only comparison of the two independently maintained rosters found **106 entries in each and
exact tuple equality**. Each new W10 path occurs exactly once in both:

- `scripts/build_w10_expert_evidence_v2.py`
- `src/scouting/data_products/wyscout/expert_evidence.py`
- `tests/contracts/test_w10_expert_evidence_v2_contracts.py`
- `tests/unit/test_w10_expert_evidence_v2.py`

Both collectors continue to classify these caches as
`REPOSITORY_POST_W04_CACHE_AUDIT_ONLY` with `AUDIT_ONLY_ZERO_READ_USE` and
`POST_W04_SOURCE_CACHE_DENIED_ZERO_READ`. Inspection confirmed that these rows have no source
authority and that the collectors use no-follow/lstat metadata for PYC classification; roster
membership adds no source, bytecode-read, hash, import, execution, retrieval or model authority.
The focused dual-collector audit tests passed 9 tests, including exact-roster, metadata-only and
zero-PYC-open cases. The full retained runtime-control suite passed **298 tests in 114.65s**,
including the four former M-7 failures.

## Formatting-only review document

`docs/reviews/cross-phase-code-review-2026-08-06.md` is Ruff-formatted and retains its complete
finding inventory and priorities: C1-C12, P-1 through P-15, L-1 through L-16 as present in the
review, and M-1 through M-7 as present in the review, together with the original baseline,
verification notes and remediation plan. Inspection found layout-only code-fence formatting and
no weakened, removed or rewritten finding. Repository-wide `ruff format --check .` reports
**1111 files already formatted**.

## Isolation and noninterference

- Read-only immutable SQLite inspection reproduced retained v1 formal counts
  `1 approval / 0 sessions / 0 judgements / 0 completions` and v1 pilot counts
  `0 approvals / 1 session / 2 judgements / 0 completions`. No retained v1 store was opened for
  migration or accepted by the v2 contract.
- The combined 93-test W10 v1/v2 contract, evaluation, web and storage boundary passed. It retains
  pseudonym conflict/original-browser resume, v1 byte/digest compatibility, v2-only mechanics-pilot
  composition, disabled formal/approval mutation routes, participant-safe bytes and protected
  origin/rank/score/control/repeat/outcome exclusion.
- The reviewed correction creates no path from v2 responses or independent descriptors into W09
  features, scaler, weights, index, score, ranking or artifacts. The W04 edits are metadata-only
  roster additions; no W09 semantic or artifact mutation was found.
- No provider, credential, network, cloud, external service or non-loopback request authority was
  introduced. No external access was performed.

## Commands and evidence

No Git command was run. Temporary stores were confined to system temporary directories and were
discarded; this report is the only retained write.

| Check | Result |
|---|---|
| Combined seven-suite W10 v1/v2 contract/evaluation/web/storage boundary | exit 0; **93 passed**, one upstream TestClient deprecation warning |
| Current focused web/storage rerun after the final candidate tightening | exit 0; **17 passed**, same warning |
| Complete `tests/unit/test_w04_wyscout_runtime_control.py` | exit 0; **298 passed in 114.65s** |
| Focused dual-collector audit-only roster/zero-read cases | exit 0; **9 passed**, 289 deselected |
| Independent no-open confinement probe | exit 0; all substitutions rejected; escaped load/record/complete and every physical-substitution check made zero SQLite open calls |
| Independent schema/current-history/completed-receipt/old-contract probes | exit 0; every mutation rejected at the intended layer; old v1/v2 objects unchanged |
| Repository-wide Ruff format check | exit 0; **1111 files already formatted** |
| Focused Ruff check | exit 0; clean |
| Focused mypy over storage and both runtime-control sources | exit 0; no issues in 3 files |
| Focused Bandit over storage and both runtime-control sources | exit 0; no findings |

The first sandboxed attempt to run the four nested-uv W04 cases could not read the host uv cache;
two non-nested cases passed and two nested cases stopped on that environment denial. The permitted
exact full-suite rerun resolved the environmental limitation and passed all 298 tests; no product
failure is inferred from the sandbox-only attempt.

## Disposition

The current bounded-confinement candidate has **no open P0-P3**. The prior findings remain closed.
Formal v2 collection remains disabled, and all A4/A5/A6/08F/formal/G-RW4/closure authorities remain
outside this report.

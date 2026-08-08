# W08 evidence-export import-boundary independent review R1

## Review identity and verdict

- Review/task ID: `W08-EXPORT-IMPORT-BOUNDARY-REVIEW-05F-R1`
- Reviewer role: fresh independent architecture/security reviewer; report-only
- Verdict: **PASS**
- Findings: **P0 0 / P1 0 / P2 0 / P3 0**
- Required architecture rework: **none**
- Representative-user gate: **PENDING — 0/5 genuine authorised reviewed records**

The final relocation is an import-routing correction with no open architecture,
security, confidentiality, audit, accessibility or evidence-honesty finding. The old
operations exporter module is absent, `scouting.operations` is telemetry-only,
`scouting.workflow.evidence_export` is the sole exporter implementation, and runtime
and focused-test callers use the permitted workflow package. All three unchanged
import-linter contracts pass, the complete focused W08 suite passes 72 tests, and the
complete packet Bandit scan reports no finding.

This PASS applies only to the architecture relocation and its functional/security
surface. It does not close W08: automated mechanics cannot satisfy the separate G-W08/G4
human gate, which remains 0/5.

## Reviewed paths

Control, specification and retained evidence read:

- `AGENTS.md`
- `../scouting-ml-production-blueprint.html`
- `../scouting-ml-agent-implementation-workflow.html`
- `pyproject.toml`
- `orchestration/task_packets/W08-EXPORT-IMPORT-BOUNDARY-05E-R1.yaml`
- `orchestration/task_packets/W08-EXPORT-IMPORT-BOUNDARY-REVIEW-05F-R1.yaml`
- `orchestration/templates/subagent_return.md`
- `reports/reviews/W08/returns/W08-EXPORT-IMPORT-BOUNDARY-05E-R1.md`
- `reports/verification/W08/export-import-boundary-report.md`
- `reports/reviews/W08/w08-independent-security-review-R4.md`
- `reports/verification/W08/limitations.md`
- `reports/verification/W08/protected-output-boundary.md`
- `reports/verification/W08/representative-user-evidence-status.md`

Implementation paths inspected:

- `src/scouting/operations/__init__.py`
- `src/scouting/workflow/__init__.py`
- `src/scouting/workflow/evidence_export.py`
- `src/scouting/web/w08.py`

Focused test paths inspected and executed:

- `tests/contracts/test_w08_workflow_contracts.py`
- `tests/security/test_w08_auth_audit.py`
- `tests/security/test_w08_workflow_access.py`
- `tests/security/test_w08_export_boundaries.py`
- `tests/security/test_w08_web_security.py`
- `tests/integration/test_w08_workflow.py`
- `tests/integration/test_w08_evidence_export.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `tests/integration/test_w08_study_harness.py`
- `tests/e2e/test_w08_local_workflow_playwright.py`

The caller/import search also covered `src`, `services`, `scripts`, `tests`, and `apps`,
excluding the explicitly protected fixture subtree.

## Exact byte-identity and import-graph disposition

The retained master evidence records the pre-move exporter Git blob as
`1c75b99449b9fe1f77e1e4f237283c55fa3492c5`. I independently read the current
`src/scouting/workflow/evidence_export.py` bytes and computed the Git blob-format SHA-1
directly in Python (`sha1(b"blob " + decimal_length + NUL + content)`), without Git:

- current byte length: `28890`
- independently computed current Git blob-format SHA-1:
  `1c75b99449b9fe1f77e1e4f237283c55fa3492c5`
- current raw-file SHA-256:
  `201b5bd9fb94fdac0a3ab0ef750790e3158b9c49331d51e7ba0dc0a793ef7e15`
- disposition: **exact retained blob identity reproduced**; no exporter byte changed
  across the relocation evidenced by the retained pre-move blob.

Import graph disposition:

- `src/scouting/operations/evidence_export.py`: absent.
- `scouting.operations`: exports only `LocalTelemetry` and `TelemetrySnapshot` from
  `.telemetry`; it imports no workflow, policy, audit or storage implementation.
- `scouting.workflow.evidence_export`: sole definition site for
  `LocalEvidenceExporter`, `EvidenceExportDenied`, `EvidenceExportIntegrityError`, and
  `EvidenceExportResult`; its audit/contracts/policy/storage dependencies flow in the
  approved direction.
- `scouting.workflow.__init__`: exposes the exporter API from the workflow package.
- W08 runtime composition (`scouting.web.w08`) and direct exporter tests import through
  `scouting.workflow`; the sole private-policy-path test imports
  `scouting.workflow.evidence_export` directly.
- Repository caller search found no reference to
  `scouting.operations.evidence_export` and no operations compatibility re-export.

The three unchanged `pyproject.toml` contracts independently reproduced as:

1. `Current scouting modules follow the approved dependency direction` — **KEPT**
2. `Serving never imports provider adapters` — **KEPT**
3. `Workflow and policy never import provider adapters` — **KEPT**

Import-linter analysed 63 files and 144 dependencies: **3 kept, 0 broken**. No policy or
configuration weakening was needed.

## Commands and results

1. `uv run lint-imports`
   - exit: `0`
   - result: 63 files, 144 dependencies; 3 contracts kept, 0 broken.

2. `uv run pytest -q tests/contracts/test_w08_workflow_contracts.py tests/security/test_w08_auth_audit.py tests/security/test_w08_workflow_access.py tests/security/test_w08_export_boundaries.py tests/security/test_w08_web_security.py tests/integration/test_w08_workflow.py tests/integration/test_w08_evidence_export.py tests/integration/test_w08_local_workflow_app.py tests/integration/test_w08_study_harness.py tests/e2e/test_w08_local_workflow_playwright.py`
   - exit: `0`
   - result: **72 passed**, one third-party Starlette TestClient deprecation warning,
     26.67 seconds.

3. `uv run bandit -q -r src/scouting/policy/r1.py src/scouting/audit/ledger.py src/scouting/workflow/r1.py src/scouting/workflow/evidence_export.py src/scouting/observations/r1.py src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py`
   - exit: `0`
   - result: no findings.

4. Read-only caller/definition search with `rg` over `src services scripts tests apps`,
   excluding `tests/fixtures/synthetic/protected/**`, plus an explicit filesystem
   absence check for `src/scouting/operations/evidence_export.py`.
   - exit: `0`
   - result: old module absent; sole implementation under workflow; W08 callers routed
     through workflow; operations callers are telemetry-only.

5. Read-only `uv run python -c ...` blob-format digest calculation.
   - final corrected calculation exit: `0`
   - result: 28,890 bytes; Git blob-format SHA-1 exactly
     `1c75b99449b9fe1f77e1e4f237283c55fa3492c5`; raw SHA-256 recorded above.
   - audit note: the first sandboxed attempt exited `2` before calculation because the
     uv cache metadata path was not readable; an escalated retry with incorrect nested
     quoting exited `1` with `SyntaxError`; the corrected read-only command then exited
     `0`. No Git executable, repository mutation or evidence mutation occurred.

## Functional and security outcomes

- **Export authorisation and denial: PASS.** Analyst/approver grants, admin denial,
  cross-tenant IDOR denial, ownership, assignment and visibility controls pass.
- **Confidentiality and protected content: PASS.** Private observations/comments are
  projected only for the exporter, author or valid latest enabled scout assignment;
  former, disabled and analyst-only assignments do not widen private scope or origin
  metadata.
- **Persisted-byte integrity: PASS.** Digest, canonical JSON, classification, fixed
  claim boundary and evidence class are checked before read, inventory, idempotent
  creation and revocation; tampered and unreadable packs fail closed.
- **Receipt/revocation: PASS.** Hash-chained audit receipts, identity/context/time
  binding, append-only revocation and denial after revocation pass.
- **Atomicity/retry: PASS.** Storage, audit and SQL failure witnesses leave no partial
  database state; savepoint recovery and a single verified retry pass.
- **Path/input boundary: PASS.** Traversal, absolute-path and symlink hazards, bounded
  form input, CSRF and unknown-object/action denial pass.
- **Web/browser/accessibility: PASS for automated mechanics.** The focused app and
  real-Chromium tests cover the authorised complete role workflow, export journey,
  denial/recovery, loopback-only requests, keyboard/skip focus, semantic structure,
  responsive widths at 1440/390/320, and history preservation. This is not human
  usability evidence.
- **W06 fixed claim boundary: PASS.** The retained and exercised boundary remains
  `NO_GO` / `MISSING_EXPERT_RELEVANCE_EVIDENCE` / `resemblance_only` /
  `synthetic_development_only` / `LIMITED` / `no_recommendation_evidence`. The
  architecture correction adds no relevance, recommendation, transfer,
  recruitment-success, value or production-readiness evidence.
- **Protected boundary: PASS.** No protected W06 expected output or protected fixture
  was opened, searched, reconstructed, inferred or used.

## Findings

### P0

None.

### P1

None.

### P2

None.

### P3

None.

## Representative-user evidence

- required genuine authorised reviewed representative-user records: **5**
- present genuine authorised reviewed representative-user records: **0**
- present participant results: **0**
- synthetic personas counted as participants: **0**
- G-W08/G4 representative-user outcome: **PENDING**

This architecture change and its automated evidence cannot satisfy the human gate. Five
distinct authorised and consenting representative users must still complete T1–T7 under
the retained protocol, with the required de-identified checksummed records and
independent review. No participant evidence was created, inferred or represented here.

## Final disposition

**PASS.** The relocated implementation preserves the retained exact blob identity,
repairs the architecture boundary without weakening import policy, and passes the full
functional/security/browser/accessibility evidence surface with zero open P0/P1/P2/P3
findings. Required architecture rework: **none**. W08 phase closure remains separately
blocked on genuine representative-user evidence at 0/5.

## Scope confirmation

- Changed path: `reports/reviews/W08/w08-export-import-boundary-review-R1.md` only.
- No Git command or Git-invoking verifier was run.
- No product, source, test, config, migration, orchestration, dependency or lockfile
  mutation was made.
- No protected W06 expected output or protected fixture was accessed or fabricated.
- No external network, provider, model, service, public endpoint or participant was
  used.
- No participant evidence was created, inferred, reconstructed or represented.
- No delegation was used.

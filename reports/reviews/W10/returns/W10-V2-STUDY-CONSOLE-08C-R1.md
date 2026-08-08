## Task

- task_id: W10-V2-STUDY-CONSOLE-08C-R1
- objective: rework the isolated, participant-safe v2 mechanics-pilot console and its dedicated checks.

## Files changed

- src/scouting/storage/expert_study.py
- src/scouting/web/w10_expert_study.py
- apps/web/templates/w10_expert_study/base.html
- apps/web/templates/w10_expert_study/v2_dashboard.html
- apps/web/templates/w10_expert_study/v2_participant.html
- apps/web/templates/w10_expert_study/v2_unavailable.html
- apps/web/static/w10-expert-study/study.css
- apps/web/static/w10-expert-study/study.js
- tests/integration/test_w10_expert_study_console.py
- tests/e2e/test_w10_expert_study_playwright.py
- reports/reviews/W10/returns/W10-V2-STUDY-CONSOLE-08C-R1.md

## Behaviour and evidence

- The v2 authority is validated as canonical JSON (including strict safe-byte reconstruction), rather than as an incompatible strict Python mapping.
- A participant pseudonym is only an identifier. Duplicate entry never rotates, issues or replaces
  an opaque capability. It returns a bounded conflict directing the operator to the original
  browser. Ordinary reload/resume continues only through that browser's existing HttpOnly
  capability cookie; there is no pseudonym-only recovery credential.
- A pre-contract or schema-contract-v1/v2 SQLite database fails closed before DDL; v2 has no
  migration or repair authority. Fresh databases use schema contract v3. `complete` is constrained
  to 0/1; completed sessions, presentations, judgements, revisions, commands, completions and
  receipt-bound response bytes are immutable through SQLite triggers.
- Every command carries an exact per-session ordinal. Every revision binds its unique source
  command ID and separately retained command ordinal. Every load reconstructs canonical command
  identity/session/order/request/response bytes, contiguous per-presentation revisions, one-to-one
  record-command linkage, exact current-to-latest-revision equality and exact receipt-to-current-
  response digests. Missing, orphaned, duplicate, reordered, cross-presentation and active unlogged
  response histories fail closed. The reproduced valid self-digested active-row rewrite is rejected
  by load, correction review and completion.
- Exact concurrent v2 `record` and `complete` replays now re-check the command after acquiring the SQLite write transaction, so a loser which observes the winner's changed revision returns the saved result only for the same session, kind and request digest. Cross-kind/request reuse remains a conflict.
- Authority loading rejects duplicate participant-safe comparison digests. SQLite independently prevents reopening a completed session, appending a judgement revision after completion, and changing or deleting the frozen presentation schedule; direct-SQL assertions cover those boundaries.
- Correction review rows bind their citation choices to the displayed mandatory evidence-family labels for that exact comparison. Browser forms never expose or free-type internal family IDs, and a relevance rating of `0` remains visibly selected in correction controls.
- V2 has an explicit completed-session detach POST that clears only its v2 HttpOnly capability
  cookie; it does not delete SQLite evidence. Re-entering that completed pseudonym from another
  browser remains a conflict. The browser journey detaches a completed participant and starts a
  genuinely distinct next participant.
- The shared page shell is route-aware: v1 retains its established copy and navigation, while v2
  identifies a visible-identity football-evidence mechanics pilot, states that protected retrieval
  provenance remains hidden, routes Study home to `/w10/v2`, and targets a real keyboard-focusable
  `#study-content` element. V2 renders the same 16 W09-input rows and governed independent-evidence
  structure side by side, with exact raw/percentile values, table fallbacks, glossary, coverage and
  limitation states; it exposes no aggregate closer/recommended/better verdict.
- The real-browser v2 journey covers keyboard skip navigation, desktop and narrow mobile rendering, symmetric panel evidence, raw/percentile toggle, glossary, safe payload/body fields and loopback-only requests. Responsive tables now wrap long evidence definitions.
- Production composition remains only `data/working/w10/study/v2/pilot/mechanics-pilot-authority-v1.json` and `data/working/w10/study/v2/pilot/mechanics-pilot-v2.sqlite3`; launch is `uv run python services/api/w10_study_main.py` on `127.0.0.1:8771`.

## Commands run

- `uv run ruff format --check src/scouting/storage/expert_study.py src/scouting/web/w10_expert_study.py tests/integration/test_w10_expert_study_console.py tests/e2e/test_w10_expert_study_playwright.py` — exit 0.
- `uv run ruff check src/scouting/storage/expert_study.py src/scouting/web/w10_expert_study.py tests/integration/test_w10_expert_study_console.py tests/e2e/test_w10_expert_study_playwright.py` — exit 0.
- `uv run python -m compileall -q src/scouting/storage/expert_study.py src/scouting/web/w10_expert_study.py` — exit 0.
- `uv run pytest -q tests/unit/test_w10_expert_study_web.py tests/integration/test_w10_expert_study_console.py` — exit 0; 13 passed, 1 warning.
- `uv run pytest -q tests/e2e/test_w10_expert_study_playwright.py -k v2_evidence` — exit 0; 1 passed (2 deselected v1 journeys).

### Master bounded-rework reproduction — 2026-08-06

- `uv sync --locked --all-groups` — exit 0; resolved 83 packages and audited 82 packages.
- Combined W10 v1/v2 contract, unit and integration command over seven focused suites — exit 0;
  **91 passed**, one upstream TestClient deprecation warning.
- `pytest -q tests/e2e/test_w10_expert_study_playwright.py` with a temporary loopback-only bind —
  exit 0; **3 passed**. The v2 journey keyboard-activates every navigation link, verifies no 404,
  skip-link focus, accurate framing, exact panel/profile parity, desktop/mobile layouts, resume,
  correction, immutable completion, detach and zero non-loopback requests; both retained v1 browser
  journeys pass unchanged.
- Repository-wide `ruff check`, `mypy src/scouting scripts`, `lint-imports` and
  `bandit -q -r scripts src` — exit 0. Focused formatting over every A2/A3 Python file passes.
- `git diff --check`, local Git guard verification and local-only verification — exit 0; zero
  remotes and the executable local-only pre-push guard are retained.
- The repository-wide formatter reports only the pre-existing untracked
  `docs/reviews/cross-phase-code-review-2026-08-06.md` code-fence formatting issue. It is outside
  the bounded W10 A2/A3 paths and was deliberately not edited by this correction.

## Residual risks and follow-up

- The real two-reviewer v2 mechanics pilot has not occurred. Its evidence cannot be simulated,
  inferred or automated.
- Formal v2 session creation, collection, freeze, approval and G-RW4 submission remain disabled.
  V1 approval does not unlock any v2 path, and no database is migrated or silently repaired.
- This is a bounded-rework candidate return for fresh independent PRE-PILOT review. It is not
  acceptance, `08F`, product-owner approval, human evidence, a protocol/query-pack freeze or W10
  closure.

## Scope confirmation

- No Git operations.
- No dependency or lockfile changes.
- No edits outside the packet's allowed paths.

## Second bounded PRE-PILOT correction — 2026-08-06

This correction addresses newly reproduced confinement and coherent-history blockers without
reopening or weakening the four previously closed findings.
The earlier packet scope confirmation applies to its original return; the W04 roster and review-
document formatting work below was executed serially as a separately authorised master integration
correction, not attributed to the 08C subagent.

- `V2MechanicsPilotStore` now rejects a filesystem-root `allowed_root`. Before schema access and
  before every connection, it revalidates the root, database and authority paths as confined,
  non-symlinked, single-link regular files and re-hashes the exact authority bytes. After a store
  is initialized, moving its database outside the guarded root and replacing the governed path
  with a symlink makes load, record and completion all fail before SQLite opens that target.
  Separate regressions reject a hard-linked database alias, a directory substituted for the
  database, a symlinked authority, an escaped constructor path and a database that disappears after
  initialization.
- Every SQLite connection now attests the exact schema-contract row, exact mechanics-pilot
  authority row and a canonical projection of every `v2_*` table and trigger definition against
  independently pinned schema-SQL digest
  `a2b5eb22b8fbc2be9802797ccab3689610e8b870f7aa3efbefe365e6cdb560a0`. Object-name parity alone
  is no longer sufficient. Missing, replaced or altered append-only/immutability trigger SQL fails
  before journal-mode setup or participant evidence reconstruction.
- The exact coherent active-history attack is retained as a regression: after dropping the
  revision and command update guards and changing the current judgement, revision and record-
  command response to the same different canonical self-digested bytes, load, correction review
  and completion all reject the database at per-connection schema attestation. Replacing the
  trigger names with altered trigger SQL also fails. Exact trigger restoration after a coherent
  completed-response rewrite still reaches the retained completion-receipt reconstruction and
  fails against its original ordered response digests.
- Schema-contract-v1/v2 databases still fail closed before any partial v3 creation. Pseudonym
  conflict/original-browser resume, schema-v3 command/revision ordering, receipt immutability,
  v1/v2 authority separation, participant-safe bytes and protected-provenance exclusion are
  unchanged.
- The independently copied W04 post-W04 PYC rosters were extended only for the four new W10 Python
  source/test paths. Their metadata-only `AUDIT_ONLY_ZERO_READ_USE` semantics are unchanged; the
  complete retained W04 runtime-control suite passes **298 tests**.
- Ruff formatted `docs/reviews/cross-phase-code-review-2026-08-06.md`; only code-fence layout
  changed and its review findings remain unchanged. Repository-wide `ruff format --check .` now
  reports **1111 files already formatted**.

### Reproduced verification

- `uv sync --locked --all-groups` — exit 0; 83 packages resolved and 82 audited.
- Combined focused W10 v1/v2 contract, unit and integration boundary — exit 0; **93 passed**, one
  upstream TestClient deprecation warning.
- Focused real-browser v2 journey — exit 0; **1 passed, 2 deselected** in 4.34 seconds, with only a
  temporary loopback bind.
- Complete `tests/unit/test_w04_wyscout_runtime_control.py` — exit 0; **298 passed** in 114.47
  seconds. The four previously reproduced admission tests pass.
- Repository-wide Ruff format/check, `mypy src/scouting scripts`, import-contracts, Bandit and
  `git diff --check` — exit 0.
- Production v2 comparison reconstruction — exit 0; 318,525 bytes, SHA-256
  `ebecc523f790264df4b1500ce5f9a2889c085607aa7858dfc776159eee4b3554`, comparison digest
  `e06544feff1fa7733dbcced337617f1b87502256702edf75b63800cc2bdde69b`, exact canonical
  reserialization, no forbidden keys and no forbidden values.

Formal v2 remains disabled. No A5 action, participant approach, database migration, W09 semantic
change, Git mutation, approval, freeze or phase acceptance is claimed. This candidate is returned
for a fresh independent PRE-PILOT re-review.

## Master A4 reconciliation — 2026-08-06

After both fresh bounded pre-pilot reviews reported no open P0-P3, the master independently
reproduced the 93-test W10 boundary, all three real-browser journeys, the complete 298-test W04
runtime-control suite, the production comparison-byte witness, retained v1 counts and formal-route
isolation. The decision is retained in
`reports/verification/W10/v2-scientific-adversarial-verification.md`.

`W10-V2-STUDY-CONSOLE-08C-R1` is **ACCEPTED for the isolated v2 mechanics-pilot boundary**. This is
an A4 engineering disposition only. It is not 08F, human evidence, v2 approval, formal authority,
G-RW4, W10 acceptance or W11 authority. The next packet is 08D in `READY` state and must stop for
at least two authentic eligible football-domain reviewers.

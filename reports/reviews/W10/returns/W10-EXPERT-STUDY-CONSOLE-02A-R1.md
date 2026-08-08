# W10 expert-study console implementation return

## Task

- task_id: `W10-EXPERT-STUDY-CONSOLE-02A:R1`
- objective: Implement the simple local-only protocol decision page, blinded expert journey,
  separate SQLite pilot/formal authorities, immutable captures, resume/idempotency/concurrency,
  and safe participant handoff.

## Files changed

- `src/scouting/storage/expert_study.py`
- `src/scouting/web/w10_expert_study.py`
- `services/api/w10_study_main.py`
- `apps/web/templates/w10_expert_study/base.html`
- `apps/web/templates/w10_expert_study/dashboard.html`
- `apps/web/templates/w10_expert_study/participant.html`
- `apps/web/templates/w10_expert_study/complete.html`
- `apps/web/templates/w10_expert_study/unavailable.html`
- `apps/web/static/w10-expert-study/study.css`
- `apps/web/static/w10-expert-study/study.js`
- `tests/unit/test_w10_expert_study_web.py`
- `tests/integration/test_w10_expert_study_console.py`
- `tests/e2e/test_w10_expert_study_playwright.py`
- `reports/reviews/W10/returns/W10-EXPERT-STUDY-CONSOLE-02A-R1.md`

## Summary

- Added one loopback `/w10` journey with a concise approval decision page, explicit immutable
  human approval, participant eligibility/consent, 22-presentation mechanics pilot, 82-presentation
  formal study, progress/resume, explicit missingness, review, submit-once receipt, and completed
  participant detach for safe sequential participation.
- Pinned the exact frozen protocol, query-pack and participant-presentation digests. The web
  process reads only canonical protocol/presentation bytes and contains no W09 runtime, evaluator,
  query-pack file, candidate origin, rank, score, threshold outcome or browser-storage seam.
- Formal primary and delayed-repeat orders are deterministic and participant-keyed; the two
  repeats use exactly the frozen participant-safe anchor identities without rendering repeat
  identity to the browser.
- Added separate `pilot.sqlite3` and `formal.sqlite3` stores/capture roots, exact authority rows,
  opaque capabilities, revisions, operation-bound command idempotency, concurrent completion,
  content-addressed immutable captures, canonical receipts, and a formal-only evaluator envelope
  export that rejects pilot, TEST_ONLY, stale, mixed, duplicate and unsafe-path input.
- TEST_ONLY formal mechanics never construct or retain `FormalStudySubmission` or
  `CompletionReceipt`; their captures explicitly say `formal_evidence_recorded:false` and cannot
  be exported to the evaluator.
- Added no-follow/exclusive output handling, symlink/hardlink/ancestor checks, strict bounded forms,
  CSRF and loopback controls, security headers, safe templating, deliberate rating placeholders,
  accessible semantic structure, and a responsive 320px layout.

## Tests run

- command: `uv run pytest -q tests/unit/test_w10_expert_study_web.py`
  - exit status: `0`
  - result: `6 passed` (one upstream Starlette/httpx deprecation warning)
- command: `uv run pytest -q tests/integration/test_w10_expert_study_console.py`
  - exit status: `0`
  - result: `5 passed` (one upstream Starlette/httpx deprecation warning)
- command: `uv run pytest -q tests/e2e/test_w10_expert_study_playwright.py`
  - exit status: `0`
  - result: `2 passed` against real local headless Chrome, including the complete 22-task journey
- command: `uv run ruff format --check src/scouting/storage/expert_study.py src/scouting/web/w10_expert_study.py services/api/w10_study_main.py tests/unit/test_w10_expert_study_web.py tests/integration/test_w10_expert_study_console.py tests/e2e/test_w10_expert_study_playwright.py`
  - exit status: `0`
  - result: all six files formatted
- command: `uv run ruff check src/scouting/storage/expert_study.py src/scouting/web/w10_expert_study.py services/api/w10_study_main.py tests/unit/test_w10_expert_study_web.py tests/integration/test_w10_expert_study_console.py tests/e2e/test_w10_expert_study_playwright.py`
  - exit status: `0`
  - result: all checks passed
- command: `uv run mypy src/scouting/storage/expert_study.py src/scouting/web/w10_expert_study.py services/api/w10_study_main.py`
  - exit status: `0`
  - result: no issues in three source files

## Artifacts/evidence

- Production composition root: `services/api/w10_study_main.py`
- Participant-safe page and assets: `apps/web/templates/w10_expert_study/` and
  `apps/web/static/w10-expert-study/`
- Operational contract/persistence boundary: `src/scouting/storage/expert_study.py`
- Browser/storage witnesses: the three W10 console test files listed above
- No file exists under the production W10 working-data roots at handback; tests used isolated
  temporary TEST_ONLY stores.

## Risks

- The page creates a real approval only when a human enters a valid product-owner pseudonym and
  checks the exact confirmation. No such action occurred during implementation or tests.
- Formal participation remains local to the host browser and should be supervised as a protected
  research process. Completion files contain protected row-level responses and must not be shared
  outside the guarded local workflow.
- FastAPI's test client emits an upstream Starlette/httpx deprecation warning; it does not affect
  the real Chrome journey or runtime behaviour and no dependency change was authorised.

## Follow-up items

- Obtain the user's explicit approval through the concise `/w10` decision page.
- Invite at least five real eligible football experts and keep the resulting protected evidence
  local for the one-use evaluator.

## Scope confirmation

- no Git operations: confirmed for the delegated implementation; the master owns integration
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no real protocol approval, participant submission or formal gate result: confirmed

## Master remediation after independent review

The master retained this producer handback and then resolved the independent review findings.
Formal repeats now follow the exact digest-bound, participant-keyed, delayed, interleaved,
nonadjacent and nonterminal schedule that the evaluator reconstructs independently; middleware
requires both a loopback Host and a loopback transport peer; and pre-submit review supports
append-only, digest-linked response corrections before the final immutable seal. The participant
view still exposes no presentation kind, origin, rank, score or cross-response linkage. The final
focused W10 contracts/evaluator/console/browser suite passed 54/54.

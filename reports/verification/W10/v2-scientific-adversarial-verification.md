# W10 presentation-v2 master scientific and adversarial verification

- Decision date: 2026-08-06
- Decision authority: W10 master
- A4 decision: **PASS**
- Packet disposition: `W10-V2-STUDY-CONSOLE-08C-R1` is **ACCEPTED**
- Next packet: `W10-V2-MECHANICS-PILOT-08D-R1` is **READY FOR AUTHENTIC HUMAN EXECUTION**
- Phase state: **W10 remains REWORK**

This decision accepts the v2 console and its protected mechanics-pilot boundary for A4 only. It is
not `W10-V2-INDEPENDENT-REVIEW-08F`, a successful mechanics pilot, product-owner approval, protocol
freeze, formal-study authority, G-RW4 evidence, W10 acceptance or W11 authority.

## Master decision basis

The master inspected the current A2/A3 implementation, task returns, the original PRE-PILOT review,
both bounded re-reviews and the retained v1 evidence. The fresh bounded reviews report no open
P0-P3. The master then independently reproduced the checks below rather than treating a reviewer's
self-assessment as gate evidence.

| A4 challenge | Reproduced result |
|---|---|
| Contract reconstruction, exact policy, missingness, purpose separation and position rules | Passed in the seven-suite 93-test W10 boundary. |
| W09-input versus independent-descriptor separation and circularity | No independent-family execution path into W09 features, scaler, weights, index, scorer or ranking; contract tests passed. |
| GK and position appropriateness | Exact GK, DF, MD defensive, MD shooting and FW rules passed; unsupported evidence remains `not_captured`, never zero or prose inference. |
| V1/v2 substitution and pilot/formal separation | V1 bytes and routes remain separate; v1 approval cannot create a v2 session; formal and approval mutation routes are absent from the v2 app. |
| Protected provenance and participant bytes | Production reconstruction was canonical and the forbidden-key/value scan was empty. |
| Identity, time, evidence coverage and asymmetric rendering | Contract and browser checks passed; both panels use the same context, metric, descriptor, glossary and profile structure. |
| Desktop, mobile, keyboard and navigation | All three real-browser journeys passed, including every navigation link, skip focus, 320-pixel layout and retained v1 navigation. |
| Resume, pseudonym conflict, replay, concurrency and immutable completion | Storage/integration checks passed, including original-cookie resume, duplicate-pseudonym conflict, exact replay and concurrent record/complete. |
| SQLite confinement and active/completed history | Per-connection physical confinement, exact schema/trigger SQL, coherent-rewrite rejection, contract-v3 fail-closed behavior and receipt reconstruction passed. |
| External-request boundary | Browser traffic remained loopback-only; no provider, credential, remote service or deployment was used. |
| Retained W04 runtime control | The complete suite passed 298 tests after its required nested local `uv` processes were permitted to read the existing host cache. Both 106-entry audit-only rosters remain equal and zero-read. |

## Exact reproduced commands and evidence

- `uv sync --locked --all-groups` — exit 0; 83 packages resolved and 82 audited.
- `UV_NO_CACHE=1 caffeinate -d uv run --no-sync pytest -q` over the seven W10 contract, unit and
  integration suites — exit 0; **93 passed**, one upstream TestClient deprecation warning.
- `UV_NO_CACHE=1 caffeinate -d uv run --no-sync pytest -q
  tests/e2e/test_w10_expert_study_playwright.py` — the initial sandbox run could not bind an
  ephemeral loopback socket; the authorised 127.0.0.1-only rerun exited 0 with **3 passed**.
- `UV_NO_CACHE=1 caffeinate -d uv run --no-sync pytest -q
  tests/unit/test_w04_wyscout_runtime_control.py` — the initial sandbox run was denied access to
  the existing host `uv` cache; the authorised local-cache rerun exited 0 with **298 passed in
  157.10 seconds**.
- `UV_NO_CACHE=1 caffeinate -d uv run --no-sync pytest -q` — complete repository gate exited 0
  with **3,091 passed**, one upstream TestClient deprecation warning, in 2,088.03 seconds
  (34 minutes 48 seconds).
- Production comparison reconstruction — exit 0; 318,525 canonical participant bytes, SHA-256
  `ebecc523f790264df4b1500ce5f9a2889c085607aa7858dfc776159eee4b3554`, comparison digest
  `e06544feff1fa7733dbcced337617f1b87502256702edf75b63800cc2bdde69b`, no forbidden key and no
  forbidden value.
- Read-only immutable SQLite counts — v1 formal has one authority, one retained approval and zero
  sessions, commands, judgements, revisions or completions; v1 pilot has one authority, one
  session, two commands, two judgements, two revisions and zero approvals or completions.
- Ports 8770 and 8771 were both closed at the decision point. No v2 pilot SQLite database existed.
- Repository-wide Ruff format/check, `mypy src/scouting scripts`, import contracts, Bandit,
  `git diff --check`, the local pre-push guard and local-only verification all passed. The W10
  phase verifier failed honestly because W10 remains REWORK, 08D has no human evidence, 08E/08F
  are unstarted and G-RW4 remains `INSUFFICIENT_EVIDENCE`.

The fresh bounded reviews retained alongside this decision are:

- `reports/reviews/W10/v2-bounded-rework-independent-review.md`
- `reports/reviews/W10/v2-bounded-confinement-independent-review.md`

Neither review is, or may be reused as, `W10-V2-INDEPENDENT-REVIEW-08F`.

## A4 disposition

The current implementation satisfies the bounded A4 gate. `W10-V2-STUDY-CONSOLE-08C-R1` is
accepted and only the separate v2 mechanics-pilot lane may proceed. The exact prepared A5
procedure is `reports/verification/W10/v2-mechanics-pilot.md`.

The remaining gate is human. At least two genuinely eligible football-domain reviewers must each
complete the five-task pilot and an explicit debrief. Their responses cannot be simulated,
automated, inferred, supplied by an AI system or counted toward G-RW4. Until that occurs, 08D is
READY rather than ACCEPTED, formal v2 remains disabled, and 08E/08F/A6/A7 remain prohibited.

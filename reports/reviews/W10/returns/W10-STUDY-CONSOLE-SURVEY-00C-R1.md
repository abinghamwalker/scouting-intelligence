# Subagent return

## Task

- task_id: `W10-STUDY-CONSOLE-SURVEY-00C`
- objective: Map reusable W08 study-console and W09 governed-workbench seams for a simple local W10 expert journey while excluding the dormant W08 workflow, separating pilot from formal evidence, and keeping expected results and candidate provenance out of participant views.

## Files changed

- `reports/reviews/W10/returns/W10-STUDY-CONSOLE-SURVEY-00C-R1.md`

## Summary

- Surveyed the accepted W08 study-console mechanics and W09 governed-workbench composition without modifying or reactivating either surface.
- Proposed a new W10-only operator console and participant runtime. The participant runtime receives only a frozen, blinded presentation bundle and an injected response store; it does not mount `/api/w09`, load a W09 report, or receive an evaluator answer/provenance bundle.
- Defined exact candidate implementation paths, routes, browser states, persistence/idempotency behaviour, leakage controls, and pilot/formal evidence separation for a later path-disjoint implementation packet against frozen W10 contracts.

## Reuse decision

### Reusable mechanics

| Concern | Accepted seam | W10 reuse | Required W10 correction or constraint |
| --- | --- | --- | --- |
| Loopback containment | `src/scouting/web/w09.py`: `_host_name`, `_loopback_host`, `local_only_policy`; `src/scouting/web/w08_study_console.py`: loopback-only participant server configuration and host rejection | Preserve IPv4, IPv6 and `localhost` loopback acceptance, explicit test-host opt-in, loopback bind, and rejection of non-loopback host headers | Implement equivalent public W10 helpers in the new W10 module; do not import W09 private underscore functions and do not import W08 modules |
| Browser security | W09 `_security_headers`; W08 `local_headers` | `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, restrictive CSP, `frame-ancestors 'none'`, same-origin connections and forms | Add `Permissions-Policy`; allow only the exact local script/style paths needed by W10; no inline answer key or external asset |
| Fresh local session | `StudyConsoleManager.start`, `_port`, `_port_available`, one active runtime, new mode-`0700` root, safe stop and lifespan shutdown | One fresh W10 participant runtime at a time, new unused session root, checked unprivileged port, explicit stop, cleared in-memory capability, mechanical receipt | Reimplement for W10 `create_w10_expert_study_app`; never call `create_w08_app`, never create W08 databases/personas, and persist resumable state before the runtime starts |
| Bounded local forms | W08 `form_values`, double-submit CSRF cookie/form token, strict content type and 64 KiB limit, bounded codes/text/counts | Use process-random CSRF tokens, `HttpOnly`, `SameSite=Strict` cookies, strict UTF-8 decoding, bounded request bytes and contract validation | Participant capability and CSRF values must not encode study mode, answer keys, candidate mapping, result IDs or evaluation state |
| Safe capture writes | W08 `_capture_path`, `_load_yaml_mapping`, `_atomic_write_capture` | Resolve under an injected non-root capture directory; reject traversal/symlinks; temporary write, flush, `fsync`, atomic replace; retain a digest receipt | Persist through a frozen W10 store contract. Do not copy the W08 YAML schema, task keys, attestations or gate fields |
| Honest evidence state | W08 keeps capture mechanics pending master reproduction and distinguishes pilot records | Completion is `COMPLETE_PENDING_EVALUATION`, never `PASS`; the browser provides no relevance verdict | W08's G-W08A/G-W08B counting and representative-user claims are obsolete and must not be reused |
| Accessible shell | W09 `workbench.html` and browser test: skip link, one header/nav/main/footer/h1, labelled controls, fieldsets/legends, details/summary, visible focus, status live region and 320 px no-overflow witness | Preserve the same semantic landmarks, keyboard order, focus transfer from skip link, labelled task controls, `aria-live` save status, details disclosure and responsive layout | Candidate order must remain meaningful to assistive technology without exposing model rank; announce neutral slot labels only |
| Safe DOM rendering | `apps/web/static/w09/workbench.js`: `textContent`, `createTextNode`, `replaceChildren`, same-origin `fetch`, `cache: "no-store"`, `credentials: "same-origin"`, `redirect: "error"` | Render all participant-controlled and candidate text with text nodes; classify loading/validation/conflict/unavailable states distinctly | No `innerHTML`, `insertAdjacentHTML`, `document.write`, browser storage, embedded JSON answer key, source-map leak or external request |
| Resume | W09 lists persisted experiments and W08 reloads capture status from disk | W10 reloads server-authoritative session/task state and returns the participant to the first incomplete task; already saved responses are represented by neutral “saved” state | Do not use `localStorage` or `sessionStorage`; they are neither authoritative nor an acceptable place for blinded fields or consent data |
| Idempotency and conflicts | `ResearchExperimentStore.save_experiment`, deterministic `research_replay_receipt_id`, immutable report addressing, exact-repeat acceptance and different-state conflict | Each start, response and completion command carries a client-generated command ID and expected session revision; exact retry returns the recorded result, command-ID reuse with different bytes or stale revision returns `409` | A completed formal capture is immutable. A correction requires an append-only pre-completion response revision defined by the frozen protocol, not overwrite of the final capture |
| Unavailable state | W09 returns `503` and mounts no research API when exact governed artifacts are missing, ambiguous or incompatible | W10 renders a neutral unavailable page and mounts no participant mutation routes unless exactly one compatible frozen presentation bundle and response-store authority load | Never substitute W08, W07, synthetic product data, a newest-found bundle, a pilot bundle for formal mode, or a different protocol digest |

### W08 concepts W10 must not inherit

W10 must not import `src/scouting/web/w08_study_console.py` or `src/scouting/web/w08.py`, mount `/w08`, call `create_w08_app`, or reuse W08 database/capture schemas. In particular it must exclude:

- analyst/scout/approver/admin personas, passwords, actor IDs, login, authentication, role switching and access-denial tasks;
- role briefs, brief submission/approval/revisions, candidate assignment, observations, disagreement amendments, shortlist transitions, meeting history, manual audit entry and export administration;
- T1–T7, W08-U/W08-P participant rosters, G-W08A/G-W08B/G4 counting, the `w08_pilot_progression_capture` record type and every staged-progression message;
- W08 evidence-origin or protected-W06 attestations as participant form work;
- runtime session expiry, two-tab workflow conflict and invalid-export recovery as study tasks;
- ephemeral synthetic accounts and synthetic candidate universes; and
- any claim that console completion, a pilot, or a participant action supplies gate acceptance.

This exclusion does not weaken or delete dormant W08 security tests. It prevents the W10 expert-relevance task from becoming a route back into the stopped workflow-first product.

## Exact W10 allocation proposal

### Frozen prerequisites owned outside the console packet

Before dispatching the console implementation, the protocol/evaluation owner should freeze contracts with distinct participant-safe and evaluator-only types. Names may be adjusted by that owner, but the boundary must be equivalent to:

- `ExpertStudyPresentationBundle`: protocol/stimulus identity plus ordered tasks containing only participant-visible prompts, neutral candidate slots and explicitly approved football evidence;
- `ExpertStudySessionView`: mode, de-identified session code, current state/revision, current task, neutral saved markers and participant-safe receipt state;
- `ExpertStudyResponseCommand` and `ExpertStudyCompletionCommand`: strict command IDs, session revision, task identity and rubric response;
- `ExpertStudyResponseStore`: prepare/load/apply/complete methods with exact-repeat idempotency and stale/different conflict; and
- evaluator-only `ExpertStudyEvaluationBundle`: expected judgements, candidate-to-source mapping, W09 experiment/query/result IDs and digests, method/arm, rank/score, randomisation seed and gate thresholds.

The console packet should consume those frozen interfaces but own none of their metric or evidence semantics. The evaluator-only bundle must not be accepted by the participant-app factory at all.

### Candidate implementation paths

Allocate these new paths together to one W10 console implementer; they do not require an edit to W08 or W09:

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

The factory boundary should be explicit:

```text
create_w10_expert_study_console(
    roster,
    presentation_store,
    response_store,
    study_parent,
    console_base_url,
    allow_test_host=False,
)
```

Starting a session constructs `create_w10_expert_participant_app(presentation, session_view, response_store)` and binds it to `127.0.0.1`. The participant factory accepts no W09 runtime/router, W09 report store, evaluator bundle, expected-result mapping or W08 app.

### Operator-console routes

The operator console is mechanical preparation only and must not display expected results, candidate provenance or aggregate relevance outcomes:

| Method | Route | Behaviour |
| --- | --- | --- |
| `GET` | `/` | Dashboard of injected de-identified roster slots and neutral states |
| `GET` | `/sessions/{session_code}` | One slot's mode, consent/qualification readiness, runtime state and mechanical receipt |
| `POST` | `/sessions/{session_code}/prepare` | Records pilot boundary acknowledgement, or formal qualification/consent confirmation, using bounded CSRF form data |
| `POST` | `/sessions/{session_code}/start` | Starts exactly one new/resumable W10 participant runtime from the mode-compatible frozen presentation bundle |
| `POST` | `/sessions/{session_code}/stop` | Stops the runtime safely, clears its browser capability, closes storage and records a mechanical capture digest/receipt |

There is deliberately no operator route that returns the evaluator bundle, expected results, per-task correctness, metric status or G-RW4 verdict.

### Participant-runtime routes

The participant runtime is on a separate checked loopback port and exposes only the following same-origin surface:

| Method | Route | Response and state rule |
| --- | --- | --- |
| `GET` | `/` | Redirects to `/w10` without adding study facts to the URL |
| `GET` | `/w10` | Renders the current participant-safe session view; resumes at the first incomplete task |
| `GET` | `/api/w10/session` | Returns only `ExpertStudySessionView`; no evaluator fields or arbitrary record lookup |
| `POST` | `/api/w10/session/start` | Idempotently moves `READY_TO_START` to `IN_PROGRESS`; exact retry is safe |
| `POST` | `/api/w10/session/tasks/{task_id}/responses` | Validates that the task is the current frozen task and applies one command/revision atomically |
| `POST` | `/api/w10/session/complete` | Requires all protocol-required responses, seals the capture and returns a neutral participant-safe receipt |

There is no `/api/w09` router, player search, free-form query, experiment/report endpoint, evaluator endpoint, arbitrary session-code endpoint, candidate-source lookup or aggregate-result endpoint in the participant runtime.

### Participant journey and UI states

The browser journey is intentionally shorter than W08:

1. **Boundary and consent:** explain historical evidence, voluntary participation, de-identification and non-claims; formal mode requires protocol-defined expert qualification and consent before runtime start.
2. **Start or resume:** show mode as “development pilot” or “formal frozen study” and the protocol/presentation digest in a non-clickable abbreviated receipt only if the protocol permits it; never show an answer key or model/result identity.
3. **Assess frozen tasks:** show one frozen prompt at a time, neutral candidate slots and only approved evidence; collect the frozen rubric response and optional bounded de-identified note.
4. **Review:** show response completeness and neutral task labels. If the frozen protocol allows correction, append a revision before final sealing; otherwise retain the submitted response unchanged.
5. **Complete:** seal once and show `Complete — pending independent evaluation` plus a response receipt. Do not show score, expected answer, metric, pass/fail, arm, rank or gate status.

Use these exact state classes in HTML/API tests:

```text
UNAVAILABLE
AWAITING_PREPARATION
READY_TO_START
IN_PROGRESS
SAVING
SAVED
VALIDATION_ERROR
CONFLICT
COMPLETE_PENDING_EVALUATION
STOPPED_WITH_RECEIPT
```

`UNAVAILABLE`, `VALIDATION_ERROR` and `CONFLICT` are distinct, visible and announced. A refresh during `IN_PROGRESS` must reconstruct the same task and response-completeness state from the server store. Completion and stop are idempotent exact retries; neither can reopen or mutate a sealed capture.

## Participant-view confidentiality contract

The strongest reusable lesson from W09 is same-process authority consistency; the necessary W10 change is data minimisation. A participant browser must never receive, including in HTML, DOM attributes, bootstrap JSON, JavaScript, CSS, URLs, cookies, response bodies, headers, error text, source maps or accessibility-only text:

- expected relevance, pair preference, known-comparable label or any other expected result;
- candidate player/grain/source identifiers unless a frozen protocol explicitly declares one as visible stimulus rather than provenance;
- W09 query, result, comparison, experiment or replay IDs/digests;
- raw rank, score/distance, feature contribution rank, retrieval method/model/index/arm or baseline/challenger assignment;
- candidate-to-W09-row mapping, original order, shuffle seed, counterbalancing cell or provenance digest;
- evaluation denominator, threshold, aggregate, per-participant correctness, `PASS`/`FAIL`/`INSUFFICIENT_EVIDENCE`, one-use gate state or protected-label availability; or
- other participants' responses, notes, session states or receipts.

Default candidate presentation should therefore use neutral labels such as `Candidate A` and `Candidate B`, protocol-approved football evidence, and a server-prepared order. If player identity or context is scientifically necessary, the protocol must enumerate that field in the presentation contract; it does not make source arm, rank, score, mapping or expected judgement visible.

The blinded presentation bundle and evaluator bundle must be separate files/roots with different types and digests. The web process reads only the presentation bundle. Evaluation occurs after capture through a separate master/evaluator invocation. This is stronger than filtering a combined object in a Jinja template because browser-route mistakes cannot serialize bytes the process never loaded.

Required leakage witnesses for the implementation packet:

- recursively inspect every participant HTML/JSON response and assert forbidden evaluator keys/known answer values are absent;
- assert the participant app route table contains no `/api/w09`, evaluator, report or arbitrary record route;
- inspect static assets for embedded expected values, mappings, candidate IDs, `innerHTML`, browser storage and external URLs;
- use a browser request listener to prove every request remains on the participant loopback origin;
- exercise validation, conflict, unavailable and exception paths and repeat the same absence assertions;
- prove the app factory rejects an evaluator bundle or a presentation whose mode/digest differs from the prepared session; and
- prove missing/ambiguous/incompatible presentation authority produces `503` with mutation routes absent, never a synthetic or alternate fallback.

## Pilot/formal evidence separation

| Control | Development pilot | Formal expert study |
| --- | --- | --- |
| Session code | Protocol roster entry with `W10-P...` class | Distinct protocol roster entry with `W10-F...` class |
| Record type | `w10_expert_relevance_pilot_capture` | `w10_expert_relevance_formal_capture` |
| Purpose | Mechanics, wording, accessibility, timing, resume and leakage rehearsal | Frozen G-RW4 candidate evidence only |
| Participant | May be an authorised rehearsal operator if protocol permits; never counted as expert evidence | Protocol-qualified football-domain expert with recorded consent |
| Storage root/table partition | `.../w10/study/pilot/<presentation_digest>/...` | `.../w10/study/formal/<presentation_digest>/...` |
| Bundle state | Draft or pilot-frozen presentation | Exact master-frozen protocol and presentation digest after pilot review |
| Metrics/gate inclusion | Hard exclusion from formal denominators and all G-RW4 claims | Eligible only when complete, qualified, consented, unique and exact-digest compatible |
| Mutation | Pilot finding may cause a new protocol/presentation digest | No silent change after first formal capture; changed protocol creates a new formal study version |
| Browser completion text | “Pilot complete — not formal relevance evidence” | “Complete — pending independent evaluation” |

Mode is immutable after preparation. Pilot data cannot be copied, relabelled or promoted into formal storage. Automated fixtures use a third `TEST_ONLY` authority/root and can never create either record type. The formal aggregator must select exact formal record type and frozen digests positively rather than exclude pilot rows by convention. Mixed digests, duplicate participant identities, incomplete consent/qualification or a prior pilot code fail closed before evaluation.

The console itself does not decide G-RW4. It records blinded responses and mechanical receipts. Protocol metrics, denominator ordering, one-use evaluation, negative result retention and final `PASS`/`FAIL`/`INSUFFICIENT_EVIDENCE` are owned by the W10 evaluation/protocol packets and occur outside every participant route.

## Proposed focused verification for the implementation packet

```text
uv run pytest -q tests/unit/test_w10_expert_study_web.py
uv run pytest -q tests/integration/test_w10_expert_study_console.py
uv run pytest -q tests/e2e/test_w10_expert_study_playwright.py
uv run ruff format --check src/scouting/web/w10_expert_study.py services/api/w10_study_main.py tests/unit/test_w10_expert_study_web.py tests/integration/test_w10_expert_study_console.py tests/e2e/test_w10_expert_study_playwright.py
uv run ruff check src/scouting/web/w10_expert_study.py services/api/w10_study_main.py tests/unit/test_w10_expert_study_web.py tests/integration/test_w10_expert_study_console.py tests/e2e/test_w10_expert_study_playwright.py
```

The master should add a source inspection asserting no import of `scouting.web.w08`, `scouting.auth`, `scouting.workflow`, `scouting.audit`, W08 templates/static assets, or `create_research_router`, and no participant-app reference to the evaluator-only contract.

## Tests run

- command: `uv run pytest -q tests/integration/test_w08_study_console.py tests/unit/test_w09_research_web.py`
  - exit status: `0`
  - result: `10 passed, 1 warning in 3.73s`; the warning is the existing FastAPI TestClient `httpx`/`httpx2` Starlette deprecation warning.
- command: `test -s reports/reviews/W10/returns/W10-STUDY-CONSOLE-SURVEY-00C-R1.md`
  - exit status: `0`
  - result: the required return artifact exists and is non-empty.

## Artifacts/evidence

- `reports/reviews/W10/returns/W10-STUDY-CONSOLE-SURVEY-00C-R1.md` — W10 reuse, exclusion, allocation, route, state and separation survey.
- Evidence source identifiers: W08 `StudyConsoleManager`, `form_values`, `_atomic_write_capture`; W09 `create_w09_app`, `_loopback_host`, `_security_headers`; W09 `ResearchExperimentStore`; W09 workbench template, script and browser witnesses.

## Risks

- The W10 protocol, response schema, expert roster, visible stimulus fields and metric thresholds are not yet frozen. The console must not invent them; its implementation packet should start only after the protocol/evaluation owner publishes exact contracts and presentation/evaluator separation.
- A single combined presentation/evaluator payload would create a high-severity participant leakage risk even if templates currently omit private fields. Keep the bytes and types physically separate and do not load the evaluator bundle in the web process.
- Reusing the W09 app/router directly would disclose ranks, scores, result identities, version pins and provenance; reusing the W08 app/console directly would reactivate dormant workflow/auth/persona concepts. Both are explicitly excluded.
- Loopback limits network exposure but is not a participant-blinding control by itself. Route minimisation, capability/CSRF handling, separate bundles and response-body witnesses remain required.

## Follow-up items

- Freeze W10 participant-safe presentation/session/response contracts and the evaluator-only answer/provenance bundle as separate authorities.
- Freeze protocol-defined visible stimulus fields, pilot roster, formal expert roster, consent/qualification rule, correction policy and presentation digest before console implementation.
- Dispatch the proposed path-disjoint W10 console implementation packet only after those prerequisites; retain metric/gate computation outside its routes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

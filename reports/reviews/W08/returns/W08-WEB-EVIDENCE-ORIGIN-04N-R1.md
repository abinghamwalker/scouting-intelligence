# W08-WEB-EVIDENCE-ORIGIN-04N — R1 return

## Objective and invariant

Correct the independent-review synthetic-as-human P1. Every `create_w08_app`
constructor now requires an explicit, server-controlled `WorkflowEvidenceOrigin`.
Forms, headers, and seeded persona identities cannot select or override that value.

## Changed files

- `src/scouting/web/w08.py`
- `services/api/w08_main.py`
- `scripts/run_w08_study.py`
- `tests/integration/test_w08_local_workflow_app.py`
- `tests/security/test_w08_web_security.py`
- `tests/e2e/test_w08_local_workflow_playwright.py`
- `tests/integration/test_w08_study_harness.py`
- `reports/reviews/W08/returns/W08-WEB-EVIDENCE-ORIGIN-04N-R1.md`

## Implementation and constructor map

`create_w08_app` has a required keyword-only `evidence_origin` parameter. It is
captured in the application closure/state and is used only for newly created
comments and observations. The amendment route continues to read and preserve the
persisted origin; it never re-selects it from the request.

All constructor calls are explicit:

- `services/api/w08_main.py`: `human_entered_local`.
- `scripts/run_w08_study.py:serve`: `human_entered_local`.
- all calls in `tests/integration/test_w08_local_workflow_app.py`: `synthetic_automated_test`.
- all calls in `tests/security/test_w08_web_security.py`: `synthetic_automated_test`.
- the Playwright loopback fixture: `synthetic_automated_test`.
- all ordinary study-harness mechanics: `synthetic_automated_test`.
- the single separately named human-mode mechanical test: `human_entered_local`.

## Origin witnesses

### Synthetic automated runtime

`test_synthetic_automated_shortlist_assignment_observation_and_conflict` submits
both an observation and a comment with an attacker-supplied
`evidence_origin=human_entered_local`. It establishes all of the following:

- database rows for both observation versions and all comments are
  `synthetic_automated_test`;
- rendered history displays `synthetic_automated_test`;
- the two observation audit `after_digest` values are recomputed from the strict
  persisted `ScoutObservationVersion` contracts (which include evidence origin) and
  match exactly;
- an authorised local export has
  `workflow_action_origins == ["synthetic_automated_test"]` even when its form
  submits a human origin.

### Human-mode mechanical runtime

`test_human_mode_route_origin_is_server_selected_mechanics_only` creates a
`human_entered_local` app, then sends an observation route form that explicitly
asks for `synthetic_automated_test`. This is an automated mechanical test using
synthetic setup accounts, not a participant, consent, judgement, task outcome, or
representative-user record. It establishes:

- the observation database row is `human_entered_local`;
- its rendered entry history is `human_entered_local`;
- an audit event exists with a 64-character after digest;
- the resulting local export has
  `workflow_action_origins == ["human_entered_local"]` despite the form attempting
  the synthetic value.

The study harness output now states that its accounts are synthetic setup accounts,
that the runtime label is mechanical provenance only, and that it is not
representative-user evidence.

## Focused verification

Final command, exit 0:

```text
uv run ruff format --check src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/e2e/test_w08_local_workflow_playwright.py tests/integration/test_w08_study_harness.py
uv run ruff check src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/e2e/test_w08_local_workflow_playwright.py tests/integration/test_w08_study_harness.py
uv run mypy src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py
uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/e2e/test_w08_local_workflow_playwright.py tests/integration/test_w08_study_harness.py tests/integration/test_w08_evidence_export.py
uv run bandit -q src/scouting/web/w08.py services/api/w08_main.py scripts/run_w08_study.py
```

Results: format check passed (7 files already formatted); Ruff passed; mypy passed
for 3 source files; pytest **27 passed** with one third-party Starlette TestClient
deprecation warning; Bandit passed with no findings.

## Residual risks and follow-up

`human_entered_local` is a provenance mode, not proof of a representative user,
consent, scout judgement, model quality, or gate satisfaction. The five-person
moderated study remains required. A fresh independent review must verify this
correction alongside the other retained W08 P1 corrections.

## Scope confirmation

No Git command or Git mutation; no dependency or lock changes; no protected W06
output access or reconstruction; no external/network/provider/model activity; no
participant/result creation; and no edits outside this packet's allowed paths.

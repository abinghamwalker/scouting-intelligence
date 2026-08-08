# Subagent return

## Task

- task_id: W03-VERTICAL-01
- objective: Implement the authenticated, deny-by-default, locally instrumented
  synthetic role-brief-to-audit vertical journey without real data or a model.

## Files changed

- src/scouting/policy/__init__.py
- src/scouting/policy/authentication.py
- src/scouting/policy/authorization.py
- src/scouting/policy/eligibility.py
- src/scouting/serving/__init__.py
- src/scouting/serving/synthetic.py
- src/scouting/workflow/__init__.py
- src/scouting/workflow/service.py
- src/scouting/audit/__init__.py
- src/scouting/audit/writer.py
- src/scouting/operations/__init__.py
- src/scouting/operations/telemetry.py
- src/scouting/web/__init__.py
- src/scouting/web/app.py
- services/api/__init__.py
- services/api/main.py
- services/worker/__init__.py
- services/worker/main.py
- apps/web/templates/w03_journey.html
- tests/e2e/test_w03_vertical_journey.py
- tests/integration/test_w03_local_telemetry.py
- tests/security/test_application_authorization.py
- reports/reviews/W03/returns/W03-VERTICAL-01-R1.md

## Summary

- Injected synthetic session accounts retain only HMAC-SHA256 token digests, compare
  every injected digest with `hmac.compare_digest`, return generic authentication
  failures, and never log credentials or request payloads.
- The accepted authorization and data-rights YAML files are executable. Unknown actor,
  role, action, context, owner/visibility, and cross-tenant cases deny by default.
  W03 export remains denied even where the actor's role grants an export action.
- Serving loads only a file named `domain.json` from the development partition during
  composition, verifies its manifest digest and classification, applies strict-before
  availability and identity admission, and constructs the contract-valid deterministic
  result and non-predictive explanation. Missing model/index evidence returns a labelled
  unavailable outcome. Runtime source contains no `expected_retrieval.json` reference
  or read.
- `ApplicationDatabase.transaction` is the only workflow database boundary. It runs
  `SET LOCAL ROLE scouting_app`, sets `scouting.tenant_id` transaction-locally, and
  verifies both values before any domain table access. Workflow code has no owner
  connection API.
- Role brief, retrieval/candidate, shortlist/entry, and all four audit events share one
  transaction. An audit writer failure rolls the material write back. Audit rows are
  insert-only through the existing schema.
- The FastAPI factory exposes local health/readiness, authenticated HTML, and the JSON
  journey without opening a listener. The worker readiness unit starts no listener.
  In-process structured logs, traces, and counters have a key allowlist, bounded record
  retention, and no exporter.
- Tests use the development expected output only as assertion data. Owner access is
  limited to idempotent test prerequisite seeding; every application-backed domain read
  and write proves the central app-role/tenant transaction boundary.

## Tests run

- command: `SCOUTING_DATABASE_URL='<redacted master-supplied loopback URL>' uv run pytest -q tests/e2e/test_w03_vertical_journey.py tests/integration/test_w03_local_telemetry.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: 13 passed; one upstream Starlette/httpx deprecation warning. A prior bounded
    run reported 10 passed and 2 setup errors because the reachable database had no
    tables. The master applied and independently confirmed accepted revision
    `0001_foundation`. A subsequent run exposed one HTTP strict-wire adapter failure
    (11 passed, 1 failed), which was corrected without relaxing contracts.
- command: `uv run ruff format --check src/scouting/policy src/scouting/serving src/scouting/workflow src/scouting/audit src/scouting/operations src/scouting/web services/api services/worker tests/e2e/test_w03_vertical_journey.py tests/integration/test_w03_local_telemetry.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: 21 files already formatted.
- command: `uv run ruff check src/scouting/policy src/scouting/serving src/scouting/workflow src/scouting/audit src/scouting/operations src/scouting/web services/api services/worker tests/e2e/test_w03_vertical_journey.py tests/integration/test_w03_local_telemetry.py tests/security/test_application_authorization.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run mypy src/scouting/policy src/scouting/serving src/scouting/workflow src/scouting/audit src/scouting/operations src/scouting/web services/api services/worker`
  - exit status: 0
  - result: no issues found in 18 source files.
- command: `uv run bandit -q -r src/scouting/policy src/scouting/serving src/scouting/workflow src/scouting/audit src/scouting/operations src/scouting/web services/api services/worker`
  - exit status: 0
  - result: no findings.
- command: `rg -n "expected_retrieval\\.json|protected" src/scouting/policy src/scouting/serving src/scouting/workflow src/scouting/audit src/scouting/operations src/scouting/web services/api services/worker apps/web/templates/w03_journey.html`
  - exit status: 0
  - result: only the serving guard rejecting paths containing `protected`; no runtime
    expected-output filename or read path.

## Artifacts/evidence

- reports/reviews/W03/returns/W03-VERTICAL-01-R1.md
- tests/e2e/test_w03_vertical_journey.py
- tests/integration/test_w03_local_telemetry.py
- tests/security/test_application_authorization.py
- fixture ID: `w03-synthetic-development-v1`
- domain manifest digest:
  `03972808bd6628dd4ffb66a975108bb15f649a0b778e493c85874ef107953e2a`
- authorization policy ID: `w03-authorization-v1`
- data-rights policy ID: `w03-synthetic-data-rights-v1`
- database application role verified by response and direct transaction:
  `scouting_app`
- retrieval run ID: `e0000000-0000-4000-8000-000000000101`
- model/index seam IDs: `w03-synthetic-deterministic-retrieval-v1`,
  `w03-development-index-v1`

## Risks

- Evidence remains deterministic W03 synthetic seam evidence only. It makes no model
  quality, expert relevance, usability, pilot, security-assurance, or recruitment
  outcome claim.
- The local test database retains append-only synthetic audit evidence by design.
- TestClient emits an upstream Starlette/httpx deprecation warning. Resolving it would
  require a dependency decision outside this packet; it does not affect the passing
  journey.

## Follow-up items

- Master independently review every changed file, rerun the packet checks, and decide
  acceptance or bounded rework.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed.

# W09-RESEARCH-UI-05A R1 return

## Outcome

Implemented the local-only W09 historical-player research workbench over the accepted injected
API and serving boundaries. The page provides the complete governed journey from dataset
authority through query, ranked explanations, comparison, saved deterministic report and exact
replay. The packet's exact checks pass.

Production discovery remains fail closed: it discovers exactly one accepted feature manifest,
loads only the compatible index from the fixed governed root, and renders an honest unavailable
page when either authority is absent or incompatible. It never selects a newest artifact,
substitutes a synthetic population, or mounts W07/W08 as the core path.

## Files changed

- `src/scouting/web/w09.py`
- `services/api/w09_main.py`
- `apps/web/templates/w09/workbench.html`
- `apps/web/static/w09/workbench.css`
- `apps/web/static/w09/workbench.js`
- `tests/unit/test_w09_research_web.py`
- `tests/e2e/test_w09_research_workbench_playwright.py`
- `reports/reviews/W09/returns/W09-RESEARCH-UI-05A-R1.md`

## Delivered

- `create_w09_app` is a strict injected presentation composition factory. Available mode accepts
  one exact `ResearchApiRuntime` and its exact `ResearchServingService`; unavailable mode accepts
  neither and requires one explicit trimmed reason.
- `services/api/w09_main.py` owns production artifact discovery and loading, dataset construction,
  exact pin composition, SQLite experiment state and the guarded local report root. This keeps
  modeling and storage assembly out of the web presentation layer.
- Production composition uses `discover_feature_matrix_manifest`, `load_feature_matrix` and
  `load_research_index` with the accepted fixed roots and validates the resulting authority again
  through `ResearchServingService` and `ResearchApiRuntime`.
- The bootstrap reconciles the retained source catalogue of 3,603 players and describes the
  recorded 1,826 matches, 3,071,395 actions and 142 teams separately from eligible matrix rows and
  eligible unique players. No assumption equates source and eligibility counts.
- `/` and `/w09` expose one responsive, keyboard-navigable workspace with dataset rights,
  attribution, versions, coverage and limitations; governed real-player search; exemplar and
  weighted-profile modes; robust-scaled weighted distance and cosine methods; feature weights;
  eligibility filters; ranked candidates; contribution, contrast and missingness explanations;
  exact comparison; experiment save; JSON or HTML report; and replay receipt state.
- Replay rendering distinguishes reproduced, incompatible-pins and deterministic-result-mismatch
  receipts. Request failures distinguish loading, empty, validation, stale/conflict and unavailable
  states.
- Browser-side canonical query and comparison digests reproduce the accepted Python canonical
  JSON encoding, including finite float formatting at fixed/scientific thresholds. Real-browser
  tests submit `1e-5`, `1e-7` and `1e16` values successfully against the strict API.
- All dynamic and untrusted content is built with `textContent`, `createTextNode` and DOM nodes.
  The page makes same-origin `/api/w09` requests only and has no HTML-injection sink.
- Every response receives `no-store`, `no-referrer`, `nosniff`, a restrictive permissions policy
  and a CSP limited to same-origin static assets/API. Non-loopback hosts are rejected.
- The claim boundary remains historical resemblance research only and explicitly excludes future
  performance, recruitment usefulness, value, availability and squad-fit claims while G-RW4 is
  absent.

## Evidence

Unit tests prove missing, ambiguous and incompatible artifact authorities fail closed; API/store
composition conflicts remain unavailable; runtime/serving injection must be exact; loopback and
response security policies cover failure surfaces; and production code has no synthetic, legacy,
provider-runtime or web-to-modeling import seam.

Real-browser tests use only explicitly synthetic, temporary governed fixtures. A real headless
Chrome instance and loopback Uvicorn process prove both query modes and both retrieval methods,
real-player search, explanations, comparison, JSON and HTML reports, exact replay, replay mismatch
states, scientific-notation digest compatibility, keyboard focus/landmarks, 320-pixel no-overflow,
same-origin request containment, and distinct empty/validation/conflict/unavailable states.

## Exact checks

```text
caffeinate -dimsu uv run ruff format --check src/scouting/web/w09.py services/api/w09_main.py tests/unit/test_w09_research_web.py tests/e2e/test_w09_research_workbench_playwright.py
4 files already formatted

caffeinate -dimsu uv run ruff check src/scouting/web/w09.py services/api/w09_main.py tests/unit/test_w09_research_web.py tests/e2e/test_w09_research_workbench_playwright.py
All checks passed!

caffeinate -dimsu uv run mypy src/scouting/web/w09.py services/api/w09_main.py
Success: no issues found in 2 source files

caffeinate -dimsu uv run pytest -q tests/unit/test_w09_research_web.py tests/e2e/test_w09_research_workbench_playwright.py
9 passed, 1 warning in 9.59s

caffeinate -dimsu uv run bandit -q -r src/scouting/web/w09.py services/api/w09_main.py
passed (no findings)
```

The sole warning is the environment's existing Starlette `TestClient`/`httpx` deprecation warning.
No dependency change was made because dependencies are outside this packet.

## Boundaries and residual follow-up

- No production feature matrix or index was generated by this packet. The production page remains
  honestly unavailable until the master rebuild publishes exactly one accepted compatible pair.
- Production artifact identities are discovered dynamically and rendered from injected public
  pins. No current matrix/index version or digest is hard-coded, so the independent-review rebuild
  can replace them without a UI change.
- Browser fixtures are synthetic only because the packet permits synthetic automated test
  fixtures. Production discovery cannot reach those paths, and they are never presented as
  retrieval-quality evidence.
- The workbench is local and in-process. No provider access, network service, deployment, cloud
  resource, authentication role journey, manual audit workflow or dependency change was added.
- G-RW4 is absent. Nothing in this workbench supports a positive football-relevance, outcome or
  recruitment-usefulness claim.

## Scope confirmation

- No Git operations: confirmed.
- No orchestration-control, dependency/lock, shared contract/API/serving/storage/reporting,
  production artifact or provider changes: confirmed.
- No edits outside the packet's allowed paths: confirmed.

# W09-RESEARCH-API-04D R1 return

## Outcome

Implemented the strict, local-only W09 research API boundary. The packet is complete and its exact checks pass.

The production surface is dependency injected and does not construct an application, discover artifacts, generate data, contact a provider, or import dormant W03/W05/W07/W08 runtime paths.

## Delivered

- `ResearchApiRuntime` freshly validates and binds one exact `ResearchDatasetDescriptor`, `ResearchServingService`, `ResearchExperimentStore`, retained attribution, non-empty rights limitations, and injected UTC clock.
- `create_research_router` returns an isolated FastAPI `APIRouter` with prefix `/api/w09`.
- Dataset and governed-matrix player endpoints:
  - `GET /datasets`
  - `GET /players`, with bounded deterministic name, position, competition, offset and limit filtering.
- Retrieval and comparison endpoints:
  - `POST /queries`
  - `GET /results/{result_id}`
  - `POST /comparisons`
- Immutable experiment/report/replay endpoints:
  - `POST /experiments`
  - `GET /experiments`
  - `GET /experiments/{experiment_id}`
  - `GET /experiments/{experiment_id}/report`
  - `POST /experiments/{experiment_id}/replay`
- Strict local `SaveResearchExperimentRequest`, `ResearchPlayerSummary`, and `ResearchPlayerSearchResponse` contracts.
- Strict JSON-mode body validation for accepted shared query/comparison contracts, preserving strict UUID, tuple, enum and UTC semantics at the HTTP boundary.
- Thread-safe immutable result and comparison caches. Repeated semantic query execution returns the first exact immutable cached result; identifier/digest conflicts fail closed.
- Save requests can bind only an exact cached result and optional paired comparison ID/digest. Reports are rendered content-addressably and persisted only through `ResearchExperimentStore`.
- Replay uses the exact saved request and pins. It appends deterministic contract-valid receipts for reproduced, incompatible-pins and deterministic-result-mismatch outcomes without rewriting saved state. Repeated replay returns the first exact receipt for the same deterministic identity.
- Exact saved report bytes are returned with `application/json` or `text/html; charset=utf-8`.
- HTTP classification is explicit: malformed/input errors `422`, absent immutable authorities `404`, and stale/incompatible/integrity conflicts `409`.

## Evidence

Integration tests use only bounded test-fixture matrix/index authorities. They cover every route, strict body rejection, stale pins, unknown IDs, bounded player search, synthetic-population denial, exact report bytes/media type, save and replay idempotency, incompatible and mismatch replay receipts, and concurrent result-cache access.

The static import/call tripwire confirms that production API code does not import raw providers, provider adapters, web/application composition, auth, audit, workflow, or legacy retrieval runtimes.

## Exact checks

```text
caffeinate -dimsu uv run ruff format --check src/scouting/api tests/unit/test_w09_research_api.py tests/integration/test_w09_research_api_integration.py
4 files already formatted

caffeinate -dimsu uv run ruff check src/scouting/api tests/unit/test_w09_research_api.py tests/integration/test_w09_research_api_integration.py
All checks passed!

caffeinate -dimsu uv run mypy src/scouting/api
Success: no issues found in 2 source files

caffeinate -dimsu uv run pytest -q tests/unit/test_w09_research_api.py tests/integration/test_w09_research_api_integration.py tests/unit/test_w09_research_serving.py tests/integration/test_w09_research_storage.py
30 passed, 1 warning in 1.25s

caffeinate -dimsu uv run bandit -q -r src/scouting/api
passed (no findings)
```

The sole warning is the environment's existing Starlette `TestClient`/`httpx` deprecation warning. No dependency change was made because dependency changes are prohibited by this packet.

## Boundaries retained

- Historical 2017/18 resemblance research only.
- No G-RW4 football-relevance, outcome, value, availability, fit, recruitment-usefulness or current-market claim.
- Player search is exclusively over the serving authority's immutable governed matrix rows and rejects any row contract carrying synthetic product data.
- No authentication, fictional roles, manual audit workflow, provider access, network service, deployment, dependency change, or production artifact discovery was introduced.
- No production artifacts were generated.

## Stop conditions

None encountered. The required public immutable `ResearchServingService.matrix_rows` authority was supplied by the accepted 04C serving boundary and consumed without private-state access or serving edits.

# W07 application independent review R1

## Decision

**PASS**

The integrated W07 local evidence application satisfies the reviewed G-W07 boundary. No
P0 or P1 finding was identified. One P2 packet-maintenance finding does not affect the
application, its executable evidence, or the accepted W05 parity result.

Finding counts: **P0 0 · P1 0 · P2 1**.

## Findings

### W07-IR-R1-P2-STALE-PARITY-READ-PATH — P2

The packet requires `reports/verification/W05/m0-serving-parity-report.json` at
`orchestration/task_packets/W07-INDEPENDENT-REVIEW-05-R1.yaml:26`, but that path is
absent. The available accepted equivalent is
`reports/verification/W05/training-serving-parity-report.md`: lines 1-9 identify it as
the W05 training-serving parity record, provide the accepted result and lineage
identities, state the direct/single/batch parity and artifact-immutability result, and
retain the resemblance-only claim boundary. This is documentation-routing debt only:
the packet's required W05 serving and retrieval parity tests passed independently.

Smallest correction: update the read-first entry to the existing accepted Markdown
record, or add the intended reviewed JSON record under master ownership.

## Independent review evidence

### Single accepted scoring path

- `src/scouting/web/w07.py:32-37` imports only the shared W05 core and public
  `serve_m0_request` / `serve_m0_batch` entry points.
- Retrieval calls only `serve_m0_request` at `src/scouting/web/w07.py:337-365`;
  comparison calls only `serve_m0_batch` at `src/scouting/web/w07.py:367-391`.
- `src/scouting/serving/m0.py:245-304` loads the accepted artifact and calls its loaded
  scorer; `src/scouting/serving/m0.py:913-922` proves the public single and batch
  functions are thin paths through that same core.
- UI composition at `src/scouting/web/w07.py:297-335` only zips and labels returned
  evidence. It contains no score, distance, contribution, ranking, or confidence
  arithmetic and defines no second scorer.
- `tests/integration/test_w07_local_evidence_app.py:109-135` spies on both public paths
  and `LoadedM0Artifact.score`, proves direct/batch byte and digest identity, and proves
  the four accepted artifact files remain unchanged.

### Evidence honesty and complete result authority

- The alert banner at `apps/web/templates/w07/_authority.html:10-15` presents
  `NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE` as a high-priority evidence boundary on
  every page. The evidence centre repeats the missing-expert boundary and unopened
  protected-output state at `apps/web/templates/w07/evidence.html:5-9`; neither can
  reasonably read as positive validation.
- `src/scouting/web/w07.py:173-217` fixes source/evidence class, model and index,
  artifact and manifest, registry and schema, taxonomy, configuration, populations,
  window and cutoff, confidence, LIMITED applicability, limitations, lineage, accepted
  result identity, W04 counts/SUPPRESSED measures, and the W06 NO_GO authority.
- `apps/web/templates/w07/_authority.html:18-40` renders those identities on all
  result pages. Per-result authority replaces the accepted fallback with the actual
  result digest, cutoff, and dependency lineage at `src/scouting/web/w07.py:321-335`.
- `apps/web/templates/w07/result.html:9-16` renders every returned row's rank,
  distance, confidence, applicability, limitations, reasons, dimensions, explanation
  inputs/contributions, and exact W04 counts while retaining `SUPPRESSED` minutes,
  rates, and per-90.
- `apps/web/templates/w07/_authority.html:35-39` keeps `resemblance_only`,
  `synthetic_development_only`, `LIMITED`, `no_recommendation_evidence`, cutoff,
  confidence, and lineage explicit. The evidence centre keeps the same boundary at
  `apps/web/templates/w07/evidence.html:7-9`.

### Routes, failure closure, accessibility, and local-only operation

- Search is bounded to the accepted 18-record catalogue and closed position vocabulary
  at `src/scouting/web/w07.py:251-278`. Player, retrieval, and comparison identities
  reject malformed or unknown UUIDs before serving at `src/scouting/web/w07.py:280-295`
  and `src/scouting/web/w07.py:349-391`; a comparison candidate must also occur in the
  returned batch rows at lines 376-382.
- Closed states use the `W07State` enum declared at `src/scouting/web/w07.py:48-53`;
  unknown state names return 404 at `src/scouting/web/w07.py:411-417`. The state
  template distinguishes loading, empty, unavailable, error, and no-go semantics at
  `apps/web/templates/w07/state.html:5-9`.
- Every response receives self-only CSP, no-store, and no-referrer policy at
  `src/scouting/web/w07.py:219-228`. Static serving is a bounded local mount at
  `src/scouting/web/w07.py:155-160`; templates contain no scripts, webfonts, external
  URLs, or external assets.
- `apps/web/templates/w07/base.html:10-32` supplies skip link, banner, navigation, main,
  and footer landmarks. Search labels and scoped/captioned tables appear at
  `apps/web/templates/w07/search.html:5-18`; the result evidence tables are captioned
  and scoped at `apps/web/templates/w07/result.html:11-14`.
- Keyboard focus, narrow layouts, scroll-contained tables, reduced motion, and print
  behaviour are implemented at `apps/web/static/w07/app.css:2-11`. The real-browser
  tests exercise 1440x900, 390x844, and 320x700 layouts, the complete activation
  journey, loopback-only requests, skip-link focus, landmarks, headings, controls,
  tables, details, and distinct states at
  `tests/e2e/test_w07_local_evidence_playwright.py:19-132`.

No protected expected-output fixture or protected output was opened. No provider access,
Node tooling, dependency installation, remote resource, external asset, or external
request occurred. Browser requests were confined to the loopback W07 application.

## Focused checks

- `uv run ruff check src/scouting/web/w07.py services/api/w07_main.py tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py`
  — exit 0; all checks passed.
- `uv run mypy src/scouting/web/w07.py services/api/w07_main.py`
  — exit 0; no issues in 2 source files.
- `uv run pytest -q tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py tests/integration/test_w05_m0_serving.py tests/e2e/test_w05_m0_retrieval.py`
  — exit 0; 17 passed, with one pre-existing Starlette TestClient deprecation warning.

## Residual risk

The application intentionally remains local, read-only, synthetic-development-only,
resemblance-only, LIMITED, and NO_GO. It does not provide expert relevance evidence,
recommendation evidence, production fitness, calibration, prospective outcomes, or
transfer validity. The sole review finding is the stale read-first filename above.

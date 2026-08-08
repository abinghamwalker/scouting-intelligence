# Subagent return

## Task

- task_id: `W09-RESEARCH-SERVING-04C`
- revision: `R1`
- objective: Serve deterministic W09 historical-player retrieval and comparison from one
  exact governed matrix/index authority, without stale or synthetic fallback.

## Files changed

- `src/scouting/serving/research.py`
- `tests/unit/test_w09_research_serving.py`
- `tests/integration/test_w09_research_serving_integration.py`
- `reports/reviews/W09/returns/W09-RESEARCH-SERVING-04C-R1.md`

## Public interface

- `ResearchServingService(*, matrix: LoadedFeatureMatrix, index: LoadedResearchIndex,
  pins: ResearchVersionPins)`
- `ResearchServingService.pins -> ResearchVersionPins`
- `ResearchServingService.matrix_manifest -> FeatureMatrixManifest`
- `ResearchServingService.matrix_rows -> tuple[FeatureMatrixRow, ...]`
- `ResearchServingService.index_manifest -> ResearchIndexManifest`
- `ResearchServingService.execute_query(request: ResearchQueryRequest, *, generated_at:
  datetime) -> ResearchQueryResult`
- `ResearchServingService.compare(request: ResearchComparisonRequest, result:
  ResearchQueryResult) -> ResearchComparison`
- fail-closed exception: `ResearchServingError(ValueError)`

## Behaviour implemented

- Construction accepts only exact loaded matrix/index dataclasses and explicit pins. It freshly
  reconstructs every strict Pydantic manifest, matrix row, identity catalogue row, population
  decision, eligibility decision, model configuration, and index catalogue row.
- It reconciles the four exact matrix roles; semantic row digests; manifest counts; source,
  canonical, grain, competition-season and identity bindings; eligibility outcomes; temporal
  and lineage pins; feature order/completeness; index roles/paths; configuration/scorer pins;
  catalogue order; raw indexed values; and reproduced robust-scaled vectors.
- Accepted center, scale and vector arrays are copied into private canonical C-order
  little-endian float64 arrays backed by immutable bytes. Mutating caller-retained loaded arrays
  after service construction cannot alter results under unchanged pins, and the private arrays
  cannot be made writeable.
- The public `matrix_rows` catalogue is the service's freshly validated frozen tuple. It does not
  return caller row objects or create a raw/provider reload seam.
- Query serving supports exemplar and weighted-profile modes and both transparent baseline
  methods. Active features must be an ordered subset of the pinned registry. Profile values are
  robust-scaled with the exact loaded center/scale; exemplar raw values come only from the exact
  pinned matrix grain.
- Filtering applies the mandatory competition first, followed by mutually exclusive position,
  minimum-minutes, explicit-player and exemplar-self exclusions. Same-player rows in different
  competition-season grains remain valid; multiple admitted grains for one player inside the
  selected competition fail closed. Population counts reconcile every stage.
- The full admitted population is scored through the shared `score_vector_rows(..., limit=None)`
  before the response limit. Ranking follows distance, canonical player UUID bytes and grain ID.
- Each candidate carries complete raw/scaled contrasts, weights, signed contributions and, for
  cosine, the stable normalized operands required by the strict result contract. Zero/subnormal
  cosine behaviour remains governed by the shared scorer/numeric helpers.
- Result identity/digest and ordering are deterministic across replay; generation time is
  retained as event evidence without changing semantic result identity. Historical-only,
  no-imputation and absent-G-RW4 limitations are always visible. Conservative lower-bound minute
  rows add result and candidate warnings.
- Comparison revalidates and exactly replays the supplied result against the already-loaded
  authority, then returns only 2-5 returned candidate grains as complete `FeatureMatrixRow`
  evidence in submitted order. Stale pins, altered results/digests and non-candidate grains fail
  closed.
- Production code does not import or call dormant W03/W05/W07/W08 serving/web/fixture paths,
  provider sources, matrix/index builders or loaders. Synthetic data appears only in automated
  temporary test fixtures and is never substituted by serving.

## Checks run

- `uv run ruff format --check src/scouting/serving/research.py
  tests/unit/test_w09_research_serving.py
  tests/integration/test_w09_research_serving_integration.py`
  - exit status: `0`
  - result: PASS — three files already formatted.
- `uv run ruff check src/scouting/serving/research.py
  tests/unit/test_w09_research_serving.py
  tests/integration/test_w09_research_serving_integration.py`
  - exit status: `0`
  - result: PASS — all checks passed.
- `uv run mypy src/scouting/serving/research.py`
  - exit status: `0`
  - result: PASS — no issues found.
- `uv run pytest -q tests/unit/test_w09_research_serving.py
  tests/integration/test_w09_research_serving_integration.py
  tests/unit/test_w09_scoring_kernel.py`
  - exit status: `0`
  - result: PASS — 32 tests passed in 0.92 seconds.
- `uv run bandit -q -r src/scouting/serving/research.py`
  - exit status: `0`
  - result: PASS — no security findings.

The sandboxed Bandit invocation could not read the existing external uv cache metadata, so the
exact command was rerun with read permission for that local cache. It made no dependency,
network or environment change.

## Test evidence

- End-to-end tests construct, physically load and serve deterministic matrix/index fixture
  artifacts through the accepted modeling loaders; no constructor bypass is used.
- Both methods and both query modes, ordered active subsets, zero-norm cosine explanations,
  lower-bound minute warnings, competition-first cross-competition identity handling, every
  filter-accounting stage, full-score-before-limit tie ordering, comparison row order and
  deterministic replay are asserted.
- Adversarial coverage rejects stale pins, unknown and out-of-order features, changed index
  vectors, missing-feature rows, duplicate rows, mismatched catalogue identities, non-candidate
  comparisons and mutated result evidence.
- A retained loaded index is made writeable and mutated after service construction; the service's
  prior and subsequent results and pins remain identical. Attempts to make service-held arrays
  writeable fail. Returned matrix rows are freshly reconstructed and frozen.
- The combined shared-scoring suite covers zero and subnormal vector normalization and strict
  contribution reconciliation.

## Residual risks and follow-up

- Serving receives already-loaded authorities rather than artifact paths. The accepted modeling
  loaders remain responsible for physical file size/hash/path verification; serving revalidates
  all in-memory semantic evidence and copies it privately but does not reread files.
- This packet materialised only automated temporary fixture artifacts. The retained production
  2017/18 matrix and index must still be built, independently reviewed and accepted before G-RW1
  or G-RW2 evidence can cite its eligible-population counts.
- No comparison/experiment persistence or HTTP route is implemented here; those remain the
  dependency-ordered repository/API packets.
- G-RW4 is absent. The service explicitly limits claims to historical resemblance research and
  does not support football relevance, future performance, value, availability, fit, outcome or
  recruitment-usefulness claims.

## Scope confirmation

- no Git operations: confirmed.
- no dependencies, lockfile, shared contracts, scorer, modeling, storage, API/web, feature,
  canonical-data or orchestration-control changes: confirmed.
- no provider access, network service, cloud resource, deployment or production artifact
  generation: confirmed.
- no edits outside the revised packet `allowed_paths`: confirmed.
- no subagent delegation: confirmed.

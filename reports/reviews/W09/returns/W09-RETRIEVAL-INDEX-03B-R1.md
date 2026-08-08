# Subagent return

## Task

- task_id: `W09-RETRIEVAL-INDEX-03B`
- revision: `R1`
- objective: Build a deterministic, versioned median/IQR retrieval index over one exact
  governed W09 eligible feature matrix, without synthetic product authority or production
  artifact generation.

## Files changed

- `src/scouting/modeling/research.py`
- `configs/models/w09-historical-retrieval-v1.json`
- `scripts/build_w09_research_index.py`
- `tests/unit/test_w09_research_index.py`
- `tests/integration/test_w09_research_index_build.py`
- `reports/reviews/W09/returns/W09-RETRIEVAL-INDEX-03B-R1.md`

## Behaviour implemented

- Added an explicit `production` versus `test_fixture` construction boundary. Production
  accepts only `data/manifests/wyscout/v5/research_features`, the repository-root matrix
  artifact namespace, the pinned model configuration, and
  `runs/w09/historical-player-workbench-v1`. The CLI exposes production mode only and never
  falls back to a fixture or legacy index.
- Added a strict loader for exactly four named feature-matrix artifacts:
  `player_catalogue`, `population_decisions`, `eligibility_decisions`, and
  `feature_matrix_rows`. It reproduces physical hashes, sizes, row counts and ordered typed-row
  semantic digests before fitting.
- Reconciles the exact catalogue/population/referred-grain/eligibility/matrix populations;
  source and canonical identities; eligibility reasons and decision digests; feature order and
  completeness; dataset, identity, canonical-build, registry and policy lineage; strict temporal
  pins; and canonical `(UUID.bytes, grain_id)` ordering. Duplicate grains or player identities,
  absent active values, synthetic markers, stale pins and unsafe paths fail closed.
- Fits median/IQR robust scaling across every eligible row with NumPy's pinned `linear`
  quantile method. A zero IQR retains the dimension with scale `1.0`; rows are never sampled,
  imputed, pre-limited or silently discarded.
- Writes deterministic NPY v2 little-endian float64 C-order center, scale and full scaled-vector
  arrays; a canonical candidate catalogue with raw explanation values; a canonical copy of the
  provider-neutral model configuration; and a self-digested `ResearchIndexManifest`.
- Pins matrix/identity/registry/policy identities, model configuration, both transparent
  Euclidean and cosine methods, shared scorer source digest, catalogue digest and every artifact
  byte/semantic digest. The index loader re-verifies those pins, read-only array properties and
  raw-catalogue-to-scaled-vector reproduction.
- Uses the shared scorer source only as the scorer-code authority. Production code does not
  import M0 package exports or any W03/W05/W07/W08 runtime, fixture, serving or provider module.
- Immutable preflight rejects incompatible existing bytes before any new payload is written.

## Key deterministic identities and conventions

- model configuration semantic digest:
  `bba6340727e0ae1c7d01e252521234708c7509aef84bbfbb68a5a15588a6e0f7`
- shared scorer source digest at verification:
  `95ad5811e728891bf62d8dbb7a1e4381549393d76017926e7e454d24c408dec8`
- matrix typed-row semantic digest:
  `SHA256(canonical_json_bytes([ordered strict row model_dump(mode="json"), ...]))`
- referred-grain digest: the same canonical JSON hash over ordered
  `{grain_id, player_id}` entries, with population rows ordered by canonical UUID bytes and each
  row's declared grain order retained.
- index order: canonical player UUID bytes, then grain ID; response scoring remains exhaustive
  and limiting is deferred to the shared serving/scorer path.

## Checks run

- `uv run ruff format --check src/scouting/modeling/research.py scripts/build_w09_research_index.py tests/unit/test_w09_research_index.py tests/integration/test_w09_research_index_build.py`
  - exit status: `0`
  - result: PASS — four files already formatted.
- `uv run ruff check src/scouting/modeling/research.py scripts/build_w09_research_index.py tests/unit/test_w09_research_index.py tests/integration/test_w09_research_index_build.py`
  - exit status: `0`
  - result: PASS — all checks passed.
- `uv run mypy src/scouting/modeling/research.py scripts/build_w09_research_index.py`
  - exit status: `0`
  - result: PASS — no issues found in two source files.
- `uv run pytest -q tests/unit/test_w09_research_index.py tests/integration/test_w09_research_index_build.py`
  - exit status: `0`
  - result: PASS — 19 tests passed in 0.91 seconds.
- `uv run bandit -q -r src/scouting/modeling/research.py scripts/build_w09_research_index.py`
  - exit status: `0`
  - result: PASS — no security findings.
- `uv run python scripts/build_w09_research_index.py`
  - exit status: `1` (expected fail-closed result)
  - result: PASS — reported `accepted W09 feature manifest root is absent or unsafe`; no
    synthetic/stale fallback and no production artifact write occurred.

The first sandboxed uv attempt could not read the existing external uv cache. The exact commands
were rerun with permission to read that local cache; no dependency, network or environment change
was made.

## Test evidence

- Two independent temporary index roots produce identical manifest and artifact bytes.
- Median/IQR values, unit scale for a constant feature, exhaustive row preservation and read-only
  LE-f64 arrays are asserted.
- Adversarial tests cover physical and semantic matrix tampering, path traversal, duplicate grain,
  duplicate player, absent active feature, temporal drift, production/fixture isolation, explicit
  synthetic-row marker rejection, stale matrix pins, immutable conflicts, forged big-endian and
  Fortran arrays, and a fully re-digested candidate-catalogue/vector contradiction.
- Only temporary automated fixtures were materialised. No production feature or index artifact was
  generated.

## Residual risks and follow-up

- The governed production feature manifest is intentionally not yet materialised, so this packet
  cannot execute or evidence the retained 2017/18 population build. The master must align the 02C
  producer with the exact four artifact roles and semantic digest conventions above, independently
  review this code, and run the final governed index build only after accepting G-RW1 evidence.
- The initial index rejects duplicate canonical players even across different grains. This is the
  packet's fail-closed duplicate-player requirement and prevents silent row selection; if retained
  02C evidence contains legitimate multi-competition rows for one canonical player, the master must
  resolve that population behavior explicitly rather than deduplicating silently.
- Retrieval filtering, query construction, feature contributions and result limiting remain the
  dependency-ordered serving packet's responsibility. This packet provides complete verified
  arrays and declares both transparent methods; it does not claim G-RW2 or football relevance.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no dependency or lockfile changes: confirmed.
- no orchestration control, shared contract, serving, web, storage-state, canonical-data or
  feature-matrix edits: confirmed.
- no network, provider access, production artifact generation or external service: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no further delegation: confirmed.

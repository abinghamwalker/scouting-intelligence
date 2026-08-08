# Subagent return

## Task

- task_id: `W09-ARCH-SURVEY-00`
- objective: Map the accepted W04, W05 and W07 seams W09 should reuse, exclude every synthetic-only interactive path, and recommend dependency-safe implementation packets without editing implementation code.

## Files changed

- `reports/reviews/W09/returns/W09-ARCH-SURVEY-00-R1.md`

## Summary

- No implementation was changed. The recommended W09 composition is an additive real-data research path that reuses W04 governance/identity/temporal foundations, W05 contract and artifact-safety patterns, a single extracted W05-compatible scoring kernel, and W07's server-rendered browser composition pattern. It must not call the current W03, W05/W07 or W08 synthetic catalogues at runtime.
- The accepted one-row W04 Bronze/Silver/Gold build is a proof seam, not the population builder. `src/scouting/data_products/wyscout/player_match.py:90` and `src/scouting/data_products/wyscout/gold.py:53` hard-code the selected player/match values, while `src/scouting/sources/wyscout_completion_index.py:986` admits only the vertical-slice member and match. W09 therefore needs a full retained-source canonical build before the feature matrix; it must not multiply the one-row proof or treat the raw event files as a serving-time database.
- The retained identity evidence already demonstrates why source count is not eligibility count: the current bundle records `PLAYER:RESOLVED=3603`, `PLAYER:REVIEW_REQUIRED=15`, and `PLAYER:REJECTED=1`. W09 must reconcile these identities and eligibility reasons rather than equating 3,603 with the matrix row count.

### Reuse map

| Accepted seam | Reuse in W09 | Boundary / required adaptation |
| --- | --- | --- |
| `src/scouting/contracts/primitives.py` and `src/scouting/contracts/evidence.py` | Canonical UUID types, strict UTC instants, SHA-256 identities, coverage, lineage and temporal evidence. | Reuse directly in additive W09 contracts. Do not loosen strict validation. |
| `src/scouting/contracts/wyscout_data.py`, `src/scouting/contracts/wyscout_identity.py`, `src/scouting/identity/wyscout.py:1024` | Canonical source identities, resolved/review-required/rejected states, source-row lineage, canonical player/match/action concepts, coverage and temporal proof. | Use the accepted bundle and only resolved canonical players. Never use source player IDs or display names as joins. The current Silver/Gold producers are one-row proof code and are not full-population producers. |
| `src/scouting/sources/wyscout_manifest.py` and `src/scouting/sources/wyscout_completion_index.py:937` | Verify the retained snapshot, member hashes, 3,071,395-action completion index and period membership before full parsing. | Add a full-population adapter/iterator alongside the accepted vertical-slice loader. Preserve the vertical-slice pins and tests unchanged. No acquisition or network path is needed or authorised. |
| `src/scouting/data_products/wyscout/__init__.py` and `src/scouting/storage/wyscout_publication.py` | Canonical Parquet projection, guarded reads, staged immutable writes, physical and semantic digests. | Extend with new research Bronze/Silver/feature-matrix root roles and manifests; do not overwrite the accepted W04 build. |
| `src/scouting/contracts/m0.py:148` | `FeatureValue` and its explicit `value`, `zero`, `missing`, `suppressed`, and `unavailable` semantics. | Reuse this absence model or an exact compatible projection. No null-to-zero or imputation shortcut. |
| `src/scouting/contracts/m0.py:561`, `:771`, and `:1008` | Array descriptors, canonical manifest/result digests, exact artifact pins, deterministic result/evidence binding, and fail-closed version matching patterns. | `M0EvidenceClass`, the W04 exact-four special case, role-brief pins and the current M0 manifest are too narrow for a full historical matrix. Add W09 dataset/matrix/index/query/comparison/experiment contracts; reuse the primitives and validation patterns rather than re-signing an M0 synthetic manifest. |
| `src/scouting/modeling/baselines.py:161` and `:280` | Median/IQR robust scaling, deterministic float64/C-order arrays, fixed NPZ bytes, immutable artifact writing and deterministic model/index identity. | The public fitter is hard-bound to 18 synthetic rows and must not be called by W09. Extract the generic geometry/artifact byte routines behind a shared interface, preserving W05 byte parity. |
| `src/scouting/m0/core.py:869` and `:877` | One in-process scorer, deterministic `(distance, canonical UUID bytes)` tie order, cosine contributions and read-only arrays. | Extract one shared scoring kernel used by both unchanged W05 behaviour and the W09 loader. Do not implement distance arithmetic separately in web/API code or a second W09 scorer. Remove W05-specific six-feature/PCA and role-membership assumptions from only the shared kernel, not from the accepted W05 wrapper. |
| `src/scouting/serving/m0.py:212`, `:245`, `:913`, and `:918` | Thin single/batch serving entry points, revalidation of nested request semantics, exact registered-root validation, artifact/request pin matching, explanations and result digest construction. | Implement an additive historical serving facade over the shared scorer. It may import contracts, guarded artifact readers and the scoring kernel; it must not import provider sources or training/materialisation code. |
| `src/scouting/web/w07.py:155` and `apps/web/templates/w07/` | FastAPI factory, loopback-safe headers, Jinja autoescape, static mounting, result-context composition, search/results/compare/evidence states and accessible server-rendered structure. | Recompose in new W09 paths. Do not import `_core`, `default_request`, the W07 catalogue, templates or routes because each is synthetic-bound. |
| `src/scouting/storage/embedded.py` and `src/scouting/storage/guarded.py` | Local SQLite operational state and guarded local report persistence. | Use for automatically recorded experiments/reports. Do not require W08 authentication, role workflow, manual audit entry or export administration in the core journey. |
| `src/scouting/evaluation/core.py` and `src/scouting/evaluation/robustness.py` | Deterministic ranking calculations, digests and robustness calculation patterns. | Add an unprotected W09 engineering evaluation surface. Do not open W06 protected output or imply that engineering stability/coverage is expert relevance. |

### Contracts and one-path architecture

Create `src/scouting/contracts/research.py`, exported deliberately from `src/scouting/contracts/__init__.py`, with strict additive contracts for:

- a dataset descriptor and capability declaration;
- a feature-matrix row/manifest at canonical `player × competition-season × fixed closed window` grain;
- an eligibility decision with minimum-minutes policy, exact/lower-bound minute state and reason codes;
- an index manifest pinned to dataset, identity bundle, feature registry, matrix, eligibility policy, scaler, method, candidate catalogue and checksums;
- an exemplar query and a weighted-profile query (exactly one mode), explicit positive feature weights, filters, limit, cutoff and every expected version/digest;
- ranked candidates with stable canonical identity, distance/similarity, feature contrasts, signed contributions, coverage, missingness, applicability and limitations;
- comparison, saved experiment, replay receipt and reproducible report contracts.

The existing `RetrievalRequest` at `src/scouting/contracts/retrieval.py:108` requires a role-brief identity and the W05 `PinnedM0ServingRequest` at `src/scouting/contracts/m0.py:771` requires W05 artifact/taxonomy pins. Neither should be filled with fictional values for W09. New research contracts should reuse their strict primitives, canonical-digest conventions, evidence types and resemblance-only claim boundary.

Use one scorer implementation. The safest seam is a master-owned serial refactor into `src/scouting/m0/scoring.py`: move the deterministic Euclidean/cosine row scoring and tie ordering from `LoadedM0Artifact.score` into a pure, typed kernel; keep `LoadedM0Artifact.score` as an adapter and prove the accepted W05 result digest remains byte-identical; have `src/scouting/serving/research.py` call that same kernel through its historical artifact loader. Scaling and index building remain in modeling, never serving or web.

### Full historical data and feature-matrix recommendation

The retained source should flow through a bounded provider adapter into canonical Parquet, then into features. Proposed production artifacts are:

- `data/working/wyscout/v5/research/build_id=<digest>/canonical/` for full canonical players, teams, matches, lineups/minute intervals and actions;
- `data/working/wyscout/v5/research/build_id=<digest>/eligibility/part-00000.parquet` with one reconciled decision for every canonical player-window considered;
- `data/working/wyscout/v5/research/build_id=<digest>/feature-matrix/part-00000.parquet` with one unique row per eligible canonical player-window;
- `data/manifests/wyscout/v5/research/<build-id>.manifest.json` binding rights, source/completion/identity/schema/code digests, row counts, filters, cutoff and every produced file;
- `runs/w09/historical-player-workbench-v1/` for the immutable scaler/index/catalogue manifest and arrays.

The initial window should be the closed 2017/18 competition-season represented by the retained five-league snapshot, with separate rows by competition-season and canonical player. Team membership may be a descriptive list/filter, not part of player identity or an accidental row-duplication key.

Minimum minutes must be an explicit versioned engineering eligibility policy derived after the inventory exposes exact-minute coverage. A candidate may qualify only from a verified exact total or a deliberately declared conservative lower-bound rule; missing/right-censored minutes are never replaced by appearances, action counts, 90-minute assumptions or imputation. The packet may freeze a threshold after producing its coverage histogram, but the report must reconcile all 3,603 recorded players through named resolved-identity, participation, minute-state, threshold, feature-completeness and final-eligible counts.

The feature registry should live at `configs/features/w09-historical-player-window-v1.json` and declare provider-neutral football concepts plus their current Wyscout mappings, numerator, denominator, unit, event/tag predicates, missing/zero/suppression policy, temporal rule and capability state. The matrix builder belongs in `src/scouting/features/historical.py`; it consumes canonical tables, not raw provider payloads. A build script may orchestrate reads and writes, but serving must never parse Wyscout files.

### Retrieval and stale-version controls

Implement robust-scaled distance and cosine baselines over every eligible row, sorted canonically before fitting/indexing. Record median, IQR, constant-feature handling, weights and all array descriptors. No random sampling may define the interactive candidate universe.

- Exemplar query: resolve exactly one canonical row from the selected matrix version and exclude that exact grain by default.
- Weighted profile query: require the exact registry feature set or an explicit active subset, finite non-negative weights and at least one positive weight. Persist the raw profile, weights and normalized scorer input.
- Eligibility filters: execute only against declared canonical catalogue fields/capabilities; return pre-filter population, excluded-by-reason and scored counts.
- Missingness: do not impute. A row missing an active ranking feature is excluded with a visible reason; missing optional evidence remains displayed but non-ranking.
- Contributions: Euclidean contributions must reconcile to the declared distance convention; cosine explanations must expose the signed per-feature similarity terms and contrast values rather than invent a percentage. Data confidence remains separate from rank.
- Stale protection: the request pins dataset, identity bundle, matrix, registry, eligibility policy, model/scaler, index and catalogue digests/versions. The loader validates all physical and semantic checksums before scoring. A mismatch returns an explicit incompatible/stale response; it never reloads current pins into the submitted request.
- Determinism: full candidate order is `(distance, canonical_player_id.bytes, grain_id)`; response limits are applied only after all eligible/filter-admitted rows are scored. Repeated requests with the same semantic request and artifacts reproduce the ranking/result digest.

Do not copy W07's `default_request()` behaviour (`src/scouting/web/w07.py:84`), which reads the currently registered manifest and constructs pins on demand. The W09 browser must submit the dataset/index identities it displayed; replacement between display and submission must fail closed.

### Synthetic-only paths excluded from W09 product composition

The following may remain for accepted tests or dormant legacy entry points, but no `services/api/w09_main.py`, `src/scouting/web/w09.py`, W09 template, W09 storage/replay path or W09 serving import may reach them:

1. W03 synthetic application: `services/api/main.py`, `src/scouting/web/app.py`, `src/scouting/serving/synthetic.py`, `src/scouting/sources/synthetic.py`, and `apps/web/templates/w03_journey.html`.
2. W05 synthetic feature/model authority: the synthetic family and fixture functions in `src/scouting/features/registry.py:520`, `:732`, and `:913`; `configs/features/w05-m0-feature-registry-v1.json`; `configs/models/w05-m0-baselines-v1.json`; `configs/roles/w05-football-responsibility-taxonomy-v1.json`; `tests/fixtures/w05/`; and `runs/w05/m0-baseline-v1/`.
3. W05 synthetic loaders/fitter/serving wrapper: `M0DevelopmentCandidates`, `load_m0_development_candidates` and `load_m0_development_queries` in `src/scouting/m0/core.py`; `fit_m0_artifact` and `run_synthetic_development_check` in `src/scouting/modeling/baselines.py`; and the hard-coded synthetic fields, population pins and limitations in `src/scouting/serving/m0.py`. Only an extracted generic scorer/artifact-safety kernel may be shared.
4. W07 synthetic browser: `src/scouting/web/w07.py`, `services/api/w07_main.py`, `apps/web/templates/w07/`, and `apps/web/static/w07/`. Its routes at `src/scouting/web/w07.py:241-411` and synthetic catalogue at `:162` are legacy evidence surfaces, not W09 routes.
5. W08 dormant collaboration/pilot: `src/scouting/web/w08.py`, `src/scouting/web/w08_study_console.py`, `services/api/w08_main.py`, the W08 study launcher, `apps/web/templates/w08/`, `apps/web/templates/w08_study_console/`, and their static assets. W08 imports the private W07 synthetic core at `src/scouting/web/w08.py:67-68` and replays it at `:751-815`; this is a preservation constraint, not a W09 integration seam.
6. Package-level accidental exposure: `src/scouting/serving/__init__.py`, `src/scouting/modeling/__init__.py`, `src/scouting/features/__init__.py`, and `src/scouting/m0/__init__.py` currently export synthetic/development entry points. W09 code should use explicit `scouting.serving.research`, `scouting.modeling.research`, and `scouting.features.historical` imports and never wildcard/package-level legacy composition.

Automated W09 tests may construct synthetic rows as fixtures, but production app construction must require a governed historical manifest and fail if only a W05 fixture/index exists. Add an import/route tripwire test that monkeypatches W03/W07/W08 constructors and W05 development loaders to raise, traverses every W09 HTML and JSON endpoint, and proves none is called. Also scan W09 implementation paths for `tests/fixtures/w05`, `runs/w05`, `synthetic_position_code`, `SyntheticServingService`, `w07_core` and `w07_default_request`.

### Browser/API/persistence composition

Create a separate `create_w09_app()` in `src/scouting/web/w09.py`, mounted by `services/api/w09_main.py`. It should own `/` and `/w09` as the new default research journey and must not mount `/w07`, `/w08` or the Study Console. Preserve the existing W07/W08 entry points and tests unchanged so those modules remain dormant and separately launchable.

Recommended strict endpoints, all backed by the same in-process serving facade rather than HTTP self-calls, are:

- `GET /api/w09/datasets` and `GET /api/w09/players`;
- `POST /api/w09/queries` and `GET /api/w09/results/{result_id}`;
- `POST /api/w09/comparisons`;
- `POST /api/w09/experiments`, `GET /api/w09/experiments/{experiment_id}`, and `POST /api/w09/experiments/{experiment_id}/replay`;
- `GET /api/w09/experiments/{experiment_id}/report` for a local reproducible JSON/HTML report.

The server-rendered workspace may use progressive form submissions, but it should keep dataset → query → ranked results → explanation → compare → save/replay visible as one coherent workspace. Search results must use governed real player display names tied to canonical IDs. No sign-in, role switch, brief revision, shortlist transition, manual audit form or W08 export administration belongs in this path.

Use `src/scouting/storage/research.py` over `src/scouting/storage/embedded.py` for operational experiment state and `GuardedStorage` for report bytes. Store the exact request/result/comparison JSON, all version pins/checksums, full eligible/filter counts, seed, warnings, code identity, report digest and optional user name/note. Replay reads the saved pins; it must reject missing or replaced artifacts rather than silently run the current index. Creation timestamps may differ from scorer identity, so reproducibility checks should compare semantic request, ordered ranking and result/report digests explicitly.

### Dependency-ordered implementation packets

All packets below are serial unless explicitly stated; the master retains contracts, orchestration controls, dependency/lock state, integration evidence and Git operations.

1. **W09-DATA-INVENTORY-01** — report-only. Read the retained source/completion manifest, identity bundle/review queue and all W04 layer manifests/products. Deliver `reports/verification/W09/retained-data-inventory.md` with rights, checksums, schemas, source/canonical counts, missing products and a reconciliation ledger. Stop on rights conflict or checksum drift.
2. **W09-RESEARCH-CONTRACTS-02A (master serial)** — `src/scouting/contracts/research.py`, `src/scouting/contracts/__init__.py`, `tests/contracts/test_w09_research_contracts.py`. Deliver the strict dataset/matrix/eligibility/index/query/result/comparison/experiment/replay contracts and digest/stale-pin adversarial tests.
3. **W09-FULL-CANONICAL-BUILD-02B** — `src/scouting/sources/wyscout_historical.py`, `src/scouting/data_products/wyscout/historical.py`, `scripts/build_w09_historical_canonical.py`, `tests/unit/test_w09_wyscout_historical_adapter.py`, `tests/integration/test_w09_full_canonical_build.py`. Inputs are only retained accepted local source/identity manifests. Deliver deterministic full canonical Parquet and manifest generation; preserve all W04 vertical-slice paths.
4. **W09-FULL-FEATURE-MATRIX-02C** — `src/scouting/features/historical.py`, `configs/features/w09-historical-player-window-v1.json`, `scripts/build_w09_feature_matrix.py`, `tests/unit/test_w09_historical_features.py`, `tests/integration/test_w09_feature_matrix.py`. Depends on 02A/02B and the inventory. Deliver the versioned eligibility ledger, matrix, catalogue and manifest plus two-root byte/semantic reproducibility, uniqueness, temporal and no-synthetic-row checks. This closes G-RW1 only after master reconciliation.
5. **W09-SHARED-SCORER-03A (master serial, independent parity review required)** — `src/scouting/m0/scoring.py`, the narrow adapter in `src/scouting/m0/core.py`, `tests/unit/test_w05_m0_models.py`, `tests/integration/test_w05_m0_serving.py`, and `tests/unit/test_w09_scoring_kernel.py`. Extract one scorer without changing W05 accepted bytes/digests/rankings.
6. **W09-INDEX-BUILDER-03B** — `src/scouting/modeling/research.py`, `configs/models/w09-research-baselines-v1.json`, `scripts/build_w09_research_index.py`, `tests/unit/test_w09_research_index.py`. Depends on 02C/03A. Deliver deterministic robust-scaling plus weighted-distance/cosine artifacts and adversarial manifest/array checks.
7. **W09-HISTORICAL-SERVING-03C** — `src/scouting/serving/research.py`, `tests/integration/test_w09_research_serving.py`, `tests/security/test_w09_research_artifact_boundaries.py`. Depends on 03B. Deliver full-population eligibility/filter execution, exemplar/profile queries, contributions/contrasts/missingness, strict pins and stale/identity/temporal fail-closed tests. This closes G-RW2 only after master parity and population checks.
8. **W09-RESEARCH-STATE-04A** — `src/scouting/storage/research.py`, the additive SQLite migration allocated by the master, `tests/integration/test_w09_research_storage.py`. Deliver immutable saved experiment versions, exact replay pins, conflict handling and guarded local report persistence. Do not import W08 workflow/audit services.
9. **W09-RESEARCH-API-04B** — strict JSON routes in `src/scouting/web/w09.py`, `services/api/w09_main.py`, `tests/integration/test_w09_research_api.py`. Depends on 03C/04A. Deliver the endpoint set above, incompatible-version errors and no synthetic fallback. Keep presentation arithmetic out of web code.
10. **W09-RESEARCH-UI-05** — `apps/web/templates/w09/`, `apps/web/static/w09/`, `tests/e2e/test_w09_research_workbench_playwright.py`, and UI-focused integration/accessibility tests. Depends on 04B. Deliver the single browser journey and synthetic/W08 non-reachability tripwire. This closes G-RW3 only after a clean first-use replayable report journey.
11. **W09-EVALUATION-06** — `src/scouting/evaluation/research.py`, `configs/evaluation/w09-frozen-research-queries-v1.json`, `scripts/evaluate_w09_research.py`, `tests/unit/test_w09_research_evaluation.py`, and `reports/verification/W09/retrieval-evaluation.md`. Depends on 03C and should run after UI/API integration identities are frozen. Evaluate byte/result reproducibility, population/filter coverage, perturbation/rank stability, eligibility edge cases and explanation reconciliation. Record weaknesses and retain the explicit absence of expert relevance evidence.
12. **W09-INDEPENDENT-REVIEW-07** — report-only independent reviewer over inventory, matrix, scorer/index, API/UI, persistence and evaluation evidence. Required checks: data reconciliation, rights, identity ambiguity, temporal leakage, stale substitution, scorer parity, UI journey, saved replay and claim language. All high-severity findings return to bounded rework before W09 acceptance.

The canonical-build, scorer extraction, shared contracts, SQLite migration and W07/W08 preservation checks should not run in parallel because they touch shared authority or accepted paths. After 02C is accepted, UI visual work can be prepared in parallel with evaluation fixture drafting only if neither packet imports or freezes unaccepted API/contract shapes.

### Import-layer and preservation constraints

- `src/scouting/contracts/research.py` imports no project module outside `scouting.contracts`.
- Provider parsing stays in `scouting.sources`/`scouting.data_products`; `scouting.features` consumes canonical tables; `scouting.modeling` builds immutable artifacts; `scouting.serving` loads and scores only; `scouting.web` composes presentation and persistence. Extend the import-linter contract under master control so W09 cannot regress this direction.
- Serving must never import `scouting.sources`, raw Wyscout paths or matrix-building functions. Web must never import modeling/training.
- Do not rename or change W07 `_core()`/`default_request()` semantics while W08 retains private imports at `src/scouting/web/w08.py:67-68`. Any shared scorer refactor must rerun the complete W05/W07/W08 suites and accepted W05 digest parity.
- Preserve every W08 route, template, authorization, audit, concurrency and export boundary. Dormant means excluded from W09 navigation/composition, not deleted or weakened.

### Claim boundary

W09 may claim deterministic, governed historical resemblance research within the declared dataset/window/feature/weight/method boundary after G-RW1–G-RW3 pass. This survey makes no football-relevance, current-market, recruitment-usefulness, outcome, value, availability or recommendation claim. G-RW4 remains absent and W06 remains `NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE`.

## Tests run

- command: `uv run lint-imports`
  - exit status: `2` on the sandboxed attempt; `0` on the required rerun with permission to read the existing external uv cache
  - result: PASS on rerun — 64 files and 146 dependencies analysed; all 3 import contracts kept and 0 broken. The first attempt did not execute the linter because uv could not read `/Users/adrian/.cache/uv/sdists-v9/.git` inside the filesystem sandbox.
- command: `test -s reports/reviews/W09/returns/W09-ARCH-SURVEY-00-R1.md`
  - exit status: `0`
  - result: PASS — the required return report exists and is non-empty.

## Artifacts/evidence

- `reports/reviews/W09/returns/W09-ARCH-SURVEY-00-R1.md`
- Accepted reference identities retained in this survey: source manifest `4e16bdb5-afe7-5601-88ad-adc124cfce3b`; source completion digest `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`; identity bundle digest `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`; W05 accepted result digest `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`.

## Risks

- **Data coverage:** only the source snapshot and one-row canonical proof are currently materialised end to end. G-RW1 cannot pass until all source/canonical/eligible counts and filters reconcile.
- **Identity:** 15 player identities are review-required and one is rejected in the retained bundle. Any guessed mapping or source-ID join is a high-severity stop.
- **Minutes/temporal:** the accepted W04 proof suppresses exact minutes and rates. A full lineup/minute derivation and explicit cutoff policy are prerequisites for per-90 features; event-time and local availability-time must both remain visible.
- **Scorer parity:** extracting a shared kernel risks changing W05 floating-point bytes, contribution order or tie behaviour. Exact accepted W05 result parity and immutable artifact checks are mandatory before using the kernel in W09.
- **Stale substitution:** browser-side auto-refresh of manifest pins would hide stale requests. Dataset/index versions must be user-visible and submitted exactly.
- **Persistence:** SQLite experiment state and report bytes can diverge unless both are content-addressed and transactionally cross-pinned.
- **W08 preservation:** W08 relies on private W07 composition and synthetic identities. Broad refactors or package-export cleanup can silently break the dormant module.
- **Performance:** 3,071,395 actions should be processed by bounded DuckDB/Polars/Parquet scans, not loaded into the web process or reparsed per query.
- **Claim scope:** engineering reproducibility/stability is not expert relevance. No evaluation metric in W09 may be presented as recruitment usefulness.

## Follow-up items

- Master should issue the inventory packet first, then allocate the serial contracts/canonical-build/matrix/scorer packets above with independent parity review around the shared scorer and W08 preservation.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and `uv.lock` were not changed.
- no edits outside `allowed_paths`: confirmed; the only file created or modified is `reports/reviews/W09/returns/W09-ARCH-SURVEY-00-R1.md` (its missing parent directories were created solely to place this allowed deliverable).

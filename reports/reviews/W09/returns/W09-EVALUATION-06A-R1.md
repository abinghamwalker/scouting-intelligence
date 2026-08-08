# Subagent return

## Task

- task_id: `W09-EVALUATION-06A`
- revision: `R1`
- objective: Implement a deterministic local evaluation harness and frozen retained-data query
  suite for W09 retrieval reproducibility, coverage, bounded sensitivity, eligibility/filter
  behaviour and explanation consistency without football-quality claims.

## Files changed

- `src/scouting/evaluation/research.py`
- `configs/evaluation/w09-frozen-retrieval-evaluation-v1.json`
- `scripts/evaluate_w09_retrieval.py`
- `tests/unit/test_w09_research_evaluation.py`
- `tests/integration/test_w09_research_evaluation_integration.py`
- `reports/reviews/W09/returns/W09-EVALUATION-06A-R1.md`

## Public interface

- `research_version_pins(matrix, index) -> ResearchVersionPins`
- `load_frozen_evaluation_suite(path, *, service) -> FrozenResearchEvaluationSuite`
- `run_research_evaluation(suite, *, service) -> ResearchRetrievalEvaluationResult`
- `render_evaluation_payload(result) -> bytes`
- fail-closed exception: `ResearchEvaluationError(ValueError)`
- local CLI: `scripts/evaluate_w09_retrieval.py --output-root <master-owned-path>`

## Behaviour implemented

- The canonical suite binds the exact retained matrix, index, feature registry, eligibility policy,
  cutoff, identity and canonical-data authorities. Every query source is an accepted real matrix
  grain; the loader rejects absent or synthetic sources, stale pins, population drift, unordered
  feature subsets, non-canonical JSON and unsafe paths.
- Nine frozen cases cover all four player positions, all five eligible domestic competitions,
  both exemplar/profile modes and both Euclidean/cosine methods. Query profile values are always
  materialised from the accepted source row, not copied into an ungoverned configuration.
- Every case runs twice at distinct frozen generation timestamps. Result identity/digest,
  candidate order, scores, contributions, warnings and mutually exclusive population accounting
  must reproduce exactly.
- Filter witnesses cover exemplar self-exclusion, position filtering, minimum minutes at the
  450-minute policy and above it, explicit player exclusion, full-population scoring before the
  response limit and empty admission.
- Explanation verification independently reproduces median/IQR-linear scaling with unit scale for
  constant features, raw and scaled contrasts, Euclidean terms, cosine normalized components,
  aggregate score, zero-weight terms, no-missingness and deterministic tie order. A result row
  outside the governed matrix or any operand/contribution inconsistency fails the evaluation.
- Two declared maximum-0.1 weight perturbations record deterministic top-five overlap, union-rank
  displacement and shared-candidate score changes. They are explicitly sensitivity evidence only,
  with no acceptable threshold and no ranking-quality interpretation.
- Coverage records retained source/matrix/player counts, unique returned grains/players, total
  full-population score evaluations and per-competition query/return coverage.
- Result evidence is a strict self-digested model rendered as canonical JSON. The CLI requires an
  explicit output root and writes a private, immutable, digest-named file; it cannot silently
  publish into the production run root.
- Limitations are exact: historical resemblance is not football relevance or recruitment
  usefulness, all eligible rows use lower-bound minutes, coverage is limited to five retained
  domestic competitions, G-RW4 is absent and stability does not validate ranking quality.

## Retained production evidence

- Frozen suite digest: `be3d4f5a69ab57f3a53fa90b84f4fbfda94c7269f362afee9a8d5af9491872ba`
- Evaluation result digest: `34a35882d1b9609cbf379783f6461b283f73bc37248c7b89b30eab0985c442c7`
- Matrix rows / unique players / source players: `1,975 / 1,965 / 3,603`
- Frozen query cases / explanation witnesses / filter witnesses / perturbations: `9 / 9 / 15 / 2`
- Eligible competitions represented: `5`
- Evaluation returned `30` unique real grains/players (`1.519%` of matrix rows) while recording
  `2,841` full-population score evaluations across the nine fixed queries.
- Both bounded top-five perturbations retained all five candidates. Mean union-rank displacement
  was `0.4` for the England Euclidean pair and `0.0` for the Italy cosine pair; these are frozen
  sensitivity observations, not quality thresholds.
- Production artifacts were read-only inputs. The packet did not write a production evaluation
  output; final publication under `runs/w09/evaluation-v1` remains master-owned.

## Checks run

- `uv run ruff format --check src/scouting/evaluation/research.py
  scripts/evaluate_w09_retrieval.py tests/unit/test_w09_research_evaluation.py
  tests/integration/test_w09_research_evaluation_integration.py`
  - exit status: `0`.
  - result: PASS — four files already formatted.
- `uv run ruff check src/scouting/evaluation/research.py scripts/evaluate_w09_retrieval.py
  tests/unit/test_w09_research_evaluation.py
  tests/integration/test_w09_research_evaluation_integration.py`
  - exit status: `0`.
  - result: PASS — all checks passed.
- `uv run mypy src/scouting/evaluation/research.py scripts/evaluate_w09_retrieval.py`
  - exit status: `0`.
  - result: PASS — no issues found in two source files.
- `uv run pytest -q tests/unit/test_w09_research_evaluation.py
  tests/integration/test_w09_research_evaluation_integration.py
  tests/unit/test_w09_research_serving.py`
  - exit status: `0`.
  - result: PASS — 17 tests passed in 4.73 seconds.
- `uv run bandit -q -r src/scouting/evaluation/research.py
  scripts/evaluate_w09_retrieval.py`
  - exit status: `0`.
  - result: PASS — no security findings.

The exact commands were run with local read access to the existing uv cache because sandboxed uv
could not inspect that cache's metadata. No network access or dependency/lock change was used.

## Test evidence

- Retained-data integration executes through production-mode matrix/index loaders and the exact
  serving authority. It reconciles source grains, positions, competitions, both methods/modes,
  counts, lower-bound minutes, deterministic evaluation bytes and claim boundaries.
- Adversarial retained-suite cases re-digest stale matrix pins and absent source grains and prove
  both fail closed.
- Synthetic rows exist only inside automated temporary serving fixtures. Those tests exercise
  zero feature weights, fully tied score order, missing-feature rejection, foreign-grain rejection
  and changed explanation operands; none can become an interactive candidate or retained-data
  quality claim.
- Unit tests cover suite/case self-digests, rank displacement invariants, canonical path safety and
  private immutable output semantics.

## Residual risks and follow-up

- G-RW4 is absent. No relevance-labelled or expert football evaluation exists, so these results
  support deterministic engineering behaviour only.
- The retained all-lower-bound minute evidence can overstate per-90 rates. The harness records the
  limitation but cannot repair unavailable exact duration evidence.
- Stability results describe only the frozen perturbations. They do not establish ranking quality,
  general robustness or a football-acceptable threshold.
- Only five retained 2017/18 domestic competitions pass the closed policy/window. This is not a
  current-market universe and does not demonstrate future-provider parity.
- Master-owned final publication and independent W09 review remain outside this packet.

## Scope confirmation

- Git transparency: one read-only `git status --short -- <allowed paths>` inspection was
  inadvertently invoked at packet resumption. It made no worktree/index/repository mutation. No
  Git write operation or later Git command was run.
- no dependencies, lockfile, orchestration controls, shared contracts, modeling, serving,
  reporting, web/API or production-artifact edits: confirmed.
- no provider/network/cloud/deployment access and no production evaluation-output write:
  confirmed.
- no edits outside the packet `allowed_paths`: confirmed.
- no subagent delegation: confirmed.

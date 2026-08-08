# W09 prestudy uplift implementation review

- Date: 2026-08-07
- Approved package: Package A — source-semantic goal repair plus delivery-readiness bundle
- Approved checkpoint: `checkpoint/w10-prestudy-uplift-reviewed`
- Delivery state: master-verified implementation candidate; checkpoint is explicitly not W10
  acceptance

## Implemented scope

The retained W09 workbench now excludes event 9 save-attempt forms from `goals_per90` while
retaining tag-101, non-own-goal evidence from all other supported event types. Canonical authority,
scorer code, population, eligibility, non-goal features and W10 thresholds remain unchanged.

The delivery bundle adds a complete dataset card, W09 model card, operator runbook, one-command
loopback launcher, expanded in-product methodology explanations, a preregistered semantic
evaluation, before/after live-search evidence and exact pin-transition evidence.

No covariance method, ratio redesign, position-conditioned scaling, small-sample shrinkage,
all-leagues pool, dependency, provider access, deployment or performance optimisation was added.

## Subagent packets and master acceptance

Three path-disjoint implementation packets ran in parallel. Each prohibited Git operations,
network access, further delegation, authority changes and out-of-scope paths, and required the
return format in `orchestration/templates/subagent_return.md`.

| Packet | Write scope | Returned evidence | Master acceptance |
|---|---|---|---|
| `W09-UPLIFT-DELIVERY-DOCS-01` | README, dataset/model cards, runbook | Required methodology, use, rights, limitation, W10 and experiment-boundary text present | Every changed document read; placeholders replaced only after production cascade; acceptance `rg` checks pass |
| `W09-UPLIFT-LOCAL-LAUNCHER-02` | launcher and launcher unit test | zsh syntax, exact loopback command, bounded port and forbidden-flag tests | Launcher read and executed; executable bit verified; 12 tests included in focused/full gates |
| `W09-UPLIFT-UI-EXPLANATION-03` | W09 template/script and focused UI/browser tests | 7 unit tests and 3 real-browser fixture tests with the known warning only | Every changed file read; tests independently reproduced; production browser witness completed |

The master retained all shared feature, model, evaluation, artifact, W10 policy, evidence, Git and
integration authority. A production Chrome witness found one automatic favicon 404; the master
added a bounded 204 loopback route plus regression assertion, then reproduced a clean console.

## Master-owned evidence and cascade

- Baseline frozen before methodology edits:
  `reports/verification/W09/uplift-semantic-baseline-v1.json`.
- Preregistered criteria/configuration:
  `configs/evaluation/w09-semantic-uplift-evaluation-v1.json`, digest
  `6340ec28d24150b3fe16174fb01c07c383119331f622fe6b9fad3582eb602fb6`.
- Post-uplift semantic result:
  `reports/verification/W09/uplift-semantic-post-v1.json`, digest
  `4bf40416d1474188c801b9d122a3c8a7000da19ba40aa00f4c886b67c4d0d880`.
- Outcome: 9,436 → 4,695 goal actions; all 4,741 event-9 rows excluded; all 518 supported
  non-event-10 set-piece goals retained; every preregistered criterion passed.
- Single cascade: matrix `a9f7cc2d5fc12ea0` → index
  `ff55b286-935c-55c4-bb8e-814a95962b41` → frozen W09 result `5dd3cf9b…e7e90` → W10 v2 policy
  `867ea773…68a9d`.
- Two clean matrices, two clean indices, two clean semantic evaluations and two W10-derived
  comparison bundles reproduced byte-identically within their respective clean roots.
- Canonical build digest remains `0105267a…264b43`; scorer digest remains `535e2447…9fc1c`.
- W10 threshold and threshold-policy projections are byte-semantically unchanged.

Detailed evidence is in:

- `reports/verification/W09/uplift-methodological-evaluation-v1.md`
- `reports/verification/W09/uplift-representative-search-comparison-v1.md`
- `reports/verification/W09/uplift-pin-transition-v1.md`

## Experiments

All four pre-uplift experiments were preserved and replayed without migration or re-pinning. Each
now has an `INCOMPATIBLE_PINS` receipt against the live matrix, including retained experiment
`e6a8a280-423c-8248-ac40-037a34b99cf7`.

Post-uplift experiment `7b406aa1-f2f5-506a-89e2-9be868a2cfd1` binds an exact Messi-to-France
Euclidean query, top-two comparison and canonical JSON report. Its result, comparison and report
digests are `2a3cdbc8…76b2b`, `3456e33c…e4d5` and `4f24eb68…b31a3`; replay status is `REPRODUCED`.

## Verification results

| Check | Result | Duration |
|---|---|---:|
| `uv sync --locked --all-groups` | 82 packages audited | 0.03s command time |
| `uv run ruff format --check .` | 1,128 files already formatted | 0.05s |
| `uv run ruff check .` | pass | 0.02s |
| `uv run mypy src/scouting scripts` | 123 source files, no issues | 1.03s |
| `uv run lint-imports` | 5 contracts kept, 0 broken | 0.15s |
| `caffeinate -dimsu uv run pytest -q` | 3,124 passed, 1 known warning | 2,259.60s wall |
| `uv run bandit -q -r scripts src` | pass; one existing `nosec` informational warning | 2.28s |
| Git guard check | pass; simulated push rejected | 0.08s |
| Local-only verifier | 25 checks pass | 1.54s |
| Focused master suite | 73 passed, 1 known warning | 7.50s |
| W09 fixture browser suite | 3 passed, 1 known warning | 9.75s |
| Production Chrome witness | exact authority/query copy; no console/page errors or external requests | 4.0s final witness |

The only pytest warning is the previously known Starlette `TestClient`/`httpx` deprecation. No new
dependency was introduced to suppress it.

## Governance disposition

W09 remains `CLOSED`. W10 remains `REWORK`; formal evidence collection is unauthorised and
unstarted; 08E and 08F are unstarted; G-RW4 remains `INSUFFICIENT_EVIDENCE`. No threshold was
rederived or moved, no participant response or protected label was used, and
`checkpoint/w10-accepted` remains absent.

The approved tag `checkpoint/w10-prestudy-uplift-reviewed` may be created only after the sole
master commit containing this reviewed bundle. It records delivery readiness before human
evidence collection and cannot be interpreted as W10 acceptance.

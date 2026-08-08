# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-REVIEW-04-R4
- objective: Independently review the surgical R4 robustness implementation and adjudicate only defects capable of changing persisted values, populations, applicability, or the later protected gate.

## Files changed

- reports/reviews/W06/evaluation-robustness-independent-review-R4.md
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R4.md

## Summary

- final verdict: **REWORK — 0 P0, 1 P1**.
- the exact R3 stress witness `013da049ef32c63d7bf5d40e825b7d377000cca70fe8b6c86fb2becb05797598` rejects under normal construction.
- the exact R3 control witness `75b2bc182bbd1e72816de51ce7516e1cf1ee2475328aa49cbabca80485699e1b` and arbitrary-authority result `fd55e1eeaf2c977f0aa38156af350fb98f1b56a8b77d50aca10681cec86a74ba` reject under normal construction.
- the exact R4 comparison witness `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb` accepts after changing only Spearman from `-0.19999999999999996` to `0.0`, retaining exact row-derived input digests and re-signing child/parent.
- one P1 remains: numeric metric/comparison children are signed and input-bound but are not exactly recomputed from persisted rows. Aggregate control parent `e67c82c8...7815` and aggregate stress parent `2e70e316...1404` independently accept changed values under the same root defect.

## Narrow constructor and fixture matrix

| Surface | Outcome |
|---|---|
| R3 stress `013da049...97598` | REJECT |
| R3 control `75b2bc18...e1b` | REJECT |
| R3 arbitrary authority `fd55e1ee...a74ba` | REJECT |
| R4 Spearman `fa8bea37...a8fb` | **ACCEPT — P1** |
| Computed stress fixture | all eight computed; split pinned `2fcdf6fd...8725` |
| Sparse fixture | exact unsupported `26e98b12...e6f2a`; deficits `340060f5...69c`, `c06d34b2...a2e` |
| Incoherent fixture | exact unsupported `38310e0b...80e1`; typed deficit `a693ae1b...d706` |
| Common-candidate fixture | exact unsupported `e75bdbe4...35fc`; typed deficits `1e975614...5eb0`, `21e40253...2162` |
| Control results | exact computed coverage/metadata/raw/shuffled-label plus unsupported pair `c8a0c416...727a` |
| Applicability | exact `3fdff230...5445`, `UNSUPPORTED`, no fabricated human evidence |
| Failure register | exact fixture `5dac72fe...17e3`; complete source retained with exact shortfall |

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w06-r4-review-pytest-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: `17 passed in 0.24s`.
- command: packet focused Ruff check with task-local UV/Ruff caches
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-r4-review-mypy-uv MYPY_CACHE_DIR=/private/tmp/w06-r4-review-mypy PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in four source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-r4-review-lint-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- command: `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.
- command: public exact R3/R4 constructor, numeric-child and fixture/closure probes via `uv run --no-sync python`
  - exit status: 0
  - result: exact witness and closure matrix above reproduced.

## Artifacts/evidence

- reports/reviews/W06/evaluation-robustness-independent-review-R4.md
- exact open witness: `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb`
- exact changed comparison child: `2202faddee618ff386a32da44c294d2cf88adc0c2540d9c2dd4bd463aeb9a0cd`
- exact retained inputs: `4113634a8c816a9eac58b6b307266fcda38e326dfc0eb7f659db7dff648b5441`, `3acadf49e014d851cd16d8fe5064b2b2fce2ab23fda98531f661f5b2c2dadd32`

## Risks

- remaining P0 risks: none identified.
- remaining P1 risks: one — persisted stress/control metric and comparison numeric values are not exactly derived from their bound rows and can be substituted after re-signing.
- applicability remains implementation-only `UNSUPPORTED`; no human-expert, protected, transfer, prospective, provider, recruitment-outcome, or positive empirical evidence is fabricated.

## Follow-up items

- Recompute and require exact complete `MetricResult`, `BootstrapInterval`, and `RankComparisonResult` children from persisted rows/protocol/metric/`k`; add exact `fa8bea37...a8fb` and aggregate value/interval regressions.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider/credential access or model tuning: confirmed.
- no implementation edits: confirmed.
- no edits outside `allowed_paths`: confirmed; only the two report paths above were written.

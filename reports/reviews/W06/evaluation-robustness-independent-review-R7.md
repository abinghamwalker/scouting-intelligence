# W06 evaluation robustness independent review — R7

## Verdict

**ACCEPT — 0 P0, 0 P1.** The R7 test-only regression closes the sole R6 P1:
all three original numeric-child substitution witnesses are reconstructed in their
original shapes, each exact parent digest is asserted literally before normal
construction, and each parent is rejected by its owning canonical-derivation
validator. The accepted R6 single-core implementation, contracts and public fixtures
remain unchanged. No defect remains that can change metrics, intervals, partitions,
leakage, applicability or the protected gate.

## Exact three-parent matrix

| Original witness | Exact reconstruction | Literal parent asserted before rejection | Normal-constructor rejection |
|---|---|---|---|
| Metadata-control comparison | Retain the original comparison inputs; change Spearman `-0.19999999999999996 -> 0.0`; re-sign the comparison and metadata-control parent. | `fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb` | `control comparison values must equal canonical derivation` |
| Metadata baseline aggregate | Retain aggregate input identity; change value `1.0 -> 0.0` and numerator `1.0 -> 0.0`; re-sign the metric and metadata-control parent. | `e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815` | `control metric values must equal canonical derivation` |
| Split aggregate and interval | Change aggregate value `1.0 -> 0.0` and numerator `2.0 -> 0.0`; re-link the interval to the changed metric while retaining point `1.0`; re-sign the cohort, every affected comparison cohort link, and the stress parent. | `2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404` | `stress metric and interval values must equal canonical derivation` |

The focused regression is at `tests/unit/test_w06_robustness.py:319-415`; the three
literals occur at lines 339, 359 and 410. A standalone public constructor invocation
also completed with exit `0` and printed the three exact parent/message pairs above.
The owning errors are distinct and prove comparison, control metric, and stress
metric/interval derivation separately.

## R6 one-core and non-change evidence

Complete readback of all required source confirms the accepted call topology remains:

| Surface | Live path |
|---|---|
| General per-query metrics | `core.evaluate_ranking` -> `core._ranking_calculation` -> `evaluation_calculations.derive_ranking_metric_children` |
| General aggregate/bootstrap | `core.bootstrap_interval` -> `core._ranking_calculation` -> the same shared calculation |
| Persisted stress/control metrics | `robustness._cohort` / `robustness.evaluate_control` -> `contracts.evaluation.derive_ranking_metric_children` -> the same shared calculation |
| Stress/control validation | Owning contract validator -> persisted adapter -> shared calculation -> exact child equality |
| Rank comparison | All producers and validators -> `contracts.evaluation.derive_rank_comparison` |

There is still one live ranking metric/bootstrap formula body in
`src/scouting/contracts/evaluation_calculations.py`; the other surfaces are adapters or
validators. Present source-byte identities are:

- `4e3ad86ba01dc07ab382e4ea039ae003b4a9694739637b0021baaa6b712690f4` — `src/scouting/contracts/evaluation_calculations.py`
- `3e37962de45a56aa9e409e5ac6c66ddeade1f28e772d6262220c23cf064c162b` — `src/scouting/contracts/evaluation.py`
- `b3da42cea5a29da6b3098a66053ac2e86dc2a9e4644b3452f8fe71f1a0747bc1` — `src/scouting/evaluation/core.py`
- `34628b5605348d07b2f780dbcb10bf3bd603c9d07f9fc81bdd7e1d78566df63d` — `src/scouting/evaluation/robustness.py`

The R7 implementation packet forbade all source and fixture edits; its mandatory return
lists only the authorized test and return paths; and the supplied master readback records
`changed_paths_scope: PASS`, `implementation_readback: PASS`, and no defects. Current
fixture identities exactly equal the accepted R6 identities:

- evaluation: `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`;
- robustness: `b5354763a57112386e67f60a1fdd0e4f694d9b9053168a68c6bac25ef4598cb6`.

Together, the supplied scope evidence, complete source readback, present source-byte
manifest and exact retained fixture identities confirm that R7 changed no production,
contract, fixture or one-core calculation bytes.

## Commands and results

All Python commands used `uv run --no-sync`, `PYTHONDONTWRITEBYTECODE=1`, a task-local
`/private/tmp` uv cache and public implementation-fixture data only.

| Command | Exit | Result |
|---|---:|---|
| Complete reads of the R7 review packet and every `read_first` path | 0 | All required authorities and complete file contents read before adjudication. |
| `env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/w06-r7-review-uv-cache uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py` | 0 | `19 passed in 0.25s`. |
| `env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/w06-r7-review-uv-cache uv run --no-sync ruff check tests/unit/test_w06_robustness.py` | 0 | All checks passed. |
| `rg -n 'fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb|e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815|2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404' tests/unit/test_w06_robustness.py` | 0 | Exact literals at lines 339, 359 and 410. |
| `shasum -a 256 tests/fixtures/w06/public-evaluation-v1.json tests/fixtures/w06/public-robustness-v1.json` | 0 | Exact accepted R6 fixture identities reproduced. |
| `shasum -a 256 src/scouting/contracts/evaluation_calculations.py src/scouting/contracts/evaluation.py src/scouting/evaluation/core.py src/scouting/evaluation/robustness.py` | 0 | Exact present source-byte manifest recorded above. |
| Standalone public constructor command shown below | 0 | The exact regression executed and printed the three full parent digests with their exact owning messages. |

Exact standalone public constructor command:

```text
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/w06-r7-review-uv-cache uv run --no-sync python -c 'import runpy; module = runpy.run_path("tests/unit/test_w06_robustness.py"); module["test_original_numeric_child_substitution_parents_reject_at_normal_construction"](); print("fa8bea37b980b8761427695e18840789f6ea4da26f63fc73d581d42e8776a8fb | control comparison values must equal canonical derivation"); print("e67c82c8800e1e4c0efa360153cd918f36d21859079ef630b3fe3d2fab477815 | control metric values must equal canonical derivation"); print("2e70e316301230b85db9bae9785c16f431f1cf3a251affd9ba3d792174741404 | stress metric and interval values must equal canonical derivation")'
```

## Remaining risks and scope confirmation

Remaining P0 risks: **none identified**. Remaining P1 risks: **none identified**.
Smallest correction: **none**.

This review used no Git operation, delegation, dependency or lock change, protected
expected-output access, external/provider/network/credential access, model tuning,
destructive action, or source/test/orchestration edit. Only the two authorized report
paths were written.

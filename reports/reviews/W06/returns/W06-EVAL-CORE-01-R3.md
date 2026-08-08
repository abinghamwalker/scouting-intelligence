# Subagent return

## Task

- task_id: W06-EVAL-CORE-01-R3
- objective: Close the retained W06 relational protected-decision, aggregate, metric, comparison and interval/run defects using public-only regression evidence.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/contracts/__init__.py
- src/scouting/evaluation/__init__.py
- src/scouting/evaluation/core.py
- tests/contracts/test_w06_evaluation_contracts.py
- tests/unit/test_w06_evaluation_metrics.py
- reports/reviews/W06/returns/W06-EVAL-CORE-01-R3.md

## Summary

- P0 protected decision chain: `EvaluationAccessRecord` binds the exact protocol, bundle, candidate-manifest, partition and consuming run ID; it requires `one_use=True`. `EvaluationRun` embeds the protocol and access object and verifies every relation. `GateDecision` embeds actual bundle/run objects for claim/narrowing decisions and requires the identical protected relation. `NO_GO` remains constructible without a run. Query feature cutoffs after the protocol cutoff reject.
- P1 canonical aggregate: candidate-universe and bundle candidate-manifest digests are recomputed; rubric and reviewer authority are relational objects; every evidence family has canonical ordering plus identifier and semantic-key uniqueness; unordered preferences are canonical; and adjudication requires same-query/candidate/rubric evidence disagreement and a rostered governed adjudicator.
- P1 metric arithmetic: finite/non-negative-zero ranked scores, protocol tie order, one executable complete-label policy, partial-gain-specific P/R arithmetic, zero-denominator unavailable statuses, and retained NDCG partial gain are enforced.
- P1 comparison identities: low-intersection set metrics are computed before Spearman insufficiency; governed canonical pair and agreement rows carry reviewer/evidence identity and deterministic result identities.
- P1 persistence/intervals: typed metric arithmetic/ranges, protocol metric/k membership, typed protocol-bound bootstrap intervals, canonical result/interval order, supported query-resampling capability and linked primary gate requirements are enforced.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: `6 passed in 0.20s`; covers each retained P0/P1 family, including public fixture digest and fixture-to-metric execution.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-core-r3-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-core-r3-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: `Success: no issues found in 3 source files`.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: `Contracts: 3 kept, 0 broken`.
- command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python -c 'import runpy; from scouting.contracts.evaluation import GateDecision, GateDecisionKind, _digest; ns = runpy.run_path("tests/contracts/test_w06_evaluation_contracts.py"); bundle = ns["public_bundle"](); result = ns["metric_result"](); access = ns["model"](ns["EvaluationAccessRecord"], {"access_id":"access","protocol_digest":bundle.protocol.protocol_digest,"bundle_digest":bundle.bundle_digest,"candidate_manifest_digest":bundle.candidate_manifest_digest,"partition":ns["EvaluationPartition"].FIT,"accessor_key":"operator","purpose":"public-test","accessed_at":ns["NOW"],"one_use":True,"consumed_by_run_id":"run"}, "access_digest"); interval = ns["model"](ns["BootstrapInterval"], {"metric_result_digest":result.result_digest,"point_value":1.0,"resample_digest":"a"*64,"seed":7,"resamples":5,"confidence":0.8,"method":ns["BootstrapMethod"].PERCENTILE,"lower":1.0,"upper":1.0,"status":ns["MetricStatus"].COMPUTED}, "interval_digest"); run = ns["model"](ns["EvaluationRun"], {"run_id":"run","protocol":bundle.protocol,"access":access,"bundle_digest":bundle.bundle_digest,"candidate_manifest_digest":bundle.candidate_manifest_digest,"partition":ns["EvaluationPartition"].FIT,"metric_results":(result,),"intervals":(interval,),"slices":(),"failures":()}, "run_digest"); gate_payload={"gate_id":"nogo","decision":GateDecisionKind.NO_GO,"protocol":bundle.protocol,"claim_boundary":"resemblance_only","reason_codes":("public-only",)}; gate_payload["gate_digest"]=_digest(GateDecision.model_construct(**gate_payload).model_dump(mode="json"), "gate_digest"); gate=GateDecision(**gate_payload); print(bundle.protocol.protocol_digest, bundle.bundle_digest, result.result_digest, interval.interval_digest, run.run_digest, gate.gate_digest)'`
  - exit status: 0
  - result: public-only protocol, bundle, result, interval, run and `NO_GO` gate identities printed; no protected file or output was opened.
- final source-state command: `UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py && UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-eval-core-r3-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py && UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-eval-core-r3-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation && UV_CACHE_DIR=/private/tmp/w06-eval-core-r3-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: 6 focused tests passed; Ruff, mypy and import-direction checks passed.

## Artifacts/evidence

- public fixture: `tests/fixtures/w06/public-evaluation-v1.json`; SHA-256 `f1f64f9a241318d8bfcec110355c4e4437616e832984beed9b97139f87599cb6`; loaded and passed through `evaluate_ranking` and `bootstrap_interval` in the focused suite.
- public test protocol digest: `477818391e3d57071cf52251a0792cb80cb71d8926ba0df82ff21ca55cee4528`.
- public test bundle digest: `fbdf359ddb31f6e9e2e8d1b543fecd1be9a933b3060dd346d8c469c9113abbfd`.
- public test metric result digest: `c77f9e7c23b3f9c915460bcdd470ed1b836e76bc86880dae4d334f2e260fa461`.
- public test interval digest: `ff698667d2a60e7ae3196594d0054d5bec6449c5014e116a8a4671c81951a4ce`.
- public test run digest: `1eb6b7fa4d0b47e65ca2ad0c0875272f9271f42c110f1c928e105e9ee7087aeb`.
- public test `NO_GO` gate digest: `c11d7ad4c7d5b603648f86d079d6d55cc620101d4edeeac22a3c77b055fabd69`.

## Risks

- Leakage/access: no protected result, population, access record, threshold or positive gate claim was constructed from evidence. Future protected execution still needs master-owned access consumption and independent review.
- Schema: the R3 relational surface intentionally changes evaluation constructors; downstream callers must migrate only under a separately authorised integration task.
- Interval: percentile intervals validate supplied resample identities and settings; independent recomputation of production resamples remains a future execution/gate concern.
- Applicability/claim: `NARROW_APPLICABILITY` and `ACCEPT_CLAIM` require a valid protected nested relation, but no applicability threshold or positive claim was defined here.

## Follow-up items

- Master/reviewer: independently challenge the public structural P0 chain and, if later authorised, perform protected execution separately. No protected evidence is available from this packet.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no edits outside `allowed_paths`: confirmed.

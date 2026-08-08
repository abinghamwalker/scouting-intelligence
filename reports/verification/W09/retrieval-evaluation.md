# W09 frozen retrieval evaluation

## Decision

`W09-EVALUATION-06` is accepted as deterministic engineering evidence over the retained
historical population. It is not football-relevance or recruitment-usefulness evidence.

## Frozen authority

- Suite: `w09-frozen-retrieval-evaluation-v1`
- Suite digest: `1c922dafed2d7bdd773ad104ae2700330f0262da80a1e2e67327c5bcb6e8adc1`
- Evaluation digest: `835e31f1eb2ba0e7dc0456c3dca9a5918fb82c278567f00247aa26bf8a5da9c0`
- Matrix version: `w09-historical-player-window-v1-a31511705ac15a5d`
- Matrix semantic digest: `428d25ed4f1fd5dec7df74f30905db875cd548270fc2824b431e1bc8a6447cc1`
- Matrix manifest digest: `dda2588f7ad81443aac614a359fbda1fcb60e533ca0d56db5d59e4669a754692`
- Index version: `w09-historical-player-index-v1`
- Index manifest digest: `30c2b6c1e0d65c8214860131f690b8b6cac05fe317ffa208a2785e11160eb0bc`
- Published evidence:
  `runs/w09/evaluation-v1/835e31f1eb2ba0e7dc0456c3dca9a5918fb82c278567f00247aa26bf8a5da9c0.evaluation.json`

The master executed the production loader and frozen suite into the governed output root. The
Unicode correction rebound the frozen suite to the corrected text-bearing authorities. Player
IDs, candidate order, ranks and scores are identical to the superseded evaluation.

## Results

- Nine real-player cases cover exemplar and weighted-profile modes, weighted Euclidean and
  weighted cosine methods, all four positions and all five eligible domestic competitions.
- Each query was executed twice at distinct frozen generation timestamps and reproduced result
  identity, semantic digest, candidate order, scores, explanations, warnings and population
  accounting.
- Nine explanation witnesses independently reproduced the median/IQR-linear scaler, raw and
  scaled contrasts, Euclidean or cosine contribution terms, zero-weight behaviour, aggregate
  scores and deterministic tie ordering.
- Fifteen filter witnesses cover exemplar self-exclusion, position, policy-floor and stricter
  minute thresholds, explicit exclusion, full scoring before limit and empty admission.
- Two bounded weight perturbations retained all five top candidates. Their mean union-rank
  displacement was `0.4` and `0.0`; these are observations, not quality thresholds.
- Coverage reconciles 1,975 eligible rows, 1,965 unique eligible players and 3,603 source players.
  The suite returned 30 unique real grains and recorded 2,841 full-population score evaluations.
- Retained matrix rows by competition reconcile to England 389, France 402, Germany 352, Italy
  409 and Spain 423.

## Independent master checks

The master inspected the implementation, configuration, CLI, unit tests and retained integration
tests, then reran:

```text
uv run ruff format --check <evaluation paths>     PASS
uv run ruff check <evaluation paths>              PASS
uv run mypy <evaluation source and CLI>            PASS
uv run pytest -q <evaluation and serving tests>    17 passed
.venv/bin/bandit -q -r <evaluation source and CLI> PASS
uv run python scripts/evaluate_w09_retrieval.py \
  --output-root runs/w09/evaluation-v1             PASS
```

## Claim boundary and weaknesses

- Historical resemblance is not football relevance or recruitment usefulness. No relevance
  labels or expert judgements exist.
- Every eligible row uses conservative lower-bound minutes, so per-90 rates may be overstated.
- The population is five retained 2017/18 domestic competitions, not current-market coverage.
- The two frozen perturbations do not establish general robustness or a football-acceptable
  threshold.
- `G-RW4` is absent. No football-quality, recommendation, value, availability, fit or outcome
  claim is supported.

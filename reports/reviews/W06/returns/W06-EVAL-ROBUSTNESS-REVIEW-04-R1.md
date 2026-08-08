# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-REVIEW-04-R1
- objective: Independently verify that W06 R1 robustness, null, missing-population,
  applicability and failure-register behavior is real, protocol-bound and fail-closed.

## Files changed

- reports/reviews/W06/evaluation-robustness-independent-review-R1.md
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R1.md

## Summary

- verdict: **REWORK**
- findings: **0 P0, 7 P1**
- Every computed stress kind used the unchanged full-population bootstrap input and
  retained zero comparisons. Split, window, threshold, walk-forward and leave-group
  transformations were not executed; chronology/minima were global and incomplete.
- Source comparison accepted two providers with disjoint candidate universes because the
  exact intersection is never computed.
- Controls reject valid nonalphabetic rank order; non-null controls have no declared
  evidence input; shuffled-label and shuffled-pair both shuffle candidate order.
- Specifications/results are not fully protocol/inventory/child-bound; failure registers
  do not bind a full source population; applicability trusts a caller boolean.
- The public fixture is label-only and the focused robustness tests never invoke the
  stress executor or controls.

## Master counterexamples and exact evidence

| Counterexample | Outcome | Severity | Independent evidence |
|---|---|---:|---|
| split `c1cbcf5b1968e11aa6473c9ca9a914b487c96a841fd7233d425ade298db3f177` | OPEN | P1 | semantic twin `66cbe9d4882755ee760839061da8bdc82a2e1c3fa41a6f9459d3821ba75c6902`: four query rows, `COMPUTED`, value `0.5`, denominator `4.0`, comparisons `0` |
| intersection source `f0f0afb88df883815037246a21e3ae384eb461c0b7286c9e18100c627bd15cca` | OPEN | P1 | semantic twin `0dc3d3a6f2bccdda1f26f7528e084e250fc71624ff15433b9ef4d2b1b6262510`: provider intersections `{}`, `COMPUTED`, comparisons `0` |
| register `31f5ab91dafe4377b5ec94b837a2cb01634e4d0883405ed25d39ee90abb99056` | OPEN, exact digest reproduced | P1 | 10 supplied cases accepted with total `100`, shortfall `0` |
| applicability `ed497952ab334aeac02d2f0f7e513e78fa31137a458583353cdade96b5ca31e2` | OPEN, exact digest reproduced | P1 | one competition/team/provider/window plus caller `True` omits mandatory-transfer deficit |
| specification `6599b30a7fb0334dc64c7001de9abc2a8722a1bcce86f91cb7557f74199bf42b` | OPEN | P1 | fresh agreement/k=999 normal-constructor witness `e8261a80778f461e3bdf49ee71517a2f59f177f637e0b1c9b468fb3410540ecf`; substituted inventory returned computed result `a48165bece4f6e8789f79a99ecb66e1946fef822fbb8d47d0300ce302bc10cdf` |
| ordered and shuffled controls | OPEN | P1 | `(beta,alpha)` rejected; label/pair nulls share candidate permutation and comparison `32cbafb4333c788a7c9b694c63211604252d3abfcc5a4d980f0e9863784b6551` |

The master packet did not provide the canonical preimages for its split, source or
specification hashes. Exact identities are retained above, unchanged accepting code paths
were read back, and independent semantic twins reproduce all three behaviors. The two
fully reconstructable master preimages reproduced byte-for-byte.

## Stress/control/constructor matrix

- Computed stress result digests, in enum order: split
  `7b3105a62b26499705ad6a29da2f842bc309511294728138dd06daa79e9829d7`,
  rolling `1332a304739b43a581f20312756f5756e2e4ba5bdaaf38a1f2c739b867e16bc2`,
  minutes `e905b908c07e5e55337a39f2392aa26beba9053c2d76a77ae91e566bc5769a3b`,
  walk-forward `f798728de444d38cbcc08b0f38131dbd8a5c814acda5f69c79ef58eff0b9dc8d`,
  leave-competition `d4eedf4f4cf929ccea52cee4c84c7af639e87d8ec6bdef5e30d06c1b95df08df`,
  leave-team `d0ae624f4f097ef17d3f0e8c7b8557d6d10228a240f7da737e80e475d6fad528`,
  leave-provider `1524f9c40cf93c86e9e56a2297469d3f8c6d34abe83de04cd5694717213d220c`,
  source-intersection `ccae405b7d897aa48943f48f2ecd6fd8c96bf81cc2a88597d56b8d0531544e03`.
  Each retained full-population input `fbe0e51f...22a7afe`, value `0.5`, denominator
  `6.0`, comparisons `0`.
- Unsupported one-query outcomes, in the same order: `978c9311...567f` (split count and
  empty half), `a6da80ba...c7ac` (one/three windows), `96484963...23a` (90-minute
  population zero), `e73c9b53...9b4b` (one/two windows), `4ac4669a...218d` (one/two
  competitions), `c0407066...289c` (one/two teams), `2478e460...b17e` (one/two
  providers), `92f57f8f...f438` (one/two providers; zero-intersection deficit
  unreachable).
- Controls: coverage `546b99d3...146f`, metadata `f424b83d...b0b1`, raw Euclidean
  `6654401a...f38`; all share unchanged comparison `8bb8bd38...ebd1`. Shuffled label
  `e15f42bc...9a53` and shuffled pair `6d6c6b9c...80c0` both use candidate permutation
  `(alpha,delta,beta,gamma)` and comparison `32cbafb4...6551`.
- Constructors: governed inventory binds query rows but no provider candidate roster or
  coherent chronology; stress specification accepts agreement/k=999; stress result
  accepts zero comparisons and does not link interval-to-metric/specification; control
  result binds only comparison protocol; register accepts false total `100`; applicability
  suppresses transfer via caller boolean.

## Tests run

- command: `UV_CACHE_DIR=/private/tmp/w06-robust-review-pytest-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: 14 passed in 0.21s.
- command: `UV_CACHE_DIR=/private/tmp/w06-robust-review-ruff-uv-cache RUFF_CACHE_DIR=/private/tmp/w06-robust-review-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/private/tmp/w06-robust-review-mypy-uv-cache MYPY_CACHE_DIR=/private/tmp/w06-robust-review-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in four source files.
- command: `UV_CACHE_DIR=/private/tmp/w06-robust-review-lint-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- command: `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: `3faba3693b28c887b0d411f0ac300fbfb166a1230727c06eeb319095ca26c549`.
- command: public inline full computed/unsupported stress, control, constructor,
  source-intersection, chronology, inventory-substitution, register and applicability
  probes via `uv run --no-sync python - <<'PY' ... PY`
  - exit status: 0
  - result: exact matrices above.
- command: `rg -n 'evaluate_stress_test|evaluate_control|StressTestResult|DeterministicControlResult' tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 1
  - result: zero matches (the evidence command wrapped this expected miss to exit 0).
- command: `test -s reports/reviews/W06/evaluation-robustness-independent-review-R1.md`
  - exit status: 0
  - result: independent review exists and is nonempty.
- command: `test -s reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R1.md`
  - exit status: 0
  - result: mandatory return exists and is nonempty.

## Artifacts/evidence

- reports/reviews/W06/evaluation-robustness-independent-review-R1.md — full independent
  verdict, source locations, exact matrices and bounded correction.
- tests/fixtures/w06/public-robustness-v1.json — public-only fixture; SHA above; contains
  no executable robustness inputs.

## Risks

- Result/population: high; a computed result does not prove its named transformation.
- Null/control: high; shuffled outcomes are not represented and valid order is rejected.
- Register: high; omitted cases and claimed totals are not cryptographically bound.
- Applicability/gate input: high; a caller boolean can suppress mandatory transfer
  deficits, and stress results can present unchanged full-population scores as computed.
- Claim boundary: still public implementation-only and unsupported; no empirical or
  positive claim is established.

## Follow-up items

- Smallest bounded correction: implement and persist the exact partition/comparison for
  every stress kind; model provider candidate intersections and chronology; bind
  specifications/results/registers to protocol and full populations; provide actual
  control inputs and shuffle governed labels/pair outcomes; derive applicability from
  exact results; replace the label-only fixture and add every computed/unsupported branch.
- Obtain a fresh independent review after bounded producer rework.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider/credential access: confirmed.
- no edits outside `allowed_paths`: confirmed; only the two authorized reports were
  created.

# Subagent return

## Task

- task_id: `W06-EVAL-ROBUSTNESS-REVIEW-04-R2`
- objective: Freshly verify the R2 seven-P1 correction and challenge whether transformed
  stress evidence, controls, fixture authority and applicability remain lineage-bound
  under normal constructors.

## Files changed

- `reports/reviews/W06/evaluation-robustness-independent-review-R2.md`
- `reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R2.md`

## Verdict

- **REWORK — 0 P0, 7 P1.**
- Detailed evidence: `reports/reviews/W06/evaluation-robustness-independent-review-R2.md`.

## R1 closure matrix

| R1 class | Fresh R2 disposition |
|---|---|
| transforms scored unchanged population | named execution cohorts now exist, but persisted row/child proof remains open through exact R2 stress witness `5edc056a4aa5d317642b1efd22e490eac2ff4a849b3f51d770babaa75f91d3f8` |
| empty source intersection computed | closed: disjoint providers return only `exact_candidate_intersection=0`, result `4d0e5c97c9e057c72e372ae469f10f33299cdd857952aa3c041a8c7eb6a0e2fd` |
| controls rejected score order / shuffled candidates | score-desc nonalphabetical ranking and label-preserved candidates close; shuffled-pair remains open through `96da14ddc305f67058a90a095b399ac428900a2b95d95fee129b420c6b861776` |
| specification/result substitutions | k=999 and inventory substitution close; foreign result children remain open through `5edc056a...d3f8` |
| failure register `31f5ab91...9056` | closed: obsolete exact shape rejects for missing complete source and current totals derive from it |
| caller-suppressed applicability `ed497952...1e2` | obsolete boolean closes; caller claim fields and trusted reasons remain open as `6497964c48f108a1c8046b96400b30573b85bd267b0f6a68f532a050558e78a0` and `cc0b50afc3667a52f5aec0df9810cf31f7f56e4b09e6faf5ffd8c4c189f71263` |
| label-only fixture | open: fixture still supplies no executable observations, scores, labels, pairs or kind-specific inputs |

## R2 master-counterexample matrix

| Master witness | Exact outcome | Severity |
|---|---|---:|
| split foreign children, `bb...bb` rosters, `cc...cc` common candidates | exact normal-constructor result `5edc056a4aa5d317642b1efd22e490eac2ff4a849b3f51d770babaa75f91d3f8` accepted | P1 |
| metadata arbitrary `input_digest=bb...bb` | exact normal-constructor control `a2fc46a61a5b5408bc1d2bc1e4cf53aec4adbf8cab202b7fb30b17ccdddb97fa` accepted with unchanged baseline/null/comparison children | P1 |
| fabricated one-pair null | exact control `96da14ddc305f67058a90a095b399ac428900a2b95d95fee129b420c6b861776`; permutation `queryone|pair|pair`; baseline=null=`1.0` | P1 |
| metadata/raw/coverage authority | same generic rows produce identical baseline `e20a2424...8a27`, null `d97634df...172a` and comparison `dea2ae96...eb87`; only caller enum/outer digest differs | P1 |
| applicability fields/reasons | normal claim-field forge `6497964c...78a0`; caller deficit produces assessment `cc0b50af...1263` | P1 |
| public fixture lineage | SHA `0f369d628b9d9ad714d62b35c0b7bebd4f345c9e2fae76f333c0d80fd77565e8`; no executable rows/labels/pairs/baseline inputs, and tests hard-code them | P1 |
| additional walk-forward boundary | result `766f1df2...f826` omits all middle-window observations and is invariant to their ranking changes | P1 |

## Execution matrix

| Stress kind | Result | Cohorts / comparisons | Disposition |
|---|---|---:|---|
| split | `ba4512d1...92bc` | 2 / 2 | computes; persisted children substitutable |
| rolling | `a4b15e55...e918` | 3 / 4 | computes |
| minutes | `36abac84...4efe` | 2 / 2 | computes |
| walk-forward | `766f1df2...f826` | 2 / 2 | computes endpoint sample; middle omitted |
| leave competition | `c0d8ef5b...aa06` | 2 / 2 | computes |
| leave team | `481116c9...c16e` | 2 / 2 | computes |
| leave provider | `480ad514...f631` | 2 / 2 | computes |
| source intersection | `4914acf9...4481` | 2 / 2 | computes exact non-empty intersection; disjoint case closes |

## Commands and results

- `UV_CACHE_DIR=/private/tmp/w06-r2-review-pytest-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: `15 passed in 0.19s`.
- `UV_CACHE_DIR=/private/tmp/w06-r2-review-ruff-uv RUFF_CACHE_DIR=/private/tmp/w06-r2-review-ruff-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: all checks passed.
- `UV_CACHE_DIR=/private/tmp/w06-r2-review-mypy-uv MYPY_CACHE_DIR=/private/tmp/w06-r2-review-mypy-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in four source files.
- `UV_CACHE_DIR=/private/tmp/w06-r2-review-lint-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: `0f369d628b9d9ad714d62b35c0b7bebd4f345c9e2fae76f333c0d80fd77565e8`.
- public exact R2 constructor probes via `UV_CACHE_DIR=/private/tmp/... PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python - <<'PY' ... PY`
  - exit status: 0 for every probe
  - result: exact stress, control and pair master hashes reproduced; applicability and walk-forward witnesses above reproduced.
- `test -s reports/reviews/W06/evaluation-robustness-independent-review-R2.md`
  - exit status: 0
  - result: detailed review exists and is non-empty.
- `test -s reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-REVIEW-04-R2.md`
  - exit status: 0
  - result: mandatory return exists and is non-empty.

## Risks

- Result risk: stress/control children can be substituted without their exact input rows.
- Population risk: walk-forward omits intermediate declared observations.
- Null risk: fabricated governed-human identity and a one-pair identity permutation compute.
- Fixture risk: JSON bytes do not drive executable identities.
- Applicability/claim risk: population, exclusions, non-claims and deficit sources are not
  fully derived, and missing governed pair evidence can be suppressed.
- Public evidence remains implementation-only and supports no human-expert, protected,
  transfer, calibration, prospective, provider, recruitment-outcome or positive claim.

## Follow-up items

- Smallest bounded correction: embed/derive exact stress and control inputs; introduce
  typed governed authority for each control kind; bind pair evidence to a governed roster
  and reject insufficient/identity permutations; derive all applicability fields and
  reasons; make fixture bytes executable; and freeze a complete walk-forward fold/cutoff.
- Obtain a fresh independent review after correction.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output access: confirmed.
- no external/provider/credential access: confirmed.
- no edits outside `allowed_paths`: confirmed.

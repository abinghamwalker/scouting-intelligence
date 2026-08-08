# Subagent return

## Task

- task_id: W06-EVAL-ROBUSTNESS-04-R2
- objective: Close every R1 robustness P1 with protocol-bound transformed cohorts, evidence-specific nulls, complete failure lineage and result-derived fixture applicability.

## Files changed

- src/scouting/contracts/evaluation.py
- src/scouting/contracts/__init__.py
- src/scouting/evaluation/robustness.py
- src/scouting/evaluation/__init__.py
- tests/contracts/test_w06_robustness_contracts.py
- tests/unit/test_w06_robustness.py
- tests/fixtures/w06/public-robustness-v1.json
- reports/reviews/W06/returns/W06-EVAL-ROBUSTNESS-04-R2.md

## Seven-P1 closure matrix

| R1 class | R2 closure |
|---|---|
| Transforms scored the unchanged population | Each computed result persists exact transformed observation cohorts, accepted-core metric/interval children and all declared cohort comparisons. |
| Empty source intersection computed | Inventories bind provider candidate rosters; source execution and contracts require the exact non-empty intersection. |
| Controls changed candidates | Ranking controls preserve score rank/candidate identity; label nulls permute labels and pair nulls permute preferred sides within query groups. |
| Specification/result substitutions | Specifications embed exact protocol and inventory; cohort, interval, comparison and result validators bind every child. |
| Forged failure total | Registers retain the complete ordered source, source digest, derived total, worst ten and shortfall. |
| Caller-suppressed applicability | Applicability takes the complete canonical stress/control roster and derives all missing reasons; no caller boolean exists. |
| Label-only fixture/tests | The public fixture declares executable computed/unsupported populations and all mandatory kinds; focused tests execute all branches and pin public identities. |

## Public identities

- fixture SHA-256: `0f369d628b9d9ad714d62b35c0b7bebd4f345c9e2fae76f333c0d80fd77565e8`
- computed stress result identities in enum order: `ba4512d1ebb9438f80c056cc857fcda578bfbb4a8c9aa4946363449fdff592bc`, `a4b15e555d9bb17acb7b7d9dd5d7bb59a7f94a717af83941ef350c93e16ee918`, `36abac8456947a7d91fe374669cf9c18223428e014dffd7ee69007364cf94efe`, `766f1df254e1714c72a8723229c56d909902b72a94c40af9bd4d7c8f3df7f826`, `c0d8ef5b25ce34cd77a7dbcd6e2837f4006299e98b0af3620432d525e3e6aa06`, `481116c9bf87ea8467b402f58bf3f7a1c20c4f2cc317834301c6c54510d2c16e`, `480ad514e24923ba3e96539565bbb419b4a4e8de79cef5b7bb6836e3fdcef631`, `4914acf9c5aee16baedae1fd9747098c34a305d007708d4dd52baed542744481`.
- split-half cohorts: `f69d2c7d5f84a2d35fe3f8d1bc7c65e8a7d13841c0736580cf8db1d4e9218fa9`, `c35cd26f990b54aed3092105e7ce148a29b03d93422fbdb6375dbcc8a6cdde3c`; comparison identities: `62114d6b2223d38abb7c9787c01c306b4c1c68c7b0d65a5b8aa2f98d8ce55e74`, `9da7cbeac1ac0602fd246a0d4f4ac45d164346a72e2038fdd4b49f46bd977a5f`.
- rolling cohorts: `6bbf9487969955b3b2dd985c37e34a7bf9962c92ee4edb36dcf4e5d7f07a94cd`, `0feb08a1123708359261099c50aa4988f337e5f61888292288003e06ea272c8e`, `9ed74f993b8b197fbcecedb3125dc1c908ab2a5b361ec50e21823e2bde8579ae`; comparisons: `97b2f431df30ec4205d32ebcfbccc9cd2babb43c84c7f7292346c1758c9eae0d`, `f1b479c594572e4cb1a44edd410c37d6c87e4c9432c018181fd4840502c84474`, `9ce22662044c5652a7026e30b40f22026319e502ef11e99b50129754b70bd170`, `ca39a1a27ef152460d9629cb0580a669eea4f69b086cad09254163fb18101ace`.
- minutes cohorts: `2a2a85bfa57cd731e3f5d342d2b2af26e9b98de6e47478051e2ad029a052876f`, `38cde410e281e20b48e805bf4e6219558e459183b2f0afb6ecfa039325fa6cc2`; comparisons: `90c3e62ee3c2e3e386c88338d605caa300548138aa0dec88977a6fddbcd5ff17`, `e34d69f90f0604de19e1404a6110782261162424b5dc854aa837ec63ff87b961`.
- walk-forward cohorts: `8de604ae4e64d13d050a9d0b7280e8d1897c27d1ff4e1a264248d96cec1fecb5`, `3edaa50d5b38e30dd9355df64af0a4bd9595c92e2ca90fa694f0e3f8e45b462a`; comparisons: `4938c022f41e25550c3cf1df0d5cbbbe99a4b4f9b12497599313632433a68d16`, `fcafbc7c0a8f43fbfbfe9ed2c104afa18f3ad39be4da74e91580d99566524e3e`.
- leave-competition cohorts: `16ede8ce7f3351c9a7d16e321cbf901e5584e8395279242e3ba6509b7c6f1046`, `43483503785bf9b1ce75eb3d7582f72a2c4049d566edc52f7d1d114d8b0922c4`; comparisons: `3bafde97e3a1a56fd5d42b73e92224a5737a8675b4742e25d1f04bbe42204b1a`, `eb6f7ddab354c3c1f105e004075f0a573df08a6a51072930bced597aab99ce90`.
- leave-team cohorts: `a6b840805ddd6e1e44285d1fa70e4f605e754305e1607104147f5b025dee10f6`, `42b90c06d1ec231f692f3c3fd56ffcfe260904bb0c8e9da0086a5f248a8ffb18`; comparisons: `adfb88becd174f0fe54166ece6a078005634158834df2d7c7714caa4f38d5892`, `db8ca0c5e5b2c1306cf49fa946c7c595ab1bf7d3410c13b479b12d5bc554c9a9`.
- leave-provider cohorts: `052555235f9aecc57070e7d7b38385d5336cf1d9607887b3176ba9afbfbab267`, `83be9b0d210b120e2a16bc176149fce5183d6622b9b20adca10f1d5888be8c50`; comparisons: `c5775877a92c425d04f8a768468bb17701736e62937057f7138d914f503fb95e`, `9126e66e598159dcfc9aa38a294350dc1da1cb05e714e9adbc6fb20be789bc2a`.
- source cohorts: `7f8ffb73f3df1b2a76d1f556c4a2b3ad1791375efc7375c64633dc53f161de61`, `5195196db56b46d1fd3094c0dda275c635f2d8e861aee51c087ab3a70ba46fdc`; comparisons: `86c20dd7c8df3962ac437fa66425052bf2a289e0f3d40f86bf454dbb09e4a141`, `1ded49166b94dbca3c26286b902e95df846dfb43f8dd190d5fc69970100095f2`.
- unsupported split-half identity: `94519ef47eb44cd1073cfe10ff4d7bf63eb27113b5ae6108af50ca5332bda1f4`, deficit `query=queryone:eligible_observations=2<4`; zero-intersection source returns only `exact_candidate_intersection=0`.
- ranking-control identities (coverage, metadata, raw, shuffled-label): `945d7f18a22555b20323322c07aa24c3528b215564e73bde2787664d71fe1878`, `cf72d73dac3fb30b362a0b70807e976620efee18d563c346d8ccd5d8d27486c3`, `4bb1a98ef858630c2c2ea13dd04b57e87d0b021a03826b1922c4af440e87d868`, `4ad2d98334f99612b056eaf044b7277309efb94a9ee56960bb6499f1d96c41a4`.
- shuffled-label baseline/null/permutation identities: `e20a2424a0e8120aa200dd0e0129cf06a53872a4dd62dffcb97912052b3c8a27`, `d2213c020ac21d761fc0eedb09d45a04f56bb92be20773799b4d9be4ff50c772`, `a67bc397e88b775678aaae6009e950ce60a3365de661128afa6fe3feae019585`.
- failure source and applicability are content-addressed by their canonical embedded objects; the R1 forged digest `31f5ab91dafe4377b5ec94b837a2cb01634e4d0883405ed25d39ee90abb99056` and caller-suppressed digest `ed497952ab334aeac02d2f0f7e513e78fa31137a458583353cdade96b5ca31e2` reject because their obsolete caller-controlled shapes are forbidden.

## Tests run

- command: `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: `15 passed in 0.21s`.
- command: `uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation`
  - exit status: 0
  - result: no issues in four source files.
- command: `uv run --no-sync lint-imports`
  - exit status: 0
  - result: three contracts kept, zero broken.
- command: `shasum -a 256 tests/fixtures/w06/public-robustness-v1.json`
  - exit status: 0
  - result: fixture SHA-256 above.

## Risks

- Public fixture evidence remains implementation-only. It establishes no human-expert, protected, transfer, calibration, prospective, provider, recruitment-outcome or positive empirical claim.

## Follow-up items

- Obtain the required fresh independent review; otherwise `none`.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no protected expected-output or external/provider access: confirmed.
- no model/protocol tuning: confirmed.
- no edits outside `allowed_paths`: confirmed.

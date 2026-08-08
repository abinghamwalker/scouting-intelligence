# Subagent return

## Task

- task_id: `W04-SOURCE-COMPLETION-INDEX-01-R3`
- objective: Close only `W04SCIIDXR1-P1-001` by making the exact accepted
  completion-reader comparison an executable prerequisite for authorized checked
  Action, Possession, Fact, Gold, and layer-manifest construction.
- disposition: `IMPLEMENTED_FOR_MASTER_AND_INDEPENDENT_REVIEW`

## Files changed

- `src/scouting/sources/wyscout_completion_index.py`
- `src/scouting/contracts/wyscout_data.py`
- `tests/unit/test_wyscout_source_completion_index.py`
- `tests/contracts/test_wyscout_data_contracts.py`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R3.md`

## Summary

- Added identity-registered, opaque in-process completion capabilities issued only
  after `validate_match_period_population` or `validate_match_population` succeeds
  against the accepted index. Direct construction, unregistered substitution,
  copy/deepcopy, and pickle replay fail closed.
- Added identity-registered checked-product handles and authorized checked builders
  for `SilverAction`, `SilverPossession`, `SilverPlayerMatchFact`,
  `GoldPlayerWindow`, and `LayerManifest`. Raw contract models remain explicitly
  `semantic_only_unchecked`; `require_checked_product` accepts only an authentic
  registered handle of the exact requested product type.
- Checked Action construction injects the exact reader-issued period sequence.
  Possession, Fact, and Gold construction accepts only transitively checked inputs
  bound by capability identity to the exact completion scope. Caller-selected
  sequence, source-row, action-ID, fact-key, or other derived fields are rejected or
  recomputed at the checked boundary.
- Checked full-match Fact construction requires all validated row-player actions
  across the match. Checked Gold derives its exact source rows and contributing fact
  keys from checked Facts.
- Checked manifests now use the exact non-empty completion scopes supplied for the
  bounded build, rather than the over-strict partial requirement to validate all
  3,652 index periods globally. Completion capabilities must be authentic, unique,
  non-overlapping, and share the accepted index binding. For Silver/Gold, the supplied
  scope identities must exactly equal the union of contributing checked-product
  scopes; omissions, extras, substitutions, product mismatches, and raw manifest
  objects fail closed.
- Added a real accepted-index positive test using match `2499719`: all `1,768`
  source actions and both indexed periods are compared before checked
  Action -> Possession -> Fact -> four-feature Gold -> one-match Gold manifest can
  return accepted handles. The same test rejects direct/raw models at every
  downstream boundary, copied/replayed handles, omitted/extra/overlapping/unissued
  manifest scopes, and raw product substitution.
- Preserved the accepted index address
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`,
  all strict integer/no-coercion, equal-clock group-first, causal provenance,
  dependency-lineage, six-coverage-authority, and exact four-feature behavior.
- Current implementation/test identities before this return was added:
  - completion source:
    `22d825631af0d27d1583a79ce4bb8adb10643bb32fe139630871727f814f1415`
  - contract source:
    `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932`
  - completion-index unit tests:
    `5beb37ee5fffadcab1d7355b879fcb65b76816b969c5581a943b1096afd98580`
  - Wyscout contract tests:
    `7ef542d5ed65437683063e2980e08a94b260771405147a860ca5d4541f1c004b`

## Tests run

- command:
  `uv run ruff format --check src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: four files already formatted.
- command:
  `uv run ruff check src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: all checks passed.
- command:
  `uv run mypy src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py`
  - exit status: `0`
  - result: no issues in four source files.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 31 files and 49 dependencies analyzed; all three import contracts kept.
- command:
  `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit status: `0`
  - result: `495 passed in 82.38s`.
- command:
  `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py::test_real_match_checked_path_reaches_gold_and_exact_scoped_manifest`
  - exit status: `0`
  - result: `1 passed in 17.04s`.
- command:
  `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py`
  - exit status: `0`
  - result: no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all 25 controls passed, including zero configured remotes,
    local push guard, one root uv project, Python 3.12, and no cloud/container/hosted
    CI/deployment surface.

The first combined final static-check invocation was denied before execution because
the sandbox could not read existing shared uv-cache metadata under
`~/.cache/uv/sdists-v9/.git`. The unchanged commands were rerun with read permission
and passed. No dependency or environment mutation occurred.

## Artifacts/evidence

- mandatory producer handback:
  `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R3.md`
- accepted immutable source-completion index:
  `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
- positive executable regression:
  `tests/contracts/test_wyscout_data_contracts.py::test_real_match_checked_path_reaches_gold_and_exact_scoped_manifest`
- direct/replay/substitution regressions:
  `tests/unit/test_wyscout_source_completion_index.py::test_exact_match_comparison_issues_opaque_nonreplayable_capability`
  and the final R3 contract-test block.

## Risks

- The capability is intentionally process-local and identity-based. It is not a
  serializable authority artifact; a process restart must repeat the accepted reader
  comparison, which is the required fail-closed behavior.
- Checked handles expose a semantic contract value only after authentic verification.
  Future product serializers must accept the checked handle and invoke
  `require_checked_product`; accepting the returned raw value as independent authority
  would recreate the reviewed bypass. No product serializer exists or was added here.
- The real one-match checked regression takes about 17 seconds and retains complete
  match-period sequence evidence. This is bounded W04 acceptance evidence, not a
  performance claim for a later implementation.
- Fresh independent adversarial review and master reproduction remain mandatory. No
  producer self-approval is claimed.

## Follow-up items

- Fresh independent R3 review of the exact candidate and capability registry.
- Master independently reruns the complete repository gate before any product work.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no delegation or self-approval: confirmed.
- no index/data/frozen-authority/orchestration/product artifact mutation: confirmed.
- no provider/network/cloud/container/hosted CI/endpoint/remote/deployment activity:
  confirmed.

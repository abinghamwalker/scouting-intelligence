# Subagent return

## Task

- task_id: `W04-SOURCE-COMPLETION-INDEX-REVIEW-02-R1`
- objective: Independently and adversarially review the exact R3 checked-capability
  candidate for ordinary construction, copy, serialization, replay, substitution,
  closure/registry extraction and downstream product-boundary bypasses.
- disposition: **REWORK**
- findings: P0 `0`, P1 `1`, P2 `0`

## Files changed

- `reports/reviews/W04/wyscout-source-completion-index-capability-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-REVIEW-02-R1.md`

## Summary

- Verified all six fixed candidate bindings before review; every digest matched.
- Confirmed the normal public checked route closes direct construction,
  `model_validate`, dump-copy, arbitrary/copied-real digest, unregistered
  `object.__new__`, exact-type/subclass substitution, copy, deepcopy, pickle/replay,
  raw `.value` reuse and normal cross-scope substitution.
- Confirmed any future serializer must accept a checked handle and invoke
  `require_checked_product`, not accept a detached raw value.
- Opened `W04SCIIDXR3CAPR1-P1-001`: standard Python callable introspection exposes
  retained completion/product issuer callables and both weak registries. Identity-only
  registry membership can therefore be forged without the exact accepted-reader
  population comparison, and `require_checked_product` would accept the forged
  registered handle.
- The same root cause permits false period-to-complete-match promotion, Action/Fact/
  Gold scope substitution, raw-value reissue and direct registry insertion. Deleting
  underscore-prefixed issuer names is not an authority control.
- The focused tests, Bandit and local-only verifier pass because the tests do not
  inspect callable closure state or registry reachability.

## Tests run

- command:
  `shasum -a 256 src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py reports/reviews/W04/wyscout-source-completion-index-independent-review-R1.md reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R3.md`
  - exit status: `0`
  - result: the four implementation/test bindings and producer-return binding matched;
    the additional prior-review digest was informational.
- command:
  `shasum -a 256 data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - exit status: `0`
  - result: the immutable index binding matched exactly.
- command:
  `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py -k 'checked or completion_reader or copied_real_membership'`
  - exit status: `0`
  - result: `6 passed, 259 deselected in 18.98s`.
- command:
  `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py`
  - exit status: initial sandbox attempt `2`; unchanged cache-read rerun `0`
  - result: first attempt could not read existing shared uv-cache metadata; authorized
    read-only rerun completed with no findings and no environment/dependency mutation.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; all 25 controls passed with zero failures.
- command: bounded read-only callable/registry state inspection
  - exit status: `0`
  - result: public checked callables retained issuer functions; getter closures retained
    both `WeakKeyDictionary` registries. Operational exploit source is intentionally
    omitted; exact defensive observations are recorded in the review.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/wyscout-source-completion-index-capability-independent-review-R1.md`
- mandatory reviewer return:
  `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-REVIEW-02-R1.md`
- finding: `W04SCIIDXR3CAPR1-P1-001`
- inspected implementation:
  `src/scouting/sources/wyscout_completion_index.py:190-327`,
  `src/scouting/sources/wyscout_completion_index.py:1060-1124`, and
  `src/scouting/sources/wyscout_completion_index.py:1415-1527`

## Risks

- P1: an ordinary in-process Python caller can obtain or mutate issuance state and
  make a raw semantic product pass the current checked-product authority boundary
  without exact completion-reader comparison.
- A future serializer that correctly calls `require_checked_product` remains unsafe
  until issuance forgery is closed.
- No additional P0/P1/P2 finding was identified in this bounded capability review.

## Follow-up items

- Return only `W04SCIIDXR3CAPR1-P1-001` for a bounded correction that replaces
  introspectable identity-only registry acceptance with independently verifiable
  exact population-and-product-scope evidence.
- Add closure/registry extraction, false complete-match, raw-value reissue and
  cross-scope forgery regressions.
- Obtain fresh independent capability/security review before the complete repository
  gate or product work resumes.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
- no delegation or self-approval: confirmed.
- no implementation, test, data, source, manifest, index, frozen authority,
  orchestration, verification or product/runtime artifact edit: confirmed.
- no provider/network/cloud/container/hosted CI/endpoint/remote/deployment access or
  action: confirmed.

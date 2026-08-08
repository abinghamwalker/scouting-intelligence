# Subagent return

## Task

- task_id: `W04-R21-PROGRESSION-FIXTURE-01-R1`
- objective: Correct only the stale perpetual identity-absence assertion so the
  frozen R21 contract remains executable through its required downstream serial
  identity lifecycle.

## Files changed

- `tests/contracts/test_w04_r21_cross_authority_composability.py`
- `reports/reviews/W04/returns/W04-R21-PROGRESSION-FIXTURE-01-R1.md`

## Summary

- The first executable identity-candidate run demonstrated that the frozen R21
  test rejected the exact identity decision/ruleset paths that R21 Sections 10
  and 11 require downstream.
- Replaced only that perpetual absence assertion with four exact lifecycle
  states: all identity artifacts absent; decision plus candidate present; review
  added; acceptance added.
- Partial candidate presence, review-before-candidate, and
  acceptance-before-review remain rejected.
- Preserved the exact 30-resource roster, its path-list digest, and every R21
  semantic, authority, dependency, product, and serializer assertion.
- The previously accepted review and gate bytes are retained under explicit
  archive paths before fresh independent review.

## Tests run

- command: focused identity plus R21 suite before correction
  - exit status: `1`
  - result: the R21 resource test rejected required future identity paths,
    demonstrating the stale fixture.
- command: focused identity plus R21 suite after correction but before review refresh
  - exit status: `1`
  - result: identity lifecycle presence passed; the sole R21 failure was the
    intentionally stale independent-review digest binding, proving fresh review
    is required.
- command: `uv run ruff format --check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: formatted.
- command: `uv run ruff check tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: all checks passed.

## Artifacts/evidence

- prior test SHA-256:
  `fffb71d4d382816f3572b575cbcd9e951309f92239ca540327cdb02304c4f9b0`
- corrected test SHA-256:
  `c51d16e1de99c28cfe5cde2feeeb8cbfc908516a59edc47cd53b08e955e75b26`
- preserved R21 design SHA-256:
  `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`

## Risks

- The fixed review and gate must not be recreated until a distinct reviewer
  binds the corrected test and returns PASS.

## Follow-up items

- Fresh independent review, followed by master gate materialization and complete
  repository gate.

## Scope confirmation

- no unauthorised dependency or lockfile changes: confirmed
- no architecture or product implementation change: confirmed
- no edit outside the two owned implementation/return paths: confirmed

# Subagent return

## Task

- task_id: `W04-IDENTITY-RULESET-REVIEW-01`
- objective: Perform a fresh independent R2 review of the corrected W04
  identity-v1 decision, ruleset, focused contract, and R1 finding closures
  without modifying or accepting the candidate.

## Files changed

- `reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-IDENTITY-RULESET-REVIEW-01-R2.md`

## Summary

- Issued `REWORK` with `P0=0`, `P1=1`, and `P2=0`.
- Independently reproduced the decision physical/canonical digest, ruleset
  physical and parsed-canonical digests, six upstream bindings, exact four-rule
  order, exact seven-policy object, UUIDv5 derivation, and kind separation.
- Reproduced closure of all three archived R1 findings: independent far-future
  review and acceptance clocks fail; exact-second and exact-six-fraction UTC
  values round-trip while other fractions, offsets, and unreal dates fail; and
  candidate/PASS/REWORK/acceptance-after-PASS/forbidden-after-REWORK lifecycle
  states classify correctly.
- Challenged missing, negative, zero, boolean, string, numeric-looking-string,
  duplicate, absent-master, name-only, cross-kind, namespace, digest, actor,
  clock, fence, canonicality, and partial-path conditions.
- Found that the focused resolution oracle compares unvalidated master-table
  keys with Python equality: source integer `1` resolves against a sole boolean
  `true` or non-integer numeric `1.0` master value. This violates
  `STRICT_DECIMAL_INTEGER` and deterministic resolution only from a unique valid
  master row.
- Modified no candidate, upstream authority, corrected contract, R20, R21,
  archived evidence, test, acceptance, orchestration, dependency, runtime,
  data-product, build, model, or product path.

## Tests run

- command: `shasum -a 256 reports/reviews/W04/wyscout-schema-design-R20.md reports/reviews/W04/wyscout-schema-design-R21.md reports/reviews/W04/archive/wyscout-identity-ruleset-independent-review-R1-rework-1a92a3a3.md reports/reviews/W04/archive/W04-IDENTITY-RULESET-REVIEW-01-R1-rework-a0f637b4.md reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json configs/schema/wyscout-v5-identity-ruleset-v1.yaml tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py reports/reviews/W04/returns/W04-IDENTITY-RULESET-DECISION-01-R2.md reports/verification/W04/wyscout-identity-ruleset-decision-R2-master-verification.md`
  - exit status: `0`
  - result: candidate, corrected contract, R20/R21, archived evidence, and
    producer/master evidence digests reproduced exactly.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent master-key strict-type challenge>`
  - exit status: `2` in the filesystem sandbox, then `0` when rerun unchanged
    with approved read access to the existing uv cache
  - result: boolean and float master values both returned `RESOLVED`; string
    master value returned `REVIEW_REQUIRED`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent candidate/R1-clock/UTC/lifecycle/type/UUIDv5 challenge>`
  - exit status: `0`
  - result: candidate digests, ordinary fail-closed cases, namespaces, all
    three R1 closures, and four lifecycle states passed; malformed boolean and
    float master keys independently reproduced the remaining fail-open state.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <fresh review record/digest/actor/fence/canonicality/partial-path challenge>`
  - exit status: `0`
  - result: exact one-finding 12-key canonical record validated as
    `REVIEW_REWORK`; malformed fence, digest mutation, and acceptance without a
    review failed closed.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `146 passed in 6.09s`; the green suite does not include malformed
    master-key strict-type cases and therefore does not disprove the P1.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_identity_ruleset_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_identity_ruleset_authority.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command: `shasum -a 256 <R20, R21, archived R1 evidence, candidate, corrected contract, cross-authority test, and fresh review paths>`
  - exit status: `0`
  - result: every protected digest remained exact after review creation.

## Artifacts/evidence

- decision physical/canonical SHA-256:
  `6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192`
- ruleset physical SHA-256:
  `8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547`
- ruleset parsed canonical SHA-256:
  `9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c`
- corrected contract SHA-256:
  `760bac798093a9e3072b4de608610a71ae6638dacac08d11e6c0a5b84a57c4b0`
- R20 physical SHA-256:
  `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- R21 physical SHA-256:
  `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`
- archived failed review SHA-256:
  `1a92a3a38d050fb83cd5ee83e842d3f6919433ceeef17e36aa1a6db017aac5d9`
- archived failed return SHA-256:
  `a0f637b4fe13c3c393b86f5d44fb59c85af001659201e21c83113cf395434c24`
- cross-authority test SHA-256:
  `c51d16e1de99c28cfe5cde2feeeb8cbfc908516a59edc47cd53b08e955e75b26`
- fresh review physical SHA-256:
  `30c94d15dbce34315d2af5df3cebbd50ce863e7e865db509130b3a09e6e080f5`
- fresh review record SHA-256:
  `1a39d59f4508adce2bd49e71d0a7105dbe26dd1ce87ce762cb4da8d42c185aeb`
- finding evidence:
  `tests/contracts/test_w04_identity_ruleset_authority.py:540-552` and the
  locked/no-sync outputs `bool_master_state=RESOLVED` and
  `float_master_state=RESOLVED`.

## Risks

- A malformed master-table boolean or non-integer numeric key can satisfy the
  focused oracle's uniqueness check and authorize a canonical identity. The
  candidate remains unaccepted, and identity/product work remains blocked.

## Follow-up items

- Validate every master-row key with exact integer type semantics before any
  equality/count operation, reject boolean/float/string master keys, and add
  direct negative regressions; then return a new focused-contract revision for
  fresh independent review.

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`
- no candidate, upstream, corrected-contract, R20, R21, archived-evidence,
  test, acceptance, runtime, Bronze, Silver, Gold, build, model, product,
  network, cloud, container, endpoint, hosted-CI, or deployment work:
  `confirmed`

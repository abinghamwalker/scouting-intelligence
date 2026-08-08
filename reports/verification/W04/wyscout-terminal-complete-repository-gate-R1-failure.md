# W04 terminal complete-repository gate R1 — retained blocker evidence

- Date: `2026-08-03`
- Disposition: **FAIL_RESTART_REQUIRED_AFTER_SMALLEST_R12_DERIVED_CORRECTION**
- Runtime revision: `R12` remains terminal; no R13 or new runtime authority

## Gate result

The master began the single terminal complete-repository/W04 gate from its first
command after terminal independent R12 PASS and master acceptance.

- locked offline all-group sync: PASS, 83 packages resolved / 82 audited;
- repository Ruff format: PASS, 709 files;
- repository Ruff lint: PASS;
- mypy `src/scouting scripts`: PASS, 65 source files;
- import-linter: PASS, 3 contracts kept / 0 broken; and
- unsuppressed `pytest -q`: **FAIL**, `2 failed, 2616 passed, 1 warning in
  1907.48s (0:31:47)`.

The test run was retained to completion. It was not interrupted, suppressed,
filtered, waived or concealed. The remaining security/local/phase/Git tail was
not eligible to contribute acceptance after pytest returned exit `1`.

## Reproduced blockers

1. `test_every_definition_reference_field_and_runtime_validator_is_closed`
   proved that the two accepted R12 runtime validators were implemented as
   Pydantic field validators while the 23-root declarative predicate ledger
   closes only model validators. Their executable validation identities were
   therefore absent from the canonical schema closure. This meets blocker test
   1: accepted executable/authority identity can differ from its purportedly
   complete declared roster.
2. `test_frozen_constant_corpus_reproduces_contracts_authorities_and_composed_inputs`
   proved that the external build-receipt authority still froze the pre-R12
   `wyscout_build.py` SHA-256
   `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16`
   while the accepted R12 build-contract byte hash is
   `fca15a585d928c17999fb606df06f5de370f20ea273f164485ed26dc8a57cdd6`.
   This also meets blocker test 1: an accepted executable authority identity is
   stale.

Neither failure is incidental PYC/cache/inode/link-count/empty-directory host
state. Both are exact executable schema-authority closure defects, so the
controlling 2026-08-03 steer permits the smallest correction. No product logic,
root roster, source/right/temporal authority, intended output, dependency,
runtime behavior, or digest meaning/formula may change.

## Authorized smallest correction

Within terminal R12, the master will:

- express the two already-accepted post-validation rules as behavior-equivalent
  model validators so the existing canonical schema machinery can enumerate
  them;
- append exactly two declarative runtime-predicate rows and update their frozen
  ledger count/digest and independent tests;
- bind the final accepted `wyscout_build.py` hash in external authority;
- mechanically regenerate only affected 23-root content digests, schema/product
  v2 descriptor preimages and inherited constants; and
- rerun focused closure/aggregate/runtime proof before restarting the entire
  complete-repository/W04 gate from command one.

This is a blocker correction inside the terminal R12 authority, not R13, another
runtime-hardening cycle, or an expansion of W04 authority.

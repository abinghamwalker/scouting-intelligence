# W10 deferred runtime host-state hardening backlog R1

- Origin phase: `W04`
- Target phase: `W10 — Expert relevance validation and research hardening`
- Proposed task: `W10-RUNTIME-HOST-STATE-HARDENING-01`
- W04 acceptance status: **RETAINED_NON_BLOCKING_DEFERRED_WORK**

## Deferred scope

W10 should generalize local runtime assurance for incidental host filesystem state
that does not satisfy the W04 blocker tests. The bounded backlog is:

1. define a portable audit-only treatment for unrelated foreign-interpreter PYC
   cache tags and newly appearing metadata-only cache rows without granting them
   executable, source, component, environment, build, schema, product, or roster
   authority;
2. separate security-relevant file substitution facts from filesystem-specific
   inode, directory link-count, empty-directory, timestamp, temporary-path, and
   equivalent metadata variation;
3. retain fail-closed executable/source/product/rights/temporal/truthful-completion
   controls while preventing non-authoritative host variation from entering a
   product digest or reopening an earlier phase; and
4. keep explicit audit evidence and portable regression fixtures for bounded
   host variants supported by the local W10 study and verification environment.

## Preserved evidence and regression coverage

W04 retains, without cleanup or concealment:

- the failed R12 complete-gate evidence (`507 passed, 6 failed`), including the
  exact pre/post repository/site PYC and retained data/run inventories;
- the exact metadata-only denial regression for
  `scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc`, including
  predicate, source, path/tag, mode/size, link/symlink and zero-read/use attacks;
- the real Darwin empty mode-`0o700` prefix-directory observation with link count
  `2` and the explicit regression rejecting the prior file-style value `1`; and
- the closure steer at `reports/verification/W04/w04-closure-steer-2026-08-03.md`.

Those current R12 corrections remain part of the terminal W04 candidate because
they close the six demonstrated failures. No additional PYC/cache-tag/inode/link-
count/empty-directory/timestamp/temp-path hardening is a W04 gate dependency unless
it has a reproducible P0/P1 path affecting executable admission, product bytes,
data rights, temporal safety, or truthful completion evidence.

## W10 entry condition

This backlog did not itself create W10 authority, dependency, provider/network access,
deployment or cost. W09 now satisfies W10's declared dependency; W10 may scope and
dispatch this work only through its normal start gate and the authority in
`docs/architecture/w10-expert-relevance-validation.md`. It must not change W04 logical
contracts, accepted security witnesses, digests, rosters or product behaviour merely
to tolerate non-authoritative host variation.

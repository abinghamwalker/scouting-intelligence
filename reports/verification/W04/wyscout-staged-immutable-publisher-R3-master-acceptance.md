# W04 staged immutable publisher R3 master acceptance

Date: 2026-08-01

Decision: `ACCEPTED_BOUNDED_PRIMITIVE_DOWNSTREAM_WIRING_GATED`

The master accepts the corrected local staged immutable publication primitive after
fresh independent review returned `PASS`, P0/P1/P2 = `0/0/0`, and the complete
bounded master suite passed.

Accepted implementation and test hashes are:

- `src/scouting/storage/wyscout_publication.py`:
  `01b56c0400af0a4fba1adbf06b53b4e94a8571be66c7e0770ca6d72b4c740c13`;
- `tests/unit/test_w04_staged_product_publisher.py`:
  `639503018a5528ad8463d21e68fbfd0133e09c9884838a2422daf911173f709e`.

The fresh independent review is
`77516478c9dd386f0e44179c1cf8219fd925f26b0460a73c771fb4f5e409d1c5`;
the master verification is the companion
`wyscout-staged-immutable-publisher-R3-master-verification.md`.

Acceptance is limited to the three exact roots, bounded normalized relative tails,
same-filesystem no-replace promotion, immutable equal replay, retained failure
evidence, both post-link fsync boundaries and the final identity-bound replay
checkpoint. The documented between-checkpoint same-trust-domain residual remains.

No product is published by this acceptance. Runtime wiring remains conditional on
the build, schema, aggregate and complete repository gates.

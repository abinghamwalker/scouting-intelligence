# W04 Wyscout runtime-control R12 terminal gate blocker correction — master acceptance

- Date: `2026-08-03`
- Parent runtime revision: `R12` (terminal)
- Decision: **MASTER_ACCEPTED_WITHIN_TERMINAL_R12**
- New runtime revision or authority: **none**

## Controlling finding and bounded disposition

The first terminal complete-repository gate ran to completion and returned `2
failed, 2616 passed, 1 warning`. Both failures demonstrated blocker class 1 from
the controlling closure steer: accepted executable validator identities and the
external build-receipt authority were not closed by the canonical 23-root schema
authority. The retained failure is recorded in
`reports/verification/W04/wyscout-terminal-complete-repository-gate-R1-failure.md`.

The master therefore applied the smallest permitted correction inside terminal
R12. No R13, new runtime-control authority, logical model, root roster, feature or
product population, source/rights/temporal authority, intended output, or digest
meaning/formula was introduced or changed.

## Accepted correction

1. `RuntimeSubsetObservation.exact_runtime_observation` and
   `FinalRecheckResult.exact_runtime_subset` are expressed as behavior-equivalent
   Pydantic after-model validators. Their validation conditions and accepted
   values are unchanged, while their executable identities are now enumerable by
   the accepted schema-closure mechanism.
2. The canonical runtime-predicate ledger and its independent frozen oracle append
   exactly predicates `P57` and `P58`; the ledger count becomes `58` and the
   canonical ledger digest becomes
   `5a787de72cdad220a6e609c9ca713df33830e4afa7845b4b2e5de3df87d57d2b`.
3. The external build-receipt authority binds the corrected build-contract source
   SHA-256
   `e77efd1d11b8ca3b873dee79511142f5fdf12092d9a455eeba0001e9c3faa34f`.
4. The two derived v2 descriptor preimages and inherited launcher/test constants
   were mechanically regenerated from the unchanged accepted algorithms and v1
   inputs.

## Frozen corrected identities

| Artifact | SHA-256 |
| --- | --- |
| build contract | `e77efd1d11b8ca3b873dee79511142f5fdf12092d9a455eeba0001e9c3faa34f` |
| schema contract | `e8ea8ec4f37be1451fa4bbfe5b04089485889fad51b716e1ff69b2d603e98bcf` |
| independent schema-closure test oracle | `4a9cfc1ba11d90b56474b77e396aa513b68f24b14fa9d3b5267be1e2d1581bff` |
| schema v2 physical | `2b16875bc9865548f43f2722c47e1ddfd882a644bad8f2c3cd7b09feb25acd50` |
| product v2 physical | `4ea2173781bba044d9b9b31b0cddaf2eb626c051694b3ef4a8c176067e612e20` |
| launcher | `8e1ddcee6686f28a12d8178c56688371f16e5bde5f6c3ba1f29d0db953632c8a` |
| runtime-control tests | `0720c3487f8685e65286036ffd6dcb054990aa6e6106a84a414a61152643267d` |

The corresponding no-LF schema/product v2 body digests are
`956f5c3cedd9c9e2b36417ad87d8a9f2f97bc54b2720a6835a3cbcde668ff6e5`
and `fa2b28166df02663120f8cf9ca1751c0c32ff75a98b6255baf181bc179088f76`.

## Focused verification

- the three exact failed/ledger/frozen-corpus closure tests: `3 passed`;
- complete schema-closure contract file: `43 passed`;
- complete v2 aggregate contract file: `17 passed`;
- complete Wyscout build-contract file: `56 passed`;
- complete runtime-control unit file: `287 passed in 90.35s`;
- Ruff format on the five affected runtime/contract/test files: PASS;
- Ruff lint on the affected files: PASS; and
- mypy on both corrected source contracts: PASS.

An initial runtime-unit invocation from the restricted tool sandbox retained `38`
failures, each caused before the tested code ran by denial of read access to the
existing local `uv` cache. The unchanged suite was rerun with normal repository
cache access and passed all `287` tests. This execution-environment denial is not
a product, authority, source/rights/temporal, completion-evidence, or P0/P1 code
finding.

The terminal R12 correction is accepted. The complete repository/W04 phase gate
must restart from command one. Accepted runtime R11 and retained real-root R3
remain the minimum W04 operational baseline; non-blocking host-state assurance
remains explicitly deferred to W10.

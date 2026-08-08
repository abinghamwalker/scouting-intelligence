# Subagent return

## Task

- task_id: `W04-BUILD-RECEIPT-CLOSURE-AUDIT-REVIEW-01`
- objective: Independently challenge whether accepted R20/R21 bytes already close
  W04 build/receipt authority and whether the proposed bounded user decision is
  sufficient.

## Files changed

- `reports/reviews/W04/wyscout-build-receipt-closure-audit-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-BUILD-RECEIPT-CLOSURE-AUDIT-REVIEW-01-R1.md`

## Summary

- Verdict: `REWORK` with `P0=0`, `P1=3`, `P2=1`.
- Accepted bytes do not close receipt contents, concrete POC window/cutoff, or
  product-authorized completion-index-bound aggregate values. A bounded user
  authorization is genuinely required; no accepted-byte-only publication route
  exists.
- R20's exact 25-key projection, post-hash 25-key invocation, and one-SHA-256
  algorithm are already implementable. No 26th key or R20/R21 rewrite is required.
- The proposed one-day window contains exactly the authentic match, the proposed
  cutoff is strictly after every current dependency/source/authority clock, the
  accepted index binding is exact, and the proposed publication graph is acyclic.
- Rework is required because `snapshot_as_of_ts=SOURCE_ACQUIRED_AT` contradicts the
  retained accepted maximum-selected-match-start rule; the proposed schema aggregate
  does not expressly bind every implemented R20 schema; receipt cross-clock ordering
  is incomplete; and the window UUID preimage keys are not byte-exact.

## Tests run

- command: complete `sed` reads of every packet `read_first` path
  - exit status: `0`
  - result: AGENTS, packet, both predecessor audits, all 4,516 R20 lines, all 1,254
    R21 lines, all 3,256 contract lines, and return template read completely.
- command: `shasum -a 256` over the closure audit, R20, R21, accepted completion
  index, both v1 preimages, and immutable source manifest
  - exit status: `0`
  - result: all fixed and supporting digests reproduced exactly.
- command: bounded receipt-symbol/schema scan with `rg`
  - exit status: `0`
  - result: only report/design references exist; no executable closed receipt-content
    model or schema ID was found.
- command: `jq` extraction of accepted completion-index England/match scope
  - exit status: `0`
  - result: member digest, row count, match, period counts and both membership digests
    reproduced.
- command: `jq` selection of England matches in the proposed half-open UTC day
  - exit status: `0`
  - result: exactly one authentic match at `2017-08-11T18:45:00Z`.
- command: `jq`/`rg` authority-clock extraction
  - exit status: `0`
  - result: latest dependency-bound clock is identity acceptance
    `2026-07-31T14:15:26Z`, strictly before the proposed cutoff.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-build-receipt-closure-audit-independent-review-R1.md`
- fixed completion index:
  `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
- retained snapshot authority: `reports/reviews/W04/wyscout-schema-design-R4.md:566`
  and `reports/reviews/W04/wyscout-schema-design-R5.md:632`
- R20 retention clause: `reports/reviews/W04/wyscout-schema-design-R20.md:10`
- R21 descriptor-only authority: `reports/reviews/W04/wyscout-schema-design-R21.md:681`

## Risks

- P1: source-acquisition snapshot would publish a temporal proof that contradicts
  accepted W04 semantics.
- P1: a partial schema aggregate would allow final bytes not content-bound by the
  projection's `schema_bundle_digest`.
- P1: unordered boundary and invocation clocks allow a receipt to claim the wrong
  run interval while all hashes and paths pass.
- P2: an underspecified UUID preimage permits multiple window-definition IDs for the
  same stated window.

## Follow-up items

- Return the closure audit for the four bounded corrections in the independent
  review, then obtain fresh review before asking the user or dispatching authoritative
  build/receipt implementation.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation/data/product/manifest/receipt/provider/network/cloud/container/
  CI/remote/endpoint/deployment action: confirmed

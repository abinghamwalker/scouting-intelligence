# W04 Wyscout identity-ruleset review R1 — master verification

## Decision

`REWORK`.

The master independently inspected the review and reproduced all three findings.
No candidate semantic or architecture contradiction exists; the defects are
confined to the focused contract.

## Preserved failed evidence

| artifact | archived path | SHA-256 |
|---|---|---|
| independent review | `reports/reviews/W04/archive/wyscout-identity-ruleset-independent-review-R1-rework-1a92a3a3.md` | `1a92a3a38d050fb83cd5ee83e842d3f6919433ceeef17e36aa1a6db017aac5d9` |
| reviewer return | `reports/reviews/W04/archive/W04-IDENTITY-RULESET-REVIEW-01-R1-rework-a0f637b4.md` | `a0f637b4fe13c3c393b86f5d44fb59c85af001659201e21c83113cf395434c24` |

## Master reproduction

The exact focused suite produced `136 passed, 1 failed`. The sole live failure
was the asserted `REVIEW_PASS` versus the valid actual `REVIEW_REWORK`.

A separate read-only challenge constructed a review at
`9999-12-30T00:00:00Z` and acceptance at `9999-12-31T00:00:00Z`; the contract
incorrectly returned `ACCEPTED`. Parsing
`2026-07-31T13:21:31.123456Z` incorrectly raised
`ValueError: noncanonical UTC`.

The decision SHA-256 remains
`6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192`;
the ruleset physical SHA-256 remains
`8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547`;
and the ruleset canonical SHA-256 remains
`9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c`.

## Scope

The bounded R2 correction may edit only the identity focused contract and its
return. It may not alter candidate/upstream evidence, create acceptance, or
begin identity runtime, Bronze, Silver, Gold, build, model, or product work.

# W04 Wyscout identity-ruleset review R2 — master verification

## Decision

`REWORK`.

The master independently reproduced the sole P1 finding. The R2 review also
correctly confirmed closure of all three R1 findings and exact preservation of
candidate/upstream evidence.

## Preserved failed evidence

| artifact | archived path | SHA-256 |
|---|---|---|
| independent review | `reports/reviews/W04/archive/wyscout-identity-ruleset-independent-review-R2-rework-30c94d15.md` | `30c94d15dbce34315d2af5df3cebbd50ce863e7e865db509130b3a09e6e080f5` |
| reviewer return | `reports/reviews/W04/archive/W04-IDENTITY-RULESET-REVIEW-01-R2-rework-f20ecbd9.md` | `f20ecbd992fcec36ffe44375b2af9acf78b6e1ee4b552b81d51a1e27e37a7931` |

## Master reproduction

The current oracle returned `RESOLVED` for both:

```text
_resolve_identity("TEAM", 1, [True])
_resolve_identity("TEAM", 1, [1.0])
```

It returned `REVIEW_REQUIRED` for `["1"]`. Python equality therefore creates
two undeclared coercion routes on the master-key side even though the reference
key is strict.

The exact focused suite remained green at `146 passed`, demonstrating the
negative-case coverage gap. Candidate and archived-evidence digests remain
exact.

## Scope

R3 may edit only the identity focused contract and its return. It must preserve
all authority bytes and every R2 clock/lifecycle correction. No acceptance or
product work is authorized.

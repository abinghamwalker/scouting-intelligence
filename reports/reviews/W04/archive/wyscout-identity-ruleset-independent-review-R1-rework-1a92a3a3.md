# W04 Wyscout identity-ruleset independent review R1

## Recommendation

`REWORK`.

The decision and safe-YAML ruleset reproduce the required four ordered entity
rules, seven closed policies, accepted upstream bindings, physical digests, and
parsed canonical digest. Independent strict-type challenges also reproduced the
required fail-closed outcomes for missing, negative, zero, boolean, string,
numeric-looking-string, duplicate, absent-master, name-only, cross-kind,
namespace, and UUIDv5 cases.

The focused contract has two clock-validation defects. First, review and
acceptance clocks have no truthful-current-time upper bound: an independently
constructed review at `9999-12-30T00:00:00Z` followed by acceptance at
`9999-12-31T00:00:00Z` validates as `ACCEPTED`. Second, its UTC parser rejects
the otherwise authorised canonical six-fraction form. Its live-state assertion
also hard-codes every present review as `REVIEW_PASS`, causing a valid `REWORK`
record to fail the packet's exact focused suite instead of yielding
`REVIEW_REWORK`. These findings prevent a PASS recommendation even though the
candidate artifact bytes and semantics otherwise reconstruct exactly.

```w04-authority-review-v1
{"candidate_id":"w04-wyscout-identity-ruleset-v1","candidate_physical_sha256":"8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547","candidate_sha256":"9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c","decision_id":"w04-wyscout-identity-ruleset-decisions-v1","decision_physical_sha256":"6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192","decision_sha256":"6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192","findings":[{"code":"IDENTITY_CLOCK_FUTURE_ACCEPTED","severity":"P1","summary":"The focused contract never bounds reviewed_at or accepted_at against truthful current time; a review at 9999-12-30T00:00:00Z and acceptance at 9999-12-31T00:00:00Z validate as ACCEPTED, so clock drift fails open contrary to R20 and the packet."},{"code":"IDENTITY_LIVE_REWORK_MISCLASSIFIED","severity":"P1","summary":"The live-state test hard-codes every present review as REVIEW_PASS; a valid REWORK machine record is parsed as REVIEW_REWORK but fails the exact focused suite, contradicting the required absent/candidate/PASS-or-REWORK/acceptance-after-PASS progression."},{"code":"IDENTITY_CLOCK_FRACTIONAL_UTC_REJECTED","severity":"P2","summary":"The focused contract hard-codes second-only UTC parsing and rejects 2026-07-31T13:21:31.123456Z, although R20 canonical UTC explicitly permits either no fraction or exactly six fractional digits."}],"recommendation":"REWORK","review_id":"w04-wyscout-identity-ruleset-independent-review-R1","review_schema_version":"w04-authority-independent-review-v1","reviewed_at":"2026-07-31T13:27:42Z","reviewed_by":"2c3ccf67-518f-543c-b213-ea40aef2c162"}
```

No candidate, upstream authority, test, acceptance, runtime, or product path was
modified. This review does not accept the candidate or authorize identity
runtime, Bronze, Silver, Gold, build, model, or product work.

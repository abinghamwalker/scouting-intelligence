# W04 Wyscout identity-ruleset independent review R2

## Recommendation

`REWORK`.

The frozen decision and safe-YAML candidate independently reproduce the required
six upstream bindings, exact four-rule order, exact seven-policy object, strict
UUIDv5 source/kind namespace derivation, candidate physical/canonical digests,
and fail-closed reference handling for missing, negative, zero, boolean, string,
numeric-looking-string, duplicate, and absent-master cases. Name-only matching
remains forbidden, same numeric IDs remain separated across kind namespaces, and
the decision, candidate, review, and acceptance digest graph remains acyclic.

All three archived R1 findings are closed. Independently far-future review and
acceptance clocks now fail their respective truthful-clock validators. Exact-second
and exact-six-fraction UTC spellings parse and round-trip byte-for-byte, while
other fraction widths, offsets, and unreal dates fail. The live lifecycle now
classifies candidate, PASS review, REWORK review, forbidden acceptance after
REWORK, and acceptance after PASS states correctly.

One new P1 focused-contract defect remains. The resolution oracle enforces strict
typing on the reference source key but not on the master-table keys before using
Python equality. Consequently source integer `1` resolves against a sole master
value of either boolean `true` or non-integer numeric `1.0`. Those are not strict
decimal integers and therefore cannot constitute the unique valid master row
required by the frozen ruleset. The current suite has no negative case for this
master-side type coercion, so malformed master evidence can authorize a canonical
identity.

```w04-authority-review-v1
{"candidate_id":"w04-wyscout-identity-ruleset-v1","candidate_physical_sha256":"8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547","candidate_sha256":"9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c","decision_id":"w04-wyscout-identity-ruleset-decisions-v1","decision_physical_sha256":"6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192","decision_sha256":"6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192","findings":[{"code":"IDENTITY_MASTER_KEY_TYPE_COERCION","severity":"P1","summary":"The focused resolution oracle validates only the reference source key before comparing unvalidated master-table values with Python equality; source integer 1 therefore resolves against boolean true or non-integer numeric 1.0, violating STRICT_DECIMAL_INTEGER and the unique-valid-master-row requirement."}],"recommendation":"REWORK","review_id":"w04-wyscout-identity-ruleset-independent-review-R1","review_schema_version":"w04-authority-independent-review-v1","reviewed_at":"2026-07-31T13:51:22Z","reviewed_by":"311c93e2-d21c-5779-b5ba-c238d9ee77ee"}
```

Candidate, corrected contract, R20, R21, upstream authority, archived R1 evidence,
tests, and acceptance remain unmodified. This review does not accept the
candidate or authorize identity runtime, Bronze, Silver, Gold, build, model, or
product work.

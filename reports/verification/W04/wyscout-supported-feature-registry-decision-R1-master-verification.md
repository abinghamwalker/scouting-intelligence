# W04 supported feature registry decision R1 — master verification

## Decision

`ACCEPT_FOR_INDEPENDENT_REVIEW`.

The producer materialized the frozen R21 feature authority without expanding
scope. The decision and candidate contain exactly fifteen ordered rows, exactly
four `SUPPORTED` rows, four `SUPPRESSED_UNSUPPORTED_DENOMINATOR` rows, and seven
`UNAVAILABLE` rows. This decision releases only a fresh independent review; it
does not accept the feature authority or permit cross-authority or product work.

## Independent readback

The master read every changed byte and independently reconstructed:

```text
decision key count: 8
candidate key count: 7
bound input count: 10
feature row count: 15
supported row count: 4
suppressed row count: 4
unavailable row count: 7
feature order: lexical, unique, exact R21 order
decision/candidate semantic restatement: PASS
```

The exact supported roster is:

```text
action_count
coordinate_known_action_count
match_count
resolved_possession_action_count
```

`resolved_possession_action_count` has only the three frozen canonical selector
inputs. Exact `possession_eligibility_state == ELIGIBLE_RESOLVED` remains an
additional applicability predicate, not a fourth input.

## Integrity

```text
decision physical/canonical SHA-256:
bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941
candidate physical SHA-256:
8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95
candidate parsed canonical SHA-256:
49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f
focused contract SHA-256:
976eeea142ee96d8c4274bb22dd8637c7486c6a1b71aec591f69962117501411
producer return SHA-256:
3931c81a38a89a9034e3bf3359f12658236a57317eb9e10f0cd2f8ba13d754e9
```

The feature authority binds the accepted field-v2 and possession-v2 candidate
and acceptance digests plus both immutable sibling-control-preimage IDs and
digests. The candidate binds the decision physical digest, and the decision and
candidate exactly restate the feature rows, policies, and bound inputs.

## Master reproduction

The master began with the required locked synchronization:

```text
83 packages resolved
82 packages audited
```

The complete focused authority/preimage suite passed:

```text
290 passed in 27.83s
```

Additional checks:

```text
focused Ruff format: PASS
focused Ruff lint: PASS
local-only verifier: 25/25 PASS
git diff --check: PASS
git remote: empty
```

The direct digest/readback reconstruction was performed independently of the
producer return and reproduced every recorded digest and state count.

## Fresh independent review requirements

The reviewer must independently challenge:

- the exact R21 roster, state split, row union, policies, and ten bindings;
- accepted field-v2 and possession-v2 lineage and canonical/physical digest
  separation;
- both acyclic sibling preimages and absence of a premature feature hash;
- strict review/acceptance progression, UUIDv5 identities, clocks, and hashes;
- exact applicability semantics, especially accepted position evidence and
  `ELIGIBLE_RESOLVED`;
- absence of cross-authority and all product paths.

`PASS` requires zero P0-P2 findings.

## Gate

Only `W04-FEATURE-REGISTRY-REVIEW-01-R1` may start. Feature acceptance,
cross-authority composition, and every product path remain blocked.

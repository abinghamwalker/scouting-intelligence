# W04 vertical-slice identity-bundle audit R1 master verification

Date: 2026-07-31

Disposition: `MASTER_ACCEPTED_FOR_BOUNDED_RUNTIME_PACKET`

The master inspected the complete audit and its R20/R21 authority references. The
audit establishes that the minimum honest initial identity bundle is the exact
source-complete identity population, while remaining a prerequisite artifact rather
than Bronze, Silver, Gold, build, receipt or product implementation.

## Accepted findings

- Exact current population: 5,594 rows: 7 resolved competitions, 142 resolved
  teams, 3,603 resolved players, 15 review-required players, one rejected player-zero
  row and 1,826 resolved matches.
- Exact open review queue: 15 non-zero absent players aggregating 23 source
  occurrences. Eight substitution-in misses are source player zero and contribute to
  the rejected-zero evidence rather than the queue.
- The initial bundle has no historical rows, supersession edges, corrections or
  prior bundle. Every row is version 1 and binds the already accepted authority graph.
- The five target source keys are uniquely resolved. Match 2499719 independently
  reconciles competition 364, season 181150 and teams 1609/1631.
- Player 285508 is bench index 4 and enters for player 192748 at nominal minute 82.
  The later product slice must use formation evidence and one right-censored `[82,83)`
  stint; it must not infer elapsed minutes or per-90 features.
- Audit return SHA-256:
  `85cb5b344993d5c61cc20f0b3b67761385e66aec4b11ce5674b8e5f2680449c0`.

## Master-frozen additive serialization values

R20 fixes queue semantics but leaves two byte-level runtime values unstated. The
bounded runtime packet freezes them without changing R20/R21 bytes or semantics:

```text
identity_review_queue_namespace = UUIDv5(
  NAMESPACE_URL,
  "urn:scouting-intelligence:w04:wyscout:identity-review-queue:v1")

queue_item_id = UUIDv5(
  identity_review_queue_namespace,
  canonical_json_text({
    "entity_kind": "PLAYER",
    "reason_family": "NONZERO_ABSENT_MASTER",
    "source_identity": <complete SourceIdentity object>,
    "source_manifest_id": <lower-case canonical UUID string>,
    "tenant_id": <lower-case canonical UUID string>
  }))

reason_codes = ("NONZERO_ABSENT_PLAYER_MASTER",)
```

`canonical_json_text` is NFC UTF-8 JSON decoded to text, with lexically sorted object
keys, compact separators, strict typed values, no floats, no unknown or duplicate
keys, and no terminal newline. No separator or alternate preimage is admitted.

The runtime candidate now requires independent implementation, master reproduction
and a fresh independent review before its bundle digest may feed build authority.
